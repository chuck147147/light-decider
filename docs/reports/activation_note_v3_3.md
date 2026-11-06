# light_decider routing_policy v3.3 激活记录

## 决策与切换

- 决策人：用户。批准日期：2026-11-06。
- 切换时间：2026-11-06 11:16:14 CST (Asia/Shanghai)。
- 依据：v6 冻结标签 SHA-256 `9a687a497f0485010ad5a1de538e485c165c4cee3780190d55ee7e2d3e304f6f` 的预注册评测。round-4 + v3.3 代价 4，低于 round-4 + v3.1 的 14；clarify 召回 7/7（v3.1 为 5/7）；clarify→decide 为 0。
- 生效策略：`light_decider/routing_policy.py`，版本标识 `v3.3`，SHA-256 `0e6d6493c01ad16f56574e4311bd2feb95d6f9872517b9037dc5506caaadabc0`。其决策逻辑取自 `routing_policy_v3_3_candidate.py`（源文件 SHA-256 `d8200283b628645816c24f67d086971837ba82cc03bea6170cd32930307a92c1`）；活动文件只把元数据标识从 `v3.3-candidate` 改为 `v3.3`，使影子日志记录正式生效版本。
- round-4 模型保持不变：`artifacts/decisioner_round4_v1_2026-11-05.joblib`，SHA-256 `6eff1a818db972bf887ed885f1cad4162dc5cef69ebdee0fb4f7ac32c37b286b`。
- v3.2b 候选未改、未激活。自动派发保持关闭。

## v3.1 回退文件

v3.1 原文件已逐字节归档到 `light_decider/routing_policy_v3_1.py`，SHA-256 为 `719f88ed53635d8b69f35e52e00741b9d9b81128d7f72d99f176ddfe9902e86e`。回退路径：将该归档文件复制回 `light_decider/routing_policy.py`。活动切换没有覆盖或删除归档。

## 影子模式

影子观察器 `light_decider/shadow.py` 从 `light_decider.routing_policy` 导入 `POLICY_VERSION`，并经 `predict.suggest_route` 调用同一活动策略；因此策略引用随活动模块切换为 v3.3，无独立 sidecar 策略指针需要改写。影子模式仍只记录日志，`automatic_dispatch_allowed` 保持 false；分数阈值和其余行为未改。

## 冒烟校验

使用默认 round-4 模型配置，在冻结 v6 标签集上完成一次冒烟复跑。冻结文件未写入。
- 状态：通过：与 v6 B 口径一致。
- 加权代价：4（期望 4）。
- Clarify 召回：7/7（期望 7/7）。
- Clarify→decide：0（期望 0）。
- 样本数：24；错误数：4.
- blind-v6-003：金标 `clarify`，模型 argmax `clarify`，最终动作 `clarify`。
- 冒烟错误清单：`[{"sample_id":"blind-v6-001","gold":"codex+declare_default","argmax":"clarify","action":"clarify","reason":"highest_model_score","cost":1},{"sample_id":"blind-v6-005","gold":"codex+declare_default","argmax":"clarify","action":"clarify","reason":"highest_model_score","cost":1},{"sample_id":"blind-v6-006","gold":"codex","argmax":"codex","action":"clarify","reason":"locale_sensitive_value_format_ambiguous","cost":1},{"sample_id":"blind-v6-024","gold":"codex+declare_default","argmax":"clarify","action":"clarify","reason":"highest_model_score","cost":1}]`。
- 冻结标签 SHA-256 复核：`9a687a497f0485010ad5a1de538e485c165c4cee3780190d55ee7e2d3e304f6f`。

本次只执行获批的策略切换与一次冒烟校验；没有训练模型、修改标签或启用自动派发。
