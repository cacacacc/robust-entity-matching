"""Guarded execution for approved traditional baseline runs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import statistics
import time
from typing import Any, Iterable, Mapping

from entity_matching.evaluation import (
    RAW_PREDICTION_SCHEMA_VERSION,
    apply_threshold,
    evaluate_binary_scores,
    prediction_artifact_path,
    select_threshold_on_validation,
    write_prediction_csv,
)
from entity_matching.experiments.training_guard import assert_fit_allowed
from entity_matching.models import (
    get_model_definition,
    instantiate_model,
    load_model_config,
    load_model_matrix,
)
from entity_matching.splitting import (
    assert_no_leakage,
    build_split_guard_report,
    build_split_manifest,
)


class TrainingExecutionError(ValueError):
    """Raised when an approved training run cannot be executed safely."""


@dataclass(frozen=True)
class SeedRunResult:
    """Serializable result summary for one model and one seed."""

    experiment_id: str
    model_id: str
    seed: int
    selected_threshold: float
    validation_metrics: dict[str, Any]
    test_metrics: dict[str, Any]
    train_label_counts: dict[str, int]
    validation_label_counts: dict[str, int]
    test_label_counts: dict[str, int]
    validation_prediction_path: str
    test_prediction_path: str
    fit_seconds: float
    validation_score_seconds: float
    test_score_seconds: float


def load_training_config(path: str | Path) -> dict[str, Any]:
    """Load and validate an approved fit-enabled training config."""

    with Path(path).open("r", encoding="utf-8") as file:
        config = json.load(file)
    validate_training_config(config)
    return config


def validate_training_config(config: Mapping[str, Any]) -> None:
    """Validate explicit approval and protocol fields for training."""

    required = {
        "experiment_id",
        "status",
        "approval",
        "dataset_config",
        "model_config",
        "processed_root",
        "results_root",
        "splits",
        "development_to_test_guards",
        "train_validation_guards",
        "threshold_selection",
        "final_test_policy",
        "random_seeds",
        "models_to_run",
        "fit_allowed",
    }
    missing = required - set(config)
    if missing:
        raise TrainingExecutionError(
            f"Training config missing keys: {sorted(missing)}"
        )
    if config["status"] != "fit_enabled_approved":
        raise TrainingExecutionError("Training requires status fit_enabled_approved")
    if config["approval"].get("approved_by_user") is not True:
        raise TrainingExecutionError("Training requires explicit user approval")
    assert_fit_allowed(config)

    splits = config["splits"]
    for role in ("train", "validation", "test"):
        if not splits.get(role):
            raise TrainingExecutionError(f"Missing split role: {role}")
    if len({splits["train"], splits["validation"], splits["test"]}) != 3:
        raise TrainingExecutionError("Train, validation, and test splits must differ")

    threshold_selection = config["threshold_selection"]
    if threshold_selection.get("split_role") != "validation":
        raise TrainingExecutionError("Threshold selection must use validation split")
    if threshold_selection.get("selection_metric") != "f1":
        raise TrainingExecutionError("Only F1 threshold selection is supported now")
    _candidate_thresholds(threshold_selection["candidate_thresholds"])

    final_test_policy = config["final_test_policy"]
    if final_test_policy.get("use_test_for_threshold_selection") is not False:
        raise TrainingExecutionError("Test split must not select thresholds")
    if final_test_policy.get("use_test_for_model_selection") is not False:
        raise TrainingExecutionError("Test split must not select models")

    if not config["models_to_run"]:
        raise TrainingExecutionError("At least one model_id is required")
    if not config["random_seeds"]:
        raise TrainingExecutionError("At least one seed is required")
    if len(set(config["random_seeds"])) != len(config["random_seeds"]):
        raise TrainingExecutionError("Seeds must be unique")


def run_approved_baseline_training(config_path: str | Path) -> dict[str, Any]:
    """Run approved baseline training, prediction, thresholding, and summaries."""

    config = load_training_config(config_path)
    _validate_training_guards(config)
    model_config = load_model_config(config["model_config"])
    matrices = _load_protocol_matrices(config)

    all_seed_results = []
    for model_id in config["models_to_run"]:
        definition = get_model_definition(model_config, model_id)
        for seed in config["random_seeds"]:
            result = _run_one_seed(config, definition, model_id, seed, matrices)
            all_seed_results.append(result)

    aggregate = _aggregate_results(config, all_seed_results)
    _write_json(
        Path(config["results_root"])
        / "summaries"
        / config["experiment_id"]
        / "aggregate.json",
        aggregate,
    )
    return aggregate


def _run_one_seed(
    config: Mapping[str, Any],
    model_definition: Mapping[str, Any],
    model_id: str,
    seed: int,
    matrices: Mapping[str, Any],
) -> SeedRunResult:
    estimator = instantiate_model(model_definition, random_seed=seed)

    fit_start = time.perf_counter()
    estimator.fit(matrices["train"].X, matrices["train"].y)
    fit_seconds = time.perf_counter() - fit_start

    validation_start = time.perf_counter()
    validation_scores = _positive_class_scores(estimator, matrices["validation"].X)
    validation_score_seconds = time.perf_counter() - validation_start

    thresholds = _candidate_thresholds(config["threshold_selection"]["candidate_thresholds"])
    threshold_selection = select_threshold_on_validation(
        matrices["validation"].y,
        validation_scores,
        thresholds,
        selection_metric=config["threshold_selection"]["selection_metric"],
        split_name="validation",
    )
    selected_threshold = float(threshold_selection["selected_threshold"])
    validation_metrics = threshold_selection["selected_metrics"]

    test_start = time.perf_counter()
    test_scores = _positive_class_scores(estimator, matrices["test"].X)
    test_score_seconds = time.perf_counter() - test_start
    test_metrics = evaluate_binary_scores(
        matrices["test"].y, test_scores, selected_threshold
    )

    validation_prediction_path = prediction_artifact_path(
        config["results_root"],
        config["experiment_id"],
        model_id,
        seed,
        "validation",
    )
    test_prediction_path = prediction_artifact_path(
        config["results_root"],
        config["experiment_id"],
        model_id,
        seed,
        "test",
    )
    write_prediction_csv(
        _prediction_rows(
            config["experiment_id"],
            model_id,
            seed,
            "validation",
            matrices["validation"],
            validation_scores,
            selected_threshold,
        ),
        validation_prediction_path,
    )
    write_prediction_csv(
        _prediction_rows(
            config["experiment_id"],
            model_id,
            seed,
            "test",
            matrices["test"],
            test_scores,
            selected_threshold,
        ),
        test_prediction_path,
    )

    result = SeedRunResult(
        experiment_id=config["experiment_id"],
        model_id=model_id,
        seed=seed,
        selected_threshold=selected_threshold,
        validation_metrics=validation_metrics,
        test_metrics=test_metrics,
        train_label_counts=matrices["train"].label_counts,
        validation_label_counts=matrices["validation"].label_counts,
        test_label_counts=matrices["test"].label_counts,
        validation_prediction_path=str(validation_prediction_path),
        test_prediction_path=str(test_prediction_path),
        fit_seconds=fit_seconds,
        validation_score_seconds=validation_score_seconds,
        test_score_seconds=test_score_seconds,
    )
    _write_json(
        Path(config["results_root"])
        / "summaries"
        / config["experiment_id"]
        / model_id
        / f"seed_{seed}.json",
        asdict(result),
    )
    return result


def _validate_training_guards(config: Mapping[str, Any]) -> None:
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

    for development_role in ("train", "validation"):
        report = build_split_guard_report(
            dataset_config,
            processed_root=processed_root,
            split_names=[splits[development_role], splits["test"]],
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


def _load_protocol_matrices(config: Mapping[str, Any]) -> dict[str, Any]:
    split_names = [
        config["splits"]["train"],
        config["splits"]["validation"],
        config["splits"]["test"],
    ]
    manifest = build_split_manifest(
        config["dataset_config"],
        processed_root=config["processed_root"],
        split_names=split_names,
    )
    return {
        role: load_model_matrix(manifest, split_name)
        for role, split_name in config["splits"].items()
    }


def _positive_class_scores(estimator: Any, X: list[list[float]]) -> list[float]:
    if not hasattr(estimator, "predict_proba"):
        raise TrainingExecutionError(
            f"Estimator does not provide predict_proba: {estimator.__class__.__name__}"
        )
    probabilities = estimator.predict_proba(X)
    classes = list(estimator.classes_)
    if 1 not in classes:
        raise TrainingExecutionError("Estimator classes do not contain positive class 1")
    positive_index = classes.index(1)
    return [float(row[positive_index]) for row in probabilities]


def _candidate_thresholds(grid: Mapping[str, Any]) -> list[float]:
    start = float(grid["start"])
    end = float(grid["end"])
    step = float(grid["step"])
    if start < 0.0 or end > 1.0 or start >= end or step <= 0.0:
        raise TrainingExecutionError("Invalid threshold grid")
    thresholds = []
    current = start
    while current <= end + 1e-12:
        thresholds.append(round(current, 10))
        current += step
    return thresholds


def _prediction_rows(
    experiment_id: str,
    model_id: str,
    seed: int,
    split_role: str,
    matrix: Any,
    scores: Iterable[float],
    threshold: float,
) -> list[dict[str, Any]]:
    score_list = list(scores)
    predictions = apply_threshold(score_list, threshold)
    return [
        {
            "schema_version": RAW_PREDICTION_SCHEMA_VERSION,
            "experiment_id": experiment_id,
            "model_id": model_id,
            "seed": seed,
            "split_role": split_role,
            "split": matrix.split,
            "pair_id": pair_id,
            "y_true": y_true,
            "score": score,
            "threshold": threshold,
            "y_pred": y_pred,
        }
        for pair_id, y_true, score, y_pred in zip(
            matrix.pair_ids, matrix.y, score_list, predictions
        )
    ]


def _aggregate_results(
    config: Mapping[str, Any], seed_results: list[SeedRunResult]
) -> dict[str, Any]:
    by_model: dict[str, list[SeedRunResult]] = {}
    for result in seed_results:
        by_model.setdefault(result.model_id, []).append(result)

    return {
        "experiment_id": config["experiment_id"],
        "status": "completed",
        "source_config": config.get("source_protocol_config"),
        "models": {
            model_id: _aggregate_model_results(results)
            for model_id, results in sorted(by_model.items())
        },
        "seed_results": [asdict(result) for result in seed_results],
    }


def _aggregate_model_results(results: list[SeedRunResult]) -> dict[str, Any]:
    test_f1_values = [float(result.test_metrics["f1"]) for result in results]
    test_precision_values = [float(result.test_metrics["precision"]) for result in results]
    test_recall_values = [float(result.test_metrics["recall"]) for result in results]
    return {
        "seeds": [result.seed for result in results],
        "test_f1_mean": statistics.mean(test_f1_values),
        "test_f1_std": _sample_std(test_f1_values),
        "test_precision_mean": statistics.mean(test_precision_values),
        "test_precision_std": _sample_std(test_precision_values),
        "test_recall_mean": statistics.mean(test_recall_values),
        "test_recall_std": _sample_std(test_recall_values),
        "selected_thresholds": [result.selected_threshold for result in results],
    }


def _sample_std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return statistics.stdev(values)


def _write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, sort_keys=True)
