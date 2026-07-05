import { readFileSync, existsSync, writeFileSync, mkdirSync } from 'fs';
import path from 'path';
import { MABState, Variant, VariantReward, VideoType, HookType, ValueAddType } from '../types/index.js';

const DATA_DIR = path.resolve(process.cwd(), 'data');
const MAB_STATE_PATH = path.join(DATA_DIR, 'mab_state.json');

const EPSILON_START = 0.5;
const EPSILON_END = 0.2;
const DECAY_AFTER_VIDEOS = 54;   // 3 cycles × 18 videos
const TOP_N = 3;

const ALL_VIDEO_TYPES: VideoType[] = [
  'stock_footage', 'kinetic_typography', 'data_viz',
  'html_css_motion', 'whiteboard_sketch', 'meme_notification', 'clip_curation_edit'
];
const ALL_HOOK_TYPES: HookType[] = ['context', 'contrarian', 'intrigue'];
const ALL_VALUE_ADD_TYPES: ValueAddType[] = [
  'fact_check_callout', 'data_viz_overlay', 'counter_argument',
  'source_citation', 'animated_annotation',
  'this_or_that_overlay', 'split_screen_comparison', 'timeline_overlay'
  // multi_source_mashup excluded — clip-only
];

export function getDefaultState(): MABState {
  return {
    epsilon: EPSILON_START,
    totalVideosProduced: 0,
    variantRewards: {},
    topVariants: [],
  };
}

export function loadState(): MABState {
  if (!existsSync(MAB_STATE_PATH)) return getDefaultState();
  try {
    return JSON.parse(readFileSync(MAB_STATE_PATH, 'utf-8'));
  } catch {
    return getDefaultState();
  }
}

export function saveState(state: MABState): void {
  mkdirSync(DATA_DIR, { recursive: true });
  writeFileSync(MAB_STATE_PATH, JSON.stringify(state, null, 2));
}

export function variantKey(v: Pick<Variant, 'videoType' | 'hookType' | 'valueAddType'>): string {
  return `${v.videoType}|${v.hookType}|${v.valueAddType ?? 'none'}`;
}

export function parseVariantKey(key: string): Variant {
  const [videoType, hookType, valueAddType] = key.split('|');
  return {
    videoType: videoType as VideoType,
    hookType: hookType as HookType,
    valueAddType: valueAddType === 'none' ? null : valueAddType as ValueAddType,
  };
}

/** Get or create reward entry for a variant */
function getOrInitReward(state: MABState, v: Variant): VariantReward {
  const key = variantKey(v);
  if (!state.variantRewards[key]) {
    state.variantRewards[key] = { totalAvd: 0, sampleCount: 0, meanAvd: 0, lastUpdated: new Date().toISOString() };
  }
  return state.variantRewards[key];
}

/** Return current epsilon (computed live from totalVideosProduced) */
export function currentEpsilon(state: MABState): number {
  const progress = Math.min(state.totalVideosProduced / DECAY_AFTER_VIDEOS, 1);
  return EPSILON_START - (EPSILON_START - EPSILON_END) * progress;
}

/** A single explore-vs-exploit decision */
export function selectVariant(
  state: MABState,
  exploreSpace: {
    videoTypes: VideoType[];
    hookTypes: HookType[];
    valueAddTypes: (ValueAddType | null)[];
  },
  override?: { variantPriorityBoost?: Partial<Record<'videoTypes' | 'hookTypes' | 'valueAddTypes', string[]>> }
): Variant {
  const epsilon = currentEpsilon(state);
  const explore = Math.random() < epsilon;

  if (explore) {
    // Random pick from explore space
    const videoType = exploreSpace.videoTypes[Math.floor(Math.random() * exploreSpace.videoTypes.length)];
    const hookType = exploreSpace.hookTypes[Math.floor(Math.random() * exploreSpace.hookTypes.length)];
    const valueAddType = exploreSpace.valueAddTypes[Math.floor(Math.random() * exploreSpace.valueAddTypes.length)];
    return { videoType, hookType, valueAddType };
  }

  // Exploit: pick from top reward variants
  const sorted = Object.entries(state.variantRewards)
    .sort(([, a], [, b]) => b.meanAvd - a.meanAvd)
    .slice(0, TOP_N);

  if (sorted.length === 0) {
    // No data yet → random
    return selectVariant(state, exploreSpace);
  }

  // Pick from top-N weighted by reward
  const total = sorted.reduce((sum, [, r]) => sum + Math.max(r.meanAvd, 1), 0);
  let rand = Math.random() * total;
  for (const [key] of sorted) {
    const r = state.variantRewards[key];
    rand -= Math.max(r.meanAvd, 1);
    if (rand <= 0) return parseVariantKey(key);
  }

  // Fallback
  return parseVariantKey(sorted[0][0]);
}

/** Generate N variants for one cycle (pure — does not save state) */
export function selectCycleVariants(state: MABState, count: number): Variant[] {
  const exploreSpace = {
    videoTypes: ALL_VIDEO_TYPES,
    hookTypes: ALL_HOOK_TYPES,
    valueAddTypes: [...ALL_VALUE_ADD_TYPES, null],
  };

  const variants: Variant[] = [];
  for (let i = 0; i < count; i++) {
    variants.push(selectVariant(state, exploreSpace));
  }
  return variants;
}

/** Commit selected variants: update state counters + persist */
export function commitVariants(state: MABState, count: number): void {
  state.totalVideosProduced += count;
  state.epsilon = currentEpsilon(state);
  saveState(state);
}

/** Record AVD reward for a variant after metrics fetch */
export function recordReward(state: MABState, variant: Variant, avdPct: number): void {
  const reward = getOrInitReward(state, variant);
  reward.totalAvd += avdPct;
  reward.sampleCount += 1;
  reward.meanAvd = reward.totalAvd / reward.sampleCount;
  reward.lastUpdated = new Date().toISOString();
  
  // Update top-3
  state.topVariants = Object.entries(state.variantRewards)
    .sort(([, a], [, b]) => b.meanAvd - a.meanAvd)
    .slice(0, TOP_N)
    .map(([key]) => key);

  saveState(state);
}

/** Apply MAB override: epsilon override + variant priority boost */
export function applyOverride(
  state: MABState,
  override: { epsilonOverride?: number | null }
): void {
  if (override.epsilonOverride != null) {
    state.epsilon = override.epsilonOverride;
    saveState(state);
  }
}
