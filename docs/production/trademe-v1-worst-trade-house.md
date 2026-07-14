# trademe_v1 — "Her Followers Called This Her Worst Trade... Then She Got A House"

## Status
| Field | Value |
|---|---|
| YouTube Video ID | [qSjvMJ9oBzs](https://youtube.com/watch?v=qSjvMJ9oBzs) |
| YouTube Channel | [Doog Radio](https://www.youtube.com/channel/UCqCJeIrbppZXoDM4iQjJZrw) (`UCqCJeIrbppZXoDM4iQjJZrw`) |
| Rendered | 2026-07-14 |
| Uploaded | 2026-07-14 13:28:45 +07 |
| Metrics fetch after (48h rule) | 2026-07-16 13:28:45 +07 |
| Metrics status | Not yet fetched, too early |
| Studio Analytics | [Open in YouTube Studio](https://studio.youtube.com/video/qSjvMJ9oBzs/analytics/tab-overview/period-default) |
| Decision | [ADR-0027](../adr/0027-proof-first-worst-trade-reversal.md) |

## Video Specs

`output/projects/trademe/final/2026-07-14-trademe_v1_worst_trade_house.mp4`

- SHA-256: `a483ed7889087886706c6da60eaa305e200d539a9c4e087714aaa513cb72566c`
- Size: 40,445,087 bytes
- Duration: 45.533333s
- Frames: 1,366 at 30fps
- Video: H.264 High, 1080x1920, yuv420p, 9:16
- Audio: AAC-LC, 48kHz stereo, 182kb/s reported by ffprobe
- Aggregate bitrate: 7,106,018 bit/s
- File: `output/projects/trademe/final/2026-07-14-trademe_v1_worst_trade_house.mp4`
- Metadata (title/description, ready for manual upload): `output/projects/trademe/final/2026-07-14-trademe_v1_worst_trade_house_metadata.txt`
- Render script: `pipeline/trademe/render_trademe_v1.py`

## YouTube Title
Her Followers Called This Her Worst Trade... Then She Got A House

## YouTube Description
```
Demi Skipper started with one bobby pin and traded her way through cars, a cabin and three tractors.

Then came the trade her followers called her worst: all three tractors for one Chipotle Celebrity Card. It looked impossible to move until she found the one buyer who cared about it.

That card became an off-grid trailer reportedly worth $40,000. A house flipper later offered her a house for the trailer.

The lesson wasn't "find a better item." It was "find the right buyer."

What's the strangest trade you've ever seen? Let me know below.

#barter #money #trademeproject #shorts
```

## Source

- Creator/channel: Demi Skipper, `@trademeproject`.
- Bobby-pin proof: [`6830088912174910726`](https://www.tiktok.com/@trademeproject/video/6830088912174910726), cut 0.00-3.20s.
- Card hook + tractor proof: [`6959642654208494853`](https://www.tiktok.com/@trademeproject/video/6959642654208494853), cuts 44.00-48.00s and 30.00-33.20s.
- Card-to-trailer proof: [`7037989725776416006`](https://www.tiktok.com/@trademeproject/video/7037989725776416006), cut 8.26-13.59s.
- House payoff: [`7040511124625755397`](https://www.tiktok.com/@trademeproject/video/7040511124625755397), cut 27.00-33.00s.
- Factual cross-check: [NBC News — How a TikToker traded her way from a bobby pin to her dream house](https://www.nbcnews.com/pop-culture/pop-culture-news/tiktoker-traded-way-bobby-pin-dream-house-rcna8552).
- Independent factual cross-check: [The Guardian — From hairpin to house: woman who mastered 'trading up' realizes dream](https://www.theguardian.com/lifeandstyle/2021/dec/11/demi-skipper-trade-me-project-bobby-pin-house).
- Footage used: five non-contiguous cuts across four TikTok uploads, 21.73s total in a 45.53s output. Every cut is below 15s; aggregate source share is 47.73%.
- Full provenance and source specs: `output/projects/trademe/source/manifest.md`.

## Why This Segment

**Multi-Clip Mashup** (ADR-0022) — no single upload contains the complete proof chain. The hook card, original bobby pin, tractors, card-to-trailer quote, and house reaction occur in separate TikToks. Combining only the proof beats makes the disputed trade legible without replaying any source clip for more than six seconds.

This is the first **Proof-First Narrative / Impossible Trade Ladder / Worst-Trade Reversal** test selected under ADR-0027. The story supplies visible evidence before the finance lesson: a bobby pin becomes a chain of increasingly valuable assets, the apparently illiquid Celebrity Card finds one unusually motivated buyer, and the resulting trailer reaches a house flipper. That makes Counterparty Value concrete rather than presenting it as generic advice.

The title intentionally reveals the house, as allowed by ADR-0027, but withholds the mechanism. This is a testable finance-format hypothesis, not a promise that one upload will reach one million views.

## Hook Formula Applied

- **Frame-0 face + proof object** (ADR-0017): Demi's face and the Chipotle Celebrity Card are both visible at frame 0. The opening is not a title card or full-screen B-roll.
- **Audience-attributed contradiction**: “Her followers called this her worst trade” conflicts with the visible card and opens the question of why she accepted it.
- **Claim precision**: the hook and title say “her followers,” not “everyone,” and never imply that Demi herself called the trade bad. NBC News and The Guardian support the audience-attributed version.
- **Gap remains open**: the title reveals the eventual house, but neither title nor hook explains how a hard-to-sell card unlocked it. The right-buyer mechanism is withheld until the explanation section.
- **Caption sync/cadence** (ADR-0018): the first caption is present at t=0; the three hook bursts update inside the opening four seconds while the real subject/card remain in motion.
- **Payoff sequence**: the card-to-$40,000-trailer proof begins at t=21.50s; the trailer-to-house setup starts at t=30.83s; the original house reveal/reaction begins at t=34.83s.

## Final narrative

- Planned destination: MONEY BLINDSPOT, English (ADR-0027)
- Actual uploaded channel: Doog Radio (`UCqCJeIrbppZXoDM4iQjJZrw`), verified from the public YouTube video metadata. This differs from the configured finance-channel ID for MONEY BLINDSPOT and must be confirmed before OAuth metrics fetch.
- Retention engine: Proof-First Narrative / Worst-Trade Reversal
- Hook: “Her followers called this her worst trade.”
- Reveal: three tractors → Chipotle Celebrity Card → off-grid trailer → house
- Teaching frame: Counterparty Value
- Ending: “She didn't need a better item. She needed the right buyer.”
- CTA: none

“Her followers” is deliberate. Direct source footage shows Demi calling the card trade one of her best trades, while NBC News and The Guardian report that followers criticized it as her worst. The video does not attribute the negative judgment to Demi or inflate it to “everyone.”

## Value-Adds (Transformative Gate, ADR-0007)

- **fact-check/source-citation overlay** — NBC News + The Guardian support the follower-criticism claim and reported trade values.
- **data-viz overlay** — animated bobby-pin → cars/cabin → tractors → Celebrity Card ladder and the reported $20K → $40K value bridge.
- **animated counterparty annotation** — crowd valuation vs. the one buyer who cared about the card, resolving to “VALUE = ITEM × BUYER FIT.”
- Commentary track: pass — Edge neural TTS controls hook, framing, explanation, and lesson; original audio is retained only for the trailer quote and house reaction.
- Every source cut under 15s: pass — longest cut is 6.00s
- Aggregate source footage at or below 50%: pass — 652/1,366 frames = 47.73%
- Source manifest: `output/projects/trademe/source/manifest.md`
- Frame-accurate script: `output/projects/trademe/scripts/script.md`

## Automated verification

| Check | Result |
|---|---|
| Resolution / aspect | Pass — 1080x1920, 9:16 |
| Duration | Pass — 45.533333s, below 60s |
| Video codec | Pass — H.264 High |
| Pixel format | Pass — yuv420p |
| Frame rate / frame count | Pass — 30fps / 1,366 frames |
| Audio codec | Pass — AAC-LC, 48kHz stereo |
| Full decode | Pass — ffmpeg completed with no errors |
| Python syntax | Pass — `py_compile` |
| Git whitespace | Pass — `git diff --check` |
| Integrated loudness | Pass — -14.53 LUFS |
| True peak | Pass — -0.64 dBTP, no clipping |
| Long unintended silence | Pass — no 5–6s gaps after audio fix; only 0.25–0.92s sentence-boundary/tail pauses |
| Trailer quote window | Pass — max volume -1.1 dB |
| House reaction window | Pass — max volume -0.6 dB |
| Final mix transcription | Pass — all nine narrator beats, the trailer quote, and “Oh my God!” recovered |
| House reaction transcription | Pass — isolated source WAV and final 6s window both transcribe as “Oh my god!” |

## Manual visual verification

- Hook frame 0 contains Demi's face and the Celebrity Card.
- Hook caption is present at t=0 and t=0.2s.
- Caption does not cover Demi's face or the card.
- Continuous subject/card motion fills the opening; macro card proof lands at about t=3s.
- No full-screen B-roll blackout occurs in the hook window.
- Bobby pin, tractors, Celebrity Card, off-grid trailer, and house are each visually identifiable.
- Source quote captions render in order; `$40,000` appears in full.
- House payoff follows tension → reveal → reaction; “A HOUSE” appears after the reveal.
- Text remains inside safe areas; no clipped text, tofu glyph, blank frame, or malformed font was found.
- The first ending render leaked the internal note “THE CARD LOOPS BACK TO THE OPENING.” Manual QA caught it; the final artifact replaces it with “SAME ITEM. DIFFERENT OUTCOME.”
- Final card/buyer formula creates a semantic hard loop back to the opening card shot.

## Known Issues

- No unresolved render, spec, caption, or audio defect remains in the canonical artifact.
- Resolved during production: the first source-audio extraction produced digital silence despite a successful decode; input-side seek plus source/final-window loudness guards now catch this class of failure.
- Resolved during production: the first verified macOS TTS pass sounded flat because five of nine lines were slowed to 0.72x. The canonical render now uses Edge neural TTS with no post tempo below 1.0x.
- Resolved during visual QA: an internal editing note appeared in the first ending card and was replaced before delivery.
- Residual external risk: public TikTok footage can still trigger Content ID/copyright action despite the documented transformative treatment. This is not a render defect and cannot be eliminated by metadata.

## Audio bug found and fixed

The first full render decoded successfully but both original-audio windows were digital silence. Root cause: output-side `-ss` was applied after time-based `afade` processing, so `afade` evaluated absolute source PTS and reduced the selected ranges to zero.

The renderer now:

1. Performs input-side seek (`-ss` before `-i`).
2. Resets local audio time with `asetpts=PTS-STARTPTS`.
3. Rejects silent extracted WAVs with `volumedetect`.
4. Rejects silent trailer/reaction windows in the final mix.

This regression guard is also documented in the `clip-curation-edit` skill.

## TTS energy redesign

The first verified artifact used macOS `say -v Ava`. Five of nine narrator lines were slowed to `atempo=0.72` to fill their visual windows, producing flat cadence and synthetic-sounding prosody.

The canonical artifact now uses:

- Engine/voice: Edge-TTS 7.2.8, `en-US-AriaNeural` (positive/confident profile).
- Beat-specific engine direction: rates from +4% to +14%; pitch from 0Hz to +4Hz.
- No slow-stretch: every post tempo is at least 1.0; verified range is 1.000000–1.113812.
- Shorter contrast phrasing for the three beats that could not fit naturally: criticism, buyer, and value.
- Light vocal compression, high-pass filtering, and per-line -16 LUFS normalization before final mixing.
- Sample-exact 48kHz fitting after `loudnorm`; every line matches its frame window and reports `truncated: false`.

Evidence:

- Timing report: `output/projects/trademe/clips/v1_work/checks/tts_energy_report.json`
- Narrator-only preview: `output/projects/trademe/clips/v1_work/checks/tts_neural_preview.wav`
- Preview transcript: `output/projects/trademe/clips/v1_work/checks/tts_neural_preview.transcript.json`
- Final transcript: `output/projects/trademe/clips/v1_work/checks/final_transcript.json`

The prior verified render is preserved for A/B listening at `output/projects/trademe/final/2026-07-14-trademe_v1_worst_trade_house_macos_tts.mp4`, SHA-256 `214dd790ac123f0860e0b9564b5364788452d7bdb227719458ed55261a77f551`.

## Residual risk

This is a production-ready hypothesis, not a guarantee of one million views. Distribution still depends on topic-channel fit, packaging, initial audience matching, and platform variance. Public TikTok footage also retains Content ID/copyright risk despite the documented transformative treatment and source attribution.

## What To Check At 48h

Uploaded as [`qSjvMJ9oBzs`](https://youtube.com/watch?v=qSjvMJ9oBzs). Complete this section no earlier than 2026-07-16 13:28:45 +07, after the mandatory 48-hour wait.

- Studio `Stayed to watch` and AVD may be compared with the existing MONEY BLINDSPOT finance videos as a creative-retention benchmark only. Do not compare views, impressions, or CTR as if distribution were controlled: this upload is on Doog Radio, a different channel ID with different audience history. Use Studio values as ground truth; do not treat YouTube Analytics API `averageViewPercentage` as the Shorts-specific Stayed metric.
- First 0-4s retention: does the face + Celebrity Card + “worst trade” contradiction hold viewers through all three hook-caption bursts?
- t=4.00-7.50s: watch for a drop when the video moves from real source footage to the animated tractors/card criticism panel. This is the earliest format-switch risk.
- t=17.70-21.50s: does the “dead weight / one buyer” explanation retain viewers long enough to reach the original $40,000 trailer proof?
- t=21.50-26.83s and t=34.83-40.83s: check whether the real quote and “Oh my God!” house reaction create retention peaks relative to the TTS-led sections.
- Title/packaging: manually inspect any Studio CTR/impressions data that is available; the public YouTube Analytics API does not expose a valid per-video impressions/CTR metric for this workflow.
- Comments: look for confusion about whether Demi called it her worst trade, skepticism about the reported values, or viewers repeating the right-buyer lesson. The first theme would indicate the audience attribution still needs to be clearer.

## Post-Production Retro

### Hook Retro

- Verbal: no stronger factual version found. “Everyone called this her worst trade” is punchier but unsupported; “Her followers called this her worst trade” preserves the contradiction without inventing consensus. The upload title reveals the house but still withholds the right-buyer mechanism, matching ADR-0027.
- Visual: none found after the final frame check. Frame 0 contains Demi's face and the Celebrity Card, the caption is already present, and real subject/card motion continues through the hook. Replacing this with a macro card-only opening would weaken the confirmed face-at-frame-0 rule.
- Audio: user review caught a real hook-quality weakness that automated spec checks could not detect: macOS TTS plus 0.72x slow-stretch sounded lifeless. The final voice uses beat-specific neural prosody and never slows speech to fill a slot.
- Comparison tool: no additional `viral-video-analysis` run was performed for this retro. The format and hook were already selected through the ADR-0027 research/grilling process; this retro focused on the observed TTS defect and final artifact evidence.

### Workflow Delta

Yes. Stage 4 previously verified only the presence/specs of audio, not synthetic-narrator energy or truncation. This production proved that a file can pass decode/loudness checks while its TTS still sounds stale because the renderer slow-stretches speech. `docs/WORKFLOW.md` Stage 4 now requires a spoken-TTS preflight: synthesize all lines before the full render, reject `atempo < 1.0`, record per-line timing/truncation, and transcribe a narrator-only preview. The ffmpeg seek/fade silence pitfall and sample-exact post-`loudnorm` fitting are also recorded in the `clip-curation-edit` skill.
