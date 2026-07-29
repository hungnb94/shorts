#!/usr/bin/env python3
"""Render Money Blindspot long-form V1: AI's Real Bottleneck Isn't Chips.

Original English narration + licensed Pexels illustration + original charts and
procedural score. This is a one-off media renderer; completion is verified on the
exact MP4, not with renderer unit tests.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import wave
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output/projects/ai-power-bottleneck"
SCRIPT = PROJECT / "scripts/script.json"
TTS_REPORT = PROJECT / "work/tts/generation-report.json"
TTS_DIR = PROJECT / "work/tts/final"
STOCK_DIR = PROJECT / "stock"
WORK = PROJECT / "work/render"
CARDS = WORK / "cards"
OVERLAYS = WORK / "overlays"
SEGMENTS = WORK / "segments"
AUDIO = WORK / "audio"
CHECKS = PROJECT / "checks"
FINAL = PROJECT / "final/2026-07-28-ai_real_bottleneck_isnt_chips.mp4"
THUMBNAIL = CHECKS / "thumbnail-v1.jpg"
TIMELINE = PROJECT / "scripts/timeline.json"

WIDTH = 1920
HEIGHT = 1080
FPS = 30
FORCE_SCENES = {item.strip() for item in os.environ.get("FORCE_SCENES", "").split(",") if item.strip()}
FONT_BOLD_PATH = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
FONT_REG_PATH = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
DARK = (8, 14, 24)
NAVY = (14, 29, 46)
CYAN = (49, 224, 208)
AMBER = (255, 184, 72)
RED = (255, 82, 91)
GREEN = (80, 218, 145)
WHITE = (244, 248, 252)
MUTED = (160, 177, 194)


def run(command: list[str | Path], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    printable = " ".join(str(part) for part in command)
    print("+", printable, flush=True)
    return subprocess.run(
        [str(part) for part in command], cwd=ROOT, check=True, text=True,
        capture_output=capture,
    )


def probe(path: Path) -> dict[str, Any]:
    result = run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
        capture=True,
    )
    return json.loads(result.stdout)


def duration(path: Path) -> float:
    return float(probe(path)["format"]["duration"])


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD_PATH if bold else FONT_REG_PATH), size)


def accent(scene: dict[str, Any]) -> tuple[int, int, int]:
    return {"cyan": CYAN, "amber": AMBER, "red": RED, "green": GREEN}.get(scene.get("accent", "cyan"), CYAN)


def wrap(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if line and draw.textbbox((0, 0), candidate, font=face)[2] > max_width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def draw_centered_lines(
    draw: ImageDraw.ImageDraw,
    text: str,
    face: ImageFont.FreeTypeFont,
    center_y: int,
    fill: tuple[int, ...],
    max_width: int = 1600,
    spacing: int = 12,
) -> None:
    lines = wrap(draw, text, face, max_width)
    line_h = face.size + spacing
    y = center_y - (len(lines) * line_h - spacing) // 2
    for line in lines:
        box = draw.textbbox((0, 0), line, font=face)
        x = (WIDTH - (box[2] - box[0])) // 2
        draw.text((x, y), line, font=face, fill=fill)
        y += line_h


def base_canvas(scene: dict[str, Any], index: int, stage: int) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), DARK)
    color = accent(scene)
    gradient = ImageDraw.Draw(image)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        row = tuple(int(DARK[channel] * (1 - ratio) + NAVY[channel] * ratio) for channel in range(3))
        gradient.line((0, y, WIDTH, y), fill=row)
    draw = ImageDraw.Draw(image, "RGBA")
    for x in range(30, WIDTH, 60):
        for y in range(30, HEIGHT, 60):
            draw.ellipse((x - 1, y - 1, x + 1, y + 1), fill=(*MUTED, 38))
    draw.ellipse((1420, -260, 2200, 520), outline=(*color, 55), width=4)
    draw.ellipse((-300, 760, 460, 1520), outline=(*color, 35), width=3)
    draw.rectangle((0, 0, WIDTH * (stage + 1) // 3, 7), fill=(*color, 220))
    chapter = scene["chapter"].replace("_", " ").upper()
    draw.text((78, 45), f"MONEY BLINDSPOT  /  {chapter}", font=font(24, bold=True), fill=(*color, 235))
    draw.text((WIDTH - 290, HEIGHT - 52), "MONEY BLINDSPOT", font=font(18, bold=True), fill=(*MUTED, 150))
    draw.text((78, HEIGHT - 52), f"{index + 1:02d} / 53", font=font(18, bold=True), fill=(*MUTED, 150))
    if scene.get("source"):
        draw.text((78, HEIGHT - 90), scene["source"], font=font(20), fill=(*MUTED, 220))
    return image


def draw_headline(draw: ImageDraw.ImageDraw, scene: dict[str, Any], color: tuple[int, int, int]) -> int:
    headline = scene.get("headline", "")
    size = 66 if len(headline) < 34 else 54
    face = font(size, bold=True)
    lines = wrap(draw, headline, face, 1650)
    y = 112
    for line in lines[:3]:
        draw.text((78, y), line, font=face, fill=WHITE)
        y += size + 8
    draw.rounded_rectangle((78, y + 10, 270, y + 20), radius=5, fill=color)
    return y + 62


def reveal_count(total: int, stage: int) -> int:
    return max(1, math.ceil(total * (stage + 1) / 3))


def render_card(scene: dict[str, Any], index: int, stage: int, output: Path) -> None:
    image = base_canvas(scene, index, stage)
    draw = ImageDraw.Draw(image, "RGBA")
    color = accent(scene)
    visual = scene["visual"]
    data = scene.get("data", {})
    steps = scene.get("steps", [])
    center_only = visual in {
        "number_card", "promise", "warning_card", "audit_intro", "audit_question",
        "final_question", "cta", "power_plant_card", "flex_compute", "classification",
        "revealed_preference", "ghost_queue", "stranded_asset", "split_bill",
        "hourly_power", "rebound_effect",
    }
    content_y = 170 if center_only else draw_headline(draw, scene, color)

    if visual == "number_card":
        headline = scene["headline"]
        face = font(190 if len(headline) <= 6 else 140, bold=True)
        draw_centered_lines(draw, headline, face, 590, color, 1600)
        if stage >= 1 and scene.get("subline"):
            draw_centered_lines(draw, scene["subline"], font(38, bold=True), 760, WHITE, 1500)
    elif visual in {"bar_growth", "dual_growth", "timeline"} and data:
        entries = list(data.items())
        shown = reveal_count(len(entries), stage)
        max_value = max(float(value) for _, value in entries if isinstance(value, (int, float)))
        y0 = max(content_y + 40, 380)
        for row, (label, value) in enumerate(entries):
            y = y0 + row * 190
            draw.text((160, y), str(label).upper(), font=font(30, bold=True), fill=WHITE)
            draw.rounded_rectangle((160, y + 55, 1590, y + 118), radius=16, fill=(32, 48, 64, 255))
            if row < shown:
                fraction = float(value) / max_value
                width = int(1430 * fraction * (0.62 + stage * 0.19))
                draw.rounded_rectangle((160, y + 55, 160 + width, y + 118), radius=16, fill=(*color, 235))
                display_value = (scene.get("display_data") or {}).get(label)
                if not display_value:
                    suffix = scene.get("suffix", "")
                    suffixes = scene.get("suffixes")
                    if suffixes and row < len(suffixes):
                        suffix = suffixes[row]
                    display_value = f"{value} {suffix}".strip()
                value_face = font(34 if len(str(display_value)) > 10 else 42, bold=True)
                draw.text((1640, y + 50), str(display_value), font=value_face, fill=color)
    elif visual == "rack_homes":
        draw.rounded_rectangle((135, 370, 600, 870), radius=32, fill=(20, 36, 53), outline=(*color, 230), width=5)
        for row in range(8):
            y = 410 + row * 52
            draw.rounded_rectangle((185, y, 550, y + 28), radius=8, fill=(40, 60, 78))
            draw.ellipse((510, y + 8, 520, y + 18), fill=GREEN)
        shown = min(65, reveal_count(65, stage))
        for home in range(shown):
            row, col = divmod(home, 13)
            x = 770 + col * 75
            y = 430 + row * 90
            draw.polygon([(x, y + 20), (x + 24, y), (x + 48, y + 20)], fill=(*AMBER, 235))
            draw.rectangle((x + 7, y + 20, x + 41, y + 53), fill=(*WHITE, 220))
    elif visual in {"grid_gate", "transformer_diagram", "grid_stack", "dependency_chain"}:
        labels = steps or (["GRID", "TRANSFORMER", "SERVERS"] if visual == "grid_gate" else ["HIGH VOLTAGE", "TRANSFORMER", "USABLE POWER"])
        shown = reveal_count(len(labels), stage)
        gap = 45
        box_w = min(390, (1650 - gap * (len(labels) - 1)) // len(labels))
        total = box_w * len(labels) + gap * (len(labels) - 1)
        x0 = (WIDTH - total) // 2
        y = 500
        for position, label in enumerate(labels):
            x = x0 + position * (box_w + gap)
            active = position < shown
            fill = (*color, 225) if active else (32, 48, 64, 180)
            draw.rounded_rectangle((x, y, x + box_w, y + 180), radius=24, fill=fill)
            lines = wrap(draw, label, font(27, bold=True), box_w - 36)
            yy = y + 68 - (len(lines) - 1) * 17
            for line in lines:
                tw = draw.textbbox((0, 0), line, font=font(27, bold=True))[2]
                draw.text((x + (box_w - tw) / 2, yy), line, font=font(27, bold=True), fill=DARK if active else MUTED)
                yy += 34
            if position < len(labels) - 1:
                ax = x + box_w + 8
                draw.line((ax, y + 90, ax + gap - 16, y + 90), fill=(*color, 210 if position < shown - 1 else 60), width=8)
                draw.polygon([(ax + gap - 16, y + 78), (ax + gap - 2, y + 90), (ax + gap - 16, y + 102)], fill=(*color, 210 if position < shown - 1 else 60))
    elif visual == "company_deal" and data:
        entries = list(data.items())
        shown = reveal_count(len(entries), stage)
        card_w = 500
        total = len(entries) * card_w + (len(entries) - 1) * 36
        x0 = (WIDTH - total) // 2
        for row, (key, value) in enumerate(entries):
            x = x0 + row * (card_w + 36)
            fill = (21, 42, 60, 245) if row < shown else (20, 30, 42, 140)
            draw.rounded_rectangle((x, 440, x + card_w, 800), radius=26, fill=fill, outline=(*color, 200 if row < shown else 45), width=4)
            draw.text((x + 35, 485), str(key).upper(), font=font(24, bold=True), fill=MUTED)
            lines = wrap(draw, str(value), font(48, bold=True), card_w - 70)
            yy = 585
            for line in lines:
                draw.text((x + 35, yy), line, font=font(48, bold=True), fill=color if row < shown else MUTED)
                yy += 58
    elif steps:
        shown = reveal_count(len(steps), stage)
        cols = min(4, len(steps))
        box_w = 370
        gap_x = 36
        rows = math.ceil(len(steps) / cols)
        start_y = max(content_y + 45, 380)
        for position, label in enumerate(steps):
            row, col = divmod(position, cols)
            row_count = min(cols, len(steps) - row * cols)
            row_total = row_count * box_w + (row_count - 1) * gap_x
            row_x = (WIDTH - row_total) // 2
            x = row_x + col * (box_w + gap_x)
            y = start_y + row * 190
            active = position < shown
            draw.rounded_rectangle((x, y, x + box_w, y + 135), radius=22, fill=(*color, 215) if active else (30, 45, 60, 150))
            face = font(25, bold=True)
            lines = wrap(draw, label, face, box_w - 30)
            yy = y + 50 - (len(lines) - 1) * 15
            for line in lines:
                tw = draw.textbbox((0, 0), line, font=face)[2]
                draw.text((x + (box_w - tw) / 2, yy), line, font=face, fill=DARK if active else MUTED)
                yy += 31
    else:
        size = 72 if len(scene["headline"]) < 40 else 58
        draw_centered_lines(draw, scene["headline"], font(size, bold=True), 570, color, 1600)
        if stage >= 1 and scene.get("subline"):
            draw_centered_lines(draw, scene["subline"], font(34, bold=True), 770, WHITE, 1550)

    image.save(output)


def make_stock_overlay(scene: dict[str, Any], index: int, output: Path) -> None:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")
    color = accent(scene)
    for y in range(HEIGHT):
        alpha = int(max(0, (y / HEIGHT - 0.42) / 0.58) * 220)
        draw.line((0, y, WIDTH, y), fill=(4, 9, 15, alpha))
    draw.rectangle((0, 0, WIDTH, 74), fill=(4, 9, 15, 145))
    draw.text((65, 25), f"MONEY BLINDSPOT  /  {scene['chapter'].replace('_', ' ').upper()}", font=font(22, bold=True), fill=(*color, 245))
    if scene.get("label"):
        label = scene["label"]
        box = draw.textbbox((0, 0), label, font=font(19, bold=True))
        x = WIDTH - (box[2] - box[0]) - 66
        draw.rounded_rectangle((x - 18, 20, WIDTH - 48, 57), radius=10, fill=(5, 10, 16, 190), outline=(*MUTED, 130), width=1)
        draw.text((x, 28), label, font=font(19, bold=True), fill=(*MUTED, 240))
    headline = scene.get("headline", "")
    size = 63 if len(headline) < 38 else 50
    lines = wrap(draw, headline, font(size, bold=True), 1540)
    y = 730 - (len(lines) - 1) * 55
    draw.rounded_rectangle((64, y - 28, 92, y + len(lines) * (size + 4) + 20), radius=10, fill=color)
    for line in lines:
        draw.text((122, y), line, font=font(size, bold=True), fill=WHITE, stroke_width=2, stroke_fill=(0, 0, 0, 160))
        y += size + 6
    if scene.get("source"):
        draw.text((122, 1008), scene["source"], font=font(19), fill=(*MUTED, 235))
    draw.text((WIDTH - 255, 1008), "MONEY BLINDSPOT", font=font(18, bold=True), fill=(*MUTED, 170))
    image.save(output)


def render_card_video(images: list[Path], stage_frames: list[int], output: Path) -> None:
    command: list[str | Path] = ["ffmpeg", "-y", "-v", "error"]
    for image, frames in zip(images, stage_frames):
        command.extend(["-loop", "1", "-framerate", str(FPS), "-t", f"{frames / FPS:.9f}", "-i", image])
    filters = []
    labels = []
    for index, frames in enumerate(stage_frames):
        denominator = max(frames - 1, 1)
        direction = f"n/{denominator}" if index % 2 == 0 else f"1-n/{denominator}"
        filters.append(
            f"[{index}:v]scale=1980:1114,"
            f"crop=1920:1080:x='(iw-ow)*({direction})':"
            f"y='(ih-oh)*(0.5+0.30*sin(n/{denominator}*PI))',"
            f"trim=duration={frames / FPS:.9f},setpts=PTS-STARTPTS,format=yuv420p[v{index}]"
        )
        labels.append(f"[v{index}]")
    filters.append("".join(labels) + f"concat=n={len(images)}:v=1:a=0[vout]")
    command.extend([
        "-filter_complex", ";".join(filters), "-map", "[vout]",
        "-frames:v", str(sum(stage_frames)), "-an", "-c:v", "libx264",
        "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), output,
    ])
    run(command)


def render_stock_video(scene: dict[str, Any], index: int, frames: int, overlay: Path, output: Path) -> None:
    asset = STOCK_DIR / scene["asset"]
    if not asset.is_file():
        raise FileNotFoundError(asset)
    asset_duration = duration(asset)
    scene_duration = frames / FPS
    offset = (index * 3.71) % max(asset_duration, 0.1)
    run([
        "ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-ss", f"{offset:.4f}", "-i", asset,
        "-loop", "1", "-i", overlay,
        "-filter_complex",
        "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
        "eq=contrast=1.06:saturation=0.86:brightness=-0.035,fps=30[base];"
        "[base][1:v]overlay=0:0:format=auto,format=yuv420p[vout]",
        "-map", "[vout]", "-frames:v", str(frames), "-an", "-c:v", "libx264",
        "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), output,
    ])


def render_scene(scene: dict[str, Any], index: int, seconds: float) -> dict[str, Any]:
    frames = max(1, math.ceil(seconds * FPS))
    aligned = frames / FPS
    segment = SEGMENTS / f"{scene['id']}.mp4"
    aligned_audio = AUDIO / f"{scene['id']}.wav"
    if scene["id"] not in FORCE_SCENES and segment.is_file() and aligned_audio.is_file():
        try:
            segment_info = probe(segment)
            video_stream = next(stream for stream in segment_info["streams"] if stream["codec_type"] == "video")
            if (
                int(video_stream["width"]) == WIDTH
                and int(video_stream["height"]) == HEIGHT
                and abs(float(segment_info["format"]["duration"]) - aligned) <= 0.04
                and abs(duration(aligned_audio) - aligned) <= 0.002
            ):
                print(f"cache hit {scene['id']} {aligned:.3f}s", flush=True)
                return {"id": scene["id"], "chapter": scene["chapter"], "frames": frames, "duration": aligned, "video": segment, "audio": aligned_audio}
        except (KeyError, StopIteration, subprocess.CalledProcessError, ValueError):
            pass
    if scene["visual"] == "stock":
        overlay = OVERLAYS / f"{scene['id']}.png"
        make_stock_overlay(scene, index, overlay)
        render_stock_video(scene, index, frames, overlay, segment)
    else:
        images = []
        for stage in range(3):
            image = CARDS / f"{scene['id']}-{stage}.png"
            render_card(scene, index, stage, image)
            images.append(image)
        frame_base = frames // 3
        stage_frames = [frame_base, frame_base, frames - frame_base * 2]
        render_card_video(images, stage_frames, segment)
    vo = TTS_DIR / f"{scene['id']}.wav"
    run([
        "ffmpeg", "-y", "-v", "error", "-i", vo,
        "-af", f"apad,atrim=0:{aligned:.9f}", "-ar", "48000", "-ac", "2",
        "-c:a", "pcm_s16le", aligned_audio,
    ])
    return {"id": scene["id"], "chapter": scene["chapter"], "frames": frames, "duration": aligned, "video": segment, "audio": aligned_audio}


def concat_media(rows: list[dict[str, Any]]) -> tuple[Path, Path]:
    video_list = WORK / "video-concat.txt"
    audio_list = WORK / "audio-concat.txt"
    video_list.write_text("".join(f"file '{row['video'].resolve()}'\n" for row in rows), encoding="utf-8")
    audio_list.write_text("".join(f"file '{row['audio'].resolve()}'\n" for row in rows), encoding="utf-8")
    video = WORK / "visual-track.mp4"
    narration = WORK / "narration-track.wav"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", video])
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", audio_list, "-c:a", "pcm_s16le", narration])
    return video, narration


def timeline(rows: list[dict[str, Any]], scenes: list[dict[str, Any]]) -> dict[str, Any]:
    cursor = 0.0
    scene_rows = []
    chapter_rows = []
    chapter_start = 0.0
    current_chapter = rows[0]["chapter"]
    for row, scene in zip(rows, scenes):
        if row["chapter"] != current_chapter:
            chapter_rows.append({"chapter": current_chapter, "start": round(chapter_start, 3), "end": round(cursor, 3)})
            current_chapter = row["chapter"]
            chapter_start = cursor
        scene_rows.append({
            "id": row["id"], "chapter": row["chapter"], "start": round(cursor, 3),
            "end": round(cursor + row["duration"], 3), "duration": round(row["duration"], 3),
            "frames": row["frames"], "narration": scene["narration"], "visual": scene["visual"],
        })
        cursor += row["duration"]
    chapter_rows.append({"chapter": current_chapter, "start": round(chapter_start, 3), "end": round(cursor, 3)})
    return {"fps": FPS, "duration": round(cursor, 3), "scenes": scene_rows, "chapters": chapter_rows}


def generate_score(total_seconds: float, chapters: list[dict[str, Any]], output: Path) -> None:
    sample_rate = 48000
    chunk_seconds = 5.0
    roots = [55.0, 61.74, 65.41, 73.42, 82.41, 65.41, 55.0]
    rng = np.random.default_rng(260728)

    def chapter_index(at: float) -> int:
        for idx, chapter in enumerate(chapters):
            if chapter["start"] <= at < chapter["end"]:
                return idx
        return len(chapters) - 1

    with wave.open(str(output), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        cursor = 0
        total_samples = math.ceil(total_seconds * sample_rate)
        while cursor < total_samples:
            count = min(int(chunk_seconds * sample_rate), total_samples - cursor)
            absolute = (cursor + np.arange(count)) / sample_rate
            idx = chapter_index(float(absolute[count // 2]))
            root = roots[idx % len(roots)]
            local = absolute - chapters[idx]["start"]
            pad = (
                0.050 * np.sin(2 * np.pi * root * absolute)
                + 0.025 * np.sin(2 * np.pi * root * 1.5 * absolute + 0.4)
                + 0.018 * np.sin(2 * np.pi * root * 2.0 * absolute + 1.1)
            )
            bpm = 72 + (idx % 3) * 6
            beat_phase = np.mod(local * bpm / 60.0, 1.0)
            pulse_env = np.exp(-beat_phase * 10.0)
            pulse = 0.026 * pulse_env * np.sin(2 * np.pi * root * 2 * absolute)
            shimmer_env = 0.5 + 0.5 * np.sin(2 * np.pi * 0.08 * absolute)
            shimmer = 0.008 * shimmer_env * np.sin(2 * np.pi * root * 6 * absolute + 0.7)
            noise = rng.normal(0, 0.0016, count)
            mono = np.tanh((pad + pulse + shimmer + noise) * 1.35)
            left = mono
            right = 0.97 * mono + 0.008 * np.sin(2 * np.pi * root * 1.01 * absolute + 0.8)
            stereo = np.column_stack([left, right])
            pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype("<i2")
            handle.writeframes(pcm.tobytes())
            cursor += count


def mix_final(video: Path, narration: Path, score: Path) -> None:
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    run([
        "ffmpeg", "-y", "-v", "error", "-i", video, "-i", narration, "-i", score,
        "-filter_complex",
        "[2:a]highpass=f=35,lowpass=f=10000,volume=0.62[music];"
        "[music][1:a]sidechaincompress=threshold=0.025:ratio=8:attack=18:release=360[duck];"
        "[1:a][duck]amix=inputs=2:normalize=0,"
        "acompressor=threshold=0.16:ratio=2:attack=5:release=100:makeup=1,"
        "loudnorm=I=-16:TP=-2.5:LRA=9,alimiter=limit=0.75:level=false[aout]",
        "-map", "0:v:0", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-ar", "48000", "-ac", "2", "-movflags", "+faststart", "-shortest", FINAL,
    ])


def extract_frame(asset: Path, at: float) -> Image.Image:
    temp = WORK / f"thumb-{asset.stem}-{at:.1f}.jpg"
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{at:.3f}", "-i", asset, "-frames:v", "1", "-q:v", "2", temp])
    return Image.open(temp).convert("RGB")


def make_thumbnail() -> None:
    left = extract_frame(STOCK_DIR / "circuit_macro_6755170.mp4", 3.0)
    right = extract_frame(STOCK_DIR / "substation_aerial_30915831.mp4", 7.0)
    left = ImageOps.fit(left, (640, 720), Image.Resampling.LANCZOS, centering=(0.55, 0.5))
    right = ImageOps.fit(right, (640, 720), Image.Resampling.LANCZOS, centering=(0.5, 0.48))
    image = Image.new("RGB", (1280, 720), DARK)
    image.paste(left, (0, 0))
    image.paste(right, (640, 0))
    image = ImageEnhance.Contrast(image).enhance(1.18)
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    for y in range(720):
        alpha = int(40 + 120 * (1 - abs(y - 360) / 360))
        draw.line((0, y, 1280, y), fill=(2, 7, 13, alpha))
    draw.polygon([(600, 0), (680, 0), (650, 720), (570, 720)], fill=(255, 60, 65, 210))
    draw.line((640, 70, 640, 650), fill=(255, 255, 255, 210), width=4)
    image = Image.alpha_composite(image.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((170, 234, 1110, 498), radius=32, fill=(4, 9, 15, 220), outline=(*AMBER, 245), width=8)
    text = "4-YEAR WAIT"
    face = font(118, bold=True)
    box = draw.textbbox((0, 0), text, font=face)
    draw.text(((1280 - (box[2] - box[0])) / 2, 270), text, font=face, fill=WHITE, stroke_width=5, stroke_fill=(0, 0, 0, 220))
    draw.text((52, 44), "AI CHIP", font=font(32, bold=True), fill=CYAN)
    label = "POWER GRID"
    box = draw.textbbox((0, 0), label, font=font(32, bold=True))
    draw.text((1228 - (box[2] - box[0]), 44), label, font=font(32, bold=True), fill=AMBER)
    image.convert("RGB").save(THUMBNAIL, quality=92, optimize=True)


def main() -> None:
    config = json.loads(SCRIPT.read_text(encoding="utf-8"))
    report = json.loads(TTS_REPORT.read_text(encoding="utf-8"))
    scenes = config["scenes"]
    report_by_id = {row["id"]: row for row in report["segments"]}
    if [scene["id"] for scene in scenes] != [row["id"] for row in report["segments"]]:
        raise RuntimeError("script and TTS report order mismatch")
    for path in (WORK, CARDS, OVERLAYS, SEGMENTS, AUDIO, CHECKS):
        path.mkdir(parents=True, exist_ok=True)

    jobs = [(scene, index, float(report_by_id[scene["id"]]["final_seconds"])) for index, scene in enumerate(scenes)]
    completed: dict[str, dict[str, Any]] = {}
    workers = max(1, min(3, (os.cpu_count() or 4) // 2))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(render_scene, *job): job[0]["id"] for job in jobs}
        for future in as_completed(futures):
            row = future.result()
            completed[row["id"]] = row
            print(f"rendered {row['id']} {row['duration']:.3f}s", flush=True)
    rows = [completed[scene["id"]] for scene in scenes]
    video, narration = concat_media(rows)
    timeline_data = timeline(rows, scenes)
    TIMELINE.write_text(json.dumps(timeline_data, indent=2) + "\n", encoding="utf-8")
    score = WORK / "original-score.wav"
    generate_score(timeline_data["duration"], timeline_data["chapters"], score)
    mix_final(video, narration, score)
    make_thumbnail()
    print(json.dumps({"final": str(FINAL), "thumbnail": str(THUMBNAIL), "duration": timeline_data["duration"]}, indent=2))


if __name__ == "__main__":
    main()
