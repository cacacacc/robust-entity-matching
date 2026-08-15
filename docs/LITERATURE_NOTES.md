# 文献笔记

本文件只记录已经读取过原始论文或官方页面后的事实、解释和待验证问题。不要把计划、假设或二手印象写成已经证实的结论。

## 2026-08-15：Phase 1 初步文献审计

### 1. Foxcroft, Christen, and Antonie：Class Ratio and Its Implications for Reproducibility and Performance in Record Linkage

来源：

https://users.cecs.anu.edu.au/~Peter.Christen/publications/foxcroft2024ratio.pdf

#### 论文研究什么

这篇论文研究 record linkage 中 `match : non-match` 类别比例对模型表现和可复现性的影响。

论文明确把 record linkage 表述为 pairwise binary classification：每一对记录被预测为 `match` 或 `non-match`。这直接支持本项目把实体匹配建模为二分类任务。

#### 使用的数据和协议

论文使用多个公开实体匹配数据集，包括：

- `abt-buy`
- `amazon-google`
- `walmart-amazon`
- `wdc xlarge computers`
- `wdc xlarge shoes`
- `wdc xlarge watches`

论文先把 labeled pairs 分成 matches 集合 `M` 和 non-matches 集合 `N`，然后控制不同的 `match : non-match` 比例。

论文实验中使用的比例包括：

- `1:1`
- `1:2`
- `1:3`
- `1:4`
- `1:5`

论文使用 10-fold 设置，每次按照 `8:1:1` 分成 training、validation 和 test。模型输出 match 概率后，在 validation set 上选择使 F1 最大的 threshold，再用于 test set。

#### 模型和指标

论文比较了：

- Random Forest；
- SVM；
- Entity Matching Transformer。

主要指标包括 precision、recall 和 F1。论文还讨论了 precision-recall curve 和 threshold。

#### 关键结论

1. class ratio 会显著影响 reported performance。
2. 只报告 matching pairs 的数量不够，必须报告 matching 和 non-matching 的数量或比例。
3. 在 deployment class imbalance 不确定时，训练时低估 non-match 数量的风险更大。
4. 论文把 random sampling 与 hard negative mining 作为未来仍需研究的方向之一。
5. 论文指出传统模型训练成本低，而 transformer 模型需要更多硬件和训练时间。

#### 对本项目的意义

这篇论文直接支撑 RQ1：

> 不同 match/non-match ratio 如何影响 precision、recall、F1、PR-AUC 和 calibration？

本项目会继承它的核心思想：控制 class ratio，不只报告一个固定比例下的结果。

本项目与它的区别：

- 本项目会加入 PR-AUC、confusion matrix、runtime、mean/std；
- 本项目会强调 entity-disjoint split 和 unseen-entity generalization；
- 本项目会把 random negative sampling 与 hard-negative sampling 作为明确实验问题，而不是只作为未来工作。

#### 当前不能直接采用的地方

论文中的具体数值不能作为本项目结果。它们只能作为文献背景。我们必须在自己的数据、代码和配置下重新运行实验。

---

### 2. Foxcroft, Sartor, and Antonie：Comparing Traditional and Deep Learning Approaches for Product Matching: Performance on Unseen Entities

来源：

https://assets.pubpub.org/izpipo2h/189-51747605873107.pdf

#### 论文研究什么

这篇论文研究传统机器学习方法和深度学习方法在 product matching 中对 seen/unseen entities 的表现差异。

论文关注的问题是：深度学习方法在 unseen entities 上的性能下降，是不是所有 record linkage 方法都会遇到，还是 representation learning classifier 更明显？

#### 使用的数据和协议

论文使用 WDC Products benchmark。该 benchmark 提供三个重要维度：

- training data size；
- corner cases；
- seen / half-seen / unseen test sets。

论文解释了 seen、half-seen 和 unseen 的含义：

- seen test set：测试 pair 中的实体在训练阶段出现过；
- unseen test set：测试 pair 中的实体没有出现在训练阶段；
- half-seen test set：pair 中一半记录对应 seen entity，一半对应 unseen entity。

论文提到 WDC Products 中 test records 本身不会直接出现在 training records 中，但实体层面的 seen/unseen 仍然是重要评估维度。

#### 特征和模型

论文使用 hand-engineered feature vectors，包括：

- edit distance；
- Jaro similarity；
- Jaro-Winkler similarity；
- Jaccard similarity；
- Sorensen-Dice；
- word/alpha/numeric token set similarity；
- overlap coefficient；
- relaxed Jaccard；
- TF-IDF cosine similarity；
- sentence-transformer embedding cosine similarity。

传统模型主要使用 scikit-learn Random Forest。

#### 关键结论

1. hand-engineered Random Forest 明显优于 Magellan-RF，但多数情况下仍弱于深度学习 representation learning 方法。
2. 在小训练数据和 unseen test set 的组合下，hand-engineered Random Forest 具有竞争力。
3. 论文认为 seen/unseen evaluation 对 representation learning classifiers 尤其重要。
4. 论文建议在现代评估中，不仅要排除训练中出现过的具体 records，还应排除与训练 records 指向同一真实实体的测试 records。
5. 论文也提醒：单一 train/test split 可能导致 seen/unseen 难度本身不同，因此需要谨慎解释结果。

#### 对本项目的意义

这篇论文直接支撑 RQ2：

> pair-random evaluation 和 entity-disjoint evaluation 的性能差异有多大，尤其是在 unseen entities 上？

它也支持本项目先做传统 baseline 的合理性：传统方法可能不是最高性能，但它们训练成本低、可解释，并且在 seen/unseen 维度上可能更稳定。

#### 当前不能直接采用的地方

论文中的 HE-RF 结果不能直接当作本项目结果。它使用了特定特征集合和 benchmark split。本项目需要自己实现或明确选择 feature set，并重新保存预测和指标。

---

## 当前文献审计得到的项目约束

1. class ratio 必须报告正负样本数量，不能只报告 F1。
2. threshold 必须在 validation set 上选择，不能用 test set 选。
3. pair-random split 和 entity-disjoint split 要分开报告。
4. 如果数据集没有可靠实体 ID，就不能声称完成严格 entity-disjoint evaluation。
5. hard-negative sampling 的规则必须在训练数据内定义，不能根据测试结果调参。
6. transformer 可作为后续扩展，但不进入 MVP。

## Phase 1 下一步待查

下一步要继续审计候选数据集，重点检查：

- 是否有原始 records；
- 是否有 labeled pairs；
- 是否有实体 ID 或 cluster ID；
- 是否有固定 train/validation/test；
- 文件大小是否适合本地下载；
- license 或使用条款是否允许公开研究使用；
- 是否支持 class-ratio、entity-disjoint 和 hard-negative 实验。

