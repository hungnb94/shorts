## Kết quả: FAIL - 90/100

Lỗi chặn duy nhất là caption beat 2 không đạt biên an toàn ngang 100 px. Các yêu cầu hook và chuyển đổi amber line sang broken red line/X đều đạt.

| Thời điểm | Phát hiện | Kết quả |
|---|---|---|
| 0.10s | Refinery phủ toàn màn hình. Một caption burst: `ONE SUPPLIER`. Amber line vừa xuất hiện, node amber ở gần mép trái. Biên caption khoảng 185 px mỗi bên. | PASS |
| 0.80s | Node amber đã di chuyển rõ sang phải, chứng minh beat 1 có chuyển động. Vẫn chỉ một caption burst: `ONE SUPPLIER`. Biên caption lớn hơn 100 px. | PASS |
| 1.60s | Caption đổi thành `CAN STOP YOUR BUSINESS`. Supply line chuyển đỏ, bị ngắt ở giữa và có X đỏ. Foreground caption khoảng x=83..989; tính cả viền đen còn khoảng 75-82 px an toàn. | **FAIL** |
| 2.80s | Broken red line và X được phóng lớn, truyền đạt shutdown rõ. Caption vẫn là một burst. Biên ngang vẫn chỉ khoảng 75-82 px. | **FAIL** |

### Text inventory

| Frame | Text chủ động | Text tình cờ trong footage |
|---|---|---|
| 0.10s | `ONE SUPPLIER` | `HOLLYFRONTIER`, `70`, railcar markings như `UTLX 99551` |
| 0.80s | `ONE SUPPLIER` | Một phần branding HollyFrontier và railcar markings |
| 1.60s | `CAN STOP YOUR BUSINESS` | Tank numbers `48`, `99`; railcar markings nhỏ |
| 2.80s | `CAN STOP YOUR BUSINESS` | Tank/railcar markings nhỏ |

`HOLLYFRONTIER` là signage có sẵn trong source footage, không phải channel logo hoặc overlay.

### Kiểm tra yêu cầu

- Full-screen refinery: PASS.
- Chuyển động refinery: phù hợp với thay đổi framing giữa các timestamp; frame tĩnh không xác nhận được chuyển động liên tục.
- Chính xác một caption burst mỗi thời điểm: PASS.
- Không black header/card: PASS.
- Không Pexels/illustration label: PASS.
- Không channel logo trong 0-3s: PASS.
- Không `INPUT/BUSINESS` diagram hoặc `EVERYTHING RUNS`: PASS.
- Amber moving supply line chuyển thành broken red line/X: PASS.
- Người mới hiểu “một supplier có thể làm business dừng hoạt động” trước 3s: PASS ở mức cấu trúc machine-assisted.
- Caption có biên ngang tối thiểu 100 px: **FAIL tại 1.60s và 2.80s**.

### Blocker

Nới caption `CAN STOP YOUR BUSINESS` vào trong để toàn bộ viền đen nằm trong vùng x=100..979. Cần thu nhỏ hoặc siết tracking khoảng 4-6% để tạo dư địa an toàn, thay vì chỉ chạm đúng 100 px.

Đây chỉ là structured machine-assisted review, không phải human/cold-viewer approval.