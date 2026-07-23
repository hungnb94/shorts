# HardKnocks V14A/V14B — Theragun Dual-Hook Design

## Status

Approved by delegated selection in the user request: generate five hooks, self-rank them, and produce the two strongest videos. No upload is authorized.

## Source

- Video: `https://www.youtube.com/watch?v=xv8qaYubDw4`
- Title: `They’re Lying To You About How To Get Rich… Here’s How I Built Theragun | Dr. Jason Wersland`
- Channel: School of Hard Knocks Podcast
- Source duration: 4401s
- Source master: `output/projects/hardknocks/source/xv8qaYubDw4.mp4` (3840x2160)
- Word-timestamped transcript: `output/projects/hardknocks/clips/v14_theragun_work/research/transcript.json`

## Constructive Diagnosis of the Previous Opening

The newest finance artifact in the repository, V13, opens with a generated Direct Search Question that takes about 2.82s to complete and does not find the billionaire until about 20.74s. Its technical hook gates passed, but the structure still asks a cold viewer to invest attention before receiving a concrete human consequence.

No current Studio metric was supplied and V13's production document still says queued, so this is a structural hypothesis—not a claim that the question caused the reported flop.

The new opening mechanism is **Verbatim Consequence Cold Open + Delayed Object Reveal**:

1. Start with the guest's original voice, not TTS.
2. Deliver a concrete consequence or absurd action in the first sentence.
3. Withhold the identity/meaning of the object for only 3–6s.
4. Reveal the jigsaw-to-Theragun connection by 5–8s.
5. Keep the guest's moving face visible throughout 0–10s; product/tool proof is a partial insert, never a full-screen face blackout.

This changes the viewer contract from “wait for the answer to my question” to “here is the surprising result—now resolve how it happened.”

## Five Hook Candidates

Scores are editorial heuristics, not analytics predictions. Weighted dimensions: curiosity gap 22%, specificity 18%, visual proof 17%, emotion 15%, payoff speed 16%, novelty versus V13 12%.

| Rank | Candidate | Exact source opening | Overlay treatment | Score / 10 | Decision |
|---:|---|---|---|---:|---|
| 1 | Absurd-number jigsaw | `I bought 250 jigsaws from Kawasaki...` (908.86s) | `250 JIGSAWS. WHY?` + rapid counter + corner tool silhouette | 9.32 | Produce V14A |
| 2 | Verbatim life-saving quote | `Doc, this thing saved my life. And I know it saved yours.` (795.06s) | `THIS THING SAVED TWO LIVES` while the object remains withheld | 9.15 | Produce V14B |
| 3 | Father rejection | `My dad looked at me... “You're crazy. People aren't going to buy this.”` (1087.44s) | `HIS DAD SAID NO ONE WOULD BUY IT` | 8.67 | Reserve |
| 4 | Crash survival | `I t-boned the side of the car... I didn't die.` (16.40s) | `THE CRASH CAME FIRST` | 8.38 | Reject for this batch: familiar founder-trauma opening and slower product connection |
| 5 | Doctor contradiction | `I really had nothing in my clinic that was going to help me.` (195.04s) | `A DOCTOR WITH NO TREATMENT` | 8.33 | Reject for this batch: strong contradiction, weaker visual object and number |

## Video V14A — 250 Jigsaws

### Hook

- Frame 0: active-speaker crop on Jason's moving face/hand gesture at source 908.86s.
- Spoken line: `I bought 250 jigsaws from Kawasaki and I shipped them to my house.`
- Editorial overlay appears by t=0.2s: `250 JIGSAWS.` then `WHY?`
- Early SFX: one mechanical click/impact at t=0–1s.
- Partial/corner proof: moving power-tool insert while Jason remains visible.
- First reveal by t=5–8s: bolt + foam ball + first Theragun connection.

### Arc

1. Absurd purchase: 250 jigsaws.
2. Prototype recipe: jigsaw + bolt + foam ball.
3. Validation: patient says it saved both lives.
4. Market signal: athletes empty the trunk.
5. Father rejection as resistance.
6. Payoff: solve one painful problem deeply before trying to look scalable.

### Value-adds

- Animated 250-unit counter and exploded prototype recipe.
- Source-citation/timeline labels (`2008 prototype`, `2009 batch`).
- Partial Pexels power-tool/maker footage; no full-screen replacement in 0–10s.
- Business Lesson Payoff.

## Video V14B — This Thing Saved Two Lives

### Hook

- Frame 0: tight active-speaker crop on Jason at source 795.06s.
- Spoken line: `Doc, this thing saved my life. And I know it saved yours.`
- Editorial overlay by t=0.2s: `THIS THING SAVED TWO LIVES`.
- The object is deliberately withheld in the first beat.
- Early SFX: heartbeat-to-mechanical-click transition in t=0–1s.
- Partial reveal at 3–5s; full jigsaw/Theragun identity resolved by 5–8s.

### Arc

1. Customer's life-saving verdict.
2. Flash back: motorcycle crash and 10/10 pain.
3. Discovery: vibrating table briefly removed the pain.
4. Prototype: Makita jigsaw in a paper bag.
5. Validation: patient and wife reaction.
6. Payoff: the first customer did not buy the product—he gave the founder the mission.

### Value-adds

- Two-person consequence counter (`PATIENT` / `FOUNDER`).
- Animated causal chain: crash → pain → vibration → prototype.
- Partial Pexels physical-recovery/tool footage; no full-screen replacement in 0–10s.
- Source citation and Business Lesson Payoff.

## Shared Production Rules

- English only.
- Original source voice throughout; no TTS narration.
- 1080x1920, H.264/AAC, 30fps, 50–75s.
- Hard-cut Multi-Clip Mashup; every source-audio clip under 15s.
- Active-Speaker Reframing and at most one semantic punch-in per answer.
- Komika Axis captions, 2–5 words per burst, one emphasized keyword.
- Moving footage throughout 0–3s; frame 0 contains a prominent human face.
- No full-screen proof/B-roll before 10s.
- Visual change every 1–2s in 0–5s and every ~2s afterward.
- Early SFX at t=0–1s.
- Custom Like/Subscribe/Comment CTA begins at 38–42s.
- Moving `HARD KNOCKS LAB` watermark changes position across the timeline.
- Transformative Gate: editorial commentary captions, at least two value-adds, each source clip under 15s, aggregate source use under 50% of the 4401s source.
- Three-source visual package: original interview, post-render animated overlays, and relevant Pexels footage.
- Video-specific production documents contain one canonical upload package each; no separate metadata file.

## Verification

For each final MP4:

1. ffprobe dimensions, codecs, frame rate, pixel format, audio, and duration.
2. Full decode.
3. Final ASR for 0–10s, CTA, and tail; compare against intended words.
4. Black/freeze/silence detectors and final integrated loudness/true peak.
5. 0–10s full-screen proof audit; speaker face must remain visible.
6. Hook frames at 0.0/0.2/0.6/1.2/1.8/2.5/3.0/5.0/8.0s.
7. Full contact sheet and mobile-scale contact sheet.
8. Bottom-row pixel scan for permanent black bands.
9. Manual review of every hard-cut audio boundary.
10. Complete production docs and Post-Production Retro.

## Risks and Mitigations

- The source is visually podcast-heavy. Mitigation: aggressive active-speaker crop, semantic reframes, partial tool/recovery inserts, and moving data/causal overlays rather than static full-screen cards.
- Both stories use the same source and product. Mitigation: V14A is an absurd-number/product-build story; V14B is a human-consequence/discovery story with different clip order, hook, proof, and lesson.
- `Saved my life` is a source-reported quote, not an independent medical claim. Keep it visibly attributed and avoid claiming Theragun treats or cures a condition.
- The exact company valuation is not required for either story. Avoid unsupported billionaire/valuation framing.
