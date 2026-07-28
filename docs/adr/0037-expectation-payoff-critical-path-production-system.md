# ADR 0037: Expectation-Payoff and Critical-Path Production System

**Date:** 2026-07-28  
**Status:** Accepted

## Context

The user supplied the English `How to Succeed in MrBeast Production` PDF and asked that its knowledge become an operational tool for this Shorts project. The source repeatedly emphasizes that the objective is the best YouTube viewing experience rather than maximum production polish; packaging sets viewer expectations; the opening receives disproportionate attention; strong formats make progress toward a withheld payoff visible; “wow factor” creates a memorable distinction; critical components and bottlenecks must be protected; creativity can substitute for spend; dull moments damage retention; and the ending should follow a satisfying payoff without outro drag.

The source also explicitly says it is not a literal rulebook. It describes a long-form production company, uses long-form CTR/AVD/AVP and minute marks, and contains internal staffing/operations language that should not become creator policy. A direct copy would conflict with this repository’s Shorts-specific metrics, 50–75 second duration, MAB selection, plateau-gated channel rotation, copyright controls, paid-generation approval and media-first QC.

Before this decision, the workflow had a strong 0–3 second Hook Gate but no blocking contract that aligned title/frame-0/first-line expectations with a verified final payoff. Source selection did not require an explicit critical-component ledger and backup. EDL construction did not require one visible progression engine or a signature moment. Cadence and information progression were defined, but there was no interval-level dullness audit, and post-production learning could still collapse several changed layers into the vague label “MrBeast editing.”

Source material and project interpretation:

- `docs/references/mrbeast-production-guide-original-en.md`
- `docs/guides/mrbeast-short-form-production-system.md`

## Decision

1. Add a blocking **Stage -1 Expectation & Payoff Contract** before the Hook Gate. Generate three lightweight candidate packages before download/polish, eliminate false, unverifiable or infeasible packages, then let MAB select among eligible treatments rather than letting an editor pick by taste. Every new Short or material revision defines:
   - audience and minimum context;
   - one visible objective/stakes/open question;
   - exact final payoff and the source/artifact that proves it;
   - draft title, frame-0 and first spoken/caption promises, all resolving to the same payoff;
   - the exact experiment layer, frozen layers, mature primary metric and falsification condition.
2. Require one visible **progression engine** with 3–5 states, such as challenge/bet, stair-step, attempt ladder, claim/counter-evidence/verdict or trade/value ladder. A quote montage does not qualify unless each quote changes the causal state.
3. Require a declared factual **Signature Moment hypothesis** that is difficult to substitute with generic production, or explicitly record `none found`. It may be a source-native reveal, verified comparison, counter-evidence flip, causal data visualization, multi-source proof reveal or story-native interaction. Effect volume alone does not qualify, and the absence of spectacle alone cannot fail an otherwise strong, truthful payoff.
4. Add a **Critical Component ledger** during source feasibility. Every component whose failure destroys the honest video records an owner, verification evidence, blocking state and backup. Resolve this critical path before cosmetic polish and record negatives/failure modes, not only attractive options.
5. Add three semantic final-artifact gates:
   - expectation match across title/frame 0/first line/payoff;
   - an interval-level no-dull-moment audit where each retained span has a story job or deliberate breathing-room function;
   - abrupt-payoff safety: remove outro drag only after final meaning, proof readability, audio decay and post-word margin are complete.
6. Treat CTA as content. It must preserve the moving story state, remain diegetic/compact under existing project rules and never be evaluated through a deliberately low-quality control.
7. Decompose “MrBeast formula” into separately testable layers: expectation/package, hook mechanism, proof timing, progression engine, signature moment, editing grammar, CTA integration, payoff/ending and publishing state. One upload cannot validate or falsify the combined system.
8. Require a post-publish retention postmortem that records distribution state first; 0–3s and 0–10s response; the three largest rises/drops mapped to exact EDL/caption/SFX; the CTA region; payoff-onset-to-EOF retention; expectation delivery; and exactly one controlled change. Compare within the same lane/vertical and at equivalent maturity rather than pooling all nine channels.
9. After a measured failure, continue the loop: exact-timestamp lesson → expert/case-study research → one strategy change → next eligible treatment. Existing MAB and lane rules continue to decide publication.
10. Keep all long-form timing, CTR and spectacle examples as contextual inspiration. This ADR does not introduce a universal cut rate, arithmetic conversion of minute marks, spending requirement or permission to exaggerate claims.
11. Preserve existing stage identifiers, but run Stage -1 in two passes: Stage -1A creates lightweight package/payoff hypotheses before source discovery; Stage 1 finds and verifies candidate spans; Stage -1B replaces assumptions with exact payoff/critical-component artifacts and locks the contract; then Stage 0 runs as the blocking pre-cut Hook Gate before Stage 2–7. A pass-A hypothesis is never verified proof.

## Considered Options

### Copy the source literally

Rejected. Long-form minute marks, thumbnail CTR, expensive spectacle and internal staff-management language do not transfer directly to Shorts and would conflict with accepted project policies.

### Keep the PDF only as optional reading

Rejected. Passive reference would not close the workflow gaps around expectation/payoff mismatch, source feasibility, quote-montage bodies and vague framework diagnosis.

### Add guidance to skills without changing project policy

Rejected. Skills would then require artifacts that `docs/WORKFLOW.md` did not enforce, creating two divergent operating systems.

### Edit the workflow without an ADR

Rejected. Stage -1, critical-component tracking and new completion gates are general project rules, not one-video sequencing notes. The workflow’s own retro policy requires a new ADR for a genuinely new rule.

## Consequences

- Concept rejection happens earlier, before renderer work, when payoff/proof or rights are weak.
- Production documents gain three lightweight candidate packages, an expectation/payoff contract, progression states, a declared signature-moment hypothesis, critical-component ledger and scoped experiment hypothesis.
- Editors cannot satisfy “MrBeast-style” production by increasing cuts or effects alone.
- The Mid-Roll Triple CTA remains required under existing ADRs, but its execution must behave as story content rather than a detached interruption.
- Final QA now checks semantic promise/progression/payoff in addition to codec, ASR, detector and visual composition gates.
- Production may spend slightly more time on pre-production contracts and feasibility, but should reduce expensive late rewrites and paid retries.
- Exact thresholds remain governed by existing Shorts ADRs and matched tests. This decision does not retroactively rerender completed videos.
