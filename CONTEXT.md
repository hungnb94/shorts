# Shorts Project Context

Animated short video factory: sản xuất Shorts 9:16, 50-75s và phát hành qua ba Channel Pool theo Plateau-Gated Cadence để AB test viral content formulas trên YouTube + TikTok, kiếm tiền qua ads revenue và affiliate marketing.

Niche: 3 verticals song song (ADR-0019, ADR-0020) — Finance/money-making (crypto, side hustle, investing, tiếng Anh, niche gốc), Health/longevity (tiếng Việt, Source Channel "Bác sĩ Hải"), AI education (tiếng Anh, professionals/knowledge workers).
Ngôn ngữ: Tiếng Anh cho niche finance + AI education (global audience, RPM cao); Tiếng Việt cho niche health (khán giả Việt Nam).
Content strategy: Curate + Repackage — lấy topic/facts/hooks từ kênh finance viral, render lại 100% bằng animation gốc. Zero footage từ nguồn.
Automation: Phased — Phase 1 semi-auto (AI generate, human review) → Phase 2 fully autonomous cron pipeline.

## Language

**Short**:
Một video 9:16, 50-75 giây, MP4 H.264 có audio stream. Đơn vị sản xuất và AB test cơ bản (ADR-0034); range này là policy nội bộ, không phải giới hạn kỹ thuật của YouTube.
_Avoid_: "video", "clip", "content" (quá chung)

**CRF (Constant Rate Factor)**:
Tham số chất lượng libx264. Giá trị thấp = chất lượng cao + file lớn. CRF=15 (near-lossless, dùng cho mọi encoding step), CRF=18 (visually lossless, trước đây dùng cho final render), CRF=23 (ffmpeg default, medium quality — tránh). Mọi encoding step trong pipeline phải chỉ định CRF rõ ràng, không để ffmpeg tự chọn default.
_Avoid_: "quality setting", "compression level"

**Lanczos Filter**:
Scaling algorithm cao cấp cho ffmpeg (`flags=lanczos`). Bắt buộc dùng khi downscale source 2160p → 1080p hoặc upscale source 640x360 → 1080x1920. Mặc định ffmpeg dùng bilinear (chất lượng thấp hơn rõ rệt). Mọi `scale=` filter trong pipeline phải có `:flags=lanczos`.
_Avoid_: "bilinear", "bicubic" (chất lượng thấp hơn)

**Batch**:
Nhóm 3 Shorts dùng chung 1 variant (A hoặc B) trong AB test, mỗi Short đi vào một lane khác nhau của Channel Pool theo thứ tự round-robin. Batch không còn gắn với một ngày lịch.
_Avoid_: "group", "set"

**Experiment**:
Một lần AB test gồm A (control) vs B (test đúng 1 biến), mỗi phía là một Batch. Experiment hoàn tất khi mọi Short đủ điều kiện đo; không còn mặc định chạy trong một ngày.
_Avoid_: "test", "comparison"

**Variant**:
Giá trị cụ thể của biến đang test. VD: "hook type = Contrarian" là một variant.
_Avoid_: "version", "option"

**Hook**:
0-3 giây đầu video, trong đó gap/mystery và narrative promise phải đọc được trong 0-2s: vật thể chưa rõ, danh tính bị giấu hoặc câu hỏi bị né; partial reveal rơi trong 5-8s, không phải 1 câu tuyên bố tĩnh đã đầy đủ nghĩa. HEIT liệt kê 3 type (Context, Contrarian, Intrigue) nhưng khảo sát 6 video viral (2026-07, xem `docs/research/hook-benchmarks-2026-07/REPORT.md`) cho thấy hook hiệu quả thường là hybrid Context→Intrigue, hoặc dạng **Dare/Challenge** (thách đố kết cục nhị phân) chưa khớp type nào trong 3 type gốc. Với Clip Curation Edit, frame t=0 của cut PHẢI chứa mặt người hoặc hành động/prop rõ ràng — không phải title card tĩnh (xem Hook-Window Rule).
_Avoid_: "intro", "opening"

**Hook Caption Sync**:
Caption burned-in phải bắt đầu ngay t=0 (không đợi giây thứ 2-3), sync theo từng cụm từ đang nói, với 1 từ khóa cảm xúc/số liệu nhấn màu khác (thường vàng). Xuất hiện ở 6/6 video trong khảo sát `docs/research/hook-benchmarks-2026-07/REPORT.md` — pattern chưa được ghi nhận trước đó dù universal.
_Avoid_: "subtitle", "text overlay" (quá chung, không nói rõ yêu cầu timing/nhấn từ)

**Caption Style Profile**:
Baseline caption project-wide (ADR-0034): 2-5 từ mỗi burst, một keyword được animate/nhấn, tâm caption mặc định ở 55-65% chiều cao frame và chỉ dịch khi visual review xác nhận đang che mặt/proof object. English dùng Komika Axis; health/Vietnamese dùng Bangers. Kích thước ffmpeg phải được calibration để match ngoại hình CapCut size 16/stroke 60, không copy literal hai số đó sang ffmpeg.
_Avoid_: "renderer default caption", "literal ffmpeg 16/60", "one font without Vietnamese glyphs"

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
Kênh YouTube dùng làm research input, cho MỘT trong 3 niche song song (ADR-0019, ADR-0020): finance viral (VD: School of Hard Knocks, 2.08M subs, tiếng Anh), health/longevity (VD: Bác sĩ Hải, tiếng Việt), hoặc AI education (VD: @mattpocockuk, @anthropic-ai — kênh practitioner/product, không nhất thiết phải "viral how-to" như 2 niche kia). Với 6 animation types (Repackage), chỉ lấy topic/facts/hooks (hoặc style/structure với niche AI education), KHÔNG lấy footage. Với Clip Curation Edit, có lấy footage nhưng vẫn transform (xem Transformative Gate). KHÁC Destination Channel (bên dưới) — Source Channel không phải kênh của user.
_Avoid_: "inspiration", "reference channel"

**Destination Channel**:
Một kênh YouTube CỦA USER nhận Short đã render, thuộc đúng một vertical và là một lane trong Channel Pool của vertical đó. Các kênh hiện có — MONEY BLINDSPOT (finance — `hardknocks`), Giảm Cân Healthy - Thực Chiến (health — `bacsihai`), Working With AI (AI-education — `aiwork`) — là lane đầu tiên của từng Channel Pool, không còn là destination duy nhất. Mỗi Destination Channel cần identity/Analytics scope riêng; `channel==MINE` không resolve đáng tin cậy về đúng channel (xem ADR-0025).
_Avoid_: nhầm với "Source Channel" ở trên — 2 khái niệm hoàn toàn khác nhau

**Channel Pool**:
Ba Destination Channel cùng phục vụ một vertical, mỗi channel được phone-verified, đã age ít nhất ba tuần trước upload đầu tiên và nhận Short theo thứ tự round-robin. Mỗi lane giữ subscriber/history riêng nhưng chia sẻ cùng niche và production system; một Short hoặc revision chỉ được phát hành trên một lane tại một thời điểm.
_Avoid_: "one channel per niche", "random channel", "simultaneous duplicate upload"

**No-Feed State**:
Trạng thái một Short đã qua 48 giờ nhưng traffic từ Shorts Feed vẫn dưới 60%. Không đồng nghĩa với low views hay Distribution Plateau: một Short ít view vẫn không ở No-Feed State nếu phần lớn traffic của nó đến từ Shorts Feed. Khi vào trạng thái này, bản gốc được giữ lại để bảo toàn delayed-pickup/data và một revision được chuyển sang Destination Channel kế tiếp trong Channel Pool.
_Avoid_: "flop", "low-view video", "plateau", "delete and repost"

**Material Revision**:
Phiên bản mới của một Short ở No-Feed State, bắt buộc dựng lại toàn bộ cửa sổ 0–3s (shot/framing, hook copy và early SFX) đồng thời thay ít nhất một trục khác trong pacing/cut order, proof visuals, captions hoặc music. Chỉ đổi metadata, export lại cùng timeline hoặc thay riêng music không đủ để trở thành Material Revision.
_Avoid_: "re-upload", "metadata refresh", "music swap", "duplicate"

**Channel Burn State**:
Trạng thái một Destination Channel có ba Short liên tiếp rơi vào No-Feed State dù từng Short đã pass toàn bộ production/publishing gates. Lane này bị loại khỏi rotation cho tới khi có replacement đã phone-verify và age đủ ba tuần; một Short yếu đơn lẻ không đủ để kết luận channel bị burn.
_Avoid_: "channel feels dead", "one flop means burned", "delete the channel"

**Food-Trial Short (Tòa Án Món Ăn)**:
Narrative format chủ lực của Companion-Meal Short, trình bày một tranh luận dinh dưỡng như phiên tòa: đối tượng được xét xử là một cáo buộc về món ăn, không phải bản thân món ăn; có bằng chứng ủng hộ và phản biện, rồi một phán quyết có hành động cụ thể cho khẩu phần hoặc bữa còn lại. Hài hước là lớp truyền tải; phán quyết phải dựa trên các giả định khẩu phần được công khai và không được biến thực phẩm thành nhãn đạo đức “tốt/xấu”.
_Avoid_: "food roast", "món độc hại", "guilty food", "nutrition lecture"

**Living-Comic Treatment**:
Treatment hình ảnh toàn thời lượng của Food-Trial Short: toàn bộ khung hình được tổ chức như các trang và panel truyện tranh, nhưng panel chính chứa footage nấu ăn thật đang chuyển động. Ảnh tĩnh chỉ được dùng như nhịp vật chứng hoặc reaction ngắn; đây không phải slideshow ảnh có pan/zoom và cũng không phải footage toàn màn hình chỉ gắn vài speech bubble.
_Avoid_: "static comic", "comic overlay only", "Ken Burns slideshow", "raw-footage layout"

**Lobby Acquittal Twist**:
Biến cố kết thúc không báo trước trong một số Food-Trial Short đủ điều kiện: sau khi vật chứng đã cho thấy cáo buộc có cơ sở và Companion-Meal Verdict đúng đã được trình bày, quan tòa hư cấu vẫn tuyên tha vì nhận lobby từ một tổ chức thực phẩm hoàn toàn hư cấu. Tập đủ điều kiện được chọn bằng random có kiểm soát để viewer không dự đoán được nhưng tránh lặp twist liên tiếp. Lobby nên là một Earned Evidence Callback gắn với nguyên liệu hoặc phe đã xuất hiện trong hồ sơ; twist không được thay thế hoặc đảo ngược thông tin dinh dưỡng đúng.
_Avoid_: "default ending", "random envelope", "real-brand bribery", "source-creator corruption", "misleading acquittal"

**Verdict-Pendulum Narrative**:
Trải nghiệm retention của Food-Trial Short trong đó viewer hình thành một phán đoán ban đầu, rồi Counter-Evidence Ladder làm kết luận tạm thời nghiêng qua lại trước verdict cuối. Pendulum mô tả trải nghiệm của viewer, không phải cấu trúc script: script không luân phiên các fact độc lập mà buộc mỗi checkpoint phải phản đòn, thêm ngoại lệ hoặc làm thay đổi ý nghĩa của vật chứng ngay trước đó. Verdict cân trọng số và ngữ cảnh của toàn bộ Recipe Case, không đếm số card hoặc cố tạo thế cân bằng giả.
_Avoid_: "alternating fact cards", "evidence dump", "forced both-sides balance", "trivia reversal", "most cards wins"

**Counter-Evidence Ladder**:
Narrative engine mặc định cho prototype Food-Trial Short đầu tiên: mỗi vật chứng mới phải trực tiếp phản bác hệ quả trước, bổ sung ngữ cảnh làm đổi ý nghĩa, đưa ra ngoại lệ hợp lệ, bóc một giả định ẩn hoặc biến vật chứng cũ thành proof quyết định. Các lượt leo thang cho tới khi một bên không còn counter đủ liên quan và tòa có thể trả lời đúng cáo buộc ban đầu; fact đúng nhưng không thay đổi vụ án bị loại khỏi video. Đây là production hypothesis được chấp nhận từ cross-video analysis Law By Mike, chưa phải causal winner đã được xác nhận.
_Avoid_: "nutrition checklist", "independent evidence ping-pong", "equal turns per side", "more facts means stronger case"

**Earned Evidence Callback**:
Payoff cuối tái sử dụng một nguyên liệu, giả định, quy tắc, phe hoặc vật chứng đã được gieo trước đó để tạo proof, character joke hoặc Lobby Acquittal Twist. Callback phải tái diễn giải hồ sơ vừa xem thay vì gắn một punchline ngẫu nhiên vào cuối; đây là pattern ưu tiên chứ không phải yêu cầu mọi tập phải có joke.
_Avoid_: "random punchline", "unseeded lobby", "unrelated CTA gag", "new evidence after verdict"

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

**Mid-Roll Triple CTA**:
CTA bắt đầu trong cửa sổ t=38–42s và yêu cầu rõ cả ba hành động Like, Subscribe và Comment. Đây là beat bắt buộc bên trong Short, không phải end card chỉ xuất hiện sau payoff; wording vẫn phải gắn với nội dung cụ thể của Short thay vì dùng một câu generic có thể dán vào mọi video.
_Avoid_: "end CTA", "like-and-subscribe only", "generic engagement line"

**Clip Curation Edit**:
Video Type #7. Download footage từ Source Channel + cut + transform (commentary + value-adds). Khác Repackage (zero-footage animation gốc).
_Avoid_: "remix", "edit", "cut" (use specific term)

**Transformative Edit**:
Synonym cho Clip Curation Edit — editing approach (cut + commentary + value-adds) đủ khác để qualify Fair Use.
_Avoid_: "highlight edit", "re-edit"

**Transformative Gate**:
3 pipeline rules ALL required trước khi upload Clip Curation Edit: (1) commentary track, (2) min 2 value-adds, (3) cut ≤50% source + mỗi clip <15s. Auto-checkable.
_Avoid_: "Fair Use check"

**Original-Voice Editorial Commentary**:
Commentary track của Clip Curation Edit được tạo bằng cách chọn, sắp xếp lại và juxtapose lời nói gốc thành một thesis mới, không thêm synthetic narration/TTS. Vẫn phải qua đủ Transformative Gate; không đồng nghĩa với đăng raw clip. Một revision bỏ TTS chỉ kiểm tra treatment mới khi các biến khác được giữ ổn định, và không chứng minh TTS là nguyên nhân nếu bản trước chưa có exposure.
_Avoid_: "no-commentary edit", "raw interview cut", "TTS-free means untransformed"

**Synthetic Narration**:
Spoken audio được tạo bằng TTS, với phạm vi phụ thuộc Video Type thay vì áp dụng một treatment cố định cho mọi Short. Synthetic Narration có thể đọc toàn bộ Short khi visual cần một narrator độc lập, hoặc chỉ đảm nhiệm Hook, CTA và Editorial Bridge ngắn khi source voice vẫn là giọng chính. Không đồng nghĩa với Commentary Track: commentary cũng có thể được thể hiện bằng Original-Voice Editorial Commentary hoặc text overlay.
_Avoid_: "AI voice" (quá chung), "voiceover" (không phân biệt synthetic với source voice), "TTS-only format"

**Narrator Voice Profile**:
Voice identity ổn định của Synthetic Narration, được gán cho đúng một Destination Channel và được khóa bằng description/config cùng Canonical Narrator Voice Artifact khi engine dùng designed voice. Finance và AI-education có Narrator Voice Profile riêng phù hợp brand tone; không tự đổi voice theo từng Short hoặc Video Type. Voice chỉ được thay đổi khi chính voice là AB Variable của một Experiment đã khai báo, để tránh tạo biến nhiễu khi đánh giá các variant khác.
_Avoid_: "random voice", "voice per video", "global narrator" (gộp nhiều Destination Channel)

**Authorized Voice Source**:
Nguồn voice hợp lệ để tạo Narrator Voice Profile: stock voice được phân phối hợp pháp cùng TTS model; artifact hoàn toàn synthetic do model có license phù hợp tạo từ text description; hoặc giọng của chính chủ/narrator có consent và license rõ ràng cho voice cloning. Không dùng giọng clone của người nổi tiếng, speaker trong Source Channel hoặc bất kỳ người nào chưa cấp quyền. Audio demo công khai chỉ là listening evidence, không tự trở thành Authorized Voice Source để conditioning hay đóng gói lại.
_Avoid_: "celebrity voice", "source-speaker clone", "public voice means free to clone"

**Canonical Narrator Voice Artifact**:
Audio reference duy nhất, được version và hash, dùng để khóa identity của một designed Narrator Voice Profile khi sinh lời thoại mới. Đây là domain asset không thể thay bằng audition/output tạm: regenerate từ cùng description vẫn có thể drift khi model/runtime thay đổi. Raw generation, normalized copy, audition, repeatability run và upstream demo đều không phải Canonical Narrator Voice Artifact.
_Avoid_: "sample WAV", "audition winner file", "regenerate later is identical"

**Narrator Runtime Adapter**:
Cơ chế kỹ thuật gọi TTS engine để hiện thực hóa một Narrator Voice Profile trong renderer. Voice Selection và Runtime Activation là hai quyết định khác nhau: adapter tạm có thể tiếp tục chạy trong khi canonical profile đã được chọn, nhưng không được hiểu adapter tạm là voice preference hoặc production identity.
_Avoid_: "selected voice means already integrated", "current adapter is the canonical voice"

**TTS Selection Gate** (ADR-0032):
Một English open-source engine/voice chỉ trở thành production default sau khi code, weights và exact voice đều qua commercial-use gate, chạy được trên Apple Silicon 16 GB không cần paid API, và được người dùng trực tiếp đánh giá ngang hoặc tốt hơn Edge baseline trên cùng audition corpus. Automated QC chỉ loại artifact invalid/silent/truncated hoặc cảnh báo pronunciation; AI/metric không chọn winner. Nếu không local candidate nào đạt listening bar, tiếp tục dùng `edge-tts`; chỉ benchmark Python API so với batch CLI trên open-source winner đã được chọn.
_Avoid_: "open source means automatic default", "AI-scored voice winner", "integration-first bake-off"

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
1 trong 10 information overlays: (hiện có) fact_check_callout, data_viz_overlay, counter_argument, source_citation, animated_annotation, multi_source_mashup + (mới) this_or_that_overlay, split_screen_comparison, timeline_overlay, circular_spotlight_reveal. multi_source_mashup = clip-only (cần footage). Max 8 apply cho animation.
_Avoid_: "annotation", "widget"

**Retention Techniques**:
Base quality layer áp dụng TỰ ĐỘNG cho mọi video, KHÔNG phải AB variable: sound design (whoosh/riser/impact), zoom punch, pattern interrupt (visual change mỗi 2-4s), cut rhythm. Thiếu = kém chất lượng, không công bằng khi test.
_Avoid_: "effects", "polish"

**Active-Speaker Reframing**:
Quy tắc dựng phỏng vấn 1-1 trong khung dọc: portrait crop chuyển trọng tâm sang người đang phát ra câu thoại — host khi hỏi, guest khi trả lời — thay vì giữ một center crop cố định cho cả cuộc trao đổi. Có thể là đổi camera thật hoặc digital reframe từ two-shot ngang; điều kiện cốt lõi là lượt thoại và visual focus phải đồng bộ.
_Avoid_: "center crop", "random angle switch", "speaker tracking" (dễ hiểu nhầm là bám mặt liên tục trong cùng một lượt thoại)

**Semantic Zoom**:
Quy tắc đổi magnification theo chức năng của beat, không theo timer: dùng medium crop ở setup, câu hỏi mới, đoạn giải thích dài hoặc khi gesture cần ngữ cảnh; punch-in close-up ở con số, confession, mệnh lệnh hoặc punchline; reset về medium ở topic/question kế tiếp. Trong một lượt trả lời, mặc định tối đa một lần punch-in để tránh zoom pumping.
_Avoid_: "cadence zoom", "constant push-in", "random punch zoom", "zoom every 2 seconds"

**Proof-Coupled B-Roll**:
Footage minh họa xuất hiện cùng beat với claim mà nó chứng minh hoặc làm rõ, thay vì chèn chỉ để tạo chuyển động. Với Clip Curation Edit dạng phỏng vấn, budget mục tiêu là 25–35% timeline; trong 0–10s chỉ dùng partial/corner insert để mặt người nói vẫn hiện diện, sau đó mới cho phép full-screen proof khi cần. Thứ tự ưu tiên nguồn: footage thật gắn trực tiếp với subject/object/platform đang được nhắc tới → stock footage cho ý trừu tượng hoặc khi không có evidence footage phù hợp.
_Avoid_: "decorative b-roll", "random stock footage", "visual variety" (nếu footage không gắn với claim cụ thể)

**Business Lesson Payoff**:
Beat tổng hợp biến câu chuyện và evidence thành đúng một nguyên lý kinh doanh có thể hành động, nêu rõ cơ chế tạo kết quả và được neo bằng lời nói/hành động thật trong source. Không phải motivational quote chung chung hoặc narrator tự suy diễn. Trong Blindspot Verification, Business Lesson Payoff phải làm video có giá trị ngay cả khi viewer không quan tâm nhân vật được check đúng hay sai.
_Avoid_: "generic takeaway", "moral of the story", "inspirational quote", "lesson card" (nếu chỉ là một câu slogan không có cơ chế/evidence)

**this_or_that_overlay**:
Value-Add Type mới. Binary choice overlay "A vs B" (VD: "Rent vs Buy", "Index vs Stock pick"). Phù hợp niche finance, MONEY+TIMEFRAME hook pattern.
_Avoid_: "comparison widget"

**split_screen_comparison**:
Value-Add Type mới. 2 panels side-by-side so sánh (VD: "5AM vs 8AM"). Dùng cho comparison hooks.
_Avoid_: "dual screen"

**timeline_overlay**:
Value-Add Type mới. Timeline/milestone bar (VD: "Day 1 → Day 30 → $1M"). Phù hợp "He made $X in Y time" hooks.
_Avoid_: "progress bar" (đã có trong render), "timeline video"

**circular_spotlight_reveal**:
Value-Add Type mới (1 mẫu, xem `docs/research/normal-vs-king-pattern-2026-07-12/REPORT.md`). Vòng tròn (khung hình elevated/aerial quay 1 set piece tròn thật, hoặc vignette/glow ring dựng bằng animation) bao quanh chủ thể payoff trong lúc camera dwell — tách biệt hẳn khỏi khung hình hỗn loạn/hand-held của đoạn setup. Khác `animated_annotation` (đó là annotation vẽ thêm lên nội dung có sẵn) — đây là 1 lựa chọn staging/framing riêng cho khoảnh khắc payoff. Chưa confirm cross-video (mới 1 mẫu).
_Avoid_: "vignette" (quá chung), "spotlight effect"

**subject_tag_callout**:
Value-Add Type mới (1 mẫu, xem `docs/research/ronaldo-security-guard-kindness-2026-07-13/REPORT.md`). Name-tag + mũi tên gắn lên 1 nhân vật ngay khi họ xuất hiện trong khung hình, TRƯỚC KHI vai trò/sự liên quan của họ được giải thích — tạo gap thị giác (viewer thắc mắc "sao lại tag người này?") thay vì gap bằng lời thoại/câu hỏi. Khác `animated_annotation` (chú thích thêm cho nội dung đã rõ nghĩa, không tạo gap) — đây là công cụ TẠO gap thị giác, dùng ở đầu Hook. Chưa confirm cross-video.
_Avoid_: "label overlay", "name tag" (quá chung, thiếu vai trò tạo-gap)

**Autonomous Optimization System**:
Hệ thống tự động evaluate eligibility của lane kế tiếp trong Channel Pool, publish theo Plateau-Gated Cadence, chờ metrics, rồi để MAB điều chỉnh strategy. Không có fixed daily upload quota; scheduler phải dừng nếu lane kế tiếp chưa đủ điều kiện.
_Avoid_: "AI optimizer", "auto-improve"

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

**Distribution Plateau**:
Trạng thái một Short đã qua ít nhất 48 giờ và tốc độ tăng view trong cửa sổ 24 giờ gần nhất chỉ còn tối đa 20% so với cửa sổ 24 giờ liền trước, được xác nhận ở hai lần kiểm tra liên tiếp. Đây là tín hiệu momentum phân phối đã suy giảm đủ để mở gate đăng Short kế tiếp trên cùng Destination Channel; một video vẫn giữ tốc độ view/ngày cao và ổn định không phải Distribution Plateau dù tỷ lệ view mới trên tổng view nhỏ.
_Avoid_: "48h elapsed", "low total views", "the graph looks flat", "fixed seven-day wait"

**Plateau-Gated Cadence**:
Chính sách mỗi Destination Channel chỉ phát hành Short tiếp theo sau khi Short trước đạt Distribution Plateau, không theo lịch daily/weekly cố định. Cadence được đánh giá độc lập theo từng Destination Channel để momentum của một vertical không chặn hai vertical còn lại.
_Avoid_: "post daily", "one Short per week", "global queue"

**Metrics Status**:
Chuỗi literal trong production doc's Status table (`Metrics status` field) mà `/fetch-metrics` skill dùng để tự quét: `"Not yet fetched..."` (match substring, prose có thể khác nhau) = còn due để fetch; `"Fetched YYYY-MM-DD"` (chính xác, không thêm prose) = đã fetch xong, loại khỏi batch scan sau này.
_Avoid_: viết prose tự do vào field này sau khi đã fetch — phải đúng literal `Fetched YYYY-MM-DD` để scanner nhận diện được

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
Tính mean AVD và các metrics đã khai báo của toàn bộ Shorts trong Target Cohort sau khi đạt stopping rule. So sánh với Target threshold và trigger Success Formula Step 9 loop (success → raise target / failure → auto-crawl).
_Avoid_: "cohort review", "post-mortem"

**Source Channel Pattern**:
Format hook được trích xuất từ phân tích top videos của kênh viral reference (vd: @theschoolofhardknocks — 31M views/top short). 3 pattern types đã identify: (1) Money+Number ($58,380, $2.5M car), (2) Curiosity Gap ("THIS is the real secret"), (3) Contrarian Reveal ("Good culture isn't made in the game"). Khác AB Variable (đơn lẻ) — Source Channel Pattern là combo hook+structure hoàn chỉnh copy từ proven viral. [NOTE: 1 pattern thứ 4 (Implied Comparison, xem bên dưới) được tìm thấy ở kênh RandomDude, nay đã confirm qua 2 video (808M + 418M views, xem `docs/research/800m-view-case-study-2026-07-11/REPORT.md` và `docs/research/normal-vs-king-pattern-2026-07-12/REPORT.md`).]
_Avoid_: "hook template", "title formula"

**Live-Approach Hook**:
Source Channel Pattern của School of Hard Knocks: một cảnh handheld liên tục bám sau host đang tiến tới người lạ, với người và tài sản địa vị cùng hiện diện ngay frame 0; lời mở “Excuse me sir…” dẫn sang câu hỏi xác minh tài sản rồi câu hỏi tiền bạc chưa được giải đáp. Hook giữ nguyên encounter tự nhiên qua first reveal trước khi commentary mới bắt đầu, thay vì dùng title card hoặc narration mở màn.
Đây là production hypothesis từ winner-only sample, không phải causal default. Hai Shorts khác story chỉ là comparison; controlled hook test phải giữ nguyên story và chỉ đổi opening treatment (ADR-0031).
_Avoid_: "street interview intro", "cold open", "walk-up shot"

**Implied Comparison Hook**:
Pattern hook thứ 4, **confirmed 2/2 video cùng kênh RandomDude** (`docs/research/800m-view-case-study-2026-07-11/REPORT.md` — shooting, 808M views; `docs/research/normal-vs-king-pattern-2026-07-12/REPORT.md` — firefighters, 418M views), khác 3 Source Channel Pattern gốc. Không có 1 dòng hook nào tự giải thích gap — caption chỉ label 1 phía ("OTHERS X") và chính TITLE/thể loại video ngầm hứa hẹn phía còn lại ("...VS King of X") sẽ xuất hiện sau. Cho phép gap dài bất thường (~40-41s ở cả 2 video, so với 5-8s target hiện có của HEIT) MIỄN LÀ đoạn chờ được lấp bằng 1 montage đủ đa dạng/giải trí để tự nó giữ chân người xem — gap không được resolve bởi câu chữ mà bởi kỳ vọng thể loại. Payoff/reveal luôn được camera "dwell" lâu hơn hẳn (~3x ở video 1, ~17.3s/29% tổng video ở video 2) so với các clip dựng cảnh (setup) trước đó. Caption template (trắng/vàng "OTHERS X" → đỏ-glow pivot) và sticker capstone (skull+cowboy hat) giống hệt ở cả 2 video — đây là brand signature của kênh, không phải lựa chọn ngẫu nhiên mỗi video. [Lưu ý: động lực tâm lý comment KHÔNG cố định — video 1 (others thực sự kém) khiến khán giả chê "others"; video 2 (others cũng là chuyên gia thật) khiến khán giả quay sang chê "the editor" vì so sánh không công bằng. Chọn source material có cân nhắc bên nào sẽ bị/được đùa cợt.]
_Avoid_: "comparison hook" (thiếu phần "không resolve bằng câu chữ"), "vs hook"

**Narrative Arc**:
Cấu trúc kể chuyện 5 nhịp: Setup (thiết lập bối cảnh) → Inciting Incident (sự cố xảy ra) → Rising Tension (căng thẳng/gap chưa giải quyết) → Resolution (nhân vật xử lý, căng thẳng hạ) → Reward (phần thưởng/twist bất ngờ nâng tầm nhân vật). Khác HEIT (cấu trúc giáo dục hook/explain/illustrate/teach) và khác Source Channel Pattern (hook đơn lẻ, không phải cả mạch truyện). **Confirmed 2/2 video, 2 kênh/2 thể loại khác nhau**: Migd5sn-0uc (Ronaldo đỡ nhân viên an ninh bị bóng trúng đầu, 147M views, real sports incident — xem `docs/research/ronaldo-security-guard-kindness-2026-07-13/REPORT.md`) và i_elsC4Kg8c (Sunnah Edit, "Hard Work Always Pays Off", 249M views, staged reward vignette — xem `docs/research/hard-work-pays-off-2026-07-13/REPORT.md`). Video thứ 2 dựng cả 5 nhịp rõ hơn hẳn (bao gồm 1 đoạn hỏi-đáp thật qua caption ở Rising Tension: "FOR HOW LONG?" → "3 YEARS") và không cần thoại/giọng nói — 100% dẫn chuyện bằng caption trên nhạc nền. Phù hợp nhất với nội dung dựng từ 1 sự kiện/case thật (vd Clip Curation Edit từ case bệnh nhân thật), không áp dụng cho nội dung giáo dục/liệt kê thuần túy. [Lưu ý: retention mechanism này khác hẳn hook-line-first — gap chính nằm ở toàn mạch truyện (điều gì sẽ xảy ra với người này?), không phải ở 1 câu hook 0-2s.]
_Avoid_: "story structure", "plot" (quá chung)

**Decision-Lock Narrative**:
Retention engine yêu cầu viewer chốt một phán đoán nhị phân trước khi biết đủ dữ kiện, rồi mở khóa evidence theo từng checkpoint để họ tự kiểm tra quyết định ban đầu. Khác `this_or_that_overlay` (một Value-Add Type đơn lẻ) và Proof-First Narrative (viewer quan sát bằng chứng nhưng không bắt buộc tự cam kết một đáp án); open loop chính là “mình đoán đúng hay sai?”. Xem ADR-0028.
_Avoid_: "quiz", "poll", "this-or-that video", "choose-your-own-adventure"

**Delayed Platform-Fit Narrative**:
Retention engine kể một năng lực bị xem nhẹ hoặc chưa tạo kết quả trong thời gian dài, rồi payoff bằng khoảnh khắc một nền tảng/cơ hội mới khớp với năng lực đã tích lũy. Evidence ladder bắt buộc phân biệt rõ thời gian luyện tập trước đó, trigger tạo platform fit, và kết quả kinh tế sau đó; không kể thành công như một cú may mắn qua đêm. Khác “overnight success” (bỏ qua accumulated skill) và khác founder origin story chung chung (không có platform-fit trigger cụ thể).
_Avoid_: "overnight success", "lucky break", "10,000-hours story" (chỉ mô tả thời gian, thiếu platform-fit payoff)

**Proof-First Narrative**:
Retention engine cho finance Short trong đó người xem chứng kiến một sự kiện tiền bạc thật, lựa chọn có stakes và hậu quả nhìn thấy được; lời giải thích chỉ bổ trợ, không thay thế bằng chứng hình ảnh. Khác Interview Wisdom ở chỗ giá trị đến từ diễn biến được quan sát trực tiếp, không phải lời kể hồi tưởng hay claim thành công.
_Avoid_: "success story", "testimonial", "interview wisdom"

**Impossible Trade Ladder**:
Một subtype của Proof-First Narrative: bắt đầu bằng vật thể giá trị rất thấp rồi cho người xem chứng kiến chuỗi trao đổi liên tiếp dẫn tới tài sản tưởng như không thể đạt được. Gap cốt lõi là liệu giao dịch kế tiếp có xảy ra và vật cuối cùng sẽ lớn tới đâu, không phải một lời khuyên làm giàu.
_Avoid_: "flipping story", "barter challenge", "rags to riches"

**Worst-Trade Reversal**:
Góc kể của Impossible Trade Ladder trong đó một giao dịch bị một nhóm khán giả được ghi nhận xem là thua cuộc sau đó trở thành cầu nối quyết định tới payoff, vì một counterparty cụ thể định giá món đồ khác thị trường chung. Hook phải gán phản ứng cho đúng nhóm có bằng chứng (VD: "her followers"), không được nâng "many followers" thành "everyone". Khác Contrarian Reveal ở chỗ cú lật được chứng minh bằng chuỗi giao dịch nhìn thấy được, không chỉ bằng một claim đối lập. Xem ADR-0027.
_Avoid_: "bad trade", "lucky trade", "contrarian story"

**Counterparty Value**:
Giá trị sử dụng mà một người mua/đối tác cụ thể gán cho tài sản, có thể cao hơn đáng kể so với định giá phổ biến hoặc sticker price vì nhu cầu, danh tính hoặc utility riêng của họ. Trong Worst-Trade Reversal, payoff không đến từ việc món đồ tự nhiên tăng giá mà từ việc tìm đúng counterparty có willingness-to-trade khác số đông. Khác market value (giá thị trường điển hình) và khác may mắn thuần túy vì việc tìm counterparty là hành động chiến lược. Xem ADR-0027.
_Avoid_: "true value", "intrinsic value", "lucky buyer"

**Source-Grounded Hook Claim**:
Một claim trong hook có mức độ khái quát không vượt quá bằng chứng trực tiếp. Nếu nguồn chỉ nói "many followers", hook phải giữ chủ thể "followers" hoặc "many followers"; không đổi thành "everyone", "the internet" hay gán quan điểm đó cho nhân vật. Đây là quality gate cho Proof-First Narrative: open loop có thể mạnh, nhưng attribution phải đúng. Xem ADR-0027.
_Avoid_: "clickbait license", "close enough", "universalized claim"

**Verbatim Segment**:
Đoạn audio gốc từ source video (Andy Frisella etc.) được extract nguyên bản, không TTS override. Là cốt lõi của Mode A. TTS chỉ dùng cho hook và CTA — phần giá trị giữa luôn là giọng thật. Xác nhận perform tốt hơn pure TTS (19.5% AVD cho pure TTS vs winner Mode A).
_Avoid_: "source clip", "raw audio", "original quote"

**Mode A**:
Render format: TTS Hook → Verbatim Segments (×4) → TTS CTA → Optional padding. Chỉ giữ 1 mode — Mode B (hybrid TTS+source quote) đã bị loại sau khi test. Audio: hook 5-7s + segments 16-20s + CTA 9-11s = 33-39s total. Khác Mode B đã deprecated.
_Avoid_: "verbatim mode", "source audio mode", "Mode B"

## Project Name

Package name (from package.json khi init): `shorts`
Wiki slug: `shorts`
