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

Dataset choice is still not locked because local schema inspection has not been completed.
Schema inspection update:

- WDC Products `80pair` is suitable as the primary MVP dataset.
- CompERBench `abt-buy` is suitable as a secondary small benchmark and smoke-test dataset.
- `abt-buy` official split is not pair-disjoint and not entity-disjoint, so it must not be used for unseen-entity claims.

Initial dataset configuration files:

- `configs/datasets/wdc_products_80pair.json`
- `configs/datasets/comperbench_abt_buy.json`

These configs record local paths, source URLs, schema fields, label mappings, audited counts, supported research questions, and known limitations. They are inputs for Phase 2 ingestion code, not final locked experiment configs.

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
