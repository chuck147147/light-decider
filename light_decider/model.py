from __future__ import annotations

from collections.abc import Mapping, Sequence

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from . import ROUTES


def format_input(text: str, context: Sequence[Mapping[str, str]] | None = None) -> str:
    """Render a short, role-aware context window for the text classifier."""
    parts: list[str] = []
    for message in context or ():
        role_value = message.get("role", "unknown")
        content_value = message.get("text", "")
        role = role_value.strip() if isinstance(role_value, str) else "unknown"
        content = content_value.strip() if isinstance(content_value, str) else ""
        role = role or "unknown"
        if content:
            parts.append(f"[{role}] {content}")
    parts.append(f"[current] {text.strip()}")
    return "\n".join(parts)


def format_semantic_input(
    text: str,
    context: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """Render role-aware Chinese input for the fine-tuned intent encoder."""
    role_names = {
        "user": "用户",
        "assistant": "助手",
        "system": "系统",
        "user_context": "用户背景",
        "assistant_context": "助手背景",
    }
    parts: list[str] = []
    for message in context or ():
        role_value = message.get("role", "unknown")
        content_value = message.get("text", "")
        role = role_value.strip() if isinstance(role_value, str) else "unknown"
        content = content_value.strip() if isinstance(content_value, str) else ""
        if content:
            parts.append(f"{role_names.get(role, '对话')}：{content}")
    parts.append(f"当前用户消息：{text.strip()}")
    return "\n".join(parts)


def build_pipeline(class_weight: dict[str, float] | str | None = None) -> Pipeline:
    """Build a CPU-friendly character n-gram text classifier."""
    return Pipeline(
        steps=[
            (
                "features",
                TfidfVectorizer(
                    analyzer="char",
                    ngram_range=(1, 4),
                    max_features=80_000,
                    min_df=1,
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1_000,
                    random_state=42,
                    class_weight=class_weight,
                ),
            ),
        ]
    )


def predict_scores(pipeline: Pipeline, text: str, context: Sequence[Mapping[str, str]] | None = None) -> dict[str, float]:
    """Return raw class probability estimates; thresholds are intentionally external."""
    rendered = format_input(text, context)
    values = pipeline.predict_proba([rendered])[0]
    classes = pipeline.named_steps["classifier"].classes_
    return {str(label): float(value) for label, value in zip(classes, values, strict=True)}


def validate_routes(labels: Sequence[str]) -> None:
    unknown = sorted(set(labels) - set(ROUTES))
    if unknown:
        raise ValueError(f"Unknown labels {unknown}; expected labels from {ROUTES}.")

