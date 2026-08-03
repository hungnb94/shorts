You are the independent Codex media reviewer required by ADR-0040. Review the NEW exact-final HardKnocks V28 artifact after a user-reported active-speaker framing correction. Review from scratch and do not inherit the prior 99 score. Do not edit files.

Exact artifact:
- path: output/projects/hardknocks/final/2026-08-03-hardknocks_v28_equity_trap.mp4
- SHA-256: 6cc5e169c8469eeb45b2c90969490a5e76e8a62a334c23f48ae7e55cc717e277
- duration: 57.866667s

Primary regression under review:
- Source is a stable two-shot.
- Apple Vision source-frame boxes put the active left face at normalized x=0.309–0.397, mean 0.364.
- Lower-face temporal motion is 1.66x–3.02x higher on the left in every original-dialogue window, identifying the left person as the active speaker.
- Prior master used focus=0.64, crop center x=0.596 and incorrectly centered the right listener.
- New master explicitly marks every source-backed segment as speaker=ben_left, focus=0.30; crop center x=0.363.

Inspect these attached artifacts carefully:
- active-speaker sweep: 21 exact-final frames, start/mid/end for all seven source-backed shots;
- hook contact sheet;
- full contact sheet;
- segment midpoints;
- boundary pairs.

Read:
- output/projects/hardknocks/clips/v28_equity_trap_work/speaker_audit/speaker-map.json
- output/projects/hardknocks/clips/v28_equity_trap_work/checks/verification-summary.json
- output/projects/hardknocks/clips/v28_equity_trap_work/checks/final_asr.json
- docs/production/hardknocks-v28-equity-trap.md
- docs/templates/codex-media-review.schema.json

Evaluate:
- whether the left active speaker is now retained and compositionally prioritized across all source-dialogue shots;
- whether any source shot still centers the right listener, clips the active face, or switches late;
- hook, expectation/open loop, visual proof progression, captions/mobile legibility, voice/SFX/music, pacing, CTA, payoff and technical compliance;
- regressions caused by the crop change, especially text/face collision, head clipping, misleading lip-sync or missing context.

Score with the schema's 100-point rubric. Report only timestamped, actionable defects. Rights, Related Video and cold-viewer limitations remain release blockers but are not reasons to invent editorial defects. Target remains >=98; do not inflate the score.
