# Shorts

Evidence-led media system: prove market demand, build authority assets, then use 9:16 Shorts as a discovery and experiment layer. Render/QC proves manufacturing quality, not product-market fit or virality.

Verticals: finance/money-making, health/longevity, and AI education. MONEY BLINDSPOT is the finance authority brand and follows flagship-first strategy.

## Context Loading — Progressive Disclosure

Do not recursively read the repository. Start here, locate files, then load only the context required by the task.

| Area | Read next |
|---|---|
| Strategy / next idea | `docs/AGENTS.md`, `docs/WORKFLOW.md` Stage -2, active file in `docs/strategy/` |
| Short production / revision | `pipeline/AGENTS.md`, matching `docs/production/*.md`, relevant ADR only |
| Renderer, TTS, captions, audio, QC | `pipeline/AGENTS.md`, relevant section of `docs/agent/media-pitfalls.md` |
| Metrics / experiments / publishing cadence | `docs/experiments/`, `docs/agent/strategy-analytics-pitfalls.md` |
| Stateful data | `data/AGENTS.md` |
| Local media | `output/AGENTS.md`; inspect only the current project/version |
| Domain vocabulary | Search `CONTEXT.md` for the term; do not load the full glossary by default |
| Spike / experiment | `spikes/AGENTS.md`, then that spike's README |

The nearest scoped `AGENTS.md` adds local workflow. Root policy wins over historical plans, production docs, research notes, renderers, and older ADRs when they conflict.

## Active Strategy — Blocking

- Market selection precedes production. Every candidate starts at `docs/WORKFLOW.md` Stage -2; no download, TTS, EDL, asset search, renderer, or polish before it passes.
- MONEY BLINDSPOT is flagship-first. Publish the evidence-led long-form authority asset first; every new Short must be a derivative with a Related Video destination. Stop unrelated standalone finance Shorts unless the user changes strategy.
- Demand evidence outranks internal scoring. Comparable public winners, current attention, and cold-viewer comprehension select ideas; hook/editorial/QC scores only enforce a quality floor.
- Begin each production cycle with at least 10 lightweight ideas, select 3 package hypotheses, and advance only 1 concept to deep production.
- Fail closed. `missing`, `unverified`, `unresolved`, or `failed` at any blocking gate means STOP, not “upload and audit later.”
- Copy proven narrative/format mechanics and repackage them; do not invent an unproven format from scratch.

## Repository Architecture

```text
docs/strategy + research + adr
              ↓ market and decision evidence
docs/WORKFLOW.md + docs/production/<video>.md
              ↓ gated production contract
pipeline/<project>/*.py  →  output/projects/<project>/{source,clips,final}
              ↓ publish and learn
data/uploads + docs/experiments + src/platforms/youtube-analytics.ts
```

| Path | Responsibility |
|---|---|
| `docs/` | Policy, workflow, decisions, evidence, and production records |
| `pipeline/` | Current manual/semi-manual Python + ffmpeg manufacturing tools |
| `output/` | Large local media grouped by project; mostly intentionally ignored by Git |
| `data/` | Durable registries, MAB/target state, narrator profiles, and upload metadata |
| `src/platforms/` | TypeScript YouTube Analytics automation |
| `assets/` | Versioned fonts and rights-managed sound assets/metadata |
| `scripts/` | Cross-project executable artifact verification |
| `spikes/` | Self-contained experiments; never a production import source |

## Production Baseline

- Output: 1080x1920, 50–75 seconds, MP4 H.264 with audio. Final names use `yyyy-mm-dd-<name>.mp4`.
- Download production source footage at the highest available quality, targeting 2160p/4K; never accept a silent fallback to 720p.
- Every Short combines source footage, animated/proof overlays, and relevant b-roll. Motion is not evidence: every visual change must advance information.
- Hook: moving footage at frame 0, caption visible by t=0.2s, 2–5 word bursts, one emphasized keyword, visual change every 0.8–1.5s during 0–5s, and simultaneous visual proof for spoken claims.
- Apply ADR-0034/0036 baseline to every Short: early SFX within 0–1s, calibrated captions, no unexplained 5–10s gap over 3s or body gap over 6s, Mid-Roll Triple CTA at 38–42s, moving watermark, and loop-payoff closure.
- Before asset search, lock ADR-0038 Sonic Intent and build an event-bound SFX ledger. Every retained cue resolves to a rights-cleared manifest asset and passes exact-final full-mix review.
- English material revisions that regenerate TTS use the profile selected by `data/narrator-voices/default.json`. Never silently fall back to Edge TTS. Internal narrator approval does not clear commercial voice rights.
- After exact-final media QC, run structured Codex review and address timestamp-supported findings. Target editorial score ≥98, maximum 3 full rerender rounds per final revision; the score is not virality evidence.
- Clip Curation Edit must include commentary, at least 2 approved value-adds, use at most 50% of the source, and keep each source clip under 15s.

## Verification by Change Type

| Change | Required evidence |
|---|---|
| Current `pipeline/<project>/render_*.py` | Render the real MP4; ffprobe/spec check, full decode, final ASR, black/freeze/silence/audio checks, and manual frames/contact sheet |
| TypeScript in `src/` | `npx tsc --noEmit` plus the relevant real command |
| Documentation / paths | Markdown/path link check and targeted search for stale old paths |
| Data schema/state | Read all consumers first; verify append-only/history behavior |

Current Python renderers are one-off production tools. Do not create or expand `test_render_*.py` or apply TDD unless explicitly requested. Existing legacy tests remain untouched.

## Durable Data and Publishing

- Never delete or reset `data/mab_state.json`, `data/tracked_videos.csv`, `data/source_videos.csv`, `data/targets/`, `data/uploads/`, narrator profiles, or `data/video_metrics.db` as cleanup.
- YouTube Analytics is unstable before 48 hours and may remain unindexed longer. Empty API results mean retry later, not zero engagement.
- API `averageViewPercentage`, `averageViewDuration`, and `engagedViews` are not reliable substitutes for Studio's Shorts-specific Stayed-to-Watch metrics. Never apply a correction factor; real Studio screenshots win.
- Each vertical uses three phone-verified, at-least-three-week-aged Destination Channels in strict round-robin. Publish only when the next lane is eligible under ADR-0035.
- Never delete a No-Feed original to reset distribution; retain it and create a Material Revision for the next eligible lane. Never upload the same revision simultaneously to multiple channels.
- Metrics observations are append-only. Log variant, epsilon, scheduler result, channel/lane, upload identity, and evidence source.

## Boundaries

### Always

- Communicate with the user in Vietnamese; keep code, identifiers, CLI output, and project docs in English.
- Gather context by filename/search first, trace definitions and consumers, and read the nearest scoped `AGENTS.md`.
- Preserve completed videos after handoff; wait for explicit revision feedback before rerendering.
- Treat `.gitignore` as storage policy, not permission to delete valuable media.

### Ask First

- Add an animation format, a fourth vertical, a platform, or change the epsilon schedule.
- Spend money on paid tools/APIs.
- Delete source footage, final media, QC evidence, research evidence, backups, or stateful data.

### Never

- Proceed past Stage -2 or another failed blocking gate.
- Use an internal score as market-demand evidence.
- Publish outside the 50–75s spec or before lane eligibility.
- Paste raw affiliate links in descriptions.
- Commit, push, rewrite Git history, expose secrets, or edit `.env` unless explicitly requested.
- Bulk-read `output/`, `docs/research/`, or historical production files without first narrowing the task.

## Detailed On-Demand References

- `docs/agent/media-pitfalls.md`: ffmpeg, crop/scale, captions, overlay timing, loudness, delayed audio, hard-cut fades, and QC failures.
- `docs/agent/strategy-analytics-pitfalls.md`: metrics lag/mismatch, MAB state, comment sampling, research download limits, and action-space effects.
- `CONTEXT.md`: domain glossary and accepted vocabulary.
- `README.md`: task-oriented repository map.