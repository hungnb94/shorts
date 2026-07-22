---
title: "OUTWISHED 001 — Higgsfield Shot Plan"
episode: 1
source_script: "001-the-cop-knew-the-code.md"
status: "generation test plan; only SHOT-001 authorized by the current request"
video_model: "Seedance 2.0"
image_model: "Nano Banana 2"
aspect_ratio: "9:16"
---

# OUTWISHED 001 — Higgsfield Shot Plan

## Generation strategy

Use a two-stage workflow for each shot:

1. create a controlled 9:16 keyframe with character references;
2. animate that keyframe with Seedance 2.0 using a motion-only prompt.

This separates composition and identity problems from motion problems. It is more controllable than asking one text-to-video prompt to invent the cast, environment, framing, and animation simultaneously.

Production rules:

- every Seedance clip is an integer `4–15s`;
- output is vertical `9:16`;
- one dominant camera move and one dramatic beat per clip;
- character identity, outfit, palette, and body proportions remain stable;
- prompts contain only visible action, camera, lighting, style, and sound;
- generated dialogue and generated captions are excluded; final English dialogue, captions, and exact SFX timing are post-production layers;
- use the Nico V4 crop as the identity reference whenever Nico is visible;
- do not use the full horizontal lineup as a start frame;
- Veyr is absent until `SHOT-008`.

## Segment map

| Shot | Script time | Higgsfield duration | Story beat | Generation focus | Continuity handoff |
|---|---:|---:|---|---|---|
| `SHOT-001` | `0–4s` | `4s` | Wrong rescuer: officer knows the vault code | Nico foreground profile, officer keypad action, two distinct burglars, body-camera light off | End after officer touches the bodycam |
| `SHOT-002` | `4–9s` | `5s` | Ten minutes earlier: break-in | Fast rewind through mansion, glass sensor, burglars enter, Nico hides | End with Nico behind kitchen island |
| `SHOT-003` | `9–15s` | `6s` | Escape and emergency call | Tray distraction, concealed pantry passage, smartwatch call | End with service passage locked |
| `SHOT-004` | `15–20s` | `5s` | False rescue | Police lights, officer apparently arrests burglars, firm hand on Nico | End on false reassurance |
| `SHOT-005` | `20–24s` | `4s` | Betrayal | Officer cuffs Nico, switches off bodycam, burglar slips loose cuff | Match the vault composition from SHOT-001 |
| `SHOT-006` | `24–31s` | `7s` | Fair-play vault clue | Open vault, safety panel, door wedge, Nico notices warning | End with Nico pushed toward basement |
| `SHOT-007` | `31–36s` | `5s` | Basement low point | Devices confiscated, Nico locked in, methodical room scan | End on small green glint |
| `SHOT-008` | `36–44s` | `8s` | Lamp discovery and Veyr awakening | Signet unlocks wall seal, Lamp reveal, violet smoke resolves into Veyr | End with Nico and Veyr facing each other |
| `SHOT-009` | `44–53s` | `9s` | First wish | Vent confirmation, notebook facts, exact wish, Veyr checks officer | End on `WISH LOCKED` visual state |
| `SHOT-010` | `53–61s` | `8s` | Wish granted with troll styling | Triple teleport, absurd human tower in vault, door closes | End on confused corrupt officer |
| `SHOT-011` | `61–67s` | `6s` | Trap closes | Safety sensor counts three, police alert, tower collapses harmlessly | End on new police unit accepting alert |
| `SHOT-012` | `67–74s` | `7s` | Veyr reveals the troll | Sirens, replay tile, Veyr scores wobble `9.5`, delighted grin | Cut to black on series promise |

Total generated duration: `74s`.

## SHOT-001 — Test specification

### Source reference

`output/projects/outwished/references/nico-v4-crop.png`

The crop contains Nico only. It avoids introducing Veyr, the Lamp, expression labels, or the horizontal character-sheet layout into a shot where those elements must not exist.

### Rejected keyframe prompt V1 — reflection overload

V1 combined four-character counting, a mirrored Nico, keypad action, bodycam detail, and two burglars in one static prompt. The result contained only one burglar and drew Nico as a physical person inside a glass doorway rather than a reflected face. It scored approximately `61/100` and was rejected before video generation.

Failure lesson: reflection is a high-ambiguity spatial instruction. Do not combine it with exact cast counting and several small plot-critical props in the same keyframe.

### Selected keyframe prompt V2 — Nano Banana 2

> Use the referenced male character exactly as Nico Vale, preserving his face, wavy dark hair, tan field jacket with teal rolled cuffs, white shirt, charcoal trousers, and warm palette. Create a vertical 9:16 opening keyframe with exactly four clearly separated adult men. Direct over-the-shoulder composition: Nico fills the left foreground from chest up in tense three-quarter profile, staring at the keypad. On the right, one adult male police officer in an original navy uniform presses a six-digit keypad beside a closed dark-steel vault; his red body-camera LED is clearly visible. In the background, two distinct adult masked burglars stand apart, each holding one empty black duffel bag. Original family-friendly 2D cut-out urban-fantasy thriller, bold dark outlines, flat colors, dramatic red-blue rim light, mobile-readable faces and hands, text-free frame. Only Nico comes from the reference; the genie and Lamp are absent.

V2 created exactly four adults, preserved Nico's identity and palette, separated both burglars, and made the keypad and bodycam readable. It scored `89/100` as a static keyframe and was accepted for animation.

### Selected motion prompt V2 — Seedance 2.0

> Animate this exact start frame for four seconds. Use one slow suspenseful push-in toward the police officer's keypad hand while all four established men remain readable. Nico stays in the left foreground; his eyes shift from the keypad to the officer and his eyebrows tighten with suspicion. The officer presses the final two digits with a stable hand, then deliberately taps the glowing red body camera and its LED switches dark. The two masked burglars in the background subtly lean forward and tighten their grip on separate empty duffel bags. Maintain stable faces, hands, uniforms, clothing, anatomy and character count. Crisp bold 2D cut-out motion, restrained dramatic acting, text-free frame, silent characters. Audio contains distinct metallic keypad beeps, one electronic body-camera power-down chirp, and a low accelerating heartbeat.

### Post-production elements excluded from generation

- Nico V.O.: `The police officer knew my safe code. I had never met him.`
- caption bursts at `0.20s`, `1.20s`, and `2.40s`;
- final loudness normalization;
- transition into the rewind at `4.00s`.

The generated shot is therefore scored as a raw visual-motion test, not as a finished Short.

## SHOT-001 acceptance rubric

| Criterion | Weight | Passing condition |
|---|---:|---|
| Story readability | 20 | Viewer immediately sees officer entering a private code while Nico reacts |
| Nico identity fidelity | 20 | Face, hair, tan/teal jacket, age, and adult male identity remain recognizable |
| Mobile composition | 15 | Nico's reaction and the officer's keypad action remain legible at phone size |
| Cast correctness | 10 | Exactly Nico, one officer, and two adult burglars; no Veyr or Lamp |
| Motion and camera control | 15 | One stable dolly-in; eye shift, key presses, and bodycam action are readable |
| 2D style consistency | 10 | Bold cut-out outlines and flat palette remain stable without photoreal drift |
| Artifact control | 10 | Hands, faces, keypad, bags, and uniform do not visibly morph |

Acceptance threshold: `75/100`, with both Story Readability and Nico Identity Fidelity at least `15/20`.

## SHOT-001 test result

Generated artifact:

`output/projects/outwished/shots/shot-001-v2.mp4`

Technical verification:

- H.264 video, `720×1280`, `24 fps`;
- AAC stereo, `44.1 kHz`;
- measured duration `4.063s`;
- `97` decoded frames;
- full decode passed;
- no black frame or freeze of at least `0.5s` was detected;
- audio mean `-23.3 dB`, max `-5.7 dB`, with no silence interval of at least `0.2s` below `-40 dB`.

Manual media score:

| Criterion | Score | Evidence |
|---|---:|---|
| Story readability | `16/20` | Officer enters the code and touches his bodycam while Nico watches suspiciously; the unproduced VO is still needed to state that Nico never met him |
| Nico identity fidelity | `18/20` | Face, hair, tan jacket, teal cuffs, white shirt, age, and adult male identity remain stable |
| Mobile composition | `13/15` | Nico and officer read immediately; Nico is slightly tight against the left edge |
| Cast correctness | `10/10` | Exactly Nico, one officer, and two masked burglars remain visible throughout |
| Motion and camera control | `11/15` | Stable push-in and readable hand transition; Nico's eye shift is subtle and the burglars barely move |
| 2D style consistency | `10/10` | Bold outlines and flat palette remain stable without photoreal drift |
| Artifact control | `8/10` | No blocking morph; the officer's hand partly hides the bodycam, so the LED-off state is not clearly held on screen |
| **Total** | **`86/100`** | Passes the `75/100` threshold with no blocking artifact |

Virality Predictor was attempted through the documented CLI command. Higgsfield CLI `1.1.19` returned `Model type "text" is not supported by generate create yet` even though the live schema lists `brain_activity`. The web page showed only its unrelated demo result while unauthenticated. No Virality Predictor score is claimed for this clip.

## Prompt standard derived from the test

1. **Crop references to the active character only.** A full lineup leaks absent characters and sheet layout into the shot.
2. **Generate the keyframe before the video.** Reject composition and cast errors before spending video credits.
3. **State the exact cast count and spatial map.** Use `exactly four adults`, then place each one in foreground, right side, and separated background positions.
4. **Avoid reflection in a crowded plot shot.** Reflection can work as its own simple insert, but not while the model must also count four people and render two small devices.
5. **Give the image model static facts only.** Identity, count, position, prop visibility, lighting, style, and aspect ratio belong in the keyframe prompt.
6. **Give Seedance motion only.** Use one camera move, one facial reaction, one primary hand action, and one restrained background action.
7. **Make state changes visible after the hand moves away.** For a light switching off, specify that the actor lowers his hand and the dark indicator remains unobstructed for at least one beat.
8. **Keep generated characters silent.** Add canonical VO, exact dialogue, captions, and calibrated SFX in post-production.
9. **Verify frame-by-frame.** A valid MP4 and a successful generation job do not prove that a small plot-critical LED actually changed state.

### Motion wording V3 — generated

> Animate this exact keyframe for four seconds with one slow suspenseful push-in. Keep all four men readable. Nico's eyes move from the keypad to the officer. The officer presses the final two digits, removes his finger, then taps the side of his bodycam, lowers his hand, and leaves the now-dark LED fully visible for one second. Both burglars make one small anticipatory step while holding separate bags. Preserve every face, hand, outfit, prop and body proportion. Crisp 2D cut-out motion, silent characters, text-free frame. Keypad beeps, one power-down chirp, low heartbeat.

V3 was generated after the user requested a score above `98/100`. The raw Seedance animation scored `99/100`: the bodycam LED visibly changes from red to dark, the officer lowers his hand, Nico's reaction lands in the final beat, both burglars remain present, and the push-in preserves identity and style.

The hook-ready composite adds:

- Inworld `Liam (en)` VO: `That officer knew my safe code. I'd never met him.`;
- Komika Axis caption bursts at `0.20s`, `0.82s`, and `2.40s`;
- one enlarged yellow keyword per burst;
- a short yellow keypad pointer during the first beat;
- normalized VO mixed over a ducked Seedance SFX bed.

Final artifact:

`output/projects/outwished/shots/shot-001-v3-hook.mp4`

Hook-ready score: `99/100`. The single point deduction is for captions partially covering the burglars' lower bodies/bags in some frames; no face, keypad, bodycam, or Nico reaction is obscured. Generation is paused at V3 per the user's instruction; no further shot variant is authorized.
