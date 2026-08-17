"""Guarded execution for approved class-ratio stress-test runs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import statistics
import time
from typing import Any
from typing import Mapping

from entity_matching.experiments.class_ratio_plan import (
    ClassRatioPlanError,
    build_sampled_training_matrix,
    build_class_ratio_run_plan,
    load_class_ratio_protocol_config,
    validate_class_ratio_protocol_config,
)
from entity_matching.experiments.training import (
    TrainingExecutionError,
    _candidate_thresholds,
    _load_protocol_matrices,
    _positive_class_scores,
    _prediction_rows,
    _sample_std,
    _validate_training_guards,
    _write_json,
)
from entity_matching.experiments.training_guard import (
    TrainingNotAllowedError,
    assert_fit_allowed,
)
from entity_matching.evaluation import (
    evaluate_binary_scores,
    select_threshold_on_validation,
    write_prediction_csv,
)
from entity_matching.models import (
    get_model_definition,
    instantiate_model,
    load_model_config,
)


class ClassRatioTrainingError(ValueError):
    """Raised when class-ratio training cannot be executed safely."""


@dataclass(frozen=True)
class ClassRatioSeedRunResult:
    """Serializable result summary for one ratio, model, and seed."""

    experiment_id: str
    ratio_id: str
    match_to_non_match_ratio: str
    model_id: str
    seed: int
    selected_threshold: float
    validation_metrics: dict[str, Any]
    test_metrics: dict[str, Any]
    train_label_counts: dict[str, int]
    validation_label_counts: dict[str, int]
    test_label_counts: dict[str, int]
    sampled_train_split: str
    sampled_train_pair_count: int
    validation_prediction_path: str
    test_prediction_path: str
    fit_seconds: float
    validation_score_seconds: float
    test_score_seconds: float


def check_class_ratio_training_readiness(
    config_path: str | Path,
    *,
    model_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Return a blocked/ready summary without fitting or writing result files."""

    config = load_class_ratio_protocol_config(config_path)
    plan = build_class_ratio_run_plan(config_path, model_ids=model_ids)
    try:
        assert_fit_allowed(config)
    except TrainingNotAllowedError as error:
        return {
            "experiment_id": config["experiment_id"],
            "status": config["status"],
            "fit_allowed": config["fit_allowed"],
            "ready_to_execute_training": False,
            "training_attempted": False,
            "writes_files_now": False,
            "guard_enforced": True,
            "blocker_error_type": error.__class__.__name__,
            "remaining_fit_blockers": config.get("fit_blockers", []),
            "ratio_count": len(plan["ratio_plans"]),
            "ratios": [
                ratio["match_to_non_match_ratio"] for ratio in plan["ratio_plans"]
            ],
            "models": [model["model_id"] for model in plan["models"]],
        }

    return {
        "experiment_id": config["experiment_id"],
        "status": config["status"],
        "fit_allowed": config["fit_allowed"],
        "ready_to_execute_training": True,
        "training_attempted": False,
        "writes_files_now": False,
        "guard_enforced": True,
        "remaining_fit_blockers": [],
        "ratio_count": len(plan["ratio_plans"]),
        "ratios": [ratio["match_to_non_match_ratio"] for ratio in plan["ratio_plans"]],
        "models": [model["model_id"] for model in plan["models"]],
    }


def load_class_ratio_training_config(path: str | Path) -> dict[str, Any]:
    """Load and validate an approved fit-enabled class-ratio training config."""

    with Path(path).open("r", encoding="utf-8") as file:
        config = json.load(file)
    validate_class_ratio_training_config(config)
    return config


def validate_class_ratio_training_config(config: Mapping[str, Any]) -> None:
    """Validate explicit approval and class-ratio training protocol fields."""

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
        "class_ratio_stress_test",
        "random_seeds",
        "models_to_run",
        "fit_allowed",
    }
    missing = required - set(config)
    if missing:
        raise ClassRatioTrainingError(
            f"Class-ratio training config missing keys: {sorted(missing)}"
        )
    if config["status"] != "fit_enabled_approved":
        raise ClassRatioTrainingError(
            "Class-ratio training requires status fit_enabled_approved"
        )
    if config["approval"].get("approved_by_user") is not True:
        raise ClassRatioTrainingError(
            "Class-ratio training requires explicit user approval"
        )
    assert_fit_allowed(config)

    _validate_class_ratio_common_fields(config)

    if not config["models_to_run"]:
        raise ClassRatioTrainingError("At least one model_id is required")


def run_approved_class_ratio_training(config_path: str | Path) -> dict[str, Any]:
    """Run a class-ratio experiment only after a config explicitly allows fitting."""

    resolved_config_path = Path(config_path)
    with resolved_config_path.open("r", encoding="utf-8") as file:
        raw_config = json.load(file)
    assert_fit_allowed(raw_config)
    config = load_class_ratio_training_config(resolved_config_path)
    config["executed_config_path"] = str(resolved_config_path)
    _validate_training_guards(config)
    matrices = _load_protocol_matrices(config)
    model_config = load_model_config(config["model_config"])

    all_seed_results = []
    for ratio_value in config["class_ratio_stress_test"][
        "negative_per_positive_values"
    ]:
        ratio_id = f"match_1_nonmatch_{ratio_value}"
        ratio_label = f"1:{ratio_value}"
        for model_id in config["models_to_run"]:
            definition = get_model_definition(model_config, model_id)
            for seed in config["random_seeds"]:
                sampled_train = build_sampled_training_matrix(
                    matrices["train"],
                    negatives_per_positive=ratio_value,
                    seed=seed,
                )
                result = _run_one_class_ratio_seed(
                    config,
                    definition,
                    model_id,
                    seed,
                    ratio_value,
                    ratio_id,
                    ratio_label,
                    sampled_train,
                    matrices,
                )
                all_seed_results.append(result)

    aggregate = _aggregate_class_ratio_results(config, all_seed_results)
    _write_json(
        Path(config["results_root"])
        / "summaries"
        / config["experiment_id"]
        / "aggregate.json",
        aggregate,
    )
    return aggregate


def _run_one_class_ratio_seed(
    config: Mapping[str, Any],
    model_definition: Mapping[str, Any],
    model_id: str,
    seed: int,
    ratio_value: int,
    ratio_id: str,
    ratio_label: str,
    sampled_train: Any,
    matrices: Mapping[str, Any],
) -> ClassRatioSeedRunResult:
    estimator = instantiate_model(model_definition, random_seed=seed)

    fit_start = time.perf_counter()
    estimator.fit(sampled_train.X, sampled_train.y)
    fit_seconds = time.perf_counter() - fit_start

    validation_start = time.perf_counter()
    validation_scores = _positive_class_scores(estimator, matrices["validation"].X)
    validation_score_seconds = time.perf_counter() - validation_start

    thresholds = _candidate_thresholds(
        config["threshold_selection"]["candidate_thresholds"]
    )
    threshold_selection = select_threshold_on_validation(
        matrices["validation"].y,
        validation_scores,
        thresholds,
        selection_metric=config["threshold_selection"]["selection_metric"],
        split_name="validation",
    )
    selected_threshold = float(threshold_selection["selected_threshold"])
    validation_metrics = threshold_selection["selected_metrics"]

    test_matrix = _test_matrix_for_ratio(config, matrices["test"], ratio_value, seed)
    test_start = time.perf_counter()
    test_scores = _positive_class_scores(estimator, test_matrix.X)
    test_score_seconds = time.perf_counter() - test_start
    test_metrics = evaluate_binary_scores(
        test_matrix.y,
        test_scores,
        selected_threshold,
    )

    validation_prediction_path = _class_ratio_prediction_path(
        config,
        ratio_id,
        model_id,
        seed,
        "validation",
    )
    test_prediction_path = _class_ratio_prediction_path(
        config,
        ratio_id,
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
            test_matrix,
            test_scores,
            selected_threshold,
        ),
        test_prediction_path,
    )

    result = ClassRatioSeedRunResult(
        experiment_id=config["experiment_id"],
        ratio_id=ratio_id,
        match_to_non_match_ratio=ratio_label,
        model_id=model_id,
        seed=seed,
        selected_threshold=selected_threshold,
        validation_metrics=validation_metrics,
        test_metrics=test_metrics,
        train_label_counts=sampled_train.label_counts,
        validation_label_counts=matrices["validation"].label_counts,
        test_label_counts=test_matrix.label_counts,
        sampled_train_split=sampled_train.split,
        sampled_train_pair_count=sampled_train.row_count,
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
        / ratio_id
        / model_id
        / f"seed_{seed}.json",
        asdict(result),
    )
    return result


def _validate_class_ratio_common_fields(config: Mapping[str, Any]) -> None:
    protocol_like = {
        **dict(config),
        "status": "protocol_locked_no_fit",
        "fit_allowed": False,
        "fit_blockers": ["training validation mirror"],
        "planned_models": list(config.get("models_to_run", [])),
    }
    try:
        validate_class_ratio_protocol_config(protocol_like)
    except ClassRatioPlanError as error:
        raise ClassRatioTrainingError(str(error)) from error


def _test_matrix_for_ratio(
    config: Mapping[str, Any],
    full_test_matrix: Any,
    ratio_value: int,
    seed: int,
) -> Any:
    stress = config["class_ratio_stress_test"]
    if stress.get("test_negative_per_positive_policy") == "match_training_ratio":
        return build_sampled_training_matrix(
            full_test_matrix,
            negatives_per_positive=ratio_value,
            seed=seed,
        )
    return full_test_matrix


def _class_ratio_prediction_path(
    config: Mapping[str, Any],
    ratio_id: str,
    model_id: str,
    seed: int,
    split_role: str,
) -> Path:
    return (
        Path(config["results_root"])
        / "predictions"
        / config["experiment_id"]
        / ratio_id
        / model_id
        / f"seed_{seed}"
        / f"{split_role}.csv"
    )


def _aggregate_class_ratio_results(
    config: Mapping[str, Any],
    seed_results: list[ClassRatioSeedRunResult],
) -> dict[str, Any]:
    by_ratio_model: dict[tuple[str, str], list[ClassRatioSeedRunResult]] = {}
    for result in seed_results:
        by_ratio_model.setdefault((result.ratio_id, result.model_id), []).append(result)

    ratio_summaries: dict[str, Any] = {}
    for (ratio_id, model_id), results in sorted(by_ratio_model.items()):
        ratio_summaries.setdefault(ratio_id, {})[model_id] = _aggregate_model_results(
            results
        )

    return {
        "experiment_id": config["experiment_id"],
        "status": "completed",
        "source_config": config.get("executed_config_path")
        or config.get("source_protocol_config"),
        "source_protocol_config": config.get("source_protocol_config"),
        "test_negative_per_positive_policy": config["class_ratio_stress_test"].get(
            "test_negative_per_positive_policy", "fixed_test_split"
        ),
        "ratios": ratio_summaries,
        "seed_results": [asdict(result) for result in seed_results],
    }


def _aggregate_model_results(results: list[ClassRatioSeedRunResult]) -> dict[str, Any]:
    test_f1_values = [float(result.test_metrics["f1"]) for result in results]
    test_precision_values = [float(result.test_metrics["precision"]) for result in results]
    test_recall_values = [float(result.test_metrics["recall"]) for result in results]
    return {
        "match_to_non_match_ratio": results[0].match_to_non_match_ratio,
        "train_label_counts": results[0].train_label_counts,
        "seeds": [result.seed for result in results],
        "selected_thresholds": [result.selected_threshold for result in results],
        "test_f1_mean": statistics.mean(test_f1_values),
        "test_f1_std": _sample_std(test_f1_values),
        "test_precision_mean": statistics.mean(test_precision_values),
        "test_precision_std": _sample_std(test_precision_values),
        "test_recall_mean": statistics.mean(test_recall_values),
        "test_recall_std": _sample_std(test_recall_values),
    }
