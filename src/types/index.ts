// ── Core Types for Shorts MAB + Success Formula ──

export type VideoType = 
  | 'stock_footage'
  | 'kinetic_typography'
  | 'data_viz'
  | 'html_css_motion'
  | 'whiteboard_sketch'
  | 'meme_notification'
  | 'clip_curation_edit';

export type HookType = 'context' | 'contrarian' | 'intrigue';

export type ValueAddType =
  | 'fact_check_callout'
  | 'data_viz_overlay'
  | 'counter_argument'
  | 'source_citation'
  | 'animated_annotation'
  | 'multi_source_mashup'
  | 'this_or_that_overlay'
  | 'split_screen_comparison'
  | 'timeline_overlay';

export type VariantStatus = 'pending' | 'uploaded' | 'metrics_fetched' | 'failed';

export type CycleStatus = 'pending' | 'rendering' | 'uploading' | 'waiting_metrics' | 'analyzed' | 'complete';

export type CohortStatus = 'active' | 'evaluating' | 'success' | 'failure';

// ── Variant ──
export interface Variant {
  videoType: VideoType;
  hookType: HookType;
  valueAddType: ValueAddType | null; // null = no value-add
}

export interface VariantPerformance {
  id: number;
  cycleId: number;
  variantKey: string;          // serialized Variant → string
  videoType: VideoType;
  hookType: HookType;
  valueAddType: ValueAddType | null;
  videoId: string | null;      // YouTube video ID after upload
  status: VariantStatus;
  avdPct: number | null;       // Average View Duration %
  ctr: number | null;
  views: number | null;
  uploadedAt: string | null;   // ISO
  metricsFetchedAt: string | null;
}

// ── Cycle ──
export interface Cycle {
  id: number;
  cycleNumber: number;
  cohortId: string;
  status: CycleStatus;
  epsilon: number;
  startedAt: string | null;
  completedAt: string | null;
}

// ── MAB State ──
export interface MABState {
  epsilon: number;
  totalVideosProduced: number;
  variantRewards: Record<string, VariantReward>; // key = variantKey
  topVariants: string[];        // top-3 variant keys
}

export interface VariantReward {
  totalAvd: number;             // sum of AVD across samples
  sampleCount: number;
  meanAvd: number;              // running average
  lastUpdated: string;          // ISO
}

// ── Cohort & Target ──
export interface Target {
  cohortId: string;
  createdAt: string;
  targetStatement: string;
  measurableOutcome: string;
  whyItMatters: string;
  thresholdAvd: number;         // e.g. 60
  totalVideos: number;
  cycleCount: number;
  status: CohortStatus;
  startedAt: string | null;
  evaluatedAt: string | null;
  achievedAvd: number | null;   // mean AVD after evaluation
}

export interface CohortEval {
  cohortId: string;
  meanAvd: number;
  videoCount: number;
  targetReached: boolean;
  topVariants: string[];
  evaluatedAt: string;
}

export interface MabOverride {
  cohortId: string;
  cycleNumber: number;
  variantPriorityBoost: Partial<{
    videoTypes: VideoType[];
    hookTypes: HookType[];
    valueAddTypes: ValueAddType[];
  }>;
  epsilonOverride: number | null;     // override epsilon for this cycle
  durationOverrideSec: number | null;
  notes: string;
}

// ── Hypotheses & Confidence ──
export interface Hypothesis {
  id: string;
  statement: string;            // "Contrarian hook + Data Viz → AVD +12% on Kinetic"
  predictedImpact: number;      // percentage points lift
  confidence: number;           // 0-1
  effort: number;               // 1-5
  iceScore: number;             // computed: impact × confidence / effort
  variantDims: Partial<Variant>;
  source: string;               // e.g. "analyzer_cycle_3", "auto_crawl_channel_x"
}

export interface ConfidenceResult {
  score: number;                // 1-100
  baseConfidence: number;
  learningBonus: number;
  breakdown: string[];
  conditionsChecklist: string[];
}
