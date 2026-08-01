#!/usr/bin/env python3
"""Render the full HardKnocks V24 ownership-dilution Short."""

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
WORK = PROJECT / "clips" / "v24_gave_away_90_work"
SEGMENT_DIR = WORK / "full_segments"
AUDIO_DIR = WORK / "audio" / "qwen-zack"
CHECKS = WORK / "checks"
CANDIDATE = WORK / "candidate_v1_gave_away_90.mp4"
BASE = WORK / "base_v1_gave_away_90.mp4"
ASS_PATH = WORK / "captions_v1.ass"
SFX_TRACK = WORK / "sfx_v1.wav"
FINAL = PROJECT / "final" / "2026-08-01-hardknocks_v24_gave_away_90.mp4"
TIMELINE_PATH = WORK / "timeline.json"

PEXELS_MEAL = ROOT / "output" / "shared" / "pexels" / "healthy_meal_5961891.mp4"
PEXELS_TEAM = ROOT / "output" / "shared" / "pexels" / "team_meeting_7643614.mp4"
PEXELS_FACT = ROOT / "output" / "shared" / "pexels" / "contract_signing_7981954.mp4"
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
    visual: str | None = None
    voice: str | None = None
    visual_start: float = 0.0
    turns: tuple[tuple[float, float], ...] = ((0.0, 0.66),)


SEGMENTS = (
    Segment("01_ownership_hook", "source", 182 / FPS, source_start=549.50),
    Segment("02_fifteen_dollars", "source", 217 / FPS, source_start=439.72),
    Segment("03_bankrupt_debt", "source", 268 / FPS, source_start=447.16),
    Segment("04_growth_claim", "source_broll", 259 / FPS, source_start=391.60, visual=str(PEXELS_MEAL), visual_start=0.1),
    Segment("05_fact_check", "narration", 217 / FPS, visual=str(PEXELS_FACT), voice="fact_check.wav", visual_start=0.3),
    Segment("06_triple_cta", "narration", 120 / FPS, visual=str(PEXELS_TEAM), voice="triple_cta_v2.wav", visual_start=2.0),
    Segment(
        "07_investor_risk",
        "source",
        230 / FPS,
        source_start=562.62,
        turns=((0.0, 0.34), (4.14, 0.66)),
    ),
    Segment("08_people_payoff", "source", 209 / FPS, source_start=555.76),
    Segment("09_smarter_people", "source", 178 / FPS, source_start=570.48),
    Segment("10_coach", "source", 100 / FPS, source_start=582.30),
    Segment("11_loop_closure", "narration", 132 / FPS, visual=str(PEXELS_TEAM), voice="loop_closure.wav", visual_start=7.0),
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
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--promote", action="store_true")
    return parser.parse_args()


def run(command: list[str | Path]) -> None:
    print("+", " ".join(str(item) for item in command), flush=True)
    subprocess.run([str(item) for item in command], cwd=ROOT, check=True)


def focus_x(focus: float) -> int:
    return round((3414 - WIDTH) * focus)


def focus_expression(turns: tuple[tuple[float, float], ...]) -> str:
    expression = str(focus_x(turns[-1][1]))
    for index in range(len(turns) - 2, -1, -1):
        boundary = turns[index + 1][0]
        expression = f"if(lt(t,{boundary:.3f}),{focus_x(turns[index][1])},{expression})"
    return expression


def source_crop(turns: tuple[tuple[float, float], ...]) -> str:
    clean_height = HEIGHT - CAPTION_BAND_PX
    recovery_width = round(WIDTH * HEIGHT / clean_height)
    return (
        f"scale=3414:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:'{focus_expression(turns)}':0,"
        "scale=1166:2074:flags=lanczos,crop=1080:1920:(in_w-1080)/2:0,"
        f"crop={WIDTH}:{clean_height}:0:0,"
        f"scale={recovery_width}:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:({recovery_width}-{WIDTH})/2:0,"
        "eq=contrast=1.05:saturation=1.04,setsar=1,format=yuv420p"
    )


def segment_audio(duration: float) -> str:
    return (
        "highpass=f=70,acompressor=threshold=0.125:ratio=2.2:attack=5:release=80:makeup=1.30,"
        "loudnorm=I=-16:TP=-1.5:LRA=10,aresample=48000:first_pts=0,apad,"
        f"atrim=0:{duration:.6f},afade=t=in:st=0:d=0.07,"
        f"afade=t=out:st={duration - 0.12:.6f}:d=0.12"
    )


def encoding(output: Path, duration: float) -> list[str | Path]:
    return [
        "-frames:v", str(round(duration * FPS)),
        "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-g", "60", "-sc_threshold", "0",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-video_track_timescale", "90000", output,
    ]


def render_source(segment: Segment, output: Path) -> None:
    assert segment.source_start is not None
    coarse = max(0.0, segment.source_start - 5.0)
    fine = segment.source_start - coarse
    video = (
        f"trim=start={fine:.6f}:end={fine + segment.duration:.6f},setpts=PTS-STARTPTS,"
        f"{source_crop(segment.turns)},fps={FPS},tpad=stop_mode=clone:stop_duration=0.20,"
        f"trim=duration={segment.duration:.6f}"
    )
    audio = (
        f"atrim=start={fine:.6f}:end={fine + segment.duration:.6f},asetpts=PTS-STARTPTS,"
        f"{segment_audio(segment.duration)}"
    )
    command: list[str | Path] = [
        "ffmpeg", "-y", "-v", "error", "-ss", f"{coarse:.6f}", "-i", SOURCE,
        "-filter_complex", f"[0:v]{video}[v];[0:a]{audio}[a]", "-map", "[v]", "-map", "[a]",
    ]
    command.extend(encoding(output, segment.duration))
    run(command)


def render_source_broll(segment: Segment, output: Path) -> None:
    assert segment.source_start is not None and segment.visual is not None
    coarse = max(0.0, segment.source_start - 5.0)
    fine = segment.source_start - coarse
    video = (
        f"trim=start={segment.visual_start:.6f}:duration={segment.duration:.6f},setpts=PTS-STARTPTS,"
        f"scale=3414:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:'(in_w-out_w)*(0.30+0.32*t/{segment.duration:.3f})':0,"
        "eq=contrast=1.06:saturation=0.96:brightness=-0.03,setsar=1,format=yuv420p,"
        f"fps={FPS},tpad=stop_mode=clone:stop_duration=0.20,trim=duration={segment.duration:.6f}"
    )
    audio = (
        f"atrim=start={fine:.6f}:end={fine + segment.duration:.6f},asetpts=PTS-STARTPTS,"
        f"{segment_audio(segment.duration)}"
    )
    command: list[str | Path] = [
        "ffmpeg", "-y", "-v", "error", "-ss", f"{coarse:.6f}", "-i", SOURCE, "-i", segment.visual,
        "-filter_complex", f"[1:v]{video}[v];[0:a]{audio}[a]", "-map", "[v]", "-map", "[a]",
    ]
    command.extend(encoding(output, segment.duration))
    run(command)


def render_narration(segment: Segment, output: Path) -> None:
    assert segment.visual is not None and segment.voice is not None
    pan_start, pan_end = ((0.28, 0.62) if "fact" in segment.name else (0.52, 0.34))
    video = (
        f"trim=start={segment.visual_start:.6f}:duration={segment.duration:.6f},setpts=PTS-STARTPTS,"
        f"scale=3414:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:'(in_w-out_w)*({pan_start:.3f}+({pan_end-pan_start:.3f})*t/{segment.duration:.3f})':0,"
        "eq=contrast=1.05:saturation=0.90:brightness=-0.05,setsar=1,format=yuv420p,"
        f"fps={FPS},tpad=stop_mode=clone:stop_duration=0.20,trim=duration={segment.duration:.6f}"
    )
    audio = (
        "highpass=f=70,acompressor=threshold=0.10:ratio=4:attack=5:release=100:makeup=1,"
        "loudnorm=I=-16:TP=-1.5:LRA=10,aresample=48000:first_pts=0,apad,"
        f"atrim=0:{segment.duration:.6f},afade=t=in:st=0:d=0.06,"
        f"afade=t=out:st={segment.duration - 0.12:.6f}:d=0.12"
    )
    command: list[str | Path] = [
        "ffmpeg", "-y", "-v", "error", "-i", segment.visual, "-i", AUDIO_DIR / segment.voice,
        "-filter_complex", f"[0:v]{video}[v];[1:a]{audio}[a]", "-map", "[v]", "-map", "[a]",
    ]
    command.extend(encoding(output, segment.duration))
    run(command)


def build_base() -> None:
    SEGMENT_DIR.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for index, segment in enumerate(SEGMENTS, start=1):
        output = SEGMENT_DIR / f"{index:02d}_{segment.name}.mp4"
        outputs.append(output)
        if segment.kind == "source":
            render_source(segment, output)
        elif segment.kind == "source_broll":
            render_source_broll(segment, output)
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


def offsets() -> dict[str, float]:
    result: dict[str, float] = {}
    cursor = 0.0
    for segment in SEGMENTS:
        result[segment.name] = cursor
        cursor += segment.duration
    return result


def build_captions() -> list[Caption]:
    out: list[Caption] = []
    os = offsets()

    def add(name: str, rows: tuple[tuple[float, float, str], ...], style: str = "Caption") -> None:
        base = os[name]
        out.extend(Caption(base + start, base + end, text, style) for start, end, text in rows)

    add("01_ownership_hook", (
        (0.00, 1.12, r"STARTED WITH {\c&H43D4FF&}100%"),
        (1.12, 2.50, r"ENDED WITH {\c&H43D4FF&}10%"),
        (2.50, 4.35, r"A {\c&H43D4FF&}$1.5B{\c&HFFFFFF&} HEADLINE"),
        (4.35, 6.06, r"WHY GIVE UP {\c&H43D4FF&}90%?"),
    ))
    add("01_ownership_hook", ((0.05, 6.00, r"OWNERSHIP  ██████████ 100%  →  █ 10%"),), "Evidence")

    add("02_fifteen_dollars", (
        (0.00, 2.20, r"{\c&H43D4FF&}$15{\c&HFFFFFF&} IN MY BANK"),
        (2.20, 3.40, r"WHEN I {\c&H43D4FF&}STARTED"),
        (3.40, 4.25, r"HOW {\c&H43D4FF&}OLD?"),
        (4.25, 5.40, r"I WAS {\c&H43D4FF&}35"),
        (5.40, 7.23, r"{\c&H43D4FF&}$15{\c&HFFFFFF&} AT 35"),
    ))
    add("02_fifteen_dollars", ((0.05, 7.10, r"STARTING BALANCE  •  FOUNDER STATEMENT"),), "Evidence")

    add("03_bankrupt_debt", (
        (0.00, 1.15, r"MY LAST {\c&H43D4FF&}COMPANY"),
        (1.15, 2.40, r"WENT {\c&H43D4FF&}BANKRUPT"),
        (2.40, 4.85, r"I CAME OUT WITH {\c&H43D4FF&}TENACITY"),
        (4.85, 6.55, r"{\c&H43D4FF&}$1 MILLION{\c&HFFFFFF&} IN DEBT"),
        (6.55, 8.93, r"THAT CREATED {\c&H43D4FF&}URGENCY"),
    ))
    add("03_bankrupt_debt", ((4.75, 8.80, r"DEBT  $1,000,000  •  FOUNDER STATEMENT"),), "Evidence")

    add("04_growth_claim", (
        (0.00, 1.90, r"FRESH MEALS {\c&H43D4FF&}DELIVERED"),
        (1.90, 3.95, r"DIRECTLY TO {\c&H43D4FF&}YOUR HOUSE"),
        (3.95, 5.40, r"THIRD {\c&H43D4FF&}FASTEST-GROWING"),
        (5.40, 7.15, r"ZERO TO {\c&H43D4FF&}$550M SALES"),
        (7.15, 8.63, r"IN JUST OVER {\c&H43D4FF&}FIVE YEARS"),
    ))
    add("04_growth_claim", ((0.05, 8.55, r"ZERO  →  $550M / 5 YEARS  •  FOUNDER CLAIM"),), "Evidence")

    add("05_fact_check", (
        (0.00, 1.30, r"THE HEADLINE {\c&H43D4FF&}HIDES THE DEAL"),
        (1.30, 3.10, r"{\c&H43D4FF&}$950M{\c&HFFFFFF&} AT CLOSE"),
        (3.10, 4.70, r"PLUS UP TO {\c&H43D4FF&}$550M"),
        (4.70, 7.23, r"ONLY IF {\c&H43D4FF&}GROWTH TARGETS HIT"),
    ))
    add("05_fact_check", ((0.05, 7.10, r"NESTLÉ  •  OCT 30, 2020  •  OFFICIAL RELEASE"),), "Source")
    add("05_fact_check", ((1.20, 7.05, r"$950M BASE VALUE  +  UP TO $550M EARNOUT"),), "Evidence")

    add("06_triple_cta", (
        (0.00, 1.20, r"{\c&H43D4FF&}LIKE{\c&HFFFFFF&} FOR MORE"),
        (1.20, 2.25, r"{\c&H43D4FF&}SUBSCRIBE"),
        (2.25, 4.00, r"{\c&H43D4FF&}COMMENT:{\c&HFFFFFF&} KEEP OR SCALE?"),
    ), "CTA")

    add("07_investor_risk", (
        (0.00, 1.70, r"DON'T INVESTORS {\c&H43D4FF&}ADD RISK?"),
        (1.70, 3.25, r"YOU GIVE UP {\c&H43D4FF&}CONTROL"),
        (3.25, 4.15, r"AND {\c&H43D4FF&}DECISIONS"),
        (4.15, 5.55, r"THE HUBRIS IS"),
        (5.55, 7.66, r"THINKING I HAVE {\c&H43D4FF&}ALL ANSWERS"),
    ))
    add("07_investor_risk", ((1.60, 7.55, r"CONTROL  ◉◉◉◉◉  →  SHARED DECISIONS"),), "Evidence")

    add("08_people_payoff", (
        (0.00, 1.25, r"IF I DIDN'T SELL {\c&H43D4FF&}90%"),
        (1.25, 3.15, r"AND GET THE {\c&H43D4FF&}PEOPLE"),
        (3.15, 4.75, r"INCLUDING {\c&H43D4FF&}EMPLOYEES"),
        (4.75, 6.90, r"THERE'S NO {\c&H43D4FF&}$1.5B EXIT"),
    ))
    add("08_people_payoff", ((0.10, 6.85, r"90% DILUTION  →  PEOPLE + CAPITAL  →  SCALE"),), "Evidence")

    add("09_smarter_people", (
        (0.00, 1.60, r"I CAN GET {\c&H43D4FF&}SMARTER PEOPLE"),
        (1.60, 3.25, r"WHO'VE {\c&H43D4FF&}DONE THINGS"),
        (3.25, 4.40, r"AND I CAN"),
        (4.40, 5.93, r"{\c&H43D4FF&}LISTEN TO THEM"),
    ))

    add("10_coach", (
        (0.00, 1.60, r"WHATEVER SPORT {\c&H43D4FF&}YOU PLAY"),
        (1.60, 3.33, r"YOU GET A {\c&H43D4FF&}COACH"),
    ))

    add("11_loop_closure", (
        (0.00, 1.55, r"HE TRADED {\c&H43D4FF&}CONTROL"),
        (1.55, 2.80, r"FOR THE {\c&H43D4FF&}TEAM"),
        (2.80, 4.40, r"THAT MADE {\c&H43D4FF&}SCALE POSSIBLE"),
    ))
    add("11_loop_closure", ((0.15, 4.35, r"100% OF A SMALLER OUTCOME  <  10% OF A LARGER ONE"),), "Evidence")
    return out


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
Style: Evidence,Arial,36,&H00FFFFFF,&H000000FF,&H40101010,&H90000000,-1,0,0,0,100,100,1,0,1,4,2,8,40,40,1580,1
Style: Watermark,Arial,27,&H68FFFFFF,&H000000FF,&H40000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,1,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines: list[str] = []
    for caption in build_captions():
        effect = r"{\fad(20,35)\t(0,120,\fscx105\fscy105)}" if caption.style in {"Caption", "CTA"} else r"{\fad(80,80)}"
        lines.append(f"Dialogue: 5,{ass_time(caption.start)},{ass_time(caption.end)},{caption.style},,0,0,0,,{effect}{caption.text}")
    for start, end, x1, x2 in ((0.0, 23.0, 35, 770), (23.0, 46.0, 770, 35), (46.0, TOTAL_DURATION, 35, 770)):
        lines.append(
            f"Dialogue: 3,{ass_time(start)},{ass_time(end)},Watermark,,0,0,0,,"
            rf"{{\move({x1},92,{x2},92,0,{round((end-start)*1000)})}}@MONEY BLINDSPOT"
        )
    ASS_PATH.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")


def build_sfx_track() -> None:
    assets = {
        "tick": SFX_DIR / "proof_tick.wav",
        "hit": SFX_DIR / "hook_origin_hit.wav",
        "whoosh": SFX_DIR / "jet_motion_whoosh.wav",
        "warm": SFX_DIR / "payoff_warm_hit.wav",
        "click": SFX_DIR / "cta_click.wav",
    }
    os = offsets()
    events = [
        (0.00, "hit", -19.0), (1.12, "tick", -20.0), (2.50, "tick", -18.0),
        (os["02_fifteen_dollars"] + 0.55, "tick", -21.0),
        (os["03_bankrupt_debt"] + 4.85, "hit", -25.0),
        (os["04_growth_claim"] + 5.40, "whoosh", -25.0),
        (os["05_fact_check"], "warm", -25.0),
        (os["05_fact_check"] + 1.30, "tick", -19.0),
        (os["05_fact_check"] + 3.10, "tick", -19.0),
        (os["06_triple_cta"], "click", -19.0),
        (os["06_triple_cta"] + 1.20, "click", -19.0),
        (os["06_triple_cta"] + 2.25, "click", -19.0),
        (os["08_people_payoff"], "warm", -21.0),
        (os["11_loop_closure"], "warm", -22.0),
    ]
    bed = SFX_DIR / "restrained_finance_bed.wav"
    command: list[str | Path] = ["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", bed]
    indexes: dict[str, int] = {}
    for name, path in assets.items():
        indexes[name] = len(indexes) + 1
        command.extend(["-i", path])
    filters = [f"[0:a]volume=-31dB,atrim=0:{TOTAL_DURATION:.6f}[bed]"]
    labels: list[str] = []
    for index, (at, name, gain) in enumerate(events):
        filters.append(f"[{indexes[name]}:a]volume={gain:.1f}dB[e{index}]")
        filters.append(f"anullsrc=r=48000:cl=stereo:d={at:.6f}[s{index}]")
        filters.append(f"[s{index}][e{index}]concat=n=2:v=0:a=1,apad,atrim=0:{TOTAL_DURATION:.6f}[p{index}]")
        labels.append(f"[p{index}]")
    filters.append(
        f"[bed]{''.join(labels)}amix=inputs={1+len(labels)}:duration=longest:normalize=0,"
        f"alimiter=limit=0.82:level=false,atrim=0:{TOTAL_DURATION:.6f}[out]"
    )
    command.extend(["-filter_complex", ";".join(filters), "-map", "[out]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", SFX_TRACK])
    run(command)


def finish_candidate() -> None:
    escaped_ass = str(ASS_PATH).replace("'", r"\'")
    run([
        "ffmpeg", "-y", "-v", "error", "-i", BASE, "-i", SFX_TRACK,
        "-filter_complex",
        f"[0:v]setpts=PTS+0.010/TB,subtitles='{escaped_ass}':fontsdir='{FONT_KOMIKA.parent}',"
        "setpts=PTS-STARTPTS[v];[0:a][1:a]amix=inputs=2:duration=first:normalize=0,"
        "alimiter=limit=0.80:level=false[a]",
        "-map", "[v]", "-map", "[a]", "-frames:v", str(round(TOTAL_DURATION * FPS)),
        "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-g", "60", "-sc_threshold", "0",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", CANDIDATE,
    ])


def write_timeline() -> None:
    cursor = 0.0
    payload: list[dict[str, object]] = []
    for segment in SEGMENTS:
        item = asdict(segment)
        item["output_start"] = round(cursor, 3)
        item["output_end"] = round(cursor + segment.duration, 3)
        payload.append(item)
        cursor += segment.duration
    TIMELINE_PATH.write_text(json.dumps({"total_duration": TOTAL_DURATION, "segments": payload}, indent=2) + "\n", encoding="utf-8")


def validate_inputs() -> None:
    required = [SOURCE, PEXELS_MEAL, PEXELS_TEAM, PEXELS_FACT, FONT_KOMIKA]
    required.extend(AUDIO_DIR / name for name in ("fact_check.wav", "triple_cta_v2.wav", "loop_closure.wav"))
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
