# Seen/Unseen Split Difficulty Analysis

本报告只分析已经生成的 raw predictions 和 processed feature tables；没有重新训练模型，也没有使用 test set 做模型选择。

分析对象：Random Forest，seed `13`。这个 seed 只用于定性/描述性错误剖析。

## Split Summary

| Split | Positives | Negatives | Hard Negatives | TP | FP | TN | FN | Precision | Recall | F1 | FP Rate | Near Threshold Rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `test_seen_000un` | `500` | `4000` | `3000` | `350` | `589` | `3411` | `150` | `0.372737` | `0.700000` | `0.486449` | `0.147250` | `0.068444` |
| `test_unseen_100un` | `500` | `4000` | `3000` | `369` | `454` | `3546` | `131` | `0.448360` | `0.738000` | `0.557823` | `0.113500` | `0.058667` |

## Key Interpretation

- 两个 test split 的标签规模相同：都是 `500` 个 match 和 `4000` 个 non-match。
- 两个 split 的 hard-negative 总数也相同：都是 `3000`。
- Random Forest 在 seen split 上多产生 `135` 个 false positives，多产生 `19` 个 false negatives。
- unseen 相比 seen 的 precision 高 `0.075623`，F1 高 `0.071374`。
- false positives 中 hard negatives 的比例：seen `0.994907`，unseen `0.997797`。

这说明当前结果不能简单解释成“seen 一定更容易，unseen 一定更难”。在这个 WDC 官方 split 上，seen 的错误主要来自更多 non-match 被模型判成 match，也就是 precision 被 false positives 拉低。

## Feature Means By Group

下面只展示对解释最有用的几个相似度特征。数值越高，表示两个商品在对应字段上越像。

| Split | Group | Count | Title Jaccard | Title Numeric | Combined Jaccard | Combined Numeric | Combined Edit |
|---|---|---:|---:|---:|---:|---:|---:|
| `test_seen_000un` | `negative` | `4000` | `0.161130` | `0.204390` | `0.092758` | `0.182242` | `0.200768` |
| `test_seen_000un` | `false_positive` | `589` | `0.302869` | `0.712165` | `0.162315` | `0.501189` | `0.252497` |
| `test_seen_000un` | `positive` | `500` | `0.280906` | `0.691657` | `0.164928` | `0.523338` | `0.243572` |
| `test_seen_000un` | `false_negative` | `150` | `0.225489` | `0.252889` | `0.146129` | `0.250131` | `0.232677` |
| `test_unseen_100un` | `negative` | `4000` | `0.160965` | `0.164985` | `0.097855` | `0.162336` | `0.206683` |
| `test_unseen_100un` | `false_positive` | `454` | `0.340815` | `0.701951` | `0.178465` | `0.515029` | `0.260252` |
| `test_unseen_100un` | `positive` | `500` | `0.347611` | `0.701660` | `0.195034` | `0.533918` | `0.264730` |
| `test_unseen_100un` | `false_negative` | `131` | `0.292312` | `0.210596` | `0.185316` | `0.301851` | `0.273534` |

## What This Means For The Project

- `seen/unseen` 是实体重叠维度，不等价于“容易/困难”维度。
- `class ratio` 和 `hard negative composition` 仍然需要单独报告；否则 F1/precision 的变化会被误读。
- 最终论文中应把 seen 结果写成 diagnostic result，把 unseen 结果保留为主要 robustness result。
