#!/usr/bin/env python3
"""
Bac si Hai — 3 Shorts v3: Continuous VO (no gaps).
Architecture:
  - SRC clips form continuous video+audio timeline (VO never stops)
  - Pexels b-roll = full-screen overlay at specific timestamps (over VO)
  - Emoji overlays + drawtext subtitles + hook + CTA + progress bar
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


def normalize_src(inp, out):
    """Re-encode src clip to uniform 1080x1920 30fps for concat."""
    vf = ("scale=1080:1920:force_original_aspect_ratio=increase,"
          "crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2,fps=30")
    cmd = ["ffmpeg", "-y", "-i", str(inp), "-vf", vf,
           "-c:v", "libx264", "-crf", "18", "-preset", "fast",
           "-pix_fmt", "yuv420p", "-r", "30",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
           str(out)]
    subprocess.run(cmd, capture_output=True, text=True, timeout=120)


def make_pexels_overlay_clip(key, duration, out):
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


# === VARIANTS ===
# src_clips: continuous VO timeline
# pexels_overlays: (start, duration, key) — fullscreen b-roll over VO
# subs: (start, end, text) — matched to src timeline
VARIANTS = [
    {
        "id": "2026-07-08-V1_duong_pha_nhi",
        "hook": "NHỊN ĂN MÀ VẪN KHÔNG GIẢM CÂN?",
        "cta": "THEO DÕI ĐỂ BIẾT THÊM MẸO NHỊN ĂN",
        "src_clips": [
            "V0_hook", "V1_a_anhgi", "V1_b_tixiu", "V1_c_beo",
            "V1_e_duong", "V1_f_catdut", "V1_g_banhuy",
            "V1_d_insulin", "V1_h_nguyentac",
        ],
        "pexels_overlays": [
            (0, 3, "scale"),
            (12, 2, "candy"),
            (16, 3, "butter_coffee"),
            (22, 3, "sugar_cube"),
            (34, 3, "cookies"),
        ],
        "subs": [
            (0, 8, "Bạn nhịn ăn để đốt mỡ, chịu đói rất nhiều"),
            (8, 12, "Tôi có ăn gì đâu"),
            (12, 16, "Chỉ một tí xíu thôi mà"),
            (16, 22, "Một thìa bơ, chút dầu ô liu"),
            (22, 28, "Vài gam đường cũng đủ tăng insulin"),
            (28, 34, "Quãng nhịn ăn bị cắt đứt"),
            (34, 40, "Bánh quy, viên kẹo tưởng vô hại"),
            (40, 46, "Chất béo không tăng insulin"),
            (46, 51, "Chút béo thì được, chút đường thì hỏng"),
        ],
        "emoji_rules": [
            (["giảm cân", "cân", "đốt mỡ", "chịu đói"], "2696_2696.png", "right_mid"),
            (["đường", "kẹo", "ngọt", "insulin"], "1f36c_1f36c.png", "right_top"),
            (["cắt đứt", "hỏng"], "1f6ab_1f6ab.png", "left_top"),
            (["bơ", "chất béo", "béo", "dầu"], "2705_2705.png", "right_mid"),
        ],
    },
    {
        "id": "V2_tang_can",
        "hook": "NHỊN ĂN CÓ THỂ KHIẾN BẠN TĂNG CÂN",
        "cta": "LƯU LẠI CHO BỮA ĂN TIẾP THEO",
        "src_clips": [
            "V0_hook", "V2_a_gayhai", "V2_b_kietsuc", "V2_c_traothu",
            "V2_d_voneghia", "V2_e_kyluat", "V2_f_thongdiep",
            "V2_g_chuyenhoa", "V2_h_du_chat",
        ],
        "pexels_overlays": [
            (0, 3, "scale"),
            (12, 3, "hungry_tired"),
            (18, 3, "fridge_night"),
            (24, 3, "small_portion"),
            (36, 3, "healthy_meal"),
        ],
        "subs": [
            (0, 8, "Bạn nhịn ăn để đốt mỡ, chịu đói rất nhiều"),
            (8, 12, "Cả hai thái cực đều gây hại"),
            (12, 17, "Nhịn kiệt sức cả ngày"),
            (17, 23, "Rồi ăn bù trả thù"),
            (23, 27, "Mọi cố gắng trở nên vô nghĩa"),
            (27, 33, "Kỷ luật nhưng cắt giảm calo quá ít"),
            (33, 41, "Não nghĩ sắp có nạn đói"),
            (41, 48, "Hạ tốc độ chuyển hóa cơ bản"),
            (48, 54, "Ăn một bữa thực sự đủ chất"),
        ],
        "emoji_rules": [
            (["tăng cân", "cân", "đốt mỡ"], "2696_2696.png", "right_mid"),
            (["trả thù", "bù", "vô nghĩa"], "1f6ab_1f6ab.png", "left_top"),
            (["quá ít", "cắt giảm", "kỷ luật"], "1f50b_1f50b.png", "right_mid"),
            (["não", "chuyển hóa", "nạn đói"], "1f9e0_1f9e0.png", "left_mid"),
            (["đủ chất", "đạm"], "2705_2705.png", "right_mid"),
        ],
    },
    {
        "id": "V3_met_moi",
        "hook": "MỆT MỎI CHOÁNG VÁNG KHI NHỊN ĂN?",
        "cta": "THỬ NGAY TRONG LẦN NHỊN ĂN TỚI",
        "src_clips": [
            "V0_hook", "V3_a_buoi", "V3_c_2duong", "V3_d_glycogen",
            "V3_e_thanh", "V3_f_donkep", "V3_g_cumkeo",
            "V3_h_khacphuc", "V3_i_muoi",
        ],
        "pexels_overlays": [
            (0, 3, "dizzy"),
            (16, 3, "drinking_water"),
            (34, 3, "sea_salt"),
            (41, 3, "avocado"),
            (44, 3, "bone_broth"),
        ],
        "subs": [
            (0, 8, "Bạn nhịn ăn để đốt mỡ, chịu đói rất nhiều"),
            (8, 14, "Không bù nước và bù khoáng đúng"),
            (14, 18, "Cơ thể mất nước hai cách"),
            (18, 24, "Đốt glycogen, mỗi gam giữ 4 gam nước"),
            (24, 30, "Insulin giảm, thận thải natri"),
            (30, 36, "Nước và khoáng đi cùng nhau"),
            (36, 42, "Choáng váng, mệt mỏi, sương mù"),
            (42, 49, "Nhưng khắc phục rất đơn giản"),
            (49, 57, "Muối biển, bơ, rau xanh, nước hầm xương"),
        ],
        "emoji_rules": [
            (["choáng", "mệt", "sương mù"], "1f9e0_1f9e0.png", "left_mid"),
            (["nước"], "1f4a7_1f4a7.png", "right_mid"),
            (["glycogen", "đốt"], "1f4aa_1f4aa.png", "right_top"),
            (["insulin", "natri", "thận"], "1f9c2_1f9c2.png", "left_top"),
            (["muối", "khoáng", "bù"], "1f9c2_1f9c2.png", "right_mid"),
            (["bơ", "kali"], "1f951_1f951.png", "left_top"),
            (["hầm"], "1f37c_1f37c.png", "right_mid"),
        ],
    },
]


def render(v):
    vid = v["id"]
    print(f"\n{'='*55}\n  {vid}\n{'='*55}")
    d = T / vid
    d.mkdir(parents=True, exist_ok=True)

    # 1. Normalize src clips for concat
    print("  Normalizing src clips...")
    norm_files = []
    for i, name in enumerate(v["src_clips"]):
        out = d / f"s{i:02d}.mp4"
        normalize_src(C / f"{name}.mp4", out)
        norm_files.append(out)

    # 2. Concat src clips (continuous VO timeline)
    print("  Concatenating src clips...")
    raw = d / "raw.mp4"
    concat_txt = d / "concat.txt"
    concat_txt.write_text("\n".join(f"file '{p.resolve()}'" for p in norm_files))
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt),
         "-c", "copy", str(raw)],
        capture_output=True, text=True, timeout=180)
    raw_dur = dur(raw)
    print(f"  Raw (continuous VO): {raw_dur:.1f}s")

    # 3. Prepare Pexels overlay clips
    print("  Preparing Pexels overlays...")
    pexels_inputs = []
    pexels_clips = []
    for i, (start, pdur, key) in enumerate(v["pexels_overlays"]):
        pc = d / f"pex{i:02d}.mp4"
        make_pexels_overlay_clip(key, pdur, pc)
        pexels_clips.append((start, pdur, key, pc, i))

    # 4. Build filter graph
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
    # Input 0 = raw video, inputs 1..N = pexels overlays, then emojis
    inputs = ["-i", str(raw)]
    input_idx = 1

    # Add Pexels inputs
    for start, pdur, key, pc, i in pexels_clips:
        inputs += ["-i", str(pc)]
        fc_parts.append(f"[{input_idx}:v]scale=1080:1920[pex{i}]")
        input_idx += 1

    # Add emoji inputs
    emoji_input_indices = {}
    for fn in used_emojis:
        epath = EMOJI_DIR / fn
        if not epath.exists():
            continue
        inputs += ["-i", str(epath)]
        fc_parts.append(f"[{input_idx}:v]scale=450:450[em{fn}]")
        emoji_input_indices[fn] = input_idx
        input_idx += 1

    # Chain Pexels overlays (fullscreen, time-limited)
    prev_tag = "0:v"
    chain_count = 0
    for start, pdur, key, pc, i in pexels_clips:
        chain_count += 1
        new_tag = f"pv{chain_count}"
        end = start + pdur
        fc_parts.append(
            f"[{prev_tag}][pex{i}]overlay=x=0:y=0"
            f":enable='between(t,{start},{end})'[{new_tag}]"
        )
        prev_tag = new_tag

    # Chain emoji overlays
    for st, et, txt in v["subs"]:
        txt_lower = txt.lower()
        for keywords, fn, pos in v["emoji_rules"]:
            if any(kw in txt_lower for kw in keywords):
                if fn not in emoji_input_indices:
                    break
                em_tag = f"em{fn}"
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
    final_tag = f"final"
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

    # 5. Apply video filter only (audio preserved via 2-step mux)
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
        err = err_lines[0] if err_lines else r.stderr[-400:]
        print(f"  FILTER ERROR: {err[:400]}")
        return False

    # 6. Mux filtered video + original audio from raw
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
    print(f"  Audio stream: OK")
    return True


def main():
    print("="*60 + "\n  BAC SI HAI — 3 SHORTS v3 (continuous VO)\n" + "="*60)
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
