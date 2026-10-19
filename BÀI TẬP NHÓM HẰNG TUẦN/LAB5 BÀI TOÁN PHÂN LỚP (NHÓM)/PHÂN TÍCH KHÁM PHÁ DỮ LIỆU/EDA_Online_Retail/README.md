# EDA Online Retail

## Mục tiêu
Khám phá dữ liệu giao dịch bán lẻ bằng Pandas, NumPy, Matplotlib và Seaborn; đánh giá chất lượng dữ liệu; phân tích doanh thu theo thời gian, quốc gia, sản phẩm và khách hàng.

## Nội dung
Notebook `EDA_Online_Retail.ipynb` gồm: nạp dữ liệu; kiểm tra kích thước/kiểu dữ liệu/giá trị thiếu/trùng lặp; chuẩn hóa ngày và số; nhận diện hóa đơn hủy, số lượng/đơn giá không hợp lệ; thống kê mô tả; histogram, boxplot, biểu đồ doanh thu tháng, top quốc gia/sản phẩm và phân tích khách hàng.

## Chuẩn bị
1. Python 3.10+ và Jupyter Notebook/JupyterLab.
2. Cài thư viện: `pip install pandas numpy matplotlib seaborn openpyxl`.
3. Tải dữ liệu từ [Kaggle notebook EDA Online Retail](https://www.kaggle.com/code/rajatkumar30/eda-online-retail) hoặc bộ dữ liệu Online Retail tương ứng.
4. Đặt file `.csv`, `.xlsx` hoặc `.xls` trong `data/`. Nếu có nhiều file, sửa `DATA_FILE` ở notebook để chọn đúng file.

## Cách chạy
Mở notebook bằng Jupyter, chọn kernel Python, chạy lần lượt các ô từ trên xuống. Kết quả bảng và biểu đồ hiển thị ngay dưới từng ô.

## Giải thích và lưu ý
`Revenue = Quantity × UnitPrice` là doanh thu ở cấp dòng hàng. Mã hóa đơn bắt đầu bằng `C` thường biểu thị hủy. Notebook giữ dữ liệu gốc để kiểm tra chất lượng, đồng thời tạo `valid` chỉ gồm số lượng và đơn giá dương cho một số phân tích doanh thu. Không xóa ngoại lai một cách máy móc; cần dựa vào nghiệp vụ. Các kết luận cuối cùng phải được điền sau khi chạy trên file dữ liệu thực tế.

## Cấu trúc
- `EDA_Online_Retail.ipynb`: mã nguồn và phần giải thích từng bước.
- `data/`: đặt dữ liệu tải từ Kaggle tại đây.
