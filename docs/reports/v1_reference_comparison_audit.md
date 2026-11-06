# 用户盲标与 Codex 参考对照审计

## 对照概况

- 用户在 Codex 参考保持隔离时完成并保存 24/24 条标签；人工标签已先独立复制存档。
- 五类动作完全一致：23/24（95.8%）。这只是人工标签与 Codex 规则参考的一致率，不是模型准确率。
- 投影到旧三分类后的标签一致：23/24。
- 本轮没有运行模型、没有训练或调参；未修改用户标签。
- 参考标签由同一 Codex 编写和标注，不能视为独立人工意见；人工标签仍为本批金标准。

### 标签分布

| 动作 | 用户人工标签 | Codex 参考 |
|---|---:|---:|
| `decide` | 8 | 8 |
| `codex` | 4 | 4 |
| `codex+declare_default` | 3 | 2 |
| `codex+check_first` | 2 | 2 |
| `clarify` | 7 | 8 |

## 分歧条目

- `blind-015`：你的标签是 `codex+declare_default`，Codex 参考是 `clarify`。
- 请求：做一个团队工作板，完成的事项要及时离开主列表，之后是删除还是归档并保留搜索记录？
- Codex 参考理由：删除与归档对数据可恢复性和搜索能力影响不同；请求没有授权实现者任选。
- Codex 参考当时将删除与归档视为影响数据保留的两种选择，并因未识别出安全默认而判 `clarify`。
- 用户随后确认：本条有意将“归档并保留搜索记录”视为安全默认，因此人工金标签 `codex+declare_default` 保持有效。这确认了本条参考分歧的处理结果；不推广为所有“删除/归档”请求的通用规则，也不回写 Codex 参考文件。

## 逐条标签

| 编号 | 人工标签 | Codex 参考 | 一致 |
|---|---|---|:---:|
| blind-001 | `decide` | `decide` | 是 |
| blind-002 | `codex` | `codex` | 是 |
| blind-003 | `clarify` | `clarify` | 是 |
| blind-004 | `decide` | `decide` | 是 |
| blind-005 | `codex+declare_default` | `codex+declare_default` | 是 |
| blind-006 | `clarify` | `clarify` | 是 |
| blind-007 | `decide` | `decide` | 是 |
| blind-008 | `codex` | `codex` | 是 |
| blind-009 | `decide` | `decide` | 是 |
| blind-010 | `clarify` | `clarify` | 是 |
| blind-011 | `codex` | `codex` | 是 |
| blind-012 | `clarify` | `clarify` | 是 |
| blind-013 | `decide` | `decide` | 是 |
| blind-014 | `codex+check_first` | `codex+check_first` | 是 |
| blind-015 | `codex+declare_default` | `clarify` | 否 |
| blind-016 | `clarify` | `clarify` | 是 |
| blind-017 | `codex+declare_default` | `codex+declare_default` | 是 |
| blind-018 | `decide` | `decide` | 是 |
| blind-019 | `clarify` | `clarify` | 是 |
| blind-020 | `codex+check_first` | `codex+check_first` | 是 |
| blind-021 | `decide` | `decide` | 是 |
| blind-022 | `codex` | `codex` | 是 |
| blind-023 | `clarify` | `clarify` | 是 |
| blind-024 | `decide` | `decide` | 是 |

