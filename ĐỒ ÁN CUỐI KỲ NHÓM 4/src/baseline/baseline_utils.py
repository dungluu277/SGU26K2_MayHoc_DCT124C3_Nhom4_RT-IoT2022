"""Tiện ích dùng chung cho pipeline baseline RT-IoT2022."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    recall_score,
)

TARGET = "Attack_type"
SEED = 42


def project_root(start: Path | None = None) -> Path:
    """Tìm thư mục dự án dựa trên thư mục hiện tại hoặc vị trí notebook."""
    current = (start or Path.cwd()).resolve()
    candidates = [current, *current.parents]
    candidates.extend(path for path in current.iterdir() if path.is_dir())
    for candidate in candidates:
        if (candidate / "data" / "raw" / "RT_IOT2022.csv").is_file():
            return candidate
    raise FileNotFoundError(
        "Không tìm thấy thư mục dự án chứa data/raw/RT_IOT2022.csv."
    )


def baseline_paths(root: Path | None = None) -> dict[str, Path]:
    """Trả về các thư mục đầu vào và đầu ra chuẩn của baseline."""
    root = (root or project_root()).resolve()
    paths = {
        "root": root,
        "raw": root / "data" / "raw",
        "processed": root / "data" / "experiments" / "baseline" / "processed",
        "splits": root / "data" / "experiments" / "baseline" / "splits",
        "models": root / "models" / "baseline",
        "metrics": root / "reports" / "baseline" / "metrics",
        "figures": root / "reports" / "baseline" / "figures" / "baseline",
    }
    for key in ("processed", "splits", "models", "metrics", "figures"):
        paths[key].mkdir(parents=True, exist_ok=True)
    return paths


def load_processed_split(
    split: str, splits_dir: Path, target: str = TARGET
) -> tuple[np.ndarray, np.ndarray]:
    """Đọc một split đã biến đổi và tách ma trận đặc trưng khỏi nhãn."""
    path = splits_dir / f"{split}_processed.csv"
    if not path.is_file():
        raise FileNotFoundError(f"Không tìm thấy split: {path}")
    frame = pd.read_csv(path, low_memory=False)
    if target not in frame.columns:
        raise ValueError(f"Split {path.name} thiếu cột nhãn {target!r}.")
    features = frame.drop(columns=target).to_numpy(dtype=np.float32)
    labels = frame[target].astype(str).to_numpy()
    if not np.isfinite(features).all():
        raise ValueError(f"Split {path.name} chứa NaN hoặc Inf.")
    return features, labels


def evaluate_classifier(
    model: Any,
    model_name: str,
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray,
    y_val: np.ndarray,
    paths: dict[str, Path],
) -> dict[str, Any]:
    """Huấn luyện, đánh giá validation và lưu toàn bộ artifact của mô hình."""
    start = time.perf_counter()
    model.fit(x_train, y_train)
    fit_seconds = round(time.perf_counter() - start, 2)
    predictions = model.predict(x_val)
    labels = sorted(np.unique(np.concatenate([y_train, y_val])))
    result = {
        "model": model_name,
        "macro_f1": float(f1_score(y_val, predictions, average="macro", zero_division=0)),
        "macro_recall": float(
            recall_score(y_val, predictions, average="macro", zero_division=0)
        ),
        "accuracy": float(accuracy_score(y_val, predictions)),
        "fit_seconds": fit_seconds,
    }
    joblib.dump(model, paths["models"] / f"{model_name}.joblib")
    (paths["metrics"] / f"{model_name}_validation.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    pd.DataFrame(
        classification_report(
            y_val, predictions, labels=labels, output_dict=True, zero_division=0
        )
    ).T.to_csv(paths["metrics"] / f"{model_name}_validation_classification_report.csv")
    pd.DataFrame(
        confusion_matrix(y_val, predictions, labels=labels),
        index=labels,
        columns=labels,
    ).to_csv(paths["metrics"] / f"{model_name}_validation_confusion_matrix.csv")
    return result
