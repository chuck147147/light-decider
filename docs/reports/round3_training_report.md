# light_decider 第三轮训练报告（2026-11-05）

## 结果概览

- 新模型文件：`artifacts/decisioner_round3_v1_2026-11-05.joblib`；SHA-256：`86c9d22575eb0b58774a23e45cc1d01a982c8541c7f53f9586395595fc6b8073`。
- 合并数据版本 SHA-256：`f0be7f3908c1be42d012cdd3b47528a8422fe984656c05d381012b5432b66477`；train 704 条，dev 127 条。
- 域内 dev 硬门槛 clarify→decide=0：实际 0，**通过**。
- 72 条 v1/v2/v3 只作为已见数据参考，不是金标，不参与参数选型；选型完成后才对 round-2 与 round-3 做相同口径回放。
- 现役策略仍为 routing_policy v3.1；v3.2b 未读取、未激活；自动派发保持关闭。

## 数据与合并审计

- Round-2 train 原样 516 条；新增候选 188 条全部并入 train；最终 train 704 条。round-2 dev 原样复制 127 条，SHA-256 与 round-2 完全相同。
- 场景家族交集：新增 188 条与 dev 为 0；train/dev 总交集为 0。
- 候选 ID 与旧 train/dev 冲突 0 条；新增 ID 重复 0 条。
- 合并数据中新增样本 reviewed=true，source=`human_confirmed_2026-11-05`，source_before_confirmation=`synthetic_new`；原始 xlsx 保持原样。`rare-dd-noauth-10` 保持 `clarify`。
- 新增五类原标签：`codex+declare_default` 73, `clarify` 65, `codex+check_first` 30, `codex` 20。折成三类后：`codex` 123, `clarify` 65。
- 合并后 train 三类分布：`decide` 181, `clarify` 235, `codex` 288。五类原标签仍保留在独立字段 `label_5class`。

### 输入文件校验

| 输入 | SHA-256 |
|---|---|
| `data\light_decider_independent_blind_holdout_v1.csv` | `9d065f614126c82b0edd8e149c30b4b641e2748f12ab6c9d86db073036eef41b` |
| `data\training_round2_v1_2026-11-04\train.jsonl` | `c05e18aaa2f393093a7879ffa43b3b0063e20e4edb553b8a12422b271242c3ab` |
| `data\training_round2_v1_2026-11-04\dev.jsonl` | `cf03fa1583713dff2a600b5df941dc0b6c358fc4bc375ef066f45fc5f77eec82` |
| `outputs\rare_class_candidates_2026-11-04\rare_class_candidates.xlsx` | `15632f984c282c58af028ac501b771927986ba35f2df7024a6621c27045f9028` |
| `outputs\rare_class_candidates_2026-11-04\rare_class_candidates_supplement.xlsx` | `045c76568dabaa76d9e79af1c0799e210611a1d5c56d29cfa4e1b1e87c8308f8` |
| `data\frozen_2026-11-03\light_decider_independent_blind_holdout_v1_human_labels_frozen_2026-11-03.jsonl` | `f5b572f313921a14ff7820ea8188af7a7366226ba6a5a7ad83153fae666c0b12` |
| `data\light_decider_independent_blind_holdout_v2_2026-11-04\blind_holdout_v2_user_labels_frozen_2026-11-04.xlsx` | `5f0cc3bacb9d84c34cf5ef7317034552d6c04915321603e9156af523f7f20b4f` |
| `data\light_decider_independent_blind_holdout_v3_2026-11-04\blind_holdout_v3_labels_frozen.jsonl` | `1b28daf61866153cda78fb6f7060ed084659f73b7ef1efd128e5f53dd0d1e07b` |
| `artifacts\decisioner_round2_v1_2026-11-04.joblib` | `f2e1dc659d1d9a78c3136401ba2d987e80bd836a85005530bf75e53510d2dc25` |
| `light_decider\routing_policy.py` | `719f88ed53635d8b69f35e52e00741b9d9b81128d7f72d99f176ddfe9902e86e` |

## 模型配置与选型

- 字符级 TF-IDF 1–4 gram、最多 80,000 特征、逻辑回归；使用 light_decider 的 round-2 同一流水线构造器。
- 轮次起点为 round-2 胜出配置：ShARC 样本权重 0.30、clarify 类权重 1.50。仅在其附近比较 ShARC 权重 0.25/0.30/0.35 与 clarify 类权重 1.40/1.50/1.60。
- 选型规则只看域内 dev：先要求 clarify→decide=0，再按域内加权代价、clarify recall、codex recall、macro-F1 排序；72 条已见集完全不参与选型。ShARC dev 只作参考。
- ShARC 样本降权仅用于 source=legacy_cleaned 且 source_dataset 名称含 sharc 的训练行；新确认样本不按 ShARC 降权。

| ShARC权重 | clarify权重 | 域内 c→d | 域内加权代价 | clarify召回 | codex召回 | macro-F1 | 被选中 |
|---:|---:|---:|---:|---:|---:|---:|---|
| 0.25 | 1.40 | 0 | 10 | 0.818 | 1.000 | 0.592 |  |
| 0.25 | 1.50 | 0 | 10 | 0.818 | 1.000 | 0.592 |  |
| 0.25 | 1.60 | 0 | 5 | 0.909 | 1.000 | 0.629 |  |
| 0.30 | 1.40 | 0 | 10 | 0.818 | 1.000 | 0.592 |  |
| 0.30 | 1.50 | 0 | 5 | 0.909 | 1.000 | 0.629 | 是 |
| 0.30 | 1.60 | 0 | 5 | 0.909 | 1.000 | 0.629 |  |
| 0.35 | 1.40 | 0 | 10 | 0.818 | 1.000 | 0.592 |  |
| 0.35 | 1.50 | 0 | 5 | 0.909 | 1.000 | 0.629 |  |
| 0.35 | 1.60 | 0 | 5 | 0.909 | 1.000 | 0.629 |  |

选中配置：ShARC 权重 0.30，clarify 权重 1.50。

## Dev 评测

### 域内 dev（唯一硬门槛切片）

样本 18；硬门槛 clarify→decide=0：实际 0，**通过**；加权代价 5。

| 真实值 \ 预测值 | `decide` | `clarify` | `codex` |
|---|---:|---:|---:|
| `decide` | 0 | 0 | 0 |
| `clarify` | 0 | 10 | 1 |
| `codex` | 0 | 0 | 7 |

| 类别 | Precision | Recall | F1 | 支持数 |
|---|---:|---:|---:|---:|
| `decide` | 0.000 | 0.000 | 0.000 | 0 |
| `clarify` | 1.000 | 0.909 | 0.952 | 11 |
| `codex` | 0.875 | 1.000 | 0.933 | 7 |

域内错误清单：

| ID | 真实 | 预测 | 代价 | 来源 | 场景家族 |
|---|---|---|---|---|---|
| v2-dedupe-meter-reading-clarify | clarify | codex | 5 | synthetic | shared::device_event_deduplication |

### ShARC dev（参考片，不参与门槛）

### ShARC 参考结果

样本 30；准确率 18/30 (60.0%)；macro-F1 0.367；加权代价 **21**；clarify→decide **1**。

混淆矩阵：

| 真实值 \ 预测值 | `decide` | `clarify` | `codex` |
|---|---:|---:|---:|
| `decide` | 4 | 11 | 0 |
| `clarify` | 1 | 14 | 0 |
| `codex` | 0 | 0 | 0 |

每类指标：

| 类别 | Precision | Recall | F1 | 支持数 |
|---|---:|---:|---:|---:|
| `decide` | 0.800 | 0.267 | 0.400 | 15 |
| `clarify` | 0.560 | 0.933 | 0.700 | 15 |
| `codex` | 0.000 | 0.000 | 0.000 | 0 |

错误清单：

| ID | 真实 | 预测 | 代价 |
|---|---|---|---|
| candidate-sharc-07c7d9afb01e2d0d09f356e02468f4b7bcaf600c | decide | clarify | 1 |
| candidate-sharc-5428ea8f13aa09f8abce5744717627870983f677 | decide | clarify | 1 |
| candidate-sharc-6d3e7adeaa2a369ebd471a46a5b1152049b77202 | decide | clarify | 1 |
| candidate-sharc-82f13958908ce92ea41f4d90f3978b3172ef7feb | decide | clarify | 1 |
| candidate-sharc-8b83c3af43346bac342b4a6376050de2125c98c4 | decide | clarify | 1 |
| candidate-sharc-8c30bb3c9025face6cbdbc5a7bf5f3ed2ec9b1da | decide | clarify | 1 |
| candidate-sharc-8fc68ec051eea67cc3f50fdd4f45bd9aca442871 | decide | clarify | 1 |
| candidate-sharc-977073a6f853e94cd26ccd9e0bd0d89b3a0e7a73 | clarify | decide | 10 |
| candidate-sharc-c520406962a948d73c4a9d1f62de9008c8f3330c | decide | clarify | 1 |
| candidate-sharc-c7666be42ddab290163aea11f9e6617c0a10c763 | decide | clarify | 1 |
| candidate-sharc-ca1a4d0beefeadbb8a718fa1e7d1e1f44bd23418 | decide | clarify | 1 |
| candidate-sharc-ea400cb3aa461a3e881687c5b5cefc98dd7c76bc | decide | clarify | 1 |

### 完整 dev（总体参考）

### 完整 dev

样本 127；准确率 112/127 (88.2%)；macro-F1 0.873；加权代价 **28**；clarify→decide **1**。

混淆矩阵：

| 真实值 \ 预测值 | `decide` | `clarify` | `codex` |
|---|---:|---:|---:|
| `decide` | 24 | 12 | 0 |
| `clarify` | 1 | 46 | 1 |
| `codex` | 1 | 0 | 42 |

每类指标：

| 类别 | Precision | Recall | F1 | 支持数 |
|---|---:|---:|---:|---:|
| `decide` | 0.923 | 0.667 | 0.774 | 36 |
| `clarify` | 0.793 | 0.958 | 0.868 | 48 |
| `codex` | 0.977 | 0.977 | 0.977 | 43 |


## 72 条已见数据参考评测（非金标）

全部 72 条（v1/v2/v3 各 24 条）使用相同冻结标签。结果仅为已见数据参考，不构成泛化证据，也未参与训练或选型。v1 的 blind-015 按本次 72 条统一回放口径计入。代价权重为 clarify→decide=10、clarify→codex*=5、其余误判=1。

| 口径 | 加权代价 | 5类精确准确率 | clarify召回 | clarify→decide | declare_default 精确召回 | check_first 精确召回 |
|---|---:|---:|---:|---:|---:|---:|
| round2_argmax | 42 | 0.583 | 0.857 | 0 | 0.000 (0/9) | 0.000 (0/6) |
| round2_policy | 25 | 0.764 | 0.905 | 0 | 0.556 (5/9) | 1.000 (6/6) |
| round3_argmax | 47 | 0.514 | 0.857 | 0 | 0.000 (0/9) | 0.000 (0/6) |
| round3_policy | 22 | 0.750 | 0.952 | 0 | 0.556 (5/9) | 1.000 (6/6) |

Round-2 配置来自 `data/training_round2_v1_2026-11-04/round2_training_report.json`；round-2 模型 SHA-256 `f2e1dc659d1d9a78c3136401ba2d987e80bd836a85005530bf75e53510d2dc25`。两轮的 v3.1 policy 口径均调用现役策略文件，SHA-256 `719f88ed53635d8b69f35e52e00741b9d9b81128d7f72d99f176ddfe9902e86e`。

### Round-3 错误清单

下表列出任一口径出错的题目，按五类冻结标签逐条对照。

| 集合 | ID | 真实五类 | R3 argmax | R3 v3.1 | argmax代价 | 策略代价 |
|---|---|---|---|---|---|---|
| v1 | blind-001 | decide | codex | decide | 1 | 0 |
| v1 | blind-004 | decide | clarify | clarify | 1 | 1 |
| v1 | blind-005 | codex+declare_default | codex | codex+declare_default | 1 | 0 |
| v1 | blind-007 | decide | clarify | decide | 1 | 0 |
| v1 | blind-009 | decide | codex | codex | 1 | 1 |
| v1 | blind-012 | clarify | codex | clarify | 5 | 0 |
| v1 | blind-013 | decide | codex | decide | 1 | 0 |
| v1 | blind-014 | codex+check_first | codex | codex+check_first | 1 | 0 |
| v1 | blind-015 | codex+declare_default | codex | clarify | 1 | 1 |
| v1 | blind-017 | codex+declare_default | codex | codex+declare_default | 1 | 0 |
| v1 | blind-018 | decide | codex | decide | 1 | 0 |
| v1 | blind-019 | clarify | codex | clarify | 5 | 0 |
| v1 | blind-020 | codex+check_first | codex | codex+check_first | 1 | 0 |
| v1 | blind-021 | decide | codex | decide | 1 | 0 |
| v1 | blind-024 | decide | codex | codex | 1 | 1 |
| v2 | blind-v2-001 | decide | codex | codex | 1 | 1 |
| v2 | blind-v2-002 | decide | codex | decide | 1 | 0 |
| v2 | blind-v2-003 | decide | codex | codex | 1 | 1 |
| v2 | blind-v2-004 | decide | codex | codex | 1 | 1 |
| v2 | blind-v2-020 | codex+declare_default | codex | codex+declare_default | 1 | 0 |
| v2 | blind-v2-021 | codex+declare_default | codex | codex+declare_default | 1 | 0 |
| v2 | blind-v2-022 | codex+declare_default | codex | codex+declare_default | 1 | 0 |
| v2 | blind-v2-023 | codex+check_first | codex | codex+check_first | 1 | 0 |
| v2 | blind-v2-024 | codex+check_first | codex | codex+check_first | 1 | 0 |
| v3 | blind-v3-003 | codex | codex | clarify | 0 | 1 |
| v3 | blind-v3-004 | codex+declare_default | codex | codex | 1 | 1 |
| v3 | blind-v3-005 | codex+check_first | codex | codex+check_first | 1 | 0 |
| v3 | blind-v3-007 | decide | clarify | clarify | 1 | 1 |
| v3 | blind-v3-010 | codex+declare_default | codex | codex | 1 | 1 |
| v3 | blind-v3-012 | clarify | clarify | codex | 0 | 5 |
| v3 | blind-v3-013 | decide | codex | codex | 1 | 1 |
| v3 | blind-v3-014 | codex | codex | codex+check_first | 0 | 1 |
| v3 | blind-v3-016 | codex+check_first | codex | codex+check_first | 1 | 0 |
| v3 | blind-v3-017 | codex+declare_default | codex | codex | 1 | 1 |
| v3 | blind-v3-018 | clarify | codex | clarify | 5 | 0 |
| v3 | blind-v3-019 | codex | codex | codex+check_first | 0 | 1 |
| v3 | blind-v3-020 | decide | clarify | clarify | 1 | 1 |
| v3 | blind-v3-023 | decide | codex | codex | 1 | 1 |
| v3 | blind-v3-024 | decide | clarify | decide | 1 | 0 |

### 按题集拆分的加权代价

| 集合 | 条数 | R2 argmax | R2 + v3.1 | R3 argmax | R3 + v3.1 |
|---|---:|---:|---:|---:|---:|
| v1 | 24 | 15 | 3 | 23 | 4 |
| v2 | 24 | 14 | 8 | 9 | 3 |
| v3 | 24 | 13 | 14 | 15 | 15 |

### 五类精确召回变化

| 类别 | Round-2 argmax | Round-2 + v3.1 | Round-3 argmax | Round-3 + v3.1 |
|---|---:|---:|---:|---:|
| `decide` | 6/18 (0.333) | 10/18 (0.556) | 1/18 (0.056) | 8/18 (0.444) |
| `clarify` | 18/21 (0.857) | 19/21 (0.905) | 18/21 (0.857) | 20/21 (0.952) |
| `codex` | 18/18 (1.000) | 15/18 (0.833) | 18/18 (1.000) | 15/18 (0.833) |
| `codex+declare_default` | 0/9 (0.000) | 5/9 (0.556) | 0/9 (0.000) | 5/9 (0.556) |
| `codex+check_first` | 0/6 (0.000) | 6/6 (1.000) | 0/6 (0.000) | 6/6 (1.000) |

## 限制与审计

- 72 条全是已见数据；不得将这些分数解释为泛化或独立盲测成绩。
- dev 硬门槛只检查 clarify→decide=0；ShARC 指标单独展示，不参与硬门槛。
- 未读取、未训练于冻结题以外的新标签以外的任何内容；冻结题只在训练完成、配置锁定后用于已见集回放。冻结输入文件全程只读。
- Round-3 模型是版本化独立产物，没有替换默认模型；未修改 routing_policy v3.1，未激活 v3.2b，自动派发仍关闭。模型概率未校准。
- round-2 dev 文件哈希保持不变：`cf03fa1583713dff2a600b5df941dc0b6c358fc4bc375ef066f45fc5f77eec82`。策略与指定参考标签文件训练前后哈希一致：是。
