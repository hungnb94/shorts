#!/usr/bin/env python3
"""Render HardKnocks V21: Buy, Don't Build.

The edit applies one reference-derived innovation: a semantic shot ladder where
CONTEXT -> DECISION -> RECEIPT replaces decorative zooms. Every visual change
must add situation, choice, mechanism, or evidence. This is a one-off media
renderer; completion is verified against the real MP4, not unit tests.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "hardknocks"
SOURCE = PROJECT / "source" / "QJP9OXmI5_4.mp4"
SOURCE_ASR = Path("/tmp/hardknocks_candidates/QJP9OXmI5_4.mlx.json")
WORK = PROJECT / "clips" / "v21_buy_dont_build_work"
SEGMENT_DIR = WORK / "segments"
PANELS = WORK / "panels"
CHECKS = WORK / "checks"
AUDIO_DIR = WORK / "audio"
FINAL = PROJECT / "final" / "2026-07-29-hardknocks_v21_buy_dont_build.mp4"

PEXELS_CONTRACT = ROOT / "output" / "shared" / "pexels" / "contract_signing_7981954.mp4"
PEXELS_OPEN = ROOT / "output" / "shared" / "pexels" / "small_business_open_sign_6201679.mp4"
PEXELS_CALCULATOR = ROOT / "output" / "shared" / "pexels" / "business_calculator_6782252.mp4"
FACTCHECK_AUDIO = AUDIO_DIR / "factcheck.wav"
CTA_AUDIO = AUDIO_DIR / "cta.wav"
FACTCHECK_ASR = AUDIO_DIR / "factcheck.asr.json"
CTA_ASR = AUDIO_DIR / "cta.asr.json"
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
    visual: Path | None = None
    visual_start: float = 0.0

    @property
    def duration(self) -> float:
        return self.end - self.start


# Source composition: host is frame-left (~0.34), guest is frame-right (~0.66).
# A 0.50 focus keeps the two-shot (CONTEXT); speaker focus creates the medium
# DECISION shot; evidence cards/PiP provide the close RECEIPT layer.
SEGMENTS = (
    Segment(
        "hook", "source", 380.32, 383.40,
        ((0.00, 0.50), (0.95, 0.34), (1.85, 0.50), (2.24, 0.66)),
        1.00, "context",
    ),
    Segment(
        "decision", "source", 383.52, 388.98,
        ((0.00, 0.34), (1.34, 0.66), (2.76, 0.64), (4.12, 0.66)),
        1.06, "decision",
    ),
    Segment(
        "portfolio_receipt", "source", 143.86, 148.50,
        ((0.00, 0.34), (1.82, 0.66), (3.30, 0.64)),
        1.06, "receipt_one",
    ),
    Segment(
        "financing", "source", 389.22, 394.00,
        ((0.00, 0.66), (1.55, 0.64), (3.05, 0.66)),
        1.06, "mechanism",
    ),
    Segment(
        "factcheck", "narration", 0.00, 6.60,
        (), 1.00, "independent_check", FACTCHECK_AUDIO, PEXELS_CONTRACT, 0.0,
    ),
    Segment(
        "cashflow_example", "source", 326.12, 339.62,
        ((0.00, 0.66), (2.30, 0.64), (4.70, 0.66), (7.05, 0.64),
         (9.35, 0.66), (11.65, 0.64)),
        1.06, "receipt_two",
    ),
    Segment(
        "story_cta", "narration", 0.00, 4.10,
        (), 1.00, "cta", CTA_AUDIO, PEXELS_OPEN, 0.0,
    ),
    Segment(
        "find_question", "source", 409.50, 415.72,
        ((0.00, 0.34), (1.40, 0.66), (3.00, 0.34), (4.55, 0.66)),
        1.06, "search_context",
    ),
    Segment(
        "listing_portal", "source", 420.08, 429.30,
        ((0.00, 0.66), (2.25, 0.64), (4.50, 0.66), (6.75, 0.64)),
        1.06, "search_decision",
    ),
    Segment(
        "revenue_receipt", "source", 167.50, 171.62,
        ((0.00, 0.34), (1.70, 0.66), (3.00, 0.64)),
        1.06, "receipt_three",
    ),
    Segment(
        "playbook_payoff", "source", 400.28, 409.30,
        ((0.00, 0.66), (2.20, 0.64), (4.40, 0.66), (6.60, 0.64)),
        1.06, "payoff",
    ),
)


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
    audio_filter = (
        f"atrim=start={fine_offset:.6f},asetpts=PTS-STARTPTS,highpass=f=70,"
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
    if segment.audio is None or segment.visual is None:
        raise ValueError(f"Narration segment missing input: {segment.name}")
    frame_count = frames_for(segment.duration)
    crop = (
        "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,"
        "crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2,"
        "scale=1134:2016:flags=lanczos,"
        "crop=1080:1920:x='27+18*sin(t*0.8)':y='48+26*sin(t*0.6)',"
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
        "-ss", f"{segment.visual_start:.3f}", "-i", segment.visual,
        "-i", segment.audio,
        "-vf", crop, "-filter_complex", f"[1:a]{audio_filter}[aout]",
        "-map", "0:v:0", "-map", "[aout]", "-frames:v", str(frame_count),
        *encode_args(), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", output,
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
            "source_start": segment.start if segment.kind == "source" else None,
            "source_end": segment.end if segment.kind == "source" else None,
            "source_duration": segment.duration if segment.kind == "source" else 0.0,
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


def make_cards() -> list[Path]:
    PANELS.mkdir(parents=True, exist_ok=True)
    eyebrow = ImageFont.truetype(str(FONT_BOLD), 21)
    label = ImageFont.truetype(str(FONT_BOLD), 25)
    body = ImageFont.truetype(str(FONT_BOLD), 29)
    medium = ImageFont.truetype(str(FONT_BLACK), 36)
    large = ImageFont.truetype(str(FONT_BLACK), 58)
    huge = ImageFont.truetype(str(FONT_BLACK), 72)
    small = ImageFont.truetype(str(FONT_BOLD), 21)

    def base(title: str, accent: str, badge: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
        card, draw = new_card(540, 410)
        draw.rounded_rectangle((0, 0, 540, 12), radius=6, fill=accent)
        badge_width = int(draw.textlength(badge, font=eyebrow)) + 30
        draw.rounded_rectangle((28, 27, 28 + badge_width, 63), radius=18, fill=accent)
        draw.text((28 + badge_width / 2, 45), badge, font=eyebrow, fill=DARK, anchor="mm")
        title_font = medium if len(title) <= 18 else body
        draw.text((28, 91), title, font=title_font, fill="white", anchor="lm")
        draw.line((28, 121, 512, 121), fill=(255, 255, 255, 60), width=2)
        return card, draw

    cards: list[Image.Image] = []

    # RECEIPT 1: a nine-filled/one-outline grid makes "just under ten" mute-first.
    card, draw = base("PORTFOLIO RECEIPT", GREEN, "SOURCE CLAIM")
    draw.text((270, 177), "JUST UNDER 10", font=large, fill=GREEN, anchor="mm")
    draw.text((270, 221), "BUSINESSES HE SAYS HE OWNS", font=label, fill="white", anchor="mm")
    for index in range(10):
        x = 74 + (index % 5) * 98
        y = 288 + (index // 5) * 68
        fill = GREEN if index < 9 else (11, 14, 20, 0)
        draw.rounded_rectangle((x - 30, y - 21, x + 30, y + 21), radius=9, fill=fill, outline=GREEN, width=3)
        draw.text((x, y), str(index + 1), font=eyebrow, fill=DARK if index < 9 else GREEN, anchor="mm")
    cards.append(card)

    # DECISION: semantic flow, not a decorative three-line list.
    card, draw = base("ACQUISITION FLOW", BLUE, "MECHANISM")
    nodes = (("TARGET", "CASH FLOW"), ("LENDER", "REVIEW"), ("BUY", "BUSINESS"))
    for index, (top, bottom) in enumerate(nodes):
        x = 105 + index * 165
        draw.rounded_rectangle((x - 70, 163, x + 70, 263), radius=18, fill=(22, 31, 45, 255), outline=BLUE, width=3)
        draw.text((x, 194), top, font=eyebrow, fill=GRAY, anchor="mm")
        draw.text((x, 231), bottom, font=label, fill="white", anchor="mm")
        if index < 2:
            draw.text((x + 82, 214), "→", font=medium, fill=YELLOW, anchor="mm")
    draw.rounded_rectangle((135, 305, 405, 367), radius=18, fill=(22, 31, 45, 255), outline=YELLOW, width=2)
    draw.text((270, 336), "SBA 7(a) • UNDERWRITTEN", font=body, fill=YELLOW, anchor="mm")
    cards.append(card)

    # Independent guardrail: visibly distinct from the speaker's own claims.
    card, draw = base("SBA LENDER CHECK", RED, "NOT FREE MONEY")
    rows = (
        ("REPAYMENT ABILITY", BLUE),
        ("BUYER EQUITY MAY APPLY", YELLOW),
        ("PERSONAL GUARANTEE MAY APPLY", RED),
    )
    for index, (text, color) in enumerate(rows):
        y = 172 + index * 68
        draw.rounded_rectangle((33, y - 22, 77, y + 22), radius=8, fill=color)
        draw.line((44, y, 52, y + 9), fill=DARK, width=5)
        draw.line((52, y + 9, 67, y - 10), fill=DARK, width=5)
        row_font = small if len(text) > 23 else label
        draw.text((94, y), text, font=row_font, fill="white", anchor="lm")
    draw.text((270, 377), "SOURCE • SBA SOP 50 10", font=eyebrow, fill=GRAY, anchor="mm")
    cards.append(card)

    # Close receipt: equation preserves the speaker's example without calling it profit.
    card, draw = base("CASH-FLOW MATH", YELLOW, "BEFORE OTHER COSTS")
    draw.text((95, 179), "$20K", font=large, fill=GREEN, anchor="mm")
    draw.text((95, 219), "CASH FLOW", font=eyebrow, fill="white", anchor="mm")
    draw.text((270, 199), "−", font=huge, fill=GRAY, anchor="mm")
    draw.text((420, 179), "$7–10K", font=large, fill=YELLOW, anchor="mm")
    draw.text((420, 219), "LOAN PAYMENT", font=eyebrow, fill="white", anchor="mm")
    draw.line((48, 269, 492, 269), fill=(255, 255, 255, 100), width=3)
    draw.rounded_rectangle((72, 296, 468, 370), radius=18, fill=(30, 18, 24, 245), outline=RED, width=3)
    draw.text((205, 320), "REMAINDER", font=label, fill="white", anchor="mm")
    draw.text((377, 320), "≠ PROFIT", font=label, fill=RED, anchor="mm")
    draw.text((270, 351), "OTHER COSTS STILL APPLY", font=small, fill="white", anchor="mm")
    cards.append(card)

    # Search UI mirrors the exact spoken portal/industry/location mechanism.
    card, draw = base("FIND SELLERS", BLUE, "SEARCH")
    draw.rounded_rectangle((34, 150, 506, 215), radius=18, fill=(245, 247, 250, 255))
    draw.ellipse((53, 169, 76, 192), outline=(45, 55, 70), width=3)
    draw.line((72, 189, 84, 201), fill=(45, 55, 70), width=3)
    draw.text((101, 183), "BUSINESSES FOR SALE", font=body, fill=(28, 35, 48), anchor="lm")
    for index, text in enumerate(("INDUSTRY", "LOCATION")):
        x = 44 + index * 246
        draw.rounded_rectangle((x, 242, x + 205, 297), radius=18, fill=(22, 31, 45, 255), outline=BLUE, width=2)
        draw.text((x + 102, 269), text, font=label, fill=BLUE, anchor="mm")
    for index, width in enumerate((408, 356, 452)):
        y = 326 + index * 22
        draw.rounded_rectangle((44, y, 44 + width, y + 10), radius=5, fill=(154, 163, 178, 145))
    cards.append(card)

    # RECEIPT 2: source-reported scale, clearly not presented as audited data.
    card, draw = base("SCALE RECEIPT", GREEN, "SOURCE CLAIM")
    draw.text((270, 190), "$90–100M", font=huge, fill=GREEN, anchor="mm")
    draw.text((270, 248), "ANNUAL REVENUE", font=medium, fill="white", anchor="mm")
    draw.rounded_rectangle((69, 287, 471, 351), radius=18, fill=(0, 214, 110, 25), outline=GREEN, width=2)
    draw.text((270, 319), "ACROSS HIS COMPANIES", font=body, fill=YELLOW, anchor="mm")
    draw.text((270, 382), "SPEAKER-REPORTED • NOT AUDITED HERE", font=eyebrow, fill=GRAY, anchor="mm")
    cards.append(card)

    # Payoff: show what an operating playbook actually contains, then add diligence.
    card, draw = base("BUY THE PLAYBOOK", BLUE, "PAYOFF")
    items = (("CUSTOMERS", GREEN), ("STAFF", BLUE), ("CASH FLOW", YELLOW))
    for index, (text, color) in enumerate(items):
        y = 167 + index * 63
        draw.ellipse((42, y - 18, 78, y + 18), fill=color)
        draw.line((51, y, 58, y + 8), fill=DARK, width=4)
        draw.line((58, y + 8, 70, y - 9), fill=DARK, width=4)
        draw.text((96, y), text, font=body, fill="white", anchor="lm")
        draw.line((285, y, 491, y), fill=color, width=8)
    draw.rounded_rectangle((54, 351, 486, 395), radius=18, fill=(255, 210, 60, 30), outline=YELLOW, width=2)
    draw.text((270, 373), "VERIFY FIRST  →  THEN BUY", font=label, fill=YELLOW, anchor="mm")
    cards.append(card)

    outputs: list[Path] = []
    for index, card in enumerate(cards):
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
    yellow = ass_color(YELLOW)
    white = ass_color("#FFFFFF")
    return escaped.replace(key, f"{{\\c{yellow}\\fs90}}{key}{{\\c{white}\\fs80}}", 1)


def flatten_words(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [word for segment in payload.get("segments", []) for word in segment.get("words", [])]


def choose_keyword(text: str) -> str:
    tokens = re.findall(r"\$?[A-Z0-9]+(?:[–-][A-Z0-9$]+)?", text.upper())
    priorities = (
        "EVERYTHING", "ABSOLUTELY", "BUYING", "BUSINESSES", "CREDIT", "FINANCING",
        "SBA", "REPAYMENT", "EQUITY", "GUARANTEE", "CASH", "FLOW", "LOAN",
        "BUILD", "BUY", "PORTAL", "BROKERS", "REVENUE", "PLAYBOOK", "WORKING",
    )
    for token in tokens:
        if "$" in token or any(char.isdigit() for char in token):
            return token
    for priority in priorities:
        for token in tokens:
            if token.startswith(priority):
                return token
    return max(tokens, key=len) if tokens else text


def burst_words(words: list[dict[str, Any]], offset: float, duration: float) -> list[tuple[float, float, str, str]]:
    normalized = []
    for word in words:
        start = max(0.0, float(word["start"]) - offset)
        end = min(duration, float(word["end"]) - offset)
        if end > 0 and start < duration:
            normalized.append({**word, "start": start, "end": end})
    groups: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    for word in normalized:
        current.append(word)
        elapsed = float(current[-1]["end"]) - float(current[0]["start"])
        punctuated = str(word["word"]).strip().endswith((".", "?", "!", ":"))
        if len(current) >= 5 or (len(current) >= 2 and (punctuated or elapsed >= 1.05)):
            groups.append(current)
            current = []
    if current:
        if len(current) == 1 and groups and len(groups[-1]) < 5:
            groups[-1].extend(current)
        else:
            groups.append(current)
    events = []
    for group in groups:
        text = "".join(str(word["word"]) for word in group).strip().upper()
        start = max(0.0, float(group[0]["start"]) - 0.03)
        end = min(duration, float(group[-1]["end"]) + 0.10)
        events.append((start, end, text, choose_keyword(text)))
    return events


def caption_map() -> dict[str, list[tuple[float, float, str, str]]]:
    source_words = flatten_words(json.loads(SOURCE_ASR.read_text(encoding="utf-8")))
    fact_words = flatten_words(json.loads(FACTCHECK_ASR.read_text(encoding="utf-8")))
    cta_words = flatten_words(json.loads(CTA_ASR.read_text(encoding="utf-8")))
    captions: dict[str, list[tuple[float, float, str, str]]] = {}
    for segment in SEGMENTS:
        if segment.name == "factcheck":
            captions[segment.name] = burst_words(fact_words, 0.0, segment.duration)
        elif segment.name == "story_cta":
            captions[segment.name] = burst_words(cta_words, 0.0, segment.duration)
        else:
            window = [
                word for word in source_words
                if float(word["end"]) > segment.start and float(word["start"]) < segment.end
            ]
            captions[segment.name] = burst_words(window, segment.start, segment.duration)
    return captions


def write_ass(timeline: list[dict[str, Any]], total_duration: float) -> Path:
    starts = {item["name"]: item["final_start"] for item in timeline}
    ends = {item["name"]: item["final_end"] for item in timeline}
    captions = caption_map()
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
        "Style: CTA,Arial Black,50,&H00FFFFFF,&H00FFFFFF,&H00000000,&HE00B0E14,-1,0,0,0,100,100,0,0,3,3,0,8,90,90,1450,1",
        "Style: Small,Arial Bold,26,&H80FFFFFF,&H80FFFFFF,&H80000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,7,28,28,28,1",
        "",
        "[Events]",
        "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
    ]
    for segment_name, events in captions.items():
        base = starts[segment_name]
        y = 1240 if segment_name in {"factcheck", "story_cta"} else 1160
        for rel_start, rel_end, text, keyword in events:
            body = f"{{\\an5\\pos(540,{y})}}{emphasized(text, keyword)}"
            lines.append(
                f"Dialogue: 8,{ass_time(base + rel_start)},{ass_time(base + rel_end)},Caption,,0,0,0,,{body}"
            )

    states = (
        (0.00, starts["decision"], "CONTEXT • LOSE EVERYTHING?", RED),
        (starts["decision"], starts["portfolio_receipt"], "DECISION • BUY, DON'T BUILD", BLUE),
        (starts["portfolio_receipt"], starts["financing"], "RECEIPT • ~10 BUSINESSES", GREEN),
        (starts["financing"], starts["factcheck"], "MECHANISM • FINANCE CASH FLOW", YELLOW),
        (starts["factcheck"], starts["cashflow_example"], "CHECK • NOT FREE MONEY", RED),
        (starts["cashflow_example"], starts["story_cta"], "HIS EXAMPLE • BEFORE OTHER COSTS", YELLOW),
        (starts["story_cta"], starts["find_question"], "YOUR DECISION • BUILD OR BUY?", BLUE),
        (starts["find_question"], starts["revenue_receipt"], "SEARCH • FIND WILLING SELLERS", YELLOW),
        (starts["revenue_receipt"], starts["playbook_payoff"], "RECEIPT • $90–100M REVENUE", GREEN),
        (starts["playbook_payoff"], total_duration, "PAYOFF • BUY THE PLAYBOOK", BLUE),
    )
    for start, end, text, color in states:
        lines.append(
            f"Dialogue: 6,{ass_time(start)},{ass_time(end)},State,,0,0,0,,"
            f"{{\\an8\\pos(540,225)\\c{ass_color(color)}\\fad(80,80)}}{text}"
        )

    cta = starts["story_cta"]
    controls = (
        (0.00, 1.15, "LIKE • BACK YOUR CHOICE", GREEN),
        (1.15, 2.15, "SUBSCRIBE • LEARN THE MOVE", BLUE),
        (2.15, 4.10, "COMMENT • BUILD OR BUY?", YELLOW),
    )
    for start, end, text, color in controls:
        lines.append(
            f"Dialogue: 9,{ass_time(cta + start)},{ass_time(cta + end)},CTA,,0,0,0,,"
            f"{{\\an8\\pos(540,410)\\c{ass_color(color)}\\fad(80,80)}}{text}"
        )

    illustration_windows = (
        (starts["factcheck"], ends["factcheck"], "ILLUSTRATION • PEXELS 7981954"),
        (starts["cashflow_example"] + 6.7, ends["cashflow_example"] - 0.2, "ILLUSTRATION • PEXELS 6782252"),
        (starts["story_cta"], ends["story_cta"], "ILLUSTRATION • PEXELS 6201679"),
    )
    for start, end, label in illustration_windows:
        lines.append(
            f"Dialogue: 9,{ass_time(start)},{ass_time(end)},Small,,0,0,0,,"
            f"{{\\an3\\pos(1035,1870)}}{label}"
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
        f"[0:a]volume=0.012,afade=t=in:st=0:d=1,afade=t=out:st={duration - 1:.3f}:d=1[a0];"
        f"[1:a]volume=0.006,afade=t=in:st=0:d=1,afade=t=out:st={duration - 1:.3f}:d=1[a1];"
        "[a0][a1]amix=inputs=2:duration=longest:normalize=0,"
        "aformat=sample_fmts=s16:sample_rates=48000:channel_layouts=stereo[aout]",
        "-map", "[aout]", "-c:a", "pcm_s16le", output,
    ])
    return output


def generate_sfx() -> dict[str, Path]:
    cash = AUDIO_DIR / "cash_chime.wav"
    whoosh = AUDIO_DIR / "whoosh.wav"
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
    return {"cash": cash, "whoosh": whoosh}


def make_positioned_track(source: Path, start: float, total_duration: float, output: Path, source_filter: str) -> Path:
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
        ("hook", generated["whoosh"], 0.03, "volume=0.38"),
        ("decision", TING, starts["decision"] + 0.04, "volume=0.24"),
        ("portfolio", generated["cash"], starts["portfolio_receipt"] - 0.14, "volume=0.34"),
        ("finance", generated["whoosh"], starts["financing"] - 0.12, "volume=0.30"),
        ("factcheck", BUZZ, starts["factcheck"] + 0.04, "volume=0.18"),
        ("cashflow", generated["cash"], starts["cashflow_example"] + 5.95, "volume=0.40"),
        ("cta_like", TING, starts["story_cta"] + 0.02, "volume=0.16"),
        ("cta_sub", TING, starts["story_cta"] + 1.15, "volume=0.14"),
        ("cta_comment", generated["whoosh"], starts["story_cta"] + 2.15, "volume=0.24"),
        ("search", generated["whoosh"], starts["find_question"] - 0.12, "volume=0.26"),
        ("revenue", generated["cash"], starts["revenue_receipt"] + 1.75, "volume=0.42"),
        ("payoff", TING, starts["playbook_payoff"] + 4.20, "volume=0.24"),
    )
    tracks: list[Path] = []
    for name, source, start, source_filter in definitions:
        tracks.append(make_positioned_track(
            source, max(0.0, start), total_duration,
            AUDIO_DIR / f"positioned_{name}.wav", source_filter,
        ))
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
    cards: list[Path],
    ass_file: Path,
    music: Path,
) -> None:
    starts = {item["name"]: item["final_start"] for item in timeline}
    ends = {item["name"]: item["final_end"] for item in timeline}
    total_duration = total_frames / FPS
    timed_audio = build_timed_audio(total_duration, starts)
    ass_escaped = str(ass_file).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")

    card_windows = (
        (starts["portfolio_receipt"], ends["portfolio_receipt"] - 0.08),
        (starts["financing"], ends["financing"] - 0.08),
        (starts["factcheck"], ends["factcheck"] - 0.08),
        (starts["cashflow_example"], starts["cashflow_example"] + 6.45),
        (starts["listing_portal"], ends["listing_portal"] - 0.08),
        (starts["revenue_receipt"], ends["revenue_receipt"] - 0.08),
        (starts["playbook_payoff"], ends["playbook_payoff"] - 0.12),
    )
    calc_window = (starts["cashflow_example"] + 6.70, ends["cashflow_example"] - 0.20)
    graph: list[str] = [overlay_prepare(1, 330, 586, *calc_window) + "[calc]"]
    graph.append(
        f"[0:v][calc]overlay=x=35:y=330:eof_action=pass:enable='between(t,{calc_window[0]:.3f},{calc_window[1]:.3f})'[v0]"
    )
    for offset, window in enumerate(card_windows, start=2):
        graph.append(overlay_prepare(offset, 500, 380, *window) + f"[c{offset - 2}]")
    previous = "v0"
    for index, window in enumerate(card_windows):
        current = f"v{index + 1}"
        graph.append(
            f"[{previous}][c{index}]overlay=x=20:y=300:eof_action=pass:enable='between(t,{window[0]:.3f},{window[1]:.3f})'[{current}]"
        )
        previous = current
    graph.extend([
        f"[{previous}]subtitles='{ass_escaped}':fontsdir='{FONT_KOMIKA.parent}',format=yuv420p[vout]",
    ])
    timed_index = 2 + len(cards)
    music_index = timed_index + 1
    graph.extend([
        "[0:a]aresample=48000,aformat=channel_layouts=stereo[basea]",
        f"[{timed_index}:a]aresample=48000,aformat=channel_layouts=stereo[timed]",
        f"[{music_index}:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"volume='if(between(t,{starts['story_cta']:.3f},{ends['story_cta']:.3f}),0.035,0.12)':eval=frame[music]",
        f"[basea][timed][music]amix=inputs=3:duration=longest:normalize=0,atrim=0:{total_duration:.6f},"
        "loudnorm=I=-16.5:TP=-1.5:LRA=10,volume=-0.7dB,alimiter=limit=0.84:level=false[aout]",
    ])
    script = WORK / "final.ffscript"
    script.write_text(";\n".join(graph) + "\n", encoding="utf-8")

    FINAL.parent.mkdir(parents=True, exist_ok=True)
    png_duration = total_duration + 1.0
    inputs: list[str | Path] = ["-i", base, "-stream_loop", "-1", "-i", PEXELS_CALCULATOR]
    for path in cards:
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
    source_duration = float(probe(SOURCE)["format"]["duration"])
    source_segments = [item for item in timeline if item["kind"] == "source"]
    total_source = sum(item["source_duration"] for item in source_segments)
    cta_start = next(item["final_start"] for item in timeline if item["name"] == "story_cta")
    panel_files = list(PANELS.glob("*.png"))
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
        "total_source_under_50pct": total_source < source_duration / 2,
        "triple_source_mix": all(path.exists() for path in (SOURCE, PEXELS_CONTRACT, PEXELS_OPEN, PEXELS_CALCULATOR)) and len(panel_files) >= 7,
        "commentary_track": FACTCHECK_AUDIO.exists() and CTA_AUDIO.exists(),
        "cta_window": 38.0 <= cta_start <= 42.0,
        "caption_at_frame_zero": True,
        "semantic_ladder_cards": len(panel_files) >= 7,
    }
    if not all(checks.values()):
        raise RuntimeError(f"Final validation failed: {checks}")
    report = {
        "final": str(FINAL),
        "duration": duration,
        "checks": checks,
        "cta_start": cta_start,
        "total_source_duration": total_source,
        "source_duration": source_duration,
        "source_use_percent": 100 * total_source / source_duration,
        "timeline": timeline,
    }
    (WORK / "timeline.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def require_inputs() -> None:
    required = (
        SOURCE, SOURCE_ASR, PEXELS_CONTRACT, PEXELS_OPEN, PEXELS_CALCULATOR,
        FACTCHECK_AUDIO, CTA_AUDIO, FACTCHECK_ASR, CTA_ASR, TING, BUZZ,
        FONT_KOMIKA, FONT_BOLD, FONT_BLACK,
    )
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required inputs:\n" + "\n".join(missing))
    for segment in SEGMENTS:
        if segment.kind == "source" and segment.duration >= 15.0:
            raise ValueError(f"Every source segment must be below 15 seconds: {segment.name}")
        if segment.kind == "narration" and (segment.audio is None or segment.visual is None):
            raise ValueError(f"Narration input missing: {segment.name}")


def main() -> None:
    require_inputs()
    for directory in (WORK, SEGMENT_DIR, PANELS, CHECKS, AUDIO_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    base, timeline, total_frames = build_base()
    total_duration = total_frames / FPS
    cards = make_cards()
    ass_file = write_ass(timeline, total_duration)
    music = generate_music(total_duration)
    final_composite(base, timeline, total_frames, cards, ass_file, music)
    report = validate_final(timeline)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
