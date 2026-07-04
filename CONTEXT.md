# Shorts Project Context

Animated short video factory: tự động sản xuất 6 videos/ngày (9:16, 30-60s) để AB test viral content formulas trên YouTube + TikTok, kiếm tiền qua ads revenue và affiliate marketing.

Niche: Finance / money-making (crypto, side hustle, investing).
Ngôn ngữ: Tiếng Anh (global audience, RPM cao).
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
0-2 giây đầu video. Theo HEIT framework, 3 types: Context, Contrarian, Intrigue.
_Avoid_: "intro", "opening"

**AVD** (Average View Duration):
Phần trăm video trung bình người xem xem trước khi scroll. Metric #1 cho viral potential.
_Avoid_: "watch time", "retention" (use specific term)

**Video Type**:
Một trong 7 visual rendering styles: Stock Footage, Kinetic Typography, Data Viz, HTML/CSS Motion, Whiteboard Sketch, Meme/Notification, Clip Curation Edit. Là AB variable chính.
_Avoid_: "format", "template" (use specific term)

**Source Channel**:
Kênh YouTube finance viral (VD: School of Hard Knocks, 2.08M subs) dùng làm research input. Chỉ lấy topic/facts/hooks, KHÔNG lấy footage.
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
Per-second audience retention curve từ YouTube Analytics API. Dùng để detect key moments (dips = boring, peaks = viral). 48h lag.
_Avoid_: "watch time graph"

**Key Moment**:
Điểm đặc biệt trong retention graph: dip (viewers skip), peak (rewatch), flat (engaged). Inform hook/pacing decisions cho videos tiếp.
_Avoid_: "highlight", "retention spike"

## Project Name

Package name (from package.json khi init): `shorts`
Wiki slug: `shorts`
