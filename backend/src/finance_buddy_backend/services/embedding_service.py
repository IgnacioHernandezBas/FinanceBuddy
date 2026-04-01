from sentence_transformers import SentenceTransformer

class EmbeddingService:
    """Service for handling embeddings."""
    
    def __init__(self):
        self.model=SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        if not texts:
            return []
        embeddings=self.model.encode(texts, show_progress_bar=True,convert_to_numpy=True )
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        """Generate an embedding for a single query text."""
        if not text.strip():
            raise ValueError("Query text cannot be empty.")

        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
