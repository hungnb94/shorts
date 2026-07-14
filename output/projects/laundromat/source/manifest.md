# Source manifest — laundromat_v1

## Primary source

- Video: `I Quit My Nursing Job For My Laundromat Business – It Brings In $475K/Year`
- Publisher: CNBC Make It
- URL: https://www.youtube.com/watch?v=Z1YZxX-fBwQ
- Source ID: `Z1YZxX-fBwQ`
- Local file: `Z1YZxX-fBwQ.mp4`
- Downloaded format: YouTube `137+140` (1920×1080 AVC + AAC/M4A)
- Source maximum available resolution at acquisition time: 1920×1080; no 2160p format was offered
- Duration: 604.25288 seconds
- Auto-subtitles: `Z1YZxX-fBwQ.en.json3`
- Metadata: `Z1YZxX-fBwQ.info.json`

## Grounded facts

| Fact | Value | Provenance |
|---|---:|---|
| Home sale | $310,000 | spoken/source graphic around 177s |
| Home equity received | $150,000 | spoken/source graphic around 182s |
| Savings invested | $50,000 | source graphic around 198s |
| Seller financing | $100,000 at 6% | spoken/source graphic around 198–202s |
| Purchase price | $300,000 | acquisition financing total and official source description |
| 2024 revenue | $475,000 | spoken around 18.08s and official source description |
| 2024 business profit | $119,000 | CNBC official source description; not presented as a spoken quote |
| 2024 owner pay | $66,000 | spoken around 438.80s and official source description |
| Current owner time | 5–6 hours/week | spoken around 236.08s |
| Time qualification | not true five years earlier; six employees/systems now | spoken around 236.08–254.56s |

Derived only for editorial visualization: `$119K / $475K = 25.05%`, displayed as `CALCULATED: 25% MARGIN`.

## Selected audio windows

| ID | Source range | Evidence |
|---|---:|---|
| `SALE` | 176.80–179.38 | sold home for $310K |
| `EQUITY` | 182.16–190.94 | $150K equity went toward the laundromat down payment |
| `FINANCE` | 198.00–203.86 | remaining $100K seller-financed at 6% over two years |
| `REVENUE` | 18.82–22.48 | $475K in 2024 |
| `OWNER_PAY` | 438.56–443.58 | paid herself $66K in 2024 |
| `HOURS` | 235.76–244.08 | five to six hours now; explicitly not true five years ago |
| `SYSTEMS` | 249.00–253.68 | hired employees and incorporated more systems |

Every source window is under 15 seconds. Each boundary was verified against Whisper Medium word timestamps before final rendering.

## Hook-window decision

- Rejected as frame 0: `177.12–198.47`, because the source displays a static purple house/acquisition infographic with no face.
- Selected 0–1.7s hook visual: moving Pexels footage `7288127`, a woman packing an order in her small business.
- Selected 1.7–2.8s hook visual: moving Pexels footage `13736697`, a woman counting money while working.
- Final hook skin-tone measured `57.17%`, `57.44%`, and `41.49%` at `0.0s`, `0.5s`, and `2.0s`; every consecutive 0.1s sample in the first 2.8s changed (`median motion=3.386`, `minimum=1.650`).
- Selected 2.8–10s action/split-screen visual windows: `6.80–9.50`, `12.00–14.00`, and `14.00–16.50`; none contains a full-screen graphic.
- Rejected `18.08–20.88`: it cuts from Cami to a washer close-up and then reveals the source's large headline, failing the first render's face and clean-caption gates.
- Rejected `438.80–441.50`: the source `$22,023` graphic appears during the clip and collides with the Decision-Lock overlay.
- Selected hook audio: `SALE` from `176.80` followed by `EQUITY` from `182.16`. Moving stock footage avoids both lip-sync mismatch and the static source infographic; no freeze frame remains.
- Post-render face/skin-tone verification remains mandatory.

## Pexels library assets

- `books_finance_7710748.mp4` — receipts/calculator; cash-flow checkpoint
- `contract_signing_7981954.mp4` — hands signing/closing a deal; acquisition checkpoint
- `real_estate_37694695.mp4` — house exterior; sold-home checkpoint
- `business_owner_packing_7288127.mp4` — moving small-business owner; hook 0–1.7s
- `woman_counting_money_13736697.mp4` — moving money-counting action; hook 1.7–2.8s

Rejected for this story: `stock_chart_8480284.mp4` and `suited_businessman_18514374.mp4`, because they are generic corporate/market imagery rather than evidence-linked visuals.
