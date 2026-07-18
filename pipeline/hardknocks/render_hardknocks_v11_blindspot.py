#!/usr/bin/env python3
"""Render HardKnocks V11 — "3 Things Every Man Wants" (Blindspot v2).

Implements docs/specs/2026-07-18-hardknocks-blindspot-verification-layer-design.md
"Revision 2". Subject: Ben Pogue (source rrDdi0vZn00, School of Hard Knocks).

Concept: "Every man wants three things. Does this millionaire really have them?"
Score him on WEALTH / FREEDOM / LEGACY, each verified against an INDEPENDENT
source (never SOHK) with a TRUE / UNVERIFIED / HALF-TRUE verdict.

Structure:
- Opening branded card: blurred Pogue portrait -> reveal ~3.5s; panel lists the
  3 criteria; "?/3" finale; Qwen narrator VO (natural_talker_male_qwen_blog).
- Interview body: captions rebuilt from ASR word-timing (2-4 word bursts at ~60%
  height); hard-cut punch-in reframe centring the active speaker (ADR-0030);
  inline split-screen verify panels (face stays visible on top, 1-3 independent
  source screenshots slide in on the bottom half with a keyword highlight) fire
  right at each checkable claim, with a ting/buzzer/uncertain stinger, while the
  interview audio keeps playing underneath; small "LESSON" pills weave in the
  business-value takeaways.
- Ending: one continuous Qwen VO ("Wealth, real. Freedom, real. Legacy? Only
  half...") drives a single sequence -- score card with a row-by-row highlight
  per criterion, cut to the LEGACY evidence reveal (not shown inline) on "he
  gave the company... his dad built it", a LESSON recap pill, then the CTA card
  (comment prompt, itself spoken by the VO).

Sourcing rule (ADR-aligned): SOHK is raw footage, never a verification source.
"""

from __future__ import annotations

import json
import math
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "hardknocks"
SOURCE = PROJECT / "source" / "rrDdi0vZn00.webm"
BRANDING = ROOT / "output" / "shared" / "hardknocks_branding"
WORK = PROJECT / "clips" / "v11_work"
PANELS = WORK / "panels"
CHECKS = WORK / "checks"
SHOTS = WORK / "source_shots"
FINAL = PROJECT / "final" / "2026-07-18-hardknocks_v11_blindspot_ben_pogue.mp4"

FONT_REGULAR = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
FONT_BLACK = Path("/System/Library/Fonts/Supplemental/Arial Black.ttf")

WIDTH = 1080
HEIGHT = 1920
FPS = 30
POST_SPEED = 1.19

GREEN = "#00D66E"
RED = "#FF4D4D"
YELLOW = "#FFD23C"
BLUE = "#4FC3F7"
DARK = "#0B0E14"

# Active-Speaker Reframing (ADR-0030): Pogue sits LEFT, host sits RIGHT.
POGUE_FOCUS = 0.28   # horizontal crop position that centres Pogue
HOST_FOCUS = 0.64    # ... and the host
ASR_MODEL = "mlx-community/whisper-small-mlx"

# --- Opening branded scoring-card ---
OPENING_FRAME_T = 1360.0
OPENING_CROP = "crop=900:1600:840:214,scale=1080:1920:flags=lanczos"
CARD_REVEAL_AT = 3.5
CARD_PANEL_H = 1150
CARD_GREEN = (0, 214, 110, 255)
CARD_WHITE = (255, 255, 255, 255)
CARD_CRITERIA = ("1. WEALTH", "2. FREEDOM", "3. LEGACY")
OPENING_VO_TEXT = "Every man wants three things. Does he really have them? Let's check."
OPENING_VO = WORK / "audio" / "opening_vo_qwen.wav"

# --- Ending: single VO-driven sequence (score card -> LEGACY reveal -> CTA) ---
ENDING_VO_TEXT = (
    "Final scorecard. Wealth, real. Freedom, real. Legacy? Only half. He gave the "
    "company to his employees, but his dad built it. The lesson: he bought the jet "
    "used, and grew what he already had. So, what's your score? Comment below."
)
ENDING_VO = WORK / "audio" / "ending_vo_qwen.wav"
# Keyframes (seconds into the VO) verified via ASR word-timing on ending_vo_qwen.wav.
ENDING_T_WEALTH = 1.82  # "Wealth" -- after the "Final scorecard." lead-in beat
ENDING_T_FREEDOM = 3.4
ENDING_T_LEGACY = 4.96
ENDING_T_DAD = 6.98     # "He gave the company..." -> cut to LEGACY evidence reveal
ENDING_T_LESSON = 10.32 # "The lesson..." -> small recap pill over the evidence
ENDING_T_CTA = 13.9     # "So, what's your score?" -> cut to CTA card
ENDING_TAIL = 1.6       # hold after VO ends so the CTA card can breathe


@dataclass(frozen=True)
class Segment:
    name: str
    source_start: float
    source_end: float
    # Hard-cut speaker turns (segment-relative seconds, speaker): the crop jumps
    # to centre whoever is speaking (punch-in reframe). First turn starts at 0.
    # (segment-relative start seconds, crop focus 0..1) per speaker turn. Focus
    # is per-segment because the seating/standing layout differs across the
    # interview (in the jet-tour price segment the host is on the LEFT and Pogue
    # centre-right; in the seated segments Pogue is on the LEFT).
    turns: tuple[tuple[float, float], ...]
    zoom: float = 1.06


@dataclass(frozen=True)
class SourceRef:
    png: str
    crop: tuple[int, int, int, int]        # x,y,w,h in the original screenshot
    highlight: tuple[int, int, int, int]   # x,y,w,h RELATIVE to the crop (yellow marker)
    outlet: str


@dataclass(frozen=True)
class InlineVerify:
    """Split-screen inline verify: face stays on top, source(s) slide in on the
    bottom half while the interview audio keeps running (+ ting/buzzer/uncertain
    sound). 1-3 independent sources per claim; UNVERIFIED shows the absence."""
    segment: str
    at: float              # segment-relative seconds
    verdict: str           # "true" | "false" | "unverified"
    claim: str
    sources: tuple[SourceRef, ...] = ()
    note: str = ""         # shown when unverified (no source)
    duration: float = 2.8


@dataclass(frozen=True)
class Lesson:
    """Woven-in business takeaway (value layer)."""
    segment: str
    at: float
    text: str
    duration: float = 2.6


@dataclass(frozen=True)
class Evidence:
    """LEGACY blindspot reveal at the end (not claimed inline)."""
    criterion: str
    verdict: str       # "true" | "half"
    claim: str
    key_stat: str
    outlet: str
    url: str
    shots: tuple[tuple[str, tuple[int, int, int, int]], ...]


SEGMENTS = (
    Segment("price_reveal", 1213.68, 1223.70,   # standing: host LEFT, Pogue centre-right
            # end extended to let "...probably about 20." finish (word ends 1223.60)
            ((0.0, 0.22), (1.9, 0.52)), zoom=1.06),
    Segment("identity", 1233.26, 1235.12,        # seated: host RIGHT, Pogue LEFT
            ((0.0, 0.64), (1.0, 0.28)), zoom=1.05),
    Segment("billions_reveal", 1235.38, 1246.90,
            ((0.0, 0.64), (2.0, 0.28)), zoom=1.05),
    Segment("competitive_edge", 1249.52, 1260.62,
            # start moved back to the lead-in ("Construction is a very competitive
            # business to be in...") instead of starting mid-thought; host asks,
            # Pogue answers at "Man," (word starts 1255.84, i.e. t=6.32 relative)
            ((0.0, 0.64), (6.32, 0.28)), zoom=1.05),
    Segment("money_reveal", 1340.00, 1353.52,
            ((0.0, 0.64), (2.6, 0.28)), zoom=1.05),
    # The sacrifice arc (1353.52-1371.00) was dropped to fit the <=60s Shorts cap
    # at natural 1.1x speed: it is the largest off-thesis block (not one of the
    # WEALTH/FREEDOM/LEGACY criteria) and carries no verify stamp.
)

# Inline split-screen verifies: source shown right at the claim (independent
# sources only, never SOHK). Crop/highlight boxes verified against the saved
# screenshots at Stage 0.
INLINE = (
    InlineVerify(
        "price_reveal", 7.4, "true", "JET: ~$20M ALL-IN",
        (SourceRef("freedom_blackjet_g550.png", (80, 838, 1060, 96), (605, 0, 280, 28), "BLACKJET"),
         SourceRef("freedom_privatejetcard.png", (20, 1740, 820, 80), (345, 34, 110, 34), "PRIVATE JET CARD COMPARISONS")),
    ),
    InlineVerify(
        "money_reveal", 4.2, "unverified", "$200M / YEAR — PERSONAL",
        note="0 PUBLIC RECORDS FOUND",
    ),
    InlineVerify(
        "money_reveal", 11.0, "true", "COMPANY: $1.5B REVENUE",
        (SourceRef("wealth_legacy_pilothill.png", (40, 900, 1100, 140), (285, 90, 130, 32), "PILOT HILL ADVISORS"),),
        duration=2.4,  # money_reveal is the last segment; keep the panel inside its 13.53s span
    ),
)

# Woven-in business value (LESSON) overlays.
LESSONS = (
    Lesson("price_reveal", 3.2, "BUY USED: he saved ~$30M vs new"),
    Lesson("billions_reveal", 6.5, "SCALE what exists -- don't start at zero"),
    Lesson("money_reveal", 7.5, "REVENUE isn't take-home. Volume != wealth"),
)

# LEGACY blindspot reveal at the end (not claimed inline).
EVIDENCE = (
    Evidence(
        "LEGACY", "half",
        "CHARITY & GIVING BACK",
        "$330M FOUNDATION  --  BUT FOUNDER (FATHER): TAX FRAUD",
        "PROPUBLICA  +  2010 FEDERAL TAX-FRAUD PLEA", "propublica.org / court record",
        (("legacy_charity_propublica.png", (0, 0, 1200, 900)),
         ("legacy_taxfraud_chuckg_backup.png", (190, 205, 555, 280))),
    ),
)

# Closing score card (3 rows). verdict: True / False / "half".
SCORE_CRITERIA = (
    ("1. WEALTH", True, "PILOT HILL: $1.5B REVENUE"),
    ("2. FREEDOM", True, "BLACKJET: USED G550 $11-35M"),
    ("3. LEGACY", "half", "PROPUBLICA + GCR: CHARITY vs FATHER'S FRAUD"),
)
SCORE_LABEL = "2 / 3"
SCORE_SUBJECT = "SUBJECT: BEN POGUE - POGUE CONSTRUCTION"
CTA_TEXT = "What's YOUR score?"
CTA_SUB = "Comment it below"


def run(args: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(str(a) for a in args), flush=True)
    return subprocess.run([str(a) for a in args], cwd=ROOT, check=True, text=True, capture_output=capture)


def probe(path: Path) -> dict[str, Any]:
    result = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)], capture=True)
    return json.loads(result.stdout)


def frames_for(seconds: float) -> int:
    return max(1, round(seconds * FPS))


def encode_args() -> list[str]:
    return ["-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p", "-r", str(FPS)]


# ---------------------------------------------------------------------------
# Segment rendering with hard-cut speaker reframe
# ---------------------------------------------------------------------------

def crop_expr(turns: tuple[tuple[float, float], ...]) -> str:
    span = 3414 - WIDTH  # 2334
    def xf(focus: float) -> int:
        return round(span * focus)
    expr = str(xf(turns[-1][1]))
    for i in range(len(turns) - 2, -1, -1):
        boundary = turns[i + 1][0]
        expr = f"if(lt(t,{boundary:.3f}),{xf(turns[i][1])},{expr})"
    return expr


def scaled_crop(turns: tuple[tuple[float, float], ...], zoom: float) -> str:
    # Scale 4K source to 1920 height (3414 wide), hard-crop 1080x1920 with the
    # crop-x jumping between speakers, then a light centre zoom.
    x_expr = crop_expr(turns)
    zoom_width = round(WIDTH * zoom)
    zoom_height = round(HEIGHT * zoom)
    return (
        f"scale=3414:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:'{x_expr}':0,"
        f"scale={zoom_width}:{zoom_height}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:(in_w-{WIDTH})/2:0,"
        "eq=contrast=1.05:saturation=1.05,setsar=1,format=yuv420p"
    )


def render_segment(segment: Segment, output: Path) -> int:
    duration = segment.source_end - segment.source_start
    frame_count = frames_for(duration)
    audio_filter = (
        "highpass=f=70,acompressor=threshold=0.125:ratio=2.0:attack=5:release=80:makeup=1.5,"
        f"loudnorm=I=-16:TP=-1.5:LRA=10,aresample=48000:first_pts=0,apad,atrim=0:{duration:.6f}"
    )
    crop = scaled_crop(segment.turns, segment.zoom)
    run([
        "ffmpeg", "-y", "-v", "error", "-ss", f"{segment.source_start:.6f}", "-i", str(SOURCE),
        "-t", f"{duration:.6f}", "-vf", f"{crop},fps={FPS}",
        "-af", audio_filter, "-frames:v", str(frame_count), *encode_args(),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(output),
    ])
    return frame_count


def build_base(work: Path) -> tuple[Path, list[dict[str, Any]], int]:
    clips = work / "segments"
    clips.mkdir(parents=True, exist_ok=True)
    timeline: list[dict[str, Any]] = []
    cursor = 0
    outputs: list[Path] = []
    for index, segment in enumerate(SEGMENTS):
        output = clips / f"{index:02d}_{segment.name}.mp4"
        count = render_segment(segment, output)
        timeline.append({
            "name": segment.name, "start_frame": cursor, "frames": count,
            "end_frame": cursor + count, "source_start": segment.source_start,
            "source_end": segment.source_end,
        })
        cursor += count
        outputs.append(output)
        if segment.source_end - segment.source_start >= 15:
            raise ValueError(f"source clip reaches 15 seconds: {segment.name}")
    concat = work / "concat.txt"
    concat.write_text("".join(f"file '{p.resolve()}'\n" for p in outputs), encoding="utf-8")
    base = work / "base.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(base)])
    return base, timeline, cursor


# ---------------------------------------------------------------------------
# PIL drawing helpers
# ---------------------------------------------------------------------------

def star_points(cx: float, cy: float, outer_r: float, inner_r: float) -> list[tuple[float, float]]:
    pts = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        r = outer_r if i % 2 == 0 else inner_r
        pts.append((cx + r * math.cos(angle), cy - r * math.sin(angle)))
    return pts


def outlined_text(d, xy, text, font, fill, outline_w=5, anchor="mm") -> None:
    x, y = xy
    if outline_w > 0:
        for dx in range(-outline_w, outline_w + 1):
            for dy in range(-outline_w, outline_w + 1):
                if dx * dx + dy * dy <= outline_w * outline_w:
                    d.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0, 255), anchor=anchor)
    d.text((x, y), text, font=font, fill=fill, anchor=anchor)


def outline_star(d, cx, cy, outer_r, inner_r, outline, width=4) -> None:
    d.polygon(star_points(cx, cy, outer_r + 2, inner_r + 2), outline=(0, 0, 0, 255), width=width + 4)
    d.polygon(star_points(cx, cy, outer_r, inner_r), outline=outline, width=width)


def fill_star(d, cx, cy, outer_r, inner_r, colour) -> None:
    d.polygon(star_points(cx, cy, outer_r, inner_r), fill=colour, outline=colour)


# ---------------------------------------------------------------------------
# Opening branded scoring card (3 criteria)
# ---------------------------------------------------------------------------

def _card_logo(panels: Path, size: int = 96) -> Path:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = 6
    d.arc([pad, pad, size - pad, size - pad], start=25, end=320, fill=(0, 0, 0, 255), width=13)
    d.arc([pad, pad, size - pad, size - pad], start=25, end=320, fill=CARD_GREEN, width=9)
    f = ImageFont.truetype(str(FONT_BLACK), int(size * 0.42))
    outlined_text(d, (size / 2, size / 2 + 2), "$", f, CARD_WHITE, outline_w=3, anchor="mm")
    path = panels / "card_logo.png"
    img.save(path)
    return path


def make_card_brand(panels: Path) -> Path:
    logo = Image.open(_card_logo(panels))
    img = Image.new("RGBA", (560, 110), (0, 0, 0, 0))
    img.paste(logo, (0, 7), logo)
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(str(FONT_BLACK), 36)
    outlined_text(d, (118, 55), "MONEY BLINDSPOT", f, CARD_GREEN, outline_w=4, anchor="lm")
    path = panels / "card_brand.png"
    img.save(path)
    return path


def make_card_header(panels: Path) -> Path:
    img = Image.new("RGBA", (WIDTH, 130), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fh = ImageFont.truetype(str(FONT_BLACK), 50)
    part1, part2 = "SCORING ", "THIS MILLIONAIRE"
    total_w = d.textlength(part1 + part2, font=fh)
    x0 = WIDTH / 2 - total_w / 2
    w1 = d.textlength(part1, font=fh)
    outlined_text(d, (x0 + w1 / 2, 65), part1.strip(), fh, CARD_WHITE, outline_w=5, anchor="mm")
    outlined_text(d, (x0 + w1 + d.textlength(part2, font=fh) / 2, 65), part2, fh, CARD_GREEN, outline_w=5, anchor="mm")
    path = panels / "card_header.png"
    img.save(path)
    return path


def make_card_row(panels: Path, i: int, item: str) -> Path:
    img = Image.new("RGBA", (1000, 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    num, label = item.split(". ", 1)
    fnum = ImageFont.truetype(str(FONT_BLACK), 66)
    flabel = ImageFont.truetype(str(FONT_BLACK), 60)
    outlined_text(d, (12, 75), f"{num}.", fnum, CARD_GREEN, outline_w=5, anchor="lm")
    outlined_text(d, (110, 75), label, flabel, CARD_WHITE, outline_w=5, anchor="lm")
    path = panels / f"card_row_{i}.png"
    img.save(path)
    return path


def make_card_star(panels: Path, i: int) -> Path:
    img = Image.new("RGBA", (150, 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    outline_star(d, 75, 75, 40, 16, outline=CARD_GREEN, width=6)
    path = panels / f"card_star_{i}.png"
    img.save(path)
    return path


def make_card_finale(panels: Path) -> Path:
    img = Image.new("RGBA", (900, 160), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fq = ImageFont.truetype(str(FONT_BLACK), 88)
    outlined_text(d, (110, 80), "?/3", fq, CARD_WHITE, outline_w=6, anchor="mm")
    for i in range(3):
        outline_star(d, 320 + i * 95, 80, 40, 16, outline=CARD_GREEN, width=6)
    path = panels / "card_finale.png"
    img.save(path)
    return path


def make_pop_sfx(work: Path) -> Path:
    out = work / "card_pop.wav"
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "sine=frequency=700:duration=0.16",
         "-af", "afade=t=in:d=0.015,afade=t=out:st=0.09:d=0.07,volume=0.55",
         "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(out)])
    return out


def render_opening_card(work: Path, panels: Path, vo: Path) -> tuple[Path, int]:
    vo_dur = float(probe(vo)["format"]["duration"])
    n = len(CARD_CRITERIA)
    header_start, text_start = 0.15, 0.35
    star_start0, star_gap = 0.80, 0.28
    finale_start = star_start0 + (n - 1) * star_gap + 0.4
    total_dur = round(max(vo_dur + 0.45, finale_start + 1.2), 2)
    frame_count = frames_for(total_dur)

    portrait = panels / "opening_portrait.png"
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{OPENING_FRAME_T:.3f}", "-i", str(SOURCE),
         "-frames:v", "1", "-vf", f"{OPENING_CROP},setsar=1", str(portrait)])
    base = work / "card_base.mp4"
    vf = (
        f"fps={FPS},split=2[sharp][toblur];"
        "[toblur]boxblur=18:2[blurred];"
        f"[blurred][sharp]xfade=transition=fade:duration=0.5:offset={CARD_REVEAL_AT - 0.25:.3f},"
        "eq=contrast=1.05:saturation=1.05,setsar=1,format=yuv420p"
    )
    run([
        "ffmpeg", "-y", "-v", "error", "-loop", "1", "-t", f"{total_dur:.3f}", "-i", str(portrait),
        "-filter_complex", vf, "-frames:v", str(frame_count), "-an", *encode_args(), str(base),
    ])

    brand = make_card_brand(panels)
    header = make_card_header(panels)
    rows = [make_card_row(panels, i, item) for i, item in enumerate(CARD_CRITERIA)]
    stars = [make_card_star(panels, i) for i in range(n)]
    finale = make_card_finale(panels)
    pop = make_pop_sfx(work)

    pngs = (brand, header, *rows, *stars, finale)
    inputs = ["-i", str(base)]
    for p in pngs:
        inputs += ["-loop", "1", "-t", f"{total_dur:.3f}", "-i", str(p)]

    panel_y0 = HEIGHT - CARD_PANEL_H
    row_y0 = panel_y0 + 320
    row_gap = 175

    def f(x: float) -> str:
        return f"{x:.3f}"

    filt = []
    panel_y = f"if(lt(t,0.28), {panel_y0}+130*(1-t/0.28), {panel_y0})"
    filt.append(f"[0:v]drawbox=x=0:y='{panel_y}':w=iw:h={CARD_PANEL_H + 140}:color=0x08090e@0.9:t=fill[s0]")
    last, idx = "s0", 1
    filt.append(f"[{idx}:v]format=rgba,fade=t=in:st={f(header_start - 0.05)}:d=0.2:alpha=1[brandf]")
    filt.append(f"[{last}][brandf]overlay=x=40:y={panel_y0 + 50}:enable='gte(t,{f(header_start - 0.05)})'[s1]")
    last, idx = "s1", idx + 1
    filt.append(f"[{idx}:v]format=rgba,fade=t=in:st={f(header_start)}:d=0.2:alpha=1[hdrf]")
    filt.append(f"[{last}][hdrf]overlay=x=0:y={panel_y0 + 175}:enable='gte(t,{f(header_start)})'[s2]")
    last, idx = "s2", idx + 1
    for i in range(n):
        filt.append(f"[{idx + i}:v]format=rgba,fade=t=in:st={f(text_start)}:d=0.2:alpha=1[txt{i}]")
        filt.append(f"[{last}][txt{i}]overlay=x=55:y={row_y0 + i * row_gap}:enable='gte(t,{f(text_start)})'[rt{i}]")
        last = f"rt{i}"
    idx += n
    for i in range(n):
        st = star_start0 + i * star_gap
        filt.append(f"[{idx + i}:v]format=rgba,fade=t=in:st={f(st)}:d=0.15:alpha=1[st{i}]")
        filt.append(f"[{last}][st{i}]overlay=x=860:y={row_y0 + i * row_gap - 2}:enable='gte(t,{f(st)})'[so{i}]")
        last = f"so{i}"
    idx += n
    finale_y = row_y0 + n * row_gap + 40
    filt.append(f"[{idx}:v]format=rgba,fade=t=in:st={f(finale_start)}:d=0.25:alpha=1[finf]")
    filt.append(f"[{last}][finf]overlay=x=(W-w)/2:y={finale_y}:enable='gte(t,{f(finale_start)})'[vout]")

    vo_idx = 1 + len(pngs)
    pop_idx = vo_idx + 1
    afilt = (
        f"[{vo_idx}:a]aresample=48000,aformat=channel_layouts=stereo,adelay=120|120,"
        "loudnorm=I=-16:TP=-1.5:LRA=10[voa];"
        f"[{pop_idx}:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.55[popa];"
        "[voa][popa]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.94[aout]"
    )
    script = work / "card.ffscript"
    script.write_text(";\n".join(filt) + ";\n" + afilt + "\n", encoding="utf-8")

    out = work / "opening_card.mp4"
    run([
        "ffmpeg", "-y", "-v", "error", *inputs, "-i", str(vo), "-i", str(pop),
        "-filter_complex_script", str(script), "-map", "[vout]", "-map", "[aout]",
        "-frames:v", str(frame_count), *encode_args(),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(out),
    ])
    return out, frame_count


# ---------------------------------------------------------------------------
# Inline split-screen verify (source on bottom half) + LESSON overlays
# ---------------------------------------------------------------------------

INLINE_PANEL_H = 940


def make_source_panel(panels: Path, ev: InlineVerify) -> Path:
    img = Image.new("RGBA", (WIDTH, INLINE_PANEL_H), (10, 13, 20, 244))
    d = ImageDraw.Draw(img)
    acc = {"true": GREEN, "false": RED, "unverified": YELLOW}[ev.verdict]
    d.rectangle((0, 0, WIDTH, 12), fill=acc)
    fbadge = ImageFont.truetype(str(FONT_BLACK), 60)
    fclaim = ImageFont.truetype(str(FONT_BOLD), 42)
    fout = ImageFont.truetype(str(FONT_BOLD), 30)
    badge = {"true": "TRUE", "false": "FALSE", "unverified": "UNVERIFIED"}[ev.verdict]
    d.text((44, 34), badge, font=fbadge, fill=acc)
    d.text((44, 116), ev.claim, font=fclaim, fill="white")
    top = 192
    if not ev.sources:
        tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
        note_size = 90
        while note_size > 40:
            fbig = ImageFont.truetype(str(FONT_BLACK), note_size)
            if tmp.textlength(ev.note, font=fbig) <= WIDTH - 100:
                break
            note_size -= 4
        outlined_text(d, (WIDTH / 2, INLINE_PANEL_H / 2 + 20), ev.note, fbig, YELLOW, outline_w=5, anchor="mm")
        d.text((WIDTH / 2, INLINE_PANEL_H / 2 + 110), "we searched filings & press", font=fclaim, fill="#AAB3C4", anchor="mm")
    else:
        avail = INLINE_PANEL_H - top - 24
        each_h = avail // len(ev.sources) - 40
        for s in ev.sources:
            full = Image.open(SHOTS / s.png).convert("RGBA")
            x0, y0, w, h = s.crop
            crop = full.crop((x0, y0, x0 + w, y0 + h))
            ov = Image.new("RGBA", crop.size, (0, 0, 0, 0))
            od = ImageDraw.Draw(ov)
            hx, hy, hw, hh = s.highlight
            od.rectangle((hx, hy, hx + hw, hy + hh), fill=(255, 210, 60, 105), outline=(255, 210, 60, 255), width=5)
            crop = Image.alpha_composite(crop, ov)
            thumb = _fit(crop.convert("RGB"), WIDTH - 90, each_h)
            x = (WIDTH - thumb.width) // 2
            d.text((x, top), f"SOURCE: {s.outlet}", font=fout, fill=BLUE)
            img.paste(thumb, (x, top + 40))
            ImageDraw.Draw(img).rectangle((x - 3, top + 37, x + thumb.width + 3, top + 40 + thumb.height + 3), outline="#334", width=2)
            top += 40 + thumb.height + 30
    path = panels / f"src_{ev.segment}_{int(ev.at * 10)}.png"
    img.save(path)
    return path


def make_lesson_png(panels: Path, lesson: Lesson) -> Path:
    # Cap the pill to fit within the frame width (minus side margins) so the
    # centred x=(W-w)/2 overlay never goes negative and clips "LESSON" off the
    # left edge -- shrink both fonts together until the text fits.
    max_box_w = WIDTH - 80
    tag_size, text_size = 34, 40
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    tag = "LESSON"
    pad = 26
    while True:
        ftag = ImageFont.truetype(str(FONT_BLACK), tag_size)
        ftext = ImageFont.truetype(str(FONT_BOLD), text_size)
        tw = tmp.textlength(tag, font=ftag)
        txw = tmp.textlength(lesson.text, font=ftext)
        box_w = int(tw + txw + pad * 3 + 30)
        if box_w <= max_box_w or text_size <= 24:
            break
        tag_size -= 1
        text_size -= 2
    box_h = 92
    img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, box_w - 1, box_h - 1), radius=16, fill=(11, 14, 20, 235), outline=YELLOW, width=4)
    d.rounded_rectangle((14, 20, 14 + tw + pad, box_h - 20), radius=10, fill=YELLOW)
    d.text((14 + (tw + pad) / 2, box_h / 2), tag, font=ftag, fill=DARK, anchor="mm")
    d.text((14 + tw + pad + 20, box_h / 2), lesson.text, font=ftext, fill="white", anchor="lm")
    path = panels / f"lesson_{lesson.segment}_{int(lesson.at * 10)}.png"
    img.save(path)
    return path


def composite_inline(captioned: Path, timeline: list[dict[str, Any]], panels: Path, work: Path, total_frames: int) -> Path:
    """Overlay inline verify panels + LESSON pills on top of the already
    captioned/mixed interview (so a panel naturally covers the caption band
    while it's on screen), and mix ting/buzzer/uncertain stingers into the
    audio at each verify's timestamp -- dialogue + music keep playing underneath."""
    seg_start = {t["name"]: t["start_frame"] / FPS for t in timeline}
    sfx_for = {"true": BRANDING / "verdict_correct_ting.wav", "false": BRANDING / "verdict_wrong_buzz.wav"}
    uncertain = make_uncertain_sfx(work)

    args = ["-i", str(captioned)]
    vlines: list[str] = []
    alines: list[str] = []
    amix_labels = ["[0:a]"]
    current = "0:v"
    idx = 1
    panel_y = HEIGHT - INLINE_PANEL_H

    for ev in INLINE:
        at = seg_start[ev.segment] + ev.at
        end = at + ev.duration
        png = make_source_panel(panels, ev)
        args += ["-loop", "1", "-t", f"{ev.duration:.3f}", "-i", str(png)]
        png_idx, idx = idx, idx + 1
        vlines.append(f"[{png_idx}:v]setpts=PTS-STARTPTS+{at:.3f}/TB,fade=t=in:st=0:d=0.22:alpha=1[src{png_idx}]")
        nxt = f"v{png_idx}"
        vlines.append(f"[{current}][src{png_idx}]overlay=x=0:y={panel_y}:eof_action=pass:"
                      f"enable='between(t,{at:.3f},{end:.3f})'[{nxt}]")
        current = nxt

        args += ["-i", str(sfx_for.get(ev.verdict, uncertain))]
        sfx_idx, idx = idx, idx + 1
        delay_ms = round(at * 1000)
        alines.append(f"[{sfx_idx}:a]aresample=48000,aformat=channel_layouts=stereo,"
                      f"adelay={delay_ms}|{delay_ms},volume=0.6[sfx{sfx_idx}]")
        amix_labels.append(f"[sfx{sfx_idx}]")

    for ls in LESSONS:
        at = seg_start[ls.segment] + ls.at
        end = at + ls.duration
        png = make_lesson_png(panels, ls)
        args += ["-loop", "1", "-t", f"{ls.duration:.3f}", "-i", str(png)]
        png_idx, idx = idx, idx + 1
        vlines.append(f"[{png_idx}:v]setpts=PTS-STARTPTS+{at:.3f}/TB,fade=t=in:st=0:d=0.15:alpha=1[les{png_idx}]")
        nxt = f"v{png_idx}"
        vlines.append(f"[{current}][les{png_idx}]overlay=x=(W-w)/2:y=250:eof_action=pass:"
                      f"enable='between(t,{at:.3f},{end:.3f})'[{nxt}]")
        current = nxt

    vlines.append(f"[{current}]null[vout]")
    alines.append("".join(amix_labels) + f"amix=inputs={len(amix_labels)}:duration=first:normalize=0,alimiter=limit=0.94[aout]")

    script = work / "inline.ffscript"
    script.write_text(";\n".join(vlines + alines) + "\n", encoding="utf-8")
    out = work / "with_inline.mp4"
    run(["ffmpeg", "-y", "-v", "error", *args, "-filter_complex_script", str(script),
         "-map", "[vout]", "-map", "[aout]", "-frames:v", str(total_frames), *encode_args(),
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(out)])
    return out


def make_uncertain_sfx(work: Path) -> Path:
    out = work / "uncertain.wav"
    # two-note descending "hmm?" tone, distinct from ting (true) / buzzer (false)
    run(["ffmpeg", "-y", "-v", "error",
         "-f", "lavfi", "-i", "sine=frequency=520:duration=0.16",
         "-f", "lavfi", "-i", "sine=frequency=390:duration=0.22",
         "-filter_complex", "[0]afade=t=out:st=0.11:d=0.05[a];[1]adelay=150|150,afade=t=out:st=0.15:d=0.06[b];"
         "[a][b]amix=inputs=2:duration=longest:normalize=0,volume=0.5[o]",
         "-map", "[o]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(out)])
    return out


# ---------------------------------------------------------------------------
# Captions from ASR word timing (2-4 word bursts, ~60% height)
# ---------------------------------------------------------------------------

def asr_words(audio: Path) -> list[dict[str, Any]]:
    import mlx_whisper
    r = mlx_whisper.transcribe(str(audio), path_or_hf_repo=ASR_MODEL, word_timestamps=True)
    words = []
    for seg in r.get("segments", []):
        for w in seg.get("words", []):
            words.append(w)
    return words


def group_bursts(words: list[dict[str, Any]]) -> list[tuple[float, float, str]]:
    bursts = []
    cur: list[dict[str, Any]] = []
    for w in words:
        cur.append(w)
        gap_next = False
        prev_end = w["end"]
        # decide to close the burst
        text_tokens = [x["word"] for x in cur]
        joined = "".join(text_tokens).strip()
        ends_punct = joined.endswith((".", "?", "!", ","))
        if len(cur) >= 3 or (len(cur) >= 2 and ends_punct):
            gap_next = True
        if gap_next:
            start = cur[0]["start"]
            end = cur[-1]["end"]
            bursts.append((start, end, joined))
            cur = []
    if cur:
        joined = "".join(x["word"] for x in cur).strip()
        bursts.append((cur[0]["start"], cur[-1]["end"], joined))
    return [b for b in bursts if b[2]]


def ass_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}:{minutes:02d}:{seconds % 60:05.2f}"


def burst_is_key(text: str) -> bool:
    up = text.upper()
    return ("$" in text or any(c.isdigit() for c in text)
            or any(k in up for k in ("MILLION", "BILLION", "FAMILY", "DAD", "BILLIONS")))


def make_subtitles(timeline: list[dict[str, Any]], work: Path) -> Path:
    ass = work / "captions.ass"
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Arial,72,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,2,80,80,730,1
Style: Key,Arial,78,&H0043D4FF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,2,80,80,730,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    audio_dir = work / "seg_audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    for item in timeline:
        seg_start_t = item["start_frame"] / FPS
        dur = item["frames"] / FPS
        wav = audio_dir / f"{item['name']}.wav"
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{item['source_start']:.6f}", "-i", str(SOURCE),
             "-t", f"{dur:.6f}", "-vn", "-ar", "16000", "-ac", "1", str(wav)])
        try:
            words = asr_words(wav)
            bursts = group_bursts(words)
        except Exception as exc:  # pragma: no cover - ASR robustness
            print(f"! ASR failed for {item['name']}: {exc}", flush=True)
            bursts = []
        for start, end, text in bursts:
            cs = seg_start_t + max(0.0, start)
            ce = seg_start_t + min(dur, end)
            if ce <= cs:
                ce = cs + 0.4
            style = "Key" if burst_is_key(text) else "Cap"
            anim = r"{\fad(40,40)\t(0,120,\fscx106\fscy106)}"
            lines.append(f"Dialogue: 4,{ass_time(cs)},{ass_time(ce)},{style},,0,0,0,,{anim}{text.upper()}\n")
    ass.write_text("".join(lines), encoding="utf-8")
    return ass


# ---------------------------------------------------------------------------
# Music + mix + burn captions
# ---------------------------------------------------------------------------

def generate_music(work: Path, name: str, raw_duration: float) -> Path:
    music = work / f"{name}.wav"
    expr = (
        "aevalsrc=(0.05*sin(2*PI*58*t)*(0.3+0.7*exp(-7*mod(t\\,0.5)))+"
        "0.013*sin(2*PI*116*t))*min(1\\,t/0.7)*min(1\\,("
        f"{raw_duration:.6f}-t)/0.7):s=48000:d={raw_duration:.6f}"
    )
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", expr,
         "-af", "lowpass=f=1300,highpass=f=35", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(music)])
    return music


def mix_and_caption(video: Path, subtitles: Path, music: Path, work: Path, raw_duration: float) -> Path:
    lines = [
        "[0:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.0[voice]",
        "[1:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.08[music]",
        f"[voice][music]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.94,atrim=0:{raw_duration:.6f}[aout]",
    ]
    script = work / "audio.ffscript"
    script.write_text(";\n".join(lines) + "\n", encoding="utf-8")
    output = work / "raw_mix.mp4"
    bottom_band = "drawbox=x=0:y=1650:w=iw:h=270:color=black@1.0:t=fill"
    vf = f"{bottom_band},subtitles='{subtitles}':fontsdir='/System/Library/Fonts/Supplemental'"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-i", str(music),
         "-filter_complex_script", str(script), "-map", "0:v:0", "-map", "[aout]", "-vf", vf,
         *encode_args(), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(output)])
    return output


# ---------------------------------------------------------------------------
# Closing sequence: evidence cutaways, score card, sources card, CTA
# ---------------------------------------------------------------------------

def _fit(im: Image.Image, max_w: int, max_h: int) -> Image.Image:
    scale = min(max_w / im.width, max_h / im.height)
    return im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)


def make_evidence_png(panels: Path, ev: Evidence) -> Path:
    img = Image.new("RGB", (WIDTH, HEIGHT), DARK)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, WIDTH, 14), fill=BLUE)
    ftitle = ImageFont.truetype(str(FONT_BLACK), 84)
    fverdict = ImageFont.truetype(str(FONT_BLACK), 52)
    fsrc = ImageFont.truetype(str(FONT_BOLD), 34)
    fkey = ImageFont.truetype(str(FONT_BLACK), 46)
    fclaim = ImageFont.truetype(str(FONT_REGULAR), 34)
    furl = ImageFont.truetype(str(FONT_REGULAR), 28)

    vlabel = {"true": "VERIFIED", "half": "HALF-TRUE"}[ev.verdict]
    vcolour = {"true": GREEN, "half": YELLOW}[ev.verdict]
    d.text((60, 70), ev.criterion, font=ftitle, fill="white")
    d.text((60, 175), ev.claim, font=fclaim, fill="#AAB3C4")
    # verdict pill top-right
    vw = d.textlength(vlabel, font=fverdict)
    d.rounded_rectangle((WIDTH - vw - 110, 74, WIDTH - 50, 150), radius=16, outline=vcolour, width=5)
    d.text((WIDTH - vw - 80, 84), vlabel, font=fverdict, fill=vcolour)

    d.text((60, 250), f"SOURCE: {ev.outlet}", font=fsrc, fill=BLUE)

    # stacked source screenshots
    top = 310
    avail_h = 1180
    crops = []
    for name, (cx, cy, cw, ch) in ev.shots:
        full = Image.open(SHOTS / name).convert("RGB")
        crops.append(full.crop((cx, cy, cx + cw, cy + ch)))
    each_h = avail_h // len(crops) - 16
    for c in crops:
        thumb = _fit(c, WIDTH - 120, each_h)
        x = (WIDTH - thumb.width) // 2
        d.rectangle((x - 4, top - 4, x + thumb.width + 4, top + thumb.height + 4), outline="#333", width=3)
        img.paste(thumb, (x, top))
        top += thumb.height + 22

    # highlighted key stat
    ky = top + 20
    for line in ev.key_stat.split("  --  "):
        tw = d.textlength(line, font=fkey)
        d.rounded_rectangle(((WIDTH - tw) / 2 - 24, ky - 8, (WIDTH + tw) / 2 + 24, ky + 62), radius=12, fill=YELLOW)
        d.text(((WIDTH - tw) / 2, ky), line, font=fkey, fill=DARK)
        ky += 88
    d.text((60, HEIGHT - 70), ev.url, font=furl, fill="#7A8394")
    path = panels / f"evidence_{ev.criterion.lower()}.png"
    img.save(path)
    return path


def make_score_card(path: Path) -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), DARK)
    d = ImageDraw.Draw(img)
    title_font = ImageFont.truetype(str(FONT_BLACK), 72)
    sub_font = ImageFont.truetype(str(FONT_REGULAR), 34)
    row_font = ImageFont.truetype(str(FONT_BLACK), 54)
    mark_font = ImageFont.truetype(str(FONT_BLACK), 40)
    cite_font = ImageFont.truetype(str(FONT_BOLD), 26)
    star_font = ImageFont.truetype(str(FONT_BLACK), 110)
    d.rectangle((0, 0, WIDTH, 16), fill=BLUE)
    d.text((60, 90), "BLINDSPOT SCORE", font=title_font, fill="white")
    d.text((60, 185), SCORE_SUBJECT, font=sub_font, fill="#AAB3C4")
    y = 300
    row_h = 300
    for name, verdict, citation in SCORE_CRITERIA:
        d.rounded_rectangle((50, y, WIDTH - 50, y + row_h - 30), radius=28, fill="#171D29", outline=BLUE, width=4)
        if verdict is True:
            mark, mcol = "TRUE", GREEN
        elif verdict == "half":
            mark, mcol = "HALF-TRUE", YELLOW
        else:
            mark, mcol = "FALSE", RED
        d.text((90, y + 30), name, font=row_font, fill="white")
        d.text((90, y + 110), mark, font=mark_font, fill=mcol)
        cy = y + 200
        for chunk in [citation]:
            tw = d.textlength(chunk, font=cite_font)
            d.rounded_rectangle((90, cy, 90 + tw + 28, cy + 46), radius=10, fill=YELLOW)
            d.text((104, cy + 8), chunk, font=cite_font, fill=DARK)
        y += row_h
    d.text((60, y + 20), SCORE_LABEL, font=star_font, fill=BLUE)
    filled = 2
    for i in range(3):
        cx = 430 + i * 115
        if i < filled:
            fill_star(d, cx, y + 90, 48, 20, YELLOW)
        else:
            outline_star(d, cx, y + 90, 48, 20, outline="#556", width=5)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def make_cta_card(path: Path) -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), DARK)
    d = ImageDraw.Draw(img)
    big = ImageFont.truetype(str(FONT_BLACK), 82)
    sub = ImageFont.truetype(str(FONT_BLACK), 60)
    outlined_text(d, (WIDTH / 2, 780), CTA_TEXT, big, YELLOW, outline_w=6, anchor="mm")
    outlined_text(d, (WIDTH / 2, 900), CTA_SUB, sub, "white", outline_w=5, anchor="mm")
    # comment bubble
    d.rounded_rectangle((WIDTH / 2 - 90, 1010, WIDTH / 2 + 90, 1150), radius=30, fill=GREEN)
    d.polygon([(WIDTH / 2 - 40, 1150), (WIDTH / 2 - 5, 1150), (WIDTH / 2 - 40, 1200)], fill=GREEN)
    for i in range(3):
        d.ellipse((WIDTH / 2 - 55 + i * 45, 1070, WIDTH / 2 - 30 + i * 45, 1095), fill=DARK)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def make_row_highlight(panels: Path) -> Path:
    w, h = WIDTH - 100 + 16, 270 + 16
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((4, 4, w - 5, h - 5), radius=34, outline=YELLOW, width=9)
    path = panels / "row_highlight.png"
    img.save(path)
    return path


def build_ending(work: Path, panels: Path, vo: Path) -> Path:
    """Single continuous VO-driven ending: score card (row-by-row highlight in
    sync with "Wealth, real / Freedom, real / Legacy? Only half") -> cut to the
    LEGACY evidence reveal on "he gave the company... his dad built it" -> a
    LESSON recap pill -> cut to the CTA card on "what's your score?"."""
    vo_dur = float(probe(vo)["format"]["duration"])
    total_dur = max(vo_dur + ENDING_TAIL, ENDING_T_CTA + 4.0)
    frame_count = frames_for(total_dur)

    score_png = panels / "score_card.png"
    make_score_card(score_png)
    legacy_png = make_evidence_png(panels, EVIDENCE[0])
    cta_png = panels / "cta_card.png"
    make_cta_card(cta_png)
    highlight_png = make_row_highlight(panels)
    lesson_png = make_lesson_png(panels, Lesson("endcard", 0.0, "BUY USED. GROW WHAT YOU HAVE."))

    def row_y(i: int) -> int:
        return 300 + i * 300 - 8

    args = [
        "-loop", "1", "-t", f"{total_dur:.3f}", "-i", str(score_png),
        "-loop", "1", "-t", f"{total_dur:.3f}", "-i", str(legacy_png),
        "-loop", "1", "-t", f"{total_dur:.3f}", "-i", str(cta_png),
        "-loop", "1", "-t", f"{total_dur:.3f}", "-i", str(highlight_png),
        "-loop", "1", "-t", f"{total_dur:.3f}", "-i", str(lesson_png),
    ]
    lines = [
        f"[3:v]format=rgba,split=3[hl0][hl1][hl2]",
        f"[4:v]format=rgba,fade=t=in:st={ENDING_T_LESSON:.3f}:d=0.2:alpha=1[lesson]",
        f"[0:v][1:v]overlay=x=0:y=0:enable='gte(t,{ENDING_T_DAD:.3f})'[base1]",
        f"[base1][2:v]overlay=x=0:y=0:enable='gte(t,{ENDING_T_CTA:.3f})'[base2]",
        f"[base2][hl0]overlay=x=42:y={row_y(0)}:enable='between(t,{ENDING_T_WEALTH:.3f},{ENDING_T_FREEDOM:.3f})'[h0]",
        f"[h0][hl1]overlay=x=42:y={row_y(1)}:enable='between(t,{ENDING_T_FREEDOM:.3f},{ENDING_T_LEGACY:.3f})'[h1]",
        f"[h1][hl2]overlay=x=42:y={row_y(2)}:enable='between(t,{ENDING_T_LEGACY:.3f},{ENDING_T_DAD:.3f})'[h2]",
        f"[h2][lesson]overlay=x=(W-w)/2:y=1730:enable='between(t,{ENDING_T_LESSON:.3f},{ENDING_T_CTA:.3f})'[vout]",
    ]

    music = generate_music(work, "ending_music", total_dur)
    ting = BRANDING / "verdict_correct_ting.wav"
    uncertain = make_uncertain_sfx(work)
    vo_idx, music_idx, ting1_idx, ting2_idx, half_idx = 5, 6, 7, 8, 9
    args += ["-i", str(vo), "-i", str(music), "-i", str(ting), "-i", str(ting), "-i", str(uncertain)]
    afilt = (
        f"[{vo_idx}:a]aresample=48000,aformat=channel_layouts=stereo,"
        "loudnorm=I=-16:TP=-1.5:LRA=10[voa];"
        f"[{music_idx}:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.07[musa];"
        f"[{ting1_idx}:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"adelay={round(ENDING_T_WEALTH*1000)}|{round(ENDING_T_WEALTH*1000)},volume=0.55[t1];"
        f"[{ting2_idx}:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"adelay={round(ENDING_T_FREEDOM*1000)}|{round(ENDING_T_FREEDOM*1000)},volume=0.55[t2];"
        f"[{half_idx}:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"adelay={round(ENDING_T_LEGACY*1000)}|{round(ENDING_T_LEGACY*1000)},volume=0.5[t3];"
        "[voa][musa][t1][t2][t3]amix=inputs=5:duration=first:normalize=0,"
        "alimiter=limit=0.94[aout]"
    )
    script = work / "ending.ffscript"
    script.write_text(";\n".join(lines) + ";\n" + afilt + "\n", encoding="utf-8")

    out = work / "ending.mp4"
    run([
        "ffmpeg", "-y", "-v", "error", *args,
        "-filter_complex_script", str(script), "-map", "[vout]", "-map", "[aout]",
        "-frames:v", str(frame_count), *encode_args(),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(out),
    ])
    return out


# ---------------------------------------------------------------------------
# Finish, checks, validate
# ---------------------------------------------------------------------------

def finish(raw_mix: Path, final: Path) -> None:
    final.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-v", "error", "-i", str(raw_mix),
         "-filter_complex", f"[0:v]setpts=PTS/{POST_SPEED}[v];[0:a]atempo={POST_SPEED}[a]",
         "-map", "[v]", "-map", "[a]", *encode_args(), "-c:a", "aac", "-b:a", "192k",
         "-ar", "48000", "-ac", "2", "-movflags", "+faststart", str(final)])


def extract_checks(final: Path, checks: Path) -> None:
    checks.mkdir(parents=True, exist_ok=True)
    info = probe(final)
    duration = float(info["format"]["duration"])
    timestamps = [0.0, 1, 2, 3.2, 4, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32, 36, 40, 44, 48, 50, 52, 54, 56, 58]
    for i, t in enumerate(x for x in timestamps if x < duration):
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(final),
             "-frames:v", "1", "-q:v", "2", str(checks / f"{i:02d}_{t:05.2f}.jpg")])
    run(["ffmpeg", "-y", "-v", "error", "-i", str(final),
         "-vf", "fps=1/2.4,drawtext=fontfile='/System/Library/Fonts/HelveticaNeue.ttc':text='%{pts\\:hms}':x=10:y=10:fontsize=28:fontcolor=yellow:borderw=3:bordercolor=black,scale=270:-2,tile=6x5:padding=4:margin=4",
         "-frames:v", "1", str(checks / "contact.jpg")])


def validate(final: Path, timeline: list[dict[str, Any]], checks: Path) -> dict[str, Any]:
    info = probe(final)
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    audio = next(s for s in info["streams"] if s["codec_type"] == "audio")
    duration = float(info["format"]["duration"])
    source_seconds = sum(item["frames"] / FPS for item in timeline)
    assertions = {
        "resolution": video["width"] == WIDTH and video["height"] == HEIGHT,
        "video_codec": video["codec_name"] == "h264",
        "pixel_format": video["pix_fmt"] == "yuv420p",
        "audio_codec": audio["codec_name"] == "aac",
        "duration_le_60": duration <= 60.0,
        "source_clips_under_15": all((item["frames"] / FPS) < 15.0 for item in timeline),
        "source_usage_under_50pct": source_seconds / 1555.0 <= 0.50,
    }
    failed = [k for k, v in assertions.items() if not v]
    if failed:
        raise AssertionError(f"validation failed: {failed}")
    run(["ffmpeg", "-v", "error", "-i", str(final), "-f", "null", "-"])
    report = {
        "output": str(final), "duration": duration, "resolution": f"{video['width']}x{video['height']}",
        "video_codec": video["codec_name"], "pixel_format": video["pix_fmt"],
        "audio_codec": audio["codec_name"], "post_speed": POST_SPEED,
        "assertions": assertions,
    }
    checks.joinpath("validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


def require_inputs() -> None:
    required = [SOURCE, FONT_REGULAR, FONT_BOLD, FONT_BLACK, OPENING_VO, ENDING_VO,
                BRANDING / "verdict_correct_ting.wav", BRANDING / "verdict_wrong_buzz.wav"]
    for name, _ in [s for ev in EVIDENCE for s in ev.shots]:
        required.append(SHOTS / name)
    for ev in INLINE:
        for s in ev.sources:
            required.append(SHOTS / s.png)
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError("missing inputs:\n" + "\n".join(missing))


def concat_copy(clips: list[Path], out: Path, work: Path, name: str) -> Path:
    listing = work / name
    listing.write_text("".join(f"file '{p.resolve()}'\n" for p in clips), encoding="utf-8")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(out)])
    return out


def main() -> None:
    require_inputs()
    for d in (WORK, PANELS, CHECKS, FINAL.parent):
        d.mkdir(parents=True, exist_ok=True)

    opening_card, _ = render_opening_card(WORK, PANELS, OPENING_VO)

    base, timeline, total_frames = build_base(WORK)
    subtitles = make_subtitles(timeline, WORK)
    raw_duration = total_frames / FPS
    music = generate_music(WORK, "music", raw_duration)
    captioned = mix_and_caption(base, subtitles, music, WORK, raw_duration)
    interview = composite_inline(captioned, timeline, PANELS, WORK, total_frames)

    ending = build_ending(WORK, PANELS, ENDING_VO)

    raw_mix = concat_copy([opening_card, interview, ending], WORK / "raw_mix_full.mp4", WORK, "concat_final_raw.txt")
    finish(raw_mix, FINAL)
    extract_checks(FINAL, CHECKS)
    validate(FINAL, timeline, CHECKS)


if __name__ == "__main__":
    main()
