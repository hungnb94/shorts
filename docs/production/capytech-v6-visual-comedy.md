# Capytech v6 — Visual Comedy Production Record

## Status

**Exact-final media QC PASS. Uploaded and public on ZapBara. The external naive-viewer Hook Gate, ADR-0035 lane eligibility, Studio wiring and made-for-kids/comment-CTA conflict were still unresolved when the public snapshot was recorded.**

| Field | Observed value |
|---|---|
| Artifact | `output/projects/capytech/final/2026-07-28-capytech_v6_visual_comedy.mp4` |
| SHA-256 | `7e4f14c23ea3c0aaad8d1643daf3ef5288967de350d39233eb653e2a10cc9cda` |
| Duration | `50.500s` |
| Video | H.264, 1080×1920, 30fps, yuv420p |
| Audio | AAC stereo, 48kHz |
| TTS / narration | None; final ASR found zero speech segments |
| QC report | `output/projects/capytech/analysis/v6_visual_comedy_qc/final_qc.json` |
| Canonical metadata | `output/projects/capytech/clips/capytech_v6_visual_comedy_work/metadata.json` |
| Paste-ready upload text | `output/projects/capytech/final/2026-07-28-capytech_v6_visual_comedy_upload.txt` |
| YouTube Video ID | [`hkxEmwLKAOw`](https://youtube.com/shorts/hkxEmwLKAOw) |
| Upload channel | ZapBara (`UCFMTbSy9rzBOenAD-U1hvhg`, `@ZapBara`) |
| Uploaded/public | `2026-07-28 15:31:42 +07` |
| Studio Analytics | [Open in YouTube Studio](https://studio.youtube.com/video/hkxEmwLKAOw/analytics/tab-overview/period-default) |
| Metrics fetch after (48h rule) | `2026-07-30 15:31:42 +07` |
| Metrics status | Not yet fetched, too early |
| Public duration | `48.301s` — `2.199s` shorter than the `50.500s` local master |
| Upload snapshot | `data/uploads/hkxEmwLKAOw.json` |

## Central Package

- Central object: a supposedly free 2050 phone charger.
- Stakes: the phone reaches 100% by draining the capybara to 0%.
- Open loop: what does the free charger take in return?
- Cold-audience anchor: low phone battery and charging.
- Factual boundary: fictional visual comedy, not a real product or prediction.

## Channel Brand

- Name: `ZapBara`
- Handle: `@ZapBara` — verified on the public channel.
- Tagline: `Tiny Capy. Big Tech Trouble.`
- Positioning: mute-first animated technology comedy for curious younger viewers.

### Channel Description

```text
ZapBara follows a curious capybara testing weird gadgets, future tech, and everyday inventions. Fast animated Shorts, visual jokes, big reactions, and endings that flip everything.
```

`ZapBara` is short, pronounceable and broad enough for future gadget, invention and three-era stories; it does not lock the channel to charging. The public upload verifies the channel name and `@ZapBara` handle.

## Public Upload Verification

- Public title and description match the canonical package exactly.
- Public availability is `public`; channel name, handle and channel ID are verified.
- A downloaded public transcode matches the local V6 master at ten sampled timestamps from 0–45s (`0.9977` mean RGB frame correlation).
- Public duration is `48.301s`, while the local master is `50.500s`. The same render is visible through 45s, but the public copy ends `2.199s` earlier; inspect the final tail in Studio if this was not intentional.
- Public category is `People & Blogs`, not the planned `Science & Technology`.
- The public metadata exposed no tags; Studio-only tags remain unverified.
- Snapshot view count `0` was observed roughly three minutes after publication and is not performance evidence.
- `capytech` / ZapBara has no configured Analytics channel alias. Do not fetch through `finance`, `health` or `aiwork` until the channel mapping/token is explicitly added.

## Scored Title Families

Scores are `/5` for cold-viewer clarity, stakes, open loop, factual accuracy and mobile-length compliance.

| Family | Candidate | Clarity | Stakes | Loop | Accuracy | Mobile | Total |
|---|---|---:|---:|---:|---:|---:|---:|
| Number | `2050 Charger Costs You 🔋😵` | 5 | 5 | 4 | 4 | 5 | 23 |
| Decision | `Use This 2050 Charger? 🔋😵` | 5 | 4 | 5 | 5 | 5 | 24 |
| Contradiction | `Free Charge, Hidden Cost 🔋😵` | 5 | 5 | 5 | 5 | 5 | **25** |
| Authority | `AI Charger Test Gone Wrong 🤖🔋` | 5 | 4 | 4 | 4 | 5 | 22 |
| Question | `Who Pays for Free Power? 🔋😵` | 4 | 5 | 5 | 5 | 5 | 24 |

The contradiction family wins because it gives a familiar object, immediate stakes and an unresolved exchange without presenting the fictional 2050 device as fact. The selected title is 27 visible graphemes and contains exactly two relevant emoji.

## Canonical Upload Package

### Title

`Free Charge, Hidden Cost 🔋😵`

### Description

```text
Free Charge, Hidden Cost 🔋😵

A capybara tests charging in 2000, 2026, and 2050—then discovers who really pays for “free” power.

#shorts #FutureTech #TechComedy
```

### Hashtags

1. `#shorts`
2. `#FutureTech`
3. `#TechComedy`

### YouTube Studio Tags

1. `future charging`
2. `tech comedy`
3. `AI animation`

### Studio Fields

- Audience: `Made for kids` — the creative brief explicitly targets younger children and the artifact uses child-directed anthropomorphic visual comedy.
- Video Language: `English (United States)`
- Location: `United States`
- Category: `Science & Technology`
- Synthetic/altered content disclosure: `Yes — AI-generated character footage and procedural post-production`
- Playlist: `BLOCKED — confirm whether AI Education Shorts is appropriate for child-directed tech comedy and provide the exact playlist ID`
- Related Video: `BLOCKED — current measured winner and destination lane are unresolved`
- Upload Details Template: `BLOCKED — approved template name/ID is not recorded`
- Raw affiliate link: none

## Hook Formula Applied

- Moving capybara, phone and visible `1%` state at frame zero.
- Escaping cable creates a literal unresolved problem.
- Three-era roulette establishes visual progression without narration.
- Early alarm/tick SFX lands inside the first second.
- The payoff mirrors the hook: phone 100% / capybara 0%, followed by the update resetting the phone to 1%.

## Value-Adds

- Animated arrows, X marks, adapter stack, scanner beam and dual pictogram meters.
- Era scoreboards and explicit `2000 → 2026 → 2050` progression.
- Phone/capybara pictograms make the drain relationship understandable without relying on the unintroduced character name.
- Diegetic micro-CTA rail preserves the moving scene; measured maximum CTA coverage is 7.44%.

## QC Evidence

- Full decode: PASS.
- Black/freeze/silence detector events: zero.
- Integrated loudness: `-16.03 LUFS`.
- True peak: `-1.94 dBTP`.
- Full ASR: zero segments, confirming no narration/TTS.
- 60 action-bound SFX; maximum onset gap `1.4s`.
- 29 cuts, each `1.0–2.3s`.
- No full-width black footer.
- Exact-final manual review: hook, CTA, icon-meter progression, payoff and full contact sheet PASS.

## Hook Gate Evidence

External naive-viewer evidence is **NOT RECORDED**. Agent/creator review does not satisfy Stage 0 item 6. The video was nevertheless uploaded; this gate remains unresolved in the audit record.

## Post-Upload Unresolved Items

1. External naive-viewer Hook Gate evidence is missing.
2. ADR-0035 destination lane eligibility is unresolved.
3. Playlist, Related Video and Upload Details Template are unresolved.
4. **Audience/CTA conflict:** the public audience setting is unverified. If Studio is set to `Made for kids`, YouTube disables comments and the rendered `COMMENT CHARGE` CTA cannot function. Keep the uploaded original; confirm the setting and apply a non-comment CTA to a future material revision if needed.

## What to Check at 48h

- Do not fetch before 48 hours.
- Separate distribution from creative using Shorts Feed share before judging the hook.
- Check Stayed to Watch and the 0–3s retention shape against the `<20% Swiped Away` objective.
- Inspect retention around the 2050 scan (`29–36s`), CTA (`38–42.4s`) and payoff (`42.4–48.5s`).
- Check whether the mute-first icon meters make the 100%/0% exchange legible without captions or narration.

## Post-Production Retro

### Hook Retro

- Verbal/text: no narration; the visible `1%` and escaping cable are stronger for this audience than an explanatory sentence. None found that adds stakes without slowing the hook.
- Visual: the moving cable, three-year roulette and early alarm already establish action and progression inside 0–3s. External naive-viewer evidence remains required.

### Workflow Delta

The packaging step exposed a child-directed-content conflict not previously resolved by the universal Triple CTA rule: made-for-kids videos cannot receive comments. The workflow now requires an audience-specific CTA audit; this upload preserves the unresolved decision in its snapshot rather than treating the Comment CTA as valid by default.
