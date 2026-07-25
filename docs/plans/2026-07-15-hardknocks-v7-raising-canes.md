# HardKnocks V7 Raising Cane's Focus Bet Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce and verify one 45–60-second Raising Cane's business case-study Short using the WEALTHIAN semantic formula and the project's HardKnocks production gates.

**Architecture:** Reuse the proven HardKnocks V6 ffmpeg/Pillow renderer structure, but replace the source, timeline, captions, evidence overlays, and QC assertions with V7-specific data. The final timeline uses four short source-audio excerpts, video-only Pexels proof overlays after the protected face window, self-authored animated analysis, verbatim ASS captions, low music/SFX, and a mild final retention speed-up.

**Tech Stack:** Python 3, `yt-dlp`, `mlx_whisper`, ffmpeg/ffprobe, Pillow, ASS subtitles, unittest.

**Execution note:** The user has not asked for commits. Execute all tasks without `git commit` or `git push`.

---

## File map

**Create**

- `pipeline/hardknocks/render_hardknocks_v7.py` — V7 timeline, source cutting, evidence compositing, captions, audio, render, and QC extraction.
- `pipeline/hardknocks/test_render_hardknocks_v7.py` — timeline/Transformative Gate/output-policy regression tests.
- `docs/production/hardknocks-v7-raising-canes-focus-bet.md` — source decisions, storyboard, specs, QC, and retro.
- `output/projects/hardknocks/source/n5EmUiLNVjg.mp4` — highest-quality source media.
- `output/projects/hardknocks/source/n5EmUiLNVjg_audio16k.wav` — transcription input.
- `output/projects/hardknocks/source/n5EmUiLNVjg_transcript.json` — word-timestamped transcript.
- `output/projects/hardknocks/clips/v7_work/` — intermediates and QC evidence.
- `output/projects/hardknocks/final/2026-07-15-hardknocks_v7_raising_canes_focus_bet.mp4` — final artifact.

**Modify**

- `data/source_videos.csv` — append `n5EmUiLNVjg` only after source lock.

**Reference only**

- `pipeline/hardknocks/render_hardknocks_v6.py`
- `pipeline/hardknocks/test_render_hardknocks_v6.py`
- `docs/WORKFLOW.md`
- `docs/specs/2026-07-15-hardknocks-v7-raising-canes-design.md`

---

### Task 1: Acquire and verify the source

- [ ] **Step 1: Download the maximum-quality source**

Run from repository root:

```bash
yt-dlp \
  -f 'bestvideo[height>=2160]+bestaudio/bestvideo+bestaudio' \
  --merge-output-format mp4 \
  -o 'output/projects/hardknocks/source/n5EmUiLNVjg.%(ext)s' \
  'https://www.youtube.com/watch?v=n5EmUiLNVjg'
```

Expected: `output/projects/hardknocks/source/n5EmUiLNVjg.mp4` exists and contains the 990-second School of Hard Knocks interview.

- [ ] **Step 2: Verify actual source streams**

Run:

```bash
ffprobe -v error -show_streams -show_format -of json \
  output/projects/hardknocks/source/n5EmUiLNVjg.mp4
```

Required:

- video stream exists;
- audio stream exists;
- maximum downloaded video is 3840×2160 when the listed 2160p format remains available;
- duration is approximately 990 seconds.

Do not claim 4K if the actual probe differs.

- [ ] **Step 3: Extract transcription audio**

Run:

```bash
ffmpeg -y -v error \
  -i output/projects/hardknocks/source/n5EmUiLNVjg.mp4 \
  -vn -ac 1 -ar 16000 -c:a pcm_s16le \
  output/projects/hardknocks/source/n5EmUiLNVjg_audio16k.wav
```

Expected: non-empty 16kHz mono PCM WAV.

- [ ] **Step 4: Generate word timestamps**

Run with the installed MLX Whisper environment used by HardKnocks V4–V6:

```bash
python3 - <<'PY'
import json
import mlx_whisper
from pathlib import Path
root = Path('output/projects/hardknocks/source')
result = mlx_whisper.transcribe(
    str(root / 'n5EmUiLNVjg_audio16k.wav'),
    path_or_hf_repo='mlx-community/whisper-large-v3-mlx',
    word_timestamps=True,
)
(root / 'n5EmUiLNVjg_transcript.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + '\n'
)
PY
```

Expected: every selected phrase can be traced to words carrying `start` and `end` timestamps.

- [ ] **Step 5: Append the dedup registry entry after verification**

Append exactly one CSV row:

```csv
n5EmUiLNVjg,"How I Turned $50,000 Into $20 Billion",School of Hard Knocks,finance,2026-07-15,hardknocks,"hardknocks_v7 Raising Cane's one-product focus bet; WEALTHIAN-style Authority-Led Hidden Economics Reveal; Multi-Clip Mashup"
```

Verify with:

```bash
python3 - <<'PY'
from pathlib import Path
text = Path('data/source_videos.csv').read_text()
assert text.count('n5EmUiLNVjg') == 1
PY
```

---

### Task 2: Lock exact source windows and pass Stage 0

- [ ] **Step 1: Extract exact selected words from the transcript**

Write a temporary inspection script that prints all words and reconstructed text inside these candidate windows:

- 188.0–200.72s — rejection/focus;
- 299.20–313.84s — funding;
- 354.80–366.00s — scale;
- 761.84–774.16s — rebuild rule.

Reconstruct each phrase with:

```python
text = ''.join(word['word'] for word in words).strip()
```

Required final semantic units:

1. `the professor gave it the worst grade in the class ... the concept will never work`;
2. `serving just chicken fingers ... restaurants ... adding menu items ... variety`;
3. `$50,000 ... small SBA loan for $50,000 ... old restaurant space`;
4. `$400 million ... north of $20 billion`;
5. `another cravable product ... focus ... build a team ... scale it`.

- [ ] **Step 2: Choose final word-safe boundaries**

Each final excerpt must:

- start on a complete grammatical unit;
- end after the final required word;
- remain `<15.0` seconds;
- preserve the numbers and qualifications heard in the source;
- not rely on JSON3 rolling-cue boundaries.

Save the chosen start/end pairs in the renderer's `ClipPlan` declarations and protect the final words with unit tests.

- [ ] **Step 3: Extract candidate visual frames**

For every final source start, extract frame 0 and +0.5s:

```bash
ffmpeg -y -v error -ss START -i output/projects/hardknocks/source/n5EmUiLNVjg.mp4 \
  -frames:v 1 output/projects/hardknocks/clips/v7_work/candidates/NAME_0.jpg
ffmpeg -y -v error -ss START_PLUS_0_5 -i output/projects/hardknocks/source/n5EmUiLNVjg.mp4 \
  -frames:v 1 output/projects/hardknocks/clips/v7_work/candidates/NAME_05.jpg
```

Manually inspect all eight frames. The first excerpt must start on moving human footage with a readable face, not food b-roll, a graphic, or a title card.

- [ ] **Step 4: Reject a freeze-frame hook**

Extract 0–3s of the candidate at 10fps and calculate consecutive-frame mean absolute deltas. Reject the candidate when median delta is `<=1.0` or any sustained 0.5-second interval is effectively frozen.

- [ ] **Step 5: Record the locked storyboard**

Place the exact verbatim source text and a minimum five-row timeline storyboard into `docs/production/hardknocks-v7-raising-canes-focus-bet.md` before full render.

---

### Task 3: Create RED renderer tests

- [ ] **Step 1: Create `pipeline/hardknocks/test_render_hardknocks_v7.py`**

The test module must import these V7 symbols:

```python
from render_hardknocks_v7 import (
    FPS,
    FINISH_PAD,
    HOOK_CAPTIONS,
    PEXELS_OVERLAYS,
    POST_SPEED,
    SOURCE_DURATION,
    TIMELINE,
    TOTAL_FRAMES,
    final_duration,
    finish_audio_filter,
    finish_video_filter,
    source_usage_ratio,
    tts_lines,
    validate_timeline,
)
```

Add tests for:

```python
def test_timeline_passes_transformative_gate():
    validate_timeline(TIMELINE, total_frames=TOTAL_FRAMES)
    assert source_usage_ratio(TIMELINE) <= 0.5
    assert 45.0 <= final_duration() <= 60.0


def test_every_source_excerpt_is_under_fifteen_seconds():
    source = [clip for clip in TIMELINE if clip.kind == 'source']
    assert len(source) >= 4
    assert all(clip.frames / FPS < 15.0 for clip in source)


def test_story_has_all_required_beats():
    names = {clip.name for clip in TIMELINE}
    assert {
        'rejection_focus',
        'funding_proof',
        'scale_proof',
        'rebuild_rule',
    }.issubset(names)


def test_hook_caption_is_visible_by_point_two():
    assert TIMELINE[0].name == 'rejection_focus'
    assert TIMELINE[0].kind == 'source'
    assert HOOK_CAPTIONS[0][0] <= 0.2
    assert HOOK_CAPTIONS[0][2] == 'THE WORST GRADE'


def test_pexels_never_replaces_the_face_before_ten_seconds():
    assert min(window.start for window in PEXELS_OVERLAYS) / POST_SPEED >= 10.0


def test_no_neural_voice_interrupts_todd_graves():
    assert tts_lines() == []


def test_finish_flushes_the_final_spoken_word():
    assert finish_audio_filter() == f'atempo={POST_SPEED}'
    assert FINISH_PAD >= 0.5
    assert finish_video_filter().startswith('tpad=')
```

Add exact boundary tests for the last words `variety`, `$50,000`, `$20 billion`, and `scale it` after the MLX transcript determines their word-end timestamps.

- [ ] **Step 2: Run the tests and confirm RED**

Run:

```bash
python3 -m unittest pipeline/hardknocks/test_render_hardknocks_v7.py -v
```

Expected: import failure because `render_hardknocks_v7.py` does not exist yet.

---

### Task 4: Acquire and verify Pexels evidence

- [ ] **Step 1: Search the Pexels API without exposing the key**

Use `PEXELS_API_KEY` only from the environment. Search portrait video results for:

- `restaurant kitchen food preparation`;
- `fried chicken kitchen`;
- `small restaurant renovation`.

Never print the API key or pass it as a command-line argument.

- [ ] **Step 2: Select one or two genuinely relevant assets**

Prefer real moving footage showing:

- one focused kitchen line or a single plated product;
- restaurant workers preparing/serving food;
- no recognizable competing restaurant logo.

Download the best useful resolution to `output/shared/pexels/` using the Pexels numeric video ID as the cache key.

- [ ] **Step 3: Verify every used Pexels window**

For each intended source offset, extract start/middle/end frames. Review contact sheets and OCR for:

- brand names;
- menus with conflicting product copy;
- watermarks;
- static/near-static motion;
- poor portrait crop.

Reject any clip that fails. Record the accepted Pexels URL, ID, local path, query, and exact used offsets in the production doc.

---

### Task 5: Implement the V7 renderer and turn tests GREEN

- [ ] **Step 1: Create `pipeline/hardknocks/render_hardknocks_v7.py` from the V6 structure**

Retain and adapt the tested V6 units:

- `TimelineClip`, `ClipPlan`, timeline accumulation;
- `probe`, `max_volume_db`, `assert_not_silent`;
- 4K-to-portrait source crop/zoom rendering;
- concat with uniform 48kHz stereo audio;
- video-only Pexels evidence compositing that preserves source audio;
- ASS captions;
- music/SFX generation and mixing;
- final `tpad + setpts` / `atempo` pass;
- check-frame extraction and `validate_output`.

Replace all V6-specific source, Pexels, file paths, captions, timeline, impact frames, labels, and validation names.

- [ ] **Step 2: Define the four-piece V7 timeline**

Use the word-safe boundaries from Task 2 and these stable names:

```python
ClipPlan('rejection_focus', 382, 'source', 188.00, crop_focus=0.50, zoom=1.42)
ClipPlan('funding_proof', 439, 'source', 299.20, crop_focus=0.50, zoom=1.38)
ClipPlan('scale_proof', 336, 'source', 354.80, crop_focus=0.50, zoom=1.44)
ClipPlan('rebuild_rule', 370, 'source', 761.84, crop_focus=0.50, zoom=1.40)
```

These values are executable JSON3-derived candidates. Replace a number only when Task 2's MLX word timestamps identify a more accurate grammatical boundary. Split a semantic beat into multiple visual pieces only when needed for crop cadence; preserve every required spoken phrase and keep each resulting piece below 15 seconds.

- [ ] **Step 3: Implement WEALTHIAN-style captions**

Use ASS styles with:

- hook: yellow, all caps, approximately 82px, top-safe zone;
- body: white/yellow, approximately 64–74px, lower safe zone;
- 1–3 words per hook burst;
- 2–5 words per body burst;
- first hook at 0.10s raw timeline;
- black outline/background for readability;
- source citation in a visually separate compact style.

Every verbatim caption must come from the final word-timestamped source text. Editorial overlays such as `ONE CORE PRODUCT` and `SOURCE-REPORTED` must not be presented as spoken quotes.

- [ ] **Step 4: Implement animated value-add overlays**

Add timed overlays for:

1. `VARIETY` versus `ONE CORE PRODUCT`;
2. `$50K CASH + $50K SBA`;
3. `1 STORE → 900+ SOURCE-REPORTED`;
4. `CRAVABLE PRODUCT → FOCUS → TEAM → SCALE`;
5. compact source citation.

Use Pillow width measurement for every line before render. Shorten copy before reducing the primary hook below the established size floor.

- [ ] **Step 5: Implement proof-footage grammar**

Define typed Pexels overlay records with `start`, `end`, `source_offset`, and `mode` (`corner` or `fullscreen`). Validation must reject:

- any full-screen or Pexels entry before final t=10s;
- any window outside raw timeline bounds;
- any missing Pexels file.

Full-screen proof after t=10s must replace video only; the selected School of Hard Knocks audio remains uninterrupted.

- [ ] **Step 6: Implement audio and final-tail protection**

- original dialogue normalized to approximately -16 LUFS;
- music mixed at a low level and ducked beneath dialogue;
- sparse impact sounds at mechanism/capital/scale transitions;
- no TTS inputs;
- `tpad` final video by at least 0.5s before `setpts`;
- audio uses `atempo=POST_SPEED`;
- `-shortest` only after tail padding is present.

- [ ] **Step 7: Run the unit tests and make them GREEN**

Run:

```bash
python3 -m unittest pipeline/hardknocks/test_render_hardknocks_v7.py -v
```

Expected: all V7 tests pass with zero failures and zero errors.

---

### Task 6: Render and run mechanical QC

- [ ] **Step 1: Render the full artifact**

Run:

```bash
python3 pipeline/hardknocks/render_hardknocks_v7.py
```

Expected final path:

```text
output/projects/hardknocks/final/2026-07-15-hardknocks_v7_raising_canes_focus_bet.mp4
```

- [ ] **Step 2: Verify stream/spec contract**

Run `ffprobe` and assert:

- 1080×1920;
- H.264/yuv420p;
- 30fps;
- AAC, 48kHz stereo;
- 45–60 seconds;
- video and audio streams both present.

- [ ] **Step 3: Decode the complete file**

Run:

```bash
ffmpeg -v error \
  -i output/projects/hardknocks/final/2026-07-15-hardknocks_v7_raising_canes_focus_bet.mp4 \
  -f null -
```

Expected: exit 0 and no decode errors.

- [ ] **Step 4: Run black/silence/volume gates**

- `blackdetect` must report no sustained black segment;
- `silencedetect=noise=-35dB:d=1.0` must not reveal missing dialogue windows;
- hook, funding, scale, and rebuild windows must each exceed the non-silent threshold;
- source and final audio must not clip.

---

### Task 7: Run visual and semantic QC, then iterate

- [ ] **Step 1: Inspect the complete hook window manually**

Extract fixed frames at:

```text
0.00, 0.10, 0.50, 1.00, 1.50, 2.00, 3.00, 4.00, 5.00, 6.00, 7.00, 8.00, 9.00, 10.00
```

Confirm:

- real human motion from frame 0 through 3s;
- hook visible by 0.2s;
- no caption clipping;
- Raising Cane's/mechanism not fully resolved at frame 0;
- speaker remains visible through 10s;
- visual/caption change approximately every 1–2s.

- [ ] **Step 2: Inspect body and payoff contact sheets**

Extract body frames every approximately 2.5 seconds plus all overlay boundaries. Confirm:

- Pexels footage is relevant and unbranded;
- data overlays are readable and correctly labeled;
- no text-only regression;
- no missing/torn subtitles;
- source crops keep the correct speaker visible;
- the last frame/payoff is not visually or semantically cut.

- [ ] **Step 3: Transcribe the final exported MP4**

Use Whisper large-v3 on the final artifact and assert recovery of:

- `worst grade`;
- `concept will never work`;
- `chicken fingers` and `variety`;
- both `$50,000` amounts;
- `$400 million`;
- `$20 billion`;
- `cravable product`, `team`, and `scale`.

If any required phrase is missing or truncated, fix the source boundary/tail and rerender. Never repair missing speech with caption text alone.

- [ ] **Step 4: Manual narrative review**

Watch the final video from start to finish with sound. Reject it unless the sequence reads without external explanation:

```text
rejection → one-product mechanism → funding proof → scale proof → rebuild rule
```

Check that music, SFX, and evidence footage support rather than interrupt Todd's speech.

- [ ] **Step 5: Re-run all affected gates after every fix**

Any timing, caption, audio, or visual change requires fresh unit tests, full render, ffprobe, decode, affected frame review, and final ASR.

---

### Task 8: Document and perform the post-production retro

- [ ] **Step 1: Complete `docs/production/hardknocks-v7-raising-canes-focus-bet.md`**

Include:

- status and source URL/ID;
- exact source windows and verbatim VO;
- final storyboard;
- narrative-beat mapping;
- WEALTHIAN formula mapping;
- Transformative Gate evidence;
- Pexels IDs/URLs/queries/offsets;
- final specs, size, bitrate, and SHA-256;
- all mechanical, visual, and semantic QC evidence;
- known trade-offs;
- 48-hour metrics checklist;
- Post-Production Retro;
- Hook Retro;
- Workflow Delta.

Do not write YouTube title/description unless the user asks separately.

- [ ] **Step 2: Verify repository hygiene**

Run:

```bash
git diff --check
git status --short
```

Confirm source MP4, transcription WAV, work clips, extracted frames, and final MP4 remain ignored by Git while renderer/tests/docs/registry changes are visible.

- [ ] **Step 3: Run final fresh verification**

Run all V7 tests and final artifact gates one last time immediately before reporting completion. Report actual command outputs; do not rely on prior runs.
