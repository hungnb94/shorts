# Ronald Wayne Qwen3 Voice Clone Design

**Date:** 2026-07-25  
**Status:** Approved by user  
**Scope:** Replace only the synthetic narrator in the Ronald Wayne Short; preserve visuals, script semantics, timing, music structure, and two direct Ronald Wayne source-voice clips.

## Goal

Create a more energetic documentary narrator inspired by the delivery in Zack D. Films Short `LFdQAkLvhUc`, using local Qwen3-TTS BaseModel zero-shot cloning. Produce a separate v2 artifact for comparison without overwriting v1.

## Reference and Attribution

- Reference URL: `https://www.youtube.com/shorts/LFdQAkLvhUc`
- Verified metadata: Zack D. Films, “The Folktale Of The Farting Daughter In Law 🤢”, 42 seconds.
- The reference is used only for narrator conditioning and delivery analysis.
- Production documentation must state that narration is synthetic and that Zack D. Films did not participate in or endorse the Ronald Wayne video.
- The cloned reference and model output must not be presented as an authentic recording of Zack D. Films.

## Selected Architecture

1. Download the reference audio with authenticated yt-dlp access and retain it only outside the repository.
2. Extract a clean 3–8 second voice window and separate/reduce music and sound effects before conditioning.
3. Use `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-6bit` at immutable revision `34ff5318365b59cba9c03ff729f2eee0814caf72`.
4. Generate each existing TTS segment independently with exact reference text and deterministic seeds.
5. Reject outputs with missing words, repeated tails, clipped phonemes, excessive noise, or raw duration requiring more than `1.42×` time compression. Use Rubber Band R3 for pitch-preserving compression; do not use FFmpeg `atempo` for these fitted Qwen takes.
6. Slot-fit accepted outputs to the existing timeline. Preserve the CBS and NextShark Ronald Wayne source-voice segments.
7. Rebuild only the audio timeline and remux it with the verified 40-beat video stream into a separate v2 file.

## Files

- Create: `data/narrator-voices/ronald_wayne_zack_style_qwen/profile.json`
- Create: `pipeline/ronaldwayne/generate_ronaldwayne_qwen_tts.py`
- Create: `output/projects/ronaldwayne/2026-07-25-ronald-wayne-v2-qwen.mp4`
- Create: `output/projects/ronaldwayne/checks-v2-qwen/`
- Create: `docs/production/ronald-wayne-v2-qwen.md`
- Modify only if required: `pipeline/ronaldwayne/render_ronaldwayne_v1.py` to accept an explicit TTS directory/output path without changing v1 defaults.

## Quality Gates

- Narration content recall: all required normalized words recovered by final-MP4 ASR, except documented proper-name substitutions that do not alter meaning.
- No repeated tail or skipped sentence in any Qwen segment.
- Maximum post-generation tempo: `1.42×` via Rubber Band R3. Empirical generation showed that the BaseModel clone path ignores the exposed native `speed` parameter; the highest required ratio was `1.40541×` for the unchanged CTA copy. Final ASR must still recover 100% of normalized content.
- Final duration: exactly `60.000s`.
- H.264 1080×1920 at 30fps; AAC stereo 48kHz.
- 40 contiguous visual beats and 40 keyframe boundaries.
- Full FFmpeg decode without errors.
- Zero black-frame events and zero freeze events over 1.55 seconds.
- Loudness target approximately `-16 LUFS`, true peak no higher than `-1.5 dBTP`.
- Direct Wayne quotes remain byte/source-window equivalent in meaning and timing.
- v1 file checksum and contents remain unchanged.

## Failure Handling

- If the selected reference contains audible music/SFX after separation, test a second clean window instead of conditioning on contaminated audio.
- If Qwen omits or repeats words, retry that segment with a new deterministic seed and simpler punctuation; never conceal missing speech with captions.
- If any segment requires over `1.42×` Rubber Band R3 compression, rewrite punctuation/chunk boundaries without changing factual meaning. This revised bound follows an executed spike: Qwen preserved the selected timbre but spoke the fixed v1 copy more slowly than the source reference; R3 preserved pitch and the resulting final-MP4 ASR recovered all normalized words.
- If the local MLX runtime cannot be installed or the pinned model cannot be verified, stop and report the exact blocker; do not silently fall back to Edge TTS.
