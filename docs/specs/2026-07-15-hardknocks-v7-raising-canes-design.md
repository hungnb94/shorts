# HardKnocks V7 — Raising Cane's Focus Bet Design

## Status

Approved by delegated choice after the user asked the producer to select the source and the approval prompt timed out with an instruction to proceed using best judgment.

Publishing-metadata extension approved by the user on 2026-07-15: keep one canonical upload package in the production doc and enforce it through Workflow Stages 5 and 6.

## Goal

Produce one English YouTube Short that adapts WEALTHIAN's `Authority-Led Hidden Economics Reveal` semantic engine to a new School of Hard Knocks source while satisfying this project's Hook Gate, Transformative Gate, 3-source visual rule, and fixed output specifications.

The Short is a business case study, not a generic founder-motivation montage:

> A college professor called the one-product restaurant concept unworkable. Todd Graves kept the focus bet, funded one damaged location, and scaled Raising Cane's.

## Selected source

- Channel: School of Hard Knocks
- Video ID: `n5EmUiLNVjg`
- Public title at selection: `How I Turned $50,000 Into $20 Billion`
- Source URL: https://www.youtube.com/watch?v=n5EmUiLNVjg
- Source duration reported by player metadata: 990s
- Player metadata at selection: 500,189 views; uploaded 2025-07-27
- Maximum listed source resolution: 2160p
- Registry check: not present in `data/source_videos.csv` before selection

## Why this source won

### Candidate A — Raising Cane's, selected

- Familiar brand and physical product.
- Founder is the operational authority.
- Counterintuitive mechanism: competitors added variety; the concept bet on chicken fingers only.
- Concrete proof chain: lowest class grade, bank rejection, $50K personal equity, $50K SBA loan, damaged first location, scale and wealth numbers.
- Clear changed decision: focus can be an operating system, not merely fewer options.
- Lower regulatory and factual-harm risk than tax or oil-investment advice.

### Candidate B — $7.1M income / $0 federal tax, rejected

Stronger surface hook but high tax-advice, jurisdiction, qualification, and fact-check burden. The sampled transcript also contains broad claims that cannot responsibly fit into a 60-second Short without losing material caveats.

### Candidate C — oil rig economics, rejected

Excellent real-world machinery footage and a `$14,500/day` proof object, but the transcript includes investment-return and tax claims requiring more context. It is also less universally familiar than a fast-food ritual.

## Narrative design

### Semantic formula

`familiar product` → `loaded rejection` → `founder authority` → `hidden focus bet` → `funding proof` → `scale proof` → `rebuild rule`

### Narrative beats

- **Hook:** The professor gave the plan the worst grade because the concept would never work.
- **Mechanism reveal:** The alleged flaw was selling only chicken fingers while competitors added variety and healthier options.
- **Proof:** Graves raised $50K, matched it with a $50K SBA loan, and rebuilt an old restaurant space.
- **Payoff:** If forced to rebuild, he would again choose a cravable product, focus on it, build a team around it, then scale.

### Curiosity-gap policy

The frame-0 hook must not name Raising Cane's, the $20B outcome, and the one-product mechanism simultaneously.

Primary hook overlay:

`THE WORST GRADE`

The source voice supplies `the concept will never work`. The chicken-finger mechanism is revealed after the initial rejection is established.

## Source-audio plan

Exact boundaries must be re-anchored with `mlx_whisper` word timestamps after the full-quality source is downloaded. JSON3 timestamps below are candidate windows, not final edit boundaries.

| Beat | Candidate source window | Maximum target | Intended content |
|---|---:|---:|---|
| Rejection + focus reveal | 188.0–200.72s | <13s | Professor gave the worst grade; one chicken-finger product versus menu variety |
| Funding proof | 299.20–313.84s | <15s | $50K personal equity + $50K SBA loan + old restaurant space |
| Scale proof | 354.80–366.00s | <12s | $400M best year and source-reported net worth north of $20B |
| Rebuild rule | 761.84–774.16s | <13s | Cravable product → focus → team → scale |

Every final source excerpt must remain under 15 seconds. Total selected source must remain below 50% of the 990-second original.

Target final duration: 48–56 seconds after pause trimming and a source-derived mild speed-up.

## Visual design

### 0–10-second hook window

- Frame 0: real moving Todd Graves footage, not a title card, freeze frame, or Ken Burns portrait.
- Self-authored hook visible by final t=0.1–0.2s.
- Yellow, all-caps, black-outline captions in 1–3-word bursts.
- Caption changes approximately every 0.8–1.4s, aligned to actual speech.
- The speaker remains visible throughout the first 10 seconds.
- Evidence may enter as a split-screen or corner proof panel; no full-screen face replacement before t=10s.
- At least one real visual change every 1–2 seconds using genuine source motion, crop punches, caption changes, or a proof panel.

### Body

Use the required three-source combination:

1. Original School of Hard Knocks footage and audio.
2. Animated analysis overlays/data visualization.
3. Brand-neutral Pexels restaurant-kitchen footage.

Pexels footage may become full-screen only after t=10s while original speech remains audible. It must depict directly relevant actions such as a focused kitchen line, frying/serving food, or rebuilding a small restaurant. Every used window requires frame and OCR review for conflicting consumer brands.

### Analysis overlays

At least two non-caption value-adds:

1. **This-or-that comparison:** `VARIETY` versus `ONE CORE PRODUCT`.
2. **Capital ladder:** `$50K CASH + $50K SBA → FIRST STORE`.
3. **Scale ladder:** `1 STORE → 900+ SOURCE-REPORTED` with `1996` context.
4. **Editorial mechanism:** `CRAVABLE PRODUCT → FOCUS → TEAM → SCALE`.
5. **Source citation:** compact `Source: School of Hard Knocks / Todd Graves` label.

Numbers that are not independently verified must be visibly framed as source-reported rather than current audited facts.

## Audio design

- Preserve Todd Graves and the interviewer as the only spoken voices.
- No neural TTS and no generic CTA.
- Use a quiet music bed and sparse impact accents at the focus reveal and capital/scale transitions.
- Derive pause-removal threshold from the selected source's real inter-word gap distribution; do not copy a fixed threshold from prior projects.
- Derive a mild speed-up from intelligibility checks and keep it within the established retention-technique guardrail.
- Duck music under all required dialogue windows.
- End on Todd's natural `focus → team → scale` payoff, not on an artificial conclusion.

## Caption policy

- Verbatim dialogue captions must be generated from word timestamps.
- Reconstruct text by concatenating raw Whisper word tokens, then strip once; never join stripped tokens with spaces.
- One speaker per caption burst.
- Target 1–3 words in the hook and 2–5 words in the body.
- English only.
- Caption width must be measured with Pillow against the real font/canvas before render and inspected on extracted final frames.
- Editorial overlays must be visually distinguishable from verbatim captions.

## Transformative Gate

The final edit must include:

1. Editorial commentary through self-authored mechanism overlays and narrative reordering.
2. At least two non-caption value-adds from comparison, capital ladder, scale ladder, source citation, and animated mechanism annotation.
3. Multi-clip construction with each source excerpt under 15 seconds.
4. Total selected source below 50% of the original duration.
5. Original/source-specific evidence, Pexels evidence, sound design, pause trimming, crop punches, and captions.

## Output contract

- Path: `output/projects/hardknocks/final/2026-07-15-hardknocks_v7_raising_canes_focus_bet.mp4`
- 1080×1920, 9:16
- H.264/yuv420p
- AAC audio, 48kHz stereo
- 30fps
- 45–60 seconds; hard maximum 60 seconds
- Date-prefixed final filename

## Publishing metadata contract

`docs/production/hardknocks-v7-raising-canes-focus-bet.md` is the single source of truth for the upload package. It must contain all four fields before the production status can be `Completed`:

1. One canonical YouTube title; no unresolved alternatives.
2. A concise YouTube description that states the case-study payoff without overstating causality or converting source-reported numbers into independently verified facts.
3. Three relevant visible hashtags for the end of the description.
4. A separate comma-delimited YouTube tags field for Studio metadata.

Do not create a second metadata file and do not generate metadata from the renderer. Workflow Stage 5 blocks completion when any field is missing; Stage 6 blocks upload until the production doc is complete.

Supporting deliverables:

- `pipeline/hardknocks/render_hardknocks_v7.py`
- `pipeline/hardknocks/test_render_hardknocks_v7.py`
- `docs/production/hardknocks-v7-raising-canes-focus-bet.md`
- renderer work/QC under `output/projects/hardknocks/clips/v7_work/`

## Verification gates

1. Unit tests for timeline continuity, per-clip ceiling, source-usage ceiling, hook-caption onset, required sections, output duration, and no TTS.
2. `ffprobe`: duration, dimensions, codecs, fps, pixel format, audio sample rate/channels.
3. Full ffmpeg decode.
4. Manual frame-0 and 0–10s frame review.
5. Hook motion gate over 0–3s; reject effectively frozen footage.
6. Caption OCR/contact-sheet review for clipping, sync, and semantic relevance.
7. Brand/OCR review of every Pexels window.
8. Black-frame and silence scans.
9. Final-export ASR check for every critical phrase and number.
10. Manual narrative review: rejection → focus mechanism → capital proof → scale proof → rebuild rule.
11. Post-Production Retro and Workflow Delta before marking complete.
12. Publishing-metadata review: title gap, factual support, description/hashtag duplication, tag relevance, and absence of raw affiliate links.

## Explicit non-goals

- No upload.
- No separate metadata file or renderer-generated metadata JSON.
- No policy rewrite based on one render.
- No tax, investing, or legal advice.
- No generic subscribe/follow CTA.
- No raw affiliate link.
