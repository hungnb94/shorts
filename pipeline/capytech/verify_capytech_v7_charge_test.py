#!/usr/bin/env python3
"""Fail-closed media QC for Capytech V7 exact-final MP4."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
FINAL = ROOT / "output/projects/capytech/final/2026-07-29-capytech_v7_charge_test.mp4"
QC = ROOT / "output/projects/capytech/analysis/v7_charge_test_qc"
EXPECTED_DURATION = 52.0


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def probe(path: Path) -> dict:
    result = run([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)
    ])
    return json.loads(result.stdout)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_loudnorm(stderr: str) -> dict:
    start = stderr.rfind("{")
    end = stderr.rfind("}")
    if start < 0 or end < start:
        raise RuntimeError("loudnorm JSON missing")
    return json.loads(stderr[start : end + 1])


def extract_frame(video: Path, timestamp: float, output: Path) -> None:
    result = run([
        "ffmpeg", "-y", "-ss", f"{timestamp:.3f}", "-i", str(video),
        "-frames:v", "1", "-vf", "scale=540:960:flags=lanczos", str(output),
    ], check=False)
    if result.returncode != 0 or not output.exists():
        raise RuntimeError(f"frame extraction failed at {timestamp}s: {result.stderr[-500:]}")


def make_sheet(frames: list[tuple[float, Path]], output: Path, cols: int, thumb=(216, 384)) -> None:
    tile_w, tile_h = thumb[0] + 20, thumb[1] + 38
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tile_w, rows * tile_h), "#070911")
    for index, (timestamp, path) in enumerate(frames):
        image = Image.open(path).convert("RGB")
        image.thumbnail(thumb)
        tile = Image.new("RGB", (tile_w, tile_h), "#111522")
        tile.paste(image, ((tile_w - image.width) // 2, 28))
        ImageDraw.Draw(tile).text((7, 6), f"{timestamp:.2f}s", fill="white")
        sheet.paste(tile, ((index % cols) * tile_w, (index // cols) * tile_h))
    sheet.save(output, quality=92)


def analyze_visual(video: Path, frame0_path: Path) -> dict:
    import cv2
    import numpy as np

    frame0 = cv2.imread(str(frame0_path))
    if frame0 is None:
        raise RuntimeError("frame 0 unavailable")
    rgb = cv2.cvtColor(frame0, cv2.COLOR_BGR2RGB)
    unique_colors = int(len(np.unique(rgb.reshape(-1, 3), axis=0)))
    bottom_luma = float(cv2.cvtColor(frame0, cv2.COLOR_BGR2GRAY)[-90:, :].mean())

    capture = cv2.VideoCapture(str(video))
    fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    sample_step = max(1, round(fps / 10.0))
    max_frames = round(fps * 3.0)
    previous = None
    deltas: list[float] = []
    index = 0
    while index <= max_frames:
        capture.set(cv2.CAP_PROP_POS_FRAMES, index)
        ok, frame = capture.read()
        if not ok:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32)
        if previous is not None:
            deltas.append(float(np.mean(np.abs(gray - previous))))
        previous = gray
        index += sample_step
    capture.release()
    return {
        "frame0_unique_colors": unique_colors,
        "frame0_bottom_90px_luma": bottom_luma,
        "hook_motion_deltas_10fps": deltas,
        "hook_motion_median": float(np.median(deltas)) if deltas else 0.0,
        "hook_motion_min": float(min(deltas)) if deltas else 0.0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manual-pass", action="store_true")
    args = parser.parse_args()
    if not FINAL.exists():
        raise FileNotFoundError(FINAL)

    QC.mkdir(parents=True, exist_ok=True)
    frames_dir = QC / "critical_frames"
    hook_dir = QC / "hook_frames"
    full_dir = QC / "full_frames"
    for directory in (frames_dir, hook_dir, full_dir):
        directory.mkdir(parents=True, exist_ok=True)

    info = probe(FINAL)
    video_streams = [s for s in info["streams"] if s.get("codec_type") == "video"]
    audio_streams = [s for s in info["streams"] if s.get("codec_type") == "audio"]
    if not video_streams or not audio_streams:
        raise RuntimeError("missing video or audio stream")
    video = video_streams[0]
    audio = audio_streams[0]
    duration = float(info["format"]["duration"])

    gates: dict[str, bool] = {
        "duration": abs(duration - EXPECTED_DURATION) <= 0.10,
        "dimensions": video.get("width") == 1080 and video.get("height") == 1920,
        "video_codec": video.get("codec_name") == "h264",
        "pixel_format": video.get("pix_fmt") == "yuv420p",
        "frame_rate": video.get("r_frame_rate") == "30/1" and video.get("avg_frame_rate") == "30/1",
        "audio_codec": audio.get("codec_name") == "aac",
        "audio_rate": audio.get("sample_rate") == "48000",
        "audio_channels": audio.get("channels") == 2,
    }

    decode = run(["ffmpeg", "-v", "error", "-i", str(FINAL), "-f", "null", "-"], check=False)
    gates["full_decode"] = decode.returncode == 0 and not decode.stderr.strip()

    detector_filter = (
        "blackdetect=d=0.20:pix_th=0.10,"
        # Fixed-camera 3D animation changes a small semantic region at a time;
        # -45dB falsely marked the moving cable as a full-frame freeze.
        "freezedetect=n=-60dB:d=1.0"
    )
    detectors = run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(FINAL),
        "-vf", detector_filter, "-af", "silencedetect=n=-48dB:d=0.75", "-f", "null", "-",
    ], check=False)
    detector_text = detectors.stderr
    black_events = re.findall(r"black_start:[^\n]+", detector_text)
    freeze_events = re.findall(r"freeze_start:[^\n]+", detector_text)
    silence_events = re.findall(r"silence_start:[^\n]+", detector_text)
    gates["no_black_events"] = not black_events
    gates["no_freeze_events"] = not freeze_events
    # Tiny transition gaps may exist, but a sustained 0.75s silence is not expected.
    gates["no_silence_events"] = not silence_events
    (QC / "detectors.log").write_text(detector_text)

    loud = run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(FINAL),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=8:print_format=json", "-f", "null", "-",
    ], check=False)
    loudness = parse_loudnorm(loud.stderr)
    integrated = float(loudness["input_i"])
    true_peak = float(loudness["input_tp"])
    lra = float(loudness["input_lra"])
    gates["integrated_loudness"] = -18.0 <= integrated <= -14.0
    gates["true_peak"] = true_peak <= -1.5
    gates["lra"] = lra <= 10.0
    (QC / "loudness.json").write_text(json.dumps(loudness, indent=2) + "\n")

    critical_times = [0.0, 0.2, 0.85, 2.0, 5.8, 8.5, 9.45, 16.5, 19.0, 20.0, 26.5, 31.5, 32.55, 36.0, 38.4, 39.5, 40.6, 42.0, 45.0, 47.8, 48.15, 48.7, 49.4, 50.2, 51.8]
    critical_frames: list[tuple[float, Path]] = []
    for timestamp in critical_times:
        output = frames_dir / f"{timestamp:05.2f}.jpg"
        extract_frame(FINAL, timestamp, output)
        critical_frames.append((timestamp, output))
    make_sheet(critical_frames, QC / "critical_frames_sheet.jpg", cols=5)

    hook_times = [x / 4 for x in range(13)]
    hook_frames: list[tuple[float, Path]] = []
    for timestamp in hook_times:
        output = hook_dir / f"{timestamp:04.2f}.jpg"
        extract_frame(FINAL, timestamp, output)
        hook_frames.append((timestamp, output))
    make_sheet(hook_frames, QC / "hook_sheet.jpg", cols=5)

    full_times = [min(51.8, x * 2.0) for x in range(27)]
    full_frames: list[tuple[float, Path]] = []
    for timestamp in full_times:
        output = full_dir / f"{timestamp:05.2f}.jpg"
        extract_frame(FINAL, timestamp, output)
        full_frames.append((timestamp, output))
    make_sheet(full_frames, QC / "contact_sheet.jpg", cols=6)

    visual = analyze_visual(FINAL, hook_frames[0][1])
    gates["visual_not_flat"] = visual["frame0_unique_colors"] >= 5000
    gates["no_black_footer"] = visual["frame0_bottom_90px_luma"] >= 8.0
    gates["hook_motion"] = visual["hook_motion_median"] > 0.40 and visual["hook_motion_min"] > 0.15

    asr_assessment_path = QC / "final_asr_assessment.json"
    asr_assessment = json.loads(asr_assessment_path.read_text()) if asr_assessment_path.exists() else {}
    gates["no_real_speech"] = asr_assessment.get("no_real_speech") is True

    evidence_paths = [
        QC / "critical_frames_sheet.jpg",
        QC / "hook_sheet.jpg",
        QC / "contact_sheet.jpg",
        QC / "detectors.log",
        QC / "loudness.json",
        QC / "final_asr.json",
        asr_assessment_path,
    ]
    final_mtime = FINAL.stat().st_mtime
    gates["evidence_freshness"] = all(path.exists() and path.stat().st_mtime >= final_mtime for path in evidence_paths)
    gates["manual_visual_review"] = args.manual_pass

    report = {
        "version": "capytech_v7_charge_test_qc_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifact": str(FINAL),
        "sha256": sha256(FINAL),
        "file_size_bytes": FINAL.stat().st_size,
        "duration_seconds": duration,
        "video_stream": video,
        "audio_stream": audio,
        "loudness": {
            "integrated_lufs": integrated,
            "true_peak_dbtp": true_peak,
            "lra_lu": lra,
        },
        "detectors": {
            "black_events": black_events,
            "freeze_events": freeze_events,
            "silence_events": silence_events,
        },
        "visual": visual,
        "asr_assessment": asr_assessment,
        "gates": gates,
        "pass": all(gates.values()),
    }
    report_path = QC / "final_qc.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    failed = [name for name, passed in gates.items() if not passed]
    print(json.dumps({
        "report": str(report_path),
        "pass": report["pass"],
        "failed_gates": failed,
        "sha256": report["sha256"],
        "duration_seconds": duration,
        "loudness": report["loudness"],
    }, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
