#!/usr/bin/env python3
"""
ASCII Love Story v3: Maximum Detail
Draw vector 1000x1000 → sample to 120x160 grid (19,200 cells)
25-char density ramp + pre-rendered character images
Vietnamese TTS, 1080x1920
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, subprocess, asyncio, edge_tts, math

OUTPUT = "/Users/hung/code/ai/shorts/output/ascii_love_v3"
FRAMES_DIR = os.path.join(OUTPUT, "frames")
AUDIO_DIR = os.path.join(OUTPUT, "audio")
os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 24

# Fonts
VI_FONT = "/Library/Fonts/Arial Unicode.ttf"
VI_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
MONO = "/System/Library/Fonts/Menlo.ttc"

def get_font(path, size):
    try: return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

BLOCK = '\u2588'

# ============================================================
# 25-char density ramp (bright → dark)
# ============================================================
DENSITY_RAMP = " .·∘●◎◉-o*+~%#@█"
# Extended with special chars for texture
RAMP_CHARS = list(DENSITY_RAMP)

# ============================================================
# COLORS
# ============================================================
SKIN      = (240, 205, 175)
SKIN_D    = (210, 170, 140)
HAIR_BK   = (25, 20, 30)
HAIR_SH   = (55, 45, 65)
LIPS      = (195, 75, 75)
LIPS_L    = (215, 100, 100)
EYE_W     = (240, 240, 245)
EYE_IRIS  = (65, 110, 170)
EYE_PUP   = (15, 12, 22)
EYE_LASH  = (18, 14, 24)
BLUSH     = (230, 165, 155)
BROW      = (35, 28, 38)

DRESS_P   = (215, 105, 150)
DRESS_L   = (235, 155, 185)
DRESS_D   = (185, 80, 125)
DRESS_HL  = (245, 185, 205)

SUIT_D    = (20, 20, 38)
SUIT_L    = (45, 45, 68)
SHIRT     = (230, 230, 235)
TIE       = (170, 35, 35)
TIE_L     = (200, 60, 60)
BELT_G    = (200, 175, 50)
SHOE      = (35, 30, 42)

BG = (8, 8, 14)
PINK_GLOW = (255, 150, 180)
GOLD      = (255, 215, 0)
WHITE     = (255, 255, 255)
DIM       = (100, 100, 120)

# ============================================================
# VECTOR DRAWING — Woman (1000x1000)
# ============================================================
def draw_woman():
    img = Image.new("RGB", (1000, 1000), BG)
    d = ImageDraw.Draw(img)
    cx = 500

    # Hair behind head
    d.ellipse([cx-185, 120, cx+185, 420], fill=HAIR_BK)
    d.polygon([(cx-180,250),(cx-210,350),(cx-220,500),(cx-200,600),
               (cx-170,650),(cx-150,550),(cx-160,400),(cx-170,300)], fill=HAIR_BK)
    d.polygon([(cx+180,250),(cx+210,350),(cx+220,500),(cx+200,600),
               (cx+170,650),(cx+150,550),(cx+160,400),(cx+170,300)], fill=HAIR_BK)
    d.arc([cx-100,130,cx+100,300], 200, 340, fill=HAIR_SH, width=3)

    # Neck
    d.polygon([(cx-45,370),(cx+45,370),(cx+50,440),(cx-50,440)], fill=SKIN)
    d.polygon([(cx-40,370),(cx+40,370),(cx+35,395),(cx-35,395)], fill=SKIN_D)

    # Face
    d.ellipse([cx-155,170,cx+155,410], fill=SKIN)
    d.polygon([(cx-140,310),(cx-100,390),(cx,410),(cx+100,390),(cx+140,310)], fill=SKIN)
    d.ellipse([cx-135,310,cx-60,370], fill=BLUSH)
    d.ellipse([cx+60,310,cx+135,370], fill=BLUSH)

    # Bangs
    d.polygon([(cx-155,200),(cx-130,170),(cx-50,190),(cx,180),(cx+50,190),
               (cx+130,170),(cx+155,200),(cx+145,260),(cx+80,240),(cx,250),
               (cx-80,240),(cx-145,260)], fill=HAIR_BK)
    d.polygon([(cx-155,200),(cx-175,220),(cx-180,300),(cx-170,270),(cx-155,240)], fill=HAIR_BK)
    d.polygon([(cx+155,200),(cx+175,220),(cx+180,300),(cx+170,270),(cx+155,240)], fill=HAIR_BK)

    # Eyes
    for ex in [cx-75, cx+75]:
        d.ellipse([ex-40,275,ex+40,325], fill=EYE_W)
        d.ellipse([ex-22,280,ex+22,320], fill=EYE_IRIS)
        d.ellipse([ex-10,290,ex+10,310], fill=EYE_PUP)
        d.ellipse([ex-5,285,ex+5,295], fill=(255,255,255))
        d.arc([ex-42,273,ex+42,327], 190, 340, fill=EYE_LASH, width=4)
        d.arc([ex-35,280,ex+35,330], 10, 170, fill=EYE_LASH, width=2)

    # Brows
    d.arc([cx-115,250,cx-35,290], 200, 340, fill=BROW, width=3)
    d.arc([cx+35,250,cx+115,290], 200, 340, fill=BROW, width=3)

    # Nose
    d.polygon([(cx-8,330),(cx+8,330),(cx+12,365),(cx-12,365)], fill=SKIN_D)
    d.arc([cx-15,355,cx+15,375], 0, 180, fill=SKIN_D, width=2)

    # Lips
    d.polygon([(cx-35,385),(cx-15,378),(cx,382),(cx+15,378),(cx+35,385),(cx,392)], fill=LIPS)
    d.ellipse([cx-30,388,cx+30,410], fill=LIPS_L)

    # Dress — S-curve
    d.polygon([(cx-200,440),(cx+200,440),(cx+180,490),(cx-180,490)], fill=DRESS_P)
    d.polygon([(cx-190,480),(cx+190,480),(cx+210,580),(cx-210,580)], fill=DRESS_P)
    d.ellipse([cx-210,500,cx-50,600], fill=DRESS_L)
    d.ellipse([cx+50,500,cx+210,600], fill=DRESS_L)
    d.polygon([(cx-210,570),(cx+210,570),(cx+100,670),(cx-100,670)], fill=DRESS_P)
    d.polygon([(cx-130,620),(cx+130,620),(cx+110,650),(cx-110,650)], fill=DRESS_D)
    d.polygon([(cx-100,660),(cx+100,660),(cx+220,760),(cx-220,760)], fill=DRESS_P)
    d.ellipse([cx-230,680,cx-30,780], fill=DRESS_L)
    d.ellipse([cx+30,680,cx+230,780], fill=DRESS_L)
    d.polygon([(cx-220,750),(cx+220,750),(cx+250,920),(cx-250,920)], fill=DRESS_P)
    d.polygon([(cx-180,770),(cx-100,770),(cx-120,900),(cx-200,900)], fill=DRESS_D)
    d.polygon([(cx+100,770),(cx+180,770),(cx+200,900),(cx+120,900)], fill=DRESS_D)
    d.polygon([(cx-30,760),(cx+30,760),(cx+50,910),(cx-50,910)], fill=DRESS_HL)

    # Arms
    d.polygon([(cx-195,450),(cx-230,460),(cx-250,600),(cx-230,610),(cx-200,500)], fill=SKIN)
    d.polygon([(cx+195,450),(cx+230,460),(cx+250,600),(cx+230,610),(cx+200,500)], fill=SKIN)
    d.ellipse([cx-260,590,cx-220,640], fill=SKIN)
    d.ellipse([cx+220,590,cx+260,640], fill=SKIN)

    # Shoes
    d.ellipse([cx-120,910,cx-50,950], fill=SHOE)
    d.ellipse([cx+50,910,cx+120,950], fill=SHOE)

    return img

# ============================================================
# VECTOR DRAWING — Man (1000x1000)
# ============================================================
def draw_man():
    img = Image.new("RGB", (1000, 1000), BG)
    d = ImageDraw.Draw(img)
    cx = 500

    # Suit shoulders
    d.polygon([(cx-230,450),(cx+230,450),(cx+220,500),(cx-220,500)], fill=SUIT_D)

    # Neck
    d.polygon([(cx-55,370),(cx+55,370),(cx+60,440),(cx-60,440)], fill=SKIN)
    d.polygon([(cx-45,370),(cx+45,370),(cx+40,400),(cx-40,400)], fill=SKIN_D)

    # Face (square jaw)
    d.ellipse([cx-160,170,cx+160,420], fill=SKIN)
    d.polygon([(cx-150,310),(cx-120,380),(cx-60,420),(cx,430),
               (cx+60,420),(cx+120,380),(cx+150,310)], fill=SKIN)
    d.polygon([(cx-120,380),(cx-60,420),(cx,430),(cx+60,420),(cx+120,380),
               (cx+80,400),(cx,415),(cx-80,400)], fill=SKIN_D)

    # Hair
    d.ellipse([cx-165,140,cx+165,310], fill=HAIR_BK)
    d.polygon([(cx-160,200),(cx-130,145),(cx-50,135),(cx,130),(cx+50,135),
               (cx+130,145),(cx+160,200),(cx+155,230),(cx+80,215),(cx,220),
               (cx-80,215),(cx-155,230)], fill=HAIR_BK)
    d.arc([cx-120,140,cx+120,230], 200, 340, fill=HAIR_SH, width=3)
    d.polygon([(cx-160,200),(cx-180,220),(cx-185,310),(cx-175,280),(cx-160,240)], fill=HAIR_BK)
    d.polygon([(cx+160,200),(cx+180,220),(cx+185,310),(cx+175,280),(cx+160,240)], fill=HAIR_BK)

    # Eyes
    for ex in [cx-80, cx+80]:
        d.ellipse([ex-38,278,ex+38,318], fill=EYE_W)
        d.ellipse([ex-20,282,ex+20,314], fill=(50,80,50))
        d.ellipse([ex-9,292,ex+9,308], fill=EYE_PUP)
        d.ellipse([ex-4,286,ex+4,294], fill=(255,255,255))
        d.arc([ex-40,275,ex+40,320], 195, 345, fill=EYE_LASH, width=5)
        d.arc([ex-30,282,ex+30,318], 15, 165, fill=EYE_LASH, width=2)

    # Brows
    d.polygon([(cx-120,258),(cx-40,252),(cx-38,264),(cx-118,270)], fill=BROW)
    d.polygon([(cx+40,252),(cx+120,258),(cx+118,270),(cx+38,264)], fill=BROW)

    # Nose
    d.polygon([(cx-10,325),(cx+10,325),(cx+15,370),(cx-15,370)], fill=SKIN_D)
    d.arc([cx-18,360,cx+18,380], 0, 180, fill=SKIN_D, width=3)

    # Mouth
    d.arc([cx-35,388,cx+35,410], 10, 170, fill=LIPS, width=3)
    d.polygon([(cx-25,395),(cx+25,395),(cx+20,402),(cx-20,402)], fill=LIPS)

    # Shirt collar + tie
    d.polygon([(cx-55,435),(cx-30,430),(cx,460),(cx+30,430),(cx+55,435),
               (cx+40,490),(cx,510),(cx-40,490)], fill=SHIRT)
    d.polygon([(cx-55,435),(cx-80,450),(cx-60,470),(cx-40,445)], fill=SHIRT)
    d.polygon([(cx+55,435),(cx+80,450),(cx+60,470),(cx+40,445)], fill=SHIRT)
    d.polygon([(cx-15,460),(cx+15,460),(cx+10,700),(cx-10,700)], fill=TIE)
    d.polygon([(cx-15,460),(cx+15,460),(cx+8,480),(cx-8,480)], fill=TIE_L)
    d.polygon([(cx-12,448),(cx+12,448),(cx+8,465),(cx-8,465)], fill=TIE_L)

    # Suit
    d.polygon([(cx-230,450),(cx-55,435),(cx-40,490),(cx-50,700),(cx-240,710)], fill=SUIT_D)
    d.polygon([(cx+230,450),(cx+55,435),(cx+40,490),(cx+50,700),(cx+240,710)], fill=SUIT_D)
    d.polygon([(cx-55,435),(cx-80,450),(cx-70,550),(cx-50,500)], fill=SUIT_L)
    d.polygon([(cx+55,435),(cx+80,450),(cx+70,550),(cx+50,500)], fill=SUIT_L)

    # Belt
    d.rectangle([cx-130,690,cx+130,715], fill=SUIT_D)
    d.rectangle([cx-20,690,cx+20,715], fill=BELT_G)

    # Trousers
    d.polygon([(cx-130,710),(cx-10,710),(cx-30,950),(cx-110,950)], fill=SUIT_D)
    d.polygon([(cx+10,710),(cx+130,710),(cx+110,950),(cx+30,950)], fill=SUIT_D)
    d.line([(cx-70,720),(cx-70,940)], fill=SUIT_L, width=2)
    d.line([(cx+70,720),(cx+70,940)], fill=SUIT_L, width=2)

    # Shoes
    d.ellipse([cx-120,935,cx-40,975], fill=SHOE)
    d.ellipse([cx+40,935,cx+120,975], fill=SHOE)

    # Arms
    d.polygon([(cx-225,460),(cx-260,470),(cx-270,680),(cx-240,690),(cx-210,550)], fill=SUIT_D)
    d.polygon([(cx+225,460),(cx+260,470),(cx+270,680),(cx+240,690),(cx+210,550)], fill=SUIT_D)
    d.ellipse([cx-280,670,cx-235,720], fill=SKIN)
    d.ellipse([cx+235,670,cx+280,720], fill=SKIN)

    return img


# ============================================================
# HIGH-DETAIL VECTOR → ASCII CONVERSION
# ============================================================
def vector_to_ascii_img(source, grid_cols, grid_rows, cell_render=6):
    """Convert vector image to HIGH-DETAIL ASCII art.
    Uses █ (full block) for every visible pixel — maximum visual density.
    Returns a PIL Image."""
    sw, sh = source.size
    pixels = source.load()
    out_w = grid_cols * cell_render
    out_h = grid_rows * cell_render
    cell_w = sw / grid_cols
    cell_h = sh / grid_rows

    out = Image.new("RGB", (out_w, out_h), BG)
    draw = ImageDraw.Draw(out)
    font = get_font(MONO, cell_render)

    for gy in range(grid_rows):
        for gx in range(grid_cols):
            sx = min(int(gx * cell_w + cell_w / 2), sw - 1)
            sy = min(int(gy * cell_h + cell_h / 2), sh - 1)
            r, g, b = pixels[sx, sy]

            # Skip background
            if r < 20 and g < 20 and b < 25:
                continue

            # Full block for maximum density
            draw.text((gx * cell_render, gy * cell_render), BLOCK,
                      fill=(r, g, b), font=font)

    return out


# ============================================================
# SCENES
# ============================================================
SCENES = [
    {
        "title": "CHƯƠNG 1", "character": "woman",
        "caption": "Ngày đó, Linh là cô gái đẹp nhất thành phố.",
        "tts": "Ngày đó, Linh là cô gái đẹp nhất thành phố. Vẻ đẹp không chỉ ở khuôn mặt, mà còn ở trái tim nhân hậu.",
        "bg": "hearts",
    },
    {
        "title": "CHƯƠNG 2", "character": "man",
        "caption": "Còn Dũng là tổng tài giàu nhất thành phố.",
        "tts": "Còn Dũng là tổng tài giàu nhất thành phố. Anh có tất cả, trừ một điều: tình yêu thực sự.",
        "bg": "sparkle",
    },
    {
        "title": "CHƯƠNG 3", "title_color": PINK_GLOW, "character": "both",
        "caption": "Họ gặp nhau tại bữa tiệc đêm đó...",
        "tts": "Họ gặp nhau tại bữa tiệc đêm đó. Ánh mắt lần đầu chạm nhau, cả thế giới như dừng lại.",
        "bg": "sparkle",
    },
    {
        "title": "CHƯƠNG 4", "title_color": PINK_GLOW, "character": "both",
        "caption": "Không tiền bạc, không địa vị. Chỉ có hai trái tim.",
        "tts": "Không tiền bạc, không địa vị. Chỉ có hai trái tim rung động. Tình yêu không cần vật chất.",
        "bg": "hearts",
    },
    {
        "title": "CHƯƠNG 5", "title_color": GOLD, "character": "man",
        "caption": "Dũng quyết định bỏ lại tất cả.",
        "tts": "Dũng quyết định bỏ lại tất cả. Đế chế tiền bạc không bằng nụ cười của cô ấy.",
        "bg": "sparkle",
    },
    {
        "title": "CHƯƠNG 6", "title_color": DRESS_P, "character": "woman",
        "caption": "Linh chờ đợi một tình yêu chân thật.",
        "tts": "Linh chờ đợi một tình yêu chân thật. Không phải vì anh giàu, mà vì anh hiểu trái tim cô.",
        "bg": "hearts",
    },
    {
        "title": "CHƯƠNG 7", "title_color": PINK_GLOW, "character": "both",
        "caption": "Hai đường cong gặp nhau tại đỉnh.",
        "tts": "Hai đường cong cuộc đời gặp nhau tại đỉnh. Từ nay, không còn đơn độc.",
        "bg": "hearts",
    },
    {
        "title": "PHẦN KẾT", "title_color": GOLD, "character": "both",
        "caption": "TÌNH YÊU KHÔNG CÓ GIÁ.",
        "tts": "Tình yêu không có giá. Nhưng không có nó, mọi thứ đều có giá. Từ hai, thành một. Không gì là không thể.",
        "bg": "hearts",
    },
]

# ============================================================
# BACKGROUND EFFECTS
# ============================================================
def draw_hearts(draw, t, alpha=0.3):
    for i in range(15):
        x = (i * 83 + int(t * 25)) % W
        y = (i * 131 + int(t * 18)) % H
        s = 10 + (i % 4) * 4
        a = int(45 * alpha * (0.5 + 0.5 * math.sin(t * 2 + i)))
        if a > 0:
            draw.text((x, y), "♥", fill=PINK_GLOW + (a,), font=get_font(MONO, s))

def draw_sparkle(draw, t, alpha=0.3):
    for i in range(25):
        x = (i * 53 + int(t * 12)) % W
        y = (i * 97 + int(t * 8)) % H
        phase = math.sin(t * 3 + i * 0.7)
        if phase > 0.3:
            a = int(70 * alpha * phase)
            s = 2 + int(5 * phase)
            draw.ellipse([x-s, y-s, x+s, y+s], fill=GOLD + (a,))

# ============================================================
# PRE-RENDER ALL CHARACTER IMAGES
# ============================================================
CHAR_IMAGES = {}

def pre_render_characters():
    """Pre-render ASCII art images for each character at high detail."""
    print("  Drawing woman vector (1000x1000)...")
    woman_vec = draw_woman()
    woman_vec.save(os.path.join(OUTPUT, "vec_woman.png"))

    print("  Drawing man vector (1000x1000)...")
    man_vec = draw_man()
    man_vec.save(os.path.join(OUTPUT, "vec_man.png"))

    # Single character: 160 cols x 220 rows, cell_render=5 → 800x1100
    print("  Converting woman to ASCII (160x220 grid, 5px cells)...")
    CHAR_IMAGES["woman"] = vector_to_ascii_img(woman_vec, 160, 220, cell_render=5)

    print("  Converting man to ASCII (160x220 grid, 5px cells)...")
    CHAR_IMAGES["man"] = vector_to_ascii_img(man_vec, 160, 220, cell_render=5)

    # Both: smaller to fit two side by side
    print("  Converting both to ASCII (100x140 grid, 4px cells)...")
    CHAR_IMAGES["woman_sm"] = vector_to_ascii_img(woman_vec, 100, 140, cell_render=4)
    CHAR_IMAGES["man_sm"] = vector_to_ascii_img(man_vec, 100, 140, cell_render=4)

    # Save previews
    for k, v in CHAR_IMAGES.items():
        v.save(os.path.join(OUTPUT, f"ascii_{k}.png"))
        print(f"    {k}: {v.size[0]}x{v.size[1]}px")

# ============================================================
# FRAME RENDERER
# ============================================================
def render_frame(scene_idx, scene, t, scene_t, frame_num, total_frames, scene_dur):
    canvas = Image.new("RGBA", (W, H), BG + (255,))
    draw = ImageDraw.Draw(canvas, "RGBA")

    # Fade
    alpha = 1.0
    if scene_t < 0.6: alpha = scene_t / 0.6
    elif scene_t > scene_dur - 0.6: alpha = (scene_dur - scene_t) / 0.6

    # BG effects
    if scene.get("bg") == "hearts": draw_hearts(draw, t, alpha * 0.5)
    elif scene.get("bg") == "sparkle": draw_sparkle(draw, t, alpha * 0.5)

    # Title
    title = scene["title"]
    tc = scene.get("title_color", DIM)
    tf = get_font(VI_BOLD, 38)
    tb = draw.textbbox((0,0), title, font=tf)
    draw.text(((W - tb[2] + tb[0])//2, 100), title, font=tf,
              fill=tuple(int(c*alpha) for c in tc) + (int(255*alpha),))

    # Character
    char_type = scene["character"]
    if char_type == "woman":
        img = CHAR_IMAGES["woman"].convert("RGB")
        x = (W - img.width) // 2
        y = (H - img.height) // 2 - 80
        canvas.paste(img, (x, y))

    elif char_type == "man":
        img = CHAR_IMAGES["man"].convert("RGB")
        x = (W - img.width) // 2
        y = (H - img.height) // 2 - 80
        canvas.paste(img, (x, y))

    elif char_type == "both":
        w_sm = CHAR_IMAGES["woman_sm"].convert("RGB")
        m_sm = CHAR_IMAGES["man_sm"].convert("RGB")
        gap = 30
        total_w = w_sm.width + gap + m_sm.width
        start_x = (W - total_w) // 2
        cy = (H - w_sm.height) // 2 - 60

        canvas.paste(w_sm, (start_x, cy))
        canvas.paste(m_sm, (start_x + w_sm.width + gap, cy))

        # Names
        nf = get_font(VI_BOLD, 28)
        for name, color, ix in [("Linh", DRESS_P, start_x + w_sm.width//2),
                                 ("Dũng", GOLD, start_x + w_sm.width + gap + m_sm.width//2)]:
            nb = draw.textbbox((0,0), name, font=nf)
            draw.text((ix - (nb[2]-nb[0])//2, cy + w_sm.height + 10),
                      name, font=nf, fill=color + (int(255*alpha),))

    # Caption — split into words for readability
    cf = get_font(VI_FONT, 34)
    cap_text = scene["caption"]
    # Word wrap
    words = cap_text.split()
    lines = []
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        tb = draw.textbbox((0,0), test, font=cf)
        if tb[2] - tb[0] > W - 120 and line:
            lines.append(line)
            line = w
        else:
            line = test
    if line: lines.append(line)

    cap_y = H - 340
    for ci, ln in enumerate(lines):
        lb = draw.textbbox((0,0), ln, font=cf)
        ca = int(255 * min(1.0, alpha * max(0, 1.0 - ci * 0.1)))
        draw.text(((W - lb[2] + lb[0])//2, cap_y + ci * 48), ln, font=cf,
                  fill=WHITE + (ca,))

    # Progress
    bar_y = H - 100
    bar_w = W - 200
    bar_x = 100
    progress = frame_num / max(1, total_frames)
    draw.rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + 6], fill=(30,30,40,200))
    draw.rectangle([bar_x, bar_y, bar_x + int(bar_w * progress), bar_y + 6],
                   fill=PINK_GLOW + (180,))

    dot_y = bar_y + 28
    dot_sp = 36
    dot_sx = W//2 - (len(SCENES) * dot_sp) // 2
    for si in range(len(SCENES)):
        dx = dot_sx + si * dot_sp
        r = 6 if si == scene_idx else 4
        dc = PINK_GLOW if si == scene_idx else (50,50,60)
        draw.ellipse([dx-r, dot_y-r, dx+r, dot_y+r], fill=dc)

    return canvas.convert("RGB")

# ============================================================
# TTS
# ============================================================
async def generate_all_tts():
    for i, scene in enumerate(SCENES):
        path = os.path.join(AUDIO_DIR, f"scene_{i:02d}.mp3")
        comm = edge_tts.Communicate(scene["tts"], "vi-VN-HoaiMyNeural", rate="+5%")
        await comm.save(path)
        print(f"  TTS {i+1}: {scene['tts'][:40]}...")

def concat_audio():
    concat = os.path.join(AUDIO_DIR, "concat.txt")
    with open(concat, "w") as f:
        for i in range(len(SCENES)):
            f.write(f"file 'scene_{i:02d}.mp3'\n")
    full = os.path.join(OUTPUT, "narration.mp3")
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,
                     "-c","copy",full], capture_output=True)
    r = subprocess.run(["ffprobe","-v","quiet","-show_entries","format=duration",
                         "-of","default=noprint_wrappers=1:nokey=1",full],
                        capture_output=True, text=True)
    return full, float(r.stdout.strip())

# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("💕 ASCII LOVE STORY v3: Maximum Detail")
    print("   1000x1000 vector → 120x160 ASCII grid")
    print("=" * 60)

    # Step 1: Pre-render characters
    print("\n🎨 Pre-rendering characters...")
    pre_render_characters()

    # Step 2: TTS
    print("\n🎙 Generating TTS...")
    asyncio.run(generate_all_tts())

    # Step 3: Audio
    print("\n🎵 Audio...")
    audio_path, audio_dur = concat_audio()
    scene_dur = audio_dur / len(SCENES)
    total_frames = int(audio_dur * FPS)
    print(f"   {audio_dur:.1f}s total, {scene_dur:.1f}s/scene, {total_frames} frames")

    # Step 4: Render frames
    print("\n🎨 Rendering frames...")
    frame_num = 0
    for si, scene in enumerate(SCENES):
        scene_frames = int(scene_dur * FPS)
        print(f"   Scene {si+1}: {scene['title']} ({scene_frames} frames)")
        for fi in range(scene_frames):
            t = frame_num / FPS
            scene_t = fi / FPS
            img = render_frame(si, scene, t, scene_t, frame_num, total_frames, scene_dur)
            img.save(os.path.join(FRAMES_DIR, f"f_{frame_num:05d}.png"))
            frame_num += 1
            if fi % (FPS * 3) == 0:
                print(f"      {100*frame_num//total_frames}%")

    # Step 5: Encode
    print("\n🎞 Encoding...")
    out = os.path.join(OUTPUT, "tinh_yeu_v3.mp4")
    subprocess.run([
        "ffmpeg","-y","-framerate",str(FPS),
        "-i", os.path.join(FRAMES_DIR, "f_%05d.png"),
        "-i", audio_path,
        "-c:v","libx264","-pix_fmt","yuv420p",
        "-crf","18","-profile:v","high",
        "-c:a","aac","-b:a","192k",
        "-shortest","-movflags","+faststart", out
    ], capture_output=True)

    if os.path.exists(out):
        sz = os.path.getsize(out) / (1024*1024)
        print(f"\n✅ DONE: {out}")
        print(f"   Size: {sz:.1f}MB, {audio_dur:.1f}s")
    else:
        print("\n❌ FAILED")

if __name__ == "__main__":
    main()
