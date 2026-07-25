# Ronald Wayne Qwen Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Execution override (2026-07-25):** The user explicitly requested no unit tests. Do not execute the unit-test steps below. Verification was performed against the real ASR, rendered frames, MP4 streams, hashes, full decode, and artifact-level verifier instead.

**Goal:** Produce a separate v3 MP4 whose captions and semantic visual states follow the actual Qwen word timestamps while preserving the v2 audio exactly and retaining forty 1.5-second visual beats.

**Architecture:** A pure `sync_timeline.py` module converts final-MP4 ASR words into a validated forty-beat synchronization manifest. A new v3 renderer consumes that manifest, composites static chrome for each full beat, delays the caption-only raster overlay until its aligned frame, remaps semantically premature cards, and stream-copies the v2 Qwen audio. An independent verifier proves timing invariants, stream identity, ASR recall, decode, format, cadence, and manual contact-sheet evidence.

**Tech Stack:** Python 3.12, pytest, Pillow, FFmpeg/ffprobe 8.1, mlx-whisper, JSON.

---

## File structure

- Create `pipeline/ronaldwayne/sync_timeline.py` — pure word normalization, phrase lookup, frame-safe caption timing, and forty-beat manifest construction.
- Create `tests/ronaldwayne/test_qwen_sync_timeline.py` — regression tests for the reported early-caption bug.
- Create `pipeline/ronaldwayne/render_ronaldwayne_v3_synced.py` — isolated visual renderer and v2-audio stream-copy mux.
- Create `pipeline/ronaldwayne/verify_ronaldwayne_v3_synced.py` — final artifact technical and alignment verifier.
- Generate `output/projects/ronaldwayne/scripts/visual-edl-v3-qwen-synced.json` — resolved timing/visual manifest.
- Generate `output/projects/ronaldwayne/2026-07-25-ronald-wayne-v3-qwen-synced.mp4` — synchronized artifact.
- Generate `output/projects/ronaldwayne/checks-v3-sync/` — ASR, audit, stream hashes, probe data, and contact sheets.
- Update `output/projects/ronaldwayne/PRODUCTION-V2-QWEN.md` with a pointer to v3; do not replace v1/v2 records.

## Task 1: Encode and test the timing contract

**Files:**
- Create: `tests/ronaldwayne/test_qwen_sync_timeline.py`
- Test against: `output/projects/ronaldwayne/checks-v2-qwen/final-asr/final.json`

- [ ] **Step 1: Write failing tests before production code**

Tests must import `pipeline.ronaldwayne.sync_timeline` and assert:

```python
def test_builds_exactly_forty_fixed_beats():
    beats = build_sync_beats(load_asr())
    assert len(beats) == 40
    assert all(b["start"] == i * 1.5 for i, b in enumerate(beats))
    assert all(b["end"] == (i + 1) * 1.5 for i, b in enumerate(beats))


def test_caption_reveal_never_precedes_anchor_word():
    for beat in build_sync_beats(load_asr()):
        assert beat["caption_at"] + 1e-9 >= beat["anchor_start"]
        assert beat["start"] <= beat["caption_at"] < beat["end"]


def test_high_risk_claims_map_to_expected_phrases():
    beats = {b["index"]: b for b in build_sync_beats(load_asr())}
    assert beats[2]["anchor_phrase"] == "eight hundred dollars"
    assert beats[11]["anchor_phrase"] == "personally liable"
    assert beats[33]["anchor_phrase"] == "five hundred dollars"
    assert beats[35]["anchor_phrase"] == "one point five nine million"
    assert beats[36]["anchor_phrase"] == "that i regret"
    assert beats[39]["anchor_phrase"] == "walking away give him freedom"


def test_silent_hold_does_not_introduce_a_new_claim():
    beat = build_sync_beats(load_asr())[25]
    assert beat["mode"] == "hold"
    assert beat["caption"] == "HIS OWN INVENTIONS"
    assert beat["anchor_phrase"] == ""
```

- [ ] **Step 2: Run RED gate**

Run:

`uv run --with pytest pytest tests/ronaldwayne/test_qwen_sync_timeline.py -q`

Expected: collection error because `pipeline.ronaldwayne.sync_timeline` does not exist.

## Task 2: Implement the synchronization manifest

**Files:**
- Create: `pipeline/ronaldwayne/sync_timeline.py`

- [ ] **Step 1: Implement minimal pure functions**

Required API:

```python
def normalize_word(text: str) -> str: ...
def load_words(asr_path: Path) -> list[dict]: ...
def find_phrase_start(words: list[dict], phrase: str) -> float: ...
def ceil_to_frame(seconds: float, fps: int = 30) -> float: ...
def build_sync_beats(asr: dict) -> list[dict]: ...
def write_manifest(asr_path: Path, output_path: Path) -> list[dict]: ...
```

Each normal beat computes:

```python
caption_at = max(beat_start, ceil_to_frame(anchor_start, 30))
```

Beat 25 uses `mode="hold"`, `caption_at=37.5`, and no anchor phrase. Every other beat must fail closed if its phrase is absent or if resolved timing falls outside the beat.

- [ ] **Step 2: Run GREEN gate**

Run the same pytest command. Expected: `4 passed`.

- [ ] **Step 3: Generate and validate manifest**

Run:

`python3 pipeline/ronaldwayne/sync_timeline.py`

Expected: writes exactly forty entries to `visual-edl-v3-qwen-synced.json`, with no caption lead.

## Task 3: Add delayed caption compositing and semantic visual remaps

**Files:**
- Create: `pipeline/ronaldwayne/render_ronaldwayne_v3_synced.py`
- Read: `pipeline/ronaldwayne/render_ronaldwayne_v1.py`
- Read: `output/projects/ronaldwayne/scripts/visual-edl-v3-qwen-synced.json`

- [ ] **Step 1: Add failing renderer contract tests**

Extend the test file to assert:

```python
def test_caption_delay_is_frame_safe():
    for beat in build_sync_beats(load_asr()):
        delay = beat["caption_at"] - beat["start"]
        assert 0 <= delay < 1.5
        assert abs(delay * 30 - round(delay * 30)) < 1e-6


def test_known_visual_mismatches_are_remapped():
    beats = {b["index"]: b for b in build_sync_beats(load_asr())}
    assert beats[13]["visual"] == "young_broke_split"
    assert beats[15]["visual"] == "grouped_assets"
    assert beats[16]["visual"] == "creditor_exposure"
    assert beats[35]["visual"] == "auction_1_59m"
    assert beats[38]["visual"] == "fool_free_split"
```

Run pytest and confirm RED because the visual identifiers/delay contract are incomplete.

- [ ] **Step 2: Implement the minimal renderer**

Use a new work directory `work/v3-qwen-synced` and never reuse v1/v2 beat caches.

Split overlays into:

```python
def chrome_overlay_for(beat, index) -> Path: ...
def caption_overlay_for(beat, index) -> Path: ...
```

Composite the caption-only PNG with:

```text
overlay=0:0:eof_action=repeat:enable='gte(t,<caption_delay>)'
```

Do not use `-loop 1` for overlay inputs. A card background may loop because it is the primary image source.

Apply the mandatory remaps from the approved design and use the v3 manifest caption strings rather than v1 hardcoded captions.

- [ ] **Step 3: Run tests and compile**

Run:

```bash
uv run --with pytest pytest tests/ronaldwayne/test_qwen_sync_timeline.py -q
uv run --with pillow python -m py_compile pipeline/ronaldwayne/render_ronaldwayne_v3_synced.py
```

Expected: all tests pass and compile exits 0.

## Task 4: Render v3 and preserve audio exactly

**Files:**
- Generate: `output/projects/ronaldwayne/2026-07-25-ronald-wayne-v3-qwen-synced.mp4`
- Generate: `output/projects/ronaldwayne/work/v3-qwen-synced/`

- [ ] **Step 1: Render all forty beats from scratch**

Run:

`uv run --with pillow python pipeline/ronaldwayne/render_ronaldwayne_v3_synced.py`

The final mux must map the new video stream and the v2 audio stream with `-c:a copy`.

- [ ] **Step 2: Prove audio identity immediately**

Hash the AAC elementary streams from v2 and v3 with FFmpeg `-f hash -hash sha256`. Expected: exact equality.

- [ ] **Step 3: Verify controls are unchanged**

Expected hashes:

- v1: `66575535235c1a1af9624d46e0afd49f5c259d2515c3abc2520721c585288f20`
- v2: `16445a6a7feac3311421483c9d33ef5e396c037a977ed056679bf62b1c6e1021`

## Task 5: Verify timing and artifact

**Files:**
- Create: `pipeline/ronaldwayne/verify_ronaldwayne_v3_synced.py`
- Generate: `output/projects/ronaldwayne/checks-v3-sync/verification-summary.json`

- [ ] **Step 1: Implement independent verification**

Verify:

- full FFmpeg decode;
- 60.000-second container and both stream durations;
- H.264 1080×1920 at 30fps;
- AAC stereo 48kHz;
- forty keyframes;
- v3 AAC elementary hash equals v2;
- caption timing audit has lead `>= 0` for all anchored beats;
- beat 25 is a hold;
- output contains forty distinct semantic beat records.

- [ ] **Step 2: Run final-MP4 ASR**

Transcribe v3 with `mlx-community/whisper-small.en-mlx` and require 151/151 normalized tokens, matching the v2 script including both Wayne quotes.

- [ ] **Step 3: Generate contact sheets**

Generate:

- full forty-beat sheet at beat midpoint;
- focused sheets for 12–25.5s, 31.5–43.5s, and 43.5–60s;
- regression frames just before and after delayed caption reveals for `$800`, personal liability, `$500`, `$1.59M`, and the final verdict.

- [ ] **Step 4: Manually inspect the real frames**

Confirm the early frame has no premature caption and the post-anchor frame has the correct caption, with readable mobile-safe placement and semantically matching evidence.

## Task 6: Documentation and final verification

**Files:**
- Update: `output/projects/ronaldwayne/PRODUCTION-V2-QWEN.md`
- Create: `docs/production/ronald-wayne-v3-qwen-synced.md`

- [ ] Record artifact checksum, stream hashes, ASR results, alignment audit, contact sheets, unchanged controls, and human-listening caveat.
- [ ] Run `python3 -m py_compile` on all Ronald Wayne pipeline files touched.
- [ ] Run `python3 -m json.tool` on all new JSON artifacts.
- [ ] Run `git diff --check`.
- [ ] Run a final fresh SHA-256, ffprobe, full decode, keyframe count, and AAC identity check immediately before handoff.
- [ ] Do not commit the dirty working tree unless the user explicitly requests commits; preserve unrelated existing changes.
