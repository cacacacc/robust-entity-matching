from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.experiments import run_approved_train_test_ratio_grid_training


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run an approved train/test ratio grid training experiment."
    )
    parser.add_argument(
        "config",
        help="Path to a fit-enabled approved train/test ratio grid config.",
    )
    args = parser.parse_args()

    aggregate = run_approved_train_test_ratio_grid_training(args.config)
    print(
        json.dumps(
            {
                "experiment_id": aggregate["experiment_id"],
                "status": aggregate["status"],
                "planned_fit_count": aggregate["planned_fit_count"],
                "planned_test_evaluation_count": aggregate[
                    "planned_test_evaluation_count"
                ],
                "seed_result_count": len(aggregate["seed_results"]),
                "summary_path": str(
                    Path("results")
                    / "summaries"
                    / aggregate["experiment_id"]
                    / "aggregate.json"
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
