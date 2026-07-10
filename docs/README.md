# Shorts Docs

## ADR (Architecture Decision Records)
Decisions that shaped the project.

| ADR | Topic |
|-----|-------|
| 0001 | Niche: finance/money-making |
| 0002 | Animation style: Kitty Explain |
| 0003 | AB test one variable at a time |
| 0004 | Language: English only |
| 0005 | Content strategy: curate & repackage |
| 0006 | Multi-format video types (7 types) |
| 0007 | Clip Curation Edit (Type #7) |
| 0008 | Value-Added Editing — all 9 types |
| 0009 | Autonomous Optimization System |
| 0010 | Video quality degradation fix |
| 0011 | Success formula strategic layer |
| 0012 | AI video generation pipeline |
| 0013 | Contiguous VO Pipeline (architectural pattern) |
| 0014 | Dedicated vision model for video analysis |
| 0016 | Frequent editing (every 3s) |
| 0017 | Hook-Window: frame 0 must show a human face |
| 0018 | Hook caption sync and cadence |
| 0019 | Multi-niche AB testing (finance/English + health/Vietnamese) |

## Production Traces
Per-video documentation with pipeline, effects, retention data.

| Video | Format | Retention | File |
|-------|--------|-----------|------|
| KspJ3qHjtRU (Ackman ASCII) | Colored ASCII | 26% | [ackman-ascii.md](production/ackman-ascii.md) |
| KspJ3qHjtRU (clip analysis) | — | — | [ackman-clip-analysis.md](production/ackman-clip-analysis.md) |
| Dangote V9 (vision) | Emoji overlay | TBD | [dangote-v9.md](production/dangote-v9.md) |
| Dangote transcript | — | — | [dangote-transcript-analysis.md](production/dangote-transcript-analysis.md) |
| Billionaire V1→V2 | Kitty Explain | — | [billionaire-improvements.md](production/billionaire-improvements.md) |
| dHDpDXSIAkA (Lawnmower→2,600 Apartments) | Clip Curation Edit | pending (uploaded 2026-07-10) | [hardknocks-lawnmower-v1.md](production/hardknocks-lawnmower-v1.md) |

## Research
- [hook-benchmarks-2026-07/REPORT.md](research/hook-benchmarks-2026-07/REPORT.md) — Hook analysis of 6 viral finance Shorts (frames + transcript + comments), basis for ADR-0018

## Reference
- [vision-model-setup.md](vision-model-setup.md) — GPT-4o vision for video analysis
- [vision-glossary.md](vision-glossary.md) — Terminology for vision analysis
