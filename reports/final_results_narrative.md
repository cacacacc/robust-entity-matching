# Final Results Narrative Draft

This draft summarizes the completed Phase 3 experiments for the WDC Products `80pair` benchmark. It is report-ready prose, but it should still be reviewed before being used as the final technical report.

## Experimental Setting

All primary experiments use WDC Products `80pair` with `train_small` for model fitting, `valid_small` for threshold selection, and WDC official test variants for evaluation. Thresholds are selected on validation F1 only. Test splits are used for reporting, not for model or threshold selection. Each main experiment reports five seeds: `13`, `29`, `47`, `71`, and `101`.

The main robustness split is `test_unseen_100un`, which is pair-, record-, and entity-disjoint from both `train_small` and `valid_small` according to the local split guard. The official seen split, `test_seen_000un`, is used only as a diagnostic split because it has entity overlap with the development data and a small validation record-overlap caveat.

## Baseline Performance

Under the fixed unseen-entity protocol, Random Forest achieved the strongest traditional baseline performance:

| Model | Test F1 Mean | Test F1 Std | Precision Mean | Recall Mean |
|---|---:|---:|---:|---:|
| `random_forest` | `0.559863` | `0.003094` | `0.469810` | `0.695200` |
| `logistic_regression` | `0.535862` | `0.000000` | `0.455820` | `0.650000` |
| `svm` | `0.529547` | `0.002328` | `0.436787` | `0.672400` |

The results show that all three traditional baselines recover a substantial portion of true matches, but precision remains lower than recall. This suggests that false positives are a central source of error under the current similarity-feature representation and validation-selected thresholds.

## Class-Ratio Findings

The fixed-test class-ratio experiment changes the training match/non-match ratio while keeping the unseen test distribution fixed. Under this protocol, changing the training ratio had a measurable but relatively modest effect compared with changing the evaluation ratio.

The full train/test ratio grid makes the distribution effect clearer. Holding the training ratio fixed and changing the test ratio from `1:1` to `1:4` caused F1 drops around `0.11` to `0.12` in several settings. These drops were driven by precision, while recall remained unchanged because the sampled test-ratio slices retained all positive test pairs and varied only the number of negatives.

Representative rows:

| Model | Train Ratio | F1 @ Test 1:1 | F1 @ Test 1:4 | F1 Drop | Precision Drop | Recall Drop |
|---|---|---:|---:|---:|---:|---:|
| `logistic_regression` | `1:3` | `0.760369` | `0.636115` | `0.124254` | `0.254987` | `0.000000` |
| `random_forest` | `1:1` | `0.782462` | `0.664034` | `0.118429` | `0.239808` | `0.000000` |
| `svm` | `1:2` | `0.757637` | `0.639351` | `0.118286` | `0.250336` | `0.000000` |

These results indicate that evaluation class ratio can substantially change reported F1 even when the fitted model is unchanged. Therefore, class-ratio reporting is necessary for interpreting entity-matching results.

## Seen vs Unseen Diagnostic

The official seen/unseen comparison produced a counterintuitive but stable result: the unseen split scored higher than the seen diagnostic split for all three traditional baselines.

| Model | Seen F1 | Unseen F1 | Unseen - Seen F1 | Seen Precision | Unseen Precision |
|---|---:|---:|---:|---:|---:|
| `random_forest` | `0.501589` | `0.559863` | `+0.058274` | `0.400998` | `0.469810` |
| `logistic_regression` | `0.487692` | `0.535862` | `+0.048169` | `0.396250` | `0.455820` |
| `svm` | `0.482928` | `0.529547` | `+0.046620` | `0.384246` | `0.436787` |

An all-seed error-profile analysis found that all `15/15` model-seed rows had more false positives on the seen split than on the unseen split, and all `15/15` rows had higher F1 on the unseen split. The model-level averages were:

| Model | Seen FP Mean | Unseen FP Mean | Seen - Unseen FP Mean | Unseen - Seen F1 Mean |
|---|---:|---:|---:|---:|
| `logistic_regression` | `483.000000` | `388.000000` | `95.000000` | `0.048169` |
| `random_forest` | `505.600000` | `394.400000` | `111.200000` | `0.058274` |
| `svm` | `521.000000` | `433.600000` | `87.400000` | `0.046620` |

This result should not be interpreted as evidence that unseen entities are inherently easier. Instead, it shows that seen/unseen status is not equivalent to split difficulty. In this benchmark configuration, the seen diagnostic split produced more false positives under the selected thresholds, which lowered precision and F1.

## Main Interpretation

The completed experiments support the central claim that entity-matching performance is shaped by both modeling choices and evaluation protocol. The model family matters, but reported F1 also depends strongly on class ratio, split construction, hard-negative composition, and the selected threshold protocol.

The strongest result is not simply that Random Forest is the best baseline. The more important result is that evaluation distribution and split composition can change the interpretation of model performance. In particular, matched or sampled test ratios can inflate F1 relative to the full imbalanced unseen test distribution, and official seen/unseen split labels do not by themselves determine difficulty.

## Limitations

These experiments use traditional similarity features and traditional classifiers only. The results should not be generalized to neural encoders or large language models. The analysis is also limited to WDC Products `80pair`; additional datasets would be needed to claim broader generality. Finally, the seen split is an official diagnostic split with known development overlap, so it should not be treated as a leakage-free final evaluation.

## Reportable Claim

A conservative reportable claim is:

> On WDC Products `80pair`, traditional entity-matching baselines are sensitive to evaluation class ratio and split composition. Under fixed unseen-entity evaluation, Random Forest performs best among the tested traditional models. However, evaluation class ratio has a larger effect on F1 than training class ratio, and the official seen diagnostic split produces more false positives than the unseen split across all inspected model-seed runs.

