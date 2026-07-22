# HardKnocks Atlanta Billionaire Hunt Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce and media-QC one 50–60 second English finance Short from `VW2t21zzYl8`, using a Mission/Challenge hook that is materially different from the preceding John Ruiz Direct Dare Question.

**Architecture:** A dedicated one-off Python renderer extracts sub-15-second source segments, uniformly crops away source captions, applies active-speaker reframing, assembles the challenge arc, composites captions/editorial overlays/Pexels/proof/CTA/watermark, and performs the final audio mix and speed-up. The deliverable is the real MP4 plus a production document and upload package; no renderer unit tests are added because project policy requires media-first verification.

**Tech Stack:** Python 3, Pillow, ffmpeg/ffprobe, yt-dlp, mlx-whisper, Qwen3-TTS MLX through `pipeline/hardknocks/tts_qwen_narrator.py`, Pexels footage, ASS captions, Markdown production/QC docs.

**No commits:** Repository policy says not to commit unless the user explicitly asks. All work remains uncommitted.

---

## File Map

- Create: `pipeline/hardknocks/render_hardknocks_v13_billionaire_hunt.py` — one-off renderer, timeline, graphics, audio, captions, compositing, and validation.
- Create: `docs/production/hardknocks-v13-atlanta-billionaire-hunt.md` — source map, checklist evidence, QC results, Hook Retro, Workflow Delta, and canonical upload package.
- Modify: `data/source_videos.csv` — register `VW2t21zzYl8` once.
- Create media: `output/projects/hardknocks/source/VW2t21zzYl8.mp4` — highest-quality source.
- Keep research media: `output/projects/hardknocks/source/VW2t21zzYl8.en.vtt` and `VW2t21zzYl8.transcript-timed.txt`.
- Create work artifacts: `output/projects/hardknocks/clips/v13_billionaire_hunt_work/`.
- Create final: `output/projects/hardknocks/final/2026-07-22-hardknocks_v13_atlanta_billionaire_hunt.mp4`.

## Task 1: Acquire and Register the Source

**Files:**
- Create: `output/projects/hardknocks/source/VW2t21zzYl8.mp4`
- Modify: `data/source_videos.csv`

- [ ] **Step 1: Download the source at the highest available 2160p-or-better quality**

Run:

```bash
yt-dlp -f 'bestvideo[height>=2160]+bestaudio/bestvideo+bestaudio' \
  --merge-output-format mp4 \
  -o 'output/projects/hardknocks/source/VW2t21zzYl8.%(ext)s' \
  'https://www.youtube.com/watch?v=VW2t21zzYl8'
```

Expected: one merged source file at `output/projects/hardknocks/source/VW2t21zzYl8.mp4`, with the source video stream at 3840×2160.

- [ ] **Step 2: Probe the downloaded source**

Run:

```bash
ffprobe -v error -show_entries \
  stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels \
  -show_entries format=duration -of json \
  output/projects/hardknocks/source/VW2t21zzYl8.mp4
```

Expected: video 3840×2160, audio present, duration approximately 1,316 seconds.

- [ ] **Step 3: Add exactly one source-registry row**

Append:

```csv
VW2t21zzYl8,"Asking Wealthy Americans How They Got Rich! (Atlanta)",School of Hard Knocks,finance,2026-07-22,hardknocks,"hardknocks_v13 Atlanta Billionaire Hunt; Mission/Challenge hook; escalating-candidate montage; Rick Jackson $3B revenue/$1B Forbes verification; Business Lesson Payoff"
```

Before appending, search the CSV for `VW2t21zzYl8`; do not add a duplicate row.

- [ ] **Step 4: Validate registry shape**

Run a Python `csv.DictReader` check that every row has the same seven columns as the header and that `VW2t21zzYl8` appears exactly once.

Expected: `rows=<count> matching_source=1 malformed=0`.

## Task 2: Lock the Source Timeline and Hook Gate

**Files:**
- Create: `output/projects/hardknocks/clips/v13_billionaire_hunt_work/checks/stage0/`
- Create: `output/projects/hardknocks/clips/v13_billionaire_hunt_work/timeline.json`

- [ ] **Step 1: Start from these candidate source windows**

Use these windows as the first precise edit map; adjust only at word boundaries after waveform/ASR inspection:

```text
mission                 0.08–5.32
rejection_1            88.48–92.72
rejection_2           114.24–116.90
rejection_3           123.52–126.28
waffle_origin         188.64–196.00
waffle_scale          194.48–202.48
prison_wealth         559.60–566.00
prison_eight_figures  602.64–607.68
rick_approach         959.76–968.24
rick_revenue          968.24–976.00
rick_confirm          980.32–985.92
rick_no_degree       1017.92–1021.04
rick_commission      1024.08–1032.24
rick_bought_firm     1032.24–1035.28
```

No single retained source clip may reach 15 seconds.

- [ ] **Step 2: Extract Stage-0 frames and hook audio**

Extract full-resolution frames at source timestamps 0.08, 0.20, 1.0, 2.0, 3.0, 4.0, and 5.0 seconds, plus a 0–10 second hook WAV.

Expected: frame zero shows the moving host’s face/body, no title card or freeze, and the 0–10 second audio includes the complete mission promise.

- [ ] **Step 3: Inspect the hook manually**

Record PASS/FAIL for:

```text
human face at first frame
moving footage throughout 0–3s
caption visible by 0.2s
one visual/overlay change every 1–2s in 0–5s
no full-screen B-roll or proof card in 0–10s
promise/gap established by 0–2s
hook family differs from B1 Direct Dare Question
```

If any row fails, change the starting source timestamp or overlay cadence before implementing the rest.

- [ ] **Step 4: Derive hard-cut and pause thresholds from this source**

Use word timestamps from `VW2t21zzYl8.en.vtt` or a local `mlx_whisper` run to compute inter-word gap distribution for selected clips. Choose the pause threshold at the natural valley in this source’s own distribution; record the distribution and selected threshold in `timeline.json`.

Expected: no fixed threshold copied from another project.

## Task 3: Prepare Verification, Supporting Visual, SFX, and Narration Assets

**Files:**
- Create: `output/projects/hardknocks/clips/v13_billionaire_hunt_work/proof_sources/forbes_rick_jackson.png`
- Reuse: `output/shared/pexels/contract_signing_7981954.mp4`
- Create: `output/projects/hardknocks/clips/v13_billionaire_hunt_work/audio/cta_qwen.wav`
- Create: `output/projects/hardknocks/clips/v13_billionaire_hunt_work/audio/payoff_qwen.wav`

- [ ] **Step 1: Capture the independent Forbes proof**

Capture a page screenshot from:

```text
https://www.forbes.com/profile/rick-jackson
```

The crop must visibly retain publisher identity and these facts:

```text
$1B real-time net worth
$3B revenue
22 businesses
```

Do not use the School of Hard Knocks source as verification.

- [ ] **Step 2: Validate existing Pexels media before reuse**

Probe and fully decode:

```bash
ffprobe -v error -show_streams -show_format -of json output/shared/pexels/contract_signing_7981954.mp4
ffmpeg -v error -i output/shared/pexels/contract_signing_7981954.mp4 -f null -
```

Extract a contact sheet from the exact contract-signing excerpt, inspect for embedded text/logos/watermarks, and label the footage `ILLUSTRATION` in the final edit. Keep original interview footage throughout the Waffle House beat; do not insert chef/kitchen stock footage because it implies restaurant operations rather than multi-location ownership.

- [ ] **Step 3: Synthesize the canonical Finance narrator CTA**

Run inside the pinned MLX environment:

```bash
.venv-mlx/bin/python pipeline/hardknocks/tts_qwen_narrator.py \
  --text 'Would you take his first bet? Like, subscribe, and comment.' \
  --out output/projects/hardknocks/clips/v13_billionaire_hunt_work/audio/cta_qwen.wav
```

- [ ] **Step 4: Synthesize the canonical Finance narrator payoff**

Run:

```bash
.venv-mlx/bin/python pipeline/hardknocks/tts_qwen_narrator.py \
  --text 'He removed their risk, then earned the right to own.' \
  --out output/projects/hardknocks/clips/v13_billionaire_hunt_work/audio/payoff_qwen.wav
```

- [ ] **Step 5: Verify both narration files before assembly**

For each WAV:

1. Probe sample rate/channels/duration.
2. Run local ASR.
3. Measure integrated loudness and true peak.
4. Confirm there is no hallucinated tail or truncated final word.

Expected: 48 kHz stereo, exact intended sentence recognized. During compositing, apply compressor then `loudnorm`, then any `adelay`; never delay before loudness normalization.

## Task 4: Implement the One-Off Renderer

**Files:**
- Create: `pipeline/hardknocks/render_hardknocks_v13_billionaire_hunt.py`

- [ ] **Step 1: Define immutable timeline data**

The renderer must define `Segment` records with:

```python
name: str
source_start: float
source_end: float
turns: tuple[tuple[float, float], ...]
zoom: float
act: str
```

The renderer must reject any `source_end - source_start >= 15` and print a final source-use report.

- [ ] **Step 2: Implement aspect-safe source-caption removal and speaker reframing**

Use the established HardKnocks pattern:

1. Scale the 4K landscape source to 1920px height.
2. Crop a 1080×1920 active-speaker viewport with frame-exact focus changes.
3. Crop the source-caption bottom band.
4. Uniformly scale both dimensions by the same recovery factor.
5. Center-crop back to 1080×1920.

Never use a permanent black `drawbox` and never non-uniformly stretch 1080×1650 to 1080×1920.

- [ ] **Step 3: Implement the exact story order**

Assemble:

```text
mission
rejection montage
waffle candidate
prison/eight-figures candidate
rick approach/revenue/confirmation
mid-roll CTA at final t=39–42s
rick no-degree/commission/bought-firm lesson
narrator payoff
```

Use the game-state progression:

```text
ONE MISSION
FIND A BILLIONAIRE
BILLIONAIRE FOUND: NO
14 LOCATIONS — NOT THE TARGET
SOURCE-REPORTED: EIGHT FIGURES
BILLIONAIRE FOUND
SOURCE CLAIM: $3B/YEAR REVENUE
FORBES: $1B NET WORTH
REMOVE THEIR RISK
EARN THE UPSIDE
```

- [ ] **Step 4: Implement caption generation from word timestamps**

Use `assets/fonts/komika-axis/KOMIKAX_.ttf` and `docs/verification/caption-calibration/caption-profile.json`:

```text
base 80px
emphasized keyword 90px
stroke 8px
center Y normally 60%, allowed 55–65%
horizontal margin 8%
2–5 words per burst
caption visible by 0.2s
```

When reconstructing words, concatenate raw `mlx_whisper` word tokens and strip once; do not strip/rejoin with spaces. Use ASS inline colors for one emphasized keyword per burst.

- [ ] **Step 5: Implement proof-coupled overlays**

Use:

1. Continuous original Waffle House interview footage over the scale beat; no chef/kitchen stock substitution.
2. Forbes proof crop over Rick’s verification beat, retaining publisher identity.
3. Pexels contract-signing footage over the commission-only lesson, labeled `ILLUSTRATION`.

No full-screen Pexels or proof image may replace the host’s face at any time in final 0–10 seconds.

- [ ] **Step 6: Implement CTA and moving watermark**

The Mid-Roll Triple CTA must begin between 39.0 and 42.0 seconds and visibly/spokenly include Like, Subscribe, and Comment. Keep moving footage visible behind the translucent CTA.

Create a compact moving watermark that occupies different safe-corner positions over at least three timeline windows without covering captions, faces, proof, or CTA.

- [ ] **Step 7: Implement audio mix and transitions**

Requirements:

```text
early SFX in 0–1s
matching SFX on hook phrase, rejection verdicts, proof entrance, billionaire confirmation, CTA
source dialogue normalized near -16 LUFS
Qwen: acompressor -> loudnorm -> adelay
music low enough to preserve dialogue intelligibility
0.12s segment fade-in and 0.20s fade-out before hard concat
final true peak <= -1.0 dBTP
```

- [ ] **Step 8: Implement final speed-up and render guards**

Apply a modest final speed-up only after all cuts/overlays are assembled. Derive the factor from the actual draft runtime so the result remains 50–75 seconds, preferably 56–60 seconds. Keep video/audio in sync using `setpts` and legal `atempo` stages.

The renderer must fail if the final probe does not show:

```text
1080x1920
H.264
yuv420p
30 fps
AAC stereo 48 kHz
50–75 seconds
```

## Task 5: Render the Actual MP4 and Fix Media Defects

**Files:**
- Create: `output/projects/hardknocks/final/2026-07-22-hardknocks_v13_atlanta_billionaire_hunt.mp4`

- [ ] **Step 1: Run the renderer**

Run:

```bash
python3 pipeline/hardknocks/render_hardknocks_v13_billionaire_hunt.py
```

Expected: the final dated MP4 plus timeline/report artifacts in the v13 work directory.

- [ ] **Step 2: Perform the first full decode and spec probe immediately**

Run ffprobe and a full ffmpeg decode before visual polishing. Fix any missing stream, frame mismatch, timestamp error, or codec/spec failure at the renderer root cause.

- [ ] **Step 3: Run final ASR and inspect hook/tail**

Transcribe the complete final, final 0–10 seconds, and final 8 seconds. Compare exact recognized hook and closing line with the intended text. If a word is clipped, extend the relevant source or VO tail before rerendering.

- [ ] **Step 4: Generate manual-review frames**

Extract full-resolution frames at:

```text
0.0, 0.2, 1.0, 2.0, 3.0, 5.0, 9.5,
every speaker turn,
every Pexels entrance/exit,
every proof entrance/exit,
39.0, 40.0, 41.5, 42.5,
final-1.0, final-0.1
```

Also create a 1fps contact sheet and a 360×640 mobile-preview contact sheet.

- [ ] **Step 5: Fix every visible or audible defect, then rerender**

Blocking defects include source-caption bleed, black footer, stretched faces, clipped text, proof too small to read, generic/incorrect Pexels visuals, face blackout in 0–10 seconds, late CTA, silent/jammed cuts, Qwen loudness dips, clipped last words, or a frozen final frame.

## Task 6: Run the Full Media QC Checklist

**Files:**
- Create: `output/projects/hardknocks/clips/v13_billionaire_hunt_work/checks/`

- [ ] **Step 1: Run automated media scans**

Run and save outputs for:

```text
ffprobe specs
full decode
blackdetect
freezedetect
silencedetect
overall loudnorm analysis
per-narrator-window loudness
0.1s audio-boundary scans around every hard cut
bottom-row brightness scan
source-use duration report
```

Expected: no unexplained black frames, no unintended freeze, no missing dialogue, no permanent black footer, and all source clips below 15 seconds.

- [ ] **Step 2: Verify ADR-0034 craft items manually**

Record PASS for:

```text
early SFX at 0–1s
caption visible by 0.2s
caption 2–5 words with one highlighted keyword
caption center 55–65% except justified avoidance
visual change every 1–2s in 0–5s
no full-screen face replacement in 0–10s
purposeful transition SFX
custom Triple CTA begins 38–42s
moving watermark changes position
```

- [ ] **Step 3: Verify Transformative Gate and source-use math**

Record commentary present, at least two value-adds, total source duration below 658 seconds, and every source excerpt below 15 seconds.

- [ ] **Step 4: Conduct one final manual replay after all fixes**

Watch the whole final from beginning to end, then separately replay 0–10 seconds, each hard cut, the Forbes proof, CTA window, and final eight seconds. This manual pass happens after the last rerender, not before it.

## Task 7: Write the Production Document and Canonical Upload Package

**Files:**
- Create: `docs/production/hardknocks-v13-atlanta-billionaire-hunt.md`

- [ ] **Step 1: Record source map and real final timeline**

Include exact source timestamps, final timestamps, individual clip durations, total source duration, source-use percentage, narrator lines, Pexels IDs, proof URLs, and renderer/final paths.

- [ ] **Step 2: Record checklist and QC evidence**

Include command outputs or summarized measurements for every Task 6 gate, plus manual frame-review results.

- [ ] **Step 3: Add Hook Retro and Workflow Delta**

Hook Retro must compare:

```text
previous B1 hook family: Direct Dare Question about disputed net worth
revised V13 hook family: Direct Search Question about the candidate ladder
promise/gap timing
frame-zero face/motion
0–5s visual cadence
what remains uncertain until retention data arrives
```

Workflow Delta must name at least one process improvement discovered during this production; if none was required, explicitly state that no reusable workflow change was found.

- [ ] **Step 4: Add exactly one canonical metadata package**

Use:

```text
Title: The Billionaire Hunt 🕵️💰

Description:
The Billionaire Hunt 🕵️💰
Atlanta had one mission: find a billionaire—and learn the bet that started it.
#shorts #billionaire #entrepreneurship

YouTube Studio tags:
billionaire mindset
entrepreneurship lessons
how the rich think
```

Verify the title is at most 30 visible characters and contains exactly two relevant emoji. Keep exactly three visible hashtags and exactly three Studio tags.

- [ ] **Step 5: Record Studio settings**

```text
Audience: Not made for kids
Language: English
Category: Education
Location: Atlanta, Georgia, United States
Playlist: finance vertical master playlist
Related Video: wire per current channel winner/newest-short rule
Altered content: No, unless the final review finds realistic synthetic material beyond narration
Paid promotion: No
Comments: On
Remixing: On
```

## Task 8: Final Repository and Artifact Verification

- [ ] **Step 1: Run `git diff --check` and inspect status**

Expected: no whitespace errors; only intended docs/code/registry changes plus expected untracked research media.

- [ ] **Step 2: Re-probe the final artifact from its canonical path**

Confirm the artifact exists and independently re-run specs/full decode rather than relying on renderer logs.

- [ ] **Step 3: Cross-check every stated user requirement**

Confirm:

```text
new hook differs from previous video
source is VW2t21zzYl8
one complete short exists
all defined checklist gates have evidence
canonical upload package exists
final filename is date-prefixed
no renderer unit tests were added
no commit or push was made
```

- [ ] **Step 4: Report the artifact and QC result**

Return the absolute final MP4 path, runtime/specs, hook comparison, checklist status, and production-doc path. If any gate remains blocked, state it directly instead of claiming completion.

## Task 9: Revision — Question-TTS Hook

This task supersedes only the original Mission/Challenge opening. Tasks 1–8 remain authoritative for the body, proof, CTA, payoff, upload package, and media-first QC.

**Files:**

- Modify: `docs/specs/2026-07-22-hardknocks-atlanta-billionaire-hunt-design.md`
- Modify: `pipeline/hardknocks/render_hardknocks_v13_billionaire_hunt.py`
- Create: `output/projects/hardknocks/clips/v13_billionaire_hunt_work/audio/question_hook_qwen.wav`
- Modify: `docs/production/hardknocks-v13-atlanta-billionaire-hunt.md`
- Replace after verification: `output/projects/hardknocks/final/2026-07-22-hardknocks_v13_atlanta_billionaire_hunt.mp4`

- [ ] **Step 1: Generate the canonical question narration**

Run:

```bash
.venv-mlx/bin/python pipeline/hardknocks/tts_qwen_narrator.py \
  --text "How many millionaires do you have to meet before you find a real billionaire?" \
  --out output/projects/hardknocks/clips/v13_billionaire_hunt_work/audio/question_hook_qwen.wav
```

Use the existing `natural_talker_male_qwen_blog` profile. Do not substitute Edge TTS or a different narrator.

- [ ] **Step 2: Verify the generated question before editing the renderer**

Use `.venv/bin/python` with `mlx_whisper` and `word_timestamps=True`. Confirm the transcript contains the complete question and derive the three caption-burst boundaries from the generated word timestamps:

```text
HOW MANY MILLIONAIRES
DO YOU HAVE TO MEET
BEFORE YOU FIND
A REAL BILLIONAIRE?
```

Reject and regenerate if `millionaires` or `billionaire` is missing or mispronounced.

- [ ] **Step 3: Replace only the opening audio/captions**

In `render_hardknocks_v13_billionaire_hunt.py`:

1. Add `QUESTION_HOOK_VO` to required inputs.
2. Keep the existing moving `mission` footage and all body segments.
3. Remove the old source-line hook captions and replace them with the three ASR-timed question bursts.
4. Remove `ONE MISSION` / `FIND A BILLIONAIRE`; use the question captions as the sole primary hook text.
5. Add the question VO to `build_timed_audio()` at t=0 using `make_positioned_track()` so its timing is represented by real leading-silence samples.
6. Duck source dialogue throughout the `mission` segment; do not allow the original mission sentence to compete with the narrator.
7. Keep the early SFX, moving footage, face visibility, game-state counter, body, proof, CTA and payoff unchanged.

- [ ] **Step 4: Render the real MP4**

Run:

```bash
python3 pipeline/hardknocks/render_hardknocks_v13_billionaire_hunt.py
```

Expected: the canonical date-prefixed MP4 is replaced by a complete 50–75 second artifact and renderer validation passes.

- [ ] **Step 5: Verify the final hook and regression-sensitive windows**

Run final ASR separately for:

```text
0–8s: complete question first; no intelligible original mission dialogue under it
proof/CTA: Forbes proof followed by Like, Subscribe and Comment
tail: complete bought-firm line and Business Lesson Payoff
```

Then re-run ffprobe, full decode, black/freeze/silence detection, loudness measurement, frame-0 face/skin gate, 0–5s mobile contact sheet, full contact sheet and exact proof/CTA/end frames. No renderer unit tests are added.

- [ ] **Step 6: Update production truth**

Update the hook family, exact transcript, timeline, runtime, SHA-256, QC numbers, Hook Retro and Workflow Delta in `docs/production/hardknocks-v13-atlanta-billionaire-hunt.md`. Preserve the existing Stage 6 upload blockers unless live Studio/lane state proves they have changed.
