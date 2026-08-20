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
    load_train_test_ratio_grid_analysis,
    write_best_train_by_test_ratio_csv,
    write_f1_matrix_csv,
    write_test_ratio_sensitivity_csv,
    write_train_test_ratio_grid_analysis_markdown,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export derived analysis tables for train/test ratio grid results."
    )
    parser.add_argument(
        "summary",
        nargs="?",
        default="results/summaries/wdc_train_test_ratio_grid_fit_v1/aggregate.json",
        help="Train/test ratio grid aggregate summary JSON path.",
    )
    parser.add_argument(
        "--f1-matrix-csv",
        default="reports/train_test_ratio_grid_f1_matrix.csv",
        help="Output F1 matrix CSV path.",
    )
    parser.add_argument(
        "--best-train-csv",
        default="reports/train_test_ratio_grid_best_train_by_test_ratio.csv",
        help="Output best-train-by-test-ratio CSV path.",
    )
    parser.add_argument(
        "--sensitivity-csv",
        default="reports/train_test_ratio_grid_test_sensitivity.csv",
        help="Output test-ratio sensitivity CSV path.",
    )
    parser.add_argument(
        "--markdown",
        default="reports/train_test_ratio_grid_analysis.md",
        help="Output analysis Markdown path.",
    )
    args = parser.parse_args()

    analysis = load_train_test_ratio_grid_analysis(args.summary)
    f1_rows = write_f1_matrix_csv(
        analysis["f1_matrix_rows"],
        args.f1_matrix_csv,
    )
    best_rows = write_best_train_by_test_ratio_csv(
        analysis["best_train_by_test_ratio_rows"],
        args.best_train_csv,
    )
    sensitivity_rows = write_test_ratio_sensitivity_csv(
        analysis["test_ratio_sensitivity_rows"],
        args.sensitivity_csv,
    )
    markdown_rows = write_train_test_ratio_grid_analysis_markdown(
        analysis,
        args.markdown,
    )
    print(
        json.dumps(
            {
                "f1_matrix_rows_written": f1_rows,
                "best_train_rows_written": best_rows,
                "sensitivity_rows_written": sensitivity_rows,
                "markdown_rows_written": markdown_rows,
                "f1_matrix_csv": args.f1_matrix_csv,
                "best_train_csv": args.best_train_csv,
                "sensitivity_csv": args.sensitivity_csv,
                "markdown": args.markdown,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
