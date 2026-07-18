# 001: Finance Narrator Reproducibility

## Decision

The English TTS bake-off is complete. The canonical Finance/English Narrator Voice Profile is `natural_talker_male_qwen_blog`:

- profile: `../../data/narrator-voices/natural_talker_male_qwen_blog/profile.json`;
- identity artifact: `../../data/narrator-voices/natural_talker_male_qwen_blog/reference.wav`;
- strategy: Qwen **Voice Design then Clone**;
- VoiceDesign model: `mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-6bit`;
- Base ICL model: `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-6bit`.

The local reference is fully synthetic and was generated from the selected text description. No human, Source Channel, celebrity, or official Qwen demo audio is used for conditioning. The official demo was listening evidence only and is not retained in the repository.

AI-education does not inherit this profile; it selects a separate narrator later. Existing `edge-tts` renderer calls remain a temporary Runtime Adapter until the direct Python API versus standalone batch CLI comparison is completed.

## Why the reference WAV is versioned

The description and seed alone are not the voice identity. Model/runtime changes can produce a different timbre from the same prompt. `reference.wav` is therefore the Canonical Narrator Voice Artifact and is protected by the SHA-256 stored in `profile.json`. All raw, normalized, audition, comparison and repeatability audio is regenerable and ignored under `work/`.

## Setup

Synthesis and ASR use separate environments because MLX-Audio is verified with NumPy 2.5 while Numba/MLX-Whisper currently resolves against an older NumPy line.

```bash
uv venv --python 3.12.9 .venv-mlx
uv pip install --python .venv-mlx/bin/python -r requirements-mlx.txt

uv venv --python 3.14.6 .venv-asr
uv pip install --python .venv-asr/bin/python -r requirements-asr.txt
```

`ffmpeg` and `ffprobe` must be available on `PATH`.

`requirements-*.in` contain the direct pins. `requirements-*.txt` are the complete, hash-locked environments consumed at install time. Regenerate a lock only as an explicit runtime migration; its SHA-256 is part of `profile.json` and every evidence run verifies the installed package set against it.

Both Qwen models are loaded from immutable Hugging Face revisions. The harness verifies the SHA-256 and size of each model and speech-tokenizer weight before executing local code from the snapshot. The profile also pins revision-specific model-card and source-license URLs.

## Verify the canonical profile

This gate checks assignment, provenance, SHA-256, WAV format, duration and full decode without loading a model:

```bash
python3 scripts/verify_profile.py
```

## Regenerate the canonical reference candidate

This never overwrites the canonical artifact. It writes a candidate under ignored `work/` and fails if the regenerated hash differs:

```bash
.venv-mlx/bin/python scripts/generate_reference_candidate.py
```

## Cross-process repeatability

Run A and B in separate OS processes:

```bash
.venv-mlx/bin/python scripts/generate_repeatability.py --run-id run_a
.venv-mlx/bin/python scripts/generate_repeatability.py --run-id run_b
.venv-mlx/bin/python scripts/prepare_repeatability.py
.venv-asr/bin/python scripts/asr_repeatability.py
```

Outputs are written under ignored `work/`. The accepted reference run produced:

- 4/4 raw cross-process hash matches;
- 4/4 normalized cross-process hash matches;
- maximum duration delta: 0.0 seconds;
- ASR sequence ratio: 0.9691;
- ASR LCS word recall: 0.9600.

The fail-closed regression suite uses synthetic WAV fixtures and requires no model load:

```bash
.venv-asr/bin/python -m unittest discover -s tests -v
```

## Failure that changed the strategy

Direct VoiceDesign synthesis of the 53.92-second upstream demo text produced valid content followed by repeated “Yeah” until the 2,048-token cap. The 163.84-second output was rejected rather than trimmed. The selected workflow therefore designs one bounded local reference and uses Base ICL for bounded semantic passages.

## Next decision

Measure direct Python API versus a standalone batch CLI on this profile before replacing the temporary `edge-tts` Runtime Adapter. Do not build an HTTP service unless measured startup or throughput data justifies one.
