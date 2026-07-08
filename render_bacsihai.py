#!/usr/bin/env python3
"""
Bac si Hai — 3 Shorts: Nhi an gian doan (Vietnamese)
Pattern: Dangote V9 + Pexels b-roll intercut
  source clips → concat → Pexels b-roll intercut → emoji overlays → drawtext subs → hook → CTA → progress bar → mux audio
"""
import subprocess, shutil, json
from pathlib import Path

# === PATHS ===
C = Path("output/clips/bacsihai")           # Source clips (center-crop portrait)
P = Path("output/pexels")                    # Pexels b-roll
A = Path("output/bacsihai_fasting/8vM7rPWzTlI_1080p.mp4")  # Full source for audio
O = Path("output/shorts/bacsihai")           # Output
T = Path("output/shorts/temp")               # Temp
EMOJI_DIR = Path("output/emoji_processed")
FONT = "/System/Library/Fonts/Helvetica.ttc"  # Vietnamese-capable

O.mkdir(parents=True, exist_ok=True)
T.mkdir(parents=True, exist_ok=True)

# === AUDIO TIMESTAMPS (from source video, for extracting VO) ===
# Maps clip name → (start_sec, end_sec) in the ORIGINAL 1080p source
CLIP_AUDIO = {
    "V1_a_anhgi": (309.0, 313.0), "V1_b_tixiu": (313.0, 317.0),
    "V1_c_beo": (319.6, 325.6), "V1_d_insulin": (326.6, 332.6),
    "V1_e_duong": (337.0, 343.0), "V1_f_catdut": (343.0, 349.0),
    "V1_g_banhuy": (347.4, 353.4), "V1_h_nguyentac": (359.1, 364.6),
    "V2_a_gayhai": (447.0, 451.4), "V2_b_kietsuc": (451.4, 456.4),
    "V2_c_traothu": (458.0, 464.0), "V2_d_voneghia": (464.4, 468.4),
    "V2_e_kyluat": (468.6, 474.6), "V2_f_thongdiep": (478.7, 486.7),
    "V2_g_chuyenhoa": (487.6, 494.6), "V2_h_du_chat": (500.9, 506.9),
    "V3_a_buoi": (597.2, 603.2), "V3_b_lonhat": (601.8, 607.8),
    "V3_c_2duong": (609.4, 613.4), "V3_d_glycogen": (613.4, 619.4),
    "V3_e_thanh": (628.1, 634.1), "V3_f_donkep": (642.2, 648.2),
    "V3_g_cumkeo": (654.2, 660.2), "V3_h_khacphuc": (670.6, 677.6),
    "V3_i_muoi": (674.8, 682.8),
}

# === PEXELS B-ROLL MAPPING ===
PEXELS = {
    "scale": P/"scale_7802051.mp4",
    "candy": P/"candy_unwrap_6605707.mp4",
    "butter_coffee": P/"butter_coffee_8106308.mp4",
    "sugar_cube": P/"sugar_cube_7628879.mp4",
    "cookies": P/"cookies_office_6430765.mp4",
    "hungry_tired": P/"hungry_tired_7214704.mp4",
    "fridge_night": P/"fridge_night_5418706.mp4",
    "small_portion": P/"small_portion_6645820.mp4",
    "healthy_meal": P/"healthy_meal_5961891.mp4",
    "dizzy": P/"dizzy_headache_8555748.mp4",
    "sea_salt": P/"sea_salt_7601298.mp4",
    "avocado": P/"avocado_7267565.mp4",
    "green_veg": P/"green_veg_7199052.mp4",
    "bone_broth": P/"bone_broth_36886085.mp4",
    "drinking_water": P/"drinking_water_19697686.mp4",
}

# === 3 VARIANTS ===
# Each clip entry: ("src", clip_name) or ("pexels", key, duration)
# Subs: (start_sec, end_sec, text) — Vietnamese
VARIANTS = [
    {
        "id": "V1_duong_pha_nhi",
        "name": "Sai lam so 1 khien ban nhi an vo ich",
        "hook": "NHỊN ĂN MÀ VẪN KHÔNG GIẢM CÂN?",
        "cta": "THEO DÕI ĐỂ BIẾT THÊM MẸO NHỊN ĂN",
        "target": 48,
        "clips": [
            ("pexels", "scale", 2.0),
            ("src", "V1_a_anhgi"),
            ("src", "V1_b_tixiu"),
            ("pexels", "candy", 2.0),
            ("src", "V1_e_duong"),
            ("pexels", "sugar_cube", 2.0),
            ("src", "V1_f_catdut"),
            ("pexels", "butter_coffee", 2.0),
            ("src", "V1_d_insulin"),
            ("src", "V1_h_nguyentac"),
        ],
        "subs": [
            (0, 2, "Bạn nhịn ăn mà vẫn không giảm cân?"),
            (2, 5, "Tôi có ăn gì đâu"),
            (5, 8, "Chỉ một tí xíu thôi mà"),
            (8, 10, "Nhưng chút đường là câu chuyện khác"),
            (10, 12, "Vài gam đường cũng đủ"),
            (12, 14, "Tăng đường huyết và insulin"),
            (14, 16, "Quãng nhịn ăn bị cắt đứt"),
            (16, 18, "Nhưng một thìa bơ thì không sao"),
            (18, 21, "95% năng lượng từ chất béo"),
            (21, 24, "Chất béo không tăng insulin"),
            (24, 27, "Chút béo thì được"),
            (27, 30, "Nhưng chút đường thì hỏng"),
            (30, 34, "Nguyên tắc: nước lọc, cà phê đen, trà"),
            (34, 38, "Không thêm gì có đường"),
            (38, 48, "Nhịn sạch. Đốt mỡ."),
        ],
        "emoji_rules": [
            (["giảm cân", "cân"], "2696_2696.png", "right_mid"),
            (["đường", "kẹo", "ngọt"], "1f36c_1f36c.png", "right_top"),
            (["insulin", "đường huyết"], "1f36c_1f36c.png", "right_mid"),
            (["cắt đứt", "hỏng"], "1f6ab_1f6ab.png", "left_top"),
            (["bơ", "chất béo", "béo"], "2705_2705.png", "right_mid"),
            (["nước", "cà phê", "trà"], "1f4a7_1f4a7.png", "right_mid"),
            (["nhịn sạch", "đốt mỡ"], "1f525_1f525.png", "left_mid"),
        ],
    },
    {
        "id": "V2_tang_can",
        "name": "Nhi an roi lai tang can",
        "hook": "NHỊN ĂN CÓ THỂ KHIẾN BẠN TĂNG CÂN",
        "cta": "LƯU LẠI CHO BỮA ĂN TIẾP THEO",
        "target": 50,
        "clips": [
            ("pexels", "scale", 2.0),
            ("src", "V2_a_gayhai"),
            ("pexels", "hungry_tired", 2.0),
            ("src", "V2_c_traothu"),
            ("pexels", "fridge_night", 2.0),
            ("src", "V2_d_voneghia"),
            ("pexels", "small_portion", 2.0),
            ("src", "V2_e_kyluat"),
            ("src", "V2_g_chuyenhoa"),
            ("src", "V2_h_du_chat"),
            ("pexels", "healthy_meal", 2.0),
        ],
        "subs": [
            (0, 2, "Nhịn ăn có thể khiến bạn tăng cân"),
            (2, 5, "Cả hai thái cực đều gây hại"),
            (5, 8, "Nhịn kiệt sức cả ngày"),
            (8, 11, "Rồi ăn bù trả thù"),
            (11, 14, "Mọi cố gắng trở nên vô nghĩa"),
            (14, 17, "Nhưng ăn quá ít cũng nguy hiểm"),
            (17, 20, "Cắt giảm calo quá mức"),
            (20, 24, "Não nghĩ: sắp có nạn đói"),
            (24, 28, "Hạ tốc độ chuyển hóa"),
            (28, 32, "Càng nhịn càng khó giảm"),
            (32, 36, "Ăn một bữa thực sự đủ chất"),
            (36, 40, "Đủ đạm, chất béo, chất xơ"),
            (40, 44, "Đủ rau xanh"),
            (44, 50, "Ăn chậm. Nhai kỹ. Thoải mái."),
        ],
        "emoji_rules": [
            (["tăng cân", "cân"], "2696_2696.png", "right_mid"),
            (["trả thù", "bù", "vô nghĩa"], "1f6ab_1f6ab.png", "left_top"),
            (["quá ít", "kiêng khem", "cắt giảm"], "1f50b_1f50b.png", "right_mid"),
            (["não", "chuyển hóa", "nạn đói"], "1f9e0_1f9e0.png", "left_mid"),
            (["đủ chất", "đạm", "béo", "xơ", "rau"], "2705_2705.png", "right_mid"),
            (["ăn chậm", "nhai", "thoải mái"], "1f64f_1f64f.png", "left_top"),
        ],
    },
    {
        "id": "V3_met_moi",
        "name": "Ly do an khien ban met moi khi nhi an",
        "hook": "MỆT MỎI CHOÁNG VÁNG KHI NHỊN ĂN?",
        "cta": "THỬ NGAY TRONG LẦN NHỊN ĂN TỚI",
        "target": 50,
        "clips": [
            ("pexels", "dizzy", 2.0),
            ("src", "V3_a_buoi"),
            ("src", "V3_c_2duong"),
            ("src", "V3_d_glycogen"),
            ("pexels", "drinking_water", 2.0),
            ("src", "V3_e_thanh"),
            ("src", "V3_f_donkep"),
            ("src", "V3_g_cumkeo"),
            ("src", "V3_h_khacphuc"),
            ("pexels", "sea_salt", 2.0),
            ("pexels", "avocado", 2.0),
            ("pexels", "bone_broth", 2.0),
        ],
        "subs": [
            (0, 2, "Choáng váng, kiệt sức khi nhịn ăn?"),
            (2, 5, "Không bù nước và bù khoáng"),
            (5, 8, "Đây là sai lầm lớn nhất"),
            (8, 11, "Cơ thể mất nước hai cách"),
            (11, 15, "Đốt glycogen dự trữ"),
            (15, 19, "Mỗi gam glycogen giữ 4 gam nước"),
            (19, 22, "Nước được giải phóng ra ngoài"),
            (22, 26, "Insulin giảm, thận thải natri"),
            (26, 30, "Nước và khoáng đi cùng nhau"),
            (30, 34, "Choáng váng, mệt mỏi, sương mù"),
            (34, 37, "Gọi là cúm kêo"),
            (37, 41, "Nhưng khắc phục rất đơn giản"),
            (41, 45, "Bù nước: muối biển, muối hồng"),
            (45, 50, "Kali, magie: bơ, rau xanh, nước hầm"),
        ],
        "emoji_rules": [
            (["choáng", "mệt", "sương mù"], "1f9e0_1f9e0.png", "left_mid"),
            (["nước"], "1f4a7_1f4a7.png", "right_mid"),
            (["glycogen"], "1f4aa_1f4aa.png", "right_top"),
            (["insulin", "natri", "thận"], "1f9c2_1f9c2.png", "left_top"),
            (["cúm kêo"], "1f50b_1f50b.png", "right_mid"),
            (["muối", "khoáng", "bù"], "1f9c2_1f9c2.png", "right_mid"),
            (["kali", "magie", "bơ", "rau", "hầm"], "1f951_1f951.png", "left_top"),
        ],
    },
]


def dur(p):
    if not p.exists():
        return 0.0
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
        capture_output=True, text=True, timeout=15
    )
    return float(r.stdout.strip()) if r.stdout.strip() else 0.0


def concat_media(files, out, t=None):
    """Concatenate media files using ffmpeg concat demuxer."""
    txt = out.with_suffix(".txt")
    txt.write_text("\n".join(f"file '{p.resolve()}'" for p in files))
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(txt), "-c", "copy"]
    if t:
        cmd += ["-t", str(t)]
    cmd.append(str(out))
    subprocess.run(cmd, capture_output=True, text=True, timeout=180)


def loop_file(inp, out, target):
    """Loop a file to reach target duration."""
    d_in = dur(inp)
    if d_in <= 0:
        return inp
    n = int(target / d_in) + 2
    txt = out.with_suffix(".loop")
    txt.write_text("\n".join([f"file '{inp.resolve()}'"] * max(n, 5)))
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(txt),
         "-c", "copy", "-t", str(target), str(out)],
        capture_output=True, text=True, timeout=180
    )
    return out


def normalize_clip(inp, out, target_dur=None):
    """Scale any input to 1080x1920 portrait, trim to target_dur if specified."""
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2,fps=30"
    cmd = ["ffmpeg", "-y", "-i", str(inp), "-vf", vf,
           "-c:v", "libx264", "-crf", "20", "-preset", "fast",
           "-c:a", "aac", "-b:a", "192k"]
    if target_dur:
        cmd += ["-t", str(target_dur)]
    cmd.append(str(out))
    subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return out


def extract_audio(clip_names, out):
    """Extract audio segments from source video for given clip names."""
    parts = []
    for i, name in enumerate(clip_names):
        if name not in CLIP_AUDIO:
            continue
        s, e = CLIP_AUDIO[name]
        p = out.with_name(f"p{i}.aac")
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(s), "-i", str(A), "-t", str(e - s),
             "-vn", "-acodec", "aac", "-b:a", "192k", str(p)],
            capture_output=True, text=True, timeout=60
        )
        parts.append(p)
    if not parts:
        return None
    concat_media(parts, out)
    for p in parts:
        p.unlink(missing_ok=True)
    return out


def build_video_track(clip_list, work_dir):
    """Build the video track by concatenating source clips and Pexels b-roll."""
    normalized = []
    for i, item in enumerate(clip_list):
        kind = item[0]
        if kind == "src":
            name = item[1]
            inp = C / f"{name}.mp4"
            out = work_dir / f"n{i}.mp4"
            # Source clips are already 1080x1920, just re-encode for concat compat
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(inp), "-c", "copy", "-t", str(dur(inp)), str(out)],
                capture_output=True, text=True, timeout=30
            )
            normalized.append(out)
        elif kind == "pexels":
            key = item[1]
            pex_dur = item[2]
            inp = PEXELS[key]
            out = work_dir / f"n{i}.mp4"
            normalize_clip(inp, out, target_dur=pex_dur)
            normalized.append(out)
    return normalized


def render(v):
    print(f"\n{'=' * 55}\n  {v['id']}: {v['name'][:50]}\n  Target: {v['target']}s\n{'=' * 55}")
    d = T / v["id"]
    d.mkdir(parents=True, exist_ok=True)

    # 1. Build video track (source + pexels intercut)
    print("  Building video track...")
    video_clips = build_video_track(v["clips"], d)
    raw = d / "raw.mp4"
    concat_media(video_clips, raw)
    raw_dur = dur(raw)
    print(f"  Raw video: {raw_dur:.1f}s ({len(video_clips)} clips)")
    if raw_dur < 1:
        print("  SKIP: raw too short")
        return False

    # 2. Loop to target duration
    lv = d / "lv.mp4"
    loop_file(raw, lv, v["target"])
    print(f"  Looped: {dur(lv):.0f}s")

    # 3. Build audio track from source clips only
    src_clip_names = [item[1] for item in v["clips"] if item[0] == "src"]
    ra = d / "ra.aac"
    extract_audio(src_clip_names, ra)
    la = d / "la.aac"
    if ra.exists():
        loop_file(ra, la, v["target"])
        print(f"  Audio: {dur(la):.0f}s")
    else:
        print("  WARNING: No audio extracted")
        la = None

    # 4. Build filter graph: emoji overlays + drawtext + progress bar
    hook = v["hook"].replace(":", "\\:").replace("'", "\u2019")
    cta = v["cta"].replace(":", "\\:").replace("'", "\u2019")
    cs = max(v["target"] - 5, 0)
    td = v["target"]

    # Find which emojis are used (in order, deduplicated)
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
    inputs = ["-i", str(lv)]

    # Add emoji inputs
    for i, fn in enumerate(used_emojis, start=1):
        epath = EMOJI_DIR / fn
        if not epath.exists():
            print(f"  WARNING: {epath} not found, skipping emoji")
            continue
        inputs += ["-i", str(epath)]
        fc_parts.append(f"[{i}:v]scale=450:450[em{i}]")

    # Chain emoji overlays
    prev_tag = "0:v"
    chain_count = 0
    for st, et, txt in v["subs"]:
        txt_lower = txt.lower()
        for keywords, fn, pos in v["emoji_rules"]:
            if any(kw in txt_lower for kw in keywords):
                if fn not in used_emojis:
                    break
                em_idx = used_emojis.index(fn) + 1
                em_tag = f"em{em_idx}"
                x_expr, y_expr = pos_map[pos]
                chain_count += 1
                new_tag = f"v{chain_count}"
                fc_parts.append(
                    f"[{prev_tag}][{em_tag}]overlay=x='{x_expr}':y='{y_expr}'"
                    f":enable='between(t,{st},{et})'[{new_tag}]"
                )
                prev_tag = new_tag
                break

    # Drawtext: subtitles + hook + CTA + progress bar
    sub_filter_parts = []
    for st, et, txt in v["subs"]:
        # Escape for ffmpeg drawtext: escape colons and single quotes
        txt_esc = txt.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\u2019")
        sub_filter_parts.append(
            f"drawtext=text='{txt_esc}'"
            f":fontfile={FONT}:fontsize=28:fontcolor=white:borderw=3:bordercolor=black@0.8"
            f":x=(w-text_w)/2:y=h-200"
            f":enable='between(t,{st},{et})'"
        )

    chain_count += 1
    final_tag = f"v{chain_count}"
    fc_parts.append(
        f"[{prev_tag}]{','.join(sub_filter_parts)},"
        f"drawtext=text='{hook}':fontfile={FONT}:fontsize=32:fontcolor=yellow"
        f":borderw=3:bordercolor=black@0.8:x=(w-text_w)/2:y=100"
        f":enable='between(t,0,5)',"
        f"drawtext=text='{cta}':fontfile={FONT}:fontsize=22:fontcolor=white"
        f":borderw=2:bordercolor=black@0.8:x=(w-text_w)/2:y=h-70"
        f":enable='between(t,{cs},{td})',"
        f"drawbox=x=0:y=ih-4:w=iw*t/{td}:h=4:color=0xFF4500:t=fill"
        f"[{final_tag}]"
    )

    fc = ";".join(fc_parts)

    # 5. Apply filter graph
    print("  Applying filters (emoji + text + progress)...")
    fv = d / "fv.mp4"
    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", fc,
        "-map", f"[{final_tag}]",
        "-c:v", "libx264", "-crf", "20", "-preset", "fast",
        str(fv)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        err_lines = [l for l in r.stderr.split("\n") if any(x in l.lower() for x in ["error", "invalid", "no such"])]
        err = err_lines[0] if err_lines else r.stderr[-300:]
        print(f"  FILTER ERROR: {err[:300]}")
        return False
    print(f"  Filtered: {dur(fv):.0f}s")

    # 6. Mux video + audio
    out = O / f"{v['id']}.mp4"
    if la and la.exists():
        cmd = ["ffmpeg", "-y", "-i", str(fv), "-i", str(la),
               "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
               "-shortest", str(out)]
    else:
        cmd = ["ffmpeg", "-y", "-i", str(fv), "-c:a", "aac", "-b:a", "192k", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(f"  MUX ERROR: {r.stderr[-200:]}")
        return False

    od = dur(out)
    mb = out.stat().st_size / 1_048_576
    print(f"  => {out.name}: {od:.0f}s, {mb:.1f}MB")

    # 7. Verify specs
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries",
         "stream=width,height,codec_name:format=duration",
         "-of", "json", str(out)],
        capture_output=True, text=True
    )
    if probe.returncode == 0:
        info = json.loads(probe.stdout)
        streams = info.get("streams", [])
        vstream = next((s for s in streams if s.get("codec_type") == "video"), {})
        w = vstream.get("width")
        h = vstream.get("height")
        codec = vstream.get("codec_name")
        final_dur = float(info.get("format", {}).get("duration", 0))
        ok = (w == 1080 and h == 1920 and codec == "h264" and 30 <= final_dur <= 60)
        print(f"  SPEC: {w}x{h} {codec} {final_dur:.1f}s {'OK' if ok else 'FAIL'}")
        if not ok:
            print(f"  SPEC VIOLATION! Expected 1080x1920 h264 30-60s")
            return False
    return True


def main():
    print("=" * 60 + "\n  BAC SI HAI — 3 SHORTS (Vietnamese)\n" + "=" * 60)
    results = [render(v) for v in VARIANTS]
    print(f"\n{'=' * 60}\n  {sum(results)}/{len(results)} OK\n{'=' * 60}")
    for v, ok in zip(VARIANTS, results):
        p = O / f"{v['id']}.mp4"
        d_ = dur(p) if ok else 0
        mb_ = p.stat().st_size / 1_048_576 if ok else 0
        print(f"  {'OK' if ok else 'FAIL'} {v['id']}: {d_:.0f}s, {mb_:.1f}MB")
    shutil.rmtree(T, ignore_errors=True)


if __name__ == "__main__":
    main()
