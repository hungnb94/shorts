# bacsihai_v6_vitamin_d_hormone — "Vitamin D Không Phải Là 'Vitamin'?"

## Status
| Field | Value |
|-------|-------|
| YouTube Video ID | Not yet uploaded |
| Rendered | 2026-07-11 |
| Metrics fetch after (48h rule) | N/A — compute once uploaded (`/log-video`) |
| Metrics status | Not applicable — not uploaded |

## Video Specs
- Duration: 43.0s
- Resolution: 1080x1920 (9:16 portrait)
- Codec: H.264 (libx264, crf 18/20), AAC 192kbps 48kHz stereo
- File: `output/projects/bacsihai/final/vitamin_d_hormone_v6.mp4` (14.1MB)
- Render script: `pipeline/bacsihai/render_bacsihai_v6.py`

## YouTube Title
Vitamin D Không Phải Là "Vitamin"? Sự Thật Rất Ít Người Biết

## YouTube Description
See `output/projects/bacsihai/final/vitamin_d_hormone_v6.txt` (Vietnamese, hashtags at end).

## Source
- Channel: Bác sĩ Hải (same Source Channel as `pipeline/bacsihai/` v1-v5, ADR-0019)
- Source video ID: `tsDZZNcUEHs` — "Vitamin D - Hormone Quan Trọng Mà Rất Nhiều Người Đang Thiếu", uploaded 2026-07-03, 577.0s (~9.6 min), a produced/edited video (not a raw livestream like v5's source) with dense burned-in Vietnamese captions and professional 3D medical-animation graphics throughout
- Footage used: 2 pieces totaling 47.26s raw (43.0s after the 1.1x speed-up) = 8.2% of the 577.0s source, well under the ADR-0007 50% ceiling
- User-supplied entry point for this production: `https://www.youtube.com/watch?v=tsDZZNcUEHs`, combined per explicit user instruction with the findings of `docs/research/800m-view-case-study-2026-07-11/REPORT.md` (the "808M views, others-vs-the-best" case study)

## Why This Segment
**Sub-format: Multi-Clip Mashup (ADR-0022)**, 2 pieces, 1 hard cut:
- Piece A: abs 30.24-35.08s (4.84s) — "Trước hết ta cần gọi đúng tên. Đầu tiên vitamin D thì không thực sự là vitamin."
- Piece B: abs 44.72-87.14s (42.42s) — the Calcitriol/hormone reveal through the classical-role (canxi/xương) teaser

The cut skips abs 35.08-44.72 (9.64s), a tangent defining what "vitamin" normally means. Skipping it pulls the actual reveal line ("Cancitriol thực chất là một loại hóc môn") forward to clip-relative t≈8.3s — inside Stage 0 item 4's ~5-10s payoff-timing target. Without the cut, the same reveal would land at clip t≈21.8s, well past the "not buried past ~15s" ceiling.

**Frame-0 check (ADR-0017)**: clip starts exactly at the word boundary for "Trước" (abs 30.24s per mlx_whisper word timestamps). The source uses a brief warm-toned flash-transition effect at this exact cut point (abs ~30.0-30.3s); verified via frame extraction at 0.05s resolution that by abs 30.24-30.25s the face is already clearly legible (glasses, eyes, mouth mid-speech), not a full white-out — passes the check with a small margin, not with certainty-to-the-frame the way a mid-shot moment would. Frames at abs 30.1-30.2s (fully white-out) were explicitly avoided.

**Transformative Gate item 3 note (flagged, not silently resolved)**: Piece B (42.42s) exceeds the "<15s per clip" rule (ADR-0007 item 3 / ADR-0022 item 2) that Multi-Clip Mashup pieces are normally held to. It is treated here as exempt because it is a single continuous take with no internal skip — the same interpretive logic `bacsihai-v5-lao-dong-tay.md` used to exempt Contiguous VO's single 52.64s segment from the same rule. This is a **new** extension of that precedent, not a repeat of it: v5's exemption applied to a video that was *entirely* one Contiguous VO segment; this video mixes a normal (<15s) piece (A) with one long continuous piece (B) inside a Multi-Clip Mashup. `pipeline/aiwork/render_aiwork_v2.py` — the only prior Multi-Clip Mashup production — instead kept *every* piece under 15s (10 pieces, longest 14.86s), so it does not establish this precedent either. Proposed resolution: an ADR-0022 addendum stating that a Multi-Clip Mashup piece may exceed 15s when it is itself a single, uncut, continuous take (i.e., the same underlying justification ADR-0013 already uses), and that the ceiling is meant to bound artificially-trimmed/discontiguous pieces, not naturally long single takes used whole. Not yet written as a formal ADR edit — flagged here per the Workflow Delta process below for the next reactive check.

**Total duration**: 47.26s raw / 43.0s final (after 1.1x speed-up) — the 45-60s ADR-0013/0022 window applies to the raw pre-speed-up segment-selection duration, matching the precedent set by `aiwork-v2-capability-curve.md` (50.74s raw / 46.2s final), not the final output number.

## Hook Formula Applied
- **Contrarian-Reveal hook**, verbatim from the source's own script: "Trước hết ta cần gọi đúng tên. Đầu tiên vitamin D thì không thực sự là vitamin." (First, we need to call it by its correct name. Vitamin D isn't actually a vitamin.) — opens a clean gap at t=0 (what IS it, then?) without naming the answer.
- **Implied-Comparison hook pattern** (new this video, sourced from `docs/research/800m-view-case-study-2026-07-11/REPORT.md`, the 808M-view "others vs the best" case study): the source's own VO states the comparison verbatim — "không chỉ liên quan đến vấn đề xương như nhiều người vẫn nghĩ" (not just about bones, like most people think) — reinforced here with a 2-card this_or_that overlay ("NHIỀU NGƯỜI NGHĨ: CHỈ LÀ XƯƠNG" → "SỰ THẬT: MIỄN DỊCH - NÃO BỘ - CẢ CƠ THỂ") timed exactly to that line (clip t≈21.0-29.1s). This is the video's first deliberate use of this pattern; see Hook Retro below for whether it generalizes.
- **Payoff-timing**: reveal ("Cancitriol thực chất là một loại hóc môn") lands at clip t≈8.3s, inside the ~5-10s target.
- **Cause+effect co-naming check**: passes — the hook line names neither a specific cause nor a specific disease/effect (contrast with the v5 pitfall), only "it's not what you think it is."
- **Cadence**: no added zoompan/motion — the source's own alternation between talking-head and 3D-animation graphics (roughly every 2-5s throughout the selected span) already satisfies the 2-Second Rule (ADR-0016) natively; verified by direct frame extraction at 1-2s intervals through the whole clip, not assumed.
- **Caption-sync**: the source has its own burned-in, professionally-timed Vietnamese captions throughout (unlike v5's raw livestream source, which had none) — no added body captions were burned in on top; see technical note below on why.

## Value-Adds (Transformative Gate, ADR-0007 — min 2 required)
1. **this_or_that / data_viz_overlay** — the 2-card Implied-Comparison sequence described above (clip t≈21.0-29.1s).
2. **animated_annotation** — emoji keyed to timestamp windows (not caption-text matching, since there is no added BODY_SUBS list this time): 🚫 (`1f6ab`) on "không thực sự"/"không chỉ" negation moments (reinforcing the contrarian-reveal framing), 🧠 (`1f9e0`) on "hóc môn"/"tín hiệu"/"cơ quan" mentions (signal/control concept).

Commentary track (gate item 1): added title-framing text "SỰ THẬT VỀ VITAMIN D" (t=0-3s) + CTA "THEO DÕI ĐỂ HIỂU ĐÚNG VỀ SỨC KHỎE" (last 4s of the clip) — the source's own captions are transcription, not commentary, so they don't satisfy this item on their own.

## Technical note: blur-fill pillarbox instead of center-crop (new this video)
v1-v5/giannis/hardknocks all convert 16:9 source to 9:16 via a tight center-crop (`scale=-2:1920,crop=1080:1920:(in_w-1080)/2:0` or equivalent), which keeps only the central ~31.6% of the original frame width. That is fine when the source is an uncaptioned talking-head/livestream shot with the subject centered, but this source has burned-in captions spanning most of the 1920px frame width — the same crop would clip caption text on both edges. Used a blur-fill pillarbox instead (`pipeline/bacsihai/render_bacsihai_v6.py`'s `VF_PILLARBOX`): the full uncropped 1080-wide video centered over a blurred, cropped full-bleed copy of itself, preserving 100% of caption legibility. `pipeline/aiwork/render_aiwork_v2.py`'s `GRAPHIC_VF` (`scale=1080:-2,pad=1080:1920:0:(1920-ih)/2:black`) is the closest existing precedent but pads with plain black rather than a blurred fill, and was only applied to occasional graphic inserts there, not the whole video.

## Known Issues
- The Piece B / 15s-per-clip exemption above is an interpretive call, not yet ratified by an ADR edit — see Why This Segment.
- Pause-trimming (Retention Technique, AGENTS.md) was evaluated and skipped: word-gap analysis of the selected span (mlx_whisper word timestamps) found ~0 measurable natural inter-word pauses in this speaker's delivery — nothing to trim. The 1.1x speed-up was still applied as a separate, independent Retention Technique.
- `mlx_whisper` transcription required the repo's `.venv` interpreter (`.venv/bin/python3`), not the system `python3` — the latter lacks the `mlx_whisper` module. First hit this session; worth a Known Pitfalls entry if it recurs.

## What To Check At 48h (once uploaded)
- Retention-graph shape in the first ~10s specifically — does the reveal landing at t≈8.3s (vs. v5's failed ~33s-buried payoff) correlate with materially better Stayed-to-Watch, as the Stage 0 item 4 rule predicts?
- Whether the Implied-Comparison card (clip t≈21-29s) correlates with a retention plateau/bump at that point, as a first data point on whether this new hook-pattern element (from the 800M-view case study) transfers to the health/Vietnamese niche — the case study itself flagged this as an untested hypothesis for a *different* niche (AI-education), so this is actually the first real test of it, in a third niche.
- Whether reusing a Source Channel's own burned-in captions (instead of adding new ones) reads as sufficiently transformative/distinct on comments, given the Transformative Gate's spirit (not just its 3 literal rules).
- Comment themes — this is a factual/educational reveal (vitamin D = hormone), watch for medical-skepticism/fact-check pushback vs. the "TIL" surprise-and-share pattern.

## Post-Production Retro

### Hook Retro (bắt buộc, mọi video — proactive)
- **Verbal**: none found — the source's own "Trước hết ta cần gọi đúng tên" / "không thực sự là vitamin" line is already a clean, complete Contrarian-Reveal opener; rewriting it would only weaken the authenticity of reusing the source's actual words.
- **Visual**: one idea not applied here — the source's own "MỘT 'VITAMIN'" title-card graphic (abs ~32-35s, inside Piece A) could have been suppressed/replaced with a continued talking-head shot via a Contiguous-VO-style crop-position switch (the `render_aiwork_v2.py` ADR-0022 addendum technique: vary a crop-window `x` offset over time instead of cutting, to avoid ever showing a graphic-only frame during the hook's first ~5s). Not applied this time because the source's own graphic is well-produced and arguably *helps* legibility of the reveal (viewers read "MỘT 'VITAMIN'" text while hearing the same words) — flagged as a hypothesis for a future video with a similar "source cuts to its own graphic mid-hook" situation, to A/B against.
- Did not run the `viral-video-analysis` skill against a second external video for this Retro (the 800M-view case study was already applied at the *design* stage, not as a post-hoc comparison) — if this video underperforms, running that skill against 1-2 more Vietnamese-health-niche viral videos specifically (not just the English/firearms case study already used) is the natural next step.
- Generalizable finding written into `docs/WORKFLOW.md`: none added yet — see Workflow Delta below for why the blur-fill-pillarbox and Piece-B-exemption findings are being routed to ADR edits instead of a Stage 0/WORKFLOW.md change.

### Workflow Delta (bắt buộc, mọi video — reactive)
Hit two cases WORKFLOW.md/ADRs don't clearly cover:
1. **Multi-Clip Mashup with one piece >15s** (a single continuous take, no internal skip) — this is a genuine new-rule case, not just an ordering gap. Action: propose an ADR-0022 addendum (see Why This Segment above) rather than editing WORKFLOW.md directly, since it's a clarification of an existing ADR's scope, matching how the aiwork-v2 addendum was handled. Not yet written as a formal diff to `docs/adr/0022-multi-clip-mashup-pipeline.md` — flagged here for a follow-up pass; this production doc is the source citation for that future edit.
2. **Source has its own burned-in captions spanning most of frame width** — this is also a new case (v1-v5/giannis/hardknocks sources never had this). Action: the blur-fill-pillarbox technique is documented in this doc's Technical Note; if a second video hits the same situation, generalize it into a citable ADR or a WORKFLOW.md Stage 2/3 note rather than re-deriving it from scratch each time.
Both are logged here rather than immediately edited into ADR/WORKFLOW.md files, since a single data point (one video) is a thinner basis than the multi-video pattern-confirmation this repo's other ADRs are usually backed by — revisit and formalize after the next 1-2 productions confirm the pattern holds.
