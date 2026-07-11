# Comment Psychology — Reading Audience Reaction

Methodology carried over from `docs/research/hook-benchmarks-2026-07/REPORT.md` section 3
("Tâm lý người xem từ comment"), which read all ~100 top comments per video (not just a
skim) and found that the actual viral driver for one channel cluster was mockery of "vòng vo
logic" (circular reasoning), not admiration — a finding that surface-level comment reading
would have missed entirely. That is the standard to match: read every comment fetched, don't
sample.

## Fetch

```bash
yt-dlp --write-comments --skip-download -o "<video_id>.%(ext)s" "<url>"
```

Save the top 100 comments and a `comments_highlights.json` (most-liked / most-replied subset)
into the video's subfolder, same as the existing `hook-benchmarks-2026-07/<video_id>/` folders.

## What to look for

1. **What viewers explicitly praise** — which specific moment/line/visual gets quoted back?
   Direct quotes in comments are the strongest signal of what actually landed.
2. **What viewers mock or fact-check** — sarcasm, "well actually" corrections, disbelief. This
   can co-exist with virality (people share things they mock, not just things they admire) —
   do not assume positive engagement means agreement.
3. **What viewers ask/are confused about** — recurring questions reveal a gap the video left
   open (sometimes intentionally, as a hook mechanism; sometimes a genuine confusion that hurt
   comprehension — distinguish the two).
4. **Recurring phrases lifted from the video** — if many comments repeat the same line from
   the video verbatim, that line is doing outsized work; flag it as a candidate hook/CTA
   pattern to test.
5. **Niche-transfer caution**: a psychological driver found in one audience (e.g. English
   finance-content viewers mocking circular logic) does not automatically transfer to a
   different niche/language/audience (e.g. Vietnamese health content). Flag this explicitly
   per the "Cảnh báo riêng cho Bác sĩ Hải" precedent in the existing REPORT.md rather than
   assuming universality.

## Output

A short prose section per video (not raw comment dumps) answering the 4 points above, feeding
into the report's synthesis section — see `report-template.md`.
