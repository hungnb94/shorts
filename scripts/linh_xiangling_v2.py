#!/usr/bin/env python3
"""
Linh Chibi v2 — Accurate recreation from reference photo
6000x6000 vector → 1400x1400 ASCII grid (1.96M cells)
Short fluffy bob, blue goggle lenses, boxy coat, knee-high socks, Mary Janes
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, math, random

OUTPUT = "/Users/hung/code/ai/shorts/output/linh_chibi_v2"
os.makedirs(OUTPUT, exist_ok=True)

BLOCK = '\u2588'
MONO  = "/System/Library/Fonts/Menlo.ttc"

def fnt(p, s):
    try: return ImageFont.truetype(p, s)
    except: return ImageFont.load_default()


# ============================================================
# COLORS — matching reference exactly
# ============================================================
class K:
    # Skin
    SKN_H  = (255, 232, 215)
    SKN    = (245, 215, 190)
    SKN_M  = (225, 188, 160)
    SKN_D  = (200, 165, 138)
    BLUSH  = (255, 175, 175)

    # Hair — warm chestnut bob
    HAIR   = (139, 98, 68)    # #8B6244 base
    HAIR2  = (165, 120, 85)
    HAIR3  = (110, 75, 48)
    HAIRSH = (196, 151, 106)  # #C4976A highlights

    # Eyes — amber with almond-round shape
    EYE_W  = (250, 248, 252)
    IRIS1  = (180, 115, 35)
    IRIS2  = (45, 24, 16)     # #2D1810 dark pupil
    IRISHL = (255, 240, 180)
    IRISHL2= (255, 255, 255)
    PUPIL  = (20, 12, 8)
    BROW   = (55, 35, 22)

    # Goggles — blue gradient lenses
    GOG_FR = (92, 58, 34)     # #5C3A22 frame
    GOG_L1 = (74, 135, 184)   # #4A87B8 dark edge
    GOG_L2 = (123, 173, 212)  # #7BADD4 light center
    GOG_HL = (170, 210, 240)
    GOG_STR= (110, 75, 48)    # strap

    # Clothing
    NAVY   = (26, 44, 72)     # #1A2C48
    NAVYL  = (40, 58, 88)
    NAVYHL = (55, 72, 105)
    CREAM  = (245, 235, 215)
    CREAMD = (225, 212, 188)
    TAN    = (212, 192, 168)  # #D4C0A8 collar/cuff trim
    TAND   = (188, 168, 142)
    BOW    = (56, 104, 168)   # #3868A8 blue bow
    BOWHL  = (80, 130, 195)
    EMBLEM = (232, 150, 58)   # #E8963A gear/flower
    EMBLEML= (245, 175, 90)
    BTNON  = (92, 58, 34)     # dark brown buttons
    BTNONHL= (120, 85, 55)

    # Skirt
    SKIRT  = (26, 44, 72)
    SKIRTL = (40, 58, 85)
    SKIRTTR= (212, 192, 168)  # tan trim at hem

    # Socks — knee-high white
    SOCK   = (248, 248, 250)
    SOCKD  = (228, 225, 228)

    # Shoes — Mary Jane dark brown
    SHOE   = (58, 34, 18)     # #3A2212
    SHOEL  = (80, 52, 32)
    BUCKLE = (212, 168, 56)   # #D4A838 gold buckle

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


def draw_eye(d, cx, cy, r=80):
    """Almond-round eye with two highlights."""
    # White — slightly almond tilted up at outer corners
    d.ellipse([cx-r,cy-int(r*0.55),cx+r,cy+int(r*0.6)], fill=K.EYE_W)
    # Iris — large, gradient
    ir = int(r*0.7)
    grad_ell(d, [cx-ir,cy-int(ir*0.25),cx+ir,cy+int(ir*0.65)],
             K.IRIS1, (120,75,25), steps=8)
    # Pupil — dark
    pr = int(r*0.28)
    d.ellipse([cx-pr,cy-pr//2,cx+pr,cy+pr], fill=K.PUPIL)
    # MAIN highlight — top-left, large white circle
    hr = int(r*0.22)
    d.ellipse([cx-int(r*0.35),cy-int(r*0.35),
               cx-int(r*0.35)+hr*2,cy-int(r*0.35)+hr*2], fill=(255,255,255))
    # Secondary highlight — bottom-right, smaller
    hr2 = int(r*0.1)
    d.ellipse([cx+int(r*0.2),cy+int(r*0.15),
               cx+int(r*0.2)+hr2*2,cy+int(r*0.15)+hr2*2], fill=(255,245,240))
    # Upper lash — thick, slight up-tilt at outer
    d.arc([cx-r-5,cy-int(r*0.65),cx+r+5,cy+int(r*0.3)], 195, 345, fill=K.BROW, width=7)
    # Lashes — 3 per outer corner
    for angle in [202,213,224]:
        rad = math.radians(angle)
        lx1 = cx + int((r-3)*math.cos(rad))
        ly1 = cy + int(r*0.45*math.sin(rad))
        lx2 = cx + int((r+16)*math.cos(rad))
        ly2 = cy + int(r*0.45*math.sin(rad)) - 12
        d.line([(lx1,ly1),(lx2,ly2)], fill=K.BROW, width=3)
    for angle in [318,330,342]:
        rad = math.radians(angle)
        lx1 = cx + int((r-3)*math.cos(rad))
        ly1 = cy + int(r*0.45*math.sin(rad))
        lx2 = cx + int((r+14)*math.cos(rad))
        ly2 = cy + int(r*0.45*math.sin(rad)) - 10
        d.line([(lx1,ly1),(lx2,ly2)], fill=K.BROW, width=3)
    # Faint pink lower waterline
    d.arc([cx-int(r*0.75),cy-int(r*0.1),cx+int(r*0.75),cy+int(r*0.5)],
          15, 165, fill=(220,195,185), width=2)


def draw_flower_clip(d, cx, cy, size):
    """Multi-color flower hair clip."""
    colors = [(100,130,200), (180,100,180), (220,185,50)]
    for i, c in enumerate(colors):
        angle = math.radians(i * 120 - 90)
        px = cx + int(size*0.5*math.cos(angle))
        py = cy + int(size*0.5*math.sin(angle))
        d.ellipse([px-size//2,py-size//2,px+size//2,py+size//2], fill=c)
    d.ellipse([cx-size//5,cy-size//5,cx+size//5,cy+size//5], fill=(240,200,80))


# ============================================================
# DRAW CHARACTER — exact proportions from reference
# ============================================================
def draw_character():
    """6000x6000 vector with exact reference proportions."""
    sz = 6000
    W = sz
    img = Image.new("RGB", (sz, sz), K.BG)
    d = ImageDraw.Draw(img)
    cx = sz // 2

    # ── PROPORTIONS from reference analysis ──
    # Height: Head 1 : Body 0.9 : Legs 1.1
    # Head top at ~10%, chin at ~38%, body to ~65%, legs to ~95%
    head_top = int(sz * 0.08)
    chin_y = int(sz * 0.40)
    head_cy = (head_top + chin_y) // 2  # 2400
    head_rx = int(sz * 0.30)  # 1800 — head width 60%
    head_ry = (chin_y - head_top) // 2  # ~1560

    body_top = chin_y
    body_rx = int(head_rx * 0.50)  # 900 — body narrower than head
    coat_hem_y = int(sz * 0.63)
    skirt_bot_y = int(sz * 0.76)
    sock_top_y = skirt_bot_y
    sock_bot_y = int(sz * 0.90)
    feet_y = int(sz * 0.96)

    eye_y = int(head_cy + head_ry * 0.1)  # slightly below center
    eye_sep = int(head_rx * 0.38)
    eye_r = int(head_rx * 0.22)  # large eyes

    # ── HAIR BEHIND — short fluffy bob ──
    # Bob shape: wide, ends just below chin
    bob_bottom = chin_y + int(head_ry * 0.4)  # short, just below chin
    d.ellipse([cx-head_rx-80, head_top-30, cx+head_rx+80, bob_bottom], fill=K.HAIR)
    # Fluffy volume — multiple overlapping layers
    for lx in range(cx-head_rx-60, cx+head_rx+60, 40):
        for ly in range(head_top+50, bob_bottom, 35):
            # Only draw outside face area
            dist_from_center = abs(lx - cx)
            if dist_from_center > head_rx * 0.7:
                d.ellipse([lx-22,ly-15,lx+22,ly+15], fill=K.HAIR2)
    # Hair sheen
    for hx in [cx-600, cx-300, cx+300, cx+600]:
        for hy in range(head_top+80, bob_bottom-40, 60):
            d.ellipse([hx-12,hy-5,hx+12,hy+5], fill=K.HAIRSH)

    # ── NECK ──
    d.polygon([(cx-90,body_top-20),(cx+90,body_top-20),
               (cx+70,body_top+40),(cx-70,body_top+40)], fill=K.SKN)

    # ── BODY — S-CURVE feminine silhouette ──
    waist_y = body_top + int((coat_hem_y - body_top) * 0.38)
    hip_y = body_top + int((coat_hem_y - body_top) * 0.65)
    waist_rx = int(body_rx * 0.28)
    hip_rx = int(body_rx * 1.45)
    # OUTLINE — very visible color to show S-curve
    outline_pts = [
        (cx - body_rx - 48, body_top - 5),
        (cx - waist_rx - 10, waist_y),
        (cx - hip_rx - 40, hip_y),
        (cx - body_rx - 130, coat_hem_y + 5),
        (cx + body_rx + 130, coat_hem_y + 5),
        (cx + hip_rx + 40, hip_y),
        (cx + waist_rx + 10, waist_y),
        (cx + body_rx + 48, body_top - 5),
    ]
    d.polygon(outline_pts, fill=(70, 100, 150))  # clearly visible blue outline
    coat_pts = [
        (cx - body_rx - 40, body_top),
        (cx - waist_rx, waist_y),
        (cx - hip_rx - 30, hip_y),
        (cx - body_rx - 120, coat_hem_y),
        (cx + body_rx + 120, coat_hem_y),
        (cx + hip_rx + 30, hip_y),
        (cx + waist_rx, waist_y),
        (cx + body_rx + 40, body_top),
    ]
    d.polygon(coat_pts, fill=K.NAVY)
    # Draw S-curve OUTLINE on top of coat — visible silhouette
    outline_color = (90, 130, 180)
    # Left side: shoulder → waist → hip → hem
    for i in range(len(coat_pts) // 2 - 1):
        p1 = coat_pts[i]
        p2 = coat_pts[i + 1]
        d.line([p1, p2], fill=outline_color, width=18)
    # Right side: hem → hip → waist → shoulder
    for i in range(len(coat_pts) // 2, len(coat_pts) - 1):
        p1 = coat_pts[i]
        p2 = coat_pts[i + 1]
        d.line([p1, p2], fill=outline_color, width=18)
    # Lighter center panel — follows S-curve tightly
    center_pts = [
        (cx - 80, body_top + 60),
        (cx - 40, waist_y),
        (cx - 90, hip_y),
        (cx - 100, coat_hem_y - 20),
        (cx + 100, coat_hem_y - 20),
        (cx + 90, hip_y),
        (cx + 40, waist_y),
        (cx + 80, body_top + 60),
    ]
    d.polygon(center_pts, fill=K.NAVYL)

    # ── BELT/WAISTBAND — BIG, emphasizes narrow waist ──
    belt_h = 100  # much bigger
    belt_pts = [
        (cx - waist_rx - 20, waist_y - belt_h),
        (cx + waist_rx + 20, waist_y - belt_h),
        (cx + waist_rx + 20, waist_y + belt_h),
        (cx - waist_rx - 20, waist_y + belt_h),
    ]
    d.polygon(belt_pts, fill=K.TAN)
    # Belt holes/detail
    for bx in range(cx - waist_rx + 20, cx + waist_rx, 40):
        d.ellipse([bx - 5, waist_y - 5, bx + 5, waist_y + 5], fill=K.TAND)
    # Belt buckle — BIG
    d.ellipse([cx - 35, waist_y - 30, cx + 35, waist_y + 30], fill=K.BUCKLE)
    d.ellipse([cx - 18, waist_y - 15, cx + 18, waist_y + 15], fill=K.TAND)

    # ── STANDING COLLAR — follows S-curve, narrower at waist ──
    collar_h = 120
    # Outer collar — follows body S-curve
    collar_pts = [
        (cx - body_rx - 35, body_top - collar_h),
        (cx - waist_rx - 10, waist_y - collar_h),
        (cx - waist_rx, waist_y),
        (cx - body_rx - 40, body_top + 10),
        (cx + body_rx + 40, body_top + 10),
        (cx + waist_rx, waist_y),
        (cx + waist_rx + 10, waist_y - collar_h),
        (cx + body_rx + 35, body_top - collar_h),
    ]
    d.polygon(collar_pts, fill=K.TAN)
    # Inner collar fold — also follows S-curve
    collar_inner = [
        (cx - body_rx - 30, body_top - collar_h + 20),
        (cx - waist_rx - 5, waist_y - collar_h + 20),
        (cx - waist_rx + 5, waist_y - 5),
        (cx - body_rx - 35, body_top - 5),
        (cx + body_rx + 35, body_top - 5),
        (cx + waist_rx - 5, waist_y - 5),
        (cx + waist_rx + 5, waist_y - collar_h + 20),
        (cx + body_rx + 30, body_top - collar_h + 20),
    ]
    d.polygon(collar_inner, fill=K.TAND)
    # Collar inner fold
    d.polygon([(cx-80,body_top-collar_h+30),(cx,body_top-collar_h-10),
               (cx+80,body_top-collar_h+30),(cx,body_top+5)], fill=K.CREAM)

    # ── CREAM SHIRT visible at collar ──
    d.polygon([(cx-100,body_top-80),(cx,body_top+10),(cx+100,body_top-80)], fill=K.CREAM)

    # ── BLUE BOW at neck ──
    bow_y = body_top - 60
    # Wings
    d.polygon([(cx-15,bow_y-10),(cx-85,bow_y+15),(cx-15,bow_y+40)], fill=K.BOW)
    d.polygon([(cx+15,bow_y-10),(cx+85,bow_y+15),(cx+15,bow_y+40)], fill=K.BOW)
    # Knot
    d.ellipse([cx-14,bow_y+5,cx+14,bow_y+28], fill=K.BOWHL)
    # Highlights
    d.ellipse([cx-65,bow_y+18,cx-35,bow_y+30], fill=K.BOWHL)
    d.ellipse([cx+35,bow_y+18,cx+65,bow_y+30], fill=K.BOWHL)

    # ── DARK BROWN BUTTONS (not gold!) ──
    for by in range(body_top+120, coat_hem_y-30, 160):
        d.ellipse([cx-14,by-14,cx+14,by+14], fill=K.BTNON)
        d.ellipse([cx-7,by-7,cx+7,by+7], fill=K.BTNONHL)

    # ── GOLD EMBLEM on left chest ──
    emb_x = cx + int(body_rx * 0.4)
    emb_y = body_top + int((coat_hem_y-body_top)*0.3)
    # Gear/flower shape
    d.ellipse([emb_x-35,emb_y-35,emb_x+35,emb_y+35], fill=K.EMBLEM)
    d.ellipse([emb_x-25,emb_y-25,emb_x+25,emb_y+25], fill=K.NAVY)
    d.ellipse([emb_x-15,emb_y-15,emb_x+15,emb_y+15], fill=K.EMBLEML)
    # Gear teeth
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        tx = emb_x + int(30*math.cos(rad))
        ty = emb_y + int(30*math.sin(rad))
        d.ellipse([tx-5,ty-5,tx+5,ty+5], fill=K.EMBLEM)

    # ── SKIRT — navy pleated, follows S-curve hips, tan trim ──
    skirt_pts = [
        (cx - hip_rx - 30, coat_hem_y),
        (cx + hip_rx + 30, coat_hem_y),
        (cx + body_rx + 180, skirt_bot_y),
        (cx - body_rx - 180, skirt_bot_y),
    ]
    d.polygon(skirt_pts, fill=K.SKIRT)
    # Pleats
    for px in range(cx - body_rx - 160, cx + body_rx + 160, 80):
        d.polygon([(px - 22, coat_hem_y + 40), (px + 22, coat_hem_y + 40),
                   (px + 12, skirt_bot_y - 10), (px - 32, skirt_bot_y - 10)], fill=K.SKIRTL)
    # TAN TRIM at skirt hem
    d.polygon([(cx - body_rx - 185, skirt_bot_y - 20), (cx + body_rx + 185, skirt_bot_y - 20),
               (cx + body_rx + 180, skirt_bot_y + 15), (cx - body_rx - 180, skirt_bot_y + 15)], fill=K.SKIRTTR)

    # ── LEGS — chibi proportions, 20% of head width ──
    for side in [-1, 1]:
        lx = cx + side * 420
        # Thigh — 720px wide
        d.polygon([(lx-360,skirt_bot_y+10),(lx+360,skirt_bot_y+10),
                   (lx+300,skirt_bot_y+450),(lx-300,skirt_bot_y+450)], fill=K.SKN)
        # Knee
        ky = skirt_bot_y + 450
        d.polygon([(lx-300,ky-20),(lx+300,ky-20),
                   (lx+230,ky+250),(lx-230,ky+250)], fill=K.SKN)
        # Calf
        cy = ky + 250
        d.polygon([(lx-230,cy),(lx+230,cy),
                   (lx+180,cy+350),(lx-180,cy+350)], fill=K.SKN)
        # Ankle
        an_y = cy + 350
        d.polygon([(lx-180,an_y),(lx+180,an_y),
                   (lx+200,an_y+120),(lx-200,an_y+120)], fill=K.SKN_M)

    # ── KNEE-HIGH WHITE SOCKS ──
    for side in [-1, 1]:
        lx = cx + side * 420
        sock_start_y = skirt_bot_y + 700
        sock_end_y = feet_y - 80
        d.polygon([(lx-185,sock_start_y),(lx+185,sock_start_y),
                   (lx+180,sock_end_y),(lx-180,sock_end_y)], fill=K.SOCK)
        for ry in range(sock_start_y, sock_end_y, 50):
            d.line([(lx-182,ry),(lx+182,ry)], fill=K.SOCKD, width=4)
        for fx in range(lx-195, lx+195, 28):
            d.ellipse([fx-16,sock_start_y-28,fx+16,sock_start_y+22], fill=K.SOCKD)
            d.ellipse([fx-14,sock_start_y-24,fx+14,sock_start_y+18], fill=K.SOCK)

    # ── MARY JANE SHOES — 15% of head = 540px wide ──
    for side in [-1, 1]:
        lx = cx + side * 420
        d.ellipse([lx-270,feet_y-90,lx+270,feet_y+150], fill=K.SHOE)
        d.ellipse([lx-230,feet_y-70,lx+230,feet_y+120], fill=K.SHOEL)
        d.polygon([(lx-275,feet_y+115),(lx+275,feet_y+115),
                   (lx+280,feet_y+150),(lx-280,feet_y+150)], fill=(40,25,12))
        d.polygon([(lx-190,feet_y-80),(lx+190,feet_y-80),
                   (lx+188,feet_y-48),(lx-188,feet_y-48)], fill=K.SHOE)
        d.ellipse([lx-25,feet_y-85,lx+25,feet_y-45], fill=K.BUCKLE)
        d.ellipse([lx-12,feet_y-78,lx+12,feet_y-52], fill=K.SHOE)

    # ── FACE — perfect round chibi ──
    d.ellipse([cx-head_rx, head_cy-head_ry, cx+head_rx, head_cy+head_ry], fill=K.SKN)
    d.ellipse([cx-head_rx+120, head_cy-head_ry+80,
               cx+head_rx-120, head_cy+head_ry-80], fill=K.SKN_H)

    # ── HAIR BANGS — straight-cut, fluffy bob ──
    bang_bot = head_cy - int(head_ry * 0.25)  # ends above eyebrows
    d.polygon([
        (cx-head_rx-40, head_top+50),
        (cx-head_rx+150, head_top-20),
        (cx-250, head_top+60),
        (cx, head_top+90),
        (cx+250, head_top+60),
        (cx+head_rx-150, head_top-20),
        (cx+head_rx+40, head_top+50),
        (cx+head_rx+30, bang_bot),
        (cx+200, bang_bot+40),
        (cx, bang_bot+50),
        (cx-200, bang_bot+40),
        (cx-head_rx-30, bang_bot),
    ], fill=K.HAIR)
    # Bangs fringe — straight-cut strands
    for bx in range(cx-head_rx+80, cx+head_rx-80, 70):
        strand_bot = bang_bot + 30 + (bx-cx)%30
        d.polygon([(bx-18,bang_bot-120),(bx+18,bang_bot-120),
                   (bx+12,strand_bot),(bx-12,strand_bot)], fill=K.HAIR2)
    # Center split hint
    d.line([(cx,bang_bot-100),(cx,bang_bot+20)], fill=K.HAIR3, width=4)
    # Bangs sheen
    d.arc([cx-350,head_top,cx+100,bang_bot+30], 210, 340, fill=K.HAIRSH, width=6)
    d.arc([cx+50,head_top,cx+450,bang_bot+30], 210, 340, fill=K.HAIRSH, width=5)

    # ── SIDE HAIR — fluffy bob framing face ──
    for side in [-1, 1]:
        sx = cx + side * (head_rx - 20)
        # Multiple overlapping layers for fluffiness
        for sy in range(bang_bot-50, bob_bottom, 18):
            wave = int(12*math.sin(sy/55))
            # Inner layer
            for offset in [-20, -5, 10, 25]:
                d.ellipse([sx+wave+offset-18,sy-10,sx+wave+offset+18,sy+10], fill=K.HAIR)
            # Middle layer — slightly different shade
            for offset in [-30, 0, 30]:
                d.ellipse([sx+wave+offset-14,sy-8,sx+wave+offset+14,sy+8], fill=K.HAIR2)
            # Outer fluffy wisps — different directions
            wx = sx + side * (30 + int(18*math.sin(sy/45)))
            d.ellipse([wx-12,sy-7,wx+12,sy+7], fill=K.HAIR3)
            # Extra outer wisps for volume
            wx2 = sx + side * (55 + int(20*math.sin(sy/50)))
            d.ellipse([wx2-8,sy-5,wx2+8,sy+5], fill=K.HAIR3)
        # Bob ends — fluffy curl at bottom
        for bx in range(sx-80, sx+80, 18):
            end_y = bob_bottom + int(15*math.sin(bx/30))
            d.ellipse([bx-12,end_y-10,bx+12,end_y+10], fill=K.HAIR2)
            d.ellipse([bx-8,end_y-6,bx+8,end_y+6], fill=K.HAIR)

    # ── AHOGE (cowlick — single strand curling up) ──
    ah_x = cx + 60
    ah_top = head_top - 100
    # Curved up-right
    d.polygon([(ah_x-10,head_top+40),(ah_x+10,head_top+40),
               (ah_x+30,ah_top+60),(ah_x+50,ah_top+20),
               (ah_x+35,ah_top),(ah_x+20,ah_top+30)], fill=K.HAIR)
    d.polygon([(ah_x-6,head_top+50),(ah_x+6,head_top+50),
               (ah_x+22,ah_top+70),(ah_x+42,ah_top+30)], fill=K.HAIR2)

    # ── FLOWER HAIR CLIPS ──
    draw_flower_clip(d, cx+head_rx-50, bang_bot+20, 45)
    draw_flower_clip(d, cx-head_rx+50, bang_bot+20, 45)

    # ── EARS ──
    for ex in [cx-head_rx+30, cx+head_rx-30]:
        d.ellipse([ex-28,eye_y-35,ex+28,eye_y+40], fill=K.SKN)
        d.ellipse([ex-14,eye_y-18,ex+14,eye_y+22], fill=K.SKN_M)

    # ── EYES — large almond-round amber ──
    draw_eye(d, cx-eye_sep, eye_y, r=eye_r)
    draw_eye(d, cx+eye_sep, eye_y, r=eye_r)

    # ── EYEBROWS — thin, short, arched ──
    for bx in [cx-eye_sep, cx+eye_sep]:
        brow_y = eye_y - eye_r - 20
        d.arc([bx-35,brow_y-10,bx+35,brow_y+20], 200, 340, fill=K.BROW, width=4)

    # ── NOSE — tiny dot ──
    nose_y = eye_y + eye_r + 40
    d.ellipse([cx-6,nose_y-3,cx+6,nose_y+10], fill=K.SKN_M)

    # ── MOUTH — small curved smile ──
    mouth_y = nose_y + 45
    d.arc([cx-28,mouth_y-8,cx+28,mouth_y+14], 12, 168, fill=(200,120,110), width=5)

    # ── BLUSH — round pink circles ──
    blush_y = eye_y + eye_r + 10
    d.ellipse([cx-eye_sep-eye_r//3,blush_y-15,
               cx-eye_sep+eye_r//3+25,blush_y+35], fill=K.BLUSH)
    d.ellipse([cx+eye_sep-eye_r//3-25,blush_y-15,
               cx+eye_sep+eye_r//3,blush_y+35], fill=K.BLUSH)

    # ── SPARKLES ──
    random.seed(42)
    for _ in range(25):
        sx = cx + random.randint(-head_rx-100, head_rx+100)
        sy = random.randint(head_top-50, feet_y)
        ss = random.randint(10, 28)
        d.polygon([(sx,sy-ss),(sx+ss//4,sy),(sx,sy+ss),(sx-ss//4,sy)], fill=K.STAR)
        d.polygon([(sx-ss,sy),(sx,sy-ss//4),(sx+ss,sy),(sx,sy+ss//4)], fill=K.STAR)

    # ── ARMS — ON TOP of everything, WITH OUTLINE for visibility ──
    for side in [-1, 1]:
        shoulder_x = cx + side * (body_rx + 40)
        ax = shoulder_x + side * 400
        arm_mid_y = body_top + int((coat_hem_y - body_top) * 0.5)
        # OUTLINE first (lighter, for visibility against dark bg)
        outline_pts_u = [(shoulder_x - 88, body_top + 55),
                         (shoulder_x + 88, body_top + 55),
                         (ax + 110, arm_mid_y),
                         (ax - 110, arm_mid_y)]
        d.polygon(outline_pts_u, fill=(60, 80, 120))
        outline_pts_l = [(ax - 110, arm_mid_y),
                         (ax + 110, arm_mid_y),
                         (ax + 90, arm_mid_y + 355),
                         (ax - 90, arm_mid_y + 355)]
        d.polygon(outline_pts_l, fill=(60, 80, 120))
        # Upper arm sleeve
        d.polygon([(shoulder_x - 80, body_top + 60),
                   (shoulder_x + 80, body_top + 60),
                   (ax + 100, arm_mid_y),
                   (ax - 100, arm_mid_y)], fill=K.NAVY)
        # Lower sleeve
        d.polygon([(ax - 100, arm_mid_y),
                   (ax + 100, arm_mid_y),
                   (ax + 80, arm_mid_y + 350),
                   (ax - 80, arm_mid_y + 350)], fill=K.NAVY)
        # TAN CUFF
        d.polygon([(ax - 82, arm_mid_y + 330),
                   (ax + 78, arm_mid_y + 330),
                   (ax + 82, arm_mid_y + 410),
                   (ax - 78, arm_mid_y + 410)], fill=K.TAN)
        d.polygon([(ax - 80, arm_mid_y + 390),
                   (ax + 76, arm_mid_y + 390),
                   (ax + 80, arm_mid_y + 440),
                   (ax - 76, arm_mid_y + 440)], fill=K.TAND)
        # WRIST
        wy = arm_mid_y + 440
        d.polygon([(ax - 65, wy), (ax + 65, wy),
                   (ax + 60, wy + 90), (ax - 60, wy + 90)], fill=K.SKN)
        # HAND — BIG chibi
        palm_y = wy + 90
        d.ellipse([ax-400,palm_y-80,ax+400,palm_y+550], fill=K.SKN)
        d.ellipse([ax-340,palm_y+60,ax+340,palm_y+470], fill=K.SKN_H)
        # 5 fingers — MAXIMUM SPREAD
        finger_data = [
            (-420, -160, 85),  # thumb — far out
            (-190, -260, 68),  # index
            (15,   -310, 68),  # middle — longest
            (220,  -270, 68),  # ring
            (420,  -200, 60),  # pinky — shortest
        ]
        for fx_off, fy_off, fr in finger_data:
            fpx = ax + fx_off
            fpy = palm_y + fy_off
            if abs(fx_off) > 300:
                d.ellipse([fpx-fr,fpy-fr,fpx+fr+120,fpy+fr], fill=K.SKN)
            else:
                d.ellipse([fpx-fr,fpy-fr,fpx+fr,fpy+fr+65], fill=K.SKN)
                d.ellipse([fpx-fr+12,fpy-fr+8,fpx+fr-12,fpy-fr+70], fill=(230,185,160))

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
    total = rows * cols
    done = 0
    for gy in range(rows):
        for gx in range(cols):
            sx = min(int(gx*cw+cw/2), sw-1)
            sy = min(int(gy*ch+ch/2), sh-1)
            r,g,b = pixels[sx,sy]
            if r<15 and g<15 and b<20: continue
            draw.text((gx*cell_px, gy*cell_px), BLOCK, fill=(r,g,b), font=font)
            done += 1
        if gy % 200 == 0:
            print(f"    {100*gy//rows}% ({gy}/{rows} rows)")
    return out


# ============================================================
# MAIN
# ============================================================
def main():
    print("="*60)
    print("✨ LINH v2 — Xiangling Accurate Chibi (10x)")
    print("   6000x6000 vector → 1400x1400 ASCII (1.96M cells)")
    print("="*60)

    print("\n🎨 Drawing character (6000x6000)...")
    vec = draw_character()
    vec.save(os.path.join(OUTPUT, "vector.png"))
    print(f"  Vector: {vec.size}")

    # 10x: 1400 cols × 1400 rows, 2px cells = 2800×2800
    print("\n  Converting to ASCII (1400x1400, 2px cells)...")
    full = to_ascii(vec, 1400, 1400, 2, blur=1.2)
    full.save(os.path.join(OUTPUT, "linh_v2_full.png"))
    print(f"  Full: {full.size}")

    # Half body
    hw, hh = full.size
    half_h = int(hh * 0.55)
    half = full.crop((0, 0, hw, half_h))
    half.save(os.path.join(OUTPUT, "linh_v2_half.png"))
    print(f"  Half: {half.size}")

    print(f"\n✅ Saved to {OUTPUT}/")


if __name__ == "__main__":
    main()
