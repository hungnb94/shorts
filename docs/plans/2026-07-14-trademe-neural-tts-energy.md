# Trade Me Neural TTS Energy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the flat macOS narrator with an energetic Edge neural narrator without changing the accepted visual timeline, source reactions, facts, or duration.

**Status:** Implemented and verified 2026-07-14.

**Architecture:** Keep `render_trademe_v1.py` as the production entry point. Extend each `TTSLine` with synthesis direction, synthesize line-by-line through `edge-tts`, fit only overlong lines with bounded speed-up, and preserve naturally short lines with tail padding. Add unit-level prosody-policy tests plus runtime duration/transcription/audio guards.

**Tech Stack:** Python 3.9, Edge-TTS 7.2.8, ffmpeg/ffprobe, unittest, mlx-whisper.

---

### Task 1: Encode and test the neural-prosody policy

**Files:**
- Create: `pipeline/trademe/test_tts_energy.py`
- Modify: `pipeline/trademe/render_trademe_v1.py:64-75,524-558`

- [x] **Step 1: Write the failing policy tests**

Create tests that import `EDGE_TTS_VOICE`, `compute_fit_tempo`, and `tts_lines`; assert the voice is `en-US-AriaNeural`, all nine beats have explicit rate/pitch direction, short lines return tempo `1.0`, overlong lines are bounded at `1.15`, and impossible fits raise `ValueError`.

- [x] **Step 2: Run the test to verify RED**

Run:

```bash
/usr/bin/python3 -m unittest pipeline.trademe.test_tts_energy -v
```

Expected: import failure because the neural-policy symbols do not exist yet.

- [x] **Step 3: Add the minimal policy model**

Extend `TTSLine` with:

```python
synthesis_text: str
rate_percent: int
pitch_hz: int
```

Add:

```python
EDGE_TTS = Path.home() / ".local/bin/edge-tts"
EDGE_TTS_VOICE = "en-US-AriaNeural"
MAX_POST_TEMPO = 1.15

def compute_fit_tempo(raw_duration: float, target_duration: float) -> float:
    speaking_target = target_duration - 0.18
    required = raw_duration / speaking_target
    if required > MAX_POST_TEMPO:
        raise ValueError("Neural line exceeds its timing budget")
    return max(1.0, required)
```

Populate all nine lines with the rate/pitch table from the design spec.

- [x] **Step 4: Run the tests to verify GREEN**

Run the same unittest command. Expected: all policy tests pass.

### Task 2: Replace macOS `say` with Edge neural synthesis

**Files:**
- Modify: `pipeline/trademe/render_trademe_v1.py:538-558`

- [x] **Step 1: Replace the synthesis command**

For each line, call:

```python
run([
    str(EDGE_TTS),
    "--voice", EDGE_TTS_VOICE,
    "--rate", f"{line.rate_percent:+d}%",
    "--pitch", f"{line.pitch_hz:+d}Hz",
    "--text", line.synthesis_text,
    "--write-media", str(raw_mp3),
])
```

- [x] **Step 2: Replace slow-stretch fitting**

Compute a bounded tempo with `compute_fit_tempo`. Apply `atempo` only at or above `1.0`; never slow speech. Use:

```text
atempo=<1.0..1.15>,highpass=f=75,
acompressor=threshold=-18dB:ratio=2.2:attack=5:release=80:makeup=2,
loudnorm=I=-16:TP=-1.5:LRA=9,
apad=whole_dur=<target>,atrim=0:<target>
```

Fade at the actual speech end, not at the end of padded silence.

- [x] **Step 3: Add runtime guards**

Reject missing Edge CLI, empty output, a fitted line shorter than `target - 0.03s`, or any line that would truncate speech.

- [x] **Step 4: Re-run policy tests and Python compilation**

```bash
/usr/bin/python3 -m unittest pipeline.trademe.test_tts_energy -v
/usr/bin/python3 -m py_compile pipeline/trademe/render_trademe_v1.py
```

Expected: both exit 0.

### Task 3: Validate the nine neural lines before a full render

**Files:**
- Generate: `output/projects/trademe/clips/v1_work/tts/*.mp3`
- Generate: `output/projects/trademe/clips/v1_work/tts/*.wav`
- Generate: `output/projects/trademe/clips/v1_work/checks/tts_energy_report.json`

- [x] **Step 1: Run only `generate_tts()`**

```bash
/usr/bin/python3 -c 'from pipeline.trademe.render_trademe_v1 import require_inputs, generate_tts; require_inputs(); generate_tts()'
```

Expected: nine neural MP3s and nine fitted WAVs.

- [x] **Step 2: Measure timing policy**

Write a JSON report with voice, requested rate/pitch, raw duration, post tempo, fitted duration, and truncation status for each beat. Expected: all post tempos are within `1.0..1.15`; all fitted files match their visual windows within 30ms.

- [x] **Step 3: Transcribe a concatenated TTS preview**

Concatenate the nine fitted WAVs and transcribe with `mlx-community/whisper-small-mlx`. Compare normalized transcript tokens to the intended narration. Expected: every factual phrase is recovered; punctuation differences are allowed.

### Task 4: Render the replacement artifact

**Files:**
- Preserve: `output/projects/trademe/final/2026-07-14-trademe_v1_worst_trade_house_macos_tts.mp4`
- Replace: `output/projects/trademe/final/2026-07-14-trademe_v1_worst_trade_house.mp4`

- [x] **Step 1: Preserve the verified previous render**

Copy the current canonical file to the `_macos_tts.mp4` path only if that backup does not already exist. Verify both hashes before rendering.

- [x] **Step 2: Run the full renderer**

```bash
/usr/bin/python3 pipeline/trademe/render_trademe_v1.py
```

Expected: exit 0, source-audio guards pass, final decode passes.

### Task 5: Verify the final mix and update documentation

**Files:**
- Modify: `docs/production/trademe-v1-worst-trade-house.md`
- Modify: `docs/specs/2026-07-14-trademe-tts-energy-design.md` only if actual verified parameters differ

- [x] **Step 1: Verify specs and audio**

Run ffprobe, full decode, `silencedetect`, and loudness analysis. Expected: 1080x1920, H.264/AAC, 30fps, ≤60s, no long unintended silence, true peak below 0 dBTP.

- [x] **Step 2: Transcribe the final mix**

Expected: all nine narrator lines, trailer quote, and isolated house reaction are recoverable.

- [x] **Step 3: Run repository hygiene checks**

```bash
/usr/bin/python3 -m unittest pipeline.trademe.test_tts_energy -v
git diff --check
git status --short --branch
```

Expected: tests and whitespace check pass. Do not commit or push.

- [x] **Step 4: Record final engine, voice, timing-policy, loudness, hash, and preserved backup path in the production report.**
