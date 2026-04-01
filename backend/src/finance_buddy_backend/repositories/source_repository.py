from sqlalchemy.orm import Session

from finance_buddy_backend.db.models import DocumentChunk, Source


class SourceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_source(
        self,
        title: str,
        source_type: str,
        content_text: str,
        url: str | None = None,
        publisher: str | None = None,
        language: str | None = None,
        content_hash: str | None = None,
        ingestion_status: str = "pending",
    ) -> Source:
        source = Source(
            title=title,
            source_type=source_type,
            url=url,
            publisher=publisher,
            language=language,
            content_text=content_text,
            content_hash=content_hash,
            ingestion_status=ingestion_status,
        )
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def get_source_by_content_hash(self, content_hash: str) -> Source | None:
        return self.db.query(Source).filter(Source.content_hash == content_hash).first()

    def update_ingestion_status(self, source_id: int, ingestion_status: str) -> Source | None:
        source = self.db.query(Source).filter(Source.id == source_id).first()
        if source is None:
            return None

        source.ingestion_status = ingestion_status
        self.db.commit()
        self.db.refresh(source)
        return source

    def create_document_chunks(self, source_id: int, chunks: list[str]) -> list[DocumentChunk]:
        document_chunks: list[DocumentChunk] = []
        cursor = 0

        for index, chunk_text in enumerate(chunks):
            char_start = cursor
            char_end = cursor + len(chunk_text)

            document_chunk = DocumentChunk(
                source_id=source_id,
                chunk_index=index,
                text=chunk_text,
                token_count=len(chunk_text.split()),
                char_start=char_start,
                char_end=char_end,
            )
            document_chunks.append(document_chunk)
            cursor = char_end

        self.db.add_all(document_chunks)
        self.db.commit()

        for document_chunk in document_chunks:
            self.db.refresh(document_chunk)

        return document_chunks
