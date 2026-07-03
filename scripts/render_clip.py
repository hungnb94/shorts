#!/usr/bin/env python3
"""
Clip Curation Edit renderer (Video Type #7, ADR 0007).

Pipeline:
  1. Parse clip-edit script (.md with cut/value_add sections)
  2. Load source clip from output/source_clips/{source_video}.mp4
  3. Cut segments (each <15s, total <=50% source) + concat
  4. Scale/crop to 9:16 (1080x1920)
  5. Generate commentary TTS (replace original audio)
  6. Render value-add overlays (data_viz counter, fact-check callout, counter_argument)
  7. Composite: footage (muted) + commentary + animated captions + overlays
  8. Transformative Gate validation before output

Usage:
    /usr/bin/python3 scripts/render_clip.py scripts/v3_04_80m_clip.md --output output/
"""
import argparse
import asyncio
import subprocess
import os
import sys
import math
import json
import re
import tempfile
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import edge_tts

WIDTH, HEIGHT, FPS = 1080, 1920, 30
FONT_REG = "/System/Library/Fonts/Helvetica.ttc"
C_WHITE = (255, 255, 255)
C_GOLD = (255, 215, 0)
C_GREEN = (0, 255, 136)
C_RED = (255, 68, 68)
C_BLACK_TRANS = (0, 0, 0, 180)


def font(size, bold=True):
    try:
        return ImageFont.truetype(FONT_REG, size, index=1 if bold else 0)
    except Exception:
        return ImageFont.truetype(FONT_REG, size)


def parse_clip_script(path):
    with open(path) as f:
        content = f.read()
    parts = re.split(r'^---$', content.strip(), flags=re.MULTILINE)
    meta = {}
    body_parts = {}
    if len(parts) >= 3:
        for line in parts[1].strip().split('\n'):
            if ':' in line:
                k, _, v = line.partition(':')
                meta[k.strip()] = v.strip().strip('"\'')
        body = parts[2].strip()
        # Parse sections
        commentary_lines = []
        cuts = []
        value_adds = []
        for line in body.split('\n'):
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            m = re.match(r'cut_\d+:\s*([\d.]+)-([\d.]+)', line)
            if m:
                cuts.append((float(m.group(1)), float(m.group(2))))
                continue
            m = re.match(r'value_add_\d+:\s*(.+)', line)
            if m:
                value_adds.append(m.group(1).strip())
                continue
            m = re.match(r'(?:HOOK|BODY\d*|CLOSING):\s*(.+)', line)
            if m:
                commentary_lines.append(m.group(1).strip())
                continue
        body_parts['commentary'] = commentary_lines
        body_parts['cuts'] = cuts
        body_parts['value_adds'] = value_adds
    return {
        'title': meta.get('title', 'Untitled'),
        'voice': meta.get('voice', 'en-US-AndrewNeural'),
        'speed': float(meta.get('speed', '1.08')),
        'source_video': meta.get('source_video'),
        'source_duration': float(meta.get('source_duration', '0')),
        'max_clip_duration': float(meta.get('max_clip_duration', '45')),
        **body_parts,
    }


def check_transformative_gate(spec, total_cut_duration):
    """Validate all 3 Transformative Gate rules. Returns (pass, reason)."""
    # Rule 1: commentary track required
    if not spec.get('commentary'):
        return False, "FAIL Rule 1: no commentary track"
    # Rule 2: min 2 value-adds
    if len(spec.get('value_adds', [])) < 2:
        return False, f"FAIL Rule 2: only {len(spec.get('value_adds', []))} value-adds, need >=2"
    # Rule 3: cut <=50% source + each clip <15s
    for start, end in spec['cuts']:
        if (end - start) >= 15:
            return False, f"FAIL Rule 3: clip {start}-{end}s exceeds 15s limit"
    if spec['source_duration'] > 0:
        half = spec['source_duration'] / 2
        if total_cut_duration > half + 0.5:  # 0.5s tolerance
            return False, f"FAIL Rule 3: total cut {total_cut_duration:.1f}s > 50% of source ({half:.1f}s)"
    return True, "PASS all 3 rules"


async def generate_tts(text, voice, rate_str, output_path):
    rate_pct = int((float(rate_str) - 1) * 100)
    rate = f"+{rate_pct}%" if rate_pct > 0 else f"{rate_pct}%"
    comm = edge_tts.Communicate(text, voice, rate=rate)
    boundaries = []
    audio_data = bytearray()
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
        elif chunk["type"] == "SentenceBoundary":
            boundaries.append({
                "text": chunk["text"],
                "offset": chunk["offset"] / 1e7,
                "duration": chunk["duration"] / 1e7,
            })
    with open(output_path, "wb") as f:
        f.write(audio_data)
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", output_path],
        capture_output=True, text=True
    )
    total_dur = float(json.loads(result.stdout)["format"]["duration"])
    return boundaries, total_dur


def cut_and_concat(source_path, cuts, temp_dir):
    """Cut segments from source, concat into single clip. Returns (concat_path, total_duration)."""
    temp_dir = temp_dir.resolve()
    source_path = source_path.resolve()
    cut_files = []
    for i, (start, end) in enumerate(cuts):
        out = temp_dir / f"cut_{i}.mp4"
        duration = end - start
        cmd = [
            "ffmpeg", "-y", "-ss", str(start), "-i", str(source_path),
            "-t", str(duration),
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
            str(out)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        cut_files.append(out)
    # Concat
    concat_list = temp_dir / "concat.txt"
    with open(concat_list, 'w') as f:
        for cf in cut_files:
            f.write(f"file '{cf}'\n")
    concat_path = temp_dir / "footage.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
        str(concat_path)
    ], capture_output=True, check=True)
    # Get duration
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(concat_path)],
        capture_output=True, text=True
    )
    total = float(result.stdout.strip())
    return concat_path, total


def render_value_add_overlays(value_adds, commentary_duration, total_duration, temp_dir):
    """Render transparent PNG overlays (data_viz counter, fact-check callout)."""
    overlay_dir = temp_dir / "overlays"
    overlay_dir.mkdir(exist_ok=True)
    total_frames = int(total_duration * FPS)

    # Detect overlay type from value_add text
    has_data_viz = any('data_viz' in va for va in value_adds)
    has_fact_check = any('fact_check' in va for va in value_adds)

    # Extract money amount for data_viz counter
    money_target = "$80M"
    for va in value_adds:
        m = re.search(r'\$[\d,.]+[KMB]?', va)
        if m:
            money_target = m.group(0)
            break

    # Fact-check text (last ~4s)
    fact_text = next((va.replace('fact_check_callout', '').replace('"', '').strip() for va in value_adds if 'fact_check' in va), "")

    for i in range(total_frames):
        t = i / FPS
        img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Data viz counter (first 25% of video) — top area, semi-transparent
        if has_data_viz and t < total_duration * 0.5:
            progress = ease_out_cubic(min(1.0, t / max(0.1, total_duration * 0.4)))
            # Parse numeric target
            num_match = re.search(r'[\d,.]+', money_target)
            base = float(num_match.group().replace(',', '')) if num_match else 80
            mult = 1e6 if 'M' in money_target.upper() else (1e3 if 'K' in money_target.upper() else (1e9 if 'B' in money_target.upper() else 1))
            current = base * progress
            if current >= 1e9:
                display = f"${current/1e9:.1f}B"
            elif current >= 1e6:
                display = f"${current/1e6:.1f}M"
            else:
                display = f"${current/1e3:.0f}K"
            # Top banner
            draw.rectangle([0, 0, WIDTH, 180], fill=(0, 0, 0, 160))
            fnt = font(72)
            bbox = draw.textbbox((0, 0), display, font=fnt)
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw) // 2, 40), display, font=fnt, fill=C_GOLD)
            label_fnt = font(28)
            lbbox = draw.textbbox((0, 0), "SINGLE DAY REVENUE", font=label_fnt)
            ltw = lbbox[2] - lbbox[0]
            draw.text(((WIDTH - ltw) // 2, 130), "SINGLE DAY REVENUE", font=label_fnt, fill=C_WHITE)

        # Fact-check callout (last 30% of video) — bottom area
        if has_fact_check and fact_text and t > total_duration * 0.65:
            callout_t = t - total_duration * 0.65
            fade = min(1.0, callout_t / 0.5)
            alpha = int(220 * fade)
            # Bottom banner
            y_start = HEIGHT - 320
            draw.rectangle([40, y_start, WIDTH - 40, HEIGHT - 80], fill=(0, 0, 0, alpha), outline=C_GREEN + (alpha,) if isinstance(C_GREEN, tuple) and len(C_GREEN) == 3 else None)
            # FACT CHECK label
            label_fnt = font(26)
            draw.text((70, y_start + 25), "FACT CHECK", font=label_fnt, fill=C_GREEN + (alpha,))
            # Text (word-wrap)
            words = fact_text.split()
            lines = []
            cur = []
            for w in words:
                cur.append(w)
                test = ' '.join(cur)
                tbbox = draw.textbbox((0, 0), test, font=font(34))
                if (tbbox[2] - tbbox[0]) > WIDTH - 140:
                    cur.pop()
                    lines.append(' '.join(cur))
                    cur = [w]
            if cur:
                lines.append(' '.join(cur))
            for li, line in enumerate(lines[:4]):
                draw.text((70, y_start + 70 + li * 44), line, font=font(34), fill=C_WHITE + (alpha,))

        img.save(overlay_dir / f"frame_{i+1:05d}.png")
    return overlay_dir


def ease_out_cubic(t):
    return 1 - (1 - max(0, min(1, t))) ** 3


def render_caption_frames(commentary, boundaries, total_duration, temp_dir):
    """Render animated word-by-word caption frames (bottom-third, kinetic style)."""
    cap_dir = temp_dir / "captions"
    cap_dir.mkdir(exist_ok=True)
    total_frames = int(total_duration * FPS)
    # Flatten all commentary into timeline of (start, end, text)
    timeline = []
    if boundaries:
        cum = 0
        for li, line in enumerate(commentary):
            # Map proportionally to TTS boundaries
            pass
    # Simpler: distribute each commentary line evenly across TTS duration
    n = len(commentary)
    for i, line in enumerate(commentary):
        start = (i / n) * total_duration
        end = ((i + 1) / n) * total_duration
        timeline.append((start, end, line))

    for fi in range(total_frames):
        t = fi / FPS
        img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Find active line
        active = None
        local_t = 0
        for (s, e, txt) in timeline:
            if s <= t < e:
                active = txt
                local_t = t - s
                break
        if active:
            # Word-by-word pop-in
            words = active.split()
            y_base = HEIGHT - 500
            # Background box
            fnt = font(52)
            max_w = 0
            total_h = 0
            wrapped = []
            cur = []
            for w in words:
                cur.append(w)
                test = ' '.join(cur)
                tbbox = draw.textbbox((0, 0), test, font=fnt)
                if (tbbox[2] - tbbox[0]) > WIDTH - 120:
                    cur.pop()
                    wrapped.append(cur)
                    cur = [w]
            if cur:
                wrapped.append(cur)
            for line_words in wrapped:
                line_str = ' '.join(line_words)
                tbbox = draw.textbbox((0, 0), line_str, font=fnt)
                max_w = max(max_w, tbbox[2] - tbbox[0])
                total_h += 70
            box_y = y_base
            draw.rounded_rectangle([60, box_y - 20, WIDTH - 60, box_y + total_h + 20], radius=16, fill=(0, 0, 0, 200))
            # Render words with pop-in based on local_t
            words_per_sec = 2.5
            for li, line_words in enumerate(wrapped):
                for wi, word in enumerate(line_words):
                    word_idx = sum(len(w) for w in wrapped[:li]) + wi
                    word_t = local_t - word_idx / words_per_sec
                    if word_t < 0:
                        continue
                    scale = max(0.01, ease_out_cubic(min(1.0, word_t / 0.25)))
                    wfnt = font(max(1, int(52 * scale)))
                    # Position
                    line_str = ' '.join(line_words)
                    tbbox = draw.textbbox((0, 0), line_str, font=fnt)
                    line_w = tbbox[2] - tbbox[0]
                    # Per-word x offset within line
                    prefix = ' '.join(line_words[:wi]) + (' ' if wi > 0 else '')
                    pbbox = draw.textbbox((0, 0), prefix, font=fnt)
                    prefix_w = pbbox[2] - pbbox[0]
                    wbbox = draw.textbbox((0, 0), word, font=fnt)
                    word_w = wbbox[2] - wbbox[0]
                    x = (WIDTH - line_w) // 2 + prefix_w
                    y = box_y + li * 70
                    col = C_GOLD if any(sym in word for sym in ['$', '%', 'M', 'B']) else C_WHITE
                    draw.text((x, y), word, font=wfnt, fill=col + (255,))
        img.save(cap_dir / f"frame_{fi+1:05d}.png")
    return cap_dir


def composite_final(footage_path, commentary_path, overlay_dir, caption_dir, output_path, total_duration):
    """Composite: footage (muted) + commentary audio + overlays + captions."""
    footage_path = Path(footage_path).resolve()
    commentary_path = Path(commentary_path).resolve()
    overlay_dir = Path(overlay_dir).resolve()
    caption_dir = Path(caption_dir).resolve()
    output_path = Path(output_path).resolve()
    tmp = output_path.parent / f"_tmp_comp_{output_path.stem}"
    tmp.mkdir(exist_ok=True)

    # Encode overlays (with alpha) — use .mov for qtrle/argb compatibility
    overlay_mp4 = tmp / "overlay.mov"
    r = subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS),
        "-i", str(overlay_dir / "frame_%05d.png"),
        "-c:v", "qtrle", "-pix_fmt", "argb",
        "-t", str(total_duration), str(overlay_mp4)
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print("  overlay encode stderr:", r.stderr[-500:])
        raise RuntimeError("overlay encode failed")

    # Encode captions (with alpha) — use .mov for qtrle/argb compatibility
    caption_mp4 = tmp / "caption.mov"
    r = subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS),
        "-i", str(caption_dir / "frame_%05d.png"),
        "-c:v", "qtrle", "-pix_fmt", "argb",
        "-t", str(total_duration), str(caption_mp4)
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print("  caption encode stderr:", r.stderr[-500:])
        raise RuntimeError("caption encode failed")

    # Composite chain
    filter_complex = (
        f"[0:v][1:v]overlay=0:0[v1];"
        f"[v1][2:v]overlay=0:0[v2]"
    )
    r = subprocess.run([
        "ffmpeg", "-y",
        "-i", str(footage_path),
        "-i", str(overlay_mp4),
        "-i", str(caption_mp4),
        "-i", str(commentary_path),
        "-filter_complex", filter_complex,
        "-map", "[v2]", "-map", "3:a",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-t", str(total_duration), "-shortest",
        str(output_path)
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print("  composite stderr:", r.stderr[-800:])
        raise RuntimeError("composite failed")
    shutil.rmtree(tmp, ignore_errors=True)


async def render_clip_edit(script_path, output_dir):
    spec = parse_clip_script(script_path)
    print(f"[clip_edit] {spec['title']}")
    print(f"  source: {spec['source_video']} ({spec['source_duration']:.1f}s)")
    print(f"  cuts: {spec['cuts']}")
    print(f"  value_adds: {spec['value_adds']}")

    total_cut = sum(e - s for s, e in spec['cuts'])
    gate_pass, reason = check_transformative_gate(spec, total_cut)
    print(f"  Transformative Gate: {reason}")
    if not gate_pass:
        print(f"  ABORT: {reason}")
        return None

    source_path = Path(f"output/source_clips/{spec['source_video']}.mp4")
    if not source_path.exists():
        print(f"  ABORT: source clip not found: {source_path}")
        return None

    out_name = Path(script_path).stem + ".mp4"
    output_path = Path(output_dir) / out_name
    temp_dir = Path(output_dir) / f"_tmp_{Path(script_path).stem}"
    temp_dir.mkdir(exist_ok=True)

    try:
        # 1. Cut + concat footage
        print("  [1/5] cutting footage...")
        footage_path, footage_dur = cut_and_concat(source_path, spec['cuts'], temp_dir)
        print(f"    footage: {footage_dur:.1f}s")

        # 2. Generate commentary TTS
        print("  [2/5] generating commentary TTS...")
        commentary_text = ' '.join(spec['commentary'])
        commentary_path = temp_dir / "commentary.mp3"
        boundaries, tts_dur = await generate_tts(commentary_text, spec['voice'], str(spec['speed']), commentary_path)
        print(f"    TTS: {tts_dur:.1f}s, {len(boundaries)} boundaries")

        # Use TTS as final duration (commentary is backbone). Trim/loop footage to match.
        total_duration = tts_dur
        if footage_dur < tts_dur:
            # Loop footage to fill — concat footage with itself then trim
            looped = temp_dir / "footage_looped.mp4"
            loop_count = math.ceil(tts_dur / footage_dur)
            loop_list = temp_dir / "loop.txt"
            with open(loop_list, 'w') as f:
                for _ in range(loop_count):
                    f.write(f"file '{footage_path.resolve()}'\n")
            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(loop_list),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
                "-t", str(total_duration), str(looped)
            ], capture_output=True, check=True)
            footage_path = looped
        else:
            # Trim footage to TTS duration
            trimmed = temp_dir / "footage_trimmed.mp4"
            subprocess.run([
                "ffmpeg", "-y", "-i", str(footage_path),
                "-t", str(total_duration),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
                str(trimmed)
            ], capture_output=True, check=True)
            footage_path = trimmed
        print(f"  final duration: {total_duration:.1f}s")

        # 3. Render value-add overlays
        print("  [3/5] rendering value-add overlays...")
        overlay_dir = render_value_add_overlays(spec['value_adds'], tts_dur, total_duration, temp_dir)

        # 4. Render captions
        print("  [4/5] rendering captions...")
        caption_dir = render_caption_frames(spec['commentary'], boundaries, total_duration, temp_dir)

        # 5. Composite
        print("  [5/5] compositing...")
        composite_final(footage_path, commentary_path, overlay_dir, caption_dir, output_path, total_duration)
        print(f"  DONE: {output_path}")
        return output_path
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("script")
    parser.add_argument("--output", default="output/")
    args = parser.parse_args()
    asyncio.run(render_clip_edit(args.script, args.output))
