"""Load model-ready matrices from validated feature tables without fitting models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from entity_matching.splitting import (
    SplitGuardError,
    SplitManifest,
    assert_no_leakage,
    build_split_guard_report,
    build_split_manifest,
    load_feature_table_rows,
)


class ModelMatrixError(ValueError):
    """Raised when model-ready matrix loading fails validation."""


@dataclass(frozen=True)
class ModelMatrix:
    """Model-ready data for one split."""

    dataset_id: str
    split: str
    pair_ids: list[str]
    y: list[int]
    X: list[list[float]]
    feature_columns: list[str]
    label_counts: dict[str, int]

    @property
    def row_count(self) -> int:
        return len(self.y)

    @property
    def feature_count(self) -> int:
        return len(self.feature_columns)

    def to_summary(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "split": self.split,
            "row_count": self.row_count,
            "feature_count": self.feature_count,
            "label_counts": self.label_counts,
            "feature_columns": self.feature_columns,
        }


@dataclass(frozen=True)
class ModelMatrixBundle:
    """Model-ready matrices for multiple validated splits."""

    dataset_id: str
    matrices: dict[str, ModelMatrix]
    feature_columns: list[str]
    guard_report: dict[str, Any]

    def to_summary(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "feature_columns": self.feature_columns,
            "splits": {
                split: matrix.to_summary()
                for split, matrix in sorted(self.matrices.items())
            },
            "guard_report": self.guard_report,
        }


def load_model_matrix(manifest: SplitManifest, split_name: str) -> ModelMatrix:
    """Load one split as X, y, and pair_ids from a validated manifest."""

    if split_name not in manifest.splits:
        raise ModelMatrixError(f"Split not found in manifest: {split_name}")

    split = manifest.splits[split_name]
    rows = load_feature_table_rows(split.path)
    feature_columns = split.feature_columns
    pair_ids = []
    y = []
    X = []

    for index, row in enumerate(rows):
        try:
            feature_values = [float(row[column]) for column in feature_columns]
        except KeyError as error:
            raise ModelMatrixError(
                f"Missing feature column in split {split_name}: {error}"
            ) from error
        if len(feature_values) != len(feature_columns):
            raise ModelMatrixError(f"Feature length mismatch in row {index}")
        pair_ids.append(str(row["pair_id"]))
        y.append(int(row["label"]))
        X.append(feature_values)

    if len(pair_ids) != split.row_count:
        raise ModelMatrixError(
            f"Row count mismatch for split {split_name}: {len(pair_ids)} != {split.row_count}"
        )

    return ModelMatrix(
        dataset_id=split.dataset_id,
        split=split.split,
        pair_ids=pair_ids,
        y=y,
        X=X,
        feature_columns=feature_columns,
        label_counts=split.label_counts,
    )


def load_model_matrix_bundle(
    config_path: str,
    *,
    processed_root: str = "data/processed",
    split_names: list[str] | None = None,
    require_pair_disjoint: bool = True,
    require_record_disjoint: bool = False,
    require_entity_disjoint: bool = False,
) -> ModelMatrixBundle:
    """Load model-ready matrices after validating splits and guard constraints."""

    guard_report = build_split_guard_report(config_path, processed_root, split_names)
    try:
        assert_no_leakage(
            guard_report,
            require_pair_disjoint=require_pair_disjoint,
            require_record_disjoint=require_record_disjoint,
            require_entity_disjoint=require_entity_disjoint,
        )
    except SplitGuardError as error:
        raise ModelMatrixError(str(error)) from error

    manifest = build_split_manifest(config_path, processed_root, split_names)
    matrices = {
        split_name: load_model_matrix(manifest, split_name)
        for split_name in sorted(manifest.splits)
    }
    feature_columns = next(iter(matrices.values())).feature_columns if matrices else []
    return ModelMatrixBundle(
        dataset_id=manifest.dataset_id,
        matrices=matrices,
        feature_columns=feature_columns,
        guard_report=guard_report,
    )


def summarize_model_matrix(matrix: ModelMatrix) -> dict[str, Any]:
    """Return a serializable summary for one model matrix."""

    return matrix.to_summary()
