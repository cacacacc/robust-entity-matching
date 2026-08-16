"""Preview configured baseline estimators without fitting them."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.models import (
    describe_estimator,
    instantiate_model_from_config,
    load_model_config,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", help="Path to a model config JSON file.")
    parser.add_argument("--seed", type=int, default=13, help="Preview random seed.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_model_config(args.config)
    estimators = {}
    for model in config["models"]:
        estimator = instantiate_model_from_config(
            args.config,
            model["model_id"],
            random_seed=args.seed,
        )
        estimators[model["model_id"]] = describe_estimator(estimator)
    print(
        json.dumps(
            {
                "status": "preview_only_not_fitted",
                "model_config": args.config,
                "seed": args.seed,
                "estimators": estimators,
            },
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
