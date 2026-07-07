#!/usr/bin/env python3
"""
ASCII Love Story CHIBI — Maximum Cuteness & Detail
Vector 3000x3000 chibi (big head, small body) → 600x500 ASCII grid (300K cells)
Sparkly eyes, rosy cheeks, cute outfits, sparkle effects
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, subprocess, asyncio, edge_tts, math, random

OUTPUT = "/Users/hung/code/ai/shorts/output/ascii_love_chibi"
FRAMES = os.path.join(OUTPUT, "frames")
AUDIO = os.path.join(OUTPUT, "audio")
os.makedirs(FRAMES, exist_ok=True)
os.makedirs(AUDIO, exist_ok=True)

W, H = 1080, 1920
FPS = 24
VI_FONT = "/Library/Fonts/Arial Unicode.ttf"
VI_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
MONO = "/System/Library/Fonts/Menlo.ttc"
BLOCK = '\u2588'

def fnt(p,s):
    try: return ImageFont.truetype(p,s)
    except: return ImageFont.load_default()

# ============================================================
# CUTE CHIBI COLORS
# ============================================================
class C:
    # Skin — warm peachy
    SKN_H  = (255, 230, 210)
    SKN_L  = (248, 218, 195)
    SKN    = (240, 205, 178)
    SKN_M  = (220, 182, 155)
    SKN_D  = (200, 162, 135)
    BLUSH  = (255, 175, 165)  # strong rosy blush
    BLUSH2 = (255, 140, 140)

    # Hair — Linh: black with blue sheen, Dũng: dark brown
    LBK   = (22, 18, 30)
    LBK2  = (35, 28, 45)
    LSHEEN= (60, 50, 85)
    LHL   = (95, 80, 120)

    DBRN  = (35, 25, 20)
    DBRN2 = (52, 38, 28)
    DHSHEEN=(80, 60, 45)
    DHL   = (110, 85, 55)

    # Eyes — BIG sparkly anime
    EW    = (245, 245, 250)
    # Linh eyes — blue
    LIR   = (65, 130, 200)
    LIR2  = (40, 90, 155)
    LIR3  = (100, 165, 230)
    # Dũng eyes — green
    DIR   = (55, 130, 70)
    DIR2  = (30, 90, 45)
    DIR3  = (85, 165, 100)

    EPUP  = (10, 8, 15)
    EHIL1 = (255, 255, 255)  # big sparkle
    EHIL2 = (200, 220, 255)  # secondary
    EHIL3 = (160, 190, 240)  # tertiary

    BROW  = (28, 22, 35)

    # Lips — cute small
    LIP   = (225, 115, 110)
    LIPL  = (240, 140, 135)
    LIPHL = (255, 175, 170)

    # Linh dress — pink
    DP    = (240, 130, 170)
    DL    = (255, 175, 205)
    DD    = (200, 100, 140)
    DHL   = (255, 200, 225)
    DRIB  = (255, 110, 160)  # ribbon

    # Dũng suit — navy
    SD    = (25, 28, 55)
    SL    = (45, 48, 75)
    SHL   = (65, 68, 95)
    SHT   = (235, 235, 240)
    DTIE  = (200, 50, 50)
    DTIEL = (230, 75, 75)

    WH    = (255, 255, 255)

    # Effects
    STAR  = (255, 230, 100)
    STAR2 = (255, 200, 150)
    HEART = (255, 120, 150)
    BG    = (12, 10, 18)
    DM    = (100, 100, 120)


# ============================================================
# HELPERS
# ============================================================
def grad_ell(d, bbox, c1, c2, steps=12):
    x0,y0,x1,y1 = bbox
    cx,cy = (x0+x1)/2,(y0+y1)/2
    rx,ry = (x1-x0)/2,(y1-y0)/2
    for i in range(steps,0,-1):
        t = i/steps
        r = int(c1[0]*(1-t)+c2[0]*t)
        g = int(c1[1]*(1-t)+c2[1]*t)
        b = int(c1[2]*(1-t)+c2[2]*t)
        d.ellipse([cx-rx*t,cy-ry*t,cx+rx*t,cy+ry*t], fill=(r,g,b))

def spark_eye(d, cx, cy, iris_c1, iris_c2, iris_hl, r=80):
    """Draw a big sparkly chibi eye."""
    # White
    d.ellipse([cx-r,cy-int(r*0.6),cx+r,cy+int(r*0.65)], fill=C.EW)
    # Iris — large, gradient
    ir = int(r*0.7)
    grad_ell(d, [cx-ir,cy-int(ir*0.3),cx+ir,cy+int(ir*0.7)], iris_c1, iris_c2, steps=8)
    # Inner iris highlight ring
    d.ellipse([cx-int(ir*0.5),cy-int(ir*0.1),cx+int(ir*0.5),cy+int(ir*0.5)], fill=iris_hl)
    # Pupil — big
    pr = int(r*0.25)
    d.ellipse([cx-pr,cy-pr//2,cx+pr,cy+pr], fill=C.EPUP)
    # MAIN sparkle — large white circle
    sr = int(r*0.22)
    d.ellipse([cx-int(r*0.3),cy-int(r*0.35),cx-int(r*0.3)+sr*2,cy-int(r*0.35)+sr*2], fill=C.EHIL1)
    # Secondary sparkle
    sr2 = int(r*0.12)
    d.ellipse([cx+int(r*0.15),cy+int(r*0.05),cx+int(r*0.15)+sr2*2,cy+int(r*0.05)+sr2*2], fill=C.EHIL2)
    # Third sparkle — small
    sr3 = int(r*0.07)
    d.ellipse([cx-int(r*0.05),cy+int(r*0.3),cx-int(r*0.05)+sr3*2,cy+int(r*0.3)+sr3*2], fill=C.EHIL3)
    # Upper eyelid — thick lashes
    d.arc([cx-r-5,cy-int(r*0.7),cx+r+5,cy+int(r*0.35)], 195, 345, fill=C.BROW, width=7)
    # Lashes — 3 per side
    for angle in [200,212,224]:
        rad = math.radians(angle)
        lx1 = cx + int((r-5)*math.cos(rad))
        ly1 = cy + int(r*0.5*math.sin(rad))
        lx2 = cx + int((r+18)*math.cos(rad))
        ly2 = cy + int(r*0.5*math.sin(rad)) - 12
        d.line([(lx1,ly1),(lx2,ly2)], fill=C.BROW, width=3)
    for angle in [320,332,344]:
        rad = math.radians(angle)
        lx1 = cx + int((r-5)*math.cos(rad))
        ly1 = cy + int(r*0.5*math.sin(rad))
        lx2 = cx + int((r+15)*math.cos(rad))
        ly2 = cy + int(r*0.5*math.sin(rad)) - 10
        d.line([(lx1,ly1),(lx2,ly2)], fill=C.BROW, width=3)
    # Lower eyelid — subtle
    d.arc([cx-int(r*0.8),cy-int(r*0.15),cx+int(r*0.8),cy+int(r*0.55)], 10, 170, fill=C.SKN_D, width=2)


# ============================================================
# CHIBI LINH — Big head, sparkly blue eyes, cute pink dress
# ============================================================
def draw_chibi_linh():
    sz = 3000
    img = Image.new("RGB", (sz, sz), C.BG)
    d = ImageDraw.Draw(img)
    cx = sz // 2

    # Chibi proportions: head ~50% of visible height
    head_cy = 620
    head_rx, head_ry = 400, 380  # balanced with body width
    body_top = 1050
    body_bot = 2350
    feet_y = 2550
    # Head height: 760px, Body: 1500px → ratio 1:1.97

    # ── HAIR BEHIND — long wavy ──
    d.ellipse([cx-430, head_cy-370, cx+430, head_cy+370], fill=C.LBK)
    # Long flowing sides
    for wx in [-360, -280, 280, 360]:
        for wy in range(950, 2200, 60):
            wave = int(35*math.sin(wy/120 + wx/200))
            d.ellipse([cx+wx+wave-40, wy-25, cx+wx+wave+40, wy+25], fill=C.LBK)
    # Hair sheen
    for hx in [-350, -200, 200, 350]:
        for hy in range(600, 2000, 80):
            wave = int(25*math.sin(hy/100 + hx/150))
            d.ellipse([cx+hx+wave-20, hy-8, cx+hx+wave+20, hy+8], fill=C.LSHEEN)
    # Highlight streaks
    for hx in [-280, 280]:
        for hy in range(500, 1800, 100):
            d.ellipse([cx+hx-10, hy-5, cx+hx+10, hy+5], fill=C.LHL)

    # ── BODY — small chibi body ──
    # Neck
    d.polygon([(cx-80,body_top-20),(cx+80,body_top-20),(cx+70,body_top+80),(cx-70,body_top+80)], fill=C.SKN)

    # ── PINK DRESS — cute A-line ──
    # Bodice
    d.polygon([(cx-200,body_top),(cx+200,body_top),(cx+180,body_top+200),(cx-180,body_top+200)], fill=C.DP)
    d.ellipse([cx-180,body_top+20,cx-40,body_top+120], fill=C.DL)
    d.ellipse([cx+40,body_top+20,cx+180,body_top+120], fill=C.DL)
    # Ribbon/bow at center
    d.polygon([(cx-35,body_top+60),(cx,body_top+40),(cx+35,body_top+60),(cx,body_top+90)], fill=C.DRIB)
    d.ellipse([cx-10,body_top+55,cx+10,body_top+75], fill=C.DRIB)
    # Skirt — wide A-line
    d.polygon([(cx-180,body_top+190),(cx+180,body_top+190),(cx+400,body_bot),(cx-400,body_bot)], fill=C.DP)
    # Skirt folds
    for fx in [-300,-150,0,150,300]:
        d.polygon([(cx+fx-25,body_top+250),(cx+fx+25,body_top+250),
                   (cx+fx+15,body_bot-40),(cx+fx-35,body_bot-40)], fill=C.DD)
    # Skirt highlight
    d.polygon([(cx-50,body_top+210),(cx+50,body_top+210),(cx+70,body_bot-30),(cx-70,body_bot-30)], fill=C.DHL)

    # ── FACE — round chibi ──
    d.ellipse([cx-head_rx, head_cy-head_ry, cx+head_rx, head_cy+head_ry], fill=C.SKN_L)
    # Chin area — slightly pointed for cute V
    d.ellipse([cx-240, head_cy+60, cx+240, head_cy+head_ry+30], fill=C.SKN)

    # ── HAIR BANGS — cute side-swept ──
    d.polygon([(cx-410,head_cy-350),(cx-300,head_cy-390),(cx-80,head_cy-330),
               (cx+80,head_cy-370),(cx+270,head_cy-340),(cx+390,head_cy-360),
               (cx+410,head_cy-300),(cx+400,head_cy-120),(cx+240,head_cy-170),
               (cx,head_cy-150),(cx-240,head_cy-180),(cx-390,head_cy-120)], fill=C.LBK)
    # Side hair framing face
    d.polygon([(cx-410,head_cy-300),(cx-440,head_cy-200),(cx-450,head_cy+200),
               (cx-410,head_cy+100),(cx-400,head_cy-120)], fill=C.LBK)
    d.polygon([(cx+410,head_cy-300),(cx+440,head_cy-200),(cx+450,head_cy+200),
               (cx+410,head_cy+100),(cx+400,head_cy-120)], fill=C.LBK)
    # Bangs sheen
    d.arc([cx-240,head_cy-400,cx+80,head_cy-200], 210, 340, fill=C.LSHEEN, width=5)
    d.arc([cx+40,head_cy-390,cx+320,head_cy-200], 210, 340, fill=C.LHL, width=4)

    # ── EARS — cute round ──
    for ex in [cx-390, cx+390]:
        d.ellipse([ex-28,head_cy-40,ex+28,head_cy+50], fill=C.SKN)
        d.ellipse([ex-14,head_cy-20,ex+14,head_cy+30], fill=C.SKN_M)
        # Earring — small sparkle
        d.ellipse([ex-7,head_cy+45,ex+7,head_cy+62], fill=C.STAR)
        d.ellipse([ex-3,head_cy+48,ex+3,head_cy+59], fill=(255,255,255))

    # ── EYES — BIG sparkly blue ──
    eye_cy = head_cy + 15
    eye_sep = 150
    spark_eye(d, cx-eye_sep, eye_cy, C.LIR, C.LIR2, C.LIR3, r=70)
    spark_eye(d, cx+eye_sep, eye_cy, C.LIR, C.LIR2, C.LIR3, r=70)

    # ── EYEBROWS — thin cute arch ──
    for bx in [cx-eye_sep, cx+eye_sep]:
        d.arc([bx-55,eye_cy-85,bx+55,eye_cy-45], 200, 340, fill=C.BROW, width=4)

    # ── NOSE — tiny dot ──
    d.ellipse([cx-8,head_cy+110,cx+8,head_cy+125], fill=C.SKN_M)

    # ── MOUTH — cute smile ──
    mouth_y = head_cy + 160
    d.arc([cx-40,mouth_y-15,cx+40,mouth_y+15], 10, 170, fill=C.LIP, width=5)
    d.ellipse([cx-8,mouth_y+2,cx+8,mouth_y+12], fill=C.LIPL)
    d.ellipse([cx-3,mouth_y+4,cx+3,mouth_y+9], fill=C.LIPHL)

    # ── BLUSH — big rosy circles ──
    d.ellipse([cx-eye_sep-40,eye_cy+55,cx-eye_sep+50,eye_cy+120], fill=C.BLUSH)
    d.ellipse([cx+eye_sep-50,eye_cy+55,cx+eye_sep+40,eye_cy+120], fill=C.BLUSH)

    # ── ARMS — small cute stubs ──
    for side in [-1, 1]:
        ax = cx + side * 210
        # Upper arm
        d.ellipse([ax-40,body_top+20,ax+40,body_top+100], fill=C.SKN)
        # Lower arm
        d.ellipse([ax-35,body_top+80,ax+35,body_top+170], fill=C.SKN)
        # Hand — round
        d.ellipse([ax-30,body_top+150,ax+30,body_top+210], fill=C.SKN)
        # Fingers — tiny
        for fi in range(3):
            fx = ax - 12 + fi * 12
            d.ellipse([fx-5,body_top+200,fx+5,body_top+225], fill=C.SKN)

    # ── LEGS — short chibi ──
    for side in [-1,1]:
        lx = cx + side * 100
        # Leg
        d.polygon([(lx-50,body_bot),(lx+50,body_bot),(lx+40,feet_y),(lx-40,feet_y)], fill=C.SKN)
        # Shoe — cute round
        d.ellipse([lx-55,feet_y-15,lx+55,feet_y+25], fill=C.DP)
        d.ellipse([lx-40,feet_y-8,lx+40,feet_y+10], fill=C.DL)
        # Shoe ribbon
        d.ellipse([lx-8,feet_y-15,lx+8,feet_y-2], fill=C.DRIB)

    # ── SPARKLES around character ──
    random.seed(42)
    for _ in range(25):
        sx = cx + random.randint(-600, 600)
        sy = random.randint(200, 2600)
        ss = random.randint(8, 25)
        # 4-point star
        d.polygon([(sx,sy-ss),(sx+ss//4,sy),(sx,sy+ss),(sx-ss//4,sy)], fill=C.STAR)
        d.polygon([(sx-ss,sy),(sx,sy-ss//4),(sx+ss,sy),(sx,sy+ss//4)], fill=C.STAR)

    return img


# ============================================================
# CHIBI DŨNG — Big head, green eyes, cute suit
# ============================================================
def draw_chibi_dung():
    sz = 3000
    img = Image.new("RGB", (sz, sz), C.BG)
    d = ImageDraw.Draw(img)
    cx = sz // 2

    head_cy = 620
    head_rx, head_ry = 390, 370
    body_top = 1050
    body_bot = 2350
    feet_y = 2550

    # ── HAIR BEHIND — short neat ──
    d.ellipse([cx-410, head_cy-360, cx+410, head_cy+350], fill=C.DBRN)
    # Side hair
    for hx in [-320, -250, 250, 320]:
        for hy in range(880, 1350, 50):
            d.ellipse([cx+hx-30, hy-18, cx+hx+30, hy+18], fill=C.DBRN2)

    # ── BODY ──
    d.polygon([(cx-80,body_top-20),(cx+80,body_top-20),(cx+70,body_top+80),(cx-70,body_top+80)], fill=C.SKN)

    # ── NAVY SUIT ──
    # Jacket
    d.polygon([(cx-220,body_top),(cx+220,body_top),(cx+200,body_top+250),(cx-200,body_top+250)], fill=C.SD)
    # Shirt collar — V shape white
    d.polygon([(cx-80,body_top),(cx,80),(cx+80,body_top),(cx+60,body_top+60),(cx,body_top+80),(cx-60,body_top+60)], fill=C.SHT)
    # Lapels
    d.polygon([(cx-80,body_top+10),(cx-140,body_top+30),(cx-120,body_top+120),(cx-80,body_top+80)], fill=C.SHL)
    d.polygon([(cx+80,body_top+10),(cx+140,body_top+30),(cx+120,body_top+120),(cx+80,body_top+80)], fill=C.SHL)
    # Tie
    d.polygon([(cx-18,body_top+30),(cx+18,body_top+30),(cx+12,body_top+220),(cx-12,body_top+220)], fill=C.DTIE)
    d.polygon([(cx-18,body_top+30),(cx+18,body_top+30),(cx+10,body_top+60),(cx-10,body_top+60)], fill=C.DTIEL)
    d.polygon([(cx-14,body_top+15),(cx+14,body_top+15),(cx+10,body_top+35),(cx-10,body_top+35)], fill=C.DTIEL)

    # Pants
    d.polygon([(cx-200,body_top+240),(cx-20,body_top+240),(cx-50,body_bot),(cx-180,body_bot)], fill=C.SD)
    d.polygon([(cx+20,body_top+240),(cx+200,body_top+240),(cx+180,body_bot),(cx+50,body_bot)], fill=C.SD)
    d.line([(cx-130,body_top+250),(cx-130,body_bot-20)], fill=C.SL, width=3)
    d.line([(cx+130,body_top+250),(cx+130,body_bot-20)], fill=C.SL, width=3)

    # ── FACE ──
    d.ellipse([cx-head_rx,head_cy-head_ry,cx+head_rx,head_cy+head_ry], fill=C.SKN_L)
    d.ellipse([cx-230,head_cy+60,cx+230,head_cy+head_ry+30], fill=C.SKN)

    # ── HAIR BANGS — neat, spiky cute ──
    d.polygon([(cx-400,head_cy-340),(cx-300,head_cy-380),(cx-80,head_cy-320),
               (cx+40,head_cy-370),(cx+180,head_cy-310),(cx+300,head_cy-360),
               (cx+390,head_cy-330),(cx+380,head_cy-120),(cx+240,head_cy-170),
               (cx,head_cy-140),(cx-240,head_cy-170),(cx-380,head_cy-120)], fill=C.DBRN)
    # Side hair
    d.polygon([(cx-400,head_cy-300),(cx-430,head_cy-200),(cx-435,head_cy+100),
               (cx-400,head_cy+20),(cx-390,head_cy-120)], fill=C.DBRN)
    d.polygon([(cx+400,head_cy-300),(cx+430,head_cy-200),(cx+435,head_cy+100),
               (cx+400,head_cy+20),(cx+390,head_cy-120)], fill=C.DBRN)
    # Hair sheen
    d.arc([cx-200,head_cy-400,cx+120,head_cy-200], 210, 340, fill=C.DHSHEEN, width=5)
    d.arc([cx+80,head_cy-390,cx+320,head_cy-200], 210, 340, fill=C.DHL, width=4)

    # ── EARS ──
    for ex in [cx-380, cx+380]:
        d.ellipse([ex-25,head_cy-35,ex+25,head_cy+45], fill=C.SKN)
        d.ellipse([ex-12,head_cy-18,ex+12,head_cy+25], fill=C.SKN_M)

    # ── EYES — BIG sparkly green ──
    eye_cy = head_cy + 15
    eye_sep = 145
    spark_eye(d, cx-eye_sep, eye_cy, C.DIR, C.DIR2, C.DIR3, r=65)
    spark_eye(d, cx+eye_sep, eye_cy, C.DIR, C.DIR2, C.DIR3, r=65)

    # ── EYEBROWS — slightly thicker ──
    for bx in [cx-eye_sep, cx+eye_sep]:
        d.arc([bx-42,eye_cy-68,bx+42,eye_cy-32], 200, 340, fill=C.BROW, width=5)

    # ── NOSE ──
    d.ellipse([cx-6,head_cy+90,cx+6,head_cy+102], fill=C.SKN_M)

    # ── MOUTH — confident smile ──
    mouth_y = head_cy + 130
    d.arc([cx-35,mouth_y-10,cx+35,mouth_y+15], 10, 170, fill=C.LIP, width=5)
    d.ellipse([cx-5,mouth_y+3,cx+5,mouth_y+11], fill=C.LIPL)

    # ── BLUSH ──
    d.ellipse([cx-eye_sep-38,eye_cy+50,cx-eye_sep+48,eye_cy+110], fill=C.BLUSH)
    d.ellipse([cx+eye_sep-48,eye_cy+50,cx+eye_sep+38,eye_cy+110], fill=C.BLUSH)

    # ── ARMS ──
    for side in [-1,1]:
        ax = cx + side * 220
        d.ellipse([ax-45,body_top+10,ax+45,body_top+100], fill=C.SD)
        d.ellipse([ax-40,body_top+80,ax+40,body_top+170], fill=C.SD)
        d.ellipse([ax-28,body_top+155,ax+28,body_top+210], fill=C.SKN)
        for fi in range(3):
            fx = ax - 10 + fi * 10
            d.ellipse([fx-4,body_top+200,fx+4,body_top+222], fill=C.SKN)

    # ── LEGS ──
    for side in [-1,1]:
        lx = cx + side * 100
        d.polygon([(lx-48,body_bot),(lx+48,body_bot),(lx+38,feet_y),(lx-38,feet_y)], fill=C.SD)
        d.ellipse([lx-52,feet_y-12,lx+52,feet_y+22], fill=(25,22,35))
        d.ellipse([lx-38,feet_y-5,lx+38,feet_y+10], fill=(40,35,50))

    # ── SPARKLES ──
    random.seed(43)
    for _ in range(20):
        sx = cx + random.randint(-600, 600)
        sy = random.randint(200, 2600)
        ss = random.randint(8, 22)
        d.polygon([(sx,sy-ss),(sx+ss//4,sy),(sx,sy+ss),(sx-ss//4,sy)], fill=C.STAR)
        d.polygon([(sx-ss,sy),(sx,sy-ss//4),(sx+ss,sy),(sx,sy+ss//4)], fill=C.STAR)

    return img


# ============================================================
# ASCII CONVERSION — high density
# ============================================================
def to_ascii(source, cols, rows, cell_px, blur=1.0):
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
            if r<15 and g<15 and b<20: continue
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
    {"title":"CHƯƠNG 3","tcolor":C.HEART,"ch":"both","cap":"Họ gặp nhau tại bữa tiệc đêm đó...",
     "tts":"Họ gặp nhau tại bữa tiệc đêm đó. Ánh mắt lần đầu chạm nhau, cả thế giới như dừng lại.","bg":"sparkle"},
    {"title":"CHƯƠNG 4","tcolor":C.HEART,"ch":"both","cap":"Không tiền bạc, không địa vị. Chỉ có hai trái tim.",
     "tts":"Không tiền bạc, không địa vị. Chỉ có hai trái tim rung động. Tình yêu không cần vật chất.","bg":"hearts"},
    {"title":"CHƯƠNG 5","tcolor":C.STAR,"ch":"m","cap":"Dũng quyết định bỏ lại tất cả.",
     "tts":"Dũng quyết định bỏ lại tất cả. Đế chế tiền bạc không bằng nụ cười của cô ấy.","bg":"sparkle"},
    {"title":"CHƯƠNG 6","tcolor":C.DRIB,"ch":"w","cap":"Linh chờ đợi một tình yêu chân thật.",
     "tts":"Linh chờ đợi một tình yêu chân thật. Không phải vì anh giàu, mà vì anh hiểu trái tim cô.","bg":"hearts"},
    {"title":"CHƯƠNG 7","tcolor":C.HEART,"ch":"both","cap":"Hai đường cong gặp nhau tại đỉnh.",
     "tts":"Hai đường cong cuộc đời gặp nhau tại đỉnh. Từ nay, không còn đơn độc.","bg":"hearts"},
    {"title":"PHẦN KẾT","tcolor":C.STAR,"ch":"both","cap":"TÌNH YÊU KHÔNG CÓ GIÁ.",
     "tts":"Tình yêu không có giá. Nhưng không có nó, mọi thứ đều có giá. Từ hai, thành một. Không gì là không thể.","bg":"hearts"},
]


# ============================================================
# EFFECTS — cute sparkles + hearts
# ============================================================
def fx_hearts(d, t, a):
    for i in range(20):
        x = (i*67+int(t*18))%W
        y = (i*113+int(t*12))%H
        s = 14+(i%4)*6
        v = int(60*a*(0.5+0.5*math.sin(t*2.5+i)))
        if v > 0:
            # Heart shape with two circles + triangle
            hs = s//2
            d.ellipse([x-hs,y-hs,x,y], fill=C.HEART+(v,))
            d.ellipse([x,y-hs,x+hs,y], fill=C.HEART+(v,))
            d.polygon([(x-hs,y),(x+hs,y),(x,y+hs)], fill=C.HEART+(v,))

def fx_sparkle(d, t, a):
    for i in range(35):
        x = (i*43+int(t*12))%W
        y = (i*83+int(t*8))%H
        p = math.sin(t*3.5+i*0.8)
        if p > 0.2:
            v = int(80*a*p)
            s = 3+int(7*p)
            # 4-point star
            d.polygon([(x,y-s),(x+s//3,y),(x,y+s),(x-s//3,y)], fill=C.STAR+(v,))
            d.polygon([(x-s,y),(x,y-s//3),(x+s,y),(x,y+s//3)], fill=C.STAR+(v,))


# ============================================================
# PRE-RENDER
# ============================================================
CHARS = {}

def prerender():
    print("  Drawing chibi Linh 3000x3000...")
    wv = draw_chibi_linh()
    wv.save(os.path.join(OUTPUT, "vec_linh.png"))
    print("  Drawing chibi Dũng 3000x3000...")
    mv = draw_chibi_dung()
    mv.save(os.path.join(OUTPUT, "vec_dung.png"))

    # Single: 600 cols × 500 rows, 2px cells → 1200x1000
    print("  Converting Linh → ASCII (600x500, 2px)...")
    CHARS["w"] = to_ascii(wv, 600, 500, 2, blur=1.0)
    print("  Converting Dũng → ASCII (600x500, 2px)...")
    CHARS["m"] = to_ascii(mv, 600, 500, 2, blur=1.0)

    # Both: 350 cols × 290 rows, 2.5px → 875x725
    print("  Converting both → ASCII (350x290, 2.5px)...")
    CHARS["ws"] = to_ascii(wv, 350, 290, 3, blur=0.8)
    CHARS["ms"] = to_ascii(mv, 350, 290, 3, blur=0.8)

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
    if st < 0.5: a = st/0.5
    elif st > sd-0.5: a = (sd-st)/0.5

    if sc.get("bg") == "hearts": fx_hearts(d, t, a*0.6)
    elif sc.get("bg") == "sparkle": fx_sparkle(d, t, a*0.6)

    tc = sc.get("tcolor", C.DM)
    tf2 = fnt(VI_BOLD, 40)
    tb = d.textbbox((0,0), sc["title"], font=tf2)
    d.text(((W-tb[2]+tb[0])//2, 100), sc["title"], font=tf2,
           fill=tuple(int(x*a) for x in tc)+(int(255*a),))

    ct = sc["ch"]
    if ct == "w":
        img = CHARS["w"]
        x = (W-img.width)//2
        y = (H-img.height)//2 - 50
        c.paste(img, (x, y))
    elif ct == "m":
        img = CHARS["m"]
        x = (W-img.width)//2
        y = (H-img.height)//2 - 50
        c.paste(img, (x, y))
    elif ct == "both":
        ws, ms = CHARS["ws"], CHARS["ms"]
        gap = 20
        tw = ws.width + gap + ms.width
        sx = (W-tw)//2
        cy = (H - max(ws.height, ms.height))//2 - 30
        c.paste(ws, (sx, cy))
        c.paste(ms, (sx+ws.width+gap, cy))
        nf = fnt(VI_BOLD, 30)
        for nm, cl, ix in [("Linh",C.DRIB, sx+ws.width//2),
                            ("Dũng",C.DTIE, sx+ws.width+gap+ms.width//2)]:
            nb = d.textbbox((0,0), nm, font=nf)
            d.text((ix-(nb[2]-nb[0])//2, cy+max(ws.height,ms.height)+10), nm, font=nf,
                   fill=cl+(int(255*a),))

    cf = fnt(VI_FONT, 36)
    words = sc["cap"].split()
    lines, line = [], ""
    for w in words:
        test = (line+" "+w).strip()
        if d.textbbox((0,0), test, font=cf)[2] > W-120 and line:
            lines.append(line); line = w
        else: line = test
    if line: lines.append(line)
    cy2 = H-320
    for i, ln in enumerate(lines):
        lb = d.textbbox((0,0), ln, font=cf)
        d.text(((W-lb[2]+lb[0])//2, cy2+i*50), ln, font=cf,
               fill=C.WH+(int(255*min(1.0,a*max(0,1-i*0.1))),))

    by=H-100; bx=100; bw=W-200; pr=fn/max(1,tf)
    d.rectangle([bx,by,bx+bw,by+6], fill=(30,30,40))
    d.rectangle([bx,by,bx+int(bw*pr),by+6], fill=C.DRIB+(180,))
    dy=by+28; ds=36; dsx=W//2-(len(SCENES)*ds)//2
    for si2 in range(len(SCENES)):
        dx=dsx+si2*ds; r=6 if si2==si else 4
        d.ellipse([dx-r,dy-r,dx+r,dy+r], fill=C.DRIB if si2==si else (50,50,60))

    return c


# ============================================================
# TTS
# ============================================================
async def gen_tts():
    for i,s in enumerate(SCENES):
        p = os.path.join(AUDIO, f"s{i:02d}.mp3")
        await edge_tts.Communicate(s["tts"],"vi-VN-HoaiMyNeural",rate="+5%").save(p)
        print(f"  TTS {i+1}: {s['tts'][:35]}...")

def concat_audio():
    cl = os.path.join(AUDIO,"concat.txt")
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
    print("💕 ASCII LOVE STORY CHIBI — Maximum Cuteness")
    print("   3000x3000 chibi → 600x500 ASCII (300K cells)")
    print("="*60)

    print("\n🎨 Pre-rendering chibi characters...")
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
            img.save(os.path.join(FRAMES,f"f_{fn:05d}.png"))
            fn += 1
            if fi%(FPS*3)==0: print(f"      {100*fn//tf}%")

    print("\n🎞 Encoding...")
    out = os.path.join(OUTPUT,"tinh_yeu_chibi.mp4")
    subprocess.run(["ffmpeg","-y","-framerate",str(FPS),
        "-i",os.path.join(FRAMES,"f_%05d.png"),"-i",ap,
        "-c:v","libx264","-pix_fmt","yuv420p","-crf","18","-profile:v","high",
        "-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",out],capture_output=True)

    if os.path.exists(out):
        sz=os.path.getsize(out)/(1024*1024)
        print(f"\n✅ DONE: {out}\n   Size: {sz:.1f}MB, {dur:.1f}s")
    else: print("\n❌ FAILED")

if __name__ == "__main__":
    main()
