from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.evaluation import audit_baseline_result_summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit an aggregate result summary against raw prediction CSV files."
    )
    parser.add_argument("summary", help="Path to aggregate.json")
    args = parser.parse_args()

    audit = audit_baseline_result_summary(args.summary)
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
