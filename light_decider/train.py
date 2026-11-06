from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import joblib
from sklearn.metrics import classification_report
from sklearn.model_selection import GroupShuffleSplit

from . import ROUTES
from .model import build_pipeline, format_input, validate_routes


ROUTE_CLASS_WEIGHTS = {"decide": 1.0, "codex": 1.0, "clarify": 1.5}


def load_examples(
    path: Path,
    include_machine_translation_drafts: bool = False,
    include_synthetic_chinese_drafts: bool = False,
    include_weak_source_drafts: bool = False,
) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(f"Training data not found: {path}. See data/README.md for the annotation format.")

    examples: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise SystemExit(f"Invalid JSON on line {line_number}: {error}") from error

        if not isinstance(row, dict):
            raise SystemExit(f"Line {line_number}: each JSON value must be an object.")

        required = ("id", "conversation_id", "text", "label", "reviewed")
        missing = [key for key in required if key not in row]
        if missing:
            raise SystemExit(f"Line {line_number} is missing fields: {', '.join(missing)}")
        if not isinstance(row["id"], str) or not row["id"].strip():
            raise SystemExit(f"Line {line_number}: id must be a non-empty string.")
        if row["id"] in seen_ids:
            raise SystemExit(f"Line {line_number}: duplicate id {row['id']!r}.")
        seen_ids.add(row["id"])
        if not isinstance(row["conversation_id"], str) or not row["conversation_id"].strip():
            raise SystemExit(f"Line {line_number}: conversation_id must be a non-empty string.")
        if not isinstance(row["text"], str) or not row["text"].strip():
            raise SystemExit(f"Line {line_number}: text must be a non-empty string.")
        if "context" in row and not isinstance(row["context"], list):
            raise SystemExit(f"Line {line_number}: context must be a list.")
        if any(
            not isinstance(item, dict)
            or not isinstance(item.get("text"), str)
            or ("role" in item and not isinstance(item["role"], str))
            for item in row.get("context", [])
        ):
            raise SystemExit(f"Line {line_number}: each context item must have string field 'text'.")
        if not isinstance(row["label"], str):
            raise SystemExit(f"Line {line_number}: label must be a string.")
        if not isinstance(row["reviewed"], bool):
            raise SystemExit(f"Line {line_number}: reviewed must be true or false.")
        is_machine_translation_draft = (
            row.get("route_reviewed") is True
            and row.get("translation_status") == "machine_translation_draft"
        )
        is_synthetic_chinese_draft = (
            row.get("route_reviewed") is True
            and row.get("translation_status") == "synthetic_chinese_draft"
        )
        is_weak_source_draft = (
            row.get("source_dataset") == "Chinese-Ambiguous-Reference"
            and row.get("label_method") == "weak_next_staff_strategy_mapping"
            and row.get("translation_status") == "weak_label_draft"
        )
        if row["reviewed"] or (
            include_machine_translation_drafts and is_machine_translation_draft
        ) or (include_synthetic_chinese_drafts and is_synthetic_chinese_draft) or (
            include_weak_source_drafts and is_weak_source_draft
        ):
            examples.append(row)
    return examples


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the lightweight route classifier.")
    parser.add_argument("--data", type=Path, default=Path("data/annotations.jsonl"))
    parser.add_argument(
        "--additional-data",
        type=Path,
        action="append",
        default=[],
        help="Add another JSONL file; may be specified more than once.",
    )
    parser.add_argument("--output", type=Path, default=Path("artifacts/decisioner.joblib"))
    parser.add_argument(
        "--include-machine-translation-drafts",
        action="store_true",
        help="Train an explicitly experimental model from assistant-reviewed routes with machine-translated Chinese text.",
    )
    parser.add_argument(
        "--include-synthetic-chinese-drafts",
        action="store_true",
        help="Include Codex-labeled native-Chinese synthetic drafts for an experimental model.",
    )
    parser.add_argument(
        "--include-weak-source-drafts",
        action="store_true",
        help="Include weakly mapped source examples for an experimental model.",
    )
    args = parser.parse_args()

    examples: list[dict[str, Any]] = []
    for data_path in (args.data, *args.additional_data):
        examples.extend(
            load_examples(
                data_path,
                include_machine_translation_drafts=args.include_machine_translation_drafts,
                include_synthetic_chinese_drafts=args.include_synthetic_chinese_drafts,
                include_weak_source_drafts=args.include_weak_source_drafts,
            )
        )
    if not examples:
        raise SystemExit("No approved examples found. Add reviewed rows or enable a draft-data option.")

    ids = [row["id"] for row in examples]
    if len(ids) != len(set(ids)):
        raise SystemExit("Duplicate example IDs found across the supplied JSONL files.")
    labels = [row["label"] for row in examples]
    validate_routes(labels)
    counts = Counter(labels)
    missing_routes = sorted(set(ROUTES) - set(counts))
    if missing_routes:
        raise SystemExit(f"Training data is missing route labels: {', '.join(missing_routes)}")
    texts = [format_input(row["text"], row.get("context", [])) for row in examples]
    groups = [row["conversation_id"] for row in examples]

    if len(set(groups)) < 5:
        raise SystemExit("Need at least five distinct conversations for a grouped holdout split.")

    splitter = GroupShuffleSplit(n_splits=50, test_size=0.2, random_state=42)
    best_split: tuple[Any, Any] | None = None
    best_validation_coverage = -1
    for candidate_train, candidate_validation in splitter.split(texts, labels, groups):
        candidate_train_labels = {labels[index] for index in candidate_train}
        candidate_validation_labels = {labels[index] for index in candidate_validation}
        if candidate_train_labels != set(ROUTES):
            continue
        if len(candidate_validation_labels) > best_validation_coverage:
            best_split = (candidate_train, candidate_validation)
            best_validation_coverage = len(candidate_validation_labels)
        if candidate_validation_labels == set(ROUTES):
            break

    if best_split is None:
        raise SystemExit(
            "Could not create a conversation-level split with all three labels in training. "
            "Add reviewed examples for each route across more conversations."
        )
    train_indices, validation_indices = best_split
    validation_labels = {labels[index] for index in validation_indices}
    if validation_labels != set(ROUTES):
        missing = sorted(set(ROUTES) - validation_labels)
        print(f"Warning: holdout data is missing routes {missing}; those validation metrics are not measurable yet.")

    pipeline = build_pipeline(class_weight=ROUTE_CLASS_WEIGHTS)
    pipeline.fit([texts[index] for index in train_indices], [labels[index] for index in train_indices])
    predictions = pipeline.predict([texts[index] for index in validation_indices])
    metrics = classification_report(
        [labels[index] for index in validation_indices],
        predictions,
        labels=list(ROUTES),
        output_dict=True,
        zero_division=0,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "pipeline": pipeline,
            "routes": list(ROUTES),
            "class_weights": ROUTE_CLASS_WEIGHTS,
            "probabilities_calibrated": False,
            "training_data_status": (
                "experimental_drafts"
                if any(not row["reviewed"] for row in examples)
                else "reviewed_annotations"
            ),
        },
        args.output,
    )
    metrics_path = args.output.with_suffix(".metrics.json")
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved model: {args.output}")
    print(f"Saved holdout metrics: {metrics_path}")
    print("Probability estimates are not calibrated; do not use them as automatic-action thresholds yet.")


if __name__ == "__main__":
    main()
