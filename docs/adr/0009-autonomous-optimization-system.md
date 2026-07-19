# Autonomous Optimization System

> **Partial supersession (2026-07-19):** ADR-0035 replaces this ADR's fixed `6 videos/day × 3 days`, 18-video cycle, single-channel scheduler and fixed five-day loop with Plateau-Gated three-channel rotation. The MAB, Chrome-upload and 48h-minimum-metrics principles remain accepted; ADR-0025 remains authoritative for the real Analytics implementation and metric limitations.

**Context**: Shorts project hiện tại = semi-manual: agent generates videos → human uploads + reviews metrics → human decides next AB test. Bottleneck = human-in-loop cho upload + metric analysis. User request: "cho quyền truy cập YouTube channel → system tự upload + measure retention + research + improve."

**Decision**: Build autonomous optimization system với 3-day cycle: (1) upload 18 videos theo MAB-selected variants, (2) wait 48h cho YouTube Analytics stable metrics, (3) analyze AVD + retention graphs → adjust strategy → repeat. Không cần human input sau initial setup.

**Architecture**:
```
┌─────────────────────────────────────────────────────────┐
│              3-DAY OPTIMIZATION CYCLE                    │
│  (Day 1-3: upload) → (48h wait) → (analyze + adjust)    │
└────────────┬────────────────────────────────────────────┘
             │
    ┌────────▼────────┐
    │  MAB STRATEGY    │ ← Epsilon-greedy: 50-50 → 20-80 after 54 videos
    │  (variant picker)│   Action space: 7 types × 3 hooks × 9 value-adds
    └────────┬────────┘
             │ (select 18 variants for 3 days)
    ┌────────▼────────┐
    │ CONTENT PIPELINE │ ← Existing: script gen → TTS → render → assembly
    │  (render videos) │
    └────────┬────────┘
             │ (18 MP4 files ready)
    ┌────────▼────────┐
    │ CHROME UPLOADER  │ ← Playwright automation, logged-in profile
    │  (6 videos/day)  │   Title, description, tags auto-generated
    └────────┬────────┘
             │ (videoId returned)
    ┌────────▼────────┐
    │  48H WAIT        │ ← YouTube Analytics lag: metrics unstable <48h
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ METRICS FETCHER  │ ← YouTube Analytics API (no auth, uses Studio export)
    │  (AVD + graph)   │   Primary: AVD %, Secondary: CTR, views
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ ANALYZER         │ ← Detect key moments (dips/peaks), rank variants
    │  (improve logic) │   Update MAB rewards, adjust epsilon
    └────────┬────────┘
             │
             └──────► Loop back to MAB (cycle N+1)
```

**Key components**:
1. **MAB Strategy** — Multi-Armed Bandit epsilon-greedy:
   - Start ε=0.5 (50% explore random, 50% exploit top-3)
   - After 3 cycles (54 videos), decay ε=0.2 (20-80)
   - Action space: existing AB variables (video type, hook type, value-add type, title pattern)
   - Reward: AVD % (average view duration)

2. **Chrome Uploader** — Playwright automation:
   - User đăng nhập YouTube vào Chrome profile cố định (e.g., `~/Library/Application Support/Google/Chrome/Profile Shorts`)
   - Script opens profile → navigates youtube.com/upload → fills form → publishes
   - No OAuth flow, no API quota burn (quota reserved for analytics)

3. **Metrics Fetcher** — 48h wait + YouTube Analytics:
   - Wait 48h after last upload (not 24h — safer for stable data)
   - Fetch: AVD %, CTR, views, retention graph (per-second curve)
   - Store in SQLite: `video_metrics` table

4. **Analyzer** — Key moments + variant ranking:
   - Parse retention graph → detect dips (boring sections), peaks (viral moments)
   - Rank variants by AVD → update MAB rewards
   - Extract patterns: "Hook type X + Value-add Y = high AVD"
   - Feed insights back to content pipeline (e.g., "zoom punch at 3s works")

**Why not pure RL**: RL papers (ARGen, LPM 1.0) focus on video generation (text → pixels), not content strategy optimization. MAB simpler, proven for discrete action spaces, faster to implement.

**Why Chrome automation vs YouTube API upload**: API upload burns 1600 quota per video (6 videos = 9600/10k daily limit). Chrome automation = zero quota, save quota for analytics fetching. Trade-off: more brittle (YouTube UI changes break script), but quota-efficient.

**Why 3-day cycle**: Balance between speed (daily = noisy, 18 videos not enough coverage) and responsiveness (weekly = miss trends). 3 days × 6 videos = 18 videos = reasonable sample per cycle.

**Why 48h wait**: YouTube Analytics API lag documented as "24h+". Research shows metrics unstable <48h. 48h = safer, accept 2-day delay for stable data.

**Why AVD primary metric**: Codebase (AGENTS.md line 43) + web research (2026 algorithm: AVD = king for Shorts). CTR secondary (thumbnail test), views tertiary (vanity metric).

**Trade-offs**:
- Autonomous = no human oversight → bad strategy can waste 54 videos before correction. Mitigation: start ε=0.5 (explore broadly), log all decisions for post-hoc review.
- Chrome automation = brittle vs API upload = quota-hungry. Pick Chrome (quota more valuable for analytics).
- 3-day cycle = slower than daily but more stable. Accept 5-day loop (3 upload + 2 wait) for better data quality.

**Alternatives considered**:
- Pure A/B test (current manual approach): requires human to design experiments, slow iteration. Rejected: doesn't scale to 189 combos (7×3×9).
- Pure RL (policy gradient): overkill for discrete actions, needs more data, harder to debug. Rejected: MAB simpler + proven.
- Daily cycle: 6 videos/day too small sample, metrics noisy. Rejected: 3-day better.

**Implementation phases**:
- Phase 1 (current PR): MAB + Chrome uploader + metrics fetcher
- Phase 2: Analyzer key moments → inform content pipeline
- Phase 3: Multi-platform (TikTok) when YouTube stable

2026-07-04

## Addendum (2026-07-12): Metrics Fetcher corrected — OAuth, not "no auth, uses Studio export"

The Metrics Fetcher line above ("YouTube Analytics API (no auth, uses Studio export)") was
stale/self-contradictory — an API call inherently needs auth, and "uses Studio export" actually
described a manual CSV-export workflow, not an automated one. `docs/adr/0025-youtube-analytics-metrics-fetcher.md`
builds the first real slice of this component: **OAuth (`yt-analytics.readonly` scope), one-time
interactive consent, refresh token persisted in a git-ignored `.env`** — implemented in
`src/platforms/youtube-analytics.ts`, the first real file in this ADR's target `src/`
architecture. See ADR-0025 for the full decision, including a known limitation (Shorts-specific
engagement/swipe-away and per-video CTR availability via this API is unconfirmed as of this
writing).
