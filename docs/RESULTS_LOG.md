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
- Random Forest and SVM have not been run yet.
