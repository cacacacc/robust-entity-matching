from __future__ import annotations

from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.experiments import (
    ExperimentConfigError,
    baseline_dependency_status,
    load_experiment_config,
    run_experiment_dry_run,
    validate_experiment_config,
)


class ExperimentDryRunTests(unittest.TestCase):
    def test_load_dry_run_config(self) -> None:
        config = load_experiment_config(
            PROJECT_ROOT / "configs/experiments/wdc_unseen_baseline_dry_run.json"
        )

        self.assertEqual(config["status"], "dry_run_only")
        self.assertFalse(config["fit_allowed"])
        self.assertEqual(config["splits"]["train"], "train_small")

    def test_validate_experiment_config_rejects_fit_allowed(self) -> None:
        config = {
            "experiment_id": "bad",
            "status": "dry_run_only",
            "dataset_config": "configs/datasets/wdc_products_80pair.json",
            "model_config": "configs/models/baseline_traditional.json",
            "processed_root": "data/processed",
            "splits": {"train": "train_small", "test": "test_unseen_100un"},
            "guards": {
                "require_pair_disjoint": True,
                "require_record_disjoint": True,
                "require_entity_disjoint": True,
            },
            "fit_allowed": True,
            "fit_blockers": ["blocked"],
        }

        with self.assertRaises(ExperimentConfigError):
            validate_experiment_config(config)

    def test_dependency_status_has_expected_keys(self) -> None:
        status = baseline_dependency_status()

        self.assertIn("sklearn_available", status)
        self.assertIn("numpy_available", status)
        self.assertIn("pandas_available", status)

    def test_run_experiment_dry_run_if_processed_present(self) -> None:
        processed_path = (
            PROJECT_ROOT / "data/processed/wdc_products_80pair/test_unseen_100un.csv"
        )
        if not processed_path.exists():
            self.skipTest("WDC processed feature tables are not present")

        summary = run_experiment_dry_run(
            PROJECT_ROOT / "configs/experiments/wdc_unseen_baseline_dry_run.json"
        )

        self.assertFalse(summary["ready_for_fit"])
        self.assertEqual(
            summary["planned_training_status"],
            "logistic_regression_first_run_completed",
        )
        self.assertEqual(
            summary["matrix_summary"]["splits"]["train_small"]["row_count"], 2500
        )
        self.assertEqual(
            summary["matrix_summary"]["splits"]["test_unseen_100un"]["feature_count"],
            24,
        )


if __name__ == "__main__":
    unittest.main()
