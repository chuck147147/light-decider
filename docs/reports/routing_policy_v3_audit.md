# routing_policy v3 实施审计

日期：2026-11-04（Asia/Shanghai）  
范围：策略层、handoff 格式、策略回归；不重训或改动模型参数。

## 改动依据与实现

| 改动 | 实现结果 | 对照样本 / 依据 |
|---|---|---|
| 四类 Codex 动作 | 策略层输出 `codex`、`codex+declare_default`、`codex+check_first`、`clarify`；模型仍保留 `decide / clarify / codex` 三类原始 argmax。 | `blind-005`、`blind-017`（声明默认）；`blind-014`、`blind-020`（先查现有约定）；`blind-003`、`blind-006`、`blind-010`、`blind-012`、`blind-016`、`blind-019`、`blind-023`（需澄清）。 |
| 默认 handoff | `codex+declare_default` 交接具体默认和理由，并要求先排查直接冲突；发现冲突时转 `codex+check_first` 核对，查不到一致方案或冲突无法兼容再追问。 | `blind-005`、`blind-017`。 |
| check-first handoff | `codex+check_first` 交接列出要检查的实现、配置、文档/API 约定和测试；查不到一致规则或有冲突时停止并追问。 | `blind-014`、`blind-020`。 |
| 关键选择问句优先澄清 | 实现请求中明确问“选哪个”或用“还是/或者”提出关键选择时路由 `clarify`，即使存在可逆默认。 | `blind-015`。其冻结标签继续保留 `codex+declare_default`，在回归中作为用户指定的已知分歧单列。 |
| 排除汇报要求误判 | 先从解释意图检测文本中去除“交接里告诉我/写明最终采用内容”等汇报要求。 | `blind-005`。 |
| 排除自足概念问句的指代误判 | 分句策略把完整请求传入 referent 判定；自足的命名概念问句不因后句“它”触发缺失指代。 | `blind-018`。 |
| 纯比较不触发实现选择规则 | 比较/知识问句不能仅因句中“更新”等比较维度词被误识别成执行任务。 | `blind-021`（关系型数据库 vs 文档数据库）。 |
| 实现请求门控与分句聚合 | 用显式动词/目标识别实现任务，不再靠 `codex` argmax 反推请求是实现任务；覆盖嵌在复合句中的新增操作，并在分句时传递原始完整请求。 | `blind-002`、`blind-010`、`blind-011`、`blind-019`、`blind-021`、`blind-022`。其中 `blind-010` 证明“给组织加发送限制”嵌在句中仍是实现请求；`blind-021` 是“更新”只作为比较维度的反例。 |
| 关键缺项拦截 | 对账户换绑控制、重复提醒频率、限流阈值/窗口、地区格式、外部审计范围、并发合并策略和合同历史访问/保留期限缺项时转 `clarify`。 | `blind-003`、`blind-006`、`blind-010`、`blind-012`、`blind-016`、`blind-019`、`blind-023`。 |
| 收窄“旧版”项目线索 | 只将旧版流程/系统/API/服务当作项目现状线索；合同数据里的旧版本不能触发 `check_first`，以免把业务政策不明误当作可查项目约定。 | `blind-014`、`blind-020` 是 check-first 正例；`blind-023` 是旧合同版本的反例，仍走 `clarify`。 |
| 高危域识别与 guard | 标签覆盖支付、权限、地区敏感解析、去重和限流；任何策略 override 不得把高危输入改向 `decide`，触发项写入 `before / after / rule_name / applied` 日志，含被拦截提议。权限识别把“财务人员提交账户变更”计为权限相关，并避免仅凭“管理员知道”把提醒请求标成权限域。 | 冻结样本：`blind-003`、`blind-004`、`blind-008`、`blind-009`、`blind-010`、`blind-012`、`blind-016`、`blind-023`。去重域另用独立防护探针验证，不伪称本批金标覆盖。 |
| 多分句统一聚合 | 全请求与各分句共用策略，动作按 `clarify > codex+check_first > codex+declare_default > codex > decide` 汇总，聚合变化本身留日志。 | `blind-001`、`blind-003`、`blind-019` 等多分句样本；动作翻转完整记录在回归报告。 |
| 旧版字符 n-gram 入口共用策略 | `light_decider.predict.suggest_route` 也调用同一策略和 handoff 函数，避免两种入口对同一类请求给出不同动作。 | 用 `blind-005`、`blind-014` 的缓存 argmax 做入口 smoke check，确认分别生成 `codex+declare_default` 和 `codex+check_first`，且自动派发为 `false`。 |

## 冻结金标回归

命令：`python scripts/run_frozen_gold_policy_regression.py`。回归从冻结的后冻结模型 argmax/分句结果回放策略，不重新推理模型，不训练或调参。该脚本读取冻结标签仅用于验收，先核对冻结文件哈希；自动派发字段必须保持 `false`。

结果文件：

- `data/policy_regression_runs/routing_policy_regression_2026-11-04.md`
- `data/policy_regression_runs/routing_policy_regression_2026-11-04.json`

通过条件为：除 `blind-015` 已知分歧外，其余 23 条最终动作符合冻结金标；五个高危域 override 防护探针均拦截 `codex → decide`；汇报要求、自足概念问句、两个入口集成、check-first handoff 和默认 handoff 检查通过。报告列出全部 argmax→最终动作翻转与各条 override 日志。

## 数据与自动化约束

- 冻结标签文件未改写，SHA-256：`f5b572f313921a14ff7820ea8188af7a7366226ba6a5a7ad83153fae666c0b12`。
- 模型、训练数据和模型参数未修改；未执行重训练。
- `automatic_dispatch_allowed` 仍为 `false`；策略只返回建议动作和 Codex handoff，不调用 Codex。
- `blind-015` 的人工标签不回改。其最终策略动作 `clarify` 是新判据直接推导的已知分歧，不计为标注或模型错误。
