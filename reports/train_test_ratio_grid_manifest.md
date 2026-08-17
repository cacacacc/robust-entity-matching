# Train/Test Ratio Grid Manifest

Protocol: WDC Products `train_small` / `valid_small` / `test_unseen_100un`.

Planned test-evaluation rows: `240`.
Planned fit tasks if optimized by train ratio/model/seed: `60`.
Train ratios: `1:1, 1:2, 1:3, 1:4`.
Test ratios: `1:1, 1:2, 1:3, 1:4`.
Models: `logistic_regression, random_forest, svm`.
Seeds: `13, 29, 47, 71, 101`.
Fit allowed now: `False`.
Writes files now: `False`.

| Train Ratio | Test Ratio | Model | Seeds | Train Rows | Test Rows |
|---|---|---|---:|---:|---:|
| `1:1` | `1:1` | `logistic_regression` | `5` | `1000` | `1000` |
| `1:1` | `1:1` | `random_forest` | `5` | `1000` | `1000` |
| `1:1` | `1:1` | `svm` | `5` | `1000` | `1000` |
| `1:1` | `1:2` | `logistic_regression` | `5` | `1000` | `1500` |
| `1:1` | `1:2` | `random_forest` | `5` | `1000` | `1500` |
| `1:1` | `1:2` | `svm` | `5` | `1000` | `1500` |
| `1:1` | `1:3` | `logistic_regression` | `5` | `1000` | `2000` |
| `1:1` | `1:3` | `random_forest` | `5` | `1000` | `2000` |
| `1:1` | `1:3` | `svm` | `5` | `1000` | `2000` |
| `1:1` | `1:4` | `logistic_regression` | `5` | `1000` | `2500` |
| `1:1` | `1:4` | `random_forest` | `5` | `1000` | `2500` |
| `1:1` | `1:4` | `svm` | `5` | `1000` | `2500` |
| `1:2` | `1:1` | `logistic_regression` | `5` | `1500` | `1000` |
| `1:2` | `1:1` | `random_forest` | `5` | `1500` | `1000` |
| `1:2` | `1:1` | `svm` | `5` | `1500` | `1000` |
| `1:2` | `1:2` | `logistic_regression` | `5` | `1500` | `1500` |
| `1:2` | `1:2` | `random_forest` | `5` | `1500` | `1500` |
| `1:2` | `1:2` | `svm` | `5` | `1500` | `1500` |
| `1:2` | `1:3` | `logistic_regression` | `5` | `1500` | `2000` |
| `1:2` | `1:3` | `random_forest` | `5` | `1500` | `2000` |
| `1:2` | `1:3` | `svm` | `5` | `1500` | `2000` |
| `1:2` | `1:4` | `logistic_regression` | `5` | `1500` | `2500` |
| `1:2` | `1:4` | `random_forest` | `5` | `1500` | `2500` |
| `1:2` | `1:4` | `svm` | `5` | `1500` | `2500` |
| `1:3` | `1:1` | `logistic_regression` | `5` | `2000` | `1000` |
| `1:3` | `1:1` | `random_forest` | `5` | `2000` | `1000` |
| `1:3` | `1:1` | `svm` | `5` | `2000` | `1000` |
| `1:3` | `1:2` | `logistic_regression` | `5` | `2000` | `1500` |
| `1:3` | `1:2` | `random_forest` | `5` | `2000` | `1500` |
| `1:3` | `1:2` | `svm` | `5` | `2000` | `1500` |
| `1:3` | `1:3` | `logistic_regression` | `5` | `2000` | `2000` |
| `1:3` | `1:3` | `random_forest` | `5` | `2000` | `2000` |
| `1:3` | `1:3` | `svm` | `5` | `2000` | `2000` |
| `1:3` | `1:4` | `logistic_regression` | `5` | `2000` | `2500` |
| `1:3` | `1:4` | `random_forest` | `5` | `2000` | `2500` |
| `1:3` | `1:4` | `svm` | `5` | `2000` | `2500` |
| `1:4` | `1:1` | `logistic_regression` | `5` | `2500` | `1000` |
| `1:4` | `1:1` | `random_forest` | `5` | `2500` | `1000` |
| `1:4` | `1:1` | `svm` | `5` | `2500` | `1000` |
| `1:4` | `1:2` | `logistic_regression` | `5` | `2500` | `1500` |
| `1:4` | `1:2` | `random_forest` | `5` | `2500` | `1500` |
| `1:4` | `1:2` | `svm` | `5` | `2500` | `1500` |
| `1:4` | `1:3` | `logistic_regression` | `5` | `2500` | `2000` |
| `1:4` | `1:3` | `random_forest` | `5` | `2500` | `2000` |
| `1:4` | `1:3` | `svm` | `5` | `2500` | `2000` |
| `1:4` | `1:4` | `logistic_regression` | `5` | `2500` | `2500` |
| `1:4` | `1:4` | `random_forest` | `5` | `2500` | `2500` |
| `1:4` | `1:4` | `svm` | `5` | `2500` | `2500` |

Notes:

- This is a dry execution manifest, not a training result.
- Validation remains fixed for threshold selection.
- Test negatives are planned as seeded samples from `test_unseen_100un`.
- No sampled train/test tables are written in this protocol-only step.
