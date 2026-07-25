# Ronald Wayne MrBeast-Editing Short Implementation Plan

> **For implementation:** execute tasks sequentially; do not mark the production artifact completed until the Hook Gate's independent naive-viewer item is supplied.

**Goal:** Produce a verified 1080x1920, 50–75 second English MONEY BLINDSPOT Short about Ronald Wayne, driven by TTS and a meaningful visual/source/reframe change no later than every 1.5 seconds.

**Architecture:** A dedicated one-off Python/ffmpeg renderer builds a 60-second frame-exact timeline from 40 visual beats of 1.5 seconds. The visual layer combines direct Ronald Wayne/Steve Wozniak footage, licensed Wikimedia assets and custom animated proof cards. A continuous synthetic narration spine uses the approved Edge TTS production fallback because the canonical Qwen narrator environment is absent. Two short direct-source voice moments remain in the audio as evidence. ASS captions, citations, moving watermark, CTA, music-state changes and event-bound SFX are composited into the final render. No renderer unit tests are added; the real MP4 is the verification target.

**Tech stack:** Python 3.12, Pillow, ffmpeg/ffprobe, yt-dlp via `uvx`, Edge TTS `en-US-AriaNeural`, ASS subtitles, Wikimedia Commons, YouTube source footage.

**No commits:** Repository policy says not to commit unless the user explicitly asks. All work remains uncommitted.

---

## Task 1 — Preserve research and resolve factual conflicts

**Files:**
- Keep: `docs/research/costly-verdict-million-view-strategy-2026-07-25/REPORT.md`
- Keep: `docs/research/costly-verdict-million-view-strategy-2026-07-25/SUPPLEMENTAL-SOURCES.md`
- Update later: `docs/research/costly-verdict-million-view-strategy-2026-07-25/summary.json`

**Actions:**
1. Treat “twelve days” as the interval from partnership signing to document withdrawal, not guaranteed total association length.
2. Use `$1.59M in 2011` for the physical-contract payoff; do not use a volatile current 10%-of-Apple number as the final fact.
3. Keep claims about partnership liability scoped to possible personal exposure, not certain seizure.
4. Build a source ledger covering every spoken number and every direct quote.

**Verification:**
- Search final script for misleading phrases: `worked at Apple for only 12 days`, `Apple took his house`, `would definitely be worth`, or uncited current market-cap math.

## Task 2 — Build and gate the 0–3 second hook

**Files:**
- Create: `output/projects/ronaldwayne/hooks/2026-07-25-ronaldwayne-hook-a.mp4`
- Create: `output/projects/ronaldwayne/analysis/hook-a-contact-sheet.jpg`
- Create: `output/projects/ronaldwayne/checks/hook-a-probe.json`

**Hook copy:**

> “He sold 10% of Apple for $800. It looks like history's worst trade—but they skip what he could lose.”

**Hook visual beats:**
- `0.0–0.75s`: tight Ronald Wayne face, `$800` impact text, cash-hit SFX.
- `0.75–1.50s`: split-screen Wayne / Apple first logo, `10%` ring collapses.
- `1.50–2.25s`: contract texture and signature stamp, `WORST TRADE?`.
- `2.25–3.00s`: house/car/bank icons enter behind Wayne, then red creditor arrows approach; caption `WHAT COULD HE LOSE?`.

**Gate:**
- Manual frame inspection at `0.0`, `0.2`, `0.75`, `1.5`, `2.25`, `2.9s`.
- Confirm face/action at frame 0, caption by 0.2s, SFX in 0–1s, open loop remains unresolved, and each visual change advances the question.
- Independent naive viewer must answer without explanation: what happened, what remains unknown, and whether they would continue. Until the user or another real cold viewer supplies this evidence, full-render status remains blocked by `docs/WORKFLOW.md` Stage 0 item 6.

## Task 3 — Download and normalize sources

**Directories:**
- Create: `output/projects/ronaldwayne/source/video/`
- Create: `output/projects/ronaldwayne/source/images/`
- Create: `output/projects/ronaldwayne/source/articles/`
- Create: `output/projects/ronaldwayne/source/metadata/`

**Video sources to download at highest available quality:**
- BBC Ronald Wayne: `bvWh8sh_wPY`
- NextShark Ronald Wayne: `YAF2-U7InWE`
- CBS direct interview: `M3R50CA9ok8`
- Steve Wozniak account: `hPyI_RtHFGU`
- KPVM Wayne account: `_nFHSv5GxhI`

**Licensed image sources:**
- Ronald Wayne portrait, CC BY-SA 4.0
- Ronald Wayne at Macworld, CC BY-SA 3.0
- Apple first logo, public domain
- Apple I museum image, CC BY-SA 4.0
- Apple I public-domain image
- Generic historical contract image, labeled `ILLUSTRATION`

**Article proof cards:**
- CNN, CNBC, NPR, BBC, Cult of Mac, NextShark.
- Render custom headline cards from verified title/publisher/date; do not depend on a full webpage screenshot or paywall.

**Verification:**
- `ffprobe` every downloaded video.
- Store source URL, title, uploader, upload date, duration and hash.
- Verify image dimensions and licenses.

## Task 4 — Synthesize and preflight narration

**Files:**
- Create: `output/projects/ronaldwayne/scripts/script-v1.txt`
- Create: `output/projects/ronaldwayne/tts/*.wav`
- Create: `output/projects/ronaldwayne/checks/tts-report.json`
- Create: `output/projects/ronaldwayne/checks/narrator-preview.wav`
- Create: `output/projects/ronaldwayne/checks/narrator-preview-transcript.txt`

**Narration script (150 words before source-voice substitutions):**

> He sold 10% of Apple for $800. It looks like the worst trade in business history. But the part everyone skips is what he could lose.
>
> Wayne drafted Apple's partnership agreement. Twelve days after signing it, he removed his name. Apple was not a corporation yet. If the business could not pay, the partners could be personally liable.
>
> Jobs and Wozniak were young, broke, and willing to risk everything. Wayne was 41. He had a house, a car, and money creditors could reach.
>
> And here is the twist: Wayne says he believed Apple would succeed. He left because he did not want decades of paperwork instead of building his own inventions.
>
> Before the verdict, like, subscribe, and comment: sell or stay?
>
> Wayne says he does not regret leaving Apple. His regret? Selling the original contract for $500. In 2011, it sold for $1.59 million.
>
> So was he history's biggest fool—or did $800 buy his freedom?

**TTS:**
- Engine: Edge TTS production fallback.
- Voice: `en-US-AriaNeural`.
- Generate sentence/beat-level clips, never one monolithic file.
- Fit only by small positive engine rate or bounded post-tempo; never slow speech to fill a slot.
- Normalize each clip before adding timeline silence.

**Source-voice evidence:**
- CBS near `00:47.27`: Wayne says there was no doubt and it was the right product.
- NextShark near `07:35.6`: Wayne says the physical contract is what he regrets.
- Each voice moment may span approximately 2–3 seconds, but the visual angle/reframe still changes at 1.5 seconds.

**Verification:**
- Duration, non-silence, peak and LUFS checks for each clip.
- Assemble narrator-only preview.
- Run ASR over hook, middle, CTA and ending; compare to intended copy.

## Task 5 — Build the 40-beat visual timeline

**File:**
- Create: `pipeline/ronaldwayne/render_ronaldwayne_v1.py`
- Create: `output/projects/ronaldwayne/scripts/edl-v1.json`

**Duration:** exactly 60.0 seconds (`40 × 1.5s`) unless TTS preflight proves a shorter 55.5 or 57.0 second frame-exact timeline reads better.

**Beat families:**

1. `0–6s — Impossible deal`: Wayne face, 10% counter, $800, Apple I, headline proof.
2. `6–15s — The document`: 1976 timeline, contract typing, three founder nodes, withdrawal stamp.
3. `15–27s — Hidden liability`: partnership/corporation comparison, debt arrows, house/car/bank assets, Jobs/Wozniak contrast.
4. `27–36s — Countertwist`: direct Wayne/CBS evidence that he believed in the product; Apple I; documentation role versus inventions.
5. `36–42s — Verdict lock + CTA`: custom scale UI; `SELL` versus `STAY`; Like + Subscribe + Comment spoken explicitly.
6. `42–54s — Actual regret`: no-regrets source card, physical contract, `$500`, auction counter to `$1.59M`.
7. `54–60s — Payoff and loop`: Wayne face, freedom visual, split verdict; final question matches opening.

**Editing rule:**
- Every 1.5-second boundary changes source, camera crop, panel layout, proof state or semantic animation.
- The first 5 seconds contain additional sub-beats at 0.75-second cadence.
- No decorative zoom counts unless it reveals, compares or reweights evidence.
- A source-voice line may remain continuous across two beats while visual crop/source panel changes.

**Transformative value-adds:**
- Commentary/TTS spine.
- Multi-source mashup.
- Factual citations.
- Animated personal-liability model.
- Counter-argument from Wozniak/source evidence.
- Custom verdict scale and auction value counter.

## Task 6 — Render captions, graphics, sound and final MP4

**Files:**
- Create: `output/projects/ronaldwayne/work/captions.ass`
- Create: `output/projects/ronaldwayne/work/music.wav`
- Create: `output/projects/ronaldwayne/work/sfx/*.wav`
- Create: `output/projects/ronaldwayne/final/2026-07-25-ronaldwayne_v1_800_bought_freedom.mp4`

**Visual requirements:**
- 1080x1920, 30 fps, H.264.
- Komika Axis English captions, 2–5 words per burst, one highlighted keyword.
- Caption visible by 0.2 seconds.
- Source labels small but readable.
- Moving MONEY BLINDSPOT watermark changes position every story section.
- No static black footer; crops refill frame uniformly.

**Audio requirements:**
- TTS dominant near -16 LUFS integrated target with TP <= -1.5 dB.
- Three score states: apparent mistake, hidden-risk tension, verdict/payoff.
- Event-bound SFX at the first `$800` impact, stamp, debt exposure, CTA lock and auction count.
- Brief music attenuation before the product-belief twist and actual-regret payoff.

## Task 7 — Media-first verification

**Files:**
- Create: `output/projects/ronaldwayne/checks/final-probe.json`
- Create: `output/projects/ronaldwayne/checks/decode.log`
- Create: `output/projects/ronaldwayne/checks/cadence-report.json`
- Create: `output/projects/ronaldwayne/analysis/final-contact-sheet.jpg`
- Create: `output/projects/ronaldwayne/analysis/hook-mobile-preview.jpg`
- Create: `output/projects/ronaldwayne/checks/final-asr.txt`

**Checks:**
1. Full ffmpeg decode with zero errors.
2. `1080x1920`, 30 fps, H.264 + AAC, 50–75 seconds.
3. Fixed-frame extraction every 0.75 seconds for 0–6s and every 1.5 seconds for the full video.
4. Verify every 1.5-second interval has a semantic visual/reframe change.
5. Manual vision review of hook, liability model, CTA, contract payoff and ending.
6. Black-frame, fixed-black-band, freeze, silence, clipping and loudness checks.
7. Final ASR on hook, CTA and tail.
8. Confirm all source clips are under 15 seconds and aggregate borrowed footage is under 50% of each source.
9. Read hook and ending together to verify loop closure.

## Task 8 — Production document and upload package

**Files:**
- Create: `docs/production/ronaldwayne-v1-800-bought-freedom.md`

**Canonical package:**
- **Title:** `He Sold Apple For $800 🍎💸` (30 characters or fewer after counting)
- **Description:** first line mirrors title; one factual sentence; exactly `#shorts #apple #money`.
- **Audience:** Not made for kids.
- **Language:** English.
- **Category:** Education.
- **Playlist:** Finance / MONEY BLINDSPOT master playlist.
- **Related Video:** current winner, to be selected only after lane eligibility check.

**Status rule:**
- `Draft — media verified, Hook Gate naive-viewer evidence pending` until the user/cold viewer supplies the required response.
- Do not upload automatically.
- Complete Hook Retro and Workflow Delta even if each answer is `none found` / `none`.
