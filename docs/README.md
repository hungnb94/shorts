# Shorts Documentation

Use this page as a router. Do not read every document in a category.

| Need | Start here | Then load |
|---|---|---|
| Select market or next idea | [`WORKFLOW.md`](WORKFLOW.md) Stage -2 | One active file in [`strategy/`](strategy/) and only relevant research |
| Produce or revise a video | [`WORKFLOW.md`](WORKFLOW.md) | Matching entry in [`production/README.md`](production/README.md) and relevant ADR |
| Understand a durable decision | [`adr/README.md`](adr/README.md) | One ADR by number/topic |
| Find external evidence | [`research/README.md`](research/README.md) | Study `REPORT.md`; raw evidence only if needed |
| Review experiment results | [`experiments/FRAMEWORK-REGISTRY.md`](experiments/FRAMEWORK-REGISTRY.md) | [`experiments/EXPERIMENT-LOG.md`](experiments/EXPERIMENT-LOG.md) |
| Run media QC | [`agent/media-pitfalls.md`](agent/media-pitfalls.md) | [`verification/`](verification/) and matching production verifier |
| Analyze metrics/publishing | [`agent/strategy-analytics-pitfalls.md`](agent/strategy-analytics-pitfalls.md) | Relevant ADR/experiment row |
| Reuse a document shape | [`templates/`](templates/) | One relevant template |
| Look up vision terminology | [`vision-glossary.md`](vision-glossary.md) | Only the relevant term |

## Categories

- `strategy/`: active market, authority-asset, and channel direction.
- `production/`: per-video contracts, retrospectives, metadata, QC, and upload evidence.
- `research/`: evidence packages; each study should be entered through `REPORT.md`.
- `adr/`: accepted and historical architecture/strategy decisions.
- `experiments/`: framework lifecycle and observed performance.
- `plans/`: historical execution plans; not policy.
- `specs/`: historical design specifications; not policy.
- `concepts/`: unapproved concepts; never authorize production by themselves.
- `script-drafts/`: historical Markdown script drafts; content, not executable code.
- `guides/`: reusable operating guidance.
- `references/`: source material, not project policy.
- `verification/`: calibration and verification artifacts.
- `agent/`: detailed on-demand context removed from the always-loaded root instructions.

Precedence: root `AGENTS.md` → accepted newer ADR/active strategy → `WORKFLOW.md` → current production contract → historical plans/specs/research.