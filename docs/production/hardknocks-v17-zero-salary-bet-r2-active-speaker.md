# HardKnocks V17 — The $0 Salary Bet (R2 Active-Speaker)

## Status

| Field | Value |
|---|---|
| Production | Complete — full media QC passed, active-speaker reframe validated |
| Render date | 2026-07-27 (R2 revision) |
| Upload status | Not uploaded — same gated reasons as the original |
| Final artifact | `output/projects/hardknocks/final/2026-07-27-hardknocks_v17_zero_salary_bet_r2_active_speaker.mp4` |
| Specs | 1080×1920, H.264 30fps, AAC stereo 48kHz, 53.0s |
| SHA-256 | `9ef1f15838bc153f5844db51f136e9c592a5ea163826cfb22276b87e097ac5c7` |
| Renderer | `pipeline/hardknocks/render_hardknocks_v17_zero_salary.py` |
| QC evidence | `output/projects/hardknocks/clips/v17_zero_salary_work/checks_r2_active_speaker/` |

## R2 changes vs R1

| Issue (R1) | R2 fix |
|---|---|
| Camera only ever stayed on host/right even when Rick was speaking | Per-turn `Segment.turns` array re-bound to active speaker for both camera angles |
| Origin segment opened on a car/reverse angle, host was not the active speaker | Origin `source_start` moved 989.12 → 989.50; turn boundary 2.56 → 2.18s so Rick enters as soon as he actually starts speaking |
| Cadence exceeded 1.5s between reframes | Every segment's largest reframe gap ≤ 1.5s, caption bursts also ≤ 1.5s |
| Full-screen Pexels insert hid Rick for 2s while he was talking | Contract illustrative insert shrunk to a 330×586 bottom-right PiP with a 78% white wash so the active speaker stays visible |
| Forbes proof card covered Rick's hair at 5.7–8.0s | Forbes card moved to top-right at 390×315, doesn't cross the active speaker |
| Per-clip decode re-decoded 17 minutes of 4K source | Hybrid seek: `-ss coarse_start` then `trim=start=offset` inside the filter, setpts to zero. Reduces decode cost while keeping frame accuracy |

## Active-speaker map

| Segment | Angle | Camera → host focus | Camera → Rick focus | Reframe gap (≤1.5s) |
|---|---|---|---|---|
| `hook_zero` | Street (4 turns) | — | f 0.28 ↔ 0.34 every 1.35s | 1.35 |
| `origin` | Street (4 turns) | f 0.75, 0.69 → 0..1.35s | f 0.28, 0.34 → 2.18s+ | 1.18 |
| `hunger` | Street (3 turns) | — | f 0.28 ↔ 0.34 every 1.35s | 1.35 |
| `rejected` | Street (4 turns) | — | f 0.28 ↔ 0.34 every 1.35s | 1.35 |
| `salary` | Street (4 turns) | — | f 0.28 ↔ 0.34 every 1.35s | 1.35 |
| `bought` | Street (3 turns) | — | f 0.28 ↔ 0.34 every 1.35s | 1.35 |
| `companies` | Car (4 turns) | f 0.32, 0.38 → 0..1.45s | f 0.72, 0.66 → 2.92s+ | 1.35 |
| `revenue` | Car (9 turns) | f 0.32, 0.38 → 0..2.80s | f 0.72, 0.66 → 3.68s+ | 0.76–1.32 |
| `find_win` | Street (6 turns) | — | f 0.28 ↔ 0.34 every 1.35s | 1.35 |
| `fulfill_need` | Street (6 turns) | — | f 0.28 ↔ 0.34 every 1.35s | 1.35 |

## Final QC

| Gate | Result |
|---|---|
| Specs (1080×1920, H.264, 30fps, AAC 48kHz, 50–75s) | ✅ all true |
| Full ffmpeg decode | ✅ exit 0 |
| Black-detect (`d=0.12:pix_th=0.20`) | ✅ 0 events |
| Freeze-detect (`n=0.003:d=1.0`) | ✅ 0 events |
| Silence-detect (`noise=-35dB:d=0.50`) | ✅ 0 events |
| Loudness (loudnorm I=-16, TP=-1.5) | -15.9 LUFS, -1.5 dBTP |
| ASR (`$1,100`, `$3 billion`, `22 companies`, `billionaire`, `33`, `commission`, `the firm`, `good business`) | ✅ all phrases recovered |
| Hook gate (0–5s) | Rick is the focal moving speaker from t=0; captions sync to voice; no freeze |
| Cold-viewer clarity | One premise ($0 salary → ownership), one payoff ($3B revenue → billionaire), one mechanism (find their win) |
| Active-speaker sheet (`active_speaker_contact2.jpg`) | All midpoint frames match expected host/Rick focus |

## YouTube metadata (carried from R1)

| Field | Value |
|---|---|
| Title | `He Worked for $0—Then Bought It` (28 chars) |
| Description | Mirrors title; closes with `#business #entrepreneurship #shorts` |
| Studio tags | `zero salary bet`, `business lessons`, `rick jackson` |
| Studio settings | Education, Not for kids, English US, Atlanta GA, No paid promotion, No synthetic disclosure |

## Upload gates (unchanged from R1)

1. **Distribution plateau** — ADR-0035 requires verified lane plateau before the next upload.
2. **Master finance playlist** — channel has no Playlists tab configured.
3. **Upload Details Template** — not yet authored.

Until those gates are satisfied, the artifact remains local. Delivery paths:

- Final MP4: `output/projects/hardknocks/final/2026-07-27-hardknocks_v17_zero_salary_bet_r2_active_speaker.mp4`
- QC evidence directory: `output/projects/hardknocks/clips/v17_zero_salary_work/checks_r2_active_speaker/`
- Renderer: `pipeline/hardknocks/render_hardknocks_v17_zero_salary.py`
- Verifier: `scripts/verify_hardknocks_v17_zero_salary.py`

## Metric falsification rule (48h post-publish)

- **Primary**: Studio `Stayed to watch` ≥ 1,000 `Shown in feed`
- **Target**: `Swiped away` < 20% with sufficient distribution
- **Falsify**: If 0–3s retention still bottoms out despite exposure → the **$0 counteroffer** itself (not active-speaker reframing) is the failing element; revisit hook or hero amount.