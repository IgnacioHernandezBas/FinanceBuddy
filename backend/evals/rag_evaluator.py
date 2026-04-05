from sqlalchemy.orm import Session

from finance_buddy_backend.repositories.retrieval_repository import RetrievalRepository
from finance_buddy_backend.services.embedding_service import EmbeddingService
from finance_buddy_backend.services.query_normalization_service import QueryNormalizationService
from finance_buddy_backend.services.retrieval_service import RetrievalService

from .models import (
    AggregateEvaluationResult,
    EvaluationExample,
    EvaluationManifest,
    PerExampleResult,
    RetrievedSourceResult,
)


class RAGEvaluator:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.retrieval_repository = RetrievalRepository(db)
        self.embedding_service = EmbeddingService()
        self.query_normalization_service = QueryNormalizationService()
        self.retrieval_service = RetrievalService(
            retrieval_repository=self.retrieval_repository,
            embedding_service=self.embedding_service,
            query_normalization_service=self.query_normalization_service,
        )

    def evaluate_retrieval(
        self,
        dataset: list[EvaluationExample],
        manifest: EvaluationManifest,
        top_k: int = 5,
    ) -> AggregateEvaluationResult:
        per_example_results = [
            self._evaluate_retrieval_example(example=example, top_k=top_k)
            for example in dataset
        ]

        aggregate_metrics = self._aggregate_retrieval_metrics(per_example_results)

        return AggregateEvaluationResult(
            dataset_name=manifest.dataset_name,
            dataset_version=manifest.dataset_version,
            total_examples=len(dataset),
            aggregate_metrics=aggregate_metrics,
            per_example_results=per_example_results,
        )

    def _evaluate_retrieval_example(
        self,
        example: EvaluationExample,
        top_k: int,
    ) -> PerExampleResult:
        retrieval_query = self.query_normalization_service.normalize_for_retrieval(
            example.question
        )
        retrieved_chunks = self.retrieval_service.retrieve_relevant_chunks(
            query=example.question,
            top_k=top_k,
        )
        retrieved_sources = self._build_retrieved_sources(retrieved_chunks)
        retrieval_metrics = self._compute_retrieval_metrics(
            expected_source_titles=example.expected_source_titles,
            retrieved_sources=retrieved_sources,
        )

        return PerExampleResult(
            question_id=example.question_id,
            question=example.question,
            language=example.language,
            retrieval_query=retrieval_query,
            retrieved_sources=retrieved_sources,
            retrieval_metrics=retrieval_metrics,
            expected_source_titles=example.expected_source_titles,
            expected_answer_points=example.expected_answer_points,
        )

    def _build_retrieved_sources(
        self,
        retrieved_chunks: list[dict[str, int | float | str | None]],
    ) -> list[RetrievedSourceResult]:
        retrieved_sources: list[RetrievedSourceResult] = []
        seen_source_ids: set[int] = set()

        for rank, chunk in enumerate(retrieved_chunks, start=1):
            source_id = int(chunk["source_id"])
            if source_id in seen_source_ids:
                continue

            seen_source_ids.add(source_id)
            retrieved_sources.append(
                RetrievedSourceResult(
                    source_id=source_id,
                    title=str(chunk["source_title"]),
                    similarity_score=(
                        float(chunk["similarity_score"])
                        if chunk["similarity_score"] is not None
                        else None
                    ),
                    rank=rank,
                )
            )

        return retrieved_sources

    def _compute_retrieval_metrics(
        self,
        expected_source_titles: list[str],
        retrieved_sources: list[RetrievedSourceResult],
    ) -> dict[str, float | bool]:
        if not retrieved_sources:
            return {
                "hit": False,
                "mrr": 0.0,
                "precision_at_k": 0.0,
            }

        expected_titles = set(expected_source_titles)
        first_match_rank: int | None = None
        matched_count = 0

        for source in retrieved_sources:
            if source.title in expected_titles:
                matched_count += 1
                if first_match_rank is None and source.rank is not None:
                    first_match_rank = source.rank

        return {
            "hit": matched_count > 0,
            "mrr": 0.0 if first_match_rank is None else 1.0 / first_match_rank,
            "precision_at_k": matched_count / len(retrieved_sources),
        }

    def _aggregate_retrieval_metrics(
        self,
        per_example_results: list[PerExampleResult],
    ) -> dict[str, float]:
        if not per_example_results:
            return {
                "retrieval_hit_rate": 0.0,
                "retrieval_mrr": 0.0,
                "retrieval_source_precision_at_k": 0.0,
            }

        total_examples = len(per_example_results)
        hit_count = 0
        mrr_total = 0.0
        precision_total = 0.0

        for result in per_example_results:
            hit_count += int(bool(result.retrieval_metrics.get("hit", False)))
            mrr_total += float(result.retrieval_metrics.get("mrr", 0.0))
            precision_total += float(result.retrieval_metrics.get("precision_at_k", 0.0))

        return {
            "retrieval_hit_rate": hit_count / total_examples,
            "retrieval_mrr": mrr_total / total_examples,
            "retrieval_source_precision_at_k": precision_total / total_examples,
        }
