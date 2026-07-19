#!/usr/bin/env python3
"""Render the project caption calibration artifact at 1080x1920.

This calibrates ffmpeg/Pillow pixel dimensions to the visual intent of the
CapCut size-16/stroke-60 reference. CapCut units are not ffmpeg pixels.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PROFILE_PATH = HERE / "caption-profile.json"
WORK = HERE / "work"
FINAL = HERE / "caption-calibration.mp4"
CONTACT_SHEET = HERE / "caption-calibration-contact-sheet.png"
MOBILE_PREVIEW = HERE / "caption-calibration-mobile.png"


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, check=True)


def load_profile() -> dict:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def fit_font(font_path: Path, text: str, requested_size: int, max_width: int, stroke: int) -> ImageFont.FreeTypeFont:
    size = requested_size
    while size >= 48:
        font = ImageFont.truetype(font_path, size)
        if font.getlength(text) + 2 * stroke <= max_width:
            return font
        size -= 1
    raise ValueError(f"Caption cannot fit safely: {text!r}")


def make_card(
    *,
    font_path: Path,
    words: list[str],
    keyword_index: int,
    base_size: int,
    keyword_size: int,
    stroke: int,
    center_y: int,
    max_width: int,
    output: Path,
) -> None:
    canvas = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    base_font = fit_font(font_path, " ".join(words), base_size, max_width, stroke)
    scale = base_font.size / base_size
    keyword_font = ImageFont.truetype(font_path, round(keyword_size * scale))
    space = base_font.getlength(" ")
    widths = [
        (keyword_font if index == keyword_index else base_font).getlength(word)
        for index, word in enumerate(words)
    ]
    total_width = sum(widths) + space * (len(words) - 1)
    if total_width + 2 * stroke > max_width:
        # Preserve safe width over the keyword bump when a phrase is close to the edge.
        keyword_font = base_font
        widths[keyword_index] = base_font.getlength(words[keyword_index])
        total_width = sum(widths) + space * (len(words) - 1)
    x = (1080 - total_width) / 2
    ascents = [
        (keyword_font if index == keyword_index else base_font).getmetrics()[0]
        for index in range(len(words))
    ]
    baseline = center_y + max(ascents) / 2
    for index, word in enumerate(words):
        font = keyword_font if index == keyword_index else base_font
        ascent = font.getmetrics()[0]
        y = baseline - ascent
        draw.text(
            (round(x), round(y)),
            word,
            font=font,
            fill="#FFD400" if index == keyword_index else "white",
            stroke_width=stroke,
            stroke_fill="black",
        )
        x += widths[index] + space
    canvas.save(output)


def main() -> None:
    profile = load_profile()
    config = profile["ffmpeg_profile"]
    width = profile["output"]["width"]
    height = profile["output"]["height"]
    center_y = round(height * config["caption_center_y_ratio"])
    max_width = round(width * (1 - 2 * config["horizontal_margin_ratio"]))

    shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir(parents=True)

    english = WORK / "english.png"
    vietnamese = WORK / "vietnamese.png"
    make_card(
        font_path=ROOT / profile["fonts"]["english"],
        words=["WATCH", "THIS", "CLOSELY"],
        keyword_index=2,
        base_size=config["english"]["base_font_size_px"],
        keyword_size=config["english"]["keyword_font_size_px"],
        stroke=config["stroke_width_px"],
        center_y=center_y,
        max_width=max_width,
        output=english,
    )
    make_card(
        font_path=ROOT / profile["fonts"]["vietnamese"],
        words=["ĐỪNG", "BỎ", "LỠ", "ĐIỀU", "NÀY"],
        keyword_index=4,
        base_size=config["vietnamese"]["base_font_size_px"],
        keyword_size=config["vietnamese"]["keyword_font_size_px"],
        stroke=config["stroke_width_px"],
        center_y=center_y,
        max_width=max_width,
        output=vietnamese,
    )

    filter_graph = (
        "[0:v]drawgrid=w=120:h=120:t=2:c=white@0.08,"
        "drawbox=x='mod(t*140,1380)-300':y=250:w=300:h=1420:color=0x2563EB@0.28:t=fill,"
        "drawbox=x='1080-mod(t*95,1300)':y=480:w=220:h=980:color=0xEF4444@0.20:t=fill[bg];"
        "[1:v]format=rgba[en];[2:v]format=rgba[vi];"
        "[bg][en]overlay=0:0:enable='lt(t,4)'[v1];"
        "[v1][vi]overlay=0:0:enable='gte(t,4)',format=yuv420p[v]"
    )
    run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=0x101826:s=1080x1920:r=30:d=8",
            "-loop", "1", "-i", str(english),
            "-loop", "1", "-i", str(vietnamese),
            "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo:d=8",
            "-filter_complex", filter_graph,
            "-map", "[v]", "-map", "3:a",
            "-t", "8", "-r", "30",
            "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
            str(FINAL),
        ]
    )
    run(
        [
            "ffmpeg", "-y", "-i", str(FINAL),
            "-vf", "select='eq(n,30)+eq(n,150)',scale=270:480:flags=lanczos,tile=2x1",
            "-frames:v", "1", "-update", "1", str(CONTACT_SHEET),
        ]
    )
    run(
        [
            "ffmpeg", "-y", "-ss", "5", "-i", str(FINAL),
            "-vf", "scale=360:640:flags=lanczos", "-frames:v", "1", "-update", "1", str(MOBILE_PREVIEW),
        ]
    )
    shutil.rmtree(WORK)
    print(FINAL)
    print(CONTACT_SHEET)
    print(MOBILE_PREVIEW)


if __name__ == "__main__":
    main()
