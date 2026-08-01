#!/usr/bin/env python3
"""Exact-final automated media verification for HardKnocks V25."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "hardknocks"
FINAL_OUTPUT = PROJECT / "final" / "2026-08-01-hardknocks_v25_searchable_story_moat.mp4"
CANDIDATE = PROJECT / "clips" / "v25_searchable_story_work" / "candidate_v1_searchable_story.mp4"
FINAL = FINAL_OUTPUT if FINAL_OUTPUT.exists() else CANDIDATE
SOURCE = PROJECT / "clips" / "v25_reference_F-QqW0Th-Lc_research" / "source.mp4"
WORK = PROJECT / "clips" / "v25_searchable_story_work"
TIMELINE = WORK / "timeline.json"
CHECKS = WORK / "checks"
FRAMES = CHECKS / "sampled_frames"
HOOK_FRAMES = CHECKS / "hook_motion_frames"


def cmd(args: list[str | Path], *, check: bool = True) -> str:
    result = subprocess.run([str(item) for item in args], text=True, capture_output=True)
    if check and result.returncode != 0:
        raise RuntimeError((result.stdout or "") + (result.stderr or ""))
    return (result.stdout or "") + (result.stderr or "")


def duration(path: Path) -> float:
    return float(cmd([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", path,
    ]).strip())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def skin_ratio(image: Image.Image) -> float:
    array = np.asarray(image.convert("RGB"), dtype=np.uint8)
    red = array[:, :, 0]
    green = array[:, :, 1]
    blue = array[:, :, 2]
    mask = (
        (red > 70) & (red < 235) & (green > 35) & (green < 190) &
        (blue > 15) & (blue < 175) & (red > green) & (green > blue) &
        ((red.astype(np.int16) - blue.astype(np.int16)) > 15)
    )
    return float(mask.mean())


def main() -> None:
    CHECKS.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)
    HOOK_FRAMES.mkdir(parents=True, exist_ok=True)
    probe_text = cmd([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-count_frames", "-of", "json", FINAL,
    ])
    (CHECKS / "final-probe.json").write_text(probe_text, encoding="utf-8")
    probe = json.loads(probe_text)
    video = next(item for item in probe["streams"] if item["codec_type"] == "video")
    audio = next(item for item in probe["streams"] if item["codec_type"] == "audio")
    final_duration = float(probe["format"]["duration"])

    decode = subprocess.run(["ffmpeg", "-v", "error", "-i", str(FINAL), "-f", "null", "-"], text=True, capture_output=True)
    black = cmd(["ffmpeg", "-hide_banner", "-i", FINAL, "-vf", "blackdetect=d=0.20:pix_th=0.05", "-an", "-f", "null", "-"])
    freeze = cmd(["ffmpeg", "-hide_banner", "-i", FINAL, "-vf", "freezedetect=n=-50dB:d=1.55", "-an", "-f", "null", "-"])
    silence = cmd(["ffmpeg", "-hide_banner", "-i", FINAL, "-af", "silencedetect=n=-45dB:d=0.70", "-vn", "-f", "null", "-"])
    loud_log = cmd([
        "ffmpeg", "-hide_banner", "-i", FINAL,
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=8:print_format=json", "-f", "null", "-",
    ])
    loud = json.loads(re.findall(r"\{\s*\"input_i\".*?\}", loud_log, re.DOTALL)[-1])
    for name, text in (
        ("decode.log", decode.stderr),
        ("blackdetect.log", black),
        ("freezedetect.log", freeze),
        ("silencedetect.log", silence),
        ("loudness.log", loud_log),
    ):
        (CHECKS / name).write_text(text, encoding="utf-8")

    cmd([
        "ffmpeg", "-y", "-v", "error", "-t", "10", "-i", FINAL,
        "-vf", "fps=2,scale=216:384,tile=5x4:padding=4:margin=4", "-frames:v", "1",
        CHECKS / "hook-0-10-contact-sheet.jpg",
    ])
    cmd([
        "ffmpeg", "-y", "-v", "error", "-i", FINAL,
        "-vf", "fps=1/2,scale=162:288,tile=8x4:padding=4:margin=4", "-frames:v", "1",
        CHECKS / "full-contact-sheet.jpg",
    ])

    for directory in (FRAMES, HOOK_FRAMES):
        for old in directory.glob("*.jpg"):
            old.unlink()
    cmd([
        "ffmpeg", "-y", "-v", "error", "-i", FINAL, "-vf", "fps=1/2,scale=270:480",
        str(FRAMES / "frame-%03d.jpg"),
    ])
    cmd([
        "ffmpeg", "-y", "-v", "error", "-t", "3", "-i", FINAL, "-vf", "fps=10,scale=270:480",
        str(HOOK_FRAMES / "frame-%03d.jpg"),
    ])

    bottom_ratios: list[float] = []
    color_counts: list[int] = []
    for path in sorted(FRAMES.glob("*.jpg")):
        image = Image.open(path).convert("RGB")
        gray = image.convert("L")
        width, height = gray.size
        bottom = gray.crop((0, int(height * 0.86), width, height))
        middle = gray.crop((0, int(height * 0.35), width, int(height * 0.70)))
        bottom_ratios.append(ImageStat.Stat(bottom).mean[0] / max(1.0, ImageStat.Stat(middle).mean[0]))
        sample = image.resize((135, 240))
        color_counts.append(len(sample.getcolors(maxcolors=135 * 240) or []))

    hook_paths = sorted(HOOK_FRAMES.glob("*.jpg"))
    hook_deltas: list[float] = []
    for first, second in zip(hook_paths, hook_paths[1:]):
        a = Image.open(first).convert("L")
        b = Image.open(second).convert("L")
        difference = ImageChops.difference(a, b)
        hook_deltas.append(float(ImageStat.Stat(difference).mean[0]))

    skin_samples: dict[str, float] = {}
    for stamp in (0.0, 0.5, 2.0):
        path = CHECKS / f"hook-face-{stamp:.1f}.jpg"
        cmd(["ffmpeg", "-y", "-v", "error", "-ss", f"{stamp:.3f}", "-i", FINAL, "-frames:v", "1", path])
        skin_samples[f"{stamp:.1f}"] = skin_ratio(Image.open(path))

    frame_caption = CHECKS / "caption-at-0.2.jpg"
    cmd(["ffmpeg", "-y", "-v", "error", "-ss", "0.20", "-i", FINAL, "-frames:v", "1", frame_caption])
    caption_image = np.asarray(Image.open(frame_caption).convert("RGB"), dtype=np.uint8)
    band = caption_image[int(1920 * 0.50):int(1920 * 0.70), :, :]
    caption_bright_ratio = float(((band[:, :, 0] > 215) & (band[:, :, 1] > 215) & (band[:, :, 2] > 215)).mean())
    caption_cyan_ratio = float(((band[:, :, 0] < 120) & (band[:, :, 1] > 150) & (band[:, :, 2] > 190)).mean())

    timeline = json.loads(TIMELINE.read_text(encoding="utf-8"))["segments"]
    source_segments = [item for item in timeline if item["kind"] in {"source", "source_silent"}]
    source_seconds = sum(float(item["duration"]) for item in source_segments)
    source_master_duration = duration(SOURCE)
    cta_start = next(float(item["output_start"]) for item in timeline if item["name"] == "11_triple_cta")

    checks = {
        "duration_50_75_and_near_64": 50 <= final_duration <= 75 and abs(final_duration - 64.0) <= 0.08,
        "h264_1080x1920_yuv420p": video.get("codec_name") == "h264" and video.get("width") == 1080 and video.get("height") == 1920 and video.get("pix_fmt") == "yuv420p",
        "fps_30": video.get("r_frame_rate") == "30/1" and video.get("avg_frame_rate") == "30/1",
        "aac_48k_stereo": audio.get("codec_name") == "aac" and audio.get("sample_rate") == "48000" and audio.get("channels") == 2,
        "full_decode": decode.returncode == 0 and not decode.stderr.strip(),
        "timeline_contiguous": all(abs(float(a["output_end"]) - float(b["output_start"])) < 0.002 for a, b in zip(timeline, timeline[1:])),
        "cta_38_42": 38 <= cta_start <= 42,
        "source_each_under_15": all(float(item["duration"]) < 15 for item in source_segments),
        "source_total_under_half_master": source_seconds <= source_master_duration * 0.5,
        "black_events_zero": black.count("black_start:") == 0,
        "freeze_events_zero": freeze.count("freeze_start:") == 0,
        "silence_events_zero": silence.count("silence_start:") == 0,
        "no_persistent_black_footer": all(value >= 0.08 for value in bottom_ratios),
        "visual_not_text_only": min(color_counts) >= 3000,
        "hook_real_motion": bool(hook_deltas) and float(np.median(hook_deltas)) > 1.0 and min(hook_deltas) > 0.30,
        "hook_face_gate": max(skin_samples.values()) >= 0.10,
        "caption_visible_by_0_2": caption_bright_ratio + caption_cyan_ratio >= 0.002,
        "loudness_window": -18 <= float(loud["input_i"]) <= -14,
        "true_peak_ceiling": float(loud["input_tp"]) <= -1.0,
    }
    summary = {
        "artifact": str(FINAL.relative_to(ROOT)),
        "sha256": sha256(FINAL),
        "size_bytes": FINAL.stat().st_size,
        "duration": final_duration,
        "frame_count": video.get("nb_read_frames"),
        "video": {
            "codec": video.get("codec_name"), "width": video.get("width"), "height": video.get("height"),
            "pixel_format": video.get("pix_fmt"), "r_frame_rate": video.get("r_frame_rate"), "avg_frame_rate": video.get("avg_frame_rate"),
        },
        "audio": {
            "codec": audio.get("codec_name"), "sample_rate": audio.get("sample_rate"), "channels": audio.get("channels"),
            "integrated_lufs": float(loud["input_i"]), "true_peak_dbtp": float(loud["input_tp"]), "lra": float(loud["input_lra"]),
        },
        "cta_start": cta_start,
        "source_use_seconds": round(source_seconds, 3),
        "source_master_seconds": source_master_duration,
        "black_events": black.count("black_start:"),
        "freeze_events": freeze.count("freeze_start:"),
        "silence_events": silence.count("silence_start:"),
        "sampled_pixel_frames": len(bottom_ratios),
        "minimum_bottom_to_middle_luma_ratio": min(bottom_ratios),
        "minimum_sample_color_count": min(color_counts),
        "hook_motion": {
            "median_delta": float(np.median(hook_deltas)), "minimum_delta": min(hook_deltas), "samples": len(hook_deltas),
        },
        "hook_skin_ratios": skin_samples,
        "caption_band": {"bright_ratio": caption_bright_ratio, "cyan_ratio": caption_cyan_ratio},
        "checks": checks,
        "automated_pass": all(checks.values()),
        "manual_visual_qc": "pending",
        "final_asr_qc": "pending",
        "exact_final_sfx_ledger_qc": "pending",
        "publication": "blocked: source/master rights and narrator publication licence unresolved",
    }
    (CHECKS / "verification-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if not summary["automated_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
