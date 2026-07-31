# ADR 0032: Language-Scoped Synthetic Narration with an Evidence-Gated Local TTS Default

**Date:** 2026-07-18
**Status:** Accepted

**2026-07-30 supersession note:** ADR-0039 supersedes this ADR's channel-scoped narrator assignment and retires `natural_talker_male_qwen_blog` from new production. Engine/model provenance, direct-listening and commercial-rights requirements remain active; the new Zack-style default is explicitly internal-only until consent/licensing clears its public-person reference.

## Context

The repository currently synthesizes some English narration with `edge-tts`, while many Clip Curation Edits deliberately preserve original source voices. Synthetic speech is not one uniform treatment: depending on the Video Type, it may carry an entire Short or only a Hook, CTA, or short Editorial Bridge. Finance and AI-education also need different brand tones.

The project is monetization-oriented, so “open source” is not sufficient by itself. The engine code, model weights, and selected voice must each have clear commercial-use terms. A local engine also must not lower perceived narration quality merely to remove a cloud dependency.

A grilling session considered a single global engine, language-specific engines, direct Python imports, a standalone CLI, a persistent local service, stock voices, and voice cloning. The session deliberately did not choose an integration boundary by opinion because startup and batching behavior need real execution evidence.

## Decision

1. Use a **language-scoped TTS architecture**, but implement and evaluate English only in the current phase. No Vietnamese engine is selected or planned yet.
2. Treat **Synthetic Narration** as a capability whose scope is chosen by Video Type: it may be full narration or only Hook, CTA, and Editorial Bridge spans.
3. Give each English Destination Channel its own stable **Narrator Voice Profile**. Finance and AI-education do not share a global narrator. A profile changes only when voice is the declared AB Variable of an Experiment.
4. Phase 1 may use either a stock voice or a fully synthetic designed voice artifact with verified model provenance. Cloning a human voice remains allowed only for the user’s own voice or a narrator with explicit consent and licensing. Conditioning a Base model on a locally generated synthetic VoiceDesign reference is permitted because no human or third-party voice is copied; an upstream demo WAV may be retained for listening comparison but must not be used as production conditioning without explicit authorization.
5. Run an English engine bake-off across Kokoro, Piper, Chatterbox, Qwen3-TTS, and OmniVoice, with the current `edge-tts` output as the production baseline. Before audio generation, each candidate must pass:
   - commercial-use review for code, model weights, and the exact selected voice;
   - local execution on the project Mac (Apple Silicon, 16 GB RAM);
   - no paid API requirement.
   OmniVoice's fixed-seed designed profile is admitted as an engine-quality sample, not yet as a production Narrator Voice Profile. It cannot become the default until repeated generations demonstrate stable identity or a separately authorized stable voice artifact is selected.
6. The user selects the preferred engine and voice by listening directly to representative samples. Automated checks remain preflight guards for invalid, silent, truncated, or malformed artifacts; they do not select the winner.
7. An open-source engine becomes the production default only when the user judges it equal to or better than the Edge baseline. Otherwise, retain `edge-tts` as the production fallback rather than accepting a quality regression.
8. Select the integration boundary only after the audio winner is known. On the winning open-source engine, compare:
   - direct Python API integration;
   - a standalone batch CLI that emits audio plus a machine-readable manifest.
9. Score the integration comparison on equivalent audio output, setup complexity, cold-start latency, per-Short batch latency, error handling, and interoperability with current Python renderers, the future TypeScript system, and AI agents. Do not add an HTTP service until measured startup or throughput data justifies one.
10. Treat **Voice Selection** and **Runtime Activation** as separate decisions. A canonical Narrator Voice Profile may be selected and versioned before its Narrator Runtime Adapter replaces the current temporary adapter.
11. Keep bake-off and integration harnesses disposable under `spikes/`; promote only the selected canonical profile and its identity-bearing reference artifact into `data/narrator-voices/`.

### Selection evidence — 2026-07-18

- The user's initial selection, `cinematic_documentary_host`, passed technical repeatability but was superseded before production assignment.
- The user explicitly confirmed `natural_talker_male_qwen_blog` as the canonical **Finance/English Narrator Voice Profile**. AI-education will select a separate profile later; this is not a global English narrator.
- The selected description comes from Qwen's official Qwen3-TTS launch blog. The blog does not publish its seed or decoding settings, so the upstream demo was used only during listening and is not stored or used for conditioning.
- A direct local attempt to synthesize the 53.92-second blog text with the VoiceDesign model failed EOS: valid content was followed by repeated “Yeah” until the 2,048-token cap, producing 163.84 seconds. The artifact was rejected rather than trimmed.
- Following Qwen's official **Voice Design then Clone** workflow, the system created a 13.44-second local synthetic reference from the exact description, then used `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-6bit` in ICL mode. The official demo was not used for conditioning.
- Two independent OS processes rendered the same four-part corpus under hash-locked Python environments and immutable model revisions. All four raw hashes and all four normalized hashes matched exactly; duration delta was 0.0 seconds; both corpus auditions passed ASR at sequence ratio 0.9691 and order/multiplicity-aware LCS word recall 0.9600.
- The identity-bearing local reference is versioned as `data/narrator-voices/natural_talker_male_qwen_blog/reference.wav` with SHA-256 `3272b6aa18551b4961871d9c119fa2e58860b8e77b455bdd3050f4020b671557`. Regenerable raw, normalized, audition, comparison, failed and superseded audio artifacts are intentionally not versioned.
- Selection is final, but Runtime Activation remains a separate task. Existing `edge-tts` calls are a temporary adapter until direct Python API versus standalone batch CLI is measured on this profile; they are no longer the preferred Finance voice identity.

## Considered Options

- **One engine for English and Vietnamese:** rejected because language quality differs and there is no current Vietnamese TTS requirement.
- **One narrator for every English Short:** rejected because finance and AI-education have different brand tones and a changing voice would confound unrelated Experiments.
- **Clone a human or the official Qwen demo in Phase 1:** rejected because public audibility is not conditioning authorization. Conditioning Qwen Base on a locally generated synthetic VoiceDesign artifact is accepted because no human or third-party voice is copied.
- **Choose direct Python imports immediately:** rejected because they couple every renderer to a Python package and cannot be evaluated fairly without measuring the alternative.
- **Choose a CLI immediately:** rejected because its startup overhead and batching ergonomics need measurement on the selected engine.
- **Replace Edge regardless of quality:** rejected because Synthetic Narration is part of retention quality, not an ideological infrastructure goal.

## Consequences

- The bake-off must run before the API-versus-CLI comparison; otherwise integration work could be spent on an engine that loses the listening test.
- Existing renderers remain unchanged during the spike.
- The canonical Finance narrator profile is versioned independently of renderer integration; `edge-tts` remains only a temporary Runtime Adapter.
- Exact voice licenses are reviewed individually; an engine-level permissive license does not automatically clear every downloadable voice.
- Retaining Edge beside a local engine is deliberate when the local candidate does not meet the listening bar.
- A future Vietnamese evaluation starts a separate language-specific decision rather than inheriting the English winner automatically.

## Related

- ADR 0003: AB Test One Variable
- ADR 0004: Language English
- ADR 0021: AI-Education TTS Commentary Layer
- ADR 0031: Cross-Story Hooks Are Comparisons, Not Controls
- `CONTEXT.md`: Synthetic Narration, Narrator Voice Profile, Authorized Voice Source, Canonical Narrator Voice Artifact, Narrator Runtime Adapter, TTS Selection Gate
- `data/narrator-voices/natural_talker_male_qwen_blog/profile.json`: canonical Finance narrator identity and provenance
