# Ronald Wayne v3 — Qwen Caption/Visual Synchronization Record

**Date:** 2026-07-25  
**Status:** Technical verification pass; subjective listening/viewing remains a publication gate  
**Artifact:** `output/projects/ronaldwayne/2026-07-25-ronald-wayne-v3-qwen-synced.mp4`

## Why v3 exists

Qwen fit the same large narration slots as the former Edge voice, but distributed words and pauses differently. The v2 visual edit still asserted several later phrases one beat early. v3 preserves the verified Qwen audio and rebuilds the visual/caption timing from final-MP4 ASR word timestamps.

## Synchronization strategy

- Preserve forty semantic beats of exactly 1.5 seconds.
- Use `checks-v2-qwen/final-asr/final.json` as the word-timing source.
- Resolve each caption to an ASR phrase anchor.
- Round reveal time upward to the next 30fps frame so captions cannot lead audio.
- Keep progress, source label, and watermark visible before caption reveal.
- Use one intentional hold at 37.5–39.0s instead of introducing a new claim during silence.
- Replace text-heavy background cards with graphic-only backgrounds where embedded labels would reveal a claim early.
- Stream-copy the verified v2 AAC audio without re-encoding or regeneration.

## Semantic remaps

The main corrections are:

- Apple structure → not a corporation → personal liability now follows the spoken sequence.
- Jobs/Woz young and broke now precedes Wayne’s age and assets.
- Wayne’s house/car/money appears only when that asset list is spoken.
- Paperwork → building → inventions follows Qwen’s actual clause timing.
- CTA is ordered as lock verdict → sell/stay → like/subscribe/comment.
- Payoff is ordered as no regret → regret question → original contract → $500 → 2011 → $1.59M.
- Final verdict is ordered as setup → biggest fool → walking away/freedom.

## Beat 36 timing defect and fix

The first v3 render exposed a real renderer defect in the direct-quote beat:

- output-level accurate seek retained long source timestamps;
- FFmpeg evaluated the caption `enable` expression against those timestamps;
- `THAT, I REGRET` therefore appeared from the first frame.

The fix uses a five-second input preroll, exact `trim`, and `setpts=PTS-STARTPTS` before caption compositing. Frame-accurate BEFORE/AFTER inspection then confirmed:

- `54.300s`: Ronald Wayne visible; caption absent;
- `54.400s`: Ronald Wayne visible; `THAT, I REGRET` present.

## Final artifact evidence

| Check | Result |
|---|---|
| Artifact SHA-256 | `b673325c79548e83959e690d98ec6295bee99cee2793b85413267fbcf03be63b` |
| File size | 18,927,744 bytes |
| Duration | 60.000s |
| Video | H.264, 1080×1920, 30fps |
| Audio | AAC, stereo, 48kHz |
| Keyframes | 40 |
| Full FFmpeg decode | Pass |
| Manifest beats | 40 |
| ASR-anchored beats | 39 |
| Intentional hold beats | 1 |
| Premature captions | 0 |
| Maximum caption lag | 0.380s |
| Final ASR | Exact v2 match, 152/152 normalized tokens |

## Audio preservation

| Stream | SHA-256 |
|---|---|
| v2 AAC elementary stream | `5d2c3bde3b943afc3b6a235341b7838109c1001f680febcbbac036bacc08d7a4` |
| v3 AAC elementary stream | `5d2c3bde3b943afc3b6a235341b7838109c1001f680febcbbac036bacc08d7a4` |

The hashes are identical. v3 changes visual/caption timing only.

## Immutable controls

- v1 SHA-256: `66575535235c1a1af9624d46e0afd49f5c259d2515c3abc2520721c585288f20`
- v2 SHA-256: `16445a6a7feac3311421483c9d33ef5e396c037a977ed056679bf62b1c6e1021`

Both controls remained unchanged after rendering v3.

## Evidence files

- Timing manifest: `output/projects/ronaldwayne/scripts/visual-edl-v3-qwen-synced.json`
- Alignment audit: `output/projects/ronaldwayne/checks-v3-sync/alignment-audit.json`
- Verification summary: `output/projects/ronaldwayne/checks-v3-sync/verification-summary.json`
- Full contact sheet: `output/projects/ronaldwayne/checks-v3-sync/contact-sheet-40-beats.jpg`
- Caption reveal regression: `output/projects/ronaldwayne/checks-v3-sync/caption-reveal-regression.jpg`
- Risk sequence sheet: `output/projects/ronaldwayne/checks-v3-sync/contact-sheet-risk-12-to-25_5s.jpg`
- Identity sequence sheet: `output/projects/ronaldwayne/checks-v3-sync/contact-sheet-identity-31_5-to-43_5s.jpg`
- Payoff sequence sheet: `output/projects/ronaldwayne/checks-v3-sync/contact-sheet-payoff-43_5-to-60s.jpg`
- Final ASR: `output/projects/ronaldwayne/checks-v3-sync/final-asr/final.txt`

## Canonical YouTube Upload Package

Packaging workflow completed against the final v3 artifact: central object/stakes/factual constraints extracted, five title families scored for cold-viewer clarity, stakes, open loop, accuracy, and mobile compliance, then one canonical package selected.

### Title

`10% Of Apple For $800? 🍎💸`

- User-visible characters: 25
- Emoji count: 2
- Factual frame: disputed shorthand remains a question, not a settled claim

### Description

```text
10% Of Apple For $800? 🍎💸
Ronald Wayne disputed the famous $800 story; this video examines the liability risk and the contract sale he regretted using synthetic cloned narration not endorsed by the source voice creator.

#shorts #Apple #BusinessHistory
```

### YouTube Studio Tags

1. `Ronald Wayne`
2. `Apple business history`
3. `founder decisions`

### Studio Settings

| Setting | Canonical value |
|---|---|
| Visibility | Unlisted first; public only after final Studio preview and all upload gates pass |
| Destination channel | BLOCKED — resolve the active ADR-0035 strict round-robin lane before upload |
| Audience | Not made for kids |
| Video language | English (United States) |
| Title/description language | English (United States) |
| Recording location | None — archival/multi-source story; no single accurate recording location |
| Category | Education |
| Paid promotion | No |
| Altered/synthetic content disclosure | Yes — synthetic cloned narration based on a real third-party voice reference |
| Raw affiliate link | None |
| Playlist | BLOCKED — no exact approved finance master-playlist name is recorded in the repository |
| Related Video | BLOCKED until the current measured winner and destination lane are resolved |
| Upload Details Template | BLOCKED — no approved template name/ID is recorded in the repository |

## Hook Gate Evidence

**BLOCKED:** no documented naive-viewer Hook Gate session exists for this v3 artifact. Do not fabricate one from internal review. The artifact can remain technically verified, but it must not be marked upload-ready until a naive viewer answers the required story/open-question/continue-watching prompts without prior explanation.

## Publication gates

Technical synchronization cannot determine whether the cloned voice feels subjectively natural or whether the edit improves retention. Watch and listen to the full 60 seconds before publication.

The narrator is a synthetic voice clone from a third-party reference. Commercial publication still requires consent/licensing review and clear disclosure. Publisher footage likewise requires rights review. The video does not guarantee any view count.

Upload remains blocked by the unresolved Hook Gate, rights/consent review, destination lane, playlist, Related Video, and Upload Details Template. Missing Studio state is recorded as `BLOCKED` rather than guessed.

## Post-Production Retro

### Hook Retro

- **Verbal:** a reusable cold-viewer framing is to lead with the known object and disputed transaction — `10% of Apple for $800?` — before introducing Ronald Wayne by name. This is stronger for cold traffic than leading with an unfamiliar proper name.
- **Visual:** the current frame-0 `10% OF APPLE` proof object is the right anchor. No stronger visual change was found without revealing the hidden-liability reversal too early.

### Workflow Delta

This production exposed two workflow gaps and both were corrected:

1. **Voice replacement sync:** slot-fit, total duration, and ASR token recall did not prove caption/semantic-visual synchronization. Stage 4 of `docs/WORKFLOW.md` now requires final-MP4 word timestamps, frame-quantized `caption_at`, semantic visual remapping, audio-stream identity proof, reveal-boundary frames, and PTS reset around accurate source seeks.
2. **Metadata packaging:** Stage 5 now requires at least five candidate title families scored for cold-viewer clarity, stakes, open loop, factual accuracy, and mobile compliance before choosing one canonical package; it also explicitly requires exactly three separate Studio tags.

The full reusable case-study workflow, failure modes, fixes, rights gate, and definition of done are stored in the `shorts-render-patterns` skill at `references/qwen-cloned-voice-word-sync-and-publishing.md`.
