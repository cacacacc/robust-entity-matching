"""Compare audited aggregate baseline summaries."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


BASELINE_COMPARISON_COLUMNS = [
    "rank_by_test_f1",
    "model_id",
    "experiment_id",
    "seeds",
    "selected_thresholds",
    "test_precision_mean",
    "test_precision_std",
    "test_recall_mean",
    "test_recall_std",
    "test_f1_mean",
    "test_f1_std",
]


class BaselineComparisonError(ValueError):
    """Raised when baseline comparison inputs are invalid."""


def load_baseline_comparison_rows(
    aggregate_summary_paths: Iterable[str | Path],
) -> list[dict[str, Any]]:
    """Load model-level comparison rows from aggregate summary JSON files."""

    rows = []
    for summary_path in aggregate_summary_paths:
        with Path(summary_path).open("r", encoding="utf-8") as file:
            summary = json.load(file)
        if summary.get("status") != "completed":
            raise BaselineComparisonError(
                f"Aggregate summary is not completed: {summary_path}"
            )
        experiment_id = summary["experiment_id"]
        for model_id, metrics in summary["models"].items():
            rows.append(
                {
                    "rank_by_test_f1": 0,
                    "model_id": model_id,
                    "experiment_id": experiment_id,
                    "seeds": list(metrics["seeds"]),
                    "selected_thresholds": list(metrics["selected_thresholds"]),
                    "test_precision_mean": float(metrics["test_precision_mean"]),
                    "test_precision_std": float(metrics["test_precision_std"]),
                    "test_recall_mean": float(metrics["test_recall_mean"]),
                    "test_recall_std": float(metrics["test_recall_std"]),
                    "test_f1_mean": float(metrics["test_f1_mean"]),
                    "test_f1_std": float(metrics["test_f1_std"]),
                }
            )

    if not rows:
        raise BaselineComparisonError("At least one model result is required")

    rows.sort(
        key=lambda row: (
            -row["test_f1_mean"],
            -row["test_precision_mean"],
            row["model_id"],
        )
    )
    for index, row in enumerate(rows, start=1):
        row["rank_by_test_f1"] = index
    return rows


def write_baseline_comparison_csv(
    rows: Iterable[Mapping[str, Any]], output_path: str | Path
) -> int:
    """Write comparison rows to CSV."""

    normalized_rows = [_format_csv_row(row) for row in rows]
    if not normalized_rows:
        raise BaselineComparisonError("At least one comparison row is required")

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=BASELINE_COMPARISON_COLUMNS)
        writer.writeheader()
        writer.writerows(normalized_rows)
    return len(normalized_rows)


def write_baseline_comparison_markdown(
    rows: Iterable[Mapping[str, Any]], output_path: str | Path
) -> int:
    """Write comparison rows as a compact Markdown table."""

    row_list = list(rows)
    if not row_list:
        raise BaselineComparisonError("At least one comparison row is required")

    lines = [
        "# Baseline Comparison",
        "",
        "Protocol: WDC Products `train_small` / `valid_small` / `test_unseen_100un`.",
        "",
        "| Rank | Model | Test F1 Mean | Test F1 Std | Precision Mean | Recall Mean | Thresholds |",
        "|---:|---|---:|---:|---:|---:|---|",
    ]
    for row in row_list:
        lines.append(
            "| {rank} | `{model}` | `{f1_mean}` | `{f1_std}` | `{precision}` | `{recall}` | `{thresholds}` |".format(
                rank=row["rank_by_test_f1"],
                model=row["model_id"],
                f1_mean=_format_float(row["test_f1_mean"]),
                f1_std=_format_float(row["test_f1_std"]),
                precision=_format_float(row["test_precision_mean"]),
                recall=_format_float(row["test_recall_mean"]),
                thresholds=", ".join(str(value) for value in row["selected_thresholds"]),
            )
        )
    lines.extend(
        [
            "",
            "Notes:",
            "",
            "- Thresholds were selected on validation only.",
            "- Test metrics were computed on `test_unseen_100un` only.",
            "- Raw prediction artifacts are local generated files under ignored `results/`.",
        ]
    )

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(row_list)


def _format_csv_row(row: Mapping[str, Any]) -> dict[str, Any]:
    formatted = dict(row)
    formatted["seeds"] = json.dumps(formatted["seeds"])
    formatted["selected_thresholds"] = json.dumps(formatted["selected_thresholds"])
    return formatted


def _format_float(value: float) -> str:
    return f"{value:.6f}"
