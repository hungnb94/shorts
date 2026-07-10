# KỊCH BẢN V5 — 1 VIDEO, NGUỒN MỚI (AGBrXy-2SxI)

## Nguyên tắc
- 1 video duy nhất lần này (không phải batch 3 video như v4)
- Mỗi video = 1 đoạn continuous từ source (VO Bác sĩ Hải nói liên tục, không ngắt) — ADR-0013
- Frame t=0 của đoạn cắt PHẢI có mặt người — đã verify bằng frame extract, xem `docs/production/bacsihai-v5-lao-dong-tay.md` — ADR-0017
- Subtitle t=0-5s = word-burst 2-5 từ/cụm, cadence ~1-1.3s, 1 từ khóa nhấn màu vàng — ADR-0018
- Subtitle t=5s→hết = tóm tắt theo từng đoạn, tightened ~4-5s/block (v4 dùng ~8-9s, quá chậm)

---

## VIDEO: "Vì Sao Người Lao Động Chân Tay Ít Bị Alzheimer Hơn?"

**Nguồn**: AGBrXy-2SxI — livestream "Bí quyết sống thọ của ông bà xưa" (2026-07-10)
**Source range**: 314.36s → 367.00s (52.64s continuous)
**Bối cảnh trong livestream**: đây là phần mở đầu "trụ cột #1: vận động" trong khung "5 trụ cột sức khỏe" mà Bác sĩ Hải dùng để giải thích bí quyết của các vùng Blue Zone.

**Lời thoại (verbatim từ source, 314.36-367.00)**:

"Nhưng mà cái vấn đề ở đây là con người ngày xưa chúng ta vận động, chúng ta lao động thì đúng hơn.
Vấn đề ở đây là lao động bằng đôi bàn tay.
Và có một cái thông tin và một trong những điều chúng ta cần biết đó chính là những người lao động bằng đôi bàn tay. Theo đúng nghĩa đen nhé.
Chứ chúng ta không phải là chúng ta nói là tôi lao động chí óc thì cũng là lao động bằng đôi bàn tay và khối óc.
Không, cái lao động bằng tay ở đây là những người làm công việc mà họ dùng tay để lao động.
Thì có một điều rất thú vị là tỉ lệ bị những vấn đề liên quan đến Parkinson hay liên quan đến vấn đề về Alzheimer.
Có nghĩa là tỉ lệ bị thoái hóa thần kinh của những nhóm người lao động bằng tay thấp hơn rất nhiều so với những người mà lao động, chúng ta gọi là lao động chí óc."

**Flow kiểm tra**: mở gap ("người xưa 'vận động' = lao động tay") → làm rõ "lao động tay" nghĩa đen là gì (loại trừ "lao động trí óc") → reveal: tỉ lệ Parkinson/Alzheimer thấp hơn rất nhiều ở nhóm lao động tay. ✓ Hợp lý, đủ 1 arc hoàn chỉnh, không cắt giữa câu.

**Lưu ý nguồn không cho số liệu %** — Bác sĩ Hải nói "thấp hơn rất nhiều" (định tính), KHÔNG có con số cụ thể. Data-viz overlay phải giữ đúng khung định tính này, không tự chế số liệu (fact-check risk).

---

## Tổng kết verification

| Video | Range | Duration | Flow | Cắt giữa câu? | Frame t=0 có mặt? |
|-------|-------|----------|------|---------------|---------------------|
| V5 lao_dong_tay | 314.36-367.00 | 52.64s | mở gap vận động→lao động tay → làm rõ nghĩa đen → reveal Parkinson/Alzheimer thấp hơn | Không ✓ | Có ✓ (verify frame `/tmp/hookcheck/hook0.jpg`, `hook05.jpg`) |
