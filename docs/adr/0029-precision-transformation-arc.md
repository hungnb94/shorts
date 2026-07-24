# ADR 0029: Precision Transformation Arc — Narrative Template, Not Video Type

**Date:** 2026-07-15
**Status:** Proposed

## Context

The analysis of Jack Craig's AI pet-salon case study (`za2VyvLl5T0`) traced the actual generated Short to `TAsr3wIN_NY`, "I Removed 5,000 Tangles From This Street Dog For THIS🐕😳." The Short reached 694.8K views in its first 1 day 22 hours and 962,129 public views by the 2026-07-15 re-fetch. Creator Studio screenshots show 69.8% average percentage viewed at 694.8K views; an earlier 302,541-view screenshot shows +784 subscribers and 97.6% of traffic from the Shorts feed.

It is a six-phase transformation:

`DECLARE → ASSESS → ISOLATE → PROCESS → BUILD → REVEAL`

The strongest reusable mechanics are a concrete before-state, an irrationally precise completion promise, a sequence of proof-coupled micro-tasks, a visible before/after payoff, and a final collection board that promises a series. The generated Short has no genuine Teach phase.

Four scopes were considered during `/grill-with-docs`:

1. Extract only cross-cutting retention mechanics and leave every script structurally unchanged.
2. Add a specialized **Precision Transformation Arc** for the three existing niches without creating a new niche or Video Type.
3. Introduce a top-level script framework parallel and bind it to AI-Pure / Video Type #8.
4. Add a fourth AI-pet-transformation niche and reproduce the source format directly.

## Proposed Decision

Define **Precision Transformation Arc** as a specialized narrative template available to the three existing niches:

`DECLARE → ASSESS → ISOLATE → PROCESS → BUILD → REVEAL`

It is classified as a narrative/retention structure, not as:

- a fourth niche;
- a Video Type or rendering technology;
- a Source Channel itself;
- a Value-Add Type;
- a new MAB action-space dimension.

### Eligibility Gate

A topic may use the template only when all of the following are true:

1. **Concrete before/after state:** the viewer can judge transformation visually without niche expertise.
2. **Auditable process:** at least three intermediate steps can be shown, not merely narrated.
3. **Proof-coupled claims:** every important number/result appears with the relevant tool, screen, measurement, or observable state in the same beat.
4. **Completion promise:** the opening creates a task whose final state is withheld.
5. **Series potential:** a checklist, scoreboard, collection, test suite, progress board, or equivalent device can show what remains unfinished after this episode.
6. **Truthfulness:** precision may simplify a real process, but numbers may not fabricate evidence or imply that synthetic events happened in the real world.

If a topic lacks an observable transformation or requires explanation before the before/after matters, use another Narrative Arc/Source Channel Pattern instead.

### Required Retention Grammar

- Frame 0 shows the before-state plus meaningful action; no title card.
- Caption is visible by t=0.2s.
- Each phase contains local micro-payoffs; no process montage that postpones all value until the final reveal.
- New tool, proof object, state change, or continuous meaningful motion appears every 1-3 seconds.
- Build accelerates relative to Process.
- Reveal is short and visually compares before/after.
- The series CTA visualizes unfinished future progress; it does not merely say "follow for more."

## Evidence

Primary report:

- `docs/research/ai-pet-salon-viral-short-2026-07-15/REPORT.md`

Direct artifact findings:

- 58.1s, 1072×1920 source.
- 168 spoken words (~173.5 WPM).
- Phase shares: Declare 7.2%, Assess 13.8%, Isolate 28.8%, Process 21.7%, Build 20.4%, Reveal 8.2%.
- Threshold-0.1 cadence indicator: median 1.42s across the Short, 1.17s inside 0-10s.
- Studio: 82.6% APV at 993 views; 69.8% APV at 694.8K views after 1 day 22 hours.
- 97.6% Shorts-feed traffic at 302,541 views.

Evidence caveats:

- Exact format evidence is n=1.
- No Studio screenshot exposes Viewed vs swiped away or the repository's canonical Stayed to watch metric.
- Current comments are contaminated by referral traffic from the later case-study video.
- The long-form video is sponsored by Higgsfield; tool endorsement is not neutral evidence.
- The long-form headline says "24 Hours," while its celebrated 694.8K result is an hour-48 update.

## Consequences

- Narrative-template classification remains independent from Video Type, but the current production direction has already rejected animation-only/AI-Pure outputs as too visually monotonous. The first test must use footage-based `stock_footage` or `clip_curation`, with real screen recording as the primary proof surface. This ADR does not reopen the rejected visual types.
- The action space does not expand until an experiment validates the template and a separate decision promotes it to an AB variable.
- The first test must change only the narrative template while holding niche, output spec, base retention techniques, and other quality gates constant.
- This proposal does not revise ADR-0018's color-emphasis wording. The analyzed Short is a real single-token-caption counterexample, but caption policy requires its own explicit decision.
- This proposal does not revise the three-source-combo policy. The AI-Pure Short shows coherent procedural motion can substitute for external b-roll, but format scope requires a separate decision.
- Do not copy the creator's unsupported upload-spacing theory (one upload until a 12-hour flatline) or his inaccurate definition of swipe-through rate.

## Validation and Falsification

Before Accepted status:

1. Use AI education as the first candidate niche and select one topic that passes the Eligibility Gate.
2. Produce one Precision Transformation variant and one baseline narrative variant while changing no other AB variable.
3. Verify 9:16, H.264/AAC, 50-75s (ADR-0034 supersedes this proposal's original 30-60s range), caption timing, cadence, and all existing safety/transformative gates.
4. Wait the normal 48-hour analytics window.
5. Compare Stayed to Watch when Studio provides it, APV/AVD as secondary signals, retention dips at phase boundaries, and subscriber conversion.

The hypothesis is weakened if:

- viewers leave during Isolate/Process despite compliant cadence;
- proof objects do not make sense without excessive explanation;
- Teach feels bolted on after Reveal;
- the narrative variant does not improve hook/overall retention over the existing niche baseline;
- synthetic precision reduces trust or creates factual ambiguity.

### First-Test Constraints: AI Education

- Evidence must be captured from a real workflow run, not a fabricated terminal, fake benchmark, or generated "before/after" screenshot.
- Screen recording must remain readable and in motion; do not reproduce `aiwork_v6` as a static presenter plus illegible terminal background.
- The transformation must be legible to professionals/knowledge workers, not require developer-only jargon.
- Existing topics (`capability curve`, `prompt bloat`, `AI misalignment`) are research context, not automatic topic approval. Reusing one requires a genuinely new before/after experiment, not a recut of the same source claims.

### Provisional First-Test Topic: Research Audit

Candidate transformation:

`unsupported AI answer → isolated claims → primary-source checks → contradiction/uncertainty ledger → citation-backed answer`

The candidate fits the six phases as follows:

- **Declare:** show the unsupported answer and the number of claims requiring verification.
- **Assess:** identify which claims have no source, weak sources, or ambiguous wording.
- **Isolate:** split the answer into independently testable claims.
- **Process:** retrieve and compare primary sources; record support, contradiction, and uncertainty.
- **Build:** reconstruct the answer from supported claims only, with a visible claim ledger.
- **Reveal/Teach:** compare before/after and teach the portable rule: do not let AI compose the final answer before its claims are independently verified.

Guardrails:

- The initial answer must come from a real captured model run with the full prompt preserved.
- The source corpus must be public and reproducible; primary sources are preferred over summaries.
- A claim may remain unresolved. The experiment may not force every row into true/false.
- The score must be defined before the run and must not reward verbosity or citation count alone.
- No headline may promise a specific error reduction until the real run produces it.

## Candidate Domain Terms

These terms remain proposed and should not enter `CONTEXT.md` until this ADR is accepted:

- **Precision Transformation Arc:** the six-phase narrative template defined above.
- **Proof-Coupled Claim:** narration, visible tool, and observable number/result landing in the same beat.
- **Completion Ladder:** micro-tasks that each close locally and open the next.
- **Collection Board CTA:** an unfinished visual collection that turns subscribe into a promise of future progress.

## Related

- ADR 0003: AB Test One Variable
- ADR 0012: AI Video Generation Pipeline / Video Type #8 (AI-Pure)
- ADR 0018: Hook Caption Sync and Cadence
- ADR 0020: Third Niche — AI Education / Fourth-Niche Ask-First Gate
- ADR 0027: Proof-First Narrative
- ADR 0028: Decision-Lock Narrative
- `docs/research/ai-pet-salon-viral-short-2026-07-15/REPORT.md`
