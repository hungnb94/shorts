# ADR 0033: Counter-Evidence Ladder for Food-Trial Shorts

**Date:** 2026-07-19  
**Status:** Accepted

## Context

The user supplied Law By Mike's [How Parents Catch Their Kids Sneaking Out](https://www.youtube.com/shorts/oqcCGjXqFWk) as a format reference and requested a multi-video analysis before locking the decision. The resulting report is:

- `docs/research/law-by-mike-counterplay-2026-07-19/REPORT.md`

The reference is a deliberate semantic remake of a mature 102.9M-view predecessor. Across the inspected set, the transferable mechanic is not simply fast captions or frequent cuts. It is nested counterplay:

- tactic → bypass → upgraded tactic;
- weak signal → stronger test → planted trap;
- claim → contextual rule → exception → exception-to-exception.

The comparison does not establish causality because upload age, topics, cast, distribution, and private retention data are uncontrolled.

## Decision

Adopt `Counter-Evidence Ladder` as the **default production hypothesis** for the first `Food-Trial Short` prototype.

### Narrative rules

1. One episode evaluates one falsifiable accusation about one `Recipe Case`.
2. The viewer is given enough information to form an initial provisional verdict.
3. Every new evidence beat must do at least one of the following:
   - directly rebut the preceding implication;
   - change its meaning through relevant serving/preparation context;
   - introduce a valid exception;
   - expose a hidden assumption in the prior calculation;
   - turn an earlier object or statement into decisive proof.
4. A correct but disconnected nutrition fact is excluded from the narrative ladder. It may remain in research notes or the description.
5. Evidence is weighted by relevance to the charge. Prosecution and defense do not receive equal card counts by default.
6. Each claim must be proof-coupled to the visible Recipe Case ingredient, quantity, declared yield, plating, or calculation assumption.
7. The last evidence beat resolves the original accusation; it does not merely add another metric.
8. `Companion-Meal Verdict` remains mandatory and converts the factual finding into a concrete second-meal and/or portion action.
9. `Lobby Acquittal Twist` remains optional and unannounced. When used, it should be an `Earned Evidence Callback` tied to an ingredient or faction already introduced. It never supersedes the factual finding.

### Production treatment

Keep the existing constrained treatment:

- moving source recipe footage inside `Living-Comic Treatment` panels;
- one stable `Judge-Narrator Treatment` voice;
- prosecution and defense represented by visually distinct text cards, evidence files, scale movement, and sound design rather than three separately animated/TTS characters;
- `On-Screen Nutrition Evidence` limited to energy, protein, fiber, and one case-specific warning;
- repository `Transformative Gate` rules still apply to reused source footage.

This ADR chooses a semantic engine, not Law By Mike's actors, captions, legal-advice surface, props, or set design.

## Prototype skeleton

1. Charge and provisional viewer judgment.
2. Prosecution material evidence.
3. Defense context that changes its implication.
4. Prosecution counter-to-counter.
5. Defense exception or admissible mitigation.
6. Decisive evidence and factual finding.
7. Companion-Meal Verdict.
8. Optional earned factual/comedic/lobby callback.

The exact number and duration of rounds remain production variables. The first prototype should not add a reversal unless it materially changes the case.

## Alternatives considered

### Alternating independent evidence

Rejected as the default. It can create superficial motion while remaining an evidence dump and encourages false balance.

### Copy the three-trick Law By Mike surface structure

Rejected. The three-prop structure is source-channel execution, not the transferable principle. Nutrition cases may require a different number of material counters.

### Linear nutrition explanation with a courtroom skin

Rejected. It does not satisfy the user's repeated-viewer-reversal goal and adds production complexity without changing the information experience.

### Full multi-character courtroom skit

Deferred. It would provide direct character dialogue but conflicts with the current lack of AI character-video generation and increases voice/animation cost. Text factions plus one Judge-Narrator preserve the semantic conflict at lower production cost.

## Consequences

### Positive

- Evidence becomes a causal story rather than a label dump.
- The viewer has a reason to continuously update a judgment.
- Multiple true facts can coexist without moralizing food.
- Source footage has a clear editorial role as evidence.
- The Companion Meal resolves the case instead of appearing as an unrelated tip.
- Earned callbacks support recurring court lore and the fictional lobby twist.

### Negative

- Research and calculation cost increases because every counter must use the same serving model and remain scientifically defensible.
- Some Recipe Cases will not support enough valid counters and must be rejected rather than padded.
- Reversal pressure can encourage cherry-picking or false equivalence; evidence admissibility needs an explicit QC gate.
- Dense counterplay can overload viewers if captions or metrics appear simultaneously.
- A corrupt-judge gag can weaken health credibility unless the factual verdict is visually preserved.

## Validation plan

Treat the format as a hypothesis, not a proven causal formula.

For the first completed Food-Trial prototypes:

- document each evidence beat and the exact prior implication it changes;
- reject disconnected facts during script review;
- verify all ingredient amounts, serving assumptions, and calculations before render;
- manually inspect whether visuals show the evidence at the same beat as the claim;
- preserve the factual finding before any Lobby Acquittal gag;
- compare future Studio hook/retention evidence against simpler narrative variants without treating public views alone as proof.

## Acceptance scope

`Counter-Evidence Ladder` is accepted as the default Food-Trial narrative engine for the first prototype and empirical test. Acceptance does not claim external causal validation or permanently prevent simpler narrative variants from being tested later.
