# ADR 0034: Guide-Derived Shorts Craft and Publishing Verification Baseline

**Date:** 2026-07-19  
**Status:** Accepted

## Context

The user supplied the living `r/shortsAlgorithm` guide built from one creator's hands-on results, including a first Short reported at 20M+ views. The guide is useful operational evidence, but it is not a controlled causal study. During grilling, the user explicitly chose to adopt nearly all craft and publishing recommendations as hard project rules rather than leave them as optional hypotheses.

YouTube's current official documentation allows square or vertical Shorts up to three minutes. The prior repository claim that a Short over 60 seconds becomes long-form is therefore obsolete. The project nevertheless chooses a narrower 50–75 second production range to implement the supplied retention strategy and preserve a bounded format.

## Decision

Apply the following baseline to every newly produced Short. Completed historical videos are not revised retroactively.

### Content Craft Gate

1. Runtime is 50–75 seconds, 9:16 at 1080x1920, MP4 H.264 with an audio stream.
2. The 0–3 second hook combines visual surprise with a clear narrative promise. Existing stricter Hook-Window, caption-sync, face/action, gap, payoff and cadence rules still apply.
3. A deliberate sound effect lands within the first second. An arrow, pointer or equivalent animated annotation identifies the focal element when the focal target is not immediately unambiguous.
4. Captions are non-negotiable:
   - 2–5 words per synchronized burst;
   - one key word per burst animated and visually emphasized;
   - caption center normally sits at 55–65% of frame height, moving only when manual review confirms it covers a face or proof object;
   - English verticals use Komika Axis; the Vietnamese health vertical uses Bangers, whose font artifact was verified to advertise Vietnamese glyph coverage and is distributed under the SIL OFL;
   - ffmpeg caption dimensions are calibrated visually to the supplied CapCut `size 16 / stroke 60` reference rather than copying those incompatible numeric units literally.
5. Image entrances/exits and transitions are purposeful and receive matching sound design; generic transition spam does not satisfy the gate.
6. A custom, on-brand `Mid-Roll Triple CTA` starts at t=38–42s and explicitly asks for Like, Subscribe and Comment. Generic stock CTA templates fail.
7. A moving watermark remains visible but non-obstructive and changes position over the timeline to resist simple crops.
8. Before full production approval, a naive viewer who was not involved in the edit watches the 0–3 second rough hook without prompting and can state the open question or promise that makes them continue. If they need the creator's explanation, the hook fails.
9. Final review triple-checks hook, CTA timing, caption timing/readability, watermark movement and all upload wiring before publication.

### Publishing Metadata Gate

1. Title is at most 30 user-visible characters including spaces and emoji, uses Title Case in every vertical, and contains exactly two tasteful emoji.
2. Description line 1 mirrors the title. It may contain at most one additional descriptive sentence, followed by exactly three visible hashtags; `#shorts` is mandatory and hashtag soup is forbidden.
3. YouTube Studio Tags contains exactly three precise niche-specific tags in the audience's language. Misleading trends are forbidden.
4. Audience is set to `Not made for kids` because the three current verticals target general/adult audiences. If a future Short is actually directed at children, legal audience classification overrides this project default.
5. Video language, location and accurate category are set explicitly.
6. The approved upload-details template is reused; last-minute metadata improvisation in Studio is forbidden.
7. Every Short is added to its vertical's master playlist.
8. Related Video wiring is set after upload. When a winner exists, the winner is updated to point viewers to the new Short; the first upload on a channel is the only bootstrap exception.

### Strategy Gate

1. Until a Destination Channel reaches 500k subscribers, Shorts take priority over long-form production.
2. Niche and format choices must come from reverse-engineering outlier channels and imitating their narrative/packaging structure, never copying their specific content.
3. The first upload on every new Destination Channel receives the same full production gate as any mature-channel release; it is not treated as a disposable test.

## Consequences

- 61–75 second files are intentionally allowed and must no longer fail spec verification.
- Existing renderers may need timing changes, caption font artifacts, watermark motion and a CTA beat before their next new production use.
- The fixed 38–42 second CTA occupies different relative positions across the duration range; this is an explicit user choice rather than a normalized timing rule.
- Title and description constraints are substantially tighter than YouTube's platform limits.
- Font files and their licenses become production assets and must be versioned with the pipeline rather than assumed to exist on the host.
