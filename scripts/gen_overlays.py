#!/usr/bin/env python3
"""Generate vector overlay PNGs (icons, badges, flashes, text callouts) with PIL."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/billionaire/overlays")
OUT.mkdir(parents=True, exist_ok=True)


def font(size):
    return ImageFont.truetype(FONT, size)


def centered(d, img, text, fnt, y=None, fill=(255, 255, 255, 255), stroke=0, stroke_fill=None):
    w, h = img.size
    bbox = d.textbbox((0, 0), text, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (w - tw) // 2 - bbox[0]
    yy = y if y is not None else (h - th) // 2 - bbox[1]
    if stroke > 0:
        d.text((x, yy), text, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    else:
        d.text((x, yy), text, font=fnt, fill=fill)


def save(img, name):
    img.save(OUT / f"{name}.png")


# ── ICONS (300x300 transparent) ──

def icon_money():
    s = 300
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([20, 20, s - 20, s - 20], fill=(0, 180, 70, 255), outline=(0, 100, 40, 255), width=6)
    centered(d, img, "$", font(160), fill=(255, 255, 255, 255))
    return img


def icon_warning():
    s = 300
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(s // 2, 20), (s - 20, s - 30), (20, s - 30)], fill=(255, 200, 0, 255),
              outline=(80, 60, 0, 255), width=6)
    centered(d, img, "!", font(150), y=70, fill=(60, 40, 0, 255))
    return img


def icon_target():
    s = 300
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([10, 10, s - 10, s - 10], fill=(220, 50, 50, 255))
    d.ellipse([55, 55, s - 55, s - 55], fill=(255, 255, 255, 255))
    d.ellipse([100, 100, s - 100, s - 100], fill=(220, 50, 50, 255))
    d.ellipse([140, 140, s - 140, s - 140], fill=(255, 255, 255, 255))
    return img


def icon_bolt():
    s = 300
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = [(s * 0.58, 10), (s * 0.18, s * 0.55), (s * 0.42, s * 0.55),
           (s * 0.32, s * 0.9), (s * 0.82, s * 0.38), (s * 0.55, s * 0.38)]
    d.polygon(pts, fill=(255, 220, 0, 255), outline=(120, 90, 0, 255), width=5)
    return img


def icon_crown():
    s = 300
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = [(30, s - 50), (30, 110), (95, 200), (150, 70), (205, 200), (270, 110), (270, s - 50)]
    d.polygon(pts, fill=(255, 200, 0, 255), outline=(120, 90, 0, 255), width=5)
    d.rectangle([30, s - 50, 270, s - 20], fill=(255, 170, 0, 255))
    # gems
    d.ellipse([60, 130, 100, 170], fill=(220, 40, 40, 255))
    d.ellipse([130, 100, 170, 140], fill=(40, 120, 220, 255))
    d.ellipse([200, 130, 240, 170], fill=(40, 200, 80, 255))
    return img


def icon_100():
    s = 300
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([20, 20, s - 20, s - 20], fill=(0, 180, 70, 255), outline=(0, 100, 40, 255), width=6)
    centered(d, img, "100%", font(70), fill=(255, 255, 255, 255))
    return img


def icon_idea():
    s = 300
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([70, 30, 230, 190], fill=(255, 235, 100, 255), outline=(200, 160, 0, 255), width=5)
    d.rectangle([120, 190, 180, 240], fill=(200, 200, 200, 255))
    d.rectangle([110, 240, 190, 270], fill=(150, 150, 150, 255))
    return img


def icon_fire():
    s = 300
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = [(150, 20), (90, 120), (120, 120), (70, 210), (130, 180),
           (120, 260), (230, 150), (170, 150), (210, 60)]
    d.polygon(pts, fill=(255, 90, 0, 255), outline=(180, 50, 0, 255), width=4)
    inner = [(150, 80), (120, 150), (145, 150), (120, 210), (185, 160), (160, 160), (180, 100)]
    d.polygon(inner, fill=(255, 220, 0, 255))
    return img


def icon_chart_up():
    s = 300
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([20, 230, 280, 250], fill=(80, 80, 80, 255))
    d.rectangle([20, 30, 40, 250], fill=(80, 80, 80, 255))
    pts = [(60, 210), (110, 170), (160, 190), (210, 110), (260, 60)]
    d.line(pts, fill=(0, 200, 80, 255), width=12, joint="curve")
    d.polygon([(260, 60), (230, 75), (255, 90)], fill=(0, 200, 80, 255))
    return img


def icon_clock():
    s = 300
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([20, 20, s - 20, s - 20], fill=(255, 255, 255, 255), outline=(40, 40, 40, 255), width=8)
    d.line([(150, 150), (150, 70)], fill=(40, 40, 40, 255), width=8)
    d.line([(150, 150), (210, 150)], fill=(40, 40, 40, 255), width=8)
    return img


# ── BADGES (580x130) ──

def badge(text, bg, name):
    img = Image.new("RGBA", (580, 130), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, 580, 130], radius=35, fill=bg)
    centered(d, img, text, font(56), fill=(255, 255, 255, 255))
    return img


# ── FLASHES (1080x1920) ──

def flash(color, name):
    img = Image.new("RGBA", (1080, 1920), color)
    return img


# ── TEXT CALLOUTS (800x220) ──

def text_callout(text, color, name, fs=110):
    img = Image.new("RGBA", (800, 220), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    centered(d, img, text, font(fs), fill=color, stroke=6, stroke_fill=(0, 0, 0, 255))
    return img


def main():
    icons = {
        "icon_money": icon_money(),
        "icon_warning": icon_warning(),
        "icon_target": icon_target(),
        "icon_bolt": icon_bolt(),
        "icon_crown": icon_crown(),
        "icon_100": icon_100(),
        "icon_idea": icon_idea(),
        "icon_fire": icon_fire(),
        "icon_chart_up": icon_chart_up(),
        "icon_clock": icon_clock(),
    }
    for name, img in icons.items():
        save(img, name)

    badges = {
        "badge_truth": badge("REAL TALK", (220, 30, 30, 240), "badge_truth"),
        "badge_key": badge("KEY INSIGHT", (0, 150, 80, 240), "badge_key"),
        "badge_money": badge("MONEY MOVE", (255, 170, 0, 240), "badge_money"),
        "badge_warning": badge("WARNING", (220, 50, 50, 240), "badge_warning"),
        "badge_protip": badge("PRO TIP", (100, 100, 220, 240), "badge_protip"),
        "badge_fact": badge("FACT CHECK", (40, 160, 80, 240), "badge_fact"),
        "badge_luxury": badge("BILLIONAIRE", (120, 20, 140, 240), "badge_luxury"),
    }
    for name, img in badges.items():
        save(img, name)

    flashes = {
        "flash_yellow": flash((255, 220, 0, 110), "flash_yellow"),
        "flash_red": flash((255, 50, 50, 90), "flash_red"),
        "flash_green": flash((0, 255, 100, 90), "flash_green"),
        "flash_white": flash((255, 255, 255, 130), "flash_white"),
    }
    for name, img in flashes.items():
        save(img, name)

    texts = {
        "text_wow": text_callout("WOW!", (255, 220, 0, 255), "text_wow"),
        "text_fact": text_callout("FACT:", (0, 220, 110, 255), "text_fact"),
        "text_never": text_callout("NEVER", (255, 80, 80, 255), "text_never"),
        "text_truth": text_callout("TRUTH", (255, 180, 0, 255), "text_truth"),
        "text_insane": text_callout("INSANE!", (255, 80, 200, 255), "text_insane"),
        "text_huge": text_callout("HUGE!", (0, 220, 110, 255), "text_huge"),
        "text_wait": text_callout("WAIT...", (255, 150, 0, 255), "text_wait"),
        "text_pause": text_callout("PAUSE", (220, 50, 50, 255), "text_pause"),
    }
    for name, img in texts.items():
        save(img, name)

    print(f"[assets] Generated {len(icons) + len(badges) + len(flashes) + len(texts)} overlays -> {OUT}")
    for p in sorted(OUT.glob("*.png")):
        print(f"  {p.name}")


if __name__ == "__main__":
    main()
