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
3. Cause+effect co-naming check (AGENTS.md pitfall, bacsihai v5): headline
   không được nêu cả nguyên nhân VÀ hệ quả cụ thể cùng lúc.
4. Payoff-timing check (bacsihai v5 pitfall): payoff thật của VO trong segment
   phải rơi trong ~5-10s đầu, không bị chôn sau ~15s.
5. Caption-sync feasibility (ADR-0018): source có clean speech onset ngay
   tại điểm bắt đầu candidate để caption lên màn hình được từ t=0.2s.
6. Cadence feasibility (ADR-0018/0016): trong 0-5s phải có sẵn 1 visual change
   mỗi 1-2s (cut, zoom, overlay, hoặc motion liên tục) — không phải shot tĩnh
   hoàn toàn, không có motion/prop/overlay slot nào.
7. Claim-strength flag (docs/research/hook-benchmarks-2026-07/REPORT.md): ghi
   nhận source có cho số liệu cụ thể hay chỉ có claim định tính — không tự
   động fail, nhưng phải log lại và ưu tiên candidate dạng Money+Number/
   Contrarian-Reveal nếu có.
8. Guide-derived promise check (ADR-0034): trong 0-3s phải có cả visual surprise
   lẫn narrative promise rõ ràng; early SFX phải có slot trong t=0-1s và focal
   target phải đọc được ngay hoặc có thể chỉ bằng arrow/pointer/annotation.
9. Naive-viewer check: cho một người không tham gia edit xem rough hook 0-3s mà
   không giải thích trước; họ phải nói được open question/promise khiến họ muốn
   xem tiếp. Nếu chỉ hiểu sau khi creator giải thích, hook fail.
```

**GATE RULE**: nếu bất kỳ item 1-6 hoặc item 8-9 fail trên MỌI candidate span trong source hiện tại, và không thể fix bằng cách chọn span khác trong cùng bản download, thì STOP. Item 7 là flag ưu tiên, không auto-fail. Quay lại Stage 1 — chọn span khác hoặc source video khác. Không được tiến sang Stage 2/3/4, và không được ship 1 hook đã biết là yếu với lý do "để retention data trả lời sau." (Đây chính là anti-pattern mà `docs/production/bacsihai-v5-lao-dong-tay.md` đã ghi nhận — self-caught weak hook, vẫn ship. Từ nay không được lặp lại.)

## Stage 1 — Source Research & Candidate Selection

- Chọn Source Channel theo từng niche (ADR-0001/0004 finance, ADR-0019 health/VN, ADR-0020 AI-ed).
- Reverse-engineer outlier channels trước khi chốt treatment: copy narrative mechanics, pacing, hook/payoff và packaging đã chứng minh được demand; không copy topic execution, wording hay footage cụ thể của họ (ADR-0034).
- Check `data/source_videos.csv` (source-video dedup registry) theo video ID/kênh trước khi chọn — tránh chọn lại đúng video hoặc lặp kịch bản đã dùng.
- Download max quality: `yt-dlp -f "bestvideo[height>=2160]+bestaudio"` (không bao giờ nhận default 720p — AGENTS.md).
- Transcribe (mlx_whisper).
- Xác định một hoặc nhiều candidate contiguous span, mỗi span kèm 1 hook angle sơ bộ → đưa từng candidate vào Stage 0.
- **Với nguồn dạng conference/talk dài (nhiều chục phút), trích 1 frame kiểm tra nhanh cho MỖI candidate window đã chọn từ transcript — không chỉ window của HOOK — trước khi chốt kế hoạch cắt** (aiwork_v3: 3/4 candidate windows chọn thuần từ nội dung transcript hóa ra là slide kiến trúc kỹ thuật hoặc màn hình CLI/terminal đầy jargon, chỉ phát hiện được khi trích frame thật ở Stage 2 — phải re-plan lại toàn bộ giữa chừng. Nội dung transcript hợp lý không đảm bảo hình ảnh tại đúng mốc đó dùng được, đặc biệt khi có ràng buộc audience-fit/né-code).
- **Với nguồn rất dài (~1 giờ trở lên), đừng đọc/xem tuyến tính toàn bộ transcript để tìm candidate — keyword-scan trước.** Quét toàn bộ transcript bằng các từ khóa liên quan tới insight tổng quát hóa được (ví dụ: "question", "clarify", "the reason", "the point", "why", "important because") để khoanh vùng ứng viên, sau đó mới đọc kỹ + frame-check từng vùng đã khoanh (Stage 0 item 1, và note ở trên). Đọc tuyến tính không khả thi ở độ dài này (aiwork_v6: nguồn 4480s/74.6 phút, 599 segments — quét từ khóa tìm ra đúng 1 câu tổng quát hóa được, nằm ở phút 53:41 của một buổi livestream lập trình gần như toàn bộ là screen-share/jargon).
- Sau khi chốt source video dùng cho video mới, append 1 dòng vào `data/source_videos.csv`.

## Stage 2 — Cut Segment

- Extract candidate đã pass Stage 0. Chọn 1 trong 2 sub-format của Clip Curation Edit (ADR-0022):
  - **Multi-Clip Mashup** (ADR-0022, duration superseded by ADR-0034): nhiều đoạn rời rạc (mỗi đoạn <15s theo ADR-0007 item 3), nối bằng ffmpeg concat demuxer, hard-cut tại mọi điểm nối (không crossfade video) — dùng khi các moment mạnh nhất nằm rải rác quá xa nhau để gom vào 1 cửa sổ 50-75s duy nhất. Vẫn phải đạt tổng 50-75s sau khi ghép; audio joins vẫn phải pass Stage 4 fade/clarity gate.
- Production doc phải nêu rõ đang dùng sub-format nào (ADR-0022) trong phần "Why This Segment".

## Stage 3 — Hook Text + Overlays

- Viết hook overlay/caption/value-add. Phải thỏa ADR-0018 (caption sync/cadence), ADR-0016 (2-Second Rule, toàn video), ADR-0008 (Value-Add Layer).
- Nếu là Clip Curation Edit: phải thỏa thêm Transformative Gate của ADR-0007 (commentary track + ≥2 value-add + ≤50% source duration / mỗi clip <15s).
- Apply ADR-0034's `Caption Style Profile`: 2-5 từ/burst, một keyword animate/emphasize, tâm caption mặc định ở 55-65% chiều cao frame; chỉ dịch để tránh che face/proof sau visual review. English dùng Komika Axis, Vietnamese dùng Bangers; lấy thông số ffmpeg từ calibration artifact đã verify, không copy literal CapCut size 16/stroke 60.
- Thêm một early SFX trong t=0-1s. Nếu focal target không rõ ngay, thêm arrow/pointer/animated annotation; không thêm pointer trang trí khi target đã hiển nhiên.
- Mọi image entrance/exit hoặc transition đã chọn phải có mục đích kể chuyện và matching SFX; generic transition spam fail gate.
- Dựng custom on-brand CTA bumper bắt đầu trong t=38-42s, lời CTA nói rõ cả Like + Subscribe + Comment. Generic stock CTA template fail.
- Thêm moving watermark không che face/proof/caption và thay đổi vị trí theo timeline để chống crop đơn giản.
- **Hook text overlay tự thêm (không phải caption gốc của nguồn) phải xuất hiện gần như ngay lập tức (~t=0.1-0.2s, không trễ hơn) và cỡ chữ đủ lớn/màu đủ nổi bật để giữ chân người xem ngay từ đầu** (user feedback, hardknocks_v2: bản render đầu tiên delay hook overlay tới t=1.3s với size=36 để tạo cadence beat - quá nhỏ, quá trễ. Cadence (item 6, Stage 0) nên đạt bằng zoompan/motion liên tục hoặc cắt cảnh, KHÔNG phải bằng cách trì hoãn hook text). Tham khảo size ~48-52px ở khung 1080px-rộng là **mốc tối thiểu (floor), không phải mục tiêu (target)** cho hook text chính - hardknocks_v2 nhận feedback tăng size 4 lần liên tiếp trên cùng 1 video (36→52→64→80→84), ưu tiên to hơn khi khung hình còn chỗ, áp dụng cho cả text phụ (stat card/counter-argument/CTA), không chỉ hook chính.
- **Nếu tăng size sẽ khiến chữ bị crop ở mép 1080px, rút ngắn nội dung chữ trước, không coi size hiện tại là trần cố định** (hardknocks_v2: câu hook dài "OTHERS SAY MONEY = HAPPY..." đã chạy sát mép ở size=64, không thể tăng thêm nếu giữ nguyên độ dài - phải rút ngắn còn "OTHERS: MONEY = HAPPY" mới tăng lên size=80 được).
- **Mỗi lần tăng size phải tự verify lại bằng frame extraction thực tế, không được suy ra an toàn từ margin của lần tăng trước** (hardknocks_v2 vòng 4: rút ngắn chữ thêm + tăng size 80→90 trong 1 bước tưởng là an toàn theo ước tính số ký tự, nhưng frame check phát hiện chữ bị crop cả 2 mép - phải lùi về size=84 mới đạt). Rút ngắn chữ + tăng size cùng lúc có thể cộng dồn vượt ngưỡng dù mỗi thay đổi riêng lẻ trông hợp lý - luôn re-verify bằng Stage 4 self-check sau MỖI lần đổi size, không chỉ lần đầu tiên đổi.
- **Đo pixel width thực tế trước khi render, không chỉ sau khi render** (bacsihai_v7): trước khi commit 1 size vào render script cho BẤT KỲ drawtext overlay nào (hook text chính, stat card, header, CTA), đo thử bằng `PIL.ImageFont.getlength(text)` với đúng font file/size sẽ dùng, so với chiều rộng khung hình (1080px) trừ margin mong muốn. bacsihai_v7's header overlay ("NHIỀU NGƯỜI NGHĨ: CHOLESTEROL = XẤU" @ size 64) bị tràn khung ở lần render đầu - bắt được qua Stage 4 frame check (đúng như quy trình), nhưng đo trước bằng PIL sẽ bắt được ngay từ đầu, biến việc sửa thành 1 vòng thay vì nhiều vòng thử-sai như hardknocks_v2's 4 rounds. Bước đo pixel không thay thế frame-check bắt buộc sau khi render (vẫn phải làm), chỉ giảm số vòng lặp cần thiết.

## Stage 4 — Render & Spec Verify

- Chạy `pipeline/<project>/render_*.py`.
- Verify 9:16 (1080x1920), 50-75s, H.264, có audio stream — trước khi qua bước tiếp (ADR-0034).
- **Chính sách kiểm tra renderer (user decision 2026-07-16): không viết unit test cho `render_*.py`.** Đây là repository sản xuất media; các renderer Python hiện tại là công cụ dựng video theo từng project, không phải product code cần TDD/test coverage. Không tạo, copy, mở rộng, hoặc coi `test_render_*.py` là completion gate trừ khi user yêu cầu rõ automated code test. Các test renderer đã tồn tại (ví dụ `pipeline/hardknocks/test_render_hardknocks_v8.py`) là legacy artifact, không phải precedent cho video tiếp theo. Gate đúng ở Stage 4 là chạy renderer thật và kiểm tra artifact MP4 bằng ffprobe/spec, full decode, final ASR, detector audio/black/freeze/silence, cùng visual frame/contact-sheet review thủ công.
- Sau khi video đã bàn giao, không tự sửa/rerender thêm chỉ vì thấy có thể tối ưu code hoặc test. Chỉ mở revision khi user yêu cầu sửa video; lúc đó rerun đúng các media gate bị ảnh hưởng, vẫn không bổ sung unit test renderer nếu user không yêu cầu.
- **Visual self-check bắt buộc**: trích xuất frame tại nhiều mốc trong cửa sổ hook (0-3s) và xem trực tiếp (không chỉ tin vào code) — xác nhận hook text overlay tự thêm hiển thị đúng thời điểm (~t=0.1-0.2s), đủ lớn/đủ nổi bật, không bị đè/che bởi caption gốc của nguồn; visual surprise + narrative promise đọc được; early SFX/focal annotation sync đúng beat. Nếu không đạt, sửa lại trước khi coi Stage 4 là xong — không lùi việc này sang Post-Production Retro.
- **Spoken-TTS preflight bắt buộc trước full render**: synthesize toàn bộ line riêng, đo raw/fitted duration và lưu per-line report (`voice`, engine rate/pitch, post-tempo, target duration, truncation). Không dùng `atempo < 1.0` để kéo chậm giọng lấp visual slot — giữ tốc độ tự nhiên rồi pad silence ở đuôi; nếu line quá dài thì rút gọn copy hoặc tăng nhẹ engine rate, chỉ cho phép post speed-up có bound. Ghép narrator-only preview và transcribe để bắt lỗi nuốt chữ/phát âm trước khi mix nhạc/source audio. Với TTS qua `loudnorm`, fit duration ở sample domain sau resample; xem pitfall chi tiết trong skill `clip-curation-edit`. (Root cause `trademe_v1`: macOS TTS có 5/9 line bị kéo xuống 0.72x, pass codec/loudness nhưng nghe phẳng và thiếu sức sống.)
- **Checklist bắt buộc trước khi coi Stage 4 là xong** (mỗi mục dưới đây từng là 1 lỗi thật lọt qua `validate()`/decode pass — codec/spec pass KHÔNG có nghĩa là video sạch):
  - [ ] **Guide-derived craft gate (ADR-0034) pass trên artifact cuối**: early SFX nghe được trong t=0-1s; 0-3s có visual surprise + narrative promise; focal pointer có mặt nếu cần; caption đúng font/profile, 2-5 từ/burst, keyword animate/emphasize, đọc được ở mobile preview và không che face/proof; CTA bumper custom bắt đầu t=38-42s và nói đủ Like/Subscribe/Comment; moving watermark thật sự đổi vị trí; transition/image motion có matching SFX. Kiểm bằng waveform + frame/contact-sheet ở đúng timestamp, không chỉ đọc filter graph.
  - [ ] **Không có khoảng đen/dead space ở BẤT KỲ đoạn nào, không chỉ đoạn cuối.** Scan pixel dòng dưới cùng khung hình (`img[y].mean()` cho các y gần đáy) tại nhiều mốc thời gian rải suốt cả video — một dải đen cố định (ví dụ drawbox che caption gốc) có thể tồn tại xuyên suốt toàn video mà chỉ lộ rõ ở đoạn không có gì vẽ đè lên (thường là đoạn cuối). `blackdetect` chỉ bắt khung hình đen HOÀN TOÀN, không bắt một dải đen cục bộ trong khung hình còn lại có nội dung — phải tự scan pixel, không dựa `blackdetect` là đủ. Nếu có card/overlay che một phần khung hình, xác nhận có cần blackout hay không: chỉ blackout khi ĐÚNG là để che nội dung nguồn không kiểm soát được (caption gốc, logo…) — nếu không có gì vẽ đè lên sau đó, đừng vẽ đen, hãy crop bỏ + zoom lại (crop cả 2 chiều theo cùng hệ số, không riêng 1 chiều, để tránh méo hình).
  - [ ] **Âm lượng TTS/VO phải đo trên FILE CUỐI ĐÃ MIX, không chỉ đo file TTS gốc riêng lẻ.** Quét `volumedetect` theo lát 0.25s xuyên suốt video, tìm bất kỳ đoạn nào tụt sâu hơn hẳn xung quanh (dấu hiệu VO bị chìm dưới dialogue/nhạc). Đo `ebur128`/`loudnorm print_format=json` riêng cho đúng khung thời gian mỗi đoạn VO đang phát, so với mức dialogue đã duck xung quanh — VO phải rõ ràng nổi hơn nền đã duck. Một file TTS test ổn khi đứng riêng (không delay) có thể vẫn bị hỏng sau khi ghép vào timeline dài hơn (ví dụ `adelay` đặt trước `loudnorm` làm sai lệch phép đo loudness) — chỉ tin kết quả đo trên bản mix cuối cùng.
  - [ ] Nếu dùng `loudnorm` cho VO: kiểm tra `target_offset` trong JSON output — nếu lệch nhiều (>1-2dB) dù đã thử cả single-pass và two-pass `linear=true`, khả năng cao là bị chặn bởi ngưỡng `TP` (true-peak) do clip có crest factor cao (đỉnh nhọn so với độ loud trung bình) — thêm 1 `acompressor` nhẹ trước `loudnorm` thay vì đổi mode.
  - [ ] **Tại mỗi điểm nối giữa 2 đoạn cắt (segment hard-cut), audio không được dừng/bắt đầu đột ngột ở full volume.** Scan `volumedetect` theo lát 0.1s, trải ~0.6s trước và sau MỖI điểm cắt — phải thấy 1 đường cong giảm dần xuống gần im lặng ngay tại điểm cắt rồi tăng dần trở lại (fade-out/fade-in), không phải một bước nhảy đột ngột từ full volume này sang full volume khác. Nếu đoạn cắt nào audio giữ nguyên full volume tới sát mép rồi nhảy thẳng sang đoạn kế, tiếng cuối câu sẽ nghe như bị chặt cụt/không rõ và cảm giác 2 câu "đè" lên nhau, không có khoảng nghỉ. Fix: thêm `afade=t=out` cuối mỗi đoạn + `afade=t=in` đầu mỗi đoạn khi render segment riêng lẻ (trước khi concat) — chỉ đổi biên độ, không đổi thời lượng/timing nên video vẫn giữ đồng bộ.
  - Chi tiết root-cause + số liệu thực tế của các lỗi trên: xem AGENTS.md Known Pitfalls (mục hardknocks b1/ruiz) và `docs/production/hardknocks-b1-ruiz-billionaire-check.md` (Revision 3, 4, và 5).

## Stage 5 — Document & Retro (`docs/production/<name>.md`)

Điền theo template hiện có (Status, Video Specs, YouTube Title/Description, Source, Why This Segment, Hook Formula Applied, Value-Adds, Known Issues, What to Check at 48h) — xem `docs/production/bacsihai-v5-lao-dong-tay.md` làm mẫu.

### Publishing Metadata & Studio Settings Gate (blocking)

Trước khi đặt Status của production doc thành `Completed`, doc phải chứa đúng một canonical upload package với đủ các trường sau:

1. `Title`: một title đã chọn, không còn alternatives; tối đa 30 user-visible characters gồm spaces/emoji, Title Case ở mọi vertical, đúng hai emoji phù hợp.
2. `Description`: dòng đầu mirror Title; tối đa một câu mô tả bổ sung, giữ rõ ranh giới giữa fact độc lập và source-reported claim, không chứa raw affiliate link; cuối description là đúng ba Hashtags.
3. `Hashtags`: đúng ba hashtag liên quan, bắt buộc chứa `#shorts`, không hashtag soup.
4. `YouTube Tags`: đúng ba Studio tags riêng, niche-specific, dùng ngôn ngữ audience, không misleading trend tags.
5. `Audience`: `Not made for kids` cho ba vertical hiện tại; nếu nội dung tương lai thực sự directed at children thì legal classification override default này.
6. `Video Language`, `Location`, `Category`: ghi explicit, localized và chính xác.
7. `Playlist`: master playlist của đúng vertical.
8. `Related Video`: winner hiện tại sẽ được update để trỏ tới Short mới; first-upload bootstrap ghi `none — first channel upload`.
9. `Upload Details Template`: tên/ID template đã approve, dùng lại trong Studio.

`Hashtags` và `YouTube Tags` là hai trường khác nhau, không được dùng một trường thay cho trường kia. Nếu bất kỳ trường nào trống, còn placeholder, sai cardinality/limit, hoặc vi phạm claim/link/audience guardrail, video chưa được coi là done và Stage 6 bị block.

Sau đó bắt buộc kết thúc mọi production doc bằng section này — yêu cầu MỌI lần, không chỉ khi có vấn đề:

```
## Post-Production Retro

### Hook Retro (bắt buộc, mọi video — proactive)
- Verbal: có cách nào làm hook lời nói/text mạnh hơn trong 3 giây đầu không?
  (Có ý tưởng mới? Viết ra. Không tìm được gì tốt hơn? Viết "none found.")
- Visual: có cách nào làm hook hình ảnh mạnh hơn trong 3 giây đầu không
  (framing, motion, prop, cut timing,...)? Áp dụng cùng rule.
- Công cụ hỗ trợ (khuyến khích, không bắt buộc): dùng skill
  `viral-video-analysis` (`.claude/skills/viral-video-analysis/SKILL.md`) để so
  sánh video vừa làm với 1-2 video viral cùng niche — trả lời 2 mục trên bằng
  bằng chứng cụ thể (hook pattern, frame-0 check, cadence, sound design) thay
  vì đoán. ADR-0023 giải thích vì sao skill này thay thế `video-analyzer`
  (Hermes/GPT-4o) cho use-case này.
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
- Khi lane đã eligible, Sunday khoảng 18:00 Atlantic/Halifax là preferred slot, không phải blocking gate; Plateau eligibility thắng lịch.
- Pre-upload gate: mở production doc và kiểm lại toàn bộ canonical package + Studio settings của Stage 5. Copy nguyên package từ doc và dùng approved `Upload Details Template`; không tự ứng biến trong upload UI. Nếu cần sửa phút cuối, cập nhật production doc trước rồi mới upload.
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

## Nằm ngoài scope (đã biết, không fix trong doc này)

- Ambiguity ở item 3 của Transformative Gate cho video dạng single-contiguous-segment.
- Các hàm helper bị duplicate giữa các render script trong `pipeline/<project>/`.
- Không có tool tự động check frame (ví dụ `inspect_image.py`) — frame-0 face check ở Stage 0 chủ đích giữ là visual judgment thủ công.
