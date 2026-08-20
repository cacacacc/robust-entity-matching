# Seen vs Unseen Baseline Comparison

Protocol: WDC Products `train_small` / `valid_small`; seen test `test_seen_000un`; unseen test `test_unseen_100un`.

| Model | Seen F1 | Unseen F1 | Unseen - Seen F1 | Seen Precision | Unseen Precision | Seen Recall | Unseen Recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| `random_forest` | `0.501589` | `0.559863` | `+0.058274` | `0.400998` | `0.469810` | `0.672400` | `0.695200` |
| `logistic_regression` | `0.487692` | `0.535862` | `+0.048169` | `0.396250` | `0.455820` | `0.634000` | `0.650000` |
| `svm` | `0.482928` | `0.529547` | `+0.046620` | `0.384246` | `0.436787` | `0.650000` | `0.672400` |

Notes:

- Thresholds were selected on the same fixed validation split.
- Seen test is an official seen diagnostic and has known development overlap; it is not a leakage-free final evaluation.
- Unseen test is the main entity-disjoint WDC evaluation used for robustness claims.
- Positive `Unseen - Seen` values mean the unseen split scored higher than the seen split under this metric.
