from __future__ import annotations

from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.experiments import (
    ExperimentProtocolError,
    load_protocol_config,
    validate_protocol_config,
    validate_protocol_guards,
)


class ExperimentProtocolTests(unittest.TestCase):
    def test_load_protocol_config(self) -> None:
        config = load_protocol_config(
            PROJECT_ROOT / "configs/experiments/wdc_unseen_baseline_protocol.json"
        )

        self.assertEqual(config["status"], "protocol_locked_no_fit")
        self.assertEqual(config["splits"]["validation"], "valid_small")
        self.assertFalse(config["fit_allowed"])

    def test_threshold_selection_must_use_validation(self) -> None:
        config = {
            "experiment_id": "bad",
            "status": "protocol_locked_no_fit",
            "dataset_config": "configs/datasets/wdc_products_80pair.json",
            "model_config": "configs/models/baseline_traditional.json",
            "processed_root": "data/processed",
            "splits": {
                "train": "train_small",
                "validation": "valid_small",
                "test": "test_unseen_100un",
            },
            "development_to_test_guards": {
                "require_pair_disjoint": True,
                "require_record_disjoint": True,
                "require_entity_disjoint": True,
            },
            "train_validation_guards": {
                "require_pair_disjoint": True,
                "require_record_disjoint": True,
                "require_entity_disjoint": False,
            },
            "threshold_selection": {
                "split_role": "test",
                "selection_metric": "f1",
                "candidate_thresholds": {"start": 0.0, "end": 1.0, "step": 0.01},
            },
            "final_test_policy": {
                "test_split_role": "test",
                "use_test_for_threshold_selection": False,
                "use_test_for_model_selection": False,
            },
            "random_seeds": [13],
            "fit_allowed": False,
            "fit_blockers": ["blocked"],
        }

        with self.assertRaises(ExperimentProtocolError):
            validate_protocol_config(config)

    def test_validate_protocol_guards_if_processed_present(self) -> None:
        processed_path = (
            PROJECT_ROOT / "data/processed/wdc_products_80pair/test_unseen_100un.csv"
        )
        if not processed_path.exists():
            self.skipTest("WDC processed feature tables are not present")

        summary = validate_protocol_guards(
            PROJECT_ROOT / "configs/experiments/wdc_unseen_baseline_protocol.json"
        )

        self.assertFalse(summary["fit_allowed"])
        self.assertFalse(summary["protocol_ready_for_fit_config"])
        self.assertEqual(summary["random_seeds"], [13, 29, 47, 71, 101])
        self.assertEqual(
            summary["train_validation_guard_report"]["record_entity_overlaps"][
                "train_small__valid_small"
            ]["entity_id_overlap"],
            500,
        )
        self.assertEqual(
            summary["development_to_test_guard_reports"]["validation_to_test"][
                "record_entity_overlaps"
            ]["test_unseen_100un__valid_small"]["entity_id_overlap"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
