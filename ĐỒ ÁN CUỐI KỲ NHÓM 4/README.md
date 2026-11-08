# RT-IoT2022 - Đồ án cuối kỳ nhóm 4

## Cấu trúc dự án

```text
RT-IoT2022-ML/
├── data/
│   ├── raw/RT_IOT2022.csv
│   └── processed/
├── notebooks/
│   ├── 01_data_understanding_eda.ipynb
│   ├── 02_data_cleaning_splitting.ipynb
│   ├── 03_data_preprocessing.ipynb
│   └── 04_random_forest_training.ipynb
├── experiments/
│   ├── baseline/
│   ├── tuning/
│   └── improvements/
├── models/
│   ├── rf_pipeline.joblib
│   └── mlp_pipeline.joblib
├── results/
│   ├── tables/
│   ├── figures/
│   └── metrics/
├── reports/
│   ├── 01_data_understanding_eda/
│   │   ├── figures/
│   │   ├── tables/
│   │   └── eda_summary.json
│   └── 02_data_cleaning_splitting/
│       ├── figures/
│       └── tables/
│   └── 03_data_preprocessing/
│       ├── figures/
│       └── tables/
│   └── 04_random_forest_training/
│       ├── figures/
│       └── tables/
│   └── 05_mlp_training/
│       ├── figures/
│       └── tables/
│   └── 06_evaluation/
│       ├── figures/
│       └── tables/
│   └── 07A_random_forest_improvement/
│       ├── figures/
│       └── tables/
├── requirements.txt
├── config.yaml
└── README.md
```

## Cài đặt

```bash
pip install -r requirements.txt
```

## Quy trình chạy

Từ thư mục dự án, chạy lần lượt:

```bash
python src/preprocessing.py
python src/train_rf.py
python src/train_mlp.py
python src/evaluate.py
```

Mỗi notebook có một thư mục riêng trong `reports/`. Các biểu đồ và bảng do
notebook tạo ra phải được lưu trong hai thư mục con `figures/` và `tables/`
tương ứng. Dataset gốc trong `data/raw/` không được ghi đè.
