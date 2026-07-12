# Flow Chuẩn — Cắt/Sản Xuất Video

Living document. File này tiến hóa qua thực tế sử dụng: mỗi lần sản xuất kết thúc bằng **Post-Production Retro** (Stage 5), xác nhận flow này vẫn đủ hoặc sửa file này *trước khi* video được coi là xong. Không được bỏ qua bước check này.

Doc này sắp xếp thứ tự pipeline và định nghĩa các gate cứng. Không lặp lại nội dung rule đã có trong ADR hay `AGENTS.md` — chỉ cite theo số/tên để tránh lệch pha khi ADR thay đổi.

## Stage 0 — HOOK GATE (chặn cứng)

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
```

**GATE RULE**: nếu bất kỳ item 1-6 fail trên MỌI candidate span trong source hiện tại, và không thể fix bằng cách chọn span khác trong cùng bản download, thì STOP. Quay lại Stage 1 — chọn span khác hoặc source video khác. Không được tiến sang Stage 2/3/4, và không được ship 1 hook đã biết là yếu với lý do "để retention data trả lời sau." (Đây chính là anti-pattern mà `docs/production/bacsihai-v5-lao-dong-tay.md` đã ghi nhận — self-caught weak hook, vẫn ship. Từ nay không được lặp lại.)

## Stage 1 — Source Research & Candidate Selection

- Chọn Source Channel theo từng niche (ADR-0001/0004 finance, ADR-0019 health/VN, ADR-0020 AI-ed).
- Check `data/source_videos.csv` (source-video dedup registry) theo video ID/kênh trước khi chọn — tránh chọn lại đúng video hoặc lặp kịch bản đã dùng.
- Download max quality: `yt-dlp -f "bestvideo[height>=2160]+bestaudio"` (không bao giờ nhận default 720p — AGENTS.md).
- Transcribe (mlx_whisper).
- Xác định một hoặc nhiều candidate contiguous span, mỗi span kèm 1 hook angle sơ bộ → đưa từng candidate vào Stage 0.
- Sau khi chốt source video dùng cho video mới, append 1 dòng vào `data/source_videos.csv`.

## Stage 2 — Cut Segment

- Extract candidate đã pass Stage 0. Chọn 1 trong 2 sub-format của Clip Curation Edit (ADR-0022):
  - **Contiguous VO** (ADR-0013): một span liền mạch 45-60s, audio bất biến, không bao giờ `concat` — dùng khi hook + payoff mạnh nhất đã nằm gọn trong 1 cửa sổ 45-60s của nguồn.
  - **Multi-Clip Mashup** (ADR-0022): nhiều đoạn rời rạc (mỗi đoạn <15s theo ADR-0007 item 3), nối bằng ffmpeg concat demuxer, hard-cut tại mọi điểm nối (không crossfade/sound-design) — dùng khi các moment mạnh nhất nằm rải rác quá xa nhau để gom vào 1 cửa sổ 45-60s duy nhất. Vẫn phải đạt tổng 45-60s sau khi ghép.
- Production doc phải nêu rõ đang dùng sub-format nào (cite ADR-0013 hoặc ADR-0022) trong phần "Why This Segment".

## Stage 3 — Hook Text + Overlays

- Viết hook overlay/caption/value-add. Phải thỏa ADR-0018 (caption sync/cadence), ADR-0016 (2-Second Rule, toàn video), ADR-0008 (Value-Add Layer).
- Nếu là Clip Curation Edit: phải thỏa thêm Transformative Gate của ADR-0007 (commentary track + ≥2 value-add + ≤50% source duration / mỗi clip <15s).
- Nếu commentary track là spoken TTS (không chỉ text overlay) layered lên audio gốc: xem ADR-0021 cho pattern mixing (ducking + amix + dynaudnorm) và cách diễn giải "audio bất biến" của ADR-0013.
- **Hook text overlay tự thêm (không phải caption gốc của nguồn) phải xuất hiện gần như ngay lập tức (~t=0.1-0.2s, không trễ hơn) và cỡ chữ đủ lớn/màu đủ nổi bật để giữ chân người xem ngay từ đầu** (user feedback, hardknocks_v2: bản render đầu tiên delay hook overlay tới t=1.3s với size=36 để tạo cadence beat - quá nhỏ, quá trễ. Cadence (item 6, Stage 0) nên đạt bằng zoompan/motion liên tục hoặc cắt cảnh, KHÔNG phải bằng cách trì hoãn hook text). Tham khảo size ~48-52px ở khung 1080px-rộng là **mốc tối thiểu (floor), không phải mục tiêu (target)** cho hook text chính - hardknocks_v2 nhận feedback tăng size 4 lần liên tiếp trên cùng 1 video (36→52→64→80→84), ưu tiên to hơn khi khung hình còn chỗ, áp dụng cho cả text phụ (stat card/counter-argument/CTA), không chỉ hook chính.
- **Nếu tăng size sẽ khiến chữ bị crop ở mép 1080px, rút ngắn nội dung chữ trước, không coi size hiện tại là trần cố định** (hardknocks_v2: câu hook dài "OTHERS SAY MONEY = HAPPY..." đã chạy sát mép ở size=64, không thể tăng thêm nếu giữ nguyên độ dài - phải rút ngắn còn "OTHERS: MONEY = HAPPY" mới tăng lên size=80 được).
- **Mỗi lần tăng size phải tự verify lại bằng frame extraction thực tế, không được suy ra an toàn từ margin của lần tăng trước** (hardknocks_v2 vòng 4: rút ngắn chữ thêm + tăng size 80→90 trong 1 bước tưởng là an toàn theo ước tính số ký tự, nhưng frame check phát hiện chữ bị crop cả 2 mép - phải lùi về size=84 mới đạt). Rút ngắn chữ + tăng size cùng lúc có thể cộng dồn vượt ngưỡng dù mỗi thay đổi riêng lẻ trông hợp lý - luôn re-verify bằng Stage 4 self-check sau MỖI lần đổi size, không chỉ lần đầu tiên đổi.
- **Đo pixel width thực tế trước khi render, không chỉ sau khi render** (bacsihai_v7): trước khi commit 1 size vào render script cho BẤT KỲ drawtext overlay nào (hook text chính, stat card, header, CTA), đo thử bằng `PIL.ImageFont.getlength(text)` với đúng font file/size sẽ dùng, so với chiều rộng khung hình (1080px) trừ margin mong muốn. bacsihai_v7's header overlay ("NHIỀU NGƯỜI NGHĨ: CHOLESTEROL = XẤU" @ size 64) bị tràn khung ở lần render đầu - bắt được qua Stage 4 frame check (đúng như quy trình), nhưng đo trước bằng PIL sẽ bắt được ngay từ đầu, biến việc sửa thành 1 vòng thay vì nhiều vòng thử-sai như hardknocks_v2's 4 rounds. Bước đo pixel không thay thế frame-check bắt buộc sau khi render (vẫn phải làm), chỉ giảm số vòng lặp cần thiết.

## Stage 4 — Render & Spec Verify

- Chạy `pipeline/<project>/render_*.py`.
- Verify 9:16 (1080x1920), ≤60s, H.264, có audio stream — trước khi qua bước tiếp.
- **Visual self-check bắt buộc**: trích xuất frame tại vài mốc trong cửa sổ hook (0-2s) và xem trực tiếp (không chỉ tin vào code) — xác nhận hook text overlay tự thêm hiển thị đúng thời điểm (~t=0.1-0.2s), đủ lớn/đủ nổi bật, không bị đè/che bởi caption gốc của nguồn. Nếu không đạt, sửa lại trước khi coi Stage 4 là xong — không lùi việc này sang Post-Production Retro.

## Stage 5 — Document & Retro (`docs/production/<name>.md`)

Điền theo template hiện có (Status, Video Specs, YouTube Title/Description, Source, Why This Segment, Hook Formula Applied, Value-Adds, Known Issues, What to Check at 48h) — xem `docs/production/bacsihai-v5-lao-dong-tay.md` làm mẫu.

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

- Upload thủ công. Không paste raw affiliate link trong description (dùng redirect domain).
- Log dòng đầu tiên vào `docs/experiments/EXPERIMENT-LOG.md`.
- Chờ 48h (metrics nhiễu nếu fetch trước đó — AGENTS.md). Fetch từ YouTube Studio, điền "What To Check At 48h" trong production doc và dòng log.

## Nằm ngoài scope (đã biết, không fix trong doc này)

- Ambiguity ở item 3 của Transformative Gate cho video dạng single-contiguous-segment.
- Các hàm helper bị duplicate giữa các render script trong `pipeline/<project>/`.
- Không có tool tự động check frame (ví dụ `inspect_image.py`) — frame-0 face check ở Stage 0 chủ đích giữ là visual judgment thủ công.
