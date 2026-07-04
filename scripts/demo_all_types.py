#!/usr/bin/env python3
"""
Multi-Format Video Demo — 5 visual styles, same audio.
Renders short ~15s demo of each type for visual comparison.
"""

import asyncio
import subprocess
import os
import math
import json
import tempfile
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import edge_tts

# === CONFIG ===
WIDTH, HEIGHT, FPS = 1080, 1920, 30
OUTPUT_DIR = Path("/Users/hung/code/ai/shorts/output/demos")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR = Path(tempfile.mkdtemp(prefix="video_demo_"))

SCRIPT_TEXT = (
    "The average American spends fifteen hundred dollars on coffee every single year. "
    "But if you invested that money at eight percent instead? "
    "That's one hundred seventy thousand dollars in thirty years. "
    "Your daily latte is literally costing you a house."
)

VOICE = "en-US-AndrewNeural"
RATE = "+8%"

# Font paths
FONT_BOLD = "/System/Library/Fonts/Helvetica.ttc"
FONT_MONO = "/System/Library/Fonts/Menlo.ttc"

def font(size, bold=True):
    try:
        return ImageFont.truetype(FONT_BOLD, size, index=1 if bold else 0)
    except:
        return ImageFont.truetype(FONT_BOLD, size)

def mono_font(size):
    return ImageFont.truetype(FONT_MONO, size)

def log(msg):
    print(f"  {msg}")

# === TTS ===
async def generate_tts():
    """Generate TTS + collect sentence boundary timings."""
    audio_path = str(TEMP_DIR / "tts.mp3")
    comm = edge_tts.Communicate(SCRIPT_TEXT, VOICE, rate=RATE)
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
    with open(audio_path, "wb") as f:
        f.write(audio_data)

    # Get total duration
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", audio_path],
        capture_output=True, text=True
    )
    total_duration = float(json.loads(result.stdout)["format"]["duration"])

    log(f"TTS: {total_duration:.1f}s, {len(boundaries)} boundaries")
    return audio_path, boundaries, total_duration

# === HELPER: encode frames to video ===
def encode_frames(frames_dir, audio_path, output_path, duration):
    """Encode PNG frames + audio → MP4."""
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%05d.png"),
        "-i", audio_path,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "15",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        "-t", str(duration),
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    size_mb = os.path.getsize(output_path) / 1024 / 1024
    log(f"Encoded: {output_path} ({size_mb:.1f}MB)")

# === TYPE 2: KINETIC TYPOGRAPHY ===
def render_kinetic_typography(audio_path, boundaries, total_duration, output_path):
    """Pure text animation on dark gradient. High energy."""
    log("Rendering Type 2: Kinetic Typography...")
    frames_dir = TEMP_DIR / "kinetic"
    frames_dir.mkdir(exist_ok=True)

    total_frames = int(total_duration * FPS)

    # Colors
    BG_TOP = (26, 26, 46)      # #1a1a2e
    BG_BOT = (22, 33, 62)      # #16213e
    TEXT_WHITE = (255, 255, 255)
    GOLD = (255, 215, 0)
    PURPLE = (157, 78, 221)

    # Segment timings (split script into visual segments)
    seg1_end = boundaries[1]["offset"] + boundaries[1]["duration"] if len(boundaries) > 1 else total_duration * 0.35
    seg2_end = boundaries[3]["offset"] + boundaries[3]["duration"] if len(boundaries) > 3 else total_duration * 0.6
    seg3_end = boundaries[5]["offset"] + boundaries[5]["duration"] if len(boundaries) > 5 else total_duration * 0.85

    segments = [
        {"end": seg1_end, "lines": ["$1,500", "on COFFEE", "every year"], "colors": [GOLD, TEXT_WHITE, TEXT_WHITE]},
        {"end": seg2_end, "lines": ["invested at 8%?", "That becomes..."], "colors": [PURPLE, TEXT_WHITE]},
        {"end": seg3_end, "lines": ["$170,000", "in 30 years"], "colors": [GOLD, TEXT_WHITE]},
        {"end": total_duration, "lines": ["Your latte", "is costing you", "a HOUSE."], "colors": [TEXT_WHITE, TEXT_WHITE, GOLD]},
    ]

    for i in range(total_frames):
        t = i / FPS

        # Find current segment
        seg_idx = 0
        for si, seg in enumerate(segments):
            if t < seg["end"]:
                seg_idx = si
                break
        else:
            seg_idx = len(segments) - 1

        seg = segments[seg_idx]
        seg_start = segments[seg_idx - 1]["end"] if seg_idx > 0 else 0
        local_t = t - seg_start

        # Create gradient background
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * ratio)
            g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * ratio)
            b = int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * ratio)
            draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

        # Animated glow circle behind text
        glow_radius = 200 + int(30 * math.sin(t * 3))
        glow_x, glow_y = WIDTH // 2, HEIGHT // 2
        for r in range(glow_radius, 0, -10):
            alpha_val = max(0, 25 - r // 10)
            color = (seg["colors"][0][0] // 4, seg["colors"][0][1] // 4, seg["colors"][0][2] // 4)
            draw.ellipse([glow_x - r, glow_y - r, glow_x + r, glow_y + r], fill=color)

        # Draw text lines with pop-in animation
        lines = seg["lines"]
        colors = seg["colors"]
        n_lines = len(lines)
        line_spacing = 100
        total_height = line_spacing * n_lines
        start_y = HEIGHT // 2 - total_height // 2

        for li, (line, color) in enumerate(zip(lines, colors)):
            line_t = local_t - li * 0.15  # stagger
            if line_t < 0:
                continue

            # Pop-in: scale 0→1 over 0.2s, then settle
            anim_duration = 0.25
            if line_t < anim_duration:
                scale = max(0.01, line_t / anim_duration)
                scale = 1 - (1 - scale) ** 3  # ease-out
            else:
                scale = 1.0 + 0.02 * math.sin((line_t - anim_duration) * 4)  # subtle bob

            fnt = font(int(72 * scale))
            bbox = draw.textbbox((0, 0), line, font=fnt)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            x = (WIDTH - tw) // 2
            y = start_y + li * line_spacing - th // 2

            # Shadow
            shadow_fnt = font(int(72 * scale))
            for dx, dy in [(3, 3)]:
                draw.text((x + dx, y + dy), line, font=shadow_fnt, fill=(0, 0, 0))

            draw.text((x, y), line, font=fnt, fill=color)

        img.save(frames_dir / f"frame_{i+1:05d}.png")

    encode_frames(frames_dir, audio_path, output_path, total_duration)

# === TYPE 3: ANIMATED DATA VIZ ===
def render_data_viz(audio_path, boundaries, total_duration, output_path):
    """Counter animations, bar charts. Numbers are the hero."""
    log("Rendering Type 3: Data Viz...")
    frames_dir = TEMP_DIR / "dataviz"
    frames_dir.mkdir(exist_ok=True)

    total_frames = int(total_duration * FPS)

    BG_COLOR = (15, 15, 23)  # Near black
    GREEN = (0, 255, 136)
    RED = (255, 68, 68)
    GOLD = (255, 215, 0)
    WHITE = (240, 240, 240)
    DIM = (80, 80, 100)

    seg1_end = boundaries[1]["offset"] + boundaries[1]["duration"] if len(boundaries) > 1 else total_duration * 0.3
    seg2_end = boundaries[3]["offset"] + boundaries[3]["duration"] if len(boundaries) > 3 else total_duration * 0.5
    seg3_end = boundaries[5]["offset"] + boundaries[5]["duration"] if len(boundaries) > 5 else total_duration * 0.75

    def ease_out_cubic(t):
        return 1 - (1 - t) ** 3

    def format_money(n):
        if n >= 1000000:
            return f"${n/1000000:.1f}M"
        elif n >= 1000:
            return f"${n/1000:.0f}K"
        return f"${n:.0f}"

    for i in range(total_frames):
        t = i / FPS
        img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
        draw = ImageDraw.Draw(img)

        # Grid background (subtle)
        for gx in range(0, WIDTH, 60):
            draw.line([(gx, 0), (gx, HEIGHT)], fill=(25, 25, 35), width=1)
        for gy in range(0, HEIGHT, 60):
            draw.line([(0, gy), (WIDTH, gy)], fill=(25, 25, 35), width=1)

        if t < seg1_end:
            # Segment 1: Counter $0 → $1,500
            progress = ease_out_cubic(min(1.0, t / seg1_end))
            current_val = int(1500 * progress)
            display = format_money(current_val)

            fnt = font(140)
            bbox = draw.textbbox((0, 0), display, font=fnt)
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw) // 2, HEIGHT // 2 - 150), display, font=fnt, fill=GREEN)

            label_fnt = font(36)
            label = "/year on COFFEE"
            bbox2 = draw.textbbox((0, 0), label, font=label_fnt)
            tw2 = bbox2[2] - bbox2[0]
            draw.text(((WIDTH - tw2) // 2, HEIGHT // 2 + 20), label, font=label_fnt, fill=DIM)

            # Animated bar
            bar_h = int(300 * progress)
            bar_w = 80
            bx = (WIDTH - bar_w) // 2
            by = HEIGHT - 400 - bar_h
            draw.rounded_rectangle([bx, by, bx + bar_w, HEIGHT - 400], radius=10, fill=GREEN)

        elif t < seg2_end:
            # Segment 2: Transition — "Invested at 8%?"
            local_t = t - seg1_end
            seg_dur = seg2_end - seg1_end
            progress = min(1.0, local_t / seg_dur)

            fnt = font(72)
            text = "Invested at 8%?"
            bbox = draw.textbbox((0, 0), text, font=fnt)
            tw = bbox[2] - bbox[0]
            y_offset = int(30 * math.sin(local_t * 5))
            draw.text(((WIDTH - tw) // 2, HEIGHT // 2 - 50 + y_offset), text, font=fnt, fill=GOLD)

            # Arrow pointing right
            arrow_y = HEIGHT // 2 + 80
            arrow_progress = ease_out_cubic(progress)
            arrow_len = int(400 * arrow_progress)
            draw.line([(WIDTH // 2 - arrow_len // 2, arrow_y), (WIDTH // 2 + arrow_len // 2, arrow_y)], fill=GOLD, width=6)
            # Arrow head
            if arrow_progress > 0.8:
                ax = WIDTH // 2 + arrow_len // 2
                draw.polygon([(ax, arrow_y), (ax - 20, arrow_y - 15), (ax - 20, arrow_y + 15)], fill=GOLD)

        elif t < seg3_end:
            # Segment 3: Counter $0 → $170,000
            local_t = t - seg2_end
            seg_dur = seg3_end - seg2_end
            progress = ease_out_cubic(min(1.0, local_t / max(0.1, seg_dur)))
            current_val = int(170000 * progress)
            display = format_money(current_val)

            fnt = font(160)
            bbox = draw.textbbox((0, 0), display, font=fnt)
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw) // 2, HEIGHT // 2 - 150), display, font=fnt, fill=GOLD)

            label_fnt = font(36)
            label = "in 30 years"
            bbox2 = draw.textbbox((0, 0), label, font=label_fnt)
            tw2 = bbox2[2] - bbox2[0]
            draw.text(((WIDTH - tw2) // 2, HEIGHT // 2 + 40), label, font=label_fnt, fill=WHITE)

            # Mini bar chart: coffee vs invested
            chart_y = HEIGHT - 500
            bar1_h = 30  # coffee (tiny)
            bar2_h = int(250 * progress)  # invested (huge)

            draw.rounded_rectangle([WIDTH // 2 - 160, chart_y + 250 - bar1_h, WIDTH // 2 - 60, chart_y + 250], radius=8, fill=RED)
            draw.rounded_rectangle([WIDTH // 2 + 60, chart_y + 250 - bar2_h, WIDTH // 2 + 160, chart_y + 250], radius=8, fill=GREEN)

            lbl_fnt = font(24)
            draw.text((WIDTH // 2 - 155, chart_y + 260), "Coffee", font=lbl_fnt, fill=RED)
            draw.text((WIDTH // 2 + 65, chart_y + 260), "Invested", font=lbl_fnt, fill=GREEN)

        else:
            # Segment 4: "Costing you a HOUSE"
            local_t = t - seg3_end
            fnt = font(80)
            text1 = "Your latte is"
            text2 = "costing you"
            text3 = "a HOUSE"

            texts = [(text1, WHITE), (text2, WHITE), (text3, RED)]
            for ti, (txt, col) in enumerate(texts):
                scale = 1.0 + 0.05 * math.sin(local_t * 4 + ti * 0.5)
                fnt_s = font(int(80 * scale))
                bbox = draw.textbbox((0, 0), txt, font=fnt_s)
                tw = bbox[2] - bbox[0]
                y = HEIGHT // 2 - 130 + ti * 100
                draw.text(((WIDTH - tw) // 2, y), txt, font=fnt_s, fill=col)

        img.save(frames_dir / f"frame_{i+1:05d}.png")

    encode_frames(frames_dir, audio_path, output_path, total_duration)

# === TYPE 4: HTML/CSS MOTION GRAPHICS (via subprocess) ===
HTMLCSS_RENDER_SCRIPT = '''
import sys, json, math
from pathlib import Path
from PIL import Image

WIDTH, HEIGHT, FPS = 1080, 1920, 30

def font(size, bold=True):
    from PIL import ImageFont
    try:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size, index=1 if bold else 0)
    except:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)

# Load config
config = json.loads(sys.argv[1])
slides_data = config["slides"]
frames_dir = Path(config["frames_dir"])
audio_path = config["audio_path"]
output_path = config["output_path"]
total_duration = config["total_duration"]

from playwright.sync_api import sync_playwright

html_template = """<!DOCTYPE html>
<html><head><style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        width: 1080px; height: 1920px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex; align-items: center; justify-content: center;
        font-family: -apple-system, 'Helvetica Neue', sans-serif;
    }
    .card {
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.25);
        border-radius: 32px;
        padding: 80px 60px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        width: 850px;
    }
    .card.gold { background: rgba(255,215,0,0.15); border-color: rgba(255,215,0,0.4); }
    .card.red { background: rgba(255,68,68,0.15); border-color: rgba(255,68,68,0.4); }
    .label { color: rgba(255,255,255,0.7); font-size: 32px; font-weight: 700; letter-spacing: 4px; margin-bottom: 30px; }
    .big-num { color: white; font-size: 130px; font-weight: 900; margin: 20px 0; line-height: 1.1; }
    .big-num.gold { color: #FFD700; text-shadow: 0 0 40px rgba(255,215,0,0.5); }
    .big-num.red { font-size: 150px; }
    .sub { color: rgba(255,255,255,0.8); font-size: 36px; margin-top: 20px; }
    .arrow { color: #FFD700; font-size: 80px; margin: 30px 0; }
</style></head><body>{{CONTENT}}</body></html>"""

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chromium", args=["--no-sandbox", "--disable-gpu"])
    page = browser.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)

    slide_images = []
    for si, slide in enumerate(slides_data):
        page.set_content(html_template.replace("{{CONTENT}}", slide["html"]))
        page.wait_for_load_state("networkidle", timeout=5000)
        img_bytes = page.screenshot(full_page=False)
        img_path = frames_dir / f"slide_{si}.png"
        with open(img_path, "wb") as f:
            f.write(img_bytes)
        slide_images.append(Image.open(img_path))
    browser.close()

total_frames = int(total_duration * FPS)
fade_duration = 0.3

for i in range(total_frames):
    t = i / FPS
    slide_idx = 0
    for si, slide in enumerate(slides_data):
        if t < slide["end"] * total_duration:
            slide_idx = si
            break
    else:
        slide_idx = len(slides_data) - 1

    slide_start_ratio = slides_data[slide_idx - 1]["end"] if slide_idx > 0 else 0
    slide_end_ratio = slides_data[slide_idx]["end"]
    slide_start_t = slide_start_ratio * total_duration
    slide_end_t = slide_end_ratio * total_duration
    local_t = t - slide_start_t

    zoom = 1.0 + 0.03 * (local_t / max(0.1, slide_end_t - slide_start_t))
    base_img = slide_images[slide_idx].resize((int(WIDTH * zoom), int(HEIGHT * zoom)), Image.LANCZOS)
    left = (base_img.width - WIDTH) // 2
    top = (base_img.height - HEIGHT) // 2
    base_img = base_img.crop((left, top, left + WIDTH, top + HEIGHT))

    if slide_idx > 0 and local_t < fade_duration:
        prev_img = slide_images[slide_idx - 1].resize((int(WIDTH * 1.03), int(HEIGHT * 1.03)), Image.LANCZOS)
        left2 = (prev_img.width - WIDTH) // 2
        top2 = (prev_img.height - HEIGHT) // 2
        prev_img = prev_img.crop((left2, top2, left2 + WIDTH, top2 + HEIGHT))
        alpha = int(255 * (local_t / fade_duration))
        base_img = Image.blend(prev_img, base_img, alpha / 255)

    base_img.save(frames_dir / f"frame_{i+1:05d}.png")

import subprocess
cmd = ["ffmpeg", "-y", "-framerate", str(FPS), "-i", str(frames_dir / "frame_%05d.png"),
       "-i", audio_path, "-c:v", "libx264", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "128k", "-shortest", "-t", str(total_duration), output_path]
subprocess.run(cmd, capture_output=True, check=True)
print(f"OK: {output_path}")
'''

def render_html_css(audio_path, boundaries, total_duration, output_path):
    """Modern glassmorphism cards via Playwright in subprocess."""
    log("Rendering Type 4: HTML/CSS Motion Graphics...")
    frames_dir = TEMP_DIR / "htmlcss"
    frames_dir.mkdir(exist_ok=True)

    slides = [
        {"end": 0.25, "html": "<div class='card'><div class='label'>ANNUAL COFFEE SPEND</div><div class='big-num'>$1,500</div><div class='sub'>that is $4.10 every single day</div></div>"},
        {"end": 0.5, "html": "<div class='card'><div class='label'>IF INVESTED AT 8%</div><div class='arrow'>\u2192 \u2192 \u2192</div><div class='sub'>for 30 years...</div></div>"},
        {"end": 0.75, "html": "<div class='card gold'><div class='label'>YOUR COFFEE BECOMES</div><div class='big-num gold'>$170,000</div><div class='sub'>a house down payment</div></div>"},
        {"end": 1.0, "html": "<div class='card red'><div class='label'>THINK ABOUT IT</div><div class='big-num red'>\U0001F9E0</div><div class='sub'>every latte = a brick of your future house</div></div>"},
    ]

    config = {
        "slides": slides,
        "frames_dir": str(frames_dir),
        "audio_path": audio_path,
        "output_path": output_path,
        "total_duration": total_duration,
    }

    # Run in subprocess to avoid asyncio conflict
    script_path = TEMP_DIR / "htmlcss_render.py"
    with open(script_path, "w") as f:
        f.write(HTMLCSS_RENDER_SCRIPT)

    result = subprocess.run(
        ["/usr/bin/python3", str(script_path), json.dumps(config)],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        raise RuntimeError(f"HTML/CSS render failed: {result.stderr[-500:]}")

    size_mb = os.path.getsize(output_path) / 1024 / 1024
    log(f"Encoded: {output_path} ({size_mb:.1f}MB)")
    return True

# === TYPE 5: WHITEBOARD SKETCH ===
def render_whiteboard(audio_path, boundaries, total_duration, output_path):
    """Hand-drawn educational style. Cream background, sketchy feel."""
    log("Rendering Type 5: Whiteboard Sketch...")
    frames_dir = TEMP_DIR / "whiteboard"
    frames_dir.mkdir(exist_ok=True)

    total_frames = int(total_duration * FPS)

    BG_COLOR = (253, 246, 227)  # Cream/paper
    INK = (44, 62, 80)          # Dark blue ink
    HIGHLIGHT = (255, 193, 7)   # Yellow highlighter
    RED_INK = (231, 76, 60)

    seg1_end = boundaries[1]["offset"] + boundaries[1]["duration"] if len(boundaries) > 1 else total_duration * 0.3
    seg2_end = boundaries[3]["offset"] + boundaries[3]["duration"] if len(boundaries) > 3 else total_duration * 0.5
    seg3_end = boundaries[5]["offset"] + boundaries[5]["duration"] if len(boundaries) > 5 else total_duration * 0.75

    for i in range(total_frames):
        t = i / FPS
        img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
        draw = ImageDraw.Draw(img)

        # Paper texture (subtle dots)
        for dot_y in range(0, HEIGHT, 40):
            for dot_x in range(0, WIDTH, 40):
                draw.ellipse([dot_x, dot_y, dot_x + 2, dot_y + 2], fill=(240, 233, 215))

        # Hand-drawn title at top
        title_fnt = font(44)
        title = "☕ COFFEE MATH"
        draw.text((80, 100), title, font=title_fnt, fill=INK)

        # Underline (wobbly)
        for ux in range(80, 400, 5):
            uy = 165 + int(3 * math.sin(ux * 0.1))
            draw.line([(ux, uy), (ux + 5, uy + int(2 * math.cos(ux * 0.15)))], fill=INK, width=3)

        if t < seg1_end:
            # Draw $1,500 with circle around it
            progress = min(1.0, t / seg1_end)
            num_fnt = font(130)
            text = "$1,500"
            bbox = draw.textbbox((0, 0), text, font=num_fnt)
            tw = bbox[2] - bbox[0]
            cx, cy = (WIDTH - tw) // 2, 500
            draw.text((cx, cy), text, font=num_fnt, fill=INK)

            # Circle being drawn (progressive)
            circle_progress = min(1.0, progress * 1.5)
            if circle_progress > 0:
                angle = circle_progress * 2 * math.pi
                steps = max(10, int(60 * circle_progress))
                prev = None
                for s in range(steps):
                    a = (s / 60) * 2 * math.pi
                    if a > angle:
                        break
                    px = WIDTH // 2 + int(250 * math.cos(a - math.pi / 2))
                    py = 600 + int(120 * math.sin(a - math.pi / 2))
                    if prev:
                        draw.line([prev, (px, py)], fill=RED_INK, width=5)
                    prev = (px, py)

            label_fnt = font(34)
            draw.text((cx - 20, 750), "per year on coffee", font=label_fnt, fill=INK)

            # Arrow down
            if progress > 0.6:
                ax = WIDTH // 2
                for ay in range(850, 950):
                    draw.point((ax + int(3 * math.sin(ay * 0.1)), ay), fill=INK)

        elif t < seg2_end:
            # "Invest at 8%"
            local_t = t - seg1_end
            num_fnt = font(100)
            draw.text((WIDTH // 2 - 200, 500), "Invest at", font=font(60), fill=INK)
            draw.text((WIDTH // 2 - 120, 580), "8% 📈", font=num_fnt, fill=HIGHLIGHT)

            # Sketchy arrow
            arrow_y = 800
            for ax in range(300, 780, 8):
                ay = arrow_y + int(5 * math.sin(ax * 0.05))
                draw.line([(ax, ay), (ax + 8, ay + int(3 * math.cos(ax * 0.07)))], fill=INK, width=4)
            # Arrowhead
            draw.polygon([(780, arrow_y), (750, arrow_y - 20), (755, arrow_y + 20)], fill=INK)

        elif t < seg3_end:
            # $170,000 result
            num_fnt = font(120)
            text = "$170,000"
            bbox = draw.textbbox((0, 0), text, font=num_fnt)
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw) // 2, 500), text, font=num_fnt, fill=RED_INK)

            # Highlight box
            box_progress = min(1.0, (t - seg2_end) / 0.5)
            if box_progress > 0:
                bw = int(tw + 60)
                bh = 160
                bx = (WIDTH - bw) // 2
                by = 490
                # Sketchy highlight rectangle
                for cx in range(int(bw * box_progress)):
                    for cy_offset in [0, bh]:
                        draw.point((bx + cx, by + cy_offset + int(2 * math.sin(cx * 0.1))), fill=HIGHLIGHT)
                    if cx % 3 == 0:
                        draw.line([(bx + cx, by), (bx + cx, by + bh)], fill=(255, 235, 130))

            draw.text(((WIDTH - 200) // 2, 700), "in 30 years!", font=font(44), fill=INK)

        else:
            # "Costing a house" with doodle
            local_t = t - seg3_end
            draw.text((WIDTH // 2 - 280, 500), "That latte =", font=font(60), fill=INK)
            draw.text((WIDTH // 2 - 180, 600), "🏠 - 1 brick", font=font(70), fill=RED_INK)

            # Sad face doodle
            face_cx, face_cy = WIDTH // 2, 1000
            draw.ellipse([face_cx - 80, face_cy - 80, face_cx + 80, face_cy + 80], outline=INK, width=4)
            draw.ellipse([face_cx - 35, face_cy - 30, face_cx - 15, face_cy - 10], fill=INK)
            draw.ellipse([face_cx + 15, face_cy - 30, face_cx + 35, face_cy - 10], fill=INK)
            # Frown
            draw.arc([face_cx - 40, face_cy + 20, face_cx + 40, face_cy + 60], 0, 180, fill=INK, width=4)

        img.save(frames_dir / f"frame_{i+1:05d}.png")

    encode_frames(frames_dir, audio_path, output_path, total_duration)

# === TYPE 6: MEME / NOTIFICATION MOCKUP ===
def render_meme_notification(audio_path, boundaries, total_duration, output_path):
    """Fake phone UI, notifications, bank alerts. Relatable/meme."""
    log("Rendering Type 6: Meme/Notification...")
    frames_dir = TEMP_DIR / "meme"
    frames_dir.mkdir(exist_ok=True)

    total_frames = int(total_duration * FPS)

    PHONE_BG = (18, 18, 18)
    NOTIF_BG = (40, 40, 45)
    GREEN = (48, 209, 88)
    RED = (255, 69, 58)
    WHITE = (255, 255, 255)
    GRAY = (142, 142, 147)
    GOLD = (255, 214, 10)

    seg1_end = boundaries[1]["offset"] + boundaries[1]["duration"] if len(boundaries) > 1 else total_duration * 0.25
    seg2_end = boundaries[3]["offset"] + boundaries[3]["duration"] if len(boundaries) > 3 else total_duration * 0.5
    seg3_end = boundaries[5]["offset"] + boundaries[5]["duration"] if len(boundaries) > 5 else total_duration * 0.75

    for i in range(total_frames):
        t = i / FPS
        img = Image.new("RGB", (WIDTH, HEIGHT), PHONE_BG)
        draw = ImageDraw.Draw(img)

        # Phone status bar
        draw.rectangle([0, 0, WIDTH, 80], fill=(30, 30, 30))
        draw.text((40, 25), "9:41", font=font(28), fill=WHITE)
        # Battery icon
        draw.rounded_rectangle([WIDTH - 100, 30, WIDTH - 40, 55], radius=4, outline=GRAY, width=2)
        draw.rectangle([WIDTH - 95, 35, WIDTH - 70, 50], fill=GREEN)

        if t < seg1_end:
            # Notification: coffee spend
            progress = min(1.0, t / seg1_end)
            slide_y = int(-300 + 380 * (1 - (1 - progress) ** 3))

            # Notification card
            draw.rounded_rectangle([40, slide_y, WIDTH - 40, slide_y + 280], radius=24, fill=NOTIF_BG)

            # App icon (coffee cup emoji style)
            draw.rounded_rectangle([70, slide_y + 25, 130, slide_y + 85], radius=12, fill=(111, 68, 42))
            draw.text((78, slide_y + 30), "☕", font=font(36))

            draw.text((155, slide_y + 25), "STARBUCKS", font=font(26), fill=GRAY)
            draw.text((155, slide_y + 55), "just now", font=font(22), fill=GRAY)

            draw.text((70, slide_y + 110), "You spent $4.10", font=font(42), fill=WHITE)
            draw.text((70, slide_y + 165), "on a Caramel Macchiato", font=font(30), fill=GRAY)

            # Red alert badge
            draw.rounded_rectangle([70, slide_y + 210, WIDTH - 70, slide_y + 255], radius=8, fill=(60, 30, 30))
            draw.text((90, slide_y + 215), "💸 That's $1,500/year!", font=font(28), fill=RED)

        elif t < seg2_end:
            # "What if you invested?" — calculator app mockup
            local_t = t - seg1_end
            draw.text((WIDTH // 2 - 200, 150), "🧮 Investment Calculator", font=font(40), fill=WHITE)

            # Calculator display
            draw.rounded_rectangle([60, 250, WIDTH - 60, 400], radius=16, fill=(30, 30, 35))
            draw.text((100, 290), "$1,500 × 8% × 30yr", font=font(36), fill=GRAY)
            draw.text((100, 340), "= ???", font=font(44), fill=GOLD)

            # Buttons grid
            btn_labels = ["7", "8", "9", "4", "5", "6", "1", "2", "3", "0", ".", "="]
            btn_size = 140
            start_x = 80
            start_y = 450
            for bi, label in enumerate(btn_labels):
                col = bi % 3
                row = bi // 3
                bx = start_x + col * (btn_size + 20)
                by = start_y + row * (btn_size + 20)
                color = (50, 50, 55) if label != "=" else GOLD
                txt_color = WHITE if label != "=" else (18, 18, 18)
                draw.rounded_rectangle([bx, by, bx + btn_size, by + btn_size], radius=20, fill=color)
                bbox = draw.textbbox((0, 0), label, font=font(48))
                tw = bbox[2] - bbox[0]
                draw.text((bx + (btn_size - tw) // 2, by + 40), label, font=font(48), fill=txt_color)

        elif t < seg3_end:
            # Result: $170,000
            local_t = t - seg2_end
            seg_dur = seg3_end - seg2_end
            progress = min(1.0, local_t / max(0.1, seg_dur))

            # Big green number counting up
            val = int(170000 * (1 - (1 - progress) ** 3))
            display = f"${val:,}"
            fnt = font(100)
            bbox = draw.textbbox((0, 0), display, font=fnt)
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw) // 2, 400), display, font=fnt, fill=GREEN)

            draw.text((WIDTH // 2 - 200, 540), "from your coffee money!", font=font(32), fill=GRAY)

            # Celebration emoji pop-in
            emoji_scale = min(1.0, progress * 2)
            efnt = font(int(120 * emoji_scale))
            draw.text((WIDTH // 2 - 60, 650), "🎉", font=efnt)

            # Bank notification
            notif_y = 850 + int(20 * math.sin(t * 4))
            draw.rounded_rectangle([40, notif_y, WIDTH - 40, notif_y + 120], radius=20, fill=NOTIF_BG)
            draw.text((70, notif_y + 20), "🏦 Bank: Your balance grew", font=font(30), fill=GREEN)
            draw.text((70, notif_y + 60), "+$170,000", font=font(42), fill=GREEN)

        else:
            # Meme punchline
            local_t = t - seg3_end
            shake = int(5 * math.sin(local_t * 15))

            draw.text((WIDTH // 2 - 250 + shake, 400), "Every sip of latte", font=font(44), fill=WHITE)
            draw.text((WIDTH // 2 - 250 + shake, 470), "is a brick of your house", font=font(44), fill=RED)

            draw.text((WIDTH // 2 - 250 + shake, 580), "going in the TRASH 🗑️", font=font(50), fill=RED)

            # Crying emoji
            draw.text((WIDTH // 2 - 50 + shake, 700), "😭", font=font(120))

            # Meme text at bottom
            draw.rounded_rectangle([40, HEIGHT - 200, WIDTH - 40, HEIGHT - 80], radius=16, fill=NOTIF_BG)
            draw.text((70, HEIGHT - 180), "POV: You're addicted to $7 lattes", font=font(30), fill=GRAY)

        img.save(frames_dir / f"frame_{i+1:05d}.png")

    encode_frames(frames_dir, audio_path, output_path, total_duration)


# === MAIN ===
async def main():
    print("=" * 60)
    print("MULTI-FORMAT VIDEO DEMO")
    print("=" * 60)

    # Step 1: Generate shared TTS
    print("\n[1/3] Generating TTS...")
    audio_path, boundaries, total_duration = await generate_tts()

    # Step 2: Render each type
    print("\n[2/3] Rendering 5 video types...")
    results = {}

    types = [
        ("type2_kinetic_typography.mp4", render_kinetic_typography),
        ("type3_data_viz.mp4", render_data_viz),
        ("type4_html_css.mp4", render_html_css),
        ("type5_whiteboard.mp4", render_whiteboard),
        ("type6_meme_notification.mp4", render_meme_notification),
    ]

    for name, render_fn in types:
        output_path = str(OUTPUT_DIR / name)
        print(f"\n--- {name} ---")
        try:
            result = render_fn(audio_path, boundaries, total_duration, output_path)
            if result is False:
                results[name] = "SKIPPED"
            else:
                results[name] = "OK"
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            results[name] = f"ERROR: {e}"

    # Step 3: Summary
    print("\n" + "=" * 60)
    print("[3/3] DEMO SUMMARY")
    print("=" * 60)
    for name, status in results.items():
        path = OUTPUT_DIR / name
        size = f"{os.path.getsize(path)/1024/1024:.1f}MB" if path.exists() else "N/A"
        print(f"  {name:40s} {status:10s} {size}")

    # Cleanup temp
    shutil.rmtree(TEMP_DIR, ignore_errors=True)
    print(f"\nOutput: {OUTPUT_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())
