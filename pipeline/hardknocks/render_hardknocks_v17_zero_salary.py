#!/usr/bin/env python3
"""Render HardKnocks V17: The $0 Salary Bet.

Source-native challenge story: Rick Jackson offers to work for zero salary,
buys the firm one year later, and explains the customer-win mechanism.  The
edit deliberately removes TTS and the mid-roll CTA tested in prior videos.

This is a one-off media renderer. Completion is verified against the actual MP4,
not renderer unit tests.
"""

from __future__ import annotations

import json
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "hardknocks"
SOURCE = PROJECT / "source" / "VW2t21zzYl8.mp4"
WORK = PROJECT / "clips" / "v17_zero_salary_work"
SEGMENT_DIR = WORK / "segments"
PANELS = WORK / "panels"
CHECKS = WORK / "checks"
AUDIO_DIR = WORK / "audio"
FINAL = PROJECT / "final" / "2026-07-27-hardknocks_v17_zero_salary_bet_r2_active_speaker.mp4"

PEXELS_CONTRACT = ROOT / "output" / "shared" / "pexels" / "contract_signing_7981954.mp4"
FORBES_SCREENSHOT = PROJECT / "clips" / "v13_billionaire_hunt_work" / "proof_sources" / "forbes_rick_jackson.png"
BRANDING = ROOT / "output" / "shared" / "hardknocks_branding"
TING = BRANDING / "verdict_correct_ting.wav"


FONT_KOMIKA = ROOT / "assets" / "fonts" / "komika-axis" / "KOMIKAX_.ttf"
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
FONT_BLACK = Path("/System/Library/Fonts/Supplemental/Arial Black.ttf")

WIDTH = 1080
HEIGHT = 1920
FPS = 30
POST_SPEED = 1.04
CAPTION_BAND_PX = 270
SEGMENT_FADE_IN = 0.12
SEGMENT_FADE_OUT = 0.20

YELLOW = "#FFD23C"
GREEN = "#00D66E"
RED = "#FF4D4D"
BLUE = "#4FC3F7"
DARK = "#0B0E14"


@dataclass(frozen=True)
class Segment:
    name: str
    source_start: float
    source_end: float
    turns: tuple[tuple[float, float], ...]
    zoom: float
    act: str

    @property
    def duration(self) -> float:
        return self.source_end - self.source_start


SEGMENTS = (
    # Street angle: Rick is frame-left (~35%); host is frame-right (~67%).
    # Reframes stay on the active speaker and land every <=1.35s.
    Segment(
        "hook_zero", 1027.36, 1032.23,
        ((0.0, 0.28), (1.35, 0.34), (2.70, 0.28), (4.05, 0.34)), 1.08, "hook",
    ),
    Segment(
        "origin", 989.50, 994.07,
        ((0.0, 0.75), (1.35, 0.69), (2.18, 0.28), (3.53, 0.34)), 1.04, "context",
    ),
    Segment(
        "hunger", 1010.16, 1013.51,
        ((0.0, 0.28), (1.35, 0.34), (2.70, 0.28)), 1.06, "context",
    ),
    Segment(
        "rejected", 1017.92, 1022.31,
        ((0.0, 0.28), (1.35, 0.34), (2.70, 0.28), (4.05, 0.34)), 1.06, "setup",
    ),
    Segment(
        "salary", 1022.32, 1027.35,
        ((0.0, 0.28), (1.35, 0.34), (2.70, 0.28), (4.05, 0.34)), 1.06, "stake",
    ),
    Segment(
        "bought", 1032.24, 1035.27,
        ((0.0, 0.28), (1.35, 0.34), (2.70, 0.28)), 1.08, "payoff",
    ),
    # Car angle: host is frame-left but turns toward Rick, so the portrait crop
    # must sit farther right than a naive face-centroid crop; Rick is frame-right.
    Segment(
        "companies", 970.60, 975.70,
        ((0.0, 0.32), (1.45, 0.38), (2.92, 0.72), (4.27, 0.66)), 1.05, "escalation",
    ),
    Segment(
        "revenue", 976.16, 985.35,
        ((0.0, 0.32), (1.40, 0.38), (2.80, 0.32),
         (3.68, 0.72), (5.08, 0.66),
         (5.84, 0.32), (6.80, 0.72), (7.35, 0.32), (8.45, 0.72)), 1.05, "proof",
    ),
    Segment(
        "find_win", 1047.52, 1055.00,
        ((0.0, 0.28), (1.35, 0.34), (2.70, 0.28),
         (4.05, 0.34), (5.40, 0.28), (6.75, 0.34)), 1.06, "lesson",
    ),
    Segment(
        "fulfill_need", 1055.00, 1063.11,
        ((0.0, 0.28), (1.35, 0.34), (2.70, 0.28),
         (4.05, 0.34), (5.40, 0.28), (6.75, 0.34)), 1.06, "lesson",
    ),
)


CAPTIONS: dict[str, tuple[tuple[float, float, str, str], ...]] = {
    "hook_zero": (
        (0.00, 1.20, "WORK FOR $0?", "$0"),
        (1.20, 2.38, "NO SALARY", "NO SALARY"),
        (2.38, 3.72, "JUST 33% COMMISSION", "33%"),
        (3.72, 4.87, "WOULD YOU GIVE ME A CHANCE?", "CHANCE"),
    ),
    "origin": (
        (0.00, 1.20, "DID YOU COME", "COME"),
        (1.20, 2.18, "FROM MONEY?", "MONEY"),
        (2.18, 3.28, "NO. THE PROJECTS.", "PROJECTS"),
        (3.28, 4.57, "MOM WAS A WAITRESS", "WAITRESS"),
    ),
    "hunger": (
        (0.00, 1.40, "ABSOLUTELY NOT", "NOT"),
        (1.40, 2.75, "SCRAPING BY", "SCRAPING"),
        (2.75, 3.35, "FOR FOOD", "FOOD"),
    ),
    "rejected": (
        (0.00, 1.35, "I WAS 20", "20"),
        (1.35, 2.75, "THEY WOULDN'T HIRE ME", "WOULDN'T"),
        (2.75, 3.80, "NO DEGREE", "NO DEGREE"),
        (3.80, 4.39, "SO I ASKED", "ASKED"),
    ),
    "salary": (
        (0.00, 1.45, "WHAT WOULD A", "WHAT"),
        (1.45, 2.65, "DEGREE MAKE?", "DEGREE"),
        (2.65, 3.85, "$1,100 A MONTH", "$1,100"),
        (3.85, 5.03, "PLUS COMMISSION", "COMMISSION"),
    ),
    "bought": (
        (0.00, 1.48, "ONE YEAR LATER", "ONE YEAR"),
        (1.48, 2.35, "I BOUGHT", "BOUGHT"),
        (2.35, 3.03, "THE FIRM", "FIRM"),
    ),
    "companies": (
        (0.00, 1.35, "HOW DID YOU", "HOW"),
        (1.35, 2.70, "GET RICH? HEALTHCARE", "HEALTHCARE"),
        (2.70, 3.80, "BUSINESS OWNER?", "OWNER"),
        (3.80, 5.10, "22 COMPANIES", "22"),
    ),
    "revenue": (
        (0.00, 1.40, "YOUR BIGGEST YEAR", "BIGGEST"),
        (1.40, 2.70, "ACROSS 22 COMPANIES?", "22"),
        (2.70, 4.15, "$3 BILLION", "$3 BILLION"),
        (4.15, 5.55, "IN ONE YEAR", "ONE YEAR"),
        (5.78, 6.82, "WITH A B?", "B"),
        (6.82, 7.52, "WITH A B.", "B"),
        (7.52, 8.55, "A BILLIONAIRE?", "BILLIONAIRE"),
        (8.55, 9.19, "YEAH.", "YEAH"),
    ),
    "find_win": (
        (0.00, 1.40, "HAVE EVERYTHING", "EVERYTHING"),
        (1.40, 2.80, "YOU WANT", "WANT"),
        (2.80, 4.20, "HELP PEOPLE GET", "HELP"),
        (4.20, 5.60, "WHAT THEY WANT", "WANT"),
        (5.60, 6.60, "FIND THEIR WIN", "WIN"),
        (6.60, 7.48, "NOT YOUR AGENDA", "NOT"),
    ),
    "fulfill_need": (
        (0.00, 1.40, "ASK WHAT", "ASK"),
        (1.40, 2.80, "THEY NEED", "NEED"),
        (2.80, 4.20, "THEN FULFILL", "FULFILL"),
        (4.20, 5.22, "THAT NEED", "NEED"),
        (5.22, 6.62, "THAT'S THE DEFINITION", "DEFINITION"),
        (6.62, 8.11, "OF GOOD BUSINESS", "GOOD BUSINESS"),
    ),
}


def run(args: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(str(a) for a in args), flush=True)
    return subprocess.run(
        [str(a) for a in args], cwd=ROOT, check=True, text=True,
        capture_output=capture,
    )


def probe(path: Path) -> dict[str, Any]:
    result = run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
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


def vo_loudnorm() -> str:
    return (
        "acompressor=threshold=0.1:ratio=4:attack=5:release=100:makeup=1,"
        "loudnorm=I=-16:TP=-1.5:LRA=10"
    )


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


def scaled_crop(segment: Segment) -> str:
    x_expr = crop_expr(segment.turns)
    zoom_width = round(WIDTH * segment.zoom)
    zoom_height = round(HEIGHT * segment.zoom)
    band_height = HEIGHT - CAPTION_BAND_PX
    recovery_width = round(WIDTH * HEIGHT / band_height)
    return (
        f"scale=3414:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:'{x_expr}':0,"
        f"scale={zoom_width}:{zoom_height}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:(in_w-{WIDTH})/2:0,"
        f"crop={WIDTH}:{band_height}:0:0,"
        f"scale={recovery_width}:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:({recovery_width}-{WIDTH})/2:0,"
        "eq=contrast=1.04:saturation=1.05,setsar=1,format=yuv420p"
    )


def render_segment(segment: Segment, output: Path) -> int:
    if segment.duration >= 15.0:
        raise ValueError(f"Source clip reaches 15 seconds: {segment.name}")
    frame_count = frames_for(segment.duration)
    coarse_start = max(0.0, segment.source_start - 5.0)
    fine_offset = segment.source_start - coarse_start
    audio_filter = (
        f"atrim=start={fine_offset:.6f},asetpts=PTS-STARTPTS,highpass=f=70,"
        "acompressor=threshold=0.125:ratio=2:attack=5:release=80:makeup=1.4,"
        "loudnorm=I=-16:TP=-1.5:LRA=10,"
        "aresample=48000:first_pts=0,apad,"
        f"atrim=0:{segment.duration:.6f},"
        f"afade=t=in:st=0:d={SEGMENT_FADE_IN:.2f},"
        f"afade=t=out:st={segment.duration - SEGMENT_FADE_OUT:.6f}:d={SEGMENT_FADE_OUT:.2f}"
    )
    run([
        # Hybrid seek: fast coarse jump, then accurate local decode. This avoids
        # both keyframe pre-roll and decoding 17 minutes of 4K source per clip.
        "ffmpeg", "-y", "-v", "error", "-ss", f"{coarse_start:.6f}",
        "-i", str(SOURCE), "-t", f"{segment.duration:.6f}",
        "-vf", f"trim=start={fine_offset:.6f},setpts=PTS-STARTPTS,{scaled_crop(segment)},fps={FPS}",
        "-af", audio_filter, "-frames:v", str(frame_count), *encode_args(),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(output),
    ])
    return frame_count


def build_base() -> tuple[Path, list[dict[str, Any]], int]:
    SEGMENT_DIR.mkdir(parents=True, exist_ok=True)
    cursor = 0
    timeline: list[dict[str, Any]] = []
    outputs: list[Path] = []
    for index, segment in enumerate(SEGMENTS):
        output = SEGMENT_DIR / f"{index:02d}_{segment.name}.mp4"
        count = render_segment(segment, output)
        timeline.append({
            "name": segment.name,
            "act": segment.act,
            "source_start": segment.source_start,
            "source_end": segment.source_end,
            "source_duration": segment.duration,
            "start_frame": cursor,
            "end_frame": cursor + count,
            "frames": count,
            "pre_speed_start": cursor / FPS,
            "pre_speed_end": (cursor + count) / FPS,
            "final_start": (cursor / FPS) / POST_SPEED,
            "final_end": ((cursor + count) / FPS) / POST_SPEED,
        })
        cursor += count
        outputs.append(output)

    concat = WORK / "concat.txt"
    concat.write_text("".join(f"file '{item.resolve()}'\n" for item in outputs), encoding="utf-8")
    base = WORK / "base.mp4"
    run([
        "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
        "-i", str(concat), "-c", "copy", str(base),
    ])
    return base, timeline, cursor


def make_proof_card() -> Path:
    PANELS.mkdir(parents=True, exist_ok=True)
    page = Image.open(FORBES_SCREENSHOT).convert("RGB")
    page = page.crop((40, 300, 830, 1450))
    page = ImageOps.contain(page, (205, 280), Image.Resampling.LANCZOS)

    card = Image.new("RGBA", (520, 420), (11, 14, 20, 238))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle((0, 0, 519, 419), radius=28, fill=(11, 14, 20, 238), outline=(255, 255, 255, 95), width=3)
    eyebrow = ImageFont.truetype(str(FONT_BOLD), 25)
    headline = ImageFont.truetype(str(FONT_BLACK), 42)
    detail = ImageFont.truetype(str(FONT_BOLD), 27)
    small = ImageFont.truetype(str(FONT_BOLD), 17)
    draw.text((260, 32), "FORBES PROFILE", font=eyebrow, fill=BLUE, anchor="mm")
    x = 20
    y = 68
    mask = Image.new("L", page.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, page.width - 1, page.height - 1), radius=12, fill=255)
    card.paste(page, (x, y), mask)
    draw.rounded_rectangle((x - 2, y - 2, x + page.width + 1, y + page.height + 1), radius=12, outline="white", width=2)
    tx = 360
    draw.text((tx, 135), "$1B", font=headline, fill=GREEN, anchor="mm")
    draw.text((tx, 180), "NET WORTH", font=detail, fill="white", anchor="mm")
    draw.text((tx, 242), "22 BUSINESSES", font=detail, fill=YELLOW, anchor="mm")
    draw.text((tx, 296), "RICK JACKSON", font=detail, fill="white", anchor="mm")
    draw.text((260, 385), "SOURCE: FORBES.COM/PROFILE/RICK-JACKSON", font=small, fill=(170, 178, 194), anchor="mm")
    output = PANELS / "forbes_proof_card.png"
    card.save(output)
    return output


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
    yellow = ass_color(YELLOW)
    white = ass_color("#FFFFFF")
    return escaped.replace(key, f"{{\\c{yellow}\\fs90}}{key}{{\\c{white}\\fs80}}", 1)


def write_ass(timeline: list[dict[str, Any]], total_duration: float) -> Path:
    starts = {item["name"]: item["pre_speed_start"] for item in timeline}
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {WIDTH}",
        f"PlayResY: {HEIGHT}",
        "ScaledBorderAndShadow: yes",
        "WrapStyle: 2",
        "",
        "[V4+ Styles]",
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding",
        "Style: Caption,Komika Axis,80,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,8,2,5,86,86,700,1",
        "Style: Hook,Komika Axis,112,&H00FFFFFF,&H00FFFFFF,&H00000000,&H900B0E14,-1,0,0,0,100,100,0,0,1,9,3,8,70,70,1450,1",
        "Style: Badge,Arial Bold,45,&H00FFFFFF,&H00FFFFFF,&H00000000,&HD00B0E14,-1,0,0,0,100,100,0,0,3,2,0,8,70,70,1530,1",
        "Style: Small,Arial Bold,28,&H80FFFFFF,&H80FFFFFF,&H80000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,7,28,28,28,1",
        "",
        "[Events]",
        "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
    ]

    for segment_name, events in CAPTIONS.items():
        base = starts[segment_name]
        for rel_start, rel_end, text, keyword in events:
            y = 1280 if segment_name == "hook_zero" else 1152
            body = f"{{\\an5\\pos(540,{y})}}{emphasized(text, keyword)}"
            lines.append(
                f"Dialogue: 8,{ass_time(base + rel_start)},{ass_time(base + rel_end)},Caption,,0,0,0,,{body}"
            )

    # Keep the cold-open state visible without adding a title card.
    lines.append(
        f"Dialogue: 5,{ass_time(0.0)},{ass_time(starts['bought'])},Badge,,0,0,0,,"
        "{\\an8\\pos(540,275)}THE $0 BET"
    )

    # Inline salary-risk comparison; both rows stay over moving footage.
    comparison_start = starts["salary"] + 1.55
    comparison_end = starts["bought"] + 0.20
    lines.append(
        f"Dialogue: 6,{ass_time(comparison_start)},{ass_time(comparison_end)},Badge,,0,0,0,,"
        "{\\an8\\pos(540,310)}THEM: $1,100 + COMMISSION"
    )
    lines.append(
        f"Dialogue: 6,{ass_time(comparison_start + 0.40)},{ass_time(comparison_end)},Badge,,0,0,0,,"
        f"{{\\an8\\pos(540,375)\\c{ass_color(YELLOW)}}}HIM: $0 + 33%"
    )

    found = starts["revenue"]
    lines.append(
        f"Dialogue: 7,{ass_time(found + 7.35)},{ass_time(found + 9.18)},Hook,,0,0,0,,"
        f"{{\\an8\\pos(540,300)\\c{ass_color(GREEN)}\\fad(80,120)}}$0 BET → BILLIONAIRE"
    )

    close = starts["fulfill_need"]
    lines.append(
        f"Dialogue: 7,{ass_time(close + 3.55)},{ass_time(close + 5.30)},Hook,,0,0,0,,"
        "{\\an8\\pos(540,310)\\fad(100,100)}THEIR WIN = ZERO RISK"
    )
    lines.append(
        f"Dialogue: 7,{ass_time(close + 5.30)},{ass_time(close + 8.05)},Hook,,0,0,0,,"
        f"{{\\an8\\pos(540,310)\\fad(100,140)\\c{ass_color(GREEN)}}}HIS WIN = OWNERSHIP"
    )

    contract_start = starts["salary"] + 1.70
    contract_end = contract_start + 2.00
    lines.append(
        f"Dialogue: 9,{ass_time(contract_start)},{ass_time(contract_end)},Small,,0,0,0,,"
        "{\\an3\\pos(1035,1870)}ILLUSTRATION • PEXELS 7981954"
    )

    thirds = [0.0, total_duration / 3, 2 * total_duration / 3, total_duration]
    positions = [(44, 70), (780, 70), (44, 1840)]
    for index, (start, end) in enumerate(zip(thirds[:-1], thirds[1:])):
        x, y = positions[index]
        lines.append(
            f"Dialogue: 10,{ass_time(start)},{ass_time(end)},Small,,0,0,0,,"
            f"{{\\an7\\pos({x},{y})}}HARD KNOCKS LAB"
        )

    output = WORK / "captions_and_overlays.ass"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def generate_music(duration: float) -> Path:
    output = AUDIO_DIR / "ambient_bed.wav"
    run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "lavfi", "-i", f"sine=frequency=82:sample_rate=48000:duration={duration:.3f}",
        "-f", "lavfi", "-i", f"sine=frequency=123:sample_rate=48000:duration={duration:.3f}",
        "-filter_complex",
        f"[0:a]volume=0.018,afade=t=in:st=0:d=1,afade=t=out:st={duration - 1:.3f}:d=1[a0];"
        f"[1:a]volume=0.010,afade=t=in:st=0:d=1,afade=t=out:st={duration - 1:.3f}:d=1[a1];"
        "[a0][a1]amix=inputs=2:duration=longest:normalize=0,"
        "aformat=sample_fmts=s16:sample_rates=48000:channel_layouts=stereo[aout]",
        "-map", "[aout]", "-c:a", "pcm_s16le", str(output),
    ])
    return output


def make_positioned_track(
    source: Path,
    start: float,
    total_duration: float,
    output: Path,
    source_filter: str,
) -> Path:
    """Build real leading-silence samples instead of relying on shifted PTS.

    This repo's ffmpeg build can rebase an adelay-shifted stream when it enters
    amix, which makes the clip audibly start at t=0. Concatenating anullsrc
    before the clip makes the delay part of the sample stream and survives all
    downstream muxing/mixing.
    """
    if start <= 0:
        run([
            "ffmpeg", "-y", "-v", "error", "-i", str(source),
            "-filter_complex",
            f"[0:a]aresample=48000,aformat=channel_layouts=stereo,{source_filter},"
            f"apad,atrim=0:{total_duration:.6f}[out]",
            "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", str(output),
        ])
    else:
        run([
            "ffmpeg", "-y", "-v", "error",
            "-f", "lavfi", "-t", f"{start:.6f}",
            "-i", "anullsrc=r=48000:cl=stereo",
            "-i", str(source),
            "-filter_complex",
            f"[1:a]aresample=48000,aformat=channel_layouts=stereo,{source_filter}[clip];"
            f"[0:a][clip]concat=n=2:v=0:a=1,apad,atrim=0:{total_duration:.6f}[out]",
            "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", str(output),
        ])
    return output


def build_timed_audio(total_duration: float, starts: dict[str, float]) -> Path:
    tracks: list[Path] = []
    definitions = (
        ("ting_early", TING, 0.08, "volume=0.38"),
        ("ting_salary", TING, starts["salary"] + 1.70, "volume=0.24"),
        ("ting_bought", TING, starts["bought"] + 0.03, "volume=0.44"),
        ("ting_revenue", TING, starts["revenue"] + 2.70, "volume=0.32"),
        ("ting_close", TING, starts["fulfill_need"] + 5.25, "volume=0.24"),
    )
    for name, source, start, source_filter in definitions:
        tracks.append(
            make_positioned_track(
                source, start, total_duration, AUDIO_DIR / f"positioned_{name}.wav", source_filter
            )
        )

    output = AUDIO_DIR / "timed_overlays.wav"
    inputs: list[str] = []
    for track in tracks:
        inputs.extend(["-i", str(track)])
    labels = "".join(f"[{index}:a]" for index in range(len(tracks)))
    run([
        "ffmpeg", "-y", "-v", "error", *inputs,
        "-filter_complex",
        f"{labels}amix=inputs={len(tracks)}:duration=longest:normalize=0,"
        f"atrim=0:{total_duration:.6f}[out]",
        "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", str(output),
    ])
    return output


def final_composite(
    base: Path,
    timeline: list[dict[str, Any]],
    total_frames: int,
    proof_card: Path,
    ass_file: Path,
    music: Path,
) -> None:
    starts = {item["name"]: item["pre_speed_start"] for item in timeline}
    ends = {item["name"]: item["pre_speed_end"] for item in timeline}
    total_duration = total_frames / FPS
    final_duration = total_duration / POST_SPEED
    final_frames = frames_for(final_duration)

    contract_start = starts["salary"] + 1.70
    contract_end = contract_start + 2.00
    proof_start = starts["find_win"] + 0.05
    proof_end = min(starts["find_win"] + 3.05, ends["find_win"])

    timed_audio = build_timed_audio(total_duration, starts)

    ass_escaped = str(ass_file).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    filter_graph = (
        # Preserve the active speaker during the illustrative insert. The old
        # full-screen Pexels cut hid Rick for two seconds while he was speaking.
        f"[1:v]scale=330:586:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop=330:586,setsar=1,format=yuv420p,"
        f"drawbox=x=0:y=0:w=iw:h=ih:color=white@0.78:t=5[contract];"
        f"[0:v][contract]overlay=x='W-w-28':y=1280:eof_action=pass:"
        f"enable='between(t,{contract_start:.3f},{contract_end:.3f})'[v2];"
        f"[2:v]scale=390:315:flags=lanczos,format=rgba,"
        f"fade=t=in:st={proof_start + 0.05:.3f}:d=0.16:alpha=1,"
        f"fade=t=out:st={proof_end - 0.18:.3f}:d=0.16:alpha=1[proof];"
        # Proof stays opposite the active Rick crop instead of covering him.
        f"[v2][proof]overlay=x='W-w-30':y=55:eof_action=pass:"
        f"enable='between(t,{proof_start:.3f},{proof_end:.3f})'[v3];"
        f"[v3]subtitles='{ass_escaped}':fontsdir='{FONT_KOMIKA.parent}'[vsub];"
        f"[vsub]setpts=PTS/{POST_SPEED:.5f},fps={FPS},format=yuv420p[vout];"
        f"[0:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.0[basea];"
        f"[3:a]aresample=48000,aformat=channel_layouts=stereo[timed];"
        f"[4:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.14[music];"
        f"[basea][timed][music]amix=inputs=3:duration=longest:normalize=0,"
        f"atrim=0:{total_duration:.3f},loudnorm=I=-16.5:TP=-1.5:LRA=10,"
        f"atempo={POST_SPEED:.5f},atrim=0:{final_duration:.6f},alimiter=limit=0.94[aout]"
    )

    script = WORK / "final.ffscript"
    script.write_text(filter_graph + "\n", encoding="utf-8")
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    png_duration = total_duration + 1.0
    run([
        "ffmpeg", "-y", "-v", "error",
        "-i", str(base),
        "-stream_loop", "-1", "-ss", "0.4", "-i", str(PEXELS_CONTRACT),
        "-loop", "1", "-t", f"{png_duration:.3f}", "-i", str(proof_card),
        "-i", str(timed_audio), "-i", str(music),
        "-filter_complex_script", str(script),
        "-map", "[vout]", "-map", "[aout]", "-frames:v", str(final_frames),
        *encode_args(), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart", "-t", f"{final_duration:.6f}", str(FINAL),
    ])


def validate_final(timeline: list[dict[str, Any]]) -> dict[str, Any]:
    data = probe(FINAL)
    video = next(stream for stream in data["streams"] if stream["codec_type"] == "video")
    audio = next(stream for stream in data["streams"] if stream["codec_type"] == "audio")
    duration = float(data["format"]["duration"])
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
        "all_source_clips_under_15s": all(item["source_duration"] < 15.0 for item in timeline),
        "total_source_under_50pct": sum(item["source_duration"] for item in timeline) < 1316.241 / 2,
    }
    if not all(checks.values()):
        raise RuntimeError(f"Final validation failed: {checks}")
    report = {
        "final": str(FINAL),
        "duration": duration,
        "checks": checks,
        "total_source_duration": sum(item["source_duration"] for item in timeline),
        "source_duration": 1316.241,
        "source_use_percent": 100 * sum(item["source_duration"] for item in timeline) / 1316.241,
        "timeline": timeline,
    }
    (WORK / "timeline.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def require_inputs() -> None:
    required = (
        SOURCE, PEXELS_CONTRACT, FORBES_SCREENSHOT, TING, FONT_KOMIKA,
    )
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required inputs:\n" + "\n".join(missing))


def main() -> None:
    require_inputs()
    for directory in (WORK, SEGMENT_DIR, PANELS, CHECKS, AUDIO_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    total_source = sum(segment.duration for segment in SEGMENTS)
    if any(segment.duration >= 15.0 for segment in SEGMENTS):
        raise ValueError("Every source segment must be strictly below 15 seconds")
    if total_source >= 1316.241 / 2:
        raise ValueError("Total source use must remain below 50% of the source")

    base, timeline, total_frames = build_base()
    total_duration = total_frames / FPS
    proof_card = make_proof_card()
    ass_file = write_ass(timeline, total_duration)
    music = generate_music(total_duration)
    final_composite(base, timeline, total_frames, proof_card, ass_file, music)
    report = validate_final(timeline)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
