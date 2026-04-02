from finance_buddy_backend.db.session import SessionLocal
from finance_buddy_backend.repositories.retrieval_repository import RetrievalRepository
from finance_buddy_backend.services.embedding_service import EmbeddingService
from finance_buddy_backend.services.retrieval_service import RetrievalService


def main() -> None:
    query = "que son los impuestos"
    top_k = 5

    with SessionLocal() as db:
        retrieval_repository = RetrievalRepository(db)
        embedding_service = EmbeddingService()
        retrieval_service = RetrievalService(
            retrieval_repository=retrieval_repository,
            embedding_service=embedding_service,
        )

        results = retrieval_service.retrieve_relevant_chunks(query, top_k=top_k)

        print(f"Query: {query}")
        print(f"Top {top_k} results:")

        for index, chunk in enumerate(results, start=1):
            print(f"\nResult {index}")
            print(f"Chunk ID: {chunk['chunk_id']}")
            print(f"Source ID: {chunk['source_id']}")
            print(f"Source Title: {chunk['source_title']}")
            print(f"Chunk Index: {chunk['chunk_index']}")
            print(f"Similarity Score: {chunk['similarity_score']:.4f}")
            print(f"Text: {str(chunk['text'])[:300]}")


if __name__ == "__main__":
    main()
