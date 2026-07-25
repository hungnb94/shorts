#!/usr/bin/env python3
"""Render the 60-second Ronald Wayne MONEY BLINDSPOT Short.

The visual edit is intentionally quantized to forty 1.5-second semantic beats.
Every beat changes source, crop, evidence card, or argument state. Captions are
rasterized with Pillow because this host FFmpeg lacks libass/drawtext.
"""

from __future__ import annotations

import json
import math
import random
import struct
import subprocess
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "ronaldwayne"
SOURCE = PROJECT / "source"
IMAGES = SOURCE / "images"
VIDEOS = SOURCE / "video"
WORK = PROJECT / "work" / "v1"
BEAT_DIR = WORK / "beats"
CARD_DIR = WORK / "cards"
OVERLAY_DIR = WORK / "overlays"
AUDIO_DIR = WORK / "audio"
ANALYSIS = PROJECT / "analysis"
CHECKS = PROJECT / "checks"
SCRIPT = PROJECT / "scripts" / "script-v1.json"
FINAL = PROJECT / "2026-07-25-ronald-wayne-v1.mp4"
FONT = ROOT / "assets" / "fonts" / "Komika-Axis.ttf"

W, H, FPS = 1080, 1920, 30
BEAT_SECONDS = 1.5
TOTAL = 60.0
YELLOW = (255, 203, 57, 255)
GREEN = (114, 235, 77, 255)
RED = (255, 86, 91, 255)
WHITE = (255, 255, 255, 255)
MUTED = (190, 198, 211, 255)
CYAN = (88, 220, 255, 255)

BBC = VIDEOS / "bvWh8sh_wPY.mp4"
NEXT = VIDEOS / "YAF2-U7InWE.mp4"
CBS = VIDEOS / "M3R50CA9ok8.mp4"
WOZ = VIDEOS / "hPyI_RtHFGU.mp4"
KPVM = VIDEOS / "_nFHSv5GxhI.mp4"
WAYNE_2022 = IMAGES / "ronald-wayne-2022.webp"
WAYNE_2009 = IMAGES / "ronald-wayne-macworld-2009.jpg"
WAYNE_KOTTKE = IMAGES / "kottke-wayne.jpg"
APPLE1 = IMAGES / "apple1-public-domain.jpg"
APPLE1_MUSEUM = IMAGES / "apple1-museum.jpg"
APPLE_LOGO = IMAGES / "apple-first-logo.png"
CONTRACT = IMAGES / "contract-illustration.jpg"


def run(cmd: list[str | Path]) -> None:
    print("+", " ".join(map(str, cmd)), flush=True)
    subprocess.run([str(x) for x in cmd], check=True)


def fit_cover(img: Image.Image, size: tuple[int, int], center_x: float = 0.5, center_y: float = 0.5) -> Image.Image:
    img = img.convert("RGB")
    tw, th = size
    scale = max(tw / img.width, th / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = max(0, min(nw - tw, int(nw * center_x - tw / 2)))
    top = max(0, min(nh - th, int(nh * center_y - th / 2)))
    return img.crop((left, top, left + tw, top + th))


def gradient_canvas(top=(8, 12, 22), bottom=(20, 26, 42)) -> Image.Image:
    im = Image.new("RGB", (W, H))
    pix = im.load()
    assert pix is not None
    for y in range(H):
        t = y / max(H - 1, 1)
        color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        for x in range(W):
            pix[x, y] = color
    return im


def dark_photo(path: Path, center_x=0.5, brightness=0.48, blur=0.0) -> Image.Image:
    im = fit_cover(Image.open(path), (W, H), center_x=center_x)
    im = ImageEnhance.Color(im).enhance(0.78)
    im = ImageEnhance.Contrast(im).enhance(1.12)
    im = ImageEnhance.Brightness(im).enhance(brightness)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return im


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT), size)


def centered_text(draw: ImageDraw.ImageDraw, text: str, y: int, size: int, fill=WHITE, stroke=9, max_width=940) -> None:
    f = font(max(size, 28))
    while size >= 28:
        f = font(size)
        box = draw.textbbox((0, 0), text, font=f, stroke_width=stroke)
        if box[2] - box[0] <= max_width:
            break
        size -= 3
    draw.text((W // 2, y), text, font=f, anchor="mm", fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0, 240))


def asset_icons(draw: ImageDraw.ImageDraw, y=1230) -> None:
    # House
    draw.rounded_rectangle((95, y, 320, y + 260), 28, fill=(10, 16, 28, 235), outline=YELLOW, width=5)
    draw.polygon([(140, y + 110), (207, y + 45), (275, y + 110)], fill=YELLOW)
    draw.rectangle((150, y + 110, 265, y + 225), fill=(238, 242, 248))
    draw.rectangle((195, y + 160, 225, y + 225), fill=(29, 38, 56))
    # Car
    draw.rounded_rectangle((425, y, 655, y + 260), 28, fill=(10, 16, 28, 235), outline=CYAN, width=5)
    draw.rounded_rectangle((465, y + 110, 615, y + 185), 22, fill=CYAN)
    draw.polygon([(495, y + 110), (530, y + 70), (580, y + 110)], fill=(180, 239, 255))
    draw.ellipse((485, y + 170, 530, y + 215), fill=(8, 12, 20))
    draw.ellipse((560, y + 170, 605, y + 215), fill=(8, 12, 20))
    # Bank
    draw.rounded_rectangle((755, y, 985, y + 260), 28, fill=(10, 16, 28, 235), outline=GREEN, width=5)
    draw.polygon([(800, y + 95), (870, y + 45), (940, y + 95)], fill=GREEN)
    for x in (815, 855, 895, 935):
        draw.rectangle((x, y + 100, x + 20, y + 205), fill=(214, 255, 226))
    draw.rectangle((790, y + 205, 955, y + 225), fill=GREEN)


def card_for(beat: dict, index: int) -> Path:
    kind = beat.get("card", "photo")
    if kind == "photo":
        im = dark_photo(Path(beat["image"]), beat.get("center_x", 0.5), beat.get("brightness", 0.48))
    elif kind == "gradient":
        im = gradient_canvas(tuple(beat.get("top", (8, 12, 22))), tuple(beat.get("bottom", (20, 26, 42))))
    elif kind == "risk":
        im = dark_photo(WAYNE_2022, 0.5, 0.28)
        asset_icons(ImageDraw.Draw(im), 1180)
    elif kind == "timeline":
        im = gradient_canvas((8, 12, 20), (24, 32, 51))
        d = ImageDraw.Draw(im)
        d.line((170, 960, 910, 960), fill=WHITE, width=12)
        d.ellipse((135, 925, 205, 995), fill=GREEN)
        d.ellipse((875, 925, 945, 995), fill=RED)
        centered_text(d, "APRIL 1", 820, 92, GREEN)
        centered_text(d, "APRIL 12", 1110, 92, RED)
        centered_text(d, "12 DAYS", 965, 142, YELLOW)
    elif kind == "liability":
        im = gradient_canvas((13, 15, 24), (34, 15, 20))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((130, 600, 950, 1250), 55, fill=(6, 10, 17), outline=RED, width=8)
        centered_text(d, "APPLE DEBT", 750, 112, RED)
        d.line((540, 880, 540, 1050), fill=RED, width=18)
        d.polygon([(500, 1040), (580, 1040), (540, 1110)], fill=RED)
        centered_text(d, "PERSONAL ASSETS", 1170, 92, WHITE)
    elif kind == "asset":
        im = gradient_canvas((8, 11, 18), (17, 26, 34))
        d = ImageDraw.Draw(im)
        asset_icons(d, 730)
        active = beat.get("active", 0)
        x = [95, 425, 755][active]
        d.rounded_rectangle((x - 12, 718, x + 242, 1002), 34, outline=RED, width=13)
    elif kind == "split":
        im = Image.new("RGB", (W, H), (10, 14, 22))
        d = ImageDraw.Draw(im)
        d.polygon([(0, 0), (W, 0), (0, H)], fill=(76, 18, 24))
        d.polygon([(W, 0), (W, H), (0, H)], fill=(12, 66, 48))
        centered_text(d, beat.get("left", "SELL"), 720, 150, RED)
        centered_text(d, "OR", 960, 84, WHITE)
        centered_text(d, beat.get("right", "STAY"), 1200, 150, GREEN)
    elif kind == "money":
        im = gradient_canvas((8, 16, 13), (11, 35, 25))
        d = ImageDraw.Draw(im)
        amount = beat.get("amount", "$800")
        centered_text(d, amount, 930, 220, YELLOW)
        if beat.get("sub"):
            centered_text(d, beat["sub"], 1130, 72, WHITE)
        for i in range(20):
            x = 70 + (i * 127) % 960
            y = 430 + (i * 173) % 980
            d.text((x, y), "$", font=font(44), fill=(70, 170, 98, 110))
    elif kind == "cta":
        im = gradient_canvas((11, 14, 25), (25, 17, 38))
        d = ImageDraw.Draw(im)
        labels = [("LIKE", YELLOW), ("SUBSCRIBE", RED), ("COMMENT", CYAN)]
        for j, (label, col) in enumerate(labels):
            y = 640 + j * 260
            d.rounded_rectangle((135, y, 945, y + 180), 40, fill=(8, 12, 20), outline=col, width=7)
            centered_text(d, label, y + 90, 96, col)
    elif kind == "headline":
        im = gradient_canvas((7, 9, 15), (24, 25, 32))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((80, 510, 1000, 1290), 42, fill=(238, 238, 232), outline=YELLOW, width=7)
        d.rectangle((80, 510, 1000, 640), fill=(30, 31, 36))
        centered_text(d, beat.get("publisher", "SOURCE"), 575, 60, WHITE)
        centered_text(d, beat.get("headline", "THE DECISION"), 850, 82, (20, 22, 28, 255), stroke=3, max_width=820)
        centered_text(d, beat.get("headline2", ""), 1000, 82, (20, 22, 28, 255), stroke=3, max_width=820)
        centered_text(d, beat.get("date", ""), 1190, 44, (70, 72, 78, 255), stroke=2)
    else:
        raise ValueError(f"Unknown card kind {kind}")
    out = CARD_DIR / f"{index:02d}.png"
    im.save(out)
    return out


def overlay_for(beat: dict, index: int) -> Path:
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # Thin progress bar gives continuous progress without counting as a state change.
    d.rectangle((0, 0, int(W * (index + 1) / 40), 10), fill=YELLOW)
    source = beat.get("source_label")
    if source:
        d.rounded_rectangle((54, 62, 520, 124), 22, fill=(6, 9, 15, 220), outline=MUTED, width=2)
        d.text((75, 93), source, font=font(31), anchor="lm", fill=MUTED)
    caption = beat["caption"]
    y = beat.get("caption_y", 1510)
    color = tuple(beat.get("color", YELLOW))
    centered_text(d, caption, y, beat.get("font_size", 98), color, stroke=10, max_width=950)
    if beat.get("subcaption"):
        centered_text(d, beat["subcaption"], y + 130, beat.get("sub_size", 54), WHITE, stroke=7, max_width=920)
    # Moving watermark; always above lower 15% exclusion line and away from subcaptions.
    xs = [65, 405, 700]
    wm_y = 1180 if beat.get("subcaption") else 1590
    d.text((xs[index % 3], wm_y), "MONEY BLINDSPOT", font=font(30), fill=(255, 255, 255, 105), stroke_width=2, stroke_fill=(0, 0, 0, 100))
    out = OVERLAY_DIR / f"{index:02d}.png"
    im.save(out)
    return out


def render_video_beat(index: int, beat: dict, overlay: Path) -> Path:
    out = BEAT_DIR / f"{index:02d}.mp4"
    crop_w = beat["crop_w"]
    crop_x = beat["crop_x"]
    vf = (
        f"[0:v]crop={crop_w}:ih:{crop_x}:0,scale={W}:{H}:flags=lanczos,"
        f"fps={FPS},eq=contrast=1.06:saturation=1.02[bg];"
        "[1:v]format=rgba[ov];[bg][ov]overlay=0:0:shortest=1,format=yuv420p[v]"
    )
    inputs: list[str | Path] = ["ffmpeg", "-y", "-v", "error"]
    if beat.get("accurate_seek"):
        inputs.extend(["-i", Path(beat["video"]), "-loop", "1", "-i", overlay, "-ss", str(beat["ss"])])
    else:
        inputs.extend(["-ss", str(beat["ss"]), "-i", Path(beat["video"]), "-loop", "1", "-i", overlay])
    run(inputs + [
        "-t", str(BEAT_SECONDS), "-an",
        "-filter_complex", vf, "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", str(FPS), "-g", "45", "-keyint_min", "45", out,
    ])
    return out


def render_card_beat(index: int, card: Path, overlay: Path) -> Path:
    out = BEAT_DIR / f"{index:02d}.mp4"
    # Alternating micro-zoom preserves motion while the semantic source still changes every 1.5s.
    z = "min(zoom+0.0015,1.08)" if index % 2 == 0 else "if(eq(on,1),1.06,max(zoom-0.0012,1.0))"
    vf = (
        f"[0:v]scale=1080:1920,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d=1:s={W}x{H}:fps={FPS}[bg];"
        "[1:v]format=rgba[ov];[bg][ov]overlay=0:0:shortest=1,format=yuv420p[v]"
    )
    run([
        "ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", card,
        "-loop", "1", "-i", overlay, "-t", str(BEAT_SECONDS), "-an",
        "-filter_complex", vf, "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", str(FPS), "-g", "45", "-keyint_min", "45", out,
    ])
    return out


def make_music() -> Path:
    out = AUDIO_DIR / "music-bed.wav"
    sr = 48000
    rng = random.Random(19760401)
    with wave.open(str(out), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        frames = bytearray()
        for n in range(int(TOTAL * sr)):
            t = n / sr
            if t < 25.5:
                freqs, base = (55.0, 82.5, 110.0), 0.052
            elif t < 43.5:
                freqs, base = (65.0, 97.5, 130.0), 0.065
            else:
                freqs, base = (49.0, 73.5, 98.0), 0.046
            drone = sum(math.sin(2 * math.pi * f * t + i * 0.7) for i, f in enumerate(freqs)) / len(freqs)
            phase = t % 1.5
            kick = math.sin(2 * math.pi * (95 - 45 * phase) * phase) * math.exp(-18 * phase) if phase < 0.22 else 0.0
            tick_phase = (t + 0.75) % 1.5
            tick = (rng.random() * 2 - 1) * math.exp(-45 * tick_phase) if tick_phase < 0.07 else 0.0
            sample = max(-0.95, min(0.95, base * drone + 0.075 * kick + 0.014 * tick))
            iv = int(sample * 32767)
            frames += struct.pack("<hh", iv, iv)
        wf.writeframes(frames)
    return out


def exact_slot(inp: Path, out: Path, seconds: float, extra_filter="") -> None:
    filters = []
    if extra_filter:
        filters.append(extra_filter)
    filters.extend([f"apad=whole_dur={seconds}", f"atrim=0:{seconds}", "aresample=48000"])
    run([
        "ffmpeg", "-y", "-v", "error", "-i", inp, "-af", ",".join(filters),
        "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", out,
    ])


def build_voice_timeline(config: dict) -> Path:
    pieces: list[Path] = []
    for seg in config["segments"]:
        slot = float(seg["end"] - seg["start"])
        out = AUDIO_DIR / f"slot-{len(pieces):02d}-{seg['id']}.wav"
        if seg["type"] == "tts":
            inp = PROJECT / "tts" / "fitted" / f"{seg['id']}.wav"
            exact_slot(inp, out, slot)
        else:
            source = {"M3R50CA9ok8": CBS, "YAF2-U7InWE": NEXT}[seg["source"]]
            raw = AUDIO_DIR / f"raw-{seg['id']}.wav"
            source_take = slot * (1.08 if seg["id"] == "cbs_quote" else 1.0)
            run([
                "ffmpeg", "-y", "-v", "error", "-i", source, "-ss", str(seg["source_start"]), "-t", str(source_take),
                "-vn", "-af", "highpass=f=65,loudnorm=I=-16:TP=-1.5:LRA=8",
                "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", raw,
            ])
            speed = 1.08 if seg["id"] == "cbs_quote" else 1.0
            exact_slot(raw, out, slot, f"atempo={speed}")
        pieces.append(out)
    concat = AUDIO_DIR / "voice-concat.txt"
    concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in pieces), encoding="utf-8")
    voice = AUDIO_DIR / "voice-timeline.wav"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat, "-c:a", "pcm_s16le", voice])
    exact = AUDIO_DIR / "voice-timeline-exact.wav"
    exact_slot(voice, exact, TOTAL)
    return exact


def beats() -> list[dict]:
    return [
        {"type":"video","video":BBC,"ss":120.0,"crop_w":608,"crop_x":900,"caption":"THE INTERNET SAYS","source_label":"BBC · RONALD WAYNE","font_size":78},
        {"type":"card","card":"photo","image":APPLE1,"caption":"10% OF APPLE","source_label":"WIKIMEDIA · PUBLIC DOMAIN","center_x":0.50,"font_size":82},
        {"type":"card","card":"photo","image":CONTRACT,"caption":"SOLD FOR $800","source_label":"THE POPULAR CLAIM · ILLUSTRATION","color":YELLOW,"brightness":0.34},
        {"type":"card","card":"headline","publisher":"RONALD WAYNE · 2026","headline":"THAT IS","headline2":"TOTALLY FALSE","date":"DIRECT CORRECTION","caption":"WAYNE DISPUTES IT","source_label":"ROOMPASS INTERVIEW · 2026","color":RED,"font_size":72},
        {"type":"video","video":BBC,"ss":121.5,"crop_w":608,"crop_x":850,"caption":"WHAT ACTUALLY HAPPENED?","source_label":"BBC","font_size":70},
        {"type":"video","video":KPVM,"ss":102.0,"crop_w":270,"crop_x":440,"caption":"DRAFTED THE AGREEMENT","source_label":"KPVM","font_size":74},
        {"type":"card","card":"photo","image":CONTRACT,"caption":"SIGNED APRIL 1","source_label":"CONTRACT ILLUSTRATION","font_size":82,"brightness":0.35},
        {"type":"card","card":"timeline","caption":"NAME REMOVED","subcaption":"12 DAYS LATER","source_label":"WAYNE'S ACCOUNT · APRIL 1976","caption_y":1450,"font_size":86},
        {"type":"card","card":"money","amount":"$800","sub":"JOBS' LATER CHECK","caption":"PAID AFTER HE LEFT","source_label":"WAYNE / VCF · 2024","color":YELLOW,"font_size":76},
        {"type":"card","card":"liability","caption":"NOT A CORPORATION","source_label":"LEGAL MECHANISM","font_size":84},
        {"type":"card","card":"liability","caption":"PERSONAL LIABILITY","source_label":"LEGAL MECHANISM","color":RED,"font_size":84},
        {"type":"video","video":WOZ,"ss":90.0,"crop_w":270,"crop_x":65,"caption":"EVERY PARTNER","source_label":"STEVE WOZNIAK · P2P","font_size":90},
        {"type":"card","card":"split","left":"JOBS + WOZ","right":"WAYNE","caption":"RISK WASN'T EQUAL","source_label":"RISK MODEL","font_size":82},
        {"type":"card","card":"asset","active":0,"caption":"HIS HOUSE","source_label":"ILLUSTRATION","color":YELLOW},
        {"type":"card","card":"asset","active":1,"caption":"HIS CAR","source_label":"ILLUSTRATION","color":CYAN},
        {"type":"card","card":"asset","active":2,"caption":"HIS SAVINGS","source_label":"ILLUSTRATION","color":GREEN},
        {"type":"card","card":"photo","image":WAYNE_KOTTKE,"caption":"WAYNE HAD ASSETS","source_label":"WIKIMEDIA COMMONS","brightness":0.50,"center_x":0.55},
        {"type":"card","card":"photo","image":APPLE1_MUSEUM,"caption":"BUT HE BELIEVED","source_label":"WIKIMEDIA COMMONS","brightness":0.50},
        {"type":"video","video":BBC,"ss":108.0,"crop_w":608,"crop_x":900,"caption":"IN APPLE","source_label":"BBC","color":GREEN},
        {"type":"video","video":CBS,"ss":47.5,"crop_w":608,"crop_x":760,"caption":"RIGHT PRODUCT","source_label":"CBS · RONALD WAYNE","color":GREEN},
        {"type":"video","video":CBS,"ss":49.0,"crop_w":608,"crop_x":700,"caption":"RIGHT TIME","source_label":"CBS · RONALD WAYNE","color":GREEN},
        {"type":"card","card":"headline","publisher":"WAYNE'S VIEW","headline":"DECADES OF","headline2":"PAPERWORK","date":"IDENTITY COST","caption":"NOT HIS DREAM","source_label":"RECONSTRUCTION","color":RED},
        {"type":"card","card":"photo","image":APPLE1,"caption":"HE WANTED TO INVENT","source_label":"APPLE I · PUBLIC DOMAIN","font_size":78},
        {"type":"video","video":BBC,"ss":196.5,"crop_w":608,"crop_x":875,"caption":"NOT MANAGE FORMS","source_label":"BBC","font_size":82},
        {"type":"card","card":"photo","image":WAYNE_2009,"caption":"HE CHOSE HIS LIFE","source_label":"WIKIMEDIA COMMONS","brightness":0.48,"center_x":0.48},
        {"type":"card","card":"split","left":"PAPERWORK","right":"INVENT","caption":"OVER APPLE","source_label":"IDENTITY VERDICT","color":YELLOW},
        {"type":"card","card":"split","left":"SELL","right":"STAY","caption":"LOCK YOUR VERDICT","source_label":"YOUR DECISION","color":YELLOW},
        {"type":"card","card":"cta","caption":"LIKE + SUBSCRIBE","source_label":"IF THE NEXT FACT FLIPS YOU","font_size":78,"color":YELLOW},
        {"type":"card","card":"cta","caption":"COMMENT: SELL OR STAY","source_label":"COMMIT BEFORE THE REVEAL","font_size":66,"color":CYAN},
        {"type":"video","video":BBC,"ss":198.0,"crop_w":608,"crop_x":880,"caption":"NO REGRET LEAVING","source_label":"BBC · RONALD WAYNE","color":GREEN,"font_size":78},
        {"type":"card","card":"headline","publisher":"NPR","headline":"A $1.6 MILLION","headline2":"REGRET","date":"DEC. 13, 2011","caption":"HIS REAL REGRET?","source_label":"NPR","color":YELLOW,"font_size":80},
        {"type":"card","card":"photo","image":CONTRACT,"caption":"THE ORIGINAL CONTRACT","source_label":"CONTRACT ILLUSTRATION","font_size":76,"brightness":0.34},
        {"type":"card","card":"money","amount":"$500","sub":"WAYNE'S SALE PRICE","caption":"HE SOLD IT","source_label":"NEXTSHARK / NPR","color":WHITE},
        {"type":"card","card":"photo","image":CONTRACT,"caption":"AUCTIONED IN 2011","source_label":"CONTRACT ILLUSTRATION","color":WHITE,"brightness":0.34},
        {"type":"card","card":"money","amount":"$1.59M","sub":"SOTHEBY'S · 2011","caption":"LATER: $1.59 MILLION","source_label":"NPR / SOTHEBY'S","font_size":72,"color":GREEN},
        {"type":"card","card":"headline","publisher":"NPR","headline":"$1.6 MILLION","headline2":"FOR THE CONTRACT","date":"VERIFIED PAYOFF","caption":"NOT THE APPLE STAKE","source_label":"NPR","font_size":68,"color":MUTED},
        {"type":"video","video":NEXT,"ss":453.8,"crop_w":608,"crop_x":720,"caption":"THAT, I REGRET","source_label":"NEXTSHARK · RONALD WAYNE","color":RED,"font_size":88,"accurate_seek":True},
        {"type":"card","card":"split","left":"FOOL","right":"FREE","caption":"WHAT'S YOUR VERDICT?","source_label":"COSTLY VERDICT","font_size":76,"color":YELLOW},
        {"type":"card","card":"photo","image":WAYNE_2022,"caption":"DID WALKING AWAY","subcaption":"GIVE HIM FREEDOM?","source_label":"RONALD WAYNE · 2022","color":YELLOW,"brightness":0.38,"font_size":70},
        {"type":"video","video":BBC,"ss":120.0,"crop_w":608,"crop_x":900,"caption":"WALK AWAY = FREEDOM?","source_label":"BBC · LOOP CLOSE","color":YELLOW,"font_size":72},
    ]


def main() -> None:
    for p in (WORK, BEAT_DIR, CARD_DIR, OVERLAY_DIR, AUDIO_DIR, ANALYSIS, CHECKS):
        p.mkdir(parents=True, exist_ok=True)
    required = [SCRIPT, FONT, BBC, NEXT, CBS, WOZ, KPVM, WAYNE_2022, WAYNE_2009, WAYNE_KOTTKE, APPLE1, APPLE1_MUSEUM, APPLE_LOGO, CONTRACT]
    for p in required:
        if not p.exists():
            raise FileNotFoundError(p)
    config = json.loads(SCRIPT.read_text(encoding="utf-8"))
    beat_list = beats()
    if len(beat_list) != 40:
        raise RuntimeError(f"Expected 40 beats, got {len(beat_list)}")

    clips: list[Path] = []
    visual_manifest = []
    for i, beat in enumerate(beat_list):
        overlay = overlay_for(beat, i)
        cached = BEAT_DIR / f"{i:02d}.mp4"
        if cached.exists():
            clip = cached
        elif beat["type"] == "video":
            clip = render_video_beat(i, beat, overlay)
        else:
            card = card_for(beat, i)
            clip = render_card_beat(i, card, overlay)
        clips.append(clip)
        visual_manifest.append({
            "index": i, "start": i * BEAT_SECONDS, "end": (i + 1) * BEAT_SECONDS,
            "type": beat["type"], "caption": beat["caption"], "source_label": beat.get("source_label"),
            "source": str(beat.get("video", beat.get("image", beat.get("card")))),
        })

    concat = WORK / "video-concat.txt"
    concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in clips), encoding="utf-8")
    base = WORK / "video-base.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat, "-c", "copy", base])

    voice = build_voice_timeline(config)
    music = make_music()
    mixed = AUDIO_DIR / "final-mix.wav"
    run([
        "ffmpeg", "-y", "-v", "error", "-i", voice, "-i", music,
        "-filter_complex",
        "[1:a]volume=0.32[m];[m][0:a]sidechaincompress=threshold=0.025:ratio=8:attack=8:release=180[ducked];"
        "[0:a][ducked]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=8[a]",
        "-map", "[a]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", mixed,
    ])

    run([
        "ffmpeg", "-y", "-v", "error", "-i", base, "-i", mixed, "-t", str(TOTAL),
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", FINAL,
    ])

    (PROJECT / "scripts" / "visual-edl-v1.json").write_text(json.dumps(visual_manifest, indent=2) + "\n", encoding="utf-8")
    print(FINAL)


if __name__ == "__main__":
    main()
