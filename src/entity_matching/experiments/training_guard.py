"""Training-entry safety guards for Phase 3."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from entity_matching.experiments.dry_run import load_experiment_config


class TrainingNotAllowedError(PermissionError):
    """Raised when an experiment config does not explicitly allow fitting."""


def assert_fit_allowed(experiment_config: Mapping[str, Any]) -> None:
    """Raise unless an experiment config explicitly allows fitting."""

    if experiment_config.get("fit_allowed") is not True:
        blockers = experiment_config.get("fit_blockers", [])
        raise TrainingNotAllowedError(
            "Model fitting is not allowed by this experiment config. "
            f"Blockers: {blockers}"
        )


def assert_fit_allowed_from_config(config_path: str | Path) -> None:
    """Load an experiment config and assert fitting is explicitly allowed."""

    config = load_experiment_config(config_path)
    assert_fit_allowed(config)
