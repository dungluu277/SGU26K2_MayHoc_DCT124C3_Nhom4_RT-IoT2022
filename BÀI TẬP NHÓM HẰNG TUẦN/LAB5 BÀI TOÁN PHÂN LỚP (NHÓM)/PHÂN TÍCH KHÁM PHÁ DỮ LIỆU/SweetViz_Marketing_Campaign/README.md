# SweetViz với Marketing Campaign

## Mục tiêu
Tìm hiểu công cụ EDA tự động SweetViz, tạo báo cáo HTML tổng hợp và thử phân tích biến mục tiêu `Response`/so sánh nhóm nếu dữ liệu có cột phù hợp.

## Tính năng chính
- Tóm tắt biến, kiểu dữ liệu, số giá trị duy nhất, giá trị thiếu và trùng lặp.
- Thống kê và trực quan hóa phân phối biến.
- Phân tích liên hệ giữa biến số và biến phân loại.
- Phân tích biến mục tiêu và so sánh hai nhóm/tập dữ liệu.
- Xuất báo cáo HTML độc lập để mở bằng trình duyệt.

## Chuẩn bị
1. Python 3.10+ và Jupyter Notebook.
2. Cài thư viện: `pip install pandas sweetviz`.
3. Tải `marketing_campaign.csv` từ [Customer Personality Analysis trên Kaggle](https://www.kaggle.com/datasets/imakash3011/customer-personality-analysis).
4. Đặt file trong `data/`. File Kaggle thường phân tách bằng tab; notebook thử đọc theo tab trước.

## Cách chạy
Mở `SweetViz_Marketing_Campaign.ipynb`, chạy lần lượt các ô. Notebook tạo:
- `SweetViz_Marketing_Report.html`
- `SweetViz_Marketing_Response_Report.html` nếu có cột `Response`
- `SweetViz_Response_Group_Comparison.html` nếu `Response` có đúng hai nhóm giá trị

Mở các file HTML bằng trình duyệt để xem báo cáo.

## Giải thích
`sv.analyze(df)` tạo báo cáo cho một DataFrame. `target_feat="Response"` yêu cầu SweetViz phân tích mối liên hệ giữa các biến và biến mục tiêu. `compare_intra()` so sánh hai nhóm trong cùng DataFrame. Đây là EDA mô tả, không chứng minh quan hệ nhân quả hoặc hiệu quả chiến dịch.

## Lưu ý
Nếu cài đặt gặp xung đột phiên bản, tạo môi trường ảo mới rồi cài lại. Không đặt tên notebook/script là `sweetviz.py`, vì có thể che khuất thư viện.
