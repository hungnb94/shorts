#!/usr/bin/env python3
"""Render the 58-second Capytech V9 real-drop base master.

This renderer consumes original master sources plus the approved preflight
interval/crop manifest. The 270x480 preflight crops are never render inputs.
Citations and comparison value-adds belong to the separate compositor.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
STORYBOARD = ROOT / "output/projects/capytech/scripts/capytech_v9_real_drop_storyboard.json"
PREFLIGHT = ROOT / "output/projects/capytech/analysis/v9_real_drop_qc/preflight"
SOURCE_MANIFEST = PREFLIGHT / "source_crop_manifest.json"
REACTION_GATE = PREFLIGHT / "reaction_blind_test.json"
TTS_MANIFEST = ROOT / "output/projects/capytech/clips/capytech_v9_real_drop_work/audio/tts_manifest.json"
PEXELS = ROOT / "output/projects/capytech/source/v9_real_drop/pexels/36460444_aerial_city.mp4"
WORK = ROOT / "output/projects/capytech/clips/capytech_v9_real_drop_work"
SEGMENTS = WORK / "segments"
TRACKS = WORK / "audio/tracks"
ASS_PATH = WORK / "captions.ass"
VISUAL = WORK / "visual_master.mp4"
AUDIO_RAW = WORK / "audio/base_mix_raw.wav"
AUDIO_FINAL = WORK / "audio/base_mix_normalized.wav"
BASE_MASTER = WORK / "base_master.mp4"
RENDER_MANIFEST = WORK / "render_manifest.json"
SOURCE_USAGE = ROOT / "output/projects/capytech/analysis/v9_real_drop_qc/source_usage.json"
FONT = ROOT / "assets/fonts/Komika-Axis.ttf"
CALIBRATION = ROOT / "docs/verification/caption-calibration/caption-profile.json"
DURATION = 58.0
FPS = 30
RATE = 48_000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command, cwd=ROOT, check=True, text=True, capture_output=capture
    )


def require_hash(path: Path, expected: str, label: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    actual = sha256(path)
    if actual != expected:
        raise RuntimeError(f"{label} hash mismatch: {actual} != {expected}")


def probe(path: Path) -> dict[str, Any]:
    return json.loads(
        run(
            [
                "ffprobe", "-v", "error", "-show_streams", "-show_format",
                "-of", "json", str(path),
            ],
            capture=True,
        ).stdout
    )


def ass_time(seconds: float) -> str:
    centiseconds = round(seconds * 100)
    hours, remainder = divmod(centiseconds, 360_000)
    minutes, remainder = divmod(remainder, 6_000)
    secs, hundredths = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{hundredths:02d}"


def ass_escape(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def caption_bursts(tts: dict[str, Any]) -> list[dict[str, Any]]:
    bursts: list[dict[str, Any]] = []
    for line in tts["lines"]:
        offset = float(line["window"][0])
        words = line["asr"]["words"]
        for start_index in range(0, len(words), 4):
            group = words[start_index:start_index + 4]
            if len(group) == 1 and bursts:
                previous = bursts.pop()
                group = previous["words"] + group
                start = previous["start"]
            else:
                start = offset + float(group[0]["start"])
            end = offset + float(group[-1]["end"]) + 0.08
            bursts.append({"start": start, "end": min(end, DURATION), "words": group})
    return bursts


def write_ass(tts: dict[str, Any]) -> list[dict[str, Any]]:
    # Font size/position are derived for the native 1080x1920 canvas. The
    # checked-in calibration file is hash-bound below; literal CapCut units are
    # never used.
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Caption,Komika Axis,82,&H00FFFFFF,&H0000D7FF,&H00201812,&H80000000,0,0,0,0,100,100,1,0,1,6,2,2,70,70,800,1
Style: Hook,Komika Axis,88,&H00FFFFFF,&H0000D7FF,&H00201812,&H80000000,0,0,0,0,100,100,1,0,1,7,2,5,60,60,710,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    events = [
        "Dialogue: 2,0:00:00.00,0:00:00.80,Hook,,0,0,0,,{\\fad(0,80)\\t(0,180,\\fscx108\\fscy108)}1,000 FT DROP",
        "Dialogue: 2,0:00:00.80,0:00:01.60,Hook,,0,0,0,,{\\c&H00D7FF&\\t(0,180,\\fscx108\\fscy108)}300 FT: SPLIT",
        "Dialogue: 2,0:00:01.60,0:00:02.40,Hook,,0,0,0,,{\\t(0,180,\\fscx108\\fscy108)}BUT THIS ONE...",
        "Dialogue: 2,0:00:02.40,0:00:03.00,Hook,,0,0,0,,{\\c&H00D7FF&\\t(0,180,\\fscx110\\fscy110)}STILL WORKED?!",
    ]
    bursts = caption_bursts(tts)
    for burst in bursts:
        words = burst["words"]
        visible = "".join(word["word"] for word in words).strip()
        tokens = re.findall(r"\S+", visible)
        if not tokens:
            continue
        emphasis = max(range(len(tokens)), key=lambda i: len(re.sub(r"\W", "", tokens[i])))
        styled = []
        for index, token in enumerate(tokens):
            if index == emphasis:
                styled.append(
                    r"{\c&H00D7FF&\b1\t(0,140,\fscx112\fscy112)}"
                    + ass_escape(token)
                    + r"{\rCaption}"
                )
            else:
                styled.append(ass_escape(token))
        events.append(
            f"Dialogue: 2,{ass_time(burst['start'])},{ass_time(burst['end'])},"
            f"Caption,,0,0,0,,{' '.join(styled)}"
        )
    ASS_PATH.parent.mkdir(parents=True, exist_ok=True)
    ASS_PATH.write_text(header + "\n".join(events) + "\n")
    return bursts


def focus_at(points: list[dict[str, Any]], at: float) -> float:
    if at <= float(points[0]["time_seconds"]):
        return float(points[0]["horizontal_focus_normalized"])
    for left, right in zip(points, points[1:]):
        left_at = float(left["time_seconds"])
        right_at = float(right["time_seconds"])
        if at <= right_at:
            ratio = (at - left_at) / (right_at - left_at)
            return float(left["horizontal_focus_normalized"]) + ratio * (
                float(right["horizontal_focus_normalized"])
                - float(left["horizontal_focus_normalized"])
            )
    return float(points[-1]["horizontal_focus_normalized"])


def dynamic_cover_filter(record: dict[str, Any], duration: float, offset: float) -> str:
    approved_points = record["focus_trajectory"]
    points = [
        {"time_seconds": 0.0, "horizontal_focus_normalized": focus_at(approved_points, offset)}
    ]
    points.extend(
        {
            "time_seconds": float(point["time_seconds"]) - offset,
            "horizontal_focus_normalized": float(point["horizontal_focus_normalized"]),
        }
        for point in approved_points
        if offset < float(point["time_seconds"]) < offset + duration
    )
    points.append(
        {
            "time_seconds": duration,
            "horizontal_focus_normalized": focus_at(approved_points, offset + duration),
        }
    )
    terms: list[str] = []
    for index, point in enumerate(points):
        at = float(point["time_seconds"])
        focus = float(point["horizontal_focus_normalized"])
        if index == len(points) - 1:
            terms.append(str(focus))
            break
        next_point = points[index + 1]
        next_at = float(next_point["time_seconds"])
        next_focus = float(next_point["horizontal_focus_normalized"])
        slope = (next_focus - focus) / (next_at - at)
        terms.append(f"if(lt(t,{next_at}),({focus}+({slope})*(t-{at})),")
    focus_expr = "".join(terms) + ")" * (len(points) - 1)
    return (
        "fps=30,setpts=PTS-STARTPTS,"
        "scale=-2:1920,"
        f"crop=1080:1920:x='clip(({focus_expr})*iw-540,0,iw-1080)':y=0,"
        f"trim=duration={duration},setpts=PTS-STARTPTS,setsar=1"
    )


def full_width_filter(duration: float) -> str:
    return (
        "[0:v]fps=30,setpts=PTS-STARTPTS,split=2[bg][fg];"
        "[bg]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,boxblur=36:3[blur];"
        "[fg]scale=1080:1920:force_original_aspect_ratio=decrease[fit];"
        f"[blur][fit]overlay=(W-w)/2:(H-h)/2,trim=duration={duration},"
        "setpts=PTS-STARTPTS,setsar=1[v]"
    )


def render_source_segment(
    name: str,
    record: dict[str, Any],
    offset: float,
    duration: float,
) -> Path:
    source = ROOT / record["source_path"]
    approved_start, approved_end = map(float, record["source_interval_local_seconds"])
    start = approved_start + offset
    if start < approved_start or start + duration > approved_end + 1e-6:
        raise RuntimeError(f"{name} exceeds approved source interval")
    destination = SEGMENTS / f"{name}.mkv"
    if record["crop_mode"] == "portrait_cover_dynamic":
        video_filter = dynamic_cover_filter(record, duration, offset)
        if name == "thousand_real_b":
            video_filter += ",scale=1458:2592,crop=1080:1920:(iw-1080)/2:(ih-1920)/2"
        elif name == "thousand_real_c":
            video_filter += (
                ",scale=1728:3072,"
                "crop=1080:1920:x='(iw-1080)/2+10*sin(24*t)':"
                "y='(ih-1920)/2+8*cos(21*t)'"
            )
        command = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", str(start), "-t", str(duration), "-i", str(source),
            "-vf", video_filter, "-an",
            "-c:v", "ffv1", "-level", "3", "-pix_fmt", "yuv420p", str(destination),
        ]
    else:
        command = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", str(start), "-t", str(duration), "-i", str(source),
            "-filter_complex", full_width_filter(duration), "-map", "[v]", "-an",
            "-c:v", "ffv1", "-level", "3", "-pix_fmt", "yuv420p", str(destination),
        ]
    run(command)
    return destination


def render_pexels_segment(name: str, start: float, duration: float) -> Path:
    destination = SEGMENTS / f"{name}.mkv"
    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", str(start), "-t", str(duration), "-i", str(PEXELS),
            "-vf",
            f"fps=30,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,trim=duration={duration},setpts=PTS-STARTPTS,setsar=1",
            "-an", "-c:v", "ffv1", "-level", "3", "-pix_fmt", "yuv420p", str(destination),
        ]
    )
    return destination


def audio_track(
    source: Path,
    source_start: float,
    clip_duration: float,
    final_start: float,
    destination: Path,
    active_filter: str,
) -> Path:
    """Create actual leading-silence samples, never timestamp-only delay."""
    tail = DURATION - final_start - clip_duration
    if tail < -1e-6:
        raise RuntimeError(f"Audio track exceeds timeline: {destination.name}")
    graph = (
        f"[0:a]atrim=start={source_start}:duration={clip_duration},asetpts=PTS-STARTPTS,"
        f"{active_filter},afade=t=in:st=0:d=0.12,"
        f"afade=t=out:st={max(0.0, clip_duration - 0.20)}:d=0.20[active];"
        f"anullsrc=r={RATE}:cl=stereo:d={final_start}[lead];"
        f"[lead][active]concat=n=2:v=0:a=1,apad,atrim=duration={DURATION},"
        "asetpts=PTS-STARTPTS[out]"
    )
    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
            "-filter_complex", graph, "-map", "[out]", "-ar", str(RATE), "-ac", "2",
            "-c:a", "pcm_s16le", str(destination),
        ]
    )
    return destination


def lavfi_event(name: str, at: float, duration: float, frequency: int) -> Path:
    destination = TRACKS / f"sfx_{name}.wav"
    tail = DURATION - at - duration
    if tail < 0:
        raise RuntimeError(f"SFX {name} exceeds timeline")
    graph = (
        f"sine=frequency={frequency}:sample_rate={RATE}:duration={duration},"
        "aformat=sample_fmts=s16:channel_layouts=stereo,"
        "afade=t=in:st=0:d=0.01,"
        f"afade=t=out:st={max(0.0, duration - 0.10)}:d=0.10,"
        "volume=0.20,acompressor=threshold=0.1:ratio=4,"
        "loudnorm=I=-20:TP=-2:LRA=8[active];"
        f"anullsrc=r={RATE}:cl=stereo:d={at}[lead];"
        f"[lead][active]concat=n=2:v=0:a=1,apad,atrim=duration={DURATION}[out]"
    )
    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-filter_complex", graph, "-map", "[out]", "-c:a", "pcm_s16le",
            "-ar", str(RATE), "-ac", "2", str(destination),
        ]
    )
    return destination


def lavfi_bed() -> Path:
    """Create a restrained continuous tonal bed so edit gaps never become dropouts."""
    destination = TRACKS / "continuous_bed.wav"
    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", f"sine=frequency=82:sample_rate={RATE}:duration={DURATION}",
            "-f", "lavfi", "-i", f"sine=frequency=123:sample_rate={RATE}:duration={DURATION}",
            "-filter_complex",
            "[0:a]volume=0.055[low];[1:a]volume=0.035[high];"
            "[low][high]amix=inputs=2:duration=longest:normalize=0,"
            "lowpass=f=1600,afade=t=in:st=0:d=0.20,afade=t=out:st=57.5:d=0.50,"
            "aformat=channel_layouts=stereo,atrim=duration=58[out]",
            "-map", "[out]", "-ar", str(RATE), "-ac", "2", "-c:a", "pcm_s16le",
            str(destination),
        ]
    )
    return destination


def validate_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    for executable in ("ffmpeg", "ffprobe"):
        if shutil.which(executable) is None:
            raise RuntimeError(f"Required executable unavailable: {executable}")
    for path in (STORYBOARD, SOURCE_MANIFEST, REACTION_GATE, TTS_MANIFEST, PEXELS, FONT, CALIBRATION):
        if not path.is_file():
            raise FileNotFoundError(path)
    storyboard = json.loads(STORYBOARD.read_text())
    source_manifest = json.loads(SOURCE_MANIFEST.read_text())
    reactions = json.loads(REACTION_GATE.read_text())
    tts = json.loads(TTS_MANIFEST.read_text())
    if storyboard["duration_seconds"] != DURATION:
        raise RuntimeError("Storyboard duration contract changed")
    if storyboard["truthful_labels_exact"] != [
        "WAIST HEIGHT", "10 STORIES", "300 FEET", "1,000 FEET"
    ]:
        raise RuntimeError("Truthful label contract changed")
    for binding in storyboard["bindings"].values():
        require_hash(ROOT / binding["path"], binding["sha256"], binding["path"])
    require_hash(STORYBOARD, tts["storyboard_sha256"], "TTS storyboard")
    expected_lines = {line["id"]: line for line in storyboard["tts_contract"]["lines"]}
    actual_lines = {line["id"]: line for line in tts["lines"]}
    if expected_lines.keys() != actual_lines.keys():
        raise RuntimeError("TTS manifest is incomplete")
    for line_id, expected in expected_lines.items():
        actual = actual_lines[line_id]
        if actual["source_text"] != expected["text"]:
            raise RuntimeError(f"TTS text mismatch: {line_id}")
        require_hash(ROOT / actual["path"], actual["sha256"], f"TTS {line_id}")
    for source in source_manifest["sources"]:
        require_hash(ROOT / source["local_mp4_path"], source["local_mp4_sha256"], source["youtube_id"])
        require_hash(ROOT / source["info_json_path"], source["info_json_sha256"], source["youtube_id"])
    pexels_record = source_manifest["pexels_acquisition_record"]
    require_hash(ROOT / pexels_record["asset_path"], pexels_record["asset_sha256"], "Pexels asset")
    for candidate in reactions["candidates"].values():
        require_hash(ROOT / candidate["path"], candidate["sha256"], "reaction sprite")
    return storyboard, source_manifest, reactions, tts


def main() -> None:
    storyboard, source_manifest, reactions, tts = validate_inputs()
    SEGMENTS.mkdir(parents=True, exist_ok=True)
    TRACKS.mkdir(parents=True, exist_ok=True)
    records = {record["id"]: record for record in source_manifest["crop_previews"]}

    # Each output segment is rendered directly from the approved original master.
    # The final round deliberately alternates setup, release, a clearly separated
    # Pexels illustration, real tracked fall/impact, and the powered result.
    plan = [
        ("hook_host", "thousand_action", 0.0, 0.8, 0.0, 0.8),
        ("hook_split", "three_hundred_result", 0.0, 0.8, 0.8, 1.6),
        ("hook_aerial", "thousand_action", 9.0, 0.8, 1.6, 2.4),
        ("hook_powered", "thousand_result", 2.5, 0.6, 2.4, 3.0),
        ("waist_action", "waist_action", 0.0, 5.0, 3.0, 8.0),
        ("waist_result", "waist_result", 0.0, 3.0, 8.0, 11.0),
        ("ten_action", "ten_stories_action", 0.0, 7.0, 11.0, 18.0),
        ("ten_result", "ten_stories_result", 0.0, 4.0, 18.0, 22.0),
        ("three_action", "three_hundred_action", 0.0, 7.0, 22.0, 29.0),
        ("three_result", "three_hundred_result", 0.0, 5.0, 29.0, 34.0),
        ("thousand_setup", "thousand_action", 0.0, 2.0, 34.0, 36.0),
        ("thousand_release", "thousand_action", 8.0, 2.0, 36.0, 38.0),
        ("thousand_real_a", "thousand_action", 9.0, 4.0, 40.0, 44.0),
        ("thousand_real_b", "thousand_action", 11.0, 3.0, 44.0, 47.0),
        ("thousand_real_c", "thousand_action", 12.0, 2.0, 47.0, 49.0),
        ("thousand_result", "thousand_result", 0.0, 6.5, 49.0, 55.5),
        ("thousand_result_tail", "thousand_result", 4.5, 0.5, 55.5, 56.0),
        ("loop_host", "thousand_action", 0.0, 2.0, 56.0, 58.0),
    ]
    visual_parts: list[Path] = []
    usage: list[dict[str, Any]] = []
    audio_tracks: list[Path] = []
    for name, crop_id, offset, duration, final_start, final_end in plan:
        record = records[crop_id]
        visual_parts.append(render_source_segment(name, record, offset, duration))
        original_start = float(record["source_interval_original_seconds"][0]) + offset
        usage.append(
            {
                "kind": "youtube",
                "video_id": record["youtube_id"],
                "crop_id": crop_id,
                "original_start": round(original_start, 3),
                "original_end": round(original_start + duration, 3),
                "final_start": final_start,
                "final_end": final_end,
                "audio_use": "muted_source_audio",
            }
        )
        # Source speech is fully muted in the timeline. The only intentional
        # source quote is rebuilt separately below; Qwen commentary, designed
        # SFX and the continuous bed carry the rest of the mix.
        source_path = ROOT / record["source_path"]
        stream_probe = probe(source_path)
        if any(stream.get("codec_type") == "audio" for stream in stream_probe["streams"]):
            track = TRACKS / f"source_{name}.wav"
            local_start = float(record["source_interval_local_seconds"][0]) + offset
            audio_tracks.append(
                audio_track(
                    source_path, local_start, duration, final_start, track,
                    "aresample=48000,aformat=channel_layouts=stereo,volume=0.0",
                )
            )

    pexels_part = render_pexels_segment("thousand_illustration", 0.0, 2.0)
    visual_parts.insert(12, pexels_part)
    usage.insert(
        12,
        {
            "kind": "pexels_illustration",
            "asset_id": 36460444,
            "original_start": 0.0,
            "original_end": 2.0,
            "final_start": 38.0,
            "final_end": 40.0,
            "audio_use": "none",
            "required_label": "ILLUSTRATION",
        },
    )

    concat_list = WORK / "visual_concat.txt"
    concat_list.write_text(
        "".join(f"file '{path.resolve()}'\n" for path in visual_parts)
    )
    raw_visual = WORK / "visual_unadorned.mkv"
    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-an", "-c:v", "ffv1", "-level", "3", "-pix_fmt", "yuv420p",
            "-t", str(DURATION), str(raw_visual),
        ]
    )

    bursts = write_ass(tts)
    sprites = {
        "smug": ROOT / reactions["candidates"]["arms_crossed_smug"]["path"],
        "shield": ROOT / reactions["candidates"]["crouched_one_arm_shield_sweat"]["path"],
        "panic": ROOT / reactions["candidates"]["both_paws_on_head_panic"]["path"],
        "stumble": ROOT / reactions["candidates"]["jaw_drop_backward_stumble"]["path"],
    }
    inputs = ["-i", str(raw_visual)]
    for sprite in sprites.values():
        inputs.extend(["-loop", "1", "-t", str(DURATION), "-i", str(sprite)])
    ass_value = str(ASS_PATH).replace("\\", r"\\").replace(":", r"\:")
    font_dir = str(FONT.parent).replace("\\", r"\\").replace(":", r"\:")
    filter_graph = (
        f"[0:v]subtitles='{ass_value}':fontsdir='{font_dir}',"
        "drawtext=fontfile='" + str(FONT) + "':text='WAIST HEIGHT':"
        "fontcolor=white:fontsize=54:borderw=5:bordercolor=black:x=50:y=90:enable='between(t,3,11)',"
        "drawtext=fontfile='" + str(FONT) + "':text='10 STORIES':"
        "fontcolor=white:fontsize=54:borderw=5:bordercolor=black:x=50:y=90:enable='between(t,11,22)',"
        "drawtext=fontfile='" + str(FONT) + "':text='300 FEET':"
        "fontcolor=white:fontsize=54:borderw=5:bordercolor=black:x=50:y=90:enable='between(t,22,34)',"
        "drawtext=fontfile='" + str(FONT) + "':text='1,000 FEET':"
        "fontcolor=white:fontsize=54:borderw=5:bordercolor=black:x=50:y=90:enable='between(t,34,56)',"
        "drawtext=fontfile='" + str(FONT) + "':text='ILLUSTRATION':"
        "fontcolor=yellow:fontsize=44:box=1:boxcolor=black@0.75:boxborderw=14:"
        "x=(w-tw)/2:y=220:enable='between(t,38,40)',"
        "drawtext=fontfile='" + str(FONT) + "':text='LIKE':fontcolor=white:"
        "fontsize=58:box=1:boxcolor=0xEF4444@0.9:boxborderw=18:x=80:y=330:"
        "enable='between(t,38,42)',"
        "drawtext=fontfile='" + str(FONT) + "':text='SUBSCRIBE':fontcolor=white:"
        "fontsize=58:box=1:boxcolor=0x2563EB@0.9:boxborderw=18:x=(w-tw)/2:y=330:"
        "enable='between(t,38,42)',"
        "drawtext=fontfile='" + str(FONT) + "':text='COMMENT':fontcolor=white:"
        "fontsize=58:box=1:boxcolor=0x16A34A@0.9:boxborderw=18:x=w-tw-80:y=330:"
        "enable='between(t,38,42)',"
        "drawtext=fontfile='" + str(FONT) + "':text='CAPYTECH':fontcolor=white@0.62:"
        "fontsize=30:box=1:boxcolor=black@0.28:boxborderw=9:"
        "x='if(lt(mod(t,24),12),42,w-tw-42)':"
        "y='if(lt(mod(t,20),10),h-th-190,190)',"
        "drawbox=x='470+90*sin(t*4)':y='760+55*cos(t*3)':w=150:h=150:"
        "color=yellow@0.9:t=8:enable='between(t,40,49)',"
        "drawtext=fontfile='" + str(FONT) + "':text='REAL DROP':fontcolor=yellow:"
        "fontsize=38:borderw=4:bordercolor=black:x='500+70*sin(t*4)':"
        "y='700+45*cos(t*3)':enable='between(t,40,49)'[base];"
        "[1:v]scale=420:747,format=rgba[s1];"
        "[2:v]scale=420:747,format=rgba[s2];"
        "[3:v]scale=420:747,format=rgba[s3];"
        "[4:v]scale=420:747,format=rgba[s4];"
        "[base][s1]overlay=x='35+8*sin(t*3)':y='1150+6*cos(t*4)':enable='between(t,3,11)'[v1];"
        "[v1][s2]overlay=x='w-overlay_w-35+12*sin(t*4)':y='1150+10*cos(t*5)':"
        "enable='between(t,11,22)'[v2];"
        "[v2][s3]overlay=x='30+20*sin(t*10)':y='1125+18*cos(t*9)':"
        "enable='between(t,22,49)'[v3];"
        "[v3][s4]overlay=x='w-overlay_w-30+35*(t-49)/7':"
        "y='1125+24*(t-49)':enable='between(t,49,56)'[v]"
    )
    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inputs,
            "-filter_complex", filter_graph, "-map", "[v]", "-an",
            "-c:v", "libx264", "-preset", "medium", "-crf", "12",
            "-pix_fmt", "yuv420p", "-r", "30", "-fps_mode", "cfr",
            "-t", str(DURATION), str(VISUAL),
        ]
    )

    # Narration tracks use real PCM leading silence. Each TTS file was already
    # compressed and normalized before its position is constructed.
    for line in tts["lines"]:
        source = ROOT / line["path"]
        track = TRACKS / f"tts_{line['id']}.wav"
        audio_tracks.append(
            audio_track(
                source, 0.0, float(line["duration_seconds"]), float(line["window"][0]),
                track, "aresample=48000,aformat=channel_layouts=stereo,volume=1.0",
            )
        )

    # Preserve the approved same-source payoff quote at 52.6-55.9.
    quote_record = records["thousand_result"]
    quote_source = ROOT / quote_record["source_path"]
    quote_original = storyboard["source_audio"]["intentional_quotes"][0]
    section_offset = (
        float(quote_record["source_interval_original_seconds"][0])
        - float(quote_record["source_interval_local_seconds"][0])
    )
    quote_local_start = float(quote_original["original_window_seconds"][0]) - section_offset
    audio_tracks.append(
        audio_track(
            quote_source, quote_local_start, 3.3, 52.6, TRACKS / "source_quote.wav",
            "aresample=48000,aformat=channel_layouts=stereo,"
            "acompressor=threshold=0.1:ratio=4,"
            "loudnorm=I=-19:TP=-2:LRA=8",
        )
    )

    for name, at, event_duration, frequency in (
        ("hook_hit", 0.08, 0.25, 880),
        ("split_crack", 0.82, 0.30, 180),
        ("waist_impact", 6.8, 0.25, 120),
        ("ten_impact", 17.7, 0.30, 90),
        ("split_reveal", 29.0, 0.35, 150),
        ("cta_pop", 38.05, 0.28, 720),
        ("real_drop_release", 36.1, 0.35, 520),
        ("impact", 47.9, 0.40, 70),
        ("powered_ding", 49.1, 0.50, 1040),
        ("loop_reset", 56.1, 0.35, 640),
    ):
        audio_tracks.append(lavfi_event(name, at, event_duration, frequency))
    audio_tracks.append(lavfi_bed())

    mix_inputs: list[str] = []
    for path in audio_tracks:
        mix_inputs.extend(["-i", str(path)])
    mix_filter = (
        "".join(f"[{index}:a]" for index in range(len(audio_tracks)))
        + f"amix=inputs={len(audio_tracks)}:duration=longest:normalize=0,"
        f"atrim=duration={DURATION},asetpts=PTS-STARTPTS,"
        "alimiter=limit=0.84:level=false[out]"
    )
    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *mix_inputs,
            "-filter_complex", mix_filter, "-map", "[out]", "-ar", str(RATE),
            "-ac", "2", "-c:a", "pcm_s16le", str(AUDIO_RAW),
        ]
    )
    measured = run(
        [
            "ffmpeg", "-hide_banner", "-nostats", "-i", str(AUDIO_RAW),
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=8:print_format=json",
            "-f", "null", "-",
        ],
        capture=True,
    )
    start, end = measured.stderr.rfind("{"), measured.stderr.rfind("}")
    if start < 0 or end < start:
        raise RuntimeError("Base-mix loudness measurement missing")
    stats = json.loads(measured.stderr[start:end + 1])
    loudnorm = (
        "loudnorm=I=-16:TP=-1.5:LRA=8:linear=true:"
        f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
        f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:"
        f"offset={stats['target_offset']},alimiter=limit=0.84:level=false"
    )
    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(AUDIO_RAW),
            "-af", loudnorm, "-ar", str(RATE), "-ac", "2",
            "-c:a", "pcm_s16le", str(AUDIO_FINAL),
        ]
    )
    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(VISUAL), "-i", str(AUDIO_FINAL),
            "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k", "-ar", str(RATE), "-ac", "2",
            "-t", str(DURATION), "-movflags", "+faststart", str(BASE_MASTER),
        ]
    )

    aggregates: dict[str, float] = {}
    for item in usage:
        if item["kind"] == "youtube":
            aggregates[item["video_id"]] = aggregates.get(item["video_id"], 0.0) + (
                item["final_end"] - item["final_start"]
            )
    SOURCE_USAGE.parent.mkdir(parents=True, exist_ok=True)
    SOURCE_USAGE.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "artifact": rel(BASE_MASTER),
                "occurrences": usage,
                "aggregate_youtube_usage_seconds": aggregates,
                "all_windows_strictly_under_15_seconds": all(
                    item["final_end"] - item["final_start"] < 15
                    for item in usage if item["kind"] == "youtube"
                ),
                "internal_thresholds_are_not_copyright_clearance": True,
            },
            indent=2,
        )
        + "\n"
    )
    manifest = {
        "schema_version": 1,
        "status": "BASE_MASTER_RENDERED",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "base_master": rel(BASE_MASTER),
        "base_master_sha256": sha256(BASE_MASTER),
        "renderer_sha256": sha256(Path(__file__).resolve()),
        "storyboard_sha256": sha256(STORYBOARD),
        "source_manifest_sha256": sha256(SOURCE_MANIFEST),
        "reaction_gate_sha256": sha256(REACTION_GATE),
        "tts_manifest_sha256": sha256(TTS_MANIFEST),
        "font_sha256": sha256(FONT),
        "caption_calibration_sha256": sha256(CALIBRATION),
        "pexels_sha256": sha256(PEXELS),
        "caption_bursts": bursts,
        "source_usage_path": rel(SOURCE_USAGE),
        "source_usage_sha256": sha256(SOURCE_USAGE),
        "audio_timing": "real PCM leading silence via anullsrc+concat; no adelay",
        "source_segment_fades": {"in_seconds": 0.12, "out_seconds": 0.20},
        "output": {"width": 1080, "height": 1920, "fps": 30, "duration": DURATION},
        "ffmpeg_version": run(["ffmpeg", "-version"], capture=True).stdout.splitlines()[0],
    }
    RENDER_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"PASS base master: {rel(BASE_MASTER)}")


if __name__ == "__main__":
    main()
