"""Preview metric and threshold-selection scaffolding using toy scores."""

from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_matching.evaluation import evaluate_binary_scores, select_threshold_on_validation


def main() -> int:
    y_validation = [1, 1, 0, 0]
    validation_scores = [0.9, 0.6, 0.4, 0.2]
    threshold_summary = select_threshold_on_validation(
        y_validation,
        validation_scores,
        candidate_thresholds=[0.3, 0.5, 0.7],
        split_name="validation",
    )
    fixed_threshold_summary = evaluate_binary_scores(
        y_validation,
        validation_scores,
        threshold_summary["selected_threshold"],
    )
    print(
        json.dumps(
            {
                "status": "toy_preview_only",
                "note": "No model predictions or project experiment results are used here.",
                "threshold_selection": threshold_summary,
                "fixed_threshold_metrics": fixed_threshold_summary,
            },
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
