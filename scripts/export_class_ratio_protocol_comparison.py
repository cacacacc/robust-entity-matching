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
    load_class_ratio_protocol_comparison_rows,
    write_class_ratio_protocol_comparison_csv,
    write_class_ratio_protocol_comparison_markdown,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export fixed-test versus matched train/test class-ratio comparison."
    )
    parser.add_argument(
        "--fixed-summary",
        default="results/summaries/wdc_class_ratio_stress_fit_v1/aggregate.json",
        help="Fixed-test class-ratio aggregate summary JSON path.",
    )
    parser.add_argument(
        "--matched-summary",
        default="results/summaries/wdc_class_ratio_matched_train_test_fit_v1/aggregate.json",
        help="Matched train/test class-ratio aggregate summary JSON path.",
    )
    parser.add_argument(
        "--csv",
        default="reports/class_ratio_protocol_comparison.csv",
        help="Output CSV path.",
    )
    parser.add_argument(
        "--markdown",
        default="reports/class_ratio_protocol_comparison.md",
        help="Output Markdown path.",
    )
    args = parser.parse_args()

    rows = load_class_ratio_protocol_comparison_rows(
        args.fixed_summary,
        args.matched_summary,
    )
    csv_rows = write_class_ratio_protocol_comparison_csv(rows, args.csv)
    markdown_rows = write_class_ratio_protocol_comparison_markdown(
        rows, args.markdown
    )
    top_delta = max(rows, key=lambda row: row["delta_test_f1_mean"])
    print(
        json.dumps(
            {
                "row_count": len(rows),
                "csv_rows_written": csv_rows,
                "markdown_rows_written": markdown_rows,
                "csv_path": args.csv,
                "markdown_path": args.markdown,
                "largest_delta_ratio": top_delta["match_to_non_match_ratio"],
                "largest_delta_model": top_delta["model_id"],
                "largest_delta_test_f1_mean": top_delta["delta_test_f1_mean"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
