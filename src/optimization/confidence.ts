import { ConfidenceResult, MABState } from '../types/index.js';

/**
 * Step 4-5: Calculate confidence level from MAB state.
 * 
 * confidence = min(100, base_confidence + learning_bonus)
 *   - base_confidence = % of recent cycles that hit target AVD
 *   - learning_bonus = +10 if top-3 stable, +5 if epsilon ≤ 0.3, +5 if new value-add validated
 */
export function calculateConfidence(
  state: MABState,
  targetAvdPct: number,
  cyclesCompleted: number,
  cyclesHitTarget: number
): ConfidenceResult {
  const baseConfidence = cyclesCompleted > 0
    ? Math.round((cyclesHitTarget / cyclesCompleted) * 100)
    : 50; // default for first cohort

  let learningBonus = 0;
  const breakdown: string[] = [];

  // Check top-3 stability
  const stableTop3 = checkTop3Stability(state);
  if (stableTop3) {
    learningBonus += 10;
    breakdown.push('+10: top-3 variants stable');
  }

  // Check epsilon level
  if (state.epsilon <= 0.3) {
    learningBonus += 5;
    breakdown.push('+5: epsilon ≤ 0.3 (more exploit mode)');
  }

  // Check validated value-adds
  const validatedValueAdds = countValueAddsInTopVariants(state);
  if (validatedValueAdds >= 2) {
    learningBonus += 5;
    breakdown.push('+5: ≥2 validated value-add types in top variants');
  }

  const score = Math.min(100, baseConfidence + learningBonus);

  // Conditions checklist
  const conditionsChecklist = buildConditionsChecklist(state, targetAvdPct, cyclesCompleted, cyclesHitTarget);

  return {
    score,
    baseConfidence,
    learningBonus,
    breakdown: breakdown.length > 0 ? breakdown : ['No bonuses yet — first cohort'],
    conditionsChecklist,
  };
}

function checkTop3Stability(state: MABState): boolean {
  if (state.topVariants.length < 3) return false;
  const rewards = state.topVariants.map(k => state.variantRewards[k]);
  if (rewards.some(r => r.sampleCount < 3)) return false;
  
  const means = rewards.map(r => r.meanAvd);
  const avg = means.reduce((s, m) => s + m, 0) / means.length;
  const variance = means.reduce((s, m) => s + (m - avg) ** 2, 0) / means.length;
  const stddev = Math.sqrt(variance);
  
  return stddev < 5; // stddev < 5% = stable
}

function countValueAddsInTopVariants(state: MABState): number {
  const valueAdds = new Set<string>();
  for (const key of state.topVariants) {
    const parts = key.split('|');
    const va = parts[2];
    if (va && va !== 'none') valueAdds.add(va);
  }
  return valueAdds.size;
}

function buildConditionsChecklist(
  state: MABState,
  targetAvdPct: number,
  cyclesCompleted: number,
  cyclesHitTarget: number
): string[] {
  const conditions: string[] = [];
  
  if (cyclesCompleted < 3) {
    conditions.push(`Need ${3 - cyclesCompleted} more cycles completed`);
  }
  
  const hitRatio = cyclesCompleted > 0 ? cyclesHitTarget / cyclesCompleted : 0;
  if (hitRatio < 1) {
    conditions.push(`Need all cycles to hit AVD ≥ ${targetAvdPct}%`);
  }
  
  if (state.epsilon > 0.25) {
    conditions.push('Need epsilon ≤ 0.25 (more exploit)');
  }
  
  if (!checkTop3Stability(state)) {
    conditions.push('Need top-3 variant rewards stable (stddev < 5%)');
  }
  
  if (countValueAddsInTopVariants(state) < 2) {
    conditions.push('Need at least 2 validated value-add types in top variants');
  }

  return conditions;
}
