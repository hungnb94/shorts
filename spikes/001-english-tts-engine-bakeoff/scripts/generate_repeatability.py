#!/usr/bin/env python3
import argparse
import json
import re
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
CORPUS = json.loads((SPIKE / "corpus.json").read_text())["samples"]
WORK = SPIKE / "work"
REFERENCE_AUDIO = PROFILE_DIR / PROFILE["identity"]["reference_audio"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate one repeatability run with the canonical Finance narrator"
    )
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.run_id):
        parser.error("--run-id must contain only letters, digits, underscore, or hyphen")
    return args


def synthesize(model, text: str, seed: int) -> tuple[np.ndarray, int, float]:
    settings = PROFILE["generation"]["clone"]
    mx.random.seed(seed)
    started = time.perf_counter()
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
    return audio, sample_rate, time.perf_counter() - started


def main() -> None:
    args = parse_args()
    environment = verify_environment(PROFILE, SPIKE, "synthesis")
    fingerprints = verify_system_fingerprints(PROFILE)
    if sha256(REFERENCE_AUDIO) != PROFILE["identity"]["reference_sha256"]:
        raise RuntimeError("Canonical reference hash mismatch")
    raw_dir = WORK / "raw" / args.run_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    for stale in raw_dir.glob("*.wav"):
        stale.unlink()
    model_spec = PROFILE["models"]["voice_clone"]
    snapshot, model_resolution = verified_model_snapshot(model_spec)
    started_batch = time.perf_counter()
    started = time.perf_counter()
    model = load_model(str(snapshot))
    load_seconds = time.perf_counter() - started
    records = []
    base_seed = PROFILE["generation"]["seed"]
    for index, sample in enumerate(CORPUS):
        audio, sample_rate, elapsed = synthesize(model, sample["text"], base_seed + index)
        duration = len(audio) / sample_rate
        low, high = sample["duration_bounds_seconds"]
        if not low <= duration <= high:
            raise RuntimeError(
                f"{sample['id']} duration {duration:.3f}s outside {low}–{high}s"
            )
        output = raw_dir / f"{sample['id']}.wav"
        sf.write(output, audio, sample_rate, subtype="PCM_16")
        records.append(
            {
                "sample_id": sample["id"],
                "run_id": args.run_id,
                "source_text": sample["text"],
                "output": str(output.relative_to(WORK)),
                "sample_rate": sample_rate,
                "duration_seconds": round(duration, 4),
                "synthesis_seconds": round(elapsed, 4),
                "sha256": sha256(output),
            }
        )
    generation = {
        "run_id": args.run_id,
        "profile_id": PROFILE["id"],
        "strategy": PROFILE["runtime"]["strategy"],
        "model": model_spec,
        "model_resolution": model_resolution,
        "runtime_environment": environment,
        "system_fingerprints": fingerprints,
        "seed_policy": f"{base_seed} + stable corpus index; reset before each item",
        "settings": PROFILE["generation"]["clone"],
        "reference_sha256": PROFILE["identity"]["reference_sha256"],
        "records": records,
        "load_seconds": round(load_seconds, 4),
        "batch_seconds": round(time.perf_counter() - started_batch, 4),
    }
    (WORK / f"generation_{args.run_id}.json").write_text(
        json.dumps(generation, indent=2) + "\n"
    )
    print(
        json.dumps(
            {
                "run_id": args.run_id,
                "records": len(records),
                "model_revision": model_resolution["resolved_revision"],
                "lock_sha256": environment["lock_sha256"],
                "load_seconds": generation["load_seconds"],
                "batch_seconds": generation["batch_seconds"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
