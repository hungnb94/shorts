#!/usr/bin/env python3
"""Post-render Capytech V9 citations and comparison value-adds."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "output/projects/capytech/clips/capytech_v9_real_drop_work"
BASE = WORK / "base_master.mp4"
RENDER_MANIFEST = WORK / "render_manifest.json"
STORYBOARD = ROOT / "output/projects/capytech/scripts/capytech_v9_real_drop_storyboard.json"
SOURCE_MANIFEST = ROOT / "output/projects/capytech/analysis/v9_real_drop_qc/preflight/source_crop_manifest.json"
SOURCE_USAGE = ROOT / "output/projects/capytech/analysis/v9_real_drop_qc/source_usage.json"
LICENSE = ROOT / "output/projects/capytech/source/v9_real_drop/pexels/license.json"
FONT = ROOT / "assets/fonts/Komika-Axis.ttf"
FINAL = ROOT / "output/projects/capytech/final/2026-07-30-capytech_v9_real_drop.mp4"
FINAL_MANIFEST = ROOT / "output/projects/capytech/analysis/v9_real_drop_qc/final_render_manifest.json"
CONCRETE_SOURCE = ROOT / "output/projects/capytech/source/v9_real_drop/master/r1_1m_impact_result.mp4"
DIRT_SOURCE = ROOT / "output/projects/capytech/source/v9_real_drop/master/w2xGzHjYCcY_full.mp4"
SURFACE_CARD = WORK / "surface_compare.png"
DURATION = 58.0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text())


def require_hash(path: Path, expected: str, label: str) -> None:
    if not path.is_file() or sha256(path) != expected:
        raise RuntimeError(f"Stale or missing compositor prerequisite: {label}")


def build_surface_card() -> None:
    stills = []
    for source, timestamp, name in (
        (CONCRETE_SOURCE, 5.0, "surface_concrete.jpg"),
        (DIRT_SOURCE, 467.0, "surface_red_dirt.jpg"),
    ):
        output = WORK / name
        subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-ss", str(timestamp), "-i", str(source), "-frames:v", "1", str(output),
            ],
            cwd=ROOT,
            check=True,
        )
        stills.append(Image.open(output).convert("RGB"))
    card = Image.new("RGB", (920, 420), (13, 18, 28))
    draw = ImageDraw.Draw(card)
    label_font = ImageFont.truetype(str(FONT), 46)
    symbol_font = ImageFont.truetype(str(FONT), 76)
    left = ImageOps.fit(stills[0], (390, 300), method=Image.Resampling.LANCZOS)
    right = ImageOps.fit(stills[1], (390, 300), method=Image.Resampling.LANCZOS)
    card.paste(left, (20, 92))
    card.paste(right, (510, 92))
    draw.rounded_rectangle((6, 6, 914, 414), radius=24, outline=(255, 215, 64), width=8)
    draw.text((94, 22), "CONCRETE", font=label_font, fill=(255, 255, 255))
    draw.text((596, 22), "RED DIRT", font=label_font, fill=(255, 215, 64))
    draw.text((435, 198), "≠", font=symbol_font, fill=(255, 82, 82), stroke_width=5, stroke_fill=(0, 0, 0))
    SURFACE_CARD.parent.mkdir(parents=True, exist_ok=True)
    card.save(SURFACE_CARD)


def main() -> None:
    storyboard = load(STORYBOARD)
    render_manifest = load(RENDER_MANIFEST)
    source_manifest = load(SOURCE_MANIFEST)
    source_usage = load(SOURCE_USAGE)
    license_record = load(LICENSE)
    require_hash(BASE, render_manifest["base_master_sha256"], "base master")
    require_hash(STORYBOARD, render_manifest["storyboard_sha256"], "storyboard")
    require_hash(SOURCE_MANIFEST, render_manifest["source_manifest_sha256"], "source manifest")
    require_hash(SOURCE_USAGE, render_manifest["source_usage_sha256"], "source usage")
    require_hash(FONT, render_manifest["font_sha256"], "Komika Axis")
    if sha256(ROOT / license_record["local_path"]) != license_record["sha256"]:
        raise RuntimeError("Pexels acquisition record does not match asset")

    expected_labels = ["WAIST HEIGHT", "10 STORIES", "300 FEET", "1,000 FEET"]
    if storyboard["truthful_labels_exact"] != expected_labels:
        raise RuntimeError("Truthful categorical labels changed")
    disclaimer = storyboard["comparison_disclaimer"]["required_on_screen_text"]
    if disclaimer != "DIFFERENT DEVICES • SURFACES • METHODS":
        raise RuntimeError("Comparison disclaimer changed")
    build_surface_card()

    font = str(FONT).replace(":", r"\:")
    # Factual citations identify sources; they do not assert permission or legal
    # clearance. The scale and outcome ribbons are categorical, not a controlled
    # durability ranking.
    filters = [
        f"drawtext=fontfile='{font}':text='SOURCE\\: PBKreviews':fontcolor=white@0.88:"
        "fontsize=30:box=1:boxcolor=black@0.58:boxborderw=9:x=w-tw-36:y=110:"
        "enable='between(t,3,11)'",
        f"drawtext=fontfile='{font}':text='SOURCE\\: TechRax':fontcolor=white@0.88:"
        "fontsize=30:box=1:boxcolor=black@0.58:boxborderw=9:x=w-tw-36:y=110:"
        "enable='between(t,11,34)'",
        f"drawtext=fontfile='{font}':text='SOURCE\\: How Ridiculous':fontcolor=white@0.88:"
        "fontsize=30:box=1:boxcolor=black@0.58:boxborderw=9:x=w-tw-36:y=110:"
        "enable='between(t,34,58)'",
        f"drawtext=fontfile='{font}':text='PEXELS 36460444 • ILLUSTRATION':"
        "fontcolor=yellow:fontsize=32:box=1:boxcolor=black@0.78:boxborderw=10:"
        "x=(w-tw)/2:y=180:enable='between(t,38,40)'",
        f"drawtext=fontfile='{font}':text='{disclaimer}':"
        "fontcolor=white:fontsize=31:box=1:boxcolor=black@0.72:boxborderw=12:"
        "x=(w-tw)/2:y=h-th-84:enable='between(t,0.8,3)+between(t,34,56)'",
        f"drawtext=fontfile='{font}':text='WAIST HEIGHT  →  MOSTLY INTACT':"
        "fontcolor=white:fontsize=34:box=1:boxcolor=0x123047@0.78:boxborderw=12:"
        "x=(w-tw)/2:y=240:enable='between(t,8,11)'",
        f"drawtext=fontfile='{font}':text='10 STORIES  →  SHATTERED BACK':"
        "fontcolor=white:fontsize=34:box=1:boxcolor=0x123047@0.78:boxborderw=12:"
        "x=(w-tw)/2:y=240:enable='between(t,18,22)'",
        f"drawtext=fontfile='{font}':text='300 FEET  →  SCREEN SEPARATED':"
        "fontcolor=white:fontsize=34:box=1:boxcolor=0x7F1D1D@0.82:boxborderw=12:"
        "x=(w-tw)/2:y=240:enable='between(t,29,34)'",
        f"drawtext=fontfile='{font}':text='1,000 FEET  →  DISPLAY POWERED':"
        "fontcolor=yellow:fontsize=36:box=1:boxcolor=0x14532D@0.86:boxborderw=13:"
        "x=(w-tw)/2:y=240:enable='between(t,49,56)'",
        f"drawtext=fontfile='{font}':text='OUTCOME FLIPS':fontcolor=yellow:"
        "fontsize=52:borderw=6:bordercolor=black:x=(w-tw)/2:y=360:"
        "enable='between(t,49,52.5)'",
        f"drawtext=fontfile='{font}':text='HEIGHT IS NOT THE ONLY VARIABLE':fontcolor=white:"
        "fontsize=40:box=1:boxcolor=0x123047@0.80:boxborderw=13:"
        "x=(w-tw)/2:y=470:enable='between(t,45,49)'",
    ]
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(BASE),
            "-loop", "1", "-t", str(DURATION), "-i", str(SURFACE_CARD),
            "-filter_complex",
            f"[0:v]{','.join(filters)}[decorated];"
            "[1:v]scale=920:420[card];"
            "[decorated][card]overlay=(W-w)/2:470:enable='between(t,42,44.6)'[v]",
            "-map", "[v]", "-map", "0:a:0",
            "-c:v", "libx264", "-preset", "medium", "-crf", "16",
            "-profile:v", "high", "-level:v", "4.2", "-pix_fmt", "yuv420p",
            "-r", "30", "-fps_mode", "cfr", "-video_track_timescale", "15360",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-t", str(DURATION), "-movflags", "+faststart", str(FINAL),
        ],
        cwd=ROOT,
        check=True,
    )

    source_hashes = {
        source["youtube_id"] + ":" + Path(source["local_mp4_path"]).name: {
            "media": source["local_mp4_sha256"],
            "info_json": source["info_json_sha256"],
        }
        for source in source_manifest["sources"]
    }
    manifest = {
        "schema_version": 1,
        "status": "FINAL_RENDERED_NOT_VERIFIED",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "artifact": rel(FINAL),
        "artifact_sha256": sha256(FINAL),
        "base_master": rel(BASE),
        "base_master_sha256": sha256(BASE),
        "renderer_path": "pipeline/capytech/render_capytech_v9_real_drop.py",
        "renderer_sha256": render_manifest["renderer_sha256"],
        "compositor_path": rel(Path(__file__).resolve()),
        "compositor_sha256": sha256(Path(__file__).resolve()),
        "storyboard_sha256": sha256(STORYBOARD),
        "source_manifest_sha256": sha256(SOURCE_MANIFEST),
        "source_usage_sha256": sha256(SOURCE_USAGE),
        "source_hashes": source_hashes,
        "tts_manifest_sha256": render_manifest["tts_manifest_sha256"],
        "reaction_gate_sha256": render_manifest["reaction_gate_sha256"],
        "font_sha256": sha256(FONT),
        "caption_calibration_sha256": render_manifest["caption_calibration_sha256"],
        "pexels_license_sha256": sha256(LICENSE),
        "pexels_asset_sha256": license_record["sha256"],
        "value_adds": [
            "multi-source factual citations",
            "categorical height/outcome comparison",
            "different-devices/surfaces/methods counter-context",
        ],
        "citation_boundary": "Citations are sourcing, not permission or copyright clearance.",
        "output": {
            "width": 1080,
            "height": 1920,
            "fps": 30,
            "duration_seconds": DURATION,
            "video": "H.264 yuv420p",
            "audio": "AAC 48kHz stereo",
        },
        "ffmpeg_version": subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True, check=True
        ).stdout.splitlines()[0],
        "publication_status": "NOT_UPLOADED",
        "virality_status": "VIRALITY_UNPROVEN",
    }
    FINAL_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    FINAL_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"PASS final composite: {rel(FINAL)}")


if __name__ == "__main__":
    main()
