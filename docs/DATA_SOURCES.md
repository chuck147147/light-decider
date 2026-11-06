# 公开决策器数据集调研

调研日期：2026-11-02

## 结论

公开数据可以让我们不从零编写所有输入，但目前没有找到一个标签正好等于本项目 `decide / codex / clarify` 的可靠中文数据集。现成数据主要分成两类：

1. **请求路由数据**：把提示词分到代码、简单问答、复杂推理或模型档位；和本项目接近，但通常没有“需要追问”标签。
2. **Jev 式结构化决策数据**：给定状态、问题和候选选项，预测正确选项；适合学习决策格式，但候选项与任务类型各不相同，不能直接当作本项目的三类路由标签。

因此，不应把公开数据未经转换就塞进 `data/annotations.jsonl`。它们适合提供种子输入、决策格式和评估方法；本项目的目标标签仍要按统一规则转换并复核。

## 候选来源

| 数据集 | 规模与内容 | 对本项目的用途 | 主要限制 |
|---|---|---|---|
| [GhostScientist/jev-decisions-v1](https://huggingface.co/datasets/GhostScientist/jev-decisions-v1) | 约 9,100 条；英文；`state + question + options + answer_key`；包含约 300 条 assistant-mode routing 和约 300 条 support-intent routing；数据卡声明 Apache-2.0。 | 可参考 Jev 式结构化决策输入，也可抽少量样本做格式/鲁棒性实验。 | `answer_key` 的候选项属于各自任务域；assistant-mode 与客服能力标签不等于 `decide/codex/clarify`。不能直接把答案映射成当前三路标签。大部分路由子集是合成数据。 |
| [OpenAGILab/Jev-dataset](https://huggingface.co/datasets/OpenAGILab/Jev-dataset) | 多种固定选项、概率和评分决策；数据卡声明 CC0；包含英文、中文、土耳其语；公开配置中有约 11.4 万条。 | 适合研究如何表达候选项、目标分布、校准集和 OOD 切分；中文邮件/客服分类部分可能提供少量种子输入。 | 以受控、合成任务为主；不是官方 Jev 训练集，也不是本项目的三路路由数据。需按第三方声明核对具体配置的来源与再分发条件。 |
| [ai-mitra/llm-router-dataset](https://huggingface.co/datasets/ai-mitra/llm-router-dataset) | 约 1,700 条英文提示词，5 类：simple、coding、reasoning、security、summarization；MIT；每类含少量手写和大量模板生成样本。 | coding 可作为 `codex` 的候选种子；简单问答/摘要可作为 `decide` 候选种子。 | 没有追问标签；security/reasoning 不能直接映射成 `clarify`；模板生成的措辞分布较窄。 |
| [somukandula/prompt-router-dataset](https://huggingface.co/datasets/somukandula/prompt-router-dataset) | 约 1,900 条英文合成提示词，分为轻量文本、代码、视觉、强通用模型四档；MIT。 | 适合做 prompt-router 分类基线和 hard-negative 案例参考。 | 预测模型档位，不判断是否追问；代码、模型档位与本项目目标不完全对应。 |
| [SWE-bench](https://huggingface.co/datasets/princeton-nlp/SWE-bench) | 官方卡片列出 19,008 条 train issue tasks；字段包括 `problem_statement`、`repo` 和解决该问题的补丁。 | 只取 train 中的问题说明和仓库名，可稳定映射到 `codex`。 | 主要是英文 GitHub issue；训练输入不要包含 `patch` 或测试补丁。HF 数据卡未填 license 字段，但上游 SWE-bench README 声明 MIT；保留 issue 来源信息。 |
| [SWE-bench Verified](https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified) | 官方 test split 有 500 条工程师验证可解的 GitHub 仓库问题；英文；上游项目声明 MIT。 | 独立的 Codex-only 来源评测；只使用 `problem_statement` 与 `repo`，不读 patch、测试补丁或 hints。 | 不是中文用户请求；机器翻译误差明显，且全部都是 Codex，不能衡量三路准确率；只保留为探索性来源评测，不训练。 |
| [ShARC](https://sharc-data.github.io/data.html) | 带规则文本、用户场景和对话历史的问答；系统需要在追问和直接回答之间选择；CC BY-SA 3.0。 | 最接近 `decide` 与 `clarify` 的带上下文样例，可把“输出追问”标成 `clarify`、“输出结论”标成 `decide`。 | 仅限规则问答场景，英文；不含 Codex 路由。使用或再分发要遵守署名和相同方式共享条件。 |
| [HumanEvalComm](https://huggingface.co/datasets/jie-jw-wu/HumanEvalComm) / [上游 HumanEval](https://github.com/openai/human-eval) | 164 道 Python HumanEval 编程题及作者核验的歧义、矛盾、不完整改写；数据卡声明 Apache-2.0，上游 HumanEval 声明 MIT。 | 原始题弱映射为 `codex`，三类改写弱映射为 `clarify`，可独立诊断“代码任务里何时应该先追问”。 | 英文原文经机翻，代码签名和 doctest 保留；不是原生路由标签，没有 `decide`；旧基准可能与预训练语料重叠。仅作开发评测，不用于训练。 |
| [Chinese-Ambiguous-Reference](https://github.com/ygan/Chinese-Ambiguous-Reference) | 1,104 条中文消费服务对话，仓库提供逐句客服策略标注并声明 MIT。 | 可提供真实中文客服上下文，帮助检查澄清边界与短回复。 | 原标注描述客服策略，不是本项目路由标签；仓库示例与部分策略代码存在不一致。本项目只做了弱映射，限消费服务域且没有 Codex 类；不能视为通用中文路由标签。 |
| [CrossWOZ](https://github.com/thu-coai/CrossWOZ) | 约 6,000 段中文任务型对话，覆盖景点、餐馆、酒店、地铁和出租车；提供用户/系统对话行为与状态标注。论文声明语料 CC BY 4.0，仓库另含 Apache-2.0 LICENSE。 | 官方 test split 可做中文多轮信息查询的 `decide` 来源评测。 | 系统侧没有可用的显式 `Request` 追问样本，不能生成 `clarify` 或 `codex`；按下一条系统 `Inform` 映射的 `decide` 标签是弱代理，只适合单类领域评测，不进三路训练。 |
| [PolyDevTasks](https://huggingface.co/datasets/Mxode/PolyDevTasks-Chinese_English_German) | 38 万余条中、英、德软件开发任务；中文部分约 14.4 万条，覆盖 8 种语言。 | 内容可能补充中文开发代理任务的 `codex` 种子。 | Hugging Face 许可元数据标为 CC BY-NC 4.0，但数据卡正文写 CC BY-SA 4.0；许可声明冲突，当前不下载、不导入。 |
| [ClariQ](https://github.com/aliannejadi/ClariQ) | 对话式搜索请求；`clarification_need` 是 1–4 分，另有候选澄清问题和用户回答；包含单轮及合成多轮。 | 可研究“何时追问”与“问什么”；能给 `clarify` 路线提供弱监督。 | 主要针对搜索意图歧义，不等同于一般助手任务；官方仓库页面未找到明确许可声明，确认许可前不导入或再分发。 |
| [ClarQ](https://github.com/vaibhav4595/ClarQ) | 约 200 万条 Stack Exchange 帖子与候选澄清问题；CC BY 4.0。 | 后续如要训练追问句生成，可作为候选语料。 | 目标是辨认/生成澄清问题，不是三路路由；帖子评论语体和聊天指令差异较大。 |
| [RouterBench 数据集](https://huggingface.co/datasets/withmartian/routerbench) / [代码](https://github.com/withmartian/routerbench) | 数据卡称有 3 万多个提示词、11 个模型的回答、成本和表现分数；总计约 1.47 GB，文件是 pickle。代码仓库为 MIT。 | 可研究第二阶段“选便宜模型还是强模型”的监督信号和质量/成本评测。 | HF 数据卡没有明确显示数据许可；pickle 不应在未核验来源和内容前直接反序列化。数据主要是英文基准，也不能代表中文用户分布。 |
| [RouteLLM](https://github.com/lm-sys/RouteLLM) | 强/弱模型路由的服务与评测框架；仓库提供已训练路由器，按成本阈值在模型档位间选择；代码为 Apache-2.0。 | 借鉴强弱模型配对、阈值校准、质量与成本的评测方式；适合作为第二阶段路由设计参考。 | 它是框架和模型选择任务，不是本项目三路动作标签数据集。若使用其偏好数据，需单独核对数据访问与使用条件。 |
| [Chatbot Arena conversations](https://huggingface.co/datasets/lmsys/chatbot_arena_conversations) | RouteLLM 所用的人类偏好数据来源之一；约 3.3 万条双模型对比对话，含 96 种语言、用户投票和语言标记。用户提示词许可为 CC BY 4.0，模型输出为 CC BY-NC 4.0；访问前必须接受 HF 数据集条件。 | 如果筛出中文提示词，并固定一组便宜/强模型，可从偏好票生成第二阶段的 `cheap / strong` 标签。 | 需接受数据条件；数据含不安全或冒犯内容，需要过滤；模型输出有非商业许可；数据不含本项目所需的统一价格表，成本需另行维护。 |
| [s1-llm-auto-router](https://huggingface.co/system1models/s1-llm-auto-router) | MIT 许可的轻量 CPU 路由模型；模型卡描述其训练使用约 3.9 万条合成请求和固定的 7 组判断字段。 | 参考轻量模型的固定 schema、软标签、分组切分和校准方式。 | 模型卡说明了数据构造方法，但对应组织目前没有公开训练数据集；其七个字段也不是本项目的三类动作。 |

## 推荐用法

### Jev-Decisions、RouterBench、RouteLLM 的接入结论

这三项都纳入项目的**数据/方法参考清单**，但暂不混进当前 `decide / codex / clarify` 主训练文件。它们回答的问题不同：Jev-Decisions 预测任务给定选项中的答案；RouterBench 和 RouteLLM 选择回答请求的模型档位。Jev 数据卡展示的字段是 `state`、`question`、`options`、`answer_key`；RouterBench 数据卡称其含 3 万多个提示词和 11 个模型的回答、成本及表现结果，文件总计约 1.47 GB；RouteLLM 则按阈值在强模型和弱模型之间路由。[Jev-Decisions 数据卡](https://huggingface.co/datasets/GhostScientist/jev-decisions-v1) · [RouterBench 数据卡](https://huggingface.co/datasets/withmartian/routerbench) · [RouteLLM](https://github.com/lm-sys/RouteLLM)

建议保留两层任务定义：

1. **第一层：动作路由器**，继续预测 `clarify / codex / decide`。当前默认是 BGE 小型中文语义分类器的 ONNX INT8 版本，字符 n-gram TF-IDF + Logistic Regression 保留作更小基线；训练数据只使用含义能按统一规则映射到这三类的样本。三项新来源不直接提供这组标签，因此不加到 `data/annotations.jsonl` 或现有候选集。
2. **第二层：模型档位路由器（可选）**，仅在第一层选出 `decide` 后，再选择“便宜模型 / 强模型”。RouterBench 可以从离线回答表现和成本按预先固定的门槛生成标签；Chatbot Arena 可以对固定模型对用人类偏好票生成标签，再用 RouteLLM 的阈值思路控制强模型调用比例。推理时只可使用用户提示词及允许的上下文，不能把模型答案、投票、评测分数或成本字段当作输入特征，否则会发生标签泄漏。

对于本项目“轻量、快速”的要求，第二层先用同一类 TF-IDF + Logistic Regression 基线即可，不要因此微调大语言模型。按提示词/对话分组切分训练和验证集，报告质量约束下的成本节省、两档模型的误路由率和推理延迟。RouterBench 的文件体积较大且以 pickle 提供，当前没有导入；先核对数据许可、文件结构与安全读取方式。Chatbot Arena 需接受数据条件、过滤不安全样本，并遵守其分字段许可。Jev-Decisions 则先只用于输入格式参考或独立小型格式测试；若要把它转成三路训练样本，必须从原始 `state` 和问题重新判断标签并记录为重新标注，不能沿用其 `answer_key`。

所以当前阶段的处理是：**加入研究方案和第二阶段设计，不导入主训练数据，也不改动现有三分类标签。**

### 如果先做本项目的三路 router

首批候选样本建议用两组：

1. **`ShARC` 的成对样本**：同一规则和问题，一条缺少关键个人信息而要求追问，另一条提供了该信息、可直接作答。它能教模型识别“缺信息”这条边界。
2. **`SWE-bench` 的 train 问题说明**：只使用 `problem_statement` 和 `repo`，标成 `codex`；不使用答案补丁或测试补丁。保留官方 train/dev/test 划分，不能把官方 test 放入训练。

`ClariQ` 可用于追问边界的参考；`ai-mitra` 可用作少量补充样本，但它的 coding 类也包含无需仓库操作的代码问答，必须逐条筛选。所有来源都要保留来源 ID 和领域标记，不要直接拼成一个未经检查的训练集：

- 明确需要修改代码、文件或仓库的请求，可以复核后映射为 `codex`。
- 不需要工具、上层助手可以直接处理的请求，可以复核后映射为 `decide`。
- `clarify` 需要另外构造：从一个原本明确的请求中移除必要条件或上下文，再由人确认缺失信息确实会阻止处理。
- `ShARC` 的追问是特定规则问答里的澄清；映射到通用助手路由前，需检查它是否能代表“缺信息所以要问”，而非只是该数据集的问答流程要求。

首批建议做一个小型中文试验集：每条保留原始英文请求、中文改写、来源 ID、原标签、新路由标签、改写/标注方式。训练、验证和测试应按原始模板或来源分组，避免同一个模板的变体分到两边。所有自动改写或自动映射的样本先标成未审核，复核后才能训练。

### 如果目标是训练真正通用的 Jev 式决策模型

项目输入格式要改为 `state + question + options`，输出候选选项和概率；这和当前固定三路分类器是不同的训练目标。可以先用 Jev 式数据集的格式做小范围实验，再选适合的紧凑语言模型；不要把当前三路分类模型称为通用 Jev 复刻。

## 当前项目状态

各轮训练的内部验证样本数和来源不同，宏 F1 不能脱离划分直接排名；相同文件上的来源评测可用于对照，但领域弱标签与机翻仍限制其代表性。

最初生成的 `data/candidates.jsonl` 共 600 条候选：ShARC 200 条、AI-Mitra 300 条、SWE-bench 100 条。原始拟议标签为 `decide` 300、`codex` 200、`clarify` 100；之后经路线筛选和机翻生成 `data/training_candidates_zh.jsonl`，已用于基线及语义模型的实验训练。它们仍未经过用户人工审核，弱映射和机翻不能视作人工真值。原始来源、转换规则与抽样记录见 `data/candidates.manifest.json`，当前训练统计见 `data/training_report.md`。

当前实验保留草稿状态并按对话/来源分组评估，同时补充中文上下文样本。RouterBench、RouteLLM 和 Jev 式数据仍只作为路由评测或决策格式参考，不混入这组三分类训练候选。

另已从 ShARC 官方 dev 划分生成 `data/sharc_dev_source_eval_zh.jsonl`，按对话树抽取 60 条并机翻为中文；该数据未用于训练。默认模型为 37/60（61.7%），当前较均衡候选为 46/60（76.7%），提升主要在 `decide`；它只覆盖 `decide / clarify`，标签来自规则问答且存在翻译限制。该集已用于候选比较，不再是未触碰盲测，详见 `data/sharc_dev_candidate_comparison_20261103/summary.md`。

此外从 ShARC 官方 train 的 300 棵新对话树生成了 `data/sharc_train_augmentation_zh.jsonl`，用于实验性来源扩充。与原 600 条候选合训后，内部来源分组宏 F1 为 0.854，低于默认模型的 0.897，因此没有启用；扩充数据全部保留为未人工审核草稿。

本轮新增 Chinese-Ambiguous-Reference 来源：去重 41 段重复对话、过滤 18 段含个人信息信号的对话，并剥离日期、地点、店铺和商品背景；生成 800 条平衡训练候选及 300 条按对话组留出的弱标签样本。训练候选需显式使用 `--include-weak-source-drafts`，默认不会读取。候选在新来源留出上的准确率由 61.3% 提高到 78.7%，但混合来源内部宏 F1 从 0.897 降到 0.846；它不替换默认模型。数据映射、过滤和命令见 `data/README.md` 与 `data/training_report.md`。

另从 CrossWOZ 官方 test split 抽取 500 条、每段对话最多一条的中文多轮信息查询，生成 `data/crosswoz_test_decide_eval_zh.jsonl`。标签只覆盖 `decide`，由用户 `Request` 后接系统 `Inform` 的策略弱映射得到，不能视作人工真值或三类总准确率。默认模型为 331/500（66.2%），Chinese-Ambiguous-Reference 候选为 428/500（85.6%）；该集合用于候选比较，现标作来源开发/选型集。CrossWOZ 不用于训练。评测和许可说明见 `data/crosswoz_source_eval_summary.md`。

此外从 SWE-bench Verified 官方 test 的 500 条任务生成 497 条 Codex-only 中文机翻评测，3 条命中明确联系方式模式的样本被排除。默认模型 Codex 召回为 416/497（83.7%），CAR 候选为 396/497（79.7%）；输入机翻质量不稳定、来源全为仓库修复任务，因此只作探索性来源信号。该数据没有用于训练，候选在这组任务上的 Codex 召回低于默认版；完整限制见 `data/swe_bench_verified_source_eval_summary.md`。

### 新增 SWE-bench Codex 候选

从 SWE-bench 官方 train 划分额外生成 300 条 Codex 弱标签机翻草稿，显式排除历史训练过的 issue ID 与 Verified 官方 test 的 issue ID；未人工审核，不用于默认模型。独立 CAR+SWE 候选在 Verified Codex-only 来源评测为 444/497（89.3%），在 CrossWOZ decide 来源评测为 436/500（87.2%），在 Chinese-Ambiguous-Reference 留出为 233/300（77.7%）。这三项已用于候选比较、且标签是弱映射或文本为机翻，不构成独立真实流量评估。详细对照见 `data/car_swe_candidate_source_eval_summary.md`；默认模型仍保持不变。

### 新增中文上下文对照草稿

另新增本地编写的 108 条中文训练草稿与 54 条场景留出，包含同一句短回复随前文改变动作标签的对照；它们属于合成数据，不是新公开语料或真实用户数据。增量候选的原始模型分类在新场景上由 32/54 提至 42/54，但 CrossWOZ 信息查询有退步，仍保留为实验候选。方法、首轮结果和限制见 `data/contextual_execution_experiment.md`。

之后又增加 108 条“明确实现且保留旧接口/行为”训练草稿及 54 条新场景评测，三类均衡、按场景隔离。新候选完整路由在该留出上为 48/54，上一候选 40/54；CrossWOZ 由 420/500 升至 432/500，SWE-bench 和中文歧义来源持平。该批数据仍是人工编写的合成草稿，不能代表真实用户流量；详细结果见 `data/contextual_contract_experiment.md`。候选没有替换默认模型。

随后新增 36 条“引用上一条方案并明确要求执行”合成训练草稿和 18 条新场景留出，用于检查短上下文执行措辞；已知错例没有放进训练。实验候选修复那条具体开发错例，新留出为 17/18，但原有来源验证宏 F1 略降、中文歧义集少 2 条，因而仍作为候选而非默认权重。逐项指标与限制见 `data/reference_execution_experiment.md`；候选没有替换默认模型。

之后又增加 36 条已选/未选方案对照训练草稿及 18 条新留出。`clarify` 场景由 4/6 升至 5/6，但留出总分仅从 15/18 升至 16/18，来源验证、CrossWOZ 与中文歧义来源均小幅回退；仍保存为单独候选，没有替换更均衡的试用候选或默认模型。详情见 `data/unselected_reference_experiment.md`。数据为项目内合成草稿，不是真实用户语料。

另以 SWE-bench-Live `verified` 快照建立了 499 条 Codex-only 外部对照：与项目已有 SWE-bench 任务 ID、repo/issue/PR 编号及精确输入交集均为 0。默认模型 Codex 召回 381/499（76.4%），当前较均衡候选 448/499（89.8%）。该集只含代码任务正例，不能评估误派率；英文 issue 由 Argos 自动翻译。它已用于一次性比较，不用于训练或逐例调参。数据快照、许可和限制见 `data/swe_bench_live_candidate_comparison_20261103/summary.md`。

### CodeQA 代码上下文负例诊断

从 [CodeQA 官方数据](https://github.com/jadecxliu/CodeQA) Java/Python test split 各抽 100 条代码理解问答，弱映射为 `decide`，用于测量“有代码上下文但不要求修改”时误派 Codex 的情况。问题由代码注释生成，英文经 Google Translate 机翻；代码片段只在运行时从本地文件临时加载，不写入评测产物。仅问题文本时两版各误派 18/200；附带真实代码时默认版误派 168/200、当前候选 198/200。可选代码块剥离模式将两版误派降至 18/200，并把平均路由时间降到约 1.1 ms。它仍是输入策略候选，默认入口未启用。数据集现标为开发集；单类、生成式问题构造和机翻限制显著，不能代表真实用户总体路由效果。完整记录见 `data/codeqa_code_context_decide_eval_20261103/summary.md`。
