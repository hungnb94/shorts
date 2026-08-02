#!/usr/bin/env python3
"""Exact-final automated media verification for HardKnocks V27.

The visual hook is new. The encoded audio stream must remain byte-identical to
V26 before its exact-final SFX audit is reused; the verifier still runs fresh
V27 probe, decode, detectors, frames and ASR through the V26 fail-closed gates.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_VERIFIER = ROOT / "pipeline" / "hardknocks" / "verify_hardknocks_v26.py"
_spec = importlib.util.spec_from_file_location("verify_hardknocks_v26", SOURCE_VERIFIER)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Unable to import {SOURCE_VERIFIER}")
v26_verify = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = v26_verify
_spec.loader.exec_module(v26_verify)

PROJECT = ROOT / "output" / "projects" / "hardknocks"
WORK = PROJECT / "clips" / "v27_decision_lock_work"
CHECKS = WORK / "checks"
FINAL = PROJECT / "final" / "2026-08-02-hardknocks_v27_decision_lock.mp4"
V26_FINAL = PROJECT / "final" / "2026-08-01-hardknocks_v26_rejected_ten_percent.mp4"
V26_WORK = PROJECT / "clips" / "v26_rejected_ten_percent_work"


def audio_md5(path: Path) -> str:
    result = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a:0", "-c", "copy", "-f", "md5", "-"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip().removeprefix("MD5=")


def configure() -> tuple[str, str]:
    v26_audio = audio_md5(V26_FINAL)
    v27_audio = audio_md5(FINAL)
    if v26_audio != v27_audio:
        raise RuntimeError(f"V27 audio changed: V26={v26_audio}, V27={v27_audio}")

    overrides = {
        "FINAL": FINAL,
        "WORK": WORK,
        "TIMELINE": WORK / "timeline.json",
        "CAPTIONS": V26_WORK / "captions_v1_word_timed.json",
        "CHECKS": CHECKS,
        "FRAMES": CHECKS / "sampled_frames",
        "HOOK_FRAMES": CHECKS / "hook_motion_frames",
        "BOUNDARY_FRAMES": CHECKS / "boundary_frames",
        "ASR_JSON": CHECKS / "final_asr.json",
        "SFX_AUDIT": V26_WORK / "checks" / "sfx-event-audit.json",
    }
    for name, value in overrides.items():
        setattr(v26_verify, name, value)
    return v26_audio, v27_audio


def main() -> None:
    v26_audio, v27_audio = configure()
    v26_verify.main()
    summary_path = CHECKS / "verification-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["artifact"] = str(FINAL.relative_to(ROOT))
    summary["material_revision"] = {
        "from": "HardKnocks V26",
        "changed_window": [0.0, 7.70],
        "changed_layer": "visual hook information design",
        "selected_strategy": "forced_prediction_lock",
        "audio_stream_md5_v26": v26_audio,
        "audio_stream_md5_v27": v27_audio,
        "audio_stream_byte_identical": v26_audio == v27_audio,
        "sfx_evidence_reuse_basis": "encoded audio stream byte identity",
    }
    summary["manual_visual_qc"] = "pending independent V27 exact-final review"
    summary["checks"]["audio_stream_byte_identical_to_v26_control"] = v26_audio == v27_audio
    summary["automated_pass"] = all(summary["checks"].values())
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if not summary["automated_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
