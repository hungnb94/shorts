# OUTWISHED 001 Speech-Bubble Text Trial Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Burn concise English comic dialogue bubbles onto the existing 57.725-second trimmed visual/SFX cut so the story is understandable without voice-over.

**Architecture:** A dedicated per-project Python renderer defines a timed bubble event list, generates one transparent full-canvas PNG per event with Pillow, and composites those overlays onto the already-verified MP4 with ffmpeg. The base video and audio remain unchanged except for one necessary H.264 re-encode of the visual layer. Media QC—not renderer unit tests—verifies the real output.

**Tech Stack:** Python 3, Pillow, ffmpeg 7, ffprobe, Comic Sans MS fallback font installed at `/System/Library/Fonts/Supplemental/Comic Sans MS Bold.ttf` because Komika Axis is not installed.

---

### Task 1: Build the timed bubble renderer

**Files:**
- Create: `pipeline/outwished/render_dialogue_text_trial.py`
- Read: `output/projects/outwished/final/2026-07-22-outwished-001-trimmed-visual-cut.mp4`
- Create: `output/projects/outwished/work/dialogue-text-trial/*.png`

- [ ] Define a `BubbleEvent` dataclass with `start`, `end`, `speaker`, `text`, `box`, `anchor`, and `kind` fields.
- [ ] Encode the approved timeline as short consecutive bursts; each event lasts at least 0.75 seconds and contains no more than two rendered lines.
- [ ] Define speaker styles: Nico cream/teal, Officer white/red, Veyr plum/cyan, System dark/cyan.
- [ ] Implement measured wrapping with `ImageDraw.textbbox`; fail when text cannot fit the event box at a minimum 42-pixel font size.
- [ ] Render rounded rectangles, high-contrast outlines, speaker labels, and triangle/cloud tails onto full-canvas 1080x1920 RGBA PNGs.
- [ ] Assert event times stay inside the probed base duration and do not overlap.
- [ ] Run `python3 pipeline/outwished/render_dialogue_text_trial.py` and require exit code 0.

### Task 2: Composite and create trial artifacts

**Files:**
- Create: `output/projects/outwished/final/2026-07-22-outwished-001-dialogue-text-trial.mp4`
- Create: `output/projects/outwished/final/2026-07-22-outwished-001-dialogue-text-trial.json`
- Create: `output/projects/outwished/analysis/2026-07-22-outwished-001-dialogue-text-contact-sheet.jpg`

- [ ] Add every generated PNG as a single-frame ffmpeg input without `-loop 1`.
- [ ] Chain `overlay=eof_action=repeat:enable='between(t,start,end)'` filters and preserve the base audio stream.
- [ ] Encode H.264 High Level 4.2, 1080x1920, 24 fps CFR, AAC stereo 48 kHz, and `+faststart`.
- [ ] Write a JSON manifest containing every displayed burst, speaker, timing, style, font fallback, and source artifact.
- [ ] Generate a contact sheet sampling every event midpoint.

### Task 3: Verify the actual MP4

**Files:**
- Create: `output/projects/outwished/final/2026-07-22-outwished-001-dialogue-text-qc.json`
- Create: `output/projects/outwished/analysis/2026-07-22-outwished-001-dialogue-text-events.jpg`

- [ ] Run ffprobe and require duration 50–75 seconds, 1080x1920, H.264 Level 4.2, 24/1 `r_frame_rate` and `avg_frame_rate`, plus AAC stereo 48 kHz.
- [ ] Run a full audio/video decode with `ffmpeg -v error ... -f null -` and require exit code 0.
- [ ] Run blackdetect ≥0.5s, freezedetect ≥1s, and silencedetect ≥1s; record all events.
- [ ] Extract every event midpoint into a labelled contact sheet.
- [ ] Manually review every labelled event for readable text, correct speaker association, face avoidance, Lamp/vault visibility, and mobile-safe margins.
- [ ] Record SHA-256 and file size in the QC report.
- [ ] Keep the artifact labelled `dialogue-text trial`; do not call it upload-final while SHOT-011/012, final VO, CTA, watermark, and publishing metadata remain missing.

## Self-review

- Spec coverage: bubble style, timing, speaker colors, system alert, local-only rendering, and media QC are all mapped to tasks.
- Placeholder scan: no TBD/TODO/unspecified implementation step remains.
- Scope: one renderer and one trial artifact; no paid generation, source revision, upload, or unrelated refactor.
- Policy: no renderer unit test and no commit are included, matching repository instructions.
