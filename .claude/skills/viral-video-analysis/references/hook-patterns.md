# Hook Patterns — Taxonomy and How to Classify

Adapted from `~/.hermes/skills/video/value-added-editing-viral-shorts/references/source-channel-patterns.md`
(originally a one-off analysis of @theschoolofhardknocks). Cross-reference this
against `CONTEXT.md` → **Hook** and **Source Channel Pattern** before writing anything new —
those glossary entries are the current state of this taxonomy for this project and must be
extended, not duplicated.

## Current taxonomy (as of CONTEXT.md, cite before assuming these are final)

HEIT names 3 base types: **Context**, **Contrarian**, **Intrigue**. The 2026-07 hook-benchmark
study (`docs/research/hook-benchmarks-2026-07/REPORT.md`) found real viral hooks are usually a
**hybrid Context→Intrigue**, or a **Dare/Challenge** type (binary-outcome dare) that didn't fit
any of the 3 original types. A separate analysis (`source-channel-patterns.md`) identified 3
surface-level *patterns* that cut across these types:

1. **Money + Number** — concrete dollar amount + timeframe ("$58,380 IN 10 YEARS"). Highest
   consistency observed. Triggers envy/curiosity via specificity, not vagueness.
2. **Curiosity Gap ("THIS")** — capitalized deictic pronoun ("THIS IS THE REAL SECRET"),
   creates an information gap. Only works if the reveal doesn't disappoint.
3. **Contrarian Reveal** — subverts an expectation ("GOOD CULTURE ISN'T MADE IN THE GAME").

Do not treat these 3 as exhaustive. Every new analysis is a chance to find a 4th, 5th... pattern
— if one doesn't fit, propose a new pattern name and update `CONTEXT.md`'s **Source Channel
Pattern** entry rather than force-fitting it.

## What to extract per video

1. **Hook line, verbatim** (0-2s, exact words/on-screen text).
2. **Gap-not-resolved check** (CONTEXT.md → Hook): does the hook line alone reveal the full
   claim, or does it withhold something until 5-8s? A hook that states a complete, resolved
   fact fails this check even if it's punchy.
3. **Pattern classification**: which of the known patterns (Money+Number / Curiosity Gap /
   Contrarian Reveal / Dare-Challenge / hybrid) does it match? If none, name a new one.
4. **Structure timing**: hook duration, body duration, CTA/reflection duration, total — same
   breakdown as `source-channel-patterns.md`'s "Structure Observed" table.

## How to apply to a new source (5-step process, carried over unchanged)

1. Watch/scan top 6-10 Shorts from the viral channel (or just the 1-2 videos given).
2. Classify each hook into a pattern type (existing or new).
3. Map the pattern to which of this project's 3 niches (finance / health-VN / AI-education,
   ADR-0001/0004, ADR-0019, ADR-0020) it transfers to, and why.
4. Check the pattern against the Stage 0 Hook Gate checklist in `docs/WORKFLOW.md` — would a
   hook written in this pattern actually pass items 2-4 (gap-not-resolved, cause+effect
   co-naming, payoff-timing)? A pattern that only works because the source video is allowed to
   be misleading is not transferable.
5. Write the concrete "Suggested Next Video / AB-Test" recommendation (see
   `report-template.md`) — name the exact niche, hook line draft, and which existing AB
   variable dimension this exercises (Video Type, Hook Type, Value-Add Type — CONTEXT.md →
   **AB Variable**).
