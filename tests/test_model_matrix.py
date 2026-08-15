from __future__ import annotations

from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.models import (
    ModelMatrixError,
    load_model_matrix,
    load_model_matrix_bundle,
)
from entity_matching.splitting import build_split_manifest


class ModelMatrixTests(unittest.TestCase):
    def test_load_wdc_model_matrix_if_processed_present(self) -> None:
        config_path = PROJECT_ROOT / "configs/datasets/wdc_products_80pair.json"
        csv_path = PROJECT_ROOT / "data/processed/wdc_products_80pair/train_small.csv"
        if not csv_path.exists():
            self.skipTest("WDC processed feature tables are not present")

        manifest = build_split_manifest(config_path, split_names=["train_small"])
        matrix = load_model_matrix(manifest, "train_small")

        self.assertEqual(matrix.dataset_id, "wdc_products_80pair")
        self.assertEqual(matrix.row_count, 2500)
        self.assertEqual(matrix.feature_count, 24)
        self.assertEqual(len(matrix.X[0]), matrix.feature_count)
        self.assertEqual(matrix.label_counts["1"], 500)

    def test_load_wdc_unseen_bundle_with_strict_guards_if_processed_present(self) -> None:
        config_path = PROJECT_ROOT / "configs/datasets/wdc_products_80pair.json"
        csv_path = PROJECT_ROOT / "data/processed/wdc_products_80pair/test_unseen_100un.csv"
        if not csv_path.exists():
            self.skipTest("WDC processed feature tables are not present")

        bundle = load_model_matrix_bundle(
            str(config_path),
            split_names=["train_small", "test_unseen_100un"],
            require_record_disjoint=True,
            require_entity_disjoint=True,
        )

        self.assertEqual(bundle.dataset_id, "wdc_products_80pair")
        self.assertEqual(bundle.matrices["train_small"].row_count, 2500)
        self.assertEqual(bundle.matrices["test_unseen_100un"].row_count, 4500)
        self.assertEqual(
            bundle.matrices["train_small"].feature_columns,
            bundle.matrices["test_unseen_100un"].feature_columns,
        )

    def test_load_wdc_train_validation_bundle_fails_strict_entity_guard_if_present(self) -> None:
        config_path = PROJECT_ROOT / "configs/datasets/wdc_products_80pair.json"
        csv_path = PROJECT_ROOT / "data/processed/wdc_products_80pair/valid_small.csv"
        if not csv_path.exists():
            self.skipTest("WDC processed feature tables are not present")

        with self.assertRaises(ModelMatrixError):
            load_model_matrix_bundle(
                str(config_path),
                split_names=["train_small", "valid_small"],
                require_entity_disjoint=True,
            )

    def test_abt_buy_bundle_fails_pair_guard_if_processed_present(self) -> None:
        config_path = PROJECT_ROOT / "configs/datasets/comperbench_abt_buy.json"
        csv_path = PROJECT_ROOT / "data/processed/comperbench_abt_buy/train.csv"
        if not csv_path.exists():
            self.skipTest("abt-buy processed feature tables are not present")

        with self.assertRaises(ModelMatrixError):
            load_model_matrix_bundle(str(config_path), split_names=["train", "test"])

    def test_abt_buy_bundle_can_be_loaded_for_diagnostic_preview_if_allowed(self) -> None:
        config_path = PROJECT_ROOT / "configs/datasets/comperbench_abt_buy.json"
        csv_path = PROJECT_ROOT / "data/processed/comperbench_abt_buy/train.csv"
        if not csv_path.exists():
            self.skipTest("abt-buy processed feature tables are not present")

        bundle = load_model_matrix_bundle(
            str(config_path),
            split_names=["train"],
            require_pair_disjoint=False,
        )

        self.assertEqual(bundle.matrices["train"].row_count, 5010)
        self.assertEqual(bundle.matrices["train"].feature_count, 16)


if __name__ == "__main__":
    unittest.main()
