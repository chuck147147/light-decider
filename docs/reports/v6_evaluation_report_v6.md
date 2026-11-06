# light_decider 盲测集 v6 评测报告

## 评测范围与来源

本报告只评测本次冻结的 24 条 v6 标签。题目由助手代填、作者 于 2026-11-06 照单全收（未逐条修改），来源为 `assistant_drafted_chuck_adopted`，不是独立盲标；021 是已记录污染项。自动派发保持关闭。
模型为 round-4；A 使用现役 routing_policy v3.1，B 使用候选 routing_policy v3.3。两种策略使用同一次批量模型推理分数，未重训、未调参、未改规则。

| 输入 | SHA-256 |
|---|---|
| 冻结标签 JSONL | `9a687a497f0485010ad5a1de538e485c165c4cee3780190d55ee7e2d3e304f6f` |
| round-4 模型 | `6eff1a818db972bf887ed885f1cad4162dc5cef69ebdee0fb4f7ac32c37b286b` |
| routing_policy v3.1 | `719f88ed53635d8b69f35e52e00741b9d9b81128d7f72d99f176ddfe9902e86e` |
| routing_policy v3.3 候选 | `d8200283b628645816c24f67d086971837ba82cc03bea6170cd32930307a92c1` |

## 总体结果

代价：clarify→decide = 10，clarify→任一 codex 系动作 = 5，其余错误 = 1，正确 = 0。准确动作按五类原标签匹配。

| 口径 | 总代价 | clarify 召回 | clarify→decide | decide 召回 | declare_default 精确召回 | check_first 精确召回 | 高危条目错误 | 三线 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| A：round-4 + v3.1（现役） | 14 | 5/7 | 0 | 6/6 | 0/3 | 2/2 | 1/4 | 未通过 |
| B：round-4 + v3.3（候选） | 4 | 7/7 | 0 | 6/6 | 0/3 | 2/2 | 0/4 | 通过 |

### 混淆矩阵（行=金标，列=最终动作）

| 口径 / 金标 | decide | codex | codex+declare_default | codex+check_first | clarify |
|---|---:|---:|---:|---:|---:|
| A：v3.1 / decide | 6 | 0 | 0 | 0 | 0 |
| A：v3.1 / codex | 0 | 5 | 0 | 0 | 1 |
| A：v3.1 / codex+declare_default | 0 | 0 | 0 | 0 | 3 |
| A：v3.1 / codex+check_first | 0 | 0 | 0 | 2 | 0 |
| A：v3.1 / clarify | 0 | 2 | 0 | 0 | 5 |
| B：v3.3 / decide | 6 | 0 | 0 | 0 | 0 |
| B：v3.3 / codex | 0 | 5 | 0 | 0 | 1 |
| B：v3.3 / codex+declare_default | 0 | 0 | 0 | 0 | 3 |
| B：v3.3 / codex+check_first | 0 | 0 | 0 | 2 | 0 |
| B：v3.3 / clarify | 0 | 0 | 0 | 0 | 7 |

## 分片结果

### Decide：全 6 条与剔除污染项 021 后的干净 5 条

问句/陈述的划分按请求文本是否以问句形式直接提问（含问号或中文疑问句尾）判定；其余记为陈述/祈使。

| 口径 | 全部 decide | 问句 | 陈述/祈使 | 排除 021 后 | 干净问句 | 干净陈述/祈使 |
|---|---:|---:|---:|---:|---:|---:|
| A：v3.1 | 6/6 | 3/3 | 3/3 | 5/5 | 3/3 | 2/2 |
| B：v3.3 | 6/6 | 3/3 | 3/3 | 5/5 | 3/3 | 2/2 |

### Clarify 子集

| 口径 | 机构政策类 | 高危类 |
|---|---:|---:|
| A：v3.1 | 2/3 | 3/4 |
| B：v3.3 | 3/3 | 4/4 |

高危类按冻结标签中的非“无”高危域标记划分；政策类为高危标记为“无”的 clarify 样本。

### 高危样本逐条结果

| 样本 | 高危域 | 金标 | A 最终动作 | B 最终动作 | A 正误 | B 正误 |
|---|---|---|---|---|---|---|
| blind-v6-003 | payment | clarify | codex | clarify | 错 | 对 |
| blind-v6-011 | rate_limiting | clarify | clarify | clarify | 对 | 对 |
| blind-v6-013 | deduplication | clarify | clarify | clarify | 对 | 对 |
| blind-v6-014 | locale_sensitive_parsing | clarify | clarify | clarify | 对 | 对 |

### 指定样本 blind-v6-003

金标 `clarify`，模型 argmax `clarify`（分数：`{"clarify":0.555368373244429,"codex":0.19966481128127794,"decide":0.24496681547429297}`）；A 最终 `codex`（规则 `explicit_implementation_request`），B 最终 `clarify`（规则 `None`）。

## 两策略差分

| 样本 | Argmax | v3.1 动作 | v3.3 动作 | 金标 | 变化原因 |
|---|---|---|---|---|---|
| blind-v6-003 | clarify | codex | clarify | clarify | v3.3 实际触发 `无` |
| blind-v6-015 | clarify | codex | clarify | clarify | v3.3 实际触发 `无` |

## 完整错误清单

每项均列金标、模型 argmax、最终动作、策略原因、高危域与计价。021 保留在字面口径中并标注污染。

### A：round-4 + v3.1

| 样本 | 金标 | Argmax | 最终动作 | 规则 / 原因 | 高危域 | 代价 | 污染 |
|---|---|---|---|---|---|---:|---|
| blind-v6-001 | codex+declare_default | clarify | clarify | `highest_model_score` | 无 | 1 | 否 |
| blind-v6-003 | clarify | clarify | codex | `explicit_implementation_request` | payment | 5 | 否 |
| blind-v6-005 | codex+declare_default | clarify | clarify | `highest_model_score` | 无 | 1 | 否 |
| blind-v6-006 | codex | codex | clarify | `locale_sensitive_value_format_ambiguous` | 无 | 1 | 否 |
| blind-v6-015 | clarify | clarify | codex | `explicit_implementation_request` | 无 | 5 | 否 |
| blind-v6-024 | codex+declare_default | clarify | clarify | `highest_model_score` | 无 | 1 | 否 |
### B：round-4 + v3.3

| 样本 | 金标 | Argmax | 最终动作 | 规则 / 原因 | 高危域 | 代价 | 污染 |
|---|---|---|---|---|---|---:|---|
| blind-v6-001 | codex+declare_default | clarify | clarify | `highest_model_score` | 无 | 1 | 否 |
| blind-v6-005 | codex+declare_default | clarify | clarify | `highest_model_score` | 无 | 1 | 否 |
| blind-v6-006 | codex | codex | clarify | `locale_sensitive_value_format_ambiguous` | 无 | 1 | 否 |
| blind-v6-024 | codex+declare_default | clarify | clarify | `highest_model_score` | 无 | 1 | 否 |

## 预注册判决

B 替换策略的建议条件为：三线全过，且总代价严格低于 A；B 若出现任何 clarify→decide 则直接出局。

候选满足预注册数值条件，可建议 作者 决定是否替换；本次未激活，现役仍为 v3.1。

本次只完成冻结集的一次策略口径评测。v6 标签来源为助手代填后由 作者 照单全收，证据等级弱于独立盲标；且 021 是训练主题污染项，因此结果不应被表述为完全独立的泛化证据。
