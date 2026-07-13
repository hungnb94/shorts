# hardknocks_lawnmower_v1 — "From a Lawnmower to a Real Estate Empire"

## Status
| Field | Value |
|-------|-------|
| YouTube Video ID | `dHDpDXSIAkA` |
| Uploaded | 2026-07-10 |
| Metrics fetch after (48h rule) | 2026-07-12 or later |
| Metrics status | Fetched 2026-07-13 |

## Video Specs
- Duration: 51.4s
- Resolution: 1080x1920 (9:16 portrait)
- Codec: H.264 (libx264, crf 18), 30fps
- Audio: AAC, 192kbps, 48kHz, stereo
- File: `output/projects/hardknocks/final/2026-07-10-hardknocks_lawnmower_v1.mp4` (43.1MB)
- Render script: `pipeline/hardknocks/render_hardknocks_v1.py`

## YouTube Title
He Mowed Lawns At 12... Now He Owns 2,600 Apartments

## YouTube Description
```
A kid pushing a lawnmower for $5 a yard had no idea he'd end up negotiating a $10,000,000 sale decades later.

This is the real math behind going from zero to a real estate empire — the number most people get wrong (net worth vs. cash flow), the deal that changed everything, and the one lesson he says matters more than the money.

Stick around for the part about what he actually did with it.

What's the first "real" money move you ever made? Drop it below.

#realestate #entrepreneur #richmindset #wealth #sidehustle #shorts
```

## Source
- Channel: School of Hard Knocks ("Asking 90 Year Old Billionaires If Getting Rich Was Worth It")
- Source video ID: `KxoKCNCLOss` (23-min original)
- Footage used: abs t=573.0-688.3s (115.3s), i.e. 51.4s of edited output from an 1391s+ source — well under the ADR-0007 50% ceiling
- Attribution intentionally dropped (ADR-0007 decision)

## Hook Formula Applied (docs/research/hook-benchmarks-2026-07/REPORT.md)
- **Cold open, no title card** — t=0 is a real handshake + smiling faces (ADR-0017 Hook-Window Rule)
- **Gap→reveal arc** — hook text "FROM A LAWNMOWER... TO A REAL ESTATE EMPIRE" opens a mystery, resolved progressively across the video (Context→Intrigue hybrid pattern)
- **Hook Caption Sync (ADR-0018)** — kept source's own word-synced, keyword-highlighted burned-in captions as-is; they already matched the researched pattern, so no need to recreate

## Clips Used (6 clips, 51.32s edited)
| # | ID | Source (abs) | Local dur | Edited timeline | Transcript |
|---|-----|-----|-----|-----|-----|
| 1 | c1_hook | 574.4-581.9 | 7.5s | 0-7.5s | "...you got rich? I did. I started. My dad was a drunk, beat my mom. She was 39 when she died in front of me. I was 16." |
| 2 | c2_rise | 582.0-591.7 | 9.7s | 7.5-17.2s | "Raised four sisters and a brother and started with a lawnmower. Became the largest mowing company... individually mowing military bases all over the country. Just sold the company 5 years ago." |
| 3 | c3_apartments | 591.84-596.46 | 4.62s | 17.2-21.82s | "Now I got 2600 apartments stocks and from Omaha, Nebraska, [Berk]shire Hathaway." |
| 4 | c4_sale | 601.0-605.3 | 4.3s | 21.82-26.12s | "...how much did you sell? It was 10 million. $10 million, sir. Congratulations." |
| 5 | c5_wisdom | 660.5-674.48 | 13.98s | 26.12-40.1s | "The biggest thing is net worth means nothing and cash flow means... that's what I learned from the recession of 2008 to 2012... until you have a lot of net worth and no cash flow. Cash flow is everything." |
| 6 | c6_legacy | 677.1-688.32 | 11.22s | 40.1-51.32s | "...never seen a hearse pull a U-Haul yet... Help others while you're here. Make an impact. I've given away over 10 million to charity... How old are you today? 68 years old." |

## Value-Adds (Transformative Gate, ADR-0007 — min 2 required)
1. **data_viz_overlay** — stat cards: "2,600 APARTMENTS" (c3), "$10,000,000 SALE" (c4), "$10M+ DONATED TO CHARITY" + "68 YEARS OLD" (c6)
2. **fact_check_callout** — "FACT CHECK: Berkshire Hathaway = Warren Buffett's company" (c3), clarifying the interviewee's slurred "Shire Hathaway" reference

Commentary track: hook-framing text (c1), "LESSON" tag (c5), CTA "CASH FLOW > NET WORTH — REMEMBER THIS" (c6).

## Known Fix Applied During Production
First render placed data-viz/CTA overlays at bottom (`y=h-320`, `y=h-140`) and they visually collided with the source's own burned-in captions, which occasionally render emphasized numbers extra-large at the very bottom of frame (e.g. a giant "68" or "16"). Fixed by moving all added overlay text to the top zone (`y=90` primary, `y=190`/`200` secondary), reserving the bottom exclusively for the source's native captions. Verified clean via frame extraction at all overlay timestamps post-fix.

## What To Check At 48h (for post-hoc analysis)
- **AVD / Stayed %** vs. the two benchmark data points already in `docs/experiments/EXPERIMENT-LOG.md` (Dangote 51.6% GOOD, bacsihai 8.6% BAD)
- **Retention graph shape** — does it hold flat through c3/c4 (the two stat-card value-adds), or dip? If it dips exactly at a stat-card overlay, that's evidence the top-zone overlay is a distraction, not a hook.
- **Where viewers drop at c5** — the wisdom clip is the longest single clip (13.98s) and has no visual cut, only the LESSON tag — check against the 2-Second Rule (ADR-0016) and Hook Caption Sync cadence (ADR-0018) if retention dips there.
- **Comment themes** — per the hook-benchmarks comment psychology research, watch for "circular logic mockery" (viewers doubting the "8 sisters and a lawnmower" origin story) vs. admiration — this is an interview format like School of Hard Knocks in the original research, which skewed admiration, not mockery.

## Retention Analysis
_Auto-generated by the fetch-metrics skill, 2026-07-13. Full per-second curve:
`output/projects/hardknocks/final/dHDpDXSIAkA-retention.csv`._

- **Views**: 987 · **AVD**: 0:31 (59.8% of 51.4s) · **CTR**: not available via API (confirmed, see ADR-0025)
- **Key moments** (z-score vs this video's own smoothed baseline):
  - peak at ~0.5s (4.0%, z=4.29)
  - peak at ~4.6s (4.2%, z=4.07)
  - dip at ~6.2s (-4.3%, z=-3.84)
