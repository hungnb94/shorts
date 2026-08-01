#!/usr/bin/env python3
"""Generate canonical Qwen narration for HardKnocks V24."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import mlx.core as mx
import numpy as np
import soundfile as sf
from mlx_audio.tts.utils import load_model  # pyright: ignore[reportMissingImports]

ROOT = Path(__file__).resolve().parents[2]
PROFILE_DIR = ROOT / "data" / "narrator-voices" / "ronald_wayne_zack_style_qwen"
PROFILE_PATH = PROFILE_DIR / "profile.json"
REFERENCE = PROFILE_DIR / "reference.wav"
WORK = ROOT / "output" / "projects" / "hardknocks" / "clips" / "v24_gave_away_90_work" / "audio" / "qwen-zack"
RAW = WORK / "raw"
REPORT = WORK / "generation-report.json"
SPIKE = ROOT / "spikes" / "001-english-tts-engine-bakeoff"
sys.path.insert(0, str(SPIKE / "scripts"))

from runtime_provenance import (  # noqa: E402  # pyright: ignore[reportMissingImports]
    sha256,
    verified_model_snapshot,
    verify_environment,
    verify_system_fingerprints,
)


@dataclass(frozen=True)
class Clip:
    clip_id: str
    text: str
    slot: float


CLIPS = (
    Clip(
        "fact_check",
        "But the headline hides the deal: nine hundred fifty million upfront, plus up to five hundred fifty million only if growth targets hit.",
        6.70,
    ),
    Clip(
        "triple_cta_v2",
        "Like for more. Subscribe. Comment: keep or scale?",
        4.00,
    ),
    Clip(
        "loop_closure",
        "He traded control for the team that made the larger outcome possible.",
        4.40,
    ),
)


def run(command: list[str | Path]) -> None:
    subprocess.run([str(item) for item in command], check=True)


def duration(path: Path) -> float:
    value = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        text=True,
    )
    return float(value.strip())


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
    rates = {item.sample_rate for item in results}
    if len(rates) != 1:
        raise RuntimeError(f"Inconsistent sample rates: {rates}")
    audio = np.concatenate([np.asarray(item.audio, dtype=np.float32).reshape(-1) for item in results])
    if not np.isfinite(audio).all() or not np.any(np.abs(audio) > 1e-5):
        raise RuntimeError("Qwen3-TTS returned silent or non-finite audio")
    return audio, rates.pop(), time.perf_counter() - started


def main() -> None:
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    if sha256(REFERENCE) != profile["identity"]["reference_sha256"]:
        raise RuntimeError("Narrator reference SHA-256 mismatch")
    environment = verify_environment(profile, SPIKE, "synthesis")
    fingerprints = verify_system_fingerprints(profile)
    snapshot, model_evidence = verified_model_snapshot(profile["models"]["voice_clone"])
    WORK.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    model = load_model(str(snapshot))
    settings = profile["generation"]["clone"]
    max_post_tempo = float(settings["max_post_tempo"])
    base_seed = int(profile["generation"]["seed"]) + 2400
    rows: list[dict[str, object]] = []

    for index, clip in enumerate(CLIPS):
        seed = base_seed + index
        raw = RAW / f"{clip.clip_id}.wav"
        if raw.is_file():
            info = sf.info(raw)
            sample_rate = info.samplerate
            raw_seconds = info.frames / info.samplerate
            synthesis_seconds = 0.0
        else:
            audio, sample_rate, synthesis_seconds = synthesize(model, clip.text, seed, profile)
            sf.write(raw, audio, sample_rate, subtype="PCM_16")
            raw_seconds = len(audio) / sample_rate
        speed = max(1.0, raw_seconds / max(clip.slot - 0.06, 0.1))
        if speed > max_post_tempo:
            raise RuntimeError(f"{clip.clip_id} requires {speed:.4f}x post-tempo; maximum is {max_post_tempo:.4f}x")
        fit_source = raw
        tempo_engine = "none"
        if speed > 1.001:
            stretched = WORK / f"{clip.clip_id}-stretched.wav"
            run(["rubberband", "-q", "-3", "-F", "-T", f"{speed:.8f}", raw, stretched])
            fit_source = stretched
            tempo_engine = "Rubber Band R3 4.0.0"
        fitted = WORK / f"{clip.clip_id}.wav"
        run([
            "ffmpeg", "-y", "-v", "error", "-i", fit_source,
            "-af", "highpass=f=65,acompressor=threshold=0.12:ratio=2.5:attack=5:release=90:makeup=1,"
            f"loudnorm=I=-16:TP=-1.5:LRA=8,aresample=48000,apad=whole_dur={clip.slot},atrim=0:{clip.slot}",
            "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", fitted,
        ])
        rows.append({
            "id": clip.clip_id,
            "text": clip.text,
            "seed": seed,
            "raw_seconds": round(raw_seconds, 4),
            "slot_seconds": clip.slot,
            "atempo": round(speed, 5),
            "tempo_engine": tempo_engine,
            "fitted_seconds": round(duration(fitted), 4),
            "synthesis_seconds": round(synthesis_seconds, 4),
            "raw_sha256": file_sha256(raw),
            "fitted_sha256": file_sha256(fitted),
        })
        print(json.dumps(rows[-1]), flush=True)

    REPORT.write_text(json.dumps({
        "engine": "Qwen3-TTS BaseModel zero-shot clone",
        "profile_id": profile["id"],
        "publication_rights": profile["assignment"]["publication_rights"],
        "reference_sha256": profile["identity"]["reference_sha256"],
        "model": model_evidence,
        "environment": environment,
        "system_fingerprints": fingerprints,
        "settings": settings,
        "seed_policy": f"{base_seed} + stable V24 clip index",
        "segments": rows,
    }, indent=2) + "\n", encoding="utf-8")
    print(REPORT)


if __name__ == "__main__":
    main()
