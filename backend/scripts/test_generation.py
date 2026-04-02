from finance_buddy_backend.db.session import SessionLocal
from finance_buddy_backend.repositories.retrieval_repository import RetrievalRepository
from finance_buddy_backend.services.embedding_service import EmbeddingService
from finance_buddy_backend.services.generation_service import GenerationService
from finance_buddy_backend.services.retrieval_service import RetrievalService


def main() -> None:
    query = "que son los impuestos"
    explanation_level = "basic"
    top_k = 3

    with SessionLocal() as db:
        retrieval_repository = RetrievalRepository(db)
        embedding_service = EmbeddingService()
        retrieval_service = RetrievalService(
            retrieval_repository=retrieval_repository,
            embedding_service=embedding_service,
        )
        generation_service = GenerationService()

        retrieved_chunks = retrieval_service.retrieve_relevant_chunks(
            query=query,
            top_k=top_k,
        )

        print(f"Query: {query}")
        print(f"Explanation level: {explanation_level}")
        print(f"Retrieved chunks: {len(retrieved_chunks)}")

        for index, chunk in enumerate(retrieved_chunks, start=1):
            print(f"\nSource {index}: {chunk['source_title']}")
            print(f"Similarity score: {chunk['similarity_score']:.4f}")
            print(f"Text preview: {str(chunk['text'])[:200]}")

        answer = generation_service.generate_response(
            question=query,
            explanation_level=explanation_level,
            retrieved_chunks=retrieved_chunks,
        )

        print("\nGenerated answer:\n")
        print(answer)


if __name__ == "__main__":
    main()
