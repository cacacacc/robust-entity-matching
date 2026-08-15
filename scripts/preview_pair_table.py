"""Load one split into the normalized pair-table representation and summarize it."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.data import load_pair_table, summarize_pair_table


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", help="Path to a dataset config JSON file.")
    parser.add_argument("split", help="Split name from the dataset config.")
    parser.add_argument("--examples", type=int, default=1, help="Number of example pairs.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pair_table = load_pair_table(args.config, args.split)
    payload = {
        "summary": summarize_pair_table(pair_table),
        "examples": [pair.__dict__ for pair in pair_table[: args.examples]],
    }
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

