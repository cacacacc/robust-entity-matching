from __future__ import annotations

from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.experiments import (
    TrainingExecutionError,
    load_training_config,
    validate_training_config,
)


class TrainingExecutionTests(unittest.TestCase):
    def test_load_fit_enabled_config(self) -> None:
        config = load_training_config(
            PROJECT_ROOT
            / "configs/experiments/wdc_unseen_logistic_regression_fit.json"
        )

        self.assertTrue(config["fit_allowed"])
        self.assertEqual(config["models_to_run"], ["logistic_regression"])
        self.assertTrue(config["approval"]["approved_by_user"])

    def test_training_config_rejects_unapproved_fit(self) -> None:
        config = {
            "experiment_id": "bad",
            "status": "fit_enabled_approved",
            "approval": {"approved_by_user": False},
            "dataset_config": "configs/datasets/wdc_products_80pair.json",
            "model_config": "configs/models/baseline_traditional.json",
            "processed_root": "data/processed",
            "results_root": "results",
            "splits": {
                "train": "train_small",
                "validation": "valid_small",
                "test": "test_unseen_100un",
            },
            "development_to_test_guards": {
                "require_pair_disjoint": True,
                "require_record_disjoint": True,
                "require_entity_disjoint": True,
            },
            "train_validation_guards": {
                "require_pair_disjoint": True,
                "require_record_disjoint": True,
                "require_entity_disjoint": False,
            },
            "threshold_selection": {
                "split_role": "validation",
                "selection_metric": "f1",
                "candidate_thresholds": {"start": 0.0, "end": 1.0, "step": 0.01},
            },
            "final_test_policy": {
                "test_split_role": "test",
                "use_test_for_threshold_selection": False,
                "use_test_for_model_selection": False,
            },
            "random_seeds": [13],
            "models_to_run": ["logistic_regression"],
            "fit_allowed": True,
        }

        with self.assertRaises(TrainingExecutionError):
            validate_training_config(config)


if __name__ == "__main__":
    unittest.main()
