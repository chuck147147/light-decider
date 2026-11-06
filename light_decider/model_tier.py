from __future__ import annotations

from collections.abc import Sequence


MODEL_TIERS = ("cheap", "strong")


def validate_model_tiers(labels: Sequence[str]) -> None:
    unknown = sorted(set(labels) - set(MODEL_TIERS))
    if unknown:
        raise ValueError(f"Unknown model tiers {unknown}; expected labels from {MODEL_TIERS}.")

