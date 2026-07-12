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

## Addendum (2026-07-12): confirmed via real API calls against the live channel

Verified end-to-end with a real OAuth token against the actual channel (MONEY BLINDSPOT,
`UCG_yrDQF5Sj6iMTZB0KSBAA`):

- **CTR/impressions: confirmed unavailable, not just unconfirmed.** `metrics=impressions` (and
  `impressionsClickThroughRate`) returns a hard `400 Unknown identifier (impressions) given in
  field parameters.metrics` — this API simply does not expose an impressions/CTR metric under
  those names. `ctr.available` will always be `false` in practice; the fetch-metrics skill's
  "leave CTR pending" behavior is therefore the permanent behavior, not a temporary fallback.
- **`averageViewPercentage` vs `Stayed (Retention/Overall)`: mapping is provisional, not
  confirmed.** A real fetch against `ChWLcE3OYpA` (Dangote, `ADR-0016`'s benchmark) returned
  `averageViewPercentage: 57.6`, `averageViewDuration: 26s` — neither matches the historical
  EXPERIMENT-LOG.md row for this same video (`Stayed (Retention/Overall)`: 51.6%, `AVD`: 0:19).
  57.6% sits closer to that row's `Swiped Away` (57.7%) than to `Stayed (Retention/Overall)`.
  This may simply be natural drift (the historical numbers were a human's Studio read at an
  earlier point with fewer accumulated views; retention % can shift as more of the audience
  arrives later), or the metric-to-Studio-panel mapping assumed above may be wrong. **Not
  resolved here** — the fetch-metrics skill should flag this in its report the first several
  times it runs (cross-check the written `averageViewPercentage` against the same video's live
  Studio dashboard once) rather than trust the mapping silently.
- **New-video indexing lag, distinct from CTR/mapping issues**: the intended first test video,
  `dHDpDXSIAkA` (hardknocks_v1, uploaded 2026-07-10, public view count 1114 per `yt-dlp`, already
  past the 48h wait), returned **zero** for every metric (views, AVD, retention curve — all
  empty), and does not appear at all in a channel-wide `dimensions=video` breakdown that
  correctly lists 8 *other*, older videos on the same channel with real numbers (proving the
  query mechanics, auth, and channel scoping are all correct). This means the Analytics
  *reporting* API can lag well past the 48h mark for very recently uploaded videos on a
  low-traffic channel, independent of whatever YouTube Studio's own dashboard shows. Recorded as
  a new pitfall in AGENTS.md — always retry after another day or two if a due video comes back
  empty, rather than treating an empty result as "this video has no data."

## Addendum (2026-07-12): this project uploads to 3 separate channels — one OAuth token per channel, not one for "the channel"

This ADR's original Decision assumed a single OAuth token would cover fetching. That assumption
was wrong: the project uploads to **3 distinct YouTube channels**, one per vertical, confirmed
via `yt-dlp`'s public `channel`/`channel_id` fields on real uploaded videos:

| Channel | Channel ID | Vertical / project folders |
|---|---|---|
| MONEY BLINDSPOT | `UCG_yrDQF5Sj6iMTZB0KSBAA` | Finance (ADR-0001/0004) — `hardknocks`, `dangote`, `giannis` |
| Giảm Cân Healthy - Thực Chiến | `UC4hMMkCOuGlV9bYl8wA8RGA` | Health/Vietnamese (ADR-0019) — `bacsihai` |
| Working With AI | `UCop24nsu-TdXZSAO_Ii_QbA` | AI-education (ADR-0020) — `aiwork` |

Also confirmed the hard way: **`channel==MINE` is unreliable and must never be used.** It
resolves to whichever channel the *authenticated Google Account's own identity* owns — not
necessarily any of the 3 channels above, and not consistently the same one across different
consent flows by different accounts. One real OAuth consent (from the account already used for
MONEY BLINDSPOT) correctly returned MONEY BLINDSPOT's data under `channel==MINE`. A second
consent, done with a different Google account (the one that originally created all 3 Brand
Account channels), returned **403 Forbidden on all 3 explicit channel IDs**, including the one
that had just worked — meaning "having created a Brand Account channel" does not imply "currently
holds recognized Manager/Owner permission on it" for Analytics API purposes. Studio's own
account-switcher (which channels an identity can currently manage) is the reliable ground truth,
not assumptions about who "owns" a channel.

**Revised decision**: every explicit-channel query uses `channel==<ID>`, never `MINE`.
Credentials are stored one refresh token per channel alias
(`GOOGLE_REFRESH_TOKEN_FINANCE`/`_HEALTH`/`_AIWORK` in `.env`), sharing one OAuth Client
ID/Secret (Google Cloud OAuth Clients are reusable across multiple separate user consents — no
need for 3 separate Cloud projects). `npm run oauth:setup:<alias>` runs the consent flow once per
channel, each time signed in as whichever Google account Studio confirms has Manager/Owner access
to that specific channel. `src/platforms/youtube-analytics.ts`'s `fetchAll` groups a batch's
input videos by channel alias and fetches each group with its own token, so one channel's
missing/broken token does not block metrics for videos on a different, already-set-up channel in
the same run.

**Operational lesson, not a code defect**: exchanging a new authorization code for a given
`.env` key overwrites whatever refresh token was there before — there is no way to recover an
overwritten token short of re-running consent again with the correct account. `--exchange-code`
and `--setup-oauth` now require an explicit `--channel <alias>` so this can't happen by accident
across channels, but re-running consent for the *same* channel/alias will still overwrite that
channel's own prior token, which is expected (Google only issues a fresh refresh token on
`prompt=consent`, and there's no reason to keep an old one once a new one for the same channel
exists).

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
