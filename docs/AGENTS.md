# Documentation Scope

Read root `AGENTS.md` first. Do not bulk-read `docs/`; route by task.

| Need | Path |
|---|---|
| Mandatory production order and gates | `WORKFLOW.md` |
| Active market/channel direction | `strategy/` |
| Durable decision rationale | `adr/README.md`, then one relevant ADR |
| Current or historical video contract | `production/<video>.md` |
| External evidence | `research/<study>/REPORT.md` |
| Experiment outcomes | `experiments/` |
| Reusable templates | `templates/` |
| Detailed agent pitfalls | `agent/README.md` |

Rules:

- Historical plans/specs/research never override root policy or an accepted newer ADR.
- Add new global rules to `WORKFLOW.md` only when they change a production gate; use an ADR for hard-to-reverse decisions.
- Keep production-specific findings in the matching `production/*.md` unless evidence supports generalization.
- Preserve citations and relative links when moving documents; run the repository link check afterward.
