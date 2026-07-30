#!/usr/bin/env python3
"""Add V10 citations, disclosures, evidence cards, CTA, and watermark."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "output/projects/capytech/clips/capytech_v10_zack_reaction_explainer_work"
BASE = WORK / "base_master.mp4"
RENDER_MANIFEST = WORK / "render_manifest.json"
FINAL = ROOT / "output/projects/capytech/final/2026-07-30-capytech_v10_zack_reaction_explainer.mp4"
FINAL_MANIFEST = WORK / "final_manifest.json"
STORYBOARD = ROOT / "output/projects/capytech/scripts/capytech_v10_zack_reaction_explainer_storyboard.json"
SOURCE_MANIFEST = ROOT / "output/projects/capytech/analysis/v9_real_drop_qc/preflight/source_crop_manifest.json"
SOURCE_USAGE = ROOT / "output/projects/capytech/analysis/v10_zack_reaction_explainer_qc/source_usage.json"
PEXELS_LICENSE = ROOT / "output/projects/capytech/source/v9_real_drop/pexels/license.json"
PEXELS = ROOT / "output/projects/capytech/source/v9_real_drop/pexels/36460444_aerial_city.mp4"
FONT = ROOT / "assets/fonts/Komika-Axis.ttf"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def require(path: Path, expected: str, label: str) -> None:
    if not path.is_file() or sha256(path) != expected:
        raise RuntimeError(f"{label} is stale")


def main() -> None:
    render = load(RENDER_MANIFEST)
    storyboard = load(STORYBOARD)
    require(BASE, render["artifact_sha256"], "base master")
    require(STORYBOARD, render["storyboard_sha256"], "storyboard")
    require(SOURCE_MANIFEST, render["source_manifest_sha256"], "source manifest")
    require(SOURCE_USAGE, render["source_usage_sha256"], "source usage")
    require(PEXELS_LICENSE, render["pexels_license_sha256"], "Pexels license")
    require(PEXELS, render["pexels_asset_sha256"], "Pexels asset")
    forbidden = storyboard["truth_contract"]["forbidden_copy"]
    approved_copy = [
        "DIFFERENT DEVICES • SURFACES • METHODS", "DIFFERENT TESTS",
        "POSSIBLE MECHANISM", "HEIGHT ALONE?", "LIKE", "SUBSCRIBE", "COMMENT",
    ]
    if any(term.lower() in " ".join(approved_copy).lower() for term in forbidden):
        raise RuntimeError("Forbidden ranking/deterministic copy entered compositor")
    font = FONT.as_posix()
    filters = [
        # Small factual citations. These identify sources; they do not imply endorsement.
        f"drawtext=fontfile='{font}':text='SOURCE\\: PBKreviews':x=38:y=1770:fontsize=34:"
        "fontcolor=white:box=1:boxcolor=black@0.65:enable='between(t,3,10)'",
        f"drawtext=fontfile='{font}':text='SOURCE\\: TechRax':x=38:y=1770:fontsize=34:"
        "fontcolor=white:box=1:boxcolor=black@0.65:enable='between(t,10,33.5)'",
        f"drawtext=fontfile='{font}':text='SOURCE\\: How Ridiculous':x=38:y=1770:fontsize=34:"
        "fontcolor=white:box=1:boxcolor=black@0.65:enable='between(t,33.5,58)'",
        # Required anthology disclaimer, including the full mechanism explanation.
        f"drawtext=fontfile='{font}':text='DIFFERENT DEVICES • SURFACES • METHODS':"
        "x=(w-text_w)/2:y=105:fontsize=37:fontcolor=white:box=1:boxcolor=black@0.72:"
        "enable='between(t,0.8,3)+between(t,33.5,58)'",
        # Compact labels preserve the locked concrete/red-dirt evidence underneath.
        f"drawtext=fontfile='{font}':text='DIFFERENT TESTS':x=45:y=155:"
        "fontsize=52:fontcolor=0x00D7FF:box=1:boxcolor=black@0.70:"
        "enable='between(t,42,49)'",
        f"drawtext=fontfile='{font}':text='CONCRETE FRAME':x=45:y=790:"
        "fontsize=38:fontcolor=white:box=1:boxcolor=black@0.68:enable='between(t,42,49)'",
        f"drawtext=fontfile='{font}':text='RED-DIRT FRAME':x=45:y=1010:"
        "fontsize=38:fontcolor=white:box=1:boxcolor=black@0.68:enable='between(t,42,49)'",
        f"drawtext=fontfile='{font}':text='POSSIBLE MECHANISM':x=45:y=1660:"
        "fontsize=46:fontcolor=white:box=1:boxcolor=black@0.70:enable='between(t,42,49)'",
        f"drawtext=fontfile='{font}':text='MORE STOPPING DISTANCE CAN REDUCE PEAK FORCE':"
        "x=45:y=1730:fontsize=31:fontcolor=white:box=1:boxcolor=black@0.68:"
        "enable='between(t,42,49)'",
        # Sequential CTA, not three simultaneous equal boxes.
        f"drawtext=fontfile='{font}':text='LIKE':x=(w-text_w)/2:y=1370:fontsize=82:"
        "fontcolor=0x00D7FF:box=1:boxcolor=black@0.78:enable='between(t,38.2,39)'",
        f"drawtext=fontfile='{font}':text='SUBSCRIBE':x=(w-text_w)/2:y=1370:fontsize=82:"
        "fontcolor=white:box=1:boxcolor=0xD32222@0.88:enable='between(t,39,40.2)'",
        f"drawtext=fontfile='{font}':text='COMMENT':x=(w-text_w)/2:y=1370:fontsize=82:"
        "fontcolor=0x00D7FF:box=1:boxcolor=black@0.78:enable='between(t,40.2,42)'",
        # Signature line appears after the split proof is readable and stays below upper evidence.
        f"drawtext=fontfile='{font}':text='THE WHOLE SCREEN CAME OFF?!':x=(w-text_w)/2:"
        "y=1510:fontsize=55:fontcolor=white:box=1:boxcolor=black@0.75:"
        "enable='between(t,30,33.2)'",
        f"drawtext=fontfile='{font}':text='HEIGHT ALONE?':x=(w-text_w)/2:y=270:"
        "fontsize=88:fontcolor=0x00D7FF:box=1:boxcolor=black@0.72:enable='between(t,56,58)'",
        # Moving watermark changes corners while avoiding captions/evidence.
        f"drawtext=fontfile='{font}':text='CAPYTECH':fontsize=30:fontcolor=white@0.55:"
        "x='if(lt(mod(t,12),6),45,w-text_w-45)':y='if(lt(mod(t,16),8),155,1700)'",
    ]
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(BASE),
               "-vf", ",".join(filters), "-map", "0:v", "-map", "0:a", "-c:v", "libx264",
               "-preset", "slow", "-crf", "15", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", "30",
               "-vsync", "cfr", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
               "-movflags", "+faststart", str(FINAL)]
    subprocess.run(command, cwd=ROOT, check=True)
    manifest = {
        "schema_version": 2, "status": "FINAL_COMPOSITED",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "artifact": rel(FINAL), "artifact_sha256": sha256(FINAL),
        "base_artifact_sha256": sha256(BASE),
        "compositor_path": rel(Path(__file__).resolve()),
        "compositor_sha256": sha256(Path(__file__).resolve()),
        "renderer_path": render["renderer_path"], "renderer_sha256": render["renderer_sha256"],
        "render_manifest_sha256": sha256(RENDER_MANIFEST),
        "storyboard_sha256": sha256(STORYBOARD),
        "tts_manifest_sha256": render["tts_manifest_sha256"],
        "tts_generator_sha256": render["tts_generator_sha256"],
        "profile_sha256": render["profile_sha256"],
        "source_manifest_sha256": sha256(SOURCE_MANIFEST),
        "source_usage_sha256": sha256(SOURCE_USAGE),
        "reaction_gate_sha256": render["reaction_gate_sha256"],
        "pexels_license_sha256": sha256(PEXELS_LICENSE),
        "pexels_asset_sha256": sha256(PEXELS),
        "font_sha256": sha256(FONT),
        "caption_calibration_sha256": render["caption_calibration_sha256"],
        "implementation_review_sha256": render["implementation_review_sha256"],
        "audio_assets": render["audio_assets"],
        "audio_asset_dag_sha256": hashlib.sha256(
            json.dumps(render["audio_assets"], sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "value_adds": [
            "source citations", "anthology disclaimer", "locked-frame mechanism evidence",
            "moving impact tracker", "stopping-distance annotation", "two real scale changes",
            "sequential triple CTA", "moving watermark", "non-ranking causal-loop card"
        ],
        "surface_card_copy": ["DIFFERENT TESTS", "POSSIBLE MECHANISM"],
        "publication_status": "NOT_UPLOADED", "virality_status": "VIRALITY_UNPROVEN",
        "exact_final_review_status": "UNVERIFIED",
    }
    FINAL_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"PASS final composite: {FINAL.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
