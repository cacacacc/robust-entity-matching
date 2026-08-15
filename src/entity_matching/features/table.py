"""Build reproducible feature tables from interim pair-table JSONL files."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from entity_matching.data.config import load_dataset_config
from entity_matching.features.string_similarity import (
    STRING_FEATURE_VERSION,
    build_string_similarity_features,
)
from entity_matching.preprocessing import (
    TEXT_STANDARDIZATION_VERSION,
    standardize_pair_payload,
)


FEATURE_TABLE_SCHEMA_VERSION = "feature_table_v1"
METADATA_COLUMNS = ["dataset_id", "split", "pair_id", "label"]


class FeatureTableError(ValueError):
    """Raised when feature-table rows fail validation."""


def load_interim_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Load interim pair-table payloads from a JSONL file."""

    payloads = []
    with Path(path).open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                payloads.append(json.loads(stripped))
            except json.JSONDecodeError as error:
                raise FeatureTableError(f"Invalid JSON on line {line_number}: {error}") from error
    return payloads


def build_feature_row(pair_payload: Mapping[str, Any]) -> dict[str, Any]:
    """Build one flat feature-table row from one interim pair payload."""

    standardized = standardize_pair_payload(pair_payload)
    features = dict(build_string_similarity_features(standardized))
    features.pop("feature_version", None)

    row: dict[str, Any] = {
        "dataset_id": standardized["dataset_id"],
        "split": standardized["split"],
        "pair_id": standardized["pair_id"],
        "label": int(standardized["label"]),
    }
    row.update(features)
    return row


def build_feature_rows(pair_payloads: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Build flat feature-table rows from interim pair payloads."""

    return [build_feature_row(payload) for payload in pair_payloads]


def feature_columns(rows: list[Mapping[str, Any]]) -> list[str]:
    """Return sorted feature columns, excluding metadata columns."""

    if not rows:
        return []
    metadata = set(METADATA_COLUMNS)
    return sorted(name for name in rows[0] if name not in metadata)


def validate_feature_rows(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Validate feature rows and return a compact schema summary."""

    if not rows:
        raise FeatureTableError("Feature table is empty")

    expected_columns = set(rows[0])
    expected_feature_columns = feature_columns(rows)
    label_counts = {"0": 0, "1": 0}

    for index, row in enumerate(rows):
        if set(row) != expected_columns:
            raise FeatureTableError(f"Row {index} has inconsistent columns")
        if row["label"] not in (0, 1):
            raise FeatureTableError(f"Row {index} has invalid label: {row['label']}")
        label_counts[str(row["label"])] += 1
        for column in expected_feature_columns:
            value = row[column]
            if not isinstance(value, (int, float)):
                raise FeatureTableError(
                    f"Row {index} column {column} is not numeric: {value!r}"
                )
            if value < 0.0 or value > 1.0:
                raise FeatureTableError(
                    f"Row {index} column {column} is outside [0, 1]: {value!r}"
                )

    return {
        "schema_version": FEATURE_TABLE_SCHEMA_VERSION,
        "text_standardization_version": TEXT_STANDARDIZATION_VERSION,
        "feature_version": STRING_FEATURE_VERSION,
        "row_count": len(rows),
        "label_counts": label_counts,
        "feature_columns": expected_feature_columns,
    }


def write_feature_table_csv(
    rows: list[Mapping[str, Any]], output_path: str | Path
) -> dict[str, Any]:
    """Write feature rows to CSV and return validation summary."""

    summary = validate_feature_rows(rows)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = METADATA_COLUMNS + summary["feature_columns"]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    summary["path"] = str(path)
    return summary


def write_feature_table_summary(summary: Mapping[str, Any], output_path: str | Path) -> None:
    """Write feature-table metadata summary next to a CSV file."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(summary, file, indent=2, sort_keys=True, ensure_ascii=False)
        file.write("\n")


def export_feature_table(
    interim_path: str | Path, output_csv_path: str | Path
) -> dict[str, Any]:
    """Export one interim JSONL split to a processed feature-table CSV."""

    payloads = load_interim_jsonl(interim_path)
    rows = build_feature_rows(payloads)
    summary = write_feature_table_csv(rows, output_csv_path)
    summary_path = Path(output_csv_path).with_suffix(".summary.json")
    summary["summary_path"] = str(summary_path)
    write_feature_table_summary(summary, summary_path)
    return summary


def export_dataset_feature_tables(
    config_path: str | Path,
    interim_root: str | Path = "data/interim",
    output_root: str | Path = "data/processed",
) -> dict[str, Any]:
    """Export every configured split for one dataset to processed feature tables."""

    config = load_dataset_config(config_path)
    interim_base = Path(interim_root) / config.dataset_id
    output_base = Path(output_root) / config.dataset_id
    summary: dict[str, Any] = {
        "dataset_id": config.dataset_id,
        "schema_version": FEATURE_TABLE_SCHEMA_VERSION,
        "text_standardization_version": TEXT_STANDARDIZATION_VERSION,
        "feature_version": STRING_FEATURE_VERSION,
        "output_dir": str(output_base),
        "splits": {},
    }

    for split in config.data["splits"]:
        interim_path = interim_base / f"{split}.jsonl"
        output_csv_path = output_base / f"{split}.csv"
        split_summary = export_feature_table(interim_path, output_csv_path)
        summary["splits"][split] = split_summary

    return summary
