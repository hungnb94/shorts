#!/usr/bin/env python3
"""Build three original 16:9 package-test thumbnails for the Dangote flagship."""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "output/projects/dangote-supply-chain/package-test"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1280, 720
NAVY = "#08111f"
PANEL = "#111f33"
WHITE = "#f7fafc"
MUTED = "#9fb0c6"
CYAN = "#45d6ff"
GREEN = "#5fe199"
RED = "#ff5c5c"
AMBER = "#ffb84d"

FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
FONT_BLACK = Path("/System/Library/Fonts/Supplemental/Arial Black.ttf")


def font(size: int, black: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BLACK if black else FONT_BOLD), size)


def fit(draw: ImageDraw.ImageDraw, text: str, max_width: int, start: int, minimum: int = 36) -> ImageFont.FreeTypeFont:
    size = start
    while size > minimum and draw.textbbox((0, 0), text, font=font(size, True))[2] > max_width:
        size -= 2
    return font(size, True)


def centered(draw: ImageDraw.ImageDraw, y: int, text: str, fill: str, size: int, max_width: int = 1180) -> None:
    f = fit(draw, text, max_width, size)
    draw.text((W // 2, y), text, font=f, fill=fill, anchor="mm", stroke_width=2, stroke_fill="#000000")


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str, width: int = 12) -> None:
    draw.line((start, end), fill=color, width=width)
    x, y = end
    draw.polygon([(x, y), (x - 24, y - 18), (x - 24, y + 18)], fill=color)


def icon_mine(draw: ImageDraw.ImageDraw, cx: int, cy: int, color: str) -> None:
    draw.polygon([(cx - 70, cy + 45), (cx - 20, cy - 55), (cx + 20, cy + 5), (cx + 55, cy - 30), (cx + 85, cy + 45)], fill=color)
    draw.ellipse((cx - 20, cy - 8, cx + 15, cy + 27), fill=NAVY)


def icon_factory(draw: ImageDraw.ImageDraw, cx: int, cy: int, color: str) -> None:
    draw.rectangle((cx - 75, cy - 25, cx + 78, cy + 55), fill=color)
    draw.polygon([(cx - 75, cy - 25), (cx - 15, cy - 75), (cx - 15, cy - 25), (cx + 45, cy - 75), (cx + 45, cy - 25)], fill=color)
    draw.rectangle((cx + 45, cy - 105, cx + 72, cy - 25), fill=color)
    for x in (cx - 48, cx - 5, cx + 38):
        draw.rectangle((x, cy + 8, x + 24, cy + 35), fill=NAVY)


def icon_truck(draw: ImageDraw.ImageDraw, cx: int, cy: int, color: str) -> None:
    draw.rectangle((cx - 85, cy - 35, cx + 30, cy + 35), fill=color)
    draw.polygon([(cx + 30, cy - 18), (cx + 68, cy - 18), (cx + 92, cy + 12), (cx + 92, cy + 35), (cx + 30, cy + 35)], fill=color)
    for x in (cx - 48, cx + 58):
        draw.ellipse((x - 20, cy + 18, x + 20, cy + 58), fill=WHITE)
        draw.ellipse((x - 10, cy + 28, x + 10, cy + 48), fill=NAVY)


def icon_drop(draw: ImageDraw.ImageDraw, cx: int, cy: int, color: str) -> None:
    draw.polygon([(cx, cy - 90), (cx - 62, cy + 5), (cx - 45, cy + 62), (cx, cy + 82), (cx + 45, cy + 62), (cx + 62, cy + 5)], fill=color)


def base() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(image)
    for x in range(0, W, 80):
        draw.line((x, 0, x, H), fill="#0d1b2b", width=1)
    for y in range(0, H, 80):
        draw.line((0, y, W, y), fill="#0d1b2b", width=1)
    draw.rounded_rectangle((32, 26, 1248, 694), radius=34, outline="#243a56", width=3)
    draw.text((62, 58), "MONEY BLINDSPOT", font=font(24), fill=CYAN)
    return image, draw


def package_a() -> Image.Image:
    image, draw = base()
    centered(draw, 160, "HE BUILT EVERY STEP", WHITE, 72)
    xs = [170, 480, 790, 1100]
    colors = [AMBER, CYAN, GREEN, GREEN]
    labels = ["RAW INPUT", "FACTORY", "LOGISTICS", "PRODUCT"]
    icon_mine(draw, xs[0], 395, colors[0])
    icon_factory(draw, xs[1], 395, colors[1])
    icon_truck(draw, xs[2], 395, colors[2])
    icon_drop(draw, xs[3], 395, colors[3])
    for left, right in zip(xs, xs[1:]):
        arrow(draw, (left + 105, 395), (right - 110, 395), WHITE, 9)
    for x, label, color in zip(xs, labels, colors):
        draw.rounded_rectangle((x - 110, 535, x + 110, 590), radius=16, fill=PANEL, outline=color, width=3)
        draw.text((x, 563), label, font=font(22), fill=color, anchor="mm")
    centered(draw, 640, "DEPENDENCY  →  CONTROL", AMBER, 42)
    return image


def package_b() -> Image.Image:
    image, draw = base()
    centered(draw, 150, "BUY THE INPUT — OR BUILD IT?", WHITE, 63)
    draw.rounded_rectangle((80, 230, 585, 585), radius=30, fill="#261522", outline=RED, width=4)
    draw.rounded_rectangle((695, 230, 1200, 585), radius=30, fill="#10271f", outline=GREEN, width=4)
    draw.text((332, 275), "DEPEND ON SUPPLIERS", font=font(30), fill=RED, anchor="mm")
    icon_truck(draw, 330, 405, RED)
    draw.text((332, 530), "PRICE • DELAY • SHORTAGE", font=font(24), fill=WHITE, anchor="mm")
    draw.text((948, 275), "BUILD THE BOTTLENECK", font=font(30), fill=GREEN, anchor="mm")
    icon_factory(draw, 948, 405, GREEN)
    draw.text((948, 530), "CONTROL • CAPITAL • RISK", font=font(24), fill=WHITE, anchor="mm")
    centered(draw, 640, "WHICH SIDE BECOMES THE MOAT?", AMBER, 40)
    return image


def package_c() -> Image.Image:
    image, draw = base()
    centered(draw, 150, "IMPORTS  →  MADE HERE", WHITE, 80)
    draw.rounded_rectangle((75, 250, 530, 570), radius=28, fill="#241a18", outline=AMBER, width=4)
    draw.rounded_rectangle((750, 250, 1205, 570), radius=28, fill="#10271f", outline=GREEN, width=4)
    draw.text((302, 290), "OUTSIDE SUPPLY", font=font(30), fill=AMBER, anchor="mm")
    icon_truck(draw, 302, 410, AMBER)
    draw.text((302, 530), "ONE BROKEN LINK", font=font(24), fill=WHITE, anchor="mm")
    draw.text((978, 290), "LOCAL SYSTEM", font=font(30), fill=GREEN, anchor="mm")
    icon_factory(draw, 978, 410, GREEN)
    draw.text((978, 530), "ONE BIGGER BET", font=font(24), fill=WHITE, anchor="mm")
    arrow(draw, (555, 410), (720, 410), CYAN, 16)
    centered(draw, 640, "CONTROL THE CHAIN — CONCENTRATE THE RISK", CYAN, 38)
    return image


PACKAGES = [
    ("A", "The Billionaire Who Built His Supply Chain", package_a),
    ("B", "Why Owning the Supply Chain Changes Everything", package_b),
    ("C", "Inside the Factory Trying to Replace Imports", package_c),
]


def main() -> None:
    thumbs = []
    for key, title, maker in PACKAGES:
        image = maker()
        path = OUT / f"package-{key.lower()}.jpg"
        image.save(path, quality=94, optimize=True)
        thumbs.append((key, title, image))

    sheet = Image.new("RGB", (1280, 3 * 490), "#050a12")
    draw = ImageDraw.Draw(sheet)
    for index, (key, title, image) in enumerate(thumbs):
        y = index * 490
        thumb = image.resize((800, 450), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (0, y + 20))
        draw.text((830, y + 60), f"PACKAGE {key}", font=font(30), fill=CYAN)
        title_font = fit(draw, title, 400, 44, 30)
        # Manual wrapping for a stable cold-test sheet.
        words = title.split()
        lines, current = [], []
        for word in words:
            probe = " ".join(current + [word])
            if draw.textbbox((0, 0), probe, font=title_font)[2] <= 400:
                current.append(word)
            else:
                lines.append(" ".join(current))
                current = [word]
        if current:
            lines.append(" ".join(current))
        for line_index, line in enumerate(lines):
            draw.text((830, y + 120 + 58 * line_index), line, font=title_font, fill=WHITE)
        draw.text((830, y + 315), "Show title + thumbnail only.", font=font(23), fill=MUTED)
        draw.text((830, y + 355), "No story explanation.", font=font(23), fill=MUTED)
    sheet.save(OUT / "cold-viewer-package-test-sheet.jpg", quality=94, optimize=True)

    print(f"created {len(PACKAGES)} thumbnails and one test sheet in {OUT}")


if __name__ == "__main__":
    main()
