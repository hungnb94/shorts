#!/usr/bin/env python3
"""Generate the canonical Finance narrator for the AI power long-form pilot.

Loads the pinned Qwen3-TTS MLX model once, synthesizes every script scene at its
natural duration, normalizes each segment before timeline placement, and records
full deterministic provenance. No speech is hard-trimmed or tempo-fitted.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import mlx.core as mx
import numpy as np
import soundfile as sf
from mlx_audio.tts.utils import load_model

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output/projects/ai-power-bottleneck"
SCRIPT = PROJECT / "scripts/script.json"
PROFILE_DIR = ROOT / "data/narrator-voices/natural_talker_male_qwen_blog"
PROFILE_PATH = PROFILE_DIR / "profile.json"
TTS_DIR = PROJECT / "work/tts"
RAW = TTS_DIR / "raw"
FINAL = TTS_DIR / "final"
REPORT = TTS_DIR / "generation-report.json"
SPIKE = ROOT / "spikes/001-english-tts-engine-bakeoff"
sys.path.insert(0, str(SPIKE / "scripts"))

from runtime_provenance import (  # noqa: E402
    sha256,
    verified_model_snapshot,
    verify_environment,
    verify_system_fingerprints,
)


def run(command: list[str | Path]) -> None:
    subprocess.run([str(part) for part in command], check=True)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe_duration(path: Path) -> float:
    value = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        text=True,
    )
    return float(value.strip())


def synthesize(model, reference: Path, text: str, seed: int, profile: dict) -> tuple[np.ndarray, int, float]:
    settings = profile["generation"]["clone"]
    mx.random.seed(seed)
    started = time.perf_counter()
    results = list(
        model.generate(
            text=text,
            ref_audio=str(reference),
            ref_text=profile["identity"]["reference_text"],
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
        raise RuntimeError("Qwen3-TTS returned no audio")
    sample_rates = {item.sample_rate for item in results}
    if len(sample_rates) != 1:
        raise RuntimeError(f"inconsistent sample rates: {sample_rates}")
    audio = np.concatenate([np.asarray(item.audio, dtype=np.float32).reshape(-1) for item in results])
    if not np.isfinite(audio).all() or not np.any(np.abs(audio) > 1e-5):
        raise RuntimeError("Qwen3-TTS returned silent or non-finite audio")
    return audio, sample_rates.pop(), time.perf_counter() - started


def main() -> None:
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    config = json.loads(SCRIPT.read_text(encoding="utf-8"))
    reference = PROFILE_DIR / profile["identity"]["reference_audio"]
    if sha256(reference) != profile["identity"]["reference_sha256"]:
        raise RuntimeError("canonical narrator reference SHA-256 mismatch")

    environment = verify_environment(profile, SPIKE, "synthesis")
    fingerprints = verify_system_fingerprints(profile)
    snapshot, model_evidence = verified_model_snapshot(profile["models"]["voice_clone"])
    RAW.mkdir(parents=True, exist_ok=True)
    FINAL.mkdir(parents=True, exist_ok=True)

    load_started = time.perf_counter()
    model = load_model(str(snapshot))
    load_seconds = time.perf_counter() - load_started
    base_seed = int(profile["generation"]["seed"])
    settings = profile["generation"]["clone"]
    batch_started = time.perf_counter()
    rows: list[dict] = []

    for index, scene in enumerate(config["scenes"]):
        scene_id = scene["id"]
        text = scene["narration"]
        seed = base_seed + index
        raw = RAW / f"{scene_id}.wav"
        cache_meta = RAW / f"{scene_id}.json"
        cache_key = {
            "text": text,
            "seed": seed,
            "reference_sha256": profile["identity"]["reference_sha256"],
            "model_revision": model_evidence["resolved_revision"],
            "generation": settings,
        }
        cache_hit = raw.is_file() and cache_meta.is_file() and json.loads(cache_meta.read_text()) == cache_key
        if cache_hit:
            info = sf.info(raw)
            raw_seconds = info.frames / info.samplerate
            sample_rate = info.samplerate
            synthesis_seconds = 0.0
        else:
            audio, sample_rate, synthesis_seconds = synthesize(model, reference, text, seed, profile)
            sf.write(raw, audio, sample_rate, subtype="PCM_16")
            cache_meta.write_text(json.dumps(cache_key, indent=2) + "\n", encoding="utf-8")
            raw_seconds = len(audio) / sample_rate
        if raw_seconds < 0.15 or raw_seconds > 35:
            raise RuntimeError(f"pathological duration for {scene_id}: {raw_seconds:.3f}s")

        final = FINAL / f"{scene_id}.wav"
        fade_out_start = max(0.0, raw_seconds - 0.025)
        run([
            "ffmpeg", "-y", "-v", "error", "-i", raw,
            "-af",
            ",".join([
                "highpass=f=65",
                "acompressor=threshold=0.1:ratio=4:attack=5:release=100:makeup=1",
                "loudnorm=I=-16:TP=-1.5:LRA=8",
                "afade=t=in:st=0:d=0.015",
                f"afade=t=out:st={fade_out_start:.6f}:d=0.025",
                "apad=pad_dur=0.18",
            ]),
            "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", final,
        ])
        final_seconds = probe_duration(final)
        row = {
            "id": scene_id,
            "chapter": scene["chapter"],
            "text": text,
            "seed": seed,
            "sample_rate": sample_rate,
            "raw_seconds": round(raw_seconds, 4),
            "final_seconds": round(final_seconds, 4),
            "pause_seconds": round(final_seconds - raw_seconds, 4),
            "synthesis_seconds": round(synthesis_seconds, 4),
            "cache_hit": cache_hit,
            "raw_sha256": file_sha256(raw),
            "final_sha256": file_sha256(final),
        }
        rows.append(row)
        print(json.dumps({"id": scene_id, "raw_seconds": row["raw_seconds"], "final_seconds": row["final_seconds"], "cache_hit": cache_hit}), flush=True)

    report = {
        "profile": profile["id"],
        "reference_sha256": profile["identity"]["reference_sha256"],
        "model": model_evidence,
        "environment": environment,
        "system_fingerprints": fingerprints,
        "load_seconds": round(load_seconds, 4),
        "batch_seconds": round(time.perf_counter() - batch_started, 4),
        "total_narration_seconds": round(sum(row["final_seconds"] for row in rows), 4),
        "segments": rows,
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(REPORT)


if __name__ == "__main__":
    main()
