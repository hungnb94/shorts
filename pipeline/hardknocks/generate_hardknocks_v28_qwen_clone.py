#!/usr/bin/env python3
"""Generate canonical internal-only Qwen narration for HardKnocks V28."""

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
WORK = ROOT / "output" / "projects" / "hardknocks" / "clips" / "v28_equity_trap_work" / "audio" / "qwen-zack"
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
        "counter_audit",
        "He says the bank takes all the risk. But watch the first-loss math.",
        4.60,
    ),
    Clip(
        "capital_stack",
        "Ten-million-dollar property. Eight-million loan. Two-million buyer equity.",
        4.60,
    ),
    Clip(
        "value_shock",
        "If its value falls twenty percent, the property is worth eight million. The buyer's two million is gone.",
        6.40,
    ),
    Clip(
        "underwriting_guardrail",
        "But LTV is only one underwriting test. Lenders test cash flow, property risk, and debt service.",
        6.4,
    ),
    Clip(
        "maturity_wave",
        "Why this matters now: eight hundred seventy-five billion dollars of commercial mortgages mature in twenty twenty-six.",
        6.20,
    ),
    Clip(
        "triple_cta",
        "Would you use eighty percent debt? Like, subscribe, and comment.",
        4.0,
    ),
    Clip(
        "recourse_guardrail",
        "And recourse can reach other borrower assets. Federal Reserve research calls it shadow equity.",
        6.40,
    ),
    Clip(
        "first_loss_payoff",
        "So neither side takes all the risk. Equity absorbs the first hit. Then the bank takes the next loss.",
        7.0,
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
    base_seed = int(profile["generation"]["seed"]) + 2800
    rows: list[dict[str, object]] = []

    for index, clip in enumerate(CLIPS):
        seed = base_seed + index
        raw = RAW / f"{clip.clip_id}.wav"
        cache_meta = RAW / f"{clip.clip_id}.json"
        cache_key = {
            "text": clip.text,
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
            cache_hit = json.loads(cache_meta.read_text(encoding="utf-8")) == cache_key
        if cache_hit:
            info = sf.info(raw)
            sample_rate = info.samplerate
            raw_seconds = info.frames / info.samplerate
            synthesis_seconds = 0.0
        else:
            audio, sample_rate, synthesis_seconds = synthesize(model, clip.text, seed, profile)
            sf.write(raw, audio, sample_rate, subtype="PCM_16")
            cache_meta.write_text(json.dumps(cache_key, indent=2) + "\n", encoding="utf-8")
            raw_seconds = len(audio) / sample_rate
        speed = max(1.0, raw_seconds / max(clip.slot - 0.08, 0.1))
        if speed > max_post_tempo:
            raise RuntimeError(
                f"{clip.clip_id} requires {speed:.4f}x post-tempo; maximum is {max_post_tempo:.4f}x"
            )
        fit_source = raw
        tempo_engine = "none"
        if speed > 1.001:
            stretched = WORK / f"{clip.clip_id}-stretched.wav"
            run(["rubberband", "-q", "-3", "-F", "-T", f"{speed:.8f}", raw, stretched])
            fit_source = stretched
            tempo_engine = "Rubber Band R3 4.0.0"
        fitted = WORK / f"{clip.clip_id}.wav"
        samples = round(clip.slot * 48000)
        run(
            [
                "ffmpeg", "-y", "-v", "error", "-i", fit_source,
                "-af",
                "highpass=f=65,acompressor=threshold=0.12:ratio=2.5:attack=5:release=90:makeup=1,"
                f"loudnorm=I=-16:TP=-1.5:LRA=8,aresample=48000:first_pts=0,"
                f"apad=whole_len={samples},atrim=end_sample={samples}",
                "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", fitted,
            ]
        )
        fitted_seconds = duration(fitted)
        if abs(fitted_seconds - clip.slot) > (1 / 48000 + 0.001):
            raise RuntimeError(f"{clip.clip_id} fitted duration {fitted_seconds:.6f} != {clip.slot:.6f}")
        rows.append(
            {
                "id": clip.clip_id,
                "text": clip.text,
                "seed": seed,
                "raw_sample_rate": sample_rate,
                "raw_seconds": round(raw_seconds, 4),
                "slot_seconds": clip.slot,
                "post_tempo": round(speed, 5),
                "tempo_engine": tempo_engine,
                "fitted_seconds": round(fitted_seconds, 4),
                "synthesis_seconds": round(synthesis_seconds, 4),
                "cache_hit": cache_hit,
                "raw_sha256": file_sha256(raw),
                "fitted_sha256": file_sha256(fitted),
                "truncated": False,
            }
        )
        print(json.dumps(rows[-1]), flush=True)

    REPORT.write_text(
        json.dumps(
            {
                "engine": "Qwen3-TTS BaseModel zero-shot clone",
                "profile_id": profile["id"],
                "publication_rights": profile["assignment"]["publication_rights"],
                "reference_sha256": profile["identity"]["reference_sha256"],
                "model": model_evidence,
                "environment": environment,
                "system_fingerprints": fingerprints,
                "settings": settings,
                "seed_policy": f"{base_seed} + stable V28 clip index",
                "segments": rows,
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    print(REPORT)


if __name__ == "__main__":
    main()
