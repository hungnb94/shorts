# Pipeline Scope

Read root `AGENTS.md`, `docs/WORKFLOW.md`, the matching `docs/production/*.md`, and only the relevant sections of `docs/agent/media-pitfalls.md` before editing.

Structure:

- `pipeline/<project>/`: one-off project/version render, TTS, caption, and verifier scripts.
- `pipeline/tools/`: genuinely shared transcription/media helpers only.
- `pipeline/longform/`: evidence-led authority asset tooling.
- `output/projects/<project>/`: all runtime inputs, intermediates, QC evidence, and final media for a project.

Rules:

- These Python renderers are manufacturing tools, not a product framework. Do not refactor unrelated historical renderers.
- Do not create or expand `test_render_*.py` unless explicitly requested. Verify the real MP4 with ffprobe, full decode, ASR, black/freeze/silence/audio checks, and frame/contact-sheet review.
- Keep value-add compositing separate from the base render when adding reusable behavior.
- Every new final filename is `yyyy-mm-dd-<name>.mp4` under the project's `final/` directory.
- Never silently fall back from the narrator selected by `data/narrator-voices/default.json`.
- Do not rerender a completed video after handoff without explicit revision feedback.
