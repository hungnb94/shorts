#!/usr/bin/env python3
"""
ASCII Love Story v5: Realistic Portrait Quality
Vector 3000x3000 realistic proportions → 500x700 ASCII grid (350K cells)
Proper anatomy, shading, hair strands, facial detail
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, subprocess, asyncio, edge_tts, math

OUTPUT = "/Users/hung/code/ai/shorts/output/ascii_love_v5"
FRAMES_DIR = os.path.join(OUTPUT, "frames")
AUDIO_DIR = os.path.join(OUTPUT, "audio")
os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 24

VI_FONT = "/Library/Fonts/Arial Unicode.ttf"
VI_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
MONO = "/System/Library/Fonts/Menlo.ttc"

def fnt(path, size):
    try: return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

BLOCK = '\u2588'

# ============================================================
# REALISTIC COLOR PALETTE
# ============================================================
class C:
    # Skin tones (5 shades for realistic shading)
    SKN_H  = (252, 225, 200)  # highlight
    SKN_L  = (242, 212, 185)  # light
    SKN    = (230, 198, 168)  # base
    SKN_M  = (210, 175, 145)  # mid shadow
    SKN_D  = (188, 152, 125)  # deep shadow
    SKN_DD = (165, 130, 105)  # darkest (nostrils, ear canal)

    # Hair
    HBK  = (25, 20, 30)
    HBK2 = (38, 30, 42)
    HSH  = (65, 52, 75)   # shine
    HHI  = (90, 72, 100)  # highlight

    # Eyes
    EW   = (240, 240, 245)
    EIR  = (55, 110, 175)   # blue iris
    EIR2 = (35, 75, 130)    # iris edge
    EPUP = (12, 10, 18)
    EHIL = (255, 255, 255)  # highlight
    EHIL2= (160, 195, 235)  # secondary highlight

    # Face
    LIP  = (195, 80, 80)
    LIPL = (210, 105, 105)
    LIPD = (170, 62, 62)
    LIPHL= (225, 130, 130)
    BROW = (30, 24, 34)
    BLUSH= (228, 175, 165)

    # Nose shadow
    NSHAD = (200, 168, 140)
    NHI   = (245, 218, 195)  # nose bridge highlight

    # Dress
    DP   = (215, 105, 150)
    DL   = (235, 155, 185)
    DD   = (185, 78, 122)
    DHL  = (248, 190, 210)
    DSH  = (168, 65, 108)

    # Suit
    SD   = (18, 18, 36)
    SL   = (40, 40, 62)
    SHL  = (58, 58, 82)
    SHT  = (230, 230, 236)
    TIE  = (168, 35, 35)
    TIEL = (198, 58, 58)
    BLTG = (200, 178, 52)

    SHO  = (30, 26, 38)

    BG   = (8, 8, 14)
    PG   = (255, 152, 182)
    GD   = (255, 218, 0)
    WH   = (255, 255, 255)
    DM   = (90, 90, 110)


# ============================================================
# HELPERS
# ============================================================
def grad_ellipse(d, bbox, c1, c2, steps=16):
    x0,y0,x1,y1 = bbox
    cx,cy = (x0+x1)/2,(y0+y1)/2
    rx,ry = (x1-x0)/2,(y1-y0)/2
    for i in range(steps,0,-1):
        t = i/steps
        r = int(c1[0]*(1-t)+c2[0]*t)
        g = int(c1[1]*(1-t)+c2[1]*t)
        b = int(c1[2]*(1-t)+c2[2]*t)
        d.ellipse([cx-rx*t,cy-ry*t,cx+rx*t,cy+ry*t],fill=(r,g,b))

def shadow(d, bbox, intensity=0.3):
    """Draw a soft shadow ellipse."""
    x0,y0,x1,y1 = bbox
    cx,cy = (x0+x1)/2,(y0+y1)/2
    rx,ry = (x1-x0)/2,(y1-y0)/2
    for i in range(8):
        t = i/8
        a = int(40*intensity*(1-t))
        d.ellipse([cx-rx*(1+t*0.3),cy-ry*(1+t*0.3),
                    cx+rx*(1+t*0.3),cy+ry*(1+t*0.3)],
                   fill=(40,35,50,a))


# ============================================================
# WOMAN — Realistic proportions (3000x3000)
# Head:body ≈ 1:7, anatomical features
# ============================================================
def draw_woman():
    sz = 3000
    img = Image.new("RGB", (sz, sz), C.BG)
    d = ImageDraw.Draw(img)
    cx = sz // 2

    # === PROPORTIONS (3000px total body height) ===
    # Head top: 200, Chin: 520 (head height = 320)
    # Shoulders: 580, Bust: 800, Waist: 1050, Hips: 1300
    # Knees: 2000, Feet: 2700
    # Head width: 240 (radius), Body width varies

    head_top = 200
    head_cy = 360   # head center
    chin = 520
    shoulder_y = 600
    bust_y = 820
    waist_y = 1100
    hip_y = 1350
    knee_y = 2050
    feet_y = 2650

    # ── HAIR BEHIND (long flowing) ──
    d.ellipse([cx-260, head_top-30, cx+260, chin+60], fill=C.HBK)
    # Long hair flowing down back
    d.polygon([(cx-250,chin-20),(cx-310,800),(cx-340,1200),(cx-300,1700),
               (cx-260,1800),(cx-220,1500),(cx-230,1000),(cx-240,600)], fill=C.HBK)
    d.polygon([(cx+250,chin-20),(cx+310,800),(cx+340,1200),(cx+300,1700),
               (cx+260,1800),(cx+220,1500),(cx+230,1000),(cx+240,600)], fill=C.HBK)
    # Hair shine streaks
    for dx in [-180, -60, 60, 180]:
        d.arc([cx+dx-40, head_top+20, cx+dx+40, head_cy+40], 220, 320, fill=C.HSH, width=3)

    # ── NECK + COLLARBONE ──
    d.polygon([(cx-65,chin-5),(cx+65,chin-5),(cx+70,shoulder_y+40),(cx-70,shoulder_y+40)], fill=C.SKN)
    d.polygon([(cx-55,chin-5),(cx+55,chin-5),(cx+48,chin+40),(cx-48,chin+40)], fill=C.SKN_M)
    # Collarbone shadows
    d.line([(cx-120,shoulder_y+10),(cx-30,shoulder_y-5)], fill=C.SKN_D, width=4)
    d.line([(cx+120,shoulder_y+10),(cx+30,shoulder_y-5)], fill=C.SKN_D, width=4)
    # Collarbone highlights
    d.line([(cx-110,shoulder_y+5),(cx-25,shoulder_y-10)], fill=C.SKN_H, width=2)
    d.line([(cx+110,shoulder_y+5),(cx+25,shoulder_y-10)], fill=C.SKN_H, width=2)

    # ── SHOULDERS (wider, feminine) ──
    d.polygon([(cx-350,shoulder_y),(cx+350,shoulder_y),
               (cx+320,shoulder_y+80),(cx-320,shoulder_y+80)], fill=C.DP)

    # ── FACE (realistic oval, not circle) ──
    # Wider at cheekbones, narrower at chin
    d.ellipse([cx-220, head_top+40, cx+220, chin+40], fill=C.SKN_L)
    # Jawline — V-shape
    d.polygon([(cx-200,chin-60),(cx-100,chin+10),(cx,chin+25),
               (cx+100,chin+10),(cx+200,chin-60)], fill=C.SKN)
    # Cheekbone shadow
    d.ellipse([cx-210,chin-80,cx-80,chin+10], fill=C.SKN_M)
    d.ellipse([cx+80,chin-80,cx+210,chin+10], fill=C.SKN_M)
    # Cheek blush
    d.ellipse([cx-190,head_cy+20,cx-80,head_cy+80], fill=C.BLUSH)
    d.ellipse([cx+80,head_cy+20,cx+190,head_cy+80], fill=C.BLUSH)

    # ── HAIR BANGS (realistic, not helmet) ──
    d.polygon([(cx-220,head_top+30),(cx-180,head_top),(cx-80,head_top+20),
               (cx,head_top+10),(cx+80,head_top+20),(cx+180,head_top),
               (cx+220,head_top+30),(cx+210,head_top+200),(cx+120,180),
               (cx,200),(cx-120,180),(cx-210,200)], fill=C.HBK)
    # Side hair framing face
    d.polygon([(cx-220,head_top+30),(cx-250,head_top+60),(cx-260,chin+100),
               (cx-230,chin+60),(cx-215,head_top+150)], fill=C.HBK)
    d.polygon([(cx+220,head_top+30),(cx+250,head_top+60),(cx+260,chin+100),
               (cx+230,chin+60),(cx+215,head_top+150)], fill=C.HBK)

    # ── EARS (partially visible under hair) ──
    for ex in [cx-215, cx+215]:
        d.ellipse([ex-20, head_cy-25, ex+20, head_cy+35], fill=C.SKN)
        d.ellipse([ex-10, head_cy-15, ex+10, head_cy+25], fill=C.SKN_M)

    # ── EYES (realistic proportions — smaller than anime) ──
    eye_cy = head_cy - 10
    for ex in [cx-95, cx+95]:
        # Eye socket shadow
        d.ellipse([ex-55, eye_cy-20, ex+55, eye_cy+28], fill=C.SKN_D)
        # Eye white
        d.ellipse([ex-42, eye_cy-12, ex+42, eye_cy+20], fill=C.EW)
        # Iris — gradient
        grad_ellipse(d, [ex-22, eye_cy-8, ex+22, eye_cy+16], C.EIR, C.EIR2, steps=10)
        # Pupil
        d.ellipse([ex-10, eye_cy, ex+10, eye_cy+14], fill=C.EPUP)
        # Main highlight
        d.ellipse([ex-6, eye_cy-2, ex+2, eye_cy+6], fill=C.EHIL)
        # Secondary highlight
        d.ellipse([ex+6, eye_cy+6, ex+14, eye_cy+12], fill=C.EHIL2)
        # Upper eyelid — thicker
        d.arc([ex-44, eye_cy-16, ex+44, eye_cy+22], 192, 348, fill=C.BROW, width=6)
        # Lower eyelid — thin
        d.arc([ex-36, eye_cy-8, ex+36, eye_cy+20], 12, 168, fill=C.SKN_D, width=2)
        # Eyelid crease
        d.arc([ex-38, eye_cy-28, ex+38, eye_cy+8], 200, 340, fill=C.SKN_M, width=2)
        # Eyelashes — upper (3-4 individual lashes)
        for angle, length in [(195,14),(205,16),(215,12),(225,10),(325,10),(335,12),(345,14)]:
            rad = math.radians(angle)
            lx1 = ex + int(42 * math.cos(rad))
            ly1 = eye_cy + int(16 * math.sin(rad))
            lx2 = ex + int((42+length) * math.cos(rad))
            ly2 = eye_cy + int((16+length*0.6) * math.sin(rad))
            d.line([(lx1,ly1),(lx2,ly2)], fill=C.BROW, width=2)

    # ── EYEBROWS (realistic arch) ──
    for bx in [cx-95, cx+95]:
        d.arc([bx-48, eye_cy-55, bx+48, eye_cy-25], 200, 340, fill=C.BROW, width=5)
        # Brow hair texture
        for i in range(5):
            t = i / 5
            mx = bx - 40 + int(80 * t)
            my = eye_cy - 42 + int(5 * math.sin(t * math.pi))
            d.line([(mx, my), (mx+6, my-3)], fill=C.BROW, width=1)

    # ── NOSE (realistic: bridge + tip + nostrils) ──
    nose_top = eye_cy + 20
    nose_tip = chin - 100
    # Bridge highlight
    d.line([(cx-4, nose_top), (cx-2, nose_tip-10)], fill=C.NHI, width=5)
    d.line([(cx+4, nose_top), (cx+2, nose_tip-10)], fill=C.NHI, width=5)
    # Nose tip — rounded
    d.ellipse([cx-18, nose_tip-15, cx+18, nose_tip+10], fill=C.SKN)
    # Nostrils
    d.ellipse([cx-20, nose_tip-5, cx-8, nose_tip+8], fill=C.SKN_DD)
    d.ellipse([cx+8, nose_tip-5, cx+20, nose_tip+8], fill=C.SKN_DD)
    # Shadow under nose tip
    d.arc([cx-22, nose_tip, cx+22, nose_tip+25], 10, 170, fill=C.SKN_D, width=2)
    # Side shadows
    d.line([(cx-16, nose_top+20), (cx-20, nose_tip-10)], fill=C.SKN_D, width=2)
    d.line([(cx+16, nose_top+20), (cx+20, nose_tip-10)], fill=C.SKN_D, width=2)

    # ── LIPS (realistic: cupid's bow + full lower lip) ──
    mouth_y = nose_tip + 55
    # Upper lip — cupid's bow
    d.polygon([(cx-45, mouth_y-5), (cx-15, mouth_y-12), (cx, mouth_y-8),
               (cx+15, mouth_y-12), (cx+45, mouth_y-5), (cx, mouth_y+2)], fill=C.LIP)
    # Lower lip — full
    d.ellipse([cx-38, mouth_y, cx+38, mouth_y+22], fill=C.LIPL)
    # Lip highlight
    d.ellipse([cx-15, mouth_y+3, cx+15, mouth_y+12], fill=C.LIPHL)
    # Lip line
    d.line([(cx-42, mouth_y-3), (cx+42, mouth_y-3)], fill=C.LIPD, width=1)
    # Shadow under lower lip
    d.arc([cx-30, mouth_y+18, cx+30, mouth_y+35], 10, 170, fill=C.SKN_D, width=2)

    # ── DRESS (realistic S-curve with fabric detail) ──
    # Bust
    d.polygon([(cx-340,shoulder_y+60),(cx+340,shoulder_y+60),
               (cx+300,bust_y+60),(cx-300,bust_y+60)], fill=C.DP)
    d.ellipse([cx-320,bust_y-20,cx-80,bust_y+80], fill=C.DL)
    d.ellipse([cx+80,bust_y-20,cx+320,bust_y+80], fill=C.DL)
    # Bust shadow
    d.ellipse([cx-260,bust_y+20,cx-100,bust_y+70], fill=C.DD)
    d.ellipse([cx+100,bust_y+20,cx+260,bust_y+70], fill=C.DD)

    # Waist — narrow
    d.polygon([(cx-300,bust_y+50),(cx+300,bust_y+50),
               (cx+160,waist_y),(cx-160,waist_y)], fill=C.DP)
    d.polygon([(cx-200,bust_y+100),(cx+200,bust_y+100),
               (cx+170,waist_y-50),(cx-170,waist_y-50)], fill=C.DD)

    # Hips — wide
    d.polygon([(cx-160,waist_y-10),(cx+160,waist_y-10),
               (cx+380,hip_y+50),(cx-380,hip_y+50)], fill=C.DP)
    d.ellipse([cx-390,waist_y+20,cx-60,hip_y+60], fill=C.DL)
    d.ellipse([cx+60,waist_y+20,cx+390,hip_y+60], fill=C.DL)

    # Skirt
    d.polygon([(cx-380,hip_y+40),(cx+380,hip_y+40),
               (cx+420,feet_y-40),(cx-420,feet_y-40)], fill=C.DP)
    # Fabric folds — vertical shadows
    for fx in [-300, -150, 0, 150, 300]:
        d.polygon([(cx+fx-30,hip_y+80),(cx+fx+30,hip_y+80),
                   (cx+fx+20,feet_y-80),(cx+fx-40,feet_y-80)], fill=C.DD)
    # Skirt highlight
    d.polygon([(cx-60,hip_y+60),(cx+60,hip_y+60),
               (cx+80,feet_y-60),(cx-80,feet_y-60)], fill=C.DHL)

    # ── ARMS (realistic with elbow + hand) ──
    # Left arm
    arm_pts_l = [
        (cx-340, shoulder_y+20),   # shoulder
        (cx-400, shoulder_y+100),  # upper arm
        (cx-420, bust_y+80),       # elbow
        (cx-400, waist_y+40),      # forearm
        (cx-380, waist_y+160),     # wrist
    ]
    for i in range(len(arm_pts_l)-1):
        x1,y1 = arm_pts_l[i]
        x2,y2 = arm_pts_l[i+1]
        w = max(30, 55 - i*8)  # tapering
        d.polygon([(x1-w,y1),(x1+w,y1),(x2+w,y2),(x2-w,y2)], fill=C.SKN)
    # Hand — fingers
    hand_x, hand_y = cx-380, waist_y+170
    d.ellipse([hand_x-25,hand_y-10,hand_x+25,hand_y+40], fill=C.SKN)
    for fi in range(4):
        fx = hand_x - 15 + fi * 10
        d.ellipse([fx-4, hand_y+35, fx+4, hand_y+60], fill=C.SKN)
    d.ellipse([hand_x+20, hand_y+20, hand_x+35, hand_y+50], fill=C.SKN)  # thumb

    # Right arm (same pattern)
    arm_pts_r = [(cx+340,shoulder_y+20),(cx+400,shoulder_y+100),
                 (cx+420,bust_y+80),(cx+400,waist_y+40),(cx+380,waist_y+160)]
    for i in range(len(arm_pts_r)-1):
        x1,y1 = arm_pts_r[i]
        x2,y2 = arm_pts_r[i+1]
        w = max(30, 55 - i*8)
        d.polygon([(x1-w,y1),(x1+w,y1),(x2+w,y2),(x2-w,y2)], fill=C.SKN)
    hand_x2 = cx+380
    d.ellipse([hand_x2-25,hand_y-10,hand_x2+25,hand_y+40], fill=C.SKN)
    for fi in range(4):
        fx = hand_x2 - 15 + fi * 10
        d.ellipse([fx-4, hand_y+35, fx+4, hand_y+60], fill=C.SKN)
    d.ellipse([hand_x2-35, hand_y+20, hand_x2-20, hand_y+50], fill=C.SKN)

    # ── SHOES ──
    d.ellipse([cx-180,feet_y-30,cx-60,feet_y+20], fill=C.SHO)
    d.ellipse([cx+60,feet_y-30,cx+180,feet_y+20], fill=C.SHO)

    return img


# ============================================================
# MAN — Realistic proportions (3000x3000)
# Broader shoulders, square jaw, taller
# ============================================================
def draw_man():
    sz = 3000
    img = Image.new("RGB", (sz, sz), C.BG)
    d = ImageDraw.Draw(img)
    cx = sz // 2

    head_top = 150
    head_cy = 340
    chin = 530
    shoulder_y = 620
    chest_y = 800
    waist_y = 1100
    hip_y = 1300
    knee_y = 2000
    feet_y = 2650

    # ── SUIT SHOULDERS (broad, masculine) ──
    d.polygon([(cx-420,shoulder_y-20),(cx+420,shoulder_y-20),
               (cx+400,shoulder_y+100),(cx-400,shoulder_y+100)], fill=C.SD)

    # ── NECK (thicker, masculine) ──
    d.polygon([(cx-80,chin-5),(cx+80,chin-5),(cx+85,shoulder_y+30),(cx-85,shoulder_y+30)], fill=C.SKN)
    d.polygon([(cx-65,chin-5),(cx+65,chin-5),(cx+55,chin+35),(cx-55,chin+35)], fill=C.SKN_M)
    # Neck tendon shadows
    d.line([(cx-40,chin+10),(cx-45,shoulder_y+10)], fill=C.SKN_D, width=3)
    d.line([(cx+40,chin+10),(cx+45,shoulder_y+10)], fill=C.SKN_D, width=3)

    # ── FACE (square jaw, masculine) ──
    d.ellipse([cx-230,head_top+30,cx+230,chin+30], fill=C.SKN_L)
    # Jaw — square
    d.polygon([(cx-210,chin-80),(cx-160,chin+15),(cx-60,chin+30),
               (cx,chin+35),(cx+60,chin+30),(cx+160,chin+15),(cx+210,chin-80)], fill=C.SKN)
    # Jaw shadow
    d.polygon([(cx-180,chin-40),(cx-120,chin+20),(cx,chin+30),
               (cx+120,chin+20),(cx+180,chin-40),(cx+140,chin-20),(cx,chin-10),(cx-140,chin-20)], fill=C.SKN_M)
    # Cheekbone
    d.line([(cx-180,head_cy-20),(cx-120,head_cy+10)], fill=C.SKN_D, width=3)
    d.line([(cx+180,head_cy-20),(cx+120,head_cy+10)], fill=C.SKN_D, width=3)

    # ── HAIR (short, neat, with texture) ──
    d.ellipse([cx-235,head_top-10,cx+235,head_cy+60], fill=C.HBK)
    d.polygon([(cx-230,head_top+40),(cx-190,head_top),(cx-80,head_top+10),
               (cx,head_top+5),(cx+80,head_top+10),(cx+190,head_top),
               (cx+230,head_top+40),(cx+220,head_top+160),(cx+130,140),
               (cx,150),(cx-130,140),(cx-220,160)], fill=C.HBK)
    # Hair texture — individual strokes
    for hx in range(-200, 201, 25):
        for hy_offset in range(0, 120, 20):
            x = cx + hx
            y = head_top + 20 + hy_offset
            d.line([(x, y), (x+3, y+12)], fill=C.HBK2, width=2)
    # Hair shine
    d.arc([cx-150,head_top,cx+150,head_cy-20], 210, 330, fill=C.HSH, width=4)
    # Side hair
    d.polygon([(cx-230,head_top+40),(cx-255,head_top+60),(cx-260,chin-20),
               (cx-235,chin-50),(cx-225,head_top+100)], fill=C.HBK)
    d.polygon([(cx+230,head_top+40),(cx+255,head_top+60),(cx+260,chin-20),
               (cx+235,chin-50),(cx+225,head_top+100)], fill=C.HBK)

    # ── EARS ──
    for ex in [cx-225, cx+225]:
        d.ellipse([ex-18,head_cy-30,ex+18,head_cy+35], fill=C.SKN)
        d.ellipse([ex-8,head_cy-18,ex+8,head_cy+22], fill=C.SKN_M)

    # ── EYES (slightly narrower than woman, sharper) ──
    eye_cy = head_cy - 5
    for ex in [cx-100, cx+100]:
        d.ellipse([ex-48,eye_cy-18,ex+48,eye_cy+25], fill=C.SKN_D)
        d.ellipse([ex-38,eye_cy-10,ex+38,eye_cy+18], fill=C.EW)
        grad_ellipse(d, [ex-20,eye_cy-6,ex+20,eye_cy+14], (50,85,55), (28,50,32), steps=8)
        d.ellipse([ex-9,eye_cy+1,ex+9,eye_cy+13], fill=C.EPUP)
        d.ellipse([ex-5,eye_cy,ex+3,eye_cy+5], fill=C.EHIL)
        d.arc([ex-40,eye_cy-14,ex+40,eye_cy+20], 194, 346, fill=C.BROW, width=6)
        d.arc([ex-32,eye_cy-6,ex+32,eye_cy+16], 12, 168, fill=C.SKN_D, width=2)
        d.arc([ex-35,eye_cy-24,ex+35,eye_cy+6], 200, 340, fill=C.SKN_M, width=2)
        # Lashes
        for angle in [198, 208, 218, 228, 332, 342]:
            rad = math.radians(angle)
            lx1 = ex + int(38*math.cos(rad))
            ly1 = eye_cy + int(14*math.sin(rad))
            lx2 = ex + int(50*math.cos(rad))
            ly2 = eye_cy + int(20*math.sin(rad))
            d.line([(lx1,ly1),(lx2,ly2)], fill=C.BROW, width=2)

    # ── EYEBROWS (thicker, straighter — masculine) ──
    for bx in [cx-100, cx+100]:
        d.polygon([(bx-50,eye_cy-48),(bx+50,eye_cy-42),(bx+48,eye_cy-32),(bx-48,eye_cy-38)], fill=C.BROW)

    # ── NOSE (stronger bridge) ──
    nose_top = eye_cy + 25
    nose_tip = chin - 80
    d.line([(cx-5,nose_top),(cx-3,nose_tip-8)], fill=C.NHI, width=6)
    d.line([(cx+5,nose_top),(cx+3,nose_tip-8)], fill=C.NHI, width=6)
    d.ellipse([cx-22,nose_tip-12,cx+22,nose_tip+8], fill=C.SKN)
    d.ellipse([cx-24,nose_tip-2,cx-10,nose_tip+10], fill=C.SKN_DD)
    d.ellipse([cx+10,nose_tip-2,cx+24,nose_tip+10], fill=C.SKN_DD)
    d.arc([cx-25,nose_tip+2,cx+25,nose_tip+25], 10, 170, fill=C.SKN_D, width=3)
    d.line([(cx-20,nose_top+25),(cx-25,nose_tip-8)], fill=C.SKN_D, width=3)
    d.line([(cx+20,nose_top+25),(cx+25,nose_tip-8)], fill=C.SKN_D, width=3)

    # ── MOUTH (slight smile) ──
    mouth_y = nose_tip + 50
    d.arc([cx-50,mouth_y-8,cx+50,mouth_y+12], 10, 170, fill=C.LIP, width=4)
    d.polygon([(cx-35,mouth_y+4),(cx+35,mouth_y+4),(cx+28,mouth_y+14),(cx-28,mouth_y+14)], fill=C.LIPD)

    # ── SHIRT COLLAR ──
    d.polygon([(cx-80,chin-5),(cx-50,chin-10),(cx,60),(cx+50,chin-10),(cx+80,chin-5),
               (cx+60,180),(cx,210),(cx-60,180)], fill=C.SHT)
    d.polygon([(cx-80,chin-5),(cx-130,chin+20),(cx-90,100),(cx-60,60)], fill=C.SHT)
    d.polygon([(cx+80,chin-5),(cx+130,chin+20),(cx+90,100),(cx+60,60)], fill=C.SHT)

    # ── TIE ──
    d.polygon([(cx-22,60),(cx+22,60),(cx+15,600),(cx-15,600)], fill=C.TIE)
    d.polygon([(cx-22,60),(cx+22,60),(cx+12,100),(cx-12,100)], fill=C.TIEL)
    d.polygon([(cx-18,40),(cx+18,40),(cx+12,68),(cx-12,68)], fill=C.TIEL)

    # ── SUIT JACKET ──
    d.polygon([(cx-420,shoulder_y-20),(cx-80,chin-5),(cx-60,180),(cx-80,600),(cx-440,620)], fill=C.SD)
    d.polygon([(cx+420,shoulder_y-20),(cx+80,chin-5),(cx+60,180),(cx+80,600),(cx+440,620)], fill=C.SD)
    d.polygon([(cx-80,chin-5),(cx-130,chin+20),(cx-110,300),(cx-80,250)], fill=C.SL)
    d.polygon([(cx+80,chin-5),(cx+130,chin+20),(cx+110,300),(cx+80,250)], fill=C.SL)
    # Lapel
    d.polygon([(cx-80,chin+30),(cx-130,chin+50),(cx-110,200),(cx-80,150)], fill=C.SHL)
    d.polygon([(cx+80,chin+30),(cx+130,chin+50),(cx+110,200),(cx+80,150)], fill=C.SHL)

    # ── BELT ──
    d.rectangle([cx-200,590,cx+200,625], fill=C.SD)
    d.rectangle([cx-30,590,cx+30,625], fill=C.BLTG)

    # ── TROUSERS ──
    d.polygon([(cx-200,620),(cx-15,620),(cx-50,feet_y-40),(cx-190,feet_y-40)], fill=C.SD)
    d.polygon([(cx+15,620),(cx+200,620),(cx+190,feet_y-40),(cx+50,feet_y-40)], fill=C.SD)
    d.line([(cx-120,630),(cx-120,feet_y-50)], fill=C.SL, width=3)
    d.line([(cx+120,630),(cx+120,feet_y-50)], fill=C.SL, width=3)

    # ── ARMS ──
    arm_r = [(cx-415,shoulder_y),(cx-470,shoulder_y+120),(cx-480,chest_y+80),
             (cx-460,waist_y+60),(cx-440,waist_y+180)]
    for i in range(len(arm_r)-1):
        x1,y1 = arm_r[i]; x2,y2 = arm_r[i+1]
        w = max(35, 65-i*8)
        d.polygon([(x1-w,y1),(x1+w,y1),(x2+w,y2),(x2-w,y2)], fill=C.SD)
    hx,hy = cx-440,waist_y+190
    d.ellipse([hx-22,hy-8,hx+22,hy+35], fill=C.SKN)
    for fi in range(4):
        d.ellipse([hx-14+fi*9,hy+30,hx-8+fi*9,hy+52], fill=C.SKN)

    arm_l = [(cx+415,shoulder_y),(cx+470,shoulder_y+120),(cx+480,chest_y+80),
             (cx+460,waist_y+60),(cx+440,waist_y+180)]
    for i in range(len(arm_l)-1):
        x1,y1 = arm_l[i]; x2,y2 = arm_l[i+1]
        w = max(35, 65-i*8)
        d.polygon([(x1-w,y1),(x1+w,y1),(x2+w,y2),(x2-w,y2)], fill=C.SD)
    hx2 = cx+440
    d.ellipse([hx2-22,hy-8,hx2+22,hy+35], fill=C.SKN)
    for fi in range(4):
        d.ellipse([hx2-14+fi*9,hy+30,hx2-8+fi*9,hy+52], fill=C.SKN)

    # ── SHOES ──
    d.ellipse([cx-200,feet_y-30,cx-50,feet_y+15], fill=C.SHO)
    d.ellipse([cx+50,feet_y-30,cx+200,feet_y+15], fill=C.SHO)

    return img


# ============================================================
# VECTOR → ASCII (high-res with anti-alias)
# ============================================================
def vector_to_ascii(source, cols, rows, cell_px, blur=1.5):
    blurred = source.filter(ImageFilter.GaussianBlur(radius=blur))
    pixels = blurred.load()
    sw, sh = blurred.size
    out = Image.new("RGB", (cols*cell_px, rows*cell_px), C.BG)
    draw = ImageDraw.Draw(out)
    font = fnt(MONO, cell_px)
    cw, ch = sw/cols, sh/rows
    for gy in range(rows):
        for gx in range(cols):
            sx = min(int(gx*cw+cw/2), sw-1)
            sy = min(int(gy*ch+ch/2), sh-1)
            r,g,b = pixels[sx,sy]
            if r<20 and g<20 and b<25: continue
            draw.text((gx*cell_px, gy*cell_px), BLOCK, fill=(r,g,b), font=font)
    return out


# ============================================================
# SCENES
# ============================================================
SCENES = [
    {"title":"CHƯƠNG 1","ch":"w","cap":"Ngày đó, Linh là cô gái đẹp nhất thành phố.",
     "tts":"Ngày đó, Linh là cô gái đẹp nhất thành phố. Vẻ đẹp không chỉ ở khuôn mặt, mà còn ở trái tim nhân hậu.","bg":"hearts"},
    {"title":"CHƯƠNG 2","ch":"m","cap":"Còn Dũng là tổng tài giàu nhất thành phố.",
     "tts":"Còn Dũng là tổng tài giàu nhất thành phố. Anh có tất cả, trừ một điều: tình yêu thực sự.","bg":"sparkle"},
    {"title":"CHƯƠNG 3","tcolor":C.PG,"ch":"both","cap":"Họ gặp nhau tại bữa tiệc đêm đó...",
     "tts":"Họ gặp nhau tại bữa tiệc đêm đó. Ánh mắt lần đầu chạm nhau, cả thế giới như dừng lại.","bg":"sparkle"},
    {"title":"CHƯƠNG 4","tcolor":C.PG,"ch":"both","cap":"Không tiền bạc, không địa vị. Chỉ có hai trái tim.",
     "tts":"Không tiền bạc, không địa vị. Chỉ có hai trái tim rung động. Tình yêu không cần vật chất.","bg":"hearts"},
    {"title":"CHƯƠNG 5","tcolor":C.GD,"ch":"m","cap":"Dũng quyết định bỏ lại tất cả.",
     "tts":"Dũng quyết định bỏ lại tất cả. Đế chế tiền bạc không bằng nụ cười của cô ấy.","bg":"sparkle"},
    {"title":"CHƯƠNG 6","tcolor":C.DP,"ch":"w","cap":"Linh chờ đợi một tình yêu chân thật.",
     "tts":"Linh chờ đợi một tình yêu chân thật. Không phải vì anh giàu, mà vì anh hiểu trái tim cô.","bg":"hearts"},
    {"title":"CHƯƠNG 7","tcolor":C.PG,"ch":"both","cap":"Hai đường cong gặp nhau tại đỉnh.",
     "tts":"Hai đường cong cuộc đời gặp nhau tại đỉnh. Từ nay, không còn đơn độc.","bg":"hearts"},
    {"title":"PHẦN KẾT","tcolor":C.GD,"ch":"both","cap":"TÌNH YÊU KHÔNG CÓ GIÁ.",
     "tts":"Tình yêu không có giá. Nhưng không có nó, mọi thứ đều có giá. Từ hai, thành một. Không gì là không thể.","bg":"hearts"},
]


# ============================================================
# EFFECTS
# ============================================================
def fx_hearts(d, t, a):
    for i in range(18):
        x = (i*79+int(t*22))%W; y = (i*127+int(t*15))%H
        s = 12+(i%4)*5; v = int(50*a*(0.5+0.5*math.sin(t*2+i)))
        if v>0: d.text((x,y),"♥",fill=C.PG+(v,),font=fnt(MONO,s))

def fx_sparkle(d, t, a):
    for i in range(30):
        x = (i*49+int(t*10))%W; y = (i*89+int(t*7))%H
        p = math.sin(t*3+i*0.7)
        if p>0.3:
            v = int(75*a*p); s = 2+int(5*p)
            d.ellipse([x-s,y-s,x+s,y+s], fill=C.GD+(v,))


# ============================================================
# PRE-RENDER
# ============================================================
CHARS = {}

def prerender():
    print("  Drawing woman 3000x3000 (realistic proportions)...")
    wv = draw_woman()
    wv.save(os.path.join(OUTPUT,"vec_woman.png"))
    print("  Drawing man 3000x3000 (realistic proportions)...")
    mv = draw_man()
    mv.save(os.path.join(OUTPUT,"vec_man.png"))

    # Single: 500 cols x 700 rows, 2px → 1000x1400
    print("  Converting woman → ASCII 500x700 grid, 2px cells...")
    CHARS["w"] = vector_to_ascii(wv, 500, 700, 2, blur=1.2)
    print("  Converting man → ASCII 500x700 grid, 2px cells...")
    CHARS["m"] = vector_to_ascii(mv, 500, 700, 2, blur=1.2)

    # Both: 250x350 grid, 3px → 750x1050
    print("  Converting both → ASCII 250x350 grid, 3px cells...")
    CHARS["ws"] = vector_to_ascii(wv, 250, 350, 3, blur=1.0)
    CHARS["ms"] = vector_to_ascii(mv, 250, 350, 3, blur=1.0)

    for k,v in CHARS.items():
        v.save(os.path.join(OUTPUT, f"ascii_{k}.png"))
        print(f"    {k}: {v.size}")


# ============================================================
# RENDER FRAME
# ============================================================
def render_frame(si, sc, t, st, fn, tf, sd):
    c = Image.new("RGB", (W, H), C.BG)
    d = ImageDraw.Draw(c)

    a = 1.0
    if st<0.6: a=st/0.6
    elif st>sd-0.6: a=(sd-st)/0.6

    if sc.get("bg")=="hearts": fx_hearts(d, t, a*0.5)
    elif sc.get("bg")=="sparkle": fx_sparkle(d, t, a*0.5)

    tc = sc.get("tcolor", C.DM)
    tf2 = fnt(VI_BOLD, 38)
    tb = d.textbbox((0,0), sc["title"], font=tf2)
    d.text(((W-tb[2]+tb[0])//2, 100), sc["title"], font=tf2,
           fill=tuple(int(x*a) for x in tc)+(int(255*a),))

    ct = sc["ch"]
    if ct=="w":
        img = CHARS["w"]
        c.paste(img, ((W-img.width)//2, (H-img.height)//2-80))
    elif ct=="m":
        img = CHARS["m"]
        c.paste(img, ((W-img.width)//2, (H-img.height)//2-80))
    elif ct=="both":
        ws, ms = CHARS["ws"], CHARS["ms"]
        gap = 15
        tw = ws.width+gap+ms.width
        sx = (W-tw)//2
        cy = (H-ws.height)//2-40
        c.paste(ws, (sx, cy))
        c.paste(ms, (sx+ws.width+gap, cy))
        nf = fnt(VI_BOLD, 28)
        for nm,cl,ix in [("Linh",C.DP,sx+ws.width//2),("Dũng",C.GD,sx+ws.width+gap+ms.width//2)]:
            nb = d.textbbox((0,0), nm, font=nf)
            d.text((ix-(nb[2]-nb[0])//2, cy+ws.height+8), nm, font=nf, fill=cl+(int(255*a),))

    cf = fnt(VI_FONT, 34)
    words = sc["cap"].split()
    lines, line = [], ""
    for w in words:
        test = (line+" "+w).strip()
        if d.textbbox((0,0), test, font=cf)[2] > W-120 and line:
            lines.append(line); line = w
        else: line = test
    if line: lines.append(line)
    cy2 = H-340
    for i, ln in enumerate(lines):
        lb = d.textbbox((0,0), ln, font=cf)
        d.text(((W-lb[2]+lb[0])//2, cy2+i*48), ln, font=cf,
               fill=C.WH+(int(255*min(1.0,a*max(0,1-i*0.1))),))

    by=H-100; bx=100; bw=W-200; pr=fn/max(1,tf)
    d.rectangle([bx,by,bx+bw,by+6], fill=(30,30,40))
    d.rectangle([bx,by,bx+int(bw*pr),by+6], fill=C.PG+(180,))
    dy=by+28; ds=36; dsx=W//2-(len(SCENES)*ds)//2
    for si2 in range(len(SCENES)):
        dx=dsx+si2*ds; r=6 if si2==si else 4
        d.ellipse([dx-r,dy-r,dx+r,dy+r], fill=C.PG if si2==si else (50,50,60))

    return c


# ============================================================
# TTS + AUDIO
# ============================================================
async def gen_tts():
    for i,s in enumerate(SCENES):
        p = os.path.join(AUDIO_DIR, f"s{i:02d}.mp3")
        await edge_tts.Communicate(s["tts"],"vi-VN-HoaiMyNeural",rate="+5%").save(p)
        print(f"  TTS {i+1}: {s['tts'][:35]}...")

def concat_audio():
    cl = os.path.join(AUDIO_DIR,"concat.txt")
    with open(cl,"w") as f:
        for i in range(len(SCENES)): f.write(f"file 's{i:02d}.mp3'\n")
    full = os.path.join(OUTPUT,"narration.mp3")
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",cl,"-c","copy",full],capture_output=True)
    r = subprocess.run(["ffprobe","-v","quiet","-show_entries","format=duration",
                         "-of","default=noprint_wrappers=1:nokey=1",full],capture_output=True,text=True)
    return full, float(r.stdout.strip())


# ============================================================
# MAIN
# ============================================================
def main():
    print("="*60)
    print("💕 ASCII LOVE STORY v5: Realistic Portrait Quality")
    print("   3000x3000 realistic anatomy → 500x700 ASCII (350K cells)")
    print("="*60)

    print("\n🎨 Pre-rendering characters...")
    prerender()

    print("\n🎙 Generating TTS...")
    asyncio.run(gen_tts())

    print("\n🎵 Audio...")
    ap, dur = concat_audio()
    sdur = dur/len(SCENES); tf = int(dur*FPS)
    print(f"   {dur:.1f}s, {sdur:.1f}s/scene, {tf} frames")

    print("\n🎨 Rendering frames...")
    fn = 0
    for si,sc in enumerate(SCENES):
        sf = int(sdur*FPS)
        print(f"   Scene {si+1}: {sc['title']} ({sf} frames)")
        for fi in range(sf):
            t=fn/FPS; st=fi/FPS
            img = render_frame(si,sc,t,st,fn,tf,sdur)
            img.save(os.path.join(FRAMES_DIR,f"f_{fn:05d}.png"))
            fn += 1
            if fi%(FPS*3)==0: print(f"      {100*fn//tf}%")

    print("\n🎞 Encoding...")
    out = os.path.join(OUTPUT,"tinh_yeu_v5.mp4")
    subprocess.run(["ffmpeg","-y","-framerate",str(FPS),
        "-i",os.path.join(FRAMES_DIR,"f_%05d.png"),"-i",ap,
        "-c:v","libx264","-pix_fmt","yuv420p","-crf","18","-profile:v","high",
        "-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",out],capture_output=True)

    if os.path.exists(out):
        sz=os.path.getsize(out)/(1024*1024)
        print(f"\n✅ DONE: {out}\n   Size: {sz:.1f}MB, {dur:.1f}s")
    else: print("\n❌ FAILED")

if __name__ == "__main__":
    main()
