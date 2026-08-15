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

## 2026-08-15：小型文件 schema 检查尝试

### 本次目标

本次原计划检查 WDC Products 的官方 sample pair-wise JSON，以及 CompERBench `abt-buy` 的 `gs_train.csv` 和 `records.zip`，目的是确认实际文件 schema，而不是运行实验。

### 已确认的官方页面信息

#### WDC Products

官方页面说明 WDC Products 文件使用 JSON Lines 格式，可以用如下方式读取：

```python
import pandas as pd
df = pd.read_json("file_name.json.gz", compression="gzip", lines=True)
```

官方页面说明 pair-wise 文件中每一行表示一对 offers。每个 offer-specific attribute 会出现两次，分别带 `_left` 和 `_right` 后缀。

官方页面确认 pair-wise 文件包含：

- `label`
- `pair_id`
- `is_hard_negative`
- 左右两侧 offer attributes，例如 title、description、price、priceCurrency、brand 等；
- 与实体或产品相关的标识字段，例如 `cluster_id` 的左右版本。

官方页面还确认：

- WDC Products 严格分离 training、validation 和 test 中出现的 records；
- benchmark 具有 seen / unseen products 维度；
- pair-wise test sets 每个包含 4,500 pairs；
- pair-wise benchmark zip 文件约 20MB 到 21.6MB，低于 500MB。

#### CompERBench `abt-buy`

官方页面确认 `abt-buy` 提供：

- `gs_train.csv`，约 107KB；
- `gs_val.csv`，约 31KB；
- `gs_test.csv`，约 16KB；
- `feature_vector.zip`，约 850KB；
- `records.zip`，约 125KB。

官方页面说明 CompERBench 提供固定 train、validation 和 test sets，并提供 feature vectors 和 source records。

官方页面还说明其 baseline feature creation 包括：

- Levenshtein；
- token-level Jaccard；
- Jaccard with inner Levenshtein；
- exact；
- containment；
- TF-IDF cosine similarity；
- numeric absolute difference。

### 当前阻塞

实际下载小型 schema 文件时被审批系统拒绝，原因是用户此前明确要求“暂时不要下载数据”；仅回复“继续”不足以明确撤销该限制。

因此本回合没有下载任何数据文件，也没有检查本地实际 CSV/JSON 列名。

### 当前结论

可以确认：

- WDC Products 是强候选数据集；
- CompERBench `abt-buy` 是很小的可审计候选任务；
- 两者的文件规模都适合本地 schema 审计；
- 但在没有实际文件列名之前，不能最终锁定 data contract。

不能确认：

- CompERBench `abt-buy` 的 `gs_train.csv` 具体列名；
- `records.zip` 内部文件名和字段；
- CompERBench 是否直接支持严格 entity-disjoint split；
- WDC Products 具体 sample 文件中的所有列名和缺失值情况。

### 下一步需要的授权

如果继续 Phase 1 schema 审计，需要明确允许下载以下小型公开文件：

- WDC Products 官方 sample 或 20MB 级 pair-wise benchmark zip；
- CompERBench `abt-buy` 的 `gs_train.csv`、`gs_val.csv`、`gs_test.csv` 和 `records.zip`。

这些文件都低于 500MB，不涉及训练、不涉及上传、不涉及付费 API。

## 2026-08-15：本地 schema 审计结果

用户已明确允许下载小型公开数据文件用于 Phase 1 schema 审计，单个文件不超过 500MB。本次只下载和解压小型公开文件，不训练模型，不上传数据，不推送 GitHub。

### 下载文件

#### WDC Products

下载位置：

- `data/raw/wdc_products_sample/sample_pairwise.json`
- `data/raw/wdc_products_sample/wdc_products_index.html`
- `data/raw/wdc_products_sample/80pair.zip`
- `data/raw/wdc_products_sample/80pair/`

文件大小：

- `sample_pairwise.json`：约 55KB；
- `80pair.zip`：约 21.0MB。

注意：最初尝试过一个错误 URL，返回的是 HTML 页面而不是 JSON。后续从 WDC Products 官方页面源码定位到真实 sample URL：

https://data.dws.informatik.uni-mannheim.de/largescaleproductcorpus/data/wdc-products/sample_pairwise.json

#### CompERBench `abt-buy`

下载位置：

- `data/raw/comperbench_abt_buy/gs_train.csv`
- `data/raw/comperbench_abt_buy/gs_val.csv`
- `data/raw/comperbench_abt_buy/gs_test.csv`
- `data/raw/comperbench_abt_buy/records.zip`
- `data/raw/comperbench_abt_buy/records/`

文件大小：

- `gs_train.csv`：109,056 bytes；
- `gs_val.csv`：31,329 bytes；
- `gs_test.csv`：15,481 bytes；
- `records.zip`：127,521 bytes。

这些文件都被 `.gitignore` 排除，不会提交到 Git。

### WDC Products schema

`sample_pairwise.json` 和 `80pair.zip` 中的 pair-wise JSON Lines 文件字段一致：

- `id_left`
- `brand_left`
- `title_left`
- `description_left`
- `price_left`
- `priceCurrency_left`
- `cluster_id_left`
- `id_right`
- `brand_right`
- `title_right`
- `description_right`
- `price_right`
- `priceCurrency_right`
- `cluster_id_right`
- `pair_id`
- `label`
- `is_hard_negative`

`label` 使用整数：

- `1`：match；
- `0`：non-match。

`is_hard_negative` 使用布尔值：

- `true`：hard negative；
- `false`：not hard negative。

`cluster_id_left` 和 `cluster_id_right` 可以用于实体层面的 seen/unseen 检查。

### WDC Products 80pair split 结构

`80pair.zip` 包含：

- `wdcproducts80cc20rnd000un_train_small.json.gz`
- `wdcproducts80cc20rnd000un_train_medium.json.gz`
- `wdcproducts80cc20rnd000un_train_large.json.gz`
- `wdcproducts80cc20rnd000un_valid_small.json.gz`
- `wdcproducts80cc20rnd000un_valid_medium.json.gz`
- `wdcproducts80cc20rnd000un_valid_large.json.gz`
- `wdcproducts80cc20rnd000un_gs.json.gz`
- `wdcproducts80cc20rnd050un_gs.json.gz`
- `wdcproducts80cc20rnd100un_gs.json.gz`

本次重点检查 small split 和三个 gold-standard test files：

| File | Total pairs | Match | Non-match | Hard negative | Not hard negative |
| --- | ---: | ---: | ---: | ---: | ---: |
| `wdcproducts80cc20rnd000un_train_small.json.gz` | 2,500 | 500 | 2,000 | 1,000 | 1,500 |
| `wdcproducts80cc20rnd000un_valid_small.json.gz` | 2,500 | 500 | 2,000 | 1,000 | 1,500 |
| `wdcproducts80cc20rnd000un_gs.json.gz` | 4,500 | 500 | 4,000 | 3,000 | 1,500 |
| `wdcproducts80cc20rnd050un_gs.json.gz` | 4,500 | 500 | 4,000 | 3,000 | 1,500 |
| `wdcproducts80cc20rnd100un_gs.json.gz` | 4,500 | 500 | 4,000 | 3,000 | 1,500 |

Pair overlap check:

- train vs valid pair overlap：0；
- train vs 000un gold-standard pair overlap：0；
- valid vs 000un gold-standard pair overlap：0。

Entity / record overlap check against `train_small`:

| Test file | Cluster overlap with train | Record ID overlap with train | Test clusters | Test record IDs |
| --- | ---: | ---: | ---: | ---: |
| `000un_gs` | 500 | 0 | 500 | 1,000 |
| `050un_gs` | 250 | 110 | 500 | 1,000 |
| `100un_gs` | 0 | 0 | 500 | 1,000 |

Interpretation:

- `000un_gs` behaves as fully seen at entity level relative to `train_small` because all 500 test clusters overlap with train clusters.
- `100un_gs` behaves as fully unseen at entity level relative to `train_small` because no test cluster overlaps with train clusters.
- `050un_gs` is mixed by design and has partial entity overlap. It also shows some record ID overlap with `train_small`, so it must be used carefully and interpreted as an official benchmark variant rather than a strict record-disjoint custom split.

### CompERBench `abt-buy` schema

Gold-standard pair files:

- `gs_train.csv`
- `gs_val.csv`
- `gs_test.csv`

Columns:

- `source_id`
- `target_id`
- `matching`

`matching` uses strings:

- `True`：match；
- `False`：non-match。

Source records:

- `record_descriptions/1_abt.csv`
- `record_descriptions/2_buy.csv`

`1_abt.csv` columns:

- `subject_id`
- `name`
- `description`
- `price`

`2_buy.csv` columns:

- `subject_id`
- `name`
- `description`
- `manufacturer`
- `price`

Encoding note:

- pair files read successfully as UTF-8;
- record files contain non-UTF-8 characters, so ingestion must support a `cp1252` or `latin-1` fallback.

Record counts:

- Abt source records：1,081；
- Buy source records：1,092。

Pair counts:

| Split | Total pairs | Match | Non-match |
| --- | ---: | ---: | ---: |
| train | 5,010 | 764 | 4,246 |
| validation | 1,439 | 220 | 1,219 |
| test | 710 | 109 | 601 |

### CompERBench `abt-buy` split overlap findings

Pair overlap:

- train vs validation：2 duplicate pairs；
- train vs test：1 duplicate pair；
- validation vs test：0 duplicate pairs。

Duplicate pairs found:

- train/validation duplicate match：`source_id=23246`, `target_id=90146847`, `matching=True`;
- train/validation duplicate non-match：`source_id=23097`, `target_id=202515446`, `matching=False`;
- train/test duplicate non-match：`source_id=32625`, `target_id=201935171`, `matching=False`.

Entity / record ID overlap:

- source train/validation overlap：555 unique source IDs；
- source train/test overlap：381 unique source IDs；
- target train/validation overlap：647 unique target IDs；
- target train/test overlap：441 unique target IDs。

Interpretation:

The official `abt-buy` split is useful for a small fixed-split baseline and class-ratio experiments, but it is not pair-disjoint due to three duplicate pairs across splits and is clearly not entity-disjoint. It should not be used to claim unseen-entity generalization.

### Updated MVP dataset recommendation

Initial MVP dataset choices:

1. WDC Products `80pair` benchmark as the primary dataset for RQ2 and RQ3.
2. CompERBench `abt-buy` as the secondary small benchmark for RQ1 and baseline pipeline smoke tests.

Rationale:

- WDC Products has explicit `cluster_id`, `label`, `pair_id`, and `is_hard_negative`, and official seen/unseen variants.
- `abt-buy` is small, easy to inspect, and suitable for early pipeline development, but its official split has leakage-like overlap and cannot support strict unseen-entity claims.

Open decision:

- Whether to include a third CompERBench product dataset, such as `amazon-google` or `products (Walmart-Amazon)`, after the first ingestion pipeline works.

## 2026-08-15：程序化 data quality report 结果

本次新增程序化质量报告，基于 normalized `PairRecord` 表示，而不是手工 shell 检查。

### WDC Products `80pair`

关键发现：

- `train_small`、`valid_small` 和 `test_unseen_100un` 之间没有 pair、record 或 entity overlap。
- `test_seen_000un` 与 `train_small` 的 entity overlap 为 500，符合 fully seen benchmark 语义。
- `test_mixed_050un` 与 `train_small` 的 entity overlap 为 250，record overlap 为 110，pair overlap 为 8。
- `test_mixed_050un` 与 `valid_small` 的 entity overlap 为 250，record overlap 为 103，pair overlap 为 11。

解释：

WDC 的 `100un` split 可以支撑严格 unseen-entity evaluation。`000un` 和 `050un` 是官方 seen/mixed benchmark variants，不能被解释为 entity-disjoint test sets。

Missing values:

WDC 的 `brand` 和 `description` 缺失很多。例如 `train_small` 中：

- `left.brand_left` 缺失 1,607；
- `right.brand_right` 缺失 1,573；
- `left.description_left` 缺失 597；
- `right.description_right` 缺失 636。

这说明后续特征工程必须显式处理 missing values，不能假设品牌和描述总是存在。

### CompERBench `abt-buy`

关键发现：

- `train` split 内部有 2 个 duplicate pair IDs，共 4 行；
- `validation` split 内部有 1 个 duplicate pair ID，共 2 行；
- `train` 与 `validation` 有 2 个 pair ID overlap；
- `train` 与 `test` 有 1 个 pair ID overlap；
- `train` 与 `test` record ID overlap 为 822；
- 没有可用 entity ID，因此 entity overlap 无法计算。

解释：

`abt-buy` 可以用于小型 ingestion、feature 和 baseline smoke tests，也可以用于 class-ratio 方法开发；但不能用于严格 leakage-free conclusion，也不能用于 unseen-entity conclusion。

Missing values:

`abt-buy` 的 price 缺失严重。例如：

- train 中 `left.price` 缺失 3,305；
- train 中 `right.price` 缺失 2,041；
- validation 中 `left.price` 缺失 983；
- test 中 `left.price` 缺失 453。

后续特征工程不能直接依赖 price；如果使用 price difference，需要设计 missing-value fallback 或显式缺失指示特征。
