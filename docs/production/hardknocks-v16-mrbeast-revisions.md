# HardKnocks V16 — MrBeast-Editing Material Revisions

Date: 2026-07-24  
Status: local production complete; V16B uploaded private; V16A/V16C remain local  
Source interview: `output/projects/hardknocks/source/xv8qaYubDw4.mp4`  
Strategy reference: https://www.youtube.com/watch?v=OASaa6MKyZQ

## Decision

Preserve V15A and build three independent Material Revisions. Each revision has one premise, one causal spine and one payoff. The reference is used for information architecture, contrast and sound-state transitions—not copied visual styling.

## Final artifacts

| Variant | Premise | Final file | Duration | SHA-256 |
|---|---|---|---:|---|
| V16A | Product is not yet a company; repeatable demand reveals the market | `output/projects/hardknocks/final/2026-07-24-hardknocks_v16a_product_not_company.mp4` | 62.900s | `de2ae73b2e526823f974565d2f8c238ca4f529a6cac5fc69439017f8f9d2e4d0` |
| V16B | The crash created the need; the back-and-forth motion created the product | `output/projects/hardknocks/final/2026-07-24-hardknocks_v16b_crash_not_breakthrough.mp4` | 51.667s | `15414e6f7f65c81b84efd013c84b07db591ac7919f40bc6fc7919550b85acfda` |
| V16C | His own clinic could not help; necessity plus mechanism produced the product | `output/projects/hardknocks/final/2026-07-24-hardknocks_v16c_clinic_could_not_help.mp4` | 60.700s | `8f1aac1506bb061410186f1ae0498e90e7803e6ce1f03508053952a27dec8bb5` |

File sizes: V16A 55,292,040 bytes; V16B 41,011,229 bytes; V16C 46,264,095 bytes.

Renderer: `pipeline/hardknocks/render_hardknocks_v16_mrbeast_revision.py`  
Canonical metadata: `output/projects/hardknocks/clips/v16_mrbeast_work/metadata.json`

## Reference findings applied

### Observed

- The reference opens with authority, quantified proof and a concrete before/after promise rather than a generic topic label.
- Its first 10 seconds contain six strong scene changes.
- Strong scene-change median is approximately 4.12s; a more sensitive motion/transition detector gives approximately 1.92s.
- Chapters reset attention with contrast, silence, music-state changes, visible proof and compact captions.
- The reference treats edit density as information progression, not as blind hard-cut frequency.

### Transfer to V16

1. Keep moving human footage and captions from frame 0.
2. Open one contradiction; do not state the full payoff in the hook.
3. Change the viewer's information state approximately every 0.8–1.5s in the hook via crop, panel, evidence or caption—not arbitrary stock.
4. Move from problem to mechanism to proof to payoff.
5. Use distinct audio states for problem, discovery and payoff.
6. Label every Pexels event `ILLUSTRATION`; source interview remains the causal evidence.
7. Hold the final payoff long enough to complete the last phoneme and visual read.

The detailed evidence/claim/hypothesis separation is in `docs/research/edit-video-mrbeast-strategy-2026-07-24/REPORT.md`.

## Cold-viewer retell

### V16A

- Subject: Jason Wersland, inventor of Theragun.
- Problem: he had a working product but not yet a company or proven market.
- Action: he solved his pain, built devices manually and put them in athletes' hands.
- Evidence/result: the trunk repeatedly emptied; people around him validated demand.
- Payoff: repeatable demand—not merely the prototype—created the business opportunity.

Trade-off: strongest finance/business fit, but product identity is intentionally withheld early to preserve the open loop.

### V16B

- Subject: Jason Wersland, later revealed as the Theragun inventor.
- Problem: a motorcycle crash created severe pain and his clinic had no useful answer.
- Action: he tested a vibrating table, isolated back-and-forth motion and decided to build what he could not find.
- Evidence/result: he made the first Theragun in February 2008.
- Payoff: the crash created the need; motion was the breakthrough.

Trade-off: strongest immediate action/stakes, but reuses the crash mechanism that V15A already tested.

### V16C

- Subject: a clinician who could not solve his own pain.
- Problem: his clinic's modalities did not provide a workable answer.
- Action: he tested the vibrating table, observed temporary relief, isolated the motion and built a device.
- Evidence/result: the first Theragun was made in February 2008.
- Payoff: necessity plus mechanism created the product.

Trade-off: clearest mechanism chain, but the least aggressive visual hook.

## Recommendation

Ranking by finance-channel fit: V16A > V16C > V16B.  
Ranking by raw hook action/stakes: V16B > V16A > V16C.

Recommended upload candidate: V16A. It changes the failed V15A crash-led premise rather than repeating it, matches the finance/business niche, and creates a fresh contradiction: product does not equal company. This is a hypothesis, not a guaranteed performance claim.

Operational rule: do not publish all three simultaneously. Register the variants for the experiment/MAB workflow, obey ADR-0035 lane eligibility and Plateau-Gated Cadence, and upload only the scheduler-selected candidate to the next eligible lane. Keep the other two as Material Revisions for later eligible tests.

## Final media QC

| Gate | V16A | V16B | V16C |
|---|---:|---:|---:|
| Duration | 62.900s | 51.667s | 60.700s |
| Source usage / full source | 1.508% | 1.239% | 1.459% |
| Pexels share | 21.66% | 26.39% | 22.44% |
| First full-screen Pexels | 11.321s | 10.377s | 10.377s |
| CTA begins | 40.000s | 40.000s | 40.000s |
| Payoff begins | 55.623s | 44.453s | 53.604s |
| Final tail safety | 196ms | 189ms | 165ms |
| Integrated loudness | -16.73 LUFS | -16.73 LUFS | -16.89 LUFS |
| True peak | -2.27 dBTP | -1.67 dBTP | -1.94 dBTP |
| Black / freeze / silence events | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| Full decode | pass | pass | pass |
| Validator assertions | all pass | all pass | all pass |

All three are 1080×1920, H.264/yuv420p at 30fps with AAC stereo 48kHz. Every retained source clip is under 15s. No TTS is used.

### ASR

Final-byte Whisper `large-v3-turbo` transcription passed all three.

- V16A ends: `And really getting the validation of the people around me was super important.`
- V16B ends: `So I made the first Theragun in February of 2008.`
- V16C ends: `So I made the first Theragun in February of 2008.`
- No `February of 2000`, `dive around`, `They have a company`, dangling conjunction or cut-off final phoneme remains.

### Visual/manual gates

- Moving face from frame 0; caption is visible by 0.2s.
- Human face remains visible throughout protected 0–10s.
- Full-screen Pexels begins only after final 10s.
- Source badge is absent at final 9.90s and visible at 10.10s. Its ASS start is raw 10.65s, resolving to final approximately 10.047s.
- Mid-roll CTA at 41.0s visibly contains `LIKE • SUBSCRIBE • COMMENT` without collision.
- Moving watermark route verified top-left → bottom-right → bottom-left; top-right remains reserved for source citation.
- 37 exact source/render midpoint pairs passed active-speaker crop review.
- All 48 start/mid/end frames across 16 Pexels events passed semantic/logo review.
- Pixel-row/column scans found no persistent black footer or side bar.
- Final payoff/tail frames are complete, readable and free of an accidental next sentence.

Primary QA evidence:

- `output/projects/hardknocks/clips/v16_mrbeast_work/qc/final_hooks_compare.jpg`
- `output/projects/hardknocks/clips/v16_mrbeast_work/qc/final_arcs_compare.jpg`
- `output/projects/hardknocks/clips/v16_mrbeast_work/qc/final_cta_mid/compare.jpg`
- `output/projects/hardknocks/clips/v16_mrbeast_work/qc/final_crop_midpoint_pairs.jpg`
- `output/projects/hardknocks/clips/v16_mrbeast_work/qc/semantic_stock_all_events.jpg`
- `output/projects/hardknocks/clips/v16_mrbeast_work/qc/source_badge_transition/compare.jpg`
- `output/projects/hardknocks/clips/v16_mrbeast_work/qc/final_tail_after_190ms.jpg`

## Transformative Gate

Pass under the repository's V15/ADR precedent:

1. Original interview dialogue plus self-authored editorial framing/payoff/CTA captions provides the commentary layer.
2. Value-adds include source citation, animated causal cards/annotations, counter-framing and labeled multi-source illustration.
3. Total source use is below 50% and every source clip is below 15s.

Pexels footage is illustration only and is never represented as Jason's accident, clinic, prototype or archival evidence.

## Canonical metadata

### V16A

Title: `Theragun Wasn't a Company ⚡`

Description:

`Jason Wersland had a working Theragun, but no company yet. Repeated athlete demand revealed the market that could turn the product into a business.`

`#Theragun #Entrepreneurship #ProductMarketFit`

Studio tags: `Theragun, Jason Wersland, founder story, product market fit, entrepreneurship, startup lessons, business story, invention, market validation, athlete recovery`

### V16B

Title: `The Crash Wasn't the Idea 🏍️`

Description:

`The motorcycle crash created the need—but the breakthrough was the back-and-forth motion that turned temporary relief into the first Theragun.`

`#Theragun #Innovation #FounderStory`

Studio tags: `Theragun, Jason Wersland, motorcycle crash, invention story, innovation, founder story, product design, pain relief, massage gun, business origins`

### V16C

Title: `His Clinic Couldn't Help Him 🏥`

Description:

`A doctor discovered his own clinic couldn't solve his pain. Testing why a vibrating table helped led him to the first Theragun.`

`#Theragun #ProblemSolving #BusinessStory`

Studio tags: `Theragun, Jason Wersland, clinic, problem solving, founder story, invention, vibrating table, product design, business story, innovation`

Each description has exactly three visible hashtags. Studio tags are stored separately in `metadata.json`.

## Status

| Field | Value |
|---|---|
| YouTube Video ID | [`aK1AODnLohE`](https://youtube.com/shorts/aK1AODnLohE?feature=share) |
| Uploaded variant | V16B — `hardknocks_v16b_crash_not_breakthrough` |
| Visibility | Private — user-reported; live metadata cannot yet be independently verified |
| Uploaded | 2026-07-24 — user-reported; exact upload time unknown |
| Logged at | 2026-07-24 11:09:34 +07 |
| Public release | Not yet public; exact timestamp unknown |
| Destination lane eligibility | Not verified; must pass ADR-0035 before public release |
| Metrics fetch after (48h rule) | N/A until public release; set to actual public timestamp +48h |
| Metrics status | N/A while private — the 48h analytics clock has not started |
| Studio Analytics | https://studio.youtube.com/video/aK1AODnLohE/analytics/tab-overview/period-default |

V16A and V16C remain local and not uploaded. No performance conclusion should be drawn from technical QC or private-upload status.

## Post-production retro

Three silent failure classes were caught only by final-byte review:

1. A frame-rounded final trim removed the end consonant in `2008`; a final-time tail assertion now blocks recurrence.
2. ffmpeg `alimiter` defaults to automatic level makeup; `level=false` plus lossy-output true-peak measurement is required.
3. A raw 10.05s source badge appeared at final 9.48s after the 1.06× speed-up; protected gates must be converted from final time to raw time and checked immediately before/after the boundary.

These lessons were added to the `short-form-video-quality-assurance` skill reference. The repository workflow remains sufficient when that final-byte discipline is followed.