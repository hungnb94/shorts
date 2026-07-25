#!/usr/bin/env python3
"""Artifact-level verifier for Ronald Wayne v3 synchronized render."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output/projects/ronaldwayne"
V1 = PROJECT / "2026-07-25-ronald-wayne-v1.mp4"
V2 = PROJECT / "2026-07-25-ronald-wayne-v2-qwen.mp4"
V3 = PROJECT / "2026-07-25-ronald-wayne-v3-qwen-synced.mp4"
MANIFEST = PROJECT / "scripts/visual-edl-v3-qwen-synced.json"
ALIGNMENT = PROJECT / "checks-v3-sync/alignment-audit.json"
V2_ASR = PROJECT / "checks-v2-qwen/final-asr/final.txt"
V3_ASR = PROJECT / "checks-v3-sync/final-asr/final.txt"
SUMMARY = PROJECT / "checks-v3-sync/verification-summary.json"
EXPECTED_V1 = "66575535235c1a1af9624d46e0afd49f5c259d2515c3abc2520721c585288f20"
EXPECTED_V2 = "16445a6a7feac3311421483c9d33ef5e396c037a977ed056679bf62b1c6e1021"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def command_output(command: list[str | Path]) -> str:
    return subprocess.check_output([str(item) for item in command], text=True).strip()


def stream_hash(path: Path, selector: str) -> str:
    value = command_output([
        "ffmpeg", "-v", "error", "-i", path, "-map", selector, "-c", "copy",
        "-f", "hash", "-hash", "sha256", "-",
    ])
    return value.split("=", 1)[1]


def probe(path: Path) -> dict[str, Any]:
    return json.loads(command_output([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size:stream=index,codec_name,codec_type,width,height,r_frame_rate,sample_rate,channels,duration",
        "-of", "json", path,
    ]))


def normalized_tokens(text: str) -> list[str]:
    text = text.lower().replace("%", " percent ")
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text)


def main() -> None:
    required = [V1, V2, V3, MANIFEST, ALIGNMENT, V2_ASR, V3_ASR]
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)

    v1_hash = sha256(V1)
    v2_hash = sha256(V2)
    v3_hash = sha256(V3)
    v2_audio = stream_hash(V2, "0:a:0")
    v3_audio = stream_hash(V3, "0:a:0")
    metadata = probe(V3)
    streams = {stream["codec_type"]: stream for stream in metadata["streams"]}
    video = streams["video"]
    audio = streams["audio"]
    keyframe_lines = command_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-skip_frame", "nokey",
        "-show_entries", "frame=pts_time", "-of", "csv=p=0", V3,
    ]).splitlines()
    decode = subprocess.run(["ffmpeg", "-v", "error", "-i", str(V3), "-f", "null", "-"], capture_output=True, text=True)
    beats = json.loads(MANIFEST.read_text(encoding="utf-8"))
    alignment = json.loads(ALIGNMENT.read_text(encoding="utf-8"))["summary"]
    expected_asr = normalized_tokens(V2_ASR.read_text(encoding="utf-8"))
    actual_asr = normalized_tokens(V3_ASR.read_text(encoding="utf-8"))

    checks = {
        "v1_control_unchanged": v1_hash == EXPECTED_V1,
        "v2_control_unchanged": v2_hash == EXPECTED_V2,
        "audio_elementary_stream_identical_to_v2": v3_audio == v2_audio,
        "full_decode": decode.returncode == 0,
        "duration_60_seconds": abs(float(metadata["format"]["duration"]) - 60.0) <= 0.001,
        "video_stream_duration_60_seconds": abs(float(video["duration"]) - 60.0) <= 0.001,
        "audio_stream_duration_60_seconds": abs(float(audio["duration"]) - 60.0) <= 0.001,
        "video_1080x1920_30fps_h264": video["codec_name"] == "h264" and video["width"] == 1080 and video["height"] == 1920 and video["r_frame_rate"] == "30/1",
        "audio_aac_stereo_48khz": audio["codec_name"] == "aac" and audio["channels"] == 2 and audio["sample_rate"] == "48000",
        "forty_keyframes": len(keyframe_lines) == 40,
        "forty_manifest_beats": len(beats) == 40,
        "alignment_audit_pass": alignment["status"] == "pass" and alignment["premature_caption_count"] == 0,
        "silent_hold_preserved": beats[25]["mode"] == "hold" and beats[25]["caption"] == "HIS OWN INVENTIONS",
        "final_asr_exactly_matches_v2_audio": actual_asr == expected_asr,
    }
    result = "pass" if all(checks.values()) else "fail"
    summary = {
        "result": result,
        "artifact": str(V3.relative_to(ROOT)),
        "artifact_sha256": v3_hash,
        "artifact_bytes": int(metadata["format"]["size"]),
        "controls": {"v1_sha256": v1_hash, "v2_sha256": v2_hash},
        "streams": {
            "v2_audio_sha256": v2_audio,
            "v3_audio_sha256": v3_audio,
            "probe": metadata,
            "keyframe_count": len(keyframe_lines),
        },
        "alignment": alignment,
        "asr": {
            "expected_normalized_tokens": len(expected_asr),
            "actual_normalized_tokens": len(actual_asr),
            "exact_match": actual_asr == expected_asr,
        },
        "visual_qc": {
            "contact_sheet": "output/projects/ronaldwayne/checks-v3-sync/contact-sheet-40-beats.jpg",
            "caption_reveal_regression": "output/projects/ronaldwayne/checks-v3-sync/caption-reveal-regression.jpg",
            "manual_result": "pass_after_beat_36_pts_reset_fix",
        },
        "checks": checks,
        "decode_stderr": decode.stderr,
    }
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"result": result, "artifact_sha256": v3_hash, "checks": checks}, indent=2))
    if result != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
