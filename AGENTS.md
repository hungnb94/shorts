# Shorts

Animated short video factory — tự động sản xuất 6 videos/ngày (9:16, 30-60s) để AB test viral content formulas trên YouTube + TikTok, kiếm tiền qua ads revenue và affiliate marketing.

Niche: Finance/money-making. Language: English. Format: Kitty Explain (animated mascot + pop-up text + wild subtitles).

## Architecture

```
                    ┌──────────────────────────────────────────────┐
                    │         AUTONOMOUS OPTIMIZATION LOOP          │
                    │            (3-day cycle, no human)            │
                    └───────────────────────┬──────────────────────┘
                                            │
                    ┌───────────────────────▼──────────────────────┐
                    │              MAB STRATEGY ENGINE              │
                    │   Epsilon-greedy: 50-50 → 20-80 after 54 vids │
                    │   Action: 7 types × 3 hooks × 9 value-adds   │
                    └───────────────────────┬──────────────────────┘
                                            │ (select 18 variants)
                    ┌───────────────────────▼──────────────────────┐
                    │           CONTENT PIPELINE                    │
                    │                                               │
                    │  ┌─────────┐  ┌──────────┐  ┌─────────────┐ │
                    │  │ SCRIPT  │→ │ VOICE    │→ │ ANIMATION   │ │
                    │  │ GEN     │  │ TTS      │  │ RENDER      │ │
                    │  │ (HEIT)  │  │          │  │ (7 types)   │ │
                    │  └─────────┘  └──────────┘  └──────┬──────┘ │
                    │                                     │        │
                    │  ┌──────────────────────────────────▼──────┐ │
                    │  │           VIDEO ASSEMBLY                 │ │
                    │  │  text overlays + subtitles + music + CTA │ │
                    │  │  → 9:16 MP4 H.264, 30-60s                │ │
                    │  └──────────────────────┬──────────────────┘ │
                    └─────────────────────────┼────────────────────┘
                                              │ (18 MP4 ready)
                    ┌─────────────────────────▼────────────────────┐
                    │         CHROME UPLOADER (Playwright)          │
                    │   Logged-in profile, 6 videos/day × 3 days    │
                    │   Auto title/description/tags                 │
                    └─────────────────────────┬────────────────────┘
                                              │ (videoId × 18)
                    ┌─────────────────────────▼────────────────────┐
                    │              48H METRICS WAIT                 │
                    │   (YouTube Analytics lag, stable after 48h)   │
                    └─────────────────────────┬────────────────────┘
                                              │
                    ┌─────────────────────────▼────────────────────┐
                    │         METRICS FETCHER (Analytics API)       │
                    │   AVD %, CTR, views, retention graph          │
                    │   Store: SQLite video_metrics table           │
                    └─────────────────────────┬────────────────────┘
                                              │
                    ┌─────────────────────────▼────────────────────┐
                    │              ANALYZER & OPTIMIZER             │
                    │   Key moments (dips/peaks), rank variants     │
                    │   Update MAB rewards, adjust epsilon          │
                    │   Extract patterns → inform next cycle        │
                    └─────────────────────────┬────────────────────┘
                                              │
                                              └───► Loop to MAB (Cycle N+1)
```

| Layer | Path | Responsibility |
|-------|------|----------------|
| MAB Strategy | `src/optimization/` | Multi-Armed Bandit variant selection, epsilon decay, reward tracking |
| Content Pipeline | `src/pipeline/` | Script gen → TTS → animation render → video assembly |
| Chrome Uploader | `src/platforms/chrome-uploader.ts` | Playwright automation, logged-in profile upload |
| Metrics Fetcher | `src/platforms/youtube-analytics.ts` | Fetch AVD, CTR, retention graph after 48h |
| Analyzer | `src/optimization/analyzer.ts` | Key moments detection, variant ranking, pattern extraction |
| Data / Storage | `src/data/` | SQLite: video_metrics, mab_state, variant_performance |
| CLI / Cron | `src/cli/` | Autonomous cycle runner, 3-day loop orchestration |

## File Dependency Chain

```
src/optimization/mab-strategy.ts     (variant selection — no deps)
       ↑
src/pipeline/script-gen.ts           (generates HEIT-structured scripts)
       ↑
src/pipeline/voice-tts.ts            (TTS audio from script)
       ↑
src/pipeline/animation-render.ts     (7 video types from script + audio)
       ↑
src/pipeline/video-assembly.ts       (compose: animation + overlays + music + CTA)
       ↑
src/platforms/chrome-uploader.ts     (Playwright upload, 6 videos/day × 3 days)
       ↑
       [48h wait]
       ↑
src/platforms/youtube-analytics.ts   (fetch AVD, CTR, retention graph)
       ↑
src/optimization/analyzer.ts         (key moments, rank variants, update MAB)
       ↑
       [loop back to mab-strategy.ts for next cycle]
```

## Commands

| Action | Command | Location |
|--------|---------|----------|
| Install deps | `npm install` | Root |
| Setup Chrome profile | `npm run setup:chrome` | Root |
| Run autonomous cycle | `npm run autonomous` | Root |
| Run single cycle (dev) | `npm run cycle -- --dry-run` | Root |
| Check MAB state | `npm run mab:status` | Root |
| Fetch metrics manually | `npm run metrics:fetch` | Root |
| Analyze retention graphs | `npm run analyze:retention` | Root |
| Type check | `npx tsc --noEmit` | Root |
| Test | `npm test` | Root |
| Lint | `npm run lint` | Root |
| Build | `npm run build` | Root |

## Key Conventions

- **TypeScript everywhere** — no Python. User default for new projects.
- **HEIT structure mandatory** — every script follows Hook(0-2s) → Explain → Illustrate → Teach. See CONTEXT.md.
- **Copy, don't invent** — find proven viral formats → repackage. Never invent new formats from scratch. See ADR 0002.
- **Autonomous optimization** — MAB selects variants, no human chooses experiments. System learns from AVD data. See ADR 0009.
- **3-day cycle** — upload 18 videos (6/day × 3), wait 48h for metrics, analyze + adjust, repeat. No daily manual intervention.
- **Video specs fixed** — 9:16 (1080x1920), 30-60s, MP4 H.264. No exceptions.
- **English only** — all content in English. See ADR 0004.
- **Affiliate at end** — value first, pitch last. Never front-load affiliate mentions.
- **Chrome profile auth** — user logs into YouTube once, system reuses profile. No OAuth flow. See ADR 0009.

## How to Setup Autonomous System

1. **Chrome profile setup**:
   ```bash
   npm run setup:chrome
   # Opens Chrome → user logs into YouTube manually → save profile
   # Profile path: ~/Library/Application Support/Google/Chrome/Profile Shorts
   ```

2. **Verify profile works**:
   ```bash
   npm run cycle -- --dry-run
   # Should open YouTube upload page with logged-in state
   ```

3. **Start autonomous loop**:
   ```bash
   npm run autonomous
   # Runs forever: 3-day cycle → 48h wait → analyze → repeat
   # Check status: npm run mab:status
   ```

4. **Monitor progress**:
   - Logs: `logs/autonomous-YYYY-MM-DD.log`
   - MAB state: `data/mab_state.json`
   - Metrics: `data/video_metrics.db` (SQLite)

**Common gotcha**: Chrome profile expires after 30 days. Re-login with `npm run setup:chrome` if uploads fail with "not logged in" error.

## How to Add a New Video Type

1. Study proven viral format (manual TikTok/YouTube research, or use tools like wron.ai)
2. Create renderer in `src/pipeline/renderers/<format>.ts` implementing the `VideoRenderer` interface
3. Document format in `src/pipeline/renderers/README.md` with example output
4. Register in `src/pipeline/renderers/index.ts`
5. Add to MAB action space in `src/optimization/mab-strategy.ts`

**Common gotcha**: new format must produce 9:16 output. Renderers that output wrong aspect ratio will fail at upload step silently (YouTube accepts but algorithm deprioritizes).

## How to Adjust MAB Strategy

1. **Change epsilon decay**:
   ```typescript
   // src/optimization/mab-strategy.ts
   const EPSILON_START = 0.5;      // Initial explore rate
   const EPSILON_END = 0.2;        // Final explore rate
   const DECAY_AFTER_VIDEOS = 54;  // 3 cycles × 18 videos
   ```

2. **Change cycle length**:
   ```typescript
   // src/cli/autonomous.ts
   const VIDEOS_PER_DAY = 6;
   const CYCLE_DAYS = 3;           // Upload phase
   const METRICS_WAIT_HOURS = 48;  // Wait phase
   ```

3. **Add new action dimension**:
   ```typescript
   // src/optimization/action-space.ts
   type Variant = {
     videoType: VideoType;   // existing
     hookType: HookType;     // existing
     valueAddType: ValueAddType; // existing
     voiceGender?: "male" | "female"; // NEW dimension
   };
   ```

**Common gotcha**: changing epsilon after system started = need to reset MAB state (`rm data/mab_state.json`) or old epsilon persists.

## How to Add a New Platform

1. Implement upload automation in `src/platforms/<platform>-uploader.ts` (e.g., TikTok, Instagram)
2. Implement metrics fetcher in `src/platforms/<platform>-analytics.ts`
3. Required methods:
   - Uploader: `upload(video, metadata)` → videoId
   - Analytics: `fetchMetrics(videoId, waitHours)` → { avd, ctr, views, retentionGraph }
4. Register in `src/platforms/index.ts`
5. Add platform credentials to `.env` (if using API) or Chrome profile (if using automation)

**Common gotcha**: TikTok rate limits harsh (~6 uploads/hour unofficial). When adding TikTok, space uploads 10+ min apart or risk shadowban.

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

### Don't conflate Value-Add Layer with Retention Techniques
Value-Add Layer (fact-check, data viz, this_or_that — 9 types, see ADR 0008) is an AB variable: "có value-add vs không" is a valid experiment. Retention Techniques (sound design, zoom punch, pattern interrupt) is BASE QUALITY applied to every video automatically. NEVER AB test "có sound design vs không sound design" — the no-sound variant is low quality, unfair test.

### Value-Add Layer must be post-render compositing, not embedded in renderer
The value-add overlay layer (ADR 0008) must be a separate compositing step AFTER the base video renders. Do NOT couple it into the main renderer (current render_clip.py couples overlay rendering into clip rendering at line 175-481). To support all 7 video types, extract overlay compositing into a shared step: base video → composite value-add overlay → output. This keeps value-adds reusable across all types.

## Boundaries

### Always
- Follow HEIT structure (Hook → Explain → Illustrate → Teach)
- Copy proven viral formats, repackage with variations
- Keep 1 variable per AB experiment
- Place affiliate/CTA at end, after value delivery
- Verify video specs before upload (9:16, ≤60s, MP4 H.264)
- Apply Retention Techniques (sound design, zoom, pattern interrupt) to EVERY video — it's base quality, not optional

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
