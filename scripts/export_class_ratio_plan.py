from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.experiments import (
    build_class_ratio_run_plan,
    class_ratio_plan_rows,
    write_class_ratio_plan_csv,
    write_class_ratio_plan_markdown,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export a compact class-ratio stress-test plan."
    )
    parser.add_argument(
        "config",
        nargs="?",
        default="configs/experiments/wdc_class_ratio_stress_protocol.json",
        help="Path to the class-ratio protocol config.",
    )
    parser.add_argument(
        "--csv",
        default="reports/class_ratio_plan.csv",
        help="Output CSV path.",
    )
    parser.add_argument(
        "--markdown",
        default="reports/class_ratio_plan.md",
        help="Output Markdown path.",
    )
    args = parser.parse_args()

    plan = build_class_ratio_run_plan(args.config)
    rows = class_ratio_plan_rows(plan)
    csv_rows = write_class_ratio_plan_csv(rows, args.csv)
    markdown_rows = write_class_ratio_plan_markdown(rows, args.markdown)
    print(
        json.dumps(
            {
                "row_count": len(rows),
                "csv_rows_written": csv_rows,
                "markdown_rows_written": markdown_rows,
                "csv_path": args.csv,
                "markdown_path": args.markdown,
                "ratios": [row["match_to_non_match_ratio"] for row in rows],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
