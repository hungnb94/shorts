# ADR 0038: Event-Ledger SFX Library and Rights Gate

**Date:** 2026-07-30  
**Status:** Accepted

## Context

The user supplied one Vietnamese instructional video about basic sound-effect design and the MyInstants Viet Nam soundboard index, asking that the lessons become a stronger SFX strategy, workflow and reusable skill system.

The instructional source demonstrates a useful sequence: determine tone/mood, mark desired actions on the timeline, divide sounds into real/diegetic and designed/non-literal categories, derive search keywords from the sound's function, and align the selected effect to the action. It explicitly introduces `whoosh`, `drone`, `ambience`, `whip`, `hit`, `drop`, `sub-drop`, `impact`, `riser` and `pop`. This is operational evidence from one creator, not a controlled retention study.

The project already requires an early SFX, purpose-bound transition sound and event-bound audio under ADR-0034/0036. However, the workflow does not require a mood lock, event ledger, keyword trail, asset manifest, license proof or full-mix semantic review. Current HardKnocks renderers duplicate procedural `cash_chime` and `whoosh` generation and reuse the same sound identity for several unrelated story jobs.

MyInstants is valuable as a vocabulary and cultural-reference surface, but its Terms grant limited personal, noncommercial site access and its DMCA policy confirms that user-uploaded material may be removed after infringement claims. A sound's presence on MyInstants does not establish commercial publication rights.

Full evidence and strategy: `docs/research/sfx-system-2026-07-30/REPORT.md`.

## Decision

1. Add a blocking **Sonic Intent** before SFX search. Every new Short records its vertical, tone, emotional arc, default palette, intentionally excluded sound families and the opening/payoff sound jobs.
2. Create an **SFX Event Ledger** from the real EDL before downloading or generating effects. Every row records final timestamp/pre-lap, visible or implied trigger, story job, family, emotion/weight, functional search query, asset ID, gain, rights status and post-mix verdict.
3. Use four production families:
   - `diegetic_foley`;
   - `motion_transition`;
   - `state_emphasis`;
   - `tension_context`.
   `meme_voice_reference` is a quarantine family, not a default production palette.
4. Treat `ambience` as contextual information and `drone`/`riser` as sustained emotional-state tools. They may continue across a state when justified, but they do not satisfy event-SFX requirements and must not become constant decorative effect spam.
5. Search by semantic and physical attributes rather than generic filenames. A query should normally identify role plus relevant speed, weight, material, space, distance or intensity.
6. Establish this rights-aware source ladder:
   - original field recording/self-recorded foley;
   - project-generated procedural sound;
   - YouTube Audio Library with saved metadata;
   - individually verified Freesound CC0 or CC-BY assets, preserving attribution where required;
   - separately licensed commercial libraries after explicit spend approval;
   - MyInstants/unknown user uploads as `reference_only` unless independent commercial rights are documented.
7. Every production asset must exist in a shared manifest with stable ID, role/family, origin, source page, license name/link or generation recipe, attribution, checksum, duration, sample rate, channels, approval status and rights status. Downloadable does not mean cleared.
8. Layer sounds only when each layer has a distinct semantic job: physical anchor, perceptual sweetener or context. Duplicate loudness without a new job is removed.
9. Audition and approve cues inside the exact dialogue + music mix. Solo audition is useful for defects but cannot prove semantic fit, speech intelligibility or fatigue.
10. Final media QC verifies the cue against the ledger, critical-word intelligibility, deliberate pre-lap, absence of delayed-track rebasing, encoded true peak/loudness, repeated-motif fatigue and manifest rights. Filter-graph intent does not prove final-artifact presence.
11. Sound design remains baseline quality in every treatment. Valid tests compare two high-quality palettes or one cue-family/timing treatment while freezing story, visuals, captions, proof order, runtime and packaging. A deliberately soundless control remains forbidden.
12. Exact SFX count, density, gain and offset are hypotheses, not universal rules from one reference video. No cue quota is introduced.
13. Completed media is not revised retroactively. The new gate applies to the next new Short or explicitly requested material revision.

## Considered options

### Download popular MyInstants buttons directly into the production pack

Rejected. Popularity and download access do not establish commercial rights. The Viet Nam index also contains voice/meme sounds that conflict with the English-language and credibility requirements of the current verticals.

### Keep the existing per-renderer generated whoosh and cash chime pattern

Rejected as the long-term system. It is rights-safe but duplicates code, overloads one sound with unrelated meanings and prevents vertical-specific sonic identity. Existing completed renderers remain untouched; migration begins with a future real production.

### Add a fixed SFX every N seconds

Rejected. It would reproduce the same quota-gaming problem ADR-0036 prevents for visual changes, reward decorative spam and mask dialogue. Cues must follow story events and state transitions.

### Treat every sustained sound as an event SFX

Rejected. Ambience, drone and score can carry context/emotion across a state, while event SFX punctuate a trigger. Conflating them would allow a constant bed to satisfy the event-bound gate.

## Consequences

- Pre-production gains a small ledger step but asset search becomes reusable and auditable.
- MyInstants becomes a reference/discovery surface rather than an unverified commercial source.
- Future renderers can converge on one rights-aware library without retroactively refactoring completed one-off scripts.
- Vertical-specific sound palettes reduce credibility mismatch and repeated meme fatigue.
- Production documents must preserve exact cue timing and provenance so retention postmortems can map outcomes to the smallest controlled audio layer.
- The project can build a proprietary sonic identity from recorded/procedural assets instead of competing on the same public meme buttons.
