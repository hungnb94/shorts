#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import mlx_whisper

ROOT = Path(__file__).resolve().parents[6]
FINAL = ROOT / "output" / "projects" / "hardknocks" / "final"
WORK = ROOT / "output" / "projects" / "hardknocks" / "clips" / "v15_theragun_work"
MODEL = "mlx-community/whisper-large-v3-turbo"
VIDEOS = {
    "v15a": FINAL / "2026-07-23-hardknocks_v15a_crash_created_theragun.mp4",
    "v15b": FINAL / "2026-07-23-hardknocks_v15b_first_patient_to_athletes.mp4",
}
WINDOWS = {
    "v15a": ((0.0, 10.0, "hook"), (30.0, 45.0, "proof_cta"), (42.0, 52.3, "tail")),
    "v15b": ((0.0, 10.0, "hook"), (27.0, 45.0, "proof_cta"), (50.0, 65.5, "tail")),
}


def transcribe(path: Path) -> dict:
    return mlx_whisper.transcribe(
        str(path),
        path_or_hf_repo=MODEL,
        word_timestamps=True,
        language="en",
    )


selected = {value.strip() for value in os.environ.get("QC_VARIANTS", "v15a,v15b").split(",") if value.strip()}
for key, video in VIDEOS.items():
    if key not in selected:
        continue
    checks = WORK / key / "checks"
    checks.mkdir(parents=True, exist_ok=True)
    full = transcribe(video)
    (checks / "asr_full.json").write_text(json.dumps(full, indent=2) + "\n", encoding="utf-8")
    (checks / "asr_full.txt").write_text(str(full.get("text", "")).strip() + "\n", encoding="utf-8")
    for start, duration, label in WINDOWS[key]:
        wav = checks / f"asr_{label}.wav"
        subprocess.run(
            [
                "ffmpeg", "-y", "-v", "error", "-ss", f"{start:.3f}", "-i", str(video),
                "-t", f"{duration:.3f}", "-vn", "-ac", "1", "-ar", "16000", str(wav),
            ],
            check=True,
        )
        result = transcribe(wav)
        (checks / f"asr_{label}.txt").write_text(str(result.get("text", "")).strip() + "\n", encoding="utf-8")
        print(key, label, str(result.get("text", "")).strip(), flush=True)
