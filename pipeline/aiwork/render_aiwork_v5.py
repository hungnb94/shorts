#!/usr/bin/env python3
"""Working With AI — Prompt Bloat v5: hardknocks-style captions (bigger, keyword-highlighted).

Rebuild of render_aiwork_v4.py (content/cut unchanged — same 7 pieces, same value-adds).
User feedback on v4: the captions are too small, and the hook question gets revealed
progressively across 4 sequential bursts (t=0-9.12s) instead of appearing all at once.
Ported the caption technique already proven in render_hardknocks_v3.py (ADR-0018
addendum: base text + selected keywords rendered bigger and in a highlight color, centered
via Pillow font metrics so mixed sizes/colors on one line stay pixel-aligned):

1. HOOK: same four phrase-groups as v4 ("WHY DOES ADDING MORE" / "INSTRUCTIONS" / "MAKE
   YOUR AI" / "WORSE?"), but stacked as 4 lines shown SIMULTANEOUSLY for the whole
   0-9.12s hook window instead of revealed one at a time — the full question is visible
   from frame 0. "WORSE?" keeps v4's keyword emphasis (bigger + yellow).
2. BODY_SUBS: same segmentation/timing as v4, ~1.4-1.8x bigger base font (40 vs v4's 28),
   with one key word/phrase per line marked via `*word*` markup and rendered bigger +
   yellow — same run-splitting technique as hardknocks' dialogue_burst_filters, adapted
   to markup instead of a fixed vocabulary set (these are short self-authored fragments,
   not natural dialogue, so per-line explicit markup is a better fit than a global word
   list). A solid background band replaces the old per-line box (per-run boxes would
   leave a seam between differently-colored/sized runs — same issue hardknocks' own
   docstring already found and fixed with a band instead of per-burst boxes).

Everything else (pieces, crop, value-adds, speed-up, duration) is unchanged from v4.
"""
import subprocess, shutil, re
from pathlib import Path
from PIL import ImageFont

SRC = Path("output/projects/aiwork/source/mWvtOHlZM-I_1080p.webm")
CHART_PNG = Path("output/projects/aiwork/final/assets/prompt_bloat_chart_v3.png")
O = Path("output/projects/aiwork/final")
T = Path("output/projects/aiwork/clips/temp_v5")
FONT = "/System/Library/Fonts/Helvetica.ttc"
FONT_BOLD = "/System/Library/Fonts/HelveticaNeue.ttc"

O.mkdir(parents=True, exist_ok=True)
T.mkdir(parents=True, exist_ok=True)

VID = "2026-07-12-aiwork_v5_prompt_bloat"
SPEED = 1.1

CROP_X = 2073  # verified via frame extraction: centers the podium/presenter after scale=-2:1920

# (id, src_start, src_end) — all pieces use the identical fixed wide-shot crop
PIECES = [
    ("hook",       45.48,   54.60),
    ("escalate",   55.56,   67.50),
    ("compl_a",    74.12,   82.16),
    ("compl_b",    82.58,   97.54),
    ("reinforce",  98.04,  104.78),
    ("fix",       105.04,  113.68),
    ("close",    2693.32, 2698.30),
]

durs = [e - s for _, s, e in PIECES]
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


# --- Body-caption keyword emphasis (ADR-0018 addendum, ported from
# render_hardknocks_v3.py's dialogue_burst_filters) --------------------------------
# Base text at BASE_SIZE/white; `*word*` markup runs render at KW_SIZE/yellow. Widths
# are measured with Pillow (same font file/index ffmpeg's drawtext loads) so multi-
# color/multi-size runs on one line stay centered on a shared baseline.
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
    """Split `*word*`-marked text into (is_keyword, words) runs of consecutive same-class tokens."""
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
    """Render one caption line as N drawtext filters (one per keyword run), Pillow-
    positioned so mixed base/keyword sizes share a centered baseline. No per-run box —
    a single band (BODY_BAND) is drawn behind the whole caption zone instead."""
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
    pid, start, end = PIECES[idx]
    d = end - start
    vf = f"scale=-2:1920,crop=1080:1920:{CROP_X}:0"
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


# Hook: the full question, shown as 4 stacked lines ALL VISIBLE FROM t=0 through the
# whole 9.12s hook window (no progressive reveal) — reframed as a question, not the
# source's own "imagine you built an agent" line (which names "agent" — developer-coded
# per the audience-fit decision). "WORSE?" is the keyword line (bigger + yellow).
HOOK_LINES = [
    ("WHY DOES ADDING MORE", 44, "white", 110),
    ("INSTRUCTIONS",         44, "white", 185),
    ("MAKE YOUR AI",         44, "white", 260),
    ("WORSE?",               62, "yellow", 340),
]
HOOK_DUR = durs[0]  # 9.12s — the hook piece's own duration

# Body captions: self-authored reframe of the source's own words (per audience-fit
# decision), not verbatim transcript — strips "agent"/"system prompt" jargon. FIX's
# captions have no relation at all to the underlying spoken audio (same pattern as HOOK).
# `*word*` marks the keyword run rendered bigger + yellow (see keyword_burst_filters).
BODY_SUBS = [
    (G["escalate"] + 0.00, G["escalate"] + 3.00, "IT WORKED *PERFECTLY* AT FIRST."),
    (G["escalate"] + 3.00, G["escalate"] + 6.00, "SO YOU KEPT ADDING *MORE* TO IT."),
    (G["escalate"] + 6.00, G["escalate"] + 8.50, "AND *MORE*."),
    (G["escalate"] + 8.50, G["escalate"] + 11.94, "AND *MORE*."),

    (G["compl_a"] + 0.00, G["compl_a"] + 3.50, "UNTIL YOUR *INSTRUCTIONS*"),
    (G["compl_a"] + 3.50, G["compl_a"] + 8.04, "BECAME *HUNDREDS* OF LINES LONG."),

    (G["compl_b"] + 0.00, G["compl_b"] + 3.00, "*MORE* PIECES. *MORE* COMPLEXITY."),
    (G["compl_b"] + 3.00, G["compl_b"] + 7.50, "AND *SUDDENLY* IT STARTED"),
    (G["compl_b"] + 7.50, G["compl_b"] + 10.50, "MAKING *MISTAKES* IT NEVER MADE BEFORE."),
    (G["compl_b"] + 10.50, G["compl_b"] + 14.96, "SOUND *FAMILIAR*?"),

    (G["reinforce"] + 0.00, G["reinforce"] + 3.50, "IT HAPPENS TO *EVERYONE* -"),
    (G["reinforce"] + 3.50, G["reinforce"] + 6.74, "EVEN THE PEOPLE WHO *BUILD* THIS STUFF."),

    (G["fix"] + 0.00, G["fix"] + 1.80, "THE *FIX*:"),
    (G["fix"] + 1.80, G["fix"] + 5.00, "*SMALL FOCUSED* STEPS -"),
    (G["fix"] + 5.00, G["fix"] + 8.64, "NOT ONE *GIANT* PROMPT."),

    (G["close"] + 0.00, G["close"] + 4.98, "*FOLLOW* FOR MORE ON USING AI WELL"),
]

# Solid bands behind the hook (top) and body (bottom) caption zones — replaces the old
# per-line box=1 so multi-run/multi-color lines don't show a seam between runs (same
# fix render_hardknocks_v3.py already made for its own dialogue captions).
HOOK_BAND = (f"drawbox=x=0:y=60:w=iw:h=360:color=black@0.45"
             f":enable='between(t,0,{HOOK_DUR:.2f})':t=fill")
BODY_BAND = "drawbox=x=0:y=1650:w=iw:h=270:color=black@0.55:t=fill"

# this_or_that_overlay: generalized 2-way version of the source's tool/skill/subagent
# framework (dropped the literal 3-way jargon split per audience-fit decision) — shown
# during compl_b's "SOUND FAMILIAR?" beat. FIX's "NOT ONE GIANT PROMPT" pays this off.
THIS_OR_THAT_A = "ONE GIANT PROMPT"
THIS_OR_THAT_B = "SMALL FOCUSED STEPS"
TOT_START = G["compl_b"] + 10.30
TOT_END = G["compl_b"] + 14.96

# data_viz_overlay: our own chart (pipeline/aiwork/make_chart_v3.py), built from the
# real 400-line / 15-line numbers named in the source (at slide-only timestamps we do
# NOT use as footage) — shown during "reinforce" as the concrete proof point, paid off
# by FIX immediately after.
CHART_START = G["reinforce"] + 0.20
CHART_END = G["reinforce"] + 6.74


def render():
    print(f"\n{'='*55}\n  {VID}\n{'='*55}")

    print("  Extracting 7 pieces (fixed wide-shot crop)...")
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

    print("  Compositing overlays + 1.1x speed-up...")
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
        drawtext(THIS_OR_THAT_A, y=560, size=30, color="0xFCA5A5", font=FONT_BOLD,
                  enable=f"between(t,{TOT_START:.2f},{TOT_END:.2f})"),
        drawtext("VS", y=630, size=24, color="white",
                  enable=f"between(t,{TOT_START:.2f},{TOT_END:.2f})", box=False),
        drawtext(THIS_OR_THAT_B, y=690, size=30, color="0x86EFAC", font=FONT_BOLD,
                  enable=f"between(t,{TOT_START:.2f},{TOT_END:.2f})"),
    ]

    pbar = f"drawbox=x=0:y=ih-4:w=iw*(t/{TOTAL:.3f}):h=4:color=0x4F46E5:t=fill"

    fc_parts = ["[1:v]scale=820:-2[chart]"]
    fc_parts.append(
        f"[0:v][chart]overlay=x=(W-w)/2:y=900"
        f":enable='between(t,{CHART_START:.2f},{CHART_END:.2f})'[withchart]"
    )
    all_text_parts = [HOOK_BAND, BODY_BAND] + burst_parts + sub_parts + tot_parts + [pbar]
    fc_parts.append(f"[withchart]{','.join(all_text_parts)},setpts=PTS/{SPEED}[vout]")
    fc = ";".join(fc_parts)

    out = O / f"{VID}.mp4"
    cmd = ["ffmpeg", "-y", "-i", str(concat_out), "-i", str(CHART_PNG),
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
    print("="*60 + "\n  WORKING WITH AI — PROMPT BLOAT v5 (Multi-Clip Mashup)\n" + "="*60)
    ok = render()
    print(f"\n{'='*60}\n  {'OK' if ok else 'FAIL'}\n{'='*60}")
    shutil.rmtree(T, ignore_errors=True)


if __name__ == "__main__":
    main()
