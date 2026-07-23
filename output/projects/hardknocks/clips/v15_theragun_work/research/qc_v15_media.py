#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[6]
FINAL = ROOT / "output" / "projects" / "hardknocks" / "final"
WORK = ROOT / "output" / "projects" / "hardknocks" / "clips" / "v15_theragun_work"
ITEMS = {
    "v15a": (
        FINAL / "2026-07-23-hardknocks_v15a_crash_created_theragun.mp4",
        [14, 25, 35, 46],
        43,
    ),
    "v15b": (
        FINAL / "2026-07-23-hardknocks_v15b_first_patient_to_athletes.mp4",
        [12, 22, 34, 49, 59],
        44,
    ),
}


def frame_at(video: Path, seconds: float, width: int = 270, height: int = 480) -> np.ndarray:
    result = subprocess.run(
        [
            "ffmpeg", "-v", "error", "-ss", f"{seconds:.3f}", "-i", str(video),
            "-frames:v", "1", "-vf",
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
            "-pix_fmt", "rgb24", "-f", "rawvideo", "-",
        ],
        check=True,
        capture_output=True,
    )
    return np.frombuffer(result.stdout, dtype=np.uint8).reshape(height, width, 3)


summary: dict[str, object] = {}
for key, (video, evidence_starts, cta_start) in ITEMS.items():
    checks = WORK / key / "checks"
    checks.mkdir(parents=True, exist_ok=True)
    detector_path = checks / "detectors.log"
    loudness_path = checks / "loudness.log"
    with detector_path.open("wb") as stderr:
        subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-i", str(video),
                "-vf", "blackdetect=d=0.20:pix_th=0.10,freezedetect=n=-50dB:d=1.0",
                "-af", "silencedetect=noise=-40dB:d=1.0", "-f", "null", "-",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=stderr,
        )
    with loudness_path.open("wb") as stderr:
        subprocess.run(
            ["ffmpeg", "-hide_banner", "-i", str(video), "-filter_complex", "ebur128=peak=true", "-f", "null", "-"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=stderr,
        )
    detector_text = detector_path.read_text(errors="replace")
    loudness_text = loudness_path.read_text(errors="replace")
    events = {
        name: len(re.findall(name, detector_text))
        for name in ("black_start", "freeze_start", "silence_start")
    }
    loudness = re.findall(r"I:\s+(-?[0-9.]+) LUFS", loudness_text)
    true_peak = re.findall(r"Peak:\s+(-?[0-9.]+) dBFS", loudness_text)

    raw = subprocess.run(
        [
            "ffmpeg", "-v", "error", "-i", str(video), "-t", "3",
            "-vf", "fps=10,scale=180:320", "-pix_fmt", "rgb24", "-f", "rawvideo", "-",
        ],
        check=True,
        capture_output=True,
    ).stdout
    frames = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 320, 180, 3)
    deltas = np.abs(frames[1:].astype(np.int16) - frames[:-1].astype(np.int16)).mean(axis=(1, 2, 3))
    red, green, blue = (frames[0, :, :, index] for index in range(3))
    skin = ((red > 95) & (green > 40) & (blue > 20) & ((red - green) > 15) & (red > blue)).mean() * 100
    run = max_run = 0
    for delta in deltas:
        run = run + 1 if delta <= 1.0 else 0
        max_run = max(max_run, run)

    times: list[tuple[float, str]] = []
    for raw_start in evidence_starts:
        final_start = raw_start / 1.06
        times.extend(
            [
                (final_start + 0.10, f"{raw_start} raw START"),
                (final_start + 1.75 / 1.06, f"{raw_start} raw MID"),
                ((raw_start + 3.40) / 1.06, f"{raw_start} raw END"),
            ]
        )
    times.append((cta_start / 1.06 + 1.0, f"CTA {cta_start} raw"))
    tiles: list[Image.Image] = []
    for seconds, label in times:
        image = Image.fromarray(frame_at(video, seconds))
        tile = Image.new("RGB", (280, 525), "#111111")
        tile.paste(image, (5, 35))
        ImageDraw.Draw(tile).text((8, 8), f"{seconds:.2f}s {label}", fill="yellow")
        tiles.append(tile)
    columns = 3
    rows = (len(tiles) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * 280, rows * 525), "#222222")
    for index, tile in enumerate(tiles):
        sheet.paste(tile, ((index % columns) * 280, (index // columns) * 525))
    sheet.save(checks / "evidence_and_cta.jpg", quality=92)

    summary[key] = {
        "detector_events": events,
        "loudness_lufs": loudness[-1] if loudness else None,
        "true_peak_dbfs": true_peak[-1] if true_peak else None,
        "skin_proxy_percent": round(float(skin), 2),
        "hook_motion": {
            "median_frame_delta": round(float(np.median(deltas)), 3),
            "minimum_frame_delta": round(float(np.min(deltas)), 3),
            "longest_static_run_seconds_below_delta_1": round(max_run / 10, 3),
        },
    }

(WORK / "qc_detector_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
