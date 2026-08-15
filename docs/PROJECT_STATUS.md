# Project Status

## Current Phase

Phase 2: Data Ingestion and Data Contract. Implementation-complete pending user approval to enter Phase 3.

## Completed Work

- Initialized the local Git repository on branch `main`.
- Created the initial repository directory structure.
- Added initial repository documentation and ignore rules.
- Connected the local repository to the GitHub remote `https://github.com/cacacacc/robust-entity-matching.git`.
- Created the first commit: `c70cb51 Initialize research project structure`.
- Added Phase 0 concept explanation, research-question review, scope boundaries, and feasibility judgment.
- Checked Python, Git, repository status, and document structure.
- Started Phase 1 with an initial audit of two core papers and official dataset sources.
- Updated `docs/LITERATURE_NOTES.md` with source-grounded notes on class ratio and unseen-entity evaluation.
- Updated `docs/DATASET_AUDIT.md` with initial dataset suitability notes for WDC Products, CompERBench, and WDC LSPM.
- Updated `docs/EXPERIMENT_PROTOCOL.md` with audit-derived draft constraints.
- User explicitly approved downloading small public files for Phase 1 schema audit, with each file under 500MB.
- Downloaded and inspected WDC Products `sample_pairwise.json` and `80pair.zip`.
- Downloaded and inspected CompERBench `abt-buy` train/validation/test labels and records.
- Found WDC Products `80pair` has suitable fields for labels, pair IDs, cluster IDs, and hard-negative flags.
- Found CompERBench `abt-buy` is small and useful, but its official split has duplicate pairs and substantial source/target ID overlap across splits.
- Created initial dataset configuration files for WDC Products `80pair` and CompERBench `abt-buy`.
- Implemented initial standard-library data ingestion helpers for loading dataset configs and validating raw file schema.
- Added a dataset audit CLI script.
- Added standard-library unit tests for dataset config loading and raw schema validation.
- Found and handled a real encoding issue in `abt-buy` record files by adding `cp1252` and `latin-1` fallback decoding.
- Implemented a normalized in-memory `PairRecord` representation for WDC Products and CompERBench `abt-buy`.
- Added `scripts/preview_pair_table.py` to summarize normalized pair tables and inspect examples.
- Implemented data quality reports for normalized pair tables.
- Added `scripts/report_data_quality.py` for JSON quality summaries.
- Found that WDC Products `test_unseen_100un` has zero record/entity overlap with `train_small` and `valid_small`.
- Found that WDC Products mixed and seen variants intentionally overlap with train/validation at the entity level, and some mixed comparisons also overlap at pair/record level.
- Found that `abt-buy` has duplicate pairs within train and validation, plus cross-split pair and record overlap.
- Defined interim schema version `pair_table_v1`.
- Implemented interim JSONL export for normalized pair tables.
- Exported WDC Products and CompERBench `abt-buy` normalized splits to `data/interim/`.
- Implemented text standardization primitives for normalized pair attributes.
- Added tests for missing-value handling, whitespace cleanup, tokenization, numeric-token extraction, attribute normalization, and interim pair payload standardization.
- Added `scripts/preview_text_standardization.py` to inspect standardized text profiles from interim JSONL files.
- Implemented initial string-similarity feature primitives under schema version `string_similarity_v1`.
- Added tests for exact match, token Jaccard, numeric-token overlap, Levenshtein distance, edit-similarity ratio, and standardized pair feature dictionaries.
- Added `scripts/preview_string_features.py` to inspect feature dictionaries from interim JSONL files.
- Implemented reproducible feature-table export under schema version `feature_table_v1`.
- Added processed CSV export plus per-split summary JSON files under `data/processed/`.
- Added schema validation and row-count tests for feature-table generation.
- Exported WDC Products and CompERBench `abt-buy` feature tables from interim JSONL.
- Bounded edit-similarity computation to the first 64 normalized characters to keep pure-Python full-split export feasible.
- Implemented split manifest loading and feature-table validation utilities.
- Implemented split guard reports for within-split duplicate pair IDs, cross-split pair overlap, record overlap, and entity overlap.
- Added `scripts/check_split_guards.py` for model-readiness checks before training.
- Confirmed WDC `train_small` vs `test_unseen_100un` passes pair, record, and entity disjoint checks.
- Confirmed WDC `train_small` vs `valid_small` has 500 overlapping entity IDs, so the official small train/validation/test trio is not fully three-way entity-disjoint.
- Confirmed CompERBench `abt-buy` feature tables preserve known duplicate train pairs and train/test pair and record leakage risks.
- Implemented model-ready matrix loading from validated feature tables without fitting models.
- Added `ModelMatrix` and `ModelMatrixBundle` containers for `X`, `y`, `pair_ids`, feature columns, label counts, and guard reports.
- Added `scripts/preview_model_matrix.py` to inspect matrix shapes and metadata.
- Added draft baseline configuration `configs/models/baseline_traditional.json` for planned traditional model families.
- Added a dry-run-only first baseline protocol config at `configs/experiments/wdc_unseen_baseline_dry_run.json`.
- Implemented experiment dry-run scaffolding that validates config, dependency availability, strict split guards, and model-ready matrix loading without fitting models.
- Added `scripts/dry_run_baseline_protocol.py` for dry-run protocol checks.
- Confirmed local optional ML dependencies are available (`sklearn`, `numpy`, `pandas`), but no model fitting has been run.
- Implemented binary metric primitives under schema version `binary_metrics_v1`.
- Implemented validation-only threshold-selection scaffold under schema version `threshold_selection_v1`.
- Added `scripts/preview_threshold_metrics.py` with toy scores only; it does not use model predictions or project experiment results.
- Completed Phase 2 reproducibility audit in `docs/PHASE_2_REPRODUCIBILITY_AUDIT.md`.
- Confirmed no model fitting, prediction generation, result reporting, or saved model artifacts have been produced.

## Verification Results

- Git is installed.
- Git version: `2.51.0.windows.2`.
- Python is installed as `python`.
- Python version: `3.11.9`.
- Windows `py` launcher is not available in the current shell.
- The workspace was initially empty.
- The workspace is now a local Git repository.
- The current branch tracks `origin/main`.
- Git reported a `dubious ownership` warning because the repository was initialized by the sandbox user while the normal Windows user is `Catherine`. This can be fixed by adding the workspace to Git's safe directory list.
- Git also reported a warning that `C:\Users\Catherine/.config/git/ignore` could not be accessed due to permission restrictions. Repository-local `.gitignore` is present and usable.

## Current Issues

- No Python environment has been created yet.
- Initial ingestion validation code and tests exist.
- Dataset choice is now provisionally selected but not protocol-locked.
- Local raw audit files have been downloaded under `data/raw/`; they are intentionally ignored by Git.
- CompERBench `abt-buy` must not be used for unseen-entity claims under its official split.
- A third product dataset, such as `amazon-google` or `products (Walmart-Amazon)`, remains optional after the first ingestion pipeline works.
- Standardized interim JSONL files have been generated under `data/interim/`; they are intentionally ignored by Git and can be regenerated.
- Text standardization, initial string-similarity feature primitives, full processed feature-table generation, split guard reporting, model-ready matrix loading, dry-run baseline protocol checks, and metric/threshold scaffolding exist, but no custom splitting module, model fitting/training, predictions, or experiments have been implemented yet.
- Quality reports are currently printed to stdout only; they are not saved as result artifacts yet.

## Next Milestone

Next milestone: decide whether to enter Phase 3 model implementation. Do not fit models until explicitly approved and the validation/threshold protocol is made explicit.

## Key Commands

```powershell
git config --global --add safe.directory D:/code/robust-entity-matching
git status --short --branch
git remote -v
python --version
git --version
python -m unittest tests.test_data_validation
python scripts/audit_dataset.py configs/datasets/wdc_products_80pair.json
python scripts/audit_dataset.py configs/datasets/comperbench_abt_buy.json
python scripts/preview_pair_table.py configs/datasets/wdc_products_80pair.json train_small --examples 1
python scripts/preview_pair_table.py configs/datasets/comperbench_abt_buy.json train --examples 1
python scripts/report_data_quality.py configs/datasets/wdc_products_80pair.json
python scripts/report_data_quality.py configs/datasets/comperbench_abt_buy.json
python scripts/export_interim_pairs.py configs/datasets/wdc_products_80pair.json
python scripts/export_interim_pairs.py configs/datasets/comperbench_abt_buy.json
python -m unittest tests.test_preprocessing
python scripts/preview_text_standardization.py data/interim/comperbench_abt_buy/train.jsonl --examples 1
python -m unittest tests.test_string_similarity_features
python scripts/preview_string_features.py data/interim/comperbench_abt_buy/train.jsonl --examples 1
python -m unittest tests.test_feature_table
python scripts/export_feature_tables.py configs/datasets/comperbench_abt_buy.json
python scripts/export_feature_tables.py configs/datasets/wdc_products_80pair.json
python -m unittest tests.test_split_guards
python scripts/check_split_guards.py configs/datasets/wdc_products_80pair.json --splits train_small test_unseen_100un --require-record-disjoint --require-entity-disjoint
python scripts/check_split_guards.py configs/datasets/comperbench_abt_buy.json --splits train test --report-only
python -m unittest tests.test_model_matrix
python scripts/preview_model_matrix.py configs/datasets/wdc_products_80pair.json --splits train_small test_unseen_100un --require-record-disjoint --require-entity-disjoint
python -m unittest tests.test_experiment_dry_run
python scripts/dry_run_baseline_protocol.py configs/experiments/wdc_unseen_baseline_dry_run.json
python -m unittest tests.test_evaluation_metrics
python scripts/preview_threshold_metrics.py
Get-Content docs/PHASE_2_REPRODUCIBILITY_AUDIT.md
```

## Latest Phase 1 Sources Checked

- Foxcroft, Christen, and Antonie, `Class Ratio and Its Implications for Reproducibility and Performance in Record Linkage`: https://users.cecs.anu.edu.au/~Peter.Christen/publications/foxcroft2024ratio.pdf
- Foxcroft, Sartor, and Antonie, `Comparing Traditional and Deep Learning Approaches for Product Matching: Performance on Unseen Entities`: https://assets.pubpub.org/izpipo2h/189-51747605873107.pdf
- WDC Products benchmark official page: https://webdatacommons.org/largescaleproductcorpus/wdc-products/index.html
- CompERBench official page: https://data.dws.informatik.uni-mannheim.de/benchmarkmatchingtasks/
- WDC LSPM v2 official page: https://webdatacommons.org/largescaleproductcorpus/v2/

## Files Created So Far

- `README.md`: public-facing project overview.
- `AGENTS.md`: collaboration and research-integrity rules.
- `.gitignore`: prevents local data, outputs, caches, and environments from being committed.
- `requirements.txt`: placeholder for future locked dependencies.
- `docs/PROJECT_BRIEF.md`: project motivation, RQs, scope, and success criteria.
- `docs/PROJECT_STATUS.md`: truthful current state and next milestone.
- `docs/DECISIONS.md`: important decisions and rationale.
- `docs/EXPERIMENT_PROTOCOL.md`: draft experiment protocol.
- `docs/PHASE_0_FOUNDATION.md`: Phase 0 explanation, RQ review, scope, and feasibility.
- `docs/LITERATURE_NOTES.md`: future paper audit notes.
- `docs/DATASET_AUDIT.md`: future dataset audit notes.
- `docs/RESULTS_LOG.md`: future experiment run log.
- `docs/LEARNING_GUIDE.md`: future learning notes.
- `docs/CODE_WALKTHROUGH.md`: future code explanation.
- `docs/INTERVIEW_GUIDE.md`: future advisor interview preparation.
- `docs/PHASE_2_REPRODUCIBILITY_AUDIT.md`: Phase 2 exit audit and Phase 3 readiness check.
