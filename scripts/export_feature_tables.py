"""Export processed feature-table CSV files from interim pair-table JSONL files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.features import export_dataset_feature_tables


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", help="Path to a dataset config JSON file.")
    parser.add_argument(
        "--interim-root",
        default="data/interim",
        help="Directory containing dataset-specific interim JSONL files.",
    )
    parser.add_argument(
        "--output-root",
        default="data/processed",
        help="Directory where processed feature-table files are written.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = export_dataset_feature_tables(
        args.config,
        interim_root=args.interim_root,
        output_root=args.output_root,
    )
    print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
