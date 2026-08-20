# Robust Entity Matching under Class Imbalance and Unseen-Entity Shift

This repository contains a reproducible machine-learning research project on entity matching under class imbalance and unseen-entity distribution shift.

The project studies how traditional entity-matching baselines behave when evaluation protocols control class ratio, entity overlap, negative sampling, validation-only threshold selection, and random seeds.

## Research Questions

RQ1: How do different match-to-non-match ratios in the training and test sets affect precision, recall, F1 score, and Average Precision diagnostics for traditional entity-matching classifiers?

RQ2: How do official seen and unseen entity splits differ under a controlled traditional-baseline protocol?

RQ3: How do hard negatives and false positives affect interpretation under unseen-entity evaluation?

## Completed MVP Scope

- WDC Products `80pair` as the primary public entity-matching dataset.
- CompERBench `abt-buy` as a secondary audited dataset for pipeline validation, not for unseen-entity claims.
- Data ingestion, inspection, cleaning, schema validation, and split-leakage checks.
- Pairwise string and attribute similarity features.
- Logistic Regression, Random Forest, and SVM baselines.
- Train, validation, and test separation.
- Validation-set threshold selection.
- Entity-disjoint unseen evaluation on WDC Products `test_unseen_100un`.
- Official WDC seen/unseen diagnostic comparison.
- Training and evaluation class-ratio stress tests.
- Five random seeds for main experiments.
- Precision, recall, F1, Average Precision diagnostics, confusion matrices, means, and standard deviations.
- Error analysis, reproducible commands, saved configurations, saved raw predictions, audits, and result synthesis.

## Repository Layout

```text
robust-entity-matching/
|-- configs/              # Dataset, model, and experiment configurations
|-- data/                 # Local data folders; contents are not committed
|-- docs/                 # Research notes, decisions, protocols, and audits
|-- notebooks/            # Exploratory analysis only
|-- scripts/              # Reproducible command-line entry points
|-- src/entity_matching/  # Project Python package
|-- tests/                # Automated tests
|-- results/              # Generated result files; contents are not committed
|-- figures/              # Generated figures; contents are not committed
`-- reports/              # Result tables and report-ready drafts
```

## Key Results

- Random Forest is the strongest current traditional baseline under the fixed WDC unseen protocol.
- Training class ratio has measurable but limited effects when the unseen test distribution is fixed.
- Evaluation class ratio has a strong effect on F1 and precision.
- The official WDC seen diagnostic split scores lower than the unseen split in this setup because it produces more false positives across all inspected model-seed rows.
- Final claims must report class ratios, split construction, threshold-selection protocol, seeds, and leakage/entity-overlap caveats.

Primary synthesis files:

- `docs/PHASE_3_RESULTS_SYNTHESIS.md`
- `docs/PROJECT_COMPLETION_AUDIT.md`
- `reports/final_results_narrative.md`

## Reproducibility Rules

- Raw data must be preserved unchanged.
- Test sets must not be used for feature, model, threshold, hyperparameter, or sampling decisions.
- Every experimental result must be traceable to a command, configuration, data version, and Git commit.
- Failed or abnormal runs must be recorded rather than silently deleted.
- Claims in the final report must distinguish prior literature, project results, reasonable interpretation, and unverified hypotheses.

## Quick Verification

```powershell
python -m unittest discover tests
```

Generated raw predictions and detailed summaries live under ignored `results/` paths and are not committed. Compact result tables and report drafts live under `reports/`.
