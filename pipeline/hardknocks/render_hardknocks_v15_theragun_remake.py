#!/usr/bin/env python3
"""Render two clarity-first Theragun Shorts from the Ed Mylett/Jason Wersland interview.

V15A tells the chronological crash-to-first-Theragun origin story.
V15B follows one clinic patient through the athlete product-market signal.
Both preserve original interview audio, active-speaker reframing, word-timed
captions, post-render proof compositing, and protected 0-10s face visibility.
"""

from __future__ import annotations

import argparse
import json
import math
import struct
import subprocess
import wave
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any



ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "hardknocks"
SOURCE = PROJECT / "source" / "xv8qaYubDw4.mp4"
RESEARCH = PROJECT / "clips" / "v14_theragun_work" / "research"
TRANSCRIPT = RESEARCH / "transcript.json"
PEXELS_MASSAGE = ROOT / "output" / "shared" / "pexels" / "massage_gun_man_6390390.mp4"
PEXELS_SHOULDER = ROOT / "output" / "shared" / "pexels" / "shoulder_recovery_6095382.mp4"
PEXELS_DESIGN = ROOT / "output" / "shared" / "pexels" / "product_design_8003421.mp4"
PEXELS_TOOL = ROOT / "output" / "shared" / "pexels" / "power_tool_workshop_6790429.mp4"
FONT_REGULAR = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
FONT_BLACK = Path("/System/Library/Fonts/Supplemental/Arial Black.ttf")
FONT_KOMIKA = ROOT / "assets" / "fonts" / "Komika-Axis.ttf"

WIDTH = 1080
HEIGHT = 1920
FPS = 30
POST_SPEED = 1.06
SOURCE_DURATION = 4401.667
CAPTION_BAND_PX = 250
SEGMENT_FADE_IN = 0.10
SEGMENT_FADE_OUT = 0.18
YELLOW = "#FFD447"
GREEN = "#45E58D"
RED = "#FF5A68"
BLUE = "#54C8FF"


@dataclass(frozen=True)
class Segment:
    name: str
    source_start: float
    source_end: float
    focus: float = 0.68
    zoom: float = 1.08

    @property
    def duration(self) -> float:
        return self.source_end - self.source_start


@dataclass(frozen=True)
class Evidence:
    start: float
    duration: float
    asset: str
    pexels_id: str
    label: str


@dataclass(frozen=True)
class Variant:
    key: str
    version: str
    final_name: str
    hook_title: str
    hook_title_end: float
    hook_followup: str
    hook_followup_end: float
    segments: tuple[Segment, ...]
    evidence: tuple[Evidence, ...]
    accent: str
    value_badges: tuple[tuple[float, float, str, str], ...]
    cta_start: float
    cta_end: float


A_SEGMENTS = (
    Segment("inventor_identity", 1.86, 5.30, 0.24, 1.06),
    Segment("accident_question", 12.72, 15.80, 0.24, 1.06),
    Segment("crash_answer", 16.40, 22.78, 0.68, 1.08),
    Segment("perspective_question", 22.94, 24.64, 0.24, 1.08),
    Segment("mission_and_clinic", 25.52, 31.52, 0.68, 1.08),
    Segment("vibrating_table", 31.66, 44.78, 0.68, 1.08),
    Segment("first_theragun", 44.78, 51.40, 0.68, 1.10),
    Segment("problem_birthed_company", 52.28, 56.58, 0.50, 1.08),
    Segment("saved_my_life", 57.08, 57.94, 0.68, 1.10),
    Segment("product_not_company", 958.12, 968.00, 0.68, 1.08),
)

B_SEGMENTS = (
    Segment("jigsaw_to_clinic", 604.92, 613.82, 0.68, 1.08),
    Segment("patient_arrives", 622.58, 624.34, 0.68, 1.08),
    Segment("same_injuries", 628.80, 631.58, 0.68, 1.10),
    Segment("prototype_must_help", 645.54, 647.66, 0.68, 1.10),
    Segment("paper_bag_trial", 671.66, 682.10, 0.68, 1.08),
    Segment("patient_improved", 783.64, 787.48, 0.68, 1.08),
    Segment("saved_two_lives", 787.54, 800.60, 0.68, 1.10),
    Segment("one_per_day", 976.64, 982.42, 0.68, 1.08),
    Segment("market_bridge", 982.42, 986.72, 0.68, 1.08),
    Segment("empty_trunk", 987.10, 992.86, 0.68, 1.10),
    Segment("athlete_market", 993.26, 1001.62, 0.68, 1.10),
)

VARIANTS = {
    "a": Variant(
        key="a", version="v15a",
        final_name="2026-07-23-hardknocks_v15a_crash_created_theragun.mp4",
        hook_title="THE THERAGUN ORIGIN", hook_title_end=3.40,
        hook_followup="A CRASH STARTED IT", hook_followup_end=7.00,
        segments=A_SEGMENTS,
        evidence=(
            Evidence(14.00, 3.50, "shoulder", "6095382", "INJURY RECOVERY"),
            Evidence(25.00, 3.50, "shoulder", "6095382", "SHOULDER RELIEF"),
            Evidence(35.00, 3.50, "massage", "6390390", "PERCUSSIVE TOOL"),
            Evidence(46.00, 3.50, "design", "8003421", "PRODUCT DEVELOPMENT"),
        ),
        accent=YELLOW,
        value_badges=(
            (14.00, 20.50, "NOTHING IN HIS CLINIC COULD HELP", RED),
            (33.80, 40.50, "PAIN  >  PROTOTYPE", BLUE),
            (45.80, 55.20, "A PRODUCT, NOT A COMPANY", GREEN),
        ), cta_start=43.00, cta_end=46.40,
    ),
    "b": Variant(
        key="b", version="v15b",
        final_name="2026-07-23-hardknocks_v15b_first_patient_to_athletes.mp4",
        hook_title="THE FIRST THERAGUN", hook_title_end=3.20,
        hook_followup="WAS A JIGSAW", hook_followup_end=8.90,
        segments=B_SEGMENTS,
        evidence=(
            Evidence(12.00, 3.50, "shoulder", "6095382", "MATCHING INJURIES"),
            Evidence(34.00, 3.50, "massage", "6390390", "PATIENT PROOF"),
            Evidence(49.00, 3.50, "design", "8003421", "EARLY PRODUCT"),
            Evidence(59.00, 3.50, "massage", "6390390", "ATHLETE MARKET"),
        ),
        accent=BLUE,
        value_badges=(
            (10.60, 16.20, "THE PATIENT HAD THE SAME INJURIES", YELLOW),
            (26.70, 43.50, "ONE PATIENT BECAME THE PROOF", GREEN),
            (43.60, 53.60, "ONE SALE A DAY", YELLOW),
            (59.00, 69.30, "ATHLETES FOUND THE MARKET", GREEN),
        ), cta_start=44.00, cta_end=47.40,
    ),
}


def run(args: list[str | Path], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    printable = " ".join(str(arg) for arg in args)
    print("+", printable, flush=True)
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


def scaled_crop(segment: Segment) -> str:
    scaled_width = 3414
    span = scaled_width - WIDTH
    crop_x = round(span * segment.focus)
    zoom_width = round(WIDTH * segment.zoom)
    zoom_height = round(HEIGHT * segment.zoom)
    visible_height = HEIGHT - CAPTION_BAND_PX
    recovery_width = round(WIDTH * HEIGHT / visible_height)
    return (
        f"scale={scaled_width}:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:{crop_x}:0,"
        f"scale={zoom_width}:{zoom_height}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:(in_w-{WIDTH})/2:0,"
        f"crop={WIDTH}:{visible_height}:0:0,"
        f"scale={recovery_width}:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:({recovery_width}-{WIDTH})/2:0,"
        "eq=contrast=1.045:saturation=1.06,setsar=1,format=yuv420p"
    )


def render_segment(segment: Segment, output: Path) -> int:
    if segment.duration >= 15.0:
        raise ValueError(f"Source clip reaches 15 seconds: {segment.name}")
    count = frames_for(segment.duration)
    audio = (
        "highpass=f=70,"
        "acompressor=threshold=0.125:ratio=2:attack=5:release=80:makeup=1.4,"
        "loudnorm=I=-16:TP=-1.5:LRA=10,aresample=48000:first_pts=0,apad,"
        f"atrim=0:{segment.duration:.6f},"
        f"afade=t=in:st=0:d={min(SEGMENT_FADE_IN, segment.duration * 0.12):.3f},"
        f"afade=t=out:st={max(0.0, segment.duration - min(SEGMENT_FADE_OUT, segment.duration * 0.18)):.6f}:"
        f"d={min(SEGMENT_FADE_OUT, segment.duration * 0.18):.3f}"
    )
    run([
        "ffmpeg", "-y", "-v", "error", "-ss", f"{segment.source_start:.6f}",
        "-i", SOURCE, "-t", f"{segment.duration:.6f}",
        "-vf", f"{scaled_crop(segment)},fps={FPS}",
        "-af", audio, "-frames:v", str(count), *encode_args(),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", output,
    ])
    return count


def build_base(variant: Variant, work: Path) -> tuple[Path, list[dict[str, Any]], int]:
    segment_dir = work / "segments"
    segment_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    timeline: list[dict[str, Any]] = []
    cursor = 0
    for index, segment in enumerate(variant.segments):
        output = segment_dir / f"{index:02d}_{segment.name}.mp4"
        count = render_segment(segment, output)
        timeline.append({
            **asdict(segment),
            "source_duration": segment.duration,
            "start_frame": cursor,
            "end_frame": cursor + count,
            "frames": count,
            "raw_start": cursor / FPS,
            "raw_end": (cursor + count) / FPS,
            "final_start": (cursor / FPS) / POST_SPEED,
            "final_end": ((cursor + count) / FPS) / POST_SPEED,
        })
        cursor += count
        outputs.append(output)
    concat = work / "concat.txt"
    concat.write_text("".join(f"file '{item.resolve()}'\n" for item in outputs), encoding="utf-8")
    base = work / "base.mp4"
    run([
        "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
        "-i", concat, "-c", "copy", base,
    ])
    return base, timeline, cursor


def load_words() -> list[dict[str, Any]]:
    payload = json.loads(TRANSCRIPT.read_text(encoding="utf-8"))
    return [word for segment in payload["segments"] for word in segment.get("words", [])]


def segment_words(segment: Segment, words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        word for word in words
        if float(word["start"]) >= segment.source_start - 0.08
        and float(word["end"]) <= segment.source_end + 0.08
    ]


def auto_bursts(segment: Segment, words: list[dict[str, Any]]) -> list[tuple[float, float, str, str]]:
    selected = segment_words(segment, words)
    groups: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    for word in selected:
        current.append(word)
        text = "".join(str(item["word"]) for item in current).strip()
        span = float(current[-1]["end"]) - float(current[0]["start"])
        punctuation = text.endswith((".", "?", "!", ",", ":", ";"))
        if len(current) >= 4 or (len(current) >= 2 and punctuation) or (len(current) >= 2 and span >= 1.35):
            groups.append(current)
            current = []
    if current:
        if len(current) == 1 and groups and len(groups[-1]) <= 4:
            groups[-1].extend(current)
        else:
            groups.append(current)

    emphasized_words = {
        "JIGSAW", "SAVED", "LIFE", "THERAGUN", "CRASH", "PAIN", "CLINIC",
        "ATHLETES", "VIBRATING", "PROTOTYPE", "PRODUCT", "COMPANY", "DIED", "DIE",
    }
    bursts: list[tuple[float, float, str, str]] = []
    for group in groups:
        text = "".join(str(item["word"]) for item in group).strip().upper()
        if not text:
            continue
        keyword = ""
        for token in text.replace("—", " ").replace("-", " ").split():
            clean = token.strip(".,!?;:'\"")
            if clean in emphasized_words or any(char.isdigit() for char in clean):
                keyword = clean
                break
        if not keyword:
            keyword = text.split()[0].strip(".,!?;:'\"")
        start = max(0.0, float(group[0]["start"]) - segment.source_start)
        end = min(segment.duration, float(group[-1]["end"]) - segment.source_start + 0.10)
        bursts.append((start, max(start + 0.24, end), text, keyword))
    return bursts


def ass_time(seconds: float) -> str:
    centiseconds = max(0, round(seconds * 100))
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    secs, cs = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{cs:02d}"


def ass_color(color: str) -> str:
    value = color.lstrip("#")
    return f"&H00{value[4:6]}{value[2:4]}{value[0:2]}"


def ass_escape(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def emphasize(text: str, keyword: str, color: str = YELLOW) -> str:
    escaped = ass_escape(text)
    key = ass_escape(keyword)
    if not key or key not in escaped:
        return escaped
    return escaped.replace(
        key,
        f"{{\\c{ass_color(color)}\\fs90}}{key}{{\\c&H00FFFFFF&\\fs80}}",
        1,
    )



def write_ass(
    variant: Variant,
    timeline: list[dict[str, Any]],
    words: list[dict[str, Any]],
    raw_duration: float,
    work: Path,
) -> Path:
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
        "Style: Caption,Komika Axis,80,&H00FFFFFF,&H00FFFFFF,&H00000000,&H70000000,-1,0,0,0,100,100,0,0,1,8,2,5,72,72,680,1",
        "Style: Hook,Arial Black,100,&H00FFFFFF,&H00FFFFFF,&H00000000,&H900B0E14,-1,0,0,0,100,100,0,0,1,9,3,8,58,58,1430,1",
        "Style: Badge,Arial Bold,42,&H00FFFFFF,&H00FFFFFF,&H00000000,&HD00B0E14,-1,0,0,0,100,100,0,0,3,2,0,8,55,55,1515,1",
        "Style: CTA,Arial Black,48,&H00FFFFFF,&H00FFFFFF,&H00000000,&HE00B0E14,-1,0,0,0,100,100,0,0,3,3,0,5,80,80,1050,1",
        "Style: Small,Arial Bold,27,&H90FFFFFF,&H90FFFFFF,&H80000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,7,26,26,26,1",
        "",
        "[Events]",
        "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
    ]

    for item, segment in zip(timeline, variant.segments):
        base = float(item["raw_start"])
        for rel_start, rel_end, text, keyword in auto_bursts(segment, words):
            body = f"{{\\an5\\pos(540,1180)\\fad(35,45)}}{emphasize(text, keyword)}"
            lines.append(
                f"Dialogue: 8,{ass_time(base + rel_start)},{ass_time(base + rel_end)},Caption,,0,0,0,,{body}"
            )

    lines.append(
        f"Dialogue: 12,{ass_time(0.05)},{ass_time(variant.hook_title_end)},Hook,,0,0,0,,"
        f"{{\\an8\\pos(540,265)\\c{ass_color(variant.accent)}\\fad(60,90)}}{variant.hook_title}"
    )
    lines.append(
        f"Dialogue: 12,{ass_time(variant.hook_title_end)},{ass_time(variant.hook_followup_end)},Badge,,0,0,0,,"
        f"{{\\an8\\pos(540,325)\\fad(70,100)}}{variant.hook_followup}"
    )

    for start, end, text, color in variant.value_badges:
        lines.append(
            f"Dialogue: 7,{ass_time(start)},{ass_time(min(end, raw_duration))},Badge,,0,0,0,,"
            f"{{\\an8\\pos(540,315)\\c{ass_color(color)}\\fad(90,100)}}{text}"
        )

    for evidence in variant.evidence:
        lines.append(
            f"Dialogue: 14,{ass_time(evidence.start)},{ass_time(evidence.start + evidence.duration)},Small,,0,0,0,,"
            f"{{\\an1\\pos(28,1848)}}ILLUSTRATION • PEXELS {evidence.pexels_id} • {evidence.label}"
        )

    lines.append(
        f"Dialogue: 15,{ass_time(variant.cta_start)},{ass_time(variant.cta_end)},CTA,,0,0,0,,"
        f"{{\\an5\\pos(540,1580)\\fad(100,110)\\c{ass_color(YELLOW)}}}LIKE  •  SUBSCRIBE  •  COMMENT"
    )

    thirds = [0.0, raw_duration / 3, 2 * raw_duration / 3, raw_duration]
    # Top-right is reserved for the source badge. Keeping it out of the
    # watermark route prevents two mandatory labels from becoming unreadable.
    positions = [(42, 72), (830, 1842), (42, 1842)]
    for index, (start, end) in enumerate(zip(thirds[:-1], thirds[1:])):
        x, y = positions[index]
        lines.append(
            f"Dialogue: 16,{ass_time(start)},{ass_time(end)},Small,,0,0,0,,"
            f"{{\\an7\\pos({x},{y})}}HARD KNOCKS LAB"
        )

    lines.append(
        f"Dialogue: 6,{ass_time(10.05)},{ass_time(raw_duration)},Small,,0,0,0,,"
        "{\\an9\\pos(1050,70)}SOURCE: ED MYLETT / JASON WERSLAND"
    )
    output = work / "captions_and_overlays.ass"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def generate_music(duration: float, work: Path) -> Path:
    output = work / "music.wav"
    run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "lavfi", "-i", f"sine=frequency=64:sample_rate=48000:duration={duration:.3f}",
        "-f", "lavfi", "-i", f"sine=frequency=96:sample_rate=48000:duration={duration:.3f}",
        "-filter_complex",
        f"[0:a]volume=0.016,afade=t=in:st=0:d=0.6,afade=t=out:st={duration - 0.8:.3f}:d=0.8[a0];"
        f"[1:a]volume=0.009,afade=t=in:st=0:d=0.6,afade=t=out:st={duration - 0.8:.3f}:d=0.8[a1];"
        "[a0][a1]amix=inputs=2:duration=longest:normalize=0,lowpass=f=900,"
        "aformat=sample_fmts=s16:sample_rates=48000:channel_layouts=stereo[out]",
        "-map", "[out]", "-c:a", "pcm_s16le", output,
    ])
    return output


def generate_sfx(duration: float, variant: Variant, work: Path) -> Path:
    output = work / "sfx.wav"
    sample_rate = 48000
    frame_count = math.ceil(duration * sample_rate)
    event_times = [0.08, variant.hook_title_end, variant.hook_followup_end, variant.cta_start]
    event_times.extend(evidence.start for evidence in variant.evidence)
    event_samples = [round(value * sample_rate) for value in event_times]
    with wave.open(str(output), "wb") as audio:
        audio.setnchannels(2)
        audio.setsampwidth(2)
        audio.setframerate(sample_rate)
        buffer = bytearray()
        for index in range(frame_count):
            value = 0.0
            for start in event_samples:
                elapsed = (index - start) / sample_rate
                if 0.0 <= elapsed <= 0.34:
                    value += 0.24 * math.sin(2 * math.pi * (240 - 120 * elapsed) * elapsed) * math.exp(-12 * elapsed)
            sample = max(-32767, min(32767, round(value * 32767)))
            buffer.extend(struct.pack("<hh", sample, sample))
            if len(buffer) >= 1024 * 1024:
                audio.writeframes(buffer)
                buffer.clear()
        if buffer:
            audio.writeframes(buffer)
    return output


def evidence_enable(variant: Variant, asset: str) -> str:
    clauses = [
        f"between(t,{item.start:.3f},{item.start + item.duration:.3f})"
        for item in variant.evidence if item.asset == asset
    ]
    return "+".join(clauses) if clauses else "0"


def final_composite(
    variant: Variant,
    base: Path,
    ass_file: Path,
    music: Path,
    sfx: Path,
    raw_duration: float,
    total_frames: int,
    work: Path,
    final: Path,
) -> None:
    final_duration = raw_duration / POST_SPEED
    final_frames = frames_for(final_duration)
    ass_path = str(ass_file).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    massage_enable = evidence_enable(variant, "massage")
    shoulder_enable = evidence_enable(variant, "shoulder")
    design_enable = evidence_enable(variant, "design")
    tool_enable = evidence_enable(variant, "tool")
    graph = (
        f"[1:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT},setsar=1,format=yuv420p[massage];"
        f"[2:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT},setsar=1,format=yuv420p[shoulder];"
        f"[3:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT},setsar=1,format=yuv420p[design];"
        f"[4:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT},setsar=1,format=yuv420p[tool];"
        f"[0:v][massage]overlay=0:0:eof_action=pass:enable='{massage_enable}'[v1];"
        f"[v1][shoulder]overlay=0:0:eof_action=pass:enable='{shoulder_enable}'[v2];"
        f"[v2][design]overlay=0:0:eof_action=pass:enable='{design_enable}'[v3];"
        f"[v3][tool]overlay=0:0:eof_action=pass:enable='{tool_enable}'[v4];"
        f"[v4]subtitles='{ass_path}':fontsdir='{FONT_KOMIKA.parent}',"
        f"drawbox=x=0:y=ih-6:w=iw*(t/{raw_duration:.6f}):h=6:color=0xFFD447:t=fill,"
        f"tpad=stop_mode=clone:stop_duration=0.30,setpts=PTS/{POST_SPEED:.5f},fps={FPS},format=yuv420p[vout];"
        "[0:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.0[voice];"
        "[5:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.24[music];"
        "[6:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.70[sfx];"
        f"[voice][music][sfx]amix=inputs=3:duration=longest:normalize=0,atrim=0:{raw_duration:.6f},"
        f"loudnorm=I=-16.5:TP=-1.5:LRA=10,atempo={POST_SPEED:.5f},"
        f"atrim=0:{final_duration:.6f},alimiter=limit=0.94[aout]"
    )
    script = work / "final.ffscript"
    script.write_text(graph + "\n", encoding="utf-8")
    final.parent.mkdir(parents=True, exist_ok=True)
    run([
        "ffmpeg", "-y", "-v", "error", "-i", base,
        "-stream_loop", "-1", "-i", PEXELS_MASSAGE,
        "-stream_loop", "-1", "-i", PEXELS_SHOULDER,
        "-stream_loop", "-1", "-i", PEXELS_DESIGN,
        "-stream_loop", "-1", "-i", PEXELS_TOOL,
        "-i", music, "-i", sfx,
        "-filter_complex_script", script,
        "-map", "[vout]", "-map", "[aout]", "-frames:v", str(final_frames),
        *encode_args(), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart", "-t", f"{final_duration:.6f}", final,
    ])


def extract_checks(final: Path, checks: Path) -> None:
    checks.mkdir(parents=True, exist_ok=True)
    info = probe(final)
    duration = float(info["format"]["duration"])
    hook_times = [0.0, 0.1, 0.2, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    for index, timestamp in enumerate(value for value in hook_times if value < duration):
        run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{timestamp:.2f}", "-i", final,
            "-frames:v", "1", "-q:v", "2", checks / f"hook_{index:02d}_{timestamp:05.2f}.jpg",
        ])
    run([
        "ffmpeg", "-y", "-v", "error", "-ss", "0", "-t", "10", "-i", final,
        "-vf", "fps=2,drawtext=fontfile='/System/Library/Fonts/HelveticaNeue.ttc':text='%{pts\\:hms}':x=10:y=10:fontsize=30:fontcolor=yellow:borderw=3:bordercolor=black,scale=270:-2,tile=5x4:padding=4:margin=4",
        "-frames:v", "1", checks / "hook_0_10.jpg",
    ])
    run([
        "ffmpeg", "-y", "-v", "error", "-i", final,
        "-vf", "fps=1/2.75,drawtext=fontfile='/System/Library/Fonts/HelveticaNeue.ttc':text='%{pts\\:hms}':x=10:y=10:fontsize=30:fontcolor=yellow:borderw=3:bordercolor=black,scale=270:-2,tile=5x4:padding=4:margin=4",
        "-frames:v", "1", checks / "contact.jpg",
    ])


def validate(
    variant: Variant,
    final: Path,
    timeline: list[dict[str, Any]],
    total_frames: int,
    checks: Path,
) -> dict[str, Any]:
    info = probe(final)
    video = next(stream for stream in info["streams"] if stream["codec_type"] == "video")
    audio = next(stream for stream in info["streams"] if stream["codec_type"] == "audio")
    duration = float(info["format"]["duration"])
    raw_duration = total_frames / FPS
    source_seconds = sum(float(item["source_duration"]) for item in timeline)
    evidence_seconds = sum(item.duration for item in variant.evidence)
    first_evidence = min(item.start for item in variant.evidence) / POST_SPEED
    assertions = {
        "resolution": video.get("width") == WIDTH and video.get("height") == HEIGHT,
        "video_codec": video.get("codec_name") == "h264",
        "pixel_format": video.get("pix_fmt") == "yuv420p",
        "frame_rate": video.get("r_frame_rate") == "30/1",
        "audio_codec": audio.get("codec_name") == "aac",
        "audio_rate": audio.get("sample_rate") == "48000",
        "audio_channels": audio.get("channels") == 2,
        "duration": 50.0 <= duration <= 75.0,
        "all_source_clips_under_15": all(float(item["source_duration"]) < 15.0 for item in timeline),
        "source_under_50pct": source_seconds / SOURCE_DURATION <= 0.50,
        "protected_hook_window": first_evidence >= 10.0,
        # Never preserve a misleading stock insert merely to hit a quota. V15B
        # deliberately keeps the real speaker visible over the jigsaw beat.
        "pexels_share": 0.20 <= evidence_seconds / raw_duration <= 0.28,
        "cta_window": 38.0 <= variant.cta_start / POST_SPEED <= 42.0,
        "no_tts": True,
    }
    failed = [name for name, passed in assertions.items() if not passed]
    if failed:
        raise AssertionError(f"Validation failed: {failed}")
    run(["ffmpeg", "-v", "error", "-i", final, "-f", "null", "-"])
    report = {
        "output": str(final),
        "duration": duration,
        "raw_duration": raw_duration,
        "post_speed": POST_SPEED,
        "source_seconds": source_seconds,
        "source_usage_percent": round(100 * source_seconds / SOURCE_DURATION, 3),
        "pexels_seconds": evidence_seconds,
        "pexels_share_percent": round(100 * evidence_seconds / raw_duration, 2),
        "first_fullscreen_pexels_final_time": round(first_evidence, 3),
        "cta_final_start": round(variant.cta_start / POST_SPEED, 3),
        "decode_check": "passed",
        "assertions": assertions,
        "timeline": timeline,
    }
    checks.joinpath("validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


def require_inputs(variant: Variant) -> None:
    required = (
        SOURCE, TRANSCRIPT, PEXELS_MASSAGE, PEXELS_SHOULDER, PEXELS_DESIGN, PEXELS_TOOL,
        FONT_REGULAR, FONT_BOLD, FONT_BLACK, FONT_KOMIKA,
    )
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing inputs:\n" + "\n".join(missing))
    for segment in variant.segments:
        if segment.duration >= 15.0:
            raise ValueError(f"Source segment reaches 15 seconds: {segment.name}")


def render_variant(variant: Variant) -> None:
    require_inputs(variant)
    work = PROJECT / "clips" / "v15_theragun_work" / variant.version
    checks = work / "checks"
    final = PROJECT / "final" / variant.final_name
    work.mkdir(parents=True, exist_ok=True)
    base, timeline, total_frames = build_base(variant, work)
    raw_duration = total_frames / FPS
    work.joinpath("timeline.json").write_text(json.dumps(timeline, indent=2) + "\n", encoding="utf-8")
    words = load_words()
    ass_file = write_ass(variant, timeline, words, raw_duration, work)
    music = generate_music(raw_duration, work)
    sfx = generate_sfx(raw_duration, variant, work)
    final_composite(
        variant, base, ass_file, music, sfx,
        raw_duration, total_frames, work, final,
    )
    extract_checks(final, checks)
    validate(variant, final, timeline, total_frames, checks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=("a", "b", "all"), default="all")
    args = parser.parse_args()
    selected = ("a", "b") if args.variant == "all" else (args.variant,)
    for key in selected:
        render_variant(VARIANTS[key])


if __name__ == "__main__":
    main()
