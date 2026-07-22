# OUTWISHED 001 — Speech-Bubble Text Trial Design

Date: 2026-07-22
Status: Approved for local trial render

## Goal

Make the current 57.725-second trimmed visual/SFX cut understandable without voice-over by burning concise English dialogue into comic speech bubbles.

## Visual treatment

- Show only one active bubble at a time.
- Use 2–5-word bursts when possible; never exceed two lines per bubble.
- Position bubbles near the speaker while avoiding faces, the Lamp, the vault keypad, and important action.
- Nico: warm cream fill, teal outline. Use a cloud-tail thought bubble for narration.
- Corrupt officer: white fill, red outline.
- Veyr: deep plum fill, cyan outline with white text.
- System state: dark compact panel with cyan outline, not a character bubble.
- Render English text with the checked-in Komika Axis font profile.

## Story text map

| Timeline | Speaker | Meaning |
|---|---|---|
| 0.20–3.80 | Nico thought | The officer knows Nico's private code despite being a stranger. |
| 4.20–8.20 | Nico thought | Ten minutes earlier, two burglars entered the house. |
| 8.55–12.25 | Nico | Home invasion; two suspects; send police. |
| 13.80–17.10 | Officer / Nico | The officer claims Nico is safe; Nico notes the unusually fast response. |
| 18.80–22.30 | Nico / Corrupt Cop | Exact reveal: `YOU'RE WITH THE BURGLARS?` / `I'M THEIR THIRD PARTNER.` Every later bubble uses the `CORRUPT COP` label. |
| 22.80–28.30 | Corrupt Cop | Closing the occupied vault sends a police alert. |
| 28.60–32.10 | Corrupt Cop / Nico thought | Nico is locked downstairs; dry reaction. |
| 33.55–41.30 | Veyr / Nico | Veyr identifies the heir and confirms that he grants wording literally. |
| 41.55–50.30 | Nico / Veyr | Exact three-thief vault wish; officer explicitly included. |
| 50.55–57.60 | Veyr / Corrupt Cop / System | Wish granted, criminals stacked, and `OTHER OFFICERS ALERTED` distinguishes incoming police from the accomplice. |

## Rendering

- Preserve the current video and audio unchanged except for the burned visual layer.
- Generate full-canvas transparent PNG overlays for each timed bubble.
- Composite overlays locally with ffmpeg; no Higgsfield generation or paid API call.
- Produce a separate `dialogue-text-trial` MP4, manifest, and contact sheet.

## Verification

- Probe for 1080x1920, H.264 High Level 4.2, true 24 fps CFR, and AAC stereo 48 kHz.
- Full-decode the final artifact.
- Run black, freeze, and silence detectors.
- Extract frames at every bubble event and manually check text legibility, speaker association, face avoidance, and action visibility.
- Keep the artifact labelled as a text-dialogue trial, not upload-final; SHOT-011/012, final VO, CTA, watermark, and publishing metadata remain outside this trial.
