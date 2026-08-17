from __future__ import annotations

from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.experiments import (
    build_class_ratio_run_plan,
    build_sampled_training_matrix,
    class_ratio_execution_manifest_rows,
    class_ratio_plan_rows,
    load_class_ratio_protocol_config,
    write_class_ratio_execution_manifest_csv,
    write_class_ratio_execution_manifest_markdown,
    write_class_ratio_plan_csv,
    write_class_ratio_plan_markdown,
)
from entity_matching.models import ModelMatrix


class ClassRatioPlanTests(unittest.TestCase):
    def test_build_sampled_training_matrix_uses_all_positives_and_seeded_negatives(self) -> None:
        matrix = ModelMatrix(
            dataset_id="toy",
            split="train",
            pair_ids=["p1", "n1", "p2", "n2", "n3", "n4"],
            y=[1, 0, 1, 0, 0, 0],
            X=[
                [1.0],
                [0.1],
                [0.9],
                [0.2],
                [0.3],
                [0.4],
            ],
            feature_columns=["score_like_feature"],
            label_counts={"0": 4, "1": 2},
        )

        sampled = build_sampled_training_matrix(
            matrix,
            negatives_per_positive=1,
            seed=13,
        )
        sampled_again = build_sampled_training_matrix(
            matrix,
            negatives_per_positive=1,
            seed=13,
        )

        self.assertEqual(sampled.row_count, 4)
        self.assertEqual(sampled.label_counts, {"0": 2, "1": 2})
        self.assertEqual(sampled.feature_columns, matrix.feature_columns)
        self.assertEqual(sampled.pair_ids, sampled_again.pair_ids)
        self.assertIn("p1", sampled.pair_ids)
        self.assertIn("p2", sampled.pair_ids)
        self.assertEqual(sampled.split, "train__match_1_nonmatch_1")

    def test_build_sampled_training_matrix_rejects_infeasible_ratio(self) -> None:
        matrix = ModelMatrix(
            dataset_id="toy",
            split="train",
            pair_ids=["p1", "n1"],
            y=[1, 0],
            X=[[1.0], [0.0]],
            feature_columns=["feature"],
            label_counts={"0": 1, "1": 1},
        )

        with self.assertRaises(ValueError):
            build_sampled_training_matrix(
                matrix,
                negatives_per_positive=2,
                seed=13,
            )

    def test_load_class_ratio_protocol_includes_one_to_three(self) -> None:
        config = load_class_ratio_protocol_config(_config_path())

        self.assertFalse(config["fit_allowed"])
        self.assertEqual(
            config["class_ratio_stress_test"]["negative_per_positive_values"],
            [1, 2, 3, 4],
        )

    def test_build_class_ratio_run_plan_if_processed_present(self) -> None:
        processed_path = (
            PROJECT_ROOT / "data/processed/wdc_products_80pair/train_small.csv"
        )
        if not processed_path.exists():
            self.skipTest("WDC processed feature tables are not present")

        plan = build_class_ratio_run_plan(
            _config_path(),
            model_ids=["logistic_regression"],
        )

        self.assertFalse(plan["fit_allowed"])
        self.assertFalse(plan["ready_to_execute_training"])
        self.assertEqual(
            [ratio["match_to_non_match_ratio"] for ratio in plan["ratio_plans"]],
            ["1:1", "1:2", "1:3", "1:4"],
        )
        one_to_three = plan["ratio_plans"][2]
        self.assertEqual(one_to_three["positive_count"], 500)
        self.assertEqual(one_to_three["negative_count"], 1500)
        self.assertEqual(one_to_three["total_count"], 2000)
        self.assertEqual(len(one_to_three["seed_plans"]), 5)
        self.assertFalse(plan["artifact_plan"]["writes_files_now"])
        self.assertFalse(plan["artifact_plan"]["writes_sampled_training_tables_now"])
        seed_plan = one_to_three["seed_plans"][0]
        self.assertEqual(seed_plan["sampled_split"], "train_small__match_1_nonmatch_3")
        self.assertEqual(seed_plan["sampled_feature_count"], 24)

    def test_build_sampled_training_matrix_for_real_one_to_three_if_processed_present(self) -> None:
        processed_path = (
            PROJECT_ROOT / "data/processed/wdc_products_80pair/train_small.csv"
        )
        if not processed_path.exists():
            self.skipTest("WDC processed feature tables are not present")

        from entity_matching.splitting import build_split_manifest
        from entity_matching.models import load_model_matrix

        manifest = build_split_manifest(
            PROJECT_ROOT / "configs/datasets/wdc_products_80pair.json",
            processed_root=PROJECT_ROOT / "data/processed",
            split_names=["train_small"],
        )
        train_matrix = load_model_matrix(manifest, "train_small")
        sampled = build_sampled_training_matrix(
            train_matrix,
            negatives_per_positive=3,
            seed=13,
        )

        self.assertEqual(sampled.row_count, 2000)
        self.assertEqual(sampled.label_counts, {"0": 1500, "1": 500})
        self.assertEqual(sampled.feature_count, 24)
        self.assertEqual(len(set(sampled.pair_ids)), sampled.row_count)

    def test_write_class_ratio_report_outputs_if_processed_present(self) -> None:
        processed_path = (
            PROJECT_ROOT / "data/processed/wdc_products_80pair/train_small.csv"
        )
        if not processed_path.exists():
            self.skipTest("WDC processed feature tables are not present")

        plan = build_class_ratio_run_plan(
            _config_path(),
            model_ids=["logistic_regression"],
        )
        rows = class_ratio_plan_rows(plan)

        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "class_ratio_plan.csv"
            markdown_path = Path(directory) / "class_ratio_plan.md"

            self.assertEqual(write_class_ratio_plan_csv(rows, csv_path), 4)
            self.assertEqual(write_class_ratio_plan_markdown(rows, markdown_path), 4)
            self.assertIn("1:3", markdown_path.read_text(encoding="utf-8"))

    def test_execution_manifest_rows_expand_ratio_model_seed_grid_if_processed_present(self) -> None:
        processed_path = (
            PROJECT_ROOT / "data/processed/wdc_products_80pair/train_small.csv"
        )
        if not processed_path.exists():
            self.skipTest("WDC processed feature tables are not present")

        plan = build_class_ratio_run_plan(_config_path())
        rows = class_ratio_execution_manifest_rows(plan)

        self.assertEqual(len(rows), 60)
        self.assertEqual(rows[0]["task_id"], "task_001")
        self.assertEqual(rows[-1]["task_id"], "task_060")
        self.assertTrue(all(row["fit_allowed"] is False for row in rows))
        self.assertTrue(all(row["writes_files_now"] is False for row in rows))
        self.assertEqual(
            {row["match_to_non_match_ratio"] for row in rows},
            {"1:1", "1:2", "1:3", "1:4"},
        )
        self.assertEqual(
            {row["model_id"] for row in rows},
            {"logistic_regression", "random_forest", "svm"},
        )

    def test_write_execution_manifest_outputs_if_processed_present(self) -> None:
        processed_path = (
            PROJECT_ROOT / "data/processed/wdc_products_80pair/train_small.csv"
        )
        if not processed_path.exists():
            self.skipTest("WDC processed feature tables are not present")

        plan = build_class_ratio_run_plan(
            _config_path(),
            model_ids=["logistic_regression"],
        )
        rows = class_ratio_execution_manifest_rows(plan)

        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "manifest.csv"
            markdown_path = Path(directory) / "manifest.md"

            self.assertEqual(write_class_ratio_execution_manifest_csv(rows, csv_path), 20)
            self.assertEqual(
                write_class_ratio_execution_manifest_markdown(rows, markdown_path),
                20,
            )
            self.assertIn(
                "Class-Ratio Execution Manifest",
                markdown_path.read_text(encoding="utf-8"),
            )


def _config_path() -> Path:
    return PROJECT_ROOT / "configs/experiments/wdc_class_ratio_stress_protocol.json"


if __name__ == "__main__":
    unittest.main()
