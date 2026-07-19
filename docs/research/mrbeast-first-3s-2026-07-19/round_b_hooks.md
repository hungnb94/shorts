# Round B — Final Hook Frameworks (HardKnocks vertical, generic, English)

Incorporates Round A judge-panel feedback (avg scores: A2=8.0, A8=8.0, A1/A3=7.0, A4=6.67,
A5/A9=6.33, A7=5.33, A10=4.67, A6=4.0) and 2 techniques confirmed from analyzing a real MrBeast
Short (`XCGVurja73c`, "I Raced The Fastest Man On Earth" — see `REPORT.md`):
1. **Direct Dare Question** (new pattern): hook line phrased as a literal binary/measurable
   question posed to the viewer, resolved only at payoff — not a declarative claim.
2. **Identity-tag overlay**: small animated name+1-line-credential graphic bouncing in ~1.5-2s,
   offloading "who is this and why should I care" off the spoken hook line.
Plus: continuous real motion / overlay-pop-in is a valid cadence substitute for hard cuts.

---

## B1 — Direct Dare Question (Blindspot-native)
**Pattern**: new — Direct Dare Question (MrBeast-confirmed)
- **Visual (t=0)**: subject already mid-motion (walking/gesturing), face clearly visible, no card.
- **VO (spoken, t=0)**: *"Is his fifty-million-dollar net worth real — or made up?"*
- **On-screen**: none at t=0; identity-tag overlay bounces in at ~1.5s: `"VERIFIED: $1.5B COMPANY"` (small, corner).
- **Gap withheld**: the verdict — resolved only at the scorecard/ending.
- **Fix applied**: reframes A6's weak checklist-tease into a real question-to-camera; unblurred face at t=0 (fixes A6's frame-0 fail).

## B2 — Money+Number, Delayed Reveal
**Pattern**: Money+Number (fix of A1)
- **Visual (t=0)**: hard cut into subject's face mid-answer.
- **On-screen (t=0)**: `"$14,..."` — partial number pops instantly, completes to `"$14,000,000/YEAR"` at ~1.5s (not instantly resolved).
- **VO**: *"...and last year alone the company cleared—"*
- **Gap withheld**: full number briefly, then how he got there.
- **Fix applied**: Round A judge flagged A1 as fully resolving the claim at t=0; partial-reveal keeps punch while re-opening a micro-gap.

## B3 — Curiosity Gap, Tightened + In Motion
**Pattern**: Curiosity Gap (fix of A2)
- **Visual (t=0)**: subject pacing/gesturing, continuous motion throughout 0-5s (not a single turn-and-hold).
- **On-screen**: `"THE MISTAKE THAT BROKE HIM"` — cut from 8 words to 5.
- **VO**: *"...and that one decision nearly cost me everything."*
- **Gap withheld**: what "the mistake" was.
- **Fix applied**: judge2 flagged 8-word caption (too long) and no visual change through 5s; shortened + added continuous motion.

## B4 — Contrarian Reveal, In Motion
**Pattern**: Contrarian Reveal (fix of A3)
- **Visual (t=0)**: subject walking toward camera mid-sentence (not a static held eye-contact shot).
- **On-screen**: `"HARD WORK ISN'T WHY HE'S RICH"`
- **VO**: *"Everyone thinks it's about working harder than everyone else. It's not."*
- **Gap withheld**: the real cause.
- **Fix applied**: judge2 flagged A3 as fully static; added motion while keeping the strong contrarian line unchanged (it scored well on lens 1 and 3).

## B5 — Live-Approach, Text-Free at t=0 (MrBeast-validated)
**Pattern**: Live-Approach
- **Visual (t=0)**: handheld camera moving toward subject, real interruption, subject turns mid-stride. NO caption at t=0 — matches MrBeast's own hook, which also has zero on-screen text in the first ~1.5s and relies entirely on real motion + spoken dialogue.
- **VO**: host, off-camera: *"Sir, real quick — how much is that watch?"*
- **On-screen**: identity-tag overlay bounces in at ~2s if subject isn't independently recognizable: `"OWNS A $1.5B COMPANY"` (credential, not the hook claim itself).
- **Gap withheld**: subject's reaction/answer and why it matters.
- **Fix applied**: Round A judge2 penalized A4 for delaying text to ~1s — MrBeast's own real example has NO text that early either, so the fix is to stop treating "text by t=0.2s" as mandatory when real motion+audio already carries the hook, and use the identity-tag (not a claim caption) for the first overlay instead.

## B6 — Implied Comparison, Concrete Stake
**Pattern**: Implied Comparison (fix of A5)
- **Visual (t=0)**: subject answering on camera, ordinary setting.
- **On-screen**: `"OTHERS SAID A $2M BUSINESS WAS IMPOSSIBLE"` — names a concrete number now (fix), still labels only one side.
- **VO**: *"People told me this would never work."*
- **Gap withheld**: the "...vs THIS ONE" payoff, arriving later per the pattern's confirmed ~30-40s tolerance.
- **Fix applied**: judge1 flagged the original as too vague/qualitative; added a real number to the "others" side while preserving the pattern's core mechanic.

## B7 — Number-Then-Correction (kept, minor cadence bump)
**Pattern**: Money+Number + Contrarian hybrid (A8 scored 8.0 avg, highest of Round A)
- **Visual (t=0)**: bold number overlay over subject's still-visible face; add a subtle push-in/zoom during the correction beat (per judge2's optional note) instead of a static hold.
- **On-screen**: `"$50,000,000"` -> strikethrough at ~1.5s -> `"...ACTUALLY $200,000,000"`
- **VO**: *"Everyone quotes the wrong number."*
- **Gap withheld**: why the real number is different.
- **Fix applied**: essentially unchanged (highest scorer); added a small zoom for the one soft cadence note raised.

## B8 — Blindspot Scorecard as Direct Dare Question
**Pattern**: new — Direct Dare Question applied to the Blindspot Verification sub-format (2nd instantiation, building pattern confidence per ADR-0031's multi-sample bar)
- **Visual (t=0)**: subject's unblurred face, already talking, no blur/freeze-frame (fixes A6's frame-0 violation).
- **VO**: narrator, direct question: *"Does he really have wealth, freedom, AND legacy — or is one of these fake?"*
- **On-screen**: identity-tag-style overlay bounces in ~1.5-2s: `"1 / 2 / 3 — SCORE: ?"` (small, corner, not a long static list).
- **Gap withheld**: the score — resolved only at the end.
- **Fix applied**: A6 scored 4.0 avg (worst of Round A) — blurred-face frame-0 violation and a long 3-item static caption. Rewritten as a genuine spoken question (MrBeast mechanic) with a compact tag graphic instead of a paragraph-length overlay.

## B9 — Direct Dare Question, Multi-Subject
**Pattern**: new — Direct Dare Question (3rd instantiation)
- **Visual (t=0)**: 3 quick face-cuts (0.3s each) of 3 different subjects — continuous fast motion, no freeze/hold at t=0.
- **VO (spoken at t=0, not delayed)**: *"Can you guess which of these three billionaires lied?"*
- **On-screen**: `"ONE LIED"` lands simultaneously with the VO at t=0 (not waiting for a freeze frame).
- **Gap withheld**: which one, and what the lie was.
- **Fix applied**: A9 (avg 6.33) lost points because the caption only landed on the freeze at ~0.9s and the premise felt vague/gimmicky per the pattern-fit judge; moving the question to spoken VO synced at t=0 (MrBeast's exact mechanic) removes the delay and grounds it in a now-confirmed pattern instead of an invented one.

## B10 — Physical-Prop Reveal, Split Cause/Effect
**Pattern**: new — object-first cold open (fix of A10)
- **Visual (t=0)**: extreme close-up on an object (car key fob), whip-pan reveals subject's face at ~0.8-1.2s.
- **On-screen (t=0)**: `"THIS UNLOCKS SOMETHING WORTH MILLIONS"` — vague on the specific figure (fix).
- **On-screen (~6s, body)**: `"$2M GARAGE"` — specific number arrives only in the body, not co-named with the object at t=0.
- **VO**: subject, already talking as pull-back happens: *"...so this one right here—"*
- **Gap withheld**: the full story AND the specific dollar figure (previously both were given away together).
- **Fix applied**: judge1 flagged A10 for co-naming cause ("this key") and effect ("$2M garage") in one breath — split them across the hook window.
