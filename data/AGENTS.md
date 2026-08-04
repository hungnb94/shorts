# Data Scope

`data/` contains durable state, not disposable build output.

| Path | Policy |
|---|---|
| `mab_state.json` | Learned cumulative MAB state; never reset mid-cycle |
| `tracked_videos.csv` | Tracked experiment/video registry; preserve history |
| `source_videos.csv` | Source dedup registry; check before source selection |
| `targets/` | Strategy/target state; preserve |
| `uploads/` | Public upload metadata snapshots; preserve |
| `narrator-voices/` | Versioned narrator identity, rights, and runtime profiles; preserve hashes/artifacts |
| `video_metrics.db` | Local append-only metrics database; ignored by Git but never treat as cache |
| `backups/` | Recovery data; delete only with explicit user approval |

Rules:

- Inspect schema and all consumers before changing a field or path.
- Metrics collection appends observations; it does not rewrite historical rows.
- Never print credentials, tokens, or private channel identity data.
