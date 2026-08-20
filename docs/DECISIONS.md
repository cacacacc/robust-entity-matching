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

## 2026-08-15: Add split guards before model-ready matrix loading

Decision: Implement split manifest validation and leakage guard reports before adding model-fitting code.

Alternatives considered:

- Start model training directly from processed CSV files.
- Rely only on earlier data quality notes.
- Fail all datasets with any duplicate pair IDs before reporting diagnostics.

Reasoning: The project research questions depend on fair evaluation protocols. Model training should not begin until feature tables have been validated and split leakage is explicitly checked. Guard reports should be able to report known dataset problems, such as `abt-buy` duplicate pairs, instead of crashing before producing diagnostic evidence.

Impact: Future training code should call split guards before loading model matrices. Strict unseen claims should require pair, record, and entity disjoint checks. Fixed-split baseline experiments may still use non-strict datasets, but only with documented limitations.

Evidence available at decision time: `python -m unittest discover tests` passed 35 tests. Guard reports confirmed WDC `train_small` vs `test_unseen_100un` has zero pair, record, and entity overlap; WDC `train_small` vs `valid_small` has 500 overlapping entity IDs; and `abt-buy` train/test has duplicate and cross-split leakage risks.

## 2026-08-15: Load model-ready matrices without fitting models

Decision: Add pure-Python `ModelMatrix` and `ModelMatrixBundle` loaders that convert validated feature tables into `X`, `y`, and `pair_ids`, while keeping model fitting out of scope.

Alternatives considered:

- Install scikit-learn and fit the first baseline immediately.
- Use pandas or NumPy as the matrix representation now.
- Let training code read CSV files directly without a checked matrix contract.

Reasoning: The project needs a clear boundary between data readiness and model training. A lightweight matrix loader verifies row alignment, feature column order, labels, and guard constraints before any estimator is introduced. This keeps the next training step smaller and reduces the chance of silent feature/label misalignment.

Impact: Future training code should consume `ModelMatrixBundle` rather than raw CSV rows. Baseline model definitions are documented in `configs/models/baseline_traditional.json`, but their implementations and hyperparameters are not locked yet.

Evidence available at decision time: `python -m unittest discover tests` passed 40 tests. `scripts/preview_model_matrix.py` loaded WDC `train_small` and `test_unseen_100un` with strict record/entity guards and reported aligned 24-feature vectors.

## 2026-08-15: Keep the first baseline protocol as dry-run only

Decision: Add `configs/experiments/wdc_unseen_baseline_dry_run.json` and dry-run scaffolding that validates dependencies, split guards, matrix loading, and planned model metadata without fitting a model.

Alternatives considered:

- Fit Logistic Regression immediately because `sklearn` is available locally.
- Use WDC `valid_small` as validation without addressing its entity overlap with `train_small`.
- Skip dry-run scaffolding and add training code directly.

Reasoning: The project requires validation-only threshold selection, but the current safe WDC unseen pair is `train_small` versus `test_unseen_100un`; validation protocol remains unresolved because `train_small` and `valid_small` have entity overlap. A dry-run keeps progress moving while preventing accidental premature training or test-set-based decisions.

Impact: The first actual baseline run must wait until threshold-selection and validation protocol are explicit. Training scripts should reject configs where `fit_allowed` is false.

Evidence available at decision time: `python -m unittest discover tests` passed 44 tests. `scripts/dry_run_baseline_protocol.py configs/experiments/wdc_unseen_baseline_dry_run.json` reported `ready_for_fit: false`, strict guard success, 24 feature columns, and local availability of `sklearn`, `numpy`, and `pandas`.

## 2026-08-15: Implement metrics and threshold selection before model fitting

Decision: Add dependency-free binary metric primitives and validation-only threshold-selection scaffolding before adding any model training code.

Alternatives considered:

- Let scikit-learn metrics handle evaluation only after model fitting.
- Pick a fixed threshold such as `0.5` without validation-selection code.
- Implement PR-AUC and calibration immediately.

Reasoning: The protocol requires threshold selection on validation data only. Implementing this boundary before training makes it harder to accidentally tune on test data. The first metric layer should cover confusion matrix, precision, recall, and F1 because these are needed for threshold selection and are simple enough to test without dependencies.

Impact: Future training code should call `select_threshold_on_validation` using validation scores only, then apply the selected threshold to held-out test scores. PR-AUC, calibration, runtime, seed aggregation, and raw prediction persistence remain future work.

Evidence available at decision time: `python -m unittest discover tests` passed 52 tests. `scripts/preview_threshold_metrics.py` produced a toy-only threshold-selection report and explicitly stated that no project predictions or experiment results were used.

## 2026-08-15: Close Phase 2 only after a reproducibility audit

Decision: Add `docs/PHASE_2_REPRODUCIBILITY_AUDIT.md` before moving toward Phase 3 model implementation.

Alternatives considered:

- Move directly from metric scaffolding into model fitting.
- Treat passing tests as sufficient without an explicit phase-exit record.
- Defer reproducibility review until after the first baseline result.

Reasoning: Phase 2 created many data contracts and generated artifacts. A written audit makes the current state falsifiable: which tests passed, which artifacts are ignored, which claims are still forbidden, and which protocol gaps remain. This is especially important before model training, where accidental leakage or premature result claims would be harder to unwind.

Impact: Phase 3 should start only after the user explicitly approves model implementation and the validation/threshold-selection protocol is clarified. Training code should refuse to run while `fit_allowed` remains false.

Evidence available at decision time: `python -m unittest discover tests` passed 52 tests; WDC `train_small` versus `test_unseen_100un` passed strict pair/record/entity guards; dry-run baseline protocol returned `ready_for_fit: false`; `results/` and `reports/` contained only `.gitkeep`; code scan found no `.fit(`, `.predict(`, `predict_proba`, `joblib`, or `pickle` training artifacts.

## 2026-08-15: Start Phase 3 with model factory and training guards, not fitting

Decision: Enter Phase 3 by adding sklearn estimator factory utilities and explicit training guards, while keeping all model fitting blocked.

Alternatives considered:

- Fit the first Logistic Regression model immediately.
- Keep model configs abstract without instantiating sklearn estimators.
- Add training code before a guard that enforces `fit_allowed`.

Reasoning: The user approved entering Phase 3, but the validation/threshold protocol remains unresolved. Instantiating unfitted estimators is a safe first modeling step: it verifies dependencies and configuration shape without creating predictions or results. A training guard prevents accidental fitting from dry-run configs.

Impact: Future training code must call the training guard before `fit()`. A fit-enabled config should be created only after validation/threshold protocol decisions are explicit.

Evidence available at decision time: `python -m unittest discover tests` passed 57 tests. `scripts/preview_model_factory.py configs/models/baseline_traditional.json --seed 13` instantiated Logistic Regression, Random Forest, and SVM estimators and reported `is_fitted: false` for all.

## 2026-08-16: Lock the first WDC unseen baseline protocol without fitting

Decision: Use WDC Products `train_small` for training, `valid_small` for threshold selection, and `test_unseen_100un` for final unseen-entity evaluation in the first traditional-baseline protocol. Keep `fit_allowed: false`.

Alternatives considered:

- Delay protocol locking until a new entity-disjoint validation split is generated.
- Use `test_unseen_100un` for threshold selection.
- Claim the official small train/validation/test trio is fully entity-disjoint.

Reasoning: `valid_small` has entity overlap with `train_small`, so it cannot support a train-validation entity-disjoint claim. However, it is still a legitimate development split for threshold selection as long as this limitation is explicit. The final unseen claim is protected because `test_unseen_100un` has zero pair, record, and entity overlap with both development splits.

Impact: Thresholds must be selected on `valid_small` only. The test split must not be used for threshold selection or model selection. The first fit-enabled config may be created only after training code can save raw predictions and the user explicitly approves the first actual baseline run.

Evidence available at decision time: `python -m unittest tests.test_experiment_protocol` passed. `scripts/validate_experiment_protocol.py configs/experiments/wdc_unseen_baseline_protocol.json` confirmed zero pair, record, and entity overlap for both train-to-test and validation-to-test comparisons, while reporting 500 entity overlaps between `train_small` and `valid_small`.

## 2026-08-16: Add run-plan and raw prediction schema before training execution

Decision: Implement a baseline run-plan preview and raw prediction artifact schema before adding any training execution code.

Alternatives considered:

- Add the first executable training script immediately.
- Let each model write predictions in its own ad hoc format.
- Defer prediction artifact design until after seeing model results.

Reasoning: Raw predictions are needed for reproducibility, threshold auditing, error analysis, and later result aggregation. Defining the schema before training prevents accidental result files with missing pair IDs, seeds, thresholds, or split roles. A run-plan preview verifies what would be executed while keeping `fit_allowed: false`.

Impact: Future training code should write `raw_predictions_v1` CSV files under the planned paths. The run-plan remains non-executing: it validates matrices, guards, model definitions, seed schedule, and artifact locations but does not train or predict.

Evidence available at decision time: `python -m unittest tests.test_prediction_artifacts tests.test_baseline_run_plan` passed. `scripts/preview_baseline_run_plan.py configs/experiments/wdc_unseen_baseline_protocol.json --model logistic_regression` reported `fit_allowed: false`, `ready_to_execute_training: false`, unfitted estimators, 24 feature columns, and planned validation/test raw prediction paths.

## 2026-08-16: Run the first approved Logistic Regression baseline

Decision: Execute only the first approved Logistic Regression baseline under the locked WDC unseen protocol.

Alternatives considered:

- Run all planned traditional baselines immediately.
- Run Random Forest and SVM before auditing the first Logistic Regression result.
- Save trained model artifacts.

Reasoning: The user explicitly approved the first real baseline run. Keeping the run to Logistic Regression makes the first result small, fast, and auditable. Saving raw predictions and summaries is enough for reproducibility and error analysis at this point; saved model artifacts can be added later if needed.

Impact: The project now has one real baseline result. Random Forest and SVM remain unrun. The first result should be audited before expanding to additional models.

Evidence available at decision time: `python scripts/run_approved_baseline.py configs/experiments/wdc_unseen_logistic_regression_fit.json` completed successfully. Five seeds produced selected threshold `0.66`, test F1 mean `0.5358615004122012`, precision mean `0.45582047685834504`, recall mean `0.65`, and standard deviation `0.0` for these metrics.

## 2026-08-16: Audit Logistic Regression results before expanding baselines

Decision: Add result-audit code and audit the first Logistic Regression baseline before running Random Forest or SVM.

Alternatives considered:

- Move directly to Random Forest and SVM.
- Trust the aggregate JSON without checking raw prediction files.
- Perform only manual inspection of a few prediction rows.

Reasoning: The project depends on reproducible, auditable results. Before adding more model outputs, the first result should prove that row-level predictions can reproduce per-seed and aggregate metrics.

Impact: Additional baselines should use the same raw prediction schema and should pass the same audit before their metrics are treated as reportable.

Evidence available at decision time: `python -m unittest tests.test_result_audit` passed. `python scripts/audit_baseline_results.py results/summaries/wdc_unseen_logistic_regression_fit_v1/aggregate.json` reported `audit_status: passed` and confirmed stored metrics match recomputed metrics from raw predictions.

## 2026-08-16: Run Random Forest and SVM under the locked WDC protocol

Decision: Execute `random_forest` and `svm` under the same locked WDC unseen protocol used for Logistic Regression.

Alternatives considered:

- Do qualitative Logistic Regression error analysis first.
- Change the protocol or feature set before running the remaining baselines.
- Run only Random Forest or only SVM.

Reasoning: The user explicitly requested running Random Forest and SVM under the same locked protocol. Keeping the split, threshold-selection rule, seed schedule, and raw prediction schema unchanged makes the three traditional baselines comparable.

Impact: The initial traditional baseline set is now complete for the first WDC unseen protocol. Next work should compare results and decide whether to add PR-AUC, report tables, or qualitative error analysis.

Evidence available at decision time: `python scripts/run_approved_baseline.py configs/experiments/wdc_unseen_rf_svm_fit.json` completed successfully. `python scripts/audit_baseline_results.py results/summaries/wdc_unseen_rf_svm_fit_v1/aggregate.json` reported `audit_status: passed`. Random Forest reached test F1 mean `0.5598631874163362`; SVM reached test F1 mean `0.5295473051367368`.

## 2026-08-16: Export a tracked comparison table for the initial baselines

Decision: Create small tracked comparison artifacts under `reports/` from audited aggregate summaries.

Alternatives considered:

- Leave the comparison only in `docs/RESULTS_LOG.md`.
- Track raw prediction CSVs in Git.
- Wait until PR-AUC is implemented before creating any table.

Reasoning: A small CSV and Markdown table gives the project a stable, machine-readable and human-readable comparison without committing large raw prediction artifacts. The table is generated from audited summaries rather than manually copied from terminal output.

Impact: Future model comparisons should update `reports/baseline_comparison.csv` and `reports/baseline_comparison.md` through `scripts/export_baseline_comparison.py`.

Evidence available at decision time: `python -m unittest tests.test_baseline_comparison` passed. `python scripts/export_baseline_comparison.py` wrote three rows and ranked `random_forest` first by test F1 mean.

## 2026-08-16: Keep detailed error examples out of Git

Decision: Store detailed false-positive and false-negative examples under ignored `results/error_analysis/`, while recording aggregate conclusions in tracked documentation.

Alternatives considered:

- Commit the full error-analysis Markdown report.
- Include raw product titles and descriptions directly in `docs/RESULTS_LOG.md`.
- Avoid saving detailed examples at all.

Reasoning: Error analysis needs raw product attributes to be useful locally, but those attributes are derived from downloaded benchmark data and should not be casually committed. Keeping detailed examples local preserves inspection ability while keeping the repository clean and lightweight.

Impact: Future qualitative analyses should write detailed local reports under `results/error_analysis/` and summarize only aggregate, non-sensitive patterns in tracked docs.

Evidence available at decision time: `python scripts/analyze_prediction_errors.py` generated JSON and Markdown reports for Random Forest seed `13`; `.gitignore` now excludes `results/error_analysis/*`.

## 2026-08-16: Add Average Precision as a threshold-free diagnostic

Decision: Report ranking Average Precision alongside selected-threshold F1 for the initial traditional baselines.

Alternatives considered:

- Continue reporting only F1, precision, and recall at the validation-selected threshold.
- Treat the coarse threshold-grid PR-AUC as the primary PR metric.
- Use scikit-learn metric helpers directly without project-level wrappers.

Reasoning: F1 at one threshold is useful but incomplete for imbalanced entity matching. Average Precision summarizes how well positive pairs are ranked above negative pairs across the score range. The project-level implementation keeps the metric definition auditable and avoids changing dependency assumptions.

Impact: Baseline comparisons should distinguish selected-threshold performance from threshold-free ranking performance. Test AP is for reporting only and must not be used to select thresholds or tune models.

Evidence available at decision time: `python -m unittest tests.test_threshold_diagnostics` passed. `python scripts/export_threshold_diagnostics.py` wrote `reports/threshold_diagnostics.csv` and `reports/threshold_diagnostics.md`, ranking `random_forest` first by test Average Precision mean.

## 2026-08-16: Plan class-ratio stress tests before running them

Decision: Add a protocol-only class-ratio stress-test plan with training ratios `1:1`, `1:2`, `1:3`, and `1:4`, while keeping model fitting disabled.

Alternatives considered:

- Start training class-ratio experiments immediately.
- Test only `1:1`, `1:2`, and `1:4`.
- Change validation and test class ratios together with the training ratio.

Reasoning: The available WDC `train_small` split has 500 matches and 2000 non-matches, so `1:1`, `1:2`, `1:3`, and `1:4` are all feasible without over-sampling or synthetic data. Keeping validation and test fixed isolates the effect of training class ratio from evaluation-set composition.

Impact: Future class-ratio runs should use all 500 training matches and sample training non-matches without replacement according to the experiment seed. The test split remains `test_unseen_100un` and must not be used for threshold or model selection.

Evidence available at decision time: `python -m unittest tests.test_class_ratio_plan` passed. `python scripts/export_class_ratio_plan.py` wrote `reports/class_ratio_plan.csv` and `reports/class_ratio_plan.md` with all four planned ratios, including `1:3`.

## 2026-08-16: Add class-ratio training guard before execution

Decision: Add a guarded class-ratio training entry point and readiness check while keeping the protocol config non-executable.

Alternatives considered:

- Implement and run the full class-ratio training loop immediately.
- Rely on documentation alone to prevent accidental training.
- Skip a class-ratio-specific guard and reuse only the baseline runner.

Reasoning: Class-ratio experiments will introduce many more runs because they cross ratios, models, and seeds. A guard-specific readiness check makes it explicit when a config is still protocol-only and prevents accidental generation of sampled training tables or prediction files.

Impact: `scripts/check_class_ratio_training_guard.py` can be used before any future class-ratio execution. The actual runner refuses the current protocol config via `TrainingNotAllowedError` because `fit_allowed` is `false`.

Evidence available at decision time: `python -m unittest tests.test_class_ratio_training_guard` passed. `python scripts/check_class_ratio_training_guard.py --model logistic_regression` reported `ready_to_execute_training: false`, `training_attempted: false`, and `writes_files_now: false`.

## 2026-08-16: Build class-ratio training matrices in memory first

Decision: Implement class-ratio sampled training matrices as in-memory `ModelMatrix` objects before adding any fitting loop.

Alternatives considered:

- Write sampled training CSV files immediately.
- Sample rows directly inside the future training loop.
- Delay sampling tests until after the full class-ratio runner exists.

Reasoning: The sampling logic is part of the experimental protocol and should be testable independently from model fitting. Returning a `ModelMatrix` preserves the existing training interface while avoiding generated sampled-data artifacts.

Impact: Future class-ratio training can reuse `build_sampled_training_matrix` and pass its output into model fitting after explicit approval. The current milestone still writes no sampled tables and produces no predictions.

Evidence available at decision time: `python -m unittest tests.test_class_ratio_plan` passed with tests for toy matrices, infeasible ratios, and the real WDC `1:3` sampled matrix.

## 2026-08-16: Implement class-ratio runner behind approval guard

Decision: Implement the class-ratio training runner code path, but keep it inaccessible to the current protocol-only config.

Alternatives considered:

- Wait to implement the runner until after approval.
- Implement the runner and immediately create a fit-enabled config.
- Use the baseline runner without ratio-specific output paths.

Reasoning: The runner needs ratio-aware output paths, sampled training matrices, and ratio-level aggregation. Implementing that structure before running experiments makes the future approval step smaller and easier to audit. The training guard still prevents accidental execution.

Impact: A future approved config can run class-ratio experiments using the existing raw prediction schema and ratio-specific result directories. Until such a config exists, `scripts/run_approved_class_ratio.py` refuses the current protocol config.

Evidence available at decision time: `python -m unittest tests.test_class_ratio_training_guard tests.test_class_ratio_plan` passed. `python scripts/check_class_ratio_training_guard.py --model logistic_regression` still reported `ready_to_execute_training: false`, `training_attempted: false`, and `writes_files_now: false`.

## 2026-08-16: Export a dry execution manifest before class-ratio runs

Decision: Add a tracked class-ratio execution manifest that expands the planned ratio/model/seed grid before any training is approved.

Alternatives considered:

- Rely on the full JSON run-plan output only.
- Wait until after training to document the executed grid.
- Track only the compact ratio plan without model and seed rows.

Reasoning: The class-ratio experiment is a larger grid than the initial baselines. A row-level manifest makes the future execution auditable before it happens: every ratio, model, seed, training size, evaluation split, and planned prediction path is visible.

Impact: Future approved class-ratio runs should be checked against `reports/class_ratio_execution_manifest.csv` before execution. Any change to ratios, models, seeds, or output paths should update the manifest first.

Evidence available at decision time: `python -m unittest tests.test_class_ratio_plan` passed. `python scripts/export_class_ratio_execution_manifest.py` wrote 60 planned task rows with `fit_allowed: false` and `writes_files_now: false`.

## 2026-08-16: Run approved class-ratio stress test and audit it

Decision: Execute the approved class-ratio stress-test run after creating a separate fit-enabled config.

Alternatives considered:

- Run only Logistic Regression first.
- Delay training until a class-ratio audit tool existed.
- Reuse the protocol-only config by flipping `fit_allowed` in place.

Reasoning: The user explicitly approved real training. A separate fit-enabled config preserves the protocol-only file as a non-executable reference. Because the run produces many artifacts, a class-ratio-specific audit was added immediately after execution.

Impact: The project now has an audited result grid for 4 training class ratios, 3 model families, and 5 seeds. Raw predictions and summaries remain under ignored `results/`, while compact result tables are exported under `reports/`.

Evidence available at decision time: `python scripts/run_approved_class_ratio.py configs/experiments/wdc_class_ratio_stress_fit.json` completed 60 seed-level tasks. `python scripts/audit_class_ratio_results.py` reported `audit_status: passed`, `ratio_count: 4`, and `seed_audit_count: 60`.

## 2026-08-16: Run a separate matched train/test class-ratio diagnostic

Decision: Add and execute a separate fit-enabled config where the test class ratio is sampled to match the training class ratio for each ratio condition.

Alternatives considered:

- Modify the original fixed-test class-ratio experiment in place.
- Treat the fixed-test result as if it also controlled test ratio.
- Re-run only one model family under matched train/test ratios.

Reasoning: The original class-ratio stress test intentionally controlled only the training ratio while keeping `test_unseen_100un` fixed. That protocol isolates the effect of training distribution under one stable unseen-entity evaluation distribution. The matched train/test variant answers a different diagnostic question: what happens when the evaluation class distribution changes together with training distribution. Keeping a separate config prevents these two interpretations from being mixed.

Impact: Reports must distinguish fixed-test results from matched train/test results. The matched results can explain sensitivity to evaluation class imbalance, but they should not replace the fixed-test results for the main robustness claim.

Evidence available at decision time: `python scripts/run_approved_class_ratio.py configs/experiments/wdc_class_ratio_matched_train_test_fit.json` completed 60 seed-level tasks. `python scripts/audit_class_ratio_results.py results/summaries/wdc_class_ratio_matched_train_test_fit_v1/aggregate.json` reported `audit_status: passed`, `ratio_count: 4`, and `seed_audit_count: 60`. The matched result table ranked Random Forest at `1:1` first with mean test F1 `0.782462373906762`.

## 2026-08-17: Compare fixed-test and matched train/test protocols explicitly

Decision: Add a dedicated protocol-comparison export instead of merging fixed-test and matched train/test class-ratio results into one leaderboard.

Alternatives considered:

- Rank all fixed and matched rows together by test F1.
- Treat matched train/test results as a corrected replacement for fixed-test results.
- Leave the distinction only in prose documentation.

Reasoning: The two experiments change different variables. Fixed-test results change only the training ratio and keep the unseen test distribution stable. Matched train/test results also change the test distribution by sampling negatives. A row-aligned comparison makes the distribution difference visible and shows that the matched F1 increase mostly comes from precision changes, while recall remains unchanged because all positive test pairs are retained.

Impact: Future reports should present fixed-test results as the main answer to the training-ratio research question, and matched train/test results as an evaluation-distribution diagnostic. The comparison artifacts should be regenerated with `scripts/export_class_ratio_protocol_comparison.py` whenever either source experiment changes.

Evidence available at decision time: `python scripts/export_class_ratio_protocol_comparison.py` wrote 12 comparison rows. The largest F1 delta was Random Forest at `1:1`, with matched-minus-fixed mean F1 `0.23599641381912817`.

## 2026-08-17: Plan a full train/test class-ratio grid before execution

Decision: Add a protocol-only train/test ratio grid crossing train ratios `1:1`, `1:2`, `1:3`, and `1:4` with test ratios `1:1`, `1:2`, `1:3`, and `1:4`.

Alternatives considered:

- Continue evaluating only the diagonal matched train/test ratios.
- Treat the fixed-test `1:8` test distribution as sufficient for all test-ratio questions.
- Start the full grid training run immediately.

Reasoning: The diagonal matched protocol cannot separate training-distribution effects from evaluation-distribution effects, because train and test ratios change together. A full grid allows comparisons across rows and columns: holding test ratio fixed isolates training-ratio effects, while holding train ratio fixed isolates test-ratio effects. The run is larger than previous experiments, so it should be planned and guarded before execution.

Impact: The project now has a dry manifest for 240 planned test evaluations and 60 optimized model fits. The protocol remains non-executable until a separate fit-enabled config is created and the user explicitly approves real training.

Evidence available at decision time: `python scripts/export_train_test_ratio_grid_manifest.py` wrote 240 dry manifest rows. `python scripts/check_train_test_ratio_grid_training_guard.py` reported `ready_to_execute_training: false`, `planned_fit_count: 60`, and `planned_test_evaluation_count: 240`.

## 2026-08-17: Run the approved full train/test class-ratio grid

Decision: Execute the full train/test ratio grid after creating a separate fit-enabled config.

Alternatives considered:

- Keep the grid as a protocol-only manifest.
- Run only the Random Forest grid first.
- Reuse the protocol-only config by changing `fit_allowed` in place.

Reasoning: The user explicitly requested fit-enabled grid execution and real training. A separate fit-enabled config preserves the protocol-only file as a reference. The runner fits each train-ratio/model/seed combination once, then evaluates that fitted model across all test ratios. This keeps the scientific grid complete while avoiding redundant fitting.

Impact: The project now has audited results for 4 train ratios, 4 test ratios, 3 model families, and 5 seeds. Raw predictions and detailed summaries remain under ignored `results/`; compact result reports are tracked under `reports/`.

Evidence available at decision time: `python scripts/run_approved_train_test_ratio_grid.py configs/experiments/wdc_train_test_ratio_grid_fit.json` completed with `planned_fit_count: 60` and `seed_result_count: 240`. `python scripts/audit_train_test_ratio_grid_results.py` reported `audit_status: passed`, `seed_audit_count: 240`, and `cell_audit_count: 48`.

## 2026-08-20: Run and report the WDC seen-vs-unseen diagnostic

Decision: Run the traditional baselines on the official WDC seen test split and compare them against the already audited unseen baselines.

Alternatives considered:

- Skip seen testing and keep only unseen robustness results.
- Assume unseen must be harder without running the seen split.
- Hide the seen result because it is lower than the unseen result.

Reasoning: The research question concerns unseen-entity shift, so the project needs an empirical seen-vs-unseen diagnostic. Scientific integrity requires reporting the observed result even when it is counterintuitive. The seen split has known development overlap, so it should be framed as an official diagnostic rather than a leakage-free final test.

Impact: The final report can now state that, under the current WDC 80pair feature/model setup, the unseen split scored higher than the seen split for all three traditional baselines. This result should motivate deeper split-composition or hard-negative analysis rather than a simplistic unseen-harder claim.

Evidence available at decision time: `python scripts/run_approved_baseline.py configs/experiments/wdc_seen_baseline_fit.json` completed 15 seed-level runs. `python scripts/audit_baseline_results.py results/summaries/wdc_seen_baseline_fit_v1/aggregate.json` passed. `python scripts/export_seen_unseen_comparison.py` wrote 3 comparison rows; Random Forest had unseen-minus-seen mean F1 `0.05827442237845326`.
