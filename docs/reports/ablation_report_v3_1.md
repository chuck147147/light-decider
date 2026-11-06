# routing_policy v3.1 逐规则留一消融审计

## 口径、数据和限制

- 合并集：v1/v2/v3 冻结集各 24 条，共 72 条；三套题现均视为已见开发数据。全部冻结标签只读，全部 72 条计入，v1 blind-015 也按其原冻结标签保留。
- 统一固定模型：`decisioner_round2_v1_2026-11-04.joblib`；模型 SHA-256：`f2e1dc659d1d9a78c3136401ba2d987e80bd836a85005530bf75e53510d2dc25`。每条模型只推理一次，LOO 各次只重放策略并复用缓存 argmax。
- v3.1 策略 SHA-256：`719f88ed53635d8b69f35e52e00741b9d9b81128d7f72d99f176ddfe9902e86e`；基线 B 为同一模型 argmax + 当前 v3.1 `apply_routing_policy`。未启用自动派发。
- v1 当时的存档预测/策略输出也已读取并纳入来源核对；它来自 2026-11-03 semantic draft，与本单固定模型不同，所以只作历史附注，不混入统一的 72 条主口径。v1 历史预测文件 SHA-256：`589b1d244916e1710d75aac986aecc107b90d95c9398571033a41d8746757fae`。
- 历史分数版本不同：v2 当时报告使用旧 v3 策略；v3 报告使用当前 v3.1。此处用固定 round-2 模型和 v3.1 重放所有三套题。
- 高危域来源：v1 的 8 条来自 Codex blind reference（代理标签、非用户确认）；v2 的 4 条来自用户冻结域标签；v3 的 5 条来自冻结标签。全体高危错误数因此需按这项来源限制解读。用户冻结的 v2+v3 高危切片为 9 条。
- 权重：完全命中 0；gold clarify→decide 10；gold clarify→任一 codex* 5；其余五动作不匹配 1。净贡献 = 禁用规则后总成本 − v3.1 启用成本，正值表示规则有益，负值表示规则有害。单条 LOO 的净贡献不可相加，因为规则间存在顺序和遮蔽效应。
- 表中 direct flips 是日志里该规则 `before != after` 的样本数；no-op 是日志记录规则但当下动作未变。no-op 也纳入 LOO，因为它可能挡住后续规则。仅排除未触发的规则和用户要求保留、明确不审计的高危域禁止到 decide guard。72 条中有 14 个不同的已触发规则名。

## v3.1 基线

| 题集 | 条数 | 加权代价 | 精确命中 | Clarify 召回 | Clarify→decide | 高危错误 |
|---|---:|---:|---:|---:|---:|---:|
| v1 | 24 | 3 | 21/24 | 7/7 | 0 | 1/8 |
| v2 | 24 | 8 | 20/24 | 6/7 | 0 | 0/4 |
| v3 | 24 | 14 | 14/24 | 6/7 | 0 | 0/5 |
| 合计 | 72 | 25 | 55/72 | 19/21 | 0 | 1/17 |

按本单五动作权重对 v1 存档的 2026-11-03 semantic-draft 最终动作重算，精确命中 12/24、加权代价 46；这是历史附注，不是 round-2 基线。早先 v1 的 23/23 策略回归排除了已知分歧 blind-015 且回放了存档分句输出；本审计按要求纳入 72 条全部样本，并统一用 round-2 重算，因此这些分数不可直接比较。

## 逐规则留一结果

| 规则名 | 直接翻转数 | no-op 触发 | 禁用后动作变化 | 救对（错→对） | 误伤（对→错） | Δv1 | Δv2 | Δv3 | 净代价贡献 | 禁用后总代价 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `comparison_without_execution_request` | 3 | 2 | 3 | 0 | 3 | +2 | +1 | +0 | +3 | 28 |
| `concurrent_edit_conflict_policy_missing` | 0 | 1 | 1 | 0 | 1 | +5 | +0 | +0 | +5 | 30 |
| `contract_history_access_or_retention_policy_missing` | 0 | 1 | 1 | 0 | 1 | +5 | +0 | +0 | +5 | 30 |
| `existing_project_convention_check` | 8 | 0 | 8 | 2 | 6 | +2 | +2 | +0 | +4 | 29 |
| `explicit_explanation_request` | 1 | 1 | 1 | 0 | 1 | +1 | +0 | +0 | +1 | 26 |
| `explicit_implementation_request` | 8 | 2 | 8 | 1 | 4 | +2 | +2 | -5 | -1 | 24 |
| `explicit_key_choice_question` | 1 | 3 | 4 | 0 | 3 | +0 | +10 | +5 | +15 | 40 |
| `external_auditor_scope_mapping_missing` | 0 | 1 | 1 | 0 | 1 | +5 | +0 | +0 | +5 | 30 |
| `locale_sensitive_value_format_ambiguous` | 2 | 1 | 3 | 1 | 2 | +5 | +5 | -1 | +9 | 34 |
| `payment_account_change_controls_missing` | 0 | 1 | 1 | 0 | 1 | +5 | +0 | +0 | +5 | 30 |
| `rate_limit_threshold_or_window_missing` | 0 | 2 | 1 | 0 | 1 | +5 | +0 | +0 | +5 | 30 |
| `reminder_cadence_missing` | 0 | 1 | 1 | 0 | 1 | +5 | +0 | +0 | +5 | 30 |
| `safe_default_declared` | 5 | 0 | 5 | 0 | 5 | +2 | +3 | +0 | +5 | 30 |
| `unresolved_policy_parameter_before_implementation` | 0 | 4 | 4 | 0 | 4 | +0 | +5 | +15 | +20 | 45 |

### 符号说明

- `Δv1/v2/v3` 和净贡献均为禁用成本减启用成本；正数表示保留规则更省错分代价，负数表示禁用规则后成本下降。
- 救对数为 v3.1 当前输出错误、禁用后变正确；误伤数为当前正确、禁用后变错。其他输出动作变化仍列在逐条影响中，避免只看准确率遗漏加权代价变化。
- 本报告把绝对净贡献 ≤ 1 个代价点作为“接近零”的操作性边界。`explicit_explanation_request` 为 +1，但其唯一直接翻转正确、未发现误伤，因此不收窄；其余净贡献为正的规则保持原样。

## 每条动作变化及误伤样本归类

### `comparison_without_execution_request`

直接翻转样本：v1/blind-013, v1/blind-021, v2/blind-v2-002。no-op 触发样本：v1/blind-007, v1/blind-018。禁用后改变的样本：3 条。

| 样本 | 冻结动作 | v3.1 启用 | 禁用后 | 单条代价启用→禁用 | 归类与原因 |
|---|---|---|---|---:|---|
| `v1/blind-013` | `decide` | `decide` | `codex` | 0→1 | 禁用误伤，规则原本有效：这是知识比较/建议题；该规则把分类结果校正为 decide。 |
| `v1/blind-021` | `decide` | `decide` | `clarify` | 0→1 | 禁用误伤，规则原本有效：这是知识比较/建议题；该规则把分类结果校正为 decide。 |
| `v2/blind-v2-002` | `decide` | `decide` | `codex` | 0→1 | 禁用误伤，规则原本有效：这是知识比较/建议题；该规则把分类结果校正为 decide。 |

### `concurrent_edit_conflict_policy_missing`

直接翻转样本：无。no-op 触发样本：v1/blind-019。禁用后改变的样本：1 条。

| 样本 | 冻结动作 | v3.1 启用 | 禁用后 | 单条代价启用→禁用 | 归类与原因 |
|---|---|---|---|---:|---|
| `v1/blind-019` | `clarify` | `clarify` | `codex` | 0→5 | 禁用误伤，规则原本有效：启用规则后的预测正确；禁用后动作偏离冻结标签。 |

### `contract_history_access_or_retention_policy_missing`

直接翻转样本：无。no-op 触发样本：v1/blind-023。禁用后改变的样本：1 条。

| 样本 | 冻结动作 | v3.1 启用 | 禁用后 | 单条代价启用→禁用 | 归类与原因 |
|---|---|---|---|---:|---|
| `v1/blind-023` | `clarify` | `clarify` | `codex` | 0→5 | 禁用误伤，规则原本有效：启用规则后的预测正确；禁用后动作偏离冻结标签。 |

### `existing_project_convention_check`

直接翻转样本：v1/blind-014, v1/blind-020, v2/blind-v2-023, v2/blind-v2-024, v3/blind-v3-005, v3/blind-v3-014, v3/blind-v3-016, v3/blind-v3-019。no-op 触发样本：无。禁用后改变的样本：8 条。

| 样本 | 冻结动作 | v3.1 启用 | 禁用后 | 单条代价启用→禁用 | 归类与原因 |
|---|---|---|---|---:|---|
| `v1/blind-014` | `codex+check_first` | `codex+check_first` | `codex` | 0→1 | 禁用误伤，规则原本有效：用户明确要求沿用或检查仓库现有约定；关掉规则会丢失 gold check_first 路由。 |
| `v1/blind-020` | `codex+check_first` | `codex+check_first` | `codex` | 0→1 | 禁用误伤，规则原本有效：用户明确要求沿用或检查仓库现有约定；关掉规则会丢失 gold check_first 路由。 |
| `v2/blind-v2-023` | `codex+check_first` | `codex+check_first` | `codex` | 0→1 | 禁用误伤，规则原本有效：用户明确要求沿用或检查仓库现有约定；关掉规则会丢失 gold check_first 路由。 |
| `v2/blind-v2-024` | `codex+check_first` | `codex+check_first` | `codex` | 0→1 | 禁用误伤，规则原本有效：用户明确要求沿用或检查仓库现有约定；关掉规则会丢失 gold check_first 路由。 |
| `v3/blind-v3-005` | `codex+check_first` | `codex+check_first` | `codex` | 0→1 | 禁用误伤，规则原本有效：用户明确要求沿用或检查仓库现有约定；关掉规则会丢失 gold check_first 路由。 |
| `v3/blind-v3-014` | `codex` | `codex+check_first` | `codex` | 1→0 | 规则误触发，禁用救对：请求已把行为/数值写全；仅因‘现有项目’线索升为 check_first，过度要求查约定。 |
| `v3/blind-v3-016` | `codex+check_first` | `codex+check_first` | `codex` | 0→1 | 禁用误伤，规则原本有效：用户明确要求沿用或检查仓库现有约定；关掉规则会丢失 gold check_first 路由。 |
| `v3/blind-v3-019` | `codex` | `codex+check_first` | `codex` | 1→0 | 规则误触发，禁用救对：请求已把行为/数值写全；仅因‘现有项目’线索升为 check_first，过度要求查约定。 |

### `explicit_explanation_request`

直接翻转样本：v1/blind-001。no-op 触发样本：v3/blind-v3-024。禁用后改变的样本：1 条。

| 样本 | 冻结动作 | v3.1 启用 | 禁用后 | 单条代价启用→禁用 | 归类与原因 |
|---|---|---|---|---:|---|
| `v1/blind-001` | `decide` | `decide` | `codex` | 0→1 | 禁用误伤，规则原本有效：启用规则后的预测正确；禁用后动作偏离冻结标签。 |

### `explicit_implementation_request`

直接翻转样本：v1/blind-005, v1/blind-017, v2/blind-v2-020, v2/blind-v2-021, v3/blind-v3-004, v3/blind-v3-010, v3/blind-v3-012, v3/blind-v3-017。no-op 触发样本：v1/blind-008, v2/blind-v2-022。禁用后改变的样本：8 条。

| 样本 | 冻结动作 | v3.1 启用 | 禁用后 | 单条代价启用→禁用 | 归类与原因 |
|---|---|---|---|---:|---|
| `v1/blind-005` | `codex+declare_default` | `codex+declare_default` | `clarify` | 0→1 | 禁用误伤，规则原本有效：这是可逆默认请求；实现闸门先把模型 clarify 提升到 codex，后续安全默认规则才能产出 gold declare_default。 |
| `v1/blind-017` | `codex+declare_default` | `codex+declare_default` | `clarify` | 0→1 | 禁用误伤，规则原本有效：这是可逆默认请求；实现闸门先把模型 clarify 提升到 codex，后续安全默认规则才能产出 gold declare_default。 |
| `v2/blind-v2-020` | `codex+declare_default` | `codex+declare_default` | `clarify` | 0→1 | 禁用误伤，规则原本有效：这是可逆默认请求；实现闸门先把模型 clarify 提升到 codex，后续安全默认规则才能产出 gold declare_default。 |
| `v2/blind-v2-021` | `codex+declare_default` | `codex+declare_default` | `clarify` | 0→1 | 禁用误伤，规则原本有效：这是可逆默认请求；实现闸门先把模型 clarify 提升到 codex，后续安全默认规则才能产出 gold declare_default。 |
| `v3/blind-v3-004` | `codex+declare_default` | `codex` | `clarify` | 1→1 | 动作变化但成本持平：动作变化但两边均计 1：新授权措辞未被 safe_default 识别，codex 与 clarify 都没命中 declare_default。 |
| `v3/blind-v3-010` | `codex+declare_default` | `codex` | `clarify` | 1→1 | 动作变化但成本持平：动作变化但两边均计 1：新授权措辞未被 safe_default 识别，codex 与 clarify 都没命中 declare_default。 |
| `v3/blind-v3-012` | `clarify` | `codex` | `clarify` | 5→0 | 规则误触发，禁用救对：规则只命中‘要求实现’，把仍含未定政策选项的请求从 clarify 覆盖成 codex。 |
| `v3/blind-v3-017` | `codex+declare_default` | `codex` | `clarify` | 1→1 | 动作变化但成本持平：动作变化但两边均计 1：新授权措辞未被 safe_default 识别，codex 与 clarify 都没命中 declare_default。 |

### `explicit_key_choice_question`

直接翻转样本：v3/blind-v3-018。no-op 触发样本：v1/blind-015, v2/blind-v2-013, v2/blind-v2-019。禁用后改变的样本：4 条。

| 样本 | 冻结动作 | v3.1 启用 | 禁用后 | 单条代价启用→禁用 | 归类与原因 |
|---|---|---|---|---:|---|
| `v1/blind-015` | `codex+declare_default` | `clarify` | `codex` | 1→1 | 动作变化但成本持平：v1 blind-015 是已知金标分歧；开关改变了动作但加权代价同为 1，原冻结标签未修改。 |
| `v2/blind-v2-013` | `clarify` | `clarify` | `codex` | 0→5 | 禁用误伤，规则原本有效：候选选项直接影响业务语义；保留问句澄清避免实现闸门把未决选择送去执行。 |
| `v2/blind-v2-019` | `clarify` | `clarify` | `codex` | 0→5 | 禁用误伤，规则原本有效：候选选项直接影响业务语义；保留问句澄清避免实现闸门把未决选择送去执行。 |
| `v3/blind-v3-018` | `clarify` | `clarify` | `codex` | 0→5 | 禁用误伤，规则原本有效：候选选项直接影响业务语义；保留问句澄清避免实现闸门把未决选择送去执行。 |

### `external_auditor_scope_mapping_missing`

直接翻转样本：无。no-op 触发样本：v1/blind-016。禁用后改变的样本：1 条。

| 样本 | 冻结动作 | v3.1 启用 | 禁用后 | 单条代价启用→禁用 | 归类与原因 |
|---|---|---|---|---:|---|
| `v1/blind-016` | `clarify` | `clarify` | `codex` | 0→5 | 禁用误伤，规则原本有效：启用规则后的预测正确；禁用后动作偏离冻结标签。 |

### `locale_sensitive_value_format_ambiguous`

直接翻转样本：v1/blind-012, v3/blind-v3-003。no-op 触发样本：v2/blind-v2-016。禁用后改变的样本：3 条。

| 样本 | 冻结动作 | v3.1 启用 | 禁用后 | 单条代价启用→禁用 | 归类与原因 |
|---|---|---|---|---:|---|
| `v1/blind-012` | `clarify` | `clarify` | `codex` | 0→5 | 禁用误伤，规则原本有效：请求输入了地区格式有歧义的日期/数值并要求选择解析政策；clarify 是金标。 |
| `v2/blind-v2-016` | `clarify` | `clarify` | `codex` | 0→5 | 禁用误伤，规则原本有效：请求输入了地区格式有歧义的日期/数值并要求选择解析政策；clarify 是金标。 |
| `v3/blind-v3-003` | `codex` | `clarify` | `codex` | 1→0 | 规则误触发，禁用救对：数字是明示常量且精度、舍入和错误处理均已定义；不是需要选择地区解释的输入格式。 |

### `payment_account_change_controls_missing`

直接翻转样本：无。no-op 触发样本：v1/blind-003。禁用后改变的样本：1 条。

| 样本 | 冻结动作 | v3.1 启用 | 禁用后 | 单条代价启用→禁用 | 归类与原因 |
|---|---|---|---|---:|---|
| `v1/blind-003` | `clarify` | `clarify` | `codex` | 0→5 | 禁用误伤，规则原本有效：启用规则后的预测正确；禁用后动作偏离冻结标签。 |

### `rate_limit_threshold_or_window_missing`

直接翻转样本：无。no-op 触发样本：v1/blind-010, v2/blind-v2-015。禁用后改变的样本：1 条。

| 样本 | 冻结动作 | v3.1 启用 | 禁用后 | 单条代价启用→禁用 | 归类与原因 |
|---|---|---|---|---:|---|
| `v1/blind-010` | `clarify` | `clarify` | `codex` | 0→5 | 禁用误伤，规则原本有效：启用规则后的预测正确；禁用后动作偏离冻结标签。 |

### `reminder_cadence_missing`

直接翻转样本：无。no-op 触发样本：v1/blind-006。禁用后改变的样本：1 条。

| 样本 | 冻结动作 | v3.1 启用 | 禁用后 | 单条代价启用→禁用 | 归类与原因 |
|---|---|---|---|---:|---|
| `v1/blind-006` | `clarify` | `clarify` | `codex` | 0→5 | 禁用误伤，规则原本有效：启用规则后的预测正确；禁用后动作偏离冻结标签。 |

### `safe_default_declared`

直接翻转样本：v1/blind-005, v1/blind-017, v2/blind-v2-020, v2/blind-v2-021, v2/blind-v2-022。no-op 触发样本：无。禁用后改变的样本：5 条。

| 样本 | 冻结动作 | v3.1 启用 | 禁用后 | 单条代价启用→禁用 | 归类与原因 |
|---|---|---|---|---:|---|
| `v1/blind-005` | `codex+declare_default` | `codex+declare_default` | `codex` | 0→1 | 禁用误伤，规则原本有效：五动作计分要求输出 declare_default；禁用后退回普通 codex，与冻结动作不一致。 |
| `v1/blind-017` | `codex+declare_default` | `codex+declare_default` | `codex` | 0→1 | 禁用误伤，规则原本有效：五动作计分要求输出 declare_default；禁用后退回普通 codex，与冻结动作不一致。 |
| `v2/blind-v2-020` | `codex+declare_default` | `codex+declare_default` | `codex` | 0→1 | 禁用误伤，规则原本有效：五动作计分要求输出 declare_default；禁用后退回普通 codex，与冻结动作不一致。 |
| `v2/blind-v2-021` | `codex+declare_default` | `codex+declare_default` | `codex` | 0→1 | 禁用误伤，规则原本有效：五动作计分要求输出 declare_default；禁用后退回普通 codex，与冻结动作不一致。 |
| `v2/blind-v2-022` | `codex+declare_default` | `codex+declare_default` | `codex` | 0→1 | 禁用误伤，规则原本有效：五动作计分要求输出 declare_default；禁用后退回普通 codex，与冻结动作不一致。 |

### `unresolved_policy_parameter_before_implementation`

直接翻转样本：无。no-op 触发样本：v2/blind-v2-018, v3/blind-v3-002, v3/blind-v3-009, v3/blind-v3-015。禁用后改变的样本：4 条。

| 样本 | 冻结动作 | v3.1 启用 | 禁用后 | 单条代价启用→禁用 | 归类与原因 |
|---|---|---|---|---:|---|
| `v2/blind-v2-018` | `clarify` | `clarify` | `codex` | 0→5 | 禁用误伤，规则原本有效：缺失的关键行为/政策参数被保护在 clarify；禁用后下游实现闸门会推成 codex。 |
| `v3/blind-v3-002` | `clarify` | `clarify` | `codex` | 0→5 | 禁用误伤，规则原本有效：缺失的关键行为/政策参数被保护在 clarify；禁用后下游实现闸门会推成 codex。 |
| `v3/blind-v3-009` | `clarify` | `clarify` | `codex` | 0→5 | 禁用误伤，规则原本有效：缺失的关键行为/政策参数被保护在 clarify；禁用后下游实现闸门会推成 codex。 |
| `v3/blind-v3-015` | `clarify` | `clarify` | `codex` | 0→5 | 禁用误伤，规则原本有效：缺失的关键行为/政策参数被保护在 clarify；禁用后下游实现闸门会推成 codex。 |

## 候选筛选结论

- 明确负贡献：`explicit_implementation_request`，净贡献 −1（v1 +2、v2 +2、v3 −5），直接翻转 8 条，no-op 触发 2 条。禁用后救回 1 条 `v3/blind-v3-012`，禁用损失 4 条正确默认路由（v1-005/017、v2-020/021）；另有 v3-004/010/017 动作变化但单条代价持平。该规则适合收窄到“不覆盖模型已判为 clarify 的请求”。
- `locale_sensitive_value_format_ambiguous` 净贡献 +9（v1 +5、v2 +5、v3 −1）。v3 `blind-v3-003` 确实是格式规则误伤，但 v1 `blind-012` 和 v2 `blind-v2-016` 两条地区输入歧义的澄清价值更高；整体为正，按限定范围保持原样。
- `existing_project_convention_check` 净贡献 +4（v1 +2、v2 +2、v3 0）。v3 `blind-v3-014/019` 是明确过触发，但 v1/v2/v3 其他六条 check_first 路由贡献更高；整体为正，不按局部错题改规则。
- `explicit_explanation_request` 净贡献 +1，正贡献的边界值；其变化样本 `v1/blind-001` 是正确解释路由，没有发现误触发，故保留。其余规则净贡献均为正，保持原文不动。
- 高危域 `override → decide` 安全 guard 没有纳入消融，不修改；未触发的规则没有样本证据，报告为未触发，不臆造贡献。

## 输入哈希

- `data\frozen_2026-11-03\light_decider_independent_blind_holdout_v1_human_labels_frozen_2026-11-03.jsonl`: `f5b572f313921a14ff7820ea8188af7a7366226ba6a5a7ad83153fae666c0b12`
- `data\light_decider_independent_blind_holdout_v1_current_model_predictions_2026-11-03.jsonl`: `589b1d244916e1710d75aac986aecc107b90d95c9398571033a41d8746757fae`
- `data\light_decider_independent_blind_holdout_v1_codex_blind_reference.jsonl`: `7b26b13811814e325fe34d1c52bb54a944f406b275e54710aed3522d91f24819`
- `data\light_decider_independent_blind_holdout_v2_2026-11-04\blind_holdout_v2_user_labels_frozen_2026-11-04.xlsx`: `5f0cc3bacb9d84c34cf5ef7317034552d6c04915321603e9156af523f7f20b4f`
- `data\light_decider_independent_blind_holdout_v2_2026-11-04\blind_holdout_v2_unlabeled.xlsx`: `64540d63b22aa9a1c833e2fcd51231dc0b972e287db2d5fb14243baa7e6d6729`
- `data\light_decider_independent_blind_holdout_v2_2026-11-04\evaluation_report_v2.md`: `04a2f6c3023df74fe63a02f72ac9405cf3a5ca33bbb2d1fba02d84c721517518`
- `data\light_decider_independent_blind_holdout_v3_2026-11-04\blind_holdout_v3_labels_frozen.jsonl`: `1b28daf61866153cda78fb6f7060ed084659f73b7ef1efd128e5f53dd0d1e07b`
- `data\light_decider_independent_blind_holdout_v3_2026-11-04\evaluation_report_v3.md`: `0fbce715ab816d4d93a547be8748d52f7e6923aafe67b2be016af63f8ccacc97`
- `artifacts\decisioner_round2_v1_2026-11-04.joblib`: `f2e1dc659d1d9a78c3136401ba2d987e80bd836a85005530bf75e53510d2dc25`
- `light_decider\routing_policy.py`: `719f88ed53635d8b69f35e52e00741b9d9b81128d7f72d99f176ddfe9902e86e`

本报告是三套已见开发集的规则审计，不构成泛化证据。
