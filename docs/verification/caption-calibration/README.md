# Caption Calibration

This directory pins the ffmpeg/Pillow caption profile adopted by ADR-0034.

## Purpose

CapCut `size 16 / stroke 60` values are editor-relative units, not ffmpeg pixels. Copying them literally into `drawtext` would produce an unusable result. `caption-profile.json` records the 1080x1920 output-normalized proxy selected for this repository:

- English: Komika Axis, 80px base / 90px emphasized keyword;
- Vietnamese: Bangers, 96px base / 108px emphasized keyword;
- stroke: 8px;
- caption center: 60% of frame height, allowed 55–65% when avoiding a face/proof object;
- horizontal safe margin: 8% per side;
- mobile verification preview: 360x640.

Bangers uses a larger optical size because equal numeric sizes made the Vietnamese sample substantially less prominent than Komika Axis. The renderer auto-fits long bursts downward while preserving the safe width.

This is a verified **visual-intent calibration**, not a claim of pixel-identical CapCut output. Exact pixel matching would require a reference frame exported from CapCut with the same font, text and canvas; no such export was supplied.

## Font artifacts

- `assets/fonts/komika-axis/KOMIKAX_.ttf`
  - SHA-256: `a6d750a82402c22e79ac360943b714726a63e1e5550b459ffbbee6906a7cb597`
  - license: `assets/fonts/komika-axis/LICENSE.txt`
  - source: Font Squirrel's Komika Axis package / Apostrophic Labs freeware license.
- `assets/fonts/bangers/Bangers-Regular.ttf`
  - SHA-256: `4160a7311de9342674cce9160cde9fcbb30f48190397d86ff1b70b455af65824`
  - license: `assets/fonts/bangers/OFL.txt`
  - source: Google Fonts repository, SIL Open Font License 1.1.
  - `fc-query` reports Vietnamese (`vi`) coverage.

Do not modify/repackage Komika Axis; its included license permits using the font as-is but forbids modified font redistribution without authorization.

## Render

From the repository root:

```bash
python3 docs/verification/caption-calibration/render_caption_calibration.py
```

Outputs:

- `caption-calibration.mp4`: 8s H.264/AAC, 1080x1920, 30fps; English sample from t=0–4s and Vietnamese sample from t=4–8s.
- `caption-calibration-contact-sheet.png`: side-by-side English/Vietnamese review.
- `caption-calibration-mobile.png`: exact 360x640 Vietnamese preview.

The MP4 is a typography/placement calibration artifact, not a production Short template. It does not replace the per-video checks for word timing, keyword animation, face/proof occlusion, early SFX, CTA or moving watermark.

## Verification performed

- Renderer exited 0.
- `ffprobe`: H.264 video, AAC audio, 1080x1920, 30fps, 8.000s.
- Manual contact-sheet review: both languages readable, uncropped and visually comparable; captions centered around 60% height; final keyword yellow; black outline clear.
- Manual native 360x640 review: Vietnamese diacritics intact, no crop, yellow keyword and outline remain legible.
