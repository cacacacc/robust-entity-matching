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
    load_train_test_ratio_grid_result_rows,
    write_train_test_ratio_grid_results_csv,
    write_train_test_ratio_grid_results_markdown,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export compact train/test ratio grid result tables."
    )
    parser.add_argument(
        "summary",
        nargs="?",
        default="results/summaries/wdc_train_test_ratio_grid_fit_v1/aggregate.json",
        help="Train/test ratio grid aggregate summary JSON path.",
    )
    parser.add_argument(
        "--csv",
        default="reports/train_test_ratio_grid_results.csv",
        help="Output CSV path.",
    )
    parser.add_argument(
        "--markdown",
        default="reports/train_test_ratio_grid_results.md",
        help="Output Markdown path.",
    )
    args = parser.parse_args()

    rows = load_train_test_ratio_grid_result_rows(args.summary)
    csv_rows = write_train_test_ratio_grid_results_csv(rows, args.csv)
    markdown_rows = write_train_test_ratio_grid_results_markdown(rows, args.markdown)
    print(
        json.dumps(
            {
                "row_count": len(rows),
                "csv_rows_written": csv_rows,
                "markdown_rows_written": markdown_rows,
                "csv_path": args.csv,
                "markdown_path": args.markdown,
                "top_train_ratio": rows[0]["train_ratio"],
                "top_test_ratio": rows[0]["test_ratio"],
                "top_model": rows[0]["model_id"],
                "top_test_f1_mean": rows[0]["test_f1_mean"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
