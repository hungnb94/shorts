# HardKnocks "Is He Still a Billionaire?" (John Ruiz, Blindspot v3)

## Status

| Field | Value |
|---|---|
| Production | Complete (Revision 8 — Business Lesson Payoff, 57.331s) |
| Render date | 2026-07-19 |
| Upload status | Uploaded; public |
| YouTube Video ID | `SInUCQ58xzU` |
| YouTube URL | https://youtube.com/shorts/SInUCQ58xzU |
| Upload reported/logged at | 2026-07-19 14:31:56 +07 |
| Public timestamp | 2026-07-19 14:29:12 +07 |
| Public metadata verification | Verified 2026-07-19 14:31 +07 — canonical title matches, duration rounds to 57s, availability public, channel is MONEY BLINDSPOT (`UCG_yrDQF5Sj6iMTZB0KSBAA`) |
| Metrics status | Not yet fetched — wait at least 48 hours after public release |
| Metrics fetch after (48h rule) | 2026-07-21 14:29:12 +07 or later |
| Studio Analytics | https://studio.youtube.com/video/SInUCQ58xzU/analytics/tab-overview/period-default |
| Final video | `output/projects/hardknocks/final/2026-07-19-hardknocks_b1_ruiz_billionaire_check.mp4` |
| Renderer | `pipeline/hardknocks/render_hardknocks_b1_ruiz.py` |
| Narrator profile | `natural_talker_male_qwen_blog` (ADR-0032, Qwen3-TTS MLX) |
| QC summary | `output/projects/hardknocks/clips/v12_work/checks/validation.json` |

## Revision 2: continuous 3-act narrative rebuild

The 1st pass (36.07s, documented below) was rejected in full after review. User feedback
(verbatim): *"video có nhịp độ quá nhanh khiến não người xem không thể hiểu được nội dung. nhảy
giữa các đoạn cắt hơi mơ hồ chả hiểu tỉ phú nói thế có ý nghĩa gì. hãy làm lại giống như một bài
văn có mở bài, thân bài, kết bài. hook là mở bài và sẽ được tiết lộ ở cuối video. cả video truyền
tải một câu chuyện/story tới người xem. loại bỏ phần đen cuối video để cả video full màn hình. hãy
học cách làm hook của MrBeast để cho video thật sự thú vị"* — pacing too fast to follow, cuts felt
disconnected, rebuild as an essay (mở bài/thân bài/kết bài) with the hook resolved only at the end,
told as one continuous story, and remove the flat dark/dead space at the end so the video stays
full-screen throughout.

Rebuild, same source/subject/claims, same renderer file:
- **Segments extended** for narrative breathing room: `origin_claim` and `house_claim` both grew
  by several seconds to include real follow-up lines ("So you didn't come from money? No, I came
  from nothing" / "...the only one of the five kids" — a deliberate callback to the origin story).
- **2 new narrator VO bridges** (`bridge1_vo_qwen.wav`, `bridge2_vo_qwen.wav`) thread the 3 beats
  together with the subject's own dialogue ducked underneath, replacing silent hard cuts.
- **Ending VO rewritten** to explicitly reopen the hook question ("So, is he still a billionaire?")
  before resolving it, per the "hook = mở bài, resolved only in kết bài" requirement.
- **Every full-screen cutaway card removed.** Inline verifies are now small corner badges that fade
  in/out over the still-playing interview footage (never freezing or cutting away). The ending's
  score rows / evidence reveal / LESSON pill / CTA are all small translucent cards composited over a
  continuous, slowed-and-desaturated loop of the house-tour footage — never a flat dark screen.
- Final duration grew from 36.07s to 43.0s (still comfortably under the 60s Shorts limit).

**2 real bugs found and fixed during this rebuild's own Stage 4 QC** (not present in the 1st pass,
introduced by the rebuild itself — see Manual Visual QC below for detail and AGENTS.md Known
Pitfalls for the generalized versions):
1. The ending's looping backdrop showed School of Hard Knocks' own burned-in captions bleeding
   through underneath our score/evidence cards, because it reused the raw segment clip directly.
2. The inline verify badges silently never appeared at all — a broken ffmpeg overlay idiom (shifting
   the PNG input's own PTS late) that differed from the working pattern used everywhere else in the
   same file.

Both were caught by extracting and visually reading actual frames at the calculated timestamps
(not just trusting the code), fixed, and re-verified by re-rendering and re-reading frames.

## Revision 3: remove the black footer band

User follow-up after reviewing Revision 2: *"fix lỗi đen cuối video (footer) sau đó tự render và
kiểm tra lỗi đen còn không"* — fix the black error at the end of the video (footer), then render and
check whether the black issue is still there.

Investigated directly (row-by-row pixel scan + full-res frame reads) rather than assumed fixed:
the ending's dark cards sit on the moving backdrop fine, but a **separate, pre-existing black band
at the very bottom of every single frame — not just the ending — was still present**. Root cause:
`mix_and_caption()`'s own `drawbox=y=1650:h=270` (there specifically to hide School of Hard Knocks'
pre-existing burned-in captions before burning in this project's own captions higher up the frame)
painted a flat black rectangle across the bottom ~14% of the canvas for the *entire* video, not just
the ending — our own captions render well above that band, so nothing ever filled it. Revision 2's
fix for the ending backdrop (a non-uniform `crop=1080:1650:0:0,scale=1080:1920`) also turned out to
subtly stretch the image vertically (aspect-ratio distortion), since width wasn't scaled by the same
factor.

Real fix: moved the caption-band removal to `scaled_crop()` (the base per-segment render step, used
by all 3 segments), replacing the drawbox/ad-hoc-crop approach entirely. It now crops the source's
own caption band off *and* zooms back up to refill 1080×1920 uniformly (both dimensions, no
distortion) before any overlay, caption, or backdrop step ever touches the footage — so no
downstream step needs its own blackout at all. `mix_and_caption()`'s drawbox and the ending
backdrop's earlier crop workaround were both removed as redundant.

Verified: row-by-row pixel scan of the bottom 20 rows now shows real image content (mean brightness
16–100, matching genuine scenery/shadow) at every sampled timestamp across the whole video —
previously a flat `0.0` at y≥1650 in every single frame, interview and ending alike.
`blackdetect` (even at a looser `pic_th=0.90`) finds zero black frames. The extra zoom (net ~1.16–1.22×
combined with each segment's existing zoom-punch) also tightened the framing noticeably — checked
visually and via `inspect_image.py`: frame 0's skin-tone reading rose from 13.09% to 16.44% (still
comfortably over the ADR-0017 10% threshold), with both faces more prominent, no cropping of the
handshake, mic, or hands anywhere in the contact sheet.

Re-rendered end to end; final duration unchanged at 43.0s, all `validate()` assertions still pass.
New file hash: `087feb6cfb15b901ff1e12d79f541be0c0d73d36cbf53cf7ea3c32d3b48aad95` (32,171,259 bytes).

## Revision 4: bridge VO narration too quiet to hear

User follow-up: *"tts bắt đầu ở giây thứ 5 quá nhỏ so với video nên làm gần như không nghe được.
kiểm tra tất cả các đoạn tts xem đoạn nào quá nhỏ thì sửa lại. sau khi render thì cũng kiểm tra lại
các đoạn này"* — the narration starting around second 5 is too quiet against the rest of the video,
almost inaudible; check every TTS segment for this and fix, then re-verify after rendering.

Measured every VO clip's own loudness (not just trusted the loudnorm target). All 4 clips
(`opening_vo_qwen.wav`, `bridge1_vo_qwen.wav`, `bridge2_vo_qwen.wav`, `ending_vo_qwen.wav`) are raw
Qwen-TTS recordings with a high peak-to-loudness ratio (e.g. bridge1: -25.3 LUFS integrated but only
-8.2 dBTP peak, a ~17dB crest factor from a sharp transient). `loudnorm`'s `TP=-1.5` ceiling caps how
much gain it will apply before risking clipping that peak — confirmed via direct `ebur128` measurement
that this happens identically whether loudnorm runs in single-pass "dynamic" mode or true two-pass
"linear" mode (the peak ceiling is the limiter, not the measurement mode) — so it stopped short of
-16 LUFS on every clip that had a big peak, landing at -18.5 to -19.4 LUFS in isolation.

But that alone doesn't explain "almost inaudible" — a 2-3dB gap isn't that. Found the real, much
bigger bug by scanning the actual mixed final audio in 0.25s slices: bridge1's & bridge2's active
windows measured -20 to -30dB mean, a deep, audible dip well below the surrounding dialogue (~-15
to -20dB) — while the isolated VO clip tested fine standalone. Root cause: in
`apply_narration_bridges()`, the filter chain applied `adelay` (prepending 5.2s of silence for
bridge1, 15.2s for bridge2, to position the clip in time) **before** `loudnorm`, so loudnorm was
measuring integrated loudness over [long silence + short speech] together, not the speech alone —
this badly corrupts loudnorm's gating and measurably worsened the result (confirmed by reproducing
both orders side by side: adelay-then-loudnorm → -26.9 LUFS; loudnorm-then-adelay → -16.4 LUFS, a
10.5dB difference). The hook VO (`adelay=0`) was unaffected by this specific bug since it has no
silence prefix to begin with — which is exactly why only the bridges (starting at t>0) were audibly
broken, matching the user's "around second 5" report precisely (bridge1 lands at final t≈4.4s).

Two-part fix in `render_hardknocks_b1_ruiz.py`:
1. Added a mild `acompressor` (threshold=0.1, ratio=4) before `loudnorm` on every VO clip, reducing
   the crest factor so loudnorm can reach -16 LUFS without needing to touch the TP ceiling at all —
   verified all 4 clips land within 0.8dB of -16 LUFS in isolation after this.
2. Reordered `apply_narration_bridges()`'s filter chain so `loudnorm` runs before `adelay`, not after.

Re-rendered and re-verified by scanning the actual final mixed audio in 0.25s slices across the
whole runtime, then measuring true integrated LUFS (`ebur128`) in each VO's active window:

| VO | Before fix (window) | After fix (window) |
|---|---:|---:|
| Hook | -14.2 LUFS (unaffected, adelay=0) | -14.2 LUFS |
| Bridge 1 | -20.5 LUFS (mixed-window; deep dip vs. surrounding dialogue) | -15.1 LUFS |
| Bridge 2 | -20.8 LUFS | -14.8 LUFS |
| Ending | -16.6 LUFS (unaffected, no adelay in this beat) | -16.4 LUFS |

All 4 windows now land in the -14.2 to -16.4 LUFS range, matching or exceeding the surrounding
ducked-dialogue level rather than dipping below it. Also re-ran the full QC suite: `silencedetect`
and `blackdetect` both clean, full decode passes, `validate()` assertions all pass, duration
unchanged at 43.0s. New file hash: `05005bf003bbb718202e9772d4fbf8a1afe37d755ecdf6a79c7147e444a13af2`
(32,172,466 bytes).

## Revision 5: small breathing pause at each segment cut

User follow-up: *"kiểm tra phần chuyển giữa các đoạn cắt video thì âm cuối không nghe rõ và nhỏ hơn
rõ rệt so với các âm khác. giữa các đoạn cắt video thì nên có khoảng nghỉ nhỏ rồi nói tiếp tránh đè
lên nhau."* — the tail sound right at each segment cut isn't clear and is noticeably quieter than
the rest; there should be a small pause between cuts before the next line continues, to avoid the
audio feeling jammed together.

Root cause: `build_base()` hard-concatenates 3 independently-rendered segments (`-f concat -c copy`,
no crossfade). Each segment's own `render_segment()` audio chain ended with a flat `atrim` and no
fade — so at every cut, whatever word was still naturally decaying got chopped off at full volume
with no taper, and the next segment's dialogue started at full volume with zero lead-in. That reads
exactly as described: an unclear, abruptly-truncated tail, and no breathing room between lines.

Fix: added a short `afade` (in: 0.12s, out: 0.20s) to each segment's own audio in `render_segment()`
— purely an amplitude envelope shape, no change to duration/timing, so video stays perfectly in
sync (video is still a hard cut, per this project's established Active-Speaker Reframing style;
only the *audio* now eases through the join). Verified with a fine 0.1s-step volume scan straddling
all 3 cut points: each now shows a clean fade-down approaching the cut (e.g. at the hook→origin cut,
-15.8 → -19.0 → -25.9 → -28.6 → **-35.0 dB** right at the join), a brief near-silent dip, then a
fade-up into the next segment's dialogue (-18.2 → -15.6 → -16.5 dB) — audibly a small pause, not a
hard slam. All 3 cuts (hook→origin, origin→house, house→ending) show the same shape.

Re-ran the full QC suite: `silencedetect`/`blackdetect` still clean (the fade dips are well under the
0.5s silence-detection threshold, so this doesn't trip a false silence-gap flag), full decode passes,
all 4 narrator VO windows re-verified unaffected (-14.2 to -16.4 LUFS, unchanged from Revision 4),
`validate()` assertions all pass, duration unchanged at 43.0s. New file hash:
`8e57259ab8577fb26b1d3d536370ce6bc37599000ccb36ba5a0c7af8b2dcef0c` (32,173,021 bytes).

## Revision 6: extend segment cuts so closing words are not truncated

User follow-up: *"hướng dẫn nhé: I came from nothing thì đoạn cắt này nên dài hơn một chút để người
xem nghe rõ âm 'nothing'. tương tự với các đoạn cắt khác cắt dài hơn một chút để người xem nghe rõ
cả câu. tự kiểm tra các đoạn khác sau khi render."* — the `origin_claim` cut should be extended
slightly so the word "nothing" is fully audible; the same applies to the other cut segments, so the
whole closing sentence is heard; self-check the other segments after rendering.

Root cause: all 3 `source_end` timestamps were set with effectively zero trailing buffer past the
segment's actual last spoken word — `origin_claim` (559.48) and `house_claim` (599.80) landed
*exactly* on the ASR word-end timestamp of "nothing." and "kids." respectively, and
`hook_billionaire` (524.92) landed 0.04s *before* "channel." finished. Revision 5's new 0.20s
`afade` out (added to fix the cut-transition issue) made this worse in a subtle way: the fade window
itself started at `duration - 0.20`, which for all 3 segments fell *inside* the still-playing closing
word, so the fade was audibly attenuating real speech, not just tapering silence.

Fix: ran `mlx_whisper` word-level ASR (`.venv/bin/python3`, `word_timestamps=True`) on source audio
windows around each segment's old end timestamp to get the exact word-end time and the gap to the
next spoken word, then extended each `source_end` so the fade-out's start point (`duration - 0.20`)
falls just after the word ends, inside the natural pause before the next line, not during the word:

| Segment | Closing word | Word ends at (raw) | Old `source_end` | New `source_end` | New fade-out starts at |
|---|---|---:|---:|---:|---:|
| `hook_billionaire` | "channel." | 524.96 | 524.92 (before word end) | 525.20 | 525.00 (0.04s after word end) |
| `origin_claim` | "nothing." | 559.48 | 559.48 (exactly on word end) | 559.75 | 559.55 (0.07s after word end) |
| `house_claim` | "kids." | 599.80 | 599.80 (exactly on word end) | 600.05 | 599.85 (0.05s after word end) |

Verified by extracting the last 2s of each rendered segment (`segments/00_hook_billionaire.mp4`,
`01_origin_claim.mp4`, `02_house_claim.mp4`) and re-running ASR on just that tail window: all 3
closing words ("channel.", "nothing.", "kids.") now transcribe fully and end at 1.66-1.76s within
the 2s window, comfortably before the clip's actual end — no truncation. Also scanned the volume
envelope in 0.2s steps across the last second of each segment (`volumedetect` per slice): no
anomalous mid-word dip, only the expected fade-down starting after the word (e.g. hook_billionaire:
-15.0 -> -20.5 -> -17.8 -> -26.8 -> -18.5 -> **-24.4 dB** at the very end, i.e. still highly variable
speech-level audio through the word, not a flat attenuation ramp cutting into it).

Re-ran the full QC suite on the new render: `blackdetect` zero black frames; `silencedetect`
(-35dB/0.3s) only fires in the ending section (3 gaps of 0.3-0.4s, all natural pauses, none
overlapping the 3 segments just extended); overall `ebur128` integrated loudness -15.7 LUFS (healthy,
consistent with Revision 4/5's fix holding); `validate()` assertions all pass; duration increased
43.0s -> 43.67s (all 3 segments individually still well under 15s: 5.50s / 10.27s / 12.77s) — still
comfortably under the 60s Shorts limit. New file hash:
`0ec9728b817f200839cbbc8998a4604de468030d59a498e2db2cd1447ca3e1c8` (32,920,120 bytes).

## Revision 7: proof-first ending and active-speaker reframing

The prior ending was reviewed directly from the MP4 and rejected as too long and too abstract:
19.70s of score rows/text cards, or 45.1% of the 43.67s runtime. The host/guest interview also used
one crop for long stretches, so speaker changes were not visually legible despite ADR-0030.

Decision after grilling the trade-offs: preserve the complete house claim in the subject's own voice,
make every retained host/guest turn visually explicit, and replace the cumulative scorecard ending
with a 10–12s proof-first resolution using real source-page crops.

Changes:

- `origin_claim` now reframes guest → host → guest at the retained turn boundaries; `house_claim`
  reframes host → guest. This follows ADR-0030 instead of using a fixed guest-centered crop.
- The house segment now starts at raw 580.38s and keeps the complete exchange: the host asks for the
  valuation, Ruiz says about $175M, then says he bought it for $46M and invested another ~$20M.
  The redundant narrator bridge and origin-story callback were removed.
- The inline house badge was moved to the actual $175M line and explicitly says `ASKING PRICE ONLY`.
- The ending uses three proof screenshots in spoken order: Forbes profile (`$1.5B`, 2023), Yahoo
  Finance 5Y price chart (`LIFW / MSPR`), and The Real Deal (`$175M` listing, $46M prior purchase).
  The final interpretation remains neutral: `STOCK WEALTH ISN'T CASH WEALTH`.
- Ending VO uses `L-I-F-W` in the TTS input so the rendered narration says `LifeWallet`; final
  large-v3-turbo ASR confirmed the complete body and ending word-for-word.
- Ending reduced to 11.97s; total runtime reduced from 43.67s to 36.669s (6.998s saved).

One additional silent ffmpeg bug was caught during final-frame review: each proof PNG input was
looped to the rounded ending duration (14.130s), a few milliseconds shorter than the 424-frame
ending stream (14.133s). With `eof_action=pass`, the CTA disappeared on the final frame even though
ffmpeg exited 0. The still inputs now run 0.5s beyond `frame_count / FPS`; direct reads at 36.00,
36.30, 36.50, and 36.58s confirm the CTA remains visible and unclipped through the last frame.

Final QC: full decode passes; no black frames; no freeze event ≥1.5s; one 0.510s silence at
25.61–26.12s is the deliberate pause between the ending question and Forbes answer; integrated
loudness is -15.9 LUFS with -0.4 dBTP true peak. Dense contact sheets and exact-turn frame reads
confirmed frame-0 face visibility, active-speaker crop changes, proof-card readability, and the
final CTA hold.

No new ADR or glossary term was needed: this revision implements the already-accepted ADR-0030
Active-Speaker Reframing / Proof-Coupled B-Roll policy rather than introducing a new architecture.

## Revision 8: Business Lesson Payoff

User feedback: the Revision 7 cut was still primarily a billionaire-status check. It needed one
expensive, actionable business lesson from Ruiz's own interview and a 50–60s runtime, without
padding the edit with filler.

The source interview was reviewed beyond the original three excerpts. Four candidate lessons were
compared: scaling the problem, wealth as rebuilding ability, selling buyer value, and daily
execution. The selected lesson is Ruiz's answer at raw `727.10–749.62s`: money comes and goes, but
drive, know-how, and vision let a builder recreate value after a loss. This was chosen over the more
generic alternatives because it directly explains the volatility already established by the
Forbes/LIFW proof and turns the fact-check into an actionable distinction between a balance-sheet
snapshot and repeatable capability.

The lesson is not appended after the verification as a motivational afterthought. It is structured
as **quote → proof → payoff quote**:

1. host asks whether money went to Ruiz's head; Ruiz answers that money comes and goes and recalls
   not having `$10` for McDonald's;
2. Forbes `$1.5B / 2023`, Yahoo Finance `LIFW / MSPR`, and The Real Deal `$175M asking price` prove
   why net worth is a volatile snapshot;
3. Ruiz completes the lesson with the lemon-selling example, drive, know-how, vision, and
   "I'll be back"; the narrator closes: `Drive and vision are the engine. Comment your takeaway.`

The two new source excerpts are `11.96s` and `9.34s`, each under the 15s Transformative Gate. They
use original source audio, word-timed captions, and host/guest Active-Speaker Reframing. Runtime is
now `57.331s`, up `20.662s` from Revision 7 while remaining below the 60s Shorts ceiling.

QC caught two audio issues before handoff. The first final mix measured `-15.3 LUFS / -0.3 dBTP`,
which left too little true-peak headroom for platform transcoding; the final finish pass now applies
`-1.2dB`, measuring `-16.48 LUFS / -1.43 dBTP`. The Qwen payoff WAV also carried a non-silent model
tail after the final ASR word. Compression/loudnorm amplified it enough for full-file Whisper to
hallucinate repeated tail words. The renderer now fades from the measured final-word endpoint
(`3.28s`) and trims after a `0.20s` release. Isolated-tail ASR with both Whisper small and
large-v3-turbo confirms only the intended `Comment your takeaway.`

`Business Lesson Payoff` was added to `CONTEXT.md` as a reusable domain term. No ADR was added:
turning a verified story into one sourced, actionable lesson is a domain/content-model refinement,
not a hard-to-reverse renderer architecture decision.

## Production decision

This video originated from a hook-rewrite exercise (`docs/research/mrbeast-first-3s-2026-07-19/REPORT.md`) that analyzed a real MrBeast Short's first-3-seconds mechanics and produced 10 candidate opening frameworks. Hook **B1** ("Direct Dare Question" — a literal, unresolved question posed to the viewer over live, already-in-motion footage, no blurred card) scored well in the multi-judge panel and was selected to be built into a real video, alongside hook B9 (kept as a separate, not-yet-built video needing a different multi-subject source).

The source footage originally flagged during MrBeast research (`lU-bh2xPl4Y`, "Asking Miami Billionaires How They Got Rich!") turned out to be a School of Hard Knocks video, not MrBeast — caught before it was misused for the MrBeast analysis, then deliberately repurposed as this video's actual source footage. Of the video's interview subjects, only John Ruiz is clearly named and fact-checkable in the segment used here, so the video is scoped to a single-subject Blindspot Verification (this project's 3rd instantiation of that sub-format, after `hardknocks_v11`'s Ben Pogue video).

**Editorial correction applied before finalizing** (user feedback, 2026-07-19): an early draft framed "Forbes billionaire in 2023, not anymore because the stock collapsed" as a "gotcha"/lie. The user pushed back — normal stock-based wealth volatility isn't deception. Both the opening and ending VO scripts, the score-card verdict labels (no FALSE row), and the closing banner were rewritten to a neutral "lesson, not a lie" framing and confirmed with the user before rendering.

## Editorial thesis

Told as one continuous 3-act story (mở bài / thân bài / kết bài), not a sequence of disconnected
fact-check beats:

> **Mở bài** — Is he still a billionaire, or did that disappear with the stock? (unresolved, live
> handshake, identity tag confirms who he is, resolved only at the end) → **Thân bài** — he plants
> his own claim ("41st billionaire I've interviewed"), narrator bridges thread the story forward, his
> origin story (Cuban immigrant, dad homeless, first to college — verified TRUE) and his $175M house
> claim (REAL DEAL: that's the asking price, not a proven sale — verified UNVERIFIED) each get a
> small non-blocking verify badge while the footage keeps playing → **Kết bài** — Ruiz says money
> comes and goes; real Forbes/Yahoo/The Real Deal proof shows net worth is a volatile snapshot; Ruiz
> then names the durable rebuilding engine as drive, know-how, and vision. The verification is the
> evidence for the business lesson, not the whole point of the video.

## Primary source

- YouTube ID: `lU-bh2xPl4Y`
- URL: https://www.youtube.com/watch?v=lU-bh2xPl4Y
- Title: "Asking Miami Billionaires How They Got Rich!"
- Channel: School of Hard Knocks
- Local file: `output/projects/hardknocks/source/lU-bh2xPl4Y.mp4` (4K, 3840×2160, downloaded at max quality)
- Source duration: 1280.46s
- Raw primary-source use: 50.69s raw / 1280.46s = 3.96% (5 excerpts, all under 15s; Revision 8 adds two sourced business-lesson excerpts at 727.10–739.06s and 740.28–749.62s)
- Sub-format: Blindspot Verification Layer (3rd instantiation; builds on ADR-0022's Multi-Clip Mashup, `hardknocks_v11`'s inline-verify design)
- Hook pattern: B1, Direct Dare Question (`docs/research/mrbeast-first-3s-2026-07-19/round_b_hooks.md`)

## Commentary treatment

Four short Qwen-narrator (`natural_talker_male_qwen_blog`) VO beats thread the final story:

- Hook, mở bài (over the live handshake, dialogue ducked underneath): *"Is he still a billionaire? Or did that disappear with the stock?"*
- Bridge 1, into thân bài (dialogue ducked, then restored): *"He says it's a rags to riches story."*
- Proof bridge, kết bài (continuous VO over real proof screenshots and moving footage): *"His net worth proves the point. Forbes said 1.5 billion dollars in 2023. Then L-I-F-W crashed, taking the paper fortune with it. The 175 million dollar house? Asking price, not a sale. Net worth is a snapshot."*
- Business Lesson Payoff (over the final moving CTA shot): *"Drive and vision are the engine. Comment your takeaway."*

The old house bridge remains removed so the host's real valuation question leads directly into
Ruiz's complete answer. The proof VO and final payoff are separated by Ruiz's own lemon-selling /
drive / vision quote, so the lesson is demonstrated rather than merely narrated. Final ASR rendered
`L-I-F-W` as `LifeWallet`, confirming the acronym workaround produced natural speech rather than
spelling noise.

Unlike `hardknocks_v11`'s blurred-portrait opening card, the hook here plays directly over live footage — no card, no blur, Ruiz's face visible and in motion from frame 0 (ADR-0017; confirmed 16.44% skin-tone by pixel stats, over the 10% threshold) — with a small identity-tag graphic ("JOHN RUIZ · FORBES BILLIONAIRE, 2023") bouncing into the top-left corner at ~1.5s so the viewer knows who this is without a spoken introduction slowing the hook down. The interview body uses the subject's and host's original voices, one short narrator bridge, active-speaker reframing, and small inline verify badges that never replace the live footage.

## Exact edit map

Approximate final-timeline windows after the 1.19× uniform speed-up (Revision 8):

| Final (approx.) | Beat | Detail |
|---:|---|---|
| 0.00–4.62s | `hook_billionaire` (raw 519.70–525.20s) | Hook VO over the live handshake (dialogue ducked ~3.6s, then restored); identity tag bounces in ~1.3s; segment's own audio resolves to "...you were the 41st billionaire that I've interviewed on this channel" — plants the payoff resolved at the ending's evidence reveal |
| 4.62s | Bridge 1 VO | "He says it's a rags to riches story." (dialogue ducked ~1.9s, then restored) |
| 4.62–13.24s | `origin_claim` (raw 549.50–559.75s) | Ruiz-focused crop for the origin story → host-focused crop for "you didn't come from money?" → Ruiz-focused crop for "I came from nothing" |
| ~9.06s | Inline verify badge | "TRUE · RAGS TO RICHES STORY" — "CONSISTENT ACROSS FORBES + PRESS PROFILES" |
| 13.24–24.70s | `house_claim` (raw 580.38–594.02s) | Host-focused crop for the valuation question → Ruiz-focused crop for the complete answer: about $175M, bought for $46M, invested another ~$20M |
| ~19.3–21.8s | Inline verify badge | "UNVERIFIED · $175M HOUSE VALUE" — "THE REAL DEAL · ASKING PRICE ONLY · LISTED FEB 2026" |
| 24.80–34.84s | `lesson_money_moves` (raw 727.10–739.06s) | Host asks whether money went to Ruiz's head → Ruiz says money comes and goes, recalls having a lot/little and not having `$10` for McDonald's; host/guest reframes follow each turn |
| 35.02–38.96s | Forbes proof | `His net worth proves the point` → source-page crop showing John Ruiz, `$1.5B`, and `2023 Billionaires Net Worth` |
| 39.94–42.28s | Price-history proof | Yahoo Finance `MSPR` 5Y chart, labeled `LIFW / MSPR`; card says `THE STOCK COLLAPSED`, not market-cap history |
| 42.56–46.42s | House proof + lesson setup | The Real Deal `$175M` asking price / `$46M` prior purchase → narrator: `Net worth is a snapshot.` |
| 46.64–54.42s | `lesson_rebuild` (raw 740.28–749.62s) | Ruiz: sell lemons → drive → know-how → vision → could lose everything and be back; original source audio and captions |
| 54.78–57.33s | Business Lesson Payoff + CTA | `NET WORTH IS A SNAPSHOT` / `DRIVE + VISION ARE THE ENGINE` / `COMMENT YOUR TAKEAWAY`; card holds through the final frame |

No footage beyond these 5 excerpts (50.69s raw total, 3.96% of the 1280.46s source) was used.

## Blindspot verification layer (final claims)

| Criterion | Verdict | Citation shown on card | Independent source |
|---|---|---|---|
| 1. Origin story | TRUE | "Cuban immigrant, first to college" | Consistent across Forbes profile + press bios (Florida Trend, The Reality TV) |
| 2. $175M house | UNVERIFIED | "Real Deal: asking price, not a sale" | The Real Deal, "John Ruiz Lists Gables Estates Mansion for $175 Million" (Feb 2026) — confirms $46M 2020 purchase, $175M listing; no confirmed sale price |
| 3. Billionaire status | HISTORICAL / VOLATILE | "Forbes $1.5B · April 2023" + "LIFW / MSPR · 5Y price" | Forbes profile (`2023 Billionaires Net Worth: $1.5B`) + Yahoo Finance 5Y price chart for current ticker `MSPR` |

No criterion is labeled FALSE. The closing CTA card now reads **"NET WORTH IS A SNAPSHOT · DRIVE +
VISION ARE THE ENGINE"** — a deliberate departure from `hardknocks_v11`'s star-rating scorecard.
Ordinary stock-based wealth volatility should not be framed as a "gotcha"; it is the evidence for
the reusable business lesson that repeatable capability is more durable than one valuation.

All verification sources are independent third parties (Forbes, The Real Deal, Yahoo Finance) —
never School of Hard Knocks itself. Revision 7 captured and composited the actual page crops rather
than relying on outlet-name-only cards. Source assets live under
`output/projects/hardknocks/clips/v12_work/proof_sources/`.

## Transformative Gate

### Commentary
Pass. The Blindspot Verification format selects, reorders, and independently fact-checks the subject's own on-camera claims into a scored thesis; the hook and ending Qwen VO bridges are original narration, not present in the source.
### Value-adds

Pass, over the required 2:
1. inline independent-source verify badges with verdict stingers (ting/uncertain);
2. identity-tag graphic (new element, derived from MrBeast hook research);
3. word-burst captions rebuilt from ASR timing;
4. three real source-page proof crops (Forbes, Yahoo Finance, The Real Deal);
5. original commentary hook, bridge, ending, and lesson/CTA card;
6. ADR-0030 active-speaker reframing at every retained host/guest turn.

### Source-use limits
Pass. Every individual source excerpt is under 15 seconds (`5.50s / 10.25s / 13.64s / 11.96s /
9.34s`); total primary-source use is `50.69s`, `3.96%` of the 1280.46s source, far under 50%; final
duration is `57.331s`, inside the requested 50–60s window and under the Shorts ceiling.

## Final technical validation

- Resolution: 1080×1920, 9:16
- Duration: 57.331s
- Video: H.264, yuv420p, 30fps
- Audio: AAC stereo, 48kHz
- Post-speed: 1.19×
- File size: 45,097,892 bytes
- SHA-256: `3ae34e9f9b3d5cfee5933aae9581f9b0154f48e885220a6f4c2cb72b66272b73`
- Full decode: passed
- All `validate()` assertions passed: resolution, video codec, pixel format, audio codec, duration
  ≥50s and ≤60s, source clips <15s each, source usage <50%

Report: `output/projects/hardknocks/clips/v12_work/checks/validation.json`

## Audio QC

- Integrated loudness: -16.48 LUFS; true peak: -1.43 dBTP; LRA: 1.60 LU.
- `silencedetect` (-45dB / 0.4s): one 0.442s event at 36.228–36.670s, the intentional pause between
  `His net worth proves the point` and the Forbes evidence; no unintended gap.
- Large-v3-turbo final ASR confirms every retained body claim, including `$175M`, `$46M`, and
  another `$20M`, both source lesson excerpts, the complete proof bridge, and the final spoken CTA.
  Report: `output/projects/hardknocks/clips/v12_work/checks/final_asr_large_v3_turbo_r8.txt`.
- The full-file ASR decoder placed an impossible extra phrase inside its final 0.04s alignment
  window. A separate final-tail extraction was therefore transcribed with both Whisper small and
  large-v3-turbo; both return only `Comment your takeaway.` Report:
  `output/projects/hardknocks/clips/v12_work/checks/final_asr_tail_crosscheck_r8.txt`.
- `blackdetect`: zero events. `freezedetect` at `n=0.003:d=1.5`: zero events.
- Hook/bridge ducking and the ending VO remain clearly above the music bed; the final gain trim adds
  platform-transcode headroom and the Qwen tail fade preserves the complete closing word.

## Manual visual QC

Verified via frame extraction, contact sheet (`output/projects/hardknocks/clips/v12_work/checks/contact.jpg`), and direct reads across both the 1st-pass and this rebuild's render iterations:

- frame 0 is the live handshake — Ruiz's face clearly lit, unblurred, in motion (not a title card or freeze-frame), passing ADR-0017; confirmed quantitatively via `inspect_image.py`: 16.44% skin-tone (over the 10% threshold), 27.6% near-black (background/shadow, not a title card);
- **found and fixed (Revision 3, bug 3)**: a persistent black footer band (the bottom ~270px of every single frame, throughout the whole video, not just the ending) — root-caused to `mix_and_caption()`'s own `drawbox` blackout, which was only ever meant to hide the source's pre-existing captions but left an empty black strip since this project's own captions render higher up the frame. Fixed at the source: `scaled_crop()` now crops that band off and zooms back up uniformly (no aspect distortion) at the base per-segment render stage, so no downstream step needs a blackout at all. See "Revision 3" above for full detail;
- identity tag ("JOHN RUIZ · FORBES BILLIONAIRE, 2023") bounces in cleanly in the top-left corner at ~1.5s raw, never overlapping the caption band;
- captions render legibly with keyword highlighting (numbers/proper nouns in a distinct color), confirmed against the source transcript word-for-word;
- the whole ending sequence plays over continuously-moving real footage, with real Forbes/Yahoo/The
  Real Deal proof crops instead of a cumulative scorecard or flat/dark/dead screen;
- **found and fixed during this rebuild's own QC (bug 1)**: the ending backdrop loop initially showed School of Hard Knocks' own pre-existing burned-in captions (present in the raw downloaded source itself, e.g. "and I've invested...") bleeding through underneath our score/evidence cards, because `make_ending_backdrop()` reused the raw segment clip directly without the same bottom-band blackout `mix_and_caption()` already applies to the interview section. Fixed by adding the identical `drawbox` blackout to the backdrop's own filter chain; re-rendered and re-verified via direct frame reads that the source's own captions no longer appear anywhere in the ending;
- **found and fixed during this rebuild's own QC (bug 2)**: the inline verify badges (origin story, house value) silently never appeared anywhere in the render — caught only by extracting frames at the exact calculated timestamps and seeing plain interview footage with no badge. Root cause: `composite_inline()` used a different, broken ffmpeg overlay idiom than the rest of the file (shifting the badge PNG's own input PTS forward via `setpts=PTS-STARTPTS+{at}/TB` on a short `-loop 1 -t {duration}` input, leaving no frame for the overlay filter to composite before that shifted start). Fixed by switching to the same idiom used everywhere else in this renderer (`build_ending()`'s row/evidence cards): loop the PNG for the *whole* interview duration and gate visibility purely via the overlay's own `fade`/`enable=between(...)` clauses. Re-rendered and confirmed both badges now render correctly, fading in over the live footage without blocking either face;
- active-speaker spot checks at 11.20/11.70/12.20/12.60s confirm guest → host → guest; checks at
  15.30/15.90s confirm host → guest for the house question and answer;
- Revision 8 dense checks at 24.0–36.0s confirm host question → Ruiz `Never` → host `Why not` →
  Ruiz answer, with no unintended face crop; the second lesson excerpt remains Ruiz-focused through
  the lemon / drive / vision / `I'll be back` payoff;
- all three proof cards are readable at 1080×1920, retain the publisher/ticker identity, and contain
  no clipped text or missing Unicode glyphs; dense 0.5s checks confirm clean Forbes → Yahoo → The
  Real Deal → Ruiz transitions;
- the Business Lesson card is fully readable from ~54.8s and remains present at
  56.50/56.80/57.05/57.20s through the final usable frame, with all lesson and CTA lines intact.

## Experiment interpretation

This video tests **hook pattern B1 (Direct Dare Question)** applied to the Blindspot Verification sub-format, using real live footage (not a blurred card) for the hook window and a small identity-tag graphic instead of a spoken introduction. It is not a controlled variant of `hardknocks_v11` — that video used a different hook mechanic (blurred-portrait reveal + branded scoring card) on a different subject. The comparison to watch for is retention through the 0–2s window specifically: does opening on live, unresolved motion (per the MrBeast-derived mechanic) outperform `hardknocks_v11`'s blur-reveal card, independent of the subject-matter difference.

## What to check after upload + 48 hours

1. Inspect 0–2s: does the live handshake + unresolved question hold viewers through the hook window better than `hardknocks_v11`'s blurred-card open?
2. Inspect whether the identity-tag graphic (new element) reads clearly at a glance without pausing, or gets missed/ignored.
3. Inspect the Business Lesson setup at ~24.8s: does Ruiz's `$10 McDonald's` memory create a second
   retention peak or a dip before the verification evidence begins?
4. Inspect the quote → proof → payoff sequence (~24.8–57.3s): do viewers stay through the
   Forbes/Yahoo/The Real Deal evidence and return to Ruiz's `I'll be back` conclusion, or leave once
   the billionaire-status question is answered?
5. Compare retention curve shape against `hardknocks_v11` descriptively only — this is a
   hook-mechanic + lesson-payoff test on a new subject, not a controlled A/B.

## YouTube Metadata

**Canonical title**

`John Ruiz's Billionaire Lesson: Build the Skill, Not the Net Worth`

**Description**

Forbes listed John Ruiz at $1.5B in 2023. Then LifeWallet stock collapsed, while his $175M mansion
remained an asking price—not a completed sale. His deeper business lesson: net worth is a snapshot;
drive, know-how, and vision are the assets that can rebuild it.

`#JohnRuiz #BusinessLessons #Money`

**YouTube Studio tags**

`John Ruiz, LifeWallet, LIFW, MSPR, billionaire, Forbes billionaire, business lessons, entrepreneurship, drive and vision, money mindset, $175 million house, Miami mansion, stock wealth, net worth, finance, School of Hard Knocks, Shorts`

## Post-Production Retro

### Hook Retro

- Verbal: the hook VO ("Is he still a billionaire? Or did that disappear with the stock?") is phrased as a literal, unresolved binary question per the Direct Dare Question pattern — resolved only by the ending's source evidence, not before.
- Visual: frame 0 shows the live handshake with Ruiz's face clearly visible and in motion — no blur, no card, no delay. This is a deliberate departure from `hardknocks_v11`'s blur-reveal card, directly testing the MrBeast-derived finding that real motion + audio can carry a hook without any on-screen text needing to land before ~1.5s (see `docs/research/mrbeast-first-3s-2026-07-19/REPORT.md`).

### Workflow Delta

- The identity-tag overlay (small name + 1-line credential graphic, bounce-in ~1.5s) is a new reusable element, worth keeping in the toolkit for any future hook that opens on live, unresolved footage of a subject the viewer can't immediately place.
- For concrete money claims, real source-page crops were materially stronger than outlet-name-only
  cards: the viewer can see `$1.5B / 2023`, the 5Y price collapse, and `$175M asking price` directly.
  Keep proof cards compact over a moving backdrop rather than turning the ending into a static page.
- Editorial calibration: verdict language must scale with how the claim actually fails to check out. A stock-price collapse is not the same failure mode as an unsubstantiated personal claim (`hardknocks_v11`'s "$200M/year personal, 0 public records found") or a family member's separate legal record (`hardknocks_v11`'s LEGACY criterion) — the scorecard and closing VO should say so explicitly ("lesson, not a lie") rather than defaulting to a punitive frame for every less-than-fully-TRUE verdict.
- Pacing/structure: retain the subject's complete claim, use active-speaker reframing for turn
  clarity, then make verification serve one sourced Business Lesson Payoff. Quote → proof → payoff
  quote is stronger than ending at the fact-check or appending a generic lesson card afterward;
  extra narrator bridges and cumulative score rows can make the story longer while conveying less.
- Two reusable ffmpeg gotchas surfaced by this rebuild's own QC were promoted to AGENTS.md Known Pitfalls (both are latent risks for any future renderer that loops raw segment footage as a backdrop, or overlays a short-duration PNG for only part of a longer timeline): (1) a raw segment clip reused as a backdrop can carry the source video's own pre-existing burned-in captions straight through unless explicitly blacked out again; (2) shifting a short overlay PNG input's own PTS forward (instead of looping it for the full timeline and gating visibility via `enable=`) silently produces no overlay at all, with no ffmpeg error to flag it.
- Two more ffmpeg audio gotchas from the Revision 4 loudness fix, also promoted to AGENTS.md Known Pitfalls: (3) `adelay` before `loudnorm` corrupts the loudness measurement (integrates over the silence prefix too) — always normalize loudness first, then delay; (4) `loudnorm`'s `TP` ceiling caps achievable loudness on high-crest-factor clips regardless of single- vs. two-pass mode — a mild compressor before loudnorm, not a fancier loudnorm invocation, is the actual fix. Both were invisible testing the VO clip in isolation and only showed up once actually mixed into the real timeline — worth remembering that audio QC needs to sample the *final mixed* track in fine time-slices, not just validate each source clip standalone.

No upload, commit, or push was performed.
