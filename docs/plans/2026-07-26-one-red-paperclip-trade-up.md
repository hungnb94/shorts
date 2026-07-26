# One Red Paperclip Trade-Up Short Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce and verify a 58–65 second English MONEY BLINDSPOT Short that turns Kyle MacDonald's fourteen documented trades into a visible paperclip-to-house challenge.

**Architecture:** Keep evidence, narration, timeline, rendering and verification separate. The renderer consumes immutable JSON manifests and verified local media; a dedicated 0–3s hook prototype must pass the repository's human Hook Gate before the full renderer is allowed to run. The final edit combines short primary-source excerpts, licensable moving object footage and a persistent animated trade ladder.

**Tech Stack:** Python 3.12, ffmpeg/ffprobe 8.x, ephemeral Pillow via `uv`, MLX Whisper, Qwen3-TTS through `.venv-mlx`, yt-dlp and Mixkit `videoFree` stock.

**Execution note:** Do not create renderer unit tests. The user prefers verification against real media artifacts and runtime output. Use compile checks, full decode, ASR, waveform measurements, frame/contact-sheet inspection, hashes and human viewing/listening evidence.

---

## File Map

### Create

- `docs/research/one-red-paperclip-2026-07-26/REPORT.md` — demand, source and MrBeast/trade-up findings.
- `docs/research/one-red-paperclip-2026-07-26/CLAIM-LEDGER.md` — claim-level source status and guardrails.
- `output/projects/paperclip/source/source-metadata.json` — yt-dlp metadata snapshot for retained video sources.
- `output/projects/paperclip/source/8s3bdVxuFBs.mp4` — Kyle's TEDxVienna source.
- `output/projects/paperclip/source/BE8b02EdZvw.mp4` — ABC 20/20 archive candidate; rights-blocked unless reviewed.
- `output/projects/paperclip/source/8s3bdVxuFBs-transcript.json` — local word-timestamped ASR.
- `output/projects/paperclip/scripts/trade-chain.json` — the fourteen canonical trade nodes.
- `output/projects/paperclip/scripts/source-ledger.json` — immutable source windows, use percentages, labels and rights state.
- `output/projects/paperclip/scripts/narration.json` — exact Qwen lines and intended semantic windows.
- `output/projects/paperclip/scripts/visual-edl-v1.json` — final frame-based visual/caption/audio manifest.
- `pipeline/paperclip/generate_paperclip_narration.py` — deterministic Qwen narration generation and duration/ASR report.
- `pipeline/paperclip/render_paperclip_hook_v1.py` — 0–3s Stage-0 prototype only.
- `pipeline/paperclip/render_paperclip_v1.py` — full artifact renderer, fail-closed on Hook Gate evidence.
- `pipeline/paperclip/generate_paperclip_qc.py` — hook, arc, source, CTA, payoff and caption-reveal contact sheets.
- `pipeline/paperclip/verify_paperclip_v1.py` — final media/ASR/source-use/QC verifier.
- `docs/production/one-red-paperclip-v1.md` — source map, artifact evidence, upload package and retro.

### Modify

- `data/source_videos.csv` — register each selected source video ID once selection is locked.
- `docs/README.md` — add the final production record to the index.
- `docs/WORKFLOW.md` — modify only if the post-production retro finds a general workflow gap not already covered.

### Immutable controls

- `docs/specs/2026-07-26-one-red-paperclip-trade-up-design.md`
- public Ronald Wayne upload `2S1gkUQ5iRo` and its local v1/v2/v3 artifacts.

---

### Task 1: Freeze the Research, Claims and Source Rights State

**Files:**
- Create: `docs/research/one-red-paperclip-2026-07-26/REPORT.md`
- Create: `docs/research/one-red-paperclip-2026-07-26/CLAIM-LEDGER.md`
- Create: `output/projects/paperclip/source/source-metadata.json`
- Modify: `data/source_videos.csv`

- [ ] **Step 1: Record public demand and failure context**

Record the dated evidence already collected:

```text
Ronald Wayne public upload: https://youtube.com/shorts/2S1gkUQ5iRo
Snapshot: 28 views at 15.77 hours after publication
Diagnostic limit: no Studio Shown in feed, Stayed to watch or AVD
Nas Daily paperclip execution: 44DtSp4ZNB0, approximately 4.18M public views
Ryan Trahan trade-up execution: Ge96ORjwsic, approximately 8.00M public views
Kyle TEDx source: 8s3bdVxuFBs, approximately 12.74M public views
```

Separate observed mechanics from causal claims: measurable goal, real prop, persistent progress and physical payoff are transferable; channel scale and audience history are confounders.

- [ ] **Step 2: Create the claim ledger**

Use this exact state model:

```markdown
| Claim | Status | Safe wording | Primary/near-primary source | Production rule |
|---|---|---|---|---|
| Kyle started with one red paperclip in July 2005 | CONFIRMED | "In 2005, Kyle started with one red paperclip." | Kyle official blog | retain |
| The chain contained fourteen trades | CONFIRMED | "Fourteen trades." | Kyle official blog; CBC | retain |
| The final exchange occurred in July 2006 | CONFIRMED | "One year later" | Kyle official blog; CBC | retain |
| Every trade was objectively worth more | UNSUPPORTED | never say this | none | block |
| The town of Kipling exchanged a house for the movie-role asset | CONFIRMED | "Kipling traded a house for the movie role." | CBC; Kyle official blog | retain |
| Intermediate dollar values | UNRESOLVED/UNNEEDED | do not state values | none required | omit |
```

Sources:

```text
https://oneredpaperclip.blogspot.com/
https://www.cbc.ca/news/canada/from-paper-clip-to-house-in-14-trades-1.573973
```

- [ ] **Step 3: Capture source metadata without claiming a license**

Run:

```bash
mkdir -p output/projects/paperclip/source
python3 -m yt_dlp --skip-download --dump-single-json --no-warnings \
  'https://www.youtube.com/watch?v=8s3bdVxuFBs' > /tmp/tedx.json
python3 -m yt_dlp --skip-download --dump-single-json --no-warnings \
  'https://www.youtube.com/watch?v=BE8b02EdZvw' > /tmp/abc.json
python3 - <<'PY'
import json
from pathlib import Path
keys = ['id','title','channel','channel_id','duration','upload_date','view_count','license','availability','resolution','webpage_url']
rows=[]
for name in ['/tmp/tedx.json','/tmp/abc.json']:
    d=json.loads(Path(name).read_text())
    rows.append({k:d.get(k) for k in keys})
out=Path('output/projects/paperclip/source/source-metadata.json')
out.write_text(json.dumps({'snapshot_date':'2026-07-26','sources':rows},indent=2)+'\n')
print(out)
PY
```

Expected: both sources are public; `license` is null/undeclared. Mark commercial publication `BLOCKED — publisher/rights review required`; do not translate public availability into permission.

- [ ] **Step 4: Append selected IDs to the dedup registry**

Append one row for each source actually retained by the final edit. Do not register ABC if the renderer ultimately excludes it. Preserve CSV schema and quote titles with commas.

- [ ] **Step 5: Verify research package**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
for p in [
 Path('docs/research/one-red-paperclip-2026-07-26/REPORT.md'),
 Path('docs/research/one-red-paperclip-2026-07-26/CLAIM-LEDGER.md'),
 Path('output/projects/paperclip/source/source-metadata.json'),
]:
 assert p.is_file() and p.stat().st_size > 500, p
print('research package: PASS')
PY
```

Expected: `research package: PASS`.

- [ ] **Step 6: Commit research records**

```bash
git add docs/research/one-red-paperclip-2026-07-26 data/source_videos.csv
git commit -m "docs: research one red paperclip story"
```

Do not add downloaded video binaries to Git.

---

### Task 2: Acquire, Decode and Transcribe the Selected Source

**Files:**
- Create: `output/projects/paperclip/source/8s3bdVxuFBs.mp4`
- Create conditionally: `output/projects/paperclip/source/BE8b02EdZvw.mp4`
- Create: `output/projects/paperclip/source/8s3bdVxuFBs-transcript.json`
- Create: `output/projects/paperclip/scripts/source-ledger.json`

- [ ] **Step 1: Download the highest usable rendition**

Try the adaptive 1080p route first:

```bash
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 -m yt_dlp \
  --js-runtimes node --extractor-args 'youtube:player_client=android_vr' \
  -f 'bv*[height<=1080]+ba/b[height<=1080]' --merge-output-format mp4 \
  -o 'output/projects/paperclip/source/%(id)s.%(ext)s' \
  'https://www.youtube.com/watch?v=8s3bdVxuFBs'
```

If YouTube rejects the adaptive stream with bot/403 status, use the verified progressive Android-client route rather than a fabricated or truncated asset:

```bash
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 -m yt_dlp \
  --extractor-args 'youtube:player_client=android' -f 18 \
  -o 'output/projects/paperclip/source/%(id)s.%(ext)s' \
  'https://www.youtube.com/watch?v=8s3bdVxuFBs'
```

The 360p fallback may appear only as a framed source insert, never as an upscaled full-screen proof image. Use 1080p Pexels/action footage for full-frame visuals.

- [ ] **Step 2: Probe, hash and fully decode**

```bash
ffprobe -v error -show_streams -show_format -of json \
  output/projects/paperclip/source/8s3bdVxuFBs.mp4 \
  > output/projects/paperclip/source/8s3bdVxuFBs-probe.json
shasum -a 256 output/projects/paperclip/source/8s3bdVxuFBs.mp4 \
  > output/projects/paperclip/source/8s3bdVxuFBs.sha256
ffmpeg -v error -i output/projects/paperclip/source/8s3bdVxuFBs.mp4 -f null -
```

Expected: full decode exits 0.

- [ ] **Step 3: Generate local word-timestamped ASR**

```bash
/usr/bin/python3 pipeline/tools/transcribe.py \
  --model mlx-community/whisper-large-v3-turbo --language en \
  output/projects/paperclip/source/8s3bdVxuFBs.mp4 \
  output/projects/paperclip/source/8s3bdVxuFBs-transcript.json
```

Expected: JSON contains non-empty `segments` and per-word timestamps.

- [ ] **Step 4: Lock source windows by spoken phrase and frame content**

Select source windows only where both word-timestamp match and frame inspection agree. Candidate semantic targets:

```text
Kyle names or displays the red paperclip.
Kyle states the goal of trading for a house.
Kyle explains the snow-globe-to-movie-role mechanism.
Kyle/archival footage shows the final house or key handoff.
```

Every retained excerpt must be below 15 seconds. For each candidate, extract start/mid/end frames and reject wrong speaker, slide-only frames, obstructive TEDx captions or source-caption bleed.

- [ ] **Step 5: Write the immutable source ledger**

Use this typed schema; populate every field from the metadata snapshot and the
local ASR/frame inspection rather than copying example values:

```python
from typing import Literal, TypedDict

class SourceClip(TypedDict):
    name: str
    start: float
    end: float
    spoken_text: str
    visual_owner: str
    label: str

class SourceEntry(TypedDict):
    id: str
    publisher: str
    license_exposed: str | None
    rights_state: Literal["CLEARED", "BLOCKED_PENDING_REVIEW"]
    clips: list[SourceClip]

class SourceLedger(TypedDict):
    schema_version: int
    sources: list[SourceEntry]
```

Reject an entry if `spoken_text` is empty or if a boundary was not derived from
the local ASR and confirmed against extracted source frames.

- [ ] **Step 6: Verify source-use limits**

Run a script that asserts each `end - start < 15.0`, all windows lie inside the probed source duration and the sum of source windows remains below 50% of both the source duration and target final runtime.

Expected: `source ledger: PASS`.

---

### Task 3: Build the Canonical Trade and Narration Manifests

**Files:**
- Create: `output/projects/paperclip/scripts/trade-chain.json`
- Create: `output/projects/paperclip/scripts/narration.json`
- Create: `pipeline/paperclip/generate_paperclip_narration.py`

- [ ] **Step 1: Encode the fourteen trade nodes**

Use exactly this ordered list:

```json
[
  [1, "red paperclip", "fish-shaped pen"],
  [2, "fish-shaped pen", "handmade doorknob"],
  [3, "handmade doorknob", "camp stove"],
  [4, "camp stove", "generator"],
  [5, "generator", "instant party package"],
  [6, "instant party package", "snowmobile"],
  [7, "snowmobile", "trip to Yahk"],
  [8, "second trip spot", "box truck"],
  [9, "box truck", "recording contract"],
  [10, "recording contract", "one year's rent in Phoenix"],
  [11, "one year's rent", "afternoon with Alice Cooper"],
  [12, "Alice Cooper meeting", "KISS snow globe"],
  [13, "KISS snow globe", "Corbin Bernsen movie role"],
  [14, "movie role", "house in Kipling, Saskatchewan"]
]
```

Include source citations and `claim_status: CONFIRMED` on every node.

- [ ] **Step 2: Lock exact narration lines**

Use this initial script; shorten only if natural synthesis exceeds 65 seconds:

```text
hook: Can this paperclip buy that house?
setup: In 2005, Kyle MacDonald set one rule: trade up until somebody offered him a home.
early: The clip became a fish pen. The pen became a doorknob. Then a stove. A generator. An instant party. And a snowmobile.
middle: He traded the snowmobile for a trip, one seat for a truck, the truck for a recording contract, and that contract for a year of rent.
strange: Then the rent bought an afternoon with Alice Cooper. That became a KISS snow globe.
mechanism: Actor Corbin Bernsen collected snow globes, so he traded Kyle a movie role.
cta: Would you keep trading? Like, subscribe, and comment before the final swap.
payoff: Kipling, Saskatchewan wanted that role. The town traded Kyle a house.
close: Fourteen trades. One year. The paperclip did not grow in value by itself. Kyle kept finding one person who wanted the next offer more.
```

Do not add intermediate dollar values, a current house value or an objective-worth claim.

- [ ] **Step 3: Implement deterministic narration generation**

`generate_paperclip_narration.py` must:

```python
def load_manifest(path: Path) -> dict: ...
def synthesize_line(line_id: str, text: str, output: Path, seed: int) -> dict: ...
def normalize_and_measure(raw: Path, final: Path) -> dict: ...
def transcribe_preview(preview: Path) -> dict: ...
def normalized_tokens(text: str) -> list[str]: ...
def main() -> None: ...
```

Use the user-selected `ronald_wayne_zack_style_qwen` profile inside `.venv-mlx`, incrementing the profile seed deterministically by manifest order. Preserve the earlier `natural_talker_male_qwen_blog` render as an immutable control. Generate the selected voice into `output/projects/paperclip/tts-qwen-zack/`, normalize to 48kHz stereo, transcribe fitted audio and write `generation-report.json` with raw/final duration, seed, tempo, hashes and truncation state for every line. Commercial publication remains blocked pending source-creator consent/licensing.

- [ ] **Step 4: Run the spoken-TTS preflight**

```bash
.venv-mlx/bin/python pipeline/paperclip/generate_paperclip_narration.py
```

Expected:

```text
10/10 narration lines generated
10/10 intended line token sets recovered by ASR
truncated lines: 0
```

If total natural narration cannot fit the visual target, shorten copy in this order: `close`, `middle`, `setup`. Do not hard-trim a phoneme or slow audio below natural speed.

- [ ] **Step 5: Listen manually to the narrator preview**

Reject mispronounced `Yahk`, `Kipling`, `Saskatchewan`, `Bernsen`, `Alice Cooper` or unnatural laughter/prosody. Regenerate the smallest affected line with a documented seed change; do not regenerate accepted lines.

- [ ] **Step 6: Commit manifest and generator**

```bash
git add pipeline/paperclip output/projects/paperclip/scripts/trade-chain.json output/projects/paperclip/scripts/narration.json
git commit -m "feat: add paperclip narration and trade manifests"
```

---

### Task 4: Acquire and Verify Moving Object Footage

**Files:**
- Create: `output/projects/paperclip/source/stock/stock-ledger.json`
- Create: selected licensable MP4 assets under `output/projects/paperclip/source/stock/`

- [ ] **Step 1: Search a machine-verifiable stock catalog**

Use the Pexels API when `PEXELS_API_KEY` is present. If it is absent, use Mixkit
public catalog pages and retain only item pages whose machine-readable
`data-license` equals `videoFree`. Do not retain `videoRestricted` items. Query
for:

```text
red paperclip hand macro
hand exchange object
camp stove flame
portable generator
snowmobile moving
box truck road
recording studio contract
house keys handover
house exterior vertical
```

Store only fields needed for provenance: provider, item ID, page URL, title or
creator, dimensions, duration, selected file URL, exposed license class and
license URL. Never print or persist an API key.

- [ ] **Step 2: Select footage by semantic action**

The frame-zero asset must contain visible hand/prop movement. Reject clips with logos, unsafe behavior, watermarks, wrong object identity, static composition or a focal object too small for a 9:16 mobile crop.

- [ ] **Step 3: Download the highest useful rendition**

Prefer vertical files at or above 1080 pixels wide. If only landscape exists,
require a clean portrait crop around the moving object. A 720p Mixkit
`videoFree` item is acceptable for a partial/split-screen action layer, not for
an archival-proof claim.

- [ ] **Step 4: Fully decode and inspect every asset**

For each selected file:

```bash
for asset in output/projects/paperclip/source/stock/*.mp4; do
  ffprobe -v error -show_streams -show_format -of json "$asset" \
    > "${asset%.mp4}.probe.json"
  ffmpeg -v error -i "$asset" -f null -
done
```

Extract start/mid/end frames, create a stock contact sheet and inspect brand/OCR
contamination manually.

- [ ] **Step 5: Write the stock ledger**

Each asset entry follows this schema:

```python
from typing import Literal, TypedDict

class StockAsset(TypedDict):
    provider: Literal["Pexels", "Mixkit"]
    asset_id: str
    query: str
    page_url: str
    title_or_creator: str
    license_name: str
    license_url: str
    local_path: str
    classification: Literal["ILLUSTRATION"]
    approved_start: float
    approved_end: float
    manual_qc: Literal["PASS"]
```

Reject an entry when the page URL, license class, license URL, local file, exact
approved window or manual start/mid/end review evidence is missing.

---

### Task 5: Build and Pass the 0–3s Human Hook Gate

**Files:**
- Create: `pipeline/paperclip/render_paperclip_hook_v1.py`
- Create: `output/projects/paperclip/hook/one-red-paperclip-hook-v1.mp4`
- Create: `output/projects/paperclip/checks-v1/hook-gate.md`

- [ ] **Step 1: Implement the prototype renderer**

The renderer must use the actual selected frame-zero licensable stock asset, the
generated hook WAV and final caption font/treatment. Output exactly 90 frames at
30fps, 1080×1920, H.264/yuv420p with AAC 48kHz stereo.

Required timeline:

```text
0.000–0.200s: hand and red paperclip already moving; metallic click begins
0.100–1.250s: CAN THIS PAPERCLIP
1.250–2.350s: BUY THAT HOUSE?
2.000–3.000s: house/key target grows while paperclip remains visible
```

- [ ] **Step 2: Render and mechanically verify**

```bash
python3 pipeline/paperclip/render_paperclip_hook_v1.py
ffprobe -v error -show_streams -show_format -of json \
  output/projects/paperclip/hook/one-red-paperclip-hook-v1.mp4
ffmpeg -v error -i output/projects/paperclip/hook/one-red-paperclip-hook-v1.mp4 -f null -
```

Extract frames at `0.0, 0.2, 0.5, 1.0, 2.0, 3.0` seconds and inspect full resolution plus a 270×480 mobile preview.

- [ ] **Step 3: Verify hook audio and ASR**

Transcribe the rough hook and confirm the exact complete question survives. Measure the first second waveform and confirm the event-bound SFX is present but does not mask `Can`.

- [ ] **Step 4: Run the human naive-viewer check**

Show only the 3-second MP4 to a real person who has not participated in the project. Do not show title, design or trade list. Record anonymized verbatim answers to:

```text
What is happening?
What question or stake do you expect the video to answer?
Would you keep watching? Why or why not?
```

Pass condition: the person identifies a paperclip-to-house challenge and wants to know whether/how the trade succeeds. Agent/model self-review does not count.

- [ ] **Step 5: Fail closed**

`render_paperclip_v1.py` must refuse to run unless `hook-gate.md` contains `Result: PASS`, a check date, rough-hook hash and three non-empty verbatim answers.

- [ ] **Step 6: Commit the hook renderer and gate record**

```bash
git add pipeline/paperclip/render_paperclip_hook_v1.py output/projects/paperclip/checks-v1/hook-gate.md
git commit -m "feat: pass paperclip hook gate"
```

Do not add the MP4 binary to Git.

---

### Task 6: Build the Frame-Based Visual EDL and Full Renderer

**Files:**
- Create: `output/projects/paperclip/scripts/visual-edl-v1.json`
- Create: `pipeline/paperclip/render_paperclip_v1.py`
- Create: `output/projects/paperclip/final/2026-07-26-one-red-paperclip-v1.mp4`

- [ ] **Step 1: Generate the frame-based EDL**

The manifest must encode each beat as integer `start_frame`/`end_frame`, semantic state, trade-node IDs, visual asset/window, caption bursts, source label, narration line and SFX event. Do not use a metronomic fixed 1.5-second grid.

Required final phases:

```text
0–6s: object, target, rule
6–20s: trades 1–4
20–38s: trades 5–10
38–42s: integrated CTA over moving trade action
42–58s: trades 11–14 and house payoff
58–65s: collapsed fourteen-node path and loop closure
```

- [ ] **Step 2: Reuse only verified renderer patterns**

Adapt from `pipeline/hardknocks/render_hardknocks_v13_billionaire_hunt.py`:

```python
@dataclass(frozen=True)
class VisualBeat:
    name: str
    start_frame: int
    end_frame: int
    visual_type: str
    asset: Path
    source_start: float
    caption_events: tuple[CaptionEvent, ...]

def render_visual_beat(beat: VisualBeat, output: Path) -> None: ...
def write_ass(edl: list[VisualBeat], narration_words: dict) -> Path: ...
def build_timed_audio(edl: list[VisualBeat]) -> Path: ...
def build_trade_ladder(edl: list[VisualBeat]) -> list[Path]: ...
def final_composite(...) -> Path: ...
def validate_local(output: Path) -> dict: ...
```

Keep each third-party source clip below 15 seconds. Use accurate preroll + exact trim + `setpts=PTS-STARTPTS` for non-keyframe archival windows.

- [ ] **Step 3: Implement the trade ladder**

The ladder remains visible but compact. Each trade advances one node with object icon/label, `TRADE n/14`, and directional motion. It must not hide the physical object or source face. At the house reveal, collapse all nodes into a single paperclip-to-house path.

- [ ] **Step 4: Implement captions from final delivered audio**

Use 2–5 words per burst, Komika Axis, one emphasized keyword and mobile-safe measured width. Derive `caption_at` from final narration/source word timestamps and quantize upward to the next 30fps frame. Keep static chrome and timed captions on separate layers.

- [ ] **Step 5: Implement integrated CTA and moving watermark**

At final 38–42 seconds, action and trade ladder continue under a partial translucent bumper. Spoken and visible CTA must contain `LIKE`, `SUBSCRIBE` and `COMMENT`. Move the watermark among three safe positions over the timeline.

- [ ] **Step 6: Implement stateful sound design**

Mix:

```text
metallic click in 0–1s
one event-bound swap accent per selected major trade
rising score across object → experience → access phases
brief attenuation immediately before the final house exchange
one confirmation impact at the house reveal
short fades at every hard audio boundary
```

Target final loudness near `-16 LUFS`, true peak at or below `-1.5 dBFS`; verify measured output rather than relying on filter arguments.

- [ ] **Step 7: Render the full artifact**

```bash
python3 pipeline/paperclip/render_paperclip_v1.py
```

Expected: final path printed; runtime 58–65 seconds; renderer exits 0.

- [ ] **Step 8: Compile and inspect repository state**

```bash
python3 -m py_compile \
  pipeline/paperclip/generate_paperclip_narration.py \
  pipeline/paperclip/render_paperclip_hook_v1.py \
  pipeline/paperclip/render_paperclip_v1.py
git diff --check
```

Expected: both commands exit 0.

---

### Task 7: Generate QC Evidence and Verify the Final MP4

**Files:**
- Create: `pipeline/paperclip/generate_paperclip_qc.py`
- Create: `pipeline/paperclip/verify_paperclip_v1.py`
- Create: `output/projects/paperclip/checks-v1/verification-summary.json`
- Create: contact sheets and extracted frames under `output/projects/paperclip/checks-v1/`

- [ ] **Step 1: Generate visual QC evidence**

Create:

```text
hook-0-to-3s.jpg — 0.0/0.2/0.5/1/2/3s
hook-0-to-10s.jpg — 0.5s cadence
trade-arc-14-nodes.jpg — one readable frame per trade node
cta-regression.jpg — before/during/after CTA
payoff-42-to-end.jpg — 1s cadence
source-start-mid-end.jpg — three frames per source excerpt
caption-reveal-regression.jpg — two frames before and one frame after selected caption reveals
thumbnail-candidate.jpg — full-size and 270×480 preview
```

Use beat-local accurate seek where global fast seek could cross an archival PTS boundary.

- [ ] **Step 2: Run final ASR**

Transcribe the final MP4 plus dedicated hook, CTA and tail windows. Verify intended normalized tokens and semantic order; ASR is timing/audit evidence, not a substitute for listening.

- [ ] **Step 3: Run media checks**

The verifier must assert:

```text
duration 58–65s
1080×1920
30fps
H.264 yuv420p
AAC stereo 48kHz
full decode exit 0
no black-frame interval
no freeze interval longer than an intentional 0.75s dwell
no unexplained silence over 0.45s
integrated loudness within -17.0 to -15.0 LUFS
true peak <= -1.0 dBFS
all 14 trade nodes represented
all source clips <15s
source-use limits pass
CTA starts in 38–42s and includes all three asks
caption onset never precedes spoken word
watermark position changes
```

- [ ] **Step 4: Perform manual visual inspection**

Inspect every generated sheet with the vision tool and manually review the MP4.
Confirm frame-zero prop/action, readable trade state, object/face not obscured,
stock `ILLUSTRATION` labels, no source ownership confusion, no static-card
interruption and a clear longer house payoff.

- [ ] **Step 5: Perform manual listening pass**

Listen end to end with headphones. Reject clipped words, wrong proper-noun pronunciation, voice handoff whiplash, doubled speech, harsh SFX, masked narration, hard audio joins or a weak payoff impact.

- [ ] **Step 6: Write and run the verifier**

```bash
python3 pipeline/paperclip/generate_paperclip_qc.py
python3 pipeline/paperclip/verify_paperclip_v1.py
python3 -m py_compile pipeline/paperclip/generate_paperclip_qc.py pipeline/paperclip/verify_paperclip_v1.py
```

Expected:

```text
paperclip v1 verification: PASS
```

- [ ] **Step 7: Hash the final artifact**

```bash
shasum -a 256 output/projects/paperclip/final/2026-07-26-one-red-paperclip-v1.mp4
```

Record the real hash and byte size in the verification summary and production document.

---

### Task 8: Package, Document and Preserve the Learning Loop

**Files:**
- Create: `docs/production/one-red-paperclip-v1.md`
- Modify: `docs/README.md`
- Modify conditionally: `docs/WORKFLOW.md`

- [ ] **Step 1: Write the production record**

Include:

```text
artifact path/hash/size/specs
public demand evidence and confounds
claim/source ledgers
exact source and licensable-stock windows
source-use percentages
narration profile and generation report
frame-based final timeline
Hook Gate verbatim evidence
ASR/audio/visual verification outputs
rights/publication blockers
known trade-offs
48-hour metrics checklist
```

Do not mark the video `Completed` while rights review, human listening/viewing or Hook Gate remains unresolved.

- [ ] **Step 2: Run the canonical metadata workflow**

Generate at least five title families and score cold-viewer clarity, stakes, open loop, factual safety and mobile compliance. Final title must be Title Case, at most 30 visible characters and contain exactly two relevant emoji. The design draft `Paperclip To A House? 📎🏠` is a candidate, not an automatic winner.

Description constraints:

```text
first line mirrors canonical title
at most one factual sentence after it
exactly three hashtags including #shorts
exactly three separate Studio tags
no raw affiliate link
Not made for kids
English
Education
finance playlist and Related Video fields explicit or BLOCKED
```

- [ ] **Step 3: Update the production index**

Add one row/link to `docs/README.md` pointing at `production/one-red-paperclip-v1.md`.

- [ ] **Step 4: Run the post-production retro**

Record:

```text
Ronald lesson: technical sync cannot compensate for late payoff, competing open loops or static information cards.
Paperclip result: whether physical frame-zero action, single progress ladder and integrated CTA passed artifact review.
Hook Retro: any stronger verbal/visual hook found after final inspection.
Workflow Delta: exact gap, or "none" if existing stages covered it.
```

If the lesson generalizes and is not already present, patch the correct Stage in `docs/WORKFLOW.md`; otherwise do not create duplicate rules.

- [ ] **Step 5: Final repository and artifact integrity check**

```bash
git diff --check
python3 - <<'PY'
from pathlib import Path
required=[
 Path('docs/production/one-red-paperclip-v1.md'),
 Path('output/projects/paperclip/checks-v1/verification-summary.json'),
 Path('output/projects/paperclip/final/2026-07-26-one-red-paperclip-v1.mp4'),
]
for p in required:
 assert p.is_file() and p.stat().st_size > 0, p
prod=required[0].read_text()
for token in ['TODO','TBD','FIXME','placeholder']:
 assert token not in prod, token
print('final package integrity: PASS')
PY
git status --short
```

Expected: `final package integrity: PASS`; status contains only intentional files.

- [ ] **Step 6: Commit production code and records**

```bash
git add pipeline/paperclip docs/production/one-red-paperclip-v1.md docs/README.md docs/WORKFLOW.md
git commit -m "feat: produce one red paperclip short"
```

Do not add generated MP4/source binaries. Do not upload or publish while the production record shows rights/publication blockers.
