# Super-agent 第二步：Codex 真实派发演练报告

日期：2026-11-06。演练通过真实路由器、执行层和本机 Codex CLI 完成。派发确认由本演练依照用户预授权输入 `y` / `N`；所有 Codex 调用都使用每 thread 独立工作目录和 `workspace-write` 沙箱。

为验证单目录写入边界，最初的 A/C 调用日志显示 CLI 还开放了系统临时目录；我关闭 `/tmp`、`$TMPDIR` roots 并清空附加 roots 后重跑。完整 thread 审阅又发现实际派发的 thread 顶层 `dry_run` 未同步，我修正后再次重跑 A/C。下文只收录最终收紧边界且 `dry_run=false` 的 A/C thread；所有中间测试目录已清理。B 在拒绝门就结束，没有重复调用。

## 调用方式与配置

- 本机 CLI：`codex-cli 0.167.0-alpha.3.2`；认证状态为 ChatGPT 登录。
- 只有 `--execute` 启用 Codex 出口。执行层打印 handoff payload 全文后提示 `确认派发给 Codex？(y/N)`；只有 `y` 调用 CLI，其他输入拒绝。
- 默认工作目录：项目下 `workspace/codex_runs/<thread_id>/`；演练未设置 `LIGHT_DECIDER_CODEX_WORKDIR`，使用三个不同的 thread 子目录。项目根未作为 Codex 工作目录。
- 命令：`codex exec --sandbox workspace-write ... -C <thread_workdir> -`；payload 经 stdin 提供。额外配置关闭 `/tmp`、`$TMPDIR` 写入根，并清空 `sandbox_workspace_write.writable_roots`。A/C 的 Codex 运行日志均报告 `sandbox: workspace-write [workdir]`。
- 官方 Codex CLI 示例也使用 `codex exec` 与 `--sandbox workspace-write`：[OpenAI Cookbook：Build iterative repair loops with Codex](https://developers.openai.com/cookbook/examples/codex/build_iterative_repair_loops_with_codex)。
- 执行层超时为 600 秒，每次用户确认后只启动一个 Codex 子进程、不重试。Codex CLI 本身的 stderr 记录了流断开后的内部连接恢复；最终调用仍以退出码 0 完成。最终输出、stdout/stderr、退出码、耗时及文件差异写入同一 thread 的独立 `dispatch_event`；执行包 `automatic_dispatch_allowed=false`。
- `codex+check_first` 额外收到范围约束：只查当前工作目录；目录为空或没有现有约定时停止、不新增或修改实现文件。

## 样本编号说明

任务把 `blind-v6-013` 标为 `to_pgm`，但冻结文件中 v6-013 是高危去重政策请求，动作是 `clarify`，不应绕过该路由进行派发。`to_pgm` 实际是冻结样本 `blind-v5-013`，且真实路由为 `codex`，所以 A 使用 v5-013。C 与 B 按要求分别使用 v6-008、v6-002。

## A. 真派发：to_pgm 实现

- 样本：`blind-v5-013`；路由动作：`codex`；确认：`y`；状态：`completed`。thread 顶层与执行包 `dry_run=false`。
- Codex 退出码：`0`；耗时：`164.377` 秒；工作目录：`<LOCAL_PATH>
- 新增文件：`to_pgm.py`，813 字节，SHA-256 `d87e66c14cda80bdee012fc44197f139b65c0399789c78e60d190c6098f3e0b7`。无修改或删除文件。
- 输出摘要：已在 [to_pgm.py](<<LOCAL_PATH>>) 实现 \`to_pgm(width, height, pixels)\`。它会生成指定的 P5 头部并拼接像素字节；参数不符合要求时抛出 \`ValueError\`。
- 生成源码：

```python
"""Build P5 PGM image data in memory."""


def to_pgm(width, height, pixels):
    """Return a P5 PGM byte string for row-major 8-bit pixels.

    Raises:
        ValueError: If dimensions are not positive integers or ``pixels`` is
            not bytes with exactly ``width * height`` entries.
    """
    if (
        not isinstance(width, int)
        or isinstance(width, bool)
        or width <= 0
        or not isinstance(height, int)
        or isinstance(height, bool)
        or height <= 0
    ):
        raise ValueError("width and height must be positive integers")

    if not isinstance(pixels, bytes) or len(pixels) != width * height:
        raise ValueError("pixels must be bytes of length width * height")

    header = f"P5\n{width} {height}\n255\n".encode("ascii")
    return header + pixels
```

## B. 拒绝派发

- 样本：`blind-v6-002`；路由动作：`codex`；确认：`N`；状态：`dispatch_declined`。
- 工作目录：`<LOCAL_PATH> `dispatch_event`、命令行或退出码；新增、修改、删除文件均为 0。

## C. check_first 空目录

- 样本：`blind-v6-008`；路由动作：`codex+check_first`；确认：`y`；状态：`completed`。thread 顶层与执行包 `dry_run=false`。
- Codex 退出码：`0`；耗时：`145.914` 秒；工作目录：`<LOCAL_PATH> 0。
- Codex 输出：

> 当前工作目录为空。我检查了目录内容及递归文件清单，未发现项目源码、项目约定（如 `AGENTS.md`）、文档或测试。
> 
> 因此无法核对队列状态模型、持久化与恢复逻辑、视图筛选约定或相关测试；按要求停止，未创建或修改任何文件。

## 完整 thread JSONL

公开导出仅保留清洗后的 A 演练记录；B/C thread 记录已移除。

```jsonl
{"schema_version":"light_decider_thread_v1","thread_id":"public-demo-a","original_request":"用 Python 写 to_pgm(width, height, pixels)，返回 P5 PGM 字节串。宽高为正整数，pixels 为长度等于宽乘高的 bytes，像素从左上角逐行排列。用 ASCII 写三行头部，第一行 P5，第二行是宽和高（用一个空格分隔），第三行 255，每行以 LF 结束，最后原样拼接像素。参数不合要求就抛 ValueError，不写文件。","context":[],"clarification_rounds":[],"route_history":[{"stage":"initial","request_text":"用 Python 写 to_pgm(width, height, pixels)，返回 P5 PGM 字节串。宽高为正整数，pixels 为长度等于宽乘高的 bytes，像素从左上角逐行排列。用 ASCII 写三行头部，第一行 P5，第二行是宽和高（用一个空格分隔），第三行 255，每行以 LF 结束，最后原样拼接像素。参数不合要求就抛 ValueError，不写文件。","action":"codex","reason":"highest_model_score","policy_override":null,"suggested_route":"codex","scores":{"clarify":0.18335332979507254,"codex":0.6373733404605998,"decide":0.17927332974432755},"high_risk_domains":[]}],"current_request":"用 Python 写 to_pgm(width, height, pixels)，返回 P5 PGM 字节串。宽高为正整数，pixels 为长度等于宽乘高的 bytes，像素从左上角逐行排列。用 ASCII 写三行头部，第一行 P5，第二行是宽和高（用一个空格分隔），第三行 255，每行以 LF 结束，最后原样拼接像素。参数不合要求就抛 ValueError，不写文件。","current_action":"codex","status":"completed","execution_package":{"type":"codex_handoff","thread_id":"4c5489f9-ef57-4729-8207-63a4d36a4b38","action":"codex","payload":"## 用户当前请求（原文）\n\n用 Python 写 to_pgm(width, height, pixels)，返回 P5 PGM 字节串。宽高为正整数，pixels 为长度等于宽乘高的 bytes，像素从左上角逐行排列。用 ASCII 写三行头部，第一行 P5，第二行是宽和高（用一个空格分隔），第三行 255，每行以 LF 结束，最后原样拼接像素。参数不合要求就抛 ValueError，不写文件。\n\n## 处理要求\n\n保留用户原意，不要补造需求。若缺少完成任务所必需的信息，先向用户澄清。","dry_run":false,"automatic_dispatch_allowed":false},"dry_run":false,"automatic_dispatch_allowed":false,"final_route_result":{"action":"codex","reason":"highest_model_score","policy_override":null,"override_log":[],"high_risk_domains":[],"declared_default":null,"check_first_targets":[],"suggested_route":"codex","codex_handoff":"## 用户当前请求（原文）\n\n用 Python 写 to_pgm(width, height, pixels)，返回 P5 PGM 字节串。宽高为正整数，pixels 为长度等于宽乘高的 bytes，像素从左上角逐行排列。用 ASCII 写三行头部，第一行 P5，第二行是宽和高（用一个空格分隔），第三行 255，每行以 LF 结束，最后原样拼接像素。参数不合要求就抛 ValueError，不写文件。\n\n## 处理要求\n\n保留用户原意，不要补造需求。若缺少完成任务所必需的信息，先向用户澄清。","scores":{"clarify":0.18335332979507254,"codex":0.6373733404605998,"decide":0.17927332974432755},"top_score":0.6373733404605998,"probabilities_calibrated":false,"automatic_dispatch_allowed":false},"codex_workdir":"<LOCAL_PATH>","dispatch_decision":{"confirmed_by_user":true,"response":"y"},"dispatch_event":{"confirmed_by_user":true,"command":["<LOCAL_PATH>","exec","--sandbox","workspace-write","--config","sandbox_workspace_write.exclude_slash_tmp=true","--config","sandbox_workspace_write.exclude_tmpdir_env_var=true","--config","sandbox_workspace_write.writable_roots=[]","--skip-git-repo-check","--ephemeral","--color","never","--output-last-message","<LOCAL_PATH>","-C","<LOCAL_PATH>","-"],"command_line":"<LOCAL_PATH> exec --sandbox workspace-write --config sandbox_workspace_write.exclude_slash_tmp=true --config sandbox_workspace_write.exclude_tmpdir_env_var=true --config sandbox_workspace_write.writable_roots=[] --skip-git-repo-check --ephemeral --color never --output-last-message <LOCAL_PATH> -C <LOCAL_PATH> -","prompt_transport":"stdin","prompt_sha256":"174be79ab948bb4c57418d76115c587e5fa40a4f58d19c0c958a310394ca1987","sandbox":"workspace-write","working_directory":"<LOCAL_PATH>","exit_code":0,"elapsed_seconds":164.377,"final_output":"已在 [to_pgm.py](<<LOCAL_PATH>>) 实现 `to_pgm(width, height, pixels)`。它会生成指定的 P5 头部并拼接像素字节；参数不符合要求时抛出 `ValueError`。","stdout":"已在 [to_pgm.py](<<LOCAL_PATH>>) 实现 `to_pgm(width, height, pixels)`。它会生成指定的 P5 头部并拼接像素字节；参数不符合要求时抛出 `ValueError`。\n","stderr":"2026-11-06T06:19:21.977207Z  WARN codex_skills::interface: ignoring interface.icon_small: icon path with '..' must resolve under plugin assets/\n2026-11-06T06:19:21.977250Z  WARN codex_skills::interface: ignoring interface.icon_large: icon path with '..' must resolve under plugin assets/\n2026-11-06T06:19:21.983688Z  WARN codex_core::shell_snapshot: Failed to create shell snapshot for powershell: Shell snapshot not supported yet for PowerShell\nOpenAI Codex v0.167.0-alpha.3.2\n--------\nworkdir: <LOCAL_PATH>\nmodel: gpt-6-luna\nprovider: openai\napproval: never\nsandbox: workspace-write [workdir]\nreasoning effort: xhigh\nreasoning summaries: none\nsession id: 01a1af83-05e6-74a2-ab6a-c62494f4b461\n--------\nuser\n执行下面完整的 Codex handoff payload。所有新建或修改的文件只能放在当前工作目录内；实现请求应在该目录中生成对应源码文件。\n\n--- handoff payload begin ---\n## 用户当前请求（原文）\n\n用 Python 写 to_pgm(width, height, pixels)，返回 P5 PGM 字节串。宽高为正整数，pixels 为长度等于宽乘高的 bytes，像素从左上角逐行排列。用 ASCII 写三行头部，第一行 P5，第二行是宽和高（用一个空格分隔），第三行 255，每行以 LF 结束，最后原样拼接像素。参数不合要求就抛 ValueError，不写文件。\n\n## 处理要求\n\n保留用户原意，不要补造需求。若缺少完成任务所必需的信息，先向用户澄清。\n--- handoff payload end ---\nwarning: Codex is ignoring 1 unrecognized configuration setting. Check for typos or deprecated settings.\n  user (<LOCAL_PATH> `computer_use.windows.always_allowed_app_ids` is ignored.\nwarning: Codex is ignoring 1 unrecognized configuration setting. Check for typos or deprecated settings.\n  user (<LOCAL_PATH> `computer_use.windows.always_allowed_app_ids` is ignored.\n2026-11-06T06:19:24.046070Z  WARN codex_skills_extension::loader::metadata: ignoring file:///C:<LOCAL_PATH> invalid openai.yaml: policy.products[0]: unknown variant `CHAT`, expected one of `CHATGPT`, `chatgpt`, `CODEX`, `codex`, `ATLAS`, `atlas` at line 8 column 5\n2026-11-06T06:19:24.046190Z  WARN codex_skills_extension::loader::metadata: ignoring file:///C:<LOCAL_PATH> invalid openai.yaml: policy.products[0]: unknown variant `CHAT`, expected one of `CHATGPT`, `chatgpt`, `CODEX`, `codex`, `ATLAS`, `atlas` at line 8 column 5\n2026-11-06T06:19:24.046214Z  WARN codex_skills_extension::loader::metadata: ignoring file:///C:<LOCAL_PATH> invalid openai.yaml: policy.products[0]: unknown variant `CHAT`, expected one of `CHATGPT`, `chatgpt`, `CODEX`, `codex`, `ATLAS`, `atlas` at line 8 column 5\n2026-11-06T06:19:24.046238Z  WARN codex_skills_extension::loader::metadata: ignoring file:///C:<LOCAL_PATH> invalid openai.yaml: policy.products[0]: unknown variant `CHAT`, expected one of `CHATGPT`, `chatgpt`, `CODEX`, `codex`, `ATLAS`, `atlas` at line 8 column 7\n2026-11-06T06:19:24.046279Z  WARN codex_skills_extension::loader::metadata: ignoring file:///C:<LOCAL_PATH> invalid openai.yaml: policy.products[0]: unknown variant `CHAT`, expected one of `CHATGPT`, `chatgpt`, `CODEX`, `codex`, `ATLAS`, `atlas` at line 8 column 5\n2026-11-06T06:19:24.046299Z  WARN codex_skills_extension::loader::metadata: ignoring file:///C:<LOCAL_PATH> invalid openai.yaml: policy.products[0]: unknown variant `CHAT`, expected one of `CHATGPT`, `chatgpt`, `CODEX`, `codex`, `ATLAS`, `atlas` at line 8 column 5\n2026-11-06T06:19:24.064887Z  WARN codex_skills::interface: ignoring interface.icon_small: icon path with '..' must resolve under plugin assets/\n2026-11-06T06:19:24.064915Z  WARN codex_skills::interface: ignoring interface.icon_large: icon path with '..' must resolve under plugin assets/\n2026-11-06T06:19:53.492358Z  WARN codex_core::responses_retry: stream disconnected - retrying sampling request (1/5 in 181ms)... turn_id=01a1af83-0c1b-7691-80dc-d35652d8afd0 retries=1 max_retries=5 sampling_error=request timed out\n2026-11-06T06:20:08.695781Z  WARN codex_core::responses_retry: stream disconnected - retrying sampling request (2/5 in 385ms)... turn_id=01a1af83-0c1b-7691-80dc-d35652d8afd0 retries=2 max_retries=5 sampling_error=request timed out\nERROR: Reconnecting... 2/5\n2026-11-06T06:20:24.103424Z  WARN codex_core::responses_retry: stream disconnected - retrying sampling request (3/5 in 867ms)... turn_id=01a1af83-0c1b-7691-80dc-d35652d8afd0 retries=3 max_retries=5 sampling_error=request timed out\nERROR: Reconnecting... 3/5\n2026-11-06T06:20:40.002322Z  WARN codex_core::responses_retry: stream disconnected - retrying sampling request (4/5 in 1.724s)... turn_id=01a1af83-0c1b-7691-80dc-d35652d8afd0 retries=4 max_retries=5 sampling_error=request timed out\nERROR: Reconnecting... 4/5\n2026-11-06T06:20:56.754269Z  WARN codex_core::responses_retry: stream disconnected - retrying sampling request (5/5 in 3.187s)... turn_id=01a1af83-0c1b-7691-80dc-d35652d8afd0 retries=5 max_retries=5 sampling_error=request timed out\nERROR: Reconnecting... 5/5\n2026-11-06T06:21:14.965054Z  WARN codex_core::client: falling back to HTTP\nwarning: Falling back from WebSockets to HTTPS transport. request timed out\ncodex\n我先查看当前目录的文件和项目约定，再把 `to_pgm` 实现在工作目录内合适的 Python 源码文件中。\nexec\n\"C:\\\\Users\\\\<LOCAL_USER>\\\\.cache\\\\codex-runtimes\\\\codex-primary-runtime\\\\dependencies\\\\native\\\\powershell\\\\pwsh.exe\" -Command \"Get-Content 'C:\\\\Users\\\\<LOCAL_USER>\\\\.codex\\\\memories\\\\MEMORY.md' -ErrorAction SilentlyContinue | Select-String -Pattern '轻量分类决策器|to_pgm|PGM' -Context 2,2; Get-ChildItem -Force | Select-Object Mode,Name\" in <LOCAL_PATH>\n succeeded in 521ms:\nexec\n\"C:\\\\Users\\\\<LOCAL_USER>\\\\.cache\\\\codex-runtimes\\\\codex-primary-runtime\\\\dependencies\\\\native\\\\powershell\\\\pwsh.exe\" -Command 'Get-Location; rg --files -uu' in <LOCAL_PATH>\n exited 1 in 494ms:\n\nPath\n----\n<LOCAL_PATH>\n\n\ncodex\n当前工作目录没有现有源码文件，我会新增 `to_pgm.py`。实现会把布尔值排除在整数尺寸之外，并对错误类型、非正尺寸和像素长度不符统一抛出 `ValueError`。\napply patch\npatch: completed\n<LOCAL_PATH>\ndiff --git a/workspace/codex_runs/4c5489f9-ef57-4729-8207-63a4d36a4b38/to_pgm.py b/workspace/codex_runs/4c5489f9-ef57-4729-8207-63a4d36a4b38/to_pgm.py\nnew file mode 100644\nindex 0000000000000000000000000000000000000000..ebca766ef0b105abf0d0af3159398032d35f4c90\n--- /dev/null\n+++ b/workspace/codex_runs/4c5489f9-ef57-4729-8207-63a4d36a4b38/to_pgm.py\n@@ -0,0 +1,25 @@\n+\"\"\"Build P5 PGM image data in memory.\"\"\"\n+\n+\n+def to_pgm(width, height, pixels):\n+    \"\"\"Return a P5 PGM byte string for row-major 8-bit pixels.\n+\n+    Raises:\n+        ValueError: If dimensions are not positive integers or ``pixels`` is\n+            not bytes with exactly ``width * height`` entries.\n+    \"\"\"\n+    if (\n+        not isinstance(width, int)\n+        or isinstance(width, bool)\n+        or width <= 0\n+        or not isinstance(height, int)\n+        or isinstance(height, bool)\n+        or height <= 0\n+    ):\n+        raise ValueError(\"width and height must be positive integers\")\n+\n+    if not isinstance(pixels, bytes) or len(pixels) != width * height:\n+        raise ValueError(\"pixels must be bytes of length width * height\")\n+\n+    header = f\"P5\\n{width} {height}\\n255\\n\".encode(\"ascii\")\n+    return header + pixels\n\nexec\n\"C:\\\\Users\\\\<LOCAL_USER>\\\\.cache\\\\codex-runtimes\\\\codex-primary-runtime\\\\dependencies\\\\native\\\\powershell\\\\pwsh.exe\" -Command \"Get-Content .\\\\to_pgm.py; git status --short\" in <LOCAL_PATH>\n succeeded in 496ms:\n\"\"\"Build P5 PGM image data in memory.\"\"\"\n\n\ndef to_pgm(width, height, pixels):\n    \"\"\"Return a P5 PGM byte string for row-major 8-bit pixels.\n\n    Raises:\n        ValueError: If dimensions are not positive integers or ``pixels`` is\n            not bytes with exactly ``width * height`` entries.\n    \"\"\"\n    if (\n        not isinstance(width, int)\n        or isinstance(width, bool)\n        or width <= 0\n        or not isinstance(height, int)\n        or isinstance(height, bool)\n        or height <= 0\n    ):\n        raise ValueError(\"width and height must be positive integers\")\n\n    if not isinstance(pixels, bytes) or len(pixels) != width * height:\n        raise ValueError(\"pixels must be bytes of length width * height\")\n\n    header = f\"P5\\n{width} {height}\\n255\\n\".encode(\"ascii\")\n    return header + pixels\n?? ../../../.gitignore\n?? ../../../DATA_SOURCES.md\n?? ../../../README.md\n?? ../../../answer_worker_7b_report.md\n?? ../../../data/\n?? ../../../executor.py\n?? ../../../install_and_answer_worker_report.md\n?? ../../../light_decider/\n?? ../../../outputs/\n?? ../../../phase2_codex_live_report.md\n?? ../../../requirements-data-build.txt\n?? ../../../requirements-semantic-runtime.txt\n?? ../../../requirements-semantic-training.txt\n?? ../../../requirements.txt\n?? ../../../scripts/\n?? ../../../super_agent_phase1_design.md\n?? ../../../try_router.py\n?? ../../../try_router_semantic.py\n?? ../../\n\ncodex\n已在 [to_pgm.py](<<LOCAL_PATH>>) 实现 `to_pgm(width, height, pixels)`。它会生成指定的 P5 头部并拼接像素字节；参数不符合要求时抛出 `ValueError`。\ntokens used\n52,300\n","error":null,"timed_out":false,"files":{"added":[{"path":"to_pgm.py","type":"file","sha256":"d87e66c14cda80bdee012fc44197f139b65c0399789c78e60d190c6098f3e0b7","size_bytes":813}],"modified":[],"removed":[]}},"final_output":"已在 [to_pgm.py](<<LOCAL_PATH>>) 实现 `to_pgm(width, height, pixels)`。它会生成指定的 P5 头部并拼接像素字节；参数不符合要求时抛出 `ValueError`。","workspace_file_changes":{"added":[{"path":"to_pgm.py","type":"file","sha256":"d87e66c14cda80bdee012fc44197f139b65c0399789c78e60d190c6098f3e0b7","size_bytes":813}],"modified":[],"removed":[]}}
```

## 无开关回归与保护文件

- `python -X utf8 -B scripts/drill_executor_clarify_loop.py` 通过：clarify→codex、clarify→decide、两轮 clarify 熔断演练通过；无 `--execute` 时与 `try_router.py` 及变更前缓存 stdout 逐字节一致。stdout 907 字节，SHA-256 `5efc7d8b788deeab3b78d14c0d853676e5d91d5f867fda0cda6165bcb1803077`，stderr 为空。
- 该回归同时核对 route model、现役 routing policy 和 v6 冻结标签哈希与既有记录一致。
- 不带开关路径仍直接委托原路由 CLI；`--execute-dry-run` 不创建 Codex dispatcher；decide 继续走原 Answer Worker，clarify 回路未改。
