#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[6]
VIDEO = ROOT / "output/projects/hardknocks/source/xv8qaYubDw4.mp4"
OUT = ROOT / "output/projects/hardknocks/clips/v14_theragun_work/research/frame_scan"
OUT.mkdir(parents=True, exist_ok=True)
FONT = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 28)


def frame_at(t: float, dst: Path) -> None:
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{t:.3f}", "-i", str(VIDEO), "-frames:v", "1",
        "-vf", "scale=480:-2", str(dst),
    ], check=True)


def sheet(name: str, times: list[float], cols: int = 4) -> None:
    cells = []
    for i, t in enumerate(times):
        p = OUT / f"{name}_{i:02d}_{t:.2f}.jpg"
        frame_at(t, p)
        img = Image.open(p).convert("RGB")
        canvas = Image.new("RGB", (480, img.height + 48), "black")
        canvas.paste(img, (0, 48))
        ImageDraw.Draw(canvas).text((12, 8), f"t={t:.2f}s", font=FONT, fill="yellow")
        cells.append(canvas)
    rows = (len(cells) + cols - 1) // cols
    out = Image.new("RGB", (cols * 480, rows * cells[0].height), (20, 20, 20))
    for i, cell in enumerate(cells):
        out.paste(cell, ((i % cols) * 480, (i // cols) * cell.height))
    out.save(OUT / f"{name}.jpg", quality=92)


sheet("intro_0_300", [float(t) for t in range(0, 301, 20)])
sheet("prototype_300_720", [float(t) for t in range(300, 721, 20)])
sheet("chapters", [0, 66, 575, 1130, 1447, 1906, 2107, 2615, 3157, 3597, 3901, 4241])
scene_times = [
    float(line) + 0.20
    for line in (OUT.parent / "scene_030_times.txt").read_text().splitlines()
    if float(line) <= 66.0
]
sheet("intro_scene_cuts", scene_times)
for hook_name, hook_start in {
    "hook_crash": 17.68,
    "hook_jigsaw_clinic": 671.66,
    "hook_saved_life": 792.86,
    "hook_250_jigsaws": 908.86,
    "hook_dad_crazy": 1087.44,
}.items():
    sheet(hook_name, [hook_start + i * 0.5 for i in range(9)], cols=3)
print(OUT)
