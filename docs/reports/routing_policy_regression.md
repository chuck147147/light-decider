# Routing policy regression — 2026-11-04

状态：**PASS**。本报告只回放冻结的模型 argmax/分句 argmax，再运行策略层；未训练或修改模型参数。冻结金标仅用于策略验收，文件 SHA-256 已核对。自动派发保持关闭。

- 样本：24 条；冻结金标一致：23/23（不计已知分歧 `blind-015`）。
- argmax 与最终动作不一致：12 条。
- 高危域覆盖：8/8 个预期样本。

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

## 检查失败项

- 无。

冻结金标 SHA-256：`f5b572f313921a14ff7820ea8188af7a7366226ba6a5a7ad83153fae666c0b12`。
