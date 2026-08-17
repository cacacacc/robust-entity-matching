from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.experiments import (
    build_train_test_ratio_grid_plan,
    check_train_test_ratio_grid_training_readiness,
    load_train_test_ratio_grid_config,
    load_train_test_ratio_grid_training_config,
    train_test_ratio_grid_manifest_rows,
    validate_train_test_ratio_grid_training_config,
    write_train_test_ratio_grid_manifest_csv,
    write_train_test_ratio_grid_manifest_markdown,
)


class TrainTestRatioGridTests(unittest.TestCase):
    def test_load_grid_protocol_config(self) -> None:
        config = load_train_test_ratio_grid_config(_config_path())

        self.assertFalse(config["fit_allowed"])
        grid = config["train_test_ratio_grid"]
        self.assertEqual(grid["train_negative_per_positive_values"], [1, 2, 3, 4])
        self.assertEqual(grid["test_negative_per_positive_values"], [1, 2, 3, 4])

    def test_load_fit_enabled_grid_config(self) -> None:
        config = load_train_test_ratio_grid_training_config(_fit_config_path())

        self.assertTrue(config["fit_allowed"])
        self.assertEqual(config["status"], "fit_enabled_approved")
        self.assertEqual(config["models_to_run"], ["logistic_regression", "random_forest", "svm"])

    def test_validate_fit_enabled_grid_config_shape_from_protocol(self) -> None:
        import json

        with _config_path().open("r", encoding="utf-8") as file:
            config = json.load(file)
        config.update(
            {
                "status": "fit_enabled_approved",
                "approval": {
                    "approved_by_user": True,
                    "approval_date": "2099-01-01",
                    "approval_note": "Unit-test shape only; not a real run config.",
                },
                "models_to_run": ["logistic_regression"],
                "fit_allowed": True,
            }
        )
        config.pop("planned_models")
        config.pop("fit_blockers")

        validate_train_test_ratio_grid_training_config(config)

    def test_grid_plan_counts_if_processed_present(self) -> None:
        if not _processed_path().exists():
            self.skipTest("WDC processed feature tables are not present")

        plan = build_train_test_ratio_grid_plan(_config_path())

        self.assertFalse(plan["fit_allowed"])
        self.assertEqual(plan["planned_fit_count"], 60)
        self.assertEqual(plan["planned_test_evaluation_count"], 240)
        self.assertEqual(
            [ratio["match_to_non_match_ratio"] for ratio in plan["train_ratio_plans"]],
            ["1:1", "1:2", "1:3", "1:4"],
        )
        self.assertEqual(
            [ratio["match_to_non_match_ratio"] for ratio in plan["test_ratio_plans"]],
            ["1:1", "1:2", "1:3", "1:4"],
        )

    def test_grid_manifest_expands_cross_product_if_processed_present(self) -> None:
        if not _processed_path().exists():
            self.skipTest("WDC processed feature tables are not present")

        plan = build_train_test_ratio_grid_plan(_config_path())
        rows = train_test_ratio_grid_manifest_rows(plan)

        self.assertEqual(len(rows), 240)
        self.assertEqual(rows[0]["task_id"], "task_001")
        self.assertEqual(rows[-1]["task_id"], "task_240")
        self.assertTrue(all(row["fit_allowed"] is False for row in rows))
        self.assertIn(
            ("1:3", "1:2"),
            {(row["train_ratio"], row["test_ratio"]) for row in rows},
        )
        selected = [
            row
            for row in rows
            if row["train_ratio"] == "1:3" and row["test_ratio"] == "1:2"
        ][0]
        self.assertEqual(selected["train_total_count"], 2000)
        self.assertEqual(selected["test_total_count"], 1500)

    def test_grid_training_guard_blocks_protocol_only_config_if_processed_present(self) -> None:
        if not _processed_path().exists():
            self.skipTest("WDC processed feature tables are not present")

        readiness = check_train_test_ratio_grid_training_readiness(
            _config_path(),
            model_ids=["logistic_regression"],
        )

        self.assertFalse(readiness["fit_allowed"])
        self.assertFalse(readiness["ready_to_execute_training"])
        self.assertFalse(readiness["training_attempted"])
        self.assertFalse(readiness["writes_files_now"])
        self.assertEqual(readiness["planned_fit_count"], 20)
        self.assertEqual(readiness["planned_test_evaluation_count"], 80)
        self.assertEqual(readiness["blocker_error_type"], "TrainingNotAllowedError")

    def test_write_grid_manifest_outputs_if_processed_present(self) -> None:
        if not _processed_path().exists():
            self.skipTest("WDC processed feature tables are not present")

        plan = build_train_test_ratio_grid_plan(
            _config_path(),
            model_ids=["logistic_regression"],
        )
        rows = train_test_ratio_grid_manifest_rows(plan)
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "grid_manifest.csv"
            markdown_path = Path(directory) / "grid_manifest.md"

            self.assertEqual(write_train_test_ratio_grid_manifest_csv(rows, csv_path), 80)
            self.assertEqual(
                write_train_test_ratio_grid_manifest_markdown(rows, markdown_path),
                80,
            )
            self.assertIn(
                "Train/Test Ratio Grid Manifest",
                markdown_path.read_text(encoding="utf-8"),
            )


def _config_path() -> Path:
    return PROJECT_ROOT / "configs/experiments/wdc_train_test_ratio_grid_protocol.json"


def _fit_config_path() -> Path:
    return PROJECT_ROOT / "configs/experiments/wdc_train_test_ratio_grid_fit.json"


def _processed_path() -> Path:
    return PROJECT_ROOT / "data/processed/wdc_products_80pair/train_small.csv"


if __name__ == "__main__":
    unittest.main()
