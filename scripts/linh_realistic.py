#!/usr/bin/env python3
"""
Linh Realistic Portrait — based on reference photo
Oval face, almond brown eyes, wavy brown hair with golden highlights,
coral lips, warm skin with freckles, black strapless top, gold necklace
Full body extrapolation: jeans + casual stance
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, math, random

OUTPUT = "/Users/hung/code/ai/shorts/output/linh_realistic"
os.makedirs(OUTPUT, exist_ok=True)

sz = 3000
BLOCK = '\u2588'
MONO = "/System/Library/Fonts/Menlo.ttc"

def fnt(p,s):
    try: return ImageFont.truetype(p,s)
    except: return ImageFont.load_default()

# ============================================================
# COLORS — matched to reference photo
# ============================================================
class C:
    # Skin — warm golden undertone (#C49B6B range)
    SKN_H  = (245, 218, 185)  # highlight (forehead, nose bridge)
    SKN_L  = (232, 200, 165)  # light
    SKN    = (218, 182, 142)  # base
    SKN_M  = (198, 162, 122)  # mid shadow
    SKN_D  = (175, 140, 100)  # deep shadow
    SKN_DD = (155, 122, 85)   # darkest
    FRECK  = (185, 145, 105)  # freckle color

    # Hair — dark brown with golden highlights
    HBRN  = (42, 30, 25)     # dark brown base
    HBRN2 = (58, 42, 32)     # mid brown
    HHIL  = (110, 78, 48)    # golden highlight
    HHIL2 = (140, 100, 60)   # bright highlight

    # Eyes — brown/hazel with golden undertone
    EW    = (238, 235, 230)
    EIR   = (130, 85, 40)    # warm brown iris
    EIR2  = (95, 62, 28)     # iris edge
    EIR_H = (165, 120, 60)   # iris highlight (golden)
    EPUP  = (15, 12, 10)
    EHIL  = (255, 255, 255)
    EHIL2 = (200, 185, 160)

    # Eyebrows — dark brown, arched
    BROW  = (45, 32, 25)

    # Lips — warm coral/reddish-orange (VIBRANT)
    LIP   = (210, 95, 65)    # vibrant coral
    LIPL  = (225, 125, 85)   # lighter coral
    LIPD  = (180, 72, 48)    # darker line
    LIPHL = (240, 160, 130)  # highlight

    # Nose
    NSHAD = (188, 152, 112)
    NHI   = (240, 215, 185)

    # Blush
    BLUSH = (220, 168, 145)

    # Black top
    TOP   = (18, 18, 22)
    TOP_L = (35, 35, 40)
    TOP_H = (50, 50, 55)

    # Blue jeans
    JNS   = (55, 75, 110)
    JNS_L = (75, 100, 140)
    JNS_D = (40, 55, 85)
    JNS_H = (90, 115, 155)

    # Gold necklace
    GOLD  = (210, 185, 80)
    GOLD_H= (240, 220, 130)

    BG = (8, 8, 14)


# ============================================================
# HELPERS
# ============================================================
def grad_ell(d, bbox, c1, c2, steps=16):
    x0,y0,x1,y1 = bbox
    cx,cy=(x0+x1)/2,(y0+y1)/2
    rx,ry=(x1-x0)/2,(y1-y0)/2
    for i in range(steps,0,-1):
        t=i/steps
        r=int(c1[0]*(1-t)+c2[0]*t)
        g=int(c1[1]*(1-t)+c2[1]*t)
        b=int(c1[2]*(1-t)+c2[2]*t)
        d.ellipse([cx-rx*t,cy-ry*t,cx+rx*t,cy+ry*t],fill=(r,g,b))

def bezier_point(p0,p1,p2,t):
    """Quadratic bezier."""
    x=(1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t**2*p2[0]
    y=(1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t**2*p2[1]
    return (x,y)

def draw_bezier(d, p0,p1,p2, fill, width=2, steps=30):
    pts = [bezier_point(p0,p1,p2,i/steps) for i in range(steps+1)]
    for i in range(len(pts)-1):
        d.line([pts[i], pts[i+1]], fill=fill, width=width)


# ============================================================
# DRAW LINH — based on reference photo
# ============================================================
def draw_linh():
    img = Image.new("RGB", (sz, sz), C.BG)
    d = ImageDraw.Draw(img)
    cx = sz // 2

    # === PROPORTIONS ===
    head_top = 200
    head_cy = 380
    chin = 560
    shoulder_y = 650
    collarbone_y = 700
    bust_y = 880
    waist_y = 1200
    hip_y = 1450
    knee_y = 2100
    feet_y = 2700

    # ── HAIR BEHIND — wavy, dark brown with golden highlights ──
    # Base shape
    d.ellipse([cx-240, head_top-20, cx+240, chin+40], fill=C.HBRN)
    # Wavy flowing sides — loose waves
    # Left wave
    pts_l = [(cx-230,chin),(cx-290,700),(cx-320,900),(cx-280,1100),
             (cx-310,1300),(cx-270,1500),(cx-240,1600)]
    for i in range(len(pts_l)-1):
        x1,y1=pts_l[i]; x2,y2=pts_l[i+1]
        w = 80 + 20*math.sin(i*1.2)
        d.polygon([(x1-w,y1),(x1+w,y1),(x2+w+10,y2),(x2-w-10,y2)], fill=C.HBRN)
    # Right wave
    pts_r = [(cx+230,chin),(cx+290,700),(cx+320,900),(cx+280,1100),
             (cx+310,1300),(cx+270,1500),(cx+240,1600)]
    for i in range(len(pts_r)-1):
        x1,y1=pts_r[i]; x2,y2=pts_r[i+1]
        w = 80 + 20*math.sin(i*1.2+1)
        d.polygon([(x1-w,y1),(x1+w,y1),(x2+w+10,y2),(x2-w-10,y2)], fill=C.HBRN)

    # Hair wave texture — undulating highlights
    for wx in [-280, -200, 200, 280]:
        for wy in range(600, 1500, 60):
            wave_x = wx + int(30*math.sin(wy/80))
            d.ellipse([wave_x-15, wy-8, wave_x+15, wy+8], fill=C.HBRN2)

    # Golden highlights in hair
    for hx in [-260, -180, 180, 260]:
        for hy in range(500, 1400, 80):
            wave_x = hx + int(20*math.sin(hy/100))
            d.ellipse([wave_x-8, hy-4, wave_x+8, hy+4], fill=C.HHIL)

    # ── NECK ──
    d.polygon([(cx-55,chin-5),(cx+55,chin-5),(cx+60,shoulder_y+30),(cx-60,shoulder_y+30)], fill=C.SKN)
    d.polygon([(cx-45,chin-5),(cx+45,chin-5),(cx+38,chin+30),(cx-38,chin+30)], fill=C.SKN_M)
    # Neck tendon shadows
    d.line([(cx-30,chin+15),(cx-35,shoulder_y+15)], fill=C.SKN_D, width=3)
    d.line([(cx+30,chin+15),(cx+35,shoulder_y+15)], fill=C.SKN_D, width=3)

    # ── COLLARBONE (prominent, visible due to low neckline) ──
    # Shadow grooves
    d.line([(cx-140,collarbone_y),(cx-40,collarbone_y-15)], fill=C.SKN_D, width=5)
    d.line([(cx+140,collarbone_y),(cx+40,collarbone_y-15)], fill=C.SKN_D, width=5)
    # Bone highlights
    d.line([(cx-130,collarbone_y-3),(cx-35,collarbone_y-18)], fill=C.SKN_H, width=3)
    d.line([(cx+130,collarbone_y-3),(cx+35,collarbone_y-18)], fill=C.SKN_H, width=3)
    # Center pit
    d.ellipse([cx-12,collarbone_y-8,cx+12,collarbone_y+5], fill=C.SKN_M)

    # ── SHOULDERS — BARE SKIN (no fabric = strapless) ──
    d.polygon([(cx-300,shoulder_y-10),(cx+300,shoulder_y-10),
               (cx+280,shoulder_y+80),(cx-280,shoulder_y+80)], fill=C.SKN)
    # Shoulder highlight
    d.ellipse([cx-280,shoulder_y-5,cx-100,shoulder_y+40], fill=C.SKN_H)
    d.ellipse([cx+100,shoulder_y-5,cx+280,shoulder_y+40], fill=C.SKN_H)

    # ── FACE — oval shape ──
    # Main face oval (longer than wide = oval)
    d.ellipse([cx-190, head_top+30, cx+190, chin+30], fill=C.SKN_L)
    # Jaw — soft oval tapering
    d.polygon([(cx-175,chin-50),(cx-90,chin+10),(cx,chin+20),
               (cx+90,chin+10),(cx+175,chin-50)], fill=C.SKN)
    # Cheek shadow
    d.ellipse([cx-175,chin-60,cx-70,chin+5], fill=C.SKN_M)
    d.ellipse([cx+70,chin-60,cx+175,chin+5], fill=C.SKN_M)
    # Cheek blush (subtle, sun-kissed)
    d.ellipse([cx-155,head_cy+10,cx-60,head_cy+65], fill=C.BLUSH)
    d.ellipse([cx+60,head_cy+10,cx+155,head_cy+65], fill=C.BLUSH)

    # Freckles — scattered on cheeks and nose bridge (PROMINENT)
    random.seed(42)
    for _ in range(60):
        fx = cx + random.randint(-120, 120)
        fy = head_cy + random.randint(-15, 75)
        # Only place on cheek/nose area
        if abs(fx - cx) > 35 or fy > head_cy + 60:
            if random.random() > 0.25:
                d.ellipse([fx-6,fy-4,fx+6,fy+4], fill=C.FRECK)
                # Subtle highlight around freckle
                d.ellipse([fx-3,fy-2,fx+3,fy+2], fill=(165,128,88))

    # ── HAIR BANGS — side part, wavy ──
    # Side part from left
    d.polygon([(cx-190,head_top+20),(cx-150,head_top),(cx-40,head_top+15),
               (cx+40,head_top+5),(cx+120,head_top+10),(cx+190,head_top+20),
               (cx+185,head_top+180),(cx+100,160),(cx,175),
               (cx-80,155),(cx-175,170)], fill=C.HBRN)
    # Left side hair framing face — wavy
    d.polygon([(cx-190,head_top+20),(cx-220,head_top+50),(cx-235,chin+80),
               (cx-205,chin+40),(cx-185,head_top+100)], fill=C.HBRN)
    # Right side — tucked behind ear, showing more face
    d.polygon([(cx+190,head_top+20),(cx+215,head_top+50),(cx+225,chin+30),
               (cx+200,chin),(cx+185,head_top+100)], fill=C.HBRN)

    # Hair highlight streaks on bangs
    d.arc([cx-120,head_top+10,cx+20,head_top+80], 220, 330, fill=C.HHIL, width=4)
    d.arc([cx+40,head_top+5,cx+160,head_top+70], 220, 330, fill=C.HHIL2, width=3)

    # ── EARS (partially visible) ──
    for ex in [cx-185, cx+185]:
        d.ellipse([ex-15,head_cy-20,ex+15,head_cy+30], fill=C.SKN)
        d.ellipse([ex-6,head_cy-10,ex+6,head_cy+18], fill=C.SKN_M)

    # ── EYES — almond shape, brown/hazel ──
    eye_cy = head_cy - 5
    eye_sep = 88  # distance from center to each eye
    for ex in [cx-eye_sep, cx+eye_sep]:
        # Eye socket shadow
        d.ellipse([ex-48,eye_cy-16,ex+48,eye_cy+22], fill=C.SKN_D)
        # Eye white — slightly almond (wider at outer corner)
        d.ellipse([ex-38,eye_cy-10,ex+42,eye_cy+16], fill=C.EW)
        # Iris — warm brown gradient
        grad_ell(d, [ex-18,eye_cy-5,ex+18,eye_cy+12], C.EIR, C.EIR2, steps=8)
        # Golden highlight in iris
        d.ellipse([ex-6,eye_cy+2,ex+6,eye_cy+9], fill=C.EIR_H)
        # Pupil
        d.ellipse([ex-7,eye_cy+1,ex+7,eye_cy+10], fill=C.EPUP)
        # Main highlight
        d.ellipse([ex-4,eye_cy-2,ex+3,eye_cy+4], fill=C.EHIL)
        # Secondary
        d.ellipse([ex+5,eye_cy+4,ex+12,eye_cy+9], fill=C.EHIL2)
        # Upper eyelid — thicker at outer corner (almond)
        draw_bezier(d, (ex-40,eye_cy-4),(ex,eye_cy-16),(ex+44,eye_cy-2), fill=C.BROW, width=5)
        # Lower eyelid — subtle
        d.arc([ex-34,eye_cy-6,ex+38,eye_cy+16], 10, 170, fill=C.SKN_D, width=2)
        # Eyelid crease
        d.arc([ex-36,eye_cy-26,ex+36,eye_cy+4], 200, 340, fill=C.SKN_M, width=2)
        # Lashes — upper
        for angle in [195,203,211,219,227,330,338,346]:
            rad=math.radians(angle)
            lx1=ex+int(40*math.cos(rad)); ly1=eye_cy+int(12*math.sin(rad))
            lx2=ex+int((40+12)*math.cos(rad)); ly2=eye_cy+int((12+10)*math.sin(rad))
            d.line([(lx1,ly1),(lx2,ly2)], fill=C.BROW, width=2)

    # ── EYEBROWS — arched, medium thickness ──
    for bx in [cx-eye_sep, cx+eye_sep]:
        draw_bezier(d, (bx-42,eye_cy-38),(bx,eye_cy-52),(bx+42,eye_cy-38),
                    fill=C.BROW, width=5)
        # Brow texture
        for i in range(6):
            t=i/6
            mx=bx-35+int(70*t)
            my=eye_cy-42-int(8*math.sin(t*math.pi))
            d.line([(mx,my),(mx+5,my-2)], fill=C.BROW, width=1)

    # ── NOSE — moderate bridge, rounded tip ──
    nose_top = eye_cy + 18
    nose_tip = chin - 85
    # Bridge — subtle highlight
    d.line([(cx-3,nose_top),(cx-2,nose_tip-8)], fill=C.NHI, width=4)
    d.line([(cx+3,nose_top),(cx+2,nose_tip-8)], fill=C.NHI, width=4)
    # Tip — slightly rounded
    d.ellipse([cx-16,nose_tip-10,cx+16,nose_tip+6], fill=C.SKN)
    # Nostrils — soft
    d.ellipse([cx-18,nose_tip-2,cx-6,nose_tip+8], fill=C.NSHAD)
    d.ellipse([cx+6,nose_tip-2,cx+18,nose_tip+8], fill=C.NSHAD)
    # Shadow under tip
    d.arc([cx-20,nose_tip+2,cx+20,nose_tip+20], 10, 170, fill=C.SKN_D, width=2)
    # Side shadows
    d.line([(cx-14,nose_top+15),(cx-18,nose_tip-5)], fill=C.SKN_D, width=2)
    d.line([(cx+14,nose_top+15),(cx+18,nose_tip-5)], fill=C.SKN_D, width=2)

    # ── LIPS — cupid's bow upper, fuller lower, coral color ──
    mouth_y = nose_tip + 48
    # Upper lip — cupid's bow
    d.polygon([(cx-38,mouth_y-3),(cx-12,mouth_y-10),(cx,mouth_y-6),
               (cx+12,mouth_y-10),(cx+38,mouth_y-3),(cx,mouth_y+2)], fill=C.LIP)
    # Lower lip — fuller
    d.ellipse([cx-32,mouth_y,cx+32,mouth_y+18], fill=C.LIPL)
    # Lip highlight
    d.ellipse([cx-12,mouth_y+3,cx+12,mouth_y+10], fill=C.LIPHL)
    # Lip line
    d.line([(cx-36,mouth_y-1),(cx+36,mouth_y-1)], fill=C.LIPD, width=1)
    # Shadow under lower lip
    d.arc([cx-25,mouth_y+15,cx+25,mouth_y+28], 10, 170, fill=C.SKN_D, width=2)

    # ── BLACK STRAPLESS TOP — starts at bust, completely bare above ──
    # No fabric at shoulders/neck at all
    # Scoop neckline — deep curve from armpit to armpit
    d.polygon([(cx-240,bust_y-10),(cx-160,bust_y+30),(cx,bust_y+40),
               (cx+160,bust_y+30),(cx+240,bust_y-10),
               (cx+230,bust_y+50),(cx-230,bust_y+50)], fill=C.TOP)
    # Skin above the top (neck to bust = all skin, no straps)
    d.polygon([(cx-240,bust_y-20),(cx,bust_y-45),(cx+240,bust_y-20),
               (cx+240,bust_y+10),(cx,bust_y+30),(cx-240,bust_y+10)], fill=C.SKN)
    # Bust shaping
    d.ellipse([cx-240,bust_y-10,cx-60,bust_y+50], fill=C.TOP_L)
    d.ellipse([cx+60,bust_y-10,cx+240,bust_y+50], fill=C.TOP_L)
    # Bust highlight
    d.ellipse([cx-180,bust_y-5,cx-100,bust_y+30], fill=C.TOP_H)

    # ── WAIST + HIPS ──
    d.polygon([(cx-240,bust_y+30),(cx+240,bust_y+30),
               (cx+140,waist_y),(cx-140,waist_y)], fill=C.TOP)
    d.polygon([(cx-140,waist_y-5),(cx+140,waist_y-5),
               (cx+280,hip_y),(cx-280,hip_y)], fill=C.TOP)

    # ── BLUE JEANS (extrapolated lower body) ──
    d.polygon([(cx-280,hip_y-5),(cx+280,hip_y-5),
               (cx+260,hip_y+100),(cx-260,hip_y+100)], fill=C.JNS)
    # Jeans fade/highlight
    d.polygon([(cx-200,hip_y+20),(cx-80,hip_y+20),
               (cx-90,hip_y+90),(cx-210,hip_y+90)], fill=C.JNS_L)

    # Legs
    d.polygon([(cx-260,hip_y+90),(cx-20,hip_y+90),
               (cx-50,knee_y),(cx-200,knee_y)], fill=C.JNS)
    d.polygon([(cx+20,hip_y+90),(cx+260,hip_y+90),
               (cx+200,knee_y),(cx+50,knee_y)], fill=C.JNS)
    # Lower legs
    d.polygon([(cx-200,knee_y-10),(cx-50,knee_y-10),
               (cx-60,feet_y),(cx-170,feet_y)], fill=C.JNS)
    d.polygon([(cx+50,knee_y-10),(cx+200,knee_y-10),
               (cx+170,feet_y),(cx+60,feet_y)], fill=C.JNS)
    # Jean highlights
    d.line([(cx-140,knee_y+20),(cx-130,feet_y-20)], fill=C.JNS_H, width=3)
    d.line([(cx+140,knee_y+20),(cx+130,feet_y-20)], fill=C.JNS_H, width=3)

    # ── ARMS (skin visible above elbow, below elbow over jeans) ──
    # Left arm
    arm_l = [(cx-270,shoulder_y+10),(cx-330,shoulder_y+100),
             (cx-350,bust_y+60),(cx-330,waist_y+20),(cx-310,waist_y+140)]
    for i in range(len(arm_l)-1):
        x1,y1=arm_l[i]; x2,y2=arm_l[i+1]
        w=max(28,50-i*6)
        d.polygon([(x1-w,y1),(x1+w,y1),(x2+w,y2),(x2-w,y2)], fill=C.SKN)
    # Hand
    hx,hy=cx-310,waist_y+145
    d.ellipse([hx-20,hy-8,hx+20,hy+32], fill=C.SKN)
    for fi in range(4):
        d.ellipse([hx-12+fi*8,hy+28,hx-6+fi*8,hy+48], fill=C.SKN)

    # Right arm
    arm_r = [(cx+270,shoulder_y+10),(cx+330,shoulder_y+100),
             (cx+350,bust_y+60),(cx+330,waist_y+20),(cx+310,waist_y+140)]
    for i in range(len(arm_r)-1):
        x1,y1=arm_r[i]; x2,y2=arm_r[i+1]
        w=max(28,50-i*6)
        d.polygon([(x1-w,y1),(x1+w,y1),(x2+w,y2),(x2-w,y2)], fill=C.SKN)
    hx2=cx+310
    d.ellipse([hx2-20,hy-8,hx2+20,hy+32], fill=C.SKN)
    for fi in range(4):
        d.ellipse([hx2-12+fi*8,hy+28,hx2-6+fi*8,hy+48], fill=C.SKN)

    # ── GOLD NECKLACE ──
    # Chain — V-shape
    draw_bezier(d, (cx-80,collarbone_y+5),(cx-20,collarbone_y+45),(cx,collarbone_y+55),
                fill=C.GOLD, width=2)
    draw_bezier(d, (cx+80,collarbone_y+5),(cx+20,collarbone_y+45),(cx,collarbone_y+55),
                fill=C.GOLD, width=2)
    # Pendant — small heart or circle
    d.ellipse([cx-8,collarbone_y+52,cx+8,collarbone_y+68], fill=C.GOLD)
    d.ellipse([cx-5,collarbone_y+54,cx+5,collarbone_y+64], fill=C.GOLD_H)

    # ── FEET ──
    d.ellipse([cx-160,feet_y-20,cx-60,feet_y+15], fill=(50,40,35))
    d.ellipse([cx+60,feet_y-20,cx+160,feet_y+15], fill=(50,40,35))

    return img


# ============================================================
# ASCII CONVERSION
# ============================================================
def to_ascii(source, cols, rows, cell_px, blur=1.5):
    blurred = source.filter(ImageFilter.GaussianBlur(radius=blur))
    pixels = blurred.load()
    sw,sh = blurred.size
    out = Image.new("RGB", (cols*cell_px, rows*cell_px), C.BG)
    draw = ImageDraw.Draw(out)
    font = fnt(MONO, cell_px)
    cw,ch = sw/cols, sh/rows
    for gy in range(rows):
        for gx in range(cols):
            sx=min(int(gx*cw+cw/2),sw-1)
            sy=min(int(gy*ch+ch/2),sh-1)
            r,g,b=pixels[sx,sy]
            if r<20 and g<20 and b<25: continue
            draw.text((gx*cell_px,gy*cell_px), BLOCK, fill=(r,g,b), font=font)
    return out


# ============================================================
# MAIN
# ============================================================
def main():
    print("💕 Drawing Linh — realistic portrait from reference photo...")
    vec = draw_linh()
    vec.save(os.path.join(OUTPUT, "vector.png"))
    print(f"  Vector: {vec.size}")

    # High detail: 500x700 grid, 2px cells
    print("  Converting to ASCII (500x700, 2px cells, blur=1.2)...")
    ascii_img = to_ascii(vec, 500, 700, 2, blur=1.2)
    ascii_img.save(os.path.join(OUTPUT, "linh_ascii.png"))
    print(f"  ASCII: {ascii_img.size}")

    # Also save a half-body crop (upper half) for comparison
    half = to_ascii(vec, 500, 350, 3, blur=1.2)
    half.save(os.path.join(OUTPUT, "linh_half.png"))
    print(f"  Half body: {half.size}")

    print(f"\n✅ Saved to {OUTPUT}/")
    print(f"  vector.png — raw vector source")
    print(f"  linh_ascii.png — full body ASCII")
    print(f"  linh_half.png — half body crop")

if __name__ == "__main__":
    main()
