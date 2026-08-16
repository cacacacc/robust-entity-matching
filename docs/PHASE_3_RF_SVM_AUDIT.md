# Phase 3 Random Forest and SVM Result Audit

Date: 2026-08-16

## Scope

This audit checks the approved Random Forest and SVM baseline run:

- Experiment: `wdc_unseen_rf_svm_fit_v1`
- Config: `configs/experiments/wdc_unseen_rf_svm_fit.json`
- Aggregate summary: `results/summaries/wdc_unseen_rf_svm_fit_v1/aggregate.json`
- Raw predictions: `results/predictions/wdc_unseen_rf_svm_fit_v1/<model_id>/seed_<seed>/`

The audit does not train new models and does not change prediction files.

## Checks Performed

- Raw prediction CSV schema matches `raw_predictions_v1`.
- Validation prediction files contain 2500 rows per seed.
- Test prediction files contain 4500 rows per seed.
- Stored thresholds match row-level prediction thresholds.
- Validation rows use `split_role=validation`.
- Test rows use `split_role=test`.
- Per-seed validation metrics recompute from raw prediction scores.
- Per-seed test metrics recompute from raw prediction scores.
- Aggregate mean and standard deviation recompute from per-seed test metrics.

## Audit Result

Status: passed.

Command:

```powershell
python scripts/audit_baseline_results.py results/summaries/wdc_unseen_rf_svm_fit_v1/aggregate.json
```

## Recomputed Aggregate Metrics

Random Forest:

- Test precision mean: `0.46980980732376343`
- Test precision std: `0.019139505455088784`
- Test recall mean: `0.6952`
- Test recall std: `0.033184333653095976`
- Test F1 mean: `0.5598631874163362`
- Test F1 std: `0.0030943756168219064`
- Selected thresholds: `0.32`, `0.37`, `0.4`, `0.38`, `0.33`

SVM:

- Test precision mean: `0.43678721061618153`
- Test precision std: `0.004334086700824968`
- Test recall mean: `0.6724`
- Test recall std: `0.0035777087639996667`
- Test F1 mean: `0.5295473051367368`
- Test F1 std: `0.0023275127069483487`
- Selected thresholds: `0.31`, `0.34`, `0.32`, `0.34`, `0.34`

## Interpretation

The saved aggregate summary is consistent with the raw prediction files. Random Forest has the highest mean test F1 among the three initial traditional baselines so far, but the difference is still based on this first feature set and this single locked WDC protocol.
