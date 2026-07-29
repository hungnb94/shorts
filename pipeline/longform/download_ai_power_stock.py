#!/usr/bin/env python3
"""Download the licensed Pexels illustration set for the AI power long-form pilot."""
from __future__ import annotations

import json
import os
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output/projects/ai-power-bottleneck"
STOCK = PROJECT / "stock"
MANIFEST = PROJECT / "source/pexels-manifest.json"

ASSETS = {
    7140928: ("server_racks_blue", "data-center server racks"),
    1085656: ("network_cables_blue", "data-center networking"),
    30915831: ("substation_aerial", "electrical substation"),
    27427299: ("power_line_storm", "high-voltage transmission"),
    15357261: ("power_line_day", "high-voltage transmission"),
    9789926: ("wind_solar_field", "renewable generation"),
    35440511: ("wind_sunrise", "wind generation"),
    11396197: ("steel_frame_construction", "industrial construction"),
    33893697: ("large_site_construction", "large-site construction"),
    6079426: ("wire_spools_factory", "electrical wire manufacturing"),
    6755170: ("circuit_macro", "computer hardware"),
}


def probe(path: Path) -> dict:
    command = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,width,height,duration",
        "-of", "json", str(path),
    ]
    payload = json.loads(subprocess.check_output(command, text=True))
    return payload["streams"][0]


def main() -> None:
    key = os.environ.get("PEXELS_API_KEY")
    if not key:
        raise SystemExit("PEXELS_API_KEY not set")
    STOCK.mkdir(parents=True, exist_ok=True)
    rows = []
    for video_id, (slug, semantic_role) in ASSETS.items():
        request = urllib.request.Request(
            f"https://api.pexels.com/videos/videos/{video_id}",
            headers={"Authorization": key, "User-Agent": "shorts-production/1.0"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            video = json.load(response)
        candidates = [
            item for item in video.get("video_files", [])
            if item.get("file_type") == "video/mp4"
            and (item.get("width") or 0) >= 1920
            and (item.get("height") or 0) >= 1080
            and (item.get("width") or 0) > (item.get("height") or 0)
        ]
        if not candidates:
            raise RuntimeError(f"No >=1080p landscape rendition for Pexels {video_id}")
        selected = max(candidates, key=lambda item: (item["width"] * item["height"], item["width"]))
        output = STOCK / f"{slug}_{video_id}.mp4"
        current = probe(output) if output.exists() and output.stat().st_size >= 1024 else None
        needs_download = (
            current is None
            or int(current["width"]) < int(selected["width"])
            or int(current["height"]) < int(selected["height"])
        )
        if needs_download:
            temporary = output.with_suffix(".download.mp4")
            download = urllib.request.Request(selected["link"], headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(download, timeout=180) as src, temporary.open("wb") as dst:
                while chunk := src.read(1024 * 1024):
                    dst.write(chunk)
            temporary.replace(output)
        actual = probe(output)
        if int(actual["width"]) != int(selected["width"]) or int(actual["height"]) != int(selected["height"]):
            raise RuntimeError(
                f"Delivered rendition mismatch for {video_id}: expected "
                f"{selected['width']}x{selected['height']}, got {actual}"
            )
        row = {
            "pexels_id": video_id,
            "slug": slug,
            "path": str(output.relative_to(ROOT)),
            "page_url": video.get("url"),
            "creator": (video.get("user") or {}).get("name"),
            "semantic_role": semantic_role,
            "classification": "ILLUSTRATION",
            "license": "Pexels License",
            "license_url": "https://www.pexels.com/license/",
            "api_rendition": {"width": selected["width"], "height": selected["height"], "file_id": selected.get("id")},
            "actual_probe": actual,
        }
        rows.append(row)
        print(f"downloaded {video_id} -> {output.name} ({actual['width']}x{actual['height']})", flush=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps({"assets": rows}, indent=2) + "\n", encoding="utf-8")
    print(MANIFEST)


if __name__ == "__main__":
    main()
