#!/usr/bin/env python3
"""Render HardKnocks V18: LinkedIn's Contrarian Test.

A source-native Reid Hoffman story about interrogating credible criticism,
spotting the hidden network thesis, taking survivable asymmetric risk, and
ending on the independently verified Microsoft acquisition payoff.

This is a one-off media renderer. Completion is verified against the exact MP4,
not renderer unit tests.
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
SOURCE = PROJECT / "source" / "q8u9vs2xjg4.mp4"
WORK = PROJECT / "clips" / "v18_linkedin_work"
SEGMENT_DIR = WORK / "segments"
PANELS = WORK / "panels"
CHECKS = WORK / "checks"
AUDIO_DIR = WORK / "audio"
FINAL = PROJECT / "final" / "2026-07-28-hardknocks_v18_linkedin_contrarian_test.mp4"

PEXELS_NETWORKING = ROOT / "output" / "shared" / "pexels" / "professional_networking_8716999.mp4"
BRIDGE_AUDIO = AUDIO_DIR / "bridge.wav"
CTA_AUDIO = AUDIO_DIR / "cta.wav"
BRANDING = ROOT / "output" / "shared" / "hardknocks_branding"
TING = BRANDING / "verdict_correct_ting.wav"

FONT_KOMIKA = ROOT / "assets" / "fonts" / "komika-axis" / "KOMIKAX_.ttf"
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
FONT_BLACK = Path("/System/Library/Fonts/Supplemental/Arial Black.ttf")

WIDTH = 1080
HEIGHT = 1920
FPS = 30
CAPTION_BAND_PX = 270
SEGMENT_FADE_IN = 0.12
SEGMENT_FADE_OUT = 0.20
SOURCE_DURATION = 971.521

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


# The source is a stable outdoor two-shot: Reid is frame-left (~32%) and the
# host is frame-right (~70%). Reframes remain on the active speaker; the hook
# varies crop every ~1s so the protected first five seconds have real motion.
SEGMENTS = (
    Segment(
        "hook_consensus", "source", 202.80, 206.68,
        ((0.0, 0.30), (0.95, 0.35), (1.95, 0.30), (2.95, 0.35)), 1.09, "hook",
    ),
    Segment(
        "test_failure", "source", 209.40, 212.38,
        ((0.0, 0.30), (1.15, 0.35), (2.20, 0.30)), 1.07, "test",
    ),
    Segment(
        "test_inversion", "source", 212.52, 215.98,
        ((0.0, 0.35), (1.15, 0.30), (2.30, 0.35)), 1.06, "test",
    ),
    Segment(
        "chance_amazing", "source", 216.08, 220.42,
        ((0.0, 0.30), (1.35, 0.35), (2.70, 0.30), (3.80, 0.35)), 1.05, "stake",
    ),
    Segment(
        "host_asks", "source", 220.54, 221.98,
        ((0.0, 0.68), (0.72, 0.73)), 1.07, "transition",
    ),
    Segment(
        "network_objection", "source", 222.08, 229.38,
        ((0.0, 0.30), (1.25, 0.35), (2.50, 0.30), (3.75, 0.35),
         (5.00, 0.30), (6.20, 0.35)), 1.05, "objection",
    ),
    Segment(
        "hidden_thesis", "source", 229.50, 234.90,
        ((0.0, 0.30), (1.35, 0.35), (2.70, 0.30), (4.05, 0.35)), 1.06, "thesis",
    ),
    Segment(
        "asymmetric_risk", "source", 142.30, 149.14,
        ((0.0, 0.30), (1.35, 0.35), (2.70, 0.30),
         (4.05, 0.35), (5.40, 0.30)), 1.06, "rule",
    ),
    Segment(
        "editorial_bridge", "narration", 0.00, 3.92,
        (), 1.00, "commentary", BRIDGE_AUDIO, 1.20,
    ),
    Segment(
        "story_cta", "narration", 0.00, 4.00,
        (), 1.00, "cta", CTA_AUDIO, 8.40,
    ),
    Segment(
        "survive_failure", "source", 149.38, 157.82,
        ((0.0, 0.70), (0.95, 0.30), (2.30, 0.35), (3.65, 0.30),
         (5.00, 0.35), (6.35, 0.30), (7.55, 0.35)), 1.06, "guardrail",
    ),
    Segment(
        "sale", "source", 276.36, 280.94,
        ((0.0, 0.70), (1.62, 0.30), (3.54, 0.70), (4.08, 0.30)), 1.08, "payoff",
    ),
    Segment(
        "acquisition", "source", 285.90, 290.84,
        ((0.0, 0.30), (1.25, 0.35), (2.50, 0.30), (3.75, 0.35)), 1.06, "proof",
    ),
    Segment(
        "worth_it", "source", 291.08, 297.56,
        ((0.0, 0.30), (1.35, 0.35), (3.92, 0.70), (4.84, 0.30), (5.70, 0.35)), 1.07, "verdict",
    ),
)


CAPTIONS: dict[str, tuple[tuple[float, float, str, str], ...]] = {
    "hook_consensus": (
        (0.00, 1.02, "MORE THAN TWO-THIRDS", "TWO-THIRDS"),
        (1.02, 2.02, "OF MY SMART FRIENDS", "SMART"),
        (2.02, 3.10, "THOUGHT I WOULD BE", "WOULD"),
        (3.10, 3.88, "A LINKEDIN FAILURE", "FAILURE"),
    ),
    "test_failure": (
        (0.00, 1.12, "WHAT IS WRONG", "WRONG"),
        (1.12, 2.18, "WITH MY IDEA?", "IDEA"),
        (2.18, 2.98, "WHY WILL IT FAIL?", "FAIL"),
    ),
    "test_inversion": (
        (0.00, 1.16, "GIVE THEM PERMISSION", "PERMISSION"),
        (1.16, 1.94, "TO DO THAT", "DO"),
        (1.94, 2.76, "WHAT DO I KNOW", "KNOW"),
        (2.76, 3.46, "THEY DO NOT?", "NOT"),
    ),
    "chance_amazing": (
        (0.00, 1.14, "IF YOU HAVE", "HAVE"),
        (1.14, 2.16, "A GOOD THEORY", "GOOD"),
        (2.16, 3.24, "YOU MIGHT HAVE", "MIGHT"),
        (3.24, 4.34, "SOMETHING AMAZING", "AMAZING"),
    ),
    "host_asks": (
        (0.00, 0.78, "WHAT DID YOU KNOW", "YOU"),
        (0.78, 1.44, "THEY DID NOT?", "NOT"),
    ),
    "network_objection": (
        (0.00, 1.20, "A NETWORK PROPERTY", "NETWORK"),
        (1.20, 2.30, "FIRST PERSON: NO VALUE", "NO VALUE"),
        (2.30, 3.44, "WE KNOW EACH OTHER", "KNOW"),
        (3.44, 4.36, "STILL NO VALUE", "NO VALUE"),
        (4.36, 5.62, "NO VALUE. NO VALUE.", "NO VALUE"),
        (5.62, 7.30, "HOW DOES IT GROW?", "GROW"),
    ),
    "hidden_thesis": (
        (0.00, 1.10, "I KNEW I COULD", "KNEW"),
        (1.10, 2.22, "GET IT TO GROW", "GROW"),
        (2.22, 3.40, "EVEN BEFORE PEOPLE", "BEFORE"),
        (3.40, 4.48, "HAD ANY VALUE", "VALUE"),
        (4.48, 5.40, "IN THE BEGINNING", "BEGINNING"),
    ),
    "asymmetric_risk": (
        (0.00, 1.14, "THE KEY TO RISK", "RISK"),
        (1.14, 2.34, "TAKE A RISK", "TAKE"),
        (2.34, 3.70, "OTHERS WILL NOT TAKE", "NOT"),
        (3.70, 4.86, "IT MIGHT FAIL", "FAIL"),
        (4.86, 5.80, "BUT IF YOU WIN", "WIN"),
        (5.80, 6.84, "YOU WIN HUGE", "HUGE"),
    ),
    "editorial_bridge": (
        (0.00, 1.18, "NOT BLIND CONFIDENCE", "NOT"),
        (1.18, 2.04, "IT WAS A", "WAS"),
        (2.04, 3.92, "SURVIVABLE BET", "SURVIVABLE"),
    ),
    "story_cta": (
        (0.00, 0.66, "LIKE", "LIKE"),
        (0.66, 1.50, "SUBSCRIBE", "SUBSCRIBE"),
        (1.50, 2.30, "AND COMMENT", "COMMENT"),
        (2.30, 3.24, "WHAT DO YOU KNOW", "KNOW"),
        (3.24, 4.00, "THEY DO NOT?", "NOT"),
    ),
    "survive_failure": (
        (0.00, 0.88, "NOT AFRAID OF FAILURE?", "FAILURE"),
        (0.88, 2.12, "EVERYONE FEARS FAILURE", "EVERYONE"),
        (2.12, 3.48, "I KNEW I COULD", "KNEW"),
        (3.48, 4.82, "SURVIVE FAILURE", "SURVIVE"),
        (4.82, 5.94, "I COULD PLAY AGAIN", "AGAIN"),
        (5.94, 7.20, "THE KEY IS", "KEY"),
        (7.20, 8.44, "YOU CAN PLAY AGAIN", "AGAIN"),
    ),
    "sale": (
        (0.00, 1.52, "WHAT DID LINKEDIN SELL FOR?", "SELL"),
        (1.52, 3.10, "$26 BILLION", "$26 BILLION"),
        (3.10, 3.82, "TO WHO?", "WHO"),
        (3.82, 4.58, "MICROSOFT", "MICROSOFT"),
    ),
    "acquisition": (
        (0.00, 1.16, "WHAT HAPPENED?", "HAPPENED"),
        (1.16, 2.40, "SATYA NADELLA", "NADELLA"),
        (2.40, 3.54, "AND BILL GATES", "GATES"),
        (3.54, 4.94, "CAME TO THE OFFICE", "OFFICE"),
    ),
    "worth_it": (
        (0.00, 1.72, "OKAY. LET US TALK.", "TALK"),
        (1.72, 3.78, "ONE OF THEIR BEST", "BEST"),
        (3.78, 4.76, "ACQUISITIONS EVER", "EVER"),
        (4.76, 5.50, "WORTH IT?", "WORTH"),
        (5.50, 6.48, "WORTH IT FOR BOTH", "BOTH"),
    ),
}


def run(args: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(str(a) for a in args), flush=True)
    return subprocess.run(
        [str(a) for a in args], cwd=ROOT, check=True, text=True,
        capture_output=capture,
    )


def probe(path: Path) -> dict[str, Any]:
    result = run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
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
    audio_filter = (
        f"atrim=start={fine_offset:.6f},asetpts=PTS-STARTPTS,highpass=f=70,"
        "acompressor=threshold=0.125:ratio=2:attack=5:release=80:makeup=1.4,"
        "loudnorm=I=-16:TP=-1.5:LRA=10,aresample=48000:first_pts=0,apad,"
        f"atrim=0:{segment.duration:.6f},"
        f"afade=t=in:st=0:d={SEGMENT_FADE_IN:.2f},"
        f"afade=t=out:st={segment.duration - SEGMENT_FADE_OUT:.6f}:d={SEGMENT_FADE_OUT:.2f}"
    )
    run([
        "ffmpeg", "-y", "-v", "error", "-ss", f"{coarse_start:.6f}",
        "-i", str(SOURCE), "-t", f"{segment.duration:.6f}",
        "-vf", f"trim=start={fine_offset:.6f},setpts=PTS-STARTPTS,{source_crop(segment)},fps={FPS}",
        "-af", audio_filter, "-frames:v", str(frame_count), *encode_args(),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(output),
    ])
    return frame_count


def render_narration_segment(segment: Segment, output: Path) -> int:
    if segment.audio is None:
        raise ValueError(f"Narration segment has no audio: {segment.name}")
    frame_count = frames_for(segment.duration)
    crop = (
        "scale=1166:2074:flags=lanczos,"
        "crop=1080:1920:"
        "x='(in_w-out_w)/2+18*sin(t*0.9)':"
        "y='(in_h-out_h)/2+24*sin(t*0.7)',"
        "eq=contrast=1.04:saturation=0.90,setsar=1,format=yuv420p,fps=30"
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
        "-ss", f"{segment.visual_start:.3f}", "-i", str(PEXELS_NETWORKING),
        "-i", str(segment.audio), "-vf", crop, "-af", audio_filter,
        "-frames:v", str(frame_count), *encode_args(),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(output),
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
            render_source_segment(segment, output)
            if segment.kind == "source"
            else render_narration_segment(segment, output)
        )
        timeline.append({
            "name": segment.name,
            "kind": segment.kind,
            "act": segment.act,
            "source_start": segment.start if segment.kind == "source" else None,
            "source_end": segment.end if segment.kind == "source" else None,
            "source_duration": segment.duration if segment.kind == "source" else 0.0,
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
        "-i", str(concat), "-c", "copy", str(base),
    ])
    return base, timeline, cursor


def make_network_panels() -> list[Path]:
    PANELS.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    nodes = [(70, 100), (210, 72), (338, 128), (98, 276), (236, 244), (350, 330)]
    edges = [(0, 1), (1, 2), (0, 3), (1, 4), (2, 5), (3, 4), (4, 5), (1, 3)]
    states = (0, 3, len(edges))
    for state, edge_count in enumerate(states):
        panel = Image.new("RGBA", (420, 470), (11, 14, 20, 232))
        draw = ImageDraw.Draw(panel)
        draw.rounded_rectangle((1, 1, 418, 468), radius=28, fill=(11, 14, 20, 232), outline=(255, 255, 255, 90), width=3)
        eyebrow = ImageFont.truetype(str(FONT_BOLD), 22)
        headline = ImageFont.truetype(str(FONT_BLACK), 32)
        label = ImageFont.truetype(str(FONT_BOLD), 20)
        draw.text((210, 34), "NETWORK EFFECT", font=eyebrow, fill=BLUE, anchor="mm")
        draw.text((210, 72), ["NO VALUE", "EARLY LINKS", "THE NETWORK GROWS"][state], font=headline, fill=[RED, YELLOW, GREEN][state], anchor="mm")
        for a, b in edges[:edge_count]:
            draw.line((nodes[a], nodes[b]), fill=(79, 195, 247, 220), width=7)
        for index, (x, y) in enumerate(nodes):
            connected = state == 2 or (state == 1 and index < 4)
            color = (0, 214, 110, 255) if connected else (154, 163, 178, 255)
            draw.ellipse((x - 19, y - 19, x + 19, y + 19), fill=color, outline="white", width=3)
        draw.text((210, 423), f"STATE {state + 1}/3", font=label, fill=(190, 198, 212), anchor="mm")
        output = PANELS / f"network_state_{state}.png"
        panel.save(output)
        outputs.append(output)
    return outputs


def make_proof_card() -> Path:
    PANELS.mkdir(parents=True, exist_ok=True)
    card = Image.new("RGBA", (500, 360), (11, 14, 20, 242))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle((1, 1, 498, 358), radius=30, fill=(11, 14, 20, 242), outline=(255, 255, 255, 105), width=3)
    eyebrow = ImageFont.truetype(str(FONT_BOLD), 24)
    value = ImageFont.truetype(str(FONT_BLACK), 76)
    detail = ImageFont.truetype(str(FONT_BOLD), 27)
    small = ImageFont.truetype(str(FONT_BOLD), 18)
    draw.text((250, 38), "OFFICIAL ANNOUNCEMENT", font=eyebrow, fill=BLUE, anchor="mm")
    draw.text((250, 120), "$26.2B", font=value, fill=GREEN, anchor="mm")
    draw.text((250, 184), "ALL-CASH TRANSACTION", font=detail, fill="white", anchor="mm")
    draw.text((250, 232), "MICROSOFT → LINKEDIN", font=detail, fill=YELLOW, anchor="mm")
    draw.text((250, 286), "MICROSOFT NEWS CENTER", font=small, fill=(190, 198, 212), anchor="mm")
    draw.text((250, 317), "JUNE 13, 2016", font=small, fill=(190, 198, 212), anchor="mm")
    output = PANELS / "microsoft_26_2b_proof.png"
    card.save(output)
    return output


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
            y = 1255 if segment_name in {"editorial_bridge", "story_cta"} else 1160
            body = f"{{\\an5\\pos(540,{y})}}{emphasized(text, keyword)}"
            lines.append(
                f"Dialogue: 8,{ass_time(base + rel_start)},{ass_time(base + rel_end)},Caption,,0,0,0,,{body}"
            )

    states = (
        (0.0, starts["test_failure"], "CONSENSUS: FAIL", RED),
        (starts["test_failure"], starts["network_objection"], "TEST THE FAILURE", YELLOW),
        (starts["network_objection"], starts["asymmetric_risk"], "HIDDEN NETWORK THESIS", BLUE),
        (starts["asymmetric_risk"], starts["editorial_bridge"], "ASYMMETRIC RISK", YELLOW),
        (starts["editorial_bridge"], starts["sale"], "SURVIVABLE BET", GREEN),
        (starts["sale"], total_duration, "PAYOFF: $26.2B", GREEN),
    )
    for start, end, text, color in states:
        lines.append(
            f"Dialogue: 6,{ass_time(start)},{ass_time(end)},State,,0,0,0,,"
            f"{{\\an8\\pos(540,245)\\c{ass_color(color)}\\fad(80,80)}}{text}"
        )

    cta = starts["story_cta"]
    cta_controls = (
        (0.00, 0.82, "LIKE • TEST THE IDEA", GREEN),
        (0.82, 1.72, "SUBSCRIBE • BUILD BETTER", BLUE),
        (1.72, 4.00, "COMMENT • WHAT DO YOU KNOW?", YELLOW),
    )
    for start, end, text, color in cta_controls:
        lines.append(
            f"Dialogue: 9,{ass_time(cta + start)},{ass_time(cta + end)},CTA,,0,0,0,,"
            f"{{\\an8\\pos(540,405)\\c{ass_color(color)}\\fad(80,80)}}{text}"
        )

    lines.append(
        f"Dialogue: 9,{ass_time(starts['editorial_bridge'])},{ass_time(ends['story_cta'])},Small,,0,0,0,,"
        "{\\an3\\pos(1035,1870)}ILLUSTRATION • PEXELS 8716999"
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
        f"[0:a]volume=0.015,afade=t=in:st=0:d=1,afade=t=out:st={duration - 1:.3f}:d=1[a0];"
        f"[1:a]volume=0.008,afade=t=in:st=0:d=1,afade=t=out:st={duration - 1:.3f}:d=1[a1];"
        "[a0][a1]amix=inputs=2:duration=longest:normalize=0,"
        "aformat=sample_fmts=s16:sample_rates=48000:channel_layouts=stereo[aout]",
        "-map", "[aout]", "-c:a", "pcm_s16le", str(output),
    ])
    return output


def make_positioned_track(source: Path, start: float, total_duration: float, output: Path, source_filter: str) -> Path:
    if start <= 0:
        run([
            "ffmpeg", "-y", "-v", "error", "-i", str(source),
            "-filter_complex",
            f"[0:a]aresample=48000,aformat=channel_layouts=stereo,{source_filter},"
            f"apad,atrim=0:{total_duration:.6f}[out]",
            "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", str(output),
        ])
    else:
        run([
            "ffmpeg", "-y", "-v", "error",
            "-f", "lavfi", "-t", f"{start:.6f}", "-i", "anullsrc=r=48000:cl=stereo",
            "-i", str(source),
            "-filter_complex",
            f"[1:a]aresample=48000,aformat=channel_layouts=stereo,{source_filter}[clip];"
            f"[0:a][clip]concat=n=2:v=0:a=1,apad,atrim=0:{total_duration:.6f}[out]",
            "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", str(output),
        ])
    return output


def build_timed_audio(total_duration: float, starts: dict[str, float]) -> Path:
    definitions = (
        ("hook", TING, 0.08, "volume=0.42"),
        ("network_0", TING, starts["network_objection"] + 0.05, "volume=0.24"),
        ("network_1", TING, starts["network_objection"] + 2.30, "volume=0.22"),
        ("network_2", TING, starts["network_objection"] + 4.80, "volume=0.28"),
        ("risk", TING, starts["asymmetric_risk"] + 4.86, "volume=0.26"),
        ("cta_like", TING, starts["story_cta"] + 0.02, "volume=0.20"),
        ("cta_sub", TING, starts["story_cta"] + 0.84, "volume=0.18"),
        ("cta_comment", TING, starts["story_cta"] + 1.74, "volume=0.18"),
        ("proof", TING, starts["sale"] + 0.04, "volume=0.38"),
    )
    tracks: list[Path] = []
    for name, source, start, source_filter in definitions:
        tracks.append(make_positioned_track(source, start, total_duration, AUDIO_DIR / f"positioned_{name}.wav", source_filter))
    output = AUDIO_DIR / "timed_overlays.wav"
    inputs: list[str] = []
    for track in tracks:
        inputs.extend(["-i", str(track)])
    labels = "".join(f"[{index}:a]" for index in range(len(tracks)))
    run([
        "ffmpeg", "-y", "-v", "error", *inputs,
        "-filter_complex",
        f"{labels}amix=inputs={len(tracks)}:duration=longest:normalize=0,atrim=0:{total_duration:.6f}[out]",
        "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", str(output),
    ])
    return output


def final_composite(base: Path, timeline: list[dict[str, Any]], total_frames: int, network_panels: list[Path], proof_card: Path, ass_file: Path, music: Path) -> None:
    starts = {item["name"]: item["final_start"] for item in timeline}
    ends = {item["name"]: item["final_end"] for item in timeline}
    total_duration = total_frames / FPS
    network_start = starts["network_objection"]
    network_end = ends["network_objection"]
    proof_start = starts["sale"]
    proof_end = starts["acquisition"] + 2.35
    timed_audio = build_timed_audio(total_duration, starts)
    ass_escaped = str(ass_file).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")

    filter_graph = (
        "[1:v]scale=390:436:flags=lanczos,format=rgba[n0];"
        "[2:v]scale=390:436:flags=lanczos,format=rgba[n1];"
        "[3:v]scale=390:436:flags=lanczos,format=rgba[n2];"
        f"[0:v][n0]overlay=x=660:y=340:eof_action=pass:enable='between(t,{network_start:.3f},{network_start + 2.30:.3f})'[v1];"
        f"[v1][n1]overlay=x=660:y=340:eof_action=pass:enable='between(t,{network_start + 2.30:.3f},{network_start + 4.80:.3f})'[v2];"
        f"[v2][n2]overlay=x=660:y=340:eof_action=pass:enable='between(t,{network_start + 4.80:.3f},{network_end:.3f})'[v3];"
        f"[4:v]scale=430:310:flags=lanczos,format=rgba,fade=t=in:st={proof_start:.3f}:d=0.16:alpha=1,"
        f"fade=t=out:st={proof_end - 0.18:.3f}:d=0.18:alpha=1[proof];"
        f"[v3][proof]overlay=x=625:y=330:eof_action=pass:enable='between(t,{proof_start:.3f},{proof_end:.3f})'[v4];"
        f"[v4]subtitles='{ass_escaped}':fontsdir='{FONT_KOMIKA.parent}',format=yuv420p[vout];"
        "[0:a]aresample=48000,aformat=channel_layouts=stereo[basea];"
        "[5:a]aresample=48000,aformat=channel_layouts=stereo[timed];"
        "[6:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.13[music];"
        f"[basea][timed][music]amix=inputs=3:duration=longest:normalize=0,atrim=0:{total_duration:.6f},"
        "loudnorm=I=-16.5:TP=-1.5:LRA=10,volume=-0.7dB,alimiter=limit=0.84:level=false[aout]"
    )
    script = WORK / "final.ffscript"
    script.write_text(filter_graph + "\n", encoding="utf-8")
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    png_duration = total_duration + 1.0
    run([
        "ffmpeg", "-y", "-v", "error", "-i", str(base),
        "-loop", "1", "-t", f"{png_duration:.3f}", "-i", str(network_panels[0]),
        "-loop", "1", "-t", f"{png_duration:.3f}", "-i", str(network_panels[1]),
        "-loop", "1", "-t", f"{png_duration:.3f}", "-i", str(network_panels[2]),
        "-loop", "1", "-t", f"{png_duration:.3f}", "-i", str(proof_card),
        "-i", str(timed_audio), "-i", str(music),
        "-filter_complex_script", str(script), "-map", "[vout]", "-map", "[aout]",
        "-frames:v", str(total_frames), *encode_args(),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart", "-t", f"{total_duration:.6f}", str(FINAL),
    ])


def validate_final(timeline: list[dict[str, Any]]) -> dict[str, Any]:
    data = probe(FINAL)
    video = next(stream for stream in data["streams"] if stream["codec_type"] == "video")
    audio = next(stream for stream in data["streams"] if stream["codec_type"] == "audio")
    duration = float(data["format"]["duration"])
    source_segments = [item for item in timeline if item["kind"] == "source"]
    total_source = sum(item["source_duration"] for item in source_segments)
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
        "triple_source_mix": SOURCE.exists() and PEXELS_NETWORKING.exists() and len(network_panels := list(PANELS.glob("network_state_*.png"))) == 3,
    }
    if not all(checks.values()):
        raise RuntimeError(f"Final validation failed: {checks}")
    report = {
        "final": str(FINAL),
        "duration": duration,
        "checks": checks,
        "total_source_duration": total_source,
        "source_duration": SOURCE_DURATION,
        "source_use_percent": 100 * total_source / SOURCE_DURATION,
        "timeline": timeline,
    }
    (WORK / "timeline.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def require_inputs() -> None:
    required = (SOURCE, PEXELS_NETWORKING, BRIDGE_AUDIO, CTA_AUDIO, TING, FONT_KOMIKA, FONT_BOLD, FONT_BLACK)
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required inputs:\n" + "\n".join(missing))
    for segment in SEGMENTS:
        if segment.kind == "source" and segment.duration >= 15.0:
            raise ValueError(f"Every source segment must be strictly below 15 seconds: {segment.name}")
        if segment.kind == "narration" and segment.audio is None:
            raise ValueError(f"Narration audio missing in segment definition: {segment.name}")


def main() -> None:
    require_inputs()
    for directory in (WORK, SEGMENT_DIR, PANELS, CHECKS, AUDIO_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    base, timeline, total_frames = build_base()
    total_duration = total_frames / FPS
    network_panels = make_network_panels()
    proof_card = make_proof_card()
    ass_file = write_ass(timeline, total_duration)
    music = generate_music(total_duration)
    final_composite(base, timeline, total_frames, network_panels, proof_card, ass_file, music)
    report = validate_final(timeline)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
