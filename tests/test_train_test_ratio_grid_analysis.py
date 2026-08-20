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
    load_train_test_ratio_grid_analysis,
    write_best_train_by_test_ratio_csv,
    write_f1_matrix_csv,
    write_test_ratio_sensitivity_csv,
    write_train_test_ratio_grid_analysis_markdown,
)


class TrainTestRatioGridAnalysisTests(unittest.TestCase):
    def test_load_grid_analysis_if_results_present(self) -> None:
        summary = _summary_path()
        if not summary.exists():
            self.skipTest("Train/test ratio grid aggregate summary is not present")

        analysis = load_train_test_ratio_grid_analysis(summary)

        self.assertEqual(len(analysis["f1_matrix_rows"]), 12)
        self.assertEqual(len(analysis["best_train_by_test_ratio_rows"]), 12)
        self.assertEqual(len(analysis["test_ratio_sensitivity_rows"]), 12)
        self.assertTrue(
            all(
                abs(row["recall_drop_1_1_to_1_4"]) < 1e-12
                for row in analysis["test_ratio_sensitivity_rows"]
            )
        )

    def test_write_grid_analysis_outputs_if_results_present(self) -> None:
        summary = _summary_path()
        if not summary.exists():
            self.skipTest("Train/test ratio grid aggregate summary is not present")

        analysis = load_train_test_ratio_grid_analysis(summary)
        with tempfile.TemporaryDirectory() as directory:
            f1_path = Path(directory) / "f1_matrix.csv"
            best_path = Path(directory) / "best_train.csv"
            sensitivity_path = Path(directory) / "sensitivity.csv"
            markdown_path = Path(directory) / "analysis.md"

            self.assertEqual(
                write_f1_matrix_csv(analysis["f1_matrix_rows"], f1_path),
                12,
            )
            self.assertEqual(
                write_best_train_by_test_ratio_csv(
                    analysis["best_train_by_test_ratio_rows"],
                    best_path,
                ),
                12,
            )
            self.assertEqual(
                write_test_ratio_sensitivity_csv(
                    analysis["test_ratio_sensitivity_rows"],
                    sensitivity_path,
                ),
                12,
            )
            self.assertEqual(
                write_train_test_ratio_grid_analysis_markdown(
                    analysis,
                    markdown_path,
                ),
                36,
            )
            self.assertIn(
                "Train/Test Ratio Grid Analysis",
                markdown_path.read_text(encoding="utf-8"),
            )


def _summary_path() -> Path:
    return (
        PROJECT_ROOT
        / "results/summaries/wdc_train_test_ratio_grid_fit_v1/aggregate.json"
    )


if __name__ == "__main__":
    unittest.main()
