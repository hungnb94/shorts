# Frame-0 Check and Cut Cadence

Adapted from `~/.hermes/skills/video/clip-curation-edit/references/hook-window-rule.md`.
That doc's postmortem technique (compare two videos' frame-0 content via pixel statistics)
is the reusable methodology here — but the *judgment* itself should be Claude looking directly
at the frame (via Read tool), matching how `docs/WORKFLOW.md` Stage 0 already does this check
("Check bằng mắt (visual inspection thủ công), không dùng script"). `inspect_image.py` is
optional supporting evidence, not the primary check.

## Frame-0 / Hook-Window check

For each video being analyzed, using the `hook_window_frames` from `extract_keyframes.py`'s
manifest (fixed-interval frames across the first ~10s):

1. Read the `t=0` frame directly. Does it show a human face or a clear
   action/prop — or a static title card / text graphic / B-roll establishing shot?
   (Hook-Window Rule / ADR-0017: title cards and static graphics at t=0 are the single
   highest-impact retention killer documented in this project — see the bacsihai V1 vs Dangote
   postmortem in `CONTEXT.md` → **Hook-Window Rule**.)
2. Note the timestamp of the first value-add overlay / on-screen graphic, if any. Compare
   against the ≤2s threshold.
3. Optionally, run `inspect_image.py` on the `t=0, 0.5, 2.0` frames for a quantitative
   skin-tone % / near-white % backup (useful when writing up *why* a frame reads as "faceless"
   for the report — pixel stats make the claim falsifiable instead of just asserted).

```bash
python3 scripts/inspect_image.py <hook_000_0.00.jpg> <hook_001_1.00.jpg> <hook_002_2.00.jpg>
```

## Cut cadence

`docs/WORKFLOW.md` Stage 0 item 6 requires "1 visual change mỗi 1-2s" in the 0-5s window
(ADR-0016 2-Second Rule, ADR-0018 cadence). To measure this objectively on someone else's
video:

1. Take the `scene_keyframes` timestamps from the manifest (ffmpeg scene-detect) that fall
   within the first 5-10s.
2. Compute the gaps between consecutive timestamps. Flag any gap >2s within the 0-5s window —
   that's either a static shot (if visually confirmed) or scene-detect simply missed a
   softer transition (zoom, overlay-only change, not a hard cut) — check the actual frames
   before concluding either way.
3. Report the observed cadence as a plain list of gaps (e.g. `[0.0, 1.2, 2.4, 3.9, 5.1]` →
   gaps `[1.2, 1.2, 1.5, 1.2]`), not just a pass/fail — the goal is to give future videos a
   concrete rhythm to imitate, not just confirm a rule was followed.

## Caption sync (ADR-0018)

If a transcript with word-level timestamps was fetched (Phase 2), check: does the burned-in
caption (if visible in frames) start at ≤0.2s, update every ~1-2s in 2-5 word bursts, with
one keyword visually emphasized? Derive burst duration from the actual transcript timing for
*this* video — do not assume the English-interview timing benchmarked in ADR-0018 transfers
directly to a different speaker/language's pacing.
