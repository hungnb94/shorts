#!/usr/bin/env python3
import json
import re
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent


def dhash(image: Image.Image) -> np.ndarray:
    pixels = np.asarray(image.convert("L").resize((9, 8)))
    return (pixels[:, 1:] > pixels[:, :-1]).flatten()


def inspect_dir(name: str) -> list[dict]:
    files = sorted((ROOT / "frames" / name).glob("*.jpg"))
    rows = []
    previous_gray = None
    previous_hash = None

    for path in files:
        image = Image.open(path).convert("RGB")
        rgb = np.asarray(image)
        gray = np.asarray(image.convert("L"))
        red = rgb[:, :, 0].astype(np.int16)
        green = rgb[:, :, 1].astype(np.int16)
        blue = rgb[:, :, 2].astype(np.int16)
        spread = rgb.max(axis=2).astype(np.int16) - rgb.min(axis=2).astype(np.int16)
        skin = (
            (red > 95)
            & (green > 40)
            & (blue > 20)
            & (spread > 15)
            & (np.abs(red - green) > 15)
            & (red > green)
            & (green > blue)
        )
        current_hash = dhash(image)
        adjacent_mad = None
        hash_distance = None
        if previous_gray is not None:
            adjacent_mad = float(
                np.mean(np.abs(gray.astype(np.int16) - previous_gray.astype(np.int16)))
            )
            hash_distance = int(np.count_nonzero(current_hash != previous_hash))

        result = subprocess.run(
            ["/opt/homebrew/bin/tesseract", str(path), "stdout", "--psm", "6"],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        ocr = re.sub(r"\s+", " ", result.stdout).strip()
        rows.append(
            {
                "file": path.name,
                "width": image.width,
                "height": image.height,
                "mean_luma": round(float(gray.mean()), 2),
                "std_luma": round(float(gray.std()), 2),
                "skin_pct": round(float(skin.mean() * 100), 2),
                "adjacent_mad": None if adjacent_mad is None else round(adjacent_mad, 2),
                "dhash_hamming": hash_distance,
                "ocr": ocr[:500],
            }
        )
        previous_gray = gray
        previous_hash = current_hash

    return rows


report = {
    name: inspect_dir(name) for name in ("hook", "ai_workflow", "overview")
}
(ROOT / "frame-inspection.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
for name, rows in report.items():
    print(f"\n### {name}: {len(rows)} frames")
    for row in rows:
        print(
            row["file"],
            "skin=", row["skin_pct"],
            "mad=", row["adjacent_mad"],
            "hash=", row["dhash_hamming"],
            "ocr=", row["ocr"][:120],
        )
