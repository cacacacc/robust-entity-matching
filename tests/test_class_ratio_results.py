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
    audit_class_ratio_result_summary,
    load_class_ratio_result_rows,
    write_class_ratio_results_csv,
    write_class_ratio_results_markdown,
)


class ClassRatioResultsTests(unittest.TestCase):
    def test_audit_class_ratio_results_if_present(self) -> None:
        summary = _summary_path()
        if not summary.exists():
            self.skipTest("Class-ratio aggregate summary is not present")

        audit = audit_class_ratio_result_summary(summary)

        self.assertEqual(audit["audit_status"], "passed")
        self.assertEqual(audit["experiment_id"], "wdc_class_ratio_stress_fit_v1")
        self.assertEqual(len(audit["seed_audits"]), 60)
        self.assertEqual(len(audit["ratio_model_audits"]), 4)

    def test_export_class_ratio_result_rows_if_present(self) -> None:
        summary = _summary_path()
        if not summary.exists():
            self.skipTest("Class-ratio aggregate summary is not present")

        rows = load_class_ratio_result_rows(summary)

        self.assertEqual(len(rows), 12)
        self.assertEqual(rows[0]["model_id"], "random_forest")
        self.assertEqual(rows[0]["match_to_non_match_ratio"], "1:4")
        self.assertGreater(rows[0]["test_f1_mean"], 0.0)

    def test_write_class_ratio_result_outputs_if_present(self) -> None:
        summary = _summary_path()
        if not summary.exists():
            self.skipTest("Class-ratio aggregate summary is not present")

        rows = load_class_ratio_result_rows(summary)
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "class_ratio_results.csv"
            markdown_path = Path(directory) / "class_ratio_results.md"

            self.assertEqual(write_class_ratio_results_csv(rows, csv_path), 12)
            self.assertEqual(
                write_class_ratio_results_markdown(rows, markdown_path), 12
            )
            self.assertIn(
                "Class-Ratio Stress-Test Results",
                markdown_path.read_text(encoding="utf-8"),
            )


def _summary_path() -> Path:
    return PROJECT_ROOT / "results/summaries/wdc_class_ratio_stress_fit_v1/aggregate.json"


if __name__ == "__main__":
    unittest.main()
