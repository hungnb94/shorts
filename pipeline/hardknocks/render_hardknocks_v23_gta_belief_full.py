#!/usr/bin/env python3
"""Render the full HardKnocks V23 GTA/control Short after Stage-0 approval."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "hardknocks"
SOURCE = PROJECT / "source" / "HeuqoqyRQdk.webm"
WORK = PROJECT / "clips" / "v23_gta_belief_work"
SEGMENT_DIR = WORK / "full_segments"
AUDIO_DIR = WORK / "audio" / "qwen-zack"
CHECKS = WORK / "checks"
CANDIDATE = WORK / "candidate_v1_gta_belief_control.mp4"
BASE = WORK / "base_v1_gta_belief_control.mp4"
ASS_PATH = WORK / "captions_v1.ass"
SFX_TRACK = WORK / "sfx_v1.wav"
FINAL = PROJECT / "final" / "2026-07-31-hardknocks_v23_gta_belief_control.mp4"
TIMELINE_PATH = WORK / "timeline.json"

PEXELS_PRODUCT = ROOT / "output" / "shared" / "pexels" / "product_design_8003421.mp4"
PEXELS_TEAM = ROOT / "output" / "shared" / "pexels" / "team_meeting_7643614.mp4"
FONT_KOMIKA = ROOT / "assets" / "fonts" / "komika-axis" / "KOMIKAX_.ttf"
SFX_DIR = ROOT / "assets" / "sfx" / "generated" / "hardknocks_v22"

WIDTH = 1080
HEIGHT = 1920
FPS = 30
CAPTION_BAND_PX = 270


@dataclass(frozen=True)
class Segment:
    name: str
    kind: str
    duration: float
    source_start: float | None = None
    source_end: float | None = None
    visual: str | None = None
    voice: str | None = None
    visual_start: float = 0.0
    turns: tuple[tuple[float, float], ...] = ((0.0, 0.66),)


SEGMENTS = (
    Segment(
        "01_gta_scale",
        "source",
        299 / FPS,
        source_start=923.10,
        source_end=923.10 + 299 / FPS,
        turns=((0.00, 0.34), (0.64, 0.66), (2.62, 0.34), (3.74, 0.66), (4.70, 0.34), (5.22, 0.66), (6.20, 0.34), (7.30, 0.66)),
    ),
    Segment("02_authority_bridge", "narration", 129 / FPS, visual=str(PEXELS_PRODUCT), voice="authority_bridge.wav", visual_start=0.7),
    Segment("03_overnight", "source", 229 / FPS, source_start=954.26, source_end=954.26 + 229 / FPS),
    Segment("04_five_years", "source", 212 / FPS, source_start=961.94, source_end=961.94 + 212 / FPS),
    Segment("05_integrity", "source", 279 / FPS, source_start=1000.18, source_end=1000.18 + 279 / FPS),
    Segment("06_counter_bridge", "narration", 111 / FPS, visual=str(PEXELS_TEAM), voice="counter_bridge.wav", visual_start=0.8),
    Segment("07_triple_cta", "narration", 108 / FPS, visual=str(PEXELS_TEAM), voice="triple_cta.wav", visual_start=5.0),
    Segment(
        "08_colleagues",
        "source",
        221 / FPS,
        source_start=1026.90,
        source_end=1026.90 + 221 / FPS,
        turns=((0.00, 0.34), (1.46, 0.66), (2.14, 0.34), (3.82, 0.66), (4.34, 0.34), (5.86, 0.66)),
    ),
    Segment("09_spiritual", "source", 183 / FPS, source_start=1050.50, source_end=1050.50 + 183 / FPS, turns=((0.00, 0.34), (1.14, 0.66))),
    Segment("10_wingspan", "source", 247 / FPS, source_start=1063.38, source_end=1063.38 + 247 / FPS),
    Segment("11_outcomes", "source", 230 / FPS, source_start=1071.60, source_end=1071.60 + 230 / FPS),
)

TOTAL_DURATION = sum(segment.duration for segment in SEGMENTS)


@dataclass(frozen=True)
class Caption:
    start: float
    end: float
    text: str
    style: str = "Caption"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true", help="Render the exact candidate")
    parser.add_argument("--promote", action="store_true", help="Copy the reviewed candidate into final/")
    return parser.parse_args()


def run(command: list[str | Path]) -> None:
    print("+", " ".join(str(item) for item in command), flush=True)
    subprocess.run([str(item) for item in command], cwd=ROOT, check=True)


def probe_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def focus_x(focus: float) -> int:
    scaled_width = 3414
    return round((scaled_width - WIDTH) * focus)


def focus_expression(turns: tuple[tuple[float, float], ...]) -> str:
    expression = str(focus_x(turns[-1][1]))
    for index in range(len(turns) - 2, -1, -1):
        boundary = turns[index + 1][0]
        expression = f"if(lt(t,{boundary:.3f}),{focus_x(turns[index][1])},{expression})"
    return expression


def source_crop(turns: tuple[tuple[float, float], ...]) -> str:
    clean_height = HEIGHT - CAPTION_BAND_PX
    recovery_width = round(WIDTH * HEIGHT / clean_height)
    zoom_width = round(WIDTH * 1.08)
    zoom_height = round(HEIGHT * 1.08)
    return (
        f"scale=3414:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:'{focus_expression(turns)}':0,"
        f"scale={zoom_width}:{zoom_height}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:(in_w-{WIDTH})/2:0,"
        f"crop={WIDTH}:{clean_height}:0:0,"
        f"scale={recovery_width}:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:({recovery_width}-{WIDTH})/2:0,"
        "eq=contrast=1.05:saturation=1.04,setsar=1,format=yuv420p"
    )


def segment_audio(duration: float) -> str:
    fade_out_start = max(0.0, duration - 0.10)
    return (
        "highpass=f=70,acompressor=threshold=0.125:ratio=2.2:attack=5:release=80:makeup=1.30,"
        "loudnorm=I=-16:TP=-1.5:LRA=10,aresample=48000:first_pts=0,apad,"
        f"atrim=0:{duration:.6f},afade=t=in:st=0:d=0.07,"
        f"afade=t=out:st={fade_out_start:.6f}:d=0.10"
    )


def output_encoding(output: Path, duration: float) -> list[str | Path]:
    return [
        "-frames:v", str(round(duration * FPS)),
        "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-g", "60", "-sc_threshold", "0",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-video_track_timescale", "90000", output,
    ]


def render_source(segment: Segment, output: Path) -> None:
    assert segment.source_start is not None and segment.source_end is not None
    coarse_start = max(0.0, segment.source_start - 5.0)
    fine_start = segment.source_start - coarse_start
    fine_end = fine_start + segment.duration
    video = (
        f"trim=start={fine_start:.6f}:end={fine_end:.6f},setpts=PTS-STARTPTS,"
        f"{source_crop(segment.turns)},fps={FPS},"
        f"tpad=stop_mode=clone:stop_duration=0.20,trim=duration={segment.duration:.6f}"
    )
    audio = (
        f"atrim=start={fine_start:.6f}:end={fine_end:.6f},asetpts=PTS-STARTPTS,"
        f"{segment_audio(segment.duration)}"
    )
    command: list[str | Path] = [
        "ffmpeg", "-y", "-v", "error", "-ss", f"{coarse_start:.6f}", "-i", SOURCE,
        "-filter_complex", f"[0:v]{video}[v];[0:a]{audio}[a]", "-map", "[v]", "-map", "[a]",
    ]
    command.extend(output_encoding(output, segment.duration))
    run(command)


def render_narration(segment: Segment, output: Path) -> None:
    assert segment.visual is not None and segment.voice is not None
    visual = Path(segment.visual)
    voice = AUDIO_DIR / segment.voice
    voice_duration = probe_duration(voice)
    tempo = voice_duration / segment.duration
    if not 0.5 <= tempo <= 2.0:
        raise RuntimeError(f"Unsupported atempo {tempo:.3f} for {segment.name}")
    pan_start = 0.30 if "authority" in segment.name else 0.48
    pan_end = 0.64 if "authority" in segment.name else 0.36
    video_filter = (
        f"trim=start={segment.visual_start:.6f}:duration={segment.duration:.6f},setpts=PTS-STARTPTS,"
        f"scale=3414:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:'(in_w-out_w)*({pan_start:.3f}+({pan_end - pan_start:.3f})*t/{segment.duration:.3f})':0,"
        "eq=contrast=1.05:saturation=0.90:brightness=-0.03,setsar=1,format=yuv420p,"
        f"fps={FPS},tpad=stop_mode=clone:stop_duration=0.20,trim=duration={segment.duration:.6f}"
    )
    audio_filter = (
        f"atempo={tempo:.6f},highpass=f=70,"
        "acompressor=threshold=0.10:ratio=4:attack=5:release=100:makeup=1,"
        f"loudnorm=I=-16:TP=-1.5:LRA=10,aresample=48000:first_pts=0,apad,atrim=0:{segment.duration:.6f},"
        f"afade=t=in:st=0:d=0.06,afade=t=out:st={segment.duration - 0.10:.6f}:d=0.10"
    )
    command: list[str | Path] = [
        "ffmpeg", "-y", "-v", "error", "-i", visual, "-i", voice,
        "-filter_complex", f"[0:v]{video_filter}[v];[1:a]{audio_filter}[a]", "-map", "[v]", "-map", "[a]",
    ]
    command.extend(output_encoding(output, segment.duration))
    run(command)


def build_base() -> None:
    SEGMENT_DIR.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for index, segment in enumerate(SEGMENTS, start=1):
        output = SEGMENT_DIR / f"{index:02d}_{segment.name}.mp4"
        outputs.append(output)
        if segment.kind == "source":
            render_source(segment, output)
        else:
            render_narration(segment, output)

    concat_file = SEGMENT_DIR / "concat.txt"
    concat_file.write_text("".join(f"file '{path.resolve()}'\n" for path in outputs), encoding="utf-8")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", BASE])


def ass_time(seconds: float) -> str:
    centiseconds = round(seconds * 100)
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    secs, cs = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{cs:02d}"


def add_local(captions: list[Caption], offset: float, start: float, end: float, text: str, style: str = "Caption") -> None:
    captions.append(Caption(offset + start, offset + end, text, style))


def build_captions() -> list[Caption]:
    captions: list[Caption] = []
    offsets: dict[str, float] = {}
    cursor = 0.0
    for segment in SEGMENTS:
        offsets[segment.name] = cursor
        cursor += segment.duration

    o = offsets["01_gta_scale"]
    for start, end, text in (
        (0.00, 0.64, r"GTA V — {\c&H43D4FF&}YOUR COMPANY?"),
        (0.64, 1.56, r"ONE OF {\c&H43D4FF&}OUR GAMES"),
        (1.56, 2.62, r"OUR {\c&H43D4FF&}BIGGEST GAME"),
        (2.62, 3.74, r"HOW MANY {\c&H43D4FF&}COPIES?"),
        (3.74, 4.70, r"{\c&H43D4FF&}230 MILLION"),
        (4.70, 5.74, r"WHAT {\c&H43D4FF&}COMPANY?"),
        (5.74, 6.42, r"{\c&H43D4FF&}TAKE-TWO INTERACTIVE"),
        (6.42, 7.30, r"HOW {\c&H43D4FF&}BIG TODAY?"),
        (7.30, 9.86, r"ABOUT A {\c&H43D4FF&}$40B MARKET CAP"),
    ):
        add_local(captions, o, start, end, text)
    add_local(captions, o, 0.15, 3.50, r"STRAUSS ZELNICK  •  TAKE-TWO CEO", "Source")
    add_local(captions, o, 3.55, 5.20, r"OFFICIAL MAY 2026: NEARLY 230M SOLD-IN", "Evidence")
    add_local(captions, o, 7.15, 9.80, r"$40B = SOURCE STATEMENT  •  INTERVIEW DATE", "Evidence")

    o = offsets["02_authority_bridge"]
    add_local(captions, o, 0.00, 1.30, r"{\c&H43D4FF&}TAKE-TWO'S CEO")
    add_local(captions, o, 1.30, 2.75, r"PUBLISHER {\c&H43D4FF&}BEHIND GTA")
    add_local(captions, o, 2.75, 4.30, r"HARDEST RULE: {\c&H43D4FF&}CONTROL")
    add_local(captions, o, 0.00, 4.30, r"ILLUSTRATION  •  PEXELS", "Source")

    o = offsets["03_overnight"]
    for start, end, text in (
        (0.00, 1.30, r"EVERYONE'S LOOKING FOR"),
        (1.30, 2.10, r"{\c&H43D4FF&}OVERNIGHT SUCCESS"),
        (2.10, 4.30, r"THE ONLY OVERNIGHT SUCCESSES"),
        (4.30, 5.40, r"ARE {\c&H43D4FF&}SOMEONE ELSE'S"),
        (5.40, 6.70, r"EVERYTHING WORTH DOING"),
        (6.70, 7.64, r"IS {\c&H43D4FF&}HARD AND SLOW"),
    ):
        add_local(captions, o, start, end, text)

    o = offsets["04_five_years"]
    for start, end, text in (
        (0.00, 1.90, r"TOOK OVER IN {\c&H43D4FF&}2007"),
        (1.90, 3.50, r"{\c&H43D4FF&}FIVE YEARS BEFORE"),
        (3.50, 4.85, r"REAL {\c&H43D4FF&}SUCCESS"),
        (4.85, 6.10, r"{\c&H43D4FF&}19 YEARS LATER"),
        (6.10, 7.08, r"STILL {\c&H43D4FF&}AT IT"),
    ):
        add_local(captions, o, start, end, text)
    add_local(captions, o, 0.00, 7.00, r"2007  →  5 YEARS  →  19 YEARS", "Evidence")

    o = offsets["05_integrity"]
    for start, end, text in (
        (0.00, 2.00, r"ONE TIME IN {\c&H43D4FF&}PARTICULAR"),
        (2.00, 4.45, r"I ACTED {\c&H43D4FF&}AGAINST"),
        (4.45, 6.45, r"MY OWN {\c&H43D4FF&}INTEGRITY"),
        (6.45, 7.45, r"IT HURT ME {\c&H43D4FF&}BADLY"),
        (7.45, 8.70, r"A {\c&H43D4FF&}POWERFUL LESSON"),
        (8.70, 9.30, r"{\c&H43D4FF&}NEVER DO THAT"),
    ):
        add_local(captions, o, start, end, text)

    o = offsets["06_counter_bridge"]
    add_local(captions, o, 0.00, 1.10, r"FAITH ISN'T {\c&H43D4FF&}PROVEN")
    add_local(captions, o, 1.10, 2.20, r"{\c&H43D4FF&}CAUSAL")
    add_local(captions, o, 2.20, 2.85, r"HIS {\c&H43D4FF&}LESSON")
    add_local(captions, o, 2.85, 3.70, r"{\c&H43D4FF&}CONTROL")
    add_local(captions, o, 0.00, 3.70, r"CAUSALITY CHECK  •  ILLUSTRATION", "Source")
    add_local(captions, o, 0.35, 3.50, r"FAITH  ≠  PROVEN CAUSE OF WEALTH", "Evidence")

    o = offsets["07_triple_cta"]
    add_local(captions, o, 0.00, 0.95, r"{\c&H43D4FF&}LIKE THIS STORY", "CTA")
    add_local(captions, o, 0.95, 1.95, r"{\c&H43D4FF&}SUBSCRIBE FOR MORE", "CTA")
    add_local(captions, o, 1.95, 3.60, r"COMMENT: WHAT CAN YOU {\c&H43D4FF&}CONTROL?", "CTA")
    add_local(captions, o, 0.00, 3.60, r"ILLUSTRATION  •  PEXELS", "Source")

    o = offsets["08_colleagues"]
    for start, end, text in (
        (0.00, 1.30, r"HOW MANY {\c&H43D4FF&}EMPLOYEES?"),
        (1.30, 2.10, r"{\c&H43D4FF&}20,000"),
        (2.10, 3.20, r"20,000 {\c&H43D4FF&}EMPLOYEES"),
        (3.20, 4.20, r"{\c&H43D4FF&}COLLEAGUES"),
        (4.20, 5.05, r"WHY {\c&H43D4FF&}NOT?"),
        (5.05, 7.36, r"I'M JUST ANOTHER {\c&H43D4FF&}COLLEAGUE"),
    ):
        add_local(captions, o, start, end, text)
    add_local(captions, o, 1.25, 7.20, r"20,000 PEOPLE  •  ONE COLLEAGUE", "Evidence")

    o = offsets["09_spiritual"]
    for start, end, text in (
        (0.00, 1.14, r"BELIEVE IN {\c&H43D4FF&}GOD?"),
        (1.14, 2.64, r"I HAVE A {\c&H43D4FF&}SPIRITUAL LIFE"),
        (2.64, 4.20, r"NOT SURE YOU'D CALL"),
        (4.20, 5.20, r"THAT BELIEVING IN {\c&H43D4FF&}GOD"),
        (5.20, 6.10, r"BUT I {\c&H43D4FF&}DO"),
    ):
        add_local(captions, o, start, end, text)

    o = offsets["10_wingspan"]
    for start, end, text in (
        (0.00, 1.40, r"IT'S A {\c&H43D4FF&}BELIEF"),
        (1.40, 3.90, r"I CAN {\c&H43D4FF&}CONTROL"),
        (3.90, 5.00, r"AND BE {\c&H43D4FF&}RESPONSIBLE FOR"),
        (5.00, 6.35, r"WHAT'S WITHIN MY {\c&H43D4FF&}WINGSPAN"),
        (6.35, 8.24, r"EVERYTHING ELSE IS {\c&H43D4FF&}OUTSIDE"),
    ):
        add_local(captions, o, start, end, text)
    add_local(captions, o, 1.20, 8.10, r"INSIDE WINGSPAN  ◉  OUTSIDE OUTCOMES", "Evidence")

    o = offsets["11_outcomes"]
    for start, end, text in (
        (0.00, 1.10, r"I CAN {\c&H43D4FF&}CONTROL"),
        (1.10, 1.90, r"MY {\c&H43D4FF&}DESIRES"),
        (1.90, 2.90, r"MY {\c&H43D4FF&}ACTIONS"),
        (2.90, 3.70, r"MY {\c&H43D4FF&}GOALS"),
        (3.70, 4.60, r"MY {\c&H43D4FF&}PLANS"),
        (4.60, 5.45, r"I CAN'T {\c&H43D4FF&}CONTROL"),
        (5.45, 6.00, r"THE {\c&H43D4FF&}OUTCOMES"),
        (6.00, 7.68, r"OUTCOMES ARE {\c&H43D4FF&}OUTSIDE"),
    ):
        add_local(captions, o, start, end, text)
    add_local(captions, o, 0.00, 4.60, r"DESIRES  •  ACTIONS  •  GOALS  •  PLANS", "Evidence")
    add_local(captions, o, 4.60, 7.68, r"EFFORT IS YOURS  •  OUTCOME ISN'T", "Evidence")
    return captions


def write_ass() -> None:
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {WIDTH}
PlayResY: {HEIGHT}
ScaledBorderAndShadow: yes
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Komika Axis,78,&H00FFFFFF,&H000000FF,&H00101010,&H50000000,-1,0,0,0,100,100,0,0,1,7,3,2,70,70,720,1
Style: CTA,Komika Axis,72,&H00FFFFFF,&H000000FF,&H00101010,&H60000000,-1,0,0,0,100,100,0,0,1,8,4,2,55,55,690,1
Style: Source,Arial,26,&H00E6E6E6,&H000000FF,&H50000000,&H80000000,-1,0,0,0,100,100,1,0,1,3,1,7,38,38,1700,1
Style: Evidence,Arial,31,&H00FFFFFF,&H000000FF,&H40101010,&H90000000,-1,0,0,0,100,100,1,0,1,4,2,8,40,40,1590,1
Style: Watermark,Arial,27,&H68FFFFFF,&H000000FF,&H40000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,1,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines: list[str] = []
    for caption in build_captions():
        effect = r"{\fad(20,35)\t(0,120,\fscx105\fscy105)}" if caption.style in {"Caption", "CTA"} else r"{\fad(80,80)}"
        lines.append(
            f"Dialogue: 5,{ass_time(caption.start)},{ass_time(caption.end)},{caption.style},,0,0,0,,{effect}{caption.text}"
        )
    watermark_legs = (
        (0.0, 25.0, 35, 770),
        (25.0, 50.0, 770, 35),
        (50.0, TOTAL_DURATION, 35, 770),
    )
    for start, end, x1, x2 in watermark_legs:
        lines.append(
            f"Dialogue: 3,{ass_time(start)},{ass_time(end)},Watermark,,0,0,0,,"
            rf"{{\move({x1},92,{x2},92,0,{round((end - start) * 1000)})}}@MONEY BLINDSPOT"
        )
    ASS_PATH.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")


def build_sfx_track() -> None:
    bed = SFX_DIR / "restrained_finance_bed.wav"
    assets = {
        "tick": SFX_DIR / "proof_tick.wav",
        "hit": SFX_DIR / "hook_origin_hit.wav",
        "whoosh": SFX_DIR / "jet_motion_whoosh.wav",
        "warm": SFX_DIR / "payoff_warm_hit.wav",
        "click": SFX_DIR / "cta_click.wav",
    }
    offsets: dict[str, float] = {}
    cursor = 0.0
    for segment in SEGMENTS:
        offsets[segment.name] = cursor
        cursor += segment.duration
    events = [
        (0.06, "tick", -19.0),
        (0.64, "hit", -18.0),
        (2.72, "tick", -20.0),
        (3.74, "tick", -18.0),
        (offsets["02_authority_bridge"], "whoosh", -23.0),
        (offsets["05_integrity"], "hit", -27.0),
        (offsets["06_counter_bridge"], "warm", -25.0),
        (offsets["07_triple_cta"], "click", -19.0),
        (offsets["07_triple_cta"] + 0.95, "click", -19.0),
        (offsets["07_triple_cta"] + 1.95, "click", -19.0),
        (offsets["09_spiritual"], "warm", -26.0),
        (TOTAL_DURATION - 0.78, "warm", -21.0),
    ]
    command: list[str | Path] = ["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", bed]
    asset_indexes: dict[str, int] = {}
    for name, path in assets.items():
        asset_indexes[name] = len(asset_indexes) + 1
        command.extend(["-i", path])

    filters = [f"[0:a]volume=-31dB,atrim=0:{TOTAL_DURATION:.6f}[bed]"]
    event_labels: list[str] = []
    for index, (at, name, gain) in enumerate(events):
        input_index = asset_indexes[name]
        filters.append(f"[{input_index}:a]volume={gain:.1f}dB[e{index}]")
        filters.append(f"anullsrc=r=48000:cl=stereo:d={at:.6f}[s{index}]")
        filters.append(
            f"[s{index}][e{index}]concat=n=2:v=0:a=1,apad,atrim=0:{TOTAL_DURATION:.6f}[p{index}]"
        )
        event_labels.append(f"[p{index}]")
    mix_inputs = "[bed]" + "".join(event_labels)
    filters.append(
        f"{mix_inputs}amix=inputs={1 + len(event_labels)}:duration=longest:normalize=0,"
        f"alimiter=limit=0.82:level=false,atrim=0:{TOTAL_DURATION:.6f}[out]"
    )
    command.extend([
        "-filter_complex", ";".join(filters), "-map", "[out]", "-ar", "48000", "-ac", "2",
        "-c:a", "pcm_s16le", SFX_TRACK,
    ])
    run(command)


def finish_candidate() -> None:
    escaped_ass = str(ASS_PATH).replace("'", r"\'")
    command: list[str | Path] = [
        "ffmpeg", "-y", "-v", "error", "-i", BASE, "-i", SFX_TRACK,
        "-filter_complex",
        f"[0:v]setpts=PTS+0.010/TB,subtitles='{escaped_ass}':fontsdir='{FONT_KOMIKA.parent}',"
        "setpts=PTS-STARTPTS[v];"
        "[0:a][1:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.80:level=false[a]",
        "-map", "[v]", "-map", "[a]", "-frames:v", str(round(TOTAL_DURATION * FPS)),
        "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-g", "60", "-sc_threshold", "0",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", CANDIDATE,
    ]
    run(command)


def write_timeline() -> None:
    cursor = 0.0
    payload: list[dict[str, object]] = []
    for segment in SEGMENTS:
        item = asdict(segment)
        item["output_start"] = round(cursor, 3)
        item["output_end"] = round(cursor + segment.duration, 3)
        payload.append(item)
        cursor += segment.duration
    TIMELINE_PATH.write_text(
        json.dumps({"total_duration": TOTAL_DURATION, "segments": payload}, indent=2), encoding="utf-8"
    )


def validate_inputs() -> None:
    required = [SOURCE, PEXELS_PRODUCT, PEXELS_TEAM, FONT_KOMIKA]
    required.extend(AUDIO_DIR / name for name in ("authority_bridge.wav", "counter_bridge.wav", "triple_cta.wav"))
    required.extend(SFX_DIR / name for name in (
        "restrained_finance_bed.wav", "proof_tick.wav", "hook_origin_hit.wav",
        "jet_motion_whoosh.wav", "payoff_warm_hit.wav", "cta_click.wav",
    ))
    missing = [path for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing inputs:\n" + "\n".join(str(path) for path in missing))


def main() -> None:
    args = parse_args()
    if not args.render and not args.promote:
        raise SystemExit("Choose --render or --promote")
    if args.render:
        validate_inputs()
        for directory in (WORK, SEGMENT_DIR, CHECKS):
            directory.mkdir(parents=True, exist_ok=True)
        build_base()
        write_ass()
        build_sfx_track()
        finish_candidate()
        write_timeline()
        print(CANDIDATE)
    if args.promote:
        if not CANDIDATE.is_file():
            raise FileNotFoundError(CANDIDATE)
        FINAL.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(CANDIDATE, FINAL)
        print(FINAL)


if __name__ == "__main__":
    main()
