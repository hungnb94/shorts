#!/usr/bin/env python3
"""Generate and slot-fit Ronald Wayne TTS segments.

No voice cloning is performed. Edge TTS stock voice metadata lives in script-v1.json.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "ronaldwayne"
SCRIPT = PROJECT / "scripts" / "script-v1.json"
RAW = PROJECT / "tts" / "raw"
FITTED = PROJECT / "tts" / "fitted"
REPORT = PROJECT / "checks" / "tts-fit-report.json"
EDGE = Path.home() / ".hermes" / "hermes-agent" / "venv" / "bin" / "edge-tts"


def run(cmd: list[str | Path], *, retries: int = 1) -> None:
    for attempt in range(1, retries + 1):
        result = subprocess.run([str(x) for x in cmd], text=True, capture_output=True)
        if result.returncode == 0:
            return
        if attempt == retries:
            raise RuntimeError(f"Command failed: {' '.join(map(str, cmd))}\n{result.stderr}")
        time.sleep(attempt * 3)


def duration(path: Path) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(path),
    ], text=True)
    return float(out.strip())


def atempo_chain(speed: float) -> str:
    parts: list[float] = []
    while speed > 2.0:
        parts.append(2.0)
        speed /= 2.0
    while speed < 0.5:
        parts.append(0.5)
        speed /= 0.5
    parts.append(speed)
    return ",".join(f"atempo={x:.6f}" for x in parts)


def main() -> None:
    config = json.loads(SCRIPT.read_text(encoding="utf-8"))
    RAW.mkdir(parents=True, exist_ok=True)
    FITTED.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for seg in config["segments"]:
        if seg["type"] != "tts":
            continue
        raw = RAW / f"{seg['id']}.mp3"
        fitted = FITTED / f"{seg['id']}.wav"
        if not raw.exists():
            run([
                EDGE, "--voice", config["voice"]["name"],
                f"--rate={config['voice']['rate']}",
                f"--pitch={config['voice']['pitch']}",
                "--text", seg["text"], "--write-media", raw,
            ], retries=4)
        raw_seconds = duration(raw)
        slot = float(seg["end"] - seg["start"])
        speed = max(1.0, raw_seconds / max(slot - 0.06, 0.1))
        if speed > 1.18:
            raise RuntimeError(
                f"{seg['id']} needs atempo {speed:.3f}, above 1.18 bound; rewrite copy"
            )
        filters = [
            "highpass=f=70",
            "acompressor=threshold=0.1:ratio=3:attack=5:release=90:makeup=1",
        ]
        if speed > 1.001:
            filters.append(atempo_chain(speed))
        filters.extend([
            "loudnorm=I=-16:TP=-1.5:LRA=8",
            "aresample=48000",
            "apad",
            f"atrim=0:{slot}",
        ])
        run([
            "ffmpeg", "-y", "-v", "error", "-i", raw,
            "-af", ",".join(filters), "-ar", "48000", "-ac", "2",
            "-c:a", "pcm_s16le", fitted,
        ])
        rows.append({
            "id": seg["id"], "raw_seconds": round(raw_seconds, 3),
            "slot_seconds": slot, "atempo": round(speed, 4),
            "fitted_seconds": round(duration(fitted), 3),
        })
    REPORT.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
