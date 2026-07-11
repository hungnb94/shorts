#!/usr/bin/env python3
"""
Dangote - 9 viral Shorts V6: 45-60s each, English, real quotes, full-screen portrait.
"""
import subprocess, shutil, json
from pathlib import Path

C = Path("output/clips/dangote")
A = Path("output/source_videos/audio.wav")
O = Path("output/shorts/dangote")
T = Path("output/shorts/temp")
O.mkdir(parents=True,exist_ok=True)

# Clip reference: {name: (start, end)} for audio extraction
CLIP_AUDIO = {
    "C1_hook": (0,4), "C2_candy": (20.6,23.3), "C3_refuse_no": (177.9,187.1),
    "C4_8years": (202.1,207.8), "C5_negotiation": (423.0,425.3),
    "C6_150b": (159.1,165.8), "C7_pregnant": (137.6,139.9),
    "C8_10b_revenue": (791.1,792.2), "C9_backward": (892.5,895.1),
    "C10_40b": (960.2,962.2), "C11_humble": (974.5,985.3),
    "C12_industrialize": (1036.8,1038.6), "C13_worth_it": (1084.5,1086.7),
    "C14_lehman": (111.9,113.6), "C15_do_your_best": (530.2,536.2),
    "C16_asia_africa": (811.6,819.6), "C17_dont_give_up": (1067.0,1077.6),
    "C18_small_biz_gap": (155.0,158.8), "C21_young_africa": (854.0,859.0),
}

VARIANTS = [
    {
        "id": "2026-07-08-V1_authority",
        "name": "The Richest Black Man on Earth Is Worth $30B",
        "clips": ["C1_hook","C2_candy","C9_backward","C8_10b_revenue","C10_40b","C11_humble","C16_asia_africa","C21_young_africa","C12_industrialize","C17_dont_give_up","C13_worth_it"],
        "hook": "THE RICHEST BLACK MAN ON EARTH IS WORTH $30B",
        "cta": "FOLLOW FOR BILLIONAIRE MINDSETS",
        "target": 52,
        "subs": [
            (0,4,"Richest black man in the world"),
            (4,7,"Started with candy to classmates"),
            (7,10,"Backward integration strategy"),
            (10,12,"About $10B a year in revenue"),
            (12,14,"Family worth over $40B"),
            (14,18,"Humbled all my life"),
            (18,24,"Asia was developed by Asians"),
            (24,30,"70% of population under 30"),
            (30,35,"I want to industrialize Africa"),
            (35,45,"Never get discouraged"),
            (45,50,"Was it worth it? Yes it was"),
        ],
    },
    {
        "id": "2026-07-08-V2_underdog",
        "name": "Candy to $30B Journey",
        "clips": ["C1_hook","C2_candy","C9_backward","C16_asia_africa","C21_young_africa","C11_humble","C12_industrialize","C17_dont_give_up","C13_worth_it"],
        "hook": "HE SOLD CANDY AS A KID. NOW HE IS WORTH $30B",
        "cta": "START SMALL. REINVEST. SCALE.",
        "target": 50,
        "subs": [
            (0,4,"Richest black person on the planet"),
            (4,7,"Started selling candy at school"),
            (7,10,"Backward integration"),
            (10,17,"Asia was developed by Asians"),
            (17,22,"70% population under 30"),
            (22,30,"Humbled all my life"),
            (30,33,"I want to industrialize Africa"),
            (33,44,"Be honest. Be strategic."),
            (44,48,"Was the sacrifice worth it? Yes"),
        ],
    },
    {
        "id": "2026-07-08-V3_refuse_no",
        "name": "99% Success = Refuse No",
        "clips": ["C7_pregnant","C14_lehman","C18_small_biz_gap","C6_150b","C4_8years","C3_refuse_no","C15_do_your_best","C17_dont_give_up"],
        "hook": "99% OF SUCCESS IS REFUSING TO TAKE NO",
        "cta": "SAVE THIS FOR WHEN YOU HEAR NO",
        "target": 50,
        "subs": [
            (0,3,"Five months pregnant when I started"),
            (3,5,"Lehman Brothers at 18"),
            (5,9,"Nobody invests in small businesses"),
            (9,15,"$150B opportunity. Only 2% to women"),
            (15,21,"Eight years to raise my first fund"),
            (21,30,"99% success = refusing to take no"),
            (30,36,"Do your best. Leave the rest."),
            (36,48,"Never get discouraged"),
        ],
    },
    {
        "id": "2026-07-08-V4_persistence",
        "name": "8 Years to Raise a Fund",
        "clips": ["C14_lehman","C7_pregnant","C18_small_biz_gap","C6_150b","C4_8years","C3_refuse_no","C15_do_your_best","C17_dont_give_up"],
        "hook": "8 YEARS OF REJECTION. SHE BUILT THE BIGGEST FUND IN AFRICA",
        "cta": "TAG SOMEONE WHO NEVER QUITS",
        "target": 50,
        "subs": [
            (0,2,"Lehman Brothers at 18"),
            (2,5,"Five months pregnant"),
            (5,9,"Nobody investing in small businesses"),
            (9,15,"$150B opportunity"),
            (15,21,"Eight years to raise my first fund"),
            (21,30,"Persistence cuts through rock"),
            (30,36,"Do your best. Leave the rest."),
            (36,48,"Never get discouraged"),
        ],
    },
    {
        "id": "2026-07-08-V5_table",
        "name": "No Seat? Build the Table",
        "clips": ["C7_pregnant","C14_lehman","C4_8years","C18_small_biz_gap","C6_150b","C3_refuse_no","C15_do_your_best","C17_dont_give_up","C13_worth_it"],
        "hook": "NO SEAT AT THE TABLE? BUILD YOUR OWN.",
        "cta": "WHAT TABLE ARE YOU BUILDING?",
        "target": 52,
        "subs": [
            (0,3,"Five months pregnant. Started anyway"),
            (3,5,"Lehman Brothers at 18"),
            (5,11,"Create your own seat at the table"),
            (11,15,"Nobody investing in small businesses"),
            (15,22,"$150B opportunity. Nobody looking there"),
            (22,31,"No seat? Create your own table"),
            (31,37,"Do your best. Leave the rest."),
            (37,47,"Never get discouraged"),
            (47,50,"Was the sacrifice worth it? Yes"),
        ],
    },
    {
        "id": "2026-07-08-V6_negotiation",
        "name": "3-Word Negotiation Secret",
        "clips": ["C5_negotiation","C15_do_your_best","C4_8years","C3_refuse_no","C6_150b","C17_dont_give_up","C13_worth_it"],
        "hook": "CLOSED A $1B DEAL. HIS SECRET? 3 WORDS.",
        "cta": "USE THIS IN YOUR NEXT NEGOTIATION",
        "target": 50,
        "subs": [
            (0,3,"Listen. Agree or disagree. Close."),
            (3,9,"Do your best. Leave the rest."),
            (9,15,"Eight years of persistence"),
            (15,24,"Persistence > power"),
            (24,31,"$150B opportunity. Look where others ignore"),
            (31,43,"Be honest. Be strategic."),
            (43,48,"Was it worth it? Yes"),
        ],
    },
    {
        "id": "2026-07-08-V7_marketgap",
        "name": "$150B Opportunity, Only 2% to Women",
        "clips": ["C18_small_biz_gap","C6_150b","C7_pregnant","C14_lehman","C4_8years","C3_refuse_no","C15_do_your_best","C17_dont_give_up","C13_worth_it"],
        "hook": "$150B OPPORTUNITY. ONLY 2% GOES TO WOMEN.",
        "cta": "WHERE IS EVERYONE IGNORING?",
        "target": 52,
        "subs": [
            (0,4,"Nobody invests in small businesses"),
            (4,11,"$150B opportunity. Only 2% to women"),
            (11,14,"Five months pregnant when I started"),
            (14,16,"Lehman Brothers. JP Morgan. PE at 21"),
            (16,22,"Eight years to raise my first fund"),
            (22,31,"99% success = refusing to take no"),
            (31,37,"Do your best. Leave the rest."),
            (37,48,"Never get discouraged"),
            (48,50,"Was it worth it? Yes"),
        ],
    },
    {
        "id": "2026-07-08-V8_pregnant",
        "name": "Pregnant at 29, Built Africa's Largest Fund",
        "clips": ["C7_pregnant","C14_lehman","C18_small_biz_gap","C6_150b","C4_8years","C3_refuse_no","C15_do_your_best","C17_dont_give_up","C13_worth_it"],
        "hook": "5 MONTHS PREGNANT. STARTED AFRICA LARGEST VC FUND.",
        "cta": "FOLLOW FOR MORE UNTOLD FOUNDER STORIES",
        "target": 52,
        "subs": [
            (0,3,"Five months pregnant. Started my own fund"),
            (3,5,"Lehman at 18. JP Morgan at 20."),
            (5,9,"Nobody invests in small businesses"),
            (9,16,"$150B opportunity. Only 2% to women"),
            (16,22,"Eight years to raise my first fund"),
            (22,31,"99% success = refusing to take no"),
            (31,37,"Do your best. Leave the rest."),
            (37,48,"Never get discouraged"),
            (48,50,"Was it worth it? Yes"),
        ],
    },
    {
        "id": "2026-07-08-V9_vision",
        "name": "$40B, Humble, Industrialize Africa",
        "clips": ["C10_40b","C11_humble","C16_asia_africa","C21_young_africa","C9_backward","C12_industrialize","C17_dont_give_up","C13_worth_it"],
        "hook": "WORTH $40B. DRIVES A TOYOTA. WANTS TO INDUSTRIALIZE AFRICA.",
        "cta": "WHAT LEGACY ARE YOU BUILDING?",
        "target": 50,
        "subs": [
            (0,3,"Family worth over $40B"),
            (3,11,"Humbled all my life"),
            (11,18,"Asia was developed by Asians"),
            (18,23,"70% of Africa is under 30"),
            (23,26,"Backward integration"),
            (26,29,"I want to industrialize Africa"),
            (29,43,"Be honest. Be strategic. Never quit"),
            (43,48,"Was it worth it? Yes"),
        ],
    },
]


def dur(p):
    if not p.exists(): return 0.0
    r = subprocess.run(["ffprobe","-v","quiet","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(p)],capture_output=True,text=True,timeout=15)
    return float(r.stdout.strip()) if r.stdout.strip() else 0.0


def concat_media(files, out, t=None):
    txt = out.with_suffix(".txt")
    txt.write_text("\n".join(f"file '{p.resolve()}'" for p in files))
    cmd = ["ffmpeg","-y","-f","concat","-safe","0","-i",str(txt),"-c","copy"]
    if t: cmd += ["-t",str(t)]
    cmd.append(str(out))
    subprocess.run(cmd,capture_output=True,text=True,timeout=180)


def loop_file(inp, out, target):
    d_in = dur(inp)
    if d_in <= 0: return inp
    n = int(target/d_in)+2
    txt = out.with_suffix(".loop")
    txt.write_text("\n".join([f"file '{inp.resolve()}'"]*max(n,5)))
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(txt),"-c","copy","-t",str(target),str(out)],capture_output=True,text=True,timeout=180)
    return out


def extract_audio(clip_names, out, extra):
    """Extract audio for the given clip names + any extra ranges."""
    ranges = []
    for name in clip_names:
        if name in CLIP_AUDIO:
            ranges.append(CLIP_AUDIO[name])
    ranges += extra
    parts = []
    for i,(s,e) in enumerate(ranges):
        p = out.with_name(f"p{i}.aac")
        subprocess.run(["ffmpeg","-y","-ss",str(s),"-i",str(A),"-t",str(e-s),"-vn","-acodec","aac","-b:a","192k",str(p)],capture_output=True,text=True,timeout=60)
        parts.append(p)
    concat_media(parts, out)
    for p in parts: p.unlink(missing_ok=True)
    return out


def write_srt(subs, path, dur_t):
    lines = []
    for i,(st,et,txt) in enumerate(subs,1):
        st=max(0,st); et=min(et,dur_t)
        def ts(t): return f"{int(t/3600):02d}:{int(t/60)%60:02d}:{int(t)%60:02d},{int(t%1*1000):03d}"
        lines.extend([str(i), f"{ts(st)} --> {ts(et)}", txt, ""])
    path.write_text("\n".join(lines))


def render(v):
    print(f"\n{'='*55}\n  {v['id']}: {v['name'][:60]}\n  Target: {v['target']}s, Clips: {len(v['clips'])}\n{'='*55}")
    d = T/v['id']; d.mkdir(parents=True,exist_ok=True)

    raw = d/"raw.mp4"
    clip_paths = [C/f"{c}.mp4" for c in v['clips']]
    concat_media(clip_paths, raw)
    raw_dur = dur(raw)
    print(f"  Raw: {raw_dur:.1f}s ({len(v['clips'])} clips)")
    if raw_dur < 1:
        print(f"  ⚠ Raw too short - skipping")
        return False

    lv = d/"lv.mp4"
    loop_file(raw, lv, v['target'])
    print(f"  Video: {dur(lv):.0f}s")

    ra = d/"ra.aac"
    extract_audio(v['clips'], ra, [])
    la = d/"la.aac"
    loop_file(ra, la, v['target'])
    print(f"  Audio: {dur(la):.0f}s")

    sr = d/"subs.srt"
    write_srt(v['subs'], sr, v['target'])

    hook = v['hook'].replace(":","\\:")
    cta = v['cta'].replace(":","\\:")
    cs = max(v['target']-5,0); td = v['target']

    # === FREQUENT EDITING (ADR-0016) ===
    # 1. Big emoji overlays: native macOS-rendered PNGs (450px), at "position-appropriate" locations
    emoji_dir = Path('output/emoji_processed')
    pop_rules = [
        (["richest","billion","$","worth","revenue","40b","10b","30b"], "1f4b0_1f4b0.png", "right_mid"),
        (["pregnant","five months","shock","fund","never"], "1f525_1f525.png", "left_top"),
        (["humble","humbled"], "1f64f_1f64f.png", "left_mid"),
        (["africa","population","70%","under 30","planet","world"], "1f30d_1f30d.png", "right_mid"),
        (["industrialize","backward","integration"], "1f3ed_1f3ed.png", "left_mid"),
        (["success","persistence","refusing","years","quit","encouraged"], "1f4aa_1f4aa.png", "right_mid"),
        (["worth it","sacrifice","yes","it was","honest","strategic"], "2728_2728.png", "left_top"),
        (["negotiation","deal","listen","agree","close"], "1f91d_1f91d.png", "right_mid"),
        (["lehman","18","started"], "1f48e_1f48e.png", "right_top"),
        (["best","leave the rest"], "2665_2665.png", "left_mid"),
    ]

    pos_map = {
        "right_top":   ("W-w-60",  "150"),
        "right_mid":   ("W-w-60",  "h/2-220"),
        "left_top":    ("60",      "150"),
        "left_mid":    ("60",      "h/2-220"),
    }

    # Find which emojis are used (in order, deduplicated)
    used_emojis = []
    for st, et, txt in v['subs']:
        txt_lower = txt.lower()
        for keywords, fn, pos in pop_rules:
            if any(kw in txt_lower for kw in keywords):
                if fn not in used_emojis:
                    used_emojis.append(fn)
                break

    # Build the filter graph step by step
    fc_parts = []
    inputs = ['-i', str(lv)]

    # Add each emoji as input and scale to 450x450 (NO -loop 1: causes deadlock with enable)
    for i, fn in enumerate(used_emojis, start=1):
        epath = emoji_dir / fn
        if not epath.exists():
            print(f"  WARNING: {epath} not found")
            continue
        inputs += ['-i', str(epath)]
        fc_parts.append(f'[{i}:v]scale=450:450[em{i}]')

    # Chain overlays - keep the chain in one path
    prev_tag = '0:v'
    chain_count = 0
    for st, et, txt in v['subs']:
        txt_lower = txt.lower()
        for keywords, fn, pos in pop_rules:
            if any(kw in txt_lower for kw in keywords):
                if fn not in used_emojis:
                    break
                em_idx = used_emojis.index(fn) + 1
                em_tag = f'em{em_idx}'
                x_expr, y_expr = pos_map[pos]
                chain_count += 1
                new_tag = f'v{chain_count}'
                fc_parts.append(
                    f'[{prev_tag}][{em_tag}]overlay=x=\'{x_expr}\':y=\'{y_expr}\':enable=\'between(t,{st},{et})\'[{new_tag}]'
                )
                prev_tag = new_tag
                break

    # Add drawtext (subtitles + hook + CTA + progress) and zoompan at the end
    sub_filter_parts = []
    for st, et, txt in v['subs']:
        txt_esc = txt.replace("'", "'\\''").replace(":", "\\:")
        sub_filter_parts.append(
            f"drawtext=text='{txt_esc}'"
            f":fontsize=22:fontcolor=white:borderw=2:bordercolor=black"
            f":x=(w-text_w)/2:y=h-180"
            f":enable='between(t,{st},{et})'"
        )

    chain_count += 1
    final_tag = f'v{chain_count}'
    fc_parts.append(
        f'[{prev_tag}]{",".join(sub_filter_parts)},'
        f"drawtext=text='{hook}':fontsize=28:fontcolor=yellow:borderw=2:bordercolor=black:x=(w-text_w)/2:y=80:enable='between(t,0,5)',"
        f"drawtext=text='{cta}':fontsize=18:fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=h-60:enable='between(t,{cs},{td})',"
        f"drawbox=x=0:y=ih-4:w=iw*t/{td}:h=4:color=0xFF4500:t=fill"
        f'[{final_tag}]'
    )

    fc = ';'.join(fc_parts)

    # 2. Apply ffmpeg with full filter graph (NO zoompan to keep it fast)
    fv = d/"fv.mp4"
    cmd = ['ffmpeg', '-y'] + inputs + [
        '-filter_complex', fc,
        '-map', f'[{final_tag}]',
        '-c:v', 'libx264', '-crf', '20', '-preset', 'fast',
        str(fv)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        err = next((l for l in r.stderr.split('\n') if any(x in l.lower() for x in ['error','invalid','no such'])), r.stderr[-200:])
        print(f"  FILTER ERROR: {err[:200]}")
        return False
    print(f"  Filtered: {dur(fv):.0f}s")

    out = O/f"{v['id']}.mp4"
    r = subprocess.run(["ffmpeg","-y","-i",str(fv),"-i",str(la),"-c:v","copy","-c:a","aac","-b:a","192k","-shortest",str(out)],capture_output=True,text=True,timeout=300)
    if r.returncode != 0: print(f"  MUX ERROR"); return False
    od=dur(out); mb=out.stat().st_size/1_048_576
    print(f"  => {out.name}: {od:.0f}s, {mb:.1f}MB")
    return True


def main():
    print("="*60+"\n  DANGOTE - 9 SHORTS (45-60s each)\n"+"="*60)
    results = [render(v) for v in VARIANTS]
    print(f"\n{'='*60}\n  {sum(results)}/{len(results)} OK\n{'='*60}")
    for v,ok in zip(VARIANTS,results):
        p = O/f"{v['id']}.mp4"
        d_ = dur(p) if ok else 0; mb_ = p.stat().st_size/1_048_576 if ok else 0
        print(f"  {'OK' if ok else 'FAIL'} {v['id']}: {d_:.0f}s, {mb_:.1f}MB")
    shutil.rmtree(T, ignore_errors=True)

if __name__=="__main__": main()
