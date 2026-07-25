# Ronald Wayne Qwen TTS–Caption–Visual Sync Design

**Date:** 2026-07-25  
**Status:** User approved Approach 1 — remap 40 beats from final-MP4 word timestamps

## Problem

The Qwen narrator is fitted into the same large script slots as v1, but its word distribution and pauses differ from the former Edge TTS. The existing visual edit still changes every 1.5 seconds, while several captions and evidence cards assert a later phrase before Qwen speaks it.

The final v2 MP4 ASR word timestamps are the timing source of truth:

`output/projects/ronaldwayne/checks-v2-qwen/final-asr/final.json`

## Scope

Create a separate synchronized revision. Preserve:

- Qwen v2 audio exactly; do not regenerate or alter TTS;
- both verified Ronald Wayne source-voice quotes;
- 60.000-second duration;
- 1080×1920, 30fps;
- forty 1.5-second semantic visual beats;
- existing source provenance, claim qualifications, and visual asset pool.

Change:

- caption text per beat;
- visual/evidence assignment where the old image now precedes its spoken claim;
- exact caption reveal time within each 1.5-second beat.

## Timing model

1. Visual beats remain `[0.0, 1.5)`, `[1.5, 3.0)`, …, `[58.5, 60.0)`.
2. Each beat has a `caption_at` global timestamp derived from the first aligned ASR word that supports the caption.
3. A caption must not appear before `caption_at`.
4. Caption reveal is rounded to the nearest video frame at 30fps.
5. Before caption reveal, progress bar, source label, and moving watermark remain visible.
6. Main caption and subcaption reveal together.
7. If no new phrase is spoken in a beat, change the image/evidence state but retain the previous completed caption or show no new claim.
8. A supporting visual may establish context at beat start, but a money amount, liability conclusion, regret claim, or verdict label must not precede the matching spoken phrase.

## Renderer architecture

Create a v3-sync renderer rather than modifying v1/v2 in place.

For each beat, generate:

- a static chrome overlay: progress bar, source label, watermark;
- a caption-only transparent overlay;
- the selected visual/card background.

FFmpeg composites the static overlay for the full beat and enables the caption overlay only at `caption_at - beat_start`. The v3 renderer must use a separate work directory and must not reuse cached v1 beat files.

The final mux takes:

- video from the newly synchronized forty-beat render;
- audio stream from `2026-07-25-ronald-wayne-v2-qwen.mp4` via stream copy.

## Approved 40-beat semantic map

| Beat | Time | Caption | Spoken alignment / visual intent |
|---:|---:|---|---|
| 00 | 0.0–1.5 | THE INTERNET SAYS | “The internet says…” |
| 01 | 1.5–3.0 | 10% OF APPLE | “ten percent of Apple” |
| 02 | 3.0–4.5 | FOR $800 | “eight hundred dollars” |
| 03 | 4.5–6.0 | WAYNE CALLS THAT FALSE | “Wayne calls that false” |
| 04 | 6.0–7.5 | WHAT ACTUALLY HAPPENED? | exact question |
| 05 | 7.5–9.0 | WAYNE DRAFTED IT | “Wayne drafted…” |
| 06 | 9.0–10.5 | PARTNERSHIP AGREEMENT | “partnership agreement” |
| 07 | 10.5–12.0 | NAME REMOVED / 12 DAYS LATER | corresponding phrase |
| 08 | 12.0–13.5 | JOBS SENT $800 | corresponding phrase |
| 09 | 13.5–15.0 | APPLE WAS… | sentence setup; do not show conclusion early |
| 10 | 15.0–16.5 | NOT A CORPORATION | corresponding phrase |
| 11 | 16.5–18.0 | PERSONAL LIABILITY | “personally liable” |
| 12 | 18.0–19.5 | JOBS + WOZ | sentence subject / risk setup |
| 13 | 19.5–21.0 | YOUNG AND BROKE | corresponding phrase; no house card |
| 14 | 21.0–22.5 | WAYNE WAS 41 | corresponding phrase |
| 15 | 22.5–24.0 | HOUSE • CAR • MONEY | corresponding asset list |
| 16 | 24.0–25.5 | CREDITORS COULD REACH | corresponding risk phrase |
| 17 | 25.5–27.0 | THE TWIST? | exact phrase |
| 18 | 27.0–28.5 | WAYNE BELIEVED IN APPLE | corresponding phrase |
| 19 | 28.5–30.0 | IT WAS THE… | Wayne source quote setup |
| 20 | 30.0–31.5 | RIGHT PRODUCT • RIGHT TIME | Wayne source quote payoff |
| 21 | 31.5–33.0 | HE EXPECTED… | sentence setup |
| 22 | 33.0–34.5 | DECADES OF PAPERWORK | corresponding phrase |
| 23 | 34.5–36.0 | INSTEAD OF BUILDING | corresponding phrase |
| 24 | 36.0–37.5 | HIS OWN INVENTIONS | corresponding phrase |
| 25 | 37.5–39.0 | HIS OWN INVENTIONS | hold completed phrase over a new visual; no new early claim |
| 26 | 39.0–40.5 | LOCK YOUR VERDICT | corresponding phrase |
| 27 | 40.5–42.0 | SELL OR STAY? | corresponding phrase |
| 28 | 42.0–43.5 | LIKE • SUBSCRIBE • COMMENT | corresponding CTA words |
| 29 | 43.5–45.0 | WAYNE SAYS… | sentence setup |
| 30 | 45.0–46.5 | NO REGRET LEAVING APPLE | corresponding phrase |
| 31 | 46.5–48.0 | WHAT DID HE REGRET? | exact question |
| 32 | 48.0–49.5 | ORIGINAL CONTRACT | corresponding phrase |
| 33 | 49.5–51.0 | SOLD FOR $500 | corresponding phrase |
| 34 | 51.0–52.5 | IN 2011… | sentence setup |
| 35 | 52.5–54.0 | SOLD FOR $1.59 MILLION | corresponding phrase |
| 36 | 54.0–55.5 | THAT, I REGRET | verified Wayne quote |
| 37 | 55.5–57.0 | SO WAS HE… | verdict setup |
| 38 | 57.0–58.5 | HISTORY'S BIGGEST FOOL? | corresponding phrase |
| 39 | 58.5–60.0 | WALKING AWAY = FREEDOM? | corresponding phrase |

## Visual remaps that are mandatory

- Beat 13: use a Jobs/Woz “young and broke” comparison, not Wayne’s house.
- Beat 14: use Wayne imagery with `WAYNE WAS 41`.
- Beat 15: show the grouped assets card.
- Beat 16: show creditor/liability exposure.
- Beats 21–25: sequence paperwork → building → inventions; beat 25 is a visual hold/transition, not a new spoken claim.
- Beats 29–35: sequence Wayne says → no regret → question → original contract → $500 → 2011 → $1.59M.
- Beats 37–39: setup → fool → freedom; the “fool” visual must not appear while only “So was he…” is spoken.

## Automated acceptance tests

Before implementation, add tests for:

1. Exactly 40 beats of exactly 1.5 seconds.
2. Every beat has an in-range `caption_at`.
3. `caption_at` is never earlier than its required ASR anchor.
4. The money/liability/regret/verdict captions map to their expected normalized ASR phrases.
5. Beat 25 introduces no new caption claim during silence.
6. Final v3 audio elementary-stream hash equals v2 Qwen audio hash.
7. Final ASR recovers 151/151 normalized tokens.
8. Final full decode passes; duration is 60.000 seconds; video is 1080×1920 at 30fps; keyframe count is 40.

## Manual acceptance review

Generate:

- a 40-beat contact sheet;
- focused contact sheets for 12–25.5s, 31.5–43.5s, and 43.5–60s;
- a timing audit table showing each caption, reveal time, matching word start, and lead/lag.

Review must confirm no caption or evidence amount appears before its spoken claim and no visual claim contradicts the words currently being heard.

## Output

`output/projects/ronaldwayne/2026-07-25-ronald-wayne-v3-qwen-synced.mp4`

v1 and v2 remain unchanged as controls.
