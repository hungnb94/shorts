#!/usr/bin/env python3
"""Generate deterministic, rights-clear sonic assets for HardKnocks V22.

Every sound is synthesized from NumPy primitives. There are no sampled or
third-party audio inputs. Asset metadata is promoted into assets/sfx/manifest.json
after real-file audition and probing.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "sfx" / "generated" / "hardknocks_v22"
SR = 48_000
SEED = 20260730


def smooth_noise(rng: np.random.Generator, count: int, width: int) -> np.ndarray:
    noise = rng.standard_normal(count + width - 1)
    kernel = np.ones(width, dtype=np.float64) / width
    return np.convolve(noise, kernel, mode="valid")


def envelope(count: int, attack: float, release: float) -> np.ndarray:
    env = np.ones(count, dtype=np.float64)
    attack_n = min(count, max(1, round(attack * SR)))
    release_n = min(count, max(1, round(release * SR)))
    env[:attack_n] = np.sin(np.linspace(0, np.pi / 2, attack_n)) ** 2
    env[-release_n:] *= np.cos(np.linspace(0, np.pi / 2, release_n)) ** 2
    return env


def stereo(mono: np.ndarray, pan: np.ndarray | float = 0.0) -> np.ndarray:
    pan_array = np.asarray(pan, dtype=np.float64)
    left = mono * np.sqrt((1.0 - pan_array) / 2.0)
    right = mono * np.sqrt((1.0 + pan_array) / 2.0)
    return np.column_stack((left, right))


def peak_limit(audio: np.ndarray, peak: float = 0.48) -> np.ndarray:
    maximum = float(np.max(np.abs(audio)))
    if maximum > 0:
        audio = audio * (peak / maximum)
    return np.asarray(audio, dtype=np.float32)


def hook_origin_hit(rng: np.random.Generator) -> np.ndarray:
    duration = 0.42
    t = np.arange(round(duration * SR)) / SR
    metal = (np.sin(2 * np.pi * 1320 * t) + 0.55 * np.sin(2 * np.pi * 1980 * t))
    metal *= np.exp(-t * 20)
    sub = np.sin(2 * np.pi * (82 - 32 * t) * t) * np.exp(-t * 12)
    transient = smooth_noise(rng, len(t), 5) * np.exp(-t * 55)
    return peak_limit(stereo((0.38 * metal + 0.62 * sub + 0.18 * transient) * envelope(len(t), 0.004, 0.15)), 0.42)


def jet_motion_whoosh(rng: np.random.Generator) -> np.ndarray:
    duration = 0.92
    t = np.arange(round(duration * SR)) / SR
    raw = rng.standard_normal(len(t))
    low = smooth_noise(rng, len(t), 23)
    brightness = np.linspace(0.08, 0.72, len(t))
    body = (brightness * raw + (1 - brightness) * low) * np.sin(np.pi * t / duration) ** 1.6
    pitch = np.sin(2 * np.pi * (75 + 120 * t / duration) * t) * np.sin(np.pi * t / duration)
    pan = np.linspace(-0.7, 0.55, len(t))
    return peak_limit(stereo(0.42 * body + 0.16 * pitch, pan), 0.38)


def proof_tick() -> np.ndarray:
    duration = 0.34
    t = np.arange(round(duration * SR)) / SR
    tone = np.sin(2 * np.pi * 920 * t) + 0.5 * np.sin(2 * np.pi * 1380 * t)
    tone *= np.exp(-t * 18)
    return peak_limit(stereo(tone * envelope(len(t), 0.003, 0.12), 0.10), 0.34)


def cta_click(rng: np.random.Generator) -> np.ndarray:
    duration = 0.18
    t = np.arange(round(duration * SR)) / SR
    click = smooth_noise(rng, len(t), 3) * np.exp(-t * 75)
    body = np.sin(2 * np.pi * 520 * t) * np.exp(-t * 30)
    return peak_limit(stereo(0.72 * click + 0.28 * body), 0.30)


def payoff_warm_hit(rng: np.random.Generator) -> np.ndarray:
    duration = 1.10
    t = np.arange(round(duration * SR)) / SR
    low = np.sin(2 * np.pi * (70 - 24 * t) * t) * np.exp(-t * 4.0)
    warmth = np.sin(2 * np.pi * 147 * t) * np.exp(-t * 5.6)
    air = smooth_noise(rng, len(t), 31) * np.exp(-t * 7.5)
    return peak_limit(stereo((0.68 * low + 0.22 * warmth + 0.10 * air) * envelope(len(t), 0.008, 0.35)), 0.40)


def restrained_bed(rng: np.random.Generator) -> np.ndarray:
    duration = 70.0
    t = np.arange(round(duration * SR)) / SR
    chords = [(73.42, 110.00, 146.83), (65.41, 98.00, 130.81), (82.41, 123.47, 164.81), (73.42, 110.00, 146.83)]
    bed = np.zeros_like(t)
    chord_len = duration / len(chords)
    for index, frequencies in enumerate(chords):
        start = round(index * chord_len * SR)
        end = round((index + 1) * chord_len * SR)
        local_t = t[start:end] - t[start]
        local = np.sum(
            np.stack([np.sin(2 * np.pi * f * local_t + index * 0.7) for f in frequencies]),
            axis=0,
        ) / len(frequencies)
        local *= envelope(len(local), 1.5, 1.5)
        bed[start:end] += local
    pulse = (0.5 + 0.5 * np.sin(2 * np.pi * 0.42 * t - np.pi / 2)) ** 5
    low_pulse = np.sin(2 * np.pi * 55 * t) * pulse
    air = smooth_noise(rng, len(t), 301)
    air /= max(1e-9, float(np.max(np.abs(air))))
    mono = 0.052 * bed + 0.018 * low_pulse + 0.009 * air
    pan = 0.12 * np.sin(2 * np.pi * 0.035 * t)
    return peak_limit(stereo(mono, pan), 0.11)


GENERATORS = {
    "hook_origin_hit.wav": hook_origin_hit,
    "jet_motion_whoosh.wav": jet_motion_whoosh,
    "proof_tick.wav": lambda _rng: proof_tick(),
    "cta_click.wav": cta_click,
    "payoff_warm_hit.wav": payoff_warm_hit,
    "restrained_finance_bed.wav": restrained_bed,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for index, (name, generator) in enumerate(GENERATORS.items()):
        rng = np.random.default_rng(SEED + index)
        audio = generator(rng)
        path = OUT / name
        sf.write(path, audio, SR, subtype="PCM_16")
        rows.append({
            "path": str(path.relative_to(ROOT)),
            "duration_s": round(len(audio) / SR, 6),
            "sample_rate_hz": SR,
            "channels": int(audio.shape[1]),
            "peak": round(float(np.max(np.abs(audio))), 6),
            "sha256": sha256(path),
            "seed": SEED + index,
        })
    report = OUT / "generation-report.json"
    report.write_text(json.dumps({"generator": str(Path(__file__).relative_to(ROOT)), "assets": rows}, indent=2) + "\n")
    print(json.dumps({"report": str(report), "assets": rows}, indent=2))


if __name__ == "__main__":
    main()
