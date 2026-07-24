# Value-Added Editing Expanded to All Video Types

Value-Added Editing (VAE) mở rộng sang TẤT CẢ video types. Giờ value-adds trở thành AB variable cho mọi type: "có value-add vs không" hoặc "type A vs B" trên cùng 1 animation type. Kiến trúc: value-add layer tách khỏi renderer chính — render base video trước, rồi composite overlay (PIL/ffmpeg, toolchain có sẵn). Transformative Gate KHÔNG đổi — vẫn chỉ apply cho Clip Curation Edit (animation = zero-footage, không copyright risk).
