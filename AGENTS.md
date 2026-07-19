# Shorts

Animated short video factory — sản xuất Shorts 9:16, 50-75s và phát hành qua ba Channel Pool theo Plateau-Gated Cadence để AB test viral content formulas trên YouTube + TikTok, kiếm tiền qua ads revenue và affiliate marketing.

Niche: Finance/money-making (English) as the primary/documented vertical, run in parallel with two additional, deliberately-chosen verticals — health/longevity (Vietnamese, Source Channel "Bác sĩ Hải") per ADR-0019, and AI education (English, professionals/knowledge workers) per ADR-0020 — multi-niche AB testing: more parallel data streams → faster overall learning. Format: Kitty Explain (animated mascot + pop-up text + wild subtitles) for the finance vertical; the health vertical uses Clip Curation Edit exclusively (see `pipeline/bacsihai/`); the AI-education vertical uses Curate+Repackage (zero footage reuse) with the specific Video Type still undecided (see ADR-0020).

## Architecture (Target — not yet built)

Everything below this heading through "Commands" describes the intended autonomous TypeScript system. **None of it exists yet** — there is no `src/` directory and `package.json` has an empty `scripts: {}`. See **Current Implementation** below for what actually runs today.

```
                    ┌──────────────────────────────────────────────┐
                    │         AUTONOMOUS OPTIMIZATION LOOP          │
                    │       (plateau-gated scheduler, no quota)     │
                    └───────────────────────┬──────────────────────┘
                                            │
                    ┌───────────────────────▼──────────────────────┐
                    │              MAB STRATEGY ENGINE              │
                    │   Epsilon-greedy: 50-50 → 20-80 after 54 vids │
                    │   Action: 7 types × 3 hooks × 9 value-adds   │
                    └───────────────────────┬──────────────────────┘
                                            │ (select next eligible variant)
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
                    │  │  → 9:16 MP4 H.264, 50-75s                │ │
                    │  └──────────────────────┬──────────────────┘ │
                    └─────────────────────────┼────────────────────┘
                                              │ (next eligible MP4 ready)
                    ┌─────────────────────────▼────────────────────┐
                    │         CHROME UPLOADER (Playwright)          │
                    │   3 lanes/vertical, strict round-robin        │
                    │   Plateau + metadata gates before upload      │
                    └─────────────────────────┬────────────────────┘
                                              │ (videoId + channelId)
                    ┌─────────────────────────▼────────────────────┐
                    │              48H METRICS WAIT                 │
                    │   (YouTube Analytics lag, stable after 48h)   │
                    └─────────────────────────┬────────────────────┘
                                              │
                    ┌─────────────────────────▼────────────────────┐
                    │         METRICS FETCHER (Analytics API)       │
                    │   AVD seconds, views, retention graph         │
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
| Metrics Fetcher | `src/platforms/youtube-analytics.ts` | Fetch API AVD/views/retention after 48h; Shorts Feed share remains a Studio check |
| Analyzer | `src/optimization/analyzer.ts` | Key moments detection, variant ranking, pattern extraction |
| Data / Storage | `src/data/` | SQLite: video_metrics, mab_state, variant_performance |
| CLI / Cron | `src/cli/` | Plateau eligibility, Channel Pool rotation and autonomous orchestration |

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
src/platforms/chrome-uploader.ts     (Playwright upload, plateau-gated Channel Pool rotation)
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
- **HEIT structure mandatory** — every script follows Hook(0-3s; promise/gap by 0-2s) → Explain → Illustrate → Teach. See CONTEXT.md.
- **Copy, don't invent** — find proven viral formats → repackage. Never invent new formats from scratch. See ADR 0002.
- **Autonomous optimization** — MAB selects variants, no human chooses experiments. System learns from AVD data. See ADR 0009.
- **Plateau-Gated Cadence** — no fixed daily/weekly quota. Each vertical uses three phone-verified, ≥3-week-aged Destination Channels in strict round-robin order; the next lane must be eligible under ADR-0035.
- **Video specs fixed** — 9:16 (1080x1920), 50-75s, MP4 H.264 with audio. No exceptions for new production (ADR-0034).
- **English for the finance vertical, Vietnamese for the health vertical** — each niche's output stays in its own Source Channel's language (ADR 0004 for finance; ADR 0019 for the parallel health/Vietnamese vertical). Never mix languages within one video.
- **Affiliate at end** — value first, pitch last. Never front-load affiliate mentions.
- **Per-channel Chrome profile auth** — each Destination Channel keeps reusable logged-in browser identity for upload; Analytics authorization is scoped independently per channel. No OAuth flow is introduced for upload itself. See ADR-0009/0035.
- **Download max quality** — always download source videos at highest available resolution (2160p/4K) using `yt-dlp -f "bestvideo[height>=2160]+bestaudio"`. Never accept default 720p.
- **3-source combo for engagement** — every video combines: (1) original source footage, (2) animated overlays (kinetic text, data viz, whiteboard), (3) Pexels b-roll for visual variety. This maximizes retention by avoiding visual monotony.
- **Standard workflow** — see `docs/WORKFLOW.md` for the mandatory per-video sequence, the blocking Hook Gate (Stage 0, no cutting/rendering before a strong 0-3s hook is chosen), and the required per-video Post-Production Retro.
- **Guide-derived verification baseline** — every new Short must pass ADR-0034: early SFX, calibrated caption profile, Mid-Roll Triple CTA at t=38-42s, moving watermark, compact metadata, playlist/Related wiring and explicit Studio settings.
- **Media-first verification; no renderer unit tests** — the current `pipeline/<project>/render_*.py` files are one-off video-production tools, not product code. Do not create, extend, or require `test_render_*.py` files and do not apply TDD to these renderers unless the user explicitly requests automated code tests. Verify the rendered MP4 itself with ffprobe/spec checks, full decode, final ASR, detector output, and manual frame/contact-sheet review. Existing renderer tests are legacy artifacts, not templates for future videos. Do not proactively revise a completed video; wait for the user to request a revision.
- **Final video filenames are date-prefixed** — every rendered file under `output/projects/<project>/final/` uses `yyyy-mm-dd-<name>.mp4` (the render date), e.g. `2026-07-11-hardknocks_v2_implied_comparison.mp4`, so the creation date is visible without checking file metadata. Applies going forward from 2026-07-11; older files are not being renamed retroactively.

## How to Setup Autonomous System (Target — not yet built)

The four "How to" sections below (through "How to Add a New Platform") describe procedures for the target TypeScript system and reference `src/` paths and `npm run` commands that don't exist yet. See **Current Implementation** above for what to actually run today.

1. **Chrome profile setup** (repeat once per Destination Channel; nine total under ADR-0035):
   ```bash
   npm run setup:chrome
   # Opens Chrome → user logs into the intended Destination Channel → save that lane's profile
   # Every lane needs a distinct persisted browser identity/profile path.
   ```

2. **Verify profile works**:
   ```bash
   npm run cycle -- --dry-run
   # Should open YouTube upload page with logged-in state
   ```

3. **Start autonomous loop**:
   ```bash
   npm run autonomous
   # Runs forever: check next lane eligibility → upload → measure → analyze → repeat
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
   const DECAY_AFTER_VIDEOS = 54;  // eligible measured Shorts, not calendar cycles
   ```

2. **Change publishing cadence**: fixed `VIDEOS_PER_DAY`/`CYCLE_DAYS` constants are superseded. The future scheduler must implement ADR-0035's Distribution Plateau, strict round-robin and No-Feed rules; no current `src/` implementation exists to edit.

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
Every new Short MUST be 9:16 (1080x1920), 50-75s, MP4 H.264 with audio. Hardcoding different specs "just this once" breaks project comparability. The future `src/data/constants.ts` must become the single source when it exists; current Python renderers must validate the final artifact directly.

### Chrome profile expires after 30 days
YouTube session expires. If autonomous loop fails with "not logged in", run `npm run setup:chrome` to re-login. Check logs for "CHROME_AUTH_EXPIRED" error.

### Metrics lag is real — wait 48h minimum
YouTube Analytics data unstable <48h. Fetching at 24h = noisy AVD numbers → bad MAB decisions. System enforces 48h wait, don't override.

### MAB epsilon must decay gradually
Starting at ε=0.2 (20% explore) too early = stuck in local maxima. Starting at ε=0.8 too long = waste quota on bad variants. Follow 50→20 after 54 videos.

### Don't reset MAB state mid-cycle
Deleting `data/mab_state.json` while system running = lose all learned rewards → restart from scratch. Only reset when intentionally changing strategy.

### The old ≤60s platform claim is obsolete; the project range is 50-75s
YouTube's current official policy classifies eligible square/vertical uploads up to three minutes as Shorts. ADR-0034 intentionally chooses a stricter 50-75s internal range from the supplied retention guide. Do not reject 61-75s as long-form, and do not expand beyond 75s without a new decision.

### Affiliate links in video description
YouTube and TikTok strip or flag raw affiliate links. Always use a redirect domain (e.g., yourdomain.com/go/product). Never paste raw Amazon/ClickBank links.

### Hook timing is non-negotiable
HEIT framework: Hook must land in 0-2 seconds. Scripts that spend 5+ seconds on intro will tank AVD. The script-gen layer targets 15-25 words for hook section. If hook exceeds 25 words, it's too slow. A hook line should never be a single fully-resolved statement — it must open a gap/mystery (unclear object, withheld identity, a question left hanging) that only gets partially answered by t=5-8s. See CONTEXT.md → **Hook**.

### Hook text must not name both the cause AND the specific effect (self-caught, bacsihai v5)
Concrete failure mode, distinct from the abstract rule above: `render_bacsihai_v5.py`'s hook overlay ("LAO ĐỘNG CHÂN TAY ÍT BỊ ALZHEIMER HƠN?") named both the causal factor (manual labor) and the specific disease (Alzheimer) in the headline — technically a question, but it leaves almost no gap, since reading it alone already tells the viewer the entire claim being tested. Compare to v4's V1 hook ("NHỊN ĂN MÀ VẪN KHÔNG GIẢM CÂN?") which names a symptom but withholds the mechanism entirely. Checklist before finalizing any hook overlay: (1) does the headline alone already reveal the cause-and-effect pair, or just one side of it? If both, rewrite to withhold at least one. Also: a hook built on a qualitative claim (source gives no number, only "much lower/higher") is inherently weaker than a Money+Number or Contrarian-Reveal hook — flag this as a source-selection constraint, not something overlay wording alone can fix.

### Hook-Window: frame 0 MUST show a human face (ADR-0017)
The 0-2s hook window is not just about hook TEXT — it is about what the viewer SEES at frame 0. For Clip Curation Edit, the source segment's first frame MUST contain a human face (skin-tone ≥10% by pixel stats). Title cards, static text graphics, "numbered list" transitions, and B-roll establishing shots are FORBIDDEN as segment starts. The first Pexels/value-add overlay must land ≤t=2s. Verified root cause of bacsihai V1 (YQTWHqTS1e8, 8.6% stayed) vs Dangote (ChWLcE3OYpA, 50% stayed): bacsihai's segment started at 304.5s = a static pink/white "Sai lầm số 5" title card (85% near-white, 0% face, first face at t=5s). Dangote started on his face at t=0. Before upload, verify with `inspect_image.py` on hook0.jpg — reject if skin-tone <10%. This rule sits ABOVE the Contiguous VO constraint: keep contiguity, but select the contiguous range so frame 0 shows a person.

### Full-screen Pexels/B-roll overlay must never replace the speaker's face anywhere in 0-10s, not just at t=0 (ADR-0017 addendum, Giannis V2)
Distinct from the frame-0 pitfall above: frame 0 can pass the face check and the video can still fail the hook window if a LATER overlay blacks out the face. Root-caused `dF0Rr2C0Msc` (Giannis V2, "A Ferrari Costs $1.1M", 37.1% stayed — worst on record until this was diagnosed): `pipeline/giannis/render_giannis_v1.py` composited full-canvas (`scale=1080:1920` + `overlay=x=0:y=0`, not a corner insert) Pexels b-roll at t=1-3s, 5-7s, and 8-10s, replacing Giannis's face with a static stock clip (watch/art-easel/mansion) for 6 of the first 10 seconds across 3 separate blackouts. The retention curve confirms the mechanism exactly: relative retention holds near-peak through t≈4.5s then falls off a cliff across t=5-9s — precisely the 2nd/3rd blackouts. The existing rule ("first overlay must land ≤t=2s") was technically satisfied and did not catch this, because it implicitly assumed "overlay" means a small supplementary graphic layered over a still-visible speaker, not a full-canvas substitution. This exact pattern also existed in `render_bacsihai_v3.py`/`v4.py` (one instance at literally t=0) but is absent from every current script (`bacsihai_v5+`, all `hardknocks_v*`/`aiwork_v*`) — already abandoned in practice via ADR-0016's zoompan+corner-overlay approach, but never explicitly banned until now. Rule: within the entire 0-10s hook window, any Pexels/value-add overlay must be a partial/corner composite that keeps the face visible — never a full-canvas overlay that removes the face from view, however briefly. Does not apply past t≈10s, where the standing 3-source-combo Pexels b-roll convention still holds.

### Hook caption sync and cadence (ADR-0018)
Benchmarked 6 independently viral Shorts (`docs/research/hook-benchmarks-2026-07/REPORT.md`) — all 6 shared two patterns not previously encoded as rules here:
- **Caption sync**: burned-in caption must be visible by t=0.2s (not delayed for a "clean" shot), updating every ~1-2s in short 2-5 word bursts synced to speech, with one keyword per burst visually emphasized (color/weight distinct from the rest).
- **Cadence**: at least one visual change (cut, zoom, new overlay, or continuous on-screen motion) every 1-2s within the hook window — tighter than the general 2-3s "2-Second Rule" (ADR-0016), specifically for the 0-5s hook region.
- **Show, don't just tell**: pair any spoken claim (wealth, results, a number) with simultaneous visual evidence (prop, environment, action) rather than narration alone — in the benchmark set, the verbal claim and its visual proof landed in the same beat, not sequentially.
Caveat: burst timing above was measured on English interview speech; Vietnamese TTS narration paces differently, so derive burst duration from actual TTS word-timing output per video, not a copy-pasted constant — verify legibility, not just retention theory, when tuning this for Bác sĩ Hải / Giảm Cân Healthy.

### Guide-derived craft verification is blocking (ADR-0034)
- Early SFX must land within t=0-1s; add an arrow/pointer/animated annotation when the focal target is ambiguous.
- Caption bursts use the Caption Style Profile from `CONTEXT.md`: Komika Axis for English, Bangers for Vietnamese, 2-5 words, one animated/emphasized keyword, normal center at 55-65% frame height. ffmpeg values come from the checked-in calibration artifact, never literal CapCut `16/60` units.
- Still-image entrances/exits and purposeful transitions receive matching SFX.
- A custom on-brand Mid-Roll Triple CTA begins at t=38-42s and asks for Like, Subscribe and Comment.
- A non-obstructive moving watermark changes position over the timeline.

### Clip Curation Edit must pass the Transformative Gate
Video Type #7 (Clip Curation Edit) uses real footage from Source Channel — unlike the 6 animation types (zero-footage). Before upload, every Clip Curation Edit MUST pass all 3 Transformative Gate rules: (1) commentary track required, (2) min 2 value-adds from [fact-check callout, data viz, source citation, multi-source mashup, animated annotation, counter-argument], (3) cut ≤50% source duration + each clip <15s. Uploading a clip edit that fails the gate = copyright strike risk. Attribution is intentionally dropped per user decision.

### ffmpeg drawtext silently drops text containing a literal "%" (aiwork v1)
`drawtext`'s default `expansion=normal` parsing treats a bare `%` as a template-escape trigger (e.g. `%{pts}`) and silently drops the rest of the string when it isn't one - the filter still exits 0, with only a buried "Stray %" warning in stderr, so a caption can vanish from a render with no visible top-level error. Any caption/overlay text that may contain a real percentage (e.g. "25%") needs `expansion=none` added to its `drawtext` filter args. Doubling to `%%` did not reliably fix this in testing - use `expansion=none` instead. First hit in `pipeline/aiwork/render_aiwork_v1.py` (percentage-heavy captions); grepped `render_bacsihai_v5.py`/`render_hardknocks_v1.py` and confirmed neither has this problem today since their captions never contain a literal `%`.

### System fonts used in this repo lack some Unicode glyphs (aiwork v1)
`Helvetica.ttc`/`HelveticaNeue.ttc` (the only fonts used across this repo's render scripts) don't include every Unicode symbol - e.g. the arrow `→` renders as a missing-glyph "tofu" box. Stick to ASCII in `drawtext` caption content (e.g. `->` instead of `→`); verify visually via a rendered frame before assuming a symbol will show up.

### mlx_whisper word tokens already carry their own leading-space semantics (hardknocks v4)
When reconstructing caption text from `mlx_whisper` `word_timestamps=True` output, do not rejoin words with `" ".join(w["word"].strip() for w in words)` — each word token already carries its own correct leading space (or lack of one), e.g. `' 10'`, `',000.'` (no leading space, meant to attach directly to the prior token), `' But'`. Stripping every token and rejoining with a space inserts a stray space before punctuation-attached continuations, rendering `"10 ,000. But if"` instead of `"10,000. But if"`. Fix: concatenate the raw word strings and strip once at the ends — `"".join(w["word"] for w in words).strip()`. First hit in `pipeline/hardknocks/render_hardknocks_v4.py`'s `auto_bursts()` helper (auto-split dialogue captions from word timestamps); caught by the mandatory Stage 4 frame-check, not by reading the code.

### ffmpeg scene-detect (`select='gt(scene,T)'`) misses cuts between visually-similar distinct clips
Confirmed while analyzing an external video (`docs/research/800m-view-case-study-2026-07-11/REPORT.md`, `viral-video-analysis` skill's `extract_keyframes.py`, threshold=0.3, the same scene-detect approach ported from the old `analyze_video.py`): the algorithm found ZERO scene changes across a 33-second montage that direct frame-by-frame reading confirmed contains at least 4-5 real hard cuts between completely different clips/people/locations (every ~2-3s). It only fired reliably during a segment with genuine fast camera panning/motion blur. Root cause: ffmpeg's `scene` metric is a per-pixel frame-difference score, and cuts between clips with similar overall brightness/composition (e.g. person + gun + wall-colored background, repeated across many amateur clips shot in similar settings) can score below threshold even though the content is logically a hard cut. Do not trust `scene_keyframes` alone for cut-cadence claims on montage-of-distinct-clips content — cross-check with direct frame reads at fixed intervals (the `hook_window_frames` set), same as this project's existing decision (`docs/WORKFLOW.md` Stage 0) to keep frame-0 checks as human/Claude visual judgment rather than fully automated.

### Top-100-by-likes comment sample can include bot/engagement-farming comments (viral-video-analysis, normal-vs-king v2)
Confirmed in `docs/research/normal-vs-king-pattern-2026-07-12/REPORT.md`: at least 7 comments in the top-100-by-likes set for a 418M-view video used near-identical, interchangeable templated wording ("The production quality is exactly what I needed I will definitely recommend this.", "This tutorial is very impressive I did not expect it to be this good.") — the giveaway being generic words like "tutorial"/"explanation" that don't match the actual video's content (a firefighting montage, not a tutorial). These score real likes and rank in the top 100, so sorting by `like_count` alone is not sufficient to guarantee an organic sample. Before writing the comment-psychology section (`references/comment-psychology.md`), scan the top-100 set for near-duplicate generic-praise wording across different authors/videos and exclude it from the thematic read — it isn't a signal about this video's specific content, just generic engagement-farming.

### `yt-dlp --write-comments` can hang/timeout on videos with thousands of comments (viral-video-analysis, ronaldo v1)
Confirmed while analyzing `Migd5sn-0uc` (5,800 comments, `docs/research/ronaldo-security-guard-kindness-2026-07-13/REPORT.md`): the plain `yt-dlp --write-comments --skip-download ...` command from `viral-video-analysis/SKILL.md` step 2 hung past a 2-minute timeout twice in a row on this video, while the same command completed in seconds on prior, lower-comment-count videos in `docs/research/hook-benchmarks-2026-07/`. Root cause is YouTube's comment-pagination continuation API, which `yt-dlp` walks page-by-page — a 5,800-comment video requires far more continuation requests than a few hundred. Fix: pass `--extractor-args "youtube:max_comments=300,300,100,100"` (or similar bounded values) to cap pagination, and run the fetch in the background (`run_in_background`) rather than blocking on it. This does mean the resulting "top 100 by likes" is only the top 100 *of the fetched subset*, not of the full comment pool — flag that explicitly as a Limitation in the report (see the Ronaldo report's Limitations section) rather than presenting it as equivalent-strength evidence to a full top-100 read.

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

### YouTube Analytics API's `averageViewPercentage`/`averageViewDuration` are NOT a reliable proxy for Studio's Shorts "Stayed to watch" — not a code bug, not a fixed bias (fetch-metrics v1, 3 confirmed cases, revised 2026-07-13)
**Revises an earlier version of this entry** that claimed a "confirmed +5-6pp positive bias" after 2 data points — a 3rd real Studio screenshot disproved that. All 3 confirmed cross-checks: Dangote (`ChWLcE3OYpA`) API 57.6% vs Studio 51.6% (+6.0pp); `dHDpDXSIAkA` API 59.84% vs Studio 54.1% (+5.74pp); `Mw7jeR6R6iE` API 36.74% vs Studio 43.6% (**-6.86pp — opposite direction**). AVD gaps are similarly inconsistent (+7s, +1s, -3s). There is no fixed-magnitude, fixed-direction correction factor — don't estimate a "corrected" number from the API value, ever.

Verified this is **not a code bug**: `src/platforms/youtube-analytics.ts`'s query is correctly scoped (`dimensions=video`, `filters=video==<id>`, metrics `views,averageViewDuration,averageViewPercentage`, a `startDate` predating any video's upload). Per Google's official metric docs (developers.google.com/youtube/analytics/metrics), these two metrics are generic long-form-video metrics that have excluded looping-clip traffic since 2021-12-13 — they are simply a **different metric family** from whatever proprietary calculation YouTube Studio's Shorts-specific "Stayed to watch" panel uses internally, which has no documented public Analytics API equivalent. This is the same root cause ADR-0025 already flagged for `Stayed (Engagement/Hook)`/`Swiped Away` (Known Limitation section) — now confirmed (3 data points) to extend to `Stayed (Retention/Overall)` too.

Practical rule: treat any `fetch-metrics`-populated `Stayed (Retention/Overall)`/`AVD` value as a rough API-only signal, not ground truth, and never back out an estimated "real" number from it. If the user supplies a real Studio screenshot for a video, that's the only way to know the true number — overwrite with it (see fetch-metrics's Studio Cross-Check Correction section). See `docs/adr/0025-youtube-analytics-metrics-fetcher.md`'s 2026-07-13 addenda (all three).

**Ruled out "it's just reporting lag" as the explanation** (checked directly, not assumed): re-fetching `dHDpDXSIAkA` twice in the same session returned byte-identical numbers both times — if lag were "catching up," the number would have moved. Also, lag would mean the API undercounts recent activity (always reads *lower* than Studio's fully-processed truth), but 2 of the 3 confirmed cases read *higher*, not lower. Lag doesn't produce a metric that overshoots ground truth. **Also tested `engagedViews`** (a real, valid metric requiring the `creatorContentType` dimension — plain `dimensions=video` gives a `500 Internal error`) as a candidate closer match, since Studio's Engagement tab has a literal "Engaged views" tile: `dHDpDXSIAkA` API 516 vs Studio 634, `Mw7jeR6R6iE` API 113 vs Studio 426 — same name, different values, doesn't help either. Also confirmed via live 400 responses that `shownInFeed`/`swipedAway`/`uniqueViewers` are not valid metric identifiers on this API. Don't re-try either of these paths expecting a different result — see ADR-0025's 2026-07-13 3rd addendum for the full detail.

### A raw segment clip reused as a backdrop still carries the source's own burned-in captions (hardknocks b1/ruiz rebuild)
Confirmed in `render_hardknocks_b1_ruiz.py`'s continuous-3-act rebuild: `make_ending_backdrop()` built the ending's continuously-playing backdrop by looping a raw segment clip (`segments/02_house_claim.mp4`) directly, then applying `setpts` (slowmo) + `eq` (desaturate) + `boxblur`. This did NOT remove School of Hard Knocks' own pre-existing burned-in captions (e.g. "and I've invested...") already present in the downloaded source video itself — they played straight through, underneath our own score/evidence cards, for the entire ending. Root cause: `mix_and_caption()` already covers this exact bottom band with a `drawbox=x=0:y=1650:w=iw:h=270:color=black@1.0:t=fill` before burning in this project's own ASR-derived captions on the interview section, but that blackout lives only in that one function — any other step that reuses a raw segment clip (not the already-captioned/blacked-out one) as a base for further compositing needs to re-apply the same drawbox, or the source's own captions resurface. Caught only by extracting and visually reading frames at the actual ending timestamps, not by trusting the filter graph. Rule: any time a raw segment clip (pre-`mix_and_caption`) is reused for a NEW purpose later in a renderer (backdrop, freeze-frame, loop, etc.), re-check whether that source video has its own pre-existing on-screen text and re-apply the same blackout if so — don't assume "raw" means "clean."

### ffmpeg overlay: shifting a short PNG input's own PTS forward (instead of looping it for the full timeline + `enable=`) silently produces no overlay, no error (hardknocks b1/ruiz rebuild)
Confirmed in the same rebuild's `composite_inline()`: two inline verify badges were built as `-loop 1 -t {ev.duration} -i {badge.png}` (a short stream, only as long as the badge should be visible) and then time-shifted into position via `setpts=PTS-STARTPTS+{at}/TB`, gated by `overlay=...:enable='between(t,{at},{end})'`. This produced a fully valid `ffmpeg` command that exited 0 with no warnings — but the badge never appeared anywhere in the rendered video, at any timestamp. Root cause: shifting a short stream's own PTS to start later leaves the overlay filter with literally no frame from that input to composite for the entire span before the shift point; unlike the working pattern used everywhere else in this same file (`build_ending()`'s row/evidence/CTA cards, the identity tag in `apply_narration_bridges()`), which loop the PNG input for the *entire* base timeline's duration and rely purely on the overlay's own `fade=`/`enable=between(...)` clauses to gate visibility. Caught only by extracting frames at the exact calculated timestamps and seeing plain footage with no badge — the ffmpeg log gave zero indication anything was wrong. Rule: for any time-windowed PNG overlay, always loop the input for the full base-video duration and gate visibility via the overlay's `enable=`/`fade` args; never shift a short-duration input's own PTS to position it in time.

### A `drawbox` blackout painted for one purpose can leave a permanent empty black band if nothing downstream ever fills it (hardknocks b1/ruiz rebuild, footer fix)
Confirmed in `render_hardknocks_b1_ruiz.py`'s Revision 2: `mix_and_caption()` drew `drawbox=y=1650:h=270:color=black@1.0:t=fill` across the bottom ~14% of every frame, for the *entire* video, specifically to hide School of Hard Knocks' own pre-existing burned-in captions before burning in this project's own ASR-derived captions higher up the frame. Because this project's captions render well above that band, nothing ever fills it — the result is a flat black strip along the bottom of literally every frame, present throughout the whole video (not just wherever the original problem was), easy to miss during QC if you're only checking for gross defects (full black frames, freeze) rather than "is any region of every single frame permanently empty." Caught only when the user explicitly flagged a black "footer" after an otherwise-passing QC pass; confirmed with a row-by-row pixel brightness scan (`img[y].mean()` per row) rather than eyeballing thumbnails. Rule: any `drawbox`/blackout added to hide something must be checked for whether anything downstream actually paints inside that same region — if not, don't blacken it; crop it off and zoom back up to refill the frame instead (see next entry for the correct way to do that), or reconsider whether the blackout is needed there at all.

### Non-uniform `crop` + `scale` back to the original dimensions silently distorts the aspect ratio (hardknocks b1/ruiz rebuild, footer fix)
A same-session first attempt at removing the black-footer band above used `crop=1080:1650:0:0,scale=1080:1920` to cut the bottom band off and refill the canvas — this scales width by 1080/1080=1x but height by 1920/1650=1.16x, a **non-uniform stretch** that subtly distorts every face/object (taller and thinner) without any error or obviously "wrong" look at a quick glance. The correct pattern (used in the real fix, `scaled_crop()`): crop the unwanted band off, `scale` **both** dimensions by the same recovery factor (e.g. target_h/cropped_h) to a wider-than-target canvas, then `crop` the excess width back off centered — e.g. `crop=1080:1650:0:0,scale={round(1080*1920/1650)}:1920,crop=1080:1920:({round(1080*1920/1650)}-1080)/2:0`. Whenever a crop removes pixels and a subsequent `scale` targets the original W:H to "refill" the frame, verify the two dimensions are being scaled by the *same* factor — if not, it's a stretch, not a zoom.

### `adelay` before `loudnorm` corrupts loudness measurement -- always normalize loudness BEFORE delaying a clip into position (hardknocks b1/ruiz, VO-too-quiet fix)
Confirmed in `apply_narration_bridges()`: the narrator VO filter chain applied `adelay={delay_ms}|{delay_ms}` (prepending several seconds of silence to position a short VO clip at its correct timestamp in a longer timeline) **before** `loudnorm=I=-16:TP=-1.5:LRA=10`. This measurably wrecks loudnorm's result: `loudnorm` integrates loudness over its *entire* input, so with a long silent prefix attached, it measures loudness across [silence + speech] instead of the speech alone, and its gating/lookback logic responds by under-amplifying badly. Reproduced side by side on the same 2.32s clip with a 5.2s delay: adelay-then-loudnorm → **-26.9 LUFS** (11dB short of the -16 target, audibly "almost inaudible" against the ducked dialogue bed); loudnorm-then-adelay → **-16.4 LUFS** (on target). The bug was silent (no ffmpeg warning/error) and didn't show up when testing the VO clip in isolation (without the delay) — it only appeared once actually rendered into the full timeline, and even then only in clips with `adelay > 0` (the very first beat, with no delay, was unaffected, which is why the defect looked like "some segments are fine, others aren't" rather than a uniform bug). Caught only by scanning the actual final mixed audio in fine time-slices (`volumedetect` in 0.25s steps) and noticing an unexplained loudness dip that didn't show up when testing the source clip alone. Rule: whenever a filter chain both delays a clip into position (`adelay`) and normalizes its loudness (`loudnorm`), always run `loudnorm` first, then `adelay` — never the reverse.

### `loudnorm`'s `TP` (true-peak) ceiling caps achievable loudness on high-crest-factor clips -- a `TP=-1.5` clip with an -8dBTP raw peak will undershoot `I=-16` regardless of single-pass vs. two-pass mode (hardknocks b1/ruiz, VO-too-quiet fix)
Confirmed across all 4 narrator VO clips in `render_hardknocks_b1_ruiz.py`: each raw Qwen-TTS recording has a large peak-to-loudness ratio (crest factor) -- e.g. one clip measured -25.3 LUFS integrated but only -8.2 dBTP peak, a ~17dB crest factor from a single sharp transient. Loudnorm won't raise a clip's gain past the point where its peak would exceed the `TP` ceiling, so on a clip like this it stops well short of the `I` target and stays there -- verified this happens **identically** whether you use loudnorm's default single-pass "dynamic" mode or a proper two-pass "linear" mode with measured input stats (tried both; both landed at exactly the same -18.5 LUFS on the same clip, an initially confusing result that ruled out "single-pass inaccuracy" as the cause). The actual fix: apply a mild `acompressor` (e.g. `threshold=0.1:ratio=4:attack=5:release=100:makeup=1`) *before* `loudnorm` to reduce the crest factor first, so loudnorm can reach the target loudness without ever needing to touch the peak ceiling -- verified this brought all 4 clips within 0.8dB of the -16 LUFS target. If a two-pass `measured_I`/`measured_TP` diagnostic run reports a `target_offset` that doesn't budge between dynamic and linear mode, suspect the TP ceiling as the actual constraint, not the normalization algorithm.

### Hard-concatenated segments need their own audio fade in/out, or every cut sounds like a truncated, jammed-together splice (hardknocks b1/ruiz, cut-transition fix)
Confirmed in `render_hardknocks_b1_ruiz.py`: `build_base()` concatenates independently-rendered segments with `-f concat -c copy` (no crossfade), and each segment's own audio chain (`render_segment()`) ended with a flat `atrim`, no fade. Result: at every cut, whatever word was still naturally decaying got chopped off at full volume with zero taper, and the next segment's dialogue started immediately at full volume with no lead-in -- user-reported symptom was "the tail sound isn't clear and is noticeably quieter, and cuts feel jammed together with no pause." Fix: append a short `afade=t=in:st=0:d=0.12` and `afade=t=out:st={duration-0.20}:d=0.20` to each segment's own audio filter chain in `render_segment()`, BEFORE concatenation. This only reshapes the amplitude envelope within each clip's existing duration -- it does not add or remove any time, so video stays frame-accurate in sync; only the audio eases through the join. Verified via a fine 0.1s-step `volumedetect` scan straddling each cut: post-fix shows a clean ramp-down to near-silence right at the join and a ramp-back-up into the next segment, instead of a flat full-volume plateau on both sides with an instant jump between them. This applies to ANY renderer in this repo that hard-concatenates independently-rendered segments (not just this file) -- always fade each segment's own audio at both ends before concat, even when the video cut itself is a deliberate hard jump cut (this project's Active-Speaker Reframing style) with no video-side fade.

### Action space explosion
Under Plateau-Gated Cadence there is no honest fixed calendar convergence estimate; fragmentation across three lanes per vertical may slow inference further because channel history is a confounder. Don't expect early convergence.

## Boundaries

### Always
- Follow HEIT structure (Hook → Explain → Illustrate → Teach)
- Copy proven viral formats, repackage with variations
- Wait 48h before fetching YouTube Analytics (stable data)
- Apply Retention Techniques (sound design, zoom, pattern interrupt) to EVERY video — it's base quality, not optional
- Let MAB select variants autonomously — don't override its choices manually
- Verify video specs before upload (9:16, 50-75s, MP4 H.264 + audio)
- Verify the full ADR-0034 craft/metadata package and ADR-0035 lane eligibility before upload
- Log every decision (variant selected, epsilon, scheduler pass, channel/lane) for post-hoc review

### Ask First
- Adding a new animation format (requires research + ADR)
- Adding a fourth niche/vertical beyond the three confirmed (finance/English ADR-0001/0004, health/Vietnamese ADR-0019, AI-education/English ADR-0020)
- Changing epsilon schedule (affects exploration strategy)
- Spending money on paid tools/APIs
- Adding a new platform (TikTok, Instagram)

### Never
- Post a new Short shorter than 50s or longer than 75s
- Publish to a Destination Channel before its previous Short reaches Distribution Plateau, except ADR-0035's first-viral seven-day exception
- Delete a No-Feed original merely to reset distribution; retain it and create a Material Revision for the next eligible lane
- Upload the same Short or revision simultaneously to multiple channels
- Paste raw affiliate links in descriptions
- Invent "original" formats from scratch (copy what works)
- Reset MAB state mid-cycle (lose learned rewards)
- Fetch metrics before 48h (noisy data → bad decisions)
- Skip logging autonomous decisions (no audit trail = can't debug bad strategy)
- Create or expand unit tests for current Python video renderers (`test_render_*.py`) unless the user explicitly asks for them; old plans/specs/tests that used TDD are historical, not current policy
- Proactively change or rerender a completed video after handoff; wait for explicit revision feedback from the user

## Testing & Media Verification

The commands below belong only to the future TypeScript autonomous system; they are not completion gates for today's per-video Python/ffmpeg production scripts.

| Area | Check | Policy |
|------|-------|--------|
| Current `pipeline/<project>/render_*.py` | Render the actual MP4, then run ffprobe/spec validation, full decode, final ASR, black/freeze/silence/audio checks, and manual frame/contact-sheet review | Required media QC; no new renderer unit test unless explicitly requested |
| Existing `test_render_*.py` files | Leave untouched unless the user asks to change/remove them | Legacy artifacts; do not copy them into the next video version and do not require them for handoff |
| Future TypeScript unit tests | `npm test` | Applies when the autonomous TypeScript system actually exists |
| Future TypeScript integration tests | `npm run test:integration` | Applies to the future script → render → output pipeline |
| Future TypeScript spec validation | `npm run test:specs` | Applies to future automated output enforcement |

For current video production, the deliverable is the verified media artifact, not test coverage. A renderer implementation is complete when the real output passes media QC and the production doc is complete.

## Architectural Policies

- **Autonomous loop is stateful**: MAB state (`data/mab_state.json`) persists across cycles. Deleting = restart from scratch.
- **Video spec enforcement**: `video-assembly.ts` is the single source of truth for output specs. No other layer may set video specs.
- **Channel topology**: each vertical has exactly three Destination Channels in a strict round-robin Channel Pool; every lane is phone-verified and aged ≥3 weeks before its first upload.
- **Publishing cadence**: eligibility is state-based, not calendar-based. Persist 24h view increments, two consecutive plateau observations, Shorts Feed share, lane order and Channel Burn State.
- **Metrics collection is async**: metrics fetched 48h+ after upload (YouTube Analytics lag). Never fetch before 48h or data is noisy.
- **Metrics data is append-only**: `video_metrics` table never mutates. Each fetch writes new row with timestamp.
- **Chrome profile is upload auth**: No OAuth flow or API key for upload. Each Destination Channel reuses its own logged-in browser identity; Analytics credentials remain channel-scoped.
- **MAB rewards are cumulative**: Each variant's reward = running average of AVD across all samples. More samples = more confident reward estimate.

## Ngôn ngữ khi trao đổi, giao tiếp: Tiếng Việt
