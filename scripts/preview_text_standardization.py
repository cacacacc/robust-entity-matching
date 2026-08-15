"""Preview text standardization for interim pair-table JSONL files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.preprocessing import standardize_pair_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl_path", help="Path to an interim pair-table JSONL file.")
    parser.add_argument(
        "--examples",
        type=int,
        default=1,
        help="Number of examples to preview.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.jsonl_path)
    previews = []
    with path.open("r", encoding="utf-8") as file:
        for index, line in enumerate(file):
            if index >= args.examples:
                break
            payload = json.loads(line)
            standardized = standardize_pair_payload(payload)
            previews.append(
                {
                    "pair_id": standardized.get("pair_id"),
                    "label": standardized.get("label"),
                    "left_text_profile": standardized["left_text_profile"],
                    "right_text_profile": standardized["right_text_profile"],
                }
            )

    print(json.dumps(previews, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
