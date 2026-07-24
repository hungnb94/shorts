# HardKnocks V16 Three-Way Material Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build three independently watchable 50–75s Theragun Material Revisions from the V15 source, applying evidence-backed hook density, contrast, SFX and complete-payoff principles learned from `OASaa6MKyZQ`.

**Architecture:** Add one per-project Python/ffmpeg renderer with shared media, caption, music, SFX and QC helpers plus three independent `Variant` timelines. Preserve V15 outputs. Render and validate actual MP4s; do not add renderer unit tests per `AGENTS.md`.

**Tech Stack:** Python 3, ffmpeg/ffprobe, Pillow, mlx-whisper via `/usr/bin/python3`, existing HardKnocks source/Pexels assets.

---

## File Structure

- Create: `pipeline/hardknocks/render_hardknocks_v16_mrbeast_revision.py` — shared renderer and all three timelines.
- Create: `output/projects/hardknocks/clips/v16_mrbeast_work/` — intermediate clips, ASS, audio, QC frames and reports.
- Create: `output/projects/hardknocks/final/2026-07-24-hardknocks_v16a_product_not_company.mp4`.
- Create: `output/projects/hardknocks/final/2026-07-24-hardknocks_v16b_crash_not_breakthrough.mp4`.
- Create: `output/projects/hardknocks/final/2026-07-24-hardknocks_v16c_clinic_could_not_help.mp4`.
- Create: `docs/production/hardknocks-v16-mrbeast-material-revisions.md` — source, design, render and QC record plus metadata for all variants.
- Preserve unchanged: V15 renderer, V15 work directories and uploaded V15A final.

### Task 1: Lock Exact Source Timeline and Assets

**Files:**
- Read: `output/projects/hardknocks/clips/v14_theragun_work/research/transcript.txt`
- Read: `output/projects/hardknocks/clips/v14_theragun_work/research/transcript.json`
- Read: `pipeline/hardknocks/render_hardknocks_v15_theragun_remake.py`
- Inspect: `output/projects/hardknocks/source/xv8qaYubDw4.mp4`
- Inspect: `output/shared/pexels/shoulder_recovery_6095382.mp4`
- Inspect: `output/shared/pexels/massage_gun_man_6390390.mp4`
- Inspect: `output/shared/pexels/product_design_8003421.mp4`

- [ ] Confirm source duration, resolution, audio and frame rate with:

```bash
ffprobe -v error -show_entries format=duration -show_entries stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels -of json output/projects/hardknocks/source/xv8qaYubDw4.mp4
```

Expected: readable video+audio source; live-probed source duration 4,401.301s.

- [ ] Read word timestamps around each candidate range and trim starts/ends to complete spoken clauses. Initial semantic windows:

```python
A = [
    ("product_not_company", 958.12, 968.00),
    ("crash", 17.68, 22.78),
    ("clinic_failure", 192.76, 197.18),
    ("table_relief", 242.42, 249.22),
    ("first_theragun", 381.56, 387.52),
    ("jigsaws", 908.86, 922.18),
    ("clinician_sales", 976.64, 982.42),
    ("empty_trunk", 987.10, 992.86),
    ("athlete_market", 993.26, 1003.34),
    ("validation", 1014.80, 1023.58),
]
B = [
    ("crash", 17.68, 22.78),
    ("clinic_failure", 186.78, 197.18),
    ("constraints", 197.32, 210.60),
    ("table_setup", 216.12, 220.62),
    ("table_relief", 237.28, 249.22),
    ("motion", 362.06, 372.90),
    ("first_theragun", 381.56, 387.52),
]
C = [
    ("clinic_failure", 192.76, 197.18),
    ("constraints", 197.32, 210.60),
    ("table_setup", 216.12, 220.62),
    ("table_relief", 237.28, 249.22),
    ("pain_returns", 250.12, 261.22),
    ("motion", 357.60, 370.00),
    ("first_theragun", 381.56, 387.52),
]
```

- [ ] Verify every final semantic window is under 15s and every variant's projected post-speed runtime is 50–75s.

- [ ] Extract one frame from each Pexels asset and reject any competing product branding or semantic mismatch. Use only crash/injury/mechanism/product-development illustration; mark it `ILLUSTRATION` on screen.

### Task 2: Implement the Shared Renderer and Three Timelines

**Files:**
- Create: `pipeline/hardknocks/render_hardknocks_v16_mrbeast_revision.py`

- [ ] Define immutable timeline records and variant contract:

```python
@dataclass(frozen=True)
class Segment:
    name: str
    source_start: float
    source_end: float
    focus: float
    zoom: float

@dataclass(frozen=True)
class Evidence:
    start: float
    duration: float
    asset: str
    pexels_id: str
    label: str
    layout: str

@dataclass(frozen=True)
class AudioBeat:
    at: float
    kind: str

@dataclass(frozen=True)
class Variant:
    key: str
    version: str
    final_name: str
    hook_title: str
    hook_followup: str
    segments: tuple[Segment, ...]
    evidence: tuple[Evidence, ...]
    value_badges: tuple[tuple[float, float, str, str], ...]
    audio_beats: tuple[AudioBeat, ...]
    cta_start: float
    cta_end: float
    payoff: str
```

- [ ] Add three independent timelines matching the design spec. Variant A closes with athlete validation; B closes with motion→product and excludes company footage; C closes with necessity→mechanism→product and excludes the crash/company footage.

- [ ] Reuse the proven V15 crop/caption approach but add a hook layout mode that keeps a face visible while placing an illustrative side panel. Never replace the face full-screen before raw t=10s.

- [ ] Generate word-synced ASS bursts from the source JSON by concatenating raw Whisper word tokens and stripping once. Caption appears by t=0.2s; bursts contain 2–5 words; one keyword receives the variant accent.

- [ ] Add informational hook overlays at approximately 0.0s, 0.8s, 1.6s, 2.5s, 3.5s and 4.7s. Changes may be crop/reframe, split state, mechanism arrow or evidence panel. Do not insert a static title-card opening.

- [ ] Add source citation after 10s, moving watermark, illustrative labels, causal/timeline cards and Mid-Roll Triple CTA beginning at raw time that resolves to final t=38–42s after speed-up.

- [ ] Generate three score states per variant: low problem pulse, brighter discovery pulse and payoff lift. Insert 120–220ms music attenuation before the decisive mechanism/payoff without removing dialogue.

- [ ] Generate purpose-bound SFX for first second, crash, constraint card, vibration motion, prototype reveal, jigsaw count, sale count, empty-trunk reveal and CTA. Build timed tracks with real leading-silence samples rather than relying on PTS-only `adelay`.

- [ ] Render segments with per-segment 120ms fade-in and 200ms fade-out before hard concat. Normalize dialogue before placement; keep final mix dialogue-led near -16 LUFS.

- [ ] Add fail-fast assertions for output specs, runtime, protected hook, each source clip `<15s`, source usage `<50%`, CTA final start `38–42s`, face-visible hook layouts and no unlabeled stock evidence.

### Task 3: Render All Three Real MP4s

**Files:**
- Execute: `pipeline/hardknocks/render_hardknocks_v16_mrbeast_revision.py`
- Create: the three final MP4 paths listed above.

- [ ] Run a syntax check:

```bash
python3 -m py_compile pipeline/hardknocks/render_hardknocks_v16_mrbeast_revision.py
```

Expected: exit 0.

- [ ] Render V16A:

```bash
/usr/bin/python3 pipeline/hardknocks/render_hardknocks_v16_mrbeast_revision.py --variant a
```

Expected: final MP4 plus `v16a/checks/validation.json`.

- [ ] Render V16B and V16C with `--variant b` and `--variant c`. Expected: each exits 0 and writes a distinct final MP4 without touching V15 files.

- [ ] Run full decode on all outputs:

```bash
for f in output/projects/hardknocks/final/2026-07-24-hardknocks_v16{a_product_not_company,b_crash_not_breakthrough,c_clinic_could_not_help}.mp4; do ffmpeg -v error -i "$f" -f null -; done
```

Expected: no decoder output and exit 0 for all files.

### Task 4: Media-First QC and Creative Adjudication

**Files:**
- Create: `output/projects/hardknocks/clips/v16_mrbeast_work/v16{a,b,c}/checks/`

- [ ] Run ffprobe/spec and final loudness checks for all variants. Expected per output: 1080×1920, 30fps, H.264/yuv420p, AAC 48kHz stereo, 50–75s, final integrated loudness approximately -16 LUFS with true peak below -1.0dBTP.

- [ ] Transcribe each final with:

```bash
/usr/bin/python3 pipeline/tools/transcribe.py --model mlx-community/whisper-large-v3-turbo --language en <final.mp4> <checks/asr.json>
```

Expected: hook, mechanism, CTA and payoff occur in the intended order; no delayed VO/SFX appears at t=0.

- [ ] Generate hook 0–10s, full-arc, CTA and payoff contact sheets. Manually inspect frame 0, every second through 10s and targeted body/payoff timestamps.

- [ ] Run black/freeze/silence scans. Any full black frame, unexplained freeze longer than 1.0s or dialogue dropout is blocking.

- [ ] Review the 0–10s contact sheet at one-second and half-second cadence.
  Require at least five manually confirmed informational visual changes while
  retaining a face throughout. Record ffmpeg scene-change counts as advisory
  only; do not fail a variant solely because scene detection misses reframes or
  cuts between visually similar interview shots.

- [ ] Inspect row brightness and aspect ratio for permanent black bands or non-uniform stretch.

- [ ] Conduct cold-viewer retell for each variant. Required retell fields: who, problem, mechanism/action, evidence, payoff. Reject any variant that needs project context to explain its causal chain.

- [ ] Produce a side-by-side scorecard across clarity, hook gap, visual proof, emotional contrast, payoff closure and finance-channel fit. Do not select a winner for the user; hand off all passing alternatives.

### Task 5: Production Record and Metadata

**Files:**
- Create: `docs/production/hardknocks-v16-mrbeast-material-revisions.md`

- [ ] Record source URL/ID, reference URL/ID, exact clip windows, source usage, illustration IDs, render commands, output hashes and all QC results.

- [ ] Provide one canonical title/description/exactly three visible hashtags/separate Studio tags for each variant. Keep claims traceable to source dialogue and avoid unsupported valuation figures.

- [ ] Record each variant as not uploaded and do not add rows to `docs/experiments/EXPERIMENT-LOG.md` until a real upload URL exists.

- [ ] Run final artifact existence, nonzero-size, ffprobe and hash verification; re-open the production document and confirm all paths/hashes match the actual files.

No commits or pushes are included because the user did not request repository history changes.