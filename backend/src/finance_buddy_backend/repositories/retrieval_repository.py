from sqlalchemy import select
from sqlalchemy.orm import Session

from finance_buddy_backend.db.models import DocumentChunk, RetrievalEvent, Source
from finance_buddy_backend.schemas.chat import ChatSource


class RetrievalRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_relevant_chunks(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[dict[str, int | float | str | None]]:
        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        distance = DocumentChunk.embedding.cosine_distance(query_embedding).label("distance")
        statement = (
            select(DocumentChunk, Source.title, Source.url, Source.publisher, distance)
            .join(Source, DocumentChunk.source_id == Source.id)
            .where(DocumentChunk.embedding.is_not(None))
            .order_by(distance)
            .limit(top_k)
        )

        rows = self.db.execute(statement).all()

        return [
            {
                "chunk_id": chunk.id,
                "source_id": chunk.source_id,
                "source_title": source_title,
                "source_url": source_url,
                "source_publisher": source_publisher,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "similarity_score": max(0.0, 1.0 - float(distance_score)),
            }
            for chunk, source_title, source_url, source_publisher, distance_score in rows
        ]

    def create_retrieval_events(
        self,
        message_id: int,
        retrieval_results: list[dict[str, int | float | str | None]],
    ) -> list[RetrievalEvent]:
        retrieval_events: list[RetrievalEvent] = []

        for rank, result in enumerate(retrieval_results, start=1):
            retrieval_event = RetrievalEvent(
                message_id=message_id,
                chunk_id=int(result["chunk_id"]),
                rank=rank,
                similarity_score=float(result["similarity_score"]),
            )
            retrieval_events.append(retrieval_event)

        self.db.add_all(retrieval_events)
        self.db.commit()

        for retrieval_event in retrieval_events:
            self.db.refresh(retrieval_event)

        return retrieval_events

    def list_sources_by_message_ids(
        self,
        message_ids: list[int],
    ) -> dict[int, list[ChatSource]]:
        if not message_ids:
            return {}

        statement = (
            select(
                RetrievalEvent.message_id,
                Source.id,
                Source.title,
                Source.url,
                Source.publisher,
                RetrievalEvent.rank,
            )
            .join(DocumentChunk, RetrievalEvent.chunk_id == DocumentChunk.id)
            .join(Source, DocumentChunk.source_id == Source.id)
            .where(RetrievalEvent.message_id.in_(message_ids))
            .order_by(RetrievalEvent.message_id, RetrievalEvent.rank)
        )

        rows = self.db.execute(statement).all()
        sources_by_message_id: dict[int, list[ChatSource]] = {}
        seen_source_ids: dict[int, set[int]] = {}

        for message_id, source_id, source_title, source_url, source_publisher, _rank in rows:
            if message_id not in sources_by_message_id:
                sources_by_message_id[message_id] = []
                seen_source_ids[message_id] = set()

            if source_id in seen_source_ids[message_id]:
                continue

            seen_source_ids[message_id].add(source_id)
            sources_by_message_id[message_id].append(
                ChatSource(
                    title=source_title,
                    url=source_url if isinstance(source_url, str) else None,
                    publisher=source_publisher if isinstance(source_publisher, str) else None,
                )
            )

        return sources_by_message_id
