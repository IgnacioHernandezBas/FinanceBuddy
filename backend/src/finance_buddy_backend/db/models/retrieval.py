from datetime import datetime
from ..base import Base
from sqlalchemy import DateTime, ForeignKey, Integer, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class RetrievalEvent(Base):
    __tablename__ = "retrieval_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"), nullable=False)
    chunk_id: Mapped[int] = mapped_column(ForeignKey("document_chunks.id"), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    message: Mapped["Message"] = relationship("Message")
    chunk: Mapped["DocumentChunk"] = relationship("DocumentChunk")
