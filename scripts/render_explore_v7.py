#!/usr/bin/env python3
"""
Hybrid Renderer v7.3 — SoHK Patterns + Footage + Pexels + Text + Emoji.
Kết hợp:
  - v6: footage extraction (Andy nói chuyện, Ken Burns zoom)
  - v4: Pexels stock clips + emoji overlays
  - v7: SoHK narrative patterns (Money+Number, Curiosity, Contrarian)

Visual layering per frame:
  Hook phase  → darkened source footage + Pexels + big hook text
  Segment phase → source footage + word-by-word caption
  CTA phase   → Pexels + CTA text + emoji
"""
import json, subprocess, asyncio, random, shutil, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import edge_tts

PROJECT  = Path("/Users/hung/code/ai/shorts")
OUTDIR   = PROJECT / "output" / "explore_v7"
OUTDIR.mkdir(parents=True, exist_ok=True)
TMPDIR   = PROJECT / "output" / "tmp_explore7"
TMPDIR.mkdir(parents=True, exist_ok=True)

SRC_MP4   = str(PROJECT / "output/source/2eicF3iPf1s.mp4")
SRC_AUDIO = TMPDIR / "source_full.wav"
PEXELS_DIR = PROJECT / "output" / "pexels"

FPS   = 30
WIDTH  = 1080
HEIGHT = 1920
AUDIO_PARAMS = ["-ac", "1", "-ar", "44100"]

# Colors
C_BLACK  = (0, 0, 0)
C_WHITE  = (255, 255, 255)
C_GOLD   = (255, 215, 0)
C_CYAN   = (0, 200, 255)
C_RED    = (255, 68, 68)
C_GREEN  = (0, 255, 136)
C_DARK   = (10, 10, 14)

FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_REG  = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_ROUND = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"

def font(size, path=FONT_BOLD):
    try:
        return ImageFont.truetype(path, max(1, int(size)))
    except:
        return ImageFont.load_default()

# ── Pexels clips ──
PEXELS_CLIPS = sorted(PEXELS_DIR.glob("pex_*.mp4"))

def pexel_frames_for_range(path, start, dur, n_frames):
    """Extract n_frames from a Pexels clip at given offset."""
    frames = []
    fd = TMPDIR / f"pex_{path.stem}_{start:.0f}"
    fd.mkdir(exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(start), "-i", str(path),
        "-t", str(dur),
        "-vf", f"fps={FPS},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-an", "-q:v", "2", str(fd / "f_%05d.jpg")
    ], capture_output=True)
    frames = sorted(fd.glob("*.jpg"))
    return [str(f) for f in frames], fd

# ── Source footage extraction ──
def extract_source_frames(start_window, end_window, vid_id):
    """Extract source video frames (Andy Frisella) at 10fps."""
    src_fd = TMPDIR / f"{vid_id}_src"
    src_fd.mkdir(exist_ok=True)
    # Clear stale frames
    for f in src_fd.glob("*.jpg"):
        f.unlink()
    dur = end_window - start_window
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(start_window), "-i", SRC_MP4,
        "-t", str(dur),
        "-vf", "fps=10,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-an", "-q:v", "2", str(src_fd / "f_%05d.jpg")
    ], capture_output=True)
    return sorted(src_fd.glob("*.jpg")), src_fd

# ── TTS ──
async def gen_tts(text, out_path):
    out_path = Path(out_path) if not isinstance(out_path, Path) else out_path
    comm = edge_tts.Communicate(text, "en-US-GuyNeural")
    tmp_mp3 = out_path.with_suffix(".mp3")
    await comm.save(str(tmp_mp3))
    subprocess.run([
        "ffmpeg", "-y", "-i", str(tmp_mp3),
        "-ac", "1", "-ar", "44100", str(out_path)
    ], capture_output=True)
    tmp_mp3.unlink(missing_ok=True)
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(out_path)], capture_output=True, text=True)
    return float(r.stdout.strip()) if r.stdout.strip() else 0

def get_duration(path):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return float(r.stdout.strip()) if r.stdout.strip() else 0

def ensure_source_audio():
    if not SRC_AUDIO.exists():
        subprocess.run([
            "ffmpeg", "-y", "-i", SRC_MP4, *AUDIO_PARAMS, str(SRC_AUDIO)
        ], capture_output=True)

# ── Helpers ──
def get_segment_text(start, end):
    with open(str(PROJECT / "output/source/2eic_transcript.json")) as f:
        data = json.load(f)
    texts = []
    for s in data.get("segments", []):
        if s["start"] >= start - 0.5 and s["end"] <= end + 0.5:
            texts.append(s["text"].strip())
    if not texts:
        for s in data.get("segments", []):
            if s["start"] < end and s["end"] > start:
                texts.append(s["text"].strip())
    return " ".join(texts) if texts else ""

def word_wrap(text, draw, font_obj, max_width):
    words = text.split()
    lines = []
    current = ""
    for w in words:
        test = current + " " + w if current else w
        bbox = draw.textbbox((0, 0), test, font=font_obj)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(current)
            current = w
        else:
            current = test
    if current:
        lines.append(current)
    return lines

# ── Frame renderer ──
def render_frame(bg_img, texts, y_start=400, font_size=52, color=C_WHITE, phase="seg"):
    """Overlay text on background image."""
    draw = ImageDraw.Draw(bg_img)
    fo = font(font_size)

    total_h = 0
    wrapped_all = []
    for txt in texts:
        lines = word_wrap(txt, draw, fo, WIDTH - 160)
        for l in lines:
            bbox = draw.textbbox((0, 0), l, font=fo)
            lh = bbox[3] - bbox[1]
            total_h += lh + 16
            wrapped_all.append(l)

    cy = y_start - total_h // 2
    for l in wrapped_all:
        bbox = draw.textbbox((0, 0), l, font=fo)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        x = (WIDTH - lw) // 2
        # Shadow
        draw.text((x + 3, cy + 3), l, font=fo, fill=(0, 0, 0))
        draw.text((x, cy), l, font=fo, fill=color)
        cy += lh + 16

    return bg_img

def add_progress_bar(img, progress, color=C_CYAN):
    draw = ImageDraw.Draw(img)
    bar_w = int(WIDTH * progress)
    draw.rectangle([0, HEIGHT - 6, bar_w, HEIGHT], fill=color)

def add_emoji(img, emoji_str, x, y, size=80):
    """Add emoji as large text."""
    draw = ImageDraw.Draw(img)
    fo = font(size, FONT_ROUND)
    draw.text((x, y), emoji_str, font=fo, fill=C_WHITE)

def apply_ken_burns(img, t, total_dur, zoom_max=1.04):
    """Subtle zoom effect."""
    zoom = 1.0 + zoom_max * (t / total_dur)
    bw = int(WIDTH / zoom)
    bh = int(HEIGHT / zoom)
    bx = (WIDTH - bw) // 2
    by = int((HEIGHT - bh) * 0.15 * (t / total_dur))
    return img.crop((bx, by, bx + bw, by + bh)).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

def darken(img, factor=0.4):
    overlay = Image.new("RGB", img.size, C_BLACK)
    return Image.blend(img, overlay, factor)

# ═══════════════════════════════════════════════════════════════
# 6 NARRATIVES — SoHK Patterns
# ═══════════════════════════════════════════════════════════════
NARRATIVES = [
    {
        "id": "new1_10year",
        "mode": "A",
        "hook": "HE MADE $58,380 IN 10 YEARS",
        "hook_tts": "He made fifty eight thousand three hundred and eighty dollars in ten years. And that changed everything.",
        "emoji": "💰",
        "segments": [
            {"start": 957.0, "end": 962.2},
            {"start": 962.2, "end": 967.5},
            {"start": 969.0, "end": 975.0},
            {"start": 977.0, "end": 982.5},
        ],
        "cta_tts": "That's the power of compounding. The first ten years feel like nothing. The next ten change your life.",
        "pexel_keywords": ["money", "cash", "business"],
    },
    {
        "id": "new2_secret",
        "mode": "A",
        "hook": "THIS IS THE REAL SECRET OF SUCCESS",
        "hook_tts": "Everyone wants the secret. Well here it is. This is the real secret of success.",
        "emoji": "🎯",
        "segments": [
            {"start": 389.0, "end": 394.5},
            {"start": 396.0, "end": 401.5},
            {"start": 403.0, "end": 408.5},
            {"start": 410.0, "end": 415.5},
        ],
        "cta_tts": "The secret isn't talent. It isn't luck. It's showing up every single day when nobody's watching.",
        "pexel_keywords": ["success", "goal", "focus"],
    },
    {
        "id": "new3_culture",
        "mode": "A",
        "hook": "GOOD CULTURE ISN'T MADE IN THE GAME",
        "hook_tts": "Good culture isn't made in the game. It's made in the practice. Here's what that means.",
        "emoji": "🧱",
        "segments": [
            {"start": 259.6, "end": 263.7},
            {"start": 263.7, "end": 267.8},
            {"start": 238.0, "end": 242.2},
            {"start": 233.8, "end": 237.9},
        ],
        "cta_tts": "You don't build culture when things are easy. You build it when things are hard. That's when it counts.",
        "pexel_keywords": ["team", "business", "office"],
    },
    {
        "id": "new4_sacrifice",
        "mode": "A",
        "hook": "A 20-YEAR-OLD SACRIFICED EVERYTHING",
        "hook_tts": "A twenty year old sacrificed everything. His friends. His weekends. His comfort. And it paid off.",
        "emoji": "🔥",
        "segments": [
            {"start": 827.6, "end": 832.8},
            {"start": 833.4, "end": 839.5},
            {"start": 851.0, "end": 855.4},
            {"start": 855.4, "end": 860.4},
        ],
        "cta_tts": "Most people aren't willing to sacrifice their twenties. That's exactly why most people stay average.",
        "pexel_keywords": ["hustle", "work", "night"],
    },
    {
        "id": "new5_car",
        "mode": "A",
        "hook": "HE OWNS A $2.5 MILLION CAR",
        "hook_tts": "He owns a two point five million dollar car. But that's not the interesting part.",
        "emoji": "🏎️",
        "segments": [
            {"start": 1108.3, "end": 1113.3},
            {"start": 1041.6, "end": 1047.0},
            {"start": 1047.0, "end": 1051.4},
            {"start": 1055.2, "end": 1059.5},
        ],
        "cta_tts": "The car isn't the point. The point is what he had to become to afford it. That's the real flex.",
        "pexel_keywords": ["car", "luxury", "money"],
    },
    {
        "id": "new6_ordinary",
        "mode": "A",
        "hook": "I KNEW I WAS MEANT FOR MORE",
        "hook_tts": "I knew I was meant for more. I just didn't know how yet. But I started anyway.",
        "emoji": "🚀",
        "segments": [
            {"start": 536.3, "end": 540.4},
            {"start": 540.4, "end": 544.6},
            {"start": 548.5, "end": 552.7},
            {"start": 552.7, "end": 557.0},
        ],
        "cta_tts": "You don't need to know how. You just need to start. The how reveals itself when you move.",
        "pexel_keywords": ["rocket", "sky", "success"],
    },
]

# ═══════════════════════════════════════════════════════════════
# RENDER
# ═══════════════════════════════════════════════════════════════
async def render_variant_a(narr, idx, out_dir):
    vid_id = f"exp{idx:02d}_{narr['id']}_A"
    out_path = Path(out_dir) / f"{vid_id}.mp4"
    if out_path.exists():
        dur = get_duration(str(out_path))
        mb = out_path.stat().st_size / 1_048_576
        print(f"  ⏭️  Exists: {vid_id} ({dur:.1f}s, {mb:.1f}MB) — delete to re-render")
        return dur, mb

    print(f"\n  [{vid_id}] Hook: {narr['hook']}")

    # 1. TTS hook
    hook_audio = TMPDIR / f"{vid_id}_hook.wav"
    hook_dur = await gen_tts(narr["hook_tts"], hook_audio)
    print(f"  Hook TTS: {hook_dur:.1f}s")

    # 2. Extract source audio segments
    seg_audios = []
    seg_texts = []
    for si, seg in enumerate(narr["segments"]):
        seg_path = TMPDIR / f"{vid_id}_seg{si}.wav"
        subprocess.run([
            "ffmpeg", "-y", "-i", SRC_MP4,
            "-ss", str(seg["start"]), "-to", str(seg["end"]),
            *AUDIO_PARAMS, str(seg_path)
        ], capture_output=True)
        seg_audios.append(seg_path)
        txt = get_segment_text(seg["start"], seg["end"])
        seg_texts.append(txt)
        print(f"  Seg {si}: {seg['start']:.1f}-{seg['end']:.1f} → \"{txt[:60]}...\"")

    # 3. TTS CTA
    cta_audio = TMPDIR / f"{vid_id}_cta.wav"
    cta_dur = await gen_tts(narr["cta_tts"], cta_audio)
    print(f"  CTA TTS: {cta_dur:.1f}s")

    # 4. Concat audio
    seg_durs = [get_duration(str(a)) for a in seg_audios]
    total_audio = hook_dur + sum(seg_durs) + cta_dur

    # Padding if needed
    extra_audio = None
    extra_text = "That's the reality. Let that sink in."
    if total_audio < 30:
        extra_audio = TMPDIR / f"{vid_id}_extra.wav"
        extra_dur = await gen_tts(extra_text, extra_audio)
        total_audio = hook_dur + sum(seg_durs) + cta_dur + extra_dur
    else:
        extra_dur = 0

    # Concat WAV master
    concat_files = [str(hook_audio)] + [str(a) for a in seg_audios] + [str(cta_audio)]
    if extra_audio:
        concat_files.append(str(extra_audio))

    full_audio = TMPDIR / f"{vid_id}_full.wav"
    inputs = []
    for cf in concat_files:
        inputs.extend(["-i", cf])
    n = len(concat_files)
    filter_parts = [f"[{i}:a]" for i in range(n)]
    subprocess.run([
        "ffmpeg", "-y", *inputs,
        "-filter_complex", f"{' '.join(filter_parts)}concat=n={n}:v=0:a=1[out]",
        "-map", "[out]", *AUDIO_PARAMS, str(full_audio)
    ], capture_output=True)

    final_audio_dur = get_duration(str(full_audio))
    print(f"  Full audio: {final_audio_dur:.1f}s")

    # 5. Extract source frames (wide window covering all segments)
    seg_starts = [s["start"] for s in narr["segments"]]
    seg_ends = [s["end"] for s in narr["segments"]]
    win_start = max(0, min(seg_starts) - 15)
    win_end = min(1152.0, max(seg_ends) + 15)
    src_frames, src_fd = extract_source_frames(win_start, win_end, vid_id)
    print(f"  Source frames: {len(src_frames)} ({win_start:.0f}s–{win_end:.0f}s)")

    # 6. Pexels clip for hook & CTA
    random.seed(idx)
    pexel_clip = random.choice(PEXELS_CLIPS) if PEXELS_CLIPS else None
    pexel_dur = get_duration(str(pexel_clip)) if pexel_clip else 0

    # Extract pexels frames for hook phase
    pexel_frames = []
    pexel_fd = None
    if pexel_clip and pexel_dur > hook_dur:
        pexel_frames, pexel_fd = pexel_frames_for_range(
            pexel_clip, max(0, pexel_dur / 3), hook_dur + 1, int(hook_dur * FPS)
        )
        print(f"  Pexels hook frames: {len(pexel_frames)}")

    # 7. Render all frames
    total_frames = int(final_audio_dur * FPS)
    frame_dir = TMPDIR / f"{vid_id}_frames"
    frame_dir.mkdir(exist_ok=True)
    # Clear old frames
    for f in frame_dir.glob("*.png"):
        f.unlink()

    print(f"  Rendering {total_frames} frames...")

    # Phase boundaries (in seconds)
    hook_end = hook_dur
    seg_phase_durs = seg_durs  # actual durations
    seg_phase_starts = []
    cur = hook_end
    for sd in seg_phase_durs:
        seg_phase_starts.append((cur, cur + sd))
        cur += sd
    cta_start = cur
    cta_end = cta_start + cta_dur
    extra_start = cta_end
    extra_end = extra_start + extra_dur if extra_audio else cta_end

    for fi in range(total_frames):
        t = fi / FPS

        # Determine phase
        is_hook = t < hook_end
        is_cta = cta_start <= t < cta_end
        is_extra = extra_audio and extra_start <= t < extra_end

        # Pick background
        if is_hook and pexel_frames:
            # Hook phase: Pexels background
            pidx = min(int((t / hook_end) * len(pexel_frames)), len(pexel_frames) - 1)
            bg = Image.open(pexel_frames[pidx]).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
            bg = darken(bg, 0.5)
        elif is_hook:
            # Hook but no pexels: source footage
            src_pos = int((t / final_audio_dur) * len(src_frames)) if src_frames else 0
            src_pos = min(src_pos, len(src_frames) - 1) if src_frames else 0
            if src_frames:
                bg = Image.open(src_frames[src_pos]).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
                bg = darken(bg, 0.5)
            else:
                bg = Image.new("RGB", (WIDTH, HEIGHT), C_DARK)
        elif is_cta or is_extra:
            # CTA/extra: source footage darkened
            src_pos = int((t / final_audio_dur) * len(src_frames)) if src_frames else 0
            src_pos = min(src_pos, len(src_frames) - 1) if src_frames else 0
            if src_frames:
                bg = Image.open(src_frames[src_pos]).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
                bg = darken(bg, 0.4)
            else:
                bg = Image.new("RGB", (WIDTH, HEIGHT), C_DARK)
        else:
            # Segment phase: source footage
            src_pos = int((t / final_audio_dur) * len(src_frames)) if src_frames else 0
            src_pos = min(src_pos, len(src_frames) - 1) if src_frames else 0
            if src_frames:
                bg = Image.open(src_frames[src_pos]).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
                bg = darken(bg, 0.35)
            else:
                bg = Image.new("RGB", (WIDTH, HEIGHT), C_DARK)

        # Ken Burns
        bg = apply_ken_burns(bg, t, final_audio_dur)

        # Overlay text based on phase
        draw = ImageDraw.Draw(bg)

        if is_hook:
            # Big hook text
            fo = font(64, FONT_BOLD)
            lines = word_wrap(narr["hook"], draw, fo, WIDTH - 120)
            total_h = sum(draw.textbbox((0, 0), l, font=fo)[3] - draw.textbbox((0, 0), l, font=fo)[1] + 16 for l in lines)
            cy = (HEIGHT - total_h) // 2 - 100
            for l in lines:
                bbox = draw.textbbox((0, 0), l, font=fo)
                lw = bbox[2] - bbox[0]
                lh = bbox[3] - bbox[1]
                x = (WIDTH - lw) // 2
                draw.text((x + 3, cy + 3), l, font=fo, fill=(0, 0, 0))
                draw.text((x, cy), l, font=fo, fill=C_GOLD)
                cy += lh + 16

            # Emoji top-right
            add_emoji(bg, narr["emoji"], WIDTH - 130, 80, 90)

        elif is_cta or is_extra:
            # CTA text — lower third
            txt = narr["cta_tts"] if is_cta else extra_text
            fo = font(48, FONT_BOLD)
            lines = word_wrap(txt, draw, fo, WIDTH - 160)
            total_h = sum(draw.textbbox((0, 0), l, font=fo)[3] - draw.textbbox((0, 0), l, font=fo)[1] + 14 for l in lines)
            cy = HEIGHT - 500 - total_h // 2
            # Background box
            draw.rectangle([40, cy - 20, WIDTH - 40, cy + total_h + 20], fill=(0, 0, 0, 180))
            for l in lines:
                bbox = draw.textbbox((0, 0), l, font=fo)
                lw = bbox[2] - bbox[0]
                lh = bbox[3] - bbox[1]
                x = (WIDTH - lw) // 2
                draw.text((x + 2, cy + 2), l, font=fo, fill=(0, 0, 0))
                draw.text((x, cy), l, font=fo, fill=C_GREEN if is_cta else C_CYAN)
                cy += lh + 14

            add_emoji(bg, narr["emoji"], 50, HEIGHT - 200, 70)

        else:
            # Segment phase: caption overlay (word-by-word style)
            seg_idx = 0
            for si, (s_start, s_end) in enumerate(seg_phase_starts):
                if s_start <= t < s_end:
                    seg_idx = si
                    break

            txt = seg_texts[seg_idx] if seg_idx < len(seg_texts) else ""
            if txt:
                # Show progressive portion (kinetic caption)
                seg_local_t = t - seg_phase_starts[seg_idx][0]
                seg_local_dur = seg_phase_durs[seg_idx]
                # Show full text wrapped, highlight current word
                fo = font(44, FONT_BOLD)
                lines = word_wrap(txt, draw, fo, WIDTH - 120)
                total_h = sum(draw.textbbox((0, 0), l, font=fo)[3] - draw.textbbox((0, 0), l, font=fo)[1] + 12 for l in lines)
                cy = HEIGHT - 350 - total_h // 2
                # Semi-transparent box
                draw.rectangle([30, cy - 15, WIDTH - 30, cy + total_h + 15], fill=(0, 0, 0))
                # Draw text
                words_shown = max(1, int(len(txt.split()) * (seg_local_t / max(seg_local_dur, 0.1))))
                words_drawn = 0
                for l in lines:
                    bbox = draw.textbbox((0, 0), l, font=fo)
                    lw = bbox[2] - bbox[0]
                    lh = bbox[3] - bbox[1]
                    x = (WIDTH - lw) // 2
                    line_words = l.split()
                    # Draw word by word
                    wx = x
                    for wi, w in enumerate(line_words):
                        if words_drawn < words_shown:
                            wbbox = draw.textbbox((0, 0), w + " ", font=fo)
                            ww = wbbox[2] - wbbox[0]
                            draw.text((wx, cy), w, font=fo, fill=C_WHITE)
                            wx += ww
                            words_drawn += 1
                    cy += lh + 12

        # Progress bar
        add_progress_bar(bg, t / final_audio_dur)

        # Save
        bg.save(frame_dir / f"f_{fi:05d}.png")

        if fi % 300 == 0:
            print(f"   ...{fi}/{total_frames}")

    # 8. Encode
    print(f"  Encoding {total_frames} frames...")
    frames_concat = TMPDIR / f"{vid_id}_frames.txt"
    with open(str(frames_concat), "w") as f:
        for fi in range(total_frames):
            fp = frame_dir / f"f_{fi:05d}.png"
            f.write(f"file '{fp}'\nduration {1/FPS:.6f}\n")

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(frames_concat),
        "-i", str(full_audio),
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest", str(out_path)
    ], capture_output=True, timeout=600)

    final_dur = get_duration(str(out_path))
    size_mb = out_path.stat().st_size / 1_048_576
    print(f"  ✅ {vid_id}.mp4 ({final_dur:.1f}s, {size_mb:.1f}MB)")

    # Cleanup
    for p in [hook_audio] + seg_audios + [cta_audio] + ([extra_audio] if extra_audio else []):
        Path(p).unlink(missing_ok=True)
    full_audio.unlink(missing_ok=True)
    shutil.rmtree(frame_dir, ignore_errors=True)
    shutil.rmtree(src_fd, ignore_errors=True)
    if pexel_fd:
        shutil.rmtree(pexel_fd, ignore_errors=True)
    frames_concat.unlink(missing_ok=True)

    return final_dur, size_mb


async def main():
    print("🎮 Hybrid Renderer v7.3 — Footage + Pexels + TTS + Text + Emoji")
    print(f"   Source: {SRC_MP4}")
    print(f"   Pexels clips: {len(PEXELS_CLIPS)}")
    print(f"   Output: {OUTDIR}\n")

    ensure_source_audio()

    results = []
    for i, narr in enumerate(NARRATIVES, 1):
        print(f"\n{'='*60}")
        print(f"  [{i}/6] {narr['id']}")
        try:
            dur, mb = await render_variant_a(narr, i, OUTDIR)
            results.append((narr["id"], dur, mb, "✅"))
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            results.append((narr["id"], 0, 0, f"❌ {e}"))

    print(f"\n{'='*60}")
    print("✅ Results:")
    for rid, dur, mb, status in results:
        mark = "✅" if dur >= 30 else "❌"
        print(f"  {mark} {rid}: {dur:.1f}s, {mb:.1f}MB")


if __name__ == "__main__":
    asyncio.run(main())
