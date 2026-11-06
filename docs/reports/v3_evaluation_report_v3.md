# blind_holdout_v3 一次性评测报告

- 评测时间：2026-11-04 20:39:11 CST
- 评测集：24 条冻结标签；本次执行一次，不重跑。
- 执行记录：首次启动因脚本导入路径错误在模型推理前退出；修复路径后正式推理执行一次。
- 标签来源：助手代填，用户 于 2026-11-04 照单全收（未修改），属于“代填 + 人工确认”，不是独立盲标；因此本报告不能称为独立盲测泛化证据。
- 冻结金标 SHA-256：`1b28daf61866153cda78fb6f7060ed084659f73b7ef1efd128e5f53dd0d1e07b`（与冻结清单一致）。
- sealed Codex 参考 SHA-256：`45d1f48ae1ac248eeeba8652c53b909bc2334d91a1ddd26143179188658e3f12`。
- round-2 模型 SHA-256：`f2e1dc659d1d9a78c3136401ba2d987e80bd836a85005530bf75e53510d2dc25`；策略版本：`v3.1`；策略文件 SHA-256：`719f88ed53635d8b69f35e52e00741b9d9b81128d7f72d99f176ddfe9902e86e`。
- 推理调用：每条样本对 round-2 模型计算一次分数；A 直接取 argmax，B 在同一次 argmax 上应用 routing_policy v3.1。未设置阈值或额外覆盖。
- 自动派发：关闭；评测只记录预测与策略结果。

## 验收线与总览

| 口径 | Clarify 召回 | Clarify→decide | 加权总代价 | 结果 |
|---|---:|---:|---:|---|
| A：round-2 argmax | 6/7 (85.7%) | 0 | 13 | 未通过 |
| B：round-2 + routing_policy v3.1 | 6/7 (85.7%) | 0 | 14 | 未通过 |

验收线：clarify 召回 ≥ 6/7；clarify→decide = 0；加权总代价 ≤ 10。权重按冻结要求计算：clarify→decide 计 10，clarify→任一 codex* 计 5，其余非完全匹配错误计 1，正确计 0。specialized codex 标签与普通 codex 作为不同五分类动作计分；另给三分类折叠结果帮助阅读模型路由能力。

## 口径 A：round-2 模型 argmax

- 五动作精确准确率：62.5%（15/24）。
- 加权代价：13（每条平均 0.542）。

### 五动作混淆矩阵

| gold \ predicted | decide | clarify | codex | codex+declare_default | codex+check_first |
|---|---:|---:|---:|---:|---:|
| decide | 3 | 1 | 2 | 0 | 0 |
| clarify | 0 | 6 | 1 | 0 | 0 |
| codex | 0 | 0 | 6 | 0 | 0 |
| codex+declare_default | 0 | 3 | 0 | 0 | 0 |
| codex+check_first | 0 | 0 | 2 | 0 | 0 |

### 五动作逐类 precision / recall

| 动作 | Precision | Recall | Support | 预测数 |
|---|---:|---:|---:|---:|
| decide | 100.0% | 50.0% | 6 | 3 |
| clarify | 60.0% | 85.7% | 7 | 10 |
| codex | 54.5% | 100.0% | 6 | 11 |
| codex+declare_default | 0.0% | 0.0% | 3 | 0 |
| codex+check_first | 0.0% | 0.0% | 2 | 0 |

### 三分类折叠混淆矩阵（codex* → codex）

| gold \ predicted | decide | clarify | codex |
|---|---:|---:|---:|
| decide | 3 | 1 | 2 |
| clarify | 0 | 6 | 1 |
| codex | 0 | 3 | 8 |


## 口径 B：round-2 模型 + routing_policy v3.1

- 五动作精确准确率：58.3%（14/24）。
- 加权代价：14（每条平均 0.583）。

### 五动作混淆矩阵

| gold \ predicted | decide | clarify | codex | codex+declare_default | codex+check_first |
|---|---:|---:|---:|---:|---:|
| decide | 3 | 1 | 2 | 0 | 0 |
| clarify | 0 | 6 | 1 | 0 | 0 |
| codex | 0 | 1 | 3 | 0 | 2 |
| codex+declare_default | 0 | 0 | 3 | 0 | 0 |
| codex+check_first | 0 | 0 | 0 | 0 | 2 |

### 五动作逐类 precision / recall

| 动作 | Precision | Recall | Support | 预测数 |
|---|---:|---:|---:|---:|
| decide | 100.0% | 50.0% | 6 | 3 |
| clarify | 75.0% | 85.7% | 7 | 8 |
| codex | 33.3% | 50.0% | 6 | 9 |
| codex+declare_default | 0.0% | 0.0% | 3 | 0 |
| codex+check_first | 50.0% | 100.0% | 2 | 4 |

### 三分类折叠混淆矩阵（codex* → codex）

| gold \ predicted | decide | clarify | codex |
|---|---:|---:|---:|
| decide | 3 | 1 | 2 |
| clarify | 0 | 6 | 1 |
| codex | 0 | 1 | 10 |


## 指定切片

decide、declare_default、check_first 的 recall 按动作子集分别统计。decide 只报告精确动作命中；对 declare_default/check_first，A 的三分类模型无法预测细分动作，因此同时列出 codex 家族路由命中与五动作精确子类命中，B 同样列出两种命中。

| 切片 | A: 精确命中 | A: codex 家族命中 | B: 精确命中 | B: codex 家族命中 |
|---|---:|---:|---:|---:|
| decide（/6） | 3/6 (50.0%) | — | 3/6 (50.0%) | — |
| codex+declare_default（/3） | 0/3 (0.0%) | 0/3 (0.0%) | 0/3 (0.0%) | 3/3 (100.0%) |
| codex+check_first（/2） | 0/2 (0.0%) | 2/2 (100.0%) | 2/2 (100.0%) | 2/2 (100.0%) |

### 高危域样本（5 条）

| ID | 标注高危域 | 金标 | A argmax | A 对错 | B 最终动作 | B 对错 | 策略检测域 |
|---|---|---|---|---|---|---|---|
| blind-v3-002 | permission | clarify | clarify | 对 | clarify | 对 | permission |
| blind-v3-006 | rate_limiting | clarify | clarify | 对 | clarify | 对 |  |
| blind-v3-009 | locale_sensitive_parsing | clarify | clarify | 对 | clarify | 对 |  |
| blind-v3-015 | payment | clarify | clarify | 对 | clarify | 对 | payment |
| blind-v3-018 | deduplication | clarify | codex | 错 | clarify | 对 | deduplication |

## 策略翻转清单

A 为 argmax 基线，没有策略翻转。B 仅将实际发生的动作变化列为翻转；被安全保护阻止的 override 单独列出。

| ID | argmax → 最终动作 | 规则名 |
|---|---|---|
| blind-v3-003 | codex → clarify | locale_sensitive_value_format_ambiguous |
| blind-v3-004 | clarify → codex | explicit_implementation_request |
| blind-v3-005 | codex → codex+check_first | existing_project_convention_check |
| blind-v3-010 | clarify → codex | explicit_implementation_request |
| blind-v3-012 | clarify → codex | explicit_implementation_request |
| blind-v3-014 | codex → codex+check_first | existing_project_convention_check |
| blind-v3-016 | codex → codex+check_first | existing_project_convention_check |
| blind-v3-017 | clarify → codex | explicit_implementation_request |
| blind-v3-018 | codex → clarify | explicit_key_choice_question |
| blind-v3-019 | codex → codex+check_first | existing_project_convention_check |

### 被阻止的策略覆盖

| ID | 当前动作 | 提议动作 | 规则名 | 阻止原因 |
|---|---|---|---|---|
| 无 | — | — | — | — |

## 三方对照与一致率

- 金标 vs Codex 参考：五动作精确一致 24/24（100.0%）；折叠到 decide/clarify/codex 后一致 24/24（100.0%）。
- 金标、Codex 参考、A argmax 三方五动作完全一致：15/24（62.5%）；三分类折叠一致：17/24（70.8%）。
- 金标、Codex 参考、B 最终动作三方五动作完全一致：14/24（58.3%）；三分类折叠一致：19/24（79.2%）。

## 逐条对照表

分数列为模型三类原始分数（未校准）。高危列左侧是冻结标签，右侧是策略从文本识别到的域。

| ID | 请求原文 | 金标 | Codex参考 | Argmax（分数） | B最终动作 | A命中 | B命中 | 高危标注 / 策略检测 | 翻转规则 |
|---|---|---|---|---|---|---|---|---|---|
| blind-v3-001 | 偏振光是什么？太阳镜怎样利用偏振减少水面或玻璃反光？ | decide | decide | decide (clarify=0.176, codex=0.166, decide=0.658) | decide | ✓ | ✓ | 无 / 无 | — |
| blind-v3-002 | 给新建的医疗影像标注平台安排放射科医生和质控人员的记录可见范围。医生能否看到全部影像、质控人员能否导出原图、成员调岗后已保存副本如何处理？请接入权限控制。 | clarify | clarify | clarify (clarify=0.466, codex=0.314, decide=0.221) | clarify | ✓ | ✓ | permission / permission | — |
| blind-v3-003 | 请用 Python 3.12 写一个只依赖标准库的 `gpx_summary.py` 命令行工具。输入一个 GPX 1.1 文件，遍历每个 track segment；仅在同一 segment 内相邻点之间累加 Haversine 距离，地球半径固定为 6,371,008.8 米。输出 JSON，包含 `point_count`、`distance_m`、`ascent_m`、`descent_m`；后三个距离值按四舍五入到整数，恰好 `.5` 时向上。爬升/下降只统计两个相邻点都带 `<ele>` 的情况，缺失高程不跨点补算。任一轨迹点的 lat/lon 缺失、非数值或超出合法范围，或 XML 不合法时，向 stderr 只输出 `invalid GPX` 并退出 2；成功退出 0。 | codex | codex | codex (clarify=0.194, codex=0.633, decide=0.173) | clarify | ✓ | ✗ | 无 / locale_sensitive_parsing | locale_sensitive_value_format_ambiguous |
| blind-v3-004 | 给新建的展品图鉴页安排卡片标题的默认字号和行距，请凭排版直觉替我拍板；访客可在显示设置里调整，藏品字段本身不动。 | codex+declare_default | codex+declare_default | clarify (clarify=0.437, codex=0.361, decide=0.202) | codex | ✗ | ✗ | 无 / 无 | explicit_implementation_request |
| blind-v3-005 | 在现有 Firefox/Chromium 扩展中加入保存和恢复命名标签组的功能。请先检查标签标识方式、同步与本地存储的分工，以及选项页配置迁移做法；沿用一致的仓库约定实现，若找不到统一做法或发现冲突先停下问我。 | codex+check_first | codex+check_first | codex (clarify=0.330, codex=0.482, decide=0.188) | codex+check_first | ✗ | ✓ | 无 / 无 | existing_project_convention_check |
| blind-v3-006 | 给市立图书馆的自助借还终端限制二维码扫描请求：按会员、终端还是网络地址计数？识别失败的扫描算不算一次？达到阈值后锁多久？请把限制接上。 | clarify | clarify | clarify (clarify=0.452, codex=0.315, decide=0.233) | clarify | ✓ | ✓ | rate_limiting / 无 | — |
| blind-v3-007 | 幸存者偏差会怎样扭曲我们对成功概率的判断？ | decide | decide | clarify (clarify=0.384, codex=0.257, decide=0.359) | clarify | ✗ | ✗ | 无 / 无 | — |
| blind-v3-008 | 请用原生 HTML/CSS/JavaScript 做 9×9 数独盘。输入 `puzzle` 是 81 位字符串，只含 1–9 和 `.`；数字是锁定线索，`.` 为空格。点击格子后输入 1–9 填值；Backspace/Delete 清空可编辑格；方向键移动焦点并在边界停住。仅检查玩家填写的数字：同行、同列或同一 3×3 宫重复时，将所有冲突的填写格标红；冲突消除后立即去红。所有格填满且全盘无重复时触发一次 `complete` 自定义事件。锁定格不可修改；不自动求解、不保存、不访问网络。 | codex | codex | codex (clarify=0.261, codex=0.555, decide=0.184) | codex | ✓ | ✓ | 无 / permission | — |
| blind-v3-009 | 给国际青少年帆船赛的报名核验服务读取选手证件出生日期。不同国家的证件可能使用地区数字或当地纪年，印刷日期与机读区也可能不一致。年龄组资格要依据哪一处日期、先转换成哪种历法、冲突时如何处理？请接入解析。 | clarify | clarify | clarify (clarify=0.437, codex=0.260, decide=0.304) | clarify | ✓ | ✓ | locale_sensitive_parsing / 无 | — |
| blind-v3-010 | 给新建的词汇练习网页加答题反馈动效。动画节奏和呈现细节请按不打断阅读的感觉代我拿主意；用户之后可以关闭动效，答案判定和学习记录都不受影响。 | codex+declare_default | codex+declare_default | clarify (clarify=0.494, codex=0.294, decide=0.212) | codex | ✗ | ✗ | 无 / 无 | explicit_implementation_request |
| blind-v3-011 | 为一个全新的前端页面做两栏文本编辑器：左侧是多行输入框，右侧实时显示等宽纯文本预览；分隔条默认占总宽度 55%，拖动时限制在 25% 到 75%；双击恢复 55%；分隔条获得焦点后左右键每次调整 1%，Shift+方向键调整 10%；用 `role=separator` 和 `aria-valuenow` 暴露当前比例；不保存宽度设置，调整布局不能改动输入内容。 | codex | codex | codex (clarify=0.326, codex=0.414, decide=0.260) | codex | ✓ | ✓ | 无 / 无 | — |
| blind-v3-012 | 从零做大学社团排练室预约功能。课程教学和学生社团同时申请时谁优先？是否给高年级社团保留名额？临时取消、爽约和候补递补各按什么校规处理？请把预约流程实现。 | clarify | clarify | clarify (clarify=0.410, codex=0.299, decide=0.292) | codex | ✓ | ✗ | 无 / 无 | explicit_implementation_request |
| blind-v3-013 | 小样本数据里，为什么中位数有时比平均数更能代表‘典型值’？ | decide | decide | codex (clarify=0.265, codex=0.422, decide=0.312) | codex | ✗ | ✗ | 无 / 无 | — |
| blind-v3-014 | 在现有 TypeScript 在线国际象棋项目的 `GameSummary` 页面加单局 PGN 导出按钮。只导出当前棋局，文件 UTF-8 编码；依次写 Event=`Casual`、Site=`?`、UTC 完局日期（`YYYY.MM.DD`）、双方名称和结果标签；棋步使用状态中的 SAN 列表并按标准回合编号；不带注释或变化分支；文件名 `game-<id>.pgn`；结果未结束时按钮禁用；标签值按 PGN 规则转义双引号和反斜杠；不改棋局记录。当前状态已提供 id、日期、双方、结果和 SAN 列表。 | codex | codex | codex (clarify=0.239, codex=0.618, decide=0.143) | codex+check_first | ✓ | ✗ | 无 / 无 | existing_project_convention_check |
| blind-v3-015 | 给新建的陶艺课程报名网站接入定金结算。学员开课前取消、主办方取消、改期后学员不接受时分别扣多少或退多少？支付手续费是否返还？请把结算流程实现。 | clarify | clarify | clarify (clarify=0.480, codex=0.236, decide=0.284) | clarify | ✓ | ✓ | payment / payment | — |
| blind-v3-016 | 在现有 JavaFX 流程图编辑器中增加连接线自动吸附到图形锚点。请先查看节点锚点的数据结构、拖动时的吸附反馈、撤销命令和文件序列化约定，按一致的仓库实现；若找不到一致规则，再停下来问我。 | codex+check_first | codex+check_first | codex (clarify=0.382, codex=0.422, decide=0.196) | codex+check_first | ✗ | ✓ | 无 / 无 | existing_project_convention_check |
| blind-v3-017 | 给新建的本地舞蹈教学播放器加播放倍率控制。首次打开的默认倍率请按看动作自然流畅的感觉替我选一个；用户可随时切回 1× 或调整，原视频和字幕不做修改。 | codex+declare_default | codex+declare_default | clarify (clarify=0.450, codex=0.330, decide=0.220) | codex | ✗ | ✗ | 无 / 无 | explicit_implementation_request |
| blind-v3-018 | 给新建的学术文献库接入多个目录源。预印本、online-first 和正式刊载版本可能标题相近但 DOI 不同；按 DOI、作者与标题相似度还是版本关系去重？合并后哪些来源字段要保留？请实现导入。 | clarify | clarify | codex (clarify=0.410, codex=0.414, decide=0.176) | clarify | ✗ | ✓ | deduplication / deduplication | explicit_key_choice_question |
| blind-v3-019 | 在现有 Electron 音频剪辑器的 `TimelinePanel` 加片段边缘吸附：拖动片段边界时只吸附其他片段的起止点，阈值为屏幕 8 CSS px；取像素距离最近者，平局按较早时间、再按 clip ID 字典序；按住 Alt 暂停吸附；拖动中显示吸附线，松开鼠标才提交一次状态变更和一次撤销记录；音频内容不重采样。 | codex | codex | codex (clarify=0.328, codex=0.490, decide=0.182) | codex+check_first | ✓ | ✗ | 无 / 无 | existing_project_convention_check |
| blind-v3-020 | 老城区想降低夏季地表温度：树冠遮荫与浅色屋顶分别通过什么途径减少热量？适合优先布置在哪类空间？ | decide | decide | decide (clarify=0.294, codex=0.278, decide=0.428) | decide | ✓ | ✓ | 无 / 无 | — |
| blind-v3-021 | 从零给手工品交易平台增加商家差评申诉流程。哪些评价可以申诉、要什么证据、商家多久内可回复、审核时是否暂时隐藏评价都按什么平台规则？请把流程接上。 | clarify | clarify | clarify (clarify=0.404, codex=0.238, decide=0.358) | clarify | ✓ | ✓ | 无 / 无 | — |
| blind-v3-022 | 在 Go 1.22 模块里实现 `BlendRGBA(a, b color.RGBA, t float64) color.RGBA`。四个 8 位通道分别按 `a+(b-a)*t` 线性插值；t 小于 0 视为 0、大于 1 视为 1；用 `math.Round` 舍入；NaN 返回 a，正无穷返回 b，负无穷返回 a；不修改输入。 | codex | codex | codex (clarify=0.228, codex=0.568, decide=0.204) | codex | ✓ | ✓ | 无 / 无 | — |
| blind-v3-023 | 为什么海拔越高，水常常在低于 100℃ 时就会沸腾？ | decide | decide | codex (clarify=0.262, codex=0.378, decide=0.359) | codex | ✗ | ✗ | 无 / 无 | — |
| blind-v3-024 | 地图上的等高线挤得很近和相隔很远，各自说明地形有什么特点？ | decide | decide | decide (clarify=0.317, codex=0.275, decide=0.408) | decide | ✓ | ✓ | 无 / 无 | — |

## 数据说明

sealed Codex 参考中 blind-v3-001 的 rationale 描述与题目内容看起来不匹配（题目讨论偏振光与太阳镜，rationale 却提到天文学）；本报告未改动参考标签或参考文件，三方一致率只比较 action 字段。

## 纪律记录

本报告只记录一次性评测。没有改动冻结标签、模型、策略、阈值或训练数据；没有将 v3 样本用于调参、补规则或训练。若任一口径未过线，按任务要求停在报告，不自动开展修复。
