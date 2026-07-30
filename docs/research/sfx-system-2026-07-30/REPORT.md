# Event-Bound SFX System — Reference Analysis and Strategy

**Snapshot:** 2026-07-30  
**Reference video:** [Hướng dẫn làm hiệu ứng âm thanh cơ bản (Phần 1)](https://www.youtube.com/watch?v=_ALr4tip3-c) by Cường — Làm Phim Nghiệp Dư  
**Discovery site supplied by the user:** [MyInstants Viet Nam index](https://www.myinstants.com/en/index/vn/)  
**Policy decision:** [ADR-0038](../../adr/0038-event-ledger-sfx-library-and-rights-gate.md)

## Executive decision

Build a reusable **sonic grammar**, not a folder of random viral buttons.

The reference video contributes a strong planning method:

1. lock tone/mood;
2. mark all meaningful actions before searching;
3. divide sounds into real/diegetic and designed/non-literal families;
4. search by the sound's function and physical source;
5. align every selected sound to an event.

MyInstants is useful for discovering audience-recognizable names, meme conventions and search vocabulary. It is **not a production-rights source by default**. Its Terms grant access for personal, noncommercial use and do not give the project commercial publication rights to user-uploaded sounds. Therefore MyInstants candidates remain `reference_only` until independent commercial rights are documented.

The project should differentiate through an owned/cleared sonic palette: recorded foley, procedural sound design, YouTube Audio Library effects, and individually verified CC0/CC-BY assets. This avoids the game-theory trap in which every editor uses the same Vine Boom/Anime Wow buttons until they become predictable, credibility-reducing and legally fragile.

## Evidence packet

### Public source snapshot

| Field | Value |
|---|---|
| Video ID | `_ALr4tip3-c` |
| Public title | `Hướng dẫn làm hiệu ứng âm thanh cơ bản (Phần 1)` |
| Channel | `Cường - - Làm Phim Nghiệp Dư` |
| Upload date | 2023-05-29 |
| Duration | 560.948s |
| Public views | 30,421 |
| Public likes | 1,111 |
| Public comments | 46 |
| Reviewed source | 3840x2160, 24 fps, AV1 + 48 kHz stereo Opus |

These counters are a 2026-07-30 snapshot, not causal evidence that the SFX method created the video's outcome.

### Audio measurements

| Measurement | Result |
|---|---:|
| Integrated loudness | -19.13 LUFS |
| True peak | +1.39 dBTP |
| Loudness range | 6.50 LU |
| Silence at -38 dB for at least 250 ms | 16 events / 6.212s total |
| Silence share | 1.11% |

The source is dense and dialogue-led. A 100 ms fast-rise proxy found 651 sharp level increases, but that count includes speech attacks, music, edits and SFX; it is **not** an SFX detector and is not used as a production quota.

## What the reference actually demonstrates

### Observed timeline

| Source window | Observed lesson | Project transfer |
|---|---|---|
| 00:00–00:24 | Pain, suspense, text appearance, action and transition examples precede the definition | Let the opening demonstrate the emotional job before explaining terminology |
| 03:06–04:08 | Lock playful/serious and light/dramatic tone before choosing effects | Add a per-video `Sonic Intent` before asset search |
| 04:08–05:10 | Mark every desired action on the edit timeline; name and color markers | Build the SFX Event Ledger from the actual EDL |
| 05:17–06:37 | Real sounds: doors, brakes, footsteps, cutting/opening; field recording improves fit | Prefer source/location sound or recorded foley when the event exists physically |
| 06:37–07:10 | Non-literal sounds communicate a different meaning than the pictured action | Use designed sound only when its semantic job is explicit |
| 07:10–07:52 | `whoosh` communicates speed/weight and exists in many variants | Search by motion, weight, material and intensity; do not use one universal whoosh |
| 07:52–08:14 | `drone` supports waiting, anxiety, mystery and anticipation | Reserve sustained tension for an unresolved state, not constant decoration |
| 08:14–09:03 | `ambience` adds place/context: forest, city, airport and similar spaces | Treat ambience as contextual information, distinct from event SFX |
| 09:03–09:13 | Additional visible keywords: `whip`, `hit`, `drop`, `sub-drop`, `impact`, `riser`, `pop` | Establish a controlled designed-SFX vocabulary rather than ad hoc filenames |

### Evidence labels

**Observed:** the source explicitly teaches mood lock, timeline markers, real versus non-literal sounds, direct recording, and the listed keyword families. Fixed frames show timeline markers, a marker index, search translation, category labels and the keyword list.

**Plausible:** planning sounds from an event ledger should reduce random effects, accelerate search and improve semantic fit. A stable sonic palette should improve brand consistency and reduce repeated audition work.

**Unproven:** the source does not isolate an optimal SFX count, volume, timing offset, retention lift or viral effect. Its public views do not prove causality. Exact density and family choices remain matched-test hypotheses.

## Current repository gap analysis

1. **No shared asset registry.** `assets/` contains fonts but no SFX manifest, rights ledger or approved palette.
2. **Per-renderer duplication.** HardKnocks V20 and V21 independently generate the same `cash_chime.wav` and pink-noise `whoosh.wav` logic.
3. **Semantic overloading.** V21 reuses one whoosh for hook, financing, CTA comment and search; one cash chime represents portfolio, cash flow and revenue. The timing is event-bound, but the sound identity does not distinguish the events.
4. **No pre-search vocabulary.** Renderers define files after the story is built rather than preserving a mood → marker → query → candidate decision trail.
5. **No asset provenance gate.** Existing paths do not consistently carry source URL, license snapshot, attribution, checksum and publication status.
6. **No fatigue control.** A sound can be technically synchronized yet become repetitive across several videos or signal the wrong vertical tone.
7. **Verification is mostly presence-based.** The workflow checks that early/transition SFX exists, but not whether the final mix masks a critical word, resolves to the intended semantic event, or uses a publication-cleared asset.

## Strategic architecture

### 1. Four production families plus one quarantine family

| Family | Typical roles | Selection question |
|---|---|---|
| `diegetic_foley` | click, door, footsteps, tool, paper, cash handling | What would this action physically sound like? |
| `motion_transition` | whoosh, whip | What direction, speed, weight, material and distance does the motion imply? |
| `state_emphasis` | hit, impact, pop, drop, sub-drop | What exact information/state change deserves emphasis? |
| `tension_context` | riser, drone, ambience | Is this building anticipation or communicating place/context? |
| `meme_voice_reference` | Vine Boom, Anime Wow, spoken meme drops | Does it fit the audience, language, credibility and documented commercial rights? |

`meme_voice_reference` is quarantined by default. It is not part of the finance, health or AI-education baseline palette.

### 2. Event ledger before sound search

Every candidate cue records:

- final timeline timestamp and optional pre-lap;
- visible/implied trigger;
- story job: hook, motion, contradiction, state change, proof, payoff, CTA or context;
- sound family and desired emotion;
- search query in functional English;
- candidate asset ID and gain;
- rights status;
- `keep`, `replace` or `remove` after full-mix audition.

A valid search query describes more than a generic category. Prefer combinations such as:

- `fast light cloth whoosh close`;
- `heavy metal impact short dry`;
- `clean UI pop soft`;
- `low cinematic sub drop short`;
- `small office room tone quiet`;
- `paper contract signature close foley`.

### 3. Rights-aware source ladder

1. original field recording / self-recorded foley;
2. project-generated procedural sound;
3. YouTube Audio Library sound effect with saved metadata;
4. Freesound `CC0`, or `CC-BY` with exact attribution preserved;
5. separately licensed commercial library after explicit spend approval;
6. MyInstants or unknown user-uploaded material as `reference_only`.

A candidate is not publication-ready merely because it is downloadable, popular or short.

### 4. Vertical sonic palettes

| Vertical | Default palette | Avoid by default |
|---|---|---|
| Finance / English | crisp dry UI, paper/metal/click foley, restrained low impacts, evidence chimes | cartoon voices, casino cash-register spam, constant booms |
| Health / English | organic foley, breath/room context, soft clean transitions, restrained warning tones | comedy meme drops on medical claims, alarm fatigue |
| AI education / English | clean digital ticks, data pulses, subtle mechanical motion, low-tech ambience | sci-fi cliché overload, glitch on every cut |

These are brand starting points, not immutable laws. A video may depart when its expectation contract requires a different mood and the production doc records why.

### 5. Layering rule

Layer sounds only when every layer has a different job:

- **anchor:** physical/diegetic event;
- **sweetener:** weight, speed or emphasis;
- **context:** location or emotional state.

Three copies of the same impact do not create three jobs. If a layer does not change perception, remove it.

### 6. Mix and QC rule

Audition in the complete dialogue + music mix, never only in solo. The final artifact must prove:

- the cue lands on the declared event or intentional pre-lap;
- every critical spoken token remains intelligible;
- no unrelated delayed event rebases to t=0;
- repeated motifs remain distinguishable and non-fatiguing;
- the encoded master passes the project's loudness/true-peak and full-decode gates;
- the cue references a manifest asset with publishable rights.

## Backward plan from the target

**Target:** improve stop-scroll and retention without sacrificing credibility, speech clarity or rights safety.

1. At 48h+, inspect distribution state before creative diagnosis.
2. Map 0–3s/0–10s and body retention changes to the exact event ledger.
3. Attribute only to the smallest controlled layer. Hook SFX primarily informs hook response; body/payoff SFX primarily informs local retention and AVD/APV.
4. Keep sound design in both test arms. Compare two high-quality palettes or one cue-family change while freezing story, footage, captions, proof order, runtime and packaging.
5. If the treatment fails: extract the exact cue-level lesson, research a comparable expert pattern, change one strategy variable, and retry on the next eligible lane.

The `<20% swiped away` objective is a direction, not a guaranteed outcome. SFX cannot compensate for a weak frame 0, false promise or slow proof.

## Game-theory and second-order effects

- **Common meme sound arms race:** familiar sounds may create an immediate pattern interrupt; repeated use by every channel makes them predictable; prediction reduces novelty and can cheapen authority.
- **Rights debt:** fast downloading accelerates editing; missing provenance accumulates; later claims or cross-platform reuse can block or devalue the catalog.
- **Semantic inflation:** if every text entrance gets a boom, no moment feels important; editors add louder effects; speech clarity and viewer trust fall.
- **Owned palette moat:** recording/generating a small set takes longer initially; reuse reduces search time; consistent motifs become a recognizable channel asset competitors cannot copy exactly.
- **Metrics overclaim:** retention movement near a cue tempts causal stories; without a matched treatment, the visual/story event is a confounder. Log hypotheses, not verdicts.

## Rollout

### Phase 0 — completed in this change

- adopt ADR-0038;
- add the SFX Event Ledger to the workflow;
- add rights and final-mix gates;
- add a reusable Hermes SFX-design skill;
- create the shared manifest foundation.

### Phase 1 — starter palette

- audit existing generated/project sounds;
- promote only sounds with known origin, checksum, technical metadata and human listening approval;
- collect several variants per core role so weight/mood can be matched rather than forcing one universal sound;
- create one audition reel per vertical in the complete dialogue/music context.

### Phase 2 — renderer integration

- extract shared lookup/mix helpers only after one real new Short proves the manifest and ledger flow;
- stop copy-pasting `generate_sfx()` across renderers;
- keep per-video timing/gain in the event ledger, not inside the asset definition.

### Phase 3 — controlled learning

- tag every published cue by family, role and palette;
- map mature retention to exact cue timestamps;
- let MAB choose between eligible high-quality sound treatments;
- retire sounds that are consistently fatiguing, credibility-breaking or semantically ambiguous.

## Sources and rights references

- Reference video: https://www.youtube.com/watch?v=_ALr4tip3-c
- MyInstants Viet Nam index: https://www.myinstants.com/en/index/vn/
- MyInstants Terms of Use: https://www.myinstants.com/en/terms_of_use.html
- MyInstants DMCA policy: https://www.myinstants.com/en/dcma_copyright_policy.html
- YouTube Audio Library help: https://support.google.com/youtube/answer/3376882?hl=en
- YouTube safe-music guidance: https://support.google.com/youtube/answer/15577610?hl=en
- Freesound license FAQ: https://freesound.org/help/faq#licenses
- Mixkit license: https://mixkit.co/license
- Adobe timed sound-effect workflow: https://helpx.adobe.com/firefly/mobile/work-with-audio-and-video/work-with-audio/generate-sound-effects-using-text-prompts.html
