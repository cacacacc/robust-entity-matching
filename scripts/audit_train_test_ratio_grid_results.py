from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.evaluation import audit_train_test_ratio_grid_result_summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit train/test ratio grid results against raw predictions."
    )
    parser.add_argument(
        "summary",
        nargs="?",
        default="results/summaries/wdc_train_test_ratio_grid_fit_v1/aggregate.json",
        help="Train/test ratio grid aggregate summary JSON path.",
    )
    args = parser.parse_args()

    audit = audit_train_test_ratio_grid_result_summary(args.summary)
    cell_count = sum(
        len(model_audits)
        for test_ratio_audits in audit["cell_audits"].values()
        for model_audits in test_ratio_audits.values()
    )
    print(
        json.dumps(
            {
                "audit_status": audit["audit_status"],
                "experiment_id": audit["experiment_id"],
                "summary_path": audit["summary_path"],
                "seed_audit_count": len(audit["seed_audits"]),
                "cell_audit_count": cell_count,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
