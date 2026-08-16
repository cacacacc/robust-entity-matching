"""Instantiate traditional baseline estimators without fitting them."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Mapping


class ModelFactoryError(ValueError):
    """Raised when a baseline model cannot be instantiated safely."""


def load_model_config(path: str | Path) -> dict[str, Any]:
    """Load a model config JSON file."""

    with Path(path).open("r", encoding="utf-8") as file:
        config = json.load(file)
    required = {"config_id", "models", "training_status"}
    missing = required - set(config)
    if missing:
        raise ModelFactoryError(f"Model config missing keys: {sorted(missing)}")
    return config


def get_model_definition(model_config: Mapping[str, Any], model_id: str) -> dict[str, Any]:
    """Return one model definition from a model config."""

    for model in model_config["models"]:
        if model["model_id"] == model_id:
            return dict(model)
    raise ModelFactoryError(f"Unknown model_id: {model_id}")


def instantiate_model(
    model_definition: Mapping[str, Any], *, random_seed: int | None = None
) -> Any:
    """Instantiate a configured sklearn estimator without fitting it."""

    family = model_definition["family"]
    parameters = copy.deepcopy(model_definition.get("parameters", {}))
    if random_seed is not None and "random_state" in parameters:
        parameters["random_state"] = random_seed

    if family == "LogisticRegression":
        from sklearn.linear_model import LogisticRegression

        return LogisticRegression(**parameters)
    if family == "RandomForestClassifier":
        from sklearn.ensemble import RandomForestClassifier

        return RandomForestClassifier(**parameters)
    if family == "SupportVectorMachine":
        from sklearn.svm import SVC

        return SVC(**parameters)

    raise ModelFactoryError(f"Unsupported model family: {family}")


def instantiate_model_from_config(
    config_path: str | Path, model_id: str, *, random_seed: int | None = None
) -> Any:
    """Load a model config and instantiate one estimator without fitting it."""

    config = load_model_config(config_path)
    definition = get_model_definition(config, model_id)
    return instantiate_model(definition, random_seed=random_seed)


def describe_estimator(estimator: Any) -> dict[str, Any]:
    """Return a compact description for an unfitted estimator."""

    return {
        "class": estimator.__class__.__name__,
        "module": estimator.__class__.__module__,
        "parameters": estimator.get_params(deep=False),
        "is_fitted": _looks_fitted(estimator),
    }


def _looks_fitted(estimator: Any) -> bool:
    return any(name.endswith("_") and not name.startswith("__") for name in vars(estimator))
