# 训练样本

把经人工确认的样本逐行保存为 JSON，文件名使用 `annotations.jsonl`。不要把示例、未确认预测或模型自动生成的标签混进训练集。

公开数据导入产生的弱标签先放在 `candidates.jsonl`，`reviewed` 保持 `false`。逐条复核并补充中文表达后，才复制到 `annotations.jsonl` 并设为 `true`。候选文件不会被训练脚本默认读取。

在项目根目录执行 `python scripts/build_candidates.py` 可生成一批候选样本。原始下载缓存保存在 `work/datasets/`，由 `.gitignore` 排除；来源、原始标签、转换规则和采样范围保存在 `data/candidates.manifest.json`。SWE-bench 中含 Unicode 替换字符的请求文本会跳过。

### 当前 600 条候选的处理状态

- `route_audit.jsonl` 对 600 条候选做了路由复核，`label` 是复核后标签，`original_label` 保留原标签；路线复核信息记在 `route_reviewed` 和 `route_review_note`。
- `translated_candidates_zh.jsonl` 保留逐字段英译中草稿以及完整英文原文和上下文。译文由本地 Argos 模型生成，不能视为人工确认。
- `training_candidates_zh.jsonl` 是训练实验用的中文输入。SWE-bench 样本使用中文指令和 Issue 标题，并保留原文用于追溯；所有候选仍为 `reviewed: false`。
- 默认训练仍只接受 `reviewed: true` 的人工标注。若要复现机器翻译草稿实验，需显式添加 `--include-machine-translation-drafts`；该模式产生的模型和指标只供实验，不代表真实中文输入上的效果。

### 复核流程

1. 执行 `python scripts/export_review_queue.py`，生成 Excel 可打开的 `data/review_queue.csv`。候选原文和上下文只供参考；超过单元格长度限制的原文会另存到 `data/review_long_text/`，审核时按 `text_en_file` 或 `context_en_file` 列打开。
2. 逐条填写 `final_route`、`text_zh`，并把 `context_zh` 中的上下文逐项翻译为 JSON 列表；如果原候选没有上下文，保持 `[]`。纯代码概念解释通常是 `decide`，明确要求编写/修改/调试代码才是 `codex`；缺少完成请求所必需的信息才是 `clarify`。
3. 确认一行的标签、中文输入和上下文后，才将 `reviewed` 设为 `true`。有疑问的行留作 `false`，不要猜。
4. 执行 `python scripts/import_review_queue.py`，将已审核行导出至 `data/annotations.jsonl`。导入器会校验标签、中文输入和上下文结构；训练脚本只会读取该文件中的已审核行。

CSV 中 `context_zh` 是 JSON 数组，需保留 `context_en` 的条目数量、顺序和 `role`。例如：`[{"role":"user_context","text":"用户背景的中文翻译"}]`。保存为 CSV 时不要删除 `candidate_id`、来源字段或列标题。

## 字段

```json
{
  "id": "sample-0001",
  "conversation_id": "thread-0001",
  "text": "用户当前输入",
  "context": [
    {"role": "user", "text": "之前的相关消息"},
    {"role": "assistant", "text": "之前的回复"}
  ],
  "label": "codex",
  "reviewed": true,
  "annotation_note": "标注依据；训练时不作为模型输入"
}
```

## 标签

- `clarify`：先判断。用户请求所需的关键信息缺失、上下文指代不明或请求相互冲突时，标为此类。
- `codex`：信息足够，且需要代码检索、修改、调试、文件或仓库操作时，标为此类。
- `decide`：信息足够，且不需要代码或工具、上层助手可以直接回答时，标为此类。

标注优先级是 `clarify` → `codex` → `decide`：先检查是否缺少关键条件；若没有，再判断是否需要代码或工具；其余可直接回答的输入标 `decide`。不要因为问题“看起来简单”就忽略它对上下文的依赖。

例子（仅说明规则，不是训练数据）：

- “帮我修复这个仓库的登录报错”，并提供了项目/错误上下文 → `codex`
- “用简单的话解释一下字符 n-gram” → `decide`
- “按刚才那个方案改一下”，但上下文里没有方案 → `clarify`

分类器只预测处理路线。`decide` 的最终回答、`clarify` 的追问由上层助手完成；`codex` 路径由固定模板整理原始请求后交接。

## 标注注意

- `conversation_id` 必须对应整段对话。训练/验证集按此字段分组，避免同一对话泄漏到两边。
- `context` 只放理解当前输入所必需的近期消息，并保留发言角色。
- `annotation_note` 只用于复核，不会送进分类器。
- `reviewed` 必须为 `true` 才会参与训练。
- 外部数据候选应保留 `source_dataset`、`source_id`、`source_split`、`source_label`、`label_method`、`source_license` 和 `language`，供审核及回溯。
- 重点标注短确认语、含糊请求、混合意图、缺少上下文和不应自动处理的情况。

语义实验使用的 `intent_examples_zh.jsonl` 是未审核的合成训练草稿，`intent_probe_zh.json` 是 35 条开发探针。探针用于检查误差，并已影响补充训练样本，因此不是独立最终测试集；两者都不能替代真实用户输入的人工标注。

`clause_examples_zh.jsonl` 保存未审核的分句训练草稿：每行是一个分句标签，`context` 保留完整原句，供模型判断该分句在原请求里的意图。默认训练脚本显式读取此草稿；它和其他合成样本一样不能视为人工确认数据。分句边界由轻量切分代码按标点和常见并列/顺序连接词识别，不作为训练标签。

`codex_judgment_eval_zh.jsonl` 是 45 条人工编写的三路挑战样本。用 `python scripts/evaluate_semantic_intent.py` 评估默认模型；可用 `--model` 指定候选 ONNX 目录、用 `--report` 指定报告文件。此集合已参与本轮错误分析和候选模型比较，因此只作为开发回归集，不能作为最终独立测试成绩，也不代表真实用户流量。

`context_policy_regression_zh.jsonl` 是 9 条专门检查上下文确认、解释请求、比较问题和含糊选项的回归样本。运行 `python scripts/evaluate_semantic_intent.py --data data/context_policy_regression_zh.jsonl --report data/context_policy_regression_report.md` 可复跑；该集合用于策略开发，不作为独立测试集。

`fresh_generalization_eval_zh.jsonl` 曾作为新措辞检查，但其错例随后用于调整策略，所以现在是开发集。`frozen_policy_eval_zh.jsonl` 的初次结果为 22/24；两个错例后来用于改规则，因此该集现已转为开发集，修复后复测为 24/24。

`frozen_policy_eval_v2_zh.jsonl` 是之后冻结的 24 条样本，在训练数据、此前评测集和开发探针中没有完全相同的文本与上下文组合。本轮只运行一次，结果 24/24；用 `python scripts/evaluate_semantic_intent.py --data data/frozen_policy_eval_v2_zh.jsonl --set-status frozen --report data/frozen_policy_eval_v2_report.md` 可复现。样本由开发者编写且规模有限，不代表真实用户流量；若用它调整后续版本，它也应转为开发集。

`frozen_policy_eval_v3_zh.jsonl` 初次评估为 21/24；三个错例用于补充“重试/文件命名规格”和缺失对象指代规则，因此此集合现已转为开发回归集。当前策略复测为 24/24，报告在 `data/frozen_policy_eval_v3_report.md`。它由开发者编写且规模有限，不代表真实用户流量。

`frozen_policy_eval_v4_zh.jsonl` 首次冻结评估为 31/36。复核发现其中一个“选更稳妥的那个”样本的标签应为 `decide`：上下文足以辨认选项，但没有要求执行；原冻结报告保存在 `data/frozen_policy_eval_v4_first_pass_report.md`。其余四类错例用于规则开发后，v4 已转为开发集，当前回归结果为 36/36，见 `data/frozen_policy_eval_v4_report.md`。开发者编写的小样本结果不能代表真实流量。

`frozen_policy_eval_v5_zh.jsonl` 是 v4 修正规则后的新冻结集，按三路均衡编写，并检查了与训练及旧评测集无完全相同的文本/上下文组合。首次冻结评估为 27/30；三个错例用于调整摘要分句、相互冲突的请求和模糊方案选择规则，因此 v5 现已转为开发集。首次报告保存在 `data/frozen_policy_eval_v5_first_pass_report.md`，当前开发回归结果见 `data/frozen_policy_eval_v5_report.md`。样本由开发者编写且数量有限，不代表真实用户流量。

`sharc_dev_source_eval_zh.jsonl` 从 ShARC 官方 dev split 中按来源对话树抽取 60 条（decide/clarify 各 30 条），每棵树只取一条；已核实官方 train/dev 之间没有重叠的 `tree_id`，项目训练候选使用的是官方 train split。标签按 ShARC 的最终回答/追问形式映射，文本和上下文由 Argos en_zh 1.9 自动翻译。默认模型为 37/60（61.7%），当前较均衡候选为 46/60（76.7%）；候选主要提高 `decide` 命中（14/30 至 24/30），`clarify` 则从 23/30 变为 22/30。该集没有 `codex` 正例，且属于规则问答领域，不代表通用中文路由准确率。它已用于候选比较，不能再视为未触碰盲测或用其错例调参；摘要见 [`sharc_dev_candidate_comparison_20261103/summary.md`](sharc_dev_candidate_comparison_20261103/summary.md)，原默认模型基线见 `data/sharc_dev_source_eval_report.md`。

`sharc_train_augmentation_zh.jsonl` 是额外抽取的 300 条 ShARC 官方 train 样本，`decide/clarify` 各 150 条，按 300 个新 `tree_id` 分组；源 ID 与原 600 条候选不重叠。路由按“最终回答/追问句”规则映射，中文由 Argos 机翻；`route_reviewed` 为 `true`，但 `reviewed` 为 `false`，仍是未人工审核的弱标签草稿。它不会被默认训练读取。可用 `--extra-base-data data/sharc_train_augmentation_zh.jsonl` 单独训练实验候选；该候选内部来源分组宏 F1 为 0.854，低于当前默认模型 0.897，因此未替换默认权重。

## SWE-bench-Live Verified Codex-only 评测

`swe_bench_live_verified_codex_eval_zh.jsonl` 使用 [SWE-bench-Live 官方数据集](https://huggingface.co/datasets/SWE-bench-Live/SWE-bench-Live) 中固定快照的 `verified` split。官方 split 有 500 条；重复 instance ID 去重后保留 499 条，来源任务日期为 2024-07 至 2025-04，覆盖 100 个仓库。仅使用仓库名和问题描述；不读取补丁、提示、测试或评测字段。文本由 Argos en_zh 1.9 自动翻译，已对项目现存 SWE-bench 训练/评测记录检查 instance ID、repo/issue/PR 编号与完整输入重叠，均为 0。源数据 MIT 许可副本见 `data/licenses/SWE-bench-Live-MIT.txt`。

## CodeQA 代码上下文误派诊断

`codeqa_code_context_decide_eval_zh.jsonl` 从 [CodeQA 官方数据](https://github.com/jadecxliu/CodeQA) 的 Java/Python `test` split 各取 100 条，共 200 条；按代码片段哈希去重。CodeQA 的任务是给代码片段和问题生成文字答案，项目将这类不含修改请求的问题弱映射为 `decide`。问题由代码注释转换生成，英文经 Google Translate 自动翻译且未经人工复核；不是自然中文真实请求。上游代码仓库 MIT 许可副本见 `licenses/CodeQA-MIT.txt`，底层来源代码的逐条许可未在数据集内标出。

仅问题文本时，默认模型与当前候选各误派 18/200（9.0%）；加入真实代码片段后分别误派 168/200（84.0%）和 198/200（99.0%）。新增的可选 `--strip-fenced-code` 模式在分类时剥离代码块，Codex handoff 仍保留原请求，两版误派均为 18/200（9.0%），平均路由约 1.1 ms/条。该模式仍是候选，默认入口未启用。此诊断集现为开发集：它只有 `decide` 弱标签，且问题由代码注释生成并经机翻；不代表自然中文真实流量。完整限制、逐项结果和复现命令见 [`codeqa_code_context_decide_eval_20261103/summary.md`](codeqa_code_context_decide_eval_20261103/summary.md)。

这是一组单类 `codex` 任务族评测，不含 `decide` 或 `clarify` 负例；报告只用于比较 Codex 召回，不能说明误派率。默认模型完整路由命中 381/499（76.4%），当前较均衡候选 448/499（89.8%），多命中 67 条。它已用于模型比较，不再作为未触碰盲测，也不用于训练/按错例调参。摘要和限制见 [`swe_bench_live_candidate_comparison_20261103/summary.md`](swe_bench_live_candidate_comparison_20261103/summary.md)。

固定快照及清洗/翻译构建命令：

```powershell
python scripts/build_swe_bench_live_verified_eval.py
```

原始 parquet 固定 SHA-256 保存在 `swe_bench_live_verified_codex_eval_manifest.json`；缓存数据保存在 `work/datasets/`。完整逐条对照见上述摘要目录中的 Markdown 和 JSON 报告。候选没有替换默认模型，自动派发继续关闭。

## 新增的原生中文弱标签来源

`chinese_ambiguous_reference_train_candidates_zh.jsonl` 与 `chinese_ambiguous_reference_holdout_zh.jsonl` 来自 [Chinese-Ambiguous-Reference](https://github.com/ygan/Chinese-Ambiguous-Reference)，上游仓库声明 MIT；项目保留了对应许可文本。原始数据缓存在 `work/datasets/chinese_ambiguous_reference.json`，不会默认提交或训练。

- 原始 1,104 段对话按完整文本去重；过滤 18 段命中电话号码、证件、地址、身高/体重等隐私信号的对话。日期、地点、商品、店铺和店铺背景等元数据不会导入训练行；上下文只保留前 6 句必要对话。
- 路由标签是弱映射：对用户发言后的下一条客服策略，明确追问/信息收集或忽略澄清需求映射到 `clarify`；符合映射规则的陈述型客服回应映射到 `decide`。来源代码和示例含有不一致，因此不确定的策略被排除。样本均为 `reviewed: false`、`route_reviewed: false`，没有 `codex` 类。
- 训练集 800 条（`decide/clarify` 各 400），留出集 300 条（各 150）；按对话组切分，组重叠为 0，训练/留出之间的精确输入上下文重叠为 0。留出集已用于一次候选比较，现在属于开发/选型集，不能作为最终盲测。
- 重建数据：先将上游文件放入 `work/datasets/chinese_ambiguous_reference.json`，然后执行 `python scripts/build_chinese_ambiguous_candidates.py`。
- 要显式将弱标签用于实验训练，执行：

```powershell
python scripts/train_semantic_intent.py --output work/bge_intent_finetuned_car_candidate --extra-base-data data/chinese_ambiguous_reference_train_candidates_zh.jsonl --include-weak-source-drafts
```

该候选在本来源留出集上为 236/300（78.7%），默认版为 184/300（61.3%）；候选的内部混合来源分组宏 F1 为 0.846，低于默认版 0.897。候选还在已用于策略开发的 45 条 Codex 回归集上得到 44/45，Codex 召回 14/15。它保存在 `artifacts/decisioner_semantic_car_candidate/`，没有替换默认模型；详细报告见 `data/chinese_ambiguous_reference_default_eval_report.md`、`data/chinese_ambiguous_reference_candidate_eval_report.md` 和 `data/codex_judgment_car_candidate_regression_report.md`。

### CrossWOZ 中文多轮信息查询来源评测

`crosswoz_test_decide_eval_zh.jsonl` 来自 CrossWOZ 官方 test split；原始对话压缩包缓存在 `work/datasets/crosswoz_data.zip`，不会默认提交或训练。论文标注语料按 CC BY 4.0 分发，仓库另提供 Apache-2.0 LICENSE；项目保留两份许可文本，并按 CC BY 4.0 对派生文本做署名。

- `scripts/build_crosswoz_decide_eval.py` 从 500 段官方测试对话中每段最多抽一条，共生成 500 条中文样本；对话上下文最多保留前 6 轮。过滤命中电话号码、证件号、邮箱和明确地址值模式的样本，并排除与已有 JSONL 完全相同的输入/上下文。
- 这是单类 `decide` 弱标签评测，不是训练数据。映射条件是当前用户轮有 `Request` 行为，紧接的系统轮有 `Inform`、无 `NoOffer` 或 `Request` 行为且不含问号；后续系统回复只用于构造弱标签，不进入模型输入。官方 test split 的筛选没有产生可用系统 `Request` 追问样本，因此它不能评测 `clarify` 或 `codex`。
- 默认模型在 500 条中判对 331 条（66.2%），CAR 候选版判对 428 条（85.6%）。该集合已经参与候选比较，归类为来源开发/选型集；因为只有 `decide` 标签，不能据此声称三路准确率提高。
- 重建数据：把官方/ConvLab 镜像的 `data.zip` 放入 `work/datasets/crosswoz_data.zip`，执行 `python scripts/build_crosswoz_decide_eval.py`。
- 复跑评测：

```powershell
python scripts/evaluate_semantic_intent.py --data data/crosswoz_test_decide_eval_zh.jsonl --model artifacts/decisioner_semantic_draft --report data/crosswoz_default_eval_report.md --set-status development
python scripts/evaluate_semantic_intent.py --data data/crosswoz_test_decide_eval_zh.jsonl --model artifacts/decisioner_semantic_car_candidate --report data/crosswoz_car_candidate_eval_report.md --set-status development
```

详细对比与限制见 `data/crosswoz_source_eval_summary.md`。CrossWOZ 被保留为独立来源评测，不加入三路训练；单类数据会把分类边界推向 `decide`，且来源没有 Codex 任务。

### SWE-bench Verified Codex 来源评测

`swe_bench_verified_codex_eval_zh.jsonl` 从 SWE-bench Verified 官方 test split 生成。该基准每条都是可解的 GitHub 仓库问题，任务族可以强映射到 `codex`；语料原文是英文，当前文件由本地 Argos Translate en_zh 1.9 自动翻译，未人工校对，不能代表真实中文用户输入。SWE-bench 上游项目声明 MIT，许可文本保存在 `data/licenses/SWE-bench-MIT.txt`。

- 官方 test 有 500 条，过滤 3 条命中明确联系方式模式的样本后保留 497 条；按原始 issue 分组，共 12 个仓库，与项目现有 JSONL 没有完全相同的输入/上下文组合。
- 输入只含仓库名和 `problem_statement` 的前段；HTML 评论、URL 和 fenced code block 会被移除。`patch`、`test_patch`、`hints_text` 与评测字段不读取。原文保留为评测行的溯源元数据，不会送进模型。
- 默认模型判对 416/497，Codex 召回 83.7%；CAR 候选判对 396/497，召回 79.7%。这是一类弱标签、英文软件仓库问题的机翻评测；不能据此判断中文三路整体准确率。
- 候选比较后，该集合属于开发/选型集，不用于训练。样本文本仍有机翻不自然之处，逐条结果应按探索性证据解读。
- 重建文件需 Python 的 `polars` 和项目已有本地 Argos 运行时；先将官方 test parquet 放入 `work/datasets/swe-bench-verified-test.parquet`，再执行 `python scripts/build_swe_bench_verified_codex_eval.py`。
- 复跑默认版和候选版评测：

```powershell
python scripts/evaluate_semantic_intent.py --data data/swe_bench_verified_codex_eval_zh.jsonl --model artifacts/decisioner_semantic_draft --report data/swe_bench_verified_default_eval_report.md --set-status development
python scripts/evaluate_semantic_intent.py --data data/swe_bench_verified_codex_eval_zh.jsonl --model artifacts/decisioner_semantic_car_candidate --report data/swe_bench_verified_car_candidate_eval_report.md --set-status development
```

对照摘要见 `data/swe_bench_verified_source_eval_summary.md`。该测试显示 CAR 候选在 CrossWOZ 的 `decide` 子集上优于默认版，但在 SWE-bench Verified 的 Codex-only 子集上较弱；因此它仍是实验候选，不替换默认模型。

### CAR+SWE Codex 扩充候选

`swe_bench_train_codex_extra_zh.jsonl` 是 300 条官方 train issue 的中文机翻训练草稿，按 issue ID 排除了历史样本和 SWE-bench Verified 官方 test ID；未人工审核。它只用于独立候选训练，不进入默认训练文件。重建命令：

```powershell
python scripts/build_swe_bench_train_codex_candidates.py
python scripts/train_semantic_intent.py --output work/bge_intent_finetuned_car_swe_candidate --extra-base-data data/chinese_ambiguous_reference_train_candidates_zh.jsonl --extra-base-data data/swe_bench_train_codex_extra_zh.jsonl --include-weak-source-drafts
python scripts/export_semantic_model.py --source work/bge_intent_finetuned_car_swe_candidate --output artifacts/decisioner_semantic_car_swe_candidate --float-onnx work/decisioner_semantic_car_swe_candidate_float.onnx
```

该候选在 SWE-bench Verified Codex-only 上为 444/497（89.3%），CrossWOZ `decide` 弱标签上为 436/500（87.2%），中文歧义指代留出上为 233/300（77.7%）；来源分组宏 F1 为 0.867，默认版历史指标为 0.897，但两者验证样本不同，不能只据这两个数判断优劣。各来源的机翻/弱标签限制和候选对照见 [`car_swe_candidate_source_eval_summary.md`](car_swe_candidate_source_eval_summary.md)。候选没有替换默认权重。

### 上下文执行意图对照实验

新增 `contextual_execution_train_drafts_zh.jsonl`（108 条，三类各 36）与 `contextual_execution_holdout_zh.jsonl`（54 条，三类各 18）。样本由 Codex 编写，`reviewed: false`，属于中文合成实验草稿。训练覆盖 24 个技术场景，评测覆盖另外 12 个场景，组与精确输入/上下文交集均为 0；同一句“可以”依前文中的修改邀请、解释邀请或未完成的选项选择，分别标为 `codex / decide / clarify`。同一作者、同一构造方法的场景留出不能替代真实用户评测。

`--extra-synthetic-data` 只把新草稿加到训练部分，保持原 CAR+SWE 的 341 条来源验证样本不变。训练产物记录分组 ID，导出时一并保留。复现命令：

```powershell
python scripts/build_contextual_execution_drafts.py
python scripts/train_semantic_intent.py --initial-model work/bge_intent_finetuned_car_swe_candidate --output work/bge_intent_finetuned_car_swe_context_warm_candidate --epochs 1 --learning-rate 3e-6 --keep-initial-checkpoint --extra-base-data data/chinese_ambiguous_reference_train_candidates_zh.jsonl --extra-base-data data/swe_bench_train_codex_extra_zh.jsonl --extra-synthetic-data data/contextual_execution_train_drafts_zh.jsonl --include-weak-source-drafts
python scripts/export_semantic_model.py --source work/bge_intent_finetuned_car_swe_context_warm_candidate --output artifacts/decisioner_semantic_car_swe_context_warm_candidate --float-onnx work/decisioner_semantic_car_swe_context_warm_candidate_float.onnx
python scripts/evaluate_contextual_execution_suite.py --output-dir data/contextual_execution_experiment_recheck
```

评测套件默认对比默认版、CAR+SWE 版和新增上下文候选，输出模型原始分类、完整路由、逐条分数和文件哈希。它从模型训练元数据读取额外来源/合成文件，检查精确输入重叠；使用新输出目录复跑，不覆盖旧报告。首次评测另带 `--first-pass`；结果用于后续改动时，这批场景应转作开发集。首次结果与实验结论见 [`contextual_execution_experiment.md`](contextual_execution_experiment.md)。

显式体验上一轮候选：`python try_router.py --model artifacts/decisioner_semantic_car_swe_context_warm_candidate`。该参数只改变本次运行所加载的模型。

### 带代码块的三路意图诊断集

`code_context_intent_eval_zh.jsonl` 由 16 个短 Python 片段构成，每个片段分别配有 `decide`（只解释）、`codex`（明确修改）和 `clarify`（缺少修改所需规格）三种中文请求，共 48 条、每路 16 条。同一代码内容在三种意图下保持一致，便于隔离用户请求措辞的作用。

样本为项目内编写的合成诊断数据，标签按项目三路定义指定，未经过用户复核，不代表真实流量；只用于开发评测，不进入训练。构建和对照命令：

```powershell
python scripts/build_code_context_intent_eval.py
python scripts/evaluate_code_context_intent_suite.py --output-dir data/code_context_intent_eval_my_run
```

评测器分别运行保留完整代码块、仅在分类时剥离 fenced code 两种模式；Codex handoff 仍保留原文。每次输出都记录数据和模型哈希，已有目录不会被覆盖。

随后构造了另一份 48 条平衡训练草稿 `code_context_clarify_train_drafts_zh.jsonl`，共 16 组“解释现状 / 明确修改 / 修改但缺少必要规格”的最小对照。该集只作为训练候选输入，`reviewed: false`，与已有 JSONL 无精确输入/上下文重叠；生成和分组信息见 `code_context_clarify_train_manifest.json`。它没有并入默认训练。

从 `decisioner_semantic_car_swe_reference_execution_epoch1_candidate` 以 2e-6 继续训练一轮并导出 `decisioner_semantic_code_context_clarify_epoch1_candidate`。同一 117 条来源验证集宏 F1 保持 0.9247，但代码意图集总体由基座的 40/48 变成 39/48：`clarify` 召回从 56.2% 提到 62.5%，`decide` 召回从 93.8% 降到 81.2%，Codex 召回仍为 100%。上下文执行留出由 51/54 降到 50/54，中文歧义集由 234/300 降到 232/300；Codex 开发集持平，CrossWOZ 略升，SWE-bench 持平。因此这是未选中的实验候选，不替换默认模型或前一候选。完整对照见 [`code_context_intent_eval_20261103_after_clarify_training/summary.md`](code_context_intent_eval_20261103_after_clarify_training/summary.md) 与 [`code_context_clarify_regression_20261103/summary.md`](code_context_clarify_regression_20261103/summary.md)。

### 接口兼容约束训练实验

`contextual_contract_train_zh.jsonl` 和 `contextual_contract_holdout_zh.jsonl` 是新编写的 108 条训练草稿与 54 条场景留出，围绕“要求实现，同时保留旧接口/行为”构造，并与项目已有完整输入/上下文零重叠。样本是合成实验数据，不代表真实用户请求。重建并训练：

```powershell
python scripts/build_contextual_contract_drafts.py
python scripts/train_semantic_intent.py --initial-model work/bge_intent_finetuned_car_swe_context_warm_candidate --output work/bge_intent_finetuned_car_swe_context_contract_epoch1_candidate --epochs 1 --learning-rate 3e-6 --extra-base-data data/chinese_ambiguous_reference_train_candidates_zh.jsonl --extra-base-data data/swe_bench_train_codex_extra_zh.jsonl --extra-synthetic-data data/contextual_execution_train_drafts_zh.jsonl --extra-synthetic-data data/contextual_contract_train_zh.jsonl --include-weak-source-drafts
python scripts/export_semantic_model.py --source work/bge_intent_finetuned_car_swe_context_contract_epoch1_candidate --output artifacts/decisioner_semantic_car_swe_context_contract_epoch1_candidate --float-onnx work/decisioner_semantic_car_swe_context_contract_epoch1_float.onnx
python scripts/evaluate_contextual_execution_suite.py --output-dir data/contextual_contract_experiment_recheck --first-pass --context-data data/contextual_contract_holdout_zh.jsonl --context-title "接口兼容约束上下文"
```

本轮候选在新 54 条的完整路由上为 48/54，原始模型分类也为 48/54；上一轮完整路由是 40/54。旧 45 条开发集仍有同一条上下文 Codex 错例，来源验证宏 F1 略低于训练起始模型，因此候选单独保存。详见 [`contextual_contract_experiment.md`](contextual_contract_experiment.md) 和 [首次逐项评测](contextual_contract_experiment_20261103/summary.md)。

上一轮候选体验命令：`python try_router.py --model artifacts/decisioner_semantic_car_swe_context_contract_epoch1_candidate`。默认入口仍指向原模型；最新实验候选见下节。

### 指代式上下文执行实验

`reference_execution_train_zh.jsonl` 新增 36 条三类均衡合成训练样本；`reference_execution_holdout_zh.jsonl` 新增 18 条不同场景留出。样本重点覆盖助手先提出方案、用户用“就照这个思路改，调用方式别动”等简短话语明确要求执行的场景，并对照询问方案利弊和引用未选定选项的追问场景。已知开发错例未加入训练，训练/留出按场景隔离，和项目现有输入及上下文零重叠。

复现和评测命令见 [`reference_execution_experiment.md`](reference_execution_experiment.md)。新候选在原错例上从 `decide` 翻为 `codex`；新场景留出完整路由与上一候选持平，为 17/18。来源验证宏 F1 略低于起始权重（0.8656 对 0.8685），中文歧义留出低 2 条、CrossWOZ 高 3 条、SWE-bench 持平。它保存在 `artifacts/decisioner_semantic_car_swe_reference_execution_epoch1_candidate/`，默认模型未更换。

显式试用：`python try_router_semantic.py --model artifacts/decisioner_semantic_car_swe_reference_execution_epoch1_candidate`。模型分数未校准，自动派发保持关闭。完整逐条结果见 [`reference_execution_experiment_20261103/summary.md`](reference_execution_experiment_20261103/summary.md)。

### 未选方案指代续训实验

为减少“前文列了多个选项，用户只说按刚才那个办法处理”被误派为 Codex，新增 36 条训练草稿和 18 条分场景留出。该轮在新留出上从 15/18 提至 16/18，`clarify` 从 4/6 提至 5/6；已明确选定方案的 `codex` 是 5/6，仍有一条被误判为 `clarify`。来源验证宏 F1 从 0.8656 降至 0.8624，CrossWOZ 少 4 条、中文歧义集少 1 条，SWE-bench 持平。因此仍推荐上一节的 `reference_execution` 候选作试用，新续训版本只保留作独立实验。

数据生成、训练导出及评测命令见 [`unselected_reference_experiment.md`](unselected_reference_experiment.md)，逐条报告见 [`unselected_reference_experiment_20261103/summary.md`](unselected_reference_experiment_20261103/summary.md)。这批样本也是合成数据；默认模型不变，自动派发仍关闭。

### HumanEvalComm 代码澄清来源评测

从 [HumanEvalComm](https://huggingface.co/datasets/jie-jw-wu/HumanEvalComm) 固定版本抽取 164 道 HumanEval Python 题及其作者核验的歧义、矛盾、不完整改写。原始完整编程题映射为 `codex`，改写题映射为 `clarify`；自然语言由 Google Translate 机翻成中文，Python 签名和 doctest 保留。分别生成歧义 328 条、矛盾 326 条、不完整 328 条，共 982 条、三类改写各自与原题配对。HumanEval 的 `solution` 和 `test_case` 字段未使用；原始 prompt 内的 doctest 示例保留在输入中。数据卡声明 Apache-2.0，上游 HumanEval 项目声明 MIT；许可文本保存在 `data/licenses/`。

该数据不是路由标注集：标签是基于“原题要求编程、改写经作者核验需要澄清”的弱映射；它只测 `codex / clarify`，且机翻和 HumanEval 公开时间久都带来偏差，因此仅作开发诊断、不参与训练，也不能代表中文真实请求准确率。构建脚本会校验固定源文件 SHA-256；下载固定 revision 的 CSV 到 `work/datasets/human_eval_comm/HumanEvalComm_v2.csv` 后重建：

```powershell
python scripts/build_humanevalcomm_route_eval.py
python scripts/evaluate_humanevalcomm_route_suite.py --output-dir data/humanevalcomm_route_eval_my_run
```

本次三个模型的评测逐项结果与哈希清单见 [`humanevalcomm_route_eval_20261103/summary.md`](humanevalcomm_route_eval_20261103/summary.md)；该目录归类为开发集。三版模型在 982 条上的整句和运行时预测逐条完全一致：整句分类把所有样本判为 `codex`（准确率 50.0%，`clarify` 召回 0%）；运行时准确率为 49.7–50.0%，`clarify` 召回仅 2.4–3.1%，`codex` 召回约 97%。这表明现有微调没有学会此类代码请求中的追问边界，不支持启用这两个候选。当前分句器平均把每条输入拆成 12.09 段，最多 33 段；端到端单条耗时约 123–212 ms。

已完成分类输入消融：`scripts/build_humanevalcomm_prose_ablation.py` 从评测文本中去掉函数签名、doctest 和示例，只留下“请编写 Python 函数”及译后的需求说明；其中 5 条不完整改写本身没有可留的自然语言说明，输入只剩通用编程请求。原始全文仍在溯源字段中，实际路由和 Codex handoff 未修改。复现命令：

```powershell
python scripts/build_humanevalcomm_prose_ablation.py
python scripts/evaluate_humanevalcomm_route_suite.py --data-dir data/humanevalcomm_route_eval_prose_only --output-dir data/humanevalcomm_route_eval_prose_only_my_run
```

消融逐项结果见 [`humanevalcomm_route_eval_prose_only_20261103/summary.md`](humanevalcomm_route_eval_prose_only_20261103/summary.md)。三版模型的整句 `clarify` 召回仍为 0%；运行时召回仍只有 2.4–3.7%，与完整输入几乎没有变化。默认模型加权平均耗时从 151.78 ms 降到 109.56 ms（约 28%）；两个候选分别下降约 44%。结论是剥离代码可减少推理开销，但不能修复分类边界；当前仅作为诊断，不接入实际路由，也不据此训练或替换默认模型。

### 中文代码规格最小对照训练实验

`code_spec_minipairs_train_zh.jsonl` 是 24 个代码场景的 48 条中文合成训练草稿；`code_spec_minipairs_holdout_zh.jsonl` 是另 16 个场景的 32 条留出。每组样本提出相同实现任务，一条明确实现关键规格、另一条缺少会改变输出/行为的关键条件，标签为 `codex / clarify`。两组按场景隔离，并与已有 JSONL 没有完全相同的输入/上下文；标签由项目内编写者指定，未经用户复核。

复现训练与导出：

```powershell
python scripts/build_code_spec_minipairs.py
python scripts/train_semantic_intent.py --initial-model work/bge_intent_finetuned_code_context_clarify_epoch1_candidate --output work/bge_intent_finetuned_code_spec_minipairs_epoch1_candidate --epochs 1 --learning-rate 2e-6 --extra-synthetic-data data/code_spec_minipairs_train_zh.jsonl
python scripts/export_semantic_model.py --source work/bge_intent_finetuned_code_spec_minipairs_epoch1_candidate --output artifacts/decisioner_semantic_code_spec_minipairs_epoch1_candidate --float-onnx work/decisioner_semantic_code_spec_minipairs_epoch1_float.onnx
```

旧运行时策略下，新留出上的基线为 16/32（50.0%，运行时 `clarify` 召回 0%），续训候选为 17/32（53.1%，`clarify` 召回 6.2%）。错误分析发现策略把“没有说明”误当成解释请求；在 `routing_policy.py` 修复该覆盖后，不改模型权重，同一候选重评为 18/32（56.2%，运行时 `clarify` 召回 12.5%）。既有 45 条三路开发集默认版和候选版均为 45/45；48 条代码上下文诊断持平。HumanEvalComm 机翻评测的 `clarify` 召回没有变化，说明微调没有泛化到该公开来源。逐条标签审查认为 7 条可能可用安全默认、3 条取决于项目约定，只有 6 条确定需要追问；候选仅命中其中 1 条（事后诊断，不作为新正式分数），未据此重标或重算成绩。

候选仍只保存在 `artifacts/decisioner_semantic_code_spec_minipairs_epoch1_candidate/`，不替换默认模型。完整结果见 [`code_spec_minipairs_experiment_20261103/summary.md`](code_spec_minipairs_experiment_20261103/summary.md)，逐条标签审查见 [`code_spec_minipairs_experiment_20261103/label_audit.md`](code_spec_minipairs_experiment_20261103/label_audit.md)，修复后策略与产物哈希见 [`code_spec_minipairs_experiment_20261103/policy_audit/manifest.json`](code_spec_minipairs_experiment_20261103/policy_audit/manifest.json)。该留出集首轮使用后归为开发集，不是盲测；概率未校准，自动派发关闭。


## 公开导出说明

公开版训练数据已经过隐私清洗，与现役模型的实际训练输入不保证逐字一致。
