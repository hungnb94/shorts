#!/usr/bin/env python3
"""Render HardKnocks V7: Raising Cane's one-product focus bet.

The edit keeps Todd Graves' original interview voice and rebuilds four short
source excerpts into a WEALTHIAN-style authority/mechanism/proof/reframe story.
Editorial value comes from progressive captions, capital/scale annotations,
and verified Pexels evidence. Every source excerpt is under 15 seconds and the
selected footage is under 5% of the original interview.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "hardknocks"
SOURCE = PROJECT / "source" / "n5EmUiLNVjg.mp4"
PEXELS_PRODUCT = ROOT / "output/shared/pexels/fried_chicken_9829921.mp4"
PEXELS_TEAM = ROOT / "output/shared/pexels/restaurant_team_4253352.mp4"
PEXELS = PEXELS_PRODUCT
WORK = PROJECT / "clips" / "v7_work"
PANELS = WORK / "panels"
CHECKS = WORK / "checks"
FINAL = PROJECT / "final" / "2026-07-15-hardknocks_v7_raising_canes_focus_bet.mp4"

WIDTH = 1080
HEIGHT = 1920
FPS = 30
POST_SPEED = 1.02
FINISH_PAD = 0.70
SOURCE_DURATION = 990.361

FONT_REGULAR = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")

NAVY = "#07111F"
PANEL = "#101820"
WHITE = "#F8FAFC"
MUTED = "#AAB8C8"
YELLOW = "#FFD447"
GREEN = "#4EE6A8"
RED = "#FF5A67"


@dataclass(frozen=True)
class TimelineClip:
    name: str
    start_frame: int
    frames: int
    kind: str
    source_start: float
    crop_focus: float
    zoom: float

    @property
    def end_frame(self) -> int:
        return self.start_frame + self.frames


@dataclass(frozen=True)
class ClipPlan:
    name: str
    frames: int
    source_start: float
    crop_focus: float
    zoom: float


@dataclass(frozen=True)
class EvidenceOverlay:
    name: str
    start_frame: int
    frames: int
    source_offset: float
    asset: Path
    mode: str

    @property
    def end_frame(self) -> int:
        return self.start_frame + self.frames


def build_timeline() -> list[TimelineClip]:
    plans = [
        ClipPlan("rejection_focus", 323, 188.60, crop_focus=0.28, zoom=1.40),
        ClipPlan("funding_proof", 422, 299.16, crop_focus=0.28, zoom=1.36),
        ClipPlan("scale_proof", 290, 354.62, crop_focus=0.28, zoom=1.44),
        ClipPlan("rebuild_rule", 403, 760.60, crop_focus=0.28, zoom=1.38),
    ]
    timeline: list[TimelineClip] = []
    cursor = 0
    for plan in plans:
        timeline.append(
            TimelineClip(
                name=plan.name,
                start_frame=cursor,
                frames=plan.frames,
                kind="source",
                source_start=plan.source_start,
                crop_focus=plan.crop_focus,
                zoom=plan.zoom,
            )
        )
        cursor += plan.frames
    return timeline


TIMELINE = build_timeline()
TOTAL_FRAMES = TIMELINE[-1].end_frame
RAW_DURATION = TOTAL_FRAMES / FPS

# Full-screen evidence starts at raw 10.40s / final 10.196s, outside the
# protected 0-10s face window. The School of Hard Knocks audio remains intact.
PEXELS_OVERLAYS = (
    EvidenceOverlay("product_reveal", 312, 72, 0.0, PEXELS_PRODUCT, "fullscreen"),
    EvidenceOverlay("team_funding", 612, 90, 2.0, PEXELS_TEAM, "corner"),
    EvidenceOverlay("team_rule", 1260, 90, 8.0, PEXELS_TEAM, "fullscreen"),
)

# First caption appears at raw t=0.10s while Todd is already moving.
HOOK_CAPTIONS = [
    (0.10, 1.35, "THE WORST GRADE"),
    (1.35, 2.55, "GOOD PLAN"),
    (2.55, 3.75, "BAD CONCEPT?"),
    (3.75, 5.10, "JUST ONE PRODUCT"),
    (5.10, 6.45, "CHICKEN FINGERS"),
    (6.45, 7.80, "EVERYONE ADDED"),
    (7.80, 9.15, "MORE VARIETY"),
    (9.15, 10.7667, "IT WOULD NEVER WORK"),
]

CAPTIONS = [
    *[(start, end, "Hook", text) for start, end, text in HOOK_CAPTIONS],
    (3.75, 6.45, "Editorial", "ONE CORE PRODUCT"),
    (10.7667, 12.10, "Caption", "I RAISED MY OWN EQUITY"),
    (12.10, 13.80, "Emphasis", "ABOUT $50,000"),
    (13.80, 15.50, "Caption", "A SMALL SBA LOAN"),
    (15.50, 17.20, "Emphasis", "ANOTHER $50,000"),
    (17.20, 18.75, "Editorial", "$50K CASH + $50K SBA"),
    (18.75, 20.45, "Caption", "AN OLD RESTAURANT SPACE"),
    (20.45, 22.55, "Caption", "DID THE WORK MYSELF"),
    (22.55, 24.8333, "Emphasis", "OPENED IN 1996"),
    (24.8333, 26.25, "Caption", "MOST IN ONE YEAR?"),
    (26.25, 28.15, "Emphasis", "$400 MILLION"),
    (28.15, 29.65, "Caption", "NET WORTH?"),
    (29.65, 31.90, "Emphasis", "NORTH OF $20 BILLION"),
    (31.90, 34.50, "Source", "SOURCE-REPORTED"),
    (34.50, 36.25, "Caption", "LOST EVERYTHING TOMORROW?"),
    (36.25, 38.05, "Emphasis", "I COULD MAKE IT BACK"),
    (38.05, 39.75, "Caption", "STICK TO WHAT YOU KNOW"),
    (39.75, 41.65, "Editorial", "CRAVABLE PRODUCT"),
    (41.65, 43.15, "Editorial", "FOCUS"),
    (43.15, 44.85, "Editorial", "BUILD A TEAM"),
    (44.85, RAW_DURATION, "Editorial", "SCALE IT"),
    (10.40, RAW_DURATION, "Citation", "SOURCE: THE SCHOOL OF HARD KNOCKS"),
]


def tts_lines() -> list:
    return []


def source_usage_ratio(timeline: list[TimelineClip]) -> float:
    source_seconds = sum(
        clip.frames for clip in timeline if clip.kind == "source"
    ) / FPS
    return source_seconds / SOURCE_DURATION


def final_duration() -> float:
    return (RAW_DURATION + FINISH_PAD) / POST_SPEED


def finish_audio_filter() -> str:
    audio_duration = RAW_DURATION / POST_SPEED + 0.35
    return (
        f"atempo={POST_SPEED},apad=pad_dur=0.35,"
        f"atrim=duration={audio_duration:.6f}"
    )


def finish_video_filter() -> str:
    return f"tpad=stop_mode=clone:stop_duration={FINISH_PAD:.2f},setpts=PTS/{POST_SPEED}"


def validate_timeline(timeline: list[TimelineClip], *, total_frames: int) -> None:
    if not timeline:
        raise ValueError("timeline is empty")
    cursor = 0
    for clip in timeline:
        if clip.start_frame != cursor:
            raise ValueError(f"timeline gap or overlap at {clip.name}")
        if clip.frames <= 0:
            raise ValueError(f"non-positive clip duration: {clip.name}")
        if clip.kind != "source":
            raise ValueError(f"unsupported timeline kind: {clip.kind}")
        if clip.frames / FPS >= 15.0:
            raise ValueError(f"source clip reaches 15 seconds: {clip.name}")
        if not 0.0 <= clip.crop_focus <= 1.0:
            raise ValueError(f"invalid crop focus: {clip.name}")
        cursor = clip.end_frame
    if cursor != total_frames:
        raise ValueError(f"timeline total mismatch: {cursor} != {total_frames}")
    if source_usage_ratio(timeline) > 0.5:
        raise ValueError("source usage exceeds 50%")
    if not 45.0 <= final_duration() <= 60.0:
        raise ValueError(f"final duration out of range: {final_duration():.3f}s")
    for overlay in PEXELS_OVERLAYS:
        if overlay.start_frame / FPS / POST_SPEED < 10.0:
            raise ValueError(f"Pexels enters protected face window: {overlay.name}")
        if overlay.frames <= 0 or overlay.end_frame > total_frames:
            raise ValueError(f"invalid evidence window: {overlay.name}")
        if overlay.mode not in {"corner", "fullscreen"}:
            raise ValueError(f"invalid evidence mode: {overlay.mode}")


def ass_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remainder = seconds % 60
    return f"{hours}:{minutes:02d}:{remainder:05.2f}"


def run(args: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(str(arg) for arg in args))
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=capture,
    )


def probe(path: Path) -> dict[str, Any]:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(path),
        ],
        capture=True,
    )
    return json.loads(result.stdout)


def max_volume_db(
    path: Path,
    *,
    start: float | None = None,
    duration: float | None = None,
) -> float:
    args = ["ffmpeg", "-hide_banner"]
    if start is not None:
        args.extend(["-ss", f"{start:.6f}"])
    args.extend(["-i", str(path)])
    if duration is not None:
        args.extend(["-t", f"{duration:.6f}"])
    args.extend(["-vn", "-af", "volumedetect", "-f", "null", "-"])
    result = subprocess.run(args, cwd=ROOT, check=True, text=True, capture_output=True)
    match = re.search(r"max_volume:\s*(-?\d+(?:\.\d+)?) dB", result.stderr)
    if not match:
        raise RuntimeError(f"Could not measure max volume for {path}")
    return float(match.group(1))


def assert_not_silent(
    path: Path,
    *,
    label: str,
    threshold_db: float = -35.0,
    start: float | None = None,
    duration: float | None = None,
) -> float:
    measured = max_volume_db(path, start=start, duration=duration)
    if measured <= threshold_db:
        raise AssertionError(
            f"{label} is silent: max_volume={measured:.1f} dB, threshold={threshold_db:.1f} dB"
        )
    print(f"AUDIO PASS {label}: max_volume={measured:.1f} dB")
    return measured


def require_inputs() -> None:
    required = [SOURCE, PEXELS_PRODUCT, PEXELS_TEAM, FONT_REGULAR, FONT_BOLD]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required inputs:\n" + "\n".join(missing))
    validate_timeline(TIMELINE, total_frames=TOTAL_FRAMES)
    for directory in [WORK, PANELS, CHECKS, FINAL.parent]:
        directory.mkdir(parents=True, exist_ok=True)


def encode_args() -> list[str]:
    return [
        "-c:v",
        "libx264",
        "-crf",
        "18",
        "-preset",
        "fast",
        "-pix_fmt",
        "yuv420p",
        "-r",
        str(FPS),
    ]


def source_video_filter(clip: TimelineClip) -> str:
    scaled_width = 3414
    crop_x = round((scaled_width - WIDTH) * clip.crop_focus)
    zoom_width = round(WIDTH * clip.zoom)
    zoom_height = round(HEIGHT * clip.zoom)
    return (
        f"scale={scaled_width}:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:{crop_x}:0,"
        f"scale={zoom_width}:{zoom_height}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:(in_w-{WIDTH})/2:(in_h-{HEIGHT})/2,"
        "eq=contrast=1.05:saturation=1.06,"
        f"fps={FPS},setsar=1,format=yuv420p"
    )


def render_source_clip(clip: TimelineClip) -> Path:
    output = WORK / f"{clip.name}.mp4"
    duration = clip.frames / FPS
    audio_filter = (
        "highpass=f=70,"
        "acompressor=threshold=0.125:ratio=2.0:attack=5:release=80:makeup=1.5,"
        "loudnorm=I=-16:TP=-1.5:LRA=10,"
        "aresample=48000:first_pts=0,"
        f"apad,atrim=0:{duration:.6f}"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-ss",
            f"{clip.source_start:.6f}",
            "-i",
            str(SOURCE),
            "-t",
            f"{duration:.6f}",
            "-vf",
            source_video_filter(clip),
            "-af",
            audio_filter,
            "-frames:v",
            str(clip.frames),
            *encode_args(),
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "2",
            str(output),
        ]
    )
    return output


def render_video_timeline() -> Path:
    outputs = [render_source_clip(clip) for clip in TIMELINE]
    concat_file = WORK / "concat.txt"
    concat_file.write_text(
        "".join(f"file '{path.resolve()}'\n" for path in outputs),
        encoding="utf-8",
    )
    base = WORK / "base_video.mp4"
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c",
            "copy",
            str(base),
        ]
    )
    return base


def composite_pexels_overlays(base_video: Path) -> Path:
    inputs: list[str] = ["-i", str(base_video)]
    filter_lines: list[str] = []
    current_video = "0:v"
    for index, overlay in enumerate(PEXELS_OVERLAYS, start=1):
        start = overlay.start_frame / FPS
        end = overlay.end_frame / FPS
        duration = overlay.frames / FPS
        inputs.extend(
            [
                "-ss",
                f"{overlay.source_offset:.3f}",
                "-t",
                f"{duration:.3f}",
                "-i",
                str(overlay.asset),
            ]
        )
        insert = f"insert{index}"
        output = f"video{index}"
        if overlay.mode == "fullscreen":
            filter_lines.append(
                f"[{index}:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
                f"crop={WIDTH}:{HEIGHT},eq=contrast=1.05:saturation=0.92:brightness=-0.03,"
                f"fps={FPS},setsar=1,setpts=PTS-STARTPTS+{start:.6f}/TB[{insert}]"
            )
            geometry = "x=0:y=0"
        else:
            filter_lines.append(
                f"[{index}:v]scale=320:569:force_original_aspect_ratio=increase,"
                "crop=320:569,eq=contrast=1.05:saturation=0.92:brightness=-0.03,"
                f"fps={FPS},setsar=1,pad=336:585:8:8:color=0xFFD447,"
                f"setpts=PTS-STARTPTS+{start:.6f}/TB[{insert}]"
            )
            geometry = "x=36:y=920"
        filter_lines.append(
            f"[{current_video}][{insert}]overlay={geometry}:"
            f"eof_action=pass:shortest=0:enable='between(t,{start:.6f},{end:.6f})'"
            f"[{output}]"
        )
        current_video = output

    filter_script = WORK / "pexels_overlay.ffscript"
    filter_script.write_text(";\n".join(filter_lines) + "\n", encoding="utf-8")
    output = WORK / "base_with_evidence.mp4"
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            *inputs,
            "-filter_complex_script",
            str(filter_script),
            "-map",
            f"[{current_video}]",
            "-map",
            "0:a:0",
            "-frames:v",
            str(TOTAL_FRAMES),
            *encode_args(),
            "-c:a",
            "copy",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    return output


def generate_music_and_sfx() -> tuple[Path, Path]:
    music = WORK / "music_bed.wav"
    impact = WORK / "impact.wav"
    music_source = (
        "aevalsrc=(0.075*sin(2*PI*58*t)*(0.30+0.70*exp(-7*mod(t\\,0.5)))+"
        "0.018*sin(2*PI*116*t)+0.008*sin(2*PI*232*t))*"
        f"min(1\\,t/0.8)*min(1\\,({RAW_DURATION:.6f}-t)/0.8):"
        f"s=48000:d={RAW_DURATION:.6f}"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            music_source,
            "-af",
            "lowpass=f=1300,highpass=f=35",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "pcm_s16le",
            str(music),
        ]
    )
    impact_source = (
        "aevalsrc=(0.24*sin(2*PI*(165-95*t)*t)+0.07*sin(2*PI*430*t))*"
        "exp(-11*t):s=48000:d=0.42"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            impact_source,
            "-af",
            "lowpass=f=1900",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "pcm_s16le",
            str(impact),
        ]
    )
    return music, impact


def make_subtitles() -> Path:
    ass = WORK / "captions.ass"
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,Arial,86,&H0047D4FF,&H000000FF,&H00000000,&H8A000000,-1,0,0,0,100,100,0,0,1,7,2,8,55,55,205,1
Style: Caption,Arial,66,&H00FFFFFF,&H000000FF,&H00000000,&H9A000000,-1,0,0,0,100,100,0,0,1,6,2,2,55,55,170,1
Style: Emphasis,Arial,78,&H0047D4FF,&H000000FF,&H00000000,&H9A000000,-1,0,0,0,100,100,0,0,1,7,2,2,50,50,170,1
Style: Editorial,Arial,76,&H0047D4FF,&H000000FF,&H00000000,&HC0000000,-1,0,0,0,100,100,0,0,3,3,0,5,70,70,0,1
Style: Source,Arial,42,&H00A8E64E,&H000000FF,&H00000000,&HA0000000,-1,0,0,0,100,100,0,0,3,2,0,2,90,90,170,1
Style: Citation,Arial,28,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,3,2,0,9,35,35,42,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    for start, end, style, text in CAPTIONS:
        safe_text = text.replace("\n", r"\N")
        animation = ""
        if style in {"Hook", "Emphasis", "Editorial"}:
            animation = r"{\fad(60,70)\t(0,140,\fscx105\fscy105)}"
        lines.append(
            f"Dialogue: 0,{ass_time(start)},{ass_time(end)},{style},,0,0,0,,"
            f"{animation}{safe_text}\n"
        )
    ass.write_text("".join(lines), encoding="utf-8")
    return ass


def mix_raw(base_video: Path, music: Path, impact: Path, subtitles: Path) -> Path:
    filter_lines = [
        "[0:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.03[base]",
        "[1:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.045[music]",
    ]
    impact_frames = [0, 77, 113, 312, 516, 745, 788, 895, 1035, 1193, 1260, 1345]
    split_outputs = "".join(f"[impact{index}]" for index in range(len(impact_frames)))
    filter_lines.append(
        f"[2:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"asplit={len(impact_frames)}{split_outputs}"
    )
    mix_labels = ["[base]", "[music]"]
    for index, frame in enumerate(impact_frames):
        delay = round(frame / FPS * 1000)
        volume = 0.20 if frame == 0 else 0.11
        filter_lines.append(
            f"[impact{index}]adelay={delay}|{delay},volume={volume:.2f}[hit{index}]"
        )
        mix_labels.append(f"[hit{index}]")
    filter_lines.append(
        "".join(mix_labels)
        + f"amix=inputs={len(mix_labels)}:duration=longest:normalize=0,"
        + f"alimiter=limit=0.94:attack=5:release=50,atrim=0:{RAW_DURATION:.6f}[aout]"
    )
    filter_script = WORK / "audio_mix.ffscript"
    filter_script.write_text(";\n".join(filter_lines) + "\n", encoding="utf-8")

    raw_mix = WORK / "raw_mix.mp4"
    subtitle_filter = (
        f"subtitles='{subtitles}':fontsdir='/System/Library/Fonts/Supplemental',"
        f"drawbox=x=0:y=ih-5:w=iw*(t/{RAW_DURATION:.6f}):h=5:color=0xFFD447:t=fill"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(base_video),
            "-i",
            str(music),
            "-i",
            str(impact),
            "-filter_complex_script",
            str(filter_script),
            "-map",
            "0:v:0",
            "-map",
            "[aout]",
            "-vf",
            subtitle_filter,
            "-frames:v",
            str(TOTAL_FRAMES),
            *encode_args(),
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            str(raw_mix),
        ]
    )
    return raw_mix


def finish(raw_mix: Path) -> None:
    finished_video = WORK / "finished_video.mp4"
    finished_audio = WORK / "finished_audio.m4a"
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(raw_mix),
            "-map",
            "0:v:0",
            "-vf",
            finish_video_filter(),
            "-an",
            *encode_args(),
            "-movflags",
            "+faststart",
            str(finished_video),
        ]
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(raw_mix),
            "-map",
            "0:a:0",
            "-vn",
            "-af",
            finish_audio_filter(),
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "2",
            str(finished_audio),
        ]
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(finished_video),
            "-i",
            str(finished_audio),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c",
            "copy",
            "-movflags",
            "+faststart",
            "-shortest",
            str(FINAL),
        ]
    )


def extract_checks() -> None:
    timestamps = [
        0.0,
        0.10,
        0.50,
        1.00,
        1.50,
        2.00,
        3.00,
        4.00,
        5.00,
        6.00,
        7.00,
        8.00,
        9.00,
        10.00,
        12.50,
        15.00,
        18.00,
        21.00,
        24.00,
        27.00,
        30.00,
        33.00,
        36.00,
        39.00,
        42.00,
        45.00,
        46.50,
    ]
    actual_duration = float(probe(FINAL)["format"]["duration"])
    for index, timestamp in enumerate(t for t in timestamps if t < actual_duration):
        output = CHECKS / f"{index:02d}_{timestamp:05.2f}.jpg"
        run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-ss",
                f"{timestamp:.2f}",
                "-i",
                str(FINAL),
                "-frames:v",
                "1",
                "-q:v",
                "2",
                str(output),
            ]
        )
    contact = CHECKS / "contact.jpg"
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(FINAL),
            "-vf",
            "fps=1/2.35,drawtext=fontfile='/System/Library/Fonts/HelveticaNeue.ttc':"
            "text='%{pts\\:hms}':x=10:y=10:fontsize=34:fontcolor=yellow:"
            "borderw=3:bordercolor=black,scale=270:-2:flags=lanczos,"
            "tile=5x4:padding=4:margin=4",
            "-frames:v",
            "1",
            str(contact),
        ]
    )


def validate_output() -> dict[str, Any]:
    info = probe(FINAL)
    video = next(stream for stream in info["streams"] if stream["codec_type"] == "video")
    audio = next(stream for stream in info["streams"] if stream["codec_type"] == "audio")
    duration = float(info["format"]["duration"])
    first_pexels = min(
        overlay.start_frame / FPS / POST_SPEED for overlay in PEXELS_OVERLAYS
    )
    assertions = {
        "width": video["width"] == WIDTH,
        "height": video["height"] == HEIGHT,
        "video_codec": video["codec_name"] == "h264",
        "pixel_format": video["pix_fmt"] == "yuv420p",
        "frame_rate": video["r_frame_rate"] == "30/1",
        "audio_codec": audio["codec_name"] == "aac",
        "audio_sample_rate": audio["sample_rate"] == "48000",
        "audio_channels": audio["channels"] == 2,
        "duration": 45.0 <= duration <= 60.0,
        "source_usage": source_usage_ratio(TIMELINE) <= 0.5,
        "original_voice_only": all(clip.kind == "source" for clip in TIMELINE),
        "first_pexels_after_10s": first_pexels >= 10.0,
    }
    failed = [name for name, passed in assertions.items() if not passed]
    if failed:
        raise AssertionError(f"Validation failed: {failed}\n{json.dumps(info, indent=2)}")

    window_specs = [
        ("hook dialogue", 0.0, 10.0),
        ("funding dialogue", 10.5, 13.0),
        ("scale dialogue", 24.5, 9.0),
        ("rebuild payoff", 34.0, 12.0),
    ]
    volumes = {
        label: assert_not_silent(
            FINAL,
            label=f"final {label}",
            threshold_db=-28.0,
            start=start,
            duration=window_duration,
        )
        for label, start, window_duration in window_specs
    }
    run(["ffmpeg", "-v", "error", "-i", str(FINAL), "-f", "null", "-"])

    report = {
        "output": str(FINAL),
        "duration": duration,
        "resolution": f"{video['width']}x{video['height']}",
        "video_codec": video["codec_name"],
        "pixel_format": video["pix_fmt"],
        "frame_rate": video["r_frame_rate"],
        "audio_codec": audio["codec_name"],
        "audio_sample_rate": audio["sample_rate"],
        "audio_channels": audio["channels"],
        "raw_duration": RAW_DURATION,
        "post_speed": POST_SPEED,
        "source_usage_percent": round(source_usage_ratio(TIMELINE) * 100, 2),
        "original_voice_only": True,
        "first_pexels_final_time": round(first_pexels, 3),
        "hook_caption_final_time": round(HOOK_CAPTIONS[0][0] / POST_SPEED, 3),
        "window_max_volume_db": volumes,
        "decode_check": "passed",
    }
    CHECKS.joinpath("validation.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    CHECKS.joinpath("timeline.json").write_text(
        json.dumps([asdict(clip) for clip in TIMELINE], indent=2) + "\n",
        encoding="utf-8",
    )
    CHECKS.joinpath("evidence_overlays.json").write_text(
        json.dumps(
            [
                {
                    **asdict(overlay),
                    "asset": str(overlay.asset),
                    "raw_start": overlay.start_frame / FPS,
                    "raw_end": overlay.end_frame / FPS,
                    "final_start": overlay.start_frame / FPS / POST_SPEED,
                }
                for overlay in PEXELS_OVERLAYS
            ],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return report


def main() -> None:
    require_inputs()
    base_video = render_video_timeline()
    evidence_video = composite_pexels_overlays(base_video)
    music, impact = generate_music_and_sfx()
    subtitles = make_subtitles()
    raw_mix = mix_raw(evidence_video, music, impact, subtitles)
    finish(raw_mix)
    extract_checks()
    validate_output()


if __name__ == "__main__":
    main()