#!/usr/bin/env python3
"""Render Capytech v6 as speech-free visual comedy for younger viewers.

Uses the already-approved Higgsfield footage, 29 cuts of 1–3 seconds, simple
cause-and-effect overlays, and event-bound cartoon SFX. No TTS, no source speech,
and no additional paid generation.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
import wave
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from pipeline.capytech import render_capytech_v1 as base  # noqa: E402
from pipeline.capytech import render_capytech_v5_higgsfield as previous  # noqa: E402

PROJECT = ROOT / "output/projects/capytech"
STORYBOARD = PROJECT / "scripts/capytech_v6_visual_comedy_storyboard.json"
WORK = PROJECT / "clips/capytech_v6_visual_comedy_work"
VISUAL = WORK / "visual_master.mp4"
AUDIO = WORK / "audio/sfx_music_mix.wav"
FINAL = PROJECT / "final/2026-07-28-capytech_v6_visual_comedy.mp4"
MANIFEST = WORK / "render_manifest.json"

W, H = 540, 960
OUT_W, OUT_H = 1080, 1920
FPS = 30
SAMPLE_RATE = 48000
DURATION = 50.5

ERA_COLORS = {
    "hook": base.CYAN,
    "2000": base.YELLOW,
    "2026": base.WHITE,
    "2050": base.RED,
    "cta": base.PURPLE,
    "payoff": base.GREEN,
    "loop": base.RED,
}


def load_storyboard() -> dict[str, Any]:
    spec = json.loads(STORYBOARD.read_text(encoding="utf-8"))
    cuts = spec["cuts"]
    errors: list[str] = []
    for index, cut in enumerate(cuts):
        duration = round(float(cut["end"] - cut["start"]), 4)
        if not 1.0 <= duration <= 3.0:
            errors.append(f"{cut['id']} duration={duration}")
        if index and cuts[index - 1]["end"] != cut["start"]:
            errors.append(f"gap before {cut['id']}")
        if cut["id"] not in previous.SOURCE_EDL or cut["id"] not in previous.REFRAMES:
            errors.append(f"missing inherited EDL/reframe for {cut['id']}")
    if cuts[0]["start"] != 0 or cuts[-1]["end"] != DURATION:
        errors.append("timeline coverage")
    if spec.get("tts") is not False:
        errors.append("TTS must be explicitly disabled")
    if errors:
        raise RuntimeError(errors)
    return spec


def active_cut(spec: dict[str, Any], t: float) -> dict[str, Any]:
    for cut in spec["cuts"]:
        if cut["start"] <= t < cut["end"]:
            return cut
    return spec["cuts"][-1]


def alpha_layer(image: Image.Image) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    return layer, ImageDraw.Draw(layer, "RGBA")


def composite_vignette(image: Image.Image) -> None:
    layer, draw = alpha_layer(image)
    draw.rectangle((0, 0, W, 90), fill=(0, 0, 0, 38))
    draw.rectangle((0, 820, W, H), fill=(0, 0, 0, 24))
    image.alpha_composite(layer)


def comic_shake(image: Image.Image, t: float, strength: float = 5.0) -> Image.Image:
    scale = 1.025
    enlarged = image.resize((int(W * scale), int(H * scale)), Image.Resampling.LANCZOS)
    extra_x = enlarged.width - W
    extra_y = enlarged.height - H
    x = int(extra_x / 2 + math.sin(t * 43) * strength)
    y = int(extra_y / 2 + math.cos(t * 37) * strength)
    x = max(0, min(extra_x, x))
    y = max(0, min(extra_y, y))
    return enlarged.crop((x, y, x + W, y + H))


def draw_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    size: int,
    color: tuple[int, int, int],
    max_width: int = 450,
) -> None:
    base.draw_center_text(draw, xy, text, size, color, stroke=base.INK, stroke_width=4, max_width=max_width)


def draw_era_badge(image: Image.Image, cut: dict[str, Any]) -> None:
    label = cut["era"].upper()
    if label in {"HOOK", "CTA", "PAYOFF", "LOOP"}:
        label = {"HOOK": "CHALLENGE", "CTA": "99%", "PAYOFF": "FINAL", "LOOP": "AGAIN?!"}[label]
    color = ERA_COLORS[cut["era"]]
    layer, draw = alpha_layer(image)
    draw.rounded_rectangle((18, 14, 168, 66), radius=17, fill=(4, 8, 18, 220), outline=(*color, 245), width=4)
    draw_text(draw, (93, 40), label, 24, color, 135)
    image.alpha_composite(layer)


def draw_speed_lines(image: Image.Image, t: float, color: tuple[int, int, int]) -> None:
    layer, draw = alpha_layer(image)
    center = (W / 2, H / 2)
    for index in range(16):
        angle = math.tau * index / 16 + t * 0.4
        inner = 310 + 12 * math.sin(t * 8 + index)
        outer = 540
        x0 = center[0] + math.cos(angle) * inner
        y0 = center[1] + math.sin(angle) * inner
        x1 = center[0] + math.cos(angle) * outer
        y1 = center[1] + math.sin(angle) * outer
        draw.line((x0, y0, x1, y1), fill=(*color, 100), width=5)
    image.alpha_composite(layer)


def draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[float, float], end: tuple[float, float], color: tuple[int, int, int], width: int = 14) -> None:
    draw.line((*start, *end), fill=(*base.INK, 180), width=width + 8)
    draw.line((*start, *end), fill=(*color, 250), width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    for delta in (2.55, -2.55):
        tip = (end[0] + 34 * math.cos(angle + delta), end[1] + 34 * math.sin(angle + delta))
        draw.line((*end, *tip), fill=(*color, 250), width=width)


def draw_battery(draw: ImageDraw.ImageDraw, x: int, y: int, value: int, color: tuple[int, int, int], width: int = 270, height: int = 96) -> None:
    draw.rounded_rectangle((x, y, x + width, y + height), radius=22, fill=(4, 8, 18, 235), outline=(*base.WHITE, 240), width=5)
    draw.rounded_rectangle((x + width, y + height * 0.28, x + width + 18, y + height * 0.72), radius=5, fill=(*base.WHITE, 230))
    inner = int((width - 24) * max(0, min(100, value)) / 100)
    if inner > 0:
        draw.rounded_rectangle((x + 10, y + 10, x + 10 + inner, y + height - 10), radius=14, fill=(*color, 235))
    draw_text(draw, (x + width / 2, y + height / 2), f"{value}%", 44, base.WHITE, width - 30)


def draw_red_x(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, pulse: float = 1.0) -> None:
    radius = size * pulse / 2
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(30, 4, 12, 205), outline=(*base.RED, 245), width=7)
    pad = radius * 0.48
    draw.line((x - pad, y - pad, x + pad, y + pad), fill=(*base.RED, 255), width=20)
    draw.line((x + pad, y - pad, x - pad, y + pad), fill=(*base.RED, 255), width=20)


def star_points(cx: float, cy: float, outer: float, inner: float, points: int = 5) -> list[tuple[float, float]]:
    result = []
    for index in range(points * 2):
        radius = outer if index % 2 == 0 else inner
        angle = -math.pi / 2 + index * math.pi / points
        result.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
    return result


def draw_particles(image: Image.Image, t: float, color: tuple[int, int, int], count: int = 28) -> None:
    layer, draw = alpha_layer(image)
    for index in range(count):
        phase = (t * (0.6 + (index % 5) * 0.07) + index * 0.137) % 1
        x = (index * 97 + int(t * 180)) % (W + 40) - 20
        y = int(-40 + phase * (H + 80))
        size = 5 + index % 6
        draw.rectangle((x, y, x + size, y + size * 2), fill=(*color, 210))
    image.alpha_composite(layer)


def draw_portals(image: Image.Image, t: float) -> None:
    layer, draw = alpha_layer(image)
    labels = [("2000", base.YELLOW), ("2026", base.CYAN), ("2050", base.RED)]
    active = int((t - 2.8) / 0.32) % 3
    for index, (label, color) in enumerate(labels):
        x = 100 + index * 170
        r = 68 + (10 if index == active else 0)
        for glow in range(30, 0, -8):
            draw.ellipse((x - r - glow, 330 - r - glow, x + r + glow, 330 + r + glow), outline=(*color, 20 + glow), width=7)
        draw.ellipse((x - r, 330 - r, x + r, 330 + r), fill=(4, 8, 18, 210), outline=(*color, 255), width=7)
        draw_text(draw, (x, 330), label, 29, color, 125)
    draw_text(draw, (W / 2, 470), "?", 88, base.WHITE, 120)
    image.alpha_composite(layer)


def draw_score(image: Image.Image, winner_2000: bool) -> None:
    layer, draw = alpha_layer(image)
    draw.rounded_rectangle((42, 180, W - 42, 500), radius=38, fill=(4, 8, 18, 242), outline=(*base.CYAN, 245), width=6)
    for index, (year, color) in enumerate((("2000", base.YELLOW), ("2026", base.WHITE), ("2050", base.RED))):
        y = 250 + index * 90
        draw_text(draw, (145, y), year, 30, color, 150)
        if index == 0 and winner_2000:
            draw.polygon(star_points(350, y, 43, 20), fill=(*base.YELLOW, 245), outline=(*base.WHITE, 230))
            draw_text(draw, (445, y), "+1", 34, base.GREEN, 80)
        elif index == 1 and not winner_2000:
            draw_red_x(draw, 365, y, 66, 1.0)
            draw_text(draw, (445, y), "0", 34, base.RED, 70)
        else:
            draw.ellipse((335, y - 22, 379, y + 22), outline=(*base.GRAY, 190), width=4)
    image.alpha_composite(layer)


def draw_adapter_stack(image: Image.Image, t: float, cut: dict[str, Any]) -> None:
    layer, draw = alpha_layer(image)
    progress = base.clamp((t - cut["start"]) / (cut["end"] - cut["start"]))
    count = max(1, min(6, 1 + int(progress * 6)))
    colors = [base.CYAN, base.YELLOW, base.PURPLE, base.GREEN, base.RED, base.WHITE]
    for index in range(count):
        x = 190 + index * 28
        y = 690 - index * 42
        wobble = math.sin(t * 16 + index) * 9
        draw.rounded_rectangle((x + wobble, y, x + 115 + wobble, y + 55), radius=14, fill=(*colors[index], 235), outline=(*base.INK, 240), width=4)
        draw.ellipse((x + 18 + wobble, y + 16, x + 31 + wobble, y + 29), fill=(*base.INK, 230))
        draw.ellipse((x + 43 + wobble, y + 16, x + 56 + wobble, y + 29), fill=(*base.INK, 230))
    image.alpha_composite(layer)


def draw_spinner(image: Image.Image, t: float) -> None:
    layer, draw = alpha_layer(image)
    cx, cy, r = 395, 590, 72
    for index in range(12):
        angle = t * 8 + index * math.tau / 12
        alpha = int(40 + 210 * (index + 1) / 12)
        x = cx + math.cos(angle) * r
        y = cy + math.sin(angle) * r
        draw.ellipse((x - 10, y - 10, x + 10, y + 10), fill=(*base.CYAN, alpha))
    draw_text(draw, (cx, cy), "...", 36, base.WHITE, 100)
    image.alpha_composite(layer)


def draw_free_button(image: Image.Image, t: float) -> None:
    layer, draw = alpha_layer(image)
    pulse = 1 + 0.05 * math.sin(t * 12)
    width, height = 350 * pulse, 150 * pulse
    x0, y0 = W / 2 - width / 2, 510 - height / 2
    draw.rounded_rectangle((x0, y0, x0 + width, y0 + height), radius=35, fill=(6, 70, 45, 235), outline=(*base.GREEN, 250), width=7)
    draw_text(draw, (W / 2, 490), "FREE?!", 54, base.GREEN, 300)
    draw.ellipse((W / 2 - 34, 535, W / 2 + 34, 603), fill=(*base.GREEN, 245), outline=(*base.WHITE, 240), width=5)
    image.alpha_composite(layer)


def draw_scan(image: Image.Image, t: float, cut: dict[str, Any], stock_frames: list[Image.Image]) -> None:
    layer, draw = alpha_layer(image)
    progress = base.clamp((t - cut["start"]) / (cut["end"] - cut["start"]))
    y = 170 + progress * 610
    draw.rectangle((100, y - 10, 440, y + 10), fill=(*base.CYAN, 210))
    draw.rectangle((120, 170, 420, y), outline=(*base.CYAN, 80), width=5)
    image.alpha_composite(layer)
    previous.draw_pexels_hologram(image, t, stock_frames)


def draw_energy_arrow(image: Image.Image, t: float) -> None:
    layer, draw = alpha_layer(image)
    # Heart icon on Volt, phone battery destination, and one unmistakable direction.
    heart_x, heart_y = 215, 520
    draw.ellipse((heart_x - 34, heart_y - 25, heart_x + 3, heart_y + 12), fill=(*base.RED, 240))
    draw.ellipse((heart_x - 3, heart_y - 25, heart_x + 34, heart_y + 12), fill=(*base.RED, 240))
    draw.polygon([(heart_x - 34, heart_y - 4), (heart_x + 34, heart_y - 4), (heart_x, heart_y + 50)], fill=(*base.RED, 240))
    end = (390, 650)
    draw_arrow(draw, (245, 550), end, base.YELLOW, 13)
    draw_battery(draw, 350, 610, int(10 + 50 * base.clamp((t - 31.4) / 2.1)), base.GREEN, 145, 68)
    image.alpha_composite(layer)


def draw_dual_meters(image: Image.Image, phone: int, character_energy: int) -> None:
    layer, draw = alpha_layer(image)
    for y, kind, value, color in ((704, "phone", phone, base.GREEN), (794, "capybara", character_energy, base.RED)):
        draw.rounded_rectangle((35, y, W - 35, y + 70), radius=20, fill=(4, 8, 18, 235), outline=(*color, 240), width=4)

        # First-time viewers do not know the character's name. Pictograms make
        # both energy sources readable without exposition or a proper noun.
        icon_x, icon_y = 92, y + 35
        if kind == "phone":
            draw.rounded_rectangle((icon_x - 18, icon_y - 27, icon_x + 18, icon_y + 27), radius=7, fill=(7, 19, 30, 245), outline=(*base.CYAN, 245), width=4)
            draw.rounded_rectangle((icon_x - 10, icon_y - 17, icon_x + 10, icon_y + 10), radius=3, fill=(*base.GREEN, 225))
            draw.ellipse((icon_x - 3, icon_y + 16, icon_x + 3, icon_y + 22), fill=(*base.WHITE, 235))
        else:
            energy_ratio = max(0.0, min(1.0, value / 100))
            fur_live = (190, 129, 82)
            fur_empty = (105, 111, 118)
            fur = tuple(int(fur_empty[i] + (fur_live[i] - fur_empty[i]) * energy_ratio) for i in range(3))
            draw.ellipse((icon_x - 27, icon_y - 27, icon_x - 7, icon_y - 8), fill=(*fur, 245), outline=(*base.INK, 230), width=2)
            draw.ellipse((icon_x + 7, icon_y - 27, icon_x + 27, icon_y - 8), fill=(*fur, 245), outline=(*base.INK, 230), width=2)
            draw.ellipse((icon_x - 26, icon_y - 22, icon_x + 26, icon_y + 24), fill=(*fur, 245), outline=(*base.WHITE, 190), width=3)
            draw.ellipse((icon_x - 16, icon_y - 7, icon_x - 9, icon_y), fill=(*base.INK, 245))
            draw.ellipse((icon_x + 9, icon_y - 7, icon_x + 16, icon_y), fill=(*base.INK, 245))
            draw.ellipse((icon_x - 16, icon_y + 2, icon_x + 16, icon_y + 21), fill=(216, 166, 126, 235))
            draw.ellipse((icon_x - 5, icon_y + 5, icon_x + 5, icon_y + 12), fill=(*base.INK, 245))

        draw.rounded_rectangle((140, y + 19, 415, y + 51), radius=14, fill=(255, 255, 255, 40))
        fill_width = int(265 * max(0, min(100, value)) / 100)
        if fill_width:
            draw.rounded_rectangle((145, y + 24, 145 + fill_width, y + 46), radius=11, fill=(*color, 245))
        draw_text(draw, (468, y + 35), f"{value}%", 21, color, 88)
    image.alpha_composite(layer)


def draw_countdown(image: Image.Image, t: float, cut: dict[str, Any]) -> None:
    progress = base.clamp((t - cut["start"]) / (cut["end"] - cut["start"]))
    number = max(1, 3 - int(progress * 3))
    layer, draw = alpha_layer(image)
    radius = 105 + 14 * math.sin(t * 16)
    draw.ellipse((W / 2 - radius, 250 - radius, W / 2 + radius, 250 + radius), fill=(30, 4, 12, 220), outline=(*base.RED, 250), width=8)
    draw_text(draw, (W / 2, 250), str(number), 110, base.WHITE, 180)
    image.alpha_composite(layer)


def draw_cta(image: Image.Image, cut_id: str, t: float) -> None:
    """Story-integrated micro CTA rail; keeps the moving scene unobstructed.

    The old centered modal covered most of Volt and the orb. This layout uses a
    compact left-side circuit, one highlighted action at a time, and a visible
    energy pulse into the ongoing charging scene.
    """
    active_step = {"c21": 0, "c22": 1, "c23": 2, "c24": 3}[cut_id]
    layer, draw = alpha_layer(image)
    x0, x1 = 42, 192
    rail_x = x1 + 10
    card_h = 60
    card_gap = 12
    top = 230
    labels = ("LOCKED", "LIKE", "SUB", "COMMENT")

    # Thin diegetic circuit: it powers the charging action instead of pausing it.
    draw.line((rail_x, top + card_h / 2, rail_x, top + 3 * (card_h + card_gap) + card_h / 2), fill=(*base.GRAY, 145), width=5)
    powered_end = top + active_step * (card_h + card_gap) + card_h / 2
    if active_step:
        draw.line((rail_x, top + card_h / 2, rail_x, powered_end), fill=(*base.GREEN, 235), width=7)
        draw.line((rail_x, powered_end, 270, 600), fill=(*base.GREEN, 150), width=5)
        pulse = (t * 2.8) % 1.0
        px = rail_x + (270 - rail_x) * pulse
        py = powered_end + (600 - powered_end) * pulse
        draw.ellipse((px - 7, py - 7, px + 7, py + 7), fill=(*base.YELLOW, 245), outline=(*base.WHITE, 210), width=2)

    for step, label in enumerate(labels):
        y0 = top + step * (card_h + card_gap)
        complete = step <= active_step
        current = step == active_step
        pulse = 1.0 + (0.035 * math.sin(t * 18) if current else 0.0)
        card_w = (x1 - x0) * pulse
        cx = (x0 + x1) / 2
        left, right = cx - card_w / 2, cx + card_w / 2
        fill = (6, 75, 48, 220) if complete else (4, 8, 18, 165)
        outline = base.GREEN if complete else base.GRAY
        draw.rounded_rectangle((left, y0, right, y0 + card_h), radius=17, fill=fill, outline=(*outline, 235), width=4 if current else 2)

        icon_x = left + 25
        icon_y = y0 + card_h / 2
        icon_color = base.YELLOW if current else (base.GREEN if complete else base.GRAY)
        if step == 0:  # padlock
            draw.arc((icon_x - 11, icon_y - 20, icon_x + 11, icon_y + 3), 190, -10, fill=(*icon_color, 245), width=5)
            draw.rounded_rectangle((icon_x - 14, icon_y - 3, icon_x + 14, icon_y + 20), radius=5, fill=(*icon_color, 230))
        elif step == 1:  # heart/like
            draw.ellipse((icon_x - 14, icon_y - 12, icon_x, icon_y + 2), fill=(*icon_color, 240))
            draw.ellipse((icon_x, icon_y - 12, icon_x + 14, icon_y + 2), fill=(*icon_color, 240))
            draw.polygon([(icon_x - 14, icon_y - 4), (icon_x + 14, icon_y - 4), (icon_x, icon_y + 17)], fill=(*icon_color, 240))
        elif step == 2:  # play/subscribe
            draw.rounded_rectangle((icon_x - 16, icon_y - 13, icon_x + 16, icon_y + 13), radius=7, fill=(*icon_color, 235))
            draw.polygon([(icon_x - 4, icon_y - 8), (icon_x - 4, icon_y + 8), (icon_x + 10, icon_y)], fill=(*base.INK, 245))
        else:  # comment
            draw.rounded_rectangle((icon_x - 16, icon_y - 13, icon_x + 16, icon_y + 10), radius=7, fill=(*icon_color, 235))
            draw.polygon([(icon_x - 8, icon_y + 7), (icon_x - 13, icon_y + 18), (icon_x + 2, icon_y + 8)], fill=(*icon_color, 235))

        draw_text(draw, (left + 94, icon_y - (7 if step == 3 and current else 0)), label, 18 if label != "COMMENT" else 15, base.WHITE, 92)
        if step == 3 and current:
            draw_text(draw, (left + 94, icon_y + 13), "CHARGE", 11, base.YELLOW, 88)
        if complete and not current:
            draw.ellipse((right - 18, y0 + 8, right - 6, y0 + 20), fill=(*base.GREEN, 245))

    image.alpha_composite(layer)


def draw_update(image: Image.Image, t: float, cut: dict[str, Any]) -> None:
    layer, draw = alpha_layer(image)
    draw.rounded_rectangle((50, 190, W - 50, 490), radius=36, fill=(4, 8, 18, 245), outline=(*base.RED, 245), width=7)
    draw_text(draw, (W / 2, 270), "UPDATE", 58, base.RED, 360)
    progress = base.clamp((t - cut["start"]) / (cut["end"] - cut["start"]))
    draw.rounded_rectangle((90, 350, W - 90, 420), radius=25, fill=(255, 255, 255, 45))
    draw.rounded_rectangle((98, 358, 98 + int((W - 196) * progress), 412), radius=20, fill=(*base.CYAN, 245))
    image.alpha_composite(layer)


def render_frame(t: float, spec: dict[str, Any], stock_frames: list[Image.Image]) -> Image.Image:
    cut = active_cut(spec, t)
    image = previous.reframe(previous.source_frame(cut, t), cut["id"]).convert("RGBA")
    if cut["id"] in {"c04", "c05", "c09", "c25", "c27"}:
        image = comic_shake(image, t, 5.5).convert("RGBA")
    composite_vignette(image)
    draw_era_badge(image, cut)
    cut_id = cut["id"]

    if cut_id == "c01":
        layer, draw = alpha_layer(image)
        value = 1
        draw_battery(draw, 245, 120, value, base.RED, 245, 100)
        image.alpha_composite(layer)
        draw_speed_lines(image, t, base.RED)
    elif cut_id == "c02":
        layer, draw = alpha_layer(image)
        end = (440 + 18 * math.sin(t * 8), 680)
        draw_arrow(draw, (300, 480), end, base.YELLOW, 14)
        image.alpha_composite(layer)
    elif cut_id == "c03":
        draw_portals(image, t)
    elif cut_id == "c04":
        layer, draw = alpha_layer(image)
        draw.polygon(star_points(W / 2, 340, 180, 90, 12), fill=(*base.YELLOW, 230), outline=(*base.RED, 245))
        draw_text(draw, (W / 2, 340), "GO!", 92, base.INK, 300)
        image.alpha_composite(layer)
    elif cut_id == "c05":
        layer, draw = alpha_layer(image)
        y = 170 + 190 * base.clamp((t - cut["start"]) / 0.9)
        draw.rounded_rectangle((330, y, 500, y + 150), radius=25, fill=(65, 55, 50, 235), outline=(*base.YELLOW, 240), width=6)
        draw.line((355, y + 150, 355, y + 185), fill=(*base.WHITE, 240), width=9)
        draw.line((395, y + 150, 395, y + 185), fill=(*base.WHITE, 240), width=9)
        draw_arrow(draw, (415, 120), (415, y - 10), base.RED, 12)
        image.alpha_composite(layer)
    elif cut_id == "c06":
        layer, draw = alpha_layer(image)
        for index in range(6):
            x = 245 + index * 32
            y = 620 + math.sin(t * 14 + index) * 20
            draw.line((x, y, x + 15, y - 25), fill=(*base.GREEN, 235), width=6)
        image.alpha_composite(layer)
    elif cut_id == "c07":
        progress = base.clamp((t - cut["start"]) / 1.25)
        layer, draw = alpha_layer(image)
        draw_battery(draw, 140, 125, int(1 + 99 * progress), base.GREEN if progress > 0.65 else base.YELLOW, 300, 105)
        image.alpha_composite(layer)
        if progress > 0.6:
            draw_particles(image, t, base.YELLOW, 34)
    elif cut_id == "c08":
        draw_score(image, True)
    elif cut_id in {"c09", "c10"}:
        layer, draw = alpha_layer(image)
        pulse = 1 + 0.10 * math.sin(t * 15)
        draw_red_x(draw, 375 if cut_id == "c09" else 225, 570, 150, pulse)
        image.alpha_composite(layer)
    elif cut_id == "c11":
        draw_adapter_stack(image, t, cut)
    elif cut_id == "c12":
        layer, draw = alpha_layer(image)
        draw.line((90, 650, 300, 650), fill=(*base.WHITE, 245), width=14)
        draw.line((355, 650, 470, 650), fill=(*base.WHITE, 245), width=14)
        draw_arrow(draw, (330, 610), (302, 610), base.RED, 8)
        draw_arrow(draw, (325, 610), (353, 610), base.RED, 8)
        draw_text(draw, (327, 700), "!", 64, base.RED, 80)
        image.alpha_composite(layer)
    elif cut_id == "c13":
        draw_spinner(image, t)
    elif cut_id == "c14":
        draw_score(image, False)
    elif cut_id == "c15":
        draw_speed_lines(image, t, base.CYAN)
    elif cut_id == "c16":
        draw_free_button(image, t)
    elif cut_id == "c17":
        draw_scan(image, t, cut, stock_frames)
    elif cut_id == "c18":
        draw_energy_arrow(image, t)
    elif cut_id == "c19":
        progress = base.clamp((t - cut["start"]) / (cut["end"] - cut["start"]))
        draw_dual_meters(image, int(5 + 80 * progress), int(95 - 65 * progress))
    elif cut_id == "c20":
        draw_countdown(image, t, cut)
    elif cut_id in {"c21", "c22", "c23", "c24"}:
        draw_cta(image, cut_id, t)
    elif cut_id == "c25":
        layer, draw = alpha_layer(image)
        draw_battery(draw, 120, 120, 100, base.GREEN, 320, 115)
        image.alpha_composite(layer)
        draw_particles(image, t, base.GREEN, 42)
        draw_speed_lines(image, t, base.GREEN)
    elif cut_id == "c26":
        draw_dual_meters(image, 100, 0)
    elif cut_id == "c27":
        layer, draw = alpha_layer(image)
        for index in range(5):
            angle = t * 3 + index * math.tau / 5
            x = W / 2 + math.cos(angle) * 120
            y = 330 + math.sin(angle) * 45
            draw.polygon(star_points(x, y, 24, 11), fill=(*base.YELLOW, 245))
        image.alpha_composite(layer)
    elif cut_id == "c28":
        draw_update(image, t, cut)
    elif cut_id == "c29":
        layer, draw = alpha_layer(image)
        draw_battery(draw, 245, 120, 1, base.RED, 245, 100)
        draw_arrow(draw, (430, 600), (470, 690), base.YELLOW, 11)
        image.alpha_composite(layer)

    # Persistent moving watermark and progress line stay outside the action/UI zones.
    base.draw_watermark(ImageDraw.Draw(image, "RGBA"), t)
    layer, draw = alpha_layer(image)
    draw.rounded_rectangle((12, H - 14, W - 12, H - 7), radius=4, fill=(255, 255, 255, 55))
    draw.rounded_rectangle((12, H - 14, 12 + int((W - 24) * base.clamp(t / DURATION)), H - 7), radius=4, fill=(*base.CYAN, 245))
    image.alpha_composite(layer)
    return image.convert("RGB")


def render_visual(spec: dict[str, Any], stock_frames: list[Image.Image]) -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-vf",
        f"scale={OUT_W}:{OUT_H}:flags=lanczos,format=yuv420p", "-an", "-c:v", "libx264",
        "-preset", "medium", "-crf", "17", "-profile:v", "high", "-level:v", "4.2",
        "-r", str(FPS), "-fps_mode", "cfr", "-movflags", "+faststart", VISUAL,
    ]
    process = subprocess.Popen([str(item) for item in command], stdin=subprocess.PIPE)
    assert process.stdin is not None
    total = int(DURATION * FPS)
    try:
        for frame_index in range(total):
            process.stdin.write(render_frame(frame_index / FPS, spec, stock_frames).tobytes())
            if frame_index % 300 == 0:
                print(f"frame {frame_index}/{total}", flush=True)
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError("visual encoder failed")


def cartoon_sfx(event: str) -> np.ndarray:
    if event in {"alarm", "plug", "success", "collapse", "update_alert", "cta_lock", "cta_unlock", "scan", "orb_hover", "energy_drain"}:
        return base.sfx(event)
    if event in {"tick", "ticks", "scanner_ticks"}:
        return np.concatenate([base.tone(0.035, 1250, 0.10), base.tone(0.045, 800, 0.07)])
    if event in {"whoosh", "slip", "flip", "magic_whoosh", "rewind"}:
        sweep = -900 if event == "rewind" else 900
        return np.concatenate([base.noise(0.12, 0.07), base.tone(0.24, 160 if sweep > 0 else 900, 0.10, sweep=sweep)])
    if event in {"bonk", "bonk_light"}:
        gain = 0.18 if event == "bonk" else 0.11
        return np.concatenate([base.tone(0.08, 105, gain, "sine"), base.noise(0.10, gain * 0.65)])
    if event in {"pop", "button_pop"}:
        return np.concatenate([base.noise(0.035, 0.13), base.tone(0.11, 540, 0.10, sweep=900)])
    if event in {"sparkle", "battery_fill", "fast_fill"}:
        return np.concatenate([base.tone(0.09, 660, 0.08), base.tone(0.09, 990, 0.09), base.tone(0.15, 1480, 0.09)])
    if event in {"confetti", "tiny_cymbal"}:
        return np.concatenate([base.noise(0.35, 0.07, False), base.tone(0.16, 1700, 0.055)])
    if event in {"error", "danger", "danger_reveal", "record_stop"}:
        return np.concatenate([base.tone(0.13, 220, 0.12, "square"), base.tone(0.18, 150, 0.13, "square")])
    if event == "stretch":
        return base.tone(0.55, 150, 0.08, sweep=950)
    if event == "snap":
        return np.concatenate([base.noise(0.045, 0.20), base.tone(0.10, 100, 0.14)])
    if event in {"roulette", "start_horn", "score_ding"}:
        return np.concatenate([base.tone(0.10, 440, 0.08), base.tone(0.10, 660, 0.09), base.tone(0.15, 880, 0.10)])
    if event in {"falling_whistle", "wobble", "comic_groan", "fail_trombone"}:
        start = 1000 if event == "falling_whistle" else 330
        sweep = -1200 if event == "falling_whistle" else -280
        return base.tone(0.65 if event != "wobble" else 0.45, start, 0.095, sweep=sweep)
    if event in {"energy_link", "countdown"}:
        return np.concatenate([base.tone(0.18, 240, 0.10), base.tone(0.10, 480, 0.075)])
    return base.tone(0.12, 440, 0.08)


SFX_EVENTS = [
    (0.02,"alarm"),(0.82,"tick"),(1.40,"whoosh"),(2.18,"slip"),(2.82,"roulette"),(3.18,"tick"),(3.58,"tick"),(3.98,"tick"),(4.40,"start_horn"),
    (5.52,"falling_whistle"),(6.35,"bonk"),(7.52,"plug"),(8.18,"sparkle"),(9.52,"battery_fill"),(10.60,"success"),(11.15,"confetti"),(11.62,"score_ding"),
    (13.02,"error"),(14.38,"bonk_light"),(15.02,"flip"),(16.42,"error"),(17.22,"pop"),(17.88,"pop"),(18.58,"pop"),(19.52,"stretch"),(20.45,"tick"),(21.32,"snap"),(21.82,"update_alert"),(22.72,"comic_groan"),(23.62,"fail_trombone"),
    (25.02,"magic_whoosh"),(25.72,"orb_hover"),(27.02,"sparkle"),(28.36,"button_pop"),(29.22,"scan"),(30.26,"scanner_ticks"),(31.42,"danger_reveal"),(32.16,"energy_link"),(33.52,"battery_fill"),(34.02,"energy_drain"),(34.85,"countdown"),(35.72,"countdown"),(36.48,"countdown"),(37.24,"countdown"),
    (38.02,"cta_lock"),(39.42,"button_pop"),(40.42,"button_pop"),(41.42,"button_pop"),(42.18,"cta_unlock"),(42.42,"success"),(43.20,"confetti"),(44.52,"record_stop"),(45.30,"danger"),(46.52,"wobble"),(47.08,"collapse"),(47.76,"tiny_cymbal"),(48.52,"update_alert"),(49.02,"fast_fill"),(49.52,"rewind"),(50.18,"alarm"),
]


def synthesize_audio() -> Path:
    AUDIO.parent.mkdir(parents=True, exist_ok=True)
    count = int(DURATION * SAMPLE_RATE)
    t = np.arange(count, dtype=np.float32) / SAMPLE_RATE
    # Bright, bouncy era beds. Speech-free by construction.
    arp_freqs = np.array([220.0, 330.0, 440.0, 660.0])
    arp_index = ((t * 8).astype(int) % len(arp_freqs))
    analog = 0.022 * np.sign(np.sin(math.tau * arp_freqs[arp_index] * t))
    digital = 0.025 * np.sin(math.tau * 73.42 * t) + 0.012 * np.sin(math.tau * 880 * t) * (np.sin(math.tau * 4 * t) > 0)
    future = 0.020 * np.sin(math.tau * 110 * t) + 0.014 * np.sin(math.tau * 111.4 * t) + 0.010 * np.sin(math.tau * 660 * t)
    mono = np.where(t < 13, analog, np.where(t < 25, digital, future)).astype(np.float32)
    score = np.column_stack((mono, mono * 0.96)).astype(np.float32)
    # Quarter-second microbeat sustains playful momentum without replacing event SFX.
    for at in np.arange(0, DURATION, 0.25):
        frequency = 520 if at < 13 else (680 if at < 25 else 420)
        gain = 0.020 if int(at * 4) % 2 else 0.030
        base.add_clip(score, base.tone(0.032, frequency, gain), float(at))
    for at, event in SFX_EVENTS:
        base.add_clip(score, cartoon_sfx(event), at, 1.0)
    peak = float(np.max(np.abs(score)))
    if peak > 0.82:
        score *= 0.82 / peak
    pcm16 = (np.clip(score, -0.95, 0.95) * 32767).astype(np.int16)
    with wave.open(str(AUDIO), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(pcm16.tobytes())
    return AUDIO


def main() -> None:
    spec = load_storyboard()
    frame_provenance = previous.prepare_generated_frames()
    stock_frames = base.prepare_pexels_frames()
    render_visual(spec, stock_frames)
    audio = synthesize_audio()
    base.mux(VISUAL, audio, FINAL, DURATION)
    actual = previous.probe_duration(FINAL)
    if abs(actual - DURATION) > 0.08:
        raise RuntimeError(f"duration mismatch: {actual}")
    cuts = spec["cuts"]
    manifest = {
        "artifact": str(FINAL.relative_to(ROOT)),
        "artifact_sha256": base.sha256(FINAL),
        "artifact_size_bytes": FINAL.stat().st_size,
        "renderer": str(Path(__file__).resolve().relative_to(ROOT)),
        "storyboard": str(STORYBOARD.relative_to(ROOT)),
        "storyboard_sha256": base.sha256(STORYBOARD),
        "duration_seconds": actual,
        "fps": FPS,
        "canvas": [OUT_W, OUT_H],
        "cut_count": len(cuts),
        "minimum_cut_seconds": min(c["end"] - c["start"] for c in cuts),
        "maximum_cut_seconds": max(c["end"] - c["start"] for c in cuts),
        "tts": False,
        "source_speech": False,
        "sfx_event_count": len(SFX_EVENTS),
        "sfx_density_per_second": round(len(SFX_EVENTS) / DURATION, 3),
        "generated_sources": previous.SOURCES,
        "generated_frame_cache": frame_provenance,
        "additional_higgsfield_credits": 0,
        "cumulative_higgsfield_credits_for_source_pack": 41.5,
        "higgsfield_balance_after_source_pack": 214.85,
        "pexels": json.loads(base.LICENSE.read_text(encoding="utf-8"))["approved"],
        "status": "rendered; exact-final V6 media QC pending",
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2, default=str) + "\n", encoding="utf-8")
    print(FINAL)


if __name__ == "__main__":
    main()
