#!/usr/bin/env python3
"""
ASCII Love Story v4: Cartoon Portrait Quality
Vector 2000x2000 → Gaussian blur → 300x400 ASCII grid (120K cells)
Smooth gradients, detailed face, anime/cartoon style
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, subprocess, asyncio, edge_tts, math

OUTPUT = "/Users/hung/code/ai/shorts/output/ascii_love_v4"
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

# Colors
SKN  = (242, 210, 180); SKN2 = (225, 188, 158); SKN3 = (210, 170, 140)
HBK  = (28, 22, 32);   HSH = (58, 48, 68);     HHI = (80, 65, 90)
LIP  = (198, 78, 78);   LIPL = (218, 105, 105); LIPD = (175, 60, 60)
EW   = (242, 242, 248); EIR = (60, 115, 180);   EPUP = (12, 10, 18)
ELSH = (18, 14, 24);    BLUSH = (232, 170, 158); BROW = (32, 26, 36)
EHIL = (140, 175, 220)  # eye highlight blue

DP   = (218, 108, 155); DL = (238, 160, 190); DD = (188, 82, 128)
DHL  = (248, 190, 210); DSH = (175, 72, 118)

SD   = (18, 18, 36);    SL = (42, 42, 65);    SHL = (62, 62, 88)
SHT  = (232, 232, 238); TIE = (172, 38, 38);  TIEL = (202, 62, 62)
BLTG = (205, 180, 52);  SHO = (32, 28, 40)

BG = (8, 8, 14); PG = (255, 152, 182); GD = (255, 218, 0); WH = (255, 255, 255); DM = (95, 95, 115)

# ============================================================
# HELPER: Draw smooth filled shape with gradient
# ============================================================
def draw_gradient_ellipse(d, bbox, color_center, color_edge, steps=20):
    """Draw an ellipse with radial gradient."""
    x0, y0, x1, y1 = bbox
    cx, cy = (x0+x1)/2, (y0+y1)/2
    rx, ry = (x1-x0)/2, (y1-y0)/2
    for i in range(steps, 0, -1):
        t = i / steps
        r = int(color_center[0]*(1-t) + color_edge[0]*t)
        g = int(color_center[1]*(1-t) + color_edge[1]*t)
        b = int(color_center[2]*(1-t) + color_edge[2]*t)
        d.ellipse([cx-rx*t, cy-ry*t, cx+rx*t, cy+ry*t], fill=(r,g,b))

def draw_gradient_rect(d, bbox, c1, c2, direction='v'):
    x0, y0, x1, y1 = bbox
    if direction == 'v':
        for y in range(y0, y1):
            t = (y - y0) / max(1, y1 - y0)
            r = int(c1[0]*(1-t) + c2[0]*t)
            g = int(c1[1]*(1-t) + c2[1]*t)
            b = int(c1[2]*(1-t) + c2[2]*t)
            d.line([(x0, y), (x1, y)], fill=(r,g,b))

# ============================================================
# WOMAN — Detailed cartoon/anime portrait (2000x2000)
# ============================================================
def draw_woman():
    sz = 2000
    img = Image.new("RGB", (sz, sz), BG)
    d = ImageDraw.Draw(img)
    cx, cy_base = sz//2, sz//2

    # ── Hair behind ──
    d.ellipse([cx-370, 200, cx+370, 840], fill=HBK)
    # Long flowing sides
    d.polygon([(cx-355,460),(cx-420,650),(cx-440,950),(cx-400,1180),
               (cx-340,1280),(cx-300,1100),(cx-310,800),(cx-330,560)], fill=HBK)
    d.polygon([(cx+355,460),(cx+420,650),(cx+440,950),(cx+400,1180),
               (cx+340,1280),(cx+300,1100),(cx+310,800),(cx+330,560)], fill=HBK)
    # Hair shine streak
    d.arc([cx-200,230,cx+200,580], 200, 340, fill=HSH, width=6)
    d.arc([cx-150,250,cx+150,550], 210, 330, fill=HHI, width=3)

    # ── Neck + shoulders ──
    d.polygon([(cx-90,730),(cx+90,730),(cx+100,880),(cx-100,880)], fill=SKN)
    d.polygon([(cx-80,730),(cx+80,730),(cx+70,780),(cx-70,780)], fill=SKN2)
    # Shoulders/dress top
    d.polygon([(cx-400,870),(cx+400,870),(cx+360,980),(cx-360,980)], fill=DP)

    # ── Face ──
    d.ellipse([cx-310,340,cx+310,820], fill=SKN)
    # Jaw refinement
    d.polygon([(cx-280,610),(cx-200,770),(cx,820),(cx+200,770),(cx+280,610)], fill=SKN)
    # Cheek blush
    d.ellipse([cx-270,620,cx-110,730], fill=BLUSH)
    d.ellipse([cx+110,620,cx+270,730], fill=BLUSH)

    # ── Hair bangs ──
    d.polygon([(cx-310,380),(cx-260,330),(cx-100,370),(cx,355),(cx+100,370),
               (cx+260,330),(cx+310,380),(cx+290,500),(cx+160,470),(cx,490),
               (cx-160,470),(cx-290,500)], fill=HBK)
    d.polygon([(cx-310,380),(cx-350,420),(cx-360,580),(cx-340,520),(cx-310,460)], fill=HBK)
    d.polygon([(cx+310,380),(cx+350,420),(cx+360,580),(cx+340,520),(cx+310,460)], fill=HBK)

    # ── Eyes — large anime style ──
    for ex in [cx-150, cx+150]:
        # Eye white
        d.ellipse([ex-80,550,ex+80,650], fill=EW)
        # Iris — gradient
        draw_gradient_ellipse(d, [ex-44,556,ex+44,644], EIR, (30,60,120), steps=12)
        # Pupil
        d.ellipse([ex-18,576,ex+18,624], fill=EPUP)
        # Highlight — big
        d.ellipse([ex-12,565,ex+8,585], fill=(255,255,255))
        # Small highlight
        d.ellipse([ex+10,590,ex+22,602], fill=EHIL)
        # Upper lash — thick
        d.arc([ex-82,546,ex+82,654], 190, 350, fill=ELSH, width=8)
        # Lower lash
        d.arc([ex-70,555,ex+70,650], 10, 170, fill=ELSH, width=3)
        # Lash extensions
        d.polygon([(ex-82,570),(ex-95,558),(ex-85,565)], fill=ELSH)
        d.polygon([(ex+82,570),(ex+95,558),(ex+85,565)], fill=ELSH)

    # ── Eyebrows ──
    d.arc([cx-230,490,cx-70,550], 200, 340, fill=BROW, width=6)
    d.arc([cx+70,490,cx+230,550], 200, 340, fill=BROW, width=6)

    # ── Nose ──
    d.polygon([(cx-16,660),(cx+16,660),(cx+24,730),(cx-24,730)], fill=SKN2)
    d.arc([cx-30,718,cx+30,748], 0, 180, fill=SKN3, width=3)

    # ── Lips — full detailed ──
    # Upper lip
    d.polygon([(cx-70,770),(cx-30,758),(cx,764),(cx+30,758),(cx+70,770),(cx,784)], fill=LIP)
    # Lower lip — full
    d.ellipse([cx-58,778,cx+58,820], fill=LIPL)
    # Lip highlight
    d.ellipse([cx-20,785,cx+20,800], fill=(235,130,130))

    # ── Dress — S-curve body ──
    # Bust
    d.polygon([(cx-380,960),(cx+380,960),(cx+420,1140),(cx-420,1140)], fill=DP)
    d.ellipse([cx-420,1000,cx-100,1160], fill=DL)
    d.ellipse([cx+100,1000,cx+420,1160], fill=DL)
    # Bust shadow
    d.ellipse([cx-350,1060,cx-150,1150], fill=DD)
    d.ellipse([cx+150,1060,cx+350,1150], fill=DD)

    # Waist — NARROW
    d.polygon([(cx-420,1130),(cx+420,1130),(cx+200,1340),(cx-200,1340)], fill=DP)
    d.polygon([(cx-260,1240),(cx+260,1240),(cx+220,1300),(cx-220,1300)], fill=DD)

    # Hips — WIDE
    d.polygon([(cx-200,1330),(cx+200,1330),(cx+440,1500),(cx-440,1500)], fill=DP)
    d.ellipse([cx-460,1350,cx-60,1520], fill=DL)
    d.ellipse([cx+60,1350,cx+460,1520], fill=DL)

    # Skirt
    d.polygon([(cx-440,1490),(cx+440,1490),(cx+500,1850),(cx-500,1850)], fill=DP)
    d.polygon([(cx-360,1510),(cx-180,1510),(cx-230,1820),(cx-400,1820)], fill=DD)
    d.polygon([(cx+180,1510),(cx+360,1510),(cx+400,1820),(cx+230,1820)], fill=DD)
    d.polygon([(cx-60,1500),(cx+60,1500),(cx+90,1830),(cx-90,1830)], fill=DHL)

    # Arms
    d.polygon([(cx-395,890),(cx-460,910),(cx-500,1180),(cx-460,1200),(cx-400,1000)], fill=SKN)
    d.polygon([(cx+395,890),(cx+460,910),(cx+500,1180),(cx+460,1200),(cx+400,1000)], fill=SKN)
    d.ellipse([cx-520,1160,cx-440,1250], fill=SKN)
    d.ellipse([cx+440,1160,cx+520,1250], fill=SKN)

    # Shoes
    d.ellipse([cx-240,1830,cx-80,1890], fill=SHO)
    d.ellipse([cx+80,1830,cx+240,1890], fill=SHO)

    return img


# ============================================================
# MAN — Detailed cartoon portrait (2000x2000)
# ============================================================
def draw_man():
    sz = 2000
    img = Image.new("RGB", (sz, sz), BG)
    d = ImageDraw.Draw(img)
    cx = sz//2

    # Suit shoulders behind
    d.polygon([(cx-460,880),(cx+460,880),(cx+440,1000),(cx-440,1000)], fill=SD)

    # Neck
    d.polygon([(cx-110,730),(cx+110,730),(cx+120,880),(cx-120,880)], fill=SKN)
    d.polygon([(cx-90,730),(cx+90,730),(cx+80,790),(cx-80,790)], fill=SKN2)

    # Face — square jaw
    d.ellipse([cx-320,340,cx+320,840], fill=SKN)
    d.polygon([(cx-300,610),(cx-240,740),(cx-120,830),(cx,850),
               (cx+120,830),(cx+240,740),(cx+300,610)], fill=SKN)
    d.polygon([(cx-240,740),(cx-120,830),(cx,850),(cx+120,830),(cx+240,740),
               (cx+160,800),(cx,835),(cx-160,800)], fill=SKN2)

    # Hair — short, neat
    d.ellipse([cx-330,260,cx+330,620], fill=HBK)
    d.polygon([(cx-320,380),(cx-260,270),(cx-100,255),(cx,248),(cx+100,255),
               (cx+260,270),(cx+320,380),(cx+310,450),(cx+160,420),(cx,435),
               (cx-160,420),(cx-310,450)], fill=HBK)
    d.arc([cx-240,270,cx+240,460], 200, 340, fill=HSH, width=5)
    d.polygon([(cx-320,380),(cx-360,420),(cx-370,600),(cx-345,540),(cx-320,460)], fill=HBK)
    d.polygon([(cx+320,380),(cx+360,420),(cx+370,600),(cx+345,540),(cx+320,460)], fill=HBK)

    # Eyes — sharp, confident
    for ex in [cx-160, cx+160]:
        d.ellipse([ex-76,556,ex+76,636], fill=EW)
        # Iris — dark green gradient
        draw_gradient_ellipse(d, [ex-40,560,ex+40,632], (50,85,55), (25,45,30), steps=10)
        d.ellipse([ex-16,576,ex+16,616], fill=EPUP)
        d.ellipse([ex-8,566,ex+8,580], fill=(255,255,255))
        d.ellipse([ex+8,588,ex+18,598], fill=(180,200,180))
        d.arc([ex-78,552,ex+78,640], 194, 346, fill=ELSH, width=7)
        d.arc([ex-62,558,ex+62,636], 12, 168, fill=ELSH, width=3)

    # Thick brows
    d.polygon([(cx-240,510),(cx-80,502),(cx-78,524),(cx-238,532)], fill=BROW)
    d.polygon([(cx+80,502),(cx+240,510),(cx+238,532),(cx+78,524)], fill=BROW)

    # Nose
    d.polygon([(cx-20,650),(cx+20,650),(cx+30,740),(cx-30,740)], fill=SKN2)
    d.arc([cx-36,728,cx+36,758], 0, 180, fill=SKN3, width=4)

    # Mouth — slight smile
    d.arc([cx-70,778,cx+70,810], 10, 170, fill=LIP, width=5)
    d.polygon([(cx-50,792),(cx+50,792),(cx+40,804),(cx-40,804)], fill=LIPD)

    # Shirt collar
    d.polygon([(cx-110,870),(cx-60,860),(cx,920),(cx+60,860),(cx+110,870),
               (cx+80,980),(cx,1020),(cx-80,980)], fill=SHT)
    d.polygon([(cx-110,870),(cx-160,895),(cx-120,940),(cx-80,900)], fill=SHT)
    d.polygon([(cx+110,870),(cx+160,895),(cx+120,940),(cx+80,900)], fill=SHT)

    # Tie
    d.polygon([(cx-30,920),(cx+30,920),(cx+20,1380),(cx-20,1380)], fill=TIE)
    d.polygon([(cx-30,920),(cx+30,920),(cx+16,960),(cx-16,960)], fill=TIEL)
    d.polygon([(cx-24,896),(cx+24,896),(cx+16,928),(cx-16,928)], fill=TIEL)

    # Suit jacket
    d.polygon([(cx-460,880),(cx-110,870),(cx-80,980),(cx-100,1380),(cx-480,1400)], fill=SD)
    d.polygon([(cx+460,880),(cx+110,870),(cx+80,980),(cx+100,1380),(cx+480,1400)], fill=SD)
    d.polygon([(cx-110,870),(cx-160,895),(cx-140,1080),(cx-100,1000)], fill=SL)
    d.polygon([(cx+110,870),(cx+160,895),(cx+140,1080),(cx+100,1000)], fill=SL)

    # Belt
    d.rectangle([cx-260,1380,cx+260,1430], fill=SD)
    d.rectangle([cx-40,1380,cx+40,1430], fill=BLTG)

    # Trousers
    d.polygon([(cx-260,1425),(cx-20,1425),(cx-60,1880),(cx-220,1880)], fill=SD)
    d.polygon([(cx+20,1425),(cx+260,1425),(cx+220,1880),(cx+60,1880)], fill=SD)
    d.line([(cx-140,1435),(cx-140,1870)], fill=SL, width=3)
    d.line([(cx+140,1435),(cx+140,1870)], fill=SL, width=3)

    # Shoes
    d.ellipse([cx-240,1860,cx-60,1930], fill=SHO)
    d.ellipse([cx+60,1860,cx+240,1930], fill=SHO)

    # Arms
    d.polygon([(cx-450,890),(cx-520,910),(cx-540,1340),(cx-490,1360),(cx-430,1080)], fill=SD)
    d.polygon([(cx+450,890),(cx+520,910),(cx+540,1340),(cx+490,1360),(cx+430,1080)], fill=SD)
    d.ellipse([cx-560,1320,cx-470,1420], fill=SKN)
    d.ellipse([cx+470,1320,cx+560,1420], fill=SKN)

    return img


# ============================================================
# VECTOR → ASCII with anti-aliasing
# ============================================================
def vector_to_ascii(source, cols, rows, cell_px, blur_radius=1.5):
    """Convert vector to ASCII with Gaussian blur for smooth edges."""
    # Anti-alias: blur source before sampling
    blurred = source.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    pixels = blurred.load()
    sw, sh = blurred.size
    out_w, out_h = cols * cell_px, rows * cell_px
    out = Image.new("RGB", (out_w, out_h), BG)
    draw = ImageDraw.Draw(out)
    font = fnt(MONO, cell_px)
    cw, ch = sw / cols, sh / rows

    for gy in range(rows):
        for gx in range(cols):
            sx = min(int(gx * cw + cw / 2), sw - 1)
            sy = min(int(gy * ch + ch / 2), sh - 1)
            r, g, b = pixels[sx, sy]
            if r < 20 and g < 20 and b < 25:
                continue
            draw.text((gx * cell_px, gy * cell_px), BLOCK, fill=(r, g, b), font=font)
    return out


# ============================================================
# SCENES
# ============================================================
SCENES = [
    {"title":"CHƯƠNG 1","char":"woman","cap":"Ngày đó, Linh là cô gái đẹp nhất thành phố.",
     "tts":"Ngày đó, Linh là cô gái đẹp nhất thành phố. Vẻ đẹp không chỉ ở khuôn mặt, mà còn ở trái tim nhân hậu.","bg":"hearts"},
    {"title":"CHƯƠNG 2","char":"man","cap":"Còn Dũng là tổng tài giàu nhất thành phố.",
     "tts":"Còn Dũng là tổng tài giàu nhất thành phố. Anh có tất cả, trừ một điều: tình yêu thực sự.","bg":"sparkle"},
    {"title":"CHƯƠNG 3","tcolor":PG,"char":"both","cap":"Họ gặp nhau tại bữa tiệc đêm đó...",
     "tts":"Họ gặp nhau tại bữa tiệc đêm đó. Ánh mắt lần đầu chạm nhau, cả thế giới như dừng lại.","bg":"sparkle"},
    {"title":"CHƯƠNG 4","tcolor":PG,"char":"both","cap":"Không tiền bạc, không địa vị. Chỉ có hai trái tim.",
     "tts":"Không tiền bạc, không địa vị. Chỉ có hai trái tim rung động. Tình yêu không cần vật chất.","bg":"hearts"},
    {"title":"CHƯƠNG 5","tcolor":GD,"char":"man","cap":"Dũng quyết định bỏ lại tất cả.",
     "tts":"Dũng quyết định bỏ lại tất cả. Đế chế tiền bạc không bằng nụ cười của cô ấy.","bg":"sparkle"},
    {"title":"CHƯƠNG 6","tcolor":DP,"char":"woman","cap":"Linh chờ đợi một tình yêu chân thật.",
     "tts":"Linh chờ đợi một tình yêu chân thật. Không phải vì anh giàu, mà vì anh hiểu trái tim cô.","bg":"hearts"},
    {"title":"CHƯƠNG 7","tcolor":PG,"char":"both","cap":"Hai đường cong gặp nhau tại đỉnh.",
     "tts":"Hai đường cong cuộc đời gặp nhau tại đỉnh. Từ nay, không còn đơn độc.","bg":"hearts"},
    {"title":"PHẦN KẾT","tcolor":GD,"char":"both","cap":"TÌNH YÊU KHÔNG CÓ GIÁ.",
     "tts":"Tình yêu không có giá. Nhưng không có nó, mọi thứ đều có giá. Từ hai, thành một. Không gì là không thể.","bg":"hearts"},
]

# ============================================================
# EFFECTS
# ============================================================
def fx_hearts(d, t, a):
    for i in range(18):
        x = (i*79 + int(t*22)) % W
        y = (i*127 + int(t*15)) % H
        s = 12 + (i%4)*5
        v = int(50*a*(0.5+0.5*math.sin(t*2+i)))
        if v > 0: d.text((x,y),"♥",fill=PG+(v,),font=fnt(MONO,s))

def fx_sparkle(d, t, a):
    for i in range(30):
        x = (i*49 + int(t*10)) % W
        y = (i*89 + int(t*7)) % H
        p = math.sin(t*3+i*0.7)
        if p > 0.3:
            v = int(75*a*p)
            s = 2 + int(5*p)
            d.ellipse([x-s,y-s,x+s,y+s], fill=GD+(v,))


# ============================================================
# PRE-RENDER
# ============================================================
CHARS = {}

def prerender():
    print("  Drawing woman 2000x2000...")
    wv = draw_woman()
    wv.save(os.path.join(OUTPUT,"vec_woman.png"))
    print("  Drawing man 2000x2000...")
    mv = draw_man()
    mv.save(os.path.join(OUTPUT,"vec_man.png"))

    # Single: 300 cols x 400 rows, 3px cells → 900x1200
    print("  Converting woman → ASCII 300x400 grid, 3px cells, blur=1.5...")
    CHARS["w"] = vector_to_ascii(wv, 300, 400, 3, blur_radius=1.5)
    print("  Converting man → ASCII 300x400 grid, 3px cells, blur=1.5...")
    CHARS["m"] = vector_to_ascii(mv, 300, 400, 3, blur_radius=1.5)

    # Both: 160x220 grid, 4px → 640x880
    print("  Converting both → ASCII 160x220 grid, 4px cells...")
    CHARS["ws"] = vector_to_ascii(wv, 160, 220, 4, blur_radius=1.0)
    CHARS["ms"] = vector_to_ascii(mv, 160, 220, 4, blur_radius=1.0)

    for k, v in CHARS.items():
        v.save(os.path.join(OUTPUT, f"ascii_{k}.png"))
        print(f"    {k}: {v.size}")


# ============================================================
# RENDER FRAME
# ============================================================
def render_frame(si, sc, t, st, fn, tf, sd):
    c = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(c)

    a = 1.0
    if st < 0.6: a = st/0.6
    elif st > sd-0.6: a = (sd-st)/0.6

    if sc.get("bg")=="hearts": fx_hearts(d, t, a*0.5)
    elif sc.get("bg")=="sparkle": fx_sparkle(d, t, a*0.5)

    # Title
    tc = sc.get("tcolor", DM)
    tf2 = fnt(VI_BOLD, 38)
    tb = d.textbbox((0,0), sc["title"], font=tf2)
    d.text(((W-tb[2]+tb[0])//2, 100), sc["title"], font=tf2,
           fill=tuple(int(x*a) for x in tc)+(int(255*a),))

    # Character
    ct = sc["char"]
    if ct == "woman":
        img = CHARS["w"]
        c.paste(img, ((W-img.width)//2, (H-img.height)//2-80))
    elif ct == "man":
        img = CHARS["m"]
        c.paste(img, ((W-img.width)//2, (H-img.height)//2-80))
    elif ct == "both":
        ws, ms = CHARS["ws"], CHARS["ms"]
        gap = 20
        tw = ws.width + gap + ms.width
        sx = (W - tw) // 2
        cy = (H - ws.height) // 2 - 40
        c.paste(ws, (sx, cy))
        c.paste(ms, (sx + ws.width + gap, cy))
        nf = fnt(VI_BOLD, 28)
        for nm, cl, ix in [("Linh",DP,sx+ws.width//2),("Dũng",GD,sx+ws.width+gap+ms.width//2)]:
            nb = d.textbbox((0,0), nm, font=nf)
            d.text((ix-(nb[2]-nb[0])//2, cy+ws.height+8), nm, font=nf, fill=cl+(int(255*a),))

    # Caption
    cf = fnt(VI_FONT, 34)
    words = sc["cap"].split()
    lines, line = [], ""
    for w in words:
        test = (line+" "+w).strip()
        if d.textbbox((0,0), test, font=cf)[2] > W-120 and line:
            lines.append(line); line = w
        else: line = test
    if line: lines.append(line)
    cy2 = H - 340
    for i, ln in enumerate(lines):
        lb = d.textbbox((0,0), ln, font=cf)
        d.text(((W-lb[2]+lb[0])//2, cy2+i*48), ln, font=cf,
               fill=WH+(int(255*min(1.0,a*max(0,1-i*0.1))),))

    # Progress
    by = H-100; bx = 100; bw = W-200
    pr = fn/max(1,tf)
    d.rectangle([bx,by,bx+bw,by+6], fill=(30,30,40))
    d.rectangle([bx,by,bx+int(bw*pr),by+6], fill=PG+(180,))
    dy = by+28; ds=36; dsx=W//2-(len(SCENES)*ds)//2
    for si2 in range(len(SCENES)):
        dx = dsx+si2*ds
        r = 6 if si2==si else 4
        d.ellipse([dx-r,dy-r,dx+r,dy+r], fill=PG if si2==si else (50,50,60))

    return c


# ============================================================
# TTS
# ============================================================
async def gen_tts():
    for i, s in enumerate(SCENES):
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
    print("💕 ASCII LOVE STORY v4: Cartoon Portrait Quality")
    print("   Vector 2000x2000 + blur → 300x400 ASCII grid")
    print("="*60)

    print("\n🎨 Pre-rendering characters (300x400 grid, 120K cells)...")
    prerender()

    print("\n🎙 Generating TTS...")
    asyncio.run(gen_tts())

    print("\n🎵 Audio...")
    ap, dur = concat_audio()
    sdur = dur/len(SCENES); tf = int(dur*FPS)
    print(f"   {dur:.1f}s, {sdur:.1f}s/scene, {tf} frames")

    print("\n🎨 Rendering frames...")
    fn = 0
    for si, sc in enumerate(SCENES):
        sf = int(sdur*FPS)
        print(f"   Scene {si+1}: {sc['title']} ({sf} frames)")
        for fi in range(sf):
            t = fn/FPS; st = fi/FPS
            img = render_frame(si, sc, t, st, fn, tf, sdur)
            img.save(os.path.join(FRAMES_DIR, f"f_{fn:05d}.png"))
            fn += 1
            if fi%(FPS*3)==0: print(f"      {100*fn//tf}%")

    print("\n🎞 Encoding...")
    out = os.path.join(OUTPUT, "tinh_yeu_v4.mp4")
    subprocess.run(["ffmpeg","-y","-framerate",str(FPS),
        "-i",os.path.join(FRAMES_DIR,"f_%05d.png"),"-i",ap,
        "-c:v","libx264","-pix_fmt","yuv420p","-crf","18","-profile:v","high",
        "-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",out],capture_output=True)

    if os.path.exists(out):
        sz = os.path.getsize(out)/(1024*1024)
        print(f"\n✅ DONE: {out}\n   Size: {sz:.1f}MB, {dur:.1f}s")
    else:
        print("\n❌ FAILED")

if __name__ == "__main__":
    main()
