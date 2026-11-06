# routing_policy v3.4 离线回放报告

**状态：候选策略，未激活。** v1–v6 与 dev 均为已见数据；本报告是回放参考分，不构成泛化证据。
本轮只改 `safe_default_for_request` 的授权信号识别。v3.3 的关键问句优先顺序、高危域拒绝、默认类型和实现门护栏均保持原样。自动派发关闭。

## 数据来源与完整性

训练侧语义来源只使用已确认、`reviewed=true` 的训练增加数据及标注细则 v3：rare_class 主批 160 条、补单 28 条、decide 边界 60 条，共 248 条；其中 73 条为 `codex+declare_default`。授权结构归纳为决定权转交、按执行者判断行事、依据用户给出的取向代选、偏好空缺同时明确委托、临时默认由执行者确定等正向结构。没有把 v1–v6 题面中的措辞抽取为信号。原有安全默认的具体对象与默认值目录未扩展。
| 来源 | 路径 | SHA-256 |
|---|---|---|
| Round-3 已确认增加数据（188 条） | `data/training_round3_v1_2026-11-05/confirmed_additions.jsonl` | `252049a40e2d0401b6d7da41b6ab4bb57a919ebc01c514dd537c3486d5d5ed64` |
| Round-4 已确认增加数据（60 条） | `data/training_round4_v1_2026-11-05/confirmed_additions.jsonl` | `26d5fccf8c64cfe339cb66270cf1d0a3f470dbdda48f9d4e7dc1496024332ca9` |
| 两轴标注细则 v3 | `data/light_decider_two_axis_annotation_guideline_v3.md` | `067d56640b50979db65967ff27a94e7f9e18aca22f38b98de96fe61075f8a18c` |

候选基于现役 v3.3（仅原策略元数据版本号与授权信号块变更）：
- v3.3 输入策略 SHA-256：`0e6d6493c01ad16f56574e4311bd2feb95d6f9872517b9037dc5506caaadabc0`。
- round-4 模型 SHA-256：`6eff1a818db972bf887ed885f1cad4162dc5cef69ebdee0fb4f7ac32c37b286b`。
- v3.4 候选 SHA-256：`f1dd31ace55199e21eff3b9543cb082b642d58696736768c9d0a05271fd36a82`。

v1–v5 与 dev 的 round-4 分数从既有 247 行回放缓存复用，SHA-256 为 `bbe2a2810b9fe21c9c710ac8735af68fc7130b2d56e45f8bc3daf44ed793b38f`；v6 的 24 条使用同一 round-4 模型补算。随后两版策略均在相同分数上回放。新缓存共 271 条：`data/policy_regression_runs/routing_policy_v3_4_replay_2026-11-06/round4_v3_3_vs_v3_4_replay_scores.jsonl`，SHA-256：`d1d2ac82f149a930018d49013e911af95f97d3d84b545b2090b5d5295e24bde5`。冻结标签和模型文件只读。

## 全部样本总代价

计价：正确 0；clarify→decide 10；clarify→codex 系（codex / declare_default / check_first）5；其他错误 1。
| 范围 | 样本数 | v3.3 代价 | v3.4 代价 | 变化（v3.4−v3.3） |
|---|---:|---:|---:|---:|
| v1–v6 盲测集合并（已见） | 144 | 36 | 35 | -1 |
| Round-4 dev（开发集） | 127 | 52 | 52 | +0 |
| 合计 | 271 | 88 | 87 | -1 |

## Declare_default 精确召回（逐套）

| 题集 | 金标数 | v3.3 | v3.4 | 找回数 |
|---|---:|---:|---:|---:|
| v1 | 3 | 2/3 | 2/3 | 0 |
| v2 | 3 | 3/3 | 3/3 | 0 |
| v3 | 3 | 0/3 | 1/3 | 1 |
| v4 | 3 | 0/3 | 0/3 | 0 |
| v5 | 3 | 0/3 | 0/3 | 0 |
| v6 | 3 | 0/3 | 0/3 | 0 |

v3–v6 中 v3.3 原先漏掉 `12` 条；v3.4 找回 `1` 条，要求至少找回 `6` 条。找回样本：`v3/blind-v3-004`。

## Clarify→codex 系代价

| 范围 | v3.3 次数 / 代价 | v3.4 次数 / 代价 | 变化 |
|---|---:|---:|---:|
| v1 | 0 / 0 | 0 / 0 | +0 |
| v2 | 0 / 0 | 0 / 0 | +0 |
| v3 | 1 / 5 | 1 / 5 | +0 |
| v4 | 0 / 0 | 0 / 0 | +0 |
| v5 | 0 / 0 | 0 / 0 | +0 |
| v6 | 0 / 0 | 0 / 0 | +0 |
| dev | 0 / 0 | 0 / 0 | +0 |
| 合计 | 1 / 5 | 1 / 5 | +0 |

新增 clarify→declare_default：`0`。新增 clarify→codex：`0`。新增 clarify→任一 codex 系动作：`0`。

## 新增非 declare 金标误报

定义：金标不是 `codex+declare_default`，v3.3 未输出该动作而 v3.4 新输出该动作。

无新增误报。

v3.4 全部非 declare 金标误报：`0` 条（其中新增 `0` 条）。

## 全部动作翻转

以下列出 v3.3 与 v3.4 最终动作不同的每条样本；同一模型 argmax 分数，`Δ代价` 为 v3.4 减 v3.3。

| 样本 | 金标 | Argmax | v3.3 → v3.4 | v3.3 规则 | v3.4 规则 | Δ代价 |
|---|---|---|---|---|---|---:|
| `v3/blind-v3-004` | codex+declare_default | clarify | clarify → codex+declare_default | `highest_model_score` | `safe_default_declared` | -1 |

## 预注册通过线与判定

- v3–v6 基线漏判的 declare_default 数：`12`；至少找回一半：`6`；实际找回：`1`。
- 已见数据上的新增 clarify→codex 系损伤：`0`（新增 declare `0`，新增裸 codex `0`）。
- **判定：未通过本轮门槛，按要求搁置 v3.4，不建议造 v7 判决题；现役 v3.3 保持不变。**

## 约束核对

- v3.4 候选从现役 v3.3 派生；除 `safe_default_for_request` 授权识别和候选版本标识外，其余策略代码逐字相同。
- explicit_key_choice_question 与关键问句澄清规则仍早于实现门和安全默认判断。
- 高危域早退 guard 原样保留；新增识别信号不会让高危请求产生 declare_default。
- 没有重训、没有修改 v3.3 现役策略、模型或任何冻结文件；自动派发未启用。
