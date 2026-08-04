# Shorts

Evidence-led media system for selecting proven demand, producing authority assets, and using 9:16 Shorts as a discovery and experiment layer.

## Start here

| Task | Read first |
|---|---|
| Any repository work | `AGENTS.md` |
| Strategy or selecting the next idea | `docs/WORKFLOW.md` Stage -2, then `docs/strategy/` |
| Producing or revising a Short | `pipeline/AGENTS.md`, the matching `docs/production/*.md`, then `docs/WORKFLOW.md` |
| Media QC | `pipeline/AGENTS.md`, `docs/agent/media-pitfalls.md`, and the matching verifier |
| Metrics or experiment analysis | `docs/experiments/`, `docs/agent/strategy-analytics-pitfalls.md` |
| Domain terminology | `CONTEXT.md` (load only the relevant term) |
| Historical decision rationale | `docs/adr/README.md`, then the relevant ADR only |

## Directory map

| Path | Purpose |
|---|---|
| `docs/` | Strategy, workflow, ADRs, research, production records, and on-demand agent references |
| `pipeline/` | Current Python/ffmpeg render, TTS, transcription, and verification tools |
| `output/projects/<project>/` | Local source, intermediate clips, QC evidence, and final media grouped by project |
| `output/shared/` | Reusable local media libraries |
| `data/` | Stateful registries, channel/experiment state, narrator profiles, and upload metadata |
| `src/` | Small TypeScript automation surface; currently YouTube Analytics only |
| `assets/` | Versioned fonts and rights-managed SFX metadata/assets |
| `spikes/` | Self-contained experiments; local environments and generated work are disposable |
| `scripts/` | Cross-project executable verification entry points |
| `.agents/skills/` | Canonical project-local agent skills |
| `.claude/skills/` | Claude Code compatibility links to canonical project skills |

## Context discipline

Do not read entire directory trees. Start from the routing table, inspect filenames, then load only the production, ADR, research report, or pitfall file required by the task. Root policy overrides historical documents when they conflict.

Large binary media and generated evidence are intentionally ignored by Git. Their absence from `git status` does not mean they are safe to delete; follow `output/AGENTS.md`.
