"""Preview model-ready X/y/pair_id matrices without fitting models."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.models import load_model_matrix_bundle


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", help="Path to a dataset config JSON file.")
    parser.add_argument(
        "--processed-root",
        default="data/processed",
        help="Directory containing dataset-specific processed feature tables.",
    )
    parser.add_argument(
        "--splits",
        nargs="+",
        help="Optional split names to load. Defaults to all configured splits.",
    )
    parser.add_argument(
        "--require-record-disjoint",
        action="store_true",
        help="Fail if selected splits share source record IDs.",
    )
    parser.add_argument(
        "--require-entity-disjoint",
        action="store_true",
        help="Fail if selected splits share entity IDs, or if entity IDs are unavailable.",
    )
    parser.add_argument(
        "--allow-pair-leakage",
        action="store_true",
        help="Allow duplicate/cross-split pair IDs for diagnostic preview only.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundle = load_model_matrix_bundle(
        args.config,
        processed_root=args.processed_root,
        split_names=args.splits,
        require_pair_disjoint=not args.allow_pair_leakage,
        require_record_disjoint=args.require_record_disjoint,
        require_entity_disjoint=args.require_entity_disjoint,
    )
    summary = bundle.to_summary()
    for split, matrix in bundle.matrices.items():
        summary["splits"][split]["first_pair_id"] = matrix.pair_ids[0]
        summary["splits"][split]["first_label"] = matrix.y[0]
        summary["splits"][split]["first_feature_vector_length"] = len(matrix.X[0])
    print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
