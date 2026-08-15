"""Load and validate processed feature-table split manifests."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Mapping

from entity_matching.data.config import load_dataset_config
from entity_matching.features.table import (
    FEATURE_TABLE_SCHEMA_VERSION,
    METADATA_COLUMNS,
    FeatureTableError,
)


@dataclass(frozen=True)
class FeatureTableSplit:
    """Metadata for one processed feature-table split."""

    dataset_id: str
    split: str
    path: str
    summary_path: str
    row_count: int
    label_counts: dict[str, int]
    duplicate_pair_id_count: int
    duplicate_pair_id_examples: list[str]
    feature_columns: list[str]
    schema_version: str
    text_standardization_version: str
    feature_version: str


@dataclass(frozen=True)
class SplitManifest:
    """Validated model-ready feature-table manifest for one dataset."""

    dataset_id: str
    splits: dict[str, FeatureTableSplit]

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "splits": {
                split_name: asdict(split)
                for split_name, split in sorted(self.splits.items())
            },
        }


def load_feature_table_summary(path: str | Path) -> dict[str, Any]:
    """Load a feature-table summary JSON file."""

    with Path(path).open("r", encoding="utf-8") as file:
        summary = json.load(file)
    required = {
        "schema_version",
        "dataset_id",
        "split",
        "row_count",
        "label_counts",
        "feature_columns",
        "text_standardization_version",
        "feature_version",
    }
    missing = required - set(summary)
    if missing:
        raise FeatureTableError(f"Summary is missing required keys: {sorted(missing)}")
    if summary["schema_version"] != FEATURE_TABLE_SCHEMA_VERSION:
        raise FeatureTableError(
            f"Unexpected feature-table schema: {summary['schema_version']}"
        )
    return summary


def load_feature_table_rows(path: str | Path) -> list[dict[str, Any]]:
    """Load a processed feature-table CSV with typed metadata and features."""

    with Path(path).open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise FeatureTableError("Feature table has no header")
        rows = []
        feature_columns = [name for name in reader.fieldnames if name not in METADATA_COLUMNS]
        for row in reader:
            typed: dict[str, Any] = {
                "dataset_id": row["dataset_id"],
                "split": row["split"],
                "pair_id": row["pair_id"],
                "label": int(row["label"]),
            }
            for column in feature_columns:
                typed[column] = float(row[column])
            rows.append(typed)
    return rows


def validate_feature_table_file(
    csv_path: str | Path, summary_path: str | Path
) -> FeatureTableSplit:
    """Validate one feature-table CSV against its summary JSON."""

    summary = load_feature_table_summary(summary_path)
    rows = load_feature_table_rows(csv_path)

    if len(rows) != summary["row_count"]:
        raise FeatureTableError(
            f"Row count mismatch for {csv_path}: {len(rows)} != {summary['row_count']}"
        )
    if not rows:
        raise FeatureTableError(f"Feature table is empty: {csv_path}")

    csv_columns = set(rows[0])
    expected_columns = set(METADATA_COLUMNS) | set(summary["feature_columns"])
    if csv_columns != expected_columns:
        raise FeatureTableError(
            f"Column mismatch for {csv_path}: {sorted(csv_columns ^ expected_columns)}"
        )

    label_counts = {"0": 0, "1": 0}
    pair_ids = set()
    duplicate_pair_ids = set()
    for index, row in enumerate(rows):
        if row["dataset_id"] != summary["dataset_id"]:
            raise FeatureTableError(f"Row {index} has unexpected dataset_id")
        if row["split"] != summary["split"]:
            raise FeatureTableError(f"Row {index} has unexpected split")
        if row["pair_id"] in pair_ids:
            duplicate_pair_ids.add(row["pair_id"])
        pair_ids.add(row["pair_id"])
        if row["label"] not in (0, 1):
            raise FeatureTableError(f"Invalid label in row {index}: {row['label']}")
        label_counts[str(row["label"])] += 1
        for column in summary["feature_columns"]:
            value = row[column]
            if value < 0.0 or value > 1.0:
                raise FeatureTableError(
                    f"Feature value outside [0, 1] in row {index}, {column}: {value}"
                )

    if label_counts != summary["label_counts"]:
        raise FeatureTableError(
            f"Label count mismatch for {csv_path}: {label_counts} != {summary['label_counts']}"
        )

    return FeatureTableSplit(
        dataset_id=summary["dataset_id"],
        split=summary["split"],
        path=str(csv_path),
        summary_path=str(summary_path),
        row_count=summary["row_count"],
        label_counts={key: int(value) for key, value in summary["label_counts"].items()},
        duplicate_pair_id_count=len(duplicate_pair_ids),
        duplicate_pair_id_examples=sorted(duplicate_pair_ids)[:10],
        feature_columns=list(summary["feature_columns"]),
        schema_version=summary["schema_version"],
        text_standardization_version=summary["text_standardization_version"],
        feature_version=summary["feature_version"],
    )


def build_split_manifest(
    config_path: str | Path,
    processed_root: str | Path = "data/processed",
    split_names: list[str] | None = None,
) -> SplitManifest:
    """Build a validated split manifest from processed feature tables."""

    config = load_dataset_config(config_path)
    selected_splits = split_names or list(config.data["splits"])
    processed_base = Path(processed_root) / config.dataset_id
    splits = {}
    reference_feature_columns: list[str] | None = None

    for split in selected_splits:
        csv_path = processed_base / f"{split}.csv"
        summary_path = processed_base / f"{split}.summary.json"
        split_metadata = validate_feature_table_file(csv_path, summary_path)
        if split_metadata.dataset_id != config.dataset_id:
            raise FeatureTableError(
                f"Split {split} belongs to {split_metadata.dataset_id}, not {config.dataset_id}"
            )
        if reference_feature_columns is None:
            reference_feature_columns = split_metadata.feature_columns
        elif split_metadata.feature_columns != reference_feature_columns:
            raise FeatureTableError(f"Feature columns differ for split {split}")
        splits[split] = split_metadata

    return SplitManifest(dataset_id=config.dataset_id, splits=splits)
