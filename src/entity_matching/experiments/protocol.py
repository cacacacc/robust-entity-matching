"""Experiment protocol validation before model fitting."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from entity_matching.splitting import assert_no_leakage, build_split_guard_report


class ExperimentProtocolError(ValueError):
    """Raised when an experiment protocol config is unsafe or incomplete."""


def load_protocol_config(path: str | Path) -> dict[str, Any]:
    """Load and validate a protocol-only experiment config."""

    with Path(path).open("r", encoding="utf-8") as file:
        config = json.load(file)
    validate_protocol_config(config)
    return config


def validate_protocol_config(config: Mapping[str, Any]) -> None:
    """Validate split roles and threshold-selection rules."""

    required = {
        "experiment_id",
        "status",
        "dataset_config",
        "model_config",
        "processed_root",
        "splits",
        "development_to_test_guards",
        "train_validation_guards",
        "threshold_selection",
        "final_test_policy",
        "random_seeds",
        "fit_allowed",
        "fit_blockers",
    }
    missing = required - set(config)
    if missing:
        raise ExperimentProtocolError(
            f"Protocol config missing keys: {sorted(missing)}"
        )
    if config["status"] != "protocol_locked_no_fit":
        raise ExperimentProtocolError(
            "Only protocol_locked_no_fit configs are supported here"
        )
    if config["fit_allowed"] is not False:
        raise ExperimentProtocolError("Protocol configs must not allow fitting")

    splits = config["splits"]
    for role in ("train", "validation", "test"):
        if not splits.get(role):
            raise ExperimentProtocolError(f"Missing split role: {role}")
    if len({splits["train"], splits["validation"], splits["test"]}) != 3:
        raise ExperimentProtocolError("Train, validation, and test splits must differ")

    threshold_selection = config["threshold_selection"]
    if threshold_selection.get("split_role") != "validation":
        raise ExperimentProtocolError("Threshold selection must use validation split")
    if threshold_selection.get("selection_metric") != "f1":
        raise ExperimentProtocolError("Only F1 threshold selection is locked now")
    _validate_threshold_grid(threshold_selection.get("candidate_thresholds"))

    final_test_policy = config["final_test_policy"]
    if final_test_policy.get("test_split_role") != "test":
        raise ExperimentProtocolError("Final test policy must name the test role")
    for key in ("use_test_for_threshold_selection", "use_test_for_model_selection"):
        if final_test_policy.get(key) is not False:
            raise ExperimentProtocolError(f"Test-set tuning is forbidden: {key}")

    if not config["random_seeds"]:
        raise ExperimentProtocolError("At least one random seed is required")
    if len(set(config["random_seeds"])) != len(config["random_seeds"]):
        raise ExperimentProtocolError("Random seeds must be unique")
    if not all(isinstance(seed, int) for seed in config["random_seeds"]):
        raise ExperimentProtocolError("Random seeds must be integers")
    if not config["fit_blockers"]:
        raise ExperimentProtocolError("Protocol config must explain why fitting is blocked")


def validate_protocol_guards(config_path: str | Path) -> dict[str, Any]:
    """Validate leakage guards for the locked split protocol."""

    config = load_protocol_config(config_path)
    splits = config["splits"]
    dataset_config = config["dataset_config"]
    processed_root = config["processed_root"]

    train_validation_report = build_split_guard_report(
        dataset_config,
        processed_root=processed_root,
        split_names=[splits["train"], splits["validation"]],
    )
    assert_no_leakage(
        train_validation_report,
        require_pair_disjoint=config["train_validation_guards"][
            "require_pair_disjoint"
        ],
        require_record_disjoint=config["train_validation_guards"][
            "require_record_disjoint"
        ],
        require_entity_disjoint=config["train_validation_guards"][
            "require_entity_disjoint"
        ],
    )

    development_to_test_reports = {}
    for role in ("train", "validation"):
        report = build_split_guard_report(
            dataset_config,
            processed_root=processed_root,
            split_names=[splits[role], splits["test"]],
        )
        assert_no_leakage(
            report,
            require_pair_disjoint=config["development_to_test_guards"][
                "require_pair_disjoint"
            ],
            require_record_disjoint=config["development_to_test_guards"][
                "require_record_disjoint"
            ],
            require_entity_disjoint=config["development_to_test_guards"][
                "require_entity_disjoint"
            ],
        )
        development_to_test_reports[f"{role}_to_test"] = report

    return {
        "experiment_id": config["experiment_id"],
        "status": config["status"],
        "fit_allowed": config["fit_allowed"],
        "splits": splits,
        "threshold_selection": config["threshold_selection"],
        "final_test_policy": config["final_test_policy"],
        "random_seeds": config["random_seeds"],
        "train_validation_guard_report": train_validation_report,
        "development_to_test_guard_reports": development_to_test_reports,
        "protocol_ready_for_fit_config": False,
        "remaining_fit_blockers": config["fit_blockers"],
    }


def _validate_threshold_grid(grid: Mapping[str, Any] | None) -> None:
    if grid is None:
        raise ExperimentProtocolError("Threshold candidate grid is required")
    start = grid.get("start")
    end = grid.get("end")
    step = grid.get("step")
    if not all(isinstance(value, (int, float)) for value in (start, end, step)):
        raise ExperimentProtocolError("Threshold grid values must be numeric")
    if start < 0.0 or end > 1.0 or start >= end:
        raise ExperimentProtocolError("Threshold grid must be within [0, 1]")
    if step <= 0.0:
        raise ExperimentProtocolError("Threshold grid step must be positive")
