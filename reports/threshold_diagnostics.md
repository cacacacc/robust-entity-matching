# Threshold Diagnostics

Protocol: WDC Products `train_small` / `valid_small` / `test_unseen_100un`.

| Rank | Model | Test AP Mean | Test AP Std | Test Grid PR-AUC Mean | F1 Mean @ Selected Threshold | Precision Mean | Recall Mean |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | `random_forest` | `0.506321` | `0.004498` | `0.505652` | `0.559863` | `0.469810` | `0.695200` |
| 2 | `svm` | `0.498283` | `0.000027` | `0.497242` | `0.529547` | `0.436787` | `0.672400` |
| 3 | `logistic_regression` | `0.466724` | `0.000000` | `0.465624` | `0.535862` | `0.455820` | `0.650000` |

Notes:

- AP means ranking average precision computed from raw prediction scores.
- Grid PR-AUC is a coarse 0.00-1.00 threshold-grid approximation, mainly for threshold-shape diagnostics.
- Selected-threshold metrics still use thresholds chosen on validation only.
- Test scores are used here for post-run reporting, not for model or threshold selection.
