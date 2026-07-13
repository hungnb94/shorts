# hardknocks_v4 — "He Trades $1 Billion A Day On Wall Street... But This Is What Actually Kept Him Going"

## Status
| Field | Value |
|-------|-------|
| YouTube Video ID | Not yet uploaded |
| Rendered | 2026-07-13 |
| Metrics fetch after (48h rule) | Recompute once uploaded |
| Metrics status | Not yet fetched, not yet uploaded |

## Video Specs
- Duration: 48.7s (raw cut 49.9s, 1.03x speed-up — mild, since the raw cut already landed at the ~50s target)
- Resolution: 1080x1920 (9:16 portrait)
- Codec: H.264 (libx264, crf 18), 30fps
- Audio: AAC, 192kbps, 48kHz, stereo (1 stream, verified via ffprobe)
- File: `output/projects/hardknocks/final/2026-07-13-hardknocks_v4_wall_street_legend.mp4` (40.6MB)
- Metadata (title/description, ready for manual upload): `output/projects/hardknocks/final/2026-07-13-hardknocks_v4_wall_street_legend_metadata.txt`
- Render script: `pipeline/hardknocks/render_hardknocks_v4.py`

## YouTube Title
He Trades $1 Billion A Day On Wall Street... But This Is What Actually Kept Him Going

## YouTube Description
```
I asked the most famous stockbroker on Wall Street how he got rich. He's traded up to a billion dollars of stock a day, for 40 years straight.

Then I asked if he'd ever been broke. What followed wasn't the answer I expected — years of real hardship, and more adversity than most people will ever face.

What kept him going wasn't the money. Stick around for his answer on what money actually buys you.

What's the hardest thing you've ever had to push through? Let me know below.

#wallstreet #stockmarket #entrepreneur #shorts
```

## Source
- Channel: School of Hard Knocks (4th source from this channel — see `data/source_videos.csv`; same channel as `render_hardknocks_v1/v2/v3.py`, ADR-0001/0004/0007).
- Source video ID: `AATw4YRFSw8` — "Asking Wall Street Moguls How They Got Rich!", uploaded 2026-10-30, 1242.9s (~20:43), 3840x2160 (4K), street-interview format outside the NYSE.
- First use of this exact video ID — checked against `data/source_videos.csv` before selection.
- Footage used: 8 non-contiguous pieces spanning source timestamps 845.62s-1197.92s, ~49.9s of edited output (raw, pre-speed-up) from a 1242.9s source — well under the ADR-0007 50% ceiling. Every individual piece <15s (largest is 9.3s).
- Subject: Peter Tuchman, a real NYSE floor broker (identified by name at source timestamp 1032.8s), described in-video as "the longest standing broker in the world, the most famous stockbroker in the world."

## Why This Segment
**Multi-Clip Mashup** (ADR-0022) — the pieces that make this work (his Money+Number HOOK stat, the PIVOT into real hardship, and his closing wisdom) are scattered from 845.6s to 1197.9s of a 20:43 source; no single 45-60s window contains them all.

This is the **same-person-callback Implied Comparison** device (CONTEXT.md → Source Channel Pattern / Implied Comparison Hook), same structural device as `hardknocks_v3` (`docs/production/hardknocks-v3-believe-in-god.md`) — but the pivot payoff here is a real personal tragedy rather than a belief. Peter Tuchman's own confident HOOK answers ("most famous stockbroker in the world," trades $0.5-1B of stock/day) give no hint of what's coming; the PIVOT, triggered by the interviewer's own follow-up question ("Have you ever been broke before?"), reveals a genuinely surprising depth: years of real financial hardship (2006-08), and — far more recently — the loss of his wife and his own near-fatal bout with COVID. The RESOLUTION/TEACH section closes on his own stated reason for continuing ("I love what I do") and his closing financial wisdom ("money buys freedom, not happiness").

**Tone decision** (explicit user decision via `/grill-with-docs` grilling session, before any cutting): **resilience-first**. The tragedy is real, stays in his own verbatim audio, and is not cut or softened — removing it would be dishonest to his story. But nothing in the overlay layer (structure caption, comparison card, or keyword-emphasis coloring) names the specific tragedy ("wife died," "COVID," "three months to live") as the attention-grabbing hook; those words are deliberately left in the plain base caption color with no size/color emphasis. Only the resilience/wisdom payoff words (love, freedom, kept, going, share, found, understand) get the keyword treatment. See Hook Formula Applied and Value-Adds below for the concrete implementation, and Known Issues for two bugs caught by the mandatory frame-check while implementing it. Scoped to this video only, by explicit user decision — not generalized into a project-wide ADR.

Transcript-driven selection: all 8 pieces were chosen from the mlx_whisper word-timestamped transcript (`output/projects/hardknocks/source/AATw4YRFSw8_transcript.json`), each cut to exact word boundaries.

## Hook Formula Applied
- **Frame-0 face/action** (ADR-0017): cold open on two real faces in medium shot outside the NYSE (Peter Tuchman speaking, interviewer holding mic) — not a title card. Verified via frame extraction at the piece's source timestamp (845.62s) before cutting, plus post-render frame-check at t=0.1s.
- **Gap-not-resolved**: the HOOK only establishes his stature and trading volume — it gives no indication that a follow-up question is about to reveal a personal tragedy. Full Hook Gate checklist run and passed (all 7 items) before any cutting began.
- **Cause+effect not co-named**: neither the hook overlay nor the YouTube title asserts a causal mechanism between his hardship and his success — both stay at "what happened," not "why it made him rich."
- **Payoff timing**: the pivot question ("Have you ever been broke before?") lands at the start of piece 3, edited-timeline t≈10.9s raw (t≈10.6s post-speed-up) — right at the front edge of the ~5-10s target, appropriate since the HOOK here is only two short pieces (~10.9s total).
- **Caption sync (ADR-0018)**: self-authored `drawtext` captions, word-synced from the mlx_whisper transcript, auto-split into 2-4 word bursts (see Known Issues for why this video used an auto-split helper instead of hand-typed bursts like `v3`). Positioned within the 1080px hard-crop, sitting on a permanent opaque bottom band (masks the source's own clipped captions, same technique as `v3`).
- **Cadence (ADR-0016/0018)**: hard cuts between all 8 pieces provide cadence at the piece boundaries; per-piece internal cadence relies on the source's own natural camera micro-movement plus the burst-by-burst caption changes (no zoom-punch added this round — flagged as a Hook Retro idea below).
- **Hook text overlay timing/size**: stat cards at size=56 (data_viz_overlay), structure caption at size=56 (reduced from an initial size=76 attempt that overflowed the frame — see Known Issues), dialogue captions at size=68 base / 75 keyword-emphasis per the established ADR-0018 addendum floor.
- **Claim-strength flag** (non-blocking): the HOOK is a strong Money+Number claim ("trades between a half a billion and a billion dollars of stock every day").

## Value-Adds (Transformative Gate, ADR-0007 — min 2 required, must be distinct categories)
1. **data_viz_overlay** — stat cards during the HOOK: "40 YEARS ON WALL STREET", "$0.5-1B TRADED / DAY".
2. **this_or_that_overlay** — a dedicated comparison card at the pivot: "THE MONEY vs THE STRUGGLE", deliberately abstract per the resilience-first tone decision (names the contrast, not the specific tragedy).

The structure caption ("THE STORY DOESN'T STOP THERE...") is the hook/structure device itself, not counted toward the 2 required value-adds — same scoping decision as `v2`/`v3`.

Commentary track: the structure caption + stat cards + comparison card + CTA (drawn from his own closing words, "money buys freedom, not happiness" → "MONEY = FREEDOM. NOT HAPPINESS.") satisfy ADR-0007 gate item 1. **No TTS was used** — matches the established hardknocks v1-v3 convention (TTS is scoped to the AI-education niche only, per ADR-0021); every word heard is Peter Tuchman's own voice.

## Known Issues
- **Auto-split dialogue captions instead of hand-typed bursts (new for this video)**: `v1`-`v3` hand-typed each `DIALOGUE_BURSTS` entry from the transcript. This video's 8 pieces / ~180 spoken words made that error-prone at this volume, so `render_hardknocks_v4.py` adds `auto_bursts()`: splits a piece's words into 2-4 word bursts, breaking on a >0.25s gap, 4 words, or 1.6s duration — whichever comes first. This worked correctly for ordinary words, but surfaced a real bug (next item) that hand-typing would not have hit the same way.
- **Word-join bug caught by the mandatory frame-check, fixed same render round**: the first `auto_bursts()` implementation rejoined words with `" ".join(w["word"].strip() for w in burst)`, which assumes every word needs a space before it. mlx_whisper's word tokens actually carry their own leading space already (e.g. `' 10'`, `',000.'` with no leading space, `' But'`) — punctuation-attached continuations like `,000.` are meant to concatenate directly onto the prior token. The bug rendered `"10 ,000. But if"` (stray space before the comma) instead of `"10,000. But if"`. Caught by the mandatory Stage 4 frame-check (extracting and visually reading the frame, not just trusting the code), same discipline that caught `v3`'s bugs. Fixed by concatenating raw word strings and stripping once (`"".join(w["word"] for w in burst).strip()`) instead of re-joining with an assumed space.
- **Resilience-first keyword-emphasis false positive, caught by the same frame-check pass**: the first keyword-color pass included "years" in the money/credibility group (white), intended for phrases like "40 years on Wall Street." But "years" also appears inside the tragedy narration ("broke for three years") — highlighting it there visually undercut the resilience-first tone decision (a credibility-colored word landing inside the hardship sentence). Removed "years" from the emphasis group entirely; it now renders in the plain base color everywhere, which is the intended behavior for tragedy-adjacent words. A second, related fix: removed "happiness" from the resilience/wisdom group (red) — it only appears in the negated clause "money does not buy you happiness," and highlighting it there risked being visually misread as endorsing happiness-via-money, the opposite of the point. "freedom" (the actual positive claim, "money buys you freedom") remains the highlighted word in that sentence.
- **Structure caption text overflow, caught by the same frame-check pass**: the first structure-caption draft, "BUT HE'S BEEN THROUGH SO MUCH..." at size=76, measured (and rendered) wider than the 1080px frame and was clipped on both edges. Measured several shorter alternatives with `PIL.ImageFont.getlength()` before re-rendering (per the `bacsihai_v7` lesson — measure pixel width before committing, not just after) and landed on "THE STORY DOESN'T STOP THERE..." at size=56 (966.5px, fits with ~57px margin each side).
- Pause-trimming was effectively a no-op: all 8 pieces were selected at exact word boundaries during transcript review, so there was no significant internal dead air to trim. The mandatory uniform speed-up (1.03x) was still applied per the base-quality rule — kept mild because the raw 49.9s cut already landed right at the ~50s target.
- No zoom-punch/pattern-interrupt was added within individual pieces this round (cadence currently relies on hard cuts between pieces plus caption-burst changes) — flagged as a Hook Retro idea below, not yet applied.

## What To Check At 48h
(Recompute the exact 48h deadline once this video is actually uploaded — not yet uploaded as of this writing.)
- AVD / Stayed % vs. `hardknocks_v1` (`dHDpDXSIAkA`, same channel, same single-person-reveal device applied to a Contiguous VO instead of a Multi-Clip Mashup) and `hardknocks_v3` (`dySR-oQ_rME`, same same-person-callback Implied Comparison device, different payoff type — belief vs. tragedy).
- Retention graph shape at the pivot point (~t=10.6s post-speed-up, when "Have you ever been broke before?" lands) — does retention hold through the tone shift from confident HOOK to vulnerable PIVOT?
- Retention through the reveal_tragedy piece specifically (~t=22-31s post-speed-up) — the single most emotionally weighty stretch; check whether it sustains or loses viewers, as a direct read on whether the resilience-first tone decision (vs. a more clickbait-forward alternative the user explicitly rejected) cost or helped retention.
- Comment themes — watch specifically for any comments reading the tragedy content as exploitative/clickbait (would indicate the resilience-first goal wasn't achieved in practice) vs. genuine engagement with the resilience/wisdom message.

## Post-Production Retro

### Hook Retro
- Verbal: none found — the interviewer's own real follow-up question ("Have you ever been broke before?") is a stronger, more natural pivot trigger than anything scripted from scratch would be; no changes made after the first cut.
- Visual: **one idea, not yet applied**. Unlike `v1`-`v3`, this video has no added zoom-punch or pattern-interrupt within individual pieces — cadence currently comes only from hard cuts between the 8 pieces and from caption-burst changes. A future iteration could add subtle zoom-in punches synced to key words (e.g. on "billion," "wife," "freedom") for extra pattern-interrupt within the longer pieces (`pivot2_rockbottom` at 8.7s and `reveal_tragedy` at 9.3s are the two longest single-shot stretches). Not applied this round since the existing cadence already passed Stage 0's feasibility check and the hard-cut-driven cadence matches `v3`'s precedent.
- Did not run the `viral-video-analysis` skill against a comparison video for this retro (no metrics yet to compare against for this or the most relevant comparisons, `v1`/`v3`) — will fold into the 48h check instead, same approach `v3` took.

### Workflow Delta
Yes — two cases not fully covered by the current docs, both now fixed at the project-policy level:
1. **Auto-split dialogue captions is a viable alternative to hand-typing for high-word-count sources**: `docs/WORKFLOW.md` Stage 3 doesn't currently distinguish between hand-typed and auto-split caption bursts. This video confirms auto-splitting (breaking on a gap/word-count/duration threshold) works correctly once the underlying word-join logic is fixed (see Known Issues) — worth noting as an available technique for future high-word-count Multi-Clip Mashups, not a required change to the workflow itself since both approaches are valid depending on piece count/word volume.
2. **mlx_whisper word-token spacing is not naturally "join with a space"** — any future code that reconstructs text from `words_timestamps=True` output must concatenate raw word strings (which already carry correct leading spacing) rather than assume every word needs an inserted space. This is a reusable gotcha for any future auto-caption tooling in this repo, not specific to this video — logging to `AGENTS.md` Known Pitfalls as a one-off insight that doesn't need its own ADR (a single string-handling fix, not an architectural decision).
3. Everything else about this production followed `docs/WORKFLOW.md` Stage 0-6 without needing a new rule or process change — the tone/format decisions (sub-format, resilience-first framing) were made explicitly before Stage 2 began, via a `/grill-with-docs` session, so no mid-production surprises occurred there.
