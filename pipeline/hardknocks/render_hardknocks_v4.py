#!/usr/bin/env python3
"""hardknocks_v4 — Peter Tuchman single-person reveal, from AATw4YRFSw8 (School of Hard
Knocks, "Asking Wall Street Moguls How They Got Rich!").

4th School of Hard Knocks source (see data/source_videos.csv). Same-person-callback
Implied Comparison device as v3 (CONTEXT.md), but the PIVOT payoff here is a real personal
tragedy, not a belief. Structure (Multi-Clip Mashup, ADR-0022 — pieces scattered ~845-1198s
of a 1242.9s source, no single 45-60s window contains them all):
- HOOK: Peter Tuchman's own quick, confident answers establish stature and a Money+Number
  claim ("most famous stockbroker in the world", trades $0.5-1B of stock/day).
- PIVOT: the SAME man, asked "have you ever been broke", reveals years of real hardship —
  broke 2006-08, then (much more recently) his wife's death and his own near-fatal COVID.
- RESOLUTION/TEACH: what kept him going ("I love what I do"), a humbling aside (doesn't
  need to flex wealth), and his closing wisdom ("money buys freedom, not happiness").

Tone (explicit user decision via /grill-with-docs grilling session, scoped to this video):
RESILIENCE-FIRST. The tragedy is real and stays in his own verbatim audio/captions (cutting
it would be dishonest to his story), but nothing in the TOP structure caption, the
comparison card, or the keyword-emphasis coloring names the specific tragedy ("wife died",
"COVID", "three months to live") as the attention-grabbing hook. Those specific words are
deliberately left in the PLAIN base caption color (no keyword emphasis) rather than
highlighted — only the resilience/wisdom payoff words (love, freedom, kept going, share,
found, understand) get the keyword color+size bump. This is the concrete implementation of
"resilience-first": the story stays fully honest, but the visual emphasis is on the lesson,
not the loss.

Crop: hard center-crop (ADR-0024), matching v1-v3. Self-authored, word-synced captions
(mlx_whisper transcript), auto-split into bursts (see auto_bursts()) rather than hand-typed
per burst — this source has 8 pieces / ~180 words, more than v3's hand-typed approach
comfortably covers without transcription error.

Value-adds (Transformative Gate, ADR-0007, 2 distinct categories):
1. data_viz_overlay — stat cards during the HOOK ("40 YEARS ON WALL STREET",
   "$0.5-1B TRADED / DAY").
2. this_or_that_overlay — "THE MONEY vs THE STRUGGLE" comparison card at the pivot,
   deliberately abstract per the resilience-first tone decision (names the CONTRAST, not
   the specific tragedy).

Retention Technique (base quality, AGENTS.md): pieces hand-selected at exact word
boundaries from the mlx_whisper transcript (output/projects/hardknocks/source/
AATw4YRFSw8_transcript.json) — checked programmatically alongside auto_bursts(). Raw cut
lands at ~49.9s, already at the ~50s target (user's stated duration preference), so only a
mild uniform speed-up is applied per the base-quality rule.
"""
import json
import subprocess
import shutil
import re
from pathlib import Path
from PIL import ImageFont

SRC = Path("output/projects/hardknocks/source/AATw4YRFSw8.mp4")
TRANSCRIPT = Path("output/projects/hardknocks/source/AATw4YRFSw8_transcript.json")
O = Path("output/projects/hardknocks/final")
T = Path("output/projects/hardknocks/clips/temp_v4")
FONT = "/System/Library/Fonts/Helvetica.ttc"
FONT_BOLD = "/System/Library/Fonts/HelveticaNeue.ttc"

O.mkdir(parents=True, exist_ok=True)
T.mkdir(parents=True, exist_ok=True)

VID = "2026-07-13-hardknocks_v4_wall_street_legend"  # date-prefixed per AGENTS.md convention
SPEED = 1.03  # mild — raw cut already ~49.9s, right at the ~50s target

# Hard center-crop (ADR-0024) — matches render_hardknocks_v1/v2/v3.py.
CROP = "scale=-2:1920,crop=1080:1920:(in_w-1080)/2:0"

# (id, src_start, src_end) — absolute seconds in the downloaded source, exact word
# boundaries from AATw4YRFSw8_transcript.json (word_timestamps=True).
PIECES = [
    ("hook1_identity",   845.62, 849.24),   # "...longest standing broker...most famous stockbroker in the world."
    ("hook2_money",      854.98, 862.26),   # "Of course...half a billion and a billion dollars of stock every day...Every day."
    ("pivot1_ask",       939.92, 943.18),   # "Have you ever been broke before? Yes, I've been virtually penniless."
    ("pivot2_rockbottom",948.72, 957.44),   # "...2006, 7 and 8, when I hit rock bottom...cowered under the covers."
    ("reveal_tragedy",  1040.66, 1049.94),  # "...broke for three years...wife died of cancer...almost died of COVID...three months to live."
    ("resolution_love", 1050.04, 1054.48),  # "...kept you going?...That I love what I do."
    ("humble_bridge",   1054.54, 1062.38),  # "...don't need to post pictures...on the back of a Bugatti...share what I found..."
    ("teach_freedom",   1192.46, 1197.92),  # "...money does not buy you happiness. Money buys you freedom..."
]

durs = [e - s for _, s, e in PIECES]
g = [sum(durs[:i]) for i in range(len(PIECES))]
TOTAL = sum(durs)
G = {pid: g[i] for i, (pid, *_r) in enumerate(PIECES)}
print("Piece durations:", [round(d, 2) for d in durs], "TOTAL:", round(TOTAL, 2))


def dur(p):
    if not p.exists():
        return 0.0
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                         "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
                        capture_output=True, text=True, timeout=15)
    return float(r.stdout.strip()) if r.stdout.strip() else 0.0


def esc(s):
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’")


def drawtext(text, y, size=30, color="white", enable=None, box=True,
             x="(w-text_w)/2", font=FONT_BOLD, boxcolor="black@0.55", boxborderw=14):
    t = esc(text)
    parts = [f"drawtext=text='{t}'", f"fontfile={font}", f"fontsize={size}",
              f"fontcolor={color}", "borderw=4", "bordercolor=black@0.9",
              f"x={x}", f"y={y}", "expansion=none"]
    if box:
        parts += ["box=1", f"boxcolor={boxcolor}", f"boxborderw={boxborderw}"]
    if enable:
        parts.append(f"enable='{enable}'")
    return ":".join(parts)


# --- Word-synced dialogue captions, auto-split into bursts ---------------------
# Unlike v3 (hand-typed bursts), this source has 8 pieces / ~180 spoken words — auto-split
# from the mlx_whisper word timestamps avoids manual transcription error at that volume.
# A burst breaks on: reaching MAX_WORDS, a gap > GAP_BREAK to the next word, or reaching
# MAX_DUR — same intent as v3's hand-picked ~2-4 word / ~0.3-1.6s bursts.
MAX_WORDS = 4
MAX_DUR = 1.6
GAP_BREAK = 0.25

_transcript = json.loads(TRANSCRIPT.read_text())
_all_words = [w for seg in _transcript["segments"] for w in seg.get("words", [])]


def words_in(a, b):
    return [w for w in _all_words if a <= w["start"] < b]


def auto_bursts(start, end):
    ws = words_in(start, end)
    bursts = []
    cur = []
    for w in ws:
        if cur:
            gap = w["start"] - cur[-1]["end"]
            cur_dur = cur[-1]["end"] - cur[0]["start"]
            if gap > GAP_BREAK or len(cur) >= MAX_WORDS or cur_dur >= MAX_DUR:
                bursts.append(cur)
                cur = []
        cur.append(w)
    if cur:
        bursts.append(cur)
    out = []
    for b in bursts:
        rel_st = b[0]["start"] - start
        rel_et = b[-1]["end"] - start
        # mlx_whisper word tokens already carry their own leading space (or lack of one,
        # e.g. ",000." attaches directly to the prior token) - re-joining with " " would
        # break punctuation-attached tokens, so concatenate raw and strip once at the ends.
        text = "".join(w["word"] for w in b).strip()
        out.append((max(0.0, rel_st), rel_et, text))
    return out


DIALOGUE_BURSTS = {pid: auto_bursts(s, e) for pid, s, e in PIECES}
for pid, bursts in DIALOGUE_BURSTS.items():
    print(f"  {pid}: {len(bursts)} bursts -> {[t for _, _, t in bursts]}")


# --- Dialogue-caption keyword emphasis (ADR-0018 addendum), RESILIENCE-FIRST tone ------
# Base body text: yellow @ DIALOGUE_BASE_SIZE (matches v3's base size/color).
# GROUP_A (white) = money/credibility vocabulary — establishes stature.
# GROUP_B (red-orange) = resilience/wisdom PAYOFF vocabulary — the takeaway this video
#   is actually about, per the user's explicit resilience-first tone decision.
# Deliberately NOT emphasized (left in plain base yellow, no color/size bump): the
# specific tragedy words (died, cancer, covid, broke, penniless, cowered, rock, bottom,
# brother, parents) — his own voice carries them honestly, but nothing visually amplifies
# them as the hook. This is the concrete implementation of "resilience-first, not
# tragedy-as-clickbait" (see module docstring and docs/production/hardknocks-v4-*.md).
DIALOGUE_BASE_SIZE = 68
DIALOGUE_KW_SIZE = 75
DIALOGUE_BASE_COLOR = "yellow"
GROUP_A_COLOR = "white"
GROUP_B_COLOR = "0xFF3B1A"
GROUP_A_WORDS = {"billion", "dollars", "stock", "40", "famous", "stockbroker", "broker"}
GROUP_B_WORDS = {"love", "freedom", "kept", "going", "share", "found", "understand"}

_font_base = ImageFont.truetype(FONT_BOLD, DIALOGUE_BASE_SIZE, index=0)
_font_kw = ImageFont.truetype(FONT_BOLD, DIALOGUE_KW_SIZE, index=0)
_space_w = _font_base.getlength(" ")
_ascent_base, _descent_base = _font_base.getmetrics()
_ascent_kw, _descent_kw = _font_kw.getmetrics()


def _classify_word(word):
    stripped = re.sub(r"[^\w']", "", word).lower()
    if stripped in GROUP_A_WORDS:
        return "A"
    if stripped in GROUP_B_WORDS:
        return "B"
    return None


def _burst_runs(text):
    runs = []
    cur_cls, cur_words = "__unset__", []
    for w in text.split(" "):
        cls = _classify_word(w)
        if cls != cur_cls:
            if cur_words:
                runs.append((cur_cls, cur_words))
            cur_cls, cur_words = cls, [w]
        else:
            cur_words.append(w)
    if cur_words:
        runs.append((cur_cls, cur_words))
    return runs


def dialogue_burst_filters(text, y_top, enable):
    runs = _burst_runs(text)
    specs = []
    for cls, words in runs:
        if cls is None:
            specs.append((words, _font_base, DIALOGUE_BASE_COLOR, _ascent_base))
        elif cls == "A":
            specs.append((words, _font_kw, GROUP_A_COLOR, _ascent_kw))
        else:
            specs.append((words, _font_kw, GROUP_B_COLOR, _ascent_kw))

    widths = [font.getlength(" ".join(words)) for words, font, _, _ in specs]
    total_w = sum(widths) + _space_w * (len(specs) - 1)
    baseline_y = y_top + _ascent_base

    filters = []
    cur_x = (1080 - total_w) / 2
    for (words, font, color, ascent), w in zip(specs, widths):
        size = DIALOGUE_KW_SIZE if font is _font_kw else DIALOGUE_BASE_SIZE
        seg_y = round(baseline_y - ascent)
        filters.append(drawtext(" ".join(words), y=seg_y, size=size, color=color,
                                 x=f"{round(cur_x)}", enable=enable, box=False))
        cur_x += w + _space_w
    return filters


def extract_piece(idx):
    pid, start, end = PIECES[idx]
    d = end - start
    out = T / f"{pid}_raw.mp4"
    cmd = ["ffmpeg", "-y", "-ss", str(start), "-i", str(SRC), "-t", str(d),
           "-vf", CROP,
           "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
           "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
           str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        print(f"  EXTRACT ERROR ({pid}): {r.stderr[-500:]}")
        return None
    print(f"  {pid}: {dur(out):.2f}s")
    return out


# Structure caption (the hook device itself, not counted as a value-add, same scoping as
# v2/v3) — only at the pivot, kept deliberately vague per resilience-first tone.
PIVOT_START = G["pivot1_ask"]
PIVOT_END = PIVOT_START + 2.5
STRUCTURE_CAPTIONS = [
    (PIVOT_START, PIVOT_END, "THE STORY DOESN'T STOP THERE..."),
]

# Value-add 1: data_viz_overlay — stat cards during the HOOK.
STAT_CARDS = [
    (G["hook1_identity"], G["hook1_identity"] + durs[0], "40 YEARS ON WALL STREET"),
    (G["hook2_money"], G["hook2_money"] + durs[1], "$0.5-1B TRADED / DAY"),
]

# Value-add 2: this_or_that_overlay — abstract per resilience-first (names the CONTRAST,
# not the specific tragedy).
COMPARISON_CARD = ("THE MONEY   vs   THE STRUGGLE", PIVOT_START, PIVOT_END)

# CTA drawn from his own words (matches v3's "pull the CTA from the subject's own closing
# line" convention).
CTA = "MONEY = FREEDOM. NOT HAPPINESS."
CTA_START = TOTAL - 4.0
CTA_END = TOTAL

progress_bar = f"drawbox=x=0:y=ih-6:w=iw*(t/{TOTAL:.3f}):h=6:color=0xFFD400:t=fill"

# Permanent bottom band — masks the source's own burned-in caption under the hard-crop
# (ADR-0024), same technique as v3.
BOTTOM_BAND = "drawbox=x=0:y=1650:w=iw:h=270:color=black@1.0:t=fill"


def render():
    print(f"\n{'='*55}\n  {VID}\n{'='*55}")

    print(f"  Extracting {len(PIECES)} pieces (hard center-crop, ADR-0024)...")
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

    print(f"  Compositing overlays + {SPEED}x speed-up...")
    parts = [BOTTOM_BAND]
    for st, et, txt in STRUCTURE_CAPTIONS:
        parts.append(drawtext(txt, y=60, size=56, color="yellow",
                               enable=f"between(t,{st:.2f},{et:.2f})"))
    for st, et, txt in STAT_CARDS:
        parts.append(drawtext(txt, y=260, size=56, color="white",
                               enable=f"between(t,{st:.2f},{et:.2f})"))
    ca_txt, ca_start, ca_end = COMPARISON_CARD
    parts.append(drawtext(ca_txt, y=1450, size=40, color="0x7CFC00",
                           enable=f"between(t,{ca_start:.2f},{ca_end:.2f})",
                           boxcolor="black@0.65"))
    parts.append(drawtext(CTA, y=60, size=56, color="yellow",
                           enable=f"between(t,{CTA_START:.2f},{CTA_END:.2f})"))
    for pid, bursts in DIALOGUE_BURSTS.items():
        base = G[pid]
        for rel_st, rel_et, txt in bursts:
            enable = f"between(t,{base+rel_st:.2f},{base+rel_et:.2f})"
            parts.extend(dialogue_burst_filters(txt, y_top=1720, enable=enable))
    parts.append(progress_bar)

    vf = ",".join(parts) + f",setpts=PTS/{SPEED}"

    out = O / f"{VID}.mp4"
    cmd = ["ffmpeg", "-y", "-i", str(concat_out),
           "-vf", vf,
           "-af", f"atempo={SPEED}",
           "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
           "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
           str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
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
    print("  Audio: OK (1 stream)")
    return True


def main():
    print("="*60 + "\n  HARDKNOCKS V4 — WALL STREET LEGEND (Multi-Clip Mashup, hard-crop)\n" + "="*60)
    ok = render()
    print(f"\n{'='*60}\n  {'OK' if ok else 'FAIL'}\n{'='*60}")
    if ok:
        shutil.rmtree(T, ignore_errors=True)


if __name__ == "__main__":
    main()
