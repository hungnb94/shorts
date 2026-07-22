#!/usr/bin/env python3
"""Render an English speech-bubble text trial over OUTWISHED episode 001."""

from __future__ import annotations

import json
import math
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "output/projects/outwished/final/2026-07-22-outwished-001-trimmed-visual-cut.mp4"
WORK = ROOT / "output/projects/outwished/work/dialogue-text-trial"
FINAL_DIR = ROOT / "output/projects/outwished/final"
ANALYSIS_DIR = ROOT / "output/projects/outwished/analysis"
FINAL = FINAL_DIR / "2026-07-22-outwished-001-dialogue-text-trial.mp4"
MANIFEST = FINAL_DIR / "2026-07-22-outwished-001-dialogue-text-trial.json"
CONTACT_SHEET = ANALYSIS_DIR / "2026-07-22-outwished-001-dialogue-text-contact-sheet.jpg"
FONT_REGULAR = Path("/System/Library/Fonts/Supplemental/Comic Sans MS.ttf")
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Comic Sans MS Bold.ttf")
CANVAS = (1080, 1920)

Kind = Literal["speech", "thought", "system"]


@dataclass(frozen=True)
class BubbleEvent:
    start: float
    end: float
    speaker: str
    text: str
    box: tuple[int, int, int, int]
    anchor: tuple[int, int] | None
    kind: Kind = "speech"


HOOK_THOUGHT = (300, 1290, 700, 240)
INTRUSION_THOUGHT = (340, 1320, 670, 240)
CALL_BUBBLE = (360, 1350, 650, 240)
RESCUE_OFFICER = (210, 1400, 790, 240)
RESCUE_NICO = (60, 1400, 680, 240)
BETRAYAL_NICO = (60, 100, 760, 250)
BETRAYAL_COP = (260, 100, 760, 250)
VAULT_RULE = (60, 100, 720, 240)
BASEMENT_COP = (320, 100, 700, 240)
BASEMENT_THOUGHT = (60, 100, 650, 240)
DISCOVERY_THOUGHT = (60, 100, 600, 240)
VEYR_REVEAL = (600, 100, 430, 240)
SHOT9_NICO = (40, 100, 560, 240)
SHOT9_VEYR = (40, 100, 520, 240)
NICO_OFFSCREEN = (40, 1320, 480, 240)
VEYR_GRANTED = (40, 100, 380, 220)
STACKED_COP = (560, 1550, 480, 220)
SYSTEM_PANEL = (130, 100, 820, 240)

EVENTS: list[BubbleEvent] = [
    BubbleEvent(0.20, 1.50, "NICO", "THAT OFFICER...", HOOK_THOUGHT, (260, 820), "thought"),
    BubbleEvent(1.55, 2.75, "NICO", "KNEW MY SAFE CODE.", HOOK_THOUGHT, (260, 820), "thought"),
    BubbleEvent(2.80, 3.80, "NICO", "I'D NEVER MET HIM.", HOOK_THOUGHT, (260, 820), "thought"),
    BubbleEvent(4.15, 5.45, "NICO", "TEN MINUTES EARLIER...", INTRUSION_THOUGHT, (300, 800), "thought"),
    BubbleEvent(5.50, 6.80, "NICO", "TWO MEN BROKE IN.", INTRUSION_THOUGHT, (300, 800), "thought"),
    BubbleEvent(6.85, 8.25, "NICO", "TO MY HOUSE.", INTRUSION_THOUGHT, (300, 800), "thought"),
    BubbleEvent(8.55, 9.60, "NICO", "HOME INVASION.", CALL_BUBBLE, (310, 900)),
    BubbleEvent(9.65, 10.70, "NICO", "TWO SUSPECTS.", CALL_BUBBLE, (310, 900)),
    BubbleEvent(10.75, 12.25, "NICO", "SEND POLICE.", CALL_BUBBLE, (310, 900)),
    BubbleEvent(13.80, 15.35, "OFFICER", "YOU'RE SAFE NOW, SIR.", RESCUE_OFFICER, (790, 920)),
    BubbleEvent(15.55, 17.10, "NICO", "THAT WAS FAST.", RESCUE_NICO, (250, 920)),
    BubbleEvent(18.80, 20.25, "NICO", "YOU'RE WITH THE BURGLARS?", BETRAYAL_NICO, (20, 900)),
    BubbleEvent(20.35, 22.30, "CORRUPT COP", "I'M THEIR THIRD PARTNER.", BETRAYAL_COP, (790, 940)),
    BubbleEvent(22.80, 24.00, "CORRUPT COP", "KEEP THE VAULT OPEN.", VAULT_RULE, (930, 1150)),
    BubbleEvent(24.05, 25.45, "CORRUPT COP", "IF IT CLOSES WITH", VAULT_RULE, (930, 1150)),
    BubbleEvent(25.50, 26.75, "CORRUPT COP", "ANYONE INSIDE...", VAULT_RULE, (930, 1150)),
    BubbleEvent(26.80, 28.30, "CORRUPT COP", "POLICE GET AN ALERT.", VAULT_RULE, (930, 1150)),
    BubbleEvent(28.60, 30.05, "CORRUPT COP", "LOCK HIM DOWNSTAIRS.", BASEMENT_COP, (1060, 720)),
    BubbleEvent(30.20, 32.10, "NICO", "WORST RESCUE EVER.", BASEMENT_THOUGHT, (310, 900), "thought"),
    BubbleEvent(33.70, 35.10, "NICO", "A HIDDEN CHAMBER?", DISCOVERY_THOUGHT, (330, 900), "thought"),
    BubbleEvent(35.15, 36.65, "NICO", "MY RING OPENED IT.", DISCOVERY_THOUGHT, (330, 900), "thought"),
    BubbleEvent(36.70, 38.15, "NICO", "AN OLD LAMP...", DISCOVERY_THOUGHT, (330, 900), "thought"),
    BubbleEvent(39.55, 41.20, "VEYR", "ALADDIN'S HEIR.", VEYR_REVEAL, (500, 820)),
    BubbleEvent(41.60, 42.75, "NICO", "CAN YOU GRANT WISHES?", SHOT9_NICO, (170, 900)),
    BubbleEvent(42.80, 43.95, "VEYR", "I OBEY WORDING.", SHOT9_VEYR, (880, 650)),
    BubbleEvent(44.00, 45.10, "VEYR", "RESULTS VARY.", SHOT9_VEYR, (880, 650)),
    BubbleEvent(45.15, 45.95, "NICO", "I WISH...", SHOT9_NICO, (170, 900)),
    BubbleEvent(46.00, 46.85, "NICO", "ALL THREE THIEVES...", SHOT9_NICO, (170, 900)),
    BubbleEvent(46.90, 47.70, "NICO", "LOCKED INSIDE...", SHOT9_NICO, (170, 900)),
    BubbleEvent(47.75, 48.60, "NICO", "THE VAULT.", SHOT9_NICO, (170, 900)),
    BubbleEvent(48.65, 49.60, "VEYR", "EVEN THE COP?", SHOT9_VEYR, (880, 650)),
    BubbleEvent(49.65, 50.35, "NICO", "ESPECIALLY HIM.", NICO_OFFSCREEN, (20, 1720)),
    BubbleEvent(50.55, 51.65, "VEYR", "GRANTED.", VEYR_GRANTED, (20, 700)),
    BubbleEvent(51.75, 53.45, "CORRUPT COP", "WHY ARE WE STACKED?!", STACKED_COP, (690, 1450)),
    BubbleEvent(53.55, 54.85, "CORRUPT COP", "OPEN THIS DOOR!", STACKED_COP, (690, 1450)),
    BubbleEvent(55.00, 57.60, "SYSTEM", "OCCUPANTS: 3\nOTHER OFFICERS ALERTED", SYSTEM_PANEL, None, "system"),
]

STYLES: dict[str, dict[str, tuple[int, ...]]] = {
    "NICO": {
        "fill": (255, 246, 214, 245),
        "outline": (21, 185, 190, 255),
        "text": (23, 29, 35, 255),
        "label": (7, 100, 107, 255),
    },
    "OFFICER": {
        "fill": (255, 255, 255, 245),
        "outline": (222, 57, 57, 255),
        "text": (24, 28, 38, 255),
        "label": (164, 27, 27, 255),
    },
    "CORRUPT COP": {
        "fill": (255, 255, 255, 245),
        "outline": (222, 57, 57, 255),
        "text": (24, 28, 38, 255),
        "label": (164, 27, 27, 255),
    },
    "VEYR": {
        "fill": (65, 29, 82, 248),
        "outline": (43, 224, 226, 255),
        "text": (255, 255, 255, 255),
        "label": (90, 240, 241, 255),
    },
    "SYSTEM": {
        "fill": (18, 25, 34, 248),
        "outline": (43, 224, 226, 255),
        "text": (255, 255, 255, 255),
        "label": (90, 240, 241, 255),
    },
}


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(command))
    return subprocess.run(command, check=True, capture_output=capture, text=True)


def probe_duration(path: Path) -> float:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture=True,
    )
    return float(result.stdout.strip())


def wrapped_lines(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    if "\n" in text:
        return text.splitlines()
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        width = draw.textbbox((0, 0), candidate, font=font, stroke_width=1)[2]
        if current and width > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    max_height: int,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    for size in range(72, 41, -2):
        font = ImageFont.truetype(str(FONT_BOLD), size)
        lines = wrapped_lines(draw, text, font, max_width)
        if len(lines) > 2:
            continue
        line_gap = max(8, size // 7)
        heights = [draw.textbbox((0, 0), line, font=font, stroke_width=1)[3] for line in lines]
        total_height = sum(heights) + line_gap * (len(lines) - 1)
        if total_height <= max_height:
            return font, lines, line_gap
    raise ValueError(f"Text does not fit at minimum font size: {text!r}")


def nearest_edge_point(box: tuple[int, int, int, int], anchor: tuple[int, int]) -> tuple[int, int]:
    x, y, width, height = box
    ax, ay = anchor
    candidates = [
        (max(x + 70, min(ax, x + width - 70)), y),
        (max(x + 70, min(ax, x + width - 70)), y + height),
        (x, max(y + 70, min(ay, y + height - 70))),
        (x + width, max(y + 70, min(ay, y + height - 70))),
    ]
    return min(candidates, key=lambda point: math.dist(point, anchor))


def draw_tail(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    anchor: tuple[int, int],
    fill: tuple[int, ...],
    outline: tuple[int, ...],
    thought: bool,
) -> None:
    edge_x, edge_y = nearest_edge_point(box, anchor)
    if thought:
        for fraction, radius in ((0.28, 18), (0.52, 25), (0.76, 33)):
            cx = round(anchor[0] + (edge_x - anchor[0]) * fraction)
            cy = round(anchor[1] + (edge_y - anchor[1]) * fraction)
            draw.ellipse(
                (cx - radius, cy - radius, cx + radius, cy + radius),
                fill=fill,
                outline=outline,
                width=7,
            )
        return

    dx = edge_x - anchor[0]
    dy = edge_y - anchor[1]
    length = max(1.0, math.hypot(dx, dy))
    perpendicular = (-dy / length, dx / length)
    half_base = 34
    base_one = (
        round(edge_x + perpendicular[0] * half_base),
        round(edge_y + perpendicular[1] * half_base),
    )
    base_two = (
        round(edge_x - perpendicular[0] * half_base),
        round(edge_y - perpendicular[1] * half_base),
    )
    draw.polygon([base_one, base_two, anchor], fill=fill)
    draw.line([base_one, anchor, base_two], fill=outline, width=8, joint="curve")


def render_event(event: BubbleEvent, path: Path) -> None:
    image = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    style = STYLES[event.speaker]
    x, y, width, height = event.box
    if not (40 <= x and 40 <= y and x + width <= 1040 and y + height <= 1880):
        raise ValueError(f"Unsafe bubble margins for {event}")

    if event.anchor is not None:
        draw_tail(
            draw,
            event.box,
            event.anchor,
            style["fill"],
            style["outline"],
            event.kind == "thought",
        )
    draw.rounded_rectangle(
        (x, y, x + width, y + height),
        radius=44 if event.kind != "system" else 24,
        fill=style["fill"],
        outline=style["outline"],
        width=9,
    )

    label_font = ImageFont.truetype(str(FONT_BOLD), 34)
    draw.text(
        (x + 38, y + 24),
        event.speaker,
        font=label_font,
        fill=style["label"],
        stroke_width=1,
        stroke_fill=style["label"],
    )
    text_font, lines, line_gap = fit_text(draw, event.text, width - 76, height - 105)
    line_heights = [draw.textbbox((0, 0), line, font=text_font, stroke_width=1)[3] for line in lines]
    total_height = sum(line_heights) + line_gap * (len(lines) - 1)
    text_y = y + 87 + max(0, (height - 105 - total_height) // 2)
    for line, line_height in zip(lines, line_heights):
        line_width = draw.textbbox((0, 0), line, font=text_font, stroke_width=1)[2]
        text_x = x + (width - line_width) // 2
        draw.text(
            (text_x, text_y),
            line,
            font=text_font,
            fill=style["text"],
            stroke_width=1,
            stroke_fill=style["text"],
        )
        text_y += line_height + line_gap
    image.save(path)


def validate_events(duration: float) -> None:
    if not BASE.exists():
        raise FileNotFoundError(BASE)
    for font in (FONT_REGULAR, FONT_BOLD):
        if not font.exists():
            raise FileNotFoundError(font)
    previous_end = 0.0
    for event in EVENTS:
        if not 0 <= event.start < event.end <= duration:
            raise ValueError(f"Invalid event timing: {event}")
        if event.start < previous_end:
            raise ValueError(f"Overlapping bubble events around {event.start:.2f}s")
        if event.end - event.start < 0.70:
            raise ValueError(f"Bubble event is too short to read: {event}")
        previous_end = event.end


def render_video() -> None:
    command = ["ffmpeg", "-y", "-i", str(BASE)]
    overlay_paths = []
    for index, event in enumerate(EVENTS, 1):
        overlay_path = WORK / f"bubble-{index:02d}.png"
        render_event(event, overlay_path)
        overlay_paths.append(overlay_path)
        command.extend(["-i", str(overlay_path)])

    filter_parts = ["[0:v]fps=24,settb=1/24,setpts=N[base]"]
    current = "base"
    for index, event in enumerate(EVENTS, 1):
        output = f"v{index}"
        filter_parts.append(
            f"[{current}][{index}:v]overlay=x=0:y=0:eof_action=repeat:shortest=0:"
            f"enable='between(t,{event.start:.3f},{event.end:.3f})'[{output}]"
        )
        current = output
    filter_parts.append(f"[{current}]fps=24,settb=1/24,setpts=N[vout]")

    command.extend(
        [
            "-filter_complex",
            ";".join(filter_parts),
            "-map",
            "[vout]",
            "-map",
            "0:a:0",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "16",
            "-profile:v",
            "high",
            "-level:v",
            "4.2",
            "-pix_fmt",
            "yuv420p",
            "-r",
            "24",
            "-fps_mode",
            "cfr",
            "-video_track_timescale",
            "12288",
            "-c:a",
            "copy",
            "-movflags",
            "+faststart",
            str(FINAL),
        ]
    )
    run(command)


def write_manifest(duration: float) -> None:
    manifest: dict[str, Any] = {
        "artifact": str(FINAL.relative_to(ROOT)),
        "kind": "speech-bubble text trial; not upload-final",
        "source": str(BASE.relative_to(ROOT)),
        "duration_seconds": duration,
        "font": {
            "requested_profile": "Komika Axis",
            "actual_fallback": str(FONT_BOLD),
            "reason": "Komika Axis is not installed on this host; fc-match fell back to Verdana",
        },
        "events": [asdict(event) for event in EVENTS],
        "remaining_gates": [
            "SHOT-011 and SHOT-012 have no generated MP4",
            "final voice-over/dialogue mix",
            "CTA and moving watermark",
            "publishing metadata and upload settings",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def make_contact_sheet() -> None:
    interval = probe_duration(FINAL) / 20
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(FINAL),
            "-vf",
            f"fps=1/{interval:.6f},scale=216:-2:flags=lanczos,tile=5x4:padding=4:margin=4:color=black",
            "-frames:v",
            "1",
            str(CONTACT_SHEET),
        ]
    )


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    duration = probe_duration(BASE)
    validate_events(duration)
    render_video()
    final_duration = probe_duration(FINAL)
    write_manifest(final_duration)
    make_contact_sheet()
    print(FINAL)
    print(MANIFEST)
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
