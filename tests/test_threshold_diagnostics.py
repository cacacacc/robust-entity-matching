from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.evaluation import (
    average_precision_score,
    load_threshold_diagnostic_rows,
    threshold_curve,
    threshold_grid_pr_auc,
    write_threshold_diagnostics_csv,
    write_threshold_diagnostics_markdown,
)


class ThresholdDiagnosticsTests(unittest.TestCase):
    def test_average_precision_uses_ranked_positive_precision(self) -> None:
        result = average_precision_score([1, 0, 1], [0.9, 0.8, 0.7])

        self.assertAlmostEqual(result, (1.0 + 2.0 / 3.0) / 2.0)

    def test_threshold_curve_and_grid_auc_are_bounded(self) -> None:
        curve = threshold_curve(
            [1, 1, 0, 0],
            [0.9, 0.6, 0.4, 0.2],
            candidate_thresholds=[0.0, 0.5, 1.0],
        )
        auc = threshold_grid_pr_auc(curve)

        self.assertEqual(len(curve), 3)
        self.assertGreaterEqual(auc, 0.0)
        self.assertLessEqual(auc, 1.0)

    def test_load_threshold_diagnostic_rows_if_results_present(self) -> None:
        summary_paths = _summary_paths()
        if not all(path.exists() for path in summary_paths):
            self.skipTest("Baseline aggregate summaries are not present")

        rows = load_threshold_diagnostic_rows(summary_paths)

        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["rank_by_test_average_precision"], 1)
        self.assertGreater(rows[0]["test_average_precision_mean"], 0.0)

    def test_write_threshold_diagnostic_outputs_if_results_present(self) -> None:
        summary_paths = _summary_paths()
        if not all(path.exists() for path in summary_paths):
            self.skipTest("Baseline aggregate summaries are not present")

        rows = load_threshold_diagnostic_rows(summary_paths)
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "threshold_diagnostics.csv"
            markdown_path = Path(directory) / "threshold_diagnostics.md"

            csv_count = write_threshold_diagnostics_csv(rows, csv_path)
            markdown_count = write_threshold_diagnostics_markdown(rows, markdown_path)

            self.assertEqual(csv_count, 3)
            self.assertEqual(markdown_count, 3)
            self.assertTrue(csv_path.exists())
            self.assertIn(
                "Threshold Diagnostics", markdown_path.read_text(encoding="utf-8")
            )


def _summary_paths() -> list[Path]:
    return [
        PROJECT_ROOT
        / "results/summaries/wdc_unseen_logistic_regression_fit_v1/aggregate.json",
        PROJECT_ROOT / "results/summaries/wdc_unseen_rf_svm_fit_v1/aggregate.json",
    ]


if __name__ == "__main__":
    unittest.main()
