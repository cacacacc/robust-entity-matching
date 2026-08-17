from __future__ import annotations

from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.experiments import (
    check_class_ratio_training_readiness,
    run_approved_class_ratio_training,
    validate_class_ratio_training_config,
)
from entity_matching.experiments.training_guard import TrainingNotAllowedError


class ClassRatioTrainingGuardTests(unittest.TestCase):
    def test_readiness_is_blocked_for_protocol_only_config(self) -> None:
        processed_path = (
            PROJECT_ROOT / "data/processed/wdc_products_80pair/train_small.csv"
        )
        if not processed_path.exists():
            self.skipTest("WDC processed feature tables are not present")

        readiness = check_class_ratio_training_readiness(
            _config_path(),
            model_ids=["logistic_regression"],
        )

        self.assertFalse(readiness["fit_allowed"])
        self.assertFalse(readiness["ready_to_execute_training"])
        self.assertFalse(readiness["training_attempted"])
        self.assertFalse(readiness["writes_files_now"])
        self.assertEqual(readiness["ratios"], ["1:1", "1:2", "1:3", "1:4"])
        self.assertEqual(readiness["models"], ["logistic_regression"])
        self.assertEqual(readiness["blocker_error_type"], "TrainingNotAllowedError")

    def test_runner_rejects_protocol_only_config_before_training(self) -> None:
        with self.assertRaises(TrainingNotAllowedError):
            run_approved_class_ratio_training(_config_path())

    def test_validate_fit_enabled_class_ratio_config_shape(self) -> None:
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

        validate_class_ratio_training_config(config)

    def test_validate_matched_train_test_ratio_config_shape(self) -> None:
        import json

        config_path = (
            PROJECT_ROOT
            / "configs/experiments/wdc_class_ratio_matched_train_test_fit.json"
        )
        with config_path.open("r", encoding="utf-8") as file:
            config = json.load(file)

        validate_class_ratio_training_config(config)
        self.assertEqual(
            config["class_ratio_stress_test"]["test_negative_per_positive_policy"],
            "match_training_ratio",
        )


def _config_path() -> Path:
    return PROJECT_ROOT / "configs/experiments/wdc_class_ratio_stress_protocol.json"


if __name__ == "__main__":
    unittest.main()
