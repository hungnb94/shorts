#!/usr/bin/env python3
"""Render Ronald Wayne v3 with Qwen-word-aligned captions and visuals.

The forty 1.5-second semantic beats remain fixed. Caption overlays are separate
from static chrome and are enabled only at each manifest's frame-safe ASR anchor.
The audio stream is copied unchanged from the verified Qwen v2 artifact.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

import render_ronaldwayne_v1 as base

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "ronaldwayne"
WORK = PROJECT / "work" / "v3-qwen-synced"
BEAT_DIR = WORK / "beats"
CARD_DIR = WORK / "cards"
CHROME_DIR = WORK / "chrome"
CAPTION_DIR = WORK / "captions"
CHECKS = PROJECT / "checks-v3-sync"
MANIFEST = PROJECT / "scripts" / "visual-edl-v3-qwen-synced.json"
V2 = PROJECT / "2026-07-25-ronald-wayne-v2-qwen.mp4"
FINAL = PROJECT / "2026-07-25-ronald-wayne-v3-qwen-synced.mp4"
W, H, FPS = base.W, base.H, base.FPS
BEAT_SECONDS = base.BEAT_SECONDS
TOTAL = base.TOTAL


def run(command: list[str | Path]) -> None:
    print("+", " ".join(str(item) for item in command), flush=True)
    subprocess.run([str(item) for item in command], check=True)


def custom_card(kind: str, index: int) -> Path:
    im = base.gradient_canvas((8, 12, 22), (22, 29, 45))
    draw = ImageDraw.Draw(im)

    if kind == "timeline_graphic":
        draw.line((170, 960, 910, 960), fill=base.WHITE, width=12)
        draw.ellipse((135, 925, 205, 995), fill=base.GREEN)
        draw.ellipse((875, 925, 945, 995), fill=base.RED)
        draw.line((215, 960, 865, 960), fill=base.YELLOW, width=8)
    elif kind == "risk_compare":
        draw.rounded_rectangle((90, 590, 500, 1260), 48, fill=(40, 18, 24), outline=base.RED, width=7)
        draw.rounded_rectangle((580, 590, 990, 1260), 48, fill=(12, 55, 44), outline=base.GREEN, width=7)
        for x in (205, 365):
            draw.ellipse((x - 55, 750, x + 55, 860), fill=(230, 220, 210))
            draw.rounded_rectangle((x - 80, 875, x + 80, 1080), 55, fill=(120, 66, 72))
        draw.ellipse((730, 750, 850, 870), fill=(230, 220, 210))
        draw.rounded_rectangle((700, 885, 880, 1110), 60, fill=(62, 124, 102))
    elif kind == "young_broke_graphic":
        for x in (250, 650):
            draw.ellipse((x, 690, x + 150, 840), fill=(226, 218, 204))
            draw.rounded_rectangle((x - 55, 855, x + 205, 1215), 80, fill=(65, 76, 94), outline=base.CYAN, width=6)
            draw.arc((x - 20, 1040, x + 175, 1170), 200, 340, fill=base.RED, width=10)
        draw.rounded_rectangle((165, 1270, 915, 1370), 40, fill=(10, 15, 24), outline=base.MUTED, width=4)
        draw.line((230, 1320, 850, 1320), fill=base.RED, width=10)
    elif kind == "creditor_graphic":
        base.asset_icons(draw, 710)
        draw.line((540, 1080, 540, 1280), fill=base.RED, width=20)
        draw.polygon([(485, 1260), (595, 1260), (540, 1350)], fill=base.RED)
        draw.rounded_rectangle((170, 1390, 910, 1500), 42, fill=(67, 17, 24), outline=base.RED, width=6)
    elif kind == "paperwork_graphic":
        for offset, angle in ((0, 0), (75, 0), (150, 0)):
            x = 165 + offset
            y = 560 + offset
            draw.rounded_rectangle((x, y, x + 610, y + 760), 24, fill=(234, 233, 224), outline=base.MUTED, width=5)
            for row in range(7):
                yy = y + 110 + row * 75
                draw.line((x + 70, yy, x + 520, yy), fill=(80, 84, 92), width=8)
    elif kind == "check_graphic":
        draw.rounded_rectangle((115, 640, 965, 1260), 44, fill=(236, 238, 228), outline=base.GREEN, width=8)
        draw.line((195, 830, 840, 830), fill=(72, 78, 84), width=9)
        draw.line((195, 965, 700, 965), fill=(72, 78, 84), width=9)
        draw.line((195, 1100, 570, 1100), fill=(72, 78, 84), width=9)
        draw.ellipse((730, 970, 850, 1090), outline=base.RED, width=12)
    elif kind == "lock_graphic":
        draw.rounded_rectangle((320, 850, 760, 1300), 52, fill=(12, 19, 30), outline=base.YELLOW, width=12)
        draw.arc((380, 570, 700, 970), 180, 360, fill=base.YELLOW, width=28)
        draw.ellipse((500, 1010, 580, 1090), fill=base.YELLOW)
        draw.rectangle((528, 1080, 552, 1190), fill=base.YELLOW)
    elif kind == "cta_graphic":
        colors = (base.YELLOW, base.RED, base.CYAN)
        for row, color in enumerate(colors):
            y = 620 + row * 260
            draw.rounded_rectangle((145, y, 935, y + 170), 46, fill=(9, 14, 24), outline=color, width=8)
            draw.ellipse((205, y + 45, 285, y + 125), outline=color, width=10)
            draw.line((360, y + 85, 850, y + 85), fill=color, width=18)
    else:
        raise ValueError(f"Unknown custom card: {kind}")

    output = CARD_DIR / f"{index:02d}.png"
    im.save(output)
    return output


def visual_configs() -> list[dict[str, Any]]:
    return [
        {"type": "video", "video": base.BBC, "ss": 120.0, "crop_w": 608, "crop_x": 900, "source_label": "BBC · RONALD WAYNE", "font_size": 78},
        {"type": "card", "card": "photo", "image": base.APPLE1, "source_label": "WIKIMEDIA · PUBLIC DOMAIN", "center_x": 0.50, "font_size": 82},
        {"type": "card", "card": "photo", "image": base.CONTRACT, "source_label": "CONTRACT ILLUSTRATION", "brightness": 0.34},
        {"type": "card", "card": "photo", "image": base.WAYNE_2022, "source_label": "RONALD WAYNE · 2022", "brightness": 0.38, "color": base.RED, "font_size": 66},
        {"type": "video", "video": base.BBC, "ss": 121.5, "crop_w": 608, "crop_x": 850, "source_label": "BBC", "font_size": 70},
        {"type": "video", "video": base.KPVM, "ss": 102.0, "crop_w": 270, "crop_x": 440, "source_label": "KPVM", "font_size": 74},
        {"type": "card", "card": "photo", "image": base.CONTRACT, "source_label": "CONTRACT ILLUSTRATION", "font_size": 68, "brightness": 0.35},
        {"type": "custom", "custom": "timeline_graphic", "source_label": "WAYNE'S ACCOUNT · APRIL 1976", "font_size": 58},
        {"type": "card", "card": "photo", "image": base.WAYNE_2022, "source_label": "WAYNE / VCF · 2024", "brightness": 0.40, "font_size": 72},
        {"type": "card", "card": "photo", "image": base.APPLE1_MUSEUM, "source_label": "APPLE COMPUTER COMPANY", "brightness": 0.46},
        {"type": "card", "card": "photo", "image": base.CONTRACT, "source_label": "PARTNERSHIP STRUCTURE", "brightness": 0.33, "color": base.RED, "font_size": 76},
        {"type": "video", "video": base.WOZ, "ss": 90.0, "crop_w": 270, "crop_x": 65, "source_label": "STEVE WOZNIAK · P2P", "color": base.RED, "font_size": 72},
        {"type": "custom", "custom": "risk_compare", "source_label": "RISK MODEL", "font_size": 80},
        {"type": "custom", "custom": "young_broke_graphic", "source_label": "JOBS + WOZ · RISK MODEL", "font_size": 82},
        {"type": "card", "card": "photo", "image": base.WAYNE_KOTTKE, "source_label": "WIKIMEDIA COMMONS", "brightness": 0.50, "center_x": 0.55, "font_size": 82},
        {"type": "card", "card": "risk", "source_label": "ASSET EXPOSURE · ILLUSTRATION", "font_size": 68},
        {"type": "custom", "custom": "creditor_graphic", "source_label": "POTENTIAL EXPOSURE · ILLUSTRATION", "color": base.RED, "font_size": 64},
        {"type": "card", "card": "photo", "image": base.APPLE1_MUSEUM, "source_label": "WIKIMEDIA COMMONS", "brightness": 0.50, "font_size": 82},
        {"type": "video", "video": base.BBC, "ss": 108.0, "crop_w": 608, "crop_x": 900, "source_label": "BBC", "color": base.GREEN, "font_size": 60},
        {"type": "video", "video": base.CBS, "ss": 47.5, "crop_w": 608, "crop_x": 760, "source_label": "CBS · RONALD WAYNE", "color": base.GREEN},
        {"type": "video", "video": base.CBS, "ss": 49.0, "crop_w": 608, "crop_x": 700, "source_label": "CBS · RONALD WAYNE", "color": base.GREEN, "font_size": 60},
        {"type": "card", "card": "photo", "image": base.WAYNE_2009, "source_label": "WIKIMEDIA COMMONS", "brightness": 0.45, "center_x": 0.48},
        {"type": "custom", "custom": "paperwork_graphic", "source_label": "IDENTITY COST · RECONSTRUCTION", "color": base.RED, "font_size": 64},
        {"type": "card", "card": "photo", "image": base.APPLE1, "source_label": "APPLE I · PUBLIC DOMAIN", "font_size": 72},
        {"type": "video", "video": base.KPVM, "ss": 103.5, "crop_w": 270, "crop_x": 440, "source_label": "KPVM · RONALD WAYNE", "color": base.GREEN, "font_size": 72},
        {"type": "card", "card": "photo", "image": base.WAYNE_2009, "source_label": "WIKIMEDIA COMMONS", "brightness": 0.52, "center_x": 0.48, "color": base.GREEN, "font_size": 72},
        {"type": "custom", "custom": "lock_graphic", "source_label": "YOUR DECISION", "color": base.YELLOW, "font_size": 72},
        {"type": "card", "card": "split", "left": "SELL", "right": "STAY", "source_label": "YOUR DECISION", "color": base.YELLOW, "font_size": 82},
        {"type": "custom", "custom": "cta_graphic", "source_label": "COMMIT BEFORE THE REVEAL", "color": base.CYAN, "font_size": 56},
        {"type": "video", "video": base.BBC, "ss": 198.0, "crop_w": 608, "crop_x": 880, "source_label": "BBC · RONALD WAYNE", "font_size": 78},
        {"type": "video", "video": base.BBC, "ss": 199.5, "crop_w": 608, "crop_x": 880, "source_label": "BBC · RONALD WAYNE", "color": base.GREEN, "font_size": 62},
        {"type": "card", "card": "photo", "image": base.WAYNE_2022, "source_label": "RONALD WAYNE · 2022", "brightness": 0.38, "font_size": 72},
        {"type": "card", "card": "photo", "image": base.CONTRACT, "source_label": "CONTRACT ILLUSTRATION", "brightness": 0.34, "font_size": 72},
        {"type": "custom", "custom": "check_graphic", "source_label": "WAYNE'S CONTRACT SALE", "color": base.YELLOW, "font_size": 72},
        {"type": "card", "card": "photo", "image": base.CONTRACT, "source_label": "CONTRACT ILLUSTRATION", "brightness": 0.40, "font_size": 78},
        {"type": "card", "card": "money", "amount": "$1.59M", "sub": "SOTHEBY'S · 2011", "source_label": "NPR / SOTHEBY'S", "color": base.GREEN, "font_size": 60},
        {"type": "video", "video": base.NEXT, "ss": 453.8, "crop_w": 608, "crop_x": 720, "source_label": "NEXTSHARK · RONALD WAYNE", "color": base.RED, "font_size": 88, "accurate_seek": True},
        {"type": "card", "card": "photo", "image": base.WAYNE_2022, "source_label": "RONALD WAYNE · 2022", "brightness": 0.38, "font_size": 78},
        {"type": "card", "card": "split", "left": "FOOL", "right": "FREE", "source_label": "COSTLY VERDICT", "font_size": 62, "color": base.YELLOW},
        {"type": "video", "video": base.BBC, "ss": 120.0, "crop_w": 608, "crop_x": 900, "source_label": "BBC · LOOP CLOSE", "color": base.YELLOW, "font_size": 58},
    ]


def chrome_overlay_for(beat: dict[str, Any], index: int) -> Path:
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, 0, int(W * (index + 1) / 40), 10), fill=base.YELLOW)
    source = beat.get("source_label")
    if source:
        font = base.font(31)
        bbox = draw.textbbox((0, 0), source, font=font)
        width = min(900, max(466, bbox[2] - bbox[0] + 60))
        draw.rounded_rectangle((54, 62, 54 + width, 124), 22, fill=(6, 9, 15, 220), outline=base.MUTED, width=2)
        draw.text((75, 93), source, font=font, anchor="lm", fill=base.MUTED)
    xs = [65, 405, 700]
    draw.text((xs[index % 3], 1180), "MONEY BLINDSPOT", font=base.font(30), fill=(255, 255, 255, 105), stroke_width=2, stroke_fill=(0, 0, 0, 100))
    output = CHROME_DIR / f"{index:02d}.png"
    im.save(output)
    return output


def caption_overlay_for(beat: dict[str, Any], index: int) -> Path:
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    y = int(beat.get("caption_y", 1510))
    color = tuple(beat.get("color", base.YELLOW))
    base.centered_text(draw, beat["caption"], y, int(beat.get("font_size", 88)), color, stroke=10, max_width=950)
    if beat.get("subcaption"):
        base.centered_text(draw, beat["subcaption"], y + 130, int(beat.get("sub_size", 50)), base.WHITE, stroke=7, max_width=920)
    output = CAPTION_DIR / f"{index:02d}.png"
    im.save(output)
    return output


def render_video_beat(index: int, beat: dict[str, Any], chrome: Path, caption: Path) -> Path:
    output = BEAT_DIR / f"{index:02d}.mp4"
    delay = float(beat["caption_delay"])
    crop_w = beat["crop_w"]
    crop_x = beat["crop_x"]
    source_prefix = ""
    command: list[str | Path] = ["ffmpeg", "-y", "-v", "error"]
    if beat.get("accurate_seek"):
        preroll = min(5.0, float(beat["ss"]))
        command.extend(["-ss", str(float(beat["ss"]) - preroll), "-i", beat["video"]])
        source_prefix = f"trim=start={preroll:.6f},setpts=PTS-STARTPTS,"
    else:
        command.extend(["-ss", str(beat["ss"]), "-i", beat["video"]])
    command.extend(["-i", chrome, "-i", caption])
    vf = (
        f"[0:v]{source_prefix}crop={crop_w}:ih:{crop_x}:0,scale={W}:{H}:flags=lanczos,fps={FPS},"
        "eq=contrast=1.06:saturation=1.02[bg];"
        "[1:v]format=rgba[chrome];[2:v]format=rgba[caption];"
        "[bg][chrome]overlay=0:0:eof_action=repeat:shortest=0[with_chrome];"
        f"[with_chrome][caption]overlay=0:0:eof_action=repeat:shortest=0:enable='gte(t,{delay:.6f})',format=yuv420p[v]"
    )
    command.extend([
        "-t", str(BEAT_SECONDS), "-an", "-filter_complex", vf, "-map", "[v]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-g", "45", "-keyint_min", "45", output,
    ])
    run(command)
    return output


def render_card_beat(index: int, beat: dict[str, Any], card: Path, chrome: Path, caption: Path) -> Path:
    output = BEAT_DIR / f"{index:02d}.mp4"
    delay = float(beat["caption_delay"])
    zoom = "min(zoom+0.0015,1.08)" if index % 2 == 0 else "if(eq(on,1),1.06,max(zoom-0.0012,1.0))"
    vf = (
        f"[0:v]scale=1080:1920,zoompan=z='{zoom}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d=1:s={W}x{H}:fps={FPS}[bg];"
        "[1:v]format=rgba[chrome];[2:v]format=rgba[caption];"
        "[bg][chrome]overlay=0:0:eof_action=repeat:shortest=0[with_chrome];"
        f"[with_chrome][caption]overlay=0:0:eof_action=repeat:shortest=0:enable='gte(t,{delay:.6f})',format=yuv420p[v]"
    )
    run([
        "ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", card, "-i", chrome, "-i", caption,
        "-t", str(BEAT_SECONDS), "-an", "-filter_complex", vf, "-map", "[v]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-g", "45", "-keyint_min", "45", output,
    ])
    return output


def main() -> None:
    for directory in (WORK, BEAT_DIR, CARD_DIR, CHROME_DIR, CAPTION_DIR, CHECKS):
        directory.mkdir(parents=True, exist_ok=True)
    required = [MANIFEST, V2, base.FONT, base.BBC, base.NEXT, base.CBS, base.WOZ, base.KPVM, base.WAYNE_2022, base.WAYNE_2009, base.WAYNE_KOTTKE, base.APPLE1, base.APPLE1_MUSEUM, base.CONTRACT]
    for path in required:
        if not Path(path).is_file():
            raise FileNotFoundError(path)

    sync_beats = json.loads(MANIFEST.read_text(encoding="utf-8"))
    visuals = visual_configs()
    if len(sync_beats) != 40 or len(visuals) != 40:
        raise RuntimeError(f"Expected 40 sync beats and visuals, got {len(sync_beats)} and {len(visuals)}")

    base.CARD_DIR = CARD_DIR
    clips: list[Path] = []
    render_manifest: list[dict[str, Any]] = []
    for index, (sync, visual) in enumerate(zip(sync_beats, visuals, strict=True)):
        beat = {**visual, **sync}
        chrome = chrome_overlay_for(beat, index)
        caption = caption_overlay_for(beat, index)
        cached = BEAT_DIR / f"{index:02d}.mp4"
        if cached.is_file():
            clip = cached
        elif beat["type"] == "video":
            clip = render_video_beat(index, beat, chrome, caption)
        else:
            card = custom_card(beat["custom"], index) if beat["type"] == "custom" else base.card_for(beat, index)
            clip = render_card_beat(index, beat, card, chrome, caption)
        clips.append(clip)
        render_manifest.append({
            **sync,
            "type": beat["type"],
            "source_label": beat.get("source_label"),
            "source": str(beat.get("video", beat.get("image", beat.get("custom", beat.get("card"))))),
        })

    concat = WORK / "video-concat.txt"
    concat.write_text("".join(f"file '{clip.as_posix()}'\n" for clip in clips), encoding="utf-8")
    base_video = WORK / "video-base.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat, "-c", "copy", base_video])

    temp = FINAL.with_suffix(".tmp.mp4")
    run([
        "ffmpeg", "-y", "-v", "error", "-i", base_video, "-i", V2, "-t", str(TOTAL),
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "copy",
        "-movflags", "+faststart", temp,
    ])
    temp.replace(FINAL)
    (CHECKS / "render-manifest.json").write_text(json.dumps(render_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(FINAL)


if __name__ == "__main__":
    main()
