# light_decider 盲测集 v4 生成报告

**题目文件：** blind_holdout_v4_unlabeled.xlsx  
**状态：** 合成生成、未标注。本单只造题，不读取模型或策略输出，不运行模型、策略或评测。  
**生成日期：** 2026-11-05（Asia/Shanghai）  
**题目文件 SHA-256（生成记录）：** a371ca92a9083c226b833b45e2b72a3fb33a42727af01f80f66b060899cc15d1

## 构成分组

| 题目设计组 | 数量 |
|---|---:|
| 纯概念、解释与比较问题 | 6 |
| 规格自足的实现请求 | 6 |
| 关键语义未定的实现请求 | 7 |
| 低风险、可逆默认的授权请求 | 3 |
| 依赖现有代码库约定的请求 | 2 |
| **合计** | **24** |

题目经固定随机种子打乱后编号，类别没有连续分组。三条低风险授权使用不同的新措辞，分别位于请求前部、中部和末尾；与两批候选表授权措辞的精确复用数为 0。两条项目约定请求均未出现“请先检查”。

高危域覆盖计数：

| 覆盖域 | 数量 |
|---|---:|
| payment | 1 |
| permission | 1 |
| rate_limiting | 1 |
| locale_sensitive_parsing | 1 |
| deduplication | 1 |

## 场景家族

| 样本编号 | 场景家族 |
|---|---|
| blind-v4-001 | 生产活动负外部性解释 |
| blind-v4-002 | 铁路曲线轨道超高原理 |
| blind-v4-003 | 水利实验站水样检测预约资格政策 |
| blind-v4-004 | 跨国设备保修登记税号地区格式解析 |
| blind-v4-005 | 雷达与激光远距离测距原理比较 |
| blind-v4-006 | Python 光谱数据分箱摘要工具 |
| blind-v4-007 | 山地风洞试验预热流程 |
| blind-v4-008 | MATLAB 重复测量均值与误差带绘图 |
| blind-v4-009 | 纺织质检重复缺陷记录合并 |
| blind-v4-010 | 玄武岩薄片查看器默认图像叠层 |
| blind-v4-011 | 供水压力传感器接口限流边界 |
| blind-v4-012 | 树木年轮信息与推断边界 |
| blind-v4-013 | Rust 半开区间包含判断函数 |
| blind-v4-014 | 桥梁巡检档案外部顾问访问权限 |
| blind-v4-015 | 海上风机检修承包商分阶段结算 |
| blind-v4-016 | 合成材料批次撤销审计流程 |
| blind-v4-017 | 语言学音位与具体语音的区别 |
| blind-v4-018 | 业余气象观测员协会认证资格与补交期限 |
| blind-v4-019 | 生态学环境容纳量概念 |
| blind-v4-020 | TypeScript 单次上升区间定位 |
| blind-v4-021 | C# WPF 公式编辑器行号开关 |
| blind-v4-022 | 玻璃窑炉日志页默认时间窗口 |
| blind-v4-023 | C++ uint64 下取整整数平方根函数 |
| blind-v4-024 | 南极冰芯数据浏览器默认首页 |

本套共 24 个不同场景家族。与 round-3 train 及两批候选表可读家族标签的规范化精确重合为 0 条；v3 明确排除的九类家族重合为 0 条。round-3 train 的 704 条请求文本另做全量近邻筛查，并按主体对象、用户目标及核心操作逐项复核。

## 避撞方法与结果

对照文本仅用于避撞，不读取标签、模型分数或策略输出。先将请求文本转小写、折叠空白并剥除标点，检查规范化全文重复；再对字符 2–4 gram 集合计算 Jaccard。0.12 作为人工复核线，达到或超过阈值的题对逐项核查。另按主体对象、用户目标和核心操作检查场景家族，并单独排查 v3 指定的九个排除家族。

| 对照组 | 对照行数 | 最高相似度 | 新题编号 | 最近邻编号 | ≥0.12 对数 | 全文重复数 |
|---|---:|---:|---|---|---:|---:|
| v1_v2_v3_72 | 72 | 0.0804 | blind-v4-006 | blind-v3-003 | 0 | 0 |
| round3_train_704 | 704 | 0.0640 | blind-v4-006 | rare-cf-fullspec-01 | 0 | 0 |
| candidate_main_160 | 160 | 0.0640 | blind-v4-006 | rare-cf-fullspec-01 | 0 | 0 |
| candidate_supplement_28 | 28 | 0.0278 | blind-v4-018 | rare-supp-187 | 0 | 0 |
| v4 内部题对 | 276 | 0.0389 | blind-v4-013 | blind-v4-023 | 0 | 0 |

跨来源规范化全文重复总数：**0**；跨来源达到或超过 0.12 的题对：**0**；v4 内部达到线的题对：**0**。

### 避撞参照文件

| 文件 | SHA-256 |
|---|---|
| data/light_decider_independent_blind_holdout_v1.csv | 9d065f614126c82b0edd8e149c30b4b641e2748f12ab6c9d86db073036eef41b |
| data/light_decider_independent_blind_holdout_v2_2026-11-04/blind_holdout_v2_unlabeled.xlsx | 64540d63b22aa9a1c833e2fcd51231dc0b972e287db2d5fb14243baa7e6d6729 |
| outputs/01a195cc-5dff-7e70-9e28-5298d354d8cf/blind_holdout_v3_unlabeled.xlsx | 5aa469c024c23374cb2bde8b433b20ebf91d39d6cae97f56c89708937d15d39d |
| data/training_round3_v1_2026-11-05/train.jsonl | 3193e331bb1fe824a31418717ad5e929fbbd431b2174f78c5c3655cd3cdcb5b6 |
| outputs/rare_class_candidates_2026-11-04/rare_class_candidates.xlsx | 15632f984c282c58af028ac501b771927986ba35f2df7024a6621c27045f9028 |
| outputs/rare_class_candidates_2026-11-04/rare_class_candidates_supplement.xlsx | 045c76568dabaa76d9e79af1c0799e210611a1d5c56d29cfa4e1b1e87c8308f8 |

## 未标注与隔离

- 工作簿沿用 v3 未标注版的八列结构：sample_id、请求文本、补充上下文、缺失关键规格、存在安全默认、高危域、最终动作、备注。
- 仅样本编号和请求原文有值；补充上下文及 D–H 标注列的 24 行均为空。工作簿不含样本级动作、两轴或高危标签。
- v1/v2/v3 题目、round-3 train、两批候选工作簿均只读；没有更改任何现有文件。
- 本单未打开策略、模型文件或 sealed reference；未运行模型、策略或评测；未训练或改规则。
