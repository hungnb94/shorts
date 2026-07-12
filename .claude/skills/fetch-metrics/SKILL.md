---
name: fetch-metrics
description: Fetch YouTube Analytics (AVD, CTR, views, per-second retention curve) for uploaded Shorts that are past their 48h wait and still marked "Not yet fetched" in docs/production/*.md + docs/experiments/EXPERIMENT-LOG.md, then fill those fields in. Use when the user asks to fetch/check/pull/track video metrics, run the metrics command, or invokes /fetch-metrics.
---

Implements the metrics-fetch half of Stage 6 ("Upload & Log") of `docs/WORKFLOW.md` — the half
that `log-video` deliberately leaves for later. `log-video` logs identity (video ID, upload
date, the 48h-fetch-after date) and explicitly never fills in AVD/Stayed/Swiped-Away. This
command fills in exactly those fields, once real data exists (AGENTS.md Known Pitfalls: metrics
are noisy before 48h — never fetch early).

Data source is the official YouTube Analytics API via OAuth (see
`docs/adr/0025-youtube-analytics-metrics-fetcher.md`) — not a browser extension, not YouTube
Studio UI scraping. The underlying script is `src/platforms/youtube-analytics.ts`, run via
`npm run metrics:fetch`.

## Input

`$ARGUMENTS` is optional:
- **Empty** (the common case): batch mode — scan for every video that is due (see Steps 1-2).
- **A YouTube URL or bare video ID**: force-refetch just that one video, even if already fetched
  or not yet 48h old (useful for testing or re-pulling after a correction).

## One-time setup (only needed the first time this skill is ever run)

Check whether `.env` exists and has a non-empty `GOOGLE_REFRESH_TOKEN`. If not, this is a
first-run — stop and tell the user to:
1. Create a Google Cloud project, enable the **YouTube Analytics API**, and create an OAuth
   Client ID of type **Desktop app** (see `docs/adr/0025-youtube-analytics-metrics-fetcher.md`
   for exact steps).
2. Copy `.env.example` to `.env` and fill in `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` /
   `GOOGLE_REDIRECT_URI`.
3. Run `npm run oauth:setup` themselves (this opens a browser consent screen — Claude cannot
   click through Google's interactive consent flow, so this one step is the user's to run).

Do not attempt to fetch metrics until this is done — offer to re-check once the user says it's set up.

## Steps

1. **Find candidate videos.** Read `docs/experiments/EXPERIMENT-LOG.md` and every
   `docs/production/*.md`. A video is a candidate if its production doc's `## Status` table has
   a `Metrics status` value containing the substring "Not yet fetched" (match by substring, not
   exact string — existing docs use varied prose like "Not yet fetched — too early..." or "Not
   yet fetched, too early").

2. **Filter to due videos** (batch mode only — skip this filter in single-video force-refetch
   mode). Parse each candidate's `Metrics fetch after (48h rule)` field and compare to the
   current date/time (`date` shell command). This field appears in two forms in the wild:
   - A full datetime, e.g. `2026-07-13 07:34 +07` — compare directly.
   - A bare date, e.g. `2026-07-12 or later` — treat as due starting `00:00` local on that date.
   Only videos whose deadline has passed, AND that have a real (non-placeholder) YouTube Video
   ID in the Status table, are due. Report which candidates were skipped as not-yet-due (don't
   silently drop them from the user-facing summary at the end).

3. **Gather each due video's duration** from its production doc's `## Video Specs` section
   (`- Duration: 51.4s`) or the matching EXPERIMENT-LOG.md row's Duration column — they should
   agree; if they don't, flag it rather than silently picking one.

4. **Call the fetcher.** Build the JSON input `[{"videoId": "...", "durationSeconds": ...}, ...]`
   and pipe it in:
   ```
   echo '<json>' | npm run --silent metrics:fetch
   ```
   **Must use `--silent`** (or call `npx tsx src/platforms/youtube-analytics.ts` directly) —
   plain `npm run metrics:fetch` prints an `> shorts@0.1.0 metrics:fetch` banner line to stdout
   ahead of the JSON, which breaks JSON parsing. Verified directly: `npm run --silent` omits the
   banner, plain `npm run` does not.
   For single-video force-refetch mode, `npm run --silent metrics:fetch -- --ids <videoId>` also
   works (no stdin needed, but then `durationSeconds` won't be known — pull duration from the
   doc yourself and don't worry if `elapsedSeconds` in the retention curve comes back `null`, only
   `elapsedRatio` will be usable in that case).
   If the call exits non-zero (hard auth failure), stop and tell the user to re-run
   `npm run oauth:setup` — don't touch any docs.

5. **For each video in the returned JSON array:**
   - If it has an `error` field: leave that video's docs untouched, note the error in your final
     report, move on to the next video.
   - Otherwise, write the retention curve to
     `output/projects/<project>/final/<video-id>-retention.csv` (columns
     `elapsed_ratio,elapsed_seconds,audience_watch_ratio`), where `<project>` comes from the
     production doc's existing `File:` line (e.g.
     `output/projects/hardknocks/final/...mp4` → project `hardknocks`).
   - Append a `## Retention Analysis` section to the production doc:
     ```markdown
     ## Retention Analysis
     _Auto-generated by the fetch-metrics skill, <today's date>. Full per-second curve:
     `output/projects/<project>/final/<video-id>-retention.csv`._

     - **Views**: <views> · **AVD**: <M:SS> (<averageViewPercentage>% of <duration>) · **CTR**: <value>% (or "not available via API — see ADR-0025")
     - **Key moments** (z-score vs this video's own smoothed baseline):
       - <type> at ~<elapsedSeconds>s (<magnitudePct>%, z=<zScore>)
       - (one bullet per entry in `keyMoments`, up to 3)
     ```
   - Update the production doc's Status table: `Metrics status` → literal `Fetched <today's date>`
     (no extra prose — a later run needs to recognize this string as "already done", so keep it
     exact). Leave `Metrics fetch after (48h rule)` untouched (it's a historical record of when
     the video became eligible, not a running state field).
   - Update the matching `docs/experiments/EXPERIMENT-LOG.md` row:
     - `AVD` → `averageViewDuration` formatted as `M:SS` (this column is a duration, not a
       percentage — confirmed from existing rows, e.g. `0:29`).
     - `Stayed (Retention/Overall)` → `averageViewPercentage`, formatted `NN.N%`.
     - **`Stayed (Engagement/Hook)` and `Swiped Away`**: the API has no confirmed field
       equivalent to YouTube Studio's Shorts-specific "how viewers engaged / swiped away" panel
       (see `engagementRetention.available` in the fetcher's output — expected `false` for now,
       per ADR-0025). **Do not approximate or invent a value for these two columns** — leave them
       exactly as `pending`. This mirrors `log-video`'s own "never invents these numbers" rule and
       the project's broader anti-fabrication norm (see AGENTS.md's bacsihai_v5 pitfall on not
       inventing a percentage the source never gave).
     - Add one short sentence to the Notes column: fetch date + a one-line key-moment summary +
       a pointer to the new `## Retention Analysis` section, not the full detail (that lives in
       the production doc).

6. **Do not commit.** Leave all edits as uncommitted working-tree changes, same as `log-video`
   and every other doc-editing skill in this repo.

7. **Report back**: which videos were fetched (with their headline numbers), which candidates
   were skipped as not-yet-due (with their due dates), and which fetches errored (with the
   error message, not silently dropped).

## Notes

- This command is idempotent for a video already marked `Fetched <date>` — batch mode will not
  re-select it (its `Metrics status` no longer contains "Not yet fetched"). To force a redo, use
  the single-video argument form.
- `data/tracked_videos.csv`, `data/video_metrics.db`, and `data/mab_state.json` are an older,
  deprecated tracking scheme — same as `log-video`'s existing rule, never touch them here either.
- If the API's `ctr.available` or `engagementRetention.available` ever flips to `true` in
  practice, that's worth flagging back to the user — it would mean ADR-0025's documented
  limitation is stale and the ADR should get an addendum, not that this skill's `pending`
  discipline should quietly change without discussion.
