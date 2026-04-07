from fastapi import HTTPException
from sqlalchemy.orm import Session

from finance_buddy_backend.repositories.conversation_repository import ConversationRepository
from finance_buddy_backend.repositories.retrieval_repository import RetrievalRepository
from finance_buddy_backend.schemas.chat import ChatResponse, ChatSource, ConversationHistoryResponse, ConversationMessage
from finance_buddy_backend.services.embedding_service import EmbeddingService
from finance_buddy_backend.services.query_normalization_service import QueryNormalizationService
from finance_buddy_backend.services.retrieval_service import RetrievalService
from finance_buddy_backend.services.generation_service import GenerationService


class ChatService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.generation_service = GenerationService()
        self.conversation_repository = ConversationRepository(db)
        self.retrieval_repository = RetrievalRepository(db)
        self.embedding_service = EmbeddingService()
        self.query_normalization_service = QueryNormalizationService()
        self.retrieval_service = RetrievalService(
            retrieval_repository=self.retrieval_repository,
            embedding_service=self.embedding_service,
            query_normalization_service=self.query_normalization_service,
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

        retrieved_chunks = self.retrieval_service.retrieve_relevant_chunks(message, top_k=5)
        if retrieved_chunks:
            self.retrieval_repository.create_retrieval_events(user_message.id, retrieved_chunks)
            try:
                answer = self.generation_service.generate_response(
                    question=message,
                    explanation_level=explanation_level,
                    retrieved_chunks=retrieved_chunks,
                )
            except Exception:
                answer = (
                    "I could not generate a grounded answer at this time. "
                    "Please try again in a moment."
                )
                answer_status = "generation_failed"
            else:
                if not answer.strip():
                    answer = (
                        "I could not generate a grounded answer at this time. "
                        "Please try again in a moment."
                    )
                    answer_status = "generation_failed"
                else:
                    answer_status = "generated"
        
        else:
            answer = (
                "I could not find enough supporting evidence in the trusted sources to answer confidently."
            )
            answer_status = "no_evidence_found"

        assistant_message = self.conversation_repository.create_message(
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
                    publisher=(
                        chunk["source_publisher"]
                        if isinstance(chunk["source_publisher"], str)
                        else None
                    ),
                )

        return ChatResponse(
            answer=answer,
            sources=list(unique_sources.values()),
            conversation_id=conversation.id,
            message_id=assistant_message.id,
        )

    def get_chat_history(self, conversation_id: int) -> ConversationHistoryResponse:
        conversation = self.conversation_repository.get_conversation_by_id(conversation_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found.")

        messages = self.conversation_repository.list_messages_by_conversation(conversation_id)
        user_message_ids = [message.id for message in messages if message.role == "user"]
        sources_by_user_message_id = self.retrieval_repository.list_sources_by_message_ids(user_message_ids)

        latest_user_message_id: int | None = None
        message_items: list[ConversationMessage] = []

        for message in messages:
            if message.role == "user":
                latest_user_message_id = message.id

            message_items.append(
                ConversationMessage(
                id=message.id,
                role=message.role,
                content=message.content,
                explanation_level=message.explanation_level,
                answer_status=message.answer_status,
                created_at=message.created_at,
                sources=(
                    sources_by_user_message_id.get(latest_user_message_id, [])
                    if message.role == "assistant" and latest_user_message_id is not None
                    else []
                ),
            )
            )

        return ConversationHistoryResponse(conversation_id=conversation_id, messages=message_items)
