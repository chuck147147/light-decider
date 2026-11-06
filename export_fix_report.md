# GitHub Export Fix Report

本报告替代已移出导出包的 `export_report.md`，记录导出包收尾改动、模型隐私扫描与运行冒烟。

## 收尾改动

- 将现役 round-4 模型复制到 `artifacts/decisioner_round4_v1_2026-11-05.joblib`，与 `light_decider/predict.py` 的默认加载路径一致。源文件与副本 SHA-256 相同：`6eff1a818db972bf887ed885f1cad4162dc5cef69ebdee0fb4f7ac32c37b286b`；大小 3,336,001 字节。
- 模型复制前使用 GNU `strings` 扫描 ASCII 与 UTF-16LE 可读字符串，共读取 69,506 行；本机路径、账户名及邮箱样式字符串命中数均为 **0**。扫描未打印或记录字符串内容。
- 删除包内旧 `export_report.md`，由本文件接替。
- 补入 `try_router_semantic.py`：导出包的 `try_router.py` 直接导入该模块，加入此原项目依赖后可使用既有入口；文件逻辑未改。

## 冒烟运行

从导出目录运行 `py -3 -X utf8 try_router.py`，输入示例：

```text
解释一下哈希表为什么平均查询是 O(1)
```

结果：退出码 0；加载 `decisioner_round4_v1_2026-11-05.joblib`；动作 `decide`，建议路线 `decide`；分数为 clarify `0.17415687431857557`、codex `0.14372309424688465`、decide `0.6821200314345398`；`automatic_dispatch_allowed` 为 `false`。

## 既有隐私清洗记录

清洗前共命中 141 项，涉及 33 个文件；清洗后全包扫描为 0。分类计数：IP地址 11、密钥样式 1、本机绝对路径 19、用户名/标注者代称 108、邮箱 2。命中表仅记录相对文件名、行号与类型，不包含匹配值。

### 清洗前命中清单

| 文件与内部位置 | 行号 | 类型 |
|---|---:|---|
| 文件与内部位置 | 行号 | 类型 |
|---|---:|---|
| `data/light_decider_independent_blind_holdout_v1_2026-11-03/light_decider_blind_label_sheet_v1_frozen_2026-11-03.xlsx!xl/workbook.xml` | 2 | 本机绝对路径 |
| `data/light_decider_independent_blind_holdout_v1_2026-11-03/light_decider_blind_label_sheet_v1_frozen_2026-11-03.xlsx!xl/workbook.xml` | 2 | 用户名/标注者代称 |
| `data/light_decider_independent_blind_holdout_v2_2026-11-04/blind_holdout_v2_user_labels_frozen_2026-11-04.xlsx!xl/workbook.xml` | 2 | 本机绝对路径 |
| `data/light_decider_independent_blind_holdout_v2_2026-11-04/blind_holdout_v2_user_labels_frozen_2026-11-04.xlsx!xl/workbook.xml` | 2 | 用户名/标注者代称 |
| `data/light_decider_independent_blind_holdout_v2_2026-11-04/freeze_manifest_v2_user_labels_2026-11-04.json` | 15 | 本机绝对路径 |
| `data/light_decider_independent_blind_holdout_v2_2026-11-04/freeze_manifest_v2_user_labels_2026-11-04.json` | 15 | 用户名/标注者代称 |
| `data/light_decider_independent_blind_holdout_v3_2026-11-04/blind_holdout_v3_codex_reference_SEALED.jsonl` | 1 | 用户名/标注者代称 |
| `data/light_decider_independent_blind_holdout_v3_2026-11-04/evaluation_report_v3.md` | 6 | 用户名/标注者代称 |
| `data/light_decider_independent_blind_holdout_v3_2026-11-04/freeze_manifest_v3.md` | 17 | 用户名/标注者代称 |
| `data/light_decider_independent_blind_holdout_v3_2026-11-04/freeze_manifest_v3_template.md` | 3 | 用户名/标注者代称 |
| `data/light_decider_independent_blind_holdout_v3_2026-11-04/generation_report_v3.md` | 82-83 | 用户名/标注者代称 |
| `data/light_decider_independent_blind_holdout_v4_2026-11-05/evaluation_report_v4.md` | 8 | 用户名/标注者代称 |
| `data/light_decider_independent_blind_holdout_v4_2026-11-05/freeze_manifest_v4.md` | 16 | 用户名/标注者代称 |
| `data/light_decider_independent_blind_holdout_v5_2026-11-06/evaluation_report_v5.md` | 5 | 用户名/标注者代称 |
| `data/light_decider_independent_blind_holdout_v5_2026-11-06/freeze_manifest_v5.md` | 3 | 用户名/标注者代称 |
| `data/light_decider_independent_blind_holdout_v6_2026-11-06/evaluation_report_v6.md` | 5, 106, 108 | 用户名/标注者代称 |
| `data/light_decider_independent_blind_holdout_v6_2026-11-06/freeze_manifest_v6.md` | 3, 28 | 用户名/标注者代称 |
| `data/training_round4_v1_2026-11-05/dev.jsonl` | 95, 99-100, 114-115 | IP地址 |
| `data/training_round4_v1_2026-11-05/dev.jsonl` | 101, 105 | 本机绝对路径 |
| `data/training_round4_v1_2026-11-05/train.jsonl` | 399, 402, 404, 451, 472 | IP地址 |
| `data/training_round4_v1_2026-11-05/train.jsonl` | 448 | 密钥样式 |
| `data/training_round4_v1_2026-11-05/train.jsonl` | 421, 433-434, 438, 442, 467-468 | 本机绝对路径 |
| `data/training_round4_v1_2026-11-05/train.jsonl` | 517-576 | 用户名/标注者代称 |
| `data/training_round4_v1_2026-11-05/train.jsonl` | 448, 450 | 邮箱 |
| `docs/reports/activation_note_v3_2b.md` | 5, 7, 15 | 用户名/标注者代称 |
| `docs/reports/activation_note_v3_3.md` | 5 | 用户名/标注者代称 |
| `docs/reports/clean_replay_round2_v3_2b.md` | 3 | 用户名/标注者代称 |
| `docs/reports/install_and_answer_worker_report.md` | 129 | IP地址 |
| `docs/reports/install_and_answer_worker_report.md` | 8 | 本机绝对路径 |
| `docs/reports/install_and_answer_worker_report.md` | 8 | 用户名/标注者代称 |
| `docs/reports/phase2_codex_live_report.md` | 24, 26, 60, 65, 77, 79 | 本机绝对路径 |
| `docs/reports/phase2_codex_live_report.md` | 24, 26, 60, 65, 77-79 | 用户名/标注者代称 |
| `docs/reports/promotion_note_round4.md` | 3, 7 | 用户名/标注者代称 |
| `docs/reports/round4_training_report.md` | 13 | 用户名/标注者代称 |
| `docs/reports/v3_evaluation_report_v3.md` | 6 | 用户名/标注者代称 |
| `docs/reports/v3_freeze_manifest_v3.md` | 17 | 用户名/标注者代称 |
| `docs/reports/v3_freeze_manifest_v3_template.md` | 3 | 用户名/标注者代称 |
| `docs/reports/v3_generation_report_v3.md` | 82-83 | 用户名/标注者代称 |
| `docs/reports/v4_evaluation_report_v4.md` | 8 | 用户名/标注者代称 |
| `docs/reports/v4_freeze_manifest_v4.md` | 16 | 用户名/标注者代称 |
| `docs/reports/v5_evaluation_report_v5.md` | 5 | 用户名/标注者代称 |
| `docs/reports/v5_freeze_manifest_v5.md` | 3 | 用户名/标注者代称 |
| `docs/reports/v6_evaluation_report_v6.md` | 5, 106, 108 | 用户名/标注者代称 |
| `docs/reports/v6_freeze_manifest_v6.md` | 3, 28 | 用户名/标注者代称 |

### 清洗后命中清单

无。

训练数据隐私清洗说明见 `data/README.md`；六套冻结件原件哈希和公开副本哈希见 `HASH_MANIFEST.md`。两份 Excel 的题目/标签单元格未改，只移除了工作簿级路径元数据；冻结标签 JSONL 与原件字节一致。

Codex A 演练 thread 样例保留 1 条清洗记录；Codex B/C 和 Answer Worker 失败 thread 示例已移除。

## 最终包状态

目录包含 `light_decider/`、`artifacts/`、`data/`、`docs/` 与运行入口。导出目录已 `git init`；没有 remote、没有 commit、没有 push。

冒烟运行生成的本地 `__pycache__` 缓存留在工作目录中；`.gitignore` 已验证忽略这些路径，因此下方文件清单与大小按 Git 可导出文件统计。自动审核拒绝了删除这些缓存文件的操作。

文件数（不含 `.git` 与忽略缓存）：`0108`
总大小（不含 `.git` 与忽略缓存）：`000005706515` 字节

## 目录树

```text
light-decider/
  artifacts/
  data/
  data/light_decider_independent_blind_holdout_v1_2026-11-03/
  data/light_decider_independent_blind_holdout_v2_2026-11-04/
  data/light_decider_independent_blind_holdout_v3_2026-11-04/
  data/light_decider_independent_blind_holdout_v4_2026-11-05/
  data/light_decider_independent_blind_holdout_v5_2026-11-06/
  data/light_decider_independent_blind_holdout_v6_2026-11-06/
  data/training_round4_v1_2026-11-05/
  docs/
  docs/reports/
  light_decider/
  light_decider/question/
  .gitignore
  CASE_STUDY.md
  HASH_MANIFEST.md
  README.md
  answer_worker.py
  artifacts/decisioner_round4_v1_2026-11-05.joblib
  data/README.md
  data/light_decider_independent_blind_holdout_v1_2026-11-03/freeze_audit_2026-11-03.md
  data/light_decider_independent_blind_holdout_v1_2026-11-03/freeze_manifest_2026-11-03.json
  data/light_decider_independent_blind_holdout_v1_2026-11-03/light_decider_blind_label_sheet_v1_frozen_2026-11-03.xlsx
  data/light_decider_independent_blind_holdout_v1_2026-11-03/light_decider_independent_blind_holdout_v1_human_labels_frozen_2026-11-03.jsonl
  data/light_decider_independent_blind_holdout_v2_2026-11-04/blind_holdout_v2_unlabeled.xlsx
  data/light_decider_independent_blind_holdout_v2_2026-11-04/blind_holdout_v2_user_labels_frozen_2026-11-04.xlsx
  data/light_decider_independent_blind_holdout_v2_2026-11-04/creation_audit.md
  data/light_decider_independent_blind_holdout_v2_2026-11-04/evaluation_report_v2.md
  data/light_decider_independent_blind_holdout_v2_2026-11-04/freeze_manifest_v2.json
  data/light_decider_independent_blind_holdout_v2_2026-11-04/freeze_manifest_v2_user_labels_2026-11-04.json
  data/light_decider_independent_blind_holdout_v3_2026-11-04/blind_holdout_v3_codex_reference_SEALED.jsonl
  data/light_decider_independent_blind_holdout_v3_2026-11-04/blind_holdout_v3_labels_frozen.jsonl
  data/light_decider_independent_blind_holdout_v3_2026-11-04/evaluation_report_v3.md
  data/light_decider_independent_blind_holdout_v3_2026-11-04/freeze_manifest_v3.md
  data/light_decider_independent_blind_holdout_v3_2026-11-04/freeze_manifest_v3_template.md
  data/light_decider_independent_blind_holdout_v3_2026-11-04/generation_report_v3.md
  data/light_decider_independent_blind_holdout_v4_2026-11-05/blind_holdout_v4_labels_frozen.jsonl
  data/light_decider_independent_blind_holdout_v4_2026-11-05/blind_holdout_v4_unlabeled.xlsx
  data/light_decider_independent_blind_holdout_v4_2026-11-05/evaluation_predictions_once.jsonl
  data/light_decider_independent_blind_holdout_v4_2026-11-05/evaluation_report_v4.md
  data/light_decider_independent_blind_holdout_v4_2026-11-05/freeze_manifest_v4.md
  data/light_decider_independent_blind_holdout_v4_2026-11-05/generation_report_v4.md
  data/light_decider_independent_blind_holdout_v5_2026-11-06/blind_holdout_v5_labels_frozen.jsonl
  data/light_decider_independent_blind_holdout_v5_2026-11-06/evaluation_report_v5.md
  data/light_decider_independent_blind_holdout_v5_2026-11-06/freeze_manifest_v5.md
  data/light_decider_independent_blind_holdout_v6_2026-11-06/blind_holdout_v6_labels_frozen.jsonl
  data/light_decider_independent_blind_holdout_v6_2026-11-06/evaluation_report_v6.md
  data/light_decider_independent_blind_holdout_v6_2026-11-06/freeze_manifest_v6.md
  data/training_round4_v1_2026-11-05/dataset_manifest.json
  data/training_round4_v1_2026-11-05/dev.jsonl
  data/training_round4_v1_2026-11-05/train.jsonl
  docs/DATA_SOURCES.md
  docs/light_decider_two_axis_annotation_guideline_v3.md
  docs/reports/ablation_report_v3_1.md
  docs/reports/activation_note_v3_2b.md
  docs/reports/activation_note_v3_3.md
  docs/reports/answer_worker_7b_report.md
  docs/reports/clean_replay_round2_v3_2b.md
  docs/reports/install_and_answer_worker_report.md
  docs/reports/phase2_codex_live_report.md
  docs/reports/policy_v3_3_replay_report.md
  docs/reports/policy_v3_4_replay_report.md
  docs/reports/promotion_note_round4.md
  docs/reports/regression_v3_2_devset.md
  docs/reports/regression_v3_2b_devset.md
  docs/reports/round2_training_report.md
  docs/reports/round3_training_report.md
  docs/reports/round4_training_report.md
  docs/reports/routing_policy_regression.md
  docs/reports/routing_policy_regression_v3_1.md
  docs/reports/routing_policy_v3_2_diff.md
  docs/reports/routing_policy_v3_audit.md
  docs/reports/training_report_round1.md
  docs/reports/v1_codex_blind_reference_audit.md
  docs/reports/v1_holdout_audit.md
  docs/reports/v1_human_labels_audit.md
  docs/reports/v1_model_predictions_audit.md
  docs/reports/v1_reference_comparison_audit.md
  docs/reports/v2_creation_audit.md
  docs/reports/v2_evaluation_report_v2.md
  docs/reports/v3_evaluation_report_v3.md
  docs/reports/v3_freeze_manifest_v3.md
  docs/reports/v3_freeze_manifest_v3_template.md
  docs/reports/v3_generation_report_v3.md
  docs/reports/v4_evaluation_report_v4.md
  docs/reports/v4_freeze_manifest_v4.md
  docs/reports/v4_generation_report_v4.md
  docs/reports/v5_evaluation_report_v5.md
  docs/reports/v5_freeze_manifest_v5.md
  docs/reports/v6_evaluation_report_v6.md
  docs/reports/v6_freeze_manifest_v6.md
  docs/super_agent_phase1_design.md
  executor.py
  export_fix_report.md
  light_decider/__init__.py
  light_decider/answer_worker.py
  light_decider/clause_segmentation.py
  light_decider/executor.py
  light_decider/handoff.py
  light_decider/input_normalization.py
  light_decider/model.py
  light_decider/model_tier.py
  light_decider/predict.py
  light_decider/predict_model_tier.py
  light_decider/predict_semantic.py
  light_decider/question/__init__.py
  light_decider/question/templates.py
  light_decider/routing_policy.py
  light_decider/routing_policy_v3_1.py
  light_decider/routing_policy_v3_2_candidate.py
  light_decider/routing_policy_v3_2b_candidate.py
  light_decider/routing_policy_v3_3_candidate.py
  light_decider/routing_policy_v3_4_candidate.py
  light_decider/semantic_runtime.py
  light_decider/shadow.py
  light_decider/train.py
  light_decider/train_model_tier.py
  requirements.txt
  templates.py
  try_router.py
  try_router_semantic.py
```
