# HardKnocks V17 Zero Salary Bet Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce and verify a 50–55 second 1080×1920 Short that opens on Rick Jackson's authentic `$0 salary / 33% commission` counteroffer, resolves with ownership and $3B company-scale proof, and ends on his business mechanism without an interruptive CTA.

**Architecture:** Fork the working V13 one-off ffmpeg/Python renderer because it already implements active-speaker reframing, caption-band removal without aspect distortion, timed overlays, source clip ceilings, and real artifact validation. Replace its story model, audio overlay model, captions, Pexels window, proof treatment, and final composite with the V17 design. Verify the actual MP4; do not add or expand renderer unit tests per repository policy.

**Tech Stack:** Python 3, ffmpeg/ffprobe, Pillow, ASS subtitles, mlx_whisper for final semantic verification.

---

## File Map

**Create**

- `pipeline/hardknocks/render_hardknocks_v17_zero_salary.py` — one-off renderer and inline spec validation.
- `scripts/verify_hardknocks_v17_zero_salary.py` — media QC runner that emits ffprobe/decode/black/freeze/silence/loudness evidence and contact sheets.
- `docs/production/hardknocks-v17-zero-salary-bet.md` — source, editorial decisions, timeline, QC, rights state, metadata, and upload gate.
- `output/projects/hardknocks/final/2026-07-27-hardknocks_v17_zero_salary_bet.mp4` — final artifact.
- `output/projects/hardknocks/clips/v17_zero_salary_work/` — segments, proof panel, ASS, audio, timeline, and checks.

**Reference only**

- `pipeline/hardknocks/render_hardknocks_v13_billionaire_hunt.py`
- `output/projects/hardknocks/source/VW2t21zzYl8.mp4`
- `output/projects/hardknocks/source/VW2t21zzYl8.transcript-timed.txt`
- `output/projects/hardknocks/clips/v13_billionaire_hunt_work/proof_sources/forbes_rick_jackson.png`
- `output/shared/pexels/contract_signing_7981954.mp4`

### Task 1: Create the V17 renderer shell

- [ ] **Step 1: Copy the proven V13 renderer**

Run:

```bash
cp pipeline/hardknocks/render_hardknocks_v13_billionaire_hunt.py \
  pipeline/hardknocks/render_hardknocks_v17_zero_salary.py
```

Expected: the V17 renderer exists and is still byte-equivalent before edits.

- [ ] **Step 2: Replace project constants and required inputs**

Set:

```python
WORK = PROJECT / "clips" / "v17_zero_salary_work"
FINAL = PROJECT / "final" / "2026-07-27-hardknocks_v17_zero_salary_bet.mp4"
POST_SPEED = 1.04
FORBES_SCREENSHOT = PROJECT / "clips" / "v13_billionaire_hunt_work" / "proof_sources" / "forbes_rick_jackson.png"
```

Remove all TTS input constants and require only the source, Pexels contract clip, Forbes screenshot, fonts, and event SFX.

- [ ] **Step 3: Confirm source windows are legal**

Use these exact windows:

```python
Segment("hook_zero", 1027.36, 1032.23, ((0.0, 0.68),), 1.08, "hook")
Segment("origin", 989.12, 994.07, ((0.0, 0.40), (1.25, 0.68)), 1.04, "context")
Segment("hunger", 1010.16, 1013.51, ((0.0, 0.68),), 1.06, "context")
Segment("rejected", 1017.92, 1022.31, ((0.0, 0.68),), 1.06, "setup")
Segment("salary", 1022.32, 1027.35, ((0.0, 0.68),), 1.06, "stake")
Segment("bought", 1032.24, 1035.27, ((0.0, 0.68),), 1.08, "payoff")
Segment("companies", 970.60, 975.70, ((0.0, 0.40), (1.55, 0.68)), 1.05, "escalation")
Segment("revenue", 976.16, 985.35, ((0.0, 0.40), (3.68, 0.68), (5.84, 0.40), (6.80, 0.68), (7.35, 0.40), (8.45, 0.68)), 1.05, "proof")
Segment("find_win", 1047.52, 1055.00, ((0.0, 0.68),), 1.06, "lesson")
Segment("fulfill_need", 1055.00, 1063.11, ((0.0, 0.68),), 1.06, "lesson")
```

Run:

```bash
python3 -m py_compile pipeline/hardknocks/render_hardknocks_v17_zero_salary.py
```

Expected: exit 0.

### Task 2: Implement visual storytelling

- [ ] **Step 1: Replace captions with V17 source-synced bursts**

Hook captions begin at source-relative `0.00` and progress through:

```text
WORK FOR $0?
NO SALARY
JUST 33% COMMISSION
WOULD YOU GIVE ME A CHANCE?
```

Body captions must express only the current information state: origin, no degree, `$1,100`, ownership, `22 companies`, `$3B`, and the other person's win.

- [ ] **Step 2: Add the salary-risk comparison overlay**

During the salary/bought section, add compact inline labels over moving footage:

```text
THEM: $1,100 + COMMISSION
HIM: $0 + 33%
```

The labels disappear before `I bought the firm`; no full-screen card is allowed.

- [ ] **Step 3: Build a compact Forbes proof badge**

Generate a phone-readable panel no larger than 520×420 with:

```text
FORBES PROFILE
$1B NET WORTH
22 BUSINESSES
```

Place it inline during the last 2–3 seconds of the revenue beat while Rick remains visible and moving.

- [ ] **Step 4: Add only one licensed stock illustration**

Use `output/shared/pexels/contract_signing_7981954.mp4` for approximately 1.5–2.0 seconds during the salary comparison, after 16 seconds. Keep source audio continuous and label it `ILLUSTRATION • PEXELS 7981954`.

- [ ] **Step 5: Close the loop over moving footage**

During the final two source-native sentences, overlay:

```text
THEIR WIN = ZERO RISK
HIS WIN = OWNERSHIP
```

The final frame remains Rick speaking; do not add an outro card, question, or CTA.

### Task 3: Implement audio and render

- [ ] **Step 1: Remove TTS and CTA audio paths**

The final audio mix must contain source dialogue, subtle generated ambient bed, and event-bound SFX only.

- [ ] **Step 2: Position event SFX**

Use real leading-silence tracks for:

- t≈0.08s: hook impact/ting;
- `bought` start: ownership ting;
- `revenue` `$3B` reveal: proof ting;
- final mechanism: subtle closure ting.

- [ ] **Step 3: Render the real artifact**

Run:

```bash
python3 pipeline/hardknocks/render_hardknocks_v17_zero_salary.py
```

Expected:

- final MP4 exists;
- duration is 50–75 seconds;
- 1080×1920 H.264 yuv420p 30fps;
- AAC stereo 48kHz;
- each selected source clip is under 15 seconds;
- total source use is under 50%.

### Task 4: Create and run media QC

- [ ] **Step 1: Create the verifier**

`scripts/verify_hardknocks_v17_zero_salary.py` must run:

- ffprobe JSON;
- full ffmpeg decode;
- blackdetect;
- freezedetect;
- silencedetect;
- loudnorm measurement;
- hook frames at 0.0/0.2/0.6/1.0/1.5/2.0/2.5/3.0/4.0/5.0s;
- a 1fps full contact sheet;
- a 0–10s mobile contact sheet;
- SHA-256.

- [ ] **Step 2: Run the verifier**

Run:

```bash
python3 scripts/verify_hardknocks_v17_zero_salary.py
```

Expected: `output/projects/hardknocks/clips/v17_zero_salary_work/checks/validation.json` reports every blocking technical check as true.

- [ ] **Step 3: Run final ASR**

Extract mono 16kHz audio and run mlx_whisper large-v3. Verify the final transcript contains, in order:

```text
no money a month
33% straight commission
bought the firm
22 companies
3 billion
find out what was the win
fulfilled that need
definition of a good business
```

### Task 5: Manual media review and corrections

- [ ] **Step 1: Inspect the 0–5s mobile hook sheet**

Reject and rerender if frame 0 does not show moving Rick footage, `$0` is not readable immediately, captions cover the mouth/eyes, or the hook requires context beyond one listen.

- [ ] **Step 2: Inspect the 1fps contact sheet**

Reject and rerender if any full-screen card, static payoff, black footer, aspect stretch, irrelevant stock, visual discontinuity, or text collision is present.

- [ ] **Step 3: Inspect exact payoff frames**

Check the ownership reveal, `$3B` reveal, Forbes badge, and final `THEIR WIN / HIS WIN` closure at full resolution.

- [ ] **Step 4: Re-run all QC after every correction**

No earlier validation result may be reused after an artifact change.

### Task 6: Production record and handoff

- [ ] **Step 1: Write the production record**

Record exact timeline, source windows, transformative layers, runtime/specs, SHA-256, ASR result, automated QC, manual Hook Gate, limitations, and upload block state in `docs/production/hardknocks-v17-zero-salary-bet.md`.

- [ ] **Step 2: Add canonical upload metadata**

Use:

```text
Title: He Worked for $0—Then Bought It

Visible hashtags: #business #entrepreneurship #shorts

Studio tags:
zero salary bet
business lessons
rick jackson
```

Description must accurately distinguish `$3B annual company revenue` from personal net worth.

- [ ] **Step 3: Verify repository state**

Run:

```bash
git status --short
git diff --check
```

Expected: only intentional renderer/spec/plan/production changes are tracked; generated media remains in ignored output paths; `git diff --check` exits 0.

- [ ] **Step 4: Handoff without upload**

Deliver the final MP4 path, SHA-256, exact runtime, QC result, contact-sheet evidence paths, and metadata package. Do not upload until the user separately authorizes publication and the destination lane/source-rights gates are satisfied.
