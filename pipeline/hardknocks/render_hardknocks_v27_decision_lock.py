#!/usr/bin/env python3
"""Render HardKnocks V27: controlled 2-second decision-lock hook treatment.

This material revision preserves HardKnocks V26's exact source, audio, body,
CTA, proof order, SFX and payoff. Only the opening information design changes:
the viewer must mentally choose BUY or PASS before the 77M reveal lands on the
source's spoken reveal.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
V26_PATH = ROOT / "pipeline" / "hardknocks" / "render_hardknocks_v26_rejected_ten_percent.py"
_spec = importlib.util.spec_from_file_location("hardknocks_v26", V26_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Unable to import {V26_PATH}")
v26 = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = v26
_spec.loader.exec_module(v26)

PROJECT = ROOT / "output" / "projects" / "hardknocks"
WORK = PROJECT / "clips" / "v27_decision_lock_work"
HOOK_DIR = WORK / "hook_gate"
CHECKS = WORK / "checks"
OVERLAY = WORK / "overlay_v1_decision_lock.mov"
CANDIDATE = WORK / "candidate_v1_decision_lock.mp4"
FINAL = PROJECT / "final" / "2026-08-02-hardknocks_v27_decision_lock.mp4"
TIMELINE = WORK / "timeline.json"
SCORECARD = WORK / "hook-strategy-scorecard.json"

BASE = v26.BASE
SFX_TRACK = v26.SFX_TRACK
CAPTION_JSON = v26.CAPTION_JSON
FONT_KOMIKA = v26.FONT_KOMIKA
FONT_SANS = v26.FONT_SANS
OW = v26.OW
OH = v26.OH
FPS = v26.FPS
TOTAL_DURATION = v26.TOTAL_DURATION
ROUGH_DURATION = 3.0
SELECTED_VARIANT = "forced_prediction_lock"

HOOK_VARIANTS = (
    {
        "id": "forced_prediction_lock",
        "mechanism": "forced prediction + two-second countdown + delayed synchronized reveal",
        "copy": "BUY 10%? / $100K / DECISION LOCKED",
        "scores": {
            "curiosity_gap": 10,
            "specificity": 9,
            "visual": 9,
            "emotion": 8,
            "payoff": 10,
            "novelty": 10,
        },
    },
    {
        "id": "identity_challenge",
        "mechanism": "identity threat + founder self-test",
        "copy": "FOUNDER TEST / WOULD YOU PASS?",
        "scores": {
            "curiosity_gap": 9,
            "specificity": 9,
            "visual": 9,
            "emotion": 9,
            "payoff": 10,
            "novelty": 9,
        },
    },
    {
        "id": "mystery_ownership",
        "mechanism": "withheld outcome + ownership mystery",
        "copy": "THE 10% NOBODY WANTED",
        "scores": {
            "curiosity_gap": 10,
            "specificity": 8,
            "visual": 9,
            "emotion": 7,
            "payoff": 10,
            "novelty": 8,
        },
    },
)


@dataclass(frozen=True)
class Caption:
    start: float
    end: float
    text: str
    highlight: str


def run(command: list[str | Path]) -> None:
    print("+", " ".join(str(item) for item in command), flush=True)
    subprocess.run([str(item) for item in command], cwd=ROOT, check=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_captions() -> tuple[Caption, ...]:
    payload = json.loads(CAPTION_JSON.read_text(encoding="utf-8"))
    return tuple(
        Caption(
            start=float(item["start"]),
            end=min(TOTAL_DURATION, float(item["end"])),
            text=str(item["text"]),
            highlight=str(item["highlight"]),
        )
        for item in payload["bursts"]
    )


def fonts() -> dict[str, ImageFont.FreeTypeFont]:
    return {
        "caption": ImageFont.truetype(str(FONT_KOMIKA), 39),
        "evidence": ImageFont.truetype(str(FONT_KOMIKA), 27),
        "number": ImageFont.truetype(str(FONT_KOMIKA), 31),
        "hero": ImageFont.truetype(str(FONT_KOMIKA), 45),
        "small_bold": ImageFont.truetype(str(FONT_SANS), 17),
        "cta": ImageFont.truetype(str(FONT_SANS), 20),
        "row": ImageFont.truetype(str(FONT_SANS), 19),
        "tiny_bold": ImageFont.truetype(str(FONT_SANS), 13),
        "tiny": ImageFont.truetype(str(FONT_SANS), 10),
        "provenance": ImageFont.truetype(str(FONT_SANS), 12),
        "watermark": ImageFont.truetype(str(FONT_SANS), 13),
    }


def draw_button(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    label: str,
    font: ImageFont.FreeTypeFont,
    *,
    active: bool,
    accent: tuple[int, int, int, int],
) -> None:
    fill = (15, 53, 72, 238) if active else (19, 24, 34, 218)
    outline = accent if active else (112, 122, 138, 210)
    draw.rounded_rectangle(box, radius=18, fill=fill, outline=outline, width=3)
    draw.text(((box[0] + box[2]) // 2, (box[1] + box[3]) // 2), label, font=font, fill=(250, 252, 255, 255), anchor="mm")


def draw_countdown(draw: ImageDraw.ImageDraw, t: float, fonts_map: dict[str, ImageFont.FreeTypeFont]) -> None:
    cyan = (67, 212, 255, 255)
    amber = (255, 184, 77, 255)
    center = (466, 150)
    radius = 31
    local = min(1.0, max(0.0, t / 1.60))
    draw.ellipse((center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius), fill=(8, 13, 23, 230), outline=(110, 122, 140, 220), width=3)
    steps = 36
    active = max(1, round((1.0 - local) * steps))
    for index in range(active):
        angle = -math.pi / 2 + (math.tau * index / steps)
        x0 = center[0] + round((radius - 6) * math.cos(angle))
        y0 = center[1] + round((radius - 6) * math.sin(angle))
        x1 = center[0] + round(radius * math.cos(angle))
        y1 = center[1] + round(radius * math.sin(angle))
        draw.line((x0, y0, x1, y1), fill=cyan, width=3)
    number = "2" if t < 0.80 else "1" if t < 1.60 else "✓"
    draw.text(center, number, font=fonts_map["small_bold"], fill=amber if number != "✓" else cyan, anchor="mm")


def draw_forced_prediction(draw: ImageDraw.ImageDraw, t: float, f: dict[str, ImageFont.FreeTypeFont]) -> None:
    cyan = (67, 212, 255, 255)
    amber = (255, 184, 77, 255)
    green = (95, 225, 153, 255)
    red = (255, 92, 92, 255)
    white = (248, 250, 252, 255)

    if t < 1.60:
        v26.panel(draw, (26, 82, 514, 282), alpha=232)
        draw.text((270, 112), "YOU HAVE 2 SECONDS", font=f["small_bold"], fill=white, anchor="ma")
        draw.text((270, 166), "BUY 10%?", font=f["hero"], fill=amber, stroke_width=2, stroke_fill=(8, 10, 15, 255), anchor="mm")
        draw.text((270, 208), "PRICE  $100K", font=f["evidence"], fill=cyan, anchor="mm")
        draw_button(draw, (58, 231, 246, 277), "BUY", f["small_bold"], active=t >= 0.80, accent=green)
        draw_button(draw, (294, 231, 482, 277), "PASS", f["small_bold"], active=t < 0.80, accent=red)
        draw_countdown(draw, t, f)
    elif t < 4.57:
        v26.panel(draw, (54, 94, 486, 235), alpha=232)
        lock = v26.ease((t - 1.60) / 0.45)
        width = round(342 * lock)
        draw.rounded_rectangle((99, 126, 99 + width, 174), radius=14, fill=(18, 63, 82, 242), outline=cyan, width=3)
        draw.text((270, 150), "DECISION LOCKED", font=f["evidence"], fill=white, anchor="mm")
        draw.text((270, 208), "$100K  ↔  10%", font=f["number"], fill=amber, anchor="mm")
    elif t < 5.46:
        v26.panel(draw, (95, 104, 445, 218), alpha=235)
        draw.text((270, 136), "NOW REVEAL THE SCALE", font=f["small_bold"], fill=white, anchor="ma")
        pulse = 0.5 + 0.5 * math.sin((t - 4.57) * math.tau * 3.0)
        draw.rectangle((135, 182, 135 + round(270 * pulse), 194), fill=cyan)
    elif t < 7.70:
        v26.panel(draw, (68, 92, 472, 252), alpha=235)
        progress = v26.ease((t - 5.46) / 0.95)
        count = round(77 * progress)
        draw.text((270, 152), f"{count}M", font=f["hero"], fill=cyan, anchor="mm")
        draw.text((270, 204), "MONTHLY PLAYERS", font=f["evidence"], fill=white, anchor="mm")
        draw.text((270, 239), "WOULD YOU CHANGE YOUR VOTE?", font=f["tiny_bold"], fill=amber, anchor="ms")


def draw_identity_challenge(draw: ImageDraw.ImageDraw, t: float, f: dict[str, ImageFont.FreeTypeFont]) -> None:
    cyan = (67, 212, 255, 255)
    amber = (255, 184, 77, 255)
    red = (255, 92, 92, 255)
    white = (248, 250, 252, 255)
    v26.panel(draw, (52, 88, 488, 255), alpha=232)
    draw.text((270, 116), "FOUNDER TEST", font=f["small_bold"], fill=cyan, anchor="ma")
    draw.text((270, 166), "WOULD YOU PASS?", font=f["hero"], fill=white, anchor="mm")
    draw.text((270, 214), "$100K FOR 10%", font=f["evidence"], fill=amber, anchor="mm")
    if t >= 1.45:
        angle = -10 + 4 * math.sin(t * 8)
        stamp = Image.new("RGBA", (210, 80), (0, 0, 0, 0))
        stamp_draw = ImageDraw.Draw(stamp, "RGBA")
        stamp_draw.rounded_rectangle((4, 4, 206, 76), radius=10, outline=red, width=6)
        stamp_draw.text((105, 40), "NO BUYERS", font=f["evidence"], fill=red, anchor="mm")
        stamp = stamp.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
        draw.bitmap((270 - stamp.width // 2, 250), stamp, fill=None)


def draw_mystery_ownership(draw: ImageDraw.ImageDraw, t: float, f: dict[str, ImageFont.FreeTypeFont]) -> None:
    cyan = (67, 212, 255, 255)
    amber = (255, 184, 77, 255)
    red = (255, 92, 92, 255)
    white = (248, 250, 252, 255)
    v26.panel(draw, (48, 90, 492, 255), alpha=232)
    draw.text((270, 120), "THE 10%", font=f["hero"], fill=amber, anchor="ma")
    draw.text((270, 174), "NOBODY WANTED", font=f["evidence"], fill=white, anchor="mm")
    draw.line((121, 214, 419, 214), fill=(120, 132, 148, 220), width=4)
    progress = v26.ease(min(1.0, t / 1.6))
    draw.line((121, 214, 121 + round(298 * progress), 214), fill=cyan, width=8)
    if t >= 1.60:
        draw.text((270, 242), "$100K ASK  →  REJECTED", font=f["small_bold"], fill=red, anchor="ms")


def draw_variant_hook(
    draw: ImageDraw.ImageDraw,
    t: float,
    variant: str,
    f: dict[str, ImageFont.FreeTypeFont],
) -> None:
    if variant == "forced_prediction_lock":
        draw_forced_prediction(draw, t, f)
    elif variant == "identity_challenge":
        draw_identity_challenge(draw, t, f)
    elif variant == "mystery_ownership":
        draw_mystery_ownership(draw, t, f)
    else:
        raise ValueError(variant)


def build_overlay(output: Path, captions: tuple[Caption, ...], *, duration: float, variant: str, full: bool) -> None:
    f = fonts()
    command = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "qtrle", "-pix_fmt", "argb", output,
    ]
    process = subprocess.Popen([str(item) for item in command], stdin=subprocess.PIPE, cwd=ROOT)
    if process.stdin is None:
        raise RuntimeError("Could not open ffmpeg overlay stdin")
    for frame in range(round(duration * FPS)):
        t = frame / FPS
        image = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image, "RGBA")
        if full and t >= 7.70:
            v26.draw_story_ui(draw, t, f)
        else:
            draw_variant_hook(draw, t, variant, f)
        caption = next((item for item in captions if item.start <= t < item.end), None)
        if caption is not None:
            caption_y = 600 if full and 38.70 <= t < 42.20 else 575
            v26.draw_centered_tokens(draw, caption_y, caption.text, caption.highlight, f["caption"])
        route = 0.5 - 0.5 * math.cos(2 * math.pi * min(1.0, t / TOTAL_DURATION) * 2.0)
        wx = 18 + round(route * 350)
        wy = 32 if t < TOTAL_DURATION / 2 else 58
        if full and 49.40 <= t < 56.60:
            wx, wy = 390, 18
        draw.text(
            (wx, wy),
            "@MONEY BLINDSPOT",
            font=f["watermark"],
            fill=(255, 255, 255, 120),
            stroke_width=1,
            stroke_fill=(0, 0, 0, 125),
        )
        progress_duration = TOTAL_DURATION if full else duration
        draw.rectangle((0, OH - 4, round(OW * t / progress_duration), OH), fill=(255, 69, 0, 255))
        process.stdin.write(image.tobytes())
    process.stdin.close()
    code = process.wait()
    if code != 0:
        raise subprocess.CalledProcessError(code, command)


def mux(base: Path, overlay: Path, output: Path, *, duration: float) -> None:
    run(
        [
            "ffmpeg", "-y", "-v", "error", "-i", base, "-i", overlay, "-i", SFX_TRACK,
            "-filter_complex",
            "[1:v]scale=1080:1920:flags=lanczos,format=rgba[ov];"
            f"[0:v]trim=0:{duration:.6f},setpts=PTS-STARTPTS[basev];"
            "[basev][ov]overlay=x=0:y=0:format=auto:shortest=0:eof_action=repeat[v];"
            f"[0:a]atrim=0:{duration:.6f},asetpts=PTS-STARTPTS[basea];"
            f"[2:a]atrim=0:{duration:.6f},asetpts=PTS-STARTPTS[sfx];"
            "[basea][sfx]amix=inputs=2:duration=first:normalize=0,"
            "volume=-0.7dB,alimiter=limit=0.84:level=false[a]",
            "-map", "[v]", "-map", "[a]", "-frames:v", str(round(duration * FPS)), "-t", f"{duration:.6f}",
            "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
            "-r", str(FPS), "-fps_mode", "cfr", "-g", "60", "-sc_threshold", "0",
            "-video_track_timescale", "90000", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            output,
        ]
    )


def write_scorecard() -> None:
    rows = []
    for item in HOOK_VARIANTS:
        row = dict(item)
        row["total"] = sum(int(value) for value in item["scores"].values())
        rows.append(row)
    rows.sort(key=lambda item: (int(item["total"]), int(item["scores"]["curiosity_gap"])), reverse=True)
    if rows[0]["id"] != SELECTED_VARIANT:
        raise RuntimeError("Deterministic hook scoring no longer selects the configured winner")
    payload = {
        "objective": "real YouTube Studio Stayed to Watch target 80%; goal, not forecast",
        "primary_metric_after_48h": "real YouTube Studio Stayed to Watch with sufficient Shorts Feed exposure",
        "frozen_layers": [
            "source and source-audio boundaries",
            "body edit from 7.70s onward",
            "captions and narration",
            "proof order and claims",
            "SFX assets and timing",
            "CTA and payoff",
            "canonical title and description",
        ],
        "changed_layer": "opening visual-information strategy from 0.00s to 7.70s",
        "variants": rows,
        "selected": SELECTED_VARIANT,
        "selection_rule": "highest six-criterion total; curiosity gap is the tie-breaker",
        "hypothesis": "A forced two-second prediction followed by a source-synchronized delayed reveal will improve hook acceptance without reducing body retention.",
        "falsification": "After sufficient feed exposure and >=48h, fail the net-win hypothesis if Stayed to Watch does not improve against a comparable same-lane baseline or if 0-10s retention/AVD materially regresses.",
    }
    SCORECARD.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_roughs(captions: tuple[Caption, ...]) -> None:
    HOOK_DIR.mkdir(parents=True, exist_ok=True)
    for item in HOOK_VARIANTS:
        variant = str(item["id"])
        overlay = HOOK_DIR / f"{variant}.mov"
        output = HOOK_DIR / f"rough_hook_{variant}.mp4"
        build_overlay(overlay, captions, duration=ROUGH_DURATION, variant=variant, full=False)
        mux(BASE, overlay, output, duration=ROUGH_DURATION)


def build_full(captions: tuple[Caption, ...]) -> None:
    build_overlay(OVERLAY, captions, duration=TOTAL_DURATION, variant=SELECTED_VARIANT, full=True)
    mux(BASE, OVERLAY, CANDIDATE, duration=TOTAL_DURATION)
    source_timeline = json.loads(v26.TIMELINE_PATH.read_text(encoding="utf-8"))
    source_timeline["material_revision"] = {
        "from": "HardKnocks V26",
        "changed_window": [0.0, 7.70],
        "changed_layer": "visual hook information design only",
        "strategy": SELECTED_VARIANT,
        "source_audio_changed": False,
        "body_after_7_70_changed": False,
    }
    source_timeline["hook_variants"] = [
        {**item, "total": sum(int(value) for value in item["scores"].values())}
        for item in HOOK_VARIANTS
    ]
    source_timeline["captions"] = [asdict(item) for item in captions]
    TIMELINE.write_text(json.dumps(source_timeline, indent=2) + "\n", encoding="utf-8")


def promote() -> None:
    if not CANDIDATE.is_file():
        raise FileNotFoundError(CANDIDATE)
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CANDIDATE, FINAL)
    manifest = {
        "final": str(FINAL.relative_to(ROOT)),
        "final_sha256": sha256(FINAL),
        "candidate": str(CANDIDATE.relative_to(ROOT)),
        "candidate_sha256": sha256(CANDIDATE),
        "base": str(BASE.relative_to(ROOT)),
        "base_sha256": sha256(BASE),
        "source_v26_final": str(v26.FINAL.relative_to(ROOT)),
        "source_v26_final_sha256": sha256(v26.FINAL),
        "selected_hook": SELECTED_VARIANT,
    }
    (WORK / "render-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if manifest["final_sha256"] != manifest["candidate_sha256"]:
        raise RuntimeError("Promoted final does not match candidate bytes")
    print(FINAL)


def validate_inputs() -> None:
    required = [BASE, SFX_TRACK, CAPTION_JSON, FONT_KOMIKA, FONT_SANS, v26.TIMELINE_PATH, v26.FINAL]
    missing = [path for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing V26 controls:\n" + "\n".join(str(path) for path in missing))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roughs", action="store_true")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--promote", action="store_true")
    parser.add_argument("--all", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not any((args.roughs, args.render, args.promote, args.all)):
        raise SystemExit("Choose --roughs, --render, --promote or --all")
    validate_inputs()
    WORK.mkdir(parents=True, exist_ok=True)
    CHECKS.mkdir(parents=True, exist_ok=True)
    captions = load_captions()
    write_scorecard()
    if args.roughs or args.all:
        build_roughs(captions)
    if args.render or args.all:
        build_full(captions)
    if args.promote or args.all:
        promote()


if __name__ == "__main__":
    main()
