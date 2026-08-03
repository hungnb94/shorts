You are the independent Codex media reviewer required by ADR-0040. This is round 2 on a NEW exact-final artifact after applying all three timestamped round-1 findings. Review from scratch. Do not edit files. Be strict, evidence-first, and do not inflate the score.

Artifact:
/Users/hung/code/ai/shorts/output/projects/hardknocks/final/2026-08-03-hardknocks_v28_equity_trap.mp4
SHA-256: 8ccad35934b952cf1f2024297e29349a644eb124c2a3114c2e34a51c61020f36

Round-1 review:
/Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v28_equity_trap_work/checks/codex-review-round-1.json

Changes applied to exact final:
1. 00:24.97-00:31.37: replaced “loan-to-value is not the whole loan” with “LTV is only one underwriting test,” and updated the panel/captions.
2. 00:40.47-00:44.47: replaced the already-resolved “Buyer or bank?” poll with “Would you use 80% debt?” while retaining Like, Subscribe and Comment.
3. 00:50.87-00:57.87: replaced the ambiguous “bank owns what comes after” ending with “So neither side takes all the risk. Equity absorbs the first hit. Then the bank takes the next loss,” and updated the final panel/captions. Final ASR confirms the last word completes before the encoded tail.
4. Fixed the Qwen raw-audio cache so changed text is keyed by text, seed, reference hash, model revision, and generation settings; the new exact-final artifact uses regenerated audio, not stale cached narration.

Updated evidence:
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v28_equity_trap_work/checks/verification-summary.json
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v28_equity_trap_work/checks/final_asr.json
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v28_equity_trap_work/checks/hook-0-10-contact-sheet.jpg
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v28_equity_trap_work/checks/full-contact-sheet.jpg
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v28_equity_trap_work/checks/segment-midpoints.jpg
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v28_equity_trap_work/checks/boundary-pairs.jpg
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v28_equity_trap_work/checks/sfx-event-audit.json
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v28_equity_trap_work/timeline.json
- /Users/hung/code/ai/shorts/docs/production/hardknocks-v28-equity-trap.md

Hard requirements on this exact hash: 57.8667s, 1080x1920 H.264/AAC, 30fps, -16.98 LUFS, -2.5 dBTP, no black/freeze/silence events, CTA at 40.47s, source use 23.86s / 3.008%, every source excerpt under 15s, all 15 retained SFX cues at least 3dB above the bed, complete exact-final ASR, frame-zero caption, and moving face footage through the hook. Exact-final OCR/inspection also rechecked the changed underwriting, CTA and payoff panels; the payoff face remains centered.

Source footage and canonical narrator are internal-only pending separate rights clearance. There is no Related Video destination, naive-viewer evidence, or post-publication retention evidence. Treat those as release/measurement limitations, not editorial-score deductions. Do not claim virality.

Use the fixed 100-point ADR-0040 rubric and output JSON matching docs/templates/codex-media-review.schema.json. Category scores must sum exactly to editorial_score. Cite timestamps for every finding. Return at most three actionable findings ranked by likely retention gain. `editorial_target_met` requires editorial_score >=98 and no media hard-gate failure; otherwise return `revise` or `blocked_external`.