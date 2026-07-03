# AB Test: One Variable Per Experiment

Mỗi experiment (1 ngày, 6 videos) chỉ thay đổi đúng 1 AB Variable giữa batch A (control) và batch B (test). Metric chính: AVD. Declare winner sau 7 experiments liên tiếp cùng biến đổi (statistical significance). Lý do: test nhiều biến cùng lúc = không isolate được causation. Trade-off: chậm hơn multi-variate, nhưng data sạch → học được chính xác yếu tố nào drove kết quả.
