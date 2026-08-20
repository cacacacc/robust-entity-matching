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
    load_seen_unseen_error_profile_rows,
    summarize_seen_unseen_error_profiles,
    write_seen_unseen_error_profile_csv,
    write_seen_unseen_error_profile_markdown,
    write_seen_unseen_model_error_profile_csv,
)


class SeenUnseenErrorProfileTests(unittest.TestCase):
    def test_load_all_seed_error_profiles_if_artifacts_present(self) -> None:
        paths = _artifact_paths()
        if not all(path.exists() for path in _required_paths(paths)):
            self.skipTest("Required seen/unseen prediction artifacts or feature tables are not present")

        seed_rows = _load_seed_rows(paths)
        model_rows = summarize_seen_unseen_error_profiles(seed_rows)

        self.assertEqual(len(seed_rows), 15)
        self.assertEqual(len(model_rows), 3)
        self.assertEqual(
            {row["model_id"] for row in model_rows},
            {"logistic_regression", "random_forest", "svm"},
        )
        self.assertTrue(all(row["seed_count"] == 5 for row in model_rows))
        self.assertTrue(
            all(row["unseen_f1_greater_seed_count"] == 5 for row in model_rows)
        )
        self.assertTrue(
            all(row["seen_fp_greater_seed_count"] == 5 for row in model_rows)
        )

    def test_write_all_seed_error_profile_outputs_if_artifacts_present(self) -> None:
        paths = _artifact_paths()
        if not all(path.exists() for path in _required_paths(paths)):
            self.skipTest("Required seen/unseen prediction artifacts or feature tables are not present")

        seed_rows = _load_seed_rows(paths)
        model_rows = summarize_seen_unseen_error_profiles(seed_rows)
        with tempfile.TemporaryDirectory() as directory:
            seed_csv = Path(directory) / "seed.csv"
            model_csv = Path(directory) / "model.csv"
            markdown = Path(directory) / "profile.md"

            self.assertEqual(write_seen_unseen_error_profile_csv(seed_rows, seed_csv), 15)
            self.assertEqual(
                write_seen_unseen_model_error_profile_csv(model_rows, model_csv),
                3,
            )
            self.assertEqual(
                write_seen_unseen_error_profile_markdown(
                    seed_rows,
                    model_rows,
                    markdown,
                ),
                18,
            )
            self.assertIn(
                "Seen/Unseen All-Seed Error Profile",
                markdown.read_text(encoding="utf-8"),
            )


def _load_seed_rows(paths: dict[str, Path]) -> list[dict]:
    return load_seen_unseen_error_profile_rows(
        dataset_config_path=paths["dataset_config"],
        prediction_pairs=_prediction_pairs(paths["results_root"]),
        seen_feature_table_path=paths["seen_features"],
        unseen_feature_table_path=paths["unseen_features"],
    )


def _prediction_pairs(results_root: Path) -> list[dict[str, Path]]:
    seeds = [13, 29, 47, 71, 101]
    unseen_experiment_by_model = {
        "logistic_regression": "wdc_unseen_logistic_regression_fit_v1",
        "random_forest": "wdc_unseen_rf_svm_fit_v1",
        "svm": "wdc_unseen_rf_svm_fit_v1",
    }
    pairs = []
    for model_id, unseen_experiment in unseen_experiment_by_model.items():
        for seed in seeds:
            pairs.append(
                {
                    "seen_prediction_path": results_root
                    / "predictions"
                    / "wdc_seen_baseline_fit_v1"
                    / model_id
                    / f"seed_{seed}"
                    / "test.csv",
                    "unseen_prediction_path": results_root
                    / "predictions"
                    / unseen_experiment
                    / model_id
                    / f"seed_{seed}"
                    / "test.csv",
                }
            )
    return pairs


def _artifact_paths() -> dict[str, Path]:
    return {
        "dataset_config": PROJECT_ROOT / "configs/datasets/wdc_products_80pair.json",
        "results_root": PROJECT_ROOT / "results",
        "seen_features": PROJECT_ROOT / "data/processed/wdc_products_80pair/test_seen_000un.csv",
        "unseen_features": PROJECT_ROOT
        / "data/processed/wdc_products_80pair/test_unseen_100un.csv",
        "seen_raw_data": PROJECT_ROOT
        / "data/raw/wdc_products_sample/80pair/wdcproducts80cc20rnd000un_gs.json.gz",
        "unseen_raw_data": PROJECT_ROOT
        / "data/raw/wdc_products_sample/80pair/wdcproducts80cc20rnd100un_gs.json.gz",
    }


def _required_paths(paths: dict[str, Path]) -> list[Path]:
    return [
        paths["dataset_config"],
        paths["seen_features"],
        paths["unseen_features"],
        paths["seen_raw_data"],
        paths["unseen_raw_data"],
        *[
            prediction_path
            for pair in _prediction_pairs(paths["results_root"])
            for prediction_path in pair.values()
        ],
    ]


if __name__ == "__main__":
    unittest.main()
