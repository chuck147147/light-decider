# light_decider 第二轮训练报告（2026-11-04）

## 结果概览

- 训练状态：`domain_dev_gate_passed`。自动派发保持关闭。
- 新数据版本 SHA-256：`897d1266b0f2a1d7177d57150360c81c11dea70b900f5ab412bd2ea048f1cb16`；训练 516 条，dev 127 条。
- 复核队列：35 条匹配成功；裁决后改标签 8 条，不变 25 条；N/A 剔除 3 条。改标仅依据所附 CSV，改标记录保留 `label_before_round2`、`label_5class_before_round2` 与 `source_before_round2`。
- 域内 dev：18 条；ShARC 未改标签参考切片：30 条；完整 dev：127 条。ShARC 与域内切片互斥，全部 dev 则包含这两类及其他 legacy 样本。
- 训练样本只取新版本 train；ShARC legacy_cleaned 样本权重 `0.3`，clarify 类权重 `1.5`。
- 选型门槛只检查域内 dev 的 clarify→decide=0：实际 `0`，结果 **通过**。
- 冻结金标评测次数：0。仅域内门槛通过后才核对 SHA-256 并读取金标。

## 裁决处理审计

| 处理 | 数量 |
|---|---:|
| 标签改变并标记 `human_confirmed` | 8 |
| 最终路由与原标签一致，原行保留 | 24 |
| N/A，从 train/dev 排除并单列 | 3 |

改标签 ID：`candidate-sharc-022b59cea42af554ab149ffa158a913f19e7e045`, `candidate-sharc-1b4393a43e6ed685824fe398c5bb462e46505858`, `candidate-sharc-5528f1bf31a19b9ebb2404c39ad5a7cd3719fd77`, `candidate-sharc-568c416344cc8a9cfca139b5fd6ba67327cb3761`, `candidate-sharc-76f0c4faebdf019e5ddad579b0d2c2d87b0669c9`, `candidate-sharc-d9a085b1e539bdd86c7657ce0d0acda3ad6cba0a`, `candidate-sharc-dee59af12b494863fa1d897958624fffe2a779d8`, `candidate-sharc-2858c6d9ec450bfe9a5e3555da2495b890a684c8`。

N/A 排除 ID：`candidate-sharc-491283e550dcdc6d96d709efae03490a1ce0487a`, `candidate-sharc-632797b27a4d8b9d81a760777c751fbf22f9f443`, `candidate-sharc-95295fee7a4157c1ec7d11964abe36fa0f303b64`。详见 `excluded_na.jsonl`。

## 样本权重与类别权重选型记录

ShARC 权重只应用于 `source=legacy_cleaned` 且来源数据集名称含 `sharc` 的训练行；其他训练行权重为 1.0。改标记录已改为 `human_confirmed`，不再被当作 legacy ShARC 降权。配置按域内 clarify→decide=0 优先，然后域内加权代价、clarify recall、decide recall、macro-F1 排序。

| ShARC 样本权重 | clarify 类权重 | 域内 c→d | 域内门槛 | 域内代价 | clarify Recall | decide Recall | macro-F1 | 秒 |
|---:|---:|---:|---|---:|---:|---:|---:|---:|
| 0.3 | 1.0 | 5 | 未过 | 65 | 0.273 | 0.000 | 0.417 | 0.46 |
| 0.3 | 1.5 | 0 | 通过 | 0 | 1.000 | 0.000 | 0.667 | 0.36 |
| 0.3 | 2.0 | 0 | 通过 | 1 | 1.000 | 0.000 | 0.627 | 0.36 |
| 0.3 | 3.0 | 0 | 通过 | 2 | 1.000 | 0.000 | 0.583 | 0.38 |
| 0.5 | 1.0 | 5 | 未过 | 55 | 0.455 | 0.000 | 0.519 | 0.35 |
| 0.5 | 1.5 | 0 | 通过 | 1 | 1.000 | 0.000 | 0.627 | 0.33 |
| 0.5 | 2.0 | 0 | 通过 | 1 | 1.000 | 0.000 | 0.627 | 0.35 |
| 0.5 | 3.0 | 0 | 通过 | 2 | 1.000 | 0.000 | 0.583 | 0.47 |
| 1.0 | 1.0 | 5 | 未过 | 50 | 0.545 | 0.000 | 0.569 | 0.31 |
| 1.0 | 1.5 | 3 | 未过 | 31 | 0.727 | 0.000 | 0.574 | 0.32 |
| 1.0 | 2.0 | 1 | 未过 | 11 | 0.909 | 0.000 | 0.611 | 0.37 |
| 1.0 | 3.0 | 0 | 通过 | 4 | 1.000 | 0.000 | 0.482 | 0.39 |

选中：ShARC 样本权重 `0.3`，clarify 类权重 `1.5`；模型 `artifacts/decisioner_round2_v1_2026-11-04.joblib`，SHA-256 `f2e1dc659d1d9a78c3136401ba2d987e80bd836a85005530bf75e53510d2dc25`。

## 域内 dev（门槛切片）

样本数 18；准确率 1.000；macro-F1 0.667；加权代价 **0**；clarify→decide **0**。

### 混淆矩阵（真实标签为行）

| 真实值 \ 预测值 | `decide` | `clarify` | `codex` |
|---|---:|---:|---:|
| `decide` | 0 | 0 | 0 |
| `clarify` | 0 | 11 | 0 |
| `codex` | 0 | 0 | 7 |

### 每类指标

| 类别 | Precision | Recall | F1 | 支持数 |
|---|---:|---:|---:|---:|
| `decide` | 0.000 | 0.000 | 0.000 | 0 |
| `clarify` | 1.000 | 1.000 | 1.000 | 11 |
| `codex` | 1.000 | 1.000 | 1.000 | 7 |

### 加权代价明细

- 无误判，总代价为 0。

## ShARC dev（参考，不参与门槛）

样本数 30；准确率 0.567；macro-F1 0.349；加权代价 **31**；clarify→decide **2**。

### 混淆矩阵（真实标签为行）

| 真实值 \ 预测值 | `decide` | `clarify` | `codex` |
|---|---:|---:|---:|
| `decide` | 4 | 11 | 0 |
| `clarify` | 2 | 13 | 0 |
| `codex` | 0 | 0 | 0 |

### 每类指标

| 类别 | Precision | Recall | F1 | 支持数 |
|---|---:|---:|---:|---:|
| `decide` | 0.667 | 0.267 | 0.381 | 15 |
| `clarify` | 0.542 | 0.867 | 0.667 | 15 |
| `codex` | 0.000 | 0.000 | 0.000 | 0 |

### 加权代价明细

- `clarify` → `decide`：2 条 × 10 = 20。
- `decide` → `clarify`：11 条 × 1 = 11。

## 完整 dev（保留总体对照）

样本数 127；准确率 0.882；macro-F1 0.874；加权代价 **33**；clarify→decide **2**。

### 混淆矩阵（真实标签为行）

| 真实值 \ 预测值 | `decide` | `clarify` | `codex` |
|---|---:|---:|---:|
| `decide` | 25 | 11 | 0 |
| `clarify` | 2 | 46 | 0 |
| `codex` | 2 | 0 | 41 |

### 每类指标

| 类别 | Precision | Recall | F1 | 支持数 |
|---|---:|---:|---:|---:|
| `decide` | 0.862 | 0.694 | 0.769 | 36 |
| `clarify` | 0.807 | 0.958 | 0.876 | 48 |
| `codex` | 1.000 | 0.953 | 0.976 | 43 |

### 加权代价明细

- `clarify` → `decide`：2 条 × 10 = 20。
- `codex` → `decide`：2 条 × 1 = 2。
- `decide` → `clarify`：11 条 × 1 = 11。

## 第一轮完整 dev 对照

第一轮原模型成绩来自冻结的 `dev_evaluation.json`，样本 130 条；第二轮完整 dev 使用用户 N/A 剔除及 CSV 裁决后的 127 条，因此这是有标签版本变化的对照，不是完全同一金标集上的模型 A/B。

- 第一轮：Accuracy 0.769；clarify Recall 0.951；clarify→decide 2；加权代价 48。
- 第二轮完整 dev：Accuracy 0.882；clarify Recall 0.958；clarify→decide 2；加权代价 33。

## 冻结金标（条件评测）

- 域内 dev 门槛已通过后才读取金标；读取前 SHA-256 核对通过：`f5b572f313921a14ff7820ea8188af7a7366226ba6a5a7ad83153fae666c0b12`。
- 输入文本按 ID 取自 `data/light_decider_independent_blind_holdout_v1_current_model_predictions_2026-11-03.jsonl`（SHA-256 `589b1d244916e1710d75aac986aecc107b90d95c9398571033a41d8746757fae`）；该文件只提供请求文本，本次忽略其中缓存的模型分数、路由和策略输出。金标标签来自冻结标签文件。
- 共 24 条；`blind-015` 按既定已知分歧单列、不计分，其余 23 条计分。有效评分运行 **1 次**。
- 审计说明：此前两次技术尝试均未产出汇总指标：第一次发现冻结标签文件只存标签；第二次因策略函数本身不返回 dispatch 字段，在首条输入后停止。修正接口后完成本次一次完整计分。金标结果没有用于改数据、调参、改规则或重训。

| 输出 | clarify Recall | clarify→decide | 加权代价 | 三项验收 |
|---|---:|---:|---:|---|
| 新模型 argmax | 6/7 | 0 | 14 | 未通过 |
| 新模型 + routing_policy v3 | 7/7 | 0 | 2 | 通过 |

验收线：clarify Recall 至少 6/7、clarify→decide 为 0、加权代价不超过 10。

## 冻结金标：新模型 argmax（23 条计分）

样本数 23；准确率 0.565；macro-F1 0.365；加权代价 **14**；clarify→decide **0**。

### 混淆矩阵（真实标签为行）

| 真实值 \ 预测值 | `decide` | `clarify` | `codex` | `codex+declare_default` | `codex+check_first` |
|---|---:|---:|---:|---:|---:|
| `decide` | 3 | 1 | 4 | 0 | 0 |
| `clarify` | 0 | 6 | 1 | 0 | 0 |
| `codex` | 0 | 0 | 4 | 0 | 0 |
| `codex+declare_default` | 0 | 2 | 0 | 0 | 0 |
| `codex+check_first` | 0 | 1 | 1 | 0 | 0 |

### 每类指标

| 类别 | Precision | Recall | F1 | 支持数 |
|---|---:|---:|---:|---:|
| `decide` | 1.000 | 0.375 | 0.545 | 8 |
| `clarify` | 0.600 | 0.857 | 0.706 | 7 |
| `codex` | 0.400 | 1.000 | 0.571 | 4 |
| `codex+declare_default` | 0.000 | 0.000 | 0.000 | 2 |
| `codex+check_first` | 0.000 | 0.000 | 0.000 | 2 |

### 加权代价明细

- `clarify` → `codex`：1 条 × 5 = 5。
- `codex+check_first` → `clarify`：1 条 × 1 = 1。
- `codex+check_first` → `codex`：1 条 × 1 = 1。
- `codex+declare_default` → `clarify`：2 条 × 1 = 2。
- `decide` → `clarify`：1 条 × 1 = 1。
- `decide` → `codex`：4 条 × 1 = 4。

## 冻结金标：+ routing_policy v3（23 条计分）

样本数 23；准确率 0.913；macro-F1 0.931；加权代价 **2**；clarify→decide **0**。

### 混淆矩阵（真实标签为行）

| 真实值 \ 预测值 | `decide` | `clarify` | `codex` | `codex+declare_default` | `codex+check_first` |
|---|---:|---:|---:|---:|---:|
| `decide` | 6 | 0 | 2 | 0 | 0 |
| `clarify` | 0 | 7 | 0 | 0 | 0 |
| `codex` | 0 | 0 | 4 | 0 | 0 |
| `codex+declare_default` | 0 | 0 | 0 | 2 | 0 |
| `codex+check_first` | 0 | 0 | 0 | 0 | 2 |

### 每类指标

| 类别 | Precision | Recall | F1 | 支持数 |
|---|---:|---:|---:|---:|
| `decide` | 1.000 | 0.750 | 0.857 | 8 |
| `clarify` | 1.000 | 1.000 | 1.000 | 7 |
| `codex` | 0.667 | 1.000 | 0.800 | 4 |
| `codex+declare_default` | 1.000 | 1.000 | 1.000 | 2 |
| `codex+check_first` | 1.000 | 1.000 | 1.000 | 2 |

### 加权代价明细

- `decide` → `codex`：2 条 × 1 = 2。

### 已知分歧（不计分）

- `blind-015`：金标 `codex+declare_default`，argmax `clarify`，最终动作 `clarify`。
## 限制与来源

- 11 条旧域内 dev 本身很小；本轮新增的人工作出裁决样本也有限，域内通过只能作为粗筛。
- 冻结金标不能代替新盲测题；上线前仍需另造未参与训练和调参的新盲测集。
- 本轮没有改 routing_policy；模型分数未校准；自动派发仍关闭。
- 新数据、复核决策、N/A 排除清单、dev 预测、报告 JSON 与模型文件均在本报告列出的路径下；旧数据版本保持不变。
