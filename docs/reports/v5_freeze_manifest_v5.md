# light_decider 盲测集 v5 冻结清单

冻结日期为 2026-11-06（Asia/Shanghai）。标签由助手代填，作者 于 2026-11-06 照单全收，未改一字。来源标记为 `assistant_drafted_chuck_adopted`。

| 文件 | SHA-256 |
|---|---|
| `blind_holdout_v5_unlabeled.xlsx`（未标注版） | `64cc64b0ad649db24b1654bdc98a11091af0798de007b258f7516f243bbc0c43` |
| `blind_holdout_v5_filled_draft.xlsx`（用户提供的代填草稿） | `294dfcbedaa8a0f8a1e9d9566642dac26d0410cd224094d150a0977b9ae51c38` |
| `blind_holdout_v5_labels_frozen.jsonl`（只读冻结版） | `2da0a06bacf3d27d77a8f84e6d9c0c4557a49010d575bc92f3c27ba39bb7e011` |

未标注版和草稿的 24 条编号、题面及补充上下文逐格一致。D–H 的单元格原值转入 JSONL，来源标记另存于 label_source 字段。

| 最终动作 | 条数 |
|---|---:|
| `decide` | 6 |
| `codex` | 6 |
| `clarify` | 7 |
| `codex+declare_default` | 3 |
| `codex+check_first` | 2 |
| **合计** | **24** |

## 冻结时登记的评测口径

A 为 round-2 + routing_policy v3.1，B 为 round-4 + routing_policy v3.1。两个口径均取同一整条请求的模型 argmax，再应用 v3.1，自动派发关闭。

clarify→decide 计 10，clarify→codex 系（含两个子动作）计 5，其余误判计 1，正确计 0。

B 的 clarify 召回至少为 6/7，clarify→decide 为 0，加权代价不超过 10。B 三项全过且总代价严格低于 A，才建议替换默认模型。B 出现任一 clarify→decide 直接出局。A 仅作对照。

机构政策类为 008、017、023，高危类为 006、012、015、019。decide 按题面句式划分，三条问句和三条陈述或祈使句。
