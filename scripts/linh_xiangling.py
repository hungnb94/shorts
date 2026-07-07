#!/usr/bin/env python3
"""
Linh Chibi — Xiangling-inspired detailed ASCII art
Based on exact proportions from reference analysis
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, math, random

OUTPUT = "/Users/hung/code/ai/shorts/output/linh_chibi"
os.makedirs(OUTPUT, exist_ok=True)

BLOCK = '\u2588'
MONO  = "/System/Library/Fonts/Menlo.ttc"

def fnt(p, s):
    try: return ImageFont.truetype(p, s)
    except: return ImageFont.load_default()


# ============================================================
# PRECISE COLORS (Xiangling-inspired palette)
# ============================================================
class K:
    # Skin
    SKN_H  = (255, 232, 215)
    SKN    = (245, 215, 190)
    SKN_M  = (225, 188, 160)
    SKN_D  = (200, 165, 138)
    BLUSH  = (255, 175, 175)
    BLUSH2 = (255, 145, 155)

    # Hair — warm chestnut brown
    HAIR   = (125, 72, 45)
    HAIR2  = (155, 95, 58)
    HAIR3  = (95, 52, 30)
    HAIRSH = (180, 125, 82)  # sheen highlight
    HAIRHL = (200, 155, 110) # bright highlight

    # Eyes — amber/golden-brown
    EYE_W  = (248, 248, 252)
    IRIS1  = (180, 115, 35)  # outer amber
    IRIS2  = (155, 92, 22)   # inner dark amber
    IRIS3  = (210, 155, 60)  # bright amber ring
    IRISHL = (255, 230, 160) # sparkle
    IRISHL2= (240, 210, 140)
    PUPIL  = (18, 12, 8)
    BROW   = (55, 35, 22)

    # Clothing
    NAVY   = (30, 35, 65)    # dark navy blue
    NAVYL  = (50, 55, 88)    # lighter navy
    NAVYHL = (70, 75, 108)   # highlight
    CREAM  = (245, 235, 215) # cream shirt
    CREAMD = (225, 212, 188)
    BOW    = (55, 120, 200)  # bright blue bow
    BOWHL  = (85, 150, 225)
    TAN    = (175, 142, 98)  # tan trim
    TAND   = (148, 118, 78)
    GOLD   = (220, 185, 65)  # gold buttons/emblem
    GOLDHL = (245, 215, 100)
    GOGD   = (45, 42, 38)    # goggle dark frame
    GOGL   = (72, 65, 58)    # goggle lens
    GOGHL  = (100, 92, 82)   # goggle strap

    # Skirt, socks, shoes
    SKIRT  = (28, 32, 60)
    SKIRTL = (45, 48, 78)
    SOCK   = (248, 245, 242)
    SOCKD  = (228, 222, 218)
    SHOE   = (25, 28, 42)
    SHOEL  = (42, 45, 58)

    # Hair clips — colorful
    CLIP_P = (180, 80, 180)  # purple-pink
    CLIP_B = (60, 120, 200)  # blue
    CLIP_Y = (220, 185, 50)  # yellow
    CLIP_G = (80, 170, 70)   # green
    CLIP_O = (220, 130, 45)  # orange

    # Stars
    STAR   = (255, 225, 90)
    BG     = (12, 10, 18)


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
    """Large round amber eye with sparkles."""
    # White
    d.ellipse([cx-r,cy-int(r*0.6),cx+r,cy+int(r*0.65)], fill=K.EYE_W)
    # Iris — large round
    ir = int(r*0.72)
    grad_ell(d, [cx-ir,cy-int(ir*0.3),cx+ir,cy+int(ir*0.7)], iris_c1, iris_c2, steps=8)
    # Inner bright ring
    d.ellipse([cx-int(ir*0.55),cy-int(ir*0.1),cx+int(ir*0.55),cy+int(ir*0.5)], fill=iris_hl)
    # Pupil — large
    pr = int(r*0.22)
    d.ellipse([cx-pr,cy-pr//2,cx+pr,cy+pr], fill=K.PUPIL)
    # MAIN sparkle — big white
    sr = int(r*0.25)
    d.ellipse([cx-int(r*0.32),cy-int(r*0.38),cx-int(r*0.32)+sr*2,cy-int(r*0.38)+sr*2], fill=(255,255,255))
    # Secondary sparkle
    sr2 = int(r*0.13)
    d.ellipse([cx+int(r*0.18),cy+int(r*0.05),cx+int(r*0.18)+sr2*2,cy+int(r*0.05)+sr2*2], fill=(240,230,210))
    # Third — tiny
    sr3 = int(r*0.07)
    d.ellipse([cx-int(r*0.05),cy+int(r*0.32),cx-int(r*0.05)+sr3*2,cy+int(r*0.32)+sr3*2], fill=(220,200,160))
    # Upper eyelid — thick lashes
    d.arc([cx-r-5,cy-int(r*0.7),cx+r+5,cy+int(r*0.35)], 195, 345, fill=K.BROW, width=8)
    # Lashes — 3 per side
    for angle in [200,212,224]:
        rad = math.radians(angle)
        lx1 = cx + int((r-5)*math.cos(rad))
        ly1 = cy + int(r*0.5*math.sin(rad))
        lx2 = cx + int((r+20)*math.cos(rad))
        ly2 = cy + int(r*0.5*math.sin(rad)) - 15
        d.line([(lx1,ly1),(lx2,ly2)], fill=K.BROW, width=3)
    for angle in [320,332,344]:
        rad = math.radians(angle)
        lx1 = cx + int((r-5)*math.cos(rad))
        ly1 = cy + int(r*0.5*math.sin(rad))
        lx2 = cx + int((r+18)*math.cos(rad))
        ly2 = cy + int(r*0.5*math.sin(rad)) - 12
        d.line([(lx1,ly1),(lx2,ly2)], fill=K.BROW, width=3)
    # Lower eyelid
    d.arc([cx-int(r*0.8),cy-int(r*0.15),cx+int(r*0.8),cy+int(r*0.55)], 10, 170, fill=K.SKN_D, width=2)


def flower_clip(d, cx, cy, size, colors):
    """Draw a small flower hair clip."""
    for i, color in enumerate(colors):
        angle = math.radians(i * 72 - 90)
        px = cx + int(size * 0.6 * math.cos(angle))
        py = cy + int(size * 0.6 * math.sin(angle))
        d.ellipse([px-size//2, py-size//2, px+size//2, py+size//2], fill=color)
    # Center
    d.ellipse([cx-size//4,cy-size//4,cx+size//4,cy+size//4], fill=(255,235,120))


# ============================================================
# DRAW XIANGLING-STYLE LINH
# ============================================================
def draw_xiangling():
    """Draw Linh in Xiangling chibi style with exact proportions."""
    sz = 3000
    W = sz
    img = Image.new("RGB", (sz, sz), K.BG)
    d = ImageDraw.Draw(img)
    cx = sz // 2

    # ── PROPORTIONS (from analysis) ──
    # Head center: 27% from top
    head_cy = int(sz * 0.27)  # 810
    # Head width: 65% of total → rx = 32.5%
    head_rx = int(sz * 0.325)  # 975
    head_ry = int(sz * 0.16)   # 480 (slightly wider than tall for round chibi)
    # Head top: 10% from top
    head_top = int(sz * 0.10)  # 300
    # Chin: 42% from top
    chin_y = int(sz * 0.42)   # 1260
    # Body starts at chin
    body_top = chin_y
    # Body width: 55% of head width
    body_rx = int(head_rx * 0.55)  # 536
    # Coat hem: 72% from top
    coat_hem_y = int(sz * 0.72)  # 2160
    # Skirt bottom: 85% from top
    skirt_bot_y = int(sz * 0.85)  # 2550
    # Feet bottom: 98% from top
    feet_y = int(sz * 0.98)    # 2940
    # Eye positions: 33% from top, 8% from center horizontal
    eye_y = int(sz * 0.33)     # 990
    eye_offset = int(sz * 0.08) # 240
    # Eye size: 18% of head width = ~350
    eye_r = int(head_rx * 0.18) # 175
    # Mouth: 39% from top
    mouth_y = int(sz * 0.39)   # 1170

    # ── HAIR BEHIND (long fluffy chestnut) ──
    # Main hair volume behind head
    d.ellipse([cx-head_rx-50, head_top-20, cx+head_rx+50, chin_y+200], fill=K.HAIR)
    # Side hair — fluffy, extends past shoulders
    for wx in [-850, -750, 750, 850]:
        for wy in range(chin_y-100, skirt_bot_y-200, 50):
            wave = int(30*math.sin(wy/100 + wx/200))
            d.ellipse([cx+wx+wave-45, wy-22, cx+wx+wave+45, wy+22], fill=K.HAIR)
    # Hair sheen
    for hx in [-700, -500, 500, 700]:
        for hy in range(head_top+50, coat_hem_y, 80):
            wave = int(20*math.sin(hy/90 + hx/150))
            d.ellipse([cx+hx+wave-15, hy-6, cx+hx+wave+15, hy+6], fill=K.HAIRSH)
    # Highlight streaks
    for hx in [-600, -400, 400, 600]:
        for hy in range(head_top+80, coat_hem_y, 90):
            d.ellipse([cx+hx-8, hy-4, cx+hx+8, hy+4], fill=K.HAIRHL)

    # ── BODY / COAT (navy blue parka) ──
    # Coat main shape — flared parka
    coat_pts = [
        (cx-body_rx-30, body_top-10),
        (cx+body_rx+30, body_top-10),
        (cx+body_rx+80, coat_hem_y),
        (cx-body_rx-80, coat_hem_y)
    ]
    d.polygon(coat_pts, fill=K.NAVY)
    # Coat lighter areas (sides)
    d.polygon([(cx-body_rx-20,body_top+50),(cx-body_rx+60,body_top+50),
               (cx-body_rx+40,coat_hem_y-30),(cx-body_rx-60,coat_hem_y-30)], fill=K.NAVYL)
    d.polygon([(cx+body_rx-60,body_top+50),(cx+body_rx+20,body_top+50),
               (cx+body_rx+60,coat_hem_y-30),(cx+body_rx-40,coat_hem_y-30)], fill=K.NAVYL)
    # Coat highlight
    d.polygon([(cx-80,body_top+80),(cx+80,body_top+80),(cx+90,coat_hem_y-20),(cx-90,coat_hem_y-20)], fill=K.NAVYHL)

    # ── TAN TRIM on collar, cuffs, hem ──
    # Collar trim
    d.polygon([(cx-body_rx-25,body_top-5),(cx+body_rx+25,body_top-5),
               (cx+body_rx+20,body_top+40),(cx-body_rx-20,body_top+40)], fill=K.TAN)
    d.polygon([(cx-body_rx-22,body_top+35),(cx+body_rx+22,body_top+35),
               (cx+body_rx+18,body_top+55),(cx-body_rx-18,body_top+55)], fill=K.TAND)
    # Cuff trim — left
    d.polygon([(cx-body_rx-75,coat_hem_y-80),(cx-body_rx-10,coat_hem_y-80),
               (cx-body_rx-10,coat_hem_y-40),(cx-body_rx-75,coat_hem_y-40)], fill=K.TAN)
    # Cuff trim — right
    d.polygon([(cx+body_rx+10,coat_hem_y-80),(cx+body_rx+75,coat_hem_y-80),
               (cx+body_rx+75,coat_hem_y-40),(cx+body_rx+10,coat_hem_y-40)], fill=K.TAN)
    # Hem trim
    d.polygon([(cx-body_rx-80,coat_hem_y-15),(cx+body_rx+80,coat_hem_y-15),
               (cx+body_rx+80,coat_hem_y+10),(cx-body_rx-80,coat_hem_y+10)], fill=K.TAN)

    # ── CREAM SHIRT visible at V-neck ──
    d.polygon([(cx-120,body_top+10),(cx,body_top+80),(cx+120,body_top+10)], fill=K.CREAM)
    d.polygon([(cx-100,body_top+15),(cx,body_top+70),(cx+100,body_top+15)], fill=K.CREAMD)

    # ── BLUE BOW TIE ──
    # Left wing
    d.polygon([(cx-10,body_top+5),(cx-90,body_top+25),(cx-10,body_top+55)], fill=K.BOW)
    # Right wing
    d.polygon([(cx+10,body_top+5),(cx+90,body_top+25),(cx+10,body_top+55)], fill=K.BOW)
    # Center knot
    d.ellipse([cx-12,body_top+18,cx+12,body_top+42], fill=K.BOWHL)
    # Bow highlight
    d.ellipse([cx-65,body_top+28,cx-30,body_top+40], fill=K.BOWHL)
    d.ellipse([cx+30,body_top+28,cx+65,body_top+40], fill=K.BOWHL)

    # ── GOLD BUTTONS ──
    for by in range(body_top+100, coat_hem_y-30, 120):
        d.ellipse([cx-12,by-12,cx+12,by+12], fill=K.GOLD)
        d.ellipse([cx-6,by-6,cx+6,by+6], fill=K.GOLDHL)

    # ── GOLD EMBLEM on left chest (our right) ──
    emb_x = cx + int(body_rx * 0.4)
    emb_y = body_top + int((coat_hem_y-body_top)*0.3)
    d.ellipse([emb_x-30,emb_y-30,emb_x+30,emb_y+30], fill=K.GOLD)
    d.ellipse([emb_x-22,emb_y-22,emb_x+22,emb_y+22], fill=K.NAVY)
    d.ellipse([emb_x-14,emb_y-14,emb_x+14,emb_y+14], fill=K.GOLD)

    # ── SKIRT (navy pleated) ──
    d.polygon([(cx-body_rx-60, coat_hem_y+5),
               (cx+body_rx+60, coat_hem_y+5),
               (cx+body_rx+100, skirt_bot_y),
               (cx-body_rx-100, skirt_bot_y)], fill=K.SKIRT)
    # Pleats
    for px in range(-body_rx-80, body_rx+80, 70):
        d.polygon([(cx+px-20,coat_hem_y+30),(cx+px+20,coat_hem_y+30),
                   (cx+px+10,skirt_bot_y-10),(cx+px-30,skirt_bot_y-10)], fill=K.SKIRTL)

    # ── LEGS (skin) ──
    for side in [-1, 1]:
        lx = cx + side * 160
        d.polygon([(lx-55,skirt_bot_y-5),(lx+55,skirt_bot_y-5),
                   (lx+45,skirt_bot_y+180),(lx-45,skirt_bot_y+180)], fill=K.SKN)

    # ── WHITE FRILLED SOCKS ──
    for side in [-1, 1]:
        lx = cx + side * 160
        sock_top = skirt_bot_y + 160
        # Sock body
        d.polygon([(lx-50,sock_top),(lx+50,sock_top),
                   (lx+48,sock_top+120),(lx-48,sock_top+120)], fill=K.SOCK)
        # Frill at top — wavy, PROMINENT
        for fx in range(lx-55, lx+55, 14):
            d.ellipse([fx-9,sock_top-15,fx+9,sock_top+10], fill=K.SOCKD)
            d.ellipse([fx-7,sock_top-12,fx+7,sock_top+7], fill=K.SOCK)
        # Lace pattern
        for fx in range(lx-45, lx+45, 20):
            d.ellipse([fx-3,sock_top+8,fx+3,sock_top+18], fill=K.SOCKD)

    # ── SHOES (dark navy, rounded) ──
    for side in [-1, 1]:
        lx = cx + side * 160
        shoe_y = skirt_bot_y + 280
        d.ellipse([lx-60,shoe_y-20,lx+60,shoe_y+40], fill=K.SHOE)
        d.ellipse([lx-45,shoe_y-12,lx+45,shoe_y+25], fill=K.SHOEL)
        # White toe cap
        d.ellipse([lx-35,shoe_y-10,lx+35,shoe_y+12], fill=(240,238,235))

    # ── ARMS (slightly out, palms forward) ──
    for side in [-1, 1]:
        ax = cx + side * (body_rx + 60)
        # Upper arm (coat sleeve)
        d.polygon([(ax-40,body_top+80),(ax+40,body_top+80),
                   (ax+side*30,body_top+280),(ax-side*10,body_top+280)], fill=K.NAVY)
        # TAN CUFF TRIM on sleeves
        d.polygon([(ax-42,body_top+260),(ax+38,body_top+260),
                   (ax+side*32,body_top+290),(ax-side*8,body_top+290)], fill=K.TAN)
        d.polygon([(ax-40,body_top+278),(ax+36,body_top+278),
                   (ax+side*30,body_top+300),(ax-side*6,body_top+300)], fill=K.TAND)
        # Hand — round, open
        hand_y = body_top + 290
        d.ellipse([ax-35,hand_y-15,ax+35,hand_y+50], fill=K.SKN)
        # Fingers — 4 small rounded
        for fi in range(4):
            fx = ax - 18 + fi * 12
            d.ellipse([fx-5,hand_y+40,fx+5,hand_y+65], fill=K.SKN)

    # ── NECK ──
    d.polygon([(cx-60,body_top-30),(cx+60,body_top-30),
               (cx+50,body_top+15),(cx-50,body_top+15)], fill=K.SKN)

    # ── FACE (round chibi) ──
    d.ellipse([cx-head_rx, head_cy-head_ry, cx+head_rx, head_cy+head_ry], fill=K.SKN)
    # Lighter center
    d.ellipse([cx-head_rx+100, head_cy-head_ry+50, cx+head_rx-100, head_cy+head_ry-50], fill=K.SKN_H)

    # ── HAIR BANGS — fluffy chestnut ──
    bang_y = head_top + 100
    # Main bang mass
    d.polygon([
        (cx-head_rx-30, bang_y),
        (cx-head_rx+100, head_top-50),
        (cx-200, head_top+20),
        (cx, head_top+50),
        (cx+200, head_top+20),
        (cx+head_rx-100, head_top-50),
        (cx+head_rx+30, bang_y),
        (cx+head_rx+20, head_cy-50),
        (cx+200, head_cy-80),
        (cx, head_cy-60),
        (cx-200, head_cy-80),
        (cx-head_rx-20, head_cy-50),
    ], fill=K.HAIR)
    # Bangs fringe — individual strands
    for bx in range(cx-head_rx+60, cx+head_rx-60, 80):
        strand_top = head_top + 80 + abs(bx-cx)//15
        strand_bot = bang_y + 100 + (bx-cx)%40
        d.polygon([(bx-15,strand_top),(bx+15,strand_top),
                   (bx+8,strand_bot),(bx-8,strand_bot)], fill=K.HAIR2)

    # ── SIDE HAIR — fluffy, spread out (NOT braids) ──
    for side in [-1, 1]:
        sx = cx + side * (head_rx - 30)
        # Multiple thin layers spreading outward
        for sy in range(bang_y, chin_y + 200, 20):
            wave = int(12*math.sin(sy/70))
            for offset in [-25, -10, 5, 20]:
                d.ellipse([sx+wave+offset-18,sy-10,sx+wave+offset+18,sy+10], fill=K.HAIR)
            # Outer wisps
            wisp_x = sx + side * (40 + int(20*math.sin(sy/60)))
            d.ellipse([wisp_x-12,sy-8,wisp_x+12,sy+8], fill=K.HAIR3)
        # Bottom hair — fluffy ends
        for wx in range(sx-60, sx+60, 25):
            end_y = chin_y + 180 + int(30*math.sin(wx/40))
            d.ellipse([wx-15,end_y-12,wx+15,end_y+12], fill=K.HAIR2)

    # ── HAIR SHEEN on bangs ──
    d.arc([cx-300,head_top,cx+100,bang_y+50], 210, 340, fill=K.HAIRSH, width=5)
    d.arc([cx+50,head_top,cx+400,bang_y+50], 210, 340, fill=K.HAIRHL, width=4)

    # ── AHOGE (cowlick — stray hair tuft on top) ──
    ahoge_x = cx + 50
    ahoge_top = head_top - 80
    # Curved strand going up-right
    d.polygon([(ahoge_x-8,head_top+30),(ahoge_x+8,head_top+30),
               (ahoge_x+25,ahoge_top+40),(ahoge_x+40,ahoge_top),
               (ahoge_x+30,ahoge_top-20),(ahoge_x+15,ahoge_top+20)], fill=K.HAIR)
    d.polygon([(ahoge_x-5,head_top+40),(ahoge_x+5,head_top+40),
               (ahoge_x+20,ahoge_top+50),(ahoge_x+35,ahoge_top+10)], fill=K.HAIR2)

    # ── GOGGLES on forehead ──
    gog_y = head_top + 160
    gog_r = 90  # goggle lens radius
    for gx in [cx-150, cx+150]:
        # Lens (tinted — gradient from dark to medium)
        d.ellipse([gx-gog_r,gog_y-gog_r,gx+gog_r,gog_y+gog_r], fill=K.GOGD)
        grad_ell(d, [gx-gog_r+12,gog_y-gog_r+12,gx+gog_r-12,gog_y+gog_r-12],
                 K.GOGL, K.GOGD, steps=6)
        # Frame ring — thick
        d.arc([gx-gog_r-8,gog_y-gog_r-8,gx+gog_r+8,gog_y+gog_r+8], 0, 360, fill=K.GOGD, width=10)
        # Lens reflection
        d.ellipse([gx-gog_r+18,gog_y-gog_r+18,gx-gog_r+50,gog_y-gog_r+50], fill=K.GOGHL)
    # Bridge connecting goggles
    d.polygon([(cx-65,gog_y-15),(cx+65,gog_y-15),(cx+65,gog_y+15),(cx-65,gog_y+15)], fill=K.GOGD)
    # Strap going around head (behind hair, visible at sides)
    for side in [-1, 1]:
        sx = cx + side * (head_rx - 50)
        d.polygon([(sx-15,gog_y-12),(sx+15,gog_y-12),(sx+12,gog_y+12),(sx-12,gog_y+12)], fill=K.GOGHL)

    # ── HAIR CLIPS — colorful flowers ──
    # Left side (our right) — purple-pink-blue
    flower_clip(d, cx+head_rx-30, bang_y+60, 35, [K.CLIP_P, K.CLIP_B, (160,60,170)])
    # Right side (our left) — yellow-green-orange
    flower_clip(d, cx-head_rx+30, bang_y+60, 35, [K.CLIP_Y, K.CLIP_G, K.CLIP_O])

    # ── EARS (peek from under hair) ──
    for ex in [cx-head_rx+40, cx+head_rx-40]:
        d.ellipse([ex-25,eye_y-30,ex+25,eye_y+35], fill=K.SKN)
        d.ellipse([ex-12,eye_y-15,ex+12,eye_y+20], fill=K.SKN_M)

    # ── EYES — large round amber ──
    spark_eye(d, cx-eye_offset, eye_y, K.IRIS1, K.IRIS2, K.IRISHL, r=eye_r)
    spark_eye(d, cx+eye_offset, eye_y, K.IRIS1, K.IRIS2, K.IRISHL, r=eye_r)

    # ── EYEBROWS ──
    for bx in [cx-eye_offset, cx+eye_offset]:
        d.arc([bx-45,eye_y-eye_r-25,bx+45,eye_y-eye_r+15], 200, 340, fill=K.BROW, width=5)

    # ── NOSE — tiny dot ──
    d.ellipse([cx-5,eye_y+eye_r+30,cx+5,eye_y+eye_r+42], fill=K.SKN_M)

    # ── MOUTH — small curved smile ──
    d.arc([cx-30,mouth_y-8,cx+30,mouth_y+15], 10, 170, fill=(200,120,110), width=4)

    # ── BLUSH — round pink circles ──
    d.ellipse([cx-eye_offset-eye_r//2, eye_y+20, cx-eye_offset+eye_r//2+20, eye_y+eye_r+10], fill=K.BLUSH)
    d.ellipse([cx+eye_offset-eye_r//2-20, eye_y+20, cx+eye_offset+eye_r//2, eye_y+eye_r+10], fill=K.BLUSH)

    # ── SPARKLES ──
    random.seed(42)
    for _ in range(20):
        sx = cx + random.randint(-head_rx-100, head_rx+100)
        sy = random.randint(head_top-50, feet_y)
        ss = random.randint(8, 20)
        d.polygon([(sx,sy-ss),(sx+ss//4,sy),(sx,sy+ss),(sx-ss//4,sy)], fill=K.STAR)
        d.polygon([(sx-ss,sy),(sx,sy-ss//4),(sx+ss,sy),(sx,sy+ss//4)], fill=K.STAR)

    return img


# ============================================================
# ASCII CONVERSION
# ============================================================
def to_ascii(source, cols, rows, cell_px, blur=1.0):
    blurred = source.filter(ImageFilter.GaussianBlur(radius=blur))
    pixels = blurred.load()
    sw, sh = blurred.size
    out = Image.new("RGB", (cols*cell_px, rows*cell_px), K.BG)
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
# MAIN
# ============================================================
def main():
    print("="*60)
    print("✨ LINH — Xiangling-inspired Chibi ASCII Art")
    print("   3000x3000 vector → high-density ASCII")
    print("="*60)

    print("\n🎨 Drawing character...")
    vec = draw_xiangling()
    vec.save(os.path.join(OUTPUT, "vector.png"))
    print(f"  Vector: {vec.size}")

    # Full detail: 700 cols × 700 rows, 1.5px cells = 1050×1050
    print("\n  Converting to ASCII (700x700, 1.5px)...")
    full = to_ascii(vec, 700, 700, 2, blur=1.0)
    full.save(os.path.join(OUTPUT, "linh_full.png"))
    print(f"  Full: {full.size}")

    # Half body crop (top 60%)
    hw, hh = full.size
    half_h = int(hh * 0.6)
    half = full.crop((0, 0, hw, half_h))
    half.save(os.path.join(OUTPUT, "linh_half.png"))
    print(f"  Half: {half.size}")

    print(f"\n✅ Saved to {OUTPUT}/")


if __name__ == "__main__":
    main()
