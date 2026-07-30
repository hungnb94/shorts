# V10 Stage-0 Code Change Report

Date: 2026-07-30
Scope: code and production documentation only
Media synthesis/rendering: not run
Review JSON creation/refresh: not run

## Exact changes

- Added `pipeline/capytech/preflight_capytech_v10_zack_hook.py`.
  - Calls `renderer.validate_inputs(require_stage0_review=False)`, so canonical
    TTS/provenance and the current Codex implementation review remain blocking.
  - Defines an exact 150-frame schedule at 30 fps: `hook_host` 23 frames,
    `hook_split` 21, `hook_scale` 24, `hook_powered` 22, and `waist_action`
    continuation 60.
  - Reuses `renderer.render_piece()` and therefore the current
    `renderer.source_filter()` sharp dynamic full-bleed crop.
  - Calls `renderer.write_captions(tts)` and burns the full canonical ASS.
  - Places the canonical hook PCM through `renderer.timed_audio()`.
  - Reuses the renderer's procedural sine bed and `hook_whoosh` early hit
    recipe.
  - Specifies native 1080x1920, CFR 30, 150 frames, H.264 High/yuv420p CRF 15,
    AAC 48 kHz stereo at 192 kbps.
  - Writes the preview, deterministic canonical JSON manifest, deterministic
    eight-frame contact sheet, and contact frames under the V10 Stage-0 folder.

- Changed `render_capytech_v10_zack_reaction_explainer.py`.
  - `validate_inputs(require_stage0_review: bool = True)` now always enforces
    existing source, storyboard, Zack TTS identity/model/weight/fitting,
    per-line PCM hash, ASR timing, and current implementation-review bindings.
  - A full render additionally requires the external Stage-0 naive-view gate.
  - The gate requires exact status `PASS_STAGE0_EXTERNAL_NAIVE_VIEW`, parseable
    UTC, nonempty reviewer and reviewer type, eight exact true assessment
    fields, and current hashes for preview, hook manifest, storyboard, TTS
    manifest, renderer, and preflight.
  - Added the preflight script to the implementation-review binding set.
  - Parameterized the existing procedural-audio function by total duration,
    selected event IDs, and output directory. Defaults preserve the full
    renderer's current 58-second audio behavior.
  - Removed the duplicate implementation-review call from `main()`; the
    returned review record still populates the immutable render manifest.

- Changed `verify_capytech_v10_zack_reaction_explainer.py`.
  - Added the preflight script to required inputs, provenance existence checks,
    and expected implementation-review bindings.
  - Added an independent Stage-0 adjudicator with the same current hashes,
    exact pass status, UTC/reviewer requirements, and exact assessment set.
  - Added `stage0_external_naive_view_current_and_passed` as a blocking final
    gate and records its status in the exact-final report.

- Changed `docs/production/capytech-v10-zack-reaction-explainer.md`.
  - Declared sub-format `Clip Curation Edit - Multi-Source Reaction Explainer`.
  - Added `Why This Segment`.
  - Documented the preflight artifact contract, external review gate, five V10
    scripts, and the required execution order.

## Findings

- Canonical V10 TTS is not currently present. This is expected: the preflight
  is intentionally non-runnable until final canonical TTS exists.
- The existing `codex_implementation_review.json` is now intentionally stale
  because renderer, verifier, and the new preflight hashes changed. It was not
  refreshed, per instruction.
- `stage0_external_naive_view.json` was not created. Full rendering therefore
  remains correctly blocked.
- Existing reaction, CRF15, sharp full-bleed, mechanism, frame-plan, voice,
  audio, and immutable QC paths were not regenerated or relaxed.

## Checks run

- `python3 -m py_compile` passed for preflight, renderer, and verifier.
- Python AST parsing passed for all three scripts.
- Every existing JSON file under `output/projects/capytech/` parsed
  successfully.
- `git diff --check` passed.
- Changed Python files contain no trailing whitespace. Existing CommonMark
  hard-break spaces in the production Markdown were preserved.
- Contract grep confirmed the preflight `False` call, renderer default full
  gate, independent verifier gate, preflight implementation bindings,
  Clip Curation declaration, and `Why This Segment`.

## Source hashes after checks

- Preflight:
  `47d8c1dc1a253d6c55ff3984bd894c2aeddc2f2b34b43941baa354c211a12415`
- Renderer:
  `5b8121655fc02b95254f2efe572caf917a64eca26a63894ab21ea96454922197`
- Verifier:
  `095150f452bd32aefb28f54253b976ebdcf1bf3711726a51da8ca50d15fc4c53`
- Production document:
  `d597fcd778384e2ef9201402dfaf196cfb4962d5f47c9047ec0abc0b7261cfbd`
