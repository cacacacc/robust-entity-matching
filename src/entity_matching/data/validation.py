"""Raw dataset schema validation using only the Python standard library."""

from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path
from typing import Any, Iterable

from entity_matching.data.config import DatasetConfig, load_dataset_config


class DatasetValidationError(RuntimeError):
    """Raised when a raw dataset does not match its config contract."""


def _require_file(path: Path) -> None:
    if not path.is_file():
        raise DatasetValidationError(f"Missing required file: {path}")


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    _require_file(path)
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as file:
                reader = csv.DictReader(file)
                if reader.fieldnames is None:
                    raise DatasetValidationError(f"CSV has no header: {path}")
                return list(reader)
        except UnicodeDecodeError:
            continue
    raise DatasetValidationError(f"Could not decode CSV file: {path}")


def _iter_jsonl_gzip(path: Path) -> Iterable[dict[str, Any]]:
    _require_file(path)
    with gzip.open(path, "rt", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise DatasetValidationError(
                    f"Invalid JSON in {path} at line {line_number}"
                ) from exc


def _require_columns(actual: Iterable[str], expected: Iterable[str], context: str) -> None:
    actual_set = set(actual)
    missing = sorted(set(expected) - actual_set)
    if missing:
        raise DatasetValidationError(f"{context} is missing columns: {missing}")


def _label_counts(rows: Iterable[dict[str, Any]], label_field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        label = str(row[label_field])
        counts[label] = counts.get(label, 0) + 1
    return counts


def _validate_expected_counts(
    actual_total: int,
    actual_label_counts: dict[str, int],
    expected: dict[str, Any],
    context: str,
) -> None:
    if actual_total != expected["total_pairs"]:
        raise DatasetValidationError(
            f"{context} total_pairs mismatch: expected {expected['total_pairs']}, "
            f"got {actual_total}"
        )

    expected_matches = expected["matches"]
    expected_non_matches = expected["non_matches"]
    actual_matches = actual_label_counts.get("1", 0) + actual_label_counts.get("True", 0)
    actual_non_matches = actual_label_counts.get("0", 0) + actual_label_counts.get(
        "False", 0
    )

    if actual_matches != expected_matches or actual_non_matches != expected_non_matches:
        raise DatasetValidationError(
            f"{context} label count mismatch: expected "
            f"match={expected_matches}, non_match={expected_non_matches}; got "
            f"match={actual_matches}, non_match={actual_non_matches}"
        )


def validate_abt_buy(config: DatasetConfig) -> dict[str, Any]:
    """Validate CompERBench abt-buy raw CSV files against the config."""

    paths = config.data["local_paths"]
    schema = config.data["schema"]
    audited_counts = config.data["audited_counts"]

    split_paths = {
        "train": config.resolve_path(paths["train_pairs"]),
        "validation": config.resolve_path(paths["validation_pairs"]),
        "test": config.resolve_path(paths["test_pairs"]),
    }

    summary: dict[str, Any] = {"dataset_id": config.dataset_id, "splits": {}}
    for split_name, path in split_paths.items():
        rows = _read_csv_rows(path)
        _require_columns(rows[0].keys() if rows else [], schema["pair_columns"], str(path))
        label_counts = _label_counts(rows, schema["label"])
        _validate_expected_counts(
            len(rows), label_counts, audited_counts[split_name], split_name
        )
        summary["splits"][split_name] = {
            "total_pairs": len(rows),
            "label_counts": label_counts,
        }

    abt_rows = _read_csv_rows(config.resolve_path(paths["abt_records"]))
    buy_rows = _read_csv_rows(config.resolve_path(paths["buy_records"]))
    _require_columns(
        abt_rows[0].keys() if abt_rows else [],
        [schema["source_record_id"], *schema["left_text_fields"], *schema["left_structured_fields"]],
        paths["abt_records"],
    )
    _require_columns(
        buy_rows[0].keys() if buy_rows else [],
        [schema["target_record_id"], *schema["right_text_fields"], *schema["right_structured_fields"]],
        paths["buy_records"],
    )

    expected_records = audited_counts["records"]
    if len(abt_rows) != expected_records["abt_records"]:
        raise DatasetValidationError("abt record count mismatch")
    if len(buy_rows) != expected_records["buy_records"]:
        raise DatasetValidationError("buy record count mismatch")

    summary["records"] = {
        "abt_records": len(abt_rows),
        "buy_records": len(buy_rows),
    }
    return summary


def validate_wdc_products(config: DatasetConfig) -> dict[str, Any]:
    """Validate WDC Products JSONL-GZIP split files against the config."""

    paths = config.data["local_paths"]
    schema = config.data["schema"]
    splits = config.data["splits"]
    audited_counts = config.data["audited_counts"]
    extracted_dir = config.resolve_path(paths["extracted_dir"])

    required_fields = [
        schema["pair_id"],
        schema["label"],
        schema["hard_negative"],
        schema["left_record_id"],
        schema["right_record_id"],
        schema["left_entity_id"],
        schema["right_entity_id"],
        *schema["left_text_fields"],
        *schema["right_text_fields"],
        *schema["left_structured_fields"],
        *schema["right_structured_fields"],
    ]

    summary: dict[str, Any] = {"dataset_id": config.dataset_id, "splits": {}}
    for split_name, file_name in splits.items():
        path = extracted_dir / file_name
        rows = list(_iter_jsonl_gzip(path))
        if not rows:
            raise DatasetValidationError(f"Empty WDC split: {path}")
        _require_columns(rows[0].keys(), required_fields, str(path))
        label_counts = _label_counts(rows, schema["label"])
        _validate_expected_counts(
            len(rows), label_counts, audited_counts[split_name], split_name
        )
        summary["splits"][split_name] = {
            "total_pairs": len(rows),
            "label_counts": label_counts,
        }

    return summary


def audit_dataset(config_path: str | Path) -> dict[str, Any]:
    """Load a dataset config and run the matching validator."""

    config = load_dataset_config(config_path)
    if config.dataset_id == "wdc_products_80pair":
        return validate_wdc_products(config)
    if config.dataset_id == "comperbench_abt_buy":
        return validate_abt_buy(config)
    raise DatasetValidationError(f"No validator registered for {config.dataset_id}")
