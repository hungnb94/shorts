#!/usr/bin/env python3
"""Render the full paperclip_v1 internal candidate from the verified EDL."""

from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "paperclip"
EDL = PROJECT / "scripts" / "visual-edl-v1.json"
EVIDENCE = PROJECT / "hook-gate" / "evidence.json"
AUDIO = PROJECT / "audio" / "narration-mix-v1.wav"
FONT_PATH = ROOT / "assets" / "fonts" / "Komika-Axis.ttf"
WORK = PROJECT / "work-v1"
BEAT_DIR = WORK / "beats"
OVERLAY_DIR = WORK / "overlays"
CARD_DIR = WORK / "cards"
VIDEO_ONLY = WORK / "paperclip-v1-video-only.mp4"
OUT = PROJECT / "2026-07-26-one-red-paperclip-v1-internal.mp4"
WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION = 61.5

WHITE = (248, 250, 252, 255)
YELLOW = (255, 225, 90, 255)
RED = (244, 63, 94, 255)
GREEN = (34, 197, 94, 255)
CYAN = (34, 211, 238, 255)
MUTED = (170, 182, 199, 255)
BG_TOP = (5, 7, 13)
BG_BOTTOM = (15, 23, 42)


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def safe(text: str) -> str:
    return (
        text.replace("→", " > ")
        .replace("•", "/")
        .replace("–", "-")
        .replace("—", "-")
        .replace("…", "...")
    )


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def centered(draw: ImageDraw.ImageDraw, text: str, y: int, size: int, fill=WHITE, stroke: int = 0) -> None:
    text = safe(text)
    f = font(size)
    box = draw.textbbox((0, 0), text, font=f, stroke_width=stroke)
    x = (WIDTH - (box[2] - box[0])) / 2
    draw.text((x, y), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0, 255))


def fit_size(draw: ImageDraw.ImageDraw, text: str, maximum: int, minimum: int, max_width: int) -> int:
    text = safe(text)
    for size in range(maximum, minimum - 1, -2):
        box = draw.textbbox((0, 0), text, font=font(size), stroke_width=3)
        if box[2] - box[0] <= max_width:
            return size
    return minimum


def gradient_background() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    for y in range(HEIGHT):
        ratio = y / max(1, HEIGHT - 1)
        color = tuple(round(BG_TOP[i] * (1 - ratio) + BG_BOTTOM[i] * ratio) for i in range(3))
        draw.line((0, y, WIDTH, y), fill=color)
    return image.convert("RGBA")


def make_chrome(beat: dict, path: Path) -> None:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    # Top and bottom readability veils.
    for y in range(0, 420):
        alpha = round(230 * (1 - y / 500))
        draw.line((0, y, WIDTH, y), fill=(2, 4, 9, max(0, alpha)))
    for y in range(1260, HEIGHT):
        alpha = round(220 * ((y - 1260) / (HEIGHT - 1260)))
        draw.line((0, y, WIDTH, y), fill=(2, 4, 9, alpha))

    draw.rounded_rectangle((52, 36, 360, 93), radius=16, fill=(0, 0, 0, 165), outline=(255, 255, 255, 55), width=2)
    draw.text((72, 49), "MONEY BLINDSPOT", font=font(28), fill=YELLOW)
    progress = int(beat["progress_index"])
    centered(draw, f"TRADE {progress} / 14" if progress else "START / 14", 44, 32, MUTED)

    dot_left, dot_right = 90, 990
    spacing = (dot_right - dot_left) / 14
    for index in range(15):
        x = round(dot_left + index * spacing)
        color = GREEN if index <= progress else (75, 85, 102, 220)
        radius = 10 if index == progress else 7
        draw.ellipse((x - radius, 112 - radius, x + radius, 112 + radius), fill=color)
        if index < 14:
            next_x = round(dot_left + (index + 1) * spacing)
            line_color = GREEN if index < progress else (75, 85, 102, 170)
            draw.line((x + 10, 112, next_x - 10, 112), fill=line_color, width=5)

    title = safe(beat["title"])
    title_size = fit_size(draw, title, 82, 48, 950)
    centered(draw, title, 155, title_size, WHITE, 4)
    subtitle = safe(beat["subtitle"])
    sub_size = fit_size(draw, subtitle, 42, 28, 930)
    centered(draw, subtitle, 260, sub_size, YELLOW, 3)

    label = safe(beat["visual"].get("label", "EDITORIAL GRAPHIC"))
    box = draw.textbbox((0, 0), label, font=font(28))
    width = box[2] - box[0]
    draw.rounded_rectangle((58, 1790, 94 + width, 1847), radius=12, fill=(0, 0, 0, 190), outline=(255, 255, 255, 45), width=2)
    draw.text((76, 1802), label, font=font(28), fill=WHITE)
    image.save(path)


def wrap_caption(draw: ImageDraw.ImageDraw, text: str, size: int, max_width: int) -> list[str]:
    words = safe(text).split()
    lines: list[str] = []
    current = ""
    f = font(size)
    for word in words:
        candidate = word if not current else f"{current} {word}"
        width = draw.textbbox((0, 0), candidate, font=f, stroke_width=4)[2]
        if width <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines[:2]


def make_caption(text: str, path: Path) -> None:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    size = 66
    lines = wrap_caption(draw, text, size, 900)
    if len(lines) > 2:
        size = 58
        lines = wrap_caption(draw, text, size, 900)
    f = font(size)
    line_height = size + 16
    total = len(lines) * line_height
    y = 1390 - total // 2
    widths = [draw.textbbox((0, 0), line, font=f, stroke_width=4)[2] for line in lines]
    box_width = min(980, max(widths, default=700) + 70)
    box_height = total + 48
    x0 = (WIDTH - box_width) // 2
    draw.rounded_rectangle((x0, y - 24, x0 + box_width, y - 24 + box_height), radius=28, fill=(0, 0, 0, 205), outline=(255, 225, 90, 180), width=3)
    for index, line in enumerate(lines):
        width = draw.textbbox((0, 0), line, font=f, stroke_width=4)[2]
        draw.text(((WIDTH - width) / 2, y + index * line_height), line, font=f, fill=WHITE, stroke_width=4, stroke_fill=(0, 0, 0, 255))
    image.save(path)


def paperclip_crop() -> Image.Image:
    source = Image.open(PROJECT / "checks-v1" / "source-scout" / "cbc-paperclip-25_5.jpg").convert("RGB")
    return source.crop((210, 120, 1070, 610))


def make_card(beat: dict, path: Path) -> None:
    image = gradient_background()
    draw = ImageDraw.Draw(image)
    theme = beat["visual"].get("theme", "generic")
    # Central luminous stage.
    draw.rounded_rectangle((90, 430, 990, 1330), radius=58, fill=(13, 20, 36, 245), outline=(255, 255, 255, 38), width=4)
    if theme == "door_fire":
        draw.rounded_rectangle((180, 610, 450, 1140), radius=22, fill=(88, 56, 36, 255), outline=WHITE, width=8)
        draw.ellipse((370, 855, 402, 887), fill=YELLOW)
        centered(draw, ">", 800, 120, YELLOW, 3)
        # Stylized camp stove/flame.
        draw.rounded_rectangle((650, 920, 870, 1080), radius=24, fill=(55, 65, 81, 255), outline=WHITE, width=7)
        draw.polygon([(760, 580), (690, 820), (760, 770), (720, 930), (840, 700), (780, 750)], fill=(249, 115, 22, 255))
    elif theme == "trip_truck":
        draw.polygon([(120, 930), (360, 610), (560, 930)], fill=(56, 189, 248, 210))
        draw.polygon([(400, 930), (650, 560), (960, 930)], fill=(125, 211, 252, 170))
        draw.rounded_rectangle((250, 980, 830, 1160), radius=24, fill=(40, 110, 190, 255), outline=WHITE, width=7)
        draw.rectangle((720, 900, 900, 1160), fill=(40, 110, 190, 255), outline=WHITE, width=7)
        draw.ellipse((360, 1110, 470, 1220), fill=(10, 15, 24, 255), outline=WHITE, width=6)
        draw.ellipse((740, 1110, 850, 1220), fill=(10, 15, 24, 255), outline=WHITE, width=6)
    elif theme == "rent_key":
        draw.polygon([(190, 800), (540, 520), (890, 800)], fill=(34, 197, 94, 220), outline=WHITE)
        draw.rectangle((260, 800, 820, 1160), fill=(22, 101, 52, 255), outline=WHITE, width=7)
        draw.rectangle((475, 930, 610, 1160), fill=(255, 255, 255, 210))
        draw.ellipse((630, 650, 800, 820), outline=YELLOW, width=28)
        draw.line((780, 780, 900, 900), fill=YELLOW, width=28)
    elif theme == "snow_globe":
        draw.ellipse((260, 520, 820, 1080), fill=(110, 190, 255, 75), outline=WHITE, width=10)
        for x, y in [(350, 680), (470, 600), (620, 710), (720, 620), (560, 840), (400, 900)]:
            draw.ellipse((x, y, x + 20, y + 20), fill=WHITE)
        centered(draw, "KISS", 740, 110, RED, 5)
        draw.rounded_rectangle((300, 1050, 780, 1190), radius=28, fill=(80, 50, 35, 255), outline=WHITE, width=8)
    elif theme == "movie_role":
        draw.rounded_rectangle((210, 680, 870, 1160), radius=32, fill=(245, 245, 245, 255), outline=WHITE, width=8)
        draw.rectangle((210, 600, 870, 750), fill=(20, 24, 34, 255), outline=WHITE, width=8)
        for x in range(210, 870, 130):
            draw.polygon([(x, 600), (x + 70, 600), (x + 130, 750), (x + 60, 750)], fill=(245, 245, 245, 255))
        centered(draw, "PAID ROLE", 860, 78, (15, 23, 42, 255))
    elif theme == "handshake":
        centered(draw, "TRADE 13", 610, 118, YELLOW, 5)
        centered(draw, "ONE SWAP LEFT", 1120, 66, GREEN, 4)
    elif theme == "locked_house":
        draw.polygon([(200, 900), (540, 590), (880, 900)], fill=(55, 65, 81, 255), outline=WHITE)
        draw.rectangle((270, 900, 810, 1190), fill=(30, 41, 59, 255), outline=WHITE, width=8)
        draw.rounded_rectangle((450, 900, 630, 1120), radius=24, fill=YELLOW, outline=(0, 0, 0, 255), width=7)
        draw.arc((475, 790, 605, 940), 180, 360, fill=YELLOW, width=24)
    elif theme == "full_trade_ladder":
        labels = ["CLIP", "PEN", "KNOB", "STOVE", "GEN", "PARTY", "SLED", "TRIP", "TRUCK", "RECORD", "RENT", "ALICE", "GLOBE", "MOVIE", "HOUSE"]
        for index, label in enumerate(labels):
            row, column = divmod(index, 3)
            x = 135 + column * 285
            y = 500 + row * 145
            color = RED if index == 0 else GREEN if index == 14 else (36, 55, 79, 255)
            draw.rounded_rectangle((x, y, x + 240, y + 94), radius=22, fill=color, outline=WHITE, width=3)
            label_font = font(34)
            width = draw.textbbox((0, 0), label, font=label_font)[2]
            draw.text((x + (240 - width) / 2, y + 27), label, font=label_font, fill=WHITE)
    elif theme == "loop_close":
        clip = paperclip_crop().resize((820, 467))
        image.paste(clip, (130, 500))
        draw.rounded_rectangle((125, 495, 955, 972), radius=30, outline=RED, width=9)
        draw.polygon([(220, 1170), (540, 940), (860, 1170)], fill=GREEN, outline=WHITE)
        draw.rectangle((300, 1170, 780, 1300), fill=(22, 101, 52, 255), outline=WHITE, width=7)
    else:
        centered(draw, safe(beat["title"]), 760, 94, CYAN, 5)
    image.save(path)


def caption_window(beat: dict) -> tuple[float, float] | None:
    caption = beat.get("caption")
    if not caption:
        return None
    start = max(float(beat["start"]), float(caption["caption_at"]))
    end = min(float(beat["end"]), float(caption["caption_end"]))
    if end <= start:
        return None
    return start - float(beat["start"]), end - float(beat["start"])


def append_overlays(filter_parts: list[str], base: str, chrome_index: int, caption_index: int | None, beat: dict) -> str:
    filter_parts.append(f"[{base}][{chrome_index}:v]overlay=0:0:shortest=1[vchrome]")
    window = caption_window(beat)
    if caption_index is not None and window:
        start, end = window
        filter_parts.append(
            f"[vchrome][{caption_index}:v]overlay=0:0:shortest=1:"
            f"enable='between(t,{start:.6f},{end:.6f})'[vout]"
        )
        return "vout"
    filter_parts.append("[vchrome]format=yuv420p[vout]")
    return "vout"


def render_beat(beat: dict, index: int) -> Path:
    duration = float(beat["duration"])
    expected_frames = round(duration * FPS)
    exact_duration = expected_frames / FPS
    if abs(exact_duration - duration) > 1e-6:
        raise RuntimeError(f"Beat is not frame integral: {beat['id']}")

    chrome = OVERLAY_DIR / f"{index:02d}-{beat['id']}-chrome.png"
    caption = OVERLAY_DIR / f"{index:02d}-{beat['id']}-caption.png"
    make_chrome(beat, chrome)
    has_caption = caption_window(beat) is not None
    if has_caption:
        make_caption(beat["caption"]["text"], caption)
    output = BEAT_DIR / f"{index:02d}-{beat['id']}.mp4"
    visual = beat["visual"]
    kind = visual["kind"]

    command = ["ffmpeg", "-y", "-v", "error"]
    filters: list[str] = []
    chrome_index = -1
    caption_index: int | None = None

    if kind == "hook_video":
        command += ["-ss", f"{visual.get('ss', 0.0):.6f}", "-i", str(ROOT / visual["path"])]
        filters.append(
            f"[0:v]trim=duration={duration:.6f},setpts=PTS-STARTPTS,"
            f"scale={WIDTH}:{HEIGHT}:flags=lanczos[base]"
        )
    elif kind == "source_framed":
        source = ROOT / visual["path"]
        ss = float(visual["ss"])
        preroll = min(5.0, ss)
        command += ["-ss", f"{ss - preroll:.6f}", "-i", str(source)]
        command += ["-loop", "1", "-framerate", str(FPS), "-i", str(chrome)]
        chrome_index = 1
        if has_caption:
            command += ["-loop", "1", "-framerate", str(FPS), "-i", str(caption)]
            caption_index = 2
        filters.append(
            f"[0:v]trim=start={preroll:.6f}:end={preroll + duration:.6f},"
            "setpts=PTS-STARTPTS,split=2[srcbg][srcfg]"
        )
        filters.append(
            f"[srcbg]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={WIDTH}:{HEIGHT},boxblur=20:2,eq=brightness=-0.38:saturation=0.85[bg]"
        )
        filters.append(
            "[srcfg]scale=1000:562:force_original_aspect_ratio=decrease:flags=lanczos,"
            "pad=1000:562:(ow-iw)/2:(oh-ih)/2:color=0x05070D[fg]"
        )
        filters.append("[bg][fg]overlay=40:600:shortest=1[base]")
    elif kind == "stock_full":
        command += ["-stream_loop", "-1", "-ss", f"{float(visual.get('ss', 0)):.6f}", "-i", str(ROOT / visual["path"])]
        command += ["-loop", "1", "-framerate", str(FPS), "-i", str(chrome)]
        chrome_index = 1
        if has_caption:
            command += ["-loop", "1", "-framerate", str(FPS), "-i", str(caption)]
            caption_index = 2
        filters.append(
            f"[0:v]trim=duration={duration:.6f},setpts=PTS-STARTPTS,"
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={WIDTH}:{HEIGHT},eq=contrast=1.08:saturation=1.08,"
            "vignette=PI/5[base]"
        )
    elif kind == "stock_chroma":
        card = CARD_DIR / f"{index:02d}-{beat['id']}-base.png"
        beat_copy = dict(beat)
        beat_copy["visual"] = {"theme": "handshake"}
        make_card(beat_copy, card)
        command += ["-stream_loop", "-1", "-ss", f"{float(visual.get('ss', 0)):.6f}", "-i", str(ROOT / visual["path"])]
        command += ["-loop", "1", "-framerate", str(FPS), "-i", str(card)]
        command += ["-loop", "1", "-framerate", str(FPS), "-i", str(chrome)]
        chrome_index = 2
        if has_caption:
            command += ["-loop", "1", "-framerate", str(FPS), "-i", str(caption)]
            caption_index = 3
        filters.append(f"[1:v]scale={WIDTH}:{HEIGHT}[cardbase]")
        filters.append(
            f"[0:v]trim=duration={duration:.6f},setpts=PTS-STARTPTS,"
            "fps=30,tpad=stop_mode=clone:stop_duration=0.1,"
            "scale=980:-2:flags=lanczos,chromakey=0x00FF00:0.24:0.09,format=rgba[hands]"
        )
        filters.append("[cardbase][hands]overlay=(W-w)/2:650:shortest=1[base]")
    elif kind == "graphic":
        card = CARD_DIR / f"{index:02d}-{beat['id']}-base.png"
        make_card(beat, card)
        command += ["-loop", "1", "-framerate", str(FPS), "-i", str(card)]
        command += ["-loop", "1", "-framerate", str(FPS), "-i", str(chrome)]
        chrome_index = 1
        if has_caption:
            command += ["-loop", "1", "-framerate", str(FPS), "-i", str(caption)]
            caption_index = 2
        filters.append(
            f"[0:v]scale={WIDTH}:{HEIGHT},"
            f"zoompan=z='min(zoom+0.00025,1.025)':x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':d={expected_frames}:s={WIDTH}x{HEIGHT}:fps={FPS}[base]"
        )
    else:
        raise ValueError(f"Unknown visual kind: {kind}")

    if kind == "hook_video":
        filters.append("[base]format=yuv420p[vout]")
        out_label = "vout"
    else:
        out_label = append_overlays(filters, "base", chrome_index, caption_index, beat)
    command += [
        "-filter_complex",
        ";".join(filters),
        "-map",
        f"[{out_label}]",
        "-an",
        "-frames:v",
        str(expected_frames),
        "-r",
        str(FPS),
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "17",
        "-pix_fmt",
        "yuv420p",
        "-g",
        str(expected_frames),
        "-keyint_min",
        str(expected_frames),
        "-sc_threshold",
        "0",
        str(output),
    ]
    run(command)
    return output


def build_soundtrack(video_only: Path) -> None:
    click_times = [9.0, 10.2, 11.2, 12.4, 14.7, 17.4, 19.7, 21.8, 24.0, 26.7, 29.8, 34.7, 40.2, 46.0]
    split_labels = "".join(f"[c{i}]" for i in range(len(click_times)))
    filters = [
        "[2:a]volume=0.025,lowpass=f=180,afade=t=in:st=0:d=1,afade=t=out:st=59:d=2[m1]",
        "[3:a]highpass=f=180,lowpass=f=1400,volume=0.004,afade=t=in:st=0:d=1,afade=t=out:st=59:d=2[m2]",
        "[m1][m2]amix=inputs=2:normalize=0[music]",
        f"[4:a]asplit={len(click_times)}{split_labels}",
    ]
    delayed: list[str] = []
    for index, click_time in enumerate(click_times):
        label = f"d{index}"
        filters.append(
            f"[c{index}]volume=0.10,afade=t=out:st=0.025:d=0.035,"
            f"adelay=delays={round(click_time * 1000)}:all=1[{label}]"
        )
        delayed.append(f"[{label}]")
    filters.append("".join(delayed) + f"amix=inputs={len(delayed)}:normalize=0[clicks]")
    filters.append("[5:a]volume=0.055,afade=t=out:st=0.30:d=0.45,adelay=delays=46000:all=1[boom]")
    filters.append(
        "[1:a][music][clicks][boom]amix=inputs=4:duration=longest:dropout_transition=0:normalize=0,"
        f"apad=whole_dur={DURATION},atrim=0:{DURATION},"
        "loudnorm=I=-15.8:TP=-1.8:LRA=8,aresample=48000[aout]"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(video_only),
            "-i",
            str(AUDIO),
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=55:duration={DURATION}:sample_rate=48000",
            "-f",
            "lavfi",
            "-i",
            f"anoisesrc=color=pink:duration={DURATION}:sample_rate=48000",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=1250:duration=0.06:sample_rate=48000",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=62:duration=0.75:sample_rate=48000",
            "-filter_complex",
            ";".join(filters),
            "-map",
            "0:v:0",
            "-map",
            "[aout]",
            "-t",
            str(DURATION),
            "-c:v",
            "copy",
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
            str(OUT),
        ]
    )


def main() -> None:
    edl = json.loads(EDL.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    if not evidence["override"]["allows_internal_render"]:
        raise RuntimeError("Hook Gate blocks internal render")
    if evidence["override"]["allows_publication"]:
        raise RuntimeError("Internal override cannot authorize publication")
    if abs(float(edl["duration"]) - DURATION) > 1e-6:
        raise RuntimeError("EDL duration mismatch")
    for directory in (WORK, BEAT_DIR, OVERLAY_DIR, CARD_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    outputs = [render_beat(beat, index) for index, beat in enumerate(edl["beats"])]
    concat = WORK / "concat.txt"
    concat.write_text("".join(f"file '{path.resolve()}'\n" for path in outputs), encoding="utf-8")
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat),
            "-c",
            "copy",
            str(VIDEO_ONLY),
        ]
    )
    build_soundtrack(VIDEO_ONLY)
    print(json.dumps({"output": str(OUT), "beats": len(outputs)}, indent=2))


if __name__ == "__main__":
    main()
