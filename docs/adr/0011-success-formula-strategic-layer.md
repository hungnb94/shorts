# ADR 0011: Success Formula as Strategic Layer Above MAB Cycles

## Context
The autonomous optimization loop runs 3-day cycles (upload 18 videos → 48h wait → analyze → adjust MAB). This is a **tactical learning loop** — it explores/exploits variant combinations but has no strategic direction. The system needed a **strategic planning layer** that:
- Sets measurable 2-week targets (Target Cohorts)
- Translates analyzer insights into guided hypotheses
- Provides human-interpretable confidence and reasoning
- Creates a feedback loop: success → raise target / failure → research top channels

## Decision
Introduce **Success Formula** — a 9-step goal-planning framework applied at the start of each **Target Cohort** (2 weeks ≈ 3 optimization cycles). It sits above the MAB loop:

```
Success Formula (per cohort, 2 weeks)
    │
    ├── Step 1-3: Target definition (human + system)
    ├── Step 4-5: Confidence from MAB history (system)
    ├── Step 6-8: Hypotheses from Analyzer → ICE prioritized → Top 3 → MAB Overrides
    ├── Step 9: Execute (MAB reads overrides) → Monitor → Loop
    │
    └── Cohort Evaluation: mean AVD of 18 videos vs Target
         ├── Success → Target threshold +3-5%
         └── Failure → Auto-crawl top channels → new hypotheses
```

## Key Design Choices

1. **Cohort = 3 cycles (18 videos)** — aligns with MAB epsilon decay (54 videos = 9 cycles = 3 cohorts to reach 20% explore). 2-week horizon is long enough for statistical significance, short enough for course correction.

2. **Target metric = mean AVD** — directly matches MAB reward signal. No proxy metric mismatch.

3. **System-driven confidence (Step 4-5)** — calculated from MAB state: recent cycle success rate + top-variant stability + epsilon level. Removes human optimism bias.

4. **Hypotheses from Analyzer (Step 6)** — not invented; extracted from retention graph key moments (dips/peaks) and variant rankings. Each hypothesis = multi-dimension variant combo + predicted impact + confidence + effort.

5. **ICE prioritization (Step 7)** — lightweight heuristic (Impact × Confidence / Effort) to select Top 3. Avoids complex optimization; transparent and fast.

6. **MAB Override configs (Step 8)** — not manual override. Structured config files (`variant_priority_boost`, `epsilon_override`, etc.) that MAB reads autonomously. Preserves autonomy while injecting strategic direction.

7. **Auto-crawl on failure with human gate (Step 9)** — system finds patterns from top channels, but human approves before injecting. Balances automation speed with quality control.

## Consequences

- **Positive**: Strategic coherence across cycles; human-understandable planning; guided exploration reduces wasted MAB samples; failure triggers systematic research.
- **Negative**: Added complexity (new files, modules); cohort horizon (2 weeks) delays feedback vs per-cycle; ICE heuristic may miss non-obvious combos.
- **Risk**: If overrides are too restrictive, MAB loses exploration benefit. Mitigation: overrides only boost priority, never forbid variants; epsilon still controls explore ratio.

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|------------------|
| Per-cycle targets (3 days) | Too noisy; AVD unstable per cycle; no strategic arc |
| Monthly targets (4+ weeks) | Too slow; 48h metrics lag × 6+ cycles = month before feedback |
| Pure MAB (no strategic layer) | No direction; explores randomly forever; human can't interpret why |
| Human-picked variants per cycle | Violates autonomous principle; bias; doesn't scale |

## Implementation Notes

New modules needed:
- `src/optimization/confidence.ts` — confidence calculation from MAB state
- `src/optimization/hypothesis.ts` — hypothesis extraction from analyzer output
- `src/optimization/ice.ts` — ICE scoring and ranking
- `src/optimization/mab-override.ts` — override config schema + reader in MAB
- `src/optimization/auto-crawl.ts` — top channel discovery + transcript analysis
- `src/cli/cohort.ts` — cohort tracking, evaluation, Success Formula orchestration

Data files:
- `data/targets/{cohort_id}.json`
- `data/mab_overrides/{cohort_id}_cycle{N}.json`
- `data/patterns/{pattern_id}.json`
- `data/crawl_cache/{channel_id}.json`