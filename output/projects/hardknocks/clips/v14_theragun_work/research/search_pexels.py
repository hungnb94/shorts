#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import urllib.parse
from pathlib import Path

OUT = Path(__file__).resolve().parent / "pexels_candidates.json"
queries = [
    "jigsaw power tool workshop",
    "inventor prototype workshop",
    "shoulder physical therapy recovery",
    "massage gun recovery",
]
key = os.environ.get("PEXELS_API_KEY")
if not key:
    raise SystemExit("PEXELS_API_KEY not set")
results = []
for query in queries:
    url = "https://api.pexels.com/videos/search?" + urllib.parse.urlencode(
        {"query": query, "per_page": 12, "orientation": "portrait"}
    )
    response = subprocess.run(
        ["curl", "-sS", "--fail-with-body", "-H", f"Authorization: {key}", url],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(response.stdout)
    for video in payload.get("videos", []):
        files = sorted(
            video.get("video_files", []),
            key=lambda item: (item.get("height") or 0, item.get("width") or 0),
            reverse=True,
        )
        results.append(
            {
                "query": query,
                "id": video["id"],
                "duration": video.get("duration"),
                "page_url": video.get("url"),
                "image": video.get("image"),
                "user": video.get("user", {}).get("name"),
                "files": [
                    {
                        "id": item.get("id"),
                        "quality": item.get("quality"),
                        "width": item.get("width"),
                        "height": item.get("height"),
                        "file_type": item.get("file_type"),
                        "link": item.get("link"),
                    }
                    for item in files
                ],
            }
        )
OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
print(f"saved {len(results)} candidates to {OUT}")
