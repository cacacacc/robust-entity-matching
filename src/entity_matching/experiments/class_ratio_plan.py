"""Plan class-ratio stress tests without fitting models."""

from __future__ import annotations

import hashlib
import csv
import json
import random
from pathlib import Path
from typing import Any, Mapping

from entity_matching.experiments.protocol import (
    ExperimentProtocolError,
    validate_protocol_config,
    validate_protocol_guards,
)
from entity_matching.models import (
    ModelMatrix,
    describe_estimator,
    get_model_definition,
    instantiate_model,
    load_model_config,
    load_model_matrix,
)
from entity_matching.splitting import build_split_manifest


class ClassRatioPlanError(ValueError):
    """Raised when a class-ratio plan is unsafe or infeasible."""


CLASS_RATIO_PLAN_COLUMNS = [
    "ratio_id",
    "match_to_non_match_ratio",
    "positive_count",
    "negative_count",
    "total_count",
    "uses_all_available_positives",
    "uses_all_available_negatives",
    "seed_count",
    "validation_split",
    "validation_row_count",
    "validation_label_counts",
    "test_split",
    "test_row_count",
    "test_label_counts",
]

CLASS_RATIO_EXECUTION_MANIFEST_COLUMNS = [
    "task_id",
    "experiment_id",
    "ratio_id",
    "match_to_non_match_ratio",
    "model_id",
    "seed",
    "train_positive_count",
    "train_negative_count",
    "train_total_count",
    "validation_split",
    "validation_row_count",
    "test_split",
    "test_row_count",
    "validation_prediction_path",
    "test_prediction_path",
    "writes_files_now",
    "fit_allowed",
]


def load_class_ratio_protocol_config(path: str | Path) -> dict[str, Any]:
    """Load and validate a protocol-only class-ratio stress-test config."""

    with Path(path).open("r", encoding="utf-8") as file:
        config = json.load(file)
    validate_class_ratio_protocol_config(config)
    return config


def validate_class_ratio_protocol_config(config: Mapping[str, Any]) -> None:
    """Validate class-ratio protocol fields without allowing fitting."""

    if "class_ratio_stress_test" not in config:
        raise ClassRatioPlanError("Missing class_ratio_stress_test section")
    try:
        validate_protocol_config(
            {
                **dict(config),
                "fit_blockers": config.get("fit_blockers", []),
            }
        )
    except ExperimentProtocolError as error:
        raise ClassRatioPlanError(str(error)) from error

    stress = config["class_ratio_stress_test"]
    required = {
        "positive_label",
        "negative_label",
        "train_positive_policy",
        "negative_per_positive_values",
        "negative_sampling",
        "fixed_evaluation_splits",
    }
    missing = required - set(stress)
    if missing:
        raise ClassRatioPlanError(
            f"class_ratio_stress_test missing keys: {sorted(missing)}"
        )
    if stress["positive_label"] != 1 or stress["negative_label"] != 0:
        raise ClassRatioPlanError("Only labels 1=match and 0=non-match are supported")
    if stress["train_positive_policy"] != "use_all_available_positives":
        raise ClassRatioPlanError("Only use_all_available_positives is supported")

    values = stress["negative_per_positive_values"]
    if not values or len(set(values)) != len(values):
        raise ClassRatioPlanError("Ratio values must be non-empty and unique")
    if not all(isinstance(value, int) and value > 0 for value in values):
        raise ClassRatioPlanError("Ratio values must be positive integers")

    sampling = stress["negative_sampling"]
    if sampling.get("without_replacement") is not True:
        raise ClassRatioPlanError("Negative sampling must be without replacement")
    if sampling.get("seeded_by") != "experiment_seed":
        raise ClassRatioPlanError("Negative sampling must be seeded by experiment_seed")
    if sampling.get("write_sampled_tables_now") is not False:
        raise ClassRatioPlanError("Protocol preview must not write sampled tables")

    fixed_splits = stress["fixed_evaluation_splits"]
    if fixed_splits == ["validation", "test"]:
        return
    if fixed_splits == ["validation"]:
        if stress.get("test_negative_per_positive_policy") != "match_training_ratio":
            raise ClassRatioPlanError(
                "Sampled-test protocols must match the training class ratio"
            )
        test_sampling = stress.get("test_negative_sampling", {})
        if test_sampling.get("without_replacement") is not True:
            raise ClassRatioPlanError("Test negative sampling must be without replacement")
        if test_sampling.get("seeded_by") != "experiment_seed":
            raise ClassRatioPlanError("Test negative sampling must be seeded by experiment_seed")
        if test_sampling.get("write_sampled_tables_now") is not False:
            raise ClassRatioPlanError("Protocol preview must not write sampled test tables")
        return
    raise ClassRatioPlanError("Validation must remain fixed; test is fixed or ratio-sampled")


def build_class_ratio_run_plan(
    config_path: str | Path,
    *,
    model_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Build a class-ratio stress-test plan without training or writing artifacts."""

    config = load_class_ratio_protocol_config(config_path)
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

    ratio_plans = _build_ratio_plans(config, train_matrix)
    return {
        "experiment_id": config["experiment_id"],
        "status": config["status"],
        "fit_allowed": config["fit_allowed"],
        "ready_to_execute_training": False,
        "remaining_fit_blockers": config["fit_blockers"],
        "splits": config["splits"],
        "class_ratio_stress_test": config["class_ratio_stress_test"],
        "random_seeds": config["random_seeds"],
        "models": model_plans,
        "ratio_plans": ratio_plans,
        "fixed_evaluation_summary": {
            "validation": validation_matrix.to_summary(),
            "test": test_matrix.to_summary(),
        },
        "artifact_plan": _build_artifact_plan(config, selected_models, ratio_plans),
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


def class_ratio_plan_rows(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return compact report rows from a full class-ratio run plan."""

    validation = plan["fixed_evaluation_summary"]["validation"]
    test = plan["fixed_evaluation_summary"]["test"]
    rows = []
    for ratio in plan["ratio_plans"]:
        rows.append(
            {
                "ratio_id": ratio["ratio_id"],
                "match_to_non_match_ratio": ratio["match_to_non_match_ratio"],
                "positive_count": ratio["positive_count"],
                "negative_count": ratio["negative_count"],
                "total_count": ratio["total_count"],
                "uses_all_available_positives": ratio["uses_all_available_positives"],
                "uses_all_available_negatives": ratio["uses_all_available_negatives"],
                "seed_count": len(ratio["seed_plans"]),
                "validation_split": validation["split"],
                "validation_row_count": validation["row_count"],
                "validation_label_counts": validation["label_counts"],
                "test_split": test["split"],
                "test_row_count": test["row_count"],
                "test_label_counts": test["label_counts"],
            }
        )
    return rows


def class_ratio_execution_manifest_rows(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Expand a class-ratio plan into ratio/model/seed execution rows."""

    validation = plan["fixed_evaluation_summary"]["validation"]
    test = plan["fixed_evaluation_summary"]["test"]
    artifact_paths = plan["artifact_plan"]["raw_prediction_paths"]
    rows = []
    task_index = 1
    for ratio in plan["ratio_plans"]:
        ratio_id = ratio["ratio_id"]
        for model in plan["models"]:
            model_id = model["model_id"]
            for seed_plan in ratio["seed_plans"]:
                seed = seed_plan["seed"]
                paths = artifact_paths[ratio_id][model_id][str(seed)]
                rows.append(
                    {
                        "task_id": f"task_{task_index:03d}",
                        "experiment_id": plan["experiment_id"],
                        "ratio_id": ratio_id,
                        "match_to_non_match_ratio": ratio[
                            "match_to_non_match_ratio"
                        ],
                        "model_id": model_id,
                        "seed": seed,
                        "train_positive_count": seed_plan["positive_count"],
                        "train_negative_count": seed_plan["negative_count"],
                        "train_total_count": seed_plan["total_count"],
                        "validation_split": validation["split"],
                        "validation_row_count": validation["row_count"],
                        "test_split": test["split"],
                        "test_row_count": test["row_count"],
                        "validation_prediction_path": paths["validation"],
                        "test_prediction_path": paths["test"],
                        "writes_files_now": plan["artifact_plan"]["writes_files_now"],
                        "fit_allowed": plan["fit_allowed"],
                    }
                )
                task_index += 1
    return rows


def build_sampled_training_matrix(
    train_matrix: ModelMatrix,
    *,
    negatives_per_positive: int,
    seed: int,
) -> ModelMatrix:
    """Build a seeded class-ratio training matrix without writing files."""

    if negatives_per_positive <= 0:
        raise ClassRatioPlanError("negatives_per_positive must be positive")

    positive_indices = [
        index for index, label in enumerate(train_matrix.y) if label == 1
    ]
    negative_indices = [
        index for index, label in enumerate(train_matrix.y) if label == 0
    ]
    if not positive_indices:
        raise ClassRatioPlanError("Training matrix has no positive rows")
    if not negative_indices:
        raise ClassRatioPlanError("Training matrix has no negative rows")

    requested_negatives = len(positive_indices) * negatives_per_positive
    if requested_negatives > len(negative_indices):
        raise ClassRatioPlanError(
            "Requested ratio 1:{ratio} needs {requested} negatives, "
            "but only {available} are available".format(
                ratio=negatives_per_positive,
                requested=requested_negatives,
                available=len(negative_indices),
            )
        )

    sampled_negative_indices = _sample_negative_indices(
        negative_indices,
        requested_negatives,
        seed,
    )
    selected_indices = sorted([*positive_indices, *sampled_negative_indices])
    sampled_y = [train_matrix.y[index] for index in selected_indices]
    return ModelMatrix(
        dataset_id=train_matrix.dataset_id,
        split=f"{train_matrix.split}__match_1_nonmatch_{negatives_per_positive}",
        pair_ids=[train_matrix.pair_ids[index] for index in selected_indices],
        y=sampled_y,
        X=[train_matrix.X[index] for index in selected_indices],
        feature_columns=list(train_matrix.feature_columns),
        label_counts={
            "0": sampled_y.count(0),
            "1": sampled_y.count(1),
        },
    )


def write_class_ratio_plan_csv(
    rows: list[Mapping[str, Any]], output_path: str | Path
) -> int:
    """Write compact class-ratio plan rows to CSV."""

    if not rows:
        raise ClassRatioPlanError("At least one class-ratio plan row is required")
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CLASS_RATIO_PLAN_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(_format_plan_csv_row(row))
    return len(rows)


def write_class_ratio_plan_markdown(
    rows: list[Mapping[str, Any]], output_path: str | Path
) -> int:
    """Write compact class-ratio plan rows to Markdown."""

    if not rows:
        raise ClassRatioPlanError("At least one class-ratio plan row is required")
    lines = [
        "# Class-Ratio Stress-Test Plan",
        "",
        "Protocol: WDC Products `train_small` / `valid_small` / `test_unseen_100un`.",
        "",
        "| Ratio | Match Count | Non-Match Count | Total Train Rows | Seeds | Uses All Negatives |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| `{ratio}` | `{pos}` | `{neg}` | `{total}` | `{seeds}` | `{all_neg}` |".format(
                ratio=row["match_to_non_match_ratio"],
                pos=row["positive_count"],
                neg=row["negative_count"],
                total=row["total_count"],
                seeds=row["seed_count"],
                all_neg=row["uses_all_available_negatives"],
            )
        )
    validation = rows[0]
    lines.extend(
        [
            "",
            "Fixed evaluation splits:",
            "",
            f"- Validation: `{validation['validation_split']}`, rows `{validation['validation_row_count']}`, labels `{validation['validation_label_counts']}`.",
            f"- Test: `{validation['test_split']}`, rows `{validation['test_row_count']}`, labels `{validation['test_label_counts']}`.",
            "",
            "Notes:",
            "",
            "- Each ratio uses all 500 available training matches.",
            "- Non-matches are sampled without replacement using the experiment seed.",
            "- The preview writes no sampled training tables and runs no model fitting.",
        ]
    )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(rows)


def write_class_ratio_execution_manifest_csv(
    rows: list[Mapping[str, Any]], output_path: str | Path
) -> int:
    """Write ratio/model/seed execution manifest rows to CSV."""

    if not rows:
        raise ClassRatioPlanError("At least one execution manifest row is required")
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=CLASS_RATIO_EXECUTION_MANIFEST_COLUMNS
        )
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def write_class_ratio_execution_manifest_markdown(
    rows: list[Mapping[str, Any]], output_path: str | Path
) -> int:
    """Write a compact execution manifest summary to Markdown."""

    if not rows:
        raise ClassRatioPlanError("At least one execution manifest row is required")

    ratio_count = len({row["ratio_id"] for row in rows})
    model_count = len({row["model_id"] for row in rows})
    seed_count = len({row["seed"] for row in rows})
    lines = [
        "# Class-Ratio Execution Manifest",
        "",
        "Protocol: WDC Products `train_small` / `valid_small` / `test_unseen_100un`.",
        "",
        f"Total planned tasks: `{len(rows)}`.",
        f"Ratios: `{ratio_count}`; models: `{model_count}`; seeds: `{seed_count}`.",
        f"Fit allowed now: `{rows[0]['fit_allowed']}`.",
        f"Writes files now: `{rows[0]['writes_files_now']}`.",
        "",
        "| Ratio | Model | Seeds | Train Rows | Validation Rows | Test Rows |",
        "|---|---|---:|---:|---:|---:|",
    ]

    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((row["match_to_non_match_ratio"], row["model_id"]), []).append(
            row
        )
    for (ratio_label, model_id), group_rows in sorted(grouped.items()):
        first = group_rows[0]
        lines.append(
            "| `{ratio}` | `{model}` | `{seeds}` | `{train}` | `{validation}` | `{test}` |".format(
                ratio=ratio_label,
                model=model_id,
                seeds=len(group_rows),
                train=first["train_total_count"],
                validation=first["validation_row_count"],
                test=first["test_row_count"],
            )
        )

    lines.extend(
        [
            "",
            "Notes:",
            "",
            "- This manifest is a dry execution preview, not a training result.",
            "- Output paths are planned paths only.",
            "- The current protocol config has `fit_allowed: false`.",
        ]
    )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(rows)


def _build_ratio_plans(
    config: Mapping[str, Any], train_matrix: Any
) -> list[dict[str, Any]]:
    positive_indices = [
        index for index, label in enumerate(train_matrix.y) if label == 1
    ]
    negative_indices = [
        index for index, label in enumerate(train_matrix.y) if label == 0
    ]
    positive_count = len(positive_indices)
    negative_count = len(negative_indices)
    plans = []
    for negatives_per_positive in config["class_ratio_stress_test"][
        "negative_per_positive_values"
    ]:
        requested_negatives = positive_count * negatives_per_positive
        if requested_negatives > negative_count:
            raise ClassRatioPlanError(
                "Requested ratio 1:{ratio} needs {requested} negatives, "
                "but only {available} are available".format(
                    ratio=negatives_per_positive,
                    requested=requested_negatives,
                    available=negative_count,
                )
            )
        seed_plans = []
        for seed in config["random_seeds"]:
            sampled_matrix = build_sampled_training_matrix(
                train_matrix,
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
                    "sampled_pair_id_fingerprint": _fingerprint(
                        sampled_matrix.pair_ids
                    ),
                }
            )
        plans.append(
            {
                "ratio_id": f"match_1_nonmatch_{negatives_per_positive}",
                "match_to_non_match_ratio": f"1:{negatives_per_positive}",
                "positive_count": positive_count,
                "negative_count": requested_negatives,
                "total_count": positive_count + requested_negatives,
                "uses_all_available_positives": True,
                "uses_all_available_negatives": requested_negatives == negative_count,
                "seed_plans": seed_plans,
            }
        )
    return plans


def _sample_negative_indices(
    negative_indices: list[int], requested_count: int, seed: int
) -> list[int]:
    if requested_count == len(negative_indices):
        return list(negative_indices)
    rng = random.Random(seed)
    return sorted(rng.sample(negative_indices, requested_count))


def _fingerprint(pair_ids: list[str]) -> str:
    payload = "\n".join(sorted(pair_ids)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _format_plan_csv_row(row: Mapping[str, Any]) -> dict[str, Any]:
    formatted = dict(row)
    formatted["validation_label_counts"] = json.dumps(
        formatted["validation_label_counts"], sort_keys=True
    )
    formatted["test_label_counts"] = json.dumps(
        formatted["test_label_counts"], sort_keys=True
    )
    return formatted


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
    ratio_plans: list[Mapping[str, Any]],
) -> dict[str, Any]:
    raw_prediction_paths: dict[str, Any] = {}
    for ratio in ratio_plans:
        ratio_id = ratio["ratio_id"]
        raw_prediction_paths[ratio_id] = {}
        for model_id in model_ids:
            raw_prediction_paths[ratio_id][model_id] = {}
            for seed in config["random_seeds"]:
                raw_prediction_paths[ratio_id][model_id][str(seed)] = {
                    split_role: str(
                        Path(config["results_root"])
                        / "predictions"
                        / config["experiment_id"]
                        / ratio_id
                        / model_id
                        / f"seed_{seed}"
                        / f"{split_role}.csv"
                    )
                    for split_role in ("validation", "test")
                }
    return {
        "raw_prediction_schema_version": "raw_predictions_v1",
        "raw_prediction_paths": raw_prediction_paths,
        "writes_files_now": False,
        "writes_sampled_training_tables_now": False,
    }
