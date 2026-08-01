#!/usr/bin/env python3
"""Render the Stage-0 rough hook for HardKnocks V24: gave away 90%."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "hardknocks"
SOURCE = PROJECT / "source" / "HeuqoqyRQdk.webm"
WORK = PROJECT / "clips" / "v24_gave_away_90_work"
HOOK_DIR = WORK / "hook_gate"
BASE_HOOK = HOOK_DIR / "rough_hook_v1_base.mp4"
CAPTIONS = HOOK_DIR / "rough_hook_v1.ass"
TIMED_SFX = HOOK_DIR / "rough_hook_v1_sfx.wav"
ROUGH_HOOK = HOOK_DIR / "rough_hook_v1_gave_away_90.mp4"

FONT_KOMIKA = ROOT / "assets" / "fonts" / "komika-axis" / "KOMIKAX_.ttf"
PROOF_TICK = ROOT / "assets" / "sfx" / "generated" / "hardknocks_v22" / "proof_tick.wav"
HOOK_HIT = ROOT / "assets" / "sfx" / "generated" / "hardknocks_v22" / "hook_origin_hit.wav"

WIDTH = 1080
HEIGHT = 1920
FPS = 30
SOURCE_START = 549.50
SOURCE_END = 555.56
DURATION = SOURCE_END - SOURCE_START
CAPTION_BAND_PX = 270


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hook-only", action="store_true", help="Render the Stage-0 rough hook")
    return parser.parse_args()


def run(command: list[str | Path]) -> None:
    print("+", " ".join(str(item) for item in command), flush=True)
    subprocess.run([str(item) for item in command], cwd=ROOT, check=True)


def source_crop() -> str:
    clean_height = HEIGHT - CAPTION_BAND_PX
    recovery_width = round(WIDTH * HEIGHT / clean_height)
    zoom_width = round(WIDTH * 1.08)
    zoom_height = round(HEIGHT * 1.08)
    guest_x = round((3414 - WIDTH) * 0.66)
    return (
        f"scale=3414:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:{guest_x}:0,"
        f"scale={zoom_width}:{zoom_height}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:(in_w-{WIDTH})/2:0,"
        f"crop={WIDTH}:{clean_height}:0:0,"
        f"scale={recovery_width}:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:({recovery_width}-{WIDTH})/2:0,"
        "eq=contrast=1.05:saturation=1.04,setsar=1,format=yuv420p"
    )


def render_base() -> None:
    coarse_start = SOURCE_START - 5.0
    fine_start = SOURCE_START - coarse_start
    fine_end = fine_start + DURATION
    video_filter = (
        f"trim=start={fine_start:.6f}:end={fine_end:.6f},setpts=PTS-STARTPTS,"
        f"{source_crop()},fps={FPS}"
    )
    audio_filter = (
        f"atrim=start={fine_start:.6f}:end={fine_end:.6f},asetpts=PTS-STARTPTS,"
        "highpass=f=70,acompressor=threshold=0.125:ratio=2:attack=5:release=80:makeup=1.35,"
        "loudnorm=I=-16:TP=-1.5:LRA=10,aresample=48000:first_pts=0,apad,"
        f"atrim=0:{DURATION:.6f},afade=t=in:st=0:d=0.06,"
        f"afade=t=out:st={DURATION - 0.10:.6f}:d=0.10"
    )
    run([
        "ffmpeg", "-y", "-v", "error", "-ss", f"{coarse_start:.6f}", "-i", SOURCE,
        "-filter_complex", f"[0:v]{video_filter}[v];[0:a]{audio_filter}[a]",
        "-map", "[v]", "-map", "[a]", "-frames:v", str(round(DURATION * FPS)),
        "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        BASE_HOOK,
    ])


def write_ass() -> None:
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {WIDTH}
PlayResY: {HEIGHT}
ScaledBorderAndShadow: yes
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,Komika Axis,82,&H00FFFFFF,&H000000FF,&H00101010,&H50000000,-1,0,0,0,100,100,0,0,1,7,3,2,70,70,720,1
Style: Watermark,Arial,28,&H70FFFFFF,&H000000FF,&H40000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,1,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = [
        r"Dialogue: 5,0:00:00.00,0:00:01.12,Hook,,0,0,0,,{\fad(20,30)\t(0,120,\fscx106\fscy106)}STARTED WITH {\c&H43D4FF&}100%",
        r"Dialogue: 5,0:00:01.12,0:00:02.50,Hook,,0,0,0,,{\fad(20,30)\t(0,120,\fscx106\fscy106)}ENDED WITH {\c&H43D4FF&}10%",
        r"Dialogue: 5,0:00:02.50,0:00:04.35,Hook,,0,0,0,,{\fad(20,30)\t(0,120,\fscx106\fscy106)}A {\c&H43D4FF&}$1.5B{\c&HFFFFFF&} HEADLINE",
        r"Dialogue: 5,0:00:04.35,0:00:06.06,Hook,,0,0,0,,{\fad(20,30)\t(0,120,\fscx106\fscy106)}WHY GIVE UP {\c&H43D4FF&}90%?",
        r"Dialogue: 3,0:00:00.00,0:00:06.06,Watermark,,0,0,0,,{\move(35,1780,760,1780,0,6060)}@MONEY BLINDSPOT",
    ]
    CAPTIONS.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


def build_sfx() -> None:
    run([
        "ffmpeg", "-y", "-v", "error", "-i", HOOK_HIT, "-i", PROOF_TICK,
        "-f", "lavfi", "-t", "1.120", "-i", "anullsrc=r=48000:cl=stereo",
        "-f", "lavfi", "-t", "2.500", "-i", "anullsrc=r=48000:cl=stereo",
        "-filter_complex",
        f"[0:a]volume=-19dB,apad,atrim=0:{DURATION:.6f}[hit];"
        f"[2:a][1:a]concat=n=2:v=0:a=1,volume=-20dB,apad,atrim=0:{DURATION:.6f}[ten];"
        f"[3:a][1:a]concat=n=2:v=0:a=1,volume=-18dB,apad,atrim=0:{DURATION:.6f}[value];"
        f"[hit][ten][value]amix=inputs=3:duration=longest:normalize=0,atrim=0:{DURATION:.6f}[out]",
        "-map", "[out]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", TIMED_SFX,
    ])


def finish() -> None:
    escaped_ass = str(CAPTIONS).replace("'", r"\'")
    run([
        "ffmpeg", "-y", "-v", "error", "-i", BASE_HOOK, "-i", TIMED_SFX,
        "-filter_complex",
        f"[0:v]setpts=PTS+0.010/TB,subtitles='{escaped_ass}':fontsdir='{FONT_KOMIKA.parent}',"
        "setpts=PTS-STARTPTS[v];"
        "[0:a][1:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.88:level=false[a]",
        "-map", "[v]", "-map", "[a]", "-frames:v", str(round(DURATION * FPS)),
        "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        ROUGH_HOOK,
    ])


def main() -> None:
    args = parse_args()
    if not args.hook_only:
        raise SystemExit("V24 is blocked at Stage 0. Use --hook-only until the Human Hook Gate passes.")
    for required in (SOURCE, FONT_KOMIKA, PROOF_TICK, HOOK_HIT):
        if not required.is_file():
            raise FileNotFoundError(required)
    HOOK_DIR.mkdir(parents=True, exist_ok=True)
    render_base()
    write_ass()
    build_sfx()
    finish()
    print(ROUGH_HOOK)


if __name__ == "__main__":
    main()
