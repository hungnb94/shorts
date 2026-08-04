# Spike Scope

Each directory under `spikes/` is a self-contained experiment with its own README, lockfiles, scripts, and verification evidence.

Rules:

- Keep decision records, source scripts, tests, complete lockfiles, and canonical artifacts.
- Local virtual environments (`.venv-*`), model caches, and generated `work/` outputs are disposable and must stay ignored.
- A completed spike must state its decision and regeneration commands in its README.
- Production code must not import from a spike. Promote validated behavior into `pipeline/`, `src/`, or `data/` explicitly.
