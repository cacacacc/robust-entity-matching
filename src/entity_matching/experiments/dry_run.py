"""Dry-run scaffolding for baseline experiments without fitting models."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any, Mapping

from entity_matching.models import load_model_matrix_bundle


class ExperimentConfigError(ValueError):
    """Raised when an experiment config is unsafe or incomplete."""


def load_experiment_config(path: str | Path) -> dict[str, Any]:
    """Load an experiment config JSON file."""

    with Path(path).open("r", encoding="utf-8") as file:
        config = json.load(file)
    validate_experiment_config(config)
    return config


def validate_experiment_config(config: Mapping[str, Any]) -> None:
    """Validate required dry-run experiment config fields."""

    required = {
        "experiment_id",
        "status",
        "dataset_config",
        "model_config",
        "processed_root",
        "splits",
        "guards",
        "fit_allowed",
        "fit_blockers",
    }
    missing = required - set(config)
    if missing:
        raise ExperimentConfigError(f"Experiment config missing keys: {sorted(missing)}")
    if config["status"] != "dry_run_only":
        raise ExperimentConfigError("Only dry_run_only experiment configs are allowed now")
    if config["fit_allowed"] is not False:
        raise ExperimentConfigError("Fitting must remain disabled in Phase 2 dry runs")

    splits = config["splits"]
    if not splits.get("train") or not splits.get("test"):
        raise ExperimentConfigError("Dry-run config must define train and test splits")
    if splits.get("validation") is not None:
        raise ExperimentConfigError("Validation split is not locked for this dry run")

    guards = config["guards"]
    for key in (
        "require_pair_disjoint",
        "require_record_disjoint",
        "require_entity_disjoint",
    ):
        if guards.get(key) is not True:
            raise ExperimentConfigError(f"Strict guard must be true: {key}")

    if not config["fit_blockers"]:
        raise ExperimentConfigError("Dry-run config must explain why fitting is blocked")


def baseline_dependency_status() -> dict[str, bool]:
    """Report optional baseline dependency availability without importing estimators."""

    return {
        "sklearn_available": importlib.util.find_spec("sklearn") is not None,
        "numpy_available": importlib.util.find_spec("numpy") is not None,
        "pandas_available": importlib.util.find_spec("pandas") is not None,
    }


def _load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def run_experiment_dry_run(config_path: str | Path) -> dict[str, Any]:
    """Validate planned baseline inputs and matrix loading without fitting models."""

    config = load_experiment_config(config_path)
    model_config = _load_json(config["model_config"])
    split_names = [config["splits"]["train"], config["splits"]["test"]]

    bundle = load_model_matrix_bundle(
        config["dataset_config"],
        processed_root=config["processed_root"],
        split_names=split_names,
        require_pair_disjoint=config["guards"]["require_pair_disjoint"],
        require_record_disjoint=config["guards"]["require_record_disjoint"],
        require_entity_disjoint=config["guards"]["require_entity_disjoint"],
    )

    return {
        "experiment_id": config["experiment_id"],
        "status": config["status"],
        "ready_for_fit": False,
        "fit_allowed": config["fit_allowed"],
        "fit_blockers": config["fit_blockers"],
        "dataset_config": config["dataset_config"],
        "model_config": config["model_config"],
        "planned_first_model": config.get("planned_first_model"),
        "planned_model_config_status": model_config.get("status"),
        "planned_training_status": model_config.get("training_status"),
        "dependency_status": baseline_dependency_status(),
        "matrix_summary": bundle.to_summary(),
    }
