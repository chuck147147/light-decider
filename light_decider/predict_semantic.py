from __future__ import annotations

import argparse
import json
from pathlib import Path

from .semantic_runtime import SemanticIntentModel, suggest_route


def main() -> None:
    parser = argparse.ArgumentParser(description="Suggest a route with the fine-tuned Chinese intent model.")
    parser.add_argument("--model", type=Path, default=Path("artifacts/decisioner_semantic_draft"))
    parser.add_argument("--text", required=True, help="The user's latest message.")
    parser.add_argument(
        "--strip-fenced-code",
        action="store_true",
        help="Ignore Markdown code blocks for intent classification while keeping the original handoff text.",
    )
    parser.add_argument(
        "--context",
        default="[]",
        help='JSON list, for example: [{"role":"assistant","text":"..."}]',
    )
    args = parser.parse_args()
    if not args.text.strip():
        raise SystemExit("--text must not be empty.")
    try:
        context = json.loads(args.context)
    except json.JSONDecodeError as error:
        raise SystemExit(f"Invalid --context JSON: {error}") from error
    if not isinstance(context, list) or any(
        not isinstance(message, dict) or not isinstance(message.get("text"), str)
        for message in context
    ):
        raise SystemExit("--context must be a JSON list of objects with string 'text' fields.")
    if any("role" in message and not isinstance(message["role"], str) for message in context):
        raise SystemExit("Each context role must be a string when provided.")

    model = SemanticIntentModel(args.model)
    result = suggest_route(
        model,
        args.text,
        context,
        ignore_fenced_code_for_routing=args.strip_fenced_code,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
