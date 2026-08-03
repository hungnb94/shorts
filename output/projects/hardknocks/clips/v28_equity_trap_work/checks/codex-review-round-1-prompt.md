You are the independent Codex media reviewer required by ADR-0040. Review this exact-final YouTube Short from scratch. Do not edit files. Be strict, evidence-first, and do not inflate the score to satisfy the >=98 target.

Artifact:
/Users/hung/code/ai/shorts/output/projects/hardknocks/final/2026-08-03-hardknocks_v28_equity_trap.mp4
SHA-256: 80045d7f11e5eba369e06d8d5c35c05aa44b09ba1a14bc94fae22b9b0b042434

Evidence:
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v28_equity_trap_work/checks/verification-summary.json
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v28_equity_trap_work/checks/final_asr.json
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v28_equity_trap_work/checks/hook-0-10-contact-sheet.jpg
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v28_equity_trap_work/checks/full-contact-sheet.jpg
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v28_equity_trap_work/checks/segment-midpoints.jpg
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v28_equity_trap_work/checks/boundary-pairs.jpg
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v28_equity_trap_work/checks/sfx-event-audit.json
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v28_equity_trap_work/timeline.json
- /Users/hung/code/ai/shorts/docs/production/hardknocks-v28-equity-trap.md

Evaluate the encoded MP4, not renderer intentions. You may use ffmpeg/ffprobe and read the evidence files. The premise is: source says a $10M property uses $2M buyer equity and $8M bank debt, then claims the bank takes all the risk; the edit counter-audits that claim through a 20% first-loss waterfall, cash-flow and underwriting guardrails, the current $875B 2026 CRE maturity wave, recourse, and a loop-closing verdict.

Hard requirements already measured: 57.8667s, 1080x1920 H.264/AAC, 30fps, -17.01 LUFS, -2.5 dBTP, no black/freeze/silence events, CTA at 40.47s, source use 23.86s / 3.008%, every source excerpt under 15s, all 15 retained SFX cues at least 3dB above the bed, complete exact-final ASR, frame-zero caption, and real moving face footage through the hook.

The source footage and canonical narrator are internal-only pending separate rights clearance. There is no naive-viewer or post-publication retention evidence. Treat those as release/measurement limitations, not editorial-score deductions. Do not claim virality.

Use the 100-point rubric in ADR-0040 and output JSON matching docs/templates/codex-media-review.schema.json. Category scores must sum exactly to editorial_score. Cite timestamps for every media finding. Return at most three actionable findings ranked by likely retention gain. `editorial_target_met` requires editorial_score >=98 and no media hard-gate failure; otherwise return `revise` or `blocked_external`.