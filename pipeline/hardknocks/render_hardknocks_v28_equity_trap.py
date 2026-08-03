#!/usr/bin/env python3
"""Render HardKnocks V28: The 20% Equity Trap.

The source claims that the bank takes all the risk on an 80%-financed
property. This internal-only Clip Curation Edit turns that claim into a
first-loss waterfall, then adds cash-flow, underwriting, maturity-wave and
recourse guardrails. Completion is based on the encoded MP4 and media QC.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "hardknocks"
SOURCE = PROJECT / "source" / "DwrRvp_qsRk.webm"
SOURCE_DURATION = 793.228
WORK = PROJECT / "clips" / "v28_equity_trap_work"
SEGMENT_DIR = WORK / "segments"
AUDIO_DIR = WORK / "audio" / "qwen-zack"
CHECKS = WORK / "checks"
HOOK_DIR = WORK / "hook_gate"
OVERLAY = WORK / "overlay_v1_equity_trap.mov"
CANDIDATE = WORK / "candidate_v1_equity_trap.mp4"
ROUGH_HOOK = HOOK_DIR / "rough_hook_v1_source_decision_lock.mp4"
FINAL = PROJECT / "final" / "2026-08-03-hardknocks_v28_equity_trap.mp4"
TIMELINE_JSON = WORK / "timeline.json"
HOOK_SCORECARD = WORK / "hook-strategy-scorecard.json"

PEXELS_PROPERTY = ROOT / "output" / "shared" / "pexels" / "real_estate_37694695.mp4"
PEXELS_CONTRACT = ROOT / "output" / "shared" / "pexels" / "contract_signing_7981954.mp4"

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
CAPTION_BAND_PX = 270
SEGMENT_FADE_IN = 0.10
SEGMENT_FADE_OUT = 0.18

WHITE = (248, 250, 252, 255)
DARK = (9, 13, 22, 232)
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
    source_start: float | None = None
    speaker: str | None = None
    focus: float | None = None
    audio_id: str | None = None
    visual: Path | None = None
    visual_start: float = 0.0

    @property
    def uses_source(self) -> bool:
        return self.kind in {"source", "narration_source"}

    @property
    def audio(self) -> Path | None:
        return AUDIO_DIR / f"{self.audio_id}.wav" if self.audio_id else None


SEGMENTS = (
    Segment("deal_ten_million", "source", 1.50, "stakes", source_start=283.20, speaker="ben_left", focus=0.30),
    Segment("buyer_two", "source", 2.14, "capital_split", source_start=286.48, speaker="ben_left", focus=0.30),
    Segment("risk_answer", "source", 1.72, "source_verdict", source_start=288.88, speaker="ben_left", focus=0.30),
    Segment("counter_audit", "narration_source", 4.60, "counter_audit", source_start=290.96, speaker="ben_left", focus=0.30, audio_id="counter_audit"),
    Segment("capital_stack", "narration_pexels", 4.60, "capital_stack", audio_id="capital_stack", visual=PEXELS_PROPERTY, visual_start=0.40),
    Segment("value_shock", "narration_pexels", 6.40, "first_loss", audio_id="value_shock", visual=PEXELS_PROPERTY, visual_start=3.10),
    Segment("cashflow_cushion", "source", 4.00, "source_guardrail", source_start=298.72, speaker="ben_left", focus=0.30),
    Segment("underwriting_guardrail", "narration_pexels", 6.40, "underwriting", audio_id="underwriting_guardrail", visual=PEXELS_CONTRACT, visual_start=0.80),
    Segment("bank_default_risk", "source", 2.90, "bank_risk", source_start=322.72, speaker="ben_left", focus=0.30),
    Segment("maturity_wave", "narration_pexels", 6.20, "current_attention", audio_id="maturity_wave", visual=PEXELS_PROPERTY, visual_start=1.80),
    Segment("triple_cta", "narration_pexels", 4.00, "cta", audio_id="triple_cta", visual=PEXELS_CONTRACT, visual_start=4.20),
    Segment("recourse_guardrail", "narration_pexels", 6.40, "recourse", audio_id="recourse_guardrail", visual=PEXELS_CONTRACT, visual_start=1.40),
    Segment("first_loss_payoff", "narration_source", 7.00, "payoff", source_start=286.20, speaker="ben_left", focus=0.30, audio_id="first_loss_payoff"),
)

HOOK_SEGMENT_COUNT = 3

CAPTIONS: dict[str, tuple[tuple[float, float, str, str], ...]] = {
    "deal_ten_million": ((0.00, 1.50, "A $10 MILLION DEAL", "$10 MILLION"),),
    "buyer_two": ((0.00, 1.05, "I PUT $2M DOWN", "$2M"), (1.05, 2.14, "BANK PUTS $8M", "$8M")),
    "risk_answer": ((0.00, 0.96, "WHO TAKES THE RISK?", "WHO"), (0.96, 1.72, "THE BANK.", "BANK")),
    "counter_audit": ((0.00, 1.10, "HE SAYS: THE BANK", "BANK"), (1.10, 2.15, "TAKES ALL THE RISK", "ALL"), (2.15, 3.22, "BUT WATCH", "WATCH"), (3.22, 4.60, "THE FIRST-LOSS MATH", "FIRST-LOSS")),
    "capital_stack": ((0.00, 1.35, "$10M PROPERTY", "$10M"), (1.35, 2.78, "$8M LOAN", "$8M"), (2.78, 4.60, "$2M BUYER EQUITY", "$2M")),
    "value_shock": ((0.00, 1.28, "VALUE FALLS 20%", "20%"), (1.28, 2.72, "$10M BECOMES $8M", "$8M"), (2.72, 4.12, "DEBT STAYS $8M", "DEBT"), (4.12, 5.28, "BUYER EQUITY", "EQUITY"), (5.28, 6.40, "FALLS TO $0", "$0")),
    "cashflow_cushion": ((0.00, 1.20, "YOU NEED", "NEED"), (1.20, 2.55, "A MUCH BIGGER CUSHION", "CUSHION"), (2.55, 4.00, "IN PROFIT", "PROFIT")),
    "underwriting_guardrail": ((0.00, 1.38, "LTV IS ONE TEST", "ONE"), (1.38, 2.45, "LENDERS CHECK", "CHECK"), (2.45, 3.70, "CASH FLOW", "CASH"), (3.70, 5.02, "PROPERTY RISK", "RISK"), (5.02, 6.40, "AND DEBT SERVICE", "DEBT")),
    "bank_default_risk": ((0.00, 1.45, "IF LOANS GO BAD", "BAD"), (1.45, 2.90, "BANK IS WORTH LESS", "LESS")),
    "maturity_wave": ((0.00, 1.18, "WHY THIS MATTERS NOW", "NOW"), (1.18, 2.82, "$875 BILLION", "$875"), (2.82, 4.56, "IN CRE MORTGAGES", "CRE"), (4.56, 6.20, "MATURE IN 2026", "2026")),
    "triple_cta": ((0.00, 1.40, "USE 80% DEBT?", "80%"), (1.40, 2.62, "LIKE + SUBSCRIBE", "SUBSCRIBE"), (2.62, 4.00, "COMMENT YOUR ANSWER", "COMMENT")),
    "recourse_guardrail": ((0.00, 1.20, "AND RECOURSE", "RECOURSE"), (1.20, 2.58, "CAN REACH", "REACH"), (2.58, 4.08, "OTHER BORROWER ASSETS", "ASSETS"), (4.08, 6.40, "FED: SHADOW EQUITY", "SHADOW")),
    "first_loss_payoff": ((0.00, 1.38, "NEITHER SIDE", "NEITHER"), (1.38, 2.82, "TAKES ALL THE RISK", "ALL"), (2.82, 4.48, "EQUITY TAKES FIRST HIT", "EQUITY"), (4.48, 5.38, "THEN THE BANK", "BANK"), (5.38, 7.00, "TAKES THE NEXT LOSS", "NEXT")),
}

HOOK_VARIANTS = (
    ("source_decision_lock", "source claim + forced prediction + delayed answer", (10, 10, 10, 9, 10, 9)),
    ("twenty_equals_hundred", "20% asset drop = 100% equity-loss contradiction", (10, 10, 10, 9, 10, 8)),
    ("is_he_right", "authority claim challenged by immediate counter-audit", (10, 9, 9, 9, 10, 9)),
    ("two_controls_ten", "$2M controls $10M scale puzzle", (9, 10, 9, 8, 9, 8)),
    ("bank_paid_eighty", "bank-paid-80% ownership mystery", (9, 9, 8, 8, 9, 8)),
    ("first_loss_layer", "withheld first-loss identity", (9, 9, 8, 8, 10, 8)),
    ("bagholder_test", "bank bagholder identity threat", (9, 8, 8, 9, 8, 8)),
    ("equity_countdown", "$2M to $0 countdown", (8, 10, 10, 8, 9, 8)),
    ("leverage_reversal", "leverage amplifies upside and first loss", (8, 8, 8, 7, 9, 7)),
    ("cushion_break", "what breaks after the cushion", (8, 8, 8, 8, 9, 8)),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hook-only", action="store_true", help="Render the locked 5.36s source-native hook")
    return parser.parse_args()


def run(command: list[str | Path], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(str(item) for item in command), flush=True)
    return subprocess.run([str(item) for item in command], cwd=ROOT, check=True, text=True, capture_output=capture)


def frames_for(seconds: float) -> int:
    return max(1, round(seconds * FPS))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def encode_args() -> list[str]:
    return ["-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p", "-r", str(FPS)]


def source_crop(focus: float) -> str:
    clean_height = HEIGHT - CAPTION_BAND_PX
    recovery_width = round(WIDTH * HEIGHT / clean_height)
    scale_width = 3414
    span = scale_width - WIDTH
    x = round(span * focus)
    return (
        f"scale={scale_width}:{HEIGHT}:flags=lanczos,crop={WIDTH}:{HEIGHT}:{x}:0,"
        f"crop={WIDTH}:{clean_height}:0:0,scale={recovery_width}:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:({recovery_width}-{WIDTH})/2:0,"
        "eq=contrast=1.04:saturation=1.03,setsar=1,format=yuv420p,fps=30"
    )


def pexels_crop() -> str:
    return (
        "scale=1134:2016:force_original_aspect_ratio=increase:flags=lanczos,"
        "crop=1080:1920:x='27+16*sin(t*0.75)':y='48+32*sin(t*0.57)',"
        "eq=contrast=1.05:saturation=0.90,setsar=1,format=yuv420p,fps=30"
    )


def narration_filter(duration: float) -> str:
    return (
        "aresample=48000,aformat=channel_layouts=stereo,highpass=f=70,"
        "acompressor=threshold=0.1:ratio=4:attack=5:release=100:makeup=1,"
        "loudnorm=I=-16:TP=-1.5:LRA=10,apad,"
        f"atrim=0:{duration:.6f},afade=t=in:st=0:d={SEGMENT_FADE_IN:.2f},"
        f"afade=t=out:st={duration - SEGMENT_FADE_OUT:.6f}:d={SEGMENT_FADE_OUT:.2f}"
    )


def render_segment(segment: Segment, output: Path) -> int:
    if segment.uses_source and segment.duration >= 15.0:
        raise ValueError(f"Source clip reaches 15 seconds: {segment.name}")
    if segment.uses_source and (segment.speaker is None or segment.focus is None):
        raise ValueError(f"Source clip lacks active-speaker framing: {segment.name}")
    frame_count = frames_for(segment.duration)
    if segment.kind == "source":
        assert segment.source_start is not None and segment.focus is not None
        coarse = max(0.0, segment.source_start - 4.0)
        fine = segment.source_start - coarse
        end = fine + segment.duration
        graph = (
            f"[0:v]trim=start={fine:.6f}:end={end:.6f},setpts=PTS-STARTPTS,{source_crop(segment.focus)}[v];"
            f"[0:a]atrim=start={fine:.6f}:end={end:.6f},asetpts=PTS-STARTPTS,"
            "highpass=f=70,acompressor=threshold=0.125:ratio=2:attack=5:release=80:makeup=1.4,"
            f"loudnorm=I=-16:TP=-1.5:LRA=10,aresample=48000:first_pts=0,apad,atrim=0:{segment.duration:.6f},"
            f"afade=t=in:st=0:d={SEGMENT_FADE_IN:.2f},afade=t=out:st={segment.duration - SEGMENT_FADE_OUT:.6f}:d={SEGMENT_FADE_OUT:.2f}[a]"
        )
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{coarse:.6f}", "-i", SOURCE, "-filter_complex", graph,
             "-map", "[v]", "-map", "[a]", "-frames:v", str(frame_count), *encode_args(),
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", output])
    elif segment.kind == "narration_source":
        assert segment.source_start is not None and segment.focus is not None and segment.audio is not None
        coarse = max(0.0, segment.source_start - 4.0)
        fine = segment.source_start - coarse
        end = fine + segment.duration
        graph = (
            f"[0:v]trim=start={fine:.6f}:end={end:.6f},setpts=PTS-STARTPTS,{source_crop(segment.focus)}[v];"
            f"[1:a]{narration_filter(segment.duration)}[a]"
        )
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{coarse:.6f}", "-i", SOURCE, "-i", segment.audio,
             "-filter_complex", graph, "-map", "[v]", "-map", "[a]", "-frames:v", str(frame_count),
             *encode_args(), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", output])
    elif segment.kind == "narration_pexels":
        assert segment.visual is not None and segment.audio is not None
        graph = f"[0:v]{pexels_crop()}[v];[1:a]{narration_filter(segment.duration)}[a]"
        run(["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-ss", f"{segment.visual_start:.3f}",
             "-i", segment.visual, "-i", segment.audio, "-filter_complex", graph,
             "-map", "[v]", "-map", "[a]", "-frames:v", str(frame_count), *encode_args(),
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", output])
    else:
        raise ValueError(segment.kind)
    return frame_count


def build_base(segments: tuple[Segment, ...], suffix: str) -> tuple[Path, list[dict[str, Any]], int]:
    SEGMENT_DIR.mkdir(parents=True, exist_ok=True)
    cursor = 0
    timeline: list[dict[str, Any]] = []
    outputs: list[Path] = []
    for index, segment in enumerate(segments):
        output = SEGMENT_DIR / f"{index:02d}_{segment.name}{suffix}.mp4"
        count = render_segment(segment, output)
        timeline.append({
            "name": segment.name,
            "kind": segment.kind,
            "act": segment.act,
            "speaker": segment.speaker,
            "focus": segment.focus,
            "source_start": segment.source_start,
            "source_end": segment.source_start + segment.duration if segment.source_start is not None else None,
            "source_duration": segment.duration if segment.uses_source else 0.0,
            "final_start": cursor / FPS,
            "final_end": (cursor + count) / FPS,
            "start_frame": cursor,
            "end_frame": cursor + count,
            "frames": count,
        })
        cursor += count
        outputs.append(output)
    concat = WORK / f"concat{suffix}.txt"
    concat.write_text("".join(f"file '{item.resolve()}'\n" for item in outputs), encoding="utf-8")
    base = WORK / f"base{suffix}.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat, "-c", "copy", base])
    return base, timeline, cursor


def ease(value: float) -> float:
    x = min(1.0, max(0.0, value))
    return x * x * (3.0 - 2.0 * x)


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], alpha: int = 230) -> None:
    draw.rounded_rectangle(box, radius=20, fill=(9, 13, 22, alpha), outline=(255, 255, 255, 90), width=2)


def centered_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.FreeTypeFont, fill: tuple[int, int, int, int]) -> None:
    draw.text(xy, text, font=font, fill=fill, stroke_width=2, stroke_fill=(0, 0, 0, 220), anchor="mm")


def draw_caption(draw: ImageDraw.ImageDraw, text: str, highlight: str, font: ImageFont.FreeTypeFont) -> None:
    box = draw.textbbox((0, 0), text, font=font, stroke_width=2)
    width = box[2] - box[0]
    panel(draw, (int(max(18, 270 - width // 2 - 18)), 554, int(min(522, 270 + width // 2 + 18)), 620), 205)
    centered_text(draw, (270, 587), text, font, WHITE)
    if highlight in text:
        prefix = text.split(highlight, 1)[0]
        full_box = draw.textbbox((0, 0), text, font=font, stroke_width=2)
        prefix_box = draw.textbbox((0, 0), prefix, font=font, stroke_width=2)
        key_box = draw.textbbox((0, 0), highlight, font=font, stroke_width=2)
        left = 270 - (full_box[2] - full_box[0]) / 2 + (prefix_box[2] - prefix_box[0])
        draw.text((left, 587), highlight, font=font, fill=AMBER, stroke_width=2, stroke_fill=(0, 0, 0, 220), anchor="lm")


def local_segment(timeline: list[dict[str, Any]], t: float) -> tuple[dict[str, Any] | None, float]:
    for item in timeline:
        if item["final_start"] <= t < item["final_end"] + 1e-6:
            return item, t - item["final_start"]
    return None, 0.0


def draw_hook(draw: ImageDraw.ImageDraw, t: float, fonts: dict[str, ImageFont.FreeTypeFont]) -> None:
    panel(draw, (26, 72, 514, 265), 235)
    centered_text(draw, (270, 104), "WHO LOSES FIRST?", fonts["small"], WHITE)
    if t < 1.50:
        centered_text(draw, (270, 164), "$10M PROPERTY", fonts["hero"], AMBER)
        centered_text(draw, (270, 220), "LOCK YOUR ANSWER", fonts["tiny"], CYAN)
    elif t < 3.64:
        centered_text(draw, (165, 168), "BUYER", fonts["evidence"], AMBER)
        centered_text(draw, (375, 168), "BANK", fonts["evidence"], CYAN)
        draw.rounded_rectangle((69, 204, 461, 235), radius=12, fill=(25, 35, 49, 245))
        draw.rounded_rectangle((69, 204, 147, 235), radius=12, fill=AMBER)
        draw.rounded_rectangle((147, 204, 461, 235), radius=12, fill=CYAN)
        centered_text(draw, (108, 219), "$2M", fonts["tiny"], (12, 16, 24, 255))
        centered_text(draw, (304, 219), "$8M", fonts["tiny"], (12, 16, 24, 255))
    else:
        centered_text(draw, (270, 152), "DECISION LOCKED", fonts["evidence"], WHITE)
        if t >= 4.60:
            centered_text(draw, (270, 214), "SOURCE ANSWER: BANK", fonts["small"], CYAN)
        else:
            centered_text(draw, (270, 214), "WAIT FOR HIS ANSWER", fonts["small"], AMBER)


def draw_story_overlay(draw: ImageDraw.ImageDraw, item: dict[str, Any], local: float, fonts: dict[str, ImageFont.FreeTypeFont]) -> None:
    name = item["name"]
    if name == "counter_audit":
        panel(draw, (56, 82, 484, 235))
        centered_text(draw, (270, 128), "SOURCE CLAIM", fonts["small"], CYAN)
        centered_text(draw, (270, 184), "BANK TAKES ALL RISK", fonts["evidence"], WHITE)
        if local > 2.1:
            centered_text(draw, (270, 224), "AUDIT THE FIRST LOSS ↓", fonts["tiny"], AMBER)
    elif name == "capital_stack":
        panel(draw, (42, 86, 498, 290))
        centered_text(draw, (270, 122), "$10M CAPITAL STACK", fonts["small"], WHITE)
        draw.rounded_rectangle((76, 160, 464, 222), radius=14, fill=(24, 34, 48, 250))
        progress = ease(local / 1.2)
        draw.rounded_rectangle((76, 160, 76 + round(310 * progress), 222), radius=14, fill=CYAN)
        draw.rounded_rectangle((386, 160, 386 + round(78 * progress), 222), radius=14, fill=AMBER)
        centered_text(draw, (231, 191), "BANK $8M", fonts["small"], (10, 15, 22, 255))
        centered_text(draw, (425, 191), "YOU $2M", fonts["tiny"], (10, 15, 22, 255))
        centered_text(draw, (270, 262), "80% DEBT • 20% EQUITY", fonts["tiny"], GRAY)
    elif name == "value_shock":
        panel(draw, (42, 72, 498, 310))
        p = ease(local / 5.2)
        value = 10.0 - 2.0 * p
        equity = max(0.0, value - 8.0)
        centered_text(draw, (270, 108), "20% VALUE SHOCK", fonts["small"], RED)
        centered_text(draw, (270, 164), f"PROPERTY  ${value:0.1f}M", fonts["evidence"], WHITE)
        centered_text(draw, (270, 216), "DEBT        $8.0M", fonts["evidence"], CYAN)
        centered_text(draw, (270, 268), f"EQUITY      ${equity:0.1f}M", fonts["evidence"], AMBER if equity > 0.05 else RED)
        if local > 5.0:
            centered_text(draw, (270, 300), "FIRST-LOSS LAYER: ERASED", fonts["tiny"], RED)
    elif name == "cashflow_cushion":
        panel(draw, (66, 84, 474, 230))
        centered_text(draw, (270, 128), "SOURCE GUARDRAIL", fonts["small"], CYAN)
        centered_text(draw, (270, 184), "BIGGER PROFIT CUSHION", fonts["evidence"], AMBER)
    elif name == "underwriting_guardrail":
        panel(draw, (48, 74, 492, 315))
        centered_text(draw, (270, 108), "LTV IS ONLY ONE TEST", fonts["small"], WHITE)
        rows = (("CASH FLOW", GREEN), ("PROPERTY RISK", AMBER), ("DEBT SERVICE", CYAN))
        for index, (text, color) in enumerate(rows):
            y = 160 + index * 58
            active = local >= index * 1.25
            draw.rounded_rectangle((94, y - 21, 446, y + 21), radius=12, fill=(16, 23, 34, 235), outline=color if active else GRAY, width=3)
            centered_text(draw, (270, y), text, fonts["small"], color if active else GRAY)
    elif name == "bank_default_risk":
        panel(draw, (64, 86, 476, 235))
        centered_text(draw, (270, 128), "THE BANK STILL HAS RISK", fonts["small"], WHITE)
        centered_text(draw, (270, 184), "AFTER THE CUSHION BREAKS", fonts["evidence"], RED)
    elif name == "maturity_wave":
        panel(draw, (42, 72, 498, 308))
        centered_text(draw, (270, 112), "2026 REFINANCING WAVE", fonts["small"], WHITE)
        p = ease(local / 2.3)
        centered_text(draw, (270, 184), f"${round(875 * p):,}B", fonts["data"], AMBER)
        centered_text(draw, (270, 240), "CRE MORTGAGES MATURE", fonts["evidence"], WHITE)
        centered_text(draw, (270, 285), "17% OF $5.0T OUTSTANDING", fonts["tiny"], CYAN)
    elif name == "triple_cta":
        panel(draw, (40, 70, 500, 330), 240)
        centered_text(draw, (270, 112), "USE 80% DEBT?", fonts["hero"], WHITE)
        controls = (("LIKE", GREEN), ("SUBSCRIBE", CYAN), ("COMMENT", AMBER))
        for index, (text, color) in enumerate(controls):
            y = 182 + index * 56
            active = local >= (0.2 + index * 0.85)
            draw.rounded_rectangle((88, y - 20, 452, y + 20), radius=12, fill=(17, 24, 36, 240), outline=color if active else GRAY, width=3)
            centered_text(draw, (270, y), text, fonts["small"], color if active else GRAY)
    elif name == "recourse_guardrail":
        panel(draw, (46, 72, 494, 310))
        centered_text(draw, (270, 110), "CONTRACT MATTERS", fonts["small"], WHITE)
        centered_text(draw, (270, 176), "RECOURSE", fonts["hero"], RED)
        centered_text(draw, (270, 230), "CAN REACH OTHER ASSETS", fonts["evidence"], AMBER)
        centered_text(draw, (270, 280), "FED: “SHADOW EQUITY”", fonts["tiny"], CYAN)
    elif name == "first_loss_payoff":
        panel(draw, (40, 72, 500, 320), 240)
        centered_text(draw, (270, 108), "FINAL VERDICT", fonts["small"], WHITE)
        centered_text(draw, (270, 168), "EQUITY", fonts["hero"], AMBER)
        centered_text(draw, (270, 212), "TAKES THE FIRST HIT", fonts["evidence"], WHITE)
        centered_text(draw, (270, 266), "BANK", fonts["hero"], CYAN)
        centered_text(draw, (270, 306), "TAKES THE NEXT LOSS", fonts["tiny"], WHITE)


def build_overlay(timeline: list[dict[str, Any]], total_frames: int, output: Path) -> None:
    fonts = {
        "caption": ImageFont.truetype(str(FONT_KOMIKA), 39),
        "hero": ImageFont.truetype(str(FONT_KOMIKA), 45),
        "data": ImageFont.truetype(str(FONT_BLACK), 45),
        "evidence": ImageFont.truetype(str(FONT_KOMIKA), 28),
        "small": ImageFont.truetype(str(FONT_BOLD), 19),
        "tiny": ImageFont.truetype(str(FONT_BOLD), 13),
        "micro": ImageFont.truetype(str(FONT_BOLD), 10),
    }
    command = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "qtrle", "-pix_fmt", "argb", output]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, cwd=ROOT)
    if process.stdin is None:
        raise RuntimeError("Could not open overlay encoder")
    for frame in range(total_frames):
        t = frame / FPS
        image = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image, "RGBA")
        item, local = local_segment(timeline, t)
        if item is not None:
            if t < sum(frames_for(s.duration) for s in SEGMENTS[:HOOK_SEGMENT_COUNT]) / FPS:
                draw_hook(draw, t, fonts)
            else:
                draw_story_overlay(draw, item, local, fonts)
            for start, end, text, highlight in CAPTIONS[item["name"]]:
                if start <= local < end:
                    draw_caption(draw, text, highlight, fonts["caption"])
                    break
            if item["kind"] in {"source", "narration_source"}:
                draw.text((18, 907), "SOURCE • SCHOOL OF HARD KNOCKS", font=fonts["micro"], fill=(255, 255, 255, 175), anchor="ls")
            elif item["name"] in {"capital_stack", "value_shock", "maturity_wave"}:
                draw.text((522, 907), "ILLUSTRATION • PEXELS 37694695", font=fonts["micro"], fill=(255, 255, 255, 175), anchor="rs")
            else:
                draw.text((522, 907), "ILLUSTRATION • PEXELS 7981954", font=fonts["micro"], fill=(255, 255, 255, 175), anchor="rs")
            if item["name"] == "underwriting_guardrail":
                draw.text((270, 885), "FEDERAL RESERVE • FEDS 2024-019", font=fonts["micro"], fill=(255, 255, 255, 185), anchor="ms")
            elif item["name"] == "maturity_wave":
                draw.text((270, 885), "MORTGAGE BANKERS ASSOCIATION • 2026-03-02", font=fonts["micro"], fill=(255, 255, 255, 185), anchor="ms")
            elif item["name"] == "recourse_guardrail":
                draw.text((270, 885), "FEDERAL RESERVE • FEDS 2021-079", font=fonts["micro"], fill=(255, 255, 255, 185), anchor="ms")
        third = min(2, int(3 * frame / max(1, total_frames)))
        positions = ((16, 26), (389, 26), (16, 884))
        draw.text(positions[third], "HARD KNOCKS LAB", font=fonts["micro"], fill=(255, 255, 255, 170), anchor="la")
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
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", graph, "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", output])
    return output


def build_sfx(timeline: list[dict[str, Any]], total: float, hook_only: bool) -> Path:
    starts = {item["name"]: item["final_start"] for item in timeline}
    events: list[tuple[str, Path, float, float]] = [
        ("hook", HOOK_HIT, 0.04, -11),
        ("split", PROOF_TICK, starts["buyer_two"], -15),
        ("question", PROOF_TICK, starts["risk_answer"], -15),
    ]
    if not hook_only:
        events.extend([
            ("counter", WHOOSH, starts["counter_audit"], -11),
            ("stack", PROOF_TICK, starts["capital_stack"], -15),
            ("shock", PROOF_TICK, starts["value_shock"], -13),
            ("cushion", PROOF_TICK, starts["cashflow_cushion"], -17),
            ("underwriting", WHOOSH, starts["underwriting_guardrail"], -11),
            ("bank_risk", PROOF_TICK, starts["bank_default_risk"], -16),
            ("maturity", PROOF_TICK, starts["maturity_wave"], -14),
            ("cta_like", CTA_CLICK, starts["triple_cta"] + 0.20, -10),
            ("cta_sub", CTA_CLICK, starts["triple_cta"] + 1.05, -10),
            ("cta_comment", CTA_CLICK, starts["triple_cta"] + 1.90, -10),
            ("recourse", WHOOSH, starts["recourse_guardrail"], -11),
            ("payoff", PAYOFF_HIT, starts["first_loss_payoff"], -15),
        ])
    tracks: list[Path] = []
    sfx_work = WORK / "audio" / "sfx"
    sfx_work.mkdir(parents=True, exist_ok=True)
    for name, source, start, db in events:
        tracks.append(make_positioned_track(source, start, total, sfx_work / f"positioned_{name}.wav", math.pow(10, db / 20)))
    inputs: list[str | Path] = []
    for track in tracks:
        inputs.extend(["-i", track])
    labels = "".join(f"[{index}:a]" for index in range(len(tracks)))
    output = sfx_work / ("timed_hook.wav" if hook_only else "timed_full.wav")
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", f"{labels}amix=inputs={len(tracks)}:duration=longest:normalize=0,atrim=0:{total:.6f}[out]", "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", output])
    return output


def composite(base: Path, overlay: Path, sfx: Path, total_frames: int, output: Path) -> None:
    total = total_frames / FPS
    output.parent.mkdir(parents=True, exist_ok=True)
    graph = (
        "[1:v]scale=1080:1920:flags=lanczos,format=rgba[ov];[0:v][ov]overlay=0:0:format=auto,format=yuv420p[v];"
        "[0:a]aresample=48000,aformat=channel_layouts=stereo[basea];"
        "[2:a]aresample=48000,aformat=channel_layouts=stereo[sfx];"
        "[3:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.125[bed];"
        f"[basea][sfx][bed]amix=inputs=3:duration=longest:normalize=0,atrim=0:{total:.6f},"
        "loudnorm=I=-16.5:TP=-2.0:LRA=10,volume=-0.5dB,alimiter=limit=0.82:level=false[a]"
    )
    run(["ffmpeg", "-y", "-v", "error", "-i", base, "-i", overlay, "-i", sfx, "-i", MUSIC_BED,
         "-filter_complex", graph, "-map", "[v]", "-map", "[a]", "-frames:v", str(total_frames),
         *encode_args(), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
         "-movflags", "+faststart", "-t", f"{total:.6f}", output])


def validate_manifest() -> None:
    data = json.loads(SFX_MANIFEST.read_text(encoding="utf-8"))
    required = {
        "hardknocks_v22_hook_origin_hit",
        "hardknocks_v22_jet_motion_whoosh",
        "hardknocks_v22_proof_tick",
        "hardknocks_v22_cta_click",
        "hardknocks_v22_payoff_warm_hit",
        "hardknocks_v22_restrained_finance_bed",
    }
    approved = {item["id"] for item in data.get("assets", []) if item.get("approval_status") == "approved" and item.get("rights_status") == "cleared"}
    missing = sorted(required - approved)
    if missing:
        raise RuntimeError(f"Missing cleared manifest assets: {missing}")


def require_inputs(segments: tuple[Segment, ...]) -> None:
    required = [SOURCE, HOOK_HIT, WHOOSH, PROOF_TICK, CTA_CLICK, PAYOFF_HIT, MUSIC_BED, SFX_MANIFEST, FONT_KOMIKA, FONT_BOLD, FONT_BLACK]
    for segment in segments:
        if segment.visual is not None:
            required.append(segment.visual)
        if segment.audio is not None:
            required.append(segment.audio)
    missing = sorted({str(path) for path in required if not path.exists()})
    if missing:
        raise FileNotFoundError("Missing inputs:\n" + "\n".join(missing))
    validate_manifest()


def probe(path: Path) -> dict[str, Any]:
    result = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path], capture=True)
    return json.loads(result.stdout)


def validate_final(timeline: list[dict[str, Any]]) -> dict[str, Any]:
    data = probe(FINAL)
    video = next(stream for stream in data["streams"] if stream["codec_type"] == "video")
    audio = next(stream for stream in data["streams"] if stream["codec_type"] == "audio")
    duration = float(data["format"]["duration"])
    source_segments = [item for item in timeline if item["source_duration"] > 0]
    total_source = sum(item["source_duration"] for item in source_segments)
    cta_start = next(item["final_start"] for item in timeline if item["name"] == "triple_cta")
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
        "three_source_mix": SOURCE.exists() and PEXELS_PROPERTY.exists() and PEXELS_CONTRACT.exists() and OVERLAY.exists(),
        "commentary_track": all(segment.audio is not None and segment.audio.exists() for segment in SEGMENTS if segment.kind.startswith("narration")),
        "cta_window": 38.0 <= cta_start <= 42.0,
        "caption_at_frame_zero": CAPTIONS["deal_ten_million"][0][0] <= 0.2,
    }
    if not all(checks.values()):
        raise RuntimeError(f"Final validation failed: {checks}")
    report = {
        "final": str(FINAL),
        "sha256": sha256(FINAL),
        "duration": duration,
        "checks": checks,
        "cta_start": cta_start,
        "total_source_duration": total_source,
        "source_duration": SOURCE_DURATION,
        "source_use_percent": 100 * total_source / SOURCE_DURATION,
        "timeline": timeline,
    }
    TIMELINE_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def write_hook_scorecard() -> None:
    rows = []
    for variant_id, mechanism, scores in HOOK_VARIANTS:
        rows.append({
            "id": variant_id,
            "mechanism": mechanism,
            "scores": dict(zip(("curiosity_gap", "specificity", "visual", "emotion", "payoff", "novelty"), scores)),
            "total": sum(scores),
            "selected": variant_id == "source_decision_lock",
        })
    rows.sort(key=lambda row: (row["total"], row["scores"]["curiosity_gap"]), reverse=True)
    HOOK_SCORECARD.write_text(json.dumps({"rubric_max": 60, "tie_breaker": "curiosity_gap", "variants": rows}, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    for directory in (WORK, SEGMENT_DIR, CHECKS, HOOK_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    write_hook_scorecard()
    segments = SEGMENTS[:HOOK_SEGMENT_COUNT] if args.hook_only else SEGMENTS
    require_inputs(segments)
    suffix = "_hook" if args.hook_only else ""
    base, timeline, total_frames = build_base(segments, suffix)
    overlay = HOOK_DIR / "overlay_hook.mov" if args.hook_only else OVERLAY
    build_overlay(timeline, total_frames, overlay)
    sfx = build_sfx(timeline, total_frames / FPS, args.hook_only)
    output = ROUGH_HOOK if args.hook_only else FINAL
    composite(base, overlay, sfx, total_frames, output)
    if args.hook_only:
        print(json.dumps({"rough_hook": str(output), "duration": total_frames / FPS, "timeline": timeline}, indent=2))
    else:
        print(json.dumps(validate_final(timeline), indent=2))


if __name__ == "__main__":
    main()
