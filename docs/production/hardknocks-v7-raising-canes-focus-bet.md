# HardKnocks V7 — Raising Cane's Focus Bet

## Status

| Field | Value |
|---|---|
| Rendered | 2026-07-15 |
| Uploaded | 2026-07-15 (user-reported); live public metadata reports `upload_date=2026-07-16`; exact upload time unavailable |
| YouTube Video ID | [`3mfOtQLLt1Y`](https://www.youtube.com/watch?v=3mfOtQLLt1Y) |
| Public metadata | Title matches; channel `MONEY BLINDSPOT`; public; duration 47s |
| Studio Analytics | https://studio.youtube.com/video/3mfOtQLLt1Y/analytics/tab-overview/period-default |
| Metrics fetch after (48h rule) | 2026-07-18 or later (conservative deadline from the public 2026-07-16 date because exact upload time is unavailable) |
| Metrics status | Not yet fetched — wait until 48h after the public upload date |
| Upload metadata | Complete in `## YouTube Metadata` below |

- Source locked and downloaded at maximum available 2160p.
- Stage 0 Hook Gate: passed on 2026-07-15.
- Final render and post-render verification: passed on 2026-07-15.

## Source

- Channel: The School of Hard Knocks
- Video: `How I Turned $50,000 Into $20 Billion`
- Video ID: `n5EmUiLNVjg`
- URL: https://www.youtube.com/watch?v=n5EmUiLNVjg
- Source duration: 990.361s
- Downloaded streams: 3840×2160 AV1 at 30000/1001fps + Opus 48kHz stereo
- Registry: `data/source_videos.csv`
- Word transcript: `output/projects/hardknocks/source/n5EmUiLNVjg_transcript.json`

## Editorial Thesis

The professor graded the restaurant plan last because a chicken-fingers-only concept looked too narrow. The same constraint became the focus bet: one core product, enough funding to open one location, then a repeatable product/team/scaling rule.

This is an editorial interpretation, not a claim that menu focus alone caused Raising Cane's growth. The dollar and scale statements remain explicitly source-reported.

## Hook Gate

### Locked hook source

- Source: 188.60–199.32s
- Frame-locked render boundary: 188.600–199.367s to preserve the last spoken word without entering the next sentence
- Verbatim VO:
  > The professor gave it the worst grade in the class because he said the plan was good, but the concept will never work. Serving just chicken fingers while other restaurants at the time were adding menu items, variety, they're adding healthy items, said it would never work.

### Hook text

- Frame 0: `THE WORST GRADE`
- Progressive reveal: `GOOD PLAN` → `BAD CONCEPT?` → `JUST ONE PRODUCT`
- The brand/outcome is withheld at frame 0.

### Visual evidence

- Frame 0 is a real moving two-person outdoor interview shot in front of a Raising Cane's vehicle.
- Todd Graves and the interviewer are both visible.
- The active speaker is Todd; portrait crop target is approximately `crop_focus=0.28`, not center crop.
- 0–3s motion gate at 10fps:
  - frames: 30
  - median consecutive-frame MAD: 3.908
  - minimum MAD: 2.531
  - threshold: >1.0
  - result: pass; not a freeze frame
- Contact sheet: `output/projects/hardknocks/clips/v7_work/candidates/contact.jpg`

## Locked Source Windows

| Beat | Source window | Raw duration | Required final word |
|---|---:|---:|---|
| Rejection + focus | 188.600–199.367s | 10.767s | `work` |
| Funding proof | 299.160–313.227s | 14.067s | `1996` |
| Scale proof | 354.620–364.287s | 9.667s | `Yeah` after `$20 billion` |
| Rebuild rule | 760.600–774.033s | 13.433s | `it` after `scale` |

All source excerpts remain below 15 seconds. Frame-locked selected source total is 47.933 seconds, 4.84% of the 990.361-second source.

## Storyboard

| Final time | HEIT | Source beat | Visual / editorial layer |
|---:|---|---|---|
| 0–3s | Hook | Professor gave it the worst grade | Moving Todd face; yellow 1–3-word captions; no brand/outcome reveal |
| 3–10s | Hook → Explain | Good plan, concept would never work | Todd stays visible; animated `GOOD PLAN / BAD CONCEPT?`; no full-screen proof |
| 10.20–24.35s | Explain → Illustrate | Only chicken fingers; $50K equity + $50K SBA + old restaurant | Product proof after the protected face window; capital stack and team insert |
| 24.35–33.82s | Illustrate | $400M best year + north of $20B | Escalating numbers followed by bottom-safe `SOURCE-REPORTED` label |
| 33.82–47.34s | Teach | Stick to what you know; cravable product, focus, team, scale | Four-step framework; source citation; end on `scale it`, no CTA; 0.203s protected audio tail |

The final retention speed is 1.02×. The selected speech was already approximately 266 WPM with a maximum selected inter-word gap of 0.36s, so no pause cut was warranted.

## HEIT Mapping

- Hook: the worst grade and the withheld reason.
- Explain: one-product focus contradicted menu-variety orthodoxy.
- Illustrate: initial capital stack, first location, and source-reported scale.
- Teach: cravable product → focus → team → scale.

## WEALTHIAN Formula Mapping

- Familiar object: chicken fingers / Raising Cane's.
- Authority: Todd Graves explains his own plan and operating rule.
- Hidden mechanism: apparent menu narrowness reframed as focus.
- Physical proof: restaurant/kitchen/product visuals and the interview location.
- Numbers: $50K + $50K SBA; $400M; north of $20B, all attributed to the source.
- Reframe: breadth was not the only path; disciplined focus became the bet.

## Transformative Gate

- Commentary: self-authored progressive analysis captions and framework overlays, visually distinct from verbatim subtitles.
- Value-add 1: `VARIETY` vs `ONE CORE PRODUCT` comparison.
- Value-add 2: $50K + $50K capital stack.
- Value-add 3: source-reported scale card.
- Value-add 4: cravable product → focus → team → scale framework.
- Source citation: compact persistent/recurring source label.
- Cut fraction: approximately 4.85% of original source, below 50%.
- Every source excerpt: <15s.
- Voice: original interview only; no neural TTS interruption.

## Pexels Evidence

| Pexels ID | Local asset | Actual ffprobe spec | Use |
|---|---|---|---|
| `9829921` | `output/shared/pexels/fried_chicken_9829921.mp4` | 1440×2560 H.264, 5.738s | Full-screen product proof at raw 10.40–12.80s; final 10.196–12.549s |
| `4253352` | `output/shared/pexels/restaurant_team_4253352.mp4` | 1080×1920 H.264, 22.04s | Corner team insert at raw 20.40–23.40s and full-screen team proof at raw 42.00–45.00s |

- Manual start/mid/end review: both assets passed; relevant moving footage; no competing brand, logo, menu, watermark, or text.
- OCR: no text detected on six sampled frames.
- Motion: median consecutive-frame MAD 3.955 for product footage and 8.787 for team footage.
- The API/CDN rendition labeled 1080×1920 for `9829921` delivered only 720×1280. It was rejected and replaced with a rendition that ffprobe confirmed as 1440×2560.

## Claim Provenance and Fact Check

- Primary voice/source: Todd Graves in The School of Hard Knocks video `n5EmUiLNVjg`.
- Raising Cane's official history confirms the chicken-fingers-only concept, lowest class grade, bank rejection, and 1996 opening: https://www.raisingcanes.com/who-we-are
- Forbes' Todd Graves profile confirms the lowest grade, 1996 launch using savings and an SBA loan, approximately 900 locations, and a real-time net-worth estimate of $22B as of 2026-07-13: https://www.forbes.com/profile/todd-graves
- Forbes' 2025 financial analysis says the limited menu helps keep costs down and reports $5.1B in 2024 sales: https://www.forbes.com/sites/chasewithorn/2025/04/09/raising-canes-billionaire-founder-nearly-doubles-his-fortune-after-record-year
- The exact `$50K` personal-equity and `$50K` SBA amounts, plus the `$400M` single-year personal claim, were not independently established by the consulted sources. They remain Todd/source-reported and the video displays a `SOURCE-REPORTED` label after the number sequence.
- Final ASR rendered `1996` as `1990`; this is a model transcription error, not an edit error. The source word-timestamp output contains `1996.` at 312.840–313.200s, and both Raising Cane's and Forbes independently confirm 1996.

## Caption Policy

- Burned caption visible by t=0.2s.
- Hook bursts: 1–3 words.
- Body bursts: 2–5 words.
- Verbatim text is derived from MLX word timestamps using raw token concatenation.
- Editorial analysis is visually separated and never styled as a spoken quote.
- Yellow/white/black visual grammar follows the WEALTHIAN benchmark, while safe zones and face-window rules follow this repository.

## YouTube Metadata

### Title

`His Professor Said It Would Never Work. Now He's Worth $20B`

### Description

His professor said a restaurant built around one core product would never work. Todd Graves kept the focus, combined $50,000 of his own equity with a $50,000 SBA loan, rebuilt an old restaurant, and scaled Raising Cane's.

The lesson isn't “sell chicken.” It's build around a craveable product, focus the operation, build the team, then scale. The exact $50K loan amounts and $400M single-year figure are Todd Graves' source-reported claims; Forbes estimates his current net worth at about $22B as of July 13, 2026.

Source interview: School of Hard Knocks — https://www.youtube.com/watch?v=n5EmUiLNVjg

#Entrepreneurship #BusinessStrategy #Shorts

### Hashtags

`#Entrepreneurship #BusinessStrategy #Shorts`

### YouTube Tags

`Todd Graves, Raising Cane's, Raising Canes, School of Hard Knocks, entrepreneur, entrepreneurship, business strategy, restaurant business, focus strategy, startup story, business case study, founder story, SBA loan, chicken fingers, YouTube Shorts`

## Verification Results

- V7 unit tests: 17/17 passed.
- Full `pipeline/hardknocks` tests: 28/28 passed.
- Duration: 47.343s.
- Resolution: 1080×1920.
- Video: H.264, yuv420p, 30fps.
- Audio: AAC, 48kHz, stereo.
- Integrated loudness: -15.7 LUFS; true peak: -0.5 dBFS.
- Required dialogue-window max volumes: hook -0.6dB; funding -0.8dB; scale -0.8dB; rebuild -0.7dB.
- Full decode: passed.
- Black events ≥0.10s: 0.
- Freeze events ≥1.5s: 0.
- Silence events ≥0.45s at -35dB: 0.
- First Pexels full-screen proof: final t=10.196s, outside protected 0–10s face window.
- First hook caption: final t=0.098s; manually visible at t=0.20s.
- Final ASR recovers the funding, `$400 million`, `$20 billion`, `craveable product`, `focus`, `build a team`, and final `scale it` payoff.
- Final ASR last word ends at 47.140s; container ends at 47.343s; protected tail margin: 0.203s.
- Manual visual review: moving Todd at frame 0; no original subtitle leak; no clipping; product/team evidence relevant; `SOURCE-REPORTED` bottom-safe; ending framework complete.
- Evidence: `output/projects/hardknocks/clips/v7_work/checks/validation.json`, `final_asr_summary.json`, `detector_summary.json`, `hook_contact.jpg`, `contact.jpg`, and `27_43.00_build_team.jpg`.

## Final Artifact

- Path: `output/projects/hardknocks/final/2026-07-15-hardknocks_v7_raising_canes_focus_bet.mp4`
- Size: 31,425,441 bytes.
- SHA-256: `78f37463da4724b06459766e0adb6aaef4209ddc79a5d6040826c1365537647d`
- Spec: 47.343s, 1080×1920, H.264/yuv420p, 30fps, AAC 48kHz stereo.

## 48-Hour Metrics Checklist

After upload and at least 48 hours:

- views;
- Studio Stayed to Watch;
- Studio AVD in seconds;
- API averageViewPercentage as API-only rough signal;
- retention curve hook loss at 0–3s, 3–10s, and payoff completion;
- comments indicating focus insight, disbelief, or source-claim skepticism.

## Post-Production Retro

- Worked: authority-first rejection hook, one-product contradiction, physical chicken proof, capital stack, source-reported economic escalation, and a no-CTA operational reframe.
- Worked: original interview voice remained coherent after four hard cuts; no neural TTS interrupted Todd's authority.
- Worked: the 1.02× speed-up preserved legibility because the selected speech was already fast and contained no dead-air valley worth cutting.
- Fixed after manual review: an initial 340px black mask was unnecessary because the final zoom crop had already removed the source subtitles. Removing it restored the full portrait composition.
- Fixed after manual review: `SOURCE-REPORTED` initially overlapped Todd's head; it was moved to the bottom safe zone and protected by a regression test.
- Fixed after final ASR: video `tpad` alone left only 48ms after the last word. A finite 350ms audio pad raised the measured final margin to 203ms.
- Fixed after ffmpeg stack inspection: applying video and padded-audio finish filters in one command deadlocked the threaded scheduler. The renderer now finishes video and finite audio separately, then stream-copy muxes them.
- Not claimed: the edit does not say menu focus alone caused growth. Limited-menu cost benefits have outside support, but the narrative remains a focused case-study interpretation.

## Hook Retro

- Frame 0 contains Todd speaking and gesturing in moving interview footage.
- The caption is visibly readable by t=0.20s.
- Median 0–3s motion MAD is 3.908; minimum is 2.531; no freeze-frame/Ken-Burns-photo failure.
- The opening reveals the rejection but withholds brand/outcome; the mechanism unfolds through progressive 1.2–1.35s caption bursts.
- Todd's face remains visible throughout 0–10s; first full-screen product proof starts at final t=10.196s.
- No source subtitle leak and no bottom mask remain in the delivered render.

## Workflow Delta

- Pexels API requests through Python `urllib` returned 403 while curl with the same environment-held Authorization header returned 200. Continue using the skill's curl path.
- Pexels API `video_files` dimensions are not sufficient verification; always ffprobe the downloaded rendition and step up to UHD when the delivered file is undersized.
- Before adding a black bar to hide source captions, render one clean frame with the exact production crop/zoom. Crop may already remove them.
- When `atempo` shortens the last spoken line, use finite `apad + atrim`, not `tpad` alone, and require ≥0.20s final-ASR tail margin.
- Avoid a single ffmpeg graph for speed-adjusted video plus padded audio under `-shortest` if the scheduler deadlocks. Render the streams separately and stream-copy mux.
