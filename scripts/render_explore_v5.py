#!/usr/bin/env python3
"""
Hybrid Audio Renderer v5 — TTS hook + source audio body.

Two modes:
  - Mode A (verbatim): Extract source audio+video segments verbatim, TTS only for hook/CTA
  - Mode B (hybrid):    TTS commentary with source quote played as accent

Fixes from v4:
  - Visual: crop (not stretch) to 9:16, slow Ken Burns (1.0→1.03)
  - Audio: source audio extracted at segment timestamps
  - Source scrubbing: contiguous frames (not jumped)
"""

import json, subprocess, asyncio, random, shutil, edge_tts
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

PROJECT = Path("/Users/hung/code/ai/shorts")
OUTDIR  = PROJECT / "output" / "explore_v5"
OUTDIR.mkdir(parents=True, exist_ok=True)
TMPDIR  = PROJECT / "output" / "tmp_explore5"
TMPDIR.mkdir(parents=True, exist_ok=True)

SRC_WEBM   = PROJECT / "output/source/2eicF3iPf1s.webm"
SRC_MP4    = PROJECT / "output/source/2eicF3iPf1s.mp4"
SRC_AUDIO  = TMPDIR / "source_full.wav"
SRC_TRANSCRIPT = PROJECT / "output/source/2eic_transcript.json"

FPS    = 30
WIDTH   = 1080
HEIGHT  = 1920

# Colors
C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)
C_GOLD  = (255, 215, 0)
C_CYAN  = (0, 200, 255)
C_RED   = (255, 80, 80)
C_DARK  = (15, 15, 20)

FONT_BOLD = "/System/Library/Fonts/Helvetica.ttc"

def font(size, bold=True):
    size = max(1, int(size))
    try:
        return ImageFont.truetype(FONT_BOLD, size, index=1 if bold else 0)
    except:
        return ImageFont.truetype(FONT_BOLD, size)

# ── Extract source audio once ──
def ensure_source_audio():
    if not SRC_AUDIO.exists():
        print("  Extracting source audio...")
        subprocess.run(["ffmpeg", "-y", "-i", str(SRC_WEBM), "-vn", "-ac", "1", "-ar", "44100", str(SRC_AUDIO)], capture_output=True)
        print(f"  ✅ Source audio: {SRC_AUDIO}")

# ── TTS for hook/CTA only ──
async def gen_tts(text, out_path):
    comm = edge_tts.Communicate(text, "en-US-GuyNeural", rate="+12%", pitch="+0Hz")
    await comm.save(out_path)
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", out_path], capture_output=True, text=True)
    return float(r.stdout.strip())

# ── Extract source video segment (video + audio) ──
def extract_source_segment(start, end, out_video, out_audio):
    """Extract video + audio from source at [start, end]."""
    dur = end - start
    # Video + audio (keep source audio — no -an! force 44100Hz mono to match TTS)
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(start), "-i", str(SRC_MP4),
        "-t", str(dur),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
        "-c:a", "aac", "-ac", "1", "-ar", "44100", "-q:v", "2", str(out_video)
    ], capture_output=True)
    # Audio only for concat mixing (re-use same segment audio, already extracted)
    # Just copy the segment video's audio - no separate extraction needed

# ── Narratives with verbatim source segments ──
NARRATIVES = [
    {
        "id": "a1_firing",
        "hook": "FIRING PEOPLE IS ACTUALLY KIND",
        "hook_tts": "If you don't fire them, you're holding them back. Here's why.",
        "mode": "A",  # Verbatim source clips
        "segments": [
            {"start": 142.4, "end": 146.9},   # "have to fire people?"
            {"start": 146.9, "end": 150.9},   # "if you don't fire them, holding back"
            {"start": 151.0, "end": 155.5},   # "keeping from what they could be great at"
            {"start": 155.5, "end": 159.7},   # "younger in business, hard thing until realized"
        ],
        "cta_tts": "The kindest thing you can do is let people go find what they're great at.",
    },
    {
        "id": "a2_discipline",
        "hook": "DISCIPLINE IS A BANK ACCOUNT",
        "hook_tts": "Discipline is a bank account. Every deposit makes you stronger.",
        "mode": "A",
        "segments": [
            {"start": 293.0, "end": 297.0},   # "invest in discipline, hurting yourself"
            {"start": 297.0, "end": 300.9},   # "discipline as bank account, deposits"
            {"start": 300.9, "end": 307.5},   # "walk past trash, not fixing it"
            {"start": 307.5, "end": 311.5},   # "not hurting gym, hurting you"
        ],
        "cta_tts": "Every time you show up, you make a deposit. Every time you don't, you withdraw.",
    },
    {
        "id": "a3_12k",
        "hook": "FROM $12K TO BILLION",
        "hook_tts": "They started with twelve thousand dollars. Now they own a billion dollar empire.",
        "mode": "A",
        "segments": [
            {"start": 332.2, "end": 336.4},   # "retail store, no money, no investors"
            {"start": 336.4, "end": 341.4},   # "started with $12,000"
            {"start": 344.9, "end": 349.9},   # "first day $7, first 10 years 700/month"
            {"start": 354.0, "end": 363.1},   # "first 10 years total $58,380, $695/month"
        ],
        "cta_tts": "Ten years of grinding. Most people would have quit. They didn't.",
    },
    {
        "id": "b1_culture",
        "hook": "CULTURE BUILDS EMPIRES",
        "hook_tts": "Andy built a billion dollar company. His secret? Culture. Not money.",
        "mode": "B",  # TTS commentary + source quotes
        "source_quotes": [
            {"start": 124.0, "end": 128.7},   # "people spend most of life at work"
            {"start": 131.9, "end": 137.3},   # "strong culture, strong business"
        ],
        "commentary_tts": (
            "Andy Frisella believes culture is everything. "
            "People spend most of their life at work. "
            "If you don't have a strong culture, you can't have a strong business. "
            "He built a billion dollar company by investing in his people first. "
            "When everybody trains together, works together, struggles together, "
            "something powerful happens. That mutual suffering builds character. "
            "That character builds companies. That's how you build an empire. "
            "It's not about the product. It's about the people. "
            "When you have the right people, everything else falls into place. "
            "That is the secret to building something that lasts."
        ),
    },
    {
        "id": "b2_fitness",
        "hook": "FITNESS EQUALS FINANCIAL SUCCESS",
        "hook_tts": "The correlation between physical fitness and financial success is huge.",
        "mode": "B",
        "source_quotes": [
            {"start": 233.8, "end": 237.9},   # "Absolutely. Huge correlation."
            {"start": 238.0, "end": 242.2},   # "mutual suffering, trains together"
        ],
        "commentary_tts": (
            "Have you seen the correlation between fitness and financial success? "
            "Andy says it's huge. The bigger thing is mutual suffering. "
            "When everybody trains together and struggles together, "
            "you see people dying on the floor and a boss next to them. "
            "But out here they are equal. "
            "The same discipline it takes to show up at five AM "
            "is the same discipline it takes to show up for your business."
        ),
    },
    {
        "id": "b3_advice",
        "hook": "THIS IS NOT LAMBORGHINIS",
        "hook_tts": "Andy says this isn't just Lamborghinis and balling out. This is a grind.",
        "mode": "B",
        "source_quotes": [
            {"start": 392.3, "end": 398.2},   # "not just Lamborghinis and balling out"
            {"start": 398.2, "end": 401.8},   # "this is hard, it's a grind"
        ],
        "commentary_tts": (
            "Andy Frisella has spent his whole life encouraging young entrepreneurs. "
            "He says this isn't just Lamborghinis and balling out. "
            "This is hard. It's a grind. "
            "And just because it's hard for you doesn't mean you're doing it wrong. "
            "It actually means you're doing it right. "
            "Anybody can learn skills. Anybody can learn to be resilient. "
            "Every single person hearing this has the ability to be great."
        ),
    },
]


async def render_variant_a(narr, hook_text, idx, out_dir):
    """Mode A: Verbatim source clips + TTS hook/CTA."""
    vid_id = f"exp{idx:02d}_{narr['id']}_A"
    print(f"  Mode A: {vid_id}")

    # 1. Generate TTS hook
    hook_audio = TMPDIR / f"{vid_id}_hook.wav"
    hook_dur = await gen_tts(narr["hook_tts"], str(hook_audio))
    print(f"  Hook TTS: {hook_dur:.1f}s")

    # 2. Generate TTS CTA
    cta_audio = TMPDIR / f"{vid_id}_cta.wav"
    cta_dur = await gen_tts(narr["cta_tts"], str(cta_audio))
    print(f"  CTA TTS: {cta_dur:.1f}s")

    # 3. Extract source segments
    seg_videos = []
    seg_audios = []
    total_source_dur = 0
    for si, seg in enumerate(narr["segments"]):
        sv = TMPDIR / f"{vid_id}_seg{si}.mp4"
        sa = TMPDIR / f"{vid_id}_seg{si}_a.wav"
        extract_source_segment(seg["start"], seg["end"], sv, sa)
        seg_videos.append(sv)
        seg_audios.append(sa)
        sd = seg["end"] - seg["start"]
        total_source_dur += sd
        print(f"  Seg {si}: {seg['start']:.1f}-{seg['end']:.1f} ({sd:.1f}s)")

    # 4. Total duration = hook + source segments + CTA
    total_dur = hook_dur + total_source_dur + cta_dur
    print(f"  Total: {total_dur:.1f}s (hook {hook_dur:.1f} + source {total_source_dur:.1f} + CTA {cta_dur:.1f})")

    if total_dur < 30:
        # Extend by adding more CTS/transition
        extra = narr["hook_tts"] + " Let that sink in."
        extra_audio = TMPDIR / f"{vid_id}_extra.wav"
        extra_dur = await gen_tts(extra, str(extra_audio))
        cta_dur += extra_dur
        total_dur = hook_dur + total_source_dur + cta_dur
        # Append extra to CTA
        subprocess.run(["ffmpeg", "-y", "-i", str(cta_audio), "-i", str(extra_audio), "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1", str(cta_audio.with_suffix(".merged.wav"))], capture_output=True)
        cta_audio = cta_audio.with_suffix(".merged.wav")

    # 5. Build full video: hook (black bg + text) → source segments → CTA (black bg + text)
    # Hook section: render as frames with Ken Burns on source preview
    hook_frames_dir = TMPDIR / f"{vid_id}_hook_frames"
    hook_frames_dir.mkdir(exist_ok=True)
    tf_hook = int(hook_dur * FPS)

    # Extract a preview frame from first source segment for hook bg
    preview_frame = TMPDIR / f"{vid_id}_preview.jpg"
    first_seg = narr["segments"][0]
    subprocess.run(["ffmpeg", "-y", "-ss", str(first_seg["start"] + 1), "-i", str(SRC_MP4), "-vframes", "1", "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", str(preview_frame)], capture_output=True)

    for i in range(tf_hook):
        t = i / FPS
        progress = t / hook_dur
        bg = Image.open(preview_frame).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        # Darken progressively
        darkness = 0.5 + 0.3 * progress
        overlay = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        bg = Image.blend(bg, overlay, darkness)
        # Slow Ken Burns zoom (1.0→1.03)
        zoom = 1.0 + 0.03 * progress
        bw, bh = int(WIDTH / zoom), int(HEIGHT / zoom)
        bx = (WIDTH - bw) // 2
        by = int((HEIGHT - bh) * 0.3 * progress)
        bg = bg.crop((bx, by, bx + bw, by + bh)).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(bg)
        # Hook text (fade in)
        scale = min(1.0, progress * 3)
        if scale > 0:
            fsz = max(1, int(60 * scale))
            fo = font(fsz)
            bbox = draw.textbbox((0, 0), hook_text, font=fo)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            draw.rectangle([(WIDTH - tw) // 2 - 20, 400, (WIDTH + tw) // 2 + 20, 400 + th + 30], fill=(0, 0, 0))
            draw.text(((WIDTH - tw) // 2, 410), hook_text, font=fo, fill=C_GOLD)
        bg.save(hook_frames_dir / f"f_{i:05d}.png")

    # CTA section: render with darkened last segment preview
    cta_frames_dir = TMPDIR / f"{vid_id}_cta_frames"
    cta_frames_dir.mkdir(exist_ok=True)
    tf_cta = int(cta_dur * FPS)
    last_seg = narr["segments"][-1]
    preview_last = TMPDIR / f"{vid_id}_preview_last.jpg"
    subprocess.run(["ffmpeg", "-y", "-ss", str(last_seg["end"] - 1), "-i", str(SRC_MP4), "-vframes", "1", "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", str(preview_last)], capture_output=True)

    for i in range(tf_cta):
        t = i / FPS
        progress = t / cta_dur
        bg = Image.open(preview_last).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        overlay = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        bg = Image.blend(bg, overlay, 0.6)
        zoom = 1.0 + 0.03 * progress
        bw, bh = int(WIDTH / zoom), int(HEIGHT / zoom)
        bx = (WIDTH - bw) // 2
        bg = bg.crop((bx, 0, bx + bw, bh)).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(bg)
        # CTA text at bottom
        scale = min(1.0, progress * 3)
        if scale > 0:
            fsz = max(1, int(48 * scale))
            fo = font(fsz)
            lines = [narr["cta_tts"][i:i+40] for i in range(0, len(narr["cta_tts"]), 40)]
            for li, line in enumerate(lines[:4]):
                bbox = draw.textbbox((0, 0), line, font=fo)
                tw = bbox[2] - bbox[0]
                y = 1200 + li * 60
                draw.text(((WIDTH - tw) // 2, y), line, font=fo, fill=C_WHITE)
        bg.save(cta_frames_dir / f"f_{i:05d}.png")

    # 6. Stitch everything together
    # Video: hook frames → source segments → CTA frames
    # Encode hook frames
    hook_vid = TMPDIR / f"{vid_id}_hook.mp4"
    subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", str(hook_frames_dir / "f_%05d.png"), "-i", str(hook_audio), "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ac", "1", "-ar", "44100", "-shortest", str(hook_vid)], capture_output=True)

    # Encode CTA frames
    cta_vid = TMPDIR / f"{vid_id}_cta.mp4"
    subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", str(cta_frames_dir / "f_%05d.png"), "-i", str(cta_audio), "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ac", "1", "-ar", "44100", "-shortest", str(cta_vid)], capture_output=True)

    # 6. Stitch everything together with concat filter (handles mixed params)
    # Build ffmpeg filter: [hook_v][hook_a][seg0_v][seg0_a]...[segN_v][segN_a][cta_v][cta_a]concat=n=X:v=1:a=1
    total_inputs = 2 + len(seg_videos)  # hook + N segments + cta
    inputs = []
    filter_parts = []
    for idx, inp in enumerate([hook_vid] + seg_videos + [cta_vid]):
        inputs += ["-i", str(inp)]
        filter_parts.append(f"[{idx}:v][{idx}:a]")
    filter_str = "".join(filter_parts) + f"concat=n={total_inputs}:v=1:a=1[outv][outa]"

    out_path = out_dir / f"{vid_id}.mp4"
    subprocess.run([
        "ffmpeg", "-y"] + inputs + [
        "-filter_complex", filter_str,
        "-map", "[outv]", "-map", "[outa]",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", str(out_path)
    ], capture_output=True)

    # Check duration
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(out_path)], capture_output=True, text=True)
    final_dur = float(r.stdout.strip())
    size_mb = out_path.stat().st_size / 1024 / 1024
    print(f"  ✅ {out_path.name} ({final_dur:.1f}s, {size_mb:.1f}MB)")

    # Cleanup
    shutil.rmtree(hook_frames_dir, ignore_errors=True)
    shutil.rmtree(cta_frames_dir, ignore_errors=True)
    for sv in seg_videos:
        sv.unlink(missing_ok=True)
    for sa in seg_audios:
        sa.unlink(missing_ok=True)
    hook_audio.unlink(missing_ok=True)
    cta_audio.unlink(missing_ok=True)
    preview_frame.unlink(missing_ok=True)
    preview_last.unlink(missing_ok=True)
    return final_dur, size_mb


async def render_variant_b(narr, hook_text, idx, out_dir):
    """Mode B: TTS commentary + source quotes as accent."""
    vid_id = f"exp{idx:02d}_{narr['id']}_B"
    print(f"  Mode B: {vid_id}")

    # 1. Generate TTS commentary (main audio track)
    tts_audio = TMPDIR / f"{vid_id}_tts.wav"
    tts_dur = await gen_tts(narr["commentary_tts"], str(tts_audio))
    print(f"  Commentary TTS: {tts_dur:.1f}s, {len(narr['commentary_tts'].split())} words")

    # 2. Extract source quote audio
    quote_audios = []
    total_quote_dur = 0
    for qi, q in enumerate(narr["source_quotes"]):
        qa = TMPDIR / f"{vid_id}_quote{qi}.wav"
        subprocess.run(["ffmpeg", "-y", "-ss", str(q["start"]), "-i", str(SRC_AUDIO), "-t", str(q["end"] - q["start"]), "-ac", "1", "-ar", "44100", str(qa)], capture_output=True)
        quote_audios.append(qa)
        total_quote_dur += q["end"] - q["start"]
    print(f"  Source quotes: {len(quote_audios)} ({total_quote_dur:.1f}s)")

    # 3. Mix: Concat TTS + quotes (simple, no ducking needed)
    # Structure: TTS[intro] → quote1 → TTS[mid] → quote2 → TTS[outro]
    tts_words = narr["commentary_tts"].split()
    split1 = len(tts_words) // 3
    split2 = 2 * len(tts_words) // 3
    tts_parts = [
        " ".join(tts_words[:split1]),
        " ".join(tts_words[split1:split2]),
        " ".join(tts_words[split2:]),
    ]

    # Generate individual TTS segments
    tts_files = []
    for pi, txt in enumerate(tts_parts):
        if not txt.strip():
            continue
        pf = TMPDIR / f"{vid_id}_tts{pi}.wav"
        await gen_tts(txt, str(pf))
        r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(pf)], capture_output=True, text=True)
        pdur = float(r.stdout.strip()) if r.stdout.strip() else 0
        tts_files.append((pf, pdur))
        print(f"  TTS part {pi}: {pdur:.1f}s ({len(txt.split())} words)")

    # Build concat list: TTS0, quote0, TTS1, quote1, TTS2
    concat_audio = TMPDIR / f"{vid_id}_concat.wav"
    concat_paths = []
    concat_paths.append(tts_files[0][0])
    if quote_audios:
        concat_paths.append(quote_audios[0])
    concat_paths.append(tts_files[1][0])
    if len(quote_audios) > 1:
        concat_paths.append(quote_audios[1])
    if len(tts_files) > 2:
        concat_paths.append(tts_files[2][0])

    # Stitch all audio files together
    if len(concat_paths) == 1:
        mixed_audio = concat_paths[0]
        final_audio_dur = tts_files[0][1]
    else:
        filter_parts = []
        for ci, ap in enumerate(concat_paths):
            filter_parts.append(f"[{ci}:a]")
        filter_complex = "".join(filter_parts) + f"concat=n={len(concat_paths)}:v=0:a=1[out]"
        inputs = []
        for ap in concat_paths:
            inputs += ["-i", str(ap)]
        subprocess.run(["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_complex, "-map", "[out]", str(concat_audio)], capture_output=True)
        r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(concat_audio)], capture_output=True, text=True)
        final_audio_dur = float(r.stdout.strip()) if r.stdout.strip() else 0
        mixed_audio = concat_audio

    print(f"  Mixed audio: {final_audio_dur:.1f}s")

    # 4. Render video frames with source footage + Ken Burns + b-roll variety
    fd = TMPDIR / f"{vid_id}_frames"
    fd.mkdir(exist_ok=True)
    tf = int(final_audio_dur * FPS)

    # Extract a WIDE window of source frames (90s+) at 10fps for smooth scrolling
    src_fd = TMPDIR / f"{vid_id}_src"
    src_fd.mkdir(exist_ok=True)
    src_total = 1152.0
    # Extract frames from a wide window covering before first quote to after last
    start_window = max(0, narr["source_quotes"][0]["start"] - 25)
    end_window = min(src_total, narr["source_quotes"][-1]["end"] + 35)
    window_dur = end_window - start_window
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(start_window), "-i", str(SRC_MP4),
        "-t", str(window_dur),
        "-vf", f"fps=10,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-an", "-q:v", "2", str(src_fd / "f_%05d.jpg")
    ], capture_output=True)
    
    all_src = sorted(src_fd.glob("*.jpg"))
    src_count = len(all_src)
    print(f"  Source frames: {src_count} ({window_dur:.0f}s window at 10fps)")

    # If too few frames for smooth scrolling, create slideshow with crossfade
    for i in range(tf):
        t = i / FPS
        if all_src:
            # Smooth scroll through frames — never repeat
            src_pos = (t / final_audio_dur) * src_count
            fi = min(int(src_pos), src_count - 1)
            bg = Image.open(all_src[fi]).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        else:
            bg = Image.new("RGB", (WIDTH, HEIGHT), C_BLACK)
        # Darken
        overlay = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        bg = Image.blend(bg, overlay, 0.35)
        # Slow Ken Burns zoom (1.0→1.04)
        zoom = 1.0 + 0.04 * (t / final_audio_dur)
        bw, bh = int(WIDTH / zoom), int(HEIGHT / zoom)
        bx = (WIDTH - bw) // 2
        by = int((HEIGHT - bh) * 0.2 * (t / final_audio_dur))
        bg = bg.crop((bx, by, bx + bw, by + bh)).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(bg)

        # Hook text (first 3s)
        if t < 3.0:
            scale = min(1.0, t / 0.3)
            fsz = max(1, int(56 * scale))
            fo = font(fsz)
            bbox = draw.textbbox((0, 0), hook_text, font=fo)
            tw = bbox[2] - bbox[0]
            draw.rectangle([(WIDTH - tw) // 2 - 15, 100, (WIDTH + tw) // 2 + 15, 180], fill=(0, 0, 0))
            draw.text(((WIDTH - tw) // 2, 110), hook_text, font=fo, fill=C_GOLD)

        # Progress bar
        bar_w = int(WIDTH * t / final_audio_dur)
        draw.rectangle([0, HEIGHT - 8, bar_w, HEIGHT], fill=C_CYAN)
        bg.save(fd / f"f_{i:05d}.png")

    # 5. Encode video with mixed audio
    out_path = out_dir / f"{vid_id}.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS), "-i", str(fd / "f_%05d.png"),
        "-i", str(mixed_audio),
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-shortest", str(out_path)
    ], capture_output=True)

    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(out_path)], capture_output=True, text=True)
    final_dur = float(r.stdout.strip())
    size_mb = out_path.stat().st_size / 1024 / 1024
    print(f"  ✅ {out_path.name} ({final_dur:.1f}s, {size_mb:.1f}MB)")

    # Cleanup
    shutil.rmtree(fd, ignore_errors=True)
    shutil.rmtree(src_fd, ignore_errors=True)
    tts_audio.unlink(missing_ok=True)
    if mixed_audio != tts_audio:
        mixed_audio.unlink(missing_ok=True)
    for pf, _ in tts_files:
        pf.unlink(missing_ok=True)
    for qa in quote_audios:
        qa.unlink(missing_ok=True)
    return final_dur, size_mb


# ── Main ──
async def main():
    print("🎮 Hybrid Audio Exploration v5 — 6 variants")
    print(f"   Mode A (verbatim): 3 videos | Mode B (hybrid): 3 videos")
    print(f"   Output: {OUTDIR}\n")

    ensure_source_audio()

    results = []
    for i, narr in enumerate(NARRATIVES, 1):
        print(f"\n{'='*60}")
        print(f"  [{i}/6] {narr['id']} (mode {narr['mode']})")
        print(f"  Hook: {narr['hook']}")

        try:
            if narr["mode"] == "A":
                dur, mb = await render_variant_a(narr, narr["hook"], i, OUTDIR)
            else:
                dur, mb = await render_variant_b(narr, narr["hook"], i, OUTDIR)
            results.append((narr["id"], dur, mb, "✅"))
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            results.append((narr["id"], 0, 0, f"❌ {e}"))

    print(f"\n{'='*60}")
    print(f"✅ Results:")
    for name, dur, mb, status in results:
        ok = "✅" if 30 <= dur <= 60 else "❌"
        print(f"  {ok} {name}: {dur:.1f}s, {mb:.1f}MB")


if __name__ == "__main__":
    asyncio.run(main())
