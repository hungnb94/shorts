# aiwork_v4_prompt_bloat, "Why Adding More Instructions Makes Your AI Worse" (Multi-Clip Mashup)

## Status
| Field | Value |
|-------|-------|
| YouTube Video ID | Not yet uploaded |
| Rendered | 2026-07-12 |
| Uploaded | **Superseded by `aiwork_v5` — not to be uploaded.** User feedback: captions too small, hook question revealed progressively instead of shown all at once. Narrative/cut content is unchanged (v5 is a caption-style-only rebuild) — file stays on disk as the known-issues record. See `docs/production/aiwork-v5-prompt-bloat.md`. |
| Metrics fetch after (48h rule) | N/A, will never be uploaded |
| Metrics status | N/A |

## Video Specs
- Duration: 58.7s
- Resolution: 1080x1920 (9:16 portrait)
- Codec: H.264 (libx264, crf 18/20), ~33fps (30fps source sped up 1.1x via `setpts`)
- Audio: AAC, 192kbps, 48kHz, stereo (single source-audio track, no TTS)
- File: `output/projects/aiwork/final/2026-07-12-aiwork_v4_prompt_bloat.mp4` (9.3MB)
- Render script: `pipeline/aiwork/render_aiwork_v4.py`

## YouTube Title
Why Adding More Instructions Makes Your AI Worse

## YouTube Description
See `output/projects/aiwork/final/2026-07-12-aiwork_v4_prompt_bloat.txt` (credits the source channel per ADR-0021's brand-sensitivity mitigation, still applicable — same mitigation, second official-channel source).

## Source
- Channel: Claude (Anthropic's own official YouTube channel)
- Source video ID: `mWvtOHlZM-I`, "Tool, skill, or subagent? Decomposing an agent that outgrew its prompt", presented by William Steuk (Applied AI, Anthropic) at Code with Claude London, 2706.0s (~45:06), max available quality confirmed (1080p is the ceiling, no 4K exists for this source)
- Second official-channel source for this niche, same source as `aiwork_v3` — see `docs/production/aiwork-v3-prompt-bloat.md` for the original grilling-session decisions (footage policy → ADR-0026, audience-fit, sub-format, hook thesis). This doc only covers what changed for v4.

## Why This Segment (what changed from v3)

A new `/grilling` session resolved the fix:
1. **Approach** (option A, confirmed): add a new 7th clip (FIX) with a fully self-authored caption, rather than re-cutting existing clips or adding narration to REINFORCE.
2. **Footage availability check** (blocking, done before committing to the plan): re-scanned the source for any footage that states the fix in generalizable, non-jargon words. None exists — the only presenter-visible window right after REINFORCE (t=105-145s) is workshop agenda-setting language, still full of the same jargon ("agentic primitives", "engineers and architects") the audience-fit decision already excludes. So FIX reuses more footage from the same safe intro window (105.04-113.68s, immediately following REINFORCE in source time) with captions that have no relation to the underlying spoken audio — same pattern already established by HOOK in v3.
3. **Ordering** (option A, confirmed): REINFORCE before FIX (not before REINFORCE, the initial framing floated in the session) — reads better as problem → you're-not-alone (proof) → here's-what-fixed-it → sign-off.
4. **Exact wording/timing**: confirmed by the user before rendering: "THE FIX:" / "SMALL FOCUSED STEPS -" / "NOT ONE GIANT PROMPT." — directly pays off the `this_or_that_overlay` shown earlier during COMPLICATION-2.

New 7-piece cut (all from the same fixed wide-shot crop, `crop=1080:1920:2073:0`, verified in v3):

| # | Role | Range | Raw dur | Quote / note |
|---|------|-------|---------|-------|
| 1 | HOOK | 45.48-54.60 | 9.12s | (unchanged from v3 — see v3 doc) |
| 2 | ESCALATE | 55.56-67.50 | 11.94s | (unchanged from v3) |
| 3 | COMPLICATION-1 | 74.12-82.16 | 8.04s | (unchanged from v3) |
| 4 | COMPLICATION-2 | 82.58-97.54 | 14.96s | (unchanged from v3) |
| 5 | REINFORCE | 98.04-104.78 | 6.74s | (unchanged from v3) |
| 6 | **FIX (new)** | 105.04-113.68 | 8.64s | Source audio here is agenda-setting jargon, not used for its words — caption is fully self-authored: "THE FIX: SMALL FOCUSED STEPS - NOT ONE GIANT PROMPT." |
| 7 | CLOSE | 2693.32-2698.30 | 4.98s | (unchanged from v3) |

Total raw 64.42s → 58.7s final after the 1.1x speed-up — close to the 60s Shorts ceiling but under it, accepted per the known preference for authentic length over the tightest possible cut (`feedback_video_duration_target` memory).

## Hook Formula Applied
Unchanged from v3 — see `docs/production/aiwork-v3-prompt-bloat.md` (cold open on presenter, fully self-authored hook question, word-burst captions, progress bar). FIX extends the same "self-authored caption over safe footage" technique to a second clip.

## Value-Adds (Transformative Gate, ADR-0007, min 2 required)
Unchanged from v3: `data_viz_overlay` (400→15 chart, `pipeline/aiwork/make_chart_v3.py`, shown during REINFORCE) and `this_or_that_overlay` ("ONE GIANT PROMPT" vs "SMALL FOCUSED STEPS", shown during COMPLICATION-2). FIX's caption now explicitly pays off the `this_or_that_overlay`'s "SMALL FOCUSED STEPS" side, closing a loop v3 left open (v3 showed the comparison but never said which side won).

## Transformative Gate, item 3 note
Cut duration 64.42s raw (58.7s final) / 2706.0s source = 2.4%, well under the 50% ceiling. Every individual piece is <15s (COMPLICATION-2 longest at 14.96s, FIX at 8.64s).

## Known Issues (corrections made during this production)
1. Carried over from v3 (still true): this source has no tight/close presenter shot at all — one fixed wide camera angle for the entire 45 minutes, mitigated with the same constant crop.
2. **No footage anywhere states the resolution in non-jargon words** — checked exhaustively (t=105-145s immediately following REINFORCE, and t=2670-2685s the closing recap slide) before deciding to caption FIX entirely in the team's own words rather than the source's. This is now the second clip (after HOOK) in this project whose caption fully diverges from its underlying audio — see Hook Retro.

## What To Check At 48h
- N/A — not yet uploaded. Fill in after Stage 6.
- Whether the added resolution beat (FIX) measurably improves retention through the back half of the video compared to what v3 would have shown, if v3 had been uploaded (it will not be — direct A/B isn't possible here, but the retention curve's shape around t≈46-54s is the thing to inspect).
- Whether two clips with fully self-authored, audio-divergent captions (HOOK and FIX) in one video reads as coherent or disjointed to real viewers — still an open, untested pattern per v3's Hook Retro.
- Whether landing at 58.7s (closer to the 60s ceiling than any prior aiwork video) shows any duration-related retention effect.

## Post-Production Retro

### Hook Retro (bắt buộc, mọi video, proactive)
- **Verbal**: found something worth recording, promoted to a note (not yet a rule). This production extends v3's "fully self-authored, audio-divergent caption" pattern from one clip (HOOK) to two (HOOK and FIX). Both times, this was forced by the source lacking any footage carrying the needed meaning in non-jargon words, not a stylistic choice made freely. Worth flagging because it's now happened twice in one project — if it recurs on a third source, that would cross the line from "one-off workaround" to "this niche's real working pattern for jargon-heavy sources," at which point a WORKFLOW.md rule would be warranted. Not promoted yet — still only 2 data points from 1 source, and no metrics exist yet to confirm the pattern even works with real viewers.
- **Visual**: nothing new. FIX reuses the same crop/frame composition already established and reviewed in v3 (no new visual pattern introduced).
