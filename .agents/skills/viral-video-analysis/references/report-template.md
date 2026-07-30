# Report Template

Mirrors the structure of `docs/research/hook-benchmarks-2026-07/REPORT.md` (the existing,
proven precedent) with one addition: a mandatory "Suggested Next Video / AB-Test" section.
Write the actual report to `docs/research/<topic-slug>-<date>/REPORT.md`. Section 2
(cross-video synthesis) only applies when analyzing more than one video — for a single
ad-hoc video, skip straight from section 1 to section 3.

```markdown
# Video Analysis: <short description> (<video count> video(s), <channel/creator>)

## 1. Per-video breakdown

### 1.1 `<video_id>` — <channel>, "<title>" (<view count>, <channel age if notable>)

- **Hook line (0-2s, verbatim)**:
- **Hook pattern classification**: (see references/hook-patterns.md)
- **Gap-not-resolved check**: pass/fail + why
- **Frame-0 check**: face/action present? title-card violation? (references/frame-and-cadence.md)
- **Cut cadence (0-5s)**: gap list in seconds
- **Sound design**: cut-on-beat rate, notable energy jumps (references/sound-design.md)
- **Overlay/text observed**: on-screen text, caption sync timing
- **Structure**: hook / body / CTA duration breakdown
- **Why it worked**: synthesis of the above, in prose

<repeat 1.2, 1.3... per video>

## 2. Cross-video synthesis (pattern appearing in >=N/M videos)

<table: pattern x how many videos x notes>

### Comparison against current Hook taxonomy (CONTEXT.md: Context / Contrarian / Intrigue)

### Patterns that don't fit the existing taxonomy

## 3. Audience psychology from comments (full read, not a sample)

<per-video or cross-video prose per references/comment-psychology.md's 4 points>

### Niche-transfer caveats

## 4. Playbook — apply immediately when writing the next hook/edit

<concrete DO/DON'T list>

## 5. Suggested Next Video / AB-Test

For each pattern strong enough to act on:
- **Niche**: which of the 3 (finance / health-VN / AI-education) and why this pattern
  transfers there specifically
- **AB Variable exercised** (CONTEXT.md → AB Variable): Video Type / Hook Type / Value-Add Type
- **Concrete hook line draft** for the next video in that niche
- **What would falsify this**: what result (AVD, Stayed to Watch) would mean the pattern
  didn't transfer, so this is a real experiment and not just inspiration

## 6. Limitations of this analysis

- Confounds not controlled for (language, niche, channel maturity, algorithm/timing luck)
- librosa onset/beat detection is heuristic (see references/sound-design.md)
- Sample size caveats if only 1-2 videos analyzed
```
