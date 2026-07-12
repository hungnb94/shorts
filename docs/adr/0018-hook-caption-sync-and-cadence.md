# ADR 0018: Hook Caption Sync and Cadence — Extending the Hook-Window Rule

**Date:** 2026-07-10
**Status:** Accepted

## Context

ADR-0017 established that frame t=0 of a hook must show a human face/action, not a static title card. That fixed the single worst failure mode (`YQTWHqTS1e8`, 8.6% stayed). But we only had one GOOD data point (Dangote, 50% stayed) to generalize from, and no evidence on what happens *inside* a compliant hook window beyond "frame 0 has a face."

We collected frame-level (26 frames/video, t=0-5s @ 0.2s), transcript, and top-100-comment evidence for 6 independently viral Shorts (Mark Tilbury x3, School of Hard Knocks x3 — see `docs/research/hook-benchmarks-2026-07/REPORT.md`) to check whether additional hard rules should exist beyond "face at t=0."

## Evidence

Two patterns held across all 6 videos that are NOT currently encoded as rules anywhere in this repo:

1. **Caption sync**: every video had a burned-in caption already on screen at t=0.0-0.2s, updating in sync with the spoken words (not full sentences at a time — short 2-5 word bursts), with exactly one emotionally/numerically loaded word per burst rendered in a highlight color (yellow in all 6 cases). Example (`Ay_hu2hI0qE`): "THIS IS WHAT'S" → "STOPPING YOU" → "BECOMING RICH..." (RICH in yellow) → "IMAGINE THIS IS YOU," (YOU in yellow), each burst landing within ~0.4-1s of the last.
2. **Cadence**: 5/6 videos had a visual change (hard cut, new caption burst, camera move, prop entering frame) at least every 0.6-1.5s within the first 5 seconds — noticeably tighter than the existing "2-Second Rule" (ADR-0016, visual event every 2-3s). The one exception (`Ay_hu2hI0qE`) held a single demo shot for ~3.6s, but that shot contained continuous motion (a toy train physically rolling), not a static frame.

Both patterns are absent from `CONTEXT.md`'s Hook/Hook-Window Rule entries and from `AGENTS.md`'s "Hook timing is non-negotiable" pitfall — those only govern frame-0 content and overall hook duration (0-2s, 15-25 words), not what happens to captions/cuts *inside* that window.

## Decision

Extend the Hook-Window Rule with two additional gating checks for the 0-5s hook region, on top of the existing frame-0 face requirement:

1. **Caption must be burned in and visible by t=0.2s** (not delayed to t=1-2s as headroom for a "clean" opening shot), updating at least once every ~1-2s, with one keyword per burst visually emphasized (color/weight distinct from the rest).
2. **At least one visual change (cut, zoom, new overlay element, or continuous on-screen motion) every 1-2s within the hook window** — tighter than the general-purpose 2-3s cadence in ADR-0016, specifically for the 0-5s hook region.

These are stricter than, not a replacement for, ADR-0016 and ADR-0017 — they apply narrowly to the hook window.

## Consequences

- Caption-generation timing in the render pipeline needs to target sub-1s burst granularity for the hook line specifically, not just render the full hook sentence as one caption block. This is a real cost: Vietnamese TTS narration paces differently from the rapid-fire English interview speech in our 6 samples, so burst timing must be derived from actual TTS word-timing output, not copied wholesale from the English benchmarks.
- Trade-off acknowledged: faster caption cycling helps retention per this evidence, but could hurt legibility if applied blindly to a slower-paced narration style. Script-writers/render pipeline should verify readability (not just retention theory) when tuning burst duration for Bác sĩ Hải / Giảm Cân Healthy content.
- Does not apply the "Ambush Interview" street-confrontation format itself (3/6 videos, all School of Hard Knocks) — that is a Clip Curation Edit-specific archetype, not a universal rule. Only the caption-sync and cadence findings are treated as universal here.

## How this connects to existing docs

- `CONTEXT.md` → **Hook Caption Sync** (new glossary term) and **Hook** (updated to describe hooks as a 2-stage setup→reveal arc, not a single static line type).
- `AGENTS.md` → "Hook timing is non-negotiable" pitfall extended with the caption-sync and cadence checklist.
- `docs/research/hook-benchmarks-2026-07/REPORT.md` → full per-video evidence and cross-video synthesis this ADR is based on.

## Open question (agent judgment, user did not confirm)

The exact burst-duration threshold (we observed 0.4-1.5s across 6 English-language samples) has not been validated against Vietnamese TTS pacing. Recommend A/B testing burst duration on the next Bác sĩ Hải batch rather than assuming the English benchmark timing transfers directly.

## Addendum (2026-07-12): multi-color-by-keyword-type scheme, and a size dimension beyond the original evidence

`hardknocks_v3`'s self-authored dialogue captions (ADR-0024) initially rendered every burst in one flat color, missing this ADR's "one keyword per burst visually emphasized" requirement entirely — caught by the user on review, not by any automated check (see `docs/production/hardknocks-v3-believe-in-god.md` Post-Production Retro for the full account).

Fixed, and extended per the user's explicit request in that grilling session:

- Regular (non-keyword) burst text: yellow @ 68px (up from an un-emphasized 52px white). The original 6-video evidence above didn't specify a base color, only that the keyword be "distinct from the rest" — yellow-as-base plus a distinct keyword color still satisfies that.
- Keyword text gets **both** a color change **and** a +10% size bump (75px vs 68px base). The size dimension is a **new extension beyond what the benchmark evidence supports** — the 6 videos in `docs/research/hook-benchmarks-2026-07/REPORT.md` only documented color emphasis, never size. Treat size-emphasis like the burst-duration open question above: adopted on the user's judgment, not yet validated against retention data.
- Rather than one project-wide highlight color, this introduces **2 keyword categories with distinct colors, chosen per-video from that video's own transcript vocabulary** — not a fixed global word list. `hardknocks_v3` used white for core-topic vocabulary (God, faith, wrestle/wrestling, godly) and `0xFF3B1A` (red-orange) for personal/emotional-payoff vocabulary (deeper, growing, confidence, purpose, plan, loved, favor). A future video should define its own 2 categories from its own content rather than reusing this exact word list.
- User decision: record this immediately as an accepted addendum (project-wide going forward), not scope it to `hardknocks_v3` only pending metrics — unlike the "neutral tone" decision in the same production, which the user explicitly scoped to one video.

**Implementation**: `drawtext` can't mix colors/sizes within a single filter call, so each caption burst is split into runs by color/size class, and one `drawtext` filter is emitted per run, pixel-positioned with Pillow (`ImageFont.getlength()` for width, `getmetrics()` for baseline alignment across mixed sizes) so multi-run lines stay visually contiguous and centered on one baseline. See `dialogue_burst_filters()` in `pipeline/hardknocks/render_hardknocks_v3.py`.
