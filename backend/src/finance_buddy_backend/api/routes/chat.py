from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from finance_buddy_backend.schemas.chat import ChatRequest, ChatResponse, ConversationHistoryResponse
from finance_buddy_backend.db.session import get_db
from finance_buddy_backend.services.chat_service import ChatService

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
