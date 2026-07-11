#!/usr/bin/env python3
"""Working With AI — Capability Curve v2: Multi-Clip Mashup rebuild of v1.

User feedback on v1 (pipeline/aiwork/render_aiwork_v1.py): the TTS preamble ("Straight
from Anthropic's own stage.") delayed the source's own strong hook past the 0-2s Hook
Gate window, and a single 46s contiguous segment wastes a 905s source that has stronger
moments scattered across it. v2 responds with the Multi-Clip Mashup sub-format (ADR-0022):
10 independently-extracted, non-contiguous ranges (some further split at internal pause
points or shot changes, but always <15s per ADR-0007), stitched via ffmpeg concat demuxer,
hard cuts only (no crossfade/sound-design/zoompan — dropped for this video per user
decision). No TTS: captions alone satisfy ADR-0007 gate item 1.

New Retention Technique (AGENTS.md): after all cuts/overlays are burned in at 1.0x, the
whole assembled timeline gets a uniform 1.1x speed-up (setpts + atempo) as the final pass.

Clip/crop notes (frame-verified, not guessed — see docs/production/aiwork-v2-capability-
curve.md):
- HOOK (186.62-193.58) is ONE continuous extract, not two: the source cuts from a tight
  portrait shot to the wide stage shot mid-word (inside "than", ~191.85s), so splitting it
  into two concat pieces would guillotine that word's audio. A single extract with a
  time-varying crop x-offset (crop filter's own 't' variable, confirmed via a drawtext
  pts test to be relative to this clip's own start when -ss precedes -i) avoids that.
- STATS (224.22-234.58, split at a natural pause into stats_a/stats_b) is a full-screen
  data-chart insert in the source, not the presenter+stage shot v1 assumed — confirmed by
  direct frame extraction. Cropping it to 1080 wide would cut off either the early data
  points or the punchline number, so it gets the same scale-to-fit+letterbox treatment as
  CLOSE's graphic half, not CROP_WIDE.
- CLOSE (367.72-374.42, split into close_a/close_b at a clean word boundary) opens on a
  full-screen "Opus 4.7 stats card" graphic (same letterbox treatment as STATS), then cuts
  to a Claude-logo bumper immediately followed by the wide stage shot. A ~0.15-0.2s tight
  profile insert right at the very tail is absorbed into close_b's CROP_WIDE treatment
  rather than given a third crop — the sliver is imperceptible before the video ends.
"""
import subprocess, shutil
from pathlib import Path

SRC = Path("output/projects/aiwork/source/tP4MGcJ80Y0_1080p.webm")
CHART_PNG = Path("output/projects/aiwork/final/assets/capability_curve_chart.png")
O = Path("output/projects/aiwork/final")
T = Path("output/projects/aiwork/clips/temp_v2")
FONT = "/System/Library/Fonts/Helvetica.ttc"
FONT_BOLD = "/System/Library/Fonts/HelveticaNeue.ttc"

O.mkdir(parents=True, exist_ok=True)
T.mkdir(parents=True, exist_ok=True)

VID = "capability_curve_v2"
SPEED = 1.1

# Presenter crops (verified via frame extraction, see docstring above)
CROP_TIGHT_X = "(in_w-1080)/2"   # true center crop, plain-background portrait shot
CROP_WIDE_X = 1650               # v1's established offset, wide "Code w/ Claude" stage shot
HOOK_SWITCH_T = 5.20             # local seconds within the hook piece: tight -> wide crop
GRAPHIC_VF = "scale=1080:-2,pad=1080:1920:0:(1920-ih)/2:black"

# (id, src_start, src_end, treatment) — treatment picks the crop/pad filter in extract_piece()
PIECES = [
    ("hook",    186.62, 193.58, "hook"),
    ("stats_a", 224.22, 229.76, "graphic"),
    ("stats_b", 230.34, 234.58, "graphic"),
    ("elab",    236.06, 250.92, "wide"),
    ("demo_a",  257.02, 258.62, "wide"),
    ("demo_b",  259.04, 263.76, "wide"),
    ("demo_c",  264.30, 265.70, "wide"),
    ("demo_d",  266.98, 271.70, "wide"),
    ("close_a", 367.72, 369.28, "graphic"),
    ("close_b", 369.28, 374.42, "wide"),
]

durs = [e - s for _, s, e, _ in PIECES]
g = [sum(durs[:i]) for i in range(len(PIECES))]  # global start offset of each piece, 1.0x timeline
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


def extract_piece(idx):
    pid, start, end, treatment = PIECES[idx]
    d = end - start
    if treatment == "hook":
        vf = (f"scale=-2:1920,crop=1080:1920:"
              f"x='if(lt(t,{HOOK_SWITCH_T}),{CROP_TIGHT_X},{CROP_WIDE_X})':y=0")
    elif treatment == "wide":
        vf = f"scale=-2:1920,crop=1080:1920:{CROP_WIDE_X}:0"
    else:  # graphic
        vf = GRAPHIC_VF
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
    print(f"  {pid}: {dur(out):.2f}s ({treatment})")
    return out


# Hook word-bursts (top zone, global 0-6.96s) — the opening rhetorical question itself is
# the hook (no separate TTS/preamble); one keyword per burst emphasized in yellow.
HOOK_BURSTS = [
    (0.00, 1.70, "RAISE YOUR HAND IF YOU FEEL", False),
    (1.70, 3.62, "LIKE CLAUDE HAS ALLOWED YOU TO", False),
    (3.62, 4.80, "GO 10X FASTER", True),
    (4.80, 6.96, "THAN A YEAR AGO", False),
]

# Dialogue captions for every other piece (bottom zone), global-timeline offsets.
BODY_SUBS = [
    (G["stats_a"] + 0.00, G["stats_a"] + 2.00, "ABOUT A YEAR AGO,"),
    (G["stats_a"] + 2.00, G["stats_a"] + 3.14, "ON OUR MODEL AT THE TIME - SONNET 3.7,"),
    (G["stats_a"] + 3.14, G["stats_a"] + 5.54, "IT SCORED 62%."),

    (G["stats_b"] + 0.00, G["stats_b"] + 2.02, "TODAY, WITH OPUS 4.7,"),
    (G["stats_b"] + 2.02, G["stats_b"] + 4.24, "IT SCORES 87%."),

    (G["elab"] + 0.00, G["elab"] + 2.36, "THAT'S AN OVER 25% JUMP"),
    (G["elab"] + 2.36, G["elab"] + 4.38, "IN JUST OVER A YEAR."),
    (G["elab"] + 4.38, G["elab"] + 6.14, "TO PUT THIS IN OTHER WORDS,"),
    (G["elab"] + 6.44, G["elab"] + 8.16, "OPUS 4.7 IS MORE THAN"),
    (G["elab"] + 8.16, G["elab"] + 10.14, "3X AS LIKELY TO SUCCEED"),
    (G["elab"] + 10.14, G["elab"] + 12.04, "ON SOME OF THOSE DIFFICULT PRs"),
    (G["elab"] + 12.04, G["elab"] + 13.48, "THAT SONNET 3.7 WAS FAILING"),
    (G["elab"] + 13.48, G["elab"] + 14.86, "ON A YEAR AGO."),

    (G["demo_a"] + 0.00, G["demo_a"] + 1.60, "SO TO MAKE THIS A BIT MORE CONCRETE,"),

    (G["demo_b"] + 0.00, G["demo_b"] + 2.16, "I HAVE A QUICK DEMO HERE"),
    (G["demo_b"] + 2.16, G["demo_b"] + 3.56, "OF THE SAME TASK,"),
    (G["demo_b"] + 3.56, G["demo_b"] + 4.72, "BUT 12 MONTHS APART."),

    (G["demo_c"] + 0.00, G["demo_c"] + 1.40, "SO LET'S GET INTO IT."),

    (G["demo_d"] + 0.00, G["demo_d"] + 1.46, "SO IN THIS EXAMPLE,"),
    (G["demo_d"] + 1.46, G["demo_d"] + 2.36, "WE'RE GOING TO BE"),
    (G["demo_d"] + 2.36, G["demo_d"] + 4.72, "COMPARING SONNET 4 TO OPUS 4.7."),

    (G["close_a"] + 0.00, G["close_a"] + 1.56, "SO IN ADDITION TO THAT BEING"),

    (G["close_b"] + 0.00, G["close_b"] + 0.92, "A BETTER OUTPUT,"),
    (G["close_b"] + 0.92, G["close_b"] + 2.26, "IT ALSO DID IT IN"),
    (G["close_b"] + 2.26, G["close_b"] + 3.30, "LESS LINES OF CODE."),
    (G["close_b"] + 3.30, G["close_b"] + 4.42, "SO IT'S MORE EFFICIENT"),
    (G["close_b"] + 4.42, G["close_b"] + 5.14, "AS WELL."),
]

# data_viz_overlay: our own chart (pipeline/aiwork/make_chart.py), shown during ELAB (the
# only clip that talks through the numbers without a chart already on screen — STATS shows
# the source's own real chart as base footage, so overlaying ours there would be redundant).
CHART_START = G["elab"] + 0.26
CHART_END = G["elab"] + 10.76

# fact_check_callout: names the benchmark. STATS's own chart subtitles "SWE-bench Verified"
# but small; reinforced here in ELAB where the same results are discussed.
FACT_CHECK = "SWE-BENCH VERIFIED - REAL GITHUB CODING TASKS"
FACT_CHECK_START = G["elab"] + 0.0
FACT_CHECK_END = G["elab"] + 8.0

# Persistent headline banner, shown during STATS (top zone, above the bottom-zone dialogue
# captions) — same numbers v1's hook led with, now anchoring the clip that states them.
HEADLINE = "62% -> 88% IN ONE YEAR"  # "->" not "→": HelveticaNeue.ttc has no arrow glyph
HEADLINE_START = G["stats_a"]
HEADLINE_END = G["stats_b"] + 4.24

CTA = "SUBSCRIBE FOR MORE ON BUILDING WITH AI"
CTA_START = TOTAL - 5.0
CTA_END = TOTAL


def render():
    print(f"\n{'='*55}\n  {VID}\n{'='*55}")

    print("  Extracting 10 pieces (per-piece crop/pad treatment)...")
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
    burst_parts = []
    for st, et, txt, emphasize in HOOK_BURSTS:
        color = "yellow" if emphasize else "white"
        burst_parts.append(drawtext(txt, y=160, size=32, color=color,
                                     enable=f"between(t,{st},{et})", box=True))

    sub_parts = []
    for st, et, txt in BODY_SUBS:
        sub_parts.append(drawtext(txt, y="h-200", size=28, color="white",
                                   enable=f"between(t,{st:.2f},{et:.2f})", box=True))

    fact_check_parts = [
        drawtext(FACT_CHECK, y=210, size=22, color="0xB8BCFF",
                  enable=f"between(t,{FACT_CHECK_START:.2f},{FACT_CHECK_END:.2f})",
                  font=FONT_BOLD),
    ]

    headline_parts = [
        drawtext(HEADLINE, y=60, size=36, color="yellow", font=FONT_BOLD,
                  enable=f"between(t,{HEADLINE_START:.2f},{HEADLINE_END:.2f})"),
    ]

    cta_parts = [
        drawtext(CTA, y="h-70", size=22, color="white",
                  enable=f"between(t,{CTA_START:.2f},{CTA_END:.2f})"),
    ]

    progress_bar = f"drawbox=x=0:y=ih-4:w=iw*(t/{TOTAL:.3f}):h=4:color=0x4F46E5:t=fill"

    fc_parts = ["[1:v]scale=950:-2[chart]"]
    fc_parts.append(
        f"[0:v][chart]overlay=x=(W-w)/2:y=780"
        f":enable='between(t,{CHART_START:.2f},{CHART_END:.2f})'[withchart]"
    )
    all_text_parts = (burst_parts + sub_parts + fact_check_parts + headline_parts
                       + cta_parts + [progress_bar])
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
    print("="*60 + "\n  WORKING WITH AI — CAPABILITY CURVE v2 (Multi-Clip Mashup)\n" + "="*60)
    ok = render()
    print(f"\n{'='*60}\n  {'OK' if ok else 'FAIL'}\n{'='*60}")
    shutil.rmtree(T, ignore_errors=True)


if __name__ == "__main__":
    main()
