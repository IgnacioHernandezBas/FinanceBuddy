import argparse

from finance_buddy_backend.db.session import SessionLocal

from .loaders import load_dataset, load_manifest, validate_dataset_against_manifest
from .mlflow_tracking import MLflowTrackingClient
from .models import EvaluationManifest, SystemAggregateEvaluationResult
from .system_evaluator import SystemEvaluator


class SystemEvalRunner:
    def run_evaluation(
        self,
        *,
        dataset_path: str,
        manifest_path: str,
        system_name: str,
        explanation_level: str,
        allow_web_search: bool,
        max_examples: int | None,
        sleep_seconds: float,
    ) -> tuple[SystemAggregateEvaluationResult, EvaluationManifest]:
        dataset = load_dataset(dataset_path)
        manifest = load_manifest(manifest_path)
        validate_dataset_against_manifest(dataset, manifest)
        if max_examples is not None:
            dataset = dataset[:max_examples]

        with SessionLocal() as session:
            evaluator = SystemEvaluator(db=session)
            result = evaluator.evaluate_system(
                system_name=system_name,
                dataset=dataset,
                manifest=manifest,
                explanation_level=explanation_level,
                allow_web_search=allow_web_search,
                sleep_seconds=sleep_seconds,
            )

        return result, manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run end-to-end system evaluation for baseline RAG or Agent V1.",
    )
    parser.add_argument(
        "--dataset-path",
        required=True,
        help="Path to the evaluation dataset JSON file.",
    )
    parser.add_argument(
        "--manifest-path",
        required=True,
        help="Path to the evaluation manifest JSON file.",
    )
    parser.add_argument(
        "--system-name",
        required=True,
        choices=["baseline_rag", "agentic_v1"],
        help="System variant to evaluate.",
    )
    parser.add_argument(
        "--explanation-level",
        default="basic",
        choices=["basic", "technical"],
        help="Explanation level passed into the system under evaluation.",
    )
    parser.add_argument(
        "--allow-web-search",
        action="store_true",
        help="Allow public web fallback when running Agent V1 evaluation.",
    )
    parser.add_argument(
        "--max-examples",
        type=int,
        default=None,
        help="Optional limit on the number of dataset examples to evaluate.",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=0.0,
        help="Seconds to sleep between examples to respect model rate limits.",
    )
    parser.add_argument(
        "--log-to-mlflow",
        action="store_true",
        help="Log the evaluation run to the configured MLflow tracking server.",
    )
    parser.add_argument(
        "--run-name",
        default=None,
        help="Optional MLflow run name.",
    )

    args = parser.parse_args()

    runner = SystemEvalRunner()
    result, manifest = runner.run_evaluation(
        dataset_path=args.dataset_path,
        manifest_path=args.manifest_path,
        system_name=args.system_name,
        explanation_level=args.explanation_level,
        allow_web_search=args.allow_web_search,
        max_examples=args.max_examples,
        sleep_seconds=args.sleep_seconds,
    )

    if args.log_to_mlflow:
        tracking_client = MLflowTrackingClient()
        run_id = tracking_client.log_system_evaluation(
            result=result,
            manifest=manifest,
            dataset_path=args.dataset_path,
            manifest_path=args.manifest_path,
            explanation_level=args.explanation_level,
            allow_web_search=args.allow_web_search,
            run_name=args.run_name,
        )
        if run_id is not None:
            print(f"MLflow run logged: {run_id}")

    print("System Evaluation Result:")
    print(result.model_dump_json(indent=2))
