# ACKMAN ASCII — Production Trace

> YouTube: https://www.youtube.com/watch?v=KspJ3qHjtRU
> Source: "Asking Billionaires What To Invest In!" (Z7aS-7Mw_Wg)
> Method: Clip Curation Edit — Colored ASCII Art

## Pipeline

```
4K Source (AV1 3840x2160)
  → yt-dlp format 401 download
  → mlx_whisper word-level transcription
  → Cut 9 segments (libx264, lossless CRF 0)
  → Colored ASCII converter (frame_to_ascii per frame)
  → Text overlays (segment labels + quotes + progress bar)
  → Mux with original audio (aac)
  → Concatenate all segments
  → 9:16 MP4 H.264 30fps
```

## Segments

| # | Label | Source Time | Duration | Quote |
|---|-------|------------|----------|-------|
| 1 | THE CHASE | 1018.9-1024.9 | 6.0s | "Excuse me sir! Bill!" |
| 2 | IDEAS > CONNECTIONS | 1078.2-1088.4 | 10.2s | "If you build it, they will come." |
| 3 | OPTIMISM | 1114.3-1118.2 | 3.9s | "You have to be optimistic." |
| 4 | SUCCESS | 1122.4-1127.1 | 4.7s | "Successful people are inspired by people trying to make it." |
| 5 | SMILING & DIALING | 1127.1-1134.4 | 7.3s | "I remembered smiling and dialing and getting rejected..." |
| 6 | WARNING: MONEY FAST | 1144.5-1149.3 | 4.8s | "Trying to make money fast = guaranteed bad outcome." |
| 7 | ADVICE: READ + LONG-TERM | 1138.2-1144.5 | 6.3s | "Learn by reading. Longer term view." |
| 8 | LONG-TERM WINS | 1149.7-1153.4 | 3.7s | "A huge advantage." |
| 9 | NEVER GIVE UP | 1165.3-1166.6 | 1.3s | "Never give up." |

**Total: 48.3s | 9 segments | 1450 frames @ 30fps**

## ASCII Art Specs

- Grid: 120×120 chars (9×16px per cell)
- Density ramp: ` .,:;+*?%S#@`
- Font: Menlo (system monospace)
- Color: source pixel colors with luminance boost
- Output: 1080×1920 H.264

## Overlays

- Segment label: top-left, 24px white
- Quote text: bottom, 28px gold (normal) / 48px gold (finale segments 8-9, positioned higher)
- Progress bar: bottom, cyan (#00E5FF), tracks overall video 0→100%

## Tools Used

| Tool | Purpose |
|------|---------|
| yt-dlp | 4K source download (format 401, AV1) |
| mlx-whisper (base) | Word-level transcription for precise timestamps |
| ffmpeg | Segment extraction, ASCII video encoding, muxing, concatenation |
| Python PIL/Pillow | ASCII frame rendering with colored characters |
| edge-tts | NOT USED — original voice preserved |

## Key Decisions

1. **Colored ASCII over plain** — retains visual info from source, more engaging than monochrome
2. **Original voice over TTS** — preserves authenticity, avoids audio duplication bug
3. **Chase hook over TTS hook** — raw drama > generic narration
4. **9 segments over 4** — full narrative arc (chase → wisdom → story → advice → punchline)
5. **Finale text larger/higher** — visual emphasis on closing message
6. **Global progress bar** — prevents viewer confusion about video length

## Files

```
output/ackman_ascii/
├── ackman_ascii_never_give_up.mp4   (41MB, final output)
├── segments/                        (cut source segments)
│   ├── H_chase.mp4
│   ├── B_ideas.mp4
│   ├── F_optimism.mp4
│   ├── G_successful.mp4
│   ├── H_smiling.mp4
│   ├── I_moneyfast.mp4
│   ├── J_investadvice.mp4
│   ├── D_longterm.mp4
│   └── E_nevergiveup.mp4
├── ascii_H_chase.mp4                (individual ASCII segments)
├── ascii_B_ideas.mp4
├── ...
└── tmp/
    └── concat.txt

scripts/
└── ascii_ackman.py                  (ASCII converter pipeline)
```

## Transcript

- Source: `output/source/Z7aS-7Mw_Wg_4k.mp4`
- Word-level: `output/source/Z7aS-7Mw_Wg_transcript_words.json`
- Tool: mlx-whisper (mlx-community/whisper-base-mlx)

## Performance

- **Retention: 26%** (viewers who stayed to watch)
- **Format: Clip Curation Edit** (real footage → colored ASCII conversion)

### Retention Analysis

26% retention is LOW. Target for Shorts: 50-70%+. Root causes:

1. **ASCII art is visually static** — despite color, the 120×120 grid has minimal motion between frames. No zoom, no camera movement, no cuts. Viewer brain detects "nothing is changing" → swipe.

2. **No frequent editing** — 9 segments run 1.3-10.2s each. Longest segment (B_ideas) is 10.2s of continuous ASCII with no visual interruption. ADR-0016 rule: edit every 3s. This video violates it in 7 of 9 segments.

3. **Hook is weak** — "Excuse me sir! Bill!" is audio-only drama. Visually it's the same ASCII grid. No text hook, no shock value in first 2 seconds. The chase audio is compelling but the VISUAL doesn't match the energy.

4. **Quote text is too small** — 28px gold on 1080×1920 = barely readable on mobile. Should be 40-50px minimum for Shorts.

5. **No emoji/symbol pops** — The 6 Dangote videos with emoji overlays (450px native macOS emoji) will likely outperform this because they have visual events every subtitle change.

6. **Progress bar is the only motion** — The cyan progress bar at the bottom is the only element that moves continuously. Everything else is static ASCII + text.

### What Worked (relative to pure animation)

- **Original voice** preserved — audio is the strongest element
- **Chase hook** creates curiosity — "who is he chasing?" keeps some viewers
- **9-segment arc** has narrative structure — not random clips
- **Colored ASCII is novel** — first 3-5 seconds may get curiosity clicks

### Lessons for Next Batch

| Issue | Fix |
|-------|-----|
| Static ASCII | Add zoompan push-in + symbol pops every 3s |
| Weak hook | Add 28px yellow text hook in first 2s |
| Small quotes | Increase to 40px, add border |
| No emoji | Add 450px emoji overlays at keyword matches |
| Long segments | Cut segments to max 5s, add more cuts |

### Comparison: ASCII vs Dangote Pipeline

| Metric | KspJ3qHjtRU (ASCII) | Dangote (emoji overlay) |
|--------|---------------------|------------------------|
| Retention | 26% | TBD |
| Visual motion | Low (static grid) | High (zoompan + emoji pops) |
| Frequent editing | No (long segments) | Yes (emoji every subtitle) |
| Hook text | None | 28px yellow, 0-5s |
| Emoji overlays | None | 450px native macOS |
| Source footage | Real (Ackman) | Real (Dangote) |
