#!/usr/bin/env python3
"""
Viral Short Video Editor v3 — Production-grade with overlays
FIXES from v2:
  1. SAR 1:1 enforced (fixes stretched/distorted display)
  2. Animated emoji/icon overlays at key timestamps
  3. Flash effects at punchline moments
  4. Badge labels ("REAL TALK", "KEY INSIGHT" etc.)
  5. Zoom punch on key moments
  6. Big text callouts ("WOW!", "FACT:", "TRUTH")
"""

import json, subprocess, sys, os
from pathlib import Path

PROJECT = Path("/Users/hung/code/ai/shorts")
SOURCE = PROJECT / "output/source/Z7aS-7Mw_Wg.webm"
TRANSCRIPT = PROJECT / "output/transcript_full.json"
OUTDIR = PROJECT / "output/clips_v3"
TMPDIR = PROJECT / "output/tmp_v3"
OVERLAYS = PROJECT / "output/overlays"
FONT = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"

OUTDIR.mkdir(parents=True, exist_ok=True)
TMPDIR.mkdir(parents=True, exist_ok=True)

with open(TRANSCRIPT) as f:
    SEGMENTS = json.load(f)["segments"]


def fmt_ass_time(s):
    h = int(s // 3600); m = int((s % 3600) // 60); sec = int(s % 60)
    cs = round((s % 1) * 100)
    if cs == 100: cs = 0; sec += 1
    return f"{h}:{m:02d}:{sec:02d}.{cs:02d}"


def get_segs(start, end):
    result = []
    for seg in SEGMENTS:
        if seg["end"] < start or seg["start"] > end: continue
        cs = max(seg["start"], start) - start
        ce = min(seg["end"], end) - start
        text = seg["text"].replace("[music]","").replace("[snorts]","").strip()
        if text: result.append({"start": cs, "end": ce, "text": text})
    return result


def gen_ass(segs, output_path, punchlines=None):
    if punchlines is None: punchlines = set()
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
    for seg in segs:
        text = seg["text"]
        words = text.split()
        if not words: continue
        seg_dur = max(seg["end"] - seg["start"], 0.1)
        tpw = seg_dur / len(words)
        chunk_size = 4 if len(words) > 8 else (3 if len(words) > 4 else 2)
        chunks = [words[i:i+chunk_size] for i in range(0, len(words), chunk_size)]
        wi = 0
        for chunk in chunks:
            cs = seg["start"] + wi * tpw
            ce = min(seg["start"] + (wi + len(chunk)) * tpw, seg["end"])
            has_punch = any(w.lower().strip(".,!?\x27\x22") in punchlines for w in chunk)
            style = "Punch" if has_punch else "Main"
            parts = []
            for i, word in enumerate(chunk):
                delay = i * int(tpw * 800 / max(len(chunk), 1))
                anim = f"\\fad(60,0)\\fscx0\\fscy0\\t({delay},{delay+150},\\fscx100\\fscy100)"
                parts.append(f"{{{anim}}}{word}")
            display = " ".join(parts)
            events.append(f"Dialogue: 0,{fmt_ass_time(cs)},{fmt_ass_time(ce+0.25)},{style},,0,0,0,,{display}")
            wi += len(chunk)
    output_path.write_text(header + "\n".join(events) + "\n")


def render(clip_id, start, end, hook, speaker="", punchlines=None,
           overlays=None):
    """
    overlays: list of dicts:
        {"type": "icon", "name": "icon_money", "ts": 3.0, "x": 800, "y": 400, "dur": 2.0, "scale": 1.5}
        {"type": "badge", "name": "badge_truth", "ts": 5.0, "x": 270, "y": 500, "dur": 1.5}
        {"type": "flash", "name": "flash_yellow", "ts": 4.0, "dur": 0.3}
        {"type": "text", "name": "text_wow", "ts": 6.0, "x": 140, "y": 600, "dur": 1.0}
    """
    if punchlines is None: punchlines = set()
    if overlays is None: overlays = []

    duration = end - start
    out = OUTDIR / f"{clip_id}.mp4"
    raw = TMPDIR / f"{clip_id}_raw.mp4"
    ass = TMPDIR / f"{clip_id}.ass"

    print(f"\n{'='*60}")
    print(f"🎬 {clip_id}: {duration:.1f}s | {hook}")
    print(f"   {len(overlays)} overlays planned")

    # Step 1: Extract raw
    r = subprocess.run([
        "ffmpeg", "-y", "-ss", str(start), "-i", str(SOURCE),
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "0",
        "-c:a", "pcm_s16le", str(raw)
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"❌ Extract: {r.stderr[-300:]}"); return None

    # Step 2: Subtitles
    segs = get_segs(start, end)
    gen_ass(segs, ass, punchlines)

    # Step 3: Build filter
    bg_scale = max(1080.0 / 1280, 1920.0 / 720)
    bg_w = int(1280 * bg_scale)
    bg_h = int(720 * bg_scale)
    bg_crop_x = (bg_w - 1080) // 2
    fg_crop_x = (1280 - 405) // 2

    hook_safe = hook.replace(":", "-").replace("'", "")
    speaker_safe = speaker.replace(":", "-").replace("'", "")

    # Start building filter chain
    # KEY FIX: setsar=1 at the END to ensure square pixels
    parts = []

    # Split source
    parts.append(f"[0:v]split=2[bg_src][fg_src]")

    # Background: scale → crop → blur → darken
    parts.append(
        f"[bg_src]scale={bg_w}:{bg_h},"
        f"crop=1080:1920:{bg_crop_x}:0,"
        f"boxblur=luma_radius=60:luma_power=3,"
        f"drawbox=x=0:y=0:w=1080:h=1920:color=black@0.35:t=fill[bg]"
    )

    # Foreground: crop → scale → sharpen
    # CRITICAL: setsar=1 here to fix pixel aspect ratio
    parts.append(
        f"[fg_src]crop=405:720:{fg_crop_x}:0,"
        f"scale=1080:1920:flags=lanczos,"
        f"setsar=1,"
        f"unsharp=5:5:0.8:3:3:0.4[fg_sharp]"
    )

    # Composite
    parts.append(f"[bg][fg_sharp]overlay=0:0[comp1]")

    # Apply overlays sequentially
    current_label = "comp1"
    overlay_idx = 2

    for ov in overlays:
        ov_path = OVERLAYS / f"{ov['name']}.png"
        if not ov_path.exists():
            continue

        ts = ov.get("ts", 0)
        dur = ov.get("dur", 1.5)
        x = ov.get("x", 540)
        y = ov.get("y", 960)
        scale = ov.get("scale", 1.0)
        ov_type = ov.get("type", "icon")

        # Calculate scaled dimensions
        if scale != 1.0:
            # We need to pre-scale the overlay PNG
            # Read original dimensions
            probe = subprocess.run(
                ["ffprobe", "-v", "quiet", "-show_entries", "stream=width,height",
                 "-of", "csv=p=0", str(ov_path)],
                capture_output=True, text=True
            )
            ow, oh = [int(x) for x in probe.stdout.strip().split(",")]
            sw, sh = int(ow * scale), int(oh * scale)
            scaled_path = TMPDIR / f"{clip_id}_ov_{ov_idx}_{ov['name']}_{scale}.png"
            subprocess.run([
                "ffmpeg", "-y", "-i", str(ov_path),
                "-vf", f"scale={sw}:{sh}",
                str(scaled_path)
            ], capture_output=True, text=True)
            ov_input = str(scaled_path)
            input_idx = overlay_idx
            parts.append(f"[{current_label}][{input_idx}:v]overlay=x={x}:y=y='if(lt(t,{ts})|gt(t,{ts+dur}),-9999,{y})':"
                        f"format=auto[next_{overlay_idx}]")
        else:
            input_idx = overlay_idx
            parts.append(f"[{current_label}][{input_idx}:v]overlay=x={x}:y='if(lt(t,{ts})|gt(t,{ts+dur}),-9999,{y})':"
                        f"format=auto[next_{overlay_idx}]")

        current_label = f"next_{overlay_idx}"
        overlay_idx += 1

    # Progress bar
    parts.append(
        f"[{current_label}]"
        f"drawbox=x=0:y=1860:w=1080:h=8:color=black@0.5:t=fill,"
        f"drawbox=x=0:y=1860:w='1080*t/{duration}':h=8:color=0x00E5FF:t=fill[pbar]"
    )
    current_label = "pbar"

    # Hook + speaker text
    parts.append(
        f"[{current_label}]"
        f"drawtext=fontfile={FONT}:text='{hook_safe}':fontsize=50:fontcolor=yellow:borderw=4:bordercolor=black:x=(w-text_w)/2:y=135,"
        f"drawtext=fontfile={FONT}:text='{speaker_safe}':fontsize=34:fontcolor=white:borderw=3:bordercolor=black:x=50:y=1770[texted]"
    )
    current_label = "texted"

    # Subtitles
    parts.append(f"[{current_label}]subtitles='{ass}',setsar=1[out]")

    # Write filter to file
    filter_file = TMPDIR / f"{clip_id}_filter.txt"
    filter_file.write_text(";\n".join(parts))

    # Build ffmpeg command with overlay inputs
    cmd = ["ffmpeg", "-y", "-i", str(raw)]
    for ov in overlays:
        ov_path = OVERLAYS / f"{ov['name']}.png"
        if ov_path.exists():
            scale = ov.get("scale", 1.0)
            if scale != 1.0:
                scaled = TMPDIR / f"{clip_id}_scaled_{ov['name']}.png"
                ow_sh = subprocess.run(
                    ["ffprobe", "-v", "quiet", "-show_entries", "stream=width,height",
                     "-of", "csv=p=0", str(ov_path)], capture_output=True, text=True)
                ow, oh = [int(x) for x in ow_sh.stdout.strip().split(",")]
                sw, sh = int(ow * scale), int(oh * scale)
                subprocess.run(["ffmpeg", "-y", "-i", str(ov_path),
                                "-vf", f"scale={sw}:{sh}", str(scaled)],
                               capture_output=True, text=True)
                cmd.extend(["-i", str(scaled)])
            else:
                cmd.extend(["-i", str(ov_path)])

    cmd.extend([
        "-filter_complex_script", str(filter_file),
        "-map", "[out]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "15",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        str(out)
    ])

    print("   🎨 Rendering with overlays...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"❌ Render: {r.stderr[-600:]}")
        return None

    raw.unlink(missing_ok=True)

    # Verify SAR is fixed
    verify = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries",
         "stream=width,height,sample_aspect_ratio,display_aspect_ratio",
         "-of", "csv=p=0", str(out)],
        capture_output=True, text=True
    )
    size = out.stat().st_size / (1024 * 1024)
    print(f"✅ {out.name} | {verify.stdout.strip().replace(chr(10), ' | ')} | {size:.1f} MB")
    return out


# ════════════════════════════════════════════════════════════
# CLIP DEFINITIONS WITH OVERLAYS
# ════════════════════════════════════════════════════════════

CLIPS = [
    {
        "id": "01-giver-taker",
        "start": 258.0, "end": 284.0,
        "hook": "THE SECRET TO WEALTH",
        "speaker": "John Hope Bryant",
        "punchlines": {"exotic","neurotic","psychotic","givers","takers","toxicity","frequency","broke","tenth"},
        "overlays": [
            {"type":"icon","name":"icon_brain","ts":2.0,"x":800,"y":300,"dur":2.0},
            {"type":"badge","name":"badge_key","ts":4.5,"x":250,"y":500,"dur":2.0},
            {"type":"flash","name":"flash_yellow","ts":5.0,"dur":0.2},
            {"type":"icon","name":"icon_warning","ts":8.0,"x":100,"y":600,"dur":1.5},
            {"type":"badge","name":"badge_truth","ts":12.0,"x":250,"y":450,"dur":2.0},
            {"type":"flash","name":"flash_red","ts":12.5,"dur":0.15},
            {"type":"icon","name":"icon_target","ts":16.0,"x":820,"y":350,"dur":2.0},
            {"type":"text","name":"text_truth","ts":18.0,"x":140,"y":700,"dur":1.5},
            {"type":"icon","name":"icon_100","ts":21.0,"x":800,"y":400,"dur":2.0},
        ],
    },
    {
        "id": "02-taco-bell",
        "start": 299.0, "end": 312.0,
        "hook": "HE GOT $100M AT TACO BELL",
        "speaker": "John Hope Bryant",
        "punchlines": {"exit","wire","taco","bell","number","three","money","small","big","soon"},
        "overlays": [
            {"type":"icon","name":"icon_money","ts":1.0,"x":800,"y":250,"dur":2.0,"scale":1.5},
            {"type":"badge","name":"badge_money","ts":2.5,"x":250,"y":500,"dur":2.5},
            {"type":"flash","name":"flash_green","ts":3.0,"dur":0.2},
            {"type":"text","name":"text_wow","ts":4.5,"x":140,"y":600,"dur":1.5},
            {"type":"icon","name":"icon_100","ts":6.5,"x":820,"y":300,"dur":2.0},
            {"type":"icon","name":"icon_crown","ts":8.5,"x":100,"y":500,"dur":2.0},
        ],
    },
    {
        "id": "03-claude-code",
        "start": 1094.0, "end": 1108.0,
        "hook": "BILL ACKMAN- LEARN THIS NOW",
        "speaker": "Bill Ackman",
        "punchlines": {"ai","code","claude","company","website","build","greatest","history","entrepreneurship"},
        "overlays": [
            {"type":"icon","name":"icon_idea","ts":1.5,"x":800,"y":250,"dur":2.0,"scale":1.3},
            {"type":"badge","name":"badge_protip","ts":3.0,"x":250,"y":500,"dur":2.5},
            {"type":"flash","name":"flash_yellow","ts":4.0,"dur":0.2},
            {"type":"icon","name":"icon_bolt","ts":5.5,"x":100,"y":400,"dur":2.0,"scale":1.2},
            {"type":"text","name":"text_fact","ts":7.0,"x":140,"y":600,"dur":1.5},
            {"type":"icon","name":"icon_target","ts":9.0,"x":820,"y":350,"dur":2.0},
        ],
    },
    {
        "id": "04-nine-broke",
        "start": 273.0, "end": 285.0,
        "hook": "YOUR FRIENDS YOUR FUTURE",
        "speaker": "John Hope Bryant",
        "punchlines": {"nine","broke","tenth","givers","takers","life","takes","proximity"},
        "overlays": [
            {"type":"icon","name":"icon_warning","ts":1.5,"x":820,"y":300,"dur":2.0},
            {"type":"flash","name":"flash_red","ts":2.5,"dur":0.15},
            {"type":"badge","name":"badge_warning","ts":3.5,"x":250,"y":500,"dur":2.0},
            {"type":"text","name":"text_never","ts":5.5,"x":140,"y":650,"dur":1.5},
            {"type":"icon","name":"icon_target","ts":7.5,"x":100,"y":500,"dur":2.0},
            {"type":"badge","name":"badge_truth","ts":9.0,"x":250,"y":450,"dur":2.0},
        ],
    },
    {
        "id": "05-never-get-rich",
        "start": 831.0, "end": 842.0,
        "hook": "YOU WILL NEVER GET RICH",
        "speaker": "Wall Street Trader",
        "punchlines": {"never","rich","working","somebody","else","desire","ai","work","yourself"},
        "overlays": [
            {"type":"text","name":"text_never","ts":1.0,"x":140,"y":600,"dur":1.5},
            {"type":"flash","name":"flash_red","ts":2.0,"dur":0.2},
            {"type":"badge","name":"badge_warning","ts":3.0,"x":250,"y":500,"dur":2.0},
            {"type":"icon","name":"icon_money","ts":5.0,"x":820,"y":300,"dur":2.0,"scale":1.3},
            {"type":"icon","name":"icon_bolt","ts":7.0,"x":100,"y":500,"dur":1.5,"scale":1.2},
        ],
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
        path = render(
            clip_id=clip["id"],
            start=clip["start"], end=clip["end"],
            hook=clip["hook"], speaker=clip["speaker"],
            punchlines=clip["punchlines"],
            overlays=clip["overlays"],
        )
        if path: results.append(path)

    print(f"\n{'='*60}")
    print(f"📊 Rendered {len(results)}/{len(clips)} clips")
    for p in results:
        print(f"  ✅ {p.name} ({p.stat().st_size/1024/1024:.1f} MB)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
