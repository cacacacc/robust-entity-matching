"""Qualitative error analysis for raw prediction artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean
from typing import Any, Iterable, Mapping

from entity_matching.data.pairs import PairRecord, load_pair_table
from entity_matching.evaluation.predictions import read_prediction_csv


ERROR_ANALYSIS_SCHEMA_VERSION = "error_analysis_v1"

CONFUSION_LABELS = {
    (1, 1): "true_positive",
    (0, 1): "false_positive",
    (0, 0): "true_negative",
    (1, 0): "false_negative",
}

DEFAULT_FEATURE_COLUMNS = [
    "attr_brand_exact_match",
    "attr_brand_token_jaccard",
    "attr_title_token_jaccard",
    "attr_title_numeric_overlap",
    "attr_description_token_jaccard",
    "attr_price_exact_match",
    "attr_price_numeric_overlap",
    "combined_token_jaccard",
    "combined_numeric_overlap",
]


class ErrorAnalysisError(ValueError):
    """Raised when error-analysis inputs are invalid."""


def analyze_prediction_errors(
    dataset_config_path: str | Path,
    split: str,
    prediction_path: str | Path,
    feature_table_path: str | Path | None = None,
    examples_per_error_type: int = 10,
) -> dict[str, Any]:
    """Join predictions with source pairs and summarize FP/FN behavior."""

    predictions = read_prediction_csv(prediction_path)
    pair_lookup = {pair.pair_id: pair for pair in load_pair_table(dataset_config_path, split)}
    feature_lookup = _load_feature_lookup(feature_table_path) if feature_table_path else {}

    joined_rows = []
    counts = {label: 0 for label in CONFUSION_LABELS.values()}
    for prediction in predictions:
        pair_id = prediction["pair_id"]
        if pair_id not in pair_lookup:
            raise ErrorAnalysisError(f"Prediction pair_id missing from pair table: {pair_id}")
        label = CONFUSION_LABELS[(prediction["y_true"], prediction["y_pred"])]
        counts[label] += 1
        joined_rows.append(
            {
                "prediction": prediction,
                "pair": pair_lookup[pair_id],
                "features": feature_lookup.get(pair_id, {}),
                "error_type": label,
            }
        )

    false_positives = [row for row in joined_rows if row["error_type"] == "false_positive"]
    false_negatives = [row for row in joined_rows if row["error_type"] == "false_negative"]

    return {
        "schema_version": ERROR_ANALYSIS_SCHEMA_VERSION,
        "dataset_config_path": str(dataset_config_path),
        "split": split,
        "prediction_path": str(prediction_path),
        "feature_table_path": str(feature_table_path) if feature_table_path else None,
        "experiment_id": predictions[0]["experiment_id"],
        "model_id": predictions[0]["model_id"],
        "seed": predictions[0]["seed"],
        "threshold": predictions[0]["threshold"],
        "row_count": len(joined_rows),
        "confusion_counts": counts,
        "error_summary": {
            "false_positive_count": len(false_positives),
            "false_negative_count": len(false_negatives),
            "false_positive_hard_negative_count": _count_hard_negatives(false_positives),
            "false_negative_hard_negative_count": _count_hard_negatives(false_negatives),
            "false_positive_score_stats": _score_stats(false_positives),
            "false_negative_score_stats": _score_stats(false_negatives),
            "feature_means_by_group": _feature_means_by_group(
                joined_rows, DEFAULT_FEATURE_COLUMNS
            ),
        },
        "examples": {
            "false_positives_highest_score": [
                _example_row(row)
                for row in sorted(
                    false_positives,
                    key=lambda item: item["prediction"]["score"],
                    reverse=True,
                )[:examples_per_error_type]
            ],
            "false_negatives_lowest_score": [
                _example_row(row)
                for row in sorted(
                    false_negatives,
                    key=lambda item: item["prediction"]["score"],
                )[:examples_per_error_type]
            ],
        },
        "notes": [
            "Examples contain raw product attributes and should remain local.",
            "The analyzed seed is descriptive; it is not used for additional model selection.",
        ],
    }


def write_error_analysis_json(analysis: Mapping[str, Any], output_path: str | Path) -> None:
    """Write error analysis as JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(analysis, file, indent=2, sort_keys=True, ensure_ascii=False)
        file.write("\n")


def write_error_analysis_markdown(
    analysis: Mapping[str, Any], output_path: str | Path
) -> None:
    """Write a compact local Markdown report with selected error examples."""

    counts = analysis["confusion_counts"]
    summary = analysis["error_summary"]
    lines = [
        "# Prediction Error Analysis",
        "",
        f"Experiment: `{analysis['experiment_id']}`",
        f"Model: `{analysis['model_id']}`",
        f"Seed: `{analysis['seed']}`",
        f"Split: `{analysis['split']}`",
        f"Threshold: `{analysis['threshold']}`",
        "",
        "## Confusion Counts",
        "",
        "| Type | Count |",
        "|---|---:|",
    ]
    for key in ["true_positive", "false_positive", "true_negative", "false_negative"]:
        lines.append(f"| `{key}` | `{counts[key]}` |")

    lines.extend(
        [
            "",
            "## Error Summary",
            "",
            f"- False positives: `{summary['false_positive_count']}`.",
            f"- False negatives: `{summary['false_negative_count']}`.",
            f"- False positives that are WDC hard negatives: `{summary['false_positive_hard_negative_count']}`.",
            f"- False negatives that are WDC hard negatives: `{summary['false_negative_hard_negative_count']}`.",
            "",
            "## Feature Means By Group",
            "",
            "| Feature | TP | FP | TN | FN |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    feature_groups = summary["feature_means_by_group"]
    for feature_name in DEFAULT_FEATURE_COLUMNS:
        values = [
            _format_optional_float(feature_groups[group].get(feature_name))
            for group in ["true_positive", "false_positive", "true_negative", "false_negative"]
        ]
        lines.append(f"| `{feature_name}` | {' | '.join(values)} |")

    lines.extend(_markdown_examples("False Positives", analysis["examples"]["false_positives_highest_score"]))
    lines.extend(_markdown_examples("False Negatives", analysis["examples"]["false_negatives_lowest_score"]))
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This report includes raw product attributes and should stay under ignored `results/error_analysis/`.",
            "- The seed is used for descriptive inspection only, not for test-set model selection.",
        ]
    )

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _load_feature_lookup(path: str | Path) -> dict[str, dict[str, float]]:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or "pair_id" not in reader.fieldnames:
            raise ErrorAnalysisError(f"Feature table missing pair_id column: {path}")
        lookup: dict[str, dict[str, float]] = {}
        for row in reader:
            lookup[row["pair_id"]] = {
                key: float(value)
                for key, value in row.items()
                if key not in {"dataset_id", "split", "pair_id", "label"}
            }
        return lookup


def _score_stats(rows: list[Mapping[str, Any]]) -> dict[str, float | None]:
    if not rows:
        return {"min": None, "mean": None, "max": None}
    scores = [float(row["prediction"]["score"]) for row in rows]
    return {"min": min(scores), "mean": mean(scores), "max": max(scores)}


def _count_hard_negatives(rows: list[Mapping[str, Any]]) -> int:
    return sum(1 for row in rows if row["pair"].is_hard_negative is True)


def _feature_means_by_group(
    rows: Iterable[Mapping[str, Any]], feature_columns: Iterable[str]
) -> dict[str, dict[str, float | None]]:
    result: dict[str, dict[str, float | None]] = {}
    for group_name in CONFUSION_LABELS.values():
        group_rows = [row for row in rows if row["error_type"] == group_name]
        result[group_name] = {}
        for column in feature_columns:
            values = [
                float(row["features"][column])
                for row in group_rows
                if column in row["features"]
            ]
            result[group_name][column] = mean(values) if values else None
    return result


def _example_row(row: Mapping[str, Any]) -> dict[str, Any]:
    prediction = row["prediction"]
    pair: PairRecord = row["pair"]
    return {
        "pair_id": pair.pair_id,
        "score": prediction["score"],
        "threshold": prediction["threshold"],
        "y_true": prediction["y_true"],
        "y_pred": prediction["y_pred"],
        "is_hard_negative": pair.is_hard_negative,
        "left_record_id": pair.left_record_id,
        "right_record_id": pair.right_record_id,
        "left": _compact_attributes(pair.left_attributes),
        "right": _compact_attributes(pair.right_attributes),
        "selected_features": {
            key: row["features"][key]
            for key in DEFAULT_FEATURE_COLUMNS
            if key in row["features"]
        },
    }


def _compact_attributes(attributes: Mapping[str, str | None]) -> dict[str, str | None]:
    compact: dict[str, str | None] = {}
    for key, value in attributes.items():
        if value is None:
            compact[key] = None
        else:
            compact[key] = _truncate(value)
    return compact


def _truncate(value: str, limit: int = 180) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3] + "..."


def _markdown_examples(title: str, examples: Iterable[Mapping[str, Any]]) -> list[str]:
    lines = ["", f"## {title}", ""]
    for index, example in enumerate(examples, start=1):
        lines.extend(
            [
                f"### Example {index}: `{example['pair_id']}`",
                "",
                f"- Score: `{example['score']}`; threshold: `{example['threshold']}`; hard negative: `{example['is_hard_negative']}`.",
                f"- Left title: {example['left'].get('title_left')}",
                f"- Right title: {example['right'].get('title_right')}",
                f"- Left brand: {example['left'].get('brand_left')}; right brand: {example['right'].get('brand_right')}.",
                f"- Left price: {example['left'].get('price_left')} {example['left'].get('priceCurrency_left')}; right price: {example['right'].get('price_right')} {example['right'].get('priceCurrency_right')}.",
                "",
            ]
        )
    return lines


def _format_optional_float(value: float | None) -> str:
    if value is None:
        return "`n/a`"
    return f"`{value:.6f}`"
