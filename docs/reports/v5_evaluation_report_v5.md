# light_decider 盲测集 v5 评测报告

**建议将默认模型替换为 round-4。** 本次评测后仍由 round-2 + v3.1 现役运行。

评测日期为 2026-11-06（Asia/Shanghai）。标签由助手代填，经 作者 当日原样采纳，来源为 `assistant_drafted_chuck_adopted`。本次从已落盘的只读冻结文件读取 24 条记录。冻结 SHA-256 为 `2da0a06bacf3d27d77a8f84e6d9c0c4557a49010d575bc92f3c27ba39bb7e011`。

A 使用 round-2，B 使用 round-4。每个模型各对 24 条完整题面计算一次批量概率，并将三类 argmax 交给同一个 v3.1 策略。计分使用策略输出的五类最终动作。现役为 round-2 + v3.1，自动派发关闭。

| 评测输入 | SHA-256 |
|---|---|
| A · `decisioner_round2_v1_2026-11-04.joblib` | `f2e1dc659d1d9a78c3136401ba2d987e80bd836a85005530bf75e53510d2dc25` |
| B · `decisioner_round4_v1_2026-11-05.joblib` | `6eff1a818db972bf887ed885f1cad4162dc5cef69ebdee0fb4f7ac32c37b286b` |
| `routing_policy.py` v3.1 | `719f88ed53635d8b69f35e52e00741b9d9b81128d7f72d99f176ddfe9902e86e` |

## 总表

| 口径 | 五类精确命中 | 加权代价 | clarify 召回 | clarify→decide | decide 召回 | declare 精确召回 | check_first 精确召回 |
|---|---:|---:|---:|---:|---:|---:|---:|
| A · round-2 + v3.1 | 18/24 (75.0%) | 10 | 6/7 (85.7%) | 0 | 4/6 (66.7%) | 0/3 (0.0%) | 2/2 (100.0%) |
| B · round-4 + v3.1 | 20/24 (83.3%) | 8 | 6/7 (85.7%) | 0 | 6/6 (100.0%) | 0/3 (0.0%) | 2/2 (100.0%) |

clarify→decide 计 10，clarify→codex 系（含两个子动作）计 5，其余误判计 1，正确计 0。

## 挑战者判决

| 条件 | B 实测 | 结果 |
|---|---:|---|
| clarify 召回 ≥6/7 | 6/7 | 通过 |
| clarify→decide = 0 | 0 | 通过 |
| 加权代价 ≤10 | 8 | 通过 |
| B 总代价严格低于 A | B 8，A 10 | 通过 |

## 分片召回

分母为切片内对应冻结动作的条数，分子只计最终动作精确匹配。

| 切片 | 样本编号尾号 | A | B |
|---|---|---:|---:|
| decide · 问句式 | 003, 004, 024 | 2/3 (66.7%) | 3/3 (100.0%) |
| decide · 陈述或祈使句式 | 014, 021, 022 | 2/3 (66.7%) | 3/3 (100.0%) |
| clarify · 机构政策类 | 008, 017, 023 | 3/3 (100.0%) | 3/3 (100.0%) |
| clarify · 高危类 | 006, 012, 015, 019 | 3/4 (75.0%) | 3/4 (75.0%) |
| declare_default · 精确召回 | 009, 010, 016 | 0/3 (0.0%) | 0/3 (0.0%) |
| check_first · 精确召回 | 011, 020 | 2/2 (100.0%) | 2/2 (100.0%) |

## 完整错误清单

### A · round-2 + v3.1

共 6 条错误，合计代价 10。

| 编号 | 冻结动作 | 模型 argmax | 最终动作 | 代价 | 策略原因 | 策略覆盖 |
|---|---|---|---|---:|---|---|
| blind-v5-003 | `decide` | `clarify` | `clarify` | 1 | `highest_model_score` | — |
| blind-v5-009 | `codex+declare_default` | `clarify` | `codex` | 1 | `explicit_implementation_request` | explicit_implementation_request |
| blind-v5-010 | `codex+declare_default` | `clarify` | `codex` | 1 | `explicit_implementation_request` | explicit_implementation_request |
| blind-v5-015 | `clarify` | `clarify` | `codex` | 5 | `explicit_implementation_request` | explicit_implementation_request |
| blind-v5-016 | `codex+declare_default` | `clarify` | `clarify` | 1 | `highest_model_score` | — |
| blind-v5-021 | `decide` | `clarify` | `clarify` | 1 | `highest_model_score` | — |

### B · round-4 + v3.1

共 4 条错误，合计代价 8。

| 编号 | 冻结动作 | 模型 argmax | 最终动作 | 代价 | 策略原因 | 策略覆盖 |
|---|---|---|---|---:|---|---|
| blind-v5-009 | `codex+declare_default` | `clarify` | `codex` | 1 | `explicit_implementation_request` | explicit_implementation_request |
| blind-v5-010 | `codex+declare_default` | `clarify` | `codex` | 1 | `explicit_implementation_request` | explicit_implementation_request |
| blind-v5-015 | `clarify` | `clarify` | `codex` | 5 | `explicit_implementation_request` | explicit_implementation_request |
| blind-v5-016 | `codex+declare_default` | `clarify` | `clarify` | 1 | `highest_model_score` | — |
