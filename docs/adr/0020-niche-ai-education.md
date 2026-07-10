# ADR 0020: Third Niche — AI Education (English)

**Date:** 2026-07-10
**Status:** Accepted

## Context

ADR-0019 documented two niches running in parallel (finance/English, health/Vietnamese) and explicitly said: "Adding a third niche/vertical, or changing which niches are active, still requires the Ask-First gate — this ADR documents the two verticals already running, it does not pre-approve future ones." `AGENTS.md`'s Boundaries → Ask First section mirrors this same gate.

The user requested a third channel: "tôi muốn làm thêm 1 kênh youtube về AI nữa giúp mọi người học và làm việc với AI tốt hơn" (I want to make one more YouTube channel about AI to help people learn and work with AI better), asking for the channel's title, description, and image/banner generation prompts.

Grilling this request surfaced two decisions that needed pinning down before drafting anything:

1. **Audience**: the user's first-pass framing ("help everyone learn and work with AI better") was broad enough to mean total beginners. But the style references the user named for the video format — `@claude`, `@mattpocockuk` (Matt Pocock), `@anthropic-ai` — skew toward practitioners already using AI tools, not absolute beginners. The user confirmed narrowing the audience to match: professionals/knowledge workers who already use ChatGPT/Claude and want to get meaningfully better at it.
2. **Format inspiration**: naming `@claude` and `@anthropic-ai` (Anthropic's own official channels) as references raised a question the existing Video Type framework doesn't have to deal with for the other two niches — does "follow their format" mean re-curating their actual footage (Clip Curation Edit, subject to the Transformative Gate) or copying their style/structure only, producing 100% original content (Curate+Repackage, the finance vertical's model)? The user confirmed: style/structure only, zero footage reuse. This avoids both the Transformative Gate machinery and the brand-sensitivity question of re-editing a company's own official channels.

## Decision

This project now runs **three niches in parallel**, all subject to the same production pipeline, video specs, and Known Pitfalls in `AGENTS.md`:

1. **Finance/money-making, English** (ADR-0001, ADR-0004).
2. **Health/longevity, Vietnamese** — Source Channel "Bác sĩ Hải" (ADR-0019).
3. **AI education, English** — audience is professionals/knowledge workers already using AI tools who want to get better at it, not absolute beginners and not developers specifically. Content strategy is Curate+Repackage (ADR-0005), same as the finance vertical: zero footage reuse, 100% original animation. Style/structure references (practical, no-fluff, demo-driven presentation) are `@claude`, `@mattpocockuk`, `@anthropic-ai` — these inform tone and pacing, not source footage. Which of the 6 zero-footage Video Types (Kinetic Typography, Data Viz, HTML/CSS Motion, Whiteboard Sketch, Meme/Notification, or a Kitty-Explain-style mascot) will render this niche is **left unresolved by this ADR** — a follow-up decision before the first script is produced.

Channel branding drafted at `output/projects/aiwork/final/brand_assets.txt`: name "Working With AI" (alt "AI, Actually"), description, avatar prompt, and banner prompt — following the same template `output/projects/bacsihai/final/brand_assets.txt` established, with English field labels matching this niche's output language.

Adding a fourth niche/vertical still requires the Ask-First gate — this ADR documents the three verticals now running, it does not pre-approve future ones.

## Consequences

- `AGENTS.md`'s top Niche/Format framing (currently naming two verticals) needs to name all three (fixed in this same change), and its Boundaries → Ask First bullet needs to read "a fourth niche" instead of "a third niche" (fixed in this same change).
- `CONTEXT.md`'s **Source Channel** glossary entry (previously "cho MỘT trong 2 niche song song") needs to say 3, and note that a Source Channel for the AI-education niche can be a practitioner/product channel (e.g. `@mattpocockuk`, `@anthropic-ai`) used for topic/style research, not only a "viral how-to" channel in the sense the finance and health examples were (fixed in this same change).
- The MAB/optimization-loop design (ADR-0009) was already flagged in ADR-0019 as single-stream-scoped for two niches; a third parallel niche makes per-niche variant-selection and reward-tracking scoping more pressing, still not resolved here.
- Video Type selection for this niche is unresolved — no `pipeline/aiwork/` render scripts exist yet, since there's nothing to script until a Video Type is chosen.
- `data/tracked_videos.csv` and `data/mab_state.json` remain scoped to finance only (per ADR-0019); this ADR does not change that.

## How this connects to existing docs

- `AGENTS.md` → top Niche/Format lines and Boundaries → Ask First bullet updated to name all three verticals.
- `CONTEXT.md` → **Source Channel** glossary entry updated.
- `docs/adr/0001-niche-finance-money-making.md`, `docs/adr/0004-*` (English-only), and `docs/adr/0019-multi-niche-ab-testing.md` remain accurate for niches 1 and 2; this ADR adds the third alongside them rather than superseding any of them.
- `output/projects/aiwork/final/brand_assets.txt` → channel branding assets for this niche.
