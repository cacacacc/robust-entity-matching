# Phase 3 Logistic Regression Result Audit

Date: 2026-08-16

## Scope

This audit checks the first approved Logistic Regression baseline:

- Experiment: `wdc_unseen_logistic_regression_fit_v1`
- Config: `configs/experiments/wdc_unseen_logistic_regression_fit.json`
- Aggregate summary: `results/summaries/wdc_unseen_logistic_regression_fit_v1/aggregate.json`
- Raw predictions: `results/predictions/wdc_unseen_logistic_regression_fit_v1/logistic_regression/seed_<seed>/`

The audit does not train new models and does not change prediction files.

## Checks Performed

- Raw prediction CSV schema matches `raw_predictions_v1`.
- Validation prediction files contain 2500 rows per seed.
- Test prediction files contain 4500 rows per seed.
- Every row uses the stored selected threshold `0.66`.
- Validation rows use `split_role=validation`.
- Test rows use `split_role=test`.
- Per-seed validation metrics recompute from raw prediction scores.
- Per-seed test metrics recompute from raw prediction scores.
- Aggregate mean and standard deviation recompute from per-seed test metrics.

## Audit Result

Status: passed.

Command:

```powershell
python scripts/audit_baseline_results.py results/summaries/wdc_unseen_logistic_regression_fit_v1/aggregate.json
```

Unit test:

```powershell
python -m unittest tests.test_result_audit
```

## Recomputed Aggregate Metrics

- Test precision mean: `0.45582047685834504`
- Test precision std: `0.0`
- Test recall mean: `0.65`
- Test recall std: `0.0`
- Test F1 mean: `0.5358615004122012`
- Test F1 std: `0.0`

## Interpretation

The saved aggregate summary is consistent with the raw prediction files. This means the first Logistic Regression result is internally reproducible from saved row-level predictions.

The result should still be interpreted narrowly:

- It is only one traditional baseline family.
- It uses simple string-similarity features.
- It does not include Random Forest, SVM, hard-negative sampling, class-ratio experiments, or PR-AUC.
- The validation split has known entity overlap with train and should be described only as a development split for threshold selection.
