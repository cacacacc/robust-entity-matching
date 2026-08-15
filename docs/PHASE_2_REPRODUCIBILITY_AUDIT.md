# Phase 2 Reproducibility Audit

Audit date: 2026-08-15.

Status: Phase 2 is implementation-complete for data ingestion, data contracts, feature-table generation, split guards, model-ready matrix loading, dry-run protocol checks, and metric scaffolding. No model fitting, prediction, evaluation run, or result reporting has been performed.

## Audit Scope

This audit checks whether the current repository state is ready to move toward Phase 3 model implementation planning.

Checked areas:

- implemented modules;
- generated local artifacts;
- Git ignore boundaries;
- test coverage;
- split/leakage guard behavior;
- dry-run baseline protocol;
- absence of training or result artifacts.

## Implemented Contracts

Current schema and protocol versions:

- Raw dataset configs: `configs/datasets/*.json`.
- Normalized pair table: `pair_table_v1`.
- Text standardization: `text_standardization_v1`.
- String similarity features: `string_similarity_v1`.
- Processed feature tables: `feature_table_v1`.
- Binary metrics: `binary_metrics_v1`.
- Threshold selection: `threshold_selection_v1`.
- First baseline dry-run config: `wdc_unseen_baseline_dry_run`.

## Verification Commands

Full test suite:

```powershell
python -m unittest discover tests
```

Result:

```text
Ran 52 tests in 14.810s
OK
```

Strict WDC unseen guard:

```powershell
python scripts/check_split_guards.py configs/datasets/wdc_products_80pair.json --splits train_small test_unseen_100un --require-record-disjoint --require-entity-disjoint
```

Result summary:

- `pair_id_overlap`: 0
- `record_id_overlap`: 0
- `entity_id_overlap`: 0

First baseline dry-run:

```powershell
python scripts/dry_run_baseline_protocol.py configs/experiments/wdc_unseen_baseline_dry_run.json
```

Result summary:

- `status`: `dry_run_only`
- `fit_allowed`: `false`
- `ready_for_fit`: `false`
- `planned_training_status`: `not_started`
- WDC `train_small`: 2,500 rows, 24 features
- WDC `test_unseen_100un`: 4,500 rows, 24 features
- `sklearn`, `numpy`, and `pandas` are locally available

## Git Ignore Audit

Confirmed ignored:

- `data/raw/*`
- `data/interim/*`
- `data/processed/*`
- local teaching workspace files such as `MISSION.md` and `lessons/`

Important correction already made:

- `.gitignore` now uses `/models/` instead of `models/`, so `src/entity_matching/models/` and `configs/models/` remain trackable project files.

## Generated Artifact Audit

Generated local artifacts exist but are ignored:

- raw audit files under `data/raw/`;
- interim pair tables under `data/interim/`;
- processed feature tables under `data/processed/`.

Result/report directories contain only `.gitkeep` placeholders:

- `results/raw/`
- `results/summaries/`
- `results/predictions/`
- `reports/`

No saved model files, prediction files, result summaries, report PDFs, or report HTML files were found.

## Training Absence Audit

A repository scan for training/prediction patterns found no model-fitting or prediction calls such as:

- `.fit(`
- `.predict(`
- `predict_proba`
- `joblib`
- `pickle`

The only matching persistence call was `json.dump` for feature-table summary metadata in `src/entity_matching/features/table.py`.

## Known Scientific Boundaries

Still true:

- No model has been fitted.
- No predictions exist.
- No experiment metrics exist.
- Threshold-selection code has only been tested with toy scores.
- PR-AUC, calibration, runtime, seed aggregation, and raw prediction persistence are not implemented.
- WDC `train_small` and `test_unseen_100un` are strict-disjoint as a pair.
- WDC `train_small` and `valid_small` have 500 overlapping entity IDs, so the official small train/validation/test trio must not be called fully three-way entity-disjoint.
- CompERBench `abt-buy` has duplicate pairs and cross-split overlap, so it remains a smoke-test or fixed-split baseline dataset only.

## Phase 2 Exit Judgment

Phase 2 can be considered complete for the current MVP foundation if the next step is Phase 3 planning and model implementation scaffolding.

Do not run model fitting yet unless the user explicitly approves moving into Phase 3 and the validation/threshold protocol is made explicit.

Recommended next step:

1. Decide the first actual baseline protocol.
2. Resolve validation strategy for threshold selection.
3. Add training code that refuses to run unless `fit_allowed` is explicitly true.
4. Save raw predictions and run metadata once training begins.
