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

## Addendum (2026-07-13): confirmed — `averageViewPercentage` runs systematically higher than Studio's real "Stayed to watch" (2nd data point)

A user-provided Studio screenshot for `dHDpDXSIAkA` (hardknocks_lawnmower_v1) gives a second real
data point beyond the Dangote case in the 2026-07-12 addendum above:

| Video | API `averageViewPercentage` | Studio "Stayed to watch" | Gap |
|---|---|---|---|
| Dangote (`ChWLcE3OYpA`) | 57.6% | 51.6% | +6.0pp |
| hardknocks_lawnmower_v1 (`dHDpDXSIAkA`) | 59.84% | 54.1% | +5.74pp |

Both cases show the API reading roughly 6 percentage points *higher* than Studio's real number,
in the same direction — no longer plausibly random drift, this looks like a systematic bias
(possibly a different denominator/window than Studio's Shorts-specific "Stayed to watch"
definition). Root cause still unidentified. Given 2/2 confirmed cases in the same direction,
`fetch-metrics` should stop treating this as merely "provisional, needs a cross-check" and treat
any API-populated `Stayed (Retention/Overall)` value as an approximation with a known positive
bias of roughly 5-6 percentage points until the cause is found — prefer a real Studio read when
the user provides one (as happened here) and overwrite the API value with it rather than keep
both. `dHDpDXSIAkA`'s `EXPERIMENT-LOG.md` row and `docs/production/hardknocks-lawnmower-v1.md`'s
`## Retention Analysis` section were corrected to the real Studio numbers (54.1% Stayed, 45.9%
Swiped, 0:30 AVD) on 2026-07-13.

Also observed: for this video, Studio's "Audience retention" panel's "Stayed to watch" (54.1%) and
the "How viewers engaged" panel's "Stayed to watch" (54.1%) read the *same* number — unlike
Dangote's historical row where `Stayed (Engagement/Hook)` (43.4%) and `Stayed (Retention/Overall)`
(51.6%) differ. Whether these two Studio panels always converge for Shorts, or only did so here by
coincidence, is not yet established — another open question for a future cross-check.

## Addendum (2026-07-13, 2nd): retraction — it is NOT a fixed +5-6pp bias; it's a different metric family entirely, and it's not a code bug

The addendum immediately above concluded, from 2 data points, that `averageViewPercentage` reads
a "systematic" +5-6pp higher than Studio's real "Stayed to watch." A 3rd real Studio screenshot
(`Mw7jeR6R6iE`, aiwork_v2) disproves that conclusion:

| Video | API `averageViewPercentage` | Studio "Stayed to watch" | Gap |
|---|---|---|---|
| Dangote (`ChWLcE3OYpA`) | 57.6% | 51.6% | +6.0pp |
| hardknocks_lawnmower_v1 (`dHDpDXSIAkA`) | 59.84% | 54.1% | +5.74pp |
| aiwork_v2 (`Mw7jeR6R6iE`) | 36.74% | 43.6% | **-6.86pp** |

The gap flips direction on the 3rd case. AVD tells the same story: API vs. Studio was +7s
(Dangote: 26s vs 19s), +1s (`dHDpDXSIAkA`: 31s vs 30s), then **-3s** (`Mw7jeR6R6iE`: 17s vs 20s).
There is no fixed-magnitude, fixed-direction correction factor to apply — the earlier "~5-6pp
positive bias" framing (and the numeric "corrected" estimates it produced for two other pending
videos, since retracted in `EXPERIMENT-LOG.md`) is wrong and should not be repeated.

**Root cause, investigated directly rather than assumed**: prompted by the user asking "maybe the
fetch-metrics code itself is wrong" — read `src/platforms/youtube-analytics.ts` end-to-end. The
query construction is correct: `dimensions=video`, `filters=video==<id>` (correctly scoped to the
specific video, not aggregated across others), metrics `views,averageViewDuration,
averageViewPercentage` (the real, documented metric names), and a `startDate` of `2020-01-01`
(predates every video in this project, so the range covers each video's full lifetime — equivalent
in intent to Studio's "since uploaded (lifetime)" window). **This is not a parameter/logic bug in
this project's code.**

Checked Google's official metric definitions
(developers.google.com/youtube/analytics/metrics): `averageViewDuration` and
`averageViewPercentage` are both documented as, verbatim, "the average length/percentage of a
video watched during a video playback. **As of December 13, 2021, this metric excludes looping
clips traffic.**" These are generic, pre-Shorts-era, long-form-video metrics. YouTube Studio's
Shorts-specific "Stayed to watch" / "How viewers engaged" panels are a separate, proprietary
Shorts-feed computation (swipe-based engagement, not simple watch-page playback) with **no
documented public Analytics API field**. This is the exact same root cause this ADR's original
Decision section already identified for `Stayed (Engagement/Hook)`/`Swiped Away` ("no confirmed
YouTube Analytics API field equivalent to YouTube Studio's Shorts-specific... panel") — this
addendum confirms, with 3 real data points, that the same limitation extends to
`Stayed (Retention/Overall)` too. The earlier "provisional mapping, needs a cross-check" framing
undersold this: it isn't a mapping that's slightly off, it's two different metrics from two
different systems that happen to both be percentages.

**Practical consequence for `fetch-metrics`**: never derive an estimated "real" number from the
API value (no correction factor exists). Continue writing the raw API value with a clear
"unconfirmed vs Studio" caveat when no real Studio read exists yet, and only ever overwrite with a
real Studio screenshot when the user provides one (Studio Cross-Check Correction section of the
skill) — never with a computed estimate.

## Addendum (2026-07-13, 3rd): ruled out "reporting lag" as the explanation; `engagedViews` tested and also doesn't match

After the 2nd addendum above, the user asked whether all of this might simply be YouTube Analytics
reporting lag (the API hasn't finished processing recent data yet) rather than a genuine
metric-family mismatch — a fair question given AGENTS.md's own separate "can lag well past 48h"
pitfall. Checked directly, two ways:

1. **Stability under re-fetch**: `dHDpDXSIAkA` was fetched twice in the same session, hours apart
   (once directly, once via a force-refetch requested to test idempotency). Both fetches returned
   *identical* numbers (987 views, AVD 31s, `averageViewPercentage` 59.84%) down to the decimal. If
   the gap vs. Studio's real 54.1% were a processing-lag artifact "catching up," the number should
   have moved between the two fetches. It didn't.
2. **Direction of the gap is inconsistent with lag**: reporting lag would mean the API
   undercounts recent activity — so `averageViewPercentage` should read *lower* than Studio's
   fully-processed number every time, if lag were the cause. Instead 2 of 3 confirmed cases show
   the API reading *higher* (Dangote +6.0pp, `dHDpDXSIAkA` +5.74pp) and only 1 reads lower
   (`Mw7jeR6R6iE` -6.86pp). A pure undercount-from-lag theory doesn't produce a metric that's
   sometimes higher than ground truth.

Conclusion: not reporting lag. Stands by the 2nd addendum's conclusion — genuinely different
metric systems, not something that resolves by waiting longer or re-fetching again later.

**Also tested `engagedViews`** (a real, valid metric — confirmed via live API calls, requires the
`creatorContentType` dimension; calling `metrics=views,engagedViews` with only `dimensions=video`
returns a `500 Internal error`, not a documented restriction, just an observed quirk) as a
candidate for a closer match to Studio's Shorts-specific numbers, since Studio's Engagement tab
literally has a tile labeled "Engaged views":

| Video | API `engagedViews`/`views` | Studio "Stayed to watch" | Gap | API `engagedViews` (raw) | Studio "Engaged views" (raw) |
|---|---|---|---|---|---|
| `dHDpDXSIAkA` | 516/987 = 52.28% | 54.1% | -1.82pp | 516 | 634 |
| `Mw7jeR6R6iE` | 113/396 = 28.54% | 43.6% | -15.06pp | 113 | 426 |
| Dangote (stale historical Studio number, not simultaneous) | 71/173 = 41.04% | 51.6% | -10.56pp | 71 | n/a |

Same-named metric, different values, in both the ratio and the raw count. `engagedViews` does not
give a reliable unified number either — don't retry this specific path expecting a different
outcome. Also confirmed via live 400 responses that `shownInFeed`, `swipedAway`, and
`uniqueViewers` are not valid metric identifiers on this API (ruling out the most obvious
guesses for Studio's "Shown in Feed" / "Viewed vs. swiped away" tiles having a direct API
equivalent under those names).

**Decision, given all of the above**: paused further investigation here at the user's request.
The practical rule from the 2nd addendum stands unchanged — YouTube Studio's real numbers are the
only reliable source for `Stayed (Retention/Overall)`, `Stayed (Engagement/Hook)`, `AVD`, and
`Swiped Away`; the API remains useful for `views`, the retention curve's shape, and key-moment
detection, not for these four columns. Whether to formally change `fetch-metrics`'s batch-mode
behavior to stop auto-filling those four columns from the API (vs. keep writing the API value with
an "unconfirmed" caveat, as it does today) is an open decision, not yet made — revisit before
relying on any of `EXPERIMENT-LOG.md`'s API-only `Stayed (Retention/Overall)`/`AVD` values for a
real MAB/optimization decision.

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
