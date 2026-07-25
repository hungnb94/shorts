# All-Upload Performance Root-Cause Review — 2026-07-25

## Executive conclusion

The uploaded portfolio has a confirmed **Business Outcome Failure** at the first rung of the project ladder, but public data alone cannot prove a portfolio-wide Distribution Outcome or Viewer-Response Outcome.

The working root-cause order agreed in the grilling session is:

1. **Production System — primary working hypothesis:** 0–3s Hook execution is not being validated against a cold viewer before publication. The project has a detailed Hook Gate, but the production record contains no naive-viewer evidence for any Short.
2. **Measurement & Learning System — confirmed systemic failure/amplifier:** most due metrics remain `pending`, OAuth is not configured, the persisted MAB state stopped updating on 2026-07-05, and many nominal experiments changed several causal variables at once. The system is producing variants, not accumulating reliable learning.
3. **Publishing System — confirmed policy/enforcement failure, causal effect on views unproven:** release cadence and visibility changes confound attribution and repeatedly contradict the repository's Plateau-Gated Cadence policy.
4. **YouTube Recommendation System — unsupported as root cause:** public views do not establish algorithmic suppression. No current Shorts Feed share exists for most uploads.

This is not “all videos failed because YouTube suppressed the channel.” The stronger diagnosis is: **the Production System is shipping hooks without an externally-observed comprehension gate, while the Measurement & Learning System is too incomplete to correct that behavior.**

## Scope and evidence standard

Scope chosen by the user: every known Short uploaded from this repository across MONEY BLINDSPOT, the health channel, the AI-education channel, and the known Doog Radio upload.

Snapshot time: `2026-07-25 09:01:59 +07`.

Evidence used:

- direct live `yt-dlp` reads of every known video ID;
- direct channel Shorts shelves for the four identified upload channels;
- `docs/experiments/EXPERIMENT-LOG.md`;
- production documents under `docs/production/`;
- `data/mab_state.json`;
- the project's accepted workflow and ADRs;
- official YouTube Help guidance on Shorts discovery and upload scheduling.

Evidence deliberately not claimed:

- no current Studio Shorts Feed share for most uploads;
- no current Studio Viewed/Swiped Away for most uploads;
- no valid inference from API `averageViewPercentage` to Studio `Stayed to watch`;
- no claim that upload frequency itself caused YouTube suppression;
- no claim that a public view count identifies whether viewers rejected a Short or never received an impression.

## Portfolio snapshot

Known uploads in the evidence set: **33**.

- Public: **31**
- Unlisted: **2** (`EpTPDrWONS0`, `U_3cCYOcCmk`), both currently reporting zero public views
- Public Shorts that had completed the 7-day Traction window: **26**
- Mature Shorts reaching Traction (`>=10,000 views in 7 days`): **0/26**
- Public Shorts still inside the 7-day window: **5**

### Channel-level public outcomes

| Channel scope | Public n | Median public views | Mean public views | Range | Mature at 7d | Reached 10K/7d |
|---|---:|---:|---:|---:|---:|---:|
| MONEY BLINDSPOT | 24 | 436 | 564.9 | 52–1,258 | 19 | 0 |
| Health | 3 | 917 | 857.0 | 254–1,400 | 3 | 0 |
| AI education | 3 | 711 | 647.7 | 330–902 | 3 | 0 |
| Doog Radio mapped upload | 1 | 541 | 541.0 | 541 | 1 | 0 |

The five public uploads still inside seven days at snapshot time were:

| Video ID | Age at snapshot | Public views |
|---|---:|---:|
| `IamwYa68Av0` | 6.42d | 60 |
| `SInUCQ58xzU` | 5.77d | 260 |
| `vzAjnoAqQ78` | 2.49d | 977 |
| `FA7c1g4PvX0` | 1.40d | 286 |
| `aK1AODnLohE` | 0.59d | 318 |

These five cannot yet be called 7-day Business Outcome Failures. V15 and V16 were also not yet eligible for the project's 48-hour analytics judgment at the snapshot time.

## What improved — and where progress stopped

MONEY BLINDSPOT did not remain flat across the whole history:

| Cohort | Public n | Median views | Mean views | Range |
|---|---:|---:|---:|---:|
| Pre-playbook through 2026-07-08 | 7 | 176 | 157.0 | 52–238 |
| Daily run, 2026-07-09 through 2026-07-17 | 12 | 991.5 | 879.8 | 160–1,258 |
| Public uploads after 2026-07-17 | 5 | 286 | 380.2 | 60–977 |

The middle cohort's median is about **5.6×** the early cohort's median. Production changes therefore produced a real public-outcome improvement. The issue is not “nothing in the Production System works.” The issue is that the portfolio reached an approximately 1K-view ceiling and did not earn the next distribution expansion.

The post-2026-07-17 cohort must not be compared as a mature cohort: all five were younger than seven days at the snapshot, and two were younger than 48 hours.

## Root-cause tree

### 1. Production System — primary working hypothesis

#### Observed

The historical Studio datapoints that do exist all miss the current `<20% Swiped Away` target by a large margin:

| Short | Swiped Away |
|---|---:|
| `YQTWHqTS1e8` | 91.4% |
| `ChWLcE3OYpA` | 57.7% |
| `dF0Rr2C0Msc` | 62.9% |
| `dHDpDXSIAkA` | 45.9% |
| `Mw7jeR6R6iE` | 56.3% |

This is direct evidence that at least the measured historical Production System repeatedly failed the cold-viewer selection gate. It does not prove the same percentages for newer Shorts.

The workflow already requires a naive viewer to watch the rough 0–3s Hook without context and state the open question/promise. A repository-wide search of production docs found no recorded naive-viewer result. By contrast, the docs contain extensive creator-side checks for caption size, timing, frame composition, SFX, cadence, ASR, overlays, and media validity.

#### Interpretation

The project has optimized what the editor can inspect while failing to persist evidence for what only a cold viewer can reveal: immediate comprehension and curiosity.

The likely Production System failure is therefore **Hook Gate enforcement**, not the absence of another font, transition, renderer effect, or checklist item.

#### Second-order effect

Because the creator already knows the source story, a self-review can decode a frame/caption combination faster than a feed viewer. Adding more craft layers can then increase creator confidence without increasing cold-viewer comprehension. The system responds to weak performance by increasing production complexity, which raises cost and expands the action space without isolating the broken gate.

#### What remains unproven

Public data cannot rank these hook sub-causes for the latest Shorts:

- frame-0 visual legibility;
- hook-copy comprehension;
- topic/stakes strength;
- visual/verbal mismatch;
- early audio;
- wrong audience personalization.

A controlled Hook experiment is required.

### 2. Measurement & Learning System — confirmed systemic failure

#### Observed

- Most production metrics remain `pending` well past their due dates.
- The real fetcher cannot authenticate because `GOOGLE_CLIENT_ID` is missing.
- The official API would still not provide Shorts Feed share or Swiped Away; Studio evidence remains necessary.
- `data/mab_state.json` reports its last updates on `2026-07-05`, before most current production uploads.
- Its variant rewards are not connected to the current portfolio's Studio outcomes.
- Production docs repeatedly state that comparisons are not controlled experiments: stories, protagonists, body, hook, narration, captions, evidence, duration, and payoff often change together.

#### Interpretation

The claimed autonomous optimization loop is not the current working system. The repository itself says the real pipeline is manual/semi-manual. MAB cannot select a winner from feedback it never receives, and cross-story comparisons cannot identify which Hook treatment caused an outcome.

#### Second-order effect

Each new format increases the number of plausible explanations. With roughly one observation per combination, the project accumulates novelty faster than evidence. Failure triggers another creative variation instead of a falsifiable update.

### 3. Publishing System — confirmed policy violation, effect size unknown

For MONEY BLINDSPOT's July sequence:

- measured upload intervals: **21**;
- intervals under 24 hours: **14**;
- intervals under 12 hours: **5**;
- V9 → V9R: **1.76 hours**;
- V15 → V16: **19.43 hours**.

Current live state also contradicts historical records:

- `U_3cCYOcCmk` was documented as public but is now unlisted with zero public views;
- `aK1AODnLohE` was documented as private but was public at the snapshot;
- V15 and V16 were published on consecutive days even though V15 had not reached the 48-hour minimum, much less a two-check Distribution Plateau.

ADR-0035 was accepted on 2026-07-19, so pre-ADR daily uploads are historical rather than violations of a rule that did not yet exist. Post-ADR V15 → V16 is a direct enforcement failure.

This makes experiment attribution unreliable. It does **not**, by itself, prove that YouTube penalized the channel for frequent uploads.

### 4. YouTube Recommendation System — unsupported as primary cause

Official YouTube Help says Shorts are ranked using performance and viewer personalization. When recommended, the system considers whether viewers choose to watch or ignore the video, whether they stay, average view duration, average percentage viewed, likes, and post-watch survey satisfaction. YouTube also names topic interest, competition, and seasonality as external influences.

Source:

- https://support.google.com/youtube/answer/11914225?hl=en

Official upload-schedule guidance recommends a consistent, sustainable schedule and explicitly asks creators to choose between lower-frequency/high-production and higher-frequency/easier production. It does not establish a universal “daily posting penalty.”

Source:

- https://support.google.com/youtube/answer/13616979?hl=en

Therefore:

- a roughly 1K-view ceiling is consistent with an initial recommendation test that did not expand, but public data cannot prove that mechanism;
- “YouTube suppressed the channel” is not supported;
- topic interest, competition, personalization, and viewer response remain live alternative explanations.

## Controlled next move

The next production should be treated as a diagnostic, not another unconstrained creative iteration.

1. Pause new public uploads until the test package is ready and the lane is eligible.
2. Select one protagonist, story, source window, body, duration, captions, evidence, audio mix, metadata timing, and upload conditions.
3. Build three materially different 0–3s openings only.
4. Blind-test the three openings with viewers who have not seen the source or brief.
5. Require each viewer to state, without prompting:
   - what is happening;
   - what unresolved question/stakes they perceive;
   - which version they would continue watching;
   - why.
6. Persist anonymized, verbatim responses in the production doc. Creator/agent self-review does not count.
7. Publish only the offline winner, after Publishing System eligibility passes.
8. Predeclare Studio `Swiped Away` at 48h as the primary metric; target `<20%`.
9. Treat AVD/APV, likes, comments, and public views as secondary outcomes.
10. Do not change the body in response to the Hook test; otherwise the result is no longer diagnostic of the Hook.

This follows ADR-0031's existing rule that a valid controlled Hook experiment keeps the protagonist/story/body and upload conditions stable and changes only the opening treatment.

## Falsification rules

The Production/Hook hypothesis is weakened if:

- blinded viewers consistently understand and prefer the selected Hook;
- the published Short receives healthy Shorts Feed share;
- yet Studio Swiped Away remains above target across repeated matched tests.

In that case, move one level down the funnel:

- if viewers choose to watch but AVD collapses, investigate body retention/payoff;
- if Viewer Response is strong but Shorts Feed share is low, investigate Publishing/Recommendation distribution;
- if both are strong but views remain below Traction, investigate topic interest, competition, audience/channel fit, and target realism.

## Decision record from the grilling session

Resolved without a new ADR because these choices are reversible diagnostic procedure, not hard-to-reverse architecture:

- replace overloaded “flop” with the three-layer Performance Outcome model;
- use the Business Outcome Ladder: 10K/7d, 100K/30d, 1M lifetime;
- inspect all known repository uploads, not only MONEY BLINDSPOT;
- accept public-only diagnosis with explicitly low causal confidence;
- separate Production, Publishing, Measurement & Learning, and YouTube Recommendation system boundaries;
- rank Production System first as the user's primary working hypothesis;
- narrow the Production hypothesis to 0–3s Hook execution;
- default unresolved timeout decisions to Hook Gate enforcement failure and a paused, controlled three-Hook diagnostic.
