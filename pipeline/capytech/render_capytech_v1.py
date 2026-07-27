#!/usr/bin/env python3
"""Render Capytech v1: Charging 2000 vs 2026 vs 2050.

One-off procedural media renderer. Completion is verified against the rendered
MP4, not renderer unit tests. See docs/production/capytech-v1-charging-eras.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import wave
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
STORYBOARD = ROOT / "output/projects/capytech/scripts/capytech_v1_storyboard.json"
STORYBOARD_V2 = ROOT / "output/projects/capytech/scripts/capytech_v2_storyboard.json"
PEXELS = ROOT / "output/projects/capytech/source/pexels/34908543.mp4"
LICENSE = ROOT / "output/projects/capytech/source/pexels/license.json"
WORK = ROOT / "output/projects/capytech/clips/capytech_v1_work"
AUDIO_DIR = WORK / "audio"
PEXELS_FRAMES = WORK / "pexels_frames"
PEXELS_PROVENANCE = PEXELS_FRAMES / "provenance.json"
FINAL_DIR = ROOT / "output/projects/capytech/final"
FINAL = FINAL_DIR / "2026-07-27-capytech_v1_charging_eras.mp4"
HOOK = WORK / "hook_rough.mp4"
VISUAL = WORK / "visual_master.mp4"
MANIFEST = WORK / "render_manifest.json"
CTA_PROVENANCE = AUDIO_DIR / "cta_provenance.json"
FONT_DISPLAY = ROOT / "assets/fonts/komika-axis/KOMIKAX_.ttf"
FONT_UI = Path("/System/Library/Fonts/Helvetica.ttc")

W, H = 540, 960
OUT_W, OUT_H = 1080, 1920
FPS = 30
DURATION = 55.0
MAX_DURATION = 75.0
MIN_DURATION = 50.0
SPEC_VERSION = "capytech_v2"
SAMPLE_RATE = 48000
PEXELS_EXTRACT_START = 0.4
PEXELS_EXTRACT_DURATION = 2.6
PEXELS_EXTRACT_FPS = 12
PEXELS_USE_START = 32.2
PEXELS_USE_END = 34.6
RNG = np.random.default_rng(2050)

WHITE = (250, 252, 255)
INK = (15, 21, 33)
NAVY = (23, 48, 83)
TEAL = (17, 176, 173)
COPPER = (229, 126, 68)
COPPER_DARK = (179, 78, 49)
CYAN = (53, 229, 255)
YELLOW = (255, 211, 69)
RED = (255, 74, 92)
GREEN = (60, 229, 144)
PURPLE = (139, 92, 246)
GRAY = (135, 145, 160)


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(command[:12]), "..." if len(command) > 12 else "", flush=True)
    return subprocess.run(command, check=True, capture_output=capture, text=True)


def probe_duration(path: Path) -> float:
    result = run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ], capture=True)
    return float(result.stdout.strip())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json_if_valid(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return value if isinstance(value, dict) else None


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def smooth(value: float) -> float:
    x = clamp(value)
    return x * x * (3.0 - 2.0 * x)


def ease_out_back(value: float) -> float:
    x = clamp(value) - 1.0
    c1 = 1.70158
    c3 = c1 + 1.0
    return 1.0 + c3 * x * x * x + c1 * x * x


def pulse(t: float, speed: float = 1.0) -> float:
    return 0.5 + 0.5 * math.sin(t * math.tau * speed)


def mix_color(a: tuple[int, int, int], b: tuple[int, int, int], ratio: float) -> tuple[int, int, int]:
    p = clamp(ratio)
    return (
        int(a[0] * (1 - p) + b[0] * p),
        int(a[1] * (1 - p) + b[1] * p),
        int(a[2] * (1 - p) + b[2] * p),
    )


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> float:
    return draw.textlength(text, font=fnt)


def fitted_font(draw: ImageDraw.ImageDraw, text: str, max_size: int, min_size: int, max_width: int) -> ImageFont.FreeTypeFont:
    for size in range(max_size, min_size - 1, -2):
        candidate = font(FONT_DISPLAY, size)
        if text_width(draw, text, candidate) <= max_width:
            return candidate
    return font(FONT_DISPLAY, min_size)


def draw_center_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    size: int,
    fill: tuple[int, int, int] = WHITE,
    stroke: tuple[int, int, int] = INK,
    stroke_width: int = 3,
    max_width: int = 490,
    display: bool = True,
) -> None:
    path = FONT_DISPLAY if display else FONT_UI
    if display:
        fnt = fitted_font(draw, text, size, max(16, size - 18), max_width)
    else:
        fnt = font(path, size)
    draw.text(xy, text, font=fnt, fill=fill, stroke_fill=stroke, stroke_width=stroke_width, anchor="mm", align="center")


def rounded_gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    width, height = size
    arr = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        ratio = y / max(1, height - 1)
        arr[y, :, :] = mix_color(top, bottom, ratio)
    return Image.fromarray(arr)


def make_background(kind: str) -> Image.Image:
    palettes = {
        "hook": ((17, 25, 46), (48, 23, 66)),
        "2000": ((250, 228, 170), (180, 120, 68)),
        "2026": ((101, 184, 213), (38, 82, 120)),
        "2050": ((22, 20, 45), (4, 10, 25)),
    }
    top, bottom = palettes[kind]
    image = rounded_gradient((W, H), top, bottom).convert("RGBA")
    draw = ImageDraw.Draw(image, "RGBA")
    horizon = 660
    draw.rectangle((0, horizon, W, H), fill=(12, 18, 28, 115) if kind in {"hook", "2050"} else (76, 49, 32, 80))
    for index in range(9):
        x = int(index * W / 8)
        draw.line((W // 2, horizon, x, H), fill=(255, 255, 255, 24), width=2)
    for y in range(horizon, H, 45):
        draw.line((0, y, W, y), fill=(255, 255, 255, 18), width=1)
    if kind == "2050":
        for x in range(30, W, 80):
            draw.line((x, 120, x, 630), fill=(*CYAN, 20), width=2)
        for y in range(160, 630, 80):
            draw.line((15, y, W - 15, y), fill=(*PURPLE, 18), width=2)
    return image


BACKGROUNDS = {key: make_background(key) for key in ("hook", "2000", "2026", "2050")}


def paste_rotated(base: Image.Image, patch: Image.Image, center: tuple[float, float], angle: float) -> None:
    rotated = patch.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    x = int(center[0] - rotated.width / 2)
    y = int(center[1] - rotated.height / 2)
    base.alpha_composite(rotated, (x, y))


def rounded_limb(size: tuple[int, int], color: tuple[int, int, int], radius: int = 18) -> Image.Image:
    patch = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(patch, "RGBA")
    draw.rounded_rectangle((3, 4, size[0] - 3, size[1] - 2), radius=radius, fill=(*color, 255), outline=(0, 0, 0, 45), width=2)
    draw.rounded_rectangle((8, 7, size[0] - 12, size[1] // 3), radius=max(5, radius // 2), fill=(255, 255, 255, 24))
    return patch


def draw_face(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: float, expression: str, energy: float) -> None:
    eye = mix_color(INK, GRAY, 1.0 - energy)
    ex = 31 * scale
    ey = cy - 9 * scale
    ew = 15 * scale
    eh = 22 * scale
    if expression in {"panic", "shock"}:
        draw.ellipse((cx - ex - ew, ey - eh, cx - ex + ew, ey + eh), fill=WHITE, outline=INK, width=max(2, int(3 * scale)))
        draw.ellipse((cx + ex - ew, ey - eh, cx + ex + ew, ey + eh), fill=WHITE, outline=INK, width=max(2, int(3 * scale)))
        draw.ellipse((cx - ex - 5 * scale, ey - 3 * scale, cx - ex + 5 * scale, ey + 10 * scale), fill=eye)
        draw.ellipse((cx + ex - 5 * scale, ey - 3 * scale, cx + ex + 5 * scale, ey + 10 * scale), fill=eye)
        draw.ellipse((cx - 17 * scale, cy + 26 * scale, cx + 17 * scale, cy + 58 * scale), fill=INK)
    elif expression == "smug":
        draw.arc((cx - ex - ew, ey - 4, cx - ex + ew, ey + 15), 205, 335, fill=eye, width=max(3, int(5 * scale)))
        draw.arc((cx + ex - ew, ey - 4, cx + ex + ew, ey + 15), 205, 335, fill=eye, width=max(3, int(5 * scale)))
        draw.arc((cx - 30 * scale, cy + 10 * scale, cx + 30 * scale, cy + 55 * scale), 10, 165, fill=eye, width=max(3, int(5 * scale)))
    elif expression == "dead":
        for offset in (-ex, ex):
            draw.line((cx + offset - 10 * scale, ey - 10 * scale, cx + offset + 10 * scale, ey + 10 * scale), fill=eye, width=max(3, int(4 * scale)))
            draw.line((cx + offset - 10 * scale, ey + 10 * scale, cx + offset + 10 * scale, ey - 10 * scale), fill=eye, width=max(3, int(4 * scale)))
        draw.line((cx - 18 * scale, cy + 37 * scale, cx + 18 * scale, cy + 37 * scale), fill=eye, width=max(3, int(4 * scale)))
    elif expression == "strain":
        draw.line((cx - 46 * scale, ey - 12 * scale, cx - 16 * scale, ey + 3 * scale), fill=eye, width=max(3, int(5 * scale)))
        draw.line((cx + 46 * scale, ey - 12 * scale, cx + 16 * scale, ey + 3 * scale), fill=eye, width=max(3, int(5 * scale)))
        draw.arc((cx - 27 * scale, cy + 20 * scale, cx + 27 * scale, cy + 57 * scale), 190, 350, fill=eye, width=max(3, int(5 * scale)))
    else:
        draw.ellipse((cx - ex - 7 * scale, ey - 10 * scale, cx - ex + 7 * scale, ey + 10 * scale), fill=eye)
        draw.ellipse((cx + ex - 7 * scale, ey - 10 * scale, cx + ex + 7 * scale, ey + 10 * scale), fill=eye)
        draw.arc((cx - 25 * scale, cy + 10 * scale, cx + 25 * scale, cy + 50 * scale), 10, 170, fill=eye, width=max(3, int(5 * scale)))


def draw_character(
    image: Image.Image,
    cx: float,
    foot_y: float,
    scale: float = 1.0,
    expression: str = "neutral",
    pose: str = "idle",
    energy: float = 1.0,
    phase: float = 0.0,
) -> None:
    energy = clamp(energy)
    skin = mix_color(COPPER, GRAY, 1 - energy)
    torso = mix_color(NAVY, (70, 75, 86), 1 - energy)
    legs = mix_color(TEAL, (83, 90, 96), 1 - energy)
    bounce = math.sin(phase * math.tau) * 4 * scale if energy > 0.1 else 0
    foot_y += bounce
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow, "RGBA")
    sd.ellipse((cx - 105 * scale, foot_y - 16 * scale, cx + 105 * scale, foot_y + 20 * scale), fill=(0, 0, 0, 72))
    shadow = shadow.filter(ImageFilter.GaussianBlur(max(2, int(6 * scale))))
    image.alpha_composite(shadow)

    body = ImageDraw.Draw(image, "RGBA")
    if pose == "collapsed":
        body.rounded_rectangle((cx - 125 * scale, foot_y - 80 * scale, cx + 80 * scale, foot_y - 10 * scale), radius=int(25 * scale), fill=(*torso, 255), outline=(0, 0, 0, 50), width=2)
        body.rounded_rectangle((cx - 155 * scale, foot_y - 70 * scale, cx - 35 * scale, foot_y + 5 * scale), radius=int(28 * scale), fill=(*skin, 255))
        body.rounded_rectangle((cx + 40 * scale, foot_y - 55 * scale, cx + 165 * scale, foot_y + 10 * scale), radius=int(24 * scale), fill=(*legs, 255))
        draw_face(body, cx - 95 * scale, foot_y - 34 * scale, 0.55 * scale, "dead", energy)
        return

    leg_w, leg_h = 58 * scale, 145 * scale
    for side in (-1, 1):
        x0 = cx + side * 34 * scale - leg_w / 2
        body.rounded_rectangle((x0, foot_y - leg_h, x0 + leg_w, foot_y), radius=int(18 * scale), fill=(*legs, 255), outline=(0, 0, 0, 40), width=2)
        body.rounded_rectangle((x0 - 7 * scale, foot_y - 25 * scale, x0 + leg_w + 10 * scale, foot_y + 3 * scale), radius=int(14 * scale), fill=(238, 245, 249, 255))

    torso_top = foot_y - 335 * scale
    body.rounded_rectangle((cx - 88 * scale, torso_top, cx + 88 * scale, foot_y - 125 * scale), radius=int(28 * scale), fill=(*torso, 255), outline=(0, 0, 0, 48), width=2)
    body.rounded_rectangle((cx - 70 * scale, torso_top + 10 * scale, cx + 20 * scale, torso_top + 42 * scale), radius=int(15 * scale), fill=(255, 255, 255, 22))

    arm_y = torso_top + 92 * scale
    poses = {
        "idle": (-8, 8), "reach": (-52, 28), "celebrate": (-55, 55),
        "strain": (-75, 70), "hold": (-28, 25), "scan": (-5, 42),
    }
    left_angle, right_angle = poses.get(pose, poses["idle"])
    for side, angle in ((-1, left_angle), (1, right_angle)):
        limb = rounded_limb((int(62 * scale), int(178 * scale)), skin, int(20 * scale))
        center = (cx + side * 112 * scale, arm_y + 52 * scale)
        paste_rotated(image, limb, center, angle * side)

    head_w, head_h = 156 * scale, 144 * scale
    head_cy = torso_top - 62 * scale
    body.rounded_rectangle(
        (cx - head_w / 2, head_cy - head_h / 2, cx + head_w / 2, head_cy + head_h / 2),
        radius=int(36 * scale), fill=(*skin, 255), outline=(0, 0, 0, 55), width=2,
    )
    body.rounded_rectangle((cx - head_w / 2 + 14 * scale, head_cy - head_h / 2 + 10 * scale, cx + 12 * scale, head_cy - head_h / 2 + 34 * scale), radius=int(12 * scale), fill=(255, 255, 255, 28))
    draw_face(body, cx, head_cy, scale, expression, energy)


def phone_patch(percent: int, size: tuple[int, int] = (112, 190), future: bool = False) -> Image.Image:
    width, height = size
    patch = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(patch, "RGBA")
    border = CYAN if future else (28, 32, 40)
    draw.rounded_rectangle((2, 2, width - 2, height - 2), radius=18, fill=(15, 19, 28, 255), outline=(*border, 255), width=5)
    draw.rounded_rectangle((10, 14, width - 10, height - 15), radius=12, fill=(25, 36, 52, 255))
    color = RED if percent <= 10 else (YELLOW if percent < 80 else GREEN)
    battery_box = (width * 0.27, height * 0.25, width * 0.73, height * 0.55)
    draw.rounded_rectangle(battery_box, radius=8, outline=(*WHITE, 255), width=3)
    bx0, by0, bx1, by1 = battery_box
    fill_h = max(2, (by1 - by0 - 8) * percent / 100)
    draw.rounded_rectangle((bx0 + 5, by1 - 5 - fill_h, bx1 - 5, by1 - 5), radius=4, fill=(*color, 255))
    draw_center_text(draw, (width / 2, height * 0.70), f"{percent}%", 28, color, stroke_width=2, max_width=width - 12)
    return patch


def draw_phone(image: Image.Image, x: float, y: float, percent: int, angle: float = 0, scale: float = 1.0, future: bool = False) -> None:
    patch = phone_patch(percent, (int(112 * scale), int(190 * scale)), future)
    paste_rotated(image, patch, (x, y), angle)


def draw_cable(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], color: tuple[int, int, int] = (30, 34, 42), width: int = 12) -> None:
    draw.line(points, fill=(0, 0, 0, 80), width=width + 6, joint="curve")
    draw.line(points, fill=(*color, 255), width=width, joint="curve")
    x, y = points[-1]
    draw.rounded_rectangle((x - 17, y - 10, x + 17, y + 10), radius=5, fill=(*color, 255), outline=(255, 255, 255, 100), width=2)


def draw_era(draw: ImageDraw.ImageDraw, era: str, color: tuple[int, int, int]) -> None:
    draw.rounded_rectangle((18, 8, 162, 58), radius=17, fill=(6, 10, 18, 205), outline=(*color, 230), width=4)
    draw_center_text(draw, (90, 33), era, 34, color, stroke_width=3, max_width=126)


def draw_caption(image: Image.Image, text: str, emphasis: str, y: int = 610) -> None:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    draw.rounded_rectangle((30, y - 54, W - 30, y + 54), radius=28, fill=(4, 8, 16, 190), outline=(255, 255, 255, 48), width=2)
    words = text.split()
    size = 38 if len(text) < 23 else 30
    fnt = fitted_font(draw, text, size, 22, W - 90)
    widths = [draw.textlength(word, font=fnt) for word in words]
    spacing = draw.textlength(" ", font=fnt)
    total = sum(widths) + spacing * max(0, len(words) - 1)
    cursor = (W - total) / 2
    for word, width in zip(words, widths):
        normalized = word.strip('"*:').upper()
        emphasized = normalized == emphasis.strip('"*:').upper() or emphasis.strip('"*:').upper() in normalized
        color = CYAN if emphasized else WHITE
        draw.text((cursor, y), word, font=fnt, fill=(*color, 255), stroke_fill=(*INK, 255), stroke_width=3, anchor="lm")
        cursor += width + spacing
    image.alpha_composite(overlay)


def draw_watermark(draw: ImageDraw.ImageDraw, t: float) -> None:
    if t < 20:
        xy = (22, 905)
        anchor = "ls"
    elif t < 39:
        xy = (W - 20, 122)
        anchor = "rs"
    else:
        xy = (W - 20, 905)
        anchor = "rs"
    draw.text(xy, "@BYTELOOP", font=font(FONT_UI, 18), fill=(255, 255, 255, 80), stroke_fill=(0, 0, 0, 65), stroke_width=1, anchor=anchor)


def draw_orb(image: Image.Image, x: float, y: float, radius: float, t: float, danger: bool = False) -> None:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    color = RED if danger else CYAN
    glow = int(28 + 20 * pulse(t, 1.6))
    for extra in range(70, 0, -10):
        alpha = max(0, int((70 - extra) * 0.7))
        draw.ellipse((x - radius - extra, y - radius - extra, x + radius + extra, y + radius + extra), fill=(*color, alpha))
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(18, 30, 52, 245), outline=(*color, 255), width=6)
    draw.ellipse((x - radius * 0.62, y - radius * 0.62, x + radius * 0.62, y + radius * 0.62), outline=(*WHITE, 130), width=2)
    for index in range(8):
        angle = t * 2 + index * math.tau / 8
        px = x + math.cos(angle) * radius * 0.72
        py = y + math.sin(angle) * radius * 0.72
        draw.ellipse((px - 5, py - 5, px + 5, py + 5), fill=(*color, 240))
    overlay = overlay.filter(ImageFilter.GaussianBlur(glow / 12))
    image.alpha_composite(overlay)


def pexels_texture(t: float, frames: list[Image.Image]) -> Image.Image | None:
    if not frames or not PEXELS_USE_START <= t <= PEXELS_USE_END:
        return None
    ratio = (t - PEXELS_USE_START) / (PEXELS_USE_END - PEXELS_USE_START)
    return frames[min(len(frames) - 1, int(ratio * len(frames)))].copy()


def load_storyboard() -> dict[str, Any]:
    spec = json.loads(STORYBOARD_V2.read_text(encoding="utf-8"))
    if spec["target_duration_seconds"] != DURATION or spec["fps"] != FPS:
        raise RuntimeError("Storyboard duration/FPS mismatch")
    beats = spec["beats"]
    if beats[0]["start"] != 0 or beats[-1]["end"] != DURATION:
        raise RuntimeError("Storyboard does not cover full timeline")
    if any(a["end"] != b["start"] for a, b in zip(beats, beats[1:])):
        raise RuntimeError("Storyboard beats are not contiguous")
    cta = next(item for item in beats if item["id"] == "triple_cta")
    if not 33 <= cta["start"] <= 36:
        raise RuntimeError("CTA outside 33–36s gate")
    if not MIN_DURATION <= DURATION <= MAX_DURATION:
        raise RuntimeError(f"Runtime outside {MIN_DURATION:g}–{MAX_DURATION:g}s gate")
    if not any(item["start"] <= 0.2 for item in spec["caption_bursts"]):
        raise RuntimeError("No caption by 0.2s")
    return spec


def prepare_pexels_frames() -> list[Image.Image]:
    if not LICENSE.exists():
        raise FileNotFoundError(f"Missing Pexels license ledger: {LICENSE}")
    if not PEXELS.exists():
        raise FileNotFoundError(f"Missing approved Pexels source: {PEXELS}")
    license_data = json.loads(LICENSE.read_text(encoding="utf-8"))["approved"]
    source_hash = sha256(PEXELS)
    if source_hash != license_data["sha256"]:
        raise RuntimeError(f"Pexels source hash mismatch: {source_hash}")
    config = {
        "source": str(PEXELS.relative_to(ROOT)),
        "source_sha256": source_hash,
        "extract_start_seconds": PEXELS_EXTRACT_START,
        "extract_duration_seconds": PEXELS_EXTRACT_DURATION,
        "extract_fps": PEXELS_EXTRACT_FPS,
        "filter": "scale=180:320:force_original_aspect_ratio=increase,crop=180:320",
        "final_usage_seconds": [PEXELS_USE_START, PEXELS_USE_END],
    }
    PEXELS_FRAMES.mkdir(parents=True, exist_ok=True)
    existing = sorted(PEXELS_FRAMES.glob("*.jpg"))
    marker = read_json_if_valid(PEXELS_PROVENANCE)
    cached_frames = marker.get("frames", []) if marker else []
    cache_valid = (
        marker is not None
        and marker.get("config") == config
        and len(existing) == round(PEXELS_EXTRACT_DURATION * PEXELS_EXTRACT_FPS)
        and len(cached_frames) == len(existing)
        and all(
            item.get("name") == path.name and item.get("sha256") == sha256(path)
            for item, path in zip(cached_frames, existing)
        )
    )
    if not cache_valid:
        for path in existing:
            path.unlink()
        run([
            "ffmpeg", "-y", "-v", "error", "-ss", str(PEXELS_EXTRACT_START), "-i", str(PEXELS),
            "-t", str(PEXELS_EXTRACT_DURATION),
            "-vf", f"fps={PEXELS_EXTRACT_FPS},scale=180:320:force_original_aspect_ratio=increase,crop=180:320",
            str(PEXELS_FRAMES / "%03d.jpg"),
        ])
        existing = sorted(PEXELS_FRAMES.glob("*.jpg"))
        expected_count = round(PEXELS_EXTRACT_DURATION * PEXELS_EXTRACT_FPS)
        if len(existing) != expected_count:
            raise RuntimeError(f"Incomplete Pexels frame cache: {len(existing)} != {expected_count}")
        marker = {
            "config": config,
            "frames": [{"name": path.name, "sha256": sha256(path)} for path in existing],
        }
        PEXELS_PROVENANCE.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")
    images: list[Image.Image] = []
    for path in existing:
        with Image.open(path) as frame:
            frame.verify()
        with Image.open(path) as frame:
            images.append(frame.convert("RGBA"))
    return images


def caption_for_time(spec: dict[str, Any], t: float) -> tuple[str, str] | None:
    for item in spec["caption_bursts"]:
        if item["start"] <= t < item["end"]:
            return item["text"], item["emphasis"]
    return None


def render_frame(t: float, spec: dict[str, Any], stock_frames: list[Image.Image]) -> Image.Image:
    if t < 3:
        kind = "hook"
    elif t < 12:
        kind = "2000"
    elif t < 24:
        kind = "2026"
    else:
        kind = "2050"
    image = BACKGROUNDS[kind].copy()
    draw = ImageDraw.Draw(image, "RGBA")
    phase = (t * 0.8) % 1.0

    if t < 3:
        progress = t / 3
        lunge = smooth(clamp(t / 1.25))
        recoil = smooth(clamp((t - 1.65) / 1.15))
        character_x = 168 + 42 * lunge - 24 * recoil
        draw_character(image, character_x, 850 - 12 * lunge, 1.12, "panic", "reach", 1.0, phase)
        slip = smooth(clamp((t - 1.2) / 1.4))
        phone_x = 370 + 18 * slip + 10 * math.sin(t * 7)
        phone_y = 365 - 8 * lunge + 10 * slip
        draw_phone(image, phone_x, phone_y, 1, -7 + 9 * slip + 3 * math.sin(t * 5), 1.2, True)
        draw.rounded_rectangle((487, 706, 536, 795), radius=10, fill=(225, 232, 242, 245), outline=(15, 22, 34, 130), width=3)
        draw.ellipse((499, 735, 507, 751), fill=(28, 35, 46, 230))
        draw.ellipse((516, 735, 524, 751), fill=(28, 35, 46, 230))
        cable_end = (411 + 78 * slip, 494 + 12 * slip)
        draw_cable(draw, [(511, 760), (485, 675), (460, 585), cable_end], CYAN, 13)
        if t > 1.0:
            phone_port = (phone_x + 23, phone_y + 114)
            draw.line((phone_port[0], phone_port[1], cable_end[0] - 18, cable_end[1]), fill=(*RED, 220), width=5)
            draw.polygon(
                [(cable_end[0] - 18, cable_end[1]), (cable_end[0] - 32, cable_end[1] - 10), (cable_end[0] - 31, cable_end[1] + 10)],
                fill=(*RED, 235),
            )
        draw.rounded_rectangle((340, 700, 515, 770), radius=18, fill=(8, 14, 25, 210), outline=(*RED, 230), width=3)
        draw_center_text(draw, (428, 735), f"00:{max(0, 60 - int(t * 18)):02d}", 35, RED, max_width=150)
    elif t < 12:
        local = t - 3
        draw_era(draw, "2000", YELLOW)
        expression = "smug" if local > 5 else "neutral"
        pose = "celebrate" if local > 7 else "hold"
        draw_character(image, 270, 852, 1.0, expression, pose, 1.0, phase)
        pct = 1 if local < 3 else min(100, int(1 + (local - 3) * 31))
        draw_phone(image, 372, 410, pct, -8, 0.86, False)
        plug_x = 105
        draw.rounded_rectangle((65, 430, 140, 550), radius=10, fill=(240, 228, 205, 255), outline=(65, 48, 35, 150), width=3)
        draw.ellipse((87, 465, 100, 486), fill=(35, 30, 25, 230))
        draw.ellipse((108, 465, 121, 486), fill=(35, 30, 25, 230))
        draw_cable(draw, [(plug_x, 500), (150, 600), (260, 680), (348, 505)], (28, 26, 24), 16)
        if 5 < local < 8:
            for i in range(6):
                angle = i * math.tau / 6 + t
                x = 372 + math.cos(angle) * 75
                y = 410 + math.sin(angle) * 75
                draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(*GREEN, 220))
        if local > 8:
            draw_center_text(draw, (270, 205), "ONE PLUG. DONE.", 34, GREEN, max_width=450)
    elif t < 24:
        local = t - 14
        draw_era(draw, "2026", WHITE)
        expression = "strain" if local > 7 else "panic"
        pose = "strain" if local > 7 else "hold"
        draw_character(image, 270, 860, 0.92, expression, pose, 1.0, phase)
        draw_phone(image, 270, 390, 1, 0, 0.82, False)
        if local < 5:
            fan = smooth(local / 3)
            colors = [RED, CYAN, YELLOW, PURPLE, GREEN]
            for index, color in enumerate(colors):
                angle = -1.35 + index * 0.68
                end_x = 270 + math.cos(angle) * (170 + 30 * fan)
                end_y = 520 + math.sin(angle) * (170 + 30 * fan)
                draw_cable(draw, [(270, 520), ((270 + end_x) / 2, 540), (end_x, end_y)], color, 8)
        elif local < 9:
            count = 1 + int((local - 5) * 2)
            for index in range(count):
                x0 = 80 + index * 40
                y0 = 700 - index * 45
                draw.rounded_rectangle((x0, y0, x0 + 150, y0 + 90), radius=12, fill=(232, 179 - index * 10, 72, 255), outline=(60, 35, 20, 120), width=3)
                label = "WRONG CABLE" if index == 0 else "ADAPTER SOLD SEPARATELY"
                draw_center_text(draw, (x0 + 75, y0 + 45), label, 18 if index == 0 else 16, INK, stroke_width=1, max_width=140)
        elif local < 12:
            reach = smooth((local - 9) / 3)
            outlet_x = 505
            draw.rounded_rectangle((470, 420, 532, 520), radius=10, fill=(236, 239, 244, 255), outline=(25, 35, 45, 100), width=3)
            draw.ellipse((488, 452, 498, 470), fill=(30, 36, 45, 220))
            draw.ellipse((506, 452, 516, 470), fill=(30, 36, 45, 220))
            cable_tip = 455 + 28 * reach
            draw_cable(draw, [(270, 485), (360, 580), (cable_tip, 492)], (30, 34, 42), 11)
            draw.line((cable_tip + 18, 492, outlet_x - 18, 492), fill=(*RED, 210), width=4)
            draw_center_text(draw, (420, 550), "2 cm SHORT", 26, RED, max_width=210)
        else:
            draw.rounded_rectangle((90, 240, 450, 540), radius=30, fill=(8, 13, 22, 238), outline=(*RED, 240), width=5)
            draw_center_text(draw, (270, 325), "UPDATE REQUIRED", 34, RED, max_width=320)
            progress = int((local - 12) / 3 * 4)
            draw.rounded_rectangle((125, 390, 415, 430), radius=18, fill=(255, 255, 255, 30))
            draw.rounded_rectangle((130, 395, 130 + progress * 2.8, 425), radius=14, fill=(*RED, 230))
            draw_center_text(draw, (270, 472), f"{progress}%", 28, WHITE, max_width=120)
    else:
        local = t - 24
        draw_era(draw, "2050", RED)
        if t < 46:
            energy = 1.0 if t < 42 else clamp(1 - (t - 42) / 9.5)
            expression = "panic" if t < 48 else "strain"
            pose = "scan" if t < 42 else "strain"
            draw_character(image, 175, 860, 0.86, expression, pose, energy, phase)
        else:
            draw_character(image, 175, 860, 0.86, "dead", "collapsed", 0.0, phase)

        orb_r = 72 + 8 * pulse(t, 1.4)
        orb_y = 300 + 12 * math.sin(t * 2.2)
        draw_orb(image, 405, orb_y, orb_r, t, t >= 35.5)
        phone_pct = 1
        if 42 <= t < 48:
            phone_pct = int(1 + (t - 42) / 6 * 99)
        elif 48 <= t < 54:
            phone_pct = 100
        elif t >= 54:
            phone_pct = max(1, int(100 - (t - 54) / 5 * 99))
        draw_phone(image, 390, 575, phone_pct, 5 * math.sin(t * 2), 0.82, True)

        if 24 <= t < 27:
            alpha = smooth((t - 24) / 3.0)
            draw_center_text(draw, (380, 175), "AI CHARGE ORB", 30, mix_color(WHITE, CYAN, alpha), max_width=260)
        elif 27 <= t < 30.5:
            scan_y = 400 + ((t - 27) % 1.2) / 1.2 * 330
            draw.rectangle((70, scan_y - 5, 310, scan_y + 5), fill=(*CYAN, 175))
            draw.line((405, orb_y + 65, 260, scan_y), fill=(*CYAN, 130), width=7)
            texture = pexels_texture(t, stock_frames)
            if texture is not None:
                panel = texture.resize((138, 245), Image.Resampling.LANCZOS)
                panel = ImageEnhance.Color(panel).enhance(0.75)
                image.alpha_composite(panel, (336, 405))
                draw.rounded_rectangle((330, 399, 480, 662), radius=14, outline=(*CYAN, 220), width=4)
                draw_center_text(draw, (405, 640), "ILLUSTRATION", 15, WHITE, stroke_width=2, max_width=130, display=False)
        elif 30.5 <= t < 33:
            draw.rounded_rectangle((72, 205, 468, 520), radius=30, fill=(7, 10, 20, 232), outline=(*RED, 240), width=5)
            draw_center_text(draw, (270, 270), "FREE CHARGE*", 40, GREEN, max_width=350)
            draw_center_text(draw, (270, 350), "ENERGY SOURCE", 29, WHITE, max_width=330)
            draw_center_text(draw, (270, 420), "YOU", 62, RED, max_width=240)
            draw_center_text(draw, (270, 480), "*TERMS ACCEPTED", 17, GRAY, stroke_width=2, max_width=260, display=False)
        elif 33 <= t < 36:
            wobble = 1 + 0.03 * math.sin((t - 33) * 18)
            panel_w = 450 * wobble
            panel_h = 290 * wobble
            draw.rounded_rectangle((W / 2 - panel_w / 2, 215 - panel_h / 2, W / 2 + panel_w / 2, 215 + panel_h / 2), radius=32, fill=(5, 9, 18, 245), outline=(*PURPLE, 255), width=6)
            draw_center_text(draw, (270, 135), "HUMAN CHECK", 40, YELLOW, max_width=380)
            draw_center_text(draw, (270, 205), "LIKE + SUBSCRIBE", 31, WHITE, max_width=400)
            draw_center_text(draw, (270, 255), "COMMENT \"CHARGE\"", 30, CYAN, max_width=420)
            draw.rounded_rectangle((95, 310, 445, 348), radius=16, fill=(255, 255, 255, 30))
            fill = clamp((t - 33) / 3.0)
            draw.rounded_rectangle((100, 315, 100 + 340 * fill, 343), radius=13, fill=(*PURPLE, 245))
            draw_center_text(draw, (270, 375), "99% LOCKED", 25, RED, max_width=260)
        elif 36 <= t < 46:
            drain = clamp((t - 36) / 10.0)
            beam_width = int(12 + 14 * pulse(t, 4))
            draw.line((240, 470, 340, orb_y + 35), fill=(*CYAN, 160), width=beam_width)
            for index in range(8):
                ratio = ((t * 2.5 + index / 8) % 1)
                x = 240 + (340 - 240) * ratio
                y = 470 + (orb_y + 35 - 470) * ratio
                draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(*YELLOW, 230))
            draw.rounded_rectangle((50, 735, 290, 775), radius=18, fill=(255, 255, 255, 28))
            draw.rounded_rectangle((55, 740, 55 + 230 * (1 - drain), 770), radius=13, fill=(*RED, 235))
            draw_center_text(draw, (170, 805), f"HUMAN {max(0, int((1 - drain) * 100))}%", 24, RED, max_width=250)
        else:
            draw.rounded_rectangle((80, 215, 460, 505), radius=30, fill=(5, 9, 18, 238), outline=(*RED, 240), width=5)
            draw_center_text(draw, (270, 285), "SYSTEM UPDATE", 40, RED, max_width=330)
            update = clamp((t - 46) / 5)
            draw.rounded_rectangle((115, 365, 425, 410), radius=20, fill=(255, 255, 255, 30))
            draw.rounded_rectangle((120, 370, 120 + 300 * update, 405), radius=16, fill=(*CYAN, 235))
            draw_center_text(draw, (270, 455), f"BATTERY {phone_pct}%", 28, YELLOW if phone_pct > 10 else RED, max_width=300)

    caption = caption_for_time(spec, t)
    ui_already_carries_text = (21 <= t < 24) or (30.5 <= t < 36) or (46 <= t < 49)
    if caption and not ui_already_carries_text:
        draw_caption(image, caption[0], caption[1], 610 if t < 29 else 650)
    draw_watermark(draw, t)

    # Continuous motion indicator: subtle foreground light streaks tied to story state.
    if kind in {"hook", "2026", "2050"}:
        for index in range(3):
            x = int((t * (45 + index * 12) + index * 170) % (W + 120)) - 60
            draw.line((x, 0, x - 80, H), fill=(255, 255, 255, 9), width=3)
    return image.convert("RGB")


def prepare_cta() -> Path:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    aiff = AUDIO_DIR / "cta_raw_v2.aiff"
    wav_path = AUDIO_DIR / "cta_ready_v3.wav"
    voice = "Samantha"
    line = "Like, subscribe, and comment charge to continue."
    config = {
        "voice": voice,
        "rate": 245,
        "text": line,
        "max_duration_seconds": 2.72,
        "sample_rate": SAMPLE_RATE,
        "channels": 2,
        "filters": "leading-silence trim, atempo, highpass, lowpass, acompressor, loudnorm",
    }
    marker = read_json_if_valid(CTA_PROVENANCE)
    if (
        wav_path.exists()
        and marker is not None
        and marker.get("config") == config
        and marker.get("wav_sha256") == sha256(wav_path)
        and 0 < probe_duration(wav_path) <= config["max_duration_seconds"]
    ):
        return wav_path
    wav_path.unlink(missing_ok=True)
    aiff.unlink(missing_ok=True)
    run(["say", "-v", voice, "-r", "245", "-o", str(aiff), line])
    raw_duration = probe_duration(aiff)
    max_duration = 2.72
    tempo = max(1.0, raw_duration / max_duration)
    if tempo > 2.0:
        raise RuntimeError(f"CTA source too long for safe atempo: {raw_duration:.3f}s")
    filters = (
        "silenceremove=start_periods=1:start_duration=0.03:start_threshold=-45dB,"
        f"atempo={tempo:.6f},highpass=f=160,lowpass=f=7800,"
        "acompressor=threshold=0.08:ratio=4:attack=5:release=80:makeup=1,"
        "loudnorm=I=-16:TP=-2:LRA=7"
    )
    run(["ffmpeg", "-y", "-v", "error", "-i", str(aiff), "-af", filters, "-ar", str(SAMPLE_RATE), "-ac", "2", "-c:a", "pcm_s16le", str(wav_path)])
    duration = probe_duration(wav_path)
    if not 0 < duration <= max_duration:
        raise RuntimeError(f"CTA cache duration invalid: {duration:.3f}s")
    CTA_PROVENANCE.write_text(json.dumps({
        "config": config,
        "wav_sha256": sha256(wav_path),
        "duration_seconds": duration,
    }, indent=2) + "\n", encoding="utf-8")
    return wav_path


def read_wav(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as handle:
        channels = handle.getnchannels()
        width = handle.getsampwidth()
        rate = handle.getframerate()
        frames = handle.readframes(handle.getnframes())
    if width != 2 or rate != SAMPLE_RATE:
        raise RuntimeError(f"Unsupported WAV format: {path}")
    data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    data = data.reshape(-1, channels)
    if channels == 1:
        data = np.repeat(data, 2, axis=1)
    return data[:, :2]


def envelope(length: int, attack: float = 0.02, release: float = 0.08) -> np.ndarray:
    env = np.ones(length, dtype=np.float32)
    a = min(length, int(attack * SAMPLE_RATE))
    r = min(length, int(release * SAMPLE_RATE))
    if a:
        env[:a] = np.linspace(0, 1, a, dtype=np.float32)
    if r:
        env[-r:] = np.linspace(1, 0, r, dtype=np.float32)
    return env


def tone(duration: float, frequency: float, amplitude: float, kind: str = "sine", sweep: float = 0.0) -> np.ndarray:
    count = max(1, int(duration * SAMPLE_RATE))
    times = np.arange(count, dtype=np.float32) / SAMPLE_RATE
    phase = math.tau * (frequency * times + sweep * times * times / 2)
    if kind == "square":
        wave_data = np.sign(np.sin(phase))
    elif kind == "saw":
        wave_data = 2 * ((frequency * times) % 1) - 1
    else:
        wave_data = np.sin(phase)
    signal = amplitude * wave_data * envelope(count)
    return np.column_stack((signal, signal)).astype(np.float32)


def noise(duration: float, amplitude: float, decay: bool = True) -> np.ndarray:
    count = max(1, int(duration * SAMPLE_RATE))
    signal = RNG.normal(0, amplitude, count).astype(np.float32)
    if decay:
        signal *= np.exp(-np.linspace(0, 7, count, dtype=np.float32))
    signal *= envelope(count, 0.002, 0.02)
    return np.column_stack((signal, signal))


def add_clip(track: np.ndarray, clip: np.ndarray, at: float, gain: float = 1.0) -> None:
    start = max(0, int(at * SAMPLE_RATE))
    end = min(len(track), start + len(clip))
    if end > start:
        track[start:end] += clip[: end - start] * gain


def sfx(event: str) -> np.ndarray:
    if event == "alarm":
        return np.concatenate([tone(0.10, 880, 0.16, "square"), tone(0.07, 0, 0), tone(0.10, 880, 0.16, "square")])
    if event in {"plug", "cta_unlock"}:
        return np.concatenate([noise(0.035, 0.18), tone(0.14, 980, 0.12, sweep=900)])
    if event == "success":
        return np.concatenate([tone(0.13, 660, 0.12), tone(0.13, 880, 0.13), tone(0.22, 1320, 0.12)])
    if event in {"lunge", "cable_slip", "cable_snap"}:
        return np.concatenate([noise(0.16, 0.09), tone(0.22, 180, 0.10, sweep=700)])
    if event in {"wrong_cable", "brick_drop", "collapse"}:
        return np.concatenate([tone(0.09, 120, 0.18), noise(0.14, 0.12)])
    if event == "box_pop":
        return np.concatenate([noise(0.06, 0.18), tone(0.11, 560, 0.08, sweep=700)])
    if event in {"update_alert", "danger", "cta_lock"}:
        return np.concatenate([tone(0.16, 220, 0.12, "square"), tone(0.16, 180, 0.12, "square")])
    if event == "orb_hover":
        return tone(0.8, 90, 0.08, sweep=130)
    if event == "scan":
        return tone(1.0, 320, 0.08, sweep=950)
    if event == "energy_drain":
        return np.concatenate([tone(1.3, 85, 0.13, sweep=260), noise(1.3, 0.035, False)])
    return tone(0.12, 440, 0.08)


def synthesize_audio(spec: dict[str, Any], duration: float) -> Path:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    count = int(duration * SAMPLE_RATE)
    t = np.arange(count, dtype=np.float32) / SAMPLE_RATE
    score = np.zeros((count, 2), dtype=np.float32)
    # Continuous harmonic beds prevent empty audio while keeping event SFX distinct.
    analog = (0.025 * np.sin(math.tau * 110 * t) + 0.018 * np.sin(math.tau * 165 * t))
    digital = (0.020 * np.sin(math.tau * 146.83 * t) + 0.017 * np.sin(math.tau * 293.66 * t))
    future = (0.028 * np.sin(math.tau * 55 * t) + 0.018 * np.sin(math.tau * 82.41 * t))
    mono = np.where(t < 14, analog, np.where(t < 29, digital, future)).astype(np.float32)
    score[:, 0] = mono
    score[:, 1] = mono * 0.96
    for beat_at in np.arange(0, duration, 0.5):
        frequency = 320 if beat_at < 14 else (480 if beat_at < 29 else 220)
        add_clip(score, tone(0.045, frequency, 0.035), float(beat_at))
    for event in spec["sfx_events"]:
        if event["at"] < duration:
            add_clip(score, sfx(event["id"]), event["at"], 1.0)
    if duration > 42:
        cta = read_wav(prepare_cta())
        # Duck score under CTA before adding the already-normalized voice.
        duck_start = int(38.92 * SAMPLE_RATE)
        duck_end = min(count, int(42.0 * SAMPLE_RATE))
        score[duck_start:duck_end] *= 0.32
        add_clip(score, cta, 33.05, 1.2)
    peak = float(np.max(np.abs(score)))
    if peak > 0.82:
        score *= 0.82 / peak
    output = AUDIO_DIR / ("hook_mix.wav" if duration <= 3.1 else "final_mix.wav")
    pcm = np.clip(score, -0.95, 0.95)
    pcm16 = (pcm * 32767).astype(np.int16)
    with wave.open(str(output), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(pcm16.tobytes())
    return output


def render_visual(spec: dict[str, Any], duration: float, output: Path, stock_frames: list[Image.Image]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-vf",
        f"scale={OUT_W}:{OUT_H}:flags=lanczos,format=yuv420p", "-an", "-c:v", "libx264",
        "-preset", "medium", "-crf", "17", "-profile:v", "high", "-level:v", "4.2",
        "-r", str(FPS), "-fps_mode", "cfr", "-movflags", "+faststart", str(output),
    ]
    print("+ rendering", int(duration * FPS), "procedural frames", flush=True)
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    assert process.stdin is not None
    try:
        for frame_index in range(int(duration * FPS)):
            frame = render_frame(frame_index / FPS, spec, stock_frames)
            process.stdin.write(frame.tobytes())
            if frame_index % 300 == 0:
                print(f"  frame {frame_index}/{int(duration * FPS)}", flush=True)
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError("ffmpeg visual encoder failed")


def mux(visual: Path, audio: Path, output: Path, duration: float) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    compressor = "acompressor=threshold=0.1:ratio=4:attack=5:release=100:makeup=1"
    analysis = subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-i", str(audio),
            "-af", f"{compressor},loudnorm=I=-16:TP=-2.0:LRA=11:print_format=json",
            "-f", "null", "-",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    blocks = re.findall(r"\{\s*\"input_i\".*?\}", analysis.stderr, flags=re.S)
    if not blocks:
        raise RuntimeError("Could not parse first-pass loudnorm measurements")
    measured = json.loads(blocks[-1])
    loudnorm = (
        f"{compressor},loudnorm=I=-16:TP=-2.0:LRA=11:"
        f"measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
        f"measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:"
        f"offset={measured['target_offset']}:linear=true"
    )
    run([
        "ffmpeg", "-y", "-v", "error", "-i", str(visual), "-i", str(audio),
        "-filter:a", loudnorm,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", str(SAMPLE_RATE),
        "-ac", "2", "-t", f"{duration:.6f}", "-movflags", "+faststart", str(output),
    ])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hook-only", action="store_true")
    args = parser.parse_args()
    spec = load_storyboard()
    duration = 3.0 if args.hook_only else DURATION
    stock_frames = [] if args.hook_only else prepare_pexels_frames()
    visual = WORK / ("hook_visual.mp4" if args.hook_only else "visual_master.mp4")
    output = HOOK if args.hook_only else FINAL
    render_visual(spec, duration, visual, stock_frames)
    audio = synthesize_audio(spec, duration)
    mux(visual, audio, output, duration)
    actual = probe_duration(output)
    if abs(actual - duration) > 0.08:
        raise RuntimeError(f"Output duration mismatch: {actual:.3f}s vs {duration:.3f}s")
    if not args.hook_only:
        license_data = json.loads(LICENSE.read_text(encoding="utf-8"))
        manifest = {
            "artifact": str(output.relative_to(ROOT)),
            "artifact_sha256": sha256(output),
            "artifact_size_bytes": output.stat().st_size,
            "renderer": str(Path(__file__).resolve().relative_to(ROOT)),
            "duration_seconds": actual,
            "fps": FPS,
            "canvas": [OUT_W, OUT_H],
            "storyboard": str(STORYBOARD_V2.relative_to(ROOT)),
            "storyboard_sha256": sha256(STORYBOARD_V2),
            "pexels": license_data["approved"],
            "pexels_used_as": "2.4-second in-world hologram from t=32.2–34.6s, labeled ILLUSTRATION",
            "pexels_frame_cache": json.loads(PEXELS_PROVENANCE.read_text(encoding="utf-8")),
            "capybluh_research_media_used_in_final": False,
            "beats": spec["beats"],
            "caption_bursts": spec["caption_bursts"],
            "audio": {
                "cta_voice": "Samantha",
                "cta_text": "Like, subscribe, and comment charge to continue.",
                "cta_window_seconds": [33.0, 36.0],
                "cta_cache": json.loads(CTA_PROVENANCE.read_text(encoding="utf-8")),
                "normalization": "acompressor before two-pass loudnorm",
                "loudness_target": {"integrated_lufs": -16, "true_peak_dbtp": -2.0, "lra_lu": 11},
            },
            "sfx_events": spec["sfx_events"],
            "watermark_routes": spec["watermark_routes"],
            "cta_interval": [33.0, 36.0],
            "cta_line": spec["cta_spoken_line"],
            "status": "rendered; final media QC pending",
        }
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
