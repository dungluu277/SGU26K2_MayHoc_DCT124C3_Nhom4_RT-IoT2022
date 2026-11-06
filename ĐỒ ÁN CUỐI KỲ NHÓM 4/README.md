# Đồ án cuối kỳ - Nhóm 4

## Cấu trúc dự án

Mỗi experiment có pipeline độc lập để dễ tái lập và so sánh:

```text
ĐỒ ÁN CUỐI KỲ NHÓM 4/
├── data/
│   ├── raw/                         # Dataset gốc
│   └── experiments/{baseline,exp_01,exp_02}/
│       ├── processed/
│       └── splits/
├── src/{baseline,exp_01,exp_02}/
│   ├── 01_EDA.ipynb
│   ├── 02_Preprocessing.ipynb
│   ├── 03_Data_Splitting.ipynb
│   ├── 04_Training/
│   │   ├── Random_Forest.ipynb
│   │   ├── SVM.ipynb
│   │   └── XGBoost.ipynb
│   └── 05_Evaluation.ipynb
├── models/{baseline,exp_01,exp_02}/
├── reports/
│   ├── baseline/
│   │   ├── figures/
│   │   │   └── baseline/
│   │   │       ├── eda/
│   │   │       ├── preprocessing/
│   │   │       ├── splitting/
│   │   │       ├── training/
│   │   │       └── evaluation/
│   │   └── metrics/
│   ├── exp_01/{figures,metrics}/
│   └── exp_02/{figures,metrics}/
├── configs/{baseline,exp_01,exp_02}.yaml
├── README.md
├── requirements.txt
└── .gitignore
```

## Quy trình thực hiện

1. Đặt dataset gốc vào `data/raw`.
2. Chọn experiment và đọc file tương ứng trong `configs`.
3. Chạy notebook `01` đến `03`.
4. Chạy các notebook mô hình trong `04_Training`.
5. Chạy `05_Evaluation` và lưu kết quả vào thư mục report của experiment.
6. Cập nhật `reports/experiment_comparison.csv` để so sánh các experiment.

Trong `reports/baseline/figures/baseline`, mỗi thư mục con tương ứng với một bước
và có thể chứa cả hình ảnh (`.png`, `.jpg`) lẫn dữ liệu trung gian (`.csv`):

- `eda`: biểu đồ và thống kê khám phá dữ liệu.
- `preprocessing`: kết quả kiểm tra sau tiền xử lý.
- `splitting`: thông tin về các tập train/validation/test.
- `training`: biểu đồ hoặc dữ liệu trong quá trình huấn luyện.
- `evaluation`: confusion matrix, ROC curve và các kết quả đánh giá.

`baseline` là cấu hình tham chiếu; `exp_01` và `exp_02` dùng để thử nghiệm các biến đổi hoặc siêu tham số khác.

## Cài đặt môi trường

```bash
pip install -r requirements.txt
```