# ADR 0014: Dedicated Vision Model for Video Analysis

**Status:** Accepted
**Date:** 2026-07-08
**Deciders:** hungnb94

## Context

The Shorts project produces 18 videos/3-day cycle. Each video needs automated quality and content analysis:
- **Scene detection** — identify key moments, cuts, transitions
- **OCR** — read text/subtitles from video frames
- **Visual quality** — detect artifacts, composition issues, spec compliance
- **Content analysis** — verify HEIT structure compliance visually

The main chat model (`deepseek-v4-flash-free`) lacks vision capability. Adding a dedicated vision model enables automated video analysis without switching from the primary chat model.

## Decision

**Add GPT-4o as a dedicated vision model** via OpenAI API, routed through:
1. **Hermes `auxiliary.vision` config** — for built-in vision tool support
2. **A custom `video-analyzer` Hermes skill** — for pipeline-level video analysis

### Why GPT-4o

| Criterion | GPT-4o | Alternatives |
|-----------|--------|-------------|
| Vision quality | ⭐⭐⭐⭐⭐ | Gemini 2.5 Pro (⭐⭐⭐⭐⭐), Claude Sonnet 4 (⭐⭐⭐⭐⭐) |
| OCR accuracy | ✅ Excellent | Claude Sonnet 4 = similar, Gemini = slightly worse |
| Native video support | ✅ Yes (frame extraction built-in) | Claude = frame-by-frame only |
| Cost | $2.50/1M input tokens | Gemini $1.25 (cheaper), Claude $3.00 (more expensive) |
| API maturity | Mature, stable | All comparable |

GPT-4o offers the best balance of vision quality, OCR accuracy, native video support, and cost for this use case.

### Why not local model

Local vision LLMs (LLaVA, Qwen2-VL GGUF) require significant GPU memory and are 10-50x slower than API calls. On macOS without dedicated GPU, frame-by-frame analysis of 30-60s video would take minutes per clip — impractical for 18-video cycles.

### Why not use current model

`deepseek-v4-flash-free` (via local 9router) is text-only. No vision capability available.

## Frame Sampling Strategy

- **Keyframe only (3-5 frames/video)** — cost-effective
- Scene detection runs first (ffmpeg scene detect) to extract keyframes
- Each keyframe sent to GPT-4o Vision API for analysis
- JSON output: structured analysis with scenes, text detected, quality scores

## Integration Pattern

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Hermes Skill │────▶│  Python Script   │────▶│  GPT-4o API  │
│ video-analyzer│     │  analyze_video.py │     │  (Vision)    │
└──────────────┘     └──────────────────┘     └──────┬───────┘
                                                     │
                                           ┌─────────▼────────┐
                                           │  JSON Analysis    │
                                           │  Report          │
                                           └──────────────────┘
```

The `video-analyzer` skill uses Hermes `terminal` tool to call a Python script that:
1. Extracts keyframes via ffmpeg
2. Sends frames to GPT-4o Vision API
3. Returns structured JSON analysis

## Consequences

**Positive:**
- Automated video quality gate before upload
- Structured data for MAB optimizer (visual quality scores)
- OCR capability for verifying text overlays
- Reusable across all 7 video types

**Negative:**
- Additional API cost: ~$0.01-0.03/video (keyframe only) = ~$0.18-0.54/cycle
- Requires OpenAI API key and billing
- Pipeline dependency on external API availability
- 2-5s latency per video analysis

**Mitigations:**
- Keyframe-only strategy minimizes cost
- JSON parsing handles API errors gracefully (retry 3x, then skip)
- Results cached locally to avoid re-analysis of unchanged videos
