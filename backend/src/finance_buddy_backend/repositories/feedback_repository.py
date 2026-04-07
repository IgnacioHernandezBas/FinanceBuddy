from sqlalchemy.orm import Session

from finance_buddy_backend.db.models import MessageFeedback


class FeedbackRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_message_id(self, message_id: int) -> MessageFeedback | None:
        return (
            self.db.query(MessageFeedback)
            .filter(MessageFeedback.message_id == message_id)
            .first()
        )

    def create_feedback(
        self,
        message_id: int,
        rating: str,
        comment: str | None,
    ) -> MessageFeedback:
        feedback = MessageFeedback(
            message_id=message_id,
            rating=rating,
            comment=comment,
        )
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def update_feedback(
        self,
        feedback: MessageFeedback,
        rating: str,
        comment: str | None,
    ) -> MessageFeedback:
        feedback.rating = rating
        feedback.comment = comment
        self.db.commit()
        self.db.refresh(feedback)
        return feedback
