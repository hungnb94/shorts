# ADR 0031: Cross-Story Hook Outputs Are Comparisons, Not Controlled Experiments

**Date:** 2026-07-17
**Status:** Accepted

## Context

Three high-performing School of Hard Knocks Shorts were reviewed for opening grammar:

- `BaNHv_WKzr0` — live approach outside a wealthy residence;
- `Q_oBqwgdoLw` — live approach around a Rolls-Royce and an age/status contradiction;
- `_n4oZF3uzME` — live interruption at a vehicle followed by ownership verification.

All three are winner samples. The review did not include a matched lower-performing control with the same story and a different opening. Their shared Live-Approach pattern is therefore observational evidence and a production hypothesis, not proof that the pattern caused their performance.

Production selected two stories from `E_9nX5ReMcY`:

- V9: `$200M` exit, `$100M` company collection, `$10K` check, and the decision to build independently;
- V10: age 30, on track for more than `$100M`, robot business, drone origin, and `get rich slow`.

The stories differ in protagonist, source ranges, claims, arc, evidence, duration, and payoff. Calling V10 a control for V9 would create a false experimental interpretation.

## Decision

1. Treat **Live-Approach Hook** and **Money+Number Hook** as scoped production hypotheses, not universal causal rules.
2. V9 uses the Live-Approach treatment because its source begins with a real interruption and visible mansion/status context.
3. V10 uses the Money+Number treatment because its strongest source-native contradiction is `>$100M → age 30 → host disbelief`.
4. Report V9 and V10 as **comparisons only**. Their future metrics may inform story-level learning, but cannot isolate hook-format causality.
5. A controlled hook experiment must:
   - use the same protagonist and story;
   - preserve source windows after the hook, duration, captions, evidence, audio mix, metadata timing, and upload conditions as closely as possible;
   - change only the opening treatment;
   - predeclare the primary metric and comparison window.
6. Do not promote Live-Approach to the default hook for future videos until matched evidence supports it.
7. ADR-0017 remains a hard gate above hook-style preference. When a live-approach source frame lacks a visible face, production must select a different range or apply a non-misleading same-source treatment that preserves a moving face without full-screen stock replacement.

## Considered Options

- **Call V10 the control for V9:** rejected because nearly every meaningful content variable changes; any result would be confounded.
- **Adopt Live-Approach as the new default from the three winner samples:** rejected because there is no matched loser/control and survivor bias is unresolved.
- **Force both stories into the same hook format:** rejected because the source-native strongest beat differs; this would weaken one story without creating a valid control.
- **Avoid documenting the distinction because it is “only production”:** rejected because future analytics could otherwise be misread as causal evidence and contaminate MAB/domain learning.

## Consequences

- V9 and V10 may both be published and measured, but their metrics must not be used to claim that Live-Approach beats Money+Number or vice versa.
- Research and production documents must label observations, interpretations, hypotheses, and causal claims separately.
- Hook retros must state the main risk and the exact retention interval to inspect.
- A future matched experiment requires an additional render of the same story rather than comparison against a different Short.
- This ADR changes experiment interpretation, not the global video type, MAB action space, or autonomous optimization schedule.

## Related

- `docs/research/sohk-opening-pattern-2026-07/REPORT.md`
- `docs/production/hardknocks-v9-live-approach-200m.md`
- `docs/production/hardknocks-v10-100m-get-rich-slow.md`
- ADR 0017: Hook-Window Source Selection
- ADR 0018: Hook Caption Sync and Cadence
- ADR 0030: Active-Speaker Reframing and Semantic Zoom
