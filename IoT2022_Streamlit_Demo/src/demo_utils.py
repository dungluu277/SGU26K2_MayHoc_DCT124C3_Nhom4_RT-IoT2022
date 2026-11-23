import json
import pickle
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


APP_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = APP_ROOT / "data"
ARTIFACT_DIR = APP_ROOT / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "e06_random_forest.joblib"
MANIFEST_PATH = ARTIFACT_DIR / "model_manifest.json"
SUMMARY_PATH = DATA_DIR / "project_summary.json"
TARGET = "Attack_type"
MAX_INFERENCE_ROWS = 50_000


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required configuration file was not found: {path}")
    with path.open(encoding="utf-8") as file:
        return json.load(file)


PROJECT_SUMMARY = _read_json(SUMMARY_PATH)
LABEL_GROUPS = PROJECT_SUMMARY["dataset"]["label_groups"]
BENIGN_CLASSES = frozenset(LABEL_GROUPS["Benign"])
ATTACK_CLASSES = frozenset(LABEL_GROUPS["Attack"])
KNOWN_CLASSES = BENIGN_CLASSES | ATTACK_CLASSES
EXPECTED_CATEGORICAL_COLUMNS = ("proto", "service")
EXPECTED_FEATURE_COUNT = 82
MODEL_LOAD_ERRORS = (
    AttributeError,
    EOFError,
    FileNotFoundError,
    ImportError,
    IndexError,
    OSError,
    pickle.UnpicklingError,
    TypeError,
    ValueError,
)

if len(KNOWN_CLASSES) != 12 or BENIGN_CLASSES & ATTACK_CLASSES:
    raise ValueError("The RT-IoT2022 attack/benign label mapping is invalid.")


def traffic_group(label: str) -> str:
    if label in BENIGN_CLASSES:
        return "Benign"
    if label in ATTACK_CLASSES:
        return "Attack"
    raise ValueError(f"Unknown RT-IoT2022 class label: {label!r}")


def render_header(title: str, subtitle: str) -> None:
    st.sidebar.markdown("### IoT Intrusion Detection")
    st.sidebar.caption("RT-IoT2022  |  ML Dashboard")
    st.sidebar.divider()
    try:
        load_model()
    except MODEL_LOAD_ERRORS as error:
        st.sidebar.error("Model Unavailable")
        st.sidebar.caption(str(error))
    else:
        st.sidebar.success("Model Loaded")

    latest = st.session_state.get("latest_predictions")
    if isinstance(latest, pd.DataFrame) and not latest.empty:
        st.sidebar.success("Prediction Ready")
    else:
        st.sidebar.caption("Prediction status: Awaiting input")

    st.sidebar.divider()
    st.sidebar.caption("Dataset  ·  RT-IoT2022")
    st.sidebar.caption("Models  ·  DT, RF, MLP")
    st.sidebar.caption("Institution  ·  Saigon University")
    st.sidebar.divider()
    st.title(title)
    st.caption(subtitle)
    st.caption("Offline research demonstration · Not a live network detector")


def load_local_csv(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"Demo data file was not found: {path}")
    return pd.read_csv(path)


@st.cache_resource(show_spinner="Loading the selected Random Forest pipeline...")
def load_model() -> Any:
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            "The model artifact is missing. Follow the 'Rebuild model artifact' "
            "instructions in this demo's README.md."
        )
    if not MANIFEST_PATH.is_file():
        raise FileNotFoundError(
            "The model manifest is missing. Rebuild the model with export_model.py."
        )
    model = joblib.load(MODEL_PATH)
    manifest = load_manifest()
    if not isinstance(model, Pipeline):
        raise TypeError("The model artifact is not a fitted sklearn Pipeline.")
    if not {"preprocessor", "classifier"}.issubset(model.named_steps):
        raise ValueError("The model pipeline is missing required fitted steps.")

    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["classifier"]
    if not isinstance(preprocessor, ColumnTransformer):
        raise TypeError("The fitted preprocessor is not a ColumnTransformer.")
    if not isinstance(classifier, RandomForestClassifier):
        raise TypeError("The selected model is not a RandomForestClassifier.")
    if classifier.class_weight != "balanced_subsample" or classifier.n_estimators != 100:
        raise ValueError("The model artifact does not match the selected E06 configuration.")
    if (
        not hasattr(model, "feature_names_in_")
        or model.n_features_in_ != EXPECTED_FEATURE_COUNT
    ):
        raise ValueError("The fitted model does not have the expected 82 input features.")
    if list(model.feature_names_in_) != manifest.get("feature_columns"):
        raise ValueError("Model input feature order does not match the manifest.")
    if set(manifest.get("categorical_columns", [])) != set(EXPECTED_CATEGORICAL_COLUMNS):
        raise ValueError(
            "The model manifest must identify proto and service as categorical."
        )
    if set(manifest.get("classes", [])) != KNOWN_CLASSES:
        raise ValueError("Model classes do not match the verified RT-IoT2022 labels.")
    if set(classifier.classes_) != KNOWN_CLASSES:
        raise ValueError("The fitted Random Forest does not contain all 12 dataset labels.")
    if len(manifest.get("numeric_columns", [])) != 80:
        raise ValueError("The model manifest must identify 80 numeric features.")
    if preprocessor.remainder != "passthrough":
        raise ValueError("The selected pipeline must pass numeric features through.")

    categorical = next(
        (
            (transformer, columns)
            for name, transformer, columns in preprocessor.transformers_
            if name == "categorical"
        ),
        None,
    )
    if categorical is None or not isinstance(categorical[0], OneHotEncoder):
        raise ValueError("The fitted pipeline is missing its categorical OneHotEncoder.")
    if tuple(categorical[1]) != EXPECTED_CATEGORICAL_COLUMNS:
        raise ValueError("The OneHotEncoder is not configured for proto and service.")
    if not hasattr(categorical[0], "categories_") or len(categorical[0].categories_) != 2:
        raise ValueError("The categorical OneHotEncoder has not been fitted.")
    if not hasattr(classifier, "estimators_"):
        raise ValueError("The Random Forest artifact has not been fitted.")
    return model


def load_manifest() -> dict[str, Any]:
    return _read_json(MANIFEST_PATH)


def prepare_features(
    frame: pd.DataFrame, manifest: dict[str, Any]
) -> tuple[pd.DataFrame, pd.Series | None, list[str]]:
    if frame.empty:
        raise ValueError("The uploaded CSV contains no rows.")
    if len(frame) > MAX_INFERENCE_ROWS:
        raise ValueError(
            f"The demo accepts up to {MAX_INFERENCE_ROWS:,} rows per upload."
        )

    labels = frame[TARGET].copy() if TARGET in frame.columns else None
    features = frame.drop(columns=[TARGET], errors="ignore").copy()
    expected = manifest["feature_columns"]
    if len(expected) != EXPECTED_FEATURE_COUNT:
        raise ValueError("The model manifest must define exactly 82 input features.")
    missing_columns = [column for column in expected if column not in features.columns]
    if missing_columns:
        preview = ", ".join(missing_columns[:10])
        more = " ..." if len(missing_columns) > 10 else ""
        raise ValueError(f"Required feature columns are missing: {preview}{more}")

    extra_columns = [column for column in features.columns if column not in expected]
    features = features.loc[:, expected]

    numeric_columns = manifest["numeric_columns"]
    categorical_columns = manifest["categorical_columns"]
    for column in numeric_columns:
        converted = pd.to_numeric(features[column], errors="coerce")
        invalid = converted.isna()
        if invalid.any():
            bad_rows = (np.flatnonzero(invalid.to_numpy())[:5] + 2).tolist()
            raise ValueError(
                f"Numeric feature {column!r} contains missing or non-numeric "
                f"values (CSV row numbers such as {bad_rows})."
            )
        if not np.isfinite(converted.to_numpy(dtype=float)).all():
            raise ValueError(f"Numeric feature {column!r} contains infinity.")
        features[column] = converted

    for column in categorical_columns:
        if features[column].isna().any():
            raise ValueError(f"Categorical feature {column!r} contains missing values.")
        features[column] = features[column].astype(str)

    if labels is not None:
        labels = labels.astype(str)
        unknown = sorted(set(labels) - KNOWN_CLASSES)
        if unknown:
            raise ValueError(f"Attack_type contains unknown classes: {unknown}")
    return features, labels, extra_columns


def predict_frame(
    model: Any,
    features: pd.DataFrame,
    labels: pd.Series | None,
) -> tuple[pd.DataFrame, dict[str, float] | None, pd.DataFrame | None]:
    predictions = model.predict(features)
    probabilities = model.predict_proba(features)
    classes = [str(label) for label in model.classes_]
    if set(classes) != KNOWN_CLASSES or len(classes) != 12:
        raise ValueError("Model output classes do not match the 12 RT-IoT2022 labels.")
    if probabilities.shape != (len(features), len(classes)):
        raise ValueError("Model probability output does not match the input rows and classes.")
    predicted_labels = [str(label) for label in predictions]
    prediction_frame = pd.DataFrame(
        {
            "Attack_type_predicted": predicted_labels,
            "Traffic_group_predicted": [
                traffic_group(label) for label in predicted_labels
            ],
            "max_class_vote": probabilities.max(axis=1),
        },
        index=features.index,
    )
    for index, label in enumerate(classes):
        prediction_frame[f"probability_{label}"] = probabilities[:, index]

    metrics = None
    matrix = None
    if labels is not None:
        metrics = {
            "accuracy": float(accuracy_score(labels, predictions)),
            "macro_f1": float(
                f1_score(labels, predictions, average="macro", zero_division=0)
            ),
            "macro_precision": float(
                precision_score(labels, predictions, average="macro", zero_division=0)
            ),
            "macro_recall": float(
                recall_score(labels, predictions, average="macro", zero_division=0)
            ),
        }
        matrix = pd.DataFrame(
            confusion_matrix(labels, predictions, labels=classes),
            index=classes,
            columns=classes,
        )
        matrix.index.name = "Actual"
        matrix.columns.name = "Predicted"
    return prediction_frame, metrics, matrix


def safe_load_model() -> Any | None:
    try:
        return load_model()
    except MODEL_LOAD_ERRORS as error:
        st.error(f"Could not load the model pipeline: {error}")
        return None

