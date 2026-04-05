import json
from pathlib import Path

from .models import EvaluationExample, EvaluationManifest


def load_dataset(path: str | Path) -> list[EvaluationExample]:
    dataset_path = Path(path)

    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

    raw_data = json.loads(dataset_path.read_text(encoding="utf-8"))

    if not isinstance(raw_data, list):
        raise ValueError("Dataset file must contain a JSON array of evaluation examples.")

    examples = [EvaluationExample.model_validate(item) for item in raw_data]

    seen_ids: set[str] = set()
    duplicated_ids: set[str] = set()

    for example in examples:
        if example.question_id in seen_ids:
            duplicated_ids.add(example.question_id)
        seen_ids.add(example.question_id)

    if duplicated_ids:
        raise ValueError(
            f"Dataset contains duplicated question_id values: {sorted(duplicated_ids)}"
        )
    return examples


def load_manifest(path: str | Path) -> EvaluationManifest:
    manifest_path = Path(path)

    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest file not found: {manifest_path}")

    raw_data = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest = EvaluationManifest.model_validate(raw_data)

    return manifest


def validate_dataset_against_manifest(
    dataset: list[EvaluationExample],
    manifest: EvaluationManifest,
) -> None:
    if manifest.record_count != len(dataset):
        raise ValueError(
            f"Manifest record_count={manifest.record_count} does not match dataset size={len(dataset)}."
        )

    stored_source_titles = set(manifest.stored_source_titles)

    for example in dataset:
        if example.language != manifest.language:
            raise ValueError(
                f"Example question_id={example.question_id} has language={example.language} "
                f"which does not match manifest language={manifest.language}."
            )

        for title in example.expected_source_titles:
            if title not in stored_source_titles:
                raise ValueError(
                    f"Example question_id={example.question_id} has expected source title='{title}' "
                    "which is not listed in manifest stored_source_titles."
                )

        