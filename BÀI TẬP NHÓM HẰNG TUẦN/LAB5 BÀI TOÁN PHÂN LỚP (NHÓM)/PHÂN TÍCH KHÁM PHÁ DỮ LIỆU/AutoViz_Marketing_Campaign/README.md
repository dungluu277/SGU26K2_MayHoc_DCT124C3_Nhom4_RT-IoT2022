# AutoViz với Marketing Campaign

## Mục tiêu
Tìm hiểu AutoViz và tự động tạo các biểu đồ EDA từ tập Marketing Campaign; quan sát phân phối, nhóm phân loại và mối quan hệ giữa các biến.

## Tính năng chính
- Tự động chọn và tạo nhiều biểu đồ dựa trên kiểu dữ liệu.
- Nhận đầu vào từ file hoặc DataFrame (tùy API/phiên bản).
- Có tùy chọn định dạng biểu đồ như PNG/SVG/JPG hoặc Bokeh ở các cấu hình được hỗ trợ.
- Có thể giới hạn số dòng/cột phân tích và lưu biểu đồ vào thư mục.

## Chuẩn bị
1. Python 3.10+ và Jupyter Notebook.
2. Cài thư viện: `pip install pandas autoviz`.
3. Tải `marketing_campaign.csv` từ [Customer Personality Analysis trên Kaggle](https://www.kaggle.com/datasets/imakash3011/customer-personality-analysis).
4. Đặt file trong `data/`. Notebook thử đọc file theo dấu tab trước.

## Cách chạy
Mở `AutoViz_Marketing_Campaign.ipynb`, chạy từng ô. Ô chính gọi `AutoViz_Class().AutoViz(...)`. Nếu API phiên bản cài đặt không tương thích với đầu vào DataFrame, chạy ô thay thế để lưu DataFrame thành CSV rồi cho AutoViz đọc file. Biểu đồ được hiển thị trong notebook và/hoặc lưu trong `AutoViz_Plots/`.

## Giải thích tham số
- `filename`: đường dẫn file; để chuỗi rỗng khi dùng DataFrame theo API hỗ trợ.
- `sep`: dấu phân cách file.
- `depVar`: tên biến mục tiêu; để rỗng khi EDA tổng quát.
- `verbose`: mức thông tin/hiển thị/lưu kết quả.
- `chart_format`: định dạng biểu đồ.
- `max_rows_analyzed`, `max_cols_analyzed`: giới hạn dữ liệu được phân tích để kiểm soát thời gian chạy.
- `save_plot_dir`: thư mục lưu biểu đồ nếu phiên bản hỗ trợ.

## Lưu ý
API AutoViz có khác biệt giữa các phiên bản. Nếu gặp lỗi tham số, kiểm tra tài liệu [AutoViz trên PyPI](https://pypi.org/project/autoviz/) và điều chỉnh theo phiên bản đã cài. Diễn giải biểu đồ cần dựa vào ý nghĩa nghiệp vụ; biểu đồ tự động không thay thế kiểm tra dữ liệu.
