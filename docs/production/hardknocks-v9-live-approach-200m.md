# HardKnocks V9 — Live Approach to the $100M/$10K Gap

## Status

| Field | Value |
|---|---|
| Production | Complete |
| Render date | 2026-07-17 |
| Upload status | Uploaded; public |
| YouTube Video ID | `U_3cCYOcCmk` |
| YouTube URL | https://youtube.com/shorts/U_3cCYOcCmk |
| Upload reported at | 2026-07-17 09:39:20 +07 |
| Public timestamp | 2026-07-17 09:38:08 +07 |
| Public metadata verification | Verified 2026-07-17 09:39 +07 — title matches, duration rounds to 56s, availability public, channel is MONEY BLINDSPOT (`UCG_yrDQF5Sj6iMTZB0KSBAA`) |
| Metrics status | Not yet fetched — wait at least 48 hours after public release |
| Metrics fetch after (48h rule) | 2026-07-19 09:38:08 +07 or later |
| Studio Analytics | https://studio.youtube.com/video/U_3cCYOcCmk/analytics/tab-overview/period-default |
| Final video | `output/projects/hardknocks/final/2026-07-17-hardknocks_v9_live_approach_200m.mp4` |
| Renderer | `pipeline/hardknocks/render_hardknocks_v9_v10_sohk.py --variant a` |
| Research | `docs/research/sohk-opening-pattern-2026-07/REPORT.md` |
| QC summary | `output/projects/hardknocks/clips/v9_work/checks/qc-summary.json` |

## Editorial thesis

The apparent `$200M` exit is reframed as an agency story:

> interrupted outside a mansion → sold to Blackstone for `$200M` → started with nothing in a basement → built a Yellow Pages internet program → company collected about `$100M` while his check was about `$10K` → decided to build on his own

The three money figures are claims made in the source interview. The edit does not present them as audited financial statements and does not claim the commission comparison alone caused the later exit.

## Primary source

- YouTube ID: `E_9nX5ReMcY`
- URL: https://www.youtube.com/watch?v=E_9nX5ReMcY
- Title: “Asking Mega Mansion Owners How They Got Rich!”
- Channel: School of Hard Knocks
- Local file: `output/projects/hardknocks/source/E_9nX5ReMcY.mp4`
- Downloaded source: 3840×2160
- Source duration: 1616.741s
- Raw primary-source use: 2.88% of the long source
- Every individual source excerpt: under 15 seconds

## Commentary track

Two short Aria bridges provide the new framing while leaving the interview voice dominant:

1. “The exit sounds instant. The origin story was nothing like it.”
2. “The company collected the upside. His commission check barely moved.”

Voice: `en-US-AriaNeural`, generated at `-2%` rate.

Final-window ASR recovered both bridges when checked independently:

- `checks/asr_windows/bridge1.wav`
- `checks/asr_windows/bridge2.wav`

## Evidence and illustration sources

| Purpose | Source | Local asset | Final window | Treatment |
|---|---|---|---:|---|
| `$200M` exit and buyback | Animated claim panel | generated in `v9_work/panels/a_exit.png` | 19.03–21.94s | continuously animated; labeled `INTERVIEW CLAIM` |
| Basement/home-work origin | Pexels 5725850 | `output/shared/pexels/home_laptop_5725850.mp4` | 24.27–28.16s | full-screen motion; labeled `ILLUSTRATION: PEXELS` |
| Yellow Pages/printed-directory beat | Pexels 36864123 | `output/shared/pexels/flipping_pages_36864123.mp4` | 40.78–44.66s | full-screen motion; labeled `ILLUSTRATION: PEXELS` |
| `$100M` versus `$10K` | Animated claim panel | generated in `v9_work/panels/a_gap.png` | 47.09–51.94s | continuously animated; labeled `INTERVIEW CLAIM` |

Total evidence/illustration usage: 27.68% of the raw timeline. The first full-screen evidence begins at final t=19.029s, after the protected 0–10s face window.

The rejected humanoid-robot Pexels candidate was not used; frame review showed a toy/demo robot that could misrepresent the founder's business.

## Exact edit map

| Final | Source | Speaker/type | Framing | Beat |
|---:|---:|---|---|---|
| 0.00–8.19s | 330.34–338.76s | live encounter | wide status approach + same-interview moving face inset | mansion interruption hook |
| 8.19–10.84s | 358.84–361.56s | host | focus 0.70, 1.20× | wealth question |
| 10.84–16.73s | 361.68–367.76s | subject | focus 0.30, 1.20× | advertising company / Blackstone setup |
| 16.73–20.94s | 368.68–373.00s | host | focus 0.70, 1.28× | sale-price question |
| 20.94–23.33s | 373.30–375.78s | subject | focus 0.30, 1.34× | `$200M`, then bought it back |
| 23.33–28.71s | TTS bridge 1 | commentary | subject visual, evidence overlay | instant exit versus slow origin |
| 28.71–29.94s | 377.90–379.18s | host | focus 0.70, 1.22× | startup-capital question |
| 29.94–33.01s | 379.18–382.36s | subject | focus 0.30, 1.32× | nothing / basement |
| 33.01–40.49s | 386.24–393.94s | host | focus 0.70, 1.18× | driving-factor question |
| 40.49–46.63s | 393.96–400.28s | subject | focus 0.30, 1.24× | Yellow Pages / internet program |
| 46.63–52.17s | TTS bridge 2 | commentary | subject visual, comparison panel | upside versus commission |
| 52.17–56.12s | 400.40–404.46s | subject | focus 0.30, 1.34× | `$100M`, `$10K`, “on my own” |

## Hook treatment

The selected live-approach source shot contains the mansion and moving host but does not show the interview subject's face clearly at frame 0. Using that source unchanged would violate ADR-0017.

The final treatment preserves the moving approach as the primary layer and adds a large, moving reaction inset from the same interview. This keeps:

- a human face visible from frame 0;
- mansion/status context visible;
- real motion throughout 0–8s;
- no stock footage or full-screen replacement in 0–10s.

Captions are present from frame 0 in short speech-synced bursts. An opaque lower caption band fully masks the source video's burned-in captions.

## Transformative Gate

### Commentary track

Pass. Two synthetic commentary bridges construct a new `instant exit versus constrained origin` interpretation. Original interview audio remains the majority.

### Value-adds

Pass, with more than two categories:

1. Persistent School of Hard Knocks source citation.
2. Two explicit commentary bridges.
3. Animated `$200M` and `$100M/$10K` claim panels.
4. Two labeled Pexels illustrations.
5. Active-speaker reframing and semantic close-ups.
6. New burst captions with money/decision emphasis.

### Source-use limits

Pass.

- Every primary-source excerpt is under 15 seconds.
- Raw primary-source usage: 2.88% of a 1616.741s source.
- Final duration: 56.133333s.
- The edit is substantially under the 50% source-duration limit.

## Claim treatment

- `$200M`, `$100M`, and `$10K` are explicitly treated as interview claims.
- The `$100M` amount is company collection/revenue language, while `$10K` is the speaker's commission check. The edit does not calculate or imply an audited profit ratio.
- The Pexels clips are labeled as illustrations and are not presented as archival footage of this subject.
- The metadata description uses “He says” to preserve claim provenance.

## Final technical validation

Generated reports:

- `output/projects/hardknocks/clips/v9_work/checks/validation.json`
- `output/projects/hardknocks/clips/v9_work/checks/qc-summary.json`

Results:

- Duration: 56.133333s
- Resolution: 1080×1920, 9:16
- Video: H.264, yuv420p, 30fps
- Audio: AAC stereo, 48kHz
- Post-speed: 1.03×
- Evidence usage: 27.68%
- First full-screen evidence: 19.029s
- Full decode: passed
- File size: 35,853,693 bytes
- SHA-256: `675bf72b1d633a3fd69710f043c479d3a08edb79e349202c71d112030e1236f6`

## Audio and detector QC

- Integrated loudness: -15.59 LUFS
- True peak: -0.61dBFS
- Loudness range: 1.50 LU
- Black-frame events: 0
- Freeze events ≥1.0s: 0
- Longest detected low-level interval below -45dB: 0.93525s
- Silence events ≥1.0s: 0
- Full decode: passed

The first panel render produced detector-visible frozen tails after its zoom reached a hard cap. The final renderer uses a continuous sinusoidal zoom; the final artifact reports zero freeze events ≥1.0s.

## ASR re-transcription QC

Files:

- `output/projects/hardknocks/clips/v9_work/checks/final_asr.json`
- `output/projects/hardknocks/clips/v9_work/checks/asr_windows/bridge1.wav`
- `output/projects/hardknocks/clips/v9_work/checks/asr_windows/bridge2.wav`

Required semantic phrases recovered:

- `Blackstone`
- `200 million`
- `started out in my basement`
- `Yellow Pages door to door`
- `collect a hundred million dollars`
- `ten thousand dollar check`
- `I'm doing this on my own`

The two TTS bridges were recovered in targeted window checks. Last full-file ASR word ends at 56.10s; the speech ending is not cut off.

## Manual visual QC

Files:

- Hook contact sheet: `output/projects/hardknocks/clips/v9_work/checks/hook_0_10.jpg`
- Whole-video sheet: `output/projects/hardknocks/clips/v9_work/checks/contact.jpg`
- Final frame: `output/projects/hardknocks/clips/v9_work/checks/final_frame.jpg`

Verified manually:

- frame 0 uses moving footage and has a clearly visible human face;
- mansion/status context remains legible;
- no full-screen evidence replaces the face in 0–10s;
- captions are visible at frame 0 and remain inside the safe area;
- source burned-in captions are fully masked;
- no tofu glyphs, cutoff captions, black frames, or blocking crop errors;
- the final payoff holds on the speaker and `ON MY OWN`.

## YouTube Metadata

### Title

`They Collected $100M. His Check Was $10K.`

### Description

He says a company collected about $100 million from an internet program he helped roll out—while his commission check was $10,000. That gap pushed him to build on his own, eventually selling a company to Blackstone for $200 million and buying it back.

#Entrepreneurship #BusinessStory #MoneyMindset

### Hashtags

`#Entrepreneurship #BusinessStory #MoneyMindset`

### YouTube Studio tags

`entrepreneur story, business motivation, 200 million company, 100 million revenue, 10000 commission check, Yellow Pages, Blackstone, how to get rich, business lessons, founder mindset, School of Hard Knocks, money mindset, business story, YouTube Shorts`

## Hook Retro

### Hypothesis

A live interruption with visible status proof should create an identity/permission gap before any money number appears. The same-interview face inset is a production workaround for this source shot, not a claim that picture-in-picture causes retention.

### Mechanical result

- moving approach footage starts at frame 0;
- a moving human face remains visible through the live-approach segment;
- caption appears at frame 0;
- mansion/status proof remains readable;
- first full-screen evidence begins at 19.029s.

### Main analytics risk

The face inset is intentionally large enough to satisfy the face-visible gate, but it competes with the mansion for visual attention. Review the 0–3s retention slope before reusing this exact composition.

## Experiment interpretation

V9 and V10 are different stories, protagonists, claims, and narrative arcs. They are comparisons, not a controlled hook experiment. A valid Live-Approach test must keep this same story/edit constant and change only the opening treatment.

## Upload state

Uploaded by the user as YouTube Short `U_3cCYOcCmk`:

- URL: https://youtube.com/shorts/U_3cCYOcCmk
- User reported the upload at: 2026-07-17 09:39:20 +07
- Public metadata timestamp: 2026-07-17 09:38:08 +07
- Public title: `They Collected $100M. His Check Was $10K.`
- Public channel: MONEY BLINDSPOT (`UCG_yrDQF5Sj6iMTZB0KSBAA`), matching the configured finance channel
- Public duration: 56s rounded
- Metrics: do not fetch before 2026-07-19 09:38:08 +07

### Early distribution observation

At `2026-07-17 10:51:13 +07`, approximately 1 hour 13 minutes after the public timestamp, `yt-dlp` still reported `view_count: 0`.

A follow-up check at `2026-07-17 11:17:37 +07`—1 hour 39 minutes 29 seconds after publication—still reported the video as public with `view_count: 0`.

This is evidence of zero observed exposure at that moment, not evidence that viewers rejected the two downstream TTS bridges. With no viewer exposure, no retention response to those lines could yet be measured.

User requested a tighter original-voice revision with both TTS bridges removed. It was produced as V9R:

- production doc: `docs/production/hardknocks-v9r-original-voice.md`;
- artifact: `output/projects/hardknocks/final/2026-07-17-hardknocks_v9r_original_voice.mp4`;
- status: production complete, not uploaded;
- causal boundary: the revision is a production hypothesis, not proof that commentary caused the initial zero-view state.

The agent did not perform the upload. No commit or push was performed.
