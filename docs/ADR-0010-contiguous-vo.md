# ADR 0010: Contiguous VO Pipeline (Architectural Pattern)

## Status
Approved

## Context
Previous pipeline attempts (v1-v3) suffered from "VO stutter" where Pexels b-roll insertions physically broke the source audio timeline, causing silent gaps and disjointed narration.

## Decision
Adopt a "Contiguous VO Pipeline" architecture:
1. Each short video MUST be a single, non-split contiguous segment from the source.
2. Source audio timeline remains completely immutable.
3. Pexels clips are composited via `filter_complex` as full-screen overlays ONLY.
4. If a segment exceeds 60s, it is trimmed to fit; if under 45s, a different source range must be selected.

## Consequences
- VO is now perfectly continuous (no gaps).
- Pexels b-roll can be freely placed at natural inflection points.
- Production time is reduced (no need to align dozens of small clips).

## Glossary
- Contiguous VO: Audio timeline derived from a single uncut range of the source video.
- Visual Overlay: B-roll footage composited using `overlay` filter, NOT `concat`.
