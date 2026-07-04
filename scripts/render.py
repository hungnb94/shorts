#!/usr/bin/env python3
"""
Multi-format renderer — accepts a script YAML file + video type, outputs MP4.
Reuses TTS from viral-video-factory, renders visuals via PIL/Playwright.

Usage:
    /usr/bin/python3 scripts/render.py scripts/topic.md --type data_viz --output output/
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
import textwrap
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Ensure edge_tts available
import edge_tts

# === CONFIG ===
WIDTH, HEIGHT, FPS = 1080, 1920, 30
FONT_REG = "/System/Library/Fonts/Helvetica.ttc"
FONT_MONO = "/System/Library/Fonts/Menlo.ttc"

# Colors
C_BG_DARK = (15, 15, 23)
C_BG_GRAD_TOP = (26, 26, 46)
C_BG_GRAD_BOT = (22, 33, 62)
C_WHITE = (255, 255, 255)
C_GOLD = (255, 215, 0)
C_GREEN = (0, 255, 136)
C_RED = (255, 68, 68)
C_PURPLE = (157, 78, 221)
C_DIM = (80, 80, 100)
C_PAPER = (253, 246, 227)
C_INK = (44, 62, 80)
C_HIGHLIGHT = (255, 193, 7)
C_PHONE_BG = (18, 18, 18)
C_NOTIF_BG = (40, 40, 45)

def font(size, bold=True):
    try:
        return ImageFont.truetype(FONT_REG, size, index=1 if bold else 0)
    except:
        return ImageFont.truetype(FONT_REG, size)

def ease_out_cubic(t):
    return 1 - (1 - max(0, min(1, t))) ** 3

def format_money(n):
    if n >= 1000000:
        return f"${n/1000000:.1f}M"
    elif n >= 1000:
        return f"${n/1000:.0f}K"
    return f"${n:.0f}"

def parse_script(path):
    """Parse YAML frontmatter + body from markdown."""
    with open(path, 'r') as f:
        content = f.read()
    parts = re.split(r'^---$', content.strip(), flags=re.MULTILINE)
    meta = {}
    body = content
    if len(parts) >= 3:
        # Simple YAML parse (avoid yaml dependency)
        for line in parts[1].strip().split('\n'):
            if ':' in line:
                k, _, v = line.partition(':')
                meta[k.strip()] = v.strip().strip('"\'')
        body = parts[2].strip()
    return {
        'title': meta.get('title', 'Untitled'),
        'video_type': meta.get('video_type', 'kinetic'),
        'voice': meta.get('voice', 'en-US-AndrewNeural'),
        'speed': float(meta.get('speed', '1.08')),
        'body': body,
        'segments': [s.strip() for s in body.strip().split('\n') if s.strip() and not s.strip().startswith('---')],
    }

async def generate_tts(text, voice, rate_str, output_path):
    comm = edge_tts.Communicate(text, voice, rate=rate_str)
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

def encode_frames(frames_dir, audio_path, output_path, duration):
    cmd = [
        "ffmpeg", "-y", "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%05d.png"),
        "-i", audio_path,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "15", "-preset", "medium",
        "-c:a", "aac", "-b:a", "128k", "-shortest", "-t", str(duration),
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)

def get_segment_timings(boundaries, total_duration):
    """Group boundaries into ~4 segments evenly."""
    if not boundaries:
        return [total_duration / 4, total_duration / 2, total_duration * 0.75, total_duration]
    # Group boundaries into 4 chunks
    n = len(boundaries)
    seg_ends = []
    per_seg = max(1, n // 4)
    for i in range(per_seg, n, per_seg):
        seg_ends.append(boundaries[i]["offset"])
    while len(seg_ends) < 3:
        seg_ends.append(seg_ends[-1] + total_duration * 0.2 if seg_ends else total_duration * 0.25)
    seg_ends.append(total_duration)
    return seg_ends

# === RENDERER: KINETIC TYPOGRAPHY ===
def render_kinetic(segments, audio_path, boundaries, total_duration, output_path, temp_dir):
    frames_dir = temp_dir / "kinetic"
    frames_dir.mkdir(exist_ok=True)
    total_frames = int(total_duration * FPS)
    seg_ends = get_segment_timings(boundaries, total_duration)

    # Extract key phrases per segment (first sentence or first ~8 words)
    seg_texts = []
    for i, seg in enumerate(segments[:4] if len(segments) >= 4 else segments):
        words = seg.split()
        if len(words) <= 6:
            seg_texts.append([seg])
        else:
            # Split into 2 lines
            mid = len(words) // 2
            seg_texts.append([' '.join(words[:mid]), ' '.join(words[mid:])])

    while len(seg_texts) < 4:
        seg_texts.append(["..."])

    colors = [C_GOLD, C_WHITE, C_GREEN, C_RED]

    for i in range(total_frames):
        t = i / FPS
        # Find segment
        seg_idx = min(3, max(0, sum(1 for e in seg_ends if t >= e)))
        seg_start = seg_ends[seg_idx - 1] if seg_idx > 0 else 0
        local_t = t - seg_start

        # Gradient background
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        for y in range(0, HEIGHT, 2):
            ratio = y / HEIGHT
            r = int(C_BG_GRAD_TOP[0] + (C_BG_GRAD_BOT[0] - C_BG_GRAD_TOP[0]) * ratio)
            g = int(C_BG_GRAD_TOP[1] + (C_BG_GRAD_BOT[1] - C_BG_GRAD_TOP[1]) * ratio)
            b = int(C_BG_GRAD_TOP[2] + (C_BG_GRAD_BOT[2] - C_BG_GRAD_TOP[2]) * ratio)
            draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
            draw.line([(0, y+1), (WIDTH, y+1)], fill=(r, g, b))

        lines = seg_texts[seg_idx]
        accent = colors[seg_idx]
        line_spacing = 120
        start_y = HEIGHT // 2 - len(lines) * line_spacing // 2

        for li, line in enumerate(lines):
            line_t = local_t - li * 0.2
            if line_t < 0:
                continue
            anim_dur = 0.3
            if line_t < anim_dur:
                scale = max(0.01, ease_out_cubic(line_t / anim_dur))
            else:
                scale = 1.0 + 0.02 * math.sin((line_t - anim_dur) * 3)
            
            fnt_size = max(1, int(64 * scale))
            fnt = font(fnt_size)
            bbox = draw.textbbox((0, 0), line, font=fnt)
            tw = bbox[2] - bbox[0]
            x = (WIDTH - tw) // 2
            y = start_y + li * line_spacing
            # Shadow
            draw.text((x + 3, y + 3), line, font=fnt, fill=(0, 0, 0))
            col = accent if li == 0 else C_WHITE
            draw.text((x, y), line, font=fnt, fill=col)

        img.save(frames_dir / f"frame_{i+1:05d}.png")
    
    encode_frames(frames_dir, audio_path, output_path, total_duration)

# === RENDERER: DATA VIZ ===
def render_data_viz(segments, audio_path, boundaries, total_duration, output_path, temp_dir):
    frames_dir = temp_dir / "dataviz"
    frames_dir.mkdir(exist_ok=True)
    total_frames = int(total_duration * FPS)
    seg_ends = get_segment_timings(boundaries, total_duration)

    # Try to extract numbers from script for counter animation
    full_text = ' '.join(segments)
    money_matches = re.findall(r'\$[\d,]+(?:\.\d+)?[KMB]?', full_text)
    percent_matches = re.findall(r'(\d+(?:\.\d+)?)\s*%', full_text)
    
    # Parse first money amount as counter target
    counter_target = 50000
    if money_matches:
        m = money_matches[0]
        num_str = re.sub(r'[^\d.]', '', m)
        try:
            base = float(num_str)
            if 'M' in m.upper():
                base *= 1000000
            elif 'K' in m.upper():
                base *= 1000
            elif 'B' in m.upper():
                base *= 1000000000
            counter_target = int(base)
        except:
            pass

    for i in range(total_frames):
        t = i / FPS
        img = Image.new("RGB", (WIDTH, HEIGHT), C_BG_DARK)
        draw = ImageDraw.Draw(img)
        
        # Grid
        for gx in range(0, WIDTH, 60):
            draw.line([(gx, 0), (gx, HEIGHT)], fill=(25, 25, 35))
        for gy in range(0, HEIGHT, 60):
            draw.line([(0, gy), (WIDTH, gy)], fill=(25, 25, 35))

        seg_idx = min(3, max(0, sum(1 for e in seg_ends if t >= e)))
        seg_start = seg_ends[seg_idx - 1] if seg_idx > 0 else 0
        local_t = t - seg_start
        seg_dur = seg_ends[seg_idx] - seg_start

        if seg_idx == 0:
            # Counter animation
            progress = ease_out_cubic(min(1.0, local_t / max(0.1, seg_dur)))
            val = int(counter_target * progress)
            display = format_money(val)
            fnt = font(140)
            bbox = draw.textbbox((0, 0), display, font=fnt)
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw) // 2, HEIGHT // 2 - 100), display, font=fnt, fill=C_GREEN)
            
            # Label from first segment
            label = segments[0][:40] + "..." if len(segments[0]) > 40 else segments[0]
            lfnt = font(32)
            lbbox = draw.textbbox((0, 0), label, font=lfnt)
            ltw = lbbox[2] - lbbox[0]
            draw.text(((WIDTH - ltw) // 2, HEIGHT // 2 + 80), label, font=lfnt, fill=C_DIM)
            
            # Bar
            bar_h = int(250 * progress)
            draw.rounded_rectangle([WIDTH//2 - 40, HEIGHT - 500, WIDTH//2 + 40, HEIGHT - 500 + bar_h], radius=10, fill=C_GREEN)

        elif seg_idx == 1:
            # Transition text
            progress = ease_out_cubic(min(1.0, local_t / max(0.1, seg_dur)))
            text = segments[1] if len(segments) > 1 else "But what if..."
            words = text.split()
            display = ' '.join(words[:6])
            fnt = font(56)
            bbox = draw.textbbox((0, 0), display, font=fnt)
            tw = bbox[2] - bbox[0]
            y_off = int(20 * math.sin(t * 4))
            draw.text(((WIDTH - tw) // 2, HEIGHT // 2 - 50 + y_off), display, font=fnt, fill=C_GOLD)
            
            # Arrow
            arrow_len = int(300 * progress)
            ay = HEIGHT // 2 + 100
            draw.line([(WIDTH//2 - arrow_len//2, ay), (WIDTH//2 + arrow_len//2, ay)], fill=C_GOLD, width=6)
            if progress > 0.7:
                ax = WIDTH//2 + arrow_len//2
                draw.polygon([(ax, ay), (ax-20, ay-15), (ax-20, ay+15)], fill=C_GOLD)

        elif seg_idx == 2:
            # Big result number
            progress = ease_out_cubic(min(1.0, local_t / max(0.1, seg_dur)))
            # Try to get result number from text
            result_target = counter_target * 3  # default
            seg2_text = segments[2] if len(segments) > 2 else ""
            seg2_money = re.findall(r'\$[\d,]+(?:\.\d+)?[KMB]?', seg2_text)
            if seg2_money:
                num_str = re.sub(r'[^\d.]', '', seg2_money[0])
                try:
                    result_target = int(float(num_str))
                    if 'M' in seg2_money[0].upper(): result_target *= 1000000
                    elif 'K' in seg2_money[0].upper(): result_target *= 1000
                except:
                    pass

            val = int(result_target * progress)
            display = format_money(val)
            fnt = font(160)
            bbox = draw.textbbox((0, 0), display, font=fnt)
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw) // 2, HEIGHT // 2 - 100), display, font=fnt, fill=C_GOLD)
            
            # Bar chart comparison
            chart_y = HEIGHT - 500
            bar1_h = 30
            bar2_h = int(220 * progress)
            draw.rounded_rectangle([WIDTH//2 - 160, chart_y + 250 - bar1_h, WIDTH//2 - 60, chart_y + 250], radius=8, fill=C_RED)
            draw.rounded_rectangle([WIDTH//2 + 60, chart_y + 250 - bar2_h, WIDTH//2 + 160, chart_y + 250], radius=8, fill=C_GREEN)
            draw.text((WIDTH//2 - 155, chart_y + 260), "Before", font=font(24), fill=C_RED)
            draw.text((WIDTH//2 + 65, chart_y + 260), "After", font=font(24), fill=C_GREEN)

        else:
            # Punchline
            text = segments[3] if len(segments) > 3 else segments[-1]
            words = text.split()
            lines = []
            cur = []
            for w in words:
                cur.append(w)
                if len(cur) >= 4:
                    lines.append(' '.join(cur))
                    cur = []
            if cur:
                lines.append(' '.join(cur))
            
            for li, line in enumerate(lines[:4]):
                scale = 1.0 + 0.04 * math.sin(t * 4 + li * 0.5)
                fnt = font(int(56 * scale))
                bbox = draw.textbbox((0, 0), line, font=fnt)
                tw = bbox[2] - bbox[0]
                col = C_RED if "not" in line.lower() or "never" in line.lower() or "cost" in line.lower() else C_WHITE
                draw.text(((WIDTH - tw) // 2, HEIGHT // 2 - 120 + li * 80), line, font=fnt, fill=col)

        img.save(frames_dir / f"frame_{i+1:05d}.png")
    
    encode_frames(frames_dir, audio_path, output_path, total_duration)

# === RENDERER: WHITEBOARD ===
def render_whiteboard(segments, audio_path, boundaries, total_duration, output_path, temp_dir):
    frames_dir = temp_dir / "whiteboard"
    frames_dir.mkdir(exist_ok=True)
    total_frames = int(total_duration * FPS)
    seg_ends = get_segment_timings(boundaries, total_duration)

    for i in range(total_frames):
        t = i / FPS
        img = Image.new("RGB", (WIDTH, HEIGHT), C_PAPER)
        draw = ImageDraw.Draw(img)
        
        # Paper dots
        for dy in range(0, HEIGHT, 40):
            for dx in range(0, WIDTH, 40):
                draw.ellipse([dx, dy, dx+2, dy+2], fill=(240, 233, 215))

        seg_idx = min(3, max(0, sum(1 for e in seg_ends if t >= e)))
        seg_start = seg_ends[seg_idx - 1] if seg_idx > 0 else 0
        local_t = t - seg_start

        # Title
        draw.text((80, 100), "MONEY FACTS", font=font(44), fill=C_INK)
        for ux in range(80, 350, 5):
            uy = 165 + int(3 * math.sin(ux * 0.1))
            draw.line([(ux, uy), (ux+5, uy)], fill=C_INK, width=3)

        if seg_idx == 0 and segments:
            text = segments[0]
            words = text.split()
            display = ' '.join(words[:5])
            fnt = font(90)
            bbox = draw.textbbox((0, 0), display, font=fnt)
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw) // 2, 400), display, font=fnt, fill=C_INK)
            
            # Circle drawing animation
            progress = ease_out_cubic(min(1.0, local_t / max(0.5, seg_ends[0])))
            steps = int(60 * progress)
            prev = None
            for s in range(steps):
                a = (s / 60) * 2 * math.pi
                px = WIDTH // 2 + int(250 * math.cos(a - math.pi/2))
                py = 480 + int(120 * math.sin(a - math.pi/2))
                if prev:
                    draw.line([prev, (px, py)], fill=C_RED, width=5)
                prev = (px, py)
            
            rest = ' '.join(words[5:8]) if len(words) > 5 else ""
            if rest:
                draw.text(((WIDTH - 300) // 2, 600), rest, font=font(34), fill=C_INK)

        elif seg_idx == 1 and len(segments) > 1:
            text = segments[1]
            words = text.split()
            for wi, word in enumerate(words[:4]):
                fnt = font(70)
                bbox = draw.textbbox((0, 0), word, font=fnt)
                tw = bbox[2] - bbox[0]
                draw.text(((WIDTH - tw) // 2, 400 + wi * 90), word, font=fnt, fill=C_HIGHLIGHT if wi == 0 else C_INK)
            
            # Arrow
            for ax in range(300, 780, 8):
                ay = 850 + int(5 * math.sin(ax * 0.05))
                draw.line([(ax, ay), (ax+8, ay)], fill=C_INK, width=4)
            draw.polygon([(780, 850), (750, 830), (755, 870)], fill=C_INK)

        elif seg_idx == 2 and len(segments) > 2:
            text = segments[2]
            money = re.findall(r'\$[\d,]+(?:\.\d+)?[KMB]?', text)
            display = money[0] if money else text[:20]
            fnt = font(120)
            bbox = draw.textbbox((0, 0), display, font=fnt)
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw) // 2, 450), display, font=fnt, fill=C_RED)
            
            # Highlight box
            progress = ease_out_cubic(min(1.0, local_t / 0.5))
            bw = int(tw + 80)
            bh = 160
            bx = (WIDTH - bw) // 2
            for cx in range(int(bw * progress)):
                draw.line([(bx + cx, 440), (bx + cx, 440 + bh)], fill=(255, 235, 130))

            rest_words = text.split()
            rest = ' '.join(rest_words[1:4]) if len(rest_words) > 1 else "in 30 years!"
            draw.text(((WIDTH - 300) // 2, 650), rest, font=font(36), fill=C_INK)

        else:
            text = segments[3] if len(segments) > 3 else segments[-1]
            words = text.split()
            for wi, word in enumerate(words[:5]):
                col = C_RED if any(x in word.lower() for x in ['cost', 'lost', 'waste', 'trash']) else C_INK
                fnt = font(60)
                bbox = draw.textbbox((0, 0), word, font=fnt)
                tw = bbox[2] - bbox[0]
                draw.text(((WIDTH - tw) // 2, 400 + wi * 80), word, font=fnt, fill=col)
            
            # Sad face
            fcx, fcy = WIDTH // 2, 1100
            draw.ellipse([fcx-70, fcy-70, fcx+70, fcy+70], outline=C_INK, width=4)
            draw.ellipse([fcx-30, fcy-25, fcx-10, fcy-5], fill=C_INK)
            draw.ellipse([fcx+10, fcy-25, fcx+30, fcy-5], fill=C_INK)
            draw.arc([fcx-35, fcy+15, fcx+35, fcy+55], 0, 180, fill=C_INK, width=4)

        img.save(frames_dir / f"frame_{i+1:05d}.png")
    
    encode_frames(frames_dir, audio_path, output_path, total_duration)

# === RENDERER: MEME/NOTIFICATION ===
def render_meme(segments, audio_path, boundaries, total_duration, output_path, temp_dir):
    frames_dir = temp_dir / "meme"
    frames_dir.mkdir(exist_ok=True)
    total_frames = int(total_duration * FPS)
    seg_ends = get_segment_timings(boundaries, total_duration)

    # Extract money from script for notification
    full_text = ' '.join(segments)
    money_matches = re.findall(r'\$[\d,]+(?:\.\d+)?[KMB]?', full_text)
    notif_amount = money_matches[0] if money_matches else "$1,500"

    for i in range(total_frames):
        t = i / FPS
        img = Image.new("RGB", (WIDTH, HEIGHT), C_PHONE_BG)
        draw = ImageDraw.Draw(img)
        
        # Status bar
        draw.rectangle([0, 0, WIDTH, 80], fill=(30, 30, 30))
        draw.text((40, 25), "9:41", font=font(28), fill=C_WHITE)
        draw.rounded_rectangle([WIDTH-100, 30, WIDTH-40, 55], radius=4, outline=C_DIM, width=2)
        draw.rectangle([WIDTH-95, 35, WIDTH-70, 50], fill=C_GREEN)

        seg_idx = min(3, max(0, sum(1 for e in seg_ends if t >= e)))
        seg_start = seg_ends[seg_idx - 1] if seg_idx > 0 else 0
        local_t = t - seg_start

        if seg_idx == 0:
            # Notification slide-in
            progress = ease_out_cubic(min(1.0, local_t / max(0.3, seg_ends[0])))
            slide_y = int(-300 + 380 * progress)
            
            draw.rounded_rectangle([40, slide_y, WIDTH-40, slide_y+280], radius=24, fill=C_NOTIF_BG)
            draw.rounded_rectangle([70, slide_y+25, 130, slide_y+85], radius=12, fill=(111, 68, 42))
            draw.text((78, slide_y+30), "\u2615", font=font(36))
            draw.text((155, slide_y+25), "TRANSACTION", font=font(26), fill=C_DIM)
            draw.text((155, slide_y+55), "just now", font=font(22), fill=C_DIM)
            
            draw.text((70, slide_y+110), f"You spent {notif_amount}", font=font(42), fill=C_WHITE)
            
            desc = segments[0][:30] if segments else "on coffee"
            draw.text((70, slide_y+165), desc, font=font(30), fill=C_DIM)
            
            draw.rounded_rectangle([70, slide_y+210, WIDTH-70, slide_y+255], radius=8, fill=(60, 30, 30))
            draw.text((90, slide_y+215), f"\U0001F4B8 That's {notif_amount}/year!", font=font(28), fill=C_RED)

        elif seg_idx == 1:
            # Calculator/investment mockup
            draw.text((WIDTH//2 - 200, 150), "\U0001F9EE Investment Math", font=font(40), fill=C_WHITE)
            draw.rounded_rectangle([60, 250, WIDTH-60, 400], radius=16, fill=(30, 30, 35))
            
            calc_text = segments[1][:30] if len(segments) > 1 else "invested instead..."
            draw.text((100, 290), calc_text, font=font(36), fill=C_DIM)
            draw.text((100, 340), "= ???", font=font(44), fill=C_GOLD)
            
            # Buttons
            btn_labels = ["7","8","9","4","5","6","1","2","3","0",".","="]
            btn_size = 140
            for bi, label in enumerate(btn_labels):
                col = bi % 3
                row = bi // 3
                bx = 80 + col * (btn_size + 20)
                by = 450 + row * (btn_size + 20)
                color = (50,50,55) if label != "=" else C_GOLD
                txt_color = C_WHITE if label != "=" else (18,18,18)
                draw.rounded_rectangle([bx, by, bx+btn_size, by+btn_size], radius=20, fill=color)
                bbox = draw.textbbox((0,0), label, font=font(48))
                tw = bbox[2] - bbox[0]
                draw.text((bx + (btn_size-tw)//2, by+40), label, font=font(48), fill=txt_color)

        elif seg_idx == 2:
            # Result counter
            progress = ease_out_cubic(min(1.0, local_t / max(0.1, seg_ends[2] - seg_start)))
            
            # Get result amount
            seg2_text = segments[2] if len(segments) > 2 else ""
            seg2_money = re.findall(r'\$[\d,]+(?:\.\d+)?[KMB]?', seg2_text)
            result_str = seg2_money[0] if seg2_money else "$170,000"
            num_str = re.sub(r'[^\d.]', '', result_str)
            try:
                base = float(num_str)
                if 'M' in result_str.upper(): base *= 1000000
                elif 'K' in result_str.upper(): base *= 1000
            except:
                base = 170000
            val = int(base * progress)
            display = f"${val:,}"
            
            fnt = font(100)
            bbox = draw.textbbox((0,0), display, font=fnt)
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH-tw)//2, 400), display, font=fnt, fill=C_GREEN)
            
            desc = segments[2][:30] if len(segments) > 2 else "from your savings!"
            draw.text((WIDTH//2 - 200, 540), desc, font=font(32), fill=C_DIM)
            
            # Celebration
            escale = min(1.0, progress * 2)
            draw.text((WIDTH//2 - 60, 650), "\U0001F389", font=font(int(120*escale)))
            
            # Bank notification
            ny = 850 + int(20 * math.sin(t * 4))
            draw.rounded_rectangle([40, ny, WIDTH-40, ny+120], radius=20, fill=C_NOTIF_BG)
            draw.text((70, ny+20), "\U0001F3E6 Balance grew", font=font(30), fill=C_GREEN)
            draw.text((70, ny+60), f"+{display}", font=font(42), fill=C_GREEN)

        else:
            # Meme punchline
            shake = int(5 * math.sin(t * 15))
            text = segments[3] if len(segments) > 3 else segments[-1]
            words = text.split()
            
            draw.text((WIDTH//2 - 250 + shake, 400), ' '.join(words[:3]), font=font(44), fill=C_WHITE)
            if len(words) > 3:
                draw.text((WIDTH//2 - 250 + shake, 470), ' '.join(words[3:6]), font=font(44), fill=C_RED)
            if len(words) > 6:
                draw.text((WIDTH//2 - 250 + shake, 580), ' '.join(words[6:9]), font=font(50), fill=C_RED)
            
            draw.text((WIDTH//2 - 50 + shake, 700), "\U0001F62D", font=font(120))
            
            draw.rounded_rectangle([40, HEIGHT-200, WIDTH-40, HEIGHT-80], radius=16, fill=C_NOTIF_BG)
            pov_text = segments[0][:40] if segments else "POV: You're broke"
            draw.text((70, HEIGHT-180), f"POV: {pov_text}", font=font(30), fill=C_DIM)

        img.save(frames_dir / f"frame_{i+1:05d}.png")
    
    encode_frames(frames_dir, audio_path, output_path, total_duration)

# === RENDERER DISPATCH ===
RENDERERS = {
    'kinetic': render_kinetic,
    'data_viz': render_data_viz,
    'whiteboard': render_whiteboard,
    'meme': render_meme,
}

# === MAIN ===
async def main():
    parser = argparse.ArgumentParser(description="Multi-format video renderer")
    parser.add_argument("script", help="Path to script YAML file")
    parser.add_argument("--type", choices=list(RENDERERS.keys()), required=True, help="Video type")
    parser.add_argument("--output", default="output/", help="Output directory")
    args = parser.parse_args()

    script_data = parse_script(args.script)
    title = script_data['title']
    video_type = args.type
    voice = script_data['voice']
    rate = f"+{int((script_data['speed'] - 1) * 100)}%"
    segments = script_data['segments']
    full_text = ' '.join(segments)

    print(f"[+] Title: {title}")
    print(f"[+] Type: {video_type}")
    print(f"[+] Segments: {len(segments)}")

    # Generate TTS
    temp_dir = Path(tempfile.mkdtemp(prefix=f"render_{video_type}_"))
    audio_path = str(temp_dir / "tts.mp3")
    print(f"[+] Generating TTS ({voice}, {rate})...")
    boundaries, total_duration = await generate_tts(full_text, voice, rate, audio_path)
    print(f"[+] TTS: {total_duration:.1f}s, {len(boundaries)} boundaries")

    # Render
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_title = re.sub(r'[^a-zA-Z0-9]', '_', title)[:50]
    output_path = str(output_dir / f"{safe_title}_{video_type}.mp4")

    print(f"[+] Rendering {video_type}...")
    render_fn = RENDERERS[video_type]
    render_fn(segments, audio_path, boundaries, total_duration, output_path, temp_dir)

    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"[+] Output: {output_path} ({size_mb:.1f}MB)")
    print(f"[+] SUCCESS")

    shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    asyncio.run(main())
