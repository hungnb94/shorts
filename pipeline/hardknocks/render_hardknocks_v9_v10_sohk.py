#!/usr/bin/env python3
"""Render HardKnocks V9/V9R/V10/V10R from the SOHK long-form interview.

V9 tests a Live-Approach hook while preserving ADR-0017 with a moving,
same-interview subject inset. V10 is a comparison Short (not a control) with
a source-native Money+Number cold open. Both use two short TTS bridges,
proof-coupled evidence after the protected 0-10s window, word-burst captions,
and the established 1.03x retention finish.

V9R is the surgical original-voice revision: it removes V9's two synthetic
bridges, closes those timeline gaps, and preserves the hook, source beats,
caption language, evidence types, and finishing treatment.

V10R applies the reviewed SOHK Live-Approach grammar to V10's robot-founder
story without TTS or picture-in-picture: host -> driver -> G-Wagon proof ->
affordability question -> business/status escalation. The body remains an
Original-Voice Editorial Commentary treatment and finishes on "get rich slow."
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "hardknocks"
SOURCE = PROJECT / "source" / "E_9nX5ReMcY.mp4"
PEXELS_HOME = ROOT / "output/shared/pexels/home_laptop_5725850.mp4"
PEXELS_PAGES = ROOT / "output/shared/pexels/flipping_pages_36864123.mp4"
PEXELS_DRONE = ROOT / "output/shared/pexels/hovering_drone_9999365.mp4"
SHARED_WORK = PROJECT / "clips" / "sohk_work"
TTS_DIR = SHARED_WORK / "tts"
FONT_REGULAR = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
EDGE_TTS = Path.home() / ".local/bin/edge-tts"

WIDTH = 1080
HEIGHT = 1920
FPS = 30
POST_SPEED = 1.03
SOURCE_DURATION = 1617.0


@dataclass(frozen=True)
class Segment:
    name: str
    kind: str
    source_start: float
    source_end: float
    focus: float
    zoom: float
    captions: tuple[str, ...]
    tts_text: str = ""
    tts_file: str = ""
    pip: bool = False


@dataclass(frozen=True)
class Evidence:
    name: str
    start: float
    duration: float
    kind: str
    asset: str
    citation: str
    source_offset: float = 0.0
    focus: float = 0.5


@dataclass(frozen=True)
class Variant:
    key: str
    version: str
    final_name: str
    segments: tuple[Segment, ...]
    evidence: tuple[Evidence, ...]
    target_min: float
    target_max: float
    expected_tts_bridges: int = 2
    tail_pad: float = 0.0


A_SEGMENTS = (
    Segment(
        "live_approach",
        "source",
        330.34,
        338.76,
        0.70,
        1.00,
        (
            "EXCUSE ME, SIR",
            "IS THIS YOUR HOUSE?",
            "HOW DID YOU AFFORD THIS?",
            "WHAT MADE YOU WEALTHY?",
            "HOW'D YOU GET IN?",
            "WE THOUGHT YOU WERE UPS",
        ),
        pip=True,
    ),
    Segment("wealth_question", "source", 358.84, 361.56, 0.70, 1.20, ("HOW DID YOU GET RICH?", "HOW'D YOU AFFORD THIS?")),
    Segment("blackstone_setup", "source", 361.68, 367.76, 0.30, 1.20, ("A LOT OF WORK", "AN ADVERTISING COMPANY", "BLACKSTONE BOUGHT IT", "NOT ONCE — TWICE")),
    Segment("exit_question", "source", 368.68, 373.00, 0.70, 1.28, ("YOU SOLD TO BLACKSTONE", "FOR HOW MUCH?", "GIVE ME A RANGE")),
    Segment("exit_reveal", "source", 373.30, 375.78, 0.30, 1.34, ("$200 MILLION", "THEN BOUGHT IT BACK")),
    Segment(
        "bridge_origin",
        "tts",
        373.30,
        378.844,
        0.30,
        1.26,
        ("THE EXIT SOUNDS INSTANT", "THE ORIGIN STORY", "WAS NOTHING LIKE IT"),
        "The exit sounds instant. The origin story was nothing like it.",
        "a_bridge1.mp3",
    ),
    Segment("capital_question", "source", 377.90, 379.18, 0.70, 1.22, ("MONEY WHEN YOU STARTED?",)),
    Segment("basement_answer", "source", 379.18, 382.36, 0.30, 1.32, ("ABSOLUTELY NOTHING", "STARTED IN MY BASEMENT", "DIDN'T COME FROM MONEY")),
    Segment("driving_factor", "source", 386.24, 393.94, 0.70, 1.18, ("WHAT WAS THE TRIGGER?", "TO BUILD A COMPANY", "WORTH HUNDREDS", "OF MILLIONS?")),
    Segment("yellow_pages", "source", 393.96, 400.28, 0.30, 1.24, ("I SOLD YELLOW PAGES", "DOOR TO DOOR", "THEN BUILT THEIR", "INTERNET PROGRAM")),
    Segment(
        "bridge_commission",
        "tts",
        400.40,
        406.112,
        0.30,
        1.26,
        ("THE COMPANY COLLECTED", "THE UPSIDE", "HIS COMMISSION CHECK", "BARELY MOVED"),
        "The company collected the upside. His commission check barely moved.",
        "a_bridge2.mp3",
    ),
    Segment("agency_payoff", "source", 400.40, 404.46, 0.30, 1.34, ("THEY COLLECTED $100M", "THEY GAVE ME $10K", "I'M DOING THIS", "ON MY OWN")),
)

A_ORIGINAL_VOICE_SEGMENTS = tuple(segment for segment in A_SEGMENTS if segment.kind == "source")

B_SEGMENTS = (
    Segment("projection", "source", 789.72, 791.54, 0.30, 1.36, ("ON TRACK FOR", "OVER $100 MILLION")),
    Segment("age_question", "source", 791.54, 792.80, 0.70, 1.34, ("$100 MILLION?", "HOW OLD ARE YOU?")),
    Segment("age_answer", "source", 792.94, 793.78, 0.30, 1.42, ("I'M 30 YEARS OLD",)),
    Segment("disbelief", "source", 793.80, 795.26, 0.70, 1.40, ("NO, YOU'RE NOT", "ARE YOU SERIOUS?")),
    Segment("robots_answer", "source", 769.74, 770.32, 0.30, 1.38, ("I SELL ROBOTS",)),
    Segment("robots_repeat", "source", 770.32, 771.18, 0.70, 1.36, ("YOU SELL ROBOTS?",)),
    Segment("robots_confirm", "source", 771.18, 773.30, 0.30, 1.34, ("ALL ROBOTS", "YES — ACTUALLY")),
    Segment(
        "bridge_timeline",
        "tts",
        769.74,
        774.828,
        0.30,
        1.30,
        ("THE NUMBER SOUNDS INSTANT", "THE TIMELINE", "WAS ANYTHING BUT"),
        "The number sounds instant. The timeline was anything but.",
        "b_bridge1.mp3",
    ),
    Segment("money_question", "source", 796.52, 798.08, 0.70, 1.28, ("DID YOU COME FROM MONEY?", "MONEY WHEN YOU STARTED?")),
    Segment("drone_origin", "source", 798.08, 801.80, 0.30, 1.32, ("NO — I GOT LUCKY", "STARTED A DRONE BUSINESS", "IN HIGH SCHOOL")),
    Segment("drone_mechanism", "source", 802.86, 810.38, 0.30, 1.24, ("MARKETING WITH DRONES", "FIRST IN THE AREA", "DRONE PHOTOGRAPHY", "BUILT THEM", "TOOK THE PICTURES")),
    Segment(
        "bridge_lesson",
        "tts",
        828.72,
        831.936,
        0.30,
        1.30,
        ("HIS ADVICE", "IS THE OPPOSITE", "OF THE HEADLINE"),
        "His advice is the opposite of the headline.",
        "b_bridge2.mp3",
    ),
    Segment("patience", "source", 818.42, 823.56, 0.30, 1.26, ("A BIG PATIENCE LEVEL", "MOST PEOPLE DON'T HAVE", "IT TAKES LONGER")),
    Segment("fast_money", "source", 828.72, 834.60, 0.30, 1.32, ("FAST MONEY NEVER LASTS", "KEEP BUILDING", "BE PATIENT", "THAT'S AN ENTREPRENEUR")),
    Segment("four_years", "source", 844.82, 848.36, 0.30, 1.34, ("LONG-TERM GROWTH", "ROBOTICS: FOUR YEARS")),
    Segment("growth_proof", "source", 856.98, 864.36, 0.30, 1.34, ("ZERO TO $1 MILLION", "VERY QUICK", "THEN THE LAST 12 MONTHS", "THE JUMP WAS ~100X")),
    Segment("payoff_host", "source", 834.60, 837.50, 0.70, 1.40, ("LONGEVITY AND ENDURANCE", "IN OTHER WORDS", "YOU GET RICH SLOW")),
    Segment("payoff_yes", "source", 837.90, 838.20, 0.30, 1.42, ("YEAH",)),
)

C_SEGMENTS = (
    Segment("host_ownership", "source", 754.98, 755.70, 0.70, 1.42, ("DO YOU LIVE HERE?",)),
    Segment("subject_ownership", "source", 755.80, 756.98, 0.30, 1.42, ("YEAH — IT'S MY HOUSE",)),
    Segment("g_wagon_cutaway", "source", 752.30, 752.95, 0.30, 1.05, ()),
    Segment(
        "host_afford",
        "source",
        766.16,
        769.38,
        0.70,
        1.30,
        ("WHAT DID YOU DO", "TO AFFORD THIS PLACE?", "ONE OF THE RICHEST", "NEIGHBORHOODS IN AMERICA"),
    ),
    Segment("robots_answer", "source", 769.66, 770.30, 0.30, 1.40, ("I SELL ROBOTS",)),
    Segment("robots_repeat", "source", 770.52, 771.14, 0.70, 1.38, ("YOU SELL ROBOTS?",)),
    Segment("robots_confirm", "source", 771.14, 771.88, 0.30, 1.40, ("SELL ROBOTS",)),
    Segment("robots_question", "source", 772.16, 772.72, 0.70, 1.38, ("DO YOU ACTUALLY?",)),
    Segment(
        "humanoid_setup",
        "source",
        772.72,
        776.22,
        0.30,
        1.30,
        ("YOU'VE SEEN THE SILVER", "HUMANOIDS ONLINE"),
    ),
    Segment(
        "humanoid_authority",
        "source",
        776.74,
        778.66,
        0.30,
        1.38,
        ("WE'VE SOLD MORE HUMANOIDS", "THAN ANYONE IN THE WORLD"),
    ),
    Segment("authority_reaction", "source", 778.82, 779.30, 0.70, 1.42, ("ARE YOU SERIOUS?",)),
    Segment(
        "revenue_question",
        "source",
        787.62,
        789.52,
        0.70,
        1.28,
        ("MOST MONEY", "IN A SINGLE YEAR?"),
    ),
    Segment("projection", "source", 789.62, 791.42, 0.30, 1.38, ("ON TRACK FOR", "OVER $100 MILLION")),
    Segment("age_question", "source", 791.54, 792.76, 0.70, 1.38, ("$100 MILLION?", "HOW OLD ARE YOU?")),
    Segment("age_answer", "source", 792.96, 793.74, 0.30, 1.42, ("I'M 30 YEARS OLD",)),
    Segment("disbelief", "source", 793.80, 795.22, 0.70, 1.42, ("NO, YOU'RE NOT", "ARE YOU SERIOUS?")),
    Segment("money_question", "source", 795.74, 797.80, 0.70, 1.28, ("DID YOU COME FROM MONEY?", "MONEY WHEN YOU STARTED?")),
    Segment("drone_origin", "source", 797.88, 801.80, 0.30, 1.32, ("NO — I GOT LUCKY", "STARTED A DRONE BUSINESS", "IN HIGH SCHOOL")),
    Segment("drone_mechanism", "source", 802.86, 810.38, 0.30, 1.24, ("MARKETING WITH DRONES", "FIRST IN THE AREA", "DRONE PHOTOGRAPHY", "BUILT THEM", "TOOK THE PICTURES")),
    Segment("patience", "source", 818.42, 823.56, 0.30, 1.26, ("A BIG PATIENCE LEVEL", "MOST PEOPLE DON'T HAVE", "IT TAKES LONGER")),
    Segment("fast_money", "source", 828.72, 834.60, 0.30, 1.32, ("FAST MONEY NEVER LASTS", "KEEP BUILDING", "BE PATIENT", "THAT'S AN ENTREPRENEUR")),
    Segment("four_years", "source", 844.82, 848.36, 0.30, 1.34, ("LONG-TERM GROWTH", "ROBOTICS: FOUR YEARS")),
    Segment("growth_proof", "source", 856.98, 864.36, 0.30, 1.34, ("ZERO TO $1 MILLION", "VERY QUICK", "THEN THE LAST 12 MONTHS", "THE JUMP WAS ~100X")),
    Segment("payoff_host", "source", 834.60, 837.50, 0.70, 1.40, ("LONGEVITY AND ENDURANCE", "IN OTHER WORDS", "YOU GET RICH SLOW")),
    Segment("payoff_yes", "source", 837.90, 838.20, 0.30, 1.42, ("YEAH",)),
)

VARIANTS = {
    "a": Variant(
        "a",
        "v9",
        "2026-07-17-hardknocks_v9_live_approach_200m.mp4",
        A_SEGMENTS,
        (
            Evidence("exit_card", 19.60, 3.00, "panel", "a_exit.png", "INTERVIEW CLAIM"),
            Evidence("home_start", 25.00, 4.00, "video", str(PEXELS_HOME), "ILLUSTRATION: PEXELS", 1.0, 0.5),
            Evidence("printed_pages", 42.00, 4.00, "video", str(PEXELS_PAGES), "ILLUSTRATION: PEXELS", 0.5, 0.5),
            Evidence("commission_gap", 48.50, 5.00, "panel", "a_gap.png", "INTERVIEW CLAIM"),
        ),
        52.0,
        58.0,
    ),
    "b": Variant(
        "b",
        "v10",
        "2026-07-17-hardknocks_v10_100m_get_rich_slow.mp4",
        B_SEGMENTS,
        (
            Evidence("headline_reframe", 10.50, 3.00, "panel", "b_headline.png", "FOUNDER PROJECTION"),
            Evidence("drone_origin", 20.00, 4.00, "video", str(PEXELS_DRONE), "ILLUSTRATION: PEXELS", 2.0, 0.5),
            Evidence("four_year_timeline", 41.20, 4.00, "panel", "b_timeline.png", "INTERVIEW CLAIM"),
            Evidence("growth_curve", 47.50, 4.00, "panel", "b_growth.png", "INTERVIEW CLAIM"),
        ),
        50.0,
        56.0,
    ),
    "r": Variant(
        "r",
        "v9r",
        "2026-07-17-hardknocks_v9r_original_voice.mp4",
        A_ORIGINAL_VOICE_SEGMENTS,
        (
            Evidence("exit_card", 19.60, 3.00, "panel", "a_exit.png", "INTERVIEW CLAIM"),
            Evidence("home_start", 24.50, 3.50, "video", str(PEXELS_HOME), "ILLUSTRATION: PEXELS", 1.0, 0.5),
            Evidence("printed_pages", 36.50, 3.00, "video", str(PEXELS_PAGES), "ILLUSTRATION: PEXELS", 0.5, 0.5),
            Evidence("commission_gap", 42.00, 3.50, "panel", "a_gap.png", "INTERVIEW CLAIM"),
        ),
        44.0,
        47.0,
        0,
        0.65,
    ),
    "c": Variant(
        "c",
        "v10r",
        "2026-07-17-hardknocks_v10r_live_approach_original_voice.mp4",
        C_SEGMENTS,
        (
            Evidence("headline_reframe", 16.20, 3.20, "panel", "b_headline.png", "FOUNDER PROJECTION"),
            Evidence("drone_origin", 27.60, 4.10, "video", str(PEXELS_DRONE), "ILLUSTRATION: PEXELS", 2.0, 0.5),
            Evidence("four_year_timeline", 46.10, 4.10, "panel", "b_timeline.png", "INTERVIEW CLAIM"),
            Evidence("growth_curve", 51.00, 4.10, "panel", "b_growth.png", "INTERVIEW CLAIM"),
        ),
        45.0,
        60.0,
        0,
        0.65,
    ),
}


def run(args: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(str(arg) for arg in args), flush=True)
    return subprocess.run([str(arg) for arg in args], cwd=ROOT, check=True, text=True, capture_output=capture)


def probe(path: Path) -> dict[str, Any]:
    result = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)], capture=True)
    return json.loads(result.stdout)


def frames_for(seconds: float) -> int:
    return max(1, round(seconds * FPS))


def segment_duration(segment: Segment) -> float:
    if segment.kind == "tts":
        media = TTS_DIR / segment.tts_file
        if media.exists():
            return float(probe(media)["format"]["duration"])
    return segment.source_end - segment.source_start


def scaled_crop(focus: float, zoom: float) -> str:
    scaled_width = 3414
    crop_x = round((scaled_width - WIDTH) * focus)
    zoom_width = round(WIDTH * zoom)
    zoom_height = round(HEIGHT * zoom)
    return (
        f"scale={scaled_width}:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:{crop_x}:0,"
        f"scale={zoom_width}:{zoom_height}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:(in_w-{WIDTH})/2:0,"
        "eq=contrast=1.05:saturation=1.06,setsar=1,format=yuv420p"
    )


def encode_args() -> list[str]:
    return ["-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p", "-r", str(FPS)]


def ensure_tts(segment: Segment) -> Path:
    output = TTS_DIR / segment.tts_file
    if output.exists():
        return output
    if not EDGE_TTS.exists():
        raise FileNotFoundError(f"edge-tts missing: {EDGE_TTS}")
    output.parent.mkdir(parents=True, exist_ok=True)
    run([str(EDGE_TTS), "--voice", "en-US-AriaNeural", "--rate=-2%", "--text", segment.tts_text, "--write-media", str(output)])
    return output


def render_source_segment(segment: Segment, output: Path) -> int:
    duration = segment_duration(segment)
    frame_count = frames_for(duration)
    audio_filter = (
        "highpass=f=70,acompressor=threshold=0.125:ratio=2.0:attack=5:release=80:makeup=1.5,"
        f"loudnorm=I=-16:TP=-1.5:LRA=10,aresample=48000:first_pts=0,apad,atrim=0:{duration:.6f}"
    )
    if segment.pip:
        main_filter = scaled_crop(segment.focus, segment.zoom)
        pip_filter = (
            "scale=3414:1920:flags=lanczos,"
            "crop=760:1250:560:120,scale=500:822:flags=lanczos,"
            "pad=516:838:8:8:color=0xFFD447,setsar=1"
        )
        filter_complex = (
            f"[0:v]{main_filter},fps={FPS}[main];"
            f"[1:v]{pip_filter},fps={FPS}[pip];"
            "[main][pip]overlay=36:110:shortest=1[vout]"
        )
        run([
            "ffmpeg", "-y", "-v", "error",
            "-ss", f"{segment.source_start:.6f}", "-i", str(SOURCE),
            "-ss", "368.680000", "-i", str(SOURCE),
            "-t", f"{duration:.6f}",
            "-filter_complex", filter_complex,
            "-map", "[vout]", "-map", "0:a:0", "-af", audio_filter,
            "-frames:v", str(frame_count), *encode_args(),
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(output),
        ])
    else:
        run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{segment.source_start:.6f}", "-i", str(SOURCE),
            "-t", f"{duration:.6f}", "-vf", f"{scaled_crop(segment.focus, segment.zoom)},fps={FPS}",
            "-af", audio_filter, "-frames:v", str(frame_count), *encode_args(),
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(output),
        ])
    return frame_count


def render_tts_segment(segment: Segment, output: Path) -> int:
    tts = ensure_tts(segment)
    duration = float(probe(tts)["format"]["duration"])
    frame_count = frames_for(duration)
    run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{segment.source_start:.6f}", "-i", str(SOURCE), "-i", str(tts),
        "-t", f"{duration:.6f}", "-vf", f"{scaled_crop(segment.focus, segment.zoom)},fps={FPS}",
        "-map", "0:v:0", "-map", "1:a:0",
        "-af", f"highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=8,aresample=48000,apad,atrim=0:{duration:.6f}",
        "-frames:v", str(frame_count), *encode_args(),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(output),
    ])
    return frame_count


def make_panel(path: Path, title: str, rows: list[tuple[str, str]], accent: str = "#FFD447") -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#0B0E14")
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.truetype(str(FONT_BOLD), 66)
    big_font = ImageFont.truetype(str(FONT_BOLD), 116)
    label_font = ImageFont.truetype(str(FONT_BOLD), 42)
    small_font = ImageFont.truetype(str(FONT_REGULAR), 32)
    draw.rectangle((0, 0, WIDTH, 18), fill=accent)
    draw.text((70, 130), title, font=title_font, fill="white")
    y = 390
    for value, label in rows:
        draw.rounded_rectangle((65, y, WIDTH - 65, y + 330), radius=34, fill="#171D29", outline=accent, width=5)
        draw.text((110, y + 55), value, font=big_font, fill=accent)
        draw.text((110, y + 210), label, font=label_font, fill="white")
        y += 390
    draw.text((70, HEIGHT - 150), "CLAIM FROM THE INTERVIEW", font=small_font, fill="#AAB3C4")
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def make_panels(panels: Path) -> None:
    make_panel(panels / "a_exit.png", "$200M EXIT", [("$200M", "SOLD TO BLACKSTONE"), ("BOUGHT BACK", "THE SAME COMPANY")])
    make_panel(panels / "a_gap.png", "THE COMMISSION GAP", [("$100M", "COMPANY COLLECTED"), ("$10K", "HIS CHECK")])
    make_panel(panels / "b_headline.png", "THE HEADLINE", [(">$100M", "ON TRACK THIS YEAR"), ("AGE 30", "FOUNDER'S ANSWER")])
    make_panel(panels / "b_timeline.png", "THE TIMELINE", [("HIGH SCHOOL", "DRONE PHOTOGRAPHY"), ("4 YEARS", "BUILDING ROBOTICS")])
    make_panel(panels / "b_growth.png", "THE BUILD", [("YEAR 1: $1M", "FROM ZERO"), ("~100X", "LATER JUMP CLAIM")])


def build_base(variant: Variant, work: Path) -> tuple[Path, list[dict[str, Any]], int]:
    clips = work / "segments"
    clips.mkdir(parents=True, exist_ok=True)
    timeline: list[dict[str, Any]] = []
    cursor = 0
    outputs: list[Path] = []
    for index, segment in enumerate(variant.segments):
        output = clips / f"{index:02d}_{segment.name}.mp4"
        count = render_tts_segment(segment, output) if segment.kind == "tts" else render_source_segment(segment, output)
        timeline.append({**asdict(segment), "start_frame": cursor, "frames": count, "end_frame": cursor + count})
        cursor += count
        outputs.append(output)
    concat = work / "concat.txt"
    concat.write_text("".join(f"file '{path.resolve()}'\n" for path in outputs), encoding="utf-8")
    base = work / "base.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(base)])
    return base, timeline, cursor


def render_evidence(evidence: Evidence, panels: Path, work: Path, index: int) -> Path:
    output = work / f"evidence_{index:02d}_{evidence.name}.mp4"
    frame_count = frames_for(evidence.duration)
    if evidence.kind == "video":
        asset = Path(evidence.asset)
        vf = (
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={WIDTH}:{HEIGHT}:(in_w-{WIDTH})*{evidence.focus:.3f}:0,"
            "eq=contrast=1.05:saturation=0.96,setsar=1,format=yuv420p"
        )
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{evidence.source_offset:.3f}", "-i", str(asset),
             "-t", f"{evidence.duration:.6f}", "-vf", f"{vf},fps={FPS}", "-an", "-frames:v", str(frame_count),
             *encode_args(), str(output)])
    else:
        panel = panels / evidence.asset
        vf = (
            f"scale={WIDTH}:{HEIGHT},"
            f"zoompan=z='1.03+0.025*sin(on*0.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={frame_count}:s={WIDTH}x{HEIGHT}:fps={FPS},setsar=1,format=yuv420p"
        )
        run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(panel), "-t", f"{evidence.duration:.6f}",
             "-vf", vf, "-an", "-frames:v", str(frame_count), *encode_args(), str(output)])
    return output


def composite_evidence(variant: Variant, base: Path, panels: Path, work: Path, total_frames: int) -> Path:
    args: list[str] = ["-i", str(base)]
    lines: list[str] = []
    current = "0:v"
    for index, evidence in enumerate(variant.evidence, start=1):
        excerpt = render_evidence(evidence, panels, work, index)
        args.extend(["-i", str(excerpt)])
        shifted = f"e{index}"
        output = f"v{index}"
        end = evidence.start + evidence.duration
        lines.append(f"[{index}:v]setpts=PTS-STARTPTS+{evidence.start:.6f}/TB[{shifted}]")
        lines.append(f"[{current}][{shifted}]overlay=0:0:eof_action=pass:shortest=0:enable='between(t,{evidence.start:.6f},{end:.6f})'[{output}]")
        current = output
    script = work / "evidence.ffscript"
    script.write_text(";\n".join(lines) + "\n", encoding="utf-8")
    output = work / "with_evidence.mp4"
    run(["ffmpeg", "-y", "-v", "error", *args, "-filter_complex_script", str(script),
         "-map", f"[{current}]", "-map", "0:a:0", "-frames:v", str(total_frames), *encode_args(),
         "-c:a", "copy", "-movflags", "+faststart", str(output)])
    return output


def ass_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}:{minutes:02d}:{seconds % 60:05.2f}"


def emphasis(text: str) -> bool:
    return any(token in text for token in ("$", "100", "200", "30", "NOTHING", "BASEMENT", "FAST MONEY", "RICH SLOW", "OWN"))


def make_subtitles(variant: Variant, timeline: list[dict[str, Any]], work: Path, raw_duration: float) -> Path:
    ass = work / "captions.ass"
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,Arial,76,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,7,2,2,55,55,170,1
Style: Emphasis,Arial,82,&H0047D4FF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,7,2,2,50,50,170,1
Style: Citation,Arial,25,&H00FFFFFF,&H000000FF,&H00000000,&HA0000000,-1,0,0,0,100,100,0,0,3,2,0,9,30,30,35,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    for index, item in enumerate(timeline):
        start = item["start_frame"] / FPS
        end = item["end_frame"] / FPS
        captions = item["captions"]
        if not captions:
            continue
        span = (end - start) / len(captions)
        for caption_index, text in enumerate(captions):
            cap_start = start + caption_index * span
            cap_end = end if caption_index == len(captions) - 1 else start + (caption_index + 1) * span
            style = "Emphasis" if emphasis(text) else "Hook"
            animation = r"{\fad(50,60)\t(0,130,\fscx104\fscy104)}"
            lines.append(f"Dialogue: 3,{ass_time(cap_start)},{ass_time(cap_end)},{style},,0,0,0,,{animation}{text}\n")
    lines.append(f"Dialogue: 2,{ass_time(10.20)},{ass_time(raw_duration)},Citation,,0,0,0,,SOURCE: SCHOOL OF HARD KNOCKS\n")
    for evidence in variant.evidence:
        lines.append(f"Dialogue: 4,{ass_time(evidence.start)},{ass_time(evidence.start + evidence.duration)},Citation,,0,0,0,,{evidence.citation}\n")
    ass.write_text("".join(lines), encoding="utf-8")
    return ass


def generate_audio_assets(work: Path, raw_duration: float) -> tuple[Path, Path]:
    music = work / "music.wav"
    impact = work / "impact.wav"
    music_expr = (
        "aevalsrc=(0.055*sin(2*PI*58*t)*(0.3+0.7*exp(-7*mod(t\\,0.5)))+"
        "0.014*sin(2*PI*116*t))*min(1\\,t/0.7)*min(1\\,("
        f"{raw_duration:.6f}-t)/0.7):s=48000:d={raw_duration:.6f}"
    )
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", music_expr,
         "-af", "lowpass=f=1300,highpass=f=35", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(music)])
    impact_expr = "aevalsrc=(0.23*sin(2*PI*(170-100*t)*t)+0.06*sin(2*PI*430*t))*exp(-11*t):s=48000:d=0.42"
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", impact_expr,
         "-af", "lowpass=f=1900", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(impact)])
    return music, impact


def mix_and_caption(video: Path, subtitles: Path, music: Path, impact: Path, work: Path, raw_duration: float, variant: Variant) -> Path:
    impact_times = [0.0] + [e.start for e in variant.evidence]
    lines = [
        "[0:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.02[voice]",
        "[1:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.090[music]",
    ]
    split = "".join(f"[i{x}]" for x in range(len(impact_times)))
    lines.append(f"[2:a]aresample=48000,aformat=channel_layouts=stereo,asplit={len(impact_times)}{split}")
    labels = ["[voice]", "[music]"]
    for index, timestamp in enumerate(impact_times):
        delay = round(timestamp * 1000)
        volume = 0.16 if index == 0 else 0.08
        lines.append(f"[i{index}]adelay={delay}|{delay},volume={volume:.2f}[hit{index}]")
        labels.append(f"[hit{index}]")
    lines.append("".join(labels) + f"amix=inputs={len(labels)}:duration=longest:normalize=0,alimiter=limit=0.94,atrim=0:{raw_duration:.6f}[aout]")
    script = work / "audio.ffscript"
    script.write_text(";\n".join(lines) + "\n", encoding="utf-8")
    output = work / "raw_mix.mp4"
    vf = (
        f"subtitles='{subtitles}':fontsdir='/System/Library/Fonts/Supplemental',"
        f"drawbox=x=0:y=ih-5:w=iw*(t/{raw_duration:.6f}):h=5:color=0xFFD447:t=fill"
    )
    run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-i", str(music), "-i", str(impact),
         "-filter_complex_script", str(script), "-map", "0:v:0", "-map", "[aout]", "-vf", vf,
         *encode_args(), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(output)])
    return output


def finish(raw_mix: Path, final: Path, tail_pad: float = 0.0) -> None:
    final.parent.mkdir(parents=True, exist_ok=True)
    video_filter = f"setpts=PTS/{POST_SPEED}"
    audio_filter = f"atempo={POST_SPEED}"
    output_limit = ["-shortest"]
    if tail_pad > 0:
        raw_duration = float(probe(raw_mix)["format"]["duration"])
        target_duration = raw_duration / POST_SPEED + tail_pad
        video_filter = f"tpad=stop_mode=clone:stop_duration={tail_pad * POST_SPEED:.6f},setpts=PTS/{POST_SPEED}"
        audio_filter += f",apad=whole_dur={target_duration:.6f},atrim=0:{target_duration:.6f}"
        output_limit = ["-t", f"{target_duration:.6f}"]
    run(["ffmpeg", "-y", "-v", "error", "-i", str(raw_mix),
         "-filter_complex", f"[0:v]{video_filter}[v];[0:a]{audio_filter}[a]",
         "-map", "[v]", "-map", "[a]", *encode_args(), "-c:a", "aac", "-b:a", "192k",
         "-ar", "48000", "-ac", "2", "-movflags", "+faststart", *output_limit, str(final)])


def extract_checks(final: Path, checks: Path) -> None:
    checks.mkdir(parents=True, exist_ok=True)
    info = probe(final)
    duration = float(info["format"]["duration"])
    timestamps = [0.0, 0.1, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 18, 22, 26, 30, 35, 40, 45, 50, 54]
    for index, timestamp in enumerate(t for t in timestamps if t < duration):
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{timestamp:.2f}", "-i", str(final),
             "-frames:v", "1", "-q:v", "2", str(checks / f"{index:02d}_{timestamp:05.2f}.jpg")])
    run(["ffmpeg", "-y", "-v", "error", "-i", str(final),
         "-vf", "fps=1/2.7,drawtext=fontfile='/System/Library/Fonts/HelveticaNeue.ttc':text='%{pts\\:hms}':x=10:y=10:fontsize=32:fontcolor=yellow:borderw=3:bordercolor=black,scale=270:-2,tile=5x4:padding=4:margin=4",
         "-frames:v", "1", str(checks / "contact.jpg")])
    run(["ffmpeg", "-y", "-v", "error", "-ss", "0", "-t", "10", "-i", str(final),
         "-vf", "fps=2,drawtext=fontfile='/System/Library/Fonts/HelveticaNeue.ttc':text='%{pts\\:hms}':x=10:y=10:fontsize=32:fontcolor=yellow:borderw=3:bordercolor=black,scale=270:-2,tile=5x4:padding=4:margin=4",
         "-frames:v", "1", str(checks / "hook_0_10.jpg")])


def validate(variant: Variant, final: Path, timeline: list[dict[str, Any]], total_frames: int, checks: Path) -> dict[str, Any]:
    info = probe(final)
    video = next(stream for stream in info["streams"] if stream["codec_type"] == "video")
    audio = next(stream for stream in info["streams"] if stream["codec_type"] == "audio")
    duration = float(info["format"]["duration"])
    raw_duration = total_frames / FPS
    evidence_ratio = sum(item.duration for item in variant.evidence) / raw_duration
    source_seconds = sum(item["frames"] / FPS for item in timeline if item["kind"] == "source")
    first_evidence = min(item.start for item in variant.evidence) / POST_SPEED
    assertions = {
        "resolution": video["width"] == WIDTH and video["height"] == HEIGHT,
        "video_codec": video["codec_name"] == "h264",
        "pixel_format": video["pix_fmt"] == "yuv420p",
        "frame_rate": video["r_frame_rate"] == "30/1",
        "audio_codec": audio["codec_name"] == "aac",
        "audio_sample_rate": audio["sample_rate"] == "48000",
        "audio_channels": audio["channels"] == 2,
        "duration": variant.target_min <= duration <= variant.target_max,
        "evidence_ratio": 0.25 <= evidence_ratio <= 0.30,
        "first_evidence_after_10": first_evidence >= 10.0,
        "source_usage": source_seconds / SOURCE_DURATION <= 0.50,
        "source_clips_under_15": all((item["frames"] / FPS) < 15.0 for item in timeline if item["kind"] == "source"),
        "expected_tts_bridges": sum(item["kind"] == "tts" for item in timeline) == variant.expected_tts_bridges,
    }
    failed = [name for name, passed in assertions.items() if not passed]
    if failed:
        raise AssertionError(f"validation failed: {failed}")
    run(["ffmpeg", "-v", "error", "-i", str(final), "-f", "null", "-"])
    report = {
        "output": str(final), "duration": duration, "resolution": f"{video['width']}x{video['height']}",
        "video_codec": video["codec_name"], "pixel_format": video["pix_fmt"], "frame_rate": video["r_frame_rate"],
        "audio_codec": audio["codec_name"], "audio_sample_rate": audio["sample_rate"], "audio_channels": audio["channels"],
        "raw_duration": raw_duration, "post_speed": POST_SPEED, "evidence_usage_percent": round(evidence_ratio * 100, 2),
        "source_usage_percent_of_long_source": round(source_seconds / SOURCE_DURATION * 100, 2),
        "first_fullscreen_evidence_final_time": round(first_evidence, 3), "decode_check": "passed", "assertions": assertions,
    }
    checks.joinpath("validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    checks.joinpath("timeline.json").write_text(json.dumps(timeline, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


def require_inputs(variant: Variant) -> None:
    required = [SOURCE, FONT_REGULAR, FONT_BOLD]
    required.extend(Path(item.asset) for item in variant.evidence if item.kind == "video")
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("missing inputs:\n" + "\n".join(missing))
    for segment in variant.segments:
        if segment.kind == "source" and segment.source_end - segment.source_start >= 15:
            raise ValueError(f"source clip reaches 15 seconds: {segment.name}")
        if segment.kind == "tts":
            ensure_tts(segment)


def render_variant(variant: Variant) -> None:
    work = PROJECT / "clips" / f"{variant.version}_work"
    panels = work / "panels"
    checks = work / "checks"
    final = PROJECT / "final" / variant.final_name
    for directory in (work, panels, checks, final.parent):
        directory.mkdir(parents=True, exist_ok=True)
    require_inputs(variant)
    make_panels(panels)
    base, timeline, total_frames = build_base(variant, work)
    raw_duration = total_frames / FPS
    with_evidence = composite_evidence(variant, base, panels, work, total_frames)
    subtitles = make_subtitles(variant, timeline, work, raw_duration)
    music, impact = generate_audio_assets(work, raw_duration)
    raw_mix = mix_and_caption(with_evidence, subtitles, music, impact, work, raw_duration, variant)
    finish(raw_mix, final, variant.tail_pad)
    extract_checks(final, checks)
    validate(variant, final, timeline, total_frames, checks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=("a", "b", "r", "c", "all"), default="all")
    args = parser.parse_args()
    selected = ("a", "b") if args.variant == "all" else (args.variant,)
    for key in selected:
        render_variant(VARIANTS[key])


if __name__ == "__main__":
    main()
