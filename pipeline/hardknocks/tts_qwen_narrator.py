#!/usr/bin/env python3
"""One-off narration synthesis with the canonical Finance narrator profile
`natural_talker_male_qwen_blog` (Qwen3-TTS MLX, Base ICL clone).

Runtime Activation of this profile is still `pending_integration` per ADR-0032
(edge-tts remains the temporary adapter, and the direct-API-vs-CLI boundary is
deliberately undecided). This wrapper is an INFORMAL activation for a single
video: it reuses the exact, evidence-verified Base-ICL call pattern from
`spikes/001-english-tts-engine-bakeoff/scripts/generate_repeatability.py` and
the spike's fail-closed provenance guards, without committing to a production
integration boundary.

Must run inside the pinned synthesis env:
    .venv-mlx/bin/python pipeline/hardknocks/tts_qwen_narrator.py \
        --text "..." --out output/.../vo.wav

Output is 48 kHz stereo PCM_s16le (pipeline-native), resampled from the model's
native 24 kHz mono via ffmpeg.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import mlx.core as mx
import numpy as np
import soundfile as sf
from mlx_audio.tts.utils import load_model

ROOT = Path(__file__).resolve().parents[2]
SPIKE = ROOT / "spikes" / "001-english-tts-engine-bakeoff"
sys.path.insert(0, str(SPIKE / "scripts"))

from runtime_provenance import (  # noqa: E402
    sha256,
    verified_model_snapshot,
    verify_environment,
    verify_system_fingerprints,
)

PROFILE_DIR = ROOT / "data" / "narrator-voices" / "natural_talker_male_qwen_blog"
PROFILE = json.loads((PROFILE_DIR / "profile.json").read_text())
REFERENCE_AUDIO = PROFILE_DIR / PROFILE["identity"]["reference_audio"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", required=True, help="Narration line to synthesize")
    parser.add_argument("--out", required=True, help="Output WAV path (48 kHz stereo)")
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Override RNG seed (default: profile generation.seed)",
    )
    return parser.parse_args()


def synthesize(text: str, seed: int) -> tuple[np.ndarray, int]:
    settings = PROFILE["generation"]["clone"]
    model_spec = PROFILE["models"]["voice_clone"]
    snapshot, _ = verified_model_snapshot(model_spec)
    model = load_model(str(snapshot))
    mx.random.seed(seed)
    results = list(
        model.generate(
            text=text,
            ref_audio=str(REFERENCE_AUDIO),
            ref_text=PROFILE["identity"]["reference_text"],
            lang_code=settings["language"],
            temperature=settings["temperature"],
            max_tokens=settings["max_tokens"],
            top_k=settings["top_k"],
            top_p=settings["top_p"],
            repetition_penalty=settings["repetition_penalty"],
            stream=False,
        )
    )
    if not results:
        raise RuntimeError("Base ICL returned no audio")
    sample_rate = results[0].sample_rate
    audio = np.concatenate(
        [np.asarray(item.audio, dtype=np.float32).reshape(-1) for item in results]
    )
    return audio, sample_rate


def main() -> None:
    args = parse_args()
    # Fail-closed provenance: pinned env, system fingerprints, model weights,
    # and the identity-bearing reference artifact must all match the profile.
    verify_environment(PROFILE, SPIKE, "synthesis")
    verify_system_fingerprints(PROFILE)
    if sha256(REFERENCE_AUDIO) != PROFILE["identity"]["reference_sha256"]:
        raise RuntimeError("Canonical reference hash mismatch")

    seed = args.seed if args.seed is not None else PROFILE["generation"]["seed"]
    audio, sample_rate = synthesize(args.text, seed)
    duration = len(audio) / sample_rate
    print(f"synth: {duration:.3f}s @ {sample_rate}Hz, seed={seed}", flush=True)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    raw = out.with_suffix(".raw24k.wav")
    sf.write(raw, audio, sample_rate, subtype="PCM_16")
    # Resample to pipeline-native 48 kHz stereo.
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(raw),
         "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(out)],
        check=True,
    )
    raw.unlink()
    print(f"wrote {out}", flush=True)


if __name__ == "__main__":
    main()
