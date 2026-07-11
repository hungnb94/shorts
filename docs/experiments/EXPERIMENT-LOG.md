# Experiment Log

Ghi nhận số liệu retention/engagement từ YouTube Studio.

| Video ID | Title | Pipeline | Duration | Stayed (Engagement/Hook) | Stayed (Retention/Overall) | AVD | Swiped Away | Notes |
|----------|-------|----------|----------|--------------------------|----------------------------|-----|-------------|-------|
| YQTWHqTS1e8 | NHỊN ĂN... | bacsihai_v4 | 59.5s | 8.6% | 8.6% | 0:29 | 91.4% | Hook failure, static card |
| ChWLcE3OYpA | Dangote | ADR-0016 | 52.1s | 43.4% | 51.6% | 0:19 | 57.7% | Benchmark GOOD |
| dF0Rr2C0Msc | Giannis V2 | Giannis V2 | 55.8s | 37.1% | N/A | N/A | 62.9% | Hook failure (37.1%) |
| dHDpDXSIAkA | Lawnmower→2,600 Apartments | hardknocks_v1 (ADR-0017/0018) | 51.4s | pending | pending | pending | pending | Uploaded 2026-07-10, fetch after 2026-07-12. First test of hook-benchmarks-2026-07 playbook. See `docs/production/hardknocks-lawnmower-v1.md` |
| TBD (not yet uploaded) | Lao Động Chân Tay Ít Bị Alzheimer Hơn? | bacsihai_v5 (ADR-0017/0018, new source) | 52.6s | N/A | N/A | N/A | N/A | Rendered 2026-07-10, not yet uploaded (manual upload pending). First Vietnamese-language mlx_whisper transcription in this repo. See `docs/production/bacsihai-v5-lao-dong-tay.md` |
| N/A (never uploaded, superseded) | AI Coding Jumped From 62% to 88% in ONE Year | aiwork_v1 (ADR-0020/0021) | 46.0s | N/A | N/A | N/A | N/A | Rendered 2026-07-10, superseded by aiwork_v2 before upload — user flagged the TTS preamble delaying the hook past 0-2s. Kept as the known-issues record. See `docs/production/aiwork-v1-capability-curve.md` |
| Mw7jeR6R6iE | AI Coding Jumped From 62% to 88% in ONE Year | aiwork_v2 (ADR-0020/0022, Multi-Clip Mashup) | 46.2s | pending | pending | pending | pending | Uploaded 2026-07-11, fetch metrics after 2026-07-13 07:34 +07 (48h). Rebuild of aiwork_v1: drops TTS, cuts together 10 pieces from across the 905s source (first video to declare the new Multi-Clip Mashup sub-format, ADR-0022, at build time), hard cuts only, pause-trimmed + sped up 1.1x (new base-quality Retention Technique, AGENTS.md). See `docs/production/aiwork-v2-capability-curve.md` |

*Glossary reference:*
- **Stayed (Engagement/Hook)**: "How viewers engaged" section (YouTube Studio). Measure hook performance.
- **Stayed (Retention/Overall)**: "Audience retention" section. Measure overall video engagement.
