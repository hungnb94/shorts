#!/usr/bin/env python3
"""
Bac si Hai — 3 Shorts v2: Fix audio repeat + premature cut.
Key change: NO loop, NO -shortest. Natural concat duration.
  src clips (with VO) + pexels (muted) → concat → overlays → done
"""
import subprocess, shutil
from pathlib import Path

C = Path("output/clips/bacsihai")
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
        capture_output=True, text=True, timeout=15
    )
    return float(r.stdout.strip()) if r.stdout.strip() else 0.0


def normalize_for_concat(inp, out, mute=False):
    """Re-encode clip to 1080x1920 30fps with uniform encoding for concat.
    If mute=True, add silent audio track (needed for concat compatibility)."""
    vf = ("scale=1080:1920:force_original_aspect_ratio=increase,"
          "crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2,fps=30")
    if mute:
        # Generate silent audio track so concat doesn't break audio stream
        cmd = ["ffmpeg", "-y", "-i", str(inp),
               "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
               "-vf", vf,
               "-c:v", "libx264", "-crf", "18", "-preset", "fast",
               "-pix_fmt", "yuv420p", "-r", "30",
               "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
               "-shortest", str(out)]
    else:
        cmd = ["ffmpeg", "-y", "-i", str(inp), "-vf", vf,
               "-c:v", "libx264", "-crf", "18", "-preset", "fast",
               "-pix_fmt", "yuv420p", "-r", "30",
               "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
               str(out)]
    subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return out


# === VARIANTS — clips + subtitle timings matched to natural concat timeline ===
# Timeline calculated from measured clip durations (see analysis output)
VARIANTS = [
    {
        "id": "2026-07-08-V1_duong_pha_nhi",
        "hook": "NHỊN ĂN MÀ VẪN KHÔNG GIẢM CÂN?",
        "cta": "THEO DÕI ĐỂ BIẾT THÊM MẸO NHỊN ĂN",
        "clips": [
            ("pexels", "scale", 2.0),
            ("src", "V1_a_anhgi"),      # 4.0s
            ("src", "V1_b_tixiu"),      # 4.0s
            ("pexels", "candy", 2.0),
            ("src", "V1_e_duong"),      # 6.0s
            ("pexels", "sugar_cube", 2.0),
            ("src", "V1_f_catdut"),     # 6.0s
            ("pexels", "butter_coffee", 2.0),
            ("src", "V1_d_insulin"),    # 6.0s
            ("src", "V1_h_nguyentac"),  # 5.5s
        ],
        # Timeline: 0-2 pex, 2-6 src, 6-10 src, 10-12 pex, 12-18 src,
        #           18-20 pex, 20-26 src, 26-28 pex, 28-34 src, 34-39.5 src
        "subs": [
            (0, 2, "Bạn nhịn ăn mà vẫn không giảm cân?"),
            (2, 6, "Tôi có ăn gì đâu"),
            (6, 10, "Chỉ một tí xíu thôi mà"),
            (10, 12, "Nhưng chút đường là khác"),
            (12, 18, "Vài gam đường cũng đủ tăng insulin"),
            (18, 20, "Quãng nhịn ăn bị cắt đứt"),
            (20, 26, "Nhưng một thìa bơ thì không sao"),
            (26, 28, "95% năng lượng từ chất béo"),
            (28, 34, "Chất béo không tăng insulin"),
            (34, 39, "Chút béo thì được, chút đường thì hỏng"),
        ],
        "emoji_rules": [
            (["giảm cân", "cân"], "2696_2696.png", "right_mid"),
            (["đường", "kẹo", "ngọt", "insulin"], "1f36c_1f36c.png", "right_top"),
            (["cắt đứt", "hỏng"], "1f6ab_1f6ab.png", "left_top"),
            (["bơ", "chất béo", "béo"], "2705_2705.png", "right_mid"),
        ],
    },
    {
        "id": "V2_tang_can",
        "hook": "NHỊN ĂN CÓ THỂ KHIẾN BẠN TĂNG CÂN",
        "cta": "LƯU LẠI CHO BỮA ĂN TIẾP THEO",
        "clips": [
            ("pexels", "scale", 2.0),
            ("src", "V2_a_gayhai"),     # 4.4s
            ("pexels", "hungry_tired", 2.0),
            ("src", "V2_c_traothu"),    # 6.0s
            ("pexels", "fridge_night", 2.0),
            ("src", "V2_d_voneghia"),   # 4.0s
            ("pexels", "small_portion", 2.0),
            ("src", "V2_e_kyluat"),     # 6.0s
            ("src", "V2_g_chuyenhoa"),  # 7.0s
            ("src", "V2_h_du_chat"),    # 6.0s
            ("pexels", "healthy_meal", 2.0),
        ],
        # Timeline: 0-2, 2-6.4, 6.4-8.4, 8.4-14.4, 14.4-16.4, 16.4-20.4,
        #           20.4-22.4, 22.4-28.4, 28.4-35.4, 35.4-41.4, 41.4-43.4
        "subs": [
            (0, 2, "Nhịn ăn có thể khiến bạn tăng cân"),
            (2, 6, "Cả hai thái cực đều gây hại"),
            (6, 8, "Nhịn kiệt sức cả ngày"),
            (8, 14, "Rồi ăn bù trả thù"),
            (14, 16, "Mọi cố gắng trở nên vô nghĩa"),
            (16, 20, "Nhưng ăn quá ít cũng nguy hiểm"),
            (20, 22, "Cắt giảm calo quá mức"),
            (22, 28, "Não nghĩ sắp có nạn đói"),
            (28, 35, "Hạ tốc độ chuyển hóa"),
            (35, 41, "Ăn một bữa thực sự đủ chất"),
            (41, 43, "Đủ đạm, béo, xơ, rau xanh"),
        ],
        "emoji_rules": [
            (["tăng cân", "cân"], "2696_2696.png", "right_mid"),
            (["trả thù", "bù", "vô nghĩa"], "1f6ab_1f6ab.png", "left_top"),
            (["quá ít", "kiêng khem", "cắt giảm"], "1f50b_1f50b.png", "right_mid"),
            (["não", "chuyển hóa", "nạn đói"], "1f9e0_1f9e0.png", "left_mid"),
            (["đủ chất", "đạm", "béo", "xơ", "rau"], "2705_2705.png", "right_mid"),
        ],
    },
    {
        "id": "V3_met_moi",
        "hook": "MỆT MỎI CHOÁNG VÁNG KHI NHỊN ĂN?",
        "cta": "THỬ NGAY TRONG LẦN NHỊN ĂN TỚI",
        "clips": [
            ("pexels", "dizzy", 2.0),
            ("src", "V3_a_buoi"),       # 6.0s
            ("src", "V3_c_2duong"),     # 4.0s
            ("src", "V3_d_glycogen"),   # 6.0s
            ("pexels", "drinking_water", 2.0),
            ("src", "V3_e_thanh"),      # 6.0s
            ("src", "V3_f_donkep"),     # 6.0s
            ("src", "V3_g_cumkeo"),     # 6.0s
            ("src", "V3_h_khacphuc"),   # 7.0s
            ("pexels", "sea_salt", 2.0),
            ("pexels", "avocado", 2.0),
            ("pexels", "bone_broth", 2.0),
        ],
        # Timeline: 0-2, 2-8, 8-12, 12-18, 18-20, 20-26, 26-32, 32-38, 38-45, 45-47, 47-49, 49-51
        "subs": [
            (0, 2, "Choáng váng, kiệt sức khi nhịn ăn?"),
            (2, 8, "Không bù nước và bù khoáng"),
            (8, 12, "Cơ thể mất nước hai cách"),
            (12, 18, "Đốt glycogen, mỗi gam giữ 4 gam nước"),
            (18, 20, "Nước được giải phóng"),
            (20, 26, "Insulin giảm, thận thải natri"),
            (26, 32, "Nước và khoáng đi cùng nhau"),
            (32, 38, "Choáng váng, mệt mỏi, sương mù"),
            (38, 45, "Gọi là cúm kêo, nhưng khắc phục dễ"),
            (45, 47, "Muối biển, muối hồng"),
            (47, 49, "Kali: quả bơ"),
            (49, 51, "Nước hầm xương"),
        ],
        "emoji_rules": [
            (["choáng", "mệt", "sương mù"], "1f9e0_1f9e0.png", "left_mid"),
            (["nước"], "1f4a7_1f4a7.png", "right_mid"),
            (["glycogen"], "1f4aa_1f4aa.png", "right_top"),
            (["insulin", "natri", "thận"], "1f9c2_1f9c2.png", "left_top"),
            (["cúm kêo"], "1f50b_1f50b.png", "right_mid"),
            (["muối", "khoáng", "bù"], "1f9c2_1f9c2.png", "right_mid"),
            (["kali", "bơ"], "1f951_1f951.png", "left_top"),
            (["hầm"], "1f37c_1f37c.png", "right_mid"),
        ],
    },
]


def render(v):
    vid = v["id"]
    print(f"\n{'='*55}\n  {vid}\n{'='*55}")
    d = T / vid
    d.mkdir(parents=True, exist_ok=True)

    # 1. Normalize all clips for concat (src=with audio, pexels=muted)
    print("  Normalizing clips...")
    norm_files = []
    for i, item in enumerate(v["clips"]):
        kind = item[0]
        out = d / f"n{i:02d}.mp4"
        if kind == "src":
            name = item[1]
            inp = C / f"{name}.mp4"
            normalize_for_concat(inp, out, mute=False)
        else:
            key = item[1]
            trim_dur = item[2]
            inp = PEXELS_MAP[key]
            # Trim to target duration then normalize
            tmp = d / f"p{i:02d}_raw.mp4"
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(inp), "-t", str(trim_dur),
                 "-c", "copy", str(tmp)],
                capture_output=True, text=True, timeout=60
            )
            normalize_for_concat(tmp, out, mute=True)
            tmp.unlink(missing_ok=True)
        norm_files.append(out)

    # 2. Concat all clips (natural duration, NO loop)
    print("  Concatenating...")
    raw = d / "raw.mp4"
    concat_txt = d / "concat.txt"
    concat_txt.write_text("\n".join(f"file '{p.resolve()}'" for p in norm_files))
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt),
         "-c", "copy", str(raw)],
        capture_output=True, text=True, timeout=180
    )
    raw_dur = dur(raw)
    print(f"  Raw: {raw_dur:.1f}s")

    # 3. Build overlay filter (emoji + drawtext + progress bar)
    td = raw_dur  # Use actual duration, not arbitrary target
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

    for i, fn in enumerate(used_emojis, start=1):
        epath = EMOJI_DIR / fn
        if not epath.exists():
            continue
        inputs += ["-i", str(epath)]
        fc_parts.append(f"[{i}:v]scale=450:450[em{i}]")

    # Emoji overlay chain
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
    final_tag = f"v{chain_count}"
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

    # 4. Apply video filter only (emoji + drawtext + progress bar)
    print("  Applying video overlays...")
    fv = d / "fv.mp4"
    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", fc,
        "-map", f"[{final_tag}]",
        "-c:v", "libx264", "-crf", "20", "-preset", "fast",
        "-an",  # no audio — will mux separately
        str(fv)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        err_lines = [l for l in r.stderr.split("\n")
                     if any(x in l.lower() for x in ["error", "invalid", "no such"])]
        err = err_lines[0] if err_lines else r.stderr[-400:]
        print(f"  FILTER ERROR: {err[:400]}")
        return False

    # 5. Mux filtered video + original audio from raw (2 separate inputs)
    out = O / f"{vid}.mp4"
    cmd = ["ffmpeg", "-y", "-i", str(fv), "-i", str(raw),
           "-map", "0:v", "-map", "1:a",
           "-c:v", "copy",
           "-c:a", "aac", "-b:a", "192k",
           "-shortest", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(f"  MUX ERROR: {r.stderr[-300:]}")
        return False

    od = dur(out)
    mb = out.stat().st_size / 1_048_576
    print(f"  => {out.name}: {od:.1f}s, {mb:.1f}MB")
    return True


def main():
    print("="*60 + "\n  BAC SI HAI — 3 SHORTS v2 (fix audio + cut)\n" + "="*60)
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
