# ADR 0024: Hard-Crop Mandatory for Clip Curation Edit — No Blur-Fill Pillarbox

**Date:** 2026-07-12
**Status:** Accepted

## Context

`render_bacsihai_v6.py` introduced a "blur-fill pillarbox" crop technique: the full uncropped source frame, scaled to fit 1080px width, centered over a blurred full-bleed copy of itself. It was adopted because that source's burned-in Vietnamese captions spanned nearly the full 1920px source width — a plain center-crop-to-1080 clipped the caption text on both edges. `render_hardknocks_v3.py` reused the same technique for the same reason (frame-tested: this source's English captions similarly get clipped by a center-crop, confirmed via `ffmpeg` frame extraction before committing).

Both videos technically satisfy the project's "9:16 (1080x1920)" spec — the output container is correctly sized. But visually, pillarbox reads as a horizontal video shrunk and padded into a vertical frame (blurred bars top/bottom, sharp footage only in a middle band), not footage that fills the frame the way a genuine vertical crop does. Reviewing `hardknocks_v3`, the user rejected this look outright: "bắt buộc phải cắt video về dạng dọc 9:16" (the video must actually be cut to vertical, not just boxed into a vertical container).

This creates a real conflict: the reason pillarbox was introduced (preserving legible source captions) doesn't go away just because pillarbox is now banned. A plain hard-crop on a wide-caption source still clips the caption text.

## Decision

Every Clip Curation Edit video must use a **hard-crop that fills the entire 1080x1920 frame with sharp source footage** (the `render_hardknocks_v1.py`/`v2.py` center-crop approach, or an off-center crop chosen to keep faces in frame — see ADR-0017). Blur-fill pillarbox is no longer a permitted fallback, for any niche.

When a source's own burned-in captions would be clipped by the hard-crop safe zone, do **not** fall back to pillarbox. Instead, **re-author the captions ourselves**: burn in new `drawtext` captions, word-synced from the mlx_whisper transcript already produced in Stage 1, positioned to fit entirely within the hard-crop's 1080px width. The source's own captions are allowed to run off-frame in the cropped-away portion — they are superseded by the self-authored ones, not relied upon.

This means caption legibility (ADR-0018) and hard-crop (this ADR) are no longer in tension: captions become something we fully control and position, rather than something inherited from the source's own frame.

## Consequences

- `hardknocks_v3` (rendered 2026-07-12, not yet uploaded) must be re-rendered: hard-crop instead of pillarbox, with self-authored word-synced captions replacing reliance on the source's own burned-in captions for the pieces where they'd otherwise be clipped.
- `bacsihai_v6` (already uploaded as `EpTPDrWONS0`) is grandfathered — not re-rendered. Re-cutting and re-uploading a already-public video for a crop-style preference isn't worth the churn/metrics-reset cost; this ADR governs new production only.
- Every future Clip Curation Edit video that would have reached for pillarbox must instead budget time to write and time captions by hand (using the transcript's word timestamps) rather than passively keeping the source's own captions. This is real added authoring work, not free.
- `docs/WORKFLOW.md` Stage 2/3 should be read as: crop choice is "hard-crop, always" (no per-source pillarbox branch); Stage 3's caption-sync step now always means "author captions," not "verify the source's existing captions survive the crop."

## Related

- ADR 0017: Hook-Window Source Selection (frame-0 face requirement; hard-crop framing must still satisfy this)
- ADR 0018: Hook Caption Sync and Cadence (now the sole path to legible captions when hard-crop would otherwise clip the source's own)
- `render_bacsihai_v6.py`: introduced blur-fill pillarbox (grandfathered, not reverted)
- `render_hardknocks_v3.py`: first video required to re-render under this ADR (see `docs/production/hardknocks-v3-believe-in-god.md` Workflow Delta)
