#!/usr/bin/env python3
"""Working With AI — AI Misalignment v6: Multi-Clip Mashup, Matt Pocock "/wayfinder" livestream.

Source (251hsWgoTPM, "LIVE: The /wayfinder Demo", Matt Pocock, 4480s livestream) is almost
entirely screen-share (VS Code + terminal + GitHub, small corner-PiP webcam) — a live
pair-programming session building a spec-first planning tool ("Wayfinder") on top of Claude
Code. Per ADR-0020's audience-fit constraint (professionals/knowledge workers, not developers
specifically), the actual dev-tool content (TikTok upload APIs, GitHub issue trees, TypeScript
schemas) is unusable verbatim — but one spoken insight, found by keyword-scanning the full
transcript rather than watching all 74 minutes, generalizes cleanly beyond code:

    "So much of like misalignment from AI is AI not asking these questions, not
    understanding what your values are, what you prioritize over other stuff."
                                                                — 53:41 into the stream

This is the video's spine. Structure: HOOK (self-authored question, cold open on the
stream's own full-frame intro before screen-share starts) -> TEACH (the insight above, real
audio+captions, no self-authoring needed since the quote is already jargon-free) -> PROOF_Q
(real footage: the AI asks a genuine clarifying question) -> PROOF_A (real footage: Matt's
thoughtful answer, showing a real preference an AI would have had to guess at) -> FIX_FOG (a
vivid real metaphor - "notice how much fog there is... this is what [a good process] is
doing... helping us find the way" - captioned to generalize away the "Wayfinder" product name)
-> CTA (self-authored, established niche branding line, real sign-off audio underneath).

Two distinct camera compositions require two different fixed crops (frame-verified, not
guessed - see docs/production/aiwork-v6-ai-misalignment.md):
- HOOK piece (1.00-9.04s): pure full-frame webcam, no screen-share yet. CROP_HOOK_X=1255
  centers his face after scale=-2:1920.
- All other pieces: VS Code/GitHub screen-share with a small corner-PiP webcam (fixed OBS
  layout, confirmed static across 3 widely-separated timestamps: 645s/3210s/4258s).
  CROP_SCREEN_X=2333 is flush against the scaled canvas's right edge, keeping the PiP face
  in-frame while showing a sliver of the real screen content on the left for authenticity.

Value-adds (Transformative Gate, ADR-0007): this_or_that_overlay ("AI THAT GUESSES" vs "AI
THAT ASKS FIRST") + data_viz_overlay (a stat-card-style text card, "THE FIX: ASK BEFORE YOU
BUILD" - no numeric chart exists for this source, matching the hardknocks convention that a
data_viz_overlay can be a styled text card, not necessarily a plotted chart).

Captions use the hardknocks/aiwork_v5 big-font + highlighted-keyword technique
(keyword_burst_filters, ported unchanged from render_aiwork_v5.py / render_hardknocks_v3.py's
dialogue_burst_filters) - base text + `*word*`-marked keyword runs, Pillow-positioned so
mixed sizes/colors share a centered baseline.
"""
import subprocess, shutil, re
from pathlib import Path
from PIL import ImageFont

SRC = Path("output/projects/aiwork/source/251hsWgoTPM_1080p.webm")
O = Path("output/projects/aiwork/final")
T = Path("output/projects/aiwork/clips/temp_v6")
FONT = "/System/Library/Fonts/Helvetica.ttc"
FONT_BOLD = "/System/Library/Fonts/HelveticaNeue.ttc"

O.mkdir(parents=True, exist_ok=True)
T.mkdir(parents=True, exist_ok=True)

VID = "2026-07-14-aiwork_v6_ai_misalignment"
SPEED = 1.02  # mild - source content is already tight/substantive, no filler to cut for pace

# Two fixed crops (frame-verified against 251hsWgoTPM_1080p.webm, see docstring)
CROP_HOOK = "scale=-2:1920,crop=1080:1920:1255:0"
CROP_SCREEN = "scale=-2:1920,crop=1080:1920:2333:0"

# (id, src_start, src_end, crop_vf) - all word-boundary-aligned via mlx_whisper transcript
PIECES = [
    ("hook",     1.00,    9.04,    CROP_HOOK),
    ("teach",    3221.85, 3231.15, CROP_SCREEN),
    ("proof_q",  3177.80, 3181.50, CROP_SCREEN),
    ("proof_a",  3209.20, 3220.20, CROP_SCREEN),
    ("fix_fog",  643.98,  653.52,  CROP_SCREEN),
    ("cta",      4255.80, 4262.90, CROP_SCREEN),
]

durs = [e - s for _, s, e, _ in PIECES]
g = [sum(durs[:i]) for i in range(len(PIECES))]
TOTAL = sum(durs)
G = {pid: g[i] for i, (pid, *_rest) in enumerate(PIECES)}


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
              f"x={x}", f"y={y}", "expansion=none"]
    if box:
        parts += ["box=1", "boxcolor=black@0.55", "boxborderw=10"]
    if enable:
        parts.append(f"enable='{enable}'")
    return ":".join(parts)


# --- Body-caption keyword emphasis (ADR-0018 addendum, ported from render_aiwork_v5.py /
# render_hardknocks_v3.py's dialogue_burst_filters). ---------------------------------------
BASE_SIZE = 40
KW_SIZE = 50
BASE_COLOR = "white"
KW_COLOR = "yellow"

_font_base = ImageFont.truetype(FONT_BOLD, BASE_SIZE, index=0)
_font_kw = ImageFont.truetype(FONT_BOLD, KW_SIZE, index=0)
_space_w = _font_base.getlength(" ")
_ascent_base, _ = _font_base.getmetrics()
_ascent_kw, _ = _font_kw.getmetrics()


def _parse_runs(text):
    tokens = re.findall(r"\*[^*]+\*|\S+", text)
    runs = []
    cur_kw, cur_words = None, []
    for tok in tokens:
        is_kw = tok.startswith("*") and tok.endswith("*")
        word = tok[1:-1] if is_kw else tok
        if is_kw != cur_kw:
            if cur_words:
                runs.append((cur_kw, cur_words))
            cur_kw, cur_words = is_kw, [word]
        else:
            cur_words.append(word)
    if cur_words:
        runs.append((cur_kw, cur_words))
    return runs


def keyword_burst_filters(text, y_top, enable):
    runs = _parse_runs(text)
    specs = []
    for is_kw, words in runs:
        if is_kw:
            specs.append((words, _font_kw, KW_COLOR, _ascent_kw))
        else:
            specs.append((words, _font_base, BASE_COLOR, _ascent_base))

    widths = [font.getlength(" ".join(words)) for words, font, _, _ in specs]
    total_w = sum(widths) + _space_w * (len(specs) - 1)
    baseline_y = y_top + _ascent_base

    filters = []
    cur_x = (1080 - total_w) / 2
    for (words, font, color, ascent), w in zip(specs, widths):
        size = KW_SIZE if font is _font_kw else BASE_SIZE
        seg_y = round(baseline_y - ascent)
        filters.append(drawtext(" ".join(words), y=seg_y, size=size, color=color,
                                 x=f"{round(cur_x)}", enable=enable, box=False))
        cur_x += w + _space_w
    return filters


def extract_piece(idx):
    pid, start, end, vf = PIECES[idx]
    d = end - start
    out = T / f"{pid}_raw.mp4"
    cmd = [
        "ffmpeg", "-y", "-ss", str(start), "-i", str(SRC), "-t", str(d),
        "-vf", vf,
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        str(out)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        print(f"  EXTRACT ERROR ({pid}): {r.stderr[-500:]}")
        return None
    print(f"  {pid}: {dur(out):.2f}s")
    return out


# HOOK: self-authored question (his real words here just say "I'm going to chat about
# Wayfinder for an hour" - not usable as the hook payoff, so the caption is fully
# self-authored per the established audience-fit pattern). All 3 lines visible from t=0
# (feedback_caption_style_standard - no progressive reveal).
HOOK_LINES = [
    ("WHY DOES YOUR AI", 44, "white", 130),
    ("KEEP GETTING", 44, "white", 210),
    ("IT WRONG?", 64, "yellow", 290),
]
HOOK_DUR = durs[0]

# Body captions. TEACH is the real quote verbatim (already jargon-free - no self-authoring
# needed). PROOF_Q/PROOF_A paraphrase away "remotion caption look" jargon while keeping the
# real beat (an AI asking a real question; a real preference it would've had to guess at).
# FIX_FOG generalizes away the "Wayfinder" product name per the audience-fit decision.
BODY_SUBS = [
    (G["teach"] + 0.00, G["teach"] + 3.75, "MISALIGNMENT FROM AI IS"),
    (G["teach"] + 3.75, G["teach"] + 5.49, "AI *NOT ASKING* THESE QUESTIONS"),
    (G["teach"] + 5.49, G["teach"] + 7.51, "NOT UNDERSTANDING YOUR *VALUES*"),
    (G["teach"] + 7.51, G["teach"] + 9.30, "WHAT YOU *PRIORITIZE*"),

    (G["proof_q"] + 0.00, G["proof_q"] + 3.70, "THE AI: \"HOW ATTACHED ARE YOU TO *THIS*?\""),

    (G["proof_a"] + 0.00, G["proof_a"] + 3.28, "\"I'M *ACTUALLY* VERY ATTACHED TO IT.\""),
    (G["proof_a"] + 3.28, G["proof_a"] + 6.76, "\"IT TOOK A LONG TIME TO GET IT *RIGHT*.\""),
    (G["proof_a"] + 6.76, G["proof_a"] + 11.00, "\"I DON'T WANT TO *LOSE* IT.\""),

    (G["fix_fog"] + 0.00, G["fix_fog"] + 2.84, "NOTICE THE *FOG*?"),
    (G["fix_fog"] + 2.84, G["fix_fog"] + 6.20, "THAT'S WHAT *GUESSING* FEELS LIKE"),
    (G["fix_fog"] + 6.20, G["fix_fog"] + 9.54, "A GOOD PROCESS *FINDS THE WAY*"),

    (G["cta"] + 0.00, G["cta"] + 7.10, "*FOLLOW* FOR MORE ON USING AI WELL"),
]

# Solid bands behind the hook (top) and body (bottom) caption zones (same fix
# render_hardknocks_v3.py / render_aiwork_v5.py already made for multi-run/multi-color lines).
HOOK_BAND = (f"drawbox=x=0:y=70:w=iw:h=310:color=black@0.45"
             f":enable='between(t,0,{HOOK_DUR:.2f})':t=fill")
BODY_BAND = "drawbox=x=0:y=1650:w=iw:h=270:color=black@0.55:t=fill"

# this_or_that_overlay: the core contrast, shown during FIX_FOG (pairs with "guessing" /
# "finds the way" captions playing at the same time).
THIS_OR_THAT_A = "AI THAT GUESSES"
THIS_OR_THAT_B = "AI THAT ASKS FIRST"
TOT_START = G["fix_fog"] + 0.20
TOT_END = G["fix_fog"] + durs[4]

# data_viz_overlay: a stat-card-style text card (no numeric chart exists for this source -
# same "card, not necessarily a plotted chart" convention hardknocks established), shown
# during the PROOF_Q/PROOF_A demonstration.
FIX_CARD = "THE FIX: ASK BEFORE YOU BUILD"
FIX_CARD_START = G["proof_q"]
FIX_CARD_END = G["proof_a"] + durs[3]


def render():
    print(f"\n{'='*55}\n  {VID}\n{'='*55}")

    print("  Extracting 6 pieces (2 crop treatments)...")
    pieces = []
    for i in range(len(PIECES)):
        p = extract_piece(i)
        if p is None:
            print("  ABORT: a piece failed to extract")
            return False
        pieces.append(p)

    concat_list = T / "concat_list.txt"
    concat_list.write_text("\n".join(f"file '{p.resolve()}'" for p in pieces))

    print("  Concatenating (hard cuts, ffmpeg concat demuxer)...")
    concat_out = T / "concat.mp4"
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
           "-c", "copy", str(concat_out)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print(f"  CONCAT ERROR: {r.stderr[-500:]}")
        return False
    concat_dur = dur(concat_out)
    print(f"  Concat: {concat_dur:.2f}s (expected {TOTAL:.2f}s)")

    print("  Compositing overlays + speed-up...")
    hook_enable = f"between(t,0,{HOOK_DUR:.2f})"
    burst_parts = [
        drawtext(txt, y=y, size=size, color=color, enable=hook_enable, box=False)
        for txt, size, color, y in HOOK_LINES
    ]

    sub_parts = []
    for st, et, txt in BODY_SUBS:
        enable = f"between(t,{st:.2f},{et:.2f})"
        sub_parts.extend(keyword_burst_filters(txt, y_top=1720, enable=enable))

    tot_parts = [
        drawtext(THIS_OR_THAT_A, y=560, size=32, color="0xFCA5A5", font=FONT_BOLD,
                  enable=f"between(t,{TOT_START:.2f},{TOT_END:.2f})"),
        drawtext("VS", y=634, size=24, color="white",
                  enable=f"between(t,{TOT_START:.2f},{TOT_END:.2f})", box=False),
        drawtext(THIS_OR_THAT_B, y=694, size=32, color="0x86EFAC", font=FONT_BOLD,
                  enable=f"between(t,{TOT_START:.2f},{TOT_END:.2f})"),
    ]

    fix_card_parts = [
        drawtext(FIX_CARD, y=220, size=34, color="0xFDE68A", font=FONT_BOLD,
                  enable=f"between(t,{FIX_CARD_START:.2f},{FIX_CARD_END:.2f})"),
    ]

    pbar = f"drawbox=x=0:y=ih-4:w=iw*(t/{TOTAL:.3f}):h=4:color=0x4F46E5:t=fill"

    all_text_parts = ([HOOK_BAND, BODY_BAND] + burst_parts + sub_parts + tot_parts
                       + fix_card_parts + [pbar])
    fc = f"[0:v]{','.join(all_text_parts)},setpts=PTS/{SPEED}[vout]"

    out = O / f"{VID}.mp4"
    cmd = ["ffmpeg", "-y", "-i", str(concat_out),
           "-filter_complex", fc,
           "-map", "[vout]", "-map", "0:a",
           "-af", f"atempo={SPEED}",
           "-c:v", "libx264", "-crf", "20", "-preset", "fast",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
           "-shortest", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        err_lines = [l for l in r.stderr.split("\n")
                     if any(x in l.lower() for x in ["error", "invalid", "no such"])]
        err = err_lines[0] if err_lines else r.stderr[-500:]
        print(f"  FILTER ERROR: {err[:500]}")
        return False

    od = dur(out)
    mb = out.stat().st_size / 1_048_576
    print(f"  => {out.name}: {od:.1f}s, {mb:.1f}MB")

    a_check = subprocess.run(
        ["ffprobe", "-v", "quiet", "-select_streams", "a",
         "-show_entries", "stream=index,codec_type", "-of", "csv=p=0", str(out)],
        capture_output=True, text=True)
    a_lines = [l for l in a_check.stdout.strip().split("\n") if l]
    if len(a_lines) != 1:
        print(f"  WARNING: expected exactly 1 audio stream, found {len(a_lines)}: {a_lines}")
        return False
    print(f"  Audio: OK (1 stream)")
    return True


def main():
    print("="*60 + "\n  WORKING WITH AI — AI MISALIGNMENT v6 (Multi-Clip Mashup)\n" + "="*60)
    ok = render()
    print(f"\n{'='*60}\n  {'OK' if ok else 'FAIL'}\n{'='*60}")
    shutil.rmtree(T, ignore_errors=True)


if __name__ == "__main__":
    main()
