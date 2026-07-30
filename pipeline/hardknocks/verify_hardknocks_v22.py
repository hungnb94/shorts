#!/usr/bin/env python3
"""Exact-final automated media verification for HardKnocks V22."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "hardknocks"
FINAL = PROJECT / "final" / "2026-07-30-hardknocks_v22_seventy_eight_tail.mp4"
WORK = PROJECT / "clips" / "v22_seventy_eight_work"
TIMELINE = WORK / "timeline.json"
CHECKS = WORK / "checks"
FRAMES = CHECKS / "sampled_frames"


def cmd(args: list[str | Path], *, check: bool = True) -> str:
    result = subprocess.run([str(item) for item in args], text=True, capture_output=True)
    if check and result.returncode != 0:
        raise RuntimeError((result.stdout or "") + (result.stderr or ""))
    return (result.stdout or "") + (result.stderr or "")


def loudnorm_json(log: str) -> dict[str, str]:
    matches = re.findall(r"\{\s*\"input_i\".*?\}", log, re.DOTALL)
    if not matches:
        raise RuntimeError("Could not parse loudnorm JSON")
    return json.loads(matches[-1])


def main() -> None:
    CHECKS.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)
    if not FINAL.is_file() or not TIMELINE.is_file():
        raise FileNotFoundError(f"Missing exact-final input: {FINAL} or {TIMELINE}")

    probe_text = cmd([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-count_frames", "-of", "json", FINAL,
    ])
    (CHECKS / "final-probe.json").write_text(probe_text, encoding="utf-8")
    probe = json.loads(probe_text)
    video = next(item for item in probe["streams"] if item["codec_type"] == "video")
    audio = next(item for item in probe["streams"] if item["codec_type"] == "audio")
    duration = float(probe["format"]["duration"])

    decode = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(FINAL), "-f", "null", "-"],
        text=True, capture_output=True,
    )
    (CHECKS / "decode.log").write_text(decode.stderr, encoding="utf-8")

    black = cmd([
        "ffmpeg", "-hide_banner", "-i", FINAL, "-vf", "blackdetect=d=0.20:pix_th=0.05", "-an", "-f", "null", "-",
    ])
    freeze = cmd([
        "ffmpeg", "-hide_banner", "-i", FINAL, "-vf", "freezedetect=n=-50dB:d=1.55", "-an", "-f", "null", "-",
    ])
    silence = cmd([
        "ffmpeg", "-hide_banner", "-i", FINAL, "-af", "silencedetect=n=-45dB:d=0.70", "-vn", "-f", "null", "-",
    ])
    loud_log = cmd([
        "ffmpeg", "-hide_banner", "-i", FINAL,
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=8:print_format=json", "-f", "null", "-",
    ])
    loud = loudnorm_json(loud_log)
    for name, text in (
        ("blackdetect.log", black), ("freezedetect.log", freeze),
        ("silencedetect.log", silence), ("loudness.log", loud_log),
    ):
        (CHECKS / name).write_text(text, encoding="utf-8")

    cmd([
        "ffmpeg", "-y", "-v", "error", "-i", FINAL,
        "-vf", "fps=2,scale=216:384,tile=5x4:padding=4:margin=4", "-frames:v", "1",
        CHECKS / "hook-0-10-contact-sheet.jpg",
    ])
    cmd([
        "ffmpeg", "-y", "-v", "error", "-i", FINAL,
        "-vf", "fps=1/2,scale=135:240,tile=7x5:padding=4:margin=4", "-frames:v", "1",
        CHECKS / "full-contact-sheet.jpg",
    ])
    cmd([
        "ffmpeg", "-y", "-v", "error", "-ss", f"{max(0.0, duration - 0.05):.3f}",
        "-i", FINAL, "-frames:v", "1", CHECKS / "final-frame.jpg",
    ])
    for name, start, length in (
        ("hook", 0.0, 10.0), ("cta", 37.3, 6.6), ("payoff", 53.8, duration - 53.8),
    ):
        cmd([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{start:.3f}", "-i", FINAL,
            "-t", f"{length:.3f}", "-c", "copy", CHECKS / f"{name}.mp4",
        ])

    for old in FRAMES.glob("*.jpg"):
        old.unlink()
    cmd([
        "ffmpeg", "-y", "-v", "error", "-i", FINAL, "-vf", "fps=1/3,scale=270:480",
        str(FRAMES / "frame-%03d.jpg"),
    ])
    bottom_ratios: list[float] = []
    for path in sorted(FRAMES.glob("*.jpg")):
        image = Image.open(path).convert("L")
        width, height = image.size
        bottom = image.crop((0, int(height * 0.86), width, height))
        middle = image.crop((0, int(height * 0.35), width, int(height * 0.70)))
        bottom_mean = ImageStat.Stat(bottom).mean[0]
        middle_mean = max(1.0, ImageStat.Stat(middle).mean[0])
        bottom_ratios.append(bottom_mean / middle_mean)
    black_footer_frames = sum(value < 0.08 for value in bottom_ratios)

    timeline_report = json.loads(TIMELINE.read_text(encoding="utf-8"))
    timeline = timeline_report["timeline"]
    contiguous = all(
        item["end_frame"] == next_item["start_frame"]
        for item, next_item in zip(timeline[:-1], timeline[1:])
    )
    cta_start = next(item["final_start"] for item in timeline if item["name"] == "story_cta")
    input_i = float(loud["input_i"])
    input_tp = float(loud["input_tp"])

    checks = {
        "duration_50_75": 50.0 <= duration <= 75.0,
        "h264_1080x1920_yuv420p": video.get("codec_name") == "h264" and video.get("width") == 1080 and video.get("height") == 1920 and video.get("pix_fmt") == "yuv420p",
        "fps_30": video.get("r_frame_rate") == "30/1",
        "aac_48k_stereo": audio.get("codec_name") == "aac" and audio.get("sample_rate") == "48000" and audio.get("channels") == 2,
        "full_decode": decode.returncode == 0 and not decode.stderr.strip(),
        "timeline_contiguous": contiguous,
        "cta_38_42": 38.0 <= cta_start <= 42.0,
        "source_each_under_15": timeline_report["checks"]["all_source_clips_under_15s"],
        "source_total_under_50pct": timeline_report["checks"]["total_source_under_50pct"],
        "black_events_zero": black.count("black_start:") == 0,
        "freeze_events_over_1_55_zero": freeze.count("freeze_start:") == 0,
        "silence_events_over_0_70_zero": silence.count("silence_start:") == 0,
        "no_persistent_black_footer": black_footer_frames == 0,
        "loudness_window": -18.0 <= input_i <= -14.0,
        "true_peak_ceiling": input_tp <= -1.0,
    }
    summary = {
        "artifact": str(FINAL.relative_to(ROOT)),
        "duration": duration,
        "frame_count": video.get("nb_read_frames"),
        "video": {
            "codec": video.get("codec_name"), "width": video.get("width"),
            "height": video.get("height"), "pixel_format": video.get("pix_fmt"),
            "fps": video.get("r_frame_rate"),
        },
        "audio": {
            "codec": audio.get("codec_name"), "sample_rate": audio.get("sample_rate"),
            "channels": audio.get("channels"), "integrated_lufs": input_i,
            "true_peak_dbtp": input_tp, "lra": float(loud["input_lra"]),
        },
        "black_events": black.count("black_start:"),
        "freeze_events_over_1_55s": freeze.count("freeze_start:"),
        "silence_events_over_0_70s": silence.count("silence_start:"),
        "sampled_pixel_frames": len(bottom_ratios),
        "black_footer_frames": black_footer_frames,
        "minimum_bottom_to_middle_luma_ratio": min(bottom_ratios) if bottom_ratios else None,
        "cta_start": cta_start,
        "source_use_seconds": timeline_report["total_source_duration"],
        "source_use_percent": timeline_report["source_use_percent"],
        "checks": checks,
        "automated_pass": all(checks.values()),
        "manual_visual_qc": "pending",
        "final_asr_qc": "pending",
        "exact_final_sfx_ledger_qc": "pending",
    }
    (CHECKS / "verification-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if not summary["automated_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
