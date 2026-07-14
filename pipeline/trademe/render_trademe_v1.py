#!/usr/bin/env python3
"""Render Trade Me V1: Proof-First Worst-Trade Reversal.

Accepted brief: ADR-0027.
Output: 1080x1920 H.264/AAC MP4, 45.53s, source-footage share <50%.
"""

from __future__ import annotations

import json
import math
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "trademe"
SOURCE = PROJECT / "source"
WORK = PROJECT / "clips" / "v1_work"
PANELS = WORK / "panels"
TTS = WORK / "tts"
CHECKS = WORK / "checks"
FINAL = PROJECT / "final" / "2026-07-14-trademe_v1_worst_trade_house.mp4"
EDGE_TTS = Path.home() / ".local/bin/edge-tts"
EDGE_TTS_VOICE = "en-US-AriaNeural"
MAX_POST_TEMPO = 1.15

WIDTH = 1080
HEIGHT = 1920
FPS = 30
TOTAL_FRAMES = 1366
TOTAL_DURATION = TOTAL_FRAMES / FPS
SOURCE_FRAMES = 652
SOURCE_SHARE = SOURCE_FRAMES / TOTAL_FRAMES

FONT_REGULAR = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")

WHITE = "#F8FAFC"
MUTED = "#AAB8C8"
NAVY = "#07111F"
PANEL = "#101F33"
YELLOW = "#FFD447"
GREEN = "#4EE6A8"
RED = "#FF5A67"
CYAN = "#55C7FF"
GOLD = "#E9B949"

SOURCES = {
    "opening": SOURCE / "6830088912174910726.mp4",
    "card": SOURCE / "6959642654208494853.mp4",
    "trailer": SOURCE / "7037989725776416006.mp4",
    "house": SOURCE / "7040511124625755397.mp4",
}


@dataclass(frozen=True)
class Clip:
    name: str
    frames: int
    path: Path


@dataclass(frozen=True)
class TTSLine:
    name: str
    start_frame: int
    frames: int
    text: str
    synthesis_text: str
    rate_percent: int
    pitch_hz: int


def run(args: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(str(arg) for arg in args))
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=capture,
    )


def probe(path: Path) -> dict[str, Any]:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(path),
        ],
        capture=True,
    )
    return json.loads(result.stdout)


def probe_duration(path: Path) -> float:
    return float(probe(path)["format"]["duration"])


def max_volume_db(path: Path, *, start: float | None = None, duration: float | None = None) -> float:
    args = ["ffmpeg", "-hide_banner"]
    if start is not None:
        args.extend(["-ss", f"{start:.6f}"])
    args.extend(["-i", str(path)])
    if duration is not None:
        args.extend(["-t", f"{duration:.6f}"])
    args.extend(["-vn", "-af", "volumedetect", "-f", "null", "-"])
    result = subprocess.run(args, cwd=ROOT, check=True, text=True, capture_output=True)
    match = re.search(r"max_volume:\s*(-?\d+(?:\.\d+)?) dB", result.stderr)
    if not match:
        raise RuntimeError(f"Could not measure max volume for {path}")
    return float(match.group(1))


def assert_not_silent(path: Path, *, label: str, threshold_db: float = -40.0, start: float | None = None, duration: float | None = None) -> float:
    measured = max_volume_db(path, start=start, duration=duration)
    if measured <= threshold_db:
        raise AssertionError(f"{label} is silent: max_volume={measured:.1f} dB, threshold={threshold_db:.1f} dB")
    print(f"AUDIO PASS {label}: max_volume={measured:.1f} dB")
    return measured


def require_inputs() -> None:
    missing = [str(path) for path in [*SOURCES.values(), FONT_REGULAR, FONT_BOLD, EDGE_TTS] if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required inputs:\n" + "\n".join(missing))
    for directory in [WORK, PANELS, TTS, CHECKS, FINAL.parent]:
        directory.mkdir(parents=True, exist_ok=True)


def font(size: int, *, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size=size)


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, start: int, floor: int = 42) -> ImageFont.FreeTypeFont:
    for size in range(start, floor - 1, -2):
        candidate = font(size)
        if draw.textbbox((0, 0), text, font=candidate)[2] <= max_width:
            return candidate
    return font(floor)


def wrap_lines(draw: ImageDraw.ImageDraw, text: str, max_width: int, start: int, max_lines: int = 2) -> tuple[list[str], ImageFont.FreeTypeFont]:
    for size in range(start, 48, -2):
        candidate = font(size)
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            trial = word if not current else f"{current} {word}"
            if draw.textbbox((0, 0), trial, font=candidate)[2] <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        if len(lines) <= max_lines:
            return lines, candidate
    return [text], fit_font(draw, text, max_width, 50, 42)


def centered_text(draw: ImageDraw.ImageDraw, text: str, y: int, *, size: int, color: str = WHITE, max_width: int = 900, max_lines: int = 2, spacing: int = 12) -> int:
    lines, chosen = wrap_lines(draw, text, max_width, size, max_lines=max_lines)
    line_height = chosen.size + spacing
    for index, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=chosen, stroke_width=1)
        x = (WIDTH - (bbox[2] - bbox[0])) // 2
        draw.text((x, y + index * line_height), line, font=chosen, fill=color, stroke_width=1, stroke_fill="#000000")
    return int(y + len(lines) * line_height)


def background() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), NAVY)
    draw = ImageDraw.Draw(image)
    top = (7, 17, 31)
    bottom = (17, 37, 60)
    for y in range(HEIGHT):
        ratio = y / (HEIGHT - 1)
        color = tuple(round(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(3))
        draw.line((0, y, WIDTH, y), fill=color)
    for x in range(40, WIDTH, 120):
        draw.line((x, 0, x, HEIGHT), fill="#10243A", width=1)
    for y in range(40, HEIGHT, 120):
        draw.line((0, y, WIDTH, y), fill="#10243A", width=1)
    draw.ellipse((780, -120, 1220, 320), fill="#102C42")
    draw.ellipse((-240, 1500, 260, 2020), fill="#0D2B35")
    return image


def draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str = YELLOW, width: int = 18) -> None:
    draw.line((*start, *end), fill=color, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    length = 42
    for offset in (2.55, -2.55):
        point = (end[0] + length * math.cos(angle + offset), end[1] + length * math.sin(angle + offset))
        draw.line((*end, *point), fill=color, width=width)


def draw_card(draw: ImageDraw.ImageDraw, center: tuple[int, int], scale: float = 1.0) -> None:
    width = int(420 * scale)
    height = int(250 * scale)
    x = center[0] - width // 2
    y = center[1] - height // 2
    draw.rounded_rectangle((x, y, x + width, y + height), radius=int(30 * scale), fill="#39151D", outline=GOLD, width=max(5, int(10 * scale)))
    draw.rounded_rectangle((x + int(28 * scale), y + int(28 * scale), x + width - int(28 * scale), y + height - int(28 * scale)), radius=int(20 * scale), outline="#8B6332", width=max(3, int(5 * scale)))
    title = "CELEBRITY"
    title_font = font(max(24, int(48 * scale)))
    bbox = draw.textbbox((0, 0), title, font=title_font)
    draw.text((center[0] - (bbox[2] - bbox[0]) // 2, center[1] - int(48 * scale)), title, font=title_font, fill=GOLD)
    sub_font = font(max(18, int(30 * scale)))
    sub = "CARD"
    bbox = draw.textbbox((0, 0), sub, font=sub_font)
    draw.text((center[0] - (bbox[2] - bbox[0]) // 2, center[1] + int(34 * scale)), sub, font=sub_font, fill=WHITE)


def draw_tractor(draw: ImageDraw.ImageDraw, origin: tuple[int, int], scale: float = 1.0, color: str = RED) -> None:
    x, y = origin
    draw.ellipse((x, y + int(150 * scale), x + int(135 * scale), y + int(285 * scale)), fill="#071018", outline=WHITE, width=4)
    draw.ellipse((x + int(300 * scale), y + int(190 * scale), x + int(390 * scale), y + int(280 * scale)), fill="#071018", outline=WHITE, width=4)
    draw.rounded_rectangle((x + int(70 * scale), y + int(95 * scale), x + int(340 * scale), y + int(225 * scale)), radius=int(20 * scale), fill=color)
    draw.rectangle((x + int(145 * scale), y + int(10 * scale), x + int(265 * scale), y + int(125 * scale)), fill="#183B55", outline=WHITE, width=4)
    draw.line((x + int(305 * scale), y + int(95 * scale), x + int(340 * scale), y + int(25 * scale)), fill=WHITE, width=8)


def draw_pin(draw: ImageDraw.ImageDraw, center: tuple[int, int], scale: float = 1.0) -> None:
    x, y = center
    length = int(520 * scale)
    gap = int(34 * scale)
    width = max(10, int(18 * scale))
    draw.line((x - length // 2, y - gap, x + length // 2, y + gap), fill=WHITE, width=width)
    draw.line((x - length // 2, y + gap, x + length // 2, y - gap), fill=WHITE, width=width)
    draw.arc((x - length // 2 - gap, y - 2 * gap, x - length // 2 + 2 * gap, y + 2 * gap), 70, 290, fill=YELLOW, width=width)
    draw.ellipse((x + length // 2 - gap, y - gap, x + length // 2 + gap, y + gap), outline=YELLOW, width=width)


def draw_trailer(draw: ImageDraw.ImageDraw, origin: tuple[int, int], scale: float = 1.0) -> None:
    x, y = origin
    width = int(480 * scale)
    height = int(300 * scale)
    draw.rounded_rectangle((x, y, x + width, y + height), radius=int(18 * scale), fill="#D9E3E8", outline=WHITE, width=7)
    draw.rectangle((x + int(45 * scale), y + int(65 * scale), x + int(175 * scale), y + int(185 * scale)), fill="#79BCE0", outline="#29465A", width=6)
    draw.rectangle((x + int(310 * scale), y + int(85 * scale), x + int(430 * scale), y + height), fill="#8B684B", outline="#29465A", width=6)
    draw.ellipse((x + int(70 * scale), y + height - int(5 * scale), x + int(175 * scale), y + height + int(100 * scale)), fill="#071018", outline=WHITE, width=4)
    draw.ellipse((x + int(315 * scale), y + height - int(5 * scale), x + int(420 * scale), y + height + int(100 * scale)), fill="#071018", outline=WHITE, width=4)
    draw.line((x + width, y + height - int(30 * scale), x + width + int(115 * scale), y + height + int(20 * scale)), fill=WHITE, width=10)


def draw_house(draw: ImageDraw.ImageDraw, origin: tuple[int, int], scale: float = 1.0) -> None:
    x, y = origin
    width = int(480 * scale)
    height = int(300 * scale)
    draw.rectangle((x, y + int(160 * scale), x + width, y + int(160 * scale) + height), fill="#F2E6D0", outline=WHITE, width=7)
    draw.polygon([(x - int(35 * scale), y + int(170 * scale)), (x + width // 2, y), (x + width + int(35 * scale), y + int(170 * scale))], fill=RED, outline=WHITE)
    draw.rectangle((x + int(195 * scale), y + int(265 * scale), x + int(290 * scale), y + int(460 * scale)), fill="#6C4B3D", outline=WHITE, width=5)
    for window_x in (x + int(70 * scale), x + int(350 * scale)):
        draw.rectangle((window_x, y + int(235 * scale), window_x + int(75 * scale), y + int(330 * scale)), fill=CYAN, outline="#29465A", width=5)


def draw_person(draw: ImageDraw.ImageDraw, center: tuple[int, int], color: str = GREEN, scale: float = 1.0) -> None:
    x, y = center
    radius = int(58 * scale)
    width = max(8, int(16 * scale))
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    draw.line((x, y + radius, x, y + int(230 * scale)), fill=color, width=width)
    draw.line((x, y + int(115 * scale), x - int(110 * scale), y + int(180 * scale)), fill=color, width=width)
    draw.line((x, y + int(115 * scale), x + int(110 * scale), y + int(180 * scale)), fill=color, width=width)
    draw.line((x, y + int(230 * scale), x - int(85 * scale), y + int(350 * scale)), fill=color, width=width)
    draw.line((x, y + int(230 * scale), x + int(85 * scale), y + int(350 * scale)), fill=color, width=width)


def draw_visual(draw: ImageDraw.ImageDraw, visual: str, accent: str) -> None:
    if visual == "tractors":
        for index, (x, y) in enumerate(((105, 720), (360, 860), (610, 720))):
            draw_tractor(draw, (x, y), scale=0.72, color=accent if index == 1 else RED)
    elif visual == "card":
        draw_card(draw, (WIDTH // 2, 925), 1.28)
    elif visual == "criticism":
        draw_card(draw, (WIDTH // 2, 960), 0.95)
        for x, y, text in ((95, 680, "NO BUYER"), (665, 720, "TOO NICHE"), (105, 1170, "BAD DEAL?")):
            draw.rounded_rectangle((x, y, x + 320, y + 110), radius=28, fill="#33151B", outline=RED, width=5)
            chosen = fit_font(draw, text, 275, 38, 28)
            draw.text((x + 24, y + 33), text, font=chosen, fill=RED)
    elif visual == "pin":
        draw_pin(draw, (WIDTH // 2, 940), 1.25)
    elif visual == "cars_cabin":
        draw.rounded_rectangle((90, 745, 400, 1040), radius=40, fill="#15314B", outline=CYAN, width=7)
        draw.ellipse((135, 985, 220, 1070), fill="#071018", outline=WHITE, width=4)
        draw.ellipse((285, 985, 370, 1070), fill="#071018", outline=WHITE, width=4)
        draw.rectangle((140, 835, 350, 985), fill=CYAN)
        draw_arrow(draw, (430, 930), (585, 930), YELLOW, 16)
        draw_house(draw, (650, 770), 0.62)
    elif visual == "search":
        draw_card(draw, (330, 965), 0.68)
        draw.ellipse((555, 715, 930, 1090), outline=accent, width=24)
        draw.line((830, 1015, 995, 1200), fill=accent, width=34)
        for radius in (105, 175):
            draw.ellipse((742 - radius, 902 - radius, 742 + radius, 902 + radius), outline="#31536A", width=5)
    elif visual == "buyer":
        draw_card(draw, (280, 955), 0.62)
        draw_arrow(draw, (470, 955), (635, 955), accent, 18)
        draw_person(draw, (805, 810), accent, 0.85)
        draw.ellipse((680, 685, 930, 935), outline=YELLOW, width=10)
    elif visual == "value_card":
        draw_card(draw, (WIDTH // 2, 860), 0.92)
        chosen = font(150)
        text = "$20K"
        bbox = draw.textbbox((0, 0), text, font=chosen)
        draw.text(((WIDTH - (bbox[2] - bbox[0])) // 2, 1110), text, font=chosen, fill=YELLOW)
    elif visual == "value_fit":
        draw_card(draw, (260, 920), 0.58)
        draw_person(draw, (820, 765), GREEN, 0.7)
        draw_arrow(draw, (445, 920), (650, 920), GREEN, 22)
        chosen = font(145)
        draw.text((420, 1115), "BUYER FIT", font=fit_font(draw, "BUYER FIT", 700, 118, 72), fill=GREEN)
    elif visual == "value_trailer":
        draw_trailer(draw, (245, 755), 1.2)
        chosen = font(150)
        text = "$40K"
        bbox = draw.textbbox((0, 0), text, font=chosen)
        draw.text(((WIDTH - (bbox[2] - bbox[0])) // 2, 1190), text, font=chosen, fill=GREEN)
    elif visual == "route":
        draw_trailer(draw, (120, 785), 0.72)
        draw_arrow(draw, (565, 1020), (820, 1020), accent, 18)
        draw.text((665, 800), "CANADA", font=font(46), fill=MUTED)
        draw.text((650, 1110), "TENNESSEE", font=font(46), fill=WHITE)
    elif visual == "flipper":
        draw_person(draw, (245, 770), GREEN, 0.68)
        draw_trailer(draw, (470, 790), 0.78)
        draw.ellipse((120, 665, 370, 915), outline=YELLOW, width=10)
    elif visual == "house":
        draw_house(draw, (260, 700), 1.15)
    elif visual == "cross_item":
        draw_card(draw, (WIDTH // 2, 920), 0.92)
        draw.line((240, 680, 845, 1210), fill=RED, width=30)
        draw.line((845, 680, 240, 1210), fill=RED, width=30)
    elif visual == "right_buyer":
        draw_card(draw, (270, 940), 0.58)
        draw_person(draw, (790, 765), GREEN, 0.78)
        draw_arrow(draw, (455, 940), (625, 940), GREEN, 22)
    elif visual == "formula":
        draw_card(draw, (230, 920), 0.48)
        draw.text((455, 860), "×", font=font(130), fill=YELLOW)
        draw_person(draw, (780, 790), GREEN, 0.62)
        draw.text((395, 1190), "= VALUE", font=font(100), fill=WHITE)
    else:
        raise ValueError(f"Unknown visual: {visual}")


def make_panel(path: Path, *, headline: str, subtitle: str, visual: str, accent: str, stage: str, citation: str = "") -> None:
    image = background()
    draw = ImageDraw.Draw(image)
    draw.text((72, 70), "MONEY BLINDSPOT  /  PROOF-FIRST", font=font(30), fill=MUTED)
    stage_font = fit_font(draw, stage, 410, 30, 24)
    stage_bbox = draw.textbbox((0, 0), stage, font=stage_font)
    stage_x = WIDTH - 72 - (stage_bbox[2] - stage_bbox[0]) - 38
    draw.rounded_rectangle((stage_x - 20, 58, WIDTH - 72, 112), radius=22, fill=accent)
    draw.text((stage_x, 72), stage, font=stage_font, fill=NAVY)
    draw.rounded_rectangle((55, 180, WIDTH - 55, 1500), radius=52, fill=PANEL, outline="#25425E", width=4)
    centered_text(draw, headline, 255, size=94, color=accent, max_width=900, max_lines=2)
    draw_visual(draw, visual, accent)
    centered_text(draw, subtitle, 1360, size=52, color=WHITE, max_width=860, max_lines=2)
    if citation:
        citation_font = fit_font(draw, citation, 880, 30, 24)
        citation_bbox = draw.textbbox((0, 0), citation, font=citation_font)
        draw.text(((WIDTH - (citation_bbox[2] - citation_bbox[0])) // 2, 1535), citation, font=citation_font, fill=MUTED)
    draw.rounded_rectangle((70, 1810, WIDTH - 70, 1822), radius=6, fill="#223C55")
    image.save(path, quality=95)


def encode_args() -> list[str]:
    return [
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "18",
        "-profile:v",
        "high",
        "-level",
        "4.2",
        "-pix_fmt",
        "yuv420p",
        "-r",
        str(FPS),
        "-g",
        str(FPS * 2),
        "-keyint_min",
        str(FPS * 2),
        "-sc_threshold",
        "0",
        "-video_track_timescale",
        "90000",
    ]


def render_panel_clip(name: str, image: Path, frames: int) -> Clip:
    output = WORK / f"{name}.mp4"
    zoom = "zoompan=z='min(max(zoom,pzoom)+0.00045,1.035)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,format=yuv420p"
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-loop",
            "1",
            "-framerate",
            str(FPS),
            "-i",
            str(image),
            "-vf",
            zoom,
            "-frames:v",
            str(frames),
            "-an",
            *encode_args(),
            str(output),
        ]
    )
    return Clip(name, frames, output)


def render_source_clip(name: str, source: Path, start: float, frames: int) -> Clip:
    output = WORK / f"{name}.mp4"
    source_badge = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},setsar=1,fps={FPS},"
        "eq=contrast=1.04:saturation=1.05,"
        "drawbox=x=34:y=44:w=325:h=62:color=black@0.68:t=fill,"
        f"drawtext=fontfile='{FONT_BOLD}':text='@TRADEMEPROJECT':expansion=none:"
        "x=55:y=61:fontsize=31:fontcolor=white,format=yuv420p"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(source),
            "-ss",
            f"{start:.3f}",
            "-vf",
            source_badge,
            "-frames:v",
            str(frames),
            "-an",
            *encode_args(),
            str(output),
        ]
    )
    return Clip(name, frames, output)


def panel_specs() -> dict[str, dict[str, str]]:
    return {
        "crit_1": {"headline": "THREE TRACTORS", "subtitle": "VISIBLE, USEFUL ASSETS", "visual": "tractors", "accent": YELLOW, "stage": "THE DISPUTED TRADE"},
        "crit_2": {"headline": "ONE CELEBRITY CARD", "subtitle": "REPORTED VALUE: ABOUT $20K", "visual": "card", "accent": GOLD, "stage": "THE DISPUTED TRADE", "citation": "SOURCE: THE GUARDIAN"},
        "crit_3": {"headline": "“WORST TRADE”", "subtitle": "FOLLOWERS DOUBTED A BUYER EXISTED", "visual": "criticism", "accent": RED, "stage": "THE DISPUTED TRADE", "citation": "SOURCES: NBC NEWS + THE GUARDIAN"},
        "ladder_1": {"headline": "START: ONE BOBBY PIN", "subtitle": "ALMOST ZERO MARKET VALUE", "visual": "pin", "accent": YELLOW, "stage": "THE LADDER"},
        "ladder_2": {"headline": "CARS + A TINY CABIN", "subtitle": "EACH TRADE CHANGED THE BUYER POOL", "visual": "cars_cabin", "accent": CYAN, "stage": "THE LADDER"},
        "ladder_3": {"headline": "THEN: THREE TRACTORS", "subtitle": "THE ASSETS THAT BECAME THE CARD", "visual": "tractors", "accent": GREEN, "stage": "THE LADDER"},
        "buyer_1": {"headline": "LOW MARKET DEMAND", "subtitle": "MOST PEOPLE SAW A HARD-TO-SELL CARD", "visual": "card", "accent": MUTED, "stage": "COUNTERPARTY VALUE"},
        "buyer_2": {"headline": "SEARCH FOR BUYER FIT", "subtitle": "VALUE CHANGES WITH WHO CAN USE IT", "visual": "search", "accent": CYAN, "stage": "COUNTERPARTY VALUE"},
        "buyer_3": {"headline": "CHIPOTLE'S “BIGGEST FAN”", "subtitle": "ONE PERSON CARED MUCH MORE", "visual": "buyer", "accent": GREEN, "stage": "COUNTERPARTY VALUE", "citation": "SOURCES: NBC NEWS + THE GUARDIAN"},
        "value_1": {"headline": "REPORTED CARD VALUE", "subtitle": "A RARE, HARD-TO-PRICE ASSET", "visual": "value_card", "accent": YELLOW, "stage": "THE VALUE BRIDGE", "citation": "SOURCE: THE GUARDIAN"},
        "value_2": {"headline": "THE ITEM DIDN'T CHANGE", "subtitle": "THE COUNTERPARTY DID", "visual": "value_fit", "accent": GREEN, "stage": "THE VALUE BRIDGE"},
        "value_3": {"headline": "OFF-GRID TRAILER", "subtitle": "REPORTED VALUE DOUBLED", "visual": "value_trailer", "accent": GREEN, "stage": "THE VALUE BRIDGE", "citation": "SOURCES: NBC NEWS + THE GUARDIAN"},
        "house_1": {"headline": "THE TRAILER MOVED", "subtitle": "CANADA TO TENNESSEE", "visual": "route", "accent": CYAN, "stage": "THE FINAL BUYER"},
        "house_2": {"headline": "A HOUSE FLIPPER WANTED IT", "subtitle": "THIS BUYER HAD WAITED FOR THE RIGHT TRADE", "visual": "flipper", "accent": YELLOW, "stage": "THE FINAL BUYER", "citation": "SOURCE: NBC NEWS"},
        "house_3": {"headline": "THE FINAL OFFER", "subtitle": "TRAILER FOR A HOUSE", "visual": "house", "accent": GREEN, "stage": "THE FINAL BUYER"},
        "insight_1": {"headline": "A BETTER ITEM?", "subtitle": "THAT WASN'T THE BOTTLENECK", "visual": "cross_item", "accent": RED, "stage": "THE MONEY BLINDSPOT"},
        "insight_2": {"headline": "THE RIGHT BUYER", "subtitle": "THAT UNLOCKED THE NEXT TRADE", "visual": "right_buyer", "accent": GREEN, "stage": "THE MONEY BLINDSPOT"},
        "insight_3": {"headline": "VALUE = ITEM × BUYER FIT", "subtitle": "SAME ITEM. DIFFERENT OUTCOME.", "visual": "formula", "accent": YELLOW, "stage": "THE MONEY BLINDSPOT"},
    }


def render_video_timeline() -> list[Clip]:
    specs = panel_specs()
    for name, spec in specs.items():
        make_panel(PANELS / f"{name}.png", **spec)

    clips: list[Clip] = []
    clips.append(render_source_clip("00_hook_card", SOURCES["card"], 44.0, 120))
    for index in range(1, 4):
        clips.append(render_panel_clip(f"01_crit_{index}", PANELS / f"crit_{index}.png", 35))
    clips.append(render_source_clip("02_bobby_pin", SOURCES["opening"], 0.0, 96))
    for index in range(1, 4):
        clips.append(render_panel_clip(f"03_ladder_{index}", PANELS / f"ladder_{index}.png", 38))
    clips.append(render_source_clip("04_tractor", SOURCES["card"], 30.0, 96))
    for index in range(1, 4):
        clips.append(render_panel_clip(f"05_buyer_{index}", PANELS / f"buyer_{index}.png", 38))
    clips.append(render_source_clip("06_trailer", SOURCES["trailer"], 8.26, 160))
    for index in range(1, 4):
        clips.append(render_panel_clip(f"07_value_{index}", PANELS / f"value_{index}.png", 40))
    for index in range(1, 4):
        clips.append(render_panel_clip(f"08_house_{index}", PANELS / f"house_{index}.png", 40))
    clips.append(render_source_clip("09_house_reveal", SOURCES["house"], 27.0, 180))
    for index in range(1, 4):
        clips.append(render_panel_clip(f"10_insight_{index}", PANELS / f"insight_{index}.png", 47))

    actual_frames = sum(clip.frames for clip in clips)
    if actual_frames != TOTAL_FRAMES:
        raise AssertionError(f"Timeline frame mismatch: {actual_frames} != {TOTAL_FRAMES}")
    return clips


def concat_video(clips: list[Clip]) -> Path:
    concat_file = WORK / "concat.txt"
    concat_file.write_text("".join(f"file '{clip.path.resolve()}'\n" for clip in clips), encoding="utf-8")
    base = WORK / "base_video.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(base)])
    return base


def tts_lines() -> list[TTSLine]:
    return [
        TTSLine("hook", 0, 120, "Her followers called this her worst trade.", "Her followers called this... her worst trade.", 8, 3),
        TTSLine("criticism", 120, 105, "Three tractors for one Chipotle card—who wants it?", "Three tractors for one Chipotle card—who wants it?", 14, 2),
        TTSLine("start", 225, 96, "But this started with a single bobby pin.", "But this started with... a single bobby pin.", 10, 4),
        TTSLine("ladder", 321, 114, "That pin climbed through cars and a cabin into three tractors.", "That pin climbed through cars and a cabin—into three tractors.", 14, 3),
        TTSLine("swap", 435, 96, "Then she swapped all three for the card.", "Then she swapped all three for the card.", 12, 2),
        TTSLine("buyer", 531, 114, "The crowd saw dead weight—but one buyer saw a dream.", "The crowd saw dead weight—but one buyer saw a dream.", 8, 4),
        TTSLine("value", 805, 120, "The same item doubled in reported value—with the right buyer.", "The same item doubled in reported value—with the right buyer.", 9, 1),
        TTSLine("house", 925, 120, "Then a house flipper wanted the trailer, and offered a house.", "Then a house flipper wanted the trailer—and offered a house.", 12, 3),
        TTSLine("insight", 1225, 141, "She didn't need a better item. She needed the right buyer.", "She didn't need a better item. She needed... the right buyer.", 4, 0),
    ]


def compute_fit_tempo(raw_duration: float, target_duration: float) -> float:
    speaking_target = target_duration - 0.18
    if speaking_target <= 0:
        raise ValueError("Target duration is too short for neural speech")
    required = raw_duration / speaking_target
    if required > MAX_POST_TEMPO:
        raise ValueError(
            f"Neural line exceeds its timing budget: required tempo {required:.3f}x > {MAX_POST_TEMPO:.2f}x"
        )
    return max(1.0, required)


def generate_tts() -> list[Path]:
    outputs: list[Path] = []
    report: list[dict[str, Any]] = []
    for line in tts_lines():
        raw = TTS / f"{line.name}_raw.mp3"
        fitted = TTS / f"{line.name}.wav"
        run(
            [
                str(EDGE_TTS),
                "--voice",
                EDGE_TTS_VOICE,
                "--rate",
                f"{line.rate_percent:+d}%",
                "--pitch",
                f"{line.pitch_hz:+d}Hz",
                "--text",
                line.synthesis_text,
                "--write-media",
                str(raw),
            ]
        )
        if not raw.exists() or raw.stat().st_size < 1_000:
            raise RuntimeError(f"Edge TTS produced an empty or invalid file: {raw}")

        raw_duration = probe_duration(raw)
        target = line.frames / FPS
        tempo = compute_fit_tempo(raw_duration, target)
        speech_duration = raw_duration / tempo
        if speech_duration > target - 0.15:
            raise RuntimeError(
                f"Neural line would be truncated: {line.name} speech={speech_duration:.3f}s target={target:.3f}s"
            )
        fade_out_start = max(0.0, speech_duration - 0.06)
        target_samples = round(target * 48_000)
        audio_filter = (
            f"atempo={tempo:.6f},"
            "highpass=f=75,"
            "acompressor=threshold=0.125:ratio=2.2:attack=5:release=80:makeup=2,"
            "afade=t=in:st=0:d=0.025,"
            f"afade=t=out:st={fade_out_start:.6f}:d=0.06,"
            "loudnorm=I=-16:TP=-1.5:LRA=9,"
            "aresample=48000:first_pts=0,"
            f"apad=whole_len={target_samples},atrim=end_sample={target_samples}"
        )
        run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-af", audio_filter, "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(fitted)])
        fitted_duration = probe_duration(fitted)
        if abs(fitted_duration - target) > 0.03:
            raise RuntimeError(
                f"Fitted TTS duration mismatch: {line.name} got={fitted_duration:.3f}s target={target:.3f}s"
            )
        assert_not_silent(fitted, label=f"neural TTS {line.name}")
        report.append(
            {
                "name": line.name,
                "voice": EDGE_TTS_VOICE,
                "rate_percent": line.rate_percent,
                "pitch_hz": line.pitch_hz,
                "raw_duration": round(raw_duration, 6),
                "post_tempo": round(tempo, 6),
                "speech_duration": round(speech_duration, 6),
                "target_duration": round(target, 6),
                "fitted_duration": round(fitted_duration, 6),
                "truncated": False,
            }
        )
        outputs.append(fitted)
    (CHECKS / "tts_energy_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return outputs


def extract_source_audio() -> tuple[Path, Path]:
    trailer = WORK / "trailer_source.wav"
    house = WORK / "house_source.wav"
    for source, start, frames, output, loudness in (
        (SOURCES["trailer"], 8.26, 160, trailer, -15),
        (SOURCES["house"], 27.0, 180, house, -14),
    ):
        duration = frames / FPS
        run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-ss",
                f"{start:.3f}",
                "-i",
                str(source),
                "-t",
                f"{duration:.6f}",
                "-vn",
                "-af",
                f"asetpts=PTS-STARTPTS,highpass=f=70,loudnorm=I={loudness}:TP=-1.5:LRA=10,afade=t=in:st=0:d=0.04,afade=t=out:st={duration - 0.08:.6f}:d=0.08",
                "-ar",
                "48000",
                "-ac",
                "2",
                "-c:a",
                "pcm_s16le",
                str(output),
            ]
        )
        assert_not_silent(output, label=f"source extract {output.name}")
    return trailer, house


def generate_music_and_sfx() -> tuple[Path, Path]:
    music = WORK / "music_bed.wav"
    sfx = WORK / "impact.wav"
    music_source = (
        "aevalsrc=(0.10*sin(2*PI*55*t)*(0.30+0.70*exp(-7*mod(t\\,0.5)))+"
        "0.025*sin(2*PI*110*t)+0.012*sin(2*PI*220*t))*"
        f"min(1\\,t/0.8)*min(1\\,({TOTAL_DURATION:.6f}-t)/0.8):s=48000:d={TOTAL_DURATION:.6f}"
    )
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", music_source, "-af", "lowpass=f=1200,highpass=f=35", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(music)])
    sfx_source = "aevalsrc=(0.28*sin(2*PI*(150-90*t)*t)+0.10*sin(2*PI*420*t))*exp(-10*t):s=48000:d=0.45"
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", sfx_source, "-af", "lowpass=f=1800", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(sfx)])
    return music, sfx


def ass_time(frame: int) -> str:
    seconds = frame / FPS
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remainder = seconds % 60
    return f"{hours}:{minutes:02d}:{remainder:05.2f}"


def make_subtitles() -> Path:
    ass = WORK / "captions.ass"
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,Arial,86,&H00FFFFFF,&H000000FF,&H00101924,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,8,70,70,230,1
Style: Caption,Arial,64,&H00FFFFFF,&H000000FF,&H00101924,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,2,70,70,235,1
Style: Source,Arial,62,&H00FFFFFF,&H000000FF,&H00101924,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,2,70,70,225,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events: list[tuple[int, int, str, str]] = [
        (0, 36, "Hook", "HER FOLLOWERS"),
        (36, 72, "Hook", "CALLED THIS HER"),
        (72, 120, "Hook", "{\\c&H005A5AFF&}WORST TRADE"),
        (120, 158, "Caption", "THREE TRACTORS"),
        (158, 188, "Caption", "BECAME ONE CARD"),
        (188, 225, "Caption", "NOBODY WOULD WANT IT?"),
        (225, 268, "Caption", "THIS STARTED WITH"),
        (268, 321, "Caption", "{\\c&H0047D4FF&}ONE BOBBY PIN"),
        (321, 359, "Caption", "CARS + A CABIN"),
        (359, 397, "Caption", "CLIMBED INTO"),
        (397, 435, "Caption", "{\\c&H00A8E64E&}THREE TRACTORS"),
        (435, 483, "Caption", "SHE SWAPPED ALL THREE"),
        (483, 531, "Caption", "FOR THE CARD"),
        (531, 569, "Caption", "HARD TO SELL"),
        (569, 607, "Caption", "UNTIL ONE BUYER"),
        (607, 645, "Caption", "{\\c&H00A8E64E&}SAW A DREAM"),
        (645, 668, "Source", "IN MY LAST TRADE..."),
        (678, 727, "Source", "THE CHIPOTLE CELEBRITY CARD"),
        (727, 767, "Source", "FOR AN OFF-GRID TRAILER"),
        (767, 805, "Source", "WORTH {\\c&H00A8E64E&}$40,000"),
        (805, 845, "Caption", "THE ITEM DIDN'T CHANGE"),
        (845, 885, "Caption", "THE RIGHT BUYER"),
        (885, 925, "Caption", "{\\c&H00A8E64E&}DOUBLED THE VALUE"),
        (925, 965, "Caption", "A HOUSE FLIPPER"),
        (965, 1005, "Caption", "WANTED THE TRAILER"),
        (1005, 1045, "Caption", "AND OFFERED A HOUSE"),
        (1045, 1086, "Source", "THE FINAL TRADE"),
        (1086, 1144, "Source", "OH MY GOD!"),
        (1144, 1225, "Source", "{\\c&H00A8E64E&}A HOUSE"),
        (1225, 1272, "Caption", "NOT A BETTER ITEM"),
        (1272, 1319, "Caption", "SHE NEEDED"),
        (1319, 1366, "Caption", "{\\c&H00A8E64E&}THE RIGHT BUYER"),
    ]
    lines = [header]
    for start, end, style, text in events:
        lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},{style},,0,0,0,,{text}\n")
    ass.write_text("".join(lines), encoding="utf-8")
    return ass


def mix_and_finish(base_video: Path, tts_files: list[Path], trailer_audio: Path, house_audio: Path, music: Path, sfx: Path, subtitles: Path) -> None:
    inputs: list[str] = ["-i", str(base_video), "-i", str(music)]
    for path in tts_files:
        inputs.extend(["-i", str(path)])
    trailer_index = 2 + len(tts_files)
    house_index = trailer_index + 1
    sfx_index = house_index + 1
    inputs.extend(["-i", str(trailer_audio), "-i", str(house_audio), "-i", str(sfx)])

    filter_lines: list[str] = []
    filter_lines.append(
        f"[1:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"volume='if(between(t,21.3,27.1),0.045,if(between(t,34.6,41.1),0.035,0.105))':eval=frame[music]"
    )
    mix_labels = ["[music]"]
    for index, line in enumerate(tts_lines(), start=2):
        delay = round(line.start_frame / FPS * 1000)
        label = f"tts{index}"
        filter_lines.append(f"[{index}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={delay}|{delay},volume=1.08[{label}]")
        mix_labels.append(f"[{label}]")

    trailer_delay = round(645 / FPS * 1000)
    house_delay = round(1045 / FPS * 1000)
    filter_lines.append(f"[{trailer_index}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={trailer_delay}|{trailer_delay},volume=1.05[trailer]")
    filter_lines.append(f"[{house_index}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={house_delay}|{house_delay},volume=1.12[house]")
    mix_labels.extend(["[trailer]", "[house]"])

    impact_frames = [0, 120, 225, 321, 435, 531, 645, 805, 925, 1045, 1225]
    sfx_outputs = "".join(f"[impact{i}]" for i in range(len(impact_frames)))
    filter_lines.append(f"[{sfx_index}:a]aresample=48000,aformat=channel_layouts=stereo,asplit={len(impact_frames)}{sfx_outputs}")
    for index, frame in enumerate(impact_frames):
        delay = round(frame / FPS * 1000)
        label = f"hit{index}"
        filter_lines.append(f"[impact{index}]adelay={delay}|{delay},volume=0.24[{label}]")
        mix_labels.append(f"[{label}]")

    filter_lines.append(
        "".join(mix_labels)
        + f"amix=inputs={len(mix_labels)}:duration=longest:normalize=0,"
        + f"alimiter=limit=0.94:attack=5:release=50,atrim=0:{TOTAL_DURATION:.6f}[aout]"
    )
    filter_script = WORK / "audio_mix.ffscript"
    filter_script.write_text(";\n".join(filter_lines) + "\n", encoding="utf-8")

    subtitle_filter = f"subtitles='{subtitles}':fontsdir='/System/Library/Fonts/Supplemental'"
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            *inputs,
            "-filter_complex_script",
            str(filter_script),
            "-map",
            "0:v:0",
            "-map",
            "[aout]",
            "-vf",
            subtitle_filter,
            "-frames:v",
            str(TOTAL_FRAMES),
            *encode_args(),
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            str(FINAL),
        ]
    )


def extract_checks() -> None:
    timestamps = [0.0, 0.2, 1.5, 3.2, 4.2, 7.7, 10.9, 14.7, 17.9, 21.7, 25.8, 27.0, 31.0, 35.0, 37.0, 40.5, 41.0, 44.8]
    for index, timestamp in enumerate(timestamps):
        output = CHECKS / f"{index:02d}_{timestamp:05.2f}.jpg"
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{timestamp:.2f}", "-i", str(FINAL), "-frames:v", "1", "-q:v", "2", str(output)])
    contact = CHECKS / "contact.jpg"
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(FINAL),
            "-vf",
            "fps=1/2.5,drawtext=fontfile='/System/Library/Fonts/HelveticaNeue.ttc':text='%{pts\\:hms}':x=10:y=10:fontsize=34:fontcolor=yellow:borderw=3:bordercolor=black,scale=270:-2:flags=lanczos,tile=5x4:padding=4:margin=4",
            "-frames:v",
            "1",
            str(contact),
        ]
    )


def validate() -> None:
    info = probe(FINAL)
    video = next(stream for stream in info["streams"] if stream["codec_type"] == "video")
    audio = next(stream for stream in info["streams"] if stream["codec_type"] == "audio")
    duration = float(info["format"]["duration"])
    assertions = {
        "width": video["width"] == WIDTH,
        "height": video["height"] == HEIGHT,
        "video_codec": video["codec_name"] == "h264",
        "audio_codec": audio["codec_name"] == "aac",
        "duration": 45.3 <= duration <= 45.8,
        "under_60s": duration <= 60.0,
        "source_share": SOURCE_SHARE <= 0.50,
    }
    failed = [name for name, passed in assertions.items() if not passed]
    if failed:
        raise AssertionError(f"Validation failed: {failed}\n{json.dumps(info, indent=2)}")
    trailer_window_max = assert_not_silent(
        FINAL,
        label="final trailer quote window",
        threshold_db=-25.0,
        start=645 / FPS,
        duration=160 / FPS,
    )
    house_window_max = assert_not_silent(
        FINAL,
        label="final house reaction window",
        threshold_db=-25.0,
        start=1045 / FPS,
        duration=180 / FPS,
    )
    run(["ffmpeg", "-v", "error", "-i", str(FINAL), "-f", "null", "-"])
    print(
        json.dumps(
            {
                "output": str(FINAL),
                "duration": duration,
                "resolution": f"{video['width']}x{video['height']}",
                "video_codec": video["codec_name"],
                "audio_codec": audio["codec_name"],
                "source_frames": SOURCE_FRAMES,
                "total_frames": TOTAL_FRAMES,
                "source_share_percent": round(SOURCE_SHARE * 100, 2),
                "trailer_window_max_db": trailer_window_max,
                "house_window_max_db": house_window_max,
                "decode_check": "passed",
            },
            indent=2,
        )
    )


def main() -> None:
    require_inputs()
    clips = render_video_timeline()
    base = concat_video(clips)
    tts_files = generate_tts()
    trailer_audio, house_audio = extract_source_audio()
    music, sfx = generate_music_and_sfx()
    subtitles = make_subtitles()
    mix_and_finish(base, tts_files, trailer_audio, house_audio, music, sfx, subtitles)
    extract_checks()
    validate()


if __name__ == "__main__":
    main()
