#!/usr/bin/env python3
"""Render HardKnocks V20: Dana White's "Dumbest Idea" progression.

The edit applies payoff-first Setup -> Conflict -> Resolution, motivated cuts,
audio pre-laps, and a factual twist ladder. It is a one-off media renderer:
completion is verified against the real MP4, not renderer unit tests.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "hardknocks"
SOURCE = PROJECT / "source" / "ZdUmqGB-XpA.mp4"
WORK = PROJECT / "clips" / "v20_dana_work"
SEGMENT_DIR = WORK / "segments"
PANELS = WORK / "panels"
CHECKS = WORK / "checks"
AUDIO_DIR = WORK / "audio"
FINAL = PROJECT / "final" / "2026-07-29-hardknocks_v20_dana_dumbest_idea.mp4"

PEXELS_CONTRACT = ROOT / "output" / "shared" / "pexels" / "contract_signing_7981954.mp4"
PROOF_AUDIO = AUDIO_DIR / "proof_bridge.wav"
CTA_AUDIO = AUDIO_DIR / "cta.wav"
BRANDING = ROOT / "output" / "shared" / "hardknocks_branding"
TING = BRANDING / "verdict_correct_ting.wav"
BUZZ = BRANDING / "verdict_wrong_buzz.wav"

FONT_KOMIKA = ROOT / "assets" / "fonts" / "komika-axis" / "KOMIKAX_.ttf"
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
FONT_BLACK = Path("/System/Library/Fonts/Supplemental/Arial Black.ttf")

WIDTH = 1080
HEIGHT = 1920
FPS = 30
CAPTION_BAND_PX = 270
SEGMENT_FADE_IN = 0.12
SEGMENT_FADE_OUT = 0.20
SOURCE_DURATION = 1415.241

YELLOW = "#FFD23C"
GREEN = "#00D66E"
RED = "#FF4D4D"
BLUE = "#4FC3F7"
DARK = "#0B0E14"
GRAY = "#9AA3B2"


@dataclass(frozen=True)
class Segment:
    name: str
    kind: str
    start: float
    end: float
    turns: tuple[tuple[float, float], ...]
    zoom: float
    act: str
    audio: Path | None = None
    visual_start: float = 0.0

    @property
    def duration(self) -> float:
        return self.end - self.start


# Host is frame-left (~35% crop focus); Dana is frame-right (~65%). The hook
# reframes Dana at <=1.5s cadence while preserving real motion from frame zero.
SEGMENTS = (
    Segment(
        "hook_dumbest", "source", 861.54, 865.82,
        ((0.00, 0.64), (0.95, 0.66), (1.90, 0.63), (2.85, 0.66)),
        1.08, "setup",
    ),
    Segment(
        "failing_question", "source", 878.64, 884.06,
        ((0.00, 0.35), (1.40, 0.33), (2.80, 0.35), (4.20, 0.34)),
        1.07, "conflict",
    ),
    Segment(
        "storylines", "source", 885.28, 890.66,
        ((0.00, 0.65), (1.50, 0.63), (3.00, 0.66), (4.50, 0.64)),
        1.07, "mechanism_one",
    ),
    Segment(
        "break_rules", "source", 927.36, 934.50,
        ((0.00, 0.65), (2.00, 0.63), (4.00, 0.66), (6.00, 0.64)),
        1.07, "mechanism_two",
    ),
    Segment(
        "boxing_doubt", "source", 935.06, 940.56,
        ((0.00, 0.65), (1.60, 0.63), (3.20, 0.66), (4.70, 0.64)),
        1.08, "reversal",
    ),
    Segment(
        "proof_bridge", "narration", 0.00, 6.16,
        (), 1.00, "independent_evidence", PROOF_AUDIO, 0.20,
    ),
    Segment(
        "collapse_question", "source", 950.46, 957.30,
        ((0.00, 0.34), (2.30, 0.36), (4.88, 0.66), (6.00, 0.64)),
        1.07, "open_loop",
    ),
    Segment(
        "story_cta", "narration", 0.00, 5.68,
        (), 1.00, "cta", CTA_AUDIO, 4.20,
    ),
    Segment(
        "paramount_payoff", "source", 961.46, 969.88,
        ((0.00, 0.66), (1.42, 0.34), (1.90, 0.66), (3.10, 0.64),
         (5.30, 0.66), (7.10, 0.64)),
        1.08, "payoff",
    ),
    Segment(
        "prove_again", "source", 970.00, 973.52,
        ((0.00, 0.66), (1.70, 0.64), (3.00, 0.66)),
        1.07, "lesson",
    ),
    Segment(
        "loop_prep", "silent_source", 860.78, 861.48,
        ((0.00, 0.64),), 1.08, "loop",
    ),
)


CAPTIONS: dict[str, tuple[tuple[float, float, str, str], ...]] = {
    "hook_dumbest": (
        (0.00, 0.52, "I WANT TO BE", "WANT"),
        (0.52, 1.14, "IN THE FIGHT BUSINESS", "FIGHT"),
        (1.14, 2.16, "PROBABLY THE DUMBEST", "DUMBEST"),
        (2.16, 3.64, "IDEA EVER", "IDEA"),
        (3.64, 4.28, "AT THAT TIME", "TIME"),
    ),
    "failing_question": (
        (0.00, 1.12, "YOU MORTGAGED YOUR FUTURE", "FUTURE"),
        (1.12, 2.96, "ON A FAILING MMA COMPANY", "FAILING"),
        (3.12, 4.20, "WHAT DID YOU SEE", "SEE"),
        (4.20, 5.42, "THAT NOBODY ELSE SAW?", "NOBODY"),
    ),
    "storylines": (
        (0.00, 1.02, "ME AND MY PARTNERS", "PARTNERS"),
        (1.02, 2.68, "LOVED THE STORYLINES", "STORYLINES"),
        (2.82, 4.60, "FIGHTING WAS MORE EXCITING", "EXCITING"),
        (4.60, 5.38, "THAN BOXING", "BOXING"),
    ),
    "break_rules": (
        (0.00, 1.70, "GO IN AND BREAK", "BREAK"),
        (1.70, 2.48, "ALL THE RULES", "RULES"),
        (2.66, 4.28, "THIS WILL NEVER WORK", "NEVER"),
        (4.28, 5.66, "THEY'RE TOO BIG", "BIG"),
        (5.66, 7.14, "YOU CAN'T", "CAN'T"),
    ),
    "boxing_doubt": (
        (0.00, 0.86, "YOU'LL NEVER BE", "NEVER"),
        (0.86, 1.22, "BIGGER THAN BOXING", "BOXING"),
        (1.40, 3.82, "FOR 25 YEARS", "25 YEARS"),
        (4.12, 5.50, "YES, YOU CAN BE", "CAN"),
    ),
    "proof_bridge": (
        (0.00, 1.42, "HIS PARTNERS BOUGHT UFC", "BOUGHT"),
        (1.42, 2.24, "FOR $2 MILLION", "$2 MILLION"),
        (2.84, 3.94, "15 YEARS LATER", "15 YEARS"),
        (4.28, 5.84, "SOLD FOR ABOUT $4 BILLION", "$4 BILLION"),
    ),
    "collapse_question": (
        (0.00, 1.32, "WAS THERE A TIME", "TIME"),
        (1.32, 2.60, "GROWING THE UFC", "UFC"),
        (2.60, 3.46, "THIS IS ALL", "ALL"),
        (3.46, 4.76, "GOING TO COLLAPSE?", "COLLAPSE"),
        (4.88, 5.76, "YOU GO THROUGH THAT", "THROUGH"),
        (5.76, 6.84, "ALL THE TIME", "TIME"),
    ),
    "story_cta": (
        (0.00, 1.14, "LIKE AND SUBSCRIBE", "LIKE"),
        (1.46, 2.02, "THEN COMMENT", "COMMENT"),
        (2.16, 3.76, "DUMB BET OR SMART DISRUPTION?", "SMART"),
        (4.10, 5.58, "HERE'S THE NUMBER", "NUMBER"),
    ),
    "paramount_payoff": (
        (0.00, 0.76, "I DID A NEW DEAL", "DEAL"),
        (0.76, 1.32, "WITH PARAMOUNT", "PARAMOUNT"),
        (1.42, 1.90, "HOW MUCH?", "HOW MUCH"),
        (1.90, 3.02, "$7.7 BILLION", "$7.7 BILLION"),
        (3.02, 4.48, "DEAL WITH PARAMOUNT", "PARAMOUNT"),
        (4.62, 6.28, "NEW PARAMOUNT DEAL", "PARAMOUNT"),
        (6.96, 8.42, "ON A FRESH SLATE", "FRESH"),
    ),
    "prove_again": (
        (0.00, 1.56, "PROVE MYSELF AGAIN", "PROVE"),
        (1.72, 3.52, "KEEP PROVING YOURSELF", "PROVING"),
    ),
    "loop_prep": (
        (0.00, 0.70, "AND IT STARTED WITH...", "STARTED"),
    ),
}


def run(args: list[str | Path], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(str(arg) for arg in args), flush=True)
    return subprocess.run(
        [str(arg) for arg in args], cwd=ROOT, check=True, text=True,
        capture_output=capture,
    )


def probe(path: Path) -> dict[str, Any]:
    result = run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
        capture=True,
    )
    return json.loads(result.stdout)


def frames_for(seconds: float) -> int:
    return max(1, round(seconds * FPS))


def encode_args() -> list[str]:
    return [
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-pix_fmt", "yuv420p", "-r", str(FPS),
    ]


def crop_expr(turns: tuple[tuple[float, float], ...]) -> str:
    scaled_width = 3414
    span = scaled_width - WIDTH

    def x_for(focus: float) -> int:
        return round(span * focus)

    expr = str(x_for(turns[-1][1]))
    for index in range(len(turns) - 2, -1, -1):
        boundary = turns[index + 1][0]
        expr = f"if(lt(t,{boundary:.3f}),{x_for(turns[index][1])},{expr})"
    return expr


def source_crop(segment: Segment) -> str:
    x_expr = crop_expr(segment.turns)
    zoom_width = round(WIDTH * segment.zoom)
    zoom_height = round(HEIGHT * segment.zoom)
    clean_height = HEIGHT - CAPTION_BAND_PX
    recovery_width = round(WIDTH * HEIGHT / clean_height)
    return (
        f"scale=3414:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:'{x_expr}':0,"
        f"scale={zoom_width}:{zoom_height}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:(in_w-{WIDTH})/2:0,"
        f"crop={WIDTH}:{clean_height}:0:0,"
        f"scale={recovery_width}:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:({recovery_width}-{WIDTH})/2:0,"
        "eq=contrast=1.04:saturation=1.05,setsar=1,format=yuv420p"
    )


def render_source_segment(segment: Segment, output: Path) -> int:
    if segment.duration >= 15.0:
        raise ValueError(f"Source clip reaches 15 seconds: {segment.name}")
    frame_count = frames_for(segment.duration)
    coarse_start = max(0.0, segment.start - 5.0)
    fine_offset = segment.start - coarse_start
    volume = "volume=0" if segment.kind == "silent_source" else "volume=1"
    audio_filter = (
        f"atrim=start={fine_offset:.6f},asetpts=PTS-STARTPTS,{volume},highpass=f=70,"
        "acompressor=threshold=0.125:ratio=2:attack=5:release=80:makeup=1.4,"
        "loudnorm=I=-16:TP=-1.5:LRA=10,aresample=48000:first_pts=0,apad,"
        f"atrim=0:{segment.duration:.6f},"
        f"afade=t=in:st=0:d={SEGMENT_FADE_IN:.2f},"
        f"afade=t=out:st={max(0.0, segment.duration - SEGMENT_FADE_OUT):.6f}:d={SEGMENT_FADE_OUT:.2f}"
    )
    run([
        "ffmpeg", "-y", "-v", "error", "-ss", f"{coarse_start:.6f}",
        "-i", SOURCE, "-t", f"{segment.duration:.6f}",
        "-vf", f"trim=start={fine_offset:.6f},setpts=PTS-STARTPTS,{source_crop(segment)},fps={FPS}",
        "-af", audio_filter, "-frames:v", str(frame_count), *encode_args(),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", output,
    ])
    return frame_count


def render_narration_segment(segment: Segment, output: Path) -> int:
    if segment.audio is None:
        raise ValueError(f"Narration segment has no audio: {segment.name}")
    frame_count = frames_for(segment.duration)
    crop = (
        "scale=1150:2045:flags=lanczos,"
        "crop=1080:1920:x='35+25*sin(t*0.9)':y='62+35*sin(t*0.7)',"
        "eq=contrast=1.04:saturation=0.94,setsar=1,format=yuv420p,fps=30"
    )
    audio_filter = (
        "aresample=48000,aformat=channel_layouts=stereo,highpass=f=70,"
        "acompressor=threshold=0.1:ratio=4:attack=5:release=100:makeup=1,"
        "loudnorm=I=-16:TP=-1.5:LRA=10,apad,"
        f"atrim=0:{segment.duration:.6f},"
        f"afade=t=in:st=0:d={SEGMENT_FADE_IN:.2f},"
        f"afade=t=out:st={segment.duration - SEGMENT_FADE_OUT:.6f}:d={SEGMENT_FADE_OUT:.2f}"
    )
    run([
        "ffmpeg", "-y", "-v", "error", "-stream_loop", "-1",
        "-ss", f"{segment.visual_start:.3f}", "-i", PEXELS_CONTRACT,
        "-i", segment.audio, "-vf", crop, "-af", audio_filter,
        "-map", "0:v:0", "-map", "1:a:0",
        "-frames:v", str(frame_count), *encode_args(),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", output,
    ])
    return frame_count


def build_base() -> tuple[Path, list[dict[str, Any]], int]:
    SEGMENT_DIR.mkdir(parents=True, exist_ok=True)
    cursor = 0
    timeline: list[dict[str, Any]] = []
    outputs: list[Path] = []
    for index, segment in enumerate(SEGMENTS):
        output = SEGMENT_DIR / f"{index:02d}_{segment.name}.mp4"
        count = (
            render_narration_segment(segment, output)
            if segment.kind == "narration"
            else render_source_segment(segment, output)
        )
        timeline.append({
            "name": segment.name,
            "kind": segment.kind,
            "act": segment.act,
            "source_start": segment.start if segment.kind != "narration" else None,
            "source_end": segment.end if segment.kind != "narration" else None,
            "source_duration": segment.duration if segment.kind != "narration" else 0.0,
            "start_frame": cursor,
            "end_frame": cursor + count,
            "frames": count,
            "final_start": cursor / FPS,
            "final_end": (cursor + count) / FPS,
        })
        cursor += count
        outputs.append(output)

    concat = WORK / "concat.txt"
    concat.write_text("".join(f"file '{item.resolve()}'\n" for item in outputs), encoding="utf-8")
    base = WORK / "base.mp4"
    run([
        "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
        "-i", concat, "-c", "copy", base,
    ])
    return base, timeline, cursor


def new_card(width: int, height: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    card = Image.new("RGBA", (width, height), (11, 14, 20, 242))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle(
        (1, 1, width - 2, height - 2), radius=28,
        fill=(11, 14, 20, 242), outline=(255, 255, 255, 105), width=3,
    )
    return card, draw


def make_cards() -> list[Path]:
    PANELS.mkdir(parents=True, exist_ok=True)
    specs = (
        ("THE BET", (("DUMB IDEA", RED), ("FAILING UFC", YELLOW), ("WHY?", BLUE))),
        ("THE METHOD", (("STORYLINES", BLUE), ("BREAK RULES", YELLOW), ("BEAT BOXING", GREEN))),
        ("INDEPENDENT CHECK", (("$2M", YELLOW), ("→  $4B", GREEN), ("CNBC • 2016", GRAY))),
        ("THE PAYOFF", (("$7.7B", GREEN), ("7 YEARS", BLUE), ("TKO • 2025", GRAY))),
    )
    eyebrow = ImageFont.truetype(str(FONT_BOLD), 23)
    value = ImageFont.truetype(str(FONT_BLACK), 42)
    arrow = ImageFont.truetype(str(FONT_BOLD), 24)
    outputs: list[Path] = []
    for index, (title, rows) in enumerate(specs):
        card, draw = new_card(420, 360)
        draw.text((210, 38), title, font=eyebrow, fill=GRAY, anchor="mm")
        for row_index, (text, color) in enumerate(rows):
            y = 105 + row_index * 95
            draw.text((210, y), text, font=value, fill=color, anchor="mm")
            if row_index < len(rows) - 1 and not text.startswith("→"):
                draw.text((210, y + 47), "↓", font=arrow, fill="white", anchor="mm")
        output = PANELS / f"card_{index}.png"
        card.save(output)
        outputs.append(output)
    return outputs


def ass_time(seconds: float) -> str:
    centiseconds = max(0, round(seconds * 100))
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    secs, cs = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{cs:02d}"


def ass_color(hex_color: str) -> str:
    value = hex_color.lstrip("#")
    return f"&H00{value[4:6]}{value[2:4]}{value[0:2]}"


def ass_escape(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def emphasized(text: str, keyword: str) -> str:
    escaped = ass_escape(text)
    key = ass_escape(keyword)
    if key not in escaped:
        return escaped
    yellow = ass_color(YELLOW)
    white = ass_color("#FFFFFF")
    return escaped.replace(key, f"{{\\c{yellow}\\fs90}}{key}{{\\c{white}\\fs80}}", 1)


def write_ass(timeline: list[dict[str, Any]], total_duration: float) -> Path:
    starts = {item["name"]: item["final_start"] for item in timeline}
    ends = {item["name"]: item["final_end"] for item in timeline}
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {WIDTH}",
        f"PlayResY: {HEIGHT}",
        "ScaledBorderAndShadow: yes",
        "WrapStyle: 2",
        "",
        "[V4+ Styles]",
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding",
        "Style: Caption,Komika Axis,80,&H00FFFFFF,&H00FFFFFF,&H00000000,&H85000000,-1,0,0,0,100,100,0,0,1,8,2,5,78,78,700,1",
        "Style: State,Arial Bold,42,&H00FFFFFF,&H00FFFFFF,&H00000000,&HD00B0E14,-1,0,0,0,100,100,0,0,3,2,0,8,60,60,1525,1",
        "Style: CTA,Arial Black,54,&H00FFFFFF,&H00FFFFFF,&H00000000,&HE00B0E14,-1,0,0,0,100,100,0,0,3,3,0,8,90,90,1450,1",
        "Style: Small,Arial Bold,28,&H80FFFFFF,&H80FFFFFF,&H80000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,7,28,28,28,1",
        "",
        "[Events]",
        "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
    ]

    for segment_name, events in CAPTIONS.items():
        base = starts[segment_name]
        for rel_start, rel_end, text, keyword in events:
            y = 1240 if segment_name in {"proof_bridge", "story_cta"} else 1160
            body = f"{{\\an5\\pos(540,{y})}}{emphasized(text, keyword)}"
            lines.append(
                f"Dialogue: 8,{ass_time(base + rel_start)},{ass_time(base + rel_end)},Caption,,0,0,0,,{body}"
            )

    states = (
        (0.00, starts["failing_question"], "DUMB IDEA?", RED),
        (starts["failing_question"], starts["storylines"], "FAILING UFC", YELLOW),
        (starts["storylines"], starts["boxing_doubt"], "STORYLINES  →  BREAK RULES", BLUE),
        (starts["boxing_doubt"], ends["proof_bridge"], "NEVER BEAT BOXING?  →  $4B", GREEN),
        (starts["collapse_question"], ends["story_cta"], "WOULD IT COLLAPSE?", YELLOW),
        (starts["paramount_payoff"], starts["loop_prep"], "$7.7B  →  PROVE AGAIN", GREEN),
        (starts["loop_prep"], total_duration, "THE BET STARTS HERE", BLUE),
    )
    for start, end, text, color in states:
        lines.append(
            f"Dialogue: 6,{ass_time(start)},{ass_time(end)},State,,0,0,0,,"
            f"{{\\an8\\pos(540,225)\\c{ass_color(color)}\\fad(80,80)}}{text}"
        )

    cta = starts["story_cta"]
    controls = (
        (0.00, 1.14, "LIKE • BACK THE BET", GREEN),
        (1.14, 2.02, "SUBSCRIBE • LEARN THE MOVE", BLUE),
        (2.02, 5.68, "COMMENT • DUMB OR SMART?", YELLOW),
    )
    for start, end, text, color in controls:
        lines.append(
            f"Dialogue: 9,{ass_time(cta + start)},{ass_time(cta + end)},CTA,,0,0,0,,"
            f"{{\\an8\\pos(540,410)\\c{ass_color(color)}\\fad(80,80)}}{text}"
        )

    lines.append(
        f"Dialogue: 9,{ass_time(starts['proof_bridge'])},{ass_time(ends['story_cta'])},Small,,0,0,0,,"
        "{\\an3\\pos(1035,1870)}ILLUSTRATION • PEXELS 7981954"
    )

    thirds = [0.0, total_duration / 3, 2 * total_duration / 3, total_duration]
    positions = [(44, 70), (770, 70), (44, 1840)]
    for index, (start, end) in enumerate(zip(thirds[:-1], thirds[1:])):
        x, y = positions[index]
        lines.append(
            f"Dialogue: 10,{ass_time(start)},{ass_time(end)},Small,,0,0,0,,"
            f"{{\\an7\\pos({x},{y})}}HARD KNOCKS LAB"
        )

    output = WORK / "captions_and_overlays.ass"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def generate_music(duration: float) -> Path:
    output = AUDIO_DIR / "ambient_bed.wav"
    run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "lavfi", "-i", f"sine=frequency=82:sample_rate=48000:duration={duration:.3f}",
        "-f", "lavfi", "-i", f"sine=frequency=123:sample_rate=48000:duration={duration:.3f}",
        "-filter_complex",
        f"[0:a]volume=0.014,afade=t=in:st=0:d=1,afade=t=out:st={duration - 1:.3f}:d=1[a0];"
        f"[1:a]volume=0.007,afade=t=in:st=0:d=1,afade=t=out:st={duration - 1:.3f}:d=1[a1];"
        "[a0][a1]amix=inputs=2:duration=longest:normalize=0,"
        "aformat=sample_fmts=s16:sample_rates=48000:channel_layouts=stereo[aout]",
        "-map", "[aout]", "-c:a", "pcm_s16le", output,
    ])
    return output


def generate_sfx() -> dict[str, Path]:
    cash = AUDIO_DIR / "cash_chime.wav"
    whoosh = AUDIO_DIR / "whoosh.wav"
    run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "lavfi", "-i", "sine=frequency=880:sample_rate=48000:duration=0.34",
        "-f", "lavfi", "-i", "sine=frequency=1320:sample_rate=48000:duration=0.28",
        "-filter_complex", "[0:a]volume=0.22[a0];[1:a]volume=0.14,adelay=70|70[a1];[a0][a1]amix=inputs=2:normalize=0,afade=t=out:st=0.18:d=0.16,aformat=channel_layouts=stereo[out]",
        "-map", "[out]", "-c:a", "pcm_s16le", cash,
    ])
    run([
        "ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
        "anoisesrc=color=pink:sample_rate=48000:duration=0.40:amplitude=0.18",
        "-af", "highpass=f=450,lowpass=f=5000,afade=t=in:st=0:d=0.08,afade=t=out:st=0.16:d=0.24,aformat=channel_layouts=stereo",
        "-c:a", "pcm_s16le", whoosh,
    ])
    return {"cash": cash, "whoosh": whoosh}


def make_positioned_track(
    source: Path, start: float, total_duration: float, output: Path, source_filter: str
) -> Path:
    if start <= 0:
        run([
            "ffmpeg", "-y", "-v", "error", "-i", source,
            "-filter_complex",
            f"[0:a]aresample=48000,aformat=channel_layouts=stereo,{source_filter},"
            f"apad,atrim=0:{total_duration:.6f}[out]",
            "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", output,
        ])
    else:
        run([
            "ffmpeg", "-y", "-v", "error",
            "-f", "lavfi", "-t", f"{start:.6f}", "-i", "anullsrc=r=48000:cl=stereo",
            "-i", source,
            "-filter_complex",
            f"[1:a]aresample=48000,aformat=channel_layouts=stereo,{source_filter}[clip];"
            f"[0:a][clip]concat=n=2:v=0:a=1,apad,atrim=0:{total_duration:.6f}[out]",
            "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", output,
        ])
    return output


def build_timed_audio(total_duration: float, starts: dict[str, float]) -> Path:
    generated = generate_sfx()
    definitions = (
        ("hook", BUZZ, 0.06, "volume=0.22"),
        ("failing", BUZZ, starts["failing_question"] + 1.95, "volume=0.18"),
        ("story", TING, starts["storylines"] + 0.04, "volume=0.22"),
        ("rules", generated["whoosh"], starts["break_rules"] - 0.14, "volume=0.34"),
        ("boxing", BUZZ, starts["boxing_doubt"] + 0.08, "volume=0.18"),
        ("proof_prelap", generated["cash"], starts["proof_bridge"] - 0.20, "volume=0.38"),
        ("collapse", generated["whoosh"], starts["collapse_question"] - 0.12, "volume=0.28"),
        ("cta_like", TING, starts["story_cta"] + 0.02, "volume=0.16"),
        ("cta_sub", TING, starts["story_cta"] + 1.14, "volume=0.14"),
        ("cta_comment", generated["whoosh"], starts["story_cta"] + 2.02, "volume=0.24"),
        ("payoff_prelap", generated["cash"], starts["paramount_payoff"] - 0.20, "volume=0.48"),
        ("payoff", TING, starts["paramount_payoff"] + 1.90, "volume=0.24"),
        ("loop", generated["whoosh"], starts["loop_prep"] + 0.02, "volume=0.34"),
    )
    tracks: list[Path] = []
    for name, source, start, source_filter in definitions:
        tracks.append(
            make_positioned_track(
                source, max(0.0, start), total_duration,
                AUDIO_DIR / f"positioned_{name}.wav", source_filter,
            )
        )
    output = AUDIO_DIR / "timed_overlays.wav"
    inputs: list[str] = []
    for track in tracks:
        inputs.extend(["-i", str(track)])
    labels = "".join(f"[{index}:a]" for index in range(len(tracks)))
    run([
        "ffmpeg", "-y", "-v", "error", *inputs,
        "-filter_complex",
        f"{labels}amix=inputs={len(tracks)}:duration=longest:normalize=0,atrim=0:{total_duration:.6f}[out]",
        "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", output,
    ])
    return output


def overlay_prepare(index: int, width: int, height: int, start: float, end: float) -> str:
    return (
        f"[{index}:v]scale={width}:{height}:flags=lanczos,format=rgba,"
        f"fade=t=in:st={start:.3f}:d=0.16:alpha=1,"
        f"fade=t=out:st={max(start, end - 0.18):.3f}:d=0.18:alpha=1"
    )


def final_composite(
    base: Path,
    timeline: list[dict[str, Any]],
    total_frames: int,
    cards: list[Path],
    ass_file: Path,
    music: Path,
) -> None:
    starts = {item["name"]: item["final_start"] for item in timeline}
    ends = {item["name"]: item["final_end"] for item in timeline}
    total_duration = total_frames / FPS
    timed_audio = build_timed_audio(total_duration, starts)
    ass_escaped = str(ass_file).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")

    windows = (
        (0.08, ends["hook_dumbest"] - 0.05),
        (starts["storylines"], ends["boxing_doubt"] - 0.05),
        (starts["proof_bridge"], ends["proof_bridge"] - 0.05),
        (starts["paramount_payoff"], ends["prove_again"] - 0.10),
    )
    graph: list[str] = []
    for offset, (start, end) in enumerate(windows, start=1):
        graph.append(overlay_prepare(offset, 370, 317, start, end) + f"[c{offset - 1}]")
    graph.extend([
        f"[0:v][c0]overlay=x=40:y=330:eof_action=pass:enable='between(t,{windows[0][0]:.3f},{windows[0][1]:.3f})'[v1]",
        f"[v1][c1]overlay=x=40:y=330:eof_action=pass:enable='between(t,{windows[1][0]:.3f},{windows[1][1]:.3f})'[v2]",
        f"[v2][c2]overlay=x=650:y=300:eof_action=pass:enable='between(t,{windows[2][0]:.3f},{windows[2][1]:.3f})'[v3]",
        f"[v3][c3]overlay=x=40:y=330:eof_action=pass:enable='between(t,{windows[3][0]:.3f},{windows[3][1]:.3f})'[v4]",
        f"[v4]subtitles='{ass_escaped}':fontsdir='{FONT_KOMIKA.parent}',format=yuv420p[vout]",
        "[0:a]aresample=48000,aformat=channel_layouts=stereo[basea]",
        "[5:a]aresample=48000,aformat=channel_layouts=stereo[timed]",
        f"[6:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"volume='if(between(t,{starts['collapse_question']:.3f},{ends['story_cta']:.3f}),0.035,0.13)':eval=frame[music]",
        f"[basea][timed][music]amix=inputs=3:duration=longest:normalize=0,atrim=0:{total_duration:.6f},"
        "loudnorm=I=-16.5:TP=-1.5:LRA=10,volume=-0.7dB,alimiter=limit=0.84:level=false[aout]",
    ])
    script = WORK / "final.ffscript"
    script.write_text(";\n".join(graph) + "\n", encoding="utf-8")

    FINAL.parent.mkdir(parents=True, exist_ok=True)
    png_duration = total_duration + 1.0
    inputs: list[str | Path] = ["-i", base]
    for path in cards:
        inputs.extend(["-loop", "1", "-t", f"{png_duration:.3f}", "-i", path])
    inputs.extend(["-i", timed_audio, "-i", music])
    run([
        "ffmpeg", "-y", "-v", "error", *inputs,
        "-filter_complex_script", script, "-map", "[vout]", "-map", "[aout]",
        "-frames:v", str(total_frames), *encode_args(),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart", "-t", f"{total_duration:.6f}", FINAL,
    ])


def validate_final(timeline: list[dict[str, Any]]) -> dict[str, Any]:
    data = probe(FINAL)
    video = next(stream for stream in data["streams"] if stream["codec_type"] == "video")
    audio = next(stream for stream in data["streams"] if stream["codec_type"] == "audio")
    duration = float(data["format"]["duration"])
    source_segments = [item for item in timeline if item["kind"] != "narration"]
    total_source = sum(item["source_duration"] for item in source_segments)
    cta_start = next(item["final_start"] for item in timeline if item["name"] == "story_cta")
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
        "triple_source_mix": SOURCE.exists() and PEXELS_CONTRACT.exists() and len(list(PANELS.glob("*.png"))) >= 4,
        "commentary_track": PROOF_AUDIO.exists() and CTA_AUDIO.exists(),
        "cta_window": 38.0 <= cta_start <= 42.0,
        "caption_at_frame_zero": CAPTIONS["hook_dumbest"][0][0] <= 0.2,
    }
    if not all(checks.values()):
        raise RuntimeError(f"Final validation failed: {checks}")
    report = {
        "final": str(FINAL),
        "duration": duration,
        "checks": checks,
        "cta_start": cta_start,
        "total_source_duration": total_source,
        "source_duration": SOURCE_DURATION,
        "source_use_percent": 100 * total_source / SOURCE_DURATION,
        "timeline": timeline,
    }
    (WORK / "timeline.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def require_inputs() -> None:
    required = (
        SOURCE, PEXELS_CONTRACT, PROOF_AUDIO, CTA_AUDIO, TING, BUZZ,
        FONT_KOMIKA, FONT_BOLD, FONT_BLACK,
    )
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required inputs:\n" + "\n".join(missing))
    for segment in SEGMENTS:
        if segment.kind != "narration" and segment.duration >= 15.0:
            raise ValueError(f"Every source segment must be below 15 seconds: {segment.name}")
        if segment.kind == "narration" and segment.audio is None:
            raise ValueError(f"Narration audio missing: {segment.name}")


def main() -> None:
    require_inputs()
    for directory in (WORK, SEGMENT_DIR, PANELS, CHECKS, AUDIO_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    base, timeline, total_frames = build_base()
    total_duration = total_frames / FPS
    cards = make_cards()
    ass_file = write_ass(timeline, total_duration)
    music = generate_music(total_duration)
    final_composite(base, timeline, total_frames, cards, ass_file, music)
    report = validate_final(timeline)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
