#!/usr/bin/env python3
"""hardknocks_v3 — "Implied Comparison" montage from npnyOvchXZs (School of Hard Knocks,
"Asking Billionaires If They Believe In God!").

3rd School of Hard Knocks source in the repo, but a different angle from v1/v2 (faith/God
vs pure wealth-psychology) — see data/source_videos.csv. Tone is deliberately neutral/
observational (explicit user decision via /grill-with-docs grilling session, scoped to
this video only, no new ADR): contrast a quick answer against a longer, more reflective
one without editorializing on whether the belief itself is true.

Structure (Multi-Clip Mashup, ADR-0022 — moments scattered across a 1296.5s/21:37 source):
- HOOK: 3 different billionaires each give a quick, near-one-word "yes" to "Do you believe
  in God?" (the unnamed veteran-fund investor's "Of course", Clint's "I sure do", Tim
  Tebow's "I do") — each <2s, satisfying the cadence rule via hard cuts alone.
- PIVOT: the SAME investor from the HOOK, revealed to have given a far longer, more
  nuanced answer moments later in the source — "wrestling with God" as a sign of
  closeness to God, not distance from it. Genuinely surprising relative to his own
  one-word HOOK answer, not just "longer" — a real callback, matching hardknocks_v2's
  Scooter Braun device (same person, HOOK vs PIVOT) rather than v2's "others vs one
  different person" variant.
- TEACH: Clint (2nd person from the HOOK) also elaborates well beyond his own quick
  answer when asked a follow-up — reinforces this isn't a cherry-picked one-off, same
  reinforcement role as v2's John segment.

Crop: hard center-crop (matching render_hardknocks_v1.py/v2.py), NOT blur-fill pillarbox.
Second pass per ADR-0024 (Hard-Crop Mandatory, No Pillarbox): the first render of this
video used pillarbox because this source's burned-in captions get clipped by a plain
center-crop (frame-tested) — the user rejected that pillarbox look outright on review
("must actually be cut to vertical"). Since hard-crop still clips the source's own
captions on this source, this version drops reliance on them entirely and burns in
self-authored, word-synced captions (from the mlx_whisper transcript) positioned to fit
inside the 1080px hard-crop safe zone instead.

Value-adds (Transformative Gate, ADR-0007, 2 distinct categories):
1. data_viz_overlay — stat card per billionaire during the HOOK montage (120 companies,
   $460M exit, NFL earnings).
2. this_or_that_overlay — a dedicated "1-WORD ANSWER vs 30-SECOND ANSWER" comparison card
   at the pivot, distinct from the HOOK/PIVOT structure captions (which are the hook
   device itself, not counted toward the 2 required value-adds, same scoping as v2).

Retention Technique (base quality, AGENTS.md): every piece was hand-cut at exact word
boundaries from the mlx_whisper transcript — checked programmatically, max internal gap
0.3s across all 8 pieces, so pause-trimming is a no-op here too (same finding as v2/v6).
A mild uniform 1.03x speed-up is still applied per the base-quality rule — kept mild
because the raw cut already lands at ~50.4s, right at the ~50s target, and a stronger
speed-up would push it below the ideal range.
"""
import subprocess, shutil, re
from pathlib import Path
from PIL import ImageFont

SRC = Path("output/projects/hardknocks/source/npnyOvchXZs.mp4")
O = Path("output/projects/hardknocks/final")
T = Path("output/projects/hardknocks/clips/temp_v3")
FONT = "/System/Library/Fonts/Helvetica.ttc"
FONT_BOLD = "/System/Library/Fonts/HelveticaNeue.ttc"

O.mkdir(parents=True, exist_ok=True)
T.mkdir(parents=True, exist_ok=True)

VID = "2026-07-12-hardknocks_v3_believe_in_god"  # date-prefixed per AGENTS.md convention
SPEED = 1.03  # mild — raw cut already ~50.4s, near the ~50s target (see module docstring)

# Hard center-crop (ADR-0024) — matches render_hardknocks_v1.py/v2.py. Frame-tested:
# both faces stay well-framed under this crop; only the source's own captions get clipped,
# which is fine now that this video authors its own captions instead of relying on them.
CROP = "scale=-2:1920,crop=1080:1920:(in_w-1080)/2:0"

# (id, src_start, src_end) — absolute seconds in the downloaded source
PIECES = [
    ("o1_investor", 238.82, 240.10),   # HOOK: "Do you believe in God?" "Of course."
    ("o2_clint",    487.78, 489.10),   # HOOK: "Do you believe in God?" "I sure do."
    ("o3_tebow",    842.86, 844.22),   # HOOK: "Do you believe in God?" "I do."
    ("p1_investor", 245.92, 256.70),   # PIVOT: "wrestling with God...closer to God"
    ("p2_investor", 256.74, 265.38),   # PIVOT: "...not wrestling with God"
    ("p3_investor", 265.42, 275.70),   # PIVOT: "...growing deeper in that faith"
    ("t1_clint",    506.10, 515.24),   # TEACH: "he showed up for me again and again"
    ("t2_clint",    515.24, 522.84),   # TEACH: "...favor of God coming behind me"
]

durs = [e - s for _, s, e in PIECES]
g = [sum(durs[:i]) for i in range(len(PIECES))]
TOTAL = sum(durs)
G = {pid: g[i] for i, (pid, *_r) in enumerate(PIECES)}
print("Piece durations:", [round(d, 2) for d in durs], "TOTAL:", round(TOTAL, 2))

# Self-authored dialogue captions (ADR-0024), word-synced from the mlx_whisper transcript
# (output/projects/hardknocks/source/npnyOvchXZs_transcript.json), 2-4 word bursts split at
# clause boundaries (commas/periods/question marks). Offsets are RELATIVE to each piece's
# own start (added to G[pid] at render time) — this replaces reliance on the source's own
# burned-in captions, which the hard-crop clips on both edges for this particular source.
DIALOGUE_BURSTS = {
    "o1_investor": [
        (0.00, 0.34, "Do you believe"),
        (0.34, 0.72, "in God?"),
        (0.86, 1.28, "Of course."),
    ],
    "o2_clint": [
        (0.00, 0.36, "Do you believe"),
        (0.36, 0.64, "in God?"),
        (0.70, 1.32, "I sure do."),
    ],
    "o3_tebow": [
        (0.00, 0.34, "Do you believe"),
        (0.34, 0.62, "in God?"),
        (0.92, 1.36, "I do."),
    ],
    "p1_investor": [
        (0.00, 0.64, "Every day,"),
        (0.78, 1.56, "I grow deeper in"),
        (1.56, 1.86, "my faith."),
        (1.88, 2.48, "And that doesn't mean"),
        (2.48, 3.66, "that I don't wrestle"),
        (3.66, 4.12, "with God."),
        (4.16, 4.54, "In fact,"),
        (4.84, 5.66, "the service I went"),
        (5.66, 6.08, "to a couple"),
        (6.08, 6.62, "weeks ago,"),
        (6.74, 7.40, "they talked about"),
        (7.40, 8.20, "by definition,"),
        (8.26, 8.94, "if you're wrestling"),
        (8.94, 9.42, "with God,"),
        (9.50, 10.28, "you are closer"),
        (10.28, 10.78, "to God."),
    ],
    "p2_investor": [
        (0.00, 1.40, "If you're accepting everything"),
        (1.40, 1.96, "that you hear,"),
        (2.08, 2.78, "everything you read,"),
        (2.94, 3.52, "and you're yes, yes,"),
        (3.52, 4.46, "and you think you're"),
        (4.46, 5.92, "living a godly life"),
        (5.92, 6.82, "and you're not questioning"),
        (6.82, 7.50, "in some way,"),
        (7.52, 8.22, "you're not wrestling"),
        (8.22, 8.64, "with God."),
    ],
    "p3_investor": [
        (0.00, 0.78, "So I think I"),
        (0.78, 1.78, "continue to wrestle"),
        (1.78, 2.24, "with God."),
        (2.32, 3.40, "I continue to ask"),
        (3.40, 4.32, "the questions that I"),
        (4.32, 5.30, "think are important"),
        (5.30, 5.72, "to me,"),
        (5.76, 6.96, "things I may disagree"),
        (6.96, 7.64, "with at times."),
        (7.66, 8.74, "But I'm always growing"),
        (8.74, 9.58, "deeper in that faith"),
        (9.58, 10.28, "through that process."),
    ],
    "t1_clint": [
        (0.00, 0.26, "Well,"),
        (0.26, 1.20, "he showed up for"),
        (1.20, 2.34, "me again and again."),
        (2.44, 3.02, "I grew up,"),
        (3.02, 3.84, "even though we didn't"),
        (3.84, 4.40, "know where we"),
        (4.40, 4.80, "could live,"),
        (4.88, 5.68, "there was always the"),
        (5.68, 6.66, "sense that God had"),
        (6.66, 7.52, "a bigger purpose,"),
        (7.64, 7.96, "that he had"),
        (7.96, 8.36, "a plan,"),
        (8.36, 9.14, "that he loved me."),
    ],
    "t2_clint": [
        (0.00, 0.48, "So it just gave"),
        (0.48, 2.06, "me confidence to start"),
        (2.06, 2.50, "a business,"),
        (2.58, 3.40, "to take a risk,"),
        (3.48, 4.24, "to know that there"),
        (4.24, 5.28, "was the favor of"),
        (5.28, 6.74, "God coming behind me"),
        (6.74, 7.40, "and going ahead"),
        (7.40, 7.60, "of me."),
    ],
}


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


# --- Dialogue-caption keyword emphasis (ADR-0018 addendum) ---------------------
# Base body text: yellow @ DIALOGUE_BASE_SIZE. Two keyword vocabularies get a
# color AND a +10% size bump (DIALOGUE_KW_SIZE) so they pop both chromatically
# and in scale, per the user's explicit request. Widths/baseline are computed
# with Pillow (same font file/face index ffmpeg's drawtext loads by default)
# so multi-color/multi-size runs on one line stay pixel-aligned and centered
# instead of relying on ffmpeg's own (single-string, single-style) text_w.
DIALOGUE_BASE_SIZE = 68
DIALOGUE_KW_SIZE = 75
DIALOGUE_BASE_COLOR = "yellow"
GROUP_A_COLOR = "white"                 # core faith/theology vocabulary
GROUP_B_COLOR = "0xFF3B1A"              # personal/emotional payoff vocabulary
GROUP_A_WORDS = {"god", "faith", "wrestle", "wrestling", "godly"}
GROUP_B_WORDS = {"deeper", "growing", "confidence", "purpose", "plan", "loved", "favor"}

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
    """Split a burst into (class, words) runs of consecutive same-class words."""
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
    """Render one burst as N drawtext filters (one per color/size run), pixel-
    positioned via Pillow so the runs sit on a shared, centered baseline."""
    runs = _burst_runs(text)
    specs = []  # (words, font, color, ascent)
    for cls, words in runs:
        if cls is None:
            specs.append((words, _font_base, DIALOGUE_BASE_COLOR, _ascent_base))
        elif cls == "A":
            specs.append((words, _font_kw, GROUP_A_COLOR, _ascent_kw))
        else:
            specs.append((words, _font_kw, GROUP_B_COLOR, _ascent_kw))

    widths = [font.getlength(" ".join(words)) for words, font, _, _ in specs]
    total_w = sum(widths) + _space_w * (len(specs) - 1)
    baseline_y = y_top + _ascent_base  # anchor baseline off the base-size ascent

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


# HOOK/structure captions (part of the hook, not counted as a value-add per v2 scoping)
HOOK_END = G["o3_tebow"] + durs[2]
PIVOT_START = G["p1_investor"]
PIVOT_END = PIVOT_START + 2.5

STRUCTURE_CAPTIONS = [
    (0.1, HOOK_END, "SOME GAVE A QUICK YES..."),
    (PIVOT_START, PIVOT_END, "THIS ONE KEPT GOING..."),
]

# Value-add 1: data_viz_overlay — stat card per billionaire during the HOOK montage
STAT_CARDS = [
    (G["o1_investor"], G["o1_investor"] + durs[0], "120 COMPANIES OWNED"),
    (G["o2_clint"], G["o2_clint"] + durs[1], "$460M COMPANY SALE"),
    (G["o3_tebow"], G["o3_tebow"] + durs[2], "$5-10M/YR (NFL CAREER)"),
]

# Value-add 2: this_or_that_overlay — dedicated comparison card, distinct from the
# STRUCTURE_CAPTIONS above (contrasts answer LENGTH/DEPTH, not people or beliefs).
# Positioned above the dialogue-caption band (y=1650) so the two never collide.
COMPARISON_CARD = ("1-WORD ANSWER   vs   30-SECOND ANSWER",
                    PIVOT_START, PIVOT_END)

# CTA drawn from the investor's own words ("always growing deeper in that faith")
CTA = "ALWAYS GROWING DEEPER"
CTA_START = TOTAL - 4.0
CTA_END = TOTAL

progress_bar = f"drawbox=x=0:y=ih-6:w=iw*(t/{TOTAL:.3f}):h=6:color=0xFFD400:t=fill"

# Permanent bottom band, on for the whole video — masks the source's own burned-in
# caption (which the hard-crop clips to an illegible fragment on both edges but does not
# remove) so it never shows through under our self-authored dialogue captions. A per-burst
# drawtext box was tried first and left a gap: the source caption's font is larger than
# ours and sits lower in frame, so it was still visible below our smaller boxed captions.
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
    parts = [BOTTOM_BAND]  # first, so all text below draws on top of it
    for st, et, txt in STRUCTURE_CAPTIONS:
        parts.append(drawtext(txt, y=60, size=76, color="yellow",
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
    # Self-authored dialogue captions (ADR-0024) — no per-line box, BOTTOM_BAND already
    # provides an opaque background across the whole band (see its comment above).
    # Keyword color/size emphasis per ADR-0018 addendum (see dialogue_burst_filters above).
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
    print("="*60 + "\n  HARDKNOCKS V3 — BELIEVE IN GOD (Multi-Clip Mashup, hard-crop)\n" + "="*60)
    ok = render()
    print(f"\n{'='*60}\n  {'OK' if ok else 'FAIL'}\n{'='*60}")
    if ok:
        shutil.rmtree(T, ignore_errors=True)


if __name__ == "__main__":
    main()
