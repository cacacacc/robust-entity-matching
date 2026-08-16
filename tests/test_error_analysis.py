from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.evaluation.error_analysis import (
    analyze_prediction_errors,
    write_error_analysis_json,
    write_error_analysis_markdown,
)


class ErrorAnalysisTests(unittest.TestCase):
    def test_random_forest_seed_13_error_counts_if_artifacts_present(self) -> None:
        paths = _artifact_paths()
        if not all(path.exists() for path in paths.values()):
            self.skipTest("Required RF prediction, feature table, or raw data is not present")

        analysis = analyze_prediction_errors(
            dataset_config_path=paths["dataset_config"],
            split="test_unseen_100un",
            prediction_path=paths["prediction"],
            feature_table_path=paths["features"],
            examples_per_error_type=3,
        )

        self.assertEqual(analysis["schema_version"], "error_analysis_v1")
        self.assertEqual(analysis["model_id"], "random_forest")
        self.assertEqual(analysis["seed"], 13)
        self.assertEqual(
            analysis["confusion_counts"],
            {
                "true_positive": 369,
                "false_positive": 454,
                "true_negative": 3546,
                "false_negative": 131,
            },
        )
        self.assertEqual(
            len(analysis["examples"]["false_positives_highest_score"]), 3
        )
        self.assertEqual(
            len(analysis["examples"]["false_negatives_lowest_score"]), 3
        )

    def test_write_error_analysis_outputs_if_artifacts_present(self) -> None:
        paths = _artifact_paths()
        if not all(path.exists() for path in paths.values()):
            self.skipTest("Required RF prediction, feature table, or raw data is not present")

        analysis = analyze_prediction_errors(
            dataset_config_path=paths["dataset_config"],
            split="test_unseen_100un",
            prediction_path=paths["prediction"],
            feature_table_path=paths["features"],
            examples_per_error_type=1,
        )
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "error_analysis.json"
            markdown_path = Path(directory) / "error_analysis.md"

            write_error_analysis_json(analysis, json_path)
            write_error_analysis_markdown(analysis, markdown_path)

            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())
            self.assertIn("False Positives", markdown_path.read_text(encoding="utf-8"))


def _artifact_paths() -> dict[str, Path]:
    return {
        "dataset_config": PROJECT_ROOT / "configs/datasets/wdc_products_80pair.json",
        "prediction": PROJECT_ROOT
        / "results/predictions/wdc_unseen_rf_svm_fit_v1/random_forest/seed_13/test.csv",
        "features": PROJECT_ROOT / "data/processed/wdc_products_80pair/test_unseen_100un.csv",
        "raw_data": PROJECT_ROOT
        / "data/raw/wdc_products_sample/80pair/wdcproducts80cc20rnd100un_gs.json.gz",
    }


if __name__ == "__main__":
    unittest.main()
