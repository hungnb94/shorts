# Output Scope

`output/` is a local media workspace and can exceed many gigabytes. Never scan or load it recursively by default.

Structure:

- `projects/<project>/source/`: downloaded source media and source transcripts.
- `projects/<project>/clips/`: cuts, render workspaces, overlays, audio, and QC evidence.
- `projects/<project>/final/`: final MP4 and final metrics artifacts.
- `shared/`: reusable Pexels, emoji, metadata, and other shared media.
- `archive/`: intentionally retired projects kept for recovery/history.
- `unsorted/`: source media not yet assigned to a project.

Cleanup policy:

- Preserve source media, final MP4s, production/QC contracts, upload evidence, and anything referenced by an active renderer.
- Scratch directories named `temp`, generated `__pycache__`, concat lists, logs, extracted frame sweeps, and intermediate audio/video may be regenerated, but remove them only after confirming the final and production record are complete.
- Never infer dispensability from `.gitignore`; large valuable media is ignored deliberately.
- For a task, inspect only `output/projects/<current-project>/` and only the needed version workspace.
