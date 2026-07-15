#!/usr/bin/env python3
"""Render Hard Knocks V6: Arthur Blank's customer-first growth story.

The edit keeps the interview's original voice continuous: critics predict failure,
Home Depot is revealed, Blank explains the public-company proof, then closes on the
listening and trust mechanism. Editorial value comes from measured captions, a
trust-funnel annotation, and small Pexels evidence inserts that never replace him.

Every extracted source piece is under 15 seconds and the complete edit uses less
than 4% of the original interview's duration.
"""

from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "hardknocks"
SOURCE = PROJECT / "source" / "cxYLRCwX_aM.mp4"
PEXELS = ROOT / "output/shared/pexels/inventory_worker_7018664.mp4"
WORK = PROJECT / "clips" / "v6_work"
PANELS = WORK / "panels"
TTS = WORK / "tts"
CHECKS = WORK / "checks"
FINAL = PROJECT / "final" / "2026-07-15-hardknocks_v6_customer_friction_moat.mp4"
EDGE_TTS = Path.home() / ".local" / "bin" / "edge-tts"
EDGE_TTS_VOICE = "en-US-AriaNeural"

WIDTH = 1080
HEIGHT = 1920
FPS = 30
POST_SPEED = 1.04
MAX_POST_TEMPO = 1.15
FINISH_PAD = 0.70
SOURCE_DURATION = 1647.621

# Raw-timeline start, end, and Pexels source offset. These remain small corner
# inserts; the interview subject stays visible and his original audio stays intact.
PEXELS_OVERLAYS = (
    (24.0, 29.0, 0.0),
    (33.0, 38.0, 5.0),
)

FONT_REGULAR = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")

NAVY = "#07111F"
PANEL = "#10233A"
WHITE = "#F8FAFC"
MUTED = "#AAB8C8"
YELLOW = "#FFD447"
GREEN = "#4EE6A8"
RED = "#FF5A67"
CYAN = "#55C7FF"


@dataclass(frozen=True)
class TimelineClip:
    name: str
    start_frame: int
    frames: int
    kind: str
    source_start: float | None = None
    pexels_start: float | None = None
    crop_focus: float = 0.63
    zoom: float = 1.0

    @property
    def end_frame(self) -> int:
        return self.start_frame + self.frames


@dataclass(frozen=True)
class ClipPlan:
    name: str
    frames: int
    kind: str
    source_start: float | None = None
    pexels_start: float | None = None
    crop_focus: float = 0.63
    zoom: float = 1.0


@dataclass(frozen=True)
class TTSLine:
    name: str
    start_frame: int
    frames: int
    text: str
    synthesis_text: str
    rate_percent: int
    pitch_hz: int


def build_timeline() -> list[TimelineClip]:
    plans = [
        # 0-6.20s: four visual punches plus the bankruptcy sting. The audio is
        # contiguous within each phrase; only dead connective tissue is removed.
        ClipPlan("hook_nuts_a", 35, "source", 1476.76, crop_focus=0.63, zoom=1.52),
        ClipPlan("hook_nuts_b", 35, "source", 1477.9267, crop_focus=0.63, zoom=1.60),
        ClipPlan("hook_inventory", 39, "source", 1479.36, crop_focus=0.63, zoom=1.54),
        ClipPlan("hook_people_price", 39, "source", 1480.66, crop_focus=0.63, zoom=1.62),
        ClipPlan("hook_broke", 38, "source", 1488.30, crop_focus=0.63, zoom=1.56),
        # Reveal and origin. Full-screen Pexels is intentionally forbidden here.
        ClipPlan("reveal_home_depot_a", 66, "source", 44.40, crop_focus=0.63, zoom=1.44),
        ClipPlan("reveal_home_depot_b", 67, "source", 46.60, crop_focus=0.63, zoom=1.50),
        # Keep the host's setup and Blank's answer together instead of inserting
        # commentary between them.
        ClipPlan("context_fired", 76, "source", 1465.76, crop_focus=0.63, zoom=1.46),
        ClipPlan("context_doubt", 97, "source", 1468.293333, crop_focus=0.63, zoom=1.50),
        ClipPlan("answer_absolutely", 18, "source", 1471.52, crop_focus=0.63, zoom=1.54),
        # Public-company proof: contiguous source audio split only for visual cadence.
        ClipPlan("public_a", 45, "source", 1489.32, crop_focus=0.63, zoom=1.34),
        ClipPlan("revenue_a", 94, "source", 1495.12, crop_focus=0.63, zoom=1.36),
        ClipPlan("revenue_b", 94, "source", 1498.253333, crop_focus=0.63, zoom=1.42),
        ClipPlan("revenue_c", 93, "source", 1501.386667, crop_focus=0.63, zoom=1.38),
        # Mechanism and humility remain in Blank's words.
        ClipPlan("listen_a", 72, "source", 1504.473333, crop_focus=0.63, zoom=1.34),
        ClipPlan("listen_b", 72, "source", 1506.873333, crop_focus=0.63, zoom=1.40),
        ClipPlan("listen_c", 72, "source", 1509.273333, crop_focus=0.63, zoom=1.36),
        ClipPlan("humility_a", 115, "source", 1511.673333, crop_focus=0.63, zoom=1.42),
        ClipPlan("humility_b", 114, "source", 1515.506667, crop_focus=0.63, zoom=1.38),
        # Finish on Blank's natural hearts/minds/wallets payoff, not a TTS CTA.
        ClipPlan("trust_a", 80, "source", 1591.52, crop_focus=0.63, zoom=1.34),
        ClipPlan("trust_b", 80, "source", 1594.186667, crop_focus=0.63, zoom=1.40),
        ClipPlan("trust_c", 80, "source", 1596.853333, crop_focus=0.63, zoom=1.36),
        ClipPlan("trust_d", 80, "source", 1599.52, crop_focus=0.63, zoom=1.42),
        ClipPlan("trust_e", 80, "source", 1602.186667, crop_focus=0.63, zoom=1.38),
        ClipPlan("trust_f", 91, "source", 1604.853333, crop_focus=0.63, zoom=1.44),
    ]
    timeline: list[TimelineClip] = []
    cursor = 0
    for plan in plans:
        timeline.append(
            TimelineClip(
                name=plan.name,
                start_frame=cursor,
                frames=plan.frames,
                kind=plan.kind,
                source_start=plan.source_start,
                pexels_start=plan.pexels_start,
                crop_focus=plan.crop_focus,
                zoom=plan.zoom,
            )
        )
        cursor += plan.frames
    return timeline


TIMELINE = build_timeline()
TOTAL_FRAMES = TIMELINE[-1].end_frame
RAW_DURATION = TOTAL_FRAMES / FPS

# First caption arrives at 0.10s; the face is already moving at frame 0.
HOOK_CAPTIONS = [
    (0.10, 1.15, "THEY CALLED HIM"),
    (1.15, 2.3333, "CRAZY."),
    (2.3333, 3.6333, "TOO MUCH INVENTORY"),
    (3.6333, 4.9333, "TOO MANY EMPLOYEES"),
    (4.9333, 6.20, "HE'LL GO BROKE"),
]

CAPTIONS = [
    *[(start, end, "Hook", text) for start, end, text in HOOK_CAPTIONS],
    (6.20, 7.35, "Caption", "EVER HEARD OF"),
    (7.35, 8.65, "Emphasis", "HOME DEPOT?"),
    (8.65, 10.6333, "Caption", "THAT WAS MY COMPANY"),
    (10.6333, 11.90, "Danger", "AT 36 YEARS OLD"),
    (11.90, 13.1667, "Danger", "YOU WERE FIRED"),
    (13.1667, 14.80, "Caption", "DID PEOPLE DOUBT YOU?"),
    (14.80, 16.40, "Caption", "THINK YOU WERE CRAZY?"),
    (16.40, 17.00, "Emphasis", "ABSOLUTELY."),
    (17.00, 18.50, "Emphasis", "IN SEPTEMBER '81: PUBLIC"),
    (18.50, 20.40, "Caption", "AND THE VOLUMES"),
    (20.40, 22.00, "Emphasis", "WERE UNBELIEVABLE"),
    (22.00, 24.00, "Caption", "THE AMOUNT OF REVENUE"),
    (24.00, 25.60, "Caption", "FROM FOUR STORES"),
    (25.60, 27.8667, "Caption", "ALL AS A RESPONSE OF"),
    (27.8667, 29.70, "Emphasis", "LISTENING + RESPONDING"),
    (29.70, 31.40, "Caption", "WHAT CUSTOMERS WANTED"),
    (31.40, 33.20, "Caption", "NOT DEBATING"),
    (33.20, 35.0667, "Emphasis", "LEARNING FROM THEM"),
    (35.0667, 36.70, "Caption", "TRUE HUMILITY"),
    (36.70, 39.00, "Caption", "THE PEOPLE WE SERVE"),
    (39.00, 42.70, "Emphasis", "KNOW BETTER THAN WE DO"),
    (42.70, 44.40, "Caption", "IN ALL THESE BUSINESSES"),
    (44.40, 46.00, "Emphasis", "DEVELOP THE TRUST"),
    (46.00, 48.00, "Caption", "ASSOCIATES OR CUSTOMERS"),
    (48.00, 50.20, "Caption", "ONCE TRUST IS ESTABLISHED"),
    (50.20, 52.00, "Caption", "OPEN THEIR HEARTS"),
    (52.00, 53.50, "Caption", "AND THEIR MINDS"),
    (53.50, 55.80, "Emphasis", "EVENTUALLY THEIR WALLETS"),
    (55.80, RAW_DURATION, "Emphasis", "A TRUST RELATIONSHIP"),
]


def tts_lines() -> list[TTSLine]:
    return []


def source_usage_ratio(timeline: list[TimelineClip]) -> float:
    source_seconds = sum(
        clip.frames for clip in timeline if clip.kind == "source"
    ) / FPS
    return source_seconds / SOURCE_DURATION


def final_duration() -> float:
    return (RAW_DURATION + FINISH_PAD) / POST_SPEED


def validate_timeline(timeline: list[TimelineClip], *, total_frames: int) -> None:
    if not timeline:
        raise ValueError("timeline is empty")
    cursor = 0
    for clip in timeline:
        if clip.start_frame != cursor:
            raise ValueError(f"timeline gap or overlap at {clip.name}")
        if clip.frames <= 0:
            raise ValueError(f"non-positive clip duration: {clip.name}")
        if clip.kind == "source":
            if clip.source_start is None:
                raise ValueError(f"source start missing: {clip.name}")
            if clip.frames / FPS >= 15.0:
                raise ValueError(f"source clip reaches 15 seconds: {clip.name}")
        if clip.kind == "pexels" and clip.pexels_start is None:
            raise ValueError(f"Pexels start missing: {clip.name}")
        cursor = clip.end_frame
    if cursor != total_frames:
        raise ValueError(f"timeline total mismatch: {cursor} != {total_frames}")
    if source_usage_ratio(timeline) > 0.5:
        raise ValueError(
            f"source usage exceeds 50%: {source_usage_ratio(timeline):.4f}"
        )
    duration = final_duration()
    if not 45.0 <= duration <= 60.0:
        raise ValueError(f"final duration out of range: {duration:.3f}s")
    if min(window[0] for window in PEXELS_OVERLAYS) / POST_SPEED < 10.0:
        raise ValueError("Pexels insert enters before the 10-second face window")


def run(args: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(str(arg) for arg in args))
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=capture,
    )


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
        capture=True,
    )
    return json.loads(result.stdout)


def probe_duration(path: Path) -> float:
    return float(probe(path)["format"]["duration"])


def max_volume_db(
    path: Path,
    *,
    start: float | None = None,
    duration: float | None = None,
) -> float:
    args = ["ffmpeg", "-hide_banner"]
    if start is not None:
        args.extend(["-ss", f"{start:.6f}"])
    args.extend(["-i", str(path)])
    if duration is not None:
        args.extend(["-t", f"{duration:.6f}"])
    args.extend(["-vn", "-af", "volumedetect", "-f", "null", "-"])
    result = subprocess.run(args, cwd=ROOT, check=True, text=True, capture_output=True)
    match = re.search(r"max_volume:\s*(-?\d+(?:\.\d+)?) dB", result.stderr)
    if not match:
        raise RuntimeError(f"Could not measure max volume for {path}")
    return float(match.group(1))


def assert_not_silent(
    path: Path,
    *,
    label: str,
    threshold_db: float = -40.0,
    start: float | None = None,
    duration: float | None = None,
) -> float:
    measured = max_volume_db(path, start=start, duration=duration)
    if measured <= threshold_db:
        raise AssertionError(
            f"{label} is silent: max_volume={measured:.1f} dB, threshold={threshold_db:.1f} dB"
        )
    print(f"AUDIO PASS {label}: max_volume={measured:.1f} dB")
    return measured


def require_inputs() -> None:
    required = [SOURCE, PEXELS, FONT_REGULAR, FONT_BOLD]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required inputs:\n" + "\n".join(missing))
    validate_timeline(TIMELINE, total_frames=TOTAL_FRAMES)
    for directory in [WORK, PANELS, TTS, CHECKS, FINAL.parent]:
        directory.mkdir(parents=True, exist_ok=True)


def font(size: int, *, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size=size)


def centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    *,
    size: int,
    color: str = WHITE,
    max_width: int = 920,
) -> None:
    chosen = font(size)
    while draw.textbbox((0, 0), text, font=chosen)[2] > max_width and chosen.size > 42:
        chosen = font(int(chosen.size - 2))
    bbox = draw.textbbox((0, 0), text, font=chosen, stroke_width=2)
    x = (WIDTH - (bbox[2] - bbox[0])) // 2
    draw.text((x, y), text, font=chosen, fill=color, stroke_width=2, stroke_fill="#000000")


def panel_background() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), NAVY)
    draw = ImageDraw.Draw(image)
    top = (7, 17, 31)
    bottom = (15, 39, 56)
    for y in range(HEIGHT):
        ratio = y / (HEIGHT - 1)
        color = tuple(round(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(3))
        draw.line((0, y, WIDTH, y), fill=color)
    for x in range(50, WIDTH, 120):
        draw.line((x, 0, x, HEIGHT), fill="#12283E", width=1)
    for y in range(50, HEIGHT, 120):
        draw.line((0, y, WIDTH, y), fill="#12283E", width=1)
    return image


def rounded_card(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    title: str,
    value: str,
    accent: str,
) -> None:
    draw.rounded_rectangle(box, radius=34, fill=PANEL, outline=accent, width=6)
    x1, y1, x2, _ = box
    centered_text(draw, title, y1 + 38, size=48, color=MUTED, max_width=x2 - x1 - 60)
    centered_text(draw, value, y1 + 125, size=68, color=accent, max_width=x2 - x1 - 60)


def create_panels() -> dict[str, Path]:
    outputs: dict[str, Path] = {}

    price = panel_background()
    draw = ImageDraw.Draw(price)
    centered_text(draw, "THE CUSTOMER-FRICTION FLYWHEEL", 170, size=58, color=YELLOW)
    rounded_card(draw, (90, 430, 990, 710), title="MORE INVENTORY", value="FEWER EMPTY SHELVES", accent=CYAN)
    rounded_card(draw, (90, 780, 990, 1060), title="MORE STAFF", value="ANSWERS NOW", accent=GREEN)
    rounded_card(draw, (90, 1130, 990, 1410), title="LOWER PRICES", value="TRUST", accent=YELLOW)
    centered_text(draw, "WHAT LOOKED INEFFICIENT FELT EFFORTLESS", 1520, size=42, color=WHITE)
    outputs["price_matrix"] = PANELS / "price_matrix.png"
    price.save(outputs["price_matrix"])

    cut = panel_background()
    draw = ImageDraw.Draw(cut)
    centered_text(draw, "THE GUARDRAIL", 190, size=58, color=YELLOW)
    centered_text(draw, "CUT COSTS", 480, size=92, color=RED)
    centered_text(draw, "WHERE CUSTOMERS", 690, size=64, color=WHITE)
    centered_text(draw, "CAN'T FEEL IT", 790, size=82, color=WHITE)
    draw.line((180, 1040, 900, 1040), fill=MUTED, width=4)
    centered_text(draw, "HIDDEN WASTE / DEAD STEPS", 1140, size=40, color=MUTED, max_width=900)
    centered_text(draw, "BACK-OFFICE DRAG", 1230, size=40, color=MUTED, max_width=900)
    outputs["guardrail_cut"] = PANELS / "guardrail_cut.png"
    cut.save(outputs["guardrail_cut"])

    invest = panel_background()
    draw = ImageDraw.Draw(invest)
    centered_text(draw, "OVERINVEST", 350, size=94, color=GREEN)
    centered_text(draw, "ONLY WHERE", 560, size=58, color=WHITE)
    centered_text(draw, "FRICTION REPEATS", 690, size=82, color=YELLOW)
    for index, label in enumerate(("OUT OF STOCK", "NO ANSWER", "NO TRUST")):
        y = 1030 + index * 160
        draw.rounded_rectangle((150, y, 930, y + 105), radius=25, fill=PANEL, outline=GREEN, width=4)
        centered_text(draw, label, y + 22, size=46, color=WHITE, max_width=720)
    outputs["guardrail_invest"] = PANELS / "guardrail_invest.png"
    invest.save(outputs["guardrail_invest"])

    close = panel_background()
    draw = ImageDraw.Draw(close)
    centered_text(draw, "LOWER COST", 360, size=82, color=MUTED)
    centered_text(draw, "IS NOT THE MOAT", 500, size=54, color=RED)
    draw.line((180, 720, 900, 720), fill=MUTED, width=4)
    centered_text(draw, "LOWER FRICTION", 850, size=92, color=GREEN)
    centered_text(draw, "IS THE MOAT", 1010, size=64, color=YELLOW)
    centered_text(draw, "WHAT WOULD YOUR CUSTOMERS LOVE?", 1400, size=52, color=WHITE)
    outputs["close"] = PANELS / "close.png"
    close.save(outputs["close"])

    return outputs


def encode_args() -> list[str]:
    return [
        "-c:v",
        "libx264",
        "-crf",
        "18",
        "-preset",
        "fast",
        "-pix_fmt",
        "yuv420p",
        "-r",
        str(FPS),
    ]


def silent_audio_input(duration: float) -> list[str]:
    return [
        "-f",
        "lavfi",
        "-t",
        f"{duration:.6f}",
        "-i",
        "anullsrc=channel_layout=stereo:sample_rate=48000",
    ]


def render_source_clip(clip: TimelineClip) -> Path:
    output = WORK / f"{clip.name}.mp4"
    duration = clip.frames / FPS
    scaled_width = 3414
    crop_x = round((scaled_width - WIDTH) * clip.crop_focus)
    zoom_width = round(WIDTH * clip.zoom)
    zoom_height = round(HEIGHT * clip.zoom)
    vf = (
        f"scale={scaled_width}:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:{crop_x}:0,"
        f"scale={zoom_width}:{zoom_height}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:(in_w-{WIDTH})/2:(in_h-{HEIGHT})/2,"
        "eq=contrast=1.04:saturation=1.05,"
        "drawbox=x=0:y=1640:w=iw:h=280:color=black@1.0:t=fill,"
        f"fps={FPS},setsar=1,format=yuv420p"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-ss",
            f"{clip.source_start:.4f}",
            "-i",
            str(SOURCE),
            "-t",
            f"{duration:.6f}",
            "-vf",
            vf,
            "-af",
            "highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=10,aresample=48000",
            *encode_args(),
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "2",
            str(output),
        ]
    )
    return output


def render_pexels_clip(clip: TimelineClip) -> Path:
    output = WORK / f"{clip.name}.mp4"
    duration = clip.frames / FPS
    zoom_width = round(WIDTH * clip.zoom)
    zoom_height = round(HEIGHT * clip.zoom)
    vf = (
        f"scale={zoom_width}:{zoom_height}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:(in_w-{WIDTH})/2:(in_h-{HEIGHT})/2,"
        "eq=contrast=1.06:saturation=0.82:brightness=-0.06,"
        f"fps={FPS},setsar=1,format=yuv420p"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-ss",
            f"{clip.pexels_start:.4f}",
            "-i",
            str(PEXELS),
            *silent_audio_input(duration),
            "-t",
            f"{duration:.6f}",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-vf",
            vf,
            *encode_args(),
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-shortest",
            str(output),
        ]
    )
    return output


def render_panel_clip(clip: TimelineClip, image: Path) -> Path:
    output = WORK / f"{clip.name}.mp4"
    duration = clip.frames / FPS
    zoom = (
        "zoompan=z='min(max(zoom,pzoom)+0.00055,1.045)':"
        "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d=1:s={WIDTH}x{HEIGHT}:fps={FPS},format=yuv420p"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-loop",
            "1",
            "-i",
            str(image),
            *silent_audio_input(duration),
            "-t",
            f"{duration:.6f}",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-vf",
            zoom,
            "-frames:v",
            str(clip.frames),
            *encode_args(),
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-shortest",
            str(output),
        ]
    )
    return output


def render_video_timeline(panel_paths: dict[str, Path]) -> Path:
    outputs: list[Path] = []
    for clip in TIMELINE:
        if clip.kind == "source":
            output = render_source_clip(clip)
        elif clip.kind == "pexels":
            output = render_pexels_clip(clip)
        elif clip.kind == "panel":
            output = render_panel_clip(clip, panel_paths[clip.name])
        else:
            raise ValueError(f"Unknown clip kind: {clip.kind}")
        outputs.append(output)

    concat_file = WORK / "concat.txt"
    concat_file.write_text(
        "".join(f"file '{path.resolve()}'\n" for path in outputs),
        encoding="utf-8",
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
            str(base),
        ]
    )
    return base


def composite_pexels_overlays(base_video: Path) -> Path:
    """Add small evidence inserts without replacing the interview or its audio."""
    inputs: list[str] = ["-i", str(base_video)]
    filter_lines: list[str] = []
    current_video = "0:v"
    for index, (start, end, source_offset) in enumerate(PEXELS_OVERLAYS, start=1):
        duration = end - start
        inputs.extend(
            [
                "-ss",
                f"{source_offset:.3f}",
                "-t",
                f"{duration:.3f}",
                "-i",
                str(PEXELS),
            ]
        )
        insert = f"insert{index}"
        output = f"video{index}"
        filter_lines.append(
            f"[{index}:v]scale=300:533:force_original_aspect_ratio=increase,"
            "crop=300:533,eq=contrast=1.05:saturation=0.88:brightness=-0.03,"
            f"fps={FPS},setsar=1,pad=316:549:8:8:color=0xF8FAFC,"
            f"setpts=PTS-STARTPTS+{start:.3f}/TB[{insert}]"
        )
        filter_lines.append(
            f"[{current_video}][{insert}]overlay=x=40:y=1010:"
            f"eof_action=pass:shortest=0:enable='between(t,{start:.3f},{end:.3f})'"
            f"[{output}]"
        )
        current_video = output

    filter_script = WORK / "pexels_overlay.ffscript"
    filter_script.write_text(";\n".join(filter_lines) + "\n", encoding="utf-8")
    output = WORK / "base_with_evidence.mp4"
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
            f"[{current_video}]",
            "-map",
            "0:a:0",
            "-frames:v",
            str(TOTAL_FRAMES),
            *encode_args(),
            "-c:a",
            "copy",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    return output


def compute_fit_tempo(raw_duration: float, target_duration: float) -> float:
    speaking_target = target_duration - 0.18
    if speaking_target <= 0:
        raise ValueError("Target duration is too short for neural speech")
    required = raw_duration / speaking_target
    if required > MAX_POST_TEMPO:
        raise ValueError(
            f"Neural line exceeds timing budget: {required:.3f}x > {MAX_POST_TEMPO:.2f}x"
        )
    return max(1.0, required)


def generate_tts() -> list[Path]:
    outputs: list[Path] = []
    report: list[dict[str, Any]] = []
    for line in tts_lines():
        raw = TTS / f"{line.name}_raw.mp3"
        fitted = TTS / f"{line.name}.wav"
        run(
            [
                str(EDGE_TTS),
                "--voice",
                EDGE_TTS_VOICE,
                "--rate",
                f"{line.rate_percent:+d}%",
                "--pitch",
                f"{line.pitch_hz:+d}Hz",
                "--text",
                line.synthesis_text,
                "--write-media",
                str(raw),
            ]
        )
        if not raw.exists() or raw.stat().st_size < 1_000:
            raise RuntimeError(f"Edge TTS produced an invalid file: {raw}")
        raw_duration = probe_duration(raw)
        target = line.frames / FPS
        tempo = compute_fit_tempo(raw_duration, target)
        speech_duration = raw_duration / tempo
        fade_out_start = max(0.0, speech_duration - 0.06)
        target_samples = round(target * 48_000)
        audio_filter = (
            f"atempo={tempo:.6f},"
            "highpass=f=75,"
            "acompressor=threshold=0.125:ratio=2.2:attack=5:release=80:makeup=2,"
            "afade=t=in:st=0:d=0.025,"
            f"afade=t=out:st={fade_out_start:.6f}:d=0.06,"
            "loudnorm=I=-16:TP=-1.5:LRA=9,"
            "aresample=48000:first_pts=0,"
            f"apad=whole_len={target_samples},atrim=end_sample={target_samples}"
        )
        run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-i",
                str(raw),
                "-af",
                audio_filter,
                "-ar",
                "48000",
                "-ac",
                "2",
                "-c:a",
                "pcm_s16le",
                str(fitted),
            ]
        )
        fitted_duration = probe_duration(fitted)
        if abs(fitted_duration - target) > 0.03:
            raise RuntimeError(
                f"Fitted TTS duration mismatch: {line.name} {fitted_duration:.3f}s != {target:.3f}s"
            )
        assert_not_silent(fitted, label=f"neural TTS {line.name}")
        report.append(
            {
                "name": line.name,
                "voice": EDGE_TTS_VOICE,
                "rate_percent": line.rate_percent,
                "pitch_hz": line.pitch_hz,
                "raw_duration": round(raw_duration, 6),
                "post_tempo": round(tempo, 6),
                "target_duration": round(target, 6),
                "truncated": False,
            }
        )
        outputs.append(fitted)
    (CHECKS / "tts_report.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    return outputs


def generate_music_and_sfx() -> tuple[Path, Path]:
    music = WORK / "music_bed.wav"
    impact = WORK / "impact.wav"
    music_source = (
        "aevalsrc=(0.085*sin(2*PI*55*t)*(0.30+0.70*exp(-7*mod(t\\,0.5)))+"
        "0.022*sin(2*PI*110*t)+0.010*sin(2*PI*220*t))*"
        f"min(1\\,t/0.8)*min(1\\,({RAW_DURATION:.6f}-t)/0.8):s=48000:d={RAW_DURATION:.6f}"
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
            music_source,
            "-af",
            "lowpass=f=1300,highpass=f=35",
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
        "aevalsrc=(0.26*sin(2*PI*(165-95*t)*t)+0.08*sin(2*PI*430*t))*"
        "exp(-11*t):s=48000:d=0.42"
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
            "lowpass=f=1900",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "pcm_s16le",
            str(impact),
        ]
    )
    return music, impact


def ass_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remainder = seconds % 60
    return f"{hours}:{minutes:02d}:{remainder:05.2f}"


def make_subtitles() -> Path:
    ass = WORK / "captions.ass"
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,Arial,82,&H00FFFFFF,&H000000FF,&H00101924,&H98000000,-1,0,0,0,100,100,0,0,1,6,2,8,60,60,230,1
Style: Caption,Arial,64,&H00FFFFFF,&H000000FF,&H00101924,&H98000000,-1,0,0,0,100,100,0,0,1,5,2,2,60,60,230,1
Style: Emphasis,Arial,74,&H0047D4FF,&H000000FF,&H00101924,&H98000000,-1,0,0,0,100,100,0,0,1,6,2,2,55,55,230,1
Style: Danger,Arial,74,&H005A5AFF,&H000000FF,&H00101924,&H98000000,-1,0,0,0,100,100,0,0,1,6,2,2,55,55,230,1
Style: Question,Arial,68,&H00A8E64E,&H000000FF,&H00101924,&H98000000,-1,0,0,0,100,100,0,0,1,6,2,2,55,55,230,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    for start, end, style, text in CAPTIONS:
        safe_text = text.replace("\n", r"\N")
        lines.append(
            f"Dialogue: 0,{ass_time(start)},{ass_time(end)},{style},,0,0,0,,{safe_text}\n"
        )
    ass.write_text("".join(lines), encoding="utf-8")
    return ass


def mix_raw(
    base_video: Path,
    music: Path,
    impact: Path,
    subtitles: Path,
) -> Path:
    inputs: list[str] = [
        "-i",
        str(base_video),
        "-i",
        str(music),
        "-i",
        str(impact),
    ]
    impact_index = 2

    filter_lines: list[str] = []
    filter_lines.append("[0:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.03[base]")
    filter_lines.append(
        "[1:a]aresample=48000,aformat=channel_layouts=stereo,"
        "volume=0.050[music]"
    )
    mix_labels = ["[base]", "[music]"]

    impact_frames = [
        0,
        70,
        148,
        186,
        319,
        510,
        555,
        836,
        1052,
        1281,
        1521,
    ]
    split_outputs = "".join(f"[impact{index}]" for index in range(len(impact_frames)))
    filter_lines.append(
        f"[{impact_index}:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"asplit={len(impact_frames)}{split_outputs}"
    )
    for index, frame in enumerate(impact_frames):
        delay = round(frame / FPS * 1000)
        volume = 0.24 if frame == 0 else 0.13
        label = f"hit{index}"
        filter_lines.append(
            f"[impact{index}]adelay={delay}|{delay},volume={volume:.2f}[{label}]"
        )
        mix_labels.append(f"[{label}]")

    filter_lines.append(
        "".join(mix_labels)
        + f"amix=inputs={len(mix_labels)}:duration=longest:normalize=0,"
        + f"alimiter=limit=0.94:attack=5:release=50,atrim=0:{RAW_DURATION:.6f}[aout]"
    )
    filter_script = WORK / "audio_mix.ffscript"
    filter_script.write_text(";\n".join(filter_lines) + "\n", encoding="utf-8")

    raw_mix = WORK / "raw_mix.mp4"
    subtitle_filter = (
        f"subtitles='{subtitles}':fontsdir='/System/Library/Fonts/Supplemental',"
        f"drawbox=x=0:y=ih-5:w=iw*(t/{RAW_DURATION:.6f}):h=5:color=0xFFD447:t=fill"
    )
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
            "-vf",
            subtitle_filter,
            "-frames:v",
            str(TOTAL_FRAMES),
            *encode_args(),
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
            str(raw_mix),
        ]
    )
    return raw_mix


def finish_audio_filter() -> str:
    return f"atempo={POST_SPEED}"


def finish_video_filter() -> str:
    return f"tpad=stop_mode=clone:stop_duration={FINISH_PAD:.2f},setpts=PTS/{POST_SPEED}"


def finish(raw_mix: Path) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(raw_mix),
            "-vf",
            finish_video_filter(),
            "-af",
            finish_audio_filter(),
            *encode_args(),
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
            "-shortest",
            str(FINAL),
        ]
    )


def extract_checks() -> None:
    timestamps = [
        0.0,
        0.10,
        0.75,
        1.50,
        2.30,
        3.40,
        4.60,
        5.70,
        7.40,
        9.20,
        10.30,
        12.00,
        14.50,
        18.50,
        22.00,
        25.00,
        29.00,
        33.50,
        38.00,
        42.50,
        47.50,
        52.00,
        55.50,
    ]
    for index, timestamp in enumerate(timestamps):
        output = CHECKS / f"{index:02d}_{timestamp:05.2f}.jpg"
        run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-ss",
                f"{timestamp:.2f}",
                "-i",
                str(FINAL),
                "-frames:v",
                "1",
                "-q:v",
                "2",
                str(output),
            ]
        )
    contact = CHECKS / "contact.jpg"
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(FINAL),
            "-vf",
            "fps=1/2.8,drawtext=fontfile='/System/Library/Fonts/HelveticaNeue.ttc':"
            "text='%{pts\\:hms}':x=10:y=10:fontsize=34:fontcolor=yellow:"
            "borderw=3:bordercolor=black,scale=270:-2:flags=lanczos,"
            "tile=5x4:padding=4:margin=4",
            "-frames:v",
            "1",
            str(contact),
        ]
    )


def validate_output() -> dict[str, Any]:
    info = probe(FINAL)
    video = next(stream for stream in info["streams"] if stream["codec_type"] == "video")
    audio = next(stream for stream in info["streams"] if stream["codec_type"] == "audio")
    duration = float(info["format"]["duration"])
    assertions = {
        "width": video["width"] == WIDTH,
        "height": video["height"] == HEIGHT,
        "video_codec": video["codec_name"] == "h264",
        "audio_codec": audio["codec_name"] == "aac",
        "duration": 45.0 <= duration <= 60.0,
        "source_usage": source_usage_ratio(TIMELINE) <= 0.5,
        "original_voice_only": all(clip.kind == "source" for clip in TIMELINE),
        "first_pexels_after_10s": min(window[0] for window in PEXELS_OVERLAYS)
        / POST_SPEED
        >= 10.0,
    }
    failed = [name for name, passed in assertions.items() if not passed]
    if failed:
        raise AssertionError(f"Validation failed: {failed}\n{json.dumps(info, indent=2)}")

    hook_max = assert_not_silent(
        FINAL,
        label="final hook dialogue",
        threshold_db=-25.0,
        start=0.0,
        duration=5.8,
    )
    middle_max = assert_not_silent(
        FINAL,
        label="final middle interview",
        threshold_db=-25.0,
        start=13.0 / POST_SPEED,
        duration=25.0,
    )
    trust_max = assert_not_silent(
        FINAL,
        label="final trust payoff",
        threshold_db=-25.0,
        start=42.70 / POST_SPEED,
        duration=13.0,
    )
    run(["ffmpeg", "-v", "error", "-i", str(FINAL), "-f", "null", "-"])

    report = {
        "output": str(FINAL),
        "duration": duration,
        "resolution": f"{video['width']}x{video['height']}",
        "video_codec": video["codec_name"],
        "audio_codec": audio["codec_name"],
        "raw_duration": RAW_DURATION,
        "post_speed": POST_SPEED,
        "source_usage_percent": round(source_usage_ratio(TIMELINE) * 100, 2),
        "original_voice_only": True,
        "first_pexels_final_time": round(
            min(window[0] for window in PEXELS_OVERLAYS) / POST_SPEED,
            3,
        ),
        "hook_caption_final_time": round(HOOK_CAPTIONS[0][0] / POST_SPEED, 3),
        "hook_dialogue_max_db": hook_max,
        "middle_interview_max_db": middle_max,
        "trust_payoff_max_db": trust_max,
        "decode_check": "passed",
    }
    (CHECKS / "validation.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    (CHECKS / "timeline.json").write_text(
        json.dumps([asdict(clip) for clip in TIMELINE], indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return report


def main() -> None:
    require_inputs()
    base_video = render_video_timeline({})
    evidence_video = composite_pexels_overlays(base_video)
    (CHECKS / "tts_report.json").write_text("[]\n", encoding="utf-8")
    music, impact = generate_music_and_sfx()
    subtitles = make_subtitles()
    raw_mix = mix_raw(evidence_video, music, impact, subtitles)
    finish(raw_mix)
    extract_checks()
    validate_output()


if __name__ == "__main__":
    main()
