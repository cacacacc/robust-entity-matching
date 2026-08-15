"""Binary-classification metric primitives for entity matching."""

from __future__ import annotations

from typing import Iterable


METRIC_SCHEMA_VERSION = "binary_metrics_v1"


class EvaluationError(ValueError):
    """Raised when metric inputs are invalid."""


def _as_lists(y_true: Iterable[int], values: Iterable[float | int]) -> tuple[list[int], list]:
    true_list = list(y_true)
    value_list = list(values)
    if len(true_list) != len(value_list):
        raise EvaluationError(
            f"Length mismatch: y_true has {len(true_list)}, values has {len(value_list)}"
        )
    if not true_list:
        raise EvaluationError("Metric inputs must not be empty")
    for index, label in enumerate(true_list):
        if label not in (0, 1):
            raise EvaluationError(f"Invalid y_true label at index {index}: {label}")
    return true_list, value_list


def apply_threshold(scores: Iterable[float], threshold: float) -> list[int]:
    """Convert match scores/probabilities into binary predictions."""

    if threshold < 0.0 or threshold > 1.0:
        raise EvaluationError(f"Threshold must be in [0, 1]: {threshold}")
    predictions = []
    for index, score in enumerate(scores):
        if score < 0.0 or score > 1.0:
            raise EvaluationError(f"Score at index {index} is outside [0, 1]: {score}")
        predictions.append(1 if score >= threshold else 0)
    return predictions


def binary_confusion_matrix(y_true: Iterable[int], y_pred: Iterable[int]) -> dict[str, int]:
    """Return binary confusion-matrix counts for positive class 1."""

    true_list, pred_list = _as_lists(y_true, y_pred)
    counts = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}
    for index, (true_label, pred_label) in enumerate(zip(true_list, pred_list)):
        if pred_label not in (0, 1):
            raise EvaluationError(f"Invalid y_pred label at index {index}: {pred_label}")
        if true_label == 1 and pred_label == 1:
            counts["tp"] += 1
        elif true_label == 0 and pred_label == 1:
            counts["fp"] += 1
        elif true_label == 0 and pred_label == 0:
            counts["tn"] += 1
        else:
            counts["fn"] += 1
    return counts


def precision_score(confusion: dict[str, int]) -> float:
    """Return precision for positive class 1."""

    denominator = confusion["tp"] + confusion["fp"]
    if denominator == 0:
        return 0.0
    return confusion["tp"] / denominator


def recall_score(confusion: dict[str, int]) -> float:
    """Return recall for positive class 1."""

    denominator = confusion["tp"] + confusion["fn"]
    if denominator == 0:
        return 0.0
    return confusion["tp"] / denominator


def f1_score(precision: float, recall: float) -> float:
    """Return F1 score from precision and recall."""

    denominator = precision + recall
    if denominator == 0.0:
        return 0.0
    return 2 * precision * recall / denominator


def evaluate_binary_scores(
    y_true: Iterable[int], scores: Iterable[float], threshold: float
) -> dict[str, object]:
    """Evaluate binary scores at a fixed threshold."""

    true_list, score_list = _as_lists(y_true, scores)
    predictions = apply_threshold(score_list, threshold)
    confusion = binary_confusion_matrix(true_list, predictions)
    precision = precision_score(confusion)
    recall = recall_score(confusion)
    f1 = f1_score(precision, recall)
    return {
        "metric_schema_version": METRIC_SCHEMA_VERSION,
        "threshold": threshold,
        "total": len(true_list),
        "positive_count": sum(true_list),
        "negative_count": len(true_list) - sum(true_list),
        "confusion_matrix": confusion,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }
