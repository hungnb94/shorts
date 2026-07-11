#!/usr/bin/env python3
"""Bac si Hai — 1 Short v5: new source (AGBrXy-2SxI), single contiguous VO segment.

Fixes vs v4 (root-caused by ADR-0017/0018 after v4's 8.6%-stayed failure):
- Paths updated to output/projects/bacsihai/{source,clips,final} (v4's output/bacsihai_fasting
  and output/shorts/bacsihai no longer exist).
- zoompan motion ported from render_hardknocks_v1.py (v4's base plate had zero motion;
  this source is a static-camera livestream, so continuous motion is needed for ADR-0018).
- Word-burst hook captions for t=0-5s, built from this video's actual mlx_whisper word
  timestamps (not a copied English-benchmark cadence, per ADR-0018's explicit caveat).
- Body captions tightened to ~4-5s blocks (v4 used ~8-9s).
- 2 value-adds for the Transformative Gate (ADR-0007): animated_annotation (emoji, v4's
  keyword-matching mechanism, keywords fixed to match accented Vietnamese text) +
  data_viz_overlay (qualitative comparison card — source gives no percentage, so the
  card states the claim qualitatively, not a fabricated number).
"""
import subprocess, shutil
from pathlib import Path

SRC = Path("output/projects/bacsihai/source/AGBrXy-2SxI_1080p.mp4")
O = Path("output/projects/bacsihai/final")
T = Path("output/projects/bacsihai/clips/temp_v5")
EMOJI_DIR = Path("output/shared/emoji_processed")
FONT = "/System/Library/Fonts/Helvetica.ttc"
FONT_BOLD = "/System/Library/Fonts/HelveticaNeue.ttc"
CROP = "scale=-2:1920,crop=1080:1920:(in_w-1080)/2:0"

O.mkdir(parents=True, exist_ok=True)
T.mkdir(parents=True, exist_ok=True)

VID = "2026-07-10-lao_dong_tay_v5"  # date-prefixed per AGENTS.md convention
SRC_START = 314.36
SRC_END = 367.00

HOOK = "LAO ĐỘNG CHÂN TAY ÍT BỊ ALZHEIMER HƠN?"
CTA = "THEO DÕI ĐỂ BIẾT THÊM BÍ QUYẾT SỐNG THỌ"

# Word-burst hook captions, t=0-6s, timestamps taken directly from mlx_whisper word-level
# output for this segment (abs time - SRC_START). Cadence ~1-1.3s, derived from actual
# Vietnamese speech pace, per ADR-0018's caveat not to reuse the English benchmark constant.
HOOK_BURSTS = [
    (0.00, 0.98, "NHƯNG MÀ CÁI VẤN ĐỀ Ở ĐÂY", False),
    (0.98, 1.80, "LÀ CON NGƯỜI NGÀY XƯA", False),
    (1.80, 3.10, "CHÚNG TA VẬN ĐỘNG,", True),
    (3.82, 4.84, "CHÚNG TA LAO ĐỘNG", True),
    (4.84, 6.00, "THÌ ĐÚNG HƠN.", False),
]

# Body captions, t=6s onward, tightened to ~4-5s blocks (vs v4's ~8-9s), aligned to the
# source's real sentence boundaries (abs time - SRC_START).
BODY_SUBS = [
    (8.36, 11.20, "Vấn đề là lao động bằng đôi bàn tay"),
    (12.12, 18.36, "Có một thông tin rất thú vị cần biết"),
    (18.36, 23.44, "Là những người lao động bằng tay — nghĩa đen"),
    (23.96, 28.02, "Không phải kiểu 'lao động trí óc' tính luôn đâu"),
    (28.18, 32.64, "Mà là người thực sự dùng tay để làm việc"),
    (33.30, 39.72, "Tỉ lệ mắc Parkinson"),
    (39.72, 42.74, "hay Alzheimer..."),
    (43.22, 48.70, "Thấp hơn rất nhiều ở nhóm lao động tay"),
    (48.70, 52.64, "So với người lao động trí óc."),
]

# animated_annotation: keyword -> emoji. Keywords are exact lowercase substrings of the
# caption text above (v4's keyword lists used unaccented forms like "duong" against
# accented captions like "đường", which never match — fixed here by matching accented text).
EMOJI_RULES = [
    (["tay", "vận động", "lao động"], "1f4aa_1f4aa.png", "right_top"),
    (["parkinson", "alzheimer", "trí óc"], "1f9e0_1f9e0.png", "left_top"),
]

# data_viz_overlay: qualitative comparison card (source gives no percentage — "thấp hơn
# rất nhiều", not a number — so the card states the claim qualitatively, not a fabricated
# stat, to stay fact-check-safe).
STAT_CARD_START = 33.30
STAT_CARD_END = 48.70


def dur(p):
    if not p.exists():
        return 0.0
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
        capture_output=True, text=True, timeout=15)
    return float(r.stdout.strip()) if r.stdout.strip() else 0.0


def esc(s):
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’")


def drawtext(text, y, size=28, color="white", enable=None, box=True,
             x="(w-text_w)/2", font=FONT):
    t = esc(text)
    parts = [f"drawtext=text='{t}'", f"fontfile={font}", f"fontsize={size}",
              f"fontcolor={color}", "borderw=3", "bordercolor=black@0.8",
              f"x={x}", f"y={y}"]
    if box:
        parts += ["box=1", "boxcolor=black@0.55", "boxborderw=10"]
    if enable:
        parts.append(f"enable='{enable}'")
    return ":".join(parts)


def extract_segment(src, start, end, out):
    """Extract the ONE contiguous segment, center-crop to 1080x1920, add zoompan motion
    (ported from render_hardknocks_v1.py — this source is a static-camera livestream, v4's
    base plate had no motion at all, which fails ADR-0018's continuous-motion requirement)."""
    duration = end - start
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start), "-i", str(src),
        "-t", str(duration),
        "-vf", f"{CROP},zoompan=z='min(zoom+0.0006,1.08)':d=1:s=1080x1920:fps=30",
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        str(out)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        print(f"  EXTRACT ERROR: {r.stderr[-500:]}")
    return out


def render():
    print(f"\n{'='*55}\n  {VID}\n{'='*55}")
    d = T

    print("  Extracting contiguous segment (with zoompan motion)...")
    raw = d / "raw.mp4"
    extract_segment(SRC, SRC_START, SRC_END, raw)
    raw_dur = dur(raw)
    print(f"  Segment: {raw_dur:.2f}s (VO continuous)")

    # Find which emoji this video actually uses (only load inputs we need)
    all_subs_text = " ".join(txt for _, _, txt in BODY_SUBS).lower()
    used_emojis = []
    for keywords, fn, pos in EMOJI_RULES:
        if any(kw in all_subs_text for kw in keywords):
            if fn not in used_emojis:
                used_emojis.append(fn)

    pos_map = {
        "right_top": ("W-w-60", "260"),
        "right_mid": ("W-w-60", "h/2-220"),
        "left_top": ("60", "260"),
        "left_mid": ("60", "h/2-220"),
    }

    inputs = ["-i", str(raw)]
    input_idx = 1
    fc_parts = []
    emoji_input_map = {}
    for fn in used_emojis:
        epath = EMOJI_DIR / fn
        if not epath.exists():
            print(f"  WARNING: emoji asset missing: {epath}")
            continue
        inputs += ["-i", str(epath)]
        fc_parts.append(f"[{input_idx}:v]scale=280:280[em_{fn}]")
        emoji_input_map[fn] = input_idx
        input_idx += 1

    prev_tag = "0:v"
    chain_count = 0
    for st, et, txt in BODY_SUBS:
        txt_lower = txt.lower()
        for keywords, fn, pos in EMOJI_RULES:
            if fn not in emoji_input_map:
                continue
            if any(kw in txt_lower for kw in keywords):
                em_tag = f"em_{fn}"
                x_expr, y_expr = pos_map[pos]
                chain_count += 1
                new_tag = f"ev{chain_count}"
                fc_parts.append(
                    f"[{prev_tag}][{em_tag}]overlay=x='{x_expr}':y='{y_expr}'"
                    f":enable='between(t,{st},{et})'[{new_tag}]"
                )
                prev_tag = new_tag
                break

    # Hook word-bursts (t=0-6s), one keyword per burst emphasized in yellow
    burst_parts = []
    for st, et, txt, emphasize in HOOK_BURSTS:
        color = "yellow" if emphasize else "white"
        burst_parts.append(drawtext(txt, y=160, size=36, color=color,
                                     enable=f"between(t,{st},{et})", box=True))

    # Body captions (t=6s onward)
    sub_parts = []
    for st, et, txt in BODY_SUBS:
        sub_parts.append(drawtext(txt, y="h-200", size=28, color="white",
                                   enable=f"between(t,{st},{et})", box=True))

    # data_viz_overlay: qualitative comparison stat card during the Parkinson/Alzheimer reveal
    stat_parts = [
        drawtext("LAO ĐỘNG TAY  vs  TRÍ ÓC", y=90, size=40, color="white",
                  enable=f"between(t,{STAT_CARD_START},{STAT_CARD_END})", font=FONT_BOLD),
        drawtext("NGUY CƠ PARKINSON & ALZHEIMER THẤP HƠN", y=170, size=26, color="0x7CFC00",
                  enable=f"between(t,{STAT_CARD_START},{STAT_CARD_END})", font=FONT_BOLD),
    ]

    chain_count += 1
    final_tag = "final"
    all_text_parts = burst_parts + sub_parts + stat_parts + [
        drawtext(HOOK, y=90, size=34, color="yellow",
                 enable="between(t,0,6)", font=FONT_BOLD),
        drawtext(CTA, y="h-70", size=22, color="white",
                 enable=f"between(t,{max(raw_dur-5,0):.1f},{raw_dur:.1f})"),
        f"drawbox=x=0:y=ih-4:w=iw*t/{raw_dur:.1f}:h=4:color=0xFF4500:t=fill",
    ]
    fc_parts.append(f"[{prev_tag}]{','.join(all_text_parts)}[{final_tag}]")

    fc = ";".join(fc_parts)

    print("  Applying overlays...")
    fv = d / "fv.mp4"
    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", fc,
        "-map", f"[{final_tag}]",
        "-c:v", "libx264", "-crf", "20", "-preset", "fast",
        "-an", str(fv)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        err_lines = [l for l in r.stderr.split("\n")
                     if any(x in l.lower() for x in ["error", "invalid", "no such"])]
        err = err_lines[0] if err_lines else r.stderr[-500:]
        print(f"  FILTER ERROR: {err[:500]}")
        return False

    out = O / f"{VID}.mp4"
    cmd = ["ffmpeg", "-y", "-i", str(fv), "-i", str(raw),
           "-map", "0:v", "-map", "1:a",
           "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
           "-shortest", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(f"  MUX ERROR: {r.stderr[-300:]}")
        return False

    od = dur(out)
    mb = out.stat().st_size / 1_048_576
    print(f"  => {out.name}: {od:.1f}s, {mb:.1f}MB")

    a_check = subprocess.run(
        ["ffprobe", "-v", "quiet", "-select_streams", "a",
         "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(out)],
        capture_output=True, text=True)
    if "audio" not in a_check.stdout:
        print(f"  WARNING: No audio stream!")
        return False
    print(f"  Audio: OK")
    return True


def main():
    print("="*60 + "\n  BAC SI HAI — 1 SHORT v5 (contiguous VO, new source)\n" + "="*60)
    ok = render()
    print(f"\n{'='*60}\n  {'OK' if ok else 'FAIL'}\n{'='*60}")
    shutil.rmtree(T, ignore_errors=True)


if __name__ == "__main__":
    main()
