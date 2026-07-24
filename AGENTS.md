# Shorts

Animated short video factory — sản xuất Shorts 9:16, 50-75s và phát hành qua Channel Pool theo Plateau-Gated Cadence để AB test viral content formulas trên YouTube + TikTok.

Niche: Finance/money-making (English) as the primary/documented vertical, run in parallel with two additional, deliberately-chosen verticals — health/longevity (Vietnamese, Source Channel "Bác sĩ Hải") per ADR-0019, and AI education (English, professionals/knowledge workers) per ADR-0020 — multi-niche AB testing: more parallel data streams → faster overall learning.

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

## Key Conventions

- **Copy, don't invent** — find proven viral formats → repackage. Never invent new formats from scratch. See ADR 0002.
- **Autonomous optimization** — MAB selects variants, no human chooses experiments. System learns from AVD data. See ADR 0009.
- **Plateau-Gated Cadence** — no fixed daily/weekly quota. Each vertical uses three phone-verified, ≥3-week-aged Destination Channels in strict round-robin order; the next lane must be eligible under ADR-0035.
- **Video specs fixed** — 9:16 (1080x1920), 50-75s, MP4 H.264 with audio. No exceptions for new production (ADR-0034).
- **English for all channel**
- **Download max quality** — always download source videos at highest available resolution (2160p/4K) using `yt-dlp -f "bestvideo[height>=2160]+bestaudio"`. Never accept default 720p.
- **3-source combo for engagement** — every video combines: (1) original source footage, (2) animated overlays (kinetic text, data viz, whiteboard), (3) Pexels b-roll for visual variety. This maximizes retention by avoiding visual monotony.
- **Standard workflow** — see `docs/WORKFLOW.md` for the mandatory per-video sequence, the blocking Hook Gate (Stage 0, no cutting/rendering before a strong 0-3s hook is chosen), and the required per-video Post-Production Retro.
- **Guide-derived verification baseline** — every new Short must pass ADR-0034: early SFX, calibrated caption profile, Mid-Roll Triple CTA at t=38-42s, moving watermark, compact metadata, playlist/Related wiring and explicit Studio settings.
- **Media-first verification; no renderer unit tests** — the current `pipeline/<project>/render_*.py` files are one-off video-production tools, not product code. Do not create, extend, or require `test_render_*.py` files and do not apply TDD to these renderers unless the user explicitly requests automated code tests.
- **Final video filenames are date-prefixed** — every rendered file under `output/projects/<project>/final/` uses `yyyy-mm-dd-<name>.mp4` (the render date), e.g. `2026-07-11-hardknocks_v2_implied_comparison.mp4`, so the creation date is visible without checking file metadata. Applies going forward from 2026-07-11; older files are not being renamed retroactively.

## Known Pitfalls

### Metrics lag is real — wait 48h minimum
YouTube Analytics data unstable <48h. Fetching at 24h = noisy AVD numbers → bad MAB decisions. System enforces 48h wait, don't override.

### Don't reset MAB state mid-cycle
Deleting `data/mab_state.json` while system running = lose all learned rewards → restart from scratch. Only reset when intentionally changing strategy.

### Hook caption sync and cadence (ADR-0018, amended by ADR-0036)
Benchmarked 6 independently viral Shorts (`docs/research/hook-benchmarks-2026-07/REPORT.md`) — all 6 shared two patterns not previously encoded as rules here:
- **Caption sync**: burned-in caption must be visible by t=0.2s (not delayed for a "clean" shot), updating every ~1-2s in short 2-5 word bursts synced to speech, with one keyword per burst visually emphasized (color/weight distinct from the rest).
- **Cadence**: ADR-0036 amends the old uniform rule: final 0-5s targets one Visual Change every 0.8-1.5s, final 5-10s has no unexplained gap >3s, and the body has no unexplained gap >6s. Cut, reframe/zoom, overlay, layout/source change or continuous motion counts; the separate Information Progression Gate blocks decorative effect spam.
- **Show, don't just tell**: pair any spoken claim (wealth, results, a number) with simultaneous visual evidence (prop, environment, action) rather than narration alone — in the benchmark set, the verbal claim and its visual proof landed in the same beat, not sequentially.

### Guide-derived craft verification is blocking (ADR-0034)
- Early SFX must land within t=0-1s; add an arrow/pointer/animated annotation when the focal target is ambiguous.
- Caption bursts use the Caption Style Profile from `CONTEXT.md`: Komika Axis for English, Bangers for Vietnamese, 2-5 words, one animated/emphasized keyword, normal center at 55-65% frame height. ffmpeg values come from the checked-in calibration artifact, never literal CapCut `16/60` units.
- Still-image entrances/exits and purposeful transitions receive matching SFX.
- A custom on-brand Mid-Roll Triple CTA begins at t=38-42s and asks for Like, Subscribe and Comment.
- A non-obstructive moving watermark changes position over the timeline.

### Clip Curation Edit must pass the Transformative Gate
Video Type #7 (Clip Curation Edit) uses real footage from Source Channel — unlike the 6 animation types (zero-footage). Before upload, every Clip Curation Edit MUST pass all 3 Transformative Gate rules: (1) commentary track required, (2) min 2 value-adds from [fact-check callout, data viz, source citation, multi-source mashup, animated annotation, counter-argument], (3) cut ≤50% source duration + each clip <15s. Uploading a clip edit that fails the gate = copyright strike risk. Attribution is intentionally dropped per user decision.

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

### Value-Add Layer must be post-render compositing, not embedded in renderer
The value-add overlay layer (ADR 0008) must be a separate compositing step AFTER the base video renders. Do NOT couple it into the main renderer (current render_clip.py couples overlay rendering into clip rendering at line 175-481). To support all 7 video types, extract overlay compositing into a shared step: base video → composite value-add overlay → output. This keeps value-adds reusable across all types.

### YouTube Analytics API can lag well past 48h for a specific video, even when Studio/public view count already show data (fetch-metrics v1)
Confirmed against the real channel while first testing `src/platforms/youtube-analytics.ts` (ADR-0025): `dHDpDXSIAkA` (hardknocks_v1, uploaded 2026-07-10, public view count 1114 per `yt-dlp`, already past the 48h wait) returned zero for every metric — views, AVD, retention curve all empty — and doesn't appear at all in a channel-wide per-video breakdown that correctly returned real numbers for 8 *other*, older videos on the same channel (proving auth/query/channel-scoping were all correct, not a bug). The 48h rule (AGENTS.md's own "Metrics lag is real" pitfall, and ADR-0009's Analytics-lag research) describes when Studio-shown metrics stabilize — it does NOT guarantee the separate Analytics *reporting* API has finished indexing a brand-new, low-traffic-channel video by then. If `/fetch-metrics` returns an all-empty result for a video that's genuinely past 48h, treat it as "not indexed yet, retry in a day or two," not as "this video has zero engagement."

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

### `adelay` can still rebase every timed VO/SFX input to t=0 when it enters `amix` -- build real leading-silence samples (hardknocks v13)
Confirmed in `render_hardknocks_v13_billionaire_hunt.py` after the first full render: proof narration intended for t=34.6s, CTA narration intended for t=39.2s, ending narration intended for t=55.4s, and several delayed SFX all played together at the beginning, drowning the real hook. The filter order was already correct (`acompressor` → `loudnorm` → `adelay`), every ffmpeg command exited 0, and the visual timeline was correct; only hook/full ASR exposed the failure. An isolated delayed-track test explained it: `adelay` shifted the stream's PTS, but the downstream mix/mux path rebased that input to start at zero instead of preserving audible leading silence. `apad,atrim=0:<timeline>` only produced trailing silence after the rebased clip, so it did not help. Fix: for each timed audio asset, generate a full-duration PCM track by concatenating `anullsrc` for the intended delay with the already-normalized clip (`[silence][clip]concat`), then `apad,atrim` to the timeline length; mix those full-duration tracks with `amix`. This makes the delay actual silent samples, not timestamp metadata. Verification must include separate final ASR reads for hook, proof/CTA and tail; measuring the isolated source clip or trusting `adelay` syntax is insufficient.

### `loudnorm`'s `TP` (true-peak) ceiling caps achievable loudness on high-crest-factor clips -- a `TP=-1.5` clip with an -8dBTP raw peak will undershoot `I=-16` regardless of single-pass vs. two-pass mode (hardknocks b1/ruiz, VO-too-quiet fix)
Confirmed across all 4 narrator VO clips in `render_hardknocks_b1_ruiz.py`: each raw Qwen-TTS recording has a large peak-to-loudness ratio (crest factor) -- e.g. one clip measured -25.3 LUFS integrated but only -8.2 dBTP peak, a ~17dB crest factor from a single sharp transient. Loudnorm won't raise a clip's gain past the point where its peak would exceed the `TP` ceiling, so on a clip like this it stops well short of the `I` target and stays there -- verified this happens **identically** whether you use loudnorm's default single-pass "dynamic" mode or a proper two-pass "linear" mode with measured input stats (tried both; both landed at exactly the same -18.5 LUFS on the same clip, an initially confusing result that ruled out "single-pass inaccuracy" as the cause). The actual fix: apply a mild `acompressor` (e.g. `threshold=0.1:ratio=4:attack=5:release=100:makeup=1`) *before* `loudnorm` to reduce the crest factor first, so loudnorm can reach the target loudness without ever needing to touch the peak ceiling -- verified this brought all 4 clips within 0.8dB of the -16 LUFS target. If a two-pass `measured_I`/`measured_TP` diagnostic run reports a `target_offset` that doesn't budge between dynamic and linear mode, suspect the TP ceiling as the actual constraint, not the normalization algorithm.

### Hard-concatenated segments need their own audio fade in/out, or every cut sounds like a truncated, jammed-together splice (hardknocks b1/ruiz, cut-transition fix)
Confirmed in `render_hardknocks_b1_ruiz.py`: `build_base()` concatenates independently-rendered segments with `-f concat -c copy` (no crossfade), and each segment's own audio chain (`render_segment()`) ended with a flat `atrim`, no fade. Result: at every cut, whatever word was still naturally decaying got chopped off at full volume with zero taper, and the next segment's dialogue started immediately at full volume with no lead-in -- user-reported symptom was "the tail sound isn't clear and is noticeably quieter, and cuts feel jammed together with no pause." Fix: append a short `afade=t=in:st=0:d=0.12` and `afade=t=out:st={duration-0.20}:d=0.20` to each segment's own audio filter chain in `render_segment()`, BEFORE concatenation. This only reshapes the amplitude envelope within each clip's existing duration -- it does not add or remove any time, so video stays frame-accurate in sync; only the audio eases through the join. Verified via a fine 0.1s-step `volumedetect` scan straddling each cut: post-fix shows a clean ramp-down to near-silence right at the join and a ramp-back-up into the next segment, instead of a flat full-volume plateau on both sides with an instant jump between them. This applies to ANY renderer in this repo that hard-concatenates independently-rendered segments (not just this file) -- always fade each segment's own audio at both ends before concat, even when the video cut itself is a deliberate hard jump cut (this project's Active-Speaker Reframing style) with no video-side fade.

### Action space explosion
Under Plateau-Gated Cadence there is no honest fixed calendar convergence estimate; fragmentation across three lanes per vertical may slow inference further because channel history is a confounder. Don't expect early convergence.

## Boundaries

### Always
- Copy proven viral formats, repackage with variations
- Wait 48h before fetching YouTube Analytics (stable data)
- Apply Retention Techniques and ADR-0036's Information Progression, event-bound SFX and Loop-Payoff Closure to EVERY Short — they are base quality, not optional
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

## Mục tiêu hôm nay ưu tiên cao nhất khi tạo video
- Giảm tỉ lệ swiped away xuống dưới 20%
- Thử nghiệm mọi loại hook (âm thanh, hình ảnh) có thể để đạt được mục tiêu này
