#!/usr/bin/env tsx
/**
 * Simulate metrics fetch for all variants in cohort-001.
 * In production, this would call YouTube Analytics API.
 * Usage: npx tsx src/cli/simulate-metrics.ts
 */
import { getCycleVariants, updateVariantMetrics, evaluateCohort } from '../data/db.js';
import { loadState, recordReward, parseVariantKey } from '../optimization/mab-strategy.js';
import { getLatestCycle } from '../data/db.js';

function simulateMetrics(): void {
  const state = loadState();
  const cycleIds = [1, 2, 3];

  console.log('Simulating metrics fetch for cohort-001...');
  
  for (const cycleId of cycleIds) {
    const variants = getCycleVariants(cycleId);
    console.log(`\nCycle ${cycleId}: ${variants.length} variants`);
    
    for (const vp of variants) {
      const avdPct = Math.round((45 + Math.random() * 30) * 10) / 10;
      const ctr = Math.round((2 + Math.random() * 8) * 10) / 10;
      const views = Math.floor(200 + Math.random() * 5000);
      
      updateVariantMetrics(vp.id, avdPct, ctr, views);
      console.log(`  ${vp.variantKey}: AVD=${avdPct}%, CTR=${ctr}%, views=${views}`);
      
      const variant = parseVariantKey(vp.variantKey);
      recordReward(state, variant, avdPct);
    }
  }

  console.log('\nMetrics recorded. Evaluating cohort...');
  
  const evalResult = evaluateCohort('cohort-001');
  console.log(`\n═ Cohort Evaluation ═`);
  console.log(`Mean AVD: ${evalResult.meanAvd.toFixed(1)}% (target: 60%)`);
  console.log(`Target reached: ${evalResult.targetReached ? 'YES ✅' : 'NO ❌'}`);
  console.log(`Top variants:`);
  for (const v of evalResult.topVariants) {
    console.log(`  - ${v}`);
  }
  console.log(`\nFinal MAB state:`);
  console.log(`  Epsilon: ${state.epsilon.toFixed(3)}`);
  console.log(`  Videos: ${state.totalVideosProduced}`);
  console.log(`  Known reward variants: ${Object.keys(state.variantRewards).length}`);
}

simulateMetrics();
