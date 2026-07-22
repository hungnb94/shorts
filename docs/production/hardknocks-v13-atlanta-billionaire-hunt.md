# HardKnocks V13 — Atlanta Billionaire Hunt

## Status

| Field | Value |
|---|---|
| Production | Complete — final audio-timing correction verified |
| Render date | 2026-07-22 |
| Upload status | Queued; not uploaded |
| Upload gate | BLOCKED until ADR-0035 lane eligibility, approved Studio template, and exact finance master playlist are verified |
| Final video | `output/projects/hardknocks/final/2026-07-22-hardknocks_v13_atlanta_billionaire_hunt.mp4` |
| Renderer | `pipeline/hardknocks/render_hardknocks_v13_billionaire_hunt.py` |
| Source | https://www.youtube.com/watch?v=VW2t21zzYl8 |
| Source title | `Asking Wealthy Americans How They Got Rich! (Atlanta)` |
| Source channel | School of Hard Knocks |
| Narrator profile | `natural_talker_male_qwen_blog` (Qwen3-TTS MLX) |
| Runtime | 57.200s |
| SHA-256 | `011aa65bb07510664e132aea3882a6af8ace9a943d83cdd930107b4addefb0f2` |
| QC summary | `output/projects/hardknocks/clips/v13_billionaire_hunt_work/checks/validation.json` |
| Design | `docs/specs/2026-07-22-hardknocks-atlanta-billionaire-hunt-design.md` |
| Implementation plan | `docs/plans/2026-07-22-hardknocks-atlanta-billionaire-hunt.md` |

## Hook Change Versus Previous Video

The previous B1 John Ruiz Short used a **Direct Dare Question**:

> Is he still a billionaire—or did that disappear with the stock?

V13 now uses a **Direct Search Question**. It keeps the proven question-first mechanism but changes the object from one disputed net-worth claim to an escalating candidate search.

> How many millionaires do you have to meet before you find a real billionaire?

The canonical `natural_talker_male_qwen_blog` narrator asks the question while the original host keeps walking toward camera. The source dialogue is fully ducked during the question, so only one spoken idea competes for attention.

ASR-timed caption sequence:

1. `HOW MANY MILLIONAIRES`
2. `DO YOU HAVE TO MEET`
3. `BEFORE YOU FIND`
4. `A REAL BILLIONAIRE?`

The question completes at final t≈2.82s. It withholds the number of candidates, whether the hunt succeeds and Rick's identity.

The hook states the objective but withholds whether the hunt succeeds and who the billionaire is.

## Narrative

### Opening — mission

The host walks toward camera and establishes the Atlanta hunt. Frame 0 contains a moving human face; no title card or freeze-frame is used.

### Body — escalating near-misses

1. An interview prospect declines to discuss wealth.
2. A Waffle House franchisee reports starting at 22 and reaching 14 locations.
3. A source participant says he learned wealth in prison and reached eight figures.
4. Rick Jackson reports owning 22 healthcare companies and $3B in annual company revenue.

The game-state overlay stays `BILLIONAIRE FOUND: NO` until Rick explicitly answers yes. The prison/eight-figure statement is labeled `SOURCE-REPORTED`; it is not presented as independently verified fact.

### Proof and payoff

The Forbes profile card verifies the identity/claim family without conflating revenue with personal wealth:

- `$1B NET WORTH`
- `22 BUSINESSES`
- `$3B ANNUAL REVENUE`

Source: https://www.forbes.com/profile/rick-jackson

After the proof, the story pivots to Rick's actionable lesson: no degree, no-salary/commission-only proposal, and buying the firm one year later. The final interpretation is:

> He removed their risk, then earned the right to own.

## Timeline

All times below are final-video times after the uniform 1.12x speed-up.

| Final time | Beat |
|---:|---|
| 0.00–3.57 | Direct Search Question on moving host footage |
| 3.57–6.18 | First rejection |
| 6.18–11.54 | Waffle House candidate on continuous original interview footage |
| 11.54–20.74 | Prison/eight-figure candidate |
| 20.74–33.51 | Rick: healthcare, 22 companies, $3B, billionaire confirmation |
| 33.51–38.10 | Forbes proof card + narrator verification |
| 38.10–41.52 | Mid-Roll Triple CTA |
| 41.52–54.29 | No-degree → no-salary/33% commission → bought the firm |
| 54.29–57.20 | Business Lesson Payoff |

Machine-readable timeline: `output/projects/hardknocks/clips/v13_billionaire_hunt_work/timeline.json`.

## Source Windows and Transformative Gate

| Segment | Raw source time | Duration |
|---|---:|---:|
| Question-hook moving backdrop | 0.08–4.08 | 4.00s |
| Rejection | 90.88–93.80 | 2.92s |
| Waffle House | 194.56–200.56 | 6.00s |
| Prison/wealth | 559.60–565.10 | 5.50s |
| Prison/eight figures | 602.64–607.44 | 4.80s |
| Rick/companies | 970.60–975.70 | 5.10s |
| Rick/revenue + confirmation | 976.16–985.36 | 9.20s |
| Proof moving backdrop | 985.36–990.48 | 5.12s |
| CTA moving backdrop | 990.48–994.32 | 3.84s |
| Rick/no degree | 1017.92–1021.03 | 3.11s |
| Rick/commission bet | 1024.08–1032.24 | 8.16s |
| Rick/bought firm | 1032.24–1035.27 | 3.03s |
| Payoff moving backdrop | 1035.27–1038.55 | 3.28s |

Transformative Gate:

- Commentary track: PASS — proof VO, context-specific CTA VO, and Business Lesson Payoff VO.
- Value-adds: PASS — game-state counter, Forbes fact-check card, Business Lesson interpretation, active-speaker reframing.
- Every source clip strictly below 15s: PASS — longest 9.20s.
- Total source use below 50%: PASS — 64.06s of a 1316.241s source, 4.867%.

## Visual and Sound Package

- Active-Speaker Reframing follows the current speaker across two-shots.
- Source burned-in caption band is cropped out, then uniformly zoomed back to 1080×1920; no black footer and no non-uniform face stretch.
- Komika Axis caption profile: short 2–5-word bursts, one yellow-emphasized keyword, normal center near 60% frame height.
- Question captions are visible at t=0, use four ASR-timed bursts and sit on the host's torso rather than covering his mouth.
- Hook visual cadence is supplied by real walking/handheld footage plus staged overlay changes; no full-screen Pexels replacement occurs during 0–10s.
- Early SFX is present at pre-speed t=0.08s.
- Pexels contract illustration: asset 7981954, explicitly labeled `ILLUSTRATION`.
- Mid-Roll Triple CTA begins at final t=38.095s and asks for Like, Subscribe, and Comment.
- `HARD KNOCKS LAB` watermark moves top-left → top-right → bottom-left over three timeline thirds.
- Long pauses were removed by source-window selection. Selected-speech word-start analysis found normal cadence through 0.441s and a pause cluster beginning at 0.559s; the project threshold was set to 0.50s. Uniform final speed-up is 1.12x.

## Final QC

Technical:

- 1080×1920, H.264, yuv420p, 30fps: PASS.
- AAC stereo, 48kHz: PASS.
- Runtime 57.200s: PASS.
- Full decode: PASS, exit 0.
- Black events: 0.
- Freeze events ≥1.0s: 0.
- Silence events ≥0.35s at -45dB: 0.
- Integrated loudness: -16.10 LUFS.
- True peak: -1.14 dBTP.

Hook:

- Frame-0 face/manual review: PASS.
- Frame-0 YCbCr skin-tone proxy: 19.08%, above the 10% gate.
- Moving footage throughout 0–3s: PASS.
- Full-screen face blackout in 0–10s: none.
- Hook ASR: `How many millionaires do you have to meet before you find a real billionaire?`

Manual media review:

- Final 0–5s mobile hook sheet: PASS.
- Full 1fps mobile contact sheet: PASS.
- Proof card at full resolution: PASS; publisher identity and $1B/$3B/22-business labels are legible.
- CTA frame at t=40.5s: PASS; all three asks and the context question are legible.
- Active-speaker crops: PASS; no face/head clipping found in critical frames.
- Source-caption bleed: none observed.
- Flat black footer: none; bottom-row pixel scan passes at seven timestamps across the runtime.
- Aspect distortion: none observed.
- End frame remains full-canvas moving footage with payoff text.

Evidence paths:

- `output/projects/hardknocks/clips/v13_billionaire_hunt_work/checks/validation.json`
- `output/projects/hardknocks/clips/v13_billionaire_hunt_work/checks/ffprobe.json`
- `output/projects/hardknocks/clips/v13_billionaire_hunt_work/checks/full_decode.log`
- `output/projects/hardknocks/clips/v13_billionaire_hunt_work/checks/visual_detectors.log`
- `output/projects/hardknocks/clips/v13_billionaire_hunt_work/checks/silence_detect.log`
- `output/projects/hardknocks/clips/v13_billionaire_hunt_work/checks/loudnorm.log`
- `output/projects/hardknocks/clips/v13_billionaire_hunt_work/checks/asr/final_asr.json`
- `output/projects/hardknocks/clips/v13_billionaire_hunt_work/checks/frames/hook_mobile.jpg`
- `output/projects/hardknocks/clips/v13_billionaire_hunt_work/checks/frames/contact_360x640.jpg`
- `output/projects/hardknocks/clips/v13_billionaire_hunt_work/checks/hook0_face_report.json`
- `output/projects/hardknocks/clips/v13_billionaire_hunt_work/checks/bottom_rows_report.json`
- `output/projects/hardknocks/clips/v13_billionaire_hunt_work/checks/audio_boundary_report.json`

## Canonical Upload Package

### YouTube Title

`The Billionaire Hunt 🕵️💰`

Validation: 24 characters, Title Case, exactly two emojis, below the 30-character cap.

### Description

```text
The Billionaire Hunt 🕵️💰
A search across Atlanta ends with Rick Jackson—and the no-salary bet that changed his career.

#shorts #business #entrepreneurship
```

Visible hashtags: exactly 3.

### YouTube Studio Tags

1. `billionaire mindset`
2. `business lessons`
3. `rick jackson`

Studio tags: exactly 3.

### Studio Settings

| Setting | Canonical value |
|---|---|
| Visibility | Unlisted first; public only after final Studio preview and ADR-0035 lane gate |
| Audience | Not made for kids |
| Video language | English (United States) |
| Title/description language | English (United States) |
| Category | Education |
| Recording location | Atlanta, Georgia, United States |
| Paid promotion | No |
| Altered/synthetic content disclosure | No — synthetic audio is clearly editorial narration and does not depict a real person saying or doing something they did not do |
| Raw affiliate link | None |
| Playlist | BLOCKED — the public MONEY BLINDSPOT channel currently has no playlists tab, and no exact approved finance master-playlist name exists in the repo |
| Related Video | BLOCKED until the current measured winner and actual destination lane are resolved |
| Upload Details Template | BLOCKED — no approved template name/ID exists in the repo |

## Upload Gate

Do not upload yet.

1. The previous known MONEY BLINDSPOT Short was public on 2026-07-19. Distribution Plateau has not been verified for the next strict-round-robin lane.
2. The destination lane must be resolved from ADR-0035 state before touching Studio; do not default to the previous channel.
3. The exact approved finance master playlist is absent. A public channel check returned `This channel does not have a playlists tab`.
4. The approved Upload Details Template name/ID is absent from repository configuration/docs.
5. Related Video wiring cannot be selected until the measured current winner and actual destination channel are known.

The media artifact and canonical title/description/tags are complete. Stage 6 remains intentionally blocked rather than inventing Studio state.

## Post-Production Retro

### Hook Retro

- The revised Direct Search Question intentionally reuses B1's proven question-first mechanism but does not copy its premise: B1 asks whether one named man still qualifies; V13 asks how many candidates the hunt must cross before finding a real billionaire.
- The complete generated question is intelligible in one listen and ends at final t≈2.82s. Final hook-window loudness is -16.2 LUFS.
- It preserves a real face and motion at frame 0, states the search objective immediately, and withholds identity/outcome until the Rick beat.
- The main second-order risk was that a multi-person montage could feel like disconnected clips. The persistent `BILLIONAIRE FOUND: NO` game state and escalating wealth thresholds keep every candidate inside one question.
- The hook should be judged at 48h against B1's Direct Dare Question using the same Studio metric family; no API percentage should be treated as a correction for Studio Stayed to Watch.

### Keep

- Direct Search Question TTS over moving original footage, with source dialogue ducked rather than competing.
- Explicit game-state counter for multi-candidate narratives.
- Active-speaker reframing and uniform caption-band removal.
- Proof card that separates personal net worth from company revenue.
- CTA positioned after the main reveal but before the actionable lesson.
- Business Lesson Payoff: one sentence that converts biography into a repeatable mechanism.

### Fix Next Time

- Do not position narration/SFX by shifting PTS and assuming `amix` will preserve it. The first render rebased every delayed track to t=0 and drowned the hook.
- Use sample-level leading silence (`anullsrc` + `concat`) for every timed audio asset, then verify placement with hook/proof/CTA/tail ASR before accepting the render.
- Drop contextually weak stock footage even when it is technically related. The chef/kitchen insert implied cooking rather than multi-location ownership, so Pexels 4253352 and its attribution were removed entirely; original interview footage now runs continuously through the Waffle House beat.
- The first question-hook render exposed a 0.377s dead-air gap before the rejection. A 0.25s rejection-SFX pre-lap/J-cut removed the gap without adding dialogue or changing the body order; final `silencedetect` is clean.
- Exact-frame review found the initial question caption covering the host's mouth. Moving only the hook captions to y=1280 preserved the body calibration and put the text on the torso.
- The proof-page body text is evidentiary rather than primary reading material; large editorial labels carry phone readability. Future proof crops should isolate only the two relevant source lines if the publisher layout allows it.

### Drop

- Do not claim the source title's `24 hours`; the retained source dialogue only establishes one mission.
- Do not present `$3B revenue` as `$3B net worth`.
- Do not independently assert the unidentified participant's prison/eight-figure story; retain the `SOURCE-REPORTED` qualifier.
- Do not upload while the lane, playlist, template, or Related Video setting is unresolved.
