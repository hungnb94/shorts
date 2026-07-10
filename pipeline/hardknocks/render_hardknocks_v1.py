#!/usr/bin/env python3
"""Render 1 Short from KxoKCNCLOss (School of Hard Knocks — lawnmower-to-empire story).

Applies the hook playbook from docs/research/hook-benchmarks-2026-07/REPORT.md +
ADR-0017 (Hook-Window Rule) + ADR-0018 (caption sync/cadence):
- Cold open on a real handshake/face, no title card.
- Source's own burned-in word-synced captions kept as-is (already compliant).
- Added value-adds (Transformative Gate, ADR-0007): data_viz_overlay (stat cards) +
  fact_check_callout (Berkshire Hathaway clarification) = 2 value-adds.
- Commentary track: hook-framing text top of clip 1, "LESSON" tag on clip 5, CTA on clip 6.
- Each cut < 15s; total used footage ~51s out of a 1391s source (<< 50%).
"""
import subprocess
from pathlib import Path

SRC = Path("output/KxoKCNCLOss/source_raw.webm")  # local timeline starts at abs t=573.0
T = Path("output/KxoKCNCLOss/temp")
O = Path("output/shorts/hardknocks")
T.mkdir(parents=True, exist_ok=True)
O.mkdir(parents=True, exist_ok=True)
FONT = "/System/Library/Fonts/Helvetica.ttc"
FONT_BOLD = "/System/Library/Fonts/HelveticaNeue.ttc"

CROP = "scale=-2:1920,crop=1080:1920:(in_w-1080)/2:0"

def esc(s):
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’")

# (id, local_start, local_end) — local = abs_source_time - 573.0
CLIPS = [
    ("c1_hook",       1.4,   8.9),
    ("c2_rise",       9.0,  18.7),
    ("c3_apartments", 18.84, 23.46),
    ("c4_sale",       28.0,  32.3),
    ("c5_wisdom",     87.5, 101.48),
    ("c6_legacy",    104.1, 115.32),
]

# cumulative global start offset in the FINAL edited video, computed from durations
durs = [e - s for _, s, e in CLIPS]
g_starts = [sum(durs[:i]) for i in range(len(durs))]
TOTAL = sum(durs)
print("Clip durations:", [round(d, 2) for d in durs], "TOTAL:", round(TOTAL, 2))


def dur(p):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                         "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
                        capture_output=True, text=True, timeout=15)
    return float(r.stdout.strip()) if r.stdout.strip() else 0.0


def drawtext(text, y, size=34, color="yellow", enable=None, box=True, x="(w-text_w)/2"):
    t = esc(text)
    parts = [f"drawtext=text='{t}'", f"fontfile={FONT_BOLD}", f"fontsize={size}",
              f"fontcolor={color}", "borderw=4", "bordercolor=black@0.9",
              f"x={x}", f"y={y}"]
    if box:
        parts += ["box=1", "boxcolor=black@0.55", "boxborderw=14"]
    if enable:
        parts.append(f"enable='{enable}'")
    return ":".join(parts)


def progress_bar(clip_idx):
    gs = g_starts[clip_idx]
    return f"drawbox=x=0:y=ih-6:w=iw*(({gs:.3f}+t)/{TOTAL:.3f}):h=6:color=0xFFD400:t=fill"


def render_clip(idx):
    cid, s, e = CLIPS[idx]
    d = e - s
    raw = T / f"{cid}_raw.mp4"
    cmd = ["ffmpeg", "-y", "-ss", str(s), "-i", str(SRC), "-t", str(d),
           "-vf", f"{CROP},zoompan=z='min(zoom+0.0006,1.08)':d=1:s=1080x1920:fps=30",
           "-c:v", "libx264", "-crf", "17", "-preset", "fast", "-pix_fmt", "yuv420p",
           "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
           str(raw)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        print(f"  RAW ERROR ({cid}): {r.stderr[-400:]}")
        return None
    print(f"  {cid}: raw {dur(raw):.2f}s")

    fc = []
    if idx == 0:
        fc.append(drawtext("FROM A LAWNMOWER... TO A REAL ESTATE EMPIRE", y=90, size=40,
                            color="yellow"))
    if idx == 2:
        # data_viz_overlay: apartments stat card — kept in the TOP zone, clear of the
        # source's own bottom-of-frame captions (which occasionally render emphasized
        # numbers extra-large at the bottom — colliding with anything placed at h-*).
        fc.append(drawtext("2,600 APARTMENTS", y=90, size=50, color="white",
                            enable=f"between(t,{0.4},{d:.2f})", box=True))
        # fact_check_callout: clarify Berkshire Hathaway, stacked below the stat card
        fc.append(drawtext("FACT CHECK: Berkshire Hathaway = Warren Buffett's company",
                            y=190, size=26, color="0x7CFC00",
                            enable=f"between(t,{d - 2.4:.2f},{d:.2f})"))
    if idx == 3:
        fc.append(drawtext("$10,000,000 SALE", y=90, size=50, color="white",
                            enable=f"between(t,{1.1},{d:.2f})"))
    if idx == 4:
        fc.append(drawtext("LESSON", y=90, size=32, color="yellow",
                            enable=f"between(t,0,{d:.2f})"))
    if idx == 5:
        fc.append(drawtext("$10M+ DONATED TO CHARITY", y=90, size=44, color="white",
                            enable=f"between(t,{6.6},{9.6})"))
        fc.append(drawtext("68 YEARS OLD", y=90, size=54, color="white",
                            enable=f"between(t,{10.0},{d:.2f})"))
        # CTA overlaps in time with the stat cards above, so it gets its own line below them
        fc.append(drawtext("CASH FLOW > NET WORTH — REMEMBER THIS", y=200, size=30,
                            color="yellow", enable=f"between(t,{d - 5:.2f},{d:.2f})"))

    fc.append(progress_bar(idx))
    vf = ",".join(fc)

    out = T / f"{cid}_final.mp4"
    cmd2 = ["ffmpeg", "-y", "-i", str(raw), "-vf", vf,
            "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
            "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            str(out)]
    r = subprocess.run(cmd2, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        print(f"  OVERLAY ERROR ({cid}): {r.stderr[-400:]}")
        return None
    print(f"  {cid}: final {dur(out):.2f}s")
    return out


def main():
    outputs = []
    for i in range(len(CLIPS)):
        o = render_clip(i)
        if o is None:
            print("ABORT: a clip failed to render")
            return
        outputs.append(o)

    concat_list = T / "concat_list.txt"
    concat_list.write_text("\n".join(f"file '{p.resolve()}'" for p in outputs))

    final = O / "hardknocks_lawnmower_v1.mp4"
    cmd3 = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-c", "copy", str(final)]
    r = subprocess.run(cmd3, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print(f"CONCAT ERROR: {r.stderr[-500:]}")
        return
    print(f"\n=> {final}: {dur(final):.2f}s, {final.stat().st_size/1048576:.1f}MB")


if __name__ == "__main__":
    main()
