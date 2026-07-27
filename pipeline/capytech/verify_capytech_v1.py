#!/usr/bin/env python3
"""Verify the exact final Capytech v1 MP4 and generate fresh QC evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
FINAL = ROOT / "output/projects/capytech/final/2026-07-27-capytech_v1_charging_eras.mp4"
ANALYSIS = ROOT / "output/projects/capytech/analysis/qc"
FRAMES = ANALYSIS / "critical_frames"
HOOK_SHEET = ANALYSIS / "hook_sheet.jpg"
CONTACT_SHEET = ANALYSIS / "contact_sheet.jpg"
REPORT = ANALYSIS / "final_qc.json"
ASR_DIR = ANALYSIS / "asr"
LICENSE = ROOT / "output/projects/capytech/source/pexels/license.json"
PEXELS = ROOT / "output/projects/capytech/source/pexels/34908543.mp4"
WORK = ROOT / "output/projects/capytech/clips/capytech_v1_work"
PEXELS_FRAMES = WORK / "pexels_frames"
PEXELS_PROVENANCE = PEXELS_FRAMES / "provenance.json"
CTA_WAV = WORK / "audio/cta_ready_v3.wav"
CTA_PROVENANCE = WORK / "audio/cta_provenance.json"
MANIFEST = WORK / "render_manifest.json"


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(command[:12]), "..." if len(command) > 12 else "", flush=True)
    return subprocess.run(command, check=True, capture_output=capture, text=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe(path: Path) -> dict[str, Any]:
    result = run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size,bit_rate:stream=index,codec_type,codec_name,width,height,pix_fmt,r_frame_rate,avg_frame_rate,sample_rate,channels,duration",
        "-of", "json", str(path),
    ], capture=True)
    return json.loads(result.stdout)


def detector_log(path: Path) -> str:
    result = subprocess.run([
        "ffmpeg", "-hide_banner", "-i", str(path),
        "-vf", "blackdetect=d=0.15:pix_th=0.08,freezedetect=n=0.002:d=0.8",
        "-af", "silencedetect=noise=-42dB:d=0.2", "-f", "null", "-",
    ], capture_output=True, text=True, check=True)
    return result.stderr


def measure_loudness(path: Path) -> dict[str, float]:
    result = subprocess.run([
        "ffmpeg", "-hide_banner", "-i", str(path),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-",
    ], capture_output=True, text=True, check=True)
    blocks = re.findall(r"\{\s*\"input_i\".*?\}", result.stderr, flags=re.S)
    if not blocks:
        raise RuntimeError("Could not parse loudnorm measurement")
    data = json.loads(blocks[-1])
    return {
        "integrated_lufs": float(data["input_i"]),
        "true_peak_dbtp": float(data["input_tp"]),
        "lra_lu": float(data["input_lra"]),
        "threshold_lufs": float(data["input_thresh"]),
    }


def extract_evidence(path: Path) -> None:
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)
    run([
        "ffmpeg", "-y", "-v", "error", "-i", str(path), "-vf",
        "fps=4,scale=216:-2:flags=lanczos,tile=4x3:padding=4:margin=4:color=black",
        "-frames:v", "1", str(HOOK_SHEET),
    ])
    run([
        "ffmpeg", "-y", "-v", "error", "-i", str(path), "-vf",
        "fps=1/2.5,scale=216:-2:flags=lanczos,tile=5x5:padding=4:margin=4:color=black",
        "-frames:v", "1", str(CONTACT_SHEET),
    ])
    times = [0.0, 0.2, 1.0, 2.9, 8.0, 16.0, 20.0, 24.0, 27.0, 31.0, 33.0, 36.0, 39.5, 41.0, 45.0, 48.5, 52.0, 53.5]
    for timestamp in times:
        run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{timestamp:.3f}", "-i", str(path),
            "-frames:v", "1", str(FRAMES / f"{timestamp:.1f}.jpg"),
        ])


def hook_motion(path: Path) -> dict[str, float]:
    temp = Path("/tmp/capytech_motion_qc")
    if temp.exists():
        shutil.rmtree(temp)
    temp.mkdir(parents=True)
    run([
        "ffmpeg", "-y", "-v", "error", "-t", "3", "-i", str(path),
        "-vf", "fps=10,scale=135:240:flags=bilinear,format=gray", str(temp / "%03d.png"),
    ])
    images = [np.asarray(Image.open(item), dtype=np.float32) for item in sorted(temp.glob("*.png"))]
    deltas = [float(np.mean(np.abs(b - a))) for a, b in zip(images, images[1:])]
    shutil.rmtree(temp)
    if not deltas:
        raise RuntimeError("No hook motion frames")
    return {
        "median_consecutive_frame_delta": round(float(np.median(deltas)), 4),
        "minimum_consecutive_frame_delta": round(float(np.min(deltas)), 4),
        "maximum_consecutive_frame_delta": round(float(np.max(deltas)), 4),
    }


def frame_stats() -> dict[str, Any]:
    stats: dict[str, Any] = {"bottom_row_means": {}, "unique_colors_at_20s": 0}
    for path in sorted(FRAMES.glob("*.jpg")):
        arr = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)
        stats["bottom_row_means"][path.stem] = round(float(arr[-40:].mean()), 3)
    middle = Image.open(FRAMES / "20.0.jpg").convert("RGB").resize((270, 480))
    middle_pixels = np.asarray(middle, dtype=np.uint8).reshape(-1, 3)
    stats["unique_colors_at_20s"] = int(len(np.unique(middle_pixels, axis=0)))
    return stats


def asr_summary(final_mtime: float) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name in ("full", "hook", "cta", "tail"):
        path = ASR_DIR / f"{name}.json"
        if not path.exists():
            result[name] = {"status": "missing", "fresh_for_final": False}
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        text = " ".join(segment.get("text", "").strip() for segment in data.get("segments", [])).strip()
        result[name] = {
            "status": "present",
            "fresh_for_final": path.stat().st_mtime >= final_mtime,
            "text": text,
            "segments": [
                {"start": item.get("start"), "end": item.get("end"), "text": item.get("text", "").strip()}
                for item in data.get("segments", [])
            ],
        }
    return result


def asset_provenance() -> tuple[dict[str, bool], str | None]:
    checks = {
        "required_files_present": False,
        "pexels_source_matches_license": False,
        "pexels_frame_cache_complete_and_hashed": False,
        "pexels_usage_is_exactly_2_5_seconds": False,
        "cta_cache_matches_provenance": False,
        "manifest_matches_asset_provenance": False,
        "manifest_matches_final_artifact": False,
    }
    required = [LICENSE, PEXELS, PEXELS_PROVENANCE, CTA_WAV, CTA_PROVENANCE, MANIFEST]
    checks["required_files_present"] = all(path.exists() for path in required)
    if not checks["required_files_present"]:
        missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
        return checks, f"Missing provenance files: {missing}"
    try:
        license_data = json.loads(LICENSE.read_text(encoding="utf-8"))["approved"]
        frame_provenance = json.loads(PEXELS_PROVENANCE.read_text(encoding="utf-8"))
        cta_provenance = json.loads(CTA_PROVENANCE.read_text(encoding="utf-8"))
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        source_hash = sha256(PEXELS)
        checks["pexels_source_matches_license"] = (
            source_hash == license_data["sha256"]
            and PEXELS.stat().st_size == license_data["file_size_bytes"]
        )
        frame_entries = frame_provenance.get("frames", [])
        frame_paths = sorted(PEXELS_FRAMES.glob("*.jpg"))
        checks["pexels_frame_cache_complete_and_hashed"] = (
            len(frame_entries) == len(frame_paths) == 34
            and all(
                item.get("name") == path.name and item.get("sha256") == sha256(path)
                for item, path in zip(frame_entries, frame_paths)
            )
            and frame_provenance.get("config", {}).get("source_sha256") == source_hash
        )
        checks["pexels_usage_is_exactly_2_5_seconds"] = (
            frame_provenance.get("config", {}).get("final_usage_seconds") == [32.2, 34.7]
            and manifest.get("pexels_used_as")
            == "2.5-second in-world hologram from t=32.2–34.7s, labeled ILLUSTRATION"
        )
        checks["cta_cache_matches_provenance"] = (
            cta_provenance.get("wav_sha256") == sha256(CTA_WAV)
            and cta_provenance.get("config", {}).get("voice") == "Samantha"
            and cta_provenance.get("config", {}).get("text")
            == "Like, subscribe, and comment charge to continue."
            and 0 < float(cta_provenance.get("duration_seconds", 0)) <= 2.72
        )
        checks["manifest_matches_asset_provenance"] = (
            manifest.get("pexels", {}).get("sha256") == source_hash
            and manifest.get("pexels_frame_cache") == frame_provenance
            and manifest.get("audio", {}).get("cta_cache") == cta_provenance
        )
        checks["manifest_matches_final_artifact"] = (
            manifest.get("artifact_sha256") == sha256(FINAL)
            and manifest.get("artifact_size_bytes") == FINAL.stat().st_size
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, OSError) as exc:
        return checks, f"Invalid provenance data: {exc}"
    return checks, None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manual-pass", action="store_true")
    args = parser.parse_args()
    if not FINAL.exists():
        raise FileNotFoundError(FINAL)
    mp4_mtime_before = FINAL.stat().st_mtime
    metadata = probe(FINAL)
    video = next(item for item in metadata["streams"] if item["codec_type"] == "video")
    audio = next(item for item in metadata["streams"] if item["codec_type"] == "audio")
    duration = float(metadata["format"]["duration"])
    assertions = {
        "resolution_1080x1920": (video.get("width"), video.get("height")) == (1080, 1920),
        "h264_yuv420p": video.get("codec_name") == "h264" and video.get("pix_fmt") == "yuv420p",
        "cfr_30fps": video.get("r_frame_rate") == "30/1" and video.get("avg_frame_rate") == "30/1",
        "aac_48khz_stereo": audio.get("codec_name") == "aac" and audio.get("sample_rate") == "48000" and audio.get("channels") == 2,
        "duration_50_to_75": 50 <= duration <= 75,
        "stream_durations_match": abs(float(video.get("duration", 0)) - float(audio.get("duration", 0))) <= 0.05,
    }
    if not all(assertions.values()):
        raise RuntimeError(f"Spec assertion failed: {assertions}")
    run(["ffmpeg", "-v", "error", "-i", str(FINAL), "-map", "0:v:0", "-f", "null", "-", "-map", "0:a:0", "-f", "null", "-"])
    detectors = detector_log(FINAL)
    detector_findings = {
        "black_events": re.findall(r"black_start:[^\n]+", detectors),
        "freeze_events": re.findall(r"freeze_(?:start|end|duration):[^\n]+", detectors),
        "silence_events": re.findall(r"silence_(?:start|end|duration):[^\n]+", detectors),
    }
    loudness = measure_loudness(FINAL)
    extract_evidence(FINAL)
    if FINAL.stat().st_mtime != mp4_mtime_before:
        raise RuntimeError("Final MP4 changed while QC was running")
    motion = hook_motion(FINAL)
    pixels = frame_stats()
    freshness = {
        str(path.relative_to(ROOT)): path.stat().st_mtime >= FINAL.stat().st_mtime
        for path in [HOOK_SHEET, CONTACT_SHEET, *sorted(FRAMES.glob("*.jpg"))]
    }
    asr = asr_summary(mp4_mtime_before)
    cta_text = asr.get("cta", {}).get("text", "").lower()
    full_text = asr.get("full", {}).get("text", "").lower()
    asr_assertions = {
        "cta_mentions_like": "like" in cta_text,
        "cta_mentions_subscribe": "subscribe" in cta_text,
        "cta_mentions_comment": "comment" in cta_text,
        "cta_mentions_charge": "charge" in cta_text,
        "full_contains_cta": all(word in full_text for word in ("like", "subscribe", "comment", "charge")),
        "hook_has_no_speech_leak": not asr.get("hook", {}).get("text", "").strip(),
        "all_asr_files_present_and_fresh": all(
            item.get("status") == "present" and item.get("fresh_for_final") is True
            for item in asr.values()
        ),
    }
    provenance_checks, provenance_error = asset_provenance()
    technical_gates = {
        "spec_assertions": all(assertions.values()),
        "detectors_clear": not any(detector_findings.values()),
        "loudness_in_range": -18.0 <= loudness["integrated_lufs"] <= -14.0,
        "true_peak_safe": loudness["true_peak_dbtp"] <= -1.5,
        "lra_safe": loudness["lra_lu"] <= 11.0,
        "hook_has_continuous_motion": motion["minimum_consecutive_frame_delta"] >= 0.5,
        "no_black_footer": min(pixels["bottom_row_means"].values()) >= 5.0,
        "visual_not_flat": pixels["unique_colors_at_20s"] >= 5000,
        "all_visual_evidence_fresh": all(freshness.values()),
        "asr_requirements": all(asr_assertions.values()),
        "asset_provenance": all(provenance_checks.values()) and provenance_error is None,
        "manual_visual_review": args.manual_pass,
    }
    internal_pass = all(technical_gates.values())
    report = {
        "artifact": str(FINAL.relative_to(ROOT)),
        "sha256": sha256(FINAL),
        "spec": metadata,
        "assertions": assertions,
        "full_decode": "PASS",
        "detectors": detector_findings,
        "loudness": loudness,
        "hook_motion": motion,
        "pixel_checks": pixels,
        "evidence_freshness": freshness,
        "asr": asr,
        "asr_assertions": asr_assertions,
        "asset_provenance": {"checks": provenance_checks, "error": provenance_error},
        "technical_gates": technical_gates,
        "manual_visual_review": "PASS" if args.manual_pass else "PENDING",
        "manual_review_scope": ["hook sheet", "full contact sheet", "CTA", "Pexels illustration", "energy payoff", "tail and loop"],
        "cold_viewer_clarity": {
            "subject": "A block character with a phone at 1 percent.",
            "objective": "Charge the phone before the visible countdown ends.",
            "action": "Try charging methods from 2000, 2026, and 2050.",
            "evidence_result": "The AI orb charges the phone by draining the human.",
            "payoff": "A system update drains the phone back to 1 percent, closing the loop."
        },
        "external_naive_viewer_gate": "UNVERIFIED — blocks Completed/upload-ready status",
        "status": "PASS with external Hook Gate item 6 upload block" if internal_pass else "QC incomplete or failed",
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(REPORT)
    if args.manual_pass and not internal_pass:
        failed = [name for name, passed in technical_gates.items() if not passed]
        raise RuntimeError(f"Blocking QC gates failed: {failed}")


if __name__ == "__main__":
    main()
