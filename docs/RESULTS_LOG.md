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

## 2026-08-16: Class-Ratio Stress-Test Plan

This is a protocol and run-plan entry, not an experiment result.

Config:

- `configs/experiments/wdc_class_ratio_stress_protocol.json`

Plan artifacts:

- `reports/class_ratio_plan.csv`
- `reports/class_ratio_plan.md`

Export command:

```powershell
python scripts/export_class_ratio_plan.py
```

Planned training ratios:

| Ratio | Match Count | Non-Match Count | Total Train Rows |
|---|---:|---:|---:|
| `1:1` | `500` | `500` | `1000` |
| `1:2` | `500` | `1000` | `1500` |
| `1:3` | `500` | `1500` | `2000` |
| `1:4` | `500` | `2000` | `2500` |

Protocol notes:

- Validation remains `valid_small`.
- Test remains `test_unseen_100un`.
- Negative sampling is without replacement and seeded by the experiment seed.
- The plan writes no sampled training tables and runs no model fitting.

Training guard check:

```powershell
python scripts/check_class_ratio_training_guard.py --model logistic_regression
```

Guard result:

- `ready_to_execute_training`: `false`.
- `training_attempted`: `false`.
- `writes_files_now`: `false`.
- `blocker_error_type`: `TrainingNotAllowedError`.
- Ratios covered by the guard check: `1:1`, `1:2`, `1:3`, `1:4`.

Sampled matrix implementation:

- `build_sampled_training_matrix` now constructs in-memory class-ratio training matrices.
- Ratio `1:3` produces 500 match rows and 1500 non-match rows, for 2000 total training rows.
- Feature columns are preserved from the original `train_small` matrix.
- No sampled matrices are written to disk in this milestone.

Runner implementation status:

- `run_approved_class_ratio_training` has been implemented as a guarded execution path.
- CLI entry point: `scripts/run_approved_class_ratio.py`.
- The current protocol config still has `fit_allowed: false`, so the runner refuses it before training.
- No class-ratio training run has been executed.

Execution manifest:

- `reports/class_ratio_execution_manifest.csv`
- `reports/class_ratio_execution_manifest.md`

Manifest summary:

- Total planned tasks: `60`.
- Ratios: `4`.
- Models: `3`.
- Seeds: `5`.
- Current `fit_allowed`: `false`.
- Current `writes_files_now`: `false`.

## 2026-08-16: Approved Class-Ratio Stress-Test Run

Experiment config:

- `configs/experiments/wdc_class_ratio_stress_fit.json`

Protocol:

- Dataset: WDC Products `80pair`.
- Train split: `train_small`.
- Validation split: `valid_small`.
- Test split: `test_unseen_100un`.
- Ratios: `1:1`, `1:2`, `1:3`, `1:4`.
- Models: `logistic_regression`, `random_forest`, `svm`.
- Seeds: `13`, `29`, `47`, `71`, `101`.
- Threshold selection: F1 on validation only.
- Test policy: final evaluation only; no threshold or model selection on test.

Run artifacts:

- Aggregate summary: `results/summaries/wdc_class_ratio_stress_fit_v1/aggregate.json`.
- Raw predictions: `results/predictions/wdc_class_ratio_stress_fit_v1/<ratio_id>/<model_id>/seed_<seed>/`.
- Result table: `reports/class_ratio_results.csv`.
- Result report: `reports/class_ratio_results.md`.

Artifact counts:

- Seed-level tasks: `60`.
- Raw prediction files: `120`.
- Summary files: `61`.
- Saved model artifacts: none.
- Sampled training tables written to disk: none.

Audit status:

- Result audit passed on 2026-08-16.
- Audit document: `docs/PHASE_3_CLASS_RATIO_AUDIT.md`.
- Audit command: `python scripts/audit_class_ratio_results.py`.

Ranked by test F1 mean:

| Rank | Ratio | Model | Test F1 Mean | Test F1 Std | Precision Mean | Recall Mean |
|---:|---|---|---:|---:|---:|---:|
| 1 | `1:4` | `random_forest` | `0.5598631874163362` | `0.0030943756168219064` | `0.46980980732376343` | `0.6952` |
| 2 | `1:2` | `random_forest` | `0.5575836592034913` | `0.009708686691557344` | `0.45914399589697374` | `0.7124` |
| 3 | `1:3` | `random_forest` | `0.5499925921651603` | `0.006856716098050768` | `0.45354502356487514` | `0.704` |
| 4 | `1:1` | `random_forest` | `0.5464659600876338` | `0.013328935929894674` | `0.4410039920985321` | `0.7216` |
| 5 | `1:4` | `logistic_regression` | `0.5358615004122012` | `0.0` | `0.45582047685834504` | `0.65` |

Interpretation:

- Random Forest remains the strongest model family across all tested class ratios.
- The full `1:4` training ratio has the highest mean test F1.
- The `1:2` Random Forest result is close to `1:4` and has higher recall, so the class-ratio effect should be discussed as a precision/recall tradeoff rather than a simple winner-takes-all result.
- Logistic Regression and SVM are less sensitive than Random Forest in this grid, but neither exceeds the best Random Forest settings.

## 2026-08-16: Approved Matched Train/Test Class-Ratio Run

Experiment config:

- `configs/experiments/wdc_class_ratio_matched_train_test_fit.json`

Protocol:

- Dataset: WDC Products `80pair`.
- Train split: `train_small`.
- Validation split: `valid_small`.
- Test source split: `test_unseen_100un`.
- Ratios: `1:1`, `1:2`, `1:3`, `1:4`.
- Models: `logistic_regression`, `random_forest`, `svm`.
- Seeds: `13`, `29`, `47`, `71`, `101`.
- Threshold selection: F1 on fixed validation only.
- Test policy: sample test negatives from `test_unseen_100un` so each test matrix matches the corresponding training ratio.
- Test policy guard: no threshold or model selection on test.

Matched train/test label counts:

| Ratio | Train Matches | Train Non-Matches | Test Matches | Test Non-Matches |
|---|---:|---:|---:|---:|
| `1:1` | `500` | `500` | `500` | `500` |
| `1:2` | `500` | `1000` | `500` | `1000` |
| `1:3` | `500` | `1500` | `500` | `1500` |
| `1:4` | `500` | `2000` | `500` | `2000` |

Run artifacts:

- Aggregate summary: `results/summaries/wdc_class_ratio_matched_train_test_fit_v1/aggregate.json`.
- Raw predictions: `results/predictions/wdc_class_ratio_matched_train_test_fit_v1/<ratio_id>/<model_id>/seed_<seed>/`.
- Result table: `reports/class_ratio_matched_train_test_results.csv`.
- Result report: `reports/class_ratio_matched_train_test_results.md`.

Artifact counts:

- Seed-level tasks: `60`.
- Raw prediction files: `120`.
- Summary files: `61`.
- Saved model artifacts: none.
- Sampled training or test tables written to disk: none.

Audit status:

- Result audit passed on 2026-08-16.
- Audit document: `docs/PHASE_3_MATCHED_CLASS_RATIO_AUDIT.md`.
- Audit command: `python scripts/audit_class_ratio_results.py results/summaries/wdc_class_ratio_matched_train_test_fit_v1/aggregate.json`.

Ranked by test F1 mean:

| Rank | Ratio | Model | Test F1 Mean | Test F1 Std | Precision Mean | Recall Mean |
|---:|---|---|---:|---:|---:|---:|
| 1 | `1:1` | `random_forest` | `0.782462373906762` | `0.00818373819607886` | `0.856289230514715` | `0.7216` |
| 2 | `1:1` | `logistic_regression` | `0.7554748564676588` | `0.013287682521376598` | `0.8537796825882654` | `0.6776` |
| 3 | `1:1` | `svm` | `0.7547528711728942` | `0.011150080501331292` | `0.8572362469543349` | `0.6744` |
| 4 | `1:2` | `random_forest` | `0.740234825430515` | `0.014246747517319528` | `0.7714291604070446` | `0.7124` |
| 5 | `1:2` | `svm` | `0.7119659069872102` | `0.005597415246050505` | `0.7453024431039434` | `0.682` |

Interpretation:

- This run confirms that the previous implementation controlled only the training ratio; this matched variant now controls both training and test ratios.
- Matched evaluation produces higher F1, especially at `1:1`, because the test distribution contains fewer non-match candidates than the original fixed `test_unseen_100un` distribution.
- The matched result is useful for distribution-shift diagnostics, but it should not replace the fixed-test result when the goal is to compare training ratios under one stable unseen-entity test distribution.

## 2026-08-17: Fixed-Test vs Matched Train/Test Protocol Comparison

Comparison artifacts:

- `reports/class_ratio_protocol_comparison.csv`
- `reports/class_ratio_protocol_comparison.md`

Export command:

```powershell
python scripts/export_class_ratio_protocol_comparison.py
```

Purpose:

- Compare the original fixed-test class-ratio run against the matched train/test class-ratio run.
- Make the evaluation-distribution change explicit instead of ranking both protocols in one mixed leaderboard.

Key comparison:

| Ratio | Model | Fixed F1 | Matched F1 | Delta F1 | Fixed Precision | Matched Precision | Fixed Recall | Matched Recall |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `1:1` | `random_forest` | `0.546466` | `0.782462` | `+0.235996` | `0.441004` | `0.856289` | `0.721600` | `0.721600` |
| `1:1` | `logistic_regression` | `0.522357` | `0.755475` | `+0.233117` | `0.425679` | `0.853780` | `0.677600` | `0.677600` |
| `1:1` | `svm` | `0.528704` | `0.754753` | `+0.226048` | `0.434862` | `0.857236` | `0.674400` | `0.674400` |
| `1:2` | `random_forest` | `0.557584` | `0.740235` | `+0.182651` | `0.459144` | `0.771429` | `0.712400` | `0.712400` |
| `1:4` | `random_forest` | `0.559863` | `0.666114` | `+0.106251` | `0.469810` | `0.640845` | `0.695200` | `0.695200` |

Interpretation:

- Matched train/test F1 is higher mostly because matched evaluation reduces the number of test non-matches.
- Recall is unchanged in this comparison because matched evaluation keeps all positive test pairs and samples only negative test pairs.
- The fixed-test protocol remains the main evidence for the training class-ratio research question.
- The matched train/test protocol should be framed as an evaluation-distribution diagnostic.

## 2026-08-17: Train/Test Ratio Grid Plan

This is a protocol and dry-manifest entry, not an experiment result.

Config:

- `configs/experiments/wdc_train_test_ratio_grid_protocol.json`

Planned grid:

- Train ratios: `1:1`, `1:2`, `1:3`, `1:4`.
- Test ratios: `1:1`, `1:2`, `1:3`, `1:4`.
- Models: `logistic_regression`, `random_forest`, `svm`.
- Seeds: `13`, `29`, `47`, `71`, `101`.

Generated dry manifest:

- `reports/train_test_ratio_grid_manifest.csv`
- `reports/train_test_ratio_grid_manifest.md`

Export command:

```powershell
python scripts/export_train_test_ratio_grid_manifest.py
```

Guard command:

```powershell
python scripts/check_train_test_ratio_grid_training_guard.py
```

Guard result:

- `ready_to_execute_training`: `false`.
- `training_attempted`: `false`.
- `writes_files_now`: `false`.
- `planned_fit_count`: `60`.
- `planned_test_evaluation_count`: `240`.
- `blocker_error_type`: `TrainingNotAllowedError`.

Interpretation:

- This grid separates train-ratio effects from test-ratio effects.
- The previous matched train/test run corresponds only to the diagonal cells of this grid.
- The previous fixed-test run used the original `test_unseen_100un` ratio of `1:8`, which is outside this grid.
- No model fitting or prediction writing has been performed for this grid yet.

## 2026-08-17: Approved Train/Test Ratio Grid Run

Experiment config:

- `configs/experiments/wdc_train_test_ratio_grid_fit.json`

Protocol:

- Dataset: WDC Products `80pair`.
- Train split: `train_small`.
- Validation split: `valid_small`.
- Test source split: `test_unseen_100un`.
- Train ratios: `1:1`, `1:2`, `1:3`, `1:4`.
- Test ratios: `1:1`, `1:2`, `1:3`, `1:4`.
- Models: `logistic_regression`, `random_forest`, `svm`.
- Seeds: `13`, `29`, `47`, `71`, `101`.
- Threshold selection: F1 on fixed validation only.
- Test policy: seeded negative sampling from `test_unseen_100un`; no threshold or model selection on test.

Run artifacts:

- Aggregate summary: `results/summaries/wdc_train_test_ratio_grid_fit_v1/aggregate.json`.
- Raw predictions: `results/predictions/wdc_train_test_ratio_grid_fit_v1/<train_ratio_id>/<test_ratio_id>/<model_id>/seed_<seed>/`.
- Result table: `reports/train_test_ratio_grid_results.csv`.
- Result report: `reports/train_test_ratio_grid_results.md`.

Artifact counts:

- Optimized model fits: `60`.
- Test evaluations: `240`.
- Grid cells: `48`.
- Summary files: `241`.
- Raw prediction files: `480`.
- Saved model artifacts: none.
- Sampled train/test tables written to disk: none.

Audit status:

- Result audit passed on 2026-08-17.
- Audit document: `docs/PHASE_3_TRAIN_TEST_RATIO_GRID_AUDIT.md`.
- Audit command: `python scripts/audit_train_test_ratio_grid_results.py`.

Ranked by test F1 mean:

| Rank | Train Ratio | Test Ratio | Model | Test F1 Mean | Test F1 Std | Precision Mean | Recall Mean |
|---:|---|---|---|---:|---:|---:|---:|
| 1 | `1:1` | `1:1` | `random_forest` | `0.782462373906762` | `0.00818373819607886` | `0.856289230514715` | `0.7216` |
| 2 | `1:2` | `1:1` | `random_forest` | `0.7816254770056504` | `0.0170599457917226` | `0.8667990137905008` | `0.7124` |
| 3 | `1:3` | `1:1` | `random_forest` | `0.7745758299748362` | `0.018622490157339754` | `0.8643869578052571` | `0.704` |
| 4 | `1:4` | `1:1` | `random_forest` | `0.7731589143679595` | `0.018688677657508618` | `0.872117006111584` | `0.6952` |
| 5 | `1:3` | `1:1` | `logistic_regression` | `0.7603687781576559` | `0.0113245201458222` | `0.8442445709855957` | `0.692` |

Interpretation:

- The strongest rows all use test ratio `1:1`, showing that precision and F1 are strongly affected by evaluation class ratio.
- Random Forest remains the strongest model family in the top cells.
- Within fixed test ratio `1:1`, Random Forest changes only slightly across train ratios, with `1:1` first and `1:2` very close.
- This grid is diagnostic for train/test distribution effects. The fixed-test `1:8` run remains the main evidence for the original WDC unseen test distribution.

## 2026-08-17: Train/Test Ratio Grid Derived Analysis

Analysis artifacts:

- `reports/train_test_ratio_grid_f1_matrix.csv`
- `reports/train_test_ratio_grid_best_train_by_test_ratio.csv`
- `reports/train_test_ratio_grid_test_sensitivity.csv`
- `reports/train_test_ratio_grid_analysis.md`

Export command:

```powershell
python scripts/export_train_test_ratio_grid_analysis.py
```

Purpose:

- Hold test ratio fixed to compare train-ratio effects.
- Hold train ratio fixed to compare test-ratio effects.
- Convert the 48-row grid leaderboard into analysis tables that support research interpretation.

Key findings:

- Best-train gaps under a fixed test ratio are small, often below `0.005` F1.
- Test-ratio effects are much larger: moving from test `1:1` to test `1:4` drops F1 by roughly `0.11` to `0.12` for many settings.
- The F1 drop is driven by precision drop; recall drop is `0.0` because every sampled test ratio keeps all positive test pairs.

Interpretation:

- Training class ratio matters, but the current grid shows weaker effects than evaluation class ratio.
- The grid is strongest as evidence that class-ratio reporting must include the evaluation ratio.
- The final report should not claim a universal best training ratio from this grid alone.

## 2026-08-20: Seen vs Unseen Baseline Comparison

Seen experiment config:

- `configs/experiments/wdc_seen_baseline_fit.json`

Unseen reference summaries:

- `results/summaries/wdc_unseen_logistic_regression_fit_v1/aggregate.json`
- `results/summaries/wdc_unseen_rf_svm_fit_v1/aggregate.json`

Comparison artifacts:

- `reports/seen_vs_unseen_comparison.csv`
- `reports/seen_vs_unseen_comparison.md`

Export command:

```powershell
python scripts/export_seen_unseen_comparison.py
```

Protocol:

- Train split: `train_small`.
- Validation split: `valid_small`.
- Seen test split: `test_seen_000un`.
- Unseen test split: `test_unseen_100un`.
- Models: `logistic_regression`, `random_forest`, `svm`.
- Seeds: `13`, `29`, `47`, `71`, `101`.
- Threshold selection: F1 on fixed validation only.

Split notes:

- `train_small` vs `test_seen_000un`: 0 pair overlap, 0 record overlap, 500 entity overlap.
- `valid_small` vs `test_seen_000un`: 0 pair overlap, 4 record overlap, 500 entity overlap.
- Seen test is an official diagnostic split, not a leakage-free final evaluation.

Audit status:

- Seen result audit passed on 2026-08-20.
- Audit document: `docs/PHASE_3_SEEN_VS_UNSEEN_AUDIT.md`.
- Audit command: `python scripts/audit_baseline_results.py results/summaries/wdc_seen_baseline_fit_v1/aggregate.json`.

Comparison:

| Model | Seen F1 | Unseen F1 | Unseen - Seen F1 | Seen Precision | Unseen Precision | Seen Recall | Unseen Recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| `random_forest` | `0.501588765037883` | `0.5598631874163362` | `0.05827442237845326` | `0.40099776227906103` | `0.46980980732376343` | `0.6724` | `0.6952` |
| `logistic_regression` | `0.48769230769230765` | `0.5358615004122012` | `0.048169192719893505` | `0.39625` | `0.45582047685834504` | `0.634` | `0.65` |
| `svm` | `0.48292754986528125` | `0.5295473051367368` | `0.04661975527145551` | `0.38424599865908854` | `0.43678721061618153` | `0.65` | `0.6724` |

Interpretation:

- In this audited run, unseen test scores are higher than seen test scores for all three traditional baselines.
- This should be reported as an empirical WDC split finding, not forced into an unseen-harder assumption.
- The unseen split remains the main entity-disjoint robustness split; the seen split is useful as an official diagnostic with known overlap caveats.

## 2026-08-20: Seen/Unseen Split Difficulty Analysis

Purpose:

- Explain why `test_seen_000un` scored lower than `test_unseen_100un`.
- Use existing raw predictions and processed feature tables only.
- Do not retrain models and do not use test data for model selection.

Command:

```powershell
python scripts/export_seen_unseen_difficulty_analysis.py
```

Artifacts:

- `reports/seen_unseen_split_difficulty.csv`
- `reports/seen_unseen_feature_difficulty.csv`
- `reports/seen_unseen_difficulty_analysis.md`
- `docs/PHASE_3_SEEN_UNSEEN_DIFFICULTY_ANALYSIS.md`

Inspected run:

- Model: `random_forest`
- Seed: `13`
- Seen prediction: `results/predictions/wdc_seen_baseline_fit_v1/random_forest/seed_13/test.csv`
- Unseen prediction: `results/predictions/wdc_unseen_rf_svm_fit_v1/random_forest/seed_13/test.csv`

Key descriptive findings:

| Split | Positives | Negatives | Hard Negatives | TP | FP | TN | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `test_seen_000un` | `500` | `4000` | `3000` | `350` | `589` | `3411` | `150` | `0.372737` | `0.700000` | `0.486449` |
| `test_unseen_100un` | `500` | `4000` | `3000` | `369` | `454` | `3546` | `131` | `0.448360` | `0.738000` | `0.557823` |

Interpretation:

- The two test splits have identical label counts and hard-negative totals.
- The seen split produces more false positives and slightly more false negatives under the inspected RF seed.
- Feature summaries show that seen negatives have higher numeric overlap than unseen negatives, while seen positives have lower title/combined textual similarity than unseen positives.
- Therefore, the lower seen F1 appears to be a split-composition/error-profile effect, not evidence that entity-seen tests are inherently harder or easier.

All-seed stability extension:

- Script: `python scripts/export_seen_unseen_error_profile.py`
- Seed-level output: `reports/seen_unseen_error_profile_by_seed.csv`
- Model-level output: `reports/seen_unseen_error_profile_by_model.csv`
- Markdown output: `reports/seen_unseen_error_profile.md`

Model-level summary:

| Model | Seeds | Seen FP Mean | Unseen FP Mean | Seen-Unseen FP Mean | Seeds Seen FP Higher | Unseen-Seen Precision Mean | Unseen-Seen F1 Mean | Seeds Unseen F1 Higher |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `logistic_regression` | `5` | `483.000000` | `388.000000` | `95.000000` | `5` | `0.059570` | `0.048169` | `5` |
| `random_forest` | `5` | `505.600000` | `394.400000` | `111.200000` | `5` | `0.068812` | `0.058274` | `5` |
| `svm` | `5` | `521.000000` | `433.600000` | `87.400000` | `5` | `0.052541` | `0.046620` | `5` |

Updated interpretation:

- The seen-lower pattern is stable across all inspected model-seed rows.
- All `15/15` rows have more false positives on seen than unseen.
- All `15/15` rows have higher F1 on unseen than seen.
- This strengthens the descriptive claim that the seen diagnostic split is harder for these baselines under the current validation-selected thresholds.
