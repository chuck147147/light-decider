# light_decider 盲测集 v6 冻结清单

冻结时间：2026-11-06 11:07:48 CST（Asia/Shanghai）。共 24 条。标签由助手代填，作者 于 2026-11-06 照单全收，未逐条修改；来源标记为 assistant_drafted_chuck_adopted。此来源不是独立盲标。

## 文件与哈希

| 文件 | SHA-256 |
|---|---|
| blind_holdout_v6_unlabeled.xlsx（未标注版） | 6e9621dc96812ffea951513d6828279865eec4c40ba826f31cd634f940054b9e |
| blind_holdout_v6_filled_draft.xlsx（助手代填草稿，用户提供） | c0948a2be2f0d6b42ab3850a65b167651196908d85ebcfec6a0a4548fc46d6d9 |
| blind_holdout_v6_labels_frozen.jsonl（D–H 原值转换） | 9a687a497f0485010ad5a1de538e485c165c4cee3780190d55ee7e2d3e304f6f |

草稿哈希与用户提供的预期前缀 c0948a2b 匹配。冻结前，草稿与未标注版的 24 条 sample_id、请求文本及补充上下文逐格一致。D–H 标签值按原值保存，未重标、未规范化。

## 动作分布

| 最终动作 | 条数 |
|---|---:|
| decide | 6 |
| codex | 6 |
| clarify | 7 |
| codex+declare_default | 3 |
| codex+check_first | 2 |
| **合计** | **24** |

## 污染记录

blind-v6-021 与 round-4 训练条目 decide-boundary-003 主题近重复，Jaccard 为 0.111。作者 裁决照常冻结，并将 blind-v6-021 记为污染项；冻结标签与题面均不作修改。后续评测的 decide 召回同时报告全 6 条字面口径，以及剔除该污染项后的干净 5 条口径。

本清单只记录冻结事实与污染项，不含任何模型输出。冻结标签可用于本次预注册评测，不得回写训练集。
