#!/usr/bin/env tsx
/**
 * Cycle Runner — orchestrate one optimization cycle:
 * 1. Load MAB state + optional override config
 * 2. Select 6 variants (or 18 for full cycle, configurable)
 * 3. Save cycle + variant records to DB
 * 4. (Placeholder) Render pipeline → Upload → Wait 48h → Fetch metrics
 * 5. Record rewards → Update MAB state
 * 
 * Usage: npx tsx src/cli/cycle-runner.ts
 *   --cohort cohort-001
 *   --videos 6
 *   [--dry-run]  // skip rendering/upload, just select variants + show
 *   [--override] // read MAB override from DB
 */

import { loadState, selectCycleVariants, recordReward, saveState } from '../optimization/mab-strategy.js';
import {
  createCycle, createVariantRecord, updateCycleStatus,
  getMabOverride, saveTarget as saveTargetToDb, getTarget
} from '../data/db.js';
import { variantKey } from '../optimization/mab-strategy.js';
import { calculateConfidence } from '../optimization/confidence.js';
import { getDefaultHypotheses, getTop3Hypotheses } from '../optimization/ice.js';
import { createMabOverrides, generateCohortReport } from '../optimization/cohort.js';
import { Target, MabOverride } from '../types/index.js';

const COHORT_ID = 'cohort-001';
const VIDEOS_PER_DAY = 6;
const CYCLE_DAYS = 3;
const METRICS_WAIT_HOURS = 48;

interface CliArgs {
  cohort: string;
  videos: number;
  dryRun: boolean;
  useOverride: boolean;
}

function parseArgs(): CliArgs {
  const args = process.argv.slice(2);
  return {
    cohort: args.includes('--cohort') ? args[args.indexOf('--cohort') + 1] : COHORT_ID,
    videos: args.includes('--videos') ? Number(args[args.indexOf('--videos') + 1]) : VIDEOS_PER_DAY,
    dryRun: args.includes('--dry-run'),
    useOverride: args.includes('--override'),
  };
}

async function main(): Promise<void> {
  const cli = parseArgs();
  const cohortId = cli.cohort;
  const videoCount = cli.videos;

  console.log(`═ Cycle Runner — Cohort: ${cohortId} ─ ${cli.dryRun ? 'DRY RUN' : 'LIVE'}`);
  
  // Step 1: Load MAB state
  const state = loadState();
  console.log(`MAB state: totalVideos=${state.totalVideosProduced}, epsilon=${state.epsilon.toFixed(3)}`);

  // Step 2: Check for MAB override
  let override: MabOverride | null = null;
  if (cli.useOverride) {
    const latestCycle = await getLatestCycleCount(cohortId);
    override = getMabOverride(cohortId, latestCycle + 1);
    if (override) {
      console.log(`Override found: ${override.notes}`);
      if (override.epsilonOverride != null) {
        state.epsilon = override.epsilonOverride;
        console.log(`Epsilon overridden to ${state.epsilon}`);
      }
    }
  }

  // Step 3: Select variants
  const variants = selectCycleVariants(state, videoCount);
  console.log(`Selected ${variants.length} variants:`);
  for (const v of variants) {
    console.log(`  ${variantKey(v)}`);
  }

  // Step 4: Save to DB
  if (!cli.dryRun) {
    const cycleId = createCycle(state.totalVideosProduced / videoCount, cohortId, state.epsilon);
    updateCycleStatus(cycleId, 'pending');
    
    for (const v of variants) {
      createVariantRecord(cycleId, v, variantKey(v));
    }
    
    console.log(`Cycle ${cycleId} saved.`);
  }

  // Step 5: Run confidence calculation (display only)
  const target = getTarget(cohortId);
  if (target) {
    const confidence = calculateConfidence(state, target.thresholdAvd, 0, 0);
    console.log(`\nConfidence: ${confidence.score}% (base=${confidence.baseConfidence}, bonus=${confidence.learningBonus})`);
    if (confidence.conditionsChecklist.length > 0) {
      console.log('Conditions for 100%:');
      for (const c of confidence.conditionsChecklist) {
        console.log(`  [ ] ${c}`);
      }
    }
  }

  // Step 6: Generate hypotheses & overrides (display for first cohort)
  if (state.totalVideosProduced <= videoCount) {
    const hypotheses = getDefaultHypotheses();
    const top3 = getTop3Hypotheses(hypotheses);
    console.log('\nTop 3 Hypotheses (ICE):');
    for (const h of top3) {
      console.log(`  # ${h.statement} (ICE=${h.iceScore.toFixed(2)})`);
    }
    
    if (!cli.dryRun) {
      const cycleCount = Math.ceil((state.totalVideosProduced) / videoCount);
      createMabOverrides(cohortId, top3, [cycleCount]);
    }
  }

  console.log(`\n✓ ${cli.dryRun ? 'Dry run' : 'Cycle'} complete.`);

  if (cli.dryRun) {
    console.log('\nNext steps to go live:');
    console.log('  1. tsx src/cli/cycle-runner.ts --cohort cohort-001 --videos 6');
    console.log('  2. Run render pipeline');
    console.log('  3. Upload to YouTube');
    console.log('  4. Wait 48h');
    console.log('  5. Fetch metrics → recordReward()');
    console.log('  6. evaluateCohort() to check target');
  }
}

async function getLatestCycleCount(cohortId: string): Promise<number> {
  // Import inline to avoid circular
  const db = await import('../data/db.js');
  const cycle = db.getLatestCycle();
  return cycle?.cycleNumber ?? 0;
}

main().catch(err => {
  console.error('Cycle runner failed:', err);
  process.exit(1);
});
