#!/usr/bin/env python3
"""
ASCII Love Story: 'Tình Yêu Đường Cong'
Detailed ASCII art characters — Beautiful S-curve girl + Handsome CEO
Each character rendered with color-coded regions (skin, hair, clothes)
Vietnamese TTS narration, 1080x1920, 8 scenes
"""
from PIL import Image, ImageDraw, ImageFont
import os, subprocess, asyncio, edge_tts, time

OUTPUT = "/Users/hung/code/ai/shorts/output/ascii_love_story"
FRAMES_DIR = os.path.join(OUTPUT, "frames")
AUDIO_DIR = os.path.join(OUTPUT, "audio")
os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 24

# Fonts
MONO = "/System/Library/Fonts/Menlo.ttc"
VI_FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
BOLD_FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

def get_mono(size):
    try: return ImageFont.truetype(MONO, size)
    except: return ImageFont.load_default()

def get_vi(size):
    try: return ImageFont.truetype(VI_FONT, size)
    except: return ImageFont.load_default()

def get_bold(size):
    try: return ImageFont.truetype(BOLD_FONT, size)
    except: return ImageFont.load_default()

# ============================================================
# ASCII ART CHARACTERS — Color-coded with (char, (r,g,b)) tuples
# Each character is a list of rows, each row is list of (char, color) tuples
# ============================================================

# Color palette
SKIN      = (245, 210, 180)
SKIN_SHADOW = (210, 175, 145)
HAIR_BLACK = (30, 25, 35)
HAIR_SHINE = (60, 50, 70)
LIPS      = (200, 80, 80)
EYE_DARK  = (25, 20, 30)
EYE_WHITE = (240, 240, 245)
EYE_COLOR = (80, 120, 180)  # blue eyes
EYE_LASH  = (20, 15, 25)
BLUSH     = (235, 170, 160)
DRESS_PINK = (220, 120, 160)
DRESS_LIGHT = (240, 170, 195)
SUIT_DARK  = (25, 25, 40)
SUIT_LINE  = (50, 50, 70)
SHIRT_WHITE = (235, 235, 240)
TIE_RED   = (180, 40, 40)
SHOE_DARK = (40, 35, 45)
BG_DARK   = (8, 8, 14)
GOLD      = (255, 215, 0)
PINK_GLOW = (255, 150, 180)
WHITE     = (255, 255, 255)
DIM       = (100, 100, 120)

def make_char_art(rows_of_tuples):
    """Convert list of rows-of-(char,color) tuples to renderable art."""
    return rows_of_tuples

BLOCK = '\u2588'  # █ full block character

def sp(ch, c=SKIN):
    """shorthand: single char pixel.
    Space -> block char so color is visible. None -> empty space."""
    if ch is None or ch == '':
        return (' ', (0, 0, 0))
    if ch == ' ':
        return (BLOCK, c)
    return (ch, c)

# ── BEAUTIFUL WOMAN (front view, S-curve silhouette) ──
WOMAN_ART = make_char_art([
    # Hair top
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_SHINE),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_SHINE),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_SHINE),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' '),sp(' '),sp(' ')],
    # Hair sides + forehead
    [sp(' '),sp(' '),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' ',HAIR_BLACK),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',HAIR_BLACK),sp(' '),sp(' ')],
    # Eyes row
    [sp(' '),sp(' '),sp(' ',HAIR_BLACK),sp(' ',SKIN),sp(' ',SKIN),sp(' ',EYE_WHITE),sp(' ',EYE_WHITE),sp(' ',EYE_WHITE),sp(' ',SKIN),sp(' ',SKIN),sp(' ',EYE_WHITE),sp(' ',EYE_WHITE),sp(' ',EYE_WHITE),sp(' ',SKIN),sp(' ',SKIN),sp(' ',HAIR_BLACK),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' ',HAIR_BLACK),sp(' ',SKIN),sp(' ',EYE_LASH),sp(' ',EYE_DARK),sp(' ',EYE_COLOR),sp(' ',EYE_DARK),sp(' ',SKIN),sp(' ',SKIN),sp(' ',EYE_DARK),sp(' ',EYE_COLOR),sp(' ',EYE_DARK),sp(' ',EYE_LASH),sp(' ',SKIN),sp(' ',HAIR_BLACK),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' ',HAIR_BLACK),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN_SHADOW),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN_SHADOW),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',HAIR_BLACK),sp(' '),sp(' ')],
    # Nose
    [sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN_SHADOW),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN_SHADOW),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN_SHADOW),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN_SHADOW),sp(' ',SKIN),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    # Lips
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',SKIN),sp(' ',LIPS),sp(' ',LIPS),sp(' ',LIPS),sp(' ',LIPS),sp(' ',SKIN),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',LIPS),sp(' ',LIPS),sp(' ',LIPS),sp(' ',LIPS),sp(' ',LIPS),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    # Chin
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    # Neck
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',SKIN),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',SKIN),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    # Shoulders + dress top (S-curve starts — wider shoulders, narrow waist)
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_LIGHT),sp(' ',DRESS_LIGHT),sp(' ',DRESS_LIGHT),sp(' ',DRESS_LIGHT),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_LIGHT),sp(' ',DRESS_LIGHT),sp(' ',DRESS_LIGHT),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_LIGHT),sp(' ',DRESS_LIGHT),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' '),sp(' '),sp(' '),sp(' ')],
    # Bust area (wider)
    [sp(' '),sp(' '),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_LIGHT),sp(' ',DRESS_LIGHT),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_LIGHT),sp(' ',DRESS_LIGHT),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' ',DRESS_PINK),sp(' ',DRESS_LIGHT),sp(' ',DRESS_LIGHT),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_LIGHT),sp(' ',DRESS_LIGHT),sp(' ',DRESS_PINK),sp(' '),sp(' '),sp(' ')],
    # Waist (narrow — S-curve!)
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_LIGHT),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_LIGHT),sp(' ',DRESS_PINK),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',DRESS_PINK),sp(' ',DRESS_LIGHT),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    # Hips (wider again — S-curve!)
    [sp(' '),sp(' '),sp(' '),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_LIGHT),sp(' ',DRESS_LIGHT),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_LIGHT),sp(' ',DRESS_LIGHT),sp(' ',DRESS_PINK),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' ',DRESS_PINK),sp(' ',DRESS_LIGHT),sp(' ',DRESS_LIGHT),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_LIGHT),sp(' ',DRESS_PINK),sp(' '),sp(' '),sp(' '),sp(' ')],
    # Dress skirt (flowing)
    [sp(' '),sp(' '),sp(' '),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_LIGHT),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_LIGHT),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_LIGHT),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_LIGHT),sp(' ',DRESS_PINK),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' ',DRESS_PINK),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    # Legs / shoes
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',SKIN),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',SKIN),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',SKIN),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',SKIN),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SHOE_DARK),sp(' ',SHOE_DARK),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SHOE_DARK),sp(' ',SHOE_DARK),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
])

# ── HANDSOME CEO (front view, suit + tie) ──
MAN_ART = make_char_art([
    # Hair
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_SHINE),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_SHINE),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' '),sp(' '),sp(' ')],
    # Forehead (square jaw = wider)
    [sp(' '),sp(' '),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',HAIR_BLACK),sp(' ',HAIR_BLACK),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' ',HAIR_BLACK),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',HAIR_BLACK),sp(' '),sp(' ')],
    # Eyes (sharper, thicker brows)
    [sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',EYE_LASH),sp(' ',EYE_LASH),sp(' ',EYE_WHITE),sp(' ',EYE_DARK),sp(' ',SKIN),sp(' ',SKIN),sp(' ',EYE_DARK),sp(' ',EYE_WHITE),sp(' ',EYE_LASH),sp(' ',EYE_LASH),sp(' ',SKIN),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',SKIN),sp(' ',EYE_DARK),sp(' ',EYE_DARK),sp(' ',EYE_DARK),sp(' ',SKIN),sp(' ',SKIN),sp(' ',EYE_DARK),sp(' ',EYE_DARK),sp(' ',EYE_DARK),sp(' ',SKIN),sp(' ',SKIN),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN_SHADOW),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN_SHADOW),sp(' ',SKIN),sp(' '),sp(' '),sp(' '),sp(' ')],
    # Nose (stronger)
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN_SHADOW),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN_SHADOW),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    # Mouth (slight smile)
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',SKIN_SHADOW),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN_SHADOW),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    # Strong jaw
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',SKIN),sp(' ',LIPS),sp(' ',LIPS),sp(' ',LIPS),sp(' ',LIPS),sp(' ',SKIN),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    # Neck (thicker)
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',SKIN),sp(' ',SKIN),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SKIN),sp(' ',SKIN),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    # Shoulders (wide — suit)
    [sp(' '),sp(' '),sp(' '),sp(' ',SUIT_DARK),sp(' ',SUIT_DARK),sp(' ',SUIT_DARK),sp(' ',SUIT_LINE),sp(' ',SHIRT_WHITE),sp(' ',SHIRT_WHITE),sp(' ',SHIRT_WHITE),sp(' ',SHIRT_WHITE),sp(' ',SUIT_LINE),sp(' ',SUIT_DARK),sp(' ',SUIT_DARK),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' ',SUIT_DARK),sp(' ',SUIT_DARK),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SHIRT_WHITE),sp(' ',TIE_RED),sp(' ',SHIRT_WHITE),sp(' ',SHIRT_WHITE),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_DARK),sp(' '),sp(' '),sp(' ')],
    # Chest (V-shape suit opening)
    [sp(' '),sp(' '),sp(' ',SUIT_DARK),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SHIRT_WHITE),sp(' ',TIE_RED),sp(' ',SHIRT_WHITE),sp(' ',SHIRT_WHITE),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_DARK),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' ',SUIT_DARK),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',TIE_RED),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_DARK),sp(' '),sp(' '),sp(' ')],
    # Belt
    [sp(' '),sp(' '),sp(' ',SUIT_DARK),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',GOLD),sp(' ',GOLD),sp(' ',GOLD),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_DARK),sp(' '),sp(' '),sp(' ')],
    # Trousers
    [sp(' '),sp(' '),sp(' '),sp(' ',SUIT_DARK),sp(' ',SUIT_DARK),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_DARK),sp(' ',SUIT_LINE),sp(' ',SUIT_DARK),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_DARK),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' ',SUIT_DARK),sp(' ',SUIT_LINE),sp(' ',SUIT_LINE),sp(' ',SUIT_DARK),sp(' ',SUIT_DARK),sp(' '),sp(' '),sp(' ',SUIT_DARK),sp(' ',SUIT_LINE),sp(' ',SUIT_DARK),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SUIT_DARK),sp(' ',SUIT_DARK),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SUIT_DARK),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SUIT_DARK),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
    # Shoes
    [sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SHOE_DARK),sp(' ',SHOE_DARK),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ',SHOE_DARK),sp(' '),sp(' '),sp(' '),sp(' '),sp(' '),sp(' ')],
])

# ── BOTH TOGETHER (side by side) ──
def get_both_art():
    """Return combined art: woman on left, man on right."""
    combined = []
    max_h = max(len(WOMAN_ART), len(MAN_ART))
    for i in range(max_h):
        left = WOMAN_ART[i] if i < len(WOMAN_ART) else [sp(' ')] * 18
        right = MAN_ART[i] if i < len(MAN_ART) else [sp(' ')] * 18
        row = left + [sp(' ')] * 3 + right  # gap between them
        combined.append(row)
    return combined

# ============================================================
# SCENES
# ============================================================
SCENES = [
    {
        "title": "CHƯƠNG 1",
        "character": "woman",
        "art": WOMAN_ART,
        "name": " Linh",
        "name_color": DRESS_PINK,
        "caption_lines": ["Ngày đó, Linh là cô gái", "đẹp nhất thành phố."],
        "tts_text": "Ngày đó, Linh là cô gái đẹp nhất thành phố. Vẻ đẹp không chỉ ở khuôn mặt, mà còn ở trái tim nhân hậu.",
        "bg_effect": "hearts",
    },
    {
        "title": "CHƯƠNG 2",
        "character": "man",
        "art": MAN_ART,
        "name": "Dũng",
        "name_color": GOLD,
        "caption_lines": ["Còn Dũng là tổng tài", "giàu nhất thành phố."],
        "tts_text": "Còn Dũng là tổng tài giàu nhất thành phố. Anh có tất cả, trừ một điều: tình yêu thực sự.",
        "bg_effect": "sparkle",
    },
    {
        "title": "CHƯƠNG 3",
        "title_color": PINK_GLOW,
        "character": "both",
        "art": get_both_art(),
        "caption_lines": ["Họ gặp nhau", "tại bữa tiệc đêm đó..."],
        "tts_text": "Họ gặp nhau tại bữa tiệc đêm đó. ánh mắt lần đầu chạm nhau, cả thế giới như dừng lại.",
        "bg_effect": "sparkle",
    },
    {
        "title": "CHƯƠNG 4",
        "title_color": PINK_GLOW,
        "character": "both",
        "art": get_both_art(),
        "caption_lines": ["Không tiền bạc, không địa vị.", "Chỉ có hai trái tim."],
        "tts_text": "Không tiền bạc, không địa vị. Chỉ có hai trái tim rung động. Tình yêu không cần vật chất.",
        "bg_effect": "hearts",
    },
    {
        "title": "CHƯƠNG 5",
        "title_color": GOLD,
        "character": "man",
        "art": MAN_ART,
        "caption_lines": ["Dũng quyết định", "bỏ lại tất cả."],
        "tts_text": "Dũng quyết định bỏ lại tất cả. Đế chế tiền bạc không bằng nụ cười của cô ấy.",
        "bg_effect": "sparkle",
    },
    {
        "title": "CHƯƠNG 6",
        "title_color": DRESS_PINK,
        "character": "woman",
        "art": WOMAN_ART,
        "caption_lines": ["Linh chờ đợi", "một tình yêu chân thật."],
        "tts_text": "Linh chờ đợi một tình yêu chân thật. Không phải vì anh giàu, mà vì anh hiểu trái tim cô.",
        "bg_effect": "hearts",
    },
    {
        "title": "CHƯƠNG 7",
        "title_color": PINK_GLOW,
        "character": "both",
        "art": get_both_art(),
        "caption_lines": ["Hai đường cong", "gặp nhau tại đỉnh."],
        "tts_text": "Hai đường cong cuộc đời gặp nhau tại đỉnh. Từ nay, không còn đơn độc.",
        "bg_effect": "hearts",
    },
    {
        "title": "PHẦN KẾT",
        "title_color": GOLD,
        "character": "both",
        "art": get_both_art(),
        "caption_lines": ["TÌNH YÊU KHÔNG CÓ", "GIÁ. NHƯNG KHÔNG CÓ NÓ,"],
        "caption_lines2": ["MỌI THỨ ĐỀU CÓ GIÁ."],
        "tts_text": "Tình yêu không có giá. Nhưng không có nó, mọi thứ đều có giá. Từ hai, thành một. Không gì là không thể.",
        "bg_effect": "hearts",
    },
]

# ============================================================
# BACKGROUND EFFECTS
# ============================================================
import math, random

def draw_hearts(draw, t, alpha=0.3):
    """Draw floating hearts in background."""
    for i in range(12):
        x = (i * 97 + int(t * 30)) % W
        y = (i * 157 + int(t * 20)) % H
        s = 8 + (i % 5) * 3
        a = int(40 * alpha * (0.5 + 0.5 * math.sin(t * 2 + i)))
        if a > 0:
            draw.text((x, y), "♥", fill=PINK_GLOW + (a,), font=get_mono(s))

def draw_sparkle(draw, t, alpha=0.3):
    """Draw sparkling dots."""
    for i in range(20):
        x = (i * 59 + int(t * 15)) % W
        y = (i * 103 + int(t * 10)) % H
        phase = math.sin(t * 3 + i * 0.7)
        if phase > 0.3:
            a = int(80 * alpha * phase)
            s = 2 + int(4 * phase)
            draw.ellipse([x-s, y-s, x+s, y+s], fill=GOLD + (a,))

def draw_bg(draw, t, effect, alpha=1.0):
    if effect == "hearts":
        draw_hearts(draw, t, alpha)
    elif effect == "sparkle":
        draw_sparkle(draw, t, alpha)

# ============================================================
# CHARACTER RENDERER
# ============================================================
def render_character(draw, art, cx, cy, scale=8, y_offset=0):
    """Render ASCII art character centered at (cx, cy) with given scale.
    Uses block chars (█) for filled areas with per-pixel colors."""
    rows = len(art)
    cols = max(len(r) for r in art)
    total_w = cols * scale
    start_x = cx - total_w // 2
    start_y = cy - rows * scale // 2 + y_offset

    mono_fnt = get_mono(scale)

    for ri, row in enumerate(art):
        y = start_y + ri * scale
        if y < 0 or y > H: continue
        for ci, (ch, color) in enumerate(row):
            x = start_x + ci * scale
            if x < 0 or x > W: continue
            if ch == BLOCK:
                draw.text((x, y), BLOCK, fill=color, font=mono_fnt)
            elif ch and ch.strip() and ch != BLOCK:
                draw.text((x, y), ch, fill=color, font=mono_fnt)

# ============================================================
# FRAME RENDERER
# ============================================================
def render_frame(scene_idx, scene, t, scene_t, frame_num):
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img, "RGBA")

    total_scene_dur = 5.0
    # Fade in/out
    alpha = 1.0
    if scene_t < 0.5:
        alpha = scene_t / 0.5
    elif scene_t > total_scene_dur - 0.5:
        alpha = (total_scene_dur - scene_t) / 0.5

    # ── Background effects ──
    draw_bg(draw, t, scene.get("bg_effect", "hearts"), alpha * 0.6)

    # ── Title ──
    title = scene["title"]
    title_color = scene.get("title_color", DIM)
    title_fnt = get_vi(36)
    tb = draw.textbbox((0,0), title, font=title_fnt)
    tw = tb[2] - tb[0]
    tc = tuple(int(c * alpha) for c in title_color) + (int(255 * alpha),)
    draw.text(((W - tw)//2, 120), title, font=title_fnt, fill=tc)

    # ── Character ──
    char_type = scene["character"]
    art = scene["art"]

    if char_type == "both":
        # Both side by side — smaller scale
        s = 6
        # Calculate combined width
        cols_w = max(len(r) for r in WOMAN_ART)
        cols_m = max(len(r) for r in MAN_ART)
        gap = 3
        total_cols = cols_w + gap + cols_m
        total_w = total_cols * s
        start_x = (W - total_w) // 2

        # Woman
        render_character(draw, WOMAN_ART, start_x + cols_w * s // 2, H // 2 - 100, scale=s)
        # Man
        render_character(draw, MAN_ART, start_x + cols_w * s + gap * s + cols_m * s // 2, H // 2 - 100, scale=s)

        # Names
        if "name" not in scene:
            name_fnt = get_vi(32)
            woman_name = "Linh"
            man_name = "Dũng"
            wn = draw.textbbox((0,0), woman_name, font=name_fnt)
            mn = draw.textbbox((0,0), man_name, font=name_fnt)
            draw.text(((W - total_w)//2 + (cols_w*s - wn[2]+wn[0])//2, H//2 - 100 + cols_w * s + 40),
                      woman_name, font=name_fnt, fill=DRESS_PINK + (int(255*alpha),))
            draw.text(((W - total_w)//2 + cols_w*s + gap*s + (cols_m*s - mn[2]+mn[0])//2, H//2 - 100 + cols_m * s + 40),
                      man_name, font=name_fnt, fill=GOLD + (int(255*alpha),))
    else:
        render_character(draw, art, W // 2, H // 2 - 80, scale=9)
        # Character name
        if "name" in scene:
            name_fnt = get_vi(40)
            nb = draw.textbbox((0,0), scene["name"], font=name_fnt)
            nw = nb[2] - nb[0]
            nc = scene.get("name_color", WHITE)
            draw.text(((W - nw)//2, H//2 + 160), scene["name"], font=name_fnt,
                      fill=nc + (int(255*alpha),))

    # ── Caption ──
    cap_fnt = get_vi(38)
    cap_y = H - 400
    for ci, line in enumerate(scene["caption_lines"]):
        cb = draw.textbbox((0,0), line, font=cap_fnt)
        cw = cb[2] - cb[0]
        ca = int(255 * min(1.0, alpha * (1.0 - ci * 0.1)))
        draw.text(((W - cw)//2, cap_y + ci * 55), line, font=cap_fnt, fill=WHITE + (ca,))

    if "caption_lines2" in scene:
        for ci, line in enumerate(scene["caption_lines2"]):
            cb = draw.textbbox((0,0), line, font=cap_fnt)
            cw = cb[2] - cb[0]
            ca = int(255 * min(1.0, alpha * (1.0 - (len(scene["caption_lines"]) + ci) * 0.1)))
            draw.text(((W - cw)//2, cap_y + (len(scene["caption_lines"]) + ci) * 55), line,
                      font=cap_fnt, fill=GOLD + (ca,))

    # ── Progress bar ──
    bar_y = H - 120
    bar_w = W - 200
    bar_x = 100
    total_frames = sum(5 * FPS for _ in SCENES)
    progress = frame_num / max(1, total_frames)
    draw.rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + 6], fill=(30, 30, 40))
    draw.rectangle([bar_x, bar_y, bar_x + int(bar_w * progress), bar_y + 6],
                   fill=PINK_GLOW + (180,))

    # Scene dots
    dot_y = bar_y + 30
    dot_sp = 36
    dot_sx = W//2 - (len(SCENES) * dot_sp) // 2
    for si in range(len(SCENES)):
        dx = dot_sx + si * dot_sp
        r = 6 if si == scene_idx else 4
        dc = PINK_GLOW if si == scene_idx else (50, 50, 60)
        draw.ellipse([dx-r, dot_y-r, dx+r, dot_y+r], fill=dc)

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
    # Get duration
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                         "-of", "default=noprint_wrappers=1:nokey=1", full],
                        capture_output=True, text=True)
    return full, float(r.stdout.strip())

# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("💕 ASCII LOVE STORY: Tình Yêu Đường Cong")
    print("=" * 60)

    # Step 1: TTS
    print("\n🎙 Generating Vietnamese TTS...")
    asyncio.run(generate_all_tts())

    # Step 2: Get total audio duration
    print("\n🎵 Concatenating audio...")
    audio_path, audio_dur = concat_audio()
    print(f"   Total audio: {audio_dur:.1f}s")

    scene_dur = audio_dur / len(SCENES)
    print(f"   Per scene: ~{scene_dur:.1f}s")

    # Step 3: Render frames
    print("\n🎨 Rendering frames...")
    frame_num = 0
    for si, scene in enumerate(SCENES):
        scene_frames = int(scene_dur * FPS)
        print(f"   Scene {si+1}/{len(SCENES)}: {scene['title']} ({scene_frames} frames)")
        for fi in range(scene_frames):
            t = frame_num / FPS
            scene_t = fi / FPS
            img = render_frame(si, scene, t, scene_t, frame_num)
            img.save(os.path.join(FRAMES_DIR, f"f_{frame_num:05d}.png"))
            frame_num += 1
            if fi % (FPS * 2) == 0:
                pct = 100 * frame_num / max(1, int(audio_dur * FPS))
                print(f"      {pct:.0f}% ({frame_num} frames)")

    print(f"   Total: {frame_num} frames")

    # Step 4: Encode
    print("\n🎞 Encoding MP4...")
    out = os.path.join(OUTPUT, "tinh_yeu_duong_cong.mp4")
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
