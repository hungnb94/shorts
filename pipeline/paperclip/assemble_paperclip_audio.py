#!/usr/bin/env python3
"""Assemble the selected narrator and Kyle payoff excerpt into final timing audio."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "paperclip"
MANIFEST = PROJECT / "scripts" / "narration-v1.json"
VOICE_REPORT = PROJECT / "tts-qwen-zack" / "generation-report.json"
FITTED = PROJECT / "tts-qwen-zack" / "fitted"
SOURCE = PROJECT / "source" / "8s3bdVxuFBs.mp4"
EVIDENCE = PROJECT / "hook-gate" / "evidence.json"
OUT_DIR = PROJECT / "audio"
OUT = OUT_DIR / "narration-mix-v1.wav"
REPORT = OUT_DIR / "audio-assembly-v1.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def duration(path: Path) -> float:
    result = subprocess.run(
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
        check=True,
        text=True,
        capture_output=True,
    )
    return float(result.stdout.strip())


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    voice_report = json.loads(VOICE_REPORT.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    if manifest["voice_profile"] != "ronald_wayne_zack_style_qwen":
        raise RuntimeError("Selected voice manifest mismatch")
    if not evidence["override"]["allows_internal_render"]:
        raise RuntimeError("Hook Gate blocks internal render")
    if evidence["override"]["allows_publication"]:
        raise RuntimeError("Internal override must not authorize publication")
    if len(voice_report["segments"]) != len(manifest["segments"]):
        raise RuntimeError("Voice report does not cover the narration manifest")

    paths: list[Path] = []
    filters: list[str] = []
    labels: list[str] = []
    rows: list[dict] = []
    report_by_id = {row["id"]: row for row in voice_report["segments"]}
    for index, segment in enumerate(manifest["segments"]):
        path = FITTED / f"{segment['id']}.wav"
        if not path.is_file():
            raise FileNotFoundError(path)
        voice_row = report_by_id[segment["id"]]
        if voice_row["status"] != "fitted":
            raise RuntimeError(f"Unfitted narration segment: {segment['id']}")
        paths.append(path)
        start_ms = round(float(segment["slot_start"]) * 1000)
        slot = float(segment["slot_end"]) - float(segment["slot_start"])
        label = f"a{index}"
        filters.append(
            f"[{index}:a]atrim=0:{slot:.6f},asetpts=PTS-STARTPTS,"
            f"adelay=delays={start_ms}:all=1[{label}]"
        )
        labels.append(f"[{label}]")
        rows.append(
            {
                "id": segment["id"],
                "path": str(path.relative_to(ROOT)),
                "start": segment["slot_start"],
                "end": segment["slot_end"],
                "sha256": voice_row["fitted_sha256"],
            }
        )

    source_index = len(paths)
    payoff = manifest["source_payoff"]
    source_start = 657.82
    source_end = 664.42
    paths.append(SOURCE)
    filters.append(
        f"[{source_index}:a]atrim=start={source_start}:end={source_end},"
        "asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-2:LRA=8,"
        f"adelay=delays={round(float(payoff['start']) * 1000)}:all=1[apayoff]"
    )
    labels.append("[apayoff]")
    target = float(manifest["target_duration"])
    filters.append(
        "".join(labels)
        + f"amix=inputs={len(labels)}:duration=longest:dropout_transition=0:normalize=0,"
        + f"apad=whole_dur={target:.6f},atrim=0:{target:.6f},aresample=48000,"
        + "loudnorm=I=-16:TP=-1.8:LRA=8[aout]"
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    command = ["ffmpeg", "-y", "-v", "error"]
    for path in paths:
        command.extend(["-i", str(path)])
    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[aout]",
            "-t",
            f"{target:.6f}",
            "-c:a",
            "pcm_s24le",
            "-ar",
            "48000",
            "-ac",
            "2",
            str(OUT),
        ]
    )
    subprocess.run(command, check=True)
    actual_duration = duration(OUT)
    if abs(actual_duration - target) > 0.02:
        raise RuntimeError(f"Audio duration mismatch: {actual_duration}")

    report = {
        "schema_version": 1,
        "project": "paperclip_v1",
        "voice_profile": manifest["voice_profile"],
        "voice_publication_gate": manifest["voice_publication_gate"],
        "target_duration": target,
        "actual_duration": actual_duration,
        "output": str(OUT.relative_to(ROOT)),
        "output_sha256": sha256(OUT),
        "segments": rows,
        "source_payoff": {
            "source": str(SOURCE.relative_to(ROOT)),
            "source_start": source_start,
            "source_end": source_end,
            "timeline_start": payoff["start"],
            "timeline_end": payoff["end"],
            "rights_state": "BLOCKED_PENDING_TED_CLEARANCE_OR_DOCUMENTED_EXCEPTION",
        },
        "human_hook_gate": evidence["human_retell"]["state"],
        "internal_render_override": evidence["override"]["state"],
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"audio": str(OUT), "duration": actual_duration}, indent=2))


if __name__ == "__main__":
    main()
