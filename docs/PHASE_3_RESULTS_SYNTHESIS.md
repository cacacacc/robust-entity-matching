# Phase 3 Results Synthesis

Date: 2026-08-20

## 本轮目的

本文件把 Phase 3 已完成的实验结果合并成一个清晰的研究叙事，方便后续写 technical report、准备面试讲解、决定 Phase 4 要补什么。

本轮不重新训练模型，不改变 research questions，不用 test set 做模型选择。

## 已完成实验地图

Phase 3 现在有四组主要证据：

| Evidence Block | Main Question | Primary Artifacts |
|---|---|---|
| Traditional baseline | 在固定 unseen test split 上，传统模型表现如何？ | `reports/baseline_comparison.md` |
| Class-ratio fixed-test | 只改变 training ratio，固定 unseen test distribution，会发生什么？ | `reports/class_ratio_results.md` |
| Train/test ratio grid | training ratio 和 evaluation ratio 谁影响更大？ | `reports/train_test_ratio_grid_analysis.md` |
| Seen/unseen diagnostic | unseen-entity split 是否一定更难？ | `reports/seen_vs_unseen_comparison.md`, `reports/seen_unseen_error_profile.md` |

## Result 1: Traditional Baselines

固定协议：

- Dataset: WDC Products `80pair`
- Train split: `train_small`
- Validation split: `valid_small`
- Test split: `test_unseen_100un`
- Threshold: validation F1 selected
- Seeds: `13`, `29`, `47`, `71`, `101`

主要结果：

| Rank | Model | Test F1 Mean | Test F1 Std | Precision Mean | Recall Mean |
|---:|---|---:|---:|---:|---:|
| 1 | `random_forest` | `0.559863` | `0.003094` | `0.469810` | `0.695200` |
| 2 | `logistic_regression` | `0.535862` | `0.000000` | `0.455820` | `0.650000` |
| 3 | `svm` | `0.529547` | `0.002328` | `0.436787` | `0.672400` |

解释：

- Random Forest 是当前 fixed unseen baseline 中最强的传统模型。
- 三个模型的 recall 都高于 precision，说明主要问题不是完全找不到 match，而是容易把一些 non-match 判成 match。
- Logistic Regression 的 std 为 `0.000000`，是因为当前实现和数据/阈值下结果在五个 seeds 上一致；这不是泛化稳定性的充分证明。

## Result 2: Training Class Ratio Has Limited Effect Under Fixed Test Distribution

固定测试协议下，训练 ratio 从 `1:1` 到 `1:4` 变化，但 test split 仍然使用完整 `test_unseen_100un`。

固定测试下的结论：

- Random Forest 仍然整体最强。
- 固定 unseen test distribution 下，training class ratio 的影响存在，但不像 evaluation class ratio 那样巨大。
- `1:4` 对应原始训练分布，Random Forest F1 为 `0.559863`。
- `1:1` training ratio 下 Random Forest F1 为 `0.546466`，没有超过 `1:4`。

因此，不能简单说“训练集越 balanced 越好”。在这个数据和特征设置下，training ratio 的效果比较温和，而且依赖模型。

## Result 3: Evaluation Class Ratio Strongly Changes F1 And Precision

matched train/test 和 full train/test grid 显示：当 test ratio 从 `1:1` 变到 `1:4`，F1 明显下降，主要原因是 precision 下降。

最清楚的证据来自 full train/test ratio grid：

| Model | Train Ratio | F1 @ Test 1:1 | F1 @ Test 1:4 | F1 Drop | Precision Drop | Recall Drop |
|---|---|---:|---:|---:|---:|---:|
| `logistic_regression` | `1:3` | `0.760369` | `0.636115` | `0.124254` | `0.254987` | `0.000000` |
| `random_forest` | `1:1` | `0.782462` | `0.664034` | `0.118429` | `0.239808` | `0.000000` |
| `svm` | `1:2` | `0.757637` | `0.639351` | `0.118286` | `0.250336` | `0.000000` |

解释：

- 这里 recall drop 为 `0.000000`，不是因为模型完全不受影响，而是因为 test-ratio sampling 保留了所有 positive pairs，只改变 negative count。
- 当 test negatives 增多时，false positives 的绝对数量和 precision penalty 变得更明显。
- 所以 F1 对 evaluation class distribution 很敏感。

这个结果直接支持项目主题：entity matching 实验不能只报告一个 F1，还要报告 evaluation class ratio。

## Result 4: Unseen Split Scored Higher Than Seen Split

seen/unseen diagnostic 的反直觉结果：

| Model | Seen F1 | Unseen F1 | Unseen - Seen F1 | Seen Precision | Unseen Precision |
|---|---:|---:|---:|---:|---:|
| `random_forest` | `0.501589` | `0.559863` | `+0.058274` | `0.400998` | `0.469810` |
| `logistic_regression` | `0.487692` | `0.535862` | `+0.048169` | `0.396250` | `0.455820` |
| `svm` | `0.482928` | `0.529547` | `+0.046620` | `0.384246` | `0.436787` |

all-seed error profile 进一步确认：

- `15/15` model-seed rows 满足 `seen FP > unseen FP`。
- `15/15` model-seed rows 满足 `unseen F1 > seen F1`。

解释：

- `seen/unseen` 描述的是 entity overlap，不是直接的 easy/hard 标签。
- 两个 test split 的 label counts 相同，hard-negative 总数也相同。
- seen split 的 lower F1 主要来自更多 false positives 和更低 precision。
- 因此，不能把实验写成“unseen entities 一定更难”。更严谨的表述是：在当前 WDC official splits 和传统 baseline 设置下，official seen diagnostic split 对这些模型更容易产生 false positives。

## Overall Answer To The Project Question

当前实验已经能回答一个清晰的本科研究问题：

> 在 entity matching 中，reported performance 不只受模型影响，也显著受 training class ratio、evaluation class ratio、hard negatives 和 seen/unseen split construction 影响。

更具体地说：

- 模型差异存在，但不是唯一因素。
- Random Forest 是当前传统 baseline 中最强的模型。
- Training class ratio 有影响，但固定 test distribution 下影响较温和。
- Evaluation class ratio 对 F1 和 precision 的影响很强。
- Unseen-entity evaluation 需要严格 split guard，但 unseen 不一定自动更难。
- 结果解释必须同时报告 class ratio、split construction、threshold protocol、seed schedule 和 leakage guard。

## 推荐论文图表

建议最终 report 使用这些核心表/图：

| Table/Figure | Source | Purpose |
|---|---|---|
| Table 1: Dataset and split summary | `configs/datasets/wdc_products_80pair.json`, split guard docs | 说明 train/valid/test label counts 和 entity overlap |
| Table 2: Traditional baseline results | `reports/baseline_comparison.md` | 回答 baseline performance |
| Table 3: Fixed-test class-ratio results | `reports/class_ratio_results.md` | 分析 training ratio |
| Figure 1: Train/test ratio F1 matrix | `reports/train_test_ratio_grid_f1_matrix.csv` | 展示 evaluation ratio sensitivity |
| Figure 2: Precision drop from test 1:1 to 1:4 | `reports/train_test_ratio_grid_test_sensitivity.csv` | 说明 F1 drop 主要由 precision drop 驱动 |
| Table 4: Seen vs unseen comparison | `reports/seen_vs_unseen_comparison.md` | 展示反直觉 seen/unseen 结果 |
| Table 5: Seen/unseen all-seed error profile | `reports/seen_unseen_error_profile_by_model.csv` | 证明 false-positive pattern 稳定 |

## 不应该做的写法

避免这些说法：

- “Unseen entities are always harder.”
- “Balanced training always improves entity matching.”
- “The best model is universally Random Forest.”
- “Matched train/test ratio results are directly comparable to fixed-test results.”
- “The seen split is leakage-free.”

更合适的写法：

- “In this WDC 80pair setting, evaluation class ratio had a stronger effect on F1 than training class ratio.”
- “The unseen split remains the main entity-disjoint robustness evaluation, but it did not score lower than the seen diagnostic split.”
- “The seen diagnostic split produced more false positives across all inspected model-seed runs.”

## Phase 4 建议

下一阶段建议不要立刻加新模型，而是先把结果转成 final-report assets：

1. 生成 publication-ready CSV tables。
2. 生成简单 figures，例如 F1 heatmap 和 precision-drop bar chart。
3. 起草英文 technical report 的 `Results` 和 `Discussion`。
4. 检查所有 claims 都有 artifact 支撑。

