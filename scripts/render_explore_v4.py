#!/usr/bin/env python3
"""
Multi-Segment Stitching — 6 variants, 30-60s each.

Each video = 3-5 content segments stitched into 1 narrative.
- Animation types: render phases with visual transitions
- Clip/Stock types: cut source footage + overlay commentary + value-adds
"""
import json, subprocess, sys, os, math, random, tempfile, shutil, asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edge_tts

PROJECT = Path("/Users/hung/code/ai/shorts")
OUTDIR = PROJECT / "output" / "explore_v4"
OUTDIR.mkdir(parents=True, exist_ok=True)
TMPDIR = PROJECT / "output" / "tmp_explore4"
TMPDIR.mkdir(parents=True, exist_ok=True)
OVERLAYS = PROJECT / "output" / "overlays"

WIDTH, HEIGHT, FPS = 1080, 1920, 30
FONT_BOLD = "/System/Library/Fonts/Helvetica.ttc"
VOICE = "en-US-AndrewNeural"
RATE = "+8%"

C_WHITE = (255, 255, 255)
C_GOLD = (255, 215, 0)
C_GREEN = (0, 255, 136)
C_RED = (255, 68, 68)
C_CYAN = (0, 229, 255)
C_BLACK = (15, 15, 23)
C_DARK_BG = (26, 26, 46)

def font(size, bold=True):
    size = max(1, int(size))
    try:
        return ImageFont.truetype(FONT_BOLD, size, index=1 if bold else 0)
    except:
        return ImageFont.truetype(FONT_BOLD, size)

# ── 6 Multi-segment narratives ──
# Each = 3-5 segments from source transcript, targeting 30-50s TTS
NARRATIVES = [
    {
        "id": "n1",
        "hook": "FROM $12K TO BILLION",
        "punchlines": {"$12,000", "$7", "$695", "10", "years", "quit", "billion", "money", "empire"},
        "full_text": "We started with twelve thousand dollars. No investors, no help, nothing. First day we sold seven dollars. Seven dollars. For ten years we made six hundred and ninety five dollars a month on average. Most people would have quit. Most people did quit. But we kept going. And then something happened. All that grinding, all that rejection, it built momentum. It became a billion dollar company. A real legit billion dollar empire.",
    },
    {
        "id": "n2",
        "hook": "FIRING PEOPLE IS KIND",
        "punchlines": {"fire", "holding", "back", "trash", "meanest", "potential", "great", "cruel"},
        "full_text": "If you don't fire them, you're holding them back from what they could be great at. You are keeping them in a place where they are trash. That is the meanest thing you can do to somebody. When I was younger in business, it was a really hard thing to fire people. Until I realized that by not firing them, I was denying their potential. Let them go. Let them find what they are great at. That's the kindest thing you can do. It sounds harsh but it's the truth. And truth is always kinder than a comfortable lie.",
    },
    {
        "id": "n3",
        "hook": "DISCIPLINE IS A BANK ACCOUNT",
        "punchlines": {"discipline", "bank", "deposit", "withdrawal", "broke", "gym", "standard", "consistent"},
        "full_text": "Think about discipline as a bank account. Every time you do something you said you were going to do, you make a deposit. Every time you don't, you make a withdrawal. If your balance is zero, you are broke. And if you are broke, you can't build anything. The same discipline that gets you to the gym at five AM is the same discipline that gets you to show up for your business. It is not about motivation. Motivation comes and goes. It is about standard. When you have a standard, you don't need motivation. You just execute.",
    },
    {
        "id": "n4",
        "hook": "REJECTION BUILT THIS EMPIRE",
        "punchlines": {"no", "rejection", "forced", "vertical", "empire", "foundation", "zero", "built"},
        "full_text": "They told him no. Every single person told him no. The banks said no. The investors said no. Even his friends said no. That rejection forced him to build something vertical. He had no choice but to grind harder, to innovate, to find a way where there was no way. In two thousand and twelve, that company became an empire. Every single no was a brick in the foundation. He would not be here without rejection. Rejection is not a stop sign. It is a detour.",
    },
    {
        "id": "n5",
        "hook": "BUGATTI IN ONE MONTH",
        "punchlines": {"Bugatti", "month", "systems", "trading", "time", "money", "rich", "wealthy", "passive"},
        "full_text": "This is the Bugatti. He made enough money in one single month to buy this car. How? Not by working harder. Not by trading more time for money. By building systems that work without him. He is not trading time for money. He is trading leverage for money. That is the difference between rich and wealthy. Rich people work for money. Wealthy people build systems that create money while they sleep. You cannot buy a Bugatti by working a job. You can only buy a Bugatti by owning assets.",
    },
    {
        "id": "n6",
        "hook": "FITNESS = FINANCIAL SUCCESS",
        "punchlines": {"fitness", "financial", "success", "correlation", "discipline", "mutual", "suffering", "equal"},
        "full_text": "Have you seen the correlation between physical fitness and financial success? Absolutely. Huge correlation. The bigger thing is mutual suffering. When everybody trains together, when everybody struggles together, something happens. You see people who are dying on the floor, and the person next to them is a boss in the company. But out here they are equal. The same discipline it takes to show up at five AM is the same discipline it takes to show up for your business. Your body and your bank account are built by the same habit. You cannot separate them.",
    },
]

# Hook patterns
def get_hook_text(hook_type, narrative):
    if hook_type == "context":
        return narrative["hook"]
    elif hook_type == "contrarian":
        cmap = {
            "FROM $12K TO BILLION": "10 YEARS OF FAILURE MADE HIM A BILLIONAIRE.",
            "FIRING PEOPLE IS KIND": "NOT FIRING IS THE CRUELEST THING.",
            "DISCIPLINE IS A BANK ACCOUNT": "MOTIVATION IS A LIE. DISCIPLINE WINS.",
            "REJECTION BUILT THIS EMPIRE": "EVERY 'NO' MADE HIM RICHER.",
            "BUGATTI IN ONE MONTH": "YOU CAN'T AFFORD IT BECAUSE YOU WORK FOR MONEY.",
            "FITNESS = FINANCIAL SUCCESS": "LAZY BODY = EMPTY WALLET.",
        }
        return cmap.get(narrative["hook"], narrative["hook"])
    else:  # intrigue
        imap = {
            "FROM $12K TO BILLION": "HOW DO YOU TURN $12K INTO A BILLION?",
            "FIRING PEOPLE IS KIND": "WHY IS FIRING THE KINDEST THING?",
            "DISCIPLINE IS A BANK ACCOUNT": "WHAT IS YOUR DISCIPLINE BALANCE?",
            "REJECTION BUILT THIS EMPIRE": "WHAT HAPPENS WHEN EVERYONE SAYS NO?",
            "BUGATTI IN ONE MONTH": "WHAT DOES IT TAKE TO BUY A BUGATTI?",
            "FITNESS = FINANCIAL SUCCESS": "IS YOUR GYM MEMBERSHIP COSTING YOU MILLIONS?",
        }
        return imap.get(narrative["hook"], narrative["hook"])


async def gen_tts(text, out_path):
    """Generate TTS + SentenceBoundary timings."""
    comm = edge_tts.Communicate(text, VOICE, rate=RATE)
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
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", out_path],
        capture_output=True, text=True
    )
    dur = float(json.loads(result.stdout)["format"]["duration"])
    return dur, boundaries


# ── Value-add renderers ──
def draw_fact_check(frame, t, seg_start, seg_end, draw):
    pr = (t - seg_start) / max(0.1, seg_end - seg_start)
    if 0.2 <= pr <= 0.5:
        draw.rounded_rectangle([50, 1400, 500, 1480], radius=10, fill=(0, 100, 200))
        draw.text((70, 1410), "FACT CHECK", font=font(28), fill=C_WHITE)

def draw_data_viz(frame, t, seg_start, seg_end, draw):
    pr = (t - seg_start) / max(0.1, seg_end - seg_start)
    if 0.2 <= pr <= 0.6:
        val = int(450 * min(1.0, (pr - 0.2) / 0.3))
        draw.text((WIDTH // 2 - 100, 400), f"${val}B", font=font(100), fill=C_GREEN)

def draw_counter_arg(frame, t, seg_start, seg_end, draw):
    pr = (t - seg_start) / max(0.1, seg_end - seg_start)
    if 0.3 <= pr <= 0.65:
        draw.rounded_rectangle([50, 1400, 1030, 1520], radius=15, fill=(200, 50, 50))
        draw.text((100, 1420), "BUT HERE'S THE TRUTH:", font=font(36), fill=C_WHITE)

def draw_source_cite(frame, t, seg_start, seg_end, draw):
    pr = (t - seg_start) / max(0.1, seg_end - seg_start)
    if 0.3 <= pr <= 0.6:
        draw.rounded_rectangle([50, 1750, 400, 1820], radius=8, fill=(40, 40, 60))
        draw.text((70, 1760), "SOURCE: Andy Frisella", font=font(24), fill=(180, 180, 200))

def draw_annotation(frame, t, seg_start, seg_end, draw):
    pr = (t - seg_start) / max(0.1, seg_end - seg_start)
    if 0.2 <= pr <= 0.5:
        ax = int(800 + 100 * math.sin(t * 5))
        draw.line([(ax, 600), (ax + 80, 600)], fill=C_GOLD, width=6)
        draw.polygon([(ax + 80, 600), (ax + 65, 590), (ax + 65, 610)], fill=C_GOLD)
        draw.text((ax + 90, 580), "KEY POINT", font=font(24), fill=C_GOLD)

def draw_this_or_that(frame, t, seg_start, seg_end, draw):
    pr = (t - seg_start) / max(0.1, seg_end - seg_start)
    if 0.25 <= pr <= 0.55:
        mx = WIDTH // 2
        draw.line([(mx, 1400), (mx, 1550)], fill=C_CYAN, width=4)
        draw.text((150, 1420), "A: QUIT", font=font(40), fill=C_RED)
        draw.text((600, 1420), "B: PUSH", font=font(40), fill=C_GREEN)

def draw_split_screen(frame, t, seg_start, seg_end, draw):
    pr = (t - seg_start) / max(0.1, seg_end - seg_start)
    if 0.2 <= pr <= 0.6:
        draw.rectangle([0, 1350, 530, 1550], fill=(60, 20, 20))
        draw.text((100, 1400), "POOR", font=font(40), fill=C_RED)
        draw.rectangle([550, 1350, 1080, 1550], fill=(20, 60, 20))
        draw.text((700, 1400), "RICH", font=font(40), fill=C_GREEN)

def draw_timeline(frame, t, seg_start, seg_end, draw):
    pr = (t - seg_start) / max(0.1, seg_end - seg_start)
    if 0.15 <= pr <= 0.7:
        bar_y = 1400; bar_w = 800; bx = (WIDTH - bar_w) // 2
        draw.rounded_rectangle([bx, bar_y, bx + bar_w, bar_y + 20], radius=10, fill=(40, 40, 60))
        fw = int(bar_w * pr)
        draw.rounded_rectangle([bx, bar_y, bx + fw, bar_y + 20], radius=10, fill=C_GOLD)
        for i, lb in enumerate(["D1", "Y5", "Y10", "$1B"]):
            mx = bx + int(bar_w * i / 3)
            draw.ellipse([mx - 8, bar_y - 4, mx + 8, bar_y + 24], fill=C_GOLD)
            draw.text((mx - 15, bar_y + 30), lb, font=font(20), fill=C_WHITE)

VA_RENDERERS = {
    "fact_check_callout": draw_fact_check,
    "data_viz_overlay": draw_data_viz,
    "counter_argument": draw_counter_arg,
    "source_citation": draw_source_cite,
    "animated_annotation": draw_annotation,
    "this_or_that_overlay": draw_this_or_that,
    "split_screen_comparison": draw_split_screen,
    "timeline_overlay": draw_timeline,
}


def ease_out(t):
    return 1 - (1 - t) ** 3


# ── Renderers ──
def render_kinetic(narrative, hook_text, audio_path, dur, boundaries, vas, out):
    """Type 2: Text animation on dark gradient with pattern interrupts."""
    fd = TMPDIR / f"{narrative['id']}_kinetic"; fd.mkdir(exist_ok=True)
    tf = int(dur * FPS)
    seg_dur = dur / 3  # Each segment gets equal time

    for i in range(tf):
        t = i / FPS
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)

        # Pattern interrupt: alternate bg color every segment
        seg_idx = min(int(t / seg_dur), 3 - 1)
        if seg_idx % 2 == 0:
            colors = [C_DARK_BG, (22, 33, 62)]
        else:
            colors = [(30, 15, 40), (46, 20, 60)]
        for y in range(HEIGHT):
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * y / HEIGHT)
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * y / HEIGHT)
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * y / HEIGHT)
            draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

        # Hook (first 3s)
        if t < 3.0:
            scale = min(1.0, t / 0.3) if t < 0.3 else 1.0 + 0.02 * math.sin((t - 0.3) * 4)
            fnt = font(int(80 * scale))
            bbox = draw.textbbox((0, 0), hook_text, font=fnt)
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw) // 2, 300), hook_text, font=fnt, fill=C_GOLD)

        # Body text from boundaries
        for b in boundaries:
            if b["offset"] <= t <= b["offset"] + b["duration"]:
                words = b["text"].split()
                for wi, w in enumerate(words):
                    wt = b["offset"] + wi * (b["duration"] / max(len(words), 1))
                    if wt <= t <= wt + 0.5:
                        sc = min(1.0, (t - wt) / 0.15) if t - wt < 0.15 else 1.0
                        fnt = font(int(60 * sc))
                        is_punch = w.lower().strip(".,!?\"'") in narrative["punchlines"]
                        col = C_CYAN if is_punch else C_WHITE
                        yp = 800 + (wi % 6) * 80
                        bbox = draw.textbbox((0, 0), w, font=fnt)
                        tw = bbox[2] - bbox[0]
                        draw.text(((WIDTH - tw) // 2, yp), w, font=fnt, fill=col)
                break

        # Value-adds
        for va in vas:
            r = VA_RENDERERS.get(va)
            if r: r(img, t, 3.0, dur, draw)

        bar_w = int(WIDTH * t / dur)
        draw.rectangle([0, HEIGHT - 10, bar_w, HEIGHT], fill=C_CYAN)
        img.save(fd / f"frame_{i+1:05d}.png")
    encode_frames(fd, audio_path, out, dur)


def render_data_viz(narrative, hook_text, audio_path, dur, boundaries, vas, out):
    """Type 3: Data viz. Numbers counter + bar charts per segment."""
    fd = TMPDIR / f"{narrative['id']}_dataviz"; fd.mkdir(exist_ok=True)
    tf = int(dur * FPS)
    seg_dur = dur / 3

    for i in range(tf):
        t = i / FPS
        img = Image.new("RGB", (WIDTH, HEIGHT), C_BLACK)
        draw = ImageDraw.Draw(img)
        # Grid
        for gx in range(0, WIDTH, 60): draw.line([(gx, 0), (gx, HEIGHT)], fill=(25, 25, 35), width=1)
        for gy in range(0, HEIGHT, 60): draw.line([(0, gy), (WIDTH, gy)], fill=(25, 25, 35), width=1)

        if t < 3.0:
            scale = min(1.0, t / 0.3)
            bbox = draw.textbbox((0, 0), hook_text, font=font(int(70 * scale)))
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw) // 2, 200), hook_text, font=font(int(70 * scale)), fill=C_GREEN)

        # Counter per segment
        seg_idx = min(int(t / seg_dur), 3 - 1)
        seg_start_t = seg_idx * seg_dur
        pr = min(1.0, (t - seg_start_t) / seg_dur)
        val = int(9999 * pr)
        draw.text((WIDTH // 2 - 160, 600), f"${val:,}", font=font(120), fill=C_GOLD)

        # Bar
        bh = int(300 * pr)
        draw.rounded_rectangle([WIDTH // 2 - 100, HEIGHT - 400 - bh, WIDTH // 2 + 100, HEIGHT - 400], radius=15, fill=C_GREEN)

        for va in vas:
            r = VA_RENDERERS.get(va)
            if r: r(img, t, 3.0, dur, draw)

        bar_w = int(WIDTH * t / dur)
        draw.rectangle([0, HEIGHT - 10, bar_w, HEIGHT], fill=C_CYAN)
        img.save(fd / f"frame_{i+1:05d}.png")
    encode_frames(fd, audio_path, out, dur)


def render_whiteboard(narrative, hook_text, audio_path, dur, boundaries, vas, out):
    """Type 5: Cream BG, sketchy handwriting style."""
    fd = TMPDIR / f"{narrative['id']}_wb"; fd.mkdir(exist_ok=True)
    tf = int(dur * FPS)
    BG, INK, HL = (253, 246, 227), (44, 62, 80), (255, 193, 7)

    for i in range(tf):
        t = i / FPS
        img = Image.new("RGB", (WIDTH, HEIGHT), BG)
        draw = ImageDraw.Draw(img)
        if t < 3.0:
            scale = min(1.0, t / 0.5)
            bbox = draw.textbbox((0, 0), hook_text, font=font(int(60 * scale)))
            tw = bbox[2] - bbox[0]
            draw.rectangle([(WIDTH - tw) // 2 - 20, 250, (WIDTH + tw) // 2 + 20, 330], fill=HL)
            draw.text(((WIDTH - tw) // 2, 260), hook_text, font=font(int(60 * scale)), fill=INK)
        # Body
        for b in boundaries:
            if b["offset"] <= t <= b["offset"] + b["duration"]:
                words = b["text"].split()
                for wi, w in enumerate(words):
                    wt = b["offset"] + wi * (b["duration"] / max(len(words), 1))
                    if wt <= t:
                        is_punch = w.lower().strip(".,!?\"'") in narrative["punchlines"]
                        col = C_RED if is_punch else INK
                        fnt = font(50 if is_punch else 44)
                        yp = 700 + (wi % 6) * 70
                        draw.text((100, yp), w, font=fnt, fill=col)
                break
        for va in vas:
            r = VA_RENDERERS.get(va)
            if r: r(img, t, 3.0, dur, draw)
        bar_w = int(WIDTH * t / dur)
        draw.rectangle([0, HEIGHT - 10, bar_w, HEIGHT], fill=INK)
        img.save(fd / f"frame_{i+1:05d}.png")
    encode_frames(fd, audio_path, out, dur)


def render_meme(narrative, hook_text, audio_path, dur, boundaries, vas, out):
    """Type 6: Fast cuts, bold text, bg color change per segment."""
    fd = TMPDIR / f"{narrative['id']}_meme"; fd.mkdir(exist_ok=True)
    tf = int(dur * FPS)
    seg_dur = dur / 3

    for i in range(tf):
        t = i / FPS
        seg_idx = min(int(t / seg_dur), 3 - 1)
        bg = C_DARK_BG if seg_idx % 2 == 0 else (46, 20, 60)
        img = Image.new("RGB", (WIDTH, HEIGHT), bg)
        draw = ImageDraw.Draw(img)

        if t < 3.0:
            scale = min(1.0, t / 0.2) if t < 0.2 else 1.0 + 0.05 * math.sin((t - 0.2) * 8)
            bbox = draw.textbbox((0, 0), hook_text, font=font(int(90 * scale)))
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw) // 2, 400), hook_text, font=font(int(90 * scale)), fill=C_CYAN)

        for b in boundaries:
            if b["offset"] <= t <= b["offset"] + b["duration"]:
                words = b["text"].split()
                for wi, w in enumerate(words):
                    wt = b["offset"] + wi * (b["duration"] / max(len(words), 1))
                    if wt <= t <= wt + 0.4:
                        is_punch = w.lower().strip(".,!?\"'") in narrative["punchlines"]
                        sz = 80 if is_punch else 60
                        col = C_GOLD if is_punch else C_WHITE
                        sc = min(1.0, (t - wt) / 0.1) if t - wt < 0.1 else 1.0
                        bbox = draw.textbbox((0, 0), w, font=font(int(sz * sc)))
                        tw = bbox[2] - bbox[0]
                        draw.text(((WIDTH - tw) // 2, 800 + (wi % 3) * 100), w, font=font(int(sz * sc)), fill=col)
                break
        for va in vas:
            r = VA_RENDERERS.get(va)
            if r: r(img, t, 3.0, dur, draw)
        bar_w = int(WIDTH * t / dur)
        draw.rectangle([0, HEIGHT - 10, bar_w, HEIGHT], fill=C_CYAN)
        img.save(fd / f"frame_{i+1:05d}.png")
    encode_frames(fd, audio_path, out, dur)


def render_stock(narrative, hook_text, audio_path, dur, boundaries, vas, out):
    """Type 1: Source video as darkened background + Ken Burns zoom/pan."""
    fd = TMPDIR / f"{narrative['id']}_stock"; fd.mkdir(exist_ok=True)
    tf = int(dur * FPS)
    src = PROJECT / "output/source/2eicF3iPf1s.webm"
    src_fd = TMPDIR / f"{narrative['id']}_src"; src_fd.mkdir(exist_ok=True)
    # Extract at 5fps for smoother motion (was 1fps)
    subprocess.run(["ffmpeg", "-y", "-i", str(src), "-vf", f"fps=5,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", "-q:v", "2", str(src_fd / "src_%05d.jpg")], capture_output=True)
    sf = sorted(src_fd.glob("src_*.jpg"))
    src_count = len(sf)

    for i in range(tf):
        t = i / FPS
        if sf:
            # Smooth scrubbing: cycle through source frames proportional to video duration
            fi = int((t / dur) * src_count) % src_count
            bg = Image.open(sf[fi]).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        else:
            bg = Image.new("RGB", (WIDTH, HEIGHT), C_BLACK)
        overlay = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        bg = Image.blend(bg, overlay, 0.4)
        # Ken Burns zoom: 1.0 → 1.1 across full duration
        zoom = 1.0 + 0.1 * (t / dur)
        bw, bh = int(WIDTH / zoom), int(HEIGHT / zoom)
        bx, by = (WIDTH - bw) // 2, int(HEIGHT * 0.2 * (t / dur))  # pan down
        cropped = bg.crop((bx, by, bx + bw, by + bh)).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(cropped)

        if t < 3.0:
            scale = min(1.0, t / 0.3)
            bbox = draw.textbbox((0, 0), hook_text, font=font(int(70 * scale)))
            tw = bbox[2] - bbox[0]
            draw.rectangle([(WIDTH - tw) // 2 - 20, 200, (WIDTH + tw) // 2 + 20, 290], fill=(0, 0, 0))
            draw.text(((WIDTH - tw) // 2, 210), hook_text, font=font(int(70 * scale)), fill=C_GOLD)

        for b in boundaries:
            if b["offset"] <= t <= b["offset"] + b["duration"]:
                words = b["text"].split()
                for wi, w in enumerate(words):
                    wt = b["offset"] + wi * (b["duration"] / max(len(words), 1))
                    if wt <= t <= wt + 0.5:
                        is_punch = w.lower().strip(".,!?\"'") in narrative["punchlines"]
                        sz = 60 if is_punch else 48
                        col = C_CYAN if is_punch else C_WHITE
                        bbox = draw.textbbox((0, 0), w, font=font(sz))
                        tw = bbox[2] - bbox[0]
                        draw.text(((WIDTH - tw) // 2, 800 + (wi % 5) * 75), w, font=font(sz), fill=col)
                break
        for va in vas:
            r = VA_RENDERERS.get(va)
            if r: r(cropped, t, 3.0, dur, draw)
        bar_w = int(WIDTH * t / dur)
        draw.rectangle([0, HEIGHT - 10, bar_w, HEIGHT], fill=C_CYAN)
        cropped.save(fd / f"frame_{i+1:05d}.png")
    encode_frames(fd, audio_path, out, dur)
    shutil.rmtree(src_fd, ignore_errors=True)


def render_clip(narrative, hook_text, audio_path, dur, boundaries, vas, out):
    """Type 7: Source footage cut + TTS overlay + Ken Burns."""
    fd = TMPDIR / f"{narrative['id']}_clip"; fd.mkdir(exist_ok=True)
    tf = int(dur * FPS)
    src = PROJECT / "output/source/2eicF3iPf1s.webm"
    src_fd = TMPDIR / f"{narrative['id']}_src"; src_fd.mkdir(exist_ok=True)
    src_total = 1152.0

    # Extract 6 segments from different parts of source (was 3)
    num_segs = 6
    seg_dur = dur / num_segs
    src_segments = []
    for si in range(num_segs):
        t_pos = (si + 1) * (src_total / (num_segs + 1))
        subprocess.run([
            "ffmpeg", "-y", "-ss", str(t_pos), "-i", str(src),
            "-t", "3", "-vf", f"fps={FPS},scale=608:1080",
            "-q:v", "2", str(src_fd / f"src_{si:02d}_%05d.png")
        ], capture_output=True)
        seg_frames = sorted(src_fd.glob(f"src_{si:02d}_*.png"))
        src_segments.append(seg_frames)

    for i in range(tf):
        t = i / FPS
        seg_idx = min(int(t / seg_dur), num_segs - 1)
        local_t = t - seg_idx * seg_dur

        # Get source frame
        seg_frames = src_segments[seg_idx]
        if seg_frames:
            fi = min(int(local_t * FPS), len(seg_frames) - 1)
            fg = Image.open(seg_frames[fi])
        else:
            fg = Image.new("RGB", (608, 1080), C_BLACK)

        bg = fg.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=30))
        darken = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        bg = Image.blend(bg, darken, 0.35)
        # Ken Burns zoom on foreground
        zoom = 1.0 + 0.08 * (local_t / seg_dur)
        fw = int(HEIGHT * 608 / 1080 * zoom)
        fh = int(HEIGHT * zoom)
        fg_zoomed = fg.resize((fw, fh), Image.Resampling.LANCZOS)
        bg.paste(fg_zoomed, ((WIDTH - fw) // 2, (HEIGHT - fh) // 2))
        # Crossfade between segments (last 0.3s of each segment)
        seg_progress = local_t / seg_dur
        if seg_progress > 0.85 and seg_idx < num_segs - 1:
            fade_alpha = (seg_progress - 0.85) / 0.15
            bg = Image.blend(bg, Image.new("RGB", (WIDTH, HEIGHT), C_BLACK), fade_alpha * 0.3)
        draw = ImageDraw.Draw(bg)

        if t < 3.0:
            scale = min(1.0, t / 0.3)
            bbox = draw.textbbox((0, 0), hook_text, font=font(int(56 * scale)))
            tw = bbox[2] - bbox[0]
            draw.rectangle([(WIDTH - tw) // 2 - 15, 100, (WIDTH + tw) // 2 + 15, 180], fill=(0, 0, 0))
            draw.text(((WIDTH - tw) // 2, 110), hook_text, font=font(int(56 * scale)), fill=C_GOLD)

        for va in vas:
            r = VA_RENDERERS.get(va)
            if r: r(bg, t, 3.0, dur, draw)

        bar_w = int(WIDTH * t / dur)
        draw.rectangle([0, HEIGHT - 10, bar_w, HEIGHT], fill=C_CYAN)
        bg.save(fd / f"frame_{i+1:05d}.png")

    encode_frames(fd, audio_path, out, dur)
    shutil.rmtree(src_fd, ignore_errors=True)


def render_html(narrative, hook_text, audio_path, dur, boundaries, vas, out):
    """Type 4: Glassmorphism card style (fallback: styled text)."""
    fd = TMPDIR / f"{narrative['id']}_html"; fd.mkdir(exist_ok=True)
    tf = int(dur * FPS)
    seg_dur = dur / 3

    for i in range(tf):
        t = i / FPS
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        for y in range(HEIGHT):
            r = int(102 + (118 - 102) * y / HEIGHT)
            g = int(126 + (74 - 126) * y / HEIGHT)
            b = int(234 + (162 - 234) * y / HEIGHT)
            draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

        cm, ct, cb = 80, 400, 1500
        card = Image.new("RGBA", (WIDTH - 2 * cm, cb - ct), (255, 255, 255, 40))
        img.paste(card, (cm, ct), card)
        draw = ImageDraw.Draw(img)

        if t < 3.0:
            scale = min(1.0, t / 0.4)
            bbox = draw.textbbox((0, 0), hook_text, font=font(int(64 * scale)))
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw) // 2, 500), hook_text, font=font(int(64 * scale)), fill=C_WHITE)

        for b in boundaries:
            if b["offset"] <= t <= b["offset"] + b["duration"]:
                words = b["text"].split()
                for wi, w in enumerate(words):
                    wt = b["offset"] + wi * (b["duration"] / max(len(words), 1))
                    if wt <= t <= wt + 0.5:
                        is_punch = w.lower().strip(".,!?\"'") in narrative["punchlines"]
                        col = C_GOLD if is_punch else (240, 240, 240)
                        sz = 56 if is_punch else 44
                        yp = 700 + (wi % 6) * 80
                        bbox = draw.textbbox((0, 0), w, font=font(sz))
                        tw = bbox[2] - bbox[0]
                        draw.text(((WIDTH - tw) // 2, yp), w, font=font(sz), fill=col)
                break
        for va in vas:
            r = VA_RENDERERS.get(va)
            if r: r(img, t, 3.0, dur, draw)
        bar_w = int(WIDTH * t / dur)
        draw.rectangle([0, HEIGHT - 10, bar_w, HEIGHT], fill=C_CYAN)
        img.save(fd / f"frame_{i+1:05d}.png")
    encode_frames(fd, audio_path, out, dur)


RENDERERS = {
    "kinetic_typography": render_kinetic,
    "data_viz": render_data_viz,
    "whiteboard_sketch": render_whiteboard,
    "meme_notification": render_meme,
    "stock_footage": render_stock,
    "clip_curation_edit": render_clip,
    "html_css_motion": render_html,
}


def encode_frames(fd, audio_path, out, dur):
    cmd = ["ffmpeg", "-y", "-framerate", str(FPS), "-i", str(fd / "frame_%05d.png"),
           "-i", str(audio_path), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "15",
           "-c:a", "aac", "-b:a", "128k", "-shortest", "-t", str(dur), "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, capture_output=True, check=True)
    shutil.rmtree(fd, ignore_errors=True)
    mb = os.path.getsize(out) / 1024 / 1024
    print(f"    ✅ {out.name} ({dur:.1f}s, {mb:.1f}MB)")


def render_variant(variant, narrative, idx):
    vid = f"exp{idx:02d}_{variant['name'][:40]}"
    print(f"\n{'='*60}")
    print(f"  [{idx}/6] {vid}")
    print(f"  Narrative: {narrative['id']}")
    print(f"  Type: {variant['video_type']} | Hook: {variant['hook_type']} | VAs: {variant['value_add']}")

    hook_text = get_hook_text(variant["hook_type"], narrative)
    audio_path = TMPDIR / f"{vid}.mp3"
    print(f"  TTS ({len(narrative['full_text'].split())} words)...")
    dur, bounds = asyncio.run(gen_tts(narrative["full_text"], str(audio_path)))
    print(f"  TTS: {dur:.1f}s, {len(bounds)} sentences")

    if dur < 30:
        print(f"  ⚠️  Only {dur:.1f}s — need 30-60s, padding text...")
        # Repeat full text with connecting phrase
        narrative["full_text"] = narrative["full_text"] + " Let me repeat that. " + narrative["full_text"]
        dur, bounds = asyncio.run(gen_tts(narrative["full_text"], str(audio_path)))
        print(f"  TTS (padded): {dur:.1f}s, {len(bounds)} sentences")

    renderer = RENDERERS.get(variant["video_type"])
    if not renderer:
        print(f"  SKIP: no renderer for {variant['video_type']}")
        return None

    out = OUTDIR / f"{vid}.mp4"
    print(f"  Rendering {variant['video_type']} ({dur:.1f}s)...")
    renderer(narrative, hook_text, str(audio_path), dur, bounds, variant["value_add"], out)
    audio_path.unlink(missing_ok=True)
    return out


# ── Main ──
if __name__ == "__main__":
    vp = PROJECT / "output" / "random_variants_v3.json"
    variants = json.loads(vp.read_text())

    print(f"🎮 Multi-Segment Exploration v4 — {len(variants)} variants")
    print(f"   Target: 30-60s each | Output: {OUTDIR}")

    results = []
    for idx, variant in enumerate(variants, 1):
        narrative = NARRATIVES[(idx - 1) % len(NARRATIVES)]
        try:
            out = render_variant(variant, narrative, idx)
            if out: results.append(out)
        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\n{'='*60}")
    print(f"✅ {len(results)}/{len(variants)} rendered")
    for p in results:
        d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.strip()
        print(f"  {p.name} ({float(d):.1f}s, {p.stat().st_size/1024/1024:.1f}MB)")
