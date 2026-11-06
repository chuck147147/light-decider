> 本成绩为开发集分数，三套题均已见过，不构成泛化证据；v3.2 的验证需等待未来 v4。

# routing_policy v3.2 候选开发集回归

## 口径与完整性

- 合并集：v1/v2/v3 各 24 条，共 72 条；标签均按原冻结来源读取，没有修改。
- 固定模型：round-2 `decisioner_round2_v1_2026-11-04.joblib`；每条 argmax 取自本轮一次性 round-2 推理缓存；候选回归只重放策略，没有再次推理模型。
- 模型 SHA-256：`f2e1dc659d1d9a78c3136401ba2d987e80bd836a85005530bf75e53510d2dc25`。
- v3.1 策略 SHA-256：`719f88ed53635d8b69f35e52e00741b9d9b81128d7f72d99f176ddfe9902e86e`。
- v3.2 候选文件 SHA-256：`1e846ddd3d5a03ec1ff51f7b534246cbd4feb207b2efb13d764669771df183bd`。
- v1 当时存档输出来自 2026-11-03 semantic draft，和固定 round-2 模型不同；它保留在消融审计作历史对照，72 条主口径统一使用固定 round-2。
- 高危标记来源：v1 的 8 条使用 Codex blind reference 作代理标记（不是用户确认金标）；v2 4 条来自用户冻结域标签；v3 5 条来自冻结标签。另报 v2+v3 用户冻结标记切片，避免混淆来源。
- 自动派发保持关闭。此候选文件不是活动策略，未替换 `light_decider/routing_policy.py`。

## v3.1 与候选 v3.2 总指标

| 指标 | v3.1 | v3.2 候选 | 判据 |
|---|---:|---:|---|
| 72 条加权总代价 | 25 | 24 | 必须严格下降：通过 |
| 五动作精确命中 | 55/72 | 52/72 | 参考指标 |
| clarify 召回 | 19/21 | 20/21 | 参考指标 |
| clarify→decide | 0 | 0 | 必须为 0：通过 |
| 高危错误（全部 17 条，含 v1 代理标记） | 1/17 | 1/17 | 不得增加：通过 |
| 高危错误（v2/v3 用户冻结标记 9 条） | 0/9 | 0/9 | 辅助切片 |

**回归结论：通过。满足三条候选门槛。**

## 按题集拆分

| 题集 | n | v3.1 代价 | v3.2 代价 | clarify 召回 v3.1→v3.2 | 高危错误 v3.1→v3.2 |
|---|---:|---:|---:|---:|---:|
| v1 | 24 | 3 | 5 | 7/7 → 7/7 | 1/8 → 1/8 |
| v2 | 24 | 8 | 10 | 6/7 → 6/7 | 0/4 → 0/4 |
| v3 | 24 | 14 | 9 | 6/7 → 7/7 | 0/5 → 0/5 |

## 五动作混淆矩阵：候选 v3.2

| 金标 \ 预测 | decide | clarify | codex | codex+declare_default | codex+check_first |
|---|---:|---:|---:|---:|---:|
| decide | 10 | 1 | 7 | 0 | 0 |
| clarify | 0 | 20 | 1 | 0 | 0 |
| codex | 0 | 1 | 15 | 0 | 2 |
| codex+declare_default | 0 | 8 | 0 | 1 | 0 |
| codex+check_first | 0 | 0 | 0 | 0 | 6 |

## 高危错误变化明细

| 方向 | 样本 | 说明 |
|---|---|---|
| 无变化 | — | 高危错误集合保持不变 |

## v3.1 → v3.2 候选动作变化（共 8 条）

| 样本 | 金标 | argmax | v3.1 | v3.2 候选 | 代价 v3.1→v3.2 | 高危域 |
|---|---|---|---|---|---:|---|
| v1/blind-005 | codex+declare_default | clarify | codex+declare_default | clarify | 0→1 | 无 |
| v1/blind-017 | codex+declare_default | clarify | codex+declare_default | clarify | 0→1 | 无 |
| v2/blind-v2-020 | codex+declare_default | clarify | codex+declare_default | clarify | 0→1 | 无 |
| v2/blind-v2-021 | codex+declare_default | clarify | codex+declare_default | clarify | 0→1 | 无 |
| v3/blind-v3-004 | codex+declare_default | clarify | codex | clarify | 1→1 | 无 |
| v3/blind-v3-010 | codex+declare_default | clarify | codex | clarify | 1→1 | 无 |
| v3/blind-v3-012 | clarify | clarify | codex | clarify | 5→0 | 无 |
| v3/blind-v3-017 | codex+declare_default | clarify | codex | clarify | 1→1 | 无 |

## 翻转规则与改动边界

候选只收窄 `explicit_implementation_request`：当模型 argmax 已为 `clarify` 时，不再由实现请求闸门把它改成 `codex`；模型给出其他动作时保留 v3.1 的原有闸门行为。没有新增规则。高危域禁止 override 到 decide 的 guard、所有其他规则和阈值保持原样。

本候选仍是已见开发集上的消融派生版本；不要据此认定已泛化或上线。未来 v4 独立盲测前，不从本报告追加调参或规则。
