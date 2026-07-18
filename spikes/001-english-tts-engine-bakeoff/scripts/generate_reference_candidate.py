#!/usr/bin/env python3
import json
import time
from pathlib import Path

import mlx.core as mx
import numpy as np
import soundfile as sf
from mlx_audio.tts.utils import load_model
from runtime_provenance import (
    sha256,
    verified_model_snapshot,
    verify_environment,
    verify_system_fingerprints,
)

SPIKE = Path(__file__).resolve().parents[1]
REPO = SPIKE.parents[1]
PROFILE_DIR = REPO / "data" / "narrator-voices" / "natural_talker_male_qwen_blog"
PROFILE = json.loads((PROFILE_DIR / "profile.json").read_text())
WORK = SPIKE / "work" / "reference-candidate"


def main() -> None:
    environment = verify_environment(PROFILE, SPIKE, "synthesis")
    fingerprints = verify_system_fingerprints(PROFILE)
    WORK.mkdir(parents=True, exist_ok=True)
    model_spec = PROFILE["models"]["voice_design"]
    settings = PROFILE["generation"]["reference"]
    seed = PROFILE["generation"]["seed"]
    snapshot, model_resolution = verified_model_snapshot(model_spec)
    started_batch = time.perf_counter()
    started = time.perf_counter()
    model = load_model(str(snapshot))
    load_seconds = time.perf_counter() - started
    mx.random.seed(seed)
    started = time.perf_counter()
    results = list(
        model.generate_voice_design(
            text=PROFILE["identity"]["reference_text"],
            instruct=PROFILE["identity"]["description"],
            language=settings["language"],
            temperature=settings["temperature"],
            max_tokens=settings["max_tokens"],
            top_k=settings["top_k"],
            top_p=settings["top_p"],
            repetition_penalty=settings["repetition_penalty"],
            stream=False,
        )
    )
    if not results:
        raise RuntimeError("VoiceDesign returned no reference audio")
    sample_rate = results[0].sample_rate
    audio = np.concatenate(
        [np.asarray(item.audio, dtype=np.float32).reshape(-1) for item in results]
    )
    duration = len(audio) / sample_rate
    if not 5.0 <= duration <= 25.0:
        raise RuntimeError(f"Reference duration {duration:.3f}s is outside 5–25s")
    output = WORK / "reference.wav"
    sf.write(output, audio, sample_rate, subtype="PCM_16")
    actual_hash = sha256(output)
    canonical_hash = PROFILE["identity"]["reference_sha256"]
    metadata = {
        "profile_id": PROFILE["id"],
        "model": model_spec,
        "model_resolution": model_resolution,
        "runtime_environment": environment,
        "system_fingerprints": fingerprints,
        "seed": seed,
        "settings": settings,
        "duration_seconds": round(duration, 4),
        "sha256": actual_hash,
        "canonical_sha256": canonical_hash,
        "canonical_hash_equal": actual_hash == canonical_hash,
        "load_seconds": round(load_seconds, 4),
        "synthesis_seconds": round(time.perf_counter() - started, 4),
        "batch_seconds": round(time.perf_counter() - started_batch, 4),
    }
    (WORK / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))
    if actual_hash != canonical_hash:
        raise RuntimeError("Regenerated reference differs from the canonical voice artifact")


if __name__ == "__main__":
    main()
