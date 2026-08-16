from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.evaluation.error_analysis import (
    analyze_prediction_errors,
    write_error_analysis_json,
    write_error_analysis_markdown,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze false positives and false negatives from raw predictions."
    )
    parser.add_argument(
        "--dataset-config",
        default="configs/datasets/wdc_products_80pair.json",
        help="Dataset config path.",
    )
    parser.add_argument(
        "--split",
        default="test_unseen_100un",
        help="Dataset split name represented by the prediction file.",
    )
    parser.add_argument(
        "--prediction",
        default="results/predictions/wdc_unseen_rf_svm_fit_v1/random_forest/seed_13/test.csv",
        help="Raw prediction CSV path.",
    )
    parser.add_argument(
        "--features",
        default="data/processed/wdc_products_80pair/test_unseen_100un.csv",
        help="Processed feature table CSV path.",
    )
    parser.add_argument(
        "--output-json",
        default="results/error_analysis/wdc_unseen_rf_svm_fit_v1/random_forest/seed_13_test_error_analysis.json",
        help="Output JSON path.",
    )
    parser.add_argument(
        "--output-markdown",
        default="results/error_analysis/wdc_unseen_rf_svm_fit_v1/random_forest/seed_13_test_error_analysis.md",
        help="Output Markdown path.",
    )
    parser.add_argument(
        "--examples",
        type=int,
        default=10,
        help="Number of examples per error type.",
    )
    args = parser.parse_args()

    analysis = analyze_prediction_errors(
        dataset_config_path=args.dataset_config,
        split=args.split,
        prediction_path=args.prediction,
        feature_table_path=args.features,
        examples_per_error_type=args.examples,
    )
    write_error_analysis_json(analysis, args.output_json)
    write_error_analysis_markdown(analysis, args.output_markdown)
    print(
        json.dumps(
            {
                "schema_version": analysis["schema_version"],
                "model_id": analysis["model_id"],
                "seed": analysis["seed"],
                "split": analysis["split"],
                "confusion_counts": analysis["confusion_counts"],
                "output_json": args.output_json,
                "output_markdown": args.output_markdown,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
