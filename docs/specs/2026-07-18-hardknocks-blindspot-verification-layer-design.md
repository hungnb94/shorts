# HardKnocks Blindspot Verification Layer — Design

## Status

Approved by the user in a brainstorming session on 2026-07-18, following user approval of the
"Verified Wealth Interview" USP proposal in
`docs/research/hardknocks-competitive-landscape-2026-07-18/REPORT.md`. All open decisions below
were resolved live with the user (scope, frequency, styling, language, meme-insert format, the
5-criteria rubric, duration handling, and verification ordering) rather than assumed.

## Goal

Give every HardKnocks video a recognizable, reusable "we checked this" production layer so
viewers register the channel as meticulous/professional rather than a quick repost — directly
executing the Verdict-beat USP already approved in the competitive-landscape report. The design
reuses this project's existing post-render value-add compositing architecture (ADR-0008) rather
than introducing a new rendering mechanism.

Two prior competitive findings motivate the concrete choices here:

- WEALTHIAN's "professional" feel comes from evidence-matched footage and quantified payoffs, not
  complex motion graphics (`docs/research/wealthian-top5-formula-2026-07-15/REPORT.md`).
- Broadcast-news Shorts (Business Insider / Bloomberg Quicktake / CNBC Make It) achieve a
  "journalism-grade" feel through a small set of **reusable templates** (lower-third citation,
  animated count-up numbers, consistent SFX) built once and reused every video — the only pattern
  of the three researched that is realistic at this project's solo/6-videos-day cadence (see the
  channel-research findings folded into this session; Johnny Harris and Cleo Abram's polish
  depends on 7-20-person teams and monthly cadence, both incompatible with this project).

## Scope

- **Phase 1 (build now, finance/HardKnocks only)**: everything in Sections 1-3 below.
- **Phase 2 (after Phase 1 ships on at least one real video)**: persistent logo/channel-bug,
  standardized cut/transition SFX library, evidence-matched b-roll discipline added to the Stage 4
  QC checklist, and rolling the **citation tag + data counter only** (not the Blindspot Score,
  which is finance-specific — see below) out to the `bacsihai` (Vietnamese) and `aiwork` niches
  with fully localized labels, never mixed-language per the existing "never mix languages within
  one video" rule.
- The **Blindspot Score** (Section 3) is scoped to HardKnocks/finance only. Its name and 5
  criteria are built around verifying wealth claims and are tied to the destination channel's own
  name (MONEY BLINDSPOT); it is not proposed for `bacsihai` or `aiwork`.

## 0. Mystery Reveal Hook (opening treatment)

Frame 0 opens with the interview subject's face **partially blurred** (soft blur preserving skin
tone/shape, not a full obscure) so the viewer doesn't immediately know which millionaire this
episode features — a curiosity-gap device layered onto whichever existing hook pattern
(Money+Number, Contrarian Reveal, Live-Approach, Implied Comparison) the source clip already uses.
The blur clears by approximately **t=3-5s**, timed to the video's existing first hook beat (e.g.,
when the Money+Number or Contrarian claim first lands), not held through the whole video.

This intersects directly with **ADR-0017's Hook-Window Rule** (frame 0 must show a real human
face, skin-tone ≥10% by pixel stats; no full-canvas overlay may remove the face in 0-10s). Early
reveal (~3-5s) was the user's explicit choice specifically to stay inside that rule's intent — a
genuine human face must still be perceptible and confirmed early, not withheld for suspense alone.
This is treated as a **scoped hook hypothesis**, the same way Live-Approach vs. Money+Number hooks
are scoped and compared rather than declared universal (ADR-0031) — it should be verified on a
real render (does the blur still pass the ≥10% skin-tone check? does it read as "mysterious" or
just "low quality/glitchy"?) before being treated as a standing technique, and its own future
metrics should not be read as proof against a non-blurred control per the same ADR-0031 logic.

## 1. Per-claim verification layer

Every time the video states a checkable number or claim, four elements fire together, frame-synced:

1. **Source Citation Tag** — small corner-anchored text, e.g. `SOURCE: FORBES 2026` when
   verifiable, `UNVERIFIED — NO PUBLIC RECORD` when not. Own font/color/position, deliberately
   distinct from the ADR-0018 keyword-caption palette so it reads as a separate "system" layer
   (like a news chyron), not a competing caption.
2. **Quantified Data Counter** — animated count-up treatment for money/percentage figures, one
   fixed font/color/animation curve reused every video (data_viz_overlay, given a permanent
   template instead of ad hoc styling).
3. **Verdict Sticker** — a short animated sticker/graphic (not a real video clip, to avoid any
   third-party copyright exposure): one "correct" variant, one "wrong/exaggerated" variant,
   reused every video. Same category of device as the sticker capstones already documented in this
   project's own research (RandomDude's skull sticker, Sunnah Edit's heart sticker) —
   `docs/research/800m-view-case-study-2026-07-11/`, `docs/research/hard-work-pays-off-2026-07-13/`.
4. **Verdict Audio Stinger** — a short "ting-ting" chime on a verified-correct claim, a short
   "wrong-answer" (trombone/buzzer style) sting on a false/exaggerated claim. Synced to the same
   frame as the sticker/citation appearance, not just dropped in loosely.

`source_citation` and `data_viz_overlay` (both pre-existing ADR-0008 value-add types) are
reclassified from **AB-testable value-add** to **mandatory Retention Technique** — same status as
sound design and zoom punch (AGENTS.md: never AB-test a base-quality technique). This also means
every Clip Curation Edit video now automatically satisfies 2 of ADR-0007's Transformative Gate
minimum-2-value-adds requirement.

Language: English for HardKnocks/finance. If/when Phase 2 extends the citation tag + data counter
to `bacsihai`, labels are fully translated (`NGUỒN:`, `ĐÃ XÁC MINH`, `CHƯA XÁC MINH`) — no English
labels kept as an "iconographic exception," per the user's explicit choice to preserve the existing
never-mix-languages rule without carving out a new exception.

## 2. Verification ordering — escalating drama

Per-claim verification moments within the video body must be ordered from **least to most
dramatic**, saving the highest-stakes check (the claim most likely to surprise, contradict, or
damn the interview subject) for latest in the video, immediately before the closing Blindspot
Score reveal. This is a scripting/editing rule, not a new visual asset: at the script-lock stage
(this project's existing per-video grilling/scripting step), the producer must explicitly rank
candidate claims by dramatic weight before deciding verification order, the same way hook
selection is already deliberately sequenced. This directly extends the project's own confirmed
Narrative Arc finding (`docs/research/hard-work-pays-off-2026-07-13/REPORT.md`) — withholding the
biggest reveal is what makes viewers stay to the end — applied specifically to the fact-check beat
sequence rather than only to the interview's own story beats.

## 3. Blindspot Score (closing capstone, HardKnocks/finance only)

Every video ends on a **Blindspot Score Card**: a fixed 5-row template evaluating the interview
subject against 5 criteria, each marked pass/fail/unverifiable, followed by a final `X/5 ⭐`
rating card.

| # | Criterion | Question |
|---|---|---|
| 1 | Receipts | Are the numbers independently checkable? |
| 2 | Repeatable | Could an average person realistically follow this path, or was it luck/inheritance/unique circumstance? |
| 3 | Story Check | Does the story hold together internally, without contradiction? |
| 4 | Blind Spot | Does the subject acknowledge luck/privilege, or claim all the credit themselves? |
| 5 | Takeaway | Is there a concrete, usable lesson, or only emotional hype? |

Criterion 4's name deliberately echoes the destination channel's own name (MONEY BLINDSPOT),
reinforcing brand recall at the exact moment of the score reveal.

The 5 criteria themselves are revealed in escalating order within the card (same escalating-drama
principle as Section 2), with the most damning/surprising criterion for that specific subject
shown last, immediately before the star rating lands.

## 4. Duration handling

Adding four per-claim elements plus a 5-row closing card will often push a video's raw cut past
60s. Per the user's explicit resolution: let the raw timeline run slightly over 60s, then apply
this project's existing pause-trim + 1.1x speed-up Retention Technique (already base quality per
AGENTS.md, first used in `aiwork_v2`) to bring the final render back under YouTube Shorts' hard
60s ceiling. This does not relax the ≤60s hard output constraint (AGENTS.md: "Never post videos
>60s to YouTube Shorts") — it uses an already-approved technique as the mechanism to keep the
final deliverable compliant despite the heavier content load. Final duration must still be
verified against the 60s cap at Stage 4 QC before upload, same as every prior video.

## 5. Assets to build before the first real video

One-time production cost, reused on every subsequent video:

- 2 sticker animations (correct / wrong)
- 2 audio stingers (ting-ting / wrong-buzzer)
- 1 Blindspot Score Card template (5-row checklist + star-rating reveal)
- Citation tag + data counter overlay templates (font, color, position, animation curve)

Proposed location: `output/shared/hardknocks_branding/`, parallel to the existing
`output/shared/{pexels,emoji_processed,metadata}` convention.

Implementation lands as reusable helper functions inside the next HardKnocks render script
(following this project's existing per-version copy-adapt convention), not as a new shared module
extracted across niches yet — that extraction is an already-known pitfall (AGENTS.md: value-add
compositing is currently coupled per-script) worth fixing eventually, but premature to force now
when only one niche uses the Blindspot Score and only two niches (Phase 2) will share the citation
tag/data counter.

## 6. Risks / open verification items

- **Caption crowding**: firing 4 elements on every checkable claim, in a ≤60s (post-speedup) video,
  risks visually crowding or overlapping the existing ADR-0018 main caption. No safe per-video
  maximum claim-check count is assumed here — this must be verified by rendering a real video and
  reviewing frames at Stage 4, not decided in advance.
- **Gate synergy vs. gaming risk**: making `source_citation` + `data_viz_overlay` permanently
  mandatory automatically satisfies ADR-0007's 2-value-add minimum every time. Watch that this
  doesn't become a ceiling (i.e., videos stop trying additional value-adds because the minimum is
  now automatic) — worth a retro check after a few videos.
- **This is a policy change to ADR-0008's value-add classification** and should be written up as
  a short ADR addendum once the first real video ships, mirroring how sound design/zoom punch were
  previously formalized as mandatory Retention Techniques.

## 7. Verification plan

No unit tests, per this project's existing convention for renderers (media-first verification,
AGENTS.md). Verify by:

1. Rendering the next real HardKnocks video with all Section 1-4 elements applied.
2. Frame-by-frame Stage 4 review confirming no overlap between the citation-tag/sticker layer and
   the main ADR-0018 caption, confirming final duration is ≤60s after the 1.1x speed-up, and
   running `inspect_image.py` on the blurred frame-0 to confirm it still clears ADR-0017's ≥10%
   skin-tone threshold.
3. Full decode + ffprobe spec check (existing pipeline).
4. Real upload, 48h wait, Studio-verified Stayed-to-Watch/AVD per existing metrics process — do
   not treat this as a controlled experiment against a non-Blindspot-Score baseline (per ADR-0031's
   standing rule that cross-story comparisons aren't controlled experiments); treat the first
   video's numbers as a new baseline data point, not a proof of causality.

---

## Revision 2 (2026-07-18) — "3 Things Every Man Wants", evidence-gated

Resolved in a `/grill-with-docs` session after the first v11 render. This revision reframes the
closing capstone and the per-claim layer around a single, unified truth-check format and hardens the
sourcing rules. It supersedes the 5-criteria Blindspot Score (Section 3) and the SOHK-derived
citations for this and future HardKnocks videos.

### Concept
"Every man wants three things. Does this millionaire really have them? Let's check." Score the
subject on **3 aspirational criteria every man wants**, each phrased in ≤3 words, each verified
against an **independent** source with a **TRUE / FALSE / HALF-TRUE** verdict.

The 3 criteria (this subject, Ben Pogue), least-to-most-dramatic order:

| # | Criterion | His claim | Independent source(s) | Verdict |
|---|---|---|---|---|
| 1 | WEALTH | company does ~$1.5B | Pilot Hill Advisors press release ("2025 revenue projected to exceed $1.5 billion", ENR #152) — shown/labelled as **REVENUE**, not net worth | TRUE |
| 2 | FREEDOM | ~$20M private jet | BlackJet G550 Buyer's Guide (pre-owned G550 $11–35M market range; consistent with his "bought used ~$20M") | TRUE |
| 3 | LEGACY (leave something forward, not inheritance) | charity / giving back | ProPublica (Pogue Family Foundation: $330M assets, $15.2M charitable disbursements) + Pilot Hill (100% employee-owned ESOP, "legacy for future generations") **BUT** Global Construction Review (founder/father **Paul** Pogue pleaded guilty to underpaying taxes) | HALF-TRUE |

Final verdict: **2 / 3**.

### Structure (supersedes the single closing-card model)
- **Opening card** (unchanged mechanic): blurred Pogue portrait → reveal ~3.5s; branded panel now
  lists the **3** criteria, finale reads **"?/3"**; Qwen VO line = *"Every man wants three things.
  Does he really have them? Let's check."*
- **During the interview (tease):** lightweight **TRUE / FALSE / UNVERIFIED** stamps fire on
  **many** checkable statements as he says them (jet price, $1.5B revenue, "took over dad's
  company", "$200M/year" = UNVERIFIED, charity, …). No full-screen source cutaways here — kept
  light to hold the interview's pace and to demonstrate breadth of checking.
- **Closing (reveal + score, payoff):** each of the 3 criteria is revealed in turn as a
  **full-screen cutaway to the real source screenshot**, cropped/zoomed to the key headline/number,
  yellow highlight, outlet name + URL visible; verdict stamp lands; then the 3-row score card +
  **VERDICT 2/3**; then a **"WE CHECKED [N] SOURCES"** rigor card listing the outlets; then a
  **comment CTA** ("What's YOUR score? Comment 👇").

### Editing/craft rules added this revision
- **Caption:** rebuilt from `mlx_whisper` word timestamps into **2–4 word bursts** at **~60% of
  frame height** (below the face), big font + one highlighted keyword; must never clip at frame
  edges. (Follows the known pitfall: concatenate raw word tokens, do not rejoin with spaces.)
- **Active-Speaker Reframing (ADR-0030):** **hard-cut punch-in** that centers whoever is speaking
  (Pogue-centered ≈ focus 0.26, host-centered ≈ 0.66), cutting on speaker turns (each caption line
  tagged with its speaker; cut only when the speaker changes).
- **Verdict accuracy:** the tax-fraud conviction is the **FATHER (Paul Pogue)**, stated explicitly;
  Ben is not accused of any crime. No fabrication — a search found **no** evidence of personal
  infidelity/scandal for Ben, so none is included.

### Sourcing rules (binding, HardKnocks going forward)
- **Never cite School of Hard Knocks (SOHK) as a verification source** — it is the raw interview
  footage (Clip Curation source), not an independent verifier. Use independent outlets or an
  explicit market-comparable inference (e.g., jet price from comparable-aircraft listings).
- Every on-screen verdict must be backed by an independent, screenshot-able source. Where a claim
  has no public record (e.g., "$200M personal in a year"), mark it **UNVERIFIED**, never guess.
- Source screenshots captured via headless Chrome; note that Cloudflare/paywalled outlets
  (Community Impact, Construction Briefing, GlobalAir, D Magazine, NBC) block headless capture —
  use accessible equivalents (Pilot Hill, BlackJet, ProPublica, Global Construction Review).
- Saved evidence assets: `output/projects/hardknocks/clips/v11_work/source_shots/`.

## Refinement 2 (2026-07-18) — inline verify, ting/buzzer/uncertain, single-VO ending

Resolved in a third `/grill-with-docs` session after Revision 2's first full render. Moves the
source reveal from "closing full-screen cutaway" to "inline, at the moment of the claim", adds
audio verdict stingers, and replaces the multi-card ending with one continuous VO-driven sequence.

### Concept
"Ngay sau khi hiển thị true thì hiển thị nguồn tại ngay đó luôn" (user) — the moment a claim is
spoken, the verification fires right there, not saved for the closing cutaway. Trust-building
(showing the receipts) and pacing (never stalling the interview) both improve by co-locating claim
and evidence.

### Structure changes (supersedes Revision 2's "During the interview" and "Closing" bullets)
- **Inline split-screen verify** (`InlineVerify`/`SourceRef`, `make_source_panel`,
  `composite_inline`): the interviewee's face stays visible on the **top half**; a panel slides up
  over the **bottom half** (`INLINE_PANEL_H = 940px`, which also covers the caption band while
  visible) showing the TRUE/FALSE/UNVERIFIED badge, the claim, and **1–3** independent source
  screenshots stacked with a yellow highlight box over the exact keyword/number, each labelled
  `SOURCE: <outlet>`. More independent sources per claim is explicitly preferred ("càng nhiều nguồn
  càng tốt"). The interview dialogue keeps playing underneath — nothing pauses for the verify.
- **Verdict stingers**: a "ting" (`verdict_correct_ting.wav`) fires on TRUE, a buzzer
  (`verdict_wrong_buzz.wav`) on FALSE, and a new two-tone descending "uncertain" tone
  (`make_uncertain_sfx`) on UNVERIFIED — mixed under the still-playing dialogue+music, not
  replacing them.
- **LESSON pills** (`Lesson`, `make_lesson_png`): small yellow-tagged recap pills ("BUY USED: he
  saved ~$30M vs new", etc.) weave the business-value layer directly into the interview body, per
  the standing instruction to keep entrepreneurial takeaways present throughout, not just at the
  end.
- **Single continuous VO-driven ending** (`build_ending`): replaces Revision 2's evidence
  cutaway ×3 + score card + sources card + CTA card sequence. WEALTH and FREEDOM evidence is
  already shown inline, so only **LEGACY is revealed at the end** (it wasn't claimed inline,
  per the earlier design decision to save one blindspot for the payoff). One Qwen VO line —
  *"Wealth, real. Freedom, real. Legacy? Only half. He gave the company to his employees, but his
  dad built it. The lesson: he bought the jet used, and grew what he already had. So, what's your
  score? Comment below."* (13.6s, `ending_vo_qwen.wav`) — drives the whole sequence: a score card
  with a **row-by-row yellow highlight** synced to "Wealth… Freedom… Legacy…", a hard cut to the
  LEGACY evidence reveal on "he gave the company… his dad built it", the LESSON recap pill layered
  on top during "the lesson…", then a hard cut to the CTA card on "what's your score?". **The CTA
  itself is spoken by the VO** (not a silent card) per the explicit instruction "CTA cũng là TTS".
  The standalone "WE CHECKED N SOURCES" card is dropped — the inline panels already show sources
  live, which is a stronger trust signal than a summary list.

### Pipeline ordering (implementation note, not a design decision)
Captions must burn in **before** the inline panels are composited, not after — a panel occupying
the bottom 940px naturally covers the caption band while it's shown; if captions were burned in
afterward, they'd float illegibly on top of the evidence screenshots. `main()` order: build base
segments → ASR captions → `mix_and_caption` (captions + voice + music) → `composite_inline`
(panels/pills + stingers on top).

### Verified during this refinement
- Re-checked the reported "$15M vs $50M" jet-price caption bug: isolated, deterministic
  (3×-repeated) ASR runs on the exact `price_reveal` segment audio transcribe "fifty million"
  correctly, and the ASR-only caption pipeline never emits a `$` glyph at all (no hardcoded
  overlay text). The bug does not reproduce in the current pipeline; re-verify against the actual
  `.ass` output after render as a final check.
- Re-verified all inline/LEGACY source screenshot crop+highlight coordinates pixel-by-pixel
  against the saved evidence PNGs (previous coordinates were rough grid-band estimates and several
  missed the target text or, in one case — `freedom_aeroclass.png` — cited a page with no price
  figure at all; swapped for `freedom_privatejetcard.png`, which states the used-G550 price
  explicitly).

### Third round (2026-07-18) — real business-lesson content, cut hygiene, transition cue
- **Business-lesson gap**: the video had almost no real entrepreneurial-wisdom material from the
  interview itself (user: "thứ quan trọng nhất là bài học về kinh doanh thì chất liệu đó trong
  video gần như không có"). Searched the full source transcript
  (`output/projects/hardknocks/source/rrDdi0vZn00_transcript.json`) for the user's own example
  questions ("How do you stand out from competition?", "life changing conversation") and found
  both answered almost verbatim at ~1249-1307s — directly adjacent to the existing
  `billions_reveal` clip. Added one new segment, `competitive_edge` (1249.52-1260.62s): host asks
  "how did you stand out from competition?", Pogue answers "we went all in on people and culture."
  Chose this over the "playing not to lose vs. playing to win" quote per user's explicit priority
  pick. The real dialogue delivers the lesson directly — no synthetic LESSON pill was added on top
  of it.
- **Cut hygiene**: two existing cuts landed mid-sentence and were extended to let the speaker
  finish: `price_reveal` end moved 1223.36 -> 1223.70 so "...probably about 20." completes (word
  ends 1223.60); `competitive_edge` start moved back to 1249.52 (from 1251.82) to include the
  "Construction is a very competitive business to be in..." lead-in instead of starting mid-thought
  on "There's hundreds down in the south alone."
  Speaker-turn timing for both re-verified via direct frame extraction (mouth movement + mic
  position), not inferred from transcript text alone.
- **UNVERIFIED panel text overflow**: the "0 PUBLIC RECORDS FOUND" note in `make_source_panel`
  overflowed the 1080px canvas at its fixed 90pt size and clipped at both edges. Fixed with the same
  dynamic-shrink-to-fit approach used for the LESSON pill.
- **Ending transition cue**: the cut from interview into the closing sequence needed a clearer
  signal that "this is the final summary" (user: wanted something like "và đây là tổng hợp cuối
  cùng"). Added a short spoken lead-in to the ending VO — "Final scorecard." — before "Wealth,
  real...", regenerated via Qwen TTS and re-verified by ASR; all `ENDING_T_*` keyframe constants
  shifted forward to match the new word timings.
- **60s cap tension**: the added segment + longer VO pushed the raw timeline past what 1.1x/1.12x
  speed could fit under 60s. User was asked directly given AGENTS.md's hard "never >60s" rule
  (breaking it drops the video out of the Shorts feed) and chose to keep the cap: `POST_SPEED`
  raised to **1.19** (from 1.12) rather than accept an over-60s upload. Final duration 59.63s.
