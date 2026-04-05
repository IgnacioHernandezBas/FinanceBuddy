import argparse

from finance_buddy_backend.db.session import SessionLocal

from .loaders import load_dataset, load_manifest, validate_dataset_against_manifest
from .mlflow_tracking import MLflowTrackingClient
from .models import AggregateEvaluationResult, EvaluationManifest
from .rag_evaluator import RAGEvaluator


class RAGEvalRunner:
    """
    Orchestrates the loading of the evaluation dataset and manifest, runs the RAG evaluation, and returns the aggregate results.
    """
    def run_evaluation(
        self,
        dataset_path: str,
        manifest_path: str,
        top_k: int = 5,
    ) -> tuple[AggregateEvaluationResult, EvaluationManifest]:
        dataset = load_dataset(dataset_path)
        manifest = load_manifest(manifest_path)
        validate_dataset_against_manifest(dataset, manifest)

        with SessionLocal() as session:
            evaluator = RAGEvaluator(db=session)
            result = evaluator.evaluate_retrieval(
                dataset=dataset,
                manifest=manifest,
                top_k=top_k,
            )
        return result, manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run retrieval evaluation on a dataset and manifest.",
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
        "--top-k",
        type=int,
        default=5,
        help="Number of top retrieved chunks to evaluate against.",
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

    runner = RAGEvalRunner()
    result, manifest = runner.run_evaluation(
        dataset_path=args.dataset_path,
        manifest_path=args.manifest_path,
        top_k=args.top_k,
    )

    if args.log_to_mlflow:
        tracking_client = MLflowTrackingClient()
        run_id = tracking_client.log_retrieval_evaluation(
            result=result,
            manifest=manifest,
            dataset_path=args.dataset_path,
            manifest_path=args.manifest_path,
            top_k=args.top_k,
            run_name=args.run_name,
        )
        if run_id is not None:
            print(f"MLflow run logged: {run_id}")

    print("Aggregate Evaluation Result:")
    print(result.model_dump_json(indent=2))
