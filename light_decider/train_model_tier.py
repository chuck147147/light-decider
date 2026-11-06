from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import joblib
from sklearn.metrics import classification_report
from sklearn.model_selection import GroupShuffleSplit

from . import model
from .model import format_input
from .model_tier import MODEL_TIERS, validate_model_tiers


def load_examples(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(
            f"Training data not found: {path}. See data/model_tier/README.md for the format."
        )

    examples: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    policy_ids: set[str] = set()

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise SystemExit(f"Invalid JSON on line {line_number}: {error}") from error
        if not isinstance(row, dict):
            raise SystemExit(f"Line {line_number}: each JSON value must be an object.")

        required = (
            "id",
            "group_id",
            "text",
            "label",
            "approved_for_training",
            "routing_policy_id",
            "source_dataset",
            "source_id",
        )
        missing = [key for key in required if key not in row]
        if missing:
            raise SystemExit(f"Line {line_number} is missing fields: {', '.join(missing)}")
        for key in ("id", "group_id", "text", "routing_policy_id", "source_dataset", "source_id"):
            if not isinstance(row[key], str) or not row[key].strip():
                raise SystemExit(f"Line {line_number}: {key} must be a non-empty string.")
        if row["id"] in seen_ids:
            raise SystemExit(f"Line {line_number}: duplicate id {row['id']!r}.")
        seen_ids.add(row["id"])
        if not isinstance(row["approved_for_training"], bool):
            raise SystemExit(f"Line {line_number}: approved_for_training must be true or false.")
        if not isinstance(row["label"], str):
            raise SystemExit(f"Line {line_number}: label must be a string.")
        if "context" in row and not isinstance(row["context"], list):
            raise SystemExit(f"Line {line_number}: context must be a list.")
        if any(
            not isinstance(item, dict)
            or not isinstance(item.get("text"), str)
            or ("role" in item and not isinstance(item["role"], str))
            for item in row.get("context", [])
        ):
            raise SystemExit(f"Line {line_number}: each context item must have a string 'text'.")

        if not row["approved_for_training"]:
            continue
        try:
            validate_model_tiers([row["label"]])
        except ValueError as error:
            raise SystemExit(f"Line {line_number}: {error}") from error
        policy_ids.add(row["routing_policy_id"])
        examples.append(row)

    if not examples:
        raise SystemExit("No approved examples found. See data/model_tier/README.md.")
    if len(policy_ids) != 1:
        raise SystemExit(
            "Train one model per routing_policy_id. Do not combine different model pairs or quality thresholds."
        )

    labels = [row["label"] for row in examples]
    validate_model_tiers(labels)
    missing_tiers = sorted(set(MODEL_TIERS) - set(labels))
    if missing_tiers:
        raise SystemExit(f"Approved data is missing model tiers: {', '.join(missing_tiers)}")
    return examples


def choose_grouped_split(
    texts: list[str], labels: list[str], groups: list[str]
) -> tuple[Any, Any] | None:
    if len(set(groups)) < 5:
        return None
    splitter = GroupShuffleSplit(n_splits=100, test_size=0.2, random_state=42)
    best_split: tuple[Any, Any] | None = None
    best_validation_coverage = -1
    for train_indices, validation_indices in splitter.split(texts, labels, groups):
        if {labels[index] for index in train_indices} != set(MODEL_TIERS):
            continue
        validation_labels = {labels[index] for index in validation_indices}
        if len(validation_labels) > best_validation_coverage:
            best_split = (train_indices, validation_indices)
            best_validation_coverage = len(validation_labels)
        if validation_labels == set(MODEL_TIERS):
            break
    return best_split


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the separate lightweight model-tier router.")
    parser.add_argument("--data", type=Path, default=Path("data/model_tier/annotations.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/model_tier.joblib"))
    args = parser.parse_args()

    examples = load_examples(args.data)
    texts = [format_input(row["text"], row.get("context", [])) for row in examples]
    labels = [row["label"] for row in examples]
    groups = [row["group_id"] for row in examples]
    counts = Counter(labels)

    split = choose_grouped_split(texts, labels, groups)
    if split is None:
        raise SystemExit(
            "Need at least five distinct prompt groups and both model tiers in training. "
            "Add more approved groups for both labels."
        )
    train_indices, validation_indices = split
    validation_tiers = {labels[index] for index in validation_indices}
    if validation_tiers != set(MODEL_TIERS):
        missing = sorted(set(MODEL_TIERS) - validation_tiers)
        print(f"Warning: holdout data is missing tiers {missing}; those metrics are not measurable yet.")

    pipeline = model.build_pipeline()
    pipeline.fit([texts[index] for index in train_indices], [labels[index] for index in train_indices])
    predictions = pipeline.predict([texts[index] for index in validation_indices])
    metrics = classification_report(
        [labels[index] for index in validation_indices],
        predictions,
        labels=list(MODEL_TIERS),
        output_dict=True,
        zero_division=0,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "pipeline": pipeline,
            "task": "model_tier",
            "tiers": list(MODEL_TIERS),
            "routing_policy_id": examples[0]["routing_policy_id"],
            "probabilities_calibrated": False,
            "training_data_status": "approved_derived_labels",
            "training_label_counts": dict(counts),
        },
        args.output,
    )
    metrics_path = args.output.with_suffix(".metrics.json")
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved model: {args.output}")
    print(f"Saved holdout metrics: {metrics_path}")
    print("Raw class scores are not calibrated; do not use them as automatic-dispatch thresholds.")


if __name__ == "__main__":
    main()
