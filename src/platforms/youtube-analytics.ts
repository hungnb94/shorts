// YouTube Analytics API fetcher — see docs/adr/0025-youtube-analytics-metrics-fetcher.md
//
// This project uploads to 3 separate YouTube channels (one per vertical, ADR-0025 addendum) —
// each requires its OWN OAuth consent (its own Google account with Manager/Owner access), so
// credentials are stored per-channel-alias, not as a single shared token.
//
// Modes:
//   --setup-oauth --channel <alias>     one-time interactive OAuth consent for that channel,
//                                        writes GOOGLE_REFRESH_TOKEN_<ALIAS> into .env
//   --exchange-code <code> --channel <alias>   same, but using a code already copied from the
//                                        browser's address bar (fallback when the local callback
//                                        port is occupied by something else)
//   --whoami --channel <alias>          smoke test: refresh that channel's token, run one query
//   --dry-run                           skip real API calls, return mock data (validates plumbing/shape only)
//   (default)                           real fetch — input via stdin JSON
//                                        [{videoId, durationSeconds?, channel}] or
//                                        --ids a,b,c --channel <alias>
//
// Output (default/--dry-run mode): a JSON array on stdout, one entry per input video.

import { createServer } from "node:http";
import { existsSync, readFileSync, writeFileSync, copyFileSync } from "node:fs";
import { exec } from "node:child_process";

const ENV_PATH = ".env";
const ENV_EXAMPLE_PATH = ".env.example";
const TOKEN_URL = "https://oauth2.googleapis.com/token";
const AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth";
const ANALYTICS_URL = "https://youtubeanalytics.googleapis.com/v2/reports";
const SCOPE = "https://www.googleapis.com/auth/yt-analytics.readonly";

// Confirmed by direct API probing (ADR-0025 addendum, 2026-07-12) — "channel==MINE" resolves to
// whichever channel the authenticated Google Account's own identity owns, which is NOT
// necessarily any of these 3 project channels depending on which account did the consent. Always
// address channels explicitly by ID, never MINE.
const CHANNEL_ALIASES: Record<string, string> = {
  finance: "UCG_yrDQF5Sj6iMTZB0KSBAA", // MONEY BLINDSPOT (hardknocks, dangote, giannis, ...)
  health: "UC4hMMkCOuGlV9bYl8wA8RGA", // Giảm Cân Healthy - Thực Chiến (bacsihai)
  aiwork: "UCop24nsu-TdXZSAO_Ii_QbA", // Working With AI (aiwork)
};

function resolveChannelId(alias: string): string {
  const id = CHANNEL_ALIASES[alias];
  if (!id) throw new Error(`Unknown channel alias "${alias}" — expected one of: ${Object.keys(CHANNEL_ALIASES).join(", ")}`);
  return id;
}

function tokenEnvKey(alias: string): string {
  return `GOOGLE_REFRESH_TOKEN_${alias.toUpperCase()}`;
}

type VideoInput = { videoId: string; durationSeconds?: number; channel?: string };

type RetentionPoint = { elapsedRatio: number; elapsedSeconds: number | null; audienceWatchRatio: number };
type KeyMoment = { type: "dip" | "peak"; elapsedSeconds: number | null; elapsedRatio: number; magnitudePct: number; zScore: number };

type Availability<T> = { available: true; value: T } | { available: false; reason: string };

type VideoMetrics = {
  videoId: string;
  views?: number;
  averageViewDuration?: number;
  averageViewPercentage?: number;
  ctr?: Availability<number>;
  engagementRetention: Availability<number>;
  retentionCurve?: RetentionPoint[];
  keyMoments?: KeyMoment[];
  error?: string;
};

function loadEnv(): void {
  if (!existsSync(ENV_PATH)) return;
  try {
    // Node >=20.12 built-in — avoids a `dotenv` runtime dependency.
    (process as any).loadEnvFile(ENV_PATH);
  } catch (err) {
    console.error(`Warning: failed to load ${ENV_PATH}: ${(err as Error).message}`);
  }
}

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing ${name} in .env — see .env.example (run: cp .env.example .env, fill it in, then npm run oauth:setup:<channel>)`);
  }
  return value;
}

function upsertEnvVar(key: string, value: string): void {
  if (!existsSync(ENV_PATH)) {
    if (existsSync(ENV_EXAMPLE_PATH)) copyFileSync(ENV_EXAMPLE_PATH, ENV_PATH);
    else writeFileSync(ENV_PATH, "");
  }
  const text = readFileSync(ENV_PATH, "utf8");
  const line = `${key}=${value}`;
  const pattern = new RegExp(`^${key}=.*$`, "m");
  const next = pattern.test(text) ? text.replace(pattern, line) : `${text.trimEnd()}\n${line}\n`;
  writeFileSync(ENV_PATH, next);
}

async function readStdin(): Promise<string> {
  const chunks: Buffer[] = [];
  for await (const chunk of process.stdin) chunks.push(chunk as Buffer);
  return Buffer.concat(chunks).toString("utf8");
}

// ---- OAuth ----

async function exchangeCodeForRefreshToken(
  code: string,
  clientId: string,
  clientSecret: string,
  redirectUri: string,
  channelAlias: string,
): Promise<void> {
  const tokenRes = await fetch(TOKEN_URL, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      code,
      client_id: clientId,
      client_secret: clientSecret,
      redirect_uri: redirectUri,
      grant_type: "authorization_code",
    }),
  });
  const tokenJson: any = await tokenRes.json();
  if (!tokenRes.ok) throw new Error(`Token exchange failed: ${JSON.stringify(tokenJson)}`);
  if (!tokenJson.refresh_token) {
    throw new Error(
      "No refresh_token in response — Google only issues one on first consent. Revoke prior access at https://myaccount.google.com/permissions and re-run.",
    );
  }
  const key = tokenEnvKey(channelAlias);
  upsertEnvVar(key, tokenJson.refresh_token);
  console.error(`Success — ${key} written to .env`);
}

// Fallback for --setup-oauth when the local callback port is already occupied by something
// else (e.g. Jenkins on 8080): exchange an authorization code copied by hand from the browser's
// address bar after Google's redirect, without needing our own server to receive it. The
// redirect_uri here is used only for Google's server-side validation that it matches the
// original auth request — it does not need to be reachable for this call to succeed.
async function exchangeCode(code: string, channelAlias: string): Promise<void> {
  loadEnv();
  resolveChannelId(channelAlias); // validates alias early, before spending the (single-use) code
  const clientId = requireEnv("GOOGLE_CLIENT_ID");
  const clientSecret = requireEnv("GOOGLE_CLIENT_SECRET");
  const redirectUri = requireEnv("GOOGLE_REDIRECT_URI");
  await exchangeCodeForRefreshToken(code, clientId, clientSecret, redirectUri, channelAlias);
}

async function setupOAuth(channelAlias: string): Promise<void> {
  loadEnv();
  resolveChannelId(channelAlias);
  const clientId = requireEnv("GOOGLE_CLIENT_ID");
  const clientSecret = requireEnv("GOOGLE_CLIENT_SECRET");
  const redirectUri = requireEnv("GOOGLE_REDIRECT_URI");
  const port = Number(new URL(redirectUri).port || 80);

  const authUrl = new URL(AUTH_URL);
  authUrl.searchParams.set("client_id", clientId);
  authUrl.searchParams.set("redirect_uri", redirectUri);
  authUrl.searchParams.set("response_type", "code");
  authUrl.searchParams.set("scope", SCOPE);
  authUrl.searchParams.set("access_type", "offline");
  authUrl.searchParams.set("prompt", "consent");

  console.error(`Authorizing channel "${channelAlias}" — sign in with the Google account that has Manager/Owner access to it.`);
  console.error("Open this URL to authorize (attempting to open it automatically too):");
  console.error(authUrl.toString());
  exec(`open "${authUrl.toString()}"`, () => {
    /* best-effort only — ignore failure on non-macOS */
  });

  const code = await new Promise<string>((resolve, reject) => {
    const server = createServer((req, res) => {
      const url = new URL(req.url ?? "/", redirectUri);
      const err = url.searchParams.get("error");
      const authCode = url.searchParams.get("code");
      if (err) {
        res.end(`OAuth error: ${err}. You can close this tab.`);
        server.close();
        reject(new Error(`OAuth consent denied/error: ${err}`));
        return;
      }
      if (authCode) {
        res.end("Authorized — you can close this tab and return to the terminal.");
        server.close();
        resolve(authCode);
      }
    });
    server.on("error", (err: NodeJS.ErrnoException) => {
      if (err.code === "EADDRINUSE") {
        reject(
          new Error(
            `Port ${port} is already in use by another process — cannot receive the OAuth redirect. ` +
              `Either free the port, change GOOGLE_REDIRECT_URI to a different port (and update it on the ` +
              `OAuth client in Google Cloud Console to match), or if you already have a ?code=... from the ` +
              `browser's address bar, run: npm run --silent metrics:fetch -- --exchange-code "<code>" --channel ${channelAlias}`,
          ),
        );
      } else {
        reject(err);
      }
    });
    server.listen(port);
  });

  await exchangeCodeForRefreshToken(code, clientId, clientSecret, redirectUri, channelAlias);
}

async function getAccessToken(channelAlias: string): Promise<string> {
  loadEnv();
  const clientId = requireEnv("GOOGLE_CLIENT_ID");
  const clientSecret = requireEnv("GOOGLE_CLIENT_SECRET");
  const refreshToken = requireEnv(tokenEnvKey(channelAlias));

  const res = await fetch(TOKEN_URL, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      refresh_token: refreshToken,
      grant_type: "refresh_token",
    }),
  });
  const json: any = await res.json();
  if (!res.ok) throw new Error(`Token refresh failed for channel "${channelAlias}": ${JSON.stringify(json)}`);
  return json.access_token;
}

async function whoami(channelAlias: string): Promise<void> {
  const channelId = resolveChannelId(channelAlias);
  const accessToken = await getAccessToken(channelAlias);
  const url = new URL(ANALYTICS_URL);
  url.searchParams.set("ids", `channel==${channelId}`);
  url.searchParams.set("startDate", "2020-01-01");
  url.searchParams.set("endDate", todayISO());
  url.searchParams.set("metrics", "views");
  const res = await fetch(url, { headers: { Authorization: `Bearer ${accessToken}` } });
  const json: any = await res.json();
  if (!res.ok) throw new Error(`Analytics API call failed for channel "${channelAlias}" (${channelId}): ${JSON.stringify(json)}`);
  console.error(`Auth OK for "${channelAlias}" (${channelId}). Lifetime views (sanity check):`, JSON.stringify(json.rows));
}

// ---- Analytics fetch ----

function todayISO(): string {
  return new Date().toISOString().slice(0, 10);
}

async function analyticsQuery(accessToken: string, channelId: string, params: Record<string, string>): Promise<any> {
  const url = new URL(ANALYTICS_URL);
  url.searchParams.set("ids", `channel==${channelId}`);
  url.searchParams.set("startDate", "2020-01-01");
  url.searchParams.set("endDate", todayISO());
  for (const [key, value] of Object.entries(params)) url.searchParams.set(key, value);
  const res = await fetch(url, { headers: { Authorization: `Bearer ${accessToken}` } });
  const json: any = await res.json();
  if (!res.ok) throw new Error(JSON.stringify(json));
  return json;
}

async function fetchTopLineMetrics(
  accessToken: string,
  channelId: string,
  videoIds: string[],
): Promise<Map<string, { views?: number; averageViewDuration?: number; averageViewPercentage?: number; ctr: Availability<number> }>> {
  const result = new Map<
    string,
    { views?: number; averageViewDuration?: number; averageViewPercentage?: number; ctr: Availability<number> }
  >();
  const filters = `video==${videoIds.join(",")}`;

  // Confirmed (ADR-0025 addendum): `impressions`/`impressionsClickThroughRate` are not
  // recognized metric identifiers on this API at all (400 Unknown identifier) — this always
  // fails, kept as a guarded attempt in case that ever changes rather than assumed permanently.
  let ctrReason = "";
  let withCtr: any = null;
  try {
    withCtr = await analyticsQuery(accessToken, channelId, {
      dimensions: "video",
      filters,
      metrics: "views,averageViewDuration,averageViewPercentage,impressions,impressionsClickThroughRate",
    });
  } catch (err) {
    ctrReason = (err as Error).message;
  }

  const base =
    withCtr ??
    (await analyticsQuery(accessToken, channelId, {
      dimensions: "video",
      filters,
      metrics: "views,averageViewDuration,averageViewPercentage",
    }));

  const headers: string[] = (base.columnHeaders ?? []).map((h: any) => h.name);
  const videoIdx = headers.indexOf("video");
  const viewsIdx = headers.indexOf("views");
  const avdIdx = headers.indexOf("averageViewDuration");
  const avpIdx = headers.indexOf("averageViewPercentage");
  const ctrIdx = headers.indexOf("impressionsClickThroughRate");

  for (const row of base.rows ?? []) {
    const id = row[videoIdx];
    const ctr: Availability<number> =
      ctrIdx !== -1
        ? { available: true, value: row[ctrIdx] }
        : { available: false, reason: ctrReason || "impressionsClickThroughRate not returned by API for this video/date range" };
    result.set(id, {
      views: viewsIdx !== -1 ? row[viewsIdx] : undefined,
      averageViewDuration: avdIdx !== -1 ? row[avdIdx] : undefined,
      averageViewPercentage: avpIdx !== -1 ? row[avpIdx] : undefined,
      ctr,
    });
  }
  return result;
}

async function fetchRetentionCurve(
  accessToken: string,
  channelId: string,
  videoId: string,
  durationSeconds?: number,
): Promise<RetentionPoint[]> {
  const json = await analyticsQuery(accessToken, channelId, {
    dimensions: "elapsedVideoTimeRatio",
    filters: `video==${videoId}`,
    metrics: "audienceWatchRatio",
  });
  const headers: string[] = (json.columnHeaders ?? []).map((h: any) => h.name);
  const ratioIdx = headers.indexOf("elapsedVideoTimeRatio");
  const watchIdx = headers.indexOf("audienceWatchRatio");
  const rows: RetentionPoint[] = (json.rows ?? [])
    .map((row: any[]) => {
      const elapsedRatio = row[ratioIdx];
      return {
        elapsedRatio,
        elapsedSeconds: durationSeconds != null ? Number((elapsedRatio * durationSeconds).toFixed(2)) : null,
        audienceWatchRatio: row[watchIdx],
      };
    })
    .sort((a: RetentionPoint, b: RetentionPoint) => a.elapsedRatio - b.elapsedRatio);
  return rows;
}

// ---- Key moment detection ----
// Threshold derived per-video (z-score vs this video's own smoothed baseline) rather than a
// hardcoded magnitude — same norm as this project's pause-trimming rule (AGENTS.md).
function detectKeyMoments(curve: RetentionPoint[], durationSeconds?: number): KeyMoment[] {
  const n = curve.length;
  if (n < 5) return [];

  const windowSeconds = 2; // reuses the 2-Second Rule pacing unit (ADR-0016)
  const windowPoints =
    durationSeconds != null
      ? Math.max(1, Math.round((windowSeconds / durationSeconds) * n))
      : Math.max(1, Math.round(n * 0.02));

  const values = curve.map((p) => p.audienceWatchRatio);
  const smoothed = values.map((_, i) => {
    const lo = Math.max(0, i - windowPoints);
    const hi = Math.min(n - 1, i + windowPoints);
    let sum = 0;
    for (let j = lo; j <= hi; j++) sum += values[j];
    return sum / (hi - lo + 1);
  });

  const residuals = values.map((v, i) => v - smoothed[i]);
  const mean = residuals.reduce((a, b) => a + b, 0) / n;
  const variance = residuals.reduce((a, b) => a + (b - mean) ** 2, 0) / n;
  const stdDev = Math.sqrt(variance);
  if (stdDev === 0) return [];

  const zScores = residuals.map((r) => (r - mean) / stdDev);
  const THRESHOLD = 1.5;

  type Flagged = { index: number; z: number; type: "dip" | "peak" };
  const flagged: Flagged[] = [];
  for (let i = 0; i < n; i++) {
    if (zScores[i] <= -THRESHOLD) flagged.push({ index: i, z: zScores[i], type: "dip" });
    else if (zScores[i] >= THRESHOLD) flagged.push({ index: i, z: zScores[i], type: "peak" });
  }

  // Merge contiguous same-type runs into one moment, keeping the most extreme point.
  const moments: KeyMoment[] = [];
  let run: Flagged[] = [];
  const flushRun = () => {
    if (run.length === 0) return;
    const extreme = run.reduce((a, b) => (Math.abs(b.z) > Math.abs(a.z) ? b : a));
    const point = curve[extreme.index];
    moments.push({
      type: extreme.type,
      elapsedSeconds: point.elapsedSeconds,
      elapsedRatio: point.elapsedRatio,
      magnitudePct: Number(((residuals[extreme.index] / smoothed[extreme.index]) * 100).toFixed(1)),
      zScore: Number(extreme.z.toFixed(2)),
    });
    run = [];
  };
  for (let i = 0; i < flagged.length; i++) {
    if (run.length === 0 || (flagged[i].index === run[run.length - 1].index + 1 && flagged[i].type === run[run.length - 1].type)) {
      run.push(flagged[i]);
    } else {
      flushRun();
      run.push(flagged[i]);
    }
  }
  flushRun();

  return moments.sort((a, b) => Math.abs(b.zScore) - Math.abs(a.zScore)).slice(0, 3);
}

// ---- Real fetch orchestration ----

async function fetchAll(inputs: VideoInput[]): Promise<VideoMetrics[]> {
  const groups = new Map<string, VideoInput[]>();
  for (const input of inputs) {
    if (!input.channel) {
      // handled per-item below via the "missing channel" error path
    }
    const key = input.channel ?? "__missing__";
    const list = groups.get(key) ?? [];
    list.push(input);
    groups.set(key, list);
  }

  const results: VideoMetrics[] = [];

  const missing = groups.get("__missing__");
  if (missing) {
    for (const input of missing) {
      results.push({
        videoId: input.videoId,
        engagementRetention: { available: false, reason: "no channel specified" },
        error: `Missing "channel" field — expected one of: ${Object.keys(CHANNEL_ALIASES).join(", ")}`,
      });
    }
    groups.delete("__missing__");
  }

  for (const [channelAlias, groupInputs] of groups) {
    let channelId: string;
    let accessToken: string;
    try {
      channelId = resolveChannelId(channelAlias);
      accessToken = await getAccessToken(channelAlias);
    } catch (err) {
      for (const input of groupInputs) {
        results.push({
          videoId: input.videoId,
          engagementRetention: { available: false, reason: "auth failed" },
          error: `Channel "${channelAlias}": ${(err as Error).message}`,
        });
      }
      continue;
    }

    let topLine: Awaited<ReturnType<typeof fetchTopLineMetrics>>;
    try {
      topLine = await fetchTopLineMetrics(
        accessToken,
        channelId,
        groupInputs.map((i) => i.videoId),
      );
    } catch (err) {
      for (const input of groupInputs) {
        results.push({
          videoId: input.videoId,
          engagementRetention: { available: false, reason: "fetch failed" },
          error: `Top-line metrics fetch failed for channel "${channelAlias}": ${(err as Error).message}`,
        });
      }
      continue;
    }

    for (const input of groupInputs) {
      try {
        const line = topLine.get(input.videoId);
        const retentionCurve = await fetchRetentionCurve(accessToken, channelId, input.videoId, input.durationSeconds);
        const keyMoments = detectKeyMoments(retentionCurve, input.durationSeconds);
        results.push({
          videoId: input.videoId,
          views: line?.views,
          averageViewDuration: line?.averageViewDuration,
          averageViewPercentage: line?.averageViewPercentage,
          ctr: line?.ctr,
          engagementRetention: {
            available: false,
            reason: "no documented YouTube Analytics API field found for Shorts swipe-away/engagement retention; see ADR-0025",
          },
          retentionCurve,
          keyMoments,
        });
      } catch (err) {
        results.push({
          videoId: input.videoId,
          engagementRetention: { available: false, reason: "fetch failed" },
          error: (err as Error).message,
        });
      }
    }
  }
  return results;
}

function dryRunResults(inputs: VideoInput[]): VideoMetrics[] {
  return inputs.map((input) => {
    const n = 100;
    const curve: RetentionPoint[] = Array.from({ length: n }, (_, i) => {
      const elapsedRatio = i / (n - 1);
      const base = 1 - 0.6 * elapsedRatio;
      const dip = elapsedRatio > 0.15 && elapsedRatio < 0.2 ? -0.15 : 0;
      return {
        elapsedRatio,
        elapsedSeconds: input.durationSeconds != null ? Number((elapsedRatio * input.durationSeconds).toFixed(2)) : null,
        audienceWatchRatio: Math.max(0, base + dip),
      };
    });
    return {
      videoId: input.videoId,
      views: 999,
      averageViewDuration: input.durationSeconds ? input.durationSeconds * 0.4 : 20,
      averageViewPercentage: 40,
      ctr: { available: true, value: 4.2 },
      engagementRetention: { available: false, reason: "dry-run: not fetched" },
      retentionCurve: curve,
      keyMoments: detectKeyMoments(curve, input.durationSeconds),
    };
  });
}

async function parseInputs(): Promise<VideoInput[]> {
  const args = process.argv.slice(2);
  const idsIdx = args.indexOf("--ids");
  if (idsIdx !== -1) {
    const ids = args[idsIdx + 1]?.split(",").map((s) => s.trim()) ?? [];
    const channelIdx = args.indexOf("--channel");
    const channel = channelIdx !== -1 ? args[channelIdx + 1] : undefined;
    return ids.map((videoId) => ({ videoId, channel }));
  }
  if (process.stdin.isTTY) {
    throw new Error("No --ids given and stdin is a TTY — pipe JSON [{videoId, durationSeconds?, channel}] or pass --ids id1,id2 --channel <alias>");
  }
  const raw = await readStdin();
  if (!raw.trim()) throw new Error("Empty stdin — expected JSON [{videoId, durationSeconds?, channel}]");
  return JSON.parse(raw);
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  try {
    const channelIdx = args.indexOf("--channel");
    const channelAlias = channelIdx !== -1 ? args[channelIdx + 1] : undefined;

    if (args.includes("--setup-oauth")) {
      if (!channelAlias) throw new Error(`--setup-oauth requires --channel <alias> (one of: ${Object.keys(CHANNEL_ALIASES).join(", ")})`);
      await setupOAuth(channelAlias);
      return;
    }
    const exchangeIdx = args.indexOf("--exchange-code");
    if (exchangeIdx !== -1) {
      const code = args[exchangeIdx + 1];
      if (!code) throw new Error("--exchange-code requires a value (the ?code=... from the redirect URL)");
      if (!channelAlias) throw new Error(`--exchange-code requires --channel <alias> (one of: ${Object.keys(CHANNEL_ALIASES).join(", ")})`);
      await exchangeCode(code, channelAlias);
      return;
    }
    if (args.includes("--whoami")) {
      if (!channelAlias) throw new Error(`--whoami requires --channel <alias> (one of: ${Object.keys(CHANNEL_ALIASES).join(", ")})`);
      await whoami(channelAlias);
      return;
    }
    const inputs = await parseInputs();
    const results = args.includes("--dry-run") ? dryRunResults(inputs) : await fetchAll(inputs);
    process.stdout.write(JSON.stringify(results, null, 2) + "\n");
  } catch (err) {
    console.error(`Error: ${(err as Error).message}`);
    process.exit(1);
  }
}

main();
