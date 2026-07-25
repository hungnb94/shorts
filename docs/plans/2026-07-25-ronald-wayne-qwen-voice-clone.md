# Ronald Wayne Qwen3 Voice Clone Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a separate Ronald Wayne v2 Short whose synthetic narrator uses a local Qwen3-TTS BaseModel clone conditioned on a short Zack D. Films delivery reference, while preserving v1 and all verified visual/source-voice timing.

**Architecture:** Build and verify a pinned MLX synthesis environment; create a project-specific reference/profile; synthesize each narrator segment independently; enforce content and duration gates; reuse the verified video stream and direct Wayne quotes; output and verify a separate v2 artifact.

**Tech Stack:** Python 3.12.9 via uv, MLX, mlx-audio, Qwen3-TTS Base 1.7B 6-bit, FFmpeg/FFprobe, mlx-whisper, Pillow, JSON provenance records.

---

### Task 1: Preserve the v1 control and prepare reference evidence

**Files:**
- Read: `output/projects/ronaldwayne/2026-07-25-ronald-wayne-v1.mp4`
- Create: `output/projects/ronaldwayne/checks-v2-qwen/v1-control.sha256`
- Create outside repository: `/tmp/voice-ref-LFdQAkLvhUc/`

- [ ] Record the current v1 SHA-256 and probe metadata.
- [ ] Confirm the downloaded source metadata has video ID `LFdQAkLvhUc`, channel `Zack D. Films`, and duration about 42 seconds.
- [ ] Use the small-Whisper word timestamps to select a complete 3–8 second sentence window.
- [ ] Extract and normalize the candidate reference to 24kHz mono PCM.
- [ ] Inspect reference ASR and loudness; reject windows with missing words or clipped boundaries.

### Task 2: Create and verify the pinned Qwen synthesis runtime

**Files:**
- Read: `spikes/001-english-tts-engine-bakeoff/requirements-mlx.txt`
- Create: `.venv-mlx/`

- [ ] Create `.venv-mlx` with Python 3.12.9 using uv.
- [ ] Install the hash-locked MLX requirements.
- [ ] Run an import gate for `mlx`, `mlx_audio`, `numpy`, and `soundfile`.
- [ ] Download Qwen Base revision `34ff5318365b59cba9c03ff729f2eee0814caf72` through `snapshot_download`.
- [ ] Verify model and speech-tokenizer sizes and SHA-256 values against the canonical profile.

### Task 3: Build a project-specific clone profile

**Files:**
- Create: `data/narrator-voices/ronald_wayne_zack_style_qwen/profile.json`
- Create: `data/narrator-voices/ronald_wayne_zack_style_qwen/reference.wav`

- [ ] Store the clean bounded reference artifact and its exact transcript.
- [ ] Record source URL/video ID, extraction window, processing chain, reference SHA-256, model revision, generation settings, and synthetic-voice attribution.
- [ ] Keep this profile separate from `natural_talker_male_qwen_blog`.
- [ ] Validate reference duration, format, ASR text, and full decode.

### Task 4: Implement segmented Qwen narration generation

**Files:**
- Create: `pipeline/ronaldwayne/generate_ronaldwayne_qwen_tts.py`
- Read: `output/projects/ronaldwayne/scripts/script-v1.json`
- Create: `output/projects/ronaldwayne/tts-qwen/raw/`
- Create: `output/projects/ronaldwayne/tts-qwen/fitted/`
- Create: `output/projects/ronaldwayne/tts-qwen/generation-report.json`

- [ ] Load the model once and generate each `type=tts` script segment with deterministic per-segment seeds.
- [ ] Write 24kHz mono raw WAV and 48kHz stereo pipeline WAV.
- [x] Measure every raw duration and fail if required compression exceeds `1.42×`.
- [x] Slot-fit with Rubber Band R3 pitch-preserving time compression when needed, followed by FFmpeg `apad` and `atrim`, while preserving the start/end schedule.
- [ ] Write a report containing input text, seed, raw duration, tempo, output duration, file SHA-256, and synthesis time.
- [ ] Run segment-level ASR and reject skipped/repeated content before video assembly.

### Task 5: Assemble v2 audio and remux the verified video

**Files:**
- Modify only as an explicit option: `pipeline/ronaldwayne/render_ronaldwayne_v1.py`
- Create: `output/projects/ronaldwayne/work/v2-qwen/audio/`
- Create: `output/projects/ronaldwayne/2026-07-25-ronald-wayne-v2-qwen.mp4`

- [ ] Reuse Qwen-fitted TTS segments for narrator slots.
- [ ] Re-extract the verified CBS and NextShark source-voice windows using accurate output seeking.
- [ ] Build an exact 60-second voice timeline.
- [ ] Reuse the music bed with sidechain ducking and target `-16 LUFS`, `-1.5 dBTP`.
- [ ] Remux with the verified v1 video stream via `-c:v copy`; never overwrite v1.

### Task 6: Verify final v2 and compare with v1

**Files:**
- Create: `output/projects/ronaldwayne/checks-v2-qwen/verification-summary.json`
- Create: `output/projects/ronaldwayne/checks-v2-qwen/asr/`
- Create: `output/projects/ronaldwayne/checks-v2-qwen/loudness.log`

- [ ] Probe duration, streams, dimensions, frame rate, sample rate, channels, bitrate, and keyframes.
- [ ] Full-decode v2 with FFmpeg.
- [ ] Confirm 40 keyframe boundaries and unchanged visual EDL.
- [ ] Run blackdetect and freezedetect.
- [ ] Measure integrated loudness, true peak, and LRA.
- [ ] Transcribe the final MP4 with word timestamps and verify all factual tokens, amounts, qualifications, CTA, Wayne quotes, and final verdict.
- [ ] Confirm v1 SHA-256 still matches the control record.
- [ ] Generate a short v1/v2 audio comparison artifact for human review if technically useful.

### Task 7: Document and hand off

**Files:**
- Create: `docs/production/ronald-wayne-v2-qwen.md`
- Modify: `output/projects/ronaldwayne/PRODUCTION.md` only to link the separate v2 record; do not overwrite v1 evidence.

- [ ] Record engine/model/revision, reference provenance, extraction window, disclosure, generation settings, ASR outcome, loudness, checksums, and remaining risks.
- [ ] State that the synthetic narrator is not Zack D. Films and no endorsement is implied.
- [ ] Deliver v2 alongside v1 so the user can compare retention treatment versus control.
- [ ] Do not claim improved retention until post-upload analytics provide evidence.
