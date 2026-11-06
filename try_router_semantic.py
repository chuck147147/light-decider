from __future__ import annotations

import argparse
import json
from functools import partial
from pathlib import Path

from light_decider.predict import DEFAULT_MODEL_PATH, load_artifact
from light_decider.predict import suggest_route as suggest_light_route
from light_decider.semantic_runtime import SemanticIntentModel
from light_decider.semantic_runtime import suggest_route as suggest_semantic_route


MODEL_PATH = Path(__file__).resolve().parent / "artifacts" / "decisioner_semantic_draft"
SHADOW_LOG_PATH = Path(__file__).resolve().parent / "logs" / "shadow" / "light_decider_v3_1.jsonl"


def read_context() -> list[dict[str, str]] | None:
    raw_context = input("上下文 JSON（不需要就直接回车）> ").strip()
    if not raw_context:
        return []
    try:
        context = json.loads(raw_context)
    except json.JSONDecodeError as error:
        print(f"JSON 格式错误：{error}")
        return None
    if not isinstance(context, list) or any(
        not isinstance(message, dict) or not isinstance(message.get("text"), str)
        for message in context
    ):
        print('上下文必须是 JSON 数组，例如：[{"role":"assistant","text":"之前的方案"}]')
        return None
    if any("role" in message and not isinstance(message["role"], str) for message in context):
        print("上下文中的 role 必须是字符串。")
        return None
    return context


def main(*, default_model: Path = MODEL_PATH) -> None:
    parser = argparse.ArgumentParser(description="交互式测试中文三路决策器。")
    parser.add_argument("--model", type=Path, help="轻量模型 joblib 文件或语义模型目录。")
    parser.add_argument(
        "--strip-fenced-code",
        action="store_true",
        help="实验性输入预处理：意图判断时忽略 Markdown 代码块，Codex handoff 仍保留原文。",
    )
    parser.add_argument(
        "--shadow",
        action="store_true",
        help="旁路运行默认轻量模型与 routing_policy v3.1，只写 JSONL 影子日志。",
    )
    parser.add_argument("--shadow-model", type=Path, default=DEFAULT_MODEL_PATH, help="影子模型 joblib 文件。")
    parser.add_argument("--shadow-log", type=Path, default=SHADOW_LOG_PATH, help="影子 JSONL 日志路径。")
    args = parser.parse_args()
    model_path = args.model or (MODEL_PATH if args.strip_fenced_code else default_model)
    if model_path.suffix.lower() == ".joblib":
        if args.strip_fenced_code:
            parser.error("--strip-fenced-code 需要语义模型目录。")
        route_request = partial(suggest_light_route, load_artifact(model_path))
        model_kind = "轻量模型"
    else:
        if not model_path.exists():
            raise SystemExit(f"找不到语义模型：{model_path}。先运行训练和导出步骤。")
        route_request = partial(
            suggest_semantic_route,
            SemanticIntentModel(model_path),
            ignore_fenced_code_for_routing=args.strip_fenced_code,
        )
        model_kind = "语义模型"
    shadow_observer = None
    if args.shadow:
        try:
            from light_decider.shadow import ShadowObserver

            shadow_observer = ShadowObserver(load_artifact(args.shadow_model), args.shadow_log)
        except Exception as error:
            print(f"影子模式未启动，主路由照常运行：{error}")
    print(f"已加载{model_kind}：{model_path.name}")
    print("输入 /exit 结束。概率尚未校准，当前只给路由建议，不会自动派发。")

    while True:
        try:
            text = input("\n当前消息> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n结束测试。")
            break
        if text.lower() in {"/exit", "/quit", "exit", "quit"}:
            print("结束测试。")
            break
        if not text:
            continue
        context = read_context()
        if context is None:
            continue
        if shadow_observer is not None:
            shadow_observer.observe(text, context)
        result = route_request(text, context)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
