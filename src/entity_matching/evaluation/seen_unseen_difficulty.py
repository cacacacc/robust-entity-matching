"""Aggregate split-difficulty analysis for WDC seen and unseen tests."""

from __future__ import annotations

import csv
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Iterable, Mapping

from entity_matching.data.pairs import PairRecord, load_pair_table
from entity_matching.evaluation.metrics import (
    binary_confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from entity_matching.evaluation.predictions import read_prediction_csv


SEEN_UNSEEN_DIFFICULTY_SCHEMA_VERSION = "seen_unseen_difficulty_v1"

DEFAULT_DIFFICULTY_FEATURE_COLUMNS = [
    "attr_brand_exact_match",
    "attr_brand_token_jaccard",
    "attr_title_edit_similarity",
    "attr_title_token_jaccard",
    "attr_title_numeric_overlap",
    "attr_description_token_jaccard",
    "attr_price_exact_match",
    "attr_price_numeric_overlap",
    "combined_edit_similarity",
    "combined_token_jaccard",
    "combined_numeric_overlap",
]

SPLIT_DIFFICULTY_SUMMARY_COLUMNS = [
    "split_label",
    "split",
    "experiment_id",
    "model_id",
    "seed",
    "threshold",
    "row_count",
    "positive_count",
    "negative_count",
    "hard_negative_count",
    "hard_negative_negative_count",
    "predicted_positive_count",
    "tp",
    "fp",
    "tn",
    "fn",
    "precision",
    "recall",
    "f1",
    "false_positive_rate",
    "false_negative_rate",
    "false_positive_hard_negative_count",
    "false_positive_hard_negative_rate",
    "positive_score_mean",
    "positive_score_std",
    "negative_score_mean",
    "negative_score_std",
    "near_threshold_count",
    "near_threshold_rate",
    "negative_near_threshold_count",
    "negative_near_threshold_rate",
]

FEATURE_DIFFICULTY_COLUMNS = [
    "split_label",
    "split",
    "group",
    "row_count",
    *DEFAULT_DIFFICULTY_FEATURE_COLUMNS,
]

SEEN_UNSEEN_ERROR_PROFILE_COLUMNS = [
    "model_id",
    "seed",
    "seen_experiment_id",
    "unseen_experiment_id",
    "seen_threshold",
    "unseen_threshold",
    "seen_fp",
    "unseen_fp",
    "seen_minus_unseen_fp",
    "seen_fn",
    "unseen_fn",
    "seen_minus_unseen_fn",
    "seen_precision",
    "unseen_precision",
    "unseen_minus_seen_precision",
    "seen_recall",
    "unseen_recall",
    "unseen_minus_seen_recall",
    "seen_f1",
    "unseen_f1",
    "unseen_minus_seen_f1",
]

SEEN_UNSEEN_MODEL_ERROR_PROFILE_COLUMNS = [
    "model_id",
    "seed_count",
    "seen_fp_mean",
    "unseen_fp_mean",
    "seen_minus_unseen_fp_mean",
    "seen_minus_unseen_fp_std",
    "seen_fp_greater_seed_count",
    "seen_fn_mean",
    "unseen_fn_mean",
    "seen_minus_unseen_fn_mean",
    "seen_minus_unseen_fn_std",
    "seen_fn_greater_seed_count",
    "unseen_minus_seen_precision_mean",
    "unseen_minus_seen_precision_std",
    "unseen_precision_greater_seed_count",
    "unseen_minus_seen_recall_mean",
    "unseen_minus_seen_recall_std",
    "unseen_recall_greater_seed_count",
    "unseen_minus_seen_f1_mean",
    "unseen_minus_seen_f1_std",
    "unseen_f1_greater_seed_count",
]

CONFUSION_GROUPS = {
    (1, 1): "true_positive",
    (0, 1): "false_positive",
    (0, 0): "true_negative",
    (1, 0): "false_negative",
}


class SeenUnseenDifficultyError(ValueError):
    """Raised when seen/unseen difficulty inputs are invalid."""


def load_seen_unseen_difficulty_analysis(
    dataset_config_path: str | Path,
    seen_prediction_path: str | Path,
    unseen_prediction_path: str | Path,
    seen_feature_table_path: str | Path,
    unseen_feature_table_path: str | Path,
    *,
    seen_split: str = "test_seen_000un",
    unseen_split: str = "test_unseen_100un",
    feature_columns: Iterable[str] = DEFAULT_DIFFICULTY_FEATURE_COLUMNS,
) -> dict[str, Any]:
    """Build descriptive split-difficulty summaries for seen and unseen tests."""

    selected_features = list(feature_columns)
    seen_rows = _load_joined_rows(
        dataset_config_path,
        seen_split,
        seen_prediction_path,
        seen_feature_table_path,
    )
    unseen_rows = _load_joined_rows(
        dataset_config_path,
        unseen_split,
        unseen_prediction_path,
        unseen_feature_table_path,
    )
    split_summary_rows = [
        _split_summary_row("seen", seen_split, seen_rows),
        _split_summary_row("unseen", unseen_split, unseen_rows),
    ]
    feature_group_rows = []
    for split_label, split, rows in [
        ("seen", seen_split, seen_rows),
        ("unseen", unseen_split, unseen_rows),
    ]:
        feature_group_rows.extend(
            _feature_group_rows(split_label, split, rows, selected_features)
        )
    return {
        "schema_version": SEEN_UNSEEN_DIFFICULTY_SCHEMA_VERSION,
        "dataset_config_path": str(dataset_config_path),
        "split_summary_rows": split_summary_rows,
        "feature_group_rows": feature_group_rows,
        "feature_columns": selected_features,
        "notes": [
            "This is descriptive analysis of existing raw predictions; it does not train or select a model.",
            "The configured Random Forest seed is used for error-profile inspection only.",
            "Tracked reports contain aggregate statistics only, not raw product attributes.",
        ],
    }


def write_split_difficulty_summary_csv(
    rows: list[Mapping[str, Any]], output_path: str | Path
) -> int:
    """Write one aggregate summary row per split."""

    return _write_csv(rows, output_path, SPLIT_DIFFICULTY_SUMMARY_COLUMNS)


def write_feature_difficulty_csv(
    rows: list[Mapping[str, Any]], output_path: str | Path
) -> int:
    """Write feature means by split and prediction/error group."""

    return _write_csv(rows, output_path, FEATURE_DIFFICULTY_COLUMNS)


def write_seen_unseen_difficulty_markdown(
    analysis: Mapping[str, Any], output_path: str | Path
) -> int:
    """Write a compact Chinese interpretation of seen/unseen difficulty."""

    summary_rows = list(analysis["split_summary_rows"])
    feature_rows = list(analysis["feature_group_rows"])
    if len(summary_rows) != 2:
        raise SeenUnseenDifficultyError("Expected exactly two split summary rows")
    seen = _row_by_label(summary_rows, "seen")
    unseen = _row_by_label(summary_rows, "unseen")
    feature_index = {
        (row["split_label"], row["group"]): row
        for row in feature_rows
    }

    lines = [
        "# Seen/Unseen Split Difficulty Analysis",
        "",
        "本报告只分析已经生成的 raw predictions 和 processed feature tables；没有重新训练模型，也没有使用 test set 做模型选择。",
        "",
        "分析对象：Random Forest，seed `13`。这个 seed 只用于定性/描述性错误剖析。",
        "",
        "## Split Summary",
        "",
        "| Split | Positives | Negatives | Hard Negatives | TP | FP | TN | FN | Precision | Recall | F1 | FP Rate | Near Threshold Rate |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            "| `{split}` | `{pos}` | `{neg}` | `{hard}` | `{tp}` | `{fp}` | `{tn}` | `{fn}` | `{precision}` | `{recall}` | `{f1}` | `{fp_rate}` | `{near_rate}` |".format(
                split=row["split"],
                pos=row["positive_count"],
                neg=row["negative_count"],
                hard=row["hard_negative_count"],
                tp=row["tp"],
                fp=row["fp"],
                tn=row["tn"],
                fn=row["fn"],
                precision=_format_float(row["precision"]),
                recall=_format_float(row["recall"]),
                f1=_format_float(row["f1"]),
                fp_rate=_format_float(row["false_positive_rate"]),
                near_rate=_format_float(row["near_threshold_rate"]),
            )
        )

    fp_delta = int(seen["fp"]) - int(unseen["fp"])
    fn_delta = int(seen["fn"]) - int(unseen["fn"])
    precision_delta = float(unseen["precision"]) - float(seen["precision"])
    f1_delta = float(unseen["f1"]) - float(seen["f1"])
    seen_fp_hard_rate = _safe_float(seen["false_positive_hard_negative_rate"])
    unseen_fp_hard_rate = _safe_float(unseen["false_positive_hard_negative_rate"])

    lines.extend(
        [
            "",
            "## Key Interpretation",
            "",
            f"- 两个 test split 的标签规模相同：都是 `{seen['positive_count']}` 个 match 和 `{seen['negative_count']}` 个 non-match。",
            f"- 两个 split 的 hard-negative 总数也相同：都是 `{seen['hard_negative_count']}`。",
            f"- Random Forest 在 seen split 上多产生 `{fp_delta}` 个 false positives，多产生 `{fn_delta}` 个 false negatives。",
            f"- unseen 相比 seen 的 precision 高 `{precision_delta:.6f}`，F1 高 `{f1_delta:.6f}`。",
            f"- false positives 中 hard negatives 的比例：seen `{seen_fp_hard_rate:.6f}`，unseen `{unseen_fp_hard_rate:.6f}`。",
            "",
            "这说明当前结果不能简单解释成“seen 一定更容易，unseen 一定更难”。在这个 WDC 官方 split 上，seen 的错误主要来自更多 non-match 被模型判成 match，也就是 precision 被 false positives 拉低。",
            "",
            "## Feature Means By Group",
            "",
            "下面只展示对解释最有用的几个相似度特征。数值越高，表示两个商品在对应字段上越像。",
            "",
            "| Split | Group | Count | Title Jaccard | Title Numeric | Combined Jaccard | Combined Numeric | Combined Edit |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for split_label in ["seen", "unseen"]:
        for group in ["negative", "false_positive", "positive", "false_negative"]:
            row = feature_index[(split_label, group)]
            lines.append(
                "| `{split}` | `{group}` | `{count}` | `{title_j}` | `{title_num}` | `{combined_j}` | `{combined_num}` | `{combined_edit}` |".format(
                    split=row["split"],
                    group=group,
                    count=row["row_count"],
                    title_j=_format_optional_float(row["attr_title_token_jaccard"]),
                    title_num=_format_optional_float(row["attr_title_numeric_overlap"]),
                    combined_j=_format_optional_float(row["combined_token_jaccard"]),
                    combined_num=_format_optional_float(row["combined_numeric_overlap"]),
                    combined_edit=_format_optional_float(row["combined_edit_similarity"]),
                )
            )

    lines.extend(
        [
            "",
            "## What This Means For The Project",
            "",
            "- `seen/unseen` 是实体重叠维度，不等价于“容易/困难”维度。",
            "- `class ratio` 和 `hard negative composition` 仍然需要单独报告；否则 F1/precision 的变化会被误读。",
            "- 最终论文中应把 seen 结果写成 diagnostic result，把 unseen 结果保留为主要 robustness result。",
        ]
    )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(summary_rows) + len(feature_rows)


def load_seen_unseen_error_profile_rows(
    dataset_config_path: str | Path,
    prediction_pairs: Iterable[Mapping[str, str | Path]],
    seen_feature_table_path: str | Path,
    unseen_feature_table_path: str | Path,
    *,
    seen_split: str = "test_seen_000un",
    unseen_split: str = "test_unseen_100un",
) -> list[dict[str, Any]]:
    """Build model/seed seen-vs-unseen error-profile rows."""

    rows = []
    for pair in prediction_pairs:
        seen_row = _split_summary_row(
            "seen",
            seen_split,
            _load_joined_rows(
                dataset_config_path,
                seen_split,
                pair["seen_prediction_path"],
                seen_feature_table_path,
            ),
        )
        unseen_row = _split_summary_row(
            "unseen",
            unseen_split,
            _load_joined_rows(
                dataset_config_path,
                unseen_split,
                pair["unseen_prediction_path"],
                unseen_feature_table_path,
            ),
        )
        rows.append(_error_profile_row(seen_row, unseen_row))
    rows.sort(key=lambda row: (row["model_id"], int(row["seed"])))
    return rows


def summarize_seen_unseen_error_profiles(
    rows: list[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Summarize seed-level seen-vs-unseen profiles by model."""

    if not rows:
        raise SeenUnseenDifficultyError("At least one error-profile row is required")
    output = []
    for model_id in sorted({row["model_id"] for row in rows}):
        model_rows = [row for row in rows if row["model_id"] == model_id]
        fp_deltas = [float(row["seen_minus_unseen_fp"]) for row in model_rows]
        fn_deltas = [float(row["seen_minus_unseen_fn"]) for row in model_rows]
        precision_deltas = [
            float(row["unseen_minus_seen_precision"]) for row in model_rows
        ]
        recall_deltas = [float(row["unseen_minus_seen_recall"]) for row in model_rows]
        f1_deltas = [float(row["unseen_minus_seen_f1"]) for row in model_rows]
        output.append(
            {
                "model_id": model_id,
                "seed_count": len(model_rows),
                "seen_fp_mean": mean(float(row["seen_fp"]) for row in model_rows),
                "unseen_fp_mean": mean(float(row["unseen_fp"]) for row in model_rows),
                "seen_minus_unseen_fp_mean": mean(fp_deltas),
                "seen_minus_unseen_fp_std": pstdev(fp_deltas),
                "seen_fp_greater_seed_count": sum(1 for value in fp_deltas if value > 0),
                "seen_fn_mean": mean(float(row["seen_fn"]) for row in model_rows),
                "unseen_fn_mean": mean(float(row["unseen_fn"]) for row in model_rows),
                "seen_minus_unseen_fn_mean": mean(fn_deltas),
                "seen_minus_unseen_fn_std": pstdev(fn_deltas),
                "seen_fn_greater_seed_count": sum(1 for value in fn_deltas if value > 0),
                "unseen_minus_seen_precision_mean": mean(precision_deltas),
                "unseen_minus_seen_precision_std": pstdev(precision_deltas),
                "unseen_precision_greater_seed_count": sum(
                    1 for value in precision_deltas if value > 0
                ),
                "unseen_minus_seen_recall_mean": mean(recall_deltas),
                "unseen_minus_seen_recall_std": pstdev(recall_deltas),
                "unseen_recall_greater_seed_count": sum(
                    1 for value in recall_deltas if value > 0
                ),
                "unseen_minus_seen_f1_mean": mean(f1_deltas),
                "unseen_minus_seen_f1_std": pstdev(f1_deltas),
                "unseen_f1_greater_seed_count": sum(1 for value in f1_deltas if value > 0),
            }
        )
    return output


def write_seen_unseen_error_profile_csv(
    rows: list[Mapping[str, Any]], output_path: str | Path
) -> int:
    """Write seed-level seen-vs-unseen error profiles."""

    return _write_csv(rows, output_path, SEEN_UNSEEN_ERROR_PROFILE_COLUMNS)


def write_seen_unseen_model_error_profile_csv(
    rows: list[Mapping[str, Any]], output_path: str | Path
) -> int:
    """Write model-level seen-vs-unseen error-profile summaries."""

    return _write_csv(rows, output_path, SEEN_UNSEEN_MODEL_ERROR_PROFILE_COLUMNS)


def write_seen_unseen_error_profile_markdown(
    seed_rows: list[Mapping[str, Any]],
    model_rows: list[Mapping[str, Any]],
    output_path: str | Path,
) -> int:
    """Write a compact Chinese all-seed error-profile report."""

    lines = [
        "# Seen/Unseen All-Seed Error Profile",
        "",
        "本报告聚合已有 raw prediction CSV；没有重新训练模型，也没有使用 test set 做模型选择。",
        "",
        "## Model-Level Stability",
        "",
        "| Model | Seeds | Seen FP Mean | Unseen FP Mean | Seen-Unseen FP | Seeds Seen FP Higher | Unseen-Seen Precision | Unseen-Seen F1 | Seeds Unseen F1 Higher |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in model_rows:
        lines.append(
            "| `{model}` | `{seeds}` | `{seen_fp}` | `{unseen_fp}` | `{fp_delta}` | `{fp_count}` | `{precision_delta}` | `{f1_delta}` | `{f1_count}` |".format(
                model=row["model_id"],
                seeds=row["seed_count"],
                seen_fp=_format_float(row["seen_fp_mean"]),
                unseen_fp=_format_float(row["unseen_fp_mean"]),
                fp_delta=_format_float(row["seen_minus_unseen_fp_mean"]),
                fp_count=row["seen_fp_greater_seed_count"],
                precision_delta=_format_float(row["unseen_minus_seen_precision_mean"]),
                f1_delta=_format_float(row["unseen_minus_seen_f1_mean"]),
                f1_count=row["unseen_f1_greater_seed_count"],
            )
        )

    lines.extend(
        [
            "",
            "## Seed-Level Rows",
            "",
            "| Model | Seed | Seen FP | Unseen FP | Seen-Unseen FP | Seen F1 | Unseen F1 | Unseen-Seen F1 |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in seed_rows:
        lines.append(
            "| `{model}` | `{seed}` | `{seen_fp}` | `{unseen_fp}` | `{fp_delta}` | `{seen_f1}` | `{unseen_f1}` | `{f1_delta}` |".format(
                model=row["model_id"],
                seed=row["seed"],
                seen_fp=row["seen_fp"],
                unseen_fp=row["unseen_fp"],
                fp_delta=row["seen_minus_unseen_fp"],
                seen_f1=_format_float(row["seen_f1"]),
                unseen_f1=_format_float(row["unseen_f1"]),
                f1_delta=_format_float(row["unseen_minus_seen_f1"]),
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- 如果 `Seeds Seen FP Higher` 接近 seed 总数，说明 seen split 的 precision penalty 不是单个 seed 的偶然现象。",
            "- 如果 `Seeds Unseen F1 Higher` 接近 seed 总数，说明 unseen > seen 的方向在该模型上稳定。",
            "- 这些结果仍然是 descriptive analysis；最终 robustness claim 仍应以 entity-disjoint unseen split 为主。",
        ]
    )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(seed_rows) + len(model_rows)


def _load_joined_rows(
    dataset_config_path: str | Path,
    split: str,
    prediction_path: str | Path,
    feature_table_path: str | Path,
) -> list[dict[str, Any]]:
    predictions = read_prediction_csv(prediction_path)
    pair_lookup = {pair.pair_id: pair for pair in load_pair_table(dataset_config_path, split)}
    feature_lookup = _load_feature_lookup(feature_table_path)
    rows = []
    for prediction in predictions:
        pair_id = prediction["pair_id"]
        if prediction["split"] != split:
            raise SeenUnseenDifficultyError(
                f"Prediction split mismatch for {pair_id}: {prediction['split']} != {split}"
            )
        if pair_id not in pair_lookup:
            raise SeenUnseenDifficultyError(f"Prediction pair_id missing from pair table: {pair_id}")
        if pair_id not in feature_lookup:
            raise SeenUnseenDifficultyError(f"Prediction pair_id missing from features: {pair_id}")
        group = CONFUSION_GROUPS[(prediction["y_true"], prediction["y_pred"])]
        rows.append(
            {
                "prediction": prediction,
                "pair": pair_lookup[pair_id],
                "features": feature_lookup[pair_id],
                "group": group,
            }
        )
    return rows


def _error_profile_row(
    seen_row: Mapping[str, Any],
    unseen_row: Mapping[str, Any],
) -> dict[str, Any]:
    if seen_row["model_id"] != unseen_row["model_id"]:
        raise SeenUnseenDifficultyError(
            f"Model mismatch: {seen_row['model_id']} != {unseen_row['model_id']}"
        )
    if int(seen_row["seed"]) != int(unseen_row["seed"]):
        raise SeenUnseenDifficultyError(
            f"Seed mismatch: {seen_row['seed']} != {unseen_row['seed']}"
        )
    return {
        "model_id": seen_row["model_id"],
        "seed": seen_row["seed"],
        "seen_experiment_id": seen_row["experiment_id"],
        "unseen_experiment_id": unseen_row["experiment_id"],
        "seen_threshold": seen_row["threshold"],
        "unseen_threshold": unseen_row["threshold"],
        "seen_fp": seen_row["fp"],
        "unseen_fp": unseen_row["fp"],
        "seen_minus_unseen_fp": int(seen_row["fp"]) - int(unseen_row["fp"]),
        "seen_fn": seen_row["fn"],
        "unseen_fn": unseen_row["fn"],
        "seen_minus_unseen_fn": int(seen_row["fn"]) - int(unseen_row["fn"]),
        "seen_precision": seen_row["precision"],
        "unseen_precision": unseen_row["precision"],
        "unseen_minus_seen_precision": float(unseen_row["precision"])
        - float(seen_row["precision"]),
        "seen_recall": seen_row["recall"],
        "unseen_recall": unseen_row["recall"],
        "unseen_minus_seen_recall": float(unseen_row["recall"])
        - float(seen_row["recall"]),
        "seen_f1": seen_row["f1"],
        "unseen_f1": unseen_row["f1"],
        "unseen_minus_seen_f1": float(unseen_row["f1"]) - float(seen_row["f1"]),
    }


def _split_summary_row(
    split_label: str,
    split: str,
    rows: list[Mapping[str, Any]],
) -> dict[str, Any]:
    if not rows:
        raise SeenUnseenDifficultyError(f"No joined rows for {split}")
    predictions = [row["prediction"] for row in rows]
    y_true = [int(prediction["y_true"]) for prediction in predictions]
    y_pred = [int(prediction["y_pred"]) for prediction in predictions]
    confusion = binary_confusion_matrix(y_true, y_pred)
    precision = precision_score(confusion)
    recall = recall_score(confusion)
    f1 = f1_score(precision, recall)
    positive_rows = [row for row in rows if row["prediction"]["y_true"] == 1]
    negative_rows = [row for row in rows if row["prediction"]["y_true"] == 0]
    false_positive_rows = [row for row in rows if row["group"] == "false_positive"]
    threshold = float(predictions[0]["threshold"])
    near_threshold_rows = _near_threshold_rows(rows, threshold)
    negative_near_threshold_rows = _near_threshold_rows(negative_rows, threshold)
    fp_hard_count = _count_hard_negatives(false_positive_rows)
    return {
        "split_label": split_label,
        "split": split,
        "experiment_id": predictions[0]["experiment_id"],
        "model_id": predictions[0]["model_id"],
        "seed": predictions[0]["seed"],
        "threshold": threshold,
        "row_count": len(rows),
        "positive_count": len(positive_rows),
        "negative_count": len(negative_rows),
        "hard_negative_count": _count_hard_negatives(rows),
        "hard_negative_negative_count": _count_hard_negatives(negative_rows),
        "predicted_positive_count": sum(y_pred),
        "tp": confusion["tp"],
        "fp": confusion["fp"],
        "tn": confusion["tn"],
        "fn": confusion["fn"],
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": _safe_divide(confusion["fp"], len(negative_rows)),
        "false_negative_rate": _safe_divide(confusion["fn"], len(positive_rows)),
        "false_positive_hard_negative_count": fp_hard_count,
        "false_positive_hard_negative_rate": _safe_divide(
            fp_hard_count, len(false_positive_rows)
        ),
        "positive_score_mean": _score_stat(positive_rows, "mean"),
        "positive_score_std": _score_stat(positive_rows, "std"),
        "negative_score_mean": _score_stat(negative_rows, "mean"),
        "negative_score_std": _score_stat(negative_rows, "std"),
        "near_threshold_count": len(near_threshold_rows),
        "near_threshold_rate": _safe_divide(len(near_threshold_rows), len(rows)),
        "negative_near_threshold_count": len(negative_near_threshold_rows),
        "negative_near_threshold_rate": _safe_divide(
            len(negative_near_threshold_rows), len(negative_rows)
        ),
    }


def _feature_group_rows(
    split_label: str,
    split: str,
    rows: list[Mapping[str, Any]],
    feature_columns: list[str],
) -> list[dict[str, Any]]:
    groups = {
        "positive": [row for row in rows if row["prediction"]["y_true"] == 1],
        "negative": [row for row in rows if row["prediction"]["y_true"] == 0],
        "true_positive": [row for row in rows if row["group"] == "true_positive"],
        "false_positive": [row for row in rows if row["group"] == "false_positive"],
        "true_negative": [row for row in rows if row["group"] == "true_negative"],
        "false_negative": [row for row in rows if row["group"] == "false_negative"],
    }
    output = []
    for group_name, group_rows in groups.items():
        output_row: dict[str, Any] = {
            "split_label": split_label,
            "split": split,
            "group": group_name,
            "row_count": len(group_rows),
        }
        for feature in feature_columns:
            output_row[feature] = _feature_mean(group_rows, feature)
        output.append(output_row)
    return output


def _load_feature_lookup(path: str | Path) -> dict[str, dict[str, float]]:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or "pair_id" not in reader.fieldnames:
            raise SeenUnseenDifficultyError(f"Feature table missing pair_id column: {path}")
        lookup: dict[str, dict[str, float]] = {}
        for row in reader:
            lookup[str(row["pair_id"])] = {
                key: float(value)
                for key, value in row.items()
                if key not in {"dataset_id", "split", "pair_id", "label"}
            }
    return lookup


def _score_stat(rows: list[Mapping[str, Any]], stat: str) -> float | None:
    if not rows:
        return None
    scores = [float(row["prediction"]["score"]) for row in rows]
    if stat == "mean":
        return mean(scores)
    if stat == "std":
        return pstdev(scores)
    raise SeenUnseenDifficultyError(f"Unknown score stat: {stat}")


def _feature_mean(rows: list[Mapping[str, Any]], feature: str) -> float | None:
    values = [
        float(row["features"][feature])
        for row in rows
        if feature in row["features"]
    ]
    return mean(values) if values else None


def _near_threshold_rows(
    rows: Iterable[Mapping[str, Any]], threshold: float, window: float = 0.05
) -> list[Mapping[str, Any]]:
    return [
        row
        for row in rows
        if abs(float(row["prediction"]["score"]) - threshold) <= window
    ]


def _count_hard_negatives(rows: Iterable[Mapping[str, Any]]) -> int:
    return sum(1 for row in rows if _pair(row).is_hard_negative is True)


def _pair(row: Mapping[str, Any]) -> PairRecord:
    return row["pair"]


def _row_by_label(rows: list[Mapping[str, Any]], split_label: str) -> Mapping[str, Any]:
    matches = [row for row in rows if row["split_label"] == split_label]
    if len(matches) != 1:
        raise SeenUnseenDifficultyError(f"Expected one row for split_label={split_label}")
    return matches[0]


def _safe_divide(numerator: int | float, denominator: int | float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _safe_float(value: Any) -> float:
    if value is None:
        return 0.0
    return float(value)


def _write_csv(
    rows: list[Mapping[str, Any]],
    output_path: str | Path,
    fieldnames: list[str],
) -> int:
    if not rows:
        raise SeenUnseenDifficultyError("At least one row is required")
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def _format_float(value: float) -> str:
    return f"{value:.6f}"


def _format_optional_float(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.6f}"
