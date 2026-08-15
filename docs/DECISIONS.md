# Decisions

## 2026-08-14: Initialize a public-ready research repository structure

Decision: Use a conventional Python research project layout with separate folders for configuration, source code, tests, documentation, local data, generated results, figures, and reports.

Alternatives considered:

- Put scripts and notebooks at the repository root.
- Delay documentation until experiments are complete.
- Track raw data and generated results directly in Git.

Reasoning: The selected layout keeps code, data, generated artifacts, and research documentation separate. This supports reproducibility and reduces the risk of committing large data or derived results accidentally.

Impact: Future experiments should be run through scripts or modules, with configurations and outputs stored in predictable locations.

Evidence available at decision time: Project requirements require reproducible commands, saved configurations, raw results, documentation, and scientific integrity checks.

## 2026-08-14: Keep Phase 0 focused on project definition and environment verification

Decision: Phase 0 will explain the problem, review research questions, define MVP boundaries, verify local tools, and validate repository structure. It will not download datasets, install large dependencies, train models, or push additional changes to GitHub.

Alternatives considered:

- Start dataset download immediately.
- Begin model implementation before auditing datasets.
- Add Transformer baselines early.

Reasoning: The project depends on dataset labels, entity identifiers, and split feasibility. Coding experiments before auditing these facts would increase the risk of leakage, unfair comparison, or wasted implementation.

Impact: Phase 1 must begin with literature and dataset audit. Dataset selection will be based on verified fields, labels, entity identifiers, size, and license.

Evidence available at decision time: The research questions require controlled class ratios, entity-disjoint splits, and negative sampling comparisons. These cannot be validated without first checking dataset structure.

## 2026-08-15: Prioritize WDC Products and CompERBench for Phase 1 dataset inspection

Decision: Treat WDC Products pair-wise benchmark and selected CompERBench tasks as the first dataset candidates to inspect for the MVP. Do not download WDC LSPM full corpus at this stage.

Alternatives considered:

- Download WDC LSPM full corpus immediately.
- Use only WDC Products for all MVP experiments.
- Use only small classic datasets such as `abt-buy` and `amazon-google`.

Reasoning: WDC Products directly supports unseen-entity and hard-negative dimensions, while CompERBench provides small fixed train/validation/test entity matching tasks suitable for traditional baselines and class-ratio experiments. WDC LSPM full files are GB-scale and unnecessary before schema needs are confirmed.

Impact: The next milestone should inspect small benchmark/sample files before final dataset selection. The project should not claim that CompERBench supports entity-disjoint splitting until its record/entity fields are checked locally.

Evidence available at decision time: WDC Products official page lists `cluster_id`, `label`, `pair_id`, `is_hard_negative`, and unseen-related benchmark dimensions. CompERBench official page lists many small entity matching tasks with train/validation/test sets, records, and feature vectors.
