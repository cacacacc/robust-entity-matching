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
    load_threshold_diagnostic_rows,
    write_threshold_diagnostics_csv,
    write_threshold_diagnostics_markdown,
)


DEFAULT_SUMMARIES = [
    "results/summaries/wdc_unseen_logistic_regression_fit_v1/aggregate.json",
    "results/summaries/wdc_unseen_rf_svm_fit_v1/aggregate.json",
]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export AP and threshold-grid diagnostics from raw predictions."
    )
    parser.add_argument(
        "summaries",
        nargs="*",
        default=DEFAULT_SUMMARIES,
        help="Aggregate summary JSON paths.",
    )
    parser.add_argument(
        "--csv",
        default="reports/threshold_diagnostics.csv",
        help="Output CSV path.",
    )
    parser.add_argument(
        "--markdown",
        default="reports/threshold_diagnostics.md",
        help="Output Markdown path.",
    )
    args = parser.parse_args()

    rows = load_threshold_diagnostic_rows(args.summaries)
    csv_rows = write_threshold_diagnostics_csv(rows, args.csv)
    markdown_rows = write_threshold_diagnostics_markdown(rows, args.markdown)
    print(
        json.dumps(
            {
                "row_count": len(rows),
                "csv_rows_written": csv_rows,
                "markdown_rows_written": markdown_rows,
                "csv_path": args.csv,
                "markdown_path": args.markdown,
                "top_model_by_test_average_precision": rows[0]["model_id"],
                "top_test_average_precision_mean": rows[0][
                    "test_average_precision_mean"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
