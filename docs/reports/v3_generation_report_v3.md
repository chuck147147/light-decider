# light_decider 盲测集 v3 造题报告

**题目文件：** `blind_holdout_v3_unlabeled.xlsx`  
**状态：** 合成生成、未人工确认；本单只造题，不做模型或策略评测。  
**样本设计：** 本套含定向压力题，非随机样本。  
**生成日期：** 2026-11-04（Asia/Shanghai）  
**题目文件 SHA-256：** `5aa469c024c23374cb2bde8b433b20ebf91d39d6cae97f56c89708937d15d39d`

## 配比与覆盖

| 请求设计类别 | 条数 |
|---|---:|
| 纯知识问答、解释、对比（decide） | 6 |
| 规格完整的实现请求（codex） | 6 |
| 缺关键规格且无安全默认（clarify） | 7 |
| 用户授权代选的可逆默认（codex+declare_default） | 3 |
| 依赖现有代码库约定（codex+check_first） | 2 |
| **合计** | **24** |

规格完整实现中有 2 条明确处于已有项目语境，但关键行为和数据均已给定，不依赖查找项目约定。授权代选组使用了不同于 v2 已出现表达的新措辞。clarify 中的两个机构规则场景分别涉及大学场地预约和手工品平台评价申诉；没有复用餐厅迟到或学校补考场景。

| 高危域覆盖 | 条数 |
|---|---:|
| payment | 1 |
| permission | 1 |
| rate_limiting | 1 |
| deduplication | 1 |
| locale_sensitive_parsing（日期/历法） | 1 |

## 避撞范围与方法

对照输入均只读：

- v1：`data/light_decider_independent_blind_holdout_v1_current_model_predictions_2026-11-03.jsonl`，仅取 24 条 `text`；不读取、不使用模型动作、分数或建议路由。
- v2：`data/light_decider_independent_blind_holdout_v2_2026-11-04/blind_holdout_v2_unlabeled.xlsx` 的 24 条请求文本；当前 SHA-256 与 v2 冻结清单记录一致。
- 第二轮实际训练/开发集：`training_final_v3_2026-11-04/train.jsonl` 516 条、`dev.jsonl` 130 条，共 646 条。
- 另逐条纳入五个 minipair/定向样本文件；共 157 行，跨集合精确去重后新增 70 条独立参考文本。文件：`code_spec_minipairs_holdout_zh.jsonl`, `code_spec_minipairs_train_zh.jsonl`, `code_spec_minipairs_two_axis_relabel_v2_zh.jsonl`, `code_spec_targeted_false_negative_minipairs_train_drafts_zh.jsonl`, `code_spec_targeted_false_negative_minipairs_v2_train_drafts_zh.jsonl`。

筛查分两层：先将空白折叠并忽略大小写做全文精确去重；然后对字符 2–4 gram 计算集合 Jaccard 相似度，分别找每条新题在 v1、v2、train/dev 和补充 minipair 中的最近邻，并人工核对最近邻及任务对象、行为目标、数据对象和规则分支。该字符相似度只是词面筛查，不证明语义独立；它不是模型推理，也没有调用模型或 routing_policy。0.12 仅作人工复核提醒线，本套没有题目超过该线；每题仍逐条做了场景族复核。

| 对照组 | 对照文本数 | 最高近邻相似度（新题 ID） |
|---|---:|---|
| v1 | 24 | 0.0361（blind-v3-001） |
| v2 | 24 | 0.0710（blind-v3-011） |
| train/dev | 646 | 0.0384（blind-v3-008） |
| 补充 minipair（精确去重后新增） | 70 | 0.0273（blind-v3-022） |

下表列出全部 24 条的新题场景族、每个对照组的最近邻和人工避撞结论。相似度为字符 n-gram 词面分数；结论按场景家族与实际操作目标人工判断。

| ID | 新题场景族 | 最近 v1 / v2 | 最近 train/dev / 补充 minipair | 人工避撞核对 |
|---|---|---|---|---|
| blind-v3-001 | 偏振光与眩光解释 | `v1:blind-018` (0.0361) / `v2:blind-v2-003` (0.0307) | `train:candidate-ai-mitra-202` (0.0349) / `minipair:code-spec-targeted-fn-refund_retry_scope-clarify` (0.0046) | 最近的 v1-018 是 HTTP 缓存校验器问题；主题为偏振光与眩光，没有共享领域或操作目标。 |
| blind-v3-002 | 医疗影像标注角色权限 | `v1:blind-023` (0.0082) / `v2:blind-v2-017` (0.0236) | `train:code-spec-minipair-holdout-export_partial_file-clarify-v2-two-axis` (0.0228) / `minipair:code-spec-minipair-train-file_write_mode-clarify` (0.0211) | 最近的 v2-017 是跨时区排班；医疗影像角色权限与排班语义不同，且没有复用 CI 凭证场景。 |
| blind-v3-003 | GPX 轨迹摘要命令行工具 | `v1:blind-013` (0.0147) / `v2:blind-v2-012` (0.0201) | `train:candidate-swebench-mesonbuild__meson-7460` (0.0275) / `minipair:code-spec-minipair-train-timezone_target-codex` (0.0255) | 最近训练项是 Meson 构建问题、时区函数；本题处理 GPX 轨迹点与分段距离，输入结构和目标均不同。 |
| blind-v3-004 | 展品图鉴卡片文字排版 | `v1:blind-022` (0.0042) / `v2:blind-v2-021` (0.0188) | `train:candidate-swebench-Lightning-AI__lightning-1177` (0.0101) / `minipair:code-spec-minipair-train-json_unknown_fields-codex` (0.0158) | 最近的 v2-021 是提交成功 toast；本题处理展品标题字号/行距，未复用通知呈现或园艺报名。 |
| blind-v3-005 | 浏览器扩展保存标签组 | `v1:blind-020` (0.0234) / `v2:blind-v2-023` (0.0313) | `train:candidate-swebench-mesonbuild__meson-7306` (0.0143) / `minipair:code-spec-targeted-fn-refund_retry_scope-clarify` (0.0090) | 最近的 v2-023 是 Godot 设置项迁移；本题的浏览器标签组身份和存储边界是另一套数据对象。 |
| blind-v3-006 | 图书馆自助借还扫码限流 | `v1:blind-021` (0.0067) / `v2:blind-v2-015` (0.0436) | `train:code-spec-minipair-holdout-symlink_walk-clarify-v2-two-axis` (0.0068) / `minipair:code-spec-minipair-train-retry_limit-clarify` (0.0068) | 最近的 v2-015 是账户恢复短信限流；本题对象是图书馆终端扫码，不涉及手机号、验证码或恢复账户。 |
| blind-v3-007 | 幸存者偏差解释 | `v1:blind-022` (0.0027) / `v2:blind-v2-003` (0.0045) | `train:v2-webhook-any2xx-safe-default` (0.0080) / `minipair:code-spec-minipair-train-retention_days-codex` (0.0063) | 最近的 v1-022 是 SVG 状态条实现；本题是对幸存者偏差的概念解释，未复用代码实现请求。 |
| blind-v3-008 | 数独棋盘冲突校验组件 | `v1:blind-002` (0.0090) / `v2:blind-v2-006` (0.0217) | `train:candidate-ai-mitra-417` (0.0384) / `minipair:v2-rate-render-jobs-clarify` (0.0159) | 最近训练项是 JavaScript 字符串/去重练习；本题是数独棋盘规则校验，没有共享数据清洗目标。 |
| blind-v3-009 | 国际帆船赛证件日期解析 | `v1:blind-021` (0.0025) / `v2:blind-v2-017` (0.0242) | `train:code-spec-minipair-holdout-export_partial_file-clarify-v2-two-axis` (0.0237) / `minipair:code-spec-minipair-train-file_write_mode-clarify` (0.0248) | 最近的 v2-017 是重复排班的夏令时处理；本题解析证件出生日期和纪年冲突，服务对象、输入源和结果用途不同。 |
| blind-v3-010 | 词汇练习答题反馈动效 | `v1:blind-015` (0.0064) / `v2:blind-v2-021` (0.0195) | `dev:candidate-ai-mitra-403` (0.0075) / `minipair:code-spec-minipair-train-worker_concurrency-codex` (0.0035) | 最近的 v2-021 是成功通知 toast；本题是词汇答题即时反馈动效，不涉及报名提交或通知生命周期。 |
| blind-v3-011 | 双栏文本编辑器分隔栏缩放 | `v1:blind-008` (0.0215) / `v2:blind-v2-009` (0.0710) | `train:candidate-swebench-JohnSnowLabs__spark-nlp-13798` (0.0248) / `minipair:code-spec-minipair-train-timezone_target-codex` (0.0209) | 最近的 v2-009 是键盘操作时间范围控件；本题调整双栏分隔比例，不调整时间端点。 |
| blind-v3-012 | 大学社团排练室预约规则 | `v1:blind-023` (0.0109) / `v2:blind-v2-019` (0.0186) | `train:code-spec-minipair-holdout-permission_inheritance-clarify-v2-two-axis` (0.0175) / `minipair:code-spec-minipair-train-config_precedence-clarify` (0.0189) | 最近的 v2-019 是学校补考成绩政策；本题分配排练室资源，不涉及成绩、考试或重考。 |
| blind-v3-013 | 中位数代表典型值的解释 | `v1:blind-007` (0.0062) / `v2:blind-v2-004` (0.0104) | `train:candidate-ai-mitra-572` (0.0233) / `minipair:code-spec-minipair-train-null_import-codex` (0.0052) | 最近的 v1-007 是 Markdown 注释取舍；本题解释中位数与典型值，主题与应用任务不同。 |
| blind-v3-014 | 国际象棋对局 PGN 导出 | `v1:blind-013` (0.0131) / `v2:blind-v2-012` (0.0125) | `dev:candidate-ai-mitra-403` (0.0355) / `minipair:code-spec-minipair-train-file_write_mode-codex` (0.0221) | 最近的 v1-013 是 SSE 与 long polling 比较；本题导出单局 PGN，文件内容与网络传输方案无关。 |
| blind-v3-015 | 陶艺课程报名定金结算 | `v1:blind-023` (0.0086) / `v2:blind-v2-013` (0.0216) | `train:code-spec-minipair-holdout-idempotency_scope-clarify-v2-two-axis` (0.0065) / `minipair:code-spec-minipair-train-interval_merge-clarify` (0.0074) | 最近的 v2-013 是跨境差旅报销付款；本题处理课程取消/改期定金，交易触发条件不同于报销与票据冲销。 |
| blind-v3-016 | 流程图连接线吸附约定 | `v1:blind-014` (0.0158) / `v2:blind-v2-023` (0.0110) | `dev:candidate-ai-mitra-652` (0.0256) / `minipair:code-spec-targeted-fn-workspace_access_inheritance-clarify` (0.0093) | 最近的 v1-014 是 OpenAPI 扩展约定；本题依赖图形锚点、拖动和序列化约定，领域不同。 |
| blind-v3-017 | 舞蹈教学播放器初始倍率 | `v1:blind-017` (0.0085) / `v2:blind-v2-020` (0.0196) | `train:candidate-swebench-Lightning-AI__lightning-1177` (0.0068) / `minipair:code-spec-minipair-train-json_unknown_fields-codex` (0.0100) | 最近的 v2-020 是照片排序默认；本题选择视频播放倍率，不涉及照片列表排序或媒体文件改写。 |
| blind-v3-018 | 学术文献目录记录去重 | `v1:blind-021` (0.0107) / `v2:blind-v2-016` (0.0407) | `dev:candidate-swebench-Lightning-AI__lightning-128` (0.0109) / `minipair:code-spec-minipair-train-money_rounding-codex` (0.0131) | 最近的 v2-016 是供应商合同日期导入；本题按出版物身份和版本关系合并书目，不解析合同日期。 |
| blind-v3-019 | Electron 音频时间轴片段吸附 | `v1:blind-022` (0.0123) / `v2:blind-v2-024` (0.0154) | `train:v2-payment-subscription-renewal-codex` (0.0141) / `minipair:code-spec-targeted-fn-billing_callback_dedupe-codex` (0.0079) | 最近的 v2-024 是遥测指标注册；本题处理音频时间轴边界吸附与撤销，目标不同。 |
| blind-v3-020 | 城市热岛措施对比 | `v1:blind-007` (0.0047) / `v2:blind-v2-003` (0.0067) | `train:candidate-ai-mitra-663` (0.0105) / `minipair:code-spec-minipair-train-config_precedence-codex` (0.0043) | 最近的 v1-007 是 Markdown 注释比较；本题比较城市降温措施，词面相似来自泛化比较问法，主题不同。 |
| blind-v3-021 | 手工品平台差评申诉规则 | `v1:blind-010` (0.0055) / `v2:blind-v2-015` (0.0137) | `dev:code-spec-minipair-holdout-event_dedup_window-clarify-v2-two-axis` (0.0065) / `minipair:code-spec-targeted-fn-refund_retry_scope-clarify` (0.0115) | 最近的 v2-015 是短信限流；本题定义商家评价申诉和内容审核，不涉及访问频率或资金结算。 |
| blind-v3-022 | RGBA 颜色线性插值 | `v1:blind-022` (0.0134) / `v2:blind-v2-001` (0.0161) | `train:candidate-swebench-ytdl-org__youtube-dl-8843` (0.0155) / `minipair:code-spec-minipair-train-money_rounding-codex` (0.0273) | 最近的训练 minipair 是金额 ROUND_HALF_UP；本题对 RGBA 通道做插值，数值对象和计算目标不同。 |
| blind-v3-023 | 高海拔沸点解释 | `v1:blind-007` (0.0068) / `v2:blind-v2-004` (0.0110) | `train:candidate-ai-mitra-1537` (0.0278) / `minipair:code-spec-minipair-holdout-rate_limit_algorithm-codex` (0.0175) | 最近的 v2-004 是 Wasm 内存视图；本题解释气压与沸点，主题不同。 |
| blind-v3-024 | 等高线疏密含义 | `v1:blind-007` (0.0253) / `v2:blind-v2-002` (0.0136) | `train:candidate-ai-mitra-78` (0.0303) / `minipair:code-spec-targeted-fn-refund_retry_scope-clarify` (0.0088) | 最近的 v1-007 是脚注/文末注释比较；本题解释地形等高线，场景与术语不同。 |

## 冻结与使用约束

- 文件列结构沿用 v2 实际模板：`sample_id`、`请求文本`、`补充上下文`、`缺失关键规格`、`存在安全默认`、`高危域`、`最终动作`、`备注`。所有补充上下文及 D–H 标注单元格均留空。
- v1 原题和 v2 原题文件未改写；v2 当前哈希 `64540d63b22aa9a1c833e2fcd51231dc0b972e287db2d5fb14243baa7e6d6729` 与其冻结清单中的哈希 `64540d63b22aa9a1c833e2fcd51231dc0b972e287db2d5fb14243baa7e6d6729` 一致。
- 未改模型、routing_policy 或任何已有数据；未重训；未运行模型、策略或评测；自动派发保持关闭。
- 内部参考答案另存为 `blind_holdout_v3_codex_reference_SEALED.jsonl`，其首行写有“作者 盲标完成前不得打开、不得用于任何调整”。盲标并冻结前不得打开、训练、调参、改规则或评测。
- 备查验收线（本单未执行）：clarify 召回 ≥6/7；clarify→decide = 0；加权代价 ≤10。待 作者 盲标并冻结后另行派单，评测只跑一次。

## 输入文件与数据版本 SHA-256

| 文件 | SHA-256 |
|---|---|
| v1 原题 CSV | `9d065f614126c82b0edd8e149c30b4b641e2748f12ab6c9d86db073036eef41b` |
| v1 文本参照 JSONL（仅取文本） | `589b1d244916e1710d75aac986aecc107b90d95c9398571033a41d8746757fae` |
| v2 未标注题册 | `64540d63b22aa9a1c833e2fcd51231dc0b972e287db2d5fb14243baa7e6d6729` |
| 两轴标注细则 v3 | `067d56640b50979db65967ff27a94e7f9e18aca22f38b98de96fe61075f8a18c` |
| 第二轮 train | `4d053f6fd31ab5e2a3ee78e8c9b3737dc91a5cb570dcede805d2891955ba6bba` |
| 第二轮 dev | `2760e07be9e49a928ef2bd362fefeb59c7ea604a9cb66f6a27ad7e0a7ac18ae6` |
| v3 未标注题册 | `5aa469c024c23374cb2bde8b433b20ebf91d39d6cae97f56c89708937d15d39d` |
