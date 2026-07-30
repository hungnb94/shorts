#!/usr/bin/env python3
"""Generate the canonical Capytech V9 commentary with Qwen Base-ICL.

Run this script with the pinned MLX environment:

    .venv-mlx/bin/python pipeline/capytech/generate_capytech_v9_tts.py

The model is loaded once. Every approved storyboard line is synthesized,
converted to 48 kHz stereo PCM, normalized, transcribed with word timestamps,
and hash-bound in a fail-closed manifest.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import mlx.core as mx
import numpy as np
import soundfile as sf
from mlx_audio.tts.utils import load_model

ROOT = Path(__file__).resolve().parents[2]
SPIKE = ROOT / "spikes/001-english-tts-engine-bakeoff"
sys.path.insert(0, str(SPIKE / "scripts"))

from runtime_provenance import (  # noqa: E402
    sha256 as provenance_sha256,
    verified_model_snapshot,
    verify_environment,
    verify_system_fingerprints,
)

STORYBOARD = ROOT / "output/projects/capytech/scripts/capytech_v9_real_drop_storyboard.json"
WORK = ROOT / "output/projects/capytech/clips/capytech_v9_real_drop_work"
AUDIO_DIR = WORK / "audio/tts"
MANIFEST = WORK / "audio/tts_manifest.json"
PROFILE_DIR = ROOT / "data/narrator-voices/natural_talker_male_qwen_blog"
PROFILE_PATH = PROFILE_DIR / "profile.json"
ASR_PYTHON = Path("/usr/bin/python3")
ASR_MODEL = "mlx-community/whisper-large-v3-turbo"
SAMPLE_RATE = 48_000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize(text: str) -> str:
    value = re.sub(r"['’]", "", text.lower())
    value = re.sub(r"\b1\s*,?\s*000\b", "one thousand", value)
    value = re.sub(r"\b300\b", "three hundred", value)
    value = re.sub(r"\b10\b", "ten", value)
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def require_file(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=capture,
    )


def transcribe(path: Path) -> dict[str, Any]:
    """Use system Python as required, keeping MLX Whisper out of this process."""
    code = (
        "import json,sys,mlx_whisper;"
        "r=mlx_whisper.transcribe(sys.argv[1],path_or_hf_repo=sys.argv[2],"
        "word_timestamps=True,language='en');"
        "print(json.dumps(r,ensure_ascii=False))"
    )
    result = run([str(ASR_PYTHON), "-c", code, str(path), ASR_MODEL], capture=True)
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid mlx_whisper JSON for {path.name}") from exc
    words = [
        {
            "word": word["word"],
            "start": round(float(word["start"]), 4),
            "end": round(float(word["end"]), 4),
        }
        for segment in payload.get("segments", [])
        for word in segment.get("words", [])
        if word.get("word") and word.get("start") is not None and word.get("end") is not None
    ]
    if not words:
        raise RuntimeError(f"No word timestamps returned for {path.name}")
    # mlx_whisper tokens already carry correct leading-space punctuation semantics.
    reconstructed = "".join(word["word"] for word in words).strip()
    return {
        "text": payload.get("text", reconstructed).strip(),
        "reconstructed_from_raw_tokens": reconstructed,
        "normalized": normalize(reconstructed),
        "words": words,
    }


def duration_seconds(path: Path) -> float:
    result = run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=nw=1:nk=1", str(path),
        ],
        capture=True,
    )
    return float(result.stdout.strip())


def validate_asr(line: dict[str, Any], asr: dict[str, Any]) -> None:
    expected_words = set(line["expected_normalized_asr"].split())
    actual_words = set(asr["normalized"].split())
    required = expected_words - {"a", "an", "the", "this", "it", "to", "and"}
    missing = sorted(required - actual_words)
    if missing:
        raise RuntimeError(f"{line['id']} ASR is missing required words: {missing}")


def main() -> None:
    for path in (STORYBOARD, PROFILE_PATH, ASR_PYTHON):
        require_file(path)
    for executable in ("ffmpeg", "ffprobe"):
        if shutil.which(executable) is None:
            raise RuntimeError(f"Required executable unavailable: {executable}")

    storyboard = json.loads(STORYBOARD.read_text())
    profile = json.loads(PROFILE_PATH.read_text())
    reference = PROFILE_DIR / profile["identity"]["reference_audio"]
    require_file(reference)

    # This is the same fail-closed Base-ICL/provenance boundary as the proven
    # hardknocks narrator wrapper.
    verify_environment(profile, SPIKE, "synthesis")
    verify_system_fingerprints(profile)
    if provenance_sha256(reference) != profile["identity"]["reference_sha256"]:
        raise RuntimeError("Canonical narrator reference hash mismatch")
    snapshot, snapshot_record = verified_model_snapshot(profile["models"]["voice_clone"])

    settings = profile["generation"]["clone"]
    seed = int(profile["generation"]["seed"])
    model = load_model(str(snapshot))
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []

    for index, line in enumerate(storyboard["tts_contract"]["lines"]):
        line_seed = seed + index
        mx.random.seed(line_seed)
        generated = list(
            model.generate(
                text=line["text"],
                ref_audio=str(reference),
                ref_text=profile["identity"]["reference_text"],
                lang_code=settings["language"],
                temperature=settings["temperature"],
                max_tokens=settings["max_tokens"],
                top_k=settings["top_k"],
                top_p=settings["top_p"],
                repetition_penalty=settings["repetition_penalty"],
                stream=False,
            )
        )
        if not generated:
            raise RuntimeError(f"Base-ICL returned no audio for {line['id']}")
        native_rate = int(generated[0].sample_rate)
        audio = np.concatenate(
            [np.asarray(item.audio, dtype=np.float32).reshape(-1) for item in generated]
        )
        if not len(audio) or not np.any(np.abs(audio) > 1e-6):
            raise RuntimeError(f"Empty audio for {line['id']}")

        raw = AUDIO_DIR / f"{index:02d}_{line['id']}.raw.wav"
        output = AUDIO_DIR / f"{index:02d}_{line['id']}.wav"
        sf.write(raw, audio, native_rate, subtype="PCM_16")
        # Compression precedes loudness normalization so the true-peak ceiling
        # does not prevent high-crest narration from reaching its target.
        run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(raw),
                "-af",
                "acompressor=threshold=0.1:ratio=4:attack=5:release=100:makeup=1,"
                "loudnorm=I=-16:TP=-1.5:LRA=10",
                "-ar", str(SAMPLE_RATE), "-ac", "2", "-c:a", "pcm_s16le", str(output),
            ]
        )
        raw.unlink()
        duration = duration_seconds(output)
        available = float(line["window"][1]) - float(line["window"][0])
        if duration <= 0.05 or duration > available:
            raise RuntimeError(
                f"{line['id']} duration {duration:.3f}s exceeds {available:.3f}s window"
            )
        asr = transcribe(output)
        validate_asr(line, asr)
        records.append(
            {
                "id": line["id"],
                "source_text": line["text"],
                "expected_normalized_asr": line["expected_normalized_asr"],
                "window": line["window"],
                "seed": line_seed,
                "path": str(output.relative_to(ROOT)),
                "sha256": sha256(output),
                "duration_seconds": round(duration, 4),
                "sample_rate": SAMPLE_RATE,
                "channels": 2,
                "codec": "pcm_s16le",
                "asr": asr,
            }
        )

    manifest = {
        "schema_version": 1,
        "status": "CANONICAL_TTS_GENERATED",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "storyboard_path": str(STORYBOARD.relative_to(ROOT)),
        "storyboard_sha256": sha256(STORYBOARD),
        "generator_path": str(Path(__file__).resolve().relative_to(ROOT)),
        "generator_sha256": sha256(Path(__file__).resolve()),
        "profile_path": str(PROFILE_PATH.relative_to(ROOT)),
        "profile_sha256": sha256(PROFILE_PATH),
        "reference_path": str(reference.relative_to(ROOT)),
        "reference_sha256": sha256(reference),
        "model_snapshot": str(snapshot),
        "model_snapshot_record": snapshot_record,
        "asr": {"python": str(ASR_PYTHON), "model": ASR_MODEL, "word_timestamps": True},
        "lines": records,
    }
    if len(records) != len(storyboard["tts_contract"]["lines"]):
        raise RuntimeError("Refusing to write incomplete TTS manifest")
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(f"PASS: {len(records)} canonical lines -> {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
