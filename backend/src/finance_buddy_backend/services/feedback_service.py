from fastapi import HTTPException
from sqlalchemy.orm import Session

from finance_buddy_backend.repositories.conversation_repository import ConversationRepository
from finance_buddy_backend.repositories.feedback_repository import FeedbackRepository
from finance_buddy_backend.schemas.feedback import (
    MessageFeedbackRequest,
    MessageFeedbackResponse,
)


class FeedbackService:
    def __init__(self, db: Session) -> None:
        self.conversation_repository = ConversationRepository(db)
        self.feedback_repository = FeedbackRepository(db)

    def submit_feedback(
        self,
        message_id: int,
        payload: MessageFeedbackRequest,
    ) -> MessageFeedbackResponse:
        message = self.conversation_repository.get_message_by_id(message_id)
        if message is None:
            raise HTTPException(status_code=404, detail="Message not found.")

        if message.role != "assistant":
            raise HTTPException(
                status_code=400,
                detail="Feedback can only be submitted for assistant messages.",
            )

        existing_feedback = self.feedback_repository.get_by_message_id(message_id)

        if existing_feedback is None:
            feedback = self.feedback_repository.create_feedback(
                message_id=message_id,
                rating=payload.rating,
                comment=payload.comment,
            )
        else:
            feedback = self.feedback_repository.update_feedback(
                feedback=existing_feedback,
                rating=payload.rating,
                comment=payload.comment,
            )

        return MessageFeedbackResponse(
            message_id=feedback.message_id,
            rating=feedback.rating,
            comment=feedback.comment,
        )
