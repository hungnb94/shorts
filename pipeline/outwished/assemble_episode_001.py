#!/usr/bin/env python3
"""Assemble accepted OUTWISHED episode 001 shots into one visual/SFX cut."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SHOTS = ROOT / "output/projects/outwished/shots"
FINAL_DIR = ROOT / "output/projects/outwished/final"
ANALYSIS_DIR = ROOT / "output/projects/outwished/analysis"
DATE = "2026-07-22"
FINAL = FINAL_DIR / f"{DATE}-outwished-001-trimmed-visual-cut.mp4"
MANIFEST = FINAL_DIR / f"{DATE}-outwished-001-trimmed-visual-cut.json"
CONTACT_SHEET = ANALYSIS_DIR / f"{DATE}-outwished-001-trimmed-contact-sheet.jpg"

EDL: list[tuple[Path, float, float, str]] = [
    (SHOTS / "shot-001-v3-raw.mp4", 0.00, 4.00, "keep complete hook action"),
    (SHOTS / "shot-002-raw.mp4", 0.00, 3.15, "intruders enter; Nico notices them"),
    (SHOTS / "shot-002-raw.mp4", 3.70, 5.00, "Nico is already hidden behind the island"),
    (SHOTS / "shot-003-raw.mp4", 0.00, 5.20, "tray diversion, hidden passage, watch call"),
    (SHOTS / "shot-004-raw.mp4", 0.00, 5.00, "false rescue remains visually coherent"),
    (SHOTS / "shot-005-raw.mp4", 0.00, 4.00, "betrayal and restraint remain coherent"),
    (SHOTS / "shot-006-raw.mp4", 0.00, 5.80, "vault clue and first officer gesture"),
    (SHOTS / "shot-007-raw.mp4", 0.00, 5.00, "basement lock-in and green glint"),
    (SHOTS / "shot-008-raw.mp4", 0.00, 8.00, "Lamp discovery and Veyr reveal"),
    (SHOTS / "shot-009-raw.mp4", 0.00, 9.00, "wish setup remains visually coherent"),
    (SHOTS / "shot-010-raw.mp4", 0.00, 7.25, "teleport, human tower, and vault close"),
]


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(command))
    return subprocess.run(command, check=True, capture_output=capture, text=True)


def probe(path: Path) -> dict[str, Any]:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels,channel_layout",
            "-of",
            "json",
            str(path),
        ],
        capture=True,
    )
    return json.loads(result.stdout)


def main() -> None:
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    missing = sorted({str(path) for path, _, _, _ in EDL if not path.exists()})
    if missing:
        raise FileNotFoundError(f"Missing accepted source clips: {missing}")

    source_metadata = []
    durations = []
    probe_cache: dict[Path, dict[str, Any]] = {}
    for source, source_in, source_out, reason in EDL:
        metadata = probe_cache.setdefault(source, probe(source))
        streams = metadata["streams"]
        if not any(stream["codec_type"] == "video" for stream in streams):
            raise ValueError(f"No video stream: {source}")
        if not any(stream["codec_type"] == "audio" for stream in streams):
            raise ValueError(f"No audio stream: {source}")
        source_duration = float(metadata["format"]["duration"])
        if not 0 <= source_in < source_out <= source_duration + 0.001:
            raise ValueError(
                f"Invalid EDL range for {source}: {source_in:.3f}-{source_out:.3f} "
                f"against {source_duration:.3f}s"
            )
        duration = source_out - source_in
        durations.append(duration)
        source_metadata.append(
            {
                "path": str(source.relative_to(ROOT)),
                "source_in_seconds": round(source_in, 3),
                "source_out_seconds": round(source_out, 3),
                "duration_seconds": round(duration, 6),
                "reason": reason,
            }
        )

    filter_parts = []
    concat_inputs = []
    for index, ((_, source_in, source_out, _), duration) in enumerate(zip(EDL, durations)):
        video_label = f"v{index}"
        audio_label = f"a{index}"
        filter_parts.append(
            f"[{index}:v]"
            "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,"
            "crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2,"
            "fps=24,setsar=1,format=yuv420p,"
            f"trim=start={source_in:.6f}:end={source_out:.6f},setpts=PTS-STARTPTS[{video_label}]"
        )
        audio_filters = [
            "aresample=48000",
            "aformat=sample_fmts=fltp:channel_layouts=stereo",
            f"atrim=start={source_in:.6f}:end={source_out:.6f}",
            "asetpts=PTS-STARTPTS",
        ]
        if index > 0:
            audio_filters.append("afade=t=in:st=0:d=0.08")
        if index < len(durations) - 1:
            fade_start = max(0.0, duration - 0.18)
            audio_filters.append(f"afade=t=out:st={fade_start:.6f}:d=0.18")
        filter_parts.append(f"[{index}:a]{','.join(audio_filters)}[{audio_label}]")
        concat_inputs.append(f"[{video_label}][{audio_label}]")

    filter_parts.append(
        "".join(concat_inputs)
        + f"concat=n={len(EDL)}:v=1:a=1[vcat][aout]"
    )
    filter_parts.append("[vcat]fps=24,settb=1/24,setpts=N[vout]")
    filter_graph = ";".join(filter_parts)

    command = ["ffmpeg", "-y"]
    for source, _, _, _ in EDL:
        command.extend(["-i", str(source)])
    command.extend(
        [
            "-filter_complex",
            filter_graph,
            "-map",
            "[vout]",
            "-map",
            "[aout]",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "16",
            "-profile:v",
            "high",
            "-level:v",
            "4.2",
            "-pix_fmt",
            "yuv420p",
            "-r",
            "24",
            "-fps_mode",
            "cfr",
            "-video_track_timescale",
            "12288",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            str(FINAL),
        ]
    )
    run(command)

    final_metadata = probe(FINAL)
    manifest = {
        "artifact": str(FINAL.relative_to(ROOT)),
        "kind": "trimmed visual/SFX assembly retaining only coherent generated intervals",
        "excluded": [
            "shot-001-v2.mp4 (superseded)",
            "shot-004-raw-rejected-identity-v1.mp4",
            "shot-005-raw-rejected-actions-v1.mp4",
            "SHOT-011 and SHOT-012 (no generated MP4 exists)",
            "dialogue, full captions, metadata, CTA, and watermark post-production",
            "SHOT-002 3.15-3.70s (abrupt floor-drop transition)",
            "SHOT-003 5.20s-end (floating gloved hand after door closes)",
            "SHOT-006 5.80s-end (repetitive pointing tail)",
            "SHOT-010 7.25s-end (spatially inconsistent portrait close-up)",
        ],
        "sources": source_metadata,
        "final_probe": final_metadata,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(FINAL),
            "-vf",
            "fps=1/3.2,scale=216:-2:flags=lanczos,tile=5x4:padding=4:margin=4:color=black",
            "-frames:v",
            "1",
            str(CONTACT_SHEET),
        ]
    )

    print(FINAL)
    print(MANIFEST)
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
