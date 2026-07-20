# FoodTrial v2 — Date Bark vs. SNICKERS

Status: Design locked; render pending  
Date: 2026-07-19  
Format: Vietnamese Living-Comic Food Trial  
Target runtime: 50–75 seconds (target ≈60 seconds)

## Case

**Charge:** the creator's broad “healthier Snickers” framing hides a decisive portion/yield dependency.

**Claim ceiling:** the declared ten-serving recipe is estimated to be higher in calories and total sugar than one official 1.86 oz SNICKERS bar while providing substantially more fiber. The verdict may call the framing overbroad; it may not call the recipe universally unhealthy.

**Verdict shape:** guilty of an under-specified claim, not guilty of being a “bad food.” No lobby acquittal. The practical sentence is to pre-cut the batch into 16 pieces and pair one with 200 g nonfat plain Greek yogurt.

## Backward plan

1. The viewer leaves knowing that ingredient quality and portion size answer different questions.
2. The decisive reveal is yield: ten pieces ≈384 kcal each; sixteen pieces ≈240 kcal each.
3. The counter-evidence ladder must flip judgment at least three times before the verdict.
4. Every numeric statement is labeled as an estimate or an official package value.
5. The final action is specific enough to execute without guessing.

## Source packet

### Recipe Case

- Video: `https://www.youtube.com/watch?v=x_Ri-BQ-0xY`
- Creator: Lifestyle of a Foodie
- Source dimensions: 1440×2560, AV1, 14.161 s
- Recipe page: `https://lifestyleofafoodie.com/date-bark/`
- Source wording: healthier Snickers-inspired no-bake dessert/snack
- Declared recipe yield: 10 servings
- Recipe: 24 Medjool dates, 1/2 cup natural peanut butter, 1/4 cup roasted peanuts, 8 oz dark chocolate, flaky salt

Approved source windows total 6.5 s (45.9% of source duration):

- 0.1–2.3 s: date/peanut base
- 5.3–7.3 s: chocolate layer
- 11.6–13.9 s: finished bark piece

Each excerpt is under 15 s. The final edit adds original commentary, a USDA comparison, official-product comparison, yield visualization, counter-argument and companion-meal action.

### Nutrition evidence

- USDA FDC 168191: Medjool dates
- USDA FDC 174294: smooth peanut butter
- USDA FDC 174262: dry-roasted peanuts
- USDA FDC 170272: 60–69% dark chocolate proxy
- USDA FDC 330137: nonfat plain Greek yogurt
- Official comparison: `https://www.snickers.com/products/chocolate/snickers-singles-size-chocolate-candy-bars-186-oz-bars`
- Canonical calculation: `output/projects/foodtrial/scripts/date_bark_v2_nutrition.json`

Rounded values used on screen:

| Comparison | Calories | Protein | Fiber | Total sugar |
|---|---:|---:|---:|---:|
| Date bark, creator yield 10 | ≈384 kcal | ≈5.9 g | ≈6.7 g | ≈47.7 g |
| Official SNICKERS 1.86 oz | 250 kcal | 5 g | 1 g | 27 g |
| Date bark, revised yield 16 | ≈240 kcal | ≈3.7 g | ≈4.2 g | ≈29.8 g |
| 1/16 bark + 200 g nonfat Greek yogurt | ≈362 kcal | ≈24.3 g | ≈4.2 g | not summed; USDA yogurt input lacks total sugar |

Uncertainty is blocking copy: date size, peanut-butter packing/brand and chocolate label vary. “Estimate” remains visible on numerical evidence cards.

## Counter-evidence ladder

| Beat | Initial judgment | Valid counter-evidence | New judgment |
|---|---|---|---|
| Calories | Date bark sounds lighter | ≈384 kcal vs 250 kcal | Claim looks guilty |
| Fiber | Calories alone are incomplete | ≈6.7 g vs 1 g fiber | Defense regains ground |
| Total sugar | “Natural” can still be concentrated | ≈47.7 g vs 27 g total sugar | Prosecution regains ground |
| Sugar context | Total and added sugar are different metrics | Dates supply much of the total; SNICKERS declares 25 g added sugar | Neither side owns the whole story |
| Yield | Same batch, different piece count | 10 pieces ≈384; 16 pieces ≈240 | Portion is the decisive assumption |
| Verdict | “Healthy” cannot be universalized | Better fiber does not mean lower energy | Claim guilty only for missing conditions |

## HEIT script

Canonical structured script: `output/projects/foodtrial/scripts/date_bark_v2_script.json`

- **Hook:** “healthier Snickers” hides a portion secret; courtroom opens immediately.
- **Explain:** the exact Recipe Case and declared yield enter evidence.
- **Illustrate:** calories → fiber → total sugar → sugar-source context → yield.
- **Teach:** verdict is scoped to the claim; the sentence is a 16-piece cut plus a protein-rich companion.

## Visual plan

- Living-Comic court header and panel frame persist throughout.
- Frame 0: moving human face tasting chocolate (Pexels 8202077), not a title card.
- Burned caption visible by t=0.2 s.
- Hook visual changes every 1–2 s through card, evidence badge and zoom/panel motion.
- Recipe footage appears only in the approved proof windows.
- Numerical cards are animated comparisons, not fake Nutrition Facts labels.
- Pexels 18831517 is explicitly labeled as companion-meal illustration.
- Caption font: bundled Bangers; 2–5 words per burst; one yellow keyword; center around 60% frame height.
- Early gavel SFX lands within t=0–1 s.
- Mid-roll custom Triple CTA begins at 38–42 s and includes Like, Subscribe and one comment prompt.
- Watermark moves among safe corners during the timeline.

## Asset gate

Canonical record: `output/projects/foodtrial/clips/date_bark_v2_work/asset_gate/asset_decisions.json`

Approved:

- Source `x_Ri-BQ-0xY`: direct proof
- Pexels 8202077: relevant hook illustration
- Pexels 18831517: relevant companion illustration

Rejected:

- Pexels 29532477: generic restaurant dessert
- Pexels 8803788: savory wrap, not yogurt
- Pexels 36353674: generic candy shop, not product proof

## Transformative Gate

- Commentary track: required and fully original.
- Value-adds: USDA comparison, official label comparison, yield visualization, metric counter-argument, actionable companion meal.
- Source reuse: 6.5/14.161 s = 45.9%; each excerpt <15 s.
- No attribution card is added to the final video per current project policy; provenance remains in this production record.

## Upload package target

Canonical title: `Date Bark Ra Tòa 🍫⚖️`  
Description line 1 mirrors the title exactly.  
Visible hashtags: `#shorts #ToaAnMonAn #DateBark`  
Studio tags: `date bark`, `dinh dưỡng`, `tòa án món ăn`

Final metadata and QC results will be appended after the actual rendered artifact passes media verification.
