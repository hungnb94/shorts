#!/usr/bin/env python3
"""Render the 3-second Stage-0 hook prototype for paperclip_v1."""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "paperclip"
PAPERCLIP_FRAME = PROJECT / "checks-v1" / "source-scout" / "cbc-paperclip-25_5.jpg"
HOUSE = PROJECT / "stock" / "mixkit-4009-house.mp4"
VOICE = PROJECT / "tts-qwen" / "fitted" / "00_hook.wav"
FONT = ROOT / "assets" / "fonts" / "Komika-Axis.ttf"
OUT = PROJECT / "hook-gate" / "paperclip-hook-v1.mp4"
OVERLAY = PROJECT / "hook-gate" / "hook-overlay.png"


def make_overlay() -> None:
    canvas = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    def centered(
        text: str,
        y: int,
        size: int,
        fill: tuple[int, int, int, int],
        stroke: int = 0,
    ) -> None:
        font = ImageFont.truetype(str(FONT), size)
        box = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
        width = box[2] - box[0]
        draw.text(
            ((1080 - width) / 2, y),
            text,
            font=font,
            fill=fill,
            stroke_width=stroke,
            stroke_fill=(0, 0, 0, 255),
        )

    draw.rounded_rectangle((62, 312, 1018, 863), radius=28, outline=(244, 63, 94, 255), width=8)
    draw.rounded_rectangle((62, 937, 1018, 1488), radius=28, outline=(34, 197, 94, 255), width=8)
    centered("CAN THIS", 66, 76, (255, 225, 90, 255))
    centered("PAPERCLIP", 145, 102, (255, 255, 255, 255), 4)
    draw.rounded_rectangle((82, 793, 545, 850), radius=12, fill=(0, 0, 0, 190))
    draw.text((96, 804), "CBC NEWS ARCHIVE  2006", font=ImageFont.truetype(str(FONT), 31), fill=(255, 255, 255, 255))
    centered("DOWN TO", 875, 48, (255, 225, 90, 255))
    draw.rounded_rectangle((82, 1418, 500, 1475), radius=12, fill=(0, 0, 0, 190))
    draw.text((96, 1429), "HOUSE  ILLUSTRATION", font=ImageFont.truetype(str(FONT), 31), fill=(255, 255, 255, 255))
    centered("BUY THAT HOUSE?", 1545, 88, (255, 255, 255, 255), 5)
    centered("ONE TRADE AT A TIME", 1680, 50, (34, 197, 94, 255), 3)
    OVERLAY.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OVERLAY)


def main() -> None:
    for path in (PAPERCLIP_FRAME, HOUSE, VOICE, FONT):
        if not path.is_file():
            raise FileNotFoundError(path)
    OUT.parent.mkdir(parents=True, exist_ok=True)

    make_overlay()
    vf = (
        "color=c=0x05070D:s=1080x1920:r=30:d=3[base];"
        "[0:v]crop=860:490:210:120,scale=940:535:flags=lanczos,"
        "zoompan=z='min(zoom+0.0006,1.04)':"
        "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=90:s=940x535:fps=30,"
        "format=yuv420p[paper];"
        "[1:v]trim=duration=3,setpts=PTS-STARTPTS,"
        "scale=940:535:force_original_aspect_ratio=increase:flags=lanczos,"
        "crop=940:535,eq=saturation=1.1:contrast=1.04[house];"
        "[base][paper]overlay=70:320:shortest=1[v1];"
        "[v1][house]overlay=70:945:shortest=1[v2];"
        "[v2][2:v]overlay=0:0:shortest=1,format=yuv420p[v]"
    )
    af = (
        "[3:a]atrim=0:3,apad=whole_dur=3,atrim=0:3,"
        "loudnorm=I=-16:TP=-1.5:LRA=8,aresample=48000[a]"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-loop",
            "1",
            "-framerate",
            "30",
            "-i",
            str(PAPERCLIP_FRAME),
            "-stream_loop",
            "-1",
            "-i",
            str(HOUSE),
            "-loop",
            "1",
            "-framerate",
            "30",
            "-i",
            str(OVERLAY),
            "-i",
            str(VOICE),
            "-filter_complex",
            vf + ";" + af,
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-t",
            "3",
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "16",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-movflags",
            "+faststart",
            str(OUT),
        ],
        check=True,
    )
    print(OUT)


if __name__ == "__main__":
    main()
