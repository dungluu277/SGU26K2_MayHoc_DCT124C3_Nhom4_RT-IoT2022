# SGU26K2_MayHoc_DCT124C3_Nhom4_RT-IoT2022


## Thành viên

<table>
  <thead>
    <tr>
      <th style="width: 40%; text-align: center;">Họ và tên</th>
      <th style="width: 26%; text-align: center;">MSSV</th>
      <th style="width: 34%; text-align: center;">Vai trò</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Lưu Lương Mạnh Dũng</td>
      <td style="text-align: center;">3124411053</td>
      <td>Nhóm trưởng</td>
    </tr>
    <tr>
      <td>Nguyễn Thành Đại</td>
      <td style="text-align: center;">3124411061</td>
      <td>Thành viên</td>
    </tr>
    <tr>
      <td>Lê Đăng Tiến</td>
      <td style="text-align: center;">3124411311</td>
      <td>Thành viên</td>
    </tr>
    <tr>
      <td>Nguyễn Xuân Hậu Thành</td>
      <td style="text-align: center;">3124411278</td>
      <td>Thành viên</td>
    </tr>
  </tbody>
</table>


### Link drive minh chứng chạy thực nghiệm: https://drive.google.com/drive/folders/1dZ6BlL46RooJ-FnvvnCHD0tSNdVDdFsu?usp=drive_link

### Link google docs: https://docs.google.com/document/d/10iYZxoF4KZjpvoaexhOCCcAlMnjlhGNXDbLvKk89F0g/edit?usp=sharing

## Link phân công công việc nhóm: https://docs.google.com/spreadsheets/d/1anzJYDVXp3kiWoB7VXHo2T5IlKezRM_1/edit?usp=sharing&ouid=114781297964179421782&rtpof=true&sd=true

## Link slide: https://canva.link/1ovkbaqvdt6njs7



## Giới thiệu đồ án

Đồ án nghiên cứu cách dùng học máy để phân loại lưu lượng mạng IoT. Nhóm sử dụng bộ dữ liệu RT-IoT2022, trong đó mỗi dòng là một mẫu lưu lượng được mô tả bằng các đặc trưng mạng; mục tiêu là dự đoán nhãn `Attack_type` thuộc 12 lớp. Đây là bài toán phân loại nhiều lớp trên dữ liệu đã thu thập, không phải một hệ thống phát hiện tấn công đang chạy trực tiếp trên mạng.

Nhóm thực hiện khám phá và kiểm tra dữ liệu, chuẩn bị các tập Train, Validation và Test, sau đó xây dựng và so sánh các mô hình Decision Tree, Random Forest, MLP cùng nhiều cấu hình thực nghiệm. Các mô hình được lựa chọn dựa trên kết quả Cross-Validation và Validation; tập Test được giữ riêng để đánh giá mô hình sau cùng. Qua quá trình so sánh, E06 Random Forest với `class_weight="balanced_subsample"` được chọn. Trên 17.687 mẫu Test, mô hình đạt Accuracy 0,9988 và Macro-F1 0,9747. Kết quả chi tiết theo từng lớp được lưu trong notebook, báo cáo HTML và bảng tính Excel của đồ án.