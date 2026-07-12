# bacsihai_v7 — "Cholesterol Không Phải Là Kẻ Thù"

## Status
| Field | Value |
|-------|-------|
| YouTube Video ID | [mziisgML2sM](https://youtube.com/watch?v=mziisgML2sM) |
| Rendered | 2026-07-12 |
| Metrics fetch after (48h rule) | 2026-07-14 20:38 +07 |
| Metrics status | Not yet fetched, too early |

## Video Specs
- Duration: 49.3s (raw cut 50.70s, 1.03x speed-up — mild, since the raw cut already landed near the ~50s target)
- Resolution: 1080x1920 (9:16 portrait)
- Codec: H.264 (libx264, crf 18), 30fps
- Audio: AAC, 192kbps, 48kHz, stereo (1 stream, verified via ffprobe)
- File: `output/projects/bacsihai/final/2026-07-12-bacsihai_v7_cholesterol_not_the_enemy.mp4` (31.0MB)
- Render script: `pipeline/bacsihai/render_bacsihai_v7.py`

## YouTube Title
Cholesterol Là Kẻ Thù? 80% Do Chính Cơ Thể Bạn Tự Tạo Ra

## YouTube Description
```
Trong nhiều thập kỷ, cholesterol bị coi là "thủ phạm" gây bệnh tim. Nhưng nếu nó thực sự nguy hiểm như vậy, tại sao cơ thể bạn lại tự tạo ra đến 80% lượng cholesterol mỗi ngày?

Bác sĩ Hải giải thích 2 sự thật ít người biết về cholesterol: tại sao 80% lượng cholesterol trong cơ thể là do CHÍNH BẠN tạo ra (không phải từ ăn uống), và tại sao mỗi tế bào trong 30 nghìn tỷ tế bào của cơ thể đều cần cholesterol để tồn tại.

Đừng vội sợ hãi trước những con số xét nghiệm khi chưa hiểu đúng bản chất.

#cholesterol #suckhoe #bacsihai #shorts
```

## Source
- Channel: Bác sĩ Hải (`UCBlKbsGXxDCwZVcdr8orrHA`) — same Source Channel as `pipeline/bacsihai/` v1-v6 (ADR-0019, health/Vietnamese vertical)
- Source video ID: `MTcn9LRJSH0` — "Đừng Vội Sợ Cholesterol: Đây Là Chất Cơ Thể Không Thể Thiếu | Bác Sĩ Hải", uploaded 2026-07-11, 553.7s (~9:14), 1920x1080 — a produced/edited video (dense burned-in captions, kinetic-typography title cards, stock-photo cutaways, and 3D cell-biology animation graphics throughout, similar production style to v6 but noticeably more graphics-heavy)
- First use of this exact video ID — checked against `data/source_videos.csv` before selection.
- Max-quality check: `yt-dlp -F` confirmed no ≥2160p stream exists for this source (max available is 1920x1080/av1); downloaded at that ceiling rather than a lower default, satisfying AGENTS.md's "always download max quality" intent given no higher stream exists.
- Footage used: 4 non-contiguous pieces totaling 50.70s raw (9.2% of the 553.7s source, well under the ADR-0007 50% ceiling). Individual piece lengths: 11.18s, 17.28s, 18.26s, 3.98s (the 17.28s and 18.26s pieces exceed the ADR-0007 item 3 "<15s per clip" rule as single continuous takes with no internal skip — same exemption precedent as `bacsihai_v6`'s Piece B and the ADR-0022 addendum it proposed).

## Why This Segment
**Multi-Clip Mashup** (ADR-0022), 4 pieces:
- **HOOK** (src 0.00-11.18s): the source's own cold open — "Nếu bạn là một trong số hàng triệu người ngoài kia nghĩ rằng cholesterol là một phần tử xấu gây hại cho cơ thể, thì rất có thể video này sẽ làm bạn thức tỉnh hoặc có thể khiến bạn khó chịu một chút." A clean, ready-made Contrarian-Reveal opener — reused verbatim rather than scripted from scratch, matching this project's consistent finding that the source's own words make the strongest hook (see Hook Retro).
- **SKIP** (src 11.18-48.66s, ~37.5s): a stakes-building tangent — "today I'll list 7 critical functions... if we lacked them we'd die within minutes, literally... I'll completely destroy that myth" — dramatic but repetitive with the HOOK's own tension, and visually dominated by a numbered-list title card ("7 CHỨC NĂNG CHÍNH"), stock B-roll, and a 3D cell-biology animation rather than the host (frame-checked at 29.7s, 35s, 40.5s, 44-48s). Skipping it pulls the concrete payoff forward — the same device `bacsihai_v6` used for its own mid-source tangent.
- **REVEAL 1** (src 48.66-65.94s): "nó chính là 80% lượng cholesterol do cơ thể chúng ta tự tạo ra, và chỉ có khoảng 20% là từ ăn uống — dù ăn bao nhiêu cũng vậy" (Money+Number payoff: 80% self-produced). Starts right as a brief "ĐIỀU 1" title-card fade clears — frame-checked clean and dramatic at src 49.5s (pointing gesture + the source's own red "80% LƯỢNG CHOLESTEROL" stat callout already burned in).
- **REVEAL 2** (src 106.08-124.34s): "cholesterol là vật liệu nền tảng cho sự sống — cơ thể có khoảng 30 nghìn tỷ tế bào, mỗi tế bào có một lớp màng, và nếu mất màng này tế bào sẽ chế.t" — a second concrete stat reinforcing the same myth-busting thesis, extending into the opening of a shelter/house analogy, cut right before the source hands off to stock crosswalk B-roll (~125s, frame-checked).
- **CLOSER** (src 154.54-158.52s): the source's own closing thesis line — "vậy nên cholesterol là vật liệu cấu tạo nên sự sống còn trong cơ thể" — used as a natural closing button.

**Frame-0 check (ADR-0017)**: HOOK starts at src 0.000s exactly — frame-extracted and confirmed genuinely clean (sharp, tight face shot, no overlay effects yet), not a "small margin" case. Within under 1s the source's own kinetic-typography/stock-photo hook-montage begins (a different generic stock photo roughly every 2-3s through the rest of the HOOK piece) — this is very high-cadence B-roll, not a disqualifying title-card start, since frame 0 itself is unambiguous.

**Payoff-timing (Stage 0 item 4)**: REVEAL 1 begins at cumulative clip-time 11.18s raw (~10.85s post-1.03x-speed-up) — right at the edge of, and slightly past, the ideal ~5-10s window, but well under the "not buried past ~15s" hard ceiling. Flagged honestly rather than rounded down: this HOOK is a touch longer than v6's 8.3s or hardknocks_v3's ~3.96s, because the source's own cold-open sentence (kept verbatim, not trimmed) runs a full 11.18s before the next usable cut point.

## Hook Formula Applied
- **Frame-0 face/action** (ADR-0017): see above — genuinely clean, not marginal.
- **Gap-not-resolved**: the HOOK states an existing belief ("cholesterol is bad") and promises a reaction ("wake you up or annoy you") without revealing the actual myth-busting fact — that's held for REVEAL 1.
- **Cause+effect not co-named**: the hook line names neither a specific mechanism nor a specific disease — stays at "you think X, this will surprise you," same pattern as prior productions' passing cases.
- **Payoff timing**: ~10.85s post-speed-up — see honest caveat above.
- **Caption-sync (ADR-0018)**: self-authored captions start at t≈0.05-0.1s (frame-verified), matching the source's own native caption timing almost exactly.
- **Cadence (ADR-0016/0018)**: the HOOK piece alone cuts through at least 4 distinct visuals (host, population-icon parallax, 2 different stock photos, kinetic-typography title cards) within its 11.18s — comfortably exceeds the 1-2s hook-window cadence target; the two REVEAL pieces likewise alternate host shots with the source's own 3D cell-biology graphics roughly every 2-5s.
- **Claim-strength flag**: Money+Number hook — 80% / 20% / 30,000 tỷ tế bào are all concrete figures stated by the source itself, not a qualitative claim.

## Value-Adds (Transformative Gate, ADR-0007 — min 2 required, distinct categories)
1. **fact-check-callout** — persistent header, switching from "LẦM TƯỞNG: CHOLESTEROL = XẤU" (myth, during HOOK) to "SỰ THẬT: THIẾT YẾU CHO SỰ SỐNG" (fact, during both REVEALs) — an explicit myth-vs-fact framing layered on top of the source's own narrative, not just restating it.
2. **data_viz_overlay** — stat cards reinforcing each REVEAL's own number: "80% TỰ CƠ THỂ TẠO RA" (REVEAL 1) and "30.000 TỶ TẾ BÀO" (REVEAL 2).

Commentary track (gate item 1): the fact-check header + stat cards + CTA satisfy this item; no TTS was used (see below).

**No TTS** — text overlay/caption commentary only, matching 100% of bacsihai v1-v6 precedent; TTS stays scoped to the AI-education niche only (ADR-0021).

## Technical note: hard-crop + self-authored captions throughout (ADR-0024)
This source's burned-in captions and kinetic-typography text cards span nearly the full 1920px frame width (confirmed via frame extraction — e.g. the CLOSER piece's own on-screen text runs edge-to-edge). Per ADR-0024, every piece uses a hard center-crop (`scale=-2:1920,crop=1080:1920:(in_w-1080)/2:0`, matching v1-v3/hardknocks) with self-authored, word-synced captions burned in from the mlx_whisper transcript, positioned inside the 1080px safe zone, applied uniformly across all 4 pieces (including the CLOSER, rather than trying to preserve the source's own giant centered text there). The source's own now-superseded text/captions are allowed to bleed through the crop as illegible fragments in the background — cosmetic only, not relied upon (see Known Issues).

## Known Issues
- **Text-width overflow, caught and fixed pre-Stage-4-completion**: the first render's fact-check-callout header ("NHIỀU NGƯỜI NGHĨ: CHOLESTEROL = XẤU" @ size 64 and "SỰ THẬT: CHOLESTEROL THIẾT YẾU" @ size 64) overflowed both edges of the 1080px frame — confirmed via the mandatory Stage 4 frame extraction, exactly the kind of bug that check exists to catch (WORKFLOW.md Stage 4: "visual self-check bắt buộc"). Fixed by measuring actual pixel width with `PIL.ImageFont.getlength()` at the real font/size before re-rendering (not just eyeballing), then shortening the copy ("LẦM TƯỞNG: CHOLESTEROL = XẤU" @ 56px = 957px, "SỰ THẬT: THIẾT YẾU CHO SỰ SỐNG" @ 56px = 971px, CTA shortened similarly @ 48px = 850px) — all comfortably under the 1080px frame with margin, re-verified via a second frame extraction pass after the fix. See Workflow Delta below — this generalizes into a WORKFLOW.md addition.
- The source's own now-superseded burned-in text/title-cards bleed through the hard-crop as illegible fragments in the background of several shots (e.g. "STEROL LÀ VẬ", "HƯ MẤT CÁI M...") — cosmetic only, expected and accepted per ADR-0024 (same as hardknocks_v3's precedent), not remediated further.
- Pause-trimming (Retention Technique, AGENTS.md) was evaluated and found to be a no-op: word-gap analysis of all 4 chosen pieces found a max internal gap of 0.42s (REVEAL 1) — nothing meaningful to trim. The mandatory 1.03x speed-up was still applied as a separate Retention Technique.
- Payoff-timing lands at ~10.85s post-speed-up, right at/slightly past the edge of the ~5-10s ideal window — see Why This Segment for the honest accounting; not treated as a Hook Gate failure (well under the 15s hard ceiling) but worth comparing against faster-payoff siblings (v6: 8.3s, hardknocks_v3: ~3.96s) at the 48h check.

## What To Check At 48h (once uploaded)
- Retention-graph shape in the first ~11s specifically — does the slightly-later-than-ideal payoff (10.85s vs. v6's 8.3s) correlate with a measurably softer hook retention, isolating whether the ~5-10s target is a hard cliff or a soft gradient.
- Whether the fact-check-callout header (myth → fact framing) reads as a value-add on comments, or as redundant with the dialogue captions already saying the same thing.
- Retention through REVEAL 2 (~30 trillion cells / membrane analogy) — this is the 2nd-longest uninterrupted stretch (18.26s raw); check whether it sustains momentum or dilutes it relative to REVEAL 1.
- Comment themes — this is a factual/educational reveal about a commonly-feared lab number; watch for medical-skepticism/fact-check pushback vs. the "TIL, I didn't know that" surprise-and-share pattern (same axis `bacsihai_v6` watched for).

## Post-Production Retro

### Hook Retro (bắt buộc, mọi video — proactive)
- **Verbal**: none found — the source's own cold-open line ("if you're one of millions who think cholesterol is bad, this video will wake you up or annoy you a little") is already a complete, natural Contrarian-Reveal opener; rewriting it would only weaken the authenticity of reusing the source's actual words, consistent with every prior bacsihai/hardknocks production's finding on this point.
- **Visual**: one idea not applied here — the HOOK piece's first ~1s (clean host face) is immediately followed by the source's own icon-parallax/stock-photo montage for the rest of the piece. A tighter cut (e.g., trimming the HOOK to just the first sentence, ending on the clean host face rather than riding through the full stock-photo montage) could keep a real human face on screen longer during the most crucial opening seconds, at the cost of a shorter, less complete hook sentence. Not applied this time because the full sentence ("...wake you up or annoy you a little") is a stronger, more complete hook than a truncated half-sentence — flagged as a hypothesis for a future video where the source's own intro montage is even more stock-photo-heavy.
- Did not run the `viral-video-analysis` skill against a comparison video for this retro (no metrics yet on this or the most relevant sibling, `bacsihai_v6`, to compare against) — will fold into the 48h check instead, comparing payoff-timing (10.85s vs. 8.3s) directly against retention data once both have it.
- Generalizable finding written into `docs/WORKFLOW.md` now: yes — see Workflow Delta below.

### Workflow Delta (bắt buộc, mọi video — reactive)
Yes — one case worth generalizing, an ordering/technique gap rather than a new rule:

**Pre-render text-width verification, now added to WORKFLOW.md Stage 3**: WORKFLOW.md Stage 3 already required shortening copy before raising size, and re-verifying via frame extraction after every size change — but only as a *post-render* check. This production's first render overflowed the frame on a *stat-card/header* overlay (not the main hook text) at a size that "looked" plausible in code but was never measured. The rule itself already existed and already generalizes to "text phụ (stat card/counter-argument/CTA)," so this isn't a new rule — it's that WORKFLOW.md didn't mention a *pre-render* way to catch it before spending a full render cycle. Fixed by computing actual pixel width via `PIL.ImageFont.getlength()` at the real font file/size in a throwaway script before committing to a size in the render script itself — turned what would likely have been a multi-round trial-and-error cycle (per `hardknocks_v2`'s 4-round precedent) into a single fix-and-reverify pass. Added one line to `docs/WORKFLOW.md` Stage 3 citing this video, recommending the same pre-render measurement step for any future drawtext overlay before the mandatory post-render frame check.
