from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.data import (
    INTERIM_SCHEMA_VERSION,
    audit_dataset,
    export_dataset_interim,
    load_dataset_config,
    load_pair_table,
    pair_to_dict,
    report_dataset_quality,
    summarize_pair_table,
)


class DatasetConfigTests(unittest.TestCase):
    def test_load_wdc_config(self) -> None:
        config = load_dataset_config(PROJECT_ROOT / "configs/datasets/wdc_products_80pair.json")
        self.assertEqual(config.dataset_id, "wdc_products_80pair")
        self.assertIn("label", config.data["schema"])

    def test_load_abt_buy_config(self) -> None:
        config = load_dataset_config(PROJECT_ROOT / "configs/datasets/comperbench_abt_buy.json")
        self.assertEqual(config.dataset_id, "comperbench_abt_buy")
        self.assertEqual(config.data["schema"]["label"], "matching")


class RawDatasetValidationTests(unittest.TestCase):
    def test_validate_wdc_products_raw_files_if_present(self) -> None:
        config_path = PROJECT_ROOT / "configs/datasets/wdc_products_80pair.json"
        raw_path = PROJECT_ROOT / "data/raw/wdc_products_sample/80pair"
        if not raw_path.exists():
            self.skipTest("WDC raw audit files are not present")

        summary = audit_dataset(config_path)
        self.assertEqual(summary["splits"]["train_small"]["total_pairs"], 2500)
        self.assertEqual(summary["splits"]["test_unseen_100un"]["label_counts"]["1"], 500)

    def test_validate_abt_buy_raw_files_if_present(self) -> None:
        config_path = PROJECT_ROOT / "configs/datasets/comperbench_abt_buy.json"
        raw_path = PROJECT_ROOT / "data/raw/comperbench_abt_buy/gs_train.csv"
        if not raw_path.exists():
            self.skipTest("abt-buy raw audit files are not present")

        summary = audit_dataset(config_path)
        self.assertEqual(summary["splits"]["train"]["total_pairs"], 5010)
        self.assertEqual(summary["records"]["abt_records"], 1081)


class NormalizedPairTableTests(unittest.TestCase):
    def test_load_wdc_normalized_pair_table_if_present(self) -> None:
        config_path = PROJECT_ROOT / "configs/datasets/wdc_products_80pair.json"
        raw_path = PROJECT_ROOT / "data/raw/wdc_products_sample/80pair"
        if not raw_path.exists():
            self.skipTest("WDC raw audit files are not present")

        pairs = load_pair_table(config_path, "train_small")
        summary = summarize_pair_table(pairs)
        self.assertEqual(summary["total_pairs"], 2500)
        self.assertEqual(summary["label_counts"]["1"], 500)
        self.assertIsNotNone(pairs[0].left_entity_id)
        self.assertIsNotNone(pairs[0].is_hard_negative)

    def test_load_abt_buy_normalized_pair_table_if_present(self) -> None:
        config_path = PROJECT_ROOT / "configs/datasets/comperbench_abt_buy.json"
        raw_path = PROJECT_ROOT / "data/raw/comperbench_abt_buy/gs_train.csv"
        if not raw_path.exists():
            self.skipTest("abt-buy raw audit files are not present")

        pairs = load_pair_table(config_path, "train")
        summary = summarize_pair_table(pairs)
        self.assertEqual(summary["total_pairs"], 5010)
        self.assertEqual(summary["label_counts"]["1"], 764)
        self.assertIsNone(pairs[0].left_entity_id)
        self.assertIn("name", pairs[0].left_attributes)


class DataQualityReportTests(unittest.TestCase):
    def test_report_wdc_quality_if_present(self) -> None:
        config_path = PROJECT_ROOT / "configs/datasets/wdc_products_80pair.json"
        raw_path = PROJECT_ROOT / "data/raw/wdc_products_sample/80pair"
        if not raw_path.exists():
            self.skipTest("WDC raw audit files are not present")

        report = report_dataset_quality(config_path)
        self.assertEqual(report["dataset_id"], "wdc_products_80pair")
        self.assertEqual(
            report["split_reports"]["test_unseen_100un"]["total_pairs"], 4500
        )
        self.assertEqual(
            report["split_overlaps"]["train_small__test_unseen_100un"][
                "entity_id_overlap"
            ],
            0,
        )

    def test_report_abt_buy_quality_if_present(self) -> None:
        config_path = PROJECT_ROOT / "configs/datasets/comperbench_abt_buy.json"
        raw_path = PROJECT_ROOT / "data/raw/comperbench_abt_buy/gs_train.csv"
        if not raw_path.exists():
            self.skipTest("abt-buy raw audit files are not present")

        report = report_dataset_quality(config_path)
        self.assertEqual(report["dataset_id"], "comperbench_abt_buy")
        self.assertEqual(report["split_reports"]["train"]["total_pairs"], 5010)
        self.assertEqual(
            report["split_overlaps"]["train__test"]["pair_id_overlap"], 1
        )


class InterimExportTests(unittest.TestCase):
    def test_pair_to_dict_has_schema_version(self) -> None:
        config_path = PROJECT_ROOT / "configs/datasets/comperbench_abt_buy.json"
        raw_path = PROJECT_ROOT / "data/raw/comperbench_abt_buy/gs_train.csv"
        if not raw_path.exists():
            self.skipTest("abt-buy raw audit files are not present")

        pair = load_pair_table(config_path, "train")[0]
        payload = pair_to_dict(pair)
        self.assertEqual(payload["schema_version"], INTERIM_SCHEMA_VERSION)
        self.assertIn("left_attributes", payload)

    def test_export_dataset_interim_to_temp_dir_if_present(self) -> None:
        config_path = PROJECT_ROOT / "configs/datasets/comperbench_abt_buy.json"
        raw_path = PROJECT_ROOT / "data/raw/comperbench_abt_buy/gs_train.csv"
        if not raw_path.exists():
            self.skipTest("abt-buy raw audit files are not present")

        with tempfile.TemporaryDirectory() as temp_dir:
            summary = export_dataset_interim(config_path, temp_dir)
            train_path = Path(summary["splits"]["train"]["path"])
            self.assertTrue(train_path.is_file())
            self.assertEqual(summary["splits"]["train"]["rows_written"], 5010)


if __name__ == "__main__":
    unittest.main()
