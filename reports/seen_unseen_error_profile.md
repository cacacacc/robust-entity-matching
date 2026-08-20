# Seen/Unseen All-Seed Error Profile

本报告聚合已有 raw prediction CSV；没有重新训练模型，也没有使用 test set 做模型选择。

## Model-Level Stability

| Model | Seeds | Seen FP Mean | Unseen FP Mean | Seen-Unseen FP | Seeds Seen FP Higher | Unseen-Seen Precision | Unseen-Seen F1 | Seeds Unseen F1 Higher |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `logistic_regression` | `5` | `483.000000` | `388.000000` | `95.000000` | `5` | `0.059570` | `0.048169` | `5` |
| `random_forest` | `5` | `505.600000` | `394.400000` | `111.200000` | `5` | `0.068812` | `0.058274` | `5` |
| `svm` | `5` | `521.000000` | `433.600000` | `87.400000` | `5` | `0.052541` | `0.046620` | `5` |

## Seed-Level Rows

| Model | Seed | Seen FP | Unseen FP | Seen-Unseen FP | Seen F1 | Unseen F1 | Unseen-Seen F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `logistic_regression` | `13` | `483` | `388` | `95` | `0.487692` | `0.535862` | `0.048169` |
| `logistic_regression` | `29` | `483` | `388` | `95` | `0.487692` | `0.535862` | `0.048169` |
| `logistic_regression` | `47` | `483` | `388` | `95` | `0.487692` | `0.535862` | `0.048169` |
| `logistic_regression` | `71` | `483` | `388` | `95` | `0.487692` | `0.535862` | `0.048169` |
| `logistic_regression` | `101` | `483` | `388` | `95` | `0.487692` | `0.535862` | `0.048169` |
| `random_forest` | `13` | `589` | `454` | `135` | `0.486449` | `0.557823` | `0.071374` |
| `random_forest` | `29` | `481` | `378` | `103` | `0.505712` | `0.560656` | `0.054944` |
| `random_forest` | `47` | `425` | `335` | `90` | `0.515249` | `0.564058` | `0.048810` |
| `random_forest` | `71` | `480` | `370` | `110` | `0.502674` | `0.560794` | `0.058120` |
| `random_forest` | `101` | `553` | `435` | `118` | `0.497860` | `0.555985` | `0.058124` |
| `svm` | `13` | `542` | `447` | `95` | `0.481050` | `0.526070` | `0.045020` |
| `svm` | `29` | `506` | `426` | `80` | `0.484940` | `0.530159` | `0.045219` |
| `svm` | `47` | `535` | `441` | `94` | `0.482405` | `0.528538` | `0.046133` |
| `svm` | `71` | `509` | `427` | `82` | `0.483847` | `0.530903` | `0.047057` |
| `svm` | `101` | `513` | `427` | `86` | `0.482397` | `0.532067` | `0.049670` |

## Interpretation

- 如果 `Seeds Seen FP Higher` 接近 seed 总数，说明 seen split 的 precision penalty 不是单个 seed 的偶然现象。
- 如果 `Seeds Unseen F1 Higher` 接近 seed 总数，说明 unseen > seen 的方向在该模型上稳定。
- 这些结果仍然是 descriptive analysis；最终 robustness claim 仍应以 entity-disjoint unseen split 为主。
