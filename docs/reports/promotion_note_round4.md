# light_decider round-4 转正记录

用户 于 2026-11-06（Asia/Shanghai）批准将默认模型切换为 round-4，切换于同日生效。

## 评测依据

v5 冻结集共 24 条，SHA-256 为 `2da0a06bacf3d27d77a8f84e6d9c0c4557a49010d575bc92f3c27ba39bb7e011`。标签来自助手代填，经 用户 原样采纳，来源为 `assistant_drafted_chuck_adopted`。[冻结清单](light_decider_independent_blind_holdout_v5_2026-11-06/freeze_manifest_v5.md)

| 预注册条件 | round-4 + v3.1 实测 | 结果 |
|---|---:|---|
| clarify 召回 ≥6/7 | 6/7 | 通过 |
| clarify→decide = 0 | 0 | 通过 |
| 加权代价 ≤10 | 8 | 通过 |
| 加权代价严格低于 round-2 + v3.1 | 8 < 10 | 通过 |

完整分片和错误清单见 [v5 评测报告](light_decider_independent_blind_holdout_v5_2026-11-06/evaluation_report_v5.md)。

## 生效配置与回退

- `light_decider.predict.DEFAULT_MODEL_PATH` 指向 `artifacts/decisioner_round4_v1_2026-11-05.joblib`。模型 SHA-256 为 `6eff1a818db972bf887ed885f1cad4162dc5cef69ebdee0fb4f7ac32c37b286b`。
- `try_router.py`、单条轻量 CLI 和影子 sidecar 共用该默认指针。语义模型入口为 `try_router_semantic.py`，也可在交互入口用 `--model` 指定语义模型目录。
- 现役策略为 v3.1。v3.2b 仍是未激活候选。影子 sidecar 仅记录 JSONL，熔断记录阈值为 0.6，自动派发关闭。
- 回退文件为 `artifacts/decisioner_round2_v1_2026-11-04.joblib`，SHA-256 为 `f2e1dc659d1d9a78c3136401ba2d987e80bd836a85005530bf75e53510d2dc25`。需要整体回退时，将 `DEFAULT_MODEL_PATH` 指回该文件。临时试用可传 `--model artifacts/decisioner_round2_v1_2026-11-04.joblib`。若同时开启影子模式，可用 `--shadow-model` 指定同一回退文件。

## 切换后冒烟校验

以 `python try_router.py` 无参数启动，从 v5 只读冻结文件输入全部 24 条请求，复跑一次。精确命中 20/24，clarify 召回 6/7，clarify→decide 为 0，加权代价为 8，与 B 口径一致。

用一条额外请求核对单条 CLI 和影子日志。单条 CLI 与交互入口输出一致，影子日志记录 round-4 和 v3.1，`automatic_dispatch_allowed` 和 `training_eligible` 均为 `false`。两份模型、两份策略以及 v5 冻结标签的 SHA-256 均与切换前一致。
