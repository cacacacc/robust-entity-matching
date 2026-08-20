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
    load_seen_unseen_comparison_rows,
    write_seen_unseen_comparison_csv,
    write_seen_unseen_comparison_markdown,
)


class SeenUnseenComparisonTests(unittest.TestCase):
    def test_load_seen_unseen_rows_if_results_present(self) -> None:
        seen_summary, unseen_summaries = _summary_paths()
        if not seen_summary.exists() or not all(path.exists() for path in unseen_summaries):
            self.skipTest("Seen/unseen aggregate summaries are not present")

        rows = load_seen_unseen_comparison_rows(seen_summary, unseen_summaries)

        self.assertEqual(len(rows), 3)
        self.assertEqual(
            {row["model_id"] for row in rows},
            {"logistic_regression", "random_forest", "svm"},
        )
        self.assertEqual({row["seen_test_split"] for row in rows}, {"test_seen_000un"})
        self.assertEqual(
            {row["unseen_test_split"] for row in rows},
            {"test_unseen_100un"},
        )
        self.assertTrue(all(row["unseen_minus_seen_f1"] > 0.0 for row in rows))

    def test_write_seen_unseen_outputs_if_results_present(self) -> None:
        seen_summary, unseen_summaries = _summary_paths()
        if not seen_summary.exists() or not all(path.exists() for path in unseen_summaries):
            self.skipTest("Seen/unseen aggregate summaries are not present")

        rows = load_seen_unseen_comparison_rows(seen_summary, unseen_summaries)
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "seen_vs_unseen.csv"
            markdown_path = Path(directory) / "seen_vs_unseen.md"

            self.assertEqual(write_seen_unseen_comparison_csv(rows, csv_path), 3)
            self.assertEqual(
                write_seen_unseen_comparison_markdown(rows, markdown_path),
                3,
            )
            self.assertIn(
                "Seen vs Unseen",
                markdown_path.read_text(encoding="utf-8"),
            )


def _summary_paths() -> tuple[Path, list[Path]]:
    return (
        PROJECT_ROOT / "results/summaries/wdc_seen_baseline_fit_v1/aggregate.json",
        [
            PROJECT_ROOT
            / "results/summaries/wdc_unseen_logistic_regression_fit_v1/aggregate.json",
            PROJECT_ROOT / "results/summaries/wdc_unseen_rf_svm_fit_v1/aggregate.json",
        ],
    )


if __name__ == "__main__":
    unittest.main()
