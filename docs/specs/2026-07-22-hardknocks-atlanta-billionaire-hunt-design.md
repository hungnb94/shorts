# HardKnocks — Atlanta Billionaire Hunt Design

Date: 2026-07-22
Status: Approved; revised 2026-07-22 to use a narrator question hook
Source: https://www.youtube.com/watch?v=VW2t21zzYl8
Source ID: `VW2t21zzYl8`
Vertical: Finance / English
Format: Clip Curation Edit — Multi-Clip Mashup

## Goal

Create one 50–60 second Short from the supplied School of Hard Knocks source. The revision keeps the existing hunt body but replaces the source-led opening with a direct Qwen-narrated question, following the proven question-first mechanism of the previous John Ruiz Short without copying its disputed-net-worth premise.

The Short asks one unanswered question, shows failed or insufficient candidates, finds Rick Jackson, verifies the billionaire payoff, then extracts one actionable lesson from how he got his first opportunity.

## Hook Design

Hook family: Direct Search Question.

Qwen narrator:

> “How many millionaires do you have to meet before you find a real billionaire?”

Visual:

- Start on the host already walking and gesturing toward camera; no title card, freeze frame, blur, or full-screen B-roll.
- Keep moving source footage throughout 0–5 seconds.
- Duck the source dialogue for the complete opening segment so the question is the only intelligible speech. Preserve the walking footage and its motion; do not add silent/frozen pre-roll.
- Burn the question as short synchronized bursts from frame 0:
  - `HOW MANY MILLIONAIRES`
  - `DO YOU HAVE TO MEET`
  - `BEFORE YOU FIND`
  - `A REAL BILLIONAIRE?`
- Add an early SFX within 0–1 second and a second accent when `REAL BILLIONAIRE` lands.
- Keep the host’s face visible throughout 0–10 seconds. Any overlay in this window must be partial and non-obstructive.
- Use 2–5 word Komika Axis bursts with one emphasized keyword per burst. Derive exact burst timing from ASR/word timestamps of the generated Qwen file rather than from the replaced source line.

Why the gap remains open: the question promises an escalating search but withholds the number of failed candidates, whether the hunt succeeds, and who the billionaire is. Rick Jackson and the verified payoff remain hidden until the body.

## Narrative Architecture

Target runtime: 56–60 seconds.

### Act 1 — Question and Resistance (0–10s)

1. Direct narrator question on moving host footage, with source dialogue fully ducked.
2. Fast montage of real rejections or evasive answers.
3. Persistent game-state graphic: `BILLIONAIRE FOUND: NO`.

Purpose: establish the search question and its difficulty without a separate exposition block.

### Act 2 — Escalating Candidates (10–24s)

1. Waffle House franchisee at 22 with 14 locations.
2. Eight-figure investor who learned about wealth while incarcerated.
3. Each beat ends with a concise editorial verdict such as `SUCCESSFUL — NOT THE TARGET`.
4. Use short narrator bridges only where needed to prevent disconnected cuts.

The incarceration beat must not mention the attempted-murder detail; it is irrelevant to the business thesis and would sensationalize the story. The eight-figure claim is labeled as source-reported, not independently verified.

### Act 3 — Billionaire Found (24–42s)

1. Host approaches Rick Jackson at the vehicle; active-speaker reframing follows each turn.
2. Rick states that he owns more than 20 healthcare companies and that they generated $3 billion in annual revenue.
3. Distinguish business revenue from personal net worth on screen:
   - `SOURCE CLAIM: $3B/YEAR REVENUE`
   - never `$3B NET WORTH`.
4. Show a brief independent-source proof panel:
   - Forbes profile: Rick Jackson, real-time net worth approximately $1B as of 2026-07-20; Jackson Healthcare generates $3B in revenue from 22 businesses.
   - Official Jackson Healthcare page: parent company of more than 20 businesses.
5. Change the game-state graphic to `BILLIONAIRE FOUND` with a confirmation stinger.

### Mid-Roll Triple CTA (starts 39–42s)

Keep Rick or the host visible behind a custom translucent bumper. Qwen narrator:

> “Would you take his first bet? Like, subscribe, and comment.”

On-screen text explicitly includes `LIKE`, `SUBSCRIBE`, and `COMMENT`. The prompt tees up the commission-only lesson instead of interrupting the story with a generic channel ad.

### Act 4 — Actionable Payoff (42–60s)

Use Rick’s original voice in three clips, each below 15 seconds:

1. They would not hire him because he lacked a degree.
2. He offered to work for no monthly salary and only straight commission.
3. One year later, he bought the firm.

Close with one short original narrator interpretation over moving footage:

> “He removed their risk, then earned the right to own.”

Final editorial card: `REMOVE THEIR RISK` → `EARN THE UPSIDE`.

## Visual and Audio Treatment

- 1080×1920 portrait, H.264, yuv420p, 30 fps, AAC stereo 48 kHz.
- Use uniform crop-and-zoom to remove the source’s burned-in bottom captions without creating a black footer or distorting aspect ratio.
- Apply Active-Speaker Reframing at every retained host/guest turn.
- Use Semantic Zoom only on meaningful beats: the opening question, `with a B`, `no salary`, and `bought the firm`.
- Keep source footage moving throughout 0–10 seconds; no full-screen proof or Pexels replacement in that window.
- After 10 seconds, use proof-coupled Pexels footage where it clarifies the exact beat, such as restaurant operations, healthcare staffing, or commission/contract risk. Generic stock must be labeled `ILLUSTRATION` and pass brand/OCR review.
- Maintain the three-source engagement stack: original source footage, animated editorial overlays, and Pexels footage.
- Rebuild captions in the calibrated English Komika Axis profile: 2–5 words per burst, one emphasized keyword, normal center around 55–65% of frame height unless visual review requires movement.
- Add purposeful SFX to the early hook accents, rejection stamps, billionaire confirmation, proof entrance/exit, and CTA transition.
- Add a non-obstructive moving watermark that changes position across the timeline.
- Apply pause trimming and a modest final speed-up derived from actual source gap distribution; do not copy a fixed threshold from another project.
- Add short audio fades at every hard segment boundary and preserve enough trailing buffer after every final spoken word.

## Transformative Gate

Commentary:

- New mission-state framing, narrator bridges, independent verification, editorial verdicts, CTA, and final business interpretation create a distinct thesis and narrative.

Value-adds, at least two required:

1. Mission/game-state counter with escalating verdicts.
2. Independent Forbes and Jackson Healthcare verification.
3. Revenue-versus-net-worth clarification.
4. Active-speaker reframing and word-timed rebuilt captions.
5. Business Lesson Payoff: removing employer risk to earn ownership upside.

Source-use limits:

- Every source excerpt must be under 15 seconds.
- Total source use must remain below 50% of the 1,316-second source.
- No clip may be looped to fill runtime.

## Claim and Editorial Guardrails

- Do not use “24 hours” in narration, overlays, title, or description because the source footage does not independently prove the elapsed duration.
- Do not conflate Jackson Healthcare’s $3B annual revenue with Rick Jackson’s net worth.
- Identify the eight-figure amount as a source-reported claim if retained.
- Do not mention Rick Jackson’s current political campaign; it distracts from the business lesson and is unnecessary to verify the source claims.
- Use the supplied School of Hard Knocks video as footage, never as the independent verification source.
- Keep allegations or unrelated controversies out of this edit because they do not bear on the selected claim or lesson.

## Upload Package Constraints

The production doc, after final QC, must contain exactly one canonical package:

- Title: at most 30 visible characters, Title Case, exactly two relevant emoji.
- Description: first line mirrors the title; at most one additional sentence; no raw affiliate link.
- Exactly three visible hashtags, including `#shorts`.
- Exactly three separate YouTube Studio tags.
- Audience: Not made for kids.
- Language: English.
- Category: Education.
- Correct finance playlist, Related Video wiring, location, and approved upload template.

## Verification Plan

No renderer unit tests will be created or expanded. Verification is against the real media artifact:

1. Probe resolution, aspect ratio, duration, codecs, pixel format, frame rate, and audio streams.
2. Full decode to null with zero ffmpeg errors.
3. Final ASR of the whole video plus dedicated 0–10 second hook and final-tail ASR.
4. Confirm the hook’s complete spoken promise and all closing words survive the final speed-up.
5. Run blackdetect, freezedetect, silencedetect, and bottom-row pixel scans across the timeline.
6. Measure overall loudness, true peak, each narrator window, and fine-grained audio around every segment boundary.
7. Confirm early SFX in the 0–1 second waveform window.
8. Extract and manually inspect full-resolution frames across 0–5 seconds, every speaker turn, every proof overlay, CTA at 39–42 seconds, and the final frame.
9. Verify caption placement, keyword emphasis, proof legibility, no clipping, no source-caption bleed, no black footer, moving watermark position changes, and no full-screen face blackout in 0–10 seconds.
10. Verify every source clip is below 15 seconds and total source use is below 50%.
11. Confirm the production doc has the full metadata and Studio-settings package plus Hook Retro and Workflow Delta.

## Known Risks and Mitigations

- Multi-subject montage can feel fragmented. Mitigation: persistent mission counter, ordered escalation, and minimal narrator bridges.
- Revealing Rick or `$3B` too early collapses the hunt. Mitigation: keep Rick hidden until Act 3.
- The mandatory CTA can interrupt the payoff. Mitigation: place it immediately after the verified find and phrase it as a bridge into the first-bet lesson.
- Source captions occupy the bottom band. Mitigation: crop then uniformly scale and center-crop; never mask with a permanent black drawbox.
- Pexels can introduce misleading brands. Mitigation: contact-sheet/OCR review, exact-excerpt full decode, and `ILLUSTRATION` labels.
- Current political coverage could hijack audience interpretation. Mitigation: omit politics entirely.
