# Laundromat V1 — Decision-Lock Production Record

**Date:** 2026-07-14  
**Status:** Rendered and verified; not uploaded  
**Vertical:** Finance / English  
**Format:** Decision-Lock Narrative (ADR-0028)

## Final artifact

- Video: `output/projects/laundromat/final/2026-07-14-laundromat_v1_decision_lock.mp4`
- SHA-256: `e4d54262229f6d8b3d59195826b61ba2dcd44f8f0082667eb6262042943699c2`
- Size: 47,591,409 bytes
- Renderer: `pipeline/laundromat/render_laundromat_v1.py`
- Tests: `pipeline/laundromat/test_render_laundromat_v1.py`
- Script/timeline: `output/projects/laundromat/scripts/script.md`
- Source manifest: `output/projects/laundromat/source/manifest.md`

No title/description/upload metadata was generated. Upload remains a separate user-controlled action.

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

- source visual share: exactly `50.0%` of 1,500 frames;
- every source visual clip: `<15s`;
- commentary: self-authored Decision-Lock framing, verdict, and decision checklist;
- value-adds: acquisition ledger, decision meter, revenue/profit waterfall, calculated-margin label, source citation, time qualification;
- three-source mix: CNBC footage + animated overlays + Pexels house/contract/finance B-roll;
- no TTS; only verbatim source audio plus music/SFX.

`$475K revenue`, `$119K business profit`, and `$66K owner pay` remain separate concepts. The displayed `CALCULATED: 25% MARGIN` is explicitly derived from `$119K / $475K`; it is not presented as a source quote.

## Hook corrections during QA

The first render failed because source windows at `18.08s` and `438.80s` introduced machine-only frames and source graphics. The final hook uses three animated portrait freezes from `236.08`, `240.00`, and `244.00`, followed by action B-roll. This avoids both static source infographics and fake lip sync.

ADR-0017 skin-tone results on the final artifact:

- `t=0.0s`: `16.04%` — PASS
- `t=0.5s`: `16.25%` — PASS
- `t=2.0s`: `25.54%` — PASS

Manual hook contact-sheet QA also passed after removing a redundant `HOUSE SALE $310K` overlay that competed with `SMART OR RECKLESS?`.

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

The visual-only profit checkpoint originally produced 3.95s below `-38 dB`. Its music level was raised; final silence scan reports no intervals ≥0.35s below `-38 dB`.

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
| Unique colors at 15s | `51,046` |
| Decode check | PASS |
| Unit tests | `9/9` PASS |
| `git diff --check` | PASS |
| Manual hook QA | PASS |
| Manual full-arc QA | PASS |
| ASR evidence gate | PASS |
| Silence gate | PASS |

## Inspection artifacts

- Hook contact sheet: `output/projects/laundromat/clips/v1_work/checks/hook-contact-delivery.jpg`
- Full contact sheet: `output/projects/laundromat/clips/v1_work/checks/contact-delivery.jpg`
- Final ASR: `output/projects/laundromat/clips/v1_work/checks/final-transcript-medium.json`
- Source word boundaries: `output/projects/laundromat/clips/v1_work/checks/source-word-boundaries.json`

## Upload state

Not uploaded. No platform state, experiment log row, or metrics record has been created.