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
from entity_matching.evaluation.predictions import (
    RAW_PREDICTION_COLUMNS,
    RAW_PREDICTION_SCHEMA_VERSION,
    PredictionArtifactError,
    prediction_artifact_path,
    summarize_prediction_rows,
    validate_prediction_rows,
    write_prediction_csv,
)

__all__ = [
    "EvaluationError",
    "METRIC_SCHEMA_VERSION",
    "PredictionArtifactError",
    "RAW_PREDICTION_COLUMNS",
    "RAW_PREDICTION_SCHEMA_VERSION",
    "THRESHOLD_SELECTION_SCHEMA_VERSION",
    "apply_threshold",
    "binary_confusion_matrix",
    "evaluate_binary_scores",
    "f1_score",
    "precision_score",
    "prediction_artifact_path",
    "recall_score",
    "select_threshold_on_validation",
    "summarize_prediction_rows",
    "validate_prediction_rows",
    "write_prediction_csv",
]
