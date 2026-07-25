# hardknocks_v2 — "3 Billionaires Say Money = Happiness... This One Didn't Agree"

## Status
| Field | Value |
|-------|-------|
| YouTube Video ID | [d6HLNU4krEw](https://youtube.com/watch?v=d6HLNU4krEw) |
| Rendered | 2026-07-11 |
| Metrics fetch after (48h rule) | 2026-07-13 13:43 +07 |
| Metrics status | Fetched 2026-07-13 |

## Video Specs
- Duration: 50.5s (extended from an initial 40.6s per user request — see Source/Known Issues below)
- Resolution: 1080x1920 (9:16 portrait)
- Codec: H.264 (libx264, crf 18), 30fps
- Audio: AAC, 192kbps, 48kHz, stereo (1 stream, verified via ffprobe)
- File: `output/projects/hardknocks/final/2026-07-11-hardknocks_v2_implied_comparison.mp4` (28.4MB)
- Metadata (title/description, ready for manual upload): `output/projects/hardknocks/final/2026-07-11-hardknocks_v2_implied_comparison_metadata.txt`
- Render script: `pipeline/hardknocks/render_hardknocks_v2.py`

## YouTube Title
3 Billionaires Say Money = Happiness... This One Didn't Agree

## YouTube Description
```
I asked billionaires the one question that matters more than "how did you get rich" — are you actually happy?

Three of them gave the answer everyone expects. Then one of them explained why that answer is missing the point entirely — and what he thinks actually matters more than the number in your bank account.

Stick around for the answer that never makes it into the highlight reel.

What's your definition of "made it"? Drop it below.

#billionaire #wealth #richmindset #entrepreneur #shorts
```

## Source
- Channel: School of Hard Knocks (same Source Channel as `pipeline/hardknocks/render_hardknocks_v1.py`, ADR-0001/0004/0007)
- Source video ID: `dK5bG5ZE3yI` — "Asking Billionaires If Getting Rich Was Worth It", uploaded 2026-03-13, 1491.5s (~24:52), 3840x2160 (4K), street-interview format across 4 different billionaires (Lance/Body Armor, John/UK mobile phones, Scooter Braun/entertainment, an unnamed Vegas private-equity investor)
- First use of this exact video ID in the repo — checked against `data/source_videos.csv` before selection (new registry, see AGENTS.md/WORKFLOW.md change in this same batch of work). Same channel as `hardknocks_v1`, but a different source video and different interview subjects — no segment/subject overlap with `hardknocks_lawnmower_v1` (`KxoKCNCLOss`).
- Footage used: 12 non-contiguous pieces spanning source timestamps 99.3s-1428.2s, ~53.2s of edited output (raw, pre-speed-up) from a 1491.5s source — well under the ADR-0007 50% ceiling. Every individual piece <15s (largest is 12.12s). Piece 7 (`p3_scooter`, 971.48-981.14s) was added after the first render to extend the video toward the ~50s target using more of Scooter Braun's own reveal/payoff content, not filler.

## Why This Segment
**Multi-Clip Mashup** (ADR-0022) — the moments that make this comparison work (host's framing question, 3 different billionaires' quick "happy" answers, Scooter Braun's much longer reveal, John's fuller elaboration, 2 closing lines) are scattered from 99s to 1428s of a 24:52 source; no single 45-60s window contains all of them.

This is the first video in the repo to test the **genuine multi-source-interview form** of the "Implied Comparison" hook pattern proposed in `docs/research/800m-view-case-study-2026-07-11/REPORT.md` (section 5, the RandomDude 808M-view case study): several quick "OTHERS say X" examples, cut together, pivoting to "THIS ONE said Y" held much longer. `bacsihai_v6` (`docs/production/bacsihai-v6-vitamin-d-hormone.md`) applied the same pattern's *name* first, but on a single source split into 2 pieces — not genuinely different people. Here the "others" (Lance, John, the PE investor) and "this one" (Scooter Braun) are real, different interview subjects from the same source video, matching the report's proposed structure much more literally. This is the "small experiment tied to recent research" for this production cycle.

Transcript-driven selection: all 12 pieces were chosen from the mlx_whisper word-timestamped transcript (`output/projects/hardknocks/source/dK5bG5ZE3yI_transcript.json`), each cut to exact word boundaries — verified zero internal gaps >0.3s within any piece (see Known Issues / pause-trim note below).

## Hook Formula Applied
- **Frame-0 face/action** (ADR-0017): cold open on the host talking directly to camera (tight/close shot), not a title card — verified via frame extraction (`/tmp/hk2_frames/f_99.5.jpg` at the time of production).
- **Gap-not-resolved**: opening line is the host's own real question ("So let's go find out if money can actually buy happiness") — poses the question, states no answer. Full Hook Gate checklist run and passed; see Known Issues for the one item needing a script-level fix (cadence).
- **Cause+effect not co-named**: neither the on-screen hook line nor the YouTube title states a specific mechanism + specific outcome together — both stay at the "is it true?" level.
- **Payoff timing**: the real reveal (Scooter Braun's answer) begins at t=7.06s of the edited timeline (raw, before the 1.06x speed-up — final ~t=6.66s), inside the ~5-10s window (AGENTS.md/bacsihai-v5 pitfall).
- **Caption sync (ADR-0018)**: this source's own burned-in, word-synced yellow captions are kept as-is (frame-verified present and legible throughout every chosen piece) — same approach as `hardknocks_v1`.
- **Cadence (ADR-0016/0018)**: cuts land at 2.68s/3.84s/5.36s inside the montage; the 2.68s host solo shot (the one span that would otherwise run without a cut) gets continuous motion via `zoompan` (same filter as `render_hardknocks_v1.py`) — this alone satisfies Stage 0 item 6, so the hook text overlay does not need to be delayed to manufacture a cadence beat (see correction below).
- **Hook text overlay timing/size (corrected after user review, then enlarged four times total across follow-up requests)**: the first render placed "OTHERS SAY GETTING RICH MADE THEM HAPPY..." at t=1.3s, size=36 — too small and too late to hold attention immediately. Round 1 fix: text now appears at t=0.1s (matching ADR-0018's t=0.2s source-caption standard, now applied to added overlays too), shortened to "OTHERS SAY MONEY = HAPPY..." and enlarged to size=52. Round 2: user asked for bigger still — bumped to size=64 (main hook line), STAT_CARDS to 36, COUNTER_ARGUMENT to 32, CTA to 40. Round 3: user flagged the header text still looked small relative to the frame — frame inspection showed "OTHERS SAY MONEY = HAPPY..." at size=64 was already running edge-to-edge at 1080px (couldn't grow further without clipping), while the shorter strings (pivot line, stat cards, counter-argument, CTA) still had large unused margins. Fix: shortened the OTHERS line to "OTHERS: MONEY = HAPPY" (27->21 chars), raised STRUCTURE_CAPTIONS to size=80, STAT_CARDS to 54, COUNTER_ARGUMENT to 52 (text shortened to "COUNTER: NOT THE FULL STORY"), CTA to 50 (text shortened to "REAL WEALTH = KNOWING YOURSELF"); y-positions adjusted (hook/counter/CTA to y=60, stat cards to y=250). Round 4: user asked to increase once more — tightened OTHERS text further to "OTHERS: MONEY=HAPPY" (21->19 chars) and pushed STRUCTURE_CAPTIONS to size=90; frame check caught this as an overcorrection — the string clipped at BOTH edges (zero margin, text ran off-frame) — backed off to size=84, which frame-verified clean. Same overshoot risk hit COUNTER_ARGUMENT (60 was borderline/near-clipping) — backed off to size=56. STAT_CARDS raised to 64 and CTA held at 56, both frame-verified with healthy margin; stat-card y nudged to 260 for clearance under the taller hook line. Frame-verified across all four rounds, with round 4 specifically re-checking every element at t=0.3/2.6/8.5/32.0/47.5 after the overcorrection — final sizes: STRUCTURE_CAPTIONS=84, STAT_CARDS=64, COUNTER_ARGUMENT=56, CTA=56, all filling most of the 1080px width without clipping. Lesson generalized to memory: the ~48-52px reference is a floor, not a target; shortening overlay copy is often the only way to grow size once a string already spans the frame; and each size bump must be re-verified by frame extraction rather than assumed safe by extrapolating from the previous round's margin, since a bigger size *and* a shorter string can still net out to clipping if pushed too far in one step.
- **Claim-strength flag** (non-blocking, docs/research/hook-benchmarks-2026-07/REPORT.md): the opening hook is qualitative ("does money buy happiness?"), not a Money+Number hook — logged as expected; the specific dollar figures appear later via the data_viz_overlay stat cards, not in the hook line itself.

## Value-Adds (Transformative Gate, ADR-0007 — min 2 required, must be distinct categories)
1. **data_viz_overlay** — stat cards during the OTHERS montage and pivot: "$5B SOLD TO COCA-COLA" (Lance), "$1.5B EXIT (UK)" (John), "$1.6B NET WORTH" (PE investor), "$1B+ EXIT" (Scooter Braun).
2. **counter_argument** — "COUNTER: NOT THE FULL STORY" overlay during the reinforcement section (John's fuller elaboration), naming the reveal explicitly rather than leaving it implicit. (Shortened from "COUNTER: THE 'HAPPY' ANSWER ISN'T THE FULL STORY" to allow a larger fontsize — see Hook Formula Applied.)

The "OTHERS:.../THIS ONE SAID..." labels are the hook/structure device itself, not counted toward the 2 required value-adds (matches this plan's design decision, distinct from how the comparison label was scoped in bacsihai_v6).

Commentary track: the structure captions above + closing CTA ("REAL WEALTH = KNOWING YOURSELF", drawn from Scooter Braun's own words, shortened from "...KNOWING WHO YOU ARE" for size) satisfy ADR-0007 gate item 1.

## Known Issues
- **Resolved**: the first cut landed at 40.6s, below the 45-60s convention in `docs/WORKFLOW.md` Stage 2. Rather than pad with tangential source material (e.g. a cycling-race anecdote unrelated to the happiness thesis) purely to hit a duration target, the fix was to find MORE of Scooter Braun's own authentic reveal content (`p3_scooter`, 971.48-981.14s — his concrete "tip"/takeaway, still on-thesis) and add it as a 12th piece, then tune `SPEED` down from 1.08x to 1.06x. Final duration: 50.5s — within convention, no padding used. See Workflow Delta below for how this changes the open question raised in the first pass.
- **Pause-trimming (AGENTS.md base-quality Retention Technique) was a no-op for this video** — checked programmatically: zero internal word-gaps >0.3s in any of the 12 chosen pieces, because each piece was already selected at exact word boundaries during transcript review. The mandatory uniform speed-up (1.06x, tuned down from the usual 1.1x since Scooter Braun's payoff is dense reflective speech, and tuned again from 1.08x once the 12th piece was added) was still applied per the base-quality rule.
- Two pieces (`o2_john` and `t2_john`) are adjacent, non-overlapping continuations of the same source moment (534.44-535.96 then 535.96-540.26) — a deliberate "cut the quote short, come back for the rest later" device mirroring the video's own hook structure at the individual-clip level, not a duplicate-footage mistake.

## What To Check At 48h
- AVD / Stayed % vs. `hardknocks_lawnmower_v1` (`dHDpDXSIAkA`, same channel/vertical, Contiguous VO sub-format) and `bacsihai_v6` (`EpTPDrWONS0`, single-source Implied-Comparison-by-name) — this is the direct comparison point for whether genuine multi-source Implied Comparison outperforms both.
- Retention graph shape at the pivot point (~7s raw / ~6.7s post-speed-up, the "THIS ONE SAID..." cut into Scooter Braun) — does retention hold or spike here, confirming the pivot itself is the strong beat the research report predicted?
- Retention through the extended Scooter Braun payoff (~t=6.7-21.3s post-speed-up, now including `p3_scooter`) — does the added content sustain the pivot's momentum or dilute it?
- Retention during the reinforcement section (John's fuller answer, ~t=30-44s post-speed-up, shifted later by the `p3_scooter` insert) — this is the longest uninterrupted single-topic stretch; check whether it's where viewers drop off (would suggest the reinforcement beat runs too long) vs. holds (would validate the "second real example" design choice).
- Comment themes — per the hook-benchmarks comment-psychology research, watch for "circular logic" mockery vs. genuine engagement with the "money isn't the full answer" reveal.

## Post-Production Retro

### Hook Retro
- Verbal: none found beyond the fix already applied — the host's own real question ("let's go find out if money can actually buy happiness") is stronger than anything scripted from scratch would be, and using real footage for the hook line (rather than a text-only card) was itself an improvement over `hardknocks_v1`'s approach.
- Visual: **found and fixed, four times** — user review of the first render caught that the added hook text overlay ("OTHERS SAY...") appeared too late (t=1.3s, delayed on purpose to manufacture a cadence beat) and was too small (size=36) to grab attention immediately. Round 1: corrected to t=0.1s / size=52 / shortened text. Round 2: user asked for bigger still — bumped to size=64, verified via frame extraction that it still fit 1080px without clipping. Round 3: user flagged the header text still looked too small relative to the frame overall — turned out "OTHERS SAY MONEY = HAPPY..." at size=64 was already edge-to-edge (the binding constraint), while the pivot line/stat cards/counter-argument/CTA had large unused margins. Fix: shortened the OTHERS copy to buy width headroom, then raised every header element's size (80/54/52/50) and re-verified via frames at 5 different timestamps. Round 4: user asked to increase once more — this time the first attempt (tighten text further + size=90/60) overshot and frame-verification caught real clipping (text running off both edges) on the OTHERS line, backed off to size=84 (and 56 for counter-argument), re-verified clean. Generalized immediately: added explicit hook-text timing/size requirements to `docs/WORKFLOW.md` Stage 3, plus a mandatory visual self-check step in Stage 4, plus a new note that each size increase must be independently frame-verified rather than assumed safe from the previous round's margin. Four rounds of feedback on the same lever (size) confirms the ~48-52px "minimum" reference in WORKFLOW.md/memory is a floor, not a target, and that shortening overlay copy — not just raising the fontsize number — is often the actual lever once a string already spans the frame width, though that lever also has a limit that must be checked visually, not assumed.
- One idea for a future iteration (not yet applied): the source has 4 interview locations (backyard, Beverly Hills storefront, a stone-wall exterior, Las Vegas casino) — a future video could lean harder into location-hopping as its own visual-variety device across the OTHERS montage, rather than incidental.
- Did not run the `viral-video-analysis` skill against a comparison video for this retro (no metrics yet to compare against — will fold into the 48h check instead, alongside the direct in-repo comparisons listed above).

### Workflow Delta
Yes - five cases not fully covered by the current docs, handled inline rather than deferred:
1. **New process, not a new rule**: added a source-video dedup registry (`data/source_videos.csv`) plus a check/append step in `docs/WORKFLOW.md` Stage 1, so future videos can check whether a source video (or its channel) was already used before re-selecting it. Done as a WORKFLOW.md edit, not a new ADR (lightweight tooling convention, not a strategic decision — same weight class as the pause-trimming Retention Technique note in AGENTS.md).
2. **Resolved**: the open question from the first pass — whether the 45-60s convention (`docs/WORKFLOW.md` Stage 2) is a hard floor to pad toward, when the source material's tightest honest cut undershoots it — was answered concretely here, not by a new rule but by direct user request: extend using MORE authentic on-thesis content from the same speaker (`p3_scooter`) rather than padding with tangential material. This confirms the WORKFLOW.md convention should stay a target to search harder for real content against, not a padding trigger — no doc change needed, the existing "don't pad" principle already covered this once more source material was found.
3. **Rule gap, now fixed**: `docs/WORKFLOW.md`'s existing caption-sync/cadence checks (Stage 0 item 5-6, ADR-0018) only ever addressed the *source's own* burned-in captions, never the hook text overlays this project adds on top. That gap let the first render of this video ship a delayed, undersized hook overlay. Fixed by adding explicit timing/size requirements to Stage 3 and a mandatory visual self-check to Stage 4 (see `docs/WORKFLOW.md` diff) — applies to every future video, not just this one.
4. **Rule gap, now fixed**: neither `docs/WORKFLOW.md` nor the hook-text memory said what to do when a caption string is already at the frame-width limit and still needs to look bigger. Added a line to `docs/WORKFLOW.md` Stage 3: when enlarging overlay text would clip within 1080px, shorten the copy first rather than treating the current size as a ceiling - verify the new size still fits via the same frame-extraction self-check, don't assume from character count alone.
5. **Rule gap, now fixed**: round 4's first attempt (shorten text + jump size 80->90 in one step) overshot and produced real edge-to-edge clipping, even though it looked safe by character-count estimate carried over from round 3's margin. There was no rule saying each size change needs its own frame check rather than being extrapolated from a prior round's measured margin. Folded into the same Stage 3 addition as item 4: verify by frame extraction after every size change, not just the first time a given overlay's size is touched.

## Retention Analysis
_Auto-generated by the fetch-metrics skill, 2026-07-13. Full per-second curve:
`output/projects/hardknocks/final/d6HLNU4krEw-retention.csv`._

- **Views**: 16 · **AVD**: 0:37 (73.14% of 50.5s) · **CTR**: not available via API (confirmed, see ADR-0025)
- **Key moments**: none returned — the per-second retention curve came back empty, likely below YouTube Analytics' minimum sample-size threshold for reporting `audienceWatchRatio` at only 16 views. Re-fetch once view count grows to see if the curve populates.

**UNCONFIRMED vs real Studio (2026-07-13, revised)**: this 73.14% came only from the API's
`averageViewPercentage`, never cross-checked against a real Studio screenshot for this specific
video (also noisy regardless, only 16 views). A 3rd cross-check (`Mw7jeR6R6iE`) showed the
API/Studio gap flips direction and magnitude per video (+6.0pp, +5.74pp, then -6.86pp) — there is
no reliable fixed correction factor, so no estimate is given here (an earlier version of this note
guessed "~67-68%," assuming a fixed bias that's now disproven — retracted). Root cause is not a
code bug (verified by reading `src/platforms/youtube-analytics.ts`) but a genuine metric-family
mismatch — see ADR-0025's 2026-07-13 2nd addendum. Do not treat 73.14% as ground truth until a
real Studio screenshot is provided (see the fetch-metrics skill's Studio Cross-Check Correction
section).
