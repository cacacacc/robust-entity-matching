from __future__ import annotations

from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.evaluation import audit_baseline_result_summary, read_prediction_csv


class ResultAuditTests(unittest.TestCase):
    def test_audit_saved_logistic_regression_result_if_present(self) -> None:
        summary_path = (
            PROJECT_ROOT
            / "results/summaries/wdc_unseen_logistic_regression_fit_v1/aggregate.json"
        )
        if not summary_path.exists():
            self.skipTest("First baseline aggregate result is not present")

        audit = audit_baseline_result_summary(summary_path)

        self.assertEqual(audit["audit_status"], "passed")
        model_audit = audit["model_audits"]["logistic_regression"]
        self.assertTrue(model_audit["aggregate_metrics_match_seed_results"])
        self.assertEqual(model_audit["selected_thresholds"], [0.66] * 5)
        self.assertEqual(len(audit["seed_audits"]), 5)

    def test_read_prediction_csv_if_present(self) -> None:
        prediction_path = (
            PROJECT_ROOT
            / "results/predictions/wdc_unseen_logistic_regression_fit_v1"
            / "logistic_regression/seed_13/test.csv"
        )
        if not prediction_path.exists():
            self.skipTest("First baseline prediction file is not present")

        rows = read_prediction_csv(prediction_path)

        self.assertEqual(len(rows), 4500)
        self.assertEqual({row["split_role"] for row in rows}, {"test"})


if __name__ == "__main__":
    unittest.main()
