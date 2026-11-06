# 人工金标冻结审计｜2026-11-03

- 冻结对象：用户填写的盲标工作簿，以及从工作簿逐条提取的 24 条人工标签。
- 日期：2026-11-03（Asia/Shanghai）。
- 冻结方式：分别另存 dated copy，校验 SHA-256 与源文件完全一致，随后设置 Windows 只读属性。
- 标签状态：24/24 条已填；原标签不再修改。若以后确认需要修正，须新建带日期的版本并保留本冻结版。
- 原始空标签 CSV 未回填；模型未运行、未训练、未调参。

## 冻结文件

| 文件 | SHA-256 | 只读 |
|---|---|:---:|
| `light_decider_blind_label_sheet_v1_frozen_2026-11-03.xlsx` | `288d88e23ee56244c284f6c02340d952a9a95ab146fc6641dd743d8344a6dcd9` | 是 |
| `light_decider_independent_blind_holdout_v1_human_labels_frozen_2026-11-03.jsonl` | `f5b572f313921a14ff7820ea8188af7a7366226ba6a5a7ad83153fae666c0b12` | 是 |

- 冻结清单：`data/frozen_2026-11-03/freeze_manifest_2026-11-03.json`。
