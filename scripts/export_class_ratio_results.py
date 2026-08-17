from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.evaluation import (
    load_class_ratio_result_rows,
    write_class_ratio_results_csv,
    write_class_ratio_results_markdown,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export compact class-ratio result tables."
    )
    parser.add_argument(
        "summary",
        nargs="?",
        default="results/summaries/wdc_class_ratio_stress_fit_v1/aggregate.json",
        help="Class-ratio aggregate summary JSON path.",
    )
    parser.add_argument(
        "--csv",
        default="reports/class_ratio_results.csv",
        help="Output CSV path.",
    )
    parser.add_argument(
        "--markdown",
        default="reports/class_ratio_results.md",
        help="Output Markdown path.",
    )
    args = parser.parse_args()

    rows = load_class_ratio_result_rows(args.summary)
    csv_rows = write_class_ratio_results_csv(rows, args.csv)
    summary = _load_summary(args.summary)
    markdown_rows = write_class_ratio_results_markdown(
        rows,
        args.markdown,
        title=_markdown_title(summary),
        test_policy_note=_test_policy_note(summary),
    )
    print(
        json.dumps(
            {
                "row_count": len(rows),
                "csv_rows_written": csv_rows,
                "markdown_rows_written": markdown_rows,
                "csv_path": args.csv,
                "markdown_path": args.markdown,
                "top_ratio": rows[0]["match_to_non_match_ratio"],
                "top_model": rows[0]["model_id"],
                "top_test_f1_mean": rows[0]["test_f1_mean"],
            },
            indent=2,
            sort_keys=True,
        )
    )


def _load_summary(summary_path: str) -> dict:
    with Path(summary_path).open("r", encoding="utf-8") as file:
        return json.load(file)


def _markdown_title(summary: dict) -> str:
    if _is_matched_train_test_summary(summary):
        return "Matched Train/Test Class-Ratio Results"
    return "Class-Ratio Stress-Test Results"


def _test_policy_note(summary: dict) -> str:
    if _is_matched_train_test_summary(summary):
        return (
            "Test negatives were sampled from `test_unseen_100un` so each test "
            "matrix matches the corresponding training ratio."
        )
    return "Test metrics were computed on fixed `test_unseen_100un`."


def _is_matched_train_test_summary(summary: dict) -> bool:
    return (
        summary.get("test_negative_per_positive_policy") == "match_training_ratio"
        or "matched_train_test" in summary.get("experiment_id", "")
    )


if __name__ == "__main__":
    main()
