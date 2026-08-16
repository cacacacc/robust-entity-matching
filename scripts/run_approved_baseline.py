from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.experiments import run_approved_baseline_training


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run an explicitly approved traditional baseline experiment."
    )
    parser.add_argument("config", help="Path to a fit-enabled experiment config")
    args = parser.parse_args()

    summary = run_approved_baseline_training(args.config)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
