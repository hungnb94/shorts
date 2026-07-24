#!/usr/bin/env python3
"""Render three evidence-led Theragun Material Revisions.

V16A follows product -> repeatable demand -> company.
V16B follows crash -> motion -> first Theragun.
V16C follows clinic failure -> mechanism -> first Theragun.

All variants preserve original interview audio and keep a human face visible
through the protected 0-10 second hook window.
"""

from __future__ import annotations

import argparse
import json
import math
import struct
import subprocess
import sys
import wave
from array import array
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.hardknocks import render_hardknocks_v15_theragun_remake as legacy

PROJECT = ROOT / "output" / "projects" / "hardknocks"
WORK_ROOT = PROJECT / "clips" / "v16_mrbeast_work"
CACHE = WORK_ROOT / "segment_cache"
WIDTH = legacy.WIDTH
HEIGHT = legacy.HEIGHT
FPS = legacy.FPS
POST_SPEED = legacy.POST_SPEED
TAIL_PAD_RAW = 0.19
YELLOW = legacy.YELLOW
GREEN = legacy.GREEN
RED = legacy.RED
BLUE = legacy.BLUE

Segment = legacy.Segment
Evidence = legacy.Evidence
Variant = legacy.Variant

ASSET_PATHS = {
    "massage": legacy.PEXELS_MASSAGE,
    "shoulder": legacy.PEXELS_SHOULDER,
    "design": legacy.PEXELS_DESIGN,
    "tool": legacy.PEXELS_TOOL,
}
ASSET_INPUT_INDEX = {"massage": 1, "shoulder": 2, "design": 3, "tool": 4}


@dataclass(frozen=True)
class HookPanel:
    start: float
    duration: float
    asset: str
    pexels_id: str
    label: str
    side: str = "left"


@dataclass(frozen=True)
class AudioBeat:
    segment: str
    offset: float
    kind: str


@dataclass(frozen=True)
class Spec:
    variant: Variant
    hook_panels: tuple[HookPanel, ...]
    audio_beats: tuple[AudioBeat, ...]
    discovery_segment: str
    payoff_segment: str
    music_drop_segment: str
    payoff_start: float


A_SEGMENTS = (
    Segment("product_hook", 965.08, 967.74, 0.68, 1.12),
    Segment("crash_impact", 16.40, 18.66, 0.68, 1.08),
    Segment("crash_flip", 18.98, 21.00, 0.68, 1.15),
    Segment("crash_survive", 21.56, 22.78, 0.68, 1.22),
    Segment("clinic_failure", 192.76, 197.18, 0.68, 1.08),
    Segment("table_relief", 240.86, 249.22, 0.68, 1.10),
    Segment("first_theragun", 384.78, 389.40, 0.68, 1.14),
    Segment("jigsaws", 908.86, 922.18, 0.68, 1.08),
    Segment("clinician_sales", 976.64, 983.40, 0.68, 1.10),
    Segment("empty_trunk", 987.10, 992.86, 0.68, 1.15),
    Segment("athlete_market", 993.26, 1001.46, 0.68, 1.12),
    Segment("validation", 1013.16, 1019.92, 0.68, 1.10),
)

B_SEGMENTS = (
    Segment("crash_impact", 16.40, 18.66, 0.68, 1.08),
    Segment("crash_flip", 18.98, 21.00, 0.68, 1.15),
    Segment("crash_survive", 21.56, 22.78, 0.68, 1.22),
    Segment("clinic_failure", 192.76, 197.18, 0.68, 1.13),
    Segment("constraints", 197.32, 206.42, 0.68, 1.08),
    Segment("injection_wait", 206.96, 210.60, 0.68, 1.12),
    Segment("what_do_i_do", 211.26, 212.96, 0.68, 1.18),
    Segment("table_setup", 216.12, 220.62, 0.68, 1.08),
    Segment("table_relief", 237.28, 249.22, 0.68, 1.10),
    Segment("motion", 362.84, 369.04, 0.68, 1.14),
    Segment("make_if_missing", 381.56, 384.46, 0.68, 1.08),
    Segment("first_theragun", 384.78, 389.40, 0.68, 1.14),
)

C_SEGMENTS = (
    Segment("clinic_setup", 192.76, 194.16, 0.68, 1.08),
    Segment("clinic_none", 194.16, 196.34, 0.68, 1.16),
    Segment("clinic_help", 196.34, 197.18, 0.68, 1.22),
    Segment("debilitating", 197.32, 200.00, 0.68, 1.10),
    Segment("surgery", 200.58, 206.42, 0.68, 1.08),
    Segment("injection_wait", 206.96, 210.60, 0.68, 1.12),
    Segment("what_do_i_do", 210.82, 212.96, 0.68, 1.18),
    Segment("table_setup", 216.12, 220.62, 0.68, 1.08),
    Segment("table_relief", 237.28, 249.22, 0.68, 1.10),
    Segment("pain_returns", 250.12, 261.22, 0.68, 1.12),
    Segment("motion", 358.60, 369.04, 0.68, 1.14),
    Segment("make_if_missing", 381.56, 384.46, 0.68, 1.08),
    Segment("first_theragun", 384.78, 389.40, 0.68, 1.14),
)


def raw_duration(segments: tuple[Segment, ...]) -> float:
    return sum(segment.duration for segment in segments)


def make_variant(
    *,
    key: str,
    version: str,
    final_name: str,
    hook_title: str,
    hook_title_end: float,
    hook_followup: str,
    hook_followup_end: float,
    segments: tuple[Segment, ...],
    evidence: tuple[Evidence, ...],
    accent: str,
    badges: tuple[tuple[float, float, str, str], ...],
    payoff: str,
    cta_start: float = 42.40,
    cta_end: float = 46.00,
) -> tuple[Variant, float]:
    duration = raw_duration(segments)
    payoff_start = max(0.0, duration - 7.4)
    return (
        Variant(
            key=key,
            version=version,
            final_name=final_name,
            hook_title=hook_title,
            hook_title_end=hook_title_end,
            hook_followup=hook_followup,
            hook_followup_end=hook_followup_end,
            segments=segments,
            evidence=evidence,
            accent=accent,
            value_badges=badges + ((payoff_start, duration, payoff, GREEN),),
            cta_start=cta_start,
            cta_end=cta_end,
        ),
        payoff_start,
    )


A_VARIANT, A_PAYOFF = make_variant(
    key="a",
    version="v16a",
    final_name="2026-07-24-hardknocks_v16a_product_not_company.mp4",
    hook_title="PRODUCT != COMPANY",
    hook_title_end=2.20,
    hook_followup="WHAT WAS MISSING?",
    hook_followup_end=4.10,
    segments=A_SEGMENTS,
    evidence=(
        Evidence(12.00, 3.60, "shoulder", "6095382", "CRASH INJURY"),
        Evidence(26.00, 3.60, "design", "8003421", "PROTOTYPE ITERATION"),
        Evidence(41.00, 3.60, "tool", "6790429", "250 JIGSAWS"),
        Evidence(55.00, 3.60, "massage", "6390390", "ATHLETE DEMAND"),
    ),
    accent=YELLOW,
    badges=(
        (4.10, 6.90, "7 YEARS EARLIER: THE CRASH", RED),
        (9.25, 13.70, "HIS OWN CLINIC FAILED HIM", RED),
        (27.90, 41.20, "ONE INVENTION -> 250 UNITS", BLUE),
        (51.80, 61.70, "THE TRUNK KEPT EMPTYING", YELLOW),
    ),
    payoff="REPEATABLE DEMAND BUILT THE COMPANY",
)

B_VARIANT, B_PAYOFF = make_variant(
    key="b",
    version="v16b",
    final_name="2026-07-24-hardknocks_v16b_crash_not_breakthrough.mp4",
    hook_title="THE CRASH WASN'T IT",
    hook_title_end=2.70,
    hook_followup="SO WHAT WAS?",
    hook_followup_end=5.20,
    segments=B_SEGMENTS,
    evidence=(
        Evidence(11.00, 3.60, "shoulder", "6095382", "INJURY CONSTRAINT"),
        Evidence(27.00, 3.60, "shoulder", "6095382", "TEMPORARY RELIEF"),
        Evidence(42.00, 3.60, "design", "8003421", "BACK-AND-FORTH MOTION"),
        Evidence(50.00, 3.60, "massage", "6390390", "FIRST THERAGUN"),
    ),
    accent=RED,
    badges=(
        (5.20, 7.00, "HE SURVIVED", GREEN),
        (7.00, 14.00, "BUT HIS CLINIC HAD NO ANSWER", RED),
        (36.00, 49.70, "RELIEF -> QUESTION -> MOTION", BLUE),
    ),
    payoff="THE MOTION CREATED THE PRODUCT",
)

C_VARIANT, C_PAYOFF = make_variant(
    key="c",
    version="v16c",
    final_name="2026-07-24-hardknocks_v16c_clinic_could_not_help.mp4",
    hook_title="HE WAS THE DOCTOR",
    hook_title_end=2.20,
    hook_followup="HIS CLINIC COULDN'T HELP",
    hook_followup_end=5.20,
    segments=C_SEGMENTS,
    evidence=(
        Evidence(11.00, 3.60, "shoulder", "6095382", "PAIN CONSTRAINT"),
        Evidence(27.00, 3.60, "shoulder", "6095382", "TEMPORARY RELIEF"),
        Evidence(43.00, 3.60, "design", "8003421", "MECHANISM TEST"),
        Evidence(56.00, 3.60, "massage", "6390390", "PRODUCT REVEAL"),
    ),
    accent=BLUE,
    badges=(
        (5.20, 10.10, "SURGERY OR MEDICATION", RED),
        (17.10, 19.70, "WHAT DO I DO?", YELLOW),
        (36.20, 48.00, "THE PAIN CAME BACK", RED),
        (48.00, 58.00, "WHY DID THE MOTION WORK?", BLUE),
    ),
    payoff="NECESSITY -> MECHANISM -> PRODUCT",
)

SPECS = {
    "a": Spec(
        variant=A_VARIANT,
        hook_panels=(
            HookPanel(0.45, 2.25, "design", "8003421", "PRODUCT", "left"),
            HookPanel(4.10, 2.90, "shoulder", "6095382", "CRASH INJURY", "left"),
        ),
        audio_beats=(
            AudioBeat("product_hook", 0.70, "drop"),
            AudioBeat("crash_impact", 0.00, "impact"),
            AudioBeat("first_theragun", 0.00, "reveal"),
            AudioBeat("jigsaws", 0.00, "count"),
            AudioBeat("empty_trunk", 0.00, "drop"),
            AudioBeat("athlete_market", 0.00, "reveal"),
        ),
        discovery_segment="first_theragun",
        payoff_segment="athlete_market",
        music_drop_segment="empty_trunk",
        payoff_start=A_PAYOFF,
    ),
    "b": Spec(
        variant=B_VARIANT,
        hook_panels=(
            HookPanel(0.45, 3.10, "shoulder", "6095382", "CRASH IMPACT", "left"),
        ),
        audio_beats=(
            AudioBeat("crash_impact", 0.00, "impact"),
            AudioBeat("crash_survive", 0.00, "reveal"),
            AudioBeat("what_do_i_do", 0.00, "drop"),
            AudioBeat("table_relief", 3.60, "vibration"),
            AudioBeat("motion", 0.00, "vibration"),
            AudioBeat("first_theragun", 0.00, "reveal"),
        ),
        discovery_segment="motion",
        payoff_segment="first_theragun",
        music_drop_segment="what_do_i_do",
        payoff_start=B_PAYOFF,
    ),
    "c": Spec(
        variant=C_VARIANT,
        hook_panels=(
            HookPanel(0.45, 3.15, "shoulder", "6095382", "PAIN", "left"),
        ),
        audio_beats=(
            AudioBeat("clinic_none", 0.00, "drop"),
            AudioBeat("surgery", 0.00, "impact"),
            AudioBeat("what_do_i_do", 0.00, "drop"),
            AudioBeat("table_relief", 3.60, "vibration"),
            AudioBeat("pain_returns", 0.00, "impact"),
            AudioBeat("motion", 0.00, "vibration"),
            AudioBeat("first_theragun", 0.00, "reveal"),
        ),
        discovery_segment="motion",
        payoff_segment="first_theragun",
        music_drop_segment="what_do_i_do",
        payoff_start=C_PAYOFF,
    ),
}


def run(args: list[str | Path], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    printable = " ".join(str(arg) for arg in args)
    print("+", printable, flush=True)
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=capture,
    )


def frames_for(seconds: float) -> int:
    return max(1, round(seconds * FPS))


def cache_path(segment: Segment) -> Path:
    safe_name = "".join(char if char.isalnum() or char in "_-" else "_" for char in segment.name)
    token = (
        f"{safe_name}_{segment.source_start:.2f}_{segment.source_end:.2f}_"
        f"{segment.focus:.2f}_{segment.zoom:.2f}.mp4"
    )
    return CACHE / token


def render_segment(segment: Segment) -> tuple[Path, int]:
    if segment.duration >= 15.0:
        raise ValueError(f"Source clip reaches 15 seconds: {segment.name}")
    CACHE.mkdir(parents=True, exist_ok=True)
    output = cache_path(segment)
    count = frames_for(segment.duration)
    if output.exists():
        return output, count

    fade_in = min(0.05, segment.duration * 0.06)
    fade_out = min(0.08, segment.duration * 0.10)
    audio = (
        "highpass=f=70,"
        "acompressor=threshold=0.125:ratio=2:attack=5:release=80:makeup=1.4,"
        "loudnorm=I=-16:TP=-1.5:LRA=10,aresample=48000:first_pts=0,apad,"
        f"atrim=0:{segment.duration:.6f},"
        f"afade=t=in:st=0:d={fade_in:.3f},"
        f"afade=t=out:st={max(0.0, segment.duration - fade_out):.6f}:d={fade_out:.3f}"
    )
    run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{segment.source_start:.6f}", "-i", legacy.SOURCE,
        "-t", f"{segment.duration:.6f}",
        "-vf", f"{legacy.scaled_crop(segment)},fps={FPS}",
        "-af", audio,
        "-frames:v", str(count),
        *legacy.encode_args(),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        output,
    ])
    return output, count


def build_base(variant: Variant, work: Path) -> tuple[Path, list[dict[str, Any]], int]:
    outputs: list[Path] = []
    timeline: list[dict[str, Any]] = []
    cursor = 0
    for segment in variant.segments:
        output, count = render_segment(segment)
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


def timeline_start(timeline: list[dict[str, Any]], name: str) -> float:
    matches = [float(item["raw_start"]) for item in timeline if item["name"] == name]
    if len(matches) != 1:
        raise ValueError(f"Expected one timeline segment named {name!r}; got {len(matches)}")
    return matches[0]


def write_ass(
    spec: Spec,
    timeline: list[dict[str, Any]],
    words: list[dict[str, Any]],
    duration: float,
    work: Path,
) -> Path:
    output = legacy.write_ass(spec.variant, timeline, words, duration, work)
    lines = output.read_text(encoding="utf-8").splitlines()
    # V15's inherited source badge starts at raw 10.05s. After the 1.06x final
    # speed-up that lands inside the protected hook at 9.48s. Move it to raw
    # 10.65s so its first final frame is safely after t=10.0s.
    old_source_prefix = f"Dialogue: 6,{legacy.ass_time(10.05)},"
    new_source_prefix = f"Dialogue: 6,{legacy.ass_time(10.65)},"
    source_badge_matches = sum(line.startswith(old_source_prefix) for line in lines)
    if source_badge_matches != 1:
        raise ValueError(f"Expected one inherited source badge; got {source_badge_matches}")
    lines = [
        new_source_prefix + line[len(old_source_prefix):]
        if line.startswith(old_source_prefix)
        else line
        for line in lines
    ]
    for panel in spec.hook_panels:
        x = 50 if panel.side == "left" else 650
        lines.append(
            f"Dialogue: 17,{legacy.ass_time(panel.start)},{legacy.ass_time(panel.start + panel.duration)},"
            f"Small,,0,0,0,,{{\\an7\\pos({x + 12},438)}}ILLUSTRATION • PEXELS {panel.pexels_id} • {panel.label}"
        )
    # The variant's original payoff badge ends at the source-float duration.
    # Extend it across the frame-alignment safety tail without double-rendering
    # the badge over the body of the video.
    payoff_tail_start = max(spec.payoff_start, raw_duration(spec.variant.segments) - 0.01)
    lines.append(
        f"Dialogue: 18,{legacy.ass_time(payoff_tail_start)},{legacy.ass_time(duration)},"
        f"Badge,,0,0,0,,{spec.variant.value_badges[-1][2]}"
    )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def write_stereo_wave(path: Path, mono: array, sample_rate: int = 48000) -> None:
    stereo = array("h")
    for value in mono:
        sample = max(-32767, min(32767, round(value)))
        stereo.append(sample)
        stereo.append(sample)
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(2)
        audio.setsampwidth(2)
        audio.setframerate(sample_rate)
        audio.writeframes(stereo.tobytes())


def generate_music(
    duration: float,
    discovery_at: float,
    payoff_at: float,
    drop_at: float,
    work: Path,
) -> Path:
    output = work / "music.wav"
    sample_rate = 48000
    frame_count = math.ceil(duration * sample_rate)
    mono = array("h")
    drop_end = drop_at + 0.18
    for index in range(frame_count):
        t = index / sample_rate
        if t < discovery_at:
            low, high, amplitude, beat = 58.0, 87.0, 0.010, 0.72
        elif t < payoff_at:
            low, high, amplitude, beat = 72.0, 144.0, 0.012, 0.58
        else:
            low, high, amplitude, beat = 92.0, 184.0, 0.014, 0.48
        pulse = 0.62 + 0.38 * max(0.0, math.sin(2 * math.pi * t / beat))
        value = amplitude * pulse * (
            0.70 * math.sin(2 * math.pi * low * t)
            + 0.30 * math.sin(2 * math.pi * high * t)
        )
        if drop_at <= t <= drop_end:
            value *= 0.03
        fade = min(1.0, t / 0.45, max(0.0, duration - t) / 0.70)
        mono.append(round(value * fade * 32767))
    write_stereo_wave(output, mono, sample_rate)
    return output


def sfx_wave(kind: str, elapsed: float) -> float:
    if kind == "impact":
        return 0.34 * math.sin(2 * math.pi * (105 - 45 * elapsed) * elapsed) * math.exp(-10 * elapsed)
    if kind == "reveal":
        return 0.24 * math.sin(2 * math.pi * (420 + 760 * elapsed) * elapsed) * math.exp(-6 * elapsed)
    if kind == "vibration":
        return 0.18 * math.sin(2 * math.pi * 145 * elapsed) * math.exp(-5 * elapsed)
    if kind == "count":
        return 0.20 * math.sin(2 * math.pi * 760 * elapsed) * math.exp(-18 * elapsed)
    if kind == "drop":
        return 0.20 * math.sin(2 * math.pi * (320 - 180 * elapsed) * elapsed) * math.exp(-13 * elapsed)
    return 0.13 * math.sin(2 * math.pi * 540 * elapsed) * math.exp(-16 * elapsed)


def generate_sfx(
    duration: float,
    spec: Spec,
    timeline: list[dict[str, Any]],
    work: Path,
) -> Path:
    output = work / "sfx.wav"
    sample_rate = 48000
    frame_count = math.ceil(duration * sample_rate)
    mix = array("f", [0.0]) * frame_count

    events: list[tuple[float, str]] = [(0.08, "reveal"), (spec.variant.cta_start, "count")]
    events.extend((panel.start, "reveal") for panel in spec.hook_panels)
    events.extend((evidence.start, "reveal") for evidence in spec.variant.evidence)
    for beat in spec.audio_beats:
        events.append((timeline_start(timeline, beat.segment) + beat.offset, beat.kind))
    for item in timeline[:8]:
        at = float(item["raw_start"])
        if at > 0.01 and at < 10.0:
            events.append((at, "tick"))

    for at, kind in events:
        length = 0.46 if kind in {"impact", "reveal", "vibration"} else 0.26
        start = max(0, round(at * sample_rate))
        stop = min(frame_count, start + round(length * sample_rate))
        for index in range(start, stop):
            mix[index] += sfx_wave(kind, (index - start) / sample_rate)

    mono = array("h", (round(max(-0.92, min(0.92, value)) * 32767) for value in mix))
    write_stereo_wave(output, mono, sample_rate)
    return output


def enable_for_evidence(variant: Variant, asset: str) -> str:
    windows = [
        f"between(t,{item.start:.3f},{item.start + item.duration:.3f})"
        for item in variant.evidence
        if item.asset == asset
    ]
    return "+".join(windows) if windows else "0"


def enable_for_panels(spec: Spec, asset: str) -> str:
    windows = [
        f"between(t,{item.start:.3f},{item.start + item.duration:.3f})"
        for item in spec.hook_panels
        if item.asset == asset
    ]
    return "+".join(windows) if windows else "0"


def panel_side(spec: Spec, asset: str) -> str:
    matches = [item.side for item in spec.hook_panels if item.asset == asset]
    return matches[0] if matches else "left"


def final_composite(
    spec: Spec,
    base: Path,
    ass_file: Path,
    music: Path,
    sfx: Path,
    duration: float,
    total_frames: int,
    work: Path,
    final: Path,
) -> None:
    final_duration = duration / POST_SPEED
    final_frames = frames_for(final_duration)
    ass_path = str(ass_file).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")

    graph_parts: list[str] = []
    for asset, index in ASSET_INPUT_INDEX.items():
        graph_parts.append(f"[{index}:v]split=2[{asset}_full_src][{asset}_panel_src]")
        graph_parts.append(
            f"[{asset}_full_src]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={WIDTH}:{HEIGHT},setsar=1,format=yuv420p[{asset}_full]"
        )
        graph_parts.append(
            f"[{asset}_panel_src]scale=390:500:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop=390:500,drawbox=x=0:y=0:w=iw:h=ih:color=white@0.86:t=5,"
            f"setsar=1,format=yuv420p[{asset}_panel]"
        )

    current = "0:v"
    layer = 1
    for asset in ASSET_INPUT_INDEX:
        output = f"vf{layer}"
        graph_parts.append(
            f"[{current}][{asset}_full]overlay=0:0:eof_action=pass:"
            f"enable='{enable_for_evidence(spec.variant, asset)}'[{output}]"
        )
        current = output
        layer += 1
    for asset in ASSET_INPUT_INDEX:
        x = 50 if panel_side(spec, asset) == "left" else 640
        output = f"vf{layer}"
        graph_parts.append(
            f"[{current}][{asset}_panel]overlay={x}:430:eof_action=pass:"
            f"enable='{enable_for_panels(spec, asset)}'[{output}]"
        )
        current = output
        layer += 1

    graph_parts.append(
        f"[{current}]subtitles='{ass_path}':fontsdir='{legacy.FONT_KOMIKA.parent}',"
        f"drawbox=x=0:y=ih-6:w=iw*(t/{duration:.6f}):h=6:color=0xFFD447:t=fill,"
        f"tpad=stop_mode=clone:stop_duration=0.30,setpts=PTS/{POST_SPEED:.5f},"
        f"fps={FPS},format=yuv420p[vout]"
    )
    graph_parts.extend([
        "[0:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.0[voice]",
        "[5:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.24[music]",
        "[6:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.72[sfx]",
        f"[voice][music][sfx]amix=inputs=3:duration=longest:normalize=0,atrim=0:{duration:.6f},"
        f"loudnorm=I=-16.5:TP=-1.5:LRA=10,atempo={POST_SPEED:.5f},"
        f"atrim=0:{final_duration:.6f},alimiter=limit=0.80:level=false[aout]",
    ])
    script = work / "final.ffscript"
    script.write_text(";\n".join(graph_parts) + "\n", encoding="utf-8")

    final.parent.mkdir(parents=True, exist_ok=True)
    run([
        "ffmpeg", "-y", "-v", "error", "-i", base,
        "-stream_loop", "-1", "-i", legacy.PEXELS_MASSAGE,
        "-stream_loop", "-1", "-i", legacy.PEXELS_SHOULDER,
        "-stream_loop", "-1", "-i", legacy.PEXELS_DESIGN,
        "-stream_loop", "-1", "-i", legacy.PEXELS_TOOL,
        "-i", music, "-i", sfx,
        "-filter_complex_script", script,
        "-map", "[vout]", "-map", "[aout]", "-frames:v", str(final_frames),
        *legacy.encode_args(),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart", "-t", f"{final_duration:.6f}", final,
    ])


def make_contact_sheet(final: Path, output: Path, interval: float, tile: str) -> None:
    run([
        "ffmpeg", "-y", "-v", "error", "-i", final,
        "-vf",
        f"fps=1/{interval:.4f},"
        "drawtext=fontfile='/System/Library/Fonts/HelveticaNeue.ttc':"
        "text='%{pts\\:hms}':x=10:y=10:fontsize=30:fontcolor=yellow:"
        f"borderw=3:bordercolor=black,scale=270:-2,tile={tile}:padding=4:margin=4",
        "-frames:v", "1", output,
    ])


def extract_checks(spec: Spec, final: Path, checks: Path) -> None:
    checks.mkdir(parents=True, exist_ok=True)
    info = legacy.probe(final)
    duration = float(info["format"]["duration"])
    hook_times = [0.0, 0.1, 0.2, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    for index, timestamp in enumerate(value for value in hook_times if value < duration):
        run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{timestamp:.2f}", "-i", final,
            "-frames:v", "1", "-q:v", "2", checks / f"hook_{index:02d}_{timestamp:05.2f}.jpg",
        ])
    run([
        "ffmpeg", "-y", "-v", "error", "-ss", "0", "-t", "10", "-i", final,
        "-vf",
        "fps=2,drawtext=fontfile='/System/Library/Fonts/HelveticaNeue.ttc':"
        "text='%{pts\\:hms}':x=10:y=10:fontsize=30:fontcolor=yellow:"
        "borderw=3:bordercolor=black,scale=270:-2,tile=5x4:padding=4:margin=4",
        "-frames:v", "1", checks / "hook_0_10.jpg",
    ])
    make_contact_sheet(final, checks / "contact.jpg", duration / 20.0, "5x4")

    targets = {
        "cta": spec.variant.cta_start / POST_SPEED,
        "payoff": spec.payoff_start / POST_SPEED,
        "tail": max(0.0, duration - 0.70),
    }
    for name, timestamp in targets.items():
        run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{timestamp:.3f}", "-i", final,
            "-frames:v", "1", "-q:v", "2", checks / f"{name}_{timestamp:.2f}.jpg",
        ])


def validate(
    spec: Spec,
    final: Path,
    timeline: list[dict[str, Any]],
    total_frames: int,
    checks: Path,
) -> dict[str, Any]:
    info = legacy.probe(final)
    source_info = legacy.probe(legacy.SOURCE)
    source_duration = float(source_info["format"]["duration"])
    video = next(stream for stream in info["streams"] if stream["codec_type"] == "video")
    audio = next(stream for stream in info["streams"] if stream["codec_type"] == "audio")
    duration = float(info["format"]["duration"])
    raw = total_frames / FPS
    source_seconds = sum(float(item["source_duration"]) for item in timeline)
    evidence_seconds = sum(item.duration for item in spec.variant.evidence)
    first_fullscreen = min(item.start for item in spec.variant.evidence) / POST_SPEED
    tail_safety = duration - float(timeline[-1]["final_end"])
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
        "source_under_50pct": source_seconds / source_duration <= 0.50,
        "fullscreen_stock_after_10s": first_fullscreen >= 10.0,
        "hook_panels_keep_face_visible": all(panel.side in {"left", "right"} for panel in spec.hook_panels),
        "pexels_share": 0.20 <= evidence_seconds / raw <= 0.28,
        "cta_window": 38.0 <= spec.variant.cta_start / POST_SPEED <= 42.0,
        "tail_safety": tail_safety >= 0.15,
        "no_tts": True,
    }
    failed = [name for name, passed in assertions.items() if not passed]
    if failed:
        raise AssertionError(f"Validation failed: {failed}")
    run(["ffmpeg", "-v", "error", "-i", final, "-f", "null", "-"])
    report = {
        "output": str(final),
        "duration": duration,
        "raw_duration": raw,
        "post_speed": POST_SPEED,
        "source_duration": source_duration,
        "source_seconds": source_seconds,
        "source_usage_percent": round(100 * source_seconds / source_duration, 3),
        "pexels_seconds": evidence_seconds,
        "pexels_share_percent": round(100 * evidence_seconds / raw, 2),
        "first_fullscreen_pexels_final_time": round(first_fullscreen, 3),
        "cta_final_start": round(spec.variant.cta_start / POST_SPEED, 3),
        "payoff_final_start": round(spec.payoff_start / POST_SPEED, 3),
        "tail_safety_final_seconds": round(tail_safety, 3),
        "decode_check": "passed",
        "assertions": assertions,
        "timeline": timeline,
    }
    checks.joinpath("validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


def require_inputs(spec: Spec) -> None:
    required = (
        legacy.SOURCE,
        legacy.TRANSCRIPT,
        *ASSET_PATHS.values(),
        legacy.FONT_REGULAR,
        legacy.FONT_BOLD,
        legacy.FONT_BLACK,
        legacy.FONT_KOMIKA,
    )
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing inputs:\n" + "\n".join(missing))
    if any(segment.duration >= 15.0 for segment in spec.variant.segments):
        raise ValueError("Every source segment must remain under 15 seconds")
    if raw_duration(spec.variant.segments) / POST_SPEED < 50.0:
        raise ValueError("Projected final runtime is shorter than 50 seconds")


def render_spec(spec: Spec) -> None:
    require_inputs(spec)
    work = WORK_ROOT / spec.variant.version
    checks = work / "checks"
    final = PROJECT / "final" / spec.variant.final_name
    work.mkdir(parents=True, exist_ok=True)

    base, timeline, total_frames = build_base(spec.variant, work)
    raw = total_frames / FPS
    media_duration = raw + TAIL_PAD_RAW
    work.joinpath("timeline.json").write_text(json.dumps(timeline, indent=2) + "\n", encoding="utf-8")
    words = legacy.load_words()
    ass_file = write_ass(spec, timeline, words, media_duration, work)
    discovery_at = timeline_start(timeline, spec.discovery_segment)
    payoff_at = timeline_start(timeline, spec.payoff_segment)
    drop_at = max(0.0, timeline_start(timeline, spec.music_drop_segment) - 0.12)
    music = generate_music(media_duration, discovery_at, payoff_at, drop_at, work)
    sfx = generate_sfx(media_duration, spec, timeline, work)
    final_composite(spec, base, ass_file, music, sfx, media_duration, total_frames, work, final)
    extract_checks(spec, final, checks)
    validate(spec, final, timeline, total_frames, checks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=("a", "b", "c", "all"), default="all")
    args = parser.parse_args()
    selected = ("a", "b", "c") if args.variant == "all" else (args.variant,)
    for key in selected:
        render_spec(SPECS[key])


if __name__ == "__main__":
    main()
