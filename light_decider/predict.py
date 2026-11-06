from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib

from . import ROUTES
from .handoff import format_codex_handoff
from .model import predict_scores
from .routing_policy import apply_routing_policy


DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[1] / "artifacts" / "decisioner_round4_v1_2026-11-05.joblib"


def load_artifact(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Model not found: {path}. Train a model first.")
    artifact = joblib.load(path)
    if not isinstance(artifact, dict) or "pipeline" not in artifact:
        raise SystemExit(f"Invalid model artifact: {path}")
    if tuple(artifact.get("routes", ())) != ROUTES:
        raise SystemExit("Model routes do not match this version of the decisioner.")
    return {**artifact, "model_filename": path.name}


def suggest_route(
    artifact: dict[str, Any],
    text: str,
    context: list[dict[str, str]] | None = None,
    min_score: float | None = None,
) -> dict[str, Any]:
    scores = predict_scores(artifact["pipeline"], text, context)
    suggested_route, top_score = max(scores.items(), key=lambda item: item[1])
    initial_override_reason = None
    if min_score is not None and top_score < min_score:
        initial_override_reason = "below_configured_min_score"

    policy = apply_routing_policy(
        suggested_route,
        text,
        context,
        initial_override_reason=initial_override_reason,
    )

    return {
        **policy,
        "suggested_route": suggested_route,
        "codex_handoff": (
            format_codex_handoff(
                text,
                context,
                action=str(policy["action"]),
                declared_defaults=[policy["declared_default"]] if policy["declared_default"] else [],
                check_first_targets=policy["check_first_targets"],
            )
            if str(policy["action"]).startswith("codex")
            else None
        ),
        "scores": scores,
        "top_score": top_score,
        "probabilities_calibrated": bool(artifact.get("probabilities_calibrated", False)),
        "automatic_dispatch_allowed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Get an experimental route suggestion.")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--text", required=True, help="The user's latest message.")
    parser.add_argument(
        "--context",
        default="[]",
        help='JSON list, for example: [{"role":"user","text":"..."}]',
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=None,
        help="Optional experimental cutoff; raw scores are uncalibrated.",
    )
    args = parser.parse_args()

    if args.min_score is not None and not 0 <= args.min_score <= 1:
        raise SystemExit("--min-score must be between 0 and 1.")
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
    result = suggest_route(artifact, args.text, context, args.min_score)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
