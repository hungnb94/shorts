#!/usr/bin/env python3
"""Render HardKnocks "Is He Still a Billionaire?" (John Ruiz, Blindspot v3).

Subject: John Ruiz (source lU-bh2xPl4Y, "Asking Miami Billionaires How They
Got Rich!", School of Hard Knocks). Hook pattern B1 -- Direct Dare Question
(see docs/research/mrbeast-first-3s-2026-07-19/round_b_hooks.md).

Concept: a continuous 3-act story (mo bai / than bai / ket bai) where Ruiz's
Business Lesson Payoff is the narrative spine: quote -> independent proof ->
payoff quote. Active-speaker reframing follows every retained speaker turn.
Every beat plays over real, continuously-moving footage; source-page crops
provide the evidence without leaving a flat/dead background.

Act structure:
- MO BAI (hook, ~0-5s): live handshake, unresolved question VO ("Is he
  still a billionaire? Or did that disappear with the stock?"), face visible
  at frame 0 (ADR-0017), identity tag bounces in ~1.5s. The hook is resolved
  ONLY in ket bai.
- THAN BAI (body, ~5-35s): one short narrator bridge, then the original
  host/guest exchange. Crop focus switches at each retained speaker turn.
  The full house answer keeps $175M, $46M purchase, and ~$20M investment;
  lesson part 1 lands on Ruiz saying money comes and goes.
- KET BAI (climax, ~35-57s): a Qwen proof bridge uses real Forbes, Yahoo
  Finance, and The Real Deal screenshots; lesson part 2 returns to Ruiz's
  drive/vision/"I'll be back" quote; the spoken lesson/CTA closes the video.

Sourcing rule (ADR-aligned): SOHK is raw footage, never a verification
source. The proof-first ending uses independent Forbes, Yahoo Finance, and
The Real Deal source pages captured on 2026-07-19.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "output" / "projects" / "hardknocks"
SOURCE = PROJECT / "source" / "lU-bh2xPl4Y.mp4"
BRANDING = ROOT / "output" / "shared" / "hardknocks_branding"
WORK = PROJECT / "clips" / "v12_work"
PANELS = WORK / "panels"
CHECKS = WORK / "checks"
PROOF_SOURCES = WORK / "proof_sources"
FINAL = PROJECT / "final" / "2026-07-19-hardknocks_b1_ruiz_billionaire_check.mp4"

FONT_REGULAR = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
FONT_BLACK = Path("/System/Library/Fonts/Supplemental/Arial Black.ttf")

WIDTH = 1080
HEIGHT = 1920
FPS = 30
POST_SPEED = 1.19
# Final AAC mix measured -15.3 LUFS / -0.3 dBTP before this trim. Leave 1.5 dB
# true-peak headroom for YouTube's lossy transcode while landing near -16.5 LUFS.
FINAL_GAIN_DB = -1.2

GREEN = "#00D66E"
RED = "#FF4D4D"
YELLOW = "#FFD23C"
BLUE = "#4FC3F7"
DARK = "#0B0E14"

ASR_MODEL = "mlx-community/whisper-small-mlx"

# --- Mo bai: Direct Dare Question VO over the live handshake (no blurred card) ---
HOOK_VO_TEXT = "Is he still a billionaire? Or did that disappear with the stock?"
HOOK_VO = WORK / "audio" / "opening_vo_qwen.wav"
HOOK_TAG_AT = 1.5     # identity-tag bounce-in, seconds into the hook segment
SUBJECT_NAME = "JOHN RUIZ"
SUBJECT_CRED = "FORBES BILLIONAIRE, 2023"

# --- Than bai: narrator bridges thread each beat together (no silent hard cuts) ---
BRIDGE1_VO_TEXT = "He says it's a rags to riches story."
BRIDGE1_VO = WORK / "audio" / "bridge1_vo_qwen.wav"

# --- Proof bridge: resolves the billionaire-check hook between the two halves
# of Ruiz's business lesson. The quote is deliberately interrupted by evidence
# so the lesson, rather than a detached fact-check, becomes the narrative spine.
ENDING_VO_TEXT = (
    "His net worth proves the point. Forbes said $1.5 billion in 2023. Then "
    "L-I-F-W crashed, taking the paper fortune with it. The $175 million house? "
    "Asking price, not a sale. Net worth is a snapshot."
)
ENDING_VO = WORK / "audio" / "proof_vo_qwen_r8.wav"
# ASR-verified word starts for the 16.08s proof VO, divided by its local speed
# so screenshot transitions remain speech-synchronous.
ENDING_VO_SPEED = 1.155
ENDING_T_LIFW = 6.18 / ENDING_VO_SPEED    # "Then LIFW crashed"
ENDING_T_HOUSE = 10.58 / ENDING_VO_SPEED  # "The $175 million house"
ENDING_T_LESSON = 14.86 / ENDING_VO_SPEED # "Net worth is a snapshot"
ENDING_TAIL = 0.0

# Final narrator payoff follows Ruiz's own "I'll be back" quote. The first half
# of the approved lesson is spoken at the end of the proof bridge; this line
# completes it without repeating "Net worth is a snapshot" twice.
PAYOFF_VO_TEXT = "Drive and vision are the engine. Comment your takeaway."
PAYOFF_VO = WORK / "audio" / "payoff_vo_qwen_r8.wav"
# Large-v3-turbo places the final word end at 3.28s. The synthesized WAV then
# carries 0.48s of non-silent model tail; loudness normalization amplified that
# tail enough for final ASR to hallucinate repeated words. Fade immediately
# after real speech and retain only a short natural release.
PAYOFF_SPEECH_END = 3.28
PAYOFF_TAIL = 0.20

FORBES_SCREENSHOT = PROOF_SOURCES / "forbes_page.png"
LIFW_SCREENSHOT = PROOF_SOURCES / "mspr_yahoo_5y.png"
REALDEAL_SCREENSHOT = PROOF_SOURCES / "therealdeal_page.png"


@dataclass(frozen=True)
class Segment:
    name: str
    source_start: float
    source_end: float
    # Hard-cut speaker turns (segment-relative seconds, crop focus 0..1). First
    # turn starts at 0. Crop focus follows the active speaker rather than
    # holding the centre two-shot for the whole interview.
    turns: tuple[tuple[float, float], ...]
    zoom: float = 1.06


@dataclass(frozen=True)
class InlineVerify:
    """Text-only inline verify card: face stays on top, a citation card slides
    in on the bottom half while the interview audio keeps running (+ ting/
    uncertain stinger). No screenshots this round (see module docstring) --
    the claim + note carry the named independent source instead."""
    segment: str
    at: float              # segment-relative seconds
    verdict: str           # "true" | "unverified" | "half"
    claim: str
    note: str              # citation shown big (e.g. "THE REAL DEAL: ASKING PRICE ONLY")
    duration: float = 2.8


@dataclass(frozen=True)
class Lesson:
    """Woven-in recap pill (value layer) -- used once, in the ending sequence."""
    segment: str
    at: float
    text: str
    duration: float = 2.6


@dataclass(frozen=True)
class Evidence:
    """Billionaire-status blindspot reveal at the end (not claimed inline)."""
    criterion: str
    verdict: str       # "true" | "half"
    claim: str
    key_stat: str       # lines separated by "  --  "
    outlet: str
    url: str


SEGMENTS = (
    # Hook doubles as the interview's first base clip: handshake, Ruiz's face
    # clearly lit and visible at frame 0 (ADR-0017; confirmed via
    # v12_work/checks/frame_520.jpg during Stage 0). Hook VO plays over the
    # first ~3.76s (ducked dialogue); "...41st billionaire..." plays at full
    # volume right after, planting the payoff resolved at ENDING_T_EVIDENCE.
    # End extended 524.92->525.20: mlx_whisper word timestamps show "channel."
    # ends at 524.96, so the old cut truncated the word's tail and the fade-out
    # started even before that. New end puts the fade-out start (525.00) just
    # after the word ends, in the pause before the next line.
    Segment("hook_billionaire", 519.70, 525.20, ((0.0, 0.50),), zoom=1.05),
    # Extended past the v1 cut to include the full Q&A close ("So you didn't
    # come from money? No, I came from nothing.") -- gives the origin story a
    # real narrative beat instead of a chopped soundbite. Bridge1 VO plays
    # over the first ~2.5s (ducked), then Ruiz's own voice carries the rest.
    # End extended 559.48->559.75: word timestamps show "nothing." ends
    # exactly at 559.48, so the old cut had zero trailing buffer -- the
    # fade-out was attenuating the word itself. New end puts the fade-out
    # start (559.55) in the gap before "They really started" (559.70).
    Segment(
        "origin_claim", 549.50, 559.75,
        ((0.0, 0.68), (8.04, 0.42), (9.16, 0.68)), zoom=1.02,
    ),
    # Start on the host's complete valuation question, then hard-reframe to
    # Ruiz at the first word of his answer. This preserves the real source
    # audio for $175M asking price, $46M purchase and ~$20M invested, removing
    # the old narrator bridge that masked the key amount.
    Segment(
        "house_claim", 580.38, 594.02,
        ((0.0, 0.42), (2.88, 0.68)), zoom=1.02,
    ),
    # Business Lesson Payoff, part 1. The rapid host -> Ruiz -> host -> Ruiz
    # reframes follow the real dialogue turns: question, "Never", "Why not?",
    # then the explanation that money comes and goes. This clip ends after
    # "Money's not that important to me" so the proof bridge can test that
    # claim before Ruiz explains the capability that lets him rebuild.
    Segment(
        "lesson_money_moves", 727.10, 739.06,
        ((0.0, 0.42), (1.12, 0.68), (1.56, 0.42), (2.14, 0.68)), zoom=1.02,
    ),
    # Business Lesson Payoff, part 2. Starts on "Because I can go sell lemons"
    # and lands on "I'll be back". It remains a separate <15s source clip and
    # is placed AFTER the proof bridge in the final assembly.
    Segment(
        "lesson_rebuild", 740.28, 749.62,
        ((0.0, 0.68),), zoom=1.02,
    ),
)

# Inline text-only verifies: fire right at each claim's resolution, well
# inside the segment's own span (no bleed into the next hard cut).
INLINE = (
    InlineVerify(
        "origin_claim", 5.28, "true", "RAGS TO RICHES STORY",
        "CONSISTENT ACROSS FORBES + PRESS PROFILES", duration=2.4,
    ),
    InlineVerify(
        "house_claim", 7.20, "unverified", "$175M HOUSE VALUE",
        "THE REAL DEAL: ASKING PRICE ONLY (LISTED FEB 2026)", duration=3.0,
    ),
)

# Billionaire-status blindspot reveal at the end (not claimed inline).
EVIDENCE = (
    Evidence(
        "BILLIONAIRE STATUS", "half",
        "REAL IN 2023 -- TIED TO ONE STOCK",
        "FORBES: $1.5B NET WORTH (APRIL 2023)  --  LIFW STOCK: DOWN ~96%, DELISTED FROM NASDAQ (DEC 2025)",
        "FORBES  +  MARKETBEAT / STOCKTITAN (NASDAQ: LIFW)", "forbes.com/profile/john-ruiz",
    ),
)

# Closing score card (3 rows). verdict: True / "half" / "unverified" -- no FALSE row.
SCORE_CRITERIA = (
    ("1. ORIGIN STORY", "true", "CUBAN IMMIGRANT, FIRST TO COLLEGE"),
    ("2. $175M HOUSE", "unverified", "REAL DEAL: ASKING PRICE, NOT A SALE"),
    ("3. BILLIONAIRE STATUS", "half", "FORBES 2023 -- ONE STOCK (LIFW)"),
)
CTA_TEXT = "NET WORTH IS A SNAPSHOT."
CTA_SUB = "DRIVE + VISION ARE THE ENGINE."
CTA_PROMPT = "COMMENT YOUR TAKEAWAY"


def run(args: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(str(a) for a in args), flush=True)
    return subprocess.run([str(a) for a in args], cwd=ROOT, check=True, text=True, capture_output=capture)


def probe(path: Path) -> dict[str, Any]:
    result = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)], capture=True)
    return json.loads(result.stdout)


def frames_for(seconds: float) -> int:
    return max(1, round(seconds * FPS))


def vo_loudnorm() -> str:
    """Narrator VO loudnorm chain. Root cause of a real "TTS too quiet"
    complaint (bridge1_vo_qwen.wav landed at -18.5 LUFS, a 2.5dB shortfall,
    against a -16 LUFS target): these raw Qwen-TTS clips have a high peak-to-
    loudness ratio (e.g. bridge1 measured -25.3 LUFS integrated but -8.2dBTP
    peak -- a ~17dB crest factor from a sharp transient). loudnorm's TP=-1.5
    ceiling caps how much gain it will apply before risking clipping that
    peak, so it undershoots the loudness target and stops there -- confirmed
    this happens identically in both loudnorm's single-pass "dynamic" mode
    and true two-pass "linear" mode (mode doesn't matter; the peak ceiling
    does). Fix: a mild compressor first brings the peak closer to the
    average level (lower crest factor), so loudnorm can push the average up
    to -16 LUFS without needing to touch the peak ceiling at all -- verified
    on all 4 VO clips, all land within 0.8dB of -16 LUFS with this chain."""
    return "acompressor=threshold=0.1:ratio=4:attack=5:release=100:makeup=1,loudnorm=I=-16:TP=-1.5:LRA=10"


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


# The source interview has School of Hard Knocks' own burned-in captions
# baked into the bottom ~270px of every frame. Crop that band off here, at
# the base render stage, and zoom back up to refill 1080x1920 -- so no
# downstream step (captions, badges, ending backdrop) ever needs to paint a
# black band over it; the canvas stays 100% real footage throughout.
CAPTION_BAND_PX = 270
_BAND_ZOOM_W = round(WIDTH * HEIGHT / (HEIGHT - CAPTION_BAND_PX))


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
        f"crop={WIDTH}:{HEIGHT - CAPTION_BAND_PX}:0:0,"
        f"scale={_BAND_ZOOM_W}:{HEIGHT}:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT}:({_BAND_ZOOM_W}-{WIDTH})/2:0,"
        "eq=contrast=1.05:saturation=1.05,setsar=1,format=yuv420p"
    )


SEGMENT_FADE_IN = 0.12
SEGMENT_FADE_OUT = 0.20


def render_segment(segment: Segment, output: Path) -> int:
    duration = segment.source_end - segment.source_start
    frame_count = frames_for(duration)
    # Segments are hard-concatenated with no crossfade -- without a fade,
    # each cut abruptly chops off the tail of whatever word was still
    # decaying and immediately slams into the next segment's dialogue at
    # full volume, which reads as an unclear, too-quiet ending and a jammed,
    # no-breathing-room transition. A short fade-out/fade-in at each
    # segment's own boundary creates a small audible pause at every cut
    # without touching timing/duration, so video stays perfectly in sync.
    audio_filter = (
        "highpass=f=70,acompressor=threshold=0.125:ratio=2.0:attack=5:release=80:makeup=1.5,"
        f"loudnorm=I=-16:TP=-1.5:LRA=10,aresample=48000:first_pts=0,apad,atrim=0:{duration:.6f},"
        f"afade=t=in:st=0:d={SEGMENT_FADE_IN:.2f},"
        f"afade=t=out:st={duration - SEGMENT_FADE_OUT:.6f}:d={SEGMENT_FADE_OUT:.2f}"
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

def outlined_text(d, xy, text, font, fill, outline_w=5, anchor="mm") -> None:
    x, y = xy
    if outline_w > 0:
        for dx in range(-outline_w, outline_w + 1):
            for dy in range(-outline_w, outline_w + 1):
                if dx * dx + dy * dy <= outline_w * outline_w:
                    d.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0, 255), anchor=anchor)
    d.text((x, y), text, font=font, fill=fill, anchor=anchor)


# ---------------------------------------------------------------------------
# Hook overlay: Direct Dare Question VO + identity tag over the handshake
# ---------------------------------------------------------------------------

def make_identity_tag_png(panels: Path) -> Path:
    fname = ImageFont.truetype(str(FONT_BLACK), 46)
    fcred = ImageFont.truetype(str(FONT_BOLD), 30)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    w = int(max(tmp.textlength(SUBJECT_NAME, font=fname), tmp.textlength(SUBJECT_CRED, font=fcred))) + 70
    h = 130
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=14, fill=(11, 14, 20, 235))
    d.rectangle((0, 0, 8, h - 1), fill=BLUE)
    d.text((30, 24), SUBJECT_NAME, font=fname, fill="white")
    d.text((30, 78), SUBJECT_CRED, font=fcred, fill=BLUE)
    path = panels / "identity_tag.png"
    img.save(path)
    return path


def apply_narration_bridges(base: Path, work: Path, panels: Path, timeline: list[dict[str, Any]]) -> Path:
    """Thread the hook + origin bridge into the base video as narrator VO
    overlays -- each ducks that beat's own dialogue for the VO's duration
    (then restores it), so the story reads as one continuous narration with
    the subject's own voice, never a silent hard cut between beats. Only
    the hook bridge shows the identity-tag graphic; the body bridges are
    audio-only (footage keeps playing, unobstructed)."""
    seg_start = {t["name"]: t["start_frame"] / FPS for t in timeline}
    hook_duration = timeline[0]["frames"] / FPS
    tag = make_identity_tag_png(panels)
    bridges = [
        (seg_start["hook_billionaire"], HOOK_VO, True, hook_duration),
        (seg_start["origin_claim"], BRIDGE1_VO, False, None),
    ]

    args = ["-i", str(base)]
    idx = 1  # ffmpeg -i input index (separate from the duck-chain label counter below)
    duck_stages: list[str] = []
    mix_labels: list[str] = []
    vlines: list[str] = []
    current = "0:v"
    chain_prev = "0:a"
    for i, (at, vo_path, show_tag, tag_hold_until) in enumerate(bridges):
        vo_dur = float(probe(vo_path)["format"]["duration"])
        duck_start = at + vo_dur - 0.16
        duck_end = at + vo_dur + 0.35
        chain_out = f"d{i + 1}"
        duck_stages.append(
            f"[{chain_prev}]volume=eval=frame:volume='if(lt(t,{at:.3f}),1,"
            f"if(lt(t,{duck_start:.3f}),0.18,if(lt(t,{duck_end:.3f}),"
            f"0.18+(t-{duck_start:.3f})/0.51*0.82,1)))'[{chain_out}]"
        )
        chain_prev = chain_out

        args += ["-i", str(vo_path)]
        vo_idx = idx
        idx += 1
        delay_ms = round(at * 1000)
        voa_label = f"voa{i + 1}"
        mix_labels.append(f"[{voa_label}]")
        # loudnorm MUST run before adelay, not after -- adelay prepends
        # `delay_ms` of silence (up to 15.2s for bridge2), and loudnorm run
        # after that measures loudness over [silence + speech] together,
        # which throws its gating off badly and rendered bridge1/bridge2
        # much quieter than intended (confirmed: the mixed final audio dipped
        # to -20 to -30dB mean right in bridge1's window, well below the
        # surrounding dialogue, matching the user's "TTS too quiet" report).
        duck_stages.append(
            f"[{vo_idx}:a]aresample=48000,aformat=channel_layouts=stereo,"
            f"{vo_loudnorm()},adelay={delay_ms}|{delay_ms}[{voa_label}]"
        )
        if show_tag:
            args += ["-loop", "1", "-t", f"{tag_hold_until:.3f}", "-i", str(tag)]
            tag_idx = idx
            idx += 1
            vlines.append(f"[{tag_idx}:v]format=rgba,fade=t=in:st=0:d=0.2:alpha=1[tagf]")
            vlines.append(
                f"[{current}][tagf]overlay=x=40:y=160:eof_action=pass:"
                f"enable='between(t,{HOOK_TAG_AT:.3f},{tag_hold_until:.3f})'[tagged]"
            )
            current = "tagged"
    vlines.append(f"[{current}]null[vout]")
    afilt = ";\n".join(duck_stages)
    afilt += f";\n[{chain_prev}]" + "".join(mix_labels) + \
        f"amix=inputs={1 + len(mix_labels)}:duration=first:normalize=0,alimiter=limit=0.94[aout]"

    out = work / "base_with_bridges.mp4"
    script = work / "bridges.ffscript"
    script.write_text(";\n".join(vlines) + ";\n" + afilt + "\n", encoding="utf-8")
    run([
        "ffmpeg", "-y", "-v", "error", *args,
        "-filter_complex_script", str(script), "-map", "[vout]", "-map", "[aout]",
        *encode_args(), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(out),
    ])
    return out


# ---------------------------------------------------------------------------
# Inline verify (small non-blocking corner badge -- footage keeps playing,
# never a full-screen cutaway; per user feedback that the earlier full-panel
# cutaways broke the story's continuity and left dead space on screen)
# ---------------------------------------------------------------------------

def make_verify_badge_png(panels: Path, ev: InlineVerify) -> Path:
    """Small rounded corner badge: verdict + claim on one line, the named
    independent source's citation on the line below -- same visual language
    as the identity tag / LESSON pill, sized to its own content only."""
    acc = {"true": GREEN, "half": YELLOW, "unverified": YELLOW}[ev.verdict]
    badge = {"true": "TRUE", "half": "HALF-TRUE", "unverified": "UNVERIFIED"}[ev.verdict]
    ftop = ImageFont.truetype(str(FONT_BLACK), 36)
    fnote = ImageFont.truetype(str(FONT_BOLD), 28)
    top_line = f"{badge} · {ev.claim}"

    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    max_w = WIDTH - 100
    while tmp.textlength(top_line, font=ftop) > max_w and ftop.size > 22:
        ftop = ImageFont.truetype(str(FONT_BLACK), ftop.size - 2)
    while tmp.textlength(ev.note, font=fnote) > max_w and fnote.size > 18:
        fnote = ImageFont.truetype(str(FONT_BOLD), fnote.size - 2)

    box_w = int(max(tmp.textlength(top_line, font=ftop), tmp.textlength(ev.note, font=fnote))) + 60
    box_h = 132
    img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, box_w - 1, box_h - 1), radius=16, fill=(11, 14, 20, 235), outline=acc, width=4)
    # Draw the full line white first, then redraw just the badge word in its
    # verdict colour on top -- same starting x/y + font means the redraw
    # exactly overlays the badge glyphs, leaving " · claim" white.
    d.text((30, 24), top_line, font=ftop, fill="white")
    d.text((30, 24), badge, font=ftop, fill=acc)
    d.text((30, 78), ev.note, font=fnote, fill="#AAB3C4")
    path = panels / f"badge_{ev.segment}_{int(ev.at * 10)}.png"
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
    """Overlay small non-blocking verify badges on top of the already
    captioned/mixed interview -- footage keeps playing full-frame throughout,
    never a cutaway -- and mix a ting/uncertain stinger into the audio at
    each verify's timestamp; dialogue + music keep playing underneath."""
    seg_start = {t["name"]: t["start_frame"] / FPS for t in timeline}
    sfx_for = {"true": BRANDING / "verdict_correct_ting.wav"}
    uncertain = make_uncertain_sfx(work)

    args = ["-i", str(captioned)]
    vlines: list[str] = []
    alines: list[str] = []
    amix_labels = ["[0:a]"]
    current = "0:v"
    idx = 1

    total_dur = total_frames / FPS
    for ev in INLINE:
        at = seg_start[ev.segment] + ev.at
        end = at + ev.duration
        png = make_verify_badge_png(panels, ev)
        # Loop the badge for the WHOLE interview duration (matching the
        # working build_ending() card pattern) and gate visibility purely
        # via the overlay's own enable=/fade windows -- shifting the input's
        # own PTS to start late (the earlier approach here) left the overlay
        # filter with no frame to composite before that shifted start, so
        # the badge silently never appeared.
        args += ["-loop", "1", "-t", f"{total_dur:.3f}", "-i", str(png)]
        png_idx, idx = idx, idx + 1
        vlines.append(f"[{png_idx}:v]format=rgba,fade=t=in:st={at:.3f}:d=0.22:alpha=1,"
                      f"fade=t=out:st={end - 0.3:.3f}:d=0.3:alpha=1[src{png_idx}]")
        nxt = f"v{png_idx}"
        vlines.append(f"[{current}][src{png_idx}]overlay=x=40:y=160:eof_action=pass:"
                      f"enable='between(t,{at:.3f},{end:.3f})'[{nxt}]")
        current = nxt

        args += ["-i", str(sfx_for.get(ev.verdict, uncertain))]
        sfx_idx, idx = idx, idx + 1
        delay_ms = round(at * 1000)
        alines.append(f"[{sfx_idx}:a]aresample=48000,aformat=channel_layouts=stereo,"
                      f"adelay={delay_ms}|{delay_ms},volume=0.6[sfx{sfx_idx}]")
        amix_labels.append(f"[sfx{sfx_idx}]")

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
    # No bottom-band blackout needed here -- scaled_crop() already crops the
    # source's own caption band off at the base render stage.
    vf = f"subtitles='{subtitles}':fontsdir='/System/Library/Fonts/Supplemental'"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-i", str(music),
         "-filter_complex_script", str(script), "-map", "0:v:0", "-map", "[aout]", "-vf", vf,
         *encode_args(), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(output)])
    return output


# ---------------------------------------------------------------------------
# Closing sequence: evidence reveal, score card, CTA
# ---------------------------------------------------------------------------

def make_ending_backdrop(work: Path, total_dur: float, name: str = "ending_backdrop") -> Path:
    """Continuous, muted, slowed-down loop of the house-tour footage as the
    ending's moving backdrop -- per the "never black out the scene" rebuild
    (module docstring), the score/evidence/lesson/CTA beats all sit as small
    translucent cards ON TOP of this real motion, never a flat dark screen.
    No caption-band handling needed here -- scaled_crop() already removed
    the source's own burned-in caption band from this clip at render_segment
    time, so this loop is already 100% clean, real footage."""
    src_clip = work / "segments" / "02_house_claim.mp4"
    out = work / f"{name}.mp4"
    frame_count = frames_for(total_dur)
    vf = "setpts=1.6*PTS,eq=brightness=-0.12:saturation=0.7:contrast=1.05,boxblur=2:1,fps=30"
    run([
        "ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", str(src_clip),
        "-vf", vf, "-an", "-frames:v", str(frame_count), *encode_args(), str(out),
    ])
    return out


def make_row_card_png(panels: Path, i: int, name: str, verdict: str, citation: str) -> Path:
    """Small translucent scorecard row -- same corner-badge visual language
    as the verify badges, sized to its own content."""
    marks = {"true": ("TRUE", GREEN), "half": ("HALF-TRUE", YELLOW), "unverified": ("UNVERIFIED", YELLOW)}
    mark, mcol = marks[verdict]
    fname = ImageFont.truetype(str(FONT_BLACK), 40)
    fmark = ImageFont.truetype(str(FONT_BLACK), 32)
    fcite = ImageFont.truetype(str(FONT_BOLD), 26)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    box_w = min(int(max(tmp.textlength(name, font=fname), tmp.textlength(citation, font=fcite))) + 60, WIDTH - 80)
    box_h = 150
    img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, box_w - 1, box_h - 1), radius=18, fill=(11, 14, 20, 225), outline=mcol, width=4)
    d.text((26, 16), name, font=fname, fill="white")
    d.text((26, 62), mark, font=fmark, fill=mcol)
    d.text((26, 104), citation, font=fcite, fill="#AAB3C4")
    path = panels / f"row_card_{i}.png"
    img.save(path)
    return path


def make_evidence_header_png(panels: Path, ev: Evidence) -> Path:
    ftitle = ImageFont.truetype(str(FONT_BLACK), 44)
    fverdict = ImageFont.truetype(str(FONT_BLACK), 30)
    fsrc = ImageFont.truetype(str(FONT_BOLD), 24)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    max_w = WIDTH - 80
    while tmp.textlength(ev.criterion, font=ftitle) > max_w - 40 and ftitle.size > 30:
        ftitle = ImageFont.truetype(str(FONT_BLACK), ftitle.size - 2)
    source_line = f"SOURCE: {ev.outlet}"
    while tmp.textlength(source_line, font=fsrc) > max_w - 40 and fsrc.size > 18:
        fsrc = ImageFont.truetype(str(FONT_BOLD), fsrc.size - 2)
    vlabel = {"true": "VERIFIED", "half": "HALF-TRUE"}[ev.verdict]
    vcolour = {"true": GREEN, "half": YELLOW}[ev.verdict]
    furl = ImageFont.truetype(str(FONT_REGULAR), 20)
    box_w = min(int(max(tmp.textlength(ev.criterion, font=ftitle), tmp.textlength(source_line, font=fsrc))) + 60, WIDTH - 80)
    box_h = 220
    img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, box_w - 1, box_h - 1), radius=18, fill=(11, 14, 20, 225), outline=vcolour, width=4)
    d.text((26, 16), ev.criterion, font=ftitle, fill="white")
    d.text((26, 70), vlabel, font=fverdict, fill=vcolour)
    d.text((26, 112), ev.claim, font=fsrc, fill="#AAB3C4")
    d.text((26, 148), source_line, font=fsrc, fill=BLUE)
    d.text((26, 184), ev.url, font=furl, fill="#7A8394")
    path = panels / "evidence_header.png"
    img.save(path)
    return path


def make_stat_pill_png(panels: Path, text: str, i: int) -> Path:
    fkey = ImageFont.truetype(str(FONT_BLACK), 36)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    while tmp.textlength(text, font=fkey) > WIDTH - 140 and fkey.size > 22:
        fkey = ImageFont.truetype(str(FONT_BLACK), fkey.size - 2)
    tw = tmp.textlength(text, font=fkey)
    box_w, box_h = int(tw) + 60, 76
    img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, box_w - 1, box_h - 1), radius=14, fill=YELLOW)
    d.text((box_w / 2, box_h / 2), text, font=fkey, fill=DARK, anchor="mm")
    path = panels / f"stat_pill_{i}.png"
    img.save(path)
    return path


def make_cta_card_png(panels: Path) -> Path:
    eyebrow = ImageFont.truetype(str(FONT_BLACK), 28)
    big = ImageFont.truetype(str(FONT_BLACK), 42)
    sub = ImageFont.truetype(str(FONT_BLACK), 40)
    prompt = ImageFont.truetype(str(FONT_BOLD), 30)
    box_w = WIDTH - 100
    box_h = 330
    img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, box_w - 1, box_h - 1), radius=22, fill=(11, 14, 20, 235), outline=GREEN, width=4)
    d.text((box_w / 2, 38), "BUSINESS LESSON", font=eyebrow, fill=BLUE, anchor="mm")
    d.text((box_w / 2, 102), CTA_TEXT, font=big, fill=YELLOW, anchor="mm")
    d.text((box_w / 2, 168), CTA_SUB, font=sub, fill="white", anchor="mm")
    d.rounded_rectangle((150, 222, box_w - 150, 296), radius=18, fill=GREEN)
    d.text((box_w / 2, 259), CTA_PROMPT, font=prompt, fill=DARK, anchor="mm")
    path = panels / "cta_card.png"
    img.save(path)
    return path


def make_source_proof_png(
    panels: Path,
    name: str,
    screenshot: Path,
    crop_box: tuple[int, int, int, int],
    eyebrow: str,
    headline_lines: tuple[str, str],
    accent: str,
) -> Path:
    """Turn a real webpage crop into a legible vertical proof card.

    The screenshot remains visibly intact (publisher identity, ticker/headline,
    chart or article image); the surrounding labels only state the exact fact
    the viewer should read before the next proof replaces it.
    """
    card_w = 980
    image_max_w, image_max_h = 900, 860
    page = Image.open(screenshot).convert("RGB").crop(crop_box)
    page = ImageOps.contain(page, (image_max_w, image_max_h), Image.Resampling.LANCZOS)
    image_y = 138
    # Size the card to its real crop rather than forcing every proof into a
    # 1320px black slab. This keeps the moving footage visible and removes the
    # dead vertical gap that made the previous ending feel like a text card.
    card_h = image_y + page.height + 260
    img = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(
        (0, 0, card_w - 1, card_h - 1), radius=26,
        fill=(11, 14, 20, 242), outline=accent, width=5,
    )

    label_font = ImageFont.truetype(str(FONT_BLACK), 34)
    d.rounded_rectangle((30, 28, card_w - 30, 104), radius=18, fill=accent)
    d.text((card_w / 2, 66), eyebrow, font=label_font, fill=DARK, anchor="mm")

    image_x = (card_w - page.width) // 2
    mask = Image.new("L", page.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, page.width - 1, page.height - 1), radius=18, fill=255)
    img.paste(page, (image_x, image_y), mask)
    d.rounded_rectangle(
        (image_x - 2, image_y - 2, image_x + page.width + 1, image_y + page.height + 1),
        radius=18, outline="#FFFFFF", width=3,
    )

    headline_font = ImageFont.truetype(str(FONT_BLACK), 46)
    sub_font = ImageFont.truetype(str(FONT_BOLD), 34)
    text_y = image_y + page.height + 62
    d.text((card_w / 2, text_y), headline_lines[0], font=headline_font, fill=accent, anchor="mm")
    d.text((card_w / 2, text_y + 64), headline_lines[1], font=sub_font, fill="white", anchor="mm")
    source_font = ImageFont.truetype(str(FONT_BOLD), 24)
    d.text((card_w / 2, card_h - 42), "SOURCE SCREENSHOT", font=source_font, fill="#7A8394", anchor="mm")

    path = panels / f"proof_{name}.png"
    img.save(path)
    return path


def build_ending(work: Path, panels: Path, vo: Path) -> Path:
    """Proof bridge between the two halves of Ruiz's business lesson.

    Real source crops replace the old cumulative scorecard: Forbes profile ->
    Yahoo 5Y price chart -> The Real Deal listing. Each proof arrives on the
    exact ASR word start; the VO lands on "Net worth is a snapshot" before the
    edit returns to Ruiz explaining the drive and vision that can rebuild it.
    """
    vo_dur = float(probe(vo)["format"]["duration"])
    total_dur = vo_dur / ENDING_VO_SPEED + ENDING_TAIL
    frame_count = frames_for(total_dur)

    backdrop = make_ending_backdrop(work, total_dur)
    proof_cards = [
        make_source_proof_png(
            panels, "forbes", FORBES_SCREENSHOT, (40, 410, 900, 900),
            "FORBES PROFILE · APRIL 2023",
            ("$1.5B NET WORTH", "REAL — BUT DATED"), BLUE,
        ),
        make_source_proof_png(
            panels, "lifw", LIFW_SCREENSHOT, (80, 500, 1100, 1200),
            "YAHOO FINANCE · LIFW / MSPR · 5Y",
            ("THE STOCK COLLAPSED", "PAPER FORTUNE ≠ CASH"), RED,
        ),
        make_source_proof_png(
            panels, "realdeal", REALDEAL_SCREENSHOT, (65, 260, 1360, 1180),
            "THE REAL DEAL · FEBRUARY 2026",
            ("$175M ASKING PRICE", "NOT A VERIFIED SALE"), YELLOW,
        ),
    ]
    args = ["-i", str(backdrop)]
    visual_cards = proof_cards
    # Keep every still input alive beyond the last encoded base frame. `-t`
    # rounded to total_dur was a few milliseconds shorter than frame_count/FPS,
    # so eof_action=pass dropped the CTA on the final frame with no ffmpeg error.
    card_input_dur = frame_count / FPS + 0.5
    for p in visual_cards:
        args += ["-loop", "1", "-t", f"{card_input_dur:.3f}", "-i", str(p)]

    lines: list[str] = []
    current = "0:v"
    proof_windows = [
        (0.0, ENDING_T_LIFW),
        (ENDING_T_LIFW, ENDING_T_HOUSE),
        (ENDING_T_HOUSE, total_dur),
    ]
    for i, (at, end) in enumerate(proof_windows):
        input_idx = i + 1
        fade_in = max(at, 0.04)
        lines.append(
            f"[{input_idx}:v]format=rgba,fade=t=in:st={fade_in:.3f}:d=0.18:alpha=1,"
            f"fade=t=out:st={end - 0.18:.3f}:d=0.18:alpha=1[proof{i}]"
        )
        nxt = f"vproof{i}"
        lines.append(
            f"[{current}][proof{i}]overlay=x=(W-w)/2:y=250:eof_action=pass:"
            f"enable='between(t,{at:.3f},{end:.3f})'[{nxt}]"
        )
        current = nxt

    lines.append(f"[{current}]null[vout]")

    music = generate_music(work, "ending_music", total_dur)
    ting = BRANDING / "verdict_correct_ting.wav"
    uncertain = make_uncertain_sfx(work)
    vo_idx = len(visual_cards) + 1
    music_idx, unc1_idx, unc2_idx, ting_idx = vo_idx + 1, vo_idx + 2, vo_idx + 3, vo_idx + 4
    args += ["-i", str(vo), "-i", str(music), "-i", str(uncertain), "-i", str(uncertain), "-i", str(ting)]
    afilt = (
        f"[{vo_idx}:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"{vo_loudnorm()},atempo={ENDING_VO_SPEED},apad,atrim=0:{total_dur:.3f}[voa];"
        f"[{music_idx}:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.07[musa];"
        f"[{unc1_idx}:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"adelay={round(ENDING_T_LIFW*1000)}|{round(ENDING_T_LIFW*1000)},volume=0.5[t1];"
        f"[{unc2_idx}:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"adelay={round(ENDING_T_HOUSE*1000)}|{round(ENDING_T_HOUSE*1000)},volume=0.5[t2];"
        f"[{ting_idx}:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"adelay={round(ENDING_T_LESSON*1000)}|{round(ENDING_T_LESSON*1000)},volume=0.55[t3];"
        f"[voa][musa][t1][t2][t3]amix=inputs=5:duration=longest:normalize=0,"
        f"atrim=0:{total_dur:.3f},alimiter=limit=0.94[aout]"
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


def split_interview_for_proof(
    interview: Path,
    timeline: list[dict[str, Any]],
    total_frames: int,
    work: Path,
) -> tuple[Path, Path]:
    """Split the captioned interview at the boundary between lesson parts.

    Captions, music and inline badges are authored once across the interview.
    Two frame-exact slices let the proof bridge sit between the lesson clips
    without merging them into a source excerpt longer than 15 seconds.
    """
    lesson_setup = next(item for item in timeline if item["name"] == "lesson_money_moves")
    split_frame = lesson_setup["end_frame"]
    split_at = split_frame / FPS
    total_dur = total_frames / FPS
    slices = [
        ("interview_before_proof", 0.0, split_at, split_frame),
        ("lesson_rebuild_captioned", split_at, total_dur - split_at, total_frames - split_frame),
    ]
    outputs: list[Path] = []
    for name, start, duration, frame_count in slices:
        out = work / f"{name}.mp4"
        vf = f"trim=start={start:.6f}:duration={duration:.6f},setpts=PTS-STARTPTS,fps={FPS}"
        af = (
            f"atrim=start={start:.6f}:duration={duration:.6f},asetpts=PTS-STARTPTS,"
            f"apad,atrim=0:{duration:.6f}"
        )
        run([
            "ffmpeg", "-y", "-v", "error", "-i", str(interview),
            "-vf", vf, "-af", af, "-frames:v", str(frame_count), *encode_args(),
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(out),
        ])
        outputs.append(out)
    return outputs[0], outputs[1]


def build_payoff(work: Path, panels: Path, vo: Path) -> Path:
    """Final spoken Business Lesson Payoff over a moving interview backdrop."""
    vo_dur = float(probe(vo)["format"]["duration"])
    total_dur = min(vo_dur, PAYOFF_SPEECH_END + PAYOFF_TAIL)
    frame_count = frames_for(total_dur)
    backdrop = make_ending_backdrop(work, total_dur, "payoff_backdrop")
    cta = make_cta_card_png(panels)
    card_input_dur = frame_count / FPS + 0.5
    music = generate_music(work, "payoff_music", total_dur)
    out = work / "payoff.mp4"

    run([
        "ffmpeg", "-y", "-v", "error",
        "-i", str(backdrop),
        "-loop", "1", "-t", f"{card_input_dur:.3f}", "-i", str(cta),
        "-i", str(vo), "-i", str(music),
        "-filter_complex",
        "[1:v]format=rgba,fade=t=in:st=0:d=0.18:alpha=1[card];"
        "[0:v][card]overlay=x=(W-w)/2:y=620:eof_action=pass[vout];"
        f"[2:a]aresample=48000,aformat=channel_layouts=stereo,{vo_loudnorm()},"
        f"afade=t=out:st={PAYOFF_SPEECH_END:.3f}:d={PAYOFF_TAIL:.3f},"
        f"apad,atrim=0:{total_dur:.6f}[voa];"
        "[3:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.07[musa];"
        f"[voa][musa]amix=inputs=2:duration=longest:normalize=0,"
        f"atrim=0:{total_dur:.6f},alimiter=limit=0.94[aout]",
        "-map", "[vout]", "-map", "[aout]", "-frames:v", str(frame_count),
        *encode_args(), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(out),
    ])
    return out


# ---------------------------------------------------------------------------
# Finish, checks, validate
# ---------------------------------------------------------------------------

def finish(raw_mix: Path, final: Path) -> None:
    final.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-v", "error", "-i", str(raw_mix),
         "-filter_complex",
         f"[0:v]setpts=PTS/{POST_SPEED}[v];"
         f"[0:a]atempo={POST_SPEED},volume={FINAL_GAIN_DB}dB[a]",
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
        "duration_ge_50": duration >= 50.0,
        "duration_le_60": duration <= 60.0,
        "source_clips_under_15": all((item["frames"] / FPS) < 15.0 for item in timeline),
        "source_usage_under_50pct": source_seconds / 1280.46 <= 0.50,
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
    required = [
        SOURCE, FONT_REGULAR, FONT_BOLD, FONT_BLACK, HOOK_VO, BRIDGE1_VO, ENDING_VO, PAYOFF_VO,
        FORBES_SCREENSHOT, LIFW_SCREENSHOT, REALDEAL_SCREENSHOT,
        BRANDING / "verdict_correct_ting.wav",
    ]
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

    base, timeline, total_frames = build_base(WORK)
    bridged = apply_narration_bridges(base, WORK, PANELS, timeline)

    subtitles = make_subtitles(timeline, WORK)
    raw_duration = total_frames / FPS
    music = generate_music(WORK, "music", raw_duration)
    captioned = mix_and_caption(bridged, subtitles, music, WORK, raw_duration)
    interview = composite_inline(captioned, timeline, PANELS, WORK, total_frames)

    interview_before_proof, lesson_rebuild = split_interview_for_proof(
        interview, timeline, total_frames, WORK,
    )
    proof_bridge = build_ending(WORK, PANELS, ENDING_VO)
    payoff = build_payoff(WORK, PANELS, PAYOFF_VO)

    raw_mix = concat_copy(
        [interview_before_proof, proof_bridge, lesson_rebuild, payoff],
        WORK / "raw_mix_full.mp4", WORK, "concat_final_raw.txt",
    )
    finish(raw_mix, FINAL)
    extract_checks(FINAL, CHECKS)
    validate(FINAL, timeline, CHECKS)


if __name__ == "__main__":
    main()
