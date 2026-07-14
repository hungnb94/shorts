# Laundromat V1 — Decision-Lock Production Record

**Date:** 2026-07-14
**Status:** Uploaded; metrics pending
**Vertical:** Finance / English
**Format:** Decision-Lock Narrative (ADR-0028)

## Status

| Field | Value |
|---|---|
| YouTube Video ID | [ljRA4KX5uXQ](https://www.youtube.com/watch?v=ljRA4KX5uXQ) |
| Upload channel | MONEY BLINDSPOT (`UCG_yrDQF5Sj6iMTZB0KSBAA`) |
| Rendered | 2026-07-14 |
| Uploaded | 2026-07-14 18:15:31 +07 |
| Studio Analytics | [Open in YouTube Studio](https://studio.youtube.com/video/ljRA4KX5uXQ/analytics/tab-overview/period-default) |
| Metrics fetch after (48h rule) | 2026-07-16 18:15:31 +07 |
| Metrics status | Not yet fetched, too early |

## Final artifact

- Video: `output/projects/laundromat/final/2026-07-14-laundromat_v1_decision_lock.mp4`
- SHA-256: `4871c473b88e12bd18c6abcd0df71219e11a10100e8e45f862c205bdb843c0f1`
- Size: 49,597,515 bytes
- Renderer: `pipeline/laundromat/render_laundromat_v1.py`
- Tests: `pipeline/laundromat/test_render_laundromat_v1.py`
- Script/timeline: `output/projects/laundromat/scripts/script.md`
- Source manifest: `output/projects/laundromat/source/manifest.md`
- Metadata: `output/projects/laundromat/final/2026-07-14-laundromat_v1_decision_lock_metadata.txt`

The verified title and description were used for the public upload recorded above.

## YouTube metadata

**Title:** `She Sold Her House For This. Smart Or Reckless?`

The description distinguishes `$475K revenue`, `$119K business profit`, and `$66K owner pay`; qualifies `5–6 hours/week` as the current state after employees/systems; cites the CNBC Make It source URL; and contains no affiliate link.

## Direction selected

The Short asks the viewer to commit to `SMART` or `RECKLESS` before revealing the acquisition evidence:

1. sold home for `$310K`;
2. `$150K` home equity toward the laundromat;
3. `$100K` seller financing at `6%` over two years;
4. `$475K` 2024 revenue;
5. `$119K` business profit;
6. `$66K` owner pay;
7. `5–6 hours/week` now, explicitly not true five years earlier;
8. employees and systems explain the time outcome.

Final rule: check purchase price, owner pay, and owner hours—not headline revenue alone.

## Why this direction won

- It transfers the decision to the viewer instead of making the viewer watch a passive success story.
- The source provides a complete evidence ladder: capital, financing, revenue, profit, owner pay, and time.
- It creates a natural reversal: `$475K revenue` sounds decisive until `$119K business profit` and `$66K owner pay` appear.
- The reusable lesson is stronger than the case itself: revenue is not owner outcome.

Rejected directions:

- Garage-manufacturing story: visually stronger, but the `$1M` title claim was not substantiated cleanly enough in the transcript.
- Generic kindness/emotion story: proven emotional format, but outside the active finance value proposition.
- Straight laundromat revenue recap: lower participation and repeats the source's underperforming packaging.

## Source and transformation

Primary source: CNBC Make It, `Z1YZxX-fBwQ`.

Transformative Gate:

- source visual share: `44.4%` of 1,500 frames;
- every source visual clip: `<15s`;
- commentary: self-authored Decision-Lock framing, verdict, and decision checklist;
- value-adds: acquisition ledger, decision meter, revenue/profit waterfall, calculated-margin label, source citation, time qualification;
- three-source mix: CNBC footage + animated overlays + five evidence-linked Pexels clips;
- no TTS; only verbatim source audio plus music/SFX.

`$475K revenue`, `$119K business profit`, and `$66K owner pay` remain separate concepts. The displayed `CALCULATED: 25% MARGIN` is explicitly derived from `$119K / $475K`; it is not presented as a source quote.

## Hook corrections during QA

The first render failed because source windows at `18.08s` and `438.80s` introduced machine-only frames and source graphics. A later workaround used three portrait freeze frames to avoid the graphics and fake lip sync; user playback correctly identified that the first three seconds still looked like a photograph. The final hook replaces every freeze with moving footage: a small-business owner packing an order (`Pexels 7288127`) followed by a woman counting money (`Pexels 13736697`).

ADR-0017 skin-tone results on the final artifact:

- `t=0.0s`: `57.17%` — PASS
- `t=0.5s`: `57.44%` — PASS
- `t=2.0s`: `41.49%` — PASS

Motion QA sampled 28 frames at 10 fps over the first 2.8 seconds: all 27 transitions moved, median frame delta `3.386`, minimum `1.650`. Manual hook contact-sheet QA also passed after removing a redundant `HOUSE SALE $310K` overlay that competed with `SMART OR RECKLESS?`.

## Audio corrections during QA

ASR on an earlier render exposed three real defects:

- `$475K` was cut out of the revenue quote;
- `$66K` was guillotined after the word “six”;
- the systems quote ended mid-sentence.

All source boundaries were rebuilt from Whisper Medium word timestamps. Final ASR confirms:

- `$310K` home sale — PASS
- `$150K` equity — PASS
- `$100K` seller financing — PASS
- `$475K` revenue — PASS
- `$66K` owner pay — PASS
- `five or six hours` — PASS
- `five years ago` qualification — PASS
- `employees` and `systems` — PASS
- `small percentage ... putting back into the laundromat` at 20.88–25.00s — PASS
- `remove me ... focus on growing ... not working in the business` through 49.60s — PASS

User playback later found that second 23 and the full 44–50s outro had no dialogue. Raising music was an incorrect first fix because the requirement was spoken narrative, not merely a non-silent stream. The final timeline now inserts a complete reinvestment quote at 20.88–25.00s and extends the complete employees/systems quote through 49.60s. Music stays ducked under both quotes and rises only for the final 0.40s tail. Final dialogue-window measurements are `-16.9 dB` mean / `-1.1 dB` max at 20.88–25.00s and `-17.2 dB` mean / `-1.7 dB` max at 43.02–49.60s. Final silence scan reports no intervals ≥0.35s below `-38 dB`.

## Final technical QA

| Check | Result |
|---|---|
| Duration | `50.000s` |
| Resolution | `1080x1920` |
| Frame rate | `30/1` |
| Video codec | H.264 |
| Pixel format | `yuv420p` |
| Audio codec | AAC |
| Audio | 48 kHz stereo |
| Integrated loudness | `-14.1 LUFS` |
| True peak | `-0.6 dBFS` |
| Hook max volume | `-1.1 dB` |
| Required dialogue, 20.88–25.00s | `-16.9 dB` mean / `-1.1 dB` max |
| Required dialogue, 43.02–49.60s | `-17.2 dB` mean / `-1.7 dB` max |
| Hook motion | 27/27 sampled transitions moved; median `3.386` |
| Unique colors at 15s | `51,046` |
| Decode check | PASS |
| Unit tests | `10/10` PASS |
| `git diff --check` | PASS |
| Manual hook QA | PASS |
| Manual full-arc QA | PASS |
| ASR evidence gate | PASS |
| Silence gate | PASS |

## Inspection artifacts

- Hook contact sheet: `output/projects/laundromat/clips/v1_work/checks/hook-contact-dialogue-fix.jpg`
- Full contact sheet: `output/projects/laundromat/clips/v1_work/checks/contact-dialogue-fix.jpg`
- Final ASR: `output/projects/laundromat/clips/v1_work/checks/final-transcript-medium.json`
- Source word boundaries: `output/projects/laundromat/clips/v1_work/checks/source-word-boundaries.json`

## Upload state

Uploaded publicly to MONEY BLINDSPOT as `ljRA4KX5uXQ`. Upload identity is recorded in `docs/experiments/EXPERIMENT-LOG.md`; metrics must not be fetched before 2026-07-16 18:15:31 +07.