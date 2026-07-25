#!/usr/bin/env python3
"""Generate project-specific Qwen3-TTS narration for Ronald Wayne v2.

Loads the pinned Qwen3-TTS Base 1.7B 6-bit model once, clones the bounded
project reference, writes deterministic per-segment raw/fitted WAVs, and fails
closed on model provenance, reference hash, pathological duration, or excessive
post-tempo. Final content recall is verified separately on the rendered MP4.
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
PROJECT = ROOT / "output" / "projects" / "ronaldwayne"
SCRIPT = PROJECT / "scripts" / "script-v2-qwen.json"
PROFILE_DIR = ROOT / "data" / "narrator-voices" / "ronald_wayne_zack_style_qwen"
PROFILE_PATH = PROFILE_DIR / "profile.json"
REFERENCE = PROFILE_DIR / "reference.wav"
RAW = PROJECT / "tts-qwen" / "raw"
FITTED = PROJECT / "tts-qwen" / "fitted"
REPORT = PROJECT / "tts-qwen" / "generation-report.json"
SPIKE = ROOT / "spikes" / "001-english-tts-engine-bakeoff"
sys.path.insert(0, str(SPIKE / "scripts"))

from runtime_provenance import (  # noqa: E402
    sha256,
    verified_model_snapshot,
    verify_environment,
    verify_system_fingerprints,
)


def run(cmd: list[str | Path]) -> None:
    subprocess.run([str(x) for x in cmd], check=True)


def duration(path: Path) -> float:
    value = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        text=True,
    )
    return float(value.strip())


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atempo_chain(speed: float) -> str:
    parts: list[float] = []
    while speed > 2.0:
        parts.append(2.0)
        speed /= 2.0
    while speed < 0.5:
        parts.append(0.5)
        speed /= 0.5
    parts.append(speed)
    return ",".join(f"atempo={value:.6f}" for value in parts)


def synthesize(model, text: str, seed: int, profile: dict) -> tuple[np.ndarray, int, float]:
    settings = profile["generation"]["clone"]
    mx.random.seed(seed)
    started = time.perf_counter()
    results = list(
        model.generate(
            text=text,
            ref_audio=str(REFERENCE),
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
        raise RuntimeError(f"Qwen3-TTS returned inconsistent sample rates: {sample_rates}")
    audio = np.concatenate(
        [np.asarray(item.audio, dtype=np.float32).reshape(-1) for item in results]
    )
    if not np.isfinite(audio).all() or not np.any(np.abs(audio) > 1e-5):
        raise RuntimeError("Qwen3-TTS returned silent or non-finite audio")
    return audio, sample_rates.pop(), time.perf_counter() - started


def main() -> None:
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    config = json.loads(SCRIPT.read_text(encoding="utf-8"))
    if sha256(REFERENCE) != profile["identity"]["reference_sha256"]:
        raise RuntimeError("Project reference SHA-256 mismatch")
    environment = verify_environment(profile, SPIKE, "synthesis")
    fingerprints = verify_system_fingerprints(profile)
    snapshot, model_evidence = verified_model_snapshot(profile["models"]["voice_clone"])

    RAW.mkdir(parents=True, exist_ok=True)
    FITTED.mkdir(parents=True, exist_ok=True)

    started_batch = time.perf_counter()
    started_load = time.perf_counter()
    model = load_model(str(snapshot))
    load_seconds = time.perf_counter() - started_load
    settings = profile["generation"]["clone"]
    max_post_tempo = float(settings["max_post_tempo"])
    base_seed = int(profile["generation"]["seed"])
    rows = []
    violations = []

    tts_segments = [segment for segment in config["segments"] if segment["type"] == "tts"]
    for index, segment in enumerate(tts_segments):
        seed = base_seed + index
        raw = RAW / f"{segment['id']}.wav"
        cache_meta = RAW / f"{segment['id']}.json"
        cache_key = {
            "text": segment["text"],
            "seed": seed,
            "reference_sha256": profile["identity"]["reference_sha256"],
            "model_revision": model_evidence["resolved_revision"],
            "generation": {
                key: value
                for key, value in settings.items()
                if key not in {"max_post_tempo", "post_tempo_engine"}
            },
        }
        cache_hit = False
        if raw.is_file() and cache_meta.is_file():
            cached = json.loads(cache_meta.read_text(encoding="utf-8"))
            cache_hit = cached == cache_key
        if cache_hit:
            info = sf.info(raw)
            sample_rate = info.samplerate
            raw_seconds = info.frames / info.samplerate
            synthesis_seconds = 0.0
        else:
            audio, sample_rate, synthesis_seconds = synthesize(
                model, segment["text"], seed, profile
            )
            sf.write(raw, audio, sample_rate, subtype="PCM_16")
            cache_meta.write_text(json.dumps(cache_key, indent=2) + "\n", encoding="utf-8")
            raw_seconds = len(audio) / sample_rate
        slot = float(segment["end"] - segment["start"])
        speed = max(1.0, raw_seconds / max(slot - 0.06, 0.1))
        if raw_seconds > slot * 2.0:
            raise RuntimeError(
                f"{segment['id']} pathological duration {raw_seconds:.3f}s for {slot:.3f}s slot"
            )
        if speed > max_post_tempo:
            fitted = FITTED / f"{segment['id']}.wav"
            if fitted.exists():
                fitted.unlink()
            violation = {
                "id": segment["id"],
                "text": segment["text"],
                "seed": seed,
                "raw_seconds": round(raw_seconds, 4),
                "slot_seconds": slot,
                "required_atempo": round(speed, 5),
                "maximum_atempo": max_post_tempo,
                "cache_hit": cache_hit,
            }
            rows.append({**violation, "status": "duration_violation"})
            violations.append(violation)
            print(json.dumps(rows[-1], ensure_ascii=False), flush=True)
            continue

        fitted = FITTED / f"{segment['id']}.wav"
        fit_source = raw
        stretch_engine = "none"
        if speed > 1.001:
            stretched = FITTED / f"{segment['id']}-stretched.wav"
            run(
                [
                    "rubberband",
                    "-q",
                    "-3",
                    "-F",
                    "-T",
                    f"{speed:.8f}",
                    raw,
                    stretched,
                ]
            )
            fit_source = stretched
            stretch_engine = "Rubber Band R3 4.0.0"
        filters = [
            "highpass=f=65",
            "acompressor=threshold=0.12:ratio=2.5:attack=5:release=90:makeup=1",
            "loudnorm=I=-16:TP=-1.5:LRA=8",
            "aresample=48000",
            f"apad=whole_dur={slot}",
            f"atrim=0:{slot}",
        ]
        run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-i",
                fit_source,
                "-af",
                ",".join(filters),
                "-ar",
                "48000",
                "-ac",
                "2",
                "-c:a",
                "pcm_s16le",
                fitted,
            ]
        )
        rows.append(
            {
                "id": segment["id"],
                "text": segment["text"],
                "seed": seed,
                "sample_rate": sample_rate,
                "raw_seconds": round(raw_seconds, 4),
                "slot_seconds": slot,
                "atempo": round(speed, 5),
                "tempo_engine": stretch_engine,
                "fitted_seconds": round(duration(fitted), 4),
                "synthesis_seconds": round(synthesis_seconds, 4),
                "cache_hit": cache_hit,
                "raw_sha256": file_sha256(raw),
                "fitted_sha256": file_sha256(fitted),
                "status": "fitted",
            }
        )
        print(json.dumps(rows[-1], ensure_ascii=False), flush=True)

    report = {
        "engine": "Qwen3-TTS BaseModel zero-shot clone",
        "profile_id": profile["id"],
        "reference_sha256": profile["identity"]["reference_sha256"],
        "model": model_evidence,
        "environment": environment,
        "system_fingerprints": fingerprints,
        "settings": settings,
        "seed_policy": f"{base_seed} + stable TTS segment index",
        "load_seconds": round(load_seconds, 4),
        "batch_seconds": round(time.perf_counter() - started_batch, 4),
        "segments": rows,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    if violations:
        raise RuntimeError(
            "Qwen duration violations: "
            + ", ".join(
                f"{item['id']}={item['required_atempo']:.4f}x" for item in violations
            )
        )
    print(json.dumps({"report": str(REPORT), "segments": len(rows)}, indent=2))


if __name__ == "__main__":
    main()
