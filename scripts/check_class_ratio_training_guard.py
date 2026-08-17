from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.experiments import check_class_ratio_training_readiness


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check whether class-ratio training is allowed without fitting."
    )
    parser.add_argument(
        "config",
        nargs="?",
        default="configs/experiments/wdc_class_ratio_stress_protocol.json",
        help="Path to the class-ratio experiment config.",
    )
    parser.add_argument(
        "--model",
        action="append",
        dest="models",
        help="Model ID to check. Repeat for multiple models.",
    )
    args = parser.parse_args()

    readiness = check_class_ratio_training_readiness(
        args.config,
        model_ids=args.models,
    )
    print(json.dumps(readiness, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
