"""Build baseline run plans without fitting or predicting."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from entity_matching.evaluation import prediction_artifact_path
from entity_matching.experiments.protocol import (
    load_protocol_config,
    validate_protocol_guards,
)
from entity_matching.models import (
    describe_estimator,
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


class BaselineRunPlanError(ValueError):
    """Raised when a safe baseline run plan cannot be built."""


def build_baseline_run_plan(
    protocol_config_path: str | Path,
    *,
    model_ids: list[str] | None = None,
    results_root: str | Path = "results",
) -> dict[str, Any]:
    """Build a training-run plan while keeping fitting disabled."""

    protocol = load_protocol_config(protocol_config_path)
    protocol_summary = validate_protocol_guards(protocol_config_path)
    model_config = load_model_config(protocol["model_config"])

    selected_model_ids = model_ids or list(protocol["planned_models"])
    model_summaries = [
        _build_model_plan(model_config, model_id, protocol["random_seeds"])
        for model_id in selected_model_ids
    ]

    matrix_summary = _build_protocol_matrix_summary(protocol)
    artifact_plan = _build_artifact_plan(
        protocol["experiment_id"],
        selected_model_ids,
        protocol["random_seeds"],
        results_root,
    )

    return {
        "experiment_id": protocol["experiment_id"],
        "status": protocol["status"],
        "fit_allowed": protocol["fit_allowed"],
        "ready_to_execute_training": False,
        "remaining_fit_blockers": protocol["fit_blockers"],
        "splits": protocol["splits"],
        "threshold_selection": protocol["threshold_selection"],
        "final_test_policy": protocol["final_test_policy"],
        "random_seeds": protocol["random_seeds"],
        "model_config": protocol["model_config"],
        "models": model_summaries,
        "matrix_summary": matrix_summary,
        "artifact_plan": artifact_plan,
        "protocol_guard_summary": _compact_protocol_guard_summary(protocol_summary),
    }


def _build_model_plan(
    model_config: dict[str, Any], model_id: str, random_seeds: list[int]
) -> dict[str, Any]:
    definition = get_model_definition(model_config, model_id)
    estimators = []
    for seed in random_seeds:
        estimator = instantiate_model(definition, random_seed=seed)
        estimators.append(
            {
                "seed": seed,
                "estimator": describe_estimator(estimator),
            }
        )
    return {
        "model_id": model_id,
        "family": definition["family"],
        "status": definition["status"],
        "estimators": estimators,
    }


def _build_protocol_matrix_summary(protocol: dict[str, Any]) -> dict[str, Any]:
    split_names = [
        protocol["splits"]["train"],
        protocol["splits"]["validation"],
        protocol["splits"]["test"],
    ]
    report = build_split_guard_report(
        protocol["dataset_config"],
        processed_root=protocol["processed_root"],
        split_names=split_names,
    )
    assert_no_leakage(
        report,
        require_pair_disjoint=True,
        require_record_disjoint=True,
        require_entity_disjoint=False,
    )
    manifest = build_split_manifest(
        protocol["dataset_config"],
        processed_root=protocol["processed_root"],
        split_names=split_names,
    )
    matrices = {
        split_name: load_model_matrix(manifest, split_name)
        for split_name in split_names
    }
    return {
        "dataset_id": manifest.dataset_id,
        "feature_columns": matrices[split_names[0]].feature_columns,
        "splits": {
            role: matrices[split_name].to_summary()
            for role, split_name in protocol["splits"].items()
        },
        "allowed_train_validation_entity_overlap": report[
            "record_entity_overlaps"
        ].get("train_small__valid_small"),
    }


def _build_artifact_plan(
    experiment_id: str,
    model_ids: list[str],
    random_seeds: list[int],
    results_root: str | Path,
) -> dict[str, Any]:
    artifacts = {}
    for model_id in model_ids:
        artifacts[model_id] = {}
        for seed in random_seeds:
            artifacts[model_id][str(seed)] = {
                split_role: str(
                    prediction_artifact_path(
                        results_root,
                        experiment_id,
                        model_id,
                        seed,
                        split_role,
                    )
                )
                for split_role in ("validation", "test")
            }
    return {
        "raw_prediction_schema_version": "raw_predictions_v1",
        "raw_prediction_paths": artifacts,
        "writes_files_now": False,
    }


def _compact_protocol_guard_summary(protocol_summary: dict[str, Any]) -> dict[str, Any]:
    train_validation_overlap = protocol_summary["train_validation_guard_report"][
        "record_entity_overlaps"
    ]["train_small__valid_small"]
    train_test_overlap = protocol_summary["development_to_test_guard_reports"][
        "train_to_test"
    ]["record_entity_overlaps"]["test_unseen_100un__train_small"]
    validation_test_overlap = protocol_summary["development_to_test_guard_reports"][
        "validation_to_test"
    ]["record_entity_overlaps"]["test_unseen_100un__valid_small"]
    return {
        "train_validation_overlap": train_validation_overlap,
        "train_test_overlap": train_test_overlap,
        "validation_test_overlap": validation_test_overlap,
    }
