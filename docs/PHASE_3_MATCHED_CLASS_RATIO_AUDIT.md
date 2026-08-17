# Phase 3 Matched Train/Test Class-Ratio Audit

Date: 2026-08-16

## Scope

This audit covers the approved matched train/test class-ratio run:

- Config: `configs/experiments/wdc_class_ratio_matched_train_test_fit.json`
- Experiment ID: `wdc_class_ratio_matched_train_test_fit_v1`
- Dataset: WDC Products `80pair`
- Train split: `train_small`
- Validation split: `valid_small`
- Test source split: `test_unseen_100un`
- Models: `logistic_regression`, `random_forest`, `svm`
- Seeds: `13`, `29`, `47`, `71`, `101`

## Protocol

This run differs from the first class-ratio stress test:

- Training negatives are sampled to create ratios `1:1`, `1:2`, `1:3`, and `1:4`.
- Test negatives are also sampled from `test_unseen_100un` so each test matrix has the same match/non-match ratio as the corresponding training matrix.
- Validation remains fixed as `valid_small`.
- Thresholds are selected on validation only.
- Test predictions are used only for final reporting and audit.

This run answers a diagnostic distribution question. It should not replace the fixed-test class-ratio result when the research question is about robustness under a stable unseen-entity test distribution.

## Label Counts

| Ratio | Train Matches | Train Non-Matches | Test Matches | Test Non-Matches |
|---|---:|---:|---:|---:|
| `1:1` | `500` | `500` | `500` | `500` |
| `1:2` | `500` | `1000` | `500` | `1000` |
| `1:3` | `500` | `1500` | `500` | `1500` |
| `1:4` | `500` | `2000` | `500` | `2000` |

## Artifacts

- Aggregate summary: `results/summaries/wdc_class_ratio_matched_train_test_fit_v1/aggregate.json`
- Raw predictions: `results/predictions/wdc_class_ratio_matched_train_test_fit_v1/<ratio_id>/<model_id>/seed_<seed>/`
- Result CSV: `reports/class_ratio_matched_train_test_results.csv`
- Result Markdown: `reports/class_ratio_matched_train_test_results.md`

Artifact counts:

- Seed-level tasks: `60`
- Raw prediction files: `120`
- Summary files: `61`
- Saved model artifacts: none
- Sampled training or test tables written to disk: none

## Audit Command

```powershell
python scripts/audit_class_ratio_results.py results/summaries/wdc_class_ratio_matched_train_test_fit_v1/aggregate.json
```

Audit result:

- `audit_status`: `passed`
- `ratio_count`: `4`
- `seed_audit_count`: `60`

## Top Results

Ranked by mean test F1:

| Rank | Ratio | Model | Test F1 Mean | Test F1 Std | Precision Mean | Recall Mean |
|---:|---|---|---:|---:|---:|---:|
| 1 | `1:1` | `random_forest` | `0.782462` | `0.008184` | `0.856289` | `0.721600` |
| 2 | `1:1` | `logistic_regression` | `0.755475` | `0.013288` | `0.853780` | `0.677600` |
| 3 | `1:1` | `svm` | `0.754753` | `0.011150` | `0.857236` | `0.674400` |
| 4 | `1:2` | `random_forest` | `0.740235` | `0.014247` | `0.771429` | `0.712400` |
| 5 | `1:2` | `svm` | `0.711966` | `0.005597` | `0.745302` | `0.682000` |

## Interpretation

The matched train/test run produces much higher F1 scores than the fixed-test class-ratio run because the test distribution becomes less imbalanced for `1:1`, `1:2`, and `1:3`. This is expected: precision usually improves when the evaluation set contains fewer non-match candidates.

The main scientific comparison should therefore keep two questions separate:

- Fixed-test protocol: how does training ratio affect performance on the same unseen-entity test distribution?
- Matched train/test protocol: how do models behave when deployment/evaluation class ratio changes together with training class ratio?

The strongest matched result is Random Forest at `1:1`, but this does not mean `1:1` is best under the original fixed unseen test distribution. Under the fixed-test run, Random Forest at `1:4` remained the top mean-F1 setting.
