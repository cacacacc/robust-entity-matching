from __future__ import annotations

from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.features import export_dataset_feature_tables
from entity_matching.splitting import (
    SplitGuardError,
    assert_no_leakage,
    build_split_guard_report,
    build_split_manifest,
    validate_feature_table_file,
)


class SplitGuardTests(unittest.TestCase):
    def test_build_split_manifest_for_abt_buy_if_processed_present(self) -> None:
        config_path = PROJECT_ROOT / "configs/datasets/comperbench_abt_buy.json"
        csv_path = PROJECT_ROOT / "data/processed/comperbench_abt_buy/train.csv"
        if not csv_path.exists():
            self.skipTest("abt-buy processed feature tables are not present")

        manifest = build_split_manifest(config_path, split_names=["train", "validation"])

        self.assertEqual(manifest.dataset_id, "comperbench_abt_buy")
        self.assertEqual(manifest.splits["train"].row_count, 5010)
        self.assertEqual(manifest.splits["train"].duplicate_pair_id_count, 2)
        self.assertEqual(manifest.splits["validation"].label_counts["1"], 220)

    def test_validate_feature_table_file_for_wdc_if_processed_present(self) -> None:
        csv_path = PROJECT_ROOT / "data/processed/wdc_products_80pair/train_small.csv"
        summary_path = (
            PROJECT_ROOT / "data/processed/wdc_products_80pair/train_small.summary.json"
        )
        if not csv_path.exists():
            self.skipTest("WDC processed feature tables are not present")

        split = validate_feature_table_file(csv_path, summary_path)

        self.assertEqual(split.dataset_id, "wdc_products_80pair")
        self.assertEqual(split.row_count, 2500)

    def test_wdc_unseen_test_guard_passes_if_processed_present(self) -> None:
        config_path = PROJECT_ROOT / "configs/datasets/wdc_products_80pair.json"
        csv_path = PROJECT_ROOT / "data/processed/wdc_products_80pair/test_unseen_100un.csv"
        if not csv_path.exists():
            self.skipTest("WDC processed feature tables are not present")

        report = build_split_guard_report(
            config_path,
            split_names=["train_small", "test_unseen_100un"],
        )

        assert_no_leakage(
            report,
            require_pair_disjoint=True,
            require_record_disjoint=True,
            require_entity_disjoint=True,
        )
        self.assertEqual(
            report["record_entity_overlaps"]["test_unseen_100un__train_small"][
                "entity_id_overlap"
            ],
            0,
        )

    def test_wdc_train_validation_entity_overlap_is_reported_if_processed_present(self) -> None:
        config_path = PROJECT_ROOT / "configs/datasets/wdc_products_80pair.json"
        csv_path = PROJECT_ROOT / "data/processed/wdc_products_80pair/valid_small.csv"
        if not csv_path.exists():
            self.skipTest("WDC processed feature tables are not present")

        report = build_split_guard_report(
            config_path,
            split_names=["train_small", "valid_small"],
        )

        self.assertEqual(
            report["record_entity_overlaps"]["train_small__valid_small"][
                "entity_id_overlap"
            ],
            500,
        )
        with self.assertRaises(SplitGuardError):
            assert_no_leakage(report, require_entity_disjoint=True)

    def test_abt_buy_official_guard_reports_pair_leakage_if_processed_present(self) -> None:
        config_path = PROJECT_ROOT / "configs/datasets/comperbench_abt_buy.json"
        csv_path = PROJECT_ROOT / "data/processed/comperbench_abt_buy/test.csv"
        if not csv_path.exists():
            self.skipTest("abt-buy processed feature tables are not present")

        report = build_split_guard_report(config_path, split_names=["train", "test"])

        self.assertEqual(report["pair_id_overlaps"]["test__train"]["pair_id_overlap"], 1)
        self.assertEqual(
            report["within_split_duplicate_pair_ids"]["train"][
                "duplicate_pair_id_count"
            ],
            2,
        )
        with self.assertRaises(SplitGuardError):
            assert_no_leakage(report, require_pair_disjoint=True)

    def test_abt_buy_strict_entity_guard_fails_when_entity_ids_unavailable(self) -> None:
        config_path = PROJECT_ROOT / "configs/datasets/comperbench_abt_buy.json"
        csv_path = PROJECT_ROOT / "data/processed/comperbench_abt_buy/train.csv"
        if not csv_path.exists():
            self.skipTest("abt-buy processed feature tables are not present")

        report = build_split_guard_report(config_path, split_names=["train", "validation"])

        with self.assertRaises(SplitGuardError):
            assert_no_leakage(report, require_entity_disjoint=True)


if __name__ == "__main__":
    unittest.main()
