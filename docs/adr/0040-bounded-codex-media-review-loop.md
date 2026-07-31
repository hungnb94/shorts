# ADR 0040: Bounded Codex Media Review Loop

**Date:** 2026-07-30  
**Status:** Accepted

## Context

Codec/spec checks do not judge whether a Short is understandable, emotionally sharp or likely to retain attention. The user requested an independent Codex review after each completed revision, followed by repeated actionable revisions until the internal quality score is approximately 98.

An unconstrained score can create false precision and an infinite polishing loop. It also cannot guarantee distribution or a million views; those outcomes depend on audience-market fit, lane state and real Studio metrics after publication.

## Decision

1. After exact-final media QC passes, create a Codex review packet containing the final MP4 path, 0-10s contact sheet, full contact sheet, final ASR, exact timeline, loudness/spec/detector report, production contract and prior-round findings.
2. Run Codex non-interactively in read-only mode. Codex must inspect the repository evidence and return structured JSON containing:
   - `editorial_score` from 0 to 100;
   - category scores and evidence timestamps;
   - blocking defects;
   - at most three ranked actionable changes;
   - `verdict`: `revise`, `editorial_target_met`, or `blocked_external`.
3. Score on this fixed 100-point rubric:
   - hook clarity and stopping power, 25;
   - expectation/open-loop integrity, 10;
   - visual proof and information progression, 15;
   - mobile caption readability/sync, 10;
   - TTS/source-dialogue/sound mix, 15;
   - pacing/no-dull-moment execution, 10;
   - CTA/payoff/ending, 10;
   - technical/compliance evidence, 5.
4. `98` is an internal editorial target, not a forecast or guarantee of virality, views, Stayed to Watch or Swiped Away.
5. Apply only findings supported by exact timestamps/artifacts. Do not accept generic requests for “more effects,” unsupported factual escalation, new paid generation, format invention or changes that violate accepted ADRs.
6. After each accepted change: regenerate affected assets, rerender the exact final MP4, repeat full media QC, rebuild the packet and request a fresh Codex review. Never rescore a stale artifact.
7. Continue until `editorial_score >= 98`, or stop with `blocked_external` when the remaining gap requires unavailable human listening/naive-viewer evidence, commercial rights, paid approval, new source footage or real post-publish metrics.
8. Keep the loop bounded to five full rerender rounds per material revision. If round five is still below 98 without an external blocker, record diminishing returns, conduct expert/case-study web research, change one strategy rather than layering more polish, and start a new material revision.
9. A score of 98 never overrides the Hook Gate, Transformative Gate, source/voice rights, lane eligibility or 48-hour metrics rule.

## Consequences

- Every handoff includes independent, timestamped review evidence rather than self-scoring alone.
- The review loop improves the artifact while resisting decorative effect spam and fabricated confidence.
- Publication remains evidence- and rights-gated even when editorial execution scores highly.
- Real performance is evaluated only from mature Studio metrics after an eligible upload.
