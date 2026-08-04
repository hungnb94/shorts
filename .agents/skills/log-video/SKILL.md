---
name: log-video
description: Log a just-uploaded YouTube Short into this repo's tracking system (docs/experiments/EXPERIMENT-LOG.md + the matching docs/production/*.md doc). Use when the user pastes a YouTube URL/ID after manually uploading a video and asks to save/log/track it.
---

Implements Stage 6 ("Upload & Log") of `docs/WORKFLOW.md` for a video that was just manually
uploaded. This is a **post-upload identity log**, not a metrics fetch — retention/AVD data
isn't stable until 48h after upload (root `AGENTS.md` → Durable Data and Publishing), so this command never invents
or guesses those numbers. It only records what/when, and computes the exact date to come back
and fill in metrics.

## Input

`$ARGUMENTS` is a YouTube URL (`youtube.com/shorts/<id>`, `youtu.be/<id>`, or
`youtube.com/watch?v=<id>`) or a bare video ID, optionally followed by a project name if you
already know which `docs/production/<name>.md` this video belongs to.

## Steps

1. **Extract the video ID** from the URL/argument.

2. **Fetch real metadata** — don't ask the user to retype what YouTube already knows:
   ```
   yt-dlp --dump-json --no-warnings "https://youtube.com/watch?v=<id>"
   ```
   Pull `title`, `upload_date` (YYYYMMDD), and `duration` (seconds) from the JSON output.

3. **Find the matching production doc.** Search `docs/production/*.md` for one whose
   `## YouTube Title` section matches the fetched title (exact or near-exact — titles are
   copy-pasted from the doc at upload time, so this should match cleanly). If a project name
   was given as a second argument, use that doc directly instead of searching.
   - If exactly one match: use it.
   - If no match: list every production doc whose `## Status` table still says
     "Not yet uploaded, manual upload pending" and ask the user which one this is (do not
     guess silently — this determines which files get edited).
   - If the doc's Status table already has a real (non-placeholder) YouTube Video ID: confirm
     with the user before overwriting (this would mean re-logging an already-logged video).

4. **Compute the 48h metrics-fetch date.** Use the current date/time (not just yt-dlp's
   date-only `upload_date`, which loses the time-of-day) as the effective upload timestamp,
   since this command runs right after the manual upload. Add 48 hours.

5. **Update the production doc's `## Status` table**:
   - `YouTube Video ID` → the real ID (as a markdown link to the video is fine)
   - `Metrics fetch after (48h rule)` → the computed absolute datetime from step 4
   - `Metrics status` → `Not yet fetched, too early`
   - Leave `Rendered` untouched.

6. **Update `docs/experiments/EXPERIMENT-LOG.md`**: find the row for this video (matched by
   title/pipeline name — it will currently show `TBD (not yet uploaded)` or similar in the
   Video ID column) and:
   - Replace the Video ID column with the real ID
   - Fill in Duration from yt-dlp's `duration` if the row doesn't already have it
   - Leave Stayed (Engagement/Hook), Stayed (Retention/Overall), AVD, Swiped Away as `pending`
     — these are never filled in by this command
   - Update the Notes column to state the upload date and the 48h fetch-after date

7. **Do not touch** `data/tracked_videos.csv`, `data/video_metrics.db`, or `data/mab_state.json`
   — those belong to an older MAB-style tracking scheme for the finance vertical that isn't
   part of this repo's current per-project workflow (per AGENTS.md's Current Implementation
   section). Only edit the two doc files above.

8. **Do not commit.** Leave the edits as uncommitted changes, same as any other doc edit in
   this repo — only commit when the user explicitly asks.

9. **Report back**: which files were updated, the video ID/title matched, and the exact
   datetime to come back and fetch 48h metrics. If the user wants, offer to schedule a
   reminder for that time (`ScheduleWakeup` or similar), but don't do this automatically.

## Notes

- This command is idempotent for the same video: re-running it after a metrics fetch should
  update identity fields without clobbering any retention numbers a human has since filled in
  by hand (only touch the Video ID / Notes / Metrics-status fields described above, never the
  Stayed/AVD/Swiped-Away columns).
- If `yt-dlp` fails (private video, network issue, rate limit), fall back to asking the user
  for title/upload date/duration directly rather than blocking.
