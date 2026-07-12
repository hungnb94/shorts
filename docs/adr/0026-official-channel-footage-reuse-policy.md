# ADR 0026: AI-Education Niche — Official-Channel Footage Reuse, Standing Policy

**Date:** 2026-07-12
**Status:** Accepted

## Context

ADR-0021 (aiwork_v1/v2, both sourced from `tP4MGcJ80Y0`, "The Capability Curve") flagged an open question rather than resolving it:

> Open question, not resolved here: whether reusing official/branded-channel footage should become a repo-wide, case-by-case-only policy or something gated more strictly niche-wide — escalate (Ask-First) if a second official-channel source is proposed for this or another niche.

For aiwork_v3, the user proposed a second source from the same official Claude/Anthropic YouTube channel: `mWvtOHlZM-I` ("Tool, skill, or subagent? Decomposing an agent that outgrew its prompt"). This is exactly the trigger ADR-0021 named. A grilling session (`/grill-with-docs`) surfaced the question directly and the user chose to resolve the policy now rather than defer it again.

## Decision

**Official-channel footage reuse is now a standing, case-by-case-allowed policy for the AI-education niche** — no per-video Ask-First escalation is required going forward, provided both of ADR-0021's existing mitigations continue to apply on every video that does it:

1. Passes the ADR-0007 Transformative Gate (commentary track, ≥2 value-adds, ≤50% source duration / each clip <15s).
2. Visible credit in the video description ("Source: Claude YouTube channel" or equivalent), per ADR-0021's brand-sensitivity mitigation.

The user's reasoning, recorded here since it's the "why" a future reader would otherwise have to reconstruct: after 2/2 videos made for this niche both ended up choosing official-channel footage reuse when asked, this is evidently the niche's real working pattern, not a rare exception — re-litigating the same escalation on every single video is friction without added safety, since the actual risk (brand/PR relationship risk, not copyright) is already mitigated by the visible-credit requirement and doesn't change video to video.

This does not lower the bar in any other way: the Transformative Gate and visible-credit requirements are unchanged, and this policy is scoped to the AI-education niche only — it says nothing about finance or health, and does not pre-approve reusing footage from a *non-official* channel (that remains governed by the existing Clip Curation Edit rules, ADR-0007/0013/0022, with no special case).

## Consequences

- Future aiwork videos may reuse official-channel footage without a fresh grilling session on the footage-policy question specifically — grilling sessions for those videos can move directly to format/audience-fit/hook decisions.
- If a genuinely new risk shows up in practice (e.g., a takedown request, a visible negative reaction from Anthropic's own channel/team), this ADR should be revisited — it resolves the policy based on the evidence available as of 2026-07-12 (zero adverse reactions reported for aiwork_v1/v2 so far, though v2 was only uploaded 2026-07-11 and is still inside its 48h metrics window), not a permanent guarantee.
- Does not change ADR-0021's audio-mixing pattern, the Transformative Gate, or ADR-0020's audience/language/niche scope in any other respect.

## Related

- ADR 0020: Niche — AI Education (original zero-footage default)
- ADR 0021: AI-Education Niche — Per-Video Clip Curation Override + TTS Commentary Layer (the open question this ADR resolves)
- ADR 0007: Clip Curation Edit (Transformative Gate)
- ADR 0022: Multi-Clip Mashup Pipeline
