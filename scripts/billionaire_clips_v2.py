"""
Smart clip selection — multi-segment stitching + sentence boundary snapping.

Fixes:
1. No mid-sentence cuts — snap to sentence boundaries (ends with .!?)
2. Multi-segment clips — stitch 2-3 viral moments into coherent narrative

Each clip = list of segments: [{"start": s, "end": e, "text": "..."}, ...]
Renderer will concat segments with 0.3s crossfade.
"""
import json, re
from pathlib import Path

TRANSCRIPT = Path("/Users/hung/code/ai/shorts/output/source/2eic_transcript.json")
t = json.loads(TRANSCRIPT.read_text())
segs = t["segments"]

# Build sentence database
sentences = []
for seg in segs:
    text = seg["text"].strip()
    if not text:
        continue
    has_end = bool(re.search(r'[.!?]\s*$', text))
    sentences.append({
        "start": seg["start"],
        "end": seg["end"],
        "text": text,
        "is_boundary": has_end
    })

def find_boundary(target_time, direction="after", max_search=8):
    """Find nearest sentence boundary within max_search seconds."""
    candidates = []
    for s in sentences:
        if not s["is_boundary"]:
            continue
        if direction == "after" and s["end"] >= target_time and s["end"] <= target_time + max_search:
            candidates.append(s)
        elif direction == "before" and s["end"] <= target_time and s["end"] >= target_time - max_search:
            candidates.append(s)
    
    if not candidates:
        return target_time  # fallback to original
    
    # Pick closest
    candidates.sort(key=lambda x: abs(x["end"] - target_time))
    return candidates[0]["end"]


def get_text_range(start, end):
    """Get transcript text in range for debugging."""
    texts = []
    for s in sentences:
        if s["end"] < start or s["start"] > end:
            continue
        texts.append(s["text"])
    return " ".join(texts)


# ── NEW CLIPS with multi-segment + boundary snapping ──

CLIPS = [
    # ── 01: Origin story — multi-segment: $12k start → 10 years struggle → breakthrough ──
    {
        "id": "01-rags-to-riches",
        "hook": "FROM $12K TO BILLIONAIRE",
        "speaker": "Andy Frisella",
        "segments": [
            # Segment 1: Starting with $12k
            {"start": 332, "end": find_boundary(350, "after")},  # "started with $12k" → boundary
            # Segment 2: First 10 years struggle
            {"start": 356, "end": find_boundary(365, "after")},  # "$695 a month for 10 years" → boundary
        ],
        "punchlines": {"12000", "$12", "$7", "seven", "695", "month", "10", "years", "money", "broke"},
        "overlays": [
            {"name": "icon_money", "ts": 1.0, "x": 780, "y": 200, "dur": 3.0, "scale": 1.5},
            {"name": "badge_money", "ts": 5.0, "x": 250, "y": 500, "dur": 2.5},
            {"name": "flash_green", "ts": 10.0, "x": 0, "y": 0, "dur": 0.2},
            {"name": "text_fact", "ts": 15.0, "x": 140, "y": 650, "dur": 2.0},
            {"name": "icon_warning", "ts": 22.0, "x": 100, "y": 400, "dur": 2.5},
            {"name": "text_insane", "ts": 28.0, "x": 140, "y": 600, "dur": 2.0},
        ],
    },
    
    # ── 02: Fire people truth — single segment, boundary snapped ──
    {
        "id": "02-fire-them",
        "hook": "WHY YOU MUST FIRE PEOPLE",
        "speaker": "Andy Frisella",
        "segments": [
            {"start": 142, "end": find_boundary(162, "after")},
        ],
        "punchlines": {"fire", "firing", "holding", "back", "great", "realize"},
        "overlays": [
            {"name": "icon_warning", "ts": 1.0, "x": 100, "y": 300, "dur": 3.0},
            {"name": "badge_warning", "ts": 5.0, "x": 250, "y": 480, "dur": 2.5},
            {"name": "flash_red", "ts": 10.0, "x": 0, "y": 0, "dur": 0.2},
            {"name": "text_truth", "ts": 15.0, "x": 140, "y": 650, "dur": 2.0},
        ],
    },
    
    # ── 03: Discipline bank — single segment ──
    {
        "id": "03-discipline-bank",
        "hook": "DISCIPLINE IS A BANK ACCOUNT",
        "speaker": "Andy Frisella",
        "segments": [
            {"start": 293, "end": find_boundary(318, "after")},
        ],
        "punchlines": {"discipline", "bank", "account", "deposits", "withdrawals", "trash", "hurting"},
        "overlays": [
            {"name": "icon_idea", "ts": 1.0, "x": 780, "y": 200, "dur": 3.0, "scale": 1.3},
            {"name": "badge_key", "ts": 5.0, "x": 250, "y": 480, "dur": 2.5},
            {"name": "icon_money", "ts": 12.0, "x": 800, "y": 300, "dur": 2.5},
            {"name": "text_fact", "ts": 18.0, "x": 140, "y": 650, "dur": 2.0},
        ],
    },
    
    # ── 04: Grind reality — multi-segment: it's hard + price to pay ──
    {
        "id": "04-grind-reality",
        "hook": "THE REAL PRICE OF SUCCESS",
        "speaker": "Andy Frisella",
        "segments": [
            # Segment 1: Not just Lambos
            {"start": 392, "end": find_boundary(408, "after")},
            # Segment 2: Everybody can be great
            {"start": 419, "end": find_boundary(430, "after")},
        ],
        "punchlines": {"hard", "grind", "wrong", "right", "Lamborghini", "price", "great", "pay"},
        "overlays": [
            {"name": "icon_fire", "ts": 1.0, "x": 780, "y": 200, "dur": 3.0, "scale": 1.3},
            {"name": "badge_truth", "ts": 6.0, "x": 250, "y": 480, "dur": 2.5},
            {"name": "text_truth", "ts": 18.0, "x": 140, "y": 650, "dur": 2.5},
            {"name": "icon_bolt", "ts": 28.0, "x": 800, "y": 300, "dur": 2.5},
        ],
    },
    
    # ── 05: Rejection story — single segment ──
    {
        "id": "05-rejection-built-empire",
        "hook": "REJECTION MADE HIM A BILLIONAIRE",
        "speaker": "Andy Frisella",
        "segments": [
            {"start": 483, "end": find_boundary(514, "after")},
        ],
        "punchlines": {"no", "never", "work", "rejection", "forced", "vertical", "2012"},
        "overlays": [
            {"name": "icon_target", "ts": 1.0, "x": 780, "y": 200, "dur": 3.0, "scale": 1.3},
            {"name": "flash_red", "ts": 8.0, "x": 0, "y": 0, "dur": 0.2},
            {"name": "text_never", "ts": 14.0, "x": 140, "y": 650, "dur": 2.0},
            {"name": "icon_bolt", "ts": 24.0, "x": 800, "y": 350, "dur": 3.0},
        ],
    },
    
    # ── 06: Bugatti — keep original (already perfect) ──
    {
        "id": "06-bugatti-money",
        "hook": "HOW TO AFFORD A BUGATTI",
        "speaker": "Andy Frisella",
        "segments": [
            {"start": 981, "end": find_boundary(996, "after")},
        ],
        "punchlines": {"Bugatti", "rich", "entrepreneur", "afford"},
        "overlays": [
            {"name": "icon_money", "ts": 1.0, "x": 780, "y": 200, "dur": 3.0, "scale": 1.5},
            {"name": "flash_yellow", "ts": 5.0, "x": 0, "y": 0, "dur": 0.2},
            {"name": "badge_luxury", "ts": 7.0, "x": 250, "y": 480, "dur": 2.5},
            {"name": "text_wow", "ts": 15.0, "x": 140, "y": 650, "dur": 2.0},
        ],
    },
    
    # ── 07: Dream house — single segment ──
    {
        "id": "07-dream-house",
        "hook": "HE VISUALIZED THIS HOUSE",
        "speaker": "Andy Frisella",
        "segments": [
            {"start": 1017, "end": find_boundary(1032, "after")},
        ],
        "punchlines": {"house", "kid", "coolest", "visualize", "bought"},
        "overlays": [
            {"name": "icon_idea", "ts": 1.0, "x": 780, "y": 200, "dur": 3.0, "scale": 1.3},
            {"name": "badge_luxury", "ts": 6.0, "x": 250, "y": 480, "dur": 2.5},
            {"name": "flash_white", "ts": 12.0, "x": 0, "y": 0, "dur": 0.2},
            {"name": "text_wow", "ts": 15.0, "x": 140, "y": 650, "dur": 2.0},
        ],
    },
    
    # ── 08: Family business — single segment ──
    {
        "id": "08-family-business",
        "hook": "BUSINESS WITH FAMILY WORKS",
        "speaker": "Andy Frisella",
        "segments": [
            {"start": 203, "end": find_boundary(232, "after")},
        ],
        "punchlines": {"family", "bad", "advice", "trust", "friends", "skills"},
        "overlays": [
            {"name": "icon_warning", "ts": 1.0, "x": 780, "y": 200, "dur": 2.5},
            {"name": "badge_truth", "ts": 6.0, "x": 250, "y": 480, "dur": 2.5},
            {"name": "text_truth", "ts": 15.0, "x": 140, "y": 650, "dur": 2.5},
            {"name": "icon_bolt", "ts": 24.0, "x": 800, "y": 350, "dur": 2.5},
        ],
    },
    
    # ── 09: Fitness = success — multi-segment: correlation + mutual suffering ──
    {
        "id": "09-fitness-success",
        "hook": "FITNESS EQUALS FINANCIAL SUCCESS",
        "speaker": "Andy Frisella",
        "segments": [
            # Segment 1: Correlation question
            {"start": 233, "end": find_boundary(244, "after")},
            # Segment 2: Mutual suffering explanation
            {"start": 247, "end": find_boundary(268, "after")},
        ],
        "punchlines": {"fitness", "financial", "success", "correlation", "huge", "suffering"},
        "overlays": [
            {"name": "icon_chart_up", "ts": 1.0, "x": 780, "y": 200, "dur": 3.0, "scale": 1.3},
            {"name": "badge_key", "ts": 6.0, "x": 250, "y": 480, "dur": 2.5},
            {"name": "icon_fire", "ts": 16.0, "x": 100, "y": 400, "dur": 3.0},
            {"name": "flash_green", "ts": 26.0, "x": 0, "y": 0, "dur": 0.2},
            {"name": "text_fact", "ts": 30.0, "x": 140, "y": 650, "dur": 2.5},
        ],
    },
]

# Compute total duration per clip (for overlay timing adjustment)
for clip in CLIPS:
    total_dur = sum(seg["end"] - seg["start"] for seg in clip["segments"])
    clip["duration"] = total_dur
    
    # Debug: show segment breakdown
    print(f"\n{clip['id']} ({total_dur:.1f}s total, {len(clip['segments'])} segments)")
    for i, seg in enumerate(clip["segments"], 1):
        dur = seg["end"] - seg["start"]
        text_preview = get_text_range(seg["start"], seg["end"])[:80]
        print(f"  [{i}] {seg['start']:.1f}-{seg['end']:.1f} ({dur:.1f}s): {text_preview}...")
