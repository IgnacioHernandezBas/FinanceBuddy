from sqlalchemy.orm import Session

from finance_buddy_backend.db.models import AgentTraceEvent


class AgentTraceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_trace_events(
        self,
        conversation_id: int,
        user_message_id: int,
        assistant_message_id: int,
        trace_events: list[dict[str, object]],
    ) -> list[AgentTraceEvent]:
        persisted_events: list[AgentTraceEvent] = []

        for event_index, payload in enumerate(trace_events, start=1):
            persisted_events.append(
                AgentTraceEvent(
                    conversation_id=conversation_id,
                    user_message_id=user_message_id,
                    assistant_message_id=assistant_message_id,
                    event_index=event_index,
                    payload=payload,
                )
            )

        if not persisted_events:
            return []

        self.db.add_all(persisted_events)
        self.db.commit()

        for event in persisted_events:
            self.db.refresh(event)

        return persisted_events
