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

## 2026-08-15: Pause local schema download until explicit user approval

Decision: Do not download even small public dataset files until the user explicitly approves data download for Phase 1 schema audit.

Alternatives considered:

- Treat "continue" as implicit permission to download small files.
- Use workarounds to download files through another path.
- Proceed with only official page-level information.

Reasoning: The project instructions previously said not to download data. Although the intended files are small and public, data download changes the local data state and should be authorized clearly.

Impact: The current audit can document official page-level schema information, but cannot lock data contracts or dataset selection until actual files are inspected.

Evidence available at decision time: An attempted download of a 107KB CompERBench `abt-buy` label file was rejected by the approval system because explicit permission to download data had not been given.

## 2026-08-15: Select WDC Products 80pair and CompERBench abt-buy as initial MVP datasets

Decision: Use WDC Products `80pair` as the primary MVP dataset and CompERBench `abt-buy` as the secondary small benchmark.

Alternatives considered:

- Use only WDC Products.
- Use `abt-buy` as if it supported unseen-entity evaluation.
- Delay all dataset selection until auditing `amazon-google` or `products (Walmart-Amazon)`.

Reasoning: WDC Products `80pair` directly supports label, pair ID, cluster ID, hard-negative flag, and official seen/unseen variants. CompERBench `abt-buy` is tiny and useful for early ingestion, class-ratio tests, and baseline smoke tests, but local inspection shows it is not pair-disjoint or entity-disjoint under the official split.

Impact: WDC Products should carry the main unseen-entity and hard-negative claims. `abt-buy` should support early pipeline validation and class-ratio experiments, not unseen-entity claims.

Evidence available at decision time: WDC `80pair` local inspection confirmed JSON fields `id_left`, `id_right`, `cluster_id_left`, `cluster_id_right`, `pair_id`, `label`, and `is_hard_negative`. `abt-buy` local inspection found `source_id`, `target_id`, and `matching`, with 5,010 train pairs, 1,439 validation pairs, and 710 test pairs, but also 3 duplicate pairs across official splits and substantial source/target ID overlap.

## 2026-08-15: Use JSON dataset configs as Phase 2 ingestion inputs

Decision: Store initial dataset metadata in JSON files under `configs/datasets/`.

Alternatives considered:

- YAML configs.
- Python constants.
- Hard-coded paths inside loader functions.

Reasoning: JSON can be read with the Python standard library and avoids adding dependencies before the environment is settled. Keeping paths, schema, label mappings, audited counts, and limitations in config files prevents hard-coded data assumptions from spreading through ingestion code.

Impact: Phase 2 ingestion code should load dataset metadata from `configs/datasets/*.json` and validate raw files against those configs.

Evidence available at decision time: The project has no Python environment or dependency lock yet, and AGENTS.md requires paths and hyperparameters to live in configuration files rather than being hard-coded.
