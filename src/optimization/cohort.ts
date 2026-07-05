import { MabOverride, Hypothesis, Target, CohortEval } from '../types/index.js';
import { saveMabOverride } from '../data/db.js';

/**
 * Step 8: Convert Top 3 hypotheses into MAB override configs.
 */
export function createMabOverrides(
  cohortId: string,
  top3Hypotheses: Hypothesis[],
  cycleNumbers: number[],
): MabOverride[] {
  const overrides: MabOverride[] = cycleNumbers.map((cycleNumber, i) => {
    const hyp = top3Hypotheses[i] ?? top3Hypotheses[0]; // cycle 3 uses top-1 if <3 hypotheses
    return {
      cohortId,
      cycleNumber,
      variantPriorityBoost: {
        videoTypes: hyp.variantDims.videoType ? [hyp.variantDims.videoType] : undefined,
        hookTypes: hyp.variantDims.hookType ? [hyp.variantDims.hookType] : undefined,
        valueAddTypes: hyp.variantDims.valueAddType ? [hyp.variantDims.valueAddType] : undefined,
      },
      epsilonOverride: null, // let MAB decay naturally
      durationOverrideSec: null,
      notes: `Hypothesis: ${hyp.statement}`,
    };
  });

  for (const o of overrides) {
    saveMabOverride(o);
  }

  return overrides;
}

/**
 * Create MAB override config for cycle N.
 * Returns structured JSON that gets saved and read by MAB.
 */
export function buildOverrideConfig(
  cohortId: string,
  cycleNumber: number,
  hypotheses: Hypothesis[],
): string {
  const top3 = hypotheses.slice(0, 3);
  const override: MabOverride = {
    cohortId,
    cycleNumber,
    variantPriorityBoost: {
      videoTypes: top3.flatMap(h => h.variantDims.videoType ? [h.variantDims.videoType] : []),
      hookTypes: top3.flatMap(h => h.variantDims.hookType ? [h.variantDims.hookType] : []),
      valueAddTypes: top3.flatMap(h => h.variantDims.valueAddType ? [h.variantDims.valueAddType] : []),
    },
    epsilonOverride: null,
    durationOverrideSec: null,
    notes: `Cycle ${cycleNumber}: built from top-3 hypotheses`,
  };
  return JSON.stringify(override, null, 2);
}

/**
 * Generate cohort progress report for mid-cycle monitoring.
 */
export function generateCohortReport(
  cohortId: string,
  target: Target,
  evalResult: CohortEval | null,
  midCycleAvd: number | null,
  cyclesCompleted: number,
  totalCycles: number,
): string {
  const lines: string[] = [];
  lines.push(`═ COHORT REPORT: ${cohortId} ═`);
  lines.push(`Target: AVD ≥ ${target.thresholdAvd}%`);
  lines.push(`Progress: ${cyclesCompleted}/${totalCycles} cycles`);
  
  if (midCycleAvd !== null) {
    const delta = midCycleAvd - target.thresholdAvd;
    const status = delta >= 0 ? 'ON TRACK ✅' : `BEHIND (${delta.toFixed(1)}% below) ⚠️`;
    lines.push(`Running AVD: ${midCycleAvd.toFixed(1)}% — ${status}`);
  }

  if (evalResult) {
    lines.push(`Cohort complete: mean AVD = ${evalResult.meanAvd.toFixed(1)}% — ${evalResult.targetReached ? 'TARGET REACHED ✅' : 'NOT REACHED ❌'}`);
    lines.push(`Top variants: ${evalResult.topVariants.join(', ') || 'N/A'}`);
  }

  return lines.join('\n');
}
