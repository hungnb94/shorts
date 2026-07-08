# Vision & Video Analysis Glossary

| Term | Definition |
|------|------------|
| **Keyframe** | A representative frame extracted from a video at a scene change boundary. Used for analysis instead of every frame. |
| **Scene detection** | Process of identifying boundaries between distinct visual scenes/clips in a video. |
| **Frame sampling** | Strategy for selecting which frames to analyze: keyframe-only, 1fps, 2fps, etc. |
| **Vision model** | An LLM capable of understanding images/video frames (e.g., GPT-4o, Claude Sonnet 4). |
| **OCR (Optical Character Recognition)** | Extracting text content from images/video frames. |
| **Video analysis** | Programmatic inspection of video content using a vision model: scene detection, OCR, quality check, composition analysis. |
| **auxiliary.vision** | Hermes Agent config section for routing vision tasks to a dedicated vision-capable model. |
| **Model routing** | Directing specific tasks (e.g., vision analysis) to different models/providers than the main chat model. |
| **HEIT compliance** | Verifying a video follows Hook→Explain→Illustrate→Teach structure by analyzing frame content and timing. |
| **Visual artifact** | Unintended visual glitch in rendered video: blockiness, color banding, missing elements, wrong aspect ratio. |
| **Composition check** | Verifying video layout meets specs: 9:16 aspect ratio, text within safe zone, proper element positioning. |
| **JSON analysis report** | Structured output from vision model containing scenes array, text_detected, quality_scores, and issues. |
