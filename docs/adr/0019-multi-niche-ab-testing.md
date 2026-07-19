# ADR 0019: Multi-Niche AB Testing (Finance/English + Health/Vietnamese)

> **Partial supersession (2026-07-19):** ADR-0034 replaces this ADR's `≤60s` shared spec with `50-75s` for new production. The multi-niche and language-scoping decisions remain accepted.

**Date:** 2026-07-10
**Status:** Accepted

## Context

AGENTS.md's top section declares a single niche ("Finance/money-making") and a single language ("English only", ADR-0004), and lists "Changing niche away from finance/money-making" under Boundaries → Ask First.

In practice, this has not been true since at least `pipeline/bacsihai/` v1 (health/weight-loss content from the Vietnamese-language channel "Bác sĩ Hải", 100% Vietnamese output — title, VO, captions, description). Four bacsihai videos (v1-v4) were produced under this "second vertical" before it was ever written down. When asked to produce a new Short from another Bác sĩ Hải video (`AGBrXy-2SxI`), continuing the niche/language mismatch was flagged per the Ask-First boundary, and the user confirmed:

> "tôi đang AB test không chỉ kênh kinh doanh, tài chính mà còn kênh sức khỏe. Càng nhiều dữ liệu thì càng nhanh thành công."
> (I'm AB-testing not just business/finance channels but also health channels. The more data, the faster the path to success.)

This is a deliberate strategy, not an oversight: running finance/English and health/Vietnamese verticals in parallel to maximize the rate of data collection across the optimization loop described in ADR-0009.

## Decision

This project runs **two niches in parallel**, both subject to the same production pipeline, video specs, and Known Pitfalls in AGENTS.md:

1. **Finance/money-making, English** (ADR-0001, ADR-0004) — the originally-documented vertical (giannis, dangote, hardknocks, and the finance `scripts/*.md` drafts).
2. **Health/longevity, Vietnamese** — Source Channel: "Bác sĩ Hải" (`pipeline/bacsihai/`). Output is 100% Vietnamese (title, VO, captions, description) since the source, audience, and channel identity are Vietnamese; this is not a translation of the finance vertical's playbook, it is a parallel one.

Each vertical is otherwise held to the identical bar: HEIT structure, 9:16/≤60s/H.264 specs, Retention Techniques applied unconditionally, Hook-Window Rule (ADR-0017) and Hook Caption Sync/Cadence (ADR-0018) both apply regardless of language — the *evidence* behind those two ADRs (pixel-level face detection, caption cadence) is language-agnostic even though the exact burst-timing constants must be re-derived per language (already noted as a caveat in ADR-0018).

Adding a third niche/vertical, or changing which niches are active, still requires the Ask-First gate — this ADR documents the two verticals already running, it does not pre-approve future ones.

## Consequences

- AGENTS.md's "Niche"/"Language" framing at the top needs to state both verticals rather than reading as finance/English-only (fixed in this same change).
- CONTEXT.md's **Source Channel** glossary entry (previously exemplified only by an English finance channel) needs to note that health channels are also valid Source Channels under this strategy (fixed in this same change).
- The MAB/optimization-loop design (ADR-0009) was written assuming a single content stream; running two niches in parallel means variant-selection and reward-tracking should eventually be scoped per-niche, not pooled — not resolved here, flagged for whoever builds the target TypeScript autonomous system.
- `data/tracked_videos.csv` and `data/mab_state.json` currently have zero bacsihai/hardknocks rows — they appear scoped to the finance/MAB vertical only. Whether/how to fold the health vertical into that tracking is an open question, not resolved by this ADR.

## How this connects to existing docs

- `AGENTS.md` → "Niche: Finance/money-making" / "Language: English" lines updated to name both verticals.
- `CONTEXT.md` → **Source Channel** glossary entry updated.
- `docs/adr/0001-niche-finance-money-making.md` and `docs/adr/0004-*` (English-only) remain accurate for the *original* vertical; this ADR adds the second one alongside them rather than superseding either.
