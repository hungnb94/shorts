#!/usr/bin/env python3
"""Render FoodTrial v2: Date Bark vs. SNICKERS.

One-off production renderer. Completion is verified against the rendered media,
not unit tests. See docs/production/foodtrial-v2-date-bark.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
import wave
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "output/projects/foodtrial/scripts/date_bark_v2_script.json"
SOURCE = ROOT / "output/projects/foodtrial/source/date_bark_v2/x_Ri-BQ-0xY.mp4"
PEXELS = {
    "8202077": ROOT / "output/projects/foodtrial/source/date_bark_v2/pexels/candidates/8202077.mp4",
    "18831517": ROOT / "output/projects/foodtrial/source/date_bark_v2/pexels/candidates/18831517.mp4",
}
WORK = ROOT / "output/projects/foodtrial/clips/date_bark_v2_work/render"
TTS_DIR = ROOT / "output/projects/foodtrial/clips/date_bark_v2_work/tts"
FINAL = ROOT / "output/projects/foodtrial/final/2026-07-19-foodtrial_v2_date_bark.mp4"
FONT_BANGERS = ROOT / "assets/fonts/bangers/Bangers-Regular.ttf"
FONT_UI = Path("/System/Library/Fonts/Helvetica.ttc")
SHARED_TING = ROOT / "output/shared/hardknocks_branding/verdict_correct_ting.wav"

WIDTH = 1080
HEIGHT = 1920
FPS = 30
SAMPLE_RATE = 48000
TAIL_PAD = 0.12
SILENCE_THRESHOLD_DB = -42
LONG_PAUSE_SECONDS = 0.35
RETAINED_PAUSE_SECONDS = 0.25

WHITE = "#FFFFFF"
INK = "#0B0E14"
YELLOW = "#FFD54A"
RED = "#FF4D5A"
GREEN = "#2DE2A5"
CYAN = "#42C8FF"
PURPLE = "#A78BFA"
MUTED = "#AAB4C6"

SPEAKER_COLORS = {
    "prosecution": RED,
    "defense": GREEN,
    "judge": YELLOW,
}


def run(command: list[str]) -> None:
    print("+", " ".join(command[:8]), "..." if len(command) > 8 else "", flush=True)
    subprocess.run(command, check=True)


def probe_duration(path: Path) -> float:
    return float(
        subprocess.check_output(
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
            text=True,
        ).strip()
    )


def encode_args() -> list[str]:
    return [
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-r",
        str(FPS),
        "-g",
        str(FPS * 2),
    ]


def frame_duration(duration: float) -> float:
    return math.ceil(duration * FPS) / FPS


def ass_time(seconds: float) -> str:
    centiseconds = max(0, round(seconds * 100))
    hours, rest = divmod(centiseconds, 360000)
    minutes, rest = divmod(rest, 6000)
    secs, centis = divmod(rest, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def escape_ass(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def sanitize_card_text(text: str) -> str:
    return text.replace("→", "->").replace("≈", "~").replace("•", "|")


def fit_font(text: str, path: Path, max_size: int, min_size: int, max_width: int) -> ImageFont.FreeTypeFont:
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    for size in range(max_size, min_size - 1, -2):
        font = ImageFont.truetype(str(path), size)
        widths = [probe.textlength(line, font=font) for line in text.splitlines()]
        if max(widths or [0]) <= max_width:
            return font
    return ImageFont.truetype(str(path), min_size)


def centered_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: Any,
) -> None:
    draw.text(xy, text, font=font, fill=fill, anchor="mm", align="center")


def load_spec() -> dict[str, Any]:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def locate_tts(beat_id: str) -> Path:
    matches = sorted(TTS_DIR.glob(f"*_{beat_id}.mp3"))
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one TTS file for {beat_id}, found {matches}")
    return matches[0]


def prepare_trimmed_tts(spec: dict[str, Any]) -> dict[str, Path]:
    output_dir = WORK / "audio/trimmed"
    output_dir.mkdir(parents=True, exist_ok=True)
    prepared: dict[str, Path] = {}
    for beat in spec["beats"]:
        source = locate_tts(beat["id"])
        output = output_dir / f"{beat['id']}.wav"
        silence_filter = (
            "silenceremove="
            f"start_periods=1:start_duration=0.05:start_threshold={SILENCE_THRESHOLD_DB}dB:"
            "start_silence=0.03:"
            f"stop_periods=-1:stop_duration={LONG_PAUSE_SECONDS}:"
            f"stop_threshold={SILENCE_THRESHOLD_DB}dB:stop_silence={RETAINED_PAUSE_SECONDS}"
        )
        run([
            "ffmpeg", "-y", "-v", "error", "-i", str(source), "-af", silence_filter,
            "-ar", str(SAMPLE_RATE), "-ac", "2", "-c:a", "pcm_s16le", str(output),
        ])
        prepared[beat["id"]] = output
    return prepared


def build_timeline(
    spec: dict[str, Any], prepared_tts: dict[str, Path]
) -> tuple[list[dict[str, Any]], float]:
    cursor = 0.0
    timeline = []
    for index, beat in enumerate(spec["beats"]):
        audio = prepared_tts[beat["id"]]
        speech_duration = probe_duration(audio)
        slot_duration = frame_duration(speech_duration + TAIL_PAD)
        row = {
            "index": index,
            "id": beat["id"],
            "start": round(cursor, 6),
            "speech_duration": round(speech_duration, 6),
            "duration": round(slot_duration, 6),
            "end": round(cursor + slot_duration, 6),
            "tts": str(audio.relative_to(ROOT)),
        }
        timeline.append(row)
        cursor += slot_duration
    cta = next(row for row in timeline if row["id"] == "triple_cta")
    if not 38 <= cta["start"] <= 42:
        raise RuntimeError(f"CTA starts at {cta['start']:.3f}s, outside 38-42s gate")
    if not 50 <= cursor <= 75:
        raise RuntimeError(f"Runtime {cursor:.3f}s outside 50-75s gate")
    return timeline, round(cursor, 6)


def build_chrome() -> Path:
    output = WORK / "panels/chrome.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((24, 24, WIDTH - 24, HEIGHT - 24), radius=34, outline=YELLOW, width=8)
    draw.rounded_rectangle((50, 42, WIDTH - 50, 138), radius=24, fill=(9, 13, 21, 225), outline=YELLOW, width=4)
    title_font = ImageFont.truetype(str(FONT_BANGERS), 54)
    centered_text(draw, (WIDTH // 2, 90), "TÒA ÁN MÓN ĂN  |  HỒ SƠ 002", title_font, WHITE)
    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output)
    return output


def build_watermark() -> Path:
    output = WORK / "panels/watermark.png"
    img = Image.new("RGBA", (270, 62), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(str(FONT_BANGERS), 34)
    draw.rounded_rectangle((0, 0, 269, 61), radius=16, fill=(5, 8, 14, 115), outline=(255, 213, 74, 120), width=2)
    centered_text(draw, (135, 32), "TÒA ÁN MÓN ĂN", font, (255, 255, 255, 150))
    img.save(output)
    return output


def beat_accent(beat: dict[str, Any]) -> str:
    if beat["id"] == "triple_cta":
        return PURPLE
    if beat["id"] == "verdict":
        return RED
    return SPEAKER_COLORS.get(beat.get("speaker", "judge"), YELLOW)


def build_background_png(beat: dict[str, Any], index: int) -> Path:
    output = WORK / "backgrounds" / f"{index:02d}_{beat['id']}.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    accent = beat_accent(beat)
    accent_rgb = tuple(int(accent[i : i + 2], 16) for i in (1, 3, 5))
    img = Image.new("RGB", (WIDTH, HEIGHT), INK)
    pixels = img.load()
    assert pixels is not None
    for y in range(HEIGHT):
        ratio = y / (HEIGHT - 1)
        base = (
            int(9 + 12 * ratio),
            int(13 + 10 * ratio),
            int(22 + 18 * ratio),
        )
        for x in range(WIDTH):
            glow = max(0.0, 1.0 - math.hypot((x - WIDTH * 0.72) / WIDTH, (y - HEIGHT * 0.28) / HEIGHT) * 2.0)
            pixels[x, y] = tuple(min(255, int(base[c] + accent_rgb[c] * glow * 0.13)) for c in range(3))
    draw = ImageDraw.Draw(img, "RGBA")
    for offset in range(-500, 1800, 220):
        draw.polygon(
            [(offset, 0), (offset + 90, 0), (offset + 720, HEIGHT), (offset + 630, HEIGHT)],
            fill=(*accent_rgb, 16),
        )
    for ring in range(5):
        radius = 120 + ring * 95
        draw.ellipse((WIDTH - 170 - radius, 250 - radius, WIDTH - 170 + radius, 250 + radius), outline=(*accent_rgb, 28), width=5)
    img.save(output)
    return output


def draw_comparison_bars(draw: ImageDraw.ImageDraw, beat: dict[str, Any], accent: str) -> None:
    visual = beat["visual"]
    if visual.get("type") != "comparison_bars":
        return
    left = float(visual["left"])
    right = float(visual["right"])
    scale = max(left, right)
    x0, x1 = 90, 850
    y0 = 418
    labels = [("DATE BARK", left, accent), ("SNICKERS", right, CYAN)]
    label_font = ImageFont.truetype(str(FONT_BANGERS), 36)
    value_font = ImageFont.truetype(str(FONT_BANGERS), 38)
    for row, (label, value, color) in enumerate(labels):
        y = y0 + row * 108
        draw.text((90, y - 43), label, font=label_font, fill=WHITE)
        draw.rounded_rectangle((x0, y, x1, y + 38), radius=18, fill=(255, 255, 255, 22))
        width = max(28, int((x1 - x0) * value / scale))
        rgb = tuple(int(color[i : i + 2], 16) for i in (1, 3, 5))
        draw.rounded_rectangle((x0, y, x0 + width, y + 38), radius=18, fill=(*rgb, 235))
        draw.text((x0 + width - 8, y + 19), f"{value:g}", font=value_font, fill=WHITE, anchor="rm")


def build_card(beat: dict[str, Any], index: int) -> Path:
    output = WORK / "panels" / f"{index:02d}_{beat['id']}_card.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    accent = beat_accent(beat)
    accent_rgb = tuple(int(accent[i : i + 2], 16) for i in (1, 3, 5))
    width, height = 940, 690
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=34, fill=(8, 12, 20, 238), outline=(*accent_rgb, 255), width=7)
    draw.rectangle((0, 0, 18, height), fill=(*accent_rgb, 255))

    title = sanitize_card_text(beat["card_title"])
    body = sanitize_card_text(beat["card_body"])
    title_font = fit_font(title, FONT_BANGERS, 58, 42, 820)
    body_font = fit_font(body, FONT_BANGERS, 68, 42, 790)
    note_font = ImageFont.truetype(str(FONT_UI), 24)
    badge_font = ImageFont.truetype(str(FONT_BANGERS), 32)

    badge = {
        "prosecution": "CÔNG TỐ",
        "defense": "BÀO CHỮA",
        "judge": "THẨM PHÁN",
    }.get(beat.get("speaker", "judge"), "THẨM PHÁN")
    if beat["id"] == "triple_cta":
        badge = "BỒI THẨM"
    draw.rounded_rectangle((42, 32, 270, 82), radius=20, fill=(*accent_rgb, 42), outline=(*accent_rgb, 220), width=2)
    centered_text(draw, (156, 57), badge, badge_font, accent)
    centered_text(draw, (width // 2, 135), title, title_font, WHITE)
    draw.line((72, 188, width - 72, 188), fill=(*accent_rgb, 170), width=3)

    body_y = 305 if beat["visual"].get("type") == "comparison_bars" else 350
    draw.multiline_text((width // 2, body_y), body, font=body_font, fill=WHITE, anchor="mm", align="center", spacing=18)
    draw_comparison_bars(draw, beat, accent)

    if beat["id"] == "verdict":
        stamp_font = ImageFont.truetype(str(FONT_BANGERS), 72)
        draw.rounded_rectangle((230, 500, 710, 610), radius=18, outline=RED, width=8)
        centered_text(draw, (470, 555), "CÓ TỘI CÓ ĐIỀU KIỆN", stamp_font, RED)
    elif beat["id"] == "triple_cta":
        prompt_font = ImageFont.truetype(str(FONT_BANGERS), 54)
        draw.rounded_rectangle((210, 500, 730, 610), radius=26, fill=(167, 139, 250, 42), outline=PURPLE, width=5)
        centered_text(draw, (470, 555), "10  HAY  16?", prompt_font, WHITE)

    note = sanitize_card_text(beat["source_note"])
    draw.text((48, height - 47), note, font=note_font, fill=MUTED)
    img.save(output)
    return output


def render_motion_background(image: Path, duration: float, output: Path) -> None:
    frames = round(duration * FPS)
    vf = (
        "zoompan=z='1.035+0.018*sin(on/24)':"
        "x='iw/2-(iw/zoom/2)+10*sin(on/31)':"
        "y='ih/2-(ih/zoom/2)+14*cos(on/37)':"
        f"d=1:s={WIDTH}x{HEIGHT}:fps={FPS},format=yuv420p"
    )
    run([
        "ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(image),
        "-vf", vf, "-an", "-frames:v", str(frames), *encode_args(), str(output),
    ])


def render_footage_background(path: Path, offset: float, duration: float, output: Path, loop: bool) -> None:
    frames = round(duration * FPS)
    command = ["ffmpeg", "-y", "-v", "error"]
    if loop:
        command += ["-stream_loop", "-1"]
    command += ["-ss", f"{offset:.3f}", "-i", str(path)]
    vf = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},fps={FPS},"
        "eq=brightness=-0.16:contrast=1.08:saturation=0.86,format=yuv420p"
    )
    command += ["-vf", vf, "-an", "-frames:v", str(frames), *encode_args(), str(output)]
    run(command)


def concat_video_parts(parts: list[Path], output: Path) -> None:
    concat_file = output.with_suffix(".txt")
    concat_file.write_text("".join(f"file '{part.resolve()}'\n" for part in parts), encoding="utf-8")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(output)])


def render_base_for_beat(beat: dict[str, Any], index: int, duration: float) -> Path:
    output = WORK / "segments" / f"{index:02d}_{beat['id']}_base.mp4"
    output.parent.mkdir(parents=True, exist_ok=True)
    background = build_background_png(beat, index)
    visual = beat["visual"]
    if visual["type"] == "pexels":
        render_footage_background(PEXELS[visual["asset_id"]], float(visual.get("offset", 0)), duration, output, loop=True)
        return output
    if visual["type"] == "source_then_motion":
        source_duration = min(float(visual["source_duration"]), duration)
        source_part = WORK / "segments" / f"{index:02d}_{beat['id']}_source.mp4"
        motion_part = WORK / "segments" / f"{index:02d}_{beat['id']}_motion.mp4"
        render_footage_background(SOURCE, float(visual["source_start"]), source_duration, source_part, loop=False)
        parts = [source_part]
        remainder = duration - source_duration
        if remainder > 0.02:
            render_motion_background(background, remainder, motion_part)
            parts.append(motion_part)
        concat_video_parts(parts, output)
        return output
    render_motion_background(background, duration, output)
    return output


def composite_segment(base: Path, card: Path, chrome: Path, duration: float, output: Path) -> None:
    frames = round(duration * FPS)
    filter_graph = (
        "[1:v]format=rgba,fade=t=in:st=0:d=0.18:alpha=1[card];"
        "[0:v][card]overlay=x=(W-w)/2:y='190+7*sin(2*PI*t/3)'[withcard];"
        "[2:v]format=rgba[chrome];"
        "[withcard][chrome]overlay=0:0:shortest=1,format=yuv420p[vout]"
    )
    run([
        "ffmpeg", "-y", "-v", "error", "-i", str(base),
        "-loop", "1", "-t", f"{duration:.6f}", "-i", str(card),
        "-loop", "1", "-t", f"{duration:.6f}", "-i", str(chrome),
        "-filter_complex", filter_graph, "-map", "[vout]", "-an",
        "-frames:v", str(frames), *encode_args(), str(output),
    ])


def render_visuals(spec: dict[str, Any], timeline: list[dict[str, Any]]) -> Path:
    chrome = build_chrome()
    outputs = []
    for beat, row in zip(spec["beats"], timeline):
        index = row["index"]
        base = render_base_for_beat(beat, index, row["duration"])
        card = build_card(beat, index)
        output = WORK / "segments" / f"{index:02d}_{beat['id']}.mp4"
        composite_segment(base, card, chrome, row["duration"], output)
        outputs.append(output)
    combined = WORK / "visuals_no_audio.mp4"
    concat_video_parts(outputs, combined)
    return combined


def render_audio(spec: dict[str, Any], timeline: list[dict[str, Any]]) -> Path:
    audio_dir = WORK / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    normalized = []
    for beat, row in zip(spec["beats"], timeline):
        source = ROOT / row["tts"]
        output = audio_dir / f"{row['index']:02d}_{beat['id']}.wav"
        filters = (
            "aresample=48000,aformat=channel_layouts=stereo,"
            "acompressor=threshold=0.1:ratio=4:attack=5:release=100:makeup=1,"
            "loudnorm=I=-16:TP=-1.5:LRA=10,"
            f"apad=pad_dur={row['duration']:.6f},atrim=0:{row['duration']:.6f}"
        )
        run([
            "ffmpeg", "-y", "-v", "error", "-i", str(source), "-af", filters,
            "-ar", str(SAMPLE_RATE), "-ac", "2", "-c:a", "pcm_s16le", str(output),
        ])
        normalized.append(output)
    concat_file = audio_dir / "narration_concat.txt"
    concat_file.write_text("".join(f"file '{path.resolve()}'\n" for path in normalized), encoding="utf-8")
    narration = audio_dir / "narration.wav"
    run([
        "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
        "-i", str(concat_file), "-c:a", "pcm_s16le", str(narration),
    ])
    return narration


def add_tone(track: np.ndarray, start: float, duration: float, frequencies: list[float], amplitude: float, decay: float) -> None:
    begin = max(0, int(start * SAMPLE_RATE))
    length = min(len(track) - begin, int(duration * SAMPLE_RATE))
    if length <= 0:
        return
    t = np.arange(length, dtype=np.float64) / SAMPLE_RATE
    signal = np.zeros(length, dtype=np.float64)
    for frequency in frequencies:
        signal += np.sin(2 * np.pi * frequency * t)
    signal /= max(1, len(frequencies))
    envelope = np.exp(-decay * t)
    track[begin : begin + length] += (signal * envelope * amplitude).astype(np.float32)


def build_sfx(timeline: list[dict[str, Any]], total_duration: float) -> Path:
    output = WORK / "audio/sfx_track.wav"
    track = np.zeros(int(total_duration * SAMPLE_RATE), dtype=np.float32)
    for row in timeline:
        add_tone(track, row["start"] + 0.08, 0.16, [520, 1040], 0.22, 20)
    add_tone(track, 0.12, 0.40, [88, 176, 900], 0.62, 12)
    cta = next(row for row in timeline if row["id"] == "triple_cta")
    add_tone(track, cta["start"] + 0.05, 0.65, [660, 990, 1320], 0.38, 4)
    verdict = next(row for row in timeline if row["id"] == "verdict")
    add_tone(track, verdict["start"] + 0.08, 0.45, [92, 184, 780], 0.58, 11)
    add_tone(track, verdict["start"] + 0.32, 0.38, [82, 164, 720], 0.46, 12)
    peak = float(np.max(np.abs(track))) or 1.0
    track = np.clip(track / max(1.0, peak / 0.9), -0.95, 0.95)
    stereo = np.column_stack([track, track])
    pcm = (stereo * 32767).astype(np.int16)
    with wave.open(str(output), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(pcm.tobytes())
    return output


def build_music(total_duration: float) -> Path:
    output = WORK / "audio/courtroom_music.wav"
    expr = (
        "aevalsrc=(0.045*sin(2*PI*58*t)*(0.3+0.7*exp(-7*mod(t\\,0.5)))+"
        "0.012*sin(2*PI*116*t)+0.008*sin(2*PI*174*t))*"
        f"min(1\\,t/0.8)*min(1\\,({total_duration:.6f}-t)/0.8):"
        f"s={SAMPLE_RATE}:d={total_duration:.6f}"
    )
    run([
        "ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", expr,
        "-af", "lowpass=f=1400,highpass=f=35", "-ar", str(SAMPLE_RATE),
        "-ac", "2", "-c:a", "pcm_s16le", str(output),
    ])
    return output


def build_captions(spec: dict[str, Any], timeline: list[dict[str, Any]]) -> Path:
    output = WORK / "captions.ass"
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Cap,Bangers,96,&H00FFFFFF,&H0000D7FF,&H00000000,&H60000000,0,0,0,0,100,100,1,0,1,8,2,5,70,70,0,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    events = []
    for beat, row in zip(spec["beats"], timeline):
        bursts = beat["captions"]
        weights = [max(1, len(item["text"].split())) for item in bursts]
        weight_sum = sum(weights)
        cursor = row["start"] + 0.05
        usable = max(0.5, row["speech_duration"] - 0.08)
        for item, weight in zip(bursts, weights):
            duration = usable * weight / weight_sum
            end = min(row["start"] + row["speech_duration"], cursor + duration)
            text = item["text"].upper()
            keyword = item["keyword"].upper()
            escaped = escape_ass(text)
            escaped_keyword = escape_ass(keyword)
            if keyword in text:
                escaped = escaped.replace(
                    escaped_keyword,
                    r"{\c&H0000D7FF&}" + escaped_keyword + r"{\c&H00FFFFFF&}",
                    1,
                )
            animation = r"{\an5\pos(540,1160)\fad(45,55)\t(0,140,\fscx106\fscy106)}"
            events.append(
                f"Dialogue: 5,{ass_time(cursor)},{ass_time(end)},Cap,,0,0,0,,{animation}{escaped}\n"
            )
            cursor = end
    output.write_text(header + "".join(events), encoding="utf-8")
    return output


def final_composite(
    visuals: Path,
    narration: Path,
    music: Path,
    sfx: Path,
    captions: Path,
    watermark: Path,
    total_duration: float,
) -> None:
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    fonts_dir = FONT_BANGERS.parent
    filter_graph = (
        f"[0:v]subtitles='{captions}':fontsdir='{fonts_dir}'[captioned];"
        "[4:v]format=rgba[wm];"
        "[captioned][wm]overlay="
        "x='if(lt(mod(t,16),8),45,W-w-45)':"
        "y='if(lt(mod(t,32),16),155,H-h-65)':shortest=1[vout];"
        "[1:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.0[voice];"
        "[2:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.08[music];"
        "[3:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.52[sfx];"
        f"[voice][music][sfx]amix=inputs=3:duration=longest:normalize=0,"
        f"alimiter=limit=0.94,apad=whole_dur={total_duration:.6f},"
        f"atrim=0:{total_duration:.6f}[aout]"
    )
    run([
        "ffmpeg", "-y", "-v", "error", "-i", str(visuals), "-i", str(narration),
        "-i", str(music), "-i", str(sfx), "-loop", "1", "-t", f"{total_duration:.6f}",
        "-i", str(watermark), "-filter_complex", filter_graph,
        "-map", "[vout]", "-map", "[aout]", *encode_args(),
        "-c:a", "aac", "-b:a", "192k", "-ar", str(SAMPLE_RATE), "-ac", "2",
        "-movflags", "+faststart", "-t", f"{total_duration:.6f}", str(FINAL),
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep-work", action="store_true", help="Retain intermediate render files")
    args = parser.parse_args()

    required = [SPEC_PATH, SOURCE, FONT_BANGERS, *PEXELS.values()]
    missing = [path for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required inputs: {missing}")

    WORK.mkdir(parents=True, exist_ok=True)
    spec = load_spec()
    prepared_tts = prepare_trimmed_tts(spec)
    timeline, total_duration = build_timeline(spec, prepared_tts)
    timing_record = {
        "case_id": spec["case_id"],
        "total_duration": total_duration,
        "cta_start": next(row["start"] for row in timeline if row["id"] == "triple_cta"),
        "source_reuse_seconds": 6.5,
        "timeline": timeline,
        "script_sha256": hashlib.sha256(SPEC_PATH.read_bytes()).hexdigest(),
    }
    (WORK / "timing.json").write_text(json.dumps(timing_record, indent=2), encoding="utf-8")
    print(json.dumps(timing_record, indent=2), flush=True)

    visuals = render_visuals(spec, timeline)
    narration = render_audio(spec, timeline)
    music = build_music(total_duration)
    sfx = build_sfx(timeline, total_duration)
    captions = build_captions(spec, timeline)
    watermark = build_watermark()
    final_composite(visuals, narration, music, sfx, captions, watermark, total_duration)

    if not args.keep_work:
        for path in (WORK / "segments").glob("*_base.mp4"):
            path.unlink(missing_ok=True)
        for path in (WORK / "segments").glob("*_source.mp4"):
            path.unlink(missing_ok=True)
        for path in (WORK / "segments").glob("*_motion.mp4"):
            path.unlink(missing_ok=True)
    print(f"FINAL={FINAL}", flush=True)


if __name__ == "__main__":
    main()
