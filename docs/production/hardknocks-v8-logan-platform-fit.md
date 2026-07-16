# HardKnocks V8 — Logan Paul Platform Fit

## Status

| Field | Value |
|---|---|
| Production | Complete |
| Render date | 2026-07-16 |
| Upload status | Uploaded; scheduled public at approximately 2026-07-16 19:00 +07 (user-reported) |
| YouTube Video ID | `-xSqHo7XjB8` |
| YouTube URL | https://youtube.com/shorts/-xSqHo7XjB8 |
| Upload reported at | 2026-07-16 18:30:34 +07 |
| Public metadata verification | Pending — scheduled video was not public when reported |
| Metrics status | Not yet fetched — wait at least 48 hours after public release |
| Metrics fetch after (48h rule) | Approximately 2026-07-18 19:00 +07 or later; replace with the exact public timestamp once available |
| Studio Analytics | https://studio.youtube.com/video/-xSqHo7XjB8/analytics/tab-overview/period-default |
| Final video | `output/projects/hardknocks/final/2026-07-16-hardknocks_v8_logan_platform_fit.mp4` |
| Renderer | `pipeline/hardknocks/render_hardknocks_v8.py` |
| Tests | `pipeline/hardknocks/test_render_hardknocks_v8.py` |
| Plan | `docs/plans/2026-07-16-hardknocks-v8-logan-platform-fit.md` |
| Framing ADR | `docs/adr/0030-active-speaker-reframing-and-semantic-zoom.md` |

## Editorial thesis

Logan Paul's apparent overnight success is reframed as a platform-fit story:

> rejection → nine to ten years of practice → 10,000 hours → Vine fits the skill → about $30M personally → Prime at $1.2B → great partners

The edit does not claim that practice alone guaranteed the outcomes. It preserves Logan's own explanation: he and Jake had already learned short-form video, Vine supplied a six-second format that fit those skills, and partners later helped scale Prime.

## Primary source

- YouTube ID: `ALvduf2Rz_c`
- URL: https://www.youtube.com/watch?v=ALvduf2Rz_c
- Title: "Asking One of the Richest Men on the Internet How He Got Rich!"
- Channel: School of Hard Knocks
- Local file: `output/projects/hardknocks/source/ALvduf2Rz_c.mp4`
- Downloaded source: 3840×2160
- Source duration: 956.383492s
- Spoken excerpts used: 55.4s raw, 5.79% of the primary source
- TTS: none; the final uses only the original interview voice

## Evidence and illustration sources

| Purpose | Source | Local asset | Source window | Final window | Treatment |
|---|---|---|---:|---:|---|
| Logan and Jake at their childhood home | Graham Bensinger, `R9ve03SbYqg` | `output/projects/hardknocks/source/evidence/logan_childhood_home_R9ve03SbYqg.mp4` | 160.40–163.60s | 10.10–13.20s | top-crop, focus 0.65 |
| Childhood-home action beat | Graham Bensinger, `R9ve03SbYqg` | same asset | 164.00–166.20s | 13.20–15.34s | top-crop, focus 0.28 |
| Actual young Logan Vine footage | Oddly Satisfying Motion, `cXNLpsB4zw4` | `output/projects/hardknocks/source/evidence/logan_vines_cXNLpsB4zw4.mp4` | 13.20–16.20s | 30.29–33.20s | top-crop; original compilation caption removed by crop |
| PRIME product proof | Logan Paul, `ebha0MzwtU8` | `output/projects/hardknocks/source/evidence/prime_commercial_ebha0MzwtU8.mp4` | 0.00–3.00s | 43.30–46.21s | full-screen product footage |
| Partner illustration | Pexels asset 7981954 | `output/shared/pexels/contract_signing_7981954.mp4` | 2.00–5.00s | 48.80–51.72s | full-screen handshake illustration |

Total evidence/illustration footage is 25.99% of the raw timeline. No full-screen evidence replaces a face before final t=10.097s.

## Exact edit map

| Final | Source | Speaker | Framing | Beat |
|---|---|---|---|---|
| 0.00–2.85s | 776.36–779.29s | Logan | close 1.36×, focus 0.36 | `weird_hook` |
| 2.85–8.48s | 756.02–761.82s | host | medium 1.20×, focus 0.70 | `overnight_question` |
| 8.48–14.95s | 761.84–768.51s | Logan | medium 1.20×, focus 0.36 | `started_at_nine` |
| 14.95–17.54s | 768.58–771.25s | Logan | close 1.36×, focus 0.36 | `not_a_job` |
| 17.54–21.78s | 779.28–783.65s | Logan | medium 1.20×, focus 0.36 | `nine_ten_years` |
| 21.78–26.57s | 783.70–788.63s | Logan | close 1.36×, focus 0.36 | `ten_thousand_hours` |
| 26.57–29.03s | 788.64–791.17s | Logan | close 1.36×, focus 0.36 | `goosebumps_work` |
| 29.03–33.27s | 791.64–796.01s | Logan | medium 1.20×, focus 0.36 | `vine_setup` |
| 33.27–36.93s | 796.00–799.77s | Logan | close 1.36×, focus 0.36 | `six_second_fit` |
| 36.93–40.00s | 802.12–805.29s | host | medium 1.20×, focus 0.70 | `personal_question` |
| 40.00–41.42s | 810.42–811.89s | Logan | close 1.36×, focus 0.36 | `thirty_million` |
| 41.42–43.30s | 812.72–814.65s | host | medium 1.20×, focus 0.70 | `company_question` |
| 43.30–45.50s | 815.96–818.23s | Logan | close 1.36×, focus 0.36 | `prime_billion` |
| 45.50–47.41s | 818.30–820.27s | host | close 1.36×, focus 0.70 | `scale_question` |
| 47.41–48.80s | 820.40–821.83s | Logan | close 1.36×, focus 0.36 | `great_partners` |
| 48.80–53.79s | 822.14–827.27s | Logan | medium 1.20×, focus 0.36 | `influencer_value` |

## Active-speaker and semantic-zoom decisions

- Host questions hard-cut to host focus 0.70.
- Logan answers hard-cut to Logan focus 0.36.
- Medium 1.20× is used for setup and reset beats.
- Close 1.36× is reserved for rejection, 10,000 hours, `$30M`, `$1.2B`, the scale question, and `great partners`.
- No periodic zoom pumping is used.
- The source's burned-in subtitles are removed by top-aligned vertical reframing; the edit burns its own short captions.

## Transformative Gate

### Commentary track

Pass. The original interview voice forms a new, coherent thesis by reordering three question/payoff arcs. No synthetic narration is added.

### Value-adds

Pass, with more than two distinct value-add categories:

1. Persistent source citation for School of Hard Knocks.
2. Multi-source mashup: childhood home, Vine, PRIME, and Pexels partner illustration.
3. Animated semantic captions with number/punchline emphasis.
4. Proof-coupled footage for Vine and PRIME.
5. Active-speaker reframing and semantic close-ups.

### Source-use limits

Pass.

- Every primary-source excerpt is under 15 seconds.
- Raw primary-source usage: 55.4s of 956.383492s = 5.79%.
- Final duration: 54.486s.
- The edit is substantially under the 50% source-duration limit.

## Claim treatment and fact-check notes

The spoken numbers are preserved as claims made by Logan in the primary interview.

- `9–10 years`, `10,000 hours`, `about $30M`, and `Prime made $1.2B in its second year` are source-reported claims, not presented as audited figures.
- Bloomberg independently reported in November 2023 that PRIME's annual sales had reached/on pace for approximately $1.2B, which supports the order of magnitude but does not independently establish every word of Logan's `second year` phrasing:
  - https://www.bloomberg.com/news/articles/2023-11-08/logan-paul-s-prime-energy-drinks-reach-1-2-billion-in-sales
- No reliable independent source was found during production for the exact personal `$30M` figure; the video therefore captions it as `ABOUT $30 MILLION` and the description says Logan `reports` it.

## Final technical validation

Generated report: `output/projects/hardknocks/clips/v8_work/checks/validation.json`

- Duration: 54.486s
- Resolution: 1080×1920
- Display aspect ratio: 9:16
- Video: H.264 High, yuv420p, 30fps
- Audio: AAC stereo, 48kHz
- Post-speed: 1.03×
- Hook caption appears at final t=0.097s
- First full-screen evidence begins at final t=10.097s
- Full decode: passed
- Final file size: 40,582,110 bytes
- SHA-256: `742e9c4ef1a63a48e77413a2f0bd79872468c46caf07e3df4bd4fb6888fe0c56`

## Audio and detector QC

Files:

- `output/projects/hardknocks/clips/v8_work/checks/detector.log`
- `output/projects/hardknocks/clips/v8_work/checks/detector_summary.json`

Results:

- Integrated loudness: -15.4 LUFS
- True peak: -0.4 dBFS
- Black-frame events: 0
- Freeze events ≥1.5s: 0
- Silence events ≥0.45s below -35dB: 0
- Window max-volume checks: -0.8dB to -0.4dB for the four narrative windows

## ASR re-transcription QC

Files:

- `output/projects/hardknocks/clips/v8_work/checks/final_asr.json`
- `output/projects/hardknocks/clips/v8_work/checks/final_asr_summary.json`

Results:

- ASR segments: 33
- All required semantic phrases recovered: `you guys are weird`, `nine, 10 years`, `10,000 hours`, `six second looping videos`, `30 mil`, `1.2 billion`, `great partners`, `build a brand`
- Last ASR word end: 54.260s
- Container duration: 54.486s
- Tail margin: 0.226s
- Speech ending is not cut off.

## Manual visual QC

Contact sheet: `output/projects/hardknocks/clips/v8_work/checks/contact.jpg`

Manually inspected:

- t=0.00s: moving Logan face at frame 0; no title card or black frame.
- t=0.20s: hook caption is visible, readable, and clear of the face.
- t=3.00s: hard cut correctly reframes to the host.
- t=10.00s: Logan remains visible through the protected 0–10s face window.
- t=10.50–15.00s: corrected, accurately sought childhood-home excerpts; Logan/Jake remain identifiable and the original lower watermark is cropped out.
- t=32.00s: actual young Logan Vine footage; original compilation caption/watermark is absent.
- t=43–46s: PRIME product evidence aligns with the `$1.2B` claim.
- t=48.8–51.7s: Pexels handshake is explicitly labeled as illustration.
- t=54.00s: stable Logan close; no black frame or abrupt visual cutoff.
- Captions stay inside the 1080×1920 safe area and do not expose source subtitles.

## Tests executed

```text
python3 -m unittest discover -s pipeline/hardknocks -p 'test_render_hardknocks_v*.py'
40 tests passed
```

The V8-specific suite was also rerun after the audio-tail fix: 13 tests passed.

## YouTube Metadata

### Title

`Logan Paul Worked 10 Years Before Making $30M`

### Description

Logan Paul says his “overnight” success took 9–10 years of making videos and 10,000 hours before Vine finally matched his skills. He later reports about a $30M personal year and says Prime reached $1.2B in its second year because great partners knew how to turn influence into a brand.

#LoganPaul #Entrepreneurship #Shorts

### Hashtags

`#LoganPaul #Entrepreneurship #Shorts`

### YouTube Tags

`Logan Paul, Logan Paul interview, Prime Hydration, entrepreneurship, business success, platform fit, Vine, YouTube creator, 10000 hours, creator economy, influencer marketing, School of Hard Knocks, business partners, overnight success, YouTube Shorts`

## Hook Retro

### Hypothesis

Starting on Logan's rejection line (`you guys are weird`) should create an unresolved social-status gap before the host asks how long success took. The first answer does not resolve the gap immediately; it escalates from rejection to nine years old, 9–10 years of practice, and 10,000 hours.

### Mechanical result

- Frame 0 is a moving Logan close-up, not a title card or freeze-frame.
- Hook caption is visible by 0.097s.
- Active-speaker face visibility is preserved through t=10.00s.
- The hook uses one semantic close and one hard speaker reframe rather than repeated zoom pumping.
- No performance claim is made yet; retention can only be judged after the normal 48-hour metrics window.

### Main risk to watch in analytics

The cold open quotes rejection before establishing the `overnight success` question. If viewers do not infer the connection quickly enough, retention may dip at the host handoff around t=2.85s. Compare the 0–3s and 3–8s retention slopes before reusing this ordering.

## Workflow Delta

1. External evidence excerpts are now pre-rendered with accurate post-input seeking before compositing. This avoids non-deterministic fast-seek behavior around dense edit points and makes contact-sheet review match the selected source window.
2. Evidence crops have their own `crop_focus`; a center crop had prioritized Jake over Logan in the childhood-home shot. The corrected windows use focus 0.65 and 0.28 around the two internal cuts.
3. Top-crop evidence mode removes compilation captions/watermarks without adding a black mask or pillarbox.
4. Final ASR initially left only 0.016s after the last detected word because `-shortest` selected the shorter audio stream. `AUDIO_FINISH_PAD` was raised to 0.70s and revalidated; the final ASR tail margin is 0.226s.

## Upload state

Uploaded by the user as YouTube Short `-xSqHo7XjB8`:

- URL: https://youtube.com/shorts/-xSqHo7XjB8
- Reported at: 2026-07-16 18:30:34 +07
- Scheduled public time: approximately 2026-07-16 19:00 +07
- Public-page verification: pending until the scheduled release is live
- Metrics: do not fetch before approximately 2026-07-18 19:00 +07; use the exact public timestamp if YouTube exposes one after release

No commit or push was performed.
