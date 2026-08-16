from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.experiments import build_baseline_run_plan


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preview a baseline run plan without fitting or predicting."
    )
    parser.add_argument("config", help="Path to a protocol-only experiment config")
    parser.add_argument(
        "--model",
        action="append",
        dest="models",
        help="Model ID to preview. Repeat for multiple models.",
    )
    parser.add_argument(
        "--results-root",
        default="results",
        help="Root directory for planned result artifacts.",
    )
    args = parser.parse_args()

    summary = build_baseline_run_plan(
        args.config,
        model_ids=args.models,
        results_root=args.results_root,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
