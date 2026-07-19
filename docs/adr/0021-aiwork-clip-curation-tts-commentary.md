# ADR 0021: AI-Education Niche — Per-Video Clip Curation Override + TTS Commentary Layer

**Date:** 2026-07-10
**Status:** Accepted

## Context

ADR-0020 set the AI-education niche's default to zero-footage Curate+Repackage specifically to sidestep the Transformative Gate (ADR-0007) and the brand-sensitivity question of re-editing an official channel's own content, and left the Video Type undecided pending "a follow-up decision before the first script is produced."

For this niche's first video, the user chose a source that is itself Anthropic's own official Claude YouTube channel ("The capability curve", tP4MGcJ80Y0). Grilling that follow-up decision surfaced three choices, and the user's answers explicitly reopened ADR-0020's zero-footage default rather than resolving Video Type within it:

1. **Footage**: reuse real footage from the source (Clip Curation Edit, Video Type #7 / ADR-0007), not zero-footage repackage.
2. **Value-add emphasis**: Data Viz — an animated capability-curve/benchmark chart, matching the topic directly.
3. **Commentary**: a free/local synthesized voiceover (TTS) layered over the segment's original audio, in addition to captions — no prior project in this repo mixes TTS with original narration. `docs/production/ackman-ascii.md`'s Key Decision #2 explicitly chose "Original voice over TTS... avoids audio duplication bug" — i.e. the one prior attempt at this went the other way, on record as a caution, not a precedent to copy.

## Decision

1. **Clip Curation Edit is available to the AI-education niche on a per-video basis** when the user explicitly chooses to reconsider the zero-footage default for that video's source — this is an acknowledged, per-video override, not a silent or blanket reversal. ADR-0020's zero-footage default remains the fallback for any other AI-ed video where this isn't explicitly revisited.
2. **Free/local TTS is adopted as this repo's mechanism for a spoken (not just text-overlay) commentary layer**, satisfying ADR-0007 rule 1 more literally than captions alone. Engine: macOS `say` (primary, zero new dependencies, offline) with `edge-tts` as a fallback if voice quality reads too robotic for a "no hype, professional" brand tone (`output/projects/aiwork/final/brand_assets.txt`) — swapping engines only changes the TTS generation step, not the mixing architecture below.
5. **Brand-sensitivity risk is flagged, not resolved**: reusing Anthropic's own official-channel footage is exactly the risk ADR-0020 cited as a reason to default to zero-footage for this niche. Passing the Transformative Gate is a legal/compliance question; brand/PR relationship risk is a separate axis that gate compliance doesn't eliminate. Mitigation adopted: the video description will visibly credit "Source: Claude YouTube channel" — a deliberate, explicit exception to ADR-0007's usual no-attribution stance, specifically for official/branded sources where visible credit lowers relationship risk without changing copyright posture either way.

## Consequences

- `pipeline/aiwork/render_aiwork_v1.py` is the first render script for this niche, and the first in the repo to mix a synthesized voice with original source audio.
- `pipeline/tools/tts_commentary_aiwork.py` becomes a reusable template for any future project wanting a spoken (not text-only) commentary layer.
- If the TTS/original-audio mix proves unreliable or sounds bad in practice (echo, phase-doubling, or anything resembling the `ackman-ascii.md` "audio duplication bug"), the fallback is to drop the TTS layer and rely on text-overlay commentary only — still fully Transformative-Gate-compliant via ADR-0007 rule 1's "voiceover OR text overlay" wording, and the proven pattern `pipeline/bacsihai/` and `pipeline/hardknocks/` already use.
- Does not change ADR-0020's Consequences for finance or health niches, and does not require retrofitting bacsihai/hardknocks with a commentary track — their existing text-overlay-only commentary already satisfies ADR-0007 rule 1.
- **Open question, not resolved here**: whether reusing official/branded-channel footage should become a repo-wide, case-by-case-only policy or something gated more strictly niche-wide — escalate (Ask-First) if a second official-channel source is proposed for this or another niche.

## Addendum (2026-07-10, from `docs/production/aiwork-v1-capability-curve.md`'s Post-Production Retro)

The commentary span should stay a generic framing/authenticity line only when the source's own opening line at the chosen `SRC_START` is *not* already a strong hook on its own. In v1, the source's own first line ("That's an over 25% jump...") was itself a strong Money+Number hook, and the ~2s TTS preamble ("Straight from Anthropic's own stage.") before it pushed that payoff line past the Hook Gate's 0-2s window rather than reinforcing it. Before choosing to prepend a TTS commentary line ahead of the segment's own audio, check whether the segment's own first spoken line already lands as a hook by itself - if it does, prefer a commentary line placed *after* it (or drop the spoken commentary and rely on text-overlay commentary only, still ADR-0007-compliant) rather than delaying it.

## Related

- ADR 0007: Clip Curation Edit (Transformative Gate)
- ADR 0013: Contiguous VO Pipeline (immutability clarified here)
- ADR 0017: Hook-Window Source Selection
- ADR 0018: Hook Caption Sync and Cadence
- ADR 0020: Niche — AI Education (default this ADR overrides per-video, not blanket)
- `docs/production/ackman-ascii.md`: prior TTS-vs-original-voice decision, cited as caution
