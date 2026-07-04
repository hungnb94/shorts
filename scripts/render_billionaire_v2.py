#!/usr/bin/env python3
"""
Billionaire Shorts renderer v2 — multi-segment stitching + sentence boundaries.

New features:
  1. Multi-segment clips — concat multiple ranges with 0.3s crossfade
  2. Sentence boundary snapping — no mid-sentence cuts
  3. Smart subtitle offsetting — per-segment transcript slicing

Pipeline per clip:
  1. Extract each segment as raw mp4
  2. Concat segments with xfade filter (0.3s crossfade)
  3. Generate unified ASS subtitles (offset per segment)
  4. Build filter_complex_script (blur bg + sharp fg + overlays)
  5. Composite final (H264 + AAC)
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
BG_SCALE = max(1080.0 / SRC_W, 1920.0 / SRC_H)  # 5.333
BG_W = int(SRC_W * BG_SCALE)  # 3413
BG_H = int(SRC_H * BG_SCALE)  # 1920
BG_CROP_X = (BG_W - 1080) // 2  # 1166
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


def build_filter(clip, raw_path):
    """Build the complete filter_complex graph for a clip."""
    dur = clip["duration"]
    hook = esc(clip["hook"])
    speaker = esc(clip.get("speaker", "School of Hard Knocks"))
    ass_path = esc(str(clip["_ass"]))
    overlays = clip.get("overlays", [])

    lines = []
    lines.append("[0:v]split=2[bg_src][fg_src];")
    lines.append(
        f"[bg_src]scale={BG_W}:{BG_H},crop=1080:1920:{BG_CROP_X}:0,"
        f"boxblur=luma_radius=60:luma_power=3,"
        f"drawbox=x=0:y=0:w=1080:h=1920:color=black@0.35:t=fill[bg];"
    )
    lines.append(
        f"[fg_src]crop={FG_W}:{SRC_H}:{FG_X}:0,scale=1080:1920:flags=lanczos,setsar=1,"
        f"unsharp=5:5:0.8:3:3:0.4[fg_sharp];"
    )
    lines.append("[bg][fg_sharp]overlay=0:0,vignette=PI/5[comp];")
    lines.append(
        f"[comp]drawbox=x=0:y=1860:w=1080:h=8:color=black@0.5:t=fill,"
        f"drawbox=x=0:y=1860:w='1080*t/{dur}':h=8:color=0x00E5FF:t=fill[pbar];"
    )
    lines.append(
        f"[pbar]drawtext=fontfile='{FONT}':text='{hook}':"
        f"fontsize=46:fontcolor=yellow:borderw=4:bordercolor=black:"
        f"x=(w-text_w)/2:y=130[hooked];"
    )
    lines.append(
        f"[hooked]drawtext=fontfile='{FONT}':text='{speaker}':"
        f"fontsize=32:fontcolor=white:borderw=3:bordercolor=black:"
        f"x=50:y=1780[spk];"
    )

    # Overlays
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

    # Subtitles
    lines.append(f"[{prev}]subtitles='{ass_path}',setsar=1[out];")

    return "\n".join(lines)


def concat_segments(clip, clip_id):
    """Extract + concat multiple segments with crossfade. Returns concat mp4 path."""
    segments = clip["segments"]
    if len(segments) == 1:
        # Single segment — direct extract
        seg = segments[0]
        out = TMPDIR / f"{clip_id}_raw.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-ss", str(seg["start"]), "-i", str(SOURCE),
            "-t", str(seg["end"] - seg["start"]),
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "0",
            "-c:a", "pcm_s16le", str(out)
        ], capture_output=True, check=True)
        return out
    
    # Multi-segment — extract each + concat with xfade
    seg_files = []
    for i, seg in enumerate(segments):
        seg_path = TMPDIR / f"{clip_id}_seg{i}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-ss", str(seg["start"]), "-i", str(SOURCE),
            "-t", str(seg["end"] - seg["start"]),
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "0",
            "-c:a", "pcm_s16le", str(seg_path)
        ], capture_output=True, check=True)
        seg_files.append(seg_path)
    
    # Build xfade filter graph: [0:v][1:v]xfade=transition=fade:duration=0.3:offset=D1[v01]; [v01][2:v]xfade...
    xfade_dur = 0.3
    filter_lines = []
    audio_inputs = "".join(f"[{i}:a]" for i in range(len(seg_files)))
    
    if len(seg_files) == 2:
        d1 = segments[0]["end"] - segments[0]["start"] - xfade_dur
        filter_lines.append(f"[0:v][1:v]xfade=transition=fade:duration={xfade_dur}:offset={d1}[v];")
        filter_lines.append(f"{audio_inputs}concat=n={len(seg_files)}:v=0:a=1[a];")
    else:
        # 3+ segments
        prev_label = "v"
        offset_acc = 0
        for i in range(len(seg_files) - 1):
            d = segments[i]["end"] - segments[i]["start"] - xfade_dur
            offset_acc += d
            in_a = f"[{i}:v]" if i == 0 else f"[{prev_label}]"
            in_b = f"[{i+1}:v]"
            out_label = "v" if i == len(seg_files) - 2 else f"v{i+1}"
            filter_lines.append(f"{in_a}{in_b}xfade=transition=fade:duration={xfade_dur}:offset={offset_acc}[{out_label}];")
            prev_label = out_label
        filter_lines.append(f"{audio_inputs}concat=n={len(seg_files)}:v=0:a=1[a];")
    
    filter_script = TMPDIR / f"{clip_id}_xfade.txt"
    filter_script.write_text("\n".join(filter_lines))
    
    # Concat
    concat_out = TMPDIR / f"{clip_id}_raw.mp4"
    inputs = []
    for f in seg_files:
        inputs += ["-i", str(f)]
    
    subprocess.run([
        "ffmpeg", "-y", *inputs,
        "-filter_complex_script", str(filter_script),
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "0",
        "-c:a", "pcm_s16le", str(concat_out)
    ], capture_output=True, check=True)
    
    # Cleanup segment files
    for f in seg_files:
        f.unlink(missing_ok=True)
    
    return concat_out


def render_clip(clip):
    clip_id = clip["id"]
    out_path = OUTDIR / f"{clip_id}.mp4"
    ass_path = TMPDIR / f"{clip_id}.ass"
    filter_path = TMPDIR / f"{clip_id}_filter.txt"

    print(f"\n{'='*60}")
    print(f"[{clip_id}] {clip['duration']:.1f}s | {len(clip['segments'])} segments | {clip['hook']}")

    # 1. Extract + concat segments
    try:
        raw_path = concat_segments(clip, clip_id)
    except subprocess.CalledProcessError as e:
        print(f"  EXTRACT FAIL: {e}")
        return None

    # 2. Subtitles — collect transcript from all segments
    all_segs = []
    time_offset = 0
    for seg_def in clip["segments"]:
        seg_segs = get_segs_in_range(seg_def["start"], seg_def["end"])
        # Offset each segment to clip-local time
        for s in seg_segs:
            s["start"] += time_offset
            s["end"] += time_offset
            all_segs.append(s)
        time_offset += (seg_def["end"] - seg_def["start"])
    
    clip["_ass"] = ass_path
    gen_ass(all_segs, ass_path, clip.get("punchlines", set()))

    # 3. Filter graph
    filter_content = build_filter(clip, raw_path)
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
        "-show_entries", "stream=width,height", "-of", "csv=p=0", str(out_path)
    ], capture_output=True, text=True)
    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"  OK: {out_path.name} | {v.stdout.strip()} | {size_mb:.1f} MB")
    return out_path


def main():
    if not TRANSCRIPT.exists():
        print("ERROR: transcript not found.")
        sys.exit(1)

    sys.path.insert(0, str(ROOT / "scripts"))
    from billionaire_clips_v2 import CLIPS

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
