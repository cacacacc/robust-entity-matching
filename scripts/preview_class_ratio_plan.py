from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.experiments import build_class_ratio_run_plan


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preview a class-ratio stress-test run plan without fitting."
    )
    parser.add_argument(
        "config",
        nargs="?",
        default="configs/experiments/wdc_class_ratio_stress_protocol.json",
        help="Path to the class-ratio protocol config.",
    )
    parser.add_argument(
        "--model",
        action="append",
        dest="models",
        help="Model ID to preview. Repeat for multiple models.",
    )
    args = parser.parse_args()

    summary = build_class_ratio_run_plan(args.config, model_ids=args.models)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
