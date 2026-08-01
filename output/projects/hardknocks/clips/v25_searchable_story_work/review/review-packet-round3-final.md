# HardKnocks V25 — Final Review Round 3/3

Exact candidate:

- MP4: `/Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v25_searchable_story_work/candidate_v1_searchable_story.mp4`
- SHA-256: `f892e52b7e1619c90a0714b3163851cf30041df1ebd13de8f528a9845e54c7f8`
- Automated verifier: PASS, 64.000s, 1080×1920, H.264/yuv420p, 30fps, AAC 48k stereo, -16.27 LUFS, -1.83 dBTP, no black/freeze/silence events, full decode PASS.
- Verifier report: `/Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v25_searchable_story_work/checks/verification-summary.json`
- Exact ASR: `/Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v25_searchable_story_work/qc/candidate-asr-round3-final.json`
- Exact frame/Vision evidence, extracted after this candidate was rendered: `/tmp/v25_round3_final/vision.jsonl`
- Production contract: `/Users/hung/code/ai/shorts/docs/production/hardknocks-v25-searchable-story-moat.md`

Round-2 findings addressed:

1. Protected hook now uses piecewise active-face tracking. Exact Apple Vision bounds remain fully inside frame at sampled `0.80, 1.00, 1.07, 1.20, 1.40, 1.60, 1.80, 2.00, 2.17s`; tightest horizontal margin is 5.5%.
2. Fixed the root crop defect: FFmpeg dynamic `scale=eval=frame` dimensions caused downstream crop coordinates to act against stale `in_w` after zoom changes. All hard-angle source sequences now use constant scale/zoom with focus re-anchors. Exact source frames at `13.40, 15.00, 16.60, 18.20, 45.16, 45.64, 46.60, 47.50s` keep detected face boxes fully in frame.
3. Mobile-readable critical straps are now larger and shorter: `BEAST GAMES • EDIT TEAM`, `MRBEAST OPINION`, `HK COMMENTARY`, `HK INFERENCE`.
4. Replaced the ambiguous `≠ 100x PRODUCTIVITY` glyph with literal `NOT 100x PRODUCTIVITY`.
5. Moved CTA captions down 30 master pixels and changed the UI text to `TOOL  OR  REPLACEMENT?`; CTA still begins 38.40s and asks Like, Subscribe and Comment.
6. Final ASR remains complete through `deserved the story`; claim/opinion/inference boundaries are unchanged and labeled.

This is the third and final review round. Required output: score /100, BLOCKER/MAJOR/MINOR findings bound to exact timestamps. A score ≥98 accepts local internal promotion; rights blockers are external and do not count as render defects. Do not ask for or recommend a fourth review round.
