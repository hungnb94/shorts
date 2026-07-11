#!/usr/bin/env python3
"""
Bac si Hai — 3 Shorts v4: ONE contiguous source segment per video.
VO never stops. Pexels = overlay only. No cutting mid-sentence.
"""
import subprocess, shutil
from pathlib import Path

SRC = Path("output/bacsihai_fasting/8vM7rPWzTlI_1080p.mp4")
P = Path("output/pexels")
O = Path("output/shorts/bacsihai")
T = Path("output/shorts/temp")
EMOJI_DIR = Path("output/emoji_processed")
FONT = "/System/Library/Fonts/Helvetica.ttc"

O.mkdir(parents=True, exist_ok=True)
T.mkdir(parents=True, exist_ok=True)

PEXELS_MAP = {
    "scale": P/"scale_7802051.mp4", "candy": P/"candy_unwrap_6605707.mp4",
    "butter_coffee": P/"butter_coffee_8106308.mp4", "sugar_cube": P/"sugar_cube_7628879.mp4",
    "cookies": P/"cookies_office_6430765.mp4",
    "hungry_tired": P/"hungry_tired_7214704.mp4", "fridge_night": P/"fridge_night_5418706.mp4",
    "small_portion": P/"small_portion_6645820.mp4", "healthy_meal": P/"healthy_meal_5961891.mp4",
    "dizzy": P/"dizzy_headache_8555748.mp4", "drinking_water": P/"drinking_water_19697686.mp4",
    "sea_salt": P/"sea_salt_7601298.mp4", "avocado": P/"avocado_7267565.mp4",
    "bone_broth": P/"bone_broth_36886085.mp4",
}


def dur(p):
    if not p.exists():
        return 0.0
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
        capture_output=True, text=True, timeout=15)
    return float(r.stdout.strip()) if r.stdout.strip() else 0.0


def extract_segment(src, start, end, out):
    """Extract a contiguous segment from source, center-crop to 1080x1920."""
    duration = end - start
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start), "-i", str(src),
        "-t", str(duration),
        "-vf", "scale=-2:1920,crop=1080:1920:(in_w-1080)/2:0,fps=30",
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        str(out)
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return out


def make_pexels_clip(key, duration, out):
    """Trim Pexels clip to duration, scale to 1080x1920, no audio."""
    inp = PEXELS_MAP[key]
    vf = ("scale=1080:1920:force_original_aspect_ratio=increase,"
          "crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2,fps=30")
    cmd = ["ffmpeg", "-y", "-i", str(inp), "-t", str(duration),
           "-vf", vf,
           "-c:v", "libx264", "-crf", "18", "-preset", "fast",
           "-pix_fmt", "yuv420p", "-r", "30",
           "-an", str(out)]
    subprocess.run(cmd, capture_output=True, text=True, timeout=60)


# === 3 VIDEOS — each is ONE contiguous segment ===
VARIANTS = [
    {
        "id": "2026-07-08-V1_duong_pha_nhi",
        "src_start": 304.5,
        "src_end": 364.0,
        "hook": "NHỊN ĂN MÀ VẪN KHÔNG GIẢM CÂN?",
        "cta": "THEO DÕI ĐỂ BIẾT THÊM MẸO NHỊN ĂN",
        "pexels_overlays": [
            (5, 3, "candy"),
            (22, 3, "butter_coffee"),
            (33, 3, "sugar_cube"),
            (43, 3, "cookies"),
        ],
        "subs": [
            (0, 9, "Sai lầm số 5: vô tình phá vỡ quãng nhịn ăn"),
            (9, 17, "Tôi có ăn gì đâu, chỉ một tí xíu thôi mà"),
            (17, 27, "Nhưng tí xíu đó là rất nhiều vấn đề"),
            (27, 38, "Một thìa bơ, chút dầu ô liu: không sao"),
            (38, 48, "Nhưng chút đường: câu chuyện hoàn toàn khác"),
            (48, 55, "Vài bánh quy, viên kẹo: tưởng vô hại"),
            (55, 60, "Chút béo thì được, chút đường thì hỏng"),
        ],
        "emoji_rules": [
            (["duong", "keo", "ngot"], "1f36c_1f36c.png", "right_top"),
            (["pha", "hong", "khac"], "1f6ab_1f6ab.png", "left_top"),
            (["bo", "beo", "dau"], "2705_2705.png", "right_mid"),
        ],
    },
    {
        "id": "V2_tang_can",
        "src_start": 444.1,
        "src_end": 504.0,
        "hook": "NHỊN ĂN CÓ THỂ KHIẾN BẠN TĂNG CÂN",
        "cta": "LƯU LẠI CHO BỮA ĂN TIẾP THEO",
        "pexels_overlays": [
            (5, 3, "hungry_tired"),
            (14, 3, "fridge_night"),
            (25, 3, "small_portion"),
            (44, 3, "healthy_meal"),
        ],
        "subs": [
            (0, 10, "Sai lam so 3: an qua nhieu hoac qua it"),
            (10, 18, "Ca hai thai cuc deu gay hai"),
            (18, 25, "Nhin an den kiet suc, roi an bu tra thu"),
            (25, 33, "Kyluat nhung cat giam calo qua it"),
            (33, 43, "Nao nghi sap co nan doi"),
            (43, 50, "Ha toc do chuyen hoa co ban"),
            (50, 60, "An mot bua thuc su du chat"),
        ],
        "emoji_rules": [
            (["tang can", "can"], "2696_2696.png", "right_mid"),
            (["tra thu", "bu"], "1f6ab_1f6ab.png", "left_top"),
            (["qua it", "cat giam"], "1f50b_1f50b.png", "right_mid"),
            (["nao", "chuyen hoa", "doi"], "1f9e0_1f9e0.png", "left_mid"),
            (["du chat", "dam"], "2705_2705.png", "right_mid"),
        ],
    },
    {
        "id": "V3_met_moi",
        "src_start": 609.4,
        "src_end": 668.8,
        "hook": "MỆT MỎI CHOÁNG VÁNG KHI NHỊN ĂN?",
        "cta": "THỬ NGAY TRONG LẦN NHỊN ĂN TỚI",
        "pexels_overlays": [
            (3, 3, "drinking_water"),
            (20, 3, "dizzy"),
            (35, 3, "sea_salt"),
            (48, 3, "avocado"),
            (52, 3, "bone_broth"),
        ],
        "subs": [
            (0, 8, "Dot glycogen: moi gam giu 4 gam nuoc"),
            (8, 14, "Nuoc duoc giai phong va thai ra ngoai"),
            (14, 24, "Insulin giam, than thai natri ra ngoai"),
            (24, 35, "Khong an thi cung bo be viec uong nuoc"),
            (35, 45, "Choang vang, met moi, kem tap trung"),
            (45, 50, "Goi la cum keo"),
            (50, 59, "Khac phuc: bu nuoc, muoi, kali, magie"),
        ],
        "emoji_rules": [
            (["nuoc"], "1f4a7_1f4a7.png", "right_mid"),
            (["glycogen"], "1f4aa_1f4aa.png", "right_top"),
            (["insulin", "natri", "than"], "1f9c2_1f9c2.png", "left_top"),
            (["choang", "met", "cum keo"], "1f9e0_1f9e0.png", "left_mid"),
            (["bu", "muoi", "khoang"], "1f9c2_1f9c2.png", "right_mid"),
            (["kali", "bo"], "1f951_1f951.png", "left_top"),
        ],
    },
]


def render(v):
    vid = v["id"]
    print(f"\n{'='*55}\n  {vid}\n{'='*55}")
    d = T / vid
    d.mkdir(parents=True, exist_ok=True)

    # 1. Extract ONE contiguous segment from source (VO continuous)
    print("  Extracting contiguous segment...")
    raw = d / "raw.mp4"
    extract_segment(SRC, v["src_start"], v["src_end"], raw)
    raw_dur = dur(raw)
    print(f"  Segment: {raw_dur:.1f}s (VO continuous)")

    # 2. Prepare Pexels overlay clips
    print("  Preparing Pexels overlays...")
    pexels_clips = []
    for start, pdur, key in v["pexels_overlays"]:
        pc = d / f"pex_{key}.mp4"
        make_pexels_clip(key, pdur, pc)
        pexels_clips.append((start, pdur, key, pc))

    # 3. Build filter graph
    td = raw_dur
    cs = max(td - 5, 0)

    hook_esc = v["hook"].replace(":", "\\:").replace("'", "\u2019")
    cta_esc = v["cta"].replace(":", "\\:").replace("'", "\u2019")

    # Find used emojis
    used_emojis = []
    for st, et, txt in v["subs"]:
        txt_lower = txt.lower()
        for keywords, fn, pos in v["emoji_rules"]:
            if any(kw in txt_lower for kw in keywords):
                if fn not in used_emojis:
                    used_emojis.append(fn)
                break

    pos_map = {
        "right_top": ("W-w-60", "150"),
        "right_mid": ("W-w-60", "h/2-220"),
        "left_top": ("60", "150"),
        "left_mid": ("60", "h/2-220"),
    }

    fc_parts = []
    inputs = ["-i", str(raw)]
    input_idx = 1

    # Add Pexels inputs
    for start, pdur, key, pc in pexels_clips:
        inputs += ["-i", str(pc)]
        fc_parts.append(f"[{input_idx}:v]scale=1080:1920[pex_{key}]")
        input_idx += 1

    # Add emoji inputs
    emoji_input_map = {}
    for fn in used_emojis:
        epath = EMOJI_DIR / fn
        if not epath.exists():
            continue
        inputs += ["-i", str(epath)]
        fc_parts.append(f"[{input_idx}:v]scale=450:450[em_{fn}]")
        emoji_input_map[fn] = input_idx
        input_idx += 1

    # Chain Pexels overlays (fullscreen, time-limited)
    prev_tag = "0:v"
    chain_count = 0
    for start, pdur, key, pc in pexels_clips:
        chain_count += 1
        new_tag = f"pv{chain_count}"
        end = start + pdur
        fc_parts.append(
            f"[{prev_tag}][pex_{key}]overlay=x=0:y=0"
            f":enable='between(t,{start},{end})'[{new_tag}]"
        )
        prev_tag = new_tag

    # Chain emoji overlays
    for st, et, txt in v["subs"]:
        txt_lower = txt.lower()
        for keywords, fn, pos in v["emoji_rules"]:
            if any(kw in txt_lower for kw in keywords):
                if fn not in emoji_input_map:
                    break
                em_tag = f"em_{fn}"
                x_expr, y_expr = pos_map[pos]
                chain_count += 1
                new_tag = f"ev{chain_count}"
                fc_parts.append(
                    f"[{prev_tag}][{em_tag}]overlay=x='{x_expr}':y='{y_expr}'"
                    f":enable='between(t,{st},{et})'[{new_tag}]"
                )
                prev_tag = new_tag
                break

    # Subtitles + hook + CTA + progress bar
    sub_parts = []
    for st, et, txt in v["subs"]:
        txt_esc = txt.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\u2019")
        sub_parts.append(
            f"drawtext=text='{txt_esc}'"
            f":fontfile={FONT}:fontsize=28:fontcolor=white"
            f":borderw=3:bordercolor=black@0.8"
            f":x=(w-text_w)/2:y=h-200"
            f":enable='between(t,{st},{et})'"
        )

    chain_count += 1
    final_tag = "final"
    fc_parts.append(
        f"[{prev_tag}]{','.join(sub_parts)},"
        f"drawtext=text='{hook_esc}':fontfile={FONT}:fontsize=32:fontcolor=yellow"
        f":borderw=3:bordercolor=black@0.8:x=(w-text_w)/2:y=100"
        f":enable='between(t,0,5)',"
        f"drawtext=text='{cta_esc}':fontfile={FONT}:fontsize=22:fontcolor=white"
        f":borderw=2:bordercolor=black@0.8:x=(w-text_w)/2:y=h-70"
        f":enable='between(t,{cs:.1f},{td:.1f})',"
        f"drawbox=x=0:y=ih-4:w=iw*t/{td:.1f}:h=4:color=0xFF4500:t=fill"
        f"[{final_tag}]"
    )

    fc = ";".join(fc_parts)

    # 4. Apply video filter (video only, audio preserved via 2-step mux)
    print("  Applying overlays...")
    fv = d / "fv.mp4"
    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", fc,
        "-map", f"[{final_tag}]",
        "-c:v", "libx264", "-crf", "20", "-preset", "fast",
        "-an", str(fv)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        err_lines = [l for l in r.stderr.split("\n")
                     if any(x in l.lower() for x in ["error", "invalid", "no such"])]
        err = err_lines[0] if err_lines else r.stderr[-500:]
        print(f"  FILTER ERROR: {err[:500]}")
        return False

    # 5. Mux filtered video + original audio from raw
    out = O / f"{vid}.mp4"
    cmd = ["ffmpeg", "-y", "-i", str(fv), "-i", str(raw),
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

    # Verify audio exists
    a_check = subprocess.run(
        ["ffprobe", "-v", "quiet", "-select_streams", "a",
         "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(out)],
        capture_output=True, text=True)
    if "audio" not in a_check.stdout:
        print(f"  WARNING: No audio stream!")
        return False
    print(f"  Audio: OK")
    return True


def main():
    print("="*60 + "\n  BAC SI HAI — 3 SHORTS v4 (contiguous VO)\n" + "="*60)
    results = [render(v) for v in VARIANTS]
    print(f"\n{'='*60}\n  {sum(results)}/{len(results)} OK\n{'='*60}")
    for v, ok in zip(VARIANTS, results):
        p = O / f"{v['id']}.mp4"
        d_ = dur(p) if ok else 0
        mb_ = p.stat().st_size / 1_048_576 if ok else 0
        print(f"  {'OK' if ok else 'FAIL'} {v['id']}: {d_:.1f}s, {mb_:.1f}MB")
    shutil.rmtree(T, ignore_errors=True)


if __name__ == "__main__":
    main()
