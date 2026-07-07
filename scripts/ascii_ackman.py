#!/usr/bin/env python3
"""
Colored ASCII Art Video Converter for Bill Ackman Short.

Takes video segments → converts frames to colored ASCII art →
renders back to video with original audio.

Pipeline:
  1. Extract frames from source segment (ffmpeg pipe)
  2. For each frame: resize → luminance → map to chars → apply source colors
  3. Render char grid to PIL image
  4. Pipe frames to ffmpeg for encoding
  5. Mux with original audio
"""
import subprocess
import tempfile
import os
import sys
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── Config ──
ROOT = Path("/Users/hung/code/ai/shorts")
SEGMENTS_DIR = ROOT / "output/ackman_ascii/segments"
OUTDIR = ROOT / "output/ackman_ascii"
TMPDIR = ROOT / "output/ackman_ascii/tmp"
TMPDIR.mkdir(parents=True, exist_ok=True)

# ASCII character density ramp (dark → bright)
DENSITY_CHARS = " .,:;+*?%S#@"
# Font for ASCII characters
FONT_PATH = "/System/Library/Fonts/Menlo.ttc"
# Grid dimensions (chars) — will be calculated based on output resolution
OUTPUT_W, OUTPUT_H = 1080, 1920  # 9:16
FPS = 30
CHAR_W, CHAR_H = 9, 16  # pixel size per character cell


def get_video_info(path):
    """Get video width, height, fps, duration."""
    r = subprocess.run([
        "ffprobe", "-v", "quiet", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,duration",
        "-show_entries", "format=duration",
        "-of", "json", str(path)
    ], capture_output=True, text=True)
    import json
    data = json.loads(r.stdout)
    stream = data["streams"][0]
    fmt = data.get("format", {})
    w, h = int(stream["width"]), int(stream["height"])
    # Parse fps from ratio
    num, den = stream["r_frame_rate"].split("/")
    fps = int(num) / int(den)
    dur = float(fmt.get("duration", stream.get("duration", 0)))
    return w, h, fps, dur


def frame_to_colored_ascii(frame_rgb, cols, rows, chars=DENSITY_CHARS):
    """Convert RGB frame to character grid + color grid.
    
    Returns:
        char_grid: (rows, cols) array of characters
        color_grid: (rows, cols, 3) array of RGB colors
    """
    h, w = frame_rgb.shape[:2]
    
    # Resize to grid dimensions
    img = Image.fromarray(frame_rgb).resize((cols, rows), Image.LANCZOS)
    small = np.array(img)
    
    # Compute luminance
    lum = (0.299 * small[:, :, 0] + 0.587 * small[:, :, 1] + 0.114 * small[:, :, 2]) / 255.0
    
    # Map luminance to characters
    n_chars = len(chars)
    indices = (np.clip(lum, 0, 0.999) * n_chars).astype(int)
    char_grid = np.array([[chars[i] for i in row] for row in indices])
    
    # Color: source pixel colors, boosted for visibility on dark bg
    # Brighter pixels = more saturated colors
    boost = np.clip(lum[:, :, None] * 2.0 + 0.4, 0.5, 1.2)
    color_grid = np.clip(small.astype(np.float32) * boost, 0, 255).astype(np.uint8)
    
    return char_grid, color_grid


def render_ascii_frame(char_grid, color_grid, font, cell_w, cell_h):
    """Render character grid to a PIL Image."""
    rows, cols = char_grid.shape
    img = Image.new("RGB", (cols * cell_w, rows * cell_h), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    for r in range(rows):
        for c in range(cols):
            ch = char_grid[r, c]
            if ch == ' ':
                continue  # Skip spaces (black bg)
            cr, cg, cb = color_grid[r, c]
            x = c * cell_w
            y = r * cell_h
            draw.text((x, y), ch, font=font, fill=(int(cr), int(cg), int(cb)))
    
    return img


def add_text_overlay(img, text, y_pos, font_path, font_size=32, color=(255, 215, 0)):
    """Add text overlay to the bottom/center of the frame."""
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    x = (img.width - text_w) // 2
    
    # Draw shadow
    draw.text((x + 2, y_pos + 2), text, font=font, fill=(0, 0, 0))
    # Draw text
    draw.text((x, y_pos), text, font=font, fill=color)
    
    return img


def add_progress_bar(img, progress, bar_h=8, color=(0, 229, 255)):
    """Add progress bar at bottom of frame."""
    draw = ImageDraw.Draw(img)
    y = img.height - bar_h - 20
    # Background bar
    draw.rectangle([40, y, img.width - 40, y + bar_h], fill=(50, 50, 50))
    # Progress
    bar_w = int((img.width - 80) * progress)
    draw.rectangle([40, y, 40 + bar_w, y + bar_h], fill=color)
    return img


def add_segment_label(img, label, font_path, font_size=24):
    """Add segment label at top."""
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()
    
    # Semi-transparent background
    draw.rectangle([20, 20, 300, 60], fill=(0, 0, 0, 180))
    draw.text((30, 25), label, font=font, fill=(255, 255, 255))
    return img


def segment_to_ascii_video(segment_path, output_path, label, quote_text=None, is_finale=False,
                           global_offset=0, total_global_frames=1):
    """Convert a single segment to colored ASCII art video with original audio.
    
    is_finale=True: larger text, positioned higher (for ending segments).
    global_offset/total_global_frames: overall video progress tracking.
    """
    print(f"\n  Converting: {segment_path.name}")
    
    # Get video info
    src_w, src_h, src_fps, duration = get_video_info(segment_path)
    n_frames = int(duration * FPS)
    print(f"    Source: {src_w}x{src_h} @ {src_fps:.1f}fps, {duration:.1f}s ({n_frames} frames)")
    
    # Calculate grid dimensions
    cols = OUTPUT_W // CHAR_W  # ~120 chars wide
    rows = OUTPUT_H // CHAR_H  # ~120 chars tall
    print(f"    Grid: {cols}x{rows} chars ({CHAR_W}x{CHAR_H}px each)")
    
    # Load font
    try:
        font = ImageFont.truetype(FONT_PATH, CHAR_H - 2)
    except:
        font = ImageFont.load_default()
        print("    Warning: using default font")
    
    # Start ffmpeg encoder (pipe raw frames)
    tmp_video = TMPDIR / f"{segment_path.stem}_ascii.mp4"
    encode_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{OUTPUT_W}x{OUTPUT_H}",
        "-r", str(FPS),
        "-i", "pipe:0",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(tmp_video),
    ]
    encoder = subprocess.Popen(
        encode_cmd, stdin=subprocess.PIPE,
        stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
    )
    
    # Extract frames from source and convert to ASCII
    extract_cmd = [
        "ffmpeg", "-i", str(segment_path),
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{src_w}x{src_h}",
        "-r", str(FPS),
        "-"
    ]
    extractor = subprocess.Popen(
        extract_cmd, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )
    
    frame_size = src_w * src_h * 3
    rendered = 0
    
    for fi in range(n_frames):
        raw = extractor.stdout.read(frame_size)
        if len(raw) < frame_size:
            break
        
        frame = np.frombuffer(raw, dtype=np.uint8).reshape(src_h, src_w, 3)
        
        # Convert to colored ASCII
        char_grid, color_grid = frame_to_colored_ascii(frame, cols, rows)
        
        # Render to image
        img = render_ascii_frame(char_grid, color_grid, font, CHAR_W, CHAR_H)
        
        # Add overlays
        img = add_segment_label(img, label, FONT_PATH)
        if quote_text:
            if is_finale:
                # Larger text, positioned higher for finale segments
                img = add_text_overlay(img, quote_text, OUTPUT_H - 400, FONT_PATH, font_size=48)
            else:
                img = add_text_overlay(img, quote_text, OUTPUT_H - 200, FONT_PATH, font_size=28)
        progress = (global_offset + fi) / max(total_global_frames - 1, 1)
        img = add_progress_bar(img, progress)
        
        # Pipe frame to encoder
        encoder.stdin.write(img.tobytes())
        rendered += 1
        
        if fi % 30 == 0:
            print(f"    Frame {fi}/{n_frames} ({fi*100//n_frames}%)")
    
    # Close streams
    extractor.stdout.close()
    encoder.stdin.close()
    encoder.wait()
    extractor.wait()
    
    print(f"    Rendered: {rendered} frames → {tmp_video.name}")
    
    # Mux with original audio
    final_out = output_path
    mux_cmd = [
        "ffmpeg", "-y",
        "-i", str(tmp_video),       # ASCII video
        "-i", str(segment_path),    # Original audio
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "128k",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        "-movflags", "+faststart",
        str(final_out),
    ]
    r = subprocess.run(mux_cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"    MUX FAIL: {r.stderr[-300:]}")
        return None
    
    print(f"    Done: {final_out.name}")
    return final_out


async def main():
    print("=" * 70)
    print("  ACKMAN ASCII VIDEO — Colored ASCII Art")
    print(f"  Segments: {SEGMENTS_DIR}")
    print(f"  Output: {OUTDIR}")
    print("=" * 70)
    
    # Segment definitions: (file, label, quote_text, is_finale)
    # Narrative: Chase → Ideas → Optimism → Successful → Smiling → Money Fast → Investment → Long-term → Never Give Up
    segments = [
        ("H_chase.mp4", "THE CHASE", '"Excuse me sir! Bill!"', False),
        ("B_ideas.mp4", "IDEAS > CONNECTIONS", '"If you build it, they will come."', False),
        ("F_optimism.mp4", "OPTIMISM", '"You have to be optimistic."', False),
        ("G_successful.mp4", "SUCCESS", '"Successful people are inspired by people trying to make it."', False),
        ("H_smiling.mp4", "SMILING & DIALING", '"I remembered smiling and dialing and getting rejected..."', False),
        ("I_moneyfast.mp4", "WARNING", '"Trying to make money fast = guaranteed bad outcome."', False),
        ("J_investadvice.mp4", "ADVICE", '"Learn by reading. Longer term view."', False),
        ("D_longterm.mp4", "LONG-TERM WINS", '"A huge advantage."', True),
        ("E_nevergiveup.mp4", "NEVER GIVE UP", '"Never give up."', True),
    ]
    
    rendered_segments = []
    
    # First pass: calculate total frames across all segments
    total_global_frames = 0
    segment_frame_counts = []
    for fname, label, quote, is_finale in segments:
        seg_path = SEGMENTS_DIR / fname
        if not seg_path.exists():
            segment_frame_counts.append(0)
            continue
        w, h, fps, dur = get_video_info(seg_path)
        n_frames = int(dur * FPS)
        segment_frame_counts.append(n_frames)
        total_global_frames += n_frames
    print(f"\n  Total frames: {total_global_frames}")
    
    # Second pass: render with global progress tracking
    global_offset = 0
    for i, (fname, label, quote, is_finale) in enumerate(segments):
        seg_path = SEGMENTS_DIR / fname
        out_path = OUTDIR / f"ascii_{fname}"
        if not seg_path.exists():
            print(f"  SKIP: {fname} not found")
            continue
        result = segment_to_ascii_video(
            seg_path, out_path, label, quote, is_finale=is_finale,
            global_offset=global_offset, total_global_frames=total_global_frames
        )
        if result:
            rendered_segments.append(result)
        global_offset += segment_frame_counts[i]
    
    # Concatenate all segments
    if len(rendered_segments) > 1:
        print(f"\n  Concatenating {len(rendered_segments)} segments...")
        concat_file = TMPDIR / "concat.txt"
        lines = [f"file '{s.absolute()}'" for s in rendered_segments]
        concat_file.write_text("\n".join(lines))
        
        final_path = OUTDIR / "ackman_ascii_never_give_up.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            str(final_path),
        ], capture_output=True, check=True)
    elif len(rendered_segments) == 1:
        final_path = OUTDIR / "ackman_ascii_never_give_up.mp4"
        rendered_segments[0].rename(final_path)
    else:
        print("  ERROR: No segments rendered")
        return
    
    # Verify
    r = subprocess.run([
        "ffprobe", "-v", "quiet", "-show_entries",
        "stream=width,height,codec_name", "-of", "csv=p=0", str(final_path)
    ], capture_output=True, text=True)
    dur_r = subprocess.run([
        "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(final_path)
    ], capture_output=True, text=True)
    final_dur = float(dur_r.stdout.strip() or 0)
    size_mb = final_path.stat().st_size / (1024*1024)
    
    print(f"\n{'='*70}")
    print(f"  DONE!")
    print(f"   Path: {final_path}")
    print(f"   Duration: {final_dur:.1f}s")
    print(f"   Size: {size_mb:.1f}MB")
    print(f"   Streams: {r.stdout.strip()}")
    print(f"{'='*70}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
