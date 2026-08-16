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
    load_baseline_comparison_rows,
    write_baseline_comparison_csv,
    write_baseline_comparison_markdown,
)


DEFAULT_SUMMARIES = [
    "results/summaries/wdc_unseen_logistic_regression_fit_v1/aggregate.json",
    "results/summaries/wdc_unseen_rf_svm_fit_v1/aggregate.json",
]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export a comparison table from aggregate baseline summaries."
    )
    parser.add_argument(
        "summaries",
        nargs="*",
        default=DEFAULT_SUMMARIES,
        help="Aggregate summary JSON paths.",
    )
    parser.add_argument(
        "--csv",
        default="reports/baseline_comparison.csv",
        help="Output CSV path.",
    )
    parser.add_argument(
        "--markdown",
        default="reports/baseline_comparison.md",
        help="Output Markdown path.",
    )
    args = parser.parse_args()

    rows = load_baseline_comparison_rows(args.summaries)
    csv_rows = write_baseline_comparison_csv(rows, args.csv)
    markdown_rows = write_baseline_comparison_markdown(rows, args.markdown)
    print(
        json.dumps(
            {
                "row_count": len(rows),
                "csv_rows_written": csv_rows,
                "markdown_rows_written": markdown_rows,
                "csv_path": args.csv,
                "markdown_path": args.markdown,
                "top_model": rows[0]["model_id"],
                "top_test_f1_mean": rows[0]["test_f1_mean"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
