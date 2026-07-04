#!/usr/bin/env python3
"""
Billionaire Shorts renderer — 9 clips from "Day in the Life of a Billionaire".
Source: 640x360 H264 → 1080x1920 9:16 shorts.

Pipeline per clip:
  1. Raw extract (accurate seek, intermediate mp4)
  2. Generate ASS subtitles (word-pop + punchline highlight)
  3. Build filter_complex_script (blur bg + sharp fg + overlays)
  4. Composite final (H264 + AAC)

Value-add layers (ADR 0008): icon/badge/flash/text overlays per clip.
Retention (ADR 0008): blur bg, vignette, progress bar, punchline highlight — base quality.
"""
import json, subprocess, sys, re
from pathlib import Path

ROOT = Path("/Users/hung/code/ai/shorts")
SOURCE = ROOT / "output/source/2eicF3iPf1s.mp4"
TRANSCRIPT = ROOT / "output/source/2eic_transcript.json"
OUTDIR = ROOT / "output/billionaire"
TMPDIR = ROOT / "output/billionaire/tmp"
OVERLAYS = ROOT / "output/billionaire/overlays"
FONT = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
OUTDIR.mkdir(parents=True, exist_ok=True)
TMPDIR.mkdir(parents=True, exist_ok=True)

# Source: 640x360 → target 1080x1920
SRC_W, SRC_H = 640, 360
# Background: scale to cover 1080x1920 → scale factor = max(1080/640, 1920/360) = 5.333
BG_SCALE = max(1080.0 / SRC_W, 1920.0 / SRC_H)  # 5.333
BG_W = int(SRC_W * BG_SCALE)  # 3413
BG_H = int(SRC_H * BG_SCALE)  # 1920
BG_CROP_X = (BG_W - 1080) // 2  # 1166
# Foreground: crop thin 9:16 strip → 360 * 9/16 = 202.5 ≈ 203
FG_W = int(SRC_H * 9 / 16)  # 202
FG_X = (SRC_W - FG_W) // 2  # 218

# Load transcript
with open(TRANSCRIPT) as f:
    WHISPER = json.load(f)
SEGMENTS = WHISPER.get("segments", [])


def fmt_ass_time(s):
    h = int(s // 3600); m = int((s % 3600) // 60); sec = int(s % 60)
    cs = round((s % 1) * 100)
    if cs == 100: cs = 0; sec += 1
    return f"{h}:{m:02d}:{sec:02d}.{cs:02d}"


def get_segs_in_range(start, end):
    """Get transcript segments within [start, end], offset to clip-local time."""
    result = []
    for seg in SEGMENTS:
        if seg["end"] < start or seg["start"] > end:
            continue
        cs = max(seg["start"], start) - start
        ce = min(seg["end"], end) - start
        text = seg["text"].strip()
        # Clean whisper artifacts
        text = re.sub(r'\[.*?\]', '', text).strip()
        if text:
            result.append({"start": cs, "end": ce, "text": text})
    return result


def gen_ass(segs, out_path, punchlines=None):
    if punchlines is None:
        punchlines = set()
    header = f"""[Script Info]
Title: Viral Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Arial Rounded MT Bold,60,&H00FFFFFF,&H0000E5FF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,5,0,2,60,60,220,1
Style: Punch,Arial Rounded MT Bold,76,&H0000E5FF,&H0000E5FF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,6,0,2,60,60,220,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for seg in segs:
        text = seg["text"]
        words = text.split()
        if not words:
            continue
        seg_dur = max(seg["end"] - seg["start"], 0.1)
        tpw = seg_dur / len(words)
        chunk_size = 4 if len(words) > 8 else (3 if len(words) > 4 else 2)
        chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]
        wi = 0
        for chunk in chunks:
            cs = seg["start"] + wi * tpw
            ce = min(seg["start"] + (wi + len(chunk)) * tpw, seg["end"])
            has_punch = any(w.lower().strip(".,!?\"'") in punchlines for w in chunk)
            style = "Punch" if has_punch else "Main"
            word_parts = []
            for i, word in enumerate(chunk):
                delay = i * int(tpw * 800 / max(len(chunk), 1))
                anim = f"\\fad(60,0)\\fscx0\\fscy0\\t({delay},{delay+150},\\fscx100\\fscy100)"
                word_parts.append(f"{{{anim}}}{word}")
            display = " ".join(word_parts)
            events.append(f"Dialogue: 0,{fmt_ass_time(cs)},{fmt_ass_time(ce + 0.25)},{style},,0,0,0,,{display}")
            wi += len(chunk)
    out_path.write_text(header + "\n".join(events) + "\n")
    return out_path


def esc(t):
    """Escape text for ffmpeg drawtext/filter."""
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "'\\''")


def build_filter(clip):
    """Build the complete filter_complex graph for a clip."""
    dur = clip["duration"]
    hook = esc(clip["hook"])
    speaker = esc(clip.get("speaker", "School of Hard Knocks"))
    ass_path = esc(str(clip["_ass"]))
    overlays = clip.get("overlays", [])

    # Count overlay inputs (after [0:v] video)
    lines = []
    # Split video for bg + fg
    lines.append("[0:v]split=2[bg_src][fg_src];")
    # Background: scale → crop → blur → darken
    lines.append(
        f"[bg_src]scale={BG_W}:{BG_H},crop=1080:1920:{BG_CROP_X}:0,"
        f"boxblur=luma_radius=60:luma_power=3,"
        f"drawbox=x=0:y=0:w=1080:h=1920:color=black@0.35:t=fill[bg];"
    )
    # Foreground: crop → scale → sharpen
    lines.append(
        f"[fg_src]crop={FG_W}:{SRC_H}:{FG_X}:0,scale=1080:1920:flags=lanczos,setsar=1,"
        f"unsharp=5:5:0.8:3:3:0.4[fg_sharp];"
    )
    # Composite
    lines.append("[bg][fg_sharp]overlay=0:0,vignette=PI/5[comp];")
    # Progress bar
    lines.append(
        f"[comp]drawbox=x=0:y=1860:w=1080:h=8:color=black@0.5:t=fill,"
        f"drawbox=x=0:y=1860:w='1080*t/{dur}':h=8:color=0x00E5FF:t=fill[pbar];"
    )
    # Hook text
    lines.append(
        f"[pbar]drawtext=fontfile='{FONT}':text='{hook}':"
        f"fontsize=46:fontcolor=yellow:borderw=4:bordercolor=black:"
        f"x=(w-text_w)/2:y=130[hooked];"
    )
    # Speaker name
    lines.append(
        f"[hooked]drawtext=fontfile='{FONT}':text='{speaker}':"
        f"fontsize=32:fontcolor=white:borderw=3:bordercolor=black:"
        f"x=50:y=1780[spk];"
    )

    # Overlays (value-add layer)
    prev = "spk"
    for i, ov in enumerate(overlays):
        label = f"ov{i}"
        ts = ov["ts"]
        te = ts + ov["dur"]
        x = ov.get("x", 780)
        y = ov.get("y", 250)
        lines.append(
            f"[{prev}][{i+1}:v]overlay=x={x}:y={y}:enable='between(t,{ts},{te})':format=auto[{label}];"
        )
        prev = label

    # Subtitles (always last, top layer) + setsar
    lines.append(f"[{prev}]subtitles='{ass_path}',setsar=1[out];")

    return "\n".join(lines)


def render_clip(clip):
    clip_id = clip["id"]
    start = clip["start"]
    dur = clip["duration"]
    end = start + dur
    out_path = OUTDIR / f"{clip_id}.mp4"
    raw_path = TMPDIR / f"{clip_id}_raw.mp4"
    ass_path = TMPDIR / f"{clip_id}.ass"
    filter_path = TMPDIR / f"{clip_id}_filter.txt"

    print(f"\n{'='*60}")
    print(f"[{clip_id}] {start:.1f}s → {end:.1f}s ({dur:.1f}s) | {clip['hook']}")

    # 1. Raw extract (accurate seek)
    r = subprocess.run([
        "ffmpeg", "-y", "-ss", str(start), "-i", str(SOURCE), "-t", str(dur),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "0",
        "-c:a", "pcm_s16le", str(raw_path)
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  EXTRACT FAIL: {r.stderr[-300:]}")
        return None

    # 2. Subtitles
    segs = get_segs_in_range(start, end)
    clip["_ass"] = ass_path
    gen_ass(segs, ass_path, clip.get("punchlines", set()))
    if not segs:
        print(f"  WARN: no transcript segments in range, empty subs")

    # 3. Filter graph
    filter_content = build_filter(clip)
    filter_path.write_text(filter_content)

    # 4. Composite
    inputs = ["-i", str(raw_path)]
    for ov in clip.get("overlays", []):
        inputs += ["-i", str(OVERLAYS / f"{ov['name']}.png")]

    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex_script", str(filter_path),
        "-map", "[out]",
        "-map", "0:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "15",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest", "-movflags", "+faststart",
        str(out_path)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    raw_path.unlink(missing_ok=True)
    if r.returncode != 0:
        print(f"  RENDER FAIL: {r.stderr[-800:]}")
        return None

    # Verify
    v = subprocess.run([
        "ffprobe", "-v", "quiet", "-select_streams", "v:0",
        "-show_entries", "width,height,sample_aspect_ratio", "-of", "csv=p=0", str(out_path)
    ], capture_output=True, text=True)
    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"  OK: {out_path.name} | {v.stdout.strip().replace(',', ' | ')} | {size_mb:.1f} MB")
    return out_path


CLIPS = [
    # Will be filled after transcript analysis
]


def main():
    if not TRANSCRIPT.exists():
        print("ERROR: transcript not found. Run transcribe first.")
        sys.exit(1)

    # Import clip definitions
    sys.path.insert(0, str(ROOT / "scripts"))
    from billionaire_clips import CLIPS

    ids = sys.argv[1:] if len(sys.argv) > 1 else [c["id"] for c in CLIPS]
    clips = [c for c in CLIPS if c["id"] in ids]

    results = []
    for clip in clips:
        p = render_clip(clip)
        if p:
            results.append(p)

    print(f"\n{'='*60}")
    print(f"Rendered {len(results)}/{len(clips)} clips")
    for p in results:
        size = p.stat().st_size / (1024 * 1024)
        print(f"  {p.name} ({size:.1f} MB)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
