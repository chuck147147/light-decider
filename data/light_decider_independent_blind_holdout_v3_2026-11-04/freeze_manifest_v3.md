# light_decider v3 盲测冻结清单

- 数据集：`light_decider_independent_blind_holdout_v3`
- 冻结时间：2026-11-04 20:29:50（Asia/Shanghai，+08:00）
- 冻结题目文件：`blind_holdout_v3_unlabeled.xlsx`
- 标注来源文件：附件实际文件名 `v3代填副本.xlsx`（请求中称 `blind_holdout_v3_filled_draft.xlsx`）
- 标注来源文件 SHA-256：`eb2960821cb8fd2ce9ac8b53edddcf549a751b488a630f7b9d7b9ac16faa3425`
- SHA-256 校验：通过；与用户指定值一致
- 冻结标签文件：`blind_holdout_v3_labels_frozen.jsonl`
- 冻结标签文件 SHA-256：`1b28daf61866153cda78fb6f7060ed084659f73b7ef1efd128e5f53dd0d1e07b`
- 标签文件只读确认：[x] 是
- 样本数：24
- 动作计数：decide 6、clarify 7、codex 6、codex+declare_default 3、codex+check_first 2

## 标签来源声明

标签由助手代填；作者 于 2026-11-04 照单全收，未作修改。来源类型为“代填 + 人工确认”，**不是独立盲标**。标签值按附件 D–H 列原样转存，未改写；原始附件工作簿保持不动。

## 冻结校验

- 输入附件哈希已在读取工作簿前核对，匹配用户指定的 SHA-256。
- 冻结标签文件包含 24 条记录；样本编号连续且唯一；动作标签均属于题册允许值。
- 冻结标签 JSONL 的哈希在设为只读后重新核验，与本清单一致。
- 参考答案文件仅在本冻结文件和本清单完成后才允许打开。
