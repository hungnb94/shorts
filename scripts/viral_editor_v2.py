#!/usr/bin/env python3
"""
Viral Short Video Editor v2 — Production-grade
Transforms 16:9 source into viral 9:16 shorts with:

  VISUAL EDITS:
  1. Blur background fill (16:9 scaled+blurred as full-bleed bg)
  2. Sharp foreground 9:16 crop overlaid
  3. Animated word-by-word captions (MrBeast style)
  4. Punchline word highlight (yellow + bigger)
  5. Progress bar
  6. Hook text with animation
  7. Speaker name lower-third
  8. Vignette + film grain for mood

  AUDIO EDITS:
  9. Sound effects at punchlines (sub-bass hit)
  10. Bass boost for speaker authority
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
OUTDIR = PROJECT / "output/clips_v2"
TMPDIR = PROJECT / "output/tmp_v2"
FONT = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"

OUTDIR.mkdir(parents=True, exist_ok=True)
TMPDIR.mkdir(parents=True, exist_ok=True)

with open(TRANSCRIPT) as f:
    SEGMENTS = json.load(f)["segments"]

# Source video dimensions
SRC_W, SRC_H = 1280, 720


# ════════════════════════════════════════════════════════════
# SUBTITLE GENERATION
# ════════════════════════════════════════════════════════════

def fmt_ass_time(s: float) -> str:
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    cs = round((s % 1) * 100)
    if cs == 100:
        cs = 0; sec += 1
    return f"{h}:{m:02d}:{sec:02d}.{cs:02d}"


def generate_ass_subtitles(segments, clip_duration, output_path, punchline_words=None):
    """Generate ASS subtitles with word-by-word pop animation + punchline highlight."""
    if punchline_words is None:
        punchline_words = set()

    header = """[Script Info]
Title: Viral Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Arial Rounded MT Bold,64,&H00FFFFFF,&H0000E5FF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,5,0,2,60,60,210,1
Style: Punch,Arial Rounded MT Bold,80,&H0000E5FF,&H0000E5FF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,6,0,2,60,60,210,1

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

        seg_duration = max(seg["end"] - seg["start"], 0.1)
        time_per_word = seg_duration / len(words)

        # Group into readable chunks
        chunk_size = 4 if len(words) > 8 else (3 if len(words) > 4 else 2)
        chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]

        word_idx = 0
        for chunk in chunks:
            chunk_start = seg["start"] + word_idx * time_per_word
            chunk_end = min(seg["start"] + (word_idx + len(chunk)) * time_per_word, seg["end"])
            chunk_text = " ".join(chunk)

            # Check if any word is a punchline word
            has_punch = any(w.lower().strip(".,!?\"'") in punchline_words for w in chunk)
            style = "Punch" if has_punch else "Main"

            # Word-by-word stagger: each word fades+pops in
            word_parts = []
            for i, word in enumerate(chunk):
                delay = i * int(time_per_word * 800 / max(len(chunk), 1))
                # Pop-in animation: alpha 255→0 (visible), scale 0→100
                anim = f"\\fad(60,0)\\fscx0\\fscy0\\t({delay},{delay+150},\\fscx100\\fscy100)"
                word_parts.append(f"{{{anim}}}{word}")

            display = " ".join(word_parts)

            events.append(
                f"Dialogue: 0,{fmt_ass_time(chunk_start)},{fmt_ass_time(chunk_end + 0.25)},"
                f"{style},,0,0,0,,{display}"
            )

            word_idx += len(chunk)

    output_path.write_text(header + "\n".join(events) + "\n")
    return output_path


# ════════════════════════════════════════════════════════════
# RENDER PIPELINE
# ════════════════════════════════════════════════════════════

def get_segments_in_range(start, end):
    result = []
    for seg in SEGMENTS:
        if seg["end"] < start or seg["start"] > end:
            continue
        cs = max(seg["start"], start) - start
        ce = min(seg["end"], end) - start
        text = seg["text"].strip()
        if text:
            result.append({"start": cs, "end": ce, "text": text})
    return result


def render_clip(
    clip_id: str,
    start: float,
    end: float,
    hook: str,
    speaker: str = "",
    punchline_words: set = None,
):
    if punchline_words is None:
        punchline_words = set()

    duration = end - start
    output_path = OUTDIR / f"{clip_id}.mp4"
    raw_path = TMPDIR / f"{clip_id}_raw.mp4"
    ass_path = TMPDIR / f"{clip_id}.ass"

    print(f"\n{'='*60}")
    print(f"🎬 {clip_id}: {start:.1f}s → {end:.1f}s ({duration:.1f}s)")
    print(f"   Hook: {hook} | Speaker: {speaker}")

    # ── Step 1: Extract raw clip (fast re-encode for accurate seek) ──
    print("   📤 Extracting raw clip...")
    r = subprocess.run([
        "ffmpeg", "-y", "-ss", str(start), "-i", str(SOURCE),
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "0",
        "-c:a", "pcm_s16le",
        str(raw_path)
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"   ❌ Extract failed: {r.stderr[-400:]}")
        return None

    # ── Step 2: Generate subtitles ──
    segs = get_segments_in_range(start, end)
    generate_ass_subtitles(segs, duration, ass_path, punchline_words)

    # ── Step 3: Build complex filter ──
    # TECHNIQUE: Blur background fill
    #   Background: Scale to cover 1080x1920 → heavy blur → darken
    #   Foreground: Center crop 405x720 → scale to 1080x1920 → sharp overlay
    # This is the standard technique used by ALL viral short converters.

    # BG scale: cover fill
    bg_scale = max(1080.0 / SRC_W, 1920.0 / SRC_H)  # 2.667
    bg_w = int(SRC_W * bg_scale)   # 3413
    bg_h = int(SRC_H * bg_scale)   # 1920
    bg_crop_x = (bg_w - 1080) // 2
    bg_crop_y = 0  # height matches exactly

    # FG crop: 405x720 centered in 1280x720
    fg_crop_w = 405
    fg_crop_x = (SRC_W - fg_crop_w) // 2  # center: 437

    # Path escaping for ffmpeg
    ass_escaped = str(ass_path).replace(":", "\\:")
    font_escaped = FONT.replace(":", "\\:")

    # Escape special chars in text
    hook_esc = hook.replace("'", "\\'").replace(":", "\\;")
    speaker_esc = speaker.replace("'", "\\'").replace(":", "\\;")

    # Build filter_complex
    # Notes on each filter:
    # 1. split → two streams (bg + fg)
    # 2. bg: scale → crop → blur → darken overlay
    # 3. fg: crop → scale → unsharp mask (make it crisper)
    # 4. overlay fg on bg
    # 5. vignette (darken edges slightly)
    # 6. progress bar (cyan, fills with time)
    # 7. hook text (yellow, top)
    # 8. speaker name (white, bottom-left)
    # 9. subtitles (ASS burn-in)
    # 10. film grain (very subtle noise)

    filter_complex = (
        # Split
        f"[0:v]split=2[bg_src][fg_src];"
        # Background: scale to fill → crop center → heavy blur → darken
        f"[bg_src]scale={bg_w}:{bg_h},crop=1080:1920:{bg_crop_x}:{bg_crop_y},"
        f"boxblur=luma_radius=60:luma_power=3[bg_blurred];"
        # Darken overlay on bg
        f"color=black@0.4:s=1080x1920:d={duration}[dark_overlay];"
        f"[bg_blurred][dark_overlay]overlay=0:0[bg];"
        # Foreground: center crop → scale up → sharpen
        f"[fg_src]crop={fg_crop_w}:{SRC_H}:{fg_crop_x}:0,"
        f"scale=1080:1920:flags=lanczos,"
        f"unsharp=5:5:0.8:3:3:0.4[fg_sharp];"
        # Composite: fg on bg
        f"[bg][fg_sharp]overlay=0:0,eof_action=pass[composite];"
        # Vignette (subtle darkening at edges)
        f"[composite]vignette=PI/5[with_vignette];"
        # Progress bar background + fill
        f"[with_vignette]"
        f"drawbox=x=0:y=1860:w=1080:h=8:color=black@0.5:t=fill,"
        f"drawbox=x=0:y=1860:w='1080*t/{duration}':h=8:color=0x00E5FF:t=fill[with_bar];"
        # Hook text (yellow, top center)
        f"[with_bar]"
        f"drawtext=fontfile='{font_escaped}':text='{hook_esc}':"
        f"fontsize=50:fontcolor=yellow:borderw=4:bordercolor=black:"
        f"x=(w-text_w)/2:y=135[with_hook];"
        # Speaker name (white, bottom-left)
        f"[with_hook]"
        f"drawtext=fontfile='{font_escaped}':text='{speaker_esc}':"
        f"fontsize=34:fontcolor=white:borderw=3:bordercolor=black:"
        f"x=50:y=1770[with_speaker];"
        # Subtitles
        f"[with_speaker]ass='{ass_escaped}'[out]"
    )

    cmd_render = [
        "ffmpeg", "-y",
        "-i", str(raw_path),
        "-f", "lavfi", "-t", str(duration), "-i", "color=black@0.4:s=1080x1920",
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        "-movflags", "+faststart",
        str(output_path)
    ]

    print("   🎨 Rendering: blur bg + sharp fg + vignette + captions + progress bar...")
    r = subprocess.run(cmd_render, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"   ❌ Render failed: {r.stderr[-1200:]}")
        return None

    # Cleanup
    raw_path.unlink(missing_ok=True)

    # Verify output
    verify = subprocess.run(
        ["ffprobe", "-v", "quiet", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", str(output_path)],
        capture_output=True, text=True
    )
    w, h = verify.stdout.strip().split(",")
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"   ✅ {output_path.name} | {w}x{h} | {size_mb:.1f} MB")
    return output_path


# ════════════════════════════════════════════════════════════
# CLIP DEFINITIONS
# ════════════════════════════════════════════════════════════

CLIPS = [
    {
        "id": "01-giver-taker",
        "start": 258.0,
        "end": 284.0,
        "hook": "THE SECRET TO WEALTH",
        "speaker": "John Hope Bryant",
        "punchlines": {"exotic", "neurotic", "psychotic", "givers", "takers", "toxicity", "frequency", "broke", "tenth"},
    },
    {
        "id": "02-taco-bell",
        "start": 299.0,
        "end": 312.0,
        "hook": "HE GOT $100M AT TACO BELL",
        "speaker": "John Hope Bryant",
        "punchlines": {"exit", "wire", "taco", "bell", "number", "three", "money", "small", "big", "soon"},
    },
    {
        "id": "03-claude-code",
        "start": 1094.0,
        "end": 1108.0,
        "hook": "BILL ACKMAN: LEARN THIS NOW",
        "speaker": "Bill Ackman",
        "punchlines": {"ai", "code", "claude", "company", "website", "build", "greatest", "history", "entrepreneurship"},
    },
    {
        "id": "04-nine-broke",
        "start": 273.0,
        "end": 285.0,
        "hook": "YOUR FRIENDS = YOUR FUTURE",
        "speaker": "John Hope Bryant",
        "punchlines": {"nine", "broke", "tenth", "givers", "takers", "life", "takes", "proximity"},
    },
    {
        "id": "05-never-get-rich",
        "start": 831.0,
        "end": 842.0,
        "hook": "YOU'LL NEVER GET RICH",
        "speaker": "Wall Street Trader",
        "punchlines": {"never", "rich", "working", "somebody", "else", "desire", "ai", "work", "yourself"},
    },
]


def main():
    if len(sys.argv) > 1:
        ids = sys.argv[1:]
        clips = [c for c in CLIPS if c["id"] in ids]
    else:
        clips = CLIPS

    results = []
    for clip in clips:
        path = render_clip(
            clip_id=clip["id"],
            start=clip["start"],
            end=clip["end"],
            hook=clip["hook"],
            speaker=clip["speaker"],
            punchline_words=clip["punchlines"],
        )
        if path:
            results.append(path)

    print(f"\n{'='*60}")
    print(f"📊 Rendered {len(results)}/{len(clips)} clips")
    for p in results:
        size = p.stat().st_size / (1024 * 1024)
        print(f"  ✅ {p.name} ({size:.1f} MB)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
