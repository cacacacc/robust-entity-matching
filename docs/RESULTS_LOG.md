# Results Log

## 2026-08-16: First Approved Logistic Regression Baseline

Experiment config:

- `configs/experiments/wdc_unseen_logistic_regression_fit.json`

Protocol:

- Dataset: WDC Products `80pair`.
- Train split: `train_small`.
- Validation split: `valid_small`.
- Test split: `test_unseen_100un`.
- Model: `logistic_regression`.
- Seeds: `13`, `29`, `47`, `71`, `101`.
- Threshold selection: F1 on validation only.
- Test policy: final evaluation only; no threshold or model selection on test.

Class ratios:

- Train: 500 match, 2000 non-match.
- Validation: 500 match, 2000 non-match.
- Test: 500 match, 4000 non-match.

Leakage notes:

- `train_small` versus `valid_small`: 0 pair overlap, 0 record overlap, 500 entity overlap.
- `train_small` versus `test_unseen_100un`: 0 pair, record, and entity overlap.
- `valid_small` versus `test_unseen_100un`: 0 pair, record, and entity overlap.
- Interpretation: validation is a development split for threshold selection, not evidence of train-validation entity-disjoint generalization. The unseen-entity claim is attached to `test_unseen_100un`.

Aggregate test results:

- Selected thresholds: `0.66`, `0.66`, `0.66`, `0.66`, `0.66`.
- Test precision mean: `0.45582047685834504`.
- Test precision std: `0.0`.
- Test recall mean: `0.65`.
- Test recall std: `0.0`.
- Test F1 mean: `0.5358615004122012`.
- Test F1 std: `0.0`.

Per-seed test confusion matrix:

- `tp`: 325.
- `fp`: 388.
- `tn`: 3612.
- `fn`: 175.

Artifacts:

- Aggregate summary: `results/summaries/wdc_unseen_logistic_regression_fit_v1/aggregate.json`.
- Per-seed summaries: `results/summaries/wdc_unseen_logistic_regression_fit_v1/logistic_regression/seed_<seed>.json`.
- Raw validation predictions: `results/predictions/wdc_unseen_logistic_regression_fit_v1/logistic_regression/seed_<seed>/validation.csv`.
- Raw test predictions: `results/predictions/wdc_unseen_logistic_regression_fit_v1/logistic_regression/seed_<seed>/test.csv`.

Artifact status:

- Result artifacts are generated locally and ignored by Git.
- No model pickle or joblib artifact was saved.
- Random Forest and SVM were run later under the same locked protocol; see the next result entry.

Audit status:

- Result audit passed on 2026-08-16.
- Audit document: `docs/PHASE_3_LOGISTIC_REGRESSION_AUDIT.md`.
- Audit command: `python scripts/audit_baseline_results.py results/summaries/wdc_unseen_logistic_regression_fit_v1/aggregate.json`.

## 2026-08-16: Random Forest and SVM Baselines

Experiment config:

- `configs/experiments/wdc_unseen_rf_svm_fit.json`

Protocol:

- Dataset: WDC Products `80pair`.
- Train split: `train_small`.
- Validation split: `valid_small`.
- Test split: `test_unseen_100un`.
- Models: `random_forest`, `svm`.
- Seeds: `13`, `29`, `47`, `71`, `101`.
- Threshold selection: F1 on validation only.
- Test policy: final evaluation only; no threshold or model selection on test.

Aggregate test results:

| Model | Precision Mean | Precision Std | Recall Mean | Recall Std | F1 Mean | F1 Std |
|---|---:|---:|---:|---:|---:|---:|
| `random_forest` | `0.46980980732376343` | `0.019139505455088784` | `0.6952` | `0.033184333653095976` | `0.5598631874163362` | `0.0030943756168219064` |
| `svm` | `0.43678721061618153` | `0.004334086700824968` | `0.6724` | `0.0035777087639996667` | `0.5295473051367368` | `0.0023275127069483487` |

Selected thresholds:

- `random_forest`: `0.32`, `0.37`, `0.4`, `0.38`, `0.33`.
- `svm`: `0.31`, `0.34`, `0.32`, `0.34`, `0.34`.

Artifacts:

- Aggregate summary: `results/summaries/wdc_unseen_rf_svm_fit_v1/aggregate.json`.
- Raw predictions: `results/predictions/wdc_unseen_rf_svm_fit_v1/<model_id>/seed_<seed>/`.

Audit status:

- Result audit passed on 2026-08-16.
- Audit document: `docs/PHASE_3_RF_SVM_AUDIT.md`.
- Audit command: `python scripts/audit_baseline_results.py results/summaries/wdc_unseen_rf_svm_fit_v1/aggregate.json`.

## 2026-08-16: Initial Traditional Baseline Comparison

Comparison artifacts:

- `reports/baseline_comparison.csv`
- `reports/baseline_comparison.md`

Export command:

```powershell
python scripts/export_baseline_comparison.py
```

Ranked by test F1 mean:

| Rank | Model | Test F1 Mean | Test F1 Std | Precision Mean | Recall Mean |
|---:|---|---:|---:|---:|---:|
| 1 | `random_forest` | `0.5598631874163362` | `0.0030943756168219064` | `0.46980980732376343` | `0.6952` |
| 2 | `logistic_regression` | `0.5358615004122012` | `0.0` | `0.45582047685834504` | `0.65` |
| 3 | `svm` | `0.5295473051367368` | `0.0023275127069483487` | `0.43678721061618153` | `0.6724` |

Interpretation:

- Random Forest is the strongest of the three initial traditional baselines under the locked WDC unseen protocol.
- All three models still have modest precision, so false-positive analysis remains important.
- This comparison ranks by selected-threshold F1 only; threshold-free diagnostics are reported in a later section.

## 2026-08-16: Random Forest False-Positive / False-Negative Analysis

Analyzed artifact:

- `results/predictions/wdc_unseen_rf_svm_fit_v1/random_forest/seed_13/test.csv`

Why seed 13:

- Seed `13` is the first seed in the locked seed list.
- It was used for descriptive qualitative analysis only.
- It was not selected because of test-set performance.

Generated local artifacts:

- `results/error_analysis/wdc_unseen_rf_svm_fit_v1/random_forest/seed_13_test_error_analysis.json`
- `results/error_analysis/wdc_unseen_rf_svm_fit_v1/random_forest/seed_13_test_error_analysis.md`

Artifact policy:

- Detailed error-analysis files are ignored by Git because they include raw product attributes.
- Tracked documents record only aggregate statistics and non-sensitive interpretation.

Confusion counts:

| Type | Count |
|---|---:|
| `true_positive` | `369` |
| `false_positive` | `454` |
| `true_negative` | `3546` |
| `false_negative` | `131` |

Key aggregate observations:

- `453 / 454` false positives are official WDC hard negatives, so most false alarms come from intentionally difficult non-match pairs.
- False positives have much higher title numeric overlap than true negatives: `0.701951` versus `0.096236`.
- False positives also have higher combined numeric overlap than true negatives: `0.515029` versus `0.117180`.
- False negatives have lower combined numeric overlap than true positives: `0.301851` versus `0.616304`.
- Under the selected threshold `0.32`, false-negative scores are low on average (`0.176107`) and never exceed `0.31`, while false-positive scores average `0.515683`.

Interpretation:

- Random Forest is mostly fooled by hard negatives that share product-like numeric or title signals with true matches.
- Missed true matches tend to have weaker surface similarity under the current string-similarity feature set.
- The next useful modeling question is whether better attribute-specific features, calibrated thresholds, or hard-negative-aware training improve precision without collapsing recall.

## 2026-08-16: Threshold Diagnostics and Average Precision

Diagnostic artifacts:

- `reports/threshold_diagnostics.csv`
- `reports/threshold_diagnostics.md`

Export command:

```powershell
python scripts/export_threshold_diagnostics.py
```

Purpose:

- F1 reports one operating point after validation-selected thresholding.
- Average Precision summarizes score-ranking quality across all possible operating points.
- Threshold-grid PR-AUC is reported as a coarse 0.00-1.00 grid diagnostic, not as the primary selection metric.

Ranked by test Average Precision mean:

| Rank | Model | Test AP Mean | Test AP Std | Test Grid PR-AUC Mean | F1 Mean @ Selected Threshold |
|---:|---|---:|---:|---:|---:|
| 1 | `random_forest` | `0.5063211072497819` | `0.004498085430516401` | `0.5056520070147552` | `0.5598631874163362` |
| 2 | `svm` | `0.49828342310310664` | `0.00002717614840984437` | `0.49724205769911434` | `0.5295473051367368` |
| 3 | `logistic_regression` | `0.46672395541280387` | `0.0` | `0.46562353144268254` | `0.5358615004122012` |

Interpretation:

- Random Forest remains first when evaluated by threshold-free ranking quality.
- SVM ranks above Logistic Regression by Average Precision even though Logistic Regression has slightly higher selected-threshold F1.
- This difference is useful: selected-threshold F1 measures one validation-chosen operating point, while Average Precision asks whether positive pairs are ranked above negative pairs across the score range.
- These diagnostics use test predictions only for post-run reporting, not for threshold or model selection.
