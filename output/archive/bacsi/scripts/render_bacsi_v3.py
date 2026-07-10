#!/usr/bin/env python3
"""Render 3 Bác sĩ Hải Shorts v3 — CORRECT subtitle sync from transcript."""
import subprocess, shutil, json
from pathlib import Path

SRC = Path("output/zSD-o37SUrk/zSD-o37SUrk_1080p.mp4")
P = Path("output/pexels")
O = Path("output/shorts/bacsi")
T = Path("output/shorts/temp")
FONT = "/System/Library/Fonts/Helvetica.ttc"
O.mkdir(parents=True, exist_ok=True); T.mkdir(parents=True, exist_ok=True)

PEXELS = {
    "bedroom": P/"bedroom_7505656.mp4",
    "phone": P/"phone_hand_9787494.mp4",
    "clock": P/"clock_night_7034348.mp4",
    "sleepless": P/"sleepless_8410597.mp4",
    "sleepwell": P/"sleep_well_6918276.mp4",
    "breathing": P/"breathing_6189263.mp4",
    "ac": P/"ac_cool_9346239.mp4",
}

def dur(p):
    if not p.exists(): return 0.0
    r = subprocess.run(["ffprobe","-v","quiet","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(p)],capture_output=True,text=True,timeout=15)
    return float(r.stdout.strip()) if r.stdout.strip() else 0.0

def make_pexels(key, length, out):
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2,fps=30"
    subprocess.run(["ffmpeg","-y","-i",str(PEXELS[key]),"-t",str(length),"-vf",vf,"-c:v","libx264","-crf","18","-preset","fast","-pix_fmt","yuv420p","-r","30","-an",str(out)],capture_output=True,timeout=60)

TRANS = json.loads(Path("output/zSD-o37SUrk/transcript.json").read_text())["segments"]
def get_subs(src_start, src_end):
    """Return [(offset_s, offset_e, text)] relative to src_start."""
    out = []
    for s in TRANS:
        if s["start"] >= src_start and s["end"] <= src_end:
            st = round(s["start"] - src_start, 1)
            en = round(s["end"] - src_start, 1)
            txt = s["text"].strip()
            if txt: out.append((st, en, txt))
    return out

# === 3 VARIANTS — Timestamps EXACTLY matching storyboard_bacsi.md ===
VARIANTS = [
    {"id": "V1_dem", "src_start": 0.0, "src_end": 56.3, "hook": "TẠI SAO BẠN HAY THỨC DẬY GIỮA ĐÊM?", "cta": "FOLLOW ĐỂ NGỦ NGON HƠN!", "pexels": [(10,3,"bedroom"),(30,3,"ac"),(44,3,"sleepwell")]},
    {"id": "V2_dienthoai", "src_start": 217.4, "src_end": 275.0, "hook": "ĐỪNG CẦM ĐIỆN THOẠI KHI MẤT NGỦ!", "cta": "FOLLOW ĐỂ NGỦ NGON!", "pexels": [(8,3,"phone"),(25,3,"clock"),(40,3,"sleepless")]},
    {"id": "V3_tho178", "src_start": 289.8, "src_end": 348.9, "hook": "KỸ THUẬT THỞ 1-7-8 NGỦ NGAY LẬP TỨC", "cta": "FOLLOW ĐỂ THỬ KỸ THUẬT NÀY!", "pexels": [(7,3,"breathing"),(25,3,"sleepwell"),(45,3,"bedroom")]},
]

def render(v):
    vid = v["id"]; print(f"\nRENDER: {vid}")
    d = T / vid; d.mkdir(parents=True, exist_ok=True)
    raw = d / "raw.mp4"
    src_dur = v["src_end"] - v["src_start"]
    subprocess.run(["ffmpeg","-y","-ss",str(v["src_start"]),"-i",str(SRC),"-t",str(src_dur),
           "-vf","scale=-2:1920,crop=1080:1920:(in_w-1080)/2:0,fps=30",
           "-c:v","libx264","-crf","18","-preset","fast","-pix_fmt","yuv420p","-r","30",
           "-c:a","aac","-b:a","192k","-ar","48000","-ac","2",str(raw)],check=True,capture_output=True)
    td = dur(raw); cs = max(td-5,0)
    
    # Pexels overlays
    pex_clips = []
    for start, pdur, key in v["pexels"]:
        pc = d / f"pex_{key}.mp4"; make_pexels(key, pdur, pc); pex_clips.append((start, pdur, key, pc))
    
    # Verbatim subs from transcript — MATCHES storyboard_bacsi.md
    subs = get_subs(v["src_start"], v["src_end"])
    print(f"  Sub lines: {len(subs)}, dur: {td:.1f}s")

    hook_esc = v["hook"].replace(":","\\:").replace("'","\u2019")
    cta_esc = v["cta"].replace(":","\\:").replace("'","\u2019")
    
    fc_parts = []; inputs = ["-i",str(raw)]; idx = 1
    for s,pd,key,pc in pex_clips:
        inputs += ["-i",str(pc)]; fc_parts.append(f"[{idx}:v]scale=1080:1920,setpts=PTS-STARTPTS[pex_{key}]"); idx+=1
    prev = "0:v"; cnt=0
    for s,pd,key,pc in pex_clips:
        cnt+=1; tag=f"pv{cnt}"; end=s+pd
        fc_parts.append(f"[{prev}][pex_{key}]overlay=x=0:y=0:enable='between(t,{s},{end})'[{tag}]"); prev=tag
    sub_parts = []
    for st,en,txt in subs:
        te = txt.replace("\\","\\\\").replace(":","\\:").replace("'","\u2019")
        sub_parts.append(f"drawtext=text='{te}':fontfile={FONT}:fontsize=28:fontcolor=white:borderw=3:bordercolor=black@0.8:x=(w-text_w)/2:y=h-200:enable='between(t,{st},{en})'")
    cnt+=1; final="final"
    fc_parts.append(f"[{prev}]{','.join(sub_parts)},drawtext=text='{hook_esc}':fontfile={FONT}:fontsize=32:fontcolor=yellow:borderw=3:bordercolor=black@0.8:x=(w-text_w)/2:y=100:enable='between(t,0,5)',drawtext=text='{cta_esc}':fontfile={FONT}:fontsize=22:fontcolor=white:borderw=2:bordercolor=black@0.8:x=(w-text_w)/2:y=h-70:enable='between(t,{cs:.1f},{td:.1f})',drawbox=x=0:y=ih-4:w=iw*t/{td:.1f}:h=4:color=0xFF4500:t=fill[{final}]")
    fc = ";".join(fc_parts)
    fv = d/"fv.mp4"
    subprocess.run(["ffmpeg","-y"]+inputs+["-filter_complex",fc,"-map",f"[{final}]","-c:v","libx264","-crf","20","-preset","fast","-an",str(fv)],check=True,capture_output=True)
    out = O/f"{vid}.mp4"
    subprocess.run(["ffmpeg","-y","-i",str(fv),"-i",str(raw),"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest",str(out)],check=True,capture_output=True)
    print(f"  OK {out.name}")
    return True

results = [render(v) for v in VARIANTS]
shutil.rmtree(T,ignore_errors=True)
print(f"\nDone: {sum(results)}/3 OK")
