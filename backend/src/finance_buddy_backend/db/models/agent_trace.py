from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class AgentTraceEvent(Base):
    __tablename__ = "agent_trace_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id"),
        nullable=False,
    )
    user_message_id: Mapped[int] = mapped_column(
        ForeignKey("messages.id"),
        nullable=False,
    )
    assistant_message_id: Mapped[int] = mapped_column(
        ForeignKey("messages.id"),
        nullable=False,
    )
    event_index: Mapped[int] = mapped_column(Integer, nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    conversation: Mapped["Conversation"] = relationship("Conversation")
    user_message: Mapped["Message"] = relationship(
        "Message",
        foreign_keys=[user_message_id],
    )
    assistant_message: Mapped["Message"] = relationship(
        "Message",
        foreign_keys=[assistant_message_id],
    )
