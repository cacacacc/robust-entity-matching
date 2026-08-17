# Phase 3 Train/Test Ratio Grid Audit

Date: 2026-08-17

## Scope

This audit covers the approved full train/test class-ratio grid:

- Config: `configs/experiments/wdc_train_test_ratio_grid_fit.json`
- Experiment ID: `wdc_train_test_ratio_grid_fit_v1`
- Source protocol: `configs/experiments/wdc_train_test_ratio_grid_protocol.json`
- Dataset: WDC Products `80pair`
- Train split: `train_small`
- Validation split: `valid_small`
- Test source split: `test_unseen_100un`
- Models: `logistic_regression`, `random_forest`, `svm`
- Seeds: `13`, `29`, `47`, `71`, `101`

## Grid

Train ratios:

- `1:1`
- `1:2`
- `1:3`
- `1:4`

Test ratios:

- `1:1`
- `1:2`
- `1:3`
- `1:4`

Execution scale:

- Optimized model fits: `60`
- Test evaluations: `240`
- Grid cells: `48`

## Protocol

- Training positives: all 500 available match pairs from `train_small`.
- Training negatives: seeded without-replacement samples from `train_small`.
- Test positives: all 500 available match pairs from `test_unseen_100un`.
- Test negatives: seeded without-replacement samples from `test_unseen_100un`.
- Validation remains fixed as `valid_small`.
- Thresholds are selected on validation only.
- Test predictions are used only for final reporting and audit.

## Artifacts

- Aggregate summary: `results/summaries/wdc_train_test_ratio_grid_fit_v1/aggregate.json`
- Raw predictions: `results/predictions/wdc_train_test_ratio_grid_fit_v1/<train_ratio_id>/<test_ratio_id>/<model_id>/seed_<seed>/`
- Result CSV: `reports/train_test_ratio_grid_results.csv`
- Result Markdown: `reports/train_test_ratio_grid_results.md`

Artifact counts:

- Seed-level evaluation summaries: `240`
- Aggregate summary files: `1`
- Total summary files: `241`
- Raw prediction files: `480`
- Saved model artifacts: none
- Sampled train/test tables written to disk: none

## Audit Command

```powershell
python scripts/audit_train_test_ratio_grid_results.py
```

Audit result:

- `audit_status`: `passed`
- `seed_audit_count`: `240`
- `cell_audit_count`: `48`

## Top Results

Ranked by mean test F1:

| Rank | Train Ratio | Test Ratio | Model | Test F1 Mean | Test F1 Std | Precision Mean | Recall Mean |
|---:|---|---|---|---:|---:|---:|---:|
| 1 | `1:1` | `1:1` | `random_forest` | `0.782462` | `0.008184` | `0.856289` | `0.721600` |
| 2 | `1:2` | `1:1` | `random_forest` | `0.781625` | `0.017060` | `0.866799` | `0.712400` |
| 3 | `1:3` | `1:1` | `random_forest` | `0.774576` | `0.018622` | `0.864387` | `0.704000` |
| 4 | `1:4` | `1:1` | `random_forest` | `0.773159` | `0.018689` | `0.872117` | `0.695200` |
| 5 | `1:3` | `1:1` | `logistic_regression` | `0.760369` | `0.011325` | `0.844245` | `0.692000` |

## Interpretation

The top-ranked rows all use test ratio `1:1`, which is the easiest evaluation distribution in this grid because it has the fewest non-match pairs. This confirms that F1 and precision are highly sensitive to the test class ratio.

The grid should be analyzed in two ways:

- Within a fixed test ratio, compare train ratios to estimate training-distribution effects.
- Within a fixed train ratio, compare test ratios to estimate evaluation-distribution effects.

The full grid is diagnostic. It does not replace the fixed-test `1:8` unseen evaluation when the research question is about robustness under the original WDC unseen test distribution.
