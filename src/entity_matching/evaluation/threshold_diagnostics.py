"""Threshold-free and threshold-grid diagnostics for binary predictions."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import statistics
from typing import Any, Iterable, Mapping

from entity_matching.evaluation.metrics import EvaluationError, evaluate_binary_scores
from entity_matching.evaluation.predictions import read_prediction_csv


THRESHOLD_DIAGNOSTICS_SCHEMA_VERSION = "threshold_diagnostics_v1"

THRESHOLD_DIAGNOSTIC_COLUMNS = [
    "rank_by_test_average_precision",
    "model_id",
    "experiment_id",
    "seeds",
    "selected_thresholds",
    "validation_average_precision_mean",
    "validation_average_precision_std",
    "test_average_precision_mean",
    "test_average_precision_std",
    "test_threshold_grid_pr_auc_mean",
    "test_threshold_grid_pr_auc_std",
    "test_precision_at_selected_threshold_mean",
    "test_recall_at_selected_threshold_mean",
    "test_f1_at_selected_threshold_mean",
]


class ThresholdDiagnosticsError(ValueError):
    """Raised when threshold-diagnostic inputs are invalid."""


def average_precision_score(y_true: Iterable[int], scores: Iterable[float]) -> float:
    """Return ranking average precision for positive class 1."""

    pairs = _validated_pairs(y_true, scores)
    positive_count = sum(label for label, _score in pairs)
    if positive_count == 0:
        raise EvaluationError("Average precision requires at least one positive label")

    sorted_pairs = sorted(
        enumerate(pairs),
        key=lambda item: (-item[1][1], item[0]),
    )
    positives_seen = 0
    precision_sum = 0.0
    for rank, (_index, (label, _score)) in enumerate(sorted_pairs, start=1):
        if label == 1:
            positives_seen += 1
            precision_sum += positives_seen / rank
    return precision_sum / positive_count


def threshold_curve(
    y_true: Iterable[int],
    scores: Iterable[float],
    candidate_thresholds: Iterable[float] | None = None,
) -> list[dict[str, Any]]:
    """Evaluate precision, recall, and F1 across a threshold grid."""

    thresholds = list(candidate_thresholds or _default_thresholds())
    if not thresholds:
        raise EvaluationError("At least one candidate threshold is required")
    return [evaluate_binary_scores(y_true, scores, threshold) for threshold in thresholds]


def threshold_grid_pr_auc(curve: Iterable[Mapping[str, Any]]) -> float:
    """Approximate PR-AUC from a finite threshold curve using trapezoids."""

    points = [(0.0, 1.0)]
    for row in curve:
        points.append((float(row["recall"]), float(row["precision"])))
    points.sort(key=lambda point: (point[0], point[1]))

    area = 0.0
    previous_recall, previous_precision = points[0]
    for recall, precision in points[1:]:
        delta = recall - previous_recall
        if delta > 0:
            area += delta * (precision + previous_precision) / 2
            previous_recall = recall
            previous_precision = precision
        else:
            previous_precision = max(previous_precision, precision)
    return area


def summarize_prediction_diagnostics(
    prediction_path: str | Path,
    candidate_thresholds: Iterable[float] | None = None,
) -> dict[str, Any]:
    """Summarize one raw prediction CSV with threshold diagnostics."""

    rows = read_prediction_csv(prediction_path)
    y_true = [row["y_true"] for row in rows]
    scores = [row["score"] for row in rows]
    curve = threshold_curve(y_true, scores, candidate_thresholds)
    return {
        "schema_version": THRESHOLD_DIAGNOSTICS_SCHEMA_VERSION,
        "prediction_path": str(prediction_path),
        "experiment_id": rows[0]["experiment_id"],
        "model_id": rows[0]["model_id"],
        "seed": rows[0]["seed"],
        "split_role": rows[0]["split_role"],
        "split": rows[0]["split"],
        "row_count": len(rows),
        "positive_count": sum(y_true),
        "negative_count": len(y_true) - sum(y_true),
        "average_precision": average_precision_score(y_true, scores),
        "threshold_grid_pr_auc": threshold_grid_pr_auc(curve),
        "threshold_curve": curve,
    }


def load_threshold_diagnostic_rows(
    aggregate_summary_paths: Iterable[str | Path],
) -> list[dict[str, Any]]:
    """Load model-level threshold diagnostics from baseline aggregate summaries."""

    seed_rows = []
    for summary_path in aggregate_summary_paths:
        with Path(summary_path).open("r", encoding="utf-8") as file:
            summary = json.load(file)
        if summary.get("status") != "completed":
            raise ThresholdDiagnosticsError(
                f"Aggregate summary is not completed: {summary_path}"
            )
        for seed_result in summary["seed_results"]:
            seed_rows.append(_seed_diagnostic_row(seed_result))

    if not seed_rows:
        raise ThresholdDiagnosticsError("At least one seed result is required")

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in seed_rows:
        key = (row["experiment_id"], row["model_id"])
        grouped.setdefault(key, []).append(row)

    model_rows = []
    for (experiment_id, model_id), rows in grouped.items():
        rows.sort(key=lambda row: row["seed"])
        model_rows.append(
            {
                "rank_by_test_average_precision": 0,
                "model_id": model_id,
                "experiment_id": experiment_id,
                "seeds": [row["seed"] for row in rows],
                "selected_thresholds": [row["selected_threshold"] for row in rows],
                "validation_average_precision_mean": _mean(
                    rows, "validation_average_precision"
                ),
                "validation_average_precision_std": _sample_std(
                    rows, "validation_average_precision"
                ),
                "test_average_precision_mean": _mean(rows, "test_average_precision"),
                "test_average_precision_std": _sample_std(
                    rows, "test_average_precision"
                ),
                "test_threshold_grid_pr_auc_mean": _mean(
                    rows, "test_threshold_grid_pr_auc"
                ),
                "test_threshold_grid_pr_auc_std": _sample_std(
                    rows, "test_threshold_grid_pr_auc"
                ),
                "test_precision_at_selected_threshold_mean": _mean(
                    rows, "test_precision_at_selected_threshold"
                ),
                "test_recall_at_selected_threshold_mean": _mean(
                    rows, "test_recall_at_selected_threshold"
                ),
                "test_f1_at_selected_threshold_mean": _mean(
                    rows, "test_f1_at_selected_threshold"
                ),
            }
        )

    model_rows.sort(
        key=lambda row: (
            -row["test_average_precision_mean"],
            -row["test_threshold_grid_pr_auc_mean"],
            row["model_id"],
        )
    )
    for index, row in enumerate(model_rows, start=1):
        row["rank_by_test_average_precision"] = index
    return model_rows


def write_threshold_diagnostics_csv(
    rows: Iterable[Mapping[str, Any]], output_path: str | Path
) -> int:
    """Write model-level threshold diagnostics to CSV."""

    normalized_rows = [_format_csv_row(row) for row in rows]
    if not normalized_rows:
        raise ThresholdDiagnosticsError("At least one diagnostic row is required")

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=THRESHOLD_DIAGNOSTIC_COLUMNS)
        writer.writeheader()
        writer.writerows(normalized_rows)
    return len(normalized_rows)


def write_threshold_diagnostics_markdown(
    rows: Iterable[Mapping[str, Any]], output_path: str | Path
) -> int:
    """Write model-level threshold diagnostics as Markdown."""

    row_list = list(rows)
    if not row_list:
        raise ThresholdDiagnosticsError("At least one diagnostic row is required")

    lines = [
        "# Threshold Diagnostics",
        "",
        "Protocol: WDC Products `train_small` / `valid_small` / `test_unseen_100un`.",
        "",
        "| Rank | Model | Test AP Mean | Test AP Std | Test Grid PR-AUC Mean | F1 Mean @ Selected Threshold | Precision Mean | Recall Mean |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in row_list:
        lines.append(
            "| {rank} | `{model}` | `{ap}` | `{ap_std}` | `{grid_auc}` | `{f1}` | `{precision}` | `{recall}` |".format(
                rank=row["rank_by_test_average_precision"],
                model=row["model_id"],
                ap=_format_float(row["test_average_precision_mean"]),
                ap_std=_format_float(row["test_average_precision_std"]),
                grid_auc=_format_float(row["test_threshold_grid_pr_auc_mean"]),
                f1=_format_float(row["test_f1_at_selected_threshold_mean"]),
                precision=_format_float(row["test_precision_at_selected_threshold_mean"]),
                recall=_format_float(row["test_recall_at_selected_threshold_mean"]),
            )
        )
    lines.extend(
        [
            "",
            "Notes:",
            "",
            "- AP means ranking average precision computed from raw prediction scores.",
            "- Grid PR-AUC is a coarse 0.00-1.00 threshold-grid approximation, mainly for threshold-shape diagnostics.",
            "- Selected-threshold metrics still use thresholds chosen on validation only.",
            "- Test scores are used here for post-run reporting, not for model or threshold selection.",
        ]
    )

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(row_list)


def _seed_diagnostic_row(seed_result: Mapping[str, Any]) -> dict[str, Any]:
    validation = summarize_prediction_diagnostics(seed_result["validation_prediction_path"])
    test = summarize_prediction_diagnostics(seed_result["test_prediction_path"])
    test_metrics = seed_result["test_metrics"]
    return {
        "experiment_id": seed_result["experiment_id"],
        "model_id": seed_result["model_id"],
        "seed": seed_result["seed"],
        "selected_threshold": float(seed_result["selected_threshold"]),
        "validation_average_precision": validation["average_precision"],
        "validation_threshold_grid_pr_auc": validation["threshold_grid_pr_auc"],
        "test_average_precision": test["average_precision"],
        "test_threshold_grid_pr_auc": test["threshold_grid_pr_auc"],
        "test_precision_at_selected_threshold": float(test_metrics["precision"]),
        "test_recall_at_selected_threshold": float(test_metrics["recall"]),
        "test_f1_at_selected_threshold": float(test_metrics["f1"]),
    }


def _validated_pairs(
    y_true: Iterable[int], scores: Iterable[float]
) -> list[tuple[int, float]]:
    true_list = list(y_true)
    score_list = list(scores)
    if len(true_list) != len(score_list):
        raise EvaluationError(
            f"Length mismatch: y_true has {len(true_list)}, scores has {len(score_list)}"
        )
    if not true_list:
        raise EvaluationError("Metric inputs must not be empty")
    pairs = []
    for index, (label, score) in enumerate(zip(true_list, score_list)):
        if label not in (0, 1):
            raise EvaluationError(f"Invalid y_true label at index {index}: {label}")
        if score < 0.0 or score > 1.0:
            raise EvaluationError(f"Score at index {index} is outside [0, 1]: {score}")
        pairs.append((label, float(score)))
    return pairs


def _default_thresholds() -> list[float]:
    return [index / 100 for index in range(0, 101)]


def _mean(rows: list[Mapping[str, Any]], key: str) -> float:
    return statistics.mean(float(row[key]) for row in rows)


def _sample_std(rows: list[Mapping[str, Any]], key: str) -> float:
    values = [float(row[key]) for row in rows]
    if len(values) < 2:
        return 0.0
    return statistics.stdev(values)


def _format_csv_row(row: Mapping[str, Any]) -> dict[str, Any]:
    formatted = dict(row)
    formatted["seeds"] = json.dumps(formatted["seeds"])
    formatted["selected_thresholds"] = json.dumps(formatted["selected_thresholds"])
    return formatted


def _format_float(value: float) -> str:
    return f"{value:.6f}"
