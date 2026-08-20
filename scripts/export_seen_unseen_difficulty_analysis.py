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
    load_seen_unseen_difficulty_analysis,
    write_feature_difficulty_csv,
    write_seen_unseen_difficulty_markdown,
    write_split_difficulty_summary_csv,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export aggregate split-difficulty analysis for WDC seen/unseen tests."
    )
    parser.add_argument(
        "--dataset-config",
        default="configs/datasets/wdc_products_80pair.json",
        help="Dataset config path.",
    )
    parser.add_argument(
        "--seen-prediction",
        default="results/predictions/wdc_seen_baseline_fit_v1/random_forest/seed_13/test.csv",
        help="Seen-test raw prediction CSV path.",
    )
    parser.add_argument(
        "--unseen-prediction",
        default="results/predictions/wdc_unseen_rf_svm_fit_v1/random_forest/seed_13/test.csv",
        help="Unseen-test raw prediction CSV path.",
    )
    parser.add_argument(
        "--seen-features",
        default="data/processed/wdc_products_80pair/test_seen_000un.csv",
        help="Seen-test processed feature table path.",
    )
    parser.add_argument(
        "--unseen-features",
        default="data/processed/wdc_products_80pair/test_unseen_100un.csv",
        help="Unseen-test processed feature table path.",
    )
    parser.add_argument(
        "--summary-csv",
        default="reports/seen_unseen_split_difficulty.csv",
        help="Output split summary CSV path.",
    )
    parser.add_argument(
        "--feature-csv",
        default="reports/seen_unseen_feature_difficulty.csv",
        help="Output feature-group CSV path.",
    )
    parser.add_argument(
        "--markdown",
        default="reports/seen_unseen_difficulty_analysis.md",
        help="Output Markdown report path.",
    )
    args = parser.parse_args()

    analysis = load_seen_unseen_difficulty_analysis(
        dataset_config_path=args.dataset_config,
        seen_prediction_path=args.seen_prediction,
        unseen_prediction_path=args.unseen_prediction,
        seen_feature_table_path=args.seen_features,
        unseen_feature_table_path=args.unseen_features,
    )
    summary_rows = write_split_difficulty_summary_csv(
        analysis["split_summary_rows"],
        args.summary_csv,
    )
    feature_rows = write_feature_difficulty_csv(
        analysis["feature_group_rows"],
        args.feature_csv,
    )
    markdown_rows = write_seen_unseen_difficulty_markdown(
        analysis,
        args.markdown,
    )
    seen = next(
        row for row in analysis["split_summary_rows"] if row["split_label"] == "seen"
    )
    unseen = next(
        row for row in analysis["split_summary_rows"] if row["split_label"] == "unseen"
    )
    print(
        json.dumps(
            {
                "summary_rows_written": summary_rows,
                "feature_rows_written": feature_rows,
                "markdown_rows_written": markdown_rows,
                "summary_csv": args.summary_csv,
                "feature_csv": args.feature_csv,
                "markdown": args.markdown,
                "seen_fp": seen["fp"],
                "unseen_fp": unseen["fp"],
                "seen_f1": seen["f1"],
                "unseen_f1": unseen["f1"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
