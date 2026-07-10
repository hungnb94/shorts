#!/bin/bash
# Build side-by-side BAD vs GOOD comparison montages
cd /Users/hung/code/ai/shorts/output/analysis
FONT="/System/Library/Fonts/Helvetica.ttc"

for T10 in 0005 0015 0025 0050 0100 0150 0200 0300 0400 0500; do
  BAD="BAD_t${T10}.jpg"
  GOOD="GOOD_t${T10}.jpg"
  if [ ! -f "$BAD" ]; then continue; fi
  T=$(echo "$T10" | awk '{printf "%.1f", $1/10}')
  OUT="CMP_t${T}s.jpg"
  if [ -f "$GOOD" ]; then
    ffmpeg -y -i "$BAD" -i "$GOOD" -filter_complex \
      "[0:v]scale=360:640,drawtext=fontfile=${FONT}:text='BAD 8.6%':fontsize=28:fontcolor=red:x=10:y=10:borderw=2:bordercolor=black[b]; \
       [1:v]scale=360:640,drawtext=fontfile=${FONT}:text='GOOD 50%':fontsize=28:fontcolor=green:x=10:y=10:borderw=2:bordercolor=black[g]; \
       [b][g]hstack=inputs=2,drawtext=fontfile=${FONT}:text='t=${T}s':fontsize=36:fontcolor=yellow:x=(w-text_w)/2:y=h-50:borderw=3:bordercolor=black[v]" \
      -map "[v]" -frames:v 1 -q:v 2 "$OUT" 2>/dev/null
  else
    cp "$BAD" "BAD_${T}s.jpg"
  fi
  [ -f "$OUT" ] && echo "OK $OUT" || echo "FAIL $T"
done
echo "Done."
