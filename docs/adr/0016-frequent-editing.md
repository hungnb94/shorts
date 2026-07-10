# ADR 0016: Frequent Editing — Retention-Driven Visual Variety

**Date:** 2026-07-08
**Status:** Accepted

## Context

Short-form video retention research shows that **viewers need a visual "event" every 2-3 seconds** to stay engaged. In short-form content (YouTube Shorts, TikTok), failure to provide this causes rapid drop-off in AVD (Average View Duration).

Our current Clip Curation Edit videos use sequential clips from the Dangote interview with static subtitles. While the clips themselves change every 2-10s, **within each clip there is zero visual motion** — the interview footage stays static. This violates the "2-Second Rule."

## Research Findings

### The 2-Second Rule (r/SmallYTChannel)
> "Anything on screen must change every 2-3 seconds. Anything can be used: cut, zoom, sound cue, graphic."

### Retention Editing / "Beastification" (Mr. Beast formula)
| Technique | Description | Impact |
|-----------|-------------|--------|
| **Cut** | Switch to different shot/angle | Prevents visual fatigue |
| **Zoom** | Slow push-in or pull-out | Adds kinetic energy |
| **Sound FX** | Whoosh, hit, riser, cash register | Emotional cueing |
| **Emoji** | Overlay emotional icons | Visual variety + emotional anchoring |
| **Text pop** | Kinetic typography entry/exit | Keeps eyes moving |
| **Color flash** | Brief white/color flash at cuts | Transition energy |

### Academic Research (Dost & Huang, 2026)
> "Seamless cuts increase liking... higher transition frequency is relevant. Overlapping cuts elevate sustained attention only when used in moderation."

Jump cuts with **seamless style** at **medium frequency** produce highest engagement.

## Implementation Plan

### Phase 1 (This cycle): Zoompan + Emoji overlays
For each clip in all 9 variants:

1. **Zoompan filter**: Slow push-in (1.0→1.05) over clip duration + center pan
2. **Emoji overlay**: At 1s into each clip, overlay a relevant emoji (💰👑🤯💪🏆)
3. **Flash transition**: 1-frame white flash between clips

### Phase 2 (Next cycle): Sound effects + b-roll
1. **Sound effects**: Cash register, whoosh, pop at emoji moments
2. **B-roll cuts**: Insert Pexels stock footage between interview clips

### Emoji Mapping
| Clip Theme | Emoji | Time |
|-----------|-------|------|
| "$30B", "$40B", "$10B" money mentions | 💰 | 1s into clip, 2s duration |
| "Richest black man", "Richest person" authority | 👑 | 1s into clip |
| "Pregnant", "Fund", shocked statements | 🤯 | 1s |
| "99% success", persistence quotes | 💪 | 1s |
| "Industrialize", "backward integration" | 🏆 | 1s |
| "Africa", "70% population" | 🌍 | 1s |
| "Worth it", emotional moments | ✨ | 1s |

## Affected Files
- `render_shorts.py` — modify `render_variant()` to add zoompan + emoji overlays
- `output/projects/dangote/final/` — all 9 videos will be regenerated

## Risks
- Zoompan on 4K-cropped-to-1080p footage might show pixelation at edges (mitigate: limit zoom to 1.05x max)
- Emoji rendering requires an emoji-capable font (Apple Color Emoji on macOS)
- Processing time increase (~2x longer render)
