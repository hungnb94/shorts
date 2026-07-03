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

## Project Name

Package name (from package.json khi init): `shorts`
Wiki slug: `shorts`
