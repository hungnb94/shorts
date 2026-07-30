#!/usr/bin/env python3
"""Build the exact V10 0.0-5.0 Stage-0 hook preview after canonical TTS exists."""

from __future__ import annotations

import json
import math
import shutil
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

import render_capytech_v10_zack_reaction_explainer as renderer


ROOT = renderer.ROOT
STAGE0 = renderer.STAGE0
PREVIEW = renderer.STAGE0_PREVIEW
MANIFEST = renderer.STAGE0_MANIFEST
CONTACT_SHEET = STAGE0 / "hook_contact_sheet.jpg"
TEMP = STAGE0 / "work"
FRAMES = TEMP / "frames"
DURATION = 5.0
FPS = renderer.FPS
SCHEDULE = [
    ("hook_host", "thousand_action", 0.0, 0.75, 0.44),
    ("hook_split", "three_hundred_result", 0.0, 0.70, None),
    ("hook_scale", "thousand_action", 9.2, 0.80, None),
    ("hook_powered", "thousand_result", 4.2, 0.75, None),
    ("waist_action", "waist_action", 0.0, 2.0, None),
]
CONTACT_TIMES = [0.0, 0.2, 0.75, 1.45, 2.25, 3.0, 4.0, 4.966667]


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=capture)


def canonical_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=False) + "\n")


def probe_preview() -> dict[str, Any]:
    result = run([
        "ffprobe", "-v", "error", "-count_frames",
        "-show_entries",
        "format=duration:stream=codec_type,codec_name,profile,pix_fmt,width,height,"
        "r_frame_rate,avg_frame_rate,nb_read_frames,sample_rate,channels",
        "-of", "json", str(PREVIEW),
    ], capture=True)
    return json.loads(result.stdout)


def make_contact_sheet() -> list[dict[str, Any]]:
    FRAMES.mkdir(parents=True, exist_ok=True)
    records = []
    tile_width, tile_height = 286, 525
    sheet = Image.new("RGB", (tile_width * 4, tile_height * 2), "#e5e7eb")
    draw = ImageDraw.Draw(sheet)
    for index, at in enumerate(CONTACT_TIMES):
        frame = FRAMES / f"{index:02d}_{at:08.6f}.png"
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{at:.6f}",
             "-i", str(PREVIEW), "-frames:v", "1", "-vf", "scale=270:480:flags=lanczos",
             str(frame)])
        image = Image.open(frame).convert("RGB")
        x, y = index % 4 * tile_width, index // 4 * tile_height
        sheet.paste(image, (x + 8, y + 35))
        draw.text((x + 8, y + 8), f"{at:.3f}s", fill="#111827")
        records.append({"time_seconds": at, "path": renderer.rel(frame),
                        "sha256": renderer.sha256(frame)})
    sheet.save(CONTACT_SHEET, quality=94, subsampling=0, optimize=False)
    return records


def main() -> None:
    for executable in ("ffmpeg", "ffprobe"):
        if shutil.which(executable) is None:
            raise RuntimeError(f"Missing executable: {executable}")
    storyboard, source_manifest, tts, implementation_review = \
        renderer.validate_inputs(require_stage0_review=False)
    STAGE0.mkdir(parents=True, exist_ok=True)
    TEMP.mkdir(parents=True, exist_ok=True)
    renderer.write_captions(tts)
    records = {record["id"]: record for record in source_manifest["crop_previews"]}

    pieces: list[Path] = []
    frame_plan = []
    cumulative_seconds = 0.0
    previous_end_frame = 0
    for name, crop_id, offset, seconds, focus_override in SCHEDULE:
        piece = renderer.render_piece(
            f"stage0_{name}", records[crop_id], offset, seconds, focus_override)
        pieces.append(piece)
        cumulative_seconds += seconds
        end_frame = math.floor(cumulative_seconds * FPS + 0.5)
        frame_plan.append({"name": name, "crop_id": crop_id, "source_offset": offset,
                           "duration_seconds": seconds, "start_frame": previous_end_frame,
                           "end_frame": end_frame, "frames": end_frame - previous_end_frame,
                           "focus_override": focus_override})
        previous_end_frame = end_frame
    if previous_end_frame != 150:
        raise RuntimeError(f"Stage-0 frame plan is {previous_end_frame}, expected 150")

    visual = TEMP / "hook_visual.mkv"
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    for piece in pieces:
        command += ["-i", str(piece)]
    filters = []
    for index, item in enumerate(frame_plan):
        filters.append(
            f"[{index}:v]fps={FPS},tpad=stop_mode=clone:stop_duration=0.12,"
            f"trim=start_frame=0:end_frame={item['frames']},"
            f"setpts=N/({FPS}*TB)[v{index}]"
        )
    filters.append("".join(f"[v{i}]" for i in range(len(pieces)))
                   + f"concat=n={len(pieces)}:v=1:a=0,fps={FPS},"
                   "trim=start_frame=0:end_frame=150,setpts=N/(30*TB),"
                   f"ass='{renderer.ASS.as_posix()}'[v]")
    command += ["-filter_complex", ";".join(filters), "-map", "[v]", "-frames:v", "150",
                "-an", "-c:v", "ffv1", "-level", "3", "-pix_fmt", "yuv420p", str(visual)]
    run(command)

    hook = next(line for line in tts["lines"] if line["id"] == "hook")
    hook_track = TEMP / "hook_canonical_placed_pcm.wav"
    renderer.timed_audio(ROOT / hook["path"], float(hook["envelope"][0]),
                         DURATION, hook_track)
    audio_records, placements = renderer.make_procedural_audio_assets(
        total_duration=DURATION, asset_ids={"hook_whoosh"}, output_dir=TEMP / "audio")
    audio_tracks = [hook_track]
    for index, (asset, start) in enumerate(placements):
        placed = TEMP / f"production_{index:02d}_{asset.stem}_placed.wav"
        audio_tracks.append(renderer.timed_audio(asset, start, DURATION, placed))
    audio = TEMP / "hook_audio.wav"
    mix = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    for track in audio_tracks:
        mix += ["-i", str(track)]
    mix += ["-filter_complex", "".join(f"[{i}:a]" for i in range(len(audio_tracks)))
            + f"amix=inputs={len(audio_tracks)}:normalize=0,"
              "loudnorm=I=-16:TP=-1.5:LRA=8[a]",
            "-map", "[a]", "-t", str(DURATION), "-ar", str(renderer.RATE), "-ac", "2",
            "-c:a", "pcm_s16le", str(audio)]
    run(mix)
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(visual),
         "-i", str(audio), "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-profile:v", "high",
         "-pix_fmt", "yuv420p", "-r", str(FPS), "-vsync", "cfr", "-frames:v", "150",
         "-c:a", "aac", "-b:a", "192k", "-ar", str(renderer.RATE), "-ac", "2",
         "-t", str(DURATION), "-movflags", "+faststart", str(PREVIEW)])

    probe = probe_preview()
    video = next(stream for stream in probe["streams"] if stream["codec_type"] == "video")
    audio_stream = next(stream for stream in probe["streams"] if stream["codec_type"] == "audio")
    if float(probe["format"]["duration"]) != DURATION \
            or (video["width"], video["height"], video["r_frame_rate"],
                video["nb_read_frames"]) != (1080, 1920, "30/1", "150") \
            or video["codec_name"] != "h264" or video["profile"] != "High" \
            or video["pix_fmt"] != "yuv420p" \
            or (audio_stream["codec_name"], audio_stream["sample_rate"],
                audio_stream["channels"]) != ("aac", "48000", 2):
        raise RuntimeError(f"Invalid Stage-0 preview encoding: {probe}")
    contact_frames = make_contact_sheet()
    payload = {
        "schema_version": 1,
        "status": "STAGE0_HOOK_PREVIEW_READY_FOR_EXTERNAL_NAIVE_VIEW",
        "artifact": renderer.rel(PREVIEW),
        "artifact_sha256": renderer.sha256(PREVIEW),
        "contact_sheet": renderer.rel(CONTACT_SHEET),
        "contact_sheet_sha256": renderer.sha256(CONTACT_SHEET),
        "contact_frames": contact_frames,
        "duration_seconds": DURATION,
        "frame_plan": frame_plan,
        "visual_contract": "renderer_current_hook_schedule_then_2s_waist_action",
        "source_filter": "renderer.source_filter_current_sharp_dynamic_full_bleed",
        "captions": {"path": renderer.rel(renderer.ASS),
                     "sha256": renderer.sha256(renderer.ASS), "scope": "full_canonical_ass"},
        "audio": {
            "hook_canonical_pcm": renderer.rel(ROOT / hook["path"]),
            "hook_canonical_pcm_sha256": hook["sha256"],
            "hook_placed_pcm": renderer.rel(hook_track),
            "hook_placed_pcm_sha256": renderer.sha256(hook_track),
            "production_assets": audio_records,
        },
        "bindings": {
            "storyboard": renderer.sha256(renderer.STORYBOARD),
            "tts_manifest": renderer.sha256(renderer.TTS_MANIFEST),
            "renderer": renderer.sha256(Path(renderer.__file__).resolve()),
            "preflight": renderer.sha256(Path(__file__).resolve()),
            "implementation_review": renderer.sha256(renderer.IMPLEMENTATION_REVIEW),
        },
        "implementation_review_status": implementation_review["status"],
        "encoding": {"width": 1080, "height": 1920, "fps": 30, "cfr": True,
                     "frames": 150, "video": "H.264 High yuv420p CRF15",
                     "audio": "AAC 48kHz stereo 192kbps"},
    }
    canonical_json(MANIFEST, payload)
    print(f"PASS Stage-0 preview: {renderer.rel(PREVIEW)}")


if __name__ == "__main__":
    main()
