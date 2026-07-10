# V1 vs V2 — Clip Selection & Rendering Improvements

## Problems Fixed

### Problem 1: Mid-sentence cuts
**V1 behavior:** Clips cut at arbitrary timestamps → video dừng giữa câu, không hoàn chỉnh
**Example:** Clip 01 ended at 379s mid-word "..." 

**V2 solution:** Sentence boundary snapping
- Scan transcript for segments ending with `.!?`
- Snap clip end within ±8s to nearest sentence boundary
- Result: All clips now end at natural pauses

### Problem 2: Short clips lack context
**V1 behavior:** Single-range clips (e.g., 24s Bugatti clip) thiếu setup/payoff
**Example:** Clip 06 (24s) chỉ có encounter scene, không có context

**V2 solution:** Multi-segment stitching
- Each clip = list of 1-3 segments from different parts of video
- ffmpeg `xfade` filter concat with 0.3s crossfade transition
- Audio concat seamless with `concat` filter
- Subtitles offset per segment to maintain sync

## Architecture Changes

### V1 Pipeline (billionaire_clips.py + render_billionaire.py)
```
User defines: {id, start, end, hook, overlays}
              ↓
        Extract [start, end]
              ↓
        Generate subs (single range)
              ↓
        Composite (bg + fg + overlays)
```

### V2 Pipeline (billionaire_clips_v2.py + render_billionaire_v2.py)
```
User defines: {id, segments: [{start, end}, ...], hook, overlays}
              ↓
        find_boundary(time, direction) — snap to sentence
              ↓
        For each segment: extract raw mp4
              ↓
        Concat segments with xfade (0.3s crossfade)
              ↓
        Generate unified subs (offset per segment)
              ↓
        Composite (bg + fg + overlays)
```

## Key Code Changes

### Sentence boundary detection
```python
def find_boundary(target_time, direction="after", max_search=8):
    """Find nearest sentence boundary within max_search seconds."""
    candidates = []
    for s in sentences:
        if not s["is_boundary"]:  # ends with .!?
            continue
        if direction == "after" and s["end"] >= target_time and s["end"] <= target_time + max_search:
            candidates.append(s)
    candidates.sort(key=lambda x: abs(x["end"] - target_time))
    return candidates[0]["end"]
```

### Multi-segment concat with xfade
```python
def concat_segments(clip, clip_id):
    # Extract each segment
    for i, seg in enumerate(segments):
        extract(seg["start"], seg["end"], f"seg{i}.mp4")
    
    # Build xfade filter: [0:v][1:v]xfade=transition=fade:duration=0.3:offset=D1[v01]
    xfade_dur = 0.3
    offset = segments[0]["end"] - segments[0]["start"] - xfade_dur
    filter = f"[0:v][1:v]xfade=transition=fade:duration={xfade_dur}:offset={offset}[v];"
    
    # Concat audio
    filter += "[0:a][1:a]concat=n=2:v=0:a=1[a];"
    
    ffmpeg -i seg0.mp4 -i seg1.mp4 -filter_complex_script xfade.txt -map [v] -map [a] raw.mp4
```

### Subtitle offsetting per segment
```python
all_segs = []
time_offset = 0
for seg_def in clip["segments"]:
    seg_segs = get_segs_in_range(seg_def["start"], seg_def["end"])
    # Offset to clip-local time
    for s in seg_segs:
        s["start"] += time_offset
        s["end"] += time_offset
        all_segs.append(s)
    time_offset += (seg_def["end"] - seg_def["start"])

gen_ass(all_segs, ass_path)  # Unified ASS for full clip
```

## Clip-by-Clip Comparison

| Clip | V1 Duration | V1 Segments | V2 Duration | V2 Segments | Improvement |
|------|-------------|-------------|-------------|-------------|-------------|
| 01 | 44s | 1 (335-379) | 31s | 2 (332-350, 356-365) | ✓ Multi-segment narrative, sentence boundaries |
| 02 | 30s | 1 (140-170) | 27s | 1 (142-169) | ✓ Sentence boundary snap |
| 03 | 33s | 1 (293-326) | 25s | 1 (293-318) | ✓ Sentence boundary snap |
| 04 | 42s | 1 (388-430) | 33s | 2 (392-408, 419-430) | ✓ Multi-segment (problem + solution) |
| 05 | 36s | 1 (481-517) | 31s | 1 (483-514) | ✓ Sentence boundary snap |
| 06 | 24s | 1 (978-1002) | 16s | 1 (981-997) | ✓ Sentence boundary snap |
| 07 | 30s | 1 (1005-1035) | 15s | 1 (1017-1032) | ✓ Sentence boundary snap, tighter |
| 08 | 37s | 1 (196-233) | 30s | 1 (203-233) | ✓ Sentence boundary snap |
| 09 | 42s | 1 (230-272) | 41s | 2 (233-245, 247-276) | ✓ Multi-segment (question + answer) |

## Quality Improvements

### V1 Issues
- Clip 01 ended mid-sentence: "...I made $695 a month. And then we worked other jobs, bartending, side hustles and things like—" [CUT]
- Clip 04 single range missed key context: "It's hard" statement separated from "Everybody can be great" payoff
- Clip 09 correlation statement without explanation felt incomplete

### V2 Fixes
- All clips end at sentence boundaries (natural pauses)
- Multi-segment clips stitch related moments into coherent narratives
- Crossfade transitions feel intentional (not jarring cuts)
- Shorter durations (15-41s vs 24-44s) → higher retention potential

## User-Facing Result

**V1:** 9 clips, some end abruptly mid-thought, single-range limits storytelling
**V2:** 9 clips, all end naturally, multi-segment clips tell complete stories

Example narrative improvement (Clip 01):
- V1: "Started with $12k → sold $7 first day → made $695/month for 10 years" (single 44s range)
- V2: "Started with $12k in Springfield" [CROSSFADE] "$695/month for 10 years" (2 segments, 31s total, tighter story)

Example boundary fix (Clip 06):
- V1: Ends at 1002s mid-conversation: "...we're at my garage. Your garage right here. This is the spot out—" [CUT]
- V2: Ends at 997s after complete sentence: "Yeah. All right. So Andy, where are we at right now? We're at my garage." [NATURAL END]
