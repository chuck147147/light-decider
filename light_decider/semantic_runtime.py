from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from . import ROUTES
from .clause_segmentation import split_request_clauses
from .handoff import format_codex_handoff
from .input_normalization import strip_code_from_context, strip_fenced_code_blocks
from .model import format_semantic_input
from .routing_policy import aggregate_policy_results, apply_routing_policy


class SemanticIntentModel:
    """CPU ONNX runtime for the fine-tuned Chinese intent classifier."""

    def __init__(self, model_dir: Path, intra_op_num_threads: int = 2) -> None:
        try:
            import onnxruntime as ort
            from tokenizers import Tokenizer
        except ImportError as error:
            raise RuntimeError(
                "Semantic inference requires onnxruntime and tokenizers. "
                "Install them with: python -m pip install -r requirements-semantic-runtime.txt"
            ) from error

        self.model_dir = model_dir
        metadata_path = model_dir / "metadata.json"
        model_path = model_dir / "model_int8.onnx"
        tokenizer_path = model_dir / "tokenizer.json"
        missing = [path.name for path in (metadata_path, model_path, tokenizer_path) if not path.exists()]
        if missing:
            raise FileNotFoundError(f"Semantic model directory {model_dir} is missing: {', '.join(missing)}")

        self.metadata: dict[str, Any] = json.loads(metadata_path.read_text(encoding="utf-8"))
        if tuple(self.metadata.get("routes", ())) != ROUTES:
            raise ValueError("Semantic model routes do not match the current decisioner routes.")
        self.max_length = int(self.metadata.get("max_length", 192))
        self.truncation_side = self.metadata.get("truncation_side", "right")
        if self.truncation_side not in {"left", "right"}:
            raise ValueError("Semantic model truncation_side must be 'left' or 'right'.")
        self.tokenizer = Tokenizer.from_file(str(tokenizer_path))
        self.tokenizer.enable_truncation(
            max_length=self.max_length,
            direction=self.truncation_side,
        )

        options = ort.SessionOptions()
        options.intra_op_num_threads = max(1, intra_op_num_threads)
        options.inter_op_num_threads = 1
        options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.session = ort.InferenceSession(
            str(model_path),
            sess_options=options,
            providers=["CPUExecutionProvider"],
        )
        self.input_names = {item.name for item in self.session.get_inputs()}
        expected_inputs = {"input_ids", "attention_mask", "token_type_ids"}
        if not expected_inputs.issubset(self.input_names):
            raise ValueError(f"ONNX model inputs {sorted(self.input_names)} do not include {sorted(expected_inputs)}")

    def predict_scores(self, text: str, context: list[dict[str, str]] | None = None) -> dict[str, float]:
        rendered = format_semantic_input(text, context)
        encoding = self.tokenizer.encode(rendered, add_special_tokens=True)
        inputs = {
            "input_ids": np.asarray([encoding.ids], dtype=np.int64),
            "attention_mask": np.asarray([encoding.attention_mask], dtype=np.int64),
            "token_type_ids": np.asarray([encoding.type_ids], dtype=np.int64),
        }
        logits = self.session.run(["logits"], inputs)[0][0].astype(np.float64)
        logits -= np.max(logits)
        probabilities = np.exp(logits)
        probabilities /= probabilities.sum()
        return {
            route: float(score)
            for route, score in zip(ROUTES, probabilities.tolist(), strict=True)
        }


def suggest_route(
    model: SemanticIntentModel,
    text: str,
    context: list[dict[str, str]] | None = None,
    *,
    ignore_fenced_code_for_routing: bool = False,
) -> dict[str, Any]:
    routing_text = text
    policy_context = context
    model_context = context
    removed_code = False
    if ignore_fenced_code_for_routing:
        routing_text, removed_from_request = strip_fenced_code_blocks(text)
        model_context, removed_from_context = strip_code_from_context(context)
        removed_code = removed_from_request or removed_from_context
        policy_context = model_context
        if removed_code:
            policy_context = [
                *(policy_context or []),
                {"role": "user_context", "text": "用户已提供相关内容。"},
            ]

    initial_override_reason = "code_only_message_without_request" if removed_code and not routing_text else None
    whole_request = _classify(
        model,
        routing_text,
        policy_context,
        model_context,
        parent_request_text=routing_text,
        initial_override_reason=initial_override_reason,
    )

    clauses = split_request_clauses(routing_text)
    clause_analysis: list[dict[str, Any]] = []

    if len(clauses) <= 1 or whole_request.get("policy_override") == "direct_text_transformation":
        clause_analysis.append({"text": text.strip(), **whole_request})
        aggregate = aggregate_policy_results(whole_request, [])
        action = aggregate["action"]
        reason = aggregate["reason"]
        policy_override = aggregate["policy_override"]
    else:
        full_request_context = [
            *(model_context or []),
            {"role": "user_context", "text": f"完整用户请求：{routing_text.strip()}"},
        ]
        for clause in clauses:
            clause_analysis.append({
                "text": clause,
                **_classify(
                    model,
                    clause,
                    policy_context,
                    full_request_context,
                    parent_request_text=routing_text,
                ),
            })
        aggregate = aggregate_policy_results(whole_request, clause_analysis)
        action = aggregate["action"]
        reason = aggregate["reason"]
        policy_override = aggregate["policy_override"]

    suggested_route = whole_request["suggested_route"]
    scores = whole_request["scores"]
    top_score = whole_request["top_score"]
    codex_handoff = (
        format_codex_handoff(
            text,
            context,
            action=action,
            declared_defaults=aggregate["declared_defaults"],
            check_first_targets=aggregate["check_first_targets"],
        )
        if action.startswith("codex")
        else None
    )
    if codex_handoff and len(clause_analysis) > 1:
        clause_lines = [
            f"- [{item['action']}] {item['text']}"
            for item in clause_analysis
        ]
        codex_handoff += "\n\n## 分句路由建议\n\n" + "\n".join(clause_lines)

    return {
        "action": action,
        "suggested_route": suggested_route,
        "codex_handoff": codex_handoff,
        "scores": scores,
        "top_score": top_score,
        "reason": reason,
        "policy_override": policy_override,
        "override_log": aggregate["override_log"],
        "high_risk_domains": aggregate["high_risk_domains"],
        "declared_defaults": aggregate["declared_defaults"],
        "check_first_targets": aggregate["check_first_targets"],
        "clause_analysis": clause_analysis,
        "probabilities_calibrated": False,
        "automatic_dispatch_allowed": False,
    }


def _classify(
    model: SemanticIntentModel,
    text: str,
    policy_context: list[dict[str, str]] | None,
    model_context: list[dict[str, str]] | None,
    *,
    parent_request_text: str | None = None,
    initial_override_reason: str | None = None,
) -> dict[str, Any]:
    scores = model.predict_scores(text, model_context)
    suggested_route, top_score = max(scores.items(), key=lambda item: item[1])
    policy = apply_routing_policy(
        suggested_route,
        text,
        policy_context,
        parent_request_text=parent_request_text,
        initial_override_reason=initial_override_reason,
    )
    return {
        **policy,
        "suggested_route": suggested_route,
        "scores": scores,
        "top_score": top_score,
    }
