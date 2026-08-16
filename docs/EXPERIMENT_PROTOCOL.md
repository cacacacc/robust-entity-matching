# Experiment Protocol

Status: Draft overall. The first WDC unseen baseline split and threshold protocol is locked as protocol-only, with model fitting still disabled.

## Audit-Derived Constraints

The Phase 1 literature and dataset audit establishes the following draft constraints:

- Report both matching and non-matching pair counts for every split and ratio.
- Select classification thresholds on the validation set only.
- Keep test sets fixed after protocol decisions are locked.
- Separate pair-random evaluation from entity-disjoint or unseen-entity evaluation.
- Do not claim entity-disjoint evaluation unless reliable entity identifiers or clusters are available.
- Define hard-negative sampling from training data only; do not tune the rule using test results.

## Datasets

To be selected after literature and dataset audit.

Current strong candidates:

- WDC Products pair-wise benchmark.
- CompERBench tasks such as `abt-buy`, `amazon-google`, or `products (Walmart-Amazon)`.

Large WDC LSPM corpus files are out of scope for the initial MVP download.

Dataset choice is provisionally selected but not protocol-locked.
Schema inspection update:

- WDC Products `80pair` is suitable as the primary MVP dataset.
- CompERBench `abt-buy` is suitable as a secondary small benchmark and smoke-test dataset.
- `abt-buy` official split is not pair-disjoint and not entity-disjoint, so it must not be used for unseen-entity claims.

Initial dataset configuration files:

- `configs/datasets/wdc_products_80pair.json`
- `configs/datasets/comperbench_abt_buy.json`

These configs record local paths, source URLs, schema fields, label mappings, audited counts, supported research questions, and known limitations. They are inputs for Phase 2 ingestion code, not final locked experiment configs.

Initial ingestion validation exists and confirms that both configs match the currently downloaded raw audit files.

Standardized in-memory pair-table contract:

- `dataset_id`: dataset identifier.
- `split`: logical split name.
- `pair_id`: unique pair identifier.
- `left_record_id` and `right_record_id`: source record IDs.
- `left_entity_id` and `right_entity_id`: entity IDs when available, otherwise `None`.
- `label`: integer class label where `1` means match and `0` means non-match.
- `left_attributes` and `right_attributes`: dictionaries containing source-specific text and structured attributes.
- `is_hard_negative`: boolean when provided by the dataset, otherwise `None`.

This representation exists in memory and can now be exported as interim JSONL. No final processed feature tables are generated yet.

Interim export schema:

- Schema version: `pair_table_v1`.
- File format: UTF-8 JSON Lines.
- Output directory: `data/interim/<dataset_id>/<split>.jsonl`.
- Each line contains the standardized pair-table fields plus `schema_version`.
- Interim files are generated artifacts and are ignored by Git.
- Interim files must be regenerated from raw data and dataset configs; they must not be manually edited.

Data quality checks currently include:

- label counts;
- hard-negative counts when available;
- missing attribute counts;
- duplicate pair IDs within each split;
- pair ID overlap across splits;
- record ID overlap across splits;
- entity ID overlap across splits when entity IDs are available.

Important current findings:

- WDC Products `test_unseen_100un` has zero pair, record, and entity overlap with `train_small` and `valid_small`.
- WDC Products `test_mixed_050un` overlaps with train/validation by design and must be interpreted as a mixed official benchmark variant.
- CompERBench `abt-buy` official splits contain duplicate pair IDs within some splits and pair/record overlap across splits, so they must not be used for strict leakage-free or unseen-entity claims.

## Splits

Planned split protocols:

- Pair-random split.
- Entity-disjoint split.

Exact train, validation, and test proportions are not locked yet.

WDC Products may be evaluated using its official seen, half-seen, and unseen benchmark splits. CompERBench tasks require further schema inspection before deciding whether entity-disjoint splits are possible.

Do not claim CompERBench supports entity-disjoint splitting until actual record/entity fields have been inspected.

Local inspection found duplicate pairs and substantial source/target ID overlap across `abt-buy` official train/validation/test splits. Therefore `abt-buy` should be treated as a fixed-split baseline dataset only unless a custom split is later designed and validated.

First WDC unseen baseline protocol:

- Config: `configs/experiments/wdc_unseen_baseline_protocol.json`.
- Train split: `train_small`.
- Validation split: `valid_small`.
- Final test split: `test_unseen_100un`.
- Train/validation rule: require pair and record disjointness; acknowledge known entity overlap and do not claim train-validation entity disjointness.
- Development/test rule: require pair, record, and entity disjointness for `train_small` versus `test_unseen_100un` and for `valid_small` versus `test_unseen_100un`.

## Random Seeds

Initial locked seed schedule for the first WDC unseen baseline protocol:

- `13`
- `29`
- `47`
- `71`
- `101`

These seeds apply to model initialization and sampling decisions once fitting is explicitly enabled.

## Features

Planned feature families:

- String similarity features.
- Attribute agreement features.
- Numeric-token or structured-field comparison features where applicable.

Exact feature list is not locked yet.

Feature candidates from the literature audit include edit distance, Jaro, Jaro-Winkler, Jaccard, token overlap, numeric-token agreement, TF-IDF cosine similarity, and attribute agreement features.

Text standardization currently exists as a preprocessing primitive, not as a final feature table:

- Version: `text_standardization_v1`.
- Missing values such as empty strings, `N/A`, `NULL`, and `None` are normalized to empty strings.
- Text is HTML-unescaped, Unicode-normalized with NFKC, lowercased, stripped, and whitespace-collapsed.
- Tokens are lowercase alphanumeric chunks.
- Numeric tokens are extracted separately for later numeric agreement features.
- Standardized profiles are generated in memory from interim pair payloads and are not yet written as processed feature artifacts.

Initial string-similarity features currently exist as primitives, not as a full feature table:

- Version: `string_similarity_v1`.
- Combined-text features:
  - `combined_exact_match`;
  - `combined_edit_similarity`;
  - `combined_token_jaccard`;
  - `combined_numeric_overlap`.
- Attribute-level features use shared base attribute names, stripping dataset-side suffixes such as `_left` and `_right`.
- Feature names are normalized to snake_case, for example `priceCurrency` becomes `price_currency`.
- Exact match returns `1.0` only when both normalized values are non-empty and equal. Two missing values are not treated as a positive match signal.
- Numeric-token overlap uses containment-style overlap: intersection size divided by the smaller non-empty numeric-token set.
- Edit similarity is bounded to the first 64 normalized characters for computational feasibility with the pure-Python implementation. Long descriptions should be interpreted mainly through token and numeric-overlap features.

Processed feature-table schema:

- Version: `feature_table_v1`.
- File format: CSV.
- Output directory: `data/processed/<dataset_id>/<split>.csv`.
- Metadata columns:
  - `dataset_id`;
  - `split`;
  - `pair_id`;
  - `label`.
- Feature columns are numeric values in `[0.0, 1.0]`.
- Each CSV has a sibling summary file: `data/processed/<dataset_id>/<split>.summary.json`.
- Summary files record schema version, text standardization version, feature version, row count, label counts, and feature column names.
- Processed feature tables are generated artifacts and are ignored by Git.
- Processed feature tables must be regenerated from interim JSONL, not manually edited.

## Split Guards

Before model training, selected feature-table splits must pass explicit model-readiness checks.

Current split guard report includes:

- feature-table CSV and summary JSON validation;
- consistent feature columns across selected splits;
- within-split duplicate pair IDs;
- cross-split pair ID overlap;
- cross-split record ID overlap;
- cross-split entity ID overlap when entity IDs are available.

Current guard findings:

- WDC Products `train_small` and `test_unseen_100un` have zero pair, record, and entity overlap.
- WDC Products `valid_small` and `test_unseen_100un` have zero pair, record, and entity overlap.
- WDC Products `train_small` and `valid_small` have 500 overlapping entity IDs, so the official small train/validation/test trio must not be described as fully three-way entity-disjoint.
- CompERBench `abt-buy` train has duplicate pair IDs, and its train/test comparison has pair and record overlap.
- `abt-buy` lacks reliable entity IDs in the current config, so strict entity-disjoint checks are unavailable and must fail closed when required.

Guard commands:

```powershell
python scripts/check_split_guards.py configs/datasets/wdc_products_80pair.json --splits train_small test_unseen_100un --require-record-disjoint --require-entity-disjoint
python scripts/check_split_guards.py configs/datasets/comperbench_abt_buy.json --splits train test --report-only
```

## Model-Ready Matrix Loading

Model-ready matrices can be loaded only after feature-table validation and split guards.

Current matrix contract:

- `X`: list of numeric feature vectors.
- `y`: list of integer labels where `1` means match and `0` means non-match.
- `pair_ids`: row-aligned pair identifiers for traceability and error analysis.
- `feature_columns`: ordered feature names used to build every vector.
- `label_counts`: split-level label counts copied from validated summaries.
- `guard_report`: the split guard report used before loading the bundle.

Current restrictions:

- Matrix loading does not fit, train, tune, or evaluate any model.
- Strict unseen loading should require pair, record, and entity disjoint checks.
- Non-strict diagnostic loading is allowed only when explicitly requested, for example for `abt-buy` smoke checks.
- Baseline model families are recorded in `configs/models/baseline_traditional.json` as planned models only.

## Baseline Dry-Run Protocol

The first baseline protocol currently exists only as a dry-run config:

- Config: `configs/experiments/wdc_unseen_baseline_dry_run.json`.
- Status: `dry_run_only`.
- Dataset: WDC Products `80pair`.
- Selected splits:
  - train: `train_small`;
  - test: `test_unseen_100un`;
  - validation: `null`.
- Required guards:
  - pair-disjoint;
  - record-disjoint;
  - entity-disjoint.
- Planned first model family: `logistic_regression`.

This config is intentionally not fit-ready because validation and threshold-selection protocol is not locked yet. It may be used to verify dependencies, split guards, feature columns, matrix shape, label counts, and model config status.

Current local dependency status from dry-run:

- `sklearn`: available;
- `numpy`: available;
- `pandas`: available.

Availability does not imply permission to train. Fitting remains blocked until the protocol explicitly allows it.

## Baseline Protocol Validation

The first protocol-only config now validates the experimental roles without fitting:

- Config: `configs/experiments/wdc_unseen_baseline_protocol.json`.
- Status: `protocol_locked_no_fit`.
- Fit allowed: `false`.
- Threshold selection split: validation only.
- Threshold selection metric: F1.
- Candidate threshold grid: `0.00` to `1.00` in steps of `0.01`.
- Test split cannot be used for threshold selection.
- Test split cannot be used for model selection.
- Test results should be reported once per seed after validation decisions are fixed.

Guard validation command:

```powershell
python scripts/validate_experiment_protocol.py configs/experiments/wdc_unseen_baseline_protocol.json
```

Current validated guard facts:

- `train_small` versus `valid_small`: zero pair overlap, zero record overlap, 500 entity overlap.
- `train_small` versus `test_unseen_100un`: zero pair, record, and entity overlap.
- `valid_small` versus `test_unseen_100un`: zero pair, record, and entity overlap.

Interpretation: `valid_small` can be used for threshold selection, but it must not be described as an entity-disjoint validation split. The final unseen-entity claim is attached only to `test_unseen_100un`.

## Models

Planned traditional baselines:

- Logistic Regression.
- Random Forest.
- SVM.

Initial model factory support exists for:

- `logistic_regression`: sklearn `LogisticRegression`, `class_weight="balanced"`, `solver="liblinear"`, `max_iter=1000`.
- `random_forest`: sklearn `RandomForestClassifier`, `n_estimators=100`, `class_weight="balanced"`, `n_jobs=1`, seed injected by runner.
- `svm`: sklearn `SVC`, linear kernel, `class_weight="balanced"`, `probability=true`, seed injected by runner.

These estimators can be instantiated but must not be fitted unless an experiment config explicitly sets `fit_allowed: true`.

Current model config:

- `configs/models/baseline_traditional.json`

Current training guard:

- Dry-run experiment config `configs/experiments/wdc_unseen_baseline_dry_run.json` is rejected by the training guard because `fit_allowed` is `false`.

Hyperparameters are initial scaffolding values, not final tuned settings.

## Threshold Selection

Thresholds must be selected on the validation set only. The test set must be used only for final evaluation.

Current threshold-selection scaffold:

- Version: `threshold_selection_v1`.
- Function: `select_threshold_on_validation`.
- Current selection metric: F1 only.
- Threshold selection refuses any split name other than `validation`.
- Default candidate thresholds are `0.00` through `1.00` in steps of `0.01`.
- No project model scores exist yet, so this scaffold has only been tested with toy scores.

For the first WDC unseen baseline protocol, threshold selection is locked to:

- split role: `validation`;
- concrete split: `valid_small`;
- metric: F1;
- candidate thresholds: `0.00` to `1.00` with step `0.01`.

## Metrics

Planned metrics:

- Precision.
- Recall.
- F1.
- PR-AUC.
- Confusion matrix.
- Runtime.
- Mean and standard deviation across seeds.

Current implemented metric primitives:

- Version: `binary_metrics_v1`.
- `apply_threshold`: converts scores in `[0.0, 1.0]` to binary predictions.
- `binary_confusion_matrix`: reports `tp`, `fp`, `tn`, and `fn` for positive class `1`.
- `precision_score`.
- `recall_score`.
- `f1_score`.
- `evaluate_binary_scores`: returns threshold, class counts, confusion matrix, precision, recall, and F1.

Not implemented yet:

- PR-AUC;
- calibration metrics;
- runtime measurement;
- mean and standard deviation across seeds;
- saved prediction files.

Metric code currently uses toy scores only. It must not be reported as experimental performance.

## Fair Comparison Rules

All models compared in the same experiment must use the same data split, features, evaluation protocol, and random seed schedule.
