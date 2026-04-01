from hashlib import sha256
from pathlib import Path

from sqlalchemy.orm import Session

from finance_buddy_backend.ingestion.loaders.pdf_loader import extract_text_from_pdf
from finance_buddy_backend.ingestion.processors.chunker import chunk_text
from finance_buddy_backend.ingestion.processors.text_normalizer import normalize_text
from finance_buddy_backend.repositories.source_repository import SourceRepository
from finance_buddy_backend.services.embedding_service import EmbeddingService
    

class IngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.source_repository = SourceRepository(self.db)
        self.embedding_service = EmbeddingService()

    def ingest_pdf(self, file_path: str)->dict:
        # Load and process the PDF file
        pdf_path=Path(file_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"File {file_path} does not exist.")
        raw_text=extract_text_from_pdf(pdf_path)
        normalized_text=normalize_text(raw_text)
        if not normalized_text:
            raise ValueError("The PDF did not contain usable text after normalization.")
        chunks=chunk_text(normalized_text)
        if not chunks:
            raise ValueError("Failed to chunk the text.")
        
        # Build source metadata
        title=pdf_path.stem
        source_type="pdf"
        publisher=pdf_path.parent.name
        language="es"
        content_hash=sha256(normalized_text.encode("utf-8")).hexdigest()

        # Check for existing source with the same content hash
        existing_source = self.source_repository.get_source_by_content_hash(content_hash)
        if existing_source is not None:
            return {
                "source_id": existing_source.id,
                "title": existing_source.title,
                "chunk_count": len(existing_source.chunks),
                "ingestion_status": existing_source.ingestion_status,
            }
        
        # if the source is new, generate embeddings for the chunks
        chunk_embeddings = self.embedding_service.embed_documents(chunks)

        if len(chunk_embeddings) != len(chunks):
            raise ValueError("The number of chunk embeddings does not match the number of chunks.")

        # Store source and chunks in the database
        source= self.source_repository.create_source(
            title=title,
            source_type=source_type,
            content_text=normalized_text,
            publisher=publisher,
            language=language,
            content_hash=content_hash,
            ingestion_status="processing"
        )
        try:
            document_chunks=self.source_repository.create_document_chunks(
                source_id=source.id, 
                chunks=chunks,
                embeddings=chunk_embeddings
            )
        except Exception as e:
            self.source_repository.update_ingestion_status(source.id, "failed")
            raise RuntimeError(f"Failed to store document chunks: {str(e)}") from e
        
        self.source_repository.update_ingestion_status(source.id, "completed")

        # Return a summary of the ingestion result
        summary={"source_id": source.id,
                "title": source.title,
                "chunk_count": len(document_chunks),
                "ingestion_status": "completed"}

        return summary

