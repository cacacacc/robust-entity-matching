"""Export compact reports from class-ratio aggregate summaries."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping


CLASS_RATIO_RESULT_COLUMNS = [
    "rank_by_test_f1",
    "ratio_id",
    "match_to_non_match_ratio",
    "model_id",
    "train_label_counts",
    "seeds",
    "selected_thresholds",
    "test_precision_mean",
    "test_precision_std",
    "test_recall_mean",
    "test_recall_std",
    "test_f1_mean",
    "test_f1_std",
]


def load_class_ratio_result_rows(summary_path: str | Path) -> list[dict[str, Any]]:
    """Load compact result rows from a class-ratio aggregate summary."""

    with Path(summary_path).open("r", encoding="utf-8") as file:
        summary = json.load(file)
    rows = []
    for ratio_id, model_summaries in summary["ratios"].items():
        for model_id, model_summary in model_summaries.items():
            rows.append(
                {
                    "rank_by_test_f1": 0,
                    "ratio_id": ratio_id,
                    "match_to_non_match_ratio": model_summary[
                        "match_to_non_match_ratio"
                    ],
                    "model_id": model_id,
                    "train_label_counts": model_summary["train_label_counts"],
                    "seeds": model_summary["seeds"],
                    "selected_thresholds": model_summary["selected_thresholds"],
                    "test_precision_mean": float(
                        model_summary["test_precision_mean"]
                    ),
                    "test_precision_std": float(model_summary["test_precision_std"]),
                    "test_recall_mean": float(model_summary["test_recall_mean"]),
                    "test_recall_std": float(model_summary["test_recall_std"]),
                    "test_f1_mean": float(model_summary["test_f1_mean"]),
                    "test_f1_std": float(model_summary["test_f1_std"]),
                }
            )
    rows.sort(
        key=lambda row: (
            -row["test_f1_mean"],
            -row["test_precision_mean"],
            row["model_id"],
            row["match_to_non_match_ratio"],
        )
    )
    for index, row in enumerate(rows, start=1):
        row["rank_by_test_f1"] = index
    return rows


def write_class_ratio_results_csv(
    rows: list[Mapping[str, Any]],
    output_path: str | Path,
) -> int:
    """Write compact class-ratio results to CSV."""

    if not rows:
        raise ValueError("At least one class-ratio result row is required")
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CLASS_RATIO_RESULT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(_format_csv_row(row))
    return len(rows)


def write_class_ratio_results_markdown(
    rows: list[Mapping[str, Any]],
    output_path: str | Path,
    *,
    title: str = "Class-Ratio Stress-Test Results",
    test_policy_note: str = "Test metrics were computed on fixed `test_unseen_100un`.",
) -> int:
    """Write compact class-ratio results to Markdown."""

    if not rows:
        raise ValueError("At least one class-ratio result row is required")
    lines = [
        f"# {title}",
        "",
        "Protocol: WDC Products `train_small` / `valid_small` / `test_unseen_100un`.",
        "",
        "| Rank | Ratio | Model | Test F1 Mean | Test F1 Std | Precision Mean | Recall Mean |",
        "|---:|---|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {rank} | `{ratio}` | `{model}` | `{f1}` | `{f1_std}` | `{precision}` | `{recall}` |".format(
                rank=row["rank_by_test_f1"],
                ratio=row["match_to_non_match_ratio"],
                model=row["model_id"],
                f1=_format_float(row["test_f1_mean"]),
                f1_std=_format_float(row["test_f1_std"]),
                precision=_format_float(row["test_precision_mean"]),
                recall=_format_float(row["test_recall_mean"]),
            )
        )
    lines.extend(
        [
            "",
            "Notes:",
            "",
            "- Thresholds were selected on validation only.",
            f"- {test_policy_note}",
            "- Raw prediction artifacts are local generated files under ignored `results/`.",
        ]
    )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(rows)


def _format_csv_row(row: Mapping[str, Any]) -> dict[str, Any]:
    formatted = dict(row)
    formatted["train_label_counts"] = json.dumps(
        formatted["train_label_counts"], sort_keys=True
    )
    formatted["seeds"] = json.dumps(formatted["seeds"])
    formatted["selected_thresholds"] = json.dumps(formatted["selected_thresholds"])
    return formatted


def _format_float(value: float) -> str:
    return f"{value:.6f}"
