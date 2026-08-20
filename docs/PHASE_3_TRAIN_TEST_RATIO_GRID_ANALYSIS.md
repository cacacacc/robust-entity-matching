# Phase 3 Train/Test Ratio Grid Analysis

Date: 2026-08-17

## Scope

This document analyzes the audited train/test ratio grid result:

- Aggregate summary: `results/summaries/wdc_train_test_ratio_grid_fit_v1/aggregate.json`
- Result table: `reports/train_test_ratio_grid_results.csv`
- Analysis report: `reports/train_test_ratio_grid_analysis.md`

The goal is to separate:

- training-ratio effects, by holding the test ratio fixed;
- evaluation-distribution effects, by holding the training ratio fixed.

## Analysis Artifacts

Generated files:

- `reports/train_test_ratio_grid_f1_matrix.csv`
- `reports/train_test_ratio_grid_best_train_by_test_ratio.csv`
- `reports/train_test_ratio_grid_test_sensitivity.csv`
- `reports/train_test_ratio_grid_analysis.md`

Export command:

```powershell
python scripts/export_train_test_ratio_grid_analysis.py
```

## Best Train Ratio Within Each Fixed Test Ratio

| Model | Test Ratio | Best Train Ratio | Best F1 | Delta To Second | Precision | Recall |
|---|---|---|---:|---:|---:|---:|
| `logistic_regression` | `1:1` | `1:3` | `0.760369` | `0.004894` | `0.844245` | `0.692000` |
| `logistic_regression` | `1:2` | `1:3` | `0.711900` | `0.003338` | `0.733621` | `0.692000` |
| `logistic_regression` | `1:3` | `1:3` | `0.669753` | `0.001327` | `0.649443` | `0.692000` |
| `logistic_regression` | `1:4` | `1:4` | `0.638192` | `0.001192` | `0.626921` | `0.650000` |
| `random_forest` | `1:1` | `1:1` | `0.782462` | `0.000837` | `0.856289` | `0.721600` |
| `random_forest` | `1:2` | `1:2` | `0.740235` | `0.002706` | `0.771429` | `0.712400` |
| `random_forest` | `1:3` | `1:2` | `0.701038` | `0.002432` | `0.690923` | `0.712400` |
| `random_forest` | `1:4` | `1:2` | `0.668881` | `0.002767` | `0.631478` | `0.712400` |
| `svm` | `1:1` | `1:2` | `0.757637` | `0.002884` | `0.852675` | `0.682000` |
| `svm` | `1:2` | `1:2` | `0.711966` | `0.001291` | `0.745302` | `0.682000` |
| `svm` | `1:3` | `1:2` | `0.670753` | `0.000875` | `0.660554` | `0.682000` |
| `svm` | `1:4` | `1:3` | `0.640225` | `0.000856` | `0.615011` | `0.668400` |

## Test-Ratio Sensitivity

Largest F1 drops from test ratio `1:1` to test ratio `1:4`:

| Model | Train Ratio | F1 @ Test 1:1 | F1 @ Test 1:4 | F1 Drop | Precision Drop | Recall Drop |
|---|---|---:|---:|---:|---:|---:|
| `logistic_regression` | `1:3` | `0.760369` | `0.636115` | `0.124254` | `0.254987` | `0.000000` |
| `logistic_regression` | `1:1` | `0.755475` | `0.634179` | `0.121296` | `0.256985` | `0.000000` |
| `random_forest` | `1:1` | `0.782462` | `0.664034` | `0.118429` | `0.239808` | `0.000000` |
| `svm` | `1:2` | `0.757637` | `0.639351` | `0.118286` | `0.250336` | `0.000000` |
| `svm` | `1:1` | `0.754753` | `0.638317` | `0.116436` | `0.251099` | `0.000000` |

## Interpretation

Training-ratio effects are relatively small inside this grid. For example, Random Forest under fixed test ratio `1:1` differs by less than `0.01` F1 between train ratios `1:1` and `1:4`. Similar best-versus-second-best gaps are often below `0.005`.

Test-ratio effects are much larger. Moving from test ratio `1:1` to `1:4` drops F1 by roughly `0.11` to `0.12` for many train/model settings. The drop comes from precision, not recall.

Recall drop is exactly `0.0` in this derived analysis because every sampled test ratio keeps all 500 positive test pairs and changes only the number of negative test pairs. The positive examples and their scores remain the same; the evaluation distribution adds more opportunities for false positives.

## Research Use

For the final report:

- Use the fixed-test `1:8` WDC unseen result as the main robustness evaluation.
- Use this grid to show that evaluation class ratio strongly changes precision and F1.
- Avoid claiming that a train ratio is universally best from the grid alone, because best-train differences are small and depend on the fixed test ratio.
