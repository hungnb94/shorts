# ADR 0017: Hook-Window Source Selection — Frame 0 Must Show a Human Face

**Date:** 2026-07-09
**Status:** Accepted

## Context

We A/B compared two clip-curation Shorts produced by visually similar pipelines (source segment → Pexels overlays → drawtext subtitles → hook bar + progress bar):

| Video | ID | "Stayed to watch" | Pipeline |
|-------|----|-------------------|----------|
| bacsihai V1 ("NHỊN ĂN MÀ VẪN KHÔNG GIẢM CÂN?") | YQTWHqTS1e8 | **8.6%** | `render_bacsihai_v4.py` |
| Dangote ("Worth $40B Drives a Toyota") | ChWLcE3OYpA | **50%** | Dangote renderer (ADR-0016) |

The instinct was: "same editing style, why such a huge gap?" Pixel-statistics inspection of both videos at frame level disproved this — the gap is NOT in the editing, it is in **what the first 3 seconds show**.

## Evidence (PIL pixel statistics on real frames)

### BAD (8.6%), hook window 0-3s
| t | avg RGB | near-white % | skin-tone % | stddev | interpretation |
|---|---------|--------------|-------------|--------|----------------|
| 0.5s | (248,235,237) | **85.2%** | **0.06%** | 25 | flat white/pink static card |
| 1.5s | (232,220,224) | 79.9% | 0.06% | 66 | same card, slight text |
| 2.5s | (232,220,224) | 79.9% | 0.06% | 65 | frame 1.5→2.5 nearly identical |
| 5.0s | (149,136,129) | 0.1% | 28.6% | 47 | first frame with a human face |

The BAD video's source segment starts at `src_start=304.5s` of `8vM7rPWzTlI`. Per the auto-subtitle, 304.5s is the **title-card transition** ("...đầu tiên sẽ là con số 5" = introducing "mistake #5"). Source frame 304.5s is a static pink/white text graphic — not the doctor speaking to camera. The first human face does not appear until t≈5s.

### GOOD (50%), hook window 0-3s
| t | avg RGB | near-white % | skin-tone % | stddev | interpretation |
|---|---------|--------------|-------------|--------|----------------|
| 0.5s | (113,107,103) | 10.3% | **19.0%** | 80 | Dangote's face, full detail |
| 1.5s | (121,113,106) | 10.5% | 19.8% | 80 | face, motion, zoompan |
| 2.5s | (117,107,100) | 10.8% | 21.3% | 82 | face + overlay detail |

GOOD starts on Dangote's face in the Forbes interview at t=0. Human present, motion present, detail present from the very first frame.

### Cross-check against retention research (`youtube-retention-benchmarks.md`)
- 65% of viewers decide swipe in the first 3 seconds (VirVid 2026).
- Videos with pattern interrupts every 3-5s retain 40-60% more.
- BAD's first Pexels overlay is at t=5s → a 5-second dead zone at the most critical moment. GOOD has continuous zoompan motion from t=0.
- 6.1% stayed = algorithm stops distributing (Shortimize 2026). 8.6% is in the same "very poor" tier — the algorithm deprioritized it after the swipe-away signal.

## Decision

**The source-segment start point for any Clip Curation Edit MUST satisfy the Hook-Window Rule: the frame at t=0 of the cut must contain a human face (skin-tone ≥10% by pixel statistics, OR visually confirmed).** Title cards, text-only graphics, slides, B-roll establishing shots, and "numbered list" transitions are forbidden as segment starts.

Selection procedure for every clip-curation variant:
1. Candidate segment start frame is extracted and pixel-inspected (skin-tone %).
2. Reject any candidate where skin-tone < 10% at t=0 AND t=0.5s of the cut.
3. If the only compelling content at a timestamp is a static graphic, shift the start backward/forward to the nearest shot where the speaker is on-camera.
4. First Pexels/value-add overlay must land no later than t=2s — never t=5s.

This rule sits ABOVE the Contiguous VO constraint (ADR-0010): contiguity must be preserved, but the contiguous range is selected so that frame 0 shows a person.

## Consequences

- Eliminates the single largest known cause of sub-10% retention in this project (static-card hook).
- Source-selection step becomes a gating check, not just a creative choice — it is now a hard pipeline rule.
- Some segments we would previously have used (like bacsihai 304.5s) become unusable at their natural start point; they must be re-anchored to a face shot.
- Does NOT solve the secondary confounds (Vietnamese vs English niche, channel maturity) — those remain noise until we get more samples. But the pixel evidence is strong enough to act on now: a 5-second face-less static open is a known retention killer regardless of language.

## How this connects to existing docs

- `CONTEXT.md` → **Hook**: "0-2 giây đầu video." This ADR sharpens it: the hook window's *frame 0* must contain a human face for clip-curation types. (Glossary updated.)
- `youtube-retention-benchmarks.md` → "6.1% stayed = very poor." bacsihai V1 at 8.6% is in that tier; this ADR is the corrective.
- `source-channel-patterns.md` → Money+Number hooks outperform generic questions. BAD's hook ("NHỊN ĂN MÀ VẪN KHÔNG GIẢM CÂN?") is a generic question, compounding the problem.

## Verification

For any future clip-curation render, before upload:
```bash
ffmpeg -ss 0 -i <final.mp4> -frames:v 1 -q:v 2 /tmp/hook0.jpg
python3 ~/.hermes/skills/productivity/image-vision-fallback/scripts/inspect_image.py /tmp/hook0.jpg
# REQUIRE: skin-tone ≥ 10%
```
Also sample t=0.5s and t=2s the same way. If all three fail the skin-tone threshold, re-anchor the segment start before uploading.

## Open question (agent judgment, user did not confirm)

Exact retention-graph shape of YQTWHqTS1e8 (drop-off concentrated in 0-3s vs 3-15s) was not confirmed from YouTube Studio. The pixel evidence (85% near-white static frame for the full 0-3s window, 0% face until t=5s) makes 0-3s drop-off the overwhelming likely explanation, but a per-second retention graph would confirm whether the cliff is at ~1s (hook text unreadable) or ~5s (face arrives too late). User to verify when convenient.
