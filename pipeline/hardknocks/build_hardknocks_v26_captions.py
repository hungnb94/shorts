#!/usr/bin/env python3
"""Generate word-timed caption bursts from the exact HardKnocks V26 base mix."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, cast

import mlx_whisper

MODEL = "mlx-community/whisper-small.en-mlx"
MAX_WORDS = 4
MAX_CHARS = 27
MAX_SECONDS = 1.75


def clean_token(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9$%'-]", "", value)


def flush(group: list[dict], bursts: list[dict]) -> None:
    if not group:
        return
    text = "".join(str(word["word"]) for word in group).strip()
    tokens = [clean_token(str(word["word"])) for word in group]
    candidates = [token for token in tokens if token]
    numeric = [token for token in candidates if any(char.isdigit() for char in token) or "$" in token or "%" in token]
    highlight = max(numeric or candidates or [text], key=len)
    bursts.append(
        {
            "start": round(float(group[0]["start"]), 3),
            "end": round(float(group[-1]["end"]), 3),
            "text": text.upper(),
            "highlight": highlight.upper(),
            "words": group,
        }
    )
    group.clear()


def build_bursts(words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # mlx_whisper punctuation continuations keep their own leading-space
    # semantics. Merge no-leading-space tokens (for example `,000`) into the
    # preceding lexical token before enforcing burst word-count limits, or a
    # boundary can incorrectly render `$100` and `,000` as separate captions.
    merged_words: list[dict[str, Any]] = []
    for word in words:
        raw = str(word.get("word", ""))
        if merged_words and raw and not raw[0].isspace():
            merged_words[-1]["word"] = str(merged_words[-1].get("word", "")) + raw
            merged_words[-1]["end"] = word.get("end", merged_words[-1].get("end"))
        else:
            merged_words.append(dict(word))
    words = merged_words

    bursts: list[dict[str, Any]] = []
    group: list[dict[str, Any]] = []
    for word in words:
        raw = str(word.get("word", ""))
        if not raw.strip():
            continue
        candidate = group + [word]
        text = "".join(str(item["word"]) for item in candidate).strip()
        duration = float(candidate[-1]["end"]) - float(candidate[0]["start"])
        if group and (len(candidate) > MAX_WORDS or len(text) > MAX_CHARS or duration > MAX_SECONDS):
            flush(group, bursts)
        group.append(word)
        if re.search(r"[.!?](?:['\"])?\s*$", raw.strip()) or len(group) >= MAX_WORDS:
            flush(group, bursts)
    flush(group, bursts)
    for index, burst in enumerate(bursts):
        if index + 1 < len(bursts):
            next_start = float(bursts[index + 1]["start"])
            burst["end"] = round(max(float(burst["end"]) + 0.10, next_start + 0.03), 3)
        else:
            burst["end"] = round(float(burst["end"]) + 0.22, 3)
    if bursts:
        bursts[0]["start"] = min(float(bursts[0]["start"]), 0.20)
    return bursts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = cast(
        dict[str, Any],
        mlx_whisper.transcribe(
            str(args.input),
            path_or_hf_repo=MODEL,
            word_timestamps=True,
            language="en",
            verbose=False,
        ),
    )
    words = [word for segment in result.get("segments", []) for word in segment.get("words", [])]
    if not words:
        raise RuntimeError("Whisper returned no word timestamps")
    bursts = build_bursts(words)
    payload = {
        "model": MODEL,
        "input": str(args.input),
        "text": str(result.get("text", "")).strip(),
        "bursts": bursts,
        "word_count": len(words),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
