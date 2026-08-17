# Class-Ratio Stress-Test Plan

Protocol: WDC Products `train_small` / `valid_small` / `test_unseen_100un`.

| Ratio | Match Count | Non-Match Count | Total Train Rows | Seeds | Uses All Negatives |
|---|---:|---:|---:|---:|---|
| `1:1` | `500` | `500` | `1000` | `5` | `False` |
| `1:2` | `500` | `1000` | `1500` | `5` | `False` |
| `1:3` | `500` | `1500` | `2000` | `5` | `False` |
| `1:4` | `500` | `2000` | `2500` | `5` | `True` |

Fixed evaluation splits:

- Validation: `valid_small`, rows `2500`, labels `{'0': 2000, '1': 500}`.
- Test: `test_unseen_100un`, rows `4500`, labels `{'0': 4000, '1': 500}`.

Notes:

- Each ratio uses all 500 available training matches.
- Non-matches are sampled without replacement using the experiment seed.
- The preview writes no sampled training tables and runs no model fitting.
