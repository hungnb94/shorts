# ADR 0030: Active-Speaker Reframing and Semantic Zoom for 1:1 Interviews

**Date:** 2026-07-16
**Status:** Accepted

## Context

The planned Logan Paul Clip Curation Edit uses a landscape two-shot in which Logan and the School of Hard Knocks host remain visible together. A fixed portrait crop would frequently center the wrong person or split attention during question-and-answer turns.

Three School of Hard Knocks Shorts were inspected as visual references on 2026-07-16:

- `BaNHv_WKzr0` — 98s, 31,353,890 public views;
- `Q_oBqwgdoLw` — 88s, 11,805,333 public views;
- `_n4oZF3uzME` — 89s, 10,916,174 public views.

Across the three references, the repeatable house grammar is active-speaker-first: the portrait frame cuts/reframes to the host for a question and to the guest for the answer. Magnification changes are discrete editorial beats rather than continuous zoom pumping. Medium framing carries setup, a new question, a longer explanation, or visible hand gestures; close framing emphasizes a number, confession, command, or punchline. The next question/topic resets to medium. Two-shots are uncommon and serve interaction/context rather than the default dialogue view.

These references exceed this repository's fixed 60-second limit and are evidence only for framing grammar, not for changing output duration.

## Proposed Decision

For 1:1 interview-based Clip Curation Edits:

1. Apply **Active-Speaker Reframing** at every retained speaker-turn boundary: host question → host-focused portrait crop; guest answer → guest-focused portrait crop.
2. Apply **Semantic Zoom**, not timer-driven cadence zoom:
   - medium crop for setup, new questions, longer explanations, and gesture-dependent beats;
   - one close-up punch-in for the strongest number, confession, command, or punchline in a speaking turn;
   - reset to medium at the next question/topic;
   - default maximum of one punch-in per answer to prevent zoom pumping.
3. Use a two-shot only when the interaction itself is the information: reaction, interruption, handshake, object exchange, or spatial context.
4. Keep **Proof-Coupled B-Roll** at 25–35% of the final timeline. In the protected 0–10s window, b-roll must remain partial/corner so the active speaker's face stays visible; full-screen proof is allowed only after 10s.
5. Prefer authentic, directly related footage (Logan archive, Vine, Prime) before generic stock. Stock is reserved for abstract claims or missing evidence.

## Considered Options

- **Fixed center crop:** simplest, but visually focuses the wrong person during many turns and wastes the 1:1 interview grammar.
- **Zoom every 1–2 seconds:** satisfies a cadence timer but creates scale oscillation unrelated to meaning and competes with caption/b-roll changes.
- **Active-speaker switching without scale changes:** clear turn-taking, but leaves numerical and emotional payoff beats visually flat.
- **Continuous face tracking:** unnecessary for a mostly stable two-shot and risks visible horizontal drift; reframe at editorial boundaries instead.

## Consequences

- Each retained source window needs a shot manifest containing speaker, semantic beat, crop target, framing level, and any b-roll replacement/insert.
- Hard crop remains mandatory under ADR-0024; active-speaker framing does not permit pillarbox or blur fill.
- The 0–10s face-protection rule remains above b-roll variety.
- More crop states increase render and manual-QC effort, but make turn-taking legible and prevent a fixed crop from privileging the silent participant.
- This is an editing policy, not a new Video Type or MAB dimension.

The user explicitly approved continued production on 2026-07-16. Active-Speaker Reframing and Semantic Zoom are therefore accepted for this video and as the default policy for future 1:1 interview-based Clip Curation Edits.

## Related

- ADR 0016: Frequent Editing
- ADR 0017: Hook-Window Source Selection
- ADR 0018: Hook Caption Sync and Cadence
- ADR 0022: Multi-Clip Mashup Pipeline
- ADR 0024: Hard-Crop Mandatory, No Pillarbox
