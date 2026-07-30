#!/usr/bin/env python3
"""Generate HardKnocks V21 narration with the canonical Finance Qwen voice.

The script verifies the canonical synthetic reference and pinned Base ICL model,
loads the model once, generates bounded semantic passages, then uses Rubber Band
only when speech must fit the locked visual slot. No Edge TTS is used.
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
WORK = ROOT / "output" / "projects" / "hardknocks" / "clips" / "v21_buy_dont_build_work"
AUDIO = WORK / "audio"
PROFILE_DIR = ROOT / "data" / "narrator-voices" / "natural_talker_male_qwen_blog"
PROFILE_PATH = PROFILE_DIR / "profile.json"
REFERENCE = PROFILE_DIR / "reference.wav"
RAW = AUDIO / "qwen" / "raw"
REPORT = AUDIO / "qwen" / "generation-report.json"
SPIKE = ROOT / "spikes" / "001-english-tts-engine-bakeoff"
sys.path.insert(0, str(SPIKE / "scripts"))

from runtime_provenance import (  # noqa: E402
    sha256,
    verified_model_snapshot,
    verify_environment,
    verify_system_fingerprints,
)

SEGMENTS = (
    {
        "id": "factcheck",
        "text": "Not free money. Lenders test repayment, and may require buyer equity and a personal guarantee.",
        "slot": 6.60,
        "output": AUDIO / "factcheck.wav",
    },
    {
        "id": "cta",
        "text": "Like and subscribe. Then comment: build or buy?",
        "slot": 4.10,
        "output": AUDIO / "cta.wav",
    },
)
MAX_POST_TEMPO = 1.22


def run(command: list[str | Path]) -> None:
    subprocess.run([str(item) for item in command], check=True)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def duration(path: Path) -> float:
    return float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(path),
    ], text=True).strip())


def synthesize(model, text: str, seed: int, profile: dict) -> tuple[np.ndarray, int, float]:
    settings = profile["generation"]["clone"]
    mx.random.seed(seed)
    started = time.perf_counter()
    results = list(model.generate(
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
    ))
    if not results:
        raise RuntimeError("Qwen3-TTS returned no audio")
    sample_rates = {item.sample_rate for item in results}
    if len(sample_rates) != 1:
        raise RuntimeError(f"Qwen3-TTS returned inconsistent sample rates: {sample_rates}")
    audio = np.concatenate([np.asarray(item.audio, dtype=np.float32).reshape(-1) for item in results])
    if not np.isfinite(audio).all() or not np.any(np.abs(audio) > 1e-5):
        raise RuntimeError("Qwen3-TTS returned silent or non-finite audio")
    return audio, sample_rates.pop(), time.perf_counter() - started


def main() -> None:
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    if profile["id"] != "natural_talker_male_qwen_blog" or profile["status"] != "canonical":
        raise RuntimeError("Wrong or non-canonical Finance narrator profile")
    if sha256(REFERENCE) != profile["identity"]["reference_sha256"]:
        raise RuntimeError("Canonical narrator reference SHA-256 mismatch")

    environment = verify_environment(profile, SPIKE, "synthesis")
    fingerprints = verify_system_fingerprints(profile)
    snapshot, model_evidence = verified_model_snapshot(profile["models"]["voice_clone"])
    RAW.mkdir(parents=True, exist_ok=True)
    AUDIO.mkdir(parents=True, exist_ok=True)

    started_batch = time.perf_counter()
    started_load = time.perf_counter()
    model = load_model(str(snapshot))
    load_seconds = time.perf_counter() - started_load
    settings = profile["generation"]["clone"]
    base_seed = int(profile["generation"]["seed"])
    rows = []

    for index, segment in enumerate(SEGMENTS):
        seed = base_seed + index
        raw = RAW / f"{segment['id']}.wav"
        raw_meta = RAW / f"{segment['id']}.json"
        cache_key = {
            "text": segment["text"],
            "seed": seed,
            "reference_sha256": profile["identity"]["reference_sha256"],
            "model_revision": model_evidence["resolved_revision"],
            "generation": settings,
        }
        cache_hit = raw.is_file() and raw_meta.is_file() and json.loads(raw_meta.read_text()) == cache_key
        if cache_hit:
            info = sf.info(raw)
            sample_rate = info.samplerate
            raw_seconds = info.frames / info.samplerate
            synthesis_seconds = 0.0
        else:
            audio, sample_rate, synthesis_seconds = synthesize(model, segment["text"], seed, profile)
            sf.write(raw, audio, sample_rate, subtype="PCM_16")
            raw_meta.write_text(json.dumps(cache_key, indent=2) + "\n", encoding="utf-8")
            raw_seconds = len(audio) / sample_rate

        slot = float(segment["slot"])
        speed = max(1.0, raw_seconds / max(slot - 0.08, 0.1))
        if speed > MAX_POST_TEMPO:
            raise RuntimeError(
                f"{segment['id']} needs {speed:.4f}x tempo, above {MAX_POST_TEMPO:.2f}x; shorten copy first"
            )
        fit_source = raw
        tempo_engine = "none"
        if speed > 1.001:
            stretched = RAW / f"{segment['id']}-stretched.wav"
            run(["rubberband", "-q", "-3", "-F", "-T", f"{speed:.8f}", raw, stretched])
            fit_source = stretched
            tempo_engine = "Rubber Band R3 4.0.0"

        output = Path(segment["output"])
        run([
            "ffmpeg", "-y", "-v", "error", "-i", fit_source,
            "-af", ",".join([
                "highpass=f=65",
                "acompressor=threshold=0.12:ratio=2.5:attack=5:release=90:makeup=1",
                "loudnorm=I=-16:TP=-1.5:LRA=8",
                "aresample=48000",
                f"apad=whole_dur={slot}",
                f"atrim=0:{slot}",
            ]),
            "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", output,
        ])
        rows.append({
            "id": segment["id"],
            "text": segment["text"],
            "seed": seed,
            "sample_rate": sample_rate,
            "raw_seconds": round(raw_seconds, 4),
            "slot_seconds": slot,
            "required_tempo": round(speed, 5),
            "tempo_engine": tempo_engine,
            "fitted_seconds": round(duration(output), 4),
            "synthesis_seconds": round(synthesis_seconds, 4),
            "cache_hit": cache_hit,
            "raw_sha256": file_sha256(raw),
            "fitted_sha256": file_sha256(output),
        })
        print(json.dumps(rows[-1], ensure_ascii=False), flush=True)

    report = {
        "engine": "Qwen3-TTS BaseModel zero-shot clone",
        "profile_id": profile["id"],
        "reference_sha256": profile["identity"]["reference_sha256"],
        "model": model_evidence,
        "environment": environment,
        "system_fingerprints": fingerprints,
        "seed_policy": f"{base_seed} + stable V21 segment index",
        "maximum_post_tempo": MAX_POST_TEMPO,
        "load_seconds": round(load_seconds, 4),
        "batch_seconds": round(time.perf_counter() - started_batch, 4),
        "segments": rows,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(REPORT), "segments": len(rows)}, indent=2))


if __name__ == "__main__":
    main()
