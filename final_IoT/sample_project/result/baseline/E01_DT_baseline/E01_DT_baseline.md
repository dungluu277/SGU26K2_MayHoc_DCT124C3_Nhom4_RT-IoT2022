# [E01] Thực nghiệm DT — baseline

## Mục tiêu và giả thuyết

Cây không giới hạn là mốc so sánh, có thể overfit.

## Phạm vi

Chỉ train và validation. Dùng cùng 3-fold CV; không đọc hoặc đánh giá test. Pipeline fit lại riêng trong mỗi training fold.

## Cấu hình

```json
{
  "id": "E01",
  "family": "DT",
  "variant": "baseline",
  "hypothesis": "Cây không giới hạn là mốc so sánh, có thể overfit.",
  "params": {}
}
```

## Tiêu chí hoàn thành
Gồm các file cần phải nộp và các bước ghi chú 
- [x] Tiền xử lý dữ liệu trên dữ liệu đã xử lý cơ bản
- [x] Cho model chạy 3CV (3 Cross validation) ghi điểm từng lượt vào excel offline, online và ghi điểm vào mardown này phần "Kết quả chạy"
- [x] Ghi chú lại nhận xét và khuyết điểm của lần exp hoặc khắc phục gì so với exp trước đó

## Kết quả đã chạy
            accuracy  macro_f1  weighted_f1   macro_precision     macro_recall
final_valid	0.997682	0.974604	0.997679	    0.986719	          0.965469

## Kết luận mô hình 
# Ưu điểm
# Nhược điểm
