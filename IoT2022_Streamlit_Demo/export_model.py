"""Rebuild the final E06 model using the source project's Train + Validation CSVs."""

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


APP_ROOT = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = (
    APP_ROOT.parent / "final_IoT" / "sample_project" / "data" / "splitted data"
)
TARGET = "Attack_type"
EXPECTED_FEATURE_COUNT = 82
EXPECTED_CATEGORICAL_COLUMNS = ("proto", "service")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fit the documented final E06 Random Forest on Train + Validation "
            "and write the artifact only into this demo directory."
        )
    )
    parser.add_argument("--train", type=Path, default=DEFAULT_DATA_DIR / "train.csv")
    parser.add_argument(
        "--validation", type=Path, default=DEFAULT_DATA_DIR / "validation.csv"
    )
    return parser.parse_args()


def validate_frames(train: pd.DataFrame, validation: pd.DataFrame) -> None:
    for name, frame in (("Train", train), ("Validation", validation)):
        if TARGET not in frame.columns:
            raise ValueError(f"{name} CSV must contain target column {TARGET!r}.")
        if frame.empty:
            raise ValueError(f"{name} CSV is empty.")
        if frame.isna().any().any():
            raise ValueError(
                f"{name} CSV contains missing values; the source E06 pipeline "
                "does not impute missing data."
            )
    if list(train.columns) != list(validation.columns):
        raise ValueError("Train and Validation columns or column order differ.")
    features = train.drop(columns=[TARGET])
    if len(features.columns) != EXPECTED_FEATURE_COUNT:
        raise ValueError("Train CSV must contain exactly 82 input features.")
    categorical = tuple(
        column
        for column in features.columns
        if not pd.api.types.is_numeric_dtype(features[column].dtype)
    )
    if categorical != EXPECTED_CATEGORICAL_COLUMNS:
        raise ValueError(
            "The source E06 pipeline expects only proto and service to be categorical."
        )


def build_pipeline(
    features: pd.DataFrame,
) -> tuple[Pipeline, list[str], list[str]]:
    numeric_columns = features.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_columns = [
        column for column in features.columns if column not in numeric_columns
    ]
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_columns,
            )
        ],
        remainder="passthrough",
    )
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=100,
                    random_state=42,
                    class_weight="balanced_subsample",
                    n_jobs=-1,
                ),
            ),
        ]
    )
    return pipeline, numeric_columns, categorical_columns


def main() -> None:
    args = parse_args()
    train_path = args.train.expanduser().resolve()
    validation_path = args.validation.expanduser().resolve()
    output_path = (APP_ROOT / "artifacts" / "e06_random_forest.joblib").resolve()
    if not train_path.is_file():
        raise FileNotFoundError(f"Train CSV not found: {train_path}")
    if not validation_path.is_file():
        raise FileNotFoundError(f"Validation CSV not found: {validation_path}")

    train = pd.read_csv(train_path)
    validation = pd.read_csv(validation_path)
    validate_frames(train, validation)

    development = pd.concat([train, validation], ignore_index=True)
    features = development.drop(columns=[TARGET])
    labels = development[TARGET].astype(str)
    summary = json.loads(
        (APP_ROOT / "data" / "project_summary.json").read_text(encoding="utf-8")
    )
    expected_classes = set(summary["dataset"]["label_groups"]["Benign"]) | set(
        summary["dataset"]["label_groups"]["Attack"]
    )
    if set(labels) != expected_classes:
        raise ValueError("Train + Validation must contain all 12 verified dataset labels.")
    model, numeric_columns, categorical_columns = build_pipeline(features)
    model.fit(features, labels)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix="e06-", suffix=".joblib", dir=output_path.parent, delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)
    try:
        joblib.dump(model, temporary_path, compress=3)
        os.replace(temporary_path, output_path)
    finally:
        temporary_path.unlink(missing_ok=True)

    manifest = {
        "model_name": "E06 Random Forest",
        "target": TARGET,
        "artifact": str(output_path.relative_to(APP_ROOT)),
        "feature_columns": features.columns.tolist(),
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "classes": [str(label) for label in model.classes_],
        "training_rows": int(len(development)),
        "fit_data": "Train + Validation; Test was not used for fitting or selection",
        "configuration": {
            "estimator": "RandomForestClassifier",
            "n_estimators": 100,
            "random_state": 42,
            "class_weight": "balanced_subsample",
            "n_jobs": -1,
            "categorical_preprocessing": "OneHotEncoder(handle_unknown='ignore')",
            "numeric_preprocessing": "passthrough",
        },
        "scikit_learn_version": sklearn.__version__,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_train_csv": train_path.name,
        "source_validation_csv": validation_path.name,
    }
    manifest_path = APP_ROOT / "artifacts" / "model_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Saved model: {output_path}")
    print(f"Saved manifest: {manifest_path}")
    print(f"Development rows: {len(development):,}")
    print(
        f"Features: {len(numeric_columns)} numeric, "
        f"{len(categorical_columns)} categorical"
    )
    print(f"scikit-learn: {sklearn.__version__}")


if __name__ == "__main__":
    main()
