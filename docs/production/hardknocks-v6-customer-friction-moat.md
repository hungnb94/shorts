# hardknocks_v6 — “They Said His Store Would Go Broke. It Became Home Depot.”

## Status

| Field | Value |
|---|---|
| Source | [Asking Atlanta Billionaires How They Got Rich!](https://www.youtube.com/watch?v=cxYLRCwX_aM) |
| Revision | Original-voice continuity revision |
| Rendered | 2026-07-15 |
| Uploaded | 2026-07-15 (time not provided) |
| YouTube Video ID | `Ff12XXpiVCM` |
| Studio Analytics | https://studio.youtube.com/video/Ff12XXpiVCM/analytics/tab-overview/period-default |
| Metrics fetch after (48h rule) | 2026-07-17 or later |
| Metrics status | Not yet fetched — wait until 48h after upload |

## Deliverables

- Final video: `output/projects/hardknocks/final/2026-07-15-hardknocks_v6_customer_friction_moat.mp4`
- Upload metadata: `output/projects/hardknocks/final/2026-07-15-hardknocks_v6_customer_friction_moat_metadata.txt`
- Renderer: `pipeline/hardknocks/render_hardknocks_v6.py`
- Tests: `pipeline/hardknocks/test_render_hardknocks_v6.py`
- QC: `output/projects/hardknocks/clips/v6_work/checks/`
- Verified transcript: `output/projects/hardknocks/clips/v6_work/checks/final_transcript.txt`

## Verified Video Specs

- Duration: 57.419s (59.067s selected timeline + 0.70s final-frame flush, 1.04x retention speed-up)
- Resolution: 1080x1920, 9:16 portrait
- Frame rate: 30fps
- Video: H.264
- Audio: AAC, 48kHz, stereo
- File size: 33,822,927 bytes (~32.3 MiB)
- Bit rate: 4,712,436 bps
- SHA-256: `f0c46a8e38fcaf3e493e6164d1df736f4cb7d4ece1c77640dd53ac92b4912656`
- Full ffmpeg decode: passed
- Peak checks: hook -2.7dB, middle interview -0.7dB, trust payoff -0.7dB

## Editorial Decision

The first render inserted a 23-second neural-commentary block after “fired at 36” and replaced the natural ending with a TTS conclusion. Human review found both transitions narratively incoherent.

The accepted revision uses Arthur Blank’s and the interviewer’s original voices throughout. The story now advances without an artificial narrator:

> predicted failure → Home Depot reveal → fired at 36 → public-company proof → listening and humility → trust payoff

Editorial transformation is supplied by clip selection, reordered proof, short synchronized captions, two small Pexels evidence inserts, zoom/cut cadence, music, and impact sound—not by interrupting the interview.

## Narrative Structure

### Hook — 0.00–5.96s

Arthur recounts the escalating criticism:

- “These guys are nuts.”
- “There’s too much inventory.”
- “Too many people on the floor.”
- “Price levels are too low.”
- “They’re gonna go broke.”

`THEY CALLED HIM` appears at final t=0.096s. The Home Depot identity remains withheld.

### Reveal and origin — 5.96–16.35s

- Home Depot reveal: “That’s how I got rich. That was my company.”
- The interviewer supplies the missing origin: fired at 36.
- The question “Did people doubt you or think you were crazy?” connects the opening criticism back to Blank’s answer.
- Blank answers “Absolutely,” without a TTS interruption.

### Proof and mechanism — 16.35–41.73s

- Home Depot went public in September 1981.
- Volumes and revenue from the first four stores were unbelievable.
- Blank attributes the result to listening and responding.
- He rejects debating customers or forcing arguments on them.
- The section ends on humility: the people being served know better than the company does.

### Payoff — 41.73–57.42s

Blank’s own closing principle remains intact:

- Build trust with associates and customers.
- Trust opens hearts and minds.
- Eventually it opens wallets.
- Final spoken payoff: “They have a trust relationship.”

There is no unrelated CTA panel or neural-voice conclusion.

## Hook Gate / First 10 Seconds

- Frame 0 is moving source footage, not a freeze frame or title card.
- Frame-0 skin-tone share: 24.61%, above the 10% ADR-0017 threshold.
- Apple Vision found one face at frame 0 and every sampled narrative checkpoint through the ending.
- Caption appears at t=0.096s; prior t=0.20 OCR read `THEY CALLED HIM` with confidence 1.000.
- No Pexels insert or full-screen replacement enters the first 10 seconds.
- Final Whisper transcript confirms the complete phrase “They’re gonna go broke.”

## Transformative Gate

Passed:

1. **Editorial commentary** — story construction and synchronized self-authored emphasis captions frame the proof/mechanism without synthetic narration.
2. **Animated annotation** — short 2–5-word bursts identify the public-company proof, listening mechanism, humility, and trust funnel.
3. **Pexels evidence** — unbranded warehouse footage appears as two 300×533 corner inserts; it never replaces the speaker or the original audio.
4. **Multi-clip mashup** — 25 short source pieces with changing zoom, captions, Pexels, music bed, impact sound and progress indicator.
5. **Source-duration ceiling** — selected footage is 3.58% of the 1,647.621s source video.
6. **Per-clip ceiling** — every source piece is under 15s; the longest is under 4s.
7. **Original voice** — `tts_report.json` is an empty list; no neural TTS is mixed into the final audio.

## Assets

### Primary source

- Channel: School of Hard Knocks
- Video ID: `cxYLRCwX_aM`
- Title: `Asking Atlanta Billionaires How They Got Rich!`
- Source duration: 1647.621s
- Source language: English
- Local source: `output/projects/hardknocks/source/cxYLRCwX_aM.mp4`
- Source specs: 3840x2160 AV1, 29.97fps; Opus stereo 48kHz
- Captions: `output/projects/hardknocks/source/cxYLRCwX_aM.en.json3`

### Pexels

- Query: `warehouse inventory worker`
- Video ID: `7018664`
- URL: https://www.pexels.com/video/woman-checking-the-inventories-in-the-warehouse-7018664/
- Local file: `output/shared/pexels/inventory_worker_7018664.mp4`
- Used as corner evidence at raw t=24–29s and 33–38s (first final appearance t=23.077s)
- OCR review found no conflicting consumer brand in the used windows.

## YouTube Metadata

### Title

They Said His Store Would Go Broke. It Became Home Depot.

### Description

“Too much inventory. Too many employees. Prices too low.”

Critics predicted Arthur Blank’s new stores would go broke. Instead, Home Depot went public in 1981—and the revenue from its first four stores shocked people.

Blank’s explanation was simple: listen to customers, learn from them, and build enough trust that they open their hearts, minds, and eventually their wallets.

Which customer signal are most businesses ignoring?

#homedepot #business #entrepreneur #shorts

This text is byte-identical to `output/projects/hardknocks/final/2026-07-15-hardknocks_v6_customer_friction_moat_metadata.txt`.

## Automated and Manual QC

- Renderer unit tests: 11/11 passed.
- Timeline continuity and 45–60s duration gates: passed.
- Original-voice-only gate: passed.
- Source-duration and per-clip limits: passed.
- ffprobe codec/spec gate: passed.
- Full-file ffmpeg decode: passed.
- Frame-0 face/skin-tone gate: passed.
- Face detection at t=0, 10.3, 14.5, 25, 33.5, 42.5, 52 and 55.5s: passed.
- OCR at 13 representative middle/end frames: confidence 1.000; no clipped caption was detected.
- Black scan: no black segment reported.
- Silence scan (`-35dB`, ≥1.0s): no interval reported.
- Manual contact-sheet review: one consistent interview composition through the ending; Pexels remains a small supporting insert; no full-screen panel.
- Final semantic-audio verification: complete hook, middle proof, humility payoff and final “trust relationship” phrase are present.

## Post-Production Retro

### What changed after human review

1. Removed every neural TTS segment.
2. Removed all full-screen strategy/guardrail/CTA panels.
3. Rebuilt 13–41.7s from the contiguous logical sequence: doubt → public proof → revenue → listening → humility.
4. Rebuilt 41.7s–end from Blank’s trust explanation and retained “trust relationship” as the final spoken phrase.
5. Converted Pexels from full-screen replacement to two small corner inserts while keeping Blank visible and audible.
6. Rewrote metadata to match the revised video.

### Defects found and fixed during revision

1. The hybrid TTS block was locally understandable but globally broke the interview’s cause-and-effect flow.
2. The TTS ending replaced a stronger natural source payoff.
3. The first revised cut ended humility before “know better than we do”; the source window was extended and protected by a test.
4. The first trust cut began after “In all these,” producing a grammatical jump; it was re-anchored at 1591.52s.
5. The final speed-up initially cut off the word “relationship.” Root cause: the speed-adjusted video ended before the decoded/tempo-adjusted AAC tail. The renderer now pads the final video by 0.70s while leaving the original audio unpadded, then uses `-shortest`; Whisper-large-v3 confirms the complete final phrase.
6. `apad` before or after `atempo` deadlocked this ffmpeg build (0% CPU, 48-byte output). A four-variant reproduction isolated `apad` as the cause; it is not used in the accepted pipeline.

### Remaining trade-off

The last frame is held briefly while the final word resolves. This is preferable to clipping the semantic payoff and occurs only at the ending, not in the 0–3s hook window.

### 48h check after upload

- Retention through the Home Depot reveal at t≈6–10.4s.
- Retention around the original-voice proof transition at t≈16–21s.
- Whether the corner Pexels inserts at t≈23.1s and t≈31.7s improve visual cadence without distracting from Blank.
- Completion rate through the hearts → minds → wallets → trust-relationship payoff.
