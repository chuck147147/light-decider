# 盲标冻结后当前模型预测审计｜2026-11-03

- 输入：冻结集 24 条文本；程序只读取 `sample_id` 和 `text`，未读取人工标签或 Codex 参考。
- 模型：项目默认语义模型 `artifacts/decisioner_semantic_draft`，CPU ONNX 推理；模型文件和路由代码哈希列于下方。
- 输出：每条包含最终 `model_action`、原始 `suggested_route`、分数、策略覆盖与分句动作；无人工标签字段。
- 时间：人工标签冻结之后运行，仅作为三方对照材料；没有训练、调参、修改模型或 `routing_policy`。
- `automatic_dispatch_allowed` 保持 false；本文件不是调参结果，不自动派发。

## 动作数量

| 当前模型动作 | 条数 |
|---|---:|
| `clarify` | 2 |
| `codex` | 12 |
| `decide` | 10 |

## 模型文件 SHA-256

- `metadata.json`: `c4b953787095f53d7d220fd8125a3aa99694b95362684e1f0aefb77ac5db0dd4`
- `model_int8.onnx`: `0338c6ead569999bea33f246f30ef4c8f1d33c0d4267cc5fee9e9bacf11bbc36`
- `tokenizer.json`: `ce8bfe92804683d89f9af99220f90f61ef9f0e7b5986bae4beeeaba06140f469`

## 推理代码 SHA-256

- `light_decider/semantic_runtime.py`: `fbdb8716513d38cc618ae7f399b142da1bf134e1b04db8dc906cbe2b08ceae8e`
- `light_decider/routing_policy.py`: `15430bc0fb550c0c2b124c729c126031ceb84c35cb852dadad633ed512b580e2`
- `light_decider/clause_segmentation.py`: `c97e31aa6d8b02884b3e2fae3bd15346f73d76ae9866118d854edff7c34643f7`
- `light_decider/input_normalization.py`: `c6871cd53d75c95d2d5c767980f6af189417f2dd669973b38e4c00e9fb8362ee`
- `light_decider/model.py`: `b99d545e28d6ca0640fb55f8892cc8b6b16af74db805e7e492e152cf8ef72e76`

