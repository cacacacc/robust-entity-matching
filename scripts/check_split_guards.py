"""Check feature-table split manifests and leakage guards."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.splitting import assert_no_leakage, build_split_guard_report


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
        help="Optional split names to check. Defaults to all configured splits.",
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
        "--report-only",
        action="store_true",
        help="Print the report without failing on leakage.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_split_guard_report(
        args.config,
        processed_root=args.processed_root,
        split_names=args.splits,
    )
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if not args.report_only:
        assert_no_leakage(
            report,
            require_pair_disjoint=True,
            require_record_disjoint=args.require_record_disjoint,
            require_entity_disjoint=args.require_entity_disjoint,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
