import { Hypothesis, Variant, VideoType, HookType, ValueAddType } from '../types/index.js';

/**
 * Step 6-7: Generate hypotheses from analyzer data and ICE-prioritize them.
 * 
 * ICE = Impact × Confidence / Effort
 *   Impact = predicted AVD lift (percentage points)
 *   Confidence = analyzer evidence strength (0-1)
 *   Effort = 1 (MAB config only) to 5 (new value-add development)
 */

// Default first-cohort hypotheses when no analyzer data exists
export function getDefaultHypotheses(): Hypothesis[] {
  return [
    {
      id: 'h1_baseline_explore',
      statement: 'Explore rộng 7 video types × 3 hooks × 9 value-adds → find 60%+ AVD combos',
      predictedImpact: 5,
      confidence: 0.7,
      effort: 1,
      iceScore: 3.5,
      variantDims: {},
      source: 'first_cohort_strategy',
    },
    {
      id: 'h2_clip_vs_animation',
      statement: 'Clip Curation Edit outperforms animation types on AVD (real footage = higher retention)',
      predictedImpact: 8,
      confidence: 0.5,
      effort: 2,
      iceScore: 2.0,
      variantDims: { videoType: 'clip_curation_edit' as VideoType },
      source: 'industry_pattern',
    },
    {
      id: 'h3_contrarian_data_viz',
      statement: 'Contrarian hook + Data Viz overlay → AVD +10% on Kinetic Typography',
      predictedImpact: 10,
      confidence: 0.3,
      effort: 1,
      iceScore: 3.0,
      variantDims: { hookType: 'contrarian' as HookType, valueAddType: 'data_viz_overlay' as ValueAddType },
      source: 'viral_channel_hypothesis',
    },
    {
      id: 'h4_this_or_that',
      statement: 'This-or-That overlay + Intrigue hook boosts AVD via curiosity gap',
      predictedImpact: 7,
      confidence: 0.25,
      effort: 1,
      iceScore: 1.75,
      variantDims: { hookType: 'intrigue' as HookType, valueAddType: 'this_or_that_overlay' as ValueAddType },
      source: 'content_strategy',
    },
    {
      id: 'h5_timeline_story',
      statement: 'Timeline overlay + Context hook maps money/earnings trajectory → narrative retention',
      predictedImpact: 6,
      confidence: 0.3,
      effort: 1,
      iceScore: 1.8,
      variantDims: { hookType: 'context' as HookType, valueAddType: 'timeline_overlay' as ValueAddType },
      source: 'content_strategy',
    },
  ];
}

export function computeIceScore(impact: number, confidence: number, effort: number): number {
  return Math.round((impact * confidence / Math.max(effort, 1)) * 100) / 100;
}

export function prioritizeHypotheses(hypotheses: Hypothesis[]): Hypothesis[] {
  return [...hypotheses]
    .map(h => ({ ...h, iceScore: computeIceScore(h.predictedImpact, h.confidence, h.effort) }))
    .sort((a, b) => b.iceScore - a.iceScore);
}

export function getTop3Hypotheses(hypotheses: Hypothesis[]): Hypothesis[] {
  return prioritizeHypotheses(hypotheses).slice(0, 3);
}
