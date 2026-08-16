from __future__ import annotations

from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.experiments import TrainingNotAllowedError, assert_fit_allowed_from_config
from entity_matching.models import (
    describe_estimator,
    get_model_definition,
    instantiate_model_from_config,
    load_model_config,
)


class ModelFactoryTests(unittest.TestCase):
    def test_load_model_config(self) -> None:
        config = load_model_config(PROJECT_ROOT / "configs/models/baseline_traditional.json")

        self.assertEqual(config["training_status"], "not_started")
        self.assertEqual(len(config["models"]), 3)

    def test_instantiate_logistic_regression_without_fitting(self) -> None:
        estimator = instantiate_model_from_config(
            PROJECT_ROOT / "configs/models/baseline_traditional.json",
            "logistic_regression",
            random_seed=13,
        )
        description = describe_estimator(estimator)

        self.assertEqual(description["class"], "LogisticRegression")
        self.assertFalse(description["is_fitted"])
        self.assertEqual(description["parameters"]["class_weight"], "balanced")

    def test_instantiate_seeded_models_without_fitting(self) -> None:
        config_path = PROJECT_ROOT / "configs/models/baseline_traditional.json"

        random_forest = instantiate_model_from_config(
            config_path, "random_forest", random_seed=29
        )
        svm = instantiate_model_from_config(config_path, "svm", random_seed=29)

        self.assertEqual(random_forest.get_params()["random_state"], 29)
        self.assertEqual(svm.get_params()["random_state"], 29)
        self.assertFalse(describe_estimator(random_forest)["is_fitted"])
        self.assertFalse(describe_estimator(svm)["is_fitted"])

    def test_get_model_definition_rejects_unknown_model(self) -> None:
        config = load_model_config(PROJECT_ROOT / "configs/models/baseline_traditional.json")

        with self.assertRaises(Exception):
            get_model_definition(config, "unknown")

    def test_training_guard_rejects_dry_run_config(self) -> None:
        with self.assertRaises(TrainingNotAllowedError):
            assert_fit_allowed_from_config(
                PROJECT_ROOT / "configs/experiments/wdc_unseen_baseline_dry_run.json"
            )


if __name__ == "__main__":
    unittest.main()
