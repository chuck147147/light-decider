from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .predict import suggest_route
from .routing_policy import POLICY_VERSION


DEFAULT_FUSE_THRESHOLD = 0.6


class ShadowObserver:
    """Record a lightweight route in the shadow log."""

    def __init__(
        self,
        artifact: dict[str, Any],
        log_path: Path,
        *,
        fuse_threshold: float = DEFAULT_FUSE_THRESHOLD,
        source: str = "shadow_real_request",
    ) -> None:
        if not 0 <= fuse_threshold <= 1:
            raise ValueError("fuse_threshold must be between 0 and 1")
        self.artifact = artifact
        self.log_path = log_path
        self.fuse_threshold = fuse_threshold
        self.source = source

    def observe(
        self,
        text: str,
        context: list[dict[str, str]] | None = None,
        *,
        sample_id: str | None = None,
    ) -> dict[str, Any]:
        timestamp = datetime.now(timezone.utc).isoformat()
        try:
            result = suggest_route(self.artifact, text, context or [])
            scores = {str(route): float(score) for route, score in result["scores"].items()}
            argmax = str(result["suggested_route"])
            top_score = float(result["top_score"])
            final_action = str(result["action"])
            override_log = list(result.get("override_log", []))
            flips = [
                {
                    "rule_name": event.get("rule_name"),
                    "before": event.get("before"),
                    "after": event.get("after"),
                    "applied": event.get("applied"),
                }
                for event in override_log
                if event.get("before") != event.get("after")
            ]
            high_risk_domains = list(result.get("high_risk_domains", []))
            fuse_reasons = []
            if high_risk_domains:
                fuse_reasons.append("high_risk_domain")
            if top_score < self.fuse_threshold:
                fuse_reasons.append("top_score_below_threshold")
            entry: dict[str, Any] = {
                "schema_version": "light_decider_shadow_v1",
                "timestamp_utc": timestamp,
                "source": self.source,
                "sample_id": sample_id,
                "request_text": text,
                "context": context or [],
                "model": self.artifact.get("model_filename", "unknown"),
                "model_argmax": argmax,
                "model_scores": scores,
                "top_score": top_score,
                "probabilities_calibrated": False,
                "policy_version": POLICY_VERSION,
                "policy_final_action": final_action,
                "flip_record": {
                    "flipped": argmax != final_action,
                    "rules": flips,
                    "all_overrides": override_log,
                },
                "high_risk_domains": high_risk_domains,
                "fuse": {
                    "threshold": self.fuse_threshold,
                    "would_route_to_human": bool(fuse_reasons),
                    "reasons": fuse_reasons,
                },
                "automatic_dispatch_allowed": False,
                "training_eligible": False,
            }
        except Exception as error:  # A shadow failure must not affect the primary path.
            entry = {
                "schema_version": "light_decider_shadow_v1",
                "timestamp_utc": timestamp,
                "source": self.source,
                "sample_id": sample_id,
                "request_text": text,
                "context": context or [],
                "policy_version": POLICY_VERSION,
                "observer_error": f"{type(error).__name__}: {error}",
                "fuse": {
                    "threshold": self.fuse_threshold,
                    "would_route_to_human": True,
                    "reasons": ["shadow_observer_error"],
                },
                "automatic_dispatch_allowed": False,
                "training_eligible": False,
            }

        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open("a", encoding="utf-8", newline="\n") as file:
                file.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")
        except Exception:
            # Shadow logging is best effort and must never break the primary route.
            pass
        return entry
