You are the independent Codex media reviewer required by ADR-0040. Review the exact-final YouTube Short below. Do not edit files. Be strict, evidence-first, and do not inflate the score to satisfy the target.

Exact artifact:
/Users/hung/code/ai/shorts/output/projects/hardknocks/final/2026-07-30-hardknocks_v22r1_seventy_eight_tail.mp4
SHA-256: fe2c7a3b1c9e3d2f665fd88b22ac035767bf7a29c5d59d79fd79f484e20994fd

Evidence:
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v22r1_seventy_eight_work/checks/verification-summary.json
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v22r1_seventy_eight_work/checks/final-asr.json
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v22r1_seventy_eight_work/checks/hook-0-10-contact-sheet.jpg
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v22r1_seventy_eight_work/checks/full-contact-sheet.jpg
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v22r1_seventy_eight_work/checks/sfx-timing-summary.json
- /Users/hung/code/ai/shorts/output/projects/hardknocks/clips/v22r1_seventy_eight_work/timeline.json
- /Users/hung/code/ai/shorts/docs/production/hardknocks-v22-seventy-eight-tail.md

Evaluate the current artifact, not intentions in code. Inspect the MP4 and supplied images. The premise is: $5M jet cost -> $78 origin -> question -> tail-number promise -> home sleep testing -> service/team mechanism -> jet payoff. The first three seconds are source Q&A: “How much did the jet cost?” / “over $5 million.” The Zack-style narrator is an internal-only voice-conditioning experiment; rights are a separate release blocker and must not be counted in editorial_score.

Use the 100-point rubric in ADR-0040 and output JSON matching docs/templates/codex-media-review.schema.json. Category scores must sum exactly to editorial_score. Cite timestamps for every media finding. Return at most three actionable findings ranked by likely retention gain. `PASS` requires editorial_score >=98 and no media hard-gate failure; otherwise use `REVISE` or `BLOCKED`. Lack of human listening and source-footage/narrator consent should appear in limitations, not fabricated as completed checks.