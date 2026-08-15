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

## Splits

Planned split protocols:

- Pair-random split.
- Entity-disjoint split.

Exact train, validation, and test proportions are not locked yet.

WDC Products may be evaluated using its official seen, half-seen, and unseen benchmark splits. CompERBench tasks require further schema inspection before deciding whether entity-disjoint splits are possible.

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
