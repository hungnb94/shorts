#!/usr/bin/env python3
"""
extract_keyframes.py - ffprobe info + ffmpeg scene-detect keyframe extraction.

Ported from ~/.hermes/skills/shorts/video-analyzer/scripts/analyze_video.py.
Unlike that script, this does NOT call any vision API - it only extracts
frames to disk and writes a JSON manifest of paths + timestamps. The caller
(Claude, running in Claude Code) reads each frame directly via the Read tool.

Two frame sets are produced:
  - scene keyframes: ffmpeg scene-change detection (`select='gt(scene,T)'`),
    capped at --max-frames, covering the whole video.
  - hook-window frames: fixed-interval frames across the first
    --hook-window-sec seconds, for measuring visual-change cadence
    (docs/WORKFLOW.md Stage 0 cadence check / ADR-0016/0018) independent of
    whether ffmpeg's scene-detect fires in that window.

Usage:
    python3 extract_keyframes.py <video_path> --out-dir <dir> \
        [--max-frames N] [--scene-threshold T] \
        [--hook-window-sec S] [--hook-window-step S]
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def check_dependencies():
    missing = []
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        missing.append("ffmpeg (install: brew install ffmpeg)")
    try:
        subprocess.run(["ffprobe", "-version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        missing.append("ffprobe (comes with ffmpeg)")
    if missing:
        print("ERROR: Missing dependencies:", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        sys.exit(1)


def get_video_info(video_path: str) -> dict:
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: ffprobe failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def detect_scene_timestamps(video_path: str, scene_threshold: float) -> list:
    detect_cmd = [
        "ffmpeg", "-i", video_path,
        "-filter:v", f"select='gt(scene,{scene_threshold})',showinfo",
        "-f", "null", "-",
    ]
    result = subprocess.run(detect_cmd, capture_output=True, text=True, timeout=120)
    timestamps = []
    for line in (result.stderr or "").split("\n"):
        m = re.search(r"pts_time:([\d.]+)", line)
        if m:
            timestamps.append(float(m.group(1)))
    if not timestamps or timestamps[0] != 0.0:
        timestamps.insert(0, 0.0)
    return sorted(set(round(t, 2) for t in timestamps))


def cap_timestamps(timestamps: list, max_frames: int) -> list:
    if len(timestamps) <= max_frames:
        return timestamps
    selected = [timestamps[0]]
    step = (len(timestamps) - 1) / (max_frames - 1)
    for i in range(1, max_frames - 1):
        idx = min(int(i * step), len(timestamps) - 1)
        selected.append(timestamps[idx])
    selected.append(timestamps[-1])
    return selected


def extract_frame(video_path: str, ts: float, out_path: str) -> bool:
    cmd = [
        "ffmpeg", "-y", "-ss", str(ts), "-i", video_path,
        "-vframes", "1", "-q:v", "2", out_path,
    ]
    subprocess.run(cmd, capture_output=True, timeout=30)
    return os.path.exists(out_path) and os.path.getsize(out_path) > 0


def build_frame_set(video_path: str, out_dir: Path, prefix: str, timestamps: list) -> list:
    frames = []
    for i, ts in enumerate(timestamps):
        out_path = out_dir / f"{prefix}_{i:03d}_{ts:.2f}.jpg"
        if extract_frame(video_path, ts, str(out_path)):
            frames.append({"path": str(out_path), "timestamp": ts})
    return frames


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video_path")
    parser.add_argument("--out-dir", required=True, help="directory to write frames + manifest.json into")
    parser.add_argument("--max-frames", type=int, default=8, help="max scene keyframes across the whole video")
    parser.add_argument("--scene-threshold", type=float, default=0.3)
    parser.add_argument("--hook-window-sec", type=float, default=10.0, help="span for fixed-interval cadence frames")
    parser.add_argument("--hook-window-step", type=float, default=1.0, help="interval between cadence frames")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    check_dependencies()

    video_path = Path(args.video_path)
    if not video_path.exists():
        print(f"ERROR: Video not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    info = get_video_info(str(video_path))
    streams = info.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
    duration = float(info.get("format", {}).get("duration", 0))
    width = video_stream.get("width", 0)
    height = video_stream.get("height", 0)

    if args.verbose:
        print(f"[INFO] Duration: {duration:.1f}s  Resolution: {width}x{height}", file=sys.stderr)

    scene_ts = detect_scene_timestamps(str(video_path), args.scene_threshold)
    scene_ts = cap_timestamps(scene_ts, args.max_frames)
    scene_frames = build_frame_set(str(video_path), out_dir, "scene", scene_ts)

    hook_end = min(args.hook_window_sec, duration) if duration else args.hook_window_sec
    hook_ts = []
    t = 0.0
    while t <= hook_end:
        hook_ts.append(round(t, 2))
        t += args.hook_window_step
    hook_frames = build_frame_set(str(video_path), out_dir, "hook", hook_ts)

    manifest = {
        "video": str(video_path),
        "duration_sec": round(duration, 1),
        "resolution": f"{width}x{height}",
        "scene_keyframes": scene_frames,
        "hook_window_frames": hook_frames,
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.verbose:
        print(f"[INFO] {len(scene_frames)} scene keyframes, {len(hook_frames)} hook-window frames", file=sys.stderr)
        print(f"[INFO] Manifest: {manifest_path}", file=sys.stderr)

    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
