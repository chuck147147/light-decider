> 本成绩为开发集分数，v1/v2/v3 三套题均已见过，不构成泛化证据；v3.2b 的验证需等待未来 v4。

# routing_policy v3.2b 候选开发集回归

## 结论

**候选通过本单门槛，但仍是未激活的开发集候选。** 72 条加权总代价为 20，低于 v3.1 的 25 和 v3.2 的 24；`clarify→decide` 为 0；17 条高危样本错误数保持 1，没有增加。`codex+declare_default` 精确命中恢复到 5/9，其中保住了 v1-005、v1-017、v2-020、v2-021 四条；v3-012 仍为 `clarify`。

## 口径与来源

- 合并集：v1/v2/v3 各 24 条，共 72 条。标签沿用已冻结文件，没有修改。
- 固定模型：`decisioner_round2_v1_2026-11-04.joblib`，SHA-256：`f2e1dc659d1d9a78c3136401ba2d987e80bd836a85005530bf75e53510d2dc25`。
- 比较基线：已归档的 [v3.2 开发集回归报告](regression_v3_2_devset.md)。该报告说明了 72 条使用同一轮 round-2 推理缓存的 argmax，策略回放没有再次推理模型。
- 当前工作区没有保存那份逐条 round-2 分数缓存。因此本报告没有重新推理或重建模型分数；72 条汇总由已归档的 v3.1/v3.2 指标、混淆矩阵和动作变化表增量推导。对策略变化涉及的 8 条样本，按归档表中的固定 argmax=`clarify` 单独调用策略候选及同源默认检测函数核验。未变化的 64 条沿用 v3.2 归档回归结果。
- 代价权重：`clarify→decide`=10，`clarify→codex*`=5，其余错误=1，正确=0。
- 高危错误使用既定 17 条口径，其中 v1 的 8 条为 Codex blind reference 代理标记（非用户确认金标），v2/v3 的 9 条为冻结域标签。
- v3.1 活动策略 SHA-256：`719f88ed53635d8b69f35e52e00741b9d9b81128d7f72d99f176ddfe9902e86e`；v3.2 候选 SHA-256：`1e846ddd3d5a03ec1ff51f7b534246cbd4feb207b2efb13d764669771df183bd`。
- v3.2b 候选 SHA-256：`f15278154ee892d2264768cf2310113fb188be89f178588db10acd7ab06a8838`。

## 三方指标对照

| 指标 | v3.1 | v3.2 | v3.2b | 候选门槛 / 说明 |
|---|---:|---:|---:|---|
| 72 条加权总代价 | 25 | 24 | **20** | ≤20：通过 |
| 五动作精确命中 | 55/72 | 52/72 | **56/72** | 参考指标 |
| clarify 召回 | 19/21 | 20/21 | **20/21** | 报告 |
| clarify→decide | 0 | 0 | **0** | 必须为 0：通过 |
| 高危错误（17 条） | 1/17 | 1/17 | **1/17** | 不增加：通过 |
| v1 代价 | 3 | 5 | **3** | 参考切片 |
| v2 代价 | 8 | 10 | **8** | 参考切片 |
| v3 代价 | 14 | 9 | **9** | 参考切片 |
| codex+declare_default 精确命中 | 5/9 | 1/9 | **5/9** | 恢复四条命中 |

候选门槛全部满足：总代价恰为 20；`clarify→decide` 为 0；高危错误与两个基线相同，没有增加。相对 v3.1，总代价下降 5、精确命中增加 1；相对 v3.2，总代价下降 4、精确命中增加 4。

## v3.2b 五动作混淆矩阵

行是金标，列是预测动作。

| 金标 \\ 预测 | decide | clarify | codex | codex+declare_default | codex+check_first | 支持数 |
|---|---:|---:|---:|---:|---:|---:|
| decide | 10 | 1 | 7 | 0 | 0 | 18 |
| clarify | 0 | 20 | 1 | 0 | 0 | 21 |
| codex | 0 | 1 | 15 | 0 | 2 | 18 |
| codex+declare_default | 0 | 4 | 0 | 5 | 0 | 9 |
| codex+check_first | 0 | 0 | 0 | 0 | 6 | 6 |
| 预测数 | 10 | 26 | 23 | 5 | 8 | 72 |

## 显式实现闸门相关样本核验

本候选只对 `explicit_implementation_request` 增加一个条件：当 argmax 是 `clarify` 时，只有 `safe_default_for_request` 返回非空，才允许闸门改为 `codex`；随后仍由原有 `safe_default_declared` 规则生成 `codex+declare_default`。无安全默认信号时保留模型的 `clarify`。信号检测与声明默认使用同一个函数。下表是策略层核验，未调用模型。

| 样本 | 金标 | 固定 argmax | 安全默认信号 | v3.1 | v3.2 | v3.2b | 变化说明 |
|---|---|---|---|---|---|---|---|
| v1/blind-005 | codex+declare_default | clarify | 有 | codex+declare_default | clarify | **codex+declare_default** | 恢复精确命中 |
| v1/blind-017 | codex+declare_default | clarify | 有 | codex+declare_default | clarify | **codex+declare_default** | 恢复精确命中 |
| v2/blind-v2-020 | codex+declare_default | clarify | 有 | codex+declare_default | clarify | **codex+declare_default** | 恢复精确命中 |
| v2/blind-v2-021 | codex+declare_default | clarify | 有 | codex+declare_default | clarify | **codex+declare_default** | 恢复精确命中 |
| v3/blind-v3-004 | codex+declare_default | clarify | 无 | codex | clarify | clarify | 保留 clarify，不扩大触发面 |
| v3/blind-v3-010 | codex+declare_default | clarify | 无 | codex | clarify | clarify | 保留 clarify，不扩大触发面 |
| v3/blind-v3-012 | clarify | clarify | 无 | codex | clarify | **clarify** | 保留对 v3.2 的修复 |
| v3/blind-v3-017 | codex+declare_default | clarify | 无 | codex | clarify | clarify | 保留 clarify，不扩大触发面 |

这 8 条均未标记为高危；四条有默认信号的样本检测到的高危域列表为空。v3.2b 相对 v3.2 只改变前四条，故 v3.2b 与 v3.2 的高危错误数仍为 1/17。

## 边界与操作状态

- 候选文件为 `light_decider/routing_policy_v3_2b_candidate.py`，以活动 v3.1 为基底，只改显式实现闸门的 clarify 覆盖条件；其他规则、阈值和高危安全 guard 保持原样。
- `light_decider/routing_policy.py` 仍为活动 v3.1；`routing_policy_v3_2_candidate.py` 未修改。v3.2b 未激活，影子模式未改变，自动派发保持关闭。
- 没有改标签、训练模型、运行训练或生成 v4。本报告是已见开发集上的候选回归结果，不能作为泛化或上线证据。
