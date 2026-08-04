---
name: viral-video-analysis
description: Reverse-engineer a viral short-form video (YouTube Shorts/TikTok) to extract concrete hook, cut/pacing, overlay/text, sound-design, and audience-psychology techniques, then propose a specific AB-test for this project's next video. Use whenever the user pastes a viral video URL and asks to analyze/study/learn from it, asks "why did this go viral", wants to compare a just-finished video against a viral reference during the Stage 5 Post-Production Retro (docs/WORKFLOW.md), or wants to reverse-engineer hook/editing/sound patterns from competitor content.
---

# Viral Video Analysis

Analyzes one or more externally-sourced viral videos (NOT this project's own output — for
that, see the Hook Gate in `docs/WORKFLOW.md` Stage 0) to extract reusable hook/editing/sound
patterns, and turns them into a concrete AB-test recommendation for one of this project's 3
niches (finance, health-VN, AI-education — CONTEXT.md → **Source Channel**).

This only feeds `docs/WORKFLOW.md` **Stage 5** (Post-Production Retro), never Stage 0 (Hook
Gate stays manual visual judgment, per that doc's own "out of scope" note). If invoked while
working on a specific `docs/production/<name>.md`, this skill's findings must directly fill in
that doc's "Hook Retro" and "Workflow Delta" subsections — don't produce a disconnected report.

Read `CONTEXT.md` and `docs/adr/0023-viral-video-analysis-skill.md` before starting if you
haven't already this session — they hold the domain vocabulary (Hook, Hook-Window Rule, Value-Add
Type, AB Variable, Source Channel Pattern...) this skill's output must speak in, and the
rationale for why this skill is built the way it is.

## Process

### 1. Intake

Get from the user (or infer): the video URL(s), a short topic-slug for the output folder name,
and whether this run is happening as part of a Stage 5 Retro for a specific production doc
(if so, get that doc's path — you'll write back into it in step 8).

### 2. Fetch

```bash
mkdir -p docs/research/<topic-slug>-<YYYY-MM-DD>/<video_id>
yt-dlp -f "bv*+ba/b" -S "res:1080" --merge-output-format mp4 \
  -o "docs/research/<slug>/<id>/source.mp4" "<url>"
yt-dlp --write-subs --write-auto-sub --sub-lang en --skip-download -o "docs/research/<slug>/<id>/transcript" "<url>"
yt-dlp --write-comments --skip-download -o "docs/research/<slug>/<id>/comments.%(ext)s" "<url>"
```

Quality note: `-S "res:1080"` caps the shorter dimension at approximately 1080 while preserving
orientation: it selects up to 1920x1080 for landscape and 1080x1920 for portrait. Do not use
`height<=1080` here: on a portrait Short that selector rejects the 1080x1920 source and can
silently fall back to 360x640. The analysis cap is deliberate — this is analysis, not footage
for reuse, so the "always download max quality / 4K" rule in `AGENTS.md` (which governs Source
Channel footage that gets edited into this project's own videos) does not apply.

Extract `comments_top100.json` / `comments_highlights.json` from the raw comments JSON the same
way `docs/research/hook-benchmarks-2026-07/<video_id>/` already does it — match that existing
file naming so both studies stay comparable.

### 3. Visual/cut extraction

```bash
python3 .agents/skills/viral-video-analysis/scripts/extract_keyframes.py \
  docs/research/<slug>/<id>/source.mp4 \
  --out-dir docs/research/<slug>/<id>/frames --max-frames 8 --hook-window-sec 10 -v
```

Produces `frames/manifest.json` with `scene_keyframes` (whole-video scene changes) and
`hook_window_frames` (fixed 1s-interval frames across 0-10s, for cadence measurement
independent of whether scene-detect fires there).

### 4. Agent visual analysis

Read every frame in the manifest directly via the Read tool — do not skip this by trying to
infer content from filenames/timestamps alone. For each: describe the scene, transcribe any
visible on-screen text/overlay, and specifically judge the `t=0` frame per
`references/frame-and-cadence.md` (face/action vs. title-card). Compute cut cadence from the
`scene_keyframes` gaps. Optionally run `inspect_image.py` on 2-3 hook-window frames for
quantitative backup (skin-tone %, near-white %) — see that file's `--help`.

### 5. Audio analysis

```bash
python3 .agents/skills/viral-video-analysis/scripts/analyze_audio.py \
  docs/research/<slug>/<id>/source.mp4 \
  --cut-timestamps "<comma-separated scene_keyframes timestamps from step 3>" \
  -o docs/research/<slug>/<id>/audio_analysis.json -v
```

Read `references/sound-design.md` for how to interpret `tempo_bpm`, `onset_times`,
`energy_jumps`, and `cuts_aligned_with_audio`.

### 6. Comment psychology

Read every comment in `comments_top100.json`/`comments_highlights.json` (not a sample) per
`references/comment-psychology.md`.

### 7. Synthesis

Write `docs/research/<slug>-<date>/REPORT.md` following `references/report-template.md`
exactly, including the "Suggested Next Video / AB-Test" section — every analysis session must
end with a concrete, falsifiable proposal, not just observations.

### 8. Integrate into docs

- **`CONTEXT.md`**: add or sharpen glossary terms per the domain-modeling discipline (challenge
  fuzzy language, cite `docs/research/<slug>/REPORT.md` as the source, match the existing
  `**Term**: definition` / `_Avoid_: ...` format exactly).
- **ADR**: only *propose* one to the user if it passes all 3 criteria (hard to reverse,
  surprising, real trade-off) — do not write one unprompted. Next available number: check
  `docs/adr/` for the highest existing `NNNN-*.md`.
- **`docs/WORKFLOW.md`**: if a finding generalizes into a new checkable rule, add one line to
  the relevant Stage 5 subsection (Hook Retro / Workflow Delta), citing this analysis.
- **`docs/agent/*-pitfalls.md`**: if it's a reusable implementation/research failure, log it
  in the relevant on-demand pitfall file instead of expanding root context.
- **If this run is a Stage 5 Retro for a specific production doc**: directly write the answers
  into that doc's `## Post-Production Retro` → `### Hook Retro` (Verbal/Visual) and
  `### Workflow Delta` subsections, per the exact format already defined in `docs/WORKFLOW.md`
  Stage 5. Cite the video analyzed as the source of the idea.

## Bundled scripts

- `scripts/extract_keyframes.py` — ffprobe + ffmpeg scene-detect, writes frames + manifest.json.
  No vision API call; the active agent reads frames directly (see ADR-0023 for why this replaced the
  GPT-4o-based `video-analyzer` Hermes skill this was ported from).
- `scripts/analyze_audio.py` — ffmpeg + librosa onset/beat/energy detection. Requires `librosa`
  (already installed in this repo's `.venv`; if working in a fresh environment run
  `pip install librosa`).
- `scripts/inspect_image.py` — optional PIL pixel-statistics backup for the frame-0 check
  (skin-tone %, near-white %, text bands). Supporting evidence only, not the primary judgment.

## References

- `references/hook-patterns.md` — hook taxonomy + classification + niche-transfer process
- `references/frame-and-cadence.md` — frame-0 check + cut cadence measurement
- `references/sound-design.md` — how to interpret `analyze_audio.py` output
- `references/comment-psychology.md` — how to read audience comments for real (not surface)
  psychological drivers
- `references/report-template.md` — exact report skeleton to fill in during step 7
