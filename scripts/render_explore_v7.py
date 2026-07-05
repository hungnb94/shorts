#!/usr/bin/env python3
"""
Hybrid Audio Renderer v7 — SoHK Patterns Applied.
Mode A only: TTS hook + source verbatim audio segments + TTS CTA/padding.
6 new narratives using School of Hard Knocks title patterns (MONEY+NUMBER, THIS, Contrarian, Authority).
"""
import json, subprocess, asyncio, random, shutil, edge_tts
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

PROJECT = Path("/Users/hung/code/ai/shorts")
OUTDIR  = PROJECT / "output" / "explore_v7"
OUTDIR.mkdir(parents=True, exist_ok=True)
TMPDIR  = PROJECT / "output" / "tmp_explore7"
TMPDIR.mkdir(parents=True, exist_ok=True)

SRC_MP4    = str(PROJECT / "output/source/2eicF3iPf1s.mp4")
SRC_WEBM   = str(PROJECT / "output/source/2eicF3iPf1s.webm")
SRC_AUDIO  = TMPDIR / "source_full.wav"

FPS    = 30
WIDTH   = 1080
HEIGHT  = 1920
AUDIO_PARAMS = ["-ac", "1", "-ar", "44100"]

# Colors
BG      = (0, 0, 0)
ACCENT  = (50, 255, 130)
WHITE   = (255, 255, 255)
DIM     = (160, 160, 160)
DARK_BG = (10, 10, 10)

try:
    FONT_BOLD = str(Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"))
    FONT      = str(Path("/System/Library/Fonts/Supplemental/Arial.ttf"))
except:
    FONT_BOLD = str(Path("/System/Library/Fonts/Helvetica.ttc"))
    FONT      = str(Path("/System/Library/Fonts/Helvetica.ttc"))

# ═══════════════════════════════════════════════════════════════
# NARRATIVES — 6 new videos using SoHK title patterns
# All Mode A: TTS hook → source verbatim segments → TTS CTA
# ═══════════════════════════════════════════════════════════════

NARRATIVES = [
    # ── #1: MONEY+NUMBER — "$58,380 in 10 Years" ──
    {
        "id": "new1_10year",
        "hook": "HE MADE $58,380 IN 10 YEARS",
        "hook_tts": "He made fifty eight thousand, three hundred and eighty dollars in ten years. Then he built a billion dollar company.",
        "mode": "A",
        "segments": [
            {"start": 349.9, "end": 354.0},   # first 3 years didn't make any money
            {"start": 354.0, "end": 363.1},   # first 10 years total I made $58,380
            {"start": 363.1, "end": 367.6},   # worked other jobs, bartending, side hustles
            {"start": 367.6, "end": 371.7},   # first couple of years we lived in the back of our store
        ],
        "cta_tts": "Ten years of grinding. Most people would have quit. He didn't. That's the difference between those who make it and those who don't.",
    },

    # ── #2: THIS — "THIS Is the Real Secret of Success" ──
    {
        "id": "new2_secret",
        "hook": "THIS IS THE REAL SECRET OF SUCCESS",
        "hook_tts": "You want to know the real secret of success? It's not talent. It's not luck. It's this.",
        "mode": "A",
        "segments": [
            {"start": 413.9, "end": 418.1},   # anybody out there can learn skills
            {"start": 418.1, "end": 422.8},   # learn to be resilient and gritty and tough
            {"start": 422.8, "end": 427.3},   # required to win
            {"start": 427.3, "end": 432.1},   # ability to be great as long as willing to pay the price
        ],
        "cta_tts": "Skills can be learned. Resilience can be built. Greatness is available to everyone. The only question is: are you willing to pay the price?",
    },

    # ── #3: Contrarian — "Why CEOs Build Weak Cultures" ──
    {
        "id": "new3_culture",
        "hook": "GOOD CULTURE ISN'T MADE IN THE GAME",
        "hook_tts": "Most CEOs think culture is built in the boardroom. Andy says it's built somewhere else entirely.",
        "mode": "A",
        "segments": [
            {"start": 259.6, "end": 263.7},   # good culture isn't made in the game
            {"start": 263.7, "end": 267.8},   # made in those hard times, struggling together
            {"start": 238.0, "end": 242.2},   # mutual suffering
            {"start": 233.8, "end": 237.9},   # huge correlation, you asked about culture
        ],
        "cta_tts": "Culture isn't built when things are easy. It's forged in the struggle. When everybody suffers together, that's when you build something real.",
    },

    # ── #4: THIS + Emotional — "A 20-Year-Old Sacrificed Everything" ──
    {
        "id": "new4_sacrifice",
        "hook": "A 20-YEAR-OLD SACRIFICED EVERYTHING",
        "hook_tts": "While you're complaining about your job, a twenty year old stormed the beaches of Normandy. That's perspective.",
        "mode": "A",
        "segments": [
            {"start": 827.6, "end": 832.8},   # my family made big sacrifices
            {"start": 833.4, "end": 839.5},   # grandma pregnant when he went to WWII, stormed D-Day
            {"start": 851.0, "end": 855.4},   # owe those men and women
            {"start": 855.4, "end": 860.4},   # if a 20-year-old man can sacrifice everything
        ],
        "cta_tts": "If a twenty year old can sacrifice his entire future for this country, you can push through your discomfort. That's the real meaning of hard work.",
    },

    # ── #5: MONEY+NUMBER + THIS — "$2.5M Car" ──
    {
        "id": "new5_car",
        "hook": "HE OWNS A $2.5 MILLION CAR",
        "hook_tts": "A two and a half million dollar car. And Andy says it's not even his favorite one.",
        "mode": "A",
        "segments": [
            {"start": 1108.3, "end": 1113.3}, # 69 charger Daytona, worth $2.5M
            {"start": 1041.6, "end": 1047.0}, # 70s Chevelle, thought was the coolest car ever made
            {"start": 1047.0, "end": 1051.4}, # out of all the cars, that's the one
            {"start": 1055.2, "end": 1059.5}, # if I was a car, I would be this car
        ],
        "cta_tts": "A two and a half million dollar car sits in his garage. But his favorite? A seventy Chevelle. Because it reminds him where he came from.",
    },

    # ── #6: Authority — "I Was Never Meant for the Ordinary" ──
    {
        "id": "new6_ordinary",
        "hook": "I KNEW I WAS MEANT FOR MORE",
        "hook_tts": "Andy Frisella knew he wasn't meant for a normal life. Here's how he knew.",
        "mode": "A",
        "segments": [
            {"start": 536.3, "end": 540.4},   # I knew I was going to do something
            {"start": 540.4, "end": 544.6},   # not meant for everything else
            {"start": 548.5, "end": 552.7},   # right out of high school, college for one semester
            {"start": 552.7, "end": 557.0},   # this is not for me, started retail store
        ],
        "cta_tts": "Most people settle for the life they're given. Andy refused. That one decision changed everything. The question is: what are you settling for?",
    },
]


# ── Utils ──
def extract_audio_44100(src, out):
    """Extract audio from source as 44100Hz mono WAV."""
    subprocess.run([
        "ffmpeg", "-y", "-i", src,
        "-ac", "1", "-ar", "44100", "-sample_fmt", "s16",
        str(out)
    ], capture_output=True, check=True)

def ensure_source_audio():
    """Ensure source audio is extracted once."""
    if not SRC_AUDIO.exists():
        print("  Extracting source audio (44100Hz mono)...")
        try:
            extract_audio_44100(SRC_WEBM, SRC_AUDIO)
        except:
            extract_audio_44100(SRC_MP4, SRC_AUDIO)

async def gen_tts(text, out_path):
    """Generate TTS audio, return duration in seconds."""
    out_path = Path(out_path) if not isinstance(out_path, Path) else out_path
    wav_path = out_path.with_suffix(".wav")
    mp3_path = out_path.with_suffix(".mp3")
    communicate = edge_tts.Communicate(text, voice="en-US-GuyNeural")
    await communicate.save(str(mp3_path))
    subprocess.run([
        "ffmpeg", "-y", "-i", str(mp3_path),
        "-ac", "1", "-ar", "44100", "-sample_fmt", "s16",
        str(wav_path)
    ], capture_output=True, check=True)
    mp3_path.unlink(missing_ok=True)
    dur = float(subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(wav_path)
    ], capture_output=True, text=True).stdout.strip())
    return dur


def get_duration(path):
    return float(subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(path)
    ], capture_output=True, text=True).stdout.strip())


# ── Frame gen ──
def gen_frame_image(text, hook=False, cta=False):
    """Generate a single 1080x1920 frame with centered quote layout."""
    img = Image.new("RGB", (WIDTH, HEIGHT), DARK_BG)
    draw = ImageDraw.Draw(img)

    # Subtle gradient overlay
    for y in range(HEIGHT):
        alpha = int(20 * (1 - y / HEIGHT))
        c = tuple(max(0, v - alpha) for v in DARK_BG)
        draw.line([(0, y), (WIDTH, y)], fill=c)

    if hook:
        font_size = 72
        color = ACCENT
    elif cta:
        font_size = 52
        color = ACCENT
    else:
        font_size = 56
        color = WHITE

    try:
        font = ImageFont.truetype(FONT_BOLD if hook or cta else FONT, font_size)
        font2 = ImageFont.truetype(FONT if not hook and not cta else FONT_BOLD, 28)
    except:
        font = ImageFont.load_default()
        font2 = ImageFont.load_default()

    # Word-wrap text
    words = text.split()
    lines = []
    current = ""
    for w in words:
        test = current + " " + w if current else w
        bbox = draw.textbbox((0, 0), test, font=font)
        tw = bbox[2] - bbox[0]
        if tw > WIDTH - 160 and current:
            lines.append(current)
            current = w
        else:
            current = test
    if current:
        lines.append(current)

    total_h = sum(draw.textbbox((0, 0), l, font=font)[3] - draw.textbbox((0, 0), l, font=font)[1] for l in lines)
    total_h += (len(lines) - 1) * 12
    y_start = (HEIGHT - total_h) // 2 - 40

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        x = (WIDTH - lw) // 2
        # Subtle shadow
        draw.text((x+2, y_start+2), line, font=font, fill=(0, 0, 0))
        draw.text((x, y_start), line, font=font, fill=color)
        lh = bbox[3] - bbox[1]
        y_start += lh + 12

    # Attribution bar
    attr = "Andy Frisella — First Form"
    ab = draw.textbbox((0, 0), attr, font=font2)
    draw.text((WIDTH - ab[2] - 60, HEIGHT - 80), attr, font=font2, fill=DIM)

    return img


def render_frames(texts, prefix):
    """Render list of text strings as PNG frames, return all paths."""
    paths = []
    for fi, txt in enumerate(texts):
        fpath = TMPDIR / f"{prefix}_f{fi:06d}.png"
        if fpath.exists():
            paths.append(str(fpath))
            continue
        img = gen_frame_image(txt, hook=(fi == 0), cta=(fi == len(texts)-1))
        img.save(fpath)
        paths.append(str(fpath))
    return paths


# ── Render variant A (Mode A: verbatim segments) ──
async def render_variant_a(narr, hook_text, idx, out_dir):
    vid_id = f"exp{idx:02d}_{narr['id']}_A"
    out_path = Path(out_dir) / f"{vid_id}.mp4"
    if out_path.exists():
        dur = get_duration(str(out_path))
        mb = out_path.stat().st_size / 1_048_576
        print(f"  ✅ Already exists: {vid_id} ({dur:.1f}s, {mb:.1f}MB)")
        return dur, mb

    print(f"  Mode A: {vid_id}")

    # 1. Generate TTS hook
    hook_audio = TMPDIR / f"{vid_id}_hook.wav"
    hook_dur = await gen_tts(narr["hook_tts"], str(hook_audio))
    print(f"  Hook: {hook_dur:.1f}s")

    # 2. Extract segments from source audio
    seg_audios = []
    for si, seg in enumerate(narr["segments"]):
        seg_path = TMPDIR / f"{vid_id}_seg{si}.wav"
        subprocess.run([
            "ffmpeg", "-y", "-i", str(SRC_AUDIO),
            "-ss", str(seg["start"]), "-to", str(seg["end"]),
            "-ac", "1", "-ar", "44100",
            str(seg_path)
        ], capture_output=True, check=True)
        seg_audios.append(seg_path)
        dur = seg["end"] - seg["start"]
        print(f"  Seg {si}: {seg['start']:.1f}-{seg['end']:.1f} ({dur:.1f}s)")

    # 3. Generate CTA
    cta_audio = TMPDIR / f"{vid_id}_cta.wav"
    cta_dur = await gen_tts(narr["cta_tts"], str(cta_audio))
    print(f"  CTA: {cta_dur:.1f}s")

    # 4. Check duration and add padding if needed
    total_audio = hook_dur + sum(s["end"] - s["start"] for s in narr["segments"]) + cta_dur

    extra_audio = None
    extra_text = ""
    n_extra = 0
    if total_audio < 30:
        need = 30 - total_audio
        extra_text = "That's the reality. Let that sink in. Think about what that means for you."
        extra_audio = TMPDIR / f"{vid_id}_extra.wav"
        extra_dur = await gen_tts(extra_text, str(extra_audio))
        print(f"  Extra padding: {extra_dur:.1f}s (needed {need:.1f}s)")
        total_audio = hook_dur + sum(s["end"] - s["start"] for s in narr["segments"]) + cta_dur + extra_dur
    else:
        extra_dur = 0

    # 5. Concat all audio as WAV master
    full_audio = TMPDIR / f"{vid_id}_full.wav"

    concat_files = [str(hook_audio)] + [str(s) for s in seg_audios] + [str(cta_audio)]
    if extra_audio:
        concat_files.append(str(extra_audio))

    filter_parts = [f"[{i}:a]" for i in range(len(concat_files))]
    concat_filter = f"\"{' '.join(filter_parts)}concat=n={len(concat_files)}:v=0:a=1[out]\""

    inputs = []
    for cf in concat_files:
        inputs.extend(["-i", cf])

    subprocess.run([
        "ffmpeg", "-y", *inputs,
        "-filter_complex", f"{' '.join(filter_parts)}concat=n={len(concat_files)}:v=0:a=1[out]",
        "-map", "[out]", "-ac", "1", "-ar", "44100",
        str(full_audio)
    ], capture_output=True, check=True)
    print(f"  Full audio: {get_duration(str(full_audio)):.1f}s")

    # 6. Extract segments video frames
    frame_windows = []
    for seg in narr["segments"]:
        win_start = max(0, seg["start"] - 2)
        frame_windows.append((win_start, seg["end"] + 2))

    # 7. Render frames — frame counts driven by ACTUAL audio durations
    hook_text = narr["hook"]
    cta_text = narr["cta_tts"]

    all_frame_texts = []

    # Hook frames — match hook audio duration
    hook_nframes = int(hook_dur * FPS)
    for _ in range(hook_nframes):
        all_frame_texts.append(hook_text)

    # Segment text frames (one text per segment, repeated for its duration)
    for seg_idx, seg in enumerate(narr["segments"]):
        seg_text = f"\"{get_segment_text(seg['start'], seg['end'])}\""
        dur = seg["end"] - seg["start"]
        n_frames = int(dur * FPS)
        for _ in range(n_frames):
            all_frame_texts.append(seg_text)

    # CTA frames — match CTA audio duration
    cta_nframes = int(cta_dur * FPS)
    for _ in range(cta_nframes):
        all_frame_texts.append(cta_text)

    # Extra padding frames if needed
    n_extra = 0
    if extra_audio:
        extra_dur_val = get_duration(str(extra_audio))
        n_extra = int(extra_dur_val * FPS)
        for _ in range(n_extra):
            all_frame_texts.append(extra_text)

    print(f"  Rendering {len(all_frame_texts)} frames...")

    # Render all frames
    frame_paths = []
    for fi, txt in enumerate(all_frame_texts):
        fpath = TMPDIR / f"{vid_id}_f{fi:06d}.png"
        if fpath.exists():
            frame_paths.append(str(fpath))
            continue
        is_hook = fi < hook_nframes
        is_cta = fi >= len(all_frame_texts) - n_extra - cta_nframes and fi < len(all_frame_texts) - n_extra
        img = gen_frame_image(txt, hook=is_hook, cta=is_cta)
        img.save(fpath)
        frame_paths.append(str(fpath))
        if fi % 300 == 0:
            print(f"   ...{fi}/{len(all_frame_texts)} frames")

    # 9. Encode final video (single pass)
    print(f"  Encoding {len(frame_paths)} frames + audio...")
    frames_concat = TMPDIR / f"{vid_id}_frames.txt"
    with open(str(frames_concat), "w") as f:
        for fp in frame_paths:
            f.write(f"file '{fp}'\nduration {1/FPS:.6f}\n")

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(frames_concat),
        "-i", str(full_audio),
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        str(out_path)
    ], capture_output=True, timeout=600)

    final_dur = get_duration(str(out_path))
    size_mb = out_path.stat().st_size / 1_048_576
    print(f"  ✅ {vid_id}.mp4 ({final_dur:.1f}s, {size_mb:.1f}MB)")

    # Cleanup tmp audio
    for p in [hook_audio] + seg_audios + [cta_audio] + ([extra_audio] if extra_audio else []):
        Path(p).unlink(missing_ok=True)
    full_audio.unlink(missing_ok=True)
    frames_concat.unlink(missing_ok=True)

    return final_dur, size_mb


# ── Helper: get segment text from transcript ──
_segment_cache = None
def get_segment_text(start, end):
    global _segment_cache
    if _segment_cache is None:
        with open(str(PROJECT / "output/source/2eic_transcript.json")) as f:
            data = json.load(f)
        _segment_cache = []
        for s in data.get("segments", []):
            _segment_cache.append({
                "start": s["start"],
                "end": s["end"],
                "text": s["text"].strip(),
            })
    # Find the segment that best covers this range
    texts = []
    for seg in _segment_cache:
        if seg["start"] >= start and seg["end"] <= end:
            texts.append(seg["text"])
    if not texts:
        # Fallback: partial overlap
        for seg in _segment_cache:
            if seg["start"] < end and seg["end"] > start:
                texts.append(seg["text"])
    return " ".join(texts) if texts else ""


# ── Main ──
async def main():
    print("🎮 Hybrid Audio Renderer v7 — SoHK Patterns, Mode A only")
    print(f"   Output: {OUTDIR}\n")

    ensure_source_audio()

    results = []
    for i, narr in enumerate(NARRATIVES, 1):
        print(f"\n{'='*60}")
        print(f"  [{i}/6] {narr['id']} (mode {narr['mode']})")
        print(f"  Hook: {narr['hook']}")

        try:
            dur, mb = await render_variant_a(narr, narr["hook"], i, OUTDIR)
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
