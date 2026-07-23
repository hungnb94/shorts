#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import mlx_whisper


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe a media file with MLX Whisper and write JSON output."
    )
    parser.add_argument("input", type=Path, help="Input audio or video file")
    parser.add_argument("output", type=Path, help="Output transcript JSON path")
    parser.add_argument(
        "--model",
        default="mlx-community/whisper-small-mlx",
        help="MLX Whisper model or local snapshot path",
    )
    parser.add_argument("--language", default="en", help="Source language code")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"Input file does not exist: {source}")

    print(f"[whisper] model={args.model} input={source}", flush=True)
    started = time.time()
    result = mlx_whisper.transcribe(
        str(source),
        path_or_hf_repo=args.model,
        language=args.language,
        word_timestamps=True,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    elapsed = time.time() - started
    print(
        f"[whisper] DONE: {len(result.get('segments', []))} segments "
        f"in {elapsed:.1f}s -> {output}",
        flush=True,
    )


if __name__ == "__main__":
    main()
