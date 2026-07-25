# aiwork_v3_prompt_bloat, "Why Adding More Instructions Makes Your AI Worse" (Multi-Clip Mashup)

## Status
| Field | Value |
|-------|-------|
| YouTube Video ID | Not yet uploaded |
| Rendered | 2026-07-12 |
| Uploaded | **Superseded by `aiwork_v4` — not to be uploaded.** User feedback: the ending (REINFORCE straight into CLOSE) skips any stated resolution and jumps to "thank you" without warning. Files stay on disk as the known-issues record (same precedent as `aiwork_v1`). See `docs/production/aiwork-v4-prompt-bloat.md`. |
| Metrics fetch after (48h rule) | N/A, will never be uploaded |
| Metrics status | N/A |

## Video Specs
- Duration: 50.8s
- Resolution: 1080x1920 (9:16 portrait)
- Codec: H.264 (libx264, crf 18/20), ~33fps (30fps source sped up 1.1x via `setpts`)
- Audio: AAC, 192kbps, 48kHz, stereo (single source-audio track, no TTS)
- File: `output/projects/aiwork/final/2026-07-12-aiwork_v3_prompt_bloat.mp4` (7.9MB)
- Render script: `pipeline/aiwork/render_aiwork_v3.py`

## YouTube Title
Why Adding More Instructions Makes Your AI Worse

## YouTube Description
See `output/projects/aiwork/final/2026-07-12-aiwork_v3_prompt_bloat.txt` (credits the source channel per ADR-0021's brand-sensitivity mitigation, still applicable — same mitigation, second official-channel source).

## Source
- Channel: Claude (Anthropic's own official YouTube channel)
- Source video ID: `mWvtOHlZM-I`, "Tool, skill, or subagent? Decomposing an agent that outgrew its prompt", presented by William Steuk (Applied AI, Anthropic) at Code with Claude London, 2706.0s (~45:06), max available quality confirmed (1080p is the ceiling, no 4K exists for this source)
- **Second official-channel source for this niche** (first was `tP4MGcJ80Y0`, aiwork_v1/v2) — resolves ADR-0021's open policy question via new ADR-0026 (case-by-case reuse now standing policy for this niche, no per-video Ask-First needed, provided Transformative Gate + visible credit continue to apply)

## Why This Segment

A grilling session (`/grill-with-docs`) preceded this build and resolved, in order: (1) footage-reuse policy for a second official-channel source → ADR-0026, (2) audience-fit — this source is a developer-conference workshop (system prompts, evals, CLI, Claude Managed Agents), squarely NOT the "knowledge worker, not developer" audience ADR-0020 sets for this niche → decision: extract only the most generalizable insight, avoid code/CLI closeups, keep the ADR-0020 audience as-is (do not expand it), (3) sub-format: Multi-Clip Mashup (ADR-0022), forced by (2) since the generalizable moments are scattered across a 45-minute talk with heavy technical content between them, (4) commentary: caption/text-overlay only, no TTS (matches aiwork_v2's proven pattern, avoids aiwork_v1's TTS-delays-hook problem), (5) value-adds: `this_or_that_overlay` + `data_viz_overlay`, (6) hook thesis: "Why does adding more instructions make your AI worse?" (opens a gap, doesn't co-name cause+effect, per the bacsihai v5 pitfall).

**Execution found a problem the grilling session's transcript-only planning missed** (see Workflow Delta): the plan's original context and demonstration candidate windows (`~213-234s`, `~1571-1602s`) turned out, on frame extraction, to be a full-screen code-architecture slide and a raw CLI/chat terminal recording respectively — both unusable under decision (2). Re-scanned frames across the whole video: the ONLY presenter-visible (non-slide, non-CLI) footage is the intro problem-setup narrative and the closing sign-off — everything else is slides or a terminal screen recording. The final cut uses six pieces, all from those two safe windows, all sharing one fixed wide camera shot (single constant crop, no time-varying crop needed — verified via frame extraction at t=20s through t=2700s that the camera never changes angle):

| # | Role | Range | Raw dur | Quote (source's own words, for reference — captions are a reframe, see Value-Adds) |
|---|------|-------|---------|-------|
| 1 | HOOK | 45.48-54.60 | 9.12s | "So folks, imagine that you built and shipped an agent to solve a problem. I'm sure that's something that a lot of the folks in this room have actually done." |
| 2 | ESCALATE | 55.56-67.50 | 11.94s | "And imagine that this agent worked fantastic, right? But it worked so well that a few weeks after shipping, you were asked to add some additional capability to the agent." |
| 3 | COMPLICATION-1 | 74.12-82.16 | 8.04s | "This pattern continued and continued until before you know it, your system prompt had grown to become several hundred lines long." |
| 4 | COMPLICATION-2 | 82.58-97.54 | 14.96s | "You have dozens of tools and sub agents that exist for your agent. And because of the complexity, you've started to see regressions in the areas that your agent was previously accelerating in. So if this is you, you're not alone." |
| 5 | REINFORCE | 98.04-104.78 | 6.74s | "We see this type of scenario happen pretty commonly with customers and actually with ourselves included in that." |
| 6 | CLOSE | 2693.32-2698.30 | 4.98s | "Thank you for spending your day at Code with Claude in London. I hope you have a great rest of your day. Appreciate it." |

All 6 pieces are <15s (ADR-0007 item 3; COMPLICATION-2 is the longest at 14.96s, right under the ceiling). Total raw 55.78s → 50.8s final after the 1.1x speed-up, landing near the top of the 45-60s range per the known preference for authentic-length cuts over the tightest possible trim.

A deliberate gap between clips 2 and 3 (67.50→74.12, ~6.6s of source skipped) drops a redundant restatement ("A few weeks after that, you received more business requirements...") that repeats clip 2's beat — tightens pacing without losing information.

The real "400 lines → 15 lines" numbers and the source's tool/skill/subagent framework are both real facts from the talk, but neither is delivered via source footage — see Value-Adds.

## Hook Formula Applied
- **Cold open on the presenter** (t=0, wide shot, cropped tight via a constant `crop=1080:1920:2073:0` offset that centers the podium) — passes Hook Gate item 1. This source offers no tight/close presenter shot anywhere (confirmed by scanning frames across the full 45 minutes) — the wide shot, cropped, is the best available, weaker than aiwork_v2's tight-portrait ideal but still a clear, centered, front-facing face at frame 0.
- **Fully self-authored hook question, not a source quote**: "Why does adding more instructions make your AI worse?" is not what the presenter says in this clip (he says "imagine you built and shipped an agent..." — developer-coded per the audience-fit decision). This is the first aiwork video where the hook caption diverges completely from the underlying spoken audio rather than captioning/quoting it — see Hook Retro.
- **Word-burst hook captions t=0-9.12s** (ADR-0018), 4 bursts (~1.7-3.3s each), one keyword ("WORSE?") emphasized in yellow, appearing at t=0 (no delay, per the hook-text-prominence rule).
- **Body captions in short 3-4s bursts** for the remaining 5 clips, self-authored reframes of the source's own words (strips "agent"/"system prompt" jargon per the audience-fit decision) rather than verbatim quotes.
- **Progress bar** (bottom edge) spanning the full assembled timeline.

## Value-Adds (Transformative Gate, ADR-0007, min 2 required)
1. **data_viz_overlay**: a custom before/after bar chart (`pipeline/aiwork/make_chart_v3.py`, indigo palette matching v1/v2's style), 400 lines → 15 lines, built from the real numbers the presenter states later in the talk (t≈226s and t≈2506s) — **neither of which is shown as footage** (both timestamps are slide-heavy, dropped per the audience-fit decision). Shown during REINFORCE (global t≈44.3-50.8s) as the concrete proof point backing "sound familiar?".
2. **this_or_that_overlay**: "ONE GIANT PROMPT" vs "SMALL FOCUSED STEPS" — a deliberately generalized 2-way version of the source's literal 3-way tool/skill/subagent framework (dropped the literal jargon split per the audience-fit decision, same reasoning as dropping the CLI/slide footage). Shown during COMPLICATION-2's "SOUND FAMILIAR?" beat (global t≈39.4-44.06s).

Commentary track: captions alone (no TTS), same as aiwork_v2's decision, still holds — captions here are a full reframe rather than quotes, but the mechanism (text overlay satisfying ADR-0007 gate item 1) is unchanged.

## Transformative Gate, item 3 note
Cut duration 55.78s raw (50.8s final) / 2706.0s source = 2.1%, well under the 50% ceiling — the lowest fraction-of-source used by any aiwork video so far, a direct consequence of the audience-fit decision excluding ~95% of the talk's runtime as visually unusable. Every individual piece is <15s (COMPLICATION-2 longest at 14.96s).

## Known Issues (corrections made during this production)
1. **Transcript-only candidate selection missed 2 of 4 non-hook windows being visually unusable**: the grilling session picked context (~213-234s) and demonstration (~1571-1602s) candidate windows based on transcript content alone. Frame extraction during Stage 2 found both are a full-screen code-architecture slide and a raw CLI/chat terminal screen respectively — neither usable under the audience-fit decision, unlike what the spoken words alone suggested. Required scanning frames across the entire 45-minute source to find the only two safe (presenter-visible) windows, and replacing the original 5-clip plan with a 6-clip plan built entirely from those two windows. Generalized into `docs/WORKFLOW.md` Stage 1 (see Workflow Delta).
2. **This source has no tight/close presenter shot at all**: unlike `tP4MGcJ80Y0` (v1/v2's source, which cuts between a tight portrait and a wide stage shot), this source holds one single fixed wide camera angle for its entire 45 minutes (verified at t=20s, 46-130s, 2600-2706s). Mitigated with a constant crop (`crop=1080:1920:2073:0`) that brings the presenter to occupy roughly a third of the vertical frame — better than the raw wide shot, but still smaller/more distant than v2's tight-portrait hook frame.
3. **A `?` typo in the source's own captions is irrelevant here**: not applicable — this video uses zero source-caption text (full reframe), so no source-caption artifacts (e.g. "Claw" for "Claude" seen in the raw auto-captions used for planning) carry through to the final captions.

## What To Check At 48h
- N/A — not yet uploaded. Fill in after Stage 6.
- Once uploaded: whether a fully self-authored hook caption (diverging completely from the underlying spoken audio) retains viewers as well as v1/v2's approach of captioning/quoting the source's own words — this is a genuinely new caption-authoring pattern for this niche, untested against real retention data.
- Whether the smaller/more-distant presenter frame (no tight-portrait option available from this source) measurably hurts hook retention compared to v2's tight-portrait cold open.
- Whether reusing Anthropic's own official-channel footage for a second video in a row (now under the standing ADR-0026 policy) draws any visible brand-relationship reaction.

## Post-Production Retro

### Hook Retro (bắt buộc, mọi video, proactive)
- **Verbal**: found something worth recording, promoted to a note (not yet a rule — untested). This is the first aiwork video whose hook caption is a full reframe rather than a quote/paraphrase of the source's own spoken words at that timestamp. This was forced by the audience-fit decision (the presenter's actual words at t=0 name "agent," developer-coded), not chosen freely — worth flagging because it means the commentary-track captions here carry more of the actual meaning-making than in v1/v2, where captions mostly transcribed what was already said. No existing Hook Gate item covers "does the caption need to literally relate to the audio" — it doesn't have to, since the audio's role here is tone/energy/pacing, not literal content. Not promoted to a WORKFLOW.md rule since it's a one-video data point, not yet a generalizable pattern; revisit after metrics.
- **Visual**: found something, did not promote to a rule (already covered). Frame 0 here is a distant wide shot (constant crop only, no tight-portrait option existed in the source at all) — weaker than v2's tight-portrait cold open per the existing Stage 0 item 1 preference note (which already prefers tight/close shots when the source offers a choice). This source simply doesn't offer that choice; no new rule needed, the existing preference note already covers the "when available, prefer tight" logic correctly — this is a source-constraint, not a process gap.

### Workflow Delta (bắt buộc, mọi video, reactive)
Yes, this production hit a case not previously covered:
1. `docs/WORKFLOW.md` Stage 1's candidate-selection step only explicitly required a frame check for the HOOK window (via Stage 0). Non-hook candidate windows chosen from transcript content alone had no explicit frame-check requirement before being locked into the plan. This production's grilling session picked 2 non-hook windows that turned out to be slide/CLI-only visuals, discovered only during Stage 2 execution, forcing a full mid-production re-plan. This is a procedural gap (the underlying "verify visually, don't guess" discipline already exists elsewhere in this repo, e.g. aiwork_v2's Known Issue #2), not a wholly new rule → fixed directly in `docs/WORKFLOW.md` Stage 1 (added a bullet requiring a 1-frame check per candidate window, not just the hook window, for long conference/talk-style sources) rather than a new ADR.
