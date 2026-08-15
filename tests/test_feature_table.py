from __future__ import annotations

import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.features import (
    FEATURE_TABLE_SCHEMA_VERSION,
    FeatureTableError,
    build_feature_row,
    export_dataset_feature_tables,
    export_feature_table,
    validate_feature_rows,
)


def _pair_payload(pair_id: str, label: int) -> dict[str, object]:
    return {
        "schema_version": "pair_table_v1",
        "dataset_id": "toy_dataset",
        "split": "train",
        "pair_id": pair_id,
        "left_record_id": f"left-{pair_id}",
        "right_record_id": f"right-{pair_id}",
        "left_entity_id": None,
        "right_entity_id": None,
        "label": label,
        "left_attributes": {"name": "Sony Camera 10X", "price": "549.00"},
        "right_attributes": {"name": "Sony Camcorder 10X", "price": "549.00"},
        "is_hard_negative": None,
    }


class FeatureTableTests(unittest.TestCase):
    def test_build_feature_row_flattens_metadata_and_features(self) -> None:
        row = build_feature_row(_pair_payload("p1", 1))

        self.assertEqual(row["dataset_id"], "toy_dataset")
        self.assertEqual(row["split"], "train")
        self.assertEqual(row["pair_id"], "p1")
        self.assertEqual(row["label"], 1)
        self.assertEqual(row["attr_price_exact_match"], 1.0)
        self.assertIn("combined_token_jaccard", row)

    def test_validate_feature_rows_rejects_inconsistent_columns(self) -> None:
        row = build_feature_row(_pair_payload("p1", 1))
        broken = dict(row)
        broken.pop("combined_token_jaccard")

        with self.assertRaises(FeatureTableError):
            validate_feature_rows([row, broken])

    def test_export_feature_table_writes_csv_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            interim_path = temp_path / "input.jsonl"
            output_path = temp_path / "features.csv"
            with interim_path.open("w", encoding="utf-8", newline="\n") as file:
                file.write(json.dumps(_pair_payload("p1", 1)) + "\n")
                file.write(json.dumps(_pair_payload("p2", 0)) + "\n")

            summary = export_feature_table(interim_path, output_path)

            self.assertEqual(summary["schema_version"], FEATURE_TABLE_SCHEMA_VERSION)
            self.assertEqual(summary["row_count"], 2)
            self.assertTrue(output_path.is_file())
            self.assertTrue(Path(summary["summary_path"]).is_file())

            with output_path.open("r", encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["pair_id"], "p1")
            self.assertIn("combined_edit_similarity", rows[0])

    def test_export_dataset_feature_tables_to_temp_dir_if_interim_present(self) -> None:
        config_path = PROJECT_ROOT / "configs/datasets/comperbench_abt_buy.json"
        interim_path = PROJECT_ROOT / "data/interim/comperbench_abt_buy/train.jsonl"
        if not interim_path.exists():
            self.skipTest("abt-buy interim files are not present")

        with tempfile.TemporaryDirectory() as temp_dir:
            summary = export_dataset_feature_tables(config_path, output_root=temp_dir)

            train_summary = summary["splits"]["train"]
            self.assertEqual(train_summary["row_count"], 5010)
            self.assertEqual(train_summary["label_counts"]["1"], 764)
            self.assertTrue(Path(train_summary["path"]).is_file())


if __name__ == "__main__":
    unittest.main()
