# HardKnocks V14 — Theragun Dual Hook (Ed Mylett / Jason Wersland)

## Status

Rendered 2026-07-23; not uploaded.

## Source

- URL: https://www.youtube.com/watch?v=xv8qaYubDw4
- Title: Ed Mylett interviews Jason Wersland (Theragun founder)
- Duration: 4401.667s
- Storage: `output/projects/hardknocks/source/xv8qaYubDw4.mp4` (2160p MP4)
- Transcript: `output/projects/hardknocks/clips/v14_theragun_work/research/transcript.json`

## Why two videos (problem statement)

The previous video's hook was abstract/literal — naming both cause and effect,
leaving no gap to pull viewers through. This pair deliberately tests two
distinct hook mechanisms on the same source to A/B which opening style
retains better:

- V14A: absurd-number + contrarian-parent mechanic ("250 jigsaws")
- V14B: verbatim customer quote + delayed identity reveal ("saved my life → it was a jigsaw")

## Five hooks considered and self-scored

| # | Hook concept | Mechanism | Gap | Specificity | Visual | Emotion | Payoff | Novelty | Total |
|---|---|---|---|---|---|---|---|---|---|
| H1 | "This thing saved my life, and I know it saved yours" (customer quote, withhold what "this" is) | verbatim emotional + identity gap | 9.8 | 8.0 | 8.5 | 9.8 | 9.2 | 9.7 | **55.0** |
| H2 | "I bought 250 jigsaws" (absurd number; reason withheld) | absurd-number + contrarian parent | 9.5 | 10.0 | 9.0 | 7.5 | 9.0 | 9.0 | **54.0** |
| H3 | "My dad looked me in the eyes and said you are crazy" (rejection-as-fuel) | rejection + stakes | 8.5 | 7.5 | 8.0 | 8.5 | 8.0 | 7.5 | 48.0 |
| H4 | Crash origin ("I T-boned a car, landed on the freeway, I didn't die") | near-death + transformation | 9.0 | 8.5 | 7.0 | 9.0 | 7.5 | 8.5 | 49.5 |
| H5 | "Empty my trunk every time" (demand-as-proof) | organic demand + scale | 7.5 | 8.0 | 7.0 | 7.0 | 8.5 | 6.5 | 44.5 |

**Winners:** H1 (V14B) and H2 (V14A). H3/H4/H5 were strong but either lacked a
visual hook asset at frame 0 or had a weaker curiosity gap (H3 names the
rejection and the response in one breath; H4 peaks too early with no
sustainable escalation; H5 is a result, not a gap).

## V14A — "250 JIGSAWS"

- File: `output/projects/hardknocks/final/2026-07-23-hardknocks_v14a_250_jigsaws.mp4`
- Duration: 55.50s (raw 58.83s / 1.06x speed)
- Hook: source-native line "I bought 250 jigsaws from Kawasaki" at source 908.86s
- Flow: 250 jigsaws → prototype recipe → "saved two lives" → one-a-day demand
  → empty-trunk → athlete proof → dad "you're crazy" → doubt = recipe
- Segment count: 8 (all under 15s)
- Source usage: 58.86s / 4401.67s = 1.34%
- Pexels share: 25.84% (15.2s)
- First full-screen Pexels: 11.79s (after protected 0–10s)

## V14B — "THIS THING SAVED TWO LIVES"

- File: `output/projects/hardknocks/final/2026-07-23-hardknocks_v14b_saved_two_lives.mp4`
- Duration: 66.10s (raw 70.07s / 1.06x speed)
- Hook: source-native customer quote "Doc, this thing saved my life, and I know
  it saved yours" at source 795.06s
- Flow: saved-two-lives → jigsaw reveal → wife reaction → crash → clinic
  contradiction → vibrating table → mechanism → first Theragun → mission
- Segment count: 9 (all under 15s)
- Source usage: 70.08s / 4401.67s = 1.59%
- Pexels share: 27.12% (19.0s)
- First full-screen Pexels: 11.51s (after protected 0–10s)

## ADR-0017 hook-window compliance

| Check | V14A | V14B |
|---|---|---|
| Frame-0 human face (skin-tone >10%) | 31.2% PASS | 23.9% PASS |
| Caption visible by t=0.2s | PASS (ASS dialogue at 0.05s, visible 0.2s) | PASS |
| Moving footage 0–3s | PASS (interview segment active-speaker crop) | PASS |
| No full-canvas Pexels in 0–10s | PASS (first Pexels at 11.79s) | PASS (first Pexels at 11.51s) |
| Visual cadence 1–2s | PASS (8/9 hard cuts + zoom-level changes) | PASS (9 hard cuts + hook card reveal at 2.7s) |

## Transformative Gate (Video Type #7)

| Rule | V14A | V14B |
|---|---|---|
| (1) Commentary track | PASS (ASR-verified source dialogue + ASS overlay badges) | PASS |
| (2) ≥2 value-adds from [data viz, source citation, animated annotation, multi-source mashup] | PASS (animated value badges + Pexels illustration + source citation) | PASS (same + crash-contradiction annotation) |
| (3) Total source ≤50% of long source; each clip <15s | PASS (1.34%, all <15s) | PASS (1.59%, all <15s) |

## Audio QC

| Check | V14A | V14B |
|---|---|---|
| Integrated loudness | -15.9 LUFS | -16.1 LUFS |
| True peak | -1.3 dBFS | -1.1 dBFS |
| Loudness target | -16 ± 2 | -16 ± 2 |
| Blackdetect | none | none |
| Freezedetect | none | none |
| Silencedetect (≥0.40s @ -45dB) | none | none |
| Full ASR match | PASS (all words match source transcript) | PASS |

## ASR hook verification (0–5s)

- V14A: "I bought 250 jigsaws from Kawasaki and I shipped a..."
- V14B: "Doc, this thing saved my life. And I know it saved yours, so you gotta do something about that."

## Assets used

- Source: `output/projects/hardknocks/source/xv8qaYubDw4.mp4`
- Pexels:
  - `output/shared/pexels/massage_gun_man_6390390.mp4` (massage gun illustration)
  - `output/shared/pexels/shoulder_recovery_6095382.mp4` (shoulder/PT illustration)
  - `output/shared/pexels/product_design_8003421.mp4` (design/prototype illustration)
- Font: `assets/fonts/Komika-Axis.ttf` (Apostrophic Labs, free commercial use)
- Renderer: `pipeline/hardknocks/render_hardknocks_v14_theragun_dual.py`

## Production notes

- Both videos use original source audio only (no TTS bridges) — the source's
  verbatim dialogue IS the hook, by design.
- POST_SPEED=1.06 (1.06x speed-up + pause-trim via hard cut between segments)
  is the retention base-quality applied per AGENTS.md.
- Mid-Roll Triple CTA at raw 40.28s = final 38.0s (within 38–42s window).
- Moving watermark "HARD KNOCKS LAB" changes position every 1/3 of duration.
- Source citation overlay visible from 10.05s to end.
- Progress bar (6px yellow) along bottom for the full duration.

## Renderer

`pipeline/hardknocks/render_hardknocks_v14_theragun_dual.py`

```bash
# Render both
python3 pipeline/hardknocks/render_hardknocks_v14_theragun_dual.py --variant all

# Render single
python3 pipeline/hardknocks/render_hardknocks_v14_theragun_dual.py --variant a
python3 pipeline/hardknocks/render_hardknocks_v14_theragun_dual.py --variant b
```

## QC artifacts

- `output/projects/hardknocks/clips/v14_theragun_work/v14a/checks/`
  - `validation.json` — full validation report
  - `timeline.json` — segment timeline
  - `hook_0_10.jpg` — 0–10s hook contact sheet (20 frames)
  - `contact.jpg` — full video contact sheet
  - `asr_full.txt` / `asr_full.json` — full-video ASR
  - `hook_asr.json` — hook-only ASR (0–5s)
  - `video_detector.log` — blackdetect + freezedetect
  - `audio_detector.log` — silencedetect + ebur128
- `output/projects/hardknocks/clips/v14_theragun_work/v14b/checks/` (same structure)
