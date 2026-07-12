# ADR 0025: YouTube Analytics Metrics Fetcher (OAuth, not extension or scraping)

**Date:** 2026-07-12
**Status:** Accepted

## Context

The project's tracking system (`docs/experiments/EXPERIMENT-LOG.md` + `docs/production/*.md`)
has a gap: `.claude/skills/log-video/SKILL.md` logs a video's identity (video ID, upload date,
the date 48h metrics become safe to fetch — AGENTS.md's Known Pitfalls: metrics are noisy before
48h) but explicitly leaves AVD/CTR/views/Stayed/Swiped-Away as `pending`, to be filled in later
by hand from YouTube Studio (`docs/WORKFLOW.md` Stage 6: "Fetch từ YouTube Studio").

The user asked how to automate that manual step, and specifically whether a Firefox/Chrome
browser extension was needed. AVD/CTR/retention are private, channel-owner-only data — not
public page data `yt-dlp` can already pull. Three ways to get it automatically:

1. **Official YouTube Analytics API via OAuth** (`yt-analytics.readonly` scope) — the standard,
   supported way to read this data programmatically.
2. **Browser automation against YouTube Studio's UI** (Playwright, reusing the Chrome profile
   already used for uploads per `docs/adr/0009-autonomous-optimization-system.md`) — no OAuth
   setup, but brittle: breaks whenever YouTube changes Studio's UI.
3. **A browser extension** — a content script that scrapes Studio pages as the user browses
   them. No precedent for this anywhere in this project's ADRs/CONTEXT.md; would require
   building and maintaining a whole separate extension codebase for the same data the other two
   options get more directly.

## Decision

Use the **official YouTube Analytics API via OAuth**, not a browser extension and not Studio-UI
scraping.

- One-time setup: a Google Cloud project, the YouTube Analytics API enabled, an OAuth Client ID
  of type **Desktop app**, and a one-time interactive consent flow (`npm run oauth:setup`) that
  the user runs themselves — Claude cannot click through Google's consent screen. The resulting
  refresh token is written to a git-ignored `.env` (see `.env.example` for the required fields:
  `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`, `GOOGLE_REFRESH_TOKEN`).
- Implementation: `src/platforms/youtube-analytics.ts` — the first real file in the target `src/`
  architecture AGENTS.md describes (this repo's `src/` did not exist before this ADR). Zero
  runtime dependencies: plain `fetch()` for the OAuth token exchange/refresh and the Analytics
  API calls, and Node's built-in `process.loadEnvFile()` instead of a `dotenv` dependency.
  Invoked via `npm run metrics:fetch` (already the target command name documented in AGENTS.md's
  Commands table).
- Orchestration: a new Claude Code Skill, `.claude/skills/fetch-metrics/SKILL.md`, mirroring
  `log-video`'s pattern (shell out for raw data, do doc-editing in the skill itself). Batch mode
  by default: scans for videos past their 48h deadline still marked "Not yet fetched", with an
  optional single-video argument to force a refetch.
- Storage: extends the *existing* tracking system (`docs/production/*.md` Status table +
  `## Retention Analysis` section, `docs/experiments/EXPERIMENT-LOG.md` row updates) — does
  **not** resurrect `data/video_metrics.db`/`data/tracked_videos.csv`, which are a deprecated
  MAB-era scheme per `log-video`'s own rule.
- Per-second retention curve data (too bulky for a markdown table) is written to
  `output/projects/<project>/final/<video-id>-retention.csv`; the production doc gets a prose
  summary of detected key moments (dips/peaks) plus a link to the CSV.
- Key-moment detection (rolling-average residual, per-video z-score, threshold `|z| > 1.5`) is
  computed inside `youtube-analytics.ts`, not left for a human/LLM to eyeball off the CSV. The
  threshold is derived from each video's *own* curve statistics, never a value copy-pasted
  across videos — same norm this project already applies to pause-trim thresholds (AGENTS.md
  Known Pitfalls).

**Known limitation, not yet resolved**: there is no confirmed YouTube Analytics API field
equivalent to YouTube Studio's Shorts-specific "How viewers engaged → Swiped away" panel (the
source of the `Stayed (Engagement/Hook)` / `Swiped Away` columns in EXPERIMENT-LOG.md — those
appear to use impressions/Shorts-feed as their denominator, a different data family from the
on-watch-page retention curve). Until/unless this is confirmed available, the fetch-metrics
skill leaves those two columns `pending` rather than approximating them from the retention
curve's early values — this project has a standing anti-fabrication norm (e.g. `bacsihai_v5`'s
"deliberately qualitative, matching what the source actually claims, no fabricated percentage")
that applies equally here. Likewise, per-video CTR (impressions-based) availability via this API
is unconfirmed for Shorts and is reported as unavailable with a reason string if the API call
fails, rather than silently omitted.

## Consequences

- This is the first OAuth integration and the first real `src/` TypeScript file in the repo —
  `package.json` gains `devDependencies` (`typescript`, `tsx`, `@types/node`) and two npm
  scripts; `.gitignore` gains `.env` and `node_modules/`.
- AVD/views/overall-retention-% automation works end-to-end once OAuth is set up. Hook-specific
  engagement (Stayed/Swiped-Away) and CTR may remain partially or fully manual until the API's
  real behavior is confirmed against a live video — the first real fetch (against
  `hardknocks_lawnmower_v1`, video `dHDpDXSIAkA`, already past its 48h mark) is the point where
  this gets resolved in practice, not on paper.
- If a future check finds the API *does* expose an equivalent field, that supersedes this ADR's
  "leave pending" rule — record it as an addendum here rather than silently changing the skill's
  behavior.
- Does not change anything about upload automation (`docs/adr/0009-autonomous-optimization-system.md`'s
  Chrome-profile approach) — this ADR is read-only analytics, a separate concern from write/upload.

## Related

- ADR 0009: Autonomous Optimization System (the target Metrics Fetcher this ADR actually
  implements a first real slice of; see that ADR's addendum correcting its stale
  "no auth, uses Studio export" phrasing)
- ADR 0016: Frequent Editing (the 2-Second Rule reused as the key-moment rolling-average window)
- `.claude/skills/log-video/SKILL.md`: the identity-logging half this ADR's skill completes
- `.claude/skills/fetch-metrics/SKILL.md`: the orchestration skill this ADR specifies
- `src/platforms/youtube-analytics.ts`: the implementation
