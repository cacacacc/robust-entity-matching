"""Evaluation metrics and threshold-selection helpers."""

from entity_matching.evaluation.metrics import (
    EvaluationError,
    METRIC_SCHEMA_VERSION,
    apply_threshold,
    binary_confusion_matrix,
    evaluate_binary_scores,
    f1_score,
    precision_score,
    recall_score,
)
from entity_matching.evaluation.thresholds import (
    THRESHOLD_SELECTION_SCHEMA_VERSION,
    select_threshold_on_validation,
)

__all__ = [
    "EvaluationError",
    "METRIC_SCHEMA_VERSION",
    "THRESHOLD_SELECTION_SCHEMA_VERSION",
    "apply_threshold",
    "binary_confusion_matrix",
    "evaluate_binary_scores",
    "f1_score",
    "precision_score",
    "recall_score",
    "select_threshold_on_validation",
]
