from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from finance_buddy_backend.schemas.chat import (
    AgentChatResponse,
    ChatRequest,
    ChatResponse,
    ConversationHistoryResponse,
)
from finance_buddy_backend.db.session import get_db
from finance_buddy_backend.services.agent_chat_service import AgentChatService
from finance_buddy_backend.services.chat_service import ChatService
from finance_buddy_backend.schemas.feedback import (
    MessageFeedbackRequest,
    MessageFeedbackResponse,
)
from finance_buddy_backend.services.feedback_service import FeedbackService


chat_router = APIRouter()


@chat_router.post("/chat", response_model=ChatResponse)
def create_chat_response(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    chat_service = ChatService(db)
    return chat_service.create_chat_response(
        message=payload.message,
        explanation_level=payload.explanation_level,
        conversation_id=payload.conversation_id
    )

@chat_router.get("/chat/{conversation_id}", response_model=ConversationHistoryResponse)
def get_chat_history(conversation_id: int,db: Session = Depends(get_db)) -> ConversationHistoryResponse:
    chat_service = ChatService(db)
    return chat_service.get_chat_history(conversation_id)

@chat_router.post("/chat/{message_id}/feedback", response_model=MessageFeedbackResponse)
def submit_message_feedback(
    message_id: int,
    payload: MessageFeedbackRequest,
    db: Session = Depends(get_db),
) -> MessageFeedbackResponse:
    feedback_service = FeedbackService(db)
    return feedback_service.submit_feedback(
        message_id=message_id,
        payload=payload,
    )

@chat_router.post("/agent/chat", response_model=AgentChatResponse)
def create_agent_chat_response(
    payload: ChatRequest,
    db: Session = Depends(get_db),
) -> AgentChatResponse:
    chat_service = AgentChatService(db)
    return chat_service.create_chat_response(
        message=payload.message,
        explanation_level=payload.explanation_level,
        conversation_id=payload.conversation_id,
    )
