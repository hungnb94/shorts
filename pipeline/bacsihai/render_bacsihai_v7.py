#!/usr/bin/env python3
"""bacsihai_v7 — "Cholesterol Isn't The Enemy" Multi-Clip Mashup from MTcn9LRJSH0
(Bac si Hai, "Dung Voi So Cholesterol: Day La Chat Co The Khong The Thieu").

First use of this source (see data/source_videos.csv). Health/Vietnamese vertical
(ADR-0019), Clip Curation Edit exclusively (AGENTS.md).

Structure (Multi-Clip Mashup, ADR-0022 — the concrete payoff sits ~48s into a 45s
stakes-building preamble, so a Contiguous VO of the raw intro would bury the
payoff far past the Stage 0 item 4 ~5-10s target):
- HOOK (0.00-11.18 src): source's own cold open — "if you're one of millions who
  think cholesterol is a bad molecule that harms the body, this video will wake
  you up or annoy you a little." Frame-0 verified clean (host's face, no overlay)
  via frame extraction before any edit; the source's own kinetic-typography/
  stock-photo hook-montage plays out over the rest of this piece as high-cadence
  B-roll (ADR-0016/0018 item 6 easily satisfied).
- SKIP 11.18-48.66 src: a ~37s stakes-building tangent ("today I'll list 7
  functions... if we lacked them we'd die within minutes, literally... I'll
  destroy that myth") — dramatic but repetitive with the HOOK's own tension, and
  visually dominated by title cards / stock B-roll / 3D cell graphics (frame-
  checked at 29.7s, 35s, 40.5s-46s), not the host. Skipping it pulls the reveal
  forward, same device bacsihai_v6 used.
- REVEAL 1 (48.66-65.94 src): "it's 80% self-produced by the body, only 20% from
  food — no matter how much we eat" (Money+Number payoff). Frame-checked clean/
  dramatic host shot at 49.5s (pointing gesture + the source's own red "80%
  LƯỢNG CHOLESTEROL" stat callout) once a brief "ĐIỀU 1" title-card fade clears.
- REVEAL 2 (106.08-124.34 src): "cholesterol is life's foundational material —
  our body has ~30 trillion cells, each with a membrane, and without it cells
  can't function and die" — 2nd concrete stat reinforcing the same thesis, plus
  the opening of the shelter/house analogy (cut before it hands off to stock
  crosswalk B-roll at ~125s, frame-checked).
- CLOSER (154.54-158.52 src): source's own closing thesis line, "so cholesterol
  IS the material that sustains life in the body" — a natural button/close.

Payoff-timing (Stage 0 item 4): REVEAL 1 begins at cumulative clip-time = 11.18s
raw (~10.85s post speed-up) — right at the edge of the ~5-10s target, not buried
past ~15s.

Crop: hard center-crop (ADR-0024), matching v6/hardknocks_v1-3. This source's
burned-in captions and mid-sentence kinetic-typography cards span nearly the
full 1920px frame width (frame-verified, e.g. the CLOSER piece's own text runs
edge-to-edge) — a hard crop would clip them, so every piece uses self-authored,
word-synced captions from the mlx_whisper transcript instead, positioned inside
the 1080px safe zone (same resolution as hardknocks_v3, applied uniformly here
across all 4 pieces rather than case-by-case).

Value-adds (Transformative Gate, ADR-0007, 2 distinct categories):
1. fact-check-callout — persistent header: "NHIỀU NGƯỜI NGHĨ..." during the HOOK,
   swapping to "SỰ THẬT: ..." for the two REVEAL pieces (myth vs. fact framing).
2. data_viz_overlay — stat cards ("80% TỰ CƠ THỂ TẠO RA" / "30.000 TỶ TẾ BÀO")
   reinforcing the two REVEAL pieces' own numbers.

Retention Technique (base quality, AGENTS.md): word-level gap check across all 4
chosen pieces found a max internal gap of 0.42s (reveal1) — pause-trimming is a
no-op here too (same finding as v5/v6/hardknocks_v3). A mild uniform 1.03x
speed-up is still applied per the base-quality rule — kept mild because the raw
cut already lands at ~50.7s, matching the project's ~50s preference.

No TTS: caption/overlay commentary only, matching 100% of bacsihai v1-v6
precedent (TTS stays scoped to the AI-education niche, ADR-0021).
"""
import subprocess, shutil, re
from pathlib import Path
from PIL import ImageFont

SRC = Path("output/projects/bacsihai/source/MTcn9LRJSH0.mp4")
O = Path("output/projects/bacsihai/final")
T = Path("output/projects/bacsihai/clips/temp_v7")
FONT = "/System/Library/Fonts/Helvetica.ttc"
FONT_BOLD = "/System/Library/Fonts/HelveticaNeue.ttc"

O.mkdir(parents=True, exist_ok=True)
T.mkdir(parents=True, exist_ok=True)

VID = "2026-07-12-bacsihai_v7_cholesterol_not_the_enemy"
SPEED = 1.03  # mild — raw cut already ~50.7s, near the ~50s target (see module docstring)

# Hard center-crop (ADR-0024) — matches v1-v3/hardknocks. Source is 1920x1080 native.
CROP = "scale=-2:1920,crop=1080:1920:(in_w-1080)/2:0"

# (id, src_start, src_end) — absolute seconds in the downloaded source
PIECES = [
    ("hook",     0.00,   11.18),   # HOOK: "this video will wake you up... or annoy you"
    ("reveal1", 48.66,   65.94),   # REVEAL 1: "80% self-produced, only 20% from food"
    ("reveal2", 106.08, 124.34),   # REVEAL 2: "30 trillion cells, membrane, die without it"
    ("closer", 154.54,  158.52),   # CLOSER: "cholesterol IS the material of survival"
]

durs = [e - s for _, s, e in PIECES]
g = [sum(durs[:i]) for i in range(len(PIECES))]
TOTAL = sum(durs)
G = {pid: g[i] for i, (pid, *_r) in enumerate(PIECES)}
print("Piece durations:", [round(d, 2) for d in durs], "TOTAL:", round(TOTAL, 2))

# Self-authored dialogue captions (ADR-0024), word-synced from the mlx_whisper transcript
# (output/projects/bacsihai/source/MTcn9LRJSH0_transcript.json), chunked to ~1-1.5s bursts
# at phrase boundaries. Offsets are RELATIVE to each piece's own start (added to G[pid] at
# render time). "chết" self-censored as "chế.t" matching this source's own on-screen
# convention (seen burned into its captions, e.g. at src ~35s: "chúng ta sẽ chế.t").
DIALOGUE_BURSTS = {
    "hook": [
        (0.00, 1.02, "Nếu bạn là một"),
        (1.02, 2.20, "trong số hàng triệu người"),
        (2.20, 3.18, "ngoài kia nghĩ rằng"),
        (3.18, 4.30, "cholesterol là"),
        (4.30, 5.24, "một phần tử xấu"),
        (5.24, 6.32, "gây hại cho cơ thể"),
        (6.32, 7.14, "thì rất có thể"),
        (7.14, 8.14, "video này sẽ"),
        (8.14, 9.02, "làm bạn thức tỉnh"),
        (9.02, 9.84, "hoặc có thể khiến"),
        (9.84, 11.18, "bạn khó chịu một chút"),
    ],
    "reveal1": [
        (0.00, 1.30, "nó chính là 80%"),
        (1.30, 2.42, "lượng cholesterol"),
        (2.42, 3.32, "do cơ thể"),
        (3.32, 4.26, "chúng ta tự tạo ra"),
        (4.26, 5.48, "và chỉ có khoảng 20%"),
        (5.48, 6.66, "cái thứ"),
        (6.66, 7.50, "mà chúng ta ăn vào"),
        (7.50, 8.58, "và cái thứ mà chúng ta"),
        (8.58, 9.34, "vẫn hay kiêng"),
        (9.76, 10.78, "là ăn cái này thì"),
        (10.78, 11.94, "nhiều cholesterol"),
        (11.94, 12.74, "cái kia thì nhiều"),
        (12.74, 13.42, "cholesterol"),
        (13.42, 14.66, "thì nó chỉ đóng góp"),
        (14.66, 15.38, "20% thôi"),
        (15.38, 16.20, "thì chúng ta có"),
        (16.20, 17.28, "ăn bao nhiêu đi chẳng nữa"),
    ],
    "reveal2": [
        (0.00, 0.94, "cholesterol là"),
        (0.94, 2.14, "vật liệu nền tảng"),
        (2.14, 3.12, "cho sự sống cơ thể"),
        (3.12, 4.24, "của chúng ta có khoảng tầm"),
        (4.24, 5.24, "30 nghìn tỷ"),
        (5.24, 5.70, "tế bào"),
        (5.70, 6.42, "mỗi một tế bào"),
        (6.42, 7.10, "đều có một lớp"),
        (7.10, 8.24, "màng tế bào bao quanh"),
        (8.24, 9.06, "và nếu như mất"),
        (9.06, 9.82, "cái màng này thì"),
        (9.82, 10.86, "tế bào sẽ không thể"),
        (10.86, 11.80, "hoạt động và sẽ"),
        (11.80, 12.06, "chế.t"),
        (12.06, 12.84, "nó giống như việc"),
        (12.84, 13.90, "con người chúng ta"),
        (13.90, 14.74, "khi mà sống trước"),
        (14.74, 15.52, "thiên nhiên thì"),
        (15.52, 16.36, "chúng ta ít nhất"),
        (16.36, 17.40, "phải có một cái túc lèo"),
        (17.40, 18.26, "để chúng ta tre thân"),
    ],
    "closer": [
        (0.00, 1.12, "vậy nên cholesterol"),
        (1.12, 2.14, "là vật liệu cấu tạo"),
        (2.14, 3.20, "nên sự sống còn"),
        (3.20, 3.98, "trong cơ thể"),
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
# Base body text: yellow @ DIALOGUE_BASE_SIZE. Group A (stat numbers, matching the
# source's own red-callout convention seen at src ~49.5s/55s) and Group B (life/
# essential-framing words, reinforcing the myth-busting thesis) get a color AND a
# +10% size bump, same pattern as hardknocks_v3's dialogue_burst_filters.
DIALOGUE_BASE_SIZE = 60
DIALOGUE_KW_SIZE = 66
DIALOGUE_BASE_COLOR = "yellow"
GROUP_A_COLOR = "0xFF3B1A"               # stat numbers — red, matches source's own callouts
GROUP_B_COLOR = "0x4CD137"               # life/essential-framing words — green
GROUP_A_WORDS = {"80", "20", "30", "nghìn", "tỷ"}
GROUP_B_WORDS = {"sống", "còn", "tảng", "nền", "thiết"}

_font_base = ImageFont.truetype(FONT_BOLD, DIALOGUE_BASE_SIZE, index=0)
_font_kw = ImageFont.truetype(FONT_BOLD, DIALOGUE_KW_SIZE, index=0)
_space_w = _font_base.getlength(" ")
_ascent_base, _descent_base = _font_base.getmetrics()
_ascent_kw, _descent_kw = _font_kw.getmetrics()


def _classify_word(word):
    stripped = re.sub(r"[^\w%']", "", word).lower()
    stripped = stripped.rstrip("%")
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


# Value-add 1: fact-check-callout — persistent header, myth (HOOK) vs. fact (REVEALs)
HOOK_END = G["reveal1"]
REVEAL_END = G["closer"]
STRUCTURE_CAPTIONS = [
    (0.1, HOOK_END, "LẦM TƯỞNG: CHOLESTEROL = XẤU"),
    (HOOK_END, REVEAL_END, "SỰ THẬT: THIẾT YẾU CHO SỰ SỐNG"),
]

# Value-add 2: data_viz_overlay — stat cards reinforcing each REVEAL's own number
STAT_CARDS = [
    (G["reveal1"], G["reveal1"] + 8.5, "80% TỰ CƠ THỂ TẠO RA"),
    (G["reveal2"], G["reveal2"] + 8.0, "30.000 TỶ TẾ BÀO"),
]

# CTA during the CLOSER piece
CTA = "THEO DÕI ĐỂ HIỂU ĐÚNG SỨC KHỎE"
CTA_START = G["closer"]
CTA_END = TOTAL

progress_bar = f"drawbox=x=0:y=ih-6:w=iw*(t/{TOTAL:.3f}):h=6:color=0xFFD400:t=fill"

# Permanent bottom band, on for the whole video — masks the source's own burned-in
# caption/kinetic-typography text (which the hard-crop clips to an illegible fragment on
# both edges but does not remove) so it never shows through under our self-authored
# dialogue captions. Same technique as render_hardknocks_v3.py.
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
        parts.append(drawtext(txt, y=60, size=56, color="yellow",
                               enable=f"between(t,{st:.2f},{et:.2f})"))
    for st, et, txt in STAT_CARDS:
        parts.append(drawtext(txt, y=280, size=52, color="white",
                               enable=f"between(t,{st:.2f},{et:.2f})"))
    parts.append(drawtext(CTA, y=60, size=48, color="yellow",
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
    print("="*60 + "\n  BACSIHAI V7 — CHOLESTEROL NOT THE ENEMY (Multi-Clip Mashup, hard-crop)\n" + "="*60)
    ok = render()
    print(f"\n{'='*60}\n  {'OK' if ok else 'FAIL'}\n{'='*60}")
    if ok:
        shutil.rmtree(T, ignore_errors=True)


if __name__ == "__main__":
    main()
