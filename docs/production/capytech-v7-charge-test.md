# Capytech V7 — Charge Test Production Record

## Status

**LOCAL EXACT-FINAL COMPLETE — MEDIA QC PASS — METADATA PASS — UPLOAD QUEUED.**

This artifact removes the known structural failures in V6, but no creative can honestly guarantee one million views. The high-confidence claim is narrower: V7 is source-faithful to Capybluh's long repeated-test engine, passes the measured local gates, and is ready for an external cold-viewer check. Publication remains blocked by ADR-0035 lane eligibility and unresolved Studio wiring.

| Field | Exact-final value |
|---|---|
| Artifact | `output/projects/capytech/final/2026-07-29-capytech_v7_charge_test.mp4` |
| SHA-256 | `5e2acf6ae4e23ea20be934d520e0fa6cf163bc97ce2925b38ef49dd66391e1b5` |
| File size | `13,944,272 bytes` |
| Duration | `52.000s` |
| Video | H.264 High, level 4.2, 1080×1920, 30fps CFR, yuv420p |
| Audio | AAC-LC stereo, 48kHz, 182kbps |
| Loudness | `-15.98 LUFS`, `-2.27 dBTP`, `3.6 LU LRA` |
| Speech | None; raw Whisper output is rejected as music/SFX hallucination |
| Renderer | `pipeline/capytech/render_capytech_v7_charge_test.py` |
| Verifier | `pipeline/capytech/verify_capytech_v7_charge_test.py` |
| Storyboard | `output/projects/capytech/scripts/capytech_v7_charge_test_storyboard.json` |
| QC | `output/projects/capytech/analysis/v7_charge_test_qc/final_qc.json` |

## Backward Strategy

### 1. Define the controllable win

The upload cannot be guaranteed to reach one million views. The controllable objective is:

- make the experiment understandable before the title is read;
- begin a physical action inside 0.3s;
- use one object, one action, one changing scalar and one fixed stage;
- provide a visible result and reaction in every round;
- keep every later round more consequential than the previous round;
- close the final state back into frame zero;
- verify that the public upload matches the local master before judging creative performance.

The primary metric objective remains `Swiped Away <20%`. It must be measured in Studio after publication; it is not inferable from this local master.

### 2. Select the source-native long architecture

V6 stretched a source format whose median duration was about 18s into a 48s video. V7 instead copies Capybluh's proven long repeated-test family:

`same phone + same cable + same plug-in action + charging time increases`

Tracker:

`1s → 1m → 10m → 1h`

Visible outcome:

`1%→2% → 1%→15% → 1%→100% → overcharge/swelling/lift/pop`

### 3. Pick the hook by mechanism, not spectacle

| Candidate | Curiosity | Specificity | Visual | Emotion | Payoff | Novelty | Total /60 | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Tracker + 1% phone + plug already moving | 9 | 10 | 9 | 7 | 10 | 8 | **53** | Selected |
| Giant-phone flash-forward | 8 | 8 | 10 | 9 | 5 | 9 | 49 | Reject: reveals payoff |
| `DO NOT CHARGE 1 HOUR` warning | 8 | 9 | 6 | 8 | 9 | 7 | 47 | Reject: text-first |
| Portal/countdown intro | 7 | 8 | 8 | 8 | 7 | 6 | 44 | Reject: repeats V6 delay |
| Split-screen all outcomes | 4 | 10 | 9 | 7 | 6 | 7 | 43 | Reject: closes curiosity gap |

The selected frame zero exposes the phone at `1%`, all four time stages and the hand–plug–cable action without a separate intro.

### 4. Lock the repeated verb and scalar

- Central object: one phone.
- Repeated verb: plug in the same cable.
- Scalar: charging duration only.
- Fixed context: one lab, one table, one camera.
- Character role: act, wait, read result, react.

No portals, era cards, adapter stacks, scanners, dual meters or unrelated subplots are introduced.

### 5. Escalate action → result → reaction

| Round | Time | Action | Result | Reaction/payoff |
|---|---:|---|---|---|
| 1s | 0–8.5s | Plug in | `+1%` | Disappointment |
| 1m | 8.5–19s | Same plug-in | `+14%` | Hope |
| 10m | 19–31.5s | Same plug-in | `FULL!` | Celebration, heat begins |
| 1h | 31.5–49.8s | Same plug-in | 100%, overcharge | Phone swells, lifts mascot, pops |
| Loop | 49.8–52s | Reset plug-in | Back to 1% | Returns to frame-zero contract |

### 6. Make semantic progress continuous

The first render exposed a second-order risk: a fixed camera can be source-faithful but read as static if only the percentage changes. The final adds a post-render semantic layer rather than decorative motion:

- an elapsed-time rail grows under the active stage;
- a charge pulse travels physically along the cable while connected;
- result bursts show `+1%`, `+14%` and `FULL!`;
- result animation never introduces a second rule.

Exact-final hook motion at 10fps sampling:

- median mean-luma delta: `0.52999`;
- minimum: `0.20109`;
- calibrated `freezedetect=-60dB:d=1.0`: zero events.

### 7. Preserve source-like visual simplicity

- Fixed 2.5D camera and stage.
- Stylized 3D capybara, phone, cable and table generated deterministically in Blender.
- No AI-shot continuity changes.
- Hand, cable, plug and phone share one physical line.
- Result text uses the licensed Komika Axis font.
- A compact moving watermark remains non-obstructive.

### 8. Use event-bound original audio

The audio is procedural and contains no source sample, narration or TTS. It includes:

- early charging/plug SFX inside the first second;
- stage stingers at each reset;
- incremental ticks and charging pulses;
- heat, swelling, lift and pop events;
- a loop reset cue.

Encoded exact-final loudness passes `-15.98 LUFS / -2.27 dBTP`.

### 9. Keep the CTA diegetic

A compact Like / Subscribe / Comment rail appears during the already-moving 1h escalation around 38–42s. It does not pause the test or replace the payoff.

Because this package is `Not made for kids`, the Comment CTA is operationally consistent. The final audience decision must still be verified in Studio.

### 10. Close the loop

The swelling phone pops, debris resolves, the phone returns to `1%`, the mascot returns to the table and the active tracker returns to `1s`. The last beat begins the same plug-in action visible at frame zero.

## Exact-Final QC

All automated and manual exact-final gates pass:

- duration, dimensions, codecs, CFR and pixel format;
- full decode with no errors;
- zero black, calibrated freeze or silence events;
- integrated loudness, true peak and LRA;
- no black footer;
- frame-zero visual richness and measured hook motion;
- fresh hook, critical-frame and full contact-sheet evidence;
- manual review of hook, result labels, CTA, swelling, lift, pop and loop;
- metadata package validation.

### ASR assessment

Whisper emitted two raw segments dominated by the token `static`:

- segment 1 compression ratio `40.84`, dominant-token ratio `98.65%`;
- segment 2 compression ratio `27.54`, dominant-token ratio `97.30%`.

These are classified as music/SFX hallucinations, not speech. The audio provenance confirms that `synth_audio()` only uses oscillators and noise; it has no voice, TTS, sample or dialogue input.

## Canonical Upload Package

### Title

`Charge Test: 1s vs 1h 🔋😵`

- 24 visible Unicode code points.
- Exactly two relevant emoji.
- Under the 30-character mobile target.

### Description

```text
Charge Test: 1s vs 1h 🔋😵

The same phone and cable face four charging times—and one very bad idea.

#shorts #PhoneCharging #VisualComedy
```

### Visible hashtags

1. `#shorts`
2. `#PhoneCharging`
3. `#VisualComedy`

### YouTube Studio tags

1. `phone charging`
2. `visual comedy`
3. `capybara animation`

### Studio fields

- Audience: `Not made for kids`
- Video Language: `English (United States)`
- Location: `United States`
- Category: `Science & Technology`
- Synthetic/altered content: `Yes — fully computer-generated 3D animation and procedural audio`
- Playlist: `BLOCKED — exact ZapBara master playlist ID is not configured`
- Related Video: `BLOCKED — ZapBara has no validated current winner`
- Upload Details Template: `BLOCKED — approved template name/ID is not recorded`
- Raw affiliate link: none

## Publication Gate

Do not upload yet.

1. Confirm the previous ZapBara Short `hkxEmwLKAOw` has reached Distribution Plateau under ADR-0035.
2. Confirm ZapBara is the next eligible strict-round-robin lane.
3. Record five external naive-viewer Hook Gate responses; require at least four to identify `phone + charging test + increasing time` from frame zero without the title.
4. Configure the exact ZapBara master playlist ID.
5. Resolve Related Video and Upload Details Template.
6. Upload the exact SHA-256 artifact above; do not re-export it in another editor.

## Post-Upload Parity Gate

Before evaluating performance:

1. Download the public transcode.
2. Verify public duration is within `0.10s` of `52.000s`.
3. Verify frame zero, each result and the 49–52s loop remain present.
4. Compare public/local audio after alignment; ordinary AAC transcode should remain strongly correlated.
5. Verify title, description, exactly three hashtags, Studio tags, audience, category, playlist and Related Video.

If parity fails, diagnose the upload pipeline before changing the creative.

## 48h+ Learning Loop

Never fetch before 48 hours.

| Evidence | Interpretation | Next action |
|---|---|---|
| Shown in feed near zero | Creative was not meaningfully tested | Investigate lane/channel/distribution; preserve the upload |
| Feed exposure exists, Swiped Away >20% | Frame-zero/topic/audience match failed | Research more source hooks; materially revise the first action |
| Drop at 8.5–19s | 1m result is too weak or too slow | Increase physical result, not decorative cuts |
| Drop at 19–31.5s | 10m escalation is predictable | Move visible heat/swell evidence earlier |
| Drop at 38–42s | CTA cost exceeds its value | Compress/relocate the diegetic CTA |
| Completion good, replay weak | Loop reset is not seamless enough | Match the final pose/charge pulse more tightly to frame zero |
| Strong hook and completion, low scale | Topic ceiling/channel history | Reuse the engine with a broader sensory object; do not abandon the format |

Failure must produce a lesson, expert/source research, a strategy change and a material revision—not a blind re-upload.

## Rights and Cost

- Blender geometry, procedural animation, compositing, music and SFX: created locally.
- Komika Axis: repository font and license used.
- Paid generation cost: `$0`.
- No third-party footage or affiliate link.
