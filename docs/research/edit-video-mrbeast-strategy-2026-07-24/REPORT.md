# Evidence Review — “Edit video triệu view như MrBeast”

Source: https://www.youtube.com/watch?v=OASaa6MKyZQ  
Video ID: `OASaa6MKyZQ`  
Channel: Cường - - Làm Phim Nghiệp Dư (`UCNeFntr5Y7Xc1GKYuMg8suQ`)  
Uploaded: 2025-02-28  
Snapshot at analysis: 117,367 views; 4,132 likes; 261 comments  
Duration: 905s (15:05)

## Method

- Downloaded the highest available 2160p video and separate audio using forced
  IPv4 after the terminal's YouTube IPv6 route timed out.
- Transcribed the complete audio locally with
  `mlx-community/whisper-large-v3-turbo`: 302 timestamped segments.
- Read the 0–10s hook at dense fixed intervals and the full arc at chapter and
  payoff timestamps.
- Ran scene-change analysis at `scene=0.30` (strong changes) and `scene=0.10`
  (sensitive motion/information changes), then manually read the contact sheets.
- Kept observed behavior separate from the video's own claims and from proposed
  causal explanations.

Working evidence:
`output/projects/hardknocks/clips/v16_reference_OASaa6MKyZQ/`

Verified reference asset:

- File: `output/projects/hardknocks/clips/v16_reference_OASaa6MKyZQ/reference.mp4`
- Video: AV1, 3240×2160, 25fps
- Audio: Opus stereo, 48kHz
- Duration: 905.301s
- Size: 482,360,474 bytes
- SHA-256: `1f3433fd7408ba0d2a79c00fa642a7b0eb73d4f5900491aa395c3e0e371608bb`

Verified ASR artifact:

- File: `output/projects/hardknocks/clips/v16_reference_OASaa6MKyZQ/transcript_asr.json`
- Model: `mlx-community/whisper-large-v3-turbo`, language `vi`
- Segments: 302/302 non-empty, covering 0.00–905.32s
- SHA-256: `cd88a71e66d37887666f591ea44ac9da3b45b9b3f79af3ac70b14a630ab973ad`

## What the video says

The presenter organizes the argument around three sections:

1. success metrics: CTR, average view duration, and retention;
2. MrBeast's editorial thinking: expectation, idea-level extremity,
   front-loaded quality, and emotional contrast;
3. rhythm: frequent cuts/changes, purposeful silence, music contrast, and SFX
   for both visible and invisible transitions.

The presenter states that a sampled MrBeast segment averaged roughly one cut
per 1.5s and proposes a “six-second rule” as a practical ceiling for introducing
new visual information. These are the presenter's claims about the sample, not
independent causal proof that a fixed cut rate creates views.

## What this video itself does

### Hook, 0–10s

Observed sequence:

1. presenter points toward camera with a large `Mr.` label;
2. immediate cut to MrBeast footage;
3. money/action imagery;
4. press/news proof;
5. phone/subscriber proof;
6. quantified outcome cards: `50% / 100M` and `>90%`.

The hook produced six strong scene changes in the first 10s. It does not wait
for the presenter to finish explaining the authority claim before showing proof.
Each change adds a new evidence state rather than merely changing decoration.

### Whole-video cadence

- Speech density: approximately 233 words per minute.
- Strong-change median gap (`scene=0.30`): approximately 4.12s.
- Sensitive-change median gap (`scene=0.10`): approximately 1.92s.
- The body is therefore slower than the hook and does not hard-cut every 1.5s.
- Each chapter resets with a minimalist title card, then alternates:
  host explanation → screen/document/MrBeast proof → host synthesis.

This is important: “new information every few seconds” is not equivalent to
“hard cut every 1.5s for the entire video.” Zooms, overlays, proof inserts,
motion, silence, and source changes can all reset attention without destroying
sentence continuity.

## Plausible drivers, not proven causes

- Immediate authority and proof may reduce the time a viewer must spend deciding
  whether the promise is credible.
- Quantified proof makes the opening claim concrete.
- A faster hook than body may optimize the initial decision while preserving
  comprehension later.
- Chapter resets reduce cognitive load in a 15-minute tutorial.
- Music/silence contrast may orient attention around discoveries and transitions.

The 117K-view snapshot does not prove that any single editing choice caused the
performance. Packaging, audience, distribution, topic, and channel history are
uncontrolled confounders.

## Transfer rules for Shorts

1. **Open, do not close, the loop.** The title and first text should define the
   contradiction/question, not state the whole cause and outcome.
2. **Show proof while making the claim.** In 0–10s, preserve the speaking face
   but use partial evidence panels, source cuts, and quantified cards.
3. **Front-load informational changes.** Target a meaningful state change every
   0.8–1.5s in 0–5s and every 2–3s through 10s. Do not require every change to be
   a full-screen cut.
4. **Use a slower body than hook.** Preserve causal comprehension; use evidence
   and semantic reframes before arbitrary effects.
5. **Build contrast into the idea and score.** Problem/tension → deliberate
   quiet beat → discovery lift → payoff state.
6. **Bind SFX to events.** Impacts, reframes, reveals, proof cards, and CTA
   actions receive purpose-specific sounds; a constant effect bed does not.
7. **Pay every open loop.** Do not introduce a new product-versus-company lesson
   at the end unless the same Short explains what created the company.
8. **Keep claims factual.** “Exaggerate the idea” means select a genuinely extreme
   source contradiction; it does not permit unsupported valuation or history.

## Audit of uploaded V15A

Uploaded V15A: `FA7c1g4PvX0`, title `A Crash Created Theragun 🏍️🔧`.

Observed gaps:

- title and opening text close the causal loop immediately:
  `THE THERAGUN ORIGIN` → `A CRASH STARTED IT`;
- the host/interviewer occupies the opening before Jason's emotional problem;
- only two strong scene changes occur in the first 10s versus six in the
  reference hook;
- no partial proof panel appears in the protected hook window;
- one sine-based score runs through the timeline rather than expressing
  pain → discovery → market contrast;
- the ending opens `I had a product, not a company` but never answers what turns
  the product into a company.

## V16 strategy

Three independent Material Revisions test different mechanisms instead of
cosmetic hook swaps:

- **V16A — Product != Company:** invention → 250 jigsaws → clinician sales →
  athlete demand → market validation.
- **V16B — Crash != Breakthrough:** crash → clinic failure → vibrating-table
  relief → back-and-forth motion → first Theragun.
- **V16C — Clinic Contradiction:** his own clinic could not solve his pain →
  temporary relief → mechanism discovery → first Theragun.

Shared execution:

- face remains visible throughout 0–10s;
- partial Pexels panels in the hook are explicitly labeled `ILLUSTRATION`;
- full-screen stock begins only after final 10s;
- captions appear by 0.2s and update in 2–5-word bursts;
- problem/discovery/payoff score states include a deliberate 180ms drop;
- purpose-specific SFX follow visible/invisible events;
- Mid-Roll Triple CTA begins at final 40s;
- each ending states and audibly pays its original premise.

Design and implementation records:

- `docs/specs/2026-07-24-hardknocks-v16-three-way-material-revision-design.md`
- `docs/plans/2026-07-24-hardknocks-v16-three-way-material-revision.md`
