"""Plan full train-ratio by test-ratio grids without fitting models."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import statistics
import time
from typing import Any, Mapping

from entity_matching.evaluation import (
    evaluate_binary_scores,
    select_threshold_on_validation,
    write_prediction_csv,
)
from entity_matching.experiments.class_ratio_plan import (
    ClassRatioPlanError,
    build_sampled_training_matrix,
)
from entity_matching.experiments.protocol import (
    ExperimentProtocolError,
    validate_protocol_config,
    validate_protocol_guards,
)
from entity_matching.experiments.training_guard import (
    TrainingNotAllowedError,
    assert_fit_allowed,
)
from entity_matching.experiments.training import (
    _candidate_thresholds,
    _load_protocol_matrices,
    _positive_class_scores,
    _prediction_rows,
    _sample_std,
    _validate_training_guards,
    _write_json,
)
from entity_matching.models import (
    describe_estimator,
    get_model_definition,
    instantiate_model,
    load_model_config,
    load_model_matrix,
)
from entity_matching.splitting import build_split_manifest


TRAIN_TEST_RATIO_GRID_MANIFEST_COLUMNS = [
    "task_id",
    "experiment_id",
    "train_ratio_id",
    "train_ratio",
    "test_ratio_id",
    "test_ratio",
    "model_id",
    "seed",
    "train_positive_count",
    "train_negative_count",
    "train_total_count",
    "test_positive_count",
    "test_negative_count",
    "test_total_count",
    "validation_split",
    "validation_row_count",
    "validation_prediction_path",
    "test_prediction_path",
    "fit_allowed",
    "writes_files_now",
]


class TrainTestRatioGridError(ValueError):
    """Raised when the train/test ratio grid protocol is invalid."""


@dataclass(frozen=True)
class TrainTestRatioGridSeedEvaluationResult:
    """Serializable result for one train ratio, test ratio, model, and seed."""

    experiment_id: str
    train_ratio_id: str
    train_ratio: str
    test_ratio_id: str
    test_ratio: str
    model_id: str
    seed: int
    selected_threshold: float
    validation_metrics: dict[str, Any]
    test_metrics: dict[str, Any]
    train_label_counts: dict[str, int]
    validation_label_counts: dict[str, int]
    test_label_counts: dict[str, int]
    sampled_train_split: str
    sampled_test_split: str
    sampled_train_pair_count: int
    sampled_test_pair_count: int
    validation_prediction_path: str
    test_prediction_path: str
    fit_seconds: float
    validation_score_seconds: float
    test_score_seconds: float


def load_train_test_ratio_grid_config(path: str | Path) -> dict[str, Any]:
    """Load and validate a protocol-only train/test ratio grid config."""

    with Path(path).open("r", encoding="utf-8") as file:
        config = json.load(file)
    validate_train_test_ratio_grid_config(config)
    return config


def validate_train_test_ratio_grid_config(config: Mapping[str, Any]) -> None:
    """Validate train/test ratio grid fields without allowing fitting."""

    if "train_test_ratio_grid" not in config:
        raise TrainTestRatioGridError("Missing train_test_ratio_grid section")
    try:
        validate_protocol_config(
            {
                **dict(config),
                "fit_blockers": config.get("fit_blockers", []),
            }
        )
    except ExperimentProtocolError as error:
        raise TrainTestRatioGridError(str(error)) from error

    grid = config["train_test_ratio_grid"]
    required = {
        "positive_label",
        "negative_label",
        "train_positive_policy",
        "test_positive_policy",
        "train_negative_per_positive_values",
        "test_negative_per_positive_values",
        "train_negative_sampling",
        "test_negative_sampling",
    }
    missing = required - set(grid)
    if missing:
        raise TrainTestRatioGridError(
            f"train_test_ratio_grid missing keys: {sorted(missing)}"
        )
    if grid["positive_label"] != 1 or grid["negative_label"] != 0:
        raise TrainTestRatioGridError("Only labels 1=match and 0=non-match are supported")
    if grid["train_positive_policy"] != "use_all_available_positives":
        raise TrainTestRatioGridError("Only all training positives are supported")
    if grid["test_positive_policy"] != "use_all_available_positives":
        raise TrainTestRatioGridError("Only all test positives are supported")

    _validate_ratio_values(grid["train_negative_per_positive_values"], "train")
    _validate_ratio_values(grid["test_negative_per_positive_values"], "test")
    _validate_sampling(grid["train_negative_sampling"], "train")
    _validate_sampling(grid["test_negative_sampling"], "test")


def load_train_test_ratio_grid_training_config(path: str | Path) -> dict[str, Any]:
    """Load and validate an approved fit-enabled train/test ratio grid config."""

    with Path(path).open("r", encoding="utf-8") as file:
        config = json.load(file)
    validate_train_test_ratio_grid_training_config(config)
    return config


def validate_train_test_ratio_grid_training_config(config: Mapping[str, Any]) -> None:
    """Validate explicit approval and grid training protocol fields."""

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
        "train_test_ratio_grid",
        "random_seeds",
        "models_to_run",
        "fit_allowed",
    }
    missing = required - set(config)
    if missing:
        raise TrainTestRatioGridError(
            f"Train/test ratio grid training config missing keys: {sorted(missing)}"
        )
    if config["status"] != "fit_enabled_approved":
        raise TrainTestRatioGridError(
            "Train/test ratio grid training requires status fit_enabled_approved"
        )
    if config["approval"].get("approved_by_user") is not True:
        raise TrainTestRatioGridError(
            "Train/test ratio grid training requires explicit user approval"
        )
    assert_fit_allowed(config)
    _validate_grid_common_fields(config)
    if not config["models_to_run"]:
        raise TrainTestRatioGridError("At least one model_id is required")


def build_train_test_ratio_grid_plan(
    config_path: str | Path,
    *,
    model_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Build a full train/test ratio grid plan without fitting models."""

    config = load_train_test_ratio_grid_config(config_path)
    guard_summary = validate_protocol_guards(config_path)
    manifest = build_split_manifest(
        config["dataset_config"],
        processed_root=config["processed_root"],
        split_names=[
            config["splits"]["train"],
            config["splits"]["validation"],
            config["splits"]["test"],
        ],
    )
    train_matrix = load_model_matrix(manifest, config["splits"]["train"])
    validation_matrix = load_model_matrix(manifest, config["splits"]["validation"])
    test_matrix = load_model_matrix(manifest, config["splits"]["test"])

    selected_models = model_ids or list(config["planned_models"])
    model_config = load_model_config(config["model_config"])
    model_plans = [
        _build_model_plan(model_config, model_id, config["random_seeds"])
        for model_id in selected_models
    ]
    train_ratio_plans = _build_ratio_plans(
        train_matrix,
        config["train_test_ratio_grid"]["train_negative_per_positive_values"],
        config["random_seeds"],
    )
    test_ratio_plans = _build_ratio_plans(
        test_matrix,
        config["train_test_ratio_grid"]["test_negative_per_positive_values"],
        config["random_seeds"],
    )
    return {
        "experiment_id": config["experiment_id"],
        "status": config["status"],
        "fit_allowed": config["fit_allowed"],
        "ready_to_execute_training": False,
        "remaining_fit_blockers": config.get("fit_blockers", []),
        "splits": config["splits"],
        "train_test_ratio_grid": config["train_test_ratio_grid"],
        "random_seeds": config["random_seeds"],
        "models": model_plans,
        "train_ratio_plans": train_ratio_plans,
        "test_ratio_plans": test_ratio_plans,
        "planned_fit_count": len(train_ratio_plans)
        * len(model_plans)
        * len(config["random_seeds"]),
        "planned_test_evaluation_count": len(train_ratio_plans)
        * len(test_ratio_plans)
        * len(model_plans)
        * len(config["random_seeds"]),
        "fixed_evaluation_summary": {
            "validation": validation_matrix.to_summary(),
            "test_source": test_matrix.to_summary(),
        },
        "artifact_plan": _build_artifact_plan(
            config, selected_models, train_ratio_plans, test_ratio_plans
        ),
        "protocol_guard_summary": {
            "train_validation_overlap": guard_summary["train_validation_guard_report"][
                "record_entity_overlaps"
            ]["train_small__valid_small"],
            "train_test_overlap": guard_summary["development_to_test_guard_reports"][
                "train_to_test"
            ]["record_entity_overlaps"]["test_unseen_100un__train_small"],
            "validation_test_overlap": guard_summary[
                "development_to_test_guard_reports"
            ]["validation_to_test"]["record_entity_overlaps"][
                "test_unseen_100un__valid_small"
            ],
        },
    }


def run_approved_train_test_ratio_grid_training(config_path: str | Path) -> dict[str, Any]:
    """Run an approved full train/test ratio grid with optimized model fitting."""

    resolved_config_path = Path(config_path)
    with resolved_config_path.open("r", encoding="utf-8") as file:
        raw_config = json.load(file)
    assert_fit_allowed(raw_config)
    config = load_train_test_ratio_grid_training_config(resolved_config_path)
    config["executed_config_path"] = str(resolved_config_path)
    _validate_training_guards(config)
    matrices = _load_protocol_matrices(config)
    model_config = load_model_config(config["model_config"])

    all_results: list[TrainTestRatioGridSeedEvaluationResult] = []
    train_values = config["train_test_ratio_grid"][
        "train_negative_per_positive_values"
    ]
    test_values = config["train_test_ratio_grid"]["test_negative_per_positive_values"]
    for train_ratio_value in train_values:
        train_ratio_id = _ratio_id(train_ratio_value)
        train_ratio_label = _ratio_label(train_ratio_value)
        for model_id in config["models_to_run"]:
            definition = get_model_definition(model_config, model_id)
            for seed in config["random_seeds"]:
                sampled_train = build_sampled_training_matrix(
                    matrices["train"],
                    negatives_per_positive=train_ratio_value,
                    seed=seed,
                )
                fit_context = _fit_grid_model_once(
                    config,
                    definition,
                    model_id,
                    seed,
                    train_ratio_id,
                    train_ratio_label,
                    sampled_train,
                    matrices["validation"],
                )
                for test_ratio_value in test_values:
                    all_results.append(
                        _evaluate_grid_test_ratio(
                            config,
                            fit_context,
                            train_ratio_id,
                            train_ratio_label,
                            test_ratio_value,
                            matrices["test"],
                        )
                    )

    aggregate = _aggregate_grid_results(config, all_results)
    _write_json(
        Path(config["results_root"])
        / "summaries"
        / config["experiment_id"]
        / "aggregate.json",
        aggregate,
    )
    return aggregate


def train_test_ratio_grid_manifest_rows(
    plan: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Expand a train/test ratio grid plan into dry evaluation rows."""

    validation = plan["fixed_evaluation_summary"]["validation"]
    paths = plan["artifact_plan"]["raw_prediction_paths"]
    rows = []
    task_index = 1
    for train_ratio in plan["train_ratio_plans"]:
        train_ratio_id = train_ratio["ratio_id"]
        for test_ratio in plan["test_ratio_plans"]:
            test_ratio_id = test_ratio["ratio_id"]
            for model in plan["models"]:
                model_id = model["model_id"]
                for seed_plan in train_ratio["seed_plans"]:
                    seed = seed_plan["seed"]
                    path_info = paths[train_ratio_id][test_ratio_id][model_id][str(seed)]
                    test_seed_plan = _seed_plan_for(test_ratio, seed)
                    rows.append(
                        {
                            "task_id": f"task_{task_index:03d}",
                            "experiment_id": plan["experiment_id"],
                            "train_ratio_id": train_ratio_id,
                            "train_ratio": train_ratio["match_to_non_match_ratio"],
                            "test_ratio_id": test_ratio_id,
                            "test_ratio": test_ratio["match_to_non_match_ratio"],
                            "model_id": model_id,
                            "seed": seed,
                            "train_positive_count": seed_plan["positive_count"],
                            "train_negative_count": seed_plan["negative_count"],
                            "train_total_count": seed_plan["total_count"],
                            "test_positive_count": test_seed_plan["positive_count"],
                            "test_negative_count": test_seed_plan["negative_count"],
                            "test_total_count": test_seed_plan["total_count"],
                            "validation_split": validation["split"],
                            "validation_row_count": validation["row_count"],
                            "validation_prediction_path": path_info["validation"],
                            "test_prediction_path": path_info["test"],
                            "fit_allowed": plan["fit_allowed"],
                            "writes_files_now": plan["artifact_plan"][
                                "writes_files_now"
                            ],
                        }
                    )
                    task_index += 1
    return rows


def check_train_test_ratio_grid_training_readiness(
    config_path: str | Path,
    *,
    model_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Return a blocked/ready grid summary without fitting or writing results."""

    config = load_train_test_ratio_grid_config(config_path)
    plan = build_train_test_ratio_grid_plan(config_path, model_ids=model_ids)
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
            "train_ratios": [
                ratio["match_to_non_match_ratio"]
                for ratio in plan["train_ratio_plans"]
            ],
            "test_ratios": [
                ratio["match_to_non_match_ratio"] for ratio in plan["test_ratio_plans"]
            ],
            "models": [model["model_id"] for model in plan["models"]],
            "planned_fit_count": plan["planned_fit_count"],
            "planned_test_evaluation_count": plan["planned_test_evaluation_count"],
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
        "train_ratios": [
            ratio["match_to_non_match_ratio"] for ratio in plan["train_ratio_plans"]
        ],
        "test_ratios": [
            ratio["match_to_non_match_ratio"] for ratio in plan["test_ratio_plans"]
        ],
        "models": [model["model_id"] for model in plan["models"]],
        "planned_fit_count": plan["planned_fit_count"],
        "planned_test_evaluation_count": plan["planned_test_evaluation_count"],
    }


def write_train_test_ratio_grid_manifest_csv(
    rows: list[Mapping[str, Any]], output_path: str | Path
) -> int:
    """Write train/test ratio grid manifest rows to CSV."""

    if not rows:
        raise TrainTestRatioGridError("At least one grid manifest row is required")
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=TRAIN_TEST_RATIO_GRID_MANIFEST_COLUMNS
        )
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def write_train_test_ratio_grid_manifest_markdown(
    rows: list[Mapping[str, Any]], output_path: str | Path
) -> int:
    """Write a compact train/test ratio grid manifest summary."""

    if not rows:
        raise TrainTestRatioGridError("At least one grid manifest row is required")
    train_ratios = sorted({row["train_ratio"] for row in rows}, key=_ratio_sort_key)
    test_ratios = sorted({row["test_ratio"] for row in rows}, key=_ratio_sort_key)
    models = sorted({row["model_id"] for row in rows})
    seeds = sorted({row["seed"] for row in rows})
    lines = [
        "# Train/Test Ratio Grid Manifest",
        "",
        "Protocol: WDC Products `train_small` / `valid_small` / `test_unseen_100un`.",
        "",
        f"Planned test-evaluation rows: `{len(rows)}`.",
        f"Planned fit tasks if optimized by train ratio/model/seed: `{len(train_ratios) * len(models) * len(seeds)}`.",
        f"Train ratios: `{', '.join(train_ratios)}`.",
        f"Test ratios: `{', '.join(test_ratios)}`.",
        f"Models: `{', '.join(models)}`.",
        f"Seeds: `{', '.join(str(seed) for seed in seeds)}`.",
        f"Fit allowed now: `{rows[0]['fit_allowed']}`.",
        f"Writes files now: `{rows[0]['writes_files_now']}`.",
        "",
        "| Train Ratio | Test Ratio | Model | Seeds | Train Rows | Test Rows |",
        "|---|---|---|---:|---:|---:|",
    ]
    grouped: dict[tuple[str, str, str], list[Mapping[str, Any]]] = {}
    for row in rows:
        key = (row["train_ratio"], row["test_ratio"], row["model_id"])
        grouped.setdefault(key, []).append(row)
    for (train_ratio, test_ratio, model_id), group_rows in sorted(
        grouped.items(), key=lambda item: (_ratio_sort_key(item[0][0]), _ratio_sort_key(item[0][1]), item[0][2])
    ):
        first = group_rows[0]
        lines.append(
            "| `{train}` | `{test}` | `{model}` | `{seeds}` | `{train_rows}` | `{test_rows}` |".format(
                train=train_ratio,
                test=test_ratio,
                model=model_id,
                seeds=len(group_rows),
                train_rows=first["train_total_count"],
                test_rows=first["test_total_count"],
            )
        )
    lines.extend(
        [
            "",
            "Notes:",
            "",
            "- This is a dry execution manifest, not a training result.",
            "- Validation remains fixed for threshold selection.",
            "- Test negatives are planned as seeded samples from `test_unseen_100un`.",
            "- No sampled train/test tables are written in this protocol-only step.",
        ]
    )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(rows)


def _fit_grid_model_once(
    config: Mapping[str, Any],
    model_definition: Mapping[str, Any],
    model_id: str,
    seed: int,
    train_ratio_id: str,
    train_ratio_label: str,
    sampled_train: Any,
    validation_matrix: Any,
) -> dict[str, Any]:
    estimator = instantiate_model(model_definition, random_seed=seed)

    fit_start = time.perf_counter()
    estimator.fit(sampled_train.X, sampled_train.y)
    fit_seconds = time.perf_counter() - fit_start

    validation_start = time.perf_counter()
    validation_scores = _positive_class_scores(estimator, validation_matrix.X)
    validation_score_seconds = time.perf_counter() - validation_start

    thresholds = _candidate_thresholds(
        config["threshold_selection"]["candidate_thresholds"]
    )
    threshold_selection = select_threshold_on_validation(
        validation_matrix.y,
        validation_scores,
        thresholds,
        selection_metric=config["threshold_selection"]["selection_metric"],
        split_name="validation",
    )
    return {
        "estimator": estimator,
        "model_id": model_id,
        "seed": seed,
        "train_ratio_id": train_ratio_id,
        "train_ratio": train_ratio_label,
        "sampled_train": sampled_train,
        "validation_matrix": validation_matrix,
        "validation_scores": validation_scores,
        "selected_threshold": float(threshold_selection["selected_threshold"]),
        "validation_metrics": threshold_selection["selected_metrics"],
        "fit_seconds": fit_seconds,
        "validation_score_seconds": validation_score_seconds,
    }


def _evaluate_grid_test_ratio(
    config: Mapping[str, Any],
    fit_context: Mapping[str, Any],
    train_ratio_id: str,
    train_ratio_label: str,
    test_ratio_value: int,
    full_test_matrix: Any,
) -> TrainTestRatioGridSeedEvaluationResult:
    test_ratio_id = _ratio_id(test_ratio_value)
    test_ratio_label = _ratio_label(test_ratio_value)
    model_id = fit_context["model_id"]
    seed = fit_context["seed"]
    selected_threshold = fit_context["selected_threshold"]
    sampled_test = build_sampled_training_matrix(
        full_test_matrix,
        negatives_per_positive=test_ratio_value,
        seed=seed,
    )

    test_start = time.perf_counter()
    test_scores = _positive_class_scores(fit_context["estimator"], sampled_test.X)
    test_score_seconds = time.perf_counter() - test_start
    test_metrics = evaluate_binary_scores(
        sampled_test.y,
        test_scores,
        selected_threshold,
    )

    validation_prediction_path = _grid_prediction_path(
        config,
        train_ratio_id,
        test_ratio_id,
        model_id,
        seed,
        "validation",
    )
    test_prediction_path = _grid_prediction_path(
        config,
        train_ratio_id,
        test_ratio_id,
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
            fit_context["validation_matrix"],
            fit_context["validation_scores"],
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
            sampled_test,
            test_scores,
            selected_threshold,
        ),
        test_prediction_path,
    )

    result = TrainTestRatioGridSeedEvaluationResult(
        experiment_id=config["experiment_id"],
        train_ratio_id=train_ratio_id,
        train_ratio=train_ratio_label,
        test_ratio_id=test_ratio_id,
        test_ratio=test_ratio_label,
        model_id=model_id,
        seed=seed,
        selected_threshold=selected_threshold,
        validation_metrics=fit_context["validation_metrics"],
        test_metrics=test_metrics,
        train_label_counts=fit_context["sampled_train"].label_counts,
        validation_label_counts=fit_context["validation_matrix"].label_counts,
        test_label_counts=sampled_test.label_counts,
        sampled_train_split=fit_context["sampled_train"].split,
        sampled_test_split=sampled_test.split,
        sampled_train_pair_count=fit_context["sampled_train"].row_count,
        sampled_test_pair_count=sampled_test.row_count,
        validation_prediction_path=str(validation_prediction_path),
        test_prediction_path=str(test_prediction_path),
        fit_seconds=fit_context["fit_seconds"],
        validation_score_seconds=fit_context["validation_score_seconds"],
        test_score_seconds=test_score_seconds,
    )
    _write_json(
        Path(config["results_root"])
        / "summaries"
        / config["experiment_id"]
        / train_ratio_id
        / test_ratio_id
        / model_id
        / f"seed_{seed}.json",
        asdict(result),
    )
    return result


def _aggregate_grid_results(
    config: Mapping[str, Any],
    seed_results: list[TrainTestRatioGridSeedEvaluationResult],
) -> dict[str, Any]:
    by_cell: dict[
        tuple[str, str, str], list[TrainTestRatioGridSeedEvaluationResult]
    ] = {}
    for result in seed_results:
        key = (result.train_ratio_id, result.test_ratio_id, result.model_id)
        by_cell.setdefault(key, []).append(result)

    grid: dict[str, Any] = {}
    for (train_ratio_id, test_ratio_id, model_id), results in sorted(by_cell.items()):
        grid.setdefault(train_ratio_id, {}).setdefault(test_ratio_id, {})[
            model_id
        ] = _aggregate_grid_cell_results(results)

    train_values = config["train_test_ratio_grid"][
        "train_negative_per_positive_values"
    ]
    test_values = config["train_test_ratio_grid"]["test_negative_per_positive_values"]
    return {
        "experiment_id": config["experiment_id"],
        "status": "completed",
        "source_config": config.get("executed_config_path"),
        "source_protocol_config": config.get("source_protocol_config"),
        "train_negative_per_positive_values": train_values,
        "test_negative_per_positive_values": test_values,
        "planned_fit_count": len(train_values)
        * len(config["models_to_run"])
        * len(config["random_seeds"]),
        "planned_test_evaluation_count": len(seed_results),
        "grid": grid,
        "seed_results": [asdict(result) for result in seed_results],
    }


def _aggregate_grid_cell_results(
    results: list[TrainTestRatioGridSeedEvaluationResult],
) -> dict[str, Any]:
    test_f1_values = [float(result.test_metrics["f1"]) for result in results]
    test_precision_values = [float(result.test_metrics["precision"]) for result in results]
    test_recall_values = [float(result.test_metrics["recall"]) for result in results]
    return {
        "train_ratio": results[0].train_ratio,
        "test_ratio": results[0].test_ratio,
        "train_label_counts": results[0].train_label_counts,
        "test_label_counts": results[0].test_label_counts,
        "seeds": [result.seed for result in results],
        "selected_thresholds": [result.selected_threshold for result in results],
        "test_f1_mean": statistics.mean(test_f1_values),
        "test_f1_std": _sample_std(test_f1_values),
        "test_precision_mean": statistics.mean(test_precision_values),
        "test_precision_std": _sample_std(test_precision_values),
        "test_recall_mean": statistics.mean(test_recall_values),
        "test_recall_std": _sample_std(test_recall_values),
    }


def _grid_prediction_path(
    config: Mapping[str, Any],
    train_ratio_id: str,
    test_ratio_id: str,
    model_id: str,
    seed: int,
    split_role: str,
) -> Path:
    return (
        Path(config["results_root"])
        / "predictions"
        / config["experiment_id"]
        / train_ratio_id
        / test_ratio_id
        / model_id
        / f"seed_{seed}"
        / f"{split_role}.csv"
    )


def _validate_grid_common_fields(config: Mapping[str, Any]) -> None:
    protocol_like = {
        **dict(config),
        "status": "protocol_locked_no_fit",
        "fit_allowed": False,
        "fit_blockers": ["training validation mirror"],
        "planned_models": list(config.get("models_to_run", [])),
    }
    validate_train_test_ratio_grid_config(protocol_like)


def _ratio_id(value: int) -> str:
    return f"match_1_nonmatch_{value}"


def _ratio_label(value: int) -> str:
    return f"1:{value}"


def _build_ratio_plans(
    matrix: Any,
    negative_per_positive_values: list[int],
    random_seeds: list[int],
) -> list[dict[str, Any]]:
    positive_count = matrix.y.count(1)
    plans = []
    for negatives_per_positive in negative_per_positive_values:
        seed_plans = []
        for seed in random_seeds:
            sampled_matrix = build_sampled_training_matrix(
                matrix,
                negatives_per_positive=negatives_per_positive,
                seed=seed,
            )
            seed_plans.append(
                {
                    "seed": seed,
                    "positive_count": sampled_matrix.label_counts["1"],
                    "negative_count": sampled_matrix.label_counts["0"],
                    "total_count": sampled_matrix.row_count,
                    "sampled_split": sampled_matrix.split,
                    "sampled_feature_count": sampled_matrix.feature_count,
                }
            )
        plans.append(
            {
                "ratio_id": f"match_1_nonmatch_{negatives_per_positive}",
                "match_to_non_match_ratio": f"1:{negatives_per_positive}",
                "positive_count": positive_count,
                "negative_count": positive_count * negatives_per_positive,
                "total_count": positive_count * (1 + negatives_per_positive),
                "seed_plans": seed_plans,
            }
        )
    return plans


def _build_model_plan(
    model_config: dict[str, Any], model_id: str, random_seeds: list[int]
) -> dict[str, Any]:
    definition = get_model_definition(model_config, model_id)
    estimators = []
    for seed in random_seeds:
        estimators.append(
            {
                "seed": seed,
                "estimator": describe_estimator(
                    instantiate_model(definition, random_seed=seed)
                ),
            }
        )
    return {
        "model_id": model_id,
        "family": definition["family"],
        "status": definition["status"],
        "estimators": estimators,
    }


def _build_artifact_plan(
    config: Mapping[str, Any],
    model_ids: list[str],
    train_ratio_plans: list[Mapping[str, Any]],
    test_ratio_plans: list[Mapping[str, Any]],
) -> dict[str, Any]:
    raw_prediction_paths: dict[str, Any] = {}
    for train_ratio in train_ratio_plans:
        train_ratio_id = train_ratio["ratio_id"]
        raw_prediction_paths[train_ratio_id] = {}
        for test_ratio in test_ratio_plans:
            test_ratio_id = test_ratio["ratio_id"]
            raw_prediction_paths[train_ratio_id][test_ratio_id] = {}
            for model_id in model_ids:
                raw_prediction_paths[train_ratio_id][test_ratio_id][model_id] = {}
                for seed in config["random_seeds"]:
                    base_path = (
                        Path(config["results_root"])
                        / "predictions"
                        / config["experiment_id"]
                        / train_ratio_id
                        / test_ratio_id
                        / model_id
                        / f"seed_{seed}"
                    )
                    raw_prediction_paths[train_ratio_id][test_ratio_id][model_id][
                        str(seed)
                    ] = {
                        "validation": str(base_path / "validation.csv"),
                        "test": str(base_path / "test.csv"),
                    }
    return {
        "raw_prediction_schema_version": "raw_predictions_v1",
        "raw_prediction_paths": raw_prediction_paths,
        "writes_files_now": False,
        "writes_sampled_training_tables_now": False,
        "writes_sampled_test_tables_now": False,
    }


def _seed_plan_for(ratio: Mapping[str, Any], seed: int) -> Mapping[str, Any]:
    for seed_plan in ratio["seed_plans"]:
        if seed_plan["seed"] == seed:
            return seed_plan
    raise TrainTestRatioGridError(f"Missing seed plan for seed {seed}")


def _validate_ratio_values(values: Any, role: str) -> None:
    if not values or len(set(values)) != len(values):
        raise TrainTestRatioGridError(f"{role} ratio values must be non-empty and unique")
    if not all(isinstance(value, int) and value > 0 for value in values):
        raise TrainTestRatioGridError(f"{role} ratio values must be positive integers")


def _validate_sampling(sampling: Mapping[str, Any], role: str) -> None:
    if sampling.get("without_replacement") is not True:
        raise TrainTestRatioGridError(f"{role} sampling must be without replacement")
    if sampling.get("seeded_by") != "experiment_seed":
        raise TrainTestRatioGridError(f"{role} sampling must be seeded by experiment_seed")
    if sampling.get("write_sampled_tables_now") is not False:
        raise TrainTestRatioGridError(f"{role} sampling must not write sampled tables")


def _ratio_sort_key(ratio_label: str) -> int:
    return int(ratio_label.split(":", maxsplit=1)[1])
