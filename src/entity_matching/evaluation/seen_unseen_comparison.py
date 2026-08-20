"""Compare WDC seen and unseen baseline aggregate summaries."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


SEEN_UNSEEN_COMPARISON_COLUMNS = [
    "model_id",
    "seen_experiment_id",
    "unseen_experiment_id",
    "seen_test_split",
    "unseen_test_split",
    "seen_f1_mean",
    "unseen_f1_mean",
    "unseen_minus_seen_f1",
    "seen_precision_mean",
    "unseen_precision_mean",
    "unseen_minus_seen_precision",
    "seen_recall_mean",
    "unseen_recall_mean",
    "unseen_minus_seen_recall",
    "seen_f1_std",
    "unseen_f1_std",
]


class SeenUnseenComparisonError(ValueError):
    """Raised when seen/unseen comparison inputs are invalid."""


def load_seen_unseen_comparison_rows(
    seen_summary_path: str | Path,
    unseen_summary_paths: Iterable[str | Path],
) -> list[dict[str, Any]]:
    """Load model-aligned seen-vs-unseen comparison rows."""

    seen_summary = _load_completed_summary(seen_summary_path)
    unseen_summaries = [_load_completed_summary(path) for path in unseen_summary_paths]
    seen_rows = _model_index(seen_summary)
    unseen_rows: dict[str, dict[str, Any]] = {}
    unseen_experiment_ids = {}
    for summary in unseen_summaries:
        for model_id, metrics in _model_index(summary).items():
            if model_id in unseen_rows:
                raise SeenUnseenComparisonError(
                    f"Duplicate unseen model result: {model_id}"
                )
            unseen_rows[model_id] = metrics
            unseen_experiment_ids[model_id] = summary["experiment_id"]

    if set(seen_rows) != set(unseen_rows):
        raise SeenUnseenComparisonError(
            f"Seen/unseen model sets differ: {sorted(seen_rows)} != {sorted(unseen_rows)}"
        )

    rows = []
    seen_test_split = _test_split_from_seed_results(seen_summary)
    for model_id in sorted(seen_rows):
        seen = seen_rows[model_id]
        unseen = unseen_rows[model_id]
        rows.append(
            {
                "model_id": model_id,
                "seen_experiment_id": seen_summary["experiment_id"],
                "unseen_experiment_id": unseen_experiment_ids[model_id],
                "seen_test_split": seen_test_split,
                "unseen_test_split": _test_split_from_model_seed_results(
                    unseen_summaries, model_id
                ),
                "seen_f1_mean": seen["test_f1_mean"],
                "unseen_f1_mean": unseen["test_f1_mean"],
                "unseen_minus_seen_f1": unseen["test_f1_mean"]
                - seen["test_f1_mean"],
                "seen_precision_mean": seen["test_precision_mean"],
                "unseen_precision_mean": unseen["test_precision_mean"],
                "unseen_minus_seen_precision": unseen["test_precision_mean"]
                - seen["test_precision_mean"],
                "seen_recall_mean": seen["test_recall_mean"],
                "unseen_recall_mean": unseen["test_recall_mean"],
                "unseen_minus_seen_recall": unseen["test_recall_mean"]
                - seen["test_recall_mean"],
                "seen_f1_std": seen["test_f1_std"],
                "unseen_f1_std": unseen["test_f1_std"],
            }
        )
    rows.sort(key=lambda row: (-row["unseen_f1_mean"], row["model_id"]))
    return rows


def write_seen_unseen_comparison_csv(
    rows: list[Mapping[str, Any]],
    output_path: str | Path,
) -> int:
    """Write seen-vs-unseen comparison rows to CSV."""

    if not rows:
        raise SeenUnseenComparisonError("At least one comparison row is required")
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=SEEN_UNSEEN_COMPARISON_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def write_seen_unseen_comparison_markdown(
    rows: list[Mapping[str, Any]],
    output_path: str | Path,
) -> int:
    """Write a compact seen-vs-unseen comparison report."""

    if not rows:
        raise SeenUnseenComparisonError("At least one comparison row is required")
    lines = [
        "# Seen vs Unseen Baseline Comparison",
        "",
        "Protocol: WDC Products `train_small` / `valid_small`; seen test `test_seen_000un`; unseen test `test_unseen_100un`.",
        "",
        "| Model | Seen F1 | Unseen F1 | Unseen - Seen F1 | Seen Precision | Unseen Precision | Seen Recall | Unseen Recall |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| `{model}` | `{seen_f1}` | `{unseen_f1}` | `{delta_f1}` | `{seen_precision}` | `{unseen_precision}` | `{seen_recall}` | `{unseen_recall}` |".format(
                model=row["model_id"],
                seen_f1=_format_float(row["seen_f1_mean"]),
                unseen_f1=_format_float(row["unseen_f1_mean"]),
                delta_f1=_format_signed_float(row["unseen_minus_seen_f1"]),
                seen_precision=_format_float(row["seen_precision_mean"]),
                unseen_precision=_format_float(row["unseen_precision_mean"]),
                seen_recall=_format_float(row["seen_recall_mean"]),
                unseen_recall=_format_float(row["unseen_recall_mean"]),
            )
        )
    lines.extend(
        [
            "",
            "Notes:",
            "",
            "- Thresholds were selected on the same fixed validation split.",
            "- Seen test is an official seen diagnostic and has known development overlap; it is not a leakage-free final evaluation.",
            "- Unseen test is the main entity-disjoint WDC evaluation used for robustness claims.",
            "- Positive `Unseen - Seen` values mean the unseen split scored higher than the seen split under this metric.",
        ]
    )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(rows)


def _load_completed_summary(summary_path: str | Path) -> dict[str, Any]:
    with Path(summary_path).open("r", encoding="utf-8") as file:
        summary = json.load(file)
    if summary.get("status") != "completed":
        raise SeenUnseenComparisonError(f"Summary is not completed: {summary_path}")
    return summary


def _model_index(summary: Mapping[str, Any]) -> dict[str, dict[str, float]]:
    return {
        model_id: {
            "test_f1_mean": float(metrics["test_f1_mean"]),
            "test_f1_std": float(metrics["test_f1_std"]),
            "test_precision_mean": float(metrics["test_precision_mean"]),
            "test_recall_mean": float(metrics["test_recall_mean"]),
        }
        for model_id, metrics in summary["models"].items()
    }


def _test_split_from_seed_results(summary: Mapping[str, Any]) -> str:
    labels = {
        seed_result["test_label_counts"]["0"] for seed_result in summary["seed_results"]
    }
    if labels != {4000}:
        raise SeenUnseenComparisonError("Unexpected test negative counts")
    return _split_name_from_prediction(summary["seed_results"][0]["test_prediction_path"])


def _test_split_from_model_seed_results(
    summaries: list[Mapping[str, Any]],
    model_id: str,
) -> str:
    for summary in summaries:
        for seed_result in summary["seed_results"]:
            if seed_result["model_id"] == model_id:
                return _split_name_from_prediction(seed_result["test_prediction_path"])
    raise SeenUnseenComparisonError(f"Missing seed result for {model_id}")


def _split_name_from_prediction(prediction_path: str) -> str:
    with Path(prediction_path).open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        first = next(reader)
    return first["split"]


def _format_float(value: float) -> str:
    return f"{value:.6f}"


def _format_signed_float(value: float) -> str:
    return f"{value:+.6f}"
