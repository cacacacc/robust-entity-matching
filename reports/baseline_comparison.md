# Baseline Comparison

Protocol: WDC Products `train_small` / `valid_small` / `test_unseen_100un`.

| Rank | Model | Test F1 Mean | Test F1 Std | Precision Mean | Recall Mean | Thresholds |
|---:|---|---:|---:|---:|---:|---|
| 1 | `random_forest` | `0.559863` | `0.003094` | `0.469810` | `0.695200` | `0.32, 0.37, 0.4, 0.38, 0.33` |
| 2 | `logistic_regression` | `0.535862` | `0.000000` | `0.455820` | `0.650000` | `0.66, 0.66, 0.66, 0.66, 0.66` |
| 3 | `svm` | `0.529547` | `0.002328` | `0.436787` | `0.672400` | `0.31, 0.34, 0.32, 0.34, 0.34` |

Notes:

- Thresholds were selected on validation only.
- Test metrics were computed on `test_unseen_100un` only.
- Raw prediction artifacts are local generated files under ignored `results/`.
