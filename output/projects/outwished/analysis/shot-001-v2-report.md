# OUTWISHED SHOT-001 — Higgsfield Test Report

Date: 2026-07-22

## Result

SHOT-001 was generated as a real 4-second vertical video using a two-stage Higgsfield workflow:

1. Nano Banana 2 keyframe;
2. Seedance 2.0 image-to-video animation.

The accepted video passed technical QC and scored `86/100` in manual media review.

## Remote results

- rejected keyframe V1: `https://d8j0ntlcm91z4.cloudfront.net/user_3FzmGFKSBfCqnFaKuvLiXP6lf2F/hf_20260722_010511_f4723ea4-3de9-47b0-9cd9-6f6de1ad5c09.png`
- accepted keyframe V2: `https://d8j0ntlcm91z4.cloudfront.net/user_3FzmGFKSBfCqnFaKuvLiXP6lf2F/hf_20260722_011257_dce7fcda-d76f-4f79-b91b-064b2a47bca2.png`
- accepted SHOT-001 video: `https://d8j0ntlcm91z4.cloudfront.net/user_3FzmGFKSBfCqnFaKuvLiXP6lf2F/hf_20260722_011433_5dc0f4e6-5aef-4459-9f28-b085a9f6dcf8.mp4`

## Local artifacts

- `output/projects/outwished/references/nico-v4-crop.png`
- `output/projects/outwished/shots/shot-001-keyframe-v1.png`
- `output/projects/outwished/shots/shot-001-keyframe-v2.png`
- `output/projects/outwished/shots/shot-001-v2.mp4`
- `output/projects/outwished/analysis/shot-001-v2-contact-sheet.png`
- `output/projects/outwished/shots/shot-001-keyframe-v1.prompt.txt`
- `output/projects/outwished/shots/shot-001-keyframe-v2.prompt.txt`
- `output/projects/outwished/shots/shot-001-motion-v2.prompt.txt`

## Generation settings

### Keyframe V2

- model: Nano Banana 2 (`nano_banana_flash`)
- aspect ratio: `9:16`
- resolution: `2k`
- input reference: cropped Nico V4 character asset

### Video V2

- model: Seedance 2.0 (`seedance_2_0`)
- start image: accepted keyframe V2
- requested duration: `4s`
- aspect ratio: `9:16`
- resolution: `720p`
- bitrate mode: `high`
- genre: `drama`
- generated audio: enabled

## Technical QC

- measured duration: `4.063s`
- video: H.264, `720×1280`, `24 fps`
- audio: AAC stereo, `44.1 kHz`
- decoded frame count: `97`
- full decode: pass
- black-frame detection: pass
- freeze detection (`>=0.5s`): pass
- audio mean: `-23.3 dB`
- audio maximum: `-5.7 dB`
- silence detection (`<-40 dB`, `>=0.2s`): no match

## Manual score

| Criterion | Score |
|---|---:|
| Story readability | `16/20` |
| Nico identity fidelity | `18/20` |
| Mobile composition | `13/15` |
| Cast correctness | `10/10` |
| Motion and camera control | `11/15` |
| 2D style consistency | `10/10` |
| Artifact control | `8/10` |
| **Total** | **`86/100`** |

Pass threshold: `75/100`.

## What worked

- exact four-character cast remained stable;
- Nico's face, hair, tan jacket, teal cuffs, white shirt, and adult male identity were preserved;
- the officer, keypad, two separate burglars, and separate bags stayed readable on mobile;
- one slow push-in produced controlled motion without character drift;
- no Veyr, Lamp, extra person, photoreal drift, black frame, or freeze appeared.

## What did not work

- V1's reflected-face composition failed: the model produced only one burglar and treated Nico as a physical person in a glass doorway;
- V2's bodycam action is partly occluded by the officer's hand, so the LED-off state is not held clearly;
- Nico's eye reaction is subtler than requested;
- the two burglars move very little;
- the raw clip lacks canonical VO and captions by design, so it is not a finished hook.

## Virality Predictor status

The documented command was attempted:

`higgsfield generate create brain_activity --video output/projects/outwished/shots/shot-001-v2.mp4 --wait`

Higgsfield CLI `1.1.19` returned:

`Model type "text" is not supported by generate create yet.`

The live model schema lists `brain_activity`, but the current CLI rejects its returned `text` type. The web page was unauthenticated and displayed only its own demo result. That demo score was not used. No fabricated Virality Predictor score is included here.

## Credits

- starting balance: `995`
- remaining balance: `973`
- total used for two keyframes and one video: `22`

## Production recommendation

Use the V2 keyframe structure and the refined V3 motion wording in `docs/concepts/outwished/episodes/001-higgsfield-shot-plan.md`. The crucial addition is: after the officer touches the bodycam, he lowers his hand and the now-dark LED remains visible for one full beat.
