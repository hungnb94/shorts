# Trade Me V1 TTS Energy Redesign

**Date:** 2026-07-14
**Status:** Implemented and verified
**Scope:** Replace only the synthetic narrator path; preserve the accepted visual timeline, factual script, source quotes, reaction audio, captions, and 45.53s duration.

## Problem

The current narrator uses macOS `say -v Ava -r 205`. The renderer then time-stretches each sentence to fill its visual window. Five of nine lines hit the minimum `atempo=0.72`, and every line is generated with the same voice/rate/pitch treatment. The result is technically intelligible but has flat prosody, weak contrast, and an unnaturally slow cadence.

## Chosen direction

Use Microsoft Edge neural TTS with `en-US-AriaNeural`:

- Voice profile: positive and confident.
- Content fit: short-form English finance narration.
- Cost: free; no paid API or credential required.
- Continuity: female narrator remains, but the engine changes from concatenative system speech to neural speech.

## Prosody design

Each narrative beat gets its own rate/pitch direction instead of a universal preset:

| Beat | Direction | Rate | Pitch |
|---|---|---:|---:|
| Hook | Controlled disbelief; stress “worst trade” | +8% | +3Hz |
| Criticism | Fast setup, no dead air | +14% | +2Hz |
| Bobby-pin reveal | Curious reset | +10% | +4Hz |
| Ladder | Rising momentum | +14% | +3Hz |
| Card swap | Decisive transition | +12% | +2Hz |
| Right buyer | Contrast crowd vs buyer | +8% | +4Hz |
| Value lesson | Confident explanation | +9% | +1Hz |
| House offer | Accelerating payoff | +12% | +3Hz |
| Final insight | Slower only at the engine level, not stretched | +4% | 0Hz |

Punctuation in the synthesis input may add micro-pauses or contrast, but spoken facts and burned captions remain unchanged.

## Timing rules

1. Never slow a neural line with post-processing: `atempo` must remain at or above 1.0.
2. If a line is shorter than its visual window, preserve natural speech and pad the tail with silence.
3. If a line exceeds its window, first raise the engine rate for that beat; permit post `atempo` only in the 1.0–1.15 range as a final fit guard.
4. Reject any line whose spoken duration still exceeds the target or whose fitted audio truncates speech.

## Voice processing

After synthesis:

1. Decode Edge MP3 to 48kHz stereo PCM.
2. High-pass at 75Hz.
3. Apply light compression for consistent presence, not radio-style over-compression.
4. Normalize each line to -16 LUFS / -1.5 dBTP.
5. Apply only short boundary fades.

## Verification

- Generate all nine neural lines and confirm none uses `atempo < 1.0` or truncates.
- Transcribe the final mix and verify all narration/source quotes.
- Re-run source-audio window guards.
- Measure integrated loudness and true peak.
- Decode the final MP4 and confirm 1080x1920, H.264/AAC, 30fps, ≤60s.
- Preserve a copy of the previous render for direct comparison before replacing the canonical filename.

## Non-goals

- No paid ElevenLabs/OpenAI API.
- No visual recut or new captions.
- No change to facts, source share, hard loop, or Transformative Gate.
- No promise that a neural voice alone guarantees higher retention.
