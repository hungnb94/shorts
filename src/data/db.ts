import Database from 'better-sqlite3';
import path from 'path';
import { existsSync, mkdirSync } from 'fs';
import {
  VariantPerformance, Variant, Cycle, MabOverride,
  Target, CohortEval, CycleStatus
} from '../types/index.js';
import { variantKey } from './mab-strategy.js';

const DATA_DIR = path.resolve(process.cwd(), 'data');
const DB_PATH = path.join(DATA_DIR, 'video_metrics.db');

let db: Database.Database;

function getDb(): Database.Database {
  if (!db) {
    mkdirSync(DATA_DIR, { recursive: true });
    db = new Database(DB_PATH);
    db.pragma('journal_mode = WAL');
    db.pragma('foreign_keys = ON');
    initTables();
  }
  return db;
}

function initTables(): void {
  const d = getDb();
  d.exec(`
    CREATE TABLE IF NOT EXISTS cycles (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      cycle_number INTEGER NOT NULL,
      cohort_id TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'pending'
        CHECK(status IN ('pending','rendering','uploading','waiting_metrics','analyzed','complete')),
      epsilon REAL NOT NULL DEFAULT 0.5,
      started_at TEXT,
      completed_at TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS variant_performance (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      cycle_id INTEGER NOT NULL,
      variant_key TEXT NOT NULL,
      video_type TEXT NOT NULL,
      hook_type TEXT NOT NULL,
      value_add_type TEXT,
      video_id TEXT,
      status TEXT NOT NULL DEFAULT 'pending'
        CHECK(status IN ('pending','uploaded','metrics_fetched','failed')),
      avd_pct REAL,
      ctr REAL,
      views INTEGER,
      uploaded_at TEXT,
      metrics_fetched_at TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      FOREIGN KEY (cycle_id) REFERENCES cycles(id)
    );

    CREATE TABLE IF NOT EXISTS targets (
      cohort_id TEXT PRIMARY KEY,
      target_statement TEXT NOT NULL,
      measurable_outcome TEXT NOT NULL,
      why_it_matters TEXT,
      threshold_avd REAL NOT NULL,
      total_videos INTEGER,
      cycle_count INTEGER,
      status TEXT NOT NULL DEFAULT 'active'
        CHECK(status IN ('active','evaluating','success','failure')),
      started_at TEXT,
      evaluated_at TEXT,
      achieved_avd REAL,
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS mab_overrides (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      cohort_id TEXT NOT NULL,
      cycle_number INTEGER NOT NULL,
      json_config TEXT NOT NULL,
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
  `);
}

// ── Cycle Operations ──

export function createCycle(cycleNumber: number, cohortId: string, epsilon: number): number {
  const d = getDb();
  const stmt = d.prepare(
    `INSERT INTO cycles (cycle_number, cohort_id, status, epsilon, started_at)
     VALUES (?, ?, 'pending', ?, datetime('now'))`
  );
  const r = stmt.run(cycleNumber, cohortId, epsilon);
  return Number(r.lastInsertRowid);
}

export function updateCycleStatus(id: number, status: CycleStatus): void {
  const d = getDb();
  d.prepare(`UPDATE cycles SET status = ? WHERE id = ?`).run(status, id);
}

export function getLatestCycle(): Cycle | null {
  const d = getDb();
  return d.prepare(`SELECT * FROM cycles ORDER BY id DESC LIMIT 1`).get() as Cycle | null;
}

// ── Variant Performance Operations ──

export function createVariantRecord(
  cycleId: number, variant: Variant, variantKeyStr: string
): number {
  const d = getDb();
  const stmt = d.prepare(
    `INSERT INTO variant_performance
     (cycle_id, variant_key, video_type, hook_type, value_add_type, status)
     VALUES (?, ?, ?, ?, ?, 'pending')`
  );
  const r = stmt.run(cycleId, variantKeyStr, variant.videoType, variant.hookType, variant.valueAddType);
  return Number(r.lastInsertRowid);
}

export function updateVariantMetrics(
  id: number, avdPct: number, ctr: number, views: number
): void {
  const d = getDb();
  d.prepare(
    `UPDATE variant_performance
     SET avd_pct = ?, ctr = ?, views = ?, status = 'metrics_fetched',
         metrics_fetched_at = datetime('now')
     WHERE id = ?`
  ).run(avdPct, ctr, views, id);
}

export function getCycleVariants(cycleId: number): VariantPerformance[] {
  const d = getDb();
  return d.prepare(`SELECT * FROM variant_performance WHERE cycle_id = ?`).all(cycleId) as VariantPerformance[];
}

// ── Target & Cohort Operations ──

export function saveTarget(target: Target): void {
  const d = getDb();
  const stmt = d.prepare(`
    INSERT INTO targets
    (cohort_id, target_statement, measurable_outcome, why_it_matters,
     threshold_avd, total_videos, cycle_count, status, started_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    ON CONFLICT(cohort_id) DO UPDATE SET
      status = excluded.status,
      started_at = COALESCE(targets.started_at, excluded.started_at)
  `);
  stmt.run(
    target.cohortId, target.targetStatement, target.measurableOutcome,
    target.whyItMatters, target.thresholdAvd, target.totalVideos,
    target.cycleCount, target.status
  );
}

export function getTarget(cohortId: string): Target | null {
  const d = getDb();
  return d.prepare(`SELECT * FROM targets WHERE cohort_id = ?`).get(cohortId) as Target | null;
}

export function evaluateCohort(cohortId: string): CohortEval {
  const d = getDb();
  // Find all variant_performance for cycles in this cohort
  const rows = d.prepare(`
    SELECT vp.avd_pct, vp.variant_key
    FROM variant_performance vp
    JOIN cycles c ON c.id = vp.cycle_id
    WHERE c.cohort_id = ? AND vp.avd_pct IS NOT NULL
  `).all(cohortId) as { avd_pct: number; variant_key: string }[];

  if (rows.length === 0) {
    return { cohortId, meanAvd: 0, videoCount: 0, targetReached: false, topVariants: [], evaluatedAt: new Date().toISOString() };
  }

  const meanAvd = rows.reduce((s, r) => s + r.avd_pct, 0) / rows.length;

  // Top variants
  const variantAvd: Record<string, number[]> = {};
  for (const r of rows) {
    if (!variantAvd[r.variant_key]) variantAvd[r.variant_key] = [];
    variantAvd[r.variant_key].push(r.avd_pct);
  }
  const topVariants = Object.entries(variantAvd)
    .map(([k, avds]) => ({ key: k, mean: avds.reduce((s, a) => s + a, 0) / avds.length }))
    .sort((a, b) => b.mean - a.mean)
    .slice(0, 3)
    .map(v => v.key);

  const target = getTarget(cohortId);
  const targetReached = target ? meanAvd >= target.thresholdAvd : false;

  // Update target record
  d.prepare(`
    UPDATE targets SET status = ?, evaluated_at = datetime('now'), achieved_avd = ?
    WHERE cohort_id = ?
  `).run(targetReached ? 'success' : 'failure', Math.round(meanAvd * 100) / 100, cohortId);

  return {
    cohortId, meanAvd: Math.round(meanAvd * 100) / 100,
    videoCount: rows.length, targetReached, topVariants,
    evaluatedAt: new Date().toISOString(),
  };
}

// ── MAB Override Operations ──

export function saveMabOverride(override: MabOverride): void {
  const d = getDb();
  d.prepare(
    `INSERT INTO mab_overrides (cohort_id, cycle_number, json_config)
     VALUES (?, ?, ?)
     ON CONFLICT DO NOTHING`
  ).run(override.cohortId, override.cycleNumber, JSON.stringify(override));
}

export function getMabOverride(cohortId: string, cycleNumber: number): MabOverride | null {
  const d = getDb();
  const row = d.prepare(
    `SELECT json_config FROM mab_overrides WHERE cohort_id = ? AND cycle_number = ?`
  ).get(cohortId, cycleNumber) as { json_config: string } | undefined;
  return row ? JSON.parse(row.json_config) : null;
}
