#!/usr/bin/env python3
"""Search and download Pexels B-roll for Bác sĩ Hải health/sleep shorts."""
import os, json, subprocess
from pathlib import Path

CACHE = Path("output/pexels")
CACHE.mkdir(parents=True, exist_ok=True)
API_KEY = os.environ.get("PEXELS_API_KEY")

QUERIES = {
    "bedroom": "bedroom bed sleep night",
    "phone_hand": "person using phone in bed",
    "clock_night": "alarm clock night",
    "sleepless": "insomnia sleepless person",
    "sleep_well": "peaceful sleep healthy",
    "breathing": "deep breathing relax",
    "ac_cool": "air conditioner cool room",
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
    if code != '200': return []
    try:
        data = json.loads(Path('/tmp/pexels_search.json').read_text())
    except:
        return []
    results = []
    for v in data.get('videos', [])[:3]:
        best = None
        for f in v.get('video_files', []):
            w, h = f.get('width', 0), f.get('height', 0)
            if h > w and w >= 540:
                if not best or f.get('height', 0) > best.get('height', 0):
                    best = f
        if not best:
            for f in v.get('video_files', []):
                w, h = f.get('width', 0), f.get('height', 0)
                if h > w:
                    best = f; break
        if best:
            results.append({'id': v['id'], 'url': best['link'], 'duration': v.get('duration', 0)})
    return results

def download(video_id, url, key):
    out_path = CACHE / f"{key}_{video_id}.mp4"
    if out_path.exists() and out_path.stat().st_size > 50000:
        print(f"  OK Cached: {out_path.name}")
        return out_path
    print(f"  Downloading {out_path.name}...")
    r = subprocess.run(['curl', '-L', '-s', '-o', str(out_path), url], capture_output=True, timeout=60)
    if r.returncode == 0 and out_path.exists() and out_path.stat().st_size > 50000:
        print(f"    {out_path.stat().st_size//1024}KB")
        return out_path
    return None

if __name__ == "__main__":
    if not API_KEY: print("ERROR: PEXELS_API_KEY not set"); exit(1)
    print(f"Searching Pexels for {len(QUERIES)} health clips...\n")
    results = {}
    for key, query in QUERIES.items():
        print(f"[{key}] '{query}'")
        clips = search_pexels(query)
        if clips:
            c = clips[0]
            path = download(c['id'], c['url'], key)
            results[key] = {'id': c['id'], 'path': str(path) if path else None}
        else:
            print("  No clips found")
            results[key] = None
    print(f"\nDone: {sum(1 for v in results.values() if v)}/{len(QUERIES)}")
