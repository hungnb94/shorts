#!/usr/bin/env python3
"""
ASCII + Emoji Story: 'From 0 To Hero'
8 scenes, each 3 seconds = 24s total, 1080x1920 (9:16)
Renders PNG frames then ffmpeg to MP4.
"""

from PIL import Image, ImageDraw, ImageFont
import os
import subprocess
import textwrap

OUTPUT_DIR = "/Users/hung/code/ai/shorts/output/animated/ascii_hero"
FRAMES_DIR = os.path.join(OUTPUT_DIR, "frames")
os.makedirs(FRAMES_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 15
SCENE_DURATION = 3  # seconds per scene
FRAMES_PER_SCENE = FPS * SCENE_DURATION  # 45 frames

# Try to find a monospace font
FONT_PATHS = [
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Monaco.ttf",
    "/System/Library/Fonts/Courier.dfont",
    "/System/Library/Fonts/SFNSMono.ttf",
]
FONT_PATH = None
for fp in FONT_PATHS:
    if os.path.exists(fp):
        FONT_PATH = fp
        break

# ============================================================
# STORY SCENES
# ============================================================
SCENES = [
    # Scene 1: Starting from nothing
    {
        "title": "SCENE 1",
        "emoji_top": "🏚️",
        "ascii_art": r"""
    .________.
    |        |
    |  ____  |
    | |    | |
    | |____| |
    |________|
    |  |  |  |
    |__|__|__|
""",
        "caption": "Ngày xưa, tôi chỉ có\nmột căn nhà nhỏ...",
        "emoji_bottom": "😔",
        "color": (120, 120, 120),
    },
    # Scene 2: Empty pockets
    {
        "title": "SCENE 2",
        "emoji_top": "👖",
        "ascii_art": r"""
      .-------.
     /  EMPTY  \
    |  .----.  |
    | | $0.00 | |
    |  '----'  |
     \ ______ /
      '-------'
""",
        "caption": "Túi trống rỗng,\nkhông một đồng...",
        "emoji_bottom": "😢",
        "color": (150, 100, 50),
    },
    # Scene 3: Decision to change
    {
        "title": "SCENE 3",
        "emoji_top": "💡",
        "ascii_art": r"""
         _
        / \
       /   \
      /  !  \
     /_______\
       |||
       |||
      /|||\
     / ||| \
    /  |||  \
""",
        "caption": "Nhưng tôi quyết tâm:\n\"KHÔNG BAO GIỜ TƯỞNG TƯỢNG\"!",
        "emoji_bottom": "🔥",
        "color": (255, 180, 50),
    },
    # Scene 4: Working hard (late nights)
    {
        "title": "SCENE 4",
        "emoji_top": "⌨️",
        "ascii_art": r"""
    ___________________
   |  3:47 AM  |  KEEP |
   |-----------|-------|
   | while(true) {     |
   |   hustle++;       |
   |   sleep(0);       |
   | }                 |
   |___________________|
""",
        "caption": "Làm việc khi người ta ngủ.\n học khi người ta chơi.",
        "emoji_bottom": "💻",
        "color": (50, 200, 150),
    },
    # Scene 5: First success
    {
        "title": "SCENE 5",
        "emoji_top": "📈",
        "ascii_art": r"""
    $|
     |      *
     |     *
     |    *
     |   *
     |  *
     | *
     |*________
     +----------->  TIME
""",
        "caption": "Dollar đầu tiên đến...\nRồi hàng nghìn...",
        "emoji_bottom": "💵",
        "color": (50, 220, 80),
    },
    # Scene 6: Growing empire
    {
        "title": "SCENE 6",
        "emoji_top": "🏢",
        "ascii_art": r"""
         _
        | |
     _  | |  _
    | | | | | |
    | | | | | |
    | | | | | |
    | | | | | |
    |_|_|_|_|_|
    |_|_|_|_|_|
""",
        "caption": "Từ 1 công ty,\nđến cả một đế chế!",
        "emoji_bottom": "👑",
        "color": (200, 160, 50),
    },
    # Scene 7: Helping others
    {
        "title": "SCENE 7",
        "emoji_top": "🤝",
        "ascii_art": r"""
      \O/     \O/     \O/
       |       |       |
      / \     / \     / \
     ~~~~~   ~~~~~   ~~~~~
""",
        "caption": "Thành công không có nghĩa\nnếu không nâng người khác lên.",
        "emoji_bottom": "❤️",
        "color": (220, 80, 100),
    },
    # Scene 8: Final triumph
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
        "caption": "TỪ 0 ĐẾN HERO\nKhông gì là không thể!",
        "emoji_bottom": "🚀",
        "color": (255, 215, 0),
    },
]

# ============================================================
# RENDER ENGINE
# ============================================================
def get_font(size):
    if FONT_PATH:
        return ImageFont.truetype(FONT_PATH, size)
    return ImageFont.load_default()

def render_scene(scene_idx, scene, frame_offset):
    """Render all frames for one scene (static background, maybe fade in/out)."""
    ascii_font = get_font(28)
    caption_font = get_font(42)
    title_font = get_font(32)
    emoji_font = get_font(80)
    
    bg = (10, 10, 15)  # near-black
    
    for f in range(FRAMES_PER_SCENE):
        img = Image.new("RGB", (W, H), bg)
        draw = ImageDraw.Draw(img)
        
        frame_num = frame_offset + f
        
        # Fade in/out effect (alpha simulation via color blending)
        alpha = 1.0
        if f < 5:
            alpha = f / 5.0
        elif f > FRAMES_PER_SCENE - 5:
            alpha = (FRAMES_PER_SCENE - f) / 5.0
        
        def blend_color(c, a):
            return tuple(int(v * a) for v in c)
        
        color = blend_color(scene["color"], alpha)
        dim_color = blend_color((180, 180, 180), alpha)
        bright_color = blend_color((255, 255, 255), alpha)
        
        y_cursor = 120
        
        # Scene number
        draw.text((W//2, y_cursor), scene["title"], fill=blend_color((80,80,80), alpha), font=title_font, anchor="mt")
        y_cursor += 60
        
        # Top emoji (centered)
        draw.text((W//2, y_cursor), scene["emoji_top"], fill=bright_color, font=emoji_font, anchor="mt")
        y_cursor += 120
        
        # ASCII art (centered block)
        ascii_lines = scene["ascii_art"].strip().split("\n")
        # Calculate total height
        line_height = 34
        ascii_total_h = len(ascii_lines) * line_height
        ascii_y = y_cursor + 20
        
        for line in ascii_lines:
            draw.text((W//2, ascii_y), line, fill=color, font=ascii_font, anchor="mt")
            ascii_y += line_height
        
        y_cursor = ascii_y + 40
        
        # Caption text (centered, 2 lines)
        caption_lines = scene["caption"].split("\n")
        for cl in caption_lines:
            draw.text((W//2, y_cursor), cl, fill=bright_color, font=caption_font, anchor="mt")
            y_cursor += 55
        
        y_cursor += 30
        
        # Bottom emoji
        draw.text((W//2, y_cursor), scene["emoji_bottom"], fill=bright_color, font=emoji_font, anchor="mt")
        
        # Progress bar at bottom
        bar_y = H - 80
        bar_w = W - 200
        bar_x = 100
        total_frames = len(SCENES) * FRAMES_PER_SCENE
        progress = frame_num / total_frames
        draw.rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + 6], fill=(40, 40, 40))
        draw.rectangle([bar_x, bar_y, bar_x + int(bar_w * progress), bar_y + 6], fill=color)
        
        # Scene indicator dots
        dot_y = bar_y + 30
        dot_spacing = 40
        dot_start_x = W//2 - (len(SCENES) * dot_spacing) // 2
        for si in range(len(SCENES)):
            dx = dot_start_x + si * dot_spacing
            r = 6 if si == scene_idx else 4
            dc = color if si == scene_idx else (60, 60, 60)
            draw.ellipse([dx-r, dot_y-r, dx+r, dot_y+r], fill=dc)
        
        # Save frame
        fname = os.path.join(FRAMES_DIR, f"frame_{frame_num:04d}.png")
        img.save(fname, "PNG")
    
    return frame_offset + FRAMES_PER_SCENE


# ============================================================
# MAIN
# ============================================================
def main():
    print(f"[ASCII HERO] Rendering {len(SCENES)} scenes × {FRAMES_PER_SCENE} frames = {len(SCENES) * FRAMES_PER_SCENE} total frames")
    
    frame_offset = 0
    for i, scene in enumerate(SCENES):
        print(f"  Scene {i+1}/{len(SCENES)}: {scene['title']} - {scene['caption'][:30].replace(chr(10),' ')}...")
        frame_offset = render_scene(i, scene, frame_offset)
    
    print(f"[ASCII HERO] {frame_offset} frames rendered to {FRAMES_DIR}/")
    
    # ffmpeg: frames -> MP4
    mp4_path = os.path.join(OUTPUT_DIR, "from_0_to_hero.mp4")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(FRAMES_DIR, "frame_%04d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        "-vf", "scale=1080:1920",
        mp4_path
    ]
    
    print(f"[ASCII HERO] Encoding MP4: {mp4_path}")
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        size_mb = os.path.getsize(mp4_path) / (1024 * 1024)
        duration = frame_offset / FPS
        print(f"[ASCII HERO] ✅ DONE: {mp4_path}")
        print(f"  Duration: {duration:.1f}s | Size: {size_mb:.1f}MB | Resolution: 1080x1920")
    else:
        print(f"[ASCII HERO] ❌ ffmpeg failed:")
        print(result.stderr[-500:])


if __name__ == "__main__":
    main()
