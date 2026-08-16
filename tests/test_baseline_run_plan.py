from __future__ import annotations

from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.experiments import build_baseline_run_plan


class BaselineRunPlanTests(unittest.TestCase):
    def test_build_baseline_run_plan_if_processed_present(self) -> None:
        processed_path = (
            PROJECT_ROOT / "data/processed/wdc_products_80pair/test_unseen_100un.csv"
        )
        if not processed_path.exists():
            self.skipTest("WDC processed feature tables are not present")

        plan = build_baseline_run_plan(
            PROJECT_ROOT / "configs/experiments/wdc_unseen_baseline_protocol.json",
            model_ids=["logistic_regression"],
        )

        self.assertFalse(plan["fit_allowed"])
        self.assertFalse(plan["ready_to_execute_training"])
        self.assertEqual(plan["splits"]["validation"], "valid_small")
        self.assertEqual(plan["matrix_summary"]["splits"]["train"]["row_count"], 2500)
        self.assertEqual(plan["matrix_summary"]["splits"]["test"]["row_count"], 4500)
        self.assertFalse(plan["models"][0]["estimators"][0]["estimator"]["is_fitted"])
        self.assertFalse(plan["artifact_plan"]["writes_files_now"])
        self.assertIn(
            "validation.csv",
            plan["artifact_plan"]["raw_prediction_paths"]["logistic_regression"]["13"][
                "validation"
            ],
        )


if __name__ == "__main__":
    unittest.main()
