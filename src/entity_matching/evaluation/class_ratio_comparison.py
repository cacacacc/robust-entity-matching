"""Compare fixed-test and matched train/test class-ratio summaries."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping


CLASS_RATIO_PROTOCOL_COMPARISON_COLUMNS = [
    "ratio_id",
    "match_to_non_match_ratio",
    "model_id",
    "fixed_test_label_counts",
    "matched_test_label_counts",
    "fixed_test_f1_mean",
    "matched_test_f1_mean",
    "delta_test_f1_mean",
    "fixed_test_precision_mean",
    "matched_test_precision_mean",
    "delta_test_precision_mean",
    "fixed_test_recall_mean",
    "matched_test_recall_mean",
    "delta_test_recall_mean",
]


class ClassRatioProtocolComparisonError(ValueError):
    """Raised when class-ratio protocol comparison inputs are invalid."""


def load_class_ratio_protocol_comparison_rows(
    fixed_summary_path: str | Path,
    matched_summary_path: str | Path,
) -> list[dict[str, Any]]:
    """Load rows comparing fixed-test and matched-test class-ratio results."""

    fixed_summary = _load_completed_summary(fixed_summary_path)
    matched_summary = _load_completed_summary(matched_summary_path)
    fixed_rows = _result_index(fixed_summary)
    matched_rows = _result_index(matched_summary)
    if set(fixed_rows) != set(matched_rows):
        raise ClassRatioProtocolComparisonError(
            "Fixed and matched summaries must contain the same ratio/model keys"
        )

    fixed_counts = _test_label_counts_by_ratio(fixed_summary)
    matched_counts = _test_label_counts_by_ratio(matched_summary)

    rows = []
    for ratio_id, model_id in sorted(fixed_rows, key=_sort_key):
        fixed = fixed_rows[(ratio_id, model_id)]
        matched = matched_rows[(ratio_id, model_id)]
        rows.append(
            {
                "ratio_id": ratio_id,
                "match_to_non_match_ratio": fixed["match_to_non_match_ratio"],
                "model_id": model_id,
                "fixed_test_label_counts": fixed_counts[ratio_id],
                "matched_test_label_counts": matched_counts[ratio_id],
                "fixed_test_f1_mean": fixed["test_f1_mean"],
                "matched_test_f1_mean": matched["test_f1_mean"],
                "delta_test_f1_mean": matched["test_f1_mean"]
                - fixed["test_f1_mean"],
                "fixed_test_precision_mean": fixed["test_precision_mean"],
                "matched_test_precision_mean": matched["test_precision_mean"],
                "delta_test_precision_mean": matched["test_precision_mean"]
                - fixed["test_precision_mean"],
                "fixed_test_recall_mean": fixed["test_recall_mean"],
                "matched_test_recall_mean": matched["test_recall_mean"],
                "delta_test_recall_mean": matched["test_recall_mean"]
                - fixed["test_recall_mean"],
            }
        )
    return rows


def write_class_ratio_protocol_comparison_csv(
    rows: list[Mapping[str, Any]],
    output_path: str | Path,
) -> int:
    """Write fixed-versus-matched class-ratio comparison rows to CSV."""

    if not rows:
        raise ClassRatioProtocolComparisonError(
            "At least one protocol comparison row is required"
        )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=CLASS_RATIO_PROTOCOL_COMPARISON_COLUMNS
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(_format_csv_row(row))
    return len(rows)


def write_class_ratio_protocol_comparison_markdown(
    rows: list[Mapping[str, Any]],
    output_path: str | Path,
) -> int:
    """Write a compact fixed-versus-matched class-ratio comparison report."""

    if not rows:
        raise ClassRatioProtocolComparisonError(
            "At least one protocol comparison row is required"
        )
    lines = [
        "# Fixed-Test vs Matched Train/Test Class-Ratio Comparison",
        "",
        "Protocol: WDC Products `train_small` / `valid_small` / `test_unseen_100un`.",
        "",
        "| Ratio | Model | Fixed F1 | Matched F1 | Delta F1 | Fixed Precision | Matched Precision | Fixed Recall | Matched Recall |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| `{ratio}` | `{model}` | `{fixed_f1}` | `{matched_f1}` | `{delta_f1}` | `{fixed_precision}` | `{matched_precision}` | `{fixed_recall}` | `{matched_recall}` |".format(
                ratio=row["match_to_non_match_ratio"],
                model=row["model_id"],
                fixed_f1=_format_float(row["fixed_test_f1_mean"]),
                matched_f1=_format_float(row["matched_test_f1_mean"]),
                delta_f1=_format_signed_float(row["delta_test_f1_mean"]),
                fixed_precision=_format_float(row["fixed_test_precision_mean"]),
                matched_precision=_format_float(row["matched_test_precision_mean"]),
                fixed_recall=_format_float(row["fixed_test_recall_mean"]),
                matched_recall=_format_float(row["matched_test_recall_mean"]),
            )
        )
    lines.extend(
        [
            "",
            "Notes:",
            "",
            "- Fixed-test results keep the original `test_unseen_100un` ratio of 500 matches and 4000 non-matches.",
            "- Matched train/test results sample test negatives so the test ratio matches the corresponding training ratio.",
            "- Thresholds were selected on the same fixed validation split in both protocols.",
            "- Positive deltas mainly reflect evaluation-distribution changes and must not be read as pure training-ratio improvements.",
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
        raise ClassRatioProtocolComparisonError(
            f"Aggregate summary is not completed: {summary_path}"
        )
    return summary


def _result_index(summary: Mapping[str, Any]) -> dict[tuple[str, str], dict[str, float]]:
    rows = {}
    for ratio_id, model_summaries in summary["ratios"].items():
        for model_id, model_summary in model_summaries.items():
            rows[(ratio_id, model_id)] = {
                "match_to_non_match_ratio": model_summary[
                    "match_to_non_match_ratio"
                ],
                "test_f1_mean": float(model_summary["test_f1_mean"]),
                "test_precision_mean": float(model_summary["test_precision_mean"]),
                "test_recall_mean": float(model_summary["test_recall_mean"]),
            }
    return rows


def _test_label_counts_by_ratio(
    summary: Mapping[str, Any],
) -> dict[str, dict[str, int]]:
    counts = {}
    for seed_result in summary["seed_results"]:
        ratio_id = seed_result["ratio_id"]
        label_counts = {
            str(label): int(count)
            for label, count in seed_result["test_label_counts"].items()
        }
        if ratio_id in counts and counts[ratio_id] != label_counts:
            raise ClassRatioProtocolComparisonError(
                f"Inconsistent test label counts for ratio_id {ratio_id}"
            )
        counts[ratio_id] = label_counts
    return counts


def _sort_key(key: tuple[str, str]) -> tuple[int, str]:
    ratio_id, model_id = key
    return (int(ratio_id.rsplit("_", maxsplit=1)[-1]), model_id)


def _format_csv_row(row: Mapping[str, Any]) -> dict[str, Any]:
    formatted = dict(row)
    formatted["fixed_test_label_counts"] = json.dumps(
        formatted["fixed_test_label_counts"], sort_keys=True
    )
    formatted["matched_test_label_counts"] = json.dumps(
        formatted["matched_test_label_counts"], sort_keys=True
    )
    return formatted


def _format_float(value: float) -> str:
    return f"{value:.6f}"


def _format_signed_float(value: float) -> str:
    return f"{value:+.6f}"
