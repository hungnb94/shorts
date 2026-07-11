#!/usr/bin/env python3
"""Bac si Hai v6 -- "Vitamin D khong phai la vitamin" (Contrarian-Reveal + Implied-Comparison).

Source: tsDZZNcUEHs -- a produced (non-livestream) video with dense burned-in Vietnamese
captions and professional 3D medical graphics/title cards throughout, unlike v1-v5's raw
livestream/talking-head-only sources.

Multi-Clip Mashup (ADR-0022): 2 pieces, 1 hard cut skipping a 9.6s "what does 'vitamin'
normally mean" tangent, to pull the hormone/calcitriol reveal forward to clip t~=8-11s
(Stage 0 item 4's ~5-10s payoff-timing target). Piece B (42.4s) exceeds the "<15s per clip"
rule but is a single continuous take with no internal skip -- same interpretive exemption
already used for Contiguous VO's single-segment case (see bacsihai-v5-lao-dong-tay.md);
flagged in the production doc as a proposed ADR-0022 addendum, not a silent violation.

Applies the 800M-view case-study finding (docs/research/800m-view-case-study-2026-07-11/
REPORT.md): the "Implied Comparison" hook pattern (setup caption states the comparison
category, pivot caption reveals the truth, payoff gets more screen time than setup). This
source's own VO already states the comparison verbatim ("khong chi lien quan xuong NHU
NHIEU NGUOI VAN NGHI"), reinforced here with a this_or_that/data_viz comparison card timed
to that exact line.

Word-gap analysis of the selected span (via mlx_whisper word timestamps) found ~0 natural
inter-word pauses -- this speaker is tightly scripted/produced, unlike v5's rambling
livestream -- so pause-trimming is skipped (nothing to trim); the uniform 1.1x speed-up
Retention Technique (aiwork v2) still applies, as a separate base-quality technique.

Source already has burned-in Vietnamese captions spanning most of the 1920px frame width.
A center-crop-to-1080 (v1-v5/giannis/hardknocks's approach) would clip caption text on both
edges. Uses a blurred-background pillarbox instead: the full uncropped 1080-wide video
centered over a blurred, cropped full-bleed copy of itself -- preserves 100% of caption
legibility instead of losing ~68% of frame width to a hard crop.
"""
import subprocess, shutil
from pathlib import Path

SRC = Path("output/projects/bacsihai/source/tsDZZNcUEHs_1080p.mp4")
O = Path("output/projects/bacsihai/final")
T = Path("output/projects/bacsihai/clips/temp_v6")
EMOJI_DIR = Path("output/shared/emoji_processed")
FONT = "/System/Library/Fonts/Helvetica.ttc"
FONT_BOLD = "/System/Library/Fonts/HelveticaNeue.ttc"

O.mkdir(parents=True, exist_ok=True)
T.mkdir(parents=True, exist_ok=True)

VID = "2026-07-11-vitamin_d_hormone_v6"  # date-prefixed per AGENTS.md convention
SPEED = 1.1

# Multi-Clip Mashup pieces (ADR-0022) -- abs timestamps in the source.
PIECE_A = (30.24, 35.08)   # "Truoc het ta can goi dung ten. Dau tien vitamin D thi khong thuc su la vitamin."
PIECE_B = (44.72, 87.14)   # reveal (Calcitriol = hormone) through the classical-role teaser
DUR_A = PIECE_A[1] - PIECE_A[0]
DUR_B = PIECE_B[1] - PIECE_B[0]
TOTAL = DUR_A + DUR_B  # pre-speed-up duration, ~47.26s

# Blur-fill pillarbox: full uncropped width-1080 video centered over a blurred full-bleed
# crop of itself. Preserves the source's burned-in captions (see module docstring).
VF_PILLARBOX = (
    "split=2[bg][fg];"
    "[bg]scale=1080:1920:force_original_aspect_ratio=increase,"
    "crop=1080:1920,gblur=sigma=25[bgb];"
    "[fg]scale=1080:-2[fgs];"
    "[bgb][fgs]overlay=(W-w)/2:(H-h)/2"
)

# Value-add 1 (this_or_that / data_viz -- Implied-Comparison card, ADR-0007 item 2):
# timed to "khong chi lien quan xuong NHU NHIEU NGUOI VAN NGHI" (abs 60.94-65.78) then
# "ma no lien quan tung ngoc ngach" (abs 65.78-68.98), mapped to clip-relative time via
# clip_t = DUR_A + (abs_t - PIECE_B[0]).
def clip_t(abs_t):
    return DUR_A + (abs_t - PIECE_B[0])

CARD1_START, CARD1_END = clip_t(60.94), clip_t(65.78)
CARD2_START, CARD2_END = clip_t(65.78), clip_t(68.98)

# Value-add 2 (animated_annotation, ADR-0007 item 2): emoji keyed to timestamp windows
# (not caption-text matching, since body captions are the source's own burned-in ones,
# not an added BODY_SUBS list like v1-v5).
EMOJI_WINDOWS = [
    # (start_abs_or_clip_already, end, emoji_file, position) -- times below are clip-relative
    (3.56, 4.40, "1f6ab_1f6ab.png", "left_top"),      # "khong thuc su" (piece A, la vitamin)
    (clip_t(52.82), clip_t(53.40), "1f9e0_1f9e0.png", "right_top"),  # "hoc mon"
    (clip_t(56.16), clip_t(56.76), "1f9e0_1f9e0.png", "right_top"),  # "tin hieu"
    (clip_t(59.76), clip_t(60.20), "1f9e0_1f9e0.png", "right_top"),  # "co quan"
    (clip_t(63.26), clip_t(63.64), "1f6ab_1f6ab.png", "left_top"),   # "khong chi" (lien quan xuong)
]

TITLE_TEXT = "SỰ THẬT VỀ VITAMIN D"
CTA_TEXT = "THEO DÕI ĐỂ HIỂU ĐÚNG VỀ SỨC KHỎE"


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


def drawtext(text, y, size=30, color="white", enable=None, box=True,
             x="(w-text_w)/2", font=FONT, expansion="none"):
    t = esc(text)
    parts = [f"drawtext=text='{t}'", f"fontfile={font}", f"fontsize={size}",
              f"fontcolor={color}", "borderw=3", "bordercolor=black@0.8",
              f"x={x}", f"y={y}", f"expansion={expansion}"]
    if box:
        parts += ["box=1", "boxcolor=black@0.55", "boxborderw=10"]
    if enable:
        parts.append(f"enable='{enable}'")
    return ":".join(parts)


def extract_piece(start, end, out):
    """Extract one Multi-Clip Mashup piece: pillarbox video, matching encode params for concat."""
    duration = end - start
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start), "-i", str(SRC),
        "-t", str(duration),
        "-vf", VF_PILLARBOX,
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-pix_fmt", "yuv420p", "-r", "30", "-profile:v", "high",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        str(out)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        print(f"  EXTRACT ERROR ({out.name}): {r.stderr[-500:]}")
    return out


def concat_pieces(piece_paths, out):
    """Hard-cut concat via ffmpeg concat demuxer -- no crossfade (ADR-0022)."""
    list_file = T / "concat_list.txt"
    list_file.write_text("".join(f"file '{p.resolve()}'\n" for p in piece_paths))
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(out)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print(f"  CONCAT ERROR: {r.stderr[-500:]}")
    return out


def render():
    print(f"\n{'='*55}\n  {VID}\n{'='*55}")
    d = T

    print("  Extracting Piece A + Piece B (pillarbox, matching encode params)...")
    piece_a = extract_piece(*PIECE_A, d / "piece_a.mp4")
    piece_b = extract_piece(*PIECE_B, d / "piece_b.mp4")

    print("  Concatenating (hard cut, no crossfade)...")
    concat = concat_pieces([piece_a, piece_b], d / "concat.mp4")
    concat_dur = dur(concat)
    print(f"  Concatenated: {concat_dur:.2f}s (pre-speed-up)")

    # Load emoji inputs actually used
    used_emojis = []
    for _, _, fn, _ in EMOJI_WINDOWS:
        if fn not in used_emojis:
            used_emojis.append(fn)

    pos_map = {
        "right_top": ("W-w-60", "260"),
        "left_top": ("60", "260"),
    }

    inputs = ["-i", str(concat)]
    input_idx = 1
    fc_parts = []
    emoji_input_map = {}
    for fn in used_emojis:
        epath = EMOJI_DIR / fn
        if not epath.exists():
            print(f"  WARNING: emoji asset missing: {epath}")
            continue
        inputs += ["-i", str(epath)]
        fc_parts.append(f"[{input_idx}:v]scale=280:280[em_{fn.replace('.', '_')}]")
        emoji_input_map[fn] = input_idx
        input_idx += 1

    prev_tag = "0:v"
    chain_count = 0
    for st, et, fn, pos in EMOJI_WINDOWS:
        if fn not in emoji_input_map:
            continue
        em_tag = f"em_{fn.replace('.', '_')}"
        x_expr, y_expr = pos_map[pos]
        chain_count += 1
        new_tag = f"ev{chain_count}"
        fc_parts.append(
            f"[{prev_tag}][{em_tag}]overlay=x='{x_expr}':y='{y_expr}'"
            f":enable='between(t,{st:.2f},{et:.2f})'[{new_tag}]"
        )
        prev_tag = new_tag

    # Title framing (t=0-3s, commentary-track requirement, ADR-0007 gate item 1) + CTA
    # (last ~4s) + Implied-Comparison cards (ADR-0007 item 2 value-add).
    text_parts = [
        drawtext(TITLE_TEXT, y=90, size=34, color="yellow", font=FONT_BOLD,
                 enable="between(t,0,3)"),
        drawtext("NHIỀU NGƯỜI NGHĨ: CHỈ LÀ XƯƠNG", y=150, size=30, color="white",
                 font=FONT_BOLD, enable=f"between(t,{CARD1_START:.2f},{CARD1_END:.2f})"),
        drawtext("SỰ THẬT: MIỄN DỊCH - NÃO BỘ - CẢ CƠ THỂ", y=150, size=27, color="0x7CFC00",
                 font=FONT_BOLD, enable=f"between(t,{CARD2_START:.2f},{CARD2_END:.2f})"),
        drawtext(CTA_TEXT, y="h-70", size=22, color="white",
                 enable=f"between(t,{max(concat_dur-4,0):.2f},{concat_dur:.2f})"),
    ]
    chain_count += 1
    final_tag = "final"
    fc_parts.append(f"[{prev_tag}]{','.join(text_parts)}[{final_tag}]")

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

    # Retention Technique (base quality, not AB variable): uniform 1.1x speed-up applied
    # last, after all cuts/overlays are burned in (aiwork v2 pattern). Pause-trimming
    # skipped -- word-gap analysis of this span found ~0 natural pauses (see docstring).
    print(f"  Applying {SPEED}x speed-up...")
    sped_v = d / "sped_v.mp4"
    cmd = ["ffmpeg", "-y", "-i", str(fv),
           "-vf", f"setpts=PTS/{SPEED}",
           "-c:v", "libx264", "-crf", "18", "-preset", "fast",
           "-an", str(sped_v)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(f"  SPEED-UP (video) ERROR: {r.stderr[-500:]}")
        return False

    sped_a = d / "sped_a.m4a"
    cmd = ["ffmpeg", "-y", "-i", str(concat),
           "-vn", "-af", f"atempo={SPEED}",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
           str(sped_a)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        print(f"  SPEED-UP (audio) ERROR: {r.stderr[-500:]}")
        return False

    out = O / f"{VID}.mp4"
    cmd = ["ffmpeg", "-y", "-i", str(sped_v), "-i", str(sped_a),
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
    print("="*60 + "\n  BAC SI HAI -- v6 (Multi-Clip Mashup, Vitamin D = hormone)\n" + "="*60)
    ok = render()
    print(f"\n{'='*60}\n  {'OK' if ok else 'FAIL'}\n{'='*60}")
    shutil.rmtree(T, ignore_errors=True)


if __name__ == "__main__":
    main()
