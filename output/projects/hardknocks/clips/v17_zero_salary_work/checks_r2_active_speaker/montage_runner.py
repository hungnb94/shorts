"""Build Montage contact sheet from args."""

import argparse
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def natural_key(path: Path) -> list:
    return [int(part) if part.isdigit() else part.lower()
            for part in re.split(r"(\d+)", path.name)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--cols", type=int, default=5)
    parser.add_argument("--thumb-width", type=int, default=360)
    args = parser.parse_args()
    files = sorted(Path(args.input_dir).iterdir(), key=natural_key)
    if not files:
        return
    cols = args.cols
    rows = (len(files) + cols - 1) // cols
    sample = Image.open(files[0])
    thumb_w = args.thumb_width
    ratio = sample.height / sample.width
    thumb_h = int(thumb_w * ratio)
    sheet = Image.new("RGB", (cols * thumb_w, rows * thumb_h), (10, 10, 10))
    draw = ImageDraw.Draw(sheet)
    for idx, path in enumerate(files):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        x = (idx % cols) * thumb_w
        y = (idx // cols) * thumb_h
        sheet.paste(image, (x, y))
        label = path.stem
        draw.text((x + 6, y + 6), label, fill=(255, 210, 60))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=92)


if __name__ == "__main__":
    main()
