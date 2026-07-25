#!/usr/bin/env python3
"""Generate visual QC evidence for Ronald Wayne v3 synchronized captions."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output/projects/ronaldwayne"
VIDEO = PROJECT / "2026-07-25-ronald-wayne-v3-qwen-synced.mp4"
MANIFEST = PROJECT / "scripts/visual-edl-v3-qwen-synced.json"
CHECKS = PROJECT / "checks-v3-sync"
FRAMES = CHECKS / "frames"
FONT_PATH = ROOT / "assets/fonts/Komika-Axis.ttf"
CELL_W, CELL_H = 270, 480
LABEL_H = 62


def extract_frame(timestamp: float, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    beat_start = max(0.0, int((timestamp + 1e-6) / 1.5) * 1.5)
    local_time = max(0.0, timestamp - beat_start)
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error", "-ss", f"{beat_start:.6f}", "-i", str(VIDEO),
            "-ss", f"{local_time:.6f}", "-frames:v", "1",
            "-vf", f"scale={CELL_W}:{CELL_H}:flags=lanczos", str(output),
        ],
        check=True,
    )


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def labeled_cell(image_path: Path, label: str) -> Image.Image:
    cell = Image.new("RGB", (CELL_W, CELL_H + LABEL_H), (8, 11, 18))
    cell.paste(Image.open(image_path).convert("RGB"), (0, LABEL_H))
    draw = ImageDraw.Draw(cell)
    draw.text((10, 8), label, font=font(20), fill=(255, 203, 57))
    return cell


def sheet(items: list[tuple[Path, str]], columns: int, output: Path) -> None:
    rows = (len(items) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * CELL_W, rows * (CELL_H + LABEL_H)), (4, 6, 10))
    for index, (path, label) in enumerate(items):
        canvas.paste(labeled_cell(path, label), ((index % columns) * CELL_W, (index // columns) * (CELL_H + LABEL_H)))
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, quality=94)


def main() -> None:
    if not VIDEO.is_file() or not MANIFEST.is_file():
        raise FileNotFoundError(VIDEO if not VIDEO.is_file() else MANIFEST)
    beats = json.loads(MANIFEST.read_text(encoding="utf-8"))
    midpoint_items: list[tuple[Path, str]] = []
    for beat in beats:
        sample = min(beat["end"] - 0.10, max(beat["start"] + 0.75, beat["caption_at"] + 0.10))
        path = FRAMES / f"beat-{beat['index']:02d}.png"
        extract_frame(sample, path)
        midpoint_items.append((path, f"B{beat['index']:02d} {sample:.2f}s"))
    sheet(midpoint_items, 5, CHECKS / "contact-sheet-40-beats.jpg")

    ranges = [
        (8, 16, 3, "contact-sheet-risk-12-to-25_5s.jpg"),
        (21, 28, 4, "contact-sheet-identity-31_5-to-43_5s.jpg"),
        (29, 39, 4, "contact-sheet-payoff-43_5-to-60s.jpg"),
    ]
    for first, last, columns, name in ranges:
        sheet(midpoint_items[first : last + 1], columns, CHECKS / name)

    regression_items: list[tuple[Path, str]] = []
    for index in (2, 5, 8, 11, 16, 22, 32, 33, 36, 39):
        beat = beats[index]
        delay = beat["caption_delay"]
        if delay <= 0:
            continue
        frame = 1 / 30
        before_t = max(beat["start"], beat["caption_at"] - 2 * frame)
        after_t = min(beat["end"] - 0.001, beat["caption_at"] + frame)
        before = FRAMES / f"reveal-{index:02d}-before.png"
        after = FRAMES / f"reveal-{index:02d}-after.png"
        extract_frame(before_t, before)
        extract_frame(after_t, after)
        regression_items.extend(
            [
                (before, f"B{index:02d} BEFORE {before_t:.3f}"),
                (after, f"B{index:02d} AFTER {after_t:.3f}"),
            ]
        )
    sheet(regression_items, 4, CHECKS / "caption-reveal-regression.jpg")
    print(f"generated {len(midpoint_items)} beat frames and {len(regression_items)} reveal frames")


if __name__ == "__main__":
    main()
