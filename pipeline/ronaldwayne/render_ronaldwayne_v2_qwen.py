#!/usr/bin/env python3
"""Assemble Ronald Wayne v2 with Qwen narrator and verified v1 visuals.

This script never writes v1. It stream-copies the v1 video track, rebuilds the
60-second audio timeline from Qwen TTS plus the two verified Ronald Wayne source
quotes, mixes the existing locally generated music bed, and writes v2-Qwen.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "ronaldwayne"
SCRIPT = PROJECT / "scripts" / "script-v2-qwen.json"
V1 = PROJECT / "2026-07-25-ronald-wayne-v1.mp4"
V2 = PROJECT / "2026-07-25-ronald-wayne-v2-qwen.mp4"
CONTROL = PROJECT / "checks-v2-qwen" / "v1-control.sha256"
TTS = PROJECT / "tts-qwen" / "fitted"
WORK = PROJECT / "work" / "v2-qwen"
AUDIO = WORK / "audio"
MUSIC = PROJECT / "work" / "v1" / "audio" / "music-bed.wav"
CBS = PROJECT / "source" / "video" / "M3R50CA9ok8.mp4"
NEXT = PROJECT / "source" / "video" / "YAF2-U7InWE.mp4"
REPORT = PROJECT / "checks-v2-qwen" / "assembly.json"
TOTAL = 60.0


def run(cmd: list[str | Path]) -> None:
    print("+", " ".join(str(item) for item in cmd), flush=True)
    subprocess.run([str(item) for item in cmd], check=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def duration(path: Path) -> float:
    value = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        text=True,
    )
    return float(value.strip())


def exact_slot(source: Path, output: Path, seconds: float, prefix_filter: str = "") -> None:
    filters = []
    if prefix_filter:
        filters.append(prefix_filter)
    filters.extend(
        [
            f"apad=whole_dur={seconds}",
            f"atrim=0:{seconds}",
            "aresample=48000",
        ]
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            source,
            "-af",
            ",".join(filters),
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "pcm_s16le",
            output,
        ]
    )


def main() -> None:
    AUDIO.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    required = [SCRIPT, V1, CONTROL, MUSIC, CBS, NEXT]
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)

    expected_v1 = CONTROL.read_text().split()[0]
    actual_v1 = sha256(V1)
    if actual_v1 != expected_v1:
        raise RuntimeError(f"v1 control hash mismatch: {actual_v1}")

    config = json.loads(SCRIPT.read_text(encoding="utf-8"))
    pieces: list[Path] = []
    records = []
    for index, segment in enumerate(config["segments"]):
        slot = float(segment["end"] - segment["start"])
        output = AUDIO / f"slot-{index:02d}-{segment['id']}.wav"
        if segment["type"] == "tts":
            source = TTS / f"{segment['id']}.wav"
            if not source.is_file():
                raise FileNotFoundError(source)
            exact_slot(source, output, slot)
            source_kind = "qwen_tts"
        else:
            source_video = {
                "M3R50CA9ok8": CBS,
                "YAF2-U7InWE": NEXT,
            }[segment["source"]]
            raw = AUDIO / f"raw-{segment['id']}.wav"
            speed = 1.08 if segment["id"] == "cbs_quote" else 1.0
            source_take = slot * speed
            run(
                [
                    "ffmpeg",
                    "-y",
                    "-v",
                    "error",
                    "-i",
                    source_video,
                    "-ss",
                    str(segment["source_start"]),
                    "-t",
                    str(source_take),
                    "-vn",
                    "-af",
                    "highpass=f=65,loudnorm=I=-16:TP=-1.5:LRA=8",
                    "-ar",
                    "48000",
                    "-ac",
                    "2",
                    "-c:a",
                    "pcm_s16le",
                    raw,
                ]
            )
            exact_slot(raw, output, slot, f"atempo={speed}")
            source_kind = "ronald_wayne_source_voice"
        pieces.append(output)
        records.append(
            {
                "index": index,
                "id": segment["id"],
                "type": source_kind,
                "start": segment["start"],
                "end": segment["end"],
                "duration": round(duration(output), 4),
                "sha256": sha256(output),
            }
        )

    concat = AUDIO / "voice-concat.txt"
    concat.write_text(
        "".join(f"file '{piece.as_posix()}'\n" for piece in pieces),
        encoding="utf-8",
    )
    voice = AUDIO / "voice-timeline.wav"
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat,
            "-c:a",
            "pcm_s16le",
            voice,
        ]
    )
    voice_exact = AUDIO / "voice-timeline-exact.wav"
    exact_slot(voice, voice_exact, TOTAL)

    mixed = AUDIO / "final-mix.wav"
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            voice_exact,
            "-i",
            MUSIC,
            "-filter_complex",
            "[1:a]volume=0.32[m];[m][0:a]sidechaincompress=threshold=0.025:ratio=8:attack=8:release=180[ducked];"
            "[0:a][ducked]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=8[a]",
            "-map",
            "[a]",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "pcm_s16le",
            mixed,
        ]
    )

    temp = V2.with_suffix(".tmp.mp4")
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            V1,
            "-i",
            mixed,
            "-t",
            str(TOTAL),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            temp,
        ]
    )
    temp.replace(V2)
    report = {
        "artifact": str(V2.relative_to(ROOT)),
        "v1_source_sha256": actual_v1,
        "v2_sha256": sha256(V2),
        "duration": duration(V2),
        "segments": records,
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
