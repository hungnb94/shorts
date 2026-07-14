# Laundromat Decision-Lock Short Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce and verify a 48–52 second English finance Short that makes the viewer lock a `SMART`/`RECKLESS` decision before progressively revealing the economics of a real laundromat acquisition.

**Architecture:** Follow the repository's existing per-project Python/ffmpeg pattern. A single renderer owns the frame-accurate timeline, source/Pexels extraction, moving-background composites, original-audio placement, decision/cash-flow overlays, captions, final mux, and automated QA. Pure timeline/financial/text-width gates are covered by a small `unittest` module before the full render.

**Tech Stack:** Python 3, ffmpeg/ffprobe, Pillow, yt-dlp, Pexels assets via the `video/pexels-download` skill, stdlib `unittest`.

**Execution note:** Do not commit or upload. The user authorized autonomous production, but repository policy still requires an explicit request before git commits or upload side effects.

---

## File map

- Create `pipeline/laundromat/render_laundromat_v1.py` — source extraction, timeline, overlays, audio, render, QA.
- Create `pipeline/laundromat/test_render_laundromat_v1.py` — pure financial/timeline/text gates.
- Create `output/projects/laundromat/source/Z1YZxX-fBwQ.mp4` — highest format actually available: YouTube format `137+140` (1080p AVC + M4A; source has no 2160p format).
- Create `output/projects/laundromat/source/Z1YZxX-fBwQ.en.json3` and `Z1YZxX-fBwQ.info.json` — timestamp/fact provenance.
- Create `output/projects/laundromat/source/manifest.md` — source and selected timestamp record.
- Create `output/projects/laundromat/scripts/script.md` — frame-accurate narrative/evidence script.
- Create `output/projects/laundromat/final/2026-07-14-laundromat_v1_decision_lock.mp4` — canonical final render.
- Create `output/projects/laundromat/final/2026-07-14-laundromat_v1_decision_lock_metadata.txt` — title and description.
- Create `docs/production/laundromat-v1-decision-lock.md` — production record and Post-Production Retro.
- Modify `data/source_videos.csv` — append source dedup entry after the candidate passes Stage 0.

### Task 1: Acquire source and prove the candidate windows

**Files:**
- Create: `output/projects/laundromat/source/Z1YZxX-fBwQ.mp4`
- Create: `output/projects/laundromat/source/Z1YZxX-fBwQ.en.json3`
- Create: `output/projects/laundromat/source/Z1YZxX-fBwQ.info.json`
- Create: `output/projects/laundromat/source/checks/*.jpg`
- Create: `output/projects/laundromat/source/manifest.md`

- [ ] **Step 1: Create project directories**

Run:

```bash
mkdir -p output/projects/laundromat/{source/checks,clips/v1_work/checks,final,scripts}
```

Expected: all directories exist; no tracked project state is deleted.

- [ ] **Step 2: Download the highest source format actually available**

The source format audit shows a maximum of 1920x1080; 2160p is unavailable. Use exact 1080p AVC + M4A IDs rather than default selection:

```bash
yt-dlp -f "137+140" --merge-output-format mp4 \
  --write-auto-subs --sub-langs en --sub-format json3 \
  --write-info-json \
  -o "output/projects/laundromat/source/%(id)s.%(ext)s" \
  "https://www.youtube.com/watch?v=Z1YZxX-fBwQ"
```

Expected: `Z1YZxX-fBwQ.mp4` is 1920x1080 with audio; JSON3 and info JSON exist.

- [ ] **Step 3: Extract Stage-0 candidate frames**

Run:

```bash
for t in 18.08 148.80 177.12 198.47 236.08 438.80; do
  ffmpeg -hide_banner -loglevel error -y -ss "$t" \
    -i output/projects/laundromat/source/Z1YZxX-fBwQ.mp4 \
    -frames:v 1 -q:v 2 "output/projects/laundromat/source/checks/frame-${t}.jpg"
done
```

Expected: six readable images. Manually select a frame-0 window containing Cami's face/action. If `177.12` is not a strong face shot, use `148.80` or a nearby talking-head onset and keep the exact `177.12` audio as a separately placed source quote.

- [ ] **Step 4: Verify direct-audio evidence windows**

Use these source ranges, each below 15 seconds:

```text
BET_A      177.12–189.60  sold home, $150K equity toward down payment
FINANCE_B  198.47–202.32  remaining $100K seller-financed at 6%
REVENUE    18.08–20.60    $475K in 2024
OWNER_PAY  438.80–442.80  paid herself $66K in 2024
HOURS_A    236.08–245.92  five to six hours now, explicitly not true five years ago
HOURS_B    250.48–254.56  employees and systems remove her from operations
```

Extract each as 16kHz mono WAV and reject `max_volume <= -40 dB` before proceeding.

- [ ] **Step 5: Write the source manifest and append the registry**

The manifest must record the source URL, format IDs, max available resolution, source facts, selected ranges, and the distinction between spoken facts and the official-description-only `$119K profit` figure.

Append exactly one CSV row:

```csv
Z1YZxX-fBwQ,"I Quit My Nursing Job For My Laundromat Business – It Brings In $475K/Year",CNBC Make It,finance,2026-07-14,laundromat,"laundromat_v1 Decision-Lock Narrative; $300K acquisition vs $475K revenue/$119K profit/$66K owner pay; Multi-Clip Mashup"
```

Run:

```bash
python3 - <<'PY'
from pathlib import Path
p = Path('data/source_videos.csv')
text = p.read_text()
assert 'Z1YZxX-fBwQ' not in text
row = 'Z1YZxX-fBwQ,"I Quit My Nursing Job For My Laundromat Business – It Brings In $475K/Year",CNBC Make It,finance,2026-07-14,laundromat,"laundromat_v1 Decision-Lock Narrative; $300K acquisition vs $475K revenue/$119K profit/$66K owner pay; Multi-Clip Mashup"\n'
p.write_text(text.rstrip('\n') + '\n' + row)
PY
```

Expected: one and only one `Z1YZxX-fBwQ` row.

### Task 2: Lock pure data and validation behavior with tests

**Files:**
- Create: `pipeline/laundromat/test_render_laundromat_v1.py`
- Create: `pipeline/laundromat/render_laundromat_v1.py`

- [ ] **Step 1: Write failing tests**

Create the test module with:

```python
import unittest

from render_laundromat_v1 import (
    Financials,
    TimelineClip,
    financial_summary,
    source_share,
    validate_timeline,
)


class LaundromatRendererTests(unittest.TestCase):
    def test_financial_summary_uses_grounded_numbers(self):
        values = financial_summary(Financials())
        self.assertEqual(values["purchase_price"], 300_000)
        self.assertEqual(values["cash_at_risk"], 200_000)
        self.assertEqual(values["profit"], 119_000)
        self.assertEqual(values["owner_pay"], 66_000)
        self.assertAlmostEqual(values["profit_margin"], 119_000 / 475_000)

    def test_source_share_is_frame_accurate(self):
        clips = [
            TimelineClip("source", 0, 300, True),
            TimelineClip("pexels", 300, 900, False),
            TimelineClip("source", 900, 1200, True),
            TimelineClip("pexels", 1200, 1500, False),
        ]
        self.assertEqual(source_share(clips), 0.4)

    def test_timeline_rejects_source_share_above_half(self):
        clips = [
            TimelineClip("source", 0, 800, True),
            TimelineClip("pexels", 800, 1500, False),
        ]
        with self.assertRaisesRegex(ValueError, "source share"):
            validate_timeline(clips, total_frames=1500)

    def test_timeline_rejects_gaps(self):
        clips = [
            TimelineClip("a", 0, 300, True),
            TimelineClip("b", 301, 1500, False),
        ]
        with self.assertRaisesRegex(ValueError, "gap or overlap"):
            validate_timeline(clips, total_frames=1500)

    def test_timeline_rejects_source_clip_at_or_above_15_seconds(self):
        clips = [
            TimelineClip("source", 0, 450, True),
            TimelineClip("pexels", 450, 1500, False),
        ]
        with self.assertRaisesRegex(ValueError, "15 seconds"):
            validate_timeline(clips, total_frames=1500)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
cd pipeline/laundromat && python3 -m unittest -v test_render_laundromat_v1.py
```

Expected: import failure because the renderer module does not exist yet.

- [ ] **Step 3: Implement the pure model and gates**

Start `render_laundromat_v1.py` with:

```python
from dataclasses import asdict, dataclass

FPS = 30


@dataclass(frozen=True)
class Financials:
    home_sale: int = 310_000
    home_equity: int = 150_000
    savings: int = 50_000
    seller_financing: int = 100_000
    purchase_price: int = 300_000
    revenue: int = 475_000
    profit: int = 119_000
    owner_pay: int = 66_000
    owner_hours_low: int = 5
    owner_hours_high: int = 6
    employees: int = 6


@dataclass(frozen=True)
class TimelineClip:
    name: str
    start_frame: int
    end_frame: int
    is_source_footage: bool

    @property
    def frames(self) -> int:
        return self.end_frame - self.start_frame


def financial_summary(values: Financials) -> dict[str, float | int]:
    result = asdict(values)
    result["cash_at_risk"] = values.home_equity + values.savings
    result["profit_margin"] = values.profit / values.revenue
    return result


def source_share(clips: list[TimelineClip]) -> float:
    total = sum(clip.frames for clip in clips)
    source = sum(clip.frames for clip in clips if clip.is_source_footage)
    if total <= 0:
        raise ValueError("timeline has no frames")
    return source / total


def validate_timeline(clips: list[TimelineClip], total_frames: int) -> None:
    if not clips or clips[0].start_frame != 0 or clips[-1].end_frame != total_frames:
        raise ValueError("timeline does not cover the complete output")
    for left, right in zip(clips, clips[1:]):
        if left.end_frame != right.start_frame:
            raise ValueError("timeline gap or overlap")
    for clip in clips:
        if clip.frames <= 0:
            raise ValueError(f"non-positive clip: {clip.name}")
        if clip.is_source_footage and clip.frames >= 15 * FPS:
            raise ValueError(f"source clip reaches 15 seconds: {clip.name}")
    if source_share(clips) > 0.50:
        raise ValueError("source share exceeds 50 percent")
```

- [ ] **Step 4: Run tests and verify GREEN**

Run:

```bash
cd pipeline/laundromat && python3 -m unittest -v test_render_laundromat_v1.py
```

Expected: five tests pass.

### Task 3: Acquire three Pexels b-roll assets through the established skill

**Files:**
- Create: Pexels files selected by the skill, then copy/link them under `output/projects/laundromat/source/pexels/`

- [ ] **Step 1: Load and follow `video/pexels-download`**

Do not write a custom downloader and do not pass the API key as an argument. Search/download these concepts:

```text
laundromat washing machines close up
house keys hand close up
counting cash hands close up
```

- [ ] **Step 2: Verify each asset**

For every selected file, run ffprobe and retain only assets with a real video stream, duration at least four seconds, and resolution sufficient for a Lanczos 1080x1920 hard crop. Record Pexels page/video IDs in `source/manifest.md`.

### Task 4: Implement the frame-accurate Decision-Lock renderer

**Files:**
- Modify: `pipeline/laundromat/render_laundromat_v1.py`
- Create: `output/projects/laundromat/scripts/script.md`

- [ ] **Step 1: Encode the timeline as data**

Use `TOTAL_FRAMES = 1500` (50.0 seconds) and these contiguous sections:

```python
TIMELINE = [
    TimelineClip("hook_owner", 0, 84, True),
    TimelineClip("bet_owner", 84, 165, True),
    TimelineClip("bet_keys", 165, 225, False),
    TimelineClip("price_ledger", 225, 345, False),
    TimelineClip("revenue", 345, 510, True),
    TimelineClip("profit_waterfall", 510, 690, False),
    TimelineClip("owner_pay", 690, 885, True),
    TimelineClip("hours_now", 885, 1065, True),
    TimelineClip("systems", 1065, 1155, False),
    TimelineClip("verdict", 1155, 1380, False),
    TimelineClip("semantic_loop", 1380, 1500, False),
]
```

This timeline uses 705 source frames out of 1,500 (47.0%). `bet_keys` keeps the source quote audible while replacing its visuals with moving keys/home-sale b-roll. Call `validate_timeline(TIMELINE, TOTAL_FRAMES)` before any extraction and do not weaken the validator.

- [ ] **Step 2: Implement moving visual backgrounds**

Implement three render paths:

```text
render_source_visual()  -> hard crop with tracked x-position, source badge, no pillarbox
render_pexels_visual()  -> hard crop with Lanczos, max 1.035x slow zoom
render_composite()      -> moving background plus partial decision/ledger/waterfall overlays
```

Every extraction must normalize to H.264 High, yuv420p, 1080x1920, 30fps, CRF 15, AAC 48kHz stereo so concat is deterministic.

- [ ] **Step 3: Implement the persistent decision meter**

The meter has two states plus an unresolved center:

```python
DECISION_STATES = [
    (0, 45, "UNRESOLVED"),
    (45, 510, "SMART_LEAN"),
    (510, 690, "CENTER"),
    (690, 1155, "SMART_QUALIFIED"),
    (1155, 1500, "VERDICT"),
]
```

The meter must remain partial-screen, avoid faces/source captions, and animate state changes rather than cutting to a full-screen card.

- [ ] **Step 4: Implement captions and evidence labels**

Render these hook bursts by frame:

```text
0–24     SHE SOLD HER HOUSE
24–51    TO BUY THIS.
51–84    SMART OR RECKLESS?
45–84    LOCK YOUR ANSWER
```

Evidence labels:

```text
$200K CASH AT RISK
$100K SELLER FINANCING • 6%
$300K PURCHASE PRICE
$475K REVENUE
$119K PROFIT • 25% MARGIN
$66K OWNER PAY
5–6 HRS/WEEK NOW
AFTER ~5 YEARS + 6 EMPLOYEES
SMART — BUT NOT BECAUSE OF REVENUE
CHECK PRICE • OWNER PAY • OWNER HOURS
```

Use `expansion=none` for all ffmpeg drawtext values containing `%`. Measure every rendered line with `ImageFont.getlength()` against a 920px maximum before invoking ffmpeg.

- [ ] **Step 5: Build the original-audio timeline**

Extract the six approved source WAVs with input-side `-ss`, `asetpts=PTS-STARTPTS`, bounded fades, and -16 LUFS line normalization. Place them at the corresponding narrative beats with `adelay`; preserve natural speed and pad silence rather than slowing speech.

Use a generated low-energy instrumental bed only if it improves continuity. Duck it to 3–5% under source voice. Add restrained impact sounds at the initial decision lock, `$475K`, `$119K`, and verdict only.

- [ ] **Step 6: Write `script.md` from the actual frame data**

The script must list every section's final frame range, source timestamp/audio quote, visual source, commentary text, citation, and Transformative Gate accounting. Values must come from the renderer constants rather than a divergent prose draft.

### Task 5: Render, inspect, and fix the real artifact

**Files:**
- Create: `output/projects/laundromat/final/2026-07-14-laundromat_v1_decision_lock.mp4`
- Create: `output/projects/laundromat/clips/v1_work/checks/*`

- [ ] **Step 1: Run tests and syntax checks**

```bash
python3 -m py_compile pipeline/laundromat/render_laundromat_v1.py
cd pipeline/laundromat && python3 -m unittest -v test_render_laundromat_v1.py
```

Expected: syntax check succeeds and all tests pass.

- [ ] **Step 2: Render**

```bash
python3 pipeline/laundromat/render_laundromat_v1.py
```

Expected: renderer exits zero and prints the final duration, frame count, source-share percentage, codecs, loudness, and check-image paths.

- [ ] **Step 3: Verify the media contract**

Reject unless all are true:

```text
1080x1920
H.264 High / yuv420p
AAC 48kHz stereo
30fps
48–52 seconds and <=60 seconds
one video stream + one audio stream
all source clips <15 seconds
source visual share <=50%
full decode succeeds
integrated loudness near -14 LUFS
true peak <= -0.5 dBTP
```

- [ ] **Step 4: Perform mandatory manual visual QA**

Extract hook frames at `0.0, 0.2, 0.6, 1.0, 1.5, 2.0, 2.8, 4.0, 5.0` and arc frames every four seconds. Inspect directly and fix any of:

```text
frame 0 lacks a large human face/action
caption absent after 0.2s
face covered by meter
copy clipped at an edge
decision meter disappears or changes incoherently
full-screen static card lasts >0.8s
source/Pexels crop looks stretched
$119K appears as a spoken quote instead of CNBC-reported data
5–6 hours/week is shown without the five-year/employees qualification
```

Re-render after every visual correction; do not infer safety from code alone.

- [ ] **Step 5: Perform audio QA**

Check every source-quote window with `volumedetect`, transcribe the final mix, and listen to the hook plus all hard cuts. Reject silent windows, guillotined words, doubled voices, or a music bed that masks speech.

### Task 6: Metadata, production record, and final repository checks

**Files:**
- Create: `output/projects/laundromat/final/2026-07-14-laundromat_v1_decision_lock_metadata.txt`
- Create: `docs/production/laundromat-v1-decision-lock.md`
- Modify: `docs/experiments/EXPERIMENT-LOG.md` only after an upload exists; do not add a fake video ID now.

- [ ] **Step 1: Write upload metadata**

Use this exact title:

```text
She Sold Her House For This. Smart Or Reckless?
```

The description must cite the specific source URL, distinguish revenue/profit/owner-pay figures, state that five to six hours per week is the current state after building a team/systems, and include no raw affiliate link.

- [ ] **Step 2: Write the production document**

Include Status, specs, hash, source, exact cuts, Why This Segment, Decision-Lock formula, value-adds, Transformative Gate, automated verification, manual visual verification, known issues, 48h metrics checklist, and both required Post-Production Retro subsections.

- [ ] **Step 3: Final verification**

Run:

```bash
python3 -m py_compile pipeline/laundromat/render_laundromat_v1.py
git diff --check
git status --short
```

Expected: no syntax or whitespace errors. Report changed/untracked files without committing or uploading.
