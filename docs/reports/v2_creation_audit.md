# light_decider 独立盲测集 v2 造题审计

- 冻结日期：2026-11-04（Asia/Shanghai）
- 样本来源：合成生成，未人工确认；未标注预期动作或两轴答案。
- 题目文件：`blind_holdout_v2_unlabeled.xlsx`；SHA-256：`64540d63b22aa9a1c833e2fcd51231dc0b972e287db2d5fb14243baa7e6d6729`。
- 题目数：24；ID：`blind-v2-001` 至 `blind-v2-024`。
- 题目文件含定向压力题，非随机样本。
- 盲标列：D–H 共 120 个单元格，全部留空；文件中没有预填标签或答案键。
- 保密使用限制：用户完成盲标前，不用于训练、调参、改规则或评测。

## 覆盖设计

以下是造题覆盖统计，类别可重叠；它们只说明题目构成，不是逐题答案或标签。

| 覆盖项 | 条数 |
|---|---:|
| 纯技术提问（含实现术语） | 4 |
| 规格齐全的实现请求 | 8 |
| 缺关键规格且无安全默认 | 7 |
| 高危域缺规格 | 4 |
| 缺规格但由用户授权安全默认 | 3 |
| 依赖现有项目约定 | 2 |
| 实现请求采用问句形式（定向压力题） | 6 |

高危域覆盖：payment、permission、rate_limiting、locale_sensitive_parsing 各至少 1 条，合计 4 条。边界压力题包括 4 条带实现术语的纯技术提问、6 条使用提问句式的明确实现请求。

## 独立性筛查方法与结果

1. 对照集为第二轮 train 516 条、dev 127 条，以及 v1 盲测输入文本 24 条，共 667 条。
2. v1 输入比较只读 `current_model_predictions` 文件的 `text` 字段；未使用模型动作、分数或建议路由来构造题目。v1 冻结金标文件仅用于 SHA-256 核验，没有改动。
3. 先将空白折叠并忽略大小写，检查规范化全文重复；结果为 0 条。
4. 使用字符级 TF-IDF 2–5 gram 检索每道题最相近的 3 条对照文本，再逐题人工对照任务对象、参与者、操作目标、决策分叉和场景族。表内给出 24 条题各自最近邻前三及人工结论。
5. 最高外部相似度为 0.0897；0.12 仅作人工复核提醒阈值，没有题目超过该值。该相似度是词面筛查，不是语义独立性的证明。
6. v2 内部最大字符相似度为 0.0545（blind-v2-005 / blind-v2-007）。两者同属网页实现，但一个处理对话框焦点/键盘，一个处理静态站离线搜索；用户目标、状态和数据流不同。

### 逐题最近邻复核

| 题目 ID | 外部最近邻前三（来源:ID，字符相似度） | 逐条人工复核结论 |
|---|---|---|
| blind-v2-001 | train:candidate-swebench-mesonbuild__meson-6878 (0.050)；v1:blind-009 (0.048)；train:v2-payment-recharge-retry-codex (0.036) | 最近邻是构建配置、MFA 与幂等请求；目标是并发 channel 的背压语义。 |
| blind-v2-002 | train:v2-payment-subscription-renewal-codex (0.075)；dev:code-spec-minipair-holdout-event_dedup_window-codex-v2-two-axis (0.048)；train:candidate-swebench-ytdl-org__youtube-dl-717 (0.045) | 最近邻是支付幂等窗口；目标是 CSS 网格轨道继承。 |
| blind-v2-003 | train:candidate-swebench-ytdl-org__youtube-dl-7399 (0.059)；v1:blind-009 (0.034)；train:candidate-swebench-Lightning-AI__lightning-1100 (0.026) | 最近邻是视频下载仓库问题；目标是 Git 历史整理命令边界。 |
| blind-v2-004 | train:candidate-swebench-JohnSnowLabs__spark-nlp-13798 (0.081)；v1:blind-009 (0.050)；dev:candidate-swebench-ytdl-org__youtube-dl-5556 (0.041) | 最近邻是数组/模型管线错误；目标是 WASM 线性内存扩容后的 view 生命周期。 |
| blind-v2-005 | train:v2-webhook-crm-contact-codex (0.029)；train:candidate-swebench-ytdl-org__youtube-dl-5533 (0.029)；dev:v2-dedupe-atomic-insert-safe-default (0.017) | 最近邻是 webhook 重复事件；目标是无框架 HTML 对话框的焦点与键盘行为。 |
| blind-v2-006 | train:candidate-swebench-mesonbuild__meson-7935 (0.042)；train:v2-webhook-invoice-paid-codex (0.025)；train:v2-webhook-shipment-update-codex (0.021) | 最近邻是构建系统配置和回调处理；目标是 Android 倒计时状态保存。 |
| blind-v2-007 | dev:candidate-sharc-14f14ca7b82b0075dbad5f5c0530652fd7e345bc (0.036)；dev:candidate-sharc-8fc68ec051eea67cc3f50fdd4f45bd9aca442871 (0.036)；train:candidate-sharc-2975b0b7e54ee2d32587c4e705a3e7c4d2d1db8f (0.031) | 最近邻是 ShARC 个人请求；目标是静态帮助站离线全文检索。 |
| blind-v2-008 | train:candidate-ai-mitra-380 (0.024)；train:code-spec-minipair-holdout-webhook_dedupe-codex-v2-two-axis (0.022)；train:candidate-ai-mitra-550 (0.021) | 最近邻是 Rust 通用函数和 webhook 去重；目标是 WebVTT cue 时间校验。 |
| blind-v2-009 | train:code-spec-minipair-holdout-signed_url_expiry-codex-v2-two-axis (0.040)；v1:blind-008 (0.031)；train:candidate-ai-mitra-378 (0.023) | 最近邻是签名链接期限和报表权限；目标是浏览器时间范围控件的键盘交互。 |
| blind-v2-010 | train:candidate-ai-mitra-358 (0.029)；train:candidate-ai-mitra-302 (0.019)；train:candidate-swebench-ytdl-org__youtube-dl-3534 (0.014) | 最近邻是通用 Node.js 问答和算术文本；目标是 Three.js 星图相机控制。 |
| blind-v2-011 | v1:blind-009 (0.039)；train:code-spec-minipair-holdout-email_international-codex-v2-two-axis (0.037)；train:code-spec-minipair-holdout-webhook_dedupe-codex-v2-two-axis (0.034) | 最近邻是 MFA、邮件编码和 webhook 词面；目标是纯函数式终端进度条渲染。 |
| blind-v2-012 | train:candidate-swebench-ytdl-org__youtube-dl-613 (0.090)；train:candidate-ai-mitra-358 (0.089)；dev:v2-dedupe-courier-scan-codex (0.072) | 最近邻的 sequence 字样、Node.js 通用问答或快递事件；目标是流式 ANSI 转义序列清理。 |
| blind-v2-013 | train:candidate-sharc-727e7b7db519a6e40f41c32f183c5dc44ea4cebb (0.024)；train:candidate-sharc-17b1824627553f2278522034eb7a8bc05c8f1648 (0.019)；train:candidate-sharc-bed60c0c17b37d284070b5cd01ee5fdaed751440 (0.019) | 最近邻是 ShARC 通用福利付款问句；目标是多币种差旅报销的汇率与已付款冲销语义。 |
| blind-v2-014 | train:candidate-swebench-ytdl-org__youtube-dl-3855 (0.010)；train:candidate-swebench-mesonbuild__meson-7196 (0.010)；train:v2-permission-design-library-clarify (0.010) | 最近邻的权限题讨论用户/文件夹继承；本题讨论 CI 服务账号的部署凭证范围与撤销。 |
| blind-v2-015 | train:candidate-swebench-Lightning-AI__lightning-1192 (0.016)；dev:candidate-swebench-ytdl-org__youtube-dl-3407 (0.011)；train:candidate-ai-mitra-674 (0.011) | 最近邻是泛化速率限制或地址校验；本题针对账户恢复短信的组合计数与冷却策略。 |
| blind-v2-016 | train:candidate-sharc-5135b36df25355bd4c1f96179900ef48322403e6 (0.024)；train:candidate-swebench-Lightning-AI__lightning-1271 (0.023)；dev:candidate-ai-mitra-1552 (0.016) | 最近邻是供应商协议摘要、CSV 词面；本题针对多国合同日期的地区歧义解析与提醒后果。 |
| blind-v2-017 | train:code-spec-minipair-holdout-export_partial_file-clarify-v2-two-axis (0.046)；dev:v2-dedupe-factory-alert-codex (0.028)；train:code-spec-minipair-holdout-zip_traversal-clarify-v2-two-axis (0.023) | 最近邻是文件失败处理、ZIP 路径和告警记录；目标是跨时区重复排班的夏令时语义。 |
| blind-v2-018 | train:v2-payment-marketplace-refund-clarify (0.014)；train:candidate-swebench-ytdl-org__youtube-dl-32138 (0.013)；train:candidate-swebench-ytdl-org__youtube-dl-8703 (0.012) | 最近邻是退款和仓库问题；本题针对餐厅迟到、桌位保留和候位规则。 |
| blind-v2-019 | train:v2-payment-recharge-retry-clarify (0.020)；train:v2-payment-subscription-renewal-clarify (0.016)；train:candidate-sharc-41f1e1273e6b12218efc6a1e80fe69a08e0197f4 (0.013) | 最近邻是充值/订阅重试；本题针对学校多次补考后的成绩呈现与计分规则。 |
| blind-v2-020 | v1:blind-017 (0.033)；train:candidate-swebench-Lightning-AI__lightning-1177 (0.014)；dev:code-spec-minipair-holdout-search_tie_break-clarify-v2-two-axis (0.013) | 最近邻是 Markdown 预览器快捷键默认；本题是本地照片浏览的可逆排序默认。 |
| blind-v2-021 | train:candidate-sharc-e406df0b0cb6dc7fda9f91b62754e291adc2fd4c (0.044)；train:v2-payment-marketplace-refund-codex (0.020)；train:code-spec-minipair-holdout-export_partial_file-codex-v2-two-axis (0.016) | 最近邻是一般报名问句、退款与导出；本题是志愿者报名成功后的非阻断 toast 行为。 |
| blind-v2-022 | dev:candidate-ai-mitra-513 (0.056)；train:candidate-ai-mitra-554 (0.054)；train:candidate-ai-mitra-413 (0.051) | 最近邻是通用 Python 深拷贝、去重和缓存；本题是测试颜色样本与可复现 seed。 |
| blind-v2-023 | v1:blind-014 (0.027)；v1:blind-020 (0.022)；dev:candidate-swebench-DataDog__integrations-core-9857 (0.017) | 最近邻是 OpenAPI 扩展和后台队列约定；本题是 Godot 游戏设置与配置迁移。 |
| blind-v2-024 | v1:blind-013 (0.059)；train:v2-payment-subscription-renewal-clarify (0.056)；train:candidate-swebench-JohnSnowLabs__spark-nlp-13798 (0.046) | 最近邻是实时传输方式问答和续费 worker；本题是 Rust telemetry 指标接入仓库惯例。 |

## 冻结与红线核验

- v1 冻结金标 SHA-256：当前 `f5b572f313921a14ff7820ea8188af7a7366226ba6a5a7ad83153fae666c0b12`；冻结记录为 `f5b572f313921a14ff7820ea8188af7a7366226ba6a5a7ad83153fae666c0b12`；一致。
- 第二轮数据版本 SHA-256：`897d1266b0f2a1d7177d57150360c81c11dea70b900f5ab412bd2ea048f1cb16`；train SHA-256：`c05e18aaa2f393093a7879ffa43b3b0063e20e4edb553b8a12422b271242c3ab`；dev SHA-256：`cf03fa1583713dff2a600b5df941dc0b6c358fc4bc375ef066f45fc5f77eec82`。
- 模型文件 `artifacts/decisioner_round2_v1_2026-11-04.joblib` SHA-256：`f2e1dc659d1d9a78c3136401ba2d987e80bd836a85005530bf75e53510d2dc25`，与第二轮 manifest 记录一致；本任务未改模型。
- `light_decider/routing_policy.py` SHA-256：`e1a1107aaf29ff75482ae1ab581d9f233c19d7763bef5ceb868bd468b48e5ae3`，与本任务开始前记录一致；本任务未改策略。
- `automatic_dispatch_allowed`：`false`（第二轮数据 manifest）；保持关闭。
- 本次只新增 v2 题目工作簿、造题审计与冻结清单；未改 v1、训练/dev 数据、模型、路由策略或派发设置。
- 审计来源声明：合成生成，未人工确认；盲标完成前不得用于训练、调参、改规则或评测。
