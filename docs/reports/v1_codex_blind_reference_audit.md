# 第二阶段·第三步：Codex 盲标参考审计

## 隔离方式

- 参考文件：`light_decider_independent_blind_holdout_v1_codex_blind_reference.jsonl`；它与用户盲标用的空标签 CSV 分开保存，不向 CSV 回填答案。
- 标注时只依据 24 条输入和 v2 细则；没有运行决策器，也没有查看模型分数、预测或评测输出。
- 标签按动作细分为 `decide`、`codex`、`codex+declare_default`、`codex+check_first` 和 `clarify`；映射回旧三分类时，后三种 Codex 动作均投影为 `codex`。

## 限制

- 该参考由同一 Codex 先写题、后按规则自标，虽盲于模型输出，却不是独立人类标注，也不能替代用户的人工金标准。
- 不用于训练、调参、正式评测或选择模型。请先完成 `light_decider_independent_blind_holdout_v1.csv` 的人工盲标，再查看此参考进行差异复核。
- `decide` 样本两轴记为 `null`，因为它们按细则不进入代码实现请求的两轴判断；高危域标记仍可独立记录。
