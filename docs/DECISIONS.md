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

## 2026-08-15: Use Python standard library for initial ingestion validation

Decision: Implement the first ingestion validation helpers using the Python standard library only.

Alternatives considered:

- Use pandas immediately.
- Delay validation until a virtual environment is created.
- Validate schemas manually through shell commands only.

Reasoning: The first Phase 2 milestone only needs config parsing, CSV reading, JSONL-GZIP reading, field checks, and count checks. These are all possible with `json`, `csv`, and `gzip`, avoiding premature dependency setup.

Impact: The project can validate raw files and configs before choosing dependency versions. Pandas can still be introduced later for feature engineering and experiment pipelines if useful.

Evidence available at decision time: `python -m unittest tests.test_data_validation` passed, and both dataset audit scripts produced expected label counts.

## 2026-08-15: Support encoding fallback for CompERBench record files

Decision: Read CSV files with UTF-8 first, then fall back to `cp1252` and `latin-1` if decoding fails.

Alternatives considered:

- Force all raw CSV files to UTF-8.
- Manually edit raw records to UTF-8.
- Ignore record files and validate pair files only.

Reasoning: Raw data must remain unchanged. Local validation found that `abt-buy` record files contain non-UTF-8 characters, so ingestion must handle the original encoding rather than modifying the source files.

Impact: Data loading is more robust while preserving raw files. Future documentation should mention this encoding behavior when explaining ingestion.

Evidence available at decision time: The first validation run failed with `UnicodeDecodeError` on `1_abt.csv`; after adding fallback decoding, unit tests and audit scripts passed.

## 2026-08-15: Normalize raw pairs into an in-memory PairRecord contract

Decision: Convert WDC Products and CompERBench `abt-buy` raw rows into a shared `PairRecord` dataclass before downstream preprocessing and feature engineering.

Alternatives considered:

- Keep dataset-specific row formats throughout the pipeline.
- Immediately write standardized processed files to disk.
- Use pandas DataFrames as the first standardized representation.

Reasoning: A shared dataclass makes the expected fields explicit while keeping this milestone small. Keeping the representation in memory avoids creating processed data before data quality reporting and data contract details are stable.

Impact: Feature engineering and split checks can later consume one consistent pair format. Processed file writing remains a later Phase 2 step after quality reports are implemented.

Evidence available at decision time: `python -m unittest tests.test_data_validation` passed with six tests, and `scripts/preview_pair_table.py` produced valid examples for both WDC Products and `abt-buy`.

## 2026-08-15: Generate data quality reports before feature engineering

Decision: Add a data quality reporting step before implementing text normalization and pairwise similarity features.

Alternatives considered:

- Move directly to feature engineering.
- Only rely on manual schema audit notes.
- Wait until after model training to inspect missing values and overlaps.

Reasoning: Missing values, duplicate pairs, and split overlap directly affect feature validity and experimental fairness. Detecting them before feature engineering prevents hidden leakage and invalid assumptions.

Impact: Phase 2 now includes programmatic quality reports. Feature engineering must use these findings, especially missing brand/description in WDC and missing price in `abt-buy`.

Evidence available at decision time: Quality reports found WDC `test_unseen_100un` has zero entity overlap with train/validation, while WDC mixed variants and `abt-buy` official splits have overlap that must be interpreted carefully.

## 2026-08-15: Write normalized pair tables to ignored interim JSONL files

Decision: Export normalized `PairRecord` tables to `data/interim/<dataset_id>/<split>.jsonl` using schema version `pair_table_v1`.

Alternatives considered:

- Keep all normalized pairs only in memory.
- Write processed CSV files.
- Wait until feature engineering before materializing any intermediate data.

Reasoning: Interim JSONL files give later feature engineering a stable, inspectable input without modifying raw data. JSONL preserves nested left/right attributes cleanly and can be generated with the Python standard library. Because `data/interim/` is ignored by Git, generated files do not pollute the repository.

Impact: Future preprocessing and feature code can read `pair_table_v1` instead of rejoining raw files every time. The interim files remain reproducible artifacts, not source data.

Evidence available at decision time: Export scripts wrote 5,010 `abt-buy` train rows and 4,500 WDC unseen test rows with matching line counts, and `git check-ignore` confirmed the outputs are excluded by `.gitignore`.

## 2026-08-15: Keep text standardization small and dependency-free before feature engineering

Decision: Implement text standardization as Python standard-library primitives under `src/entity_matching/preprocessing/`, without writing final processed feature tables yet.

Alternatives considered:

- Add pandas or scikit-learn preprocessing immediately.
- Combine text normalization and similarity feature extraction in one module.
- Write normalized text artifacts to `data/processed/` before feature definitions are stable.

Reasoning: Lowercasing, whitespace cleanup, missing-value handling, tokenization, and numeric-token extraction are needed before reliable string-similarity features can be tested. Keeping these as small pure functions makes behavior easy to test and review before introducing feature engineering or model dependencies.

Impact: Feature engineering should consume `text_standardization_v1` profiles instead of repeatedly inventing local normalization rules. Final processed feature files remain out of scope until feature definitions are implemented and validated.

Evidence available at decision time: `python -m unittest tests.test_preprocessing` passed seven tests, and `scripts/preview_text_standardization.py` successfully previewed standardized profiles from interim JSONL input.

## 2026-08-15: Implement initial string-similarity features as primitives before full feature tables

Decision: Add dependency-free string-similarity primitives under `src/entity_matching/features/` with schema version `string_similarity_v1`, and preview them from interim JSONL without generating full processed feature tables yet.

Alternatives considered:

- Install feature-engineering dependencies immediately.
- Generate full processed feature tables before feature definitions are tested.
- Skip simple string features and move directly to model training.

Reasoning: The first feature layer should be transparent and easy to audit. Exact match, token Jaccard, numeric-token overlap, and normalized edit similarity are simple enough to test with the Python standard library and are aligned with the traditional-baseline MVP. Delaying full feature-table export keeps this milestone focused on feature semantics rather than pipeline scale.

Impact: Downstream feature-table generation should reuse `string_similarity_v1` rather than redefining similarity behavior. Missing-vs-missing exact matches are scored as `0.0` to avoid inflated similarity from shared missing fields. Feature names should remain snake_case for stable model inputs.

Evidence available at decision time: `python -m unittest discover tests` passed 24 tests, and `scripts/preview_string_features.py` produced feature dictionaries for both `abt-buy` and WDC interim JSONL examples.

## 2026-08-15: Materialize feature tables as ignored CSV files with summary metadata

Decision: Export full split-level feature tables to `data/processed/<dataset_id>/<split>.csv` using schema version `feature_table_v1`, with a sibling `.summary.json` file for each split.

Alternatives considered:

- Keep features only as preview dictionaries.
- Write nested JSONL feature rows.
- Move directly from interim JSONL to model training without materialized feature tables.

Reasoning: CSV gives traditional ML baselines a simple, inspectable tabular input. The summary JSON preserves reproducibility metadata that should not be buried in the CSV itself: schema version, text standardization version, feature version, row counts, label counts, and feature column names. Keeping `data/processed/` ignored by Git prevents generated artifacts from polluting the repository.

Impact: Future model training should read `feature_table_v1` CSV files and validate them against the summary metadata before fitting. Feature-table export remains a reproducible generation step, not a source-data editing step.

Evidence available at decision time: `python -m unittest discover tests` passed 29 tests. Export completed for `abt-buy` and WDC Products, producing expected row counts such as 5,010 `abt-buy` train rows and 4,500 WDC unseen test rows.

## 2026-08-15: Bound edit similarity for pure-Python full-split export

Decision: Compute `edit_similarity_ratio` on the first 64 normalized characters by default while keeping full `levenshtein_distance` available as a primitive.

Alternatives considered:

- Compute full Levenshtein edit similarity for every combined text and description field.
- Drop edit similarity entirely.
- Install optimized external string-similarity dependencies immediately.

Reasoning: Full pure-Python Levenshtein on long descriptions made full dataset export exceed local time limits. Bounded edit similarity keeps short title/name comparisons useful while making full-split export feasible without adding dependencies. Long descriptions are still represented by token Jaccard and numeric-token overlap.

Impact: `combined_edit_similarity` and long-field edit similarities are approximate prefix-based features. This must be disclosed in methods and can later be revisited with an optimized dependency or feature ablation.

Evidence available at decision time: Full export timed out before bounding; after bounding, all 29 tests passed in about 13 seconds, `abt-buy` export completed in about 13 seconds, and WDC Products export completed in about 45 seconds.
