# Code Walkthrough

本文件记录核心代码模块的职责、输入输出、数据流和验证方式。当前实现范围包括 Phase 2 的配置读取、raw schema 校验、normalized pair table、data quality report、interim JSONL export、text standardization 和初始 string-similarity feature primitives。

## `src/entity_matching/data/config.py`

文件职责：

加载 `configs/datasets/*.json` 数据集配置，并提供相对路径解析。

主要对象：

- `DatasetConfig`：保存配置文件路径和解析后的 JSON 内容。
- `load_dataset_config(path)`：读取 JSON 配置，并检查顶层必要字段是否存在。

输入：

- dataset config JSON 路径。

输出：

- `DatasetConfig` 对象。

关键实现选择：

- 使用 Python 标准库 `json`，暂时不引入额外依赖。
- 通过 `DatasetConfig.resolve_path()` 把配置中的相对路径解析到项目根目录。

如何测试：

```powershell
python -m unittest tests.test_data_validation
```

## `src/entity_matching/data/validation.py`

文件职责：

读取 raw dataset 文件并验证它们是否符合 dataset config 中记录的 schema 和 audited counts。

主要对象和函数：

- `DatasetValidationError`：schema 或计数不匹配时抛出的错误。
- `validate_wdc_products(config)`：验证 WDC Products `80pair` JSONL-GZIP 文件。
- `validate_abt_buy(config)`：验证 CompERBench `abt-buy` CSV 文件和 records 文件。
- `audit_dataset(config_path)`：根据 `dataset_id` 自动选择对应 validator。

输入：

- dataset config JSON；
- `data/raw/` 下的原始文件。

输出：

- 一个 summary dictionary，包含 split 名称、pair 数量和 label counts。

数据流：

1. 读取 config。
2. 根据 `dataset_id` 选择 validator。
3. 检查 raw 文件是否存在。
4. 读取 CSV 或 JSONL-GZIP。
5. 检查必要字段。
6. 统计 label counts。
7. 与 config 中的 audited counts 对比。
8. 返回 summary。

关键实现选择：

- WDC Products 使用 `gzip` 和 `json` 逐行读取 `.json.gz`。
- CompERBench 使用 `csv.DictReader` 读取 CSV。
- CSV 默认先尝试 UTF-8；如果失败，回退到 `cp1252` 和 `latin-1`。这是因为 `abt-buy` record files 中存在非 UTF-8 字符。
- 当前阶段只验证 schema 和计数，不生成 processed data。

如何运行：

```powershell
python scripts/audit_dataset.py configs/datasets/wdc_products_80pair.json
python scripts/audit_dataset.py configs/datasets/comperbench_abt_buy.json
```

## `scripts/audit_dataset.py`

文件职责：

提供命令行入口，方便对某个 dataset config 运行 raw schema validation。

输入：

- 一个 config JSON 路径。

输出：

- JSON 格式的 validation summary。

示例：

```powershell
python scripts/audit_dataset.py configs/datasets/wdc_products_80pair.json
```

## `tests/test_data_validation.py`

文件职责：

测试 dataset config loading 和 raw file validation。

测试内容：

- WDC config 可以被加载；
- abt-buy config 可以被加载；
- 如果本地 raw audit files 存在，则验证 WDC raw schema 和 counts；
- 如果本地 raw audit files 存在，则验证 abt-buy raw schema、counts 和 record counts。

当前测试结果：

```text
Ran 4 tests in 0.512s
OK
```

## 当前限制

- 还没有 feature engineering。
- 还没有 split、sampling、model 或 metric 代码。
- 还没有最终 processed feature table。
- raw data 和 interim data 文件被 `.gitignore` 排除，因此在新环境中运行 validation 或 export 前需要先下载对应 raw 数据并重新生成 interim 文件。

## `src/entity_matching/data/pairs.py`

文件职责：

把不同原始格式的数据转换成统一的内存表示 `PairRecord`。

主要对象和函数：

- `PairRecord`：标准化后的记录对。
- `load_pair_table(config_path, split)`：读取一个 dataset split，并返回 `list[PairRecord]`。
- `summarize_pair_table(pair_table)`：统计 pair 数量、label counts 和 hard-negative counts。

标准化字段：

- `dataset_id`
- `split`
- `pair_id`
- `left_record_id`
- `right_record_id`
- `left_entity_id`
- `right_entity_id`
- `label`
- `left_attributes`
- `right_attributes`
- `is_hard_negative`

数据流：

1. 读取 dataset config。
2. 根据 `dataset_id` 选择 WDC 或 abt-buy loader。
3. WDC 直接从 pair-wise JSONL-GZIP 行中抽取左右字段。
4. abt-buy 先读取左右 source records，再用 `source_id` 和 `target_id` join 到 pair labels。
5. 输出统一的 `PairRecord` 列表。

关键实现选择：

- `label` 统一为整数：`1` 表示 match，`0` 表示 non-match。
- WDC 的 `cluster_id_left/right` 保留为 entity IDs。
- abt-buy 没有可靠 entity IDs，所以 `left_entity_id/right_entity_id` 设为 `None`。
- abt-buy 没有 hard-negative 标记，所以 `is_hard_negative` 设为 `None`。

如何运行：

```powershell
python scripts/preview_pair_table.py configs/datasets/wdc_products_80pair.json train_small --examples 1
python scripts/preview_pair_table.py configs/datasets/comperbench_abt_buy.json train --examples 1
```

当前测试结果：

```text
Ran 6 tests in 0.325s
OK
```

## `src/entity_matching/data/quality.py`

文件职责：

为 normalized pair table 生成数据质量报告。

主要函数：

- `report_pair_table_quality(pair_table)`：生成单个 split 的质量报告。
- `report_split_overlaps(split_tables)`：检查多个 split 之间的 pair、record 和 entity overlap。
- `report_dataset_quality(config_path)`：读取一个 dataset config 中的所有 split，并生成完整质量报告。

报告内容：

- label counts；
- hard-negative counts；
- missing attribute counts；
- duplicate pair IDs；
- split 间 pair ID overlap；
- split 间 record ID overlap；
- split 间 entity ID overlap，如果 entity ID 存在。

如何运行：

```powershell
python scripts/report_data_quality.py configs/datasets/wdc_products_80pair.json
python scripts/report_data_quality.py configs/datasets/comperbench_abt_buy.json
```

当前测试结果：

```text
Ran 8 tests in 0.754s
OK
```

关键发现：

- WDC `test_unseen_100un` 与 `train_small` / `valid_small` 没有 pair、record 或 entity overlap。
- WDC mixed split 与 train/validation 有部分 overlap，必须按官方 mixed variant 解释。
- `abt-buy` 有 split 内 duplicate pairs 和跨 split overlap，不适合 unseen-entity claim。

## `src/entity_matching/data/interim.py`

文件职责：

把 normalized `PairRecord` 导出为可再生成的 interim JSONL 文件。

主要函数：

- `pair_to_dict(pair)`：把 `PairRecord` 转成带 `schema_version` 的 dictionary。
- `write_pair_table_jsonl(pair_table, output_path)`：把一个 split 写成 JSON Lines。
- `export_dataset_interim(config_path, output_root)`：导出一个 dataset config 中的所有 split。

Interim schema：

- schema version：`pair_table_v1`；
- 每行一个 pair；
- UTF-8 JSON Lines；
- 输出路径：`data/interim/<dataset_id>/<split>.jsonl`。

如何运行：

```powershell
python scripts/export_interim_pairs.py configs/datasets/wdc_products_80pair.json
python scripts/export_interim_pairs.py configs/datasets/comperbench_abt_buy.json
```

当前验证：

- `data/interim/comperbench_abt_buy/train.jsonl` 有 5,010 行；
- `data/interim/wdc_products_80pair/test_unseen_100un.jsonl` 有 4,500 行；
- `data/interim/` 被 `.gitignore` 排除。

当前测试结果：

```text
Ran 10 tests in 1.096s
OK
```

## `src/entity_matching/preprocessing/text.py`

文件职责：

为 normalized pair attributes 提供文本标准化原子函数。它不计算 similarity features，也不训练模型。

主要对象和函数：

- `TEXT_STANDARDIZATION_VERSION`：当前文本标准化版本，值为 `text_standardization_v1`。
- `normalize_text(value)`：处理 HTML entity、Unicode NFKC、大小写、空白和常见缺失值。
- `tokenize_text(value)`：把文本切成 lowercase alphanumeric tokens。
- `extract_numeric_tokens(value)`：抽取数字 token，供后续 numeric agreement features 使用。
- `normalize_attributes(attributes)`：对一个 attribute dictionary 的所有值做标准化。
- `build_text_profile(attributes)`：生成 normalized attributes、combined text、tokens 和 numeric tokens。
- `standardize_pair_payload(pair_payload)`：从 interim pair-table payload 生成左右两侧 text profiles。

关键实现选择：

- 继续使用 Python 标准库，暂时不引入 pandas、scikit-learn 或 NLP 依赖。
- raw attributes 保留不变，标准化结果作为额外 profile 添加。
- 当前阶段只做 preprocessing primitives，不生成最终 processed feature table。

如何运行测试：

```powershell
python -m unittest tests.test_preprocessing
```

当前测试结果：

```text
Ran 7 tests in 0.000s
OK
```

## `scripts/preview_text_standardization.py`

文件职责：

从 `data/interim/<dataset_id>/<split>.jsonl` 读取少量样本，展示标准化后的左右 text profiles，方便人工检查 preprocessing 是否符合预期。

示例：

```powershell
python scripts/preview_text_standardization.py data/interim/comperbench_abt_buy/train.jsonl --examples 1
```

## `src/entity_matching/features/string_similarity.py`

文件职责：

提供第一版 string-similarity feature primitives。它把 `text_standardization_v1` 生成的左右 text profiles 转成小型 feature dictionary，但当前还不写 full processed feature table。

主要对象和函数：

- `STRING_FEATURE_VERSION`：当前 feature 版本，值为 `string_similarity_v1`。
- `exact_match_score(left, right)`：非空且相等才返回 `1.0`；两个缺失值不算 match signal。
- `jaccard_similarity(left_tokens, right_tokens)`：计算 token set Jaccard。
- `numeric_token_overlap(left_numeric_tokens, right_numeric_tokens)`：计算 containment-style numeric overlap。
- `levenshtein_distance(left, right)`：标准 Levenshtein edit distance。
- `edit_similarity_ratio(left, right)`：把 edit distance 归一化到 `[0.0, 1.0]`。
- `build_string_similarity_features(standardized_pair_payload)`：从 standardized pair payload 生成 combined 和 attribute-level features。

当前 feature families：

- combined text exact match；
- combined text edit similarity；
- combined token Jaccard；
- combined numeric-token overlap；
- shared attribute-level exact match；
- shared attribute-level edit similarity；
- shared attribute-level token Jaccard；
- shared attribute-level numeric-token overlap。

关键实现选择：

- 继续使用 Python 标准库，不引入大型依赖。
- Attribute base names 会去掉 `_left` / `_right` 后缀。
- Feature names 会规范成 snake_case，例如 `priceCurrency` 变成 `price_currency`。
- 当前阶段只预览 feature dictionary，不生成最终训练用 feature table。

如何运行测试：

```powershell
python -m unittest tests.test_string_similarity_features
python -m unittest discover tests
```

当前测试结果：

```text
Ran 24 tests in 1.220s
OK
```

## `scripts/preview_string_features.py`

文件职责：

从 `data/interim/<dataset_id>/<split>.jsonl` 读取少量样本，先应用 `text_standardization_v1`，再输出 `string_similarity_v1` feature dictionary，方便人工检查 feature 语义。

示例：

```powershell
python scripts/preview_string_features.py data/interim/comperbench_abt_buy/train.jsonl --examples 1
python scripts/preview_string_features.py data/interim/wdc_products_80pair/train_small.jsonl --examples 1
```

## `src/entity_matching/features/table.py`

文件职责：

把 `data/interim/<dataset_id>/<split>.jsonl` 中的 normalized pairs 批量转换成 processed feature-table CSV。

主要对象和函数：

- `FEATURE_TABLE_SCHEMA_VERSION`：当前 feature-table schema，值为 `feature_table_v1`。
- `FeatureTableError`：feature table schema validation 失败时抛出的错误。
- `load_interim_jsonl(path)`：读取 interim JSONL。
- `build_feature_row(pair_payload)`：把一条 pair payload 转成扁平 feature row。
- `build_feature_rows(pair_payloads)`：批量生成 feature rows。
- `validate_feature_rows(rows)`：检查 row 非空、columns 一致、label 合法、feature 值为 `[0.0, 1.0]` 内的数字。
- `write_feature_table_csv(rows, output_path)`：写出 CSV。
- `export_feature_table(interim_path, output_csv_path)`：导出单个 split。
- `export_dataset_feature_tables(config_path, interim_root, output_root)`：导出一个 dataset config 中的所有 split。

输出：

- `data/processed/<dataset_id>/<split>.csv`
- `data/processed/<dataset_id>/<split>.summary.json`

CSV metadata columns：

- `dataset_id`
- `split`
- `pair_id`
- `label`

Summary JSON 记录：

- schema version；
- text standardization version；
- feature version；
- row count；
- label counts；
- feature columns。

关键实现选择：

- processed feature tables 是可再生成产物，被 `.gitignore` 排除。
- 当前仍然不训练模型。
- `edit_similarity_ratio` 对长文本做 64 字符边界，避免 pure-Python Levenshtein 在 description 上过慢。

如何运行：

```powershell
python scripts/export_feature_tables.py configs/datasets/comperbench_abt_buy.json
python scripts/export_feature_tables.py configs/datasets/wdc_products_80pair.json
```

当前测试结果：

```text
Ran 29 tests in 13.481s
OK
```

## `scripts/export_feature_tables.py`

文件职责：

命令行导出一个 dataset config 中所有 split 的 processed feature tables，并打印 JSON summary。

示例：

```powershell
python scripts/export_feature_tables.py configs/datasets/wdc_products_80pair.json
```

## `src/entity_matching/splitting/manifest.py`

文件职责：

读取并验证 processed feature tables，生成 model-ready split manifest。

主要对象和函数：

- `FeatureTableSplit`：一个 split 的 CSV path、summary path、row count、label counts、feature columns 和 duplicate pair 统计。
- `SplitManifest`：一个 dataset 的多个 validated splits。
- `load_feature_table_summary(path)`：读取 `.summary.json`。
- `load_feature_table_rows(path)`：读取 CSV，并把 label 转成 `int`、feature values 转成 `float`。
- `validate_feature_table_file(csv_path, summary_path)`：验证 CSV 与 summary 是否一致。
- `build_split_manifest(config_path, processed_root, split_names)`：为一组 split 生成 manifest。

验证内容：

- summary 必须包含 schema、dataset、split、row count、label counts、feature columns；
- CSV row count 必须等于 summary；
- label counts 必须等于 summary；
- feature columns 必须一致；
- feature values 必须在 `[0.0, 1.0]`；
- duplicate pair IDs 会被记录，不会阻止 report 生成。

## `src/entity_matching/splitting/guards.py`

文件职责：

在模型训练前生成 split guard report，并在需要时 fail closed。

主要函数：

- `build_split_guard_report(config_path, processed_root, split_names)`：生成完整 guard report。
- `assert_no_leakage(report, require_pair_disjoint, require_record_disjoint, require_entity_disjoint)`：根据选择的严格程度抛出 `SplitGuardError`。
- `compare_pair_sets(manifest)`：检查 processed feature tables 的 pair ID overlap。
- `compare_record_and_entity_sets(config_path, split_names)`：基于 normalized pair tables 检查 record/entity overlap。

关键发现：

- WDC `train_small` 和 `test_unseen_100un` 可通过严格 pair、record、entity disjoint check。
- WDC `train_small` 和 `valid_small` 有 500 个 entity overlap。
- `abt-buy` train 有 duplicate pair IDs，train/test 有 pair 和 record overlap。

## `scripts/check_split_guards.py`

文件职责：

命令行运行 split guard report。

示例：

```powershell
python scripts/check_split_guards.py configs/datasets/wdc_products_80pair.json --splits train_small test_unseen_100un --require-record-disjoint --require-entity-disjoint
python scripts/check_split_guards.py configs/datasets/comperbench_abt_buy.json --splits train test --report-only
```

## `src/entity_matching/models/matrix.py`

文件职责：

把已经通过 feature-table validation 和 split guards 的 CSV 转成模型将来要用的 `X`、`y` 和 `pair_ids`。当前不训练模型。

主要对象和函数：

- `ModelMatrix`：一个 split 的 `X`、`y`、`pair_ids`、feature columns 和 label counts。
- `ModelMatrixBundle`：多个 split 的矩阵，加上 guard report。
- `load_model_matrix(manifest, split_name)`：从 validated manifest 读取一个 split。
- `load_model_matrix_bundle(config_path, ...)`：先运行 guard，再读取多个 split。
- `summarize_model_matrix(matrix)`：返回摘要，不打印完整 `X`。

关键实现选择：

- 继续使用 Python list，不引入 NumPy、pandas 或 scikit-learn。
- `pair_ids` 与 `X` / `y` 行对齐，方便后续 error analysis。
- 如果 strict guards 不通过，matrix loading 会 fail closed。
- `abt-buy` 这类有 known leakage 的数据只能在显式允许时做 diagnostic preview。

## `scripts/preview_model_matrix.py`

文件职责：

预览 model-ready matrix 的 shape、feature columns、label counts 和第一条 pair，不进行训练。

示例：

```powershell
python scripts/preview_model_matrix.py configs/datasets/wdc_products_80pair.json --splits train_small test_unseen_100un --require-record-disjoint --require-entity-disjoint
```

## `configs/models/baseline_traditional.json`

文件职责：

记录计划中的 traditional baseline families 和随机种子。当前状态是 `draft_not_trained`，不代表模型已经实现或训练。

## `src/entity_matching/experiments/dry_run.py`

文件职责：

验证第一轮 baseline protocol 是否能安全进入训练前状态，但不 fit 模型。

主要函数：

- `load_experiment_config(path)`：读取 dry-run experiment config。
- `validate_experiment_config(config)`：强制当前只允许 `dry_run_only`，并且 `fit_allowed` 必须为 `false`。
- `baseline_dependency_status()`：检查 `sklearn`、`numpy`、`pandas` 是否可用，但不训练。
- `run_experiment_dry_run(config_path)`：运行 config validation、dependency check、split guards 和 matrix loading，返回 summary。

关键实现选择：

- 即使本地 `sklearn` 可用，也不调用 estimator。
- 如果 validation/threshold protocol 未锁定，`ready_for_fit` 必须保持 `false`。

## `scripts/dry_run_baseline_protocol.py`

文件职责：

命令行运行 baseline protocol dry-run。

示例：

```powershell
python scripts/dry_run_baseline_protocol.py configs/experiments/wdc_unseen_baseline_dry_run.json
```

## `configs/experiments/wdc_unseen_baseline_dry_run.json`

文件职责：

记录第一轮 WDC unseen baseline 的训练前协议。当前只允许 dry-run，不允许 fit。

## `src/entity_matching/models/factory.py`

文件职责：

从 `configs/models/baseline_traditional.json` 实例化 traditional baseline estimators，但不 fit。

主要函数：

- `load_model_config(path)`：读取 model config。
- `get_model_definition(model_config, model_id)`：查找一个 model definition。
- `instantiate_model(model_definition, random_seed)`：创建 sklearn estimator。
- `instantiate_model_from_config(config_path, model_id, random_seed)`：从 config 直接创建 estimator。
- `describe_estimator(estimator)`：返回 estimator class、module、parameters 和 `is_fitted`。

支持的 model families：

- `LogisticRegression`
- `RandomForestClassifier`
- `SupportVectorMachine`，对应 sklearn `SVC`

## `src/entity_matching/experiments/training_guard.py`

文件职责：

在任何训练入口调用 `fit()` 前检查实验配置是否允许训练。

主要函数：

- `assert_fit_allowed(experiment_config)`
- `assert_fit_allowed_from_config(config_path)`

当前行为：

- `configs/experiments/wdc_unseen_baseline_dry_run.json` 会被拒绝训练，因为 `fit_allowed` 是 `false`。

## `scripts/preview_model_factory.py`

文件职责：

预览 baseline estimators 的配置和 fitted 状态，不训练模型。

示例：

```powershell
python scripts/preview_model_factory.py configs/models/baseline_traditional.json --seed 13
```

## `src/entity_matching/evaluation/metrics.py`

文件职责：

提供二分类 metric primitives。当前只用于 toy scores 和未来评估脚手架，不包含真实模型结果。

主要函数：

- `apply_threshold(scores, threshold)`：把 `[0.0, 1.0]` 分数转成 `0/1` 预测。
- `binary_confusion_matrix(y_true, y_pred)`：计算 `tp`、`fp`、`tn`、`fn`。
- `precision_score(confusion)`。
- `recall_score(confusion)`。
- `f1_score(precision, recall)`。
- `evaluate_binary_scores(y_true, scores, threshold)`：在固定 threshold 下返回完整指标 summary。

关键实现选择：

- 正类是 `1`，也就是 `match`。
- score 和 threshold 必须在 `[0.0, 1.0]`。
- 如果 precision 或 recall 分母为 0，返回 `0.0`。

## `src/entity_matching/evaluation/thresholds.py`

文件职责：

只允许基于 validation split 选择 threshold。

主要函数：

- `select_threshold_on_validation(y_true, scores, candidate_thresholds, selection_metric, split_name)`。

关键实现选择：

- 当前只支持 `selection_metric="f1"`。
- 如果 `split_name` 不是 `validation`，直接抛出错误。
- 默认候选 threshold 是 `0.00` 到 `1.00`，步长 `0.01`。

## `scripts/preview_threshold_metrics.py`

文件职责：

用 toy scores 演示 metric 和 threshold-selection 输出格式。它不读取项目预测，也不产生实验结果。

## `configs/experiments/wdc_unseen_baseline_protocol.json`

文件职责：
锁定第一轮 WDC unseen baseline 的 split 角色和 threshold-selection 规则，但仍然不允许训练模型。

当前 split 角色：

- `train_small`：训练 split；
- `valid_small`：validation split，只用于选择 threshold；
- `test_unseen_100un`：最终 test split，只用于最终评估。

关键限制：

- `fit_allowed` 仍然是 `false`；
- test split 不能用于 threshold selection；
- test split 不能用于 model selection；
- `train_small` 和 `valid_small` 有已知 entity overlap，所以不能声称 train-validation entity-disjoint；
- `test_unseen_100un` 必须同时和 train、validation 保持 pair、record、entity disjoint。

## `src/entity_matching/experiments/protocol.py`

文件职责：
在真正训练模型之前，验证 protocol-only experiment config 是否安全。

主要函数：

- `load_protocol_config(path)`：读取并验证 protocol config；
- `validate_protocol_config(config)`：检查字段、split 角色、threshold selection、test-use policy 和 random seeds；
- `validate_protocol_guards(config_path)`：运行 split guard，确认 development splits 和 test split 之间没有 pair、record、entity leakage。

这个模块不会调用 `fit()`，也不会生成预测或实验结果。

## `scripts/validate_experiment_protocol.py`

文件职责：
命令行验证 protocol-only config，并输出 guard summary。

示例：

```powershell
python scripts/validate_experiment_protocol.py configs/experiments/wdc_unseen_baseline_protocol.json
```

当前用途：
确认第一轮 baseline 的实验规则已经可以被代码检查，而不只是写在文档里。
