# Ronald Wayne v3 — Qwen Caption/Visual Synchronization Record

**Date:** 2026-07-25  
**Status:** Technical verification pass; subjective listening/viewing remains a publication gate  
**Artifact:** `output/projects/ronaldwayne/2026-07-25-ronald-wayne-v3-qwen-synced.mp4`

## Why v3 exists

Qwen fit the same large narration slots as the former Edge voice, but distributed words and pauses differently. The v2 visual edit still asserted several later phrases one beat early. v3 preserves the verified Qwen audio and rebuilds the visual/caption timing from final-MP4 ASR word timestamps.

## Synchronization strategy

- Preserve forty semantic beats of exactly 1.5 seconds.
- Use `checks-v2-qwen/final-asr/final.json` as the word-timing source.
- Resolve each caption to an ASR phrase anchor.
- Round reveal time upward to the next 30fps frame so captions cannot lead audio.
- Keep progress, source label, and watermark visible before caption reveal.
- Use one intentional hold at 37.5–39.0s instead of introducing a new claim during silence.
- Replace text-heavy background cards with graphic-only backgrounds where embedded labels would reveal a claim early.
- Stream-copy the verified v2 AAC audio without re-encoding or regeneration.

## Semantic remaps

The main corrections are:

- Apple structure → not a corporation → personal liability now follows the spoken sequence.
- Jobs/Woz young and broke now precedes Wayne’s age and assets.
- Wayne’s house/car/money appears only when that asset list is spoken.
- Paperwork → building → inventions follows Qwen’s actual clause timing.
- CTA is ordered as lock verdict → sell/stay → like/subscribe/comment.
- Payoff is ordered as no regret → regret question → original contract → $500 → 2011 → $1.59M.
- Final verdict is ordered as setup → biggest fool → walking away/freedom.

## Beat 36 timing defect and fix

The first v3 render exposed a real renderer defect in the direct-quote beat:

- output-level accurate seek retained long source timestamps;
- FFmpeg evaluated the caption `enable` expression against those timestamps;
- `THAT, I REGRET` therefore appeared from the first frame.

The fix uses a five-second input preroll, exact `trim`, and `setpts=PTS-STARTPTS` before caption compositing. Frame-accurate BEFORE/AFTER inspection then confirmed:

- `54.300s`: Ronald Wayne visible; caption absent;
- `54.400s`: Ronald Wayne visible; `THAT, I REGRET` present.

## Final artifact evidence

| Check | Result |
|---|---|
| Artifact SHA-256 | `b673325c79548e83959e690d98ec6295bee99cee2793b85413267fbcf03be63b` |
| File size | 18,927,744 bytes |
| Duration | 60.000s |
| Video | H.264, 1080×1920, 30fps |
| Audio | AAC, stereo, 48kHz |
| Keyframes | 40 |
| Full FFmpeg decode | Pass |
| Manifest beats | 40 |
| ASR-anchored beats | 39 |
| Intentional hold beats | 1 |
| Premature captions | 0 |
| Maximum caption lag | 0.380s |
| Final ASR | Exact v2 match, 152/152 normalized tokens |

## Audio preservation

| Stream | SHA-256 |
|---|---|
| v2 AAC elementary stream | `5d2c3bde3b943afc3b6a235341b7838109c1001f680febcbbac036bacc08d7a4` |
| v3 AAC elementary stream | `5d2c3bde3b943afc3b6a235341b7838109c1001f680febcbbac036bacc08d7a4` |

The hashes are identical. v3 changes visual/caption timing only.

## Immutable controls

- v1 SHA-256: `66575535235c1a1af9624d46e0afd49f5c259d2515c3abc2520721c585288f20`
- v2 SHA-256: `16445a6a7feac3311421483c9d33ef5e396c037a977ed056679bf62b1c6e1021`

Both controls remained unchanged after rendering v3.

## Evidence files

- Timing manifest: `output/projects/ronaldwayne/scripts/visual-edl-v3-qwen-synced.json`
- Alignment audit: `output/projects/ronaldwayne/checks-v3-sync/alignment-audit.json`
- Verification summary: `output/projects/ronaldwayne/checks-v3-sync/verification-summary.json`
- Full contact sheet: `output/projects/ronaldwayne/checks-v3-sync/contact-sheet-40-beats.jpg`
- Caption reveal regression: `output/projects/ronaldwayne/checks-v3-sync/caption-reveal-regression.jpg`
- Risk sequence sheet: `output/projects/ronaldwayne/checks-v3-sync/contact-sheet-risk-12-to-25_5s.jpg`
- Identity sequence sheet: `output/projects/ronaldwayne/checks-v3-sync/contact-sheet-identity-31_5-to-43_5s.jpg`
- Payoff sequence sheet: `output/projects/ronaldwayne/checks-v3-sync/contact-sheet-payoff-43_5-to-60s.jpg`
- Final ASR: `output/projects/ronaldwayne/checks-v3-sync/final-asr/final.txt`

## Publication gates

Technical synchronization cannot determine whether the cloned voice feels subjectively natural or whether the edit improves retention. Watch and listen to the full 60 seconds before publication.

The narrator is a synthetic voice clone from a third-party reference. Commercial publication still requires consent/licensing review and clear disclosure. Publisher footage likewise requires rights review. The video does not guarantee any view count.
