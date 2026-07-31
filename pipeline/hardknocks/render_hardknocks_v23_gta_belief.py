#!/usr/bin/env python3
"""Render the Stage-0 rough hook for HardKnocks V23: GTA and control.

The opening applies the shared V18/V21 hook pattern: a moving human face,
source-native question/answer, familiar high-stakes object, frame-zero captions,
and a complete first micro-payoff before the broader story opens.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "hardknocks"
SOURCE = PROJECT / "source" / "HeuqoqyRQdk.webm"
WORK = PROJECT / "clips" / "v23_gta_belief_work"
HOOK_DIR = WORK / "hook_gate"
ROUGH_HOOK = HOOK_DIR / "rough_hook_v1_gta_company_reveal.mp4"
BASE_HOOK = HOOK_DIR / "rough_hook_v1_base.mp4"
CAPTIONS = HOOK_DIR / "rough_hook_v1.ass"
TIMED_SFX = HOOK_DIR / "rough_hook_v1_sfx.wav"

FONT_KOMIKA = ROOT / "assets" / "fonts" / "komika-axis" / "KOMIKAX_.ttf"
PROOF_TICK = ROOT / "assets" / "sfx" / "generated" / "hardknocks_v22" / "proof_tick.wav"
REVEAL_HIT = ROOT / "assets" / "sfx" / "generated" / "hardknocks_v22" / "hook_origin_hit.wav"

WIDTH = 1080
HEIGHT = 1920
FPS = 30
SOURCE_START = 923.10
SOURCE_END = 925.82
DURATION = SOURCE_END - SOURCE_START
CAPTION_BAND_PX = 270


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hook-only", action="store_true", help="Render the Stage-0 rough hook")
    return parser.parse_args()


def run(command: list[str | Path]) -> None:
    print("+", " ".join(str(item) for item in command), flush=True)
    subprocess.run([str(item) for item in command], cwd=ROOT, check=True)


def crop_expr() -> str:
    scaled_width = 3414
    span = scaled_width - WIDTH

    def x_for(focus: float) -> int:
        return round(span * focus)

    host = x_for(0.34)
    guest = x_for(0.66)
    return f"if(lt(t,0.640),{host},{guest})"


def source_crop() -> str:
    clean_height = HEIGHT - CAPTION_BAND_PX
    recovery_width = round(WIDTH * HEIGHT / clean_height)
    zoom_width = round(WIDTH * 1.08)
    zoom_height = round(HEIGHT * 1.08)
    return (
        f"scale=3414:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:'{crop_expr()}':0,"
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
        f"atrim=0:{DURATION:.6f},afade=t=in:st=0:d=0.08,"
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
    font_name = "Komika Axis"
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {WIDTH}
PlayResY: {HEIGHT}
ScaledBorderAndShadow: yes
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,{font_name},80,&H00FFFFFF,&H000000FF,&H00101010,&H50000000,-1,0,0,0,100,100,0,0,1,7,3,2,70,70,720,1
Style: Watermark,Arial,28,&H70FFFFFF,&H000000FF,&H40000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,1,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = [
        r"Dialogue: 5,0:00:00.00,0:00:00.64,Hook,,0,0,0,,{\fad(20,30)\t(0,120,\fscx106\fscy106)}GTA V — {\c&H43D4FF&}YOUR COMPANY?",
        r"Dialogue: 5,0:00:00.64,0:00:01.56,Hook,,0,0,0,,{\fad(20,30)\t(0,120,\fscx106\fscy106)}ONE OF {\c&H43D4FF&}OUR GAMES",
        r"Dialogue: 5,0:00:01.56,0:00:02.72,Hook,,0,0,0,,{\fad(20,30)\t(0,120,\fscx106\fscy106)}OUR {\c&H43D4FF&}BIGGEST GAME",
        r"Dialogue: 3,0:00:00.00,0:00:02.72,Watermark,,0,0,0,,{\move(35,1780,760,90,0,2720)}@MONEY BLINDSPOT",
    ]
    CAPTIONS.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


def build_sfx() -> None:
    run([
        "ffmpeg", "-y", "-v", "error", "-i", PROOF_TICK, "-i", REVEAL_HIT,
        "-f", "lavfi", "-t", "0.060", "-i", "anullsrc=r=48000:cl=stereo",
        "-f", "lavfi", "-t", "0.640", "-i", "anullsrc=r=48000:cl=stereo",
        "-filter_complex",
        f"[2:a][0:a]concat=n=2:v=0:a=1,volume=-19dB,apad,atrim=0:{DURATION:.6f}[tick];"
        f"[3:a][1:a]concat=n=2:v=0:a=1,volume=-18dB,apad,atrim=0:{DURATION:.6f}[hit];"
        f"[tick][hit]amix=inputs=2:duration=longest:normalize=0,atrim=0:{DURATION:.6f}[out]",
        "-map", "[out]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", TIMED_SFX,
    ])


def finish() -> None:
    escaped_ass = str(CAPTIONS).replace("'", r"\'")
    run([
        "ffmpeg", "-y", "-v", "error", "-i", BASE_HOOK, "-i", TIMED_SFX,
        "-filter_complex",
        f"[0:v]setpts=PTS+0.010/TB,subtitles='{escaped_ass}':fontsdir='{FONT_KOMIKA.parent}',"
        "setpts=PTS-STARTPTS[v];"
        "[0:a][1:a]amix=inputs=2:duration=first:normalize=0,"
        "alimiter=limit=0.88:level=false[a]",
        "-map", "[v]", "-map", "[a]", "-frames:v", str(round(DURATION * FPS)),
        "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        ROUGH_HOOK,
    ])


def main() -> None:
    args = parse_args()
    if not args.hook_only:
        raise SystemExit("V23 is blocked at Stage 0. Use --hook-only until the Human Hook Gate passes.")
    for required in (SOURCE, FONT_KOMIKA, PROOF_TICK, REVEAL_HIT):
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
