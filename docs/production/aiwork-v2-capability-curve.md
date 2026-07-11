# aiwork_v2_capability_curve, "AI Coding Jumped From 62% to 88% in ONE Year" (Multi-Clip Mashup rebuild)

## Status
| Field | Value |
|-------|-------|
| YouTube Video ID | [Mw7jeR6R6iE](https://youtube.com/shorts/Mw7jeR6R6iE) |
| Rendered | 2026-07-11 |
| Uploaded | 2026-07-11 |
| Metrics fetch after (48h rule) | 2026-07-13 07:34 +07 |
| Metrics status | Not yet fetched, too early |

## Video Specs
- Duration: 46.2s
- Resolution: 1080x1920 (9:16 portrait)
- Codec: H.264 (libx264, crf 18/20), ~33fps (30fps source sped up 1.1x via `setpts`)
- Audio: AAC, 192kbps, 48kHz, stereo (single source-audio track, no TTS — see Why This Segment)
- File: `output/projects/aiwork/final/2026-07-11-capability_curve_v2.mp4` (9.9MB)
- Render script: `pipeline/aiwork/render_aiwork_v2.py`

## YouTube Title
AI Coding Jumped From 62% to 88% in ONE Year (Real Benchmark)

## YouTube Description
See `output/projects/aiwork/final/2026-07-11-capability_curve_v2.txt` (credits the source channel per ADR-0021's brand-sensitivity mitigation, still applicable — same source footage).

## Source
- Channel: Claude (Anthropic's own official YouTube channel)
- Source video ID: `tP4MGcJ80Y0`, "The capability curve", presented by Alex Albert, 905.0s (~15:05), max available quality confirmed (1080p is the ceiling, no 4K exists for this source)
- Footage used: 10 independently-extracted pieces totaling 50.74s raw (46.2s after the 1.1x speed-up), 5.6% of the 905.0s source, well under the ADR-0007 50% ceiling
- Rebuild of `pipeline/aiwork/render_aiwork_v1.py` (`docs/production/aiwork-v1-capability-curve.md`), which stays on disk untouched as the known-issues record; v1 was rendered but never uploaded

## Why This Segment
v1 used one contiguous 46s block (abs 236.0-282.0s) plus a TTS commentary preamble. The user flagged two problems directly after reviewing it: the TTS preamble ("Straight from Anthropic's own stage.") delayed the source's own strong hook line past the Hook Gate's 0-2s window (exactly what v1's own Post-Production Retro had self-diagnosed), and the edit should cut together multiple parts of the 905s source rather than staying inside one 45-60s window. A grilling session (`/grill-with-docs`) confirmed: build a genuinely new version (not an overwrite), use a **true Multi-Clip Mashup** (ADR-0022, new this session — formalizes what `render_hardknocks_v1.py` was already doing undocumented), drop TTS entirely (captions alone satisfy ADR-0007 gate item 1), hard-cut every boundary (no crossfade/sound-design/zoompan — dropped for this video by explicit user decision), and add a new pause-trimming + 1.1x speed-up Retention Technique (AGENTS.md) applied as the final pass.

Five macro-clips were researched directly against the real transcript (word-level timestamps) and verified with frame extraction, not guessed:

| # | Role | Range | Raw dur | Quote |
|---|------|-------|---------|-------|
| 1 | HOOK | 186.62-193.58 | 6.96s | "Raise your hand if you feel like Claude has allowed you to go 10 times faster than what you were doing a year ago." |
| 2 | STATS | 224.22-234.58 | 9.78s (2 pieces) | "...Sonnet 3.7, it scored 62%... Today, with Opus 4.7, it scores 87%." |
| 3 | ELAB | 236.06-250.92 | 14.86s | "That's an over 25% jump in just over a year... more than three times as likely to succeed..." |
| 4 | DEMO | 257.02-271.70 | 12.44s (4 pieces) | "...a quick demo... comparing Sonnet 4 to Opus 4.7." |
| 5 | CLOSE | 367.72-374.42 | 6.70s (2 pieces) | "...a better output... less lines of code... more efficient as well." |

This replaces v1's SRC_START entirely — the video now opens on the rhetorical hook question rather than the numbers, with the numbers themselves landing as the payoff in STATS (global t=6.96s), comfortably inside the payoff-timing window ADR-0017 expects. STATS and DEMO are each further split at natural pause points found by analyzing the real inter-word gap distribution (gap > 0.35s), CLOSE is split at a clean word-end boundary (see Known Issues for why "clean boundary" mattered), and ELAB/HOOK stay single pieces. All 10 pieces are <15s (ADR-0007 item 3; ELAB is the longest at 14.86s).

**Avoid-zones respected**: the faceless chart-closeup crossfade between STATS and ELAB (abs 234.9-236.0s, the exact span v1's SRC_START correction was about) falls in the untouched gap between clips. The technical-difficulties dead air (abs 280.48-285.72s) is well clear of DEMO's end.

**Considered and rejected**: abs t=213.58-222.58s, where the presenter names "SWE-bench Verified" (mis-transcribed by whisper as "Sweet Bench Verified"). Not included as a 6th clip — the fact_check_callout value-add already names the benchmark without adding 9s of runtime.

## Hook Formula Applied
- **Cold open on a tight portrait shot** (abs t=186.62), plain background, presenter's face filling most of the frame, mouth mid-speech — passes Hook Gate item 1 (ADR-0017) more strongly than v1's wide establishing shot (see Hook Retro).
- **Rhetorical-question hook, not a number**: "Raise your hand if you feel like Claude has allowed you to go 10 times faster..." opens a genuine gap (is this true? how much, really?) that only resolves at STATS's real numbers (t=6.96s) — inside the Hook Gate's payoff-timing window (ADR-0017), so the qualitative-claim caveat in AGENTS.md's Known Pitfalls doesn't apply here the way it did to bacsihai v5 (see Hook Retro).
- **Word-burst hook captions t=0-6.96s** (ADR-0018), 4 bursts, timestamps taken directly from the source's own mlx_whisper word-level output, one keyword ("10X") emphasized in yellow.
- **Mid-clip shot change handled without an audio cut**: the source itself cuts from the tight portrait shot to the wide stage shot mid-word (inside "than", ~191.85s of the source). Rather than splitting this into two concat pieces (which would guillotine that word), HOOK stays one continuous extract with a time-varying crop x-offset (`crop`'s own `t` variable, confirmed relative to the piece's own start) — full audio continuity preserved (see Known Issues).
- **Body captions in short 1.4-2.4s bursts** (ADR-0018) for every other piece, aligned to real word/sentence boundaries.
- **Progress bar** (bottom edge, hardknocks-style) spanning the full assembled timeline, giving the viewer a sense of progress across the discontinuous multi-clip edit.

## Value-Adds (Transformative Gate, ADR-0007, min 2 required)
1. **data_viz_overlay**, the capability-curve chart (`pipeline/aiwork/make_chart.py`, reused as-is from v1), now shown during **ELAB** (global t≈17.0-27.5s) rather than at t=0 — repositioned because STATS's own base footage turned out to already be a full-screen shot of the source's real chart (see Known Issues), so overlaying our custom chart there would have shown the same data twice back to back. ELAB is the clip that discusses the jump in words ("an over 25% jump", "3x as likely") without any chart on screen, making it a better fit for "show, don't just tell" (ADR-0018).
2. **fact_check_callout**, "SWE-BENCH VERIFIED - REAL GITHUB CODING TASKS" (plain hyphen, not em-dash — see Known Issues), also repositioned to ELAB (t≈16.74-24.74s), reinforcing the benchmark name the source's own chart shows in small print during STATS.

Commentary track: captions alone (no TTS this time) satisfy ADR-0007 gate item 1, per the user's explicit decision to drop TTS entirely.

## Transformative Gate, item 3 note
Cut duration 50.74s raw (46.2s final) / 905.0s source = 5.6%, well under the 50% ceiling. Every individual piece is <15s (ELAB longest at 14.86s), satisfying item 3 literally — this video is the first to declare the Multi-Clip Mashup sub-format (ADR-0022) explicitly at build time, unlike `render_hardknocks_v1.py`'s retroactive classification.

## Known Issues (corrections made during this production)
1. **HOOK's internal shot change lands mid-word, not at a pause**: frame-by-frame verification found the source cuts from the tight portrait shot to the wide stage shot at approximately abs t=191.85s — squarely inside the word "than" (191.42-192.14s per the transcript), not at any silence. A concat-piece split there would have guillotined that word's audio. Fixed by keeping HOOK as one continuous extract with a time-varying `crop` x-offset expression instead of two spliced pieces — full audio continuity, only the visual crop changes. Generalizes beyond this video (see Workflow Delta).
2. **STATS's real content is a full-screen chart, not the presenter+stage shot assumed during planning**: the original plan (informed by a design-pass agent's frame sampling) assumed STATS shared DEMO/ELAB's wide "Code w/ Claude" stage crop. Direct frame extraction during implementation showed STATS is actually a full-screen insert of the source's own real benchmark chart ("Every model moves the ceiling — SWE-bench Verified since Sonnet 3.7"), with no presenter visible at all. A straight 1080-wide crop of that chart would have cut off either the early data points or the 87.6% punchline. Fixed by giving STATS the same scale-to-fit-width + letterbox-pad treatment as CLOSE's graphic half, and by moving the data_viz_overlay/fact_check_callout value-adds to ELAB instead (see Value-Adds above) to avoid showing the same chart twice.
3. **CLOSE's internal split point also needed a word-boundary check**: the visual cut from the graphic card to the Claude-logo bumper falls inside the word "being" (368.98-369.28s). Chose 369.28 (the word's end) as the piece boundary instead of the visually-exact cut point (~369.05-369.1s) — costs at most ~0.2s of the plain-cream bumper shot being rendered with the graphic's letterbox treatment instead of the wide crop, imperceptible given the bumper has almost no content to crop incorrectly.
4. **Em-dash avoided in the fact_check_callout text**: reused v1's exact wording but replaced "—" with a plain "-", per the existing AGENTS.md Known Pitfall about `Helvetica.ttc`/`HelveticaNeue.ttc` missing some Unicode glyphs (that pitfall was found via the arrow character; hadn't been checked against em-dash specifically, so treated it as equally suspect rather than assuming it's fine).
5. **Audio cut-boundary check (`AGENTS.md`'s Hard cut is a known-low-severity risk per ADR-0022) done quantitatively**: since no audio playback tool exists in this repo, ran a waveform-discontinuity check (sample-to-sample delta at each of the 9 concat boundaries vs. a local baseline) instead of a literal listen — all 9 boundaries showed no outlier discontinuity (ratios 0.5-3.6x baseline, well below the >8x threshold that would flag a click).

## What To Check At 48h
- Whether the rhetorical-question hook (no number in the first 6.96s) retains viewers as well as, or better than, a hook that leads with the number directly — this is the single biggest open question about this video's hook design (see Hook Retro).
- Retention-graph shape at each of the 9 hard-cut boundaries specifically, does the multi-clip mashup's lack of crossfade cost retention at any individual cut versus v1's single continuous segment?
- Stayed to Watch / AVD vs. v1 (never uploaded, no data) and the existing benchmarks in `docs/experiments/EXPERIMENT-LOG.md` (Dangote 51.6% GOOD, bacsihai v4 8.6% BAD, hardknocks_v1/bacsihai_v5 pending)
- Whether the 1.1x speed-up (new Retention Technique, first use) reads as natural pacing or as noticeably rushed
- Whether reusing Anthropic's own official-channel footage draws any visible brand-relationship reaction, the open risk ADR-0021 flagged (unchanged from v1)

## Post-Production Retro

### Hook Retro (bắt buộc, mọi video, proactive)
- **Verbal**: found something worth recording, not promoted to a new rule. AGENTS.md's existing Known Pitfall notes "a hook built on a qualitative claim... is inherently weaker than a Money+Number... hook." This video's opening line is exactly that kind of qualitative claim ("10 times faster... a year ago", no number yet stated as fact). It's an intentional, acceptable exception: the real number lands as the payoff at t=6.96s, well inside the Hook Gate's ~5-8s payoff-timing window (ADR-0017 item 4), so the qualitative opener is functioning as the "gap" the Hook Gate wants, not a weakness. Worth noting explicitly since it's easy to over-apply the "always lead with a number" instinct — already covered by existing Hook Gate items 2 (gap-not-resolved) and 4 (payoff-timing), so no new checklist item needed.
- **Visual**: found something, promoted to a rule. Frame 0 here is a tight portrait shot (plain background, face filling most of the frame) rather than v1's wide establishing shot — a visibly stronger Hook Gate item-1 pass (bigger, clearer face, more immediately legible as "a person is about to say something to you" than a small figure on a stage). This generalizes: added a preference note to Stage 0 item 1 in `docs/WORKFLOW.md`, citing this video.

### Workflow Delta (bắt buộc, mọi video, reactive)
Yes, this production hit one case not previously covered:
1. ADR-0022's item 3 ("each individual clip may itself be further split at internal pause points... these sub-cuts follow the same hard-cut rule") assumed internal splits always land at a pause/silence. HOOK's internal shot change instead lands mid-word, and CLOSE's lands at a word boundary that's close-but-not-exact to the true visual cut point. This is a genuinely new, reusable technique (time-varying filter parameter within a single continuous extract, instead of forcing a concat-piece split) that the ADR's own rule doesn't cover as written → added as an addendum to ADR-0022's Decision section (not a new ADR, since it's a direct clarification of an existing rule this ADR already governs).
2. The STATS visual-treatment correction (Known Issue #2) was caught by this video's own frame-extraction discipline (Stage 2/Stage 0's existing "verify visually, don't guess" norm), not by a gap in `docs/WORKFLOW.md` itself — no workflow change needed for that one, logged as a Known Issue only.
