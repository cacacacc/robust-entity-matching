"""Export compact reports from train/test ratio grid aggregate summaries."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping


TRAIN_TEST_RATIO_GRID_RESULT_COLUMNS = [
    "rank_by_test_f1",
    "train_ratio_id",
    "train_ratio",
    "test_ratio_id",
    "test_ratio",
    "model_id",
    "train_label_counts",
    "test_label_counts",
    "seeds",
    "selected_thresholds",
    "test_precision_mean",
    "test_precision_std",
    "test_recall_mean",
    "test_recall_std",
    "test_f1_mean",
    "test_f1_std",
]


def load_train_test_ratio_grid_result_rows(
    summary_path: str | Path,
) -> list[dict[str, Any]]:
    """Load compact result rows from a train/test ratio grid summary."""

    with Path(summary_path).open("r", encoding="utf-8") as file:
        summary = json.load(file)
    rows = []
    for train_ratio_id, test_ratios in summary["grid"].items():
        for test_ratio_id, model_summaries in test_ratios.items():
            for model_id, cell_summary in model_summaries.items():
                rows.append(
                    {
                        "rank_by_test_f1": 0,
                        "train_ratio_id": train_ratio_id,
                        "train_ratio": cell_summary["train_ratio"],
                        "test_ratio_id": test_ratio_id,
                        "test_ratio": cell_summary["test_ratio"],
                        "model_id": model_id,
                        "train_label_counts": cell_summary["train_label_counts"],
                        "test_label_counts": cell_summary["test_label_counts"],
                        "seeds": cell_summary["seeds"],
                        "selected_thresholds": cell_summary["selected_thresholds"],
                        "test_precision_mean": float(
                            cell_summary["test_precision_mean"]
                        ),
                        "test_precision_std": float(
                            cell_summary["test_precision_std"]
                        ),
                        "test_recall_mean": float(cell_summary["test_recall_mean"]),
                        "test_recall_std": float(cell_summary["test_recall_std"]),
                        "test_f1_mean": float(cell_summary["test_f1_mean"]),
                        "test_f1_std": float(cell_summary["test_f1_std"]),
                    }
                )
    rows.sort(
        key=lambda row: (
            -row["test_f1_mean"],
            -row["test_precision_mean"],
            row["model_id"],
            _ratio_sort_key(row["train_ratio"]),
            _ratio_sort_key(row["test_ratio"]),
        )
    )
    for index, row in enumerate(rows, start=1):
        row["rank_by_test_f1"] = index
    return rows


def write_train_test_ratio_grid_results_csv(
    rows: list[Mapping[str, Any]],
    output_path: str | Path,
) -> int:
    """Write compact train/test ratio grid results to CSV."""

    if not rows:
        raise ValueError("At least one train/test ratio grid result row is required")
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=TRAIN_TEST_RATIO_GRID_RESULT_COLUMNS
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(_format_csv_row(row))
    return len(rows)


def write_train_test_ratio_grid_results_markdown(
    rows: list[Mapping[str, Any]],
    output_path: str | Path,
) -> int:
    """Write compact train/test ratio grid results to Markdown."""

    if not rows:
        raise ValueError("At least one train/test ratio grid result row is required")
    lines = [
        "# Train/Test Ratio Grid Results",
        "",
        "Protocol: WDC Products `train_small` / `valid_small` / `test_unseen_100un`.",
        "",
        "| Rank | Train Ratio | Test Ratio | Model | Test F1 Mean | Test F1 Std | Precision Mean | Recall Mean |",
        "|---:|---|---|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {rank} | `{train}` | `{test}` | `{model}` | `{f1}` | `{f1_std}` | `{precision}` | `{recall}` |".format(
                rank=row["rank_by_test_f1"],
                train=row["train_ratio"],
                test=row["test_ratio"],
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
            "- Thresholds were selected on fixed validation only.",
            "- Test metrics were computed on seeded class-ratio samples from `test_unseen_100un`.",
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
    formatted["test_label_counts"] = json.dumps(
        formatted["test_label_counts"], sort_keys=True
    )
    formatted["seeds"] = json.dumps(formatted["seeds"])
    formatted["selected_thresholds"] = json.dumps(formatted["selected_thresholds"])
    return formatted


def _ratio_sort_key(ratio_label: str) -> int:
    return int(ratio_label.split(":", maxsplit=1)[1])


def _format_float(value: float) -> str:
    return f"{value:.6f}"
