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
    load_seen_unseen_difficulty_analysis,
    write_feature_difficulty_csv,
    write_seen_unseen_difficulty_markdown,
    write_split_difficulty_summary_csv,
)


class SeenUnseenDifficultyTests(unittest.TestCase):
    def test_load_seen_unseen_difficulty_if_artifacts_present(self) -> None:
        paths = _artifact_paths()
        if not all(path.exists() for path in paths.values()):
            self.skipTest("Required seen/unseen predictions, features, or raw data are not present")

        analysis = _load_analysis(paths)
        summary_rows = analysis["split_summary_rows"]
        seen = _row_by_label(summary_rows, "seen")
        unseen = _row_by_label(summary_rows, "unseen")

        self.assertEqual(analysis["schema_version"], "seen_unseen_difficulty_v1")
        self.assertEqual(len(summary_rows), 2)
        self.assertEqual(seen["positive_count"], 500)
        self.assertEqual(unseen["positive_count"], 500)
        self.assertEqual(seen["negative_count"], 4000)
        self.assertEqual(unseen["negative_count"], 4000)
        self.assertEqual(seen["hard_negative_count"], 3000)
        self.assertEqual(unseen["hard_negative_count"], 3000)
        self.assertGreater(seen["fp"], unseen["fp"])
        self.assertGreater(unseen["f1"], seen["f1"])

    def test_write_seen_unseen_difficulty_outputs_if_artifacts_present(self) -> None:
        paths = _artifact_paths()
        if not all(path.exists() for path in paths.values()):
            self.skipTest("Required seen/unseen predictions, features, or raw data are not present")

        analysis = _load_analysis(paths)
        with tempfile.TemporaryDirectory() as directory:
            summary_path = Path(directory) / "split_difficulty.csv"
            feature_path = Path(directory) / "feature_difficulty.csv"
            markdown_path = Path(directory) / "difficulty.md"

            self.assertEqual(
                write_split_difficulty_summary_csv(
                    analysis["split_summary_rows"],
                    summary_path,
                ),
                2,
            )
            self.assertEqual(
                write_feature_difficulty_csv(
                    analysis["feature_group_rows"],
                    feature_path,
                ),
                12,
            )
            self.assertEqual(
                write_seen_unseen_difficulty_markdown(analysis, markdown_path),
                14,
            )
            self.assertIn(
                "Seen/Unseen Split Difficulty Analysis",
                markdown_path.read_text(encoding="utf-8"),
            )


def _load_analysis(paths: dict[str, Path]) -> dict:
    return load_seen_unseen_difficulty_analysis(
        dataset_config_path=paths["dataset_config"],
        seen_prediction_path=paths["seen_prediction"],
        unseen_prediction_path=paths["unseen_prediction"],
        seen_feature_table_path=paths["seen_features"],
        unseen_feature_table_path=paths["unseen_features"],
    )


def _artifact_paths() -> dict[str, Path]:
    return {
        "dataset_config": PROJECT_ROOT / "configs/datasets/wdc_products_80pair.json",
        "seen_prediction": PROJECT_ROOT
        / "results/predictions/wdc_seen_baseline_fit_v1/random_forest/seed_13/test.csv",
        "unseen_prediction": PROJECT_ROOT
        / "results/predictions/wdc_unseen_rf_svm_fit_v1/random_forest/seed_13/test.csv",
        "seen_features": PROJECT_ROOT / "data/processed/wdc_products_80pair/test_seen_000un.csv",
        "unseen_features": PROJECT_ROOT
        / "data/processed/wdc_products_80pair/test_unseen_100un.csv",
        "seen_raw_data": PROJECT_ROOT
        / "data/raw/wdc_products_sample/80pair/wdcproducts80cc20rnd000un_gs.json.gz",
        "unseen_raw_data": PROJECT_ROOT
        / "data/raw/wdc_products_sample/80pair/wdcproducts80cc20rnd100un_gs.json.gz",
    }


def _row_by_label(rows: list[dict], split_label: str) -> dict:
    return next(row for row in rows if row["split_label"] == split_label)


if __name__ == "__main__":
    unittest.main()
