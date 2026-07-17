# HardKnocks V9R — Original-Voice Revision

**Date:** 2026-07-17
**Status:** Production complete; QC passed; uploaded/public
**Parent treatment:** HardKnocks V9 Live-Approach (`U_3cCYOcCmk`)

## Decision Record

At `2026-07-17 10:51:13 +07`, the public V9 upload had been live for approximately 1 hour 13 minutes and `yt-dlp` reported `view_count: 0`.

### Evidence

- V9 was public and available.
- Public view count at the observation time was zero.
- No viewer had therefore produced an observable retention response to either TTS bridge.
- The two synthetic bridges in V9 were:
  - “The exit sounds instant. The origin story was nothing like it.”
  - “The company collected the upside. His commission check barely moved.”

### Interpretation

Zero views at that observation point is a distribution/exposure state, not evidence that viewers rejected the commentary. The commentary occurs downstream, so it cannot explain a measured retention failure before any viewer exposure exists.

### Production Hypothesis

An original-voice-only revision may still be a better treatment because it:

- removes approximately 11 seconds of synthetic narration;
- moves directly from the `$200M` exit to the no-capital origin;
- moves directly from the Yellow Pages setup to the `$100M / $10K` payoff;
- reduces total duration from 56.13 seconds to 45.87 seconds;
- keeps the source speaker's voice continuous.

This is a production hypothesis, not a causal diagnosis of V9's initial zero-view state.

### Chosen Scope

The grill confirmation timed out, so the least-confounded interpretation of the user's explicit request was used:

- remove both TTS bridges;
- close both timeline gaps;
- preserve the Live-Approach hook;
- preserve the same-source moving face inset;
- preserve source segments, caption language, music, panels and Pexels asset types;
- retime evidence overlays to the shortened timeline;
- keep the existing V9 upload public;
- do not upload the revision automatically.

## Artifact

`output/projects/hardknocks/final/2026-07-17-hardknocks_v9r_original_voice.mp4`

| Field | Value |
|---|---:|
| Duration | 45.866667s |
| Resolution | 1080x1920 |
| Frame rate | 30fps |
| Video | H.264, yuv420p |
| Audio | AAC stereo, 48kHz |
| File size | 29,588,454 bytes |
| SHA-256 | `c5a9a9cd6d3772d1988053c90fd0471e6bcf949eaf9fdb52b5e3c5fb6b2f3d42` |
| Post speed | 1.03x |
| Synthetic TTS bridges | 0 |
| Evidence usage | 27.92% |
| First full-screen evidence | 19.029s final time |
| Long-source usage | 2.88% |

## Story Arc

1. Live encounter and mansion/status proof.
2. Host asks how the subject became wealthy.
3. Subject names the advertising company and Blackstone.
4. `$200M` sale and buyback reveal.
5. Immediate source-native transition to “absolutely nothing” and basement origin.
6. Trigger question and multi-hundred-million ambition.
7. Yellow Pages door-to-door and internet-program setup.
8. `$100M` collected versus `$10K` check.
9. Original decisive payoff: “I'm doing this on my own.”

## Evidence Timeline

Raw timeline timings precede the final 1.03x speed-up.

| Start | Duration | Evidence | Label |
|---:|---:|---|---|
| 19.60s | 3.00s | `$200M` sale/buyback panel | `INTERVIEW CLAIM` |
| 24.50s | 3.50s | Home/laptop Pexels footage | `ILLUSTRATION: PEXELS` |
| 36.50s | 3.00s | Printed-pages Pexels footage | `ILLUSTRATION: PEXELS` |
| 42.00s | 3.50s | `$100M vs $10K` panel | `INTERVIEW CLAIM` |

## Transformative Gate

| Requirement | Result |
|---|---|
| Editorial commentary | Pass — source speech is selected and reordered into a new `$200M → zero capital → $100M/$10K → independence` thesis |
| Minimum two value-adds | Pass — two claim panels, two labeled Pexels illustrations, word-burst captions and source citation |
| Source usage ≤50% | Pass — 2.88% of the long source |
| Every source excerpt <15s | Pass |

This is an **Original-Voice Editorial Commentary** treatment: no synthetic narration, but not a raw interview repost.

## QC

Canonical report:

`output/projects/hardknocks/clips/v9r_work/checks/qc-summary.json`

| Check | Result |
|---|---|
| Full decode | Pass |
| Resolution/codecs/frame rate | Pass |
| Black events | 0 |
| Freeze events ≥1s | 0 |
| Silence events ≥1s | 0 |
| Intentional ending margin | 0.487s after final spoken word |
| Integrated loudness | -15.70 LUFS |
| True peak | -0.56dBFS |
| Hook Face Gate | Pass at 0.0s, 0.5s and 2.0s |
| Hook contact-sheet review | Pass |
| Whole-video contact-sheet review | Pass |
| Final payoff-frame review | Pass |
| Final artifact ASR | Pass |

ASR recovered all required evidence and payoff meaning:

- Blackstone;
- `$200 million`;
- basement origin;
- Yellow Pages;
- `$100 million` collected;
- `$10,000` check;
- “doing this on my own.”

## Experiment Boundary

V9R is not a controlled test of TTS commentary unless upload conditions, audience exposure and all other variables can be held stable. A later upload time is itself a confound.

Do not log either of these claims:

- “V9 flopped because of the commentary.”
- “V9R proves original voice performs better.”

The valid future comparison is descriptive:

- V9 treatment: Live-Approach + two TTS bridges, 56.13s.
- V9R treatment: same narrative design without synthetic bridges, 45.87s.

## Upload Recommendation

Keep V9 public long enough to distinguish delayed distribution from genuine low reach. Do not delete and immediately reupload the same story, because that destroys the observation window and adds timing/reupload confounds.

If V9R is uploaded, log it as a **revision treatment**, not as a clean control.

## YouTube Metadata

### Title

`They Collected $100M. His Check Was $10K`

### Description

He says a company collected about $100 million from an internet program he helped roll out—while his commission check was $10,000. That gap pushed him to build on his own, eventually selling a company to Blackstone for $200 million and buying it back.

#Entrepreneurship #BusinessStory #MoneyMindset

### YouTube Studio Tags

`entrepreneur story, business motivation, 200 million company, 100 million revenue, 10000 commission check, Yellow Pages, Blackstone, how to get rich, business lessons, founder mindset, School of Hard Knocks, money mindset, business story, YouTube Shorts`

### Upload State

- Status: Uploaded; public
- YouTube video ID: `GGGDbkuZUD0`
- YouTube URL: https://youtube.com/shorts/GGGDbkuZUD0
- Shared URL supplied by user: https://youtube.com/shorts/GGGDbkuZUD0?feature=share
- Upload reported by user: 2026-07-17 11:25:39 +07
- Public timestamp verified from metadata: 2026-07-17 11:23:29 +07
- Public title: `They Collected $100M. His Check Was $10K`
- Public channel: MONEY BLINDSPOT (`UCG_yrDQF5Sj6iMTZB0KSBAA`), matching the configured `finance` channel
- Public duration: 46s rounded
- Metrics status: Not yet fetched — wait at least 48 hours
- Metrics fetch after: 2026-07-19 11:23:29 +07 or later
- Studio Analytics: https://studio.youtube.com/video/GGGDbkuZUD0/analytics/tab-overview/period-default

The agent did not perform the upload. No deletion, commit or push was performed.
