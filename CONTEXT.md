# Shorts Project Context

Animated short video factory: tự động sản xuất 6 videos/ngày (9:16, 30-60s) để AB test viral content formulas trên YouTube + TikTok, kiếm tiền qua ads revenue và affiliate marketing.

Niche: 3 verticals song song (ADR-0019, ADR-0020) — Finance/money-making (crypto, side hustle, investing, tiếng Anh, niche gốc), Health/longevity (tiếng Việt, Source Channel "Bác sĩ Hải"), AI education (tiếng Anh, professionals/knowledge workers).
Ngôn ngữ: Tiếng Anh cho niche finance + AI education (global audience, RPM cao); Tiếng Việt cho niche health (khán giả Việt Nam).
Content strategy: Curate + Repackage — lấy topic/facts/hooks từ kênh finance viral, render lại 100% bằng animation gốc. Zero footage từ nguồn.
Automation: Phased — Phase 1 semi-auto (AI generate, human review) → Phase 2 fully autonomous cron pipeline.

## Language

**Short**:
Một video 9:16, 30-60 giây, MP4 H.264. Đơn vị sản xuất và AB test cơ bản.
_Avoid_: "video", "clip", "content" (quá chung)

**CRF (Constant Rate Factor)**:
Tham số chất lượng libx264. Giá trị thấp = chất lượng cao + file lớn. CRF=15 (near-lossless, dùng cho mọi encoding step), CRF=18 (visually lossless, trước đây dùng cho final render), CRF=23 (ffmpeg default, medium quality — tránh). Mọi encoding step trong pipeline phải chỉ định CRF rõ ràng, không để ffmpeg tự chọn default.
_Avoid_: "quality setting", "compression level"

**Lanczos Filter**:
Scaling algorithm cao cấp cho ffmpeg (`flags=lanczos`). Bắt buộc dùng khi downscale source 2160p → 1080p hoặc upscale source 640x360 → 1080x1920. Mặc định ffmpeg dùng bilinear (chất lượng thấp hơn rõ rệt). Mọi `scale=` filter trong pipeline phải có `:flags=lanczos`.
_Avoid_: "bilinear", "bicubic" (chất lượng thấp hơn)

**Batch**:
Nhóm 3 videos dùng chung 1 variant (A hoặc B) trong AB test. Mỗi ngày = 1 experiment = 2 batches (A vs B).
_Avoid_: "group", "set"

**Experiment**:
Một lần AB test chạy trong 1 ngày: A (control) vs B (test 1 biến). Declare winner sau 7 experiments liên tiếp cùng biến.
_Avoid_: "test", "comparison"

**Variant**:
Giá trị cụ thể của biến đang test. VD: "hook type = Contrarian" là một variant.
_Avoid_: "version", "option"

**Hook**:
0-2 giây đầu video — nhưng thực chất là 1 cung 2 giai đoạn: setup 1 gap/mystery (vật thể chưa rõ, danh tính bị giấu, câu hỏi bị né) rồi partial reveal trong 5-8s, không phải 1 câu tuyên bố tĩnh đã đầy đủ nghĩa. HEIT liệt kê 3 type (Context, Contrarian, Intrigue) nhưng khảo sát 6 video viral (2026-07, xem `docs/research/hook-benchmarks-2026-07/REPORT.md`) cho thấy hook hiệu quả thường là hybrid Context→Intrigue, hoặc dạng **Dare/Challenge** (thách đố kết cục nhị phân) chưa khớp type nào trong 3 type gốc. Với Clip Curation Edit, frame t=0 của cut PHẢI chứa mặt người hoặc hành động/prop rõ ràng — không phải title card tĩnh (xem Hook-Window Rule).
_Avoid_: "intro", "opening"

**Hook Caption Sync**:
Caption burned-in phải bắt đầu ngay t=0 (không đợi giây thứ 2-3), sync theo từng cụm từ đang nói, với 1 từ khóa cảm xúc/số liệu nhấn màu khác (thường vàng). Xuất hiện ở 6/6 video trong khảo sát `docs/research/hook-benchmarks-2026-07/REPORT.md` — pattern chưa được ghi nhận trước đó dù universal.
_Avoid_: "subtitle", "text overlay" (quá chung, không nói rõ yêu cầu timing/nhấn từ)

**Hook-Window Rule**:
Quy tắc chọn điểm bắt đầu source segment cho Clip Curation Edit (ADR-0017): frame tại t=0 của cut phải chứa mặt người — skin-tone ≥10% theo pixel statistics, hoặc confirm visually. Title card / text graphic / slide / B-roll establishing / "numbered list transition" bị cấm làm segment start. Overlay đầu tiên phải land ≤t=2s. Nguyên nhân ra đời: bacsihai V1 (YQTWHqTS1e8) = 8.6% stayed vì segment bắt đầu tại 304.5s = static title card "Sai lầm số 5" (85% near-white, 0% face), mặt người đầu tiên ở t=5s. So với Dangote (ChWLcE3OYpA) = 50% stayed, mặt người + motion ngay t=0.
_Avoid_: "hook rule", "face rule"

**Swiped Away**:
% impressions trong Shorts feed mà viewer swipe trong vài giây đầu. Label: YouTube Studio → Engagement → "How viewers engaged" → "Swiped away." Denominator = impressions. Đo sức hút của frame 0. Khi Stayed to Watch hoặc AVD không hiển thị (video ít view), đây là metric fallback duy nhất.
_Avoid_: "bounce rate", "scroll away", "exit rate"

**Stayed to Watch**:
% views (không phải impressions) mà viewer xem vượt qua vài giây đầu — "engaged views" theo YouTube Partner Program. Label: YouTube Studio → Engagement → Audience retention → "Stayed to watch." Denominator = views (đã loại swiped away). Đo engagement ở gate 2 — viewer ĐÃ vào xem, có ở lại hay thoát ngay. [NOTE: denominator chính xác chưa verify trực tiếp với YouTube docs — web research (shortimize.com) cho biết đây = engaged views, không phải impressions. Cần confirm khi có thêm data.]
_Avoid_: "viewed percentage" (đó là 100 − Swiped away, denominator khác), "retention", "viewed" (use specific term)

**AVD** (Average View Duration):
Số giây tuyệt đối trung bình viewer xem video (những người ĐÃ stayed). Label: YouTube Studio → Overview → "Average view duration." Đo sức giữ của toàn bộ video. Để so sánh giữa các video khác duration, chia AVD cho tổng duration → Average percentage viewed. KHÔNG phải % — là số giây. Định nghĩa cũ (dòng trước đây nói "phần trăm") SAI.
_Avoid_: "watch time" (tổng giây của tất cả viewers, không phải trung bình), "retention" (use specific term)

**Video Type**:
Một trong 7 visual rendering styles: Stock Footage, Kinetic Typography, Data Viz, HTML/CSS Motion, Whiteboard Sketch, Meme/Notification, Clip Curation Edit. Là AB variable chính.
_Avoid_: "format", "template" (use specific term)

**Source Channel**:
Kênh YouTube dùng làm research input, cho MỘT trong 3 niche song song (ADR-0019, ADR-0020): finance viral (VD: School of Hard Knocks, 2.08M subs, tiếng Anh), health/longevity (VD: Bác sĩ Hải, tiếng Việt), hoặc AI education (VD: @mattpocockuk, @anthropic-ai — kênh practitioner/product, không nhất thiết phải "viral how-to" như 2 niche kia). Với 6 animation types (Repackage), chỉ lấy topic/facts/hooks (hoặc style/structure với niche AI education), KHÔNG lấy footage. Với Clip Curation Edit, có lấy footage nhưng vẫn transform (xem Transformative Gate).
_Avoid_: "inspiration", "reference channel"

**Curate**:
Quá trình xem video từ Source Channel, extract topic + facts + hook pattern. Output = text research notes, không phải video.
_Avoid_: "copy", "steal", "scrape"

**Repackage**:
Render lại curated content bằng Video Type gốc (animation). Output = 100% original visual, cùng information value. Khác với re-upload (dùng footage gốc).
_Avoid_: "remix", "edit", "cut"

**AB Variable**:
Một dimension được thay đổi giữa A và B trong experiment. Chỉ 1 biến đổi mỗi experiment.
VD: video type, hook type, title pattern, video length, voice, CTA, thumbnail.
_Avoid_: "parameter", "factor"

**Clip Curation Edit**:
Video Type #7. Download footage từ Source Channel + cut + transform (commentary + value-adds). Khác Repackage (zero-footage animation gốc).
_Avoid_: "remix", "edit", "cut" (use specific term)

**Transformative Edit**:
Synonym cho Clip Curation Edit — editing approach (cut + commentary + value-adds) đủ khác để qualify Fair Use.
_Avoid_: "highlight edit", "re-edit"

**Transformative Gate**:
3 pipeline rules ALL required trước khi upload Clip Curation Edit: (1) commentary track, (2) min 2 value-adds, (3) cut ≤50% source + mỗi clip <15s. Auto-checkable.
_Avoid_: "Fair Use check"

**Hard-Crop Convention** (ADR-0024):
Mọi Clip Curation Edit BẮT BUỘC crop lấp đầy toàn bộ khung 1080x1920 bằng footage nét — không dùng blur-fill pillarbox (nền mờ full-bleed + video thu nhỏ ở giữa), dù pillarbox vẫn kỹ thuật đúng spec 9:16. Nếu caption cháy sẵn của nguồn bị crop cắt mất, tự viết lại caption (drawtext, word-synced từ transcript) thay vì chuyển sang pillarbox. `bacsihai_v6` (đã upload) được grandfathered, không re-render.
_Avoid_: "pillarbox", "letterbox" (kỹ thuật đã bị cấm dùng làm giải pháp, trừ bacsihai_v6 grandfathered)

**Value-Added Editing (VAE)**:
Umbrella term cho việc thêm layers giá trị mới (thông tin + retention) mà bản gốc không có. Apply cho TẤT CẢ 7 video types, không chỉ Clip Curation Edit. Bao gồm 2 nhóm: Value-Add Layer (AB testable) + Retention Techniques (base quality).
_Avoid_: "editing style", "format enhancement"

**Value-Add Layer**:
Post-render compositing step — render base video trước, rồi composite value-add overlay on top. Là AB variable: "có value-add vs không" hoặc "type A vs B" trên cùng 1 video type. 9 types tổng (xem Value-Add Type). Independence: tách khỏi renderer chính → dùng cho mọi video type.
_Avoid_: "overlay", "effect" (quá chung)

**Value-Add Type**:
1 trong 9 information overlays: (hiện có) fact_check_callout, data_viz_overlay, counter_argument, source_citation, animated_annotation, multi_source_mashup + (mới) this_or_that_overlay, split_screen_comparison, timeline_overlay. multi_source_mashup = clip-only (cần footage). Max 8 apply cho animation.
_Avoid_: "annotation", "widget"

**Retention Techniques**:
Base quality layer áp dụng TỰ ĐỘNG cho mọi video, KHÔNG phải AB variable: sound design (whoosh/riser/impact), zoom punch, pattern interrupt (visual change mỗi 2-4s), cut rhythm. Thiếu = kém chất lượng, không công bằng khi test.
_Avoid_: "effects", "polish"

**this_or_that_overlay**:
Value-Add Type mới. Binary choice overlay "A vs B" (VD: "Rent vs Buy", "Index vs Stock pick"). Phù hợp niche finance, MONEY+TIMEFRAME hook pattern.
_Avoid_: "comparison widget"

**split_screen_comparison**:
Value-Add Type mới. 2 panels side-by-side so sánh (VD: "5AM vs 8AM"). Dùng cho comparison hooks.
_Avoid_: "dual screen"

**timeline_overlay**:
Value-Add Type mới. Timeline/milestone bar (VD: "Day 1 → Day 30 → $1M"). Phù hợp "He made $X in Y time" hooks.
_Avoid_: "progress bar" (đã có trong render), "timeline video"

**Autonomous Optimization System**:
Hệ thống tự động upload + measure + improve videos. 3-day cycle: upload 18 videos → wait 48h metrics → MAB adjust strategy → repeat. Không cần human input sau setup.
_Avoid_: "AI optimizer", "auto-improve"

**Optimization Cycle**:
1 iteration của autonomous system: 3 days upload (18 videos) + 48h metrics wait = 5 days total. Sau đó analyze + adjust strategy cho cycle tiếp.
_Avoid_: "training loop", "iteration"

**Multi-Armed Bandit (MAB)**:
Optimization algorithm chọn variant nào upload tiếp. Balance explore (test mới) vs exploit (dùng top performers). Epsilon-greedy: 50-50 lúc đầu → 20-80 sau 3 cycles.
_Avoid_: "reinforcement learning", "AI model"

**Epsilon (ε)**:
Tỉ lệ explore trong MAB. ε=0.5 = 50% explore (random variants), 50% exploit (top-3). Decay về 0.2 sau 54 videos.
_Avoid_: "exploration rate"

**Chrome Profile Auth**:
Upload method: user đăng nhập YouTube vào Chrome profile cố định, system dùng profile đó để upload (không dùng OAuth API). Playwright automation.
_Avoid_: "browser automation", "headless Chrome"

**Retention Graph**:
Per-second audience retention curve từ YouTube Analytics API. Dùng để detect key moments (dips = boring, peaks = viral). 48h lag. Implemented (ADR-0025): fetched by `src/platforms/youtube-analytics.ts` via OAuth (`yt-analytics.readonly`), triggered qua `/fetch-metrics` skill, raw curve lưu tại `output/projects/<project>/final/<video-id>-retention.csv` (per-second data quá lớn cho markdown table).
_Avoid_: "watch time graph"

**Key Moment**:
Điểm đặc biệt trong retention graph: dip (viewers skip), peak (rewatch), flat (engaged). Inform hook/pacing decisions cho videos tiếp. Implemented (ADR-0025): detect bằng z-score của residual so với rolling-average baseline, ngưỡng tính riêng cho từng video (không hardcode 1 hằng số chung cho mọi video) — cùng nguyên tắc với pause-trim threshold (AGENTS.md).
_Avoid_: "highlight", "retention spike"

**Metrics Status**:
Chuỗi literal trong production doc's Status table (`Metrics status` field) mà `/fetch-metrics` skill dùng để tự quét: `"Not yet fetched..."` (match substring, prose có thể khác nhau) = còn due để fetch; `"Fetched YYYY-MM-DD"` (chính xác, không thêm prose) = đã fetch xong, loại khỏi batch scan sau này.
_Avoid_: viết prose tự do vào field này sau khi đã fetch — phải đúng literal `Fetched YYYY-MM-DD` để scanner nhận diện được

**Target**:
Mục tiêu dạng outcome-measurable đặt cho 2 tuần (Target Cohort horizon), KHÔNG phải per-video hay per-cycle. Đo = AVD trung bình cohort ≥ ngưỡng X%. Khác Optimization Cycle (3 ngày execute unit). Đây là layer strategic phía trên MAB.
_Avoid_: "goal", "objective", "target" (khi dùng cho video/cycle)

**Target Cohort**:
Tập 18 videos × ~3 cycles ≈ 2 tuần mà 1 Target áp dụng. Khi đặt Target mới = bắt đầu cohort mới. Cohort collects outcomes từ các cycle bên trong để chốt đạt/không đạt Target.
_Avoid_: "batch" (đã dùng cho AB), "period"

**Success Formula**:
Khung goal-planning 9 bước áp dụng ở đầu mỗi Target Cohort: (1) mục tiêu (Target statement), (2) kết quả đo được, (3) tại sao quan trọng, (4) mức tự tin 1-100%, (5) điều kiện tự tin 100%, (6) việc cần làm, (7) sắp xếp ưu tiên, (8) chọn 3 việc đầu → mổ xẻ hành động, (9) thực thi. Loop feedback: thành công → nâng Target; thất bại → research + nâng cấp → quay bước (6). Khác Optimization Cycle (vòng learning, không có steps 1-3).
_Avoid_: "goal framework", "OKR"

**Hypothesis**:
Một dự đoán có cấu trúc từ Analyzer output: "Variant dimension A + Variant dimension B → AVD +X% trên Video Type C". Có 3 thành phần: predicted_impact (%), confidence (0-1), effort (1-5). Khác với AB Variable (đơn lẻ) — Hypothesis là combo multi-dimension.
_Avoid_: "guess", "theory", "variant combo"

**ICE Score**:
Heuristic prioritization cho Hypotheses: Impact × Confidence / Effort. Impact = predicted AVD lift (%), Confidence = analyzer evidence strength, Effort = 1 (MAB config only) đến 5 (new value-add development). Rank hypotheses để chọn Top 3.
_Avoid_: "priority score", "ranking"

**MAB Override**:
File config ghi đè hành vi MAB cho 1 cycle cụ thể: `variant_priority_boost` (ưu tiên hook/value-add/video-type), `epsilon_override`, `value_add_config`, `duration_override`. Được tạo ở Step 8, MAB đọc tự động ở cycle sau. Khác MAB State (learned rewards).
_Avoid_: "MAB config", "manual override"

**Auto-Crawl**:
Tự động tìm + tải + phân tích top N finance channels (YouTube search → yt-dlp transcript → pattern extract) khi cohort fail. Output = hypotheses mới cho cohort sau. Human gate: system trình bày findings, user approve trước khi inject.
_Avoid_: "scraping", "research bot"

**Cohort Evaluation**:
Tính toán mean AVD của 18 videos (3 cycles) sau khi metrics fetched. So sánh với Target threshold. Trigger Success Formula Step 9 loop (success → raise target / failure → auto-crawl).
_Avoid_: "cohort review", "post-mortem"

**Source Channel Pattern**:
Format hook được trích xuất từ phân tích top videos của kênh viral reference (vd: @theschoolofhardknocks — 31M views/top short). 3 pattern types đã identify: (1) Money+Number ($58,380, $2.5M car), (2) Curiosity Gap ("THIS is the real secret"), (3) Contrarian Reveal ("Good culture isn't made in the game"). Khác AB Variable (đơn lẻ) — Source Channel Pattern là combo hook+structure hoàn chỉnh copy từ proven viral. [NOTE: 1 phân tích khác (`docs/research/800m-view-case-study-2026-07-11/REPORT.md`, kênh RandomDude 808M views) tìm thấy 1 pattern thứ 4 chưa khớp cả 3 type trên — xem "Implied Comparison Hook" bên dưới. Chỉ 1 video, coi là hypothesis chưa confirm.]
_Avoid_: "hook template", "title formula"

**Implied Comparison Hook**:
Pattern hook thứ 4 (hypothesis, 1 video, xem `docs/research/800m-view-case-study-2026-07-11/REPORT.md`), khác 3 Source Channel Pattern gốc. Không có 1 dòng hook nào tự giải thích gap — caption chỉ label 1 phía ("OTHERS X SKILL") và chính TITLE/thể loại video ngầm hứa hẹn phía còn lại ("...VS King of X") sẽ xuất hiện sau. Cho phép gap dài bất thường (~40s trong case study, so với 5-8s target hiện có của HEIT) MIỄN LÀ đoạn chờ được lấp bằng 1 montage đủ đa dạng/giải trí để tự nó giữ chân người xem — gap không được resolve bởi câu chữ mà bởi kỳ vọng thể loại. Payoff/reveal luôn được camera "dwell" lâu hơn hẳn (case study: ~3x) so với các clip dựng cảnh (setup) trước đó.
_Avoid_: "comparison hook" (thiếu phần "không resolve bằng câu chữ"), "vs hook"

**Verbatim Segment**:
Đoạn audio gốc từ source video (Andy Frisella etc.) được extract nguyên bản, không TTS override. Là cốt lõi của Mode A. TTS chỉ dùng cho hook và CTA — phần giá trị giữa luôn là giọng thật. Xác nhận perform tốt hơn pure TTS (19.5% AVD cho pure TTS vs winner Mode A).
_Avoid_: "source clip", "raw audio", "original quote"

**Mode A**:
Render format: TTS Hook → Verbatim Segments (×4) → TTS CTA → Optional padding. Chỉ giữ 1 mode — Mode B (hybrid TTS+source quote) đã bị loại sau khi test. Audio: hook 5-7s + segments 16-20s + CTA 9-11s = 33-39s total. Khác Mode B đã deprecated.
_Avoid_: "verbatim mode", "source audio mode", "Mode B"

## Project Name

Package name (from package.json khi init): `shorts`
Wiki slug: `shorts`
