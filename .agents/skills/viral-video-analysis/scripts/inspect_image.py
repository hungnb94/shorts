#!/usr/bin/env python3
"""
inspect_image.py — PIL pixel-statistics image inspector.

Use when native vision tools are unavailable. Produces a structured
report covering palette, dominant colors, accent buckets, skin-tone
presence, row-profile (text bands), column-profile (text extents),
and per-region luminance. Optional --ascii on detected bands.

Usage:
    python3 inspect_image.py <path> [<path> ...]
    python3 inspect_image.py --no-row   <path>     # skip row profile (faster)
    python3 inspect_image.py --ascii-at y1,y2       # ASCII a band (run after first pass)

See accompanying SKILL.md (image-vision-fallback skill) for the
interpretation guide and pitfalls.
"""

from __future__ import annotations
import argparse
import statistics
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required: pip install pillow")


# ---------- core stats ----------

def core_stats(img: Image.Image) -> dict:
    pixels = list(img.getdata())
    n = len(pixels)
    avg = [sum(c[i] for c in pixels) / n for i in range(3)]
    sd = [
        statistics.pstdev(c[i] for c in pixels) for i in range(3)
    ]
    return {"avg": avg, "sd": sd, "n": n}


def top_colors(img: Image.Image, n: int = 5) -> list[tuple[tuple[int, int, int], int]]:
    small = img.resize((40, 72)).quantize(colors=8).convert("RGB")
    counts: dict[tuple[int, int, int], int] = {}
    for c in small.getdata():
        counts[c] = counts.get(c, 0) + 1
    items = sorted(counts.items(), key=lambda kv: -kv[1])
    total = sum(c for _, c in items)
    return [(rgb, count, round(count / total * 100, 1)) for rgb, count in items[:n]]


def accent_buckets(pixels: list) -> dict[str, int]:
    n = len(pixels)
    near_white = sum(
        1 for r, g, b in pixels if r > 220 and g > 220 and b > 220
    )
    near_black = sum(
        1 for r, g, b in pixels if r < 25 and g < 25 and b < 25
    )
    red_dom = sum(
        1 for r, g, b in pixels if r > 140 and g < 70 and b < 70
    )
    skin = sum(
        1
        for r, g, b in pixels
        if 70 < r < 230
        and 40 < g < 180
        and 20 < b < 170
        and r > g > b
        and r - b > 15
    )
    return {
        "near_white/px": near_white,
        "near_black/px": near_black,
        "red_dom/px": red_dom,
        "skin/px": skin,
        "n/px": n,
    }


def luminance_region(img: Image.Image) -> dict[str, float]:
    """Luminance averaged per third (top/mid/bot)."""
    w, h = img.size
    out = {}
    for name, box in (
        ("top", (0, 0, w, h // 3)),
        ("mid", (0, h // 3, w, 2 * h // 3)),
        ("bot", (0, 2 * h // 3, w, h)),
    ):
        region = img.crop(box)
        rp = list(region.getdata())
        lum = sum(sum(c) for c in rp) / (3 * len(rp))
        out[name] = round(lum, 1)
    return out


def row_profile(img: Image.Image, step: int = 8, thresh: int = 120) -> list[tuple[int, int]]:
    """Return [(y, bright_pixel_count)] for sampled rows."""
    g = img.convert("L")
    w, h = g.size
    out = []
    for y in range(0, h, step):
        bright = sum(1 for x in range(w) if g.getpixel((x, y)) > thresh)
        out.append((y, bright))
    return out


def cluster_bands(rows: list[tuple[int, int]]) -> list[tuple[int, int, int]]:
    """Cluster adjacent rows (gap <= 3*step) into bands. Returns [(y_start, y_end, max_bright)]."""
    bands = []
    cur = []
    for y, c in rows:
        if c == 0:
            if cur:
                bands.append(cur)
                cur = []
            continue
        if cur and y - cur[-1][0] > 12:  # gap > 12 = new band
            bands.append(cur)
            cur = []
        cur.append((y, c))
    if cur:
        bands.append(cur)
    return [
        (
            band[0][0],
            band[-1][0],
            max(c for _, c in band),
        )
        for band in bands
    ]


def column_profile(img: Image.Image, y1: int, y2: int, thresh: int = 120) -> tuple[int, int, str]:
    """For a y-band, return (left, right, ascii-bar-chart of 30 buckets)."""
    g = img.convert("L")
    w, _ = g.size
    cols = [0] * w
    for y in range(y1, y2):
        for x in range(w):
            if g.getpixel((x, y)) > thresh:
                cols[x] += 1
    nz = [i for i, c in enumerate(cols) if c > 0]
    if not nz:
        return -1, -1, "(empty band)"
    left, right = min(nz), max(nz)
    bucket_w = max(1, w // 30)
    lines = []
    for b in range(30):
        s = b * bucket_w
        e = min(w, (b + 1) * bucket_w)
        v = sum(cols[s:e])
        bar = "#" * min(40, v // 2)
        lines.append(f"  {s:3d}-{e:3d} {bar}")
    return left, right, "\n".join(lines)


def ascii_crop(img: Image.Image, box: tuple[int, int, int, int], step: int = 2) -> str:
    crop = img.crop(box).convert("L")
    cw, ch = crop.size
    out = []
    for y in range(0, ch, step):
        line = ""
        for x in range(0, cw, step):
            v = crop.getpixel((x, y))
            line += (
                "#" if v > 200 else "+" if v > 150 else "." if v > 100 else " "
            )
        out.append(line)
    return "\n".join(out)


# ---------- entry ----------

def inspect(path: str, *, do_row: bool = True, ascii_bands: list[tuple[int, int]] | None = None) -> None:
    img = Image.open(path).convert("RGB")
    w, h = img.size
    print(f"\n=== {path}  ({w}x{h}) ===")

    s = core_stats(img)
    print(
        f"avg RGB: ({s['avg'][0]:.0f}, {s['avg'][1]:.0f}, {s['avg'][2]:.0f})  "
        f"stddev: ({s['sd'][0]:.1f}, {s['sd'][1]:.1f}, {s['sd'][2]:.1f})"
    )

    print("top 5 colors (RGB, share%):")
    for c, _, share in top_colors(img, 5):
        print(f"   {c}  {share:5.1f}%")

    pixels = list(img.getdata())
    b = accent_buckets(pixels)
    print(
        f"near-white: {b['near_white/px']/b['n/px']*100:5.2f}%   "
        f"near-black: {b['near_black/px']/b['n/px']*100:5.2f}%   "
        f"red-dom: {b['red_dom/px']/b['n/px']*100:5.2f}%   "
        f"skin-tone: {b['skin/px']/b['n/px']*100:5.2f}%"
    )

    lum = luminance_region(img)
    print(
        f"luminance by region — top:{lum['top']:.0f}  mid:{lum['mid']:.0f}  bot:{lum['bot']:.0f}"
    )

    if do_row:
        rows = row_profile(img)
        bands = cluster_bands(rows)
        print(f"\nrow profile: {len(rows)} sampled rows → {len(bands)} bright band(s)")
        for y1, y2, mb in bands:
            print(f"  band y={y1}..{y2}  max bright-px/row={mb}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("paths", nargs="+", help="one or more image paths")
    p.add_argument("--no-row", action="store_true", help="skip row-profile (faster)")
    p.add_argument(
        "--ascii-at",
        action="append",
        default=[],
        metavar="x1,y1,x2,y2",
        help="emit ASCII for a crop; repeat for multiple crops",
    )
    args = p.parse_args()

    for path in args.paths:
        inspect(path, do_row=not args.no_row)

    if args.ascii_at:
        print("\n--- ASCII crops ---")
        for path in args.paths:
            img = Image.open(path).convert("RGB")
            print(f"\n# {path}")
            for spec in args.ascii_at:
                try:
                    box = tuple(int(v) for v in spec.split(","))
                except ValueError:
                    print(f"  bad --ascii-at spec: {spec}")
                    continue
                if len(box) != 4:
                    print(f"  bad --ascii-at spec: {spec}")
                    continue
                print(f"\n--- crop {box} ---")
                print(ascii_crop(img, box))


if __name__ == "__main__":
    main()
