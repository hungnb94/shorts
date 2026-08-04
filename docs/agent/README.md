# Agent Context Index

This directory holds detailed instructions that should not be loaded into every session.

| File | Load when |
|---|---|
| `media-pitfalls.md` | Editing Python/ffmpeg renderers, TTS/audio composition, captions, overlays, or media QC |
| `strategy-analytics-pitfalls.md` | Market research, YouTube comments, metrics, MAB, publishing cadence, or experiment analysis |

Context policy:

1. `AGENTS.md` is the compact always-on policy and routing layer.
2. The nearest scoped `AGENTS.md` defines local workflow for `docs/`, `pipeline/`, `data/`, `output/`, or `spikes/`.
3. `CONTEXT.md` is the domain glossary; search for a term and read only that entry.
4. `docs/WORKFLOW.md` owns the ordered production gates.
5. ADRs explain durable decisions; production and research docs are historical evidence, not global policy.
