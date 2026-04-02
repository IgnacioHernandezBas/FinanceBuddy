from fastapi import HTTPException
from sqlalchemy.orm import Session

from finance_buddy_backend.repositories.conversation_repository import ConversationRepository
from finance_buddy_backend.repositories.retrieval_repository import RetrievalRepository
from finance_buddy_backend.schemas.chat import ChatResponse, ChatSource, ConversationHistoryResponse, ConversationMessage
from finance_buddy_backend.services.embedding_service import EmbeddingService
from finance_buddy_backend.services.retrieval_service import RetrievalService


class ChatService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.conversation_repository = ConversationRepository(db)
        self.retrieval_repository = RetrievalRepository(db)
        self.embedding_service = EmbeddingService()
        self.retrieval_service = RetrievalService(
            retrieval_repository=self.retrieval_repository,
            embedding_service=self.embedding_service,
        )

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
                raise HTTPException(status_code=404, detail="Conversation not found.")

        user_message = self.conversation_repository.create_message(
            conversation_id=conversation.id,
            role="user",
            content=message,
            explanation_level=explanation_level,
            answer_status=None,
        )

        retrieved_chunks = self.retrieval_service.retrieve_relevant_chunks(message, top_k=3)
        if retrieved_chunks:
            self.retrieval_repository.create_retrieval_events(user_message.id, retrieved_chunks)
            answer = (
                f"This is still a mock answer for: '{message}'. "
                "The response is now backed by retrieved source chunks."
            )
            answer_status = "retrieved_mock"
        else:
            answer = (
                f"This is still a mock answer for: '{message}'. "
                "No relevant source chunks were retrieved."
            )
            answer_status = "no_evidence_mock"

        self.conversation_repository.create_message(
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
            explanation_level=explanation_level,
            answer_status=answer_status,
        )

        unique_sources: dict[int, ChatSource] = {}
        for chunk in retrieved_chunks:
            source_id = int(chunk["source_id"])
            if source_id not in unique_sources:
                unique_sources[source_id] = ChatSource(
                    title=str(chunk["source_title"]),
                    url=chunk["source_url"] if isinstance(chunk["source_url"], str) else None,
                )

        return ChatResponse(
            answer=answer,
            sources=list(unique_sources.values()),
            conversation_id=conversation.id,
        )

    def get_chat_history(self, conversation_id: int) -> ConversationHistoryResponse:
        conversation = self.conversation_repository.get_conversation_by_id(conversation_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found.")

        messages = self.conversation_repository.list_messages_by_conversation(conversation_id)
        message_items = [
            ConversationMessage(
                id=message.id,
                role=message.role,
                content=message.content,
                explanation_level=message.explanation_level,
                answer_status=message.answer_status,
                created_at=message.created_at,
            )
            for message in messages
        ]
        return ConversationHistoryResponse(conversation_id=conversation_id, messages=message_items)
