#!/usr/bin/env python3
"""Render Capytech v5 from five budget-gated Higgsfield shots.

The final cut uses 29 editorial segments of 1–3 seconds, local kinetic overlays,
one licensed Pexels illustration, original narration/music/SFX, and no additional
paid generation. Completion is verified on the rendered MP4.
"""

from __future__ import annotations

import functools
import json
import math
import subprocess
import sys
import wave
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from pipeline.capytech import render_capytech_v1 as base  # noqa: E402

PROJECT = ROOT / "output/projects/capytech"
STORYBOARD = PROJECT / "scripts/capytech_higgsfield_v4_storyboard.json"
GENERATED = PROJECT / "higgsfield/video-v5"
WORK = PROJECT / "clips/capytech_v5_higgsfield_work"
FRAME_CACHE = WORK / "generated_frames"
AUDIO_DIR = WORK / "audio"
VISUAL = WORK / "visual_master.mp4"
FINAL = PROJECT / "final/2026-07-28-capytech_v5_higgsfield_charging_eras.mp4"
MANIFEST = WORK / "render_manifest.json"
EDGE_TTS = Path.home() / ".local/bin/edge-tts"

W, H = 540, 960
OUT_W, OUT_H = 1080, 1920
FPS = 30
SOURCE_FPS = 24
SAMPLE_RATE = 48000
DURATION = 50.5

SOURCES = {
    "g01": GENERATED / "g01_hook_motion.mp4",
    "g02": GENERATED / "g02_2000_motion.mp4",
    "g03": GENERATED / "g03_2026_motion.mp4",
    "g04": GENERATED / "g04_2050_motion.mp4",
    "g05": GENERATED / "g05_payoff_motion.mp4",
}

# Final cuts map to coherent generated subranges. Repeated ranges are hidden by
# story-bearing UI, macro crops, or the intentional end-to-hook loop reprise.
SOURCE_EDL: dict[str, tuple[str, float, float]] = {
    "c01": ("g01", 0.00, 1.40), "c02": ("g01", 1.40, 2.80),
    "c03": ("g01", 2.70, 3.95), "c04": ("g01", 3.70, 5.00),
    "c05": ("g02", 0.00, 1.50), "c06": ("g02", 1.45, 2.80),
    "c07": ("g02", 2.75, 5.00), "c08": ("g02", 3.40, 4.80),
    "c09": ("g03", 0.00, 1.40), "c10": ("g03", 0.80, 2.00),
    "c11": ("g03", 1.40, 2.80), "c12": ("g03", 2.30, 3.80),
    "c13": ("g03", 3.35, 4.90), "c14": ("g03", 4.00, 5.00),
    "c15": ("g04", 0.00, 1.40), "c16": ("g04", 1.20, 2.60),
    "c17": ("g04", 2.35, 3.80), "c18": ("g04", 3.15, 4.80),
    "c19": ("g04", 3.70, 5.00), "c20": ("g05", 0.00, 2.00),
    "c21": ("g05", 0.50, 1.90), "c22": ("g05", 1.00, 2.00),
    "c23": ("g05", 1.40, 2.40), "c24": ("g05", 1.80, 2.80),
    "c25": ("g05", 2.00, 3.40), "c26": ("g05", 2.40, 3.80),
    "c27": ("g05", 3.00, 5.00), "c28": ("g01", 4.00, 5.00),
    "c29": ("g01", 1.00, 0.00),
}

# scale, horizontal focus, vertical focus. Uniform scaling followed by crop only.
REFRAMES: dict[str, tuple[float, float, float]] = {
    "c01": (1.02, 0.50, 0.48), "c02": (1.17, 0.26, 0.43),
    "c03": (1.07, 0.50, 0.47), "c04": (1.18, 0.50, 0.34),
    "c05": (1.02, 0.50, 0.50), "c06": (1.20, 0.50, 0.54),
    "c07": (1.08, 0.50, 0.46), "c08": (1.12, 0.50, 0.40),
    "c09": (1.02, 0.50, 0.50), "c10": (1.18, 0.50, 0.48),
    "c11": (1.10, 0.45, 0.52), "c12": (1.17, 0.50, 0.56),
    "c13": (1.10, 0.50, 0.43), "c14": (1.13, 0.50, 0.40),
    "c15": (1.02, 0.50, 0.50), "c16": (1.10, 0.50, 0.48),
    "c17": (1.15, 0.50, 0.52), "c18": (1.08, 0.50, 0.45),
    "c19": (1.18, 0.27, 0.47), "c20": (1.12, 0.50, 0.42),
    "c21": (1.07, 0.50, 0.43), "c22": (1.11, 0.35, 0.43),
    "c23": (1.11, 0.50, 0.43), "c24": (1.11, 0.65, 0.43),
    "c25": (1.04, 0.50, 0.50), "c26": (1.18, 0.30, 0.48),
    "c27": (1.08, 0.50, 0.66), "c28": (1.10, 0.50, 0.42),
    "c29": (1.02, 0.50, 0.48),
}

NARRATION = [
    ("hook", 0.12, 5.20, "Three years. One percent battery. One charger drains him to zero."),
    ("era_2000", 5.62, 12.70, "In 2000, one giant charger did everything. Plug it in, and instant full battery."),
    ("era_2026", 13.08, 24.78, "In 2026, the cable is wrong. Every fix needs another adapter. It still cannot reach, and now the phone wants an update."),
    ("era_2050", 25.08, 37.80, "By 2050, charging is wireless, instant, and free. Until the orb reveals what it is actually charging from."),
    ("cta", 38.05, 42.25, "Like, subscribe, and comment charge to unlock the final percent."),
    ("payoff", 42.52, 48.28, "The phone hits one hundred. Volt hits zero."),
    ("loop", 48.58, 50.25, "Then comes the update."),
]


def run(command: list[str | Path], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(item) for item in command], check=True, capture_output=capture, text=True
    )


def probe_duration(path: Path) -> float:
    result = run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", path,
    ], capture=True)
    return float(result.stdout.strip())


def load_storyboard() -> dict[str, Any]:
    spec = json.loads(STORYBOARD.read_text(encoding="utf-8"))
    cuts = spec["cuts"]
    errors: list[str] = []
    for index, cut in enumerate(cuts):
        duration = float(cut["end"] - cut["start"])
        if not 1.0 <= duration <= 3.0:
            errors.append(f"{cut['id']} duration={duration}")
        if index and cuts[index - 1]["end"] != cut["start"]:
            errors.append(f"gap before {cut['id']}")
        if cut["id"] not in SOURCE_EDL or cut["id"] not in REFRAMES:
            errors.append(f"missing EDL/reframe for {cut['id']}")
    if cuts[0]["start"] != 0 or cuts[-1]["end"] != DURATION:
        errors.append("timeline coverage")
    if errors:
        raise RuntimeError(f"invalid v5 EDL: {errors}")
    return spec


def prepare_generated_frames() -> dict[str, dict[str, Any]]:
    FRAME_CACHE.mkdir(parents=True, exist_ok=True)
    report: dict[str, dict[str, Any]] = {}
    for source_id, source in SOURCES.items():
        if not source.exists():
            raise FileNotFoundError(source)
        target = FRAME_CACHE / source_id
        marker_path = target / "provenance.json"
        source_hash = base.sha256(source)
        config = {
            "source": str(source.relative_to(ROOT)),
            "source_sha256": source_hash,
            "source_fps": SOURCE_FPS,
            "filter": f"fps={SOURCE_FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
        }
        marker = base.read_json_if_valid(marker_path)
        frames = sorted(target.glob("*.jpg")) if target.exists() else []
        valid = marker is not None and marker.get("config") == config and len(frames) >= 120
        if not valid:
            target.mkdir(parents=True, exist_ok=True)
            for frame in frames:
                frame.unlink()
            run([
                "ffmpeg", "-y", "-v", "error", "-i", source, "-vf", config["filter"],
                "-q:v", "2", target / "%03d.jpg",
            ])
            frames = sorted(target.glob("*.jpg"))
            if len(frames) < 120:
                raise RuntimeError(f"incomplete frame cache {source_id}: {len(frames)}")
            marker = {
                "config": config,
                "frame_count": len(frames),
                "first_frame_sha256": base.sha256(frames[0]),
                "last_frame_sha256": base.sha256(frames[-1]),
            }
            marker_path.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")
        assert marker is not None
        report[source_id] = marker
    return report


@functools.lru_cache(maxsize=96)
def load_source_frame(source_id: str, frame_number: int) -> Image.Image:
    path = FRAME_CACHE / source_id / f"{frame_number:03d}.jpg"
    if not path.exists():
        available = sorted((FRAME_CACHE / source_id).glob("*.jpg"))
        if not available:
            raise FileNotFoundError(path)
        path = available[-1]
    with Image.open(path) as frame:
        return frame.convert("RGB").copy()


def active_cut(spec: dict[str, Any], t: float) -> dict[str, Any]:
    for cut in spec["cuts"]:
        if cut["start"] <= t < cut["end"]:
            return cut
    return spec["cuts"][-1]


def source_frame(cut: dict[str, Any], t: float) -> Image.Image:
    source_id, source_start, source_end = SOURCE_EDL[cut["id"]]
    progress = base.clamp((t - cut["start"]) / (cut["end"] - cut["start"]))
    source_t = source_start + (source_end - source_start) * progress
    frame_number = max(1, min(121, 1 + int(source_t * SOURCE_FPS)))
    return load_source_frame(source_id, frame_number)


def reframe(image: Image.Image, cut_id: str) -> Image.Image:
    scale, focus_x, focus_y = REFRAMES[cut_id]
    width = int(round(W * scale))
    height = int(round(H * scale))
    enlarged = image.resize((width, height), Image.Resampling.LANCZOS)
    left = int(round((width - W) * base.clamp(focus_x)))
    top = int(round((height - H) * base.clamp(focus_y)))
    return enlarged.crop((left, top, left + W, top + H))


def draw_era_badge(draw: ImageDraw.ImageDraw, cut_id: str) -> None:
    if cut_id <= "c04":
        label, color = "CHALLENGE", base.CYAN
    elif cut_id <= "c08":
        label, color = "2000", base.YELLOW
    elif cut_id <= "c14":
        label, color = "2026", base.WHITE
    else:
        label, color = "2050", base.RED
    draw.rounded_rectangle((18, 18, 168, 68), radius=16, fill=(5, 9, 18, 205), outline=(*color, 235), width=3)
    base.draw_center_text(draw, (93, 43), label, 25, color, max_width=135)


def draw_year_challenge(image: Image.Image, t: float) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((28, 176, W - 28, 430), radius=30, fill=(4, 8, 18, 232), outline=(*base.CYAN, 220), width=5)
    base.draw_center_text(draw, (W / 2, 225), "1% BATTERY", 43, base.RED, max_width=440)
    years = [("2000", base.YELLOW), ("2026", base.WHITE), ("2050", base.RED)]
    phase = int((t - 2.8) / 0.53) % 3
    for index, (label, color) in enumerate(years):
        x = 98 + index * 172
        active = index == phase
        draw.rounded_rectangle((x - 70, 285, x + 70, 355), radius=18, fill=(*color, 220 if active else 45), outline=(*color, 255), width=4)
        base.draw_center_text(draw, (x, 320), label, 27, base.INK if active else color, max_width=125)
    base.draw_center_text(draw, (W / 2, 397), "WHICH YEAR WINS?", 27, base.CYAN, max_width=430)


def draw_scoreboard(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((45, 185, W - 45, 440), radius=34, fill=(5, 9, 18, 238), outline=(*base.GREEN, 240), width=5)
    base.draw_center_text(draw, (W / 2, 240), "ROUND 1", 28, base.YELLOW, max_width=250)
    base.draw_center_text(draw, (W / 2, 318), "2000 WINS", 52, base.GREEN, max_width=420)
    base.draw_center_text(draw, (W / 2, 392), "ONE PLUG", 27, base.WHITE, max_width=300)


def draw_update_panel(image: Image.Image, label: str, progress: float) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((55, 185, W - 55, 455), radius=34, fill=(4, 8, 18, 238), outline=(*base.RED, 240), width=5)
    base.draw_center_text(draw, (W / 2, 260), label, 38, base.RED, max_width=410)
    draw.rounded_rectangle((95, 345, W - 95, 390), radius=18, fill=(255, 255, 255, 28))
    draw.rounded_rectangle((100, 350, 100 + int((W - 200) * base.clamp(progress)), 385), radius=15, fill=(*base.CYAN, 240))
    base.draw_center_text(draw, (W / 2, 425), f"{int(base.clamp(progress) * 100)}%", 25, base.YELLOW, max_width=160)


def draw_energy_source(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((55, 175, W - 55, 455), radius=34, fill=(4, 8, 18, 235), outline=(*base.RED, 240), width=5)
    base.draw_center_text(draw, (W / 2, 235), "FREE CHARGE*", 40, base.GREEN, max_width=400)
    base.draw_center_text(draw, (W / 2, 320), "ENERGY SOURCE", 29, base.WHITE, max_width=350)
    base.draw_center_text(draw, (W / 2, 395), "YOU", 62, base.RED, max_width=240)


def draw_dual_meters(image: Image.Image, phone: int, volt: int) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    for y, label, value, color in ((720, "PHONE", phone, base.GREEN), (800, "VOLT", volt, base.RED)):
        draw.rounded_rectangle((45, y, W - 45, y + 55), radius=18, fill=(3, 7, 14, 218), outline=(*color, 220), width=3)
        base.draw_center_text(draw, (105, y + 27), label, 20, base.WHITE, max_width=105)
        draw.rounded_rectangle((165, y + 15, W - 105, y + 40), radius=10, fill=(255, 255, 255, 28))
        draw.rounded_rectangle((170, y + 20, 170 + int((W - 280) * value / 100), y + 35), radius=7, fill=(*color, 240))
        base.draw_center_text(draw, (W - 70, y + 27), f"{value}%", 20, color, max_width=80)


def draw_cta_step(image: Image.Image, cut_id: str) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    labels = {"c21": "LOCKED AT 99%", "c22": "LIKE", "c23": "SUBSCRIBE", "c24": "COMMENT CHARGE"}
    index = {"c21": 0, "c22": 1, "c23": 2, "c24": 3}[cut_id]
    draw.rounded_rectangle((42, 170, W - 42, 455), radius=34, fill=(4, 7, 17, 242), outline=(*base.PURPLE, 245), width=6)
    base.draw_center_text(draw, (W / 2, 230), labels[cut_id], 41 if index else 34, base.RED if index == 0 else base.CYAN, max_width=430)
    for step, label in enumerate(("LIKE", "SUB", "COMMENT")):
        x0 = 73 + step * 137
        active = step < index
        color = base.GREEN if active else base.GRAY
        draw.rounded_rectangle((x0, 300, x0 + 115, 360), radius=16, fill=(*color, 210 if active else 65), outline=(*color, 235), width=3)
        base.draw_center_text(
            draw,
            (x0 + 57, 330),
            label,
            18,
            base.WHITE,
            stroke_width=1,
            max_width=105,
        )
    progress = index / 3
    draw.rounded_rectangle((75, 392, W - 75, 425), radius=14, fill=(255, 255, 255, 28))
    draw.rounded_rectangle((80, 397, 80 + int((W - 160) * progress), 420), radius=11, fill=(*base.GREEN, 240))


def draw_pexels_hologram(image: Image.Image, t: float, stock_frames: list[Image.Image]) -> None:
    if not stock_frames:
        return
    ratio = base.clamp((t - 29.2) / 2.2)
    frame = stock_frames[min(len(stock_frames) - 1, int(ratio * len(stock_frames)))].copy()
    panel = frame.resize((135, 240), Image.Resampling.LANCZOS)
    panel = ImageEnhance.Color(panel).enhance(0.75)
    image.alpha_composite(panel, (18, 105))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((14, 101, 157, 365), radius=14, outline=(*base.CYAN, 225), width=4)
    base.draw_center_text(draw, (85, 350), "ILLUSTRATION", 14, base.WHITE, stroke_width=2, max_width=125, display=False)


def draw_caption(image: Image.Image, cut: dict[str, Any]) -> None:
    if cut["id"] in {"c03", "c08", "c14", "c18", "c21", "c22", "c23", "c24", "c28"}:
        return
    text = str(cut["caption"])
    words = text.replace("/", " ").split()
    emphasis = max(words, key=len).strip("?:%'") if words else text
    base.draw_caption(image, text, emphasis, 610)


def render_frame(t: float, spec: dict[str, Any], stock_frames: list[Image.Image]) -> Image.Image:
    cut = active_cut(spec, t)
    image = reframe(source_frame(cut, t), cut["id"]).convert("RGBA")
    # Mild grade and top/bottom vignette preserve generated detail while improving text contrast.
    # Paint translucent fills on a separate layer. Drawing an alpha fill directly
    # onto the RGBA source replaces pixels instead of blending them, which would
    # create opaque black bands when the frame is converted back to RGB.
    vignette = Image.new("RGBA", image.size, (0, 0, 0, 0))
    vignette_draw = ImageDraw.Draw(vignette, "RGBA")
    vignette_draw.rectangle((0, 0, W, 100), fill=(0, 0, 0, 32))
    vignette_draw.rectangle((0, 560, W, H), fill=(0, 0, 0, 24))
    image.alpha_composite(vignette)
    draw = ImageDraw.Draw(image, "RGBA")
    draw_era_badge(draw, cut["id"])

    if cut["id"] == "c03":
        draw_year_challenge(image, t)
    elif cut["id"] == "c08":
        draw_scoreboard(image)
    elif cut["id"] == "c14":
        draw_update_panel(image, "UPDATE REQUIRED", (t - cut["start"]) / (cut["end"] - cut["start"]) * 0.04)
    elif cut["id"] == "c17":
        draw_pexels_hologram(image, t, stock_frames)
    elif cut["id"] == "c18":
        draw_energy_source(image)
    elif cut["id"] in {"c19", "c20"}:
        progress = base.clamp((t - 33.5) / 4.5)
        draw_dual_meters(image, int(1 + 78 * progress), int(100 - 67 * progress))
    elif cut["id"] in {"c21", "c22", "c23", "c24"}:
        draw_cta_step(image, cut["id"])
    elif cut["id"] == "c26":
        draw_dual_meters(image, 100, 0)
    elif cut["id"] == "c28":
        draw_update_panel(image, "SYSTEM UPDATE", (t - cut["start"]) / (cut["end"] - cut["start"]))

    draw_caption(image, cut)
    base.draw_watermark(ImageDraw.Draw(image, "RGBA"), t)
    progress = base.clamp(t / DURATION)
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((12, H - 14, W - 12, H - 7), radius=4, fill=(255, 255, 255, 35))
    draw.rounded_rectangle((12, H - 14, 12 + int((W - 24) * progress), H - 7), radius=4, fill=(*base.CYAN, 235))
    if t - cut["start"] < 1 / FPS and cut["id"] in {"c05", "c09", "c15", "c21", "c25", "c28"}:
        draw.rectangle((0, 0, W - 1, H - 1), outline=(*base.CYAN, 220), width=12)
    return image.convert("RGB")


def render_visual(spec: dict[str, Any], stock_frames: list[Image.Image]) -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-vf",
        f"scale={OUT_W}:{OUT_H}:flags=lanczos,format=yuv420p", "-an", "-c:v", "libx264",
        "-preset", "medium", "-crf", "17", "-profile:v", "high", "-level:v", "4.2",
        "-r", str(FPS), "-fps_mode", "cfr", "-movflags", "+faststart", VISUAL,
    ]
    process = subprocess.Popen([str(item) for item in command], stdin=subprocess.PIPE)
    assert process.stdin is not None
    total = int(DURATION * FPS)
    try:
        for frame_index in range(total):
            process.stdin.write(render_frame(frame_index / FPS, spec, stock_frames).tobytes())
            if frame_index % 300 == 0:
                print(f"frame {frame_index}/{total}", flush=True)
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError("visual encoder failed")


def generate_voice(name: str, text: str, slot_seconds: float) -> tuple[Path, dict[str, Any]]:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    if not EDGE_TTS.exists():
        raise FileNotFoundError(EDGE_TTS)
    raw = AUDIO_DIR / f"{name}_raw.mp3"
    ready = AUDIO_DIR / f"{name}.wav"
    marker_path = AUDIO_DIR / f"{name}.json"
    config = {"voice": "en-US-AndrewNeural", "rate": "+15%", "text": text, "slot_seconds": slot_seconds}
    marker = base.read_json_if_valid(marker_path)
    if marker is not None and marker.get("config") == config and ready.exists() and marker.get("sha256") == base.sha256(ready):
        return ready, marker
    run([EDGE_TTS, "--voice", config["voice"], "--rate", config["rate"], "--text", text, "--write-media", raw])
    raw_duration = probe_duration(raw)
    tempo = max(1.0, raw_duration / max(0.1, slot_seconds - 0.08))
    if tempo > 2.0:
        raise RuntimeError(f"{name} requires unsafe tempo {tempo:.3f}")
    filters = (
        "silenceremove=start_periods=1:start_duration=0.03:start_threshold=-45dB,"
        f"atempo={tempo:.8f},highpass=f=120,lowpass=f=9000,"
        "acompressor=threshold=0.08:ratio=4:attack=5:release=90:makeup=1,"
        "loudnorm=I=-16:TP=-2:LRA=7"
    )
    run([
        "ffmpeg", "-y", "-v", "error", "-i", raw, "-af", filters,
        "-ar", str(SAMPLE_RATE), "-ac", "2", "-c:a", "pcm_s16le", ready,
    ])
    duration = probe_duration(ready)
    if duration > slot_seconds + 0.03:
        raise RuntimeError(f"{name} voice exceeds slot {duration:.3f}>{slot_seconds:.3f}")
    marker = {"config": config, "duration_seconds": duration, "sha256": base.sha256(ready), "atempo": tempo}
    marker_path.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")
    return ready, marker


def synthesize_audio() -> tuple[Path, dict[str, Any]]:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    count = int(DURATION * SAMPLE_RATE)
    t = np.arange(count, dtype=np.float32) / SAMPLE_RATE
    analog = 0.022 * np.sin(math.tau * 110 * t) + 0.013 * np.sign(np.sin(math.tau * 220 * t))
    digital = 0.025 * np.sin(math.tau * 73.42 * t) + 0.013 * np.sin(math.tau * 587.33 * t)
    future = 0.027 * np.sin(math.tau * 55 * t) + 0.017 * np.sin(math.tau * 82.41 * t)
    mono = np.where(t < 13, analog, np.where(t < 25, digital, future)).astype(np.float32)
    score = np.column_stack((mono, mono * 0.96)).astype(np.float32)

    for at in np.arange(0, DURATION, 0.5):
        frequency = 360 if at < 13 else (520 if at < 25 else 240)
        base.add_clip(score, base.tone(0.045, frequency, 0.032), float(at))
    events = [
        (0.05, "alarm"), (0.55, "lunge"), (1.55, "cable_slip"),
        (5.55, "brick_drop"), (7.55, "plug"), (9.55, "success"),
        (13.05, "wrong_cable"), (17.25, "box_pop"), (19.55, "box_pop"),
        (21.85, "cable_snap"), (23.65, "update_alert"),
        (25.05, "orb_hover"), (29.25, "scan"), (31.45, "danger"),
        (33.55, "energy_drain"), (38.05, "cta_lock"), (42.45, "cta_unlock"),
        (46.55, "collapse"), (48.55, "update_alert"), (49.55, "alarm"),
    ]
    for at, event in events:
        base.add_clip(score, base.sfx(event), at)

    voice_report: dict[str, Any] = {}
    for name, start, end, text in NARRATION:
        voice_path, voice_meta = generate_voice(name, text, end - start)
        voice = base.read_wav(voice_path)
        score[int(max(0, start - 0.05) * SAMPLE_RATE):int(min(DURATION, end + 0.08) * SAMPLE_RATE)] *= 0.24
        base.add_clip(score, voice, start, 1.12)
        voice_report[name] = {"start": start, "end": end, "text": text, **voice_meta}

    peak = float(np.max(np.abs(score)))
    if peak > 0.82:
        score *= 0.82 / peak
    output = AUDIO_DIR / "final_mix.wav"
    pcm16 = (np.clip(score, -0.95, 0.95) * 32767).astype(np.int16)
    with wave.open(str(output), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(pcm16.tobytes())
    return output, voice_report


def main() -> None:
    spec = load_storyboard()
    frame_provenance = prepare_generated_frames()
    stock_frames = base.prepare_pexels_frames()
    render_visual(spec, stock_frames)
    audio, voice_report = synthesize_audio()
    base.mux(VISUAL, audio, FINAL, DURATION)
    actual = probe_duration(FINAL)
    if abs(actual - DURATION) > 0.08:
        raise RuntimeError(f"duration mismatch {actual:.3f} != {DURATION:.3f}")
    cuts = spec["cuts"]
    license_data = json.loads(base.LICENSE.read_text(encoding="utf-8"))["approved"]
    manifest = {
        "artifact": str(FINAL.relative_to(ROOT)),
        "artifact_sha256": base.sha256(FINAL),
        "artifact_size_bytes": FINAL.stat().st_size,
        "renderer": str(Path(__file__).resolve().relative_to(ROOT)),
        "storyboard": str(STORYBOARD.relative_to(ROOT)),
        "storyboard_sha256": base.sha256(STORYBOARD),
        "duration_seconds": actual,
        "fps": FPS,
        "canvas": [OUT_W, OUT_H],
        "cut_count": len(cuts),
        "minimum_cut_seconds": min(item["end"] - item["start"] for item in cuts),
        "maximum_cut_seconds": max(item["end"] - item["start"] for item in cuts),
        "generated_sources": {key: {"path": str(path.relative_to(ROOT)), "sha256": base.sha256(path)} for key, path in SOURCES.items()},
        "generated_frame_cache": frame_provenance,
        "pexels": license_data,
        "pexels_used_as": "moving in-world illustration panel during c17 scan reveal",
        "narration": voice_report,
        "paid_generation": {
            "successful_images": 4,
            "failed_images_not_charged": 1,
            "successful_videos": 5,
            "credits_spent": 41.5,
            "balance_before": 256.35,
            "balance_after": 214.85,
            "paid_retries": 0,
        },
        "status": "rendered; exact-final media QC pending",
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(FINAL)


if __name__ == "__main__":
    main()
