#!/usr/bin/env python3
"""Render HardKnocks V8: Logan Paul's delayed platform-fit story.

The edit keeps the original School of Hard Knocks interview voice while
rebuilding sixteen short excerpts into rejection, deliberate practice,
platform fit, and business-payoff beats. Active-speaker reframing hard-cuts
between the host and Logan; semantic zoom reserves close framing for numbers,
confessions, and punchlines. Archive footage, an official PRIME commercial,
Pexels illustration, progressive captions, and persistent citations make the
edit independently useful and auditable.
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
SOURCE = PROJECT / "source" / "ALvduf2Rz_c.mp4"
EVIDENCE_DIR = PROJECT / "source" / "evidence"
CHILDHOOD_ARCHIVE = EVIDENCE_DIR / "logan_childhood_home_R9ve03SbYqg.mp4"
VINE_ARCHIVE = EVIDENCE_DIR / "logan_vines_cXNLpsB4zw4.mp4"
PRIME_COMMERCIAL = EVIDENCE_DIR / "prime_commercial_ebha0MzwtU8.mp4"
PEXELS_PARTNERS = ROOT / "output/shared/pexels/contract_signing_7981954.mp4"
WORK = PROJECT / "clips" / "v8_work"
PANELS = WORK / "panels"
CHECKS = WORK / "checks"
FINAL = PROJECT / "final" / "2026-07-16-hardknocks_v8_logan_platform_fit.mp4"

WIDTH = 1080
HEIGHT = 1920
FPS = 30
POST_SPEED = 1.03
FINISH_PAD = 0.70
AUDIO_FINISH_PAD = 0.70
SOURCE_DURATION = 956.383492

FONT_REGULAR = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")


@dataclass(frozen=True)
class TimelineClip:
    name: str
    start_frame: int
    frames: int
    kind: str
    source_start: float
    crop_focus: float
    zoom: float
    speaker: str
    framing: str

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
    speaker: str
    framing: str


@dataclass(frozen=True)
class EvidenceOverlay:
    name: str
    start_frame: int
    frames: int
    source_offset: float
    asset: Path
    mode: str
    crop_focus: float = 0.5

    @property
    def end_frame(self) -> int:
        return self.start_frame + self.frames


def build_timeline() -> list[TimelineClip]:
    plans = [
        ClipPlan("weird_hook", 88, 776.36, 0.36, 1.36, "logan", "close"),
        ClipPlan("overnight_question", 174, 756.02, 0.70, 1.20, "host", "medium"),
        ClipPlan("started_at_nine", 200, 761.84, 0.36, 1.20, "logan", "medium"),
        ClipPlan("not_a_job", 80, 768.58, 0.36, 1.36, "logan", "close"),
        ClipPlan("nine_ten_years", 131, 779.28, 0.36, 1.20, "logan", "medium"),
        ClipPlan("ten_thousand_hours", 148, 783.70, 0.36, 1.36, "logan", "close"),
        ClipPlan("goosebumps_work", 76, 788.64, 0.36, 1.36, "logan", "close"),
        ClipPlan("vine_setup", 131, 791.64, 0.36, 1.20, "logan", "medium"),
        ClipPlan("six_second_fit", 113, 796.00, 0.36, 1.36, "logan", "close"),
        ClipPlan("personal_question", 95, 802.12, 0.70, 1.20, "host", "medium"),
        ClipPlan("thirty_million", 44, 810.42, 0.36, 1.36, "logan", "close"),
        ClipPlan("company_question", 58, 812.72, 0.70, 1.20, "host", "medium"),
        ClipPlan("prime_billion", 68, 815.96, 0.36, 1.36, "logan", "close"),
        ClipPlan("scale_question", 59, 818.30, 0.70, 1.36, "host", "close"),
        ClipPlan("great_partners", 43, 820.40, 0.36, 1.36, "logan", "close"),
        ClipPlan("influencer_value", 154, 822.14, 0.36, 1.20, "logan", "medium"),
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
                speaker=plan.speaker,
                framing=plan.framing,
            )
        )
        cursor += plan.frames
    return timeline


TIMELINE = build_timeline()
TOTAL_FRAMES = TIMELINE[-1].end_frame
RAW_DURATION = TOTAL_FRAMES / FPS

# Full-screen evidence begins at raw 10.40s / final 10.10s, outside the
# protected 0-10s face window. Original interview audio remains intact.
EVIDENCE_OVERLAYS = (
    EvidenceOverlay("childhood_home", 312, 96, 160.4, CHILDHOOD_ARCHIVE, "topcrop", 0.65),
    EvidenceOverlay("childhood_brothers", 408, 66, 164.0, CHILDHOOD_ARCHIVE, "topcrop", 0.28),
    EvidenceOverlay("vine_archive", 936, 90, 13.2, VINE_ARCHIVE, "topcrop", 0.42),
    EvidenceOverlay("prime_product", 1338, 90, 0.0, PRIME_COMMERCIAL, "fullscreen"),
    EvidenceOverlay("partner_handshake", 1508, 90, 2.0, PEXELS_PARTNERS, "fullscreen"),
)

# First caption appears at raw t=0.10s while Logan is already moving.
HOOK_CAPTIONS = [
    (0.10, 2.13, "YOU GUYS ARE WEIRD"),
    (2.13, 2.93, "BUT WE LOVED IT"),
    (2.93, 5.30, "SUCCESS NOW"),
    (5.30, 6.85, "OVERNIGHT?"),
    (6.85, 8.73, "HOW LONG BEFORE MONEY?"),
]

CAPTIONS = [
    *[(start, end, "Hook", text) for start, end, text in HOOK_CAPTIONS],
    (8.73, 9.67, "Caption", "THAT'S THE QUESTION"),
    (9.67, 12.15, "Emphasis", "STARTED AT 9"),
    (12.15, 15.40, "Caption", "NEW SITE: YOUTUBE"),
    (15.40, 18.07, "Editorial", "YOUTUBER WASN'T A JOB"),
    (18.07, 20.40, "Emphasis", "9-10 YEARS"),
    (20.40, 22.43, "Caption", "BEFORE VINE"),
    (22.43, 25.10, "Emphasis", "10,000 HOURS"),
    (25.10, 27.37, "Caption", "BEFORE THE RIGHT MEDIUM"),
    (27.37, 28.80, "Caption", "I'M GETTING GOOSEBUMPS"),
    (28.80, 29.90, "Editorial", "WE PUT IN THE WORK"),
    (29.90, 32.00, "Caption", "THEN VINE APPEARED"),
    (32.00, 34.27, "Editorial", "THE FORMAT FINALLY FIT"),
    (34.27, 36.10, "Emphasis", "6-SECOND LOOPS"),
    (36.10, 38.03, "Editorial", "GOOD. FAST."),
    (38.03, 41.20, "Caption", "MOST MONEY IN ONE YEAR?"),
    (41.20, 42.67, "Emphasis", "ABOUT $30 MILLION"),
    (42.67, 44.60, "Caption", "WHAT ABOUT YOUR COMPANIES?"),
    (44.60, 46.87, "Emphasis", "PRIME: $1.2 BILLION"),
    (46.87, 48.83, "Caption", "HOW DID YOU SCALE?"),
    (48.83, 50.27, "Emphasis", "GREAT PARTNERS"),
    (50.27, 52.80, "Caption", "THEY UNDERSTOOD INFLUENCE"),
    (52.80, RAW_DURATION, "Editorial", "THEN BUILT A BRAND"),
    (10.40, RAW_DURATION, "Citation", "SOURCE: SCHOOL OF HARD KNOCKS"),
    (10.40, 15.80, "Archive", "ARCHIVE: GRAHAM BENSINGER"),
    (31.20, 34.20, "Archive", "ARCHIVE: ODDLY SATISFYING MOTION"),
    (44.60, 47.60, "Archive", "SOURCE: LOGAN PAUL / PRIME"),
    (50.27, 53.27, "Archive", "ILLUSTRATION: PEXELS"),
]


def tts_lines() -> list:
    return []


def source_usage_ratio(timeline: list[TimelineClip]) -> float:
    source_seconds = sum(clip.frames for clip in timeline if clip.kind == "source") / FPS
    return source_seconds / SOURCE_DURATION


def evidence_usage_ratio() -> float:
    return sum(overlay.frames for overlay in EVIDENCE_OVERLAYS) / TOTAL_FRAMES


def final_duration() -> float:
    return (RAW_DURATION + FINISH_PAD) / POST_SPEED


def finish_audio_filter() -> str:
    audio_duration = RAW_DURATION / POST_SPEED + AUDIO_FINISH_PAD
    return (
        f"atempo={POST_SPEED},apad=pad_dur={AUDIO_FINISH_PAD:.2f},"
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
        if clip.speaker not in {"host", "logan"}:
            raise ValueError(f"invalid speaker: {clip.name}")
        if clip.framing not in {"medium", "close"}:
            raise ValueError(f"invalid framing: {clip.name}")
        cursor = clip.end_frame
    if cursor != total_frames:
        raise ValueError(f"timeline total mismatch: {cursor} != {total_frames}")
    if source_usage_ratio(timeline) > 0.5:
        raise ValueError("source usage exceeds 50%")
    if not 45.0 <= final_duration() <= 60.0:
        raise ValueError(f"final duration out of range: {final_duration():.3f}s")
    if not 0.25 <= evidence_usage_ratio() <= 0.35:
        raise ValueError(f"evidence ratio out of range: {evidence_usage_ratio():.3f}")
    for overlay in EVIDENCE_OVERLAYS:
        if overlay.start_frame / FPS / POST_SPEED < 10.0:
            raise ValueError(f"evidence enters protected face window: {overlay.name}")
        if overlay.frames <= 0 or overlay.end_frame > total_frames:
            raise ValueError(f"invalid evidence window: {overlay.name}")
        if overlay.mode not in {"fullscreen", "topcrop"}:
            raise ValueError(f"invalid evidence mode: {overlay.mode}")
        if not 0.0 <= overlay.crop_focus <= 1.0:
            raise ValueError(f"invalid evidence crop focus: {overlay.name}")


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
    required = [
        SOURCE,
        CHILDHOOD_ARCHIVE,
        VINE_ARCHIVE,
        PRIME_COMMERCIAL,
        PEXELS_PARTNERS,
        FONT_REGULAR,
        FONT_BOLD,
    ]
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
        f"crop={WIDTH}:{HEIGHT}:(in_w-{WIDTH})/2:0,"
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


def render_evidence_excerpt(overlay: EvidenceOverlay, index: int) -> Path:
    """Decode an external excerpt with accurate post-input seeking.

    Fast pre-input seeking can land on the wrong AV1 keyframe in the evidence
    downloads. Post-input ``-ss`` is slower but frame-accurate and keeps the
    archive selection auditable. ``topcrop`` adds a mild top-aligned punch-in
    that removes compilation subtitles/watermarks near the source bottom.
    """
    output = WORK / f"evidence_{index:02d}_{overlay.name}.mp4"
    duration = overlay.frames / FPS
    if overlay.mode == "topcrop":
        video_filter = (
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={WIDTH}:{HEIGHT}:(in_w-{WIDTH})*{overlay.crop_focus:.3f}:0,"
            "scale=1210:2150:flags=lanczos,"
            f"crop={WIDTH}:{HEIGHT}:(in_w-{WIDTH})/2:0,"
            "eq=contrast=1.05:saturation=0.94:brightness=-0.02,"
            f"fps={FPS},setsar=1,format=yuv420p"
        )
    else:
        video_filter = (
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={WIDTH}:{HEIGHT},"
            "eq=contrast=1.05:saturation=0.94:brightness=-0.02,"
            f"fps={FPS},setsar=1,format=yuv420p"
        )
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(overlay.asset),
            "-ss",
            f"{overlay.source_offset:.3f}",
            "-t",
            f"{duration:.3f}",
            "-vf",
            video_filter,
            "-an",
            "-frames:v",
            str(overlay.frames),
            *encode_args(),
            str(output),
        ]
    )
    return output


def composite_evidence_overlays(base_video: Path) -> Path:
    inputs: list[str] = ["-i", str(base_video)]
    filter_lines: list[str] = []
    current_video = "0:v"
    for index, overlay in enumerate(EVIDENCE_OVERLAYS, start=1):
        start = overlay.start_frame / FPS
        end = overlay.end_frame / FPS
        excerpt = render_evidence_excerpt(overlay, index)
        inputs.extend(["-i", str(excerpt)])
        insert = f"insert{index}"
        output = f"video{index}"
        filter_lines.append(
            f"[{index}:v]fps={FPS},setsar=1,"
            f"setpts=PTS-STARTPTS+{start:.6f}/TB[{insert}]"
        )
        filter_lines.append(
            f"[{current_video}][{insert}]overlay=x=0:y=0:"
            f"eof_action=pass:shortest=0:enable='between(t,{start:.6f},{end:.6f})'"
            f"[{output}]"
        )
        current_video = output

    filter_script = WORK / "evidence_overlay.ffscript"
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
        "aevalsrc=(0.070*sin(2*PI*58*t)*(0.30+0.70*exp(-7*mod(t\\,0.5)))+"
        "0.016*sin(2*PI*116*t)+0.007*sin(2*PI*232*t))*"
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
Style: Caption,Arial,66,&H00FFFFFF,&H000000FF,&H00000000,&H9A000000,-1,0,0,0,100,100,0,0,1,6,2,2,55,55,190,1
Style: Emphasis,Arial,78,&H0047D4FF,&H000000FF,&H00000000,&H9A000000,-1,0,0,0,100,100,0,0,1,7,2,2,50,50,190,1
Style: Editorial,Arial,72,&H0047D4FF,&H000000FF,&H00000000,&HC0000000,-1,0,0,0,100,100,0,0,3,3,0,5,70,70,0,1
Style: Citation,Arial,26,&H00FFFFFF,&H000000FF,&H00000000,&HA0000000,-1,0,0,0,100,100,0,0,3,2,0,9,35,35,42,1
Style: Archive,Arial,24,&H00FFFFFF,&H000000FF,&H00000000,&HA0000000,-1,0,0,0,100,100,0,0,3,2,0,7,35,35,42,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    for start, end, style, text in CAPTIONS:
        safe_text = text.replace("\n", r"\N")
        animation = ""
        if style in {"Hook", "Emphasis", "Editorial"}:
            animation = r"{\fad(60,70)\t(0,140,\fscx105\fscy105)}"
        layer = 2 if style in {"Citation", "Archive"} else 3
        lines.append(
            f"Dialogue: {layer},{ass_time(start)},{ass_time(end)},{style},,0,0,0,,"
            f"{animation}{safe_text}\n"
        )
    ass.write_text("".join(lines), encoding="utf-8")
    return ass


def mix_raw(base_video: Path, music: Path, impact: Path, subtitles: Path) -> Path:
    filter_lines = [
        "[0:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.03[base]",
        "[1:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.043[music]",
    ]
    impact_frames = [0, 542, 673, 1028, 1236, 1338, 1465]
    split_outputs = "".join(f"[impact{index}]" for index in range(len(impact_frames)))
    filter_lines.append(
        f"[2:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"asplit={len(impact_frames)}{split_outputs}"
    )
    mix_labels = ["[base]", "[music]"]
    for index, frame in enumerate(impact_frames):
        delay = round(frame / FPS * 1000)
        volume = 0.18 if frame == 0 else 0.10
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
        10.50,
        12.00,
        14.00,
        16.00,
        18.00,
        21.50,
        24.00,
        27.00,
        30.00,
        32.00,
        34.00,
        37.00,
        40.00,
        42.00,
        44.00,
        46.00,
        48.00,
        50.00,
        52.00,
        54.00,
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
            "fps=1/2.70,drawtext=fontfile='/System/Library/Fonts/HelveticaNeue.ttc':"
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
    first_evidence = min(
        overlay.start_frame / FPS / POST_SPEED for overlay in EVIDENCE_OVERLAYS
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
        "evidence_usage": 0.25 <= evidence_usage_ratio() <= 0.35,
        "original_voice_only": all(clip.kind == "source" for clip in TIMELINE),
        "first_fullscreen_evidence_after_10s": first_evidence >= 10.0,
    }
    failed = [name for name, passed in assertions.items() if not passed]
    if failed:
        raise AssertionError(f"Validation failed: {failed}\n{json.dumps(info, indent=2)}")

    window_specs = [
        ("hook dialogue", 0.0, 9.0),
        ("practice dialogue", 17.0, 12.0),
        ("money payoff", 39.5, 9.0),
        ("partner close", 48.5, 5.0),
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
        "evidence_usage_percent": round(evidence_usage_ratio() * 100, 2),
        "original_voice_only": True,
        "first_fullscreen_evidence_final_time": round(first_evidence, 3),
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
                for overlay in EVIDENCE_OVERLAYS
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
    evidence_video = composite_evidence_overlays(base_video)
    music, impact = generate_music_and_sfx()
    subtitles = make_subtitles()
    raw_mix = mix_raw(evidence_video, music, impact, subtitles)
    finish(raw_mix)
    extract_checks()
    validate_output()


if __name__ == "__main__":
    main()
