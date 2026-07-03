# Shorts

Animated short video factory — tự động sản xuất 6 videos/ngày (9:16, 30-60s) để AB test viral content formulas trên YouTube + TikTok, kiếm tiền qua ads revenue và affiliate marketing.

Niche: Finance/money-making. Language: English. Format: Kitty Explain (animated mascot + pop-up text + wild subtitles).

## Architecture

```
                    ┌──────────────────────────────────────────────┐
                    │                CRON SCHEDULER                  │
                    │         (runs daily, 6 videos/day)             │
                    └───────────────────────┬──────────────────────┘
                                            │
                    ┌───────────────────────▼──────────────────────┐
                    │           CONTENT PIPELINE                    │
                    │                                               │
                    │  ┌─────────┐  ┌──────────┐  ┌─────────────┐ │
                    │  │ SCRIPT  │→ │ VOICE    │→ │ ANIMATION   │ │
                    │  │ GEN     │  │ TTS      │  │ RENDER      │ │
                    │  │ (HEIT)  │  │          │  │ (Kitty)     │ │
                    │  └─────────┘  └──────────┘  └──────┬──────┘ │
                    │                                     │        │
                    │  ┌──────────────────────────────────▼──────┐ │
                    │  │           VIDEO ASSEMBLY                 │ │
                    │  │  text overlays + subtitles + music + CTA │ │
                    │  │  → 9:16 MP4 H.264, 30-60s                │ │
                    │  └──────────────────────┬──────────────────┘ │
                    └─────────────────────────┼────────────────────┘
                                              │
                    ┌─────────────────────────▼────────────────────┐
                    │           DISTRIBUTION                        │
                    │  ┌──────────┐  ┌────────┐  ┌──────────────┐ │
                    │  │ YOUTUBE  │  │ TIKTOK │  │ METRICS COL  │ │
                    │  │ SHORTS   │  │        │  │ (AVD, views, │ │
                    │  │ API      │  │ API    │  │  affiliate)  │ │
                    │  └──────────┘  └────────┘  └──────┬───────┘ │
                    └────────────────────────────────────┼────────┘
                                                         │
                    ┌────────────────────────────────────▼────────┐
                    │           AB TEST ENGINE                     │
                    │  A (control, 3 videos) vs B (test, 3 videos) │
                    │  1 variable/experiment, metric: AVD          │
                    │  → winner declared after 7 same-variable     │
                    │    experiments                               │
                    └──────────────────────────────────────────────┘
```

| Layer | Path | Responsibility |
|-------|------|----------------|
| Content Pipeline | `src/pipeline/` | Script gen → TTS → animation render → video assembly |
| Distribution | `src/platforms/` | YouTube/TikTok upload + metrics collection |
| AB Test Engine | `src/ab-test/` | Experiment config, variant assignment, winner declaration |
| Data / Storage | `src/data/` | Experiment results, video metadata, affiliate tracking |
| CLI / Cron | `src/cli/` | Daily run command, experiment runner |

## File Dependency Chain

```
src/ab-test/experiment.ts        (experiment config — no deps)
       ↑
src/pipeline/script-gen.ts       (generates HEIT-structured scripts)
       ↑
src/pipeline/voice-tts.ts        (TTS audio from script)
       ↑
src/pipeline/animation-render.ts (Kitty Explain animation from script + audio)
       ↑
src/pipeline/video-assembly.ts   (compose: animation + overlays + music + CTA)
       ↑
src/cli/daily-run.ts             (orchestrates full pipeline for 1 day)
       ↑
src/platforms/youtube.ts, tiktok.ts  (upload + collect metrics)
       ↑
src/ab-test/analyzer.ts          (compare A vs B, declare winner)
```

## Commands

| Action | Command | Location |
|--------|---------|----------|
| Install deps | `npm install` | Root |
| Run dev (1 experiment) | `npm run dev -- --experiment <name>` | Root |
| Run daily (6 videos) | `npm run daily` | Root |
| Run AB test analysis | `npm run analyze` | Root |
| Type check | `npx tsc --noEmit` | Root |
| Test | `npm test` | Root |
| Lint | `npm run lint` | Root |
| Build | `npm run build` | Root |

## Key Conventions

- **TypeScript everywhere** — no Python. User default for new projects.
- **HEIT structure mandatory** — every script follows Hook(0-2s) → Explain → Illustrate → Teach. See CONTEXT.md.
- **Copy, don't invent** — find proven viral formats → repackage. Never invent new formats from scratch. See ADR 0002.
- **1 variable per experiment** — AB tests change exactly 1 dimension between A and B. See ADR 0003.
- **Video specs fixed** — 9:16 (1080x1920), 30-60s, MP4 H.264. No exceptions.
- **English only** — all content in English. See ADR 0004.
- **Affiliate at end** — value first, pitch last. Never front-load affiliate mentions.

## How to Add a New Experiment

1. Create experiment config in `src/ab-test/experiments/<name>.ts`:
   ```typescript
   export const experiment = {
     name: "hook-type-contrarian-vs-context",
     variable: "hookType",
     variantA: { hookType: "context" },
     variantB: { hookType: "contrarian" },
     duration: 7, // days to run
     metric: "avd",
   };
   ```
2. Register in `src/ab-test/registry.ts`
3. Run: `npm run dev -- --experiment hook-type-contrarian-vs-context`
4. After 7 days: `npm run analyze -- --experiment hook-type-contrarian-vs-context`

**Common gotcha**: experiment name must be unique across all experiments. Duplicate names overwrite results silently.

## How to Add a New Animation Format

1. Study proven viral format (manual TikTok/YouTube research, or use tools like wron.ai)
2. Create renderer in `src/pipeline/renderers/<format>.ts` implementing the `VideoRenderer` interface
3. Document format in `src/pipeline/renderers/README.md` with example output
4. Register in `src/pipeline/renderers/index.ts`
5. Can be used as AB variable: `{ renderer: "<format>" }`

**Common gotcha**: new format must produce 9:16 output. Renderers that output wrong aspect ratio will fail at upload step silently (YouTube accepts but algorithm deprioritizes).

## How to Add a New Platform

1. Implement `PlatformPublisher` interface in `src/platforms/<platform>.ts`
2. Required methods: `upload(video)`, `getMetrics(videoId)`, `getRetentionGraph(videoId)`
3. Register in `src/platforms/index.ts`
4. Add platform credentials to `.env` (see `.env.example`)
5. Metrics auto-collected by `src/data/metrics-collector.ts`

## Known Pitfalls

### DO NOT hardcode video specs
Every video MUST be 9:16 (1080x1920), 30-60s, MP4 H.264. Hardcoding different specs "just this once" breaks platform algorithm performance. Source specs from `src/data/constants.ts`.

### TikTok API rate limits
TikTok's upload API has strict rate limits (unofficial ~6/hour). When posting 6 videos/day, space uploads 10+ minutes apart. The `tiktok.ts` publisher has built-in delay, but if you bypass it, TikTok shadowbans the account.

### YouTube Shorts must be ≤60s
YouTube treats videos >60s as regular videos, not Shorts. This kills reach (regular videos don't appear in Shorts feed). The video-assembly layer enforces this, but TTS + animation timing can overrun — always verify final duration before upload.

### Affiliate links in video description
YouTube and TikTok strip or flag raw affiliate links. Always use a redirect domain (e.g., yourdomain.com/go/product). Never paste raw Amazon/ClickBank links.

### Hook timing is non-negotiable
HEIT framework: Hook must land in 0-2 seconds. Scripts that spend 5+ seconds on intro will tank AVD. The script-gen layer targets 15-25 words for hook section. If hook exceeds 25 words, it's too slow.

### Clip Curation Edit must pass the Transformative Gate
Video Type #7 (Clip Curation Edit) uses real footage from Source Channel — unlike the 6 animation types (zero-footage). Before upload, every Clip Curation Edit MUST pass all 3 Transformative Gate rules: (1) commentary track required, (2) min 2 value-adds from [fact-check callout, data viz, source citation, multi-source mashup, animated annotation, counter-argument], (3) cut ≤50% source duration + each clip <15s. Uploading a clip edit that fails the gate = copyright strike risk. Attribution is intentionally dropped per user decision.

### "Original" content underperforms
Per wiki research (1.2B views case study): "Put your ego down and stop trying to be original." Every video should follow a proven format with variations. Inventing new formats from scratch is the #1 reason channels fail.

## Boundaries

### Always
- Follow HEIT structure (Hook → Explain → Illustrate → Teach)
- Copy proven viral formats, repackage with variations
- Keep 1 variable per AB experiment
- Place affiliate/CTA at end, after value delivery
- Verify video specs before upload (9:16, ≤60s, MP4 H.264)

### Ask First
- Adding a new animation format (requires research + ADR)
- Changing niche away from finance/money-making
- Multi-variate testing (breaks the 1-variable rule)
- Spending money on paid tools/APIs

### Never
- Post videos >60s to YouTube Shorts
- Paste raw affiliate links in descriptions
- Invent "original" formats from scratch (copy what works)
- Skip AB test tracking (every video must be tagged with experiment + variant)
- Upload to both platforms simultaneously (space 10+ min apart)

## Testing

| What | Command | Why |
|------|---------|-----|
| Unit tests | `npm test` | Pipeline stages, AB test logic, video spec validation |
| Integration test | `npm run test:integration` | Full pipeline: script → render → verify output specs |
| Spec validation | `npm run test:specs` | Every rendered video checked for 9:16, duration, codec |

Integration tests mock TTS and animation APIs but validate real video output specs (ffprobe). This catches spec violations early without burning API credits.

## Architectural Policies

- **Experiment isolation**: each experiment writes to its own data directory. Never share state between experiments.
- **Video spec enforcement**: `video-assembly.ts` is the single source of truth for output specs. No other layer may set video specs.
- **Metrics collection is async**: metrics are fetched 24h+ after upload (platforms lag). Never analyze experiments with <24h old data.
- **AB data is append-only**: experiment results are never mutated. Winner declaration writes a new record, doesn't update old ones.
