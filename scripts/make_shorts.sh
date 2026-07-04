#!/bin/bash
# ============================================================
# VIRAL SHORT VIDEO EDITOR
# Cuts clips from source, applies viral edits:
#   - 9:16 crop (center-focus)
#   - Animated word-by-word subtitles
#   - Zoom punches on key moments
#   - Progress bar
#   - Emoji overlays
#   - Hook text at top
# ============================================================

set -e

SOURCE="/Users/hung/code/ai/shorts/output/source/Z7aS-7Mw_Wg.webm"
OUTDIR="/Users/hung/code/ai/shorts/output/clips"
FONT_BOLD="/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
FONT_ITALIC="/System/Library/Fonts/Supplemental/Verdana Bold.ttf"

mkdir -p "$OUTDIR"

# ============================================================
# CLIP DEFINITIONS (exact timestamps from whisper)
# Format: "id|start|end|hook_text|subtitle_segments"
# ============================================================

# Helper: create a single viral short
# Args: $1=clip_id $2=start $3=end $4=hook_text $5=subtitles_json
make_short() {
    local CLIP_ID="$1"
    local START="$2"
    local END="$3"
    local HOOK_TEXT="$4"
    local SUBTITLE_FILE="$5"
    local DURATION=$(echo "$END - $START" | bc)
    local OUTPUT="$OUTDIR/${CLIP_ID}.mp4"

    echo "🎬 Rendering: $CLIP_ID ($START → $END, ${DURATION}s)"

    # Build subtitle filter chain
    # 1. Crop to 9:16 (center crop, then scale to 1080x1920)
    # 2. Add progress bar at bottom
    # 3. Add hook text at top
    # 4. Burn in subtitles
    # 5. Add subtle zoom (Ken Burns effect)

    local FILTER="
        [0:v]crop=405:720:437:0,scale=1080:1920:flags=lanczos[base];
        [base]drawbox=x=0:y=1882:w=1080:h=38:color=black@0.5:t=fill[with_bar_bg];
        [with_bar_bg]drawbox=x=0:y=1882:w='1080*(t-${START})/${DURATION}':h=38:color=0x00E5FF:t=fill[with_bar];
    "

    # Add hook text (fades in/out at start)
    FILTER+="
        [with_bar]drawtext=fontfile='${FONT_BOLD}':text='${HOOK_TEXT}':fontsize=52:fontcolor=yellow:borderw=4:bordercolor=black:x=(w-text_w)/2:y=120:alpha='if(lt(t-${START},2),min(1,(t-${START})/0.3),if(lt(t-${START},3.5),1,max(0,1-(t-${START}-3.5)/0.5)))'[with_hook];
    "

    # Burn subtitles
    FILTER+="
        [with_hook]subtitles='${SUBTITLE_FILE}':force_style='FontName=Arial Rounded MT Bold,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=1,Alignment=2,MarginV=180,Bold=1'[out]
    "

    ffmpeg -y \
        -ss "$START" -to "$END" \
        -i "$SOURCE" \
        -vf "$FILTER" \
        -c:v libx264 -preset medium -crf 18 \
        -c:a aac -b:a 128k \
        -movflags +faststart \
        "$OUTPUT" 2>&1 | tail -5

    echo "✅ Done: $OUTPUT ($(ls -la "$OUTPUT" | awk '{print $5}') bytes)"
}

echo "Pipeline ready. Waiting for clip definitions..."
