#!/usr/bin/env python3
"""hardknocks_v5 — Nigerian real-estate developer reveal, from g9K6l15bQGc (School of Hard
Knocks, "Asking Nigerian Billionaires How They Got Rich!").

5th School of Hard Knocks source (see data/source_videos.csv). Same-person-callback
Implied Comparison device as v2-v4 (CONTEXT.md), Multi-Clip Mashup (ADR-0022 — pieces
scattered ~480-591s and one closing zinger at ~683s of a 1532.4s source, no single 45-60s
window contains them all):
- HOOK: developer's own quick credential/Money+Number answers (21 years, 5000+ units,
  $50M in a single year).
- PIVOT: asked if he ever imagined this growing up, he reveals real childhood hardship —
  no roof over their head, evicted, slept under a bridge.
- TEACH: his own wisdom on reputation/keeping your word, and a contrarian finance lesson
  (banks want your money idle, not working for you).
- CTA: his own aphorism, pulled verbatim from later in the same interview ("Branding never
  sleeps.") — same "CTA from the subject's own closing line" convention as v3/v4.

Explicit swipe-away-reduction target for this video (per this repo's 2026-07-13 research
session, docs/research/hard-work-pays-off-2026-07-13/ and the Giannis V2 root-cause in
ADR-0017): apply every currently-confirmed rule at once — frame-0 face check (all pieces
verified via direct frame reads, tight two-shot framing throughout, no full-screen b-roll
anywhere per the new ADR-0017 addendum), ADR-0018 caption sync/cadence, and a 3-color
keyword-emphasis palette (extends v3/v4's 2-color scheme) as the incremental refinement
flagged in that research as low-risk to test on the next video.

Crop: hard center-crop (ADR-0024), matching v1-v4. Self-authored, word-synced captions
(mlx_whisper transcript), auto-split into bursts (see auto_bursts(), ported from v4).

Value-adds (Transformative Gate, ADR-0007, 2 distinct categories):
1. data_viz_overlay — stat cards during the HOOK ("21 YEARS A DEVELOPER",
   "5,000+ UNITS BUILT", "$50M IN ONE YEAR").
2. this_or_that_overlay — "$50M DEVELOPER vs SLEPT UNDER A BRIDGE" comparison card at the
   pivot reveal (Implied Comparison device, CONTEXT.md).

Retention Technique (base quality, AGENTS.md): pieces hand-selected at exact word
boundaries from the mlx_whisper transcript (output/projects/hardknocks/source/
g9K6l15bQGc_transcript.json). Raw cut lands at ~45.3s (all-substantive content, no filler
padding — see this repo's duration-preference memory: top of the 45-60s range via more
authentic content, not the tightest possible cut), only a mild uniform speed-up applied.
"""
import json
import subprocess
import shutil
import re
from pathlib import Path
from PIL import ImageFont

SRC = Path("output/projects/hardknocks/source/g9K6l15bQGc.mp4")
TRANSCRIPT = Path("output/projects/hardknocks/source/g9K6l15bQGc_transcript.json")
O = Path("output/projects/hardknocks/final")
T = Path("output/projects/hardknocks/clips/temp_v5")
FONT = "/System/Library/Fonts/Helvetica.ttc"
FONT_BOLD = "/System/Library/Fonts/HelveticaNeue.ttc"

O.mkdir(parents=True, exist_ok=True)
T.mkdir(parents=True, exist_ok=True)

VID = "2026-07-14-hardknocks_v5_bridge_developer"  # date-prefixed per AGENTS.md convention
SPEED = 1.02  # mild — raw cut already ~45.3s, all-substantive, no filler to trim

# Hard center-crop (ADR-0024) — matches render_hardknocks_v1-v4.py.
CROP = "scale=-2:1920,crop=1080:1920:(in_w-1080)/2:0"

# (id, src_start, src_end) — absolute seconds in the downloaded source, exact word
# boundaries from g9K6l15bQGc_transcript.json (word_timestamps=True).
PIECES = [
    ("hook1_years",     480.32, 481.02),  # "21 years."
    ("hook2_units",     498.46, 500.38),  # "Well, I'm sure we've done over 5000 units."
    ("hook3_money",     505.34, 506.12),  # "Fifty million dollars."
    ("pivot1_never",    510.16, 516.74),  # "Never...my growing up was not anything like this. There was a time we didn't have a roof over our head."
    ("pivot2_bridge",   517.92, 524.14),  # "Yeah...living in my mom's store and the landlord kicked us out. So we spent some time under the bridge."
    ("pivot3_vision",   526.48, 533.48),  # "Absolutely...you don't even have a good roof over your head. So what kind of vision are you going to have? What ambition would you have?"
    ("teach1_deliverer",567.06, 572.94),  # "On the promise of a deliverer. Your name is the first opportunity for you to make money."
    ("teach2_integrity",572.94, 576.12),  # "What do you make out of your name? What is the integrity behind your name?"
    ("teach3_word",     576.16, 582.88),  # "You got to keep your word...So if you tell people you'll deliver quality houses for them, deliver quality houses."
    ("teach4_banks",    585.52, 590.98),  # "Banks love everybody to keep their money idle in the banks rather than money working for them."
    ("cta_branding",    682.70, 683.52),  # "Branding never sleeps."
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


# --- Word-synced dialogue captions, auto-split into bursts (ported from v4) -----
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
        # mlx_whisper word tokens already carry their own leading space (or lack of one) -
        # concatenate raw and strip once at the ends (hardknocks_v4 stray-space pitfall).
        text = "".join(w["word"] for w in b).strip()
        out.append((max(0.0, rel_st), rel_et, text))
    return out


DIALOGUE_BURSTS = {pid: auto_bursts(s, e) for pid, s, e in PIECES}
for pid, bursts in DIALOGUE_BURSTS.items():
    print(f"  {pid}: {len(bursts)} bursts -> {[t for _, _, t in bursts]}")


# --- Dialogue-caption keyword emphasis (ADR-0018 addendum), 3-COLOR extension -----------
# Base body text: yellow @ DIALOGUE_BASE_SIZE (matches v3/v4's base size/color).
# GROUP_MONEY (white) = credibility/stats vocabulary — establishes the HOOK's stature.
# GROUP_HARDSHIP (red-orange) = the adversity/PIVOT vocabulary — the reveal this video
#   turns on.
# GROUP_WISDOM (green) = the TEACH payoff vocabulary — the actionable lesson.
# This is the incremental 3-color-palette refinement flagged (not yet confirmed) in
# docs/research/hard-work-pays-off-2026-07-13/REPORT.md section 4 — v3/v4 only used 2
# groups (base + 1 emphasis color); this video is the first test of a 3rd distinct group.
DIALOGUE_BASE_SIZE = 68
DIALOGUE_KW_SIZE = 75
DIALOGUE_BASE_COLOR = "yellow"
GROUP_MONEY_COLOR = "white"
GROUP_HARDSHIP_COLOR = "0xFF3B1A"
GROUP_WISDOM_COLOR = "0x7CFC00"
GROUP_MONEY_WORDS = {"21", "years", "5000", "units", "fifty", "million", "dollars"}
GROUP_HARDSHIP_WORDS = {"never", "roof", "bridge", "landlord", "kicked"}
GROUP_WISDOM_WORDS = {"name", "word", "deliver", "quality", "banks", "idle", "working"}

_font_base = ImageFont.truetype(FONT_BOLD, DIALOGUE_BASE_SIZE, index=0)
_font_kw = ImageFont.truetype(FONT_BOLD, DIALOGUE_KW_SIZE, index=0)
_space_w = _font_base.getlength(" ")
_ascent_base, _descent_base = _font_base.getmetrics()
_ascent_kw, _descent_kw = _font_kw.getmetrics()


def _classify_word(word):
    stripped = re.sub(r"[^\w']", "", word).lower()
    if stripped in GROUP_MONEY_WORDS:
        return "MONEY"
    if stripped in GROUP_HARDSHIP_WORDS:
        return "HARDSHIP"
    if stripped in GROUP_WISDOM_WORDS:
        return "WISDOM"
    return None


_GROUP_COLOR = {"MONEY": GROUP_MONEY_COLOR, "HARDSHIP": GROUP_HARDSHIP_COLOR,
                "WISDOM": GROUP_WISDOM_COLOR}


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
        else:
            specs.append((words, _font_kw, _GROUP_COLOR[cls], _ascent_kw))

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
# v2/v3/v4) — only at the pivot, deliberately vague to keep the gap open (Stage 0 item 2).
PIVOT_START = G["pivot1_never"]
PIVOT_END = PIVOT_START + 2.5
STRUCTURE_CAPTIONS = [
    (PIVOT_START, PIVOT_END, "BUT GROWING UP..."),
]

# Value-add 1: data_viz_overlay — stat cards during the HOOK.
STAT_CARDS = [
    (G["hook1_years"], G["hook1_years"] + durs[0], "21 YEARS A DEVELOPER"),
    (G["hook2_units"], G["hook2_units"] + durs[1], "5,000+ UNITS BUILT"),
    (G["hook3_money"], G["hook3_money"] + durs[2], "$50M IN ONE YEAR"),
]

# Value-add 2: this_or_that_overlay — Implied Comparison card at the pivot reveal.
COMPARISON_CARD = ("$50M DEVELOPER   vs   SLEPT UNDER A BRIDGE",
                    G["pivot2_bridge"], G["pivot2_bridge"] + durs[4])

# CTA drawn from his own words (matches v3/v4's "pull the CTA from the subject's own
# closing line" convention) — pulled from later in the same interview (t=682.7s source).
CTA = "BRANDING NEVER SLEEPS."
CTA_START = G["cta_branding"]
CTA_END = TOTAL

progress_bar = f"drawbox=x=0:y=ih-6:w=iw*(t/{TOTAL:.3f}):h=6:color=0xFFD400:t=fill"

# Permanent bottom band — masks the source's own burned-in caption under the hard-crop
# (ADR-0024), same technique as v2-v4.
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
    parts.append(drawtext(ca_txt, y=1450, size=36, color="0x7CFC00",
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
    print("="*60 + "\n  HARDKNOCKS V5 — BRIDGE DEVELOPER (Multi-Clip Mashup, hard-crop)\n" + "="*60)
    ok = render()
    print(f"\n{'='*60}\n  {'OK' if ok else 'FAIL'}\n{'='*60}")
    if ok:
        shutil.rmtree(T, ignore_errors=True)


if __name__ == "__main__":
    main()
