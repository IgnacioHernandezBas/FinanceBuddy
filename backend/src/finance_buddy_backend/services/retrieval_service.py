from finance_buddy_backend.repositories.retrieval_repository import RetrievalRepository
from finance_buddy_backend.services.embedding_service import EmbeddingService
from finance_buddy_backend.services.query_normalization_service import QueryNormalizationService


class RetrievalService:
    def __init__(
        self,
        retrieval_repository: RetrievalRepository,
        embedding_service: EmbeddingService,
        query_normalization_service: QueryNormalizationService | None = None,
    ) -> None:
        self.retrieval_repository = retrieval_repository
        self.embedding_service = embedding_service
        self.query_normalization_service = query_normalization_service or QueryNormalizationService()

    def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, int | float | str | None]]:
        retrieval_query = self.query_normalization_service.normalize_for_retrieval(query)
        query_embedding = self.embedding_service.embed_query(retrieval_query)
        return self.retrieval_repository.get_relevant_chunks(query_embedding, top_k)
