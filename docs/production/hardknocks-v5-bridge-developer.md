# hardknocks_v5 — "He Makes $50 Million A Year... But He Used To Sleep Under A Bridge"

## Status
| Field | Value |
|-------|-------|
| YouTube Video ID | [cyzcNAeg16A](https://youtube.com/watch?v=cyzcNAeg16A) |
| Rendered | 2026-07-14 |
| Uploaded | 2026-07-14 08:54 +07 |
| Metrics fetch after (48h rule) | 2026-07-16 08:54 +07 |
| Metrics status | Not yet fetched, too early |

## Video Specs
- Duration: 44.7s (raw cut 45.3s, 1.02x speed-up — mild, since the raw cut is already all-substantive content at the low end of the ~45-60s preferred range, no filler to trim)
- Resolution: 1080x1920 (9:16 portrait)
- Codec: H.264 (libx264, crf 18), 30fps
- Audio: AAC, 192kbps, 48kHz, stereo (1 stream, verified via ffprobe)
- File: `output/projects/hardknocks/final/2026-07-14-hardknocks_v5_bridge_developer.mp4` (28.1MB)
- Metadata (title/description, ready for manual upload): `output/projects/hardknocks/final/2026-07-14-hardknocks_v5_bridge_developer_metadata.txt`
- Render script: `pipeline/hardknocks/render_hardknocks_v5.py`

## YouTube Title
He Makes $50 Million A Year... But He Used To Sleep Under A Bridge

## YouTube Description
```
I asked a Nigerian real-estate developer — 21 years in the business, over 5,000 units built, $50 million in his best year — if he always knew this was possible.

His answer wasn't what I expected. Growing up, he and his family didn't have a roof over their heads. They were evicted from his mom's store and spent time sleeping under a bridge.

What he does with his name and his word now is the reason people trust him with their money. Stick around for his lesson on why banks want your money sitting idle — and why he refuses to let that happen to his.

What's the best piece of money advice you've ever received? Let me know below.

#realestate #entrepreneur #nigeria #shorts
```

## Source
- Channel: School of Hard Knocks (5th source from this channel — see `data/source_videos.csv`; same channel as `render_hardknocks_v1/v2/v3/v4.py`, ADR-0001/0004/0007).
- Source video ID: `g9K6l15bQGc` — "Asking Nigerian Billionaires How They Got Rich!", uploaded 2026-07-13, 1532.4s (~25:32), 3840x2160 (4K), street-interview format in Lagos, Nigeria.
- First use of this exact video ID — checked against `data/source_videos.csv` before selection.
- This is a multi-interview compilation (several Nigerian entrepreneurs/executives in one video); this production uses only the 2nd interview subject (a real-estate developer, on-camera ~468-764s of the source), not the other subjects in the same video.
- Footage used: 11 non-contiguous pieces spanning source timestamps 480.3s-683.5s, ~45.3s of edited output (raw, pre-speed-up) from a 1532.4s source — well under the ADR-0007 50% ceiling (and under 50% of even just this one subject's own ~296s on-camera segment). Every individual piece <15s (largest is 7.0s).
- Subject: an unnamed Nigerian real-estate developer (no name given on-camera in the used pieces), 21 years in the business, described in-video as having built over 5,000 units and one of the biggest real-estate developers in Africa.

## Why This Segment
**Multi-Clip Mashup** (ADR-0022) — the pieces that make this work (his Money+Number credential HOOK, the PIVOT into real childhood hardship, and his closing wisdom) are scattered from 480.3s to 683.5s of a 25:32 source; no single 45-60s window contains them all.

This is the **same-person-callback Implied Comparison** device (CONTEXT.md → Source Channel Pattern / Implied Comparison Hook), the same structural device as `hardknocks_v2`/`v3`/`v4`. The HOOK establishes stature purely through numbers (21 years, 5,000+ units, $50M in a year) with no hint of hardship. The PIVOT, triggered by the interviewer's own follow-up ("did you have any idea growing up..."), reveals a single-word "Never" followed by a genuinely vivid, concrete hardship: no roof over their heads, evicted from his mother's store, sleeping under a bridge. The closing payoff uses his own philosophy about reputation ("your name is the first opportunity to make money... you got to keep your word") and a contrarian finance lesson (banks want your money idle, not working for you).

Transcript-driven selection: all 11 pieces were chosen from the mlx_whisper word-timestamped transcript (`output/projects/hardknocks/source/g9K6l15bQGc_transcript.json`), each cut to exact word boundaries.

**Explicit swipe-away-reduction target for this video** (per the 2026-07-13 research session — `docs/research/hard-work-pays-off-2026-07-13/REPORT.md`, and the Giannis V2 root-cause added to `docs/adr/0017-hook-window-source-selection.md`): this production applies every currently-confirmed retention rule simultaneously (frame-0 face check on every piece, no full-screen overlay anywhere, ADR-0018 caption sync/cadence) plus one new incremental test — a 3-color keyword-emphasis palette (see Value-Adds) — as the concrete next step that research session's synthesis proposed. User's stated target for this video: raise Stayed to Watch toward 70% (current project best is 54.1%, `hardknocks_lawnmower_v1`); this is a stretch target, not a number this single video is expected to hit outright — see What To Check At 48h.

## Hook Formula Applied
- **Frame-0 face/action** (ADR-0017): cold open on two real faces in a tight two-shot (developer + interviewer, mic clearly in frame) outside a building under construction — not a title card, not a wide establishing shot. Verified via direct frame extraction at the piece's source timestamp (480.3s) before cutting, plus post-render frame-check at t=0s/0.2s/1.0s/2.0s (all pass).
- **Gap-not-resolved**: the HOOK (21 years / 5,000 units / $50M) establishes stature and wealth only — it gives no indication a childhood-hardship reveal is coming. Full Hook Gate checklist (all 7 items) run and passed before any cutting began.
- **Cause+effect not co-named**: neither the hook overlay, the comparison card, nor the YouTube title assert a causal mechanism between the hardship and the wealth — both stay at "what happened" (two contrasting facts), not "why it made him rich."
- **Payoff timing**: the pivot word ("Never...") lands at edited-timeline t≈3.3s (post-speed-up), with the concrete "slept under a bridge" reveal landing by t≈9.8-15.9s — the credential HOOK itself is only 3.2s (three short pieces), so the gap opens and resolves faster than `v4`'s longer HOOK did.
- **Caption sync (ADR-0018)**: self-authored `drawtext` captions, word-synced from the mlx_whisper transcript, auto-split into 2-4 word bursts (`auto_bursts()`, ported unchanged from `v4`). Positioned on a permanent opaque bottom band that masks the source's own burned-in captions, same technique as `v2`-`v4`.
- **Cadence (ADR-0016/0018)**: hard cuts between all 11 pieces (average piece ~4.1s, several under 1s) provide strong cadence at piece boundaries; caption-burst changes add further sub-2s visual change throughout, including the hook window itself (3 stat-card/caption changes in the first 3.3s).
- **Hook text overlay timing/size**: verified via frame extraction that the first stat card ("21 YEARS A DEVELOPER") and first dialogue caption ("21 years.") are both visible at t=0.0s — not delayed. Stat cards at size=56, structure caption at size=56, dialogue captions at size=68 base / 75 keyword-emphasis, matching the established ADR-0018 addendum floor. Pixel-width checked for every overlay string before finalizing (largest: the comparison card at 826px, 254px margin; largest dialogue burst at 955px, 125px margin) — none exceed the 1080px frame.
- **Claim-strength flag** (non-blocking): the HOOK is a strong Money+Number claim ("$50 million dollars" in a single year, 5,000+ units), and the PIVOT is a strong Contrarian-Reveal ("slept under a bridge") — both of the two strongest categories from `docs/research/hook-benchmarks-2026-07/REPORT.md`.

## Value-Adds (Transformative Gate, ADR-0007 — min 2 required, must be distinct categories)
1. **data_viz_overlay** — stat cards during the HOOK: "21 YEARS A DEVELOPER", "5,000+ UNITS BUILT", "$50M IN ONE YEAR".
2. **this_or_that_overlay** — a dedicated comparison card at the pivot reveal: "$50M DEVELOPER vs SLEPT UNDER A BRIDGE" (Implied Comparison device, CONTEXT.md).

The structure caption ("BUT GROWING UP...") is the hook/structure device itself, not counted toward the 2 required value-adds — same scoping decision as `v2`-`v4`.

**New this video (incremental test, not yet confirmed)**: a 3-color keyword-emphasis palette extending `v3`/`v4`'s 2-color scheme (base + 1 accent). Base captions stay yellow; three distinct keyword groups get their own color — white for HOOK/credibility words (21, years, 5000, units, fifty, million, dollars), red-orange (`0xFF3B1A`) for PIVOT/hardship words (never, roof, bridge, landlord, kicked), and green (`0x7CFC00`, matching the comparison-card color) for payoff/wisdom words (name, word, deliver, quality, banks, idle, working). This directly implements the "low-risk refinement to test on the next video" recommendation from `docs/research/hard-work-pays-off-2026-07-13/REPORT.md` section 4 (derived from analyzing a viral video that used a comparable multi-color semantic caption scheme). Flagged for the 48h retro: does the 3rd color read as a coherent system to viewers, or add visual noise vs. `v3`/`v4`'s simpler 2-color version? Not yet confirmed either way.

Commentary track: the structure caption + stat cards + comparison card + CTA (drawn from his own words, "Branding never sleeps.") satisfy ADR-0007 gate item 1. **No TTS was used** — matches the established hardknocks v1-v4 convention (TTS is scoped to the AI-education niche only, per ADR-0021); every word heard is the developer's (and, in two short paraphrase moments, the interviewer's) own real voice.

## Known Issues
- None found this round — `auto_bursts()` and the keyword-emphasis machinery were ported directly from `v4` (already fixed for the word-join stray-space bug there) rather than reimplemented, and the frame-check pass found no overflow/crop/timing issues on the first render (see Hook Formula Applied's pixel-width note).
- One deliberate content choice, not a bug: `teach2_integrity` ("What do you make out of your name? What is the integrity behind your name?") is the subject asking himself a rhetorical question as part of his own answer, not the interviewer — included because it's his own authentic build-up to the "keep your word" payoff, at the cost of ~3.2s that could otherwise have tightened the cut. Judged worth it for authenticity (this repo's stated preference for real content over the tightest possible cut) since it's genuinely his own reasoning, not padding.

## What To Check At 48h
Not yet uploaded — this section to be completed once uploaded and 48h have passed.
- AVD / Stayed % vs. `hardknocks_v4` (`3HRpaESmJWY`, same same-person-callback Implied Comparison device, tragedy-pivot vs. this video's childhood-hardship-pivot) and `hardknocks_lawnmower_v1` (`dHDpDXSIAkA`, current project-best at 54.1% Stayed to Watch — the benchmark this video is explicitly trying to beat toward the user's stated 70% target).
- Retention graph shape at the pivot point (~t=3.3s post-speed-up, when "Never..." lands, and ~t=9.8-15.9s when "slept under a bridge" resolves) — does retention hold through the tone shift from confident credential HOOK to vulnerable PIVOT, and does the faster (3.3s vs. `v4`'s ~10.6s) gap-open timing help or hurt vs. `v4`?
- Whether the new 3-color caption palette (vs. `v3`/`v4`'s 2-color scheme) shows any distinguishable retention difference — flagged as an open, unconfirmed test in Value-Adds above.
- Comment themes — watch for any comments questioning authenticity/staging of the hardship story (this is real-interview content, not the staged-reward genre flagged as a risk in `docs/research/hard-work-pays-off-2026-07-13/REPORT.md`, but worth checking regardless).

## Post-Production Retro

### Hook Retro
- Verbal: none found — the interviewer's real follow-up question ("did you have any idea growing up...") is a stronger, more natural pivot trigger than anything scripted from scratch would be; no changes made after the first cut.
- Visual: **one idea, not yet applied**, same open item `v4` flagged — no added zoom-punch or pattern-interrupt within individual pieces; cadence currently comes only from hard cuts between the 11 pieces and caption-burst changes. A future iteration could add subtle zoom-in punches synced to key reveal words ("Never," "bridge") for extra pattern-interrupt within the two longest pieces (`pivot3_vision` at 7.0s and `teach3_word` at 6.7s). Not applied this round since the existing cadence already passed Stage 0's feasibility check.
- Did not run the `viral-video-analysis` skill against a comparison video for this retro specifically — the 2026-07-13 session (`docs/research/hard-work-pays-off-2026-07-13/REPORT.md`) already fed this production directly (3-color caption palette, swipe-away benchmark framing), so a redundant comparison wasn't run; will fold further comparison into the 48h check instead.

### Workflow Delta
No — this production followed `docs/WORKFLOW.md` Stage 0-6 without needing a new rule or process change. The 3-color caption palette is an unconfirmed experiment (n=1, this video), not yet a generalized rule — per `docs/adr/domain-modeling` discipline it stays scoped to this video's Value-Adds section until (if) a 2nd video confirms it works, rather than being promoted into `docs/WORKFLOW.md` or `AGENTS.md` prematurely.
