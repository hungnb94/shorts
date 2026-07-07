#!/usr/bin/env python3
"""
Viral Short Video Editor v4 — Production-grade stock_footage + kinetic captions.
2026 techniques: pattern interrupts, data overlays, kitty mascot, Ken Burns.

Pipeline:
  script def → TTS → select pexels clips → render frames (PIL) → ffmpeg encode
"""
import asyncio, edge_tts, json, math, random, shutil, subprocess, sys, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from collections import defaultdict

PROJECT = Path("/Users/hung/code/ai/shorts")
OUTDIR  = PROJECT / "output" / "viral_v4"
OUTDIR.mkdir(parents=True, exist_ok=True)
TMPDIR  = PROJECT / "output" / "tmp_v4"
TMPDIR.mkdir(parents=True, exist_ok=True)

PEXELS_DIR = PROJECT / "output" / "pexels"
OVERLAYS_DIR = PROJECT / "output" / "overlays"

WIDTH, HEIGHT, FPS = 1080, 1920, 30

# ── Colors ──
C_BLACK  = (0, 0, 0)
C_WHITE  = (255, 255, 255)
C_GOLD   = (255, 215, 0)
C_CYAN   = (0, 200, 255)
C_RED    = (255, 68, 68)
C_GREEN  = (0, 255, 136)
C_PURPLE = (180, 50, 255)
C_DARK   = (15, 15, 20)

FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
FONT_ARIAL = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
FONT_VI = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"  # Vietnamese diacriticals

# Voice map per language
TTS_VOICES = {
    "en": {"voice": "en-US-GuyNeural",   "rate": "+10%"},
    "vi": {"voice": "vi-VN-NamMinhNeural", "rate": "+0%"},
}

def font(size, path=FONT_BOLD, bold=True):
    size = max(1, int(size))
    try:
        return ImageFont.truetype(path, size, index=1 if bold else 0)
    except:
        return ImageFont.truetype(path, size)

def vi_font(size):
    """Font that renders Vietnamese diacriticals correctly."""
    return font(size, path=FONT_VI)

# ── Load pexels clips ──
PEXELS_CLIPS = sorted(PEXELS_DIR.glob("pex_*.mp4"))
print(f"📦 Loaded {len(PEXELS_CLIPS)} pexels clips")

def get_pexel_duration(path):
    r = subprocess.run(["ffprobe","-v","quiet","-show_entries","format=duration","-of","csv=p=0",str(path)],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)

PEXELS_INFO = [(p, get_pexel_duration(p)) for p in PEXELS_CLIPS]
PEXELS_POOL = [(p, d) for p, d in PEXELS_INFO if d >= 5]
print(f"  {len(PEXELS_POOL)} clips with >=5s duration")

# ── Kitty mascot ──
def make_kitty_overlay(size=120):
    """Create a cute cat mascot overlay (simple pixel-art style)."""
    s = size * 2  # retina
    img = Image.new("RGBA", (s, s), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    # Circle face
    face_color = (255, 200, 100, 255)
    draw.ellipse([s*0.1, s*0.05, s*0.9, s*0.85], fill=face_color)
    # Ears
    draw.polygon([(s*0.12, s*0.15), (s*0.25, s*0.02), (s*0.35, s*0.12)], fill=face_color)
    draw.polygon([(s*0.65, s*0.12), (s*0.75, s*0.02), (s*0.88, s*0.15)], fill=face_color)
    # Inner ears
    ear_col = (255, 150, 150, 255)
    draw.polygon([(s*0.16, s*0.14), (s*0.25, s*0.05), (s*0.32, s*0.13)], fill=ear_col)
    draw.polygon([(s*0.68, s*0.13), (s*0.75, s*0.05), (s*0.84, s*0.14)], fill=ear_col)
    # Eyes
    eye_col = (50, 50, 50, 255)
    draw.ellipse([s*0.25, s*0.25, s*0.43, s*0.43], fill=eye_col)
    draw.ellipse([s*0.57, s*0.25, s*0.75, s*0.43], fill=eye_col)
    # Eye shine
    shine = (255,255,255,230)
    draw.ellipse([s*0.30, s*0.28, s*0.38, s*0.36], fill=shine)
    draw.ellipse([s*0.62, s*0.28, s*0.70, s*0.36], fill=shine)
    # Nose
    draw.polygon([(s*0.45, s*0.48), (s*0.55, s*0.48), (s*0.50, s*0.55)], fill=(255,120,120,255))
    # Mouth
    draw.arc([s*0.35, s*0.48, s*0.50, s*0.62], 180, 360, fill=(80,40,40,255), width=max(1,s//30))
    draw.arc([s*0.50, s*0.48, s*0.65, s*0.62], 180, 360, fill=(80,40,40,255), width=max(1,s//30))
    # Whiskers
    wcol = (80, 40, 40, 180)
    for dx in [-1, 1]:
        cx = s*0.5 + dx*s*0.15
        cy = s*0.52
        draw.line([cx, cy, cx-dx*s*0.25, cy-s*0.08], fill=wcol, width=max(1,s//40))
        draw.line([cx, cy, cx-dx*s*0.25, cy], fill=wcol, width=max(1,s//40))
        draw.line([cx, cy, cx-dx*s*0.25, cy+s*0.08], fill=wcol, width=max(1,s//40))
    return img.resize((size, size), Image.Resampling.LANCZOS)

KITTY_OVERLAY = make_kitty_overlay(100)

# ── Scripts ──
SCRIPTS = [
    {
        "id": "v4_01_saving_poor",
        "hook": "SAVING MONEY IS MAKING YOU POOR",
        "hook_short": "Saving is making you poor?",
        "tts_text": (
            "Here is a truth the banks don't want you to know. "
            "Saving money in a regular account is literally making you poorer every single day. "
            "With inflation at 3.5 percent and your savings account earning 0.01 percent, "
            "you are losing 3.49 percent of your purchasing power annually. "
            "On ten thousand dollars, that is three hundred and forty nine dollars gone. "
            "Poof. Into thin air. "
            "The wealthy don't save. They invest. They buy assets that outpace inflation. "
            "Real estate. Stocks. Businesses. "
            "The average millionaire has seven streams of income. "
            "Not seven savings accounts. "
            "Stop saving your way to poverty."
        ),
        "cta": "Start investing. Your future self will thank you.",
        "stats": [
            ("$349/yr", "LOST on $10k savings"),
            ("3.5%", "Inflation rate 2026"),
            ("7×", "Income streams of millionaires"),
        ],
        "keywords": ["money", "wealth", "investment", "finance"],
    },
    {
        "id": "v4_02_nine_to_five_risk",
        "hook": "YOUR 9-5 IS THE RISKIEST BET",
        "hook_short": "Your job is the real gamble",
        "tts_text": (
            "Think having a job is safe? Think again. "
            "The average person will be fired or laid off seven times in their career. "
            "Seven times. And the average severance covers just two weeks of expenses. "
            "Meanwhile, over 40 million Americans have side hustles because they know "
            "one paycheck away from disaster is not a strategy. "
            "The rich have assets that work while they sleep. "
            "The middle class has a boss who can fire them with a two-week notice. "
            "That is not security. That is a leash. "
            "Real security isn't a steady paycheck. "
            "It is having multiple income streams that nobody can take away from you."
        ),
        "cta": "Build something on the side. Your job won't last forever.",
        "stats": [
            ("7×", "Times avg person gets fired"),
            ("40M+", "Americans with side hustles"),
            ("2 wks", "Average severance covers"),
        ],
        "keywords": ["business", "office", "entrepreneur", "startup"],
    },
    {
        "id": "v4_03_credit_card_rich",
        "hook": "CREDIT CARDS MAKE YOU RICHER",
        "hook_short": "Credit cards = wealth tool?",
        "tts_text": (
            "This sounds crazy but hear me out. "
            "Credit cards make you richer if you use them right. "
            "The top one percent collect over one thousand dollars per year in cashback and rewards. "
            "That is free money. But the average American pays over eight hundred dollars a year in interest "
            "because they carry a balance. "
            "See the difference? The rich use credit cards as tools. They pay them off every single month. "
            "They collect the rewards. They build their credit score to access cheaper loans. "
            "The poor use credit cards as crutches. They buy stuff they cannot afford "
            "and pay the bank twenty five percent interest. "
            "The card is not the problem. It is how you use it."
        ),
        "cta": "Use credit like the rich do. Pay it off. Every. Single. Month.",
        "stats": [
            ("$1,000+/yr", "Rewards for top 1%"),
            ("$800/yr", "Interest avg American pays"),
            ("25%", "Credit card interest rate"),
        ],
        "keywords": ["money", "credit", "finance", "business"],
    },
    {
        "id": "v4_04_rent_problem",
        "hook": "YOUR RENT IS THE REAL WEALTH KILLER",
        "hook_short": "Rent is destroying your wealth",
        "tts_text": (
            "Stop blaming avocado toast. Your rent is the real problem. "
            "The average renter spends thirty percent of their income on housing. "
            "That is money you will never see again. No equity. No asset. Nothing. "
            "Over thirty years, the average renter pays over seven hundred thousand dollars in rent. "
            "Imagine if that seven hundred thousand had been invested in the S&P 500. "
            "At ten percent average returns, that would be over four million dollars. "
            "Four million dollars you burned on a roof over your head. "
            "Real estate is the number one wealth builder in America. "
            "Homeowners have forty times the net worth of renters on average. "
            "The math is not complicated. Owning builds wealth. Renting builds your landlord's wealth."
        ),
        "cta": "Find a way to own. Even a small starter home builds equity.",
        "stats": [
            ("$700K+", "Rent paid over 30 years"),
            ("$4M+", "Lost investment potential"),
            ("40×", "Homeowner vs renter net worth"),
        ],
        "keywords": ["real estate", "house", "money", "investment"],
    },
    {
        "id": "v4_05_spend_more",
        "hook": "YOU SHOULD SPEND MORE MONEY",
        "hook_short": "Spending more = wealth?",
        "tts_text": (
            "Here is a mindset shift that changed my life. "
            "You should spend more money. But only on things that go up in value. "
            "The wealthy spend thirty percent of their income on assets. "
            "The average person spends less than five percent. "
            "When you buy a course that teaches you a high income skill, "
            "that money comes back to you ten times over. "
            "When you buy a watch, that money is gone. "
            "Warren Buffett still lives in the same house he bought in 1958 for thirty one thousand dollars. "
            "He spends money on stocks and businesses, not cars and clothes. "
            "The goal is not to hoard money. The goal is to deploy it where it works for you."
        ),
        "cta": "Spend on assets. Not on things that depreciate.",
        "stats": [
            ("30%", "Rich spend on assets"),
            ("<5%", "Avg person spends on assets"),
            ("10×", "Return on education investment"),
        ],
        "keywords": ["success", "wealth", "business", "investment"],
    },
    {
        "id": "v4_06_broke_choice",
        "hook": "BEING BROKE IS A CHOICE",
        "hook_short": "Is broke a choice?",
        "tts_text": (
            "I know this sounds harsh. But being broke is a choice. "
            "Not poverty. Poverty is systemic. Being broke is a temporary financial state. "
            "There are over one thousand four hundred self-made millionaires in America "
            "who started with nothing. Zero. Zip. "
            "The difference between them and everyone else is not IQ. "
            "It is not luck. It is financial education and discipline. "
            "The average millionaire reads twelve books a year. "
            "The average person reads zero after college. "
            "Financial literacy is the single biggest predictor of wealth. "
            "You cannot solve a money problem until you understand money. "
            "The information is free. YouTube. Books. Podcasts. "
            "The only thing stopping you is you."
        ),
        "cta": "Read one book on personal finance this week. Start with Rich Dad Poor Dad.",
        "stats": [
            ("1,400+", "Self-made millionaires from $0"),
            ("12/yr", "Books millionaires read"),
            ("0/yr", "Avg person reads (after college)"),
        ],
        "keywords": ["success", "education", "mindset", "wealth"],
    },
    # ── Vietnamese scripts ──
    {
        "id": "vi_01_tiet_kiem_ngheo",
        "hook": "TIẾT KIỆM ĐANG LÀM BẠN NGHÈO ĐI",
        "hook_short": "Tiết kiệm = nghèo?",
        "lang": "vi",
        "tts_text": (
            "Đây là sự thật mà ngân hàng không muốn bạn biết. "
            "Gửi tiết kiệm tài khoản thường thực sự đang làm bạn nghèo đi mỗi ngày. "
            "Với lạm phát 3.5 phần trăm và tài khoản tiết kiệm chỉ trả 0.01 phần trăm, "
            "bạn đang mất 3.49 phần trăm sức mua mỗi năm. "
            "Trên mười nghìn đô la, đó là ba trăm bốn mươi chín đô la bay mất. "
            "Không bao giờ quay lại. "
            "Người giàu không tiết kiệm. Họ đầu tư. Họ mua tài sản tăng giá nhanh hơn lạm phát. "
            "Bất động sản. Cổ phiếu. Doanh nghiệp. "
            "Người giàu trung bình có bảy nguồn thu nhập. "
            "Không phải bảy tài khoản tiết kiệm. "
            "Hãy ngừng tiết kiệm theo cách dẫn đến nghèo khổ."
        ),
        "cta": "Bắt đầu đầu tư. Tương lai bạn sẽ cảm ơn bạn.",
        "stats": [
            ("$349/năm", "Mất trên $10k tiết kiệm"),
            ("3.5%", "Tỷ lệ lạm phát 2026"),
            ("7×", "Nguồn thu nhập của người giàu"),
        ],
        "keywords": ["money", "wealth", "investment", "finance"],
    },
    {
        "id": "vi_02_lam_thue_rui_ro",
        "hook": "LÀM CÔNG ĂN LƯƠNG LÀ RỦI RO NHẤT",
        "hook_short": "Làm thuê là rủi ro?",
        "lang": "vi",
        "tts_text": (
            "Nghĩ rằng có việc làm là an toàn? Hãy suy nghĩ lại. "
            "Người trung bình sẽ bị sa thải hoặc cho thôi việc bảy lần trong sự nghiệp. "
            "Bảy lần. Và trợ cấp trung bình chỉ đủ chi phí hai tuần. "
            "Trong khi đó, hơn 40 triệu người Mỹ có nghề tay trái vì họ biết "
            "một khoản lương cách khủng hoảng hai tuần không phải là chiến lược. "
            "Người giàu có tài sản làm việc khi họ ngủ. "
            "Giới trung lưu có ông chủ có thể sa thải họ với thông báo hai tuần. "
            "Đó không phải là sự an toàn. Đó là một sợi dây xích. "
            "Sự an toàn thực sự không phải là khoản lương ổn định. "
            "Đó là có nhiều nguồn thu nhập mà không ai có thể lấy đi."
        ),
        "cta": "Xây dựng thứ gì đó bên cạnh. Việc làm của bạn sẽ không tồn tại mãi.",
        "stats": [
            ("7×", "Lần trung bình bị sa thải"),
            ("40M+", "Người Mỹ có nghề tay trái"),
            ("2 tuần", "Trợ cấp trung bình"),
        ],
        "keywords": ["business", "office", "entrepreneur", "startup"],
    },
]

# ── Load overlays ──
OVERLAY_CACHE = {}
for p in OVERLAYS_DIR.glob("*.png"):
    OVERLAY_CACHE[p.stem] = Image.open(p).convert("RGBA")

def get_overlay(name):
    return OVERLAY_CACHE.get(name)

# ════════════════════════════════════════════════════════════
# RENDERER
# ════════════════════════════════════════════════════════════

async def gen_tts(text, out_path, voice=None, rate=None, lang="en"):
    """Generate TTS, return (path, duration_sec). Voice/rate auto-selected by lang if not given."""
    if voice is None:
        cfg = TTS_VOICES.get(lang, TTS_VOICES["en"])
        voice = cfg["voice"]
    if rate is None:
        cfg = TTS_VOICES.get(lang, TTS_VOICES["en"])
        rate = cfg["rate"]
    comm = edge_tts.Communicate(text, voice, rate=rate)
    await comm.save(str(out_path))
    r = subprocess.run(["ffprobe","-v","quiet","-show_entries","format=duration","-of","csv=p=0",str(out_path)],
                       capture_output=True, text=True)
    dur = float(r.stdout.strip() or 0)
    return out_path, dur

def select_pexels_for_duration(target_dur, keywords=None):
    """Select pexels clips to cover target_dur. Returns list of (path, segment_start, segment_end)."""
    random.seed(42)  # deterministic
    pool = list(PEXELS_POOL)
    random.shuffle(pool)
    
    if keywords:
        # Try to find clips whose filename matches keywords
        kw_pool = [p for p in pool if any(k in str(p).lower() for k in keywords)]
        if kw_pool:
            pool = kw_pool + pool  # prefer keyword matches
    
    clips = []
    remaining = target_dur + 2
    while remaining > 3 and pool:
        clip_path, clip_dur = pool.pop(0)
        seg_dur = min(clip_dur, remaining)
        clips.append((clip_path, clip_dur))
        remaining -= seg_dur
        if remaining < 3:
            break
    
    if not clips:
        # Fallback to first clip, loop it
        clips = [(PEXELS_POOL[0][0], PEXELS_POOL[0][1])]
    
    return clips

def extract_frames(clip_path, total_dur, out_dir):
    """Extract all frames from a clip at 30fps, cropped to 9:16."""
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y", "-i", str(clip_path),
        "-vf", f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT},fps={FPS}",
        "-an", "-q:v", "2", "-frames:v", str(int(total_dur * FPS)),
        str(out_dir / "f_%05d.jpg")
    ], capture_output=True)
    frames = sorted(out_dir.glob("f_*.jpg"))
    return frames

def ease_out_cubic(t):
    return 1 - (1 - max(0, min(1, t))) ** 3

def ease_out_bounce(t):
    t = max(0, min(1, t))
    if t < 1/2.75: return 7.5625*t*t
    elif t < 2/2.75: return 7.5625*(t-1.5/2.75)*(t-1.5/2.75)+0.75
    elif t < 2.5/2.75: return 7.5625*(t-2.25/2.75)*(t-2.25/2.75)+0.9375
    else: return 7.5625*(t-2.625/2.75)*(t-2.625/2.75)+0.984375

async def render_video(script, idx):
    """Render one full video from script definition."""
    vid_id = script["id"]
    lang = script.get("lang", "en")
    print(f"\n{'='*70}")
    print(f"🎬 [{idx}/6] {vid_id}")
    print(f"   Hook: {script['hook']}")
    
    vid_dir = TMPDIR / vid_id
    vid_dir.mkdir(parents=True, exist_ok=True)
    
    # ── 1. Generate TTS ──
    print(f"   🎙 Generating TTS...")
    tts_path = vid_dir / "tts.mp3"
    tts_path, tts_dur = await gen_tts(script["tts_text"], tts_path, lang=lang)
    print(f"      TTS duration: {tts_dur:.1f}s ({len(script['tts_text'].split())} words)")
    
    total_dur = max(30, min(60, tts_dur + 3.5))  # pad for hook + CTA
    if tts_dur < 27:
        # Pad with silence if too short
        pad_dur = 30 - tts_dur
        print(f"      Padding with {pad_dur:.1f}s silence (min 30s)")
        pad_path = vid_dir / "pad.wav"
        subprocess.run(["ffmpeg","-y","-f","lavfi","-i",f"anullsrc=duration={pad_dur}","-ac","1","-ar","44100",str(pad_path)], capture_output=True)
        # Merge
        merged = vid_dir / "tts_padded.mp3"
        subprocess.run(["ffmpeg","-y","-i",str(tts_path),"-i",str(pad_path),
                       "-filter_complex","[0:a][1:a]concat=n=2:v=0:a=1",str(merged)], capture_output=True)
        tts_path = merged
        total_dur = tts_dur + pad_dur
    elif tts_dur > 58:
        # Trim to 58s max
        trimmed = vid_dir / "tts_trimmed.mp3"
        subprocess.run(["ffmpeg","-y","-i",str(tts_path),"-t","58",str(trimmed)], capture_output=True)
        tts_path = trimmed
        total_dur = 58
    
    print(f"      Final duration: {total_dur:.1f}s")
    
    # ── 2. Select and extract stock footage ──
    print(f"   🎬 Preparing stock footage...")
    pexels_selected = select_pexels_for_duration(total_dur, script.get("keywords"))
    print(f"      Selected {len(pexels_selected)} clips")
    
    # Extract frames from each clip, then interleave
    all_src_frames = []
    clip_frame_counts = []
    for ci, (cp, cd) in enumerate(pexels_selected):
        clip_dir = vid_dir / f"src_{ci}"
        frames = extract_frames(cp, cd, clip_dir)
        clip_frame_counts.append(len(frames))
        all_src_frames.extend(frames)
        print(f"      Clip {ci}: {cd:.1f}s → {len(frames)} frames")
    
    if not all_src_frames:
        # Fallback: black frames
        all_src_frames = None
    
    total_frames = int(total_dur * FPS)
    src_count = len(all_src_frames) if all_src_frames else 0
    
    # ── 3. Create background music (simple ambient) ──
    # We'll use ffmpeg's audio filter to add a subtle bg music
    # Actually, let's skip music for now to avoid complexity
    
    # ── 4. Render frames ──
    print(f"   🎨 Rendering {total_frames} frames...")
    frames_dir = vid_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    
    # Split TTS text into words for caption timing
    words = script["tts_text"].split()
    n_words = len(words)
    words_per_sec = n_words / tts_dur if tts_dur > 0 else 3
    
    # Stats timing
    stats = script.get("stats", [])
    
    # Pre-select fonts based on language
    use_vi = (lang == "vi")
    HOOK_FONT  = FONT_VI if use_vi else FONT_ARIAL
    STAT_FONT  = FONT_VI if use_vi else FONT_ARIAL
    CAPTION_FONT = FONT_VI if use_vi else FONT_ARIAL
    
    # Kitty bounce animation
    kitty_bounce_frames = []
    for ki in range(60):  # precompute 60 bounce frames
        progress = ki / 20.0
        bounce_y = int(10 * math.sin(progress * math.pi * 2))
        kitty_bounce_frames.append(bounce_y)
    
    for fi in range(total_frames):
        t = fi / FPS
        progress = t / total_dur
        
        # ── Select source frame ──
        if all_src_frames:
            src_idx = min(int((t / total_dur) * src_count), src_count - 1)
            bg = Image.open(all_src_frames[src_idx]).convert("RGB").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        else:
            bg = Image.new("RGB", (WIDTH, HEIGHT), C_DARK)
        
        # Darken slightly for text readability
        overlay = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        bg = Image.blend(bg, overlay, 0.30)
        
        # ── Ken Burns slow zoom ──
        zoom = 1.0 + 0.02 * min(1.0, progress * 2)
        bw, bh = int(WIDTH / zoom), int(HEIGHT / zoom)
        bx = (WIDTH - bw) // 2
        by = int((HEIGHT - bh) * 0.15 * (t % 5 / 5))
        bg = bg.crop((bx, by, bx + bw, by + bh)).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        
        draw = ImageDraw.Draw(bg, "RGBA")
        
        # ── Hook (first 3s) ──
        if t < 3.0:
            hook_progress = min(1.0, t / 0.4)
            hook_scale = max(1, int(58 * hook_progress))
            fo = font(hook_scale, HOOK_FONT)
            hook_text = script["hook"]
            bbox = draw.textbbox((0, 0), hook_text, font=fo)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            # Background pill
            pill_w = tw + 80
            pill_h = th + 40
            pill_x = (WIDTH - pill_w) // 2
            pill_y = HEIGHT * 0.25
            draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h],
                                   radius=24, fill=(0, 0, 0, 200))
            draw.text(((WIDTH - tw) // 2, pill_y + 20), hook_text, font=fo, fill=C_GOLD)
        
        # ── Stats data viz (show each stat at its time window) ──
        if stats:
            n_stats = len(stats)
            for si, (big_num, label) in enumerate(stats):
                stat_start = 3.0 + si * (total_dur - 4.0) / n_stats
                stat_end = stat_start + (total_dur - 4.0) / n_stats * 0.7
                if stat_start <= t < stat_end:
                    local_t = t - stat_start
                    stat_window = stat_end - stat_start
                    fade_in = min(1.0, local_t / 0.3)
                    scale = min(1.0, local_t * 3)
                    
                    # Big number
                    num_fnt = font(int(120 * scale), STAT_FONT)
                    label_fnt = font(int(28 * scale))
                    
                    # Background
                    draw.rounded_rectangle([60, 280, WIDTH - 60, 500],
                                           radius=20, fill=(0, 0, 0, int(200 * fade_in)))
                    
                    nb = draw.textbbox((0, 0), big_num, font=num_fnt)
                    nw = nb[2] - nb[0]
                    draw.text(((WIDTH - nw) // 2, 295), big_num, font=num_fnt,
                              fill=C_GOLD + (int(255 * fade_in),))
                    
                    lb = draw.textbbox((0, 0), label, font=label_fnt)
                    lw = lb[2] - lb[0]
                    draw.text(((WIDTH - lw) // 2, 420), label, font=label_fnt,
                              fill=C_WHITE + (int(200 * fade_in),))
        
        # ── Kinetic captions (word-by-word, bottom 1/3) ──
        # Find which words have been spoken by this point
        words_spoken = int(t * words_per_sec)
        # Show last 6-8 words in a scroll
        window_start = max(0, words_spoken - 7)
        visible_words = words[window_start:words_spoken + 2]
        
        if visible_words:
            # Group into lines (max ~8 chars per word, ~4 words per line)
            caption_lines = []
            cur_line = []
            cur_chars = 0
            for w in visible_words:
                cur_line.append(w)
                cur_chars += len(w)
                if cur_chars > 20 or len(cur_line) >= 5:
                    caption_lines.append(cur_line)
                    cur_line = []
                    cur_chars = 0
            if cur_line:
                caption_lines.append(cur_line)
            
            # Background box for captions
            line_heights = 66
            total_box_h = len(caption_lines) * line_heights + 30
            box_y = HEIGHT - total_box_h - 120
            
            draw.rounded_rectangle([40, box_y, WIDTH - 40, box_y + total_box_h],
                                   radius=16, fill=(0, 0, 0, 200))
            
            # Sub-word index tracking
            word_idx_in_visible = 0
            for li, line_words in enumerate(caption_lines):
                for wi, word in enumerate(line_words):
                    global_word_idx = window_start + word_idx_in_visible
                    word_t = t - global_word_idx / words_per_sec
                    word_progress = max(0, min(1, word_t * 2))  # fade in over 0.5s
                    
                    if word_progress <= 0:
                        word_idx_in_visible += 1
                        continue
                    
                    scale = ease_out_cubic(word_progress)
                    caption_fnt = font(int(48 * max(0.01, scale)), CAPTION_FONT)
                    
                    # Word color: highlight money-related words in gold
                    is_money_word = any(sym in word for sym in ["$", "%", "×", "million", "thousand", "billion", "%"])
                    word_color = C_GOLD if is_money_word else C_WHITE
                    
                    bbox = draw.textbbox((0, 0), word, font=caption_fnt)
                    tw = bbox[2] - bbox[0]
                    
                    # Calculate x position: center the entire line, then position this word
                    line_str = " ".join(line_words)
                    lb = draw.textbbox((0, 0), line_str, font=font(48, CAPTION_FONT))
                    line_w = lb[2] - lb[0]
                    
                    prefix = " ".join(line_words[:wi]) + (" " if wi > 0 else "")
                    pb = draw.textbbox((0, 0), prefix, font=font(48, CAPTION_FONT))
                    prefix_w = pb[2] - pb[0]
                    
                    x = (WIDTH - line_w) // 2 + prefix_w
                    y = box_y + 20 + li * line_heights
                    
                    alpha = int(255 * min(1.0, word_progress + 0.3))
                    draw.text((x, y), word, font=caption_fnt, fill=word_color + (alpha,))
                    
                    word_idx_in_visible += 1
        
        # ── Kitty mascot (top-right corner, subtle bounce) ──
        kitty_x = WIDTH - KITTY_OVERLAY.width - 20
        kitty_y = 30 + (kitty_bounce_frames[fi % len(kitty_bounce_frames)] if kitty_bounce_frames else 0)
        # Subtle fade in/out at edges
        kitty_alpha = 220
        if t < 1.0:
            kitty_alpha = int(220 * t)
        elif t > total_dur - 1.5:
            kitty_alpha = int(220 * (total_dur - t) / 1.5)
        
        if kitty_alpha > 0:
            kitty = KITTY_OVERLAY.copy()
            kitty.putalpha(int(255 * kitty_alpha / 220))
            bg.paste(kitty, (kitty_x, kitty_y), kitty)
        
        # ── Pattern interrupt: flash at key moments ──
        # Flash when stats change or at punchline moments
        punchline_times = set()
        if stats:
            for si in range(len(stats)):
                pt = 3.0 + si * (total_dur - 4.0) / len(stats)
                punchline_times.add(pt)
        punchline_times.add(total_dur * 0.5)  # mid-point flash
        
        for pt in punchline_times:
            dt = t - pt
            if 0 <= dt < 0.15:
                flash_alpha = int(60 * (1 - dt / 0.15))
                flash = Image.new("RGBA", (WIDTH, HEIGHT), C_CYAN + (flash_alpha,))
                bg.paste(flash, (0, 0), flash)
        
        # ── Progress bar (thin line at bottom) ──
        bar_width = int(WIDTH * t / total_dur)
        draw.rectangle([0, HEIGHT - 6, bar_width, HEIGHT], fill=C_CYAN + (200,))
        
        # ── Time code watermark (subtle branding) ──
        if fi % 10 == 0:
            tc_fnt = font(16)
            tc = f"{int(t//60):02d}:{int(t%60):02d}"
            draw.text((WIDTH - 70, HEIGHT - 30), tc, font=tc_fnt, fill=(255, 255, 255, 60))
        
        # Save frame
        bg.save(frames_dir / f"f_{fi:05d}.png")
        
        if fi % 300 == 0:
            print(f"      Frame {fi}/{total_frames} ({100*fi//total_frames}%)")
    
    # ── 5. Encode to MP4 ──
    print(f"   🎞 Encoding video...")
    out_path = OUTDIR / f"{vid_id}.mp4"
    temp_video = vid_dir / "video.mp4"
    
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS), "-i", str(frames_dir / "f_%05d.png"),
        "-i", str(tts_path),
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-crf", "17", "-profile:v", "high", "-level", "4.1",
        "-c:a", "aac", "-b:a", "128k", "-shortest",
        "-movflags", "+faststart",
        str(temp_video)
    ], capture_output=True)
    
    # ── 6. Verify and copy ──
    # Rename
    temp_video.rename(out_path)
    
    r = subprocess.run(["ffprobe","-v","quiet","-show_entries","format=duration,size","-of","csv=p=0",str(out_path)],
                       capture_output=True, text=True)
    parts = r.stdout.strip().split(",")
    final_dur = float(parts[0]) if parts else 0
    size_mb = out_path.stat().st_size / 1024 / 1024
    
    # Verify specs
    verify = subprocess.run([
        "ffprobe", "-v", "quiet", "-show_entries",
        "stream=width,height,codec_name", "-of", "csv=p=0", str(out_path)
    ], capture_output=True, text=True)
    
    print(f"   ✅ {out_path.name}")
    print(f"      Duration: {final_dur:.1f}s | Size: {size_mb:.1f}MB")
    print(f"      Streams: {verify.stdout.strip()}")
    
    # Cleanup frames
    shutil.rmtree(frames_dir, ignore_errors=True)
    shutil.rmtree(vid_dir / "src_0", ignore_errors=True)
    shutil.rmtree(vid_dir / "src_1", ignore_errors=True)
    shutil.rmtree(vid_dir / "src_2", ignore_errors=True)
    
    return out_path, final_dur, size_mb

# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════

async def main():
    print("=" * 70)
    print("🎥 VIRAL SHORT VIDEO FACTORY v4 — 2026 EDITION")
    print(f"   Output: {OUTDIR}")
    print(f"   {len(SCRIPTS)} scripts to render")
    print("=" * 70)
    
    results = []
    for i, script in enumerate(SCRIPTS, 1):
        try:
            path, dur, mb = await render_video(script, i)
            ok = "✅" if 28 <= dur <= 62 else "⚠️"
            results.append((script["id"], dur, mb, ok))
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            results.append((script["id"], 0, 0, f"❌ {e}"))
    
    print(f"\n{'='*70}")
    print(f"📊 FINAL RESULTS:")
    print(f"{'='*70}")
    for name, dur, mb, status in results:
        spec = "✅" if 28 <= dur <= 62 else "❌"
        hook = next((s["hook"] for s in SCRIPTS if s["id"] == name), "")
        print(f"  {status} {name}")
        print(f"     {dur:.1f}s | {mb:.1f}MB | {hook}")
    print(f"\n📁 All videos in: {OUTDIR}")

if __name__ == "__main__":
    asyncio.run(main())
