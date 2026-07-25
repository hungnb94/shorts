# Flow Chuẩn — Cắt/Sản Xuất Video

Living document. File này tiến hóa qua thực tế sử dụng: mỗi lần sản xuất kết thúc bằng **Post-Production Retro** (Stage 5), xác nhận flow này vẫn đủ hoặc sửa file này *trước khi* video được coi là xong. Không được bỏ qua bước check này.

Doc này sắp xếp thứ tự pipeline và định nghĩa các gate cứng. Không lặp lại nội dung rule đã có trong ADR hay `AGENTS.md` — chỉ cite theo số/tên để tránh lệch pha khi ADR thay đổi.

## Stage 0 — 0–3s HOOK GATE (chặn cứng)

Chạy bước này trên MỌI candidate segment trước khi cắt, render, hoặc làm overlay. Không bước nào dưới đây được bắt đầu trước khi có 1 candidate pass.

```
1. Frame-0 face/action check (ADR-0017): tại t=0 candidate phải có mặt người
   hoặc hành động/prop rõ ràng — không phải title card, static text, hay B-roll.
   Check bằng mắt (visual inspection thủ công), không dùng script. Nếu nguồn có
   cả 2 lựa chọn, ưu tiên shot cận/tight (mặt chiếm phần lớn khung hình) hơn
   wide/establishing shot — mặt lớn hơn, rõ hơn, "đọc" nhanh hơn là có người
   đang nói chuyện với mình (aiwork v2: tight portrait mở đầu > v1's wide stage
   shot cho cùng Hook Gate item 1).
2. Gap-not-resolved check (CONTEXT.md → Hook): hook line dự kiến, đọc riêng,
   KHÔNG được nói hết toàn bộ claim — phải mở 1 gap/mystery ở 0-2s, chỉ
   partial reveal ở 5-8s.
3. Cause+effect co-naming check (AGENTS.md pitfall): headline không được nêu cả nguyên nhân VÀ hệ quả cụ thể cùng lúc.
4. Cadence feasibility (ADR-0018/0036): trong final 0-5s phải có phương án đạt
   target 1 Visual Change mỗi 0.8-1.5s; final 5-10s không có gap không giải thích
   >3s. Cut, reframe/zoom, overlay, đổi layout/source hoặc motion liên tục đều
   được tính; không ép hard cut làm hỏng câu thoại.
5. Guide-derived promise check (ADR-0034): trong 0-3s phải có cả visual surprise
   lẫn narrative promise rõ ràng; early SFX phải có slot trong t=0-1s và focal
   target phải đọc được ngay hoặc có thể chỉ bằng arrow/pointer/annotation.
6. Naive-viewer check: cho một người không tham gia edit xem rough hook 0-3s mà
   không giải thích trước; họ phải nói được open question/promise khiến họ muốn
   xem tiếp. Nếu chỉ hiểu sau khi creator giải thích, hook fail. Production doc
   phải lưu ngày check, rough-hook version và câu trả lời nguyên văn đã ẩn danh;
   creator/agent tự xem không được tính là naive viewer. Không có evidence này
   thì item 6 là `unverified` và Hook Gate vẫn block render/upload — không được
   tự suy ra pass từ frame-check, caption timing hay cadence.
7. Information Progression feasibility (ADR-0036): chuỗi Visual Changes dự kiến
   phải đẩy ít nhất một question, causal step, contrast, proof state hoặc payoff;
   không được dùng toàn flash/emoji/zoom trang trí chỉ để đủ cadence.
```

**GATE RULE**: nếu bất kỳ item 1-7 trên MỌI candidate span trong source hiện tại, và không thể fix bằng cách chọn span khác trong cùng bản download, thì STOP. Quay lại Stage 1 — chọn span khác hoặc source video khác. Không được tiến sang Stage 2/3/4, và không được ship 1 hook đã biết là yếu với lý do "để retention data trả lời sau."

## Stage 1 — Source Research & Candidate Selection

- Chọn Source Channel theo từng niche (ADR-0001/0004 finance, ADR-0019 health/VN, ADR-0020 AI-ed).
- Reverse-engineer outlier channels trước khi chốt treatment: copy narrative mechanics, pacing, hook/payoff và packaging đã chứng minh được demand; không copy topic execution, wording hay footage cụ thể của họ (ADR-0034).
- Check `data/source_videos.csv` (source-video dedup registry) theo video ID/kênh trước khi chọn — tránh chọn lại đúng video hoặc lặp kịch bản đã dùng.
- Download max quality: `yt-dlp -f "bestvideo[height>=2160]+bestaudio"` (không bao giờ nhận default 720p — AGENTS.md).
- Transcribe (mlx_whisper).
- **Với nguồn dạng conference/talk dài (nhiều chục phút), trích 1 frame kiểm tra nhanh cho MỖI candidate window đã chọn từ transcript — không chỉ window của HOOK — trước khi chốt kế hoạch cắt**
- **Với nguồn rất dài (~1 giờ trở lên), đừng đọc/xem tuyến tính toàn bộ transcript để tìm candidate — keyword-scan trước.** Quét toàn bộ transcript bằng các từ khóa liên quan tới insight tổng quát hóa được (ví dụ: "question", "clarify", "the reason", "the point", "why", "important because") để khoanh vùng ứng viên, sau đó mới đọc kỹ + frame-check từng vùng đã khoanh (Stage 0 item 1, và note ở trên). Đọc tuyến tính không khả thi ở độ dài này (aiwork_v6: nguồn 4480s/74.6 phút, 599 segments — quét từ khóa tìm ra đúng 1 câu tổng quát hóa được, nằm ở phút 53:41 của một buổi livestream lập trình gần như toàn bộ là screen-share/jargon).
- Sau khi chốt source video dùng cho video mới, append 1 dòng vào `data/source_videos.csv`.

## Stage 2 — Cut Segment

- Extract candidate đã pass Stage 0. Chọn 1 trong 2 sub-format của Clip Curation Edit (ADR-0022):
  - **Multi-Clip Mashup** (ADR-0022, duration superseded by ADR-0034): nhiều đoạn rời rạc (mỗi đoạn <15s theo ADR-0007 item 3), nối bằng ffmpeg concat demuxer — dùng khi các moment mạnh nhất nằm rải rác quá xa nhau để gom vào 1 cửa sổ 50-75s duy nhất. Vẫn phải đạt tổng 50-75s sau khi ghép; audio joins vẫn phải pass Stage 4 fade/clarity gate.
- Production doc phải nêu rõ đang dùng sub-format nào (ADR-0022) trong phần "Why This Segment".

## Stage 3 — Hook Text + Overlays

- Viết hook overlay/caption/value-add. Phải thỏa ADR-0018 (caption sync), ADR-0036 (tiered cadence + Information Progression), ADR-0008 (Value-Add Layer).
- Nếu là Clip Curation Edit: phải thỏa thêm Transformative Gate của ADR-0007 (commentary track + ≥2 value-add + ≤50% source duration / mỗi clip <15s).
- Apply ADR-0034's `Caption Style Profile`: 2-5 từ/burst, một keyword animate/emphasize, tâm caption mặc định ở 55-65% chiều cao frame; chỉ dịch để tránh che face/proof sau visual review. English dùng Komika Axis, Vietnamese dùng Bangers; lấy thông số ffmpeg từ calibration artifact đã verify, không copy literal CapCut size 16/stroke 60.
- Thêm một early SFX trong t=0-1s. Nếu focal target không rõ ngay, thêm arrow/pointer/animated annotation; không thêm pointer trang trí khi target đã hiển nhiên.
- Mọi image entrance/exit hoặc transition đã chọn phải có mục đích kể chuyện và matching SFX; generic transition spam fail gate.
- Bind SFX vào visible/implied event cụ thể; constant effect bed không đạt ADR-0036. Narrative Short có Problem → Discovery → Payoff phải dùng các score state khác nhau và một music attenuation ngắn trước discovery/payoff quyết định; educational Short dùng section-level audio contrast, không bị ép vào arc ba trạng thái.
- Stock/Pexels phải ghi `ILLUSTRATION` khi reasonable viewer có thể nhầm đó là footage thật của người, sự kiện, sản phẩm hoặc evidence đang được claim. Generic b-roll hiển nhiên không bắt buộc label nhưng không được gọi là proof.
- Dựng custom on-brand CTA bumper bắt đầu trong t=38-42s, lời CTA nói rõ cả Like + Subscribe + Comment. Generic stock CTA template fail.
- Thêm moving watermark không che face/proof/caption và thay đổi vị trí theo timeline để chống crop đơn giản.
- **Hook text overlay tự thêm (không phải caption gốc của nguồn) phải xuất hiện gần như ngay lập tức (~t=0.1-0.2s, không trễ hơn) và cỡ chữ đủ lớn/màu đủ nổi bật để giữ chân người xem ngay từ đầu** (user feedback, hardknocks_v2: bản render đầu tiên delay hook overlay tới t=1.3s với size=36 để tạo cadence beat - quá nhỏ, quá trễ. Cadence (item 4, Stage 0) nên đạt bằng zoompan/motion liên tục hoặc cắt cảnh, KHÔNG phải bằng cách trì hoãn hook text). Tham khảo size ~48-52px ở khung 1080px-rộng là **mốc tối thiểu (floor), không phải mục tiêu (target)** cho hook text chính - hardknocks_v2 nhận feedback tăng size 4 lần liên tiếp trên cùng 1 video (36→52→64→80→84), ưu tiên to hơn khi khung hình còn chỗ, áp dụng cho cả text phụ (stat card/counter-argument/CTA), không chỉ hook chính.
- **Nếu tăng size sẽ khiến chữ bị crop ở mép 1080px, rút ngắn nội dung chữ trước, không coi size hiện tại là trần cố định** (hardknocks_v2: câu hook dài "OTHERS SAY MONEY = HAPPY..." đã chạy sát mép ở size=64, không thể tăng thêm nếu giữ nguyên độ dài - phải rút ngắn còn "OTHERS: MONEY = HAPPY" mới tăng lên size=80 được).
- **Mỗi lần tăng size phải tự verify lại bằng frame extraction thực tế, không được suy ra an toàn từ margin của lần tăng trước** (hardknocks_v2 vòng 4: rút ngắn chữ thêm + tăng size 80→90 trong 1 bước tưởng là an toàn theo ước tính số ký tự, nhưng frame check phát hiện chữ bị crop cả 2 mép - phải lùi về size=84 mới đạt). Rút ngắn chữ + tăng size cùng lúc có thể cộng dồn vượt ngưỡng dù mỗi thay đổi riêng lẻ trông hợp lý - luôn re-verify bằng Stage 4 self-check sau MỖI lần đổi size, không chỉ lần đầu tiên đổi.
- **Đo pixel width thực tế trước khi render, không chỉ sau khi render** (bacsihai_v7): trước khi commit 1 size vào render script cho BẤT KỲ drawtext overlay nào (hook text chính, stat card, header, CTA), đo thử bằng `PIL.ImageFont.getlength(text)` với đúng font file/size sẽ dùng, so với chiều rộng khung hình (1080px) trừ margin mong muốn. bacsihai_v7's header overlay ("NHIỀU NGƯỜI NGHĨ: CHOLESTEROL = XẤU" @ size 64) bị tràn khung ở lần render đầu - bắt được qua Stage 4 frame check (đúng như quy trình), nhưng đo trước bằng PIL sẽ bắt được ngay từ đầu, biến việc sửa thành 1 vòng thay vì nhiều vòng thử-sai như hardknocks_v2's 4 rounds. Bước đo pixel không thay thế frame-check bắt buộc sau khi render (vẫn phải làm), chỉ giảm số vòng lặp cần thiết.

## Stage 4 — Render & Spec Verify

- Chạy `pipeline/<project>/render_*.py`.
- Verify 9:16 (1080x1920), 50-75s, H.264, có audio stream — trước khi qua bước tiếp (ADR-0034).
- **Chính sách kiểm tra renderer: không viết unit test cho `render_*.py`.** Đây là repository sản xuất media; các renderer Python hiện tại là công cụ dựng video theo từng project, không phải product code cần TDD/test coverage.
- **Visual self-check bắt buộc**: trích xuất frame tại nhiều mốc trong cửa sổ hook (0-3s) và xem trực tiếp (không chỉ tin vào code) — xác nhận hook text overlay tự thêm hiển thị đúng thời điểm (~t=0.1-0.2s), đủ lớn/đủ nổi bật, không bị đè/che bởi caption gốc của nguồn; visual surprise + narrative promise đọc được; early SFX/focal annotation sync đúng beat. Nếu không đạt, sửa lại trước khi coi Stage 4 là xong — không lùi việc này sang Post-Production Retro.
- **Cadence + Information Progression check (ADR-0036)**: xem fixed frames/contact sheet ở 0.5-1s cadence xuyên final 0-10s và targeted body spans. Final 0-5s target Visual Change mỗi 0.8-1.5s; final 5-10s không có unexplained gap >3s; sau 10s không có unexplained gap >6s. Scene detector chỉ là advisory. Manual review phải xác nhận mỗi narrative phase có question/causal/proof/payoff progression, không chỉ effect spam.
- **Loop-Payoff Closure check (ADR-0036)**: đọc lại hook và ending cạnh nhau; ending phải trả đúng open loop ban đầu và không mở một lesson thứ hai mà Short chưa giải thích.
- **Spoken-TTS preflight bắt buộc trước full render**: synthesize toàn bộ line riêng, đo raw/fitted duration và lưu per-line report (`voice`, engine rate/pitch, post-tempo, target duration, truncation). Không dùng `atempo < 1.0` để kéo chậm giọng lấp visual slot — giữ tốc độ tự nhiên rồi pad silence ở đuôi; nếu line quá dài thì rút gọn copy hoặc tăng nhẹ engine rate, chỉ cho phép post speed-up có bound. Ghép narrator-only preview và transcribe để bắt lỗi nuốt chữ/phát âm trước khi mix nhạc/source audio. Với TTS qua `loudnorm`, fit duration ở sample domain sau resample; xem pitfall chi tiết trong skill `clip-curation-edit`. (Root cause `trademe_v1`: macOS TTS có 5/9 line bị kéo xuống 0.72x, pass codec/loudness nhưng nghe phẳng và thiếu sức sống.)
- **Voice/TTS replacement sync gate**: khi thay voice hoặc TTS engine cho timeline đã dựng, slot-fit và tổng duration đúng KHÔNG chứng minh caption/visual sync. Render voice-control trước, transcribe audio của final MP4 bằng word timestamps, quantize `caption_at` lên frame kế tiếp, remap semantic visual theo clause thực sự được nói, và giữ caption layer tách khỏi static chrome. Với visual-only revision, mux lại accepted audio bằng stream copy và chứng minh audio-stream hash giống control. Bắt buộc có contact sheet toàn timeline + cặp BEFORE/AFTER quanh reveal; direct-source accurate seek phải reset PTS trước local caption gate. Xem `shorts-render-patterns/references/qwen-cloned-voice-word-sync-and-publishing.md` (root cause: Ronald Wayne v2 pass duration/ASR nhưng caption và proof visual chạy trước Qwen; v3 phát hiện thêm output-seek PTS bug ở direct quote).
- **Checklist bắt buộc trước khi coi Stage 4 là xong** (mỗi mục dưới đây từng là 1 lỗi thật lọt qua `validate()`/decode pass — codec/spec pass KHÔNG có nghĩa là video sạch):
  - [ ] **Guide-derived craft gate (ADR-0034) pass trên artifact cuối**: early SFX nghe được trong t=0-1s; 0-3s có visual surprise + narrative promise; focal pointer có mặt nếu cần; caption đúng font/profile, 2-5 từ/burst, keyword animate/emphasize, đọc được ở mobile preview và không che face/proof; CTA bumper custom bắt đầu t=38-42s và nói đủ Like/Subscribe/Comment; moving watermark thật sự đổi vị trí; transition/image motion có matching SFX. Kiểm bằng waveform + frame/contact-sheet ở đúng timestamp, không chỉ đọc filter graph.
  - [ ] **Không có khoảng đen/dead space ở BẤT KỲ đoạn nào, không chỉ đoạn cuối.** Scan pixel dòng dưới cùng khung hình (`img[y].mean()` cho các y gần đáy) tại nhiều mốc thời gian rải suốt cả video — một dải đen cố định (ví dụ drawbox che caption gốc) có thể tồn tại xuyên suốt toàn video mà chỉ lộ rõ ở đoạn không có gì vẽ đè lên (thường là đoạn cuối). `blackdetect` chỉ bắt khung hình đen HOÀN TOÀN, không bắt một dải đen cục bộ trong khung hình còn lại có nội dung — phải tự scan pixel, không dựa `blackdetect` là đủ. Nếu có card/overlay che một phần khung hình, xác nhận có cần blackout hay không: chỉ blackout khi ĐÚNG là để che nội dung nguồn không kiểm soát được (caption gốc, logo…) — nếu không có gì vẽ đè lên sau đó, đừng vẽ đen, hãy crop bỏ + zoom lại (crop cả 2 chiều theo cùng hệ số, không riêng 1 chiều, để tránh méo hình).
  - [ ] **Tại mỗi điểm nối giữa 2 đoạn cắt (segment hard-cut), audio không được dừng/bắt đầu đột ngột ở full volume.** Scan `volumedetect` theo lát 0.1s, trải ~0.6s trước và sau MỖI điểm cắt — phải thấy 1 đường cong giảm dần xuống gần im lặng ngay tại điểm cắt rồi tăng dần trở lại (fade-out/fade-in), không phải một bước nhảy đột ngột từ full volume này sang full volume khác. Nếu đoạn cắt nào audio giữ nguyên full volume tới sát mép rồi nhảy thẳng sang đoạn kế, tiếng cuối câu sẽ nghe như bị chặt cụt/không rõ và cảm giác 2 câu "đè" lên nhau, không có khoảng nghỉ. Fix: thêm `afade=t=out` cuối mỗi đoạn + `afade=t=in` đầu mỗi đoạn khi render segment riêng lẻ (trước khi concat) — chỉ đổi biên độ, không đổi thời lượng/timing nên video vẫn giữ đồng bộ.
  - Chi tiết root-cause + số liệu thực tế của các lỗi trên: xem AGENTS.md Known Pitfalls (mục hardknocks b1/ruiz) và `docs/production/hardknocks-b1-ruiz-billionaire-check.md` (Revision 3, 4, và 5).

## Stage 5 — Document & Retro (`docs/production/<name>.md`)

Điền theo template hiện có (Status, Video Specs, YouTube Title/Description, Source, Why This Segment, Hook Formula Applied, Value-Adds, Known Issues, What to Check at 48h) — xem `docs/production/bacsihai-v5-lao-dong-tay.md` làm mẫu.

### Hook Gate Evidence (blocking)

Production doc phải ghi riêng evidence của Stage 0 item 6: ngày check, định danh
rough-hook version, câu hỏi đưa cho naive viewer (không được giải thích story) và
câu trả lời nguyên văn đã ẩn danh về (a) họ thấy chuyện gì đang xảy ra, (b) open
question/stakes là gì, (c) họ có tiếp tục xem không và vì sao. Dòng tự đánh giá
kiểu "frame-0 pass" / "hook mạnh" không thay thế evidence này. Thiếu section này
thì Status không được chuyển thành `Completed` và Short không được upload.

### Publishing Metadata & Studio Settings Gate (blocking)

Trước khi đặt Status của production doc thành `Completed`, chạy packaging workflow rồi lưu đúng một canonical upload package:

1. Trích `central decision/object`, stakes, open loop, known audience anchor và factual constraints từ final script/artifact.
2. Tạo ít nhất 5 title thuộc các family money/number, decision, contradiction, authority và question; chấm từng title theo cold-viewer clarity, stakes, open loop, factual accuracy và mobile-length compliance. Với cold audience, ưu tiên object/entity đã biết hơn proper name ít người biết. Claim đang tranh cãi phải ở dạng question hoặc attribution, không được biến thành fact.
3. Chọn đúng một canonical title; không đưa alternatives vào upload package. Sau đó tạo description và Studio fields theo gate dưới đây.

Canonical upload package phải đủ các trường sau:

1. `Title`: một title đã chọn, không còn alternatives; tối đa 30 user-visible characters gồm spaces/emoji, Title Case ở mọi vertical, đúng hai emoji phù hợp.
2. `Description`: dòng đầu mirror Title; tối đa một câu mô tả bổ sung, giữ rõ ranh giới giữa fact độc lập và source-reported claim, không chứa raw affiliate link; cuối description là đúng ba Hashtags.
3. `Hashtags`: đúng ba hashtag liên quan, bắt buộc chứa `#shorts`, không hashtag soup.
4. `YouTube Studio Tags`: đúng ba niche-specific tags, là field riêng và không thay thế Hashtags.
5. `Audience`: `Not made for kids` cho ba vertical hiện tại; nếu nội dung tương lai thực sự directed at children thì legal classification override default này.
6. `Video Language`, `Location`, `Category`: ghi explicit, localized và chính xác.
7. `Playlist`: master playlist của đúng vertical.
8. `Related Video`: winner hiện tại sẽ được update để trỏ tới Short mới; first-upload bootstrap ghi `none — first channel upload`.
9. `Upload Details Template`: tên/ID template đã approve, dùng lại trong Studio.

Sau đó bắt buộc kết thúc mọi production doc bằng section này — yêu cầu MỌI lần, không chỉ khi có vấn đề:

```
## Post-Production Retro

### Hook Retro (bắt buộc, mọi video — proactive)
- Verbal: có cách nào làm hook lời nói/text mạnh hơn trong 3 giây đầu không?
  (Có ý tưởng mới? Viết ra. Không tìm được gì tốt hơn? Viết "none found.")
- Visual: có cách nào làm hook hình ảnh mạnh hơn trong 3 giây đầu không
  (framing, motion, prop, cut timing,...)? Áp dụng cùng rule.
- Nếu ý tưởng generalize được ra ngoài video này, cập nhật/thêm 1 item vào
  checklist Stage 0 trong docs/WORKFLOW.md ngay, cite video này làm nguồn.

### Workflow Delta (bắt buộc, mọi video — reactive)
Lần sản xuất này có gặp case mà các stage trong docs/WORKFLOW.md chưa cover không?
- Không -> viết "none".
- Có -> thực hiện đúng 1 hành động trước khi coi video này là xong:
  - Lỗ hổng về thứ tự/quy trình (rule đã tồn tại ở nơi khác, workflow chỉ
    chưa nói rõ khi nào check) -> sửa ngay stage tương ứng trong WORKFLOW.md.
  - Rule hoàn toàn mới, chưa từng được thiết lập -> viết ADR mới, rồi thêm
    1 dòng cite vào WORKFLOW.md.
  - Sự cố một lần, không phải rule chung -> thêm entry vào AGENTS.md Known
    Pitfalls thay vào đó.
```

**Enforcement**: Status của production doc một video KHÔNG được đánh dấu done, và dòng của nó trong `docs/experiments/EXPERIMENT-LOG.md` KHÔNG được đánh dấu final, cho tới khi cả 2 subsection trên đã điền đầy đủ — dù chỉ là "none" / "none found".

## Stage 6 — Upload & Log

- **Lane eligibility gate (ADR-0035)**: xác nhận Destination Channel hiện tại đúng strict round-robin order và Short trước trên lane đó đã đạt Distribution Plateau. Nếu chưa, STOP/queue; không skip lane. Ngoại lệ duy nhất: Short đầu tiên trên channel vẫn viral thì Short thứ hai có thể lên sau khoảng bảy ngày.
- Upload thủ công. Không paste raw affiliate link trong description (dùng redirect domain). Set `Not made for kids`, language, location, category và master playlist.
- Sau upload, set/verify Related Video wiring: winner hiện tại → Short mới; first-upload bootstrap được miễn.
- Log dòng đầu tiên vào `docs/experiments/EXPERIMENT-LOG.md`.
- Trong 48h đầu, reply genuine questions/substantive comments để giữ thread hữu ích hoạt động; bỏ qua spam, abuse và engagement bait lặp lại.

## Stage 7 — 48h Distribution & Plateau Verification

1. Chờ đủ 48h rồi mới fetch/check; không panic hoặc xóa sớm trong pickup window 24-48h.
2. Record Shorts Feed traffic share:
   - `>=70%` → healthy;
   - `60%..<70%` → watch state, giữ và monitor;
   - `<60%` → No-Feed State.
3. No-Feed original luôn được giữ. Tạo Material Revision bằng cách dựng lại toàn bộ 0-3s (shot/framing + hook copy + early SFX) và đổi thêm ít nhất một axis trong pacing/cut order, proof visuals, captions hoặc music; metadata-only/music-only không tính. Queue revision vào lane kế tiếp khi eligible.
4. Ba No-Feed liên tiếp trên cùng lane → Channel Burn State; remove lane khỏi rotation trong lúc replacement được phone-verify và age ≥3 tuần. Một Short flop không đủ kết luận burn.
5. Mỗi 24h record view increment. Distribution Plateau chỉ pass khi latest 24h increment `<=20%` preceding 24h increment ở hai checks liên tiếp và Short đã ≥48h. Video vẫn kéo view/ngày cao/ổn định không phải plateau.
6. Khi plateau, inspect AVD và retention 0-3s; metric yếu nhất phải được ghi vào production brief của Short kế tiếp. Không dùng API AVD/APV để giả lập Studio Stayed to Watch.
