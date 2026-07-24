# ADR 0036: Front-Loaded Visual Cadence and Purpose-Bound Audio

**Date:** 2026-07-24  
**Status:** Accepted

## Context

The evidence review of `OASaa6MKyZQ` found a materially denser hook than body: six strong changes in 0–10s, a sensitive-change median near 1.92s, and a strong-change median near 4.12s. The source argues for frequent editing, but neither its performance nor its stated “one cut per 1.5s” example isolates cadence as a causal driver. Blindly requiring hard cuts at one fixed rate would reward effect spam, damage sentence comprehension, and turn one observational case into an unsupported universal law.

The project already requires hook caption sync, frequent visual change, early SFX, purposeful transitions and proof-coupled visuals. The unresolved trade-off is how to front-load density without applying one editing rhythm or one emotional score architecture to every Short.

## Decision

1. `Visual Change` remains the countable cadence unit. A cut, reframe/zoom, overlay entry or exit, layout/source change, or continuous motion reset counts even when it is not new evidence.
2. A separate `Information Progression Gate` prevents quota gaming: across each narrative phase, the sequence of Visual Changes must collectively advance a question, causal step, contrast, proof state or payoff. Decorative changes may support cadence, but a phase made only of decorative changes fails.
3. Cadence is tiered:
   - final t=0–5s: target one Visual Change every 0.8–1.5s;
   - final t=5–10s: no unexplained Visual Change gap over 3s;
   - after final t=10s: no unexplained Visual Change gap over 6s.
   The 0.8–1.5s range is a production target and matched-test hypothesis, not proof that every Short needs a hard cut at that rate. Continuous purposeful motion can satisfy a window without damaging a spoken clause.
4. Three principles become project-wide baseline quality:
   - the edit progresses information rather than merely decorating time;
   - SFX are bound to visible or implied events instead of forming a constant effect bed;
   - the ending pays the opening loop rather than introducing an unresolved second lesson.
5. Audio architecture follows the content engine:
   - a narrative Short with a Problem → Discovery → Payoff spine uses distinct score states and a brief deliberate music attenuation before its decisive discovery or payoff;
   - an educational Short uses section-level audio contrast and is not forced into the three-state emotional arc;
   - all Shorts still obey ADR-0034’s early-SFX and purposeful-transition requirements.
6. Stock footage is labeled `ILLUSTRATION` only when a reasonable viewer could mistake it for real footage of the claimed person, event, product or evidence. Obviously generic illustration does not require a permanent label; it still cannot be described as proof.
7. The exact hook cadence remains testable. The next eligible matched test should compare a 0.8–1.5s Visual Change treatment with the prior 1–2s treatment while holding story, hook copy, proof order, audio treatment and packaging constant. Both arms must retain the same baseline quality, and MAB/lane eligibility still controls publication.

## Considered Options

- Make 0.8–1.5s hard-cut cadence mandatory throughout: rejected because the reference itself slows in the body and because comprehension is a higher-order constraint.
- Keep all findings local to HardKnocks V16: rejected because information progression, event-bound SFX and loop closure generalize safely across verticals.
- Label every stock shot `ILLUSTRATION`: rejected because obvious generic b-roll would add cognitive clutter without improving claim integrity.
- Force three score states onto every Short: rejected because educational explanations do not always contain a genuine Problem → Discovery → Payoff arc.

## Consequences

- ADR-0016’s undifferentiated 2–3s guidance is amended by this tiered policy.
- Stage 0 must establish cadence feasibility through 10s before production, and Stage 4 must inspect fixed frames/contact sheets rather than trusting scene detection alone.
- Editors cannot satisfy retention quality by counting arbitrary flashes, emoji or zooms while the story remains informationally static.
- Completed artifacts, including HardKnocks V16A/B/C, are not retroactively changed or rerendered.
- The exact 0.8–1.5s target may be revised after a valid matched test; the three project-wide baseline principles remain independent of that result.
