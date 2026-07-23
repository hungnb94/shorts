# HardKnocks V15 — Theragun Clarity Remake

## Status

| Field | V15A | V15B |
|---|---|---|
| Production | Complete | Complete |
| Render date | 2026-07-23 | 2026-07-23 |
| Upload status | Uploaded/public | Not uploaded |
| YouTube Video ID | `FA7c1g4PvX0` | — |
| YouTube | https://youtube.com/shorts/FA7c1g4PvX0 | — |
| Studio Analytics | https://studio.youtube.com/video/FA7c1g4PvX0/analytics/tab-overview/period-default | — |
| Actual channel | MONEY BLINDSPOT (`UCG_yrDQF5Sj6iMTZB0KSBAA`), matches `finance` alias | — |
| Upload timestamp | 2026-07-23 23:19:36 +07 | — |
| Metrics status | Not yet fetched — wait 48h | Not applicable — not uploaded |
| Metrics fetch after (48h rule) | 2026-07-25 23:19:36 +07 | — |
| Upload gate | Upload occurred; ADR-0035 lane/Studio gate outcome not independently verified | Blocked until ADR-0035 lane eligibility and Studio settings are verified |
| Final artifact | `output/projects/hardknocks/final/2026-07-23-hardknocks_v15a_crash_created_theragun.mp4` | `output/projects/hardknocks/final/2026-07-23-hardknocks_v15b_first_patient_to_athletes.mp4` |
| Runtime | 52.233s | 63.300s |
| SHA-256 | `ea43cebea4b43efa9b8d8aac409da454866cd5037e7df6216e13c906261811e7` | `e0f7ee6619ded5ccad03932c4cd99c46fafb5502e6e6c7eee4a7ccaf6462371e` |

## Upload Log

V15A public metadata was verified from the live YouTube URL with `yt-dlp` on
2026-07-23 23:20 +07:

- Availability: public.
- Exact public timestamp: 2026-07-23 23:19:36 +07.
- Public title and description match the canonical package in this document.
- Public duration rounds to 52s, consistent with the 52.233s local artifact.
- Destination channel is MONEY BLINDSPOT (`UCG_yrDQF5Sj6iMTZB0KSBAA`), matching
  the configured `finance` channel alias.
- Do not fetch or interpret retention metrics before 2026-07-25 23:19:36 +07.

## Source

- URL: https://www.youtube.com/watch?v=xv8qaYubDw4
- Subject: Jason Wersland, inventor/founder of Theragun
- Local source: `output/projects/hardknocks/source/xv8qaYubDw4.mp4`
- Source duration: 4401.667s
- Transcript: `output/projects/hardknocks/clips/v14_theragun_work/research/transcript.json`
- Renderer: `pipeline/hardknocks/render_hardknocks_v15_theragun_remake.py`

## Why V15 Replaces V14

V14 optimized for curiosity before comprehension. Its hooks were individually interesting, but the clips jumped across prototype, patient, crash, wife, father, demand and mission without preserving one causal chain. A cold viewer could hear memorable lines while still failing to answer what happened, what Jason did and why the ending mattered.

V15 uses one premise and one payoff per artifact:

- V15A premise: a motorcycle crash created the personal problem that led Jason to the first Theragun. Payoff: inventing a product and building a company are separate problems.
- V15B premise: the first prototype was validated on one patient. Payoff: repeated athlete demand—not founder intuition—revealed the real market.

## Narrative and Clarity Gate

### V15A — Crash → invention → company lesson

1. Jason is identified as the inventor of the massage gun.
2. A 2007 motorcycle crash establishes the inciting problem.
3. Ongoing shoulder pain and an under-equipped clinic establish the need.
4. A vibrating treatment table reveals the useful back-and-forth motion.
5. Jason builds the first Theragun.
6. The final distinction closes the story: he had a product, not yet a company.

Cold-viewer answers from the MP4 alone:

- Who: Jason Wersland, inventor of the massage gun.
- Problem: crash-related pain with no useful treatment in his clinic.
- Action: adapts the motion he felt from a vibrating table into a device.
- Result/payoff: first Theragun; then the product-versus-company lesson.

Verdict: PASS.

### V15B — Patient proof → athlete market

1. Jason states that the clinic prototype was a Makita jigsaw.
2. A patient arrives with injuries similar to Jason's.
3. Jason brings the jigsaw prototype in a paper bag and tries it on him.
4. The patient improves and later says the device saved both their lives.
5. Jason sells one per day to clinicians.
6. Athletes repeatedly empty his trunk and ask for multiple units.
7. Jason realizes athletes are the broader market.

Cold-viewer answers from the MP4 alone:

- Who: Jason Wersland, inventor of the early Theragun prototype.
- Problem: an improvised device needed real-world validation and a market.
- Action: tests it on a matching patient, then sells directly to clinicians and athletes.
- Result/payoff: patient proof validates the product; athlete pull reveals product-market fit.

Verdict: PASS.

## Verified Media Data

| Check | V15A | V15B |
|---|---:|---:|
| Resolution / codec | 1080×1920, H.264, yuv420p, 30fps | Same |
| Audio | AAC stereo, 48kHz | Same |
| Raw duration | 55.367s | 67.100s |
| Final duration after 1.06x | 52.233s | 63.300s |
| Source excerpt total | 55.380s (1.258% of source) | 67.100s (1.524% of source) |
| Longest source clip | 13.120s | 13.060s |
| Full-screen Pexels | 14.0s / 25.29% | 14.0s / 20.86% |
| First full-screen Pexels | final t=13.208s | final t=11.321s |
| Mid-roll CTA start | final t=40.566s | final t=41.509s |
| Full decode | PASS | PASS |
| Black events | 0 | 0 |
| Freeze events | 0 | 0 |
| Silence events | 0 | 0 |
| Integrated loudness | -16.1 LUFS | -16.1 LUFS |
| True peak | -1.3 dBFS | -1.5 dBFS |
| Frame-0 skin proxy | 50.56% | 27.18% |
| Hook static runs > threshold | 0 | 0 |

## Hook and Craft Gates

- Moving human footage is present from frame 0 through 3s in both artifacts.
- Dialogue captions are visible by t=0.2s and use short ASR-timed bursts.
- No full-screen Pexels replaces the speaker during 0–10s.
- Early SFX lands in the first second.
- V15A headline: `THE THERAGUN ORIGIN` → `IT STARTED WITH A CRASH`.
- V15B headline: `THE FIRST THERAGUN` → `WAS A JIGSAW`.
- Compact `LIKE • SUBSCRIBE • COMMENT` CTA keeps the interview visible.
- Source badge remains top-right. Moving watermark route is top-left → bottom-right → bottom-left, avoiding source-badge collision.
- Manual final contact-sheet review found no active-speaker crop, caption collision, black footer or evidence/claim mismatch.

## ASR Verification

V15A critical phrases all survive in the final artifact:

- `inventor of the massage gun`
- `motorcycle`
- `nothing in my clinic`
- `first Theragun`
- `I have a product. I didn't have a company`

V15B critical phrases all survive in the final artifact:

- `Makita jigsaw`
- `same injuries that I did`
- `That thing at my house has to help this guy`
- `this thing saved my life`
- `selling one a day`
- `my trunk would be empty`
- `this is actually for athletes`

The final V15B tail ends on the complete payoff `they see this, the benefit of that.` No sentence is truncated after it.

## Transformative Gate

| Rule | V15A | V15B |
|---|---|---|
| Commentary / original dialogue track | PASS | PASS |
| At least two value-add types | PASS: active-speaker reframing, animated causal badges, source citation, Pexels illustration | PASS: same |
| Every source clip <15s | PASS | PASS |
| Total source cut <50% of source | PASS: 1.258% | PASS: 1.524% |

The cached `power_tool_workshop` insert was rejected during exact-frame QC because it depicted a drill press rather than a jigsaw. V15B keeps Jason visible while the original audio and caption identify the Makita jigsaw. Semantic integrity takes priority over a stock-footage quota.

## Canonical Upload Package

Canonical machine-readable metadata: `output/projects/hardknocks/clips/v15_theragun_work/metadata.json`.

### V15A

Title:

`A Crash Created Theragun 🏍️🔧`

Description:

A Crash Created Theragun 🏍️🔧 #Theragun #FounderStory #shorts

After a motorcycle crash left Jason Wersland in pain, nothing in his clinic helped—until a vibrating treatment table revealed the motion behind the first Theragun. The invention solved his pain, but building the company was the next problem.

YouTube Studio tags (not visible hashtags):

1. `Theragun`
2. `Jason Wersland`
3. `founder story`

### V15B

Title:

`Theragun Began as a Jigsaw 🪚🔧`

Description:

Theragun Began as a Jigsaw 🪚🔧 #Theragun #ProductMarketFit #shorts

The first Theragun began as a Makita jigsaw carried into a clinic in a paper bag. One patient became the proof; athletes later revealed the product’s real market.

YouTube Studio tags (not visible hashtags):

1. `Theragun`
2. `product market fit`
3. `invention story`

## QC Evidence

- `output/projects/hardknocks/clips/v15_theragun_work/v15a/checks/validation.json`
- `output/projects/hardknocks/clips/v15_theragun_work/v15a/checks/asr_full.txt`
- `output/projects/hardknocks/clips/v15_theragun_work/v15a/checks/asr_hook.txt`
- `output/projects/hardknocks/clips/v15_theragun_work/v15a/checks/asr_proof_cta.txt`
- `output/projects/hardknocks/clips/v15_theragun_work/v15a/checks/asr_tail.txt`
- `output/projects/hardknocks/clips/v15_theragun_work/v15a/checks/hook_0_10.jpg`
- `output/projects/hardknocks/clips/v15_theragun_work/v15a/checks/contact.jpg`
- `output/projects/hardknocks/clips/v15_theragun_work/v15b/checks/validation.json`
- `output/projects/hardknocks/clips/v15_theragun_work/v15b/checks/asr_full.txt`
- `output/projects/hardknocks/clips/v15_theragun_work/v15b/checks/asr_hook.txt`
- `output/projects/hardknocks/clips/v15_theragun_work/v15b/checks/asr_proof_cta.txt`
- `output/projects/hardknocks/clips/v15_theragun_work/v15b/checks/asr_tail.txt`
- `output/projects/hardknocks/clips/v15_theragun_work/v15b/checks/hook_0_10.jpg`
- `output/projects/hardknocks/clips/v15_theragun_work/v15b/checks/contact.jpg`
- `output/projects/hardknocks/clips/v15_theragun_work/research/qc_media_report.json`

## Reproduction

```bash
python3 -m py_compile pipeline/hardknocks/render_hardknocks_v15_theragun_remake.py
/usr/bin/python3 pipeline/hardknocks/render_hardknocks_v15_theragun_remake.py --variant all
```

No Python renderer unit test was added; completion is based on real MP4 decode, detectors, final ASR and manual media review per repository policy.
