# ADR 0039: Global Zack-Style Internal Narrator

**Date:** 2026-07-30  
**Status:** Accepted

## Context

The user previously approved `ronald_wayne_zack_style_qwen` after a direct listening comparison and has now explicitly selected that delivery identity for all future videos, superseding ADR-0032's channel-scoped Finance narrator assignment. The profile uses Qwen3-TTS BaseModel zero-shot conditioning from a bounded public Zack D. Films reference. The reference is technically reproducible and the profile is hash-locked, but public availability is not voice-cloning consent.

The project needs one unambiguous runtime default without falsely treating a public voice as commercially licensed.

## Decision

1. `data/narrator-voices/default.json` is the machine-readable global pointer; it resolves `data/narrator-voices/ronald_wayne_zack_style_qwen/profile.json` as the default Synthetic Narration profile for every new English video and every material revision that regenerates TTS.
2. The profile status is `canonical_internal_only`. It may be used for internal drafts, editorial review and private evaluation.
3. Commercial publication remains blocked until explicit narrator consent/licensing permits this conditioning use, or the public-person reference is replaced by an authorized synthetic/stock/self-owned reference that passes a direct user listening comparison.
4. Every renderer/generator must resolve the profile by ID, verify the reference SHA-256 and pinned model revision, record generation settings/seeds, enforce the profile's `1.42x` maximum Rubber Band post-tempo and run final-MP4 ASR.
5. Edge TTS is not a final-quality fallback. A generation failure stops the production path; it does not silently change narrator identity.
6. Existing published artifacts are not retroactively changed. Existing unfinished projects change voice only when the user requests a material revision or their narration is regenerated for another reason.
7. Production documentation must disclose synthetic narration and state that Zack D. Films did not participate in or endorse the video.

## Supersession

This ADR supersedes ADR-0032 only for narrator assignment and scope:

- the Finance default `natural_talker_male_qwen_blog` is retired from new production;
- separate channel narrator identities are replaced by this global internal default.

ADR-0032's engine/model provenance, Apple Silicon, no-paid-API, direct-listening and commercial-rights gates remain active.

## Consequences

- Voice identity is consistent across future videos and no longer drifts by project.
- Current output can be evaluated internally with the user-selected delivery.
- A voice-rights gate is explicit rather than hidden inside renderer code.
- Reaching an editorial quality target does not override narrator-reference or footage publication rights.
