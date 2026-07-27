# Capytech Charging Short Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce and verify an original 56–60 second 2.5D animated Short that adapts Capybluh's escalation mechanics to the AI-tech story `Charging: 2000 vs 2026 vs 2050`.

**Architecture:** A one-off Python/Pillow renderer generates original 540×960 animation frames and pipes them to ffmpeg for 1080×1920 H.264 encoding. The renderer separately synthesizes a deterministic score and event-bound SFX, generates one diegetic robotic CTA line, composites audio in final timeline time, and muxes the final artifact. A separate media verifier probes and fully decodes the exact MP4, runs detectors, extracts fresh visual evidence, measures final AAC loudness, and writes a machine-readable QC report.

**Tech Stack:** Python 3, Pillow, NumPy, ffmpeg/ffprobe, macOS `say` for one robotic system line, yt-dlp only for source-channel research, Pexels downloader for one licensed in-world hologram insert.

**Repository Policy:** Do not create `test_render_*.py` or unit-test the one-off renderer. Completion evidence is the actual MP4 and media QC. Do not commit or push.

**Execution status (2026-07-27):** All internal production and media-QC tasks were executed. Exact results and design deltas are recorded in `docs/production/capytech-v1-charging-eras.md`. The external naive-viewer Hook Gate remains unresolved and blocks upload-ready status; unchecked boxes below preserve the original execution plan rather than retroactively rewriting it as a completion log.

---

### Task 1: Lock the storyboard and production paths

**Files:**
- Create: `output/projects/capytech/scripts/capytech_v1_storyboard.json`
- Create: `output/projects/capytech/source/capybluh_research_summary.json`

- [ ] **Step 1: Create the storyboard JSON**

Define `version`, `target_duration_seconds`, `fps`, `beats`, `caption_bursts`, `sfx_events`, `score_states`, `watermark_routes`, and `reserved_geometry`. Use these exact beat boundaries:

- hook: 0.0–3.0
- era_2000: 3.0–14.0
- era_2026: 14.0–29.0
- era_2050_setup: 29.0–39.0
- triple_cta: 39.0–42.0
- energy_drain: 42.0–54.0
- update_loop: 54.0–59.0

The CTA text is exactly `LIKE + SUBSCRIBE + COMMENT "CHARGE"`, and the spoken line is exactly `Like, subscribe, and comment charge to continue.`

- [ ] **Step 2: Preserve a compact evidence summary**

Record the inspected Capybluh video IDs, snapshot metrics, observed mechanics, control-video caveat, and the explicit rule `research media must not enter the final render`.

- [ ] **Step 3: Validate both JSON files**

Run:

```bash
python3 -m json.tool output/projects/capytech/scripts/capytech_v1_storyboard.json >/dev/null
python3 -m json.tool output/projects/capytech/source/capybluh_research_summary.json >/dev/null
```

Expected: both commands exit 0.

### Task 2: Acquire one truthful licensed stock insert

**Files:**
- Create: `output/projects/capytech/source/pexels/<asset-id>.mp4`
- Create: `output/projects/capytech/source/pexels/license.json`

- [ ] **Step 1: Load and follow the `video/pexels-download` skill**

Search for vertical or crop-safe server-rack/electricity footage suitable only as a 1–2 second in-world hologram marked `ILLUSTRATION`.

- [ ] **Step 2: Reject semantic near-matches**

Inspect start, middle, and end frames of the exact downloaded file. Reject clips that do not visibly show servers, electrical infrastructure, or energy flow.

- [ ] **Step 3: Store licensing evidence**

Record Pexels page URL, creator, asset ID, direct-file SHA-256, dimensions, duration, and license marker in `license.json`.

- [ ] **Step 4: Define the no-stock fallback**

If no truthful licensed clip passes, omit the insert rather than using misleading footage. Replace it with an original animated server-grid visualization; do not weaken the semantic gate to meet a footage quota.

### Task 3: Implement the procedural visual renderer

**Files:**
- Create: `pipeline/capytech/render_capytech_v1.py`

- [ ] **Step 1: Add deterministic project constants and validation**

Use source canvas 540×960, output 1080×1920, 30 fps, 59.0 seconds, Komika Axis font, and fixed random seed. Validate the storyboard beat order, 50–75 second runtime, CTA start in 38–42 seconds, hook caption by 0.2 seconds, and non-overlapping reserved geometry before rendering.

- [ ] **Step 2: Implement reusable drawing primitives**

Implement focused helpers for easing, camera transform, rounded boxes, outlined text with measured fitting, soft shadows, floor perspective, block-character body parts, face states, phone UI, cable curves, plug, boxes/adapters, AI orb, scan beam, particles, progress meters, CTA panel, and watermark.

The original character palette must be copper/orange skin, navy torso, turquoise legs, and white shoes. Do not use Capybluh's yellow/blue/green combination.

- [ ] **Step 3: Implement frame-level story state**

For each frame time, derive a pure scene state from the storyboard rather than mutating hidden state. The state must include camera, character pose, face, phone position and percentage, cable/prop positions, era label, foreground action, caption burst, CTA visibility, orb status, human-energy percentage, update percentage, and watermark route.

- [ ] **Step 4: Implement the hook**

At frame 0 show the character's large frightened face, a clearly readable `1%` phone, and the charger beyond reach. Maintain real character/prop motion throughout 0–3 seconds. Show `HOW BAD DOES 2050 GET?` by 0.2 seconds and use at least three meaningful progression states before 3.0 seconds: see 1%, lunge, charger slips farther.

- [ ] **Step 5: Implement era escalation**

Render:

- 2000: brick phone, oversized robust cable, immediate success.
- 2026: wrong-cable fan, nested `ADAPTER SOLD SEPARATELY` boxes, cable stopping just short, then a forced update.
- 2050: floating orb, `FREE CHARGE*`, scan, accept, `ENERGY SOURCE: YOU`, triple CTA at 39.0–42.0, human drain, phone 100%, and update drain back to 1%.

Every visual change must advance the objective, friction, price, or payoff; do not add decorative flash-only beats.

- [ ] **Step 6: Implement exact loop composition**

At 58.7–59.0 seconds, place the 1% phone, exhausted character, and charger so the geometry can cut cleanly back to frame 0. The emotional state may differ, but the phone and primary silhouette must occupy closely matched screen regions.

- [ ] **Step 7: Pipe raw frames to ffmpeg**

Stream RGB24 540×960 frames to ffmpeg, upscale with Lanczos to 1080×1920, encode H.264 High Profile, yuv420p, 30 fps, CRF 16–18, and `+faststart`. Write a silent visual master to `output/projects/capytech/clips/capytech_v1_work/visual_master.mp4`.

### Task 4: Build and mix the original audio package

**Files:**
- Modify: `pipeline/capytech/render_capytech_v1.py`
- Create: `output/projects/capytech/clips/capytech_v1_work/audio/`

- [ ] **Step 1: Synthesize the deterministic score**

Generate three original stereo PCM score states with NumPy: playful analog for 2000, faster digital pulse for 2026, and low ominous futuristic layer for 2050. Use simple oscillators, noise percussion, envelopes, and section-level transitions; do not use copyrighted music.

- [ ] **Step 2: Synthesize event-bound SFX**

Create short WAVs for alarm, plug click, success chime, wrong-cable clacks, box pops, cable snap-back, update alert, orb hover, scan, accept, CTA lock/unlock, energy drain, collapse, and update drain. Each SFX must align to one visible or implied event.

- [ ] **Step 3: Generate the CTA voice**

Use an installed macOS system voice suitable for an in-world robotic system. Generate the exact CTA line to AIFF/WAV, trim only leading/trailing silence, apply mild robotic filtering, then compressor before loudness normalization. Do not time-stretch below natural speed; shorten the line only if it cannot fit 39.0–42.0 seconds.

- [ ] **Step 4: Build full-duration tracks with real leading silence**

For every timed SFX and CTA asset, concatenate PCM silence samples before the clip and pad/trim to 59.0 seconds. Do not rely on `adelay` timestamps entering `amix`.

- [ ] **Step 5: Mix and encode final audio**

Duck score under CTA and decisive payoff events, normalize dialogue before positional silence, mix to stereo 48 kHz, leave encoder headroom, and encode AAC at 192 kbps. Mux with the visual master to `output/projects/capytech/final/2026-07-27-capytech_v1_charging_eras.mp4`.

### Task 5: Render and inspect the blocking hook rough

**Files:**
- Create: `output/projects/capytech/clips/capytech_v1_work/hook_rough.mp4`
- Create: `output/projects/capytech/analysis/hook_frames/`

- [ ] **Step 1: Render only 0–3 seconds**

Run:

```bash
python3 pipeline/capytech/render_capytech_v1.py --hook-only
```

Expected: a playable 1080×1920 H.264/AAC rough hook.

- [ ] **Step 2: Extract direct hook frames**

Extract 0.0, 0.2, 0.5, 1.0, 1.5, 2.0, 2.5, and 2.9 second frames from the rough.

- [ ] **Step 3: Manually verify the hook**

Confirm face/action at frame 0, text by 0.2 seconds, readable 1%, continuous motion, visible problem, early SFX, no collision, and meaningful state changes every 0.8–1.5 seconds.

- [ ] **Step 4: Record the external-viewer block**

Create a production-doc section with `Hook Gate item 6: unverified — external naive-viewer evidence required`. Do not invent a response or mark the artifact upload-ready.

### Task 6: Render the full final MP4

**Files:**
- Create: `output/projects/capytech/final/2026-07-27-capytech_v1_charging_eras.mp4`
- Create: `output/projects/capytech/clips/capytech_v1_work/render_manifest.json`

- [ ] **Step 1: Render the full timeline**

Run:

```bash
python3 pipeline/capytech/render_capytech_v1.py
```

Expected: final MP4 and manifest containing exact beat times, caption times, SFX times, CTA interval, watermark routes, source asset hashes, and renderer version.

- [ ] **Step 2: Stop on any renderer failure**

If rendering, TTS, stock decode, or muxing fails, inspect the real error, change strategy, and rerun. Do not create placeholder media or fabricated reports.

### Task 7: Implement and run final-artifact media QC

**Files:**
- Create: `pipeline/capytech/verify_capytech_v1.py`
- Create: `output/projects/capytech/analysis/qc/`

- [ ] **Step 1: Probe and fully decode the exact MP4**

Verify 1080×1920, 30 fps, H.264/yuv420p, AAC 48 kHz stereo, 50–75 seconds, and successful full video/audio decode to null.

- [ ] **Step 2: Run defect detectors**

Run blackdetect, freezedetect, silencedetect, integrated loudness, true peak, and bottom-row brightness scans at distributed timestamps. Read reported timestamps rather than checking exit codes only.

- [ ] **Step 3: Verify the final audio semantically**

Transcribe the final MP4 itself for the hook, CTA/proof, and tail windows. Confirm no delayed CTA/SFX leaks into the hook; the CTA includes Like, Subscribe, and Comment; and no voice begins or truncates at EOF.

- [ ] **Step 4: Generate fresh visual evidence**

Generate a dense 0–10 second hook sheet, full-video contact sheet, CTA frames, scan/source-reveal frames, phone-100/human-0 payoff frame, pre-loop frame, and final frame. Ensure every evidence file is newer than the MP4 it verifies.

- [ ] **Step 5: Manually inspect the artifact**

Check character continuity, prop continuity, mobile text readability, crop safety, caption/face separation, moving watermark route, stock hologram label, no black footer, no non-uniform stretch, CTA timing, exact payoff, and loop geometry.

- [ ] **Step 6: Write machine-readable results**

Write `output/projects/capytech/analysis/qc/final_qc.json` with artifact path, source MP4 hash, measured specs, detector findings, loudness, ASR verdicts, manual frame verdicts, cold-viewer clarity answers, and the external naive-viewer upload block.

- [ ] **Step 7: Revalidate after any rerender**

Any changed MP4 bytes invalidate affected detector, ASR, visual, and checksum evidence. Regenerate those outputs from the latest final artifact.

### Task 8: Complete production documentation and handoff metadata

**Files:**
- Create: `docs/production/capytech-v1-charging-eras.md`
- Modify: `docs/experiments/EXPERIMENT-LOG.md` only if the video is actually uploaded
- Modify: `data/source_videos.csv` only for final-used YouTube source footage; research-only Capybluh videos are not appended

- [ ] **Step 1: Write the production record**

Include status, exact specs, source-channel research, originality boundary, story rationale, hook formula, source/licensing ledger, value-adds, craft-gate evidence, QC results, known issues, and 48-hour metrics checklist.

- [ ] **Step 2: Create one canonical upload package**

Use exactly:

- Title candidate family scoring for at least five titles.
- One final title no longer than 30 visible characters, Title Case, exactly two relevant emoji.
- One description whose first line mirrors the title, at most one additional sentence, and exactly three visible hashtags including `#shorts`.
- Exactly three separate YouTube Studio tags.
- Audience `Not made for kids`, English language, accurate location/category, AI-education playlist, Related Video field, and Upload Details Template field.

- [ ] **Step 3: Run the mandatory retro**

Complete Hook Retro and Workflow Delta. Update WORKFLOW/ADR/AGENTS only if the production reveals a genuinely reusable missing rule or pitfall.

- [ ] **Step 4: Preserve the upload block honestly**

Until external naive-viewer evidence exists, status must remain `Rendered and QC-passed; upload blocked by Hook Gate item 6`, not `Completed` or `upload-ready`.

- [ ] **Step 5: Compute final checksum last**

Run:

```bash
shasum -a 256 output/projects/capytech/final/2026-07-27-capytech_v1_charging_eras.mp4
```

Record the checksum only after no further edit remains.
