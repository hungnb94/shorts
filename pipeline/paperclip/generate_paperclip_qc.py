#!/usr/bin/env python3
"""Generate visual QC evidence for paperclip_v1 from the final MP4."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "paperclip"
VIDEO = PROJECT / "2026-07-26-one-red-paperclip-v1-internal.mp4"
EDL = PROJECT / "scripts" / "visual-edl-v1.json"
CHECKS = PROJECT / "checks-v1"
BEAT_FRAMES = CHECKS / "beat-frames"
REVEAL_FRAMES = CHECKS / "caption-reveal-frames"
PAYOFF_FRAMES = CHECKS / "payoff-frames"
FONT = ROOT / "assets" / "fonts" / "Komika-Axis.ttf"
FPS = 30


def extract(time_value: float, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(VIDEO),
            "-ss",
            f"{max(0.0, time_value):.6f}",
            "-frames:v",
            "1",
            "-vf",
            "scale=270:480:flags=lanczos",
            str(output),
        ],
        check=True,
    )


def sheet(items: list[tuple[Path, str]], columns: int, output: Path) -> None:
    thumb_w, thumb_h, label_h, gap = 270, 480, 64, 10
    rows = (len(items) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * (thumb_w + gap) + gap, rows * (thumb_h + label_h + gap) + gap), (5, 7, 13))
    draw = ImageDraw.Draw(canvas)
    label_font = ImageFont.truetype(str(FONT), 22)
    for index, (path, label) in enumerate(items):
        row, column = divmod(index, columns)
        x = gap + column * (thumb_w + gap)
        y = gap + row * (thumb_h + label_h + gap)
        image = Image.open(path).convert("RGB")
        canvas.paste(image, (x, y))
        clean = label.replace("→", ">").replace("•", "/").replace("—", "-")
        draw.text((x + 4, y + thumb_h + 8), clean[:32], font=label_font, fill=(248, 250, 252))
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, quality=92)


def main() -> None:
    if not VIDEO.is_file():
        raise FileNotFoundError(VIDEO)
    edl = json.loads(EDL.read_text(encoding="utf-8"))

    beat_items: list[tuple[Path, str]] = []
    for index, beat in enumerate(edl["beats"]):
        sample = min(float(beat["end"]) - 1 / FPS, float(beat["start"]) + max(0.15, float(beat["duration"]) * 0.55))
        path = BEAT_FRAMES / f"{index:02d}-{beat['id']}.jpg"
        extract(sample, path)
        beat_items.append((path, f"{index:02d} {beat['start']:.1f}s {beat['title']}"))
    sheet(beat_items, 5, CHECKS / "contact-sheet-20-beats.jpg")

    seen: set[tuple[float, str]] = set()
    reveal_items: list[tuple[Path, str]] = []
    for beat in edl["beats"]:
        caption = beat.get("caption")
        if not caption:
            continue
        key = (float(caption["caption_at"]), caption["text"])
        if key in seen:
            continue
        seen.add(key)
        at = float(caption["caption_at"])
        before = max(0.0, at - 2 / FPS)
        after = min(float(edl["duration"]) - 1 / FPS, at + 1 / FPS)
        safe_name = f"{len(reveal_items)//2:02d}"
        before_path = REVEAL_FRAMES / f"{safe_name}-before.jpg"
        after_path = REVEAL_FRAMES / f"{safe_name}-after.jpg"
        extract(before, before_path)
        extract(after, after_path)
        reveal_items.append((before_path, f"BEFORE {at:.2f} {caption['text']}"))
        reveal_items.append((after_path, f"AFTER {at:.2f} {caption['text']}"))
    sheet(reveal_items, 4, CHECKS / "caption-reveal-regression.jpg")

    payoff_items: list[tuple[Path, str]] = []
    for index, time_value in enumerate([45.70, 46.05, 48.95, 51.65, 52.55, 53.30, 59.20, 61.40]):
        path = PAYOFF_FRAMES / f"{index:02d}-{time_value:.2f}.jpg"
        extract(time_value, path)
        payoff_items.append((path, f"{time_value:.2f}s"))
    sheet(payoff_items, 4, CHECKS / "payoff-contact-sheet.jpg")
    print(json.dumps({"beat_frames": len(beat_items), "caption_pairs": len(reveal_items) // 2, "payoff_frames": len(payoff_items)}, indent=2))


if __name__ == "__main__":
    main()
