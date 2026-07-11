#!/usr/bin/env python3
"""Working With AI — Capability Curve v1: first video for the AI-education niche.

Clip Curation Edit (Video Type #7) of tP4MGcJ80Y0 ("The capability curve", Anthropic's
own Claude YouTube channel) — a per-video override of ADR-0020's zero-footage default,
decided via grilling and recorded in ADR-0021.

Structure mirrors pipeline/bacsihai/render_bacsihai_v5.py (config -> content data ->
helpers -> extract_segment -> render -> main), with two deltas:
- mix_commentary_audio(): layers a short TTS commentary line over the ORIGINAL,
  untouched, contiguous source audio via gain-ducking + amix (ADR-0021), rather than
  just re-muxing the raw segment audio directly.
- Two value-adds for the Transformative Gate (ADR-0007): data_viz_overlay (a chart PNG
  built from the real numbers on Alex Albert's own slide, see pipeline/aiwork/make_chart.py)
  + fact_check_callout (names/explains SWE-bench Verified, which this chosen span's
  audio never names by itself since the segment starts after that line).
"""
import subprocess, shutil
from pathlib import Path

SRC = Path("output/projects/aiwork/source/tP4MGcJ80Y0_1080p.webm")
COMMENTARY_WAV = Path("output/projects/aiwork/source/commentary_v1.wav")
CHART_PNG = Path("output/projects/aiwork/final/assets/capability_curve_chart.png")
O = Path("output/projects/aiwork/final")
T = Path("output/projects/aiwork/clips/temp_v1")
FONT = "/System/Library/Fonts/Helvetica.ttc"
FONT_BOLD = "/System/Library/Fonts/HelveticaNeue.ttc"
# Presenter stands right-of-center in this wide stage shot (verified visually via test
# crops at t=245s, see docs/production/aiwork-v1-capability-curve.md) — a naive true-center
# crop lands between the slide and the presenter and frames neither.
CROP = "scale=-2:1920,crop=1080:1920:1650:0"

O.mkdir(parents=True, exist_ok=True)
(O / "assets").mkdir(parents=True, exist_ok=True)
T.mkdir(parents=True, exist_ok=True)

VID = "capability_curve_v1"
# SRC_START was originally 234.90 (start of a natural audio pause) but frame-inspection
# (docs/production/aiwork-v1-capability-curve.md) showed the camera is still on the
# faceless chart-closeup shot there, with a crossfade to the presenter only completing at
# ~236.0 — moved to 236.0 to satisfy the Hook Gate's frame-0 face/action requirement
# (ADR-0017), which costs the natural pre-speech pause (see mix_commentary_audio below).
SRC_START = 236.0
SRC_END = 282.0

HOOK = "62% -> 88% IN ONE YEAR"  # "->" not "→": HelveticaNeue.ttc has no arrow glyph (renders as tofu)
FACT_CHECK = "SWE-BENCH VERIFIED — REAL GITHUB CODING TASKS"
CTA = "SUBSCRIBE FOR MORE ON BUILDING WITH AI"

# Hook word-bursts (t=0-4.44s), timestamps from the source's real mlx_whisper word output
# (abs time - SRC_START), covering the first spoken payoff line of our chosen span. The
# TTS commentary (see mix_commentary_audio) plays under this without its own caption —
# real speech now starts at offset ~0.06s (no pre-roll pause left after the SRC_START
# move above), so a separate commentary caption would collide with this one on screen.
HOOK_BURSTS = [
    (0.00, 2.42, "THAT'S AN OVER 25% JUMP", True),
    (2.42, 4.44, "IN JUST OVER A YEAR.", False),
]

# Body captions (t=4.44s onward), tightened to ~1.5-3s blocks per ADR-0018, aligned to
# the source's real sentence/word boundaries (abs time - SRC_START). "three times" ->
# "3x" is a caption-only stylization (shorter, punchier on-screen), not a transcript error.
BODY_SUBS = [
    (4.44, 6.20, "To put this in other words,"),
    (6.50, 9.64, "Opus 4.7 is more than 3x as likely"),
    (9.64, 12.10, "to succeed on some of those difficult PRs"),
    (12.10, 14.92, "that Sonnet 3.7 was failing on a year ago."),
    (17.20, 19.20, "Now, numbers are great,"),
    (19.30, 20.70, "but examples are even better."),
    (21.02, 22.62, "So to make this a bit more concrete,"),
    (23.04, 24.30, "I have a quick demo here"),
    (25.20, 27.76, "of the same task, but 12 months apart."),
    (28.30, 29.70, "So let's get into it."),
    (30.98, 32.44, "So in this example,"),
    (33.34, 35.70, "we're comparing Sonnet 4 to Opus 4.7."),
    (36.92, 39.48, "And we're going to give them the same task."),
    (40.60, 44.48, "Oh, let's go back here and get this demo working."),
]

# data_viz_overlay: our own chart (pipeline/aiwork/make_chart.py), not the source's slide —
# covers the 62.3%->87.6% comparison, which this chosen span's audio only ever refers to
# abstractly ("an over 25% jump", "three times as likely"), never restating the raw numbers.
CHART_START = 0.0
CHART_END = 15.5

# fact_check_callout: names the benchmark, since "SWE-bench Verified" itself was said
# before our chosen span started (at t=213-217s of the source, outside SRC_START/SRC_END).
FACT_CHECK_START = 0.0
FACT_CHECK_END = 8.0


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
    # expansion=none: drawtext's default text-expansion parser treats a bare '%' as a
    # template escape (e.g. '%{pts}') and silently drops the rest of the string otherwise
    # (ffmpeg logs "Stray %" — found while reviewing this render's first pass, since our
    # captions contain real percentages like "25%"). We never use %{...} expansion, so
    # disabling it outright is simpler and more robust than escaping every '%' as '%%'.
    parts = [f"drawtext=text='{t}'", f"fontfile={font}", f"fontsize={size}",
              f"fontcolor={color}", "borderw=3", "bordercolor=black@0.8",
              f"x={x}", f"y={y}", "expansion=none"]
    if box:
        parts += ["box=1", "boxcolor=black@0.55", "boxborderw=10"]
    if enable:
        parts.append(f"enable='{enable}'")
    return ":".join(parts)


def extract_segment(src, start, end, out):
    """Extract the ONE contiguous segment (ADR-0013), crop to the presenter (see CROP
    comment above), add a gentle zoompan push-in — this is real edited conference footage
    (already cuts between shots, unlike bacsihai's static livestream camera), but our own
    fixed-position crop still benefits from continuous motion per ADR-0016/0018."""
    duration = end - start
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start), "-i", str(src),
        "-t", str(duration),
        "-vf", f"{CROP},zoompan=z='min(zoom+0.0004,1.06)':d=1:s=1080x1920:fps=30",
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        str(out)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        print(f"  EXTRACT ERROR: {r.stderr[-500:]}")
    return out


def mix_commentary_audio(raw, commentary_wav, out, commentary_start=0.0, duck_level=0.15):
    """Layer the TTS commentary over the ORIGINAL, untouched, contiguous source audio
    (ADR-0021). Original audio is gain-ducked (volume envelope only, no cuts/gaps) during
    the commentary span, then returns to full volume — the only audio edit, consistent
    with ADR-0013/ADR-0021's reading of 'immutable' as no splices, not no gain automation.
    Most of the commentary (0-1.16s) actually lands in a natural pause in the real audio
    (234.58-236.06s of the source); only the last ~0.84s overlaps real speech, so the duck
    is brief."""
    comm_dur = dur(commentary_wav)
    duck_end = commentary_start + comm_dur
    delay_ms = int(commentary_start * 1000)
    filt = (
        f"[0:a]volume='if(between(t,{commentary_start},{duck_end}),{duck_level},1)':eval=frame[orig];"
        f"[1:a]adelay={delay_ms}|{delay_ms}[comm];"
        f"[orig][comm]amix=inputs=2:duration=first:dropout_transition=0.3,"
        f"dynaudnorm=f=150:g=15[aout]"
    )
    cmd = ["ffmpeg", "-y", "-i", str(raw), "-i", str(commentary_wav),
           "-filter_complex", filt, "-map", "[aout]",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print(f"  MIX ERROR: {r.stderr[-500:]}")
    return out


def render():
    print(f"\n{'='*55}\n  {VID}\n{'='*55}")
    d = T

    print("  Extracting contiguous segment (with zoompan motion)...")
    raw = d / "raw.mp4"
    extract_segment(SRC, SRC_START, SRC_END, raw)
    raw_dur = dur(raw)
    print(f"  Segment: {raw_dur:.2f}s (VO continuous)")

    print("  Mixing TTS commentary over original audio...")
    mixed_audio = d / "mixed_audio.m4a"
    mix_commentary_audio(raw, COMMENTARY_WAV, mixed_audio)

    # Hook word-bursts (t=0-5.54s), one keyword per burst emphasized in yellow
    burst_parts = []
    for st, et, txt, emphasize in HOOK_BURSTS:
        color = "yellow" if emphasize else "white"
        burst_parts.append(drawtext(txt, y=160, size=34, color=color,
                                     enable=f"between(t,{st},{et})", box=True))

    # Body captions (t=5.54s onward)
    sub_parts = []
    for st, et, txt in BODY_SUBS:
        sub_parts.append(drawtext(txt, y="h-200", size=28, color="white",
                                   enable=f"between(t,{st},{et})", box=True))

    fact_check_parts = [
        drawtext(FACT_CHECK, y=210, size=22, color="0xB8BCFF",
                  enable=f"between(t,{FACT_CHECK_START},{FACT_CHECK_END})", font=FONT_BOLD),
    ]

    fc_parts = ["[1:v]scale=950:-2[chart]"]
    chart_overlay = (
        f"[0:v][chart]overlay=x=(W-w)/2:y=780"
        f":enable='between(t,{CHART_START},{CHART_END})'[withchart]"
    )
    fc_parts.append(chart_overlay)

    final_tag = "final"
    all_text_parts = burst_parts + sub_parts + fact_check_parts + [
        drawtext(HOOK, y=90, size=36, color="yellow",
                 enable="between(t,0,6)", font=FONT_BOLD),
        drawtext(CTA, y="h-70", size=22, color="white",
                 enable=f"between(t,{max(raw_dur-5,0):.1f},{raw_dur:.1f})"),
        f"drawbox=x=0:y=ih-4:w=iw*t/{raw_dur:.1f}:h=4:color=0x4F46E5:t=fill",
    ]
    fc_parts.append(f"[withchart]{','.join(all_text_parts)}[{final_tag}]")

    fc = ";".join(fc_parts)

    print("  Applying overlays...")
    fv = d / "fv.mp4"
    cmd = ["ffmpeg", "-y", "-i", str(raw), "-i", str(CHART_PNG),
           "-filter_complex", fc,
           "-map", f"[{final_tag}]",
           "-c:v", "libx264", "-crf", "20", "-preset", "fast",
           "-an", str(fv)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        err_lines = [l for l in r.stderr.split("\n")
                     if any(x in l.lower() for x in ["error", "invalid", "no such"])]
        err = err_lines[0] if err_lines else r.stderr[-500:]
        print(f"  FILTER ERROR: {err[:500]}")
        return False

    out = O / f"{VID}.mp4"
    cmd = ["ffmpeg", "-y", "-i", str(fv), "-i", str(mixed_audio),
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
         "-show_entries", "stream=index,codec_type", "-of", "csv=p=0", str(out)],
        capture_output=True, text=True)
    a_lines = [l for l in a_check.stdout.strip().split("\n") if l]
    if len(a_lines) != 1:
        print(f"  WARNING: expected exactly 1 audio stream, found {len(a_lines)}: {a_lines}")
        return False
    print(f"  Audio: OK (1 stream)")
    return True


def main():
    print("="*60 + "\n  WORKING WITH AI — CAPABILITY CURVE v1\n" + "="*60)
    ok = render()
    print(f"\n{'='*60}\n  {'OK' if ok else 'FAIL'}\n{'='*60}")
    shutil.rmtree(T, ignore_errors=True)


if __name__ == "__main__":
    main()
