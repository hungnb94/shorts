#!/usr/bin/env python3
"""Render HardKnocks V13: Atlanta Billionaire Hunt.

Direct Search Question hook, escalating candidate montage, independent Forbes
proof, Mid-Roll Triple CTA, and Rick Jackson's commission-only Business Lesson
Payoff.

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
WORK = PROJECT / "clips" / "v13_billionaire_hunt_work"
SEGMENT_DIR = WORK / "segments"
PANELS = WORK / "panels"
CHECKS = WORK / "checks"
AUDIO_DIR = WORK / "audio"
PROOF_SOURCES = WORK / "proof_sources"
FINAL = PROJECT / "final" / "2026-07-22-hardknocks_v13_atlanta_billionaire_hunt.mp4"

PEXELS_CONTRACT = ROOT / "output" / "shared" / "pexels" / "contract_signing_7981954.mp4"
FORBES_SCREENSHOT = PROOF_SOURCES / "forbes_rick_jackson.png"
CTA_VO = AUDIO_DIR / "cta_qwen.wav"
PROOF_VO = AUDIO_DIR / "proof_qwen.wav"
PAYOFF_VO = AUDIO_DIR / "payoff_qwen.wav"
QUESTION_HOOK_VO = AUDIO_DIR / "question_hook_qwen.wav"
BRANDING = ROOT / "output" / "shared" / "hardknocks_branding"
TING = BRANDING / "verdict_correct_ting.wav"
BUZZ = BRANDING / "verdict_wrong_buzz.wav"

FONT_KOMIKA = ROOT / "assets" / "fonts" / "komika-axis" / "KOMIKAX_.ttf"
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
FONT_BLACK = Path("/System/Library/Fonts/Supplemental/Arial Black.ttf")

WIDTH = 1080
HEIGHT = 1920
FPS = 30
POST_SPEED = 1.12
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
    Segment("mission", 0.08, 4.08, ((0.0, 0.50),), 1.03, "hook"),
    Segment(
        "rejection", 90.88, 93.80,
        ((0.0, 0.35), (1.20, 0.66), (2.05, 0.35)), 1.03, "resistance",
    ),
    Segment("waffle", 194.56, 200.56, ((0.0, 0.34),), 1.03, "candidate"),
    Segment(
        "prison_wealth", 559.60, 565.10,
        ((0.0, 0.66), (2.15, 0.35)), 1.03, "candidate",
    ),
    Segment(
        "prison_eight", 602.64, 607.44,
        ((0.0, 0.66), (2.35, 0.35)), 1.03, "candidate",
    ),
    Segment(
        "rick_companies", 970.60, 975.70,
        ((0.0, 0.40), (1.55, 0.68)), 1.03, "find",
    ),
    Segment(
        "rick_revenue", 976.16, 985.36,
        ((0.0, 0.40), (3.68, 0.68), (5.84, 0.40), (6.80, 0.68),
         (7.35, 0.40), (8.45, 0.68)), 1.03, "find",
    ),
    Segment("proof_backdrop", 985.36, 990.48, ((0.0, 0.58),), 1.05, "proof"),
    Segment("cta_backdrop", 990.48, 994.32, ((0.0, 0.58),), 1.05, "cta"),
    Segment("rick_no_degree", 1017.92, 1021.03, ((0.0, 0.68),), 1.04, "lesson"),
    Segment("rick_commission", 1024.08, 1032.24, ((0.0, 0.68),), 1.04, "lesson"),
    Segment("rick_bought", 1032.24, 1035.27, ((0.0, 0.68),), 1.04, "lesson"),
    Segment("payoff_backdrop", 1035.27, 1038.55, ((0.0, 0.68),), 1.05, "payoff"),
)


CAPTIONS: dict[str, tuple[tuple[float, float, str, str], ...]] = {
    "mission": (
        (0.00, 1.14, "HOW MANY MILLIONAIRES", "MILLIONAIRES"),
        (1.14, 1.80, "DO YOU HAVE TO MEET", "MEET"),
        (1.80, 2.50, "BEFORE YOU FIND", "FIND"),
        (2.50, 3.95, "A REAL BILLIONAIRE?", "BILLIONAIRE"),
    ),
    "rejection": (
        (0.00, 1.35, "I CAN'T DISCUSS THAT", "CAN'T"),
        (1.35, 2.92, "NO, THANK YOU", "NO"),
    ),
    "waffle": (
        (0.00, 2.25, "A FRANCHISEE AT 22", "22"),
        (2.25, 4.45, "I HAD 14 LOCATIONS", "14"),
        (4.45, 6.00, "THEN HOTELS TOO", "HOTELS"),
    ),
    "prison_wealth": (
        (0.00, 2.20, "WHERE'D YOU LEARN WEALTH?", "WEALTH"),
        (2.20, 3.25, "IN PRISON", "PRISON"),
        (3.25, 5.50, "I STARTED READING", "READING"),
    ),
    "prison_eight": (
        (0.00, 2.30, "WHAT'S YOUR NET WORTH?", "NET WORTH"),
        (2.30, 4.80, "EIGHT FIGURES", "EIGHT"),
    ),
    "rick_companies": (
        (0.00, 1.60, "HOW'D YOU GET RICH?", "RICH"),
        (1.60, 2.80, "HEALTHCARE", "HEALTHCARE"),
        (2.80, 5.10, "I OWN 22 COMPANIES", "22"),
    ),
    "rick_revenue": (
        (0.00, 2.75, "YOUR BIGGEST YEAR?", "BIGGEST"),
        (2.75, 5.75, "$3 BILLION A YEAR", "$3 BILLION"),
        (5.75, 6.80, "WITH A B?", "B"),
        (6.80, 7.55, "WITH A B.", "B"),
        (7.55, 8.55, "A BILLIONAIRE?", "BILLIONAIRE"),
        (8.55, 9.20, "YEAH.", "YEAH"),
    ),
    "proof_backdrop": (
        (0.00, 1.60, "FORBES CONFIRMS IT", "FORBES"),
        (1.60, 3.35, "$1 BILLION NET WORTH", "$1 BILLION"),
        (3.35, 5.12, "$3 BILLION REVENUE", "$3 BILLION"),
    ),
    "cta_backdrop": (
        (0.00, 1.60, "WOULD YOU TAKE IT?", "TAKE"),
        (1.60, 3.84, "LIKE, SUBSCRIBE, COMMENT", "COMMENT"),
    ),
    "rick_no_degree": (
        (0.00, 1.65, "THEY WOULDN'T HIRE ME", "WOULDN'T"),
        (1.65, 3.11, "NO DEGREE", "NO DEGREE"),
    ),
    "rick_commission": (
        (0.00, 2.90, "$1,100 A MONTH", "$1,100"),
        (2.90, 4.75, "PLUS COMMISSION", "COMMISSION"),
        (4.75, 6.30, "WHAT IF NO SALARY?", "NO SALARY"),
        (6.30, 8.16, "JUST 33% COMMISSION", "33%"),
    ),
    "rick_bought": (
        (0.00, 1.55, "ONE YEAR LATER", "ONE YEAR"),
        (1.55, 3.03, "I BOUGHT THE FIRM", "BOUGHT"),
    ),
    "payoff_backdrop": (
        (0.00, 1.65, "HE REMOVED THEIR RISK", "RISK"),
        (1.65, 3.28, "THEN EARNED OWNERSHIP", "OWNERSHIP"),
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
    audio_filter = (
        "highpass=f=70,"
        "acompressor=threshold=0.125:ratio=2:attack=5:release=80:makeup=1.4,"
        "loudnorm=I=-16:TP=-1.5:LRA=10,"
        "aresample=48000:first_pts=0,apad,"
        f"atrim=0:{segment.duration:.6f},"
        f"afade=t=in:st=0:d={SEGMENT_FADE_IN:.2f},"
        f"afade=t=out:st={segment.duration - SEGMENT_FADE_OUT:.6f}:d={SEGMENT_FADE_OUT:.2f}"
    )
    run([
        "ffmpeg", "-y", "-v", "error", "-ss", f"{segment.source_start:.6f}",
        "-i", str(SOURCE), "-t", f"{segment.duration:.6f}",
        "-vf", f"{scaled_crop(segment)},fps={FPS}",
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
    page = ImageOps.contain(page, (880, 930), Image.Resampling.LANCZOS)

    card = Image.new("RGBA", (980, 1460), (11, 14, 20, 245))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle((0, 0, 979, 1459), radius=32, fill=(11, 14, 20, 245), outline=(255, 255, 255, 80), width=3)
    eyebrow = ImageFont.truetype(str(FONT_BOLD), 34)
    headline = ImageFont.truetype(str(FONT_BLACK), 62)
    detail = ImageFont.truetype(str(FONT_BOLD), 40)
    draw.text((490, 52), "FORBES PROFILE", font=eyebrow, fill=BLUE, anchor="mm")
    x = (980 - page.width) // 2
    y = 100
    mask = Image.new("L", page.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, page.width - 1, page.height - 1), radius=18, fill=255)
    card.paste(page, (x, y), mask)
    draw.rounded_rectangle((x - 2, y - 2, x + page.width + 1, y + page.height + 1), radius=18, outline="white", width=3)
    draw.text((490, 1100), "$1B NET WORTH", font=headline, fill=GREEN, anchor="mm")
    draw.text((490, 1185), "22 BUSINESSES", font=detail, fill="white", anchor="mm")
    draw.text((490, 1250), "$3B ANNUAL REVENUE", font=detail, fill=YELLOW, anchor="mm")
    draw.text((490, 1365), "SOURCE: FORBES.COM/PROFILE/RICK-JACKSON", font=eyebrow, fill=(170, 178, 194), anchor="mm")
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
        "Style: CTA,Arial Black,72,&H00FFFFFF,&H00FFFFFF,&H00000000,&HD00B0E14,-1,0,0,0,100,100,0,0,3,3,0,5,90,90,1050,1",
        "Style: Small,Arial Bold,28,&H80FFFFFF,&H80FFFFFF,&H80000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,7,28,28,28,1",
        "",
        "[Events]",
        "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
    ]

    for segment_name, events in CAPTIONS.items():
        base = starts[segment_name]
        for rel_start, rel_end, text, keyword in events:
            if segment_name == "proof_backdrop":
                y = 1580
            elif segment_name == "mission":
                # The walking close-up fills the hook frame; place captions on
                # the torso rather than obscuring the host's mouth.
                y = 1280
            else:
                y = 1152
            body = f"{{\\an5\\pos(540,{y})}}{emphasized(text, keyword)}"
            lines.append(
                f"Dialogue: 8,{ass_time(base + rel_start)},{ass_time(base + rel_end)},Caption,,0,0,0,,{body}"
            )

    rejection = starts["rejection"]
    lines.append(
        f"Dialogue: 4,{ass_time(rejection)},{ass_time(starts['rick_revenue'] + 7.35)},Badge,,0,0,0,,"
        "{\\an8\\pos(540,320)}BILLIONAIRE FOUND: NO"
    )
    waffle = starts["waffle"]
    lines.append(
        f"Dialogue: 6,{ass_time(waffle + 2.15)},{ass_time(waffle + 5.95)},Badge,,0,0,0,,"
        "{\\an8\\pos(540,400)\\c&H003CD2FF&}14 LOCATIONS — NOT THE TARGET"
    )
    prison = starts["prison_eight"]
    lines.append(
        f"Dialogue: 6,{ass_time(prison + 2.25)},{ass_time(prison + 4.75)},Badge,,0,0,0,,"
        "{\\an8\\pos(540,400)\\c&H003CD2FF&}SOURCE-REPORTED: EIGHT FIGURES"
    )
    found = starts["rick_revenue"]
    lines.append(
        f"Dialogue: 7,{ass_time(found + 7.35)},{ass_time(found + 9.18)},Hook,,0,0,0,,"
        f"{{\\an8\\pos(540,300)\\c{ass_color(GREEN)}\\fad(80,120)}}BILLIONAIRE FOUND"
    )

    cta = starts["cta_backdrop"]
    lines.append(
        f"Dialogue: 7,{ass_time(cta + 0.05)},{ass_time(cta + 3.80)},CTA,,0,0,0,,"
        f"{{\\an5\\pos(540,680)\\fad(120,120)\\c{ass_color(YELLOW)}}}LIKE  •  SUBSCRIBE  •  COMMENT"
    )
    lines.append(
        f"Dialogue: 7,{ass_time(cta + 0.15)},{ass_time(cta + 3.80)},Badge,,0,0,0,,"
        "{\\an5\\pos(540,820)}WOULD YOU TAKE HIS FIRST BET?"
    )

    no_degree = starts["rick_no_degree"]
    lines.append(
        f"Dialogue: 5,{ass_time(no_degree)},{ass_time(starts['rick_bought'] + 3.0)},Badge,,0,0,0,,"
        "{\\an8\\pos(540,320)}THE FIRST BET"
    )
    payoff = starts["payoff_backdrop"]
    lines.append(
        f"Dialogue: 6,{ass_time(payoff)},{ass_time(payoff + 1.65)},Hook,,0,0,0,,"
        "{\\an8\\pos(540,300)}REMOVE THEIR RISK"
    )
    lines.append(
        f"Dialogue: 6,{ass_time(payoff + 1.65)},{ass_time(payoff + 3.25)},Hook,,0,0,0,,"
        f"{{\\an8\\pos(540,300)\\c{ass_color(GREEN)}}}EARN THE UPSIDE"
    )

    contract_start = starts["rick_commission"] + 0.65
    contract_end = starts["rick_commission"] + 6.55
    lines.append(
        f"Dialogue: 9,{ass_time(contract_start)},{ass_time(contract_end)},Small,,0,0,0,,"
        "{\\an1\\pos(42,1810)}ILLUSTRATION • PEXELS 7981954"
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
        ("question_hook_vo", QUESTION_HOOK_VO, 0.0, vo_loudnorm()),
        ("proof_vo", PROOF_VO, starts["proof_backdrop"], vo_loudnorm()),
        ("cta_vo", CTA_VO, starts["cta_backdrop"], vo_loudnorm()),
        ("payoff_vo", PAYOFF_VO, starts["payoff_backdrop"], vo_loudnorm()),
        ("ting_early", TING, 0.08, "volume=0.42"),
        ("ting_hook_reveal", TING, 2.62, "volume=0.34"),
        ("ting_found", TING, starts["rick_revenue"] + 7.35, "volume=0.55"),
        ("ting_proof", TING, starts["proof_backdrop"], "volume=0.38"),
        # Pre-lap the rejection cue so the question-to-first-candidate cut flows
        # without a detector-visible dead-air gap.
        ("buzz_reject", BUZZ, starts["rejection"] - 0.25, "volume=0.30"),
        ("buzz_eight", BUZZ, starts["prison_eight"] + 2.25, "volume=0.22"),
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

    mission_start, mission_end = starts["mission"], ends["mission"]
    contract_start = starts["rick_commission"] + 0.65
    contract_end = starts["rick_commission"] + 6.55
    proof_start, proof_end = starts["proof_backdrop"], ends["proof_backdrop"]
    cta_start, cta_end = starts["cta_backdrop"], ends["cta_backdrop"]
    payoff_start, payoff_end = starts["payoff_backdrop"], ends["payoff_backdrop"]

    timed_audio = build_timed_audio(total_duration, starts)

    ass_escaped = str(ass_file).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    filter_graph = (
        f"[1:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT},setsar=1,format=yuv420p[contract];"
        f"[0:v][contract]overlay=x=0:y=0:eof_action=pass:"
        f"enable='between(t,{contract_start:.3f},{contract_end:.3f})'[v2];"
        f"[2:v]format=rgba,fade=t=in:st={proof_start + 0.05:.3f}:d=0.16:alpha=1,"
        f"fade=t=out:st={proof_end - 0.18:.3f}:d=0.16:alpha=1[proof];"
        f"[v2][proof]overlay=x=(W-w)/2:y=190:eof_action=pass:"
        f"enable='between(t,{proof_start:.3f},{proof_end:.3f})'[v3];"
        f"[v3]subtitles='{ass_escaped}':fontsdir='{FONT_KOMIKA.parent}'[vsub];"
        f"[vsub]setpts=PTS/{POST_SPEED:.5f},fps={FPS},format=yuv420p[vout];"
        f"[0:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"volume=0.015:enable='between(t,{mission_start:.3f},{mission_end:.3f})',"
        f"volume=0.02:enable='between(t,{proof_start:.3f},{cta_end:.3f})',"
        f"volume=0.02:enable='between(t,{payoff_start:.3f},{payoff_end:.3f})'[basea];"
        f"[3:a]aresample=48000,aformat=channel_layouts=stereo[timed];"
        f"[4:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.24[music];"
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
        SOURCE, PEXELS_CONTRACT, FORBES_SCREENSHOT,
        QUESTION_HOOK_VO, CTA_VO, PROOF_VO, PAYOFF_VO, TING, BUZZ, FONT_KOMIKA,
    )
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required inputs:\n" + "\n".join(missing))


def main() -> None:
    require_inputs()
    for directory in (WORK, SEGMENT_DIR, PANELS, CHECKS, AUDIO_DIR, PROOF_SOURCES):
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
