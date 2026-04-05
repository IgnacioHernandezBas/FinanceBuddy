import json
from pathlib import Path
import tempfile
from typing import Iterable

import mlflow
import pandas as pd

from finance_buddy_backend.core.config import settings

from .models import AggregateEvaluationResult, EvaluationManifest, PerExampleResult


class MLflowTrackingClient:
    def __init__(self) -> None:
        self.enabled = settings.mlflow_enabled
        if self.enabled:
            mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
            mlflow.set_experiment(settings.mlflow_experiment_name)

    def log_retrieval_evaluation(
        self,
        *,
        result: AggregateEvaluationResult,
        manifest: EvaluationManifest,
        dataset_path: str,
        manifest_path: str,
        top_k: int,
        run_name: str | None = None,
    ) -> str | None:
        if not self.enabled:
            return None

        with mlflow.start_run(run_name=run_name) as run:
            tracked_dataset = self._build_tracked_dataset(
                dataset_path=dataset_path,
                dataset_name=manifest.dataset_name,
            )
            mlflow.log_input(tracked_dataset, context="evaluation")

            mlflow.log_params(
                {
                    "run_type": "retrieval_eval",
                    "dataset_name": manifest.dataset_name,
                    "dataset_version": manifest.dataset_version,
                    "dataset_language": manifest.language,
                    "domain": manifest.domain,
                    "source_family": manifest.source_family,
                    "top_k": top_k,
                    "record_count": result.total_examples,
                }
            )

            mlflow.log_metrics(result.aggregate_metrics)
            mlflow.log_artifact(dataset_path, artifact_path="inputs")
            mlflow.log_artifact(manifest_path, artifact_path="inputs")

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                output_path = temp_path / "aggregate_evaluation_result.json"
                output_path.write_text(
                    result.model_dump_json(indent=2),
                    encoding="utf-8",
                )
                mlflow.log_artifact(str(output_path), artifact_path="outputs")

                per_example_path = temp_path / "per_example_results.json"
                per_example_path.write_text(
                    self._dump_per_example_results(result.per_example_results),
                    encoding="utf-8",
                )
                mlflow.log_artifact(str(per_example_path), artifact_path="outputs")

                failure_summary_path = temp_path / "failure_summary.md"
                failure_summary_path.write_text(
                    self._build_failure_summary(result.per_example_results),
                    encoding="utf-8",
                )
                mlflow.log_artifact(str(failure_summary_path), artifact_path="outputs")

                evaluation_notes_path = temp_path / "evaluation_notes.md"
                evaluation_notes_path.write_text(
                    self._build_evaluation_notes(),
                    encoding="utf-8",
                )
                mlflow.log_artifact(str(evaluation_notes_path), artifact_path="outputs")

            return run.info.run_id

    def _dump_per_example_results(
        self,
        per_example_results: list[PerExampleResult],
    ) -> str:
        return "[\n" + ",\n".join(
            result.model_dump_json(indent=2) for result in per_example_results
        ) + "\n]"

    def _build_failure_summary(
        self,
        per_example_results: Iterable[PerExampleResult],
    ) -> str:
        weak_results = [
            result
            for result in per_example_results
            if float(result.retrieval_metrics.get("mrr", 0.0)) < 1.0
            or float(result.retrieval_metrics.get("precision_at_k", 0.0)) < 1.0
        ]

        if not weak_results:
            return "# Failure Summary\n\nNo weak retrieval cases were detected in this run.\n"

        lines = ["# Failure Summary", ""]
        for result in weak_results:
            lines.append(f"## {result.question_id}")
            lines.append(f"- Question: {result.question}")
            lines.append(
                f"- MRR: {float(result.retrieval_metrics.get('mrr', 0.0)):.4f}"
            )
            lines.append(
                f"- Precision@k: {float(result.retrieval_metrics.get('precision_at_k', 0.0)):.4f}"
            )
            lines.append(
                "- Expected sources: "
                + ", ".join(result.expected_source_titles or ["none"])
            )
            lines.append(
                "- Retrieved sources: "
                + ", ".join(source.title for source in result.retrieved_sources)
            )
            lines.append("")

        return "\n".join(lines)

    def _build_evaluation_notes(self) -> str:
        return (
            "# Evaluation Notes\n\n"
            "- This run evaluates retrieval only.\n"
            "- Matching is title-based in v1 using expected_source_titles.\n"
            "- Retrieved source_id is logged for debugging and local inspection.\n"
            "- Generation quality and LLM-as-a-judge metrics are not included in this run.\n"
        )

    def _build_tracked_dataset(
        self,
        *,
        dataset_path: str,
        dataset_name: str,
    ):
        dataset_records = json.loads(Path(dataset_path).read_text(encoding="utf-8"))
        dataset_frame = pd.DataFrame(dataset_records)
        return mlflow.data.from_pandas(
            dataset_frame,
            source=dataset_path,
            name=dataset_name,
        )
