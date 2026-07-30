# Capytech V10 Zack Reaction Explainer

Date: 2026-07-30  
Implementation: `EXACT_FINAL_QC_PASS`  
Publication: `PUBLIC — https://youtube.com/shorts/UBkpHM-VAUA`  
Virality: `VIRALITY_UNPROVEN`  
Human cold-viewer review: `UNVERIFIED`

## Production scope

Sub-format: `Clip Curation Edit - Multi-Source Reaction Explainer`. The edit
uses real test footage from multiple source videos, a complete self-authored
Zack commentary track, animated annotations/data labels, source citations, and
a counter-argument against treating unmatched tests as a controlled ranking.
Each retained source occurrence remains under 15 seconds and aggregate use of
each source remains at or below 50% of its source duration.

V10 is a reaction-first explanation of an apparent contradiction: a phone in
the selected 300-foot test visibly separates, while a different phone in a
different 1,000-foot test still powers on. It is not a height ladder, phone
ranking, or controlled experiment.

The truthful explanation is deliberately qualified. Height affects speed.
Rigid surfaces generally deform less, while more stopping distance can reduce
peak force. Landing orientation, device construction, surface, and test method
also differ. The footage cannot isolate any one of those variables.

The production phase synthesized and ASR-checked the approved Zack narration,
generated native reaction assets, rendered the base master, composited the
post-render value-add layer, and verified the exact final artifact. The final
verifier passed all 97 blocking gates. Human cold-viewer evidence remains
explicitly unverified.

## Why This Segment

The selected segment contains a compact, visually legible contradiction that
already exists in proven source footage: the 300-foot phone visibly separates,
while a different phone in a real 1,000-foot test still powers on. That gives
the first three seconds an ordered evidence chain rather than an invented
format: human host, 300-foot split, real 1,000-foot scale, then powered display.

The segment is useful only if the edit explicitly rejects the tempting
same-phone and height-ranking interpretation. V10 therefore opens an unresolved
question and spends the body explaining why surface, stopping distance,
orientation, construction, and test method prevent a controlled comparison.
The segment earns selection because the visual proof and the corrective
explanation arrive in the same Short, not because it proves one phone is
stronger.

## Canonical hook and timeline

The canonical first line is:

`Three hundred feet split this phone. Another fell a thousand and powered on. Why?`

The hook has a 0.0-4.8 second narration envelope, while its contradiction
visuals complete by 3.0 seconds. Baseline visuals may begin at 3.0 seconds, but
baseline narration cannot begin before 5.0 seconds and cannot overlap the
measured hook.

| Final window | Job |
|---|---|
| 0.0-3.0 | Moving human reaction, separated phone, real 1,000-foot scale, powered display |
| 3.0-10.0 | Waist-height concrete baseline |
| 10.0-19.0 | Ten-story shattered-back escalation |
| 19.0-22.0 | Qualified rigid-landing mechanism |
| 22.0-29.5 | 300-foot display separation |
| 29.5-33.5 | Native-resolution three-state signature reaction |
| 33.5-38.0 | Different 1,000-foot setup and release |
| 38.0-40.0 | Pexels motion, continuously labeled `ILLUSTRATION` |
| 40.0-42.0 | Real source action under sequential CTA |
| 42.0-49.0 | Locked concrete/red-dirt frames, tracker, stopping-distance annotation, two scale changes, and compact mechanism labels |
| 49.0-52.6 | Powered-display visual payoff; Zack's last word remains due by 52.35 |
| 52.6-55.9 | Isolated source quote: `It is on! That's unreal!` |
| 56.0-58.0 | Moving-host loop with `HEIGHT ALONE?` |

## Narrator contract

The generator is locked to:

- Profile ID: `ronald_wayne_zack_style_qwen`
- Profile SHA-256: `ea056c484bc075495fb696887390c32028e54ea5759f7379e6680545914d4408`
- Reference SHA-256: `73550032e52f99f02230d2bd0ca656b8627d936d086889a6534d51dc9541ca09`
- Model: `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-6bit`
- Revision: `34ff5318365b59cba9c03ff729f2eee0814caf72`
- Main weight SHA-256: `b043693cb63f38f4e0ae5fe39a5cfdb466ef199dc5a767991a4a46235ac27e67`
- Speech-tokenizer weight SHA-256: `836b7b357f5ea43e889936a3709af68dfe3751881acefe4ecf0dbd30ba571258`
- Generation settings: English, temperature 0.7, max tokens 768,
  top-k 30, top-p 0.9, repetition penalty 1.5
- Fitting provenance: engine label `Rubber Band R3`, parsed CLI version
  `4.0.0`, combined label `Rubber Band R3 4.0.0`, maximum tempo 1.42

The cache key binds line ID, normalized text, seed, profile and reference
hashes, model repository and revision, both weights, complete generation
settings, and complete fitting settings.

The sequence is synthesis, mild crest compression, loudness normalization,
duration measurement, Rubber Band fitting if required, word-timestamp ASR, and
ordered-token validation. Speech is never fitted with `atrim`, `-t`, sample
slicing, or an output-duration cap. A line that needs more than 1.42x must be
rewritten.

Each narration envelope contains real PCM guard padding. ASR word timestamps
must remain inside the declared speech guard. The payoff must finish by 52.35,
the CTA by 41.7, and the loop by 57.75 seconds. Source audio is muted on every
visual source clip. Only the exact approved quote is restored, with no Zack
narration overlap.

## Reaction contract

The renderer generates nine transparent production reaction poses directly at
1080x1920. It never reads or upscales V9's 270x480 preflight proxies.

The signature reaction has these distinct states:

1. 29.5-29.8: neutral read.
2. 29.8-30.3: both paws rise, eyes widen, and jaw opens.
3. 30.2-30.6: the torso starts recoiling while both feet remain fixed.
4. 30.6-31.15: the torso center moves backward by at least 90 native pixels
   relative to the fixed feet.

Baseline uses a smug chest, folded-paw, and head pose. Shielding uses a curled
torso, squint, and protective-paw silhouette. The powered payoff spans
49.0-52.6 and progresses through read, eye-pop, and recoil states while its
speech deadline remains 52.35.

Every pose must occupy 65-75% of frame height. The separated display remains
readable before the reaction and stays unobstructed in the upper evidence
layout. The verifier creates a dense 270x480 exact-final sheet with separate
checks for evidence timing, coverage, eyes, mouth, left paw, right paw,
body-center displacement, and silhouette change. There is no long-lived panic
sticker.

## Provenance and source reuse

V10 reuses these V9 inputs read-only:

- Source/crop manifest:
  `output/projects/capytech/analysis/v9_real_drop_qc/preflight/source_crop_manifest.json`
- Pexels license:
  `output/projects/capytech/source/v9_real_drop/pexels/license.json`
- Pexels asset:
  `output/projects/capytech/source/v9_real_drop/pexels/36460444_aerial_city.mp4`

All generated audio, reactions, segments, manifests, source usage, evidence,
QC, base master, and final output use distinct V10 paths. No V9 source,
storyboard, script, or provenance record is modified or overwritten.

The final verifier independently hashes the storyboard, generator, renderer,
compositor, verifier, narrator profile, reference audio, model identity,
weights, font, caption calibration, V9 source manifest, V10 source-usage
ledger, native reaction assets and gate, Pexels license and asset, manifests,
evidence, and final MP4.

The Stage-0 preflight fails before preview generation unless the implementation
review is passing and bound to the current storyboard, generator, renderer,
preflight, compositor, and verifier hashes. The full renderer additionally
fails unless `stage0_external_naive_view.json` has the exact
`PASS_STAGE0_EXTERNAL_NAIVE_VIEW` status, a real UTC review time, nonempty
reviewer identity/type, all required naive-view assessments, and current hashes
for the preview, hook manifest, storyboard, TTS manifest, renderer, and
preflight.

Exact-final verification writes deterministic `qc_candidate.json`, excluding
timestamps, report prose, and review status. The exact-final review binds only
to that immutable candidate hash. A read-only adjudication checks the review
record, so rewriting the human-readable QC report cannot invalidate it.

## Audio craft layer

The exact render uses an original procedural 196/294/392 Hz harmonic PCM pad,
high-passed at 150 Hz and low-passed at 1,800 Hz, plus native 48 kHz PCM event
sounds. This replaces the earlier sub-bass-only concept with energy that remains
measurable in the 150-2,000 Hz phone-translation band. Provenance records include
the local ffmpeg filter recipe, timing, path, and SHA-256. Events cover the first
second, drop, impact, split, signature recoil, sequential
Like/Subscribe/Comment entrances, mechanism card and both scale changes,
powered reveal/eye-pop/recoil, and loop. All timed tracks use real PCM leading
silence. A start of exactly zero bypasses the silence concat and uses direct
`apad,atrim`.

The spoken CTA is `Like, subscribe, and comment your guess: does it survive?`
and its final ASR word must land by 41.7 seconds.

## Artifact inventory

The V10 implementation comprises exactly five Python scripts: generator,
Stage-0 hook preflight, renderer, compositor, and verifier. The V10 storyboard
and this production document are the two non-Python source artifacts. The V9
preflight script remains a read-only reference for focus-trajectory semantics.

The V10 preflight creates an exact 0.0-5.0-second review MP4 only after canonical
TTS exists. Its first 90 frames use the renderer's current
`hook_host`/`hook_split`/`hook_scale`/`hook_powered` allocation; its final 60
frames continue `waist_action`. It uses the same sharp dynamic full-bleed source
filter, full canonical ASS captions, canonical placed hook PCM, procedural bed,
and early hook hit. The deterministic manifest and contact sheet live under
`output/projects/capytech/analysis/v10_zack_reaction_explainer_qc/stage0/`.

## Exact-final verification

The media phase must run, in order:

```text
.venv-mlx/bin/python pipeline/capytech/generate_capytech_v10_zack_tts.py
python3 pipeline/capytech/preflight_capytech_v10_zack_hook.py
# Independent naive-view review writes stage0_external_naive_view.json.
python3 pipeline/capytech/render_capytech_v10_zack_reaction_explainer.py
python3 pipeline/capytech/composite_capytech_v10_value_adds.py
python3 pipeline/capytech/verify_capytech_v10_zack_reaction_explainer.py
```

Blocking checks include 1080x1920 H.264 High/yuv420p at 30 fps CFR, AAC
48 kHz stereo, 58-second duration, full decode, black/freeze/silence scan,
successful detector and loudness processes, finite loudness fields, encoded
loudness and true peak, exact-final full/hook/body/CTA/mechanism/payoff/
quote/tail ASR, source-speech allowlisting, captions, sequential CTA, Pexels
disclosure, mechanism-copy order, reaction anatomy and recoil, watermark,
citations, transformative-use ledger, and current Codex review bindings.

The machine visual assessment may be recorded as `VERIFIED_MACHINE_PROXY`.
That never changes the independent human cold-viewer field from `UNVERIFIED`.

## Exact-final production result

The handed-off exact artifact is:

`output/projects/capytech/final/2026-07-30-capytech_v10_zack_reaction_explainer.mp4`

- Artifact SHA-256:
  `60639b179e388d890260e53d31993a98e398e01404551f037b4e036b5ac88cac`
- Canonical QC candidate SHA-256:
  `630b317fd219fce5e4e548367b2da6e541c7baca4632b8658ba466bde8e8c7c3`
- Exact-final QC report SHA-256:
  `2898f363a26dfc0dbd10141cfc252d61e7abf13298394f28417137b55c5bafe5`
- Verifier result: `exact_final_pass=true`, 97/97 gates true, no failed gate.
- Media: 58.000 seconds, 1080x1920, CFR 30 fps, exactly 1,740 frames,
  H.264 High/yuv420p and AAC 48 kHz stereo.
- Audio: -16.32 LUFS integrated, -2.15 dBTP true peak; all three narration-gap
  phone-band windows remained present and bounded.
- Final Codex review: `PASS_ACTIONABLE_FINDINGS_APPLIED`, zero unresolved
  actionable findings, bound to the canonical QC candidate.
- Machine-proxy visual review: passed. Independent human cold-viewer review:
  `UNVERIFIED`.

## YouTube metadata package

Canonical title:

`Powered On After 1,000FT? 📱🤯`

Canonical description:

```text
Powered On After 1,000FT? 📱🤯

One phone split at 300 feet, but a different phone powered on after a separate 1,000-foot drop—here’s one possible reason.

#PhoneDrop #TechExplained #shorts
```

Studio tags, entered separately without `#`:

`phone drop test, smartphone durability, impact physics`

## Public upload identity

- Video ID: `UBkpHM-VAUA`
- User-supplied URL:
  `https://youtube.com/shorts/UBkpHM-VAUA?feature=share`
- Public timestamp: `2026-07-30T14:47:06+00:00`
  (`2026-07-30 21:47:06 +07`)
- Actual channel: ZapBara (`UCFMTbSy9rzBOenAD-U1hvhg`, `@ZapBara`)
- Public metadata: title and description match the canonical package exactly;
  availability is public; category is `People & Blogs`; no public tags were
  exposed.
- Public duration: `56.331610s`; local exact-final duration: `58.000000s`;
  `public - local = -1.668390s`.
- Public-master identity: same visual lineage. Frames through 15s match at the
  same timestamps (`0.999499` mean grayscale correlation); from 25-55s, public
  frames align best to local frames about 1.5-2.0s later (`0.939795` aligned
  mean). The user confirmed that the 56.331610s public version intentionally
  revises a few weaker sections and remains approximately 90% the same as the
  local master. The exact edit list and audio identity were not independently
  audited. Use the public cut and duration as the experiment identity; retain
  the 58s local artifact only as provenance/QC evidence for its own timeline.
- Metrics lifecycle: `IN FLIGHT`; keep Stayed/AVD/Swiped fields `pending` and do
  not fetch or diagnose performance before `2026-08-01 21:47:06 +07`.
- Analytics routing: ZapBara/capytech remains `UNMAPPED`; do not use finance,
  health or aiwork credentials.
- Upload snapshot: `data/uploads/UBkpHM-VAUA.json`.
- Studio-only fields—including Audience, language, location, synthetic-content
  disclosure, playlist, Related Video, upload template, thumbnail and ADR-0035
  lane eligibility—remain unverified. Independent human cold-viewer review also
  remains `UNVERIFIED`.

Virality remains `VIRALITY_UNPROVEN` until real post-publication analytics are
available after the required reporting delay.

## Post-Production Retro

### Hook Retro

- Verbal: no stronger truthful line was found after the empirical TTS rewrite;
  the final hook preserves the different-phone qualifier and open question.
- Visual: the exact-current Stage-0 machine proxy passed the ordered
  split/scale/powered contradiction. Independent human evidence remains missing
  and is not inferred from the public upload.

### Workflow Delta

- Public-master verification found that matching title, dimensions and opening
  frames do not establish exact timeline identity. The upload snapshot therefore
  preserves public duration and timing-offset evidence separately from local
  exact-final provenance. The user later confirmed the difference was caused by
  intentional edits to a few weaker sections; the public cut is authoritative
  for analytics while local 97/97 QC remains scoped to the local 58s timeline.
