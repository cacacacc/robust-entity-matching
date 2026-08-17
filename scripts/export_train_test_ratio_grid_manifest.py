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
    build_train_test_ratio_grid_plan,
    train_test_ratio_grid_manifest_rows,
    write_train_test_ratio_grid_manifest_csv,
    write_train_test_ratio_grid_manifest_markdown,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export a dry manifest for a train/test ratio grid."
    )
    parser.add_argument(
        "config",
        nargs="?",
        default="configs/experiments/wdc_train_test_ratio_grid_protocol.json",
        help="Path to the train/test ratio grid protocol config.",
    )
    parser.add_argument(
        "--model",
        action="append",
        dest="models",
        help="Model ID to include. Repeat for multiple models.",
    )
    parser.add_argument(
        "--csv",
        default="reports/train_test_ratio_grid_manifest.csv",
        help="Output CSV path.",
    )
    parser.add_argument(
        "--markdown",
        default="reports/train_test_ratio_grid_manifest.md",
        help="Output Markdown path.",
    )
    args = parser.parse_args()

    plan = build_train_test_ratio_grid_plan(args.config, model_ids=args.models)
    rows = train_test_ratio_grid_manifest_rows(plan)
    csv_rows = write_train_test_ratio_grid_manifest_csv(rows, args.csv)
    markdown_rows = write_train_test_ratio_grid_manifest_markdown(rows, args.markdown)
    print(
        json.dumps(
            {
                "row_count": len(rows),
                "csv_rows_written": csv_rows,
                "markdown_rows_written": markdown_rows,
                "csv_path": args.csv,
                "markdown_path": args.markdown,
                "planned_fit_count": plan["planned_fit_count"],
                "planned_test_evaluation_count": plan[
                    "planned_test_evaluation_count"
                ],
                "fit_allowed": plan["fit_allowed"],
                "writes_files_now": plan["artifact_plan"]["writes_files_now"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
