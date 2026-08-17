# Class-Ratio Execution Manifest

Protocol: WDC Products `train_small` / `valid_small` / `test_unseen_100un`.

Total planned tasks: `60`.
Ratios: `4`; models: `3`; seeds: `5`.
Fit allowed now: `False`.
Writes files now: `False`.

| Ratio | Model | Seeds | Train Rows | Validation Rows | Test Rows |
|---|---|---:|---:|---:|---:|
| `1:1` | `logistic_regression` | `5` | `1000` | `2500` | `4500` |
| `1:1` | `random_forest` | `5` | `1000` | `2500` | `4500` |
| `1:1` | `svm` | `5` | `1000` | `2500` | `4500` |
| `1:2` | `logistic_regression` | `5` | `1500` | `2500` | `4500` |
| `1:2` | `random_forest` | `5` | `1500` | `2500` | `4500` |
| `1:2` | `svm` | `5` | `1500` | `2500` | `4500` |
| `1:3` | `logistic_regression` | `5` | `2000` | `2500` | `4500` |
| `1:3` | `random_forest` | `5` | `2000` | `2500` | `4500` |
| `1:3` | `svm` | `5` | `2000` | `2500` | `4500` |
| `1:4` | `logistic_regression` | `5` | `2500` | `2500` | `4500` |
| `1:4` | `random_forest` | `5` | `2500` | `2500` | `4500` |
| `1:4` | `svm` | `5` | `2500` | `2500` | `4500` |

Notes:

- This manifest is a dry execution preview, not a training result.
- Output paths are planned paths only.
- The current protocol config has `fit_allowed: false`.
