# ZapBara vs Capybluh: Root-Cause Analysis of `hkxEmwLKAOw`

Date: 2026-07-28  
Target: https://youtube.com/shorts/hkxEmwLKAOw  
Source channel: https://www.youtube.com/@capybluh/shorts  
Point-in-time data: `docs/research/zapbara-capybluh-root-cause-2026-07-28/evidence-summary.json`

## Executive verdict

The current public count does **not yet prove that the creative failed**. At the last refresh, the Short had 2 public views only 6.49 hours after publication. Without private Studio data for `Shown in feed`, `Viewed vs swiped away`, AVD/APV, traffic source, and the retention curve, there is no statistically defensible way to distinguish “YouTube has barely tested it” from “the first test audience rejected it.”

However, the media comparison does establish two root findings with greater than 99% confidence:

1. **The video copied Capybluh's surface identifiers, not the causal content engine.** It copied a speech-free animated character, era labels, reaction shots, and cartoon sound effects. It did not copy the source format's repeated experiment: one familiar object, one repeated action, one monotonic visual variable, one fixed stage, and one extreme physical payoff.
2. **The public upload is not the approved local artifact.** The visuals closely match through the shared duration, but the public file is about 2.2 seconds shorter and its audio is materially different from the verified master. This is not explainable by ordinary AAC/YouTube transcoding.

The strongest creative root cause is therefore not “animation quality” or “the algorithm.” It is a **format-architecture mismatch** caused by combining an 18-second source formula with a mandatory 50-second runtime, a separate 5.5-second hook, a 4.4-second CTA, multiple explanatory UI systems, and only 25 seconds of generated base-character footage.

A million-view outcome can never be guaranteed at 99% because recommendation and viewer response are stochastic. What can be made greater than 99% reproducible is **source-format fidelity**. The next production should either:

- copy Capybluh's 14–29 second `object 2000 vs 2026 vs 2050` format faithfully, which requires an explicit exception to this project's 50–75 second rule; or
- retain the 50–75 second rule and copy Capybluh's proven long format, `1s vs 1m vs 10m vs 1h`, rather than stretching the short three-era format.

Under the current project policy, the second option is the recommended route.

## What was inspected

### Target evidence

- Public Short and current public metadata.
- Publicly downloadable video/audio stream.
- Local approved master: `output/projects/capytech/final/2026-07-28-capytech_v6_visual_comedy.mp4`.
- Renderer, storyboard, render manifest, QC report, upload snapshot, and packaging metadata.
- Frame samples at 0.5-second and 1-second intervals.
- Audio loudness, onset, waveform correlation, and AAC round-trip control.
- Public channel state for ZapBara.

### Source evidence

All 88 currently exposed Capybluh Shorts were collected for metadata-level analysis. Media was inspected for multiple winners and controls, including:

| Video | Runtime | Point-in-time views | Role |
|---|---:|---:|---|
| [Oreo 2000 vs 2026 vs 2050](https://youtube.com/shorts/NL4Hrvis-_8) | 16s | 216.9M | three-era winner |
| [Buldak 2000 vs 2026 vs 2050](https://youtube.com/shorts/z3t4DbsKkLs) | 29s | 131.9M | three-era winner |
| [Donut 2000 vs 2026 vs 2050](https://youtube.com/shorts/l8YoE0g8oqc) | 18s | 97.4M | three-era winner |
| [Phone 2000 vs 2026 vs 2050](https://youtube.com/shorts/PzRfD1C3VjI) | 17s | 10.1M | topic-matched control |
| [Pringles 2000 vs 2026 vs 2050](https://youtube.com/shorts/nSEG9A_uMco) | 21s | 6.3M | format-matched control |
| [1s vs 1h](https://youtube.com/shorts/t854ZvvEuPk) | 50s | 163.3M | long-format winner |
| [1s vs 1m](https://youtube.com/shorts/iOxZ5Yi1u3c) | 56s | 96.3M | long-format winner |
| [1s vs 1h](https://youtube.com/shorts/u3yS1GN9vj4) | 57s | 62.0M | long-format winner |
| [1s vs 1h](https://youtube.com/shorts/xDnToe-5KYc) | 56s | 4.6M | long-format control |

The public source channel displayed about 2.74M subscribers, roughly 2.76B channel views, and 88 Shorts. ZapBara displayed one upload, zero subscribers, and two total views. Raw lifetime views are therefore heavily confounded by channel history and video age.

## The source formula we actually needed to copy

### Short three-era format

Across 16 Capybluh titles containing `2000`, `2026`, and `2050`:

- runtime range: 14–29 seconds;
- median runtime: 18 seconds;
- median point-in-time views: 24.17M;
- the target public runtime, 48.267 seconds, is 2.68 times the source median and 1.66 times the source maximum.

The repeatable semantic engine is:

1. **One familiar object is visible at frame 0.** Oreo, donut, Buldak, phone, Pringles.
2. **The exact comparison state is visible at frame 0.** The active year appears immediately.
3. **The same action repeats in every era.** Open/eat, inspect/use, or interact with the same product.
4. **One property changes.** Filling amount, hole size, quantity, fold count, heat, or another immediately visible scalar.
5. **The stage and camera remain nearly fixed.** This makes comparison effortless; continuity is an information device, not a production limitation.
6. **The viewer predicts the next state.** Once 2000 and 2026 are seen, the viewer waits to discover how absurd 2050 becomes.
7. **The final state becomes a physical gag.** The object overwhelms, traps, burns, disappoints, or otherwise changes the character's body/reaction.
8. **The video stops immediately after the reaction.** No separate explanation, scoreboard, or long CTA is needed.

Examples:

- Donut enlarges the same hole until the final donut becomes an absurd ring around the character.
- Phone increases the same fold/accordion behavior across eras.
- Pringles uses the same quantity-decline idea, but its progression is slower and its final empty-can result is more predictable. It is a useful matched control: retaining the skin and structure does not guarantee a top hit if the final visual idea is weak.

### Proven long format

Capybluh also has a source-compatible solution for the project's 50–75 second constraint:

- `1s vs 1h`, 50s, 163.3M views;
- `1s vs 1m`, 56s, 96.3M views;
- another `1s vs 1h`, 57s, 62.0M views.

These videos are not elongated three-era skits. They use a different retention engine:

1. A persistent stage tracker such as `1s / 1m / 10m / 1h` appears from frame 0.
2. The first experiment begins immediately.
3. Every stage is a complete mini-loop: setup -> action -> visible result -> character reaction.
4. Each later stage increases time, effort, tool intensity, object transformation, or consequence.
5. A stage resolves approximately every 8–13 seconds, providing four intermediate payoffs before the final payoff.
6. The same object and rule persist, so the viewer never has to relearn the story.

This is why the long videos can sustain 50–57 seconds. They contain multiple source-native rounds; they do not fill time with a standalone hook, unrelated era mechanisms, UI, or a CTA interruption.

## What our video copied—and what it changed

### What was copied successfully

- Speech-free visual storytelling.
- A central animated mascot.
- Year labels and a `2000 / 2026 / 2050` shell.
- Cartoon reactions and event-bound sound effects.
- A broadly readable everyday object: phone charging.
- A future-state physical consequence.

These choices explain why the result feels superficially related to Capybluh.

### What was not copied

| Source invariant | `hkxEmwLKAOw` |
|---|---|
| Same object/action repeated | Different mini-mechanisms: giant charger, adapters, update, wireless orb, energy theft |
| One visual scalar | Multiple concepts: charger size, connector compatibility, cable reach, software update, price, energy source, two meters |
| Fixed stage for comparison | Different rooms, compositions, props, overlays, and camera reframes |
| Active era/action at frame 0 | Generic `CHALLENGE` preamble; era one starts around 5.5s |
| Minimal explanatory UI | Battery card, arrow, portals, scoreboard, adapter stack, spinner, `FREE?!`, scan, dual meters, CTA rail, final cards |
| Short 14–29s structure | 48.267s public runtime |
| Immediate final reaction and stop | 4.4s mid-roll CTA plus payoff and attempted loop |
| Mostly unique causal animation | Five 5-second generated base clips remapped into 29 cuts over 50.5s |

This is the central failure: the production treated `2000 / 2026 / 2050` as the format. It is only the label. The actual format is **repeated physical comparison under a single rule**.

## Timeline comparison

### Our first ten seconds

- `0.0s`: mascot, a small phone/battery problem, and a vague `CHALLENGE` label.
- `0–2.8s`: the viewer sees charging trouble, but not the promised three-era comparison.
- `2.8–4.4s`: three year portals explain the format through UI.
- `4.4–5.5s`: `GO` transition.
- `~5.5s`: the first real era begins.

The 5.5-second standalone setup consumes 11.4% of the public runtime. It is not empty in the traditional editing sense—there is motion and sound—but it is **semantic delay**. The source winners spend those same seconds completing most or all of their first era.

### Source examples

- Oreo begins `2000` at frame 0, switches to `2026` around 5s, and reaches `2050` around 11s.
- Donut begins `2000` at frame 0, switches around 7s and 12s, and finishes around 18s.
- Buldak begins `2000` at frame 0 and delivers visible product handling, heat escalation, and reaction during its first ten seconds.
- The 50-second `1s vs 1h` winner shows all stage labels immediately, starts the first tool/object interaction at once, completes the first result/reaction around 8–9s, and then advances to the next stage.

The lesson is not merely “cut faster.” It is: **start the repeated rule at frame 0**.

## Semantic clarity versus visual activity

The target has more measured pixel activity than the reference examples:

- target mean edge density: 0.2129;
- Buldak: 0.1075;
- Oreo: 0.1135;
- Donut: 0.1022;
- Phone: 0.0794.

The target is roughly 1.9–2.7 times as edge-dense as these examples. Its mean frame-difference score is also 1.1–1.9 times higher.

This does not make it more engaging. Much of the extra activity comes from composited UI, particles, reframes, speed lines, meters, and cuts. Capybluh's strongest clips are visually simpler because the **object itself changes state**. A stable frame makes the meaningful change easier to detect.

This exposes a QC blind spot: cadence and SFX density passed, but semantic progression was not validated by an unbriefed viewer. The packaging metadata explicitly records: `External naive-viewer Hook Gate evidence is not recorded.`

## Character and physical comedy

Capybluh's Roblox-like mascot has several operational advantages:

- a known visual language and established channel identity;
- crisp silhouette and exaggerated face states;
- deterministic hand-object contact;
- props that retain shape across the complete action;
- an intentionally simple fixed stage that makes state changes obvious.

The ZapBara capybara is more detailed and polished as a still image, but detail is not the retention engine. The five generated clips constrain the character to relatively generic poses, while overlays carry much of the explanation. Reusing overlapping source ranges under new cuts and reframes creates editorial motion without always creating new physical causality.

The better production system is not “add more effects.” It is to generate or animate complete action-result-reaction chains with controllable prop physics. A reusable rigged 3D scene would likely outperform repeated five-second generative clips for this particular format because it preserves character, camera, hand-object contact, and exact state progression across every round.

## Topic, audience, and packaging mismatch

### Topic

YouTube's official Shorts guidance states that topic interest, competition, viewer history, and performance all affect reach. The source's largest three-era examples use globally familiar branded foods with immediate sensory stakes: taste, heat, size, quantity, and shrinkflation.

Within the same established source channel:

- food winners reached approximately 97M–217M;
- `Phone 2000 vs 2026 vs 2050` was around 10.1M.

Ten million is still a success, but it is a useful control showing that the house style alone does not erase topic differences. Phone/charging has broad recognition but weaker sensory payoff than Buldak heat or food-size absurdity.

### Title

Source titles state the exact visual contract:

- `Oreo 2000 vs 2026 vs 2050`
- `Buldak 2000 vs 2026 vs 2050`
- `Phone 2000 vs 2026 vs 2050`

Our title, `Free Charge, Hidden Cost`, is a reasonable abstract curiosity line but hides both the series format and the exact object comparison. This matters most for a new channel with no established audience graph. The internal title rubric awarded itself perfect cold-viewer clarity without an external naive-viewer test.

A source-faithful title would have been closer to `Phone Charging 2000 vs 2026 vs 2050`.

### Audience architecture

The repository's documented AI-education vertical targets English-speaking professionals/knowledge workers. The Capytech packaging instead positions this as visual comedy for younger children and recommends `Made for kids`. Meanwhile, the public category currently resolves as `People & Blogs`, although the planned package specified `Science & Technology`.

These are conflicting audience signals:

- visual grammar: young child/family animation;
- topic/hashtags: future tech and AI animation;
- broader project vertical: professional AI education;
- title: abstract cautionary tech comedy;
- public category: People & Blogs.

A new channel needs one coherent viewer promise. The next video should not try to serve children, tech professionals, AI-animation enthusiasts, and general comedy viewers simultaneously.

## CTA and Made-for-kids contradiction

The mid-roll triple CTA runs approximately `38.0–42.4s`, or 9.1% of the public runtime. It interrupts the 2050 climax just before the payoff.

The packaging plan says the audience is `Made for kids`, while the CTA asks viewers to like, subscribe, and comment. YouTube disables comments and restricts other features on made-for-kids content. The production metadata itself records that the comment CTA cannot function as written.

This creates a lose-lose design:

- if the video is accurately made-for-kids, the comment request is nonfunctional;
- if it is not made-for-kids despite being explicitly designed for younger children, there is a compliance question that must be resolved honestly;
- in both cases, the four-second interruption departs from the source format.

This is not proven to have caused the current two-view count, but it is a high-confidence process defect and a likely retention cost once the video receives feed exposure.

Official reference: https://support.google.com/youtube/answer/9527654?hl=en&co=GENIE.Platform%3DDesktop

## Public upload integrity incident

The local QC pass did not guarantee that the public artifact matched the approved master.

### Verified differences

- local duration: 50.5s;
- public duration: 48.267s;
- public duration recorded by the upload metadata: 48.301s;
- missing tail: approximately 2.20–2.23s, including the attempted update/loop material;
- visual sampled-frame correlation through the common timeline: 0.9977;
- best aligned audio correlation in the first 12s: 0.2177;
- residual public-audio energy after fitting the local master: 97.36%;
- public downloaded audio: approximately -1.0 LUFS integrated and +5.71 dBTP;
- local master: approximately -15.9 LUFS and -1.54 dBTP;
- about 20.7% of decoded public samples in each channel exceed absolute 0.99 before playback clamping;
- source audio attribution shown by YouTube: `Original Sound`.

A control AAC round trip of the local master retained 0.9989 waveform correlation. Ordinary AAC encoding therefore does not explain the 0.2177 public/local correlation. The public upload contains a materially different or heavily overlaid audio signal. The exact upload-side mechanism is not recorded, so it should not be guessed.

Player-side loudness normalization may reduce playback gain, but it cannot restore waveform information removed by upstream clipping and does not explain the mismatch with the approved master.

### Consequence

The local media QC proved the wrong thing: it proved that the local master was valid, not that viewers received that master. The public artifact needs a post-upload parity gate before any upload can be called complete.

## Sound is a secondary factor, not the root cause

The Buldak benchmark publicly attributes `The Amazing Digital Circus Theme Song`, a recognizable sound that can provide trend and sound-page discovery signals. YouTube explicitly says sampled/trending audio can influence personalization and sound-page discovery.

However, the 217M-view Oreo benchmark attributes `Original Sound`. This is a direct counterexample to “the trending song caused the virality.” Sound selection is an amplifier and distribution vector, not the invariant core.

Official Shorts discovery reference: https://support.google.com/youtube/answer/11914225?hl=en&co=YOUTUBE._YTVideoType%3Dshorts

## Channel-history and distribution confound

At the measurement point:

- ZapBara: one video, zero displayed subscribers, two displayed views;
- Capybluh: 88 Shorts, about 2.74M subscribers, and roughly 2.76B channel views.

Capybluh has a large learned viewer graph, repeat viewers, brand recognition, and historical recommendation data. ZapBara does not. This difference is certain; its exact causal contribution is not measurable from public data.

It would also be incorrect to claim that YouTube deliberately suppresses new channels. YouTube's official documentation says Shorts are matched based on personalization, performance, and external factors; it does not state a blanket new-channel penalty. A new channel can still receive a Shorts-feed test.

The correct diagnosis requires Studio data after the project's 48-hour waiting period:

- If `Shown in feed` is near zero, the result is primarily an exposure/distribution problem and creative quality remains untested.
- If feed exposure is meaningful but `Viewed vs swiped away` misses the target, frame-0 contract and topic/audience matching are the first suspects.
- If viewers choose to watch but retention falls around 2.8–5.5s, the portal/`GO` preamble is implicated.
- If retention drops around 38–42s, the CTA interruption is implicated.
- If the ending has weak completion/replay, the lost tail and payoff/loop structure are implicated.

Do not delete or re-upload merely to reset distribution. Preserve this upload, wait at least 48 hours, and use the project's plateau/material-revision rules.

## Ranked hypothesis matrix

| Rank | Hypothesis | Evidence for | Counter-evidence / limitation | Confidence |
|---:|---|---|---|---:|
| 1 | Copied visual skin, not repeated-comparison engine | Direct frame/storyboard comparison; multiple winner and control samples | None material | 99% |
| 2 | Three-era format was stretched beyond its native runtime | 48.267s versus 14–29s source range, 18s median; 5.5s preamble; 4.4s CTA | Buldak itself is longer at 29s, but still far shorter | 99% |
| 3 | Public artifact differs materially from approved master | Duration, audio correlation, residual energy, loudness, AAC control | Exact upload-side cause unknown | >99% for mismatch; 80% for retention impact if exposed |
| 4 | UI activity replaced semantic object-state progression | About 2x source edge density; many overlays; one-to-many concepts | Some UI is story-bearing and may help comprehension | 95% |
| 5 | Cold-viewer/audience validation was skipped | Metadata explicitly says external naive-viewer gate not recorded; targeting signals conflict | No direct user study was available | 95% process confidence |
| 6 | New-channel history limits available personalization signals | 0 subscribers/1 upload versus 2.74M/88 Shorts | New channels are not categorically suppressed; Studio exposure is unknown | 99% confound exists; 75% causal weight |
| 7 | Topic has weaker broad/sensory appeal than top food winners | Official topic-interest factor; phone control ~10M versus food winners 97–217M | Phone still reached 10M on source channel | 85% |
| 8 | Mid-roll CTA and made-for-kids design are incompatible | CTA consumes 9.1%; comments restricted; source has no equivalent interruption | No target retention curve yet | 99% process issue; 70% likely retention cost |
| 9 | Generic AI character physics reduce comic clarity | Five short generated sources; overlays carry causal explanation | Still-image quality is high and visuals are coherent overall | 75% |
| 10 | Lack of trending sound caused low views | Buldak uses a named trend sound; official sound-page mechanism | Oreo reached 217M with Original Sound | 30% as primary cause |

## Five-whys root cause

1. **Why is the result not behaving like the source?**  
   The viewer receives a more complex, slower, less comparable story.
2. **Why is it slower and less comparable?**  
   Three unrelated charging mechanisms were put inside a format whose source uses one repeated object/action/variable.
3. **Why was that done?**  
   The 14–29 second source format was forced into a 50.5-second project runtime with a standalone hook, triple CTA, payoff section, and loop requirement.
4. **Why did QC still pass?**  
   QC optimized measurable craft proxies—cut cadence, motion, SFX count, technical media validity—but did not include an external cold-viewer semantic test or public-upload parity test.
5. **Why is the strategic system vulnerable to this?**  
   It treats checklists as additive. Every “best practice” is added even when it breaks the causal mechanism of the copied format. Source fidelity needs to be a blocking architecture constraint, not another item in the checklist.

## Second- and third-order effects

### Checklist accumulation

More overlays -> more measured visual changes -> QC appears stronger -> the object becomes less legible -> choose-to-view and comprehension can fall -> the team responds by adding even more explanation. This is a negative reinforcement loop.

### New channel plus mixed audience

No viewer history -> YouTube must infer likely viewers from topic and early behavior -> mixed child/tech/professional signals seed an incoherent audience -> early response becomes noisier -> distribution confidence grows more slowly.

### Copying the incumbent's skin

A new channel copying the exact visual skin competes directly with an incumbent that owns the mascot association, sound familiarity, and audience graph. The defensible move is to copy the **causal grammar** while owning a different mascot/topic promise. This is the blue-ocean opportunity: `Capybluh mechanics + ZapBara tech objects`, not `Capybluh labels + unrelated tech exposition`.

### Paid generative footage

Five-second generation constraints -> overlapping source ranges and UI are used to reach 50s -> physical causality weakens -> more paid retries seem necessary. A reusable deterministic 3D rig can reverse the economics: higher initial setup, then cheaper, consistent, editable action chains for every future episode.

## Recommended next-video route

### Route A: exact three-era mimic

Use only if the project explicitly approves an exception to the 50–75 second policy.

Specification:

- 16–24 seconds; never exceed the source's observed 29-second maximum.
- Title and frame-0 label: `Phone Charging 2000 vs 2026 vs 2050`.
- One fixed table/camera.
- Same phone and same plug-in action in every era.
- One monotonic variable only, such as adapter count or cable complexity.
- First physical action by `0.3s`.
- Each era: action -> visible result -> facial reaction.
- `2050` ends in one extreme body-object gag.
- No standalone hook, scoreboard, scan explanation, mid-roll CTA, or post-payoff explanation.

This is the highest-fidelity route, but it currently violates repository policy.

### Route B: source-native long format — recommended

Working concept: **`Phone Charging: 1s vs 1m vs 10m vs 1h`**

Target runtime: 50–56 seconds.

Persistent top tracker from frame 0:

`1s | 1m | 10m | 1h`

Example structure:

1. `0–9s — 1s`: same phone, same charger, immediate plug-in, tiny result, unimpressed reaction.
2. `9–20s — 1m`: repeat the exact action, visibly larger result, hopeful reaction.
3. `20–33s — 10m`: repeat, full charge, celebration, first sign of excessive heat/size.
4. `33–49s — 1h`: repeat, extreme fictional overcharge consequence physically overwhelms the mascot.
5. `49–53s`: one clean final reaction that visually returns toward frame 0.

Rules:

- One object, one action, one measurable variable, one stage.
- Every round must have its own payoff; no section exists only to explain another section.
- No separate 0–5s intro. The first round is the hook.
- Do not use a four-second triple CTA inside the experiment. If ADR-0034 remains mandatory, record explicitly that exact Capybluh fidelity is impossible and test the CTA as a known intervention rather than pretending it belongs to the source format.
- Keep only the persistent stage tracker and one result indicator. Remove decorative scoreboards, portals, scanners, and redundant meters.
- Use complete physical action clips; do not relabel the same generated motion as several different semantic events.
- Treat the final overcharge as obvious fiction, not a factual product/safety claim.

## Production architecture recommendation

For reliable imitation, replace “five unrelated generative clips plus heavy post overlays” with a reusable scene system:

- rigged ZapBara mascot;
- fixed table/background/camera presets;
- reusable phone, cable, charger, food, and tool props;
- named facial reaction poses;
- deterministic hand-to-prop constraints;
- one timeline per action-result-reaction round;
- renderer adds only labels, sound, and final color finishing.

This lets the team modify the actual joke—object state and physics—instead of trying to rescue weak causality in post-production.

If paid Higgsfield generation remains the chosen route, budget for complete stage-length causal shots or controlled extensions. Do not start a paid batch without the user's explicit cost approval.

## Blocking gates for the next production

### Gate 1: source-format declaration

Before storyboarding, write exactly one line:

`Object + repeated verb + changing scalar + final physical exaggeration.`

If any era uses a different verb or scalar, reject the concept.

### Gate 2: runtime-family match

- Three-era format: 14–29s observed source range.
- Long test format: 49–60s observed successful source range.

Do not stretch one family to satisfy the other family's runtime.

### Gate 3: frame-0 test

Show frame 0 for 200ms to at least five unbriefed viewers. At least four must identify:

- the central object;
- what test/comparison has started;
- the active stage or year.

### Gate 4: mute-first animatic test

After one silent viewing, at least four of five unbriefed viewers must correctly state:

- the repeated action;
- the variable that changes;
- the order of stages;
- what happened in the final gag.

### Gate 5: semantic cadence

A semantic state—not merely a cut, particle, zoom, or UI pulse—must change every 2–4 seconds. A state change is a new action, object state, result, or reaction.

### Gate 6: public-upload parity

Immediately after upload, download the public artifact and verify:

- duration difference no greater than 0.10s;
- sampled visual correlation at expected timestamps;
- aligned audio correlation greater than 0.95 unless an intentionally documented library sound was added;
- expected sound attribution;
- first frame and final payoff/loop present;
- expected category, audience, playlist, and related-video settings.

The current upload would fail this gate.

### Gate 7: 48-hour distribution diagnosis

Do not declare success/failure before the 48-hour analytics gate. Record:

- Shown in feed;
- Viewed vs swiped away, with the project goal of swiped away below 20%;
- Audience-retention Stayed to watch, kept separate from Viewed vs swiped away;
- AVD in seconds;
- average percentage viewed;
- retention timestamps at the first action, each stage transition, CTA, payoff, and ending;
- traffic source and sound-page traffic if applicable.

## What not to do next

- Do not delete this Short to reset distribution.
- Do not interpret two views at 6.49 hours as a reliable creative sample.
- Do not make another 50-second `2000/2026/2050` video with a 5-second preamble.
- Do not solve semantic ambiguity by adding more UI.
- Do not reuse a comment CTA on a made-for-kids upload.
- Do not claim a local QC pass until the public artifact is checked.
- Do not assume a recognizable song is the secret; Oreo is a 217M counterexample using Original Sound.
- Do not copy the blocky character as the key asset. Copy the repeated experiment and physical state-change engine.

## Confidence statement

I am greater than 99% confident in these two findings:

1. `hkxEmwLKAOw` is not a faithful implementation of Capybluh's three-era causal grammar.
2. The public audio/tail do not match the verified local master.

I am not 99% confident that either defect caused the current public count of two views, because the Short was only 6.49 hours old and private distribution/retention data were unavailable. Claiming otherwise would be fabricated certainty.

The next video can be made greater than 99% mechanically similar to the source **format** by passing the seven gates above. No honest process can guarantee a million-view result at 99%, because YouTube explicitly ranks on viewer response, personalization, topic interest, competition, and other external factors.

## Sources and reproducibility

Primary public sources:

- Target Short: https://youtube.com/shorts/hkxEmwLKAOw
- ZapBara: https://www.youtube.com/@ZapBara/about
- Capybluh: https://www.youtube.com/@capybluh/about
- Capybluh Shorts: https://www.youtube.com/@capybluh/shorts
- YouTube Shorts search/discovery guidance: https://support.google.com/youtube/answer/11914225?hl=en&co=YOUTUBE._YTVideoType%3Dshorts
- YouTube audience/made-for-kids settings: https://support.google.com/youtube/answer/9527654?hl=en&co=GENIE.Platform%3DDesktop

Repository evidence:

- `data/uploads/hkxEmwLKAOw.json`
- `docs/production/capytech-v6-visual-comedy.md`
- `docs/specs/2026-07-27-capybluh-strategy-short-design.md`
- `output/projects/capytech/source/capybluh_research_summary.json`
- `output/projects/capytech/scripts/capytech_v6_visual_comedy_storyboard.json`
- `pipeline/capytech/render_capytech_v5_higgsfield.py`
- `pipeline/capytech/render_capytech_v6_visual_comedy.py`
- `output/projects/capytech/analysis/v6_visual_comedy_qc/final_qc.json`
- `output/projects/capytech/clips/capytech_v6_visual_comedy_work/render_manifest.json`
- `output/projects/capytech/clips/capytech_v6_visual_comedy_work/metadata.json`

Derived evidence:

- `docs/research/zapbara-capybluh-root-cause-2026-07-28/evidence-summary.json`

The comment sample was bounded to approximately 300 fetched comments per sampled video where available. It was used only as supporting evidence for comprehension and reaction themes, not as a complete or globally top-ranked comment census.
