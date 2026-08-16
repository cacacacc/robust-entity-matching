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
    load_baseline_comparison_rows,
    write_baseline_comparison_csv,
    write_baseline_comparison_markdown,
)


class BaselineComparisonTests(unittest.TestCase):
    def test_load_baseline_comparison_rows_if_results_present(self) -> None:
        summary_paths = _summary_paths()
        if not all(path.exists() for path in summary_paths):
            self.skipTest("Baseline aggregate summaries are not present")

        rows = load_baseline_comparison_rows(summary_paths)

        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["model_id"], "random_forest")
        self.assertEqual(rows[0]["rank_by_test_f1"], 1)
        self.assertGreater(rows[0]["test_f1_mean"], rows[-1]["test_f1_mean"])

    def test_write_comparison_outputs_to_temp_files_if_results_present(self) -> None:
        summary_paths = _summary_paths()
        if not all(path.exists() for path in summary_paths):
            self.skipTest("Baseline aggregate summaries are not present")

        rows = load_baseline_comparison_rows(summary_paths)
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "comparison.csv"
            markdown_path = Path(directory) / "comparison.md"

            csv_count = write_baseline_comparison_csv(rows, csv_path)
            markdown_count = write_baseline_comparison_markdown(rows, markdown_path)

            self.assertEqual(csv_count, 3)
            self.assertEqual(markdown_count, 3)
            self.assertTrue(csv_path.exists())
            self.assertIn("random_forest", markdown_path.read_text(encoding="utf-8"))


def _summary_paths() -> list[Path]:
    return [
        PROJECT_ROOT
        / "results/summaries/wdc_unseen_logistic_regression_fit_v1/aggregate.json",
        PROJECT_ROOT / "results/summaries/wdc_unseen_rf_svm_fit_v1/aggregate.json",
    ]


if __name__ == "__main__":
    unittest.main()
