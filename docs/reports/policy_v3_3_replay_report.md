# light_decider routing_policy v3.3 候选回放报告

2026-11-06（Asia/Shanghai）。以下为已见数据的离线参考回放，包含 v1–v5 各 24 条及固定 dev 127 条。此回放不作为激活判决。

v3.3 从现役 v3.1 按字节复制。两处产生 explicit_implementation_request 的入口共用一条限制：argmax 为 clarify 时，只有既有 safe_default_for_request 返回非空信号才允许该门覆盖。跳过覆盖后仍按原顺序执行后续逻辑。反向还原核对了版本标识和两处门控之外的所有字节。

同一 round-4 模型对 247 条完整请求做一次批量 predict_proba，两版分别使用同一 argmax 和上下文。五类最终动作精确计分，clarify→decide 计 10，clarify→codex 系计 5，其余误判计 1，正确计 0。回放仅计算动作，自动派发关闭。

逐条分数缓存为 [round4_v3_1_vs_v3_3_replay_scores.jsonl](round4_v3_1_vs_v3_3_replay_scores.jsonl)，247 行，SHA-256 为 `bbe2a2810b9fe21c9c710ac8735af68fc7130b2d56e45f8bc3daf44ed793b38f`。缓存含三类概率、argmax、两版动作、策略原因和覆盖记录、既有默认信号及风险切片标记。

## 切片对照

风险子集取冻结标签的合法风险域与两版共同的风险探测结果的并集。v1 与 dev 采用探测结果补齐，v2 保留既有冻结快照口径，字面值 13 不属于风险域。域内 dev 沿用 round-2/round-4 的来源定义，含 rule_derived、synthetic、human_confirmed。ShARC 参考片仅包括 legacy_cleaned 的 ShARC 样本。

| 切片 | 样本数 | 高危数 | clarify→decide v3.1 → v3.3 | 总代价 v3.1 → v3.3 | 代价变化 | 高危代价 v3.1 → v3.3 |
|---|---:|---:|---:|---:|---:|---:|
| v1–v5 盲测片合计 | 120 | 28 | 1 → 1 | 42 → 32 | -10 | 6 → 1 |
| 域内 dev | 18 | 6 | 0 → 0 | 2 → 2 | +0 | 0 → 0 |
| v1 | 24 | 8 | 0 → 0 | 2 → 2 | +0 | 0 → 0 |
| v2 | 24 | 4 | 0 → 0 | 1 → 1 | +0 | 0 → 0 |
| v3 | 24 | 7 | 1 → 1 | 21 → 21 | +0 | 1 → 1 |
| v4 | 24 | 5 | 0 → 0 | 10 → 5 | -5 | 0 → 0 |
| v5 | 24 | 4 | 0 → 0 | 8 → 3 | -5 | 5 → 0 |
| ShARC dev（参考） | 30 | 7 | 3 → 3 | 41 → 41 | +0 | 3 → 3 |
| 其余 dev（参考） | 79 | 0 | 0 → 0 | 9 → 9 | +0 | 0 → 0 |
| 全部 dev（参考） | 127 | 13 | 3 → 3 | 52 → 52 | +0 | 3 → 3 |

v1 的 blind-015 按既有 24 条统一回放口径计入。v5 的 v3.1 基线复现 B 口径，代价 8、clarify→decide 为 0、clarify 召回 6/7、精确命中 20/24。

## v5-015 型与 declare 题

| 切片 | 编号 | 冻结动作 | argmax | 最终动作 v3.1 → v3.3 | 代价 v3.1 → v3.3 | 代价变化 | 高危域 |
|---|---|---|---|---|---:|---:|---|
| v5 | blind-v5-015 | clarify | clarify | codex → clarify | 5 → 0 | -5 | payment |
| v5 | blind-v5-009 | codex+declare_default | clarify | codex → clarify | 1 → 1 | +0 | — |
| v5 | blind-v5-010 | codex+declare_default | clarify | codex → clarify | 1 → 1 | +0 | — |
| v5 | blind-v5-016 | codex+declare_default | clarify | clarify → clarify | 1 → 1 | +0 | — |

四条指定样本的既有安全默认信号均为空。v5-015 的显式多选一政策请求在 v3.1 被实现门改成 codex，v3.3 保留 clarify。009、010 原先被实现门推到裸 codex，现在保留 clarify。016 两版均为 clarify。三条 declare 的精确命中均为 0/3，单条代价均为 1。

按冻结动作和 argmax 均为 clarify、默认信号为空、实现门推到 codex 的定义，247 条中这类错误由 2 降至 0。v3.1 涉及 blind-v4-003、blind-v5-015。所有 clarify→codex 系误判由 3 变为 1。剩余的 blind-v3-012 的 argmax 是 decide，两版都由实现门推到 codex。盲测片剩余一条 clarify→decide 为 blind-v3-021，两版都保留模型的 decide。

全量 declare_default 精确召回为 5/17 → 5/17。四条 argmax 为 clarify 且有既有默认信号的请求（blind-005、blind-017、blind-v2-020、blind-v2-021）在两版都经实现门进入 codex，再命中 declare_default。另有六条无信号的 declare 题由 codex 转为 clarify，每条代价仍为 1，编号见下表。

## 全部最终动作翻转

共 8 条。变化方向为 v3.1 到 v3.3，负代价变化表示代价减少。

| 切片 | 编号 | 冻结动作 | argmax | 最终动作 v3.1 → v3.3 | 代价 v3.1 → v3.3 | 代价变化 | 高危域 |
|---|---|---|---|---|---:|---:|---|
| v3 | blind-v3-004 | codex+declare_default | clarify | codex → clarify | 1 → 1 | +0 | — |
| v3 | blind-v3-010 | codex+declare_default | clarify | codex → clarify | 1 → 1 | +0 | — |
| v3 | blind-v3-017 | codex+declare_default | clarify | codex → clarify | 1 → 1 | +0 | — |
| v4 | blind-v4-003 | clarify | clarify | codex → clarify | 5 → 0 | -5 | — |
| v4 | blind-v4-022 | codex+declare_default | clarify | codex → clarify | 1 → 1 | +0 | — |
| v5 | blind-v5-009 | codex+declare_default | clarify | codex → clarify | 1 → 1 | +0 | — |
| v5 | blind-v5-010 | codex+declare_default | clarify | codex → clarify | 1 → 1 | +0 | — |
| v5 | blind-v5-015 | clarify | clarify | codex → clarify | 5 → 0 | -5 | payment |

## 输入与候选文件 SHA-256

| 路径 | SHA-256 |
|---|---|
| `data/light_decider_independent_blind_holdout_v1.csv` | `9d065f614126c82b0edd8e149c30b4b641e2748f12ab6c9d86db073036eef41b` |
| `data/frozen_2026-11-03/light_decider_independent_blind_holdout_v1_human_labels_frozen_2026-11-03.jsonl` | `f5b572f313921a14ff7820ea8188af7a7366226ba6a5a7ad83153fae666c0b12` |
| `work/blind_v2_artifact/frozen_eval_inputs_v2.json` | `830cf52895284e37ca18b720a5a22ff0acb368973aa0e81ddc84652b775aaf76` |
| `data/light_decider_independent_blind_holdout_v2_2026-11-04/blind_holdout_v2_user_labels_frozen_2026-11-04.xlsx` | `5f0cc3bacb9d84c34cf5ef7317034552d6c04915321603e9156af523f7f20b4f` |
| `data/light_decider_independent_blind_holdout_v3_2026-11-04/blind_holdout_v3_labels_frozen.jsonl` | `1b28daf61866153cda78fb6f7060ed084659f73b7ef1efd128e5f53dd0d1e07b` |
| `data/light_decider_independent_blind_holdout_v4_2026-11-05/blind_holdout_v4_labels_frozen.jsonl` | `02ca2168736c978bb077f7490c46002a74ed735b96199f93c6709ffc0f1366e1` |
| `data/light_decider_independent_blind_holdout_v5_2026-11-06/blind_holdout_v5_labels_frozen.jsonl` | `2da0a06bacf3d27d77a8f84e6d9c0c4557a49010d575bc92f3c27ba39bb7e011` |
| `data/training_round2_v1_2026-11-04/dev.jsonl` | `cf03fa1583713dff2a600b5df941dc0b6c358fc4bc375ef066f45fc5f77eec82` |
| `artifacts/decisioner_round4_v1_2026-11-05.joblib` | `6eff1a818db972bf887ed885f1cad4162dc5cef69ebdee0fb4f7ac32c37b286b` |
| `light_decider/routing_policy.py` | `719f88ed53635d8b69f35e52e00741b9d9b81128d7f72d99f176ddfe9902e86e` |
| `light_decider/routing_policy_v3_2b_candidate.py` | `f15278154ee892d2264768cf2310113fb188be89f178588db10acd7ab06a8838` |
| `light_decider/routing_policy_v3_3_candidate.py` | `d8200283b628645816c24f67d086971837ba82cc03bea6170cd32930307a92c1` |

输入哈希在回放前后核对一致。现役组合为 round-4 + v3.1，v3.3 为离线候选。
