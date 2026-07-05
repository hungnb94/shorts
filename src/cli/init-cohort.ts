#!/usr/bin/env tsx
/**
 * Initialize first Target Cohort.
 * Usage: npx tsx src/cli/init-cohort.ts
 */
import { saveTarget, createCycle, updateCycleStatus } from '../data/db.js';
import { Target } from '../types/index.js';

const TARGET: Target = {
  cohortId: 'cohort-001',
  createdAt: new Date().toISOString(),
  targetStatement: 'AVD ≥ 60% over cohort (18 videos, ~3 cycles, 2 weeks)',
  measurableOutcome: 'Mean AVD of all videos in cohort ≥ 60%',
  whyItMatters: 'Algorithm threshold — 60% AVD is YouTube minimum for recommended feed push',
  thresholdAvd: 60,
  totalVideos: 18,
  cycleCount: 3,
  status: 'active',
  startedAt: new Date().toISOString(),
  evaluatedAt: null,
  achievedAvd: null,
};

function main(): void {
  saveTarget(TARGET);
  console.log(`Target saved: ${TARGET.targetStatement}`);
  console.log(`Threshold: ${TARGET.thresholdAvd}%, Cohort: ${TARGET.cohortId}`);
}

main();
