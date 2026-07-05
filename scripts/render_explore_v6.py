#!/usr/bin/env python3
"""
Hybrid Audio Renderer v6 — TTS hook + source audio body.

Changes from v5:
- Mode A: concat tất cả audio thành WAV, render frames tuần tự, encode 1 lần (không concat filter)
- Mode B: extract wide window (60s+) frames, smooth scroll không repeat
- Audio: tất cả 44100Hz mono để match
"""

import json, subprocess, asyncio, random, shutil, edge_tts
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

PROJECT = Path("/Users/hung/code/ai/shorts")
OUTDIR  = PROJECT / "output" / "explore_v5"
OUTDIR.mkdir(parents=True, exist_ok=True)
TMPDIR  = PROJECT / "output" / "tmp_explore5"
TMPDIR.mkdir(parents=True, exist_ok=True)

SRC_MP4    = str(PROJECT / "output/source/2eicF3iPf1s.mp4")
SRC_WEBM   = str(PROJECT / "output/source/2eicF3iPf1s.webm")
SRC_AUDIO  = TMPDIR / "source_full.wav"

FPS    = 30
WIDTH   = 1080
HEIGHT  = 1920
AUDIO_PARAMS = ["-ac", "1", "-ar", "44100"]  # All audio → 44.1kHz mono

# Colors
C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)
C_GOLD  = (255, 215, 0)
C_CYAN  = (0, 200, 255)

FONT_BOLD = "/System/Library/Fonts/Helvetica.ttc"

def font(size, bold=True):
    size = max(1, int(size))
    try:
        return ImageFont.truetype(FONT_BOLD, size, index=1 if bold else 0)
    except:
        return ImageFont.truetype(FONT_BOLD, size)

# ── Source audio ──
def ensure_source_audio():
    if not SRC_AUDIO.exists():
        print("  Extracting source audio...")
        subprocess.run(["ffmpeg", "-y", "-i", SRC_MP4, "-vn"] + AUDIO_PARAMS + [str(SRC_AUDIO)], capture_output=True)

# ── TTS ──
async def gen_tts(text, out_path):
    out_path = Path(out_path) if not isinstance(out_path, Path) else out_path
    comm = edge_tts.Communicate(text, "en-US-GuyNeural", rate="+12%", pitch="+0Hz")
    await comm.save(str(out_path))
    # Resample to 44100 mono for consistency
    resampled = out_path.with_suffix(".resampled.wav")
    subprocess.run(["ffmpeg", "-y", "-i", str(out_path)] + AUDIO_PARAMS + [str(resampled)], capture_output=True)
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(resampled)], capture_output=True, text=True)
    dur = float(r.stdout.strip()) if r.stdout.strip() else 0
    out_path.unlink(missing_ok=True)
    shutil.move(str(resampled), str(out_path))
    return dur

# ── Extract source video segment (frames + audio WAV) ──
def extract_segment_frames(start, end, out_dir):
    """Extract video frames + audio WAV from source."""
    dur = end - start
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(start), "-i", SRC_MP4,
        "-t", str(dur),
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps={FPS}",
        "-an", "-q:v", "2", str(out_dir / "f_%05d.jpg")
    ], capture_output=True)

def extract_segment_audio(start, end, out_audio):
    """Extract audio WAV from source."""
    dur = end - start
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(start), "-i", SRC_MP4,
        "-t", str(dur), "-vn"
    ] + AUDIO_PARAMS + [str(out_audio)], capture_output=True)


NARRATIVES = [
    {
        "id": "a1_firing",
        "hook": "FIRING PEOPLE IS ACTUALLY KIND",
        "hook_tts": "If you don't fire them, you're holding them back. Here's why.",
        "mode": "A",
        "segments": [
            {"start": 142.4, "end": 146.9},
            {"start": 146.9, "end": 150.9},
            {"start": 151.0, "end": 155.5},
            {"start": 155.5, "end": 159.7},
        ],
        "cta_tts": "The kindest thing you can do is let people go find what they're great at.",
    },
    {
        "id": "a2_discipline",
        "hook": "DISCIPLINE IS A BANK ACCOUNT",
        "hook_tts": "Discipline is a bank account. Every deposit makes you stronger.",
        "mode": "A",
        "segments": [
            {"start": 293.0, "end": 297.0},
            {"start": 297.0, "end": 300.9},
            {"start": 300.9, "end": 307.5},
            {"start": 307.5, "end": 311.5},
        ],
        "cta_tts": "Every time you show up, you make a deposit. Every time you don't, you withdraw.",
    },
    {
        "id": "a3_12k",
        "hook": "FROM $12K TO BILLION",
        "hook_tts": "They started with twelve thousand dollars. Now they own a billion dollar empire.",
        "mode": "A",
        "segments": [
            {"start": 332.2, "end": 336.4},
            {"start": 336.4, "end": 341.4},
            {"start": 344.9, "end": 349.9},
            {"start": 354.0, "end": 363.1},
        ],
        "cta_tts": "Ten years of grinding. Most people would have quit. They didn't.",
    },
    {
        "id": "b1_culture",
        "hook": "CULTURE BUILDS EMPIRES",
        "hook_tts": "Andy built a billion dollar company. His secret? Culture. Not money.",
        "mode": "B",
        "source_quotes": [
            {"start": 124.0, "end": 128.7},
            {"start": 131.9, "end": 137.3},
        ],
        "commentary_tts": "Andy Frisella built a billion dollar company by focusing on one thing. Culture. He says people spend most of their life at work. If you don't have a strong culture, you can't have a strong business. So he created a culture where everybody trains together, works together, and struggles together. That mutual suffering builds character. That character builds companies. It's not about the product. It's about the people. When you have the right people who share the same values, everything else falls into place. That's the secret. Culture. Not money. Not strategy. Culture.",
    },
    {
        "id": "b2_fitness",
        "hook": "FITNESS EQUALS FINANCIAL SUCCESS",
        "hook_tts": "The correlation between physical fitness and financial success is huge.",
        "mode": "B",
        "source_quotes": [
            {"start": 233.8, "end": 237.9},
            {"start": 238.0, "end": 242.2},
        ],
        "commentary_tts": "There's a huge correlation between physical fitness and financial success. Andy says it's not just about looking good. When everybody trains together and struggles together, something powerful happens. Mutual suffering. You see people who are dying on the gym floor, and the person next to them is their boss at work. But out here, they are equal. The same discipline it takes to show up at five AM for a workout is exactly the same discipline it takes to show up for your business. Your body and your bank account are built by the same habit. You cannot separate them. Work on both.",
    },
    {
        "id": "b3_advice",
        "hook": "THIS IS NOT LAMBORGHINIS",
        "hook_tts": "Andy says this isn't just Lamborghinis and balling out. This is a grind.",
        "mode": "B",
        "source_quotes": [
            {"start": 392.3, "end": 398.2},
            {"start": 398.2, "end": 401.8},
        ],
        "commentary_tts": "Andy Frisella has spent his whole life encouraging young entrepreneurs. He says this isn't just about Lamborghinis and balling out. This is hard. It's a grind. And just because it's hard doesn't mean you're doing it wrong. It means you're doing it right. Anybody can learn the skills. Anybody can learn to be resilient. But you have to be willing to pay the price. And that price is often left out of what you see on the internet. Every single person hearing this has the ability to be great. But greatness requires sacrifice. Are you willing to pay that price?",
    },
]


# ── Mode A: concat all audio as WAV, render frames sequentially, encode once ──
async def render_variant_a(narr, hook_text, idx, out_dir):
    vid_id = f"exp{idx:02d}_{narr['id']}_A"
    print(f"  Mode A: {vid_id}")

    frames_dir = TMPDIR / f"{vid_id}_frames"
    frames_dir.mkdir(exist_ok=True)

    # Track total frames and audio segments
    total_frames = 0
    audio_segments = []

    # --- Hook section ---
    hook_audio = TMPDIR / f"{vid_id}_hook.wav"
    hook_dur = await gen_tts(narr["hook_tts"], str(hook_audio))
    print(f"  Hook: {hook_dur:.1f}s")
    audio_segments.append((str(hook_audio), hook_dur))
    tf_hook = int(hook_dur * FPS)

    # Preview frame for hook background
    preview = TMPDIR / f"{vid_id}_preview.jpg"
    first_seg = narr["segments"][0]
    subprocess.run(["ffmpeg", "-y", "-ss", str(first_seg["start"] + 1), "-i", SRC_MP4,
        "-vframes", "1", "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", str(preview)], capture_output=True)
    bg = Image.open(preview).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

    for i in range(tf_hook):
        t = i / FPS
        progress = t / hook_dur
        # Darken progressively + Ken Burns
        overlay = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        darkened = Image.blend(bg, overlay, 0.5 + 0.3 * progress)
        zoom = 1.0 + 0.03 * progress
        bw, bh = int(WIDTH / zoom), int(HEIGHT / zoom)
        bx = (WIDTH - bw) // 2
        by = int((HEIGHT - bh) * 0.3 * progress)
        frame = darkened.crop((bx, by, bx + bw, by + bh)).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(frame)
        scale = min(1.0, progress * 3)
        if scale > 0:
            fsz = max(1, int(60 * scale))
            fo = font(fsz)
            bbox = draw.textbbox((0, 0), hook_text, font=fo)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            draw.rectangle([(WIDTH - tw)//2 - 20, 400, (WIDTH + tw)//2 + 20, 400 + th + 30], fill=(0,0,0))
            draw.text(((WIDTH - tw)//2, 410), hook_text, font=fo, fill=C_GOLD)
        frame.save(frames_dir / f"f_{total_frames+i:06d}.png")
    total_frames += tf_hook
    preview.unlink(missing_ok=True)

    # --- Source segments ---
    for si, seg in enumerate(narr["segments"]):
        # Extract frames
        seg_fd = TMPDIR / f"{vid_id}_seg{si}"
        seg_fd.mkdir(exist_ok=True)
        extract_segment_frames(seg["start"], seg["end"], seg_fd)

        # Extract audio as WAV
        seg_audio = TMPDIR / f"{vid_id}_seg{si}.wav"
        extract_segment_audio(seg["start"], seg["end"], seg_audio)
        seg_dur = seg["end"] - seg["start"]
        print(f"  Seg {si}: {seg['start']:.1f}-{seg['end']:.1f} ({seg_dur:.1f}s)")
        audio_segments.append((str(seg_audio), seg_dur))

        # Copy frames with darkened overlay
        seg_frames = sorted(seg_fd.glob("f_*.jpg"))
        for fpath in seg_frames:
            fg = Image.open(fpath).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
            overlay = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
            fg = Image.blend(fg, overlay, 0.3)
            fg.save(frames_dir / f"f_{total_frames:06d}.png")
            total_frames += 1
        shutil.rmtree(seg_fd, ignore_errors=True)

    # --- CTA section ---
    cta_audio = TMPDIR / f"{vid_id}_cta.wav"
    cta_dur = await gen_tts(narr["cta_tts"], str(cta_audio))

    # Pad CTA if total < 30s (use NEW text, don't repeat CTA)
    full_hook_new = False
    if hook_dur + sum(s["end"]-s["start"] for s in narr["segments"]) + cta_dur < 30:
        extra_audio = TMPDIR / f"{vid_id}_extra.wav"
        extra_text = "That's the reality. Let that sink in."
        extra_dur = await gen_tts(extra_text, str(extra_audio))
        # Append to CTA audio
        merged_cta = TMPDIR / f"{vid_id}_cta_merged.wav"
        subprocess.run([
            "ffmpeg", "-y", "-i", str(cta_audio), "-i", str(extra_audio),
            "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[out]",
            "-map", "[out]", str(merged_cta)
        ], capture_output=True)
        r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(merged_cta)], capture_output=True, text=True)
        cta_dur = float(r.stdout.strip()) if r.stdout.strip() else cta_dur
        cta_audio.unlink(missing_ok=True)
        cta_audio = merged_cta
        extra_audio.unlink(missing_ok=True)

    audio_segments.append((str(cta_audio), cta_dur))
    print(f"  CTA: {cta_dur:.1f}s")

    # CTA frames
    last_seg = narr["segments"][-1]
    preview_last = TMPDIR / f"{vid_id}_preview_last.jpg"
    subprocess.run(["ffmpeg", "-y", "-ss", str(last_seg["end"] - 1), "-i", SRC_MP4,
        "-vframes", "1", "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", str(preview_last)], capture_output=True)
    bg_last = Image.open(preview_last).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    tf_cta = int(cta_dur * FPS)

    for i in range(tf_cta):
        t = i / FPS
        progress = t / cta_dur
        overlay = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        darkened = Image.blend(bg_last, overlay, 0.6)
        zoom = 1.0 + 0.03 * progress
        bw, bh = int(WIDTH / zoom), int(HEIGHT / zoom)
        bx = (WIDTH - bw) // 2
        frame = darkened.crop((bx, 0, bx + bw, bh)).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(frame)
        scale = min(1.0, progress * 3)
        if scale > 0:
            fsz = max(1, int(48 * scale))
            fo = font(fsz)
            lines = [narr["cta_tts"][i:i+40] for i in range(0, len(narr["cta_tts"]), 40)]
            for li, line in enumerate(lines[:4]):
                bbox = draw.textbbox((0, 0), line, font=fo)
                tw = bbox[2] - bbox[0]
                y = 1200 + li * 60
                draw.text(((WIDTH - tw)//2, y), line, font=fo, fill=C_WHITE)
        frame.save(frames_dir / f"f_{total_frames+i:06d}.png")
    total_frames += tf_cta
    preview_last.unlink(missing_ok=True)

    # --- Concat all audio segments into one WAV ---
    full_audio = TMPDIR / f"{vid_id}_full.wav"
    if len(audio_segments) > 1:
        inputs = []
        for ap, _ in audio_segments:
            inputs += ["-i", str(ap)]
        filter_parts = [f"[{i}:a]" for i in range(len(audio_segments))]
        filter_complex = "".join(filter_parts) + f"concat=n={len(audio_segments)}:v=0:a=1[out]"
        subprocess.run(["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_complex, "-map", "[out]"] + AUDIO_PARAMS + [str(full_audio)], capture_output=True)
    else:
        shutil.copy(audio_segments[0][0], full_audio)

    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(full_audio)], capture_output=True, text=True)
    full_dur = float(r.stdout.strip()) if r.stdout.strip() else 0
    print(f"  Full audio: {full_dur:.1f}s")

    # --- Encode once ---
    out_path = out_dir / f"{vid_id}.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS), "-i", str(frames_dir / "f_%06d.png"),
        "-i", str(full_audio),
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-shortest", str(out_path)
    ], capture_output=True)

    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(out_path)], capture_output=True, text=True)
    final_dur = float(r.stdout.strip())
    size_mb = out_path.stat().st_size / 1024 / 1024
    print(f"  ✅ {out_path.name} ({final_dur:.1f}s, {size_mb:.1f}MB)")

    # Cleanup
    shutil.rmtree(frames_dir, ignore_errors=True)
    for ap, _ in audio_segments:
        Path(ap).unlink(missing_ok=True)
    full_audio.unlink(missing_ok=True)

    return final_dur, size_mb


# ── Mode B: TTS commentary + source quotes as accent ──
async def render_variant_b(narr, hook_text, idx, out_dir):
    vid_id = f"exp{idx:02d}_{narr['id']}_B"
    print(f"  Mode B: {vid_id}")

    # 1. Generate TTS hook
    hook_audio = TMPDIR / f"{vid_id}_hook.wav"
    hook_dur = await gen_tts(narr["hook_tts"], str(hook_audio))
    print(f"  Hook TTS: {hook_dur:.1f}s")

    # 2. Split commentary for concat with quotes
    tts_words = narr["commentary_tts"].split()
    split1 = len(tts_words) // 3
    split2 = 2 * len(tts_words) // 3
    tts_parts = [
        " ".join(tts_words[:split1]),
        " ".join(tts_words[split1:split2]),
        " ".join(tts_words[split2:]),
    ]

    tts_files = []
    for pi, txt in enumerate(tts_parts):
        if not txt.strip():
            continue
        pf = TMPDIR / f"{vid_id}_tts{pi}.wav"
        pdur = await gen_tts(txt, str(pf))
        tts_files.append((pf, pdur))
        print(f"  TTS part {pi}: {pdur:.1f}s ({len(txt.split())} words)")

    # 3. Extract source quote audio
    quote_audios = []
    total_quote_dur = 0
    for qi, q in enumerate(narr["source_quotes"]):
        qa = TMPDIR / f"{vid_id}_quote{qi}.wav"
        extract_segment_audio(q["start"], q["end"], qa)
        r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(qa)], capture_output=True, text=True)
        qd = float(r.stdout.strip()) if r.stdout.strip() else 0
        quote_audios.append(qa)
        total_quote_dur += qd
    print(f"  Source quotes: {len(quote_audios)} ({total_quote_dur:.1f}s)")

    # 4. Concat: hook→TTS0→quote0→TTS1→quote1→TTS2
    concat_audio = TMPDIR / f"{vid_id}_concat.wav"
    concat_paths = [hook_audio, tts_files[0][0]]
    if quote_audios:
        concat_paths.append(quote_audios[0])
    concat_paths.append(tts_files[1][0])
    if len(quote_audios) > 1:
        concat_paths.append(quote_audios[1])
    if len(tts_files) > 2:
        concat_paths.append(tts_files[2][0])

    inputs = []
    for ap in concat_paths:
        inputs += ["-i", str(ap)]
    filter_parts = [f"[{i}:a]" for i in range(len(concat_paths))]
    filter_complex = "".join(filter_parts) + f"concat=n={len(concat_paths)}:v=0:a=1[out]"
    subprocess.run(["ffmpeg", "-y"] + inputs + [
        "-filter_complex", filter_complex, "-map", "[out]"
    ] + AUDIO_PARAMS + [str(concat_audio)], capture_output=True)

    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(concat_audio)], capture_output=True, text=True)
    final_audio_dur = float(r.stdout.strip()) if r.stdout.strip() else 0
    print(f"  Mixed audio: {final_audio_dur:.1f}s")

    # 5. Render video frames
    fd = TMPDIR / f"{vid_id}_frames"
    fd.mkdir(exist_ok=True)
    tf = int(final_audio_dur * FPS)

    # Extract wide window of source frames
    src_fd = TMPDIR / f"{vid_id}_src"
    src_fd.mkdir(exist_ok=True)
    start_window = max(0, narr["source_quotes"][0]["start"] - 25)
    end_window = min(1152.0, narr["source_quotes"][-1]["end"] + 35)
    window_dur = end_window - start_window
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(start_window), "-i", SRC_MP4,
        "-t", str(window_dur),
        "-vf", f"fps=10,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-an", "-q:v", "2", str(src_fd / "f_%05d.jpg")
    ], capture_output=True)

    all_src = sorted(src_fd.glob("*.jpg"))
    src_count = len(all_src)
    print(f"  Source frames: {src_count} ({window_dur:.0f}s window at 10fps)")

    for i in range(tf):
        t = i / FPS
        if all_src:
            src_pos = (t / final_audio_dur) * src_count
            fi = min(int(src_pos), src_count - 1)
            bg = Image.open(all_src[fi]).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        else:
            bg = Image.new("RGB", (WIDTH, HEIGHT), C_BLACK)
        overlay = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        bg = Image.blend(bg, overlay, 0.35)
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
            draw.rectangle([(WIDTH - tw)//2 - 15, 100, (WIDTH + tw)//2 + 15, 180], fill=(0,0,0))
            draw.text(((WIDTH - tw)//2, 110), hook_text, font=fo, fill=C_GOLD)

        bar_w = int(WIDTH * t / final_audio_dur)
        draw.rectangle([0, HEIGHT - 8, bar_w, HEIGHT], fill=C_CYAN)
        bg.save(fd / f"f_{i:05d}.png")

    # 6. Encode video
    out_path = out_dir / f"{vid_id}.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS), "-i", str(fd / "f_%05d.png"),
        "-i", str(concat_audio),
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-shortest", str(out_path)
    ], capture_output=True)

    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(out_path)], capture_output=True, text=True)
    final_dur = float(r.stdout.strip())
    size_mb = out_path.stat().st_size / 1024 / 1024
    print(f"  ✅ {out_path.name} ({final_dur:.1f}s, {size_mb:.1f}MB)")

    # Cleanup
    shutil.rmtree(fd, ignore_errors=True)
    shutil.rmtree(src_fd, ignore_errors=True)
    hook_audio.unlink(missing_ok=True)
    concat_audio.unlink(missing_ok=True)
    for pf, _ in tts_files:
        pf.unlink(missing_ok=True)
    for qa in quote_audios:
        qa.unlink(missing_ok=True)

    return final_dur, size_mb


async def main():
    print("🎮 Hybrid Audio Exploration v6 — all audio 44100Hz mono, single-pass encode")
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
