#!/usr/bin/env python3
"""Render HardKnocks V25: Searchable Story Moat."""

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
RESEARCH = PROJECT / "clips" / "v25_reference_F-QqW0Th-Lc_research"
SOURCE = RESEARCH / "source.mp4"
WORK = PROJECT / "clips" / "v25_searchable_story_work"
SEGMENT_DIR = WORK / "segments"
AUDIO_DIR = WORK / "audio" / "qwen-zack"
CHECKS = WORK / "checks"
BASE = WORK / "base_v1_searchable_story.mp4"
OVERLAY = WORK / "overlay_v1_searchable_story.mov"
SFX_TRACK = WORK / "sfx_v1.wav"
CANDIDATE = WORK / "candidate_v1_searchable_story.mp4"
HOOK_BASE = WORK / "hook_gate" / "rough_hook_base_v1.mp4"
HOOK_CANDIDATE = WORK / "hook_gate" / "rough_hook_v1_only_1000.mp4"
FINAL = PROJECT / "final" / "2026-08-01-hardknocks_v25_searchable_story_moat.mp4"
TIMELINE_PATH = WORK / "timeline.json"

PEXELS_TEAM = ROOT / "output" / "shared" / "pexels" / "team_meeting_7643614.mp4"
PEXELS_TYPING = ROOT / "output" / "shared" / "pexels" / "woman_typing_email_6608213.mp4"
PEXELS_LAPTOP = ROOT / "output" / "shared" / "pexels" / "home_laptop_5725850.mp4"
FONT_KOMIKA = ROOT / "assets" / "fonts" / "komika-axis" / "KOMIKAX_.ttf"
FONT_SANS = Path("/System/Library/Fonts/Helvetica.ttc")
SFX_DIR = ROOT / "assets" / "sfx" / "generated" / "hardknocks_v22"

WIDTH = 1080
HEIGHT = 1920
OW = 540
OH = 960
FPS = 30
TOTAL_DURATION = 64.0


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
    focus_end: float | None = None
    zoom: float = 1.18
    zoom_end: float | None = None
    turns: tuple[tuple[float, float, float], ...] = ()
    focus_points: tuple[tuple[float, float], ...] = ()
    visual_duration: float | None = None
    audio_duration: float | None = None
    voice_in: float = 0.0


SEGMENTS = (
    Segment("01_only_1000", "source", 1.04, source_start=1478.080, focus=0.32, focus_end=0.55, zoom=1.07),
    Segment(
        "02_only_hold", "source_silent", 1.16, source_start=1479.120, zoom=1.07,
        focus_points=((0.00, 0.52), (0.56, 0.30), (0.76, 0.225), (0.96, 0.18), (1.16, 0.20)),
    ),
    Segment("03_started_100k", "source", 1.20, source_start=1441.919, focus=0.57, focus_end=0.55, zoom=1.08),
    Segment("04_army_failed", "source", 3.20, source_start=1443.120, focus=0.55, focus_end=0.52, zoom=1.09),
    Segment("05_what_changed", "source_silent", 0.60, source_start=1446.320, focus=0.52, zoom=1.12),
    Segment("06_archive_context", "narration", 5.40, visual=str(PEXELS_TEAM), voice="archive_context.wav", visual_start=1.0),
    Segment(
        "07_authentic_capture", "source", 6.40, source_start=1421.640,
        turns=((0.00, 0.88, 1.12), (0.60, 0.56, 1.12), (3.24, 0.55, 1.12), (4.72, 0.54, 1.12)),
        audio_duration=6.14,
    ),
    Segment("08_retrieval_problem", "narration", 6.20, visual=str(PEXELS_TYPING), voice="retrieval_problem.wav", visual_start=1.0),
    Segment(
        "09_ai_search", "source", 8.30, source_start=1448.400,
        turns=((0.00, 1.00, 1.12), (1.47, 0.53, 1.12), (4.16, 0.56, 1.12), (6.10, 1.00, 1.12)),
    ),
    Segment("10_source_claim_reduction", "narration", 4.90, visual=str(PEXELS_LAPTOP), voice="source_claim_reduction.wav", visual_start=4.0),
    Segment("11_triple_cta", "narration", 3.40, visual=str(PEXELS_TEAM), voice="triple_cta.wav", visual_start=8.0),
    Segment(
        "12_editor_payoff", "source", 5.80, source_start=1461.500,
        turns=((0.00, 1.00, 1.12), (2.93, 0.52, 1.12)), audio_duration=4.60,
    ),
    Segment("13_bottleneck_migration", "narration", 8.30, visual=str(PEXELS_TEAM), voice="bottleneck_migration.wav", visual_start=0.0),
    Segment("14_moat_closure", "narration", 8.10, visual=str(PEXELS_LAPTOP), voice="moat_closure.wav", visual_start=10.0),
)

if abs(sum(segment.duration for segment in SEGMENTS) - TOTAL_DURATION) > 1e-6:
    raise RuntimeError("V25 segment durations must sum to exactly 64 seconds")


@dataclass(frozen=True)
class Caption:
    start: float
    end: float
    text: str
    highlight: str


CAPTIONS = (
    Caption(0.00, 1.04, "ONLY 1,000 HOURS?!", "1,000"),
    Caption(1.04, 2.20, "ONLY?!", "ONLY"),
    Caption(2.20, 3.40, "STARTED WITH 100,000", "100,000"),
    Caption(3.40, 4.75, "AN ARMY OF EDITORS", "ARMY"),
    Caption(4.75, 6.60, "STILL TOO MUCH", "TOO"),
    Caption(6.60, 7.20, "WHAT CHANGED?", "CHANGED"),
    Caption(7.20, 8.60, "THE FIRST BOTTLENECK", "BOTTLENECK"),
    Caption(8.60, 9.90, "WAS NOT CUTTING", "NOT"),
    Caption(9.90, 11.30, "FIND RIGHT MOMENTS", "RIGHT"),
    Caption(11.30, 12.60, "ACROSS 1,000 PEOPLE", "1,000"),
    Caption(12.60, 14.50, "CAMERAS ROLLING 24/7", "24/7"),
    Caption(14.50, 16.70, "NO WORDS PUT IN", "NO"),
    Caption(16.70, 19.00, "WE GET THE FOOTAGE", "FOOTAGE"),
    Caption(19.00, 20.35, "ALWAYS-ON CAPTURE", "CAPTURE"),
    Caption(20.40, 21.80, "CAME AT A COST", "COST"),
    Caption(21.80, 23.60, "100,000-HOUR HAYSTACK", "100,000-HOUR"),
    Caption(23.60, 25.20, "PROBLEM: RETRIEVAL", "RETRIEVAL"),
    Caption(25.20, 27.10, "TRANSCRIBE + SEARCH", "SEARCH"),
    Caption(27.10, 29.10, "SEARCH BY PERSON", "SEARCH"),
    Caption(29.10, 31.10, "SEARCH: EMOTIONAL", "EMOTIONAL"),
    Caption(31.10, 33.50, "SEARCH: EXCITED", "EXCITED"),
    Caption(33.50, 34.80, "MRBEAST SAYS", "SAYS"),
    Caption(34.80, 36.50, "100,000H TO 1,000H", "1,000H"),
    Caption(36.50, 38.40, "100x SMALLER SEARCH", "SEARCH"),
    Caption(38.40, 39.35, "TOOL OR REPLACEMENT?", "REPLACEMENT?"),
    Caption(39.35, 40.20, "LIKE + SUBSCRIBE", "SUBSCRIBE"),
    Caption(40.20, 41.20, "THEN COMMENT", "COMMENT"),
    Caption(41.20, 41.80, "YOUR TAKE", "TAKE"),
    Caption(41.80, 43.60, "A GREAT EDITOR", "GREAT"),
    Caption(43.60, 45.60, "CAN ACCOMPLISH MORE", "MORE"),
    Caption(45.60, 47.60, "MORE IN LESS TIME", "LESS"),
    Caption(47.60, 49.20, "NARROWER SEARCH", "NARROWER"),
    Caption(49.20, 51.00, "100,000H DOWN TO 1,000H", "1,000H"),
    Caption(51.00, 53.10, "NUMBERS DO NOT PROVE", "NOT"),
    Caption(53.10, 55.90, "NOT 100x PRODUCTIVITY", "NOT"),
    Caption(55.90, 57.80, "RETRIEVAL GOT CHEAPER", "CHEAPER"),
    Caption(57.80, 59.70, "THE BOTTLENECK MOVED", "MOVED"),
    Caption(59.70, 61.80, "TO HUMAN JUDGMENT", "HUMAN"),
    Caption(61.80, 64.00, "WHICH MOMENT WINS?", "WINS?"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hook", action="store_true")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--promote", action="store_true")
    return parser.parse_args()


def run(command: list[str | Path]) -> None:
    print("+", " ".join(str(item) for item in command), flush=True)
    subprocess.run([str(item) for item in command], cwd=ROOT, check=True)


def offsets() -> dict[str, float]:
    result: dict[str, float] = {}
    cursor = 0.0
    for segment in SEGMENTS:
        result[segment.name] = cursor
        cursor += segment.duration
    return result


def encoding(output: Path, duration: float) -> list[str | Path]:
    return [
        "-frames:v", str(round(duration * FPS)),
        "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-g", "60", "-sc_threshold", "0",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-video_track_timescale", "90000", output,
    ]


def step_expression(turns: tuple[tuple[float, float, float], ...], value_index: int) -> str:
    expression = f"{turns[-1][value_index]:.4f}"
    for index in range(len(turns) - 2, -1, -1):
        boundary = turns[index + 1][0]
        expression = f"if(lt(t,{boundary:.4f}),{turns[index][value_index]:.4f},{expression})"
    return expression


def piecewise_linear_expression(points: tuple[tuple[float, float], ...]) -> str:
    expression = f"{points[-1][1]:.4f}"
    for index in range(len(points) - 2, -1, -1):
        start_t, start_value = points[index]
        end_t, end_value = points[index + 1]
        delta_t = end_t - start_t
        linear = (
            f"{start_value:.4f}+({end_value - start_value:.4f})"
            f"*(t-{start_t:.4f})/{delta_t:.4f}"
        )
        expression = f"if(lt(t,{end_t:.4f}),{linear},{expression})"
    return expression


def portrait_crop(segment: Segment) -> str:
    if segment.turns:
        focus = step_expression(segment.turns, 1)
        zoom = step_expression(segment.turns, 2)
    else:
        focus_end = segment.focus if segment.focus_end is None else segment.focus_end
        zoom_end = segment.zoom if segment.zoom_end is None else segment.zoom_end
        focus = (
            piecewise_linear_expression(segment.focus_points)
            if segment.focus_points
            else f"{segment.focus:.4f}+({focus_end-segment.focus:.4f})*t/{segment.duration:.4f}"
        )
        zoom = f"{segment.zoom:.4f}+({zoom_end-segment.zoom:.4f})*t/{segment.duration:.4f}"
    return (
        f"scale=w=-2:h='round({HEIGHT}*({zoom})/2)*2':eval=frame:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:"
        f"'(in_w-out_w)*max(0.02,min(0.98,{focus}))':"
        f"'(in_h-out_h)/2',"
        "eq=contrast=1.05:saturation=1.04:brightness=-0.01,setsar=1,format=yuv420p"
    )


def source_audio(duration: float, speech_duration: float) -> str:
    return (
        "highpass=f=70,acompressor=threshold=0.125:ratio=2.2:attack=5:release=80:makeup=1.30,"
        f"loudnorm=I=-16:TP=-1.5:LRA=10,afade=t=in:st=0:d=0.05,"
        f"afade=t=out:st={max(0.0, speech_duration - 0.10):.6f}:d=0.10,"
        f"aresample=48000:first_pts=0,apad,atrim=0:{duration:.6f}"
    )


def render_source(segment: Segment, output: Path, *, silent: bool) -> None:
    assert segment.source_start is not None
    coarse = max(0.0, segment.source_start - 5.0)
    fine = segment.source_start - coarse
    visual_duration = segment.duration if segment.visual_duration is None else segment.visual_duration
    audio_duration = segment.duration if segment.audio_duration is None else segment.audio_duration
    video = (
        f"trim=start={fine:.6f}:end={fine + visual_duration:.6f},setpts=PTS-STARTPTS,"
        f"{portrait_crop(segment)},fps={FPS},"
        f"tpad=stop_mode=clone:stop_duration=0.20,trim=duration={segment.duration:.6f}"
    )
    command: list[str | Path] = ["ffmpeg", "-y", "-v", "error", "-ss", f"{coarse:.6f}", "-i", SOURCE]
    if silent:
        command.extend(["-f", "lavfi", "-t", f"{segment.duration:.6f}", "-i", "anullsrc=r=48000:cl=stereo"])
        graph = f"[0:v]{video}[v];[1:a]atrim=0:{segment.duration:.6f}[a]"
    else:
        audio = (
            f"atrim=start={fine:.6f}:end={fine + audio_duration:.6f},asetpts=PTS-STARTPTS,"
            f"{source_audio(segment.duration, audio_duration)}"
        )
        graph = f"[0:v]{video}[v];[0:a]{audio}[a]"
    command.extend(["-filter_complex", graph, "-map", "[v]", "-map", "[a]"])
    command.extend(encoding(output, segment.duration))
    run(command)


def render_narration(segment: Segment, output: Path) -> None:
    assert segment.visual is not None and segment.voice is not None
    video = (
        f"trim=start={segment.visual_start:.6f}:duration={segment.duration:.6f},setpts=PTS-STARTPTS,"
        "scale=1160:-2:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:'(in_w-out_w)*(0.150+(0.700)*t/{segment.duration:.3f})':'(in_h-out_h)/2',"
        "eq=contrast=1.06:saturation=0.92:brightness=-0.06,setsar=1,format=yuv420p,"
        f"fps={FPS},tpad=stop_mode=clone:stop_duration=0.20,trim=duration={segment.duration:.6f}"
    )
    audio = (
        f"atrim=start={segment.voice_in:.6f},asetpts=PTS-STARTPTS,"
        "highpass=f=70,acompressor=threshold=0.10:ratio=4:attack=5:release=100:makeup=1,"
        "loudnorm=I=-16:TP=-1.5:LRA=8,aresample=48000:first_pts=0,apad,"
        f"atrim=0:{segment.duration:.6f},afade=t=in:st=0:d=0.04,"
        f"afade=t=out:st={max(0.0, segment.duration - 0.10):.6f}:d=0.10"
    )
    command: list[str | Path] = [
        "ffmpeg", "-y", "-v", "error", "-i", segment.visual, "-i", AUDIO_DIR / segment.voice,
        "-filter_complex", f"[0:v]{video}[v];[1:a]{audio}[a]", "-map", "[v]", "-map", "[a]",
    ]
    command.extend(encoding(output, segment.duration))
    run(command)


def build_base() -> None:
    SEGMENT_DIR.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for index, segment in enumerate(SEGMENTS, start=1):
        output = SEGMENT_DIR / f"{index:02d}_{segment.name}.mp4"
        outputs.append(output)
        if segment.kind == "source":
            render_source(segment, output, silent=False)
        elif segment.kind == "source_silent":
            render_source(segment, output, silent=True)
        elif segment.kind == "narration":
            render_narration(segment, output)
        else:
            raise ValueError(segment.kind)
    concat_file = SEGMENT_DIR / "concat.txt"
    concat_file.write_text("".join(f"file '{path.resolve()}'\n" for path in outputs), encoding="utf-8")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", BASE])


def build_hook() -> None:
    hook_segments = SEGMENTS[:5]
    outputs: list[Path] = []
    for index, segment in enumerate(hook_segments, start=1):
        output = SEGMENT_DIR / f"{index:02d}_{segment.name}.mp4"
        outputs.append(output)
        render_source(segment, output, silent=segment.kind == "source_silent")
    HOOK_BASE.parent.mkdir(parents=True, exist_ok=True)
    concat_file = HOOK_BASE.parent / "concat.txt"
    concat_file.write_text("".join(f"file '{path.resolve()}'\n" for path in outputs), encoding="utf-8")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", HOOK_BASE])
    if not OVERLAY.is_file():
        build_overlay()
    if not SFX_TRACK.is_file():
        build_sfx_track()
    run([
        "ffmpeg", "-y", "-v", "error", "-i", HOOK_BASE, "-i", OVERLAY, "-i", SFX_TRACK,
        "-filter_complex",
        "[1:v]trim=0:7.2,setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,format=rgba[ov];"
        "[0:v][ov]overlay=x=0:y=0:format=auto:shortest=0:eof_action=repeat,setpts=PTS-STARTPTS[v];"
        "[2:a]atrim=0:7.2,asetpts=PTS-STARTPTS[sfx];"
        "[0:a][sfx]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.80:level=false[a]",
        "-map", "[v]", "-map", "[a]", "-frames:v", str(round(7.2 * FPS)),
        "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-g", "60", "-sc_threshold", "0", "-video_track_timescale", "90000",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", HOOK_CANDIDATE,
    ])


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
    measured = draw.textlength(text, font=font)
    if measured > 500:
        fitted_size = max(31, math.floor(font.size * 500 / measured))
        font = ImageFont.truetype(str(FONT_KOMIKA), fitted_size)
    space = max(5, round(draw.textlength(" ", font=font)))
    widths = [round(draw.textlength(token, font=font)) for token in tokens]
    total = sum(widths) + space * max(0, len(tokens) - 1)
    x = (OW - total) // 2
    for token, width in zip(tokens, widths):
        color = accent if highlight.upper().strip("?!:,\"") in token.upper().strip("?!:,\"") else fill
        draw.text(
            (x, y), token, font=font, fill=color,
            stroke_width=4, stroke_fill=(8, 10, 15, 245), anchor="la",
        )
        x += width + space


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], *, alpha: int = 205) -> None:
    draw.rounded_rectangle(box, radius=18, fill=(10, 14, 22, alpha), outline=(67, 212, 255, 210), width=2)


def small_label(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, font: ImageFont.FreeTypeFont) -> None:
    width = round(draw.textlength(text, font=font)) + 18
    height = font.size + 14
    draw.rounded_rectangle((x, y, x + width, y + height), radius=9, fill=(10, 14, 22, 225))
    draw.text((x + 9, y + 7), text, font=font, fill=(240, 244, 249, 250))


def progress_ease(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return 1 - (1 - value) ** 3


def draw_story_ui(draw: ImageDraw.ImageDraw, t: float, fonts: dict[str, ImageFont.FreeTypeFont]) -> None:
    cyan = (67, 212, 255, 255)
    white = (248, 250, 252, 255)
    amber = (255, 184, 77, 255)
    red = (255, 92, 92, 255)
    green = (95, 225, 153, 255)

    if 0 <= t < 7.20:
        small_label(draw, 275, 82, "BEAST GAMES • EDIT TEAM", fonts["provenance"])

    if 0 <= t < 1.04:
        panel(draw, (112, 120, 428, 202), alpha=205)
        draw.text((270, 138), "SEARCH POOL", font=fonts["small_bold"], fill=white, anchor="ma")
        draw.text((270, 167), "1,000 HOURS", font=fonts["evidence"], fill=cyan, anchor="ma")
    elif 1.04 <= t < 2.20:
        pulse = 1 + 0.04 * math.sin((t - 1.04) * 12)
        w = round(250 * pulse)
        panel(draw, ((OW - w) // 2, 132, (OW + w) // 2, 204), alpha=215)
        draw.text((270, 165), '"ONLY"?!', font=fonts["evidence"], fill=amber, anchor="mm")
    elif 2.20 <= t < 3.40:
        p = progress_ease((t - 2.20) / 1.20)
        panel(draw, (45, 118, 495, 205), alpha=205)
        draw.rounded_rectangle((67, 164, 67 + round(400 * p), 184), radius=9, fill=red)
        draw.text((270, 140), "RAW ARCHIVE  •  MRBEAST CLAIM", font=fonts["tiny"], fill=white, anchor="ma")
        draw.text((270, 193), "100,000 HOURS", font=fonts["small_bold"], fill=red, anchor="ma")
    elif 3.40 <= t < 6.60:
        panel(draw, (45, 112, 495, 232), alpha=205)
        visible = min(8, 1 + int((t - 3.40) / 0.35))
        for index in range(8):
            x = 83 + (index % 4) * 102
            y = 135 + (index // 4) * 42
            color = cyan if index < visible else (65, 72, 86, 200)
            draw.ellipse((x, y, x + 18, y + 18), fill=color)
            draw.rectangle((x - 4, y + 19, x + 22, y + 31), fill=color)
        draw.text((270, 219), "ARMY  ≠  ENOUGH", font=fonts["small_bold"], fill=red, anchor="ms")
    elif 6.60 <= t < 7.20:
        panel(draw, (112, 130, 428, 205), alpha=215)
        draw.text((270, 168), "WHAT CHANGED?", font=fonts["evidence"], fill=amber, anchor="mm")

    if 7.20 <= t < 12.60:
        local = t - 7.20
        panel(draw, (42, 110, 498, 286), alpha=205)
        draw.text((72, 146), "1,000", font=fonts["number"], fill=cyan)
        draw.text((220, 157), "CONTESTANTS", font=fonts["small_bold"], fill=white)
        draw.text((72, 205), "24/7", font=fonts["number"], fill=amber)
        draw.text((220, 216), "CAMERAS", font=fonts["small_bold"], fill=white)
        tiles = min(10, 1 + int(local / 0.45))
        for i in range(tiles):
            x = 73 + (i % 5) * 82
            y = 250 + (i // 5) * 18
            draw.rounded_rectangle((x, y, x + 65, y + 10), radius=4, fill=(67, 212, 255, 170))

    if 19.00 <= t < 25.20:
        local = t - 19.00
        panel(draw, (46, 105, 494, 300), alpha=205)
        draw.text((270, 136), "RAW FOOTAGE ARCHIVE", font=fonts["small_bold"], fill=white, anchor="ma")
        count = min(12, 2 + int(local * 1.8))
        for i in range(count):
            x = 77 + (i % 4) * 98
            y = 166 + (i // 4) * 35
            draw.rounded_rectangle((x, y, x + 80, y + 22), radius=5, fill=(38, 56, 78, 230), outline=cyan, width=1)
        draw.ellipse((390, 241, 434, 285), outline=amber, width=6)
        draw.line((426, 278, 454, 303), fill=amber, width=7)
        draw.text((270, 290), "100,000H  •  UNINDEXED", font=fonts["tiny"], fill=red, anchor="ms")

    if 25.20 <= t < 33.50:
        local = t - 25.20
        panel(draw, (38, 106, 502, 336), alpha=215)
        draw.text((62, 131), "TRANSCRIPT INDEX", font=fonts["small_bold"], fill=white)
        query = "SEARCH: EMOTIONAL" if local >= 3.6 else "SEARCH: PERSON"
        draw.rounded_rectangle((62, 168, 478, 213), radius=12, fill=(235, 239, 245, 240))
        draw.text((82, 180), query, font=fonts["small_bold"], fill=(15, 20, 29, 255))
        results = max(1, min(4, int((local - 1.1) / 1.0) + 1))
        for i in range(results):
            y = 230 + i * 25
            draw.rounded_rectangle((72, y, 450 - i * 12, y + 16), radius=5, fill=(67, 212, 255, 185))
        draw.text((270, 326), "ILLUSTRATIVE SEARCH UI", font=fonts["tiny"], fill=(225, 231, 238, 220), anchor="ms")

    if 33.50 <= t < 38.40:
        local = t - 33.50
        panel(draw, (40, 100, 500, 342), alpha=225)
        draw.text((270, 128), "MRBEAST-REPORTED REVIEW POOL", font=fonts["tiny"], fill=white, anchor="ma")
        draw.text((112, 190), "100,000H", font=fonts["number"], fill=red, anchor="lm")
        arrow_p = progress_ease(local / 2.0)
        draw.line((205, 190, 205 + round(125 * arrow_p), 190), fill=cyan, width=10)
        if arrow_p > 0.7:
            draw.polygon(((330, 190), (307, 176), (307, 204)), fill=cyan)
        draw.text((428, 190), "1,000H", font=fonts["number"], fill=green, anchor="rm")
        draw.text((270, 248), "100x SMALLER SEARCH SPACE", font=fonts["small_bold"], fill=cyan, anchor="mm")
        draw.text((270, 285), "NOT 100x PRODUCTIVITY", font=fonts["small_bold"], fill=amber, anchor="mm")
        draw.text((270, 325), "SOURCE CLAIM • NOT INDEPENDENTLY AUDITED", font=fonts["tiny"], fill=white, anchor="ms")

    if 38.40 <= t < 41.80:
        draw.rounded_rectangle((292, 98, 516, 132), radius=12, fill=(10, 14, 22, 220), outline=amber, width=2)
        draw.text((404, 115), "TOOL  OR  REPLACEMENT?", font=fonts["small_bold"], fill=white, anchor="mm")
        active = 0 if t < 39.25 else 1 if t < 40.10 else 2 if t < 40.95 else 3
        labels = (("LIKE", 39.25), ("SUBSCRIBE", 40.10), ("COMMENT", 40.95))
        for index, (label, _) in enumerate(labels, start=1):
            y = 140 + (index - 1) * 58
            fill = (18, 63, 82, 230) if index <= active else (24, 29, 39, 210)
            outline = cyan if index <= active else (90, 98, 112, 200)
            draw.rounded_rectangle((320, y, 505, y + 44), radius=16, fill=fill, outline=outline, width=2)
            draw.text((412, y + 22), label, font=fonts["small_bold"], fill=white, anchor="mm")

    if 47.60 <= t < 55.90:
        local = t - 47.60
        panel(draw, (40, 102, 500, 330), alpha=220)
        draw.text((270, 130), "BOTTLENECK MIGRATION", font=fonts["small_bold"], fill=white, anchor="ma")
        retrieval = max(30, round(190 * (1 - 0.75 * progress_ease(local / 3.0))))
        judgment = min(190, round(55 + 135 * progress_ease(local / 5.0)))
        draw.text((68, 184), "RETRIEVAL", font=fonts["tiny"], fill=white)
        draw.rounded_rectangle((165, 178, 165 + retrieval, 202), radius=7, fill=green)
        draw.text((68, 238), "JUDGMENT", font=fonts["tiny"], fill=white)
        draw.rounded_rectangle((165, 232, 165 + judgment, 256), radius=7, fill=amber)
        draw.text((270, 302), "SEARCH CHEAPER  →  JUDGMENT SCARCER", font=fonts["small_bold"], fill=cyan, anchor="ms")

    if 55.90 <= t <= 64.00:
        panel(draw, (35, 96, 505, 340), alpha=225)
        draw.text((270, 125), "THE SCARCE SKILL MOVED", font=fonts["small_bold"], fill=white, anchor="ma")
        local = t - 55.90
        retrieval = max(35, round(200 * (1 - 0.80 * progress_ease(local / 2.4))))
        judgment = min(220, round(45 + 175 * progress_ease(local / 4.0)))
        draw.text((64, 180), "RETRIEVAL", font=fonts["tiny"], fill=white)
        draw.rounded_rectangle((165, 173, 165 + retrieval, 199), radius=8, fill=green)
        draw.text((64, 234), "JUDGMENT", font=fonts["tiny"], fill=white)
        draw.rounded_rectangle((165, 227, 165 + judgment, 253), radius=8, fill=amber)
        draw.text((270, 292), "REAL MOMENT  →  STORY", font=fonts["small_bold"], fill=cyan, anchor="mm")
        draw.text((270, 326), "HUMAN VERDICT", font=fonts["evidence"], fill=amber, anchor="ms")


def build_overlay() -> None:
    fonts = {
        "caption": ImageFont.truetype(str(FONT_KOMIKA), 39),
        "evidence": ImageFont.truetype(str(FONT_KOMIKA), 27),
        "number": ImageFont.truetype(str(FONT_KOMIKA), 30),
        "small_bold": ImageFont.truetype(str(FONT_SANS), 17),
        "tiny": ImageFont.truetype(str(FONT_SANS), 10),
        "provenance": ImageFont.truetype(str(FONT_SANS), 18),
        "watermark": ImageFont.truetype(str(FONT_SANS), 13),
    }
    command = [
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
        "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "qtrle", "-pix_fmt", "argb", OVERLAY,
    ]
    process = subprocess.Popen([str(item) for item in command], stdin=subprocess.PIPE, cwd=ROOT)
    assert process.stdin is not None
    total_frames = round(TOTAL_DURATION * FPS)
    pexels_ranges = (
        (7.20, 12.60, "PEXELS 7643614 • ILLUSTRATION"),
        (19.00, 25.20, "PEXELS 6608213 • ILLUSTRATION"),
        (33.50, 38.40, "PEXELS 5725850 • ILLUSTRATION"),
        (38.40, 41.80, "HK CTA • PEXELS 7643614"),
        (47.60, 55.90, "HK COMMENTARY • PEXELS 7643614"),
        (55.90, 64.00, "HK INFERENCE • PEXELS 5725850"),
    )
    for frame in range(total_frames):
        t = frame / FPS
        image = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image, "RGBA")
        draw_story_ui(draw, t, fonts)
        for start, end, label in pexels_ranges:
            if start <= t < end:
                small_label(draw, 18, 84, label, fonts["provenance"])
                break
        if 41.80 <= t < 47.60:
            small_label(draw, 18, 84, "MRBEAST OPINION", fonts["provenance"])
        caption = next((item for item in CAPTIONS if item.start <= t < item.end), None)
        if caption is not None:
            caption_y = 590 if 38.40 <= t < 41.80 else 575
            draw_centered_tokens(draw, caption_y, caption.text, caption.highlight, fonts["caption"])
        route = 0.5 - 0.5 * math.cos(2 * math.pi * min(1.0, t / TOTAL_DURATION) * 2.0)
        wx = 18 + round(route * 350)
        draw.text((wx, 38), "@MONEY BLINDSPOT", font=fonts["watermark"], fill=(255, 255, 255, 115), stroke_width=1, stroke_fill=(0, 0, 0, 120))
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
        (1.04, "whoosh", -24.0),
        (2.20, "tick", -18.0),
        (3.40, "whoosh", -25.0),
        (6.60, "hit", -25.0),
        (25.20, "tick", -21.0),
        (29.50, "tick", -19.0),
        (33.50, "whoosh", -25.0),
        (39.25, "click", -19.0),
        (40.10, "click", -19.0),
        (40.95, "click", -19.0),
        (46.90, "warm", -24.0),
        (47.60, "tick", -21.0),
        (55.90, "warm", -22.0),
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
    command.extend([
        "-filter_complex", ";".join(filters), "-map", "[out]",
        "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", SFX_TRACK,
    ])
    run(command)


def finish_candidate() -> None:
    run([
        "ffmpeg", "-y", "-v", "error", "-i", BASE, "-i", OVERLAY, "-i", SFX_TRACK,
        "-filter_complex",
        "[1:v]scale=1080:1920:flags=lanczos,format=rgba[ov];"
        "[0:v][ov]overlay=x=0:y=0:format=auto:shortest=0:eof_action=repeat,setpts=PTS-STARTPTS[v];"
        "[0:a][2:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.80:level=false[a]",
        "-map", "[v]", "-map", "[a]", "-frames:v", str(round(TOTAL_DURATION * FPS)),
        "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-g", "60", "-sc_threshold", "0", "-video_track_timescale", "90000",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", CANDIDATE,
    ])


def write_timeline() -> None:
    cursor = 0.0
    payload: list[dict[str, object]] = []
    for segment in SEGMENTS:
        item = asdict(segment)
        item["output_start"] = round(cursor, 3)
        item["output_end"] = round(cursor + segment.duration, 3)
        payload.append(item)
        cursor += segment.duration
    TIMELINE_PATH.write_text(json.dumps({
        "total_duration": TOTAL_DURATION,
        "segments": payload,
        "captions": [asdict(caption) for caption in CAPTIONS],
    }, indent=2) + "\n", encoding="utf-8")


def validate_inputs() -> None:
    required = [SOURCE, PEXELS_TEAM, PEXELS_TYPING, PEXELS_LAPTOP, FONT_KOMIKA, FONT_SANS]
    required.extend(AUDIO_DIR / name for name in (
        "archive_context.wav", "retrieval_problem.wav", "source_claim_reduction.wav",
        "triple_cta.wav", "bottleneck_migration.wav", "moat_closure.wav",
    ))
    required.extend(SFX_DIR / name for name in (
        "restrained_finance_bed.wav", "proof_tick.wav", "hook_origin_hit.wav",
        "jet_motion_whoosh.wav", "payoff_warm_hit.wav", "cta_click.wav",
    ))
    missing = [path for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing inputs:\n" + "\n".join(str(path) for path in missing))


def main() -> None:
    args = parse_args()
    if not args.hook and not args.render and not args.promote:
        raise SystemExit("Choose --hook, --render or --promote")
    if args.hook:
        for directory in (WORK, SEGMENT_DIR, CHECKS):
            directory.mkdir(parents=True, exist_ok=True)
        required = [SOURCE, FONT_KOMIKA, FONT_SANS]
        required.extend(SFX_DIR / name for name in (
            "restrained_finance_bed.wav", "proof_tick.wav", "hook_origin_hit.wav",
            "jet_motion_whoosh.wav", "payoff_warm_hit.wav", "cta_click.wav",
        ))
        missing = [path for path in required if not path.is_file()]
        if missing:
            raise FileNotFoundError("Missing hook inputs:\n" + "\n".join(str(path) for path in missing))
        build_hook()
        print(HOOK_CANDIDATE)
    if args.render:
        validate_inputs()
        for directory in (WORK, SEGMENT_DIR, CHECKS):
            directory.mkdir(parents=True, exist_ok=True)
        build_base()
        build_overlay()
        build_sfx_track()
        finish_candidate()
        write_timeline()
        print(CANDIDATE)
    if args.promote:
        if not CANDIDATE.is_file():
            raise FileNotFoundError(CANDIDATE)
        FINAL.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(CANDIDATE, FINAL)
        print(FINAL)


if __name__ == "__main__":
    main()
