# Phase 3 Seen/Unseen Difficulty Analysis

Date: 2026-08-20

## 本轮目的

上一轮 seen/unseen baseline comparison 出现了一个反直觉结果：

- `test_unseen_100un` 的 F1 高于 `test_seen_000un`；
- 这个现象在 Logistic Regression、Random Forest、SVM 上都出现；
- 直觉上很多人会以为 unseen entities 一定更难，但实验结果并不支持这个简单说法。

本轮不重新训练模型，只分析已经生成的 raw predictions 和 processed feature tables，检查 seen split 为什么可能更难。

## 分析对象

- Dataset: WDC Products `80pair`
- Train split: `train_small`
- Validation split: `valid_small`
- Seen test split: `test_seen_000un`
- Unseen test split: `test_unseen_100un`
- Model inspected: `random_forest`
- Seed inspected: `13`
- Threshold: validation-selected threshold `0.32`

注意：seed `13` 只用于定性/描述性错误剖析，不用于模型选择。

## 新增分析脚本

```powershell
python scripts/export_seen_unseen_difficulty_analysis.py
```

输出文件：

- `reports/seen_unseen_split_difficulty.csv`
- `reports/seen_unseen_feature_difficulty.csv`
- `reports/seen_unseen_difficulty_analysis.md`

## Split-Level Findings

| Split | Positives | Negatives | Hard Negatives | TP | FP | TN | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `test_seen_000un` | `500` | `4000` | `3000` | `350` | `589` | `3411` | `150` | `0.372737` | `0.700000` | `0.486449` |
| `test_unseen_100un` | `500` | `4000` | `3000` | `369` | `454` | `3546` | `131` | `0.448360` | `0.738000` | `0.557823` |

关键点：

- 两个 test split 的 label ratio 完全相同：`500` positives / `4000` negatives。
- 两个 test split 的 hard-negative 总数也相同：`3000`。
- seen split 多出 `135` 个 false positives。
- seen split 多出 `19` 个 false negatives。
- 所以 seen F1 更低，不是因为它的正负比例更差，而是因为它在当前特征和阈值下产生了更多错误，尤其是 false positives。

## Feature-Level Findings

| Split | Group | Title Jaccard | Title Numeric | Combined Jaccard | Combined Numeric |
|---|---|---:|---:|---:|---:|
| `test_seen_000un` | negative | `0.161130` | `0.204390` | `0.092758` | `0.182242` |
| `test_unseen_100un` | negative | `0.160965` | `0.164985` | `0.097855` | `0.162336` |
| `test_seen_000un` | false_positive | `0.302869` | `0.712165` | `0.162315` | `0.501189` |
| `test_unseen_100un` | false_positive | `0.340815` | `0.701951` | `0.178465` | `0.515029` |
| `test_seen_000un` | positive | `0.280906` | `0.691657` | `0.164928` | `0.523338` |
| `test_unseen_100un` | positive | `0.347611` | `0.701660` | `0.195034` | `0.533918` |

解释：

- seen split 的 negative pairs 在 numeric overlap 上更高，尤其是 title numeric 和 combined numeric。这会让部分 non-match 看起来更像 match。
- false positives 在两个 split 里都高度像 positives，说明模型主要被 hard/non-match 相似样本迷惑。
- seen positives 的 title/combined textual similarity 低于 unseen positives，这可能让 seen split 的部分真实 match 更难被模型识别。

## 研究解释

这个结果提醒我们：`seen/unseen` 描述的是 entity overlap，不是直接的 easy/hard 标签。

换句话说：

- seen entity 不一定更容易；
- unseen entity 不一定更难；
- split 的 hard-negative 组成、字段相似度分布、threshold 附近样本密度都会影响结果；
- 只报告 F1 而不报告 split composition，容易把实验现象解释错。

## 对最终报告的写法

最终报告中应这样表述：

- `test_unseen_100un` 是主要 robustness evaluation，因为它与 training entities disjoint。
- `test_seen_000un` 是 official diagnostic split，但存在 entity overlap 和少量 validation record overlap caveat。
- 当前 baseline 结果显示 unseen split 反而更高，这不是矛盾，而是说明 official WDC split difficulty 不只由 entity seen/unseen 决定。
- 该现象支持本项目的核心动机：entity matching 的 robustness evaluation 必须同时报告 class ratio、split construction、hard negatives 和 leakage/entity overlap。

## Verification

Focused test:

```powershell
python -m unittest tests.test_seen_unseen_difficulty
```

Result:

- `Ran 2 tests`
- `OK`

## All-Seed Stability Check

为了确认 RF seed `13` 的观察不是偶然现象，本轮进一步聚合了三种 baseline model 的全部五个 seeds：

- Models: `logistic_regression`, `random_forest`, `svm`
- Seeds: `13`, `29`, `47`, `71`, `101`
- Total model-seed rows: `15`

导出命令：

```powershell
python scripts/export_seen_unseen_error_profile.py
```

输出文件：

- `reports/seen_unseen_error_profile_by_seed.csv`
- `reports/seen_unseen_error_profile_by_model.csv`
- `reports/seen_unseen_error_profile.md`

### Model-Level Stability

| Model | Seeds | Seen FP Mean | Unseen FP Mean | Seen-Unseen FP Mean | Seeds Seen FP Higher | Unseen-Seen Precision Mean | Unseen-Seen F1 Mean | Seeds Unseen F1 Higher |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `logistic_regression` | `5` | `483.000000` | `388.000000` | `95.000000` | `5` | `0.059570` | `0.048169` | `5` |
| `random_forest` | `5` | `505.600000` | `394.400000` | `111.200000` | `5` | `0.068812` | `0.058274` | `5` |
| `svm` | `5` | `521.000000` | `433.600000` | `87.400000` | `5` | `0.052541` | `0.046620` | `5` |

### Interpretation Update

这个 all-seed profile 加强了前面的解释：

- seen split 不是只在 RF seed `13` 上更低；
- 对三个 baseline model，五个 seeds 全部满足 `seen FP > unseen FP`；
- 对三个 baseline model，五个 seeds 全部满足 `unseen F1 > seen F1`；
- 因此，seen split 的 lower F1 是稳定的 error-profile pattern，主要表现为更多 false positives 和更低 precision。

这仍然不是 causal proof。我们不能说“实体 seen 导致更多 false positives”。更严谨的说法是：

> 在当前 WDC official splits、传统 baseline、固定 validation threshold 下，seen diagnostic split 的 non-match pairs 更容易被模型误判为 match；因此 seen F1 低于 unseen F1。

