# Context Map

## Project Structure (current, as of 2026-07-10)

- `pipeline/<project>/` : Per-project Python render scripts (e.g. `bacsihai/`, `giannis/`, `hardknocks/`); `pipeline/tools/` for shared utilities
- `output/projects/<name>/{source,clips,final,scripts}` : Per-project source downloads, cut clips, final 9:16 shorts, script drafts
- `output/shared/` : Libraries reused across projects (Pexels b-roll, processed emoji assets, metadata)
- `output/archive/` : Retired/superseded projects
- `output/unsorted/` : Downloaded source not yet assigned to a named project
- `data/` : `mab_state.json`, `tracked_videos.csv`, `targets/`, `video_metrics.db` (SQLite), `backups/`
- `docs/adr/` : Architecture Decision Records
- `docs/concepts/` : Unapproved concept bibles and style-feasibility artifacts; concepts do not change vertical topology or authorize production
- `scripts/` : Markdown video script drafts

## Project Structure (target, not yet built)

- `src/optimization/` : MAB Strategy Engine
- `src/pipeline/` : Content Pipeline (Script, Voice, Animation)
- `src/platforms/` : Chrome Uploader, YouTube Analytics

See `AGENTS.md` → "Current Implementation" vs "Architecture (Target)" for the full picture.

## Files

- `package.json` : Dependencies (currently empty — no scripts/deps yet)
- `AGENTS.md` : Project documentation
- `CONTEXT.md` : Project context
- `docs/concepts/outwished/SERIES-BIBLE.md` : Concept backbone for the high-IQ Owner-vs-Genie fair-play wish duel
