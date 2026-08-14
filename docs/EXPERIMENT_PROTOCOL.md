# Experiment Protocol

Status: Draft. This protocol is not locked.

## Datasets

To be selected after literature and dataset audit.

## Splits

Planned split protocols:

- Pair-random split.
- Entity-disjoint split.

Exact train, validation, and test proportions are not locked yet.

## Random Seeds

Planned minimum: five random seeds. Exact seed values are not locked yet.

## Features

Planned feature families:

- String similarity features.
- Attribute agreement features.
- Numeric-token or structured-field comparison features where applicable.

Exact feature list is not locked yet.

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

