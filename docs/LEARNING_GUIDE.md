# 学习指南

这个文档用于持续记录项目中的核心概念、直观例子、常见误区、对应代码路径和实验结果。它不是一次性笔记，而是随着项目推进不断补充的复习材料。

## 1. 记录链接 / 实体匹配 / 实体解析

英文术语：Record Linkage / Entity Matching / Entity Resolution

定义：判断两条记录是否指向同一个真实世界实体。

直观例子：

```text
Apple iPhone 14 Pro 256GB Black
iPhone 14Pro Apple Black 256 G
```

这两条记录写法不同，但可能描述同一个商品。

在本项目中的位置：这是整个项目的核心预测任务。后续的数据读取、特征工程、模型训练、实验评估都围绕它展开。

为什么需要：真实世界的数据经常来自不同来源，字段不统一、命名不一致、属性缺失。实体匹配可以把这些不同来源中指向同一对象的记录识别出来。

常见误区：文本相似不等于实体相同。两个标题很像，但型号、容量或规格不同，仍然可能是 `non-match`。

对应代码路径：暂未实现。

对应实验结果：暂未产生。

## 2. 二分类

英文术语：Binary Classification

定义：监督学习中，每个样本只属于两个类别之一。

在本项目中，每个样本是一对记录，标签是：

- `match`：同一个实体；
- `non-match`：不同实体。

直观例子：

```text
input:  record_a, record_b, similarity_features
output: P(match)
```

模型先输出概率，再通过阈值（threshold）转成最终标签。

为什么需要：把实体匹配转成二分类后，就可以使用成熟的机器学习方法，例如 Logistic Regression、Random Forest 和 SVM。

常见误区：模型输出的概率不是最终标签。阈值不同，precision 和 recall 会改变。

对应代码路径：暂未实现。

对应实验结果：暂未产生。

## 3. match 和 non-match

英文术语：Match / Non-Match

定义：

- `match`：两条记录指向同一个真实实体。
- `non-match`：两条记录指向不同真实实体。

直观例子：

```text
Apple iPhone 14 Pro 128GB
Apple iPhone 14 Pro 256GB
```

这两条记录文本非常相似，但容量不同，可能是 `non-match`。

在本项目中的位置：这是所有训练、验证和测试数据的标签定义。

为什么需要：如果标签定义不清楚，模型训练和实验评价都会失去意义。

常见误区：不要把“看起来差不多”直接当作 `match`。实体匹配要关注真实实体是否相同，而不是只看字符串表面相似。

对应代码路径：暂未实现。

对应实验结果：暂未产生。

## 4. 类别不平衡

英文术语：Class Imbalance

定义：不同类别的样本数量差异很大。

在实体匹配中，`non-match` 通常远多于 `match`，因为随机两条记录大概率不是同一个实体。

直观例子：如果有 1000 对记录，其中 950 对是 `non-match`，50 对是 `match`，这就是类别不平衡。

在本项目中的位置：RQ1 直接研究 class imbalance 对指标的影响。

为什么需要：类别比例会影响 precision、recall、F1 和 PR-AUC。只在一种比例下报告结果，可能会误导读者。

常见误区：accuracy 不适合做本项目的主要指标。一个模型如果全部预测为多数类，也可能得到很高 accuracy。

对应代码路径：暂未实现。

对应实验结果：暂未产生。

## 5. 未见实体分布偏移

英文术语：Unseen-Entity Shift

定义：测试集中的实体没有出现在训练集中。

直观例子：训练集中没有任何 iPhone 14 的记录，测试集中才出现 iPhone 14。模型必须判断这些新实体的记录是否匹配。

在本项目中的位置：RQ2 直接研究 unseen-entity generalization，也就是模型对未见实体的泛化能力。

为什么需要：现实应用里总会出现训练时没见过的新实体。模型必须学习通用规律，而不是记住训练集里的具体对象。

常见误区：只保证同一个 pair 不重复是不够的。同一个实体仍然可能通过不同 pair 同时出现在训练集和测试集中。

对应代码路径：暂未实现。

对应实验结果：暂未产生。

## 6. pair-random split

英文术语：Pair-Random Split

定义：把候选记录对随机划分到 train、validation 和 test。

直观例子：

```text
train: (product_1_record_a, product_1_record_b)
test:  (product_1_record_a, product_1_record_c)
```

这里具体 pair 不同，但同一个实体 `product_1` 同时出现在 train 和 test。

在本项目中的位置：RQ2 会把 pair-random split 与 entity-disjoint split 进行比较。

为什么需要：pair-random split 是常见基线协议。我们需要知道它和更严格协议之间差多少。

常见误区：pair 没重复不代表没有数据泄漏。实体层面的重叠也可能让测试结果过于乐观。

对应代码路径：暂未实现。

对应实验结果：暂未产生。

## 7. entity-disjoint split

英文术语：Entity-Disjoint Split

定义：训练集、验证集和测试集中的实体互不重叠。

直观例子：如果某个商品实体出现在测试集中，那么这个商品实体的任何记录都不能出现在训练集中。

在本项目中的位置：这是测试 unseen-entity generalization 的关键协议。

为什么需要：它能减少模型记住特定实体的机会，更接近“遇到新实体时还能不能工作”的问题。

常见误区：entity-disjoint split 依赖可靠实体 ID。如果数据集没有实体 ID，就必须谨慎处理，不能假装已经严格隔离。

对应代码路径：暂未实现。

对应实验结果：暂未产生。

## 8. hard-negative sampling

英文术语：Hard-Negative Sampling

定义：选择那些看起来很像但实际上不是同一实体的负样本。

直观例子：

```text
Apple iPhone 14 Pro 128GB
Apple iPhone 14 Pro 256GB
```

这类 pair 文本非常相似，但规格不同，可能是困难负样本。

在本项目中的位置：RQ3 比较 hard-negative sampling 和 random negative sampling。

为什么需要：随机负样本往往太容易，模型可能只学会区分明显不同的商品。困难负样本能迫使模型关注型号、容量、数字和关键属性。

常见误区：hard-negative 的规则不能根据测试结果调整，否则会造成实验偏差。

对应代码路径：暂未实现。

对应实验结果：暂未产生。

## 9. string similarity features

英文术语：String Similarity Features

定义：把两条记录之间的文本相似程度转换成机器学习模型可以读取的数字。

在本项目中，当前第一版 feature schema 是 `string_similarity_v1`。

当前已经实现的直观特征：

- `exact_match`：两个标准化字符串是否完全一样；
- `token_jaccard`：两个 token 集合有多少重叠；
- `edit_similarity`：一个字符串改成另一个字符串需要多少编辑操作，越接近表示越相似；
- `numeric_overlap`：数字 token 的重叠程度，例如型号、容量、价格中的数字。

直观例子：

```text
left title:  sony camera 10x
right title: sony camcorder 10x
```

这两个标题不是 exact match，但 token 中都包含 `sony` 和 `10x`，所以 token Jaccard 会大于 0。数字 token 也有重叠，因此 numeric overlap 可能提供额外信号。

为什么需要：机器学习模型不能直接理解原始标题、描述和价格字段。我们要先把“像不像”变成数值特征，后面 Logistic Regression、Random Forest 和 SVM 才能学习。

常见误区：两个字段都缺失不应该自动算作相似。在本项目中，两个缺失值的 `exact_match` 记为 `0.0`，避免 missing value 太多时虚高。

对应代码路径：

- `src/entity_matching/features/string_similarity.py`
- `tests/test_string_similarity_features.py`
- `scripts/preview_string_features.py`

对应实验结果：暂未产生。当前只是 feature primitives 和真实样本预览，还没有训练模型。

## 10. feature table

英文术语：Feature Table

定义：每一行是一对记录，每一列是模型可以读取的数值特征，再加上必要的 metadata，例如 `pair_id` 和 `label`。

在本项目中，当前第一版 feature-table schema 是 `feature_table_v1`。

直观例子：

```text
pair_id,label,combined_token_jaccard,combined_numeric_overlap
14654897#36425270,1,0.2,0.2
```

这表示某一对记录是 `match`，它们的 combined token overlap 和 numeric overlap 都是 `0.2`。

为什么需要：模型不能直接吃 nested JSON 或原始文本。我们需要把每个 pair 转成固定列的表格，后续 Logistic Regression、Random Forest 和 SVM 才能训练。

常见误区：生成 feature table 不等于训练模型。它只是把数据准备成 model-ready 的形状，还没有产生实验结果。

对应代码路径：

- `src/entity_matching/features/table.py`
- `tests/test_feature_table.py`
- `scripts/export_feature_tables.py`

对应本地输出：

- `data/processed/comperbench_abt_buy/*.csv`
- `data/processed/wdc_products_80pair/*.csv`
- `data/processed/*/*.summary.json`

对应实验结果：暂未产生。当前只是生成和验证 feature tables。

## 11. leakage guard

英文术语：Leakage Guard

定义：在训练模型前，自动检查 train、validation、test 之间有没有不该出现的重复或重叠。

本项目当前检查四类风险：

- within-split duplicate pair IDs：同一个 split 内 pair 重复；
- cross-split pair overlap：同一个 pair 同时出现在不同 split；
- cross-split record overlap：同一条 source record 同时出现在不同 split；
- cross-split entity overlap：同一个真实实体同时出现在不同 split。

为什么需要：如果模型在训练时见过测试实体或测试 pair 的一部分，测试指标可能会虚高。这样得到的结论不能支持 RQ2 的 unseen-entity generalization。

当前真实发现：

- WDC `train_small` 和 `test_unseen_100un` 没有 pair、record、entity overlap；
- WDC `train_small` 和 `valid_small` 有 500 个 entity overlap；
- `abt-buy` train 内部有 duplicate pair IDs，train/test 之间也有 pair 和 record overlap。

常见误区：不要因为 test split 是 unseen，就自动假设 train、validation、test 三者完全 entity-disjoint。guard report 要逐对检查。

对应代码路径：

- `src/entity_matching/splitting/manifest.py`
- `src/entity_matching/splitting/guards.py`
- `tests/test_split_guards.py`
- `scripts/check_split_guards.py`

对应实验结果：暂未产生。当前只是训练前的数据协议检查。

## 12. model-ready matrix

英文术语：Model-Ready Matrix

定义：把 feature table 变成模型可以直接读取的三个核心对象：

- `X`：二维数值特征列表；
- `y`：标签列表；
- `pair_ids`：每一行对应的 pair ID。

直观例子：

```text
pair_ids = ["14654897#36425270", ...]
y = [1, ...]
X = [[0.0, 0.2, 0.5, ...], ...]
```

为什么需要：feature table 是文件格式，model-ready matrix 是训练接口。先建立这个接口，可以保证后面 Logistic Regression、Random Forest、SVM 都用同样的 feature order 和 label alignment。

常见误区：加载 matrix 不等于训练模型。当前只是确认数据已经能安全进入模型层，还没有 fit、predict 或 evaluation。

对应代码路径：

- `src/entity_matching/models/matrix.py`
- `tests/test_model_matrix.py`
- `scripts/preview_model_matrix.py`
- `configs/models/baseline_traditional.json`

对应实验结果：暂未产生。当前只是 matrix loading 和 baseline config。

## 13. dry-run protocol

英文术语：Dry-Run Protocol

定义：在真正训练模型之前，先检查配置、依赖、split guards、feature columns、matrix shape 和 label counts 是否全部合理。

在本项目中，当前 dry-run config 是：

```text
configs/experiments/wdc_unseen_baseline_dry_run.json
```

为什么需要：本地虽然已经有 `sklearn`，但这不代表可以马上训练。我们还没有锁定 validation 和 threshold-selection protocol。如果现在训练，很容易不小心用 test set 做选择，破坏实验诚信。

当前 dry-run 会检查：

- `fit_allowed` 必须是 `false`；
- split 必须通过 pair / record / entity guards；
- `X`、`y`、`pair_ids` 可以加载；
- feature vector 长度和 feature columns 对齐；
- planned model config 仍然是 `draft_not_trained`。

常见误区：dry-run 成功不等于实验成功。它只说明“训练前输入看起来准备好了”，还没有任何模型结果。

对应代码路径：

- `src/entity_matching/experiments/dry_run.py`
- `tests/test_experiment_dry_run.py`
- `scripts/dry_run_baseline_protocol.py`
- `configs/experiments/wdc_unseen_baseline_dry_run.json`

对应实验结果：暂未产生。当前只是 protocol dry-run。

## 14. threshold selection 和 metrics

英文术语：Threshold Selection / Metrics

定义：模型通常输出一个 `score` 或概率，例如 `0.73`。我们需要选择一个 threshold，把分数转成最终预测：

```text
score >= threshold -> predict match
score < threshold  -> predict non-match
```

为什么 threshold 只能在 validation 上选：如果你用 test set 来挑 threshold，test set 就不再是公平的最终考试，而变成了调参数据。这会让实验结果偏乐观。

当前实现的 metrics：

- confusion matrix：`tp`、`fp`、`tn`、`fn`；
- precision；
- recall；
- F1。

直观理解：

- precision：预测为 match 的里面，有多少是真的 match；
- recall：真实 match 里面，有多少被找出来；
- F1：precision 和 recall 的折中。

常见误区：`0.5` 不一定是最佳 threshold。不同 class ratio 下，threshold 会影响 precision / recall tradeoff。

对应代码路径：

- `src/entity_matching/evaluation/metrics.py`
- `src/entity_matching/evaluation/thresholds.py`
- `tests/test_evaluation_metrics.py`
- `scripts/preview_threshold_metrics.py`

对应实验结果：暂未产生。当前只用 toy scores 测试评估逻辑。

## 15. model factory 和 training guard

英文术语：Model Factory / Training Guard

定义：

- model factory：根据配置创建模型对象；
- training guard：在真正调用 `fit()` 前检查当前配置是否允许训练。

为什么需要：进入 Phase 3 后，我们要开始接触模型代码，但不能让模型训练不小心提前发生。现在 validation 和 threshold protocol 还没有锁定，所以训练必须继续被挡住。

当前支持创建但不训练的模型：

- Logistic Regression；
- Random Forest；
- linear SVM。

关键点：

```text
instantiate estimator != fit model
```

创建 estimator 只是检查配置和依赖能不能工作；`fit()` 才是真正训练。

常见误区：本地有 `sklearn` 不代表现在可以训练。训练必须等实验配置显式设置 `fit_allowed: true`。

对应代码路径：

- `src/entity_matching/models/factory.py`
- `src/entity_matching/experiments/training_guard.py`
- `scripts/preview_model_factory.py`
- `tests/test_model_factory.py`

对应实验结果：暂未产生。当前只是 model factory preview。

## 16. validation protocol 和 test isolation

英文术语：Validation Protocol / Test Isolation

定义：
validation protocol 是实验中规定“哪个数据 split 可以用来做什么”的规则。test isolation 是指最终测试集必须和开发阶段用到的数据隔离，不能被训练、调 threshold 或选模型污染。

本项目当前锁定的第一轮规则是：

- `train_small`：以后训练模型；
- `valid_small`：以后选择 threshold；
- `test_unseen_100un`：以后最终评估。

为什么不能直接用 test 选 threshold：
如果模型输出一个分数，比如 `0.73`，我们还需要选一个 threshold，把分数变成 `match` 或 `non-match`。如果用 test set 来挑这个 threshold，就等于提前看了考试答案。最后的 test 分数会偏乐观，科研上不干净。

为什么 `valid_small` 可以用，但要谨慎解释：
我们检查到 `train_small` 和 `valid_small` 之间有 500 个 entity overlap。所以它不是 entity-disjoint validation。它可以作为开发用 validation，帮助选择 threshold，但不能作为“模型能泛化到全新实体”的证据。

真正支持 unseen-entity claim 的是：

```text
train_small -> test_unseen_100un: pair/record/entity overlap = 0
valid_small -> test_unseen_100un: pair/record/entity overlap = 0
```

直观理解：

- validation 是练习考试，用来定规则；
- test 是正式考试，只能规则定好后再看；
- 如果用正式考试来定规则，结果就不再可信。

对应代码路径：

- `configs/experiments/wdc_unseen_baseline_protocol.json`
- `src/entity_matching/experiments/protocol.py`
- `scripts/validate_experiment_protocol.py`
- `tests/test_experiment_protocol.py`

当前验证命令：

```powershell
python scripts/validate_experiment_protocol.py configs/experiments/wdc_unseen_baseline_protocol.json
```

对应实验结果：
暂未产生。当前只是锁定和验证实验协议，没有训练模型、没有预测文件、没有 test metrics。
