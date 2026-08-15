from __future__ import annotations

from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.evaluation import (
    EvaluationError,
    apply_threshold,
    binary_confusion_matrix,
    evaluate_binary_scores,
    f1_score,
    precision_score,
    recall_score,
    select_threshold_on_validation,
)


class EvaluationMetricTests(unittest.TestCase):
    def test_apply_threshold_uses_greater_than_or_equal(self) -> None:
        self.assertEqual(apply_threshold([0.2, 0.5, 0.8], 0.5), [0, 1, 1])

    def test_apply_threshold_rejects_invalid_scores(self) -> None:
        with self.assertRaises(EvaluationError):
            apply_threshold([1.2], 0.5)
        with self.assertRaises(EvaluationError):
            apply_threshold([0.5], -0.1)

    def test_binary_confusion_matrix_counts_positive_class(self) -> None:
        confusion = binary_confusion_matrix([1, 1, 0, 0], [1, 0, 1, 0])
        self.assertEqual(confusion, {"tp": 1, "fp": 1, "tn": 1, "fn": 1})

    def test_precision_recall_f1_handle_zero_denominators(self) -> None:
        confusion = {"tp": 0, "fp": 0, "tn": 3, "fn": 2}
        precision = precision_score(confusion)
        recall = recall_score(confusion)
        self.assertEqual(precision, 0.0)
        self.assertEqual(recall, 0.0)
        self.assertEqual(f1_score(precision, recall), 0.0)

    def test_evaluate_binary_scores_returns_metrics(self) -> None:
        result = evaluate_binary_scores([1, 1, 0, 0], [0.9, 0.6, 0.4, 0.2], 0.5)
        self.assertEqual(result["confusion_matrix"], {"tp": 2, "fp": 0, "tn": 2, "fn": 0})
        self.assertEqual(result["precision"], 1.0)
        self.assertEqual(result["recall"], 1.0)
        self.assertEqual(result["f1"], 1.0)

    def test_evaluate_binary_scores_rejects_length_mismatch(self) -> None:
        with self.assertRaises(EvaluationError):
            evaluate_binary_scores([1], [0.8, 0.2], 0.5)

    def test_select_threshold_on_validation_chooses_best_f1(self) -> None:
        result = select_threshold_on_validation(
            [1, 1, 0, 0],
            [0.9, 0.6, 0.4, 0.2],
            candidate_thresholds=[0.3, 0.5, 0.7],
            split_name="validation",
        )
        self.assertEqual(result["selection_split"], "validation")
        self.assertEqual(result["selected_threshold"], 0.5)
        self.assertEqual(result["selected_metric_value"], 1.0)

    def test_select_threshold_refuses_test_split(self) -> None:
        with self.assertRaises(EvaluationError):
            select_threshold_on_validation(
                [1, 0],
                [0.8, 0.2],
                candidate_thresholds=[0.5],
                split_name="test",
            )


if __name__ == "__main__":
    unittest.main()
