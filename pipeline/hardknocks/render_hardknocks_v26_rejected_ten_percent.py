#!/usr/bin/env python3
"""Render HardKnocks V26: The Rejected 10%."""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "hardknocks"
WORK = PROJECT / "clips" / "v26_rejected_ten_percent_work"
SOURCE = WORK / "source" / "dwd9i-z1HIY.mp4"
SEGMENT_DIR = WORK / "segments"
AUDIO_DIR = WORK / "audio" / "qwen-zack"
CHECKS = WORK / "checks"
BASE = WORK / "base_v1_rejected_ten_percent.mp4"
OVERLAY = WORK / "overlay_v1_rejected_ten_percent.mov"
SFX_TRACK = WORK / "sfx_v1.wav"
CAPTION_JSON = WORK / "captions_v1_word_timed.json"
CANDIDATE = WORK / "candidate_v1_rejected_ten_percent.mp4"
FINAL = PROJECT / "final" / "2026-08-01-hardknocks_v26_rejected_ten_percent.mp4"
TIMELINE_PATH = WORK / "timeline.json"

PEXELS_MOBILE = ROOT / "output" / "shared" / "pexels" / "mobile_gaming_6145416.mp4"
AWS_ANIMATION = WORK / "generated" / "aws_infrastructure_v1.mp4"
FONT_KOMIKA = ROOT / "assets" / "fonts" / "komika-axis" / "KOMIKAX_.ttf"
FONT_SANS = Path("/System/Library/Fonts/Helvetica.ttc")
SFX_DIR = ROOT / "assets" / "sfx" / "generated" / "hardknocks_v22"
WHISPER_PYTHON = ROOT / ".venv" / "bin" / "python"
CAPTION_BUILDER = ROOT / "pipeline" / "hardknocks" / "build_hardknocks_v26_captions.py"

WIDTH = 1080
HEIGHT = 1920
OW = 540
OH = 960
FPS = 30
TOTAL_DURATION = 62.20


@dataclass(frozen=True)
class Segment:
    name: str
    kind: str
    duration: float
    source_start: float | None = None
    visual: str | None = None
    voice: str | None = None
    visual_start: float = 0.0
    focus: float = 0.50


SEGMENTS = (
    Segment("01_rejected_hook", "source", 7.70, source_start=1200.160, focus=0.60),
    Segment(
        "02_casino_misdirect",
        "source_voice",
        3.00,
        source_start=1197.160,
        focus=0.53,
        voice="casino_misdirect.wav",
    ),
    Segment("03_host_casino_question", "source", 52 / FPS, source_start=1207.160, focus=0.58),
    Segment("04_provider_explanation", "source", 284 / FPS, source_start=1208.893, focus=0.60),
    Segment(
        "05_distribution_model",
        "narration",
        4.80,
        visual=str(PEXELS_MOBILE),
        voice="distribution_model.wav",
        visual_start=0.0,
    ),
    Segment("06_host_scale_question", "source", 110 / FPS, source_start=1218.360, focus=0.58),
    Segment("07_founder_valuation", "source", 88 / FPS, source_start=1222.027, focus=0.60),
    Segment(
        "08_valuation_math",
        "narration",
        5.40,
        visual=str(PEXELS_MOBILE),
        voice="valuation_math.wav",
        visual_start=4.80,
    ),
    Segment(
        "09_triple_cta",
        "source_voice",
        3.50,
        source_start=1224.960,
        focus=0.55,
        voice="triple_cta.wav",
    ),
    Segment(
        "10_valuation_guardrail",
        "source_voice",
        7.20,
        source_start=1232.000,
        focus=0.60,
        voice="valuation_guardrail.wav",
    ),
    Segment(
        "11_aws_independent_check",
        "narration",
        7.20,
        visual=str(AWS_ANIMATION),
        voice="aws_independent_check.wav",
        visual_start=0.0,
    ),
    Segment(
        "12_distribution_payoff",
        "source_voice",
        5.60,
        source_start=1200.160,
        focus=0.60,
        voice="distribution_payoff.wav",
    ),
)

if abs(sum(segment.duration for segment in SEGMENTS) - TOTAL_DURATION) > 1e-6:
    raise RuntimeError("V26 segment durations must sum to exactly 62.20 seconds")


@dataclass(frozen=True)
class Caption:
    start: float
    end: float
    text: str
    highlight: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--promote", action="store_true")
    return parser.parse_args()


def run(command: list[str | Path]) -> None:
    print("+", " ".join(str(item) for item in command), flush=True)
    subprocess.run([str(item) for item in command], cwd=ROOT, check=True)


def encoding(output: Path, duration: float) -> list[str | Path]:
    return [
        "-frames:v",
        str(round(duration * FPS)),
        "-c:v",
        "libx264",
        "-crf",
        "18",
        "-preset",
        "fast",
        "-pix_fmt",
        "yuv420p",
        "-r",
        str(FPS),
        "-fps_mode",
        "cfr",
        "-g",
        "60",
        "-sc_threshold",
        "0",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-ar",
        "48000",
        "-ac",
        "2",
        "-video_track_timescale",
        "90000",
        output,
    ]


def source_video_filter(segment: Segment, fine: float) -> str:
    # Keep scale dimensions constant inside each segment. The top crop removes the
    # source's own caption band, then a uniform scale refills the portrait canvas.
    x = f"trunc(min(max({segment.focus:.4f}*in_w-540,0),in_w-1080)/2)*2"
    return (
        f"trim=start={fine:.6f}:duration={segment.duration:.6f},setpts=PTS-STARTPTS,"
        "crop=3840:1900:0:0,scale=-2:1920:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:x='{x}':y=0,"
        "eq=contrast=1.05:saturation=1.03:brightness=-0.015,setsar=1,format=yuv420p,"
        f"fps={FPS},settb=1/{FPS},setpts=N,"
        f"tpad=stop_mode=clone:stop_duration=0.20,trim=duration={segment.duration:.6f}"
    )


def source_audio_filter(segment: Segment, fine: float) -> str:
    return (
        f"atrim=start={fine:.6f}:duration={segment.duration:.6f},asetpts=PTS-STARTPTS,"
        "highpass=f=70,acompressor=threshold=0.125:ratio=2.2:attack=5:release=80:makeup=1.30,"
        f"loudnorm=I=-16:TP=-1.5:LRA=10,afade=t=in:st=0:d=0.05,"
        f"afade=t=out:st={max(0.0, segment.duration - 0.12):.6f}:d=0.12,"
        f"aresample=48000:first_pts=0,apad,atrim=0:{segment.duration:.6f}"
    )


def voice_audio_filter(segment: Segment) -> str:
    return (
        "atrim=start=0,asetpts=PTS-STARTPTS,highpass=f=65,"
        "acompressor=threshold=0.12:ratio=2.5:attack=5:release=90:makeup=1,"
        "loudnorm=I=-16:TP=-1.5:LRA=8,aresample=48000:first_pts=0,apad,"
        f"atrim=0:{segment.duration:.6f},afade=t=in:st=0:d=0.04,"
        f"afade=t=out:st={max(0.0, segment.duration - 0.10):.6f}:d=0.10"
    )


def render_source(segment: Segment, output: Path) -> None:
    assert segment.source_start is not None
    coarse = max(0.0, segment.source_start - 5.0)
    fine = segment.source_start - coarse
    graph = (
        f"[0:v]{source_video_filter(segment, fine)}[v];"
        f"[0:a]{source_audio_filter(segment, fine)}[a]"
    )
    command: list[str | Path] = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-ss",
        f"{coarse:.6f}",
        "-i",
        SOURCE,
        "-filter_complex",
        graph,
        "-map",
        "[v]",
        "-map",
        "[a]",
    ]
    command.extend(encoding(output, segment.duration))
    run(command)


def render_source_voice(segment: Segment, output: Path) -> None:
    assert segment.source_start is not None and segment.voice is not None
    coarse = max(0.0, segment.source_start - 5.0)
    fine = segment.source_start - coarse
    graph = (
        f"[0:v]{source_video_filter(segment, fine)}[v];"
        f"[1:a]{voice_audio_filter(segment)}[a]"
    )
    command: list[str | Path] = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-ss",
        f"{coarse:.6f}",
        "-i",
        SOURCE,
        "-i",
        AUDIO_DIR / segment.voice,
        "-filter_complex",
        graph,
        "-map",
        "[v]",
        "-map",
        "[a]",
    ]
    command.extend(encoding(output, segment.duration))
    run(command)


def render_narration(segment: Segment, output: Path) -> None:
    assert segment.visual is not None and segment.voice is not None
    video = (
        f"trim=start={segment.visual_start:.6f}:duration={segment.duration:.6f},setpts=PTS-STARTPTS,"
        "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,"
        "crop=1080:1920:(in_w-out_w)/2:(in_h-out_h)/2,"
        "eq=contrast=1.05:saturation=0.88:brightness=-0.055,setsar=1,format=yuv420p,"
        f"fps={FPS},settb=1/{FPS},setpts=N,"
        f"tpad=stop_mode=clone:stop_duration=0.20,trim=duration={segment.duration:.6f}"
    )
    graph = f"[0:v]{video}[v];[1:a]{voice_audio_filter(segment)}[a]"
    command: list[str | Path] = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-i",
        segment.visual,
        "-i",
        AUDIO_DIR / segment.voice,
        "-filter_complex",
        graph,
        "-map",
        "[v]",
        "-map",
        "[a]",
    ]
    command.extend(encoding(output, segment.duration))
    run(command)


def build_aws_infrastructure_animation() -> None:
    """Build a semantic infrastructure illustration; never substitute warehouse footage."""
    AWS_ANIMATION.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{OW}x{OH}",
        "-r",
        str(FPS),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libx264",
        "-crf",
        "16",
        "-preset",
        "fast",
        "-pix_fmt",
        "yuv420p",
        "-r",
        str(FPS),
        "-frames:v",
        str(round(7.20 * FPS)),
        AWS_ANIMATION,
    ]
    process = subprocess.Popen([str(item) for item in command], cwd=ROOT, stdin=subprocess.PIPE)
    if process.stdin is None:
        raise RuntimeError("Could not open ffmpeg stdin for AWS animation")

    base = Image.new("RGB", (OW, OH), (5, 13, 26))
    base_draw = ImageDraw.Draw(base)
    for y in range(OH):
        blend = y / max(1, OH - 1)
        base_draw.line((0, y, OW, y), fill=(5, round(13 + 20 * blend), round(26 + 38 * blend)))

    rack_xs = (70, 220, 370)
    total_frames = round(7.20 * FPS)
    for frame_index in range(total_frames):
        t = frame_index / FPS
        image = base.copy()
        draw = ImageDraw.Draw(image, "RGBA")

        grid_shift = round((t * 18) % 48)
        for x in range(-48 + grid_shift, OW + 48, 48):
            draw.line((x, 380, x, OH), fill=(39, 89, 132, 32), width=1)
        for y in range(380 + grid_shift, OH + 48, 48):
            draw.line((0, y, OW, y), fill=(39, 89, 132, 28), width=1)
        draw.rectangle((0, 850, OW, OH), fill=(18, 46, 70, 235))
        for floor_x in range(-60 + grid_shift * 2, OW + 60, 60):
            draw.line((floor_x, 850, floor_x + 90, OH), fill=(67, 212, 255, 42), width=2)

        pulse = 0.5 + 0.5 * math.sin(t * math.tau * 0.8)
        cloud_box = (185, 392, 355, 484)
        draw.rounded_rectangle(cloud_box, radius=42, fill=(18, 53, 82, 235), outline=(67, 212, 255, 230), width=4)
        draw.ellipse((204, 370, 275, 443), fill=(18, 53, 82, 255), outline=(67, 212, 255, 230), width=4)
        draw.ellipse((257, 352, 340, 443), fill=(18, 53, 82, 255), outline=(67, 212, 255, 230), width=4)
        ring = round(10 + pulse * 10)
        draw.ellipse((270 - ring, 422 - ring, 270 + ring, 422 + ring), outline=(255, 174, 66, 210), width=3)

        for rack_index, x in enumerate(rack_xs):
            rack = (x, 568, x + 100, 850)
            activity = 0.5 + 0.5 * math.sin(t * math.tau * 1.1 + rack_index * 1.7)
            draw.rounded_rectangle(
                rack,
                radius=10,
                fill=(8, round(23 + 20 * activity), round(39 + 44 * activity), 245),
                outline=(116, 172, 210, 220),
                width=3,
            )
            draw.rectangle((x + 9, 584, x + 91, 606), fill=(24, 58, 83, 255))
            for bay in range(6):
                top = 622 + bay * 34
                draw.rounded_rectangle((x + 10, top, x + 90, top + 24), radius=4, fill=(15, 42, 63, 255), outline=(52, 105, 139, 220), width=1)
                phase = t * 3.0 + rack_index * 0.9 + bay * 0.55
                light = (93, 255, 172, 255) if math.sin(phase) > -0.25 else (255, 174, 66, 230)
                draw.ellipse((x + 72, top + 7, x + 80, top + 15), fill=light)
            draw.line((270, 484, x + 50, 568), fill=(67, 212, 255, 125), width=3)
            packet_progress = (t * 0.52 + rack_index * 0.27) % 1.0
            packet_x = round(270 + (x + 50 - 270) * packet_progress)
            packet_y = round(484 + (568 - 484) * packet_progress)
            draw.rounded_rectangle((packet_x - 8, packet_y - 5, packet_x + 8, packet_y + 5), radius=4, fill=(255, 174, 66, 245))

        scan_y = round(585 + ((t * 65) % 245))
        draw.rectangle((55, scan_y - 10, 485, scan_y + 10), fill=(67, 212, 255, 42))
        draw.line((55, scan_y, 485, scan_y), fill=(67, 212, 255, 155), width=3)
        process.stdin.write(image.tobytes())

    process.stdin.close()
    return_code = process.wait()
    if return_code != 0:
        raise subprocess.CalledProcessError(return_code, command)


def build_base() -> None:
    build_aws_infrastructure_animation()
    SEGMENT_DIR.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for index, segment in enumerate(SEGMENTS, start=1):
        output = SEGMENT_DIR / f"{index:02d}_{segment.name}.mp4"
        outputs.append(output)
        if segment.kind == "source":
            render_source(segment, output)
        elif segment.kind == "source_voice":
            render_source_voice(segment, output)
        elif segment.kind == "narration":
            render_narration(segment, output)
        else:
            raise ValueError(segment.kind)
    concat_file = SEGMENT_DIR / "concat.txt"
    concat_file.write_text("".join(f"file '{path.resolve()}'\n" for path in outputs), encoding="utf-8")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", BASE])


def build_captions() -> tuple[Caption, ...]:
    # Transcribe each hard-cut audio segment independently. Whole-timeline
    # Whisper can classify a noisy interview run as no-speech and replace an
    # otherwise intelligible 10-second answer with ellipses. Segment-local ASR
    # preserves the exact spoken words and keeps caption timing deterministic.
    parts_dir = CHECKS / "caption_parts"
    parts_dir.mkdir(parents=True, exist_ok=True)
    combined_bursts: list[dict[str, object]] = []
    transcript_parts: list[str] = []
    caption_corrections = {
        "BIGGEST COMPANY TODAY.": ("HOW BIG IS THE COMPANY?", "BIG"),
        "SAY YOU OWN A": ("SO YOU OWN A", "OWN"),
        "AND OWNERSHIP DELUDES": ("AND OWNERSHIP DILUTES", "DILUTES"),
        "THE BED INVESTORS MISSED": ("THE BET INVESTORS MISSED", "BET"),
    }
    cursor = 0.0
    for index, segment in enumerate(SEGMENTS, start=1):
        media = SEGMENT_DIR / f"{index:02d}_{segment.name}.mp4"
        part_json = parts_dir / f"{index:02d}_{segment.name}.json"
        run([WHISPER_PYTHON, CAPTION_BUILDER, media, part_json])
        part = json.loads(part_json.read_text(encoding="utf-8"))
        transcript_parts.append(str(part.get("text", "")).strip())
        for item in part["bursts"]:
            local_start = max(0.0, float(item["start"]))
            local_end = min(segment.duration, float(item["end"]))
            if local_start >= segment.duration or local_end <= local_start:
                continue
            text, highlight = caption_corrections.get(
                str(item["text"]),
                (str(item["text"]), str(item["highlight"])),
            )
            combined_bursts.append(
                {
                    "start": round(cursor + local_start, 3),
                    "end": round(cursor + local_end, 3),
                    "text": text,
                    "highlight": highlight,
                    "words": [],
                }
            )
        cursor += segment.duration
    merged_bursts: list[dict[str, object]] = []
    for burst in combined_bursts:
        text = str(burst["text"])
        if len(text.split()) == 1 and merged_bursts:
            previous = merged_bursts[-1]
            previous_text = str(previous["text"])
            close_enough = float(str(burst["start"])) - float(str(previous["end"])) <= 0.15
            if len(previous_text.split()) + 1 <= 5 and close_enough:
                previous["text"] = f"{previous_text} {text}"
                previous["end"] = burst["end"]
                previous["highlight"] = burst["highlight"]
                continue
        merged_bursts.append(burst)
    combined_bursts = merged_bursts
    payload = {
        "model": "mlx-community/whisper-small.en-mlx",
        "input": "segment-local exact base mix",
        "text": " ".join(part for part in transcript_parts if part),
        "bursts": combined_bursts,
    }
    CAPTION_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    captions = tuple(
        Caption(
            start=float(item["start"]),
            end=min(TOTAL_DURATION, float(item["end"])),
            text=str(item["text"]),
            highlight=str(item["highlight"]),
        )
        for item in payload["bursts"]
        if float(item["start"]) < TOTAL_DURATION
    )
    if not captions or captions[0].start > 0.20:
        raise RuntimeError("Caption word timing failed the t<=0.20 hook gate")
    return captions


def draw_centered_tokens(
    draw: ImageDraw.ImageDraw,
    y: int,
    text: str,
    highlight: str,
    font: ImageFont.FreeTypeFont,
    *,
    fill: tuple[int, int, int, int] = (255, 255, 255, 255),
    accent: tuple[int, int, int, int] = (67, 212, 255, 255),
) -> None:
    tokens = text.split(" ")
    clean_highlight = highlight.upper().strip("?!:,.'\"")

    def draw_line(line_tokens: list[str], line_y: int) -> None:
        line_font = font
        line_text = " ".join(line_tokens)
        measured = draw.textlength(line_text, font=line_font)
        if measured > 480:
            fitted_size = max(24, math.floor(line_font.size * 480 / measured))
            line_font = ImageFont.truetype(str(FONT_KOMIKA), fitted_size)
        space = max(5, round(draw.textlength(" ", font=line_font)))
        widths = [round(draw.textlength(token, font=line_font)) for token in line_tokens]
        total = sum(widths) + space * max(0, len(line_tokens) - 1)
        if total > 500:
            raise RuntimeError(f"Caption line exceeds safe width: {line_text!r} ({total}px)")
        x = (OW - total) // 2
        for token, width in zip(line_tokens, widths):
            clean_token = token.upper().strip("?!:,.'\"")
            color = accent if clean_highlight and clean_highlight in clean_token else fill
            draw.text(
                (x, line_y),
                token,
                font=line_font,
                fill=color,
                stroke_width=4,
                stroke_fill=(8, 10, 15, 245),
                anchor="la",
            )
            x += width + space

    if len(tokens) >= 4 and draw.textlength(text, font=font) > 480:
        split = math.ceil(len(tokens) / 2)
        draw_line(tokens[:split], y - 27)
        draw_line(tokens[split:], y + 25)
    else:
        draw_line(tokens, y)


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], *, alpha: int = 212) -> None:
    draw.rounded_rectangle(box, radius=18, fill=(10, 14, 22, alpha), outline=(67, 212, 255, 220), width=2)


def small_label(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, font: ImageFont.FreeTypeFont) -> None:
    width = round(draw.textlength(text, font=font)) + 18
    height = font.size + 14
    draw.rounded_rectangle((x, y, x + width, y + height), radius=9, fill=(10, 14, 22, 225))
    draw.text((x + 9, y + 7), text, font=font, fill=(240, 244, 249, 250))


def ease(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return 1 - (1 - value) ** 3


def draw_operator_nodes(
    draw: ImageDraw.ImageDraw,
    t: float,
    start: float,
    fonts: dict[str, ImageFont.FreeTypeFont],
    *,
    large: bool = False,
) -> None:
    cyan = (67, 212, 255, 255)
    amber = (255, 184, 77, 255)
    white = (248, 250, 252, 255)
    panel(draw, (36, 102, 504, 332), alpha=220)
    draw.text((270, 129), "ONE GAME  →  MANY OPERATORS", font=fonts["small_bold"], fill=white, anchor="ma")
    center = (270, 207)
    draw.rounded_rectangle((228, 175, 312, 239), radius=12, fill=(28, 47, 66, 255), outline=amber, width=3)
    draw.text(center, "GAME", font=fonts["tiny_bold"], fill=amber, anchor="mm")
    nodes = 10 if large else 8
    visible = min(nodes, 1 + int(max(0.0, t - start) / 0.30))
    for index in range(nodes):
        angle = 2 * math.pi * index / nodes
        radius_x = 176
        radius_y = 78
        x = round(center[0] + radius_x * math.cos(angle))
        y = round(center[1] + radius_y * math.sin(angle))
        if index < visible:
            draw.line((center[0], center[1], x, y), fill=(67, 212, 255, 130), width=2)
            draw.rounded_rectangle((x - 24, y - 15, x + 24, y + 15), radius=6, fill=(18, 63, 82, 240), outline=cyan, width=2)
            draw.text((x, y), "OP", font=fonts["tiny_bold"], fill=white, anchor="mm")
    draw.text((270, 316), "DISTRIBUTION, NOT A CASINO", font=fonts["small_bold"], fill=cyan, anchor="ms")


def draw_story_ui(draw: ImageDraw.ImageDraw, t: float, fonts: dict[str, ImageFont.FreeTypeFont]) -> None:
    cyan = (67, 212, 255, 255)
    white = (248, 250, 252, 255)
    amber = (255, 184, 77, 255)
    red = (255, 92, 92, 255)
    green = (95, 225, 153, 255)

    if 0.00 <= t < 1.20:
        panel(draw, (55, 90, 485, 206), alpha=225)
        draw.text((270, 122), "WOULD YOU BUY", font=fonts["evidence"], fill=white, anchor="ma")
        pulse = 1.0 + 0.035 * math.sin(t * 12)
        font = ImageFont.truetype(str(FONT_KOMIKA), round(43 * pulse))
        draw.text((270, 177), "10%?", font=font, fill=amber, stroke_width=3, stroke_fill=(8, 10, 15, 255), anchor="mm")
    elif 1.20 <= t < 2.64:
        panel(draw, (62, 106, 478, 220), alpha=220)
        draw.text((151, 151), "$100K", font=fonts["number"], fill=green, anchor="mm")
        progress = ease((t - 1.20) / 0.65)
        draw.line((217, 151, 217 + round(104 * progress), 151), fill=cyan, width=8)
        if progress > 0.72:
            draw.polygon(((326, 151), (307, 139), (307, 163)), fill=cyan)
        draw.text((392, 151), "10%", font=fonts["number"], fill=amber, anchor="mm")
        draw.text((270, 203), "COULD NOT RAISE", font=fonts["small_bold"], fill=red, anchor="ms")
    elif 2.64 <= t < 5.20:
        panel(draw, (80, 102, 460, 226), alpha=225)
        local = ease((t - 2.64) / 1.1)
        count = round(77 * local)
        draw.text((270, 151), f"{count}M", font=fonts["hero"], fill=cyan, anchor="mm")
        draw.text((270, 202), "MONTHLY PLAYERS", font=fonts["small_bold"], fill=white, anchor="ms")
        small_label(draw, 165, 230, "SPEAKER-REPORTED", fonts["tiny"])
    elif 5.20 <= t < 7.70:
        panel(draw, (45, 105, 495, 244), alpha=220)
        draw.text((150, 133), "THEN", font=fonts["small_bold"], fill=red, anchor="ma")
        draw.text((150, 182), "NO $100K", font=fonts["evidence"], fill=red, anchor="mm")
        draw.line((270, 126, 270, 218), fill=(120, 130, 145, 220), width=3)
        draw.text((390, 133), "NOW", font=fonts["small_bold"], fill=green, anchor="ma")
        draw.text((390, 182), "77M", font=fonts["evidence"], fill=green, anchor="mm")
        draw.text((270, 230), "WHAT CHANGED?", font=fonts["small_bold"], fill=amber, anchor="ms")

    if 7.70 <= t < 10.70:
        panel(draw, (125, 108, 415, 232), alpha=220)
        draw.text((270, 140), "ONLINE CASINO?", font=fonts["small_bold"], fill=white, anchor="ma")
        draw.line((215, 168, 325, 220), fill=red, width=12)
        draw.line((325, 168, 215, 220), fill=red, width=12)
        draw.text((270, 226), "NO.", font=fonts["evidence"], fill=red, anchor="ms")

    if 10.70 <= t < 12.433:
        panel(draw, (285, 110, 510, 205), alpha=215)
        draw.text((397, 145), "A CASINO?", font=fonts["small_bold"], fill=white, anchor="ma")
        draw.text((397, 186), "ASK THE MODEL", font=fonts["tiny_bold"], fill=amber, anchor="ma")

    if 12.433 <= t < 21.90:
        draw_operator_nodes(draw, t, 12.433, fonts)

    if 21.90 <= t < 26.70:
        draw_operator_nodes(draw, t, 21.90, fonts, large=True)
        small_label(draw, 18, 84, "PEXELS 6145416 • ILLUSTRATION", fonts["provenance"])

    if 26.70 <= t < 33.30:
        panel(draw, (70, 102, 470, 245), alpha=220)
        draw.text((270, 132), "COMPANY VALUE?", font=fonts["small_bold"], fill=white, anchor="ma")
        draw.text((270, 185), "$5 BILLION", font=fonts["hero"], fill=amber, anchor="mm")
        draw.text((270, 231), "SPEAKER-REPORTED • NOT AUDITED", font=fonts["tiny"], fill=white, anchor="ms")

    if 33.30 <= t < 38.70:
        panel(draw, (38, 96, 502, 337), alpha=230)
        draw.text((270, 124), "HEADLINE OWNERSHIP MATH", font=fonts["small_bold"], fill=white, anchor="ma")
        draw.text((104, 185), "$5B", font=fonts["number"], fill=amber, anchor="lm")
        draw.text((270, 185), "× 10%", font=fonts["number"], fill=cyan, anchor="mm")
        progress = ease((t - 33.30) / 2.0)
        draw.line((360, 185, 360 + round(58 * progress), 185), fill=cyan, width=8)
        if progress > 0.72:
            draw.polygon(((427, 185), (410, 174), (410, 196)), fill=cyan)
        if t >= 34.10:
            draw.text((270, 245), "$500M", font=fonts["hero"], fill=green, anchor="mm")
        draw.text((270, 290), "BEFORE DILUTION", font=fonts["evidence"], fill=red, anchor="mm")
        draw.text((270, 326), "SOURCE VALUATION • NOT AN AUDITED RETURN", font=fonts["tiny"], fill=white, anchor="ms")
        small_label(draw, 18, 84, "PEXELS 6145416 • ILLUSTRATION", fonts["provenance"])

    if 38.70 <= t < 42.20:
        panel(draw, (290, 88, 520, 132), alpha=220)
        draw.text((405, 110), "WOULD YOU INVEST?", font=fonts["small_bold"], fill=white, anchor="mm")
        active = 0 if t < 38.90 else 1 if t < 40.00 else 2 if t < 41.10 else 3
        labels = ("LIKE", "SUBSCRIBE", "COMMENT YES / NO")
        for index, label in enumerate(labels, start=1):
            y = 145 + (index - 1) * 58
            fill = (18, 63, 82, 235) if index <= active else (24, 29, 39, 215)
            outline = cyan if index <= active else (90, 98, 112, 200)
            draw.rounded_rectangle((304, y, 518, y + 44), radius=16, fill=fill, outline=outline, width=2)
            draw.text((411, y + 22), label, font=fonts["cta"], fill=white, anchor="mm")

    if 42.20 <= t < 49.40:
        panel(draw, (38, 96, 502, 344), alpha=230)
        draw.text((270, 124), "HEADLINE MATH ≠ RETURN", font=fonts["small_bold"], fill=red, anchor="ma")
        local = ease((t - 42.20) / 5.0)
        total_w = 388
        x0 = 76
        y0 = 170
        founder_w = round(total_w * (0.78 - 0.28 * local))
        investor_w = round(total_w * (0.10 + 0.12 * local))
        option_w = total_w - founder_w - investor_w
        draw.rounded_rectangle((x0, y0, x0 + founder_w, y0 + 55), radius=8, fill=cyan)
        draw.rectangle((x0 + founder_w, y0, x0 + founder_w + investor_w, y0 + 55), fill=amber)
        draw.rounded_rectangle((x0 + founder_w + investor_w, y0, x0 + total_w, y0 + 55), radius=8, fill=red)
        draw.text((270, 250), "VALUATION CHANGES", font=fonts["evidence"], fill=white, anchor="mm")
        draw.text((270, 290), "OWNERSHIP DILUTES", font=fonts["evidence"], fill=amber, anchor="mm")
        draw.text((270, 330), "NO VERIFIED INVESTOR RETURN CLAIM", font=fonts["tiny"], fill=white, anchor="ms")

    if 49.40 <= t < 56.60:
        panel(draw, (32, 90, 508, 360), alpha=235)
        draw.text((270, 118), "INDEPENDENT CHECK • AWS", font=fonts["small_bold"], fill=white, anchor="ma")
        rows = (("4,500+", "ONLINE CASINOS"), ("100+", "COUNTRIES"), ("35M+", "MONTHLY PLAYERS"))
        visible = min(3, 1 + int((t - 49.40) / 1.25))
        for index, (value, label) in enumerate(rows):
            y = 165 + index * 58
            color = green if index < visible else (82, 92, 108, 220)
            draw.text((76, y), value, font=fonts["number"], fill=color, anchor="lm")
            draw.text((246, y), label, font=fonts["row"], fill=white, anchor="lm")
        draw.text((270, 344), "AWS CASE STUDY • CHECKPOINT FIGURES", font=fonts["tiny"], fill=white, anchor="ms")
        small_label(draw, 18, 56, "LOCAL ANIMATION • ILLUSTRATION", fonts["provenance"])

    if 56.60 <= t <= TOTAL_DURATION:
        draw_operator_nodes(draw, t, 56.60, fonts, large=True)
        draw.text((270, 365), "THE MOAT WAS DISTRIBUTION", font=fonts["evidence"], fill=amber, stroke_width=2, stroke_fill=(8, 10, 15, 255), anchor="mm")
        if t >= 60.20:
            draw.text((270, 414), "ONE SUPPLIER → THOUSANDS", font=fonts["small_bold"], fill=white, anchor="mm")
            draw.text((270, 448), "OF STOREFRONTS", font=fonts["evidence"], fill=cyan, anchor="mm")
            draw.text((270, 486), "10% FOR $100K?", font=fonts["tiny_bold"], fill=amber, anchor="mm")


def build_overlay(captions: tuple[Caption, ...]) -> None:
    fonts = {
        "caption": ImageFont.truetype(str(FONT_KOMIKA), 39),
        "evidence": ImageFont.truetype(str(FONT_KOMIKA), 27),
        "number": ImageFont.truetype(str(FONT_KOMIKA), 31),
        "hero": ImageFont.truetype(str(FONT_KOMIKA), 45),
        "small_bold": ImageFont.truetype(str(FONT_SANS), 17),
        "cta": ImageFont.truetype(str(FONT_SANS), 20),
        "row": ImageFont.truetype(str(FONT_SANS), 19),
        "tiny_bold": ImageFont.truetype(str(FONT_SANS), 13),
        "tiny": ImageFont.truetype(str(FONT_SANS), 10),
        "provenance": ImageFont.truetype(str(FONT_SANS), 12),
        "watermark": ImageFont.truetype(str(FONT_SANS), 13),
    }
    command = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgba",
        "-s",
        f"{OW}x{OH}",
        "-r",
        str(FPS),
        "-i",
        "-",
        "-an",
        "-c:v",
        "qtrle",
        "-pix_fmt",
        "argb",
        OVERLAY,
    ]
    process = subprocess.Popen([str(item) for item in command], stdin=subprocess.PIPE, cwd=ROOT)
    assert process.stdin is not None
    total_frames = round(TOTAL_DURATION * FPS)
    for frame in range(total_frames):
        t = frame / FPS
        image = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image, "RGBA")
        draw_story_ui(draw, t, fonts)
        caption = next((item for item in captions if item.start <= t < item.end), None)
        if caption is not None:
            caption_y = 600 if 38.70 <= t < 42.20 else 575
            draw_centered_tokens(draw, caption_y, caption.text, caption.highlight, fonts["caption"])
        route = 0.5 - 0.5 * math.cos(2 * math.pi * min(1.0, t / TOTAL_DURATION) * 2.0)
        wx = 18 + round(route * 350)
        wy = 32 if t < TOTAL_DURATION / 2 else 58
        if 49.40 <= t < 56.60:
            wx = 390
            wy = 18
        draw.text(
            (wx, wy),
            "@MONEY BLINDSPOT",
            font=fonts["watermark"],
            fill=(255, 255, 255, 120),
            stroke_width=1,
            stroke_fill=(0, 0, 0, 125),
        )
        draw.rectangle((0, OH - 4, round(OW * t / TOTAL_DURATION), OH), fill=(255, 69, 0, 255))
        process.stdin.write(image.tobytes())
    process.stdin.close()
    code = process.wait()
    if code != 0:
        raise subprocess.CalledProcessError(code, command)


def build_sfx_track() -> None:
    assets = {
        "tick": SFX_DIR / "proof_tick.wav",
        "hit": SFX_DIR / "hook_origin_hit.wav",
        "whoosh": SFX_DIR / "jet_motion_whoosh.wav",
        "warm": SFX_DIR / "payoff_warm_hit.wav",
        "click": SFX_DIR / "cta_click.wav",
    }
    events = [
        (0.00, "hit", -19.0),
        (1.20, "tick", -20.0),
        (2.64, "tick", -18.0),
        (7.70, "whoosh", -25.0),
        (10.70, "hit", -25.0),
        (21.90, "whoosh", -24.0),
        (26.70, "tick", -21.0),
        (33.30, "warm", -23.0),
        (38.90, "click", -20.0),
        (40.00, "click", -20.0),
        (41.10, "click", -20.0),
        (42.20, "hit", -24.0),
        (49.40, "tick", -19.0),
        (56.60, "warm", -21.0),
    ]
    bed = SFX_DIR / "restrained_finance_bed.wav"
    command: list[str | Path] = ["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", bed]
    indexes: dict[str, int] = {}
    for name, path in assets.items():
        indexes[name] = len(indexes) + 1
        command.extend(["-i", path])
    filters = [f"[0:a]volume=-31dB,atrim=0:{TOTAL_DURATION:.6f}[bed]"]
    labels: list[str] = []
    for index, (at, name, gain) in enumerate(events):
        filters.append(f"[{indexes[name]}:a]volume={gain:.1f}dB[e{index}]")
        filters.append(f"anullsrc=r=48000:cl=stereo:d={at:.6f}[s{index}]")
        filters.append(f"[s{index}][e{index}]concat=n=2:v=0:a=1,apad,atrim=0:{TOTAL_DURATION:.6f}[p{index}]")
        labels.append(f"[p{index}]")
    filters.append(
        f"[bed]{''.join(labels)}amix=inputs={1 + len(labels)}:duration=longest:normalize=0,"
        f"alimiter=limit=0.82:level=false,atrim=0:{TOTAL_DURATION:.6f}[out]"
    )
    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[out]",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "pcm_s16le",
            SFX_TRACK,
        ]
    )
    run(command)


def finish_candidate() -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            BASE,
            "-i",
            OVERLAY,
            "-i",
            SFX_TRACK,
            "-filter_complex",
            "[1:v]scale=1080:1920:flags=lanczos,format=rgba[ov];"
            "[0:v][ov]overlay=x=0:y=0:format=auto:shortest=0:eof_action=repeat,setpts=PTS-STARTPTS[v];"
            "[0:a][2:a]amix=inputs=2:duration=first:normalize=0,"
            "volume=-0.7dB,alimiter=limit=0.84:level=false[a]",
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-frames:v",
            str(round(TOTAL_DURATION * FPS)),
            "-t",
            f"{TOTAL_DURATION:.6f}",
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-preset",
            "fast",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(FPS),
            "-fps_mode",
            "cfr",
            "-g",
            "60",
            "-sc_threshold",
            "0",
            "-video_track_timescale",
            "90000",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "2",
            CANDIDATE,
        ]
    )


def write_timeline(captions: tuple[Caption, ...]) -> None:
    cursor = 0.0
    payload: list[dict[str, object]] = []
    for segment in SEGMENTS:
        item = asdict(segment)
        item["output_start"] = round(cursor, 3)
        item["output_end"] = round(cursor + segment.duration, 3)
        payload.append(item)
        cursor += segment.duration
    TIMELINE_PATH.write_text(
        json.dumps(
            {
                "total_duration": TOTAL_DURATION,
                "segments": payload,
                "captions": [asdict(caption) for caption in captions],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def validate_inputs() -> None:
    required = [
        SOURCE,
        PEXELS_MOBILE,
        FONT_KOMIKA,
        FONT_SANS,
        WHISPER_PYTHON,
        CAPTION_BUILDER,
    ]
    required.extend(
        AUDIO_DIR / name
        for name in (
            "casino_misdirect.wav",
            "distribution_model.wav",
            "valuation_math.wav",
            "triple_cta.wav",
            "valuation_guardrail.wav",
            "aws_independent_check.wav",
            "distribution_payoff.wav",
        )
    )
    required.extend(
        SFX_DIR / name
        for name in (
            "restrained_finance_bed.wav",
            "proof_tick.wav",
            "hook_origin_hit.wav",
            "jet_motion_whoosh.wav",
            "payoff_warm_hit.wav",
            "cta_click.wav",
        )
    )
    missing = [path for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing inputs:\n" + "\n".join(str(path) for path in missing))


def main() -> None:
    args = parse_args()
    if not args.render and not args.promote:
        raise SystemExit("Choose --render or --promote")
    if args.render:
        validate_inputs()
        for directory in (WORK, SEGMENT_DIR, CHECKS):
            directory.mkdir(parents=True, exist_ok=True)
        build_base()
        captions = build_captions()
        build_overlay(captions)
        build_sfx_track()
        finish_candidate()
        write_timeline(captions)
        print(CANDIDATE)
    if args.promote:
        if not CANDIDATE.is_file():
            raise FileNotFoundError(CANDIDATE)
        FINAL.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(CANDIDATE, FINAL)
        print(FINAL)


if __name__ == "__main__":
    main()
