"""Training-entry safety guards for Phase 3."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


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

    with Path(config_path).open("r", encoding="utf-8") as file:
        config = json.load(file)
    assert_fit_allowed(config)
