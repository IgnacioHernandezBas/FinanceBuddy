from finance_buddy_backend.repositories.retrieval_repository import RetrievalRepository
from finance_buddy_backend.services.embedding_service import EmbeddingService


class RetrievalService:
    def __init__(
        self,
        retrieval_repository: RetrievalRepository,
        embedding_service: EmbeddingService,
    ) -> None:
        self.retrieval_repository = retrieval_repository
        self.embedding_service = embedding_service

    def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, int | float | str | None]]:
        query_embedding = self.embedding_service.embed_query(query)
        return self.retrieval_repository.get_relevant_chunks(query_embedding, top_k)
