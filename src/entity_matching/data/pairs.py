"""Normalize raw entity-matching pairs into a common in-memory table."""

from __future__ import annotations

from dataclasses import dataclass
import csv
import gzip
import json
from pathlib import Path
from typing import Any

from entity_matching.data.config import DatasetConfig, load_dataset_config
from entity_matching.data.validation import DatasetValidationError


@dataclass(frozen=True)
class PairRecord:
    """A normalized record pair used by downstream project stages."""

    dataset_id: str
    split: str
    pair_id: str
    left_record_id: str
    right_record_id: str
    label: int
    left_attributes: dict[str, str | None]
    right_attributes: dict[str, str | None]
    left_entity_id: str | None = None
    right_entity_id: str | None = None
    is_hard_negative: bool | None = None


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as file:
                return list(csv.DictReader(file))
        except UnicodeDecodeError:
            continue
    raise DatasetValidationError(f"Could not decode CSV file: {path}")


def _record_lookup(rows: list[dict[str, str]], record_id_field: str) -> dict[str, dict[str, str]]:
    return {str(row[record_id_field]): row for row in rows}


def _load_abt_buy_pair_table(config: DatasetConfig, split: str) -> list[PairRecord]:
    paths = config.data["local_paths"]
    schema = config.data["schema"]

    split_to_path_key = {
        "train": "train_pairs",
        "validation": "validation_pairs",
        "test": "test_pairs",
    }
    if split not in split_to_path_key:
        raise DatasetValidationError(f"Unknown abt-buy split: {split}")

    pair_rows = _read_csv_rows(config.resolve_path(paths[split_to_path_key[split]]))
    left_records = _record_lookup(
        _read_csv_rows(config.resolve_path(paths["abt_records"])),
        schema["source_record_id"],
    )
    right_records = _record_lookup(
        _read_csv_rows(config.resolve_path(paths["buy_records"])),
        schema["target_record_id"],
    )

    pair_table: list[PairRecord] = []
    for row in pair_rows:
        left_id = str(row["source_id"])
        right_id = str(row["target_id"])
        if left_id not in left_records:
            raise DatasetValidationError(f"Missing left record id {left_id}")
        if right_id not in right_records:
            raise DatasetValidationError(f"Missing right record id {right_id}")

        left = left_records[left_id]
        right = right_records[right_id]
        pair_table.append(
            PairRecord(
                dataset_id=config.dataset_id,
                split=split,
                pair_id=f"{left_id}#{right_id}",
                left_record_id=left_id,
                right_record_id=right_id,
                label=1 if row[schema["label"]] == "True" else 0,
                left_attributes={
                    field: left.get(field)
                    for field in [
                        *schema["left_text_fields"],
                        *schema["left_structured_fields"],
                    ]
                },
                right_attributes={
                    field: right.get(field)
                    for field in [
                        *schema["right_text_fields"],
                        *schema["right_structured_fields"],
                    ]
                },
            )
        )
    return pair_table


def _load_wdc_pair_table(config: DatasetConfig, split: str) -> list[PairRecord]:
    paths = config.data["local_paths"]
    schema = config.data["schema"]
    splits = config.data["splits"]
    if split not in splits:
        raise DatasetValidationError(f"Unknown WDC Products split: {split}")

    path = config.resolve_path(paths["extracted_dir"]) / splits[split]
    pair_table: list[PairRecord] = []
    with gzip.open(path, "rt", encoding="utf-8") as file:
        for line in file:
            row: dict[str, Any] = json.loads(line)
            pair_table.append(
                PairRecord(
                    dataset_id=config.dataset_id,
                    split=split,
                    pair_id=str(row[schema["pair_id"]]),
                    left_record_id=str(row[schema["left_record_id"]]),
                    right_record_id=str(row[schema["right_record_id"]]),
                    left_entity_id=str(row[schema["left_entity_id"]]),
                    right_entity_id=str(row[schema["right_entity_id"]]),
                    label=int(row[schema["label"]]),
                    is_hard_negative=bool(row[schema["hard_negative"]]),
                    left_attributes={
                        field: _string_or_none(row.get(field))
                        for field in [
                            *schema["left_text_fields"],
                            *schema["left_structured_fields"],
                        ]
                    },
                    right_attributes={
                        field: _string_or_none(row.get(field))
                        for field in [
                            *schema["right_text_fields"],
                            *schema["right_structured_fields"],
                        ]
                    },
                )
            )
    return pair_table


def _string_or_none(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def load_pair_table(config_path: str | Path, split: str) -> list[PairRecord]:
    """Load one raw split into the normalized pair-table representation."""

    config = load_dataset_config(config_path)
    if config.dataset_id == "wdc_products_80pair":
        return _load_wdc_pair_table(config, split)
    if config.dataset_id == "comperbench_abt_buy":
        return _load_abt_buy_pair_table(config, split)
    raise DatasetValidationError(f"No pair-table loader registered for {config.dataset_id}")


def summarize_pair_table(pair_table: list[PairRecord]) -> dict[str, Any]:
    """Return basic counts for a normalized pair table."""

    label_counts: dict[str, int] = {}
    hard_negative_counts: dict[str, int] = {}
    for pair in pair_table:
        label_key = str(pair.label)
        label_counts[label_key] = label_counts.get(label_key, 0) + 1
        if pair.is_hard_negative is not None:
            hard_key = str(pair.is_hard_negative)
            hard_negative_counts[hard_key] = hard_negative_counts.get(hard_key, 0) + 1

    summary: dict[str, Any] = {
        "dataset_id": pair_table[0].dataset_id if pair_table else None,
        "split": pair_table[0].split if pair_table else None,
        "total_pairs": len(pair_table),
        "label_counts": label_counts,
    }
    if hard_negative_counts:
        summary["hard_negative_counts"] = hard_negative_counts
    return summary

