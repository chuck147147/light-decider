# Ollama 安装与 Answer Worker 实跑报告

日期：2026-11-06。实跑回答仅供人工检查，没有自动评分。

## 安装与本机配置

- 安装：winget 能识别 `Ollama.Ollama`，但其下载文件保持 0 字节且无活动连接；停止该次挂起进程后改用 Ollama 官方 Windows 安装脚本。
- Ollama：`ollama version is 0.40.15`；当前用户 PATH 已包含 `<LOCAL_PATH>
- 本地服务：`http://localhost:11434` 返回 HTTP 200，正文 `Ollama is running`。
- 本机：AMD Ryzen 9 8940HX，16 核 / 32 线程；15.3 GB 内存；NVIDIA GeForce RTX 5060 Laptop GPU 4.0 GB、AMD Radeon 610M 0.5 GB。
- 模型：`qwen2.5:3b-instruct`，`ollama pull` 一次成功；模型主 blob 1.9 GB（约 2 GB）。
- 官方资料：[Windows 安装页](https://ollama.com/download/windows)、[Qwen2.5 模型库](https://ollama.com/library/qwen2.5)、[Ollama OpenAI 兼容接口说明](https://github.com/ollama/ollama/blob/main/docs/api/openai-compatibility.mdx)。

## 安装冒烟

题目：说明冰芯中封存的微小气泡怎样帮助研究者估计冰层形成时期的大气成分。

### `ollama run qwen2.5:3b-instruct` 完整回答

冰芯是地球历史中宝贵的记录者，它们能够揭示过去数百万年来地球的气候变化，包括温度、降水模式、风向以及大气成分。在冰芯中，封存的微小气泡包含了一定时期内大气的气体样本，这对于研究者理解过去的大气组成具有重要的科学价值。

大气中的气体成分会通过各种自然过程被封存在冰芯中的气泡内。这些气泡能够提供关于过去大气中某些气体浓度的直接信息，例如二氧化碳、氮气、氧气等。在特定的温度和压力条件下，这些气体组分会形成液态或气态的微小气泡，并被封闭在冰的晶格结构中。

通过分析冰芯中的微小气泡，研究者能够恢复过去大气中的成分和含量。这种方法的一个重要前提是冰芯的冰结构能够保持足够长的时间，以便从大气中捕获气体。通常，研究者会从冰芯中提取这些微小气泡，然后使用现代的技术手段，如质谱分析，来测定这些气泡中气体的种类和浓度。

例如，通过测定大气中二氧化碳（CO₂）的浓度，研究者可以估计过去冰盖或冰川附近大气中二氧化碳的浓度。由于二氧化碳在大气中的浓度变化，特别是在工业化进程中的急剧增加，了解过去大气中二氧化碳的含量对于理解全球变暖的历史和趋势至关重要。

同样地，氮气（N₂）、氧气（O₂）等其他气体的含量也能通过冰芯中的微小气泡来估计。这些气体的组成信息对于理解地球大气历史的演变过程具有重要意义。因此，冰芯中的微小气泡为研究者提供了一种独特的方法，来估计过去的大气组成，这对于理解气候变化以及地球历史中气体循环过程提供了宝贵的见解。

### OpenAI 兼容 POST

- 请求：`POST http://localhost:11434/v1/chat/completions`；相同题目；HTTP 200。
- 响应耗时：2.151 秒；用量：prompt 53、completion 256、total 309 tokens。
- 请求 JSON 包含 `temperature=0.2`、`options.num_ctx=4096`、`keep_alive=60s`，接口返回 HTTP 200。Ollama 的兼容接口说明指出 OpenAI API 没有标准上下文长度字段；该 HTTP 200 不单独证明扩展参数已应用。Answer Worker 因此改用原生 `/api/chat`，它支持 `options.num_ctx` 和 `keep_alive`。

## Answer Worker 配置与行为

| 项 | 设置 |
|---|---|
| Base URL | `LIGHT_DECIDER_ANSWER_BASE_URL`，缺省 `http://localhost:11434/v1` |
| Model | `LIGHT_DECIDER_ANSWER_MODEL`，缺省 `qwen2.5:3b-instruct` |
| HTTP timeout | 120 秒 |
| Context | 原生 `/api/chat` 的 `options.num_ctx=4096` |
| Keep alive | 原生 `/api/chat` 的 `keep_alive=60s` |
| Temperature | 0.2 |
| System prompt | `直接回答用户的问题，不提路由、不解释自己是执行层。` |
| 并发 | 进程内全局锁串行；同一时刻处理一个请求 |
| 重试 | 服务错误、超时或异常响应最多请求 2 次；仍失败记 `answer_failed`，输出“本地模型不可用，已转人工”，保留错误详情，不切换出口 |
| 非 decide | clarify 回路保持原样；Codex 仍只生成 dry-run 包 |

## v6 decide 六题实跑

执行方式：真实 round-4 路由器 + 现役策略 + `executor.py --execute`；使用 6 条 v6 冻结金标 decide 题。Answer Worker 使用已配置服务地址解析到同一 Ollama 实例的原生 `/api/chat`，以确保 `options.num_ctx=4096`、`options.temperature=0.2` 和 `keep_alive=60s` 生效。回答仅供人工审阅，没有自动评分。

### blind-v6-004

请求：比较木管乐器和弦乐器演奏同一音高时，泛音分布如何形成可辨认的音色差异。

实际动作：`decide`；线程状态：`answered`；进程退出码：0。

Answer Worker：model=`qwen2.5:3b-instruct`，耗时 `2.72` 秒，attempts=`1`，usage=`{"prompt_tokens": 55, "completion_tokens": 128, "total_tokens": 183}`。

**回答全文**

木管乐器和弦乐器在演奏同一音高时，由于其发声原理和内部结构的不同，会产生不同的泛音分布，从而形成可辨认的音色差异。木管乐器通过空气柱的振动产生声音，而弦乐器通过弦的振动产生声音。木管乐器的音色通常具有更丰富的泛音层次，这些泛音是由于空气柱在不同长度的共鸣腔内振动产生的。弦乐器的音色则更多依赖于弦的振动频率，其泛音分布相对较为简单，但仍然存在，只是与弦振动频率的倍数关系不同。

### blind-v6-009

请求：解释一下，传统榫卯接头如何依靠接触面的几何咬合限制木构件沿不同方向滑动。

实际动作：`decide`；线程状态：`answered`；进程退出码：0。

Answer Worker：model=`qwen2.5:3b-instruct`，耗时 `0.551` 秒，attempts=`1`，usage=`{"prompt_tokens": 54, "completion_tokens": 65, "total_tokens": 119}`。

**回答全文**

传统榫卯接头通过精确的几何设计，使得木构件之间的接触面形成特定的几何关系，这些关系限制了木构件沿不同方向的滑动。这种设计利用了木材的自然特性，以及榫卯接头的精确配合，确保了结构的稳定性和耐久性。

### blind-v6-019

请求：为什么炎热天气里，远处柏油路面上会出现像积水一样晃动的倒影，换个观察位置后影像又会改变？

实际动作：`decide`；线程状态：`answered`；进程退出码：0。

Answer Worker：model=`qwen2.5:3b-instruct`，耗时 `0.758` 秒，attempts=`1`，usage=`{"prompt_tokens": 58, "completion_tokens": 77, "total_tokens": 135}`。

**回答全文**

这是因为柏油路面在炎热天气下会变得非常热，导致其表面温度高于周围空气温度，形成局部的热空气上升，这种现象称为热对流。当光线照射到这种热对流形成的边界时，会形成类似水面的倒影效果。当观察位置改变时，热对流边界的位置也会随之改变，导致影像变化。

### blind-v6-021

请求：说明冰芯中封存的微小气泡怎样帮助研究者估计冰层形成时期的大气成分。

实际动作：`decide`；线程状态：`answered`；进程退出码：0。

Answer Worker：model=`qwen2.5:3b-instruct`，耗时 `0.42` 秒，attempts=`1`，usage=`{"prompt_tokens": 53, "completion_tokens": 46, "total_tokens": 99}`。

**回答全文**

冰芯中的微小气泡保存了大气当时的气体组成，通过分析这些气泡，研究者可以估计冰层形成时期的地球大气成分，包括过去的大气温度、压力和温室气体浓度等。

### blind-v6-022

请求：萤火虫的发光反应怎样把化学能转成可见光，为什么通常没有同等强度的发热？

实际动作：`decide`；线程状态：`answered`；进程退出码：0。

Answer Worker：model=`qwen2.5:3b-instruct`，耗时 `0.817` 秒，attempts=`1`，usage=`{"prompt_tokens": 52, "completion_tokens": 99, "total_tokens": 151}`。

**回答全文**

萤火虫发光的化学反应涉及荧光素酶催化荧光素氧化产生可见光，同时生成ATP，这个过程伴随着能量的释放。通常情况下，萤火虫发光时的能量大部分以光的形式释放，很少以热的形式释放，因此看起来发光过程不伴随明显的发热。这是因为发光反应中的能量转换效率较高，大部分能量被用于光的发射，而剩余的能量以热的形式散失，但通常这部分能量不足以产生明显的热量。

### blind-v6-023

请求：电梯从静止开始向上加速时，体重秤上的读数为什么会短暂变大？

实际动作：`decide`；线程状态：`answered`；进程退出码：0。

Answer Worker：model=`qwen2.5:3b-instruct`，耗时 `0.423` 秒，attempts=`1`，usage=`{"prompt_tokens": 48, "completion_tokens": 44, "total_tokens": 92}`。

**回答全文**

因为电梯加速上升时，人会经历一个向上的加速度，根据牛顿第二定律，人会感受到一个额外的向上支持力，这个额外的力使得体重秤的读数增加。

## 服务未启动失败路径演练

用真实路由器对 `blind-v6-004` 执行 `--execute`，仅将该次子进程的 Base URL 指向未监听的 `http://<LOCAL_IP>:9/v1`，以模拟 Ollama 服务不可用；实际安装的 11434 服务保持运行。失败时没有切换到 Codex 或其他出口。

- 线程状态：`answer_failed`；尝试次数：`2`；耗时：`4.103` 秒。
- CLI 输出了两次连接失败详情并打印 `本地模型不可用，已转人工`。

失败 thread 示例已从公开副本移除；失败语义与上述摘要一致。
## 回归与保护文件

- clarify/codex 执行层演练：`python -B scripts/drill_executor_clarify_loop.py` 通过（原澄清回路、转人工和 Codex dry-run 路径）。
- 无 `--execute` 回归：executor.py 与 try_router.py 及改动前 stdout 字节一致，907 字节；SHA-256 `5efc7d8b788deeab3b78d14c0d853676e5d91d5f867fda0cda6165bcb1803077`；stderr 为空：`True`。
- 未更改路由模型、策略和冻结标签；以下哈希与原记录一致：
- active routing_policy.py：`0e6d6493c01ad16f56574e4311bd2feb95d6f9872517b9037dc5506caaadabc0`
- round4 model：`6eff1a818db972bf887ed885f1cad4162dc5cef69ebdee0fb4f7ac32c37b286b`
- v6 frozen labels：`9a687a497f0485010ad5a1de538e485c165c4cee3780190d55ee7e2d3e304f6f`

## 代码入口

- 新增 `light_decider/answer_worker.py`；执行层增加 `--execute`。
- 不带开关仍调用原路由 CLI；`--execute-dry-run` 仍不调用本地回答 Worker。
- `--execute` 只在 decide 动作调用 Worker；Codex handoff 仍为 dry-run。
