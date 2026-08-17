# Phase 3 Class-Ratio Protocol Comparison

Date: 2026-08-17

## Scope

This document compares two completed class-ratio protocols:

- Fixed-test protocol: `configs/experiments/wdc_class_ratio_stress_fit.json`
- Matched train/test protocol: `configs/experiments/wdc_class_ratio_matched_train_test_fit.json`

Both protocols use:

- Dataset: WDC Products `80pair`
- Train split: `train_small`
- Validation split: `valid_small`
- Test source split: `test_unseen_100un`
- Models: `logistic_regression`, `random_forest`, `svm`
- Seeds: `13`, `29`, `47`, `71`, `101`
- Threshold selection: validation F1 only

## Comparison Artifacts

- CSV: `reports/class_ratio_protocol_comparison.csv`
- Markdown: `reports/class_ratio_protocol_comparison.md`

Export command:

```powershell
python scripts/export_class_ratio_protocol_comparison.py
```

## Protocol Difference

The fixed-test protocol changes only the training ratio. Test evaluation always uses the original `test_unseen_100un` distribution:

- Test matches: `500`
- Test non-matches: `4000`
- Test ratio: `1:8`

The matched train/test protocol changes both training and test ratios:

| Ratio | Matched Test Matches | Matched Test Non-Matches |
|---|---:|---:|
| `1:1` | `500` | `500` |
| `1:2` | `500` | `1000` |
| `1:3` | `500` | `1500` |
| `1:4` | `500` | `2000` |

## Key Comparison

| Ratio | Model | Fixed F1 | Matched F1 | Delta F1 | Fixed Precision | Matched Precision | Fixed Recall | Matched Recall |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `1:1` | `logistic_regression` | `0.522357` | `0.755475` | `+0.233117` | `0.425679` | `0.853780` | `0.677600` | `0.677600` |
| `1:1` | `random_forest` | `0.546466` | `0.782462` | `+0.235996` | `0.441004` | `0.856289` | `0.721600` | `0.721600` |
| `1:1` | `svm` | `0.528704` | `0.754753` | `+0.226048` | `0.434862` | `0.857236` | `0.674400` | `0.674400` |
| `1:2` | `random_forest` | `0.557584` | `0.740235` | `+0.182651` | `0.459144` | `0.771429` | `0.712400` | `0.712400` |
| `1:4` | `random_forest` | `0.559863` | `0.666114` | `+0.106251` | `0.469810` | `0.640845` | `0.695200` | `0.695200` |

## Interpretation

The matched train/test protocol increases F1 because it reduces the number of test non-matches. This mainly raises precision. Recall is unchanged in the comparison table because the matched protocol keeps all 500 positive test pairs and samples only negative test pairs.

Therefore:

- The fixed-test protocol is the main evidence for the training class-ratio question.
- The matched train/test protocol is a diagnostic showing metric sensitivity to evaluation class distribution.
- The two protocols should be reported side by side, not merged into one leaderboard.

## Current Conclusion

Under the fixed-test protocol, Random Forest at `1:4` is the strongest mean-F1 setting. Under the matched train/test protocol, Random Forest at `1:1` is strongest, but that result is partly explained by the easier balanced evaluation distribution.
