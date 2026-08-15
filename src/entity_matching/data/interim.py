"""Export normalized pair tables to reproducible interim JSONL files."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
from typing import Any

from entity_matching.data.config import load_dataset_config
from entity_matching.data.pairs import PairRecord, load_pair_table


INTERIM_SCHEMA_VERSION = "pair_table_v1"


def pair_to_dict(pair: PairRecord) -> dict[str, Any]:
    """Serialize a normalized pair record using the interim schema."""

    payload = asdict(pair)
    payload["schema_version"] = INTERIM_SCHEMA_VERSION
    return payload


def write_pair_table_jsonl(pair_table: list[PairRecord], output_path: str | Path) -> int:
    """Write a normalized pair table to JSON Lines and return row count."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        for pair in pair_table:
            file.write(json.dumps(pair_to_dict(pair), ensure_ascii=False, sort_keys=True))
            file.write("\n")
    return len(pair_table)


def export_dataset_interim(
    config_path: str | Path, output_root: str | Path = "data/interim"
) -> dict[str, Any]:
    """Export all configured splits for one dataset to interim JSONL files."""

    config = load_dataset_config(config_path)
    output_base = Path(output_root) / config.dataset_id
    exported: dict[str, Any] = {
        "dataset_id": config.dataset_id,
        "schema_version": INTERIM_SCHEMA_VERSION,
        "output_dir": str(output_base),
        "splits": {},
    }

    for split in config.data["splits"]:
        pair_table = load_pair_table(config_path, split)
        output_path = output_base / f"{split}.jsonl"
        rows_written = write_pair_table_jsonl(pair_table, output_path)
        exported["splits"][split] = {
            "path": str(output_path),
            "rows_written": rows_written,
        }

    return exported

