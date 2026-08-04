## Kết quả

**PASS - 99/100**

| Thời điểm | Caption | Bounds gồm stroke, px | Lề trong vùng x=100..980 | Kết quả |
|---:|---|---|---:|---|
| 0.10s | `ONE SUPPLIER` | x=174..894, y=1207..1316 | trái 74, phải 86 | PASS |
| 0.80s | `ONE SUPPLIER` | x=174..894, y=1207..1316 | trái 74, phải 86 | PASS |
| 1.60s | `CAN STOP YOUR BUSINESS` | x≈101..974, y≈1215..1296 | trái 1, phải 6 | PASS |
| 2.80s | `CAN STOP YOUR BUSINESS` | x≈101..975, y≈1215..1296 | trái 1, phải 5 | PASS |

Bounds được đo từ alpha của exact overlay sau Lanczos scale 540x960 → 1080x1920. Beat đỏ có full-frame tint nên bounds caption được tách bằng alpha-background subtraction.

## Kiểm tra yêu cầu

| Yêu cầu | Kết quả | Bằng chứng máy |
|---|---|---|
| Refinery chuyển động toàn màn hình | PASS | PNG 1080x1920; MAD ngoài vùng overlay lần lượt 17.85, 20.70, 30.81 |
| Chỉ một caption burst cùng lúc | PASS | 1 burst/frame; chuyển burst tại 1.5s |
| Không black header/card | PASS | Tỷ lệ pixel đen trong 400 px phía trên = 0.0000 ở cả bốn frame |
| Không Pexels/illustration label | PASS | Không có trong hook overlay/text inventory |
| Không channel logo | PASS | `MONEY BLINDSPOT` chỉ được renderer bật từ t≥3.0s |
| Không diagram `INPUT/BUSINESS` cũ | PASS | Không phát hiện |
| Không `EVERYTHING RUNS` | PASS | Không phát hiện |
| Amber line thành broken red line/X | PASS | Amber line/dot tại 0.10-0.80s; red break/X tại 1.60-2.80s |
| Ý nghĩa rõ trước 3s | PASS | Chuỗi caption tạo câu `ONE SUPPLIER CAN STOP YOUR BUSINESS`; red X củng cố quan hệ dừng |
| Caption nằm trong x=100..980 | PASS | Biên x nhỏ nhất 101, lớn nhất 975 |

## Text inventory

- **0.10s:** `ONE SUPPLIER`; source branding/markings nhỏ gồm `HOLLYFRONTIER`, `70`, railcar markings.
- **0.80s:** `ONE SUPPLIER`; HollyFrontier/industrial markings một phần.
- **1.60s:** `CAN STOP YOUR BUSINESS`; tank numbers `48`, `99`; railcar markings.
- **2.80s:** `CAN STOP YOUR BUSINESS`; tank/railcar markings nhỏ.

`HOLLYFRONTIER` là branding có sẵn trong footage, không phải channel logo.

**Blockers:** Không có.

**Cảnh báo không chặn:** Caption dài chỉ còn 1 px dư địa ở biên an toàn bên trái. Exact-final hiện tại đạt yêu cầu, nhưng không nên phóng to, tăng tracking hoặc đổi scaling.