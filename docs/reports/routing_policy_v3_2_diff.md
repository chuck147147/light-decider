# routing_policy v3.2 候选差异说明

## 文件

- 基线：`light_decider/routing_policy.py`，版本 `v3.1`
- 候选：`light_decider/routing_policy_v3_2_candidate.py`，版本 `v3.2-candidate`
- 活动策略未替换，模型、阈值和训练数据未改。

## 唯一改动：收窄 explicit_implementation_request

**规则原则：** 当 round-2 argmax 已给出 `clarify`，实现请求措辞不再覆盖这个澄清动作；模型给出 `decide` 时，保留 v3.1 的显式实现路由。没有增加新规则。

实现上在 `intent_override_reason` 和后置实现闸门两个入口应用同一条件：跳过 `explicit_implementation_request` 对当前 `clarify` 的覆盖。

消融依据（72 条，成本为禁用−启用）：

- v3.1 加权总代价：25。
- 禁用整条规则：总代价 24，净贡献 −1；v1 子集 Δ=+2、v2 Δ=+2、v3 Δ=−5。
- 规则基线直接翻转 8 条，另有 2 条 no-op 触发；禁用后最终动作变化 8 条。
- 禁用后救回 1 条错判：`v3/blind-v3-012`，成本 5→0。它仍有未定的校规政策选项，单凭“实现”措辞不应把模型的 clarify 改为 codex。
- 禁用后损失 4 条正确默认路由：`v1/blind-005`、`v1/blind-017`、`v2/blind-v2-020`、`v2/blind-v2-021`，每条成本 0→1。另有 `v3/blind-v3-004/010/017` 动作变化但单条加权成本持平。
- 因为整条删除虽降低总成本，却会丢失前述可逆默认路由，候选只按一般原则收窄为“不覆盖 argmax clarify”。该条件在本 72 条上的回归效果与留一方向一致。

## 未改规则与安全约束

- `locale_sensitive_value_format_ambiguous` 净贡献 +9；虽误伤 `v3/blind-v3-003`，但 v1/v2 两条地区敏感输入澄清的收益更高，因此按限制不改。
- `existing_project_convention_check` 净贡献 +4；虽误伤 `v3/blind-v3-014/019`，六条正确 check_first 路由仍使整体为正，因此不改。
- 其余规则净贡献为正；保持 v3.1 原样。
- 高危域 override 到 `decide` 的安全 guard 未改；候选没有任何路径可绕过该 guard。

候选回归：72 条总成本 25→24，clarify→decide 仍为 0，高危错误 1/17→1/17；详见 `regression_v3_2_devset.md`。该集为已见开发集，结果不是泛化证据。
