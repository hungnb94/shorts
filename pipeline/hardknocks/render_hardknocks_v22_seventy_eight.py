#!/usr/bin/env python3
"""Render HardKnocks V22: The $78 Tail Number.

Backward-planned causal story: $78 origin -> tail-number promise -> boring
sleep-testing business -> service/team mechanism -> jet-as-reward payoff.
This one-off renderer consumes only the exact source EDL, two labeled Pexels
illustrations, canonical Qwen narration, and manifest-bound generated SFX.
Completion is based on the encoded MP4 and media QC, not renderer unit tests.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "hardknocks"
SOURCE = PROJECT / "source" / "4fOaAGCuuJU.webm"
SOURCE_DURATION = 1358.668
WORK = PROJECT / "clips" / "v22_seventy_eight_work"
SEGMENT_DIR = WORK / "segments"
PANELS = WORK / "panels"
CHECKS = WORK / "checks"
AUDIO_DIR = WORK / "audio"
HOOK_DIR = WORK / "hook_gate"
FINAL = PROJECT / "final" / "2026-07-30-hardknocks_v22_seventy_eight_tail.mp4"
ROUGH_HOOK = HOOK_DIR / "rough_hook_v5.mp4"

PEXELS_SLEEP = ROOT / "output" / "shared" / "pexels" / "sleepy_man_7131825.mp4"
PEXELS_TEAM = ROOT / "output" / "shared" / "pexels" / "team_meeting_7643614.mp4"

HOOK_QUESTION = AUDIO_DIR / "hook_question.wav"
RECEIPT_BRIDGE = AUDIO_DIR / "receipt_bridge.wav"
SLEEP_BRIDGE = AUDIO_DIR / "sleep_bridge.wav"
CTA_AUDIO = AUDIO_DIR / "cta.wav"
PAYOFF_AUDIO = AUDIO_DIR / "payoff.wav"

SFX_DIR = ROOT / "assets" / "sfx" / "generated" / "hardknocks_v22"
HOOK_HIT = SFX_DIR / "hook_origin_hit.wav"
JET_WHOOSH = SFX_DIR / "jet_motion_whoosh.wav"
PROOF_TICK = SFX_DIR / "proof_tick.wav"
CTA_CLICK = SFX_DIR / "cta_click.wav"
PAYOFF_HIT = SFX_DIR / "payoff_warm_hit.wav"
MUSIC_BED = SFX_DIR / "restrained_finance_bed.wav"
SFX_MANIFEST = ROOT / "assets" / "sfx" / "manifest.json"

FONT_KOMIKA = ROOT / "assets" / "fonts" / "komika-axis" / "KOMIKAX_.ttf"
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
FONT_BLACK = Path("/System/Library/Fonts/Supplemental/Arial Black.ttf")

WIDTH = 1080
HEIGHT = 1920
FPS = 30
CAPTION_BAND_PX = 270
SEGMENT_FADE_IN = 0.10
SEGMENT_FADE_OUT = 0.18

YELLOW = "#FFD23C"
GREEN = "#00D66E"
RED = "#FF4D4D"
BLUE = "#4FC3F7"
DARK = "#0B0E14"
GRAY = "#A8B0BF"


@dataclass(frozen=True)
class Segment:
    name: str
    kind: str
    start: float
    end: float
    turns: tuple[tuple[float, float], ...]
    zoom: float
    act: str
    audio: Path | None = None
    visual: Path | None = None
    fade_out: float = SEGMENT_FADE_OUT

    @property
    def duration(self) -> float:
        return self.end - self.start

    @property
    def uses_source(self) -> bool:
        return self.kind in {"source", "narration_source", "silent_source"}


SEGMENTS = (
    Segment(
        "origin_78", "source", 32.32, 34.40,
        ((0.00, 0.42), (0.82, 0.39), (1.56, 0.42)),
        1.08, "origin",
    ),
    Segment(
        "hook_question", "narration_source", 190.00, 193.80,
        ((0.00, 0.50), (0.90, 0.34), (2.10, 0.50), (3.05, 0.34)),
        1.05, "object_mystery", HOOK_QUESTION,
    ),
    Segment(
        "tail_promise", "source", 193.519, 200.20,
        ((0.00, 0.34), (1.35, 0.31), (2.75, 0.34), (4.20, 0.32)),
        1.07, "promise",
    ),
    Segment(
        "receipt_bridge", "narration_source", 200.00, 203.40,
        ((0.00, 0.50), (1.00, 0.34), (2.05, 0.50)),
        1.05, "pivot", RECEIPT_BRIDGE,
    ),
    Segment(
        "company_identity", "source", 280.32, 285.36,
        ((0.00, 0.34), (1.50, 0.31), (3.10, 0.34), (4.70, 0.32)),
        1.07, "business_identity",
    ),
    Segment(
        "kitchen_origin", "source", 287.199, 289.92,
        ((0.00, 0.34), (1.18, 0.31)),
        1.08, "kitchen_origin",
    ),
    Segment(
        "sleep_reveal", "narration_pexels", 2.20, 7.10,
        (), 1.00, "contrarian_reveal", SLEEP_BRIDGE, PEXELS_SLEEP,
    ),
    Segment(
        "patient_scale", "source", 290.32, 298.50,
        ((0.00, 0.34), (2.00, 0.31), (4.10, 0.34), (6.20, 0.32)),
        1.07, "scale_receipt",
    ),
    Segment(
        "scale_hold", "silent_source", 298.50, 299.99,
        ((0.00, 0.34), (0.76, 0.31)), 1.10, "proof_hold",
    ),
    Segment(
        "story_cta", "narration_pexels", 4.20, 9.20,
        (), 1.00, "cta", CTA_AUDIO, PEXELS_TEAM,
    ),
    Segment(
        "service_moat", "source", 493.60, 507.28,
        ((0.00, 0.34), (2.80, 0.31), (5.80, 0.34), (8.80, 0.32)),
        1.07, "service_moat", fade_out=0.08,
    ),
    Segment(
        "team_scale", "source", 550.399, 557.12,
        ((0.00, 0.34), (2.10, 0.31), (4.30, 0.34), (6.30, 0.32)),
        1.07, "team_scale", fade_out=0.08,
    ),
    Segment(
        "payoff", "narration_source", 201.00, 206.20,
        ((0.00, 0.50), (1.30, 0.34), (2.70, 0.50), (4.05, 0.34)),
        1.05, "payoff", PAYOFF_AUDIO,
    ),
)


CAPTIONS: dict[str, tuple[tuple[float, float, str, str], ...]] = {
    "origin_78": (
        (0.00, 0.98, "JAN 2015: $78", "$78"),
        (0.98, 2.08, "TO MY NAME", "MY"),
    ),
    "hook_question": (
        (0.00, 1.12, "SO WHY PUT", "WHY"),
        (1.12, 2.18, "SEVENTY-EIGHT", "SEVENTY-EIGHT"),
        (2.18, 3.80, "ON A $5M JET?", "$5M"),
    ),
    "tail_promise": (
        (0.00, 1.28, "ONE DAY", "ONE DAY"),
        (1.28, 4.00, "GET MY OWN PLANE", "PLANE"),
        (4.00, 5.05, "PUT 78", "78"),
        (5.05, 6.681, "ON THE TAIL NUMBER", "TAIL"),
    ),
    "receipt_bridge": (
        (0.00, 0.72, "HE DID", "DID"),
        (0.72, 1.84, "BUT THE PLANE", "PLANE"),
        (1.84, 3.40, "WAS ONLY THE RECEIPT", "RECEIPT"),
    ),
    "company_identity": (
        (0.00, 1.50, "I OWN BLACKSTONE", "BLACKSTONE"),
        (1.50, 2.45, "MEDICAL SERVICES", "MEDICAL"),
        (2.45, 3.68, "HOME SLEEP TESTING", "SLEEP"),
        (3.68, 5.04, "ACROSS THE UNITED STATES", "UNITED STATES"),
    ),
    "kitchen_origin": (
        (0.00, 1.24, "STARTED IN MY KITCHEN", "KITCHEN"),
        (1.24, 2.721, "IN 2012", "2012"),
    ),
    "sleep_reveal": (
        (0.00, 1.32, "THE BUSINESS WASN'T AI", "AI"),
        (1.32, 2.38, "OR CRYPTO", "CRYPTO"),
        (2.38, 4.90, "IT WAS HOME SLEEP TESTING", "SLEEP"),
    ),
    "patient_scale": (
        (0.00, 2.28, "A FEW HUNDRED PATIENTS", "HUNDRED"),
        (2.28, 3.54, "EVERY MONTH", "MONTH"),
        (3.54, 5.62, "NOW WE'VE TESTED", "NOW"),
        (5.62, 8.18, "OVER ONE MILLION", "ONE MILLION"),
    ),
    "story_cta": (
        (0.00, 1.06, "LIKE AND SUBSCRIBE", "LIKE"),
        (1.06, 2.06, "THEN COMMENT", "COMMENT"),
        (2.06, 3.54, "WHAT BORING BUSINESS", "BORING"),
        (3.54, 5.00, "WOULD YOU BUILD?", "YOU"),
    ),
    "service_moat": (
        (0.00, 2.30, "OTHER PRODUCTS EXIST", "OTHER"),
        (2.30, 4.10, "WHAT SEPARATES US", "SEPARATES"),
        (4.10, 6.20, "IS EVERYTHING AROUND", "EVERYTHING"),
        (6.20, 8.50, "THE PRODUCT", "PRODUCT"),
        (8.50, 10.80, "THE SERVICE LEVEL", "SERVICE"),
        (10.80, 13.68, "IS WHAT'S IMPORTANT", "IMPORTANT"),
    ),
    "team_scale": (
        (0.00, 1.90, "MY STAFF MADE MORE", "MORE"),
        (1.90, 3.00, "MONEY THAN ME", "ME"),
        (3.00, 4.20, "I WAS WILLING", "WILLING"),
        (4.20, 5.65, "TO INVEST IN MY TEAM", "TEAM"),
        (5.65, 6.721, "THAT HELPS YOU SCALE", "SCALE"),
    ),
    "payoff": (
        (0.00, 1.42, "THE JET WAS THE REWARD", "REWARD"),
        (1.42, 2.62, "BETTER SERVICE", "SERVICE"),
        (2.62, 3.80, "PAYING THE TEAM", "TEAM"),
        (3.80, 5.20, "WAS THE BUSINESS", "BUSINESS"),
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hook-only", action="store_true", help="Render only the 0–3.2s rough-hook gate")
    return parser.parse_args()


def run(args: list[str | Path], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(str(arg) for arg in args), flush=True)
    return subprocess.run(
        [str(arg) for arg in args], cwd=ROOT, check=True, text=True,
        capture_output=capture,
    )


def probe(path: Path) -> dict[str, Any]:
    result = run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
        capture=True,
    )
    return json.loads(result.stdout)


def frames_for(seconds: float) -> int:
    return max(1, round(seconds * FPS))


def encode_args() -> list[str]:
    return [
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-pix_fmt", "yuv420p", "-r", str(FPS),
    ]


def crop_expr(turns: tuple[tuple[float, float], ...]) -> str:
    scaled_width = 3414
    span = scaled_width - WIDTH

    def x_for(focus: float) -> int:
        return round(span * focus)

    expr = str(x_for(turns[-1][1]))
    for index in range(len(turns) - 2, -1, -1):
        boundary = turns[index + 1][0]
        expr = f"if(lt(t,{boundary:.3f}),{x_for(turns[index][1])},{expr})"
    return expr


def source_crop(segment: Segment) -> str:
    x_expr = crop_expr(segment.turns)
    zoom_width = round(WIDTH * segment.zoom)
    zoom_height = round(HEIGHT * segment.zoom)
    clean_height = HEIGHT - CAPTION_BAND_PX
    recovery_width = round(WIDTH * HEIGHT / clean_height)
    return (
        f"scale=3414:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:'{x_expr}':0,"
        f"scale={zoom_width}:{zoom_height}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:(in_w-{WIDTH})/2:0,"
        f"crop={WIDTH}:{clean_height}:0:0,"
        f"scale={recovery_width}:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:({recovery_width}-{WIDTH})/2:0,"
        "eq=contrast=1.04:saturation=1.04,setsar=1,format=yuv420p"
    )


def render_source_segment(segment: Segment, output: Path) -> int:
    if segment.duration >= 15.0:
        raise ValueError(f"Source clip reaches 15 seconds: {segment.name}")
    frame_count = frames_for(segment.duration)
    coarse_start = max(0.0, segment.start - 5.0)
    fine_start = segment.start - coarse_start
    fine_end = fine_start + segment.duration
    video_filter = (
        f"trim=start={fine_start:.6f}:end={fine_end:.6f},setpts=PTS-STARTPTS,"
        f"{source_crop(segment)},fps={FPS}"
    )
    if segment.kind == "source":
        audio_filter = (
            f"atrim=start={fine_start:.6f}:end={fine_end:.6f},asetpts=PTS-STARTPTS,"
            "highpass=f=70,acompressor=threshold=0.125:ratio=2:attack=5:release=80:makeup=1.4,"
            "loudnorm=I=-16:TP=-1.5:LRA=10,aresample=48000:first_pts=0,apad,"
            f"atrim=0:{segment.duration:.6f},"
            f"afade=t=in:st=0:d={SEGMENT_FADE_IN:.2f},"
            f"afade=t=out:st={max(0.0, segment.duration - segment.fade_out):.6f}:d={segment.fade_out:.2f}"
        )
        run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{coarse_start:.6f}", "-i", SOURCE,
            "-filter_complex", f"[0:v]{video_filter}[v];[0:a]{audio_filter}[a]",
            "-map", "[v]", "-map", "[a]", "-frames:v", str(frame_count),
            *encode_args(), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", output,
        ])
    elif segment.kind == "silent_source":
        run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{coarse_start:.6f}", "-i", SOURCE,
            "-f", "lavfi", "-t", f"{segment.duration:.6f}", "-i", "anullsrc=r=48000:cl=stereo",
            "-filter_complex", f"[0:v]{video_filter}[v]",
            "-map", "[v]", "-map", "1:a:0", "-frames:v", str(frame_count),
            *encode_args(), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", output,
        ])
    elif segment.kind == "narration_source":
        if segment.audio is None:
            raise ValueError(f"Narration source segment missing audio: {segment.name}")
        audio_filter = (
            "aresample=48000,aformat=channel_layouts=stereo,highpass=f=70,"
            "acompressor=threshold=0.1:ratio=4:attack=5:release=100:makeup=1,"
            "loudnorm=I=-16:TP=-1.5:LRA=10,apad,"
            f"atrim=0:{segment.duration:.6f},"
            f"afade=t=in:st=0:d={SEGMENT_FADE_IN:.2f},"
            f"afade=t=out:st={segment.duration - SEGMENT_FADE_OUT:.6f}:d={SEGMENT_FADE_OUT:.2f}"
        )
        run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{coarse_start:.6f}", "-i", SOURCE,
            "-i", segment.audio,
            "-filter_complex", f"[0:v]{video_filter}[v];[1:a]{audio_filter}[a]",
            "-map", "[v]", "-map", "[a]", "-frames:v", str(frame_count),
            *encode_args(), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", output,
        ])
    else:
        raise ValueError(f"Unsupported source segment kind: {segment.kind}")
    return frame_count


def render_pexels_segment(segment: Segment, output: Path) -> int:
    if segment.audio is None or segment.visual is None:
        raise ValueError(f"Pexels segment missing inputs: {segment.name}")
    frame_count = frames_for(segment.duration)
    crop = (
        "scale=1134:2150:force_original_aspect_ratio=increase:flags=lanczos,"
        "crop=1080:1920:x='27+18*sin(t*0.85)':y='115+42*sin(t*0.62)',"
        "eq=contrast=1.05:saturation=0.92,setsar=1,format=yuv420p,fps=30"
    )
    audio_filter = (
        "aresample=48000,aformat=channel_layouts=stereo,highpass=f=70,"
        "acompressor=threshold=0.1:ratio=4:attack=5:release=100:makeup=1,"
        "loudnorm=I=-16:TP=-1.5:LRA=10,apad,"
        f"atrim=0:{segment.duration:.6f},"
        f"afade=t=in:st=0:d={SEGMENT_FADE_IN:.2f},"
        f"afade=t=out:st={segment.duration - SEGMENT_FADE_OUT:.6f}:d={SEGMENT_FADE_OUT:.2f}"
    )
    run([
        "ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-ss", f"{segment.start:.3f}",
        "-i", segment.visual, "-i", segment.audio,
        "-filter_complex", f"[0:v]{crop}[v];[1:a]{audio_filter}[a]",
        "-map", "[v]", "-map", "[a]", "-frames:v", str(frame_count),
        *encode_args(), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", output,
    ])
    return frame_count


def build_base(segments: tuple[Segment, ...], suffix: str = "") -> tuple[Path, list[dict[str, Any]], int]:
    SEGMENT_DIR.mkdir(parents=True, exist_ok=True)
    cursor = 0
    timeline: list[dict[str, Any]] = []
    outputs: list[Path] = []
    for index, segment in enumerate(segments):
        output = SEGMENT_DIR / f"{index:02d}_{segment.name}{suffix}.mp4"
        count = render_pexels_segment(segment, output) if segment.kind == "narration_pexels" else render_source_segment(segment, output)
        timeline.append({
            "name": segment.name,
            "kind": segment.kind,
            "act": segment.act,
            "source_start": segment.start if segment.uses_source else None,
            "source_end": segment.end if segment.uses_source else None,
            "source_duration": segment.duration if segment.uses_source else 0.0,
            "start_frame": cursor,
            "end_frame": cursor + count,
            "frames": count,
            "final_start": cursor / FPS,
            "final_end": (cursor + count) / FPS,
        })
        cursor += count
        outputs.append(output)

    concat = WORK / f"concat{suffix}.txt"
    concat.write_text("".join(f"file '{item.resolve()}'\n" for item in outputs), encoding="utf-8")
    base = WORK / f"base{suffix}.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat, "-c", "copy", base])
    return base, timeline, cursor


def new_card(width: int, height: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    card = Image.new("RGBA", (width, height), (11, 14, 20, 238))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle(
        (1, 1, width - 2, height - 2), radius=26,
        fill=(11, 14, 20, 238), outline=(255, 255, 255, 105), width=3,
    )
    return card, draw


def make_cards() -> list[Path]:
    PANELS.mkdir(parents=True, exist_ok=True)
    specs = (
        ("THE ORIGIN", (("$78", YELLOW), ("JAN 2015", GRAY))),
        ("THE PROMISE", (("OWN PLANE", BLUE), ("TAIL: 78", YELLOW))),
        ("THE SCALE", (("~200 / MONTH", BLUE), ("1,000,000+", GREEN), ("SOURCE CLAIM", GRAY))),
        ("THE MOAT", (("PRODUCT", BLUE), ("+ SERVICE", GREEN))),
        ("THE ENGINE", (("PAY TEAM", YELLOW), ("→ SCALE", GREEN))),
    )
    eyebrow = ImageFont.truetype(str(FONT_BOLD), 22)
    value = ImageFont.truetype(str(FONT_BLACK), 38)
    outputs: list[Path] = []
    for index, (title, rows) in enumerate(specs):
        card, draw = new_card(360, 285)
        draw.text((180, 32), title, font=eyebrow, fill=GRAY, anchor="mm")
        step = 74 if len(rows) == 3 else 92
        start_y = 88
        for row_index, (text, color) in enumerate(rows):
            draw.text((180, start_y + row_index * step), text, font=value, fill=color, anchor="mm")
        output = PANELS / f"card_{index}.png"
        card.save(output)
        outputs.append(output)
    return outputs


def ass_time(seconds: float) -> str:
    centiseconds = max(0, round(seconds * 100))
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    secs, cs = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{cs:02d}"


def ass_color(hex_color: str) -> str:
    value = hex_color.lstrip("#")
    return f"&H00{value[4:6]}{value[2:4]}{value[0:2]}"


def ass_escape(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def emphasized(text: str, keyword: str) -> str:
    escaped = ass_escape(text)
    key = ass_escape(keyword)
    if key not in escaped:
        return escaped
    return escaped.replace(
        key,
        f"{{\\c{ass_color(YELLOW)}\\fs90}}{key}{{\\c{ass_color('#FFFFFF')}\\fs80}}",
        1,
    )


def write_ass(timeline: list[dict[str, Any]], total_duration: float, suffix: str = "") -> Path:
    starts = {item["name"]: item["final_start"] for item in timeline}
    ends = {item["name"]: item["final_end"] for item in timeline}
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {WIDTH}", f"PlayResY: {HEIGHT}",
        "ScaledBorderAndShadow: yes", "WrapStyle: 2", "",
        "[V4+ Styles]",
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding",
        "Style: Caption,Komika Axis,80,&H00FFFFFF,&H00FFFFFF,&H00000000,&H85000000,-1,0,0,0,100,100,0,0,1,8,2,5,78,78,700,1",
        "Style: State,Arial Bold,40,&H00FFFFFF,&H00FFFFFF,&H00000000,&HD00B0E14,-1,0,0,0,100,100,0,0,3,2,0,8,60,60,1530,1",
        "Style: CTA,Arial Black,52,&H00FFFFFF,&H00FFFFFF,&H00000000,&HE00B0E14,-1,0,0,0,100,100,0,0,3,3,0,8,90,90,1450,1",
        "Style: Small,Arial Bold,26,&H80FFFFFF,&H80FFFFFF,&H80000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,7,28,28,28,1",
        "", "[Events]", "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
    ]

    for segment_name, events in CAPTIONS.items():
        if segment_name not in starts:
            continue
        base = starts[segment_name]
        for rel_start, rel_end, text, keyword in events:
            body = f"{{\\an5\\pos(540,1160)}}{emphasized(text, keyword)}"
            lines.append(f"Dialogue: 8,{ass_time(base + rel_start)},{ass_time(min(base + rel_end, total_duration))},Caption,,0,0,0,,{body}")

    states = (
        (0.00, starts.get("tail_promise", total_duration), "$78  →  WHY 78?", YELLOW),
        (starts.get("tail_promise", total_duration), starts.get("company_identity", total_duration), "PROMISE  →  RECEIPT", BLUE),
        (starts.get("company_identity", total_duration), starts.get("patient_scale", total_duration), "BORING PROBLEM", YELLOW),
        (starts.get("patient_scale", total_duration), ends.get("story_cta", total_duration), "KITCHEN  →  1,000,000+", GREEN),
        (starts.get("service_moat", total_duration), ends.get("team_scale", total_duration), "SERVICE  →  TEAM", BLUE),
        (starts.get("payoff", total_duration), total_duration, "REWARD  ≠  BUSINESS", YELLOW),
    )
    for start, end, text, color in states:
        if end > start:
            lines.append(
                f"Dialogue: 6,{ass_time(start)},{ass_time(end)},State,,0,0,0,,"
                f"{{\\an8\\pos(540,220)\\c{ass_color(color)}\\fad(80,80)}}{text}"
            )

    if "story_cta" in starts:
        cta = starts["story_cta"]
        controls = (
            (0.00, 1.06, "LIKE • BACK BORING BUSINESS", GREEN),
            (1.06, 2.06, "SUBSCRIBE • LEARN THE MOAT", BLUE),
            (2.06, 5.00, "COMMENT • WHAT WOULD YOU BUILD?", YELLOW),
        )
        for start, end, text, color in controls:
            lines.append(
                f"Dialogue: 9,{ass_time(cta + start)},{ass_time(cta + end)},CTA,,0,0,0,,"
                f"{{\\an8\\pos(540,400)\\c{ass_color(color)}\\fad(80,80)}}{text}"
            )

    if "sleep_reveal" in starts:
        lines.append(
            f"Dialogue: 9,{ass_time(starts['sleep_reveal'])},{ass_time(ends['sleep_reveal'])},Small,,0,0,0,,"
            "{\\an3\\pos(1030,1870)}ILLUSTRATION • PEXELS 7131825"
        )
    if "story_cta" in starts:
        lines.append(
            f"Dialogue: 9,{ass_time(starts['story_cta'])},{ass_time(ends['story_cta'])},Small,,0,0,0,,"
            "{\\an3\\pos(1030,1870)}ILLUSTRATION • PEXELS 7643614"
        )

    for item in timeline:
        if item["kind"] in {"source", "narration_source", "silent_source"}:
            lines.append(
                f"Dialogue: 5,{ass_time(item['final_start'])},{ass_time(item['final_end'])},Small,,0,0,0,,"
                "{\\an7\\pos(34,1810)}SOURCE • SCHOOL OF HARD KNOCKS"
            )

    thirds = [0.0, total_duration / 3, 2 * total_duration / 3, total_duration]
    positions = [(40, 72), (760, 72), (40, 1785)]
    for index, (start, end) in enumerate(zip(thirds[:-1], thirds[1:])):
        x, y = positions[index]
        lines.append(
            f"Dialogue: 10,{ass_time(start)},{ass_time(end)},Small,,0,0,0,,"
            f"{{\\an7\\pos({x},{y})}}HARD KNOCKS LAB"
        )

    output = WORK / f"captions_and_overlays{suffix}.ass"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def make_positioned_track(source: Path, start: float, total: float, output: Path, volume: float) -> Path:
    source_filter = f"aresample=48000,aformat=channel_layouts=stereo,volume={volume:.6f}"
    if start <= 0:
        run([
            "ffmpeg", "-y", "-v", "error", "-i", source,
            "-filter_complex", f"[0:a]{source_filter},apad,atrim=0:{total:.6f}[out]",
            "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", output,
        ])
    else:
        run([
            "ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-t", f"{start:.6f}",
            "-i", "anullsrc=r=48000:cl=stereo", "-i", source,
            "-filter_complex",
            f"[1:a]{source_filter}[clip];[0:a][clip]concat=n=2:v=0:a=1,apad,atrim=0:{total:.6f}[out]",
            "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", output,
        ])
    return output


def build_timed_audio(total: float, starts: dict[str, float], hook_only: bool = False) -> Path:
    definitions: list[tuple[str, Path, float, float]] = [
        ("hook_origin", HOOK_HIT, 0.06, math.pow(10, -11 / 20)),
        ("jet_question", JET_WHOOSH, 1.94, math.pow(10, -14 / 20)),
    ]
    if not hook_only:
        definitions.extend([
            ("promise", JET_WHOOSH, starts["tail_promise"], math.pow(10, -17 / 20)),
            ("company", PROOF_TICK, starts["company_identity"], math.pow(10, -16 / 20)),
            ("scale", PROOF_TICK, starts["patient_scale"], math.pow(10, -14 / 20)),
            ("cta_like", CTA_CLICK, starts["story_cta"] + 0.20, math.pow(10, -18 / 20)),
            ("cta_sub", CTA_CLICK, starts["story_cta"] + 1.45, math.pow(10, -18 / 20)),
            ("cta_comment", CTA_CLICK, starts["story_cta"] + 2.70, math.pow(10, -18 / 20)),
            ("service", PROOF_TICK, starts["service_moat"], math.pow(10, -17 / 20)),
            ("payoff", PAYOFF_HIT, starts["payoff"], math.pow(10, -16 / 20)),
        ])
    tracks: list[Path] = []
    for name, source, start, volume in definitions:
        tracks.append(make_positioned_track(source, max(0.0, start), total, AUDIO_DIR / f"positioned_{name}.wav", volume))
    output = AUDIO_DIR / ("timed_hook.wav" if hook_only else "timed_overlays.wav")
    inputs: list[str] = []
    for track in tracks:
        inputs.extend(["-i", str(track)])
    labels = "".join(f"[{index}:a]" for index in range(len(tracks)))
    run([
        "ffmpeg", "-y", "-v", "error", *inputs,
        "-filter_complex", f"{labels}amix=inputs={len(tracks)}:duration=longest:normalize=0,atrim=0:{total:.6f}[out]",
        "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", output,
    ])
    return output


def overlay_prepare(index: int, start: float, end: float) -> str:
    return (
        f"[{index}:v]scale=360:285:flags=lanczos,format=rgba,"
        f"fade=t=in:st={start:.3f}:d=0.14:alpha=1,"
        f"fade=t=out:st={max(start, end - 0.16):.3f}:d=0.16:alpha=1"
    )


def composite(
    base: Path,
    timeline: list[dict[str, Any]],
    total_frames: int,
    cards: list[Path],
    ass_file: Path,
    output: Path,
    hook_only: bool = False,
) -> None:
    starts = {item["name"]: item["final_start"] for item in timeline}
    ends = {item["name"]: item["final_end"] for item in timeline}
    total = total_frames / FPS
    if hook_only:
        total = min(total, 3.20)
        total_frames = round(total * FPS)
    timed = build_timed_audio(total, starts, hook_only=hook_only)
    ass_escaped = str(ass_file).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")

    if hook_only:
        windows = (
            (0.08, min(ends["origin_78"] - 0.05, total - 0.05), 650, 310, 0),
            (starts["hook_question"], total - 0.05, 650, 310, 1),
        )
    else:
        windows = (
            (0.08, ends["origin_78"] - 0.05, 650, 310, 0),
            (starts["hook_question"], ends["receipt_bridge"] - 0.05, 40, 310, 1),
            (starts["patient_scale"], ends["scale_hold"] - 0.02, 650, 310, 2),
            (starts["service_moat"], ends["service_moat"] - 0.05, 40, 310, 3),
            (starts["team_scale"], ends["team_scale"] - 0.05, 650, 310, 4),
        )

    graph: list[str] = []
    current = "0:v"
    for offset, (start, end, x, y, card_index) in enumerate(windows, start=1):
        graph.append(overlay_prepare(offset, start, end) + f"[card{offset}]")
        next_label = f"v{offset}"
        graph.append(
            f"[{current}][card{offset}]overlay=x={x}:y={y}:eof_action=pass:"
            f"enable='between(t,{start:.3f},{end:.3f})'[{next_label}]"
        )
        current = next_label
    graph.append(f"[{current}]subtitles='{ass_escaped}':fontsdir='{FONT_KOMIKA.parent}',format=yuv420p[vout]")

    timed_input = 1 + len(windows)
    bed_input = timed_input + 1
    graph.extend([
        "[0:a]aresample=48000,aformat=channel_layouts=stereo[basea]",
        f"[{timed_input}:a]aresample=48000,aformat=channel_layouts=stereo[timed]",
        f"[{bed_input}:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.55[bed]",
        f"[basea][timed][bed]amix=inputs=3:duration=longest:normalize=0,atrim=0:{total:.6f},"
        "loudnorm=I=-16.5:TP=-2.0:LRA=10,volume=-0.5dB,alimiter=limit=0.82:level=false[aout]",
    ])
    script = WORK / ("hook.ffscript" if hook_only else "final.ffscript")
    script.write_text(";\n".join(graph) + "\n", encoding="utf-8")

    output.parent.mkdir(parents=True, exist_ok=True)
    inputs: list[str | Path] = ["-i", base]
    for _, _, _, _, card_index in windows:
        inputs.extend(["-loop", "1", "-t", f"{total + 1:.3f}", "-i", cards[card_index]])
    inputs.extend(["-i", timed, "-i", MUSIC_BED])
    run([
        "ffmpeg", "-y", "-v", "error", *inputs,
        "-filter_complex_script", script, "-map", "[vout]", "-map", "[aout]",
        "-frames:v", str(total_frames), *encode_args(),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart", "-t", f"{total:.6f}", output,
    ])


def validate_manifest() -> None:
    data = json.loads(SFX_MANIFEST.read_text())
    required_ids = {
        "hardknocks_v22_hook_origin_hit",
        "hardknocks_v22_jet_motion_whoosh",
        "hardknocks_v22_proof_tick",
        "hardknocks_v22_cta_click",
        "hardknocks_v22_payoff_warm_hit",
        "hardknocks_v22_restrained_finance_bed",
    }
    approved = {
        item["id"] for item in data.get("assets", [])
        if item.get("approval_status") == "approved" and item.get("rights_status") == "cleared"
    }
    missing = sorted(required_ids - approved)
    if missing:
        raise RuntimeError(f"SFX manifest approval missing: {missing}")


def validate_final(timeline: list[dict[str, Any]]) -> dict[str, Any]:
    data = probe(FINAL)
    video = next(stream for stream in data["streams"] if stream["codec_type"] == "video")
    audio = next(stream for stream in data["streams"] if stream["codec_type"] == "audio")
    duration = float(data["format"]["duration"])
    source_segments = [item for item in timeline if item["source_duration"] > 0]
    total_source = sum(item["source_duration"] for item in source_segments)
    cta_start = next(item["final_start"] for item in timeline if item["name"] == "story_cta")
    checks = {
        "width": video.get("width") == WIDTH,
        "height": video.get("height") == HEIGHT,
        "codec": video.get("codec_name") == "h264",
        "pixel_format": video.get("pix_fmt") == "yuv420p",
        "frame_rate": video.get("r_frame_rate") == "30/1",
        "audio_codec": audio.get("codec_name") == "aac",
        "audio_rate": audio.get("sample_rate") == "48000",
        "audio_channels": audio.get("channels") == 2,
        "duration": 50.0 <= duration <= 75.0,
        "all_source_clips_under_15s": all(item["source_duration"] < 15.0 for item in source_segments),
        "total_source_under_50pct": total_source < SOURCE_DURATION / 2,
        "three_source_mix": SOURCE.exists() and PEXELS_SLEEP.exists() and PEXELS_TEAM.exists() and len(list(PANELS.glob("*.png"))) >= 5,
        "commentary_track": all(path.exists() for path in (HOOK_QUESTION, RECEIPT_BRIDGE, SLEEP_BRIDGE, CTA_AUDIO, PAYOFF_AUDIO)),
        "cta_window": 38.0 <= cta_start <= 42.0,
        "caption_at_frame_zero": CAPTIONS["origin_78"][0][0] <= 0.2,
    }
    if not all(checks.values()):
        raise RuntimeError(f"Final validation failed: {checks}")
    report = {
        "final": str(FINAL),
        "duration": duration,
        "checks": checks,
        "cta_start": cta_start,
        "total_source_duration": total_source,
        "source_duration": SOURCE_DURATION,
        "source_use_percent": 100 * total_source / SOURCE_DURATION,
        "timeline": timeline,
    }
    (WORK / "timeline.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def require_inputs() -> None:
    required = (
        SOURCE, PEXELS_SLEEP, PEXELS_TEAM, HOOK_QUESTION, RECEIPT_BRIDGE,
        SLEEP_BRIDGE, CTA_AUDIO, PAYOFF_AUDIO, HOOK_HIT, JET_WHOOSH,
        PROOF_TICK, CTA_CLICK, PAYOFF_HIT, MUSIC_BED, SFX_MANIFEST,
        FONT_KOMIKA, FONT_BOLD, FONT_BLACK,
    )
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required inputs:\n" + "\n".join(missing))
    for segment in SEGMENTS:
        if segment.uses_source and segment.duration >= 15.0:
            raise ValueError(f"Every source segment must be below 15 seconds: {segment.name}")
        if segment.kind.startswith("narration") and segment.audio is None:
            raise ValueError(f"Narration audio missing: {segment.name}")
    validate_manifest()


def main() -> None:
    args = parse_args()
    require_inputs()
    for directory in (WORK, SEGMENT_DIR, PANELS, CHECKS, AUDIO_DIR, HOOK_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    cards = make_cards()
    if args.hook_only:
        base, timeline, total_frames = build_base(SEGMENTS[:2], "_hook")
        ass_file = write_ass(timeline, total_frames / FPS, "_hook")
        composite(base, timeline, total_frames, cards, ass_file, ROUGH_HOOK, hook_only=True)
        print(json.dumps({"rough_hook": str(ROUGH_HOOK), "duration": 3.2}, indent=2))
        return

    base, timeline, total_frames = build_base(SEGMENTS)
    total_duration = total_frames / FPS
    ass_file = write_ass(timeline, total_duration)
    composite(base, timeline, total_frames, cards, ass_file, FINAL)
    report = validate_final(timeline)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
