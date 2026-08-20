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
    load_seen_unseen_comparison_rows,
    write_seen_unseen_comparison_csv,
    write_seen_unseen_comparison_markdown,
)


DEFAULT_UNSEEN_SUMMARIES = [
    "results/summaries/wdc_unseen_logistic_regression_fit_v1/aggregate.json",
    "results/summaries/wdc_unseen_rf_svm_fit_v1/aggregate.json",
]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export WDC seen-vs-unseen baseline comparison tables."
    )
    parser.add_argument(
        "--seen-summary",
        default="results/summaries/wdc_seen_baseline_fit_v1/aggregate.json",
        help="Seen-test aggregate summary JSON path.",
    )
    parser.add_argument(
        "--unseen-summary",
        action="append",
        dest="unseen_summaries",
        help="Unseen-test aggregate summary JSON path. Repeat for multiple summaries.",
    )
    parser.add_argument(
        "--csv",
        default="reports/seen_vs_unseen_comparison.csv",
        help="Output CSV path.",
    )
    parser.add_argument(
        "--markdown",
        default="reports/seen_vs_unseen_comparison.md",
        help="Output Markdown path.",
    )
    args = parser.parse_args()

    rows = load_seen_unseen_comparison_rows(
        args.seen_summary,
        args.unseen_summaries or DEFAULT_UNSEEN_SUMMARIES,
    )
    csv_rows = write_seen_unseen_comparison_csv(rows, args.csv)
    markdown_rows = write_seen_unseen_comparison_markdown(rows, args.markdown)
    top_delta = max(rows, key=lambda row: row["unseen_minus_seen_f1"])
    print(
        json.dumps(
            {
                "row_count": len(rows),
                "csv_rows_written": csv_rows,
                "markdown_rows_written": markdown_rows,
                "csv_path": args.csv,
                "markdown_path": args.markdown,
                "largest_unseen_minus_seen_model": top_delta["model_id"],
                "largest_unseen_minus_seen_f1": top_delta["unseen_minus_seen_f1"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
