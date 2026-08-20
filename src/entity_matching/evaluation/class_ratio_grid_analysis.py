"""Derived analysis tables for train/test ratio grid results."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Mapping

from entity_matching.evaluation.class_ratio_grid_results import (
    load_train_test_ratio_grid_result_rows,
)


F1_MATRIX_COLUMNS = [
    "model_id",
    "train_ratio",
    "test_1_1_f1_mean",
    "test_1_2_f1_mean",
    "test_1_3_f1_mean",
    "test_1_4_f1_mean",
]

BEST_TRAIN_BY_TEST_RATIO_COLUMNS = [
    "model_id",
    "test_ratio",
    "best_train_ratio",
    "best_test_f1_mean",
    "best_precision_mean",
    "best_recall_mean",
    "second_best_train_ratio",
    "delta_to_second_best_f1",
]

TEST_RATIO_SENSITIVITY_COLUMNS = [
    "model_id",
    "train_ratio",
    "f1_at_test_1_1",
    "f1_at_test_1_4",
    "f1_drop_1_1_to_1_4",
    "precision_at_test_1_1",
    "precision_at_test_1_4",
    "precision_drop_1_1_to_1_4",
    "recall_at_test_1_1",
    "recall_at_test_1_4",
    "recall_drop_1_1_to_1_4",
]


def load_train_test_ratio_grid_analysis(
    summary_path: str | Path,
) -> dict[str, list[dict[str, Any]]]:
    """Build derived analysis tables from a train/test ratio grid summary."""

    result_rows = load_train_test_ratio_grid_result_rows(summary_path)
    return {
        "f1_matrix_rows": train_test_ratio_f1_matrix_rows(result_rows),
        "best_train_by_test_ratio_rows": best_train_by_test_ratio_rows(result_rows),
        "test_ratio_sensitivity_rows": test_ratio_sensitivity_rows(result_rows),
    }


def train_test_ratio_f1_matrix_rows(
    result_rows: list[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Return one F1 matrix row per model and train ratio."""

    index = _index_rows(result_rows)
    model_ids = sorted({row["model_id"] for row in result_rows})
    train_ratios = sorted({row["train_ratio"] for row in result_rows}, key=_ratio_key)
    test_ratios = sorted({row["test_ratio"] for row in result_rows}, key=_ratio_key)
    rows = []
    for model_id in model_ids:
        for train_ratio in train_ratios:
            row = {"model_id": model_id, "train_ratio": train_ratio}
            for test_ratio in test_ratios:
                row[_test_f1_column(test_ratio)] = index[
                    (model_id, train_ratio, test_ratio)
                ]["test_f1_mean"]
            rows.append(row)
    return rows


def best_train_by_test_ratio_rows(
    result_rows: list[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Return the best train ratio for each model and fixed test ratio."""

    model_ids = sorted({row["model_id"] for row in result_rows})
    test_ratios = sorted({row["test_ratio"] for row in result_rows}, key=_ratio_key)
    rows = []
    for model_id in model_ids:
        for test_ratio in test_ratios:
            candidates = [
                row
                for row in result_rows
                if row["model_id"] == model_id and row["test_ratio"] == test_ratio
            ]
            candidates.sort(
                key=lambda row: (
                    -row["test_f1_mean"],
                    -row["test_precision_mean"],
                    _ratio_key(row["train_ratio"]),
                )
            )
            best = candidates[0]
            second = candidates[1]
            rows.append(
                {
                    "model_id": model_id,
                    "test_ratio": test_ratio,
                    "best_train_ratio": best["train_ratio"],
                    "best_test_f1_mean": best["test_f1_mean"],
                    "best_precision_mean": best["test_precision_mean"],
                    "best_recall_mean": best["test_recall_mean"],
                    "second_best_train_ratio": second["train_ratio"],
                    "delta_to_second_best_f1": best["test_f1_mean"]
                    - second["test_f1_mean"],
                }
            )
    return rows


def test_ratio_sensitivity_rows(
    result_rows: list[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Measure metric drops from test ratio 1:1 to 1:4 for each train row."""

    index = _index_rows(result_rows)
    model_ids = sorted({row["model_id"] for row in result_rows})
    train_ratios = sorted({row["train_ratio"] for row in result_rows}, key=_ratio_key)
    rows = []
    for model_id in model_ids:
        for train_ratio in train_ratios:
            easy = index[(model_id, train_ratio, "1:1")]
            hard = index[(model_id, train_ratio, "1:4")]
            rows.append(
                {
                    "model_id": model_id,
                    "train_ratio": train_ratio,
                    "f1_at_test_1_1": easy["test_f1_mean"],
                    "f1_at_test_1_4": hard["test_f1_mean"],
                    "f1_drop_1_1_to_1_4": easy["test_f1_mean"]
                    - hard["test_f1_mean"],
                    "precision_at_test_1_1": easy["test_precision_mean"],
                    "precision_at_test_1_4": hard["test_precision_mean"],
                    "precision_drop_1_1_to_1_4": easy["test_precision_mean"]
                    - hard["test_precision_mean"],
                    "recall_at_test_1_1": easy["test_recall_mean"],
                    "recall_at_test_1_4": hard["test_recall_mean"],
                    "recall_drop_1_1_to_1_4": easy["test_recall_mean"]
                    - hard["test_recall_mean"],
                }
            )
    rows.sort(
        key=lambda row: (
            -row["f1_drop_1_1_to_1_4"],
            row["model_id"],
            _ratio_key(row["train_ratio"]),
        )
    )
    return rows


def write_f1_matrix_csv(
    rows: list[Mapping[str, Any]], output_path: str | Path
) -> int:
    """Write F1 matrix rows to CSV."""

    return _write_csv(rows, output_path, F1_MATRIX_COLUMNS)


def write_best_train_by_test_ratio_csv(
    rows: list[Mapping[str, Any]], output_path: str | Path
) -> int:
    """Write best-train-by-test rows to CSV."""

    return _write_csv(rows, output_path, BEST_TRAIN_BY_TEST_RATIO_COLUMNS)


def write_test_ratio_sensitivity_csv(
    rows: list[Mapping[str, Any]], output_path: str | Path
) -> int:
    """Write test-ratio sensitivity rows to CSV."""

    return _write_csv(rows, output_path, TEST_RATIO_SENSITIVITY_COLUMNS)


def write_train_test_ratio_grid_analysis_markdown(
    analysis: Mapping[str, list[Mapping[str, Any]]],
    output_path: str | Path,
) -> int:
    """Write a compact Markdown analysis of the train/test ratio grid."""

    f1_rows = list(analysis["f1_matrix_rows"])
    best_rows = list(analysis["best_train_by_test_ratio_rows"])
    sensitivity_rows = list(analysis["test_ratio_sensitivity_rows"])
    lines = [
        "# Train/Test Ratio Grid Analysis",
        "",
        "Protocol: WDC Products `train_small` / `valid_small` / `test_unseen_100un`.",
        "",
        "## Best Train Ratio Within Each Test Ratio",
        "",
        "| Model | Test Ratio | Best Train Ratio | Best F1 | Delta To Second | Precision | Recall |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in best_rows:
        lines.append(
            "| `{model}` | `{test}` | `{train}` | `{f1}` | `{delta}` | `{precision}` | `{recall}` |".format(
                model=row["model_id"],
                test=row["test_ratio"],
                train=row["best_train_ratio"],
                f1=_format_float(row["best_test_f1_mean"]),
                delta=_format_float(row["delta_to_second_best_f1"]),
                precision=_format_float(row["best_precision_mean"]),
                recall=_format_float(row["best_recall_mean"]),
            )
        )
    lines.extend(
        [
            "",
            "## Largest F1 Drops From Test 1:1 To Test 1:4",
            "",
            "| Model | Train Ratio | F1 @ Test 1:1 | F1 @ Test 1:4 | F1 Drop | Precision Drop | Recall Drop |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in sensitivity_rows[:8]:
        lines.append(
            "| `{model}` | `{train}` | `{easy}` | `{hard}` | `{drop}` | `{pdrop}` | `{rdrop}` |".format(
                model=row["model_id"],
                train=row["train_ratio"],
                easy=_format_float(row["f1_at_test_1_1"]),
                hard=_format_float(row["f1_at_test_1_4"]),
                drop=_format_float(row["f1_drop_1_1_to_1_4"]),
                pdrop=_format_float(row["precision_drop_1_1_to_1_4"]),
                rdrop=_format_float(row["recall_drop_1_1_to_1_4"]),
            )
        )
    lines.extend(
        [
            "",
            "## F1 Matrices",
            "",
        ]
    )
    for model_id in sorted({row["model_id"] for row in f1_rows}):
        lines.extend(
            [
                f"### `{model_id}`",
                "",
                "| Train Ratio | Test 1:1 | Test 1:2 | Test 1:3 | Test 1:4 |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for row in [row for row in f1_rows if row["model_id"] == model_id]:
            lines.append(
                "| `{train}` | `{t11}` | `{t12}` | `{t13}` | `{t14}` |".format(
                    train=row["train_ratio"],
                    t11=_format_float(row["test_1_1_f1_mean"]),
                    t12=_format_float(row["test_1_2_f1_mean"]),
                    t13=_format_float(row["test_1_3_f1_mean"]),
                    t14=_format_float(row["test_1_4_f1_mean"]),
                )
            )
        lines.append("")
    lines.extend(
        [
            "Notes:",
            "",
            "- Fixed test-ratio slices isolate training-ratio effects.",
            "- Fixed train-ratio rows show evaluation-distribution sensitivity.",
            "- Recall drops are zero here because all test positives are retained while only test negatives are sampled.",
        ]
    )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(f1_rows) + len(best_rows) + len(sensitivity_rows)


def _index_rows(
    result_rows: list[Mapping[str, Any]],
) -> dict[tuple[str, str, str], Mapping[str, Any]]:
    return {
        (row["model_id"], row["train_ratio"], row["test_ratio"]): row
        for row in result_rows
    }


def _write_csv(
    rows: list[Mapping[str, Any]],
    output_path: str | Path,
    fieldnames: list[str],
) -> int:
    if not rows:
        raise ValueError("At least one analysis row is required")
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def _test_f1_column(test_ratio: str) -> str:
    return f"test_{test_ratio.replace(':', '_')}_f1_mean"


def _ratio_key(ratio_label: str) -> int:
    return int(ratio_label.split(":", maxsplit=1)[1])


def _format_float(value: float) -> str:
    return f"{value:.6f}"
