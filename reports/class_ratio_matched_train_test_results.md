# Matched Train/Test Class-Ratio Results

Protocol: WDC Products `train_small` / `valid_small` / `test_unseen_100un`.

| Rank | Ratio | Model | Test F1 Mean | Test F1 Std | Precision Mean | Recall Mean |
|---:|---|---|---:|---:|---:|---:|
| 1 | `1:1` | `random_forest` | `0.782462` | `0.008184` | `0.856289` | `0.721600` |
| 2 | `1:1` | `logistic_regression` | `0.755475` | `0.013288` | `0.853780` | `0.677600` |
| 3 | `1:1` | `svm` | `0.754753` | `0.011150` | `0.857236` | `0.674400` |
| 4 | `1:2` | `random_forest` | `0.740235` | `0.014247` | `0.771429` | `0.712400` |
| 5 | `1:2` | `svm` | `0.711966` | `0.005597` | `0.745302` | `0.682000` |
| 6 | `1:2` | `logistic_regression` | `0.707439` | `0.006089` | `0.746344` | `0.674000` |
| 7 | `1:3` | `random_forest` | `0.695480` | `0.010190` | `0.691462` | `0.704000` |
| 8 | `1:3` | `svm` | `0.669844` | `0.005783` | `0.672104` | `0.668400` |
| 9 | `1:3` | `logistic_regression` | `0.669753` | `0.007146` | `0.649443` | `0.692000` |
| 10 | `1:4` | `random_forest` | `0.666114` | `0.014283` | `0.640845` | `0.695200` |
| 11 | `1:4` | `svm` | `0.639368` | `0.007754` | `0.609604` | `0.672400` |
| 12 | `1:4` | `logistic_regression` | `0.638192` | `0.007009` | `0.626921` | `0.650000` |

Notes:

- Thresholds were selected on validation only.
- Test negatives were sampled from `test_unseen_100un` so each test matrix matches the corresponding training ratio.
- Raw prediction artifacts are local generated files under ignored `results/`.
