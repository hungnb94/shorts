# Short-Video Scriptwriting and Higgsfield Skill Research

Date: 2026-07-24 07:47 +07
Scope: reusable agent skills for 50–75 second vertical video, with emphasis on scripting, hook design, storyboard/shot planning, continuity, Higgsfield generation, cost control, and final media QC.

## Executive conclusion

There is no single public skill that is best end to end.

The strongest current pieces solve different parts of the problem:

- **Short-form scripting architecture:** `social-media-skills/skills` — especially `short-form-video-script` plus `scripting-and-storyboarding`.
- **Cinematic direction and prompt craft:** the official downloadable Higgsfield `seedance-shotlist-director`, supplemented by the dramaturgy and continuity ideas in `smixs/visual-skills`.
- **Live Higgsfield execution:** official `higgsfield-ai/skills` version `0.12.0` and Higgsfield CLI `1.1.19`.
- **End-to-end orchestration architecture:** ViMax, especially its separate screenwriter, storyboard, reference-selection, best-image-selection, continuity, and assembly stages.
- **Editing and artifact verification:** `browser-use/video-use` plus this repository's `short-form-video-quality-assurance`.

Each candidate also has a serious limitation:

- Public writing/storyboard skills do not execute Higgsfield jobs or control credits.
- Official Higgsfield skills execute models but have thin short-form narrative logic and weak final-video QC.
- Public model-specific prompt guides become stale quickly. A prominent July 2026 guide describes `seedance_2_5`, but the live Higgsfield catalog on this machine exposes only `seedance1_5`, `seedance_2_0`, and `seedance_2_0_mini`.
- ViMax is a framework rather than a Hermes skill, is not Higgsfield-CLI-first, and is not optimized for this project's 50–75 second Shorts format.
- Several local legacy skills contradict the current project baseline.

The right move is not to install one “best” skill or create a giant replacement `SKILL.md`. Build a small, contract-driven stack that combines the best ideas while keeping runtime model discovery, cost preflight, generation, and QC separate.

## Research method and evidence boundary

The audit used:

1. Local Hermes skill contents under `/Users/hung/.hermes/skills`.
2. Official Higgsfield skill repository and CLI documentation.
3. A downloadable Higgsfield `seedance-shotlist-director.skill` discovered from an official Higgsfield article and extracted locally for inspection.
4. Live Higgsfield CLI model, workflow, preset, and cost queries.
5. Public Agent Skills with inspectable `SKILL.md` files.
6. Open-source end-to-end video-agent frameworks.
7. Official YouTube and TikTok creator guidance.

This is an architecture and craft audit, not an empirical render benchmark. No paid generation was run. Public popularity is not treated as proof of output quality.

## Live Higgsfield verification

Verified on 2026-07-24:

- Higgsfield CLI: `1.1.19`, built 2026-07-18.
- Local `higgsfield-generate` skill: `0.12.0`.
- Local `higgsfield-video-explainer` skill: `0.12.0`.
- Upstream Higgsfield skill version marker: `0.12.0`.
- Live Seedance models: `seedance1_5`, `seedance_2_0`, `seedance_2_0_mini`.
- `seedance_2_5` is not present in the live model catalog.
- Ten live `video-explainer` presets are available.
- `explainer_video` is not present in the current model registry; both `model get` and cost preflight fail with `No model with job_type "explainer_video"`.

Verified dry-run costs for 720p, 9:16:

| Job | Duration | Cost |
|---|---:|---:|
| `seedance_2_0`, `mode=std` | 15s | 67.5 credits |
| `cinematic_studio_video_3_5` | 15s | 75 credits |
| `gemini_omni` | 10s | 30 credits |
| `seed_audio` | one short take | 0.3 credits |
| `nano_banana_2`, 2K style key | one image | 2 credits |

At the observed 301-credit balance:

- Four 15-second Seedance clips for a 60-second timeline cost 270 credits before retries, leaving 31.
- Four 15-second Cinema 3.5 clips cost 300 credits before retries, leaving 1.
- Six 10-second Gemini Omni clips plus six short Seed Audio takes cost at least 181.8 credits; a generated style key brings the known subtotal to 183.8, but the final `explainer_video` assembly cost cannot currently be queried because the model is unavailable.

Cost preflight and a hard retry cap are therefore production requirements, not optional UX polish.

## Best public references by component

### 1. Best scripting architecture: `social-media-skills/skills`

Useful skills:

- `short-form-video-script`
- `scripting-and-storyboarding`
- `hook-writer`

What is worth adopting:

- Separate the content promise from format execution.
- Write a three-track script: visual, on-screen text, spoken/audio.
- Treat the hook as a coordinated visual + text + spoken beat.
- Require a true payoff for the hook.
- Use the storyboard as a decision document, not decorative art.
- Number shots and make generation-ready shot briefs.
- Do runtime and feasibility math before production.

What must not be copied blindly:

- Its default target is roughly 15–35 seconds, not this project's 50–75 seconds.
- Some retention and sound-off claims come from marketing vendors rather than platform-first evidence.
- It assumes a human shoot and WoopSocial publishing, not Higgsfield execution.
- It has no reference-asset registry, model schema validation, cost cap, paid-generation recovery, or final MP4 QC.

Verdict: best structural reference for a new general `short-video-scriptwriter`, but not install-and-run production logic.

### 2. Best official Higgsfield directing reference: `seedance-shotlist-director`

What is worth adopting:

- Read the script as a director rather than splitting text mechanically.
- Explicit geo-spatial blocking.
- Camera movement must be motivated.
- Translate emotion into body action and micro-pauses.
- Carry wardrobe, props, weather, physical damage, and emotional state across shots.
- Use complete, standalone prompts with character and scene context repeated where necessary.
- Preserve scene numbering across revisions.

What must be changed:

- It hard-codes every prompt to 15 seconds, increasing cost and blast radius.
- Its default “8K IMAX” prefix over-specifies an unavailable output target and contains generic style inflation.
- Continuity is held “internally” rather than emitted as a machine-readable artifact. That breaks handoff between agents and sessions.
- It produces an HTML checklist but no model/input mapping, cost plan, job manifest, generation execution, or QC report.
- Its `/mnt/user-data/outputs/` path is not portable to this macOS/Hermes environment.
- It is film-first, not Shorts-first; it has no first-second hook gate, visual proof requirement, or 50–75 second narrative contract.

Verdict: the best official seed for a storyboard/director skill, but it needs a structured continuity bible and runtime-aware production layer.

### 3. Best cinematic craft library: `smixs/visual-skills`

What is worth adopting:

- Scene formula: desire + obstacle + space geometry + controlled gaze + editing rhythm.
- Every shot must change emotion, advance action, or increase pressure.
- Environmental pressure, physical micro-action, and a sound/visual motif make prompts concrete.
- Camera movement needs a reason.
- Shot cards include function, framing, composition, eye trace, duration, cut type, sound, light, and production note.
- Multi-clip prompts repeat complete continuity anchors.
- The continuity checklist and defect-specific prompt fixes are practical.

What must be treated as untrusted until runtime verification:

- Model names, versions, limits, and CLI syntax.
- Its `seedance_2_5` section is not supported by the live Higgsfield catalog tested here.
- Several claimed command flags do not map directly to the current Higgsfield CLI schema.
- The skill has no cost governance or paid-generation execution.

Verdict: strongest craft reference, but use only its model-agnostic dramaturgy and continuity concepts. Runtime contracts must come from Higgsfield CLI, never this static catalog.

### 4. Best end-to-end architecture reference: ViMax

What is worth adopting:

- Distinct agents/stages for screenwriting, script planning, scene extraction, storyboard design, character extraction, reference selection, first-frame generation, best-image selection, video generation, and final assembly.
- Persistent workspace artifacts and resumable sessions.
- Reference retrieval from earlier timeline frames.
- Generate multiple candidate first frames and use visual evaluation to select the most consistent.
- Parallelize compatible shots rather than serializing everything.
- Keep idea-to-video and script-to-video as separate entry points.

What must be adapted:

- It is a Python framework, not a reusable Hermes skill.
- It is not Higgsfield-CLI-first.
- It is general film/video infrastructure, not optimized for Shorts hook, HEIT, source-backed claims, captions, CTA, and this project's media gates.
- Parallelization without an explicit dependency graph can still break continuity.
- Its marketing claims should not substitute for local media QC.

Verdict: best architecture to learn from, not a drop-in replacement.

### 5. Best editing execution reference: `browser-use/video-use`

What is worth adopting:

- Inspect source media before choosing edit strategy.
- Snap cuts to word boundaries.
- Separate strategy confirmation from destructive editing.
- Verify the exact output before handoff.
- Persist reusable scripts and intermediate artifacts.

Limit:

- It is strongest for editing existing footage, not script-to-Higgsfield generation.

Verdict: use its artifact discipline and verification loop, not its domain model.

### 6. Useful but narrow references

- `AgriciDaniel/claude-shorts`: practical long-video clipping and ranking, but not original script-to-video production.
- `aicontentskills/ai-video-storyboard-skill`: useful storyboard fields and continuity warnings, but no execution or QC.
- `beshuaxian/higgsfield-seedance2-jineng`: broad genre prompt examples, but it is prompt-library-heavy, was not updated after 2026-04-09 at audit time, and lacks live schema validation, cost control, execution, and QC.
- `coreyhaines31/marketingskills/video`: broad tool-routing overview, but too general for a production contract.

## Official platform guidance that should shape the new stack

### YouTube

YouTube's 2025 Shorts deep dive emphasizes:

- the first second as the critical hook window;
- concise mini-stories or impactful moments;
- immediate shock or intrigue followed by satisfaction.

This supports the repository's stronger 0–3 second hook gate and argues against a script skill that begins with exposition.

YouTube's later creator guidance emphasizes authenticity, audience feedback, and using trends as tools rather than as the entire identity. For this project, the practical reconciliation is:

- copy proven format mechanics;
- do not copy another creator's words or identity;
- preserve a specific evidence-backed point of view.

### TikTok

TikTok's official Creative Codes use:

- hook → body → close;
- early value proposition;
- movement, transitions, text, and sound as attention tools;
- vertical high-resolution media with platform-safe UI zones;
- authentic, platform-native production rather than TV-style polish.

The 2025 SMB playbook reinforces planning scripts, props, timing, multiple angles, clear audio, real faces, showing rather than telling, and regular creative refresh.

This creates an important constraint for Higgsfield: cinematic polish is not automatically platform-native. A fully synthetic 60-second film can be less effective than a hybrid Short with authentic source voice, real proof, and one or two high-value generated scenes.

## Audit of the current local stack

### Keep and strengthen

#### `video/hook-design-for-shorts`

Strong mechanism diversity and scoring. Keep it as the hook specialist, but its selected hook must be emitted into the shared script/shot contract with:

- promised payoff;
- simultaneous visual proof;
- first-frame plan;
- caption and SFX timing;
- exact downstream shot IDs.

#### `creative/short-form-serialized-storytelling`

Strong for recurring fiction, causal callbacks, fair-play setups, and 50–75 second timing. Keep it as a niche writer. Do not make it the default scriptwriter for finance, health, or AI education.

#### `video/short-form-video-quality-assurance`

This is the strongest local completion gate. Keep it. Extend it with generative-video checks for identity drift, object-state continuity, physics, text artifacts, and inter-shot lighting consistency.

#### `higgsfield-generate`

Keep it as the live execution primitive and model/workflow discovery layer. Its local `SKILL.md` matches upstream version `0.12.0` at audit time.

Required correction: replace “Do not pre-estimate cost unless asked” with mandatory preflight for every paid plan, a total estimate, remaining-balance forecast, hard cap, and explicit approval before submission.

### Patch or quarantine

#### `higgsfield-video-explainer`

Good ideas:

- fact research before scripting;
- one style key across blocks;
- audio/video block pairing;
- ordered server-side assembly;
- regenerate only failed blocks.

Blocking issue:

- The skill requires `explainer_video`, but the live CLI cannot resolve that model on this account/environment. The skill cannot currently complete its promised final assembly path.

Action: quarantine paid use until the official model contract is available, or patch the workflow with a verified alternative assembler and exact cost preflight. Do not silently return loose clips.

#### `video/clip-curation-edit`

Contains valuable hard-earned production lessons, but the main file has stale and contradictory rules:

- 50–75 seconds in the current baseline, but 45–60 and ≤60 appear later.
- SRT/subtitles guidance conflicts with later “drawtext for all text” guidance.
- looping is presented as a workflow step despite later quality rules warning against repetitive looping.
- duplicated step numbering and historical implementation details make routing hard.

Action: split stable policy from renderer-specific troubleshooting; keep one current contract and move historical pitfalls into references.

### Deprecate as production entry points

#### `video/viral-v4-renderer`

It locks in legacy defaults that conflict with current policy: 30–60 seconds, Edge TTS voices, kitty mascot, Ken Burns stock-footage style, and a fixed six-video batch. Preserve only as historical reference.

#### `video/value-added-editing-viral-shorts`

It contains useful postmortems, but its main entry point is overgrown and stale: 30–60 seconds, lower-resolution source download examples, Edge TTS, Ken Burns guidance, and contradictory exploration policy. Extract durable lessons into current skills, then deprecate this as a top-level production workflow.

## Core gaps

1. **No general nonfiction scriptwriter** for finance, health, and AI education that combines research, HEIT, hook variants, visual proof, claim citations, caption/SFX plan, and 50–75 second timing.
2. **No shared handoff contract** between hook, script, storyboard, Higgsfield generation, assembly, and QC.
3. **No machine-readable continuity bible** for characters, wardrobe, props, locations, lighting, object-state progression, and reference assets.
4. **No runtime prompt compiler** that maps a shot to the current model schema instead of copying static flags.
5. **No dependency-aware generation plan**. Independent shots can run in parallel; shots that inherit a character state, end frame, prop state, or camera geometry must be serialized.
6. **No mandatory cost plan** with exact preflight, balance forecast, retry budget, hard cap, and approval boundary.
7. **No AI-specific defect taxonomy** for targeted retries.
8. **No evaluation suite covering the full script-to-final workflow**. Official Higgsfield evals have useful scenario discipline, but they are manual and do not test this project's 50–75 second artifact contract.
9. **No post-generation narrative review**. A collection of individually attractive shots can still fail as one coherent Short.

## Recommended target architecture

Do not create six unrelated giant skills. Use one orchestrator and three focused production modules, reusing the strongest existing skills.

### A. `short-video-studio` — orchestrator

Responsibilities:

- choose the correct writer/production path;
- maintain stage state;
- validate required artifacts before the next paid stage;
- never duplicate logic owned by a specialist skill.

Stages:

`reference format → research/evidence → hook → script → director plan → cost approval → generation → assembly → final QC → metadata`

### B. `short-video-scriptwriter` — general nonfiction writer

Inputs:

- vertical, audience, language, duration, platform;
- proven source format;
- source/evidence pack;
- current channel/series voice.

Outputs:

- one-sentence viewer promise;
- 5–10 hook candidates using different mechanisms;
- scored winner plus one alternate mechanism;
- claim/evidence map;
- timestamped three-track script: spoken/audio, visual proof/action, on-screen text/SFX;
- HEIT or another explicitly selected narrative model;
- exact word count, duration math, and payoff audit.

It should call existing `hook-design-for-shorts` rather than reimplement hook scoring.

### C. `short-video-director` — storyboard, continuity, shot manifest

Outputs:

- director treatment;
- continuity bible;
- asset/reference registry;
- timecoded shot manifest;
- shot dependency graph;
- transition and sound map;
- model-agnostic shot intent.

Every shot record should include at least:

- `shot_id`, `start`, `end`, `beat`, `function`;
- `visual_proof_or_action`;
- `frame`, `composition`, `camera`, `movement_reason`;
- `eye_trace`, `lighting`, `sound`, `transition`;
- `character_state_in`, `character_state_out`;
- `prop_state_in`, `prop_state_out`;
- `reference_assets`;
- `continuity_dependencies`;
- `final_frame`;
- `failure_risks`.

### D. `higgsfield-video-production` — compiler and paid execution

Responsibilities:

1. Query live models/workflows and inspect schemas.
2. Route each shot by capability, references, duration, quality, and cost.
3. Compile model-specific prompts from the model-agnostic manifest.
4. Run cost preflight for every job.
5. Produce total, remaining balance, retry reserve, and hard cap.
6. Ask for explicit approval before paid generation.
7. Generate anchors/first frames before expensive dependent video shots.
8. Parallelize only independent jobs.
9. Persist job IDs, inputs, outputs, costs, and status for resume.
10. Classify defects and regenerate only affected shots.
11. Assemble the real MP4 and hand it to `short-form-video-quality-assurance`.

Keep `higgsfield-generate` as the low-level execution dependency.

## Proposed artifact contracts

Use durable files rather than context-only handoffs:

- `creative-brief.yaml`
- `evidence-pack.md`
- `hook-candidates.json`
- `script.md`
- `continuity-bible.yaml`
- `shot-manifest.json`
- `generation-plan.json`
- `cost-plan.json`
- `jobs.json`
- `qc-report.md`
- final MP4 and canonical production metadata

Each artifact needs a schema version and the upstream artifact hash/version it was derived from. If the script changes, dependent shot, prompt, cost, job, and QC artifacts must be marked stale.

## Retry taxonomy

Never use blind “try again” retries.

| Failure class | Correct response |
|---|---|
| Prompt misunderstanding | simplify action, move critical instruction earlier, remove contradictions |
| Identity drift | strengthen reference set and exact identity anchors; regenerate dependent shots only |
| Wardrobe/prop/location drift | correct continuity state and reference mapping |
| Motion/camera artifact | reduce simultaneous actions/moves; shorten or split shot |
| Composition/eye-trace failure | revise framing and subject placement, not narrative copy |
| Text/logo artifact | remove generated text; add deterministic post overlay |
| Physics/anatomy defect | simplify interaction, use better start/end frames, route model if needed |
| Narrative mismatch | return to script/shot function; do not polish the wrong shot |
| Audio/dialogue mismatch | separate generated visuals from controlled VO/SFX or shorten dialogue |
| Model/schema failure | re-query live catalog; never invent model names or flags |

## Second- and third-order effects

### 1. Continuity failures compound

A wrong hero face, wardrobe, location, or prop state in an early anchor invalidates every dependent shot. Therefore canonical references must be approved before expensive generation, and dependency edges must be explicit.

### 2. Long clips reduce job count but increase blast radius

A failed 15-second generation is expensive and may invalidate several narrative beats at once. Use 5/10/15-second duration based on dramatic function and risk, not a universal 15-second block.

### 3. Shot-level optimization can damage whole-video rhythm

The most beautiful individual shot may be wrong for the sequence. Every candidate must be scored twice: local shot quality and contribution to hook/payoff/cadence across the assembled timeline.

### 4. Parallel generation can break causality

Parallelize only shots that share frozen references and do not inherit mutable state. A prop moving from unopened to broken, a wet wardrobe, or an end-frame match cut creates serial dependencies.

### 5. Static model catalogs become liabilities

New model marketing moves faster than skill maintenance. Runtime discovery is the source of truth. Static references should explain capabilities and decision principles, not assert current IDs or flags without a live check.

### 6. Retry budgets can grow exponentially

Without a hard cap, several shots × several defects × multiple model routes can consume the entire balance. Reserve credits for one targeted retry on critical shots, then stop and revise the plan.

### 7. Full-synthetic polish can reduce platform fit

TikTok's official guidance favors human, native, authentic content; YouTube emphasizes the immediate hook and compact story. Generic “cinematic AI” is increasingly commoditized. The defensible strategy is hybrid production:

- authentic source/voice or a distinctive owned narrator;
- real evidence/data/proof;
- Higgsfield for shots that cannot be filmed, high-entropy visual hooks, controlled metaphors, transitions, and signature scenes;
- deterministic captions, data visualization, watermark, and CTA in post.

This also lowers cost and continuity risk while preserving the project's three-source visual strategy.

### 8. More skills can make the system worse

Adding one skill per genre/model creates routing ambiguity and contradictory policy. Keep stable production contracts centralized, and place model/genre examples in references. A small orchestration graph beats a large flat skill catalog.

## Blue-ocean recommendation

Do not compete on “who can generate the prettiest generic AI video.” That capability is rapidly commoditizing.

Compete on a repeatable hybrid format:

1. proven viral narrative grammar;
2. source-backed claim and visible proof;
3. one recognizable channel motif/character/visual system;
4. Higgsfield-generated impossible shot or metaphor that becomes the signature pattern interrupt;
5. exact final-artifact QC and an auditable metrics feedback loop.

This is harder to copy than a prompt and cheaper than generating every second synthetically.

## Priority roadmap

### P0 — correctness and spend safety

1. Patch `higgsfield-generate` to require cost preflight, balance forecast, hard cap, and approval.
2. Quarantine `higgsfield-video-explainer` until the final assembler path is live and costable.
3. Create artifact schemas and the `short-video-studio` stage contract.
4. Create `short-video-scriptwriter` for 50–75 second nonfiction.
5. Create `short-video-director` with continuity bible and dependency graph.
6. Create `higgsfield-video-production` using live schema discovery and targeted retry.

### P1 — quality and regression prevention

1. Extend `short-form-video-quality-assurance` with AI-video continuity/physics/text checks.
2. Add dry-run evals and fixtures before any paid test.
3. Consolidate `clip-curation-edit`; separate current policy from historical troubleshooting.
4. Deprecate `viral-v4-renderer` and the overgrown `value-added-editing-viral-shorts` entry point after durable lessons are migrated.

### P2 — optimization

1. Add model-routing telemetry: model, parameters, cost, failure class, accepted/rejected result.
2. Add candidate-first-frame generation and visual selection for high-risk scenes.
3. Connect published performance back to hook mechanism, narrative format, and visual treatment after the required analytics delay.
4. Use the data to adjust routing and prompts; do not manually override the MAB's experiment selection.

## Acceptance tests before paid rollout

1. **Model drift:** a request for nonexistent `seedance_2_5` is rejected after live discovery; no job is submitted.
2. **Budget:** a 60-second all-Seedance plan reports 270 credits and the remaining balance before approval.
3. **Cap:** a plan that exceeds available balance or retry cap cannot submit.
4. **Script contract:** a finance/health/AI topic produces cited claims, exact timing, hook/payoff mapping, and three tracks.
5. **Continuity:** every generated shot has explicit input/output state and reference assets.
6. **Dependency graph:** independent shots may run in parallel; state-dependent shots cannot.
7. **Targeted retry:** one failed shot regenerates without resubmitting accepted siblings.
8. **Resume:** existing running/completed job IDs are reused rather than duplicated.
9. **Final artifact:** real MP4 passes technical probe, full decode, ASR, black/freeze/silence/loudness checks, manual frames, continuity review, and cold-viewer clarity.
10. **Invalidation:** any script/timeline/render change marks downstream cost/QC/hash evidence stale.

The official Higgsfield repository's 13 manual scenarios are a useful starting discipline, but the local suite must add Shorts timing, cost control, continuity, resume, targeted retry, and final-byte media verification.

## Sources

### Official Higgsfield

- Skills repository: https://github.com/higgsfield-ai/skills
- CLI repository: https://github.com/higgsfield-ai/cli
- Skills cookbook: https://github.com/higgsfield-ai/skills/blob/main/COOKBOOK.md
- Official eval method: https://github.com/higgsfield-ai/skills/tree/main/evals
- Seedance 2.0: https://higgsfield.ai/seedance/2.0
- Seedance 2.0 official ByteDance page: https://seed.bytedance.com/en/seedance2_0
- Higgsfield cinematic headphones article containing the downloadable shot-list skill: https://higgsfield.ai/blog/cinematic_headphones

### Public skills and frameworks

- Social Media Skills: https://github.com/social-media-skills/skills
- Visual Skills: https://github.com/smixs/visual-skills
- Video Use: https://github.com/browser-use/video-use
- ViMax: https://github.com/HKUDS/ViMax
- Claude Shorts: https://github.com/AgriciDaniel/claude-shorts
- AI Video Storyboard Skill: https://github.com/aicontentskills/ai-video-storyboard-skill
- Marketing Skills video skill: https://github.com/coreyhaines31/marketingskills/tree/main/skills/video
- Community Seedance/Higgsfield prompt collection: https://github.com/beshuaxian/higgsfield-seedance2-jineng

### Official platform guidance

- YouTube Shorts deep dive, 2025-01-28: https://blog.youtube/creator-and-artist-stories/youtube-shorts-deep-dive/
- YouTube “Five tips to master Shorts,” 2025-08-04: https://blog.youtube/creator-and-artist-stories/five-tips-to-master-shorts/
- TikTok Creative Codes: https://ads.tiktok.com/business/library/Creative_Codes_One_Pager_CA.pdf
- TikTok SMB Creative Playbook 2025: https://ads.tiktok.com/business/library/TikTok_SMB_Creative_Playbook_2025.pdf
