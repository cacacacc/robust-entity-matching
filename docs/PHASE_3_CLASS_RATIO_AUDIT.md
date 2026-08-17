# Phase 3 Class-Ratio Stress-Test Audit

Date: 2026-08-16

## Scope

This audit covers the approved class-ratio stress-test run:

- Config: `configs/experiments/wdc_class_ratio_stress_fit.json`
- Aggregate summary: `results/summaries/wdc_class_ratio_stress_fit_v1/aggregate.json`
- Prediction root: `results/predictions/wdc_class_ratio_stress_fit_v1/`

## Protocol

- Dataset: WDC Products `80pair`.
- Train split: `train_small`.
- Validation split: `valid_small`.
- Test split: `test_unseen_100un`.
- Class ratios: `1:1`, `1:2`, `1:3`, `1:4`.
- Models: `logistic_regression`, `random_forest`, `svm`.
- Seeds: `13`, `29`, `47`, `71`, `101`.
- Threshold selection: F1 on validation only.
- Test policy: final evaluation only; no test-set threshold or model selection.

## Artifact Counts

- Seed-level tasks: 60.
- Raw prediction files: 120.
- Summary files: 61.
- Saved model artifacts: none.
- Sampled training tables written to disk: none.

## Audit Command

```powershell
python scripts/audit_class_ratio_results.py
```

## Audit Result

```text
audit_status: passed
experiment_id: wdc_class_ratio_stress_fit_v1
ratio_count: 4
seed_audit_count: 60
```

## Result Export

```powershell
python scripts/export_class_ratio_results.py
```

Generated reports:

- `reports/class_ratio_results.csv`
- `reports/class_ratio_results.md`

## Top-Level Finding

Random Forest is the strongest model across the class-ratio grid by mean test F1. Its best ratio is `1:4`, but `1:2` is close and has higher mean recall.

Top rows by test F1 mean:

| Rank | Ratio | Model | Test F1 Mean | Precision Mean | Recall Mean |
|---:|---|---|---:|---:|---:|
| 1 | `1:4` | `random_forest` | `0.5598631874163362` | `0.46980980732376343` | `0.6952` |
| 2 | `1:2` | `random_forest` | `0.5575836592034913` | `0.45914399589697374` | `0.7124` |
| 3 | `1:3` | `random_forest` | `0.5499925921651603` | `0.45354502356487514` | `0.704` |

## Interpretation Limits

- These results are valid for the current WDC `80pair` feature set and traditional baselines only.
- Validation is used for threshold selection, but `train_small` and `valid_small` have known entity overlap, so this is not a fully three-way entity-disjoint protocol.
- The unseen-entity claim remains attached to `test_unseen_100un`, which is entity-disjoint from both development splits.
- The run should not be interpreted as final model selection until class-ratio result diagnostics and any planned reporting metrics are finalized.
