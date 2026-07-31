# Codex Short-Form Media Review Prompt

Review the exact final Short as an independent editorial critic. Do not edit files. Inspect the supplied MP4, contact sheets, ASR, timeline, verification report and production contract. Use repository rules in `AGENTS.md`, `CONTEXT.md`, `docs/WORKFLOW.md` and ADR-0040.

Inputs supplied by the caller:

- exact-final MP4 and SHA-256;
- 0-10s contact sheet;
- full contact sheet;
- final ASR;
- timeline/source-use ledger;
- media verification report;
- production document;
- prior review, if any.

Score exactly these categories:

- hook clarity and stopping power: 25;
- expectation/open-loop integrity: 10;
- visual proof and information progression: 15;
- mobile caption readability/sync: 10;
- TTS/source-dialogue/sound mix: 15;
- pacing/no-dull-moment execution: 10;
- CTA/payoff/ending: 10;
- technical/compliance evidence: 5.

Rules:

1. `editorial_score` must equal the sum of all category scores.
2. Cite exact timestamps or artifact evidence for every deduction.
3. Return no more than three findings, ranked by expected retention impact.
4. Reject generic advice such as “more effects,” unsupported factual escalation, format invention or changes that violate source/voice rights and accepted ADRs.
5. Use `editorial_target_met` only when score is at least 98 and no editorial blocking defect remains.
6. Acknowledge that this score cannot guarantee virality or one million views and does not override publication rights, lane eligibility, naive-viewer evidence or mature Studio metrics.
7. If the evidence packet cannot support a category, deduct honestly and name the limitation; do not invent observation.

Return only JSON matching `docs/templates/codex-media-review.schema.json`.
