# Class-Ratio Stress-Test Results

Protocol: WDC Products `train_small` / `valid_small` / `test_unseen_100un`.

| Rank | Ratio | Model | Test F1 Mean | Test F1 Std | Precision Mean | Recall Mean |
|---:|---|---|---:|---:|---:|---:|
| 1 | `1:4` | `random_forest` | `0.559863` | `0.003094` | `0.469810` | `0.695200` |
| 2 | `1:2` | `random_forest` | `0.557584` | `0.009709` | `0.459144` | `0.712400` |
| 3 | `1:3` | `random_forest` | `0.549993` | `0.006857` | `0.453545` | `0.704000` |
| 4 | `1:1` | `random_forest` | `0.546466` | `0.013329` | `0.441004` | `0.721600` |
| 5 | `1:4` | `logistic_regression` | `0.535862` | `0.000000` | `0.455820` | `0.650000` |
| 6 | `1:3` | `svm` | `0.530953` | `0.004001` | `0.440641` | `0.668400` |
| 7 | `1:4` | `svm` | `0.529547` | `0.002328` | `0.436787` | `0.672400` |
| 8 | `1:1` | `svm` | `0.528704` | `0.004190` | `0.434862` | `0.674400` |
| 9 | `1:2` | `logistic_regression` | `0.528528` | `0.012338` | `0.436280` | `0.674000` |
| 10 | `1:2` | `svm` | `0.527150` | `0.005530` | `0.429838` | `0.682000` |
| 11 | `1:1` | `logistic_regression` | `0.522357` | `0.009290` | `0.425679` | `0.677600` |
| 12 | `1:3` | `logistic_regression` | `0.521459` | `0.007166` | `0.418892` | `0.692000` |

Notes:

- Thresholds were selected on validation only.
- Test metrics were computed on fixed `test_unseen_100un`.
- Raw prediction artifacts are local generated files under ignored `results/`.
