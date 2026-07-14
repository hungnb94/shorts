# aiwork_v6 — "Why Your AI Keeps Getting It Wrong" (Multi-Clip Mashup)

## Status
| Field | Value |
|-------|-------|
| YouTube Video ID | Not yet uploaded (manual upload per `docs/WORKFLOW.md` Stage 6) |
| Rendered | 2026-07-14 |
| Uploaded | Pending |
| Metrics fetch after (48h rule) | Pending (starts counting from upload time) |
| Metrics status | Pending |

## Video Specs
- Duration: 47.8s (raw cut 48.68s, 1.02x speed-up — mild, matching the hardknocks_v5 rationale: the 6 selected pieces are already all-substantive, nothing left to trim for pace)
- Resolution: 1080x1920 (9:16 portrait)
- Codec: H.264 (libx264, crf 20), 30fps
- Audio: AAC, 192kbps, 48kHz, stereo (single source-audio track, no TTS)
- File: `output/projects/aiwork/final/2026-07-14-aiwork_v6_ai_misalignment.mp4` (16.7MB)
- Metadata (title/description, ready for manual upload): `output/projects/aiwork/final/2026-07-14-aiwork_v6_ai_misalignment.txt`
- Render script: `pipeline/aiwork/render_aiwork_v6.py`

## YouTube Title
Why Your AI Keeps Getting It Wrong

## YouTube Description
```
A developer building his own AI planning tool said the quiet part out loud: so much of AI misalignment isn't a model problem - it's that the AI never asked what you actually cared about in the first place.

Watch it happen in real time: the AI asks a real clarifying question, he gives a real answer it could never have guessed - and that's the difference between an AI that guesses and one that asks first.

Source: Matt Pocock (@mattpocockuk) YouTube channel, live "/wayfinder Demo" stream - commentary and value-add overlays added here.

Working With AI - short, practical breakdowns of how professionals actually use AI tools. No hype, no "AI will take your job" fearmongering. Just what to try next.

#AI #Claude #PromptEngineering #Productivity
```

## Source
- Channel: Matt Pocock (`@mattpocockuk`) — an individual AI/TypeScript educator, named in ADR-0020 as one of this niche's three style/structure references (`@claude`, `@mattpocockuk`, `@anthropic-ai`). **First non-official-channel source used for this niche** (aiwork_v1/v2/v3/v4/v5 all reused footage from the official Claude/Anthropic YouTube channel, governed by ADR-0026's standing carve-out). Matt Pocock's channel is not a company-branded channel, so it carries none of the brand/PR risk ADR-0026 was written to manage — it is governed by the same default Clip Curation Edit rules (ADR-0007/0013/0022) that already apply to every other creator this project reuses footage from (School of Hard Knocks, Bác sĩ Hải), with no special case either way. No new Ask-First escalation was needed.
- Source video ID: `251hsWgoTPM` — "LIVE: The /wayfinder Demo", uploaded 2026-07-13, 4480.0s (~74.6min), 1920x1080 (max available — this livestream re-upload caps at 1080p60, no 2160p exists for it), a live pair-programming session building "Wayfinder" (a spec-first planning tool/skill on top of Claude Code).
- First use of this exact video ID — checked against `data/source_videos.csv` before selection.
- The source is ~99% screen-share (VS Code + terminal + GitHub issues) with a small corner-PiP webcam, and covers extremely developer-specific content (TikTok upload API research, GitHub issue trees, TypeScript schema migrations) — none of it usable verbatim under ADR-0020's audience-fit constraint (professionals/knowledge workers, not developers specifically).
- Footage used: 6 non-contiguous pieces spanning source timestamps 1.00s-4262.90s, 48.68s of edited output (raw, pre-speed-up) from a 4480.0s source — 1.09%, far under the ADR-0007 50% ceiling. Every individual piece <15s (largest is proof_a at 11.00s).
- Only ~26 seconds of the source (the very opening, before screen-share starts) is a pure full-frame webcam shot — used for HOOK. Every other piece used is the fixed screen-share+corner-PiP layout, confirmed static via frame checks at three widely-separated timestamps (645s, 3210s, 4258s).

## Why This Segment
**Multi-Clip Mashup** (ADR-0022) — the pieces that make this work are scattered from t=1s (the cold-open intro) to t=4262s (a closing sign-off 70+ minutes later); no single 45-60s window contains them all.

**How the candidate was found**: this source is far longer (74.6min) than any prior aiwork source (v1/v2: 15min, v3-v5: 45min) and is almost entirely developer-jargon screen-share — linearly watching or reading the 599-segment transcript for a usable, generalizable moment was not practical. Instead, the full transcript was keyword-scanned for words associated with a generalizable insight ("question", "clarify", "the reason", "the point", "why", etc.), which surfaced exactly one clean, quotable, jargon-free line at 53:41 into the stream:

> "So much of like misalignment from AI is AI not asking these questions, not understanding what your values are, what you prioritize over other stuff."

This became the video's spine (piece `teach`). Everything else was built around it: a real demonstration of the AI actually asking a clarifying question (`proof_q`, "How attached are you to the exact Remotion caption look?" — paraphrased in-caption to drop the "Remotion" jargon) immediately followed by Matt's own thoughtful, non-obvious answer (`proof_a`, "I am actually very attached to the exact remotion caption look... it took a long time to get it right... I don't want to get rid of it") — a real preference an AI would have had to guess at if it hadn't asked. A second keyword-scan hit, a vivid "fog" metaphor at 10:44 ("Notice how much fog there is in this... this is what [a good workflow] is doing... helping us find the way"), reinforces the resolution while its caption generalizes away the literal "Wayfinder" product name. This same-video-content-mining approach (grep the transcript by theme rather than by the actual literal source of the video) is new for this niche and is written up as a Stage 1 addition in `docs/WORKFLOW.md` for future long-source selection.

**Two-crop pipeline**: the source's opening ~26s (before screen-share starts) is a completely different camera composition (pure full-frame webcam) from every other piece used (VS Code/GitHub screen-share with a small, fixed corner-PiP webcam). A single shared crop, as used in `render_aiwork_v4.py`/`render_aiwork_v5.py`, would put the presenter's face out-of-frame for one of the two compositions — confirmed by testing the screen-share crop (`CROP_SCREEN_X=2333`) against the HOOK footage and finding it captured only bookshelf, no face. `CROP_HOOK_X=1255` was derived and frame-verified separately for the full-frame composition; `CROP_SCREEN_X=2333` (flush against the scaled canvas's right edge) was derived by measuring the PiP box's pixel boundary directly (a clear color transition at source x≈1428) and verified against three separate timestamps 3600s apart, confirming the OBS layout is static throughout the stream.

## Hook Formula Applied
- **Frame-0 face/action** (ADR-0017): cold open on Matt's real full-frame webcam intro (tight portrait, talking, gesturing) — not a title card, not a wide/establishing shot, and not the screen-share layout at all (confirmed via frame extraction at t=0/0.2/1.0/2.0, all pass).
- **Gap-not-resolved**: the self-authored HOOK text ("WHY DOES YOUR AI / KEEP GETTING / IT WRONG?") is fully self-authored (his real words here just say he's about to spend an hour on "Wayfinder" — not usable as the hook payoff per the established audience-fit pattern) and names neither the mechanism (AI not asking questions) nor the fix — only the pain-point question. Full Hook Gate checklist (all 7 items) run and passed before any cutting began.
- **Cause+effect not co-named**: neither the hook text nor the YouTube title asserts the specific mechanism up front — the title stays at "keeps getting it wrong" (effect only), the mechanism is reserved for the TEACH piece's payoff.
- **Payoff timing**: the TEACH piece (the real "misalignment... not asking these questions" quote) begins immediately at cumulative t=8.07s post-edit, right at the front edge of the ~5-10s ideal window (Stage 0 item 4) — the HOOK itself is a single 8s piece, so the gap opens and resolves as fast as this source's real footage allows.
- **Caption sync (ADR-0018)**: HOOK lines are all visible simultaneously from t=0 (feedback_caption_style_standard: no progressive reveal). Body captions (TEACH/PROOF_Q/PROOF_A/FIX_FOG/CTA) are self-authored or lightly-paraphrased quotes, word-synced to the real audio, using the established `keyword_burst_filters` technique (ported unchanged from `render_aiwork_v5.py`/`render_hardknocks_v3.py`).
- **Cadence (ADR-0016/0018)**: hard cuts between all 6 pieces plus caption-burst changes provide visual-change cadence throughout; within the HOOK piece itself (a single continuous shot, no internal cut), Stage 0 item 6's "motion liên tục" allowance is satisfied by Matt's own natural talking/gesturing plus the ever-present progress bar.
- **Hook text overlay timing/size**: verified via frame extraction that all 3 hook lines are visible at t=0.0s — not delayed. Sizes 44/44/64px, matching the established ADR-0018 addendum floor (~48-52px minimum for supporting text; hook keyword line at 64px exceeds it). Pixel-width checked via `PIL.ImageFont.getlength()` for every overlay string before rendering (see Value-Adds for the two long TEACH captions that initially overflowed and were shortened) — none of the final strings exceed the 1080px frame (smallest margin: 84.5px, since revised to 337.8px after shortening — see Known Issues).
- **Claim-strength flag** (non-blocking): the HOOK is a pain-point QUESTION, not a Money+Number or Contrarian-Reveal — consistent with this niche's established pattern (aiwork_v3-v5 all used question-form hooks, not money/contrarian ones). Logged per Stage 0 item 7, not treated as a failure.

## Value-Adds (Transformative Gate, ADR-0007 — min 2 required, must be distinct categories)
1. **this_or_that_overlay** — "AI THAT GUESSES" vs "AI THAT ASKS FIRST", shown during the FIX_FOG piece (pairs with its "that's what guessing feels like" / "finds the way" captions playing at the same time).
2. **data_viz_overlay** — a stat-card-style text card, "THE FIX: ASK BEFORE YOU BUILD", shown during the PROOF_Q/PROOF_A demonstration. No numeric chart exists for this source (unlike aiwork_v2's real 400-vs-15 comparison); reusing the hardknocks/aiwork convention that a data_viz_overlay can be a styled text card, not necessarily a plotted chart.

Commentary track: the self-authored HOOK text + paraphrased PROOF/FIX captions + CTA satisfy ADR-0007 gate item 1. **No TTS was used** — matches the established aiwork v1-v5 convention (TTS is scoped to Clip Curation Edit overrides only, per ADR-0021, and not used here); every word heard is Matt Pocock's own real voice.

**Transformative Gate item 3**: 48.68s raw / 4480.0s source = 1.09%, far under the 50% ceiling. Largest individual piece (`proof_a`) is 11.00s, under the 15s per-clip ceiling.

## Known Issues
- Two of the initially-drafted TEACH/FIX_FOG captions overflowed or nearly overflowed the 1080px frame when measured via `PIL.ImageFont.getlength()` *before* rendering (per the bacsihai_v7-derived Stage 3 discipline): "MISALIGNMENT FROM AI IS AI *NOT ASKING* THESE QUESTIONS" measured at 1259px (179px over), and "A GOOD PROCESS *FINDS THE WAY* THROUGH IT" measured at 995.5px (only 84.5px margin, too tight). Both were shortened before the first render rather than discovered via a failed frame-check — the first caption split into two sequential bursts ("MISALIGNMENT FROM AI IS" / "AI *NOT ASKING* THESE QUESTIONS"), the second trimmed to "A GOOD PROCESS *FINDS THE WAY*" (dropped "THROUGH IT"). No overflow found in the actual render (single render attempt, no re-render needed).
- The `data_viz_overlay` stat card ("THE FIX: ASK BEFORE YOU BUILD") sits over a busy part of the VS Code file-tree background (the `.github`/`.husky`/`.pnpm-store` rows) — legible in the frame-check (opaque box behind the text) but visually busier than ideal. Not a blocking issue since it doesn't obscure Matt's face or the dialogue captions; flagged for a possible position tweak if a future video reuses this exact card style.

## What To Check At 48h
Not yet uploaded — this section to be completed once uploaded and 48h have passed.
- Stayed to Watch / AVD vs. `aiwork_v5_prompt_bloat` (`jNM7dmy-cFE`, same niche, same official-channel-vs-non-official-channel comparison point now possible for the first time) and vs. `aiwork_v2_capability_curve` (`Mw7jeR6R6iE`, 43.6% Stayed to Watch, current aiwork project-best on record).
- Whether a non-official-channel source (an individual creator/practitioner) performs differently from the official Claude/Anthropic channel sources used in v1-v5 — first data point for this specific comparison.
- Whether the keyword-scan-for-insight source-selection technique (new for this niche, see Why This Segment) produces a video that holds attention as well as videos built from more traditionally-curated talks.
- Comment themes — watch for any comments about the "Wayfinder"/dev-tool origin leaking through despite the audience-fit captioning (i.e., whether non-developer viewers still find the underlying demo confusing).

## Post-Production Retro

### Hook Retro
- Verbal: none found — the self-authored question hook ("WHY DOES YOUR AI KEEP GETTING IT WRONG?") is a direct, deliberately generic reframe of the real "misalignment" insight; no stronger verbal alternative surfaced during review.
- Visual: same open item as `hardknocks_v4`/`hardknocks_v5` — no added zoom-punch or pattern-interrupt within individual pieces; cadence currently comes only from hard cuts between the 6 pieces and caption-burst changes. Not applied this round since the existing cadence already passed Stage 0's feasibility check (the HOOK piece's own natural talking/gesturing motion satisfies item 6's "motion liên tục" allowance).
- Did not run the `viral-video-analysis` skill against a comparison video for this retro — the source itself (a non-traditional livestream rather than a produced short) doesn't have a close comparable in the existing benchmark set; will fold into the 48h check instead if metrics suggest a hook problem.

### Workflow Delta
Yes — two additions made, both process gaps rather than one-off incidents:
1. **`docs/WORKFLOW.md` Stage 1** — added a note on keyword-scanning full transcripts for candidate insights when the source is ~1 hour or longer, since linear reading/watching stops being practical at that length (this video's source was 74.6min / 599 segments, well beyond any prior source used by this project). Cited this video as the source.
2. No new ADR needed for the non-official-channel source question — ADR-0026 already explicitly scopes its footage-reuse carve-out to *official* channels and already states that non-official-channel reuse (like this video's) falls back to the existing default Clip Curation Edit rules with no special case. This production doc simply confirms that reasoning holds in practice; nothing to change in the ADR itself.
