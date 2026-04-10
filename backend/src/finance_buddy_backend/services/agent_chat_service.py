from fastapi import HTTPException
from sqlalchemy.orm import Session

from finance_buddy_backend.agent.graph import build_agent_graph
from finance_buddy_backend.agent.state import AgentState
from finance_buddy_backend.core.config import settings
from finance_buddy_backend.repositories.conversation_repository import ConversationRepository
from finance_buddy_backend.repositories.retrieval_repository import RetrievalRepository
from finance_buddy_backend.schemas.chat import (
    AgentChatResponse,
    AgentRetrievedChunk,
    ChatSource,
)
from finance_buddy_backend.services.embedding_service import EmbeddingService
from finance_buddy_backend.services.generation_service import GenerationService
from finance_buddy_backend.services.query_normalization_service import QueryNormalizationService
from finance_buddy_backend.services.retrieval_service import RetrievalService


class AgentChatService:
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
        self.graph = build_agent_graph(
            retrieval_service=self.retrieval_service,
            generation_service=self.generation_service,
        )

    def build_initial_state(
        self,
        conversation_id: int,
        user_message_id: int,
        message: str,
        explanation_level: str,
    ) -> AgentState:
        return {
            "conversation_id": conversation_id,
            "user_message_id": user_message_id,
            "question": message,
            "explanation_level": explanation_level,
            "web_access_mode": settings.agent_web_access_mode,
            "errors": [],
        }

    def create_chat_response(
        self,
        message: str,
        explanation_level: str,
        conversation_id: int | None = None,
    ) -> AgentChatResponse:
        if conversation_id is None:
            conversation = self.conversation_repository.create_conversation(
                user_identifier=None,
                title=None,
            )
        else:
            conversation = self.conversation_repository.get_conversation_by_id(
                conversation_id
            )
            if conversation is None:
                raise HTTPException(status_code=404, detail="Conversation not found.")

        user_message = self.conversation_repository.create_message(
            conversation_id=conversation.id,
            role="user",
            content=message,
            explanation_level=explanation_level,
            answer_status=None,
        )

        initial_state = self.build_initial_state(
            conversation_id=conversation.id,
            user_message_id=user_message.id,
            message=message,
            explanation_level=explanation_level,
        )

        final_state = self.graph.invoke(initial_state)

        internal_chunks = final_state.get("internal_chunks", [])
        if internal_chunks:
            self.retrieval_repository.create_retrieval_events(
                user_message.id,
                internal_chunks,
            )
        debug_chunks: list[AgentRetrievedChunk] = []
        for chunk in internal_chunks:
            score = chunk.get("similarity_score")
            debug_chunks.append(
                AgentRetrievedChunk(
                    source_id=chunk.get("source_id") if isinstance(chunk.get("source_id"), int) else None,
                    source_title=chunk.get("source_title")
                    if isinstance(chunk.get("source_title"), str)
                    else None,
                    source_url=chunk.get("source_url")
                    if isinstance(chunk.get("source_url"), str)
                    else None,
                    source_publisher=chunk.get("source_publisher")
                    if isinstance(chunk.get("source_publisher"), str)
                    else None,
                    score=float(score) if isinstance(score, (int, float)) else None,
                    text=chunk.get("text") if isinstance(chunk.get("text"), str) else None,
                )
            )

        answer = final_state.get("answer")
        if not isinstance(answer, str) or not answer.strip():
            answer = (
                "I could not generate a grounded answer at this time. "
                "Please try again in a moment."
            )

        answer_status = final_state.get("answer_status")
        if not isinstance(answer_status, str) or not answer_status.strip():
            answer_status = "agent_failed"

        final_sources = final_state.get("final_sources", [])
        chat_sources: list[ChatSource] = []

        for source in final_sources:
            title = source.get("title")
            if not isinstance(title, str) or not title.strip():
                continue

            url = source.get("url")
            publisher = source.get("publisher")

            chat_sources.append(
                ChatSource(
                    title=title,
                    url=url if isinstance(url, str) else None,
                    publisher=publisher if isinstance(publisher, str) else None,
                )
            )

        assistant_message = self.conversation_repository.create_message(
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
            explanation_level=explanation_level,
            answer_status=answer_status,
        )

        return AgentChatResponse(
            answer=answer,
            sources=chat_sources,
            conversation_id=conversation.id,
            message_id=assistant_message.id,
            trace_events=final_state.get("trace_events", []),
            retrieved_chunks=debug_chunks,
        )
