#!/usr/bin/env python3
"""Render HardKnocks V29: The $20B Supply-Chain Trap."""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "hardknocks"
SOURCE = ROOT / "output" / "projects" / "dangote-supply-chain" / "source" / "master" / "jVs4NBoHZic-source-master.mp4"
SOURCE_DURATION = 2964.236190
WORK = PROJECT / "clips" / "v29_supply_chain_trap_work"
SEGMENT_DIR = WORK / "segments"
AUDIO_DIR = WORK / "audio" / "qwen-zack"
CHECKS = WORK / "checks"
OVERLAY = WORK / "overlay_v1_supply_chain.mov"
FINAL = PROJECT / "final" / "2026-08-04-hardknocks_v29_supply_chain_trap.mp4"
TIMELINE_JSON = WORK / "timeline.json"
HOOK_SCORECARD = WORK / "hook-strategy-scorecard.json"
ASSET_MANIFEST = WORK / "asset-manifest.json"

PEXELS_REFINERY = ROOT / "output" / "pexels" / "12891229.mp4"
PEXELS_PUMPJACK = ROOT / "output" / "pexels" / "10227529.mp4"

SFX_DIR = ROOT / "assets" / "sfx" / "generated" / "hardknocks_v22"
HOOK_HIT = SFX_DIR / "hook_origin_hit.wav"
WHOOSH = SFX_DIR / "jet_motion_whoosh.wav"
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
OW = 540
OH = 960
FPS = 30
BEAT = 1.5

WHITE = (248, 250, 252, 255)
DARK = (9, 13, 22, 236)
CYAN = (67, 212, 255, 255)
AMBER = (255, 184, 77, 255)
GREEN = (95, 225, 153, 255)
RED = (255, 92, 92, 255)
GRAY = (166, 177, 194, 255)


@dataclass(frozen=True)
class Segment:
    name: str
    kind: str
    duration: float
    act: str
    audio_id: str | None = None
    source_audio_start: float | None = None
    source_audio_duration: float | None = None
    source_visual_start: float | None = None
    visual: Path | None = None
    visual_start: float = 0.0
    illustration_label: str | None = None

    @property
    def audio(self) -> Path | None:
        return AUDIO_DIR / f"{self.audio_id}.wav" if self.audio_id else None

    @property
    def final_source_duration(self) -> float:
        return self.duration if self.kind in {"source_quote", "source", "narration_source"} else 0.0


SEGMENTS = (
    Segment(
        "export_import_quote", "source_quote", 7.5, "contradiction",
        source_audio_start=560.60, source_audio_duration=11.0, source_visual_start=565.0,
    ),
    Segment(
        "twenty_billion_question", "narration_stock", 4.5, "open_loop",
        audio_id="twenty_billion_question", visual=PEXELS_REFINERY, visual_start=0.0,
        illustration_label="ILLUSTRATION • PEXELS 12891229",
    ),
    Segment(
        "refinery_decision", "source", 6.0, "answer",
        source_audio_start=606.64, source_audio_duration=6.0, source_visual_start=606.64,
    ),
    Segment("backward_integration", "narration_card", 4.5, "mechanism", audio_id="backward_integration"),
    Segment(
        "control_prize", "narration_stock", 4.5, "value_pool", audio_id="control_prize",
        visual=PEXELS_REFINERY, visual_start=4.5, illustration_label="ILLUSTRATION • PEXELS 12891229",
    ),
    Segment(
        "nameplate_capacity", "narration_stock", 6.0, "scale", audio_id="nameplate_capacity",
        visual=PEXELS_REFINERY, visual_start=9.0, illustration_label="ILLUSTRATION • PEXELS 12891229",
    ),
    Segment("risk_moved", "narration_card", 4.5, "reversal", audio_id="risk_moved"),
    Segment(
        "triple_cta", "narration_source", 4.5, "cta", audio_id="triple_cta",
        source_visual_start=606.64,
    ),
    Segment(
        "allocation_shortfall", "narration_stock", 6.0, "counter_evidence", audio_id="allocation_shortfall",
        visual=PEXELS_PUMPJACK, visual_start=7.0, illustration_label="ILLUSTRATION • PEXELS 10227529",
    ),
    Segment(
        "cargoes", "narration_stock", 6.0, "dependency", audio_id="cargoes",
        visual=PEXELS_PUMPJACK, visual_start=13.0, illustration_label="ILLUSTRATION • PEXELS 10227529",
    ),
    Segment("payoff", "narration_card", 6.0, "payoff", audio_id="payoff"),
    Segment(
        "loop_question", "narration_source", 4.5, "loop", audio_id="loop_question",
        source_visual_start=606.64,
    ),
)

CAPTIONS: dict[str, tuple[tuple[float, float, str, str], ...]] = {
    "export_import_quote": (
        (0.0, 1.5, "PRODUCE OIL", "OIL"),
        (1.5, 3.0, "BUT DON'T REFINE", "DON'T"),
        (3.0, 4.5, "EXPORT CRUDE OIL", "CRUDE"),
        (4.5, 6.0, "THEN IMPORT PRODUCTS", "IMPORT"),
        (6.0, 7.5, "IMPORTATION COSTS MONEY", "MONEY"),
    ),
    "twenty_billion_question": (
        (0.0, 1.5, "SO WHY BET", "WHY"),
        (1.5, 3.0, "TWENTY BILLION DOLLARS", "BILLION"),
        (3.0, 4.5, "ON ONE REFINERY?", "ONE"),
    ),
    "refinery_decision": (
        (0.0, 1.5, "I DECIDED", "DECIDED"),
        (1.5, 3.0, "TO MAKE A REFINERY", "REFINERY"),
        (3.0, 4.5, "THE BIGGEST EVER", "BIGGEST"),
        (4.5, 6.0, "IN THE WORLD", "WORLD"),
    ),
    "backward_integration": (
        (0.0, 1.5, "THIS IS", "THIS"),
        (1.5, 3.0, "BACKWARD INTEGRATION", "INTEGRATION"),
        (3.0, 4.5, "BUILD THE SUPPLIER", "BUILD"),
    ),
    "control_prize": (
        (0.0, 1.5, "YOU GAIN CONTROL", "CONTROL"),
        (1.5, 3.0, "TIMING + QUALITY", "QUALITY"),
        (3.0, 4.5, "AND EVENTUALLY COST", "COST"),
    ),
    "nameplate_capacity": (
        (0.0, 1.5, "NAMEPLATE CAPACITY", "CAPACITY"),
        (1.5, 3.0, "SIX HUNDRED FIFTY", "FIFTY"),
        (3.0, 4.5, "THOUSAND BARRELS", "THOUSAND"),
        (4.5, 6.0, "EVERY DAY", "DAY"),
    ),
    "risk_moved": (
        (0.0, 1.5, "BUT DEPENDENCY", "DEPENDENCY"),
        (1.5, 3.0, "DID NOT DISAPPEAR", "NOT"),
        (3.0, 4.5, "IT MOVED UPSTREAM", "UPSTREAM"),
    ),
    "triple_cta": (
        (0.0, 1.5, "WOULD YOU BUILD IT?", "YOU"),
        (1.5, 3.0, "LIKE + SUBSCRIBE", "SUBSCRIBE"),
        (3.0, 4.5, "COMMENT: CONTROL OR TRAP?", "COMMENT"),
    ),
    "allocation_shortfall": (
        (0.0, 1.5, "EARLY TWENTY TWENTY-SIX", "EARLY"),
        (1.5, 3.0, "LOCAL REFINERIES RECEIVED", "RECEIVED"),
        (3.0, 4.5, "JUST FORTY-SIX PERCENT", "FORTY-SIX"),
        (4.5, 6.0, "OF ALLOCATED CRUDE", "CRUDE"),
    ),
    "cargoes": (
        (0.0, 1.5, "DANGOTE STILL NEEDED", "NEEDED"),
        (1.5, 3.0, "THIRTEEN TO FIFTEEN", "FIFTEEN"),
        (3.0, 4.5, "CARGOES EACH MONTH", "CARGOES"),
        (4.5, 6.0, "AND IMPORTED THE REST", "IMPORTED"),
    ),
    "payoff": (
        (0.0, 1.5, "VERTICAL INTEGRATION", "INTEGRATION"),
        (1.5, 3.0, "MOVES THE BOTTLENECK", "MOVES"),
        (3.0, 4.5, "EVERY LINK YOU OWN", "OWN"),
        (4.5, 6.0, "MAKES THE BET BIGGER", "BIGGER"),
    ),
    "loop_question": (
        (0.0, 1.5, "SO WOULD YOU", "YOU"),
        (1.5, 3.0, "BUILD YOUR SUPPLIER?", "SUPPLIER"),
        (3.0, 4.5, "CONTROL OR TRAP?", "TRAP"),
    ),
}

HOOK_VARIANTS = (
    ("twenty_billion_trap", "$20B supply-chain trap", (10, 10, 9, 9, 9, 9)),
    ("export_import", "export crude then import fuel", (9, 10, 10, 8, 10, 9)),
    ("risk_reversal", "the refinery moved the risk", (10, 8, 8, 8, 10, 10)),
    ("own_bottleneck", "he built his supplier", (9, 9, 10, 8, 9, 9)),
    ("twenty_billion_question", "why risk $20B", (10, 9, 9, 8, 9, 8)),
    ("oil_rich_dependent", "oil-rich, fuel-dependent", (9, 9, 9, 8, 9, 8)),
    ("supplier_choke", "supplier can choke you", (9, 8, 8, 8, 9, 8)),
    ("missing_link", "he built the missing link", (9, 8, 9, 7, 9, 8)),
    ("capacity_bet", "650K-barrel bet", (8, 10, 8, 7, 8, 8)),
    ("forced_choice", "would you build your supplier", (8, 8, 7, 8, 9, 8)),
)


def run(command: list[str | Path], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(str(item) for item in command), flush=True)
    return subprocess.run([str(item) for item in command], cwd=ROOT, check=True, text=True, capture_output=capture)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def frames_for(seconds: float) -> int:
    return round(seconds * FPS)


def encode_args() -> list[str]:
    return [
        "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-g", "45", "-keyint_min", "45", "-sc_threshold", "0",
    ]


def source_crop() -> str:
    return (
        "scale=-1:1920:flags=lanczos,"
        "crop=1080:1920:x='(iw-1080)/2+18*sin(t*0.8)':y=0,"
        "eq=contrast=1.04:saturation=1.03,setsar=1,format=yuv420p,fps=30"
    )


def stock_crop() -> str:
    return (
        "scale=-1:1920:flags=lanczos,"
        "crop=1080:1920:x='(iw-1080)/2+22*sin(t*0.65)':y=0,"
        "eq=contrast=1.05:saturation=0.90,setsar=1,format=yuv420p,fps=30"
    )


def narration_filter(duration: float) -> str:
    return (
        "aresample=48000,aformat=channel_layouts=stereo,highpass=f=70,"
        "acompressor=threshold=0.1:ratio=4:attack=5:release=100:makeup=1,"
        "loudnorm=I=-16:TP=-1.5:LRA=10,apad,"
        f"atrim=0:{duration:.6f},afade=t=in:st=0:d=0.08,"
        f"afade=t=out:st={duration - 0.14:.6f}:d=0.14"
    )


def render_segment(segment: Segment, output: Path) -> int:
    frame_count = frames_for(segment.duration)
    if segment.duration % BEAT != 0:
        raise ValueError(f"Segment is off the 1.5s grid: {segment.name}")
    if segment.kind == "source_quote":
        assert segment.source_audio_start is not None
        assert segment.source_audio_duration is not None
        assert segment.source_visual_start is not None
        coarse = min(segment.source_audio_start, segment.source_visual_start) - 4.0
        audio_start = segment.source_audio_start - coarse
        visual_start = segment.source_visual_start - coarse
        tempo = segment.source_audio_duration / segment.duration
        graph = (
            f"[0:v]trim=start={visual_start:.6f}:end={visual_start + segment.duration:.6f},setpts=PTS-STARTPTS,{source_crop()}[v];"
            f"[0:a]atrim=start={audio_start:.6f}:end={audio_start + segment.source_audio_duration:.6f},asetpts=PTS-STARTPTS,"
            f"atempo={tempo:.8f},highpass=f=70,acompressor=threshold=0.125:ratio=2:attack=5:release=80:makeup=1.4,"
            f"loudnorm=I=-16:TP=-1.5:LRA=10,aresample=48000:first_pts=0,apad,atrim=0:{segment.duration:.6f}[a]"
        )
        run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{coarse:.6f}", "-i", SOURCE,
            "-filter_complex", graph, "-map", "[v]", "-map", "[a]", "-frames:v", str(frame_count),
            *encode_args(), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", output,
        ])
    elif segment.kind == "source":
        assert segment.source_audio_start is not None
        assert segment.source_visual_start is not None
        coarse = segment.source_audio_start - 4.0
        start = segment.source_audio_start - coarse
        graph = (
            f"[0:v]trim=start={start:.6f}:end={start + segment.duration:.6f},setpts=PTS-STARTPTS,{source_crop()}[v];"
            f"[0:a]atrim=start={start:.6f}:end={start + segment.duration:.6f},asetpts=PTS-STARTPTS,"
            "highpass=f=70,acompressor=threshold=0.125:ratio=2:attack=5:release=80:makeup=1.4,"
            f"loudnorm=I=-16:TP=-1.5:LRA=10,aresample=48000:first_pts=0,apad,atrim=0:{segment.duration:.6f}[a]"
        )
        run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{coarse:.6f}", "-i", SOURCE,
            "-filter_complex", graph, "-map", "[v]", "-map", "[a]", "-frames:v", str(frame_count),
            *encode_args(), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", output,
        ])
    elif segment.kind == "narration_source":
        assert segment.source_visual_start is not None and segment.audio is not None
        graph = f"[0:v]{source_crop()}[v];[1:a]{narration_filter(segment.duration)}[a]"
        run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{segment.source_visual_start:.6f}", "-i", SOURCE,
            "-i", segment.audio, "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
            "-frames:v", str(frame_count), *encode_args(), "-c:a", "aac", "-b:a", "192k",
            "-ar", "48000", "-ac", "2", output,
        ])
    elif segment.kind == "narration_stock":
        assert segment.visual is not None and segment.audio is not None
        graph = f"[0:v]{stock_crop()}[v];[1:a]{narration_filter(segment.duration)}[a]"
        run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{segment.visual_start:.6f}", "-i", segment.visual,
            "-i", segment.audio, "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
            "-frames:v", str(frame_count), *encode_args(), "-c:a", "aac", "-b:a", "192k",
            "-ar", "48000", "-ac", "2", output,
        ])
    elif segment.kind == "narration_card":
        assert segment.audio is not None
        graph = f"[0:v]format=yuv420p,fps=30[v];[1:a]{narration_filter(segment.duration)}[a]"
        run([
            "ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
            f"color=c=0x081120:s={WIDTH}x{HEIGHT}:r={FPS}:d={segment.duration:.6f}",
            "-i", segment.audio, "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
            "-frames:v", str(frame_count), *encode_args(), "-c:a", "aac", "-b:a", "192k",
            "-ar", "48000", "-ac", "2", output,
        ])
    else:
        raise ValueError(segment.kind)
    return frame_count


def build_base() -> tuple[Path, list[dict[str, Any]], int]:
    SEGMENT_DIR.mkdir(parents=True, exist_ok=True)
    cursor = 0
    timeline: list[dict[str, Any]] = []
    outputs: list[Path] = []
    for index, segment in enumerate(SEGMENTS):
        output = SEGMENT_DIR / f"{index:02d}_{segment.name}.mp4"
        count = render_segment(segment, output)
        start = cursor / FPS
        end = (cursor + count) / FPS
        timeline.append(
            {
                "name": segment.name,
                "kind": segment.kind,
                "act": segment.act,
                "final_start": start,
                "final_end": end,
                "duration": segment.duration,
                "start_frame": cursor,
                "end_frame": cursor + count,
                "frames": count,
                "source_audio_start": segment.source_audio_start,
                "source_audio_duration": segment.source_audio_duration,
                "source_visual_start": segment.source_visual_start,
                "source_duration": segment.final_source_duration,
                "visual": str(segment.visual.relative_to(ROOT)) if segment.visual else None,
                "visual_start": segment.visual_start,
                "illustration_label": segment.illustration_label,
            }
        )
        cursor += count
        outputs.append(output)
    concat = WORK / "concat.txt"
    concat.write_text("".join(f"file '{item.resolve()}'\n" for item in outputs), encoding="utf-8")
    base = WORK / "base.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat, "-c", "copy", base])
    return base, timeline, cursor


def ease(value: float) -> float:
    x = min(1.0, max(0.0, value))
    return x * x * (3.0 - 2.0 * x)


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], alpha: int = 232) -> None:
    draw.rounded_rectangle(box, radius=20, fill=(9, 13, 22, alpha), outline=(255, 255, 255, 90), width=2)


def centered_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.FreeTypeFont, fill: tuple[int, int, int, int]) -> None:
    draw.text(xy, text, font=font, fill=fill, stroke_width=2, stroke_fill=(0, 0, 0, 220), anchor="mm")


def fit_font(text: str, start: int, minimum: int = 26) -> ImageFont.FreeTypeFont:
    for size in range(start, minimum - 1, -1):
        font = ImageFont.truetype(str(FONT_KOMIKA), size)
        box = font.getbbox(text, stroke_width=2)
        if box[2] - box[0] <= 470:
            return font
    return ImageFont.truetype(str(FONT_KOMIKA), minimum)


def draw_caption(draw: ImageDraw.ImageDraw, text: str, highlight: str) -> None:
    font = fit_font(text, 39)
    box = draw.textbbox((0, 0), text, font=font, stroke_width=2)
    width = box[2] - box[0]
    panel(draw, (int(max(18, 270 - width / 2 - 18)), 552, int(min(522, 270 + width / 2 + 18)), 620), 210)
    centered_text(draw, (270, 586), text, font, WHITE)
    if highlight in text:
        prefix = text.split(highlight, 1)[0]
        full_box = draw.textbbox((0, 0), text, font=font, stroke_width=2)
        prefix_box = draw.textbbox((0, 0), prefix, font=font, stroke_width=2)
        left = 270 - (full_box[2] - full_box[0]) / 2 + (prefix_box[2] - prefix_box[0])
        draw.text((left, 586), highlight, font=font, fill=AMBER, stroke_width=2, stroke_fill=(0, 0, 0, 220), anchor="lm")


def local_segment(timeline: list[dict[str, Any]], t: float) -> tuple[dict[str, Any] | None, float]:
    for item in timeline:
        if item["final_start"] <= t < item["final_end"] + 1e-6:
            return item, t - item["final_start"]
    return None, 0.0


def draw_chain(draw: ImageDraw.ImageDraw, active: int, crude_risk: bool, y: int = 190) -> None:
    labels = ("CRUDE", "REFINE", "STORE", "SELL")
    xs = (82, 205, 328, 451)
    for index, (x, label) in enumerate(zip(xs, labels)):
        color = RED if crude_risk and index == 0 else (GREEN if index <= active else GRAY)
        draw.rounded_rectangle((x - 48, y - 28, x + 48, y + 28), radius=12, fill=(14, 22, 33, 245), outline=color, width=4)
        centered_text(draw, (x, y), label, ImageFont.truetype(str(FONT_BOLD), 13), color)
        if index < len(xs) - 1:
            draw.line((x + 50, y, xs[index + 1] - 50, y), fill=color, width=5)


def draw_story_overlay(draw: ImageDraw.ImageDraw, item: dict[str, Any], local: float, fonts: dict[str, ImageFont.FreeTypeFont]) -> None:
    name = item["name"]
    beat_index = int(local // BEAT)
    if name == "export_import_quote":
        panel(draw, (34, 48, 506, 238))
        centered_text(draw, (270, 80), "$20B SUPPLY-CHAIN TRAP", fonts["small"], WHITE)
        left = 118
        right = 422
        centered_text(draw, (left, 145), "CRUDE", fonts["hero"], AMBER)
        centered_text(draw, (right, 145), "FUEL", fonts["hero"], CYAN)
        progress = ease((local % BEAT) / BEAT)
        draw.line((170, 145, 360, 145), fill=WHITE, width=6)
        draw.polygon(((360, 133), (386, 145), (360, 157)), fill=WHITE)
        dot_x = round(170 + 190 * progress)
        draw.ellipse((dot_x - 8, 137, dot_x + 8, 153), fill=RED if beat_index >= 1 else GREEN)
        centered_text(draw, (270, 208), "EXPORT → IMPORT BACK", fonts["evidence"], RED if beat_index >= 1 else AMBER)
    elif name == "twenty_billion_question":
        panel(draw, (46, 74, 494, 324))
        centered_text(draw, (270, 118), "WHY BUILD THE LINK?", fonts["small"], WHITE)
        value = round(20 * ease(local / 2.5))
        centered_text(draw, (270, 182), f"${value}B", fonts["data"], AMBER)
        centered_text(draw, (270, 240), "ONE REFINERY", fonts["hero"], CYAN)
        centered_text(draw, (270, 294), "REPORTED INVESTMENT", fonts["evidence"], WHITE)
    elif name == "refinery_decision":
        panel(draw, (54, 80, 486, 270))
        centered_text(draw, (270, 122), "THE DECISION", fonts["small"], CYAN)
        centered_text(draw, (270, 186), "BUILD THE MISSING LINK", fonts["evidence"], WHITE)
        if beat_index >= 2:
            centered_text(draw, (270, 238), "REFINERY", fonts["hero"], AMBER)
    elif name == "backward_integration":
        panel(draw, (30, 72, 510, 310))
        centered_text(draw, (270, 112), "BACKWARD INTEGRATION", fonts["small"], WHITE)
        draw_chain(draw, min(3, beat_index + 1), False, 192)
        step_labels = ("IMPORT THE INPUT", "BUILD THE SUPPLIER", "CONTROL THE LINK")
        centered_text(draw, (270, 274), step_labels[min(2, beat_index)], fonts["evidence"], AMBER)
        active_x = (82, 205, 328, 451)[min(3, beat_index + 1)]
        pulse = 9 + round(6 * (0.5 + 0.5 * math.sin(local * 8)))
        draw.ellipse((active_x - 50 - pulse, 142 - pulse, active_x + 50 + pulse, 242 + pulse), outline=(67, 212, 255, 150), width=4)
    elif name == "control_prize":
        panel(draw, (48, 72, 492, 318))
        centered_text(draw, (270, 108), "THE CONTROL PRIZE", fonts["small"], WHITE)
        rows = (("TIMING", CYAN), ("QUALITY", GREEN), ("COST", AMBER))
        for index, (label, color) in enumerate(rows):
            y = 162 + index * 60
            active = beat_index >= index
            draw.rounded_rectangle((112, y - 22, 428, y + 22), radius=12, fill=(15, 23, 34, 240), outline=color if active else GRAY, width=3)
            centered_text(draw, (270, y), label, fonts["evidence"], color if active else GRAY)
    elif name == "nameplate_capacity":
        panel(draw, (42, 72, 498, 310))
        centered_text(draw, (270, 108), "NAMEPLATE CAPACITY", fonts["small"], WHITE)
        progress = ease(local / 4.8)
        value = round(650 * progress)
        centered_text(draw, (270, 172), f"{value:,}K", fonts["data"], AMBER)
        draw.rounded_rectangle((82, 222, 458, 258), radius=14, fill=(27, 36, 48, 245))
        draw.rounded_rectangle((82, 222, 82 + round(376 * progress), 258), radius=14, fill=CYAN)
        centered_text(draw, (270, 286), "BARRELS / DAY", fonts["evidence"], WHITE)
    elif name == "risk_moved":
        panel(draw, (30, 72, 510, 316))
        centered_text(draw, (270, 108), "THE BOTTLENECK MOVED", fonts["small"], RED)
        draw_chain(draw, 3, beat_index >= 1, 194)
        if beat_index >= 1:
            centered_text(draw, (270, 274), "CRUDE FEEDSTOCK", fonts["hero"], RED)
            pulse = 12 + round(8 * (0.5 + 0.5 * math.sin(local * 7)))
            draw.ellipse((82 - 52 - pulse, 194 - 34 - pulse, 82 + 52 + pulse, 194 + 34 + pulse), outline=(255, 92, 92, 205), width=5)
            draw.polygon(((145, 242), (198, 264), (145, 286)), fill=RED)
    elif name == "triple_cta":
        panel(draw, (40, 70, 500, 344), 242)
        centered_text(draw, (270, 108), "WOULD YOU BUILD IT?", fonts["small"], WHITE)
        draw.rounded_rectangle((70, 145, 255, 220), radius=18, fill=(18, 31, 33, 245), outline=GREEN, width=4)
        draw.rounded_rectangle((285, 145, 470, 220), radius=18, fill=(36, 22, 28, 245), outline=RED, width=4)
        centered_text(draw, (162, 182), "CONTROL", fonts["evidence"], GREEN)
        centered_text(draw, (378, 182), "TRAP", fonts["evidence"], RED)
        controls = ("LIKE", "SUBSCRIBE", "COMMENT")
        for index, label in enumerate(controls):
            active = local >= 0.3 + index * 0.9
            y = 258 + index * 30
            centered_text(draw, (270, y), label, fonts["tiny"], (CYAN if active else GRAY))
    elif name == "allocation_shortfall":
        panel(draw, (42, 70, 498, 316))
        centered_text(draw, (270, 106), "Q1 2026 CRUDE DELIVERY", fonts["small"], WHITE)
        progress = 0.46 * ease(local / 3.8)
        centered_text(draw, (270, 176), f"{round(progress * 100)}%", fonts["data"], RED)
        draw.rounded_rectangle((80, 226, 460, 264), radius=14, fill=(35, 40, 48, 245))
        draw.rounded_rectangle((80, 226, 80 + round(380 * progress), 264), radius=14, fill=RED)
        centered_text(draw, (270, 294), "OF ALLOCATED CRUDE", fonts["evidence"], WHITE)
    elif name == "cargoes":
        panel(draw, (38, 70, 502, 326))
        centered_text(draw, (270, 106), "COMPANY-REPORTED NEED", fonts["small"], WHITE)
        centered_text(draw, (270, 166), "13–15", fonts["data"], AMBER)
        centered_text(draw, (270, 214), "CARGOES / MONTH", fonts["evidence"], WHITE)
        for index in range(15):
            x = 100 + (index % 8) * 48
            y = 260 + (index // 8) * 34
            active = index < min(15, 1 + beat_index * 5)
            draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill=CYAN if active else GRAY)
    elif name == "payoff":
        panel(draw, (28, 68, 512, 332))
        centered_text(draw, (270, 104), "FINAL VERDICT", fonts["small"], WHITE)
        draw_chain(draw, 3, beat_index >= 1, 178)
        states = ("OWN MORE LINKS", "BOTTLENECK MOVES", "CONTROL EXPANDS", "BET EXPANDS")
        centered_text(draw, (270, 222), states[min(3, beat_index)], fonts["tiny"], CYAN if beat_index < 3 else RED)
        meter = ease(local / 6.2)
        draw.rounded_rectangle((76, 246, 464, 282), radius=14, fill=(31, 38, 49, 245))
        draw.rounded_rectangle((76, 246, 76 + round(388 * meter), 282), radius=14, fill=AMBER if beat_index < 4 else RED)
        centered_text(draw, (270, 308), "MORE CONTROL → BIGGER BET", fonts["evidence"], RED if beat_index >= 4 else AMBER)
    elif name == "loop_question":
        panel(draw, (44, 72, 496, 324), 242)
        centered_text(draw, (270, 112), "YOU OWN THE BOTTLENECK", fonts["small"], WHITE)
        centered_text(draw, (270, 176), "WOULD YOU BUILD IT?", fonts["hero"], AMBER)
        draw.rounded_rectangle((68, 238, 252, 292), radius=14, outline=GREEN, width=4, fill=(15, 27, 31, 238))
        draw.rounded_rectangle((288, 238, 472, 292), radius=14, outline=RED, width=4, fill=(34, 20, 26, 238))
        centered_text(draw, (160, 265), "CONTROL", fonts["tiny"], GREEN)
        centered_text(draw, (380, 265), "TRAP", fonts["tiny"], RED)


def build_overlay(timeline: list[dict[str, Any]], total_frames: int) -> None:
    fonts = {
        "hero": ImageFont.truetype(str(FONT_KOMIKA), 43),
        "data": ImageFont.truetype(str(FONT_BLACK), 48),
        "evidence": ImageFont.truetype(str(FONT_KOMIKA), 27),
        "small": ImageFont.truetype(str(FONT_BOLD), 19),
        "tiny": ImageFont.truetype(str(FONT_BOLD), 13),
        "micro": ImageFont.truetype(str(FONT_BOLD), 10),
    }
    command = [
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
        "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "qtrle",
        "-pix_fmt", "argb", OVERLAY,
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, cwd=ROOT)
    if process.stdin is None:
        raise RuntimeError("Could not open overlay encoder")
    total = total_frames / FPS
    for frame in range(total_frames):
        t = frame / FPS
        image = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image, "RGBA")
        item, local = local_segment(timeline, t)
        if item is not None:
            if item["kind"] == "narration_card":
                # Keep original-card scenes alive between semantic state changes.
                # The moving signal dots encode flow rather than decorative cuts.
                for dot in range(12):
                    x = int((34 + dot * 47 + t * (34 + dot % 3 * 8)) % OW)
                    y = 360 + (dot % 4) * 54
                    radius = 8 + dot % 3
                    color = (67, 212, 255, 215) if dot % 3 else (255, 184, 77, 215)
                    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
                scanner_y = 350 + int((local * 72) % 220)
                draw.line((28, scanner_y, 512, scanner_y), fill=(67, 212, 255, 125), width=5)
            draw_story_overlay(draw, item, local, fonts)
            for start, end, text, highlight in CAPTIONS[item["name"]]:
                if start <= local < end:
                    draw_caption(draw, text, highlight)
                    break
            if item["kind"] in {"source_quote", "source", "narration_source"}:
                draw.text((18, 910), "SOURCE • NBIM • 2026-05-13", font=fonts["micro"], fill=(255, 255, 255, 178), anchor="ls")
            elif item["illustration_label"]:
                panel(draw, (104, 794, 528, 844), 232)
                draw.text((516, 819), item["illustration_label"], font=fonts["small"], fill=(255, 255, 255, 240), anchor="rm")
            if item["name"] == "nameplate_capacity":
                draw.text((270, 886), "NAMEPLATE • NOT SUSTAINED OUTPUT", font=fonts["micro"], fill=(255, 255, 255, 190), anchor="ms")
            elif item["name"] == "allocation_shortfall":
                draw.text((270, 886), "REUTERS • REGULATOR DATA • 2026-05-05", font=fonts["micro"], fill=(255, 255, 255, 190), anchor="ms")
            elif item["name"] == "cargoes":
                draw.text((270, 886), "REUTERS • COMPANY STATEMENT • 2026-07-14", font=fonts["micro"], fill=(255, 255, 255, 190), anchor="ms")
        route = int(3 * t / max(total, 0.1))
        positions = ((16, 28), (390, 28), (16, 862))
        draw.text(positions[min(2, route)], "MONEY BLINDSPOT", font=fonts["micro"], fill=(255, 255, 255, 175), anchor="la")
        process.stdin.write(image.tobytes())
    process.stdin.close()
    code = process.wait()
    if code != 0:
        raise RuntimeError(f"Overlay encoder exited {code}")


def make_positioned_track(source: Path, start: float, total: float, output: Path, volume: float) -> Path:
    base = f"aresample=48000,aformat=channel_layouts=stereo,volume={volume:.7f}"
    if start <= 0:
        graph = f"[0:a]{base},apad,atrim=0:{total:.6f}[out]"
        inputs: list[str | Path] = ["-i", source]
    else:
        graph = f"[1:a]{base}[clip];[0:a][clip]concat=n=2:v=0:a=1,apad,atrim=0:{total:.6f}[out]"
        inputs = ["-f", "lavfi", "-t", f"{start:.6f}", "-i", "anullsrc=r=48000:cl=stereo", "-i", source]
    run([
        "ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", graph, "-map", "[out]",
        "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", output,
    ])
    return output


def build_sfx(timeline: list[dict[str, Any]], total: float) -> Path:
    starts = {item["name"]: item["final_start"] for item in timeline}
    events: list[tuple[str, Path, float, float]] = [
        ("hook", HOOK_HIT, 0.04, -11),
        ("refine_gap", PROOF_TICK, 1.50, -15),
        ("export", PROOF_TICK, 3.00, -15),
        ("import", PROOF_TICK, 4.50, -15),
        ("import_cost", PROOF_TICK, 6.00, -15),
        ("question", WHOOSH, starts["twenty_billion_question"], -12),
        ("decision", PROOF_TICK, starts["refinery_decision"], -16),
        ("mechanism", WHOOSH, starts["backward_integration"], -17),
        ("timing", PROOF_TICK, starts["control_prize"], -16),
        ("quality", PROOF_TICK, starts["control_prize"] + 1.50, -16),
        ("cost", PROOF_TICK, starts["control_prize"] + 3.00, -16),
        ("capacity", PROOF_TICK, starts["nameplate_capacity"], -15),
        ("upstream", WHOOSH, starts["risk_moved"], -11),
        ("cta_like", CTA_CLICK, starts["triple_cta"] + 0.30, -10),
        ("cta_sub", CTA_CLICK, starts["triple_cta"] + 1.20, -10),
        ("cta_comment", CTA_CLICK, starts["triple_cta"] + 2.10, -10),
        ("allocation", PROOF_TICK, starts["allocation_shortfall"], -14),
        ("cargo", PROOF_TICK, starts["cargoes"], -15),
        ("payoff", PAYOFF_HIT, starts["payoff"], -15),
        ("loop", WHOOSH, starts["loop_question"], -12),
    ]
    work = WORK / "audio" / "sfx"
    work.mkdir(parents=True, exist_ok=True)
    tracks = [
        make_positioned_track(source, start, total, work / f"positioned_{name}.wav", math.pow(10, db / 20))
        for name, source, start, db in events
    ]
    inputs: list[str | Path] = []
    for track in tracks:
        inputs.extend(["-i", track])
    labels = "".join(f"[{index}:a]" for index in range(len(tracks)))
    output = work / "timed_full.wav"
    run([
        "ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex",
        f"{labels}amix=inputs={len(tracks)}:duration=longest:normalize=0,atrim=0:{total:.6f}[out]",
        "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", output,
    ])
    return output


def composite(base: Path, sfx: Path, total_frames: int) -> None:
    total = total_frames / FPS
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    graph = (
        "[1:v]scale=1080:1920:flags=lanczos,format=rgba[ov];"
        "[0:v][ov]overlay=0:0:format=auto,format=yuv420p[v];"
        "[0:a]aresample=48000,aformat=channel_layouts=stereo[basea];"
        "[2:a]aresample=48000,aformat=channel_layouts=stereo[sfx];"
        "[3:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.125[bed];"
        f"[basea][sfx][bed]amix=inputs=3:duration=longest:normalize=0,atrim=0:{total:.6f},"
        "loudnorm=I=-16.5:TP=-2.0:LRA=10,volume=-0.5dB,alimiter=limit=0.82:level=false[a]"
    )
    run([
        "ffmpeg", "-y", "-v", "error", "-i", base, "-i", OVERLAY, "-i", sfx, "-i", MUSIC_BED,
        "-filter_complex", graph, "-map", "[v]", "-map", "[a]", "-frames:v", str(total_frames),
        *encode_args(), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart", "-t", f"{total:.6f}", FINAL,
    ])


def validate_inputs() -> None:
    required = [
        SOURCE, PEXELS_REFINERY, PEXELS_PUMPJACK, HOOK_HIT, WHOOSH, PROOF_TICK,
        CTA_CLICK, PAYOFF_HIT, MUSIC_BED, SFX_MANIFEST, FONT_KOMIKA, FONT_BOLD, FONT_BLACK,
    ]
    required.extend(segment.audio for segment in SEGMENTS if segment.audio is not None)
    missing = sorted(str(path) for path in required if path is not None and not path.exists())
    if missing:
        raise FileNotFoundError("Missing inputs:\n" + "\n".join(missing))
    manifest = json.loads(SFX_MANIFEST.read_text(encoding="utf-8"))
    approved = {
        item["id"] for item in manifest.get("assets", [])
        if item.get("approval_status") == "approved" and item.get("rights_status") == "cleared"
    }
    required_ids = {
        "hardknocks_v22_hook_origin_hit", "hardknocks_v22_jet_motion_whoosh",
        "hardknocks_v22_proof_tick", "hardknocks_v22_cta_click",
        "hardknocks_v22_payoff_warm_hit", "hardknocks_v22_restrained_finance_bed",
    }
    if not required_ids <= approved:
        raise RuntimeError(f"Missing cleared SFX: {sorted(required_ids - approved)}")


def write_preproduction_artifacts() -> None:
    rows = []
    for variant_id, mechanism, scores in HOOK_VARIANTS:
        rows.append(
            {
                "id": variant_id,
                "mechanism": mechanism,
                "scores": dict(zip(("curiosity_gap", "specificity", "visual", "emotion", "payoff", "novelty"), scores)),
                "total": sum(scores),
                "selected": variant_id == "twenty_billion_trap",
            }
        )
    rows.sort(key=lambda row: (row["total"], row["scores"]["curiosity_gap"]), reverse=True)
    HOOK_SCORECARD.write_text(json.dumps({"rubric_max": 60, "tie_breaker": "curiosity_gap", "variants": rows}, indent=2) + "\n")
    ASSET_MANIFEST.write_text(
        json.dumps(
            {
                "approved": [
                    {
                        "id": 12891229,
                        "path": str(PEXELS_REFINERY.relative_to(ROOT)),
                        "sha256": sha256(PEXELS_REFINERY),
                        "classification": "relevant refinery illustration",
                        "label": "ILLUSTRATION • PEXELS 12891229",
                    },
                    {
                        "id": 10227529,
                        "path": str(PEXELS_PUMPJACK.relative_to(ROOT)),
                        "sha256": sha256(PEXELS_PUMPJACK),
                        "classification": "generic upstream extraction illustration",
                        "label": "ILLUSTRATION • PEXELS 10227529",
                    },
                ],
                "rejected": [
                    {"id": 19621044, "reason": "visible vessel branding and unverified cargo/route"},
                    {"id": 30243437, "reason": "generic utility system; not identifiable as crude infrastructure"},
                ],
            },
            indent=2,
        ) + "\n"
    )


def validate_final(timeline: list[dict[str, Any]], total_frames: int) -> dict[str, Any]:
    data = json.loads(
        run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", FINAL], capture=True).stdout
    )
    video = next(stream for stream in data["streams"] if stream["codec_type"] == "video")
    audio = next(stream for stream in data["streams"] if stream["codec_type"] == "audio")
    duration = float(data["format"]["duration"])
    source_segments = [item for item in timeline if item["source_duration"] > 0]
    cta_start = next(item["final_start"] for item in timeline if item["name"] == "triple_cta")
    beats: list[dict[str, Any]] = []
    for item in timeline:
        for start, end, text, highlight in CAPTIONS[item["name"]]:
            beats.append(
                {
                    "index": len(beats),
                    "start": item["final_start"] + start,
                    "end": item["final_start"] + end,
                    "source": item["name"],
                    "caption": text,
                    "highlight": highlight,
                    "function": item["act"],
                }
            )
    checks = {
        "width": video.get("width") == WIDTH,
        "height": video.get("height") == HEIGHT,
        "codec": video.get("codec_name") == "h264",
        "pixel_format": video.get("pix_fmt") == "yuv420p",
        "frame_rate": video.get("r_frame_rate") == "30/1",
        "audio_codec": audio.get("codec_name") == "aac",
        "audio_rate": audio.get("sample_rate") == "48000",
        "audio_channels": audio.get("channels") == 2,
        "duration": abs(duration - 64.5) <= 0.05,
        "frame_count": total_frames == 1935,
        "beat_count": len(beats) == 43,
        "edl_contiguous": all(abs(row["end"] - beats[index + 1]["start"]) < 0.001 for index, row in enumerate(beats[:-1])),
        "max_beat_1_5": all(row["end"] - row["start"] <= 1.5001 for row in beats),
        "caption_at_frame_zero": beats[0]["start"] <= 0.2,
        "captions_2_to_5_words": all(2 <= len(row["caption"].split()) <= 5 for row in beats),
        "source_clips_under_15": all(item["source_duration"] < 15 for item in source_segments),
        "source_final_under_50pct": sum(item["source_duration"] for item in source_segments) < duration * 0.5,
        "cta_window": 38.0 <= cta_start <= 42.0 or (cta_start <= 38.0 and next(item["final_end"] for item in timeline if item["name"] == "triple_cta") >= 38.0),
        "exact_stock_set": {
            item["visual"] for item in timeline if item["visual"]
        } == {str(PEXELS_REFINERY.relative_to(ROOT)), str(PEXELS_PUMPJACK.relative_to(ROOT))},
    }
    if not all(checks.values()):
        raise RuntimeError(f"Final validation failed: {checks}")
    report = {
        "final": str(FINAL.relative_to(ROOT)),
        "sha256": sha256(FINAL),
        "duration": duration,
        "checks": checks,
        "cta_start": cta_start,
        "source_final_seconds": sum(item["source_duration"] for item in source_segments),
        "source_master_duration": SOURCE_DURATION,
        "timeline": timeline,
        "beats": beats,
    }
    TIMELINE_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    for directory in (WORK, SEGMENT_DIR, CHECKS):
        directory.mkdir(parents=True, exist_ok=True)
    validate_inputs()
    write_preproduction_artifacts()
    base, timeline, total_frames = build_base()
    build_overlay(timeline, total_frames)
    sfx = build_sfx(timeline, total_frames / FPS)
    composite(base, sfx, total_frames)
    print(json.dumps(validate_final(timeline, total_frames), indent=2))


if __name__ == "__main__":
    main()
