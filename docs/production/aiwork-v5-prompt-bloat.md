# aiwork_v5_prompt_bloat, "Why Adding More Instructions Makes Your AI Worse" (Multi-Clip Mashup)

## Status
| Field | Value |
|-------|-------|
| YouTube Video ID | `jNM7dmy-cFE` |
| Rendered | 2026-07-12 |
| Uploaded | 2026-07-12 22:20 +07 |
| Metrics fetch after (48h rule) | 2026-07-14 22:20 +07 |
| Metrics status | Pending — do not fetch before the date above |
| Studio Analytics | https://studio.youtube.com/video/jNM7dmy-cFE/analytics/tab-overview/period-default |

## Video Specs
- Duration: 58.7s
- Resolution: 1080x1920 (9:16 portrait)
- Codec: H.264 (libx264, crf 18/20), ~33fps (30fps source sped up 1.1x via `setpts`)
- Audio: AAC, 192kbps, 48kHz, stereo (single source-audio track, no TTS)
- File: `output/projects/aiwork/final/2026-07-12-aiwork_v5_prompt_bloat.mp4` (8.8MB)
- Render script: `pipeline/aiwork/render_aiwork_v5.py`

## YouTube Title
Why Adding More Instructions Makes Your AI Worse

## YouTube Description
See `output/projects/aiwork/final/2026-07-12-aiwork_v5_prompt_bloat.txt` (unchanged from v4 — credits the source channel per ADR-0021's brand-sensitivity mitigation).

## Source
Same source and cut as `aiwork_v4` — see `docs/production/aiwork-v4-prompt-bloat.md` and `docs/production/aiwork-v3-prompt-bloat.md` for the grilling-session decisions (footage policy → ADR-0026, audience-fit, sub-format, hook thesis, the FIX-clip resolution beat). **This doc only covers the caption-style change — no content, timing, or cut changed from v4.**

## Why This Change (what changed from v4)

User feedback on v4, verbatim: *"chúng ta nên học cách làm sub giống hardnock vì sub này nhỏ quá và còn tách ra làm mấy câu liên tiếp. ghi luôn 1 lần [hook text]... còn chữ ở dưới cũng có chữ to hơn và highlight các phần quan trọng"* — v4's captions were too small, and the hook question revealed itself across 4 sequential bursts instead of appearing all at once; body captions should be bigger with important words highlighted, matching the style already proven in `render_hardknocks_v3.py`.

Ported directly from `render_hardknocks_v3.py` (its `dialogue_burst_filters` technique, an ADR-0018 addendum — base text + selected keywords rendered bigger and in a highlight color, positioned via Pillow font metrics so mixed sizes/colors on one line share a centered baseline):

1. **HOOK**: same four phrase-groups as v4 ("WHY DOES ADDING MORE" / "INSTRUCTIONS" / "MAKE YOUR AI" / "WORSE?"), but now stacked as 4 lines shown simultaneously for the entire 0-9.12s hook window rather than revealed one at a time — the whole question is visible and legible from frame 0. "WORSE?" keeps its keyword emphasis (62pt vs 44pt base, yellow vs white).
2. **BODY_SUBS**: identical segmentation/timing to v4 (no captions added, removed, or re-timed), but rendered ~1.4-1.8x bigger (40pt base / 50pt keyword, vs v4's flat 28pt) with one key word or short phrase per line marked via `*word*` markup and rendered bigger + yellow (e.g. "IT WORKED *PERFECTLY* AT FIRST.", "NOT ONE *GIANT* PROMPT.").
3. **Background bands replace per-line boxes**: a single translucent `drawbox` band behind the hook zone (top, only during the hook window) and another behind the body-caption zone (bottom, spans the whole video) replace the old per-caption `box=1`. Necessary because a keyword run and its neighboring base-text run are now two separate `drawtext` filters (different fonts/sizes/colors) — giving each its own box left a visible seam between them. This is the exact fix `render_hardknocks_v3.py` already made for the same reason (see its own docstring), reused here rather than re-derived.

Keyword selection per line (one phrase per caption, chosen for "this is the word that carries the beat"):

| Caption | Keyword(s) |
|---|---|
| IT WORKED PERFECTLY AT FIRST. | PERFECTLY |
| SO YOU KEPT ADDING MORE TO IT. / AND MORE. ×2 | MORE |
| UNTIL YOUR INSTRUCTIONS / BECAME HUNDREDS OF LINES LONG. | INSTRUCTIONS / HUNDREDS |
| MORE PIECES. MORE COMPLEXITY. | MORE (×2) |
| AND SUDDENLY IT STARTED / MAKING MISTAKES IT NEVER MADE BEFORE. / SOUND FAMILIAR? | SUDDENLY / MISTAKES / FAMILIAR |
| IT HAPPENS TO EVERYONE - / EVEN THE PEOPLE WHO BUILD THIS STUFF. | EVERYONE / BUILD |
| THE FIX: / SMALL FOCUSED STEPS - / NOT ONE GIANT PROMPT. | FIX / SMALL FOCUSED / GIANT |
| FOLLOW FOR MORE ON USING AI WELL | FOLLOW |

## Hook Formula Applied
Unchanged from v3/v4 in substance (cold open on presenter, fully self-authored hook question, progress bar) — the presentation mechanics changed as described above (all 4 lines simultaneous, keyword line bigger/yellow) but the underlying Hook Gate compliance (frame-0 face, gap-opening question, no cause+effect co-naming) is identical.

## Value-Adds (Transformative Gate, ADR-0007, min 2 required)
Unchanged from v3/v4: `data_viz_overlay` (400→15 chart) and `this_or_that_overlay` ("ONE GIANT PROMPT" vs "SMALL FOCUSED STEPS"). Not touched by this caption-style pass.

## Transformative Gate, item 3 note
Unchanged from v4: 64.42s raw / 2706.0s source = 2.4%, well under the 50% ceiling.

## Known Issues
Carried over from v3/v4 unchanged (no new issues introduced by this pass):
1. This source has no tight/close presenter shot — one fixed wide camera angle for the entire 45 minutes, mitigated with the same constant crop.
2. No footage anywhere states the resolution in non-jargon words (why FIX's caption is self-authored, same as HOOK's).

## What To Check At 48h
- N/A — not yet uploaded. Fill in after Stage 6.
- Whether the bigger/highlighted captions measurably improve retention or completion-rate over what a smaller-caption version would have shown (no direct A/B here since v4 will not be uploaded, but this is the first aiwork video with the hardknocks-style caption treatment — worth comparing against hardknocks' own retention numbers once both have data).
- Whether showing the full hook question at once (vs. progressive reveal) changes average-view-duration in the first 2-3s specifically.

## Post-Production Retro

### Hook Retro (bắt buộc, mọi video, proactive)
- **Verbal**: nothing new to log — hook wording is unchanged from v3/v4, only its on-screen presentation changed.
- **Visual**: found something worth recording, promoted to a cross-project note (not a new ADR — this reuses an existing technique, it doesn't invent one). This is the first time a technique originally built for `hardknocks` (dialogue-caption keyword emphasis, ADR-0018 addendum) was explicitly ported to a second project (`aiwork`) rather than reinvented per-project. Saved as a feedback memory (`feedback_caption_style_standard`) so future videos in any niche default to this treatment (big base font, one highlighted keyword phrase per line, single simultaneous multi-line reveal for any caption too long for one line at large size) instead of each project re-deriving its own small-font/per-line-box style from scratch.

### Workflow Delta (bắt buộc, mọi video, reactive)
No WORKFLOW.md/ADR change needed. This was a straightforward reuse of an already-documented, already-proven technique (hardknocks' own ADR-0018 addendum) — "copy, don't invent" (AGENTS.md Key Conventions) applied across projects, not just within one. If a third project independently re-derives the same caption style, that would be the trigger to promote it from "reusable technique living in hardknocks' render script" to a shared helper module or an explicit WORKFLOW.md/ADR-0018 rule — not done here since only 2 projects use it so far.
