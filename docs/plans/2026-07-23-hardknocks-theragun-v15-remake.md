# HardKnocks Theragun V15 Remake Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build two new 50–75s Theragun Shorts whose premise, chronology and payoff remain understandable to a cold viewer while retaining the project’s media/craft gates.

**Architecture:** Create a new standalone V15 renderer by adapting the proven V14 ffmpeg/ASS pipeline without modifying the rejected V14 baseline. V15A uses a chronological crash-to-invention arc; V15B uses clinic validation-to-athlete-market proof. Both preserve original source voice, split source turns for active-speaker portrait crops, composite proof-coupled Pexels only after 10s, and use a compact non-blocking CTA after the first payoff.

**Tech Stack:** Python 3, ffmpeg/ffprobe, Pillow, mlx_whisper, ASS/libass.

---

## File map

- Create `pipeline/hardknocks/render_hardknocks_v15_theragun_remake.py` — V15 timeline, segment rendering, captions, proof compositing, SFX/music and built-in media validation.
- Create `docs/production/hardknocks-v15-theragun-remake.md` — canonical production trace and publishing metadata for both artifacts.
- Create `output/projects/hardknocks/clips/v15_theragun_work/<variant>/...` — intermediate timeline, ASS, detector and QC artifacts.
- Create `output/projects/hardknocks/final/2026-07-23-hardknocks_v15a_crash_created_theragun.mp4`.
- Create `output/projects/hardknocks/final/2026-07-23-hardknocks_v15b_first_patient_to_athletes.mp4`.
- Preserve `pipeline/hardknocks/render_hardknocks_v14_theragun_dual.py` and both rejected V14 MP4s unchanged as failed baselines.

### Task 1: Implement source-native V15 timelines

**Files:**
- Create: `pipeline/hardknocks/render_hardknocks_v15_theragun_remake.py`

- [ ] **Step 1: Copy only the working render/QC primitives from V14 into a new V15 file**

Keep `Segment`, `Evidence`, `Variant`, `render_segment`, timeline frame accounting, word-timestamp captions, post-render compositing, audio fades, full decode and ffprobe validation. Remove V14’s hook-card generator and rejected quote-first constants.

- [ ] **Step 2: Define V15A chronology and speaker crops**

Use these exact source windows, all under 15 seconds:

```python
A_SEGMENTS = (
    Segment("inventor_identity", 1.86, 5.30, 0.24, 1.06),
    Segment("accident_question", 12.72, 15.80, 0.24, 1.06),
    Segment("crash_answer", 16.40, 22.78, 0.68, 1.08),
    Segment("perspective_question", 22.94, 24.64, 0.24, 1.08),
    Segment("mission_and_clinic", 25.52, 31.52, 0.68, 1.08),
    Segment("vibrating_table", 31.66, 44.78, 0.68, 1.08),
    Segment("first_theragun", 44.78, 51.40, 0.68, 1.10),
    Segment("problem_birthed_company", 52.28, 56.58, 0.24, 1.08),
    Segment("saved_my_life", 57.08, 57.94, 0.68, 1.10),
    Segment("product_not_company", 958.12, 968.00, 0.68, 1.08),
)
```

Expected raw duration: `55.38s`; expected final duration at `1.06x`: approximately `52.25s`. The first full `Theragun` word lands near raw `38.58s`, before the compact CTA.

- [ ] **Step 3: Define V15B chronology and speaker crops**

```python
B_SEGMENTS = (
    Segment("jigsaw_to_clinic", 604.92, 613.82, 0.68, 1.08),
    Segment("patient_arrives", 622.58, 624.34, 0.68, 1.08),
    Segment("same_injuries", 628.80, 631.20, 0.68, 1.10),
    Segment("prototype_must_help", 644.32, 647.46, 0.68, 1.10),
    Segment("paper_bag_trial", 671.66, 682.10, 0.68, 1.08),
    Segment("patient_improved", 783.64, 787.48, 0.68, 1.08),
    Segment("saved_two_lives", 787.54, 800.60, 0.68, 1.10),
    Segment("one_per_day", 976.64, 982.42, 0.68, 1.08),
    Segment("market_bridge", 982.42, 986.72, 0.68, 1.08),
    Segment("empty_trunk", 987.10, 992.86, 0.68, 1.10),
    Segment("athlete_market", 993.26, 1003.34, 0.68, 1.10),
)
```

Expected raw duration: `69.46s`; expected final duration: approximately `65.53s`. The patient proof completes near raw `39.06s`; the market discovery remains the final payoff.

- [ ] **Step 4: Define clarity-first overlays**

Use speech captions from ASR as the primary text. Add only the following top labels:

```python
V15A: 0.05–3.40 "THE THERAGUN ORIGIN"; 3.45–10.00 "IT STARTED WITH A CRASH"
V15B: 0.05–3.20 "THE FIRST THERAGUN"; 3.20–8.90 "WAS A JIGSAW"
```

Add minimal chapter badges tied to causal updates, not decorative cards. Do not use unresolved `THIS THING` in the hook.

- [ ] **Step 5: Keep the CTA non-blocking and after the first payoff**

Set per-variant raw CTA start to `43.00s` for V15A and `44.00s` for V15B. Render `LIKE • SUBSCRIBE • COMMENT` as a compact bottom-band overlay for about 3.4 raw seconds; do not cover the active speaker or replace the story with a full-screen card.

### Task 2: Add proof-coupled post-render compositing

**Files:**
- Modify: `pipeline/hardknocks/render_hardknocks_v15_theragun_remake.py`

- [ ] **Step 1: Register existing verified assets**

```python
PEXELS_MASSAGE = output/shared/pexels/massage_gun_man_6390390.mp4
PEXELS_SHOULDER = output/shared/pexels/shoulder_recovery_6095382.mp4
PEXELS_DESIGN = output/shared/pexels/product_design_8003421.mp4
PEXELS_TOOL = output/shared/pexels/power_tool_workshop_6790429.mp4
```

- [ ] **Step 2: Schedule V15A evidence**

Use four `3.50s` full-screen proof windows after raw 10s: shoulder recovery during clinic/pain, shoulder mechanism during table relief, massage-gun use at product reveal, and product-design/massage use at the company transition. Total Pexels share should remain approximately 25%.

- [x] **Step 3: Schedule V15B evidence**

Use four `3.50s` windows after raw 10s: shoulder recovery for matching injuries, massage-gun use for patient proof, product design for early sales, and massage-gun use for athlete-market proof. Exact-frame QC rejected the cached `power_tool_workshop` insert because it shows a drill press rather than a jigsaw. The jigsaw beat therefore keeps Jason visible while the original audio and caption say `Makita jigsaw`; semantic integrity takes priority over an arbitrary stock quota. Final Pexels share target is approximately 20%.

- [ ] **Step 4: Preserve causality around every insert**

Keep original audio continuous under each proof insert. Label Pexels as illustration. Reject any insert that implies a competing brand, depicts an unsupported event, or hides a critical product/patient reaction.

### Task 3: Render both real MP4 artifacts

**Files:**
- Create: `output/projects/hardknocks/final/2026-07-23-hardknocks_v15a_crash_created_theragun.mp4`
- Create: `output/projects/hardknocks/final/2026-07-23-hardknocks_v15b_first_patient_to_athletes.mp4`

- [ ] **Step 1: Syntax-check the renderer**

Run:

```bash
python3 -m py_compile pipeline/hardknocks/render_hardknocks_v15_theragun_remake.py
```

Expected: exit code `0`.

- [ ] **Step 2: Render V15A and inspect before spending time on V15B**

```bash
/usr/bin/python3 pipeline/hardknocks/render_hardknocks_v15_theragun_remake.py --variant a
```

Expected: final MP4 plus `validation.json`, `timeline.json`, hook sheet and arc sheet.

- [ ] **Step 3: Render V15B**

```bash
/usr/bin/python3 pipeline/hardknocks/render_hardknocks_v15_theragun_remake.py --variant b
```

Expected: final MP4 plus equivalent checks.

### Task 4: Run media-first QC and manual clarity review

**Files:**
- Create: `output/projects/hardknocks/clips/v15_theragun_work/<variant>/checks/*`

- [ ] **Step 1: Verify specs and full decode**

Require 1080x1920, H.264/yuv420p, 30fps, AAC 48kHz stereo, 50–75s, every source excerpt under 15s, source cut below 50% of source duration, and first full-screen Pexels after final t=10s.

- [ ] **Step 2: Run detectors**

Run ffmpeg `blackdetect`, `freezedetect`, `silencedetect` and EBU loudness analysis on the actual final MP4. Require no black/freeze/silence defects and loudness near the renderer target.

- [ ] **Step 3: Run final-artifact ASR**

Transcribe each full final MP4 and targeted hook/payoff/tail windows. Assert these critical phrases survive:

```text
V15A: inventor / massage gun / motorcycle accident / nothing in my clinic / first Theragun / product / company
V15B: Makita jigsaw / clinic / same injuries / saved my life / one a day / trunk / athletes
```

- [ ] **Step 4: Review hook and arc sheets manually**

Reject if frame 0 is static, any 0–3s interval lacks real human motion, face/caption collision occurs, full-screen Pexels appears before 10s, the active speaker is cropped out, or a proof insert mismatches the spoken claim.

- [ ] **Step 5: Run cold-viewer clarity gate**

Review each final video without title/description and answer:

```text
Who is the story about?
What problem occurred?
What did he do?
What result/payoff followed?
```

Do not hand off unless each answer can be stated from the MP4 alone.

### Task 5: Write canonical production and publishing metadata

**Files:**
- Create: `docs/production/hardknocks-v15-theragun-remake.md`

- [ ] **Step 1: Record verified media data and timelines**

Copy measured durations, codecs, loudness, source windows, Pexels windows, ASR checks and clarity verdicts from actual outputs; do not use expected values as final evidence.

- [ ] **Step 2: Add one canonical metadata package per video**

For each V15 artifact, provide one title no longer than 30 visible characters with exactly two emoji, a description whose first line mirrors the title and ends with exactly three visible hashtags including `#shorts`, and exactly three separate Studio tags.

- [ ] **Step 3: Validate metadata programmatically**

Check title length, emoji count, description mirror, hashtag cardinality and Studio-tag cardinality before handoff.

## Self-review

- Spec coverage: both distinct story spines, original source voice, active-speaker crops, proof-coupled 3-source treatment, compact CTA, technical QC, ASR, visual review, clarity review and metadata are covered.
- Placeholder scan: no `TBD`, `TODO`, `implement later` or undefined artifact paths.
- Scope: V14 remains unchanged; only a new V15 renderer/doc/output namespace is added.
- Policy exception: no Python renderer unit test is added; completion is based on real MP4 QC per repository policy.
