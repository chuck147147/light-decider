# Round-2 + routing_policy v3.2b clean replay

> 本表为已见开发数据回放，不是盲测泛化成绩。它仅用于 用户 已批准的激活前置条件，不得据此重训或修改标签。

- 回放时间：2026-11-05 14:48:22 +0800（Asia/Shanghai）
- 回放范围：v1–v4 冻结题 96 条 + round-2 dev 127 条，共 223 条；v1 的 blind-015 按冻结标签计入。
- 执行方式：round-2 固定模型对 223 条输入从零计算一次批量分数；v3.1 和 v3.2b 对同一 argmax 与同一上下文逐条回放。未读取任何历史预测分数或策略输出。
- round-2 模型 SHA-256：`f2e1dc659d1d9a78c3136401ba2d987e80bd836a85005530bf75e53510d2dc25`。v3.1 SHA-256：`719f88ed53635d8b69f35e52e00741b9d9b81128d7f72d99f176ddfe9902e86e`。v3.2b 候选 SHA-256：`f15278154ee892d2264768cf2310113fb188be89f178588db10acd7ab06a8838`。
- 逐条分数缓存：`data/light_decider_activation_v3_2b_2026-11-05/round2_clean_replay_scores.jsonl`；223 条；SHA-256 `06fe2d3db38464850e1bcff4597df7a9a0185f924a7f698b17f5fab8409dff78`。缓存逐条保存请求、金标、三类模型分数、argmax、两版策略动作/翻转日志、风险域与代价。
- 自动派发：关闭。此回放不执行 Codex handoff 或任何外部动作。

## 总体逐口径对照

| 口径 | 条数 | 五类准确 | 加权总代价 | clarify 召回 | clarify→decide | 高危错误 |
|---|---:|---:|---:|---:|---:|---:|
| round2 + v3.1 | 223 | 174/223 (78.0%) | 79 | 71/76 | 2 | 5/37 |
| round2 + v3.2b | 223 | 175/223 (78.5%) | 74 | 72/76 | 2 | 5/37 |

## 按题集拆分

| 题集 | 条数 | v3.1 代价 | v3.2b 代价 | 差值 (v3.2b−v3.1) | v3.1 高危错 | v3.2b 高危错 | clarify→decide (v3.1/v3.2b) |
|---|---:|---:|---:|---:|---:|---:|---:|
| v1 | 24 | 3 | 3 | +0 | 1/8 | 1/8 | 0/0 |
| v2 | 24 | 8 | 8 | +0 | 0/4 | 0/4 | 0/0 |
| v3 | 24 | 14 | 9 | -5 | 1/7 | 1/7 | 0/0 |
| v4 | 24 | 13 | 13 | +0 | 0/5 | 0/5 | 0/0 |
| round2_dev | 127 | 41 | 41 | +0 | 3/13 | 3/13 | 2/2 |

## 激活前置条件复核

- clarify→decide 为 0：不满足（v3.1 2，v3.2b 2）。
- 高危条目零新增错误：满足。v3.1 高危错 5 条，v3.2b 高危错 5 条；新增错误 0 条；修复 0 条。
- v3.2b 总代价不高于 v3.1：满足（74 vs 79）。
- 三项条件合计：未全部满足，不得激活。


## v3.1 错误清单

| 题集 | 编号 | 金标 | 预测 | 代价 | argmax | 策略原因 |
|---|---|---|---|---:|---|---|
| v1 | blind-009 | decide | codex | 1 | codex | high_risk_override_cannot_route_to_decide |
| v1 | blind-015 | codex+declare_default | clarify | 1 | clarify | explicit_key_choice_question |
| v1 | blind-024 | decide | codex | 1 | codex | highest_model_score |
| v2 | blind-v2-001 | decide | codex | 1 | codex | highest_model_score |
| v2 | blind-v2-003 | decide | codex | 1 | codex | highest_model_score |
| v2 | blind-v2-004 | decide | codex | 1 | codex | highest_model_score |
| v2 | blind-v2-017 | clarify | codex | 5 | codex | highest_model_score |
| v3 | blind-v3-003 | codex | clarify | 1 | codex | locale_sensitive_value_format_ambiguous |
| v3 | blind-v3-004 | codex+declare_default | codex | 1 | clarify | explicit_implementation_request |
| v3 | blind-v3-007 | decide | clarify | 1 | clarify | highest_model_score |
| v3 | blind-v3-010 | codex+declare_default | codex | 1 | clarify | explicit_implementation_request |
| v3 | blind-v3-012 | clarify | codex | 5 | clarify | explicit_implementation_request |
| v3 | blind-v3-013 | decide | codex | 1 | codex | highest_model_score |
| v3 | blind-v3-014 | codex | codex+check_first | 1 | codex | existing_project_convention_check |
| v3 | blind-v3-017 | codex+declare_default | codex | 1 | clarify | explicit_implementation_request |
| v3 | blind-v3-019 | codex | codex+check_first | 1 | codex | existing_project_convention_check |
| v3 | blind-v3-023 | decide | codex | 1 | codex | highest_model_score |
| v4 | blind-v4-001 | decide | clarify | 1 | clarify | highest_model_score |
| v4 | blind-v4-002 | decide | clarify | 1 | clarify | highest_model_score |
| v4 | blind-v4-003 | clarify | codex | 5 | codex | highest_model_score |
| v4 | blind-v4-008 | codex | codex+check_first | 1 | codex | existing_project_convention_check |
| v4 | blind-v4-010 | codex+declare_default | decide | 1 | clarify | explicit_explanation_request |
| v4 | blind-v4-012 | decide | clarify | 1 | clarify | highest_model_score |
| v4 | blind-v4-021 | codex | codex+check_first | 1 | codex | existing_project_convention_check |
| v4 | blind-v4-022 | codex+declare_default | codex | 1 | clarify | explicit_implementation_request |
| v4 | blind-v4-024 | codex+declare_default | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-ai-mitra-113 | decide | codex | 1 | decide | explicit_implementation_request |
| round2_dev | candidate-ai-mitra-456 | codex | decide | 1 | decide | highest_model_score |
| round2_dev | candidate-ai-mitra-469 | codex | decide | 1 | decide | highest_model_score |
| round2_dev | candidate-sharc-07c7d9afb01e2d0d09f356e02468f4b7bcaf600c | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-5428ea8f13aa09f8abce5744717627870983f677 | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-6d3e7adeaa2a369ebd471a46a5b1152049b77202 | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-82f13958908ce92ea41f4d90f3978b3172ef7feb | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-8b83c3af43346bac342b4a6376050de2125c98c4 | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-8c30bb3c9025face6cbdbc5a7bf5f3ed2ec9b1da | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-8fc68ec051eea67cc3f50fdd4f45bd9aca442871 | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-977073a6f853e94cd26ccd9e0bd0d89b3a0e7a73 | clarify | decide | 10 | decide | highest_model_score |
| round2_dev | candidate-sharc-c520406962a948d73c4a9d1f62de9008c8f3330c | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-c7666be42ddab290163aea11f9e6617c0a10c763 | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-ca1a4d0beefeadbb8a718fa1e7d1e1f44bd23418 | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-ea400cb3aa461a3e881687c5b5cefc98dd7c76bc | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-f676c41dcc3cfb6f08d2a1c33581ae51e816b738 | clarify | decide | 10 | decide | highest_model_score |
| round2_dev | candidate-swebench-DataDog__integrations-core-6239 | codex | decide | 1 | codex | explicit_explanation_request |
| round2_dev | candidate-swebench-Lightning-AI__lightning-128 | codex | decide | 1 | codex | explicit_explanation_request |
| round2_dev | candidate-swebench-mesonbuild__meson-6887 | codex | decide | 1 | codex | explicit_explanation_request |
| round2_dev | candidate-swebench-ytdl-org__youtube-dl-3407 | codex | decide | 1 | codex | explicit_explanation_request |
| round2_dev | candidate-swebench-ytdl-org__youtube-dl-6731 | codex | decide | 1 | codex | explicit_explanation_request |
| round2_dev | code-spec-minipair-holdout-search_tie_break-clarify-v2-two-axis | codex+declare_default | codex | 1 | codex | highest_model_score |
| round2_dev | v2-dedupe-atomic-insert-safe-default | codex+declare_default | codex | 1 | codex | highest_model_score |

## v3.2b 错误清单

| 题集 | 编号 | 金标 | 预测 | 代价 | argmax | 策略原因 |
|---|---|---|---|---:|---|---|
| v1 | blind-009 | decide | codex | 1 | codex | high_risk_override_cannot_route_to_decide |
| v1 | blind-015 | codex+declare_default | clarify | 1 | clarify | explicit_key_choice_question |
| v1 | blind-024 | decide | codex | 1 | codex | highest_model_score |
| v2 | blind-v2-001 | decide | codex | 1 | codex | highest_model_score |
| v2 | blind-v2-003 | decide | codex | 1 | codex | highest_model_score |
| v2 | blind-v2-004 | decide | codex | 1 | codex | highest_model_score |
| v2 | blind-v2-017 | clarify | codex | 5 | codex | highest_model_score |
| v3 | blind-v3-003 | codex | clarify | 1 | codex | locale_sensitive_value_format_ambiguous |
| v3 | blind-v3-004 | codex+declare_default | clarify | 1 | clarify | highest_model_score |
| v3 | blind-v3-007 | decide | clarify | 1 | clarify | highest_model_score |
| v3 | blind-v3-010 | codex+declare_default | clarify | 1 | clarify | highest_model_score |
| v3 | blind-v3-013 | decide | codex | 1 | codex | highest_model_score |
| v3 | blind-v3-014 | codex | codex+check_first | 1 | codex | existing_project_convention_check |
| v3 | blind-v3-017 | codex+declare_default | clarify | 1 | clarify | highest_model_score |
| v3 | blind-v3-019 | codex | codex+check_first | 1 | codex | existing_project_convention_check |
| v3 | blind-v3-023 | decide | codex | 1 | codex | highest_model_score |
| v4 | blind-v4-001 | decide | clarify | 1 | clarify | highest_model_score |
| v4 | blind-v4-002 | decide | clarify | 1 | clarify | highest_model_score |
| v4 | blind-v4-003 | clarify | codex | 5 | codex | highest_model_score |
| v4 | blind-v4-008 | codex | codex+check_first | 1 | codex | existing_project_convention_check |
| v4 | blind-v4-010 | codex+declare_default | decide | 1 | clarify | explicit_explanation_request |
| v4 | blind-v4-012 | decide | clarify | 1 | clarify | highest_model_score |
| v4 | blind-v4-021 | codex | codex+check_first | 1 | codex | existing_project_convention_check |
| v4 | blind-v4-022 | codex+declare_default | clarify | 1 | clarify | highest_model_score |
| v4 | blind-v4-024 | codex+declare_default | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-ai-mitra-113 | decide | codex | 1 | decide | explicit_implementation_request |
| round2_dev | candidate-ai-mitra-456 | codex | decide | 1 | decide | highest_model_score |
| round2_dev | candidate-ai-mitra-469 | codex | decide | 1 | decide | highest_model_score |
| round2_dev | candidate-sharc-07c7d9afb01e2d0d09f356e02468f4b7bcaf600c | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-5428ea8f13aa09f8abce5744717627870983f677 | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-6d3e7adeaa2a369ebd471a46a5b1152049b77202 | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-82f13958908ce92ea41f4d90f3978b3172ef7feb | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-8b83c3af43346bac342b4a6376050de2125c98c4 | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-8c30bb3c9025face6cbdbc5a7bf5f3ed2ec9b1da | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-8fc68ec051eea67cc3f50fdd4f45bd9aca442871 | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-977073a6f853e94cd26ccd9e0bd0d89b3a0e7a73 | clarify | decide | 10 | decide | highest_model_score |
| round2_dev | candidate-sharc-c520406962a948d73c4a9d1f62de9008c8f3330c | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-c7666be42ddab290163aea11f9e6617c0a10c763 | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-ca1a4d0beefeadbb8a718fa1e7d1e1f44bd23418 | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-ea400cb3aa461a3e881687c5b5cefc98dd7c76bc | decide | clarify | 1 | clarify | highest_model_score |
| round2_dev | candidate-sharc-f676c41dcc3cfb6f08d2a1c33581ae51e816b738 | clarify | decide | 10 | decide | highest_model_score |
| round2_dev | candidate-swebench-DataDog__integrations-core-6239 | codex | decide | 1 | codex | explicit_explanation_request |
| round2_dev | candidate-swebench-Lightning-AI__lightning-128 | codex | decide | 1 | codex | explicit_explanation_request |
| round2_dev | candidate-swebench-mesonbuild__meson-6887 | codex | decide | 1 | codex | explicit_explanation_request |
| round2_dev | candidate-swebench-ytdl-org__youtube-dl-3407 | codex | decide | 1 | codex | explicit_explanation_request |
| round2_dev | candidate-swebench-ytdl-org__youtube-dl-6731 | codex | decide | 1 | codex | explicit_explanation_request |
| round2_dev | code-spec-minipair-holdout-search_tie_break-clarify-v2-two-axis | codex+declare_default | codex | 1 | codex | highest_model_score |
| round2_dev | v2-dedupe-atomic-insert-safe-default | codex+declare_default | codex | 1 | codex | highest_model_score |

## 标签与风险口径

- v1 使用冻结用户标签；v2 使用冻结用户标签和对应的 canonical prompt/context snapshot；v3/v4 使用冻结 JSONL 中的动作；round-2 dev 使用 `label_5class`。标签只读。
- 高危切片统一取显式合法域标记（有标记时）与两版策略共同的 `detect_high_risk_domains` 结果并集。v1 与 dev 原表没有风险域列，因此用同一 detector 补齐；v2 的非域值 `13` 不作为风险域。两版 detector 对 223 条的输出一致。
- weighted cost: exact=0; clarify→decide=10; clarify→codex* =5; all other mismatches=1。
