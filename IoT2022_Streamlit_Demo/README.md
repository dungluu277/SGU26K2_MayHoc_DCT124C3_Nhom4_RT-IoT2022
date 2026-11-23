# RT-IoT2022 Streamlit Demo

Standalone, offline batch-inference demonstration for the SGU RT-IoT2022
classification project. The app has four pages: Overview, Attack Detection,
Prediction Analysis, and Model Comparison.

This is a research demonstration only. It does not monitor a live network,
provide a production API, or automatically respond to attacks.

## Confirmed source and demo paths

- Read-only source project: `../final_IoT/`
- Standalone demo: `IoT2022_Streamlit_Demo/`
- Model artifact and all app files are stored in this demo directory.

No source notebook, dataset, report, result, or workspace-level README is
modified by the app setup or model export process.

## Model and preprocessing provenance

The original project contained no `.joblib`, `.pkl`, ONNX, or other serialized
E06 model artifact. The final model evaluation notebook specifies the selected
pipeline as:

- `ColumnTransformer` with `OneHotEncoder(handle_unknown="ignore")` for
  `proto` and `service`.
- Numeric input columns passed through unchanged.
- `RandomForestClassifier(n_estimators=100, random_state=42,
  class_weight="balanced_subsample", n_jobs=-1)`.
- Final fit on Train + Validation (100,222 rows); Test is not used for fitting
  or model selection.

The included `artifacts/e06_random_forest.joblib` was rebuilt from the source
Train and Validation CSVs by `export_model.py`, matching that documented
configuration. It is not a serialized artifact copied from the notebooks,
because no such artifact existed in the source.

The app's headline Test metrics and per-class Test evaluation are the saved
results from the original project. They are separate from the rebuilt model;
the app does not claim that a regenerated artifact reproduces those saved
numbers exactly across scikit-learn versions.

## Run the application

Use Python 3.11–3.13 on Windows PowerShell:

```powershell
cd IoT2022_Streamlit_Demo
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1
```

Open the local URL printed by Streamlit (usually `http://localhost:8501`).

## Pages

1. **Overview** — compact dataset and reported Test KPIs, a log-scale class
   distribution, the seven-stage research workflow and source EDA figures.
2. **Attack Detection** — upload a CSV or run the included sample flows through
   the fitted pipeline. The page validates the 82-feature schema, summarizes
   predictions, filters and inspects individual flows, and downloads all
   predicted labels and class votes. `Attack_type` is optional; when present,
   it is used only to score that uploaded file.
3. **Prediction Analysis** — inspect class and Attack/Benign distributions,
   maximum class votes and individual records. Labeled uploads additionally
   show their classification report, confusion matrix and misclassified flows;
   unlabeled uploads do not show evaluation metrics. Saved held-out Test
   results are clearly separated from current predictions.
4. **Model Comparison** — compare saved Test accuracy, Macro-F1, Macro-Recall
   and error counts for Decision Tree, Random Forest, MLP and the balanced
   Random Forest; inspect all 14 experiments with CV and Validation shown
   separately.

## CSV format for inference

Provide the same feature columns as the model's expected schema. The CSV may
include an optional `Attack_type` column for evaluation; otherwise it is
ignored. Extra columns are ignored, but missing model features, missing
values, non-numeric numeric features, and unknown labels are reported.

`data/sample_flows.csv` contains a small, unlabeled sample extracted from the
source Test split. Do not treat it as a new independent test set.

For the Attack / Benign grouping, the project report identifies
`MQTT_Publish`, `Thing_Speak`, and `Wipro_bulb` as normal device traffic. The
other nine RT-IoT2022 labels are attack classes.

The displayed `max_class_vote` is the maximum Random Forest class vote. It is
not calibrated as a real-world probability of compromise.

## Rebuild the model artifact safely

The included artifact is ready to use. If it is removed, the
export script recreates it from the original prepared Train and Validation
files and writes outputs only into this demo's `artifacts/` directory:

```powershell
python export_model.py
```

The default inputs are read from
`../final_IoT/sample_project/data/splitted data/`. To rebuild without the
original folder, supply compatible prepared Train and Validation CSVs:

```powershell
python export_model.py --train .\path\to\train.csv --validation .\path\to\validation.csv
```

This script never reads Test, does not edit notebooks or source data, and
validates required columns and missing values before fitting. Only run
`joblib.load` on artifacts you trust; joblib files can execute code when loaded.

## Contents

- `app.py` and `pages/` — Streamlit interface and four pages.
- `src/demo_utils.py` — shared model loading, schema checks and inference.
- `export_model.py` — reproducible E06 pipeline export.
- `artifacts/` — fitted model and provenance manifest.
- `data/` — sample flows, copied result tables and compact project metadata.
- `assets/` — copied source EDA/result figures.

## Study results and limitations

The source experiment reports 99.88% Test Accuracy, 0.9747 Test Macro-F1,
0.9609 Test Macro-Recall, and 21 errors across 17,687 Test records. The
Random Forest balanced-subsample improvement over the baseline is small, and
no statistical significance test was reported.

Results come from a single dataset and a record-level stratified split. Rare
classes have very low support, and no deployment to a live or edge IoT system
was evaluated. High Accuracy is not evidence of perfect detection or
generalization to new attack families.

## Reference

UCI Machine Learning Repository, RT-IoT2022,
[DOI 10.24432/C5P338](https://doi.org/10.24432/C5P338).
