#!/usr/bin/env python3
"""
Character Animation Clone — "Rookie Bet"

Clones the story/emotional arc of a viral Polymarket ad (YouTube Shorts
_3ocv5yTcgM: underestimated kid -> mascot believes in him -> he becomes a
superstar -> mascot cashes a huge prediction-market win -> celebration)
with fully original characters and a fictional brand ("ProphetLine").

Nothing from the source video is reused: no footage, no audio, no character
designs. Everything below (SVG characters, CSS animation, TTS narration) is
generated from scratch.

Pipeline: one HTML/CSS+SVG scene per story beat -> Playwright records each
scene as real video (record_video_dir, CSS @keyframes play in wall-clock
time) -> scenes + per-scene TTS narration are concatenated -> muxed into a
single vertical short.

Usage:
    /usr/bin/python3 scripts/animate_character_clone.py
"""

import asyncio
import json
import os
import subprocess
import tempfile
from pathlib import Path

import edge_tts

WIDTH, HEIGHT, FPS = 1080, 1920, 30
OUTPUT_DIR = Path("/Users/hung/code/ai/shorts/output/character_clone")

NARRATOR_VOICE = "en-US-AndrewNeural"
COACH_VOICE = "en-US-RogerNeural"   # older, gruff — for the coach's quoted put-down
HYPE_VOICE = "en-US-AriaNeural"     # bright/female — for the direct-address CTA
NARRATOR_RATE = "+8%"
COACH_RATE = "+2%"
HYPE_RATE = "+10%"

# === NARRATION (fresh script hitting the same beats — no source transcript used) ===
# Each line carries its own voice so the video isn't a single monotone narrator:
# the coach's put-down is spoken "in character", the rest is narrated, and the
# closing question gets a brighter, more energetic voice.
NARRATION = [
    {"text": "You'll never make it, kid. Sit the rest of the season out.",
     "voice": COACH_VOICE, "rate": COACH_RATE},
    {"text": "But Milo the mascot saw something else — and bet everything on it, on ProphetLine.",
     "voice": NARRATOR_VOICE, "rate": NARRATOR_RATE},
    {"text": "Years of rain, mud, and getting back up. Nobody was watching. Milo never looked away.",
     "voice": NARRATOR_VOICE, "rate": NARRATOR_RATE},
    {"text": "Then the kid became THE player. And Milo's prediction hit for four hundred ten thousand dollars.",
     "voice": NARRATOR_VOICE, "rate": NARRATOR_RATE},
    {"text": "Same coach who wrote him off? Now front row, cheering the loudest.",
     "voice": NARRATOR_VOICE, "rate": NARRATOR_RATE},
    {"text": "You already know how this story ends. So — are you watching, or are you predicting?",
     "voice": HYPE_VOICE, "rate": HYPE_RATE},
]

# === SHARED CSS: characters as inline SVG, poses/expressions via classes ===
BASE_CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
body {
    width:1080px; height:1920px; overflow:hidden;
    font-family:-apple-system,'Helvetica Neue',Arial,sans-serif;
    position:relative;
}
.scene-bg { position:absolute; inset:0; }
.zoom-wrap { position:absolute; inset:0; transform-origin:50% 50%; }

.char { position:absolute; transform-origin:center bottom; filter:drop-shadow(0 14px 16px rgba(0,0,0,0.4)); }
/* cartoon ink outline on every solid shape (paths with their own stroke, e.g. mouths, are untouched) */
.char circle, .char ellipse, .char rect, .char polygon { stroke:#14141c; stroke-width:3; stroke-linejoin:round; }
.char .no-stroke { stroke:none; }

/* ---- Milo the mascot: round orange/purple blob, no teeth, big derpy eyes ---- */
.milo-body { fill:#ff8a3d; }
.milo-belly { fill:#ffd9a8; }
.milo-spot { fill:#7b3fe4; }
.milo { animation: milo-idle 1.6s ease-in-out infinite; }
@keyframes milo-idle {
    0%,100% { transform:translateY(0) rotate(-2deg); }
    50%     { transform:translateY(-14px) rotate(2deg); }
}
.milo.excited { animation: milo-excited 0.5s ease-in-out infinite; }
@keyframes milo-excited {
    0%,100% { transform:translateY(0) scale(1,1); }
    50%     { transform:translateY(-40px) scale(1.05,0.95); }
}

/* ---- Kid: colored kit, messy hair ---- */
.kid.slump { animation: kid-slump 2s ease-in-out infinite; }
@keyframes kid-slump {
    0%,100% { transform:rotate(-3deg) translateY(4px); }
    50%     { transform:rotate(-1deg) translateY(0); }
}
.kid.kick { animation: kid-kick 0.9s ease-in-out infinite; }
@keyframes kid-kick {
    0%,100%   { transform:rotate(0deg); }
    30%       { transform:rotate(-8deg); }
    55%       { transform:rotate(14deg); }
}
.kid.hero { animation: kid-hero 1.4s ease-in-out infinite; }
@keyframes kid-hero {
    0%,100% { transform:translateY(0) scale(1); }
    50%     { transform:translateY(-10px) scale(1.02); }
}

/* ---- Coach: gray tracksuit, scowl -> grin ---- */
.coach.stern { animation: coach-stern 2.4s ease-in-out infinite; }
@keyframes coach-stern {
    0%,100% { transform:rotate(1deg); }
    50%     { transform:rotate(-1deg); }
}
.coach.cheer { animation: coach-cheer 0.7s ease-in-out infinite; }
@keyframes coach-cheer {
    0%,100% { transform:translateY(0) rotate(0deg); }
    50%     { transform:translateY(-24px) rotate(-4deg); }
}

/* ---- Star A (Ronaldo-styled) / Star B (Messi-styled) ---- */
.star.pose { animation: star-pose 1.8s ease-in-out infinite; }
@keyframes star-pose {
    0%,100% { transform:translateY(0); }
    50%     { transform:translateY(-8px); }
}
.star.fistpump { animation: star-fistpump 0.6s ease-in-out infinite; }
@keyframes star-fistpump {
    0%,100% { transform:translateY(0) rotate(0deg); }
    50%     { transform:translateY(-30px) rotate(-6deg); }
}

/* ---- Phone / UI card ---- */
.phone {
    position:absolute; width:420px; height:840px; left:330px; top:540px;
    background:#111; border-radius:48px; border:8px solid #222;
    box-shadow:0 24px 70px rgba(0,0,0,0.55);
    animation: phone-in 0.6s ease-out;
}
@keyframes phone-in {
    0%   { transform:translateY(60px) scale(0.9); opacity:0; }
    100% { transform:translateY(0) scale(1); opacity:1; }
}
.phone-screen { position:absolute; inset:16px; background:#0d1117; border-radius:36px; padding:36px; color:#fff; overflow:hidden; }
.phone-screen::before {
    content:''; position:absolute; top:-40%; left:-40%; width:60%; height:180%;
    background:rgba(255,255,255,0.06); transform:rotate(20deg);
}
.phone-brand { font-size:28px; font-weight:800; color:#a97bff; letter-spacing:1px; }
.phone-label { font-size:22px; color:#9aa; margin-top:24px; }
.phone-amount { font-size:64px; font-weight:900; color:#3ddc84; margin-top:10px; text-shadow:0 0 30px rgba(61,220,132,0.5); }
.phone-check {
    width:64px; height:64px; border-radius:50%; background:#3ddc84;
    display:flex; align-items:center; justify-content:center; margin:24px 0;
    animation: pop-in 0.4s ease-out;
}
@keyframes pop-in { 0% { transform:scale(0); } 70% { transform:scale(1.2); } 100% { transform:scale(1); } }

/* ---- text overlays ---- */
.caption {
    position:absolute; left:50px; right:50px; text-align:center;
    font-weight:900; color:#fff; text-shadow:0 4px 4px rgba(0,0,0,0.9), 0 0 30px rgba(0,0,0,0.6);
    -webkit-text-stroke: 2px rgba(0,0,0,0.5);
    animation: caption-in 0.5s ease-out;
}
@keyframes caption-in {
    0%   { transform:translateY(30px); opacity:0; }
    100% { transform:translateY(0); opacity:1; }
}
.badge {
    position:absolute; padding:14px 28px; border-radius:999px; font-weight:800;
    background:#7b3fe4; color:#fff; font-size:26px; box-shadow:0 10px 30px rgba(123,63,228,0.4);
}

/* ---- environment: pitch, stadium, weather, particles ---- */
.pitch-stripes {
    position:absolute; inset:0;
    background-image: repeating-linear-gradient(100deg, rgba(255,255,255,0.05) 0 70px, rgba(0,0,0,0.04) 70px 140px);
}
.goal {
    position:absolute; width:300px; height:200px;
}
.floodlights { position:absolute; top:30px; left:0; right:0; height:20px; }
.floodlights i {
    position:absolute; width:16px; height:16px; border-radius:50%; background:#fff9c4;
    box-shadow:0 0 24px 8px rgba(255,249,196,0.85);
}
.crowd-band {
    position:absolute; left:0; right:0; height:170px;
    background-color:#141c30;
    background-image: radial-gradient(circle at 13px 13px, #26314f 7px, transparent 8px);
    background-size: 30px 30px;
    border-bottom:4px solid rgba(0,0,0,0.4);
}
.rain {
    position:absolute; inset:0; opacity:0.35; pointer-events:none;
    background-image: repeating-linear-gradient(105deg, rgba(255,255,255,0.22) 0px 2px, transparent 2px 26px);
    animation: rain-fall 0.5s linear infinite;
}
@keyframes rain-fall { from { background-position:0 0; } to { background-position:-45px 70px; } }
.sparkle {
    position:absolute; border-radius:50%; background:#fff; opacity:0.9;
    animation: sparkle-tw 1.4s ease-in-out infinite;
}
@keyframes sparkle-tw { 0%,100% { opacity:0.2; transform:scale(0.6); } 50% { opacity:1; transform:scale(1.2); } }
.confetti { position:absolute; border-radius:3px; animation: confetti-fall linear infinite; }
@keyframes confetti-fall {
    0%   { transform:translateY(-60px) rotate(0deg); opacity:1; }
    100% { transform:translateY(2100px) rotate(420deg); opacity:0.85; }
}
.vignette { position:absolute; inset:0; box-shadow: inset 0 0 240px rgba(0,0,0,0.55); pointer-events:none; }
"""


def svg_milo(cls="milo", w=220, h=220):
    return f'''<svg class="char {cls}" width="{w}" height="{h}" viewBox="0 0 200 200">
      <ellipse class="milo-body" cx="100" cy="120" rx="70" ry="65"/>
      <ellipse class="milo-belly" cx="100" cy="135" rx="42" ry="38"/>
      <ellipse class="no-stroke" cx="80" cy="90" rx="20" ry="11" fill="rgba(255,255,255,0.28)"/>
      <circle class="milo-spot" cx="60" cy="90" r="10"/>
      <circle class="milo-spot" cx="140" cy="95" r="7"/>
      <circle cx="78" cy="105" r="16" fill="#fff"/><circle cx="122" cy="105" r="16" fill="#fff"/>
      <circle class="no-stroke" cx="81" cy="108" r="7" fill="#1a1a1a"/><circle class="no-stroke" cx="119" cy="108" r="7" fill="#1a1a1a"/>
      <path d="M85 140 Q100 152 115 140" stroke="#1a1a1a" stroke-width="4" fill="none" stroke-linecap="round"/>
      <ellipse class="milo-body" cx="45" cy="140" rx="14" ry="22" transform="rotate(-20 45 140)"/>
      <ellipse class="milo-body" cx="155" cy="140" rx="14" ry="22" transform="rotate(20 155 140)"/>
    </svg>'''


def svg_kid(cls="kid slump", w=180, h=260, kit="#4a6fa5", smile=False):
    mouth = "M70 73 Q80 82 90 73" if smile else "M70 75 Q80 70 90 75"
    return f'''<svg class="char {cls}" width="{w}" height="{h}" viewBox="0 0 160 240">
      <circle class="kid-skin" cx="80" cy="55" r="34" fill="#f2c49b"/>
      <path d="M48 40 Q80 5 112 40 Q112 55 100 55 Q95 35 80 35 Q65 35 60 55 Q48 55 48 40" fill="#7a5230"/>
      <circle class="no-stroke" cx="68" cy="58" r="5" fill="#1a1a1a"/><circle class="no-stroke" cx="92" cy="58" r="5" fill="#1a1a1a"/>
      <path d="{mouth}" stroke="#1a1a1a" stroke-width="3" fill="none" stroke-linecap="round"/>
      <rect x="45" y="90" width="70" height="80" rx="18" fill="{kit}"/>
      <rect class="no-stroke" x="45" y="90" width="70" height="20" rx="10" fill="rgba(255,255,255,0.18)"/>
      <rect x="15" y="95" width="34" height="16" rx="8" fill="{kit}"/>
      <rect x="111" y="95" width="34" height="16" rx="8" fill="{kit}"/>
      <rect x="55" y="165" width="22" height="55" rx="10" fill="{kit}"/>
      <rect x="83" y="165" width="22" height="55" rx="10" fill="{kit}"/>
      <rect x="50" y="215" width="30" height="14" rx="6" fill="#2a2a2a"/>
      <rect x="80" y="215" width="30" height="14" rx="6" fill="#2a2a2a"/>
    </svg>'''


def svg_coach(cls="coach stern", w=180, h=260, smile=False):
    mouth = "M66 72 Q80 84 94 72" if smile else "M66 75 Q80 68 94 75"
    brow = "M62 47 L74 50 M98 47 L86 50" if not smile else "M62 47 L74 49 M98 47 L86 49"
    return f'''<svg class="char {cls}" width="{w}" height="{h}" viewBox="0 0 160 240">
      <circle cx="80" cy="55" r="32" fill="#e0b088"/>
      <rect x="45" y="90" width="70" height="85" rx="14" fill="#5c5c5c"/>
      <rect class="no-stroke" x="45" y="90" width="70" height="18" rx="9" fill="rgba(255,255,255,0.12)"/>
      <rect x="15" y="95" width="34" height="70" rx="10" fill="#5c5c5c"/>
      <rect x="111" y="95" width="34" height="70" rx="10" fill="#5c5c5c"/>
      <path d="{brow}" stroke="#5a3d20" stroke-width="3" fill="none" stroke-linecap="round"/>
      <circle class="no-stroke" cx="66" cy="55" r="4" fill="#1a1a1a"/><circle class="no-stroke" cx="94" cy="55" r="4" fill="#1a1a1a"/>
      <path d="{mouth}" stroke="#1a1a1a" stroke-width="4" fill="none" stroke-linecap="round"/>
      <circle cx="80" cy="90" r="8" fill="#d4af37"/>
      <rect x="55" y="175" width="22" height="55" rx="10" fill="#333"/>
      <rect x="83" y="175" width="22" height="55" rx="10" fill="#333"/>
    </svg>'''


def svg_star(cls="star pose", w=190, h=270, kit="#ffcc33", beard=False):
    beard_svg = '<path d="M62 68 Q80 90 98 68 L94 78 Q80 88 66 78 Z" fill="#3a2a1a"/>' if beard else ""
    return f'''<svg class="char {cls}" width="{w}" height="{h}" viewBox="0 0 160 250">
      <circle cx="80" cy="55" r="33" fill="#c98a5b"/>
      {beard_svg}
      <path d="M50 38 Q80 15 110 38 Q108 48 80 45 Q52 48 50 38" fill="#1a1a1a"/>
      <circle class="no-stroke" cx="68" cy="55" r="4" fill="#1a1a1a"/><circle class="no-stroke" cx="94" cy="55" r="4" fill="#1a1a1a"/>
      <path d="M66 72 Q80 80 96 72" stroke="#1a1a1a" stroke-width="3" fill="none" stroke-linecap="round"/>
      <rect x="42" y="88" width="76" height="82" rx="16" fill="{kit}"/>
      <rect class="no-stroke" x="42" y="88" width="76" height="18" rx="9" fill="rgba(255,255,255,0.2)"/>
      <rect x="12" y="93" width="34" height="60" rx="10" fill="{kit}"/>
      <rect x="114" y="93" width="34" height="60" rx="10" fill="{kit}"/>
      <rect x="52" y="170" width="24" height="55" rx="10" fill="#e8e8e8"/>
      <rect x="84" y="170" width="24" height="55" rx="10" fill="#e8e8e8"/>
    </svg>'''


def svg_goal(left=590, top=1140):
    return f'''<svg class="goal" style="left:{left}px;top:{top}px;" viewBox="0 0 300 200">
      <rect x="20" y="10" width="10" height="180" fill="#eee" stroke="#14141c" stroke-width="3"/>
      <rect x="270" y="10" width="10" height="180" fill="#eee" stroke="#14141c" stroke-width="3"/>
      <rect x="20" y="10" width="260" height="10" fill="#eee" stroke="#14141c" stroke-width="3"/>
      <line x1="35" y1="20" x2="35" y2="185" stroke="#cfd8dc" stroke-width="1" opacity="0.5"/>
      <line x1="60" y1="20" x2="60" y2="185" stroke="#cfd8dc" stroke-width="1" opacity="0.5"/>
      <line x1="240" y1="20" x2="240" y2="185" stroke="#cfd8dc" stroke-width="1" opacity="0.5"/>
    </svg>'''


def svg_ball(left=560, top=1300, size=64):
    return f'''<svg style="position:absolute;left:{left}px;top:{top}px;" width="{size}" height="{size}" viewBox="0 0 60 60">
      <circle cx="30" cy="30" r="26" fill="#fff" stroke="#14141c" stroke-width="3"/>
      <polygon points="30,14 40,22 36,34 24,34 20,22" fill="#14141c"/>
    </svg>'''


def floodlights(y=30, count=6):
    spans = "".join(
        f'<i style="left:{int(60 + i * (960 / (count - 1)))}px;"></i>' for i in range(count)
    )
    return f'<div class="floodlights" style="top:{y}px;">{spans}</div>'


def confetti_field(n=14, colors=("#ff8a3d", "#3ddc84", "#7b3fe4", "#ffcc33", "#e85d75")):
    import random
    rnd = random.Random(7)
    pieces = []
    for i in range(n):
        left = rnd.randint(20, 1020)
        size = rnd.randint(10, 18)
        color = colors[i % len(colors)]
        dur = round(rnd.uniform(1.6, 3.2), 2)
        delay = round(rnd.uniform(-2.5, 0), 2)
        pieces.append(
            f'<div class="confetti" style="left:{left}px;top:-40px;width:{size}px;height:{int(size*0.6)}px;'
            f'background:{color};animation-duration:{dur}s;animation-delay:{delay}s;"></div>'
        )
    return "".join(pieces)


def sparkle_field(n=18):
    import random
    rnd = random.Random(3)
    pts = []
    for i in range(n):
        left = rnd.randint(20, 1060)
        top = rnd.randint(20, 700)
        size = rnd.choice([3, 4, 5, 6])
        delay = round(rnd.uniform(0, 1.4), 2)
        pts.append(f'<div class="sparkle" style="left:{left}px;top:{top}px;width:{size}px;height:{size}px;animation-delay:{delay}s;"></div>')
    return "".join(pts)


def html_page(body_html, bg, duration):
    return f"""<!DOCTYPE html><html><head><style>
{BASE_CSS}
.zoom-wrap {{ animation: zoom-in {duration:.2f}s ease-in-out forwards; }}
@keyframes zoom-in {{ from {{ transform:scale(1); }} to {{ transform:scale(1.07); }} }}
</style></head>
<body>
  <div class="scene-bg" style="background:{bg}"></div>
  <div class="zoom-wrap">{body_html}</div>
  <div class="vignette"></div>
</body></html>"""


def field_bg():
    return "linear-gradient(180deg,#2f8f4e 0%,#1f6b39 100%)"


STADIUM_BG = "radial-gradient(ellipse at 50% 15%, #2a3a5a 0%, #0a0f1e 70%)"
NIGHT_FIELD_BG = "linear-gradient(180deg,#0a1220 0%,#123018 60%,#0d2412 100%)"

# === SCENE BUILDERS (each takes the actual TTS-driven duration for Ken Burns pacing) ===

def scene_1_hook(duration):
    body = f'''
    <div class="pitch-stripes"></div>
    {svg_goal(430, 640)}
    {svg_ball(505, 1275, 56)}
    <div style="position:absolute;left:120px;top:960px;">{svg_coach("coach stern", 200, 290)}</div>
    <div style="position:absolute;left:420px;top:1080px;">{svg_kid("kid slump", 160, 230)}</div>
    <div style="position:absolute;left:760px;top:1010px;">{svg_milo("milo", 190, 190)}</div>
    <div class="caption" style="top:170px;font-size:52px;">"You'll NEVER make it, kid."</div>
    <div class="badge" style="top:1660px;left:60px;">FOOTBALL SCHOOL — CUT DAY</div>
    '''
    return html_page(body, field_bg(), duration)


def scene_2_belief(duration):
    body = f'''
    <div class="rain"></div>
    <div style="position:absolute;left:330px;top:300px;">{svg_milo("milo excited", 240, 240)}</div>
    <div class="phone" style="top:640px;">
      <div class="phone-screen">
        <div class="phone-brand">PROPHETLINE</div>
        <div class="phone-label">PREDICTION PLACED</div>
        <div class="phone-amount">$25</div>
        <div class="phone-label" style="margin-top:36px;">"This kid becomes a superstar."</div>
      </div>
    </div>
    <div style="position:absolute;left:80px;top:1500px;">{svg_kid("kid kick", 170, 250)}</div>
    <div style="position:absolute;left:780px;top:1520px;">{svg_star("star pose", 180, 250, "#ffcc33")}</div>
    <div class="caption" style="top:120px;font-size:48px;">Milo saw something nobody else did.</div>
    '''
    return html_page(body, NIGHT_FIELD_BG, duration)


def scene_3_timeskip(duration):
    body = f'''
    {floodlights(30, 7)}
    <div class="crowd-band" style="top:120px;"></div>
    <div style="position:absolute;left:390px;top:820px;">{svg_kid("kid hero", 260, 380, smile=True)}</div>
    <div style="position:absolute;left:100px;top:1100px;">{svg_star("star fistpump", 170, 240, "#ffcc33")}</div>
    <div style="position:absolute;left:800px;top:1120px;">{svg_star("star fistpump", 170, 240, "#e85d75", True)}</div>
    <div class="caption" style="top:320px;font-size:56px;">Years later.</div>
    <div class="caption" style="top:1700px;font-size:40px;color:#3ddc84;">He became THE player.</div>
    '''
    return html_page(body, STADIUM_BG, duration)


def scene_4_payoff(duration):
    body = f'''
    {sparkle_field(16)}
    <div style="position:absolute;left:340px;top:280px;">{svg_milo("milo excited", 220, 220)}</div>
    <div class="phone" style="top:600px;">
      <div class="phone-screen">
        <div class="phone-brand">PROPHETLINE</div>
        <div class="phone-check">&#10003;</div>
        <div class="phone-label">YOUR PREDICTION WON</div>
        <div class="phone-amount">$410,000</div>
        <div class="phone-label" style="margin-top:24px;">Payout: +1,640%</div>
      </div>
    </div>
    <div class="caption" style="top:1720px;font-size:46px;color:#3ddc84;">Milo called it years ago.</div>
    '''
    return html_page(body, "linear-gradient(180deg,#0d0d14 0%,#1a1a2e 100%)", duration)


def scene_5_climax(duration):
    body = f'''
    {floodlights(30, 7)}
    <div class="crowd-band" style="top:100px;"></div>
    {confetti_field(16)}
    <div style="position:absolute;left:70px;top:1300px;">{svg_coach("coach cheer", 190, 270, smile=True)}</div>
    <div style="position:absolute;left:330px;top:1020px;">{svg_kid("kid hero", 210, 300, smile=True)}</div>
    <div style="position:absolute;left:600px;top:1060px;">{svg_star("star fistpump", 170, 240, "#ffcc33")}</div>
    <div style="position:absolute;left:830px;top:1080px;">{svg_star("star fistpump", 160, 230, "#e85d75", True)}</div>
    <div style="position:absolute;left:420px;top:760px;">{svg_milo("milo excited", 190, 190)}</div>
    <div class="badge" style="top:1790px;left:340px;background:#3ddc84;color:#0a1220;">PROPHETLINE.APP</div>
    <div class="caption" style="top:330px;font-size:46px;">Same coach. Front row now.</div>
    '''
    return html_page(body, STADIUM_BG, duration)


def scene_6_cta(duration):
    body = f'''
    {sparkle_field(22)}
    <div style="position:absolute;left:400px;top:760px;">{svg_milo("milo excited", 260, 260)}</div>
    <div class="caption" style="top:1200px;font-size:50px;">Are you watching?</div>
    <div class="caption" style="top:1290px;font-size:50px;color:#a97bff;">Or predicting?</div>
    <div class="badge" style="top:1600px;left:270px;font-size:32px;">PROPHETLINE — PREDICT WHAT'S NEXT</div>
    '''
    return html_page(body, "linear-gradient(135deg,#1a1a2e 0%,#0d0d14 100%)", duration)


SCENES = [scene_1_hook, scene_2_belief, scene_3_timeskip, scene_4_payoff, scene_5_climax, scene_6_cta]

RECORD_SCRIPT = """
import sys, json
from playwright.sync_api import sync_playwright

cfg = json.loads(sys.argv[1])
with sync_playwright() as p:
    browser = p.chromium.launch(channel="chromium", args=["--no-sandbox", "--disable-gpu"])
    context = browser.new_context(
        viewport={"width": cfg["width"], "height": cfg["height"]},
        record_video_dir=cfg["video_dir"],
        record_video_size={"width": cfg["width"], "height": cfg["height"]},
    )
    page = context.new_page()
    page.set_content(cfg["html"])
    page.wait_for_timeout(int(cfg["duration"] * 1000))
    video = page.video
    context.close()
    browser.close()
    print(video.path())
"""


async def generate_tts(text, voice, rate_str, output_path, retries=3):
    last_err = None
    for attempt in range(retries):
        try:
            comm = edge_tts.Communicate(text, voice, rate=rate_str)
            audio_data = bytearray()
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            if not audio_data:
                raise RuntimeError("empty audio")
            with open(output_path, "wb") as f:
                f.write(audio_data)
            break
        except Exception as e:
            last_err = e
            print(f"    [!] TTS attempt {attempt+1} failed: {e}")
            await asyncio.sleep(2)
    else:
        raise last_err
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", output_path],
        capture_output=True, text=True,
    )
    return float(json.loads(result.stdout)["format"]["duration"])


def record_scene(html, duration, video_dir, script_path):
    cfg = {"html": html, "duration": duration, "video_dir": str(video_dir), "width": WIDTH, "height": HEIGHT}
    result = subprocess.run(
        ["/usr/bin/python3", str(script_path), json.dumps(cfg)],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Scene record failed: {result.stderr[-800:]}")
    return result.stdout.strip().splitlines()[-1]


def normalize_scene(raw_webm, duration, out_mp4):
    """Re-encode to fixed FPS/duration so scenes concatenate cleanly."""
    subprocess.run([
        "ffmpeg", "-y", "-i", str(raw_webm),
        "-t", str(duration),
        "-r", str(FPS), "-vf", f"scale={WIDTH}:{HEIGHT}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
        "-an", str(out_mp4),
    ], capture_output=True, check=True)


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix="character_clone_"))
    script_path = temp_dir / "record_scene.py"
    script_path.write_text(RECORD_SCRIPT)

    print(f"[+] Temp dir: {temp_dir}")
    scene_video_paths = []
    scene_audio_paths = []

    for i, (scene_fn, line) in enumerate(zip(SCENES, NARRATION), start=1):
        print(f"[+] Scene {i}: generating TTS ({line['voice']})...")
        audio_path = temp_dir / f"audio_{i}.mp3"
        duration = await generate_tts(line["text"], line["voice"], line["rate"], audio_path)
        duration = max(duration, 2.0) + 0.4  # small pad so animation doesn't cut off narration
        print(f"    duration={duration:.2f}s")

        print(f"[+] Scene {i}: rendering animation...")
        video_dir = temp_dir / f"video_{i}"
        video_dir.mkdir()
        html = scene_fn(duration)
        raw_webm = record_scene(html, duration, video_dir, script_path)

        norm_path = temp_dir / f"scene_{i}.mp4"
        normalize_scene(raw_webm, duration, norm_path)

        scene_video_paths.append(norm_path)
        scene_audio_paths.append((audio_path, duration))

    # Concat videos (silent)
    concat_list = temp_dir / "concat.txt"
    concat_list.write_text("".join(f"file '{p}'\n" for p in scene_video_paths))
    silent_video = temp_dir / "silent.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
        str(silent_video),
    ], capture_output=True, check=True)

    # Concat audio with matching per-scene padding (pad each clip to its scene duration)
    padded_audio_paths = []
    for i, (audio_path, duration) in enumerate(scene_audio_paths, start=1):
        padded = temp_dir / f"audio_pad_{i}.mp3"
        subprocess.run([
            "ffmpeg", "-y", "-i", str(audio_path),
            "-af", f"apad=whole_dur={duration}",
            "-t", str(duration),
            str(padded),
        ], capture_output=True, check=True)
        padded_audio_paths.append(padded)

    audio_concat_list = temp_dir / "audio_concat.txt"
    audio_concat_list.write_text("".join(f"file '{p}'\n" for p in padded_audio_paths))
    final_audio = temp_dir / "narration.mp3"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(audio_concat_list),
        "-c", "copy", str(final_audio),
    ], capture_output=True, check=True)

    total_duration = sum(d for _, d in scene_audio_paths)
    output_path = OUTPUT_DIR / "rookie_bet.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-i", str(silent_video), "-i", str(final_audio),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "medium",
        "-c:a", "aac", "-b:a", "128k", "-shortest", "-t", str(total_duration),
        str(output_path),
    ], capture_output=True, check=True)

    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"[+] Output: {output_path} ({size_mb:.1f}MB, ~{total_duration:.1f}s)")
    print("[+] SUCCESS")


if __name__ == "__main__":
    asyncio.run(main())
