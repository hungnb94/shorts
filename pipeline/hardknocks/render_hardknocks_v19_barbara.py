#!/usr/bin/env python3
"""Render HardKnocks V19: Barbara Corcoran's Rejection Ladder.

The edit applies the reference video's payoff-first Setup -> Conflict ->
Resolution system, motivated cuts, audio pre-laps, and continuous surprise.
It is a one-off media renderer: completion is verified against the real MP4,
not renderer unit tests.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "hardknocks"
SOURCE = PROJECT / "source" / "nswPe9PAgjo.mp4"
WORK = PROJECT / "clips" / "v19_barbara_work"
SEGMENT_DIR = WORK / "segments"
PANELS = WORK / "panels"
CHECKS = WORK / "checks"
AUDIO_DIR = WORK / "audio"
FINAL = PROJECT / "final" / "2026-07-29-hardknocks_v19_barbara_rejection_ladder.mp4"

PEXELS_EMAIL = ROOT / "output" / "shared" / "pexels" / "woman_typing_email_6608213.mp4"
BRIDGE_AUDIO = AUDIO_DIR / "bridge.wav"
CTA_AUDIO = AUDIO_DIR / "cta.wav"
BRANDING = ROOT / "output" / "shared" / "hardknocks_branding"
TING = BRANDING / "verdict_correct_ting.wav"
BUZZ = BRANDING / "verdict_wrong_buzz.wav"

FONT_KOMIKA = ROOT / "assets" / "fonts" / "komika-axis" / "KOMIKAX_.ttf"
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
FONT_BLACK = Path("/System/Library/Fonts/Supplemental/Arial Black.ttf")

WIDTH = 1080
HEIGHT = 1920
FPS = 30
CAPTION_BAND_PX = 270
SEGMENT_FADE_IN = 0.12
SEGMENT_FADE_OUT = 0.20
SOURCE_DURATION = 1053.301

YELLOW = "#FFD23C"
GREEN = "#00D66E"
RED = "#FF4D4D"
BLUE = "#4FC3F7"
DARK = "#0B0E14"
GRAY = "#9AA3B2"


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
    visual_start: float = 0.0

    @property
    def duration(self) -> float:
        return self.end - self.start


# Barbara sits frame-left (~25%); the host sits frame-right (~70%). Crop turns
# keep the active speaker near center. The opening changes crop every ~1 second
# while preserving real facial movement from frame zero.
SEGMENTS = (
    Segment(
        "hook_fired", "source", 138.90, 143.45,
        ((0.00, 0.22), (0.95, 0.25), (1.90, 0.22), (2.85, 0.25),
         (3.80, 0.22), (4.80, 0.25)), 1.10, "setup",
    ),
    Segment(
        "host_question", "source", 147.10, 149.45,
        ((0.00, 0.22), (1.05, 0.77), (1.75, 0.73)), 1.07, "open_loop",
    ),
    Segment(
        "email_reply", "source", 149.30, 155.45,
        ((0.00, 0.22), (1.18, 0.25), (2.36, 0.22), (3.54, 0.25),
         (4.72, 0.22)), 1.08, "conflict",
    ),
    Segment(
        "seat_won", "source", 155.35, 163.25,
        ((0.00, 0.22), (1.25, 0.25), (2.50, 0.22), (3.75, 0.25),
         (5.00, 0.22), (6.25, 0.25)), 1.07, "resolution_one",
    ),
    Segment(
        "failure_buffer", "source", 484.20, 492.25,
        ((0.00, 0.77), (1.10, 0.22), (2.50, 0.25), (3.75, 0.22),
         (5.00, 0.22), (6.25, 0.25), (7.35, 0.22)), 1.07, "mechanism",
    ),
    Segment(
        "editorial_bridge", "narration", 0.00, 5.08,
        (), 1.00, "commentary", BRIDGE_AUDIO, 1.80,
    ),
    Segment(
        "two_million_offer", "source", 320.15, 324.75,
        ((0.00, 0.22), (1.15, 0.25), (2.30, 0.22), (3.45, 0.25)),
        1.08, "decision",
    ),
    Segment(
        "story_cta", "narration", 0.00, 5.32,
        (), 1.00, "cta", CTA_AUDIO, 6.60,
    ),
    Segment(
        "sixty_six_payoff", "source", 324.65, 329.35,
        ((0.00, 0.22), (1.15, 0.25), (2.30, 0.22), (3.45, 0.25)),
        1.09, "resolution_two",
    ),
    Segment(
        "cash_in_a_day", "source", 13.25, 25.30,
        ((0.00, 0.77), (1.55, 0.22), (3.10, 0.25), (4.65, 0.77),
         (6.20, 0.22), (7.75, 0.77), (9.30, 0.22), (10.65, 0.25)),
        1.07, "proof",
    ),
    Segment(
        "loop_prep", "silent_source", 136.62, 137.32,
        ((0.00, 0.22),), 1.10, "loop",
    ),
)


CAPTIONS: dict[str, tuple[tuple[float, float, str, str], ...]] = {
    "hook_fired": (
        (0.00, 0.83, "I GOT CHOSEN", "CHOSEN"),
        (0.83, 1.55, "FOR SHARK TANK", "SHARK TANK"),
        (1.55, 2.45, "I SIGNED THE CONTRACT", "SIGNED"),
        (2.45, 3.35, "FOR SHARK TANK", "SHARK TANK"),
        (3.35, 4.00, "I GOT FIRED", "FIRED"),
        (4.00, 4.55, "BY SHARK TANK", "SHARK TANK"),
    ),
    "host_question": (
        (0.00, 1.16, "ROLLER COASTER RIDE", "COASTER"),
        (1.16, 2.35, "HOW'D YOU WIN IT BACK?", "BACK"),
    ),
    "email_reply": (
        (0.35, 1.90, "GOOD AT PERSUADING", "PERSUADING"),
        (1.90, 3.05, "I WROTE THE PRODUCER", "WROTE"),
        (3.05, 4.85, "A VIVID EMAIL", "EMAIL"),
        (4.85, 6.15, "YOU MADE A MISTAKE", "MISTAKE"),
    ),
    "seat_won": (
        (0.00, 1.42, "REJECTION BECAME A", "REJECTION"),
        (1.42, 2.15, "LUCKY CHARM", "LUCKY"),
        (2.15, 3.24, "EVERYTHING IN MY LIFE", "LIFE"),
        (3.24, 4.24, "THAT WAS REJECTION", "REJECTION"),
        (4.24, 5.18, "BECAME A LUCKY CHARM", "LUCKY"),
        (5.18, 6.38, "INVITE BOTH WOMEN", "BOTH"),
        (6.38, 7.40, "COMPETE FOR THE SEAT", "SEAT"),
        (7.40, 7.90, "AND I WON", "WON"),
    ),
    "failure_buffer": (
        (0.00, 1.15, "HOW'D YOU FIND SELF-BELIEF?", "SELF-BELIEF"),
        (1.15, 2.50, "I HAD 22 JOBS", "22 JOBS"),
        (2.50, 3.64, "IF IT DIDN'T WORK", "DIDN'T"),
        (3.64, 4.82, "I'D GET MY OLD JOB BACK", "BACK"),
        (4.82, 5.88, "THAT'S PRETTY GOOD", "GOOD"),
        (5.88, 8.05, "I WAS HAPPY POOR", "HAPPY"),
    ),
    "editorial_bridge": (
        (0.00, 1.48, "HER EDGE WASN'T LUCK", "LUCK"),
        (1.48, 2.95, "EVERY REJECTION TRIGGERED", "REJECTION"),
        (2.95, 4.15, "A BETTER NEXT MOVE", "NEXT"),
        (4.15, 5.08, "SHE REPEATED IT", "REPEATED"),
    ),
    "two_million_offer": (
        (0.00, 1.10, "TIMING IS IMPORTANT", "TIMING"),
        (1.10, 2.60, "I ALMOST SOLD", "SOLD"),
        (2.60, 3.65, "FOR $2 MILLION", "$2 MILLION"),
        (3.65, 4.60, "I TURNED IT DOWN", "DOWN"),
    ),
    "story_cta": (
        (0.45, 1.60, "LIKE + SUBSCRIBE", "LIKE"),
        (1.60, 2.85, "AND COMMENT", "COMMENT"),
        (2.85, 4.40, "TAKE $2M NOW", "$2M"),
        (4.40, 5.32, "OR WAIT?", "WAIT"),
    ),
    "sixty_six_payoff": (
        (0.00, 1.32, "BUT TWO YEARS LATER", "TWO YEARS"),
        (1.32, 2.70, "I SOLD MY BUSINESS", "SOLD"),
        (2.70, 3.88, "FOR $66 MILLION", "$66 MILLION"),
        (3.88, 4.70, "TIMING IS EVERYTHING", "TIMING"),
    ),
    "cash_in_a_day": (
        (0.00, 1.78, "MOST MADE IN ONE YEAR?", "ONE YEAR"),
        (1.78, 3.36, "$66 MILLION CASH", "$66 MILLION"),
        (3.36, 4.82, "I HAVEN'T SPENT IT", "SPENT"),
        (4.82, 6.15, "MADE IN A YEAR?", "YEAR"),
        (6.15, 6.50, "NO.", "NO."),
        (6.50, 7.35, "MADE IN ONE DAY", "ONE DAY"),
        (7.35, 8.55, "ONE DAY? HOW?", "HOW"),
        (8.55, 9.85, "I SOLD THE BUSINESS", "SOLD"),
        (9.85, 10.95, "BUILT CORCORAN GROUP", "CORCORAN"),
        (10.95, 12.05, "THAT'S WHAT THEY PAID", "PAID"),
    ),
    "loop_prep": (
        (0.00, 0.70, "AND IT STARTED WITH...", "STARTED"),
    ),
}


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
        "eq=contrast=1.04:saturation=1.05,setsar=1,format=yuv420p"
    )


def render_source_segment(segment: Segment, output: Path) -> int:
    if segment.duration >= 15.0:
        raise ValueError(f"Source clip reaches 15 seconds: {segment.name}")
    frame_count = frames_for(segment.duration)
    coarse_start = max(0.0, segment.start - 5.0)
    fine_offset = segment.start - coarse_start
    volume = "volume=0" if segment.kind == "silent_source" else "volume=1"
    audio_filter = (
        f"atrim=start={fine_offset:.6f},asetpts=PTS-STARTPTS,{volume},highpass=f=70,"
        "acompressor=threshold=0.125:ratio=2:attack=5:release=80:makeup=1.4,"
        "loudnorm=I=-16:TP=-1.5:LRA=10,aresample=48000:first_pts=0,apad,"
        f"atrim=0:{segment.duration:.6f},"
        f"afade=t=in:st=0:d={SEGMENT_FADE_IN:.2f},"
        f"afade=t=out:st={max(0.0, segment.duration - SEGMENT_FADE_OUT):.6f}:d={SEGMENT_FADE_OUT:.2f}"
    )
    run([
        "ffmpeg", "-y", "-v", "error", "-ss", f"{coarse_start:.6f}",
        "-i", SOURCE, "-t", f"{segment.duration:.6f}",
        "-vf", f"trim=start={fine_offset:.6f},setpts=PTS-STARTPTS,{source_crop(segment)},fps={FPS}",
        "-af", audio_filter, "-frames:v", str(frame_count), *encode_args(),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", output,
    ])
    return frame_count


def render_narration_segment(segment: Segment, output: Path) -> int:
    if segment.audio is None:
        raise ValueError(f"Narration segment has no audio: {segment.name}")
    frame_count = frames_for(segment.duration)
    crop = (
        "scale=1166:-2:flags=lanczos,"
        "crop=1080:1920:"
        "x='(in_w-out_w)/2+18*sin(t*0.9)':"
        "y='(in_h-out_h)/2+28*sin(t*0.7)',"
        "eq=contrast=1.04:saturation=0.92,setsar=1,format=yuv420p,fps=30"
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
        "ffmpeg", "-y", "-v", "error", "-stream_loop", "-1",
        "-ss", f"{segment.visual_start:.3f}", "-i", PEXELS_EMAIL,
        "-i", segment.audio, "-vf", crop, "-af", audio_filter,
        "-frames:v", str(frame_count), *encode_args(),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", output,
    ])
    return frame_count


def build_base() -> tuple[Path, list[dict[str, Any]], int]:
    SEGMENT_DIR.mkdir(parents=True, exist_ok=True)
    cursor = 0
    timeline: list[dict[str, Any]] = []
    outputs: list[Path] = []
    for index, segment in enumerate(SEGMENTS):
        output = SEGMENT_DIR / f"{index:02d}_{segment.name}.mp4"
        count = (
            render_narration_segment(segment, output)
            if segment.kind == "narration"
            else render_source_segment(segment, output)
        )
        timeline.append({
            "name": segment.name,
            "kind": segment.kind,
            "act": segment.act,
            "source_start": segment.start if segment.kind != "narration" else None,
            "source_end": segment.end if segment.kind != "narration" else None,
            "source_duration": segment.duration if segment.kind != "narration" else 0.0,
            "start_frame": cursor,
            "end_frame": cursor + count,
            "frames": count,
            "final_start": cursor / FPS,
            "final_end": (cursor + count) / FPS,
        })
        cursor += count
        outputs.append(output)

    concat = WORK / "concat.txt"
    concat.write_text("".join(f"file '{item.resolve()}'\n" for item in outputs), encoding="utf-8")
    base = WORK / "base.mp4"
    run([
        "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
        "-i", concat, "-c", "copy", base,
    ])
    return base, timeline, cursor


def new_card(width: int, height: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    card = Image.new("RGBA", (width, height), (11, 14, 20, 242))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle(
        (1, 1, width - 2, height - 2), radius=28,
        fill=(11, 14, 20, 242), outline=(255, 255, 255, 105), width=3,
    )
    return card, draw


def make_state_cards() -> list[Path]:
    PANELS.mkdir(parents=True, exist_ok=True)
    specs = (
        ("CASE 1 • THE SEAT", (("SIGNED", GREEN), ("FIRED", RED), ("NEXT?", YELLOW))),
        ("THE COUNTERMOVE", (("EMAIL", BLUE), ("COMPETE", YELLOW), ("SEAT WON", GREEN))),
        ("FAILURE BUFFER", (("22 JOBS", YELLOW), ("FALLBACK", BLUE), ("NO FEAR", GREEN))),
    )
    outputs: list[Path] = []
    eyebrow = ImageFont.truetype(str(FONT_BOLD), 23)
    value = ImageFont.truetype(str(FONT_BLACK), 42)
    arrow = ImageFont.truetype(str(FONT_BOLD), 26)
    for index, (title, rows) in enumerate(specs):
        card, draw = new_card(420, 360)
        draw.text((210, 38), title, font=eyebrow, fill=GRAY, anchor="mm")
        for row_index, (text, color) in enumerate(rows):
            y = 105 + row_index * 95
            draw.text((210, y), text, font=value, fill=color, anchor="mm")
            if row_index < len(rows) - 1:
                draw.text((210, y + 47), "↓", font=arrow, fill="white", anchor="mm")
        output = PANELS / f"state_{index}.png"
        card.save(output)
        outputs.append(output)
    return outputs


def make_email_proof() -> Path:
    card, draw = new_card(500, 330)
    eyebrow = ImageFont.truetype(str(FONT_BOLD), 23)
    headline = ImageFont.truetype(str(FONT_BLACK), 42)
    detail = ImageFont.truetype(str(FONT_BOLD), 24)
    small = ImageFont.truetype(str(FONT_BOLD), 18)
    draw.text((250, 38), "INDEPENDENT CHECK", font=eyebrow, fill=BLUE, anchor="mm")
    draw.text((250, 102), "OFFER RESCINDED", font=headline, fill=RED, anchor="mm")
    draw.text((250, 162), "EMAIL WON THE SEAT BACK", font=detail, fill=GREEN, anchor="mm")
    draw.text((250, 223), "CNBC MAKE IT", font=small, fill="white", anchor="mm")
    draw.text((250, 258), "APRIL 23, 2023", font=small, fill=GRAY, anchor="mm")
    draw.text((250, 296), "BARBARA'S ACCOUNT", font=small, fill=GRAY, anchor="mm")
    output = PANELS / "email_proof.png"
    card.save(output)
    return output


def make_decision_cards() -> list[Path]:
    PANELS.mkdir(parents=True, exist_ok=True)
    specs = (
        ("THE DECISION", "$2M NOW", "OR WAIT?", YELLOW),
        ("THE PAYOFF", "$2M  →  $66M", "33×", GREEN),
    )
    outputs: list[Path] = []
    eyebrow = ImageFont.truetype(str(FONT_BOLD), 24)
    value = ImageFont.truetype(str(FONT_BLACK), 52)
    huge = ImageFont.truetype(str(FONT_BLACK), 86)
    for index, (title, line_one, line_two, color) in enumerate(specs):
        card, draw = new_card(510, 315)
        draw.text((255, 38), title, font=eyebrow, fill=BLUE, anchor="mm")
        draw.text((255, 130), line_one, font=value, fill=color, anchor="mm")
        draw.text((255, 232), line_two, font=huge if index else value, fill=color, anchor="mm")
        output = PANELS / f"decision_{index}.png"
        card.save(output)
        outputs.append(output)
    return outputs


def make_sale_proof() -> Path:
    card, draw = new_card(500, 350)
    eyebrow = ImageFont.truetype(str(FONT_BOLD), 23)
    value = ImageFont.truetype(str(FONT_BLACK), 78)
    detail = ImageFont.truetype(str(FONT_BOLD), 25)
    small = ImageFont.truetype(str(FONT_BOLD), 18)
    draw.text((250, 38), "INDEPENDENT CHECK", font=eyebrow, fill=BLUE, anchor="mm")
    draw.text((250, 124), "$66M", font=value, fill=GREEN, anchor="mm")
    draw.text((250, 190), "CORCORAN GROUP SALE", font=detail, fill="white", anchor="mm")
    draw.text((250, 245), "CNBC MAKE IT", font=small, fill=YELLOW, anchor="mm")
    draw.text((250, 282), "SALE CLOSED IN 2001", font=small, fill=GRAY, anchor="mm")
    draw.text((250, 320), "REPORTED MARCH 8, 2018", font=small, fill=GRAY, anchor="mm")
    output = PANELS / "sale_proof.png"
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
    starts = {item["name"]: item["final_start"] for item in timeline}
    ends = {item["name"]: item["final_end"] for item in timeline}
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
        "Style: Caption,Komika Axis,80,&H00FFFFFF,&H00FFFFFF,&H00000000,&H85000000,-1,0,0,0,100,100,0,0,1,8,2,5,78,78,700,1",
        "Style: State,Arial Bold,42,&H00FFFFFF,&H00FFFFFF,&H00000000,&HD00B0E14,-1,0,0,0,100,100,0,0,3,2,0,8,60,60,1525,1",
        "Style: CTA,Arial Black,54,&H00FFFFFF,&H00FFFFFF,&H00000000,&HE00B0E14,-1,0,0,0,100,100,0,0,3,3,0,8,90,90,1450,1",
        "Style: Small,Arial Bold,28,&H80FFFFFF,&H80FFFFFF,&H80000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,7,28,28,28,1",
        "",
        "[Events]",
        "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
    ]

    for segment_name, events in CAPTIONS.items():
        base = starts[segment_name]
        for rel_start, rel_end, text, keyword in events:
            y = 1240 if segment_name in {"editorial_bridge", "story_cta"} else 1160
            body = f"{{\\an5\\pos(540,{y})}}{emphasized(text, keyword)}"
            lines.append(
                f"Dialogue: 8,{ass_time(base + rel_start)},{ass_time(base + rel_end)},Caption,,0,0,0,,{body}"
            )

    states = (
        (0.00, starts["email_reply"], "SIGNED  →  FIRED", RED),
        (starts["email_reply"], starts["failure_buffer"], "EMAIL  →  SEAT", GREEN),
        (starts["failure_buffer"], starts["two_million_offer"], "22 JOBS  →  NO FEAR", YELLOW),
        (starts["two_million_offer"], starts["sixty_six_payoff"], "$2M NOW  OR  WAIT?", YELLOW),
        (starts["sixty_six_payoff"], starts["loop_prep"], "WAIT  →  $66M", GREEN),
        (starts["loop_prep"], total_duration, "THE COMEBACK STARTS HERE", BLUE),
    )
    for start, end, text, color in states:
        lines.append(
            f"Dialogue: 6,{ass_time(start)},{ass_time(end)},State,,0,0,0,,"
            f"{{\\an8\\pos(540,225)\\c{ass_color(color)}\\fad(80,80)}}{text}"
        )

    cta = starts["story_cta"]
    cta_controls = (
        (0.00, 1.46, "LIKE • BACK THE COMEBACK", GREEN),
        (1.46, 2.56, "SUBSCRIBE • LEARN THE MOVE", BLUE),
        (2.56, 5.32, "COMMENT • $2M NOW OR WAIT?", YELLOW),
    )
    for start, end, text, color in cta_controls:
        lines.append(
            f"Dialogue: 9,{ass_time(cta + start)},{ass_time(cta + end)},CTA,,0,0,0,,"
            f"{{\\an8\\pos(540,410)\\c{ass_color(color)}\\fad(80,80)}}{text}"
        )

    lines.append(
        f"Dialogue: 9,{ass_time(starts['editorial_bridge'])},{ass_time(ends['story_cta'])},Small,,0,0,0,,"
        "{\\an3\\pos(1035,1870)}ILLUSTRATION • PEXELS 6608213"
    )

    thirds = [0.0, total_duration / 3, 2 * total_duration / 3, total_duration]
    positions = [(44, 70), (770, 70), (44, 1840)]
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
        f"[0:a]volume=0.014,afade=t=in:st=0:d=1,afade=t=out:st={duration - 1:.3f}:d=1[a0];"
        f"[1:a]volume=0.007,afade=t=in:st=0:d=1,afade=t=out:st={duration - 1:.3f}:d=1[a1];"
        "[a0][a1]amix=inputs=2:duration=longest:normalize=0,"
        "aformat=sample_fmts=s16:sample_rates=48000:channel_layouts=stereo[aout]",
        "-map", "[aout]", "-c:a", "pcm_s16le", output,
    ])
    return output


def generate_sfx() -> dict[str, Path]:
    click = AUDIO_DIR / "type_click.wav"
    cash = AUDIO_DIR / "cash_chime.wav"
    whoosh = AUDIO_DIR / "whoosh.wav"
    run([
        "ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
        "anoisesrc=color=white:sample_rate=48000:duration=0.10:amplitude=0.22",
        "-af", "highpass=f=1500,lowpass=f=6500,afade=t=out:st=0.03:d=0.07,aformat=channel_layouts=stereo",
        "-c:a", "pcm_s16le", click,
    ])
    run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "lavfi", "-i", "sine=frequency=880:sample_rate=48000:duration=0.34",
        "-f", "lavfi", "-i", "sine=frequency=1320:sample_rate=48000:duration=0.28",
        "-filter_complex", "[0:a]volume=0.22[a0];[1:a]volume=0.14,adelay=70|70[a1];[a0][a1]amix=inputs=2:normalize=0,afade=t=out:st=0.18:d=0.16,aformat=channel_layouts=stereo[out]",
        "-map", "[out]", "-c:a", "pcm_s16le", cash,
    ])
    run([
        "ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
        "anoisesrc=color=pink:sample_rate=48000:duration=0.40:amplitude=0.18",
        "-af", "highpass=f=450,lowpass=f=5000,afade=t=in:st=0:d=0.08,afade=t=out:st=0.16:d=0.24,aformat=channel_layouts=stereo",
        "-c:a", "pcm_s16le", whoosh,
    ])
    return {"click": click, "cash": cash, "whoosh": whoosh}


def make_positioned_track(
    source: Path, start: float, total_duration: float, output: Path, source_filter: str
) -> Path:
    if start <= 0:
        run([
            "ffmpeg", "-y", "-v", "error", "-i", source,
            "-filter_complex",
            f"[0:a]aresample=48000,aformat=channel_layouts=stereo,{source_filter},"
            f"apad,atrim=0:{total_duration:.6f}[out]",
            "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", output,
        ])
    else:
        run([
            "ffmpeg", "-y", "-v", "error",
            "-f", "lavfi", "-t", f"{start:.6f}", "-i", "anullsrc=r=48000:cl=stereo",
            "-i", source,
            "-filter_complex",
            f"[1:a]aresample=48000,aformat=channel_layouts=stereo,{source_filter}[clip];"
            f"[0:a][clip]concat=n=2:v=0:a=1,apad,atrim=0:{total_duration:.6f}[out]",
            "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", output,
        ])
    return output


def build_timed_audio(total_duration: float, starts: dict[str, float]) -> Path:
    generated = generate_sfx()
    definitions = (
        ("hook", TING, 0.08, "volume=0.40"),
        ("fired", BUZZ, starts["hook_fired"] + 3.90, "volume=0.25"),
        ("email", generated["click"], starts["email_reply"] + 2.95, "volume=0.55"),
        ("won", TING, starts["seat_won"] + 7.42, "volume=0.30"),
        ("typing_prelap", generated["click"], starts["editorial_bridge"] - 0.18, "volume=0.60"),
        ("offer_reject", BUZZ, starts["two_million_offer"] + 3.85, "volume=0.22"),
        ("cta_like", TING, starts["story_cta"] + 0.02, "volume=0.18"),
        ("cta_sub", TING, starts["story_cta"] + 1.46, "volume=0.16"),
        ("cta_comment", generated["click"], starts["story_cta"] + 2.54, "volume=0.42"),
        ("cash_prelap", generated["cash"], starts["sixty_six_payoff"] - 0.20, "volume=0.48"),
        ("proof", TING, starts["cash_in_a_day"] + 0.04, "volume=0.28"),
        ("loop", generated["whoosh"], starts["loop_prep"] + 0.02, "volume=0.36"),
    )
    tracks: list[Path] = []
    for name, source, start, source_filter in definitions:
        tracks.append(
            make_positioned_track(
                source, max(0.0, start), total_duration,
                AUDIO_DIR / f"positioned_{name}.wav", source_filter,
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
        f"{labels}amix=inputs={len(tracks)}:duration=longest:normalize=0,atrim=0:{total_duration:.6f}[out]",
        "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", output,
    ])
    return output


def overlay_prepare(index: int, width: int, height: int, start: float, end: float) -> str:
    return (
        f"[{index}:v]scale={width}:{height}:flags=lanczos,format=rgba,"
        f"fade=t=in:st={start:.3f}:d=0.16:alpha=1,"
        f"fade=t=out:st={max(start, end - 0.18):.3f}:d=0.18:alpha=1"
    )


def final_composite(
    base: Path,
    timeline: list[dict[str, Any]],
    total_frames: int,
    state_cards: list[Path],
    email_proof: Path,
    decision_cards: list[Path],
    sale_proof: Path,
    ass_file: Path,
    music: Path,
) -> None:
    starts = {item["name"]: item["final_start"] for item in timeline}
    ends = {item["name"]: item["final_end"] for item in timeline}
    total_duration = total_frames / FPS
    timed_audio = build_timed_audio(total_duration, starts)
    ass_escaped = str(ass_file).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")

    state_windows = (
        (0.08, starts["email_reply"] - 0.05),
        (starts["email_reply"], starts["failure_buffer"] - 0.05),
        (starts["failure_buffer"], starts["editorial_bridge"] - 0.05),
    )
    email_window = (starts["email_reply"] + 1.20, ends["seat_won"] - 0.25)
    decision_window = (starts["two_million_offer"], ends["story_cta"])
    payoff_window = (starts["sixty_six_payoff"], ends["sixty_six_payoff"])
    sale_window = (starts["cash_in_a_day"] + 0.10, ends["cash_in_a_day"] - 0.25)

    graph: list[str] = []
    for offset, (start, end) in enumerate(state_windows, start=1):
        graph.append(overlay_prepare(offset, 370, 317, start, end) + f"[s{offset - 1}]")
    graph.append(overlay_prepare(4, 430, 284, *email_window) + "[email]")
    graph.append(overlay_prepare(5, 455, 281, *decision_window) + "[decision0]")
    graph.append(overlay_prepare(6, 455, 281, *payoff_window) + "[decision1]")
    graph.append(overlay_prepare(7, 430, 301, *sale_window) + "[sale]")
    graph.extend([
        f"[0:v][s0]overlay=x=650:y=330:eof_action=pass:enable='between(t,{state_windows[0][0]:.3f},{state_windows[0][1]:.3f})'[v1]",
        f"[v1][s1]overlay=x=650:y=330:eof_action=pass:enable='between(t,{state_windows[1][0]:.3f},{state_windows[1][1]:.3f})'[v2]",
        f"[v2][s2]overlay=x=650:y=330:eof_action=pass:enable='between(t,{state_windows[2][0]:.3f},{state_windows[2][1]:.3f})'[v3]",
        f"[v3][email]overlay=x=620:y=350:eof_action=pass:enable='between(t,{email_window[0]:.3f},{email_window[1]:.3f})'[v4]",
        f"[v4][decision0]overlay=x=595:y=340:eof_action=pass:enable='between(t,{decision_window[0]:.3f},{decision_window[1]:.3f})'[v5]",
        f"[v5][decision1]overlay=x=595:y=340:eof_action=pass:enable='between(t,{payoff_window[0]:.3f},{payoff_window[1]:.3f})'[v6]",
        f"[v6][sale]overlay=x=620:y=345:eof_action=pass:enable='between(t,{sale_window[0]:.3f},{sale_window[1]:.3f})'[v7]",
        f"[v7]subtitles='{ass_escaped}':fontsdir='{FONT_KOMIKA.parent}',format=yuv420p[vout]",
        "[0:a]aresample=48000,aformat=channel_layouts=stereo[basea]",
        "[8:a]aresample=48000,aformat=channel_layouts=stereo[timed]",
        "[9:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.13[music]",
        f"[basea][timed][music]amix=inputs=3:duration=longest:normalize=0,atrim=0:{total_duration:.6f},"
        "loudnorm=I=-16.5:TP=-1.5:LRA=10,volume=-0.7dB,alimiter=limit=0.84:level=false[aout]",
    ])
    script = WORK / "final.ffscript"
    script.write_text(";\n".join(graph) + "\n", encoding="utf-8")

    FINAL.parent.mkdir(parents=True, exist_ok=True)
    png_duration = total_duration + 1.0
    pngs = [*state_cards, email_proof, *decision_cards, sale_proof]
    inputs: list[str | Path] = ["-i", base]
    for path in pngs:
        inputs.extend(["-loop", "1", "-t", f"{png_duration:.3f}", "-i", path])
    inputs.extend(["-i", timed_audio, "-i", music])
    run([
        "ffmpeg", "-y", "-v", "error", *inputs,
        "-filter_complex_script", script, "-map", "[vout]", "-map", "[aout]",
        "-frames:v", str(total_frames), *encode_args(),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart", "-t", f"{total_duration:.6f}", FINAL,
    ])


def validate_final(timeline: list[dict[str, Any]]) -> dict[str, Any]:
    data = probe(FINAL)
    video = next(stream for stream in data["streams"] if stream["codec_type"] == "video")
    audio = next(stream for stream in data["streams"] if stream["codec_type"] == "audio")
    duration = float(data["format"]["duration"])
    source_segments = [item for item in timeline if item["kind"] != "narration"]
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
        "triple_source_mix": SOURCE.exists() and PEXELS_EMAIL.exists() and len(list(PANELS.glob("*.png"))) >= 7,
        "commentary_track": BRIDGE_AUDIO.exists() and CTA_AUDIO.exists(),
        "cta_window": 38.0 <= cta_start <= 42.0,
        "caption_at_frame_zero": CAPTIONS["hook_fired"][0][0] <= 0.2,
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
    (WORK / "timeline.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def require_inputs() -> None:
    required = (
        SOURCE, PEXELS_EMAIL, BRIDGE_AUDIO, CTA_AUDIO, TING, BUZZ,
        FONT_KOMIKA, FONT_BOLD, FONT_BLACK,
    )
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required inputs:\n" + "\n".join(missing))
    for segment in SEGMENTS:
        if segment.kind != "narration" and segment.duration >= 15.0:
            raise ValueError(f"Every source segment must be below 15 seconds: {segment.name}")
        if segment.kind == "narration" and segment.audio is None:
            raise ValueError(f"Narration audio missing: {segment.name}")


def main() -> None:
    require_inputs()
    for directory in (WORK, SEGMENT_DIR, PANELS, CHECKS, AUDIO_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    base, timeline, total_frames = build_base()
    total_duration = total_frames / FPS
    state_cards = make_state_cards()
    email_proof = make_email_proof()
    decision_cards = make_decision_cards()
    sale_proof = make_sale_proof()
    ass_file = write_ass(timeline, total_duration)
    music = generate_music(total_duration)
    final_composite(
        base, timeline, total_frames, state_cards, email_proof,
        decision_cards, sale_proof, ass_file, music,
    )
    report = validate_final(timeline)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
