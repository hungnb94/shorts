# Shorts

Animated short video factory — tự động sản xuất 6 videos/ngày (9:16, 30-60s) để AB test viral content formulas trên YouTube + TikTok, kiếm tiền qua ads revenue và affiliate marketing.

Niche: Finance/money-making (English) as the primary/documented vertical, run in parallel with two additional, deliberately-chosen verticals — health/longevity (Vietnamese, Source Channel "Bác sĩ Hải") per ADR-0019, and AI education (English, professionals/knowledge workers) per ADR-0020 — multi-niche AB testing: more parallel data streams → faster overall learning. Format: Kitty Explain (animated mascot + pop-up text + wild subtitles) for the finance vertical; the health vertical uses Clip Curation Edit exclusively (see `pipeline/bacsihai/`); the AI-education vertical uses Curate+Repackage (zero footage reuse) with the specific Video Type still undecided (see ADR-0020).

## Architecture (Target — not yet built)

Everything below this heading through "Commands" describes the intended autonomous TypeScript system. **None of it exists yet** — there is no `src/` directory and `package.json` has an empty `scripts: {}`. See **Current Implementation** below for what actually runs today.

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

## Current Implementation (as of 2026-07-10)

The real, working pipeline is manual/semi-manual Python + ffmpeg, run per project rather than as an autonomous loop:

| Path | Contents |
|------|----------|
| `pipeline/<project>/render_*.py` | Per-project render scripts (e.g. `pipeline/bacsihai/`, `pipeline/giannis/`, `pipeline/hardknocks/`) |
| `pipeline/render_shorts.py`, `pipeline/make_shorts.sh` | Generic/shared render entry points |
| `pipeline/tools/` | Shared utilities (`transcribe.py`, `montage.sh`) |
| `output/projects/<name>/{source,clips,final,scripts}` | One folder per project: raw source download, cut scene clips, final assembled 9:16 shorts, storyboard/script drafts |
| `output/shared/{pexels,emoji_processed,metadata}` | Libraries reused across projects |
| `output/archive/<name>/` | Retired/superseded projects, kept intact |
| `output/unsorted/<video-id>/` | Downloaded source clips not yet assigned to a named project |
| `data/mab_state.json`, `data/tracked_videos.csv`, `data/targets/`, `data/video_metrics.db` | Real stateful data — see Known Pitfalls, never delete |
| `scripts/*.md` | Markdown video script drafts (content, not code) |

`npm install`/`npm run ...` do not work yet — `package.json` has no dependencies or scripts. There is no Chrome uploader automation, no MAB engine, and no autonomous loop; videos are produced and uploaded manually per the current per-project Python scripts.

## File Dependency Chain (Target — not yet built)

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

## Commands (Target — not yet built)

None of these commands exist today; `package.json` has no scripts. Kept here as the target CLI surface for when the autonomous system is built.

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

- **TypeScript everywhere** — no Python. User default for new projects; the target autonomous system should be built this way. The current working pipeline (`pipeline/`) is Python + ffmpeg, predating this convention — not a model to copy for new code.
- **HEIT structure mandatory** — every script follows Hook(0-2s) → Explain → Illustrate → Teach. See CONTEXT.md.
- **Copy, don't invent** — find proven viral formats → repackage. Never invent new formats from scratch. See ADR 0002.
- **Autonomous optimization** — MAB selects variants, no human chooses experiments. System learns from AVD data. See ADR 0009.
- **3-day cycle** — upload 18 videos (6/day × 3), wait 48h for metrics, analyze + adjust, repeat. No daily manual intervention.
- **Video specs fixed** — 9:16 (1080x1920), 30-60s, MP4 H.264. No exceptions.
- **English for the finance vertical, Vietnamese for the health vertical** — each niche's output stays in its own Source Channel's language (ADR 0004 for finance; ADR 0019 for the parallel health/Vietnamese vertical). Never mix languages within one video.
- **Affiliate at end** — value first, pitch last. Never front-load affiliate mentions.
- **Chrome profile auth** — user logs into YouTube once, system reuses profile. No OAuth flow. See ADR 0009.
- **Download max quality** — always download source videos at highest available resolution (2160p/4K) using `yt-dlp -f "bestvideo[height>=2160]+bestaudio"`. Never accept default 720p.
- **3-source combo for engagement** — every video combines: (1) original source footage, (2) animated overlays (kinetic text, data viz, whiteboard), (3) Pexels b-roll for visual variety. This maximizes retention by avoiding visual monotony.
- **Standard workflow** — see `docs/WORKFLOW.md` for the mandatory per-video sequence, the blocking Hook Gate (Stage 0, no cutting/rendering before a strong 0-3s hook is chosen), and the required per-video Post-Production Retro.
- **Final video filenames are date-prefixed** — every rendered file under `output/projects/<project>/final/` uses `yyyy-mm-dd-<name>.mp4` (the render date), e.g. `2026-07-11-hardknocks_v2_implied_comparison.mp4`, so the creation date is visible without checking file metadata. Applies going forward from 2026-07-11; older files are not being renamed retroactively.

## How to Setup Autonomous System (Target — not yet built)

The four "How to" sections below (through "How to Add a New Platform") describe procedures for the target TypeScript system and reference `src/` paths and `npm run` commands that don't exist yet. See **Current Implementation** above for what to actually run today.

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

### Chrome profile expires after 30 days
YouTube session expires. If autonomous loop fails with "not logged in", run `npm run setup:chrome` to re-login. Check logs for "CHROME_AUTH_EXPIRED" error.

### Metrics lag is real — wait 48h minimum
YouTube Analytics data unstable <48h. Fetching at 24h = noisy AVD numbers → bad MAB decisions. System enforces 48h wait, don't override.

### MAB epsilon must decay gradually
Starting at ε=0.2 (20% explore) too early = stuck in local maxima. Starting at ε=0.8 too long = waste quota on bad variants. Follow 50→20 after 54 videos.

### Don't reset MAB state mid-cycle
Deleting `data/mab_state.json` while system running = lose all learned rewards → restart from scratch. Only reset when intentionally changing strategy.

### YouTube Shorts must be ≤60s
YouTube treats videos >60s as regular videos, not Shorts. This kills reach (regular videos don't appear in Shorts feed). The video-assembly layer enforces this, but TTS + animation timing can overrun — always verify final duration before upload.

### Affiliate links in video description
YouTube and TikTok strip or flag raw affiliate links. Always use a redirect domain (e.g., yourdomain.com/go/product). Never paste raw Amazon/ClickBank links.

### Hook timing is non-negotiable
HEIT framework: Hook must land in 0-2 seconds. Scripts that spend 5+ seconds on intro will tank AVD. The script-gen layer targets 15-25 words for hook section. If hook exceeds 25 words, it's too slow. A hook line should never be a single fully-resolved statement — it must open a gap/mystery (unclear object, withheld identity, a question left hanging) that only gets partially answered by t=5-8s. See CONTEXT.md → **Hook**.

### Hook text must not name both the cause AND the specific effect (self-caught, bacsihai v5)
Concrete failure mode, distinct from the abstract rule above: `render_bacsihai_v5.py`'s hook overlay ("LAO ĐỘNG CHÂN TAY ÍT BỊ ALZHEIMER HƠN?") named both the causal factor (manual labor) and the specific disease (Alzheimer) in the headline — technically a question, but it leaves almost no gap, since reading it alone already tells the viewer the entire claim being tested. Compare to v4's V1 hook ("NHỊN ĂN MÀ VẪN KHÔNG GIẢM CÂN?") which names a symptom but withholds the mechanism entirely. Checklist before finalizing any hook overlay: (1) does the headline alone already reveal the cause-and-effect pair, or just one side of it? If both, rewrite to withhold at least one. (2) For Contiguous VO segments (ADR-0013), check the actual timestamp within the chosen segment where the VO payoff lands — if it's well past ~8-10s (bacsihai v5's landed at ~33s of a 52.6s clip), the segment's pacing is weak regardless of overlay wording, and a different source range should be considered. Also: a hook built on a qualitative claim (source gives no number, only "much lower/higher") is inherently weaker than a Money+Number or Contrarian-Reveal hook — flag this as a source-selection constraint, not something overlay wording alone can fix.

### Hook-Window: frame 0 MUST show a human face (ADR-0017)
The 0-2s hook window is not just about hook TEXT — it is about what the viewer SEES at frame 0. For Clip Curation Edit, the source segment's first frame MUST contain a human face (skin-tone ≥10% by pixel stats). Title cards, static text graphics, "numbered list" transitions, and B-roll establishing shots are FORBIDDEN as segment starts. The first Pexels/value-add overlay must land ≤t=2s. Verified root cause of bacsihai V1 (YQTWHqTS1e8, 8.6% stayed) vs Dangote (ChWLcE3OYpA, 50% stayed): bacsihai's segment started at 304.5s = a static pink/white "Sai lầm số 5" title card (85% near-white, 0% face, first face at t=5s). Dangote started on his face at t=0. Before upload, verify with `inspect_image.py` on hook0.jpg — reject if skin-tone <10%. This rule sits ABOVE the Contiguous VO constraint: keep contiguity, but select the contiguous range so frame 0 shows a person.

### Hook caption sync and cadence (ADR-0018)
Benchmarked 6 independently viral Shorts (`docs/research/hook-benchmarks-2026-07/REPORT.md`) — all 6 shared two patterns not previously encoded as rules here:
- **Caption sync**: burned-in caption must be visible by t=0.2s (not delayed for a "clean" shot), updating every ~1-2s in short 2-5 word bursts synced to speech, with one keyword per burst visually emphasized (color/weight distinct from the rest).
- **Cadence**: at least one visual change (cut, zoom, new overlay, or continuous on-screen motion) every 1-2s within the hook window — tighter than the general 2-3s "2-Second Rule" (ADR-0016), specifically for the 0-5s hook region.
- **Show, don't just tell**: pair any spoken claim (wealth, results, a number) with simultaneous visual evidence (prop, environment, action) rather than narration alone — in the benchmark set, the verbal claim and its visual proof landed in the same beat, not sequentially.
Caveat: burst timing above was measured on English interview speech; Vietnamese TTS narration paces differently, so derive burst duration from actual TTS word-timing output per video, not a copy-pasted constant — verify legibility, not just retention theory, when tuning this for Bác sĩ Hải / Giảm Cân Healthy.

### Clip Curation Edit must pass the Transformative Gate
Video Type #7 (Clip Curation Edit) uses real footage from Source Channel — unlike the 6 animation types (zero-footage). Before upload, every Clip Curation Edit MUST pass all 3 Transformative Gate rules: (1) commentary track required, (2) min 2 value-adds from [fact-check callout, data viz, source citation, multi-source mashup, animated annotation, counter-argument], (3) cut ≤50% source duration + each clip <15s. Uploading a clip edit that fails the gate = copyright strike risk. Attribution is intentionally dropped per user decision.

### ffmpeg drawtext silently drops text containing a literal "%" (aiwork v1)
`drawtext`'s default `expansion=normal` parsing treats a bare `%` as a template-escape trigger (e.g. `%{pts}`) and silently drops the rest of the string when it isn't one - the filter still exits 0, with only a buried "Stray %" warning in stderr, so a caption can vanish from a render with no visible top-level error. Any caption/overlay text that may contain a real percentage (e.g. "25%") needs `expansion=none` added to its `drawtext` filter args. Doubling to `%%` did not reliably fix this in testing - use `expansion=none` instead. First hit in `pipeline/aiwork/render_aiwork_v1.py` (percentage-heavy captions); grepped `render_bacsihai_v5.py`/`render_hardknocks_v1.py` and confirmed neither has this problem today since their captions never contain a literal `%`.

### System fonts used in this repo lack some Unicode glyphs (aiwork v1)
`Helvetica.ttc`/`HelveticaNeue.ttc` (the only fonts used across this repo's render scripts) don't include every Unicode symbol - e.g. the arrow `→` renders as a missing-glyph "tofu" box. Stick to ASCII in `drawtext` caption content (e.g. `->` instead of `→`); verify visually via a rendered frame before assuming a symbol will show up.

### ffmpeg scene-detect (`select='gt(scene,T)'`) misses cuts between visually-similar distinct clips
Confirmed while analyzing an external video (`docs/research/800m-view-case-study-2026-07-11/REPORT.md`, `viral-video-analysis` skill's `extract_keyframes.py`, threshold=0.3, the same scene-detect approach ported from the old `analyze_video.py`): the algorithm found ZERO scene changes across a 33-second montage that direct frame-by-frame reading confirmed contains at least 4-5 real hard cuts between completely different clips/people/locations (every ~2-3s). It only fired reliably during a segment with genuine fast camera panning/motion blur. Root cause: ffmpeg's `scene` metric is a per-pixel frame-difference score, and cuts between clips with similar overall brightness/composition (e.g. person + gun + wall-colored background, repeated across many amateur clips shot in similar settings) can score below threshold even though the content is logically a hard cut. Do not trust `scene_keyframes` alone for cut-cadence claims on montage-of-distinct-clips content — cross-check with direct frame reads at fixed intervals (the `hook_window_frames` set), same as this project's existing decision (`docs/WORKFLOW.md` Stage 0) to keep frame-0 checks as human/Claude visual judgment rather than fully automated.

### "Original" content underperforms
Per wiki research (1.2B views case study): "Put your ego down and stop trying to be original." Every video should follow a proven format with variations. Inventing new formats from scratch is the #1 reason channels fail.

### Don't conflate Value-Add Layer with Retention Techniques
Value-Add Layer (fact-check, data viz, this_or_that — 9 types, see ADR 0008) is an AB variable: "có value-add vs không" is a valid experiment. Retention Techniques (sound design, zoom punch, pattern interrupt, pause-trimming + speed-up) is BASE QUALITY applied to every video automatically. NEVER AB test "có sound design vs không sound design" — the no-sound variant is low quality, unfair test.

### Pause-trimming + speed-up is a Retention Technique, applies to every video (aiwork v2)
Cut inter-sentence pauses/dead air out of the source (jump-cut style, hard cut - no crossfade needed) and apply a uniform speed-up (aiwork v2 used 1.1x, `setpts=PTS/1.1` + single `atempo=1.1` pass) to the final assembled timeline, after all cuts and overlays are burned in. This is base quality for every future video (Contiguous VO or Multi-Clip Mashup, ADR-0022), not an AB variable, same as sound design/zoom punch. The pause-cut threshold must be derived per-project from that project's own transcript's real inter-word gap distribution (look for the natural valley between "normal speech" and "real pause" gap lengths) - do not copy-paste 1.1x/0.35s as fixed constants across projects with different speakers/pacing.

### Value-Add Layer must be post-render compositing, not embedded in renderer
The value-add overlay layer (ADR 0008) must be a separate compositing step AFTER the base video renders. Do NOT couple it into the main renderer (current render_clip.py couples overlay rendering into clip rendering at line 175-481). To support all 7 video types, extract overlay compositing into a shared step: base video → composite value-add overlay → output. This keeps value-adds reusable across all types.

### YouTube Analytics API can lag well past 48h for a specific video, even when Studio/public view count already show data (fetch-metrics v1)
Confirmed against the real channel while first testing `src/platforms/youtube-analytics.ts` (ADR-0025): `dHDpDXSIAkA` (hardknocks_v1, uploaded 2026-07-10, public view count 1114 per `yt-dlp`, already past the 48h wait) returned zero for every metric — views, AVD, retention curve all empty — and doesn't appear at all in a channel-wide per-video breakdown that correctly returned real numbers for 8 *other*, older videos on the same channel (proving auth/query/channel-scoping were all correct, not a bug). The 48h rule (AGENTS.md's own "Metrics lag is real" pitfall, and ADR-0009's Analytics-lag research) describes when Studio-shown metrics stabilize — it does NOT guarantee the separate Analytics *reporting* API has finished indexing a brand-new, low-traffic-channel video by then. If `/fetch-metrics` returns an all-empty result for a video that's genuinely past 48h, treat it as "not indexed yet, retry in a day or two," not as "this video has zero engagement."

### YouTube Analytics API has no impressions/CTR metric under that name (fetch-metrics v1)
Confirmed via a real API call while building ADR-0025: `metrics=impressions` (and `impressionsClickThroughRate`) returns a hard `400 Unknown identifier (impressions) given in field parameters.metrics` — not a permissions/scope issue, the identifier itself doesn't exist in this API. Per-video CTR is not automatable via `youtube-analytics.ts`; the `EXPERIMENT-LOG.md` CTR figure (when present) stays a manual Studio-UI read.

### Action space explosion
7 video types × 3 hook types × 9 value-adds = 189 possible variants. MAB needs ~5-10 samples per variant for statistical significance = 945-1890 videos minimum. At 18 videos/cycle, that's 52-105 cycles (8-17 months) to fully explore. Epsilon-greedy helps but system will take months to converge. Don't expect optimal strategy in first 10 cycles.

## Boundaries

### Always
- Follow HEIT structure (Hook → Explain → Illustrate → Teach)
- Copy proven viral formats, repackage with variations
- Wait 48h before fetching YouTube Analytics (stable data)
- Apply Retention Techniques (sound design, zoom, pattern interrupt) to EVERY video — it's base quality, not optional
- Let MAB select variants autonomously — don't override its choices manually
- Verify video specs before upload (9:16, ≤60s, MP4 H.264)
- Log every decision (variant selected, epsilon, cycle number) for post-hoc review

### Ask First
- Adding a new animation format (requires research + ADR)
- Adding a fourth niche/vertical beyond the three confirmed (finance/English ADR-0001/0004, health/Vietnamese ADR-0019, AI-education/English ADR-0020)
- Changing epsilon schedule (affects exploration strategy)
- Spending money on paid tools/APIs
- Adding a new platform (TikTok, Instagram)

### Never
- Post videos >60s to YouTube Shorts
- Paste raw affiliate links in descriptions
- Invent "original" formats from scratch (copy what works)
- Reset MAB state mid-cycle (lose learned rewards)
- Fetch metrics before 48h (noisy data → bad decisions)
- Skip logging autonomous decisions (no audit trail = can't debug bad strategy)

## Testing

| What | Command | Why |
|------|---------|-----|
| Unit tests | `npm test` | Pipeline stages, AB test logic, video spec validation |
| Integration test | `npm run test:integration` | Full pipeline: script → render → verify output specs |
| Spec validation | `npm run test:specs` | Every rendered video checked for 9:16, duration, codec |

Integration tests mock TTS and animation APIs but validate real video output specs (ffprobe). This catches spec violations early without burning API credits.

## Architectural Policies

- **Autonomous loop is stateful**: MAB state (`data/mab_state.json`) persists across cycles. Deleting = restart from scratch.
- **Video spec enforcement**: `video-assembly.ts` is the single source of truth for output specs. No other layer may set video specs.
- **Metrics collection is async**: metrics fetched 48h+ after upload (YouTube Analytics lag). Never fetch before 48h or data is noisy.
- **Metrics data is append-only**: `video_metrics` table never mutates. Each fetch writes new row with timestamp.
- **Chrome profile is single source of auth**: No OAuth flow, no API keys for upload. User logs in once, system reuses profile.
- **MAB rewards are cumulative**: Each variant's reward = running average of AVD across all samples. More samples = more confident reward estimate.

## Ngôn ngữ khi trao đổi, giao tiếp: Tiếng Việt
