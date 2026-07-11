# ADR 0023: Viral Video Analysis Skill

**Status:** Accepted
**Date:** 2026-07-11
**Deciders:** hungnb94

## Context

The project needed a repeatable way to reverse-engineer externally-sourced viral Shorts
(hook, cuts, overlays, sound design, audience psychology) and turn findings into concrete
AB-test proposals for this project's own videos. This had previously been done once, by hand
(`docs/research/hook-benchmarks-2026-07/REPORT.md`, which fed ADR-0018 and several `CONTEXT.md`
terms) but was not a repeatable tool.

Relevant tooling already existed but was scattered and inactive in Claude Code:
`~/.hermes/skills/shorts/video-analyzer` (ffmpeg scene-detect + **GPT-4o Vision**, built for
QA'ing this project's own pre-upload videos — see ADR-0014), `~/.hermes/skills/video/value-
added-editing-viral-shorts` (hook-pattern extraction from one viral channel), `~/.hermes/skills/
video/clip-curation-edit` (frame-0/hook-window pixel-stat postmortem methodology, ADR-0017),
and `~/.hermes/skills/productivity/image-vision-fallback` (`inspect_image.py`, a pure-PIL
pixel-statistics tool with no vision-API dependency).

## Decision

Build a new, project-local Claude Code skill, `.claude/skills/viral-video-analysis/`, that
ports the reusable *logic* from the above Hermes skills rather than calling them, and adds one
genuinely new capability (automated sound-design analysis).

### Why not call the existing `video-analyzer` skill directly

`video-analyzer` calls GPT-4o Vision via the Hermes agent runtime, because Hermes's default
chat model (`deepseek-v4-flash-free`) has no vision capability (ADR-0014's reasoning). This
project's actual production driver is Claude Code, which has native multimodal vision — Claude
can read an extracted keyframe directly via the Read tool with no API key, no per-call cost,
and no external dependency. `docs/WORKFLOW.md`'s Stage 0 already reached the same conclusion
for its own frame-0 check ("Không có tool tự động check frame... chủ đích giữ là visual
judgment thủ công"). `extract_keyframes.py` therefore keeps `analyze_video.py`'s ffmpeg
scene-detection and frame-extraction logic verbatim in spirit, but drops the `analyze_frames`/
`encode_frame` GPT-4o call entirely. `inspect_image.py` is carried over unchanged as optional
quantitative backup evidence (skin-tone %, near-white %), not the primary judgment mechanism.

### Why project-local, not `~/.agents/skills/` (global)

The skill's logic is inseparable from this project's own vocabulary and gates (HEIT, Hook,
Hook-Window Rule, AB Variable, Stage 0/5 of `docs/WORKFLOW.md`) — it reads and writes
`CONTEXT.md`, `docs/adr/`, `docs/WORKFLOW.md`, and `AGENTS.md` directly. A skill this coupled
to one repo's domain model belongs next to `log-video`/`dedup` in `.claude/skills/`, not in the
cross-project `~/.agents/skills/` tier (domain-modeling, remotion-best-practices, etc.), which
holds only genuinely repo-agnostic skills.

### Why only Stage 5, not Stage 0

Stage 0 (Hook Gate) is a hard blocking gate on the project's own candidate segment, deliberately
kept as fast manual visual judgment before any cutting starts. Wiring a multi-phase
external-video analysis skill into that gate would slow down every single video's pre-cut
checklist for a benefit (reverse-engineered competitor pattern) that's better suited to the
reflective, already-slower Stage 5 (Post-Production Retro), where the Hook Retro and Workflow
Delta subsections already ask exactly the questions this skill is built to answer with
evidence instead of guesswork.

### New capability: sound-design analysis via librosa

No tool in the repo analyzed sound effects/music timing automatically (`pipeline/tools/`
scripts only transcribe speech). Added `scripts/analyze_audio.py`: ffmpeg extracts the audio
track, `librosa` detects onset/beat/tempo and RMS energy jumps, and (given cut timestamps)
flags whether visual cuts land "on the beat" — a concrete, checkable sound-design signature
that previously required subjective re-listening. `librosa` was installed into this repo's
existing `.venv` (already used for `mlx-whisper`/`Pillow`/`numpy`/`scipy`).

## Consequences

**Positive:**
- No new external API key/cost — everything runs on ffmpeg + Claude's native vision + local
  Python (librosa), fully offline-capable except for the `yt-dlp` fetch step.
- Findings flow into the same docs (`CONTEXT.md`, `docs/adr/`, `docs/WORKFLOW.md`,
  `AGENTS.md`) that already govern production, instead of living in a disconnected report.
- Every analysis session ends in a concrete, falsifiable "Suggested Next Video / AB-Test"
  proposal (see `references/report-template.md`), keeping this aligned with the project's
  "everything is an AB test" philosophy (ADR-0003) rather than producing inspiration with no
  clear next action.

**Negative / accepted tradeoffs:**
- `librosa`'s onset/beat detection is heuristic and can miss soft sound effects or mis-tag
  speech transients as percussive onsets — documented as a stated limitation in
  `references/sound-design.md`, not silently treated as ground truth.
- The existing `~/.hermes/skills/shorts/video-analyzer` (GPT-4o-based) is left as-is for its
  original purpose (own-video pre-upload QA); this ADR does not migrate that use case, only
  adds a separate, purpose-built skill for external/competitor video analysis.
