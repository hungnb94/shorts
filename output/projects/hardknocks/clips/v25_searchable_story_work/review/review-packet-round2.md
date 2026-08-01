# HardKnocks V25 — Review Round 2 Packet

Exact candidate:

- MP4: `/Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v25_searchable_story_work/candidate_v1_searchable_story.mp4`
- SHA-256: `542017396e8f872a878349688118be78141da4c43619c64bf524ee7a6cf77d97`
- Runtime/spec: 64.000s, 1080×1920, H.264/yuv420p, 30fps, AAC 48k stereo
- Automated verifier: PASS
- Verification report: `/Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v25_searchable_story_work/checks/verification-summary.json`
- Exact ASR: `/Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v25_searchable_story_work/qc/candidate-asr-round2.json`
- Timeline: `/Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v25_searchable_story_work/timeline.json`
- Production contract: `/Users/hung/code/ai/shorts/docs/production/hardknocks-v25-searchable-story-moat.md`
- Round-2 extracted frames and Apple Vision OCR/face data: `/tmp/v25_round2_frames/`

Round-1 findings applied:

1. Fixed protected hook crop at 1.04–2.20; Apple Vision now sees the 1.50s face fully in frame (`x=0.067`, `w=0.572`).
2. Added early `BEAST GAMES EDITORS` context anchor.
3. Replaced unsupported `UNSCRIPTED REACTIONS` with narrower `ALWAYS-ON FOOTAGE` wording.
4. Replaced `AI TRANSCRIBED IT` with evidence-safe `TRANSCRIBE + SEARCH`.
5. Changed attribution narration to `According to MrBeast`; final ASR reads `According to Mr. Beast`.
6. Compressed required Mid-Roll Triple CTA from 4.0s to 3.4s; it still asks Like, Subscribe and Comment and starts at 38.40s per project policy.
7. Added `SOURCE OPINION • MRBEAST`, `HARDKNOCKS COMMENTARY`, and `HARDKNOCKS INFERENCE` labels.
8. Changed isolated guardrail caption to `NOT 100x PRODUCTIVITY`.
9. Corrected Pexels asset labels per exact segment and changed `TASTE SCARCER` to `JUDGMENT SCARCER`.
10. Regenerated exact TTS, overlay, SFX timing, candidate, ASR and all automated QC evidence.

Hard constraints:

- Treat source rights and narrator publication licence as external release blockers, not render defects.
- A Mid-Roll Triple CTA beginning at 38–42s and asking Like, Subscribe and Comment is mandatory project policy; evaluate execution, do not recommend deleting or moving it to the tail.
- `100,000 → 1,000` is only a MrBeast-reported 100× smaller search space, never 100× productivity/cost/quality.
- Review round cap is three; this is round 2.

Required output: one score /100, timestamped BLOCKER/MAJOR/MINOR findings, and exact required edits only. A score of 98+ means editorial acceptance for local internal final; it is not a virality or rights guarantee.
