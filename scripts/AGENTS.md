# Repository Verification Scripts

This directory contains cross-project executable verification entry points. Historical Markdown content belongs in `docs/script-drafts/`.

Rules:

- Read root `AGENTS.md` and the relevant project production contract before running a verifier.
- Verifiers inspect real artifacts and fail closed; they must not mutate final media or durable data.
- Keep project-specific render/build logic under `pipeline/<project>/`; only cross-project or repository-level verification belongs here.
- Do not add Markdown video drafts to this directory.
