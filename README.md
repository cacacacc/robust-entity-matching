# Robust Entity Matching under Class Imbalance and Unseen-Entity Shift

This repository contains a reproducible machine-learning research project on entity matching under class imbalance and unseen-entity distribution shift.

The project studies whether traditional machine-learning baselines can provide stable, interpretable, and fair comparisons for entity matching when evaluation protocols control class ratio, entity overlap, negative sampling, and random seeds.

## Research Questions

RQ1: How do different match-to-non-match ratios in the training and test sets affect precision, recall, F1 score, PR-AUC, and calibration of traditional entity-matching classifiers?

RQ2: How much performance difference exists between pair-random evaluation and entity-disjoint evaluation, particularly on previously unseen entities?

RQ3: Does hard-negative sampling improve unseen-entity generalization compared with random negative sampling, and what types of errors does it reduce or introduce?

## Minimum Scope

- At least two public entity-matching datasets.
- Data ingestion, inspection, cleaning, and schema validation.
- Pairwise string and attribute similarity features.
- Logistic Regression, Random Forest, and SVM baselines.
- Train, validation, and test separation.
- Validation-set threshold selection.
- Pair-random and entity-disjoint splits.
- Random negative sampling and hard-negative sampling.
- At least five random seeds.
- Precision, recall, F1, PR-AUC, confusion matrix, runtime, mean, and standard deviation.
- Error analysis, reproducible commands, saved configurations, and raw results.

## Repository Layout

```text
robust-entity-matching/
├── configs/              # Dataset, model, and experiment configurations
├── data/                 # Local data folders; contents are not committed
├── docs/                 # Research notes, decisions, protocol, and learning materials
├── notebooks/            # Exploratory analysis only
├── scripts/              # Reproducible command-line entry points
├── src/entity_matching/  # Project Python package
├── tests/                # Automated tests
├── results/              # Generated result files; contents are not committed
├── figures/              # Generated figures; contents are not committed
└── reports/              # Technical report drafts and final exports
```

## Reproducibility Rules

- Raw data must be preserved unchanged.
- Test sets must not be used for feature, model, threshold, hyperparameter, or sampling decisions.
- Every experimental result must be traceable to a command, configuration, data version, and Git commit.
- Failed or abnormal runs must be recorded rather than silently deleted.
- Claims in the final report must distinguish prior literature, project results, reasonable interpretation, and unverified hypotheses.

## Current Status

Phase 0 is in progress: repository setup and project definition.

