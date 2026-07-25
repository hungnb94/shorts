#!/usr/bin/env python3
"""Render a 3-second Ronald Wayne rough hook for the blocking Hook Gate.

This is intentionally a rough-hook artifact, not the final Short. It uses four
semantic visual states at 0.75-second cadence, synthetic narration, an early
impact SFX, and a human face at frame zero.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "ronaldwayne"
SOURCE = PROJECT / "source"
WORK = PROJECT / "work" / "hook-c"
HOOKS = PROJECT / "hooks"
ANALYSIS = PROJECT / "analysis"
CHECKS = PROJECT / "checks"
BBC = SOURCE / "video" / "bvWh8sh_wPY.mp4"
APPLE_LOGO = SOURCE / "images" / "apple-first-logo.png"
APPLE1 = SOURCE / "images" / "apple1-public-domain.jpg"
CONTRACT = SOURCE / "images" / "contract-illustration.jpg"
TTS_RAW = PROJECT / "tts" / "hook_c_guy_raw.mp3"
TTS_WAV = WORK / "hook_c_guy.wav"
SFX = WORK / "impact.wav"
FONT = ROOT / "assets" / "fonts" / "Komika-Axis.ttf"
FINAL = HOOKS / "2026-07-25-ronaldwayne-hook-c.mp4"
FPS = 30
WIDTH = 1080
HEIGHT = 1920
BEAT = 1.5
TOTAL = 6.0


def run(cmd: list[str | Path]) -> None:
    print("+", " ".join(map(str, cmd)), flush=True)
    subprocess.run([str(x) for x in cmd], check=True)


def fit_cover(img: Image.Image, size: tuple[int, int], center_x: float = 0.5) -> Image.Image:
    tw, th = size
    scale = max(tw / img.width, th / img.height)
    nw, nh = round(img.width * scale), round(img.height * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = round((nw - tw) * center_x)
    top = max(0, (nh - th) // 2)
    return img.crop((left, top, left + tw, top + th))


def make_cards() -> tuple[Path, Path, Path]:
    frame = WORK / "wayne-120.jpg"
    run(["ffmpeg", "-y", "-v", "error", "-ss", "120", "-i", BBC, "-frames:v", "1", frame])

    # Beat 3: real Apple I hardware, public domain, instead of the unfamiliar first logo.
    bg = fit_cover(Image.open(APPLE1).convert("RGB"), (WIDTH, HEIGHT), center_x=0.5)
    bg = ImageEnhance.Brightness(bg).enhance(0.52)
    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    vd.rectangle((0, 0, WIDTH, 370), fill=(6, 9, 16, 178))
    vd.rectangle((0, 1470, WIDTH, HEIGHT), fill=(6, 9, 16, 190))
    bg = Image.alpha_composite(bg.convert("RGBA"), vignette).convert("RGB")
    apple_card = WORK / "apple-card.png"
    bg.save(apple_card)

    # Beat 3: contract illustration, explicitly not Apple's contract.
    contract = fit_cover(Image.open(CONTRACT).convert("RGB"), (WIDTH, HEIGHT), center_x=0.48)
    contract = ImageEnhance.Color(contract).enhance(0.35)
    contract = ImageEnhance.Contrast(contract).enhance(1.3)
    contract = ImageEnhance.Brightness(contract).enhance(0.42)
    contract_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (5, 8, 14, 80))
    cod = ImageDraw.Draw(contract_overlay)
    cod.rounded_rectangle((70, 1420, 1010, 1725), radius=34, fill=(7, 10, 17, 225), outline=(255, 86, 91, 255), width=6)
    contract = Image.alpha_composite(contract.convert("RGBA"), contract_overlay).convert("RGB")
    contract_card = WORK / "contract-card.png"
    contract.save(contract_card)

    # Beat 4: Wayne plus a visual risk model; these are illustrative icons, not evidence footage.
    src = Image.open(frame).convert("RGB")
    # Crop around Wayne's face while preserving some left-side lead room.
    src = src.crop((850, 0, 1458, 1080)).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    src = ImageEnhance.Brightness(src).enhance(0.48)
    src = ImageEnhance.Color(src).enhance(0.68)
    card = src.convert("RGBA")
    overlay = Image.new("RGBA", card.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    panel_y = 1210
    d.rounded_rectangle((70, panel_y, 1010, 1780), radius=42, fill=(8, 11, 18, 225), outline=(255, 203, 57, 255), width=6)
    # House icon.
    d.polygon([(150, 1450), (260, 1340), (370, 1450)], fill=(255, 214, 77, 255))
    d.rectangle((180, 1450, 340, 1615), fill=(245, 245, 245, 255))
    d.rectangle((245, 1510, 290, 1615), fill=(28, 35, 48, 255))
    # Car icon.
    d.rounded_rectangle((430, 1450, 670, 1585), radius=28, fill=(77, 180, 255, 255))
    d.polygon([(475, 1450), (525, 1375), (620, 1375), (660, 1450)], fill=(130, 215, 255, 255))
    for x in (485, 615):
        d.ellipse((x - 35, 1555, x + 35, 1625), fill=(14, 18, 25, 255))
    # Bank/account icon.
    d.polygon([(745, 1435), (875, 1350), (1005, 1435)], fill=(116, 245, 161, 255))
    d.rectangle((765, 1450, 985, 1490), fill=(116, 245, 161, 255))
    for x in (790, 850, 910, 970):
        d.rectangle((x, 1490, x + 24, 1595), fill=(230, 255, 238, 255))
    d.rectangle((755, 1595, 995, 1635), fill=(116, 245, 161, 255))
    # Creditor arrows descend toward the assets.
    for x in (260, 550, 875):
        d.line((x, 1240, x, 1320), fill=(255, 80, 90, 255), width=18)
        d.polygon([(x - 28, 1300), (x + 28, 1300), (x, 1340)], fill=(255, 80, 90, 255))
    card = Image.alpha_composite(card, overlay)
    risk_card = WORK / "risk-card.png"
    card.convert("RGB").save(risk_card)
    return apple_card, contract_card, risk_card


def centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    size: int,
    fill: tuple[int, int, int, int],
) -> None:
    font = ImageFont.truetype(str(FONT), size)
    draw.text(
        (WIDTH // 2, y), text, font=font, fill=fill, anchor="mm",
        stroke_width=max(5, size // 14), stroke_fill=(12, 17, 29, 255),
    )


def make_overlays() -> list[Path]:
    specs = [
        (("HE SOLD", 205, 112, (255, 255, 255, 255)), ("10% OF APPLE", 1640, 112, (114, 235, 77, 255))),
        (("SOLD FOR $800", 225, 126, (255, 203, 57, 255)), ("APPLE I - 1976", 1640, 92, (255, 255, 255, 255))),
        (("WORST TRADE", 220, 116, (255, 255, 255, 255)), ("EVER?", 1580, 176, (255, 86, 91, 255)), ("CONTRACT ILLUSTRATION", 1810, 34, (190, 198, 211, 255))),
        (("WHAT DID HE KNOW", 175, 82, (255, 203, 57, 255)), ("THAT WE DON'T?", 310, 82, (255, 255, 255, 255))),
    ]
    outputs: list[Path] = []
    for idx, lines in enumerate(specs):
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for text, y, size, color in lines:
            centered_text(draw, text, y, size, color)
        out = WORK / f"overlay-{idx}.png"
        overlay.save(out)
        outputs.append(out)
    return outputs


def render_visuals(apple_card: Path, contract_card: Path, risk_card: Path, overlays: list[Path]) -> Path:
    clips: list[Path] = []
    video_specs = [(120.0, 900)]
    for idx, (start, crop_x) in enumerate(video_specs):
        out = WORK / f"beat-{idx}.mp4"
        run([
            "ffmpeg", "-y", "-v", "error", "-ss", str(start), "-i", BBC,
            "-loop", "1", "-i", overlays[idx], "-t", str(BEAT), "-an",
            "-filter_complex", f"[0:v]crop=608:1080:{crop_x}:0,scale={WIDTH}:{HEIGHT}:flags=lanczos,fps={FPS}[bg];[1:v]format=rgba[ov];[bg][ov]overlay=0:0:shortest=1,format=yuv420p[v]",
            "-map", "[v]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-g", str(FPS), "-keyint_min", str(FPS),
            out,
        ])
        clips.append(out)
    for idx, card in enumerate((apple_card, contract_card, risk_card), start=1):
        out = WORK / f"beat-{idx}.mp4"
        run([
            "ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", card,
            "-loop", "1", "-i", overlays[idx], "-t", str(BEAT), "-an",
            "-filter_complex", f"[0:v]fps={FPS}[bg];[1:v]format=rgba[ov];[bg][ov]overlay=0:0:shortest=1,format=yuv420p[v]",
            "-map", "[v]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-g", str(FPS), "-keyint_min", str(FPS),
            out,
        ])
        clips.append(out)
    concat = WORK / "concat.txt"
    concat.write_text("".join(f"file '{p.resolve()}'\n" for p in clips), encoding="utf-8")
    base = WORK / "base.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat, "-c", "copy", base])
    return base


def make_audio() -> None:
    run([
        "ffmpeg", "-y", "-v", "error", "-i", TTS_RAW,
        f"-af", f"highpass=f=70,acompressor=threshold=0.1:ratio=3:attack=5:release=90:makeup=1,loudnorm=I=-16:TP=-1.5:LRA=8,aresample=48000,apad,atrim=0:{TOTAL}",
        "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", TTS_WAV,
    ])
    run([
        "ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
        "aevalsrc=(0.38*sin(2*PI*(180-100*t)*t)+0.16*sin(2*PI*620*t))*exp(-11*t):s=48000:d=0.5",
        "-af", "lowpass=f=2200,loudnorm=I=-18:TP=-2:LRA=6", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", SFX,
    ])


def finish(base: Path) -> None:
    run([
        "ffmpeg", "-y", "-v", "error", "-i", base, "-i", TTS_WAV, "-i", SFX,
        "-filter_complex",
        "[0:v]null[v];"
        f"[1:a]atrim=0:{TOTAL},asetpts=PTS-STARTPTS[vo];"
        f"[2:a]adelay=30|30,apad,atrim=0:{TOTAL},volume=0.42[sfx];"
        "[vo][sfx]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.94[a]",
        "-map", "[v]", "-map", "[a]", "-t", str(TOTAL),
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", FINAL,
    ])


def checks() -> None:
    probe = subprocess.run([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", FINAL
    ], check=True, capture_output=True, text=True).stdout
    (CHECKS / "hook-c-probe.json").write_text(probe, encoding="utf-8")
    run([
        "ffmpeg", "-y", "-v", "error", "-i", FINAL,
        "-vf", "fps=2,scale=270:480,tile=4x3:padding=4:margin=4", "-frames:v", "1",
        ANALYSIS / "hook-c-contact-sheet.jpg",
    ])
    run(["ffmpeg", "-v", "error", "-i", FINAL, "-f", "null", "-"])
    report = {
        "artifact": str(FINAL.relative_to(ROOT)),
        "duration_seconds": TOTAL,
        "visual_state_boundaries": [0.0, 1.5, 3.0, 4.5, 6.0],
        "max_visual_state_duration": 1.5,
        "frame_zero": "Ronald Wayne tight BBC interview crop",
        "tts": "Edge TTS en-US-GuyNeural +26%, pitch -8Hz",
        "caption_visible_at": 0.0,
        "early_sfx_at": 0.03,
        "naive_viewer_gate": "pending independent human response",
    }
    (CHECKS / "hook-c-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    for d in (WORK, HOOKS, ANALYSIS, CHECKS):
        d.mkdir(parents=True, exist_ok=True)
    for required in (BBC, APPLE_LOGO, APPLE1, CONTRACT, TTS_RAW, FONT):
        if not required.exists():
            raise FileNotFoundError(required)
    apple_card, contract_card, risk_card = make_cards()
    overlays = make_overlays()
    make_audio()
    base = render_visuals(apple_card, contract_card, risk_card, overlays)
    finish(base)
    checks()
    print(FINAL)


if __name__ == "__main__":
    main()
