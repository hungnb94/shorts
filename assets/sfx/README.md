# Shared SFX Library

This directory is the machine-readable foundation for the rights-aware SFX system in ADR-0038. It intentionally starts with no promoted assets: existing per-project files must be audited rather than silently declared safe or production-approved.

`manifest.schema.json` is fail-closed for promoted assets: an `approved` entry must have a repository path and `cleared` or `attribution_required` rights; generated assets require a reproducible recipe, and non-generated assets require exact source/license URLs.

Each future manifest entry must contain:

- `id`: stable semantic ID;
- `path`: repository-relative asset path;
- `family`: `diegetic_foley`, `motion_transition`, `state_emphasis`, `tension_context`, or quarantined `meme_voice_reference`;
- `role`: specific role such as `whoosh`, `impact`, `riser` or `ambience`;
- `origin`: `recorded`, `generated`, `youtube_audio_library`, `freesound_cc0`, `freesound_cc_by`, `licensed_third_party`, or `reference_only`;
- `source_url`: exact source page, not only a domain;
- `license_name` and `license_url`, or a reproducible `generation_recipe`;
- `attribution`: exact required copy or an empty string;
- `sha256`, `duration_s`, `sample_rate_hz`, and `channels`;
- `approval_status`: `candidate`, `approved`, or `retired`;
- `rights_status`: `cleared`, `attribution_required`, `reference_only`, or `blocked`;
- `audition_notes`: vertical, full-mix context and human review result.

Rules:

1. Do not place downloaded MyInstants audio in the production library without independent commercial rights.
2. Do not promote an asset merely because a completed renderer already used it.
3. Keep timing and per-video gain in the production SFX Event Ledger, not in this asset manifest.
4. Hash the exact bytes that enter the render and preserve required attribution in the canonical production document.
