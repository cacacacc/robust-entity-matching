# Phase 3 Seen vs Unseen Audit

Date: 2026-08-20

## Scope

This audit covers the WDC seen-test baseline run and its comparison with the existing unseen-test baselines.

Seen run:

- Config: `configs/experiments/wdc_seen_baseline_fit.json`
- Experiment ID: `wdc_seen_baseline_fit_v1`
- Train split: `train_small`
- Validation split: `valid_small`
- Test split: `test_seen_000un`
- Models: `logistic_regression`, `random_forest`, `svm`
- Seeds: `13`, `29`, `47`, `71`, `101`

Unseen references:

- `results/summaries/wdc_unseen_logistic_regression_fit_v1/aggregate.json`
- `results/summaries/wdc_unseen_rf_svm_fit_v1/aggregate.json`

## Leakage And Split Notes

Local split guard inspection found:

- `train_small` vs `test_seen_000un`: 0 pair overlap, 0 record overlap, 500 entity overlap.
- `valid_small` vs `test_seen_000un`: 0 pair overlap, 4 record overlap, 500 entity overlap.

Therefore, `test_seen_000un` should be treated as an official seen-split diagnostic. It is not a leakage-free final test in the same sense as `test_unseen_100un`.

## Commands

Run seen baseline:

```powershell
python scripts/run_approved_baseline.py configs/experiments/wdc_seen_baseline_fit.json
```

Audit seen baseline:

```powershell
python scripts/audit_baseline_results.py results/summaries/wdc_seen_baseline_fit_v1/aggregate.json
```

Export seen-vs-unseen comparison:

```powershell
python scripts/export_seen_unseen_comparison.py
```

## Artifacts

- Seen aggregate summary: `results/summaries/wdc_seen_baseline_fit_v1/aggregate.json`
- Seen raw predictions: `results/predictions/wdc_seen_baseline_fit_v1/<model_id>/seed_<seed>/`
- Comparison CSV: `reports/seen_vs_unseen_comparison.csv`
- Comparison Markdown: `reports/seen_vs_unseen_comparison.md`

Artifact counts:

- Seen seed summaries: `15`
- Seen aggregate summary files: `1`
- Seen raw prediction files: `30`
- Saved model artifacts: none

## Audit Result

- `audit_status`: `passed`
- Models audited: `logistic_regression`, `random_forest`, `svm`
- Seed results audited: `15`

## Comparison

| Model | Seen F1 | Unseen F1 | Unseen - Seen F1 | Seen Precision | Unseen Precision | Seen Recall | Unseen Recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| `random_forest` | `0.501589` | `0.559863` | `+0.058274` | `0.400998` | `0.469810` | `0.672400` | `0.695200` |
| `logistic_regression` | `0.487692` | `0.535862` | `+0.048169` | `0.396250` | `0.455820` | `0.634000` | `0.650000` |
| `svm` | `0.482928` | `0.529547` | `+0.046620` | `0.384246` | `0.436787` | `0.650000` | `0.672400` |

## Interpretation

The observed result is that `test_unseen_100un` scores higher than `test_seen_000un` for all three traditional baselines. This is not the naive expectation that unseen entities must always be harder.

The result should be interpreted carefully:

- Both seen and unseen test splits have the same label counts: 500 matches and 4000 non-matches.
- The seen split has known development overlap and is not leakage-free.
- The unseen split remains the correct split for entity-disjoint robustness claims.
- The performance difference may reflect official WDC split composition and hard-negative difficulty, not only entity seen/unseen status.

The final report should state this as an empirical finding rather than forcing an unseen-harder narrative.
