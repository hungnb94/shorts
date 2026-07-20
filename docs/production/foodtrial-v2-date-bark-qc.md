# FoodTrial v2 — Date Bark — QC Report

Date: 2026-07-19
Final artifact: `output/projects/foodtrial/final/2026-07-19-foodtrial_v2_date_bark.mp4`
Renderer: `pipeline/foodtrial/render_foodtrial_date_bark_v2.py`
Spec: `output/projects/foodtrial/scripts/date_bark_v2_script.json` (sha256 d5cfa82b…)

## 1. Media spec gate

| Check | Required | Observed | Pass |
|---|---|---|---|
| Container | MP4 | mov,mp4,m4a (isom/mp41) | PASS |
| Video codec | H.264 | h264 High, yuv420p | PASS |
| Resolution | 1080x1920 (9:16) | 1080x1920 | PASS |
| Frame rate | 30 fps | 30/1 | PASS |
| Pixel format | yuv420p | yuv420p, bt709, progressive | PASS |
| Audio codec | AAC | aac LC, 48 kHz, stereo | PASS |
| Duration | 50-75 s | 62.567 s | PASS |
| Audio duration | matches video | 62.566 s | PASS |
| GOP / faststart | ≥1s, +faststart | g=60, +faststart | PASS |

ffprobe: 1080x1920, 30 fps, 1872 video frames, 2934 audio frames, 2 streams.

## 2. Decode integrity

- Full decode to null: PASS (no errors).
- blackdetect (d≥0.20s, pix_th=0.02): no black frames reported.
- freezedetect (n=0.003, d≥1.5): no freeze frames reported.
- silencedetect (-45 dB, d≥0.60 s): no unwanted long silences; inter-beat gaps are the expected ~0.6-0.7 s narration pauses, well below the 0.8 s "dead air" ceiling.

## 3. Loudness

- Two-pass loudnorm measurement on final mix:
  - input_i = -15.34 LUFS, input_tp = -1.40 dBTP, LRA = 1.60
  - target = -14 LUFS, output_i = -14.09 LUFS (offset +0.09)
- Per-clip normalization target -16 LUFS TP-1.5 was applied before mix; final mix sits within ±1 dB of -14 LUFS YouTube target.

## 4. Timeline gates

- Total runtime: 62.567 s — within 50-75 s gate.
- CTA beat starts at t=41.433 s — within the 38-42 s Mid-Roll Triple CTA gate.
- Hook beat duration: 4.167 s — promise/gap delivered within 0-3 s by narration + on-screen card.
- Verdict beat at t=45.933-51.800 s.
- Source reuse: 6.5 s total across 3 windows of x_Ri-BQ-0xY (0.1-2.3, 5.3-7.3, 11.6-13.9), each <15 s; source duration 14.161 s, reuse 45.9% — under the 50% Transformative Gate ceiling.

## 5. Caption verification

- Caption font: Bangers (Vietnamese) per ADR-0034.
- Caption position (band detection on extracted frames, threshold 200, step 4): every sampled beat (t=0.2/2.0/10.5/23.0/41.6/46.2/56.0 s) shows a bright text band at y≈1112-1190 (frame-mid ≈60%), matching the canonical Caption Style Profile (center Y 55-65%).
- ASCII crop of v_000.2.png and v_041.6.png confirms letterforms present and not clipped; keyword highlighting via inline ASS colour override active.
- Stroke 8 px, keyword color #FFD54A (yellow), base white #FFFFFF per profile.

## 6. Card / chrome / watermark

- Yellow border + "TÒA ÁN MÓN ĂN | HỒ SƠ 002" top chrome visible on every sampled frame (ASCII crop y=180-260 confirms chrome text band at 9-13% frame height).
- Info card content band detected at y≈280-750 across all sampled beats.
- Moving watermark detected at y≈1800-1816 (~94% height) on t=56.0 s sample, consistent with the moving-watermark overlay expression (`x`/`y` oscillating on 8 s / 16 s cycles per the renderer).

## 7. Final ASR (sanity check)

mlx_whisper (vi, whisper-small-mlx) transcription of the final mix reads back all 10 beats in correct order:
hook → recipe_docket → calorie_charge (384 kcal vs 250) → fiber_defense (~7 g vs 1 g) → sugar_charge (~48 g vs 27 g) → sugar_context → yield_reveal (384 vs 240) → triple_cta ("10 hay 16") → verdict ("Có tội… điều kiện… không phải vì món ăn xấu") → companion_meal ("200g sữa chua hy lạp… 362 kcal, 24g protein").

No fabricated trial results, taste reactions, or subject reactions are present in the narration or on-screen text.

## 8. Claim ceiling (ADR-0033)

- Prosecution evidence: 10-serving recipe = 384 kcal, 47.7 g sugar per serving (USDA FDC-sourced ingredient math; see `date_bark_v2_nutrition.json`).
- Counter-evidence: same tray cut into 16 = 240 kcal per serving; fiber 4.2 g; plus 200 g nonfat Greek yogurt companion = 362 kcal, 24 g protein combined.
- Verdict text on screen and in VO: "Có tội có điều kiện — không phải vì món ăn xấu, mà vì khẩu phần." No universal health claim is made.
- Source Note printed under every card cites USDA FDC IDs and SNICKERS official page, satisfying the "limited to this recipe + assumptions" ceiling.

## 9. Overall verdict

PASSES all gates in ADR-0034 Content Craft Gate and the project's Media Verification policy. Ready for upload package assembly.
