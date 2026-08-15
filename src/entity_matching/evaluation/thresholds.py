"""Validation-only threshold selection helpers."""

from __future__ import annotations

from typing import Iterable

from entity_matching.evaluation.metrics import EvaluationError, evaluate_binary_scores


THRESHOLD_SELECTION_SCHEMA_VERSION = "threshold_selection_v1"


def select_threshold_on_validation(
    y_true: Iterable[int],
    scores: Iterable[float],
    candidate_thresholds: Iterable[float] | None = None,
    *,
    selection_metric: str = "f1",
    split_name: str = "validation",
) -> dict[str, object]:
    """Select a threshold on validation data only."""

    if split_name != "validation":
        raise EvaluationError(
            f"Threshold selection must use validation split, got: {split_name}"
        )
    if selection_metric != "f1":
        raise EvaluationError(f"Unsupported selection metric: {selection_metric}")

    thresholds = list(candidate_thresholds or _default_thresholds())
    if not thresholds:
        raise EvaluationError("At least one candidate threshold is required")

    evaluated = []
    for threshold in thresholds:
        evaluated.append(evaluate_binary_scores(y_true, scores, threshold))

    best = max(
        evaluated,
        key=lambda result: (
            result[selection_metric],
            result["precision"],
            result["recall"],
            -abs(result["threshold"] - 0.5),
        ),
    )
    return {
        "threshold_selection_schema_version": THRESHOLD_SELECTION_SCHEMA_VERSION,
        "selection_split": split_name,
        "selection_metric": selection_metric,
        "selected_threshold": best["threshold"],
        "selected_metric_value": best[selection_metric],
        "selected_metrics": best,
        "candidate_thresholds": thresholds,
        "candidate_results": evaluated,
    }


def _default_thresholds() -> list[float]:
    return [index / 100 for index in range(0, 101)]
