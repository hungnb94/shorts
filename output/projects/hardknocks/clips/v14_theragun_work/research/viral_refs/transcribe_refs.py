#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import mlx_whisper

ROOT = Path(__file__).resolve().parent
IDS = [
    "icox-xKoGKc",
    "F8TkkC6_WDQ",
    "U3iT0RXkflU",
    "nmitENcUczU",
    "Y2dkRTTELz4",
    "yJtINrOAlbU",
]

for video_id in IDS:
    source = ROOT / f"{video_id}.mp4"
    output = ROOT / f"{video_id}.transcript.json"
    result = mlx_whisper.transcribe(
        str(source),
        path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
        language="en",
        word_timestamps=True,
        verbose=False,
    )
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    text = result.get("text", "")
    print(f"{video_id}: {text.strip() if isinstance(text, str) else text}")
