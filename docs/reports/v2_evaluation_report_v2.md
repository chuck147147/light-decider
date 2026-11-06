# light_decider 盲测集 v2 一次性泛化评测

- 评测时间：2026-11-04T16:48:54.652257+08:00。
- 题集：24 条合成定向压力题；本次按用户冻结标签逐条评分。
- 标签冻结文件 SHA-256：`5f0cc3bacb9d84c34cf5ef7317034552d6c04915321603e9156af523f7f20b4f`；冻结清单：`data/light_decider_independent_blind_holdout_v2_2026-11-04/freeze_manifest_v2_user_labels_2026-11-04.json`。
- 第二轮模型 SHA-256：`f2e1dc659d1d9a78c3136401ba2d987e80bd836a85005530bf75e53510d2dc25`；routing_policy v3 SHA-256：`e1a1107aaf29ff75482ae1ab581d9f233c19d7763bef5ceb868bd468b48e5ae3`。
- 本报告仅包含唯一一次评分；没有据结果改标签、训练/调参或改策略，v2 未进入训练集；自动派发保持关闭。
- 验收线在推理前已写入冻结清单：clarify 召回 ≥ 6/7；clarify→decide = 0；加权总代价 ≤ 10。
- 用户确认的标签来源声明已原文收入冻结清单。001–004 的两轴“否/否”不参与本评测，最终动作按用户标注 `decide` 计分。
- 数据备注：填写表在 C/F/H 列存在字面值 `13`（分别 22/20/24 个单元格），原始冻结文件保留不变；推理文本和上下文取自原始冻结题目文件，仅将四个已知域名标记计入高危切片，未把 `13` 当作上下文或高危域。
- 计分类别保留五个用户动作；模型 argmax 只能输出 `decide/clarify/codex`，策略输出可以包含两个 codex 特殊动作。clarify→codex 的 5 分也适用于 `codex+declare_default` 和 `codex+check_first`。

## v2 结果总览与验收

| 口径 | clarify 召回 | clarify→decide | 加权总代价 | 高危域错误 | 验收 |
|---|---:|---:|---:|---:|---|
| 第二轮模型 argmax | 6/7 | 0 | 14 | 0/4 | 未通过 |
| 第二轮模型 + routing_policy v3 | 5/7 | 0 | 16 | 0/4 | 未通过 |

### v1 冻结金标历史对照（不重跑）

| 口径 | 计分数 | clarify 召回 | clarify→decide | 加权总代价 |
|---|---:|---:|---:|---:|
| v1 金标：第二轮模型 argmax | 23/24 | 6/7 | 0 | 14 |
| v1 金标：第二轮模型 + routing_policy v3 | 23/24 | 7/7 | 0 | 2 |

v1 数字直接摘自上述已存档报告，未重新推理；当时 `blind-015` 作为已知分歧不计分。**v1 策略分数含开发集成分**，不应视为独立泛化成绩；v2 是这次新的盲测集，样本仅 24 条且有意加大边界题比例。

## 第二轮模型 argmax

样本数 24；准确率 0.583；macro-F1 0.289；加权总代价 **14**；clarify→decide **0**。

### 混淆矩阵（真实标签为行）

| 真实值 \ 预测值 | `decide` | `clarify` | `codex` | `codex+declare_default` | `codex+check_first` |
|---|---:|---:|---:|---:|---:|
| `decide` | 0 | 0 | 4 | 0 | 0 |
| `clarify` | 0 | 6 | 1 | 0 | 0 |
| `codex` | 0 | 0 | 8 | 0 | 0 |
| `codex+declare_default` | 0 | 2 | 1 | 0 | 0 |
| `codex+check_first` | 0 | 1 | 1 | 0 | 0 |

### 每类 Precision / Recall

| 类别 | Precision | Recall | F1 | 支持数 |
|---|---:|---:|---:|---:|
| `decide` | 0.000 | 0.000 | 0.000 | 4 |
| `clarify` | 0.667 | 0.857 | 0.750 | 7 |
| `codex` | 0.533 | 1.000 | 0.696 | 8 |
| `codex+declare_default` | 0.000 | 0.000 | 0.000 | 3 |
| `codex+check_first` | 0.000 | 0.000 | 0.000 | 2 |

### 加权代价明细

- `clarify` → `codex`：1 条 × 5 = 5。
- `codex+check_first` → `clarify`：1 条 × 1 = 1。
- `codex+check_first` → `codex`：1 条 × 1 = 1。
- `codex+declare_default` → `clarify`：2 条 × 1 = 2。
- `codex+declare_default` → `codex`：1 条 × 1 = 1。
- `decide` → `codex`：4 条 × 1 = 4。

验收：clarify 召回 `6/7`（通过）；clarify→decide `0`（通过）；加权总代价 `14`（未通过）。**综合：未通过**。

## 第二轮模型 + routing_policy v3

样本数 24；准确率 0.667；macro-F1 0.573；加权总代价 **16**；clarify→decide **0**。

### 混淆矩阵（真实标签为行）

| 真实值 \ 预测值 | `decide` | `clarify` | `codex` | `codex+declare_default` | `codex+check_first` |
|---|---:|---:|---:|---:|---:|
| `decide` | 1 | 0 | 3 | 0 | 0 |
| `clarify` | 0 | 5 | 2 | 0 | 0 |
| `codex` | 0 | 0 | 8 | 0 | 0 |
| `codex+declare_default` | 0 | 1 | 2 | 0 | 0 |
| `codex+check_first` | 0 | 0 | 0 | 0 | 2 |

### 每类 Precision / Recall

| 类别 | Precision | Recall | F1 | 支持数 |
|---|---:|---:|---:|---:|
| `decide` | 1.000 | 0.250 | 0.400 | 4 |
| `clarify` | 0.833 | 0.714 | 0.769 | 7 |
| `codex` | 0.533 | 1.000 | 0.696 | 8 |
| `codex+declare_default` | 0.000 | 0.000 | 0.000 | 3 |
| `codex+check_first` | 1.000 | 1.000 | 1.000 | 2 |

### 加权代价明细

- `clarify` → `codex`：2 条 × 5 = 10。
- `codex+declare_default` → `clarify`：1 条 × 1 = 1。
- `codex+declare_default` → `codex`：2 条 × 1 = 2。
- `decide` → `codex`：3 条 × 1 = 3。

验收：clarify 召回 `5/7`（未通过）；clarify→decide `0`（通过）；加权总代价 `16`（未通过）。**综合：未通过**。

## 高危域错误明细

| 口径 | 错误数 | 错误条目（ID / 域 / 金标 / 预测） |
|---|---:|---|
| 模型 argmax | 0/4 | 无 |
| 模型 + policy v3 | 0/4 | 无 |

## routing_policy v3 翻转清单

| 样本 ID | 模型 argmax | 最终动作 | 触发规则 / 原因 |
|---|---|---|---|
| blind-v2-002 | codex | decide | comparison_without_execution_request |
| blind-v2-018 | clarify | codex | explicit_implementation_request |
| blind-v2-021 | clarify | codex | explicit_implementation_request |
| blind-v2-023 | clarify | codex+check_first | existing_project_convention_check |
| blind-v2-024 | codex | codex+check_first | existing_project_convention_check |

## 边界与后续控制

- v2 是定向压力题，不是自然流量随机抽样；24 条尤其是 7 条 clarify 的样本量只能提供小样本泛化信号。
- 结果只作验收记录。任何错题的标签复核、模型训练/参数修改或路由规则修改，均须先等用户决定；v2 不得加入训练集。
- 自动派发未启用；本次没有执行外部派发或业务副作用。
