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
    audit_train_test_ratio_grid_result_summary,
    load_train_test_ratio_grid_result_rows,
    write_train_test_ratio_grid_results_csv,
    write_train_test_ratio_grid_results_markdown,
)


class TrainTestRatioGridResultsTests(unittest.TestCase):
    def test_audit_grid_results_if_present(self) -> None:
        summary = _summary_path()
        if not summary.exists():
            self.skipTest("Train/test ratio grid aggregate summary is not present")

        audit = audit_train_test_ratio_grid_result_summary(summary)

        self.assertEqual(audit["audit_status"], "passed")
        self.assertEqual(audit["experiment_id"], "wdc_train_test_ratio_grid_fit_v1")
        self.assertEqual(len(audit["seed_audits"]), 240)

    def test_export_grid_result_rows_if_present(self) -> None:
        summary = _summary_path()
        if not summary.exists():
            self.skipTest("Train/test ratio grid aggregate summary is not present")

        rows = load_train_test_ratio_grid_result_rows(summary)

        self.assertEqual(len(rows), 48)
        self.assertEqual(rows[0]["rank_by_test_f1"], 1)
        self.assertGreater(rows[0]["test_f1_mean"], 0.0)

    def test_write_grid_result_outputs_if_present(self) -> None:
        summary = _summary_path()
        if not summary.exists():
            self.skipTest("Train/test ratio grid aggregate summary is not present")

        rows = load_train_test_ratio_grid_result_rows(summary)
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "grid_results.csv"
            markdown_path = Path(directory) / "grid_results.md"

            self.assertEqual(write_train_test_ratio_grid_results_csv(rows, csv_path), 48)
            self.assertEqual(
                write_train_test_ratio_grid_results_markdown(rows, markdown_path),
                48,
            )
            self.assertIn(
                "Train/Test Ratio Grid Results",
                markdown_path.read_text(encoding="utf-8"),
            )


def _summary_path() -> Path:
    return (
        PROJECT_ROOT
        / "results/summaries/wdc_train_test_ratio_grid_fit_v1/aggregate.json"
    )


if __name__ == "__main__":
    unittest.main()
