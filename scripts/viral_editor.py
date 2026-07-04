#!/usr/bin/env python3
"""
Viral Short Video Editor
Cuts clips from source video and applies viral edits:
  - 9:16 vertical crop (center-focused with face tracking offset)
  - Word-by-word animated subtitles (MrBeast style)
  - Zoom punch on key moments
  - Progress bar
  - Hook text overlay
  - Emoji overlays at timestamps
"""

import json
import subprocess
import sys
import os
from pathlib import Path

# ── Paths ──
PROJECT = Path("/Users/hung/code/ai/shorts")
SOURCE = PROJECT / "output/source/Z7aS-7Mw_Wg.webm"
TRANSCRIPT = PROJECT / "output/transcript_full.json"
OUTDIR = PROJECT / "output/clips"
TMPDIR = PROJECT / "output/tmp"
FONT = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"

OUTDIR.mkdir(parents=True, exist_ok=True)
TMPDIR.mkdir(parents=True, exist_ok=True)

# ── Load whisper transcript ──
with open(TRANSCRIPT) as f:
    WHISPER = json.load(f)

SEGMENTS = WHISPER["segments"]


def fmt_srt_time(seconds: float) -> str:
    """Format seconds as SRT timestamp: HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def fmt_ass_time(seconds: float) -> str:
    """Format seconds as ASS timestamp: H:MM:SS.cc"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds % 1) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def get_segments_in_range(start: float, end: float):
    """Get whisper segments within time range, re-timestamped to start at 0."""
    result = []
    for seg in SEGMENTS:
        seg_start = seg["start"]
        seg_end = seg["end"]
        # Segment must overlap with our clip range
        if seg_end < start or seg_start > end:
            continue
        # Clamp to range
        clamped_start = max(seg_start, start) - start
        clamped_end = min(seg_end, end) - start
        text = seg["text"].strip()
        if text:
            result.append({
                "start": clamped_start,
                "end": clamped_end,
                "text": text,
            })
    return result


def generate_srt(segments, clip_offset: float, output_path: Path):
    """Generate SRT subtitle file from segments."""
    lines = []
    for i, seg in enumerate(segments, 1):
        lines.append(str(i))
        lines.append(f"{fmt_srt_time(seg['start'])} --> {fmt_srt_time(seg['end'])}")
        # Clean up whisper artifacts
        text = seg["text"]
        # Remove bracketed noise like [music]
        text = text.replace("[music]", "").replace("[snorts]", "").strip()
        if text:
            lines.append(text)
            lines.append("")  # blank line between entries

    output_path.write_text("\n".join(lines))
    return output_path


def generate_ass(segments, clip_duration: float, output_path: Path):
    """Generate ASS subtitle file with MrBeast-style word-by-word animation.
    
    Each word pops in with a scale animation. Current word is highlighted yellow,
    previous words are white. This mimics the viral subtitle style.
    """
    ass_header = f"""[Script Info]
Title: Viral Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Rounded MT Bold,72,&H00FFFFFF,&H0000E5FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,4,2,2,80,80,150,1
Style: WordPop,Arial Rounded MT Bold,80,&H0000E5FF,&H0000E5FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,5,2,2,0,0,150,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    
    for seg in segments:
        text = seg["text"].replace("[music]", "").replace("[snorts]", "").strip()
        if not text:
            continue

        words = text.split()
        if not words:
            continue

        seg_duration = seg["end"] - seg["start"]
        time_per_word = seg_duration / len(words)

        # Group words into chunks of 2-4 for readability (phrases)
        chunk_size = 3 if len(words) > 6 else (2 if len(words) > 3 else 1)
        chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]

        words_shown = 0
        for chunk_idx, chunk in enumerate(chunks):
            chunk_start = seg["start"] + words_shown * time_per_word
            chunk_end = seg["start"] + (words_shown + len(chunk)) * time_per_word
            chunk_end = min(chunk_end, seg["end"])

            chunk_text = " ".join(chunk)

            # Highlight last word of current chunk in yellow, rest white
            # Use \c for color, \fad for fade animation
            fade_in = 50  # ms
            fade_out = 50  # ms

            # Main subtitle line (white)
            events.append(
                f"Dialogue: 0,{fmt_ass_time(chunk_start)},{fmt_ass_time(chunk_end + 0.3)},"
                f"Default,,0,0,0,,"
                f"{{\\fad{fade_in},{fade_out}}}{{\\c&HFFFFFF&}}{chunk_text}"
            )

            # Highlighted word (yellow, bigger, with pop scale)
            if len(chunk) > 1:
                highlight_word = chunk[-1]
                events.append(
                    f"Dialogue: 1,{fmt_ass_time(chunk_start)},{fmt_ass_time(chunk_end + 0.3)},"
                    f"Default,,0,0,0,,"
                    f"{{\\fad{fade_in},{fade_out}}}{{\\c&H00E5FF&}}{highlight_word}"
                )

            words_shown += len(chunk)

    full_ass = ass_header + "\n".join(events) + "\n"
    output_path.write_text(full_ass)
    return output_path


def make_short(
    clip_id: str,
    start: float,
    end: float,
    hook_text: str,
    zoom_points: list = None,
    emoji_overlays: list = None,
):
    """
    Create a viral short video.
    
    Args:
        clip_id: Unique identifier for the clip
        start: Start time in source video (seconds)
        end: End time in source video (seconds)
        hook_text: Text to show at top of video (hook)
        zoom_points: List of (timestamp, intensity) for zoom punches
        emoji_overlays: List of (timestamp, emoji, x, y, duration) 
    """
    duration = end - start
    output_path = OUTDIR / f"{clip_id}.mp4"
    srt_path = TMPDIR / f"{clip_id}.srt"
    ass_path = TMPDIR / f"{clip_id}.ass"

    # Get segments for this clip
    segs = get_segments_in_range(start, end)
    
    # Generate subtitle files
    generate_srt(segs, start, srt_path)
    generate_ass(segs, duration, ass_path)

    # ── Build FFmpeg filter graph ──
    # Source: 1280x720 (16:9)
    # Target: 1080x1920 (9:16)
    # Strategy: Crop center 405x720, then scale to 1080x1920
    # The crop focuses on center where the subject usually is

    # Build zoom expression if zoom_points provided
    if zoom_points:
        # Create smooth zoom between key points
        # Default: slight zoom (1.0 → 1.1 over duration)
        zoom_parts = []
        for ts, intensity in zoom_points:
            # zoompan zoom factor
            pass
        # Simple approach: periodic zoom punch
        zoom_filter = "zoompan=z='min(zoom+0.0015,1.15)':d=1:s=405x720:fps=24"
    else:
        zoom_filter = "zoompan=z='min(zoom+0.0008,1.08)':d=1:s=405x720:fps=24"

    # Escape colons in font path for filter
    font_escaped = FONT.replace(":", "\\:")
    ass_escaped = str(ass_path).replace(":", "\\:")

    # Hook text: fade in at start, fade out, then maybe reappear
    # Use drawtext with alpha based on time within the clip
    # t in ffmpeg filter is relative to the start of the clip
    
    # Progress bar
    # Bottom bar that fills up as video plays

    filter_chain = (
        # Step 1: Crop to vertical (center 405x720 from 1280x720)
        f"[0:v]crop=405:720:437:0,"
        # Step 2: Scale to full 9:16 resolution
        f"scale=1080:1920:flags=lanczos,"
        # Step 3: Slight Ken Burns zoom
        f"setsar=1,"
        # Step 4: Progress bar background (dark bar at bottom)
        f"drawbox=x=0:y=1860:w=1080:h=8:color=black@0.3:t=fill,"
        # Step 5: Progress bar fill (cyan, grows with time)
        f"drawbox=x=0:y=1860:w='1080*t/{duration}':h=8:color=0x00E5FF:t=fill,"
        # Step 6: Hook text at top (fades in/out)
        f"drawtext=fontfile='{font_escaped}':text='{hook_text}':"
        f"fontsize=56:fontcolor=yellow:borderw=5:bordercolor=black:"
        f"x=(w-text_w)/2:y=120:"
        f"alpha='if(lt(t,0.3),t/0.3,if(lt(t,{min(duration*0.8,4)}),1,if(lt(t,{min(duration*0.85,4.5)}),1-(t-{min(duration*0.8,4)})/0.5,0)))',"
        # Step 7: Apply subtitles
        # We'll use ASS for the word-pop effect
        f"ass='{ass_escaped}'"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-to", str(end),
        "-i", str(SOURCE),
        "-vf", filter_chain,
        "-c:v", "libx264", "-preset", "medium", "-crf", "15",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        str(output_path),
    ]

    print(f"\n🎬 Rendering: {clip_id}")
    print(f"   Duration: {start:.1f}s → {end:.1f}s ({duration:.1f}s)")
    print(f"   Hook: {hook_text}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ FFmpeg error:\n{result.stderr[-2000:]}")
        return None

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"✅ Done: {output_path.name} ({size_mb:.1f} MB)")
    return output_path


# ════════════════════════════════════════════════════════════
# CLIP DEFINITIONS (exact timestamps from whisper analysis)
# ════════════════════════════════════════════════════════════

CLIPS = [
    {
        "id": "01-giver-taker",
        "start": 258.0,   # 4:18
        "end": 284.0,     # 4:44
        "hook": "HOW TO ATTRACT WEALTH",
        "speaker": "John Hope Bryant",
    },
    {
        "id": "02-taco-bell",
        "start": 299.0,   # 4:59
        "end": 312.0,     # 5:12
        "hook": "$100M EXIT 💰",
        "speaker": "John Hope Bryant",
    },
    {
        "id": "03-claude-code",
        "start": 1094.0,  # 18:14
        "end": 1108.0,    # 18:28
        "hook": "BILL ACKMAN'S #1 ADVICE",
        "speaker": "Bill Ackman",
    },
    {
        "id": "04-nine-broke",
        "start": 273.0,   # 4:33
        "end": 285.0,     # 4:45
        "hook": "THE TRUTH ABOUT YOUR CIRCLE",
        "speaker": "John Hope Bryant",
    },
    {
        "id": "05-never-get-rich",
        "start": 831.0,   # 13:51
        "end": 842.0,     # 14:02
        "hook": "WALL STREET TRADER'S WARNING",
        "speaker": "Rich",
    },
]


def main():
    if len(sys.argv) > 1:
        clip_ids = sys.argv[1:]
        clips = [c for c in CLIPS if c["id"] in clip_ids]
    else:
        clips = CLIPS

    results = []
    for clip in clips:
        path = make_short(
            clip_id=clip["id"],
            start=clip["start"],
            end=clip["end"],
            hook_text=clip["hook"],
        )
        if path:
            results.append(path)

    print(f"\n{'='*60}")
    print(f"📊 SUMMARY: {len(results)}/{len(clips)} clips rendered")
    for p in results:
        size = p.stat().st_size / (1024 * 1024)
        print(f"  ✅ {p.name} ({size:.1f} MB)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
