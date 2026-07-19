# aiwork_v1_capability_curve, "AI Coding Jumped From 62% to 88% in ONE Year"

## Status
| Field | Value |
|-------|-------|
| YouTube Video ID | Not yet uploaded, manual upload pending (no upload automation exists in this repo, per AGENTS.md) |
| Rendered | 2026-07-10 |
| Metrics fetch after (48h rule) | 48h after upload timestamp (pending video ID to compute exact time) |
| Metrics status | Not yet fetched, too early |

## Video Specs
- Duration: 46.0s
- Resolution: 1080x1920 (9:16 portrait)
- Codec: H.264 (libx264, crf 18/20), 30fps
- Audio: AAC, 192kbps, 48kHz, stereo (mixed: original source audio + TTS commentary, see ADR-0021)
- File: `output/projects/aiwork/final/2026-07-10-capability_curve_v1.mp4` (10.5MB)
- Render script: `pipeline/aiwork/render_aiwork_v1.py`

## YouTube Title
AI Coding Jumped From 62% to 88% in ONE Year (Real Benchmark)

## YouTube Description
See `output/projects/aiwork/final/2026-07-10-capability_curve_v1.txt` (credits the source channel per ADR-0021's brand-sensitivity mitigation).

## Source
- Channel: Claude (Anthropic's own official YouTube channel)
- Source video ID: `tP4MGcJ80Y0`, "The capability curve", presented by Alex Albert, 905.0s (~15:05), max available quality confirmed (1080p is the ceiling, no 4K exists for this source)
- Footage used: abs t=236.0-282.0s (46.0s), i.e. 5.1% of a 905.0s source, well under the ADR-0007 50% ceiling
- First video for the AI-education niche (ADR-0020), and the first to exercise ADR-0021's per-video Clip Curation Edit override + TTS commentary layer
- Part of the confirmed multi-niche AB-testing strategy (ADR-0019/0020), AI-education/English vertical, run in parallel with the finance/English and health/Vietnamese verticals

## Why This Segment
The source's own on-screen slide with the raw benchmark numbers (62.3% → 87.6%, SWE-bench Verified) sits at abs t≈213-235s, just before this chosen span. The originally-considered start point, t=234.9 (chosen from a real audio pause in the transcript), failed Stage 0 Hook Gate item 1 on frame inspection: the camera was still on a faceless chart-closeup shot there, with the crossfade to the presenter's wide shot only completing at ~236.0. Moved `SRC_START` to 236.0 to open on a clear human presenter (ADR-0017).

The resulting span is a complete, self-contained arc: the reveal payoff ("that's an over 25% jump... Opus 4.7 is more than 3x as likely to succeed on those difficult PRs Sonnet 3.7 was failing on a year ago") followed by the live-demo setup ("we're going to compare Sonnet 4 to Opus 4.7... same task, 12 months apart"). Because the chosen span's own audio only ever references the benchmark numbers abstractly ("an over 25% jump", "3x as likely") and never restates 62.3%/87.6% directly, the data-viz chart (built from the real numbers on Alex Albert's own slide, not a screenshot of it) is what actually shows the reader the underlying stat, never fabricated, transcribed directly off the source's own on-screen slide.

## Hook Formula Applied
- **Cold open on a human face, no title card**, verified via iterative frame extraction at 234.7/234.9/235.0/235.2/235.4/235.6/235.8/236.0s on the raw source (ADR-0017); `SRC_START=236.0` is the first frame where the crossfade to the presenter's wide shot is complete.
- **TTS commentary co-plays t=0-1.999s** ("Straight from Anthropic's own stage."), satisfies ADR-0007 gate item 1 as a genuinely spoken commentary track (not just text), ducked under the original audio via a gain envelope rather than muting it (ADR-0021's mixing pattern).
- **Word-burst hook captions t=0-4.44s** (ADR-0018): 2 bursts ("THAT'S AN OVER 25% JUMP", yellow-emphasized, then "IN JUST OVER A YEAR."), timestamps taken from the source's own real mlx_whisper word-level output, not an invented cadence constant.
- **Chart overlay visible from frame 0** (`CHART_START=0.0`), the actual 62.3%→87.6% SWE-bench Verified curve, giving simultaneous visual proof of the spoken claim rather than narration alone (ADR-0018 "show, don't just tell").
- **Fact-check callout** ("SWE-BENCH VERIFIED, REAL GITHUB CODING TASKS", t=0-8s), names the benchmark, since the source itself names it before our chosen span starts (t=213-217s, outside `SRC_START`/`SRC_END`).
- **Continuous motion**, `zoompan` push-in on the base plate (ADR-0016/0018 cadence); this is already-edited conference footage (unlike bacsihai's static livestream camera), so the crop/zoom is on top of existing camera cuts.
- **Body captions tightened to ~1.5-3s blocks** (ADR-0018), aligned to the source's real sentence/word boundaries.

## Value-Adds (Transformative Gate, ADR-0007, min 2 required)
1. **data_viz_overlay**, the capability-curve chart (`pipeline/aiwork/make_chart.py`), styled in the channel's own indigo palette rather than reproducing the source slide's look, visible t=0-15.5s.
2. **fact_check_callout**, "SWE-BENCH VERIFIED, REAL GITHUB CODING TASKS", t=0-8s.

Commentary track: TTS voiceover ("Straight from Anthropic's own stage.") plus captions throughout satisfy gate item 1 more literally than text-overlay alone (ADR-0021).

## Known Issues (bugs found and fixed during this production)
1. **ffmpeg drawtext "Stray %" silent-drop bug**, captions containing a literal `%` (e.g. "25%") were silently dropped from the render entirely under drawtext's default `expansion=normal` parsing; ffmpeg exits 0 with no visible top-level error, only a buried "Stray %" warning in stderr. Root-caused via isolated single-filter test renders. Fixed by adding `expansion=none` to every `drawtext` call, `%%`-escaping did **not** reliably fix it in testing. Now recorded in AGENTS.md Known Pitfalls (see Workflow Delta below).
2. **Missing glyph ("tofu") bug**, the HOOK headline originally used a Unicode arrow (`→`); neither `Helvetica.ttc` nor `HelveticaNeue.ttc` (the only fonts used across this repo's render scripts) include that glyph, so it rendered as a missing-glyph box. Fixed by using ASCII `->` instead. Now recorded in AGENTS.md Known Pitfalls.
3. **Self-caught design correction, not a bug**: the originally-chosen `SRC_START=234.9` (picked from a real audio pause) failed Hook Gate item 1 on frame inspection, see "Why This Segment" above.

## What To Check At 48h
- Retention-graph shape specifically in the 0-2s TTS-commentary window, does the ~2s generic framing line before the source's own hook payoff ("That's an over 25% jump...") cost early retention? This is the single biggest open question about this video's hook design (see Hook Retro below).
- Stayed to Watch / AVD vs. the existing benchmarks in `docs/experiments/EXPERIMENT-LOG.md` (Dangote 51.6% GOOD, bacsihai v4 8.6% BAD, hardknocks_v1 / bacsihai_v5 pending)
- Whether the professional, no-hype tone (vs. the more emotionally-charged finance/health niches) reads as flat or as credible in comments/retention
- Whether reusing Anthropic's own official-channel footage draws any visible brand-relationship reaction, the open risk ADR-0021 flagged
- Whether the TTS commentary (macOS `say`, Samantha voice) reads as acceptably professional or noticeably robotic against real recorded speech in the same clip

## Post-Production Retro

### Hook Retro (bắt buộc, mọi video, proactive)
- **Verbal**: found something. The TTS commentary line ("Straight from Anthropic's own stage.") is a generic authenticity-framing line, not itself a hook payload, it plays first and delays the source's own actual hook line ("That's an over 25% jump...") by ~2s. Since the Hook Gate requires the hook to land in 0-2s, and this source's own opening line is already a strong Money+Number hook on its own, prepending TTS commentary here works against the hook rather than for it. This generalizes to any future Clip Curation Edit using ADR-0021's TTS-commentary pattern specifically, not to Stage 0's universal checklist, since most video types carry no TTS commentary layer at all, so it's added as an addendum to ADR-0021 rather than to `docs/WORKFLOW.md` (see Workflow Delta below).
- **Visual**: none found beyond what's already applied. Frame 0 shows the presenter clearly (Hook Gate item 1 satisfied), and the chart is visible from t=0, giving simultaneous visual proof of the spoken claim (ADR-0018 "show, don't just tell"). A future idea, not promoted to a rule: an animated draw-on reveal of the chart line instead of a static overlay might read as more dynamic.

### Workflow Delta (bắt buộc, mọi video, reactive)
Yes, this production hit cases not previously covered:
1. ffmpeg drawtext's default `expansion=normal` mode silently drops caption text containing a literal `%`, a one-off engineering incident, not a production-strategy rule → logged as an AGENTS.md Known Pitfalls entry.
2. `Helvetica.ttc`/`HelveticaNeue.ttc` lack the Unicode arrow glyph (`→`), a one-off engineering incident → logged as a second AGENTS.md Known Pitfalls entry.
3. ADR-0021 stated `pipeline/tools/tts_commentary_aiwork.py` as a reusable TTS-generation script, but v1's commentary was actually generated via ad-hoc `say`/mlx_whisper commands with no script saved, a process gap (the file was already decided in the ADR, just never built) → fixed directly: created `pipeline/tools/tts_commentary_aiwork.py` now, tested end-to-end, so the ADR's claim holds for the next video reusing this pattern.
4. The Hook Retro finding above (TTS preamble delaying the source's own hook line) is new guidance for ADR-0021's pattern specifically → added as an addendum to ADR-0021's Decision section.
