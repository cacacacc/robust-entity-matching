# Fixed-Test vs Matched Train/Test Class-Ratio Comparison

Protocol: WDC Products `train_small` / `valid_small` / `test_unseen_100un`.

| Ratio | Model | Fixed F1 | Matched F1 | Delta F1 | Fixed Precision | Matched Precision | Fixed Recall | Matched Recall |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `1:1` | `logistic_regression` | `0.522357` | `0.755475` | `+0.233117` | `0.425679` | `0.853780` | `0.677600` | `0.677600` |
| `1:1` | `random_forest` | `0.546466` | `0.782462` | `+0.235996` | `0.441004` | `0.856289` | `0.721600` | `0.721600` |
| `1:1` | `svm` | `0.528704` | `0.754753` | `+0.226048` | `0.434862` | `0.857236` | `0.674400` | `0.674400` |
| `1:2` | `logistic_regression` | `0.528528` | `0.707439` | `+0.178911` | `0.436280` | `0.746344` | `0.674000` | `0.674000` |
| `1:2` | `random_forest` | `0.557584` | `0.740235` | `+0.182651` | `0.459144` | `0.771429` | `0.712400` | `0.712400` |
| `1:2` | `svm` | `0.527150` | `0.711966` | `+0.184816` | `0.429838` | `0.745302` | `0.682000` | `0.682000` |
| `1:3` | `logistic_regression` | `0.521459` | `0.669753` | `+0.148294` | `0.418892` | `0.649443` | `0.692000` | `0.692000` |
| `1:3` | `random_forest` | `0.549993` | `0.695480` | `+0.145487` | `0.453545` | `0.691462` | `0.704000` | `0.704000` |
| `1:3` | `svm` | `0.530953` | `0.669844` | `+0.138890` | `0.440641` | `0.672104` | `0.668400` | `0.668400` |
| `1:4` | `logistic_regression` | `0.535862` | `0.638192` | `+0.102331` | `0.455820` | `0.626921` | `0.650000` | `0.650000` |
| `1:4` | `random_forest` | `0.559863` | `0.666114` | `+0.106251` | `0.469810` | `0.640845` | `0.695200` | `0.695200` |
| `1:4` | `svm` | `0.529547` | `0.639368` | `+0.109821` | `0.436787` | `0.609604` | `0.672400` | `0.672400` |

Notes:

- Fixed-test results keep the original `test_unseen_100un` ratio of 500 matches and 4000 non-matches.
- Matched train/test results sample test negatives so the test ratio matches the corresponding training ratio.
- Thresholds were selected on the same fixed validation split in both protocols.
- Positive deltas mainly reflect evaluation-distribution changes and must not be read as pure training-ratio improvements.
