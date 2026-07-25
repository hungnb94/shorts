#!/usr/bin/env python3
"""Independent verification for Ronald Wayne v1 final render."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "ronaldwayne"
FINAL = PROJECT / "2026-07-25-ronald-wayne-v1.mp4"
EDL = PROJECT / "scripts" / "visual-edl-v1.json"
CHECKS = PROJECT / "checks"
ANALYSIS = PROJECT / "analysis"


def cmd(args: list[str | Path], *, capture=True) -> str:
    p = subprocess.run([str(x) for x in args], text=True, capture_output=capture, check=True)
    return (p.stdout or "") + (p.stderr or "")


def main() -> None:
    CHECKS.mkdir(parents=True, exist_ok=True)
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    if not FINAL.exists():
        raise FileNotFoundError(FINAL)

    probe_text = cmd([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", FINAL,
    ])
    (CHECKS / "final-probe.json").write_text(probe_text, encoding="utf-8")
    probe = json.loads(probe_text)
    streams = probe["streams"]
    video = next(x for x in streams if x["codec_type"] == "video")
    audio = next(x for x in streams if x["codec_type"] == "audio")
    duration = float(probe["format"]["duration"])

    decode = subprocess.run([
        "ffmpeg", "-v", "error", "-i", str(FINAL), "-f", "null", "-"
    ], text=True, capture_output=True)
    (CHECKS / "decode.log").write_text(decode.stderr, encoding="utf-8")

    edl = json.loads(EDL.read_text(encoding="utf-8"))
    starts = [float(x["start"]) for x in edl]
    ends = [float(x["end"]) for x in edl]
    gaps = [round(ends[i] - starts[i], 6) for i in range(len(edl))]
    contiguous = all(abs(ends[i] - starts[i + 1]) < 1e-6 for i in range(len(edl) - 1))

    keyframes_text = cmd([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-skip_frame", "nokey",
        "-show_entries", "frame=best_effort_timestamp_time", "-of", "csv=p=0", FINAL,
    ])
    (CHECKS / "keyframes.txt").write_text(keyframes_text, encoding="utf-8")
    keyframes = [float(x.strip().split(",")[0]) for x in keyframes_text.splitlines() if x.strip()]

    black = cmd([
        "ffmpeg", "-hide_banner", "-i", FINAL, "-vf", "blackdetect=d=0.20:pix_th=0.05",
        "-an", "-f", "null", "-",
    ])
    (CHECKS / "blackdetect.log").write_text(black, encoding="utf-8")
    freeze = cmd([
        "ffmpeg", "-hide_banner", "-i", FINAL, "-vf", "freezedetect=n=-50dB:d=1.55",
        "-an", "-f", "null", "-",
    ])
    (CHECKS / "freezedetect.log").write_text(freeze, encoding="utf-8")
    loud = cmd([
        "ffmpeg", "-hide_banner", "-i", FINAL,
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=8:print_format=json", "-f", "null", "-",
    ])
    (CHECKS / "loudness.log").write_text(loud, encoding="utf-8")

    cmd([
        "ffmpeg", "-y", "-v", "error", "-i", FINAL,
        "-vf", "fps=2,scale=216:384,tile=5x4:padding=4:margin=4", "-frames:v", "1",
        ANALYSIS / "hook-0-10-contact-sheet.jpg",
    ])
    cmd([
        "ffmpeg", "-y", "-v", "error", "-i", FINAL,
        "-vf", "fps=2/3,scale=135:240,tile=8x5:padding=4:margin=4", "-frames:v", "1",
        ANALYSIS / "full-40-beat-contact-sheet.jpg",
    ])
    cmd([
        "ffmpeg", "-y", "-v", "error", "-ss", "59.9", "-i", FINAL, "-frames:v", "1",
        ANALYSIS / "final-frame.jpg",
    ])

    summary = {
        "artifact": str(FINAL.relative_to(ROOT)),
        "duration": duration,
        "duration_pass": 59.95 <= duration <= 60.05,
        "video": {"codec": video["codec_name"], "width": video["width"], "height": video["height"], "fps": video["r_frame_rate"]},
        "audio": {"codec": audio["codec_name"], "sample_rate": audio.get("sample_rate"), "channels": audio.get("channels")},
        "spec_pass": video["codec_name"] == "h264" and video["width"] == 1080 and video["height"] == 1920 and audio["codec_name"] == "aac",
        "decode_pass": decode.returncode == 0 and not decode.stderr.strip(),
        "edl_count": len(edl),
        "edl_count_pass": len(edl) == 40,
        "edl_contiguous_pass": contiguous,
        "max_visual_state_seconds": max(gaps),
        "cadence_pass": max(gaps) <= 1.5 and min(gaps) > 0,
        "keyframe_count": len(keyframes),
        "keyframe_sample": keyframes[:12],
        "black_events": black.count("black_start:"),
        "freeze_events_over_1_55s": freeze.count("freeze_start:"),
        "manual_pixel_qc": "pending",
        "asr_qc": "pending",
    }
    summary["automated_pass"] = all([
        summary["duration_pass"], summary["spec_pass"], summary["decode_pass"],
        summary["edl_count_pass"], summary["edl_contiguous_pass"], summary["cadence_pass"],
        summary["black_events"] == 0,
    ])
    (CHECKS / "verification-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if not summary["automated_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
