# Phase 0 基础理解与研究问题审查

日期：2026-08-14

## 1. 核心概念

### 1.1 记录链接 / 实体匹配 / 实体解析

记录链接（Record Linkage），也叫实体匹配（Entity Matching）或实体解析（Entity Resolution），指的是判断两条记录是否指向同一个真实世界中的对象。

在本项目里，这个对象通常是一个商品。例如两个电商网站上都有一条手机商品记录：

```text
Apple iPhone 14 Pro 256GB Black
iPhone 14Pro Apple Black 256 G
```

它们写法不同，但可能是同一个商品。实体匹配要判断这两条记录是否应该被连接起来。

注意：一条记录（record）是数据表里的一行或一个商品 listing；一个实体（entity）是真实世界中的那个商品本身。

### 1.2 为什么实体匹配可以转化为二分类

二分类（Binary Classification）是机器学习里最常见的监督学习形式之一。每个样本只属于两个类别中的一个。

实体匹配可以被转化为二分类，因为每一对记录只有两种可能：

- `match`：两条记录指向同一个真实实体。
- `non-match`：两条记录指向不同真实实体。

模型的输入不是单独一条记录，而是一对记录，以及这对记录之间的相似度特征。例如：

- 标题有多相似；
- 品牌是否一致；
- 型号是否一致；
- 数字 token 是否一致，例如 `128GB`、`256GB`；
- 价格、规格等结构化属性是否接近。

模型的输出通常是一个概率，例如：

```text
P(match) = 0.82
```

然后我们再通过一个阈值（threshold）把概率变成最终标签。例如阈值是 `0.6`，那么 `0.82 >= 0.6`，就预测为 `match`。

### 1.3 match 和 non-match 是什么

`match` 表示两条记录应该合并或连接，因为它们描述同一个真实实体。

`non-match` 表示两条记录不应该合并，因为它们描述不同实体。

一个常见误区是：文本很像就一定是 `match`。这在商品匹配里经常不成立。

例如：

```text
Apple iPhone 14 Pro 128GB
Apple iPhone 14 Pro 256GB
```

这两个标题很像，但容量不同，可能是两个不同商品，因此可能是 `non-match`。

反过来，两条记录文本差异很大，也可能是 `match`，因为不同网站可能省略字段、使用缩写或改变词序。

### 1.4 类别不平衡是什么

类别不平衡（Class Imbalance）指两个类别的样本数量差异很大。

在实体匹配里，`non-match` 通常远多于 `match`。原因很简单：如果随机拿两个商品记录，它们大概率不是同一个商品。

这会影响模型评价。假设测试集中 99% 都是 `non-match`，一个模型如果永远预测 `non-match`，它的准确率（accuracy）也可能很高，但它其实完全找不到真正的 `match`。

因此本项目不会只看 accuracy，而会重点看：

- precision；
- recall；
- F1；
- PR-AUC；
- confusion matrix；
- 多个随机种子的 mean 和 standard deviation。

### 1.5 未见实体分布偏移是什么

未见实体分布偏移（Unseen-Entity Shift）指测试集里的实体在训练集中从来没有出现过。

例如训练集中出现过 iPhone 13、Samsung S22，但测试集中出现的是 iPhone 14，并且 iPhone 14 的所有记录都没有出现在训练集中。此时模型不能依赖“记住某个商品”，只能依赖一般匹配规律。

这对实体匹配很重要，因为真实应用里经常会遇到新商品、新公司、新病人、新文献或新地址。模型如果只能处理训练集中见过的实体，它的研究价值就比较有限。

### 1.6 pair-random split 为什么可能高估结果

pair-random split 指随机把“记录对”分到训练集、验证集和测试集。

问题在于：虽然具体的 pair 没有重复，但同一个实体可能同时出现在训练集和测试集中。

例如：

```text
train: (iPhone 14 listing A, iPhone 14 listing B)
test:  (iPhone 14 listing A, iPhone 14 listing C)
```

这时测试集里出现了训练集中见过的实体。模型可能不是学会了通用匹配规则，而是受益于熟悉的商品名称、品牌和属性。

因此 pair-random split 可能让结果过于乐观。

更严格的划分方式是 entity-disjoint split。它要求训练集、验证集和测试集之间实体不重叠，从而更直接地测试模型对未见实体的泛化能力。

## 2. 这个项目试图回答什么问题

这个项目不是单纯做一个分类器，也不是只追求最高 F1。

它真正想回答的是：

传统机器学习实体匹配模型在更严格、更公平的实验协议下是否仍然可靠？

具体来说，我们关心：

1. 类别比例变化时，模型表现会怎样变化？
2. pair-random split 是否会因为实体重叠而高估模型效果？
3. entity-disjoint split 下模型还能不能泛化到未见实体？
4. hard-negative sampling 是否能提升模型处理困难负样本的能力？
5. 简单、可解释、低成本的传统模型能不能作为稳定 baseline？

## 3. Research Questions 审查

### RQ1

原问题：

> How do different match-to-non-match ratios in the training and test sets affect the precision, recall, F1 score, PR-AUC, and calibration of traditional entity-matching classifiers?

中文理解：

不同的 `match : non-match` 比例会怎样影响传统实体匹配分类器的 precision、recall、F1、PR-AUC 和概率校准？

可实验验证性：可以。我们可以人为控制训练集和测试集的类别比例，例如 `1:1`、`1:2`、`1:3`、`1:5`，然后在相同模型和相同划分规则下比较指标。

范围判断：适合本科个人研究。这个问题不要求大模型，传统机器学习模型就能完成。

主要风险：不能根据测试集结果选择“最好看的比例”。所有比例都要如实报告，并记录每个比例下的正负样本数量。

### RQ2

原问题：

> How much performance difference exists between pair-random evaluation and entity-disjoint evaluation, particularly on previously unseen entities?

中文理解：

pair-random evaluation 和 entity-disjoint evaluation 之间的性能差异有多大？尤其是在测试集实体从未出现在训练集中的情况下。

可实验验证性：可以，但依赖数据集是否提供可靠的实体 ID。

范围判断：适合本科个人研究，但这是项目中最需要小心的数据划分问题。Phase 1 必须先检查数据字段和标签来源。

主要风险：如果数据集没有实体 ID，就很难做真正严格的 entity-disjoint split。到时候要么换数据集，要么清楚记录代理方案和局限性。

### RQ3

原问题：

> Does hard-negative sampling improve unseen-entity generalization compared with random negative sampling, and what types of errors does it reduce or introduce?

中文理解：

与随机负样本采样相比，困难负样本采样是否能改善模型在未见实体上的泛化？它减少了哪些错误，又可能引入哪些新错误？

可实验验证性：可以。我们可以固定评估集，只改变训练阶段负样本生成方式，然后比较结果和错误类型。

范围判断：适合本科个人研究，但应该放在数据读取、特征、划分和 baseline 完成之后。

主要风险：hard-negative 的定义不能偷看测试集结果。采样规则必须只基于训练数据，并在最终测试前锁定。

## 4. 与 Luiza Antonie 教授方向的关系

这个项目与目标导师方向是匹配的，因为它直接涉及：

- Record Linkage；
- Data Integration；
- Classification；
- Data Mining；
- Applied Machine Learning；
- 实验协议和可复现性。

已检查的证据：University of Guelph 官方页面列出 Luiza Antonie 教授的研究方向包括 Record Linkage、Longitudinal Data、Data Mining、Data Integration 和 Classification。

来源：https://www.uoguelph.ca/computing/people/luiza-antonie

这个匹配点的表达要谨慎：我们不能说这个项目“完全等同于导师研究”，只能说它与导师公开列出的多个研究方向有明确交集。

## 5. 可行性判断

在个人本科研究范围内，这个项目是可完成的，前提是控制 MVP 范围。

可行的原因：

- 先使用小规模或抽样后的公开数据集；
- 先做传统机器学习 baseline；
- 用 scikit-learn、pandas、NumPy 等成熟工具；
- 每一步都有测试和文档；
- 不提前引入 Transformer 或大规模 WDC 全量处理。

会让项目失控的做法：

- 一开始就下载超大规模数据；
- 一开始就加 Transformer；
- 同时做太多数据集；
- 没有锁定实验协议就开始比较结果；
- 只追求最高 F1。

## 6. MVP

本项目的最小可行版本（Minimum Viable Project, MVP）包括：

- 至少两个公开实体匹配数据集；
- 可复现的数据读取和数据质量检查；
- pairwise similarity features；
- Logistic Regression、Random Forest、SVM 三个 baseline；
- pair-random split 和 entity-disjoint split；
- random negative sampling 和 hard-negative sampling；
- `1:1`、`1:2`、`1:3`、`1:5` 类别比例实验；
- 至少五个随机种子；
- 保存原始预测、指标、汇总结果和运行时间；
- 完成人工 error analysis；
- 完成 README、技术报告、学习指南和面试材料。

## 7. 可选扩展

只有 MVP 完成且可复现后，才考虑：

- Blocking / Candidate Generation；
- blocking 指标；
- 更大规模 WDC 实验；
- probability calibration；
- Transformer baseline。

扩展必须服务研究问题，不能只是为了堆技术名词。

## 8. 非目标

本项目当前不做：

- 生产级网站；
- LLM 或 RAG 包装；
- 只追求最高 F1；
- 看到测试结果后修改测试集；
- 从相关性推出因果关系；
- 编造实验结果或论文级创新；
- baseline 完成前加入大模型。

## 9. 成功标准

阶段成功不是指“模型分数高”，而是指每一步真实、可复核、可继续。

最终成功要求：

- 研究问题和实验一一对应；
- 结果能追溯到配置、命令、代码版本和输出文件；
- 没有已知未解释的数据泄漏；
- 多随机种子结果完整；
- 错误分析完成；
- README、technical report、learning guide、code walkthrough 和 interview guide 能支持你独立解释整个项目。

