#!/usr/bin/env python3
"""Finish OUTWISHED SHOT-001 V3 with calibrated captions, pointer, and VO."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / "docs/verification/caption-calibration/caption-profile.json"
RAW = ROOT / "output/projects/outwished/shots/shot-001-v3-raw.mp4"
VOICE = ROOT / "output/projects/outwished/shots/shot-001-v3-vo-liam.wav"
WORK = ROOT / "output/projects/outwished/work/shot-001-v3"
FINAL = ROOT / "output/projects/outwished/shots/shot-001-v3-hook.mp4"
CONTACT_SHEET = ROOT / "output/projects/outwished/analysis/shot-001-v3-hook-contact-sheet.png"
MOBILE_PREVIEW = ROOT / "output/projects/outwished/analysis/shot-001-v3-hook-mobile.png"
DURATION = 4.062993


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, check=True)


def fit_font(font_path: Path, text: str, requested_size: int, max_width: int, stroke: int) -> ImageFont.FreeTypeFont:
    size = requested_size
    while size >= 48:
        font = ImageFont.truetype(font_path, size)
        if font.getlength(text) + 2 * stroke <= max_width:
            return font
        size -= 1
    raise ValueError(f"Caption cannot fit safely: {text!r}")


def make_caption(
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


def make_pointer(output: Path) -> None:
    canvas = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    color = (255, 212, 0, 255)
    draw.line((820, 555, 970, 610), fill=(0, 0, 0, 230), width=34)
    draw.line((820, 555, 970, 610), fill=color, width=18)
    draw.polygon([(970, 610), (915, 575), (930, 635)], fill=(0, 0, 0, 230))
    draw.polygon([(965, 606), (925, 580), (936, 625)], fill=color)
    canvas.save(output)


def main() -> None:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    config = profile["ffmpeg_profile"]
    font_path = ROOT / profile["fonts"]["english"]
    center_y = round(profile["output"]["height"] * config["caption_center_y_ratio"])
    max_width = round(profile["output"]["width"] * (1 - 2 * config["horizontal_margin_ratio"]))

    shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir(parents=True)
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    CONTACT_SHEET.parent.mkdir(parents=True, exist_ok=True)

    cards = [
        ("caption-1.png", ["THAT", "OFFICER"], 1),
        ("caption-2.png", ["KNEW", "MY", "SAFE", "CODE"], 2),
        ("caption-3.png", ["I'D", "NEVER", "MET", "HIM"], 1),
    ]
    for filename, words, keyword_index in cards:
        make_caption(
            font_path=font_path,
            words=words,
            keyword_index=keyword_index,
            base_size=config["english"]["base_font_size_px"],
            keyword_size=config["english"]["keyword_font_size_px"],
            stroke=config["stroke_width_px"],
            center_y=center_y,
            max_width=max_width,
            output=WORK / filename,
        )
    make_pointer(WORK / "pointer.png")

    filter_graph = (
        "[2:v]format=rgba,fade=t=in:st=0.20:d=0.08:alpha=1,fade=t=out:st=0.74:d=0.08:alpha=1[c1];"
        "[3:v]format=rgba,fade=t=in:st=0.82:d=0.08:alpha=1,fade=t=out:st=2.27:d=0.08:alpha=1[c2];"
        "[4:v]format=rgba,fade=t=in:st=2.40:d=0.08:alpha=1,fade=t=out:st=3.64:d=0.08:alpha=1[c3];"
        "[5:v]format=rgba,fade=t=in:st=0:d=0.08:alpha=1,fade=t=out:st=0.82:d=0.18:alpha=1[ptr];"
        "[0:v][ptr]overlay=0:0:enable='between(t,0,1.00)'[v1];"
        "[v1][c1]overlay=0:0:enable='between(t,0.20,0.82)'[v2];"
        "[v2][c2]overlay=0:0:enable='between(t,0.82,2.35)'[v3];"
        "[v3][c3]overlay=0:0:enable='between(t,2.40,3.72)',format=yuv420p[vout];"
        "[0:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.28[bed];"
        "[1:a]aresample=48000,aformat=channel_layouts=stereo,highpass=f=70,"
        "acompressor=threshold=0.1:ratio=4:attack=5:release=100:makeup=1,"
        "loudnorm=I=-16:TP=-1.5:LRA=10[voice];"
        f"[bed][voice]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.94,atrim=0:{DURATION:.6f}[aout]"
    )

    command = ["ffmpeg", "-y", "-i", str(RAW), "-i", str(VOICE)]
    for filename, _, _ in cards:
        command.extend(["-loop", "1", "-t", f"{DURATION:.6f}", "-i", str(WORK / filename)])
    command.extend(["-loop", "1", "-t", f"{DURATION:.6f}", "-i", str(WORK / "pointer.png")])
    command.extend(
        [
            "-filter_complex", filter_graph,
            "-map", "[vout]", "-map", "[aout]",
            "-t", f"{DURATION:.6f}", "-r", "24",
            "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
            str(FINAL),
        ]
    )
    run(command)
    run(
        [
            "ffmpeg", "-y", "-v", "error", "-i", str(FINAL),
            "-vf", "fps=2,scale=270:-1:flags=lanczos,tile=4x2:padding=4:margin=4:color=black",
            "-frames:v", "1", str(CONTACT_SHEET),
        ]
    )
    run(
        [
            "ffmpeg", "-y", "-v", "error", "-ss", "2.70", "-i", str(FINAL),
            "-vf", "scale=360:640:flags=lanczos", "-frames:v", "1", "-update", "1", str(MOBILE_PREVIEW),
        ]
    )
    print(FINAL)
    print(CONTACT_SHEET)
    print(MOBILE_PREVIEW)


if __name__ == "__main__":
    main()
