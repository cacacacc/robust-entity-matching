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
    load_class_ratio_protocol_comparison_rows,
    write_class_ratio_protocol_comparison_csv,
    write_class_ratio_protocol_comparison_markdown,
)


class ClassRatioProtocolComparisonTests(unittest.TestCase):
    def test_load_fixed_vs_matched_rows_if_results_present(self) -> None:
        fixed_summary, matched_summary = _summary_paths()
        if not fixed_summary.exists() or not matched_summary.exists():
            self.skipTest("Class-ratio aggregate summaries are not present")

        rows = load_class_ratio_protocol_comparison_rows(
            fixed_summary, matched_summary
        )

        self.assertEqual(len(rows), 12)
        first = rows[0]
        self.assertEqual(first["match_to_non_match_ratio"], "1:1")
        self.assertEqual(first["model_id"], "logistic_regression")
        self.assertEqual(first["fixed_test_label_counts"], {"0": 4000, "1": 500})
        self.assertEqual(first["matched_test_label_counts"], {"0": 500, "1": 500})
        self.assertGreater(first["delta_test_f1_mean"], 0.0)

    def test_write_fixed_vs_matched_outputs_if_results_present(self) -> None:
        fixed_summary, matched_summary = _summary_paths()
        if not fixed_summary.exists() or not matched_summary.exists():
            self.skipTest("Class-ratio aggregate summaries are not present")

        rows = load_class_ratio_protocol_comparison_rows(
            fixed_summary, matched_summary
        )
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "class_ratio_protocol_comparison.csv"
            markdown_path = Path(directory) / "class_ratio_protocol_comparison.md"

            self.assertEqual(
                write_class_ratio_protocol_comparison_csv(rows, csv_path), 12
            )
            self.assertEqual(
                write_class_ratio_protocol_comparison_markdown(rows, markdown_path),
                12,
            )
            self.assertIn(
                "Fixed-Test vs Matched Train/Test",
                markdown_path.read_text(encoding="utf-8"),
            )


def _summary_paths() -> tuple[Path, Path]:
    return (
        PROJECT_ROOT
        / "results/summaries/wdc_class_ratio_stress_fit_v1/aggregate.json",
        PROJECT_ROOT
        / "results/summaries/wdc_class_ratio_matched_train_test_fit_v1/aggregate.json",
    )


if __name__ == "__main__":
    unittest.main()
