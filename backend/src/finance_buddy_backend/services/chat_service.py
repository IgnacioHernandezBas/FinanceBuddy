from fastapi import HTTPException
from sqlalchemy.orm import Session
from finance_buddy_backend.repositories.conversation_repository import ConversationRepository
from finance_buddy_backend.schemas.chat import ChatResponse, ChatSource, ConversationMessage, ConversationHistoryResponse


class ChatService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.conversation_repository = ConversationRepository(db)

    def create_chat_response(
        self,
        message: str,
        explanation_level: str,
        conversation_id: int | None = None,
    ) -> ChatResponse:
        if conversation_id is None:
            conversation = self.conversation_repository.create_conversation(
                user_identifier=None,
                title=None,
            )
        else:
            conversation = self.conversation_repository.get_conversation_by_id(conversation_id)
            if conversation is None:
                raise ValueError("Conversation not found.")

        self.conversation_repository.create_message(
            conversation_id=conversation.id,
            role="user",
            content=message,
            explanation_level=explanation_level,
            answer_status=None,
        )

        answer = f"This is a mock response for: '{message}'."

        self.conversation_repository.create_message(
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
            explanation_level=explanation_level,
            answer_status="mock",
        )

        return ChatResponse(
            answer=answer,
            sources=[
                ChatSource(
                    title="Mock Financial Education Source",
                    url="https://example.com/finance-source",
                )
            ],
            conversation_id=conversation.id,
        )
    
    def get_chat_history(self, conversation_id: int) -> ConversationHistoryResponse:
        conversation = self.conversation_repository.get_conversation_by_id(conversation_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found.")
        messages = self.conversation_repository.list_messages_by_conversation(conversation_id)
        messages_items= [
            ConversationMessage(
                id=message.id,
                role=message.role,
                content=message.content,
                explanation_level=message.explanation_level,
                answer_status=message.answer_status,
                created_at=message.created_at
            )
            for message in messages
        ]
        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            messages=messages_items
        )