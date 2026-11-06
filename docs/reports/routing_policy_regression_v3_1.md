# Routing policy v3.1 regression — 2026-11-04

状态：**PASS**。v1 部分只回放冻结的模型 argmax/分句 argmax，再运行策略层；未训练或修改模型参数。冻结金标仅用于策略验收，文件 SHA-256 已核对。自动派发保持关闭。

- 样本：24 条；冻结金标一致：23/23（不计已知分歧 `blind-015`）。
- argmax 与最终动作不一致：12 条。
- 高危域覆盖：8/8 个预期样本。
- 模型未改动；第二轮模型 SHA-256：`f2e1dc659d1d9a78c3136401ba2d987e80bd836a85005530bf75e53510d2dc25`。策略 v3.1 SHA-256：`719f88ed53635d8b69f35e52e00741b9d9b81128d7f72d99f176ddfe9902e86e`。

## 本轮原则改动

- 先执行高危域与缺少关键行为参数检查，再检查已有项目约定，最后才应用实现意图覆盖。通用缺项判据识别明确未定项或同一实现请求中的多个开放参数问题；blind-v2-018 仅作为动机样本，规则未使用其业务场景词面。
- 显式实现判定覆盖“从零/从头 + 通用建设动词”句式。加入“由你按常见习惯/惯例选择”“由你决定”等显式授权线索；只有可逆、低风险且能给出具体默认值的受支持细节会转为 `codex+declare_default`，handoff 写出具体默认及理由。
- 高危域无条件跳过安全默认声明；即使出现授权措辞，未定的高危策略参数仍由缺项规则导向 `clarify`。自动派发关闭，模型未重训。

## 动作翻转清单

- `blind-003`: `codex` → `clarify`
- `blind-005`: `codex` → `codex+declare_default`
- `blind-006`: `codex` → `clarify`
- `blind-010`: `decide` → `clarify`
- `blind-012`: `codex` → `clarify`
- `blind-014`: `codex` → `codex+check_first`
- `blind-015`: `codex` → `clarify`
- `blind-016`: `decide` → `clarify`
- `blind-017`: `codex` → `codex+declare_default`
- `blind-019`: `codex` → `clarify`
- `blind-020`: `codex` → `codex+check_first`
- `blind-023`: `decide` → `clarify`

## 24 条结果

| ID | argmax | 最终动作 | 冻结金标 | 高危域 | 主要 override |
|---|---|---|---|---|---|
| blind-001 | `decide` | `decide` | `decide` | — | explicit_explanation_request |
| blind-002 | `codex` | `codex` | `codex` | — | — |
| blind-003 | `codex` | `clarify` | `clarify` | payment, permission | payment_account_change_controls_missing |
| blind-004 | `decide` | `decide` | `decide` | payment | comparison_without_execution_request |
| blind-005 | `codex` | `codex+declare_default` | `codex+declare_default` | — | safe_default_declared |
| blind-006 | `codex` | `clarify` | `clarify` | — | reminder_cadence_missing |
| blind-007 | `decide` | `decide` | `decide` | — | comparison_without_execution_request |
| blind-008 | `codex` | `codex` | `codex` | permission | explicit_implementation_request |
| blind-009 | `decide` | `decide` | `decide` | permission | comparison_without_execution_request |
| blind-010 | `decide` | `clarify` | `clarify` | rate_limiting | rate_limit_threshold_or_window_missing |
| blind-011 | `codex` | `codex` | `codex` | — | — |
| blind-012 | `codex` | `clarify` | `clarify` | locale_sensitive_parsing | locale_sensitive_value_format_ambiguous |
| blind-013 | `decide` | `decide` | `decide` | — | comparison_without_execution_request |
| blind-014 | `codex` | `codex+check_first` | `codex+check_first` | — | existing_project_convention_check |
| blind-015 | `codex` | `clarify` | `codex+declare_default` | — | explicit_key_choice_question |
| blind-016 | `decide` | `clarify` | `clarify` | permission | external_auditor_scope_mapping_missing |
| blind-017 | `codex` | `codex+declare_default` | `codex+declare_default` | — | safe_default_declared |
| blind-018 | `decide` | `decide` | `decide` | — | comparison_without_execution_request |
| blind-019 | `codex` | `clarify` | `clarify` | — | concurrent_edit_conflict_policy_missing |
| blind-020 | `codex` | `codex+check_first` | `codex+check_first` | — | existing_project_convention_check |
| blind-021 | `decide` | `decide` | `decide` | — | comparison_without_execution_request |
| blind-022 | `codex` | `codex` | `codex` | — | — |
| blind-023 | `decide` | `clarify` | `clarify` | permission | contract_history_access_or_retention_policy_missing |
| blind-024 | `decide` | `decide` | `decide` | — | — |

## 已知分歧

`blind-015` 冻结金标保留为 `codex+declare_default`；新判据要求用户以问句提出‘删除还是归档’，因此策略输出 `clarify`。按用户要求单列为已知分歧，不记为模型或标注错误。

## 五个高危域的 override 防护探针

- `payment`：识别为 `payment`；试图由 `codex` override 到 `decide` 被拦截，动作保留 `codex`；通过。
- `permission`：识别为 `permission`；试图由 `codex` override 到 `decide` 被拦截，动作保留 `codex`；通过。
- `locale_sensitive_parsing`：识别为 `locale_sensitive_parsing`；试图由 `codex` override 到 `decide` 被拦截，动作保留 `codex`；通过。
- `deduplication`：识别为 `deduplication`；试图由 `codex` override 到 `decide` 被拦截，动作保留 `codex`；通过。
- `rate_limiting`：识别为 `rate_limiting`；试图由 `codex` override 到 `decide` 被拦截，动作保留 `codex`；通过。

## 旧版字符 n-gram 入口集成探针

- `blind-005`：期望 `codex+declare_default`，实际 `codex+declare_default`；自动派发 `false`；通过。
- `blind-014`：期望 `codex+check_first`，实际 `codex+check_first`；自动派发 `false`；通过。

## v3.1 原则探针

- `generic_missing_parameters_precede_implementation`：期望 `clarify` / `unresolved_policy_parameter_before_implementation`，实际 `clarify` / `unresolved_policy_parameter_before_implementation`；高危域 `—`；通过。
- `explicit_authority_names_reversible_default`：期望 `codex+declare_default` / `safe_default_declared`，实际 `codex+declare_default` / `safe_default_declared`；高危域 `—`；通过。
- `high_risk_authority_does_not_bypass_missing_policy`：期望 `clarify` / `unresolved_policy_parameter_before_implementation`，实际 `clarify` / `unresolved_policy_parameter_before_implementation`；高危域 `payment`；通过。

## v2 已见集合参考分（非泛化证据）

本节只是在已见 v2 题目上回放第二轮模型与 v3.1 策略，用作已见集合参考；它不是独立泛化证据，也未用于调整模型、标签或规则。共 24 条；clarify 召回 6/7；clarify→decide 0；加权总代价 8；高危域错误 0；argmax→最终动作翻转 6 条。

| 金标 \ 预测 | `decide` | `clarify` | `codex` | `codex+declare_default` | `codex+check_first` |
|---|---:|---:|---:|---:|---:|
| `decide` | 1 | 0 | 3 | 0 | 0 |
| `clarify` | 0 | 6 | 1 | 0 | 0 |
| `codex` | 0 | 0 | 8 | 0 | 0 |
| `codex+declare_default` | 0 | 0 | 0 | 3 | 0 |
| `codex+check_first` | 0 | 0 | 0 | 0 | 2 |

### v2 每类 Precision / Recall

| 类别 | Precision | Recall | 支持数 |
|---|---:|---:|---:|
| `decide` | 1.000 | 0.250 | 4 |
| `clarify` | 1.000 | 0.857 | 7 |
| `codex` | 0.667 | 1.000 | 8 |
| `codex+declare_default` | 1.000 | 1.000 | 3 |
| `codex+check_first` | 1.000 | 1.000 | 2 |

### v2 高危域错误

- 无高危域错误。

### v2 策略翻转（已见集合）

- `blind-v2-002`：`codex` → `decide`（comparison_without_execution_request）
- `blind-v2-020`：`clarify` → `codex+declare_default`（explicit_implementation_request, safe_default_declared）
- `blind-v2-021`：`clarify` → `codex+declare_default`（explicit_implementation_request, safe_default_declared）
- `blind-v2-022`：`codex` → `codex+declare_default`（explicit_implementation_request, safe_default_declared）
- `blind-v2-023`：`clarify` → `codex+check_first`（existing_project_convention_check）
- `blind-v2-024`：`codex` → `codex+check_first`（existing_project_convention_check）

## 检查失败项

- 无。

v1 冻结金标 SHA-256：`f5b572f313921a14ff7820ea8188af7a7366226ba6a5a7ad83153fae666c0b12`。v2 冻结标签 SHA-256：`5f0cc3bacb9d84c34cf5ef7317034552d6c04915321603e9156af523f7f20b4f`；v2 输入快照 SHA-256：`830cf52895284e37ca18b720a5a22ff0acb368973aa0e81ddc84652b775aaf76`。v2 是已见集合参考分，不是泛化证据。
