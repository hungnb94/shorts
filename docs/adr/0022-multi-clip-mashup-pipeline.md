# ADR 0022: Multi-Clip Mashup Pipeline (second Clip Curation Edit sub-format)

**Date:** 2026-07-10
**Status:** Accepted

## Context

ADR-0007 established Clip Curation Edit (Video Type #7) with a Transformative Gate whose item 3 reads "cut <=50% source duration, moi clip <15s" (each clip <15s) - wording that already presupposes multiple clips are the normal case, not an exception.

ADR-0013 later introduced "Contiguous VO Pipeline": one single, non-split contiguous segment per video, audio timeline completely immutable. Its own Context section is explicit about why: "Previous pipeline attempts (v1-v3) suffered from 'VO stutter' where Pexels b-roll insertions physically broke the source audio timeline, causing silent gaps and disjointed narration." This was a fix for one specific failure mode (silent b-roll insertions splitting a single narration track), not a blanket ban on ever concatenating multiple source-derived clips.

`pipeline/hardknocks/render_hardknocks_v1.py` (first hardknocks video, uploaded as `dHDpDXSIAkA`) already concatenates 6 discontiguous source ranges via the ffmpeg concat demuxer, each independently encoded then hard-cut together - no crossfade, no b-roll insertion, no silent gaps. `docs/production/bacsihai-v5-lao-dong-tay.md` and `docs/WORKFLOW.md` both flagged this as "appears to violate ADR-0013" and left it as a known, unresolved inconsistency rather than reconciling it.

Grilling a v2 rebuild of `pipeline/aiwork/render_aiwork_v1.py` (user feedback: the hook was weak, and the video should cut together multiple parts of the 905s source rather than staying inside one 45-60s block) surfaced the same pattern as a deliberate choice, not an accident. This is the moment to name what hardknocks was already doing, rather than let a second video repeat an undocumented pattern.

## Decision

Clip Curation Edit (ADR-0007) has two sub-formats, chosen per video based on whether the source material's best moments are reachable within one 45-60s window or are scattered across a much longer source:

1. **Contiguous VO** (ADR-0013, unchanged): one single, non-split segment, 45-60s, audio timeline completely immutable (no cuts, no splices - gain-only automation such as ducking is permitted per ADR-0021's clarification). Use when the strongest hook + payoff already sit inside one reachable 45-60s window in the source (bacsihai, dangote).
2. **Multi-Clip Mashup** (new, this ADR): several independently-extracted, non-contiguous source ranges, each internally contiguous and each <15s (ADR-0007 item 3), stitched together with the **ffmpeg concat demuxer** (`-f concat -safe 0 -c copy`). Boundaries are **hard cuts** - no crossfade, no forced whoosh/sound-design at the join, matching what `render_hardknocks_v1.py` already does. Use when the strongest moments (hook, payoff, concrete example, closing beat) are spread across a source too long for any single 45-60s window to reach all of them.
3. Within a Multi-Clip Mashup, each individual clip may itself be further split at internal pause points (see the pause-trimming Retention Technique, logged in AGENTS.md) - these sub-cuts follow the same hard-cut rule as the macro clip boundaries. All resulting pieces must still satisfy the same encode-parameter uniformity the concat demuxer's `-c copy` requires (matching codec/profile/pix_fmt/timebase across every piece, not just matching CRF).
4. `render_hardknocks_v1.py` is retroactively classified as the first (undocumented-until-now) instance of Multi-Clip Mashup, not a standing ADR-0013 violation. `docs/WORKFLOW.md`'s "Nam ngoai scope" note about this is removed/reclassified accordingly (see that file's own diff).
5. Total duration target for Multi-Clip Mashup stays the same 45-60s window ADR-0013 uses - this ADR does not relax that floor/ceiling, only how the segment is assembled.

## Consequences

- `pipeline/aiwork/render_aiwork_v2.py` becomes the first video built under this ADR with the sub-format named explicitly at build time (rather than discovered after the fact, as with hardknocks).
- Choosing Multi-Clip Mashup means giving up ADR-0013's audio-continuity guarantee inside individual hard-cut boundaries - accept the risk of an audible click at a cut (not at a zero-crossing) as a known, low-severity tradeoff; revisit with a short crossfade only if a specific cut is audibly bad on review, not preemptively for every cut.
- Does not change ADR-0013's Consequences for videos that use Contiguous VO - that sub-format, and its "audio immutable" guarantee, is unaffected.
- Does not retroactively require re-editing `render_hardknocks_v1.py` - it already satisfies this ADR's rules as written; only its documentation status changes (violation -> named sub-format).
- Any future video choosing this sub-format should state so explicitly in its own production doc's "Why This Segment" section, the same way Contiguous VO videos cite ADR-0013.

## Addendum (2026-07-11, from `docs/production/aiwork-v2-capability-curve.md`'s Post-Production Retro)

Item 3 above assumed an internal split point (pause-trim or otherwise) always lands in silence. In practice a clip's internal shot change can land mid-word instead — `render_aiwork_v2.py`'s HOOK clip cuts from a tight portrait shot to the wide stage shot at approximately the midpoint of the word "than", not at any pause. Splitting that into two concat pieces would guillotine the word's audio the same way a mistimed pause-trim cut would.

**When an internal split point does not land at a word/pause boundary, do not force a concat-piece split there.** Instead keep that span as ONE continuous extract and vary the relevant filter parameter over time within it — e.g. a `crop` filter's `x` offset via `if(lt(t,SWITCH_T),A,B)`, where `t` is confirmed to run relative to that extract's own start when `-ss` precedes `-i` (verified with a `drawtext=text='%{pts}'` test render). This preserves full audio continuity across the shot change; only the visual crop changes. Use the nearest word/pause boundary as the piece-split point only when one exists close enough to the true visual cut to not look wrong (`render_aiwork_v2.py`'s CLOSE clip: cut chosen at a word's end, ~0.2s after the true visual transition, accepted as imperceptible).

## Related

- ADR 0007: Clip Curation Edit (Transformative Gate, incl. the "<15s per clip" rule this sub-format satisfies literally)
- ADR 0013: Contiguous VO Pipeline (the sibling sub-format; its "VO stutter" context is specific to silent b-roll insertion, not multi-clip concat)
- ADR 0021: AI-Education TTS Commentary (its audio-immutability clarification is specific to Contiguous VO; does not apply to Multi-Clip Mashup, which has no single immutable track to begin with)
- `pipeline/hardknocks/render_hardknocks_v1.py`: first (retroactively classified) instance
- `docs/production/aiwork-v2-capability-curve.md`: first video to declare this sub-format at build time
