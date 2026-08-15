"""Data quality reports for normalized pair tables."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from entity_matching.data.config import load_dataset_config
from entity_matching.data.pairs import PairRecord, load_pair_table, summarize_pair_table


def _is_missing(value: str | None) -> bool:
    return value is None or value == ""


def _missing_attribute_counts(pair_table: list[PairRecord]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for pair in pair_table:
        for field, value in pair.left_attributes.items():
            if _is_missing(value):
                counts[f"left.{field}"] += 1
        for field, value in pair.right_attributes.items():
            if _is_missing(value):
                counts[f"right.{field}"] += 1
    return dict(sorted(counts.items()))


def _duplicate_pair_ids(pair_table: list[PairRecord]) -> dict[str, Any]:
    pair_ids = [pair.pair_id for pair in pair_table]
    counts = Counter(pair_ids)
    duplicates = {pair_id: count for pair_id, count in counts.items() if count > 1}
    return {
        "duplicate_pair_id_count": len(duplicates),
        "duplicate_pair_rows": sum(duplicates.values()),
        "examples": dict(list(duplicates.items())[:10]),
    }


def report_pair_table_quality(pair_table: list[PairRecord]) -> dict[str, Any]:
    """Build a quality report for one normalized pair table."""

    summary = summarize_pair_table(pair_table)
    return {
        **summary,
        "missing_attribute_counts": _missing_attribute_counts(pair_table),
        "duplicate_pairs": _duplicate_pair_ids(pair_table),
    }


def _id_set(pair_table: list[PairRecord], field: str) -> set[str]:
    values: set[str] = set()
    for pair in pair_table:
        value = getattr(pair, field)
        if value is not None:
            values.add(str(value))
    return values


def report_split_overlaps(split_tables: dict[str, list[PairRecord]]) -> dict[str, Any]:
    """Report pair, record, and entity overlap for every split pair."""

    split_names = list(split_tables)
    overlaps: dict[str, Any] = {}
    for index, left_name in enumerate(split_names):
        for right_name in split_names[index + 1 :]:
            left_table = split_tables[left_name]
            right_table = split_tables[right_name]
            key = f"{left_name}__{right_name}"

            left_pair_ids = _id_set(left_table, "pair_id")
            right_pair_ids = _id_set(right_table, "pair_id")
            left_record_ids = _id_set(left_table, "left_record_id") | _id_set(
                left_table, "right_record_id"
            )
            right_record_ids = _id_set(right_table, "left_record_id") | _id_set(
                right_table, "right_record_id"
            )
            left_entity_ids = _id_set(left_table, "left_entity_id") | _id_set(
                left_table, "right_entity_id"
            )
            right_entity_ids = _id_set(right_table, "left_entity_id") | _id_set(
                right_table, "right_entity_id"
            )

            overlaps[key] = {
                "pair_id_overlap": len(left_pair_ids & right_pair_ids),
                "record_id_overlap": len(left_record_ids & right_record_ids),
                "entity_id_overlap": len(left_entity_ids & right_entity_ids)
                if left_entity_ids and right_entity_ids
                else None,
            }
    return overlaps


def report_dataset_quality(config_path: str | Path) -> dict[str, Any]:
    """Load all configured splits and return quality reports."""

    config = load_dataset_config(config_path)
    split_names = list(config.data["splits"].keys())
    split_tables = {
        split_name: load_pair_table(config_path, split_name) for split_name in split_names
    }
    return {
        "dataset_id": config.dataset_id,
        "split_reports": {
            split_name: report_pair_table_quality(pair_table)
            for split_name, pair_table in split_tables.items()
        },
        "split_overlaps": report_split_overlaps(split_tables),
    }

