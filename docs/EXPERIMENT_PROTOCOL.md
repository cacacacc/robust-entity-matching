# Experiment Protocol

Status: Draft. This protocol is not locked.

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

## Random Seeds

Planned minimum: five random seeds. Exact seed values are not locked yet.

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

## Models

Planned traditional baselines:

- Logistic Regression.
- Random Forest.
- SVM.

Hyperparameters are not locked yet.

## Threshold Selection

Thresholds must be selected on the validation set only. The test set must be used only for final evaluation.

## Metrics

Planned metrics:

- Precision.
- Recall.
- F1.
- PR-AUC.
- Confusion matrix.
- Runtime.
- Mean and standard deviation across seeds.

## Fair Comparison Rules

All models compared in the same experiment must use the same data split, features, evaluation protocol, and random seed schedule.
