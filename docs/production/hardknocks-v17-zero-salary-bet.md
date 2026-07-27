# HardKnocks V17 — The $0 Salary Bet

## Status

| Field | Value |
|---|---|
| Production | Complete — all media QC passed, manual Hook Gate pass |
| Render date | 2026-07-27 |
| Upload status | Not uploaded — awaiting separate user authorization and lane/source-rights gates |
| Final video | `output/projects/hardknocks/final/2026-07-27-hardknocks_v17_zero_salary_bet.mp4` |
| Renderer | `pipeline/hardknocks/render_hardknocks_v17_zero_salary.py` |
| Source | School of Hard Knocks, `VW2t21zzYl8` — "Asking Wealthy Americans How They Got Rich! (Atlanta)" |
| Narrator | None — 100% authentic source voice (Rick Jackson) |
| Runtime | 53.400 s |
| SHA-256 | `5c51676ef5d7a59285665c6f5db1089488487bdab01e5b563bd9645a0463cb9b` |
| QC summary | `output/projects/hardknocks/clips/v17_zero_salary_work/checks/validation.json` |
| Design spec | `docs/specs/2026-07-27-hardknocks-v17-zero-salary-bet-design.md` |
| Implementation plan | `docs/plans/2026-07-27-hardknocks-v17-zero-salary-bet.md` |

## Hook Change Versus Prior Videos

Previous V13 used a **Direct Search Question** narrated by TTS over walking host footage:

> "How many millionaires do you have to meet before you find a real billionaire?"

V17 uses a **Source-Native Challenge Hook**: the very first audible idea is the subject's own counteroffer — no TTS, no narrator, no title card, no delay.

> "What if I work for no money a month—and just 33% straight commission?"

This is the highest-scoring candidate from the 12-hook rubric (52/60) and the authentic source-native line scores 52/60 as H1. The visual packaging line **H10** (`$0 salary. 33% commission. One impossible bet.`) scored 53/60 and is rendered as caption bursts over the same footage.

## Narrative

### Act 1 — The Bet and the Origin (0–21s)

1. **Cold open** on Rick saying his counteroffer (hook).
2. Rewind to childhood: projects, no father, mother a waitress, foster care, scraping by for food.
3. At 20: rejected because he had no degree.
4. Asks what a degree-holder earns: `$1,100 a month + commission`.

### Act 2 — Literal Payoff and Escalation (21–38s)

5. Rick: `One year later, I bought the firm.`
6. Escalation: `I own 22 companies.`
7. Company-scale claim: `$3 billion a year.`
8. Interviewer asks if he is a billionaire; Rick answers `Yeah.`
9. Compact Forbes proof badge appears inline while Rick continues speaking.

### Act 3 — Mechanism and Closure (38–53s)

10. Rick explains the win-win mechanism: find the other person's win, don't sell your agenda, fulfill their need.
11. Final overlay closes the hook: `THEIR WIN = ZERO RISK` → `HIS WIN = OWNERSHIP`.
12. Final spoken line: `That's the definition of a good business.`

## Source Windows and Transformative Gate

Primary source: `output/projects/hardknocks/source/VW2t21zzYl8.mp4` (3840×2160 AV1, 29.97 fps, Opus stereo, 1316.241 s).

| Segment | Raw source window | Duration | Act |
|---|---|---:|---|
| `hook_zero` | 1027.36–1032.23 | 4.87 s | hook |
| `origin` | 989.12–994.07 | 4.95 s | context |
| `hunger` | 1010.16–1013.51 | 3.35 s | context |
| `rejected` | 1017.92–1022.31 | 4.39 s | setup |
| `salary` | 1022.32–1027.35 | 5.03 s | stake |
| `bought` | 1032.24–1035.27 | 3.03 s | payoff |
| `companies` | 970.60–975.70 | 5.10 s | escalation |
| `revenue` | 976.16–985.35 | 9.19 s | proof |
| `find_win` | 1047.52–1055.00 | 7.48 s | lesson |
| `fulfill_need` | 1055.00–1063.11 | 8.11 s | lesson |

- Every continuous source clip is strictly **under 15 s** (max 9.19 s).
- Total selected source: **55.5 s** (4.22 % of the 1316.241 s source) — well below the 50 % ceiling.
- Transformative layers satisfied:
  1. Editorial commentary: hook packaging, progress state, salary-risk comparison, explicit closing mechanism.
  2. Animated annotation/data viz: `$0`, `$1,100`, `33%`, `22`, `$3B` keyword-emphasis bursts.
  3. Independent source citation: compact Forbes badge.
  4. Multi-source mashup: original interview + one licensed Pexels illustration + independent proof page.
  5. 100 % authentic source dialogue — **no TTS used**.

## Visual and Sound Package

- 1080×1920, H.264, yuv420p, 30 fps, MP4.
- Active-Speaker Reframing throughout; Rick is the frame-0 focal subject.
- Source burned-in caption band cropped and uniformly refilled — **no black footer**, no aspect stretch.
- Hook captions visible at t=0, change every 1.0–1.4 s:
  - `WORK FOR $0?`
  - `NO SALARY`
  - `JUST 33% COMMISSION`
  - `WOULD YOU GIVE ME A CHANCE?`
- Body captions: 2–5 words, Komika Axis, one yellow-emphasized keyword, normal center near 60 % frame height.
- Real moving source footage throughout 0–10 s; **no freeze, face-in-PiP, or generic stock** in the opening.
- One short Pexels contract-signing insert (`output/shared/pexels/contract_signing_7981954.mp4`) labeled `ILLUSTRATION • PEXELS 7981954` during the salary comparison (≈1.5–2.0 s), source audio continuous.
- Compact Forbes badge (520×420) appears inline during the last 2–3 s of the `revenue` beat; Rick stays visible and moving.
- Early impact SFX at ≈0.08 s; ownership ting at `bought`, proof ting at `$3B`, closure ting at final mechanism.
- Subtle ambient bed at 0.14 volume; no music bed dominates.
- **No Like/Subscribe/Comment CTA** — deliberately removed after V13/V11 evidence that mid-roll CTA disrupted momentum before payoff.
- Small moving `HARD KNOCKS LAB` watermark cycles top-left → top-right → bottom-left.

## Final QC

### Technical (automated)

| Check | Result |
|---|---|
| 1080×1920 | PASS |
| H.264 / yuv420p / 30 fps | PASS |
| AAC stereo 48 kHz | PASS |
| Runtime 50–75 s | PASS (53.400 s) |
| Full ffmpeg decode | PASS (exit 0) |
| Black segments ≥0.12 s | 0 |
| Freeze segments ≥1.0 s | 0 |
| Silence ≥0.5 s at −35 dB | 0 |
| All source clips <15 s | PASS (max 9.19 s) |
| Total source <50 % | PASS (4.22 %) |
| SHA-256 | `5c51676ef5d7a59285665c6f5db1089488487bdab01e5b563bd9645a0463cb9b` |

### Hook (automated + manual)

- Frame-0 face/motion: **PASS** — Rick's face visible and moving at t=0.
- Frame-0 skin-tone proxy: 18.7 % (above 10 % gate).
- `$0` readable before 0.5 s.
- Spoken hook intelligible in one listen: `what if I work for no money a month and just 33% straight commission?`
- No caption covers mouth/eyes in hook window.
- No stock, freeze, face PiP, or generic title card in 0–10 s.

### ASR semantic verification (mlx_whisper large-v3)

Core phrases present in order:

```
✓ no money a month
✓ 33% commission
✓ bought the firm
✓ 22 companies
✓ three billion
✓ help other people get what they want
✓ fulfilled that need
✓ definition of a good business
```

All must-have phrases detected; sequence matches editorial intent.

### Manual media review (full 1fps contact sheet + 0–5s mobile sheet)

- No full-screen static card at any point.
- No black footer or aspect-distortion artifacts.
- Pexels illustration is brief, labeled, and does not replace source audio.
- Forbes badge is compact and inline; never full-screen.
- Ending frame is moving source footage with final overlay; no dead hold.
- Visual cadence meets ADR-0036: ≤1.5 s visual change in 0–5 s, no unexplained gap >3 s in 5–10 s, no unexplained gap >6 s in body.

## Canonical Upload Package

### YouTube Title

```
He Worked for $0—Then Bought It
```

Validation: 28 characters, Title Case, one emoji, below 30-character cap.

### Description

```
He offered to work for $0 salary and 33% commission after being rejected for not having a degree. One year later, he owned the company. Today he runs 22 healthcare companies doing $3 billion in annual revenue.

The lesson: find the other person's win. Remove their risk. Then earn the ownership.

What would you risk to own your outcome?

#business #entrepreneurship #shorts
```

Visible hashtags: exactly 3 (`#business #entrepreneurship #shorts`).

### YouTube Studio Tags

1. `zero salary bet`
2. `business lessons`
3. `rick jackson`

Studio tags: exactly 3.

### Studio Settings (canonical)

| Setting | Canonical value |
|---|---|
| Visibility | Unlisted first; public only after final Studio preview and ADR-0035 lane gate |
| Audience | Not made for kids |
| Video language | English (United States) |
| Title/description language | English (United States) |
| Category | Education |
| Recording location | Atlanta, Georgia, United States |
| Paid promotion | No |
| Altered/synthetic content disclosure | No — no synthetic audio depicts a real person saying/doing something they did not |
| Raw affiliate link | None |
| Playlist | **BLOCKED** — no approved finance master playlist exists in repo; public MONEY BLINDSPOT channel has no playlists tab |
| Related Video | **BLOCKED** until current measured winner and actual destination lane are resolved |
| Upload Details Template | **BLOCKED** — no approved template name/ID exists in repo |

## Upload Gate

**Do not upload yet.**

1. Previous MONEY BLINDSPOT Short (V13) was public on 2026-07-19; Distribution Plateau has not been verified for the next strict-round-robin lane.
2. Destination lane must be resolved from ADR-0035 state before touching Studio; do not default to the previous channel.
3. Exact approved finance master playlist is absent; a public channel check returned `This channel does not have a playlists tab`.
4. Approved Upload Details Template name/ID is absent from repository configuration/docs.
5. Related Video wiring cannot be selected until the measured current winner and actual destination channel are known.

The media artifact and canonical title/description/tags are complete. Stage 6 remains intentionally blocked rather than inventing Studio state.

## Post-Production Retro

### Hook Retro

- The cold-open source-native counteroffer worked as designed: the spoken promise is the visual hook simultaneously.
- Caption bursts `WORK FOR $0?` / `NO SALARY` / `JUST 33% COMMISSION` land every ~1.1 s over the same moving face, satisfying ADR-0036 cadence.
- No TTS, no narrator, no competing audio — only Rick's voice. This matches the proven Mode A verbatim pattern that outperformed hybrids in earlier experiments.

### Keep

- Source-native challenge hook with caption packaging.
- Inline salary-risk comparison (`THEM: $1,100 + COMMISSION` / `HIM: $0 + 33%`) over continuous footage.
- Compact inline Forbes badge that never freezes or covers the speaker.
- Event-bound SFX instead of a music bed.
- No mid-roll CTA; the mechanism lesson lands uninterrupted.
- Explicit loop closure: `THEIR WIN = ZERO RISK` → `HIS WIN = OWNERSHIP` over the final source-native line.

### Fix Next Time

- Do not assume the source MP4 persists; re-download at render time if missing (V17 started with a deleted 4K file).
- Hook captions at y=1280 correctly avoided the mouth, but the first two bursts (`WORK FOR $0?`, `NO SALARY`) slightly overlap the upper chest — acceptable but could shift up 40–60 px for absolute safety.
- The `salary` segment window includes a natural pause after `$1,100 a month`; the 1.04x retention speed-up trimmed it cleanly, but verify ASR on the isolated word `commission` if a tighter word-boundary trim is ever needed.

### Drop

- Any TTS narration for this sub-format.
- Mid-roll Triple CTA.
- Full-screen proof/strategy/guardrail/CTA panels.
- Generic stock openings.
- Final static card or question.

## Success Metrics (after public release + 48 h)

- **Primary:** Studio `Stayed to watch` after ≥1,000 `Shown in feed`.
- **Goal:** `Swiped away` < 20 % when sufficient distribution exists.
- **Secondary:** AVD in absolute seconds and retention at 0–3 s (hook), 20–25 s (ownership payoff), 30–38 s (escalation/proof), 38–53 s (mechanism/closure).
- **Falsification rule:** If first-3 s retention remains weak despite adequate feed exposure, the `$0 salary` challenge itself — not execution density — must be questioned.

---

**Handoff:** Final artifact, SHA-256, runtime, QC report, contact sheets, ASR JSON, and metadata package are ready. Publication remains blocked until the user separately authorizes upload and the destination lane/source-rights gates are satisfied.