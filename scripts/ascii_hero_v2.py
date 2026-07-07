#!/usr/bin/env python3
"""
ASCII + Emoji Story: 'Từ 0 Đến Hero' v2
Fix: Vietnamese font (Arial Unicode) + TTS voiceover (edge-tts)
8 scenes, 3s each = 24s, 1080x1920
"""

from PIL import Image, ImageDraw, ImageFont
import os
import subprocess
import asyncio
import edge_tts

OUTPUT_DIR = "/Users/hung/code/ai/shorts/output/animated/ascii_hero_v2"
FRAMES_DIR = os.path.join(OUTPUT_DIR, "frames")
AUDIO_DIR = os.path.join(OUTPUT_DIR, "audio")
os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 15
SCENE_DURATION = 5  # seconds per scene
FRAMES_PER_SCENE = FPS * SCENE_DURATION  # 45 frames

# Font with Vietnamese support
FONT_REGULAR = "/Library/Fonts/Arial Unicode.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"

def get_font(size, bold=False):
    path = FONT_BOLD if bold else FONT_REGULAR
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    # Fallback
    return ImageFont.load_default()

# ============================================================
# STORY SCENES — Vietnamese with TTS text
# ============================================================
SCENES = [
    {
        "title": "SCENE 1",
        "emoji_top": "🏚️",
        "ascii_art": r"""
      .---------.
     /   ~~~     \
    |  .------.  |
    | |  NO  |   |
    | | MONEY |  |
    |  '------'  |
    |   |    |   |
    |___|____|___|
""",
        "caption_lines": ["Ngày xưa,", "tôi chỉ có", "một căn nhà nhỏ..."],
        "tts_text": "Ngày xưa, tôi chỉ có một căn nhà nhỏ.",
        "emoji_bottom": "😔",
        "color": (180, 180, 180),
    },
    {
        "title": "SCENE 2",
        "emoji_top": "👖",
        "ascii_art": r"""
      .-----------.
     /   EMPTY     \
    |   .-------.  |
    |  |  $0.00  | |
    |   '-------'  |
     \   POCKET   /
      '-----------'
""",
        "caption_lines": ["Túi trống rỗng,", "không một đồng..."],
        "tts_text": "Túi trống rỗng, không một đồng.",
        "emoji_bottom": "😢",
        "color": (200, 140, 60),
    },
    {
        "title": "SCENE 3",
        "emoji_top": "💡",
        "ascii_art": r"""
           _
          / \
         /   \
        / YES \
       /       \
      /_________\
        | | |
        | | |
       /| | |\
      / |_|_| \
""",
        "caption_lines": ["Nhưng tôi quyết tâm:", "\"KHÔNG BAO GIỜ", "TƯỞNG TƯỢNG\""],
        "tts_text": "Nhưng tôi quyết tâm. Không bao giờ từ bỏ.",
        "emoji_bottom": "🔥",
        "color": (255, 200, 60),
    },
    {
        "title": "SCENE 4",
        "emoji_top": "💻",
        "ascii_art": r"""
    ___________________
   |  03:47 AM | HUSTLE|
   |-----------|-------|
   | while(true) {     |
   |   work++;         |
   |   sleep(0);       |
   | }                 |
   |___________________|
""",
        "caption_lines": ["Làm việc khi người ta ngủ.", "Học khi người ta chơi."],
        "tts_text": "Làm việc khi người ta ngủ. Học khi người ta chơi.",
        "emoji_bottom": "🔥",
        "color": (60, 220, 160),
    },
    {
        "title": "SCENE 5",
        "emoji_top": "📈",
        "ascii_art": r"""
    $  |
       |        *
       |       *
       |      *
       |     *
       |    *
       |   *
       |  *
       | *
       |*________
       +-----------> TIME
""",
        "caption_lines": ["Dollar đầu tiên đến...", "Rồi hàng nghìn..."],
        "tts_text": "Dollar đầu tiên đến. Rồi hàng nghìn. Rồi hàng triệu.",
        "emoji_bottom": "💵",
        "color": (80, 240, 100),
    },
    {
        "title": "SCENE 6",
        "emoji_top": "🏢",
        "ascii_art": r"""
         _
        | |  _
     _  | | | |  _
    | | | | | | | |
    | | | | | | | |
    | | | | | | | |
    |_|_|_|_|_|_|_|
    |_|_|_|_|_|_|_|
""",
        "caption_lines": ["Từ một công ty...", "Đến cả một đế chế!"],
        "tts_text": "Từ một công ty nhỏ. Đến cả một đế chế!",
        "emoji_bottom": "👑",
        "color": (220, 180, 60),
    },
    {
        "title": "SCENE 7",
        "emoji_top": "🤝",
        "ascii_art": r"""
      \O/     \O/     \O/
       |       |       |
      / \     / \     / \
     ~~~~~   ~~~~~   ~~~~~
""",
        "caption_lines": ["Thành công không có nghĩa", "nếu không nâng", "người khác lên."],
        "tts_text": "Thành công không có nghĩa, nếu không nâng người khác lên.",
        "emoji_bottom": "❤️",
        "color": (240, 100, 120),
    },
    {
        "title": "SCENE 8",
        "emoji_top": "🏆",
        "ascii_art": r"""
        ___________
       '._==_==_=_.'
       .-\:      /-.
      | (|:.     |) |
       '-|:.     |-'
         \::.    /
          '::. .'
            ) (
          _.' '._
         '-------'
""",
        "caption_lines": ["TỪ 0 ĐẾN HERO", "Không gì là", "không thể!"],
        "tts_text": "Từ không gì cả. Đến anh hùng. Không gì là không thể!",
        "emoji_bottom": "🚀",
        "color": (255, 220, 60),
    },
]


# ============================================================
# TTS GENERATOR
# ============================================================
async def generate_tts():
    """Generate TTS audio for each scene."""
    tts_tasks = []
    for i, scene in enumerate(SCENES):
        audio_path = os.path.join(AUDIO_DIR, f"scene_{i:02d}.mp3")
        communicate = edge_tts.Communicate(
            text=scene["tts_text"],
            voice="vi-VN-HoaiMyNeural",  # Vietnamese female voice
            rate="+5%",
            pitch="+0Hz"
        )
        await communicate.save(audio_path)
        print(f"  TTS {i+1}: {scene['tts_text'][:40]}... -> {audio_path}")
    
    print("[TTS] All audio files generated.")

def generate_tts_sync():
    asyncio.run(generate_tts())


# ============================================================
# RENDER ENGINE
# ============================================================
def render_scene(scene_idx, scene, frame_offset):
    ascii_font = get_font(30)
    caption_font = get_font(44, bold=True)
    title_font = get_font(30)
    emoji_font = get_font(90)
    
    bg = (8, 8, 14)
    
    for f in range(FRAMES_PER_SCENE):
        img = Image.new("RGB", (W, H), bg)
        draw = ImageDraw.Draw(img)
        
        frame_num = frame_offset + f
        
        # Fade in/out
        alpha = 1.0
        if f < 4:
            alpha = f / 4.0
        elif f > FRAMES_PER_SCENE - 4:
            alpha = (FRAMES_PER_SCENE - f) / 4.0
        
        def bc(c, a):
            """Blend color with alpha."""
            return tuple(max(0, min(255, int(v * a + 8 * (1-a)))) for v in c)
        
        color = bc(scene["color"], alpha)
        white = bc((255, 255, 255), alpha)
        dim = bc((100, 100, 100), alpha)
        
        # ---- Layout: vertically centered ----
        # Calculate total content height first, then center
        
        # Title
        title_h = 50
        # Emoji top
        emoji_top_h = 120
        # ASCII art
        ascii_lines = scene["ascii_art"].strip().split("\n")
        ascii_line_h = 34
        ascii_h = len(ascii_lines) * ascii_line_h + 20
        # Caption
        caption_line_h = 52
        caption_h = len(scene["caption_lines"]) * caption_line_h + 20
        # Emoji bottom
        emoji_bot_h = 100
        # Gap
        gap = 30
        
        total_h = title_h + emoji_top_h + ascii_h + caption_h + emoji_bot_h + gap * 4
        y_start = max(100, (H - total_h) // 2)
        y = y_start
        
        # Title
        draw.text((W//2, y), scene["title"], fill=dim, font=title_font, anchor="mt")
        y += title_h + gap
        
        # Top emoji
        draw.text((W//2, y), scene["emoji_top"], fill=white, font=emoji_font, anchor="mt")
        y += emoji_top_h + gap
        
        # ASCII art — bright, centered
        for line in ascii_lines:
            draw.text((W//2, y), line, fill=color, font=ascii_font, anchor="mt")
            y += ascii_line_h
        y += gap
        
        # Caption — white, bold
        for line in scene["caption_lines"]:
            draw.text((W//2, y), line, fill=white, font=caption_font, anchor="mt")
            y += caption_line_h
        y += gap
        
        # Bottom emoji
        draw.text((W//2, y), scene["emoji_bottom"], fill=white, font=emoji_font, anchor="mt")
        
        # ---- Progress bar ----
        bar_y = H - 100
        bar_w = W - 200
        bar_x = 100
        total_frames = len(SCENES) * FRAMES_PER_SCENE
        progress = frame_num / total_frames
        draw.rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + 8], fill=(30, 30, 30))
        draw.rectangle([bar_x, bar_y, bar_x + int(bar_w * progress), bar_y + 8], fill=color)
        
        # Scene dots
        dot_y = bar_y + 30
        dot_spacing = 40
        dot_start_x = W//2 - (len(SCENES) * dot_spacing) // 2
        for si in range(len(SCENES)):
            dx = dot_start_x + si * dot_spacing
            r = 7 if si == scene_idx else 5
            dc = color if si == scene_idx else (50, 50, 50)
            draw.ellipse([dx-r, dot_y-r, dx+r, dot_y+r], fill=dc)
        
        # Save
        fname = os.path.join(FRAMES_DIR, f"frame_{frame_num:04d}.png")
        img.save(fname, "PNG")
    
    return frame_offset + FRAMES_PER_SCENE


# ============================================================
# MAIN
# ============================================================
def main():
    total_frames = len(SCENES) * FRAMES_PER_SCENE
    print(f"[ASCII HERO v2] {len(SCENES)} scenes × {FRAMES_PER_SCENE} frames = {total_frames} frames")
    print(f"[ASCII HERO v2] Font: {FONT_REGULAR} (Vietnamese support)")
    
    # Step 1: Generate TTS
    print("\n=== STEP 1: TTS Audio ===")
    generate_tts_sync()
    
    # Step 2: Render frames
    print("\n=== STEP 2: Render Frames ===")
    frame_offset = 0
    for i, scene in enumerate(SCENES):
        print(f"  Scene {i+1}/{len(SCENES)}: {scene['caption_lines'][0][:30]}...")
        frame_offset = render_scene(i, scene, frame_offset)
    print(f"  Total: {frame_offset} frames rendered")
    
    # Step 3: Concat TTS audio
    print("\n=== STEP 3: Concat Audio ===")
    audio_concat = os.path.join(AUDIO_DIR, "concat_list.txt")
    with open(audio_concat, "w") as f:
        for i in range(len(SCENES)):
            f.write(f"file 'scene_{i:02d}.mp3'\n")
    
    full_audio = os.path.join(OUTPUT_DIR, "full_narration.mp3")
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", audio_concat,
        "-c", "copy",
        full_audio
    ], capture_output=True)
    print(f"  Audio: {full_audio}")
    
    # Step 4: Get audio duration
    probe = subprocess.run([
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        full_audio
    ], capture_output=True, text=True)
    audio_duration = float(probe.stdout.strip())
    print(f"  Audio duration: {audio_duration:.1f}s")
    
    # Step 5: Encode video with audio
    print("\n=== STEP 4: Encode MP4 ===")
    mp4_path = os.path.join(OUTPUT_DIR, "tu_0_den_hero.mp4")
    
    # Video is 24s, audio might be shorter/longer — use -shortest
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(FRAMES_DIR, "frame_%04d.png"),
        "-i", full_audio,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        "-vf", "scale=1080:1920",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        mp4_path
    ], capture_output=True, text=True)
    
    if os.path.exists(mp4_path):
        size_mb = os.path.getsize(mp4_path) / (1024 * 1024)
        # Probe final
        final = subprocess.run([
            "ffprobe", "-v", "quiet",
            "-show_entries", "format=duration:stream=codec_name,width,height",
            "-of", "compact",
            mp4_path
        ], capture_output=True, text=True)
        print(f"\n[ASCII HERO v2] ✅ DONE: {mp4_path}")
        print(f"  Size: {size_mb:.1f}MB")
        print(f"  {final.stdout.strip()}")
    else:
        print(f"[ASCII HERO v2] ❌ FAILED")


if __name__ == "__main__":
    main()
