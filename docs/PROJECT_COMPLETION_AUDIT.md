# Project Completion Audit

Date: 2026-08-20

## 结论

当前项目可以结束为一个完整的本科研究 MVP。

更准确地说：

- 可以结束：traditional-baseline research MVP。
- 不建议继续扩：新模型、Transformer、大数据集、更多训练网格。
- 还可以做但不是必须：生成正式图片、写完整最终论文、整理 GitHub commit/push。

本项目已经具备申请/面试展示所需的核心内容：清晰研究问题、可复现实验协议、公开数据、传统 baseline、class-ratio 分析、seen/unseen 分析、错误分析、审计脚本、测试、结果综合和 report-ready 英文叙事。

## MVP 完成度审查

| Requirement | Status | Evidence |
|---|---|---|
| Public entity-matching dataset | Done | WDC Products `80pair`; CompERBench `abt-buy` audited as secondary pipeline dataset |
| Raw-data integrity | Done | Raw/interim/processed data are ignored; raw data not edited |
| Schema audit | Done | `docs/DATASET_AUDIT.md`, dataset configs |
| Feature pipeline | Done | `src/entity_matching/features/`, `scripts/export_feature_tables.py` |
| Split leakage checks | Done | `scripts/check_split_guards.py`, `docs/EXPERIMENT_PROTOCOL.md` |
| Traditional baselines | Done | Logistic Regression, Random Forest, SVM |
| Validation-only threshold selection | Done | Protocol and raw prediction artifacts include validation-selected thresholds |
| Five seeds | Done | `13`, `29`, `47`, `71`, `101` |
| Fixed unseen evaluation | Done | `test_unseen_100un` |
| Class-ratio experiments | Done | fixed-test, matched train/test, full train/test ratio grid |
| Seen/unseen diagnostic | Done | `docs/PHASE_3_SEEN_VS_UNSEEN_AUDIT.md` |
| Error analysis | Done | RF qualitative analysis and all-seed seen/unseen error profile |
| Result audits | Done | baseline, class-ratio, train/test grid audits |
| Tests | Done | `python -m unittest discover tests` passes |
| Result synthesis | Done | `docs/PHASE_3_RESULTS_SYNTHESIS.md`, `reports/final_results_narrative.md` |
| Public README | Done | `README.md` updated to current MVP state |
| Dependency file | Done | `requirements.txt` records `scikit-learn==1.8.0` |

## Research Questions: End-State Assessment

### RQ1: Class Ratio

Status: sufficiently answered for MVP.

Evidence:

- Fixed-test class-ratio experiment.
- Matched train/test class-ratio diagnostic.
- Full train/test ratio grid.
- Reports:
  - `reports/class_ratio_results.md`
  - `reports/class_ratio_protocol_comparison.md`
  - `reports/train_test_ratio_grid_analysis.md`

Main answer:

Training ratio matters, but evaluation ratio has a stronger visible effect on F1 and precision in the current WDC setup.

### RQ2: Seen/Unseen Entity Shift

Status: answered as an official WDC seen/unseen diagnostic, with caveats.

Evidence:

- Seen baseline run.
- Unseen baseline run.
- Seen/unseen comparison.
- All-seed false-positive profile.
- Reports:
  - `reports/seen_vs_unseen_comparison.md`
  - `reports/seen_unseen_error_profile.md`
  - `docs/PHASE_3_SEEN_UNSEEN_DIFFICULTY_ANALYSIS.md`

Main answer:

Unseen did not score lower than seen in this setup. The official seen diagnostic split produced more false positives across all inspected model-seed rows. Therefore, seen/unseen status is not the same thing as easy/hard split difficulty.

### RQ3: Hard Negatives

Status: partially answered; enough for MVP interpretation, not enough for a separate hard-negative-sampling claim.

Evidence:

- WDC hard-negative flags are preserved.
- RF seed `13` qualitative error analysis found false positives are mostly official hard negatives.
- Seen/unseen error profile supports a false-positive-centered interpretation.

Limit:

The project did not run a separate hard-negative-sampling intervention against random negative sampling. Therefore, the final report should not claim that hard-negative sampling improves or hurts unseen generalization. It may claim that hard negatives explain many observed false positives.

Decision:

This is acceptable for ending the MVP because the main completed contribution shifted toward protocol sensitivity: class ratio, evaluation ratio, and seen/unseen split composition.

## What Is Still Missing?

### Must-Have Before Ending

None.

The minimum research MVP is complete.

### Should-Have Before Public GitHub Push

- Review tracked docs for private/local-only wording.
- Decide whether to commit `reports/*.csv` and `reports/*.md`.
- Keep `results/`, `data/`, and detailed raw example reports ignored.
- Run `git status --short`.
- Make one clean commit.
- Push only after explicit user approval.

### Nice-To-Have For A Stronger Final Submission

- Generate final figures from existing CSVs:
  - F1 heatmap from `reports/train_test_ratio_grid_f1_matrix.csv`.
  - Precision-drop bar chart from `reports/train_test_ratio_grid_test_sensitivity.csv`.
  - Seen/unseen FP comparison from `reports/seen_unseen_error_profile_by_model.csv`.
- Expand `reports/final_results_narrative.md` into a full technical report with Introduction, Methods, Results, Discussion, Limitations, and References.
- Add a small `Makefile` or `scripts/reproduce_core_results.py` that lists the intended reproduction order.

These are presentation polish tasks, not blockers.

## Non-Goals To Stop Here

Do not add these before ending the MVP:

- Transformer or large-language-model baselines.
- Larger WDC full-corpus experiments.
- New datasets beyond the audited WDC/CompERBench scope.
- Paid APIs or cloud compute.
- Hyperparameter sweeps beyond the current baseline protocol.
- Changing research questions to chase a higher score.

Adding any of these now would expand the project rather than complete it.

## Final Claim Boundary

Safe final claim:

> On WDC Products `80pair`, traditional entity-matching baselines are sensitive to evaluation class ratio and split composition. Random Forest is the strongest tested traditional baseline under the fixed unseen protocol. Evaluation class ratio has a stronger visible effect on F1 and precision than training ratio alone. The official seen diagnostic split produces more false positives than the unseen split across all inspected model-seed rows.

Unsafe final claims:

- Unseen entities are always harder.
- Balanced training always improves entity matching.
- Random Forest is universally best for entity matching.
- Hard-negative sampling improves unseen generalization.
- The seen split is leakage-free.

## End Decision

Recommendation: stop experimental work here and mark the research MVP complete.

Next project mode should be writing/presentation, not more experiments.

