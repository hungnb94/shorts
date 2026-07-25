# Plan — HardKnocks V8: Logan Paul Delayed Platform Fit

**Date:** 2026-07-16
**Status:** Complete; rendered and QC-passed on 2026-07-16.

## Goal

Create one English finance/creator-economy Clip Curation Edit from `ALvduf2Rz_c` that adapts the authority-led rejection → hidden mechanism → economic proof structure used by HardKnocks V7 (`3mfOtQLLt1Y`) without treating V7 as a confirmed winner before its 48-hour metrics window.

The selected narrative is a **Delayed Platform-Fit Narrative**:

`called weird → practiced for 9–10 years / 10,000 hours → Vine fit six-second storytelling → $30M personal-year proof → Prime $1.2B company proof → partners understood influencer distribution`

## Source

- Channel: School of Hard Knocks
- Video: `Asking One of the Richest Men on the Internet How He Got Rich!`
- Video ID: `ALvduf2Rz_c`
- URL: https://www.youtube.com/watch?v=ALvduf2Rz_c
- Public duration: 956s
- Public source resolution: 3840×2160
- Public snapshot: 155,232 views and 5,827 likes on 2026-07-16
- Candidate interview region: approximately 12:36–13:46 from the public transcript

A 1920×1080 research section covering 12:30–13:50 was downloaded and visually inspected. It is a stable landscape two-shot: Logan remains on the left and the host remains on the right. The source itself does not switch camera angles during the selected exchange, so portrait turn-taking must be created through digital Active-Speaker Reframing.

## Decisions Locked During Grilling

1. Editorial thesis: 10,000 hours before platform fit.
2. Hook order: Logan's `you guys are weird` rejection → host asks how long success took → Logan reveals 9–10 years / 10,000 hours.
3. Proof-Coupled B-Roll budget: 25–35% of final timeline.
4. B-roll sources: authentic Logan/Vine/Prime footage first; stock only for abstract ideas or missing evidence.
5. Provisional payoff: `$30M personal` → `Prime $1.2B` → `great partners`.
6. Provisional host presence: retain three compressed questions—overnight success, best personal year, and company result.
7. Framing policy: Active-Speaker Reframing plus Semantic Zoom per proposed ADR-0030.

Items 5–7 use the recommended defaults because their interactive questions timed out. The user's subsequent instruction to continue creating the video confirmed those defaults and moved ADR-0030 to Accepted.

## Candidate Storyboard

All source times below are transcript-level candidates, not frame-locked edit boundaries. Production must re-transcribe the maximum-quality source with MLX Whisper word timestamps before any final cut.

| Final beat | Approx. source | Speaker | Narrative role | Portrait framing | Proof / value-add |
|---|---:|---|---|---|---|
| `YOU GUYS ARE WEIRD` | 12:56–12:58 | Logan | Rejection cold open | guest medium → semantic close on `weird` | moving archival early-content insert, corner only |
| `OVERNIGHT?` | 12:36–12:41 | Host | Open the duration gap | hard switch to host medium | progressive hook caption; no full-screen b-roll |
| `I STARTED AT 9` | 12:41–12:49 | Logan | Origin | hard switch to guest medium | early YouTube evidence, partial/corner within 0–10s |
| `9–10 YEARS / 10,000 HOURS` | 12:58–13:07 | Logan | Hidden mechanism | guest medium → close on `10,000 hours` | timeline/data visualization; short creator-work stock only if no authentic footage fits |
| `VINE FIT SIX SECONDS` | 13:10–13:18 | Logan | Platform-fit trigger | reset guest medium to preserve gestures | authentic Vine/short-form footage; full-screen allowed after t=10s |
| `MOST IN ONE YEAR?` | 13:21–13:29 | Host | Economic proof setup | hard switch to host medium | number ladder begins |
| `ABOUT $30M` | 13:29–13:31 | Logan | Personal payoff | guest close | `$30M` data card; no decorative cash stock |
| `WHAT ABOUT THE COMPANIES?` | 13:31–13:34 | Host | Escalation setup | host medium | reset scale |
| `PRIME MADE $1.2B` | 13:34–13:38 | Logan | Company payoff | guest close on `$1.2B` | authentic Prime product/distribution footage |
| `GREAT PARTNERS` | 13:38–13:46 | Host → Logan | Closing reframe | host medium → guest medium; optional close on final `brand` | partner/distribution framework and source citation |

Target final duration: 50–57 seconds after bounded speed-up. Every retained source excerpt must remain under 15 seconds, even when adjacent excerpts preserve one continuous Logan answer.

## Active-Speaker Reframing

The output uses hard editorial reframes, not continuous face tracking:

- Logan crop target: calibrated from the left side of the 4K two-shot.
- Host crop target: calibrated from the right side of the 4K two-shot.
- Switch crop on retained speaker-turn boundaries, not several frames late.
- Preserve eye-line and enough shoulder/gesture context; do not force the face to dead center if that removes the microphone or meaningful hand motion.
- Two-shot is allowed only for interaction/reaction context, not as the default answer framing.
- Hard-crop full bleed remains mandatory; no blur fill or pillarbox.

## Semantic Zoom

Use two intentional scale states, calibrated on real frames:

- **Medium:** question setup, topic reset, longer explanation, or gesture-dependent beat.
- **Close:** strongest number, confession/rejection, command, or punchline.

Rules:

- maximum one punch-in per answer by default;
- reset to medium at the next host question/topic;
- no constant push-in and no zoom every 1–2 seconds;
- caption changes, speaker cuts, b-roll, and motion already satisfy cadence—do not stack a zoom merely to satisfy a timer;
- every crop/scale state must be manually frame-checked for clipped hair, chin, hands, microphone, and captions.

## Proof-Coupled B-Roll Plan

Target 25–35% of the final timeline, approximately 13–19 seconds for a 52–55 second Short.

Priority assets:

1. moving Logan/Jake early-video evidence;
2. Vine-era short-form footage or interface evidence;
3. authentic Prime product/distribution footage;
4. generic creator-work stock only where an abstract accumulation-of-practice beat cannot be shown authentically.

Guardrails:

- 0–10s: only partial/corner inserts; active speaker face remains visible continuously;
- after 10s: full-screen proof allowed for short windows;
- every insert must align with the spoken claim in the same beat;
- reject static photos, decorative luxury stock, unrelated money footage, competing brands, watermarks, and unverifiable archive clips;
- source/copyright provenance must be logged before render.

## Caption and Claim Policy

- English only.
- Burned caption visible by t=0.2s.
- Hook bursts: 1–3 words; body bursts: 2–5 words.
- One emphasized keyword/number per burst.
- Verbatim captions come from raw MLX word-token concatenation.
- Editorial labels must look different from verbatim speech.
- `$30M` is Logan's personal estimate in the interview.
- `Prime made $1.2B in its second year` is Logan's source-reported company claim and must be labeled/cited as such unless independently verified.
- Do not imply that 10,000 hours alone caused Prime's result; the final partner/distribution beat prevents a single-cause claim.

## Transformative Gate

- Commentary: progressive editorial framing, evidence ladder, and transferable platform-fit reframe.
- Value-add 1: 9–10 years / 10,000-hours timeline.
- Value-add 2: Vine platform-fit explanation.
- Value-add 3: `$30M → $1.2B` source-reported number ladder.
- Value-add 4: partner + influencer-distribution framework.
- Multi-source mashup: authentic archive/Prime proof plus limited stock where necessary.
- Every source excerpt <15s; total source usage far below 50% of the 956-second source.

## Production Gates

1. Download maximum-quality 2160p source and register it in `data/source_videos.csv`.
2. Generate MLX Whisper word timestamps and lock frame-accurate windows.
3. Extract hook and all candidate frames; verify moving face/action and crop feasibility.
4. Source and QC every external proof asset before rendering.
5. Build tests for duration, clip limits, source ratio, 0–10s face protection, b-roll budget, and speaker-turn crop mapping.
6. Render base interview with Active-Speaker Reframing and Semantic Zoom.
7. Composite Proof-Coupled B-Roll and value-adds.
8. Verify 1080×1920, H.264/yuv420p, AAC, 30fps, 45–60s, decode, loudness, black/freeze/silence events, caption timing, final spoken payoff, and manual contact sheets.
9. Create the production doc with one canonical title, description, exactly three hashtags, separate YouTube Studio tags, claim provenance, QC results, Hook Retro, and Workflow Delta.
10. Do not upload, commit, or push unless separately requested.

## Approval

The user confirmed shared understanding and authorized production on 2026-07-16 with the instruction `tiếp tục tạo video`.

## Completion

- Final: `output/projects/hardknocks/final/2026-07-16-hardknocks_v8_logan_platform_fit.mp4`
- Production record: `docs/production/hardknocks-v8-logan-platform-fit.md`
- Final duration: 54.486s
- Primary-source usage: 5.79%
- Evidence/illustration coverage: 25.99%
- First full-screen evidence: 10.097s
- Hook caption: 0.097s
- Decode, spec, black/freeze/silence, ASR-tail, contact-sheet, and active-speaker checks: passed
- Upload: user-reported as YouTube Short `-xSqHo7XjB8`, scheduled public around 2026-07-16 19:00 +07; public metadata verification pending
- Commit and push: not performed
