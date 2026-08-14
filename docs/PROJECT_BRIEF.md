# Project Brief

## Motivation

Entity matching, also called record linkage or entity resolution, decides whether two records from possibly different sources refer to the same real-world entity. This project studies how robust traditional machine-learning entity-matching models are under class imbalance and unseen-entity distribution shift.

## Research Questions

RQ1: How do different match-to-non-match ratios in the training and test sets affect precision, recall, F1 score, PR-AUC, and calibration of traditional entity-matching classifiers?

RQ2: How much performance difference exists between pair-random evaluation and entity-disjoint evaluation, particularly on previously unseen entities?

RQ3: Does hard-negative sampling improve unseen-entity generalization compared with random negative sampling, and what types of errors does it reduce or introduce?

## MVP

- Use at least two public entity-matching datasets.
- Build reproducible ingestion, cleaning, feature, split, sampling, training, and evaluation pipelines.
- Compare Logistic Regression, Random Forest, and SVM.
- Evaluate class ratios, entity-disjoint generalization, random negative sampling, and hard-negative sampling.
- Report metrics across at least five random seeds.
- Complete error analysis and project documentation.

## Optional Extensions

Optional extensions include blocking, candidate generation, calibration analysis, larger WDC experiments, and Transformer baselines. These are out of scope until the MVP is reproducible.

## Non-Goals

This project will not build a production web application, wrap the work in an LLM/RAG system, chase only the highest F1 score, change test sets based on results, or fabricate novelty beyond the evidence.

## Success Criteria

The project is successful only if its main claims are backed by reproducible experiments, saved configurations, saved results, tests, and clear documentation.

