# Sound Design Analysis — Reading `analyze_audio.py` Output

No prior tool in this repo analyzed sound effects/music automatically — this is new
capability built for this skill (`scripts/analyze_audio.py`, librosa-based). Maps to
`CONTEXT.md` → **Retention Techniques** ("sound design (whoosh/riser/impact), zoom punch,
pattern interrupt, cut rhythm... base quality, KHÔNG phải AB variable").

## What the script gives you

```bash
python3 scripts/analyze_audio.py <video.mp4> --cut-timestamps <comma-separated scene cut times> -o audio_analysis.json
```

- `tempo_bpm` — overall estimated tempo of the background music/rhythm.
- `beat_times` — timestamps librosa believes are on-beat.
- `onset_times` — percussive attack events (broader than beats; catches one-off
  hits/whooshes/impacts as well as musical beats).
- `energy_jumps` — timestamps where loudness (RMS, in dB) jumps by more than the threshold
  (default 6dB) from one frame to the next — a proxy for a riser payoff, a music drop, or a
  sudden sound-effect hit.
- `cuts_aligned_with_audio` (only if `--cut-timestamps` given) — for each visual cut, the
  nearest onset/beat and whether it lands within +/-150ms (`cut_on_beat: true/false`).

## How to interpret

1. **Cut-on-beat rate**: what fraction of visual cuts have `cut_on_beat: true`? A high rate
   (most cuts land on a beat/onset) is a concrete, checkable sound-design signature — report
   it as a number, not an impression.
2. **Energy jumps near the hook**: check whether any `energy_jumps` fall within the 0-3s hook
   window — a loudness swell right as the hook line lands is a common "make it feel important"
   technique; note the exact timestamp and whether it coincides with a visual cut or overlay.
3. **Tempo vs pacing**: does a fast tempo_bpm correlate with a tight cut cadence (from
   `frame-and-cadence.md`), or does the video use a slow/ambient track with fast cuts anyway
   (contrast as a deliberate technique)? Don't assume tempo and visual pacing must match —
   report what's actually observed.
4. **Honesty about limits**: librosa's onset/beat detection is a heuristic, not ground truth —
   it can miss soft sound effects (e.g. quiet whoosh under dialogue) or mis-tag a spoken
   plosive as a percussive onset. State this as a limitation in the report rather than
   presenting `cut_on_beat: false` as proof no sound design exists there; a human spot-check
   of 1-2 flagged cuts is worth doing before making a strong claim.
