# light_decider 盲测集 v4 一次性评测报告

> 本报告仅记录本次冻结集评测结果。v4 结果不得用于调参、改规则、改标签或模型；v3.2b 仍为未激活候选，当前组合保持 round-2 + v3.1。

- 评测时间：2026-11-05 13:47:58 +0800（Asia/Shanghai）
- 本次运行：冻结后一次性评测；round-2、round-3 各在 24 条请求上做一次批量 `predict_proba`，全部口径复用同一批模型分数；未训练模型、未改参数或规则。
- 冻结标签 SHA-256：`02ca2168736c978bb077f7490c46002a74ed735b96199f93c6709ffc0f1366e1`；源附件 SHA-256：`db3b7965e9a5f9ca1817027ac56239bcd1e6aeb88b43a717ae6a7e70bfc58f76`。
- 标签来源：助手代填，作者 于 2026-11-05 照单全收、未逐条改动；证据等级同 v3，弱于 v1/v2 独立标注。
- round-2 模型 SHA-256：`f2e1dc659d1d9a78c3136401ba2d987e80bd836a85005530bf75e53510d2dc25`；round-3 模型 SHA-256：`86c9d22575eb0b58774a23e45cc1d01a982c8541c7f53f9586395595fc6b8073`。
- 现役 routing_policy v3.1 SHA-256：`719f88ed53635d8b69f35e52e00741b9d9b81128d7f72d99f176ddfe9902e86e`；候选 v3.2b SHA-256：`f15278154ee892d2264768cf2310113fb188be89f178588db10acd7ab06a8838`。
- 自动派发：保持关闭；本次仅离线计算并写报告。
- 计分：五类动作精确匹配；clarify→decide 计 10，clarify→codex* 计 5，其余错误计 1，判对计 0。三个预注册验收口径为 A/B/C；纯 argmax 仅作参考。

## 验收门槛与总览

| 口径 | 五类准确 | 加权代价 | clarify 召回 | clarify→decide | decide 召回 | declare_default 精确召回 | check_first 精确召回 | 高危错误 / 5 | 门槛 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| round2_argmax | 15/24 (62.5%) | 13 | 6/7 (85.7%) | 0 | 3/6 (50.0%) | 0/3 (0.0%) | 0/2 (0.0%) | 0 | 参考口径 |
| round3_argmax | 13/24 (54.2%) | 11 | 7/7 (100.0%) | 0 | 0/6 (0.0%) | 0/3 (0.0%) | 0/2 (0.0%) | 0 | 参考口径 |
| A_round2_v3_1 | 15/24 (62.5%) | 13 | 6/7 (85.7%) | 0 | 3/6 (50.0%) | 0/3 (0.0%) | 2/2 (100.0%) | 0 | 未通过 |
| B_round3_v3_1 | 12/24 (50.0%) | 16 | 6/7 (85.7%) | 0 | 0/6 (0.0%) | 0/3 (0.0%) | 2/2 (100.0%) | 0 | 未通过 |
| C_round3_v3_2b | 13/24 (54.2%) | 11 | 7/7 (100.0%) | 0 | 0/6 (0.0%) | 0/3 (0.0%) | 2/2 (100.0%) | 0 | 未通过 |

验收线：clarify 召回 ≥6/7、clarify→decide = 0、加权总代价 ≤10。此门槛分别对 A、B、C 判断；两行 argmax 仅作参照，不作为三口径策略验收。

## 口径差分

### A vs B：只改变模型，均使用 v3.1

- 加权代价：13 → 16（round-3 相对 round-2 +3）。五类准确：15/24 → 12/24（-3 条）。
- clarify 召回：6/7 → 6/7；decide 召回：3/6 → 0/6。
- 最终动作改变的条目（round-2→round-3，v3.1 固定）：blind-v4-005, blind-v4-017, blind-v4-019, blind-v4-024。

### B vs C：只改变策略，均使用 round-3

- 加权代价：16 → 11（v3.2b 相对 v3.1 -5）；五类准确：12/24 → 13/24（+1 条）。
- clarify 召回：6/7 → 7/7；decide 召回：0/6 → 0/6。
- 最终动作改变的条目（v3.1→v3.2b，round-3 argmax 固定）：blind-v4-003。

## round2_argmax

- 加权总代价：**13**；五类精确命中：15/24。
- clarify 召回：6/7；clarify→decide：0；decide 召回：3/6。
- declare_default 精确召回：0/3；check_first 精确召回：0/2；高危错误：0/5。

### 五类混淆矩阵

| 金标 \ 预测 | decide | clarify | codex | codex+declare_default | codex+check_first |
|---|---:|---:|---:|---:|---:|
| decide | 3 | 3 | 0 | 0 | 0 |
| clarify | 0 | 6 | 1 | 0 | 0 |
| codex | 0 | 0 | 6 | 0 | 0 |
| codex+declare_default | 0 | 3 | 0 | 0 | 0 |
| codex+check_first | 0 | 1 | 1 | 0 | 0 |

### 五条高危样本逐条结果

| 编号 | 高危域 | 金标 | 预测 | 结果 |
|---|---|---|---|---|
| blind-v4-004 | locale_sensitive_parsing | clarify | clarify | 正确 |
| blind-v4-009 | deduplication | clarify | clarify | 正确 |
| blind-v4-011 | rate_limiting | clarify | clarify | 正确 |
| blind-v4-014 | permission | clarify | clarify | 正确 |
| blind-v4-015 | payment | clarify | clarify | 正确 |

### 全部错误清单

| 编号 | 金标 | 预测 | 代价 | 模型 argmax | 策略原因 | 策略覆盖 |
|---|---|---|---:|---|---|---|
| blind-v4-001 | decide | clarify | 1 | clarify | — | — |
| blind-v4-002 | decide | clarify | 1 | clarify | — | — |
| blind-v4-003 | clarify | codex | 5 | codex | — | — |
| blind-v4-007 | codex+check_first | clarify | 1 | clarify | — | — |
| blind-v4-010 | codex+declare_default | clarify | 1 | clarify | — | — |
| blind-v4-012 | decide | clarify | 1 | clarify | — | — |
| blind-v4-016 | codex+check_first | codex | 1 | codex | — | — |
| blind-v4-022 | codex+declare_default | clarify | 1 | clarify | — | — |
| blind-v4-024 | codex+declare_default | clarify | 1 | clarify | — | — |

## round3_argmax

- 加权总代价：**11**；五类精确命中：13/24。
- clarify 召回：7/7；clarify→decide：0；decide 召回：0/6。
- declare_default 精确召回：0/3；check_first 精确召回：0/2；高危错误：0/5。

### 五类混淆矩阵

| 金标 \ 预测 | decide | clarify | codex | codex+declare_default | codex+check_first |
|---|---:|---:|---:|---:|---:|
| decide | 0 | 6 | 0 | 0 | 0 |
| clarify | 0 | 7 | 0 | 0 | 0 |
| codex | 0 | 0 | 6 | 0 | 0 |
| codex+declare_default | 0 | 0 | 3 | 0 | 0 |
| codex+check_first | 0 | 0 | 2 | 0 | 0 |

### 五条高危样本逐条结果

| 编号 | 高危域 | 金标 | 预测 | 结果 |
|---|---|---|---|---|
| blind-v4-004 | locale_sensitive_parsing | clarify | clarify | 正确 |
| blind-v4-009 | deduplication | clarify | clarify | 正确 |
| blind-v4-011 | rate_limiting | clarify | clarify | 正确 |
| blind-v4-014 | permission | clarify | clarify | 正确 |
| blind-v4-015 | payment | clarify | clarify | 正确 |

### 全部错误清单

| 编号 | 金标 | 预测 | 代价 | 模型 argmax | 策略原因 | 策略覆盖 |
|---|---|---|---:|---|---|---|
| blind-v4-001 | decide | clarify | 1 | clarify | — | — |
| blind-v4-002 | decide | clarify | 1 | clarify | — | — |
| blind-v4-005 | decide | clarify | 1 | clarify | — | — |
| blind-v4-007 | codex+check_first | codex | 1 | codex | — | — |
| blind-v4-010 | codex+declare_default | codex | 1 | codex | — | — |
| blind-v4-012 | decide | clarify | 1 | clarify | — | — |
| blind-v4-016 | codex+check_first | codex | 1 | codex | — | — |
| blind-v4-017 | decide | clarify | 1 | clarify | — | — |
| blind-v4-019 | decide | clarify | 1 | clarify | — | — |
| blind-v4-022 | codex+declare_default | codex | 1 | codex | — | — |
| blind-v4-024 | codex+declare_default | codex | 1 | codex | — | — |

## A_round2_v3_1

- 加权总代价：**13**；五类精确命中：15/24。
- clarify 召回：6/7；clarify→decide：0；decide 召回：3/6。
- declare_default 精确召回：0/3；check_first 精确召回：2/2；高危错误：0/5。

### 五类混淆矩阵

| 金标 \ 预测 | decide | clarify | codex | codex+declare_default | codex+check_first |
|---|---:|---:|---:|---:|---:|
| decide | 3 | 3 | 0 | 0 | 0 |
| clarify | 0 | 6 | 1 | 0 | 0 |
| codex | 0 | 0 | 4 | 0 | 2 |
| codex+declare_default | 1 | 1 | 1 | 0 | 0 |
| codex+check_first | 0 | 0 | 0 | 0 | 2 |

### 五条高危样本逐条结果

| 编号 | 高危域 | 金标 | 预测 | 结果 |
|---|---|---|---|---|
| blind-v4-004 | locale_sensitive_parsing | clarify | clarify | 正确 |
| blind-v4-009 | deduplication | clarify | clarify | 正确 |
| blind-v4-011 | rate_limiting | clarify | clarify | 正确 |
| blind-v4-014 | permission | clarify | clarify | 正确 |
| blind-v4-015 | payment | clarify | clarify | 正确 |

### 全部错误清单

| 编号 | 金标 | 预测 | 代价 | 模型 argmax | 策略原因 | 策略覆盖 |
|---|---|---|---:|---|---|---|
| blind-v4-001 | decide | clarify | 1 | clarify | highest_model_score | — |
| blind-v4-002 | decide | clarify | 1 | clarify | highest_model_score | — |
| blind-v4-003 | clarify | codex | 5 | codex | highest_model_score | — |
| blind-v4-008 | codex | codex+check_first | 1 | codex | existing_project_convention_check | existing_project_convention_check |
| blind-v4-010 | codex+declare_default | decide | 1 | clarify | explicit_explanation_request | explicit_explanation_request |
| blind-v4-012 | decide | clarify | 1 | clarify | highest_model_score | — |
| blind-v4-021 | codex | codex+check_first | 1 | codex | existing_project_convention_check | existing_project_convention_check |
| blind-v4-022 | codex+declare_default | codex | 1 | clarify | explicit_implementation_request | explicit_implementation_request |
| blind-v4-024 | codex+declare_default | clarify | 1 | clarify | highest_model_score | — |

## B_round3_v3_1

- 加权总代价：**16**；五类精确命中：12/24。
- clarify 召回：6/7；clarify→decide：0；decide 召回：0/6。
- declare_default 精确召回：0/3；check_first 精确召回：2/2；高危错误：0/5。

### 五类混淆矩阵

| 金标 \ 预测 | decide | clarify | codex | codex+declare_default | codex+check_first |
|---|---:|---:|---:|---:|---:|
| decide | 0 | 6 | 0 | 0 | 0 |
| clarify | 0 | 6 | 1 | 0 | 0 |
| codex | 0 | 0 | 4 | 0 | 2 |
| codex+declare_default | 1 | 0 | 2 | 0 | 0 |
| codex+check_first | 0 | 0 | 0 | 0 | 2 |

### 五条高危样本逐条结果

| 编号 | 高危域 | 金标 | 预测 | 结果 |
|---|---|---|---|---|
| blind-v4-004 | locale_sensitive_parsing | clarify | clarify | 正确 |
| blind-v4-009 | deduplication | clarify | clarify | 正确 |
| blind-v4-011 | rate_limiting | clarify | clarify | 正确 |
| blind-v4-014 | permission | clarify | clarify | 正确 |
| blind-v4-015 | payment | clarify | clarify | 正确 |

### 全部错误清单

| 编号 | 金标 | 预测 | 代价 | 模型 argmax | 策略原因 | 策略覆盖 |
|---|---|---|---:|---|---|---|
| blind-v4-001 | decide | clarify | 1 | clarify | highest_model_score | — |
| blind-v4-002 | decide | clarify | 1 | clarify | highest_model_score | — |
| blind-v4-003 | clarify | codex | 5 | clarify | explicit_implementation_request | explicit_implementation_request |
| blind-v4-005 | decide | clarify | 1 | clarify | highest_model_score | — |
| blind-v4-008 | codex | codex+check_first | 1 | codex | existing_project_convention_check | existing_project_convention_check |
| blind-v4-010 | codex+declare_default | decide | 1 | codex | explicit_explanation_request | explicit_explanation_request |
| blind-v4-012 | decide | clarify | 1 | clarify | highest_model_score | — |
| blind-v4-017 | decide | clarify | 1 | clarify | highest_model_score | — |
| blind-v4-019 | decide | clarify | 1 | clarify | highest_model_score | — |
| blind-v4-021 | codex | codex+check_first | 1 | codex | existing_project_convention_check | existing_project_convention_check |
| blind-v4-022 | codex+declare_default | codex | 1 | codex | highest_model_score | — |
| blind-v4-024 | codex+declare_default | codex | 1 | codex | highest_model_score | — |

## C_round3_v3_2b

- 加权总代价：**11**；五类精确命中：13/24。
- clarify 召回：7/7；clarify→decide：0；decide 召回：0/6。
- declare_default 精确召回：0/3；check_first 精确召回：2/2；高危错误：0/5。

### 五类混淆矩阵

| 金标 \ 预测 | decide | clarify | codex | codex+declare_default | codex+check_first |
|---|---:|---:|---:|---:|---:|
| decide | 0 | 6 | 0 | 0 | 0 |
| clarify | 0 | 7 | 0 | 0 | 0 |
| codex | 0 | 0 | 4 | 0 | 2 |
| codex+declare_default | 1 | 0 | 2 | 0 | 0 |
| codex+check_first | 0 | 0 | 0 | 0 | 2 |

### 五条高危样本逐条结果

| 编号 | 高危域 | 金标 | 预测 | 结果 |
|---|---|---|---|---|
| blind-v4-004 | locale_sensitive_parsing | clarify | clarify | 正确 |
| blind-v4-009 | deduplication | clarify | clarify | 正确 |
| blind-v4-011 | rate_limiting | clarify | clarify | 正确 |
| blind-v4-014 | permission | clarify | clarify | 正确 |
| blind-v4-015 | payment | clarify | clarify | 正确 |

### 全部错误清单

| 编号 | 金标 | 预测 | 代价 | 模型 argmax | 策略原因 | 策略覆盖 |
|---|---|---|---:|---|---|---|
| blind-v4-001 | decide | clarify | 1 | clarify | highest_model_score | — |
| blind-v4-002 | decide | clarify | 1 | clarify | highest_model_score | — |
| blind-v4-005 | decide | clarify | 1 | clarify | highest_model_score | — |
| blind-v4-008 | codex | codex+check_first | 1 | codex | existing_project_convention_check | existing_project_convention_check |
| blind-v4-010 | codex+declare_default | decide | 1 | codex | explicit_explanation_request | explicit_explanation_request |
| blind-v4-012 | decide | clarify | 1 | clarify | highest_model_score | — |
| blind-v4-017 | decide | clarify | 1 | clarify | highest_model_score | — |
| blind-v4-019 | decide | clarify | 1 | clarify | highest_model_score | — |
| blind-v4-021 | codex | codex+check_first | 1 | codex | existing_project_convention_check | existing_project_convention_check |
| blind-v4-022 | codex+declare_default | codex | 1 | codex | highest_model_score | — |
| blind-v4-024 | codex+declare_default | codex | 1 | codex | highest_model_score | — |

## 本轮边界与后续状态

- v4 仅作为本次一次性验收输入；报告结果不得回流训练、调参、阈值或规则修改。
- 候选 routing_policy v3.2b 未激活；现役仍为 round-2 模型 + routing_policy v3.1。
- 本报告没有打开任何 sealed Codex 参考文件；没有改动标签、模型或策略。
