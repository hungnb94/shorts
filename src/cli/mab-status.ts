#!/usr/bin/env tsx
/**
 * MAB Status — display current state, top variants, and cohort progress.
 */
import { loadState, variantKey, currentEpsilon } from '../optimization/mab-strategy.js';
import { getLatestCycle, getTarget, evaluateCohort } from '../data/db.js';
import { calculateConfidence } from '../optimization/confidence.js';

function main(): void {
  const state = loadState();
  const epsilon = currentEpsilon(state);

  console.log('┌─ MAB STATE ─────────────────────────────┐');
  console.log(`  Videos produced  : ${state.totalVideosProduced}`);
  console.log(`  Epsilon (ε)      : ${epsilon.toFixed(3)} (${(epsilon * 100).toFixed(0)}% explore)`);
  console.log(`  Known variants   : ${Object.keys(state.variantRewards).length}`);
  console.log('├─ TOP VARIANTS ───────────────────────────┤');

  const sorted = Object.entries(state.variantRewards)
    .sort(([, a], [, b]) => b.meanAvd - a.meanAvd)
    .slice(0, 5);

  if (sorted.length === 0) {
    console.log('  No reward data yet.');
  } else {
    for (const [i, [key, reward]] of sorted.entries()) {
      const parsed = key.split('|');
      const label = `[${parsed[0]}] hook=${parsed[1]}${parsed[2] !== 'none' ? ' va=' + parsed[2] : ''}`;
      console.log(`  ${i + 1}. ${label}`);
      console.log(`     samples=${reward.sampleCount} mean_AVD=${reward.meanAvd.toFixed(1)}%`);
    }
  }

  console.log('├─ TARGET ─────────────────────────────────┤');
  const target = getTarget('cohort-001');
  if (target) {
    console.log(`  Cohort     : ${target.cohortId}`);
    console.log(`  Target Avd : ≥ ${target.thresholdAvd}%`);
    console.log(`  Status     : ${target.status}`);

    if (target.achievedAvd != null) {
      console.log(`  Achieved   : ${target.achievedAvd}%`);
      console.log(`  Result     : ${target.achievedAvd >= target.thresholdAvd ? '✓ SUCCESS' : '✗ FAILURE'}`);
    }

    const confidence = calculateConfidence(state, target.thresholdAvd, 0, 0);
    console.log(`  Confidence : ${confidence.score}%`);
  } else {
    console.log('  No target set yet.');
  }

  console.log('├─ RECENT CYCLES ──────────────────────────┤');
  const cycle = getLatestCycle();
  if (cycle) {
    console.log(`  Cycle #${cycle.cycleNumber} — ${cycle.status}`);
    if (cycle.epsilon) console.log(`  Epsilon     : ${cycle.epsilon}`);
    if (cycle.startedAt) console.log(`  Started     : ${cycle.startedAt}`);
  } else {
    console.log('  No cycles yet.');
  }

  console.log('└───────────────────────────────────────────┘');
  
  // Show cohort eval if data exists
  const evalResult = evaluateCohort('cohort-001');
  if (evalResult.videoCount > 0) {
    console.log(`\nCohort Evaluation: ${evalResult.meanAvd.toFixed(1)}% mean AVD over ${evalResult.videoCount} videos`);
    console.log(`Target reached: ${evalResult.targetReached ? 'YES ✅' : 'NO ❌'}`);
  }
}

main();
