#!/usr/bin/env python3
"""
ASCII Love Story v2: 'Tình Yêu Đường Cong'
High-detail ASCII characters — draw at 1000x1000 vector, sample to ASCII grid
Vietnamese TTS, 1080x1920, 8 scenes
"""
from PIL import Image, ImageDraw, ImageFont
import os, subprocess, asyncio, edge_tts, math

OUTPUT = "/Users/hung/code/ai/shorts/output/ascii_love_v2"
FRAMES_DIR = os.path.join(OUTPUT, "frames")
AUDIO_DIR = os.path.join(OUTPUT, "audio")
os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 24
SCENE_DUR = 5.0  # default, adjusted to audio

# Fonts
VI_FONT = "/Library/Fonts/Arial Unicode.ttf"
VI_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
MONO = "/System/Library/Fonts/Menlo.ttc"

def get_font(path, size):
    try: return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

# ============================================================
# CHARACTER RENDERER — draw vector at 1000x1000, sample to grid
# ============================================================

# Colors
SKIN      = (240, 205, 175)
SKIN_DARK = (210, 170, 140)
HAIR_BK   = (25, 20, 30)
HAIR_SH   = (55, 45, 65)
LIPS      = (195, 75, 75)
LIPS_LIGHT = (215, 100, 100)
EYE_W     = (240, 240, 245)
EYE_IRIS  = (65, 110, 170)
EYE_PUP   = (15, 12, 22)
EYE_LASH  = (18, 14, 24)
BLUSH     = (230, 165, 155)
BROW      = (35, 28, 38)
NECK_SH   = (220, 180, 150)

# Dress
DRESS_P   = (215, 105, 150)
DRESS_L   = (235, 155, 185)
DRESS_D   = (185, 80, 125)
DRESS_HL  = (245, 185, 205)

# Suit
SUIT_D    = (20, 20, 38)
SUIT_L    = (45, 45, 68)
SUIT_HL   = (65, 65, 88)
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

BLOCK = '\u2588'

# ── Draw woman vector at 1000x1000 ──
def draw_woman_1000():
    """Draw a beautiful woman with S-curve at 1000x1000 resolution."""
    img = Image.new("RGB", (1000, 1000), BG)
    draw = ImageDraw.Draw(img)

    cx = 500  # center x

    # ── Hair (behind head) ──
    # Long flowing hair
    draw.ellipse([cx-185, 120, cx+185, 420], fill=HAIR_BK)
    # Hair sides flowing down
    draw.polygon([
        (cx-180, 250), (cx-210, 350), (cx-220, 500),
        (cx-200, 600), (cx-170, 650), (cx-150, 550),
        (cx-160, 400), (cx-170, 300)
    ], fill=HAIR_BK)
    draw.polygon([
        (cx+180, 250), (cx+210, 350), (cx+220, 500),
        (cx+200, 600), (cx+170, 650), (cx+150, 550),
        (cx+160, 400), (cx+170, 300)
    ], fill=HAIR_BK)
    # Hair shine
    draw.arc([cx-100, 130, cx+100, 300], 200, 340, fill=HAIR_SH, width=3)

    # ── Neck ──
    draw.polygon([
        (cx-45, 370), (cx+45, 370),
        (cx+50, 440), (cx-50, 440)
    ], fill=SKIN)
    # Neck shadow
    draw.polygon([
        (cx-40, 370), (cx+40, 370),
        (cx+35, 395), (cx-35, 395)
    ], fill=SKIN_DARK)

    # ── Face (oval) ──
    draw.ellipse([cx-155, 170, cx+155, 410], fill=SKIN)
    # Jaw contour (narrower chin)
    draw.polygon([
        (cx-140, 310), (cx-100, 390), (cx, 410),
        (cx+100, 390), (cx+140, 310)
    ], fill=SKIN)
    # Cheek blush
    draw.ellipse([cx-135, 310, cx-60, 370], fill=BLUSH)
    draw.ellipse([cx+60, 310, cx+135, 370], fill=BLUSH)

    # ── Hair bangs (over forehead) ──
    draw.polygon([
        (cx-155, 200), (cx-130, 170), (cx-50, 190),
        (cx, 180), (cx+50, 190), (cx+130, 170),
        (cx+155, 200), (cx+145, 260), (cx+80, 240),
        (cx, 250), (cx-80, 240), (cx-145, 260)
    ], fill=HAIR_BK)
    # Side bangs
    draw.polygon([
        (cx-155, 200), (cx-175, 220), (cx-180, 300),
        (cx-170, 270), (cx-155, 240)
    ], fill=HAIR_BK)
    draw.polygon([
        (cx+155, 200), (cx+175, 220), (cx+180, 300),
        (cx+170, 270), (cx+155, 240)
    ], fill=HAIR_BK)

    # ── Eyes ──
    for ex in [cx-75, cx+75]:
        # White
        draw.ellipse([ex-40, 275, ex+40, 325], fill=EYE_W)
        # Iris
        draw.ellipse([ex-22, 280, ex+22, 320], fill=EYE_IRIS)
        # Pupil
        draw.ellipse([ex-10, 290, ex+10, 310], fill=EYE_PUP)
        # Highlight
        draw.ellipse([ex-5, 285, ex+5, 295], fill=(255, 255, 255))
        # Upper lash line
        draw.arc([ex-42, 273, ex+42, 327], 190, 350, fill=EYE_LASH, width=4)
        # Lower lash
        draw.arc([ex-35, 280, ex+35, 330], 10, 170, fill=EYE_LASH, width=2)

    # ── Eyebrows ──
    draw.arc([cx-115, 250, cx-35, 290], 200, 340, fill=BROW, width=3)
    draw.arc([cx+35, 250, cx+115, 290], 200, 340, fill=BROW, width=3)

    # ── Nose ──
    draw.polygon([
        (cx-8, 330), (cx+8, 330), (cx+12, 365), (cx-12, 365)
    ], fill=SKIN_DARK)
    draw.arc([cx-15, 355, cx+15, 375], 0, 180, fill=SKIN_DARK, width=2)

    # ── Lips ──
    # Upper lip
    draw.polygon([
        (cx-35, 385), (cx-15, 378), (cx, 382),
        (cx+15, 378), (cx+35, 385), (cx, 392)
    ], fill=LIPS)
    # Lower lip
    draw.ellipse([cx-30, 388, cx+30, 410], fill=LIPS_LIGHT)

    # ── Dress body (S-curve!) ──
    # Shoulders
    draw.polygon([
        (cx-200, 440), (cx+200, 440),
        (cx+180, 490), (cx-180, 490)
    ], fill=DRESS_P)
    # Bust (wider)
    draw.polygon([
        (cx-190, 480), (cx+190, 480),
        (cx+210, 580), (cx-210, 580)
    ], fill=DRESS_P)
    draw.ellipse([cx-210, 500, cx-50, 600], fill=DRESS_L)
    draw.ellipse([cx+50, 500, cx+210, 600], fill=DRESS_L)

    # Waist (NARROW — S-curve!)
    draw.polygon([
        (cx-210, 570), (cx+210, 570),
        (cx+100, 670), (cx-100, 670)
    ], fill=DRESS_P)
    # Waist detail
    draw.polygon([
        (cx-130, 620), (cx+130, 620),
        (cx+110, 650), (cx-110, 650)
    ], fill=DRESS_D)

    # Hips (WIDE again — S-curve!)
    draw.polygon([
        (cx-100, 660), (cx+100, 660),
        (cx+220, 760), (cx-220, 760)
    ], fill=DRESS_P)
    draw.ellipse([cx-230, 680, cx-30, 780], fill=DRESS_L)
    draw.ellipse([cx+30, 680, cx+230, 780], fill=DRESS_L)

    # Skirt flowing down
    draw.polygon([
        (cx-220, 750), (cx+220, 750),
        (cx+250, 920), (cx-250, 920)
    ], fill=DRESS_P)
    # Skirt folds
    draw.polygon([
        (cx-180, 770), (cx-100, 770),
        (cx-120, 900), (cx-200, 900)
    ], fill=DRESS_D)
    draw.polygon([
        (cx+100, 770), (cx+180, 770),
        (cx+200, 900), (cx+120, 900)
    ], fill=DRESS_D)
    draw.polygon([
        (cx-30, 760), (cx+30, 760),
        (cx+50, 910), (cx-50, 910)
    ], fill=DRESS_HL)

    # ── Arms ──
    # Left arm
    draw.polygon([
        (cx-195, 450), (cx-230, 460),
        (cx-250, 600), (cx-230, 610),
        (cx-200, 500)
    ], fill=SKIN)
    # Right arm
    draw.polygon([
        (cx+195, 450), (cx+230, 460),
        (cx+250, 600), (cx+230, 610),
        (cx+200, 500)
    ], fill=SKIN)

    # ── Hands ──
    draw.ellipse([cx-260, 590, cx-220, 640], fill=SKIN)
    draw.ellipse([cx+220, 590, cx+260, 640], fill=SKIN)

    # ── Feet/shoes ──
    draw.ellipse([cx-120, 910, cx-50, 950], fill=SHOE)
    draw.ellipse([cx+50, 910, cx+120, 950], fill=SHOE)

    return img


# ── Draw man vector at 1000x1000 ──
def draw_man_1000():
    """Draw a handsome CEO at 1000x1000 resolution."""
    img = Image.new("RGB", (1000, 1000), BG)
    draw = ImageDraw.Draw(img)

    cx = 500

    # ── Suit shoulders (behind everything) ──
    draw.polygon([
        (cx-230, 450), (cx+230, 450),
        (cx+220, 500), (cx-220, 500)
    ], fill=SUIT_D)

    # ── Neck ──
    draw.polygon([
        (cx-55, 370), (cx+55, 370),
        (cx+60, 440), (cx-60, 440)
    ], fill=SKIN)
    draw.polygon([
        (cx-45, 370), (cx+45, 370),
        (cx+40, 400), (cx-40, 400)
    ], fill=SKIN_DARK)

    # ── Face (squarer jaw) ──
    draw.ellipse([cx-160, 170, cx+160, 420], fill=SKIN)
    # Strong jaw
    draw.polygon([
        (cx-150, 310), (cx-120, 380), (cx-60, 420),
        (cx, 430), (cx+60, 420), (cx+120, 380), (cx+150, 310)
    ], fill=SKIN)
    # Jaw shadow
    draw.polygon([
        (cx-120, 380), (cx-60, 420), (cx, 430),
        (cx+60, 420), (cx+120, 380), (cx+80, 400), (cx, 415), (cx-80, 400)
    ], fill=SKIN_DARK)

    # ── Hair (short, slicked) ──
    draw.ellipse([cx-165, 140, cx+165, 310], fill=HAIR_BK)
    # Hair on top (higher)
    draw.polygon([
        (cx-160, 200), (cx-130, 145), (cx-50, 135),
        (cx, 130), (cx+50, 135), (cx+130, 145), (cx+160, 200),
        (cx+155, 230), (cx+80, 215), (cx, 220),
        (cx-80, 215), (cx-155, 230)
    ], fill=HAIR_BK)
    # Hair shine
    draw.arc([cx-120, 140, cx+120, 230], 200, 340, fill=HAIR_SH, width=3)
    # Side part
    draw.polygon([
        (cx-160, 200), (cx-180, 220), (cx-185, 310),
        (cx-175, 280), (cx-160, 240)
    ], fill=HAIR_BK)
    draw.polygon([
        (cx+160, 200), (cx+180, 220), (cx+185, 310),
        (cx+175, 280), (cx+160, 240)
    ], fill=HAIR_BK)

    # ── Eyes (sharper, narrower) ──
    for ex in [cx-80, cx+80]:
        # White
        draw.ellipse([ex-38, 278, ex+38, 318], fill=EYE_W)
        # Iris
        draw.ellipse([ex-20, 282, ex+20, 314], fill=(50, 80, 50))  # dark green
        # Pupil
        draw.ellipse([ex-9, 292, ex+9, 308], fill=EYE_PUP)
        # Highlight
        draw.ellipse([ex-4, 286, ex+4, 294], fill=(255, 255, 255))
        # Upper lash
        draw.arc([ex-40, 275, ex+40, 320], 195, 345, fill=EYE_LASH, width=5)
        # Lower
        draw.arc([ex-30, 282, ex+30, 318], 15, 165, fill=EYE_LASH, width=2)

    # ── Thick eyebrows ──
    draw.polygon([
        (cx-120, 258), (cx-40, 252), (cx-38, 264), (cx-118, 270)
    ], fill=BROW)
    draw.polygon([
        (cx+40, 252), (cx+120, 258), (cx+118, 270), (cx+38, 264)
    ], fill=BROW)

    # ── Nose ──
    draw.polygon([
        (cx-10, 325), (cx+10, 325), (cx+15, 370), (cx-15, 370)
    ], fill=SKIN_DARK)
    draw.arc([cx-18, 360, cx+18, 380], 0, 180, fill=SKIN_DARK, width=3)

    # ── Mouth (slight confident smile) ──
    draw.arc([cx-35, 388, cx+35, 410], 10, 170, fill=LIPS, width=3)
    draw.polygon([
        (cx-25, 395), (cx+25, 395), (cx+20, 402), (cx-20, 402)
    ], fill=LIPS)

    # ── Shirt collar ──
    draw.polygon([
        (cx-55, 435), (cx-30, 430), (cx, 460), (cx+30, 430), (cx+55, 435),
        (cx+40, 490), (cx, 510), (cx-40, 490)
    ], fill=SHIRT)
    # Collar points
    draw.polygon([
        (cx-55, 435), (cx-80, 450), (cx-60, 470), (cx-40, 445)
    ], fill=SHIRT)
    draw.polygon([
        (cx+55, 435), (cx+80, 450), (cx+60, 470), (cx+40, 445)
    ], fill=SHIRT)

    # ── Tie ──
    draw.polygon([
        (cx-15, 460), (cx+15, 460),
        (cx+10, 700), (cx-10, 700)
    ], fill=TIE)
    draw.polygon([
        (cx-15, 460), (cx+15, 460),
        (cx+8, 480), (cx-8, 480)
    ], fill=TIE_L)
    # Tie knot
    draw.polygon([
        (cx-12, 448), (cx+12, 448), (cx+8, 465), (cx-8, 465)
    ], fill=TIE_L)

    # ── Suit jacket ──
    draw.polygon([
        (cx-230, 450), (cx-55, 435), (cx-40, 490),
        (cx-50, 700), (cx-240, 710)
    ], fill=SUIT_D)
    draw.polygon([
        (cx+230, 450), (cx+55, 435), (cx+40, 490),
        (cx+50, 700), (cx+240, 710)
    ], fill=SUIT_D)
    # Lapel highlights
    draw.polygon([
        (cx-55, 435), (cx-80, 450), (cx-70, 550), (cx-50, 500)
    ], fill=SUIT_L)
    draw.polygon([
        (cx+55, 435), (cx+80, 450), (cx+70, 550), (cx+50, 500)
    ], fill=SUIT_L)

    # ── Belt ──
    draw.rectangle([cx-130, 690, cx+130, 715], fill=SUIT_D)
    draw.rectangle([cx-20, 690, cx+20, 715], fill=BELT_G)

    # ── Trousers ──
    draw.polygon([
        (cx-130, 710), (cx-10, 710),
        (cx-30, 950), (cx-110, 950)
    ], fill=SUIT_D)
    draw.polygon([
        (cx+10, 710), (cx+130, 710),
        (cx+110, 950), (cx+30, 950)
    ], fill=SUIT_D)
    # Trouser crease
    draw.line([(cx-70, 720), (cx-70, 940)], fill=SUIT_L, width=2)
    draw.line([(cx+70, 720), (cx+70, 940)], fill=SUIT_L, width=2)

    # ── Shoes ──
    draw.ellipse([cx-120, 935, cx-40, 975], fill=SHOE)
    draw.ellipse([cx+40, 935, cx+120, 975], fill=SHOE)

    # ── Arms ──
    draw.polygon([
        (cx-225, 460), (cx-260, 470),
        (cx-270, 680), (cx-240, 690),
        (cx-210, 550)
    ], fill=SUIT_D)
    draw.polygon([
        (cx+225, 460), (cx+260, 470),
        (cx+270, 680), (cx+240, 690),
        (cx+210, 550)
    ], fill=SUIT_D)
    # Hands
    draw.ellipse([cx-280, 670, cx-235, 720], fill=SKIN)
    draw.ellipse([cx+235, 670, cx+280, 720], fill=SKIN)

    return img


# ============================================================
# VECTOR → ASCII GRID CONVERSION
# ============================================================

def rgb_to_char(r, g, b):
    """Map RGB to a display character with its color.
    Uses luminance to pick character density."""
    lum = 0.299 * r + 0.587 * g + 0.114 * b

    # Background detection
    if r < 20 and g < 20 and b < 25:
        return None  # transparent/background

    # Character selection based on luminance
    if lum > 220:
        ch = '.'  # very bright
    elif lum > 180:
        ch = '+'  # bright
    elif lum > 140:
        ch = 'o'  # medium-bright
    elif lum > 100:
        ch = '#'  # medium
    elif lum > 60:
        ch = '@'  # dark
    else:
        ch = BLOCK  # very dark = filled

    return (ch, (r, g, b))


def vector_to_ascii_grid(source_img, grid_cols, grid_rows):
    """Convert a 1000x1000 source image to ASCII grid.
    Returns list of rows, each row = list of (char, color) or None."""
    sw, sh = source_img.size
    pixels = source_img.load()

    cell_w = sw / grid_cols
    cell_h = sh / grid_rows

    grid = []
    for gy in range(grid_rows):
        row = []
        for gx in range(grid_cols):
            # Sample center of cell
            sx = int(gx * cell_w + cell_w / 2)
            sy = int(gy * cell_h + cell_h / 2)
            sx = min(sx, sw - 1)
            sy = min(sy, sh - 1)

            r, g, b = pixels[sx, sy]
            cell = rgb_to_char(r, g, b)
            row.append(cell)
        grid.append(row)
    return grid


# ============================================================
# SCENE DEFINITIONS
# ============================================================

# Pre-generate character grids at different densities
WOMAN_VECTOR = None
MAN_VECTOR = None
WOMAN_GRID = None
MAN_GRID = None

def init_characters():
    global WOMAN_VECTOR, MAN_VECTOR, WOMAN_GRID, MAN_GRID
    print("  Drawing woman at 1000x1000...")
    WOMAN_VECTOR = draw_woman_1000()
    print("  Drawing man at 1000x1000...")
    MAN_VECTOR = draw_man_1000()

    # Convert to ASCII grids — 40 cols for single char, 30 cols for side-by-side
    print("  Converting to ASCII grids...")
    WOMAN_GRID = vector_to_ascii_grid(WOMAN_VECTOR, 40, 50)
    MAN_GRID = vector_to_ascii_grid(MAN_VECTOR, 40, 50)

    # Save previews
    WOMAN_VECTOR.save(os.path.join(OUTPUT, "preview_woman.png"))
    MAN_VECTOR.save(os.path.join(OUTPUT, "preview_man.png"))
    print("  Saved vector previews")

SCENES = [
    {
        "title": "CHƯƠNG 1",
        "character": "woman",
        "caption_lines": ["Ngày đó, Linh là cô gái", "đẹp nhất thành phố."],
        "tts_text": "Ngày đó, Linh là cô gái đẹp nhất thành phố. Vẻ đẹp không chỉ ở khuôn mặt, mà còn ở trái tim nhân hậu.",
        "bg_effect": "hearts",
    },
    {
        "title": "CHƯƠNG 2",
        "character": "man",
        "caption_lines": ["Còn Dũng là tổng tài", "giàu nhất thành phố."],
        "tts_text": "Còn Dũng là tổng tài giàu nhất thành phố. Anh có tất cả, trừ một điều: tình yêu thực sự.",
        "bg_effect": "sparkle",
    },
    {
        "title": "CHƯƠNG 3",
        "title_color": PINK_GLOW,
        "character": "both",
        "caption_lines": ["Họ gặp nhau", "tại bữa tiệc đêm đó..."],
        "tts_text": "Họ gặp nhau tại bữa tiệc đêm đó. Ánh mắt lần đầu chạm nhau, cả thế giới như dừng lại.",
        "bg_effect": "sparkle",
    },
    {
        "title": "CHƯƠNG 4",
        "title_color": PINK_GLOW,
        "character": "both",
        "caption_lines": ["Không tiền bạc, không địa vị.", "Chỉ có hai trái tim."],
        "tts_text": "Không tiền bạc, không địa vị. Chỉ có hai trái tim rung động. Tình yêu không cần vật chất.",
        "bg_effect": "hearts",
    },
    {
        "title": "CHƯƠNG 5",
        "title_color": GOLD,
        "character": "man",
        "caption_lines": ["Dũng quyết định", "bỏ lại tất cả."],
        "tts_text": "Dũng quyết định bỏ lại tất cả. Đế chế tiền bạc không bằng nụ cười của cô ấy.",
        "bg_effect": "sparkle",
    },
    {
        "title": "CHƯƠNG 6",
        "title_color": DRESS_P,
        "character": "woman",
        "caption_lines": ["Linh chờ đợi", "một tình yêu chân thật."],
        "tts_text": "Linh chờ đợi một tình yêu chân thật. Không phải vì anh giàu, mà vì anh hiểu trái tim cô.",
        "bg_effect": "hearts",
    },
    {
        "title": "CHƯƠNG 7",
        "title_color": PINK_GLOW,
        "character": "both",
        "caption_lines": ["Hai đường cong", "gặp nhau tại đỉnh."],
        "tts_text": "Hai đường cong cuộc đời gặp nhau tại đỉnh. Từ nay, không còn đơn độc.",
        "bg_effect": "hearts",
    },
    {
        "title": "PHẦN KẾT",
        "title_color": GOLD,
        "character": "both",
        "caption_lines": ["TÌNH YÊU KHÔNG CÓ", "GIÁ."],
        "tts_text": "Tình yêu không có giá. Nhưng không có nó, mọi thứ đều có giá. Từ hai, thành một. Không gì là không thể.",
        "bg_effect": "hearts",
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
# GRID RENDERER — render ASCII grid onto canvas
# ============================================================
def render_ascii_grid(draw, grid, cx, cy, cell_size, y_offset=0):
    """Render a character grid centered at (cx, cy)."""
    rows = len(grid)
    cols = max(len(r) for r in grid)
    total_w = cols * cell_size
    total_h = rows * cell_size
    sx = cx - total_w // 2
    sy = cy - total_h // 2 + y_offset

    mono = get_font(MONO, max(6, cell_size - 1))

    for ri, row in enumerate(grid):
        y = sy + ri * cell_size
        if y < -cell_size or y > H + cell_size: continue
        for ci, cell in enumerate(row):
            if cell is None: continue
            ch, color = cell
            x = sx + ci * cell_size
            if x < -cell_size or x > W + cell_size: continue
            draw.text((x, y), ch, fill=color, font=mono)

# ============================================================
# FRAME RENDERER
# ============================================================
def render_frame(scene_idx, scene, t, scene_t, frame_num, total_frames):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img, "RGBA")

    # Fade in/out
    alpha = 1.0
    if scene_t < 0.6:
        alpha = scene_t / 0.6
    elif scene_t > SCENE_DUR - 0.6:
        alpha = (SCENE_DUR - scene_t) / 0.6

    # Background effects
    effect = scene.get("bg_effect", "hearts")
    if effect == "hearts":
        draw_hearts(draw, t, alpha * 0.5)
    elif effect == "sparkle":
        draw_sparkle(draw, t, alpha * 0.5)

    # Title
    title = scene["title"]
    title_color = scene.get("title_color", DIM)
    tf = get_font(VI_BOLD, 38)
    tb = draw.textbbox((0, 0), title, font=tf)
    tw = tb[2] - tb[0]
    tc = tuple(int(c * alpha) for c in title_color) + (int(255 * alpha),)
    draw.text(((W - tw) // 2, 100), title, font=tf, fill=tc)

    # Character rendering
    char_type = scene["character"]

    if char_type == "woman":
        render_ascii_grid(draw, WOMAN_GRID, W // 2, H // 2 - 120, 14)
    elif char_type == "man":
        render_ascii_grid(draw, MAN_GRID, W // 2, H // 2 - 120, 14)
    elif char_type == "both":
        # Side by side, smaller
        total_cols = 40 + 5 + 40  # woman + gap + man
        cell = 10
        total_w = total_cols * cell
        left_cx = (W - total_w) // 2 + 40 * cell // 2
        right_cx = (W - total_w) // 2 + 40 * cell + 5 * cell + 40 * cell // 2

        render_ascii_grid(draw, WOMAN_GRID, left_cx, H // 2 - 100, cell)
        render_ascii_grid(draw, MAN_GRID, right_cx, H // 2 - 100, cell)

        # Names
        nf = get_font(VI_BOLD, 30)
        name_y = H // 2 + 230
        for name, color, x in [("Linh", DRESS_P, left_cx), ("Dũng", GOLD, right_cx)]:
            nb = draw.textbbox((0, 0), name, font=nf)
            nw = nb[2] - nb[0]
            draw.text((x - nw // 2, name_y), name, font=nf, fill=color + (int(255 * alpha),))

    # Caption
    cf = get_font(VI_FONT, 36)
    cap_y = H - 380
    for ci, line in enumerate(scene["caption_lines"]):
        cb = draw.textbbox((0, 0), line, font=cf)
        cw = cb[2] - cb[0]
        ca = int(255 * min(1.0, alpha * max(0, 1.0 - ci * 0.15)))
        draw.text(((W - cw) // 2, cap_y + ci * 52), line, font=cf, fill=WHITE + (ca,))

    # Progress
    bar_y = H - 110
    bar_w = W - 200
    bar_x = 100
    progress = frame_num / max(1, total_frames)
    draw.rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + 6], fill=(30, 30, 40))
    draw.rectangle([bar_x, bar_y, bar_x + int(bar_w * progress), bar_y + 6],
                   fill=PINK_GLOW + (180,))

    # Dots
    dot_y = bar_y + 28
    dot_sp = 36
    dot_sx = W // 2 - (len(SCENES) * dot_sp) // 2
    for si in range(len(SCENES)):
        dx = dot_sx + si * dot_sp
        r = 6 if si == scene_idx else 4
        dc = PINK_GLOW if si == scene_idx else (50, 50, 60)
        draw.ellipse([dx - r, dot_y - r, dx + r, dot_y + r], fill=dc)

    return img

# ============================================================
# TTS
# ============================================================
async def generate_all_tts():
    for i, scene in enumerate(SCENES):
        path = os.path.join(AUDIO_DIR, f"scene_{i:02d}.mp3")
        comm = edge_tts.Communicate(scene["tts_text"], "vi-VN-HoaiMyNeural", rate="+5%")
        await comm.save(path)
        print(f"  TTS {i+1}: {scene['tts_text'][:40]}...")

def concat_audio():
    concat = os.path.join(AUDIO_DIR, "concat.txt")
    with open(concat, "w") as f:
        for i in range(len(SCENES)):
            f.write(f"file 'scene_{i:02d}.mp3'\n")
    full = os.path.join(OUTPUT, "narration.mp3")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat,
                     "-c", "copy", full], capture_output=True)
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                         "-of", "default=noprint_wrappers=1:nokey=1", full],
                        capture_output=True, text=True)
    return full, float(r.stdout.strip())

# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("💕 ASCII LOVE STORY v2: Tình Yêu Đường Cong")
    print("   Vector 1000x1000 → ASCII grid")
    print("=" * 60)

    # Step 1: Init characters
    print("\n🎨 Drawing characters at 1000x1000...")
    init_characters()

    # Step 2: TTS
    print("\n🎙 Generating Vietnamese TTS...")
    asyncio.run(generate_all_tts())

    # Step 3: Get audio timing
    print("\n🎵 Concatenating audio...")
    audio_path, audio_dur = concat_audio()
    global SCENE_DUR
    SCENE_DUR = audio_dur / len(SCENES)
    print(f"   Total audio: {audio_dur:.1f}s, per scene: {SCENE_DUR:.1f}s")

    # Step 4: Render frames
    print("\n🎨 Rendering frames...")
    total_frames = int(audio_dur * FPS)
    frame_num = 0

    for si, scene in enumerate(SCENES):
        scene_frames = int(SCENE_DUR * FPS)
        print(f"   Scene {si+1}/{len(SCENES)}: {scene['title']} ({scene_frames} frames)")
        for fi in range(scene_frames):
            t = frame_num / FPS
            scene_t = fi / FPS
            img = render_frame(si, scene, t, scene_t, frame_num, total_frames)
            img.save(os.path.join(FRAMES_DIR, f"f_{frame_num:05d}.png"))
            frame_num += 1
            if fi % (FPS * 3) == 0:
                pct = 100 * frame_num / max(1, total_frames)
                print(f"      {pct:.0f}%")

    print(f"   Total: {frame_num} frames")

    # Step 5: Encode
    print("\n🎞 Encoding MP4...")
    out = os.path.join(OUTPUT, "tinh_yeu_duong_cong_v2.mp4")
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(FRAMES_DIR, "f_%05d.png"),
        "-i", audio_path,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "18", "-profile:v", "high",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        out
    ], capture_output=True)

    if os.path.exists(out):
        sz = os.path.getsize(out) / (1024 * 1024)
        r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries",
                             "format=duration:stream=width,height,codec_name",
                             "-of", "compact", out], capture_output=True, text=True)
        print(f"\n✅ DONE: {out}")
        print(f"   Size: {sz:.1f}MB")
        print(f"   {r.stdout.strip()}")
    else:
        print("\n❌ FAILED")

if __name__ == "__main__":
    main()
