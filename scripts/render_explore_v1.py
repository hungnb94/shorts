#!/usr/bin/env python3
"""
Random Exploration Renderer — 6 variants, 1 video each.

Action space: 7 video types × 3 hook types × 9 value-adds.
Random select (seed=42), exclude failed E-leadership variant.
Uses existing renderers: demo_all_types.py (animation), render_clip.py (clip curation).

Pipeline per variant:
  1. Pick content segment from source transcript (random)
  2. Generate TTS commentary (edge_tts, en-US-AndrewNeural)
  3. Render base video by type (kinetic_typography, data_viz, whiteboard, etc.)
  4. Composite value-add overlays
  5. Output 1080x1920 H264+AAC, <60s
"""
import json, subprocess, sys, os, math, random, tempfile, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edge_tts

PROJECT = Path("/Users/hung/code/ai/shorts")
OUTDIR = PROJECT / "output" / "explore_v1"
OUTDIR.mkdir(parents=True, exist_ok=True)
TMPDIR = PROJECT / "output" / "tmp_explore"
TMPDIR.mkdir(parents=True, exist_ok=True)
OVERLAYS = PROJECT / "output" / "overlays"

WIDTH, HEIGHT, FPS = 1080, 1920, 30
FONT_BOLD = "/System/Library/Fonts/Helvetica.ttc"
VOICE = "en-US-AndrewNeural"
RATE = "+8%"

# Colors
C_WHITE = (255, 255, 255)
C_GOLD = (255, 215, 0)
C_GREEN = (0, 255, 136)
C_RED = (255, 68, 68)
C_CYAN = (0, 229, 255)
C_PURPLE = (157, 78, 221)
C_BLACK = (15, 15, 23)
C_DARK_BG = (26, 26, 46)

def font(size, bold=True):
    size = max(1, int(size))
    try:
        return ImageFont.truetype(FONT_BOLD, size, index=1 if bold else 0)
    except:
        return ImageFont.truetype(FONT_BOLD, size)

# ── Content segments from billionaire transcript ──
# Curated viral moments, 15-40s each, sentence-boundary snapped
CONTENT_SEGMENTS = [
    {
        "id": "discipline_bank",
        "start": 293, "end": 318,
        "text": "Discipline is a bank account. Every time you do something you said you were going to do, you make a deposit. Every time you don't, you make a withdrawal. If your balance is zero, you're broke.",
        "hook": "DISCIPLINE IS A BANK ACCOUNT",
        "hook_type_bytes": b"\xe2\x9d\x8c",
        "punchlines": {"discipline", "bank", "account", "deposits", "withdrawals", "broke"},
    },
    {
        "id": "fire_people",
        "start": 142, "end": 169,
        "text": "If you don't fire them, you are holding them back from what they could be great at. You are keeping them in a place where they are trash. That is the meanest thing you can do to somebody.",
        "hook": "FIRING PEOPLE IS KIND",
        "punchlines": {"fire", "holding", "back", "great", "trash", "meanest"},
    },
    {
        "id": "12k_to_billion",
        "start": 332, "end": 365,
        "text": "Started with $12,000. First day we made $7. For 10 years we made $695 a month. Most people would've quit. But we didn't. And then it became a billion dollar company.",
        "hook": "FROM $12K TO BILLIONAIRE",
        "punchlines": {"$12", "$7", "$695", "month", "10", "years", "billion"},
    },
    {
        "id": "bugatti_garage",
        "start": 981, "end": 997,
        "text": "This is the Bugatti. He made enough money in one month to buy this car. How? By building systems that work without him.",
        "hook": "HE BOUGHT A BUGATTI IN ONE MONTH",
        "punchlines": {"Bugatti", "month", "money", "systems"},
    },
    {
        "id": "rejection_empire",
        "start": 483, "end": 514,
        "text": "They told him no. Every single person told him no. That rejection forced him to build something vertical. And in 2012, it became an empire.",
        "hook": "REJECTION BUILT HIS EMPIRE",
        "punchlines": {"no", "rejection", "forced", "vertical", "2012", "empire"},
    },
    {
        "id": "fitness_success",
        "start": 233, "end": 276,
        "text": "Have you seen the correlation between fitness and financial success? Absolutely. Huge correlation. Because the same discipline it takes to show up at 5 AM is the same discipline it takes to show up for your business.",
        "hook": "FITNESS EQUALS FINANCIAL SUCCESS",
        "punchlines": {"fitness", "financial", "success", "correlation", "huge", "discipline", "5"},
    },
]


# ── Hook patterns ──
def get_hook_text(hook_type, content):
    """Generate hook text based on hook type."""
    if hook_type == "context":
        # Context: states a fact, no spin
        return content["hook"]
    elif hook_type == "contrarian":
        # Contrarian: challenges conventional wisdom
        contrarian_map = {
            "DISCIPLINE IS A BANK ACCOUNT": "MOTIVATION IS A LIE. DISCIPLINE WINS.",
            "FIRING PEOPLE IS KIND": "NOT FIRING THEM IS CRUEL.",
            "FROM $12K TO BILLIONAIRE": "10 YEARS OF BROKE MADE HIM RICH.",
            "HE BOUGHT A BUGATTI IN ONE MONTH": "YOU CAN'T AFFORD A BUGATTI. HE CAN.",
            "REJECTION BUILT HIS EMPIRE": "EVERY 'NO' MADE HIM RICHER.",
            "FITNESS EQUALS FINANCIAL SUCCESS": "LAZY BODY = LAZY WALLET.",
        }
        return contrarian_map.get(content["hook"], content["hook"])
    else:  # intrigue
        # Intrigue: raises question
        intrigue_map = {
            "DISCIPLINE IS A BANK ACCOUNT": "WHY DISCIPLINE = MONEY IN THE BANK?",
            "FIRING PEOPLE IS KIND": "WHY FIRING SOMEONE IS THE KINDEST THING?",
            "FROM $12K TO BILLIONAIRE": "HOW DO YOU TURN $12K INTO A BILLION?",
            "HE BOUGHT A BUGATTI IN ONE MONTH": "WHAT BUYS A BUGATTI IN ONE MONTH?",
            "REJECTION BUILT HIS EMPIRE": "WHAT HAPPENS WHEN EVERYONE SAYS NO?",
            "FITNESS EQUALS FINANCIAL SUCCESS": "CAN GYM TIME EQUAL INCOME TIME?",
        }
        return intrigue_map.get(content["hook"], content["hook"])


# ── TTS ──
async def gen_tts(text, out_path, rate=RATE):
    """Generate TTS audio + collect word boundaries."""
    comm = edge_tts.Communicate(text, VOICE, rate=rate)
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
    with open(out_path, "wb") as f:
        f.write(audio_data)
    
    # Get duration
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", out_path],
        capture_output=True, text=True
    )
    duration = float(json.loads(result.stdout)["format"]["duration"])
    return duration, boundaries


# ── Value-add overlay renderers ──
def draw_fact_check_callout(frame, t, seg_start, seg_end, draw):
    """FACT: badge with text, appears at 30% through segment."""
    progress = (t - seg_start) / max(0.1, seg_end - seg_start)
    if 0.25 <= progress <= 0.55:
        # Badge
        draw.rounded_rectangle([50, 1400, 500, 1480], radius=10, fill=(0, 100, 200, 220))
        draw.text((70, 1410), "FACT CHECK", font=font(28), fill=C_WHITE)
        # Text below
        draw.text((50, 1500), "Source verified", font=font(24), fill=(200, 200, 200))


def draw_data_viz_overlay(frame, t, seg_start, seg_end, draw):
    """Counter animation showing a number."""
    progress = (t - seg_start) / max(0.1, seg_end - seg_start)
    if 0.2 <= progress <= 0.6:
        # Big number counter
        val = int(450 * min(1.0, (progress - 0.2) / 0.3))
        text = f"${val}B"
        draw.text((WIDTH // 2 - 100, 400), text, font=font(100), fill=C_GREEN)


def draw_counter_argument(frame, t, seg_start, seg_end, draw):
    """BUT... callout challenging the statement."""
    progress = (t - seg_start) / max(0.1, seg_end - seg_start)
    if 0.35 <= progress <= 0.65:
        # Red background
        draw.rounded_rectangle([50, 1400, 1030, 1520], radius=15, fill=(200, 50, 50, 200))
        draw.text((100, 1420), "BUT HERE'S THE TRUTH:", font=font(36), fill=C_WHITE)


def draw_source_citation(frame, t, seg_start, seg_end, draw):
    """SOURCE: badge with attribution."""
    progress = (t - seg_start) / max(0.1, seg_end - seg_start)
    if 0.3 <= progress <= 0.6:
        draw.rounded_rectangle([50, 1750, 400, 1820], radius=8, fill=(40, 40, 60, 220))
        draw.text((70, 1760), "SOURCE: Andy Frisella", font=font(24), fill=(180, 180, 200))


def draw_animated_annotation(frame, t, seg_start, seg_end, draw):
    """Arrow + label annotation."""
    progress = (t - seg_start) / max(0.1, seg_end - seg_start)
    if 0.2 <= progress <= 0.5:
        # Animated arrow pointing
        arrow_x = int(800 + 100 * math.sin(t * 5))
        draw.line([(arrow_x, 600), (arrow_x + 80, 600)], fill=C_GOLD, width=6)
        draw.polygon([(arrow_x + 80, 600), (arrow_x + 65, 590), (arrow_x + 65, 610)], fill=C_GOLD)
        draw.text((arrow_x + 90, 580), "KEY POINT", font=font(24), fill=C_GOLD)


def draw_this_or_that(frame, t, seg_start, seg_end, draw):
    """A vs B binary choice overlay."""
    progress = (t - seg_start) / max(0.1, seg_end - seg_start)
    if 0.25 <= progress <= 0.55:
        # Split screen visual
        mid_x = WIDTH // 2
        draw.line([(mid_x, 1400), (mid_x, 1550)], fill=C_CYAN, width=4)
        draw.text((150, 1420), "A: QUIT", font=font(40), fill=C_RED)
        draw.text((600, 1420), "B: PUSH", font=font(40), fill=C_GREEN)


def draw_split_screen(frame, t, seg_start, seg_end, draw):
    """Two-panel comparison."""
    progress = (t - seg_start) / max(0.1, seg_end - seg_start)
    if 0.2 <= progress <= 0.6:
        # Left panel: POOR MINDSET
        draw.rectangle([0, 1350, 530, 1550], fill=(60, 20, 20, 180))
        draw.text((100, 1400), "POOR", font=font(40), fill=C_RED)
        # Right panel: RICH MINDSET
        draw.rectangle([550, 1350, 1080, 1550], fill=(20, 60, 20, 180))
        draw.text((700, 1400), "RICH", font=font(40), fill=C_GREEN)


def draw_timeline_overlay(frame, t, seg_start, seg_end, draw):
    """Milestone timeline bar."""
    progress = (t - seg_start) / max(0.1, seg_end - seg_start)
    if 0.15 <= progress <= 0.7:
        # Timeline bar
        bar_y = 1400
        bar_w = 800
        bar_x = (WIDTH - bar_w) // 2
        # Background bar
        draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + 20], radius=10, fill=(40, 40, 60))
        # Progress fill
        fill_w = int(bar_w * progress)
        draw.rounded_rectangle([bar_x, bar_y, bar_x + fill_w, bar_y + 20], radius=10, fill=C_GOLD)
        # Milestones
        for i, label in enumerate(["Day 1", "Year 5", "Year 10", "$1B"]):
            mx = bar_x + int(bar_w * i / 3)
            draw.ellipse([mx - 8, bar_y - 4, mx + 8, bar_y + 24], fill=C_GOLD)
            draw.text((mx - 30, bar_y + 30), label, font=font(20), fill=C_WHITE)


VALUE_ADD_RENDERERS = {
    "fact_check_callout": draw_fact_check_callout,
    "data_viz_overlay": draw_data_viz_overlay,
    "counter_argument": draw_counter_argument,
    "source_citation": draw_source_citation,
    "animated_annotation": draw_animated_annotation,
    "this_or_that_overlay": draw_this_or_that,
    "split_screen_comparison": draw_split_screen,
    "timeline_overlay": draw_timeline_overlay,
}


# ── Video type renderers ──
def render_kinetic_typography(content, hook_text, audio_path, duration, boundaries, value_adds, output_path):
    """Type 2: Pure text animation on dark gradient. High energy."""
    frames_dir = TMPDIR / f"{content['id']}_kinetic"
    frames_dir.mkdir(exist_ok=True)
    total_frames = int(duration * FPS)
    
    for i in range(total_frames):
        t = i / FPS
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        # Gradient background
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(C_DARK_BG[0] + (22 - C_DARK_BG[0]) * ratio)
            g = int(C_DARK_BG[1] + (33 - C_DARK_BG[1]) * ratio)
            b = int(C_DARK_BG[2] + (62 - C_DARK_BG[2]) * ratio)
            draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
        
        # Hook text (first 3s)
        if t < 3.0:
            scale = min(1.0, t / 0.3) if t < 0.3 else 1.0 + 0.03 * math.sin((t - 0.3) * 4)
            fnt = font(int(80 * scale))
            bbox = draw.textbbox((0, 0), hook_text, font=fnt)
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw) // 2, 300), hook_text, font=fnt, fill=C_GOLD)
        else:
            # Body text from boundaries
            for b in boundaries:
                if b["offset"] <= t <= b["offset"] + b["duration"]:
                    text = b["text"]
                    words = text.split()
                    for wi, word in enumerate(words):
                        wt = b["offset"] + wi * (b["duration"] / max(len(words), 1))
                        if wt <= t <= wt + 0.5:
                            scale = min(1.0, (t - wt) / 0.15) if t - wt < 0.15 else 1.0
                            fnt = font(int(60 * scale))
                            is_punch = word.lower().strip(".,!?\"'") in content["punchlines"]
                            color = C_CYAN if is_punch else C_WHITE
                            y_pos = 800 + wi * 80
                            bbox = draw.textbbox((0, 0), word, font=fnt)
                            tw = bbox[2] - bbox[0]
                            draw.text(((WIDTH - tw) // 2, y_pos), word, font=fnt, fill=color)
                    break
        
        # Value-adds
        for va in value_adds:
            renderer = VALUE_ADD_RENDERERS.get(va)
            if renderer:
                renderer(img, t, 3.0, duration, draw)
        
        # Progress bar
        bar_w = int(WIDTH * t / duration)
        draw.rectangle([0, HEIGHT - 10, bar_w, HEIGHT], fill=C_CYAN)
        
        img.save(frames_dir / f"frame_{i+1:05d}.png")
    
    encode_frames(frames_dir, audio_path, output_path, duration)


def render_data_viz(content, hook_text, audio_path, duration, boundaries, value_adds, output_path):
    """Type 3: Counter animations, bar charts. Numbers are the hero."""
    frames_dir = TMPDIR / f"{content['id']}_dataviz"
    frames_dir.mkdir(exist_ok=True)
    total_frames = int(duration * FPS)
    
    for i in range(total_frames):
        t = i / FPS
        img = Image.new("RGB", (WIDTH, HEIGHT), C_BLACK)
        draw = ImageDraw.Draw(img)
        
        # Grid background
        for gx in range(0, WIDTH, 60):
            draw.line([(gx, 0), (gx, HEIGHT)], fill=(25, 25, 35), width=1)
        for gy in range(0, HEIGHT, 60):
            draw.line([(0, gy), (WIDTH, gy)], fill=(25, 25, 35), width=1)
        
        # Hook (first 3s)
        if t < 3.0:
            scale = min(1.0, t / 0.3) if t < 0.3 else 1.0
            fnt = font(int(70 * scale))
            bbox = draw.textbbox((0, 0), hook_text, font=fnt)
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw) // 2, 200), hook_text, font=fnt, fill=C_GREEN)
        
        # Animated counter (main visual)
        counter_val = int(t * 100)
        text = f"${counter_val}"
        fnt = font(140)
        bbox = draw.textbbox((0, 0), text, font=fnt)
        tw = bbox[2] - bbox[0]
        draw.text(((WIDTH - tw) // 2, 600), text, font=fnt, fill=C_GOLD)
        
        # Bar chart
        bar_h = int(200 * (t / duration))
        draw.rounded_rectangle([WIDTH // 2 - 100, HEIGHT - 400 - bar_h, WIDTH // 2 + 100, HEIGHT - 400], radius=15, fill=C_GREEN)
        
        # Value-adds
        for va in value_adds:
            renderer = VALUE_ADD_RENDERERS.get(va)
            if renderer:
                renderer(img, t, 3.0, duration, draw)
        
        # Progress bar
        bar_w = int(WIDTH * t / duration)
        draw.rectangle([0, HEIGHT - 10, bar_w, HEIGHT], fill=C_CYAN)
        
        img.save(frames_dir / f"frame_{i+1:05d}.png")
    
    encode_frames(frames_dir, audio_path, output_path, duration)


def render_whiteboard(content, hook_text, audio_path, duration, boundaries, value_adds, output_path):
    """Type 5: Hand-drawn educational style. Cream background."""
    frames_dir = TMPDIR / f"{content['id']}_whiteboard"
    frames_dir.mkdir(exist_ok=True)
    total_frames = int(duration * FPS)
    
    BG = (253, 246, 227)
    INK = (44, 62, 80)
    HIGHLIGHT = (255, 193, 7)
    
    for i in range(total_frames):
        t = i / FPS
        img = Image.new("RGB", (WIDTH, HEIGHT), BG)
        draw = ImageDraw.Draw(img)
        
        # Hook (first 3s)
        if t < 3.0:
            scale = min(1.0, t / 0.5)
            fnt = font(int(60 * scale))
            bbox = draw.textbbox((0, 0), hook_text, font=fnt)
            tw = bbox[2] - bbox[0]
            # Highlight behind text
            draw.rectangle([(WIDTH - tw) // 2 - 20, 250, (WIDTH + tw) // 2 + 20, 330], fill=HIGHLIGHT)
            draw.text(((WIDTH - tw) // 2, 260), hook_text, font=fnt, fill=INK)
        
        # Body text (handwritten style)
        for b in boundaries:
            if b["offset"] <= t <= b["offset"] + b["duration"]:
                text = b["text"]
                # Simulate handwriting: draw word by word
                words = text.split()
                for wi, word in enumerate(words):
                    wt = b["offset"] + wi * (b["duration"] / max(len(words), 1))
                    if wt <= t:
                        is_punch = word.lower().strip(".,!?\"'") in content["punchlines"]
                        color = C_RED if is_punch else INK
                        fnt = font(50 if is_punch else 44)
                        y_pos = 700 + (wi % 6) * 70
                        x_pos = 100 + (wi // 6) * 0
                        draw.text((x_pos, y_pos), word, font=fnt, fill=color)
                break
        
        # Value-adds
        for va in value_adds:
            renderer = VALUE_ADD_RENDERERS.get(va)
            if renderer:
                renderer(img, t, 3.0, duration, draw)
        
        # Progress bar
        bar_w = int(WIDTH * t / duration)
        draw.rectangle([0, HEIGHT - 10, bar_w, HEIGHT], fill=INK)
        
        img.save(frames_dir / f"frame_{i+1:05d}.png")
    
    encode_frames(frames_dir, audio_path, output_path, duration)


def render_meme_notification(content, hook_text, audio_path, duration, boundaries, value_adds, output_path):
    """Type 6: Meme/notification style. Fast cuts, bold text."""
    frames_dir = TMPDIR / f"{content['id']}_meme"
    frames_dir.mkdir(exist_ok=True)
    total_frames = int(duration * FPS)
    
    for i in range(total_frames):
        t = i / FPS
        img = Image.new("RGB", (WIDTH, HEIGHT), C_BLACK)
        draw = ImageDraw.Draw(img)
        
        # Alternating background every 3s (pattern interrupt)
        bg_color = C_DARK_BG if int(t / 3) % 2 == 0 else (46, 20, 60)
        img.paste(bg_color, [0, 0, WIDTH, HEIGHT])
        draw = ImageDraw.Draw(img)
        
        # Hook (first 3s) — big impact
        if t < 3.0:
            scale = min(1.0, t / 0.2) if t < 0.2 else 1.0 + 0.05 * math.sin((t - 0.2) * 8)
            fnt = font(int(90 * scale))
            bbox = draw.textbbox((0, 0), hook_text, font=fnt)
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw) // 2, 400), hook_text, font=fnt, fill=C_CYAN)
        
        # Big text words throughout
        for b in boundaries:
            if b["offset"] <= t <= b["offset"] + b["duration"]:
                words = b["text"].split()
                for wi, word in enumerate(words):
                    wt = b["offset"] + wi * (b["duration"] / max(len(words), 1))
                    if wt <= t <= wt + 0.4:
                        is_punch = word.lower().strip(".,!?\"'") in content["punchlines"]
                        size = 80 if is_punch else 60
                        color = C_GOLD if is_punch else C_WHITE
                        scale = min(1.0, (t - wt) / 0.1) if t - wt < 0.1 else 1.0
                        fnt = font(int(size * scale))
                        bbox = draw.textbbox((0, 0), word, font=fnt)
                        tw = bbox[2] - bbox[0]
                        y_pos = 800 + (wi % 3) * 100
                        draw.text(((WIDTH - tw) // 2, y_pos), word, font=fnt, fill=color)
                break
        
        # Value-adds
        for va in value_adds:
            renderer = VALUE_ADD_RENDERERS.get(va)
            if renderer:
                renderer(img, t, 3.0, duration, draw)
        
        # Progress bar
        bar_w = int(WIDTH * t / duration)
        draw.rectangle([0, HEIGHT - 10, bar_w, HEIGHT], fill=C_CYAN)
        
        img.save(frames_dir / f"frame_{i+1:05d}.png")
    
    encode_frames(frames_dir, audio_path, output_path, duration)


def render_stock_footage(content, hook_text, audio_path, duration, boundaries, value_adds, output_path):
    """Type 1: Stock footage style — using source video frames as background."""
    frames_dir = TMPDIR / f"{content['id']}_stock"
    frames_dir.mkdir(exist_ok=True)
    total_frames = int(duration * FPS)
    
    # Extract source frames
    source = PROJECT / "output/source/2eicF3iPf1s.webm"
    source_frames = TMPDIR / f"{content['id']}_src"
    source_frames.mkdir(exist_ok=True)
    
    # Extract 1 frame per second from source segment
    seg_start = content["start"]
    seg_end = content["end"]
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(seg_start), "-i", str(source),
        "-t", str(seg_end - seg_start),
        "-vf", f"fps=1,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-q:v", "2", str(source_frames / "src_%03d.jpg")
    ], capture_output=True)
    
    src_files = sorted(source_frames.glob("src_*.jpg"))
    
    for i in range(total_frames):
        t = i / FPS
        # Use source frame as background
        if src_files:
            frame_idx = min(int(t), len(src_files) - 1)
            bg = Image.open(src_files[frame_idx]).resize((WIDTH, HEIGHT))
        else:
            bg = Image.new("RGB", (WIDTH, HEIGHT), C_BLACK)
        
        # Darken
        overlay = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        bg = Image.blend(bg, overlay, 0.4)
        draw = ImageDraw.Draw(bg)
        
        # Hook (first 3s)
        if t < 3.0:
            scale = min(1.0, t / 0.3)
            fnt = font(int(70 * scale))
            bbox = draw.textbbox((0, 0), hook_text, font=fnt)
            tw = bbox[2] - bbox[0]
            # Black box behind text
            draw.rectangle([(WIDTH - tw) // 2 - 20, 200, (WIDTH + tw) // 2 + 20, 290], fill=(0, 0, 0))
            draw.text(((WIDTH - tw) // 2, 210), hook_text, font=fnt, fill=C_GOLD)
        
        # Body text
        for b in boundaries:
            if b["offset"] <= t <= b["offset"] + b["duration"]:
                words = b["text"].split()
                for wi, word in enumerate(words):
                    wt = b["offset"] + wi * (b["duration"] / max(len(words), 1))
                    if wt <= t <= wt + 0.5:
                        is_punch = word.lower().strip(".,!?\"'") in content["punchlines"]
                        size = 60 if is_punch else 48
                        color = C_CYAN if is_punch else C_WHITE
                        fnt = font(size)
                        bbox = draw.textbbox((0, 0), word, font=fnt)
                        tw = bbox[2] - bbox[0]
                        y_pos = 800 + (wi % 5) * 75
                        draw.text(((WIDTH - tw) // 2, y_pos), word, font=fnt, fill=color)
                break
        
        # Value-adds
        for va in value_adds:
            renderer = VALUE_ADD_RENDERERS.get(va)
            if renderer:
                renderer(bg, t, 3.0, duration, draw)
        
        # Progress bar
        bar_w = int(WIDTH * t / duration)
        draw.rectangle([0, HEIGHT - 10, bar_w, HEIGHT], fill=C_CYAN)
        
        bg.save(frames_dir / f"frame_{i+1:05d}.png")
    
    encode_frames(frames_dir, audio_path, output_path, duration)
    shutil.rmtree(source_frames, ignore_errors=True)


def render_clip_curation(content, hook_text, audio_path, duration, boundaries, value_adds, output_path):
    """Type 7: Clip Curation Edit — use source footage + TTS commentary."""
    frames_dir = TMPDIR / f"{content['id']}_clip"
    frames_dir.mkdir(exist_ok=True)
    total_frames = int(duration * FPS)
    source = PROJECT / "output/source/2eicF3iPf1s.webm"
    
    # Extract source video segment
    seg_path = TMPDIR / f"{content['id']}_seg.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(content["start"]), "-i", str(source),
        "-t", str(content["end"] - content["start"]),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "0",
        "-an", str(seg_path)
    ], capture_output=True)
    
    # Extract frames from segment
    subprocess.run([
        "ffmpeg", "-y", "-i", str(seg_path),
        "-vf", f"fps={FPS},scale=405:720",
        "-q:v", "2", str(frames_dir / "src_%05d.png")
    ], capture_output=True)
    
    src_frames = sorted(frames_dir.glob("src_*.png"))
    
    for i in range(total_frames):
        t = i / FPS
        # Source frame as foreground
        if i < len(src_frames):
            fg = Image.open(src_frames[i])
        else:
            fg = Image.new("RGB", (405, 720), C_BLACK)
        
        # Scale to 9:16 with blur background
        bg = fg.resize((WIDTH, HEIGHT), Image.LANCZOS)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=30))
        # Darken background
        darken = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        bg = Image.blend(bg, darken, 0.35)
        
        # Foreground centered
        fg_916 = fg.resize((int(HEIGHT * 405 / 720), HEIGHT), Image.LANCZOS)
        fg_w = fg_916.width
        bg.paste(fg_916, ((WIDTH - fg_w) // 2, 0))
        
        draw = ImageDraw.Draw(bg)
        
        # Hook (first 3s)
        if t < 3.0:
            scale = min(1.0, t / 0.3)
            fnt = font(int(56 * scale))
            bbox = draw.textbbox((0, 0), hook_text, font=fnt)
            tw = bbox[2] - bbox[0]
            draw.rectangle([(WIDTH - tw) // 2 - 15, 100, (WIDTH + tw) // 2 + 15, 180], fill=(0, 0, 0))
            draw.text(((WIDTH - tw) // 2, 110), hook_text, font=fnt, fill=C_GOLD)
        
        # Value-adds
        for va in value_adds:
            renderer = VALUE_ADD_RENDERERS.get(va)
            if renderer:
                renderer(bg, t, 3.0, duration, draw)
        
        # Progress bar
        bar_w = int(WIDTH * t / duration)
        draw.rectangle([0, HEIGHT - 10, bar_w, HEIGHT], fill=C_CYAN)
        
        bg.save(frames_dir / f"frame_{i+1:05d}.png")
    
    encode_frames(frames_dir, audio_path, output_path, duration)
    seg_path.unlink(missing_ok=True)


def render_html_css(content, hook_text, audio_path, duration, boundaries, value_adds, output_path):
    """Type 4: HTML/CSS motion graphics — glassmorphism cards."""
    # Reuse kinetic typography as fallback (HTML/CSS needs Playwright subprocess)
    # For speed, render as styled text cards
    frames_dir = TMPDIR / f"{content['id']}_html"
    frames_dir.mkdir(exist_ok=True)
    total_frames = int(duration * FPS)
    
    for i in range(total_frames):
        t = i / FPS
        # Gradient background
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(102 + (118 - 102) * ratio)
            g = int(126 + (74 - 126) * ratio)
            b = int(234 + (162 - 234) * ratio)
            draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
        
        # Glass card
        card_margin = 80
        card_top = 400
        card_bottom = 1500
        # Semi-transparent card
        card = Image.new("RGBA", (WIDTH - 2 * card_margin, card_bottom - card_top), (255, 255, 255, 40))
        img.paste(card, (card_margin, card_top), card)
        draw = ImageDraw.Draw(img)
        
        # Hook (first 3s)
        if t < 3.0:
            scale = min(1.0, t / 0.4)
            fnt = font(int(64 * scale))
            bbox = draw.textbbox((0, 0), hook_text, font=fnt)
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw) // 2, 500), hook_text, font=fnt, fill=C_WHITE)
        
        # Body text
        for b in boundaries:
            if b["offset"] <= t <= b["offset"] + b["duration"]:
                words = b["text"].split()
                for wi, word in enumerate(words):
                    wt = b["offset"] + wi * (b["duration"] / max(len(words), 1))
                    if wt <= t <= wt + 0.5:
                        is_punch = word.lower().strip(".,!?\"'") in content["punchlines"]
                        size = 56 if is_punch else 44
                        color = C_GOLD if is_punch else (240, 240, 240)
                        fnt = font(size)
                        y_pos = 700 + (wi % 6) * 80
                        bbox = draw.textbbox((0, 0), word, font=fnt)
                        tw = bbox[2] - bbox[0]
                        draw.text(((WIDTH - tw) // 2, y_pos), word, font=fnt, fill=color)
                break
        
        # Value-adds
        for va in value_adds:
            renderer = VALUE_ADD_RENDERERS.get(va)
            if renderer:
                renderer(img, t, 3.0, duration, draw)
        
        # Progress bar
        bar_w = int(WIDTH * t / duration)
        draw.rectangle([0, HEIGHT - 10, bar_w, HEIGHT], fill=C_CYAN)
        
        img.save(frames_dir / f"frame_{i+1:05d}.png")
    
    encode_frames(frames_dir, audio_path, output_path, duration)


RENDERERS = {
    "kinetic_typography": render_kinetic_typography,
    "data_viz": render_data_viz,
    "whiteboard_sketch": render_whiteboard,
    "meme_notification": render_meme_notification,
    "stock_footage": render_stock_footage,
    "clip_curation_edit": render_clip_curation,
    "html_css_motion": render_html_css,
}


def encode_frames(frames_dir, audio_path, output_path, duration):
    """Encode PNG frames + audio → MP4."""
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%05d.png"),
        "-i", str(audio_path),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "15",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest", "-t", str(duration),
        "-movflags", "+faststart",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    # Cleanup frames
    shutil.rmtree(frames_dir, ignore_errors=True)
    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"    Encoded: {output_path.name} ({size_mb:.1f}MB)")


def render_variant(variant, content, idx):
    """Render a single variant video."""
    vid = f"exp{idx:02d}_{variant['name'][:40]}"
    print(f"\n{'='*60}")
    print(f"  [{idx}/6] {vid}")
    print(f"  Type: {variant['video_type']} | Hook: {variant['hook_type']} | VAs: {variant['value_add']}")
    
    # Generate hook text
    hook_text = get_hook_text(variant["hook_type"], content)
    
    # Generate TTS
    audio_path = TMPDIR / f"{vid}.mp3"
    print(f"  Generating TTS...")
    duration, boundaries = asyncio.run(gen_tts(content["text"], str(audio_path)))
    print(f"  TTS: {duration:.1f}s, {len(boundaries)} words")
    
    # Clip to <60s
    if duration > 58:
        duration = 58
    
    # Render
    renderer = RENDERERS.get(variant["video_type"])
    if not renderer:
        print(f"  SKIP: no renderer for {variant['video_type']}")
        return None
    
    output_path = OUTDIR / f"{vid}.mp4"
    print(f"  Rendering {variant['video_type']}...")
    renderer(content, hook_text, str(audio_path), duration, boundaries, variant["value_add"], output_path)
    
    audio_path.unlink(missing_ok=True)
    return output_path


# ── Main ──
import asyncio

variants_path = PROJECT / "output" / "random_variants_v1.json"
variants = json.loads(variants_path.read_text())

print(f"🎮 Random Exploration — {len(variants)} variants")
print(f"   Output: {OUTDIR}")

# Assign content to variants (round-robin)
results = []
for idx, variant in enumerate(variants, 1):
    content = CONTENT_SEGMENTS[(idx - 1) % len(CONTENT_SEGMENTS)]
    try:
        out = render_variant(variant, content, idx)
        if out:
            results.append(out)
    except Exception as e:
        print(f"  ERROR: {e}")

print(f"\n{'='*60}")
print(f"✅ Rendered {len(results)}/{len(variants)} variants")
for p in results:
    size = os.path.getsize(p) / 1024 / 1024
    print(f"  {p.name} ({size:.1f}MB)")
