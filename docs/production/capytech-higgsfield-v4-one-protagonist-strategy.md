# Capytech Higgsfield v4 — One-Protagonist Strategy

Date: 2026-07-28
Status: creative and 1–3s edit design locked; paid generation requires explicit hard-cap approval

## Strategic correction

V3 incorrectly mapped a different cast member to each era. That weakens comparison causality because a viewer can attribute the outcome to the person rather than the year. V4 uses one protagonist, one phone and one objective across every era.

## Protagonist contract

- ID: Volt.
- Species/style: original capybara tech mascot; premium stylized 3D animated-film rendering.
- Silhouette: broad, rounded and heavy with a low center of gravity.
- Face: broad muzzle, relaxed eyes, thick low eyebrows and deadpan reactions.
- Wardrobe invariant: charcoal utility top with coral trim, mint pouch, **full-length coral trousers covering waist through ankles**, cream sneakers.
- Prohibited: bare lower body, shorts that expose the upper legs, missing trousers, skirt-like garment, changing trouser color, duplicated limbs, copyrighted cues.
- Prop continuity: one unbranded phone and one charging cable.

## Story engine — challenge, stakes, escalation, payoff

The same Volt receives the same phone at 1% in 2000, 2026 and 2050. The edit uses high-stakes challenge storytelling—clear objective, visible progress, escalating obstacles, frequent information changes and a large consequence—without copying MrBeast's likeness, wording, music or proprietary assets. Each era changes only the technology, friction and hidden cost.

1. Hook: `1% BATTERY` → `3 DIFFERENT YEARS` → `ONE DRAINS HIM TO ZERO`; Volt lunges as the cable escapes.
2. 2000: one oversized charger, one plug, immediate success; scoreboard gives 2000 the lead.
3. 2026: wrong connector → adapter chain → cable still short → forced update; every failure is a separate visual beat.
4. 2050: an AI orb offers effortless charging; Volt accepts; the scan reveals that Volt is the energy source.
5. Diegetic CTA: the orb locks the phone at 99% and requires Like, Subscribe and Comment `CHARGE` to release it.
6. Payoff: the phone reaches 100%; Volt drains to 0% and collapses safely onto a padded charging mat.
7. Loop: a system update drains the phone back to 1%; the cable and framing return to the hook geometry.

## Hook selection

Five candidates were evaluated with the six-part Hook Design rubric. The selected hook is the only one that combines a concrete number, three-way challenge, withheld losing year and a guaranteed visual payoff:

`I GAVE HIM 1% BATTERY IN THREE DIFFERENT YEARS. ONE CHARGER DRAINED HIM TO ZERO.`

It is delivered as three mobile-readable caption bursts rather than one paragraph. Frame 0 shows Volt's face, the nearly-empty phone and active cable motion. The losing year remains hidden until the 2050 reveal.

## Reuse boundary

All v2/v3 clips containing Zip, Byte, or multiple characters are retained as superseded experiment artifacts. They must not enter the v4 final MP4. Do not delete or overwrite them.

## Duration and 1–3 second cadence

Target 50.5 seconds: the shortest repository-compliant runtime with a half-second safety margin. The final EDL contains 29 cuts; every cut is 1.0–2.3 seconds. The hook changes at 1.1–1.6 second intervals. Eight 5-second generated shots provide 40 seconds of unique motion; local phone close-ups, connector macros, scoreboards, meter animations and the intentional hook-loop reprise provide the remaining 10.5 seconds. No shot is prolonged with a static hold, non-uniform stretch or decorative effect that adds no information.

The cut-level source of truth is `output/projects/capytech/scripts/capytech_higgsfield_v4_storyboard.json`. Every cut must change at least one of: action, camera scale, year, obstacle, score, battery state, energy state or story question.

## Paid-generation topology and hard cap

1. Stage A: generate one master/hook frame of Volt in full-length coral trousers, then one 5-second Kling 3.0 Turbo hook clip. Cost: 8.5 credits. Stop and gate face, cast count, trousers, phone, motion and generated text before continuing.
2. Stage B: use the accepted master as the only character reference for seven additional start frames and seven additional 5-second Kling clips: 2000; 2026 wrong cable; 2026 adapter chain; 2026 update; 2050 offer/scan; 2050 drain; payoff.
3. Live unit costs checked on 2026-07-27: Nano Banana 2 Lite image = 1 credit; Kling 3.0 Turbo 5-second clip = 7.5 credits.
4. Full no-retry hard cap: 68.0 credits. Balance forecast: 256.35 → 247.85 after Stage A → 188.35 after the full batch.
5. No generation job may be submitted until the user explicitly approves the 68.0-credit hard cap. No automatic retry; any rejected image or clip requires a new cost preview and approval.

## Audio

Original procedural chiptune → glitch-hop → dreamy supersaw music plus event-bound SFX. No commercial song is baked into the master. A licensed trend may replace the music through YouTube Shorts Audio Library at upload.

## Blocking gates

- Exactly one character in every shot; no v2/v3 three-character footage may enter the final.
- Full-length trousers visible and stable whenever the lower body is in frame.
- Same face, body proportions, wardrobe and phone across adjacent shots.
- 1080×1920, 30 fps, 50.5s, H.264/yuv420p + AAC 48 kHz stereo.
- Caption by 0.2s; early SFX by 1.0s; diegetic CTA starts at 38.0s.
- Every final cut lasts 1.0–3.0 seconds; the cut EDL covers 0.0–50.5 seconds contiguously.
- No generated text, logo, black frame, freeze, stretch or overlay collision.
- Loudness -16 ±1 LUFS and encoded true peak ≤ -1 dBTP.
- External naive-viewer Hook Gate remains unverified until a real viewer supplies evidence.
