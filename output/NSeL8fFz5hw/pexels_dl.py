#!/usr/bin/env python3
"""Search and download Pexels B-roll for Giannis 3 videos. API key from env only."""
import os, json, subprocess
from pathlib import Path

CACHE = Path("output/pexels")
CACHE.mkdir(parents=True, exist_ok=True)
API_KEY = os.environ.get("PEXELS_API_KEY")

QUERIES = {
    # V1 Ferrari: luxury car, watch, art, real estate, race
    "ferrari_red": "ferrari red car driving",
    "luxury_watch": "luxury watch closeup",
    "art_gallery": "art gallery painting",
    "real_estate": "luxury house exterior modern",
    "race_track": "running race track athlete",
    # V2 broke: empty stadium, luxury car, mansion, stock market
    "empty_stadium": "empty stadium seats",
    "luxury_car_drive": "luxury car driving city",
    "mansion_exterior": "mansion exterior pool",
    "stock_chart": "stock market chart trading",
    "quiet_reading": "person reading book quiet",
    # V3 lawyer: office meeting, contract, suited men, books
    "office_meeting": "business meeting office suited",
    "contract_signing": "contract signing handshake",
    "suited_businessman": "businessman suit walking",
    "books_finance": "books finance learning desk",
}

def search_pexels(query, per_page=3):
    cmd = [
        'curl', '-s', '-G',
        '-H', f'Authorization: {API_KEY}',
        'https://api.pexels.com/videos/search',
        '--data-urlencode', f'query={query}',
        '--data-urlencode', 'per_page=3',
        '--data-urlencode', 'orientation=portrait',
        '-o', '/tmp/pexels_search.json',
        '-w', '%{http_code}'
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    code = r.stdout.strip()
    if code != '200':
        print(f"  HTTP {code} for '{query}'")
        return []
    try:
        data = json.loads(Path('/tmp/pexels_search.json').read_text())
    except:
        return []
    results = []
    for v in data.get('videos', [])[:3]:
        # Pick the best vertical file: prefer HD (720p+)
        best = None
        for f in v.get('video_files', []):
            w, h = f.get('width', 0), f.get('height', 0)
            if h > w and w >= 540:  # portrait + at least 540p wide
                if not best or f.get('height', 0) > best.get('height', 0):
                    best = f
        if not best:
            for f in v.get('video_files', []):
                w, h = f.get('width', 0), f.get('height', 0)
                if h > w:
                    best = f
                    break
        if best:
            results.append({'id': v['id'], 'url': best['link'], 'duration': v.get('duration', 0)})
    return results

def download_pexels(video_id, url, key):
    out_path = CACHE / f"{key}_{video_id}.mp4"
    if out_path.exists() and out_path.stat().st_size > 50000:
        print(f"  ✓ Cached: {out_path.name} ({out_path.stat().st_size//1024}KB)")
        return out_path
    print(f"  ↓ Downloading {video_id} -> {out_path.name}")
    r = subprocess.run(['curl', '-L', '-s', '-o', str(out_path), url], capture_output=True, timeout=60)
    if r.returncode == 0 and out_path.exists() and out_path.stat().st_size > 50000:
        print(f"    Saved {out_path.stat().st_size//1024}KB")
        return out_path
    else:
        if out_path.exists():
            out_path.unlink()
        return None

if __name__ == "__main__":
    if not API_KEY:
        print("ERROR: PEXELS_API_KEY not set")
        exit(1)
    print(f"Searching Pexels for {len(QUERIES)} B-rolls...\n")
    results = {}
    for key, query in QUERIES.items():
        print(f"[{key}] '{query}'")
        clips = search_pexels(query)
        if clips:
            # Take first available
            c = clips[0]
            path = download_pexels(c['id'], c['url'], key)
            results[key] = {'id': c['id'], 'path': str(path) if path else None, 'duration': c['duration']}
        else:
            print(f"  ✗ No clips found")
            results[key] = None
    # Save manifest
    Path("output/NSeL8fFz5hw/pexels_manifest.json").write_text(json.dumps(results, indent=2))
    print(f"\nDone. Manifest: output/NSeL8fFz5hw/pexels_manifest.json")
    print(f"Downloaded: {sum(1 for v in results.values() if v)}/{len(QUERIES)}")
