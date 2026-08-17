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
    read_prediction_csv,
    summarize_prediction_rows,
    validate_prediction_rows,
    write_prediction_csv,
)
from entity_matching.evaluation.result_audit import (
    ResultAuditError,
    audit_baseline_result_summary,
)
from entity_matching.evaluation.comparison import (
    BASELINE_COMPARISON_COLUMNS,
    BaselineComparisonError,
    load_baseline_comparison_rows,
    write_baseline_comparison_csv,
    write_baseline_comparison_markdown,
)
from entity_matching.evaluation.error_analysis import (
    ERROR_ANALYSIS_SCHEMA_VERSION,
    ErrorAnalysisError,
    analyze_prediction_errors,
    write_error_analysis_json,
    write_error_analysis_markdown,
)
from entity_matching.evaluation.threshold_diagnostics import (
    THRESHOLD_DIAGNOSTICS_SCHEMA_VERSION,
    THRESHOLD_DIAGNOSTIC_COLUMNS,
    ThresholdDiagnosticsError,
    average_precision_score,
    load_threshold_diagnostic_rows,
    summarize_prediction_diagnostics,
    threshold_curve,
    threshold_grid_pr_auc,
    write_threshold_diagnostics_csv,
    write_threshold_diagnostics_markdown,
)
from entity_matching.evaluation.class_ratio_audit import (
    audit_class_ratio_result_summary,
)
from entity_matching.evaluation.class_ratio_results import (
    CLASS_RATIO_RESULT_COLUMNS,
    load_class_ratio_result_rows,
    write_class_ratio_results_csv,
    write_class_ratio_results_markdown,
)
from entity_matching.evaluation.class_ratio_comparison import (
    CLASS_RATIO_PROTOCOL_COMPARISON_COLUMNS,
    ClassRatioProtocolComparisonError,
    load_class_ratio_protocol_comparison_rows,
    write_class_ratio_protocol_comparison_csv,
    write_class_ratio_protocol_comparison_markdown,
)
from entity_matching.evaluation.class_ratio_grid_audit import (
    audit_train_test_ratio_grid_result_summary,
)
from entity_matching.evaluation.class_ratio_grid_results import (
    TRAIN_TEST_RATIO_GRID_RESULT_COLUMNS,
    load_train_test_ratio_grid_result_rows,
    write_train_test_ratio_grid_results_csv,
    write_train_test_ratio_grid_results_markdown,
)

__all__ = [
    "BASELINE_COMPARISON_COLUMNS",
    "BaselineComparisonError",
    "CLASS_RATIO_PROTOCOL_COMPARISON_COLUMNS",
    "CLASS_RATIO_RESULT_COLUMNS",
    "ClassRatioProtocolComparisonError",
    "ERROR_ANALYSIS_SCHEMA_VERSION",
    "ErrorAnalysisError",
    "EvaluationError",
    "METRIC_SCHEMA_VERSION",
    "PredictionArtifactError",
    "RAW_PREDICTION_COLUMNS",
    "RAW_PREDICTION_SCHEMA_VERSION",
    "ResultAuditError",
    "THRESHOLD_DIAGNOSTIC_COLUMNS",
    "THRESHOLD_DIAGNOSTICS_SCHEMA_VERSION",
    "THRESHOLD_SELECTION_SCHEMA_VERSION",
    "TRAIN_TEST_RATIO_GRID_RESULT_COLUMNS",
    "ThresholdDiagnosticsError",
    "analyze_prediction_errors",
    "apply_threshold",
    "audit_baseline_result_summary",
    "audit_class_ratio_result_summary",
    "audit_train_test_ratio_grid_result_summary",
    "average_precision_score",
    "binary_confusion_matrix",
    "evaluate_binary_scores",
    "f1_score",
    "load_baseline_comparison_rows",
    "load_class_ratio_protocol_comparison_rows",
    "load_class_ratio_result_rows",
    "load_train_test_ratio_grid_result_rows",
    "load_threshold_diagnostic_rows",
    "precision_score",
    "prediction_artifact_path",
    "read_prediction_csv",
    "recall_score",
    "select_threshold_on_validation",
    "summarize_prediction_diagnostics",
    "summarize_prediction_rows",
    "threshold_curve",
    "threshold_grid_pr_auc",
    "validate_prediction_rows",
    "write_baseline_comparison_csv",
    "write_baseline_comparison_markdown",
    "write_class_ratio_protocol_comparison_csv",
    "write_class_ratio_protocol_comparison_markdown",
    "write_class_ratio_results_csv",
    "write_class_ratio_results_markdown",
    "write_train_test_ratio_grid_results_csv",
    "write_train_test_ratio_grid_results_markdown",
    "write_error_analysis_json",
    "write_error_analysis_markdown",
    "write_threshold_diagnostics_csv",
    "write_threshold_diagnostics_markdown",
    "write_prediction_csv",
]
