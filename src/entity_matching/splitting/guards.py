"""Leakage guard reports for model-ready feature-table splits."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
from typing import Any

from entity_matching.data.pairs import PairRecord, load_pair_table
from entity_matching.splitting.manifest import (
    SplitManifest,
    build_split_manifest,
    load_feature_table_rows,
)


class SplitGuardError(ValueError):
    """Raised when a split guard detects disallowed leakage."""


def compare_pair_sets(manifest: SplitManifest) -> dict[str, dict[str, int]]:
    """Compare pair_id overlap across processed feature-table splits."""

    split_pairs = {}
    for split_name, split in manifest.splits.items():
        rows = load_feature_table_rows(split.path)
        split_pairs[split_name] = {row["pair_id"] for row in rows}

    overlaps = {}
    for left_split, right_split in combinations(sorted(split_pairs), 2):
        key = f"{left_split}__{right_split}"
        overlaps[key] = {
            "pair_id_overlap": len(split_pairs[left_split] & split_pairs[right_split])
        }
    return overlaps


def compare_record_and_entity_sets(
    config_path: str | Path, split_names: list[str]
) -> dict[str, dict[str, int | None]]:
    """Compare record/entity overlap across normalized pair tables."""

    split_tables = {split: load_pair_table(config_path, split) for split in split_names}
    split_records = {
        split: _record_ids(pair_table) for split, pair_table in split_tables.items()
    }
    split_entities = {
        split: _entity_ids(pair_table) for split, pair_table in split_tables.items()
    }

    overlaps = {}
    for left_split, right_split in combinations(sorted(split_names), 2):
        left_entities = split_entities[left_split]
        right_entities = split_entities[right_split]
        entity_overlap = (
            None
            if left_entities is None or right_entities is None
            else len(left_entities & right_entities)
        )
        key = f"{left_split}__{right_split}"
        overlaps[key] = {
            "record_id_overlap": len(
                split_records[left_split] & split_records[right_split]
            ),
            "entity_id_overlap": entity_overlap,
        }
    return overlaps


def build_split_guard_report(
    config_path: str | Path,
    processed_root: str | Path = "data/processed",
    split_names: list[str] | None = None,
) -> dict[str, Any]:
    """Build a model-readiness report for selected feature-table splits."""

    manifest = build_split_manifest(config_path, processed_root, split_names)
    selected_splits = sorted(manifest.splits)
    return {
        "dataset_id": manifest.dataset_id,
        "selected_splits": selected_splits,
        "manifest": manifest.to_dict(),
        "within_split_duplicate_pair_ids": {
            split_name: {
                "duplicate_pair_id_count": split.duplicate_pair_id_count,
                "duplicate_pair_id_examples": split.duplicate_pair_id_examples,
            }
            for split_name, split in sorted(manifest.splits.items())
        },
        "pair_id_overlaps": compare_pair_sets(manifest),
        "record_entity_overlaps": compare_record_and_entity_sets(
            config_path, selected_splits
        ),
    }


def assert_no_leakage(
    report: dict[str, Any],
    *,
    require_pair_disjoint: bool = True,
    require_record_disjoint: bool = False,
    require_entity_disjoint: bool = False,
) -> None:
    """Raise if selected leakage constraints are violated."""

    if require_pair_disjoint:
        for split_name, values in report["within_split_duplicate_pair_ids"].items():
            if values["duplicate_pair_id_count"] > 0:
                raise SplitGuardError(
                    f"Duplicate pair IDs in {split_name}: {values['duplicate_pair_id_count']}"
                )
        for comparison, values in report["pair_id_overlaps"].items():
            if values["pair_id_overlap"] > 0:
                raise SplitGuardError(
                    f"Pair leakage in {comparison}: {values['pair_id_overlap']}"
                )

    if require_record_disjoint or require_entity_disjoint:
        for comparison, values in report["record_entity_overlaps"].items():
            if require_record_disjoint and values["record_id_overlap"] > 0:
                raise SplitGuardError(
                    f"Record leakage in {comparison}: {values['record_id_overlap']}"
                )
            if require_entity_disjoint:
                entity_overlap = values["entity_id_overlap"]
                if entity_overlap is None:
                    raise SplitGuardError(
                        f"Entity IDs unavailable for strict entity-disjoint check in {comparison}"
                    )
                if entity_overlap > 0:
                    raise SplitGuardError(
                        f"Entity leakage in {comparison}: {entity_overlap}"
                    )


def _record_ids(pair_table: list[PairRecord]) -> set[str]:
    ids = set()
    for pair in pair_table:
        ids.add(pair.left_record_id)
        ids.add(pair.right_record_id)
    return ids


def _entity_ids(pair_table: list[PairRecord]) -> set[str] | None:
    ids = set()
    for pair in pair_table:
        if pair.left_entity_id is None or pair.right_entity_id is None:
            return None
        ids.add(pair.left_entity_id)
        ids.add(pair.right_entity_id)
    return ids
