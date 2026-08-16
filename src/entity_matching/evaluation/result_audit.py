"""Audit saved baseline summaries against raw prediction artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import statistics
from typing import Any, Mapping

from entity_matching.evaluation.metrics import evaluate_binary_scores
from entity_matching.evaluation.predictions import read_prediction_csv


class ResultAuditError(ValueError):
    """Raised when saved result artifacts do not match raw predictions."""


def audit_baseline_result_summary(summary_path: str | Path) -> dict[str, Any]:
    """Audit an aggregate result summary against raw prediction CSV files."""

    with Path(summary_path).open("r", encoding="utf-8") as file:
        summary = json.load(file)

    seed_audits = [_audit_seed_result(seed) for seed in summary["seed_results"]]
    model_audits = {}
    for model_id, model_summary in summary["models"].items():
        model_seed_audits = [
            audit for audit in seed_audits if audit["model_id"] == model_id
        ]
        model_audits[model_id] = _audit_model_summary(
            model_summary, model_seed_audits
        )

    return {
        "audit_status": "passed",
        "experiment_id": summary["experiment_id"],
        "summary_path": str(summary_path),
        "model_audits": model_audits,
        "seed_audits": seed_audits,
    }


def _audit_seed_result(seed_result: Mapping[str, Any]) -> dict[str, Any]:
    selected_threshold = float(seed_result["selected_threshold"])
    return {
        "experiment_id": seed_result["experiment_id"],
        "model_id": seed_result["model_id"],
        "seed": seed_result["seed"],
        "selected_threshold": selected_threshold,
        "validation": _audit_split_predictions(
            seed_result["validation_prediction_path"],
            seed_result["validation_metrics"],
            selected_threshold,
            expected_split_role="validation",
        ),
        "test": _audit_split_predictions(
            seed_result["test_prediction_path"],
            seed_result["test_metrics"],
            selected_threshold,
            expected_split_role="test",
        ),
    }


def _audit_split_predictions(
    prediction_path: str | Path,
    stored_metrics: Mapping[str, Any],
    selected_threshold: float,
    *,
    expected_split_role: str,
) -> dict[str, Any]:
    rows = read_prediction_csv(prediction_path)
    split_roles = {row["split_role"] for row in rows}
    if split_roles != {expected_split_role}:
        raise ResultAuditError(
            f"Unexpected split_role values in {prediction_path}: {sorted(split_roles)}"
        )

    thresholds = {row["threshold"] for row in rows}
    if thresholds != {selected_threshold}:
        raise ResultAuditError(
            f"Unexpected threshold values in {prediction_path}: {sorted(thresholds)}"
        )

    y_true = [row["y_true"] for row in rows]
    scores = [row["score"] for row in rows]
    recomputed = evaluate_binary_scores(y_true, scores, selected_threshold)
    _assert_metric_dict_close(stored_metrics, recomputed, prediction_path)

    return {
        "prediction_path": str(prediction_path),
        "row_count": len(rows),
        "recomputed_metrics": recomputed,
        "stored_metrics_match_raw_predictions": True,
    }


def _audit_model_summary(
    model_summary: Mapping[str, Any], seed_audits: list[Mapping[str, Any]]
) -> dict[str, Any]:
    seeds = [audit["seed"] for audit in seed_audits]
    if seeds != model_summary["seeds"]:
        raise ResultAuditError(
            f"Model seed list mismatch: {seeds} != {model_summary['seeds']}"
        )

    thresholds = [audit["selected_threshold"] for audit in seed_audits]
    if thresholds != model_summary["selected_thresholds"]:
        raise ResultAuditError(
            "Selected threshold list mismatch: "
            f"{thresholds} != {model_summary['selected_thresholds']}"
        )

    test_precision_values = [
        float(audit["test"]["recomputed_metrics"]["precision"]) for audit in seed_audits
    ]
    test_recall_values = [
        float(audit["test"]["recomputed_metrics"]["recall"]) for audit in seed_audits
    ]
    test_f1_values = [
        float(audit["test"]["recomputed_metrics"]["f1"]) for audit in seed_audits
    ]
    checks = {
        "test_precision_mean": statistics.mean(test_precision_values),
        "test_precision_std": _sample_std(test_precision_values),
        "test_recall_mean": statistics.mean(test_recall_values),
        "test_recall_std": _sample_std(test_recall_values),
        "test_f1_mean": statistics.mean(test_f1_values),
        "test_f1_std": _sample_std(test_f1_values),
    }
    for key, recomputed_value in checks.items():
        _assert_close(float(model_summary[key]), recomputed_value, key)

    return {
        "seeds": seeds,
        "selected_thresholds": thresholds,
        "aggregate_metrics_match_seed_results": True,
        "recomputed_aggregate_metrics": checks,
    }


def _assert_metric_dict_close(
    stored: Mapping[str, Any], recomputed: Mapping[str, Any], context: str | Path
) -> None:
    for key in ("threshold", "total", "positive_count", "negative_count"):
        if stored[key] != recomputed[key]:
            raise ResultAuditError(
                f"Metric mismatch in {context}, {key}: "
                f"{stored[key]} != {recomputed[key]}"
            )
    if stored["confusion_matrix"] != recomputed["confusion_matrix"]:
        raise ResultAuditError(
            f"Confusion mismatch in {context}: "
            f"{stored['confusion_matrix']} != {recomputed['confusion_matrix']}"
        )
    for key in ("precision", "recall", "f1"):
        _assert_close(float(stored[key]), float(recomputed[key]), f"{context}:{key}")


def _assert_close(left: float, right: float, context: str) -> None:
    if abs(left - right) > 1e-12:
        raise ResultAuditError(f"Value mismatch for {context}: {left} != {right}")


def _sample_std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return statistics.stdev(values)
