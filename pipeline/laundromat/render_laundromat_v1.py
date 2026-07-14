#!/usr/bin/env python3
"""Render the laundromat_v1 Decision-Lock finance Short.

The edit keeps CNBC's original voice, replaces static source infographics with
moving source/Pexels footage, and makes the viewer's SMART/RECKLESS decision the
retention engine. No TTS is generated.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageFont

FPS = 30
WIDTH = 1080
HEIGHT = 1920
TOTAL_FRAMES = 1500
TOTAL_DURATION = TOTAL_FRAMES / FPS
REQUIRED_DIALOGUE_WINDOWS = [
    (20.88, 25.00, -24.0),
    (43.02, 49.60, -24.0),
]

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output/projects/laundromat"
SOURCE = PROJECT / "source/Z1YZxX-fBwQ.mp4"
PEXELS = {
    "books": PROJECT / "source/pexels/books_finance_7710748.mp4",
    "contract": PROJECT / "source/pexels/contract_signing_7981954.mp4",
    "house": PROJECT / "source/pexels/real_estate_37694695.mp4",
    "hook_owner": PROJECT / "source/pexels/business_owner_packing_7288127.mp4",
    "hook_money": PROJECT / "source/pexels/woman_counting_money_13736697.mp4",
}
WORK = PROJECT / "clips/v1_work"
CLIPS = WORK / "timeline"
CHECKS = WORK / "checks"
AUDIO = WORK / "audio"
SCRIPT = PROJECT / "scripts/script.md"
FINAL = PROJECT / "final/2026-07-14-laundromat_v1_decision_lock.mp4"
FONT = "/System/Library/Fonts/HelveticaNeue.ttc"
FONT_DIR = "/System/Library/Fonts"


@dataclass(frozen=True)
class Financials:
    home_sale: int = 310_000
    home_equity: int = 150_000
    savings: int = 50_000
    seller_financing: int = 100_000
    purchase_price: int = 300_000
    revenue: int = 475_000
    profit: int = 119_000
    owner_pay: int = 66_000
    owner_hours_low: int = 5
    owner_hours_high: int = 6
    employees: int = 6


@dataclass(frozen=True)
class TimelineClip:
    name: str
    start_frame: int
    end_frame: int
    is_source_footage: bool

    @property
    def frames(self) -> int:
        return self.end_frame - self.start_frame


@dataclass(frozen=True)
class VisualRecipe:
    kind: str
    source_start: float = 0.0
    focus: float = 0.5
    pexels_key: str = ""
    pexels_start: float = 0.0


@dataclass(frozen=True)
class AudioPiece:
    name: str
    source_start: float
    source_end: float
    output_start: float
    evidence: str

    @property
    def duration(self) -> float:
        return self.source_end - self.source_start


# Any frame containing CNBC footage counts as source footage, including the
# two partial Pexels inserts in the first ten seconds. Moving Pexels replaces
# the old freeze-frame hook, reducing source footage to 44.4%.
TIMELINE = [
    TimelineClip("hook_face_a", 0, 24, False),
    TimelineClip("hook_face_b", 24, 51, False),
    TimelineClip("hook_face_c", 51, 84, False),
    TimelineClip("bet_owner", 84, 165, True),
    TimelineClip("bet_house_split", 165, 225, True),
    TimelineClip("price_contract_split", 225, 300, True),
    TimelineClip("price_contract", 300, 345, False),
    TimelineClip("revenue", 345, 510, True),
    TimelineClip("profit_waterfall", 510, 690, False),
    TimelineClip("owner_pay", 690, 810, True),
    TimelineClip("owner_pay_broll", 810, 885, False),
    TimelineClip("hours_now", 885, 1050, True),
    TimelineClip("systems", 1050, 1155, False),
    TimelineClip("verdict", 1155, 1380, False),
    TimelineClip("semantic_loop", 1380, 1500, False),
]

VISUAL_RECIPES = {
    "hook_face_a": VisualRecipe("pexels", pexels_key="hook_owner", pexels_start=0.00),
    "hook_face_b": VisualRecipe("pexels", pexels_key="hook_owner", pexels_start=0.80),
    "hook_face_c": VisualRecipe("pexels", pexels_key="hook_money", pexels_start=0.00),
    "bet_owner": VisualRecipe("source", source_start=6.80, focus=0.50),
    "bet_house_split": VisualRecipe(
        "split", source_start=12.00, focus=0.50, pexels_key="house", pexels_start=1.0
    ),
    "price_contract_split": VisualRecipe(
        "split", source_start=14.00, focus=0.50, pexels_key="contract", pexels_start=1.0
    ),
    "price_contract": VisualRecipe("pexels", pexels_key="contract", pexels_start=3.5),
    "revenue": VisualRecipe("source", source_start=50.00, focus=0.50),
    "profit_waterfall": VisualRecipe("pexels", pexels_key="books", pexels_start=1.0),
    "owner_pay": VisualRecipe("source", source_start=270.00, focus=0.50),
    "owner_pay_broll": VisualRecipe("pexels", pexels_key="books", pexels_start=7.0),
    "hours_now": VisualRecipe("source", source_start=236.08, focus=0.50),
    "systems": VisualRecipe("pexels", pexels_key="contract", pexels_start=5.0),
    "verdict": VisualRecipe("pexels", pexels_key="books", pexels_start=4.0),
    "semantic_loop": VisualRecipe("pexels", pexels_key="house", pexels_start=2.0),
}

AUDIO_PIECES = [
    AudioPiece("sale", 176.80, 179.38, 0.00, "sold home for $310K"),
    AudioPiece("equity", 182.16, 190.94, 2.58, "$150K equity went toward laundromat down payment"),
    AudioPiece("finance", 198.00, 203.86, 11.36, "$100K seller financing at 6%"),
    AudioPiece("revenue", 18.82, 22.48, 17.22, "$475K 2024 revenue"),
    AudioPiece(
        "profit_context",
        398.30,
        402.42,
        20.88,
        "takes a small percentage and reinvests it in the laundromat",
    ),
    AudioPiece("owner_pay", 438.56, 443.58, 25.00, "$66K 2024 owner pay"),
    AudioPiece("hours", 235.76, 244.08, 30.02, "5-6 hours now; not true five years ago"),
    AudioPiece(
        "systems",
        249.00,
        260.26,
        38.34,
        "employees and systems remove her from operations to focus on growth",
    ),
]


def financial_summary(values: Financials) -> dict[str, float | int]:
    result = asdict(values)
    result["cash_at_risk"] = values.home_equity + values.savings
    result["profit_margin"] = values.profit / values.revenue
    return result


def source_share(clips: list[TimelineClip]) -> float:
    total = sum(clip.frames for clip in clips)
    source = sum(clip.frames for clip in clips if clip.is_source_footage)
    if total <= 0:
        raise ValueError("timeline has no frames")
    return source / total


def validate_timeline(clips: list[TimelineClip], total_frames: int) -> None:
    if not clips or clips[0].start_frame != 0 or clips[-1].end_frame != total_frames:
        raise ValueError("timeline does not cover the complete output")
    for left, right in zip(clips, clips[1:]):
        if left.end_frame != right.start_frame:
            raise ValueError("timeline gap or overlap")
    for clip in clips:
        if clip.frames <= 0:
            raise ValueError(f"non-positive clip: {clip.name}")
        if clip.is_source_footage and clip.frames >= 15 * FPS:
            raise ValueError(f"source clip reaches 15 seconds: {clip.name}")
    if source_share(clips) > 0.50:
        raise ValueError("source share exceeds 50 percent")


def run(command: list[str], timeout: int = 300) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        rendered = " ".join(command)
        raise RuntimeError(
            f"Command failed ({result.returncode}): {rendered}\n"
            f"stdout:\n{result.stdout[-2000:]}\n"
            f"stderr:\n{result.stderr[-4000:]}"
        )
    return result


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
        timeout=60,
    )
    return json.loads(result.stdout)


def probe_duration(path: Path) -> float:
    return float(probe(path)["format"]["duration"])


def require_inputs() -> None:
    required = [SOURCE, Path(FONT), *PEXELS.values()]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required inputs: {missing}")
    for directory in (CLIPS, CHECKS, AUDIO, FINAL.parent, SCRIPT.parent):
        directory.mkdir(parents=True, exist_ok=True)


def encode_video_args() -> list[str]:
    return [
        "-c:v",
        "libx264",
        "-profile:v",
        "high",
        "-crf",
        "15",
        "-preset",
        "fast",
        "-pix_fmt",
        "yuv420p",
        "-r",
        str(FPS),
        "-video_track_timescale",
        "90000",
    ]


def source_filter(focus: float) -> str:
    return (
        "scale=-2:1920:flags=lanczos,"
        f"crop=1080:1920:(in_w-1080)*{focus:.4f}:0,"
        "fps=30,setsar=1,format=yuv420p"
    )


def pexels_filter(width: int = WIDTH, height: int = HEIGHT) -> str:
    return (
        f"scale={width}:{height}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={width}:{height},fps=30,setsar=1,format=yuv420p"
    )


def render_source_clip(clip: TimelineClip, recipe: VisualRecipe, output: Path) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-ss",
            f"{recipe.source_start:.3f}",
            "-i",
            str(SOURCE),
            "-vf",
            source_filter(recipe.focus),
            "-frames:v",
            str(clip.frames),
            "-an",
            *encode_video_args(),
            str(output),
        ]
    )


def render_freeze_clip(clip: TimelineClip, recipe: VisualRecipe, output: Path) -> None:
    freeze_filter = (
        f"{source_filter(recipe.focus)},"
        "zoompan=z='min(zoom+0.001,1.025)':"
        "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={clip.frames}:s={WIDTH}x{HEIGHT}:fps={FPS},setsar=1"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-ss",
            f"{recipe.source_start:.3f}",
            "-i",
            str(SOURCE),
            "-vf",
            freeze_filter,
            "-frames:v",
            str(clip.frames),
            "-an",
            *encode_video_args(),
            str(output),
        ]
    )


def render_pexels_clip(clip: TimelineClip, recipe: VisualRecipe, output: Path) -> None:
    asset = PEXELS[recipe.pexels_key]
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-ss",
            f"{recipe.pexels_start:.3f}",
            "-i",
            str(asset),
            "-vf",
            pexels_filter(),
            "-frames:v",
            str(clip.frames),
            "-an",
            *encode_video_args(),
            str(output),
        ]
    )


def render_split_clip(clip: TimelineClip, recipe: VisualRecipe, output: Path) -> None:
    asset = PEXELS[recipe.pexels_key]
    graph = (
        f"[0:v]{source_filter(recipe.focus)}[base];"
        f"[1:v]{pexels_filter(340, 620)}[insert];"
        "[base]drawbox=x=670:y=835:w=390:h=690:color=white@0.92:t=fill[framed];"
        "[framed][insert]overlay=x='W-w-55':y='870':shortest=1[outv]"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-ss",
            f"{recipe.source_start:.3f}",
            "-i",
            str(SOURCE),
            "-ss",
            f"{recipe.pexels_start:.3f}",
            "-i",
            str(asset),
            "-filter_complex",
            graph,
            "-map",
            "[outv]",
            "-frames:v",
            str(clip.frames),
            "-an",
            *encode_video_args(),
            str(output),
        ]
    )


def render_visual_timeline() -> list[Path]:
    validate_timeline(TIMELINE, TOTAL_FRAMES)
    outputs: list[Path] = []
    for index, clip in enumerate(TIMELINE):
        recipe = VISUAL_RECIPES[clip.name]
        output = CLIPS / f"{index:02d}_{clip.name}.mp4"
        if recipe.kind == "freeze":
            render_freeze_clip(clip, recipe, output)
        elif recipe.kind == "source":
            render_source_clip(clip, recipe, output)
        elif recipe.kind == "pexels":
            render_pexels_clip(clip, recipe, output)
        elif recipe.kind == "split":
            render_split_clip(clip, recipe, output)
        else:
            raise ValueError(f"Unknown visual recipe kind: {recipe.kind}")
        outputs.append(output)
    return outputs


def concat_visual_timeline(clips: list[Path]) -> Path:
    concat_file = WORK / "timeline.txt"
    concat_file.write_text(
        "".join(f"file '{clip.resolve()}'\n" for clip in clips), encoding="utf-8"
    )
    base = WORK / "base_video.mp4"
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
            str(concat_file),
            "-c",
            "copy",
            "-an",
            str(base),
        ]
    )
    return base


def ass_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remainder = seconds % 60
    return f"{hours}:{minutes:02d}:{remainder:05.2f}"


def make_subtitles() -> Path:
    path = WORK / "captions.ass"
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,Helvetica Neue,82,&H00FFFFFF,&H000000FF,&H00101924,&H88000000,-1,0,0,0,100,100,0,0,1,7,2,8,60,60,150,1
Style: Dialogue,Helvetica Neue,62,&H00FFFFFF,&H000000FF,&H00101924,&H88000000,-1,0,0,0,100,100,0,0,1,6,2,2,65,65,185,1
Style: Final,Helvetica Neue,74,&H00FFFFFF,&H000000FF,&H00101924,&H88000000,-1,0,0,0,100,100,0,0,1,7,2,5,70,70,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = [
        (0.00, 0.80, "Hook", "SHE SOLD HER HOUSE"),
        (0.80, 1.70, "Hook", "{\\c&H0047D4FF&}FOR $310,000"),
        (1.70, 2.80, "Hook", "TO BUY {\\c&H0047D4FF&}THIS."),
        (2.80, 4.20, "Hook", "{\\c&H003B5AFF&}SMART OR RECKLESS?"),
        (4.20, 5.50, "Hook", "LOCK YOUR ANSWER"),
        (2.58, 4.40, "Dialogue", "I TOOK HOME {\\c&H0047D4FF&}$150,000"),
        (4.40, 6.20, "Dialogue", "OF THE $310K"),
        (6.20, 8.20, "Dialogue", "PAID OFF THE HOME LOAN"),
        (8.20, 11.36, "Dialogue", "PUT $150K TOWARD THE LAUNDROMAT"),
        (11.36, 13.20, "Dialogue", "SELLER FINANCED {\\c&H0047D4FF&}$100K"),
        (13.20, 17.22, "Dialogue", "AT {\\c&H0047D4FF&}6% OVER TWO YEARS"),
        (17.22, 20.88, "Dialogue", "{\\c&H0047E67C&}$475K IN 2024"),
        (20.88, 22.20, "Dialogue", "WHATEVER I MAKE ON THE LAUNDROMAT"),
        (22.20, 23.60, "Dialogue", "I TAKE A SMALL PERCENTAGE"),
        (23.60, 25.00, "Dialogue", "AND PUT IT BACK INTO THE LAUNDROMAT"),
        (25.00, 27.20, "Dialogue", "IN 2024"),
        (27.20, 30.02, "Dialogue", "I PAID MYSELF {\\c&H0047E67C&}$66K"),
        (30.02, 33.00, "Dialogue", "{\\c&H0047E67C&}5-6 HOURS A WEEK NOW"),
        (33.00, 35.20, "Dialogue", "I'M HESITANT TO TELL PEOPLE THAT"),
        (35.20, 38.34, "Dialogue", "NOT HOW IT WAS FIVE YEARS AGO"),
        (38.34, 40.20, "Dialogue", "{\\c&H0047E67C&}HIRED EMPLOYEES"),
        (40.20, 42.20, "Dialogue", "INCORPORATED MORE SYSTEMS"),
        (42.20, 44.20, "Dialogue", "TO REMOVE ME FROM THE BUSINESS"),
        (44.20, 46.40, "Dialogue", "SO I CAN FOCUS ON GROWING IT"),
        (46.40, 49.60, "Dialogue", "NOT WORKING IN THE BUSINESS"),
        (43.02, 45.20, "Final", "{\\c&H0047E67C&}SMART."),
        (45.20, 47.60, "Final", "BECAUSE SHE BUILT SYSTEMS."),
        (47.60, 50.00, "Final", "NOT BECAUSE OF $475K REVENUE."),
    ]
    lines = [header]
    for start, end, style, text in events:
        lines.append(
            f"Dialogue: 0,{ass_time(start)},{ass_time(end)},{style},,0,0,0,,{text}\n"
        )
    path.write_text("".join(lines), encoding="utf-8")
    return path


def escape_drawtext(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "’")
    )


def drawtext(
    text: str,
    *,
    y: int,
    size: int,
    color: str,
    start: float,
    end: float,
    x: str = "(w-text_w)/2",
    box: bool = True,
) -> str:
    parts = [
        f"drawtext=text='{escape_drawtext(text)}'",
        f"fontfile='{FONT}'",
        f"fontsize={size}",
        f"fontcolor={color}",
        "borderw=5",
        "bordercolor=black@0.95",
        f"x={x}",
        f"y={y}",
        "expansion=none",
        f"enable='between(t,{start:.2f},{end:.2f})'",
    ]
    if box:
        parts.extend(["box=1", "boxcolor=black@0.58", "boxborderw=18"])
    return ":".join(parts)


def assert_overlay_text_fits() -> None:
    specs = [
        ("CASH AT RISK $200K", 66),
        ("PURCHASE PRICE $300K", 66),
        ("SELLER FINANCE $100K @ 6%", 58),
        ("$475K REVENUE", 86),
        ("$119K PROFIT", 86),
        ("CALCULATED: 25% MARGIN", 64),
        ("$66K OWNER PAY", 84),
        ("5-6 HOURS/WEEK NOW", 70),
        ("NOT TRUE 5 YEARS AGO", 64),
        ("EMPLOYEES + SYSTEMS", 62),
    ]
    for text, size in specs:
        font = ImageFont.truetype(FONT, size=size, index=0)
        width = font.getlength(text)
        if width > 920:
            raise ValueError(f"Overlay text too wide ({width:.1f}px): {text}")


def make_overlay_video(base: Path, subtitles: Path) -> Path:
    assert_overlay_text_fits()
    filters = [
        "drawbox=x=0:y=0:w=iw:h=ih:color=black@0.08:t=fill",
        "drawbox=x=0:y=ih-7:w=iw*(t/50):h=7:color=0x47D4FF:t=fill",
        "drawbox=x=70:y=1370:w=940:h=112:color=black@0.68:t=fill:enable='between(t,1.2,43.02)'",
        "drawbox=x=105:y=1440:w=870:h=10:color=white@0.40:t=fill:enable='between(t,1.2,43.02)'",
        drawtext("RECKLESS", y=1385, size=32, color="0xFF5A3B", start=1.2, end=43.02, x="105", box=False),
        drawtext("SMART", y=1385, size=32, color="0x7CE647", start=1.2, end=43.02, x="w-text_w-105", box=False),
    ]
    for start, end, x, color in (
        (1.20, 11.36, 360, "0xFF5A3B"),
        (11.36, 17.22, 460, "0xFFD447"),
        (17.22, 20.88, 760, "0x7CE647"),
        (20.88, 25.00, 540, "0x47D4FF"),
        (25.00, 43.02, 710, "0x7CE647"),
    ):
        filters.append(
            f"drawbox=x={x}:y=1423:w=26:h=44:color={color}:t=fill:"
            f"enable='between(t,{start:.2f},{end:.2f})'"
        )

    filters.extend(
        [
            drawtext("CASH AT RISK $200K", y=210, size=66, color="0xFFD447", start=5.50, end=8.20),
            drawtext("PURCHASE PRICE $300K", y=210, size=66, color="white", start=8.20, end=11.36),
            drawtext("SELLER FINANCE $100K @ 6%", y=210, size=58, color="0xFFD447", start=11.36, end=17.22),
            drawtext("$475K REVENUE", y=210, size=86, color="0x7CE647", start=17.22, end=20.88),
            "drawbox=x=100:y=590:w=880:h=84:color=0x47D4FF@0.72:t=fill:enable='between(t,20.88,25.00)'",
            "drawbox=x=100:y=720:w=220:h=84:color=0x7CE647@0.82:t=fill:enable='between(t,20.88,25.00)'",
            drawtext("$119K PROFIT", y=430, size=86, color="0x7CE647", start=20.88, end=22.80),
            drawtext("CALCULATED: 25% MARGIN", y=430, size=64, color="0xFFD447", start=22.80, end=25.00),
            drawtext("$66K OWNER PAY", y=210, size=84, color="0x7CE647", start=25.00, end=30.02),
            drawtext("5-6 HOURS/WEEK NOW", y=210, size=70, color="0x7CE647", start=30.02, end=35.20),
            drawtext("NOT TRUE 5 YEARS AGO", y=210, size=64, color="0xFFD447", start=35.20, end=38.34),
            drawtext("EMPLOYEES + SYSTEMS", y=210, size=62, color="0x7CE647", start=38.34, end=43.02),
            drawtext("SOURCE: CNBC MAKE IT | 2024 FIGURES", y=80, size=28, color="white@0.85", start=17.22, end=30.02, x="w-text_w-50", box=False),
            f"subtitles='{subtitles}':fontsdir='{FONT_DIR}'",
        ]
    )
    output = WORK / "overlay_video.mp4"
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(base),
            "-vf",
            ",".join(filters),
            "-frames:v",
            str(TOTAL_FRAMES),
            "-an",
            *encode_video_args(),
            str(output),
        ],
        timeout=600,
    )
    return output


def volume_stats_db(
    path: Path, start: float = 0.0, duration: float | None = None
) -> tuple[float, float]:
    command = [
        "ffmpeg",
        "-hide_banner",
        "-nostats",
        "-ss",
        f"{start:.3f}",
        "-i",
        str(path),
    ]
    if duration is not None:
        command.extend(["-t", f"{duration:.3f}"])
    command.extend(["-vn", "-af", "volumedetect", "-f", "null", "-"])
    result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"volumedetect failed for {path}: {result.stderr[-2000:]}")
    mean_match = re.search(r"mean_volume: ([\-\d.]+) dB", result.stderr)
    max_match = re.search(r"max_volume: ([\-\d.]+) dB", result.stderr)
    if not mean_match or not max_match:
        raise RuntimeError(f"No volume result for {path}")
    return float(mean_match.group(1)), float(max_match.group(1))


def max_volume_db(path: Path, start: float = 0.0, duration: float | None = None) -> float:
    return volume_stats_db(path, start=start, duration=duration)[1]


def extract_audio_pieces() -> list[Path]:
    outputs: list[Path] = []
    for piece in AUDIO_PIECES:
        output = AUDIO / f"{piece.name}.wav"
        fade_out = max(0.0, piece.duration - 0.04)
        audio_filter = (
            "asetpts=PTS-STARTPTS,highpass=f=65,"
            "loudnorm=I=-16:TP=-1.5:LRA=9,"
            "afade=t=in:st=0:d=0.025,"
            f"afade=t=out:st={fade_out:.4f}:d=0.04,"
            "aresample=48000,aformat=channel_layouts=stereo,"
            f"apad=whole_dur={piece.duration:.4f},atrim=0:{piece.duration:.4f}"
        )
        run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-ss",
                f"{piece.source_start:.3f}",
                "-i",
                str(SOURCE),
                "-t",
                f"{piece.duration:.4f}",
                "-vn",
                "-af",
                audio_filter,
                "-ar",
                "48000",
                "-ac",
                "2",
                "-c:a",
                "pcm_s16le",
                str(output),
            ]
        )
        if max_volume_db(output) <= -40.0:
            raise RuntimeError(f"Extracted source audio is silent: {piece.name}")
        outputs.append(output)
    return outputs


def generate_music_and_sfx() -> tuple[Path, Path]:
    music = AUDIO / "music_bed.wav"
    sfx = AUDIO / "impact.wav"
    source = (
        "aevalsrc=(0.10*sin(2*PI*55*t)*(0.30+0.70*exp(-7*mod(t\\,0.5)))+"
        "0.025*sin(2*PI*110*t)+0.012*sin(2*PI*220*t))*"
        f"min(1\\,t/0.8)*min(1\\,({TOTAL_DURATION:.4f}-t)/0.8):"
        f"s=48000:d={TOTAL_DURATION:.4f}"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            source,
            "-af",
            "lowpass=f=1200,highpass=f=35",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "pcm_s16le",
            str(music),
        ]
    )
    impact_source = (
        "aevalsrc=(0.28*sin(2*PI*(150-90*t)*t)+"
        "0.10*sin(2*PI*420*t))*exp(-10*t):s=48000:d=0.45"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            impact_source,
            "-af",
            "lowpass=f=1800",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "pcm_s16le",
            str(sfx),
        ]
    )
    return music, sfx


def music_volume_expression() -> str:
    return "volume='if(gte(t,49.60),1.00,0.035)':eval=frame"


def mix_and_finish(
    overlay_video: Path,
    source_audio: list[Path],
    music: Path,
    sfx: Path,
) -> None:
    inputs = ["-i", str(overlay_video), "-i", str(music)]
    for path in source_audio:
        inputs.extend(["-i", str(path)])
    sfx_index = 2 + len(source_audio)
    inputs.extend(["-i", str(sfx)])

    lines = [
        "[1:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"{music_volume_expression()}[music]"
    ]
    mix_labels = ["[music]"]
    for index, piece in enumerate(AUDIO_PIECES, start=2):
        delay = round(piece.output_start * 1000)
        label = f"voice{index}"
        lines.append(
            f"[{index}:a]aresample=48000,aformat=channel_layouts=stereo,"
            f"adelay={delay}|{delay},volume=1.0[{label}]"
        )
        mix_labels.append(f"[{label}]")

    impact_times = [0.00, 17.22, 20.88, 25.00, 43.02, 49.60]
    split_labels = "".join(f"[impact{i}]" for i in range(len(impact_times)))
    lines.append(
        f"[{sfx_index}:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"asplit={len(impact_times)}{split_labels}"
    )
    for index, timestamp in enumerate(impact_times):
        delay = round(timestamp * 1000)
        label = f"hit{index}"
        lines.append(
            f"[impact{index}]adelay={delay}|{delay},volume=0.18[{label}]"
        )
        mix_labels.append(f"[{label}]")

    lines.append(
        "".join(mix_labels)
        + f"amix=inputs={len(mix_labels)}:duration=longest:normalize=0,"
        + "alimiter=limit=0.94:attack=5:release=50,"
        + "loudnorm=I=-14:TP=-1.0:LRA=9,"
        + f"atrim=0:{TOTAL_DURATION:.4f}[aout]"
    )
    filter_script = WORK / "audio_mix.ffscript"
    filter_script.write_text(";\n".join(lines) + "\n", encoding="utf-8")

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
            "-frames:v",
            str(TOTAL_FRAMES),
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
            str(FINAL),
        ],
        timeout=600,
    )


def write_script_document() -> None:
    visual_rows = []
    for clip in TIMELINE:
        recipe = VISUAL_RECIPES[clip.name]
        start = clip.start_frame / FPS
        end = clip.end_frame / FPS
        detail = recipe.kind
        if recipe.kind in {"freeze", "source", "split"}:
            detail += f"; CNBC @{recipe.source_start:.2f}s"
        if recipe.pexels_key:
            detail += f"; Pexels {recipe.pexels_key} @{recipe.pexels_start:.2f}s"
        visual_rows.append(
            f"| `{clip.name}` | {start:.2f}–{end:.2f}s | {clip.frames} | "
            f"{'yes' if clip.is_source_footage else 'no'} | {detail} |"
        )
    audio_rows = [
        f"| `{piece.name}` | {piece.output_start:.2f}–"
        f"{piece.output_start + piece.duration:.2f}s | "
        f"{piece.source_start:.2f}–{piece.source_end:.2f}s | {piece.evidence} |"
        for piece in AUDIO_PIECES
    ]
    content = f"""# laundromat_v1 — Decision-Lock script

**Render:** `2026-07-14-laundromat_v1_decision_lock.mp4`
**Duration:** {TOTAL_DURATION:.2f}s / {TOTAL_FRAMES} frames @ {FPS}fps
**Source visual share:** {source_share(TIMELINE) * 100:.1f}%
**Audio:** CNBC verbatim quotes; no TTS

## Viewer promise

The viewer must decide whether selling a home to buy a laundromat was SMART or
RECKLESS before seeing the acquisition price, revenue, profit, owner pay, and
owner-time evidence.

## Narrative beats

| Time | Beat | Evidence/value |
|---:|---|---|
| 0.00–2.58s | Decision lock | Sold home for $310K; SMART or RECKLESS? |
| 2.58–11.36s | Capital at risk | $150K home equity went toward the laundromat; acquisition ledger remains visible |
| 11.36–17.22s | Financing | $100K seller financing at 6% over two years |
| 17.22–25.00s | Revenue vs profit | $475K revenue; CNBC-reported $119K profit; calculated 25.05% margin |
| 25.00–30.02s | Owner outcome | $66K paid to owner in 2024 |
| 30.02–38.34s | Time qualification | 5–6 hours/week now, explicitly not true five years ago |
| 38.34–49.60s | Systems payoff + verdict | Employees/systems remove the owner from operations; SMART because of systems, not headline revenue |
| 49.60–50.00s | Audio tail | Impact/music resolves the final beat |

## Visual timeline

| Clip | Output range | Frames | Counts as source | Recipe |
|---|---:|---:|---|---|
{chr(10).join(visual_rows)}

## Audio timeline

| Piece | Output range | CNBC source range | Evidence |
|---|---:|---:|---|
{chr(10).join(audio_rows)}

## Transformative Gate

1. Commentary: self-authored Decision-Lock framing, verdict, and decision rule.
2. Value-adds: acquisition ledger, revenue/profit waterfall, source citation,
   persistent decision meter, time qualification, and final decision checklist.
3. Source visual use: {source_share(TIMELINE) * 100:.1f}% of frames; every source
   visual clip is shorter than 15 seconds.
4. Three-source mix: CNBC footage + animated overlays + five Pexels library clips.

## Financial language guardrail

`$475K revenue`, `$119K business profit`, and `$66K owner pay` remain separate
concepts. The 25% margin is explicitly derived from CNBC's reported figures and
is not presented as Cami's spoken quote.
"""
    SCRIPT.write_text(content, encoding="utf-8")


def extract_checks() -> None:
    timestamps = [
        0.0, 0.2, 0.6, 1.0, 1.5, 2.0, 2.8, 4.0, 5.0, 7.0, 9.5,
        12.0, 16.5, 19.5, 23.5, 26.5, 30.5, 35.0, 39.0, 42.0, 45.0, 48.8,
    ]
    for index, timestamp in enumerate(timestamps):
        output = CHECKS / f"{index:02d}_{timestamp:05.2f}.jpg"
        run(
            [
                "ffmpeg", "-y", "-v", "error", "-ss", f"{timestamp:.2f}",
                "-i", str(FINAL), "-frames:v", "1", "-q:v", "2", str(output),
            ],
            timeout=60,
        )
    run(
        [
            "ffmpeg", "-y", "-v", "error", "-i", str(FINAL), "-vf",
            "fps=1/2.5,"
            "drawtext=fontfile='/System/Library/Fonts/HelveticaNeue.ttc':"
            "text='%{pts\\:hms}':x=10:y=10:fontsize=34:fontcolor=yellow:"
            "borderw=3:bordercolor=black,scale=270:-2:flags=lanczos,"
            "tile=5x4:padding=4:margin=4",
            "-frames:v", "1", str(CHECKS / "contact.jpg"),
        ],
        timeout=180,
    )
    hook_files = sorted(CHECKS.glob("0[0-8]_*.jpg"))
    hook_sheet = Image.new("RGB", (360 * 3, 640 * 3), (15, 15, 15))
    for index, path in enumerate(hook_files):
        image = Image.open(path).convert("RGB").resize(
            (360, 640), Image.Resampling.LANCZOS
        )
        hook_sheet.paste(image, ((index % 3) * 360, (index // 3) * 640))
    hook_sheet.save(CHECKS / "hook-contact.jpg", quality=92)


def measure_loudness(path: Path) -> tuple[float, float]:
    result = subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
            "-filter_complex", "ebur128=peak=true", "-f", "null", "-",
        ],
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ebur128 failed: {result.stderr[-2000:]}")
    integrated = re.findall(r"I:\s+(-?[\d.]+) LUFS", result.stderr)
    peaks = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", result.stderr)
    if not integrated or not peaks:
        raise RuntimeError("Could not parse ebur128 summary")
    return float(integrated[-1]), float(peaks[-1])


def unique_color_count(path: Path, timestamp: float = 15.0) -> int:
    frame = CHECKS / "color-check.png"
    run(
        [
            "ffmpeg", "-y", "-v", "error", "-ss", f"{timestamp:.2f}",
            "-i", str(path), "-frames:v", "1", str(frame),
        ],
        timeout=60,
    )
    colors = Image.open(frame).convert("RGB").getcolors(maxcolors=WIDTH * HEIGHT)
    return WIDTH * HEIGHT if colors is None else len(colors)


def validate_final() -> dict[str, Any]:
    info = probe(FINAL)
    videos = [stream for stream in info["streams"] if stream["codec_type"] == "video"]
    audios = [stream for stream in info["streams"] if stream["codec_type"] == "audio"]
    if len(videos) != 1 or len(audios) != 1:
        raise AssertionError(f"Expected one video and one audio stream: {info['streams']}")
    video = videos[0]
    audio = audios[0]
    duration = float(info["format"]["duration"])
    frame_rate = video["r_frame_rate"]
    assertions = {
        "width": video["width"] == WIDTH,
        "height": video["height"] == HEIGHT,
        "video_codec": video["codec_name"] == "h264",
        "pixel_format": video["pix_fmt"] == "yuv420p",
        "frame_rate": frame_rate == "30/1",
        "audio_codec": audio["codec_name"] == "aac",
        "audio_rate": audio["sample_rate"] == "48000",
        "audio_channels": audio["channels"] == 2,
        "duration": 49.90 <= duration <= 50.10,
        "under_60s": duration <= 60.0,
        "source_share": source_share(TIMELINE) <= 0.50,
    }
    failures = [name for name, passed in assertions.items() if not passed]
    if failures:
        raise AssertionError(
            f"Media validation failed: {failures}\n{json.dumps(info, indent=2)}"
        )

    run(["ffmpeg", "-v", "error", "-i", str(FINAL), "-f", "null", "-"], timeout=300)
    integrated_lufs, true_peak = measure_loudness(FINAL)
    if not (-16.0 <= integrated_lufs <= -12.0):
        raise AssertionError(f"Integrated loudness out of range: {integrated_lufs} LUFS")
    if true_peak > -0.5:
        raise AssertionError(f"True peak too high: {true_peak} dBFS")
    colors = unique_color_count(FINAL)
    if colors <= 5000:
        raise AssertionError(f"Text-only/low-visual regression: {colors} unique colors")
    hook_max = max_volume_db(FINAL, start=0.0, duration=3.0)
    if hook_max <= -30.0:
        raise AssertionError(f"Hook audio too quiet: {hook_max} dB")
    required_dialogue_audio = {}
    for start, end, minimum_mean in REQUIRED_DIALOGUE_WINDOWS:
        window_duration = end - start
        mean_volume, max_volume = volume_stats_db(
            FINAL, start=start, duration=window_duration
        )
        label = f"{start:.2f}-{end:.2f}s"
        required_dialogue_audio[label] = {
            "mean_db": mean_volume,
            "max_db": max_volume,
        }
        if mean_volume < minimum_mean:
            raise AssertionError(
                f"Required dialogue too quiet at {label}: "
                f"{mean_volume} dB mean (minimum {minimum_mean} dB)"
            )
    return {
        "output": str(FINAL),
        "duration": duration,
        "resolution": f"{video['width']}x{video['height']}",
        "video_codec": video["codec_name"],
        "pixel_format": video["pix_fmt"],
        "frame_rate": frame_rate,
        "audio_codec": audio["codec_name"],
        "audio_rate": audio["sample_rate"],
        "source_share_percent": source_share(TIMELINE) * 100,
        "integrated_lufs": integrated_lufs,
        "true_peak_dbfs": true_peak,
        "hook_max_db": hook_max,
        "required_dialogue_audio": required_dialogue_audio,
        "unique_colors_at_15s": colors,
        "decode_check": "passed",
    }


def main() -> None:
    require_inputs()
    validate_timeline(TIMELINE, TOTAL_FRAMES)
    shutil.rmtree(CLIPS, ignore_errors=True)
    CLIPS.mkdir(parents=True, exist_ok=True)
    clips = render_visual_timeline()
    base = concat_visual_timeline(clips)
    subtitles = make_subtitles()
    overlay_video = make_overlay_video(base, subtitles)
    source_audio = extract_audio_pieces()
    music, sfx = generate_music_and_sfx()
    mix_and_finish(overlay_video, source_audio, music, sfx)
    write_script_document()
    extract_checks()
    report = validate_final()
    (CHECKS / "validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
