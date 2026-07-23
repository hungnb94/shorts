# HardKnocks Theragun Dual-Hook Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce two independently watchable, fully verified 50–75s Shorts from source `xv8qaYubDw4`, using the two winning verbatim cold opens selected in the design.

**Architecture:** One self-contained one-off Python renderer defines shared media helpers and two variant manifests. Each manifest assembles original-voice source clips with active-speaker reframing, proof-coupled Pexels inserts, ASS overlays/captions, post-render value-add compositing, audio transitions, CTA, and watermark. Completion is based on the two real MP4 artifacts and media QC, not renderer unit tests.

**Tech Stack:** Python 3, ffmpeg/ffprobe, Pillow, mlx-whisper transcript data, Pexels API assets, ASS subtitles.

---

## File Map

- Create: `pipeline/hardknocks/render_hardknocks_v14_theragun_dual.py` — shared renderer plus V14A/V14B manifests, render, and validation entry points.
- Create: `docs/production/hardknocks-v14a-250-jigsaws.md` — V14A production record and canonical upload package.
- Create: `docs/production/hardknocks-v14b-saved-two-lives.md` — V14B production record and canonical upload package.
- Modify: `data/source_videos.csv` — register source use once.
- Preserve: `output/projects/hardknocks/source/xv8qaYubDw4.mp4` — 4K source master.
- Generate: `output/projects/hardknocks/clips/v14_theragun_work/` — research, assets, intermediates, timelines, and QC evidence.
- Generate: `output/projects/hardknocks/final/2026-07-23-hardknocks_v14a_250_jigsaws.mp4`.
- Generate: `output/projects/hardknocks/final/2026-07-23-hardknocks_v14b_saved_two_lives.mp4`.

## Task 1: Lock Source Windows and Shot Manifests

- [ ] Read `transcript.json` word timestamps around the selected beats: 16.40–22.78, 195.04–197.18, 242.42–249.22, 366.54–386.80, 604.92–613.82, 671.22–687.12, 795.06–800.60, 908.86–926.12, 976.64–1009.76, and 1087.44–1117.06.
- [ ] Extract representative frames from every retained candidate window from the 4K master and reject any start that lacks a readable face/action state.
- [ ] Write two machine-readable manifests inside the renderer. Each clip must contain `name`, `source_start`, `source_end`, `speaker`, `semantic_role`, `crop_target`, `framing_level`, `punch_in_word`, `b_roll_asset`, and `b_roll_mode`.
- [ ] Keep every source-audio segment strictly under 15s; split longer ideas at word boundaries.
- [ ] For V14A, sequence: 250 jigsaws → bolt/foam recipe → saved-life validation → athlete trunk signal → father rejection → business lesson.
- [ ] For V14B, sequence: saved-two-lives verdict → crash → 10/10 pain/clinic contradiction → vibrating-table relief → jigsaw patient test → mission payoff.
- [ ] Calculate pre-speed and post-speed duration; adjust only by adding/removing complete semantic beats until each target lands inside 50–75s.

## Task 2: Acquire and Gate Pexels Assets

- [ ] Use the Pexels API workflow from `video:pexels-download`; never print or pass the API key as an argument.
- [ ] Search for three classes of footage: close-up power-tool/jigsaw motion, workshop prototype assembly, and physical recovery/shoulder treatment.
- [ ] Download the highest useful rendition for the selected assets into `output/shared/pexels/`.
- [ ] Run ffprobe, full decode, and start/mid/end contact sheets for every asset.
- [ ] Reject footage with visible consumer brands, unsafe tool use, misleading medical treatment, static composition, watermarks, or resolution below the production need.
- [ ] Record approved Pexels IDs, URLs, classification (`ILLUSTRATION`), and exact source windows in both production docs.

## Task 3: Build Shared Renderer Infrastructure

- [ ] Create `pipeline/hardknocks/render_hardknocks_v14_theragun_dual.py` by reusing only verified patterns from `render_hardknocks_v13_billionaire_hunt.py`: command runner, active-speaker crop, uniform caption-band crop/zoom, per-segment audio fades, ASS generation, full-duration timed audio tracks, CTA, moving watermark, post-speed finish, and validation.
- [ ] Keep variant data separate from rendering helpers through immutable manifest/dataclass values.
- [ ] Reconstruct Whisper captions by concatenating raw word tokens and stripping once; never join stripped words with spaces.
- [ ] Generate 2–5-word Komika Axis caption bursts aligned to word timestamps and emphasize one semantic keyword per burst.
- [ ] Add per-segment 0.12s fade-in and 0.20s fade-out before hard concat.
- [ ] Apply one uniform project-derived speed-up to video/audio only after base assembly; do not copy V13's 1.12x without checking this speaker's pause-gap distribution.
- [ ] Render value-add overlays after the base timeline, not inside segment extraction.
- [ ] Do not create or modify `test_render_*.py` files.

## Task 4: Implement V14A — 250 Jigsaws

- [ ] Open on source 908.86s with Jason's moving face/hand gesture and exact original audio.
- [ ] Show `250 JIGSAWS.` by t=0.2s, then `WHY?`; place a partial moving tool insert without covering Jason.
- [ ] Land a mechanical click/impact SFX in t=0–1s.
- [ ] Resolve the first hook gap by t=5–8s with the bolt + foam ball + first Theragun causal chain.
- [ ] Add animated counter, exploded prototype recipe, 2008/2009 timeline labels, source citation, and Business Lesson Payoff.
- [ ] Keep full-screen b-roll disabled until t≥10s.
- [ ] Begin the custom Like/Subscribe/Comment CTA within t=38–42s without interrupting the primary proof reveal.
- [ ] Move `HARD KNOCKS LAB` watermark across at least three non-obstructive positions.
- [ ] Render `output/projects/hardknocks/final/2026-07-23-hardknocks_v14a_250_jigsaws.mp4`.

## Task 5: Implement V14B — Saved Two Lives

- [ ] Open cleanly at source 795.06s on `Doc, this thing saved my life`, not on the connective words before it.
- [ ] Show `THIS THING SAVED TWO LIVES` by t=0.2s while withholding the object identity.
- [ ] Land heartbeat-to-mechanical-click SFX in t=0–1s.
- [ ] Use a partial silhouette/object insert while preserving Jason's face; resolve the jigsaw/Theragun identity by t=5–8s.
- [ ] Add the `PATIENT`/`FOUNDER` consequence counter, animated crash→pain→vibration→prototype causal chain, source citation, and Business Lesson Payoff.
- [ ] Keep full-screen b-roll disabled until t≥10s.
- [ ] Begin the custom Like/Subscribe/Comment CTA within t=38–42s after the main causal reveal.
- [ ] Move `HARD KNOCKS LAB` watermark across at least three non-obstructive positions.
- [ ] Render `output/projects/hardknocks/final/2026-07-23-hardknocks_v14b_saved_two_lives.mp4`.

## Task 6: Run Technical and Semantic QC

For both final files:

- [ ] Run ffprobe and verify 1080x1920, H.264/yuv420p, 30fps, AAC 48kHz stereo, and 50–75s.
- [ ] Run a full decode to null and require exit code 0.
- [ ] Run blackdetect, freezedetect, silencedetect, and ebur128/loudnorm measurement.
- [ ] Extract and transcribe 0–10s, CTA, and tail windows from the final mix; verify no duplicated audio, missing first words, or clipped payoff.
- [ ] Generate required 12-frame 0–6s hook sheet at 0.5s intervals and 12-frame arc sheet at 4s intervals.
- [ ] Extract frames at 0.0/0.2/0.6/1.2/1.8/2.5/3.0/5.0/8.0s and manually confirm face continuity, overlay readability, caption sync, and no full-screen face blackout.
- [ ] Scan lower image rows at distributed timestamps to reject a permanent black footer.
- [ ] Review every audio hard-cut boundary with 0.1s volume slices and listen to the final videos continuously.
- [ ] If a QC item fails, fix the root cause, rerender the affected variant, and rerun every affected gate on the new final artifact.

## Task 7: Document and Register

- [ ] Append one row for `xv8qaYubDw4` to `data/source_videos.csv`, listing both V14A and V14B.
- [ ] Write `docs/production/hardknocks-v14a-250-jigsaws.md` with specs, timeline, hook formula, source windows, Transformative Gate math, value-adds, Pexels attribution, QC evidence, known issues, canonical upload package, Studio settings, and Post-Production Retro.
- [ ] Write `docs/production/hardknocks-v14b-saved-two-lives.md` with the same complete sections.
- [ ] For each video, supply exactly one title ≤30 visible characters in Title Case with exactly two emojis; description line one mirrors the title and ends with exactly three hashtags including `#shorts`; list exactly three separate Studio tags.
- [ ] Keep upload status queued/blocked pending ADR-0035 lane eligibility, exact playlist, approved Upload Details Template, and Related Video resolution.
- [ ] Do not append to `EXPERIMENT-LOG.md` until a real upload occurs.
- [ ] Complete Hook Retro and Workflow Delta for both videos; update workflow/ADR/pitfall documentation only if production reveals a genuinely reusable new rule.

## Task 8: Final Verification

- [ ] Re-run fresh ffprobe, full decode, final ASR, detector, and contact-sheet commands after the final edit timestamp.
- [ ] Compare both artifacts side by side: V14A must remain the product-build/absurd-number story; V14B must remain the human-consequence/discovery story.
- [ ] Run `git status --short` and inspect the diff to ensure no secrets, source media, generated intermediates, or unrelated files are staged/tracked.
- [ ] Report both absolute artifact paths, verified specs, hook text, QC evidence paths, and canonical upload packages. Do not upload, commit, or push.
