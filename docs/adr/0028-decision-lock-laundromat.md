# ADR 0028: Decision-Lock Finance Narrative — Sell the House or Walk Away

**Date:** 2026-07-14
**Status:** Accepted

## Context

The latest visual audit found a shared weakness across the current Shorts: they ask the viewer to receive information but rarely require the viewer to do anything with it. `hardknocks_v5` and `aiwork_v6` remain visually dominated by one interview composition, while `trademe_v1` adds proof but repeatedly replaces moving evidence with full-screen explanatory cards. The videos can satisfy the existing technical gates while still feeling observational rather than participatory.

Three directions were considered:

1. Continue Proof-First Narrative with denser real-event footage. This improves visual evidence but keeps the viewer passive.
2. Build a visual puzzle around a hidden financial mistake. This creates participation but depends heavily on animation and risks repeating the cheap-looking visual types already rejected.
3. Ask the viewer to lock a consequential decision before the financial evidence is revealed. This combines a real human bet, progressive proof, and a reusable decision rule.

The third direction is selected.

## Decision

The next finance Short will introduce a **Decision-Lock Narrative** using CNBC Make It's 2025 laundromat case. The viewer must judge whether selling a home to buy the laundromat was smart or reckless before seeing the full economics.

- Opening claim: **“She sold her house to buy this. Smart or reckless?”**
- Persistent choice: `SMART` versus `RECKLESS`; the viewer is prompted to lock an answer inside the first three seconds.
- Evidence checkpoints: $200K cash at risk plus $100K seller financing; $475K 2024 revenue; about $119K profit; $66K paid to the owner; five to six owner-hours per week only after roughly five years, six employees, and operating systems.
- Final decision rule: **check purchase price, owner pay, and owner hours — never judge a business by revenue alone.**
- Ending: no follow/subscribe CTA. Return to the opening choice so the viewer can compare the initial judgment with the evidence-backed one.

The source is `Z1YZxX-fBwQ`, “I Quit My Nursing Job For My Laundromat Business – It Brings In $475K/Year.” Its long-form upload has over 1.3M views and supplies direct footage and first-person statements. CNBC's two existing Shorts on the same case have much lower distribution and run longer than this project's 60-second ceiling; their packaging is not treated as the proven format. This experiment uses the source facts and footage but replaces the success-profile packaging with a binary decision trial.

## Consequences

- The decision UI is a whole-video retention structure, not merely a `this_or_that_overlay` added to an otherwise unchanged interview edit.
- Moving footage remains visible behind or beside overlays; no static explanatory card may occupy the full frame for more than 0.8 seconds.
- Original voice is preferred over TTS. Self-authored editorial captions provide the commentary track, while selected first-person source statements preserve authenticity.
- The Transformative Gate still applies: every source clip under 15 seconds, aggregate source footage at or below 50%, and at least two value-adds. This video uses a source-citation/fact ledger, an animated decision meter, and a progressive cash-flow waterfall.
- This is a single experimental format hypothesis, not proof that Decision-Lock Narrative will outperform. It is falsified if the opening choice does not improve Stayed to Watch over the finance baseline or if retention drops at evidence checkpoints instead of holding through the verdict.
