# light_decider 盲测集 v4 冻结清单

- 数据集：`light_decider_independent_blind_holdout_v4`
- 冻结时间：2026-11-05 13:45:18 +0800（Asia/Shanghai）
- 标注来源文件：附件实际文件名 `v4 代填草稿.xlsx`（任务中称 `blind_holdout_v4_filled_draft.xlsx`）
- 标注来源文件 SHA-256：`db3b7965e9a5f9ca1817027ac56239bcd1e6aeb88b43a717ae6a7e70bfc58f76`
- SHA-256 校验：通过；与用户指定值一致
- 冻结标签文件：`blind_holdout_v4_labels_frozen.jsonl`
- 冻结标签文件 SHA-256：`02ca2168736c978bb077f7490c46002a74ed735b96199f93c6709ffc0f1366e1`
- 样本数：24
- 动作计数：decide 6、codex 6、clarify 7、codex+declare_default 3、codex+check_first 2
- 标签列：附件 D–H 原值转存；未改动标签

## 标签来源声明

标签由助手代填；作者 于 2026-11-05 照单全收，未逐条改动。证据等级与 v3 同级，属于“代填 + 人工确认”，弱于 v1/v2 的独立人工标注；本集不能称为独立盲标。

## 冻结校验

- 在读取工作簿内容前校验了源文件 SHA-256，与任务指定值完全一致。
- 冻结 JSONL 含 24 条记录，编号连续且唯一，五类动作分布与预注册数量一致。
- 冻结标签逐项取自工作簿，不依据策略或模型输出生成或修改。
- 本次评测将在冻结文件与本清单写入后开始；未打开 sealed 参考文件。
