#!/bin/bash
# Generate synthetic SFX with ffmpeg + download Pixabay music
# All tracks need to be ~45s for our timeline

set -e
mkdir -p audio/music audio/sfx
cd audio

# ========== SYNTHETIC SFX (using ffmpeg filters) ==========

echo "=== Generating synthetic SFX ==="

# 1. HEARTBEAT - low thump with echo (Ch1-2)
# Use WAV for better quality for SFX
ffmpeg -y -f lavfi -i "sine=frequency=80:duration=45" \
  -af "volume=0.6,tremolo=f=1.2:d=0.7,lowpass=f=200,echo=0.8:0.9:1000:0.3" \
  sfx/heartbeat_loop.wav 2>&1 | tail -1

# 2. SERVER HUM - constant drone (Ch1-4, fades in Ch5)
ffmpeg -y -f lavfi -i "sine=frequency=110:duration=45" \
  -af "volume=0.15,lowpass=f=300,tremolo=f=0.3:d=0.4" \
  sfx/server_hum.mp3 2>&1 | tail -1

# 3. GLITCH Bzzt - short bursts (Ch3-4)
ffmpeg -y -f lavfi -i "anoisesrc=color=brown:duration=45:amplitude=0.3" \
  -af "volume=0.4,highpass=f=2000,tremolo=f=8:d=0.9,acompressor=threshold=0.1:ratio=10" \
  sfx/glitch_static.mp3 2>&1 | tail -1

# 4. CASH REGISTER (ka-ching) - single short burst at 5s
ffmpeg -y -f lavfi -i "sine=frequency=1200:duration=0.5" \
  -af "volume=0.5,tremolo=f=20:d=0.5,aphaser=in_gain=0.4:out_gain=0.5:delay=3:decay=0.4:speed=0.5" \
  sfx/cash_ching.mp3 2>&1 | tail -1

# 5. HEART MONITOR FLATLINE - dramatic beep (Ch5)
# Use WAV for better quality for SFX
ffmpeg -y -f lavfi -i "sine=frequency=440:duration=2" \
  -af "volume=0.8,tremolo=f=2:d=0.5,echo=0.8:0.9:500:0.7" \
  sfx/flatline.wav 2>&1 | tail -1

# 6. GLASS SHATTER - noise burst (Ch5)
ffmpeg -y -f lavfi -i "anoisesrc=color=white:duration=0.8:amplitude=0.5" \
  -af "volume=0.6,highpass=f=1500,lowpass=f=10000,tremolo=f=30:d=0.7" \
  sfx/shatter.mp3 2>&1 | tail -1

# 7. APPLAUSE / CROWD CHEER (Ch4 false victory)
ffmpeg -y -f lavfi -i "anoisesrc=color=pink:duration=45:amplitude=0.25" \
  -af "volume=0.4,bandpass=f=2000:width_type=h:w=1500,tremolo=f=1:d=0.3" \
  sfx/crowd_noise.mp3 2>&1 | tail -1

echo ""
echo "=== Downloading Pixabay music (best-effort) ==="

# Sad cinematic piano - Ch1-2
curl -sL --max-time 20 -o music/sad_piano.mp3 \
  "https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3" || \
echo "  sad_piano download failed, will use synthetic"

# Tension riser - Ch5
curl -sL --max-time 20 -o music/tension.mp3 \
  "https://cdn.pixabay.com/audio/2024/02/27/audio_4f120e528c.mp3" || \
echo "  tension download failed"

# Inspiring orchestral - Ch6-7
curl -sL --max-time 20 -o music/inspiring.mp3 \
  "https://cdn.pixabay.com/audio/2022/03/15/audio_b0c01f9b06.mp3" || \
echo "  inspiring download failed"

echo ""
echo "=== Done ==="
ls -la music/ sfx/
