# Framework and Technique Experiment Registry

Snapshot: 2026-07-25 09:42 +07

## Purpose

This registry prevents two opposite mistakes:

1. declaring a framework dead because one combined video failed;
2. adopting a technique because one early upload received a larger initial test.

A Short is not one framework. It is a bundle of independently variable layers:

1. **Source/topic/package:** subject, story, title and audience fit.
2. **Hook mechanism:** contradiction, question, number, comparison or live action.
3. **Narrative architecture:** the causal order that carries the body and payoff.
4. **Editing grammar:** cuts, reframes, evidence panels, captions, motion, SFX and information-state cadence.
5. **Evidence/value-add layer:** citations, verification, data visualization and commentary.
6. **Publishing/measurement:** channel, lane, visibility, timing and metric availability.

A bad bundle does not falsify every layer inside it. Every experiment must name the exact layer under test and freeze the others.

## Status vocabulary

| Status | Meaning | Promotion/demotion rule |
|---|---|---|
| `NOT TESTED` | Exists only as a draft or local artifact | Requires a real eligible upload |
| `IN FLIGHT` | Public, but younger than the 48h measurement window or missing Studio truth | Do not classify from views alone |
| `PROMISING — EARLY` | Beats a matched leading indicator, but has no mature primary metric | Requires follow-up; never call validated |
| `INCONCLUSIVE` | Observed, but confounded or missing primary metrics | Run a controlled or matched test |
| `UNDERPERFORMING SIGNAL` | Materially behind a relevant cohort, but causal attribution is incomplete | Inspect distribution and retention before retirement |
| `FALSIFIED IN SCOPE` | A predeclared hypothesis failed under a sufficiently controlled test, or a direct media defect aligns with the measured failure | Retire only the exact mechanism/scope tested |
| `VALIDATED` | Repeated controlled/matched tests improve the predeclared primary metric without a material downstream regression | Scale within the tested scope; continue holdout monitoring |
| `VALIDATED FOR BASE QUALITY` | Repeated evidence shows the technique prevents defects; it is not an AB variable anymore | Apply by default, keep monitoring |

## Evidence hierarchy

From strongest to weakest:

1. direct defect-to-retention alignment in the actual uploaded media;
2. same-source/same-body test changing one variable;
3. randomized or matched cohort with predeclared primary metric;
4. cross-story cohort correlation;
5. public views without Studio distribution/retention;
6. creator intuition or offline aesthetic preference.

### Failure rule

A framework is not marked `FALSIFIED IN SCOPE` merely because a video has low views. Require either:

- one direct, timestamp-aligned defect with a matching retention failure; or
- at least two independent, mature tests below the predeclared primary metric with the main confounders controlled.

The repository's Traction threshold (`10K views in 7 days`) is a business outcome. Missing it says the bundle failed commercially; it does not identify which framework caused the failure.

### Promising rule

A technique may be marked `PROMISING — EARLY` only when:

- it beats a relevant age-matched or Studio leading indicator;
- the mechanism is visible in the uploaded bytes;
- the result is labeled as correlation, not cause;
- the next falsification test is specified.

Promotion to `VALIDATED` requires at least three independent tests with improved Studio `How viewers engaged / Stayed to watch`, no material loss in AVD/APV, and no repeated business-outcome regression.

## Current registry

### Confirmed failed execution patterns

| Pattern | Scope | Evidence | Status | Decision |
|---|---|---|---|---|
| Static title-card opening | Hook execution | Bác sĩ Hải V4: 91.4% Swiped Away; opening is a static card | `FALSIFIED IN SCOPE` | Do not use static title-card frame 0 |
| Full-screen stock replacing the speaker repeatedly in 0–10s | Hook execution | Giannis uploaded render: three speaker blackouts; retention decline aligns with the second/third blackout; 62.9% Swiped Away | `FALSIFIED IN SCOPE` | Preserve face/action and use partial evidence layouts in the protected hook |

These are execution failures, not evidence that all stock footage, all title text or all clip curation fails.

### HardKnocks narrative/format families

Public-view counts below are current snapshots, not retention truth and not age-normalized unless explicitly stated.

| Family | Uploaded evidence | Public outcome snapshot | Primary-metric evidence | Status | Interpretation |
|---|---|---:|---|---|---|
| Contiguous original-voice founder reveal | V1 | 1,258 views | Real Studio: 54.1% Stayed, 45.9% Swiped Away, 0:30 AVD | `INCONCLUSIVE`, current Studio benchmark | Best verified HardKnocks hook response, but still missed Traction |
| Implied Comparison / same-person callback | V2–V5 | 1,100 / 1,004 / 1,195 / 554 | V2 has API-only APV; no reliable Studio set | `INCONCLUSIVE` | Repeated ~1K ceiling; neither breakout nor clean falsification |
| Authority-led hidden economics / focus bet | V6–V7 | 641 / 1,144 | Pending | `INCONCLUSIVE` | V7 matched the channel's ~1K ceiling; attribution unavailable |
| Active-speaker reframing + semantic zoom | V8 | 1,148 | Pending | `INCONCLUSIVE` as a performance driver; retain as craft | A single editing primitive cannot be credited from one cross-story upload |
| Live-approach + original voice | V9R / V10R | 979 / 761 | Pending | `INCONCLUSIVE` | V9's unlisted zero-view state is publishing/distribution evidence, not a content verdict |
| Blindspot Verification / Business Lesson Payoff | V11 / B1 | 60 / 260 | Pending | `UNDERPERFORMING SIGNAL` | Two severe relative misses; still lacks Studio distribution/retention separation |
| Theragun chronological clarity | V15A | 286 views at 34.38h | Younger than 48h at snapshot | `IN FLIGHT`, weak early signal | Clearer story did not itself produce a strong initial response |
| MrBeast-informed front-loaded information progression | V16B | 318 views at 14.94h; user-reported Studio rank 1/10 | Younger than 48h at snapshot | `PROMISING — EARLY` | Strongest recent early signal; not yet a retention or causal win |

### V16B technique decomposition

Do not register “MrBeast editing” as one indivisible framework. V16B changed several things versus V15A:

| Changed variable | V15A | V16B |
|---|---|---|
| Public title | `A Crash Created Theragun` | `The Crash Wasn't the Idea` |
| Hook semantics | States the cause and closes the loop | Rejects the obvious cause and opens a question |
| Hook headline | `THE THERAGUN ORIGIN` → `A CRASH STARTED IT` | `THE CRASH WASN'T IT` → `SO WHAT WAS?` |
| Hard cuts in final 0–10s | 2 | 4 |
| Non-caption information-state events in final 0–10s | Sparse | 9 observed/designed events |
| Partial evidence panel in hook | None | Injury panel begins at ~0.42s |
| Body/payoff | Crash → invention → company distinction | Crash → clinic failure → motion → first product |
| Audio grammar | One main score state | Problem/discovery/payoff states plus event SFX |

Therefore V16B supports the combined hypothesis:

> Contrarian open loop + front-loaded information progression + event-bound sound improves initial viewer acceptance relative to a resolved, slower hook.

It does **not** isolate hard-cut frequency.

## Required next test

### Hypothesis

Within a matched HardKnocks story, increasing meaningful information-state cadence in final 0–5s to one event every 0.8–1.5s improves real Studio `Stayed to watch` without lowering AVD/APV.

### Treatment definition

Count an event only when it changes what the viewer knows or where proof is located:

- speaker/shot cut;
- semantic reframe or crop;
- evidence panel appearing/disappearing;
- persistent headline state change;
- proof object or causal annotation;
- purposeful audio-state transition paired with a narrative event.

A dialogue-caption burst alone is tracked separately. Decorative shakes, particles or arbitrary b-roll do not count.

### Controlled design

1. Use one new source/story and one frozen 50–75s body.
2. Freeze title, spoken hook, source windows, captions, music bed, CTA, payoff and metadata.
3. Create only two 0–10s treatments:
   - **Sparse control:** V15-like hard-cut gaps around 3s; no partial evidence panel.
   - **Dense treatment:** meaningful state every 0.8–1.5s in 0–5s and every 2–3s in 5–10s.
4. Run blind cold-viewer retell before upload. Both must communicate the same who/problem/question.
5. Publish only when lane eligible. Do not upload simultaneously or delete the loser.
6. Primary metric after 48h: real Studio `How viewers engaged / Stayed to watch`.
7. Secondary metrics: Swiped Away, AVD/APV, 0–10s retention shape, shown-in-feed trajectory and views at equal elapsed time.
8. Falsification: if the dense treatment does not improve Stayed to watch, or improves hook response but causes a meaningful AVD/APV decline, frequent information progression is not a net win in that scope.

Until this test runs, V16B remains `PROMISING — EARLY`, not validated.