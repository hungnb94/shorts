# bacsihai_v5_lao_dong_tay — "Vì Sao Người Lao Động Chân Tay Ít Bị Alzheimer Hơn?"

## Status
| Field | Value |
|-------|-------|
| YouTube Video ID | Not yet uploaded (manual upload — no Chrome uploader automation exists) |
| Rendered | 2026-07-10 |
| Metrics fetch after (48h rule) | 48h after manual upload, whenever that happens |
| Metrics status | N/A — not uploaded yet |

## Video Specs
- Duration: 52.6s
- Resolution: 1080x1920 (9:16 portrait)
- Codec: H.264 (libx264, crf 18/20), 30fps
- Audio: AAC, 192kbps, 48kHz, stereo
- File: `output/projects/bacsihai/final/lao_dong_tay_v5.mp4` (18.7MB)
- Render script: `pipeline/bacsihai/render_bacsihai_v5.py`

## YouTube Title
Vì Sao Người Lao Động Chân Tay Ít Bị Alzheimer Hơn?

## YouTube Description
See `output/projects/bacsihai/final/lao_dong_tay_v5.txt` (Vietnamese, hashtags at end).

## Source
- Channel: Bác sĩ Hải (same channel as `pipeline/bacsihai/` v1-v4)
- Source video ID: `AGBrXy-2SxI` — livestream "Bí quyết sống thọ của ông bà xưa", uploaded 2026-07-10, 4137.8s (~69 min), `was_live=true`
- Footage used: abs t=314.36-367.00s (52.64s), i.e. 1.27% of a 4137.8s source — well under the ADR-0007 50% ceiling
- This is part of the confirmed multi-niche AB-testing strategy (see `docs/adr/0019-multi-niche-ab-testing.md`) — Vietnamese health/longevity vertical, run in parallel with the English finance vertical

## Why This Segment
The source is a raw livestream with substantial rambling (sound checks, greetings, "comment số 1" engagement bait) in its opening minutes — confirmed the risk flagged in the plan before curation. The chosen segment sits inside the video's "5 pillars of Blue Zone longevity" framing (pillar #1: movement/labor) and is the tightest self-contained arc found: setup ("people back then 'moved' through manual labor, not exercise") → clarification (must be literal hand labor, not "mental labor") → payoff (manual laborers have a much lower rate of Parkinson's/Alzheimer's than desk workers). Complete arc, no mid-sentence cut, 52.64s fits the ADR-0013 45-60s window.

**Source gives no percentage** — Bác sĩ Hải says "thấp hơn rất nhiều" (qualitative), not a number. The data-viz overlay below deliberately states the claim qualitatively rather than inventing a stat.

## Hook Formula Applied
- **Cold open on face, no title card** — verified via frame extraction at t=0/t=0.5s/t=2s on the raw source AND re-verified on the final rendered output (ADR-0017). Livestream camera is on the host's face essentially continuously — unlike v4's failure (a static title-card graphic), this source made the face-gate easy to satisfy; the harder constraint was finding a *coherent* 45-60s block (see above).
- **Word-burst hook captions, t=0-6s** (ADR-0018) — 5 bursts, cadence ~0.7-1.3s, timestamps taken directly from this video's own mlx_whisper word-level output (language="vi") rather than the English-benchmark constant ADR-0018 warns against reusing. One keyword per relevant burst emphasized in yellow ("VẬN ĐỘNG", "LAO ĐỘNG").
- **Continuous motion** — `zoompan` (ported from `render_hardknocks_v1.py`) applied to the base plate, since this is a static-camera livestream shot (v4's base plate had no motion at all).
- **Body captions tightened to ~4-5s blocks** (v4 used ~8-9s blocks) — aligned to the source's real sentence boundaries.

## Value-Adds (Transformative Gate, ADR-0007 — min 2 required)
1. **animated_annotation** — emoji overlays keyed to caption keywords: 💪 (`1f4aa`) on "tay"/"vận động"/"lao động" mentions, 🧠 (`1f9e0`) on "parkinson"/"alzheimer"/"trí óc" mentions. (Note: v4's emoji keyword lists were unaccented Latin substrings matched against accented Vietnamese caption text, which never matches — fixed here by using accented substrings that actually appear in the caption text.)
2. **data_viz_overlay** — qualitative comparison card ("LAO ĐỘNG TAY vs TRÍ ÓC" / "NGUY CƠ PARKINSON & ALZHEIMER THẤP HƠN") shown during the reveal (t=33.3-48.7s). Deliberately qualitative, matching what the source actually claims (no fabricated percentage).

Commentary track: hook-framing text (t=0-6s) + CTA (t=47.6-52.6s) satisfy gate item 1.

## Transformative Gate — item 3 note (flagged, not silently checked off)
ADR-0007 item 3 reads "cut ≤50% of source duration AND each individual clip <15s." The 50% ceiling is trivially satisfied (52.64s / 4137.8s = 1.3%). The "<15s per clip" clause was written with the multi-clip mashup format (e.g. `render_hardknocks_v1.py`'s 6 concatenated clips) in mind; this video is the Contiguous-VO single-segment format (ADR-0013), where the entire video *is* the one segment and is instead bounded by ADR-0013's 45-60s range (52.64s, compliant). This is the same precedent v4's own videos (e.g. `V1_duong_pha_nhi`, 59.5s single clip) were produced under. Worth a future ADR clarification distinguishing the two sub-formats explicitly, but not resolved here.

## Known Issue Noted, Not Fixed Here
`render_hardknocks_v1.py` concatenates 6 non-contiguous clips (with gaps between them, e.g. clip 4 ends at abs 605.3s and clip 5 starts at abs 660.5s) via `concat`, which appears to violate ADR-0013's "MUST be a single, non-split contiguous segment" / "never `concat`" rule. That video is already uploaded (`dHDpDXSIAkA`, metrics pending) — out of scope to fix retroactively here, but flagged since I ported technique from that script and want the inconsistency on record rather than silently reproduced.

## What To Check At 48h (for post-hoc analysis, once uploaded)
- Stayed to Watch / AVD vs. the existing benchmarks in `docs/experiments/EXPERIMENT-LOG.md` (Dangote 51.6% GOOD, bacsihai v4 8.6% BAD, hardknocks_v1 pending)
- Whether the ~4-5s body-caption cadence (vs v4's ~8-9s) actually helps retention through the middle of the video, not just the 0-5s hook window
- Whether Vietnamese-language mlx_whisper transcription (first use in this repo, `whisper-medium-mlx`) produced accurate enough word timestamps — check the rendered captions against the source audio for any diacritic/timing drift
- Comment themes — this is a factual/educational claim (Parkinson's/Alzheimer's + manual labor), watch for medical-skepticism pushback vs. the personal-story admiration pattern seen on the hardknocks upload
