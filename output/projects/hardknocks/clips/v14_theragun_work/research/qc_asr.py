#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import mlx_whisper

parser = argparse.ArgumentParser()
parser.add_argument("video")
parser.add_argument("output")
args = parser.parse_args()
result = mlx_whisper.transcribe(
    args.video,
    path_or_hf_repo="mlx-community/whisper-medium-mlx",
    language="en",
    word_timestamps=True,
)
Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
text = result.get("text", "")
print(text.strip() if isinstance(text, str) else str(text))
