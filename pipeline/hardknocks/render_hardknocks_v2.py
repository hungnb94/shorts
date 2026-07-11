#!/usr/bin/env python3
"""hardknocks_v2 — "Implied Comparison" montage from dK5bG5ZE3yI (School of Hard Knocks,
"Asking Billionaires If Getting Rich Was Worth It").

First genuine multi-source-interview test of the Implied Comparison pattern proposed in
docs/research/800m-view-case-study-2026-07-11/REPORT.md (section 5): several quick
"OTHERS SAY..." examples cut together, pivoting to "THIS ONE SAID..." held much longer.
bacsihai_v6 only reused the pattern's NAME on a single source (2-piece); this is the first
video where the "others" are genuinely different people, not a relabeled single narrative.

Structure (Multi-Clip Mashup, ADR-0022 — moments scattered across a 1491s/24:52 source):
- HOOK: host's own framing question ("does money buy happiness?"), then 3 different
  billionaires' quick, simple "yes I'm happy" answers (Lance/Body Armor, John/UK phones,
  the Vegas PE guy) — each <2s, each individually <15s per ADR-0007 gate item 3.
- PIVOT + PAYOFF: Scooter Braun's answer to the same question, held far longer (~25.2s
  across 3 concat pieces per ADR-0022 item 3, each still <15s) — genuine reveal, not
  padding: "I don't think that's how life works... people with a lot more money than me
  can feel very, very empty", followed by his own concrete takeaway ("start doing work
  on yourself now... that's a lot more important than making any amount of money") —
  added per user request to lengthen the video toward ~50s using more of the SAME
  real reveal rather than unrelated filler.
- TEACH: John's own fuller answer (cut short in the HOOK montage) reveals the same
  complexity once he elaborates — reinforces the reveal isn't a cherry-picked outlier.
- CLOSING: Lance's and the PE guy's own "money isn't the full answer" / "take your time"
  lines, both already introduced in the HOOK, giving a callback close.

Crop: plain center-crop (matching pipeline/hardknocks/render_hardknocks_v1.py), NOT the
blur-fill pillarbox from render_bacsihai_v6.py. Frame-checked (docs/production/hardknocks-
v2-implied-comparison.md): this source's burned-in captions sit safely inside a
1080-wide center crop of the scaled 3840x2160 frame, same as v1's source — pillarbox
was v6-specific (that source's captions spanned near-full 1920px width), not a general
rule (see the corrected plan for this video, and ADR-0007/0022 review notes).

Value-adds (Transformative Gate, ADR-0007, 2 distinct categories):
1. data_viz_overlay — net worth / exit stat cards during the HOOK montage.
2. counter_argument — "COUNTER: ..." label during TEACH, naming the reveal explicitly.
The OTHERS-vs-THIS-ONE labels are part of the HOOK/structure, not counted as a value-add.

Retention Technique (base quality, AGENTS.md): every chosen clip was already hand-cut to
exact word boundaries (verified: zero internal gaps >0.3s in any piece — see production
doc), so pause-trimming has nothing to remove here. A mild uniform 1.06x speed-up
(setpts/atempo) is applied at the end regardless, per the mandatory base-quality rule —
tuned down from the 1.1x used elsewhere because Scooter's payoff is dense, reflective
speech that loses clarity if over-compressed.
"""
import subprocess, shutil
from pathlib import Path

SRC = Path("output/projects/hardknocks/source/dK5bG5ZE3yI.mp4")
O = Path("output/projects/hardknocks/final")
T = Path("output/projects/hardknocks/clips/temp_v2")
FONT = "/System/Library/Fonts/Helvetica.ttc"
FONT_BOLD = "/System/Library/Fonts/HelveticaNeue.ttc"

O.mkdir(parents=True, exist_ok=True)
T.mkdir(parents=True, exist_ok=True)

VID = "2026-07-11-hardknocks_v2_implied_comparison"  # date-prefixed per AGENTS.md convention
SPEED = 1.06  # tuned down further (was 1.08) so the added p3_scooter piece lands near 50s

CROP = "scale=-2:1920,crop=1080:1920:(in_w-1080)/2:0"

# (id, src_start, src_end) — absolute seconds in the downloaded source
PIECES = [
    ("host",       99.34,   102.02),
    ("o1_lance",   225.42,  226.58),
    ("o2_john",    534.44,  535.96),
    ("o3_pe",      1300.90, 1302.60),
    ("p1_scooter", 946.90,  950.30),
    ("p2_scooter", 959.28,  971.40),
    ("p3_scooter", 971.48,  981.14),
    ("t1_john",    512.62,  518.18),
    ("t1b_john",   526.48,  530.70),
    ("t2_john",    535.96,  540.26),
    ("c1_lance",   233.96,  236.38),
    ("c2_pe",      1423.82, 1428.24),
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
             x="(w-text_w)/2", font=FONT_BOLD):
    t = esc(text)
    parts = [f"drawtext=text='{t}'", f"fontfile={font}", f"fontsize={size}",
              f"fontcolor={color}", "borderw=4", "bordercolor=black@0.9",
              f"x={x}", f"y={y}", "expansion=none"]
    if box:
        parts += ["box=1", "boxcolor=black@0.55", "boxborderw=14"]
    if enable:
        parts.append(f"enable='{enable}'")
    return ":".join(parts)


def extract_piece(idx):
    pid, start, end = PIECES[idx]
    d = end - start
    vf = f"{CROP},zoompan=z='min(zoom+0.0006,1.08)':d=1:s=1080x1920:fps=30"
    out = T / f"{pid}_raw.mp4"
    cmd = ["ffmpeg", "-y", "-ss", str(start), "-i", str(SRC), "-t", str(d),
           "-vf", vf,
           "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
           "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
           str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        print(f"  EXTRACT ERROR ({pid}): {r.stderr[-500:]}")
        return None
    print(f"  {pid}: {dur(out):.2f}s")
    return out


# HOOK/structure captions (part of the hook, not counted as a value-add)
OTHERS_LABEL_START = 0.1  # near-instant (ADR-0018: caption visible by t=0.2s) — user
                          # feedback on the first cut of this video: hook text appeared
                          # too late (1.3s) and too small to hold attention immediately.
                          # zoompan's continuous motion already satisfies Hook Gate item 6
                          # cadence on its own, so nothing is lost by not delaying this.
OTHERS_LABEL_END = G["o3_pe"] + durs[3]  # end of o3_pe
PIVOT_LABEL_START = G["p1_scooter"]
PIVOT_LABEL_END = PIVOT_LABEL_START + 2.3

STRUCTURE_CAPTIONS = [
    # shortened from "OTHERS SAY MONEY = HAPPY..." so a bigger fontsize still
    # fits 1080px width without clipping (frame-verified: at size=64 the
    # original 27-char string already ran edge-to-edge; tightened further,
    # dropping spaces around "=", to free width for another size bump)
    (OTHERS_LABEL_START, OTHERS_LABEL_END, "OTHERS: MONEY=HAPPY"),
    (PIVOT_LABEL_START, PIVOT_LABEL_END, "THIS ONE SAID..."),
]

# Value-add 1: data_viz_overlay — net worth / exit stat cards during the HOOK montage
STAT_CARDS = [
    (G["o1_lance"], G["o1_lance"] + durs[1], "$5B SOLD TO COCA-COLA"),
    (G["o2_john"], G["o2_john"] + durs[2], "$1.5B EXIT (UK)"),
    (G["o3_pe"], G["o3_pe"] + durs[3], "$1.6B NET WORTH"),
    (G["p1_scooter"], G["p1_scooter"] + 2.0, "$1B+ EXIT"),
]

# Value-add 2: counter_argument — names the reveal explicitly during TEACH
# (shortened from "COUNTER: THE 'HAPPY' ANSWER ISN'T THE FULL STORY" — same
# fontsize-vs-width reason as STRUCTURE_CAPTIONS above)
COUNTER_ARGUMENT = ("COUNTER: NOT THE FULL STORY",
                     G["t1_john"], G["t2_john"] + durs[8])

CTA = "REAL WEALTH = KNOWING YOURSELF"  # shortened from "...KNOWING WHO YOU ARE" for size
CTA_START = TOTAL - 4.3
CTA_END = TOTAL

progress_bar = f"drawbox=x=0:y=ih-6:w=iw*(t/{TOTAL:.3f}):h=6:color=0xFFD400:t=fill"


def render():
    print(f"\n{'='*55}\n  {VID}\n{'='*55}")

    print(f"  Extracting {len(PIECES)} pieces (center-crop, matching v1)...")
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
    parts = []
    for st, et, txt in STRUCTURE_CAPTIONS:
        parts.append(drawtext(txt, y=60, size=84, color="yellow",
                               enable=f"between(t,{st:.2f},{et:.2f})"))
    for st, et, txt in STAT_CARDS:
        parts.append(drawtext(txt, y=260, size=64, color="white",
                               enable=f"between(t,{st:.2f},{et:.2f})"))
    ca_txt, ca_start, ca_end = COUNTER_ARGUMENT
    parts.append(drawtext(ca_txt, y=60, size=56, color="0x7CFC00",
                           enable=f"between(t,{ca_start:.2f},{ca_end:.2f})"))
    parts.append(drawtext(CTA, y=60, size=56, color="yellow",
                           enable=f"between(t,{CTA_START:.2f},{CTA_END:.2f})"))
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
    print("="*60 + "\n  HARDKNOCKS V2 — IMPLIED COMPARISON (Multi-Clip Mashup)\n" + "="*60)
    ok = render()
    print(f"\n{'='*60}\n  {'OK' if ok else 'FAIL'}\n{'='*60}")
    if ok:
        shutil.rmtree(T, ignore_errors=True)


if __name__ == "__main__":
    main()
