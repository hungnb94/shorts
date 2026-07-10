#!/usr/bin/env python3
"""Render 3 Giannis Shorts v1: Contiguous VO + Pexels overlays + drawtext."""
import subprocess, shutil
from pathlib import Path

SRC = Path("output/NSeL8fFz5hw/NSeL8fFz5hw_2160p.mp4")
P = Path("output/pexels")
O = Path("output/shorts/giannis")
T = Path("output/shorts/temp")
EMOJI_DIR = Path("output/emoji_processed")
FONT = "/System/Library/Fonts/Helvetica.ttc"
O.mkdir(parents=True, exist_ok=True); T.mkdir(parents=True, exist_ok=True)

PEXELS_MAP = {
    # V1
    "ferrari": P/"ferrari_red_13358188.mp4",
    "watch": P/"luxury_watch_11267671.mp4",
    "art": P/"art_gallery_8348366.mp4",
    "house": P/"real_estate_37694695.mp4",
    "race": P/"race_track_37264419.mp4",
    # V2
    "stadium": P/"empty_stadium_37099690.mp4",
    "luxcar": P/"luxury_car_drive_33313836.mp4",
    "mansion": P/"mansion_exterior_27066154.mp4",
    "chart": P/"stock_chart_8480284.mp4",
    "reading": P/"quiet_reading_6448179.mp4",
    # V3
    "office": P/"office_meeting_7845427.mp4",
    "contract": P/"contract_signing_7981954.mp4",
    "suit": P/"suited_businessman_18514374.mp4",
    "books": P/"books_finance_7710748.mp4",
}

def dur(p):
    if not p.exists(): return 0.0
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(p)], capture_output=True, text=True, timeout=15)
    return float(r.stdout.strip()) if r.stdout.strip() else 0.0

def make_pexels_clip(key, duration, out):
    inp = PEXELS_MAP[key]
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2,fps=30"
    cmd = ["ffmpeg", "-y", "-i", str(inp), "-t", str(duration), "-vf", vf, "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p", "-r", "30", "-an", str(out)]
    subprocess.run(cmd, capture_output=True, text=True, timeout=60)

# --- 3 VARIANTS (Timestamps from approved storyboard) ---
VARIANTS = [
    {"id": "V1_ferrari_1.1M", "src_start": 413.5, "src_end": 470.5, "hook": "A FERRARI COSTS $1.1M", "cta": "FOLLOW FOR MORE MONEY SECRETS", "pexels": [(1, 2, "watch"), (5, 2, "art"), (8, 2, "house"), (24, 2, "ferrari"), (35, 2, "race")], "subs": [(0, 5, "Price is what you pay. Value is what you get."), (5, 12, "Everything I pay must return value to me."), (12, 22, "1M in the market = +100K a year at 9 to 10%"), (22, 30, "So a 1M Ferrari is really a 1.1M Ferrari"), (30, 42, "Opportunity cost. The money I could have made."), (42, 50, "I started from minus 100. Not zero. Minus 100."), (50, 57, "Last in the race. Then first place.")]},
    {"id": "V2_60pct_broke", "src_start": 623.2, "src_end": 675.0, "hook": "60% OF ATHLETES GO BROKE", "cta": "BUILD WEALTH. NOT IMAGE.", "pexels": [(1, 2, "stadium"), (12, 2, "luxcar"), (16, 2, "mansion"), (36, 2, "chart")], "subs": [(0, 4, "Six years after you retire, people go broke."), (4, 10, "60 percent of athletes. 60 percent."), (10, 18, "They cannot maintain the same lifestyle."), (18, 25, "Income stops. Spending does not."), (25, 35, "Rich is what you see. Wealth is what you don't."), (35, 45, "Extreme wealth is what you haven't spent."), (45, 52, "They keep investing. That is the game.")]},
    {"id": "V3_lawyer_agent", "src_start": 347.5, "src_end": 404.5, "hook": "NEVER LET YOUR LAWYER KNOW YOUR AGENT", "cta": "EDUCATE YOURSELF. FOLLOW FOR MORE.", "pexels": [(3, 2, "suit"), (8, 2, "office"), (28, 2, "contract"), (40, 2, "books")], "subs": [(0, 5, "They provide you a lawyer, agent, financial advisor."), (5, 12, "Oh yeah, these are your people. Trust them."), (12, 18, "If you do not learn, you will always need them."), (18, 28, "Do not let your lawyer, agent, advisor know one another."), (28, 35, "Never. They should never be boys."), (35, 45, "They can keep one another accountable."), (45, 57, "In the contract he put X Y Z. He benefits, not you.")]}
]

def render(v):
    vid = v["id"]; print(f"\n{'='*60}\n  RENDER: {vid}\n{'='*60}")
    d = T / vid; d.mkdir(parents=True, exist_ok=True)
    
    raw = d / "raw.mp4"
    # Center-crop source to 1080x1920 (9:16)
    cmd = ["ffmpeg", "-y", "-ss", str(v["src_start"]), "-i", str(SRC), "-t", str(v["src_end"]-v["src_start"]), "-vf", "scale=-2:1920,crop=1080:1920:(in_w-1080)/2:0,fps=30", "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(raw)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0: print(f"  RAW ERROR: {r.stderr[-200:]}"); return False
    
    raw_dur = dur(raw)
    print(f"  Raw: {raw_dur:.1f}s")
    td = raw_dur; cs = max(td - 5, 0)
    
    # Prepare pexels clips
    pexels_clips = []
    for start, pdur, key in v["pexels"]:
        pc = d / f"pex_{key}.mp4"; make_pexels_clip(key, pdur, pc); pexels_clips.append((start, pdur, key, pc))
    
    hook_esc = v["hook"].replace(":", "\\:").replace("'", "\u2019")
    cta_esc = v["cta"].replace(":", "\\:").replace("'", "\u2019")
    
    fc_parts = []; inputs = ["-i", str(raw)]; idx = 1
    for s, pd, key, pc in pexels_clips:
        inputs += ["-i", str(pc)]
        fc_parts.append(f"[{idx}:v]scale=1080:1920,setpts=PTS-STARTPTS[pex_{key}]"); idx += 1
    
    prev = "0:v"; cnt = 0
    for s, pd, key, pc in pexels_clips:
        cnt += 1; tag = f"pv{cnt}"; end = s + pd
        fc_parts.append(f"[{prev}][pex_{key}]overlay=x=0:y=0:enable='between(t,{s},{end})'[{tag}]"); prev = tag
    
    sub_parts = []
    for s, e, txt in v["subs"]:
        te = txt.replace("\\","\\\\").replace(":","\\:").replace("'","\u2019")
        sub_parts.append(f"drawtext=text='{te}':fontfile={FONT}:fontsize=28:fontcolor=white:borderw=3:bordercolor=black@0.8:x=(w-text_w)/2:y=h-200:enable='between(t,{s},{e})'")
    
    cnt += 1; final = "final"
    fc_parts.append(f"[{prev}]{','.join(sub_parts)},drawtext=text='{hook_esc}':fontfile={FONT}:fontsize=32:fontcolor=yellow:borderw=3:bordercolor=black@0.8:x=(w-text_w)/2:y=100:enable='between(t,0,5)',drawtext=text='{cta_esc}':fontfile={FONT}:fontsize=22:fontcolor=white:borderw=2:bordercolor=black@0.8:x=(w-text_w)/2:y=h-70:enable='between(t,{cs:.1f},{td:.1f})',drawbox=x=0:y=ih-4:w=iw*t/{td:.1f}:h=4:color=0xFF4500:t=fill[{final}]")
    fc = ";".join(fc_parts)
    
    fv = d / "fv.mp4"
    cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", fc, "-map", f"[{final}]", "-c:v", "libx264", "-crf", "20", "-preset", "fast", "-an", str(fv)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0: print(f"  FILTER ERROR: {r.stderr[-200:]}"); return False
    
    out = O / f"{vid}.mp4"
    cmd = ["ffmpeg", "-y", "-i", str(fv), "-i", str(raw), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0: print(f"  MUX ERROR: {r.stderr[-200:]}"); return False
    
    od = dur(out); mb = out.stat().st_size / 1048576
    print(f"  ✓ {out.name}: {od:.1f}s, {mb:.1f}MB")
    return True

def main():
    print("="*60 + "\n  GIANNIS — 3 SHORTS v1 (Contiguous VO + Pexels)\n" + "="*60)
    results = [render(v) for v in VARIANTS]
    print(f"\n{'='*60}\n  Results: {sum(results)}/{len(results)} OK\n{'='*60}")
    for v, ok in zip(VARIANTS, results):
        p = O / f"{v['id']}.mp4"
        d_ = dur(p) if ok else 0
        mb_ = p.stat().st_size/1048576 if ok else 0
        print(f"  {'OK' if ok else 'FAIL'} {v['id']}: {d_:.1f}s, {mb_:.1f}MB")
    shutil.rmtree(T, ignore_errors=True)

if __name__ == "__main__":
    main()
