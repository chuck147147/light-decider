from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib

from .model import predict_scores
from .model_tier import MODEL_TIERS


def load_artifact(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Model not found: {path}. Train a model-tier model first.")
    artifact = joblib.load(path)
    if (
        not isinstance(artifact, dict)
        or artifact.get("task") != "model_tier"
        or "pipeline" not in artifact
        or tuple(artifact.get("tiers", ())) != MODEL_TIERS
    ):
        raise SystemExit(f"Invalid model-tier artifact: {path}")
    return artifact


def suggest_model_tier(
    artifact: dict[str, Any], text: str, context: list[dict[str, str]] | None = None
) -> dict[str, Any]:
    scores = predict_scores(artifact["pipeline"], text, context)
    suggested_tier, top_score = max(scores.items(), key=lambda item: item[1])
    return {
        "task": "model_tier",
        "suggested_tier": suggested_tier,
        "scores": scores,
        "top_score": top_score,
        "routing_policy_id": artifact.get("routing_policy_id"),
        "probabilities_calibrated": bool(artifact.get("probabilities_calibrated", False)),
        "automatic_dispatch_allowed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Suggest a model tier; call this only after the action router returns decide."
    )
    parser.add_argument("--model", type=Path, default=Path("artifacts/model_tier.joblib"))
    parser.add_argument("--text", required=True, help="The current user request.")
    parser.add_argument(
        "--context",
        default="[]",
        help='JSON list, for example: [{"role":"user","text":"..."}]',
    )
    args = parser.parse_args()
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
        raise SystemExit("Each --context role must be a string when provided.")

    artifact = load_artifact(args.model)
    result = suggest_model_tier(artifact, args.text, context)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
