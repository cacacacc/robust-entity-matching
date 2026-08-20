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
    load_seen_unseen_error_profile_rows,
    summarize_seen_unseen_error_profiles,
    write_seen_unseen_error_profile_csv,
    write_seen_unseen_error_profile_markdown,
    write_seen_unseen_model_error_profile_csv,
)


DEFAULT_MODELS = ["logistic_regression", "random_forest", "svm"]
DEFAULT_SEEDS = [13, 29, 47, 71, 101]
UNSEEN_EXPERIMENT_BY_MODEL = {
    "logistic_regression": "wdc_unseen_logistic_regression_fit_v1",
    "random_forest": "wdc_unseen_rf_svm_fit_v1",
    "svm": "wdc_unseen_rf_svm_fit_v1",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export all-seed seen-vs-unseen error profiles from raw predictions."
    )
    parser.add_argument(
        "--dataset-config",
        default="configs/datasets/wdc_products_80pair.json",
        help="Dataset config path.",
    )
    parser.add_argument(
        "--seen-experiment",
        default="wdc_seen_baseline_fit_v1",
        help="Seen baseline prediction experiment ID.",
    )
    parser.add_argument(
        "--results-root",
        default="results",
        help="Results root containing prediction artifacts.",
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
        "--seed-csv",
        default="reports/seen_unseen_error_profile_by_seed.csv",
        help="Output seed-level CSV path.",
    )
    parser.add_argument(
        "--model-csv",
        default="reports/seen_unseen_error_profile_by_model.csv",
        help="Output model-level CSV path.",
    )
    parser.add_argument(
        "--markdown",
        default="reports/seen_unseen_error_profile.md",
        help="Output Markdown report path.",
    )
    args = parser.parse_args()

    prediction_pairs = _prediction_pairs(
        results_root=Path(args.results_root),
        seen_experiment=args.seen_experiment,
    )
    seed_rows = load_seen_unseen_error_profile_rows(
        dataset_config_path=args.dataset_config,
        prediction_pairs=prediction_pairs,
        seen_feature_table_path=args.seen_features,
        unseen_feature_table_path=args.unseen_features,
    )
    model_rows = summarize_seen_unseen_error_profiles(seed_rows)
    seed_count = write_seen_unseen_error_profile_csv(seed_rows, args.seed_csv)
    model_count = write_seen_unseen_model_error_profile_csv(model_rows, args.model_csv)
    markdown_count = write_seen_unseen_error_profile_markdown(
        seed_rows,
        model_rows,
        args.markdown,
    )
    print(
        json.dumps(
            {
                "seed_rows_written": seed_count,
                "model_rows_written": model_count,
                "markdown_rows_written": markdown_count,
                "seed_csv": args.seed_csv,
                "model_csv": args.model_csv,
                "markdown": args.markdown,
            },
            indent=2,
            sort_keys=True,
        )
    )


def _prediction_pairs(
    results_root: Path,
    seen_experiment: str,
) -> list[dict[str, Path]]:
    pairs = []
    for model_id in DEFAULT_MODELS:
        unseen_experiment = UNSEEN_EXPERIMENT_BY_MODEL[model_id]
        for seed in DEFAULT_SEEDS:
            pairs.append(
                {
                    "seen_prediction_path": results_root
                    / "predictions"
                    / seen_experiment
                    / model_id
                    / f"seed_{seed}"
                    / "test.csv",
                    "unseen_prediction_path": results_root
                    / "predictions"
                    / unseen_experiment
                    / model_id
                    / f"seed_{seed}"
                    / "test.csv",
                }
            )
    return pairs


if __name__ == "__main__":
    main()
