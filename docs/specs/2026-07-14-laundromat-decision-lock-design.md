# Laundromat Decision-Lock Short

**Date:** 2026-07-14
**Status:** Self-approved for implementation under the user's autonomous-production authorization
**Target:** Finance / English; render a production-ready Short, do not upload automatically

## Problem

The current Shorts are technically compliant but still look like edited explanations:

- `hardknocks_v5`: one two-person interview composition dominates both the hook and the full arc.
- `aiwork_v6`: one presenter plus an illegible terminal background repeats through most of the arc.
- `trademe_v1`: real proof exists, but full-screen navy cards repeatedly interrupt the human story.

The common gap is viewer agency. The viewer receives a claim and waits for an explanation; they are not required to predict, decide, or test themselves. More captions and more overlays would increase density without changing that relationship.

## Research and alternatives

### A. More Proof-First footage

Use another real money transformation and reduce explanatory cards. This is visually safer and reuses ADR-0027, but the viewer remains a spectator. Rejected as too incremental for the requested new value frame.

### B. Hidden-mistake visual puzzle

Show a business setup and ask the viewer to spot the missing cost. This creates interaction but would rely heavily on animation or screen graphics, repeating visual types the user has already rejected as cheap. Rejected for visual-risk reasons.

### C. Decision-Lock Narrative — selected

Put the viewer in the buyer's seat, force a binary judgment before the evidence, then reveal the economics in stages. The viewer stays for self-verification, while the final lesson transfers as a concrete decision checklist.

The selected source is CNBC Make It's `Z1YZxX-fBwQ`. Verified source facts:

- Sold home for $310K and retained $150K equity.
- Added $50K savings and seller-financed the remaining $100K at 6% over two years, implying a $300K purchase price.
- 2024 revenue: about $475K.
- 2024 profit: about $119K, stated in the official description.
- 2024 owner pay: $66K.
- Current owner time: about five to six hours per week, explicitly qualified as the result of years of work, employees, and systems.

A 9.4M-view garage-production candidate (`PUfjMOK2WXE`) was also researched. It is more visually dynamic, but its “$1M/year” claim exists primarily in the title while the transcript directly proves only a $600 setup, 10K bridge units, and later contract manufacturing. It was rejected for this experiment because the core hook would require more claim qualification than the laundromat case.

## Creative contract

### Title

`She Sold Her House For This. Smart Or Reckless?`

### Hook

`SHE SOLD HER HOUSE` → `TO BUY THIS.` → `SMART OR RECKLESS?`

The owner must be visible at frame 0, with the first caption visible by t=0.2s. A two-choice decision meter appears by t=1.5s, and `LOCK YOUR ANSWER` lands by t=2.8s. The choice is not resolved until the final section.

### Value promise

The viewer practices evaluating a real business acquisition rather than hearing another entrepreneur success story. The transferable rule is:

`CHECK PRICE. OWNER PAY. OWNER HOURS.`

`NEVER JUDGE A BUSINESS BY REVENUE ALONE.`

## Timeline

| Time | Narrative beat | Audio/evidence | Visual direction |
|---:|---|---|---|
| 0.0–2.8s | Decision hook | Cami's exact “I sold my home” statement | Tight owner/face shot plus laundromat motion; three rapid caption bursts; `SMART`/`RECKLESS` meter appears without covering the face |
| 2.8–7.5s | Lock the bet | $150K home equity + $50K savings | Moving laundromat footage stays visible; animated cash chips combine into `$200K CASH AT RISK` |
| 7.5–11.5s | Complete the price | $100K seller financing at 6% | Partial split-screen ledger; total resolves to `$300K PURCHASE PRICE`; decision meter stays unresolved |
| 11.5–17.0s | Seductive headline | Cami's exact `$475K in 2024` statement | Real machines/customers plus large `$475K REVENUE`; meter swings toward `SMART` |
| 17.0–23.0s | First reversal | Official CNBC figure: about $119K profit | Cash-flow waterfall removes expenses; `$119K PROFIT / 25% MARGIN`; meter returns toward center |
| 23.0–29.5s | Owner reality | Cami's exact `$66K paid myself` statement | Owner remains visible in a corner/side panel; waterfall narrows to `$66K OWNER PAY` |
| 29.5–38.5s | Time payoff with qualification | Exact `5–6 hours/week` and “not how it was five years ago” statements | Clock compresses to `5–6 HRS/WEEK NOW`; then `AFTER ~5 YEARS + 6 EMPLOYEES`; no passive-income overclaim |
| 38.5–46.0s | Verdict and teaching | Self-authored editorial captions; source music/room tone only | Verdict: `SMART — BUT NOT BECAUSE OF REVENUE`; three-item checklist animates over moving footage |
| 46.0–50.0s | Semantic loop | No CTA | `WOULD YOU SELL YOUR HOUSE?` returns with the same decision meter, then hard-cuts into frame 0 |

Target duration is 48–52 seconds. The renderer may tighten pauses but must not extend beyond 60 seconds.

## Visual system

- Moving human or machine footage remains visible throughout the first ten seconds.
- No full-screen static card may persist longer than 0.8 seconds anywhere.
- Original CNBC footage targets 45–48% of final frames.
- Pexels footage supplies laundromat machinery, keys/home-sale symbolism, and cash-handling detail where source footage is not shown.
- Animated value-adds are composited over moving footage: decision meter, acquisition ledger, cash-flow waterfall, and final checklist.
- In the first ten seconds, Pexels/value-add footage may only be partial or split-screen so the owner/decision subject remains visible.
- Hook cadence: visual or caption state change every 0.6–1.3 seconds through t=5s.
- Caption palette: white base; yellow for purchase/revenue figures; red-orange for risk/expense; green for owner-pay/time payoff.
- All copy is measured with Pillow before render and verified on extracted real frames afterward.

## Audio system

- No TTS.
- Use short verbatim source-audio statements for the bet, revenue, owner pay, and current owner-hours.
- Editorial commentary is carried by self-authored on-screen text, which satisfies ADR-0007's commentary requirement.
- Preserve natural speech speed; pause trimming is allowed only at real silence boundaries.
- Normalize the final mix near -14 LUFS with no clipping and confirm every selected source-audio window is audible.
- Use a subtle licensed/local instrumental bed only if one already exists in the repository and does not obscure the source voice; otherwise retain source room tone/music and use clean hard cuts.

## Transformative Gate

1. Commentary: pass through persistent editorial decision framing and the final three-number rule.
2. Value-adds: animated decision meter; source-cited acquisition/cash-flow ledger; cash-flow waterfall; final checklist.
3. Source use: each visual source clip under 15 seconds; aggregate CNBC footage at or below 50% of final frames.
4. Three-source visual mix: original source footage + animated overlays + Pexels b-roll.
5. Source citation: visible `SOURCE: CNBC MAKE IT • 2024 FIGURES` on the financial checkpoint and a specific source link in metadata/production documentation.

## Failure handling

- If the planned frame-0 timestamp does not show Cami's face/action, select another source timestamp before rendering; do not solve it with a title card.
- If a financial claim is not present in direct audio, label it as an official CNBC-reported figure rather than writing it as Cami's spoken quote.
- If the source crop removes essential visual context, use a tracked side crop or split-screen rather than pillarbox.
- If the source footage share exceeds 50%, replace visuals with Pexels or animated overlays while preserving the verbatim audio.
- If the choice UI covers the face or source captions, reposition or shorten copy; do not shrink the hook below the project floor.

## Verification

- Python syntax and renderer dry-run checks.
- Full render and decode.
- ffprobe: 1080x1920, H.264 High, yuv420p, AAC, 30fps, 30–60 seconds.
- Frame-accurate source-share report and per-clip duration report.
- Hook contact sheet at 0.0, 0.2, 0.6, 1.0, 1.5, 2.0, 2.8, 4.0, and 5.0 seconds.
- Arc contact sheet every four seconds.
- Manual visual check for face visibility, caption timing, clipping, static-card duration, decision-meter continuity, and actual laundromat proof.
- Loudness, true-peak, selected-window audibility, and final transcription checks.
- Production doc, metadata file, source registry entry, and Post-Production Retro.

## Success and falsification

Primary creative target: beat the current finance baseline of 54.1% Stayed to Watch without sacrificing completion through the final verdict. This is a stretch hypothesis, not a guarantee.

Decision-Lock Narrative is weakened if either occurs after the normal analytics wait:

- retention falls before the first financial checkpoint, meaning the choice was not compelling enough to hold the viewer; or
- retention falls at each number reveal, meaning the ledger reads as explanation rather than escalating evidence.

A successful curve should hold through the locked choice, show renewed attention at the `$119K` reversal, and preserve enough viewers to reach the owner-hours verdict.
