# 数据集审计

本文件记录公开数据集的官方来源、字段、规模、标签来源、实体 ID、下载风险和是否适合 MVP。当前阶段只审计，不下载数据。

## 2026-08-15：Phase 1 初步数据源审计

### 1. WDC Products：A Multi-Dimensional Entity Matching Benchmark

官方页面：

https://webdatacommons.org/largescaleproductcorpus/wdc-products/index.html

#### 数据集用途

WDC Products 是一个面向 product entity matching 的 benchmark，专门支持多个评估维度：

- corner-case 数量；
- test set 中 unseen entities 的比例；
- development set size。

它同时提供 pair-wise formulation 和 multi-class formulation。本项目 MVP 主要关注 pair-wise formulation。

#### 规模

官方页面说明：

- 共 11,715 个 product offers；
- 共 2,162 个 product entities；
- 包含 training、validation 和 test sets；
- pair-wise test sets 每个包含 4,500 pairs；
- small pair-wise training set 为 2,500 pairs；
- medium pair-wise training set 为 6,000 pairs；
- large pair-wise training set 约 19,000 到 20,000 pairs。

这个规模适合本科个人项目和本地实验。

#### 字段

官方页面列出的 offer 字段包括：

- `id`
- `brand`
- `title`
- `description`
- `price`
- `priceCurrency`
- `cluster_id`
- `label`
- `pair_id`
- `is_hard_negative`
- `unseen`

其中：

- `cluster_id` 指向真实产品实体；
- pair-wise 文件中的 `label` 是 `1` 或 `0`；
- `is_hard_negative` 标记负样本是否由相似性度量选择；
- `pair_id` 唯一标识一对 offer。

#### 对本项目 RQ 的适配性

RQ1 class ratio：适合。pair-wise 文件有 label，可以重采样不同 match/non-match ratio。

RQ2 unseen-entity shift：非常适合。官方 benchmark 本身提供 seen、half-seen、unseen 维度，并有 `cluster_id`。

RQ3 hard-negative sampling：非常适合。pair-wise 文件包含 `is_hard_negative` 字段，可以用于审计或构造 hard-negative 实验。

#### 风险和注意事项

- 不能一开始下载全量大语料；只考虑 benchmark zip 或小规模 pair-wise 文件。
- 官方 benchmark 已经有自己的 split。我们需要决定是完全沿用官方 split，还是基于 records/cluster_id 自己构造 split。这个决定会影响 RQ2。
- `is_hard_negative` 可以帮助实验，但不能直接把官方标记当作本项目唯一 hard-negative 定义，后续需要明确实验协议。

#### 初步判断

强烈候选 MVP 数据集。它同时支持 unseen entities、hard negatives、pair-wise labels 和实体 ID，是本项目最核心的数据源候选。

---

### 2. CompERBench / Benchmark Matching Tasks

官方页面：

https://data.dws.informatik.uni-mannheim.de/benchmarkmatchingtasks/

#### 数据集用途

该页面提供 21 个完整 entity matching benchmark tasks，目标是提高 entity matching 方法的可复现性和可比性。

页面提供固定的 train、validation、test sets，也提供 feature vectors 和 source records。

#### 候选任务

与本项目最相关的任务包括：

- `abt-buy`
- `amazon-google`
- `products (Walmart-Amazon)`
- `wdc_xlarge_watches`
- `wdc_xlarge_computers`
- `wdc_xlarge_shoes`
- `wdc_xlarge_cameras`

这些数据集也出现在 class-ratio 论文的实验中。

#### 文件规模

页面列出的许多文件很小，适合本地实验。例如：

- `abt-buy` records 约 125KB，feature vector 约 850KB；
- `amazon-google` records 约 602KB，feature vector 约 1.5MB；
- `products (Walmart-Amazon)` records 约 13.5MB，feature vector 约 3.8MB；
- WDC xlarge records 和 feature vectors 通常也在 MB 级别。

这符合本项目“不先下载大数据”的原则。

#### 对本项目 RQ 的适配性

RQ1 class ratio：适合。它提供 labeled train/validation/test pairs，可用于控制 match/non-match ratio。

RQ2 unseen-entity shift：待确认。虽然有 records 和 labeled pairs，但需要检查 records 中是否有可靠实体 ID 或是否能从 pair labels 构建 entity clusters。

RQ3 hard-negative sampling：部分适合。它提供 feature vectors 和 source records，可以用相似度选择 hard negatives，但需要自己定义规则。

#### 风险和注意事项

- 并非所有任务都有可靠实体 ID；必须下载前先确认文件结构，下载后再做 schema audit。
- 已提供 fixed split，但这些 split 未必是 entity-disjoint。
- feature vectors 可用于快速 baseline，但如果直接使用官方 feature vectors，必须说明我们没有自己实现这些特征。MVP 最好至少实现自己的基础特征模块。

#### 初步判断

适合作为第二类 MVP 数据源候选，尤其适合 class-ratio 实验和传统模型 baseline。是否适合 entity-disjoint split 需要下一步下载小文件后检查字段。

---

### 3. WDC Product Data Corpus and Gold Standard for Large-Scale Product Matching V2 / LSPM

官方页面：

https://webdatacommons.org/largescaleproductcorpus/v2/

#### 数据集用途

这是大规模 product matching 数据源。官方说明其 product data corpus 包含大量 product offers，并提供 gold standard 和训练集。

#### 规模

该数据源的全量文件较大：

- full product corpus 为 GB 级；
- English corpus 也是 GB 级；
- 部分 training sets 为 MB 到几十 MB；
- gold standard 文件较小。

#### 字段

官方页面说明 pair 文件包含左右 offer 的字段，并包含：

- `pair_id`
- `label`
- 左右 offer 的属性字段。

数据语料还包含 offer ID、URL、cluster 信息等。

#### 对本项目 RQ 的适配性

RQ1：适合，尤其是 gold standard 和 training subsets。

RQ2：可能适合，但需要确认可下载文件中是否保留 cluster/entity 信息。

RQ3：可能适合，但 hard-negative 需要自己定义。

#### 风险和注意事项

- 不下载 GB 级全量 corpus，除非后续明确需要并获得确认。
- 优先考虑小规模 gold standard 或 training subset。
- 如果使用该数据源，必须清楚记录下载文件名、大小和字段。

#### 初步判断

作为可选数据源或补充数据源。当前不作为第一下载目标；优先审计 WDC Products benchmark 和 CompERBench 小型任务。

---

## 初步数据集选择建议

当前还不最终锁定 MVP 数据集。初步建议：

1. 第一优先级：WDC Products pair-wise benchmark。
2. 第二优先级：CompERBench 中的 `abt-buy`、`amazon-google` 或 `products (Walmart-Amazon)`。
3. 暂缓：WDC LSPM 全量 corpus。

原因：

- WDC Products 最符合 RQ2 和 RQ3；
- CompERBench 小型任务适合 RQ1 和快速 baseline；
- LSPM 全量规模过大，不适合一开始下载。

## 下一步数据审计任务

下一步应下载或查看小型样例文件，而不是下载全量数据。目标是确认：

- pair 文件的 schema；
- label 的取值；
- 是否存在 entity ID / cluster ID；
- 是否能构造 entity-disjoint split；
- 是否已有 hard-negative 标记；
- 文件大小是否低于 500MB；
- license 和引用要求。

