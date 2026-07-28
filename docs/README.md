# Shorts Docs

## Operating Guides

- [WORKFLOW.md](WORKFLOW.md) — blocking end-to-end production flow
- [MrBeast-Informed Short-Form Production System](guides/mrbeast-short-form-production-system.md) — expectation-first, backward-planned system for promise, progression, signature moment, critical components, payoff, and learning

## ADR (Architecture Decision Records)
Decisions that shaped the project.

| ADR | Topic |
|-----|-------|
| 0001 | Niche: finance/money-making |
| 0002 | Animation style: Kitty Explain |
| 0003 | AB test one variable at a time |
| 0004 | Language: English only |
| 0005 | Content strategy: curate & repackage |
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
| 0020 | Third niche: AI education (English) |
| 0037 | Expectation-payoff and critical-path production system |

## Production Traces
Per-video documentation with pipeline, effects, retention data.

| Video | Format | Retention | File |
|-------|--------|-----------|------|
| dHDpDXSIAkA (Lawnmower→2,600 Apartments) | Clip Curation Edit | pending (uploaded 2026-07-10) | [hardknocks-lawnmower-v1.md](production/hardknocks-lawnmower-v1.md) |
| Ronald Wayne v3 (10% of Apple) | Qwen TTS + word-aligned 40-beat render | technical pass; upload blocked | [ronald-wayne-v3-qwen-synced.md](production/ronald-wayne-v3-qwen-synced.md) |
| One Red Paperclip v1 | Visible trade-up challenge + Qwen/source payoff | uploaded/public; experiment in flight; publication deviations logged | [one-red-paperclip-v1.md](production/one-red-paperclip-v1.md) |

## Research
- [hook-benchmarks-2026-07/REPORT.md](research/hook-benchmarks-2026-07/REPORT.md) — Hook analysis of 6 viral finance Shorts (frames + transcript + comments), basis for ADR-0018

## Reference
- [MrBeast production guide — original English MarkItDown extraction](references/mrbeast-production-guide-original-en.md) — user-supplied PDF converted to Markdown; source material, not project policy
- [vision-glossary.md](vision-glossary.md) — Terminology for vision analysis
