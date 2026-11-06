# light_decider 第四轮训练报告（2026-11-05）

## 结果概览

- round-4 模型：`artifacts/decisioner_round4_v1_2026-11-05.joblib`；SHA-256：`6eff1a818db972bf887ed885f1cad4162dc5cef69ebdee0fb4f7ac32c37b286b`。
- 训练集：516 条 round-2 原样训练数据 + 60 条已确认 decide 边界数据 = 576 条；五类 rare_class 188 条未并入。
- 域内 dev 硬门槛 clarify→decide=0：实际 0，通过。
- round-4 模型只作为候选；默认模型仍为 round-2，现役策略保持 v3.1，自动派发关闭。

## 数据版本与校验

- Round-2 train 原样 516 条，SHA-256 `c05e18aaa2f393093a7879ffa43b3b0063e20e4edb553b8a12422b271242c3ab`；round-2 dev 原样复制 127 条，SHA-256 `cf03fa1583713dff2a600b5df941dc0b6c358fc4bc375ef066f45fc5f77eec82`（与指定 cf03fa15… 一致）。
- Decide 边界工作簿 60 条，SHA-256 `def43b94f69233164314b9acf8d74ffb1c3a4dad86b5c4d7cbee27c305561d7a`；用户确认前 workbook source/reviewed 为 synthetic_new/false，合并视图按 用户 于 2026-11-05 确认记为 `human_confirmed_2026-11-05` / reviewed=true。原 xlsx 未改。
- 新 train 576 条；三分类分布：clarify 180、codex 170、decide 226。保留的五类标签字段分布：clarify 180、codex 160、codex+check_first 2、codex+declare_default 8、decide 226。新增 60 条五类原标签均保存在 `label_5class`，训练视图通过 `label` 训练三分类。
- 新增 60 条场景家族与 dev 交集：0；round-2 原 train/dev 交集：0；ID 冲突：0。新增样本 reviewed=true，source=`human_confirmed_2026-11-05`。
- round-3 的 rare_class 188 条未读取、未并入；仅在本报告中记录为明确排除项。

### 关键文件 SHA-256

| 输入 | SHA-256 |
|---|---|
| `artifacts/decisioner_round2_v1_2026-11-04.joblib` | `f2e1dc659d1d9a78c3136401ba2d987e80bd836a85005530bf75e53510d2dc25` |
| `data/frozen_2026-11-03/light_decider_independent_blind_holdout_v1_human_labels_frozen_2026-11-03.jsonl` | `f5b572f313921a14ff7820ea8188af7a7366226ba6a5a7ad83153fae666c0b12` |
| `data/light_decider_independent_blind_holdout_v1.csv` | `9d065f614126c82b0edd8e149c30b4b641e2748f12ab6c9d86db073036eef41b` |
| `data/light_decider_independent_blind_holdout_v2_2026-11-04/blind_holdout_v2_user_labels_frozen_2026-11-04.xlsx` | `5f0cc3bacb9d84c34cf5ef7317034552d6c04915321603e9156af523f7f20b4f` |
| `data/light_decider_independent_blind_holdout_v3_2026-11-04/blind_holdout_v3_labels_frozen.jsonl` | `1b28daf61866153cda78fb6f7060ed084659f73b7ef1efd128e5f53dd0d1e07b` |
| `data/light_decider_independent_blind_holdout_v4_2026-11-05/blind_holdout_v4_labels_frozen.jsonl` | `02ca2168736c978bb077f7490c46002a74ed735b96199f93c6709ffc0f1366e1` |
| `data/training_round2_v1_2026-11-04/dev.jsonl` | `cf03fa1583713dff2a600b5df941dc0b6c358fc4bc375ef066f45fc5f77eec82` |
| `data/training_round2_v1_2026-11-04/train.jsonl` | `c05e18aaa2f393093a7879ffa43b3b0063e20e4edb553b8a12422b271242c3ab` |
| `light_decider/routing_policy.py` | `719f88ed53635d8b69f35e52e00741b9d9b81128d7f72d99f176ddfe9902e86e` |
| `outputs/01a195cc-5dff-7e70-9e28-5298d354d8cf/decide_boundary_candidates.xlsx` | `def43b94f69233164314b9acf8d74ffb1c3a4dad86b5c4d7cbee27c305561d7a` |
| `work/rare_class_candidates_build_2026-11-04/round3_source_rows/v2_frozen_raw.json` | `8ec0426cee588fc824a892c71f460109ebccb1555396c6aaf1856d39308ac013` |
| `data/training_round4_v1_2026-11-05/train.jsonl` | `ba7e6c362f9501aeacfcd471e5ce6b4a8cf0bd8077260fe459dccaa45fa2753f` |
| `data/training_round4_v1_2026-11-05/dev.jsonl` | `cf03fa1583713dff2a600b5df941dc0b6c358fc4bc375ef066f45fc5f77eec82` |
| `artifacts/decisioner_round4_v1_2026-11-05.joblib` | `6eff1a818db972bf887ed885f1cad4162dc5cef69ebdee0fb4f7ac32c37b286b` |

## 训练配置

- 字符级 TF-IDF，1–4 gram，最多 80,000 个特征，sublinear TF；逻辑回归 max_iter=1000、random_state=42。
- 类别权重固定为 decide=1.0、clarify=1.5、codex=1.0；没有搜索权重或阈值。
- 训练样本权重固定：仅 source=legacy_cleaned 且 source_dataset 名称含 sharc 的训练行取 0.3，其余取 1.0。60 条新数据标为 human_confirmed，不受 ShARC 降权。
- 实际模型训练耗时 0.41 秒。概率未校准。

## Dev 评测

域内 dev 为唯一硬门槛切片；ShARC 切片只作来源参考；同时保留完整 dev 对照。

### 域内 dev（硬门槛）

样本 18；准确率 17/18 (94.4%)；macro-F1 0.627；加权代价 **1**；clarify→decide **0**。

混淆矩阵：

| 真实值 \ 预测值 | `decide` | `clarify` | `codex` |
|---|---:|---:|---:|
| `decide` | 0 | 0 | 0 |
| `clarify` | 0 | 11 | 0 |
| `codex` | 0 | 1 | 6 |

每类指标：

| 类别 | Precision | Recall | F1 | 支持数 |
|---|---:|---:|---:|---:|
| `decide` | 0.000 | 0.000 | 0.000 | 0 |
| `clarify` | 0.917 | 1.000 | 0.957 | 11 |
| `codex` | 1.000 | 0.857 | 0.923 | 7 |

### ShARC dev（参考，不参与门槛）

样本 30；准确率 16/30 (53.3%)；macro-F1 0.332；加权代价 **41**；clarify→decide **3**。

混淆矩阵：

| 真实值 \ 预测值 | `decide` | `clarify` | `codex` |
|---|---:|---:|---:|
| `decide` | 4 | 11 | 0 |
| `clarify` | 3 | 12 | 0 |
| `codex` | 0 | 0 | 0 |

每类指标：

| 类别 | Precision | Recall | F1 | 支持数 |
|---|---:|---:|---:|---:|
| `decide` | 0.571 | 0.267 | 0.364 | 15 |
| `clarify` | 0.522 | 0.800 | 0.632 | 15 |
| `codex` | 0.000 | 0.000 | 0.000 | 0 |

### 完整 dev（总体对照）

样本 127；准确率 109/127 (85.8%)；macro-F1 0.853；加权代价 **45**；clarify→decide **3**。

混淆矩阵：

| 真实值 \ 预测值 | `decide` | `clarify` | `codex` |
|---|---:|---:|---:|
| `decide` | 25 | 11 | 0 |
| `clarify` | 3 | 45 | 0 |
| `codex` | 2 | 2 | 39 |

每类指标：

| 类别 | Precision | Recall | F1 | 支持数 |
|---|---:|---:|---:|---:|
| `decide` | 0.833 | 0.694 | 0.758 | 36 |
| `clarify` | 0.776 | 0.938 | 0.849 | 48 |
| `codex` | 1.000 | 0.907 | 0.951 | 43 |

### 域内 dev 错误清单

| ID | 金标 | R4预测 | 代价 | 场景家族 |
|---|---|---|---:|---|
| v2-dedupe-atomic-insert-safe-default | codex | clarify | 1 | shared::device_event_deduplication |

### ShARC dev 错误清单

| ID | 金标 | R4预测 | 代价 |
|---|---|---|---:|
| candidate-sharc-07c7d9afb01e2d0d09f356e02468f4b7bcaf600c | decide | clarify | 1 |
| candidate-sharc-14f14ca7b82b0075dbad5f5c0530652fd7e345bc | clarify | decide | 10 |
| candidate-sharc-1a22e4c931d8fe0ca8778915792ca460b90d1706 | decide | clarify | 1 |
| candidate-sharc-5428ea8f13aa09f8abce5744717627870983f677 | decide | clarify | 1 |
| candidate-sharc-6d3e7adeaa2a369ebd471a46a5b1152049b77202 | decide | clarify | 1 |
| candidate-sharc-82f13958908ce92ea41f4d90f3978b3172ef7feb | decide | clarify | 1 |
| candidate-sharc-8b83c3af43346bac342b4a6376050de2125c98c4 | decide | clarify | 1 |
| candidate-sharc-8c30bb3c9025face6cbdbc5a7bf5f3ed2ec9b1da | decide | clarify | 1 |
| candidate-sharc-977073a6f853e94cd26ccd9e0bd0d89b3a0e7a73 | clarify | decide | 10 |
| candidate-sharc-c520406962a948d73c4a9d1f62de9008c8f3330c | decide | clarify | 1 |
| candidate-sharc-c7666be42ddab290163aea11f9e6617c0a10c763 | decide | clarify | 1 |
| candidate-sharc-ca1a4d0beefeadbb8a718fa1e7d1e1f44bd23418 | decide | clarify | 1 |
| candidate-sharc-ea400cb3aa461a3e881687c5b5cefc98dd7c76bc | decide | clarify | 1 |
| candidate-sharc-f676c41dcc3cfb6f08d2a1c33581ae51e816b738 | clarify | decide | 10 |

### 完整 dev 错误清单

| ID | 金标 | R4预测 | 代价 | 来源 | 场景家族 |
|---|---|---|---:|---|---|
| candidate-ai-mitra-456 | codex | decide | 1 | legacy_cleaned | legacy::ai-mitra/llm-router-dataset::ai-mitra-row-456 |
| candidate-ai-mitra-459 | codex | clarify | 1 | legacy_cleaned | legacy::ai-mitra/llm-router-dataset::ai-mitra-row-459 |
| candidate-ai-mitra-469 | codex | decide | 1 | legacy_cleaned | legacy::ai-mitra/llm-router-dataset::ai-mitra-row-469 |
| candidate-sharc-07c7d9afb01e2d0d09f356e02468f4b7bcaf600c | decide | clarify | 1 | legacy_cleaned | legacy::UCLNLP/sharc::sharc-tree-f61bf40d7c3915ccbe8f375606ae84016c4af408 |
| candidate-sharc-14f14ca7b82b0075dbad5f5c0530652fd7e345bc | clarify | decide | 10 | legacy_cleaned | legacy::UCLNLP/sharc::sharc-tree-94f5722a28e203ce2604fc2a8dfb3d407913ddf0 |
| candidate-sharc-1a22e4c931d8fe0ca8778915792ca460b90d1706 | decide | clarify | 1 | legacy_cleaned | legacy::UCLNLP/sharc::sharc-tree-90d62b51353a6ccef87c4cc9644f9e75d749722f |
| candidate-sharc-5428ea8f13aa09f8abce5744717627870983f677 | decide | clarify | 1 | legacy_cleaned | legacy::UCLNLP/sharc::sharc-tree-061a6ee9c30f33816bd5660b9f6dd84b1485f611 |
| candidate-sharc-6d3e7adeaa2a369ebd471a46a5b1152049b77202 | decide | clarify | 1 | legacy_cleaned | legacy::UCLNLP/sharc::sharc-tree-f82d35d8dbefa83d27fc344720492a257909d2df |
| candidate-sharc-82f13958908ce92ea41f4d90f3978b3172ef7feb | decide | clarify | 1 | legacy_cleaned | legacy::UCLNLP/sharc::sharc-tree-736bdd99dbc133df080b7e74cb14342b0c9860c8 |
| candidate-sharc-8b83c3af43346bac342b4a6376050de2125c98c4 | decide | clarify | 1 | legacy_cleaned | legacy::UCLNLP/sharc::sharc-tree-c44d93269e1bb1e752dea01cda54682efe3ce0cf |
| candidate-sharc-8c30bb3c9025face6cbdbc5a7bf5f3ed2ec9b1da | decide | clarify | 1 | legacy_cleaned | legacy::UCLNLP/sharc::sharc-tree-2c93452e825a3aed069ac1f6e307640c46481cb0 |
| candidate-sharc-977073a6f853e94cd26ccd9e0bd0d89b3a0e7a73 | clarify | decide | 10 | legacy_cleaned | legacy::UCLNLP/sharc::sharc-tree-31bb96aaa90435933358cce2d617a4614887baa9 |
| candidate-sharc-c520406962a948d73c4a9d1f62de9008c8f3330c | decide | clarify | 1 | legacy_cleaned | legacy::UCLNLP/sharc::sharc-tree-2b4716df0ee1a593461ba8503b567611cecbc298 |
| candidate-sharc-c7666be42ddab290163aea11f9e6617c0a10c763 | decide | clarify | 1 | legacy_cleaned | legacy::UCLNLP/sharc::sharc-tree-a86f52fcab68ce8019852eb29ef868bc2912cee6 |
| candidate-sharc-ca1a4d0beefeadbb8a718fa1e7d1e1f44bd23418 | decide | clarify | 1 | legacy_cleaned | legacy::UCLNLP/sharc::sharc-tree-dbd1a50d7186a61c651031dd072ec79bdb263047 |
| candidate-sharc-ea400cb3aa461a3e881687c5b5cefc98dd7c76bc | decide | clarify | 1 | legacy_cleaned | legacy::UCLNLP/sharc::sharc-tree-2ff23ddcf4d6fc0fb53c7abc25b407724be9012c |
| candidate-sharc-f676c41dcc3cfb6f08d2a1c33581ae51e816b738 | clarify | decide | 10 | legacy_cleaned | legacy::UCLNLP/sharc::sharc-tree-30873d5fd2b2fa0980face79df787ecf6f089834 |
| v2-dedupe-atomic-insert-safe-default | codex | clarify | 1 | synthetic | shared::device_event_deduplication |

## 96 条已见题参考回放（非金标）

v1–v4 四套题均为已见集合；下表仅作训练轮次参考，不构成泛化或盲测证据。两模型分别使用 round-2 与 round-4 argmax，并通过同一现役 routing_policy v3.1。权重：clarify→decide=10、clarify→codex*=5、其余误判=1。

| 集合 | 样本数 | Decide 召回 R2 | Decide 召回 R4 | 加权代价 R2 | 加权代价 R4 | Clarify 召回 R2 | Clarify 召回 R4 | declare 精确召回 R2 | declare 精确召回 R4 | check_first 精确召回 R2 | check_first 精确召回 R4 | c→d R2/R4 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| v1 | 24 | 6/8 (0.750) | 7/8 (0.875) | 3 | 2 | 1.000 | 1.000 | 2/3 | 2/3 | 2/2 | 2/2 | 0/0 |
| v2 | 24 | 1/4 (0.250) | 4/4 (1.000) | 8 | 1 | 0.857 | 1.000 | 3/3 | 3/3 | 2/2 | 2/2 | 0/0 |
| v3 | 24 | 3/6 (0.500) | 6/6 (1.000) | 14 | 21 | 0.857 | 0.714 | 0/3 | 0/3 | 2/2 | 2/2 | 0/1 |
| v4 | 24 | 3/6 (0.500) | 6/6 (1.000) | 13 | 10 | 0.857 | 0.857 | 0/3 | 0/3 | 2/2 | 2/2 | 0/0 |
| 合计 | 96 | 13/24 (0.542) | 23/24 (0.958) | 38 | 34 | 0.893 | 0.893 | 5/12 | 5/12 | 8/8 | 8/8 | 0/1 |

### 96 条参考集错误清单

| 集合 | ID | 金标 | R2+v3.1 | R4+v3.1 | R2代价 | R4代价 |
|---|---|---|---|---|---:|---:|
| v1 | blind-009 | decide | codex | decide | 1 | 0 |
| v1 | blind-015 | codex+declare_default | clarify | clarify | 1 | 1 |
| v1 | blind-024 | decide | codex | codex | 1 | 1 |
| v2 | blind-v2-001 | decide | codex | decide | 1 | 0 |
| v2 | blind-v2-003 | decide | codex | decide | 1 | 0 |
| v2 | blind-v2-004 | decide | codex | decide | 1 | 0 |
| v2 | blind-v2-010 | codex | codex | decide | 0 | 1 |
| v2 | blind-v2-017 | clarify | codex | clarify | 5 | 0 |
| v3 | blind-v3-003 | codex | clarify | clarify | 1 | 1 |
| v3 | blind-v3-004 | codex+declare_default | codex | codex | 1 | 1 |
| v3 | blind-v3-007 | decide | clarify | decide | 1 | 0 |
| v3 | blind-v3-010 | codex+declare_default | codex | codex | 1 | 1 |
| v3 | blind-v3-012 | clarify | codex | codex | 5 | 5 |
| v3 | blind-v3-013 | decide | codex | decide | 1 | 0 |
| v3 | blind-v3-014 | codex | codex+check_first | codex+check_first | 1 | 1 |
| v3 | blind-v3-017 | codex+declare_default | codex | codex | 1 | 1 |
| v3 | blind-v3-019 | codex | codex+check_first | codex+check_first | 1 | 1 |
| v3 | blind-v3-021 | clarify | clarify | decide | 0 | 10 |
| v3 | blind-v3-023 | decide | codex | decide | 1 | 0 |
| v4 | blind-v4-001 | decide | clarify | decide | 1 | 0 |
| v4 | blind-v4-002 | decide | clarify | decide | 1 | 0 |
| v4 | blind-v4-003 | clarify | codex | codex | 5 | 5 |
| v4 | blind-v4-008 | codex | codex+check_first | codex+check_first | 1 | 1 |
| v4 | blind-v4-010 | codex+declare_default | decide | decide | 1 | 1 |
| v4 | blind-v4-012 | decide | clarify | decide | 1 | 0 |
| v4 | blind-v4-021 | codex | codex+check_first | codex+check_first | 1 | 1 |
| v4 | blind-v4-022 | codex+declare_default | codex | codex | 1 | 1 |
| v4 | blind-v4-024 | codex+declare_default | clarify | clarify | 1 | 1 |

## 审计与限制

- 模型仅以 576 条 train 拟合一次；未在 dev 或已见题上调参。Dev 仅用于报告预设域内门槛；ShARC dev 仅参考。
- v1–v4 题目只在拟合完成后读取并用于参考回放，未用于训练或选型；冻结文件全程只读。
- 运行前后策略 SHA-256 均为 `719f88ed53635d8b69f35e52e00741b9d9b81128d7f72d99f176ddfe9902e86e`；round-2 模型仍为默认模型，round-4 未替换；自动派发保持关闭。
- round-4 的训练数据仅为 round-2 train 516 + 60 条决定边界候选；round-3 rare_class 188 条明确排除。是否采用 round-4 等 v5 盲测判决。
