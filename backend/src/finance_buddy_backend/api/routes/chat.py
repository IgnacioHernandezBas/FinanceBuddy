from fastapi import APIRouter
from finance_buddy_backend.schemas.chat import ChatRequest, ChatResponse, ChatSource

chat_router = APIRouter()


@chat_router.post("/chat", response_model=ChatResponse)
def create_chat_response(payload: ChatRequest) -> ChatResponse:
    return ChatResponse(
        answer=(
            f"This is a mock response for: '{payload.message}'. "
            f"Explanation level: {payload.explanation_level}."
        ),
        sources=[
            ChatSource(
                title="Mock Financial Education Source",
                url="https://example.com/finance-source",
            )
        ],
    )