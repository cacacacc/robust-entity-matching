"""Raw prediction artifact schema and validation helpers."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterable, Mapping


RAW_PREDICTION_SCHEMA_VERSION = "raw_predictions_v1"

RAW_PREDICTION_COLUMNS = [
    "schema_version",
    "experiment_id",
    "model_id",
    "seed",
    "split_role",
    "split",
    "pair_id",
    "y_true",
    "score",
    "threshold",
    "y_pred",
]


class PredictionArtifactError(ValueError):
    """Raised when raw prediction artifact rows are invalid."""


def prediction_artifact_path(
    results_root: str | Path,
    experiment_id: str,
    model_id: str,
    seed: int,
    split_role: str,
) -> Path:
    """Return the planned path for one raw prediction CSV artifact."""

    return (
        Path(results_root)
        / "predictions"
        / experiment_id
        / model_id
        / f"seed_{seed}"
        / f"{split_role}.csv"
    )


def validate_prediction_rows(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Validate and normalize raw prediction rows before writing."""

    normalized_rows = []
    for index, row in enumerate(rows):
        missing = set(RAW_PREDICTION_COLUMNS) - set(row)
        if missing:
            raise PredictionArtifactError(
                f"Prediction row {index} missing columns: {sorted(missing)}"
            )

        normalized = {
            "schema_version": str(row["schema_version"]),
            "experiment_id": str(row["experiment_id"]),
            "model_id": str(row["model_id"]),
            "seed": int(row["seed"]),
            "split_role": str(row["split_role"]),
            "split": str(row["split"]),
            "pair_id": str(row["pair_id"]),
            "y_true": int(row["y_true"]),
            "score": float(row["score"]),
            "threshold": float(row["threshold"]),
            "y_pred": int(row["y_pred"]),
        }
        _validate_prediction_row(normalized, index)
        normalized_rows.append(normalized)

    if not normalized_rows:
        raise PredictionArtifactError("At least one prediction row is required")
    return normalized_rows


def write_prediction_csv(rows: Iterable[Mapping[str, Any]], output_path: str | Path) -> int:
    """Write validated raw prediction rows to CSV."""

    normalized_rows = validate_prediction_rows(rows)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=RAW_PREDICTION_COLUMNS)
        writer.writeheader()
        writer.writerows(normalized_rows)
    return len(normalized_rows)


def read_prediction_csv(path: str | Path) -> list[dict[str, Any]]:
    """Read and validate raw prediction rows from CSV."""

    with Path(path).open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != RAW_PREDICTION_COLUMNS:
            raise PredictionArtifactError(
                f"Unexpected prediction columns in {path}: {reader.fieldnames}"
            )
        return validate_prediction_rows(reader)


def summarize_prediction_rows(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize validated raw prediction rows without computing model metrics."""

    normalized_rows = validate_prediction_rows(rows)
    label_counts = {"0": 0, "1": 0}
    prediction_counts = {"0": 0, "1": 0}
    for row in normalized_rows:
        label_counts[str(row["y_true"])] += 1
        prediction_counts[str(row["y_pred"])] += 1
    return {
        "schema_version": RAW_PREDICTION_SCHEMA_VERSION,
        "row_count": len(normalized_rows),
        "label_counts": label_counts,
        "prediction_counts": prediction_counts,
    }


def _validate_prediction_row(row: Mapping[str, Any], index: int) -> None:
    if row["schema_version"] != RAW_PREDICTION_SCHEMA_VERSION:
        raise PredictionArtifactError(
            f"Prediction row {index} has unexpected schema_version"
        )
    if row["split_role"] not in {"validation", "test"}:
        raise PredictionArtifactError(
            f"Prediction row {index} has invalid split_role: {row['split_role']}"
        )
    if row["y_true"] not in {0, 1}:
        raise PredictionArtifactError(f"Prediction row {index} has invalid y_true")
    if row["y_pred"] not in {0, 1}:
        raise PredictionArtifactError(f"Prediction row {index} has invalid y_pred")
    if row["score"] < 0.0 or row["score"] > 1.0:
        raise PredictionArtifactError(f"Prediction row {index} has invalid score")
    if row["threshold"] < 0.0 or row["threshold"] > 1.0:
        raise PredictionArtifactError(f"Prediction row {index} has invalid threshold")
