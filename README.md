# light_decider

一个为个人 Agent 工作流做请求分诊的轻量路由器：请求先被判为 **直接回答（decide）/ 先追问（clarify）/ 交给编程 Agent（codex）**，再由执行层接通对应的 Worker。

**在线演示**：[chuck147147.github.io/light-decider](https://chuck147147.github.io/light-decider/) —— 浏览器本地运行的移植版，输入一句话即可看到分诊结果（与 Python 现役系统 144/144 对拍一致）。

- **判断层**：字符 TF-IDF + 逻辑回归三分类，叠加可审计的规则策略（现役：Round 4 模型 + 策略 v3.3）
- **评测方式**：代价矩阵先行（clarify→decide 记 10 分）、六套冻结盲测集、预注册判决线、标签来源分级披露，负结果与正结果同等记录
- **执行层（Super-agent）**：decide 出口接本地 Ollama（qwen2.5:7b-instruct）真答题；clarify 出口两轮追问回路、超限转人工；codex 出口生成结构化交接包，真实派发经人工确认门、沙箱限定独立工作目录
- **红线**：自动派发关闭；冻结标签永不修改；影子日志不回流训练

完整的方法、迭代记录、负结果与局限见 [CASE_STUDY.md](CASE_STUDY.md)。

## 快速开始

```bash
python try_router.py "解释一下哈希表为什么平均查询是 O(1)"
python executor.py --execute "给这个函数补上参数校验"   # codex 出口会先请你确认
```

## 目录

- `light_decider/`：路由模型与策略
- `executor.py` / `answer_worker.py` / `templates.py`：执行层与本地回答 Worker
- `data/`：训练数据与六套冻结盲测集（含来源说明）
- `docs/`：标注细则与各轮评测报告
