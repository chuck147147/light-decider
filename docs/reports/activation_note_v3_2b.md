# routing_policy v3.2b 激活记录

## 决定

- 决策人：用户
- 决策日期：2026-11-05
- 授权背景：用户 批准基于累计证据进行破格激活；该授权受本单三项回放前置条件约束。
- 执行状态：**未激活**。前置条件未全部满足，因此没有切换现役策略，也没有修改影子模式 sidecar。
- 当前组合：round-2 模型 + routing_policy v3.1；自动派发保持关闭。

## 证据链

1. `data/policy_regression_runs/routing_policy_v3_2_audit_2026-11-04/ablation_report_v3_1.md`：`explicit_implementation_request` 留一净贡献为 -1。
2. `data/policy_regression_runs/routing_policy_v3_2_audit_2026-11-04/regression_v3_2b_devset.md`：v1–v3 的 72 条已见开发集上，v3.2b 代价 20，低于 v3.1 的 25；clarify→decide 为 0，高危错误为 1/17 且没有增加。该报告记录的是开发集成绩，不是泛化证据。
3. 用户 本次批准说明还将“v4 签名救援复现”列为累计证据之一；当前工作区未发现可独立核验的复现文件，因此本记录不把它当作本次回放结果或盲测过线证据。
4. `data/light_decider_independent_blind_holdout_v4_2026-11-05/evaluation_report_v4.md`：v4 的 round-3 + v3.2b 口径代价为 11，高于预注册上限 10；该口径未通过成本线。不得改述为盲测通过。
5. 本次 clean replay 重新计算 round-2 模型在 v1–v4 全部 96 条和 round-2 dev 127 条上的逐条分数，并用同一分数分别回放 v3.1 与 v3.2b。逐条缓存：`round2_clean_replay_scores.jsonl`，SHA-256：`06fe2d3db38464850e1bcff4597df7a9a0185f924a7f698b17f5fab8409dff78`。

## 激活前置条件结果

| 条件 | 回放结果 | 是否满足 |
|---|---|---|
| v3.2b clarify→decide = 0 | 2 条 | **否** |
| 高危条目不新增错误 | v3.1 与 v3.2b 均为 5/37；新增 0 条 | 是 |
| v3.2b 总代价不高于 v3.1 | 74 vs 79 | 是 |

未满足的两条为 round-2 dev 样本 `candidate-sharc-977073a6f853e94cd26ccd9e0bd0d89b3a0e7a73` 和 `candidate-sharc-f676c41dcc3cfb6f08d2a1c33581ae51e816b738`。两条金标均为 clarify，模型 argmax 与两版策略最终动作均为 decide，原因是 `highest_model_score`。

## 当前操作状态

因为 clarify→decide 前置条件未通过，本次没有把 `routing_policy_v3_2b_candidate.py` 复制到现役指针，没有创建或替换 v3.1 归档，也没有改动 sidecar。`routing_policy.py` 继续保持 v3.1。v3.2b 仍是未激活候选，自动派发仍关闭。

本次全量结果是已见数据上的开发回放，不是新泛化证据。v3.2b 没有在 v4 上通过代价≤10的成本线。
