# OUTWISHED SHOT-001 V3 — Hook-Ready QC Report

Date: 2026-07-22
Status: accepted; generation paused at V3 by user request

## Final artifact

`output/projects/outwished/shots/shot-001-v3-hook.mp4`

Remote raw Seedance result:

`https://d8j0ntlcm91z4.cloudfront.net/user_3FzmGFKSBfCqnFaKuvLiXP6lf2F/hf_20260722_014126_cbedb162-4b5c-4a68-977e-b6c4e38793a3.mp4`

The remote URL is the raw animation. The local hook-ready artifact also contains canonical VO, calibrated captions, a keypad pointer, and the final audio mix.

## Score

Hook-ready manual media score: `99/100`.

| Criterion | Score | Evidence |
|---|---:|---|
| Visual story | `20/20` | Final keypad press, red-to-dark bodycam state, officer hand lowering, and Nico's recognition are all visible |
| Nico identity | `15/15` | Face, hair, tan jacket, teal cuffs, age, and silhouette remain stable through the push-in |
| Mobile composition and captions | `14/15` | Text is readable at 360×640 and avoids faces/keypad/bodycam; it partially covers the burglars' lower bodies/bags |
| Motion and hook cadence | `15/15` | Immediate motion plus three micro-beats: keypad, bodycam, Nico reaction; visual change every 1–2 seconds |
| Cast and artifact control | `10/10` | Exactly Nico, one officer, and two burglars; no blocking hand/face/prop drift |
| VO-caption narrative clarity | `15/15` | Nine-word VO preserves the mystery gap; three 2–4-word caption bursts follow the speech structure |
| Sound and technical readiness | `10/10` | Early SFX bed, VO normalization before mix, valid H.264/AAC artifact, full decode, no black/freeze |
| **Total** | **`99/100`** | Above the requested `>98` target |

This is an internal craft score, not a guarantee of real audience retention. Actual retention requires publication and YouTube Studio data.

## Hook layers

- VO: `That officer knew my safe code. I'd never met him.`
- voice: Inworld `Liam (en)`
- VO duration: `3.580s`
- caption 1: `0.20–0.82s` — `THAT OFFICER`, `OFFICER` emphasized
- caption 2: `0.82–2.35s` — `KNEW MY SAFE CODE`, `SAFE` emphasized
- caption 3: `2.40–3.72s` — `I'D NEVER MET HIM`, `NEVER` emphasized
- caption font: Komika Axis
- font sizes: `80px` base / `90px` emphasized
- stroke: `8px`
- caption center: `60%` frame height
- horizontal safe margin: `8%`
- pointer: yellow arrow toward the keypad during the first beat

## Technical QC

- duration: `4.083333s`
- video: H.264, `1080×1920`, `24 fps`
- video frames: `98`
- audio: AAC stereo, `48 kHz`
- full decode: pass
- black detection: no match
- freeze detection (`>=0.5s`): no match
- integrated loudness: `-15.91 LUFS`
- true peak: `-2.86 dBTP`
- one `0.232s` low-level interval occurs during the deliberate sentence/bodycam pause
- SHA-256: `503523d9bb1759310b0d09bf91318fa1d0d703c8f20fbf9c167967f61edf4e2d`

## Review artifacts

- `output/projects/outwished/analysis/shot-001-v3-hook-contact-sheet.png`
- `output/projects/outwished/analysis/shot-001-v3-hook-mobile.png`
- `output/projects/outwished/analysis/shot-001-v3-hook-frames/cap1.png`
- `output/projects/outwished/analysis/shot-001-v3-hook-frames/cap2.png`
- `output/projects/outwished/analysis/shot-001-v3-hook-frames/cap3.png`

## Reproduction

Renderer:

`pipeline/outwished/render_shot_001_v3.py`

Inputs:

- `output/projects/outwished/shots/shot-001-v3-raw.mp4`
- `output/projects/outwished/shots/shot-001-v3-vo-liam.wav`
- `output/projects/outwished/shots/shot-001-keyframe-v3.png`
- `output/projects/outwished/shots/shot-001-keyframe-v3.prompt.txt`
- `output/projects/outwished/shots/shot-001-motion-v3.prompt.txt`

## Credits

- V3 iteration: `40` credits
- cumulative V1–V3 test: `62` credits
- remaining balance: `933` credits

No additional keyframe or video variant was generated after the user's pause instruction.
